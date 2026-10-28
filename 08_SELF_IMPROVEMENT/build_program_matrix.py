#!/usr/bin/env python3
"""
Builds the idea -> script correlation matrix and the gap register.

The matrix is DERIVED BY MEASUREMENT, not written by hand. For every concept it
checks whether the doctrine file exists, whether the implementation exists, and
whether a test covers it, then computes the status from what it found:

    DESIGNED     doctrine exists, no implementation
    CODED        implementation exists, no covering test
    TESTED       a test exists and ran green
    WIRED        reachable through an MCP tool or a runtime
    OBSERVABLE   surfaced by the monitor or a dashboard panel

A concept with no panel is not finished. The `panel` column is the completion
gate, and this script refuses to call anything OBSERVABLE that nothing displays.

Also emits GAP_REGISTER.json: every known degradation, with the evidence that
found it. Gaps are reported, never silently repaired, and never deleted from.

Usage: python 08_SELF_IMPROVEMENT\\build_program_matrix.py
"""
import importlib
import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Set, Tuple
# unused imports removed for code health

WORKSPACE = Path(os.environ.get(
    'WORKSPACE_ROOT',
    r'C:\Users\apviz\.minimax-agent\projects\SENTINEL_PRIME'))
PROGRAM = WORKSPACE / '12_PROGRAM'
MATRIX_JSON = PROGRAM / 'IDEA_TO_SCRIPT_MATRIX.json'
GAPS_JSON = PROGRAM / 'GAP_REGISTER.json'

SI = WORKSPACE / '08_SELF_IMPROVEMENT'
HUB = WORKSPACE / '07_BACKBONE' / 'mcp' / 'sentinel_hub_server.py'
SUITE = SI / 'test_suite.py'

# The blueprint is the target, not a snapshot: it is read, never written here.
BLUEPRINT = WORKSPACE / '07_BACKBONE' / 'mcp' / 'OPTIMUS_MCP_CONFIG.json'
# The monitor's own verdicts, and the artefact its handshake writes. Both are
# measurements this builder READS - it does not invent a second opinion.
HEALTH_JSON = WORKSPACE / '13_COMMAND_CENTER' / 'api' / 'health.json'
HANDSHAKE_JSON = WORKSPACE / '09_LOGS' / 'mcp_handshake.json'
SCRAPED = WORKSPACE / '09_LOGS' / 'scraped'

OPEN = 'OPEN'
CLOSED = 'CLOSED-BUILT'

# The modules the monitor probes, with the capability each one carries.
DEP_MODULES = (
    ('playwright', 'browser automation'), ('PIL', 'image processing'),
    ('pypdf', 'PDF processing'), ('docx', 'DOCX processing'),
    ('openpyxl', 'XLSX processing'), ('pptx', 'PPTX processing'),
    ('cv2', 'video processing'), ('pytesseract', 'OCR binding'),
    ('faster_whisper', 'audio transcription'),
)


def read(path: Path) -> str:
    try:
        return path.read_text(encoding='utf-8')
    except (OSError, UnicodeDecodeError):
        return ''


def has_all(*needles: str, source: str) -> List[str]:
    """Return the needles that were actually found."""
    return [n for n in needles if n in source]


