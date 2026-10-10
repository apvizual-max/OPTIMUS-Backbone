"""
minimax_antigravity_bridge.py — OPTIMUS bridge: MiniMax Code <-> Antigravity ecosystem.

Antigravity ecosystem = Antigravity CLI (agy.exe v1.2.5) + Antigravity IDE
(Electron/Chromium) + Antigravity app (Electron) + Antigravity_Ecosystem_Terminal
container on :9878.

Popy's role for Mavis: Antigravity is now the SMALL-TASKS / AI COUNCIL back-up.
This bridge therefore prioritises (a) reading Antigravity's past work and memory,
(b) asking for a second opinion, (c) delegating narrow leaf tasks.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
for _cand in (_HERE / "shared", _HERE.parent / "shared", Path("/app/shared")):
    if (_cand / "minimax_bridge_core.py").exists():
        sys.path.insert(0, str(_cand))
        break

from minimax_bridge_core import (  # noqa: E402
    BridgeCore, Check, check_binary, check_cmd, check_health_endpoint,
    check_path_exists, find_binary, host_path, in_container, run,
    list_containers,
)

# Windows host paths. Inside the container they are bind-mounted under /host/.
_W_AGY_CLI = r"C:\Users\apviz\AppData\Local\agy\bin\agy.exe"
_W_DOCKER = r"C:\Program Files\Docker\Docker\resources\bin\docker.exe"
_W_ROAMING = r"C:\Users\apviz\AppData\Roaming\Antigravity"
_W_IDE = r"C:\Users\apviz\AppData\Local\Programs\Antigravity IDE"
_W_APP = r"C:\Users\apviz\AppData\Local\Programs\antigravity"
_W_LOCAL = r"C:\Users\apviz\AppData\Local\agy"

AGY_CLI = find_binary(_W_AGY_CLI) or _W_AGY_CLI
DOCKER = find_binary(_W_DOCKER) or _W_DOCKER
AGY_ROAMING = host_path(_W_ROAMING)
AGY_IDE = host_path(_W_IDE)
AGY_APP = host_path(_W_APP)
AGY_LOCAL = host_path(_W_LOCAL)
AGY_TERMINAL = "http://host.docker.internal:9878" if in_container() else "http://127.0.0.1:9878"


class AntigravityBridge(BridgeCore):
    BRIDGE_NAME = "minimax-antigravity-bridge"
    TARGET = "antigravity"
    TARGET_CLI = AGY_CLI
    PORT = int(os.environ.get("BRIDGE_PORT", "8802"))

    def __init__(self) -> None:
        super().__init__()
        # Delegate specs must carry the WINDOWS path — Mavis runs them on the host.
        self.TARGET_CLI = _W_AGY_CLI
        self.healers = {"log_rotation": self.h_logs}
        self._register()
        self.delegates({
            "description": "Dispatch a prompt to the Antigravity CLI agent.",
            "argv": ["{cli}", "--print", "{prompt}"],
            "notes": [
                "agy --print (-p) runs one prompt non-interactively.",
                "Use --output-format json when you need structured output.",
                "Use --conversation <id> to resume Antigravity's own past work.",
                "Use --add-dir <path> to grant it a workspace.",
                "Popy's rule: small tasks and AI-council opinions only.",
            ],
            "body": {
                "prompt": "string (required)",
                "project": "optional Antigravity project id/name",
                "model": "optional model override",
                "timeout": "int seconds, default 300",
            },
        })
        self.audit({
            "agy_app_storage": str(AGY_ROAMING / "app_storage.json"),
            "agy_logs": str(AGY_ROAMING / "logs"),
            "agy_local_storage": str(AGY_ROAMING / "Local Storage"),
            "agy_session_storage": str(AGY_ROAMING / "Session Storage"),
            "agy_cli_bin": str(AGY_LOCAL / "bin"),
        })

    # ---------------- checks ----------------
    def _register(self) -> None:
        def c_agy_present() -> Check:
            p = Path(AGY_CLI)
            if p.exists():
                sz = p.stat().st_size
                return Check("bin.agy", "ok", "agy CLI present", f"{p} ({sz} B)")
            return Check("bin.agy", "fail", "agy CLI not found", AGY_CLI,
                         remedy="Bind-mount AppData\\Local\\agy into the bridge.")
        self.check(c_agy_present)

        def c_version() -> Check:
            """A Linux container cannot exec agy.exe. Report binary evidence instead."""
            p = Path(AGY_CLI)
            if not p.exists():
                return Check("agy.version", "fail", "agy binary missing", str(p))
            return Check("agy.version", "warn",
                         "version probe is host-side (bridge cannot exec agy.exe)",
                         f"{p.name} {p.stat().st_size} B",
                         remedy="Run: & '" + _W_AGY_CLI + "' --version")

        def c_ide() -> Check:
            exe = AGY_IDE / "Antigravity IDE.exe"
            if exe.exists():
                return Check("agy.ide", "ok", "Antigravity IDE installed", str(exe))
            return Check("agy.ide", "warn", "Antigravity IDE not found", str(exe))

        def c_app() -> Check:
            exe = AGY_APP / "Antigravity.exe"
            if exe.exists():
                return Check("agy.app", "ok", "Antigravity app installed", str(exe))
            return Check("agy.app", "warn", "Antigravity app not found", str(exe))

        def c_agents_list() -> Check:
            """Cannot exec agy.exe in a Linux container; surface the host command."""
            return Check("agy.agents", "warn",
                         "agent list is host-side (bridge cannot exec agy.exe)",
                         remedy="Run: & '" + _W_AGY_CLI + "' agent")

        def c_memory_readable() -> Check:
            """Antigravity keeps conversation/project state under AppData\\Roaming."""
            if not AGY_ROAMING.exists():
                return Check("agy.memory", "fail", "Antigravity roaming dir missing",
                             str(AGY_ROAMING))
            storage = AGY_ROAMING / "Local Storage"
            size = 0
            files = 0
            if storage.exists():
                for f in storage.rglob("*"):
                    if f.is_file():
                        files += 1
                        try:
                            size += f.stat().st_size
                        except OSError:
                            pass
            return Check("agy.memory", "ok",
                         f"Antigravity state readable ({files} files, {size} B)",
                         str(AGY_ROAMING),
                         evidence={"files": files, "bytes": size})

        def c_past_work() -> Check:
            app_storage = AGY_ROAMING / "app_storage.json"
            if not app_storage.exists():
                return Check("agy.past_work", "warn", "app_storage.json absent",
                             str(app_storage))
            try:
                import json
                data = json.loads(app_storage.read_text(encoding="utf-8", errors="replace"))
            except Exception as e:  # noqa: BLE001
                return Check("agy.past_work", "fail", "app_storage.json unreadable",
                             f"{type(e).__name__}: {e}")
            keys = list(data) if isinstance(data, dict) else []
            convos = [k for k in keys if "convo" in k.lower() or "session" in k.lower()]
            return Check("agy.past_work", "ok",
                         f"{len(keys)} state keys, {len(convos)} conversation/session keys",
                         evidence={"sample_keys": keys[:12]})

        def c_terminal_container() -> Check:
            ok, rows, err = list_containers(prefix="Antigravity_Ecosystem_Terminal")
            if not ok:
                return Check("agy.terminal_container", "warn",
                             "docker not reachable in bridge", err,
                             remedy="Check host-side: docker ps --filter name=Antigravity")
            if not rows:
                return Check("agy.terminal_container", "warn",
                             "Antigravity_Ecosystem_Terminal not found")
            r = rows[0]
            return Check("agy.terminal_container",
                         "ok" if r["status"] == "running" else "warn",
                         f"Antigravity_Ecosystem_Terminal: {r['status']}", evidence=r)

        for fn in (c_version, c_ide, c_app, c_agents_list, c_memory_readable,
                   c_past_work, c_terminal_container):
            self.check(fn)
        self.check(check_health_endpoint(AGY_TERMINAL, "agy.terminal_http",
                                         "Antigravity Ecosystem Terminal :9878"))
        self.check(check_path_exists("agy.local_bin", str(AGY_LOCAL / "bin"),
                                     "agy bin dir"))

    # ---------------- healers ----------------
    def h_logs(self, _p: dict) -> Check:
        """Report log sizes and stale files. Read-only; never deletes."""
        logdir = AGY_ROAMING / "logs"
        if not logdir.exists():
            return Check("agy.logs", "warn", "no Antigravity logs dir", str(logdir))
        big = []
        total = 0
        for f in logdir.rglob("*"):
            if f.is_file():
                s = f.stat().st_size
                total += s
                if s > 5_000_000:
                    big.append((str(f), s))
        return Check("agy.logs", "ok", f"{total} B of logs",
                     f"{len(big)} files > 5 MB",
                     evidence={"big": big[:10], "total_bytes": total})


if __name__ == "__main__":
    AntigravityBridge().serve()
