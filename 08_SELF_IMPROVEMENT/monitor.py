#!/usr/bin/env python3
"""
SENTINEL self-monitor. Produces one health.json, consumed by the Command
Center and by MCP.

THE ONE RULE THIS FILE EXISTS TO ENFORCE
---------------------------------------
A check that did not run is not a passing check, and a check whose verdict is
a hardcoded sentence is not a check. Every entry below is computed from a
measurement taken NOW, and the status vocabulary has four values on purpose:

    OK        measured, and the measurement is within bounds
    FAIL      measured, and the measurement is out of bounds
    STALE      measured, but the underlying artefact is older than its bound
    NOT_RUN   the check could not run; the reason is recorded

NOT_RUN is a first-class status. A panel that cannot say "I did not check" will
eventually be believed when it did not check.

Nothing here writes outside SENTINEL_PRIME, and nothing here decides anything:
it measures. The Command Center renders; it does not rule.

Usage:
    python 08_SELF_IMPROVEMENT\\monitor.py            # human report
    python 08_SELF_IMPROVEMENT\\monitor.py --json     # machine report

health.json is rewritten on every run. It used to be written only under
`--write`, which nobody passes routinely, so the file the dashboard read aged
silently and served a verdict a live run no longer produced. `--write` is still
accepted and ignored.
"""
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

WORKSPACE = Path(os.environ.get(
    'WORKSPACE_ROOT',
    r'C:\Users\apviz\.minimax-agent\projects\SENTINEL_PRIME'))
BRAIN = WORKSPACE / '11_BRAIN'
PROGRAM = WORKSPACE / '12_PROGRAM'
LOGS = WORKSPACE / '09_LOGS'
CC = WORKSPACE / '13_COMMAND_CENTER'
HEALTH_FILE = CC / 'api' / 'health.json'

STALE_SECONDS = 300          # 5 minutes: a state file older than this is STALE
MAX_STATE_AGE = 3600         # 1 hour: beyond this the workflow is not trusted
# A handshake record describes CODE, not a transient state. Reusing the
# workflow's 1 hour here was a category error: a workflow genuinely changes
# within the hour, while the hub either starts or it does not, and that fact
# only changes when the code or the environment does. The sharp arm is
# `superseded` - the server edited after the record was written - which is
# what actually caught the original problem. The age arm is the backstop for
# the other way the world changes without the source moving: an SDK or Python
# upgrade. A day says "if nobody re-probed this in a day, we do not claim to
# know", and matches the fact that the record only refreshes when someone asks.
HANDSHAKE_MAX_AGE = 86400    # 1 day

OK, FAIL, STALE, NOT_RUN = 'OK', 'FAIL', 'STALE', 'NOT_RUN'


def _now() -> str:
    return datetime.now().isoformat()


def check(cid: str, family: str, status: str, value: Any, evidence: str,
          bound: str = '') -> Dict[str, Any]:
    return {
        'id': cid,
        'family': family,
        'status': status,
        'value': value,
        'bound': bound,
        'evidence': evidence,
        'measured_at': _now(),
    }


def age_seconds(path: Path) -> Optional[float]:
    if not path.exists():
        return None
    return time.time() - path.stat().st_mtime


def _read_unplaced() -> Optional[int]:
    """How many verbatim messages are unplaced, or None if it is unknown.

    The count is recorded in 02_CHAPTERS/UNPLACED.md and NOWHERE else - not in
    corpus_stats.json, not in chapter_map.json. Returning None when the file is
    absent is the point: a missing source is UNKNOWN, and unknown is not zero.
    """
    f = BRAIN / '02_CHAPTERS' / 'UNPLACED.md'
    if not f.exists():
        return None
    try:
        txt = f.read_text(encoding='utf-8', errors='replace')
    except OSError:
        return None
    if '**None.**' in txt:
        return 0
    return len(re.findall(r'(?m)^\s*[-*]\s', txt))



# ---------------------------------------------------------------- corpus

def corpus_checks() -> List[Dict[str, Any]]:
    out = []
    corpus = BRAIN / '01_RAW' / 'corpus_full.jsonl'
    stats = BRAIN / '01_RAW' / 'corpus_stats.json'
    freeze = LOGS / 'corpus_freeze' / 'SHA256SUMS.txt'
    chapters = BRAIN / '02_CHAPTERS'
    index = BRAIN / '00_CORPUS_INDEX.md'

    a = age_seconds(corpus)
    out.append(check(
        'corpus_present', 'corpus', OK if corpus.exists() else FAIL,
        corpus.stat().st_size if corpus.exists() else 0,
        f'corpus_full.jsonl age={a:.0f}s' if a is not None else 'corpus missing',
        'file must exist'))

    out.append(check(
        'corpus_fresh', 'corpus',
        OK if (a is not None and a < MAX_STATE_AGE) else (STALE if a is not None else NOT_RUN),
        round(a, 1) if a is not None else None,
        'extraction is a snapshot; older than the bound means the conversation moved on',
        f'< {MAX_STATE_AGE}s'))

    s = None
    if stats.exists():
        try:
            s = json.loads(stats.read_text(encoding='utf-8'))
        except json.JSONDecodeError as exc:
            out.append(check('corpus_stats_parse', 'corpus', FAIL, None, str(exc)))
    # Two of the keys read here used to be invented: `total_user_turns` and
    # `unplaced_messages` are NOT in corpus_stats.json (the real key is
    # `user_turns`, and the file carries no unplaced figure at all). `.get()`
    # returned None for both, so the monitor reported turns=None and, worse,
    # raised a FAIL on corpus_no_unplaced for a corpus that has zero unplaced
    # messages. A detector that manufactures a failure from a missing key is
    # worse than no detector: it teaches the reader to ignore it.
    unplaced = _read_unplaced()
    out.append(check(
        'corpus_stats', 'corpus', OK if s else NOT_RUN,
        {'messages': s.get('messages_total'), 'turns': s.get('user_turns'),
         'unplaced': unplaced} if s else None,
        'corpus_stats.json parsed' if s else 'corpus_stats.json missing or unreadable'))

    if s:
        out.append(check(
            'corpus_no_unplaced', 'corpus',
            OK if unplaced == 0 else (FAIL if unplaced is not None else NOT_RUN),
            unplaced,
            ('UNPLACED.md declares "None" - every verbatim message belongs to a chapter'
             if unplaced == 0 else
             ('UNPLACED.md lists %s entr(y/ies)' % unplaced if unplaced is not None
              else 'UNPLACED.md not found - the unplaced count is UNKNOWN, not zero')),
            '== 0'))

        retention = (s.get('retention') or {}).get('verbatim_retention_ratio')
        out.append(check(
            'corpus_retention', 'corpus',
            OK if (retention is not None and retention >= 0.95) else FAIL, retention,
            'emitted verbatim text vs extracted source text - the "nothing cut" measure',
            '>= 0.95'))

    ch_files = sorted(chapters.glob('CH_*.md')) if chapters.exists() else []
    out.append(check(
        'corpus_chapters', 'corpus', OK if len(ch_files) > 0 else FAIL, len(ch_files),
        f'{len(ch_files)} chapter files under 02_CHAPTERS/', '> 0'))

    unplaced_file = chapters / 'UNPLACED.md'
    empty_unplaced = False
    if unplaced_file.exists():
        txt = unplaced_file.read_text(encoding='utf-8')
        empty_unplaced = '**None.**' in txt
    out.append(check(
        'corpus_unplaced_declared', 'corpus', OK if empty_unplaced else NOT_RUN,
        empty_unplaced,
        'UNPLACED.md must exist and state that nothing was dropped',
        'file present and empty'))

    for cid, path in (('corpus_index', index), ('corpus_freeze', freeze)):
        a = age_seconds(path)
        out.append(check(
            cid, 'corpus', OK if path.exists() else FAIL,
            {'bytes': path.stat().st_size} if path.exists() else 0,
            f'{path.name} age={a:.0f}s' if a is not None else f'{path.name} missing',
            'file must exist'))
    return out


# -------------------------------------------------------------- workflow