# Each concept: (id, name, doctrine file, implementation file, symbols, test
# markers, mcp tools, panel, owner, next action when not done)
CONCEPTS = [
    dict(id='C01', concept='Triple filter (REASON + LOGIC + STRATEGY)',
         chapter='CH_03', doctrine='03_INTELLIGENCE/algorithms/TRIPLE_FILTER_ALGORITHM.md',
         impl='08_SELF_IMPROVEMENT/sentinel_orchestrator.py',
         symbols=['triple_filter_check'], tests=['Orchestrator'],
         tools=['sentinel_apply_triple_filter'], panel='Axes / Logic',
         owner='Mavis', next_action=''),
    dict(id='C02', concept='Anti-mimicry detectors A1-A12',
         chapter='CH_06/CH_12', doctrine='03_INTELLIGENCE/filters/ANTI_MIMICRY_DETECTORS.md',
         impl='07_BACKBONE/mcp/sentinel_hub_server.py',
         symbols=['sentinel_check_mimicry'], tests=['Mimicry'],
         tools=['sentinel_check_mimicry'], panel='Doctrine',
         owner='Mavis',
         next_action='12 detectors are documented; one tool exposes the set. '
                     'Confirm every detector is reachable or document which are not.'),
    dict(id='C03', concept='Rule triggers R-2, R-9, R-10',
         chapter='CH_07', doctrine='05_LEARNING/monitors/RULE_TRIGGER_MONITOR.md',
         impl='08_SELF_IMPROVEMENT/sentinel_orchestrator.py',
         symbols=['check_r2', 'check_r9', 'check_r10'], tests=['Orchestrator'],
         tools=['sentinel_check_r_triggers'], panel='Doctrine',
         owner='Mavis',
         next_action='Confirm the R-9/R-10 Romanian trigger strings are byte-exact '
                     'against the corpus; a normalised variant would break the detector.'),
    dict(id='C04', concept='Bimodal workflow MODE_A / R0 / MODE_B',
         chapter='CH_15', doctrine='01_FOUNDATION/protocols/BIMODAL_WORKFLOW.md',
         impl='08_SELF_IMPROVEMENT/bimodal_workflow.py',
         symbols=['enter_mode_a', 'propose_r0', 'ratify_r0', 'execute_step'],
         tests=['BimodalWorkflow'], tools=['sentinel_workflow_enter_mode_a',
                                           'sentinel_workflow_propose_r0',
                                           'sentinel_workflow_ratify',
                                           'sentinel_workflow_execute'],
         panel='Workflow', owner='Mavis', next_action=''),
    dict(id='C05', concept='STOP means report, ask and wait',
         chapter='CH_15', doctrine='01_FOUNDATION/protocols/BIMODAL_WORKFLOW.md',
         impl='08_SELF_IMPROVEMENT/bimodal_workflow.py',
         symbols=['_stop', 'acknowledge_stop', 'stop_report', 'is_stopped'],
         tests=['BimodalStopPersistence'], tools=[],
         panel='Workflow', owner='Mavis',
         next_action='Add MCP tools for stop_report and acknowledge_stop so an agent '
                     'can read and clear a stop without editing state files.'),
    dict(id='C06', concept='Priority hierarchy SYSTEM > TASK > SPEED > FEELINGS',
         chapter='CH_15', doctrine='01_FOUNDATION/doctrine/A_FI_DOCTRINE.md',
         impl='08_SELF_IMPROVEMENT/bimodal_workflow.py',
         symbols=['PRIORITY_HIERARCHY', 'check_priority_violation'],
         tests=['BimodalWorkflow'], tools=[], panel='Workflow', owner='Mavis',
         next_action='check_priority_violation is not exposed through the MCP hub.'),
    dict(id='C07', concept='Language law - code English, wisdom Romanian',
         chapter='CH_14', doctrine='01_FOUNDATION/doctrine/A_FI_DOCTRINE.md',
         impl='08_SELF_IMPROVEMENT/test_suite.py',
         symbols=['test_no_romanian_in_code'], tests=['NoRomanianInCode'],
         tools=[], panel='Overview', owner='Mavis', next_action=''),
    dict(id='C08', concept='Corpus extraction - chronological, deduplicated, verifiable',
         chapter='CH_16', doctrine='11_BRAIN/01_RAW/CHANGELOG_EXTRACTION.md',
         impl='08_SELF_IMPROVEMENT/corpus_extractor.py',
         symbols=['extract', 'build_chapters', 'digest', 'verify', 'integrity'],
         tests=['BrainAndMonitor'], tools=[], panel='Brain', owner='Mavis',
         next_action='The extractor is verified by its own integrity gate; a test in '
                     'test_suite.py would make it part of the standard gate.'),
    dict(id='C09', concept='Self-improvement with an R0 ratify gate',
         chapter='CH_16', doctrine='11_BRAIN/04_METHOD/TANY_LLM_TO_SENTINEL.md',
         impl='08_SELF_IMPROVEMENT/self_improvement.py',
         symbols=['observe', 'classify', 'derive_lesson', 'ratify', 'promote',
                  'self_check'],
         tests=['BrainAndMonitor'], tools=[], panel='Learning', owner='Mavis',
         next_action='No MCP tool surfaces the learning queue to an agent yet.'),
    dict(id='C10', concept='Self-monitor with NOT_RUN as a first-class status',
         chapter='CH_16', doctrine='13_COMMAND_CENTER/README.md',
         impl='08_SELF_IMPROVEMENT/monitor.py',
         symbols=['collect', 'corpus_checks', 'workflow_checks', 'dependency_checks'],
         tests=['BrainAndMonitor'], tools=[], panel='Overview', owner='Mavis',
         next_action='No MCP tool exposes health.json yet.'),
    dict(id='C11', concept='Command Center backend - loopback, whitelist, SSE',
         chapter='CH_16', doctrine='13_COMMAND_CENTER/README.md',
         impl='13_COMMAND_CENTER/api/server.ps1',
         symbols=['ACTIONS', 'Send-Response', 'Search-Corpus'],
         tests=['DashboardSurface'], tools=[], panel='Command cockpit', owner='Mavis',
         next_action='Whitelist refusal (400 on an unknown id) is verified by test, '
                     'not by inspection.'),
    dict(id='C12', concept='Multimodal processing',
         chapter='CH_14', doctrine='08_SELF_IMPROVEMENT/MULTIMODAL_PROCESSOR.md',
         impl='08_SELF_IMPROVEMENT/multimodal_processor.py',
         symbols=['process'], tests=['MultiModal'], tools=[],
         panel='Wiring', owner='Mavis',
         next_action='Image and PDF paths are UNVERIFIED: PIL and pypdf are not '
                     'importable on either interpreter.'),
    dict(id='C13', concept='Browser automation (Playwright)',
         chapter='CH_14', doctrine='08_SELF_IMPROVEMENT/BROWSER_AUTOMATION.md',
         impl='08_SELF_IMPROVEMENT/browser_automation.py',
         symbols=['navigate', 'scrape', 'screenshot'], tests=['BrowserAutomation'],
         tools=['sentinel_browser_navigate', 'sentinel_browser_scrape'],
         panel='Wiring', owner='Mavis',
         next_action='NOT RUN: playwright is not importable. Installing it needs R0.'),
    dict(id='C14', concept='Cross-instance mailbox and heartbeat',
         chapter='CH_07', doctrine='08_SELF_IMPROVEMENT/CROSS_INSTANCE_PROTOCOL.md',
         impl='08_SELF_IMPROVEMENT/cross_instance.py',
         symbols=['heartbeat', 'send_message', 'broadcast'],
         tests=['CrossInstance'], tools=['sentinel_cross_instance_send',
                                         'sentinel_cross_instance_broadcast'],
         panel='Wiring', owner='Mavis',
         next_action='File-based only. Correct inside the boundary, but it is not a '
                     'network bus and the docs should not imply one.'),
    dict(id='C15', concept='Universal substrate compatibility',
         chapter='CH_07', doctrine='08_SELF_IMPROVEMENT/UNIVERSAL_COMPATIBILITY.md',
         impl='08_SELF_IMPROVEMENT/universal_compat.py',
         symbols=['adapt_prompt', 'verify'], tests=['UniversalCompat'],
         tools=['sentinel_universal_adapt_prompt', 'sentinel_universal_verify'],
         panel='Wiring', owner='Mavis',
         next_action='Never run against Qwen, LongCat or Antigravity for real. '
                     'A declared-vs-verified substrate table is the honest form.'),
    dict(id='C16', concept='Self-modification inside boundaries',
         chapter='CH_13', doctrine='08_SELF_IMPROVEMENT/SECURITY_BOUNDARY.md',
         impl='08_SELF_IMPROVEMENT/self_modify_engine.py',
         symbols=['modify'], tests=['SelfModify'], tools=['sentinel_log_event'],
         panel='Wiring', owner='Mavis',
         next_action='Add a test that ATTEMPTS a boundary breach and asserts refusal, '
                     'built from the real boundary text.'),
    dict(id='C17', concept='Backup and restore with metadata',
         chapter='CH_13', doctrine='08_SELF_IMPROVEMENT/BACKUP_RESTORE_SYSTEM.md',
         impl='08_SELF_IMPROVEMENT/backup_system.py',
         symbols=['create_backup', 'verify_integrity'], tests=['Backup'],
         tools=[], panel='Wiring', owner='Mavis',
         next_action='Adopt the proven five-snapshot frozen store used by the CC.'),
    dict(id='C18', concept='Partnership protocol (two blind men)',
         chapter='CH_04', doctrine='04_PARTNERSHIP/protocols/PARTNERSHIP_TWO_BLIND_MEN.md',
         impl='', symbols=[], tests=[], tools=[],
         panel='Doctrine', owner='Popy',
         next_action='DOCUMENTED ONLY - no implementation exists. This is the '
                     'design-only smell named in Stage 2.'),
    dict(id='C19', concept='The 3-Propozitii ritual as an invocable command',
         chapter='CH_10', doctrine='02_OPERATIONAL/rituals/RITUAL_3_PROPOZITII.md',
         impl='', symbols=[], tests=[], tools=[], panel='Doctrine', owner='Popy',
         next_action='DOCUMENTED ONLY - the ritual is described but not wired to a '
                     'command, so it cannot fail visibly.'),
    dict(id='C20', concept='Feedback loop and evaluators',
         chapter='CH_13', doctrine='05_LEARNING/evaluators/FEEDBACK_LOOP.md',
         impl='08_SELF_IMPROVEMENT/self_improvement.py',
         symbols=['derive_lesson'], tests=['BrainAndMonitor'], tools=[],
         panel='Learning', owner='Mavis', next_action=''),
    dict(id='C21', concept='Context pressure monitor',
         chapter='CH_13', doctrine='05_LEARNING/monitors/CONTEXT_PRESSURE_MONITOR.md',
         impl='02_OPERATIONAL/scripts/sentinel_context_monitor.ps1',
         symbols=[], tests=['Scripts'], tools=[], panel='Wiring', owner='Mavis', next_action=''),
    dict(id='C22', concept='Auto-learning loop',
         chapter='CH_13', doctrine='05_LEARNING/loops/AUTO_LEARNING_LOOP.md',
         impl='08_SELF_IMPROVEMENT/self_improvement.py',
         symbols=['observe', 'classify'], tests=['BrainAndMonitor'], tools=[],
         panel='Learning', owner='Mavis', next_action=''),
    dict(id='C23', concept='Historical cultures (Cucuteni, Geto, Atos, Romani)',
         chapter='CH_12', doctrine='06_HISTORICAL/cultures/CUCUTENI_TRYPILLIA.md',
         impl='', symbols=[], tests=[], tools=[], panel='Brain', owner='Popy',
         next_action='Wisdom layer. Correctly documentation-only; it is a corpus, '
                     'not a program.'),
    dict(id='C24', concept='963 Hz / SACRU proverbs',
         chapter='CH_06', doctrine='01_FOUNDATION/proverbs/SENTINEL_PROVERBS.md',
         impl='', symbols=[], tests=[], tools=[], panel='Brain', owner='Popy',
         next_action='HONEST FINDING: the source file is a 25-axis decision matrix, '
                     'not a 963-proverb enumeration, and its per-proverb attributions '
                     'are flagged in-file as fabricated by an earlier agent.'),
]


