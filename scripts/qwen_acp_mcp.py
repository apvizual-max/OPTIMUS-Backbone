#!/usr/bin/env python
"""
qwen_acp_mcp.py -- ACP -> MCP adapter for Qwen Code.

WHY THIS EXISTS
---------------
Mavis had an MCP entry `qwen-mcp-http` pointing at
    http://localhost:8765/mcp
That endpoint does not exist. Qwen 0.19.2 does NOT expose an MCP server
transport. It exposes:
    /health          200  {"status":"ok"}
    /                200  Web Shell UI
    /acp             406  WebSocket  <-- Agent Client Protocol, the real surface
    /mcp             404  <-- what the old entry assumed
    /workspace/mcp   200  a DIAGNOSTIC of Qwen's own MCP-client servers,
                          not a transport for external clients

So `qwen-mcp-http` was built on a protocol misconception. This adapter speaks
MCP on stdio (what Mavis consumes) and drives Qwen over ACP.

THE ONE THING THAT ACTUALLY BREAKS
----------------------------------
`session/new` REQUIRES an `mcpServers` array. Omit it and Qwen answers a
generic `Internal error`; the real validation message only appears on the
stdio transport:

    "mcpServers": Invalid input: expected array, received undefined

With `mcpServers: []` sessions are created fine. This is the fix.

KNOWN EXTERNAL BLOCKER (diagnosed, not fixable from here)
--------------------------------------------------------
Qwen's active model provider is a LOCAL Ollama model
(`qwen2.5-coder:1.5b` at http://127.0.0.1:11434). Ollama is NOT installed on
this machine, so `session/prompt` returns
    {"code":-32603,"details":"Connection error."}
That is the model provider being unreachable, not a protocol fault.
Run `qwen_doctor` for the live confirmation.
"""
from __future__ import annotations

import asyncio
import json
import os
import subprocess
import sys
import threading
import time
import uuid
from typing import Any

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:  # pragma: no cover
    print("FATAL: the 'mcp' package is required. Run with the Hermes venv python:\n"
          r"  C:\Users\apviz\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe",
          file=sys.stderr)
    raise

DEFAULT_CWD = os.environ.get(
    "OPTIMUS_WORKSPACE", r"C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard"
)
QWEN_CMD = os.environ.get(
    "QWEN_CMD", r"C:\Users\apviz\AppData\Local\qwen-code\bin\qwen.cmd"
)
ACPPROMPT_TIMEOUT = float(os.environ.get("QWEN_ACP_TIMEOUT", "180"))

mcp = FastMCP("qwen-acp-adapter")