def workflow_checks() -> List[Dict[str, Any]]:
    out = []
    state = LOGS / 'bimodal_state.json'
    if not state.exists():
        out.append(check('workflow_state', 'workflow', NOT_RUN, None,
                         'bimodal_state.json missing - the workflow has never run here',
                         'file must exist'))
        return out

    try:
        wf = json.loads(state.read_text(encoding='utf-8'))
    except json.JSONDecodeError as exc:
        out.append(check('workflow_state', 'workflow', FAIL, None,
                         f'state file is not valid JSON: {exc}'))
        return out

    mode = wf.get('mode')
    stop_reason = wf.get('stop_reason')
    stopped_at = wf.get('stopped_at')
    failures = wf.get('consecutive_failures', 0)

    out.append(check(
        'workflow_mode', 'workflow',
        OK if mode in ('MODE_A', 'R0', 'MODE_B', 'STOPPED') else FAIL, mode,
        'MODE_A -> R0 -> MODE_B -> STOPPED; anything else is a corrupted machine',
        'one of the four modes'))

    # THE CHECK THAT WOULD HAVE CAUGHT THE 2026-10-04 DEFECT.
    # A STOPPED mode must carry a reason and a timestamp. Before the fix,
    # STOPPED was never assigned and a real stop was erased by the next persist.
    if mode == 'STOPPED':
        complete = bool(stop_reason) and bool(stopped_at)
        out.append(check(
            'workflow_stop_visible', 'workflow', OK if complete else FAIL,
            {'stop_reason': bool(stop_reason), 'stopped_at': bool(stopped_at)},
            'STOPPED must be observable: mode, reason and timestamp all present',
            'reason AND timestamp present'))
    else:
        # A non-STOPPED mode carrying a stop reason would be a leak in the other
        # direction: a stop that is no longer honoured.
        leaked = mode != 'MODE_A' and bool(stop_reason)
        out.append(check(
            'workflow_stop_consistent', 'workflow', FAIL if leaked else OK,
            {'mode': mode, 'stop_reason': stop_reason},
            'a stop reason outside MODE_A/STOPPED is inconsistent state',
            'no orphaned stop reason'))

    out.append(check(
        'workflow_failures', 'workflow', OK if failures < 5 else FAIL, failures,
        '5 consecutive MODE_B failures must land in STOPPED, never a 6th attempt',
        '< 5'))

    a = age_seconds(state)
    out.append(check(
        'workflow_state_fresh', 'workflow',
        OK if (a is not None and a < STALE_SECONDS) else STALE,
        round(a, 1) if a is not None else None,
        'how long since the workflow last wrote its state', f'< {STALE_SECONDS}s'))

    log = LOGS / 'bimodal_workflow.log'
    a = age_seconds(log)
    out.append(check(
        'workflow_log', 'workflow',
        OK if (a is not None and a < STALE_SECONDS * 6) else (STALE if a is not None else NOT_RUN),
        round(a, 1) if a is not None else None,
        'transition log freshness', f'< {STALE_SECONDS * 6}s'))
    return out


# ------------------------------------------------------------------ code

def code_checks() -> List[Dict[str, Any]]:
    out = []
    si = WORKSPACE / '08_SELF_IMPROVEMENT'
    modules = ['bimodal_workflow', 'sentinel_orchestrator', 'multimodal_processor',
               'self_modify_engine', 'universal_compat', 'browser_automation',
               'cross_instance', 'backup_system', 'performance_tracker',
               'corpus_extractor', 'self_improvement', 'monitor']
    missing = []
    for m in modules:
        if not (si / f'{m}.py').exists():
            missing.append(m)
    out.append(check(
        'code_modules_present', 'code', OK if not missing else FAIL,
        {'expected': len(modules), 'missing': missing},
        'each engine must exist as a file', 'none missing'))

    # The language law, measured by scanning rather than by trusting the suite.
    offenders = []
    # The character class is written with \\u escapes on purpose. Written as
    # literal diacritics it would be flagged by its own scan - the detector
    # flagging its own implementation - which is the same class of mistake as a
    # test fixture that reproduces the bug it exists to catch.
    try:
        import re
        pattern = re.compile('[\u0103\u00e2\u00ee\u0219\u021b\u0102\u00c2\u00ce\u0218\u021a\u015f\u0163]')
        for py in sorted(si.glob('*.py')):
            try:
                text = py.read_text(encoding='utf-8')
            except (OSError, UnicodeDecodeError):
                continue
            for i, line in enumerate(text.splitlines(), 1):
                if line.lstrip().startswith('#') or 'coding' in line[:40]:
                    continue
                if pattern.search(line):
                    offenders.append(f'{py.name}:{i}')
    except Exception as exc:
        out.append(check('code_language_scan', 'code', NOT_RUN, None, str(exc)))
    else:
        out.append(check(
            'code_no_romanian', 'code', OK if not offenders else FAIL, offenders[:20],
            'the language law: code, identifiers, docstrings and runtime messages in '
            'English. Romanian belongs in wisdom, not in source.', 'no diacritics in code'))

    ts = si / 'test_suite.py'
    out.append(check(
        'code_test_suite', 'code', OK if ts.exists() else FAIL,
        {'bytes': ts.stat().st_size} if ts.exists() else 0,
        'test harness present', 'file must exist'))
    return out


# --------------------------------------------------------------- wiring

def _npx_resolution_check(npx_specs):
    """Resolve every npx package the config declares, with a control package.

    The control is what makes this a measurement. Without it, an unreachable
    registry and a 404 are indistinguishable, and the check would report FAIL
    for a network outage - the instrument fault that looks like a product fault.
    """
    if not npx_specs:
        return check('mcp_npx_packages_resolve', 'wiring', NOT_RUN, None,
                     'no npx entries declared in the config', 'every npx package resolves')

    import subprocess

    packages = []
    for sname, sspec in npx_specs:
        for arg in (sspec.get('args') or []):
            a = str(arg)
            if a.startswith('-') or a in ('npx', 'node', 'python'):
                continue
            # A path, not a package: drive letters, backslashes, or a file
            # extension. Every scoped npm package contains "/" (@scope/name), so
            # "/" cannot be the discriminator - the first version of this filter
            # used it and silently matched nothing, reporting an empty list while
            # looking like it had run.
            if '\\' in a or ':' in a or a.lower().endswith(('.py', '.js', '.mjs', '.cmd')):
                continue
            if not re.match(r'^(@[a-z0-9-]+/)?[a-z0-9][a-z0-9._-]*$', a, re.I):
                continue
            if a not in [p for _, p in packages]:
                packages.append((sname, a))

    # Resolve npm through the project's own resolver. Bare 'npm' raises
    # FileNotFoundError in a subprocess started by an agent runtime, because the
    # inherited PATH predates the node install - the same failure class already
    # documented for tesseract. Resolving it explicitly is what makes this check
    # able to see the 404s at all.
    try:
        import tool_resolver
        npm_path = tool_resolver.resolve('npm')['path'] if 'npm' in tool_resolver.KNOWN_LOCATIONS else None
    except Exception:
        npm_path = None
    if not npm_path:
        import shutil as _sh
        npm_path = _sh.which('npm')
    if not npm_path:
        return check(
            'mcp_npx_packages_resolve', 'wiring', NOT_RUN,
            {'declared': [p for _, p in packages]},
            'npm could not be located by the resolver or by PATH - the check '
            'could not run, so it is NOT_RUN and not FAIL',
            'every npx package resolves')

    def _ask(pkg):
        try:
            r = subprocess.run([npm_path, 'view', pkg, 'version', '--silent'],
                               capture_output=True, text=True, timeout=90)
            out = (r.stdout or '').strip()
            return out if r.returncode == 0 and out else None
        except (OSError, subprocess.SubprocessError):
            return None

    control = _ask('react')
    if control is None:
        return check(
            'mcp_npx_packages_resolve', 'wiring', NOT_RUN,
            {'declared': [p for _, p in packages]},
            'npm registry unreachable (control package did not resolve) - '
            'nothing was falsified, so this is NOT_RUN and not FAIL',
            'every npx package resolves')

    # Bolt Optimization: Run npm checks in parallel to significantly reduce execution time
    import concurrent.futures

    resolved, missing = [], []
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        # Submit the declared packages checks
        futures_pkg = {executor.submit(_ask, pkg): (sname, pkg) for sname, pkg in packages}

        for future in concurrent.futures.as_completed(futures_pkg):
            sname, pkg = futures_pkg[future]
            res = future.result()
            (resolved if res else missing).append(f'{sname} -> {pkg}')

    # Ensure consistent ordering since futures complete in arbitrary order
    resolved.sort()
    missing.sort()

    detail = (f'{len(resolved)}/{len(packages)} declared npx packages resolve '
              f'(registry control answered: {control})')
    if missing:
        detail += ('. Missing: ' + '; '.join(missing) +
                   '. A declared package that 404s cannot be started by npx.')
    return check(
        'mcp_npx_packages_resolve', 'wiring',
        OK if not missing else FAIL,
        {'declared': len(packages), 'resolved': len(resolved), 'missing': missing},
        detail, 'every npx package the config declares actually resolves')


