"""
minimax_bridge_core.py â€” shared library for OPTIMUS MiniMaxâ†”ecosystem bridges.

Role: doctor + delegate + centralize. Every bridge exposes the same HTTP surface
so Mavis (or any agent) can interrogate, dispatch to, and audit its target
ecosystem through one uniform contract.

Endpoints (all GET unless noted):
  /health          â€” liveness + self-report
  /schema          â€” full tool catalogue as JSON (this container's capabilities)
  /doctor          â€” diagnose the target ecosystem (structured report)
  /doctor/detailed â€” same, verbose
  /audit           â€” read the target's memory/state/logs, return findings
  POST /delegate   â€” dispatch a task to the target's agent CLI
  POST /heal       â€” apply a known-good fix (requires explicit action field)
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Callable

BRIDGE_VERSION = "1.0.0"
STARTED_AT = time.time()

# Every stat() on a Windows bind mount inside the container is a gRPC-FUSE round
# trip. Directory audits are bounded so a large tree degrades gracefully instead
# of holding the HTTP request open past any client timeout.
_AUDIT_CAP = 5000


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def in_container() -> bool:
    """True when running inside the Linux bridge container (not bare Windows)."""
    import platform
    return platform.system().lower() != "windows"


def host_path(*windows_parts: str) -> Path:
    """
    Resolve a host path from inside the bridge container.

    The compose file bind-mounts each host path as a SIBLING mount point
    (Docker rejects nested mounts under a read-only parent), so translate the
    longest matching prefix to its mount point:

        C:\\...\\AppData\\Local\\hermes\\mcp-servers -> /mcp-servers
        C:\\...\\AppData\\Local\\hermes                -> /hermes
        C:\\Users\\apviz\\.hermes                       -> /hermes-home
        C:\\...\\AppData\\Local\\agy                    -> /agy-local
        C:\\...\\Roaming\\Antigravity                   -> /ag-roaming
        C:\\...\\Programs\\Antigravity IDE              -> /agy-ide
        C:\\...\\Programs\\antigravity                  -> /agy-app
        C:\\...\\Docker\\resources\\bin                 -> /hostbin
    """
    if not in_container():
        return Path(*windows_parts)
    p = Path(*windows_parts)
    win = str(p).replace("/", "\\")
    mounts = (
        (r"C:\Users\apviz\AppData\Local\hermes\mcp-servers", "/mcp-servers"),
        (r"C:\Users\apviz\AppData\Local\hermes", "/hermes"),
        (r"C:\Users\apviz\.hermes", "/hermes-home"),
        (r"C:\Users\apviz\AppData\Roaming\Antigravity", "/ag-roaming"),
        (r"C:\Users\apviz\AppData\Local\agy", "/agy-local"),
        (r"C:\Users\apviz\AppData\Local\Programs\Antigravity IDE", "/agy-ide"),
        (r"C:\Users\apviz\AppData\Local\Programs\antigravity", "/agy-app"),
        (r"C:\Program Files\Docker\Docker\resources\bin", "/hostbin"),
    )
    for prefix, mount in mounts:
        if win.lower().startswith(prefix.lower()):
            tail = win[len(prefix):].lstrip("\\/").replace("\\", "/")
            return Path(mount) / tail if tail else Path(mount)
    rest = p.as_posix()
    drive = p.drive.rstrip(":")
    if drive:
        rest = rest[len(drive) + 1:]
    return Path("/host") / rest


def find_first(*candidates: str) -> Path | None:
    """Return the first candidate path that exists, honouring the container mapping."""
    for c in candidates:
        p = host_path(c) if in_container() else Path(c)
        if p.exists():
            return p
    return None


def find_binary(*candidates: str) -> str | None:
    """
    Find an executable from a list of candidate paths, trying the host path first
    when inside a container. Returns a path usable by subprocess in this env.
    """
    for c in candidates:
        direct = Path(c)
        if direct.exists():
            return str(direct)
        if in_container():
            host = host_path(c)
            if host.exists():
                return str(host)
    return None


def run(cmd: list[str], timeout: int = 60) -> tuple[int, str, str]:
    """Run a command, never raise. Returns (rc, stdout, stderr)."""
    try:
        p = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout, errors="replace"
        )
        return p.returncode, p.stdout, p.stderr
    except FileNotFoundError:
        return 127, "", f"not found: {cmd[0]}"
    except subprocess.TimeoutExpired:
        return 124, "", f"timeout after {timeout}s: {cmd[0]}"
    except Exception as e:  # noqa: BLE001
        return 1, "", f"{type(e).__name__}: {e}"


@dataclass
class Check:
    """One diagnostic finding."""
    id: str
    severity: str          # ok | warn | fail
    title: str
    detail: str = ""
    remedy: str = ""
    evidence: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DoctorReport:
    bridge: str
    target: str
    ts: str
    checks: list[Check] = field(default_factory=list)
    meta: dict[str, Any] = field(default_factory=dict)

    @property
    def worst(self) -> str:
        order = {"ok": 0, "warn": 1, "fail": 2}
        return max((c.severity for c in self.checks), key=lambda s: order.get(s, 0), default="ok")

    def to_dict(self) -> dict[str, Any]:
        return {
            "bridge": self.bridge,
            "target": self.target,
            "ts": self.ts,
            "health": self.worst,
            "ok_count": sum(1 for c in self.checks if c.severity == "ok"),
            "warn_count": sum(1 for c in self.checks if c.severity == "warn"),
            "fail_count": sum(1 for c in self.checks if c.severity == "fail"),
            "checks": [c.to_dict() for c in self.checks],
            "meta": self.meta,
        }


class BridgeCore:
    """
    Base class for an OPTIMUS ecosystem bridge.

    Subclasses declare TARGET, PORT, and register checks/healers.
    """

    BRIDGE_NAME: str = "minimax-bridge"
    TARGET: str = "unknown"
    TARGET_CLI: str = ""
    PORT: int = 8800

    def __init__(self) -> None:
        self.checks: list[Callable[[], Check]] = []
        self.healers: dict[str, Callable[[dict], Check]] = {}
        self.audit_sources: dict[str, str] = {}
        self.delegate_spec: dict[str, Any] = {}
        self.journal_path = Path("/opt/optimus/journal")
        try:
            self.journal_path.mkdir(parents=True, exist_ok=True)
        except OSError:
            self.journal_path = Path("/tmp/optimus-journal")
            self.journal_path.mkdir(parents=True, exist_ok=True)

    # ---------- journal ----------
    def journal_write(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Append one JSONL record to the bridge journal."""
        rec = {
            "ts": now_iso(),
            "bridge": self.BRIDGE_NAME,
            "target": self.TARGET,
            **payload,
        }
        f = self.journal_path / f"{self.BRIDGE_NAME}.jsonl"
        with f.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, default=str) + "\n")
        return {"ok": True, "path": str(f), "record": rec}

    def journal_read(self, limit: int = 50) -> dict[str, Any]:
        """Return the most recent journal records, newest last."""
        f = self.journal_path / f"{self.BRIDGE_NAME}.jsonl"
        if not f.exists():
            return {"bridge": self.BRIDGE_NAME, "path": str(f),
                    "exists": False, "records": []}
        lines = [l for l in f.read_text(encoding="utf-8", errors="replace").splitlines()
                 if l.strip()]
        recs = []
        for l in lines[-limit:]:
            try:
                recs.append(json.loads(l))
            except json.JSONDecodeError:
                recs.append({"raw": l})
        return {"bridge": self.BRIDGE_NAME, "path": str(f), "exists": True,
                "total": len(lines), "records": recs}

    # ---------- registration ----------
    def check(self, fn: Callable[[], Check]) -> None:
        self.checks.append(fn)

    def heal(self, action: str) -> Callable[[dict], Check]:
        def deco(fn: Callable[[dict], Check]) -> Callable[[dict], Check]:
            self.healers[action] = fn
            return fn
        return deco

    def audit(self, name: str, path: str) -> None:
        self.audit_sources[name] = path

    def delegates(self, spec: dict[str, Any]) -> None:
        self.delegate_spec = spec

    # ---------- endpoints ----------
    def health(self) -> dict[str, Any]:
        return {
            "ok": True,
            "service": self.BRIDGE_NAME,
            "target": self.TARGET,
            "version": BRIDGE_VERSION,
            "uptime_s": round(time.time() - STARTED_AT, 1),
            "role": "MiniMax Code <-> " + self.TARGET,
        }

    def schema(self) -> dict[str, Any]:
        return {
            "bridge": self.BRIDGE_NAME,
            "version": BRIDGE_VERSION,
            "target": self.TARGET,
            "http": {
                "GET /health": "liveness",
                "GET /schema": "this capability catalogue",
                "GET /doctor": "diagnose target ecosystem",
                "GET /doctor/detailed": "verbose diagnosis",
                "GET /audit": "read target memory/state/logs",
                "GET /journal": "read this bridge's journal",
                "POST /journal": "append a journal record",
                "POST /delegate": "dispatch task to target agent CLI",
                "POST /heal": "apply named remedy (requires action in body)",
            },
            "journal": str(self.journal_path / f"{self.BRIDGE_NAME}.jsonl"),
            "checks": [c.__name__ for c in self.checks],
            "healers": list(self.healers),
            "audit_sources": self.audit_sources,
            "delegate": self.delegate_spec,
        }

    def doctor(self, detailed: bool = False) -> DoctorReport:
        rep = DoctorReport(self.BRIDGE_NAME, self.TARGET, now_iso())
        for fn in self.checks:
            try:
                rep.checks.append(fn())
            except Exception as e:  # noqa: BLE001
                rep.checks.append(Check("check.crash", "fail", "Check raised",
                                        f"{type(e).__name__}: {e}"))
        if not detailed:
            rep.checks = [c for c in rep.checks if c.severity != "ok"]
        rep.meta = {
            "target_cli": self.TARGET_CLI,
            "target_cli_present": bool(shutil.which(self.TARGET_CLI)) if self.TARGET_CLI else False,
            "bridge_version": BRIDGE_VERSION,
        }
        return rep

    def audit(self, mapping: dict[str, str] | None = None) -> dict[str, Any]:
        if mapping:
            self.audit_sources.update(mapping)
        out: dict[str, Any] = {"bridge": self.BRIDGE_NAME, "ts": now_iso(), "sources": {}}
        for name, path in self.audit_sources.items():
            p = Path(path)
            entry: dict[str, Any] = {"path": path, "exists": p.exists()}
            if p.exists():
                try:
                    if p.is_dir():
                        # Bounded single walk. Materialising the full rglob list and
                        # then stat-ing every entry made /audit unusable on bind-
                        # mounted Windows trees (thousands of gRPC-FUSE round trips).
                        count = 0
                        total_bytes = 0
                        sample: list[str] = []
                        truncated = False
                        for root, _dirs, filenames in os.walk(p, topdown=True):
                            for fn in filenames:
                                if count >= _AUDIT_CAP:
                                    truncated = True
                                    break
                                count += 1
                                if len(sample) < 15:
                                    sample.append(os.path.join(root, fn))
                                try:
                                    total_bytes += os.stat(
                                        os.path.join(root, fn)).st_size
                                except OSError:
                                    pass
                            if truncated:
                                break
                        entry["file_count"] = count
                        entry["sample"] = sample
                        entry["total_bytes"] = total_bytes
                        if truncated:
                            entry["truncated"] = True
                    else:
                        entry["size"] = p.stat().st_size
                        entry["mtime"] = datetime.fromtimestamp(
                            p.stat().st_mtime, timezone.utc
                        ).isoformat()
                        entry["head"] = p.read_text(
                            encoding="utf-8", errors="replace"
                        )[:4000]
                except Exception as e:  # noqa: BLE001
                    entry["error"] = f"{type(e).__name__}: {e}"
            out["sources"][name] = entry
        return out

    def delegate(self, payload: dict[str, Any]) -> dict[str, Any]:
        """
        Produce a ready-to-run command for the target CLI.

        The bridge runs in a Linux container and cannot exec hermes.exe /
        agy.exe (Windows PE binaries). So /delegate is a COMMAND SPEC EMITTER:
        it validates the request and returns the exact command Mavis should run
        on the Windows host. If this bridge happens to run on Windows (dev
        mode), it executes directly.
        """
        prompt = payload.get("prompt") or payload.get("task")
        if not prompt:
            return {"ok": False, "error": "missing 'prompt' or 'task' in body"}
        if not self.TARGET_CLI:
            return {"ok": False, "error": "bridge declares no target CLI"}

        argv = self.delegate_spec.get("argv", ["{cli}", "-p", "{prompt}"])
        cmd = [
            a.replace("{cli}", self.TARGET_CLI)
             .replace("{prompt}", str(prompt))
             .replace("{project}", str(payload.get("project", "")))
             .replace("{model}", str(payload.get("model", "")))
            for a in argv
        ]
        cmd = [c for c in cmd if c != ""]
        timeout = int(payload.get("timeout", payload.get("timeout_s", 300)))

        if not in_container():
            rc, so, se = run(cmd, timeout=timeout)
            return {
                "ok": rc == 0, "mode": "executed",
                "bridge": self.BRIDGE_NAME, "target": self.TARGET,
                "command": cmd, "returncode": rc,
                "stdout": so[:20000], "stderr": se[:8000], "ts": now_iso(),
            }

        return {
            "ok": True,
            "mode": "spec",
            "bridge": self.BRIDGE_NAME,
            "target": self.TARGET,
            "command": cmd,
            "powershell": " & '" + "', '".join(cmd) + "'",
            "timeout_s": timeout,
            "note": (
                "Run this on the Windows host. The bridge container cannot exec "
                "Windows binaries. Mavis executes it via the bash tool."
            ),
            "ts": now_iso(),
        }

    def apply_heal(self, payload: dict[str, Any]) -> dict[str, Any]:
        action = payload.get("action")
        if not action:
            return {"ok": False, "error": "missing 'action' in body",
                    "available": list(self.healers)}
        fn = self.healers.get(action)
        if fn is None:
            return {"ok": False, "error": f"unknown action {action!r}",
                    "available": list(self.healers)}
        try:
            chk = fn(payload)
            return {"ok": chk.severity != "fail", "action": action, "result": chk.to_dict()}
        except Exception as e:  # noqa: BLE001
            return {"ok": False, "action": action, "error": f"{type(e).__name__}: {e}"}

    # ---------- server ----------
    def serve(self) -> None:
        core = self

        class Handler(BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.1"

            def _send(self, obj: dict[str, Any], code: int = 200) -> None:
                body = json.dumps(obj, indent=2, default=str).encode()
                self.send_response(code)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def do_GET(self) -> None:  # noqa: N802
                path = self.path.split("?")[0].rstrip("/") or "/"
                try:
                    if path in ("/", "/health"):
                        self._send(core.health())
                    elif path == "/schema":
                        self._send(core.schema())
                    elif path == "/doctor":
                        self._send(core.doctor(False).to_dict())
                    elif path == "/doctor/detailed":
                        self._send(core.doctor(True).to_dict())
                    elif path == "/audit":
                        self._send(core.audit())
                    elif path == "/journal":
                        q = self.path.split("?")[1] if "?" in self.path else ""
                        lim = 50
                        for kv in q.split("&"):
                            if kv.startswith("limit="):
                                lim = int(kv.split("=", 1)[1] or 50)
                        self._send(core.journal_read(lim))
                    else:
                        self._send({"ok": False, "error": f"no route {path}"}, 404)
                except Exception as e:  # noqa: BLE001
                    self._send({"ok": False, "error": f"{type(e).__name__}: {e}"}, 500)

            def do_POST(self) -> None:  # noqa: N802
                path = self.path.split("?")[0].rstrip("/") or "/"
                n = int(self.headers.get("Content-Length") or 0)
                raw = self.rfile.read(n) if n else b"{}"
                try:
                    payload = json.loads(raw or b"{}")
                except Exception:
                    payload = {}
                try:
                    if path == "/delegate":
                        self._send(core.delegate(payload))
                    elif path == "/journal":
                        self._send(core.journal_write(payload))
                    elif path == "/heal":
                        self._send(core.apply_heal(payload))
                    else:
                        self._send({"ok": False, "error": f"no route {path}"}, 404)
                except Exception as e:  # noqa: BLE001
                    self._send({"ok": False, "error": f"{type(e).__name__}: {e}"}, 500)

            def log_message(self, *_a: Any) -> None:
                return  # quiet

        srv = ThreadingHTTPServer(("0.0.0.0", core.PORT), Handler)
        srv.serve_forever()


# ---------- reusable checks ----------
def check_binary(name: str, remedy: str = "") -> Check:
    def _c() -> Check:
        p = shutil.which(name)
        if p:
            return Check(f"bin.{name}", "ok", f"{name} on PATH", p)
        return Check(f"bin.{name}", "fail", f"{name} NOT on PATH", remedy=remedy)
    return _c


def check_path_exists(cid: str, path: str, title: str = "") -> Check:
    def _c() -> Check:
        p = Path(path)
        if p.exists():
            return Check(cid, "ok", title or f"{p} exists", str(p),
                         evidence={"is_dir": p.is_dir()})
        return Check(cid, "fail", title or f"{p} missing", f"expected at {path}")
    return _c


def check_health_endpoint(url: str, cid: str = "svc.health", title: str = "") -> Check:
    def _c() -> Check:
        import re as _re
        import urllib.error
        import urllib.request
        try:
            with urllib.request.urlopen(url, timeout=5) as r:
                ctype = (r.headers.get("Content-Type") or "").split(";")[0].strip()
                raw = r.read(2000)
                body = raw.decode("utf-8", "replace")
                try:
                    parsed = json.loads(body)
                except Exception:
                    parsed = None
                if parsed is not None:
                    return Check(cid, "ok", title or f"{url} reachable", body[:300],
                                 evidence=parsed if isinstance(parsed, dict) else {})
                # Non-JSON body. This is usually a web UI or an SPA catch-all,
                # not an API -- reporting the markup as the detail dumps a wall
                # of <script>/<style> into the dashboard and means nothing.
                # Summarise instead. Note the SPA trap: a 200 here does not
                # prove any particular API route exists.
                m = _re.search(r"<title[^>]*>(.*?)</title>", body, _re.I | _re.S)
                summary = f"{ctype or 'non-JSON'} response, {len(raw)} B"
                if m:
                    summary += f', title "{m.group(1).strip()[:60]}"'
                return Check(cid, "ok", title or f"{url} reachable", summary,
                             evidence={"content_type": ctype, "bytes": len(raw),
                                       "is_json": False,
                                       "note": "web UI / SPA response, not a JSON API"})
        except urllib.error.HTTPError as e:
            return Check(cid, "warn", title or f"{url} HTTP {e.code}", str(e))
        except Exception as e:  # noqa: BLE001
            return Check(cid, "fail", title or f"{url} unreachable", f"{type(e).__name__}: {e}")
    return _c


def check_cmd(cid: str, cmd: list[str], title: str, severity_if_nonzero: str = "warn",
              timeout: int = 60) -> Check:
    def _c() -> Check:
        rc, so, se = run(cmd, timeout=timeout)
        if rc == 0:
            return Check(cid, "ok", title, so.strip()[:400])
        return Check(cid, severity_if_nonzero, f"{title} -> rc={rc}",
                     (se or so).strip()[:400], evidence={"rc": rc})
    return _c


# ---------------------------------------------------------------------------
# Docker access from inside the bridge container (via the mounted socket)
# ---------------------------------------------------------------------------
DOCKER_SOCK = "/var/run/docker.sock"


def docker_client():
    """Return a docker SDK client, or None when the socket is unavailable."""
    if not in_container():
        return None
    try:
        import docker  # type: ignore
    except ImportError:
        return None
    try:
        return docker.DockerClient(base_url="unix://" + DOCKER_SOCK)
    except Exception:  # noqa: BLE001
        return None


def check_docker(cid: str = "docker.engine", title: str = "Docker engine") -> Check:
    def _c() -> Check:
        cli = docker_client()
        if cli is None:
            # Windows host: cannot reach the engine from a Linux container without
            # the SDK. Report as informational, not a failure.
            return Check(cid, "warn", "Docker not reachable from bridge container",
                         "Install the docker SDK in the image and mount "
                         "/var/run/docker.sock, or run this check host-side.",
                         evidence={"in_container": in_container()})
        try:
            v = cli.version()
            return Check(cid, "ok", title, v.get("Version", "?"),
                         evidence={"server": v.get("Version")})
        except Exception as e:  # noqa: BLE001
            return Check(cid, "fail", "Docker engine error", f"{type(e).__name__}: {e}")
    return _c


def list_containers(prefix: str = "", all_containers: bool = True) -> tuple[bool, list[dict], str]:
    """Return (ok, [{name,status,image,ports}], error)."""
    cli = docker_client()
    if cli is None:
        return False, [], "no docker client"
    try:
        conts = cli.containers.list(all=all_containers)
    except Exception as e:  # noqa: BLE001
        return False, [], f"{type(e).__name__}: {e}"
    out = []
    for c in conts:
        if prefix and not c.name.startswith(prefix):
            continue
        out.append({
            "name": c.name,
            "status": c.status,
            "image": (c.image.tags or ["?"])[0] if c.image.tags else "?",
            "ports": {k: v for k, v in (c.ports or {}).items()},
        })
    return True, out, ""


def restart_container(name: str) -> tuple[bool, str]:
    cli = docker_client()
    if cli is None:
        return False, "no docker client"
    try:
        c = cli.containers.get(name)
        c.restart(timeout=60)
        return True, f"restarted {name}"
    except Exception as e:  # noqa: BLE001
        return False, f"{type(e).__name__}: {e}"