# --------------------------------------------------------------------------
# ACP client over stdio
# --------------------------------------------------------------------------
class AcpSession:
    """
    One `qwen --acp` child, one JSON-RPC session.

    stdio is used rather than the WebSocket daemon because it is the transport
    that surfaces Qwen's REAL validation errors. The daemon collapses them into
    an opaque `Internal error` and then kills the child with SIGTERM.
    """

    def __init__(self, cwd: str = DEFAULT_CWD) -> None:
        self.cwd = cwd
        self.proc: subprocess.Popen | None = None
        self._id = 0
        self.session_id: str | None = None
        self.models: dict[str, Any] = {}
        self.stderr_tail: list[str] = []
        self._read_err = threading.Thread(target=self._drain_stderr, daemon=True)
        self._read_err.start()

    # -- plumbing ----------------------------------------------------------
    def _drain_stderr(self) -> None:
        if not self.proc or not self.proc.stderr:
            return
        for line in self.proc.stderr:
            self.stderr_tail.append(line.rstrip())
            del self.stderr_tail[:-40]

    def _send(self, obj: dict) -> None:
        assert self.proc and self.proc.stdin
        self.proc.stdin.write(json.dumps(obj) + "\n")
        self.proc.stdin.flush()

    def _call(self, method: str, params: dict | None = None,
              timeout: float = 60.0) -> dict:
        if not self.proc or self.proc.poll() is not None:
            raise RuntimeError("qwen ACP child is not running")
        self._id += 1
        mid = self._id
        msg: dict[str, Any] = {"jsonrpc": "2.0", "id": mid, "method": method}
        if params is not None:
            msg["params"] = params
        self._send(msg)
        deadline = time.time() + timeout
        while time.time() < deadline:
            if self.proc.poll() is not None:
                raise RuntimeError(
                    "qwen ACP child exited (code=%s)\n%s"
                    % (self.proc.returncode, "\n".join(self.stderr_tail[-8:]))
                )
            line = self.proc.stdout.readline()
            if not line:
                continue
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            if d.get("id") == mid:
                return d
        raise TimeoutError(f"{method} timed out after {timeout}s")

    # -- lifecycle ---------------------------------------------------------
    def start(self) -> None:
        self.proc = subprocess.Popen(
            [QWEN_CMD, "--acp"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, encoding="utf-8", errors="replace",
            cwd=self.cwd, bufsize=1,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        self._call("initialize", {
            "protocolVersion": 1,
            "clientCapabilities": {"fs": {"readTextFile": True, "writeTextFile": True}},
        }, timeout=45)
        # mcpServers is REQUIRED. Without it Qwen returns a bare Internal error.
        r = self._call("session/new", {
            "cwd": self.cwd,
            "mcpServers": [],          # <-- the fix
        }, timeout=60)
        if "error" in r:
            raise RuntimeError("session/new failed: %s" % json.dumps(r["error"]))
        self.session_id = r["result"]["sessionId"]
        self.models = r["result"].get("models", {})

    def close(self) -> None:
        if self.proc and self.proc.poll() is None:
            try:
                self.proc.kill()
            except Exception:
                pass

    def prompt(self, text: str, timeout: float = ACPPROMPT_TIMEOUT) -> str:
        r = self._call("session/prompt", {
            "sessionId": self.session_id,
            "prompt": [{"type": "text", "text": text}],
        }, timeout=timeout)
        if "error" in r:
            err = r["error"]
            detail = (err.get("data") or {}).get("details") if isinstance(err.get("data"), dict) else None
            raise RuntimeError("prompt failed: %s%s" % (err.get("message"), f" ({detail})" if detail else ""))
        return r.get("result", {}).get("stopReason", "") or "ok"


# --------------------------------------------------------------------------
# Qwen extension methods: daemon WebSocket only
# --------------------------------------------------------------------------
ACP_WS_URL = os.environ.get("QWEN_ACP_WS", "ws://127.0.0.1:8765/acp")


async def _ws_call(method: str, params: dict | None = None, timeout: float = 45.0) -> dict:
    """
    Call a method over the daemon's ACP WebSocket.

    The `_qwen/*` extension methods are registered on the `qwen serve` DAEMON
    only. Verified 2026-10-02:
        stdio     -> {"code":-32601,"message":"\"Method not found\""}
        websocket -> {"result":{...}}
    So those tools must NOT go through the stdio child.
    """
    import websockets
    async with websockets.connect(ACP_WS_URL, max_size=16 * 1024 * 1024) as ws:
        await ws.send(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize",
                                  "params": {"protocolVersion": 1, "clientCapabilities": {}}}))
        await asyncio.wait_for(ws.recv(), timeout)
        await ws.send(json.dumps({"jsonrpc": "2.0", "id": 2, "method": method,
                                  "params": params or {}}))
        while True:
            raw = await asyncio.wait_for(ws.recv(), timeout)
            try:
                d = json.loads(raw)
            except json.JSONDecodeError:
                continue
            if d.get("id") == 2:
                return d


def ws_call(method: str, params: dict | None = None, timeout: float = 45.0) -> dict:
    """
    Sync wrapper that works from inside a running event loop.

    The MCP server is async, so `asyncio.run()` here would raise
    "asyncio.run() cannot be called from a running event loop". Run the
    coroutine on its own loop in a worker thread instead. Reports the real
    cause instead of returning silent nulls.
    """
    box: dict[str, Any] = {}

    def _run() -> None:
        try:
            box["r"] = asyncio.run(_ws_call(method, params, timeout))
        except Exception as e:  # noqa: BLE001
            box["r"] = {"error": {
                "code": "daemon_unreachable",
                "message": f"{type(e).__name__}: {e}",
                "hint": f"the _qwen/* methods need `qwen serve` on {ACP_WS_URL}. "
                        f"Start it with: optimus qwen serve",
            }}

    t = threading.Thread(target=_run, daemon=True)
    t.start()
    t.join(timeout + 10)
    if "r" not in box:
        return {"error": {"code": "timeout",
                          "message": f"{method} did not answer within {timeout}s",
                          "hint": f"is the daemon up on {ACP_WS_URL}?"}}
    return box["r"]