# ------------------------------------------------------- live profile drift
#
# Everything above this line reads DECLARATIONS. This is the check that reads
# the thing a session actually uses.
#
# Measured 2026-10-10: the config declared seven python servers, all seven were
# on disk, all seven handshaked - and NONE of them was registered in the live
# minimax MCP profile. They existed, started, and were unreachable from every
# session. `mcp_config_servers_exist` reported OK the whole time, correctly: it
# was asked whether the files exist, and they did. It was never asked whether
# anything can reach them.
#
# A declared entry is not a running process. A running process is not a callable
# tool. This closes that gap.
LIVE_PROFILE_ENV = 'MINIMAX_MCP_PROFILE'
LIVE_PROFILE_DEFAULT = r"C:\Users\apviz\.minimax\mcp.json"


def _live_profile_servers() -> tuple:
    """Read (servers_by_path, error) from the live MCP profile.

    Returns the error rather than raising, because "the profile file could not
    be read" and "the profile is missing these servers" are different findings
    and must not collapse into one verdict.
    """
    path = os.environ.get(LIVE_PROFILE_ENV) or LIVE_PROFILE_DEFAULT
    try:
        raw = Path(path).read_text(encoding='utf-8-sig')
        cfg = json.loads(raw)
    except (OSError, json.JSONDecodeError) as exc:
        return {}, f'could not read the live MCP profile at {path}: {exc}'
    servers = cfg.get('mcpServers') if isinstance(cfg, dict) else None
    if not isinstance(servers, dict):
        return {}, f'{path} has no mcpServers object'
    # Index by the SCRIPT each entry launches, not by entry name, because the
    # names differ: the config calls it `git`, the profile calls it `git-tools`.
    #
    # `enabled: false` is skipped on purpose. A disabled entry sits in the file
    # looking registered, and indexing it made the check report ok for a server
    # that cannot start. Present in the file is not live in the profile.
    by_path: Dict[str, str] = {}
    for name, spec in servers.items():
        if not isinstance(spec, dict):
            continue
        if spec.get('enabled', True) is False:
            continue
        for arg in (spec.get('args') or []):
            text = str(arg)
            if text.lower().endswith('.py'):
                by_path[os.path.normcase(text)] = name
    return by_path, None


def _live_profile_check(spec: dict) -> Dict[str, Any]:
    """Are the servers the config says are live, actually live and enabled?"""
    declared = {}
    for sname, sspec in (spec.get('servers') or {}).items():
        if not isinstance(sspec, dict):
            continue
        for arg in (sspec.get('args') or []):
            text = str(arg)
            if text.lower().endswith('.py'):
                declared[os.path.normcase(text)] = sname

    by_path, err = _live_profile_servers()
    if err:
        return check('mcp_live_profile_registered', 'wiring', NOT_RUN, None,
                     err + ' - nothing was falsified, so this is NOT_RUN and '
                            'not FAIL', 'the servers the config says are live are live')

    # The config declares its own deployment set. That is what makes this a
    # check rather than a report: it states an expectation, and reality either
    # matches it or does not.
    expected = ((spec.get('liveProfileRegistration') or {}).get('registered') or {})
    expected_names = {k for k in expected if k != 'total'}

    # Compare by SCRIPT PATH, from the config's own declaration into the live
    # profile. The first version of this check derived the expectation from the
    # live profile, which made it circular and unfalsifiable: with prime-bridge
    # REMOVED from the profile it still reported ok, because the set of
    # "expected" names was built by looking them up in the very file that was
    # missing them. The expectation must come from the DECLARATION; the profile
    # is only ever the thing under test.
    expected_paths = {p for p, n in declared.items() if n in expected_names}
    missing_expected = sorted(expected_paths - set(by_path))

    live = sorted({by_path[p] for p in declared if p in by_path})
    unregistered = sorted({declared[p] for p in declared if p not in by_path})

    verdict = OK if not missing_expected else FAIL
    detail = (f'{len(live)} of {len(declared)} declared .py servers are registered '
              f'and enabled in the live profile: {", ".join(live) or "none"}')
    if unregistered:
        detail += (f'. Declared but deliberately not registered: '
                   f'{", ".join(unregistered)} - their tools are already served '
                   f'by the live sentinel-hub, and registering them would put '
                   f'duplicate tool names in front of every session')
    if missing_expected:
        detail += (f'. NOT LIVE: '
                   f'{", ".join(sorted(declared[p] for p in missing_expected))}'
                   f' - registered by explicit decision, so its absence or its '
                   f'disabled state is drift, not intent, and those tools are '
                   f'not callable from any session')
    return check(
        'mcp_live_profile_registered', 'wiring', verdict,
        {'declared_python': len(declared), 'registered': live,
         'not_registered_by_design': unregistered,
         'expected_live_count': len(expected_paths),
         'missing_from_live_profile': sorted(declared[p] for p in missing_expected)},
        detail,
        'every server the config records as live is actually registered and '
        'enabled in the live MCP profile')


# ---------------------------------------------------------------- coverage
#
# A declared server that is not on disk is not automatically a missing
# capability. Four of the five declared .py servers describe work the live
# `sentinel-hub` performs under different tool names: EU SENT / DOR / search /
# anti-mimicry ARE the state fields `sentinel_get_state` reads, and R-9 / R-10
# trigger monitoring IS `sentinel_check_r_triggers`. The fifth, filesystem and
# workspace access, belongs to the registered filesystem server.
#
# So the mismatch has two very different causes and the monitor must say which:
#   * the capability was never built  -> a real gap
#   * the capability moved into another registered server and the blueprint
#     was never updated               -> stale documentation
# Reporting both as an undifferentiated FAIL is honest but not actionable, and
# it hides the fact that the BLUEPRINT - not the implementation - is what is
# out of date. The verdict below stays FAIL either way, because an agent that
# reads OPTIMUS_MCP_CONFIG.json and launches `prime-bridge` really does fail.
# What changes is that the diagnosis now names the cause.
#
# The table is a CLAIM and it is falsifiable on every run: each named server
# must be registered and enabled in the LIVE profile, and each named tool must
# actually exist in that server's real tool list. If either stops holding, the
# coverage collapses to uncovered and the entry is reported as a genuine gap.
# A table that cannot fail is not a mapping, it is a waiver.
CAPABILITY_COVERAGE = {
    'sentinel-state': (
        'sentinel-hub',
        ('sentinel_get_state', 'sentinel_set_state', 'sentinel_check_context'),
        'EU SENT / DOR / search / anti-mimicry are the state fields these read and write'),
    'rule-triggers': (
        'sentinel-hub', ('sentinel_check_r_triggers',),
        'R-9 / R-10 trigger monitoring is this tool\'s entire subject'),
    'context-pressure': (
        'sentinel-hub', ('sentinel_check_context',),
        'context pressure is what this tool measures'),
    'learning-loop': (
        'sentinel-hub',
        ('sentinel_extract_patterns', 'sentinel_log_event', 'sentinel_create_handoff'),
        'the derive -> record -> hand-off loop the description names'),
    'prime-bridge': (
        'mcp-server-filesystem', (),
        'filesystem and workspace access, provided by the registered filesystem server'),
}