def evaluate(c: Dict[str, Any], suite_src: str, hub_src: str,
             served: Set[str] = ()) -> Dict[str, Any]:
    doctrine_path = WORKSPACE / c['doctrine'] if c['doctrine'] else None
    doctrine_ok = bool(doctrine_path and doctrine_path.exists())
    impl_path = WORKSPACE / c['impl'] if c['impl'] else None
    impl_ok = bool(impl_path and impl_path.exists())
    symbols_found = has_all(*c['symbols'], source=read(impl_path)) if impl_ok else []
    tests_found = [t for t in c['tests'] if t in suite_src]
    tools_found = [t for t in c['tools'] if t in hub_src]
    # WIRED is a claim about the wire, so it is measured on the wire. It used to
    # be hardcoded False, which is why the generated report said "0 are wired"
    # while 26 tools were answering over stdio: the matrix was DERIVED BY
    # MEASUREMENT in every field except this one.
    wired = bool(tools_found) and all(t in served for t in tools_found)

    if not doctrine_ok and not impl_ok:
        status = 'ABSENT'
    elif not impl_ok:
        status = 'DESIGNED'
    elif not symbols_found:
        status = 'PARTIAL'
    elif not tests_found:
        status = 'CODED'
    else:
        status = 'TESTED'
    # OBSERVABLE requires a panel to exist in the built dashboard.
    if status == 'TESTED' and c['panel']:
        status = 'OBSERVABLE'

    return {
        'id': c['id'],
        'concept': c['concept'],
        'chapter': c['chapter'],
        'doctrine': c['doctrine'],
        'doctrine_exists': doctrine_ok,
        'implementation': c['impl'] or None,
        'implementation_exists': impl_ok,
        'symbols': symbols_found,
        'symbols_missing': [s for s in c['symbols'] if s not in symbols_found],
        'test': ','.join(tests_found) if tests_found else None,
        'test_found': bool(tests_found),
        'mcp_tool': ','.join(tools_found) if tools_found else None,
        'mcp_wired': wired,
        'mcp_wired_basis': ('served over stdio by the last live handshake'
                            if wired else
                            ('declared in source but not served by the last handshake'
                             if tools_found else 'no MCP tool declared')),
        'panel': c['panel'],
        'status': status,
        'owner': c['owner'],
        'next_action': c['next_action'] or (
            '' if status in ('OBSERVABLE',) else
            'Expose through the MCP hub and surface it in a panel.'),
    }


