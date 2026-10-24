#!/usr/bin/env python3
"""
Build a narrow MCP server that serves a chosen slice of the SENTINEL hub.

Why this module exists
----------------------
`OPTIMUS_MCP_CONFIG.json` declares five servers by name, each with a
description of the capability it owns. None of the five files existed on disk,
while every one of those capabilities already lived inside
`sentinel_hub_server.py` as a named tool. So the declarations were true about
the intent and false about the disk - a promise with nothing behind it.

The repair is neither to repoint the config at the hub nor to delete the
declarations. It is to build what the config already asks for: five servers,
each serving the tools that carry its capability, over ONE implementation of
each capability. That implementation stays in `sentinel_hub_server.py`; a slice
delegates and never copies. A copy would drift, and the first divergence would
be two servers giving different answers to the same question.

A caller that only wants SENTINEL state gets a server with three tools instead of
twenty-six. That is the whole point of a slice: same truth, smaller surface.

One hard constraint, because breaking it fails silently
-------------------------------------------------------
stdio is the transport, so **stdout belongs to the MCP protocol**. A stray
`print()` in these servers corrupts the JSON-RPC stream and the client drops the
connection with no useful diagnostic. Anything a human needs to read goes to
stderr.
"""
import asyncio
import sys
from pathlib import Path
from typing import Iterable, List, Tuple

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import sentinel_hub_server as hub  # noqa: E402  (path set above, on purpose)


def _slug(server_name: str) -> str:
    return server_name.lower().replace(' ', '-')


async def plan(server_name: str, tool_names: Iterable[str]) -> Tuple[list, List[str]]:
    """Resolve a slice name list against the hub's declared tools.

    Returns (tools, missing). `missing` is never empty or ignored: a slice that
    names a tool the hub does not declare would start and then serve a hole,
    which is exactly the class of quiet failure this whole exercise is about.
    """
    declared = {t.name: t for t in await hub.list_tools()}
    wanted = list(tool_names)
    missing = [n for n in wanted if n not in declared]
    return [declared[n] for n in wanted if n in declared], missing


async def serve(server_name: str, tool_names: Iterable[str],
                version: str = '1.0.0') -> int:
    """Run `server_name` as a stdio MCP server exposing only `tool_names`."""
    from mcp.server.mcpserver import MCPServer

    tools, missing = await plan(server_name, tool_names)
    if missing:
        # stderr, not stdout: stdout is the protocol channel.
        print(f'{server_name}: cannot serve, the hub does not declare '
              f'{missing}', file=sys.stderr)
        return 1

    server = MCPServer(server_name, version=version,
                       tools=[hub._register(t) for t in tools])
    # The six sentinel_workflow_* bodies attach their singleton to the hub's
    # module global `server`. Binding it here keeps that invariant true no
    # matter which slice is running, so adding a workflow tool to a slice later
    # cannot silently reintroduce the NameError this originally caused.
    hub.server = server
    await server.run_stdio_async()
    return 0


def main(server_name: str, tool_names: Iterable[str]) -> None:
    raise SystemExit(asyncio.run(serve(server_name, tool_names)))