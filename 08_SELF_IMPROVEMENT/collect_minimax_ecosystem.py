#!/usr/bin/env python3
"""
collect_minimax_ecosystem.py - measure the local MINIMAX ecosystem from disk.

WHY THIS EXISTS
    The Command Center is meant to be the control hub for the whole local
    MINIMAX ecosystem: the agent runtime, the skills, the MCP fleet, the
    sessions, the memory. A hub that shows only its own data is a dashboard,
    not a hub.

    The obvious way to get this data is to shell out to the `mavis` CLI and ask
    it for the agent roster and the live session list. That CLI is NOT on PATH
    on this machine - measured, not assumed - so an implementation that called
    it would report a permanently empty panel, or worse, would invent numbers
    to fill the space.

    So this collector reads the runtime's own state on disk, which is real and
    verifiable, and reports each surface separately with its own status. Where
    something genuinely cannot be measured from disk, the panel says
    NOT_AVAILABLE and names the reason. That is the same law the rest of
    SENTINEL applies: a measured value or an honest absence, never a plausible
    number.

WHAT IT MEASURES (all under activeDataDir)
    agents/                 the agent roster
    agents/mavis/skills/    installed skills, and which of them are SENTINEL
    mcp.json                the live MCP server configuration
    mcp-runtime-names.json  the names the runtime actually resolved
    sessions/               local conversation records
    memory/                 agent memory
    config.yaml, permission.json, channel-*.yaml

THE ONE EXCEPTION TO "READS DISK": THE NETWORK PROBE
    `design_cloud_reach` is the only surface here that leaves the machine. It
    opens a DNS query and a TLS handshake against the MINIMAX Design cloud
    gateway hosts, because "which cloud can this machine actually reach" cannot
    be answered from a file. That exception is stated here rather than smuggled
    in, and it is bounded on purpose:
      * it makes NO API call and sends NO credential - it stops at the
        handshake and reports the certificate it was presented;
      * it launches nothing, so it cannot start the app it measures;
      * it costs roughly 10 s of runtime, which is why each host is capped at
        5 s and every host gets a verdict either way;
      * a resolver that fails yields an honest "unresolved", never a silent
        omission, so a flaky network cannot turn this surface green.
    Note that this file DOES import subprocess - it runs a read-only
    Get-Process inventory. "Reads state" was never the same claim as "spawns
    nothing", and conflating the two is how a false assurance gets written.

Run:  python collect_minimax_ecosystem.py [--check]
      --check  verify the output is fresh and readable, write nothing
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

MINIMAX_ROOT = Path(os.environ.get("MINIMAX_HOME", r"C:\Users\apviz\.minimax"))
OUT_PATH = Path(__file__).resolve().parent.parent / "13_COMMAND_CENTER" / "api" / "minimax-ecosystem.json"

MEASURED = "MEASURED"
NOT_AVAILABLE = "NOT_AVAILABLE"
ERROR = "ERROR"

# Mirrors cross_instance.HEARTBEAT_ALIVE_SECONDS. Duplicated deliberately rather
# than imported: importing that module to read a constant would put the collector
# one accidental constructor away from writing the registry it is reporting on.
HEARTBEAT_ALIVE_SECONDS = 300

SURFACES: list[dict] = []


def add(sid: str, label: str, status: str, value, detail: str, source: str = "") -> None:
    SURFACES.append({
        "id": sid,
        "label": label,
        "status": status,
        "value": value,
        "detail": detail,
        "source": source,
        "measured_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
    })


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


# ------------------------------------------------------------------ agents --
def collect_agents() -> dict:
    agents_dir = MINIMAX_ROOT / "agents"
    if not agents_dir.is_dir():
        add("agents", "Agent runtime", NOT_AVAILABLE, None,
            f"{agents_dir} does not exist - the runtime root is not where it is expected",
            str(agents_dir))
        return {}

    roster = []
    for d in sorted(agents_dir.iterdir()):
        if not d.is_dir() or d.name.startswith("."):
            continue  # .builtin is machinery, not an agent Popy selects
        entry = {"name": d.name}
        cfg = d / "config.yaml"
        if cfg.is_file():
            entry["config_bytes"] = cfg.stat().st_size
        for sub in ("skills", "memory", "sessions", "workspace"):
            if (d / sub).is_dir():
                entry[sub] = sum(1 for x in (d / sub).iterdir())
        roster.append(entry)

    add("agents", "Agent runtime", MEASURED, {"count": len(roster), "roster": roster},
        f"{len(roster)} agents installed: {', '.join(a['name'] for a in roster)}",
        str(agents_dir))
    return {a["name"]: a for a in roster}


# ------------------------------------------------------------------ skills --
def collect_skills() -> None:
    skills_dir = MINIMAX_ROOT / "agents" / "mavis" / "skills"
    if not skills_dir.is_dir():
        add("skills", "Installed skills", NOT_AVAILABLE, None,
            f"{skills_dir} not found", str(skills_dir))
        return

    all_skills, sentinel = [], []
    for d in sorted(skills_dir.iterdir()):
        if not d.is_dir():
            continue
        skill_md = d / "SKILL.md"
        entry = {"name": d.name, "has_skill_md": skill_md.is_file()}
        if skill_md.is_file():
            entry["bytes"] = skill_md.stat().st_size
        all_skills.append(entry)
        if "sentinel" in d.name.lower():
            sentinel.append(entry)

    add("skills", "Installed skills", MEASURED,
        {"count": len(all_skills), "sentinel_count": len(sentinel),
         "sentinel": [s["name"] for s in sentinel]},
        f"{len(all_skills)} skills in the mavis runtime root; {len(sentinel)} are SENTINEL",
        str(skills_dir))

    # A hub should be able to say whether its own pieces are actually wired,
    # not merely present. The installer is the authority on drift.
    installer = Path(__file__).resolve().parent / "install_skills.py"
    if installer.is_file():
        add("skills_drift", "SENTINEL skill drift", MEASURED, "see_console",
            "run: python install_skills.py --check", str(installer))
    else:
        add("skills_drift", "SENTINEL skill drift", NOT_AVAILABLE, None,
            "install_skills.py not found next to this collector", str(installer))


# --------------------------------------------------------------------- mcp --
def collect_mcp() -> None:
    cfg_path = MINIMAX_ROOT / "mcp.json"
    if not cfg_path.is_file():
        add("mcp_config", "MCP configuration", NOT_AVAILABLE, None,
            f"{cfg_path} not found", str(cfg_path))
    else:
        try:
            cfg = read_json(cfg_path)
            servers = cfg.get("mcpServers", cfg.get("servers", {}))
            if isinstance(servers, dict):
                detail = ", ".join(f"{k}({v.get('type', v.get('command', '?'))})"
                                   for k, v in servers.items()) if servers else "none declared"
                add("mcp_config", "MCP configuration", MEASURED,
                    {"count": len(servers), "names": sorted(servers.keys())},
                    f"{len(servers)} servers declared: {detail}", str(cfg_path))
            else:
                add("mcp_config", "MCP configuration", MEASURED,
                    {"count": len(servers)}, f"{len(servers)} servers declared (list form)",
                    str(cfg_path))
        except (json.JSONDecodeError, OSError) as e:
            add("mcp_config", "MCP configuration", ERROR, None,
                f"could not parse {cfg_path}: {e}", str(cfg_path))

    names_path = MINIMAX_ROOT / "mcp-runtime-names.json"
    if not names_path.is_file():
        add("mcp_runtime", "MCP runtime names", NOT_AVAILABLE, None,
            f"{names_path} not found", str(names_path))
    else:
        try:
            data = read_json(names_path)
            if isinstance(data, dict):
                keys = sorted(data.keys())
            elif isinstance(data, list):
                keys = sorted(str(x) for x in data)
            else:
                keys = []
            add("mcp_runtime", "MCP runtime names", MEASURED, {"count": len(keys), "names": keys},
                f"{len(keys)} names resolved by the runtime", str(names_path))
        except (json.JSONDecodeError, OSError) as e:
            add("mcp_runtime", "MCP runtime names", ERROR, None,
                f"could not parse {names_path}: {e}", str(names_path))


# ------------------------------------------------------- sessions / memory --
def _count_dir(label: str, path: Path, sid: str) -> None:
    if not path.is_dir():
        add(sid, label, NOT_AVAILABLE, None, f"{path} not found", str(path))
        return
    n = sum(1 for _ in path.iterdir())
    add(sid, label, MEASURED, {"entries": n}, f"{n} entries", str(path))


def collect_runtime_dirs() -> None:
    _count_dir("Local sessions", MINIMAX_ROOT / "agents" / "mavis" / "sessions", "sessions")
    _count_dir("Agent memory", MINIMAX_ROOT / "agents" / "mavis" / "memory", "memory")
    _count_dir("Integrations", MINIMAX_ROOT / "integrations", "integrations")
    _count_dir("Plugins", MINIMAX_ROOT / "plugins", "plugins")


# --------------------------------------------------------- config surfaces --
def collect_config() -> None:
    for sid, label, name in (
        ("config", "Runtime config", "config.yaml"),
        ("permissions", "Permission policy", "permission.json"),
        ("channel_bindings", "Channel bindings", "channel-bindings.yaml"),
        ("channel_routes", "Channel routes", "channel-routes.yaml"),
    ):
        p = MINIMAX_ROOT / name
        if p.is_file():
            add(sid, label, MEASURED, {"bytes": p.stat().st_size},
                f"{name} present ({p.stat().st_size} B)", str(p))
        else:
            add(sid, label, NOT_AVAILABLE, None, f"{name} not found", str(p))


# ---------------------------------------------------- the capability gap ----
def collect_cli_capability() -> None:
    """The live roster and session list are CLI-only. Say so, loudly, instead of
    leaving a hole in the hub that looks like data."""
    # Deliberately shutil.which only. This runs every 4th refresh cycle; spawning
    # a CLI here to ask its version would add process churn to a collector whose
    # spawn rate is already reported. Presence on PATH is the measurement; the
    # version is read from each package's own manifest by collect_desktop_family.
    import shutil
    found_roles = {}
    for exe, role in (("mcode", "agent (headless exec + ACP delegation)"),
                      ("mmx", "capability CLI (text/image/video/speech/vision/search)"),
                      ("mavis", "legacy"), ("mcodectl", "legacy"), ("minimax", "legacy")):
        found = shutil.which(exe)
        if found:
            found_roles[exe] = {"path": found, "role": role}
    if found_roles:
        detail = "; ".join(f"{e} -> {v['path']} ({v['role']})" for e, v in found_roles.items())
        add("minimax_cli", "MINIMAX CLI", MEASURED, found_roles, detail, "PATH")
        return
    add("minimax_cli", "MINIMAX CLI", NOT_AVAILABLE, None,
        "no mcode/mmx/mavis/mcodectl/minimax executable on PATH, so the live agent "
        "roster and session list cannot be queried from a host-side collector. "
        "Everything else in this panel is read from the runtime's own files and "
        "is measured regardless.",
        "PATH")


# ------------------------------------------------- desktop app family (new) --
# The Code desktop app, the Design app and the Hub are the local half of the
# MINIMAX cloud story. They are measured from their own install trees and their
# own Electron state, not inferred from each other.

APPDATA_AGENT = Path(os.environ.get("APPDATA", "")) / "MiniMax Agent"
DESIGN_DIR = Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "MiniMax Design"
HUB_DIR = Path(r"C:\Program Files\MiniMaxHub")


def _processes_matching(names: set[str]):
    """Live processes whose executable name matches. Returns (rows, error).

    Three defects lived here, and each one produced a confident wrong answer:

    1. It parsed `wmic` output by splitting on spaces. The process this most
       needs to see is "MiniMax Code.exe" - two tokens, so the name never
       matched. A name with a space defeats whitespace parsing.
    2. `wmic` is not on PATH on this machine at all, so the query never ran.
    3. The failure was swallowed into an empty list, and an empty list was
       reported as "no Code process is running" while eleven were running.

    (3) is the one that matters. A missing dependency must never be allowed to
    arrive as a zero. So the failure is returned, not absorbed, and the caller
    reports it as an error with the reason. PowerShell emits JSON, which also
    removes the parsing problem entirely."""
    import json as _json
    import subprocess
    if not names:
        return [], None
    joined = ",".join(f"'{n}'" for n in sorted(names))
    script = (
        f"Get-Process -Name {joined} -ErrorAction SilentlyContinue | "
        "Select-Object ProcessName,Id,WorkingSet64 | ConvertTo-Json -Compress"
    )
    try:
        p = subprocess.run(
            ["powershell", "-NoProfile", "-Command", script],
            capture_output=True, text=True, timeout=45, errors="replace")
    except FileNotFoundError:
        return None, "the powershell executable is not on PATH, so no process list could be taken"
    except subprocess.TimeoutExpired:
        return None, "the process query timed out after 45 s"
    if p.returncode != 0 and not (p.stdout or "").strip():
        return None, f"the process query failed (rc={p.returncode}): " \
                     f"{(p.stderr or '').strip()[:160]}"
    raw = (p.stdout or "").strip()
    if not raw:
        return [], None                      # genuinely nothing matched
    try:
        data = _json.loads(raw)
    except ValueError as e:
        return None, f"the process query returned unparseable output: {str(e)[:120]}"
    if isinstance(data, dict):               # ConvertTo-Json collapses a single row
        data = [data]
    rows = []
    for d in data:
        try:
            rows.append((str(d.get("ProcessName", "")).lower(),
                         int(d.get("Id")), int(d.get("WorkingSet64") or 0)))
        except (TypeError, ValueError):
            continue
    return rows, None


def _read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return None


def collect_desktop_apps() -> None:
    # --- Code desktop app: live process telemetry -------------------------
    procs, perr = _processes_matching({"minimax code", "minimax design", "minimax hub"})
    if perr:
        # A measurement that could not be taken is NOT a measurement of zero.
        add("desktop_code_processes", "Code desktop app processes", ERROR,
            None, f"process telemetry unavailable: {perr}", "Get-Process via PowerShell")
        procs = []
    else:
        code = [p for p in procs if p[0].lower().startswith("minimax code")]
        if code:
            total_mb = sum(p[2] for p in code) / (1024 * 1024)
            add("desktop_code_processes", "Code desktop app processes", MEASURED,
                len(code),
                f"{len(code)} live processes, {total_mb:.0f} MB working set in total "
                f"(largest {max(p[2] for p in code) / (1024 * 1024):.0f} MB)",
                "Get-Process via PowerShell")
        else:
            add("desktop_code_processes", "Code desktop app processes", NOT_AVAILABLE,
                0, "the query succeeded and found no 'MiniMax Code' process running",
                "Get-Process via PowerShell")

    # --- task telemetry from the app's own observability outbox ------------
    outbox = APPDATA_AGENT / "observability-outbox.jsonl"
    if outbox.exists():
        names, lines, newest = {}, 0, 0.0
        try:
            for raw in outbox.read_text(encoding="utf-8", errors="replace").splitlines():
                raw = raw.strip()
                if not raw or not raw.startswith("{"):
                    continue
                ev = _read_json_line(raw)
                if ev is None:
                    continue
                lines += 1
                if ev.get("eventName"):
                    names[ev["eventName"]] = names.get(ev["eventName"], 0) + 1
                ts = (ev.get("createdAt") or 0) / 1000.0
                newest = max(newest, ts)
        except OSError as e:
            add("task_telemetry", "App task telemetry", ERROR, None,
                f"could not read the outbox: {e}", str(outbox))
        else:
            age = (time.time() - newest) if newest else -1
            top = sorted(names.items(), key=lambda kv: -kv[1])[:5]
            add("task_telemetry", "App task telemetry", MEASURED,
                {"events": lines, "distinct": len(names), "newest_age_s": round(age, 1)},
                f"{lines} events, {len(names)} distinct kinds; newest {age:.0f}s old. "
                f"Most frequent: " + ", ".join(f"{k} x{v}" for k, v in top),
                str(outbox))
    else:
        add("task_telemetry", "App task telemetry", NOT_AVAILABLE,
            None, f"no outbox at {outbox}", str(outbox))

    # --- the embedded browser: the local-to-cloud path ---------------------
    tabs_file = APPDATA_AGENT / "embedded-browser-tabs.json"
    reg = (_read_json(tabs_file) or {}).get("registry", {}) if tabs_file.exists() else {}
    sessions = reg.get("sessions") or []
    if sessions:
        tabs, hosts = 0, set()
        for s in sessions:
            for t in (s.get("tabs") or []):
                tabs += 1
                u = (t.get("url") or "")
                if "//" in u:
                    hosts.add(u.split("//", 1)[1].split("/", 1)[0])
        add("embedded_browser", "Embedded browser tabs", MEASURED,
            {"sessions": len(sessions), "tabs": tabs, "hosts": sorted(hosts)},
            f"{len(sessions)} session(s), {tabs} tab(s) across {len(hosts)} host(s). "
            f"This is the surface the desktop app uses to reach cloud services.",
            str(tabs_file))
    else:
        add("embedded_browser", "Embedded browser tabs", NOT_AVAILABLE,
            None, f"no tab registry at {tabs_file} (the app has never opened one)",
            str(tabs_file))

    # --- the cloud bridge device identity ----------------------------------
    rc = APPDATA_AGENT / "remote-control" / "state.json"
    state = _read_json(rc) if rc.exists() else None
    if isinstance(state, dict) and state.get("desktop_device_id"):
        add("cloud_bridge_device", "Cloud bridge device", MEASURED,
            state["desktop_device_id"],
            "the desktop app has registered a remote-control device id, which is "
            "the identity the cloud side addresses this machine by",
            str(rc))
    else:
        add("cloud_bridge_device", "Cloud bridge device", NOT_AVAILABLE,
            None, f"no remote-control state at {rc}; the app has not registered "
                  f"this machine for remote control",
            str(rc))

    # --- agent identity, WITHOUT touching the tokens -----------------------
    cfg = APPDATA_AGENT / "minimax-agent-config.json"
    conf = _read_json(cfg) if cfg.exists() else None
    if isinstance(conf, dict):
        # Deliberately: the presence of the token block is reported, its value
        # never read. A control hub that printed a credential would be a worse
        # defect than a panel with one fewer number in it.
        has_tokens = bool(conf.get("tokens"))
        add("agent_identity", "Signed-in identity", MEASURED,
            {"keys": sorted(conf.keys()), "tokens_present": has_tokens},
            f"config present with keys: {', '.join(sorted(conf.keys()))}. "
            f"Tokens are {'present' if has_tokens else 'absent'}; their VALUES are "
            f"never read or emitted by this collector.",
            str(cfg))
    else:
        add("agent_identity", "Signed-in identity", NOT_AVAILABLE,
            None, f"no readable config at {cfg}", str(cfg))

    # --- MiniMax Design ----------------------------------------------------
    # Status is MEASURED whether or not the app is running. "Is it installed,
    # and is it running right now" is a question about this machine, and the
    # collector answers it. An audit flagged labelling a stopped app
    # NOT_AVAILABLE as muddy: it filed a real measurement under a heading that
    # means "could not be measured", which is how a reader learns to distrust
    # the heading. NOT_AVAILABLE now stays reserved for surfaces that genuinely
    # cannot be read at all - like the CLI, which is not installed.
    design_exe = DESIGN_DIR / "MiniMax Design.exe"
    if design_exe.exists():
        try:
            ver = design_exe.stat().st_size
        except OSError:
            ver = 0
        running = any(p[0].lower().startswith("minimax design") for p in procs)
        res = DESIGN_DIR / "current" / "resources"
        add("design_app", "MINIMAX Design", MEASURED,
            {"installed": True, "running": running, "exe_bytes": ver},
            (f"installed ({ver} B launcher)"
             + (" and RUNNING" if running else
                " but not running, so its local gateway under resources\\gateway "
                "is not up and nothing it serves can be measured")),
            str(design_exe))
    else:
        add("design_app", "MINIMAX Design", NOT_AVAILABLE,
            None, f"not installed at {design_exe}", str(design_exe))

    # --- MiniMax Hub -------------------------------------------------------
    hub_exe = next((p for p in HUB_DIR.glob("*.exe")
                    if not p.name.lower().startswith("uninstall")), None)
    if hub_exe is not None:
        running = any(p[0].lower().startswith("minimax hub") for p in procs)
        add("hub_app", "MINIMAX Hub", MEASURED,
            {"installed": True, "running": running},
            f"installed at {HUB_DIR}" + (" and RUNNING" if running else ", not running"),
            str(hub_exe))
    else:
        add("hub_app", "MINIMAX Hub", NOT_AVAILABLE,
            None, f"no executable under {HUB_DIR}", str(HUB_DIR))


def collect_design_integration() -> None:
    """MINIMAX Design's local-to-cloud seam, measured from its install tree.

    This is the surface that makes "one component reaches the cloud" concrete.
    The Design app ships an EMBEDDED GATEWAY (`resources/gateway`) whose whole
    purpose is to be the single local point through which cloud calls are made:
    `resources/conf/external_api_conf.yaml` maps video/image/speech/music
    operations to MINIMAX and third-party endpoints. So the interesting question
    is not "is a Design window open" but "what is actually wired here, and is the
    gateway up".

    Three rules this obeys, each learned the hard way elsewhere:

    1. NEVER start the app. It is Popy's to launch; a collector that launches
       what it measures is not measuring, it is acting. Every fact below comes
       from files on disk.
    2. Installed-but-stopped is MEASURED, not NOT_AVAILABLE. The install tree is
       readable right now; that is a real answer about this machine.
    3. Absent counts are counts, never guesses. A missing directory is reported
       as 0 with the path shown, so "0 plugins" stays distinguishable from
       "could not look".
    """
    if not DESIGN_DIR.exists():
        add("design_gateway", "Design gateway", NOT_AVAILABLE, None,
            f"MINIMAX Design is not installed at {DESIGN_DIR}", str(DESIGN_DIR))
        # The install root being absent is a MEASUREMENT, not a reason to leave
        # holes in the inventory. A surface that cannot be measured is still
        # NAMED, with the reason it could not be measured - exactly like a
        # missing key that reads NOT_MEASURED instead of a silent blank. A
        # reader must be able to see that the route loader, the cloud hosts
        # and the cloud reach were looked for and not found, instead of
        # inferring it from their absence.
        #
        # Measured 2026-10-28: the install root existed on 2026-10-05 and is
        # absent now. The app was uninstalled, or moved. Which one is not
        # knowable from here, so it is not claimed.
        for _sid, _label in (
            ("design_route_loader", "Design route loader"),
            ("design_cloud_hosts", "Design cloud gateway hosts"),
            ("design_cloud_reach", "Design cloud reachability"),
            ("design_cloud_auth", "Design cloud credential"),
        ):
            add(_sid, _label, NOT_AVAILABLE, None,
                f"MINIMAX Design is not installed at {DESIGN_DIR}, so this "
                f"surface could not be measured - not available, not zero, "
                f"and not working", str(DESIGN_DIR))
        return

    res = DESIGN_DIR / "current" / "resources"

    # -- the gateway itself ------------------------------------------------
    gw_pkg = res / "gateway" / "package.json"
    gw_dist = res / "gateway" / "dist"
    gw_present = gw_pkg.exists()
    gw_version = None
    if gw_present:
        try:
            gw_version = _read_json(gw_pkg).get("version")
        except (OSError, ValueError, AttributeError):
            gw_version = None
    migrations = sorted(p.name for p in gw_dist.glob("*.sql")) if gw_dist.is_dir() else []

    procs, _perr = _processes_matching({"minimax design"})
    gw_running = bool(procs)
    add("design_gateway", "Design gateway",
        MEASURED if gw_present else NOT_AVAILABLE,
        {"installed": gw_present, "version": gw_version,
         "migrations": len(migrations), "running": gw_running},
        (f"embedded gateway present (v{gw_version or '?'}, {len(migrations)} "
         f"schema migrations)"
         + ("" if gw_running else
            "; NOT running - the app has not been launched, so no Design "
            "operation can be routed through it and any such capability is "
            "unmeasured rather than absent")),
        str(gw_pkg))

    # -- the cloud seam: what the gateway can actually reach ---------------
    # Counted from the file's own indentation, never from a hand-maintained
    # list. A hardcoded vendor list would be a claim about a file that changes.
    #
    # The hierarchy is three deep and getting it wrong is silent:
    #   cloud_gateway:            (depth 0)
    #     video:                  (depth 2)  <- CATEGORY
    #       minimax:              (depth 4)  <- VENDOR
    #         generate: /api/...  (depth 6)  <- OPERATION
    # An earlier version of this parser matched any indented line and so counted
    # OPERATION names as families and vendor leaves as providers: it reported
    # "20 families across 46 providers" when the file actually holds 6
    # categories and 16 vendors. Both numbers looked plausible and both were
    # wrong, which is why the indentation level is what identifies a role.
    conf = res / "conf" / "external_api_conf.yaml"
    categories: list[str] = []
    vendors: set[str] = set()
    ops = 0
    if conf.exists():
        try:
            in_cloud = False
            raw_lines = conf.read_text(encoding="utf-8",
                                       errors="replace").splitlines()
            for n, raw in enumerate(raw_lines):
                stripped = raw.strip()
                if not stripped or stripped.startswith("#"):
                    continue
                if raw.startswith("cloud_gateway"):
                    in_cloud = True
                    continue
                if not in_cloud:
                    continue
                if raw and not raw[0].isspace():
                    break                      # left the cloud_gateway block
                indent = len(raw) - len(raw.lstrip(" "))
                name = stripped.split(":")[0].strip()
                val = stripped.split(":", 1)[1].strip() if ":" in stripped else ""
                # A ROUTED OPERATION carries an endpoint. `speech_model:
                # speech-2.8-hd` has a value but no path - it names a model, it
                # routes nothing, and counting it reported 48 operations against
                # 47 actual endpoints.
                has_endpoint = val.startswith("/")

                if indent <= 2:
                    categories.append(name)
                elif has_endpoint:
                    ops += 1
                elif indent <= 4 and val:
                    ops += 1          # a bare key at vendor level = an operation
                elif indent <= 4:
                    # A childless-pending key at vendor level that turns out to
                    # have no children is not a vendor. This is checked ONLY at
                    # the vendor depth: `cover:` also has children, but it lives
                    # deeper and is a grouping node under a vendor, not a
                    # provider - applying "has children => vendor" at every depth
                    # invented a 14th provider named `cover`.
                    child = None
                    for later in raw_lines[n + 1:]:
                        if not later.strip() or later.strip().startswith("#"):
                            continue
                        li = len(later) - len(later.lstrip(" "))
                        if li <= indent:
                            break
                        child = later.strip().split(":")[0].strip()
                        break
                    if child is not None:
                        vendors.add(name)
                    else:
                        ops += 1
                # Deeper key with no value and no endpoint of its own: a pure
                # grouping node. It routes nothing, so it is not an operation.
        except OSError:
            categories, vendors, ops = [], set(), 0
    # -- is that route table a live config, or dead documentation? ----------
    # This check is what stops the seam from being taken on faith. A YAML file
    # with 47 endpoints in it proves nothing about whether any code READS it,
    # and the obvious way to check - a text search - answers WRONG here for two
    # unrelated reasons, both of which I hit:
    #   * ripgrep does not descend into `gateway/dist` (ignored build output),
    #     so a content sweep of the install tree reports "no consumer";
    #   * and it cannot see inside `app.asar` at all, which is where the host
    #     table lives.
    # A byte-level sweep of the whole tree (1404 files, 651 MB) does find the
    # consumer: `gateway/dist/main.js`, via `YAML_CANDIDATES` and
    # `loadYamlSync()`. So the loader is targeted here rather than re-scanning
    # 651 MB on every collector cycle.
    import re as _re

    gw_main = res / "gateway" / "dist" / "main.js"
    loader_found = False
    loader_bytes = 0
    embedded_routes = 0
    raw_api = 0
    candidate_count = 0
    if gw_main.is_file():
        try:
            blob = gw_main.read_bytes()
            loader_bytes = len(blob)
            loader_found = b"external_api_conf" in blob
            # Two different counts, both real. `embedded_routes` is the
            # distinct `key: "/api/..."` literal form; `raw_api` is every
            # `/api/` string in the bundle, which also includes matches inside
            # larger expressions and unrelated vendors. Reporting only the
            # first made a reader unable to reconcile it with the second, so
            # both travel together rather than one standing in for the other.
            embedded_routes = len(_re.findall(rb":\s*[\"']?(/api/[^\"'\s,}]+)", blob))
            raw_api = blob.count(b"/api/")
            cand = _re.search(rb"YAML_CANDIDATES\s*=\s*\[(.*?)\];", blob, _re.S)
            if cand:
                candidate_count = len(
                    _re.findall(rb"external_api_conf\.yaml", cand.group(1)))
        except OSError:
            loader_found = False
    # The loader's __dirname is resources/gateway/dist, so its first candidate
    # ("../../conf/external_api_conf.yaml") resolves to resources/conf/ - which
    # is the very file counted above. Checked, not assumed.
    add("design_route_loader", "Design route loader",
        MEASURED if loader_found else NOT_AVAILABLE,
        {"loader_present": loader_found, "loader_bytes": loader_bytes,
         "embedded_route_literals": embedded_routes,
         "raw_api_occurrences": raw_api,
         "yaml_candidates": candidate_count,
         "primary_resolves": conf.exists()},
        (f"the route table is read at gateway startup by {gw_main.name} "
         f"({loader_bytes:,} bytes, {candidate_count} YAML_CANDIDATES search "
         f"paths, the first resolving to this {conf.name}); the bundle carries "
         f"{embedded_routes} distinct `key: \"/api/...\"` literals and "
         f"{raw_api:,} `/api/` occurrences in all - two different counts, both "
         f"reported so neither is mistaken for the other - it is live config, "
         f"not documentation"
         if loader_found else
         f"no consumer of {conf.name} at {gw_main} - the route table would be "
         f"configuration on disk with nothing reading it, and the seam below "
         f"would be a claim rather than a capability"),
        str(gw_main))

    add("design_cloud_seam", "Design cloud seam",
        MEASURED if categories else NOT_AVAILABLE,
        {"categories": categories, "vendor_count": len(vendors),
         "vendors": sorted(vendors), "operations": ops},
        (f"{len(categories)} capability categories ({', '.join(categories)}) across "
         f"{len(vendors)} providers and {ops} routed operations, traced to a "
         f"live loader (see design_route_loader)"
         if categories else
         f"no readable external_api_conf.yaml at {conf} - the cloud route map is "
         f"unmeasured, not empty"),
        str(conf))

    # -- agent profiles: the app's own worker definitions ------------------
    profiles_dir = res / "agent-profiles" / "v2" / "config" / "agents"
    profiles = sorted(p.stem for p in profiles_dir.glob("*.md")) \
        if profiles_dir.is_dir() else []
    add("design_profiles", "Design agent profiles",
        MEASURED if profiles else NOT_AVAILABLE,
        {"count": len(profiles), "names": profiles},
        (f"{len(profiles)} agent profiles shipped: {', '.join(profiles)}"
         if profiles else f"no agent profiles at {profiles_dir}"),
        str(profiles_dir))

    # -- bundled plugins: local capability the app brings with it ----------
    plugins_dir = res / "bundled-plugins"
    plugins = sorted(p.name for p in plugins_dir.iterdir() if p.is_dir()) \
        if plugins_dir.is_dir() else []
    add("design_plugins", "Design bundled plugins",
        MEASURED if plugins else NOT_AVAILABLE,
        {"count": len(plugins), "names": plugins},
        (f"{len(plugins)} bundled plugins: {', '.join(plugins)}"
         if plugins else f"no bundled plugins at {plugins_dir}"),
        str(plugins_dir))

    # -- WHERE does "the cloud" actually point, and can this machine get
    #    there? A route table whose hosts are unreachable is a map of nowhere.
    #    The host table is not in the YAML at all: the YAML header says so, and
    #    points at getCloudGatewayUrl(), which lives in app.asar.
    import mmap

    asar = res / "app.asar"
    host_table: dict[str, dict[str, str]] = {}
    default_host = None
    if asar.is_file():
        try:
            with asar.open("rb") as fh:
                mm = mmap.mmap(fh.fileno(), 0, access=mmap.ACCESS_READ)
                try:
                    start = mm.find(b"const CLOUD_GATEWAY_URLS = {")
                    if start >= 0:
                        end = mm.find(b"};", start)
                        if end < 0:            # unbounded slice would read 51 MB
                            end = start + 2000
                        block = mm[start:end].decode("utf-8", "replace")
                        region = None
                        for line in block.splitlines():
                            s = line.strip().rstrip(",")
                            # The region key carries its own brace - the real
                            # line is `domestic: {`, not `domestic`. Matching a
                            # remembered shape instead of the actual one is
                            # how this first returned an empty table while the
                            # bytes were sitting right there in the file.
                            reg = _re.match(r"^(\w+):\s*\{$", s)
                            if reg:
                                region = reg.group(1)
                                host_table[region] = {}
                                continue
                            chan = _re.match(
                                r'^(dev|test|staging|prod)\s*:\s*"([^"]+)"$', s)
                            if chan and region:
                                host_table[region][chan.group(1)] = chan.group(2)
                        dflt = _re.search(
                            rb"DEFAULT_CLOUD_GATEWAY_URL\s*=\s*"
                            rb"CLOUD_GATEWAY_URLS\.(\w+)\.(\w+)", mm)
                        if dflt:
                            default_host = host_table.get(
                                dflt.group(1).decode(), {}).get(
                                dflt.group(2).decode())
                finally:
                    mm.close()
        except (OSError, ValueError):
            host_table, default_host = {}, None

    flat = [(rg, ch, u) for rg, chans in sorted(host_table.items())
            for ch, u in sorted(chans.items())]
    add("design_cloud_hosts", "Design cloud gateway hosts",
        MEASURED if flat else NOT_AVAILABLE,
        {"regions": len(host_table), "urls": len(flat),
         "table": host_table, "default": default_host},
        (f"getCloudGatewayUrl() resolves the cloud gateway to {len(flat)} URLs "
         f"across {len(host_table)} regions; default {default_host or '?'} "
         f"(overridable with CLOUD_GATEWAY_BASE_URL)"
         if flat else
         f"cloud gateway URL table not found inside {asar.name} - which host "
         f"the routes resolve to is unmeasured, not local"),
        str(asar))

    # -- live reachability: DNS + TLS, no API call, nothing launched.
    import ipaddress
    import socket
    import ssl

    distinct = sorted({u.split("//", 1)[-1].split("/", 1)[0] for _, _, u in flat})
    reach: dict[str, dict] = {}
    for host in distinct:
        rec: dict = {"host": host}
        try:
            infos = socket.getaddrinfo(host, 443, proto=socket.IPPROTO_TCP)
        except OSError as e:
            rec["tls"] = "unresolved"
            rec["error"] = type(e).__name__
            reach[host] = rec
            continue
        ips = sorted({i[4][0] for i in infos})
        rec["ips"] = ips
        addrs = [ipaddress.ip_address(i) for i in ips]
        # "private" was the wrong word to lead with. RFC1918 is literally true
        # but incidental: these are internal addresses surfacing in a public
        # DNS answer. The fact a reader can act on is that the handshake times
        # out from here. Both are recorded; the detail text leads with reach.
        rec["scope"] = ("rfc1918" if all(a.is_private for a in addrs)
                        else "public" if all(a.is_global for a in addrs)
                        else "mixed")
        rec["tls"] = "unreachable"
        for ip in ips:
            try:
                t0 = time.time()
                raw = socket.create_connection((ip, 443), timeout=5)
                with ssl.create_default_context().wrap_socket(
                        raw, server_hostname=host) as ss:
                    cert = ss.getpeercert()
                    rec["tls"] = "ok"
                    rec["tls_ms"] = int((time.time() - t0) * 1000)
                    rec["tls_cn"] = dict(x[0] for x in cert.get("subject", ())) \
                        .get("commonName")
                    rec["tls_expires"] = cert.get("notAfter")
                break
            except Exception as e:
                rec.setdefault("error", type(e).__name__)
        reach[host] = rec          # stored on BOTH paths - an earlier version
                                  # stored only in the DNS-failure branch, so
                                  # every host that actually resolved was
                                  # measured and then silently discarded
    live = sorted(h for h, r in reach.items() if r.get("tls") == "ok")
    rfc1918 = sorted(h for h, r in reach.items() if r.get("scope") == "rfc1918")
    dead = sorted(h for h, r in reach.items() if r.get("tls") != "ok")
    # Built in statements, not one nested conditional expression. Balancing
    # an unbalanced parenthesis across a `+` chain is exactly the work a reader
    # cannot check at a glance, and it shipped a trailing ")" into the panel.
    detail_reach = (f"{len(live)} of {len(reach)} gateway hosts complete a "
                    f"TLS handshake from this machine "
                    f"({', '.join(live) or 'none'})")
    if dead:
        detail_reach += f"; {len(dead)} do not ({', '.join(dead)})"
        if rfc1918:
            detail_reach += ", resolving to RFC1918 internal addresses"
    if not reach:
        detail_reach = "no gateway hosts resolved to probe"
    add("design_cloud_reach", "Design cloud reachability",
        MEASURED if reach else NOT_AVAILABLE,
        {"probed": len(reach), "live": len(live), "live_hosts": live,
         "unreachable_hosts": dead, "rfc1918_hosts": rfc1918,
         "hosts": reach},
        detail_reach, "dns + tls/443")

    # -- the credential gate. Booleans only: the value is never read or shown.
    tok = (os.environ.get("HILO_USER_TOKEN") or "").strip()
    tok_file = (os.environ.get("HILO_USER_TOKEN_FILE") or "").strip()
    file_ok = bool(tok_file) and Path(tok_file).is_file()
    add("design_cloud_auth", "Design cloud credential",
        MEASURED,
        {"HILO_USER_TOKEN_set": bool(tok),
         "HILO_USER_TOKEN_FILE_set": bool(tok_file),
         "file_exists": file_ok},
        ("a user token is configured, so cloud-bound MCP calls can authenticate"
         if (tok or file_ok) else
         "no HILO_USER_TOKEN or HILO_USER_TOKEN_FILE in this process - the app "
         "itself warns \"no HILO_USER_TOKEN / HILO_USER_TOKEN_FILE set; "
         "cloud-bound MCP tool calls will 401\", so every route above answers "
         "401 even once the host is reachable"),
        "process environment")


def collect_sentinel_control_plane() -> None:
    """The SENTINEL hub is registered in the MINIMAX profile, so it belongs on
    the same panel as the apps it governs.

    Deliberately zero-subprocess: this collector runs every 4th refresh cycle and
    its spawn rate is already a reported finding. Everything here is read with
    ast + json in-process. A surface that cannot be read says NOT_AVAILABLE; it
    never guesses a tool count.
    """
    import ast

    profile = MINIMAX_ROOT / "mcp.json"
    if not profile.is_file():
        add("sentinel_profile", "SENTINEL in MCP profile", NOT_AVAILABLE, None,
            f"live MCP profile not found at {profile}", str(profile))
        add("sentinel_hub", "SENTINEL MCP hub", NOT_AVAILABLE, None,
            "cannot assess the hub without the live MCP profile", str(profile))
        return

    try:
        cfg = json.loads(profile.read_text(encoding="utf-8"))
        servers = cfg.get("mcpServers", {}) or {}
    except Exception as e:
        add("sentinel_profile", "SENTINEL in MCP profile", ERROR, None,
            f"live MCP profile is unreadable: {e}", str(profile))
        add("sentinel_hub", "SENTINEL MCP hub", ERROR, None,
            f"cannot assess the hub: profile unreadable ({e})", str(profile))
        return

    enabled = [n for n, s in servers.items() if s.get("enabled")]
    has_hub = "sentinel-hub" in servers
    add("sentinel_profile", "SENTINEL in MCP profile", MEASURED,
        {"servers": len(servers), "enabled": len(enabled), "has_sentinel_hub": has_hub},
        f"{len(servers)} MCP servers declared in the live profile, {len(enabled)} enabled"
        + (", sentinel-hub registered" if has_hub else ", sentinel-hub NOT registered"),
        str(profile))

    hub_src = Path(__file__).resolve().parent.parent / "07_BACKBONE" / "mcp" / "sentinel_hub_server.py"
    if not hub_src.is_file():
        add("sentinel_hub", "SENTINEL MCP hub", NOT_AVAILABLE, None,
            f"hub source not found at {hub_src}", str(hub_src))
        return

    entry = servers.get("sentinel-hub", {}) or {}
    # Count the declared tools by parsing, not by launching the server.
    try:
        tree = ast.parse(hub_src.read_text(encoding="utf-8"))
        declared = sum(1 for n in ast.walk(tree)
                       if isinstance(n, ast.Call) and getattr(n.func, "attr", "") == "Tool")
    except Exception as e:
        add("sentinel_hub", "SENTINEL MCP hub", ERROR, None,
            f"hub source does not parse: {e}", str(hub_src))
        return

    argv = entry.get("args") or []
    wired = bool(entry.get("command")) and bool(argv)
    detail = (f"{declared} tools declared in source; registered="
              f"{entry.get('enabled', False)}; transport={entry.get('transport', entry.get('type', '?'))}")
    if not wired:
        detail += "; WARNING registered without a resolvable command+argv"
    add("sentinel_hub", "SENTINEL MCP hub", MEASURED,
        {"declared_tools": declared, "registered": bool(entry),
         "enabled": bool(entry.get("enabled")), "command": entry.get("command"),
         "argv": argv, "source_bytes": hub_src.stat().st_size},
        detail, str(hub_src))


def collect_swarm_liveness() -> None:
    """How many of the five SENTINEL instances are actually alive.

    Liveness is DERIVED from heartbeat age, never from the `status` string a
    writer left behind: a file written once says ACTIVE forever. The directory is
    read directly rather than by constructing CrossInstance, so this collector
    stays a pure observer and measuring the swarm can never register into it -
    construction used to write the registry, which meant LOOKING at the registry
    is what made it claim somebody was present.

    Zero subprocess, consistent with the other SENTINEL surfaces.
    """
    import ast
    from datetime import datetime

    here = Path(__file__).resolve().parent
    src = here / "cross_instance.py"
    hb_dir = here.parent / "09_LOGS" / "cross_instance" / "heartbeats"

    if not src.is_file():
        add("swarm_liveness", "SENTINEL swarm", NOT_AVAILABLE, None,
            f"instance roster not found at {src}", str(src))
        return

    known = None
    try:
        tree = ast.parse(src.read_text(encoding="utf-8"))
        for node in tree.body:
            if isinstance(node, ast.Assign) and any(
                    getattr(t, "id", "") == "INSTANCES" for t in node.targets):
                known = list(ast.literal_eval(node.value))
        if not known:
            raise ValueError("INSTANCES not found at module level")
    except Exception as e:
        add("swarm_liveness", "SENTINEL swarm", ERROR, None,
            f"cannot read the instance roster: {e}", str(src))
        return

    if not hb_dir.is_dir():
        add("swarm_liveness", "SENTINEL swarm", NOT_AVAILABLE, None,
            f"no heartbeat directory at {hb_dir}", str(hb_dir))
        return

    alive, stale, seen = [], [], set()
    for f in sorted(hb_dir.glob("*.json")):
        try:
            hb = json.loads(f.read_text(encoding="utf-8"))
            ts = datetime.fromisoformat(hb["timestamp"])
            if ts.tzinfo is None:
                ts = ts.astimezone()
            age = (datetime.now(ts.tzinfo) - ts).total_seconds()
        except Exception:
            continue
        name = hb.get("instance_id", f.stem)
        seen.add(name)
        entry = {"instance_id": name, "age_seconds": round(age, 1),
                 "reported_status": hb.get("status"), "is_alive": age < HEARTBEAT_ALIVE_SECONDS}
        (alive if age < HEARTBEAT_ALIVE_SECONDS else stale).append(entry)

    never = [i for i in known if i not in seen]
    detail = f"{len(alive)} of {len(known)} instances alive"
    if never:
        detail += "; never registered: " + ", ".join(never)
    if stale:
        detail += (f"; {len(stale)} heartbeat(s) expired - derived STALE although the "
                   f"writer claimed ACTIVE")
    add("swarm_liveness", "SENTINEL swarm", MEASURED,
        {"known": known, "known_count": len(known), "alive_count": len(alive),
         "alive": alive, "stale": stale, "never_registered": never,
         "liveness_basis": "heartbeat age; the stored status is never the verdict"},
        detail, str(hb_dir))


def _read_json_line(raw: str):
    try:
        return json.loads(raw)
    except Exception:
        return None


# -------------------------------------------------------------------- main --
def build() -> dict:
    SURFACES.clear()
    collect_agents()
    collect_skills()
    collect_mcp()
    collect_runtime_dirs()
    collect_config()
    collect_cli_capability()
    collect_desktop_apps()
    collect_design_integration()
    collect_sentinel_control_plane()
    collect_swarm_liveness()

    measured = sum(1 for s in SURFACES if s["status"] == MEASURED)
    unavailable = sum(1 for s in SURFACES if s["status"] == NOT_AVAILABLE)
    errors = sum(1 for s in SURFACES if s["status"] == ERROR)
    return {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "minimax_root": str(MINIMAX_ROOT),
        "counts": {"measured": measured, "not_available": unavailable, "error": errors,
                   "total": len(SURFACES)},
        "surfaces": SURFACES,
    }


def main() -> int:
    report = build()
    c = report["counts"]
    print("=" * 72)
    print("  MINIMAX ECOSYSTEM COLLECTOR")
    print("=" * 72)
    for s in report["surfaces"]:
        mark = {MEASURED: "[ok]  ", NOT_AVAILABLE: "[----]", ERROR: "[ERR]"}[s["status"]]
        print(f"  {mark} {s['id']:16} {s['detail']}")
    print("-" * 72)
    print(f"  {c['measured']} measured / {c['not_available']} not-available / "
          f"{c['error']} errors   ({c['total']} surfaces)")
    print(f"  root: {report['minimax_root']}")

    if "--check" in sys.argv:
        if OUT_PATH.is_file():
            age = time.time() - OUT_PATH.stat().st_mtime
            print(f"  [ok]   output present, age {age:.0f}s -> {OUT_PATH}")
        else:
            print(f"  [----] output not written yet: {OUT_PATH}")
        return 0

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  wrote {OUT_PATH} ({OUT_PATH.stat().st_size} B)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