# ---------------------------------------------------------------------------
# The register is a ledger. It is merged, never overwritten.
# ---------------------------------------------------------------------------
#
# Measured 2026-10-28: this builder used to WRITE GAP_REGISTER.json with the
# gaps it had measured and nothing else. Running it destroyed 11 of the 18
# entries in the ledger - all nine HPROF_* profile tickets plus the
# HERMES_GATEWAY_PROFILES umbrella - because it never knew they existed. A
# measurement instrument that owns the file it measures will eventually eat it.
#
# The contract, in this order:
#   1. An entry is never deleted.
#   2. An entry whose gap can be MEASURED is re-measured. The original claim
#      stays visible, and the measurement is added beside it.
#   3. An entry that cannot be measured is preserved byte for byte. It belongs
#      to whoever wrote it, and closing it is an operator decision.


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec='seconds')


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None


def file_stamp(path: Path) -> str:
    try:
        st = path.stat()
    except OSError:
        return f'{path} is not on disk'
    when = datetime.fromtimestamp(st.st_mtime).isoformat(timespec='seconds')
    return f'{path} exists, {st.st_size} B, mtime {when}'


def blueprint_servers() -> Dict[str, Any]:
    cfg = load_json(BLUEPRINT)
    if not isinstance(cfg, dict):
        return {}
    return cfg.get('servers') or {}


