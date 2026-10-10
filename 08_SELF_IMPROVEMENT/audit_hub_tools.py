"""Full 26-tool audit in a hermetic sandbox, including the state-mutating tools.

WORKSPACE_ROOT relocates every data path the hub touches (bimodal_state.json,
cross_instance heartbeats and mailboxes, handoff files, logs) into a temp tree,
while the CODE still loads from the real install via PYTHONPATH. So the
mutating tools can actually be exercised without touching live SENTINEL state.

This closes the gap left by the reachability audit, which had to skip 10 tools
precisely because calling them would have overwritten real state.
"""
import asyncio
import json
import os
import pathlib
import shutil
import sys
import tempfile

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REAL_SI = r"C:\Users\apviz\.minimax-agent\projects\SENTINEL_PRIME\08_SELF_IMPROVEMENT"
REAL_HUB = r"C:\Users\apviz\.minimax-agent\projects\SENTINEL_PRIME\07_BACKBONE\mcp\sentinel_hub_server.py"

SANDBOX = pathlib.Path(tempfile.mkdtemp(prefix="sentinel_sandbox_"))
(SANDBOX / "08_SELF_IMPROVEMENT").mkdir(parents=True, exist_ok=True)
(SANDBOX / "09_LOGS").mkdir(parents=True, exist_ok=True)
(SANDBOX / "07_BACKBONE" / "mcp").mkdir(parents=True, exist_ok=True)
# Only the entry file is copied; every module resolves from the real install.
shutil.copy2(REAL_HUB, SANDBOX / "07_BACKBONE" / "mcp" / "sentinel_hub_server.py")

# Baseline of real state, to prove afterwards that nothing outside moved.
LIVE_STATE = pathlib.Path(REAL_SI).parent / "09_LOGS" / "bimodal_state.json"
before = LIVE_STATE.read_bytes() if LIVE_STATE.exists() else None

MUTATING_ARGS = {
    "sentinel_set_state": {"eu_sent": True, "dor": True, "search": True, "anti_mimicry": True},
    "sentinel_workflow_enter_mode_a": {"reason": "sandbox audit"},
    "sentinel_workflow_propose_r0": {"goal": "audit", "expected_result": "no live state touched",
                                     "success_criteria": ["live state unchanged"]},
    "sentinel_workflow_ratify": {},
    "sentinel_workflow_execute": {"action": "noop audit step"},
    "sentinel_workflow_report_interruption": {"reason": "sandbox audit interruption"},
    "sentinel_create_handoff": {"summary": "sandbox audit"},
    "sentinel_log_event": {"event_type": "decision", "content": "sandbox audit run"},
    "sentinel_cross_instance_send": {"to_instance": "SENTINEL-DESKTOP", "message_type": "state_share",
                                     "payload": {"note": "sandbox"}},
    "sentinel_cross_instance_broadcast": {"message_type": "state_share", "payload": {"note": "sandbox"}},
}

READONLY_ARGS = {
    "sentinel_confirm_identity": {"instance": "AUDIT"},
    "sentinel_get_state": {}, "sentinel_workflow_state": {}, "sentinel_check_context": {},
    "sentinel_check_mimicry": {"output": "OK?"}, "sentinel_check_r_triggers": {"user_input": "hi"},
    "sentinel_apply_triple_filter": {"claim": "x", "context": "y"},
    "sentinel_make_educated_guess": {"claim": "x", "probability": 50},
    "sentinel_extract_patterns": {"text": "a b c"},
    "sentinel_universal_adapt_prompt": {"prompt": "x", "substrate": "claude-code"},
    "sentinel_universal_verify": {"output": "x", "substrate": "claude-code"},
    "sentinel_combine_perspectives": {"popy_perspective": "x", "sentinel_data": "y"},
    "sentinel_cross_instance_active": {},
    "sentinel_browser_navigate": {"url": "about:blank"},
    "sentinel_browser_scrape": {"url": "about:blank"},
    "sentinel_browser_screenshot": {"url": "about:blank", "full_page": False},
}


async def main():
    env = dict(os.environ)
    env["WORKSPACE_ROOT"] = str(SANDBOX)
    env["PYTHONPATH"] = REAL_SI + os.pathsep + env.get("PYTHONPATH", "")

    proc = await asyncio.create_subprocess_exec(
        sys.executable, str(SANDBOX / "07_BACKBONE" / "mcp" / "sentinel_hub_server.py"),
        stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE, cwd=str(SANDBOX), env=env)

    async def send(o):
        proc.stdin.write((json.dumps(o) + "\n").encode("utf-8"))
        await proc.stdin.drain()

    async def recv(t=60.0):
        line = await asyncio.wait_for(proc.stdout.readline(), timeout=t)
        if not line:
            raise RuntimeError("closed")
        return json.loads(line.decode("utf-8"))

    rows = []
    try:
        await send({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
            "protocolVersion": "2024-11-05", "capabilities": {},
            "clientInfo": {"name": "sandbox", "version": "1"}}})
        await recv()
        await send({"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}})
        await send({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
        tools = [t["name"] for t in (await recv()).get("result", {}).get("tools", [])]

        nid = 200
        for name in tools:
            args = MUTATING_ARGS.get(name, READONLY_ARGS.get(name, {}))
            nid += 1
            try:
                await send({"jsonrpc": "2.0", "id": nid, "method": "tools/call",
                            "params": {"name": name, "arguments": args}})
                res = await recv()
                if "error" in res:
                    rows.append((name, "PROTOCOL_ERROR", str(res["error"])[:50]))
                    continue
                text = res.get("result", {}).get("content", [{}])[0].get("text", "")
                low = text.lower()
                if low.startswith("unknown tool"):
                    rows.append((name, "UNREACHABLE", "Unknown tool"))
                elif low.startswith("{") and '"error"' in low:
                    rows.append((name, "REACHABLE/ERROR", text[:70].replace("\n", " ")))
                else:
                    kind = "MUTATING-OK" if name in MUTATING_ARGS else "OK"
                    rows.append((name, kind, text[:50].replace("\n", " ")))
            except Exception as e:
                rows.append((name, "EXCEPTION", str(e)[:50]))
    finally:
        try:
            proc.stdin.close()
        except Exception:
            pass
        try:
            proc.terminate()
            await asyncio.wait_for(proc.wait(), timeout=10)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass

    buckets = {}
    for n, k, d in rows:
        buckets.setdefault(k, []).append(n)
    print("sandbox: %s\n" % SANDBOX)
    print("advertised: %d\n" % len(tools))
    for k in sorted(buckets):
        print("%-16s %2d  %s" % (k, len(buckets[k]), ", ".join(sorted(buckets[k]))))
    print("\n--- detail: anything not OK / MUTATING-OK ---")
    for n, k, d in rows:
        if k not in ("OK", "MUTATING-OK"):
            print("  %-36s %-16s %s" % (n, k, d))

    after = LIVE_STATE.read_bytes() if LIVE_STATE.exists() else None
    print("\nLIVE STATE UNCHANGED: %s" % (before == after))
    print("sandbox wrote %d file(s)" % len([p for p in SANDBOX.rglob("*") if p.is_file()]))
    for p in sorted(SANDBOX.rglob("*")):
        if p.is_file():
            print("   %-58s %6d B" % (str(p.relative_to(SANDBOX)), p.stat().st_size))


asyncio.run(main())