LIVE_PROFILE = Path(r"C:\Users\apviz\.minimax\mcp.json")


_HANDSHAKE = WORKSPACE / '13_COMMAND_CENTER' / 'api' / 'mcp_handshake.py'


def _hub_serves() -> tuple:
    """Ask the hub what it actually serves, by running a real MCP handshake.

    Returns (served_tool_names, detail). An empty set means the hub is NOT
    serving, and `detail` says why.

    This is the same script the Command Center's MCP wiring button runs, so
    there is one handshake implementation rather than two that can disagree.

    Reading tool names out of the hub's source with a regex is not a substitute
    for this, and the difference is not academic: until the port to mcp 2.x the
    hub could not execute a single line, yet the regex found all 26 tool names
    and the monitor reported five capabilities as "verified live". A name in a
    source file is not a tool being served. Anything less than a real handshake
    must not be reported as liveness.
    """
    import json as _json
    import subprocess as _sp

    if not _HANDSHAKE.is_file():
        return set(), f'handshake script not found at {_HANDSHAKE.name}'
    try:
        proc = _sp.run([sys.executable, str(_HANDSHAKE)],
                       capture_output=True, text=True, timeout=90)
    except (OSError, ValueError, _sp.SubprocessError) as exc:
        return set(), f'handshake could not run: {type(exc).__name__}: {exc}'

    verdict = next((ln for ln in proc.stdout.splitlines()
                    if ln.startswith('RESULT:')), None)
    if not verdict:
        tail = (proc.stderr or '').strip().splitlines()
        return set(), (f'no verdict (exit {proc.returncode})'
                       + (f': {tail[-1][:160]}' if tail else ''))
    try:
        payload = _json.loads(verdict.split('RESULT:', 1)[1].strip())
    except ValueError:
        return set(), 'handshake verdict was not valid JSON'
    served = set(payload.get('served') or ())
    if not served:
        return set(), f'handshake served 0 tools (exit {proc.returncode})'
    return served, f'handshake served {len(served)} tools'


def _coverage_evidence() -> dict:
    """Re-verify the coverage table against reality. Returns {name: (ok, where)}.

    Deliberately reads the LIVE profile and a LIVE handshake rather than
    trusting the table: the table says where a capability claims to live, and
    those two things say whether it still does.
    """
    registered: set = set()
    if LIVE_PROFILE.is_file():
        try:
            prof = json.loads(LIVE_PROFILE.read_text(encoding='utf-8'))
            servers = prof.get('mcpServers') or {}
            registered = {n for n, s in servers.items()
                          if isinstance(s, dict) and s.get('enabled', True)}
        except (json.JSONDecodeError, OSError, AttributeError, TypeError):
            registered = set()

    served, hub_detail = _hub_serves()

    evidence: dict = {}
    for name, (server, tools, _why) in CAPABILITY_COVERAGE.items():
        if server not in registered:
            evidence[name] = (False, f'{server} is not registered and enabled '
                                     f'in the live profile')
        elif server == 'sentinel-hub' and not served:
            evidence[name] = (False, f'sentinel-hub is registered but a live '
                                     f'handshake served nothing: {hub_detail}')
        elif tools and not set(tools).issubset(served):
            missing = sorted(set(tools) - served)
            evidence[name] = (False, f'{server} is registered but a live handshake '
                                     f'did not serve {missing}')
        else:
            evidence[name] = (True, f'{server}' + (f' ({len(tools)} tools)'
                                                  if tools else ''))
    return evidence