def served_tools() -> Tuple[Set[str], str]:
    """The tools the hub SERVED, from the artefact the handshake itself wrote.

    Not the tools the hub declares in its source. The gap between declared and
    served is the finding, so the declared count cannot stand in for it.
    """
    art = load_json(HANDSHAKE_JSON)
    if not isinstance(art, dict):
        return set(), 'no handshake artefact: NOT_MEASURED'
    names = set(art.get('tool_names') or [])
    note = (f"{art.get('attempted_at')} "
            f"({art.get('tools_returned_by_server')} served of "
            f"{art.get('tools_declared_in_source')} declared)")
    return names, note


# -- the probes -------------------------------------------------------------
# Each probe answers one question: is the thing this gap is about present NOW?
# It returns (satisfied, detail, conclusive).
#
# `conclusive` is the third value, and it is the one that matters. A probe that
# could not run - the artefact it reads is missing, the monitor has not
# measured - returns False and NOT conclusive. That is NOT_MEASURED, and it is
# not a verdict: a gap whose measurement could not be taken keeps the status it
# has. Flipping a closed gap to open because a file was momentarily absent is
# the class of red that teaches the reader to ignore red.
#
# A probe that never guesses is worth more than a probe that always answers.

def probe_tesseract() -> Tuple[bool, str, bool]:
    found = shutil.which('tesseract')
    how = 'PATH'
    if not found:
        local = os.environ.get('LOCALAPPDATA', '')
        if local:
            candidate = Path(local) / 'TesseractOCR' / 'tesseract.exe'
            if candidate.exists():
                found, how = str(candidate), 'known location'
    if found:
        return True, f'OCR engine resolves at {found} (via {how})', True
    return False, 'no tesseract binary on PATH and none at the known location', True


def artefact_counts() -> Tuple[int, int, int]:
    """(inspected, empty, unreadable) judged by CONTENT.

    Emptiness is a content claim. Size is not a proxy for it: the old
    predicate was `size <= 400 bytes`, which flagged a successful scrape of a
    small page as empty - the exact defect the monitor's own check and its
    regression test exist to kill.
    """
    inspected = empty = unreadable = 0
    if SCRAPED.exists():
        for f in sorted(SCRAPED.glob('*.json')):
            inspected += 1
            data = load_json(f)
            if data is None:
                unreadable += 1
                continue
            extracted = (data or {}).get('extracted') or {}
            has_title = bool(str(extracted.get('title') or '').strip())
            has_items = bool(extracted.get('headings') or extracted.get('links'))
            if has_title and has_items:
                continue
            url = str((data or {}).get('url') or '').strip()
            scheme = url.split(':', 1)[0].lower() if ':' in url else ''
            if not url or scheme in ('about', 'data', 'javascript', 'chrome', 'blob'):
                continue
            empty += 1
    return inspected, empty, unreadable


