#!/usr/bin/env python3
"""
Live MCP wiring check for the SENTINEL Command Center.

Answers one question with evidence instead of with a constant: does the hub
server actually start, and how many tools does it serve over the wire?

The `mcp_wiring` cockpit action used to print a hardcoded
"26 tools DECLARED, 0 WIRED (no runtime handshake performed)". That string did
not depend on the state of anything. It stayed true even after the server was
fixed, which is worse than being wrong - it taught the operator to stop reading
the line.

DECLARED is counted by reading the server source: it is the number of tools the
file says it has. WIRED is counted from a real stdio MCP handshake against the
server as a subprocess. When the two disagree, the gap is the finding.

Read-only: spawns the server, calls initialize + tools/list, never calls a tool,
never writes anything.
"""
import asyncio
import ast
import io
import json
import os
import sys
from pathlib import Path

WORKSPACE = Path(os.environ.get(
    "WORKSPACE_ROOT",
    r"C:\Users\apviz\.minimax-agent\projects\SENTINEL_PRIME",
))
SERVER = WORKSPACE / "07_BACKBONE" / "mcp" / "sentinel_hub_server.py"


def declared_count() -> int:
    """Count the tool declarations in the server source.

    Parsed, not grepped. A regex over the file text counts a commented-out
    `name="sentinel_x"` line as a real tool, which is a check that reports on
    comments instead of on the thing it claims to measure.
    """
    tree = ast.parse(io.open(SERVER, encoding="utf-8").read())
    names = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        fn = node.func
        if not (isinstance(fn, ast.Attribute) and fn.attr == "Tool"):
            continue
        for kw in node.keywords:
            if kw.arg == "name" and isinstance(kw.value, ast.Constant):
                names.append(kw.value.value)
    if len(names) != len(set(names)):
        raise RuntimeError(f"duplicate tool declarations in source: {names}")
    return len(names)


async def wired_names() -> list:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    params = StdioServerParameters(
        command=sys.executable,
        args=[str(SERVER)],
        env=dict(os.environ),
    )
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.list_tools()
            return [t.name for t in result.tools]


async def main() -> int:
    if not SERVER.exists():
        print(f"MCP WIRING FAIL: server not found at {SERVER}")
        return 1

    declared = declared_count()
    print(f"DECLARED in {SERVER.name}: {declared}  (counted from source)")

    try:
        names = await asyncio.wait_for(wired_names(), timeout=60.0)
    except Exception as exc:                       # noqa: BLE001 - reported, not swallowed
        print(f"WIRED: 0  - the server did not complete a handshake: "
              f"{type(exc).__name__}: {exc}")
        print(f"RESULT: {declared} tools DECLARED, 0 WIRED")
        return 1

    print(f"WIRED: {len(names)}  (live MCP handshake: initialize + tools/list)")
    print("RESULT: " + json.dumps({
        "declared": declared,
        "wired": len(names),
        "gap": declared - len(names),
        "served": sorted(names),
    }))

    if len(names) != declared:
        print(f"MISMATCH: {declared} declared but {len(names)} served. "
              f"A tool that is declared but not served is a defect, not scaffolding.")
        return 1
    print("MATCH: every declared tool is served over MCP")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))