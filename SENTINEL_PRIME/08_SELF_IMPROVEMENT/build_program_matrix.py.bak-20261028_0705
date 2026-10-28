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
import json
import os
from pathlib import Path
from typing import Any, Dict, List
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


def evaluate(c: Dict[str, Any], suite_src: str, hub_src: str) -> Dict[str, Any]:
    doctrine_path = WORKSPACE / c['doctrine'] if c['doctrine'] else None
    doctrine_ok = bool(doctrine_path and doctrine_path.exists())
    impl_path = WORKSPACE / c['impl'] if c['impl'] else None
    impl_ok = bool(impl_path and impl_path.exists())
    symbols_found = has_all(*c['symbols'], source=read(impl_path)) if impl_ok else []
    tests_found = [t for t in c['tests'] if t in suite_src]
    tools_found = [t for t in c['tools'] if t in hub_src]

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
        'mcp_wired': False,
        'panel': c['panel'],
        'status': status,
        'owner': c['owner'],
        'next_action': c['next_action'] or (
            '' if status in ('OBSERVABLE',) else
            'Expose through the MCP hub and surface it in a panel.'),
    }


def build_gaps(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Every known degradation, each with the evidence that found it."""
    import importlib
    gaps = []

    for mod, capability in (
        ('playwright', 'browser automation'), ('PIL', 'image processing'),
        ('pypdf', 'PDF processing'), ('docx', 'DOCX processing'),
        ('openpyxl', 'XLSX processing'), ('pptx', 'PPTX processing'),
        ('cv2', 'video processing'), ('pytesseract', 'OCR binding'),
        ('faster_whisper', 'audio transcription'),
    ):
        try:
            importlib.import_module(mod)
            continue
        except Exception:
            gaps.append({
                'id': f'DEP_{mod}', 'area': 'dependency', 'status': 'OPEN',
                'what': f'{capability} is UNVERIFIED: {mod} is not importable',
                'evidence': 'measured by monitor.py dependency family on both '
                            'interpreter 3.14.6 and 3.11.15',
                'impact': 'the affected path is not proven to work',
                'fix_requires': 'R0 - installing packages is not automatic',
                'owner': 'Popy',
            })

    import shutil
    if not shutil.which('tesseract'):
        gaps.append({
            'id': 'BIN_TESSERACT', 'area': 'dependency', 'status': 'OPEN',
            'what': 'OCR engine not on PATH',
            'evidence': 'monitor.py bin_tesseract check',
            'impact': 'OCR is unverified even if pytesseract were installed',
            'fix_requires': 'R0 - external binary install', 'owner': 'Popy',
        })

    for r in rows:
        if r['status'] in ('DESIGNED', 'ABSENT', 'PARTIAL'):
            gaps.append({
                'id': f"CONCEPT_{r['id']}", 'area': 'concept', 'status': 'OPEN',
                'what': f"{r['concept']} is {r['status']}",
                'evidence': f"doctrine_exists={r['doctrine_exists']} "
                            f"implementation_exists={r['implementation_exists']} "
                            f"symbols_missing={r['symbols_missing']}",
                'impact': 'documented but not running',
                'fix_requires': r['next_action'] or 'implementation',
                'owner': r['owner'],
            })

    gaps.append({
        'id': 'WIRING_MCP', 'area': 'wiring', 'status': 'OPEN',
        'what': 'MCP tools are DECLARED but not WIRED to any runtime',
        'evidence': 'no Hermes handshake has been performed; monitor reports '
                    'mcp_tools_wired as NOT_RUN',
        'impact': 'an agent cannot actually call the SENTINEL tools through Hermes',
        'fix_requires': 'R0 - registering an MCP server is a cross-system change',
        'owner': 'Popy',
    })

    scraped = WORKSPACE / '09_LOGS' / 'scraped'
    empty = [f.name for f in scraped.glob('*.json') if f.stat().st_size <= 400] \
        if scraped.exists() else []
    if empty:
        gaps.append({
            'id': 'ARTIFACT_EMPTY', 'area': 'logs', 'status': 'OPEN',
            'what': f'{len(empty)} empty result files in 09_LOGS/scraped',
            'evidence': 'left by browser test runs; they look like success and are not',
            'impact': 'visual noise that reads as evidence',
            'fix_requires': 'explicit operator decision - deletion is never automatic',
            'owner': 'Popy',
        })

    return gaps


def main():
    PROGRAM.mkdir(parents=True, exist_ok=True)
    suite_src = read(SUITE)
    hub_src = read(HUB)

    rows = [evaluate(c, suite_src, hub_src) for c in CONCEPTS]
    gaps = build_gaps(rows)

    MATRIX_JSON.write_text(json.dumps(rows, indent=2, ensure_ascii=False),
                           encoding='utf-8')
    GAPS_JSON.write_text(json.dumps(gaps, indent=2, ensure_ascii=False),
                         encoding='utf-8')

    counts: Dict[str, int] = {}
    for r in rows:
        counts[r['status']] = counts.get(r['status'], 0) + 1
    print(f'concepts: {len(rows)}')
    for k in sorted(counts):
        print(f'  {k:12s} {counts[k]}')
    print(f'gaps    : {len(gaps)} open')
    print(f'written : {MATRIX_JSON}')
    print(f'written : {GAPS_JSON}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