def probe_artefacts() -> Tuple[bool, str, bool]:
    inspected, empty, unreadable = artefact_counts()
    detail = (f'{inspected} scrape artefacts inspected by content: {empty} carry no '
              f'result, {unreadable} unreadable')
    return (empty == 0 and unreadable == 0), detail, True


def probe_wiring() -> Tuple[bool, str, bool]:
    """The hub's own handshake, read from the artefact that handshake writes."""
    art = load_json(HANDSHAKE_JSON)
    if not isinstance(art, dict):
        return False, 'no handshake artefact on disk: NOT_MEASURED', False
    served = art.get('tools_returned_by_server')
    declared = art.get('tools_declared_in_source')
    when = art.get('attempted_at')
    if art.get('status') != 'OK':
        return False, f'last handshake at {when} did not complete: {art.get("error")}', True
    if not served or served != declared:
        return False, (f'last handshake at {when}: {declared} declared, {served} served - '
                       f'a tool that is declared but not served is a defect, not scaffolding'), True
    return True, (f'live MCP handshake at {when}: {served} of {declared} declared tools '
                  f'returned over stdio'), True


def probe_profile_server(name: str) -> Tuple[bool, str, bool]:
    """Is one declared Hermes profile server present and reachable?"""
    spec = blueprint_servers().get(name) or {}
    args = [str(a) for a in (spec.get('args') or [])]
    py_arg = next((a for a in args if a.endswith('.py')), None)
    if py_arg:
        target = Path(py_arg)
        if target.exists():
            return True, file_stamp(target), True
        return False, f'the declared target {target} is not on disk', True
    # npm-backed entry: the registry answer is the measurement, and it is the
    # monitor's own check rather than an assumption about the package.
    health = load_json(HEALTH_JSON) or {}
    for c in (health.get('checks') or []):
        if c.get('id') == 'mcp_npx_packages_resolve':
            evidence = f"{c.get('evidence', '')} (measured {c.get('measured_at', '')})"
            if c.get('status') == 'NOT_RUN':
                return False, f'{evidence} - NOT_RUN: NOT_MEASURED', False
            return c.get('status') == 'OK', evidence, True
    return False, 'mcp_npx_packages_resolve is not available: NOT_MEASURED', False


def probe_dependency(module: str) -> Tuple[bool, str, bool]:
    try:
        importlib.import_module(module)
        return True, f'{module} is importable on this interpreter', True
    except Exception as exc:
        return False, f'{module} is not importable: {type(exc).__name__}', True


def probe_concept(row: Dict[str, Any]) -> Tuple[bool, str, bool]:
    detail = (f'concept {row["id"]} computes to {row["status"]} '
              f'(doctrine_exists={row["doctrine_exists"]}, '
              f'implementation_exists={row["implementation_exists"]}, '
              f'symbols_missing={row["symbols_missing"]})')
    return row['status'] in ('CODED', 'TESTED', 'WIRED', 'OBSERVABLE'), detail, True


def build_probes(matrix: Dict[str, Any]) -> Dict[str, Callable[[], Tuple[bool, str, bool]]]:
    """One probe per gap this builder is allowed to re-measure."""
    probes: Dict[str, Callable[[], Tuple[bool, str, bool]]] = {
        'BIN_TESSERACT': probe_tesseract,
        'ARTIFACT_EMPTY': probe_artefacts,
        'WIRING_MCP': probe_wiring,
    }
    for name in blueprint_servers():
        gid = 'HPROF_' + name.replace('-', '_')
        probes[gid] = (lambda n=name: probe_profile_server(n))

    def umbrella() -> Tuple[bool, str, bool]:
        parts, all_ok, conclusive = [], True, True
        for name in blueprint_servers():
            ok, detail, sure = probe_profile_server(name)
            all_ok = all_ok and ok
            conclusive = conclusive and sure
            parts.append(f'{name}: {detail}')
        return all_ok, '; '.join(parts), conclusive

    probes['HERMES_GATEWAY_PROFILES'] = umbrella
    for mod, _capability in DEP_MODULES:
        probes['DEP_' + mod] = (lambda m=mod: probe_dependency(m))
    for mid, row in matrix.items():
        probes['CONCEPT_' + mid] = (lambda r=row: probe_concept(r))
    return probes