# --------------------------------------------------------------------------
# Tools
# --------------------------------------------------------------------------
@mcp.tool()
def qwen_doctor() -> str:
    """
    Full Qwen diagnosis: ACP reachable? session creatable? model provider alive?
    Use this before assuming Qwen is broken -- it names the actual failure layer.
    """
    out: dict[str, Any] = {"acp_transport": "unknown", "session": "unknown",
                           "model_provider": "unknown", "findings": []}
    s = AcpSession()
    try:
        s.start()
        out["acp_transport"] = "ok"
        out["session"] = "ok"
        out["session_id"] = s.session_id
        out["current_model"] = s.models.get("currentModelId")
        out["available_models"] = [m.get("modelId") for m in
                                   s.models.get("availableModels", [])]
        try:
            s.prompt("Reply with exactly: QWEN-ACP-OK", timeout=45)
            out["model_provider"] = "ok"
        except Exception as e:
            out["model_provider"] = "unreachable"
            out["findings"].append(
                "session/prompt failed: %s. The active provider '%s' is a LOCAL "
                "Ollama endpoint (127.0.0.1:11434) and Ollama is not installed on "
                "this machine. Fix by installing+starting Ollama, or by completing "
                "Qwen cloud OAuth so 'coder-model(qwen-oauth)' becomes active."
                % (e, out.get("current_model"))
            )
    except Exception as e:
        out["session"] = "failed"
        out["findings"].append("ACP session creation failed: %s" % e)
        out["stderr"] = s.stderr_tail[-8:]
    finally:
        s.close()
    return json.dumps(out, indent=2, ensure_ascii=False)


@mcp.tool()
def qwen_prompt(prompt: str, timeout: float = ACPPROMPT_TIMEOUT) -> str:
    """
    Send one prompt to Qwen over ACP and return its reply.

    Raises a diagnostic error if the model provider is unreachable -- that is an
    environment fault (no Ollama / no OAuth), not a protocol fault.
    """
    s = AcpSession()
    try:
        s.start()
        reply = s.prompt(prompt, timeout=timeout)
        return json.dumps({"ok": True, "session": s.session_id,
                           "model": s.models.get("currentModelId"),
                           "stop_reason": reply})
    finally:
        s.close()


@mcp.tool()
def qwen_session_probe() -> str:
    """Create an ACP session and report what Qwen says about itself, without prompting."""
    s = AcpSession()
    try:
        s.start()
        return json.dumps({"ok": True, "session_id": s.session_id,
                           "models": s.models}, indent=2, ensure_ascii=False)
    finally:
        s.close()


@mcp.tool()
def qwen_auth_device_flow_start() -> str:
    """
    Start the Qwen OAuth device flow and return the one-click verification URL.

    Routed over the DAEMON WebSocket: this is a `_qwen/*` extension and does not
    exist on the stdio transport (it answers -32601 there). The flow expires in
    ~15 minutes; re-run for a fresh code.
    """
    r = ws_call("_qwen/workspace/auth/device_flow/start", {"providerId": "qwen-oauth"})
    if "error" in r and isinstance(r["error"], dict) and r["error"].get("code") == -32601:
        return json.dumps({"ok": False, "error": "_qwen/* is not available on the stdio "
                              "transport, and the daemon did not answer."}, indent=2)
    return json.dumps(r, indent=2, ensure_ascii=False)


@mcp.tool()
def qwen_auth_status() -> str:
    """Qwen OAuth status plus the list of configured model providers (daemon WebSocket)."""
    status = ws_call("_qwen/workspace/auth/status")
    providers = ws_call("_qwen/workspace/providers")
    # Never hand back silent nulls: an error object is the information.
    out = {
        "auth": status.get("result") if "result" in status else status.get("error"),
        "providers": providers.get("result") if "result" in providers else providers.get("error"),
    }
    if out["auth"] is None and out["providers"] is None:
        out["ok"] = False
        out["hint"] = f"daemon not answering on {ACP_WS_URL}; run: optimus qwen serve"
    else:
        out["ok"] = True
    return json.dumps(out, indent=2, ensure_ascii=False)


@mcp.tool()
def qwen_workspace_tools() -> str:
    """List the tools/filesystem capabilities Qwen exposes over its ACP extensions."""
    r = ws_call("_qwen/workspace/tools")
    if "error" in r and isinstance(r["error"], dict) and r["error"].get("code") == -32601:
        return json.dumps({"ok": False,
                           "error": "_qwen/* is not available on the stdio transport"},
                          indent=2)
    return json.dumps(r.get("result", r), indent=2, ensure_ascii=False)[:20000]


if __name__ == "__main__":
    mcp.run()