def wiring_checks() -> List[Dict[str, Any]]:
    out = []
    hub = WORKSPACE / '07_BACKBONE' / 'mcp' / 'sentinel_hub_server.py'
    cfg = WORKSPACE / '07_BACKBONE' / 'mcp' / 'OPTIMUS_MCP_CONFIG.json'
    skills_dir = WORKSPACE / '07_BACKBONE' / 'skills'

    declared = []
    if hub.exists():
        try:
            import re
            declared = re.findall(r'name="(sentinel_[a-z0-9_]+)"',
                                  hub.read_text(encoding='utf-8'))
        except OSError as exc:
            out.append(check('mcp_hub_read', 'wiring', NOT_RUN, None, str(exc)))
    out.append(check(
        'mcp_tools_declared', 'wiring', OK if declared else FAIL, len(declared),
        f'{len(declared)} SENTINEL tools registered in the hub', '> 0'))

    # DECLARED is not WIRED. A name in the source proves only that the source
    # contains the name. Wiring means a client spawned the server, completed
    # the MCP initialize handshake, and got tools back over the wire.
    #
    # This check used to be a hardcoded NOT_RUN with the comment "no runtime
    # handshake has been performed". That was honest, but it was also
    # unmoveable: nothing in the system could ever change it, so the tools were
    # unverifiable forever. It now reads the measured record written by
    # mcp_handshake.py, and keeps NOT_RUN for the case that actually applies -
    # no handshake attempted yet, or one that did not complete.
    record = LOGS / 'mcp_handshake.json'
    if not record.exists():
        out.append(check(
            'mcp_tools_wired', 'wiring', NOT_RUN, None,
            'no runtime handshake has been performed; run 08_SELF_IMPROVEMENT/'
            'mcp_handshake.py. The tools are DECLARED, not WIRED. A declared tool '
            'must not be presented as a working one.', '0 wired'))
    else:
        try:
            rec = json.loads(record.read_text(encoding='utf-8'))
        except (json.JSONDecodeError, OSError) as exc:
            out.append(check(
                'mcp_tools_wired', 'wiring', FAIL, None,
                f'handshake record unreadable: {exc}',
                'a readable handshake record'))
        else:
            returned = int(rec.get('tools_returned_by_server') or 0)
            probe = rec.get('probe_result') or {}
            probe_ok = bool(probe.get('ok')) and bool(probe.get('arguments_arrived'))
            hs_ok = rec.get('status') == 'OK' and returned > 0 and probe_ok
            record_mtime = record.stat().st_mtime
            age = (time.time() - record_mtime)

            # A verdict is only about the thing it measured. This record was
            # written 2026-10-05 and the server it describes was edited on
            # 2026-10-09, so its OK described a file that no longer exists in
            # that form. Reading the contents alone cannot notice that: the
            # record still says status=OK, 26 tools, probe ok. Age was
            # measured and then only printed, while STALE - the status this
            # very file defines for "measured, but older than its bound" - went
            # unused here. Same defect class as the source-regex coverage
            # above, reached by staleness instead of by text.
            hub_src = WORKSPACE / '07_BACKBONE' / 'mcp' / 'sentinel_hub_server.py'
            try:
                hub_mtime = hub_src.stat().st_mtime if hub_src.is_file() else 0.0
            except OSError:
                hub_mtime = 0.0
            superseded = hub_mtime > record_mtime
            expired = age > HANDSHAKE_MAX_AGE
            stale_reason = []
            if superseded:
                stale_reason.append(
                    'the server was edited after this record was written, so the '
                    'record describes a different file')
            if expired:
                stale_reason.append(
                    f'it is {age / 3600:.1f}h old (bound {HANDSHAKE_MAX_AGE}s)')
            # A record whose probe did not positively verify is FAIL, not
            # NOT_RUN. That is deliberate and it is load-bearing: the monitor
            # reads this file from disk and CANNOT distinguish an honest
            # probe timeout from a record someone edited by hand. Both arrive
            # as status=OK, N tools, probe not ok. Reporting NOT_RUN for that
            # shape would let a forged record read as a benign "could not
            # verify" - a more believable lie than a loud FAIL, and it would
            # defeat the suite's "OK must be unearnable" guard, which mutates
            # exactly these two shapes and demands FAIL.
            #
            # So the conservative reading wins, and the load-induced probe
            # timeout is a real transient of the PROBE, not a verdict change.
            # Fix it at the producer (make the probe tolerate load); never by
            # relaxing what the monitor is willing to believe.
            #
            # A fresh record still gets FAIL when the probe did not verify, so
            # that guard is untouched: staleness is only ever consulted for a
            # record too old - or too old relative to the code - to speak about
            # the server as it stands.
            if stale_reason:
                hs_status = STALE
            else:
                hs_status = OK if hs_ok else FAIL
            out.append(check(
                'mcp_tools_wired', 'wiring', hs_status,
                {'tools_over_the_wire': returned,
                 'probe_tool': probe.get('tool'),
                 'probe_ok': probe_ok,
                 'handshake_status': rec.get('status'),
                 'record_age_seconds': round(age, 1),
                 'record_superseded_by_server_edit': superseded},
                f'{returned} tools returned by the server over stdio; probe '
                f'"{probe.get("tool")}" ok={probe_ok}, arguments arrived='
                f'{probe.get("arguments_arrived")}. Measured {age:.0f}s ago by '
                f'mcp_handshake.py, not asserted here.'
                + (f' STALE, because {"; and ".join(stale_reason)}. Re-run '
                   f'08_SELF_IMPROVEMENT\\mcp_handshake.py to re-measure.'
                   if stale_reason else ''),
                'a completed handshake returning > 0 tools, with a probe whose '
                'arguments provably reached the handler'))

    cfg_ok, cfg_detail = False, 'config missing'
    if cfg.exists():
        try:
            json.loads(cfg.read_text(encoding='utf-8'))
            cfg_ok, cfg_detail = True, 'OPTIMUS_MCP_CONFIG.json is valid JSON'
        except json.JSONDecodeError as exc:
            cfg_detail = f'invalid JSON: {exc}'
    out.append(check('mcp_config', 'wiring', OK if cfg_ok else FAIL, None, cfg_detail))

    # A config that parses is not a config that can be started. mcp_config was
    # satisfied by valid JSON alone, so it passed while 5 of the 9 declared
    # servers pointed at .py files that did not exist anywhere in the workspace.
    # An agent that trusted this config would launch prime-bridge,
    # sentinel-state, rule-triggers, learning-loop or context-pressure and get
    # a failure - the promise was in the file, the server was not.
    #
    # HISTORICAL, kept as written: that was true when this check was added. It
    # is no longer true, and the numbers below are the ones this run would
    # measure, not the ones it measured. Measured 2026-10-10: 7 declared .py
    # servers, all 7 present, because the five were BUILT at their declared
    # paths and web-tools/git were repointed from phantom npx packages to local
    # servers. Kept rather than rewritten, because a comment that is silently
    # edited each time the numbers move stops recording when the class of bug
    # was first seen - which is the only reason it is worth having.
    #
    # The entries were never pruned: whether to implement or prune is an
    # operator decision, not a monitor's. What the monitor must not do is let
    # the mismatch stay invisible.
    if cfg_ok:
        try:
            spec = json.loads(cfg.read_text(encoding='utf-8'))
            referenced, absent = 0, []
            npx_specs = []
            for sname, sspec in (spec.get('servers') or {}).items():
                for arg in sspec.get('args', []):
                    if not str(arg).endswith('.py'):
                        npx_specs.append((sname, sspec))
                        continue  # npm package: resolved by the companion check below
                    referenced += 1
                    if not Path(arg).exists():
                        absent.append(f'{sname} -> {arg}')
            # WHY it is absent matters, so it is measured rather than asserted.
            # Each absent entry is matched against the coverage table, which is
            # itself re-verified on this run against the live profile and a real
            # MCP handshake with the hub - not against names read out of its
            # source file, which stayed constant while the hub could not start.
            cover = _coverage_evidence()
            covered, uncovered = [], []
            for entry in absent:
                sname = entry.split(' -> ')[0]
                ok, where = cover.get(sname, (False, 'no coverage mapping is declared'))
                (covered if ok else uncovered).append({'declared_as': sname,
                                                       'live_under': where})
            out.append(check(
                'mcp_config_servers_exist', 'wiring',
                OK if not absent else FAIL,
                {'referenced_python_servers': referenced, 'missing': len(absent),
                 'missing_entries': absent,
                 'capability_covered_elsewhere': covered,
                 'capability_uncovered': uncovered},
                f'{referenced} .py servers referenced by the config, '
                f'{len(absent)} not on disk'
                + (f'. {len(covered)} of those capabilities are verified live '
                   f'under another registered server '
                   f'({", ".join(c["declared_as"] for c in covered)}); '
                   f'{len(uncovered)} have no live equivalent'
                   if absent else '. All referenced servers exist.')
                + ('. A declared server that cannot start is a false promise, so '
                   'this stays FAIL: the blueprint is stale, but an agent that '
                   'reads it and launches those names still fails. Rewriting or '
                   'pruning the config is an operator decision.'
                   if absent else ''),
                'every referenced .py server exists on disk'))

            # The npx entries were skipped on an assumption written as a comment:
            # "npm package, resolved by npx at launch". That assumption is the
            # whole claim, and it was never checked. It is also false: two of the
            # four packages named in this config return a hard 404 from the npm
            # registry, so `npx -y <pkg>` fails exactly the way the missing .py
            # files do. The monitor reported 5 dead servers while the config
            # actually carried 7.
            #
            # A comment is not a check. This resolves each package and reports
            # which side of the registry answered. If the registry itself is
            # unreachable the verdict is NOT_RUN - never FAIL, because an offline
            # machine has falsified nothing - and never OK.
            out.append(_npx_resolution_check(npx_specs))
            out.append(_live_profile_check(spec))
        except (json.JSONDecodeError, OSError, TypeError) as exc:
            out.append(check(
                'mcp_config_servers_exist', 'wiring', FAIL, None,
                f'could not inspect the config: {exc}',
                'every referenced .py server exists on disk'))

    skills = sorted(skills_dir.glob('*.md')) if skills_dir.exists() else []
    out.append(check(
        'skills_present', 'wiring', OK if skills else FAIL,
        [s.name for s in skills], f'{len(skills)} skill files', '> 0'))
    return out


# ----------------------------------------------------------------- logs