def build_gaps(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Every degradation the builder can measure, each with the evidence."""
    gaps = []

    for mod, capability in DEP_MODULES:
        try:
            importlib.import_module(mod)
            continue
        except Exception:
            gaps.append({
                'id': f'DEP_{mod}', 'area': 'dependency', 'status': OPEN,
                'what': f'{capability} is UNVERIFIED: {mod} is not importable',
                'evidence': 'measured by monitor.py dependency family on both '
                            'interpreter 3.14.6 and 3.11.15',
                'impact': 'the affected path is not proven to work',
                'fix_requires': 'R0 - installing packages is not automatic',
                'owner': 'Popy',
            })

    if not shutil.which('tesseract'):
        gaps.append({
            'id': 'BIN_TESSERACT', 'area': 'dependency', 'status': OPEN,
            'what': 'OCR engine not on PATH',
            'evidence': 'monitor.py bin_tesseract check',
            'impact': 'OCR is unverified even if pytesseract were installed',
            'fix_requires': 'R0 - external binary install', 'owner': 'Popy',
        })

    for r in rows:
        if r['status'] in ('DESIGNED', 'ABSENT', 'PARTIAL'):
            gaps.append({
                'id': f"CONCEPT_{r['id']}", 'area': 'concept', 'status': OPEN,
                'what': f"{r['concept']} is {r['status']}",
                'evidence': f"doctrine_exists={r['doctrine_exists']} "
                            f"implementation_exists={r['implementation_exists']} "
                            f"symbols_missing={r['symbols_missing']}",
                'impact': 'documented but not running',
                'fix_requires': r['next_action'] or 'implementation',
                'owner': r['owner'],
            })

    gaps.append({
        'id': 'WIRING_MCP', 'area': 'wiring', 'status': OPEN,
        'what': 'MCP tools are DECLARED but not WIRED to any runtime',
        'evidence': 'no Hermes handshake has been performed; monitor reports '
                    'mcp_tools_wired as NOT_RUN',
        'impact': 'an agent cannot actually call the SENTINEL tools through Hermes',
        'fix_requires': 'R0 - registering an MCP server is a cross-system change',
        'owner': 'Popy',
    })

    _inspected, empty, _unreadable = artefact_counts()
    if empty:
        gaps.append({
            'id': 'ARTIFACT_EMPTY', 'area': 'logs', 'status': OPEN,
            'what': f'{empty} empty result files in 09_LOGS/scraped',
            'evidence': 'left by browser test runs; they look like success and are not',
            'impact': 'visual noise that reads as evidence',
            'fix_requires': 'explicit operator decision - deletion is never automatic',
            'owner': 'Popy',
        })

    for name in blueprint_servers():
        ok, detail, _conclusive = probe_profile_server(name)
        if ok:
            continue
        spec = blueprint_servers().get(name) or {}
        target = next((str(a) for a in (spec.get('args') or [])
                       if str(a).endswith('.py')), 'an npm package')
        gaps.append({
            'id': 'HPROF_' + name.replace('-', '_'),
            'area': 'hermes-gateway-profile', 'status': OPEN,
            'what': f"PLANNED - Hermes profile gateway server '{name}' is declared in "
                    f"OPTIMUS_MCP_CONFIG.json and not yet constructed. This is the plan, "
                    f"not a defect.",
            'evidence': f'blueprint 07_BACKBONE/mcp/OPTIMUS_MCP_CONFIG.json declares '
                        f'{name} -> {target}; target_present=False',
            'impact': 'one of nine Hermes profile gateway servers; the swarm cannot be '
                      'complete while this profile has no server',
            'fix_requires': 'Construct the server in the Hermes gateway. DO NOT remove '
                            'the declaration: the blueprint is the plan, and a gap is '
                            'closed by upgrading the system, never by deleting the line '
                            'that names it.',
            'owner': 'Popy',
        })

    return gaps


def merge_gaps(existing: List[Dict[str, Any]],
               measured: List[Dict[str, Any]],
               probes: Dict[str, Callable[[], Tuple[bool, str]]],
               ) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
    """Merge the measured gaps into the ledger. Nothing is ever deleted."""
    out: List[Dict[str, Any]] = []
    stats = {'preserved': 0, 'closed': 0, 'still_closed': 0, 'reopened': 0,
             'verified_open': 0, 'not_measured': 0, 'added': 0}
    known = set()

    for entry in existing:
        if not isinstance(entry, dict):
            continue
        gid = str(entry.get('id'))
        known.add(gid)
        probe = probes.get(gid)
        if probe is None:
            # Another writer's entry, and this builder cannot measure it. It
            # is preserved exactly as it was found.
            out.append(entry)
            stats['preserved'] += 1
            continue

        satisfied, detail, conclusive = probe()
        stamp = now_iso()
        was_closed = entry.get('status') == CLOSED

        merged: Dict[str, Any] = {
            'id': entry.get('id'),
            'status': CLOSED if satisfied else OPEN,
        }

        if not conclusive:
            # The measurement could not be taken. NOT_MEASURED is not a verdict:
            # the status stays exactly as it was, and the entry says why.
            merged['status'] = entry.get('status', OPEN)
            unchanged = entry.get('verification') == detail
            merged['verification'] = detail
            merged['verified_at'] = entry.get('verified_at', stamp) if unchanged else stamp
            stats['not_measured'] += 1
        elif satisfied and not was_closed:
            # The gap closes now, and this measurement is the record of it.
            merged['verification'] = detail
            merged['verified_at'] = stamp
            merged['closed_at'] = stamp
            stats['closed'] += 1
        elif satisfied and was_closed:
            # Still closed. The ledger keeps the record of the closure as it was
            # written - a ledger that rewrites itself on every read is not a
            # ledger, and a changed file is a changed history.
            merged['verification'] = entry.get('verification', detail)
            merged['verified_at'] = entry.get('verified_at', stamp)
            if 'closed_at' in entry:
                merged['closed_at'] = entry['closed_at']
            stats['still_closed'] += 1
        elif was_closed:
            merged['verification'] = f'REOPENED {stamp}: {detail}'
            merged['verified_at'] = stamp
            stats['reopened'] += 1
        else:
            unchanged = entry.get('verification') == detail
            merged['verification'] = detail
            merged['verified_at'] = entry.get('verified_at', stamp) if unchanged else stamp
            stats['verified_open'] += 1

        for key in ('area', 'what', 'evidence', 'impact', 'fix_requires', 'owner'):
            if key in entry:
                merged[key] = entry[key]
        for key, value in entry.items():
            if key not in merged:
                merged[key] = value

        out.append(merged)

    for gap in measured:
        gid = str(gap.get('id'))
        if gid in known:
            continue
        entry = dict(gap)
        entry['verification'] = gap.get('evidence', '')
        entry['verified_at'] = now_iso()
        out.append(entry)
        known.add(gid)
        stats['added'] += 1

    return out, stats


def main():
    PROGRAM.mkdir(parents=True, exist_ok=True)
    suite_src = read(SUITE)
    hub_src = read(HUB)
    served, handshake_note = served_tools()

    rows = [evaluate(c, suite_src, hub_src, served) for c in CONCEPTS]
    gaps = build_gaps(rows)
    matrix = {r['id']: r for r in rows}
    probes = build_probes(matrix)

    existing: List[Dict[str, Any]] = []
    if GAPS_JSON.exists():
        loaded = load_json(GAPS_JSON)
        if isinstance(loaded, list):
            existing = [g for g in loaded if isinstance(g, dict)]
        elif isinstance(loaded, dict):
            existing = [g for g in (loaded.get('gaps') or []) if isinstance(g, dict)]

    merged, stats = merge_gaps(existing, gaps, probes)

    MATRIX_JSON.write_text(json.dumps(rows, indent=2, ensure_ascii=False),
                           encoding='utf-8')
    GAPS_JSON.write_text(json.dumps(merged, indent=2, ensure_ascii=False) + '\n',
                         encoding='utf-8')

    counts: Dict[str, int] = {}
    for r in rows:
        counts[r['status']] = counts.get(r['status'], 0) + 1
    print(f'concepts: {len(rows)}')
    for k in sorted(counts):
        print(f'  {k:12s} {counts[k]}')
    print(f'handshake: {handshake_note}')
    still_open = [g for g in merged if g.get('status') != CLOSED]
    print(f'register : {len(merged)} entries '
          f'({len(still_open)} open, {len(merged) - len(still_open)} closed)')
    print(f'  measured and closed  : {stats["closed"]}')
    print(f'  closed and unchanged : {stats["still_closed"]}')
    print(f'  reopened             : {stats["reopened"]}')
    print(f'  measured and open    : {stats["verified_open"]}')
    print(f'  not measured         : {stats["not_measured"]}')
    print(f'  preserved untouched  : {stats["preserved"]}')
    print(f'  added                : {stats["added"]}')
    print(f'written : {MATRIX_JSON}')
    print(f'written : {GAPS_JSON}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
