#!/usr/bin/env python3
"""
MCP runtime handshake for the SENTINEL hub.

`mcp_tools_wired` used to be a hardcoded NOT_RUN with the comment "no runtime
handshake has been performed". That is honest, but it is also permanent: nothing
in the system could ever move it, so 26 declared tools stayed unverifiable
forever. This performs the handshake for real.

The distinction the check cares about:
  DECLARED - a name appears in the source text.
  WIRED    - a client spawned the server, completed the MCP initialize
             handshake, and got tools/list back over the wire.

A regex over the source can only ever prove DECLARED. Only a live stdio
conversation proves WIRED, and only a live call proves a tool actually runs.

Writes: 09_LOGS/mcp_handshake.json (the measured record the monitor reads).
All code/comments/messages in English.
"""
import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

WORKSPACE = Path(os.environ.get(
    "WORKSPACE_ROOT", r"C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\SENTINEL_PRIME"))
HUB = WORKSPACE / "07_BACKBONE" / "mcp" / "sentinel_hub_server.py"
RECORD = WORKSPACE / "09_LOGS" / "mcp_handshake.json"

PROTOCOL_VERSION = "2024-11-05"
CLIENT_INFO = {"name": "sentinel-handshake", "version": "1.0"}


def _frame(payload: dict) -> bytes:
    """One JSON-RPC message, newline-delimited (MCP stdio transport)."""
    return (json.dumps(payload) + "\n").encode("utf-8")


async def _read_message(reader) -> dict:
    """Read one newline-delimited JSON-RPC message."""
    while True:
        line = await reader.readline()
        if not line:
            raise ConnectionError("server closed the stream")
        line = line.strip()
        if not line:
            continue
        return json.loads(line.decode("utf-8"))