def log_checks() -> List[Dict[str, Any]]:
    out = []
    artifacts = {
        'bimodal_state': LOGS / 'bimodal_state.json',
        'bimodal_log': LOGS / 'bimodal_workflow.log',
        'orchestrator_state': LOGS / 'orchestrator_state.json',
        'performance_metrics': LOGS / 'performance_metrics.json',
        'self_modifications': LOGS / 'self_modifications.log',
        'state_transitions': LOGS / 'state_transitions.log',
        'self_improvement': LOGS / 'self_improvement.log',
    }
    parse_errors = []
    for name, path in artifacts.items():
        a = age_seconds(path)
        if a is None:
            out.append(check(f'log_{name}', 'logs', NOT_RUN, None,
                             f'{path.name} does not exist', 'file must exist'))
            continue
        status = OK if a < STALE_SECONDS * 10 else STALE
        out.append(check(f'log_{name}', 'logs', status, round(a, 1),
                         f'{path.name} last written {a:.0f}s ago',
                         f'< {STALE_SECONDS * 10}s'))
        if path.suffix == '.json' and a < MAX_STATE_AGE:
            try:
                json.loads(path.read_text(encoding='utf-8'))
            except json.JSONDecodeError as exc:
                parse_errors.append(f'{path.name}: {exc}')
    out.append(check(
        'logs_parse', 'logs', OK if not parse_errors else FAIL, parse_errors,
        'every state JSON must parse; a corrupt state file is a silent failure',
        'no parse errors'))

    # A scrape artefact is "empty" only if it carries no result. Deciding that
    # from file SIZE was the original bug: example.com is a genuinely tiny page,
    # so eight successful scrapes of it were 290 bytes each and were reported as
    # eight empty artefacts. That is a false positive pointed at good data, and
    # the check's own remedy (deletion) would have destroyed evidence.
    #
    # The question is about CONTENT, so ask about content: does it parse, and
    # does it carry something a successful scrape always produces (a title plus
    # at least one extracted heading or link)?
    scraped = LOGS / 'scraped'
    empty, unreadable, expected_empty, inspected = [], [], [], 0
    if scraped.exists():
        for f in sorted(scraped.glob('*.json')):
            inspected += 1
            try:
                data = json.loads(f.read_text(encoding='utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError, OSError) as exc:
                # Unreadable is not the same claim as empty; tracked separately
                # so a corrupt file can never be quietly counted as "fine".
                unreadable.append(f'{f.name}: {type(exc).__name__}')
                continue
            extracted = (data or {}).get('extracted') or {}
            has_title = bool(str(extracted.get('title') or '').strip())
            has_items = bool(extracted.get('headings') or extracted.get('links'))
            if has_title and has_items:
                continue
            # "A successful scrape always produces a title plus at least one
            # heading or link" is this check's premise, and "always" is exactly
            # the word that breaks it. `about:blank` has no title, no headings
            # and no links by definition, so an artefact recording that is a
            # SUCCESSFUL scrape of a page that has no content - not a silent
            # failure. Demanding content from it made the check fire on correct
            # data, which is the same class of error as the size heuristic it
            # was written to replace.
            #
            # Navigation-only targets are counted apart rather than excused:
            # they are still listed, so nothing is hidden. They just stop being
            # classified as failures, which they never were.
            url = str((data or {}).get('url') or '').strip()
            scheme = url.split(':', 1)[0].lower() if ':' in url else ''
            if not url or scheme in ('about', 'data', 'javascript', 'chrome', 'blob'):
                expected_empty.append(f.name)
            else:
                empty.append(f.name)
    out.append(check(
        'logs_empty_artifacts', 'logs',
        OK if not empty and not unreadable else FAIL,
        {'inspected': inspected, 'empty': len(empty), 'unreadable': len(unreadable),
         'empty_files': empty, 'unreadable_files': unreadable,
         'expected_empty_navigation_targets': expected_empty},
        f'{inspected} scrape artefacts inspected by content: {len(empty)} of a '
        f'content-bearing URL carry no result, {len(unreadable)} unreadable, '
        f'{len(expected_empty)} are navigation-only targets with no content by '
        f'definition. Size is never the criterion - a successful scrape of a '
        f'small page is small. Reported, not deleted: deleting is an explicit '
        f'operator decision.',
        '0 empty and 0 unreadable artefacts'))
    return out


# ---------------------------------------------------------- dependencies

def dependency_checks() -> List[Dict[str, Any]]:
    """Measured capability, so a degraded path can never look healthy."""
    out = []
    required = {
        'playwright': 'browser automation',
        'PIL': 'image processing',
        'pypdf': 'PDF processing',
        'docx': 'DOCX processing',
        'openpyxl': 'XLSX processing',
        'pptx': 'PPTX processing',
        'cv2': 'video processing (OpenCV)',
        'pytesseract': 'OCR binding',
        'faster_whisper': 'audio transcription',
    }
    import importlib
    for mod, capability in required.items():
        try:
            importlib.import_module(mod)
            status, note = OK, f'{capability}: importable'
        except Exception:
            status, note = FAIL, f'{capability}: {mod} not importable - UNVERIFIED'
        out.append(check(f'dep_{mod}', 'dependencies', status, None, note))

    # Importable is not the same as compatible.
    #
    # faster-whisper 1.2.1 (the latest release) calls
    #     av.open(path, mode="r", metadata_errors="ignore")
    # and declares only `av>=11`, with no upper bound. PyAV later removed that
    # keyword, so the resolver installs av 19 and every `import faster_whisper`
    # succeeds while the first real file fails with
    #     open() got an unexpected keyword argument 'metadata_errors'
    #
    # Both of the loop's checks above would have reported green throughout that
    # entire breakage: the modules import, and neither of them is asked to open
    # anything. An import test asserts that a package is present; only a
    # capability call asserts that it works. This one calls the exact API the
    # audio path calls, so the pin in requirements_verified.txt is guarded
    # rather than merely documented.
    av_note = 'av/faster-whisper compatibility NOT_TESTED'
    av_status = OK
    av_value = None
    try:
        import av
        import tempfile
        av_version = av.__version__
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tf:
            wav_path = tf.name
            tf.write(b'RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00'
                     b'\x44\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00')
        container = av.open(wav_path, mode='r', metadata_errors='ignore')
        stream_count = len(container.streams)
        container.close()
        av_value = {'av': av_version, 'streams': stream_count}
        av_note = (f'av {av_version} accepts metadata_errors - the exact call '
                   f'faster-whisper makes opens a real container ({stream_count} streams)')
    except TypeError as e:
        av_status = FAIL
        av_note = (f'av/faster-whisper INCOMPATIBLE: {e}. faster-whisper pins '
                   f'av>=11 with no upper bound; reinstall av>=15.1.0,<16')
    except ImportError as e:
        av_status = FAIL
        av_note = f'av/faster-whisper compatibility UNVERIFIED: {e}'
    except Exception as e:
        av_status = FAIL
        av_note = f'av probe failed: {type(e).__name__}: {e}'
    out.append(check(
        'dep_av_faster_whisper_compat', 'dependencies', av_status, av_value,
        av_note,
        'the audio path opens a real container, not just an import'))

    # An external binary is a different failure mode from a missing module.
    #
    # Resolution must not depend on PATH alone. tesseract is installed and
    # working, and the directory IS in the user PATH in the registry, but a
    # process launched by an agent runtime inherits a PATH captured earlier, so
    # shutil.which returned None in a fresh shell while the engine ran fine
    # when invoked directly. A check that reports "not on PATH" for a working
    # binary is measuring the launcher, not the capability. tool_resolver
    # tries an explicit override, then the documented install location, then
    # PATH - and reports which one answered, so the verdict is auditable.
    import shutil
    import tool_resolver
    for binary, capability in (('tesseract', 'OCR engine'),
                               ('docker', 'container runtime'),
                               ('git', 'version control')):
        if binary in tool_resolver.KNOWN_LOCATIONS:
            info = tool_resolver.resolve(binary)
            found, via = info['path'], info['found_via']
            detail = (f'{capability} ({binary}) at {found} '
                      f'[resolved via {via}, not assumed from PATH]'
                      if found else
                      f'{capability} ({binary}): not found. Tried: '
                      f'{"; ".join(info["searched"])}')
            value = {'path': found, 'found_via': via}
        else:
            found = shutil.which(binary)
            via = 'PATH'
            detail = (f'{capability} ({binary}) at {found}' if found
                      else f'{capability} ({binary}): not on PATH')
            value = found
        out.append(check(
            f'bin_{binary}', 'dependencies', OK if found else FAIL, value,
            detail,
            'a working binary, located rather than assumed'))
    return out


# --------------------------------------------------------- program matrix

def program_checks() -> List[Dict[str, Any]]:
    out = []
    matrix = PROGRAM / 'IDEA_TO_SCRIPT_MATRIX.json'
    if not matrix.exists():
        out.append(check('program_matrix', 'program', NOT_RUN, None,
                         f'{matrix.name} not generated yet',
                         'generated by build_program_matrix.py'))
        return out
    try:
        rows = json.loads(matrix.read_text(encoding='utf-8'))
    except json.JSONDecodeError as exc:
        out.append(check('program_matrix', 'program', FAIL, None, str(exc)))
        return out

    counts = {}
    for r in rows:
        counts[r.get('status', 'UNKNOWN')] = counts.get(r.get('status', 'UNKNOWN'), 0) + 1
    out.append(check(
        'program_matrix', 'program', OK, {'rows': len(rows), 'by_status': counts},
        'concept -> file -> tool -> test -> panel correlation', 'file must parse'))

    stuck = [r for r in rows if r.get('status') == 'DESIGNED']
    unowned = [r['concept'] for r in stuck if not r.get('owner')]
    out.append(check(
        'program_no_unowned_design', 'program', OK if not unowned else FAIL, unowned,
        'a concept left in DESIGNED must still have an owner and a next action',
        'no unowned DESIGNED rows'))
    return out


# ------------------------------------------------------------- dashboard

def dashboard_checks() -> List[Dict[str, Any]]:
    out = []
    for cid, path in (
        ('cc_index', CC / 'index.html'),
        ('cc_server', CC / 'api' / 'server.ps1'),
        ('cc_collector', CC / 'api' / 'collect-sentinel.ps1'),
        ('cc_state', CC / 'api' / 'sentinel-state.json'),
    ):
        a = age_seconds(path)
        out.append(check(
            cid, 'dashboard',
            OK if path.exists() else NOT_RUN,
            {'bytes': path.stat().st_size} if path.exists() else 0,
            f'{path.name}' + (f' age={a:.0f}s' if a is not None else ' missing'),
            'Command Center part present'))
    return out


def _ps_structural_brace_deltas(text: str) -> List[int]:
    """Per-line `{` minus `}` across `text`, counting only real structure.

    Counting raw characters is wrong, and it was wrong here. A `{` inside a
    here-string or a double-quoted string shifted the running depth, so every
    assignment after it was treated as nested when it was not - and vice versa.
    The two PowerShell checks below shared that helper.

    The VERDICT usually survived, because a real case collision is rare and the
    depth only has to be wrong by one assignment. But the DIAGNOSIS did not: a
    collision check that blames the wrong file is as useless to the person
    reading it as one that finds nothing. Found 2026-10-10 by reviewer.

    Handles what actually appears in these scripts: `<# ... #>` block comments,
    `#` line comments, " and ' strings, and @"/@' here-strings that are opened
    at end of line and closed by "@/'@ at the start of a later line.
    """
    deltas: List[int] = []
    in_block_comment = False
    here_terminator: Optional[str] = None
    # `quote` lives OUTSIDE the loop on purpose. PowerShell double-quoted
    # strings may span lines, and a backtick at end of line continues the
    # string onto the next one. Initialised per line - which is what it did
    # first - a multi-line string lost its state at every newline, so the
    # scanner read the continuation as code. Found by verifier 2026-10-10:
    #
    #     $x = "line1 { line2 " line3      PowerShell: depth 0
    #     (a collision after it is REAL)    scanner:    depth 1, and MISSES it
    #
    # The naive counter missed this one too, so it was a shared blind spot
    # rather than a regression - which is exactly why it survived two rounds
    # of review. Latent: no real .ps1 currently uses a multi-line quoted string.
    quote: Optional[str] = None

    for line in text.splitlines():
        if here_terminator is not None:
            # Inside a here-string the whole line is literal until the opener's
            # terminator appears at the start of a line.
            deltas.append(0)
            if line.lstrip().startswith(here_terminator):
                here_terminator = None
            continue

        out_chars: List[str] = []
        i, n = 0, len(line)
        while i < n:
            if in_block_comment:
                idx = line.find('#>', i)
                if idx == -1:
                    i = n
                else:
                    in_block_comment = False
                    i = idx + 2
                continue
            ch = line[i]
            if quote is not None:
                # PowerShell escaping, both spellings, found by verifier
                # 2026-10-10. Getting these wrong is not cosmetic: a missed
                # brace means a missed depth change, which means a missed
                # $Path/$path collision - the exact class of silent defect
                # this function exists to catch, so a regression here is worse
                # than the naive counting it replaced.
                #
                #   "..."  escapes with a BACKTICK:  `"   is a literal quote.
                #   '...'  escapes by DOUBLING:    ''   is a literal quote.
                #
                # sentinel-hub.ps1:586 contains  "`  inside a double-quoted
                # regex. Treating that as a string terminator closed the string
                # early and the following `"` opened a new one, so a real brace
                # after it was counted as structure.
                if quote == '"' and ch == '`':
                    i += 2
                    continue
                if ch == quote:
                    if quote == "'" and i + 1 < n and line[i + 1] == "'":
                        i += 2
                        continue
                    quote = None
                i += 1
                continue
            if ch == '<' and line.startswith('<#', i):
                in_block_comment = True
                i += 2
                continue
            if ch in ('"', "'"):
                quote = ch
                i += 1
                continue
            # Here-string opener: @" or @' with nothing but whitespace after it.
            # The terminator is the opener's quote FOLLOWED BY '@ - i.e. "@ or
            # '@. It was briefly built as quote+quote, which can never match
            # the closing line, so the scanner stayed "inside" the here-string
            # for the rest of the file and reported depth 0 for every
            # subsequent line - a detector that finds nothing, which is the
            # failure mode this function exists to remove.
            if (ch == '@' and i + 1 < n and line[i + 1] in ('"', "'")
                    and not line[i + 2:].strip()):
                here_terminator = line[i + 1] + '@'
                break
            out_chars.append(ch)
            i += 1

        if in_block_comment and '#>' not in line:
            # Block comment opened and not closed on this line.
            pass
        cleaned = ''.join(out_chars)
        # `#` starts a comment only outside quotes, which the scan guarantees.
        hash_at = cleaned.find('#')
        if hash_at != -1:
            cleaned = cleaned[:hash_at]
        deltas.append(cleaned.count('{') - cleaned.count('}'))

    return deltas


def powershell_checks() -> List[Dict[str, Any]]:
    """Structural checks on the PowerShell layer.

    These exist because of a real, silent, high-cost defect found on
    2026-10-04. collect-sentinel.ps1 declared a path as `$STATE` and later
    assigned the state OBJECT to `$state`. PowerShell variable names are
    case-INSENSITIVE, so those were one variable: the second assignment
    overwrote the path, and `Set-Content -Path $STATE` wrote a file literally
    named "System.Collections.Specialized.OrderedDictionary" in the workspace
    root. The script still exited 0, still appended its history file, and still
    printed a healthy summary line. The Command Center served its honest
    fallback for the whole build with nothing anywhere reporting an error.

    The two checks below are the fingerprint of that failure mode, generalised:
    a case collision at script scope, and a file whose name is a .NET type name.
    """
    out: List[Dict[str, Any]] = []
    scripts = sorted(WORKSPACE.rglob('*.ps1'))
    scripts = [p for p in scripts if 'backups' not in p.parts and 'corpus_freeze' not in p.parts]
    out.append(check(
        'ps_scripts_found', 'powershell',
        OK if scripts else NOT_RUN, len(scripts),
        f'{len(scripts)} PowerShell script(s) under the workspace'))

    # --- case collisions at script scope ---------------------------------
    # Function-local variables that share a name in different functions are
    # legal and are ignored: only depth-0 assignments share one storage slot.
    collisions: List[str] = []
    for path in scripts:
        try:
            # utf-8-sig, not utf-8: Windows PowerShell 5.1 writes a BOM with
            # -Encoding UTF8, so several .ps1 here start with U+FEFF. Read as
            # plain utf-8 the BOM survives as a character, the first line stops
            # matching ^\s*\$..., and the collision check silently sees nothing.
            # A detector that goes blind on a BOM is worse than no detector,
            # because it reports OK.
            text = path.read_text(encoding='utf-8-sig', errors='replace')
        except OSError:
            continue
        depth = 0
        assigned: Dict[str, str] = {}
        brace_deltas = _ps_structural_brace_deltas(text)
        for line, delta in zip(text.splitlines(), brace_deltas):
            m = re.match(r'^\s*\$([A-Za-z_][A-Za-z0-9_]*)\s*=', line)
            if m and depth <= 0:
                name = m.group(1)
                prior = assigned.get(name.lower())
                if prior and prior != name:
                    collisions.append(
                        f'{path.name}: ${prior} and ${name} are one variable')
                assigned[name.lower()] = name
            depth += delta
    out.append(check(
        'ps_variable_case_collisions', 'powershell',
        FAIL if collisions else OK, len(collisions),
        '; '.join(collisions) if collisions else
        'no two script-scope variables in any .ps1 differ only by case',
        'PowerShell folds $Foo and $foo into one variable'))

    # --- script-scope variables shadowed inside a function ----------------
    # The collision check above only looks at depth 0, because two function-local
    # variables sharing a name in DIFFERENT functions is legal. But a function
    # local that shadows a SCRIPT variable is not legal in effect, even though it
    # is legal in form: inside that function the local wins, and if the code
    # meant to read the script variable it silently reads its own instead.
    #
    # This is not hypothetical. server.ps1's Search-Corpus assigned its Python
    # here-string to `$py` while the interpreter path was `$PY`; every corpus
    # search then executed the source text as a PowerShell command. The first
    # detector missed it precisely because the collision lived inside a function.
    shadowed: List[str] = []
    assign = re.compile(r'^\s*\$([A-Za-z_][A-Za-z0-9_]*)\s*=')
    for path in scripts:
        try:
            text = path.read_text(encoding='utf-8-sig', errors='replace')
        except OSError:
            continue
        script_vars: Dict[str, str] = {}
        local_vars: Dict[str, str] = {}
        depth = 0
        in_func = False
        func_name = ''
        brace_deltas = _ps_structural_brace_deltas(text)
        for line, delta in zip(text.splitlines(), brace_deltas):
            m = assign.match(line)
            if m:
                name = m.group(1)
                if depth <= 0:
                    script_vars[name.lower()] = name
                else:
                    if not in_func:
                        # entering the first function body
                        in_func, local_vars = True, {}
                    prior = local_vars.get(name.lower())
                    if prior and prior != name:
                        shadowed.append(f'{path.name}: {func_name} $' + prior +
                                        f' and ${name} are one variable')
                    elif name.lower() in script_vars and script_vars[name.lower()] != name:
                        shadowed.append(f'{path.name}: {func_name} ${name} shadows script ${script_vars[name.lower()]}')
                    local_vars[name.lower()] = name
            if re.match(r'^\s*function\s+[A-Za-z_][A-Za-z0-9_\-]*', line):
                fn = re.search(r'function\s+([A-Za-z_][A-Za-z0-9_\-]*)', line)
                func_name = fn.group(1) if fn else '?'
                in_func, local_vars = True, {}
            depth += delta
            if depth <= 0 and in_func:
                in_func, func_name, local_vars = False, '', {}
    out.append(check(
        'ps_shadowed_script_vars', 'powershell',
        FAIL if shadowed else OK, len(shadowed),
        '; '.join(shadowed) if shadowed else
        'no function-local variable shadows or collides with a script variable',
        'a local $py silently replaces a script $PY inside the function'))

    # --- stray files named after a .NET type -----------------------------
    # The signature of a path variable that was overwritten by an object and
    # then handed to a cmdlet that wanted a path.
    #
    # Scope matters, and getting it wrong is how a detector reports green while
    # the artifact it exists to catch is sitting on disk. Because the bogus
    # ToString() is a RELATIVE path, Set-Content resolves it against the CURRENT
    # WORKING DIRECTORY - so the same defect produced junk in SENTINEL_PRIME\,
    # in 13_COMMAND_CENTER\, and once in the projects\ root one level ABOVE the
    # workspace. A scan limited to WORKSPACE saw two of the three and called the
    # job done. The parent directory is therefore scanned too, and its presence
    # is reported rather than assumed.
    type_like = re.compile(
        r'^(System\.[A-Za-z.]+|Microsoft\.[A-Za-z.]+'
        r'|Collections\.[A-Za-z.]+|Hashtable|OrderedDictionary|Object\[\])$')
    strays: List[str] = []
    # Recursive inside the workspace.
    for p in WORKSPACE.rglob('*'):
        if p.is_file() and type_like.match(p.name):
            try:
                strays.append(f'{p.relative_to(WORKSPACE)} ({p.stat().st_size}B)')
            except (ValueError, OSError):
                strays.append(f'{p} (unstatable)')
    # NON-recursive above the workspace. The stray file landed directly in
    # projects\, so a top-level listing is sufficient to catch the observed
    # failure. A recursive walk up there would drag in the quarantine backup
    # tree and turn a 50 ms check into a multi-second one, which is how a
    # monitor gets switched off.
    parent = WORKSPACE.parent
    if parent and parent != WORKSPACE:
        try:
            for p in parent.iterdir():
                if p.is_file() and type_like.match(p.name):
                    strays.append(f'ABOVE WORKSPACE: {p.name} ({p.stat().st_size}B)')
        except OSError:
            pass
    out.append(check(
        'ps_stray_type_named_files', 'powershell',
        FAIL if strays else OK, len(strays),
        '; '.join(strays) if strays else
        ('no file is named after a .NET type inside SENTINEL_PRIME\\ or in its '
         'immediate parent (a path/object variable collision)'),
        'catches the collector writing state to its own ToString()'))

    return out


# ------------------------------------------------------------------ main

FAMILIES = [
    ('corpus', corpus_checks),
    ('workflow', workflow_checks),
    ('code', code_checks),
    ('wiring', wiring_checks),
    ('logs', log_checks),
    ('dependencies', dependency_checks),
    ('program', program_checks),
    ('dashboard', dashboard_checks),
    ('powershell', powershell_checks),
]


def collect() -> Dict[str, Any]:
    started = time.time()
    checks: List[Dict[str, Any]] = []
    for family, fn in FAMILIES:
        try:
            checks.extend(fn())
        except Exception as exc:
            checks.append(check(f'{family}_family', family, NOT_RUN, None,
                                f'{type(exc).__name__}: {exc}'))

    by_status: Dict[str, int] = {OK: 0, FAIL: 0, STALE: 0, NOT_RUN: 0}
    by_family: Dict[str, Dict[str, int]] = {}
    for c in checks:
        by_status[c['status']] = by_status.get(c['status'], 0) + 1
        f = by_family.setdefault(c['family'],
                                 {OK: 0, FAIL: 0, STALE: 0, NOT_RUN: 0})
        f[c['status']] = f.get(c['status'], 0) + 1

    report = {
        'generated_at': _now(),
        'duration_sec': round(time.time() - started, 3),
        'overall': 'FAIL' if by_status[FAIL] else ('DEGRADED' if by_status[NOT_RUN]
                                                   or by_status[STALE] else 'OK'),
        'counts': by_status,
        'total_checks': len(checks),
        'by_family': by_family,
        'checks': checks,
        'interpretation': (
            'OK means every check ran and passed. DEGRADED means at least one check '
            'could not run or is stale - the capability is UNVERIFIED, not working. '
            'FAIL means at least one measured value is out of bounds.'),
    }
    return report


def render(report: Dict[str, Any]) -> str:
    lines = ['=' * 78, 'SENTINEL SELF-MONITOR', f"generated {report['generated_at']}",
             f"overall: {report['overall']}   "
             f"OK={report['counts'][OK]} FAIL={report['counts'][FAIL]} "
             f"STALE={report['counts'][STALE]} NOT_RUN={report['counts'][NOT_RUN]}",
             '=' * 78]
    family = None
    for c in report['checks']:
        if c['family'] != family:
            family = c['family']
            lines.append('')
            lines.append(f'-- {family.upper()} ' + '-' * (66 - len(family)))
        mark = {OK: '  ok  ', FAIL: ' FAIL ', STALE: 'STALE ', NOT_RUN: 'NOTRUN'}[c['status']]
        lines.append(f"[{mark}] {c['id']:28s} {str(c['value'])[:34]:34s} {c['evidence'][:90]}")
    lines += ['', report['interpretation'], '=' * 78]
    return '\n'.join(lines)


def main():
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding='utf-8', errors='replace')
        except (AttributeError, ValueError):
            pass

    report = collect()
    if '--json' in sys.argv:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(render(report))

    # DEFECT 19 FIX (2026-10-04, found by the independent verifier)
    # health.json was only refreshed under `--write`. Nobody runs with that
    # flag routinely, so the file the dashboard reads aged silently: the
    # verifier found a copy 7 minutes old still carrying a STALE verdict that
    # a live run no longer produced, and had to reconcile two different answers
    # to the same question.
    #
    # A stale cache presented as current is the exact failure the "always show
    # data age" rule exists to prevent, and this module's own docstring says it
    # "produces one health.json" - not "produces it on request". So it is now
    # written on every run. `--write` is accepted and ignored for compatibility.
    HEALTH_FILE.parent.mkdir(parents=True, exist_ok=True)
    HEALTH_FILE.write_text(json.dumps(report, indent=2, ensure_ascii=False),
                           encoding='utf-8')
    if '--write' in sys.argv:
        print(f'\nwritten: {HEALTH_FILE}')
    return 0 if report['overall'] != 'FAIL' else 1


if __name__ == '__main__':
    raise SystemExit(main())
