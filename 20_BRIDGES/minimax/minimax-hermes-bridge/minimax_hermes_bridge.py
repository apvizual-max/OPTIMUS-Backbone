"""
minimax_hermes_bridge.py Ã¢â‚¬â€ OPTIMUS bridge: MiniMax Code <-> Hermes ecosystem.

Hermes ecosystem = Hermes CLI agent (hermes.exe) + Hermes Desktop app + 31
hermes-mcp-* Docker containers + the hermes-sentinel-daemon guardrail.

Mavis uses this container as the system DOCTOR for Hermes: /doctor diagnoses
config drift, venv currency, container health, MCP fleet, sentinel enforcement.
/audit reads Hermes memory + logs. /delegate dispatches work to the Hermes CLI.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

_HERE = Path(__file__).resolve().parent
for _cand in (_HERE / "shared", _HERE.parent / "shared", Path("/app/shared")):
    if (_cand / "minimax_bridge_core.py").exists():
        sys.path.insert(0, str(_cand))
        break

from minimax_bridge_core import (  # noqa: E402
    BridgeCore, Check, check_binary, check_cmd, check_health_endpoint,
    check_path_exists, find_binary, find_first, host_path, in_container, run,
    check_docker, list_containers, restart_container,
)

# Windows host paths. Inside the container they are bind-mounted under /host/.
_W_HERMES_BASE = r"C:\Users\apviz\AppData\Local\hermes"
_W_HERMES_BIN = _W_HERMES_BASE + r"\bin\hermes.exe"
_W_HERMES_VENV = _W_HERMES_BASE + r"\hermes-agent\venv\Scripts\hermes.exe"
_W_PY = _W_HERMES_BASE + r"\hermes-agent\venv\Scripts\python.exe"
_W_DOCKER = r"C:\Program Files\Docker\Docker\resources\bin\docker.exe"
_W_HERMES_HOME = r"C:\Users\apviz\.hermes"
_W_SENTINEL = (_W_HERMES_BASE
               + r"\mcp-servers\custom\sentinel-daemon\sentinel_daemon.py")

HERMES_CLI = find_binary(_W_HERMES_BIN, _W_HERMES_VENV) or _W_HERMES_BIN
PY_EXE = find_binary(_W_PY) or _W_PY
DOCKER = find_binary(_W_DOCKER) or _W_DOCKER
HERMES_HOME = host_path(_W_HERMES_HOME)
# The live config.yaml lives at the Hermes BASE dir, not under ~/.hermes.
HERMES_CFG = (find_first(_W_HERMES_BASE + r"\config.yaml",
                         _W_HERMES_HOME + r"\config.yaml",
                         _W_HERMES_BASE + r"\hermes-agent\config.yaml")
              or host_path(_W_HERMES_BASE, "config.yaml"))
HERMES_ROOT = host_path(_W_HERMES_BASE, "hermes-agent")
HERMES_SRC = host_path(_W_HERMES_BASE, "hermes-agent")
SENTINEL_SRC = host_path(_W_SENTINEL)
# The daemon's HTTP health server binds inside its own container only (port not
# published), so it is NOT probed from here. Container liveness covers it.


class HermesBridge(BridgeCore):
    BRIDGE_NAME = "minimax-hermes-bridge"
    TARGET = "hermes"
    TARGET_CLI = HERMES_CLI
    PORT = int(os.environ.get("BRIDGE_PORT", "8801"))

    def __init__(self) -> None:
        super().__init__()
        # Delegate specs must carry the WINDOWS path — Mavis runs them on the host.
        self.TARGET_CLI = _W_HERMES_BIN
        self.healers = {
            "sync_venv": self.h_sync,
            "heal_enforcement": self.h_enforce,
            "restart_container": self.h_restart,
        }
        self._register()
        self.delegates({
            "description": "Dispatch a prompt to the Hermes CLI agent in print mode.",
            "argv": ["{cli}", "-z", "{prompt}"],
            "notes": [
                "Hermes print flag is -z (per hermes --help).",
                "Model follows cli-config.yaml: MiniMax-M3 via minimax-oauth.",
                "Set 'model' in the body only if overriding the profile default.",
            ],
            "body": {"prompt": "string (required)", "timeout": "int seconds, default 300"},
        })
        self.audit({
            "hermes_config": str(HERMES_HOME / "config.yaml"),
            "hermes_cli_model": str(HERMES_SRC / "cli-config.yaml"),
            "hermes_config": str(HERMES_CFG),
            "hermes_dotenv": str(HERMES_ROOT / ".env"),
            "hermes_history": str(HERMES_HOME / ".hermes_history"),
            "sentinel_daemon_src": str(SENTINEL_SRC),
            "sentinel_logs": str(HERMES_ROOT / "logs"),
            "gateway_state": str(HERMES_ROOT / "gateway_state.json"),
            "whatsapp_session": str(HERMES_ROOT / "whatsapp" / "session"),
        })

    # ---------------- checks ----------------
    def _check_hermes_present(self) -> Check:
        p = Path(HERMES_CLI)
        if p.exists():
            return Check("bin.hermes", "ok", "hermes CLI located", str(p))
        return Check("bin.hermes", "fail", "hermes CLI not found", HERMES_CLI,
                     remedy="Bind-mount C:\\Users\\apviz\\AppData\\Local\\hermes\\bin into the bridge.")

    def _check_version(self) -> Check:
        """Read model/provider evidence from the live config."""
        import re as _re
        # cli-config.yaml is a symlink into the real config. A symlink is only
        # BROKEN when it fails to resolve -- merely being a symlink is not a
        # fault. The old test used `is_symlink()` alone and so reported a
        # healthy link as broken on every single run.
        cli = HERMES_SRC / "cli-config.yaml"
        is_link = cli.is_symlink()
        broken = is_link and not cli.exists()
        if broken:
            cand = HERMES_CFG
            if cand.exists() and cand.stat().st_size > 0:
                txt = cand.read_text(encoding="utf-8", errors="replace")
                m = _re.search(r"default:\s*(\S+)", txt) or _re.search(
                    r"default:\s*\n\s+(\S+)", txt)
                prov = _re.search(r"provider:\s*(\S+)", txt)
                base = _re.search(r"base_url:\s*'?([^'\n]+)'?", txt)
                return Check(
                    "hermes.version", "warn",
                    f"cli-config.yaml is a symlink that does not resolve inside the "
                    f"Linux container; reading {cand.name} directly",
                    f"default={m.group(1) if m else '?'} "
                    f"provider={prov.group(1) if prov else '?'} "
                    f"base={base.group(1) if base else '?'}",
                    remedy=("Verify host-side only if Hermes fails to start: "
                            "Get-Item cli-config.yaml | Select LinkType,Target. "
                            "A Windows link is NOT resolvable from the bridge, "
                            "so this warning is expected on a bind mount."),
                    evidence={"symlink_unresolved_in_container": True,
                              "read_from": str(cand),
                              "note": "container-side view; not proof of host fault"},
                )
        if not cli.exists():
            return Check("hermes.version", "fail", "no cli-config.yaml on disk",
                         str(HERMES_SRC), remedy="Hermes writes it on first run.")
        txt = cli.read_text(encoding="utf-8", errors="replace")
        m = _re.search(r"default:\s*(\S+)", txt)
        prov = _re.search(r"provider:\s*(\S+)", txt)
        base = _re.search(r"base_url:\s*'?([^'\n]+)'?", txt)
        if m:
            return Check("hermes.version", "ok",
                         f"default={m.group(1)} provider={prov.group(1) if prov else '?'} "
                         f"base={base.group(1) if base else '?'}",
                         evidence={"source": str(cli), "default_model": m.group(1),
                                   "symlink": is_link})
        return Check("hermes.version", "warn", "cli-config.yaml has no default:",
                     str(cli))


    def _check_venv_currency(self) -> Check:
        """
        The single most valuable check: venv drift makes every real command hang.

        A Linux container cannot exec the Windows venv python, so currency is
        inferred from install-stamp.json (written by the installer) vs uv.lock.
        The previous version looked for a non-existent '.venv-stamp' file, so
        `stale` was always False and this reported a vacuous "ok" even when
        the venv was out of date. Absence of a stamp is now a warn, not an ok.
        """
        import json as _json
        lock = HERMES_ROOT / "uv.lock"
        stamp = HERMES_ROOT / "install-stamp.json"
        if not lock.exists():
            return Check("hermes.venv_currency", "warn", "uv.lock not found",
                         str(lock), remedy="Host-side probe needed.")
        lm = lock.stat().st_mtime
        if not stamp.exists():
            return Check("hermes.venv_currency", "warn",
                         "install-stamp.json not found; venv currency unverifiable",
                         str(stamp),
                         remedy="Host-side: run hermes update, or the bridge /heal sync_venv.",
                         evidence={"lock_mtime": lm, "stamp_mtime": None})
        sm = stamp.stat().st_mtime
        stale = sm < lm
        meta: dict[str, Any] = {}
        try:
            meta = _json.loads(stamp.read_text(encoding="utf-8", errors="replace"))
        except Exception as e:  # noqa: BLE001
            meta = {"parse_error": f"{type(e).__name__}: {e}"}
        dirty = bool(meta.get("dirty"))
        ver = meta.get("displayVersion") or meta.get("baseVersion") or "?"
        detail = (f"{ver}  lock={lm:.0f} stamp={sm:.0f}"
                  + ("  [dirty tree]" if dirty else ""))
        if stale:
            return Check("hermes.venv_currency", "fail", "venv STALE vs uv.lock",
                         detail,
                         remedy="Host-side: hermes update, or the bridge /heal sync_venv.",
                         evidence={"lock_mtime": lm, "stamp_mtime": sm,
                                   "version": ver, "dirty": dirty})
        sev = "warn" if dirty else "ok"
        return Check("hermes.venv_currency", sev,
                     "venv stamp current vs lockfile" if not dirty
                     else "venv stamp current, but Hermes source tree is dirty",
                     detail,
                     remedy=("Hermes checkout has uncommitted changes; they will be "
                             "reverted by the next `hermes update`."
                             if dirty else ""),
                     evidence={"lock_mtime": lm, "stamp_mtime": sm,
                               "version": ver, "dirty": dirty,
                               "commit": meta.get("commit")})


    def _check_hang_probe(self) -> Check:
        """
        A Linux container cannot exec hermes.exe, so this reports the host-side
        probe command and the drift evidence instead of a live call.
        """
        import re as _re
        cli = HERMES_SRC / "cli-config.yaml"
        if not cli.exists():
            cli = HERMES_ROOT / "cli-config.yaml"
        prov = base = "?"
        if cli.exists():
            txt = cli.read_text(encoding="utf-8", errors="replace")
            m = _re.search(r"provider:\s*(\S+)", txt)
            b = _re.search(r"base_url:\s*'?([^'\n]+)'?", txt)
            prov = m.group(1) if m else "?"
            base = b.group(1) if b else "?"
        return Check(
            "hermes.status", "warn",
            "status probe is host-side (bridge cannot exec hermes.exe)",
            f"provider={prov} base_url={base}",
            remedy='Run: & \'' + _W_HERMES_BIN + '\' status',
        )


    def _check_containers(self) -> Check:
        ok, rows, err = list_containers(prefix="hermes-mcp-")
        if not ok:
            return Check("hermes.containers", "warn", "docker not reachable in bridge",
                         err, remedy="Count the fleet host-side via bash.")
        if not rows:
            return Check("hermes.containers", "fail", "no hermes-mcp-* containers",
                         "The load-bearing swarm is absent. NEVER prune -a.")
        down = [r for r in rows if r["status"] != "running"]
        if down:
            return Check("hermes.containers", "warn",
                         f"{len(rows)} containers, {len(down)} not running",
                         "; ".join(f"{r['name']}({r['status']})" for r in down[:6]),
                         remedy="Diagnose first, restart ONE container second.",
                         evidence={"count": len(rows)})
        return Check("hermes.containers", "ok",
                     f"{len(rows)} hermes-mcp-* containers running",
                     evidence={"count": len(rows)})


    def _check_sentinel_enforcement(self) -> Check:
        """Read the 4 REQUIRED_ENFORCEMENT invariants the daemon self-heals."""
        try:
            import yaml
        except ImportError:
            return Check("hermes.sentinel_enforcement", "warn",
                         "PyYAML not installed in this interpreter",
                         "Run the doctor inside the container (requirements.txt ships PyYAML).")
        cfg = HERMES_CFG
        if not cfg.exists():
            return Check("hermes.sentinel_enforcement", "warn",
                         "config.yaml not found",
                         str(cfg), remedy="Start Hermes once so it writes config.")
        try:
            data = yaml.safe_load(cfg.read_text(encoding="utf-8", errors="replace")) or {}
        except Exception as e:  # noqa: BLE001
            return Check("hermes.sentinel_enforcement", "fail",
                         "config.yaml unreadable", f"{type(e).__name__}: {e}")
        enf = (data.get("enforcement") or {}) if isinstance(data, dict) else {}
        req = {"enabled": True, "guardian_strict": True,
               "trigger_detection": True, "auto_recalibrate": True}
        bad = {k: enf.get(k) for k, v in req.items() if enf.get(k) is not v}
        if bad:
            return Check("hermes.sentinel_enforcement", "fail",
                         "Sentinel enforcement invariants violated",
                         f"expected {req}, found {enf}",
                         remedy="POST /heal {\"action\":\"heal_enforcement\"}")
        return Check("hermes.sentinel_enforcement", "ok",
                     "all 4 enforcement invariants hold", evidence=enf)


    def _check_sentinel_source(self) -> Check:
        if SENTINEL_SRC.exists():
            return Check("hermes.sentinel_source", "ok",
                         "sentinel_daemon.py present",
                         f"{SENTINEL_SRC} ({SENTINEL_SRC.stat().st_size} B)")
        return Check("hermes.sentinel_source", "fail",
                     "sentinel_daemon.py missing", str(SENTINEL_SRC))


    def _check_sentinel_container(self) -> Check:
        ok, rows, err = list_containers(prefix="hermes-sentinel-daemon")
        if not ok:
            return Check("hermes.sentinel_container", "warn",
                         "docker not reachable in bridge", err,
                         remedy="Check host-side: docker ps --filter name=hermes-sentinel-daemon")
        if not rows:
            return Check("hermes.sentinel_container", "fail",
                         "sentinel daemon container not found",
                         "The live guardrail is down.")
        status = rows[0]["status"]
        sev = "ok" if status == "running" else "warn"
        return Check("hermes.sentinel_container", sev,
                     f"sentinel daemon: {status}", evidence=rows[0])


    def _check_mcp_fleet(self) -> Check:
        cfg = HERMES_CFG
        if not cfg.exists():
            return Check("hermes.mcp_fleet", "warn", "no config.yaml", str(HERMES_CFG))
        lines = cfg.read_text(encoding="utf-8", errors="replace").splitlines()
        # Count the SERVER entries under mcp_servers:, not the key itself.
        # `txt.count("mcp_servers:")` always returned 1 and the `or` fallback
        # was then short-circuited, so this reported "~1 server" regardless of
        # how many were actually wired.
        start = None
        base_indent = 0
        for i, ln in enumerate(lines):
            s = ln.rstrip()
            if s.lstrip().startswith("mcp_servers:") and not s.lstrip().startswith("#"):
                start = i + 1
                base_indent = len(s) - len(s.lstrip())
                break
        names: list[str] = []
        if start is not None:
            for ln in lines[start:]:
                if not ln.strip() or ln.lstrip().startswith("#"):
                    continue
                indent = len(ln) - len(ln.lstrip())
                if indent <= base_indent:
                    break
                s = ln.strip()
                if indent == base_indent + 2 and s.endswith(":"):
                    names.append(s[:-1].strip())
        sev = "ok" if names else "warn"
        return Check("hermes.mcp_fleet", sev,
                     f"{len(names)} mcp_servers declared in config.yaml",
                     ", ".join(names[:6]) + (" ..." if len(names) > 6 else ""),
                     remedy="" if names else "Hermes writes these on first MCP start.",
                     evidence={"count": len(names), "names": names,
                               "source": str(cfg)})



    def _check_hermes_optimus(self) -> Check:
        """
        HERMES_OPTIMUS pre-dates Mavis; the doctor should still see it.

        Depth- and count-bounded by design. A full recursive stat of this tree
        costs ~16s (1984 files x ~8ms per gRPC-FUSE round trip), which blew past
        any client timeout on /doctor. A health check needs presence + shape,
        not an exact byte total, so enumeration is bounded and reports the
        truncation instead of hiding the cost.
        """
        _TREE_MAX_DEPTH = 2    # top-level shape only
        _TREE_CAP = 500       # each stat is a gRPC-FUSE round trip (~8ms)
        d = host_path(_W_HERMES_BASE, "HERMES_OPTIMUS")
        if not d.exists():
            return Check("hermes.optimus_tree", "warn", "HERMES_OPTIMUS absent",
                         str(d), remedy="Optional; created ad hoc in the past.")
        depth0 = _W_HERMES_BASE + r"\HERMES_OPTIMUS"
        try:
            subs = sorted(p.name for p in d.iterdir() if p.is_dir())
        except OSError as e:
            return Check("hermes.optimus_tree", "warn",
                         "HERMES_OPTIMUS unreadable", f"{type(e).__name__}: {e}")
        files = 0
        truncated = False
        for root, dirnames, filenames in os.walk(d, topdown=True):
            if root.rstrip("/\\").count("\\") - depth0.count("\\") >= _TREE_MAX_DEPTH:
                dirnames[:] = []
            for fn in filenames:
                if files >= _TREE_CAP:
                    truncated = True
                    break
                files += 1
            if truncated:
                break
        note = f", capped at {_TREE_CAP}" if truncated else ""
        return Check("hermes.optimus_tree", "ok",
                     f"HERMES_OPTIMUS present: {len(subs)} top-level dirs, "
                     f"{files}+ files{note}",
                     evidence={"dirs": subs, "files": files,
                               "depth": _TREE_MAX_DEPTH,
                               "truncated": truncated})


    def _register(self) -> None:
        self.check(self._check_hermes_present)
        self.check(check_docker("hermes.dockerd", "Docker engine"))
        self.check(self._check_hermes_optimus)
        for fn in (self._check_version, self._check_venv_currency, self._check_hang_probe, self._check_containers,
                   self._check_sentinel_enforcement, self._check_sentinel_source, self._check_sentinel_container,
                   self._check_mcp_fleet):
            self.check(fn)
        # The daemon's HTTP health server binds inside the container only (no published
        # port), so it is deliberately NOT probed from the host.
        # Container liveness is covered by hermes.sentinel_container instead.
        self.check(check_path_exists("hermes.home", str(HERMES_HOME), ".hermes home dir"))

    # ---------------- healers ----------------
    def h_sync(self, _p: dict) -> Check:
        """The only healer that mutates the venv. Requires explicit R0 from Popy."""
        code = (
            "import sys;sys.path.insert(0,r'%s');"
            "from hermes_cli import plugin_manager as pm;"
            "r=pm.sync_venv(set(), explicit=True, project_root=r'%s', "
            "evict_incompatible_plugins=True);"
            "print('SYNCED', r)" % (HERMES_ROOT, HERMES_ROOT)
        )
        py = PY_EXE
        rc, so, se = run([py, "-I", "-B", "-c", code], timeout=900)
        if rc == 0:
            return Check("hermes.venv_sync", "ok", "venv synced", so.strip()[:300])
        return Check("hermes.venv_sync", "fail", "sync failed",
                     (se or so)[:400])

    def h_enforce(self, _p: dict) -> Check:
        """Restore the 4 sentinel enforcement booleans in .hermes/config.yaml."""
        try:
            import yaml
        except ImportError:
            return Check("hermes.heal_enforcement", "fail",
                         "PyYAML not installed in this interpreter",
                         "Run the heal inside the container.")
        cfg = HERMES_HOME / "config.yaml"
        if not cfg.exists():
            return Check("hermes.heal_enforcement", "fail", "config.yaml missing", str(cfg))
        data = yaml.safe_load(cfg.read_text(encoding="utf-8", errors="replace")) or {}
        enf = data.get("enforcement")
        if not isinstance(enf, dict):
            enf = {}
            data["enforcement"] = enf
        changed = []
        for k, v in (("enabled", True), ("guardian_strict", True),
                     ("trigger_detection", True), ("auto_recalibrate", True)):
            if enf.get(k) is not v:
                enf[k] = v
                changed.append(k)
        if not changed:
            return Check("hermes.heal_enforcement", "ok", "enforcement already correct")
        cfg.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True),
                       encoding="utf-8")
        return Check("hermes.heal_enforcement", "ok",
                     f"healed {changed}", evidence={"changed": changed})

    def h_restart(self, p: dict) -> Check:
        """Restart ONE container. Diagnose first. NEVER prune, NEVER rm -f."""
        name = p.get("name") or ""
        if not name:
            return Check("hermes.restart", "fail", "missing 'name'",
                         'body: {"name":"<exact container name>"}')
        if not name.startswith("hermes-mcp-"):
            return Check("hermes.restart", "fail", "refusing non-Hermes container",
                         f"{name!r} is outside the hermes-mcp-* fleet")
        rc, so, se = run(["/usr/bin/docker", "restart", name], timeout=120)
        if rc == 0:
            return Check("hermes.restart", "ok", f"restarted {name}", so.strip()[:200])
        return Check("hermes.restart", "fail", f"restart {name} failed", se[:300])


if __name__ == "__main__":
    HermesBridge().serve()


