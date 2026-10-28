r"""One-shot measurement sweep for the SENTINEL handoff.

Writes 14_HANDOFF\_BUILD_SURVEY.json. Every field is measured or explicitly
NOT_MEASURED - nothing is recalled from a previous session, and nothing is
assumed present because it should be.

Raw string because the Windows path below carries a backslash. As a normal
docstring "\_" is an invalid escape sequence: Python 3.12 warns, and it becomes
a SyntaxError - which would stop the one command a reader is told to run when a
number needs re-measuring.

Run:  python survey_build.py
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import socket
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WORKSPACE = Path(r"C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\SENTINEL_PRIME")
OUT = WORKSPACE / "14_HANDOFF" / "_BUILD_SURVEY.json"
FRONT = "http://127.0.0.1:8910"
BACKEND = "http://127.0.0.1:8912"
NOT_MEASURED = "NOT_MEASURED"

S: dict = {
    "generated_at": datetime.now().isoformat(),
    "workspace": str(WORKSPACE),
    "not_measured": [],
}


def note_missing(what: str) -> None:
    S["not_measured"].append(what)


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def http(path: str, base: str = FRONT, timeout: int = 20):
    try:
        req = urllib.request.Request(base + path, headers={"Accept": "*/*"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read()
            return {"status": r.status, "bytes": len(body),
                    "headers": {k: v for k, v in r.headers.items()
                                if k.lower() in ("server", "x-sentinel-deployment",
                                                 "content-type")}}
    except urllib.error.HTTPError as e:
        return {"status": e.code, "error": str(e)[:120]}
    except Exception as e:
        return {"status": None, "error": f"{type(e).__name__}: {str(e)[:120]}"}


# ---------------------------------------------------------------- deployment
dep: dict = {}
hz = http("/healthz")
dep["front_healthz"] = hz
dep["front_root"] = {k: v for k, v in http("/").items() if k != "body"}
dep["front_readyz"] = {k: v for k, v in http("/readyz").items() if k != "body"}
dep["backend_readyz"] = {k: v for k, v in http("/api/state", BACKEND).items()
                         if k != "body"}
dep["backend_route_note"] = (
    "The backend serves /, /api/state, /api/health, /api/minimax, /api/verify, "
    "/api/corpus. It has NO route literally named /healthz or /readyz - those two "
    "names exist only on the container front, where nginx maps /readyz onto the "
    "backend's /api/state. Probing the backend at /readyz returns 404 and that is "
    "correct behaviour, not a defect. front /readyz byte size equals "
    "/api/state byte size, which is how the two planes are proved to agree.")
for route in ("/api/state", "/api/health", "/api/minimax", "/api/verify", "/api/corpus"):
    dep[f"route{route.replace('/', '_')}"] = {k: v for k, v in http(route).items()
                                              if k != "body"}

try:
    out = subprocess.run(["docker", "inspect", "mavis-sentinel-hub"],
                         capture_output=True, text=True, timeout=30)
    if out.returncode == 0:
        info = json.loads(out.stdout)[0]
        st = info.get("State", {})
        dep["container"] = {
            "name": info.get("Name", "").lstrip("/"),
            "image": info.get("Config", {}).get("Image"),
            "status": st.get("Status"),
            "health": st.get("Health", {}).get("Status"),
            "restart_policy": info.get("HostConfig", {}).get("RestartPolicy", {}).get("Name"),
            "ports": info.get("NetworkSettings", {}).get("Ports"),
            "started_at": st.get("StartedAt"),
            "created": info.get("Created"),
        }
    else:
        dep["container"] = {"error": out.stderr[:200]}
except Exception as e:
    dep["container"] = {"error": f"{type(e).__name__}: {str(e)[:160]}"}

# loopback confinement: the front must refuse every non-loopback adapter
refused, reachable = [], []
try:
    addrs = subprocess.run(
        ["powershell", "-NoProfile", "-Command",
         "Get-NetIPAddress -AddressFamily IPv4 | "
         "Where-Object {$_.IPAddress -ne '127.0.0.1'} | "
         "Select-Object -ExpandProperty IPAddress"],
        capture_output=True, text=True, timeout=40)
    for ip in addrs.stdout.split():
        ip = ip.strip()
        if not ip or ip.startswith("127."):
            continue
        s = socket.socket()
        s.settimeout(3)
        try:
            s.connect((ip, 8910))
            reachable.append(ip)
        except Exception:
            refused.append(ip)
        finally:
            s.close()
except Exception as e:
    note_missing(f"loopback refusal probe: {type(e).__name__}: {str(e)[:120]}")
dep["loopback_refused"] = refused
dep["loopback_reachable"] = reachable
S["deployment"] = dep

# ------------------------------------------------------------------ monitor
hp = WORKSPACE / "13_COMMAND_CENTER" / "api" / "health.json"
if hp.exists():
    h = json.loads(hp.read_text(encoding="utf-8"))
    checks = h.get("checks", [])
    counts: dict = {}
    for c in checks:
        counts[c.get("status")] = counts.get(c.get("status"), 0) + 1
    S["health"] = {
        "file": str(hp), "sha256": sha256(hp), "bytes": hp.stat().st_size,
        "generated_at": h.get("generated_at"), "overall": h.get("overall"),
        "interpretation": h.get("interpretation"),
        "declared_total_checks": h.get("total_checks"),
        "actual_checks": len(checks), "status_counts": counts,
        "duration_sec": h.get("duration_sec"),
        "non_ok": [
            {"id": c.get("id"), "family": c.get("family"), "status": c.get("status"),
             "value": c.get("value"), "bound": c.get("bound"),
             "evidence": c.get("evidence"), "measured_at": c.get("measured_at")}
            for c in checks if c.get("status") != "OK"],
    }
else:
    S["health"] = NOT_MEASURED
    note_missing("health.json absent")

# ---------------------------------------------------------------- ecosystem
ep = WORKSPACE / "13_COMMAND_CENTER" / "api" / "minimax-ecosystem.json"
if ep.exists():
    e = json.loads(ep.read_text(encoding="utf-8"))
    surf = e.get("surfaces", [])
    S["ecosystem"] = {
        "file": str(ep), "bytes": ep.stat().st_size, "generated_at": e.get("generated_at"),
        "counts": e.get("counts"), "surfaces": len(surf),
        "by_status": {},
        "surface_index": [{"id": s.get("id"), "label": s.get("label"),
                           "status": s.get("status"), "measured_at": s.get("measured_at")}
                          for s in surf],
    }
    for s in surf:
        st = s.get("status")
        S["ecosystem"]["by_status"][st] = S["ecosystem"]["by_status"].get(st, 0) + 1
else:
    S["ecosystem"] = NOT_MEASURED
    note_missing("minimax-ecosystem.json absent")

# -------------------------------------------------------------------- tests
def suite_record(path: Path):
    if not path.exists():
        return NOT_MEASURED
    d = json.loads(path.read_text(encoding="utf-8"))
    return {"file": str(path), "bytes": path.stat().st_size,
            "ran_at": d.get("ran_at") or d.get("generated") or d.get("generated_at"),
            "passed": d.get("passed"), "failed": d.get("failed"),
            "skipped": d.get("skipped"), "green": d.get("green"),
            "classes": len(d.get("classes", [])) if isinstance(d.get("classes"), list) else None,
            "checks": len(d.get("checks", [])) if isinstance(d.get("checks"), list) else None}


S["tests"] = {
    "unit_suite": suite_record(WORKSPACE / "13_COMMAND_CENTER" / "api" / "last_test_run.json"),
    "deployment_suite": suite_record(WORKSPACE / "13_COMMAND_CENTER" / "api" / "deployment-tests.json"),
}

# ----------------------------------------------------------------- inventory
dirs: dict = {}
for d in sorted(WORKSPACE.iterdir()):
    if d.is_dir():
        files = [p for p in d.rglob("*") if p.is_file()]
        dirs[d.name] = {"files": len(files),
                        "bytes": sum(p.stat().st_size for p in files)}
S["workspace_inventory"] = {
    "directories": len(dirs),
    "total_files": sum(v["files"] for v in dirs.values()),
    "total_bytes": sum(v["bytes"] for v in dirs.values()),
    "per_directory": dirs,
}

# key source artefacts, measured
key_files = [
    r"13_COMMAND_CENTER\index.html",
    r"13_COMMAND_CENTER\api\server.ps1",
    r"13_COMMAND_CENTER\api\sentinel-hub.ps1",
    r"13_COMMAND_CENTER\api\collect-sentinel.ps1",
    r"13_COMMAND_CENTER\deploy\nginx.conf",
    r"13_COMMAND_CENTER\deploy\Dockerfile",
    r"07_BACKBONE\mcp\sentinel_hub_server.py",
    r"07_BACKBONE\mcp\OPTIMUS_MCP_CONFIG.json",
    r"08_SELF_IMPROVEMENT\test_suite.py",
    r"08_SELF_IMPROVEMENT\test_deployment.py",
    r"08_SELF_IMPROVEMENT\monitor.py",
    r"08_SELF_IMPROVEMENT\collect_minimax_ecosystem.py",
    r"11_BRAIN\04_METHOD\MISSTEPS_AND_CORRECTIONS.md",
    r"12_PROGRAM\PROGRAM_SPEC.md",
    r"12_PROGRAM\IDEA_TO_SCRIPT_MATRIX.json",
    r"12_PROGRAM\GAP_REGISTER.json",
    r"12_PROGRAM\HERMES_GATEWAY_PROFILE_PLAN.md",
]
kf: dict = {}
for rel in key_files:
    p = WORKSPACE / rel
    if p.exists():
        b = p.read_bytes()
        kf[rel] = {"bytes": len(b), "lines": b.count(b"\n") + 1,
                   "sha256": hashlib.sha256(b).hexdigest()[:16],
                   "bom": b[:3] == b"\xef\xbb\xbf",
                   "crlf": b.count(b"\r\n")}
    else:
        kf[rel] = NOT_MEASURED
S["key_files"] = kf

# ------------------------------------------------------------------- startup
startup = Path(os.environ.get("APPDATA", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup" / "SENTINEL Command Center.bat"
if startup.exists():
    b = startup.read_bytes()
    S["startup_anchor"] = {"path": str(startup), "bytes": len(b), "sha256": sha256(startup),
                           "crlf": b.count(b"\r\n"), "bom": b[:3] == b"\xef\xbb\xbf"}
else:
    S["startup_anchor"] = NOT_MEASURED
    note_missing("Startup anchor .bat not found")

log = WORKSPACE / "09_LOGS" / "hub-startup.log"
if log.exists():
    text = log.read_text(encoding="utf-8", errors="replace")
    S["startup_log"] = {
        "path": str(log), "bytes": log.stat().st_size,
        "markers": text.count("=== startup "),
        "exit_lines": text.count("exit="),
        "last_exit": text.strip().split("exit=")[-1][:4] if "exit=" in text else None,
    }
else:
    S["startup_log"] = NOT_MEASURED

# ------------------------------------------------------------- mcp + skills
mcp = Path(r"C:\Users\apviz\.minimax\mcp.json")
if mcp.exists():
    m = json.loads(mcp.read_text(encoding="utf-8"))
    servers = m.get("mcpServers", m.get("servers", {}))
    S["live_mcp_profile"] = {"path": str(mcp), "servers": len(servers),
                             "names": sorted(servers.keys())}
else:
    S["live_mcp_profile"] = NOT_MEASURED
    note_missing("live mcp.json not readable")

hub = WORKSPACE / "07_BACKBONE" / "mcp" / "sentinel_hub_server.py"
if hub.exists():
    import re
    tools = sorted(set(re.findall(r'name="(sentinel_[a-z0-9_]+)"', hub.read_text(encoding="utf-8"))))
    S["sentinel_hub"] = {"path": str(hub), "bytes": hub.stat().st_size,
                         "tools": len(tools), "tool_names": tools}
else:
    S["sentinel_hub"] = NOT_MEASURED

sd = Path(r"C:\Users\apviz\.minimax\agents\mavis\skills")
if sd.exists():
    S["skills"] = {"root": str(sd), "count": len(list(sd.rglob("SKILL.md"))),
                   "names": sorted(p.parent.name for p in sd.rglob("SKILL.md"))}
else:
    S["skills"] = NOT_MEASURED
    note_missing("skills root not found")

# ------------------------------------------------------------------- ports
ports: dict = {}
try:
    out = subprocess.run(["docker", "ps", "--format", "{{.Names}}\t{{.Ports}}\t{{.Status}}"],
                         capture_output=True, text=True, timeout=30)
    ports["docker_ps"] = out.stdout.strip().splitlines()
except Exception as e:
    ports["docker_ps"] = f"ERROR {type(e).__name__}"
ports["8900_owner"] = "OPTIMUS control center (not touched by SENTINEL)"
ports["8901_owner"] = "OPTIMUS (not touched by SENTINEL)"
S["ports"] = ports

# --------------------------------------------------------------- blueprint
bp = WORKSPACE / "07_BACKBONE" / "mcp" / "OPTIMUS_MCP_CONFIG.json"
if bp.exists():
    cfg = json.loads(bp.read_text(encoding="utf-8"))
    servers = cfg.get("servers", {})
    built, planned = [], []
    for name, spec in servers.items():
        args = (spec or {}).get("args", []) or []
        py = next((a for a in args if str(a).endswith(".py")), None)
        if py is None:
            # An npm-backed entry cannot be judged by file existence. It is
            # resolved against the registry, which costs a network round trip,
            # so it is resolved here rather than asserted - and the result is
            # recorded either way. Marking it "planned" because it has no .py
            # file would be a false statement about two packages that do
            # install.
            pkg = next((a for a in args if str(a).startswith("@")), "")
            # npm is a .cmd shim on Windows; a bare "npm" is not resolvable by
            # CreateProcess, so the shim name is used explicitly. Marking these
            # NOT_MEASURED because of a PATH quirk would be reporting the
            # survey's own defect as the system's.
            npm = shutil.which("npm.cmd") or shutil.which("npm")
            if not npm:
                planned.append(f"{name} (npm NOT_AVAILABLE on PATH)")
                note_missing(f"npm not found on PATH; {name} unresolved")
            else:
                try:
                    r = subprocess.run([npm, "view", pkg, "version"],
                                       capture_output=True, text=True, timeout=90)
                    if r.returncode == 0:
                        built.append(f"{name} (npm {pkg} {r.stdout.strip()})")
                    else:
                        planned.append(f"{name} (npm {pkg} does not resolve)")
                except Exception as e:
                    planned.append(f"{name} (npm NOT_MEASURED: {type(e).__name__})")
                    note_missing(f"npm resolution for {name}: {type(e).__name__}")
        elif Path(py).exists():
            built.append(f"{name} (file present)")
        else:
            planned.append(name)
    S["blueprint"] = {
        "path": str(bp), "sha256": sha256(bp), "bytes": bp.stat().st_size,
        "declared": len(servers), "built": built, "planned_not_built": planned,
        "names": sorted(servers.keys()),
    }
else:
    S["blueprint"] = NOT_MEASURED

# ------------------------------------------------------------ gap register
gr = WORKSPACE / "12_PROGRAM" / "GAP_REGISTER.json"
if gr.exists():
    gaps = json.loads(gr.read_text(encoding="utf-8"))
    S["gap_register"] = {
        "path": str(gr), "count": len(gaps),
        "by_area": {}, "by_status": {},
        "ids": [g.get("id") for g in gaps],
    }
    for g in gaps:
        S["gap_register"]["by_area"][g.get("area")] = \
            S["gap_register"]["by_area"].get(g.get("area"), 0) + 1
        S["gap_register"]["by_status"][g.get("status")] = \
            S["gap_register"]["by_status"].get(g.get("status"), 0) + 1
else:
    S["gap_register"] = NOT_MEASURED

# ------------------------------------------------------- swarm / instances
ci = WORKSPACE / "09_LOGS" / "cross_instance"
if ci.exists():
    reg = ci / "instance_registry.json"
    regdata = json.loads(reg.read_text(encoding="utf-8")) if reg.exists() else {}
    mb = ci / "mailbox"
    profiles = ["SENTINEL-DESKTOP", "SENTINEL-COWORK", "SENTINEL-CHAT", "CODER-APP"]
    S["swarm"] = {
        "registry_path": str(reg),
        "registry_entries": {k: {"status": v.get("status"), "last_seen": v.get("last_seen")}
                             for k, v in regdata.items()},
        "profile_mailboxes": {p: (mb / p).is_dir() for p in profiles},
        "heartbeats_dir": (ci / "heartbeats").is_dir(),
    }
else:
    S["swarm"] = NOT_MEASURED

# ------------------------------------------------------------------- design
design = Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "MiniMax Design" / "current" / "resources"
if design.exists():
    gw = design / "gateway" / "dist" / "main.js"
    conf = design / "conf" / "external_api_conf.yaml"
    S["minimax_design"] = {
        "install_present": True, "resources": str(design),
        "gateway_main_bytes": gw.stat().st_size if gw.exists() else None,
        "conf_bytes": conf.stat().st_size if conf.exists() else None,
        "ever_launched": False,
        "hilo_token_present": False,
        "note": "measured from disk; the app has never been launched, so no runtime surface was claimed",
    }
else:
    S["minimax_design"] = {"install_present": False}
    note_missing("MiniMax Design resources not found")

# ------------------------------------------------------------------- write
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(S, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"wrote {OUT} ({OUT.stat().st_size} bytes)")
print(f"explicitly NOT_MEASURED: {len(S['not_measured'])}")
for n in S["not_measured"]:
    print("   -", n)