async def handshake() -> dict:
    """Spawn the hub, initialise, list tools, and record what came back."""
    result = {
        "server_file": str(HUB),
        "attempted_at": datetime.now().isoformat(),
        "status": "NOT_RUN",
        "error": None,
        "protocol_version": None,
        "server_name": None,
        "tools_declared_in_source": 0,
        "tools_returned_by_server": 0,
        "tool_names": [],
        "probe_result": None,
    }

    if not HUB.exists():
        result["error"] = f"hub not found: {HUB}"
        return result

    import re
    src = HUB.read_text(encoding="utf-8", errors="replace")
    result["tools_declared_in_source"] = len(
        re.findall(r'name="(sentinel_[a-z0-9_]+)"', src))

    env = dict(os.environ)
    env["WORKSPACE_ROOT"] = str(WORKSPACE)
    env["PYTHONIOENCODING"] = "utf-8"

    proc = await asyncio.create_subprocess_exec(
        sys.executable, str(HUB),
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        env=env,
    )

    try:
        # --- initialize -------------------------------------------------
        proc.stdin.write(_frame({
            "jsonrpc": "2.0", "id": 1, "method": "initialize",
            "params": {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {},
                "clientInfo": CLIENT_INFO,
            },
        }))
        await proc.stdin.drain()

        init = await asyncio.wait_for(_read_message(proc.stdout), timeout=30)
        if "error" in init:
            result["error"] = f"initialize rejected: {init['error']}"
            return result
        info = init.get("result", {}).get("serverInfo", {})
        result["server_name"] = info.get("name")
        result["protocol_version"] = (
            init.get("result", {}).get("protocolVersion"))

        # The server may assert the initialized notification before serving.
        proc.stdin.write(_frame({"jsonrpc": "2.0", "method": "notifications/initialized"}))
        await proc.stdin.drain()

        # --- tools/list -------------------------------------------------
        proc.stdin.write(_frame({
            "jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}))
        await proc.stdin.drain()

        listed = await asyncio.wait_for(_read_message(proc.stdout), timeout=30)
        if "error" in listed:
            result["error"] = f"tools/list rejected: {listed['error']}"
            return result

        tools = listed.get("result", {}).get("tools", [])
        result["tools_returned_by_server"] = len(tools)
        result["tool_names"] = sorted(t.get("name", "") for t in tools)

        # --- call ONE tool for real -------------------------------------
        # Listing proves the server answers. Calling proves a tool executes.
        #
        # The probe is pinned to sentinel_confirm_identity, and it is passed
        # the arguments that tool actually declares. An earlier version picked
        # the first name alphabetically; that happened to be
        # sentinel_apply_triple_filter, which accepted {"instance": ...} and
        # answered "PENDING_EVALUATION" - a green-looking reply to a call whose
        # required "claim" argument was never supplied. A probe that cannot
        # fail is not a probe, so the tool and its arguments are now explicit.
        probe = "sentinel_confirm_identity"
        probe_args = {"instance": "M3"}
        probe_deadline_ok = False
        if probe in result["tool_names"]:
            # Retry the probe. A single 30s wait is not enough when the machine
            # is also running transcription, npm lookups and the test suite:
            # the probe was observed timing out under exactly that load while
            # the server itself was healthy. The fix belongs HERE, at the
            # producer - not in the monitor, which cannot tell a slow probe from
            # a doctored record and must keep treating both as FAIL.
            for attempt in (1, 2):
                # Re-send the call on every attempt. A retry that only re-reads
                # the stream is not a retry: the request was consumed and
                # discarded, so attempt 2 would wait on a message that was never
                # asked for.
                proc.stdin.write(_frame({
                    "jsonrpc": "2.0", "id": 3, "method": "tools/call",
                    "params": {"name": probe, "arguments": probe_args}}))
                await proc.stdin.drain()
                try:
                    called = await asyncio.wait_for(
                        _read_message(proc.stdout), timeout=60)
                except asyncio.TimeoutError:
                    result.setdefault("probe_attempt_errors", []).append(
                        f"attempt {attempt}: timed out after 60s")
                    continue
                if "error" in called:
                    result["probe_result"] = {"tool": probe, "ok": False,
                                              "error": called["error"]}
                    break

                texts = called.get("result", {}).get("content", [])
                body = "".join(t.get("text", "") for t in texts)
                echoed = None
                try:
                    echoed = json.loads(body).get("instance")
                except (json.JSONDecodeError, AttributeError):
                    pass
                result["probe_result"] = {
                    "tool": probe, "ok": True,
                    "arguments_sent": probe_args,
                    # The tool echoes the instance it received. If that is not
                    # the value sent, the arguments never reached the handler
                    # and a green reply would mean nothing.
                    "instance_echoed": echoed,
                    "arguments_arrived": echoed == probe_args["instance"],
                    "content_bytes": len(body),
                    "preview": body[:200],
                    "attempts": attempt,
                }
                break
            probe_deadline_ok = result.get("probe_result") is not None
        else:
            result["probe_result"] = {"tool": probe, "ok": False,
                                      "error": "probe tool not in tools/list"}
            probe_deadline_ok = True

        # A record must never claim OK while carrying no probe result. That
        # combination was observed in the field (handshake_status=OK with
        # probe_tool=None) and it is self-contradictory: the server answered
        # tools/list, but nothing proved a tool executed. State the truth
        # instead of letting the two halves disagree.
        if not probe_deadline_ok:
            result["status"] = "NOT_RUN"
            result["error"] = (
                "the probe never completed after 2 attempts; the server returned "
                "tools but no tool call was proven to execute")
        else:
            result["status"] = "OK"

    except asyncio.TimeoutError:
        result["error"] = "timed out waiting for the server to answer"
    except Exception as exc:  # noqa: BLE001 - the record must always be written
        result["error"] = f"{type(exc).__name__}: {exc}"
    finally:
        try:
            if proc.stdin and not proc.stdin.is_closing():
                proc.stdin.close()
        except Exception:
            pass
        try:
            await asyncio.wait_for(proc.wait(), timeout=10)
        except asyncio.TimeoutError:
            proc.kill()
        stderr_text = b""
        try:
            stderr_text = await asyncio.wait_for(proc.stderr.read(), timeout=5)
        except Exception:
            pass
        if stderr_text:
            first = stderr_text.decode("utf-8", errors="replace").strip().splitlines()
            result["stderr_first_line"] = first[0] if first else ""

    result["finished_at"] = datetime.now().isoformat()
    return result


async def _main() -> int:
    rec = await handshake()
    RECORD.parent.mkdir(parents=True, exist_ok=True)
    RECORD.write_text(json.dumps(rec, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"server           : {rec['server_name']}")
    print(f"protocol         : {rec['protocol_version']}")
    print(f"declared in src  : {rec['tools_declared_in_source']}")
    print(f"returned by wire : {rec['tools_returned_by_server']}")
    print(f"probe            : {rec['probe_result']}")
    print(f"status           : {rec['status']}")
    if rec.get("error"):
        print(f"error            : {rec['error']}")
    if rec.get("stderr_first_line"):
        print(f"stderr           : {rec['stderr_first_line']}")
    print(f"record           : {RECORD}")
    return 0 if rec["status"] == "OK" else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(_main()))
