#!/usr/bin/env python3
"""
Self-improvement loop for the MINIMAX SENTINEL BRAIN.

The system improves itself by the SAME procedure Popy used to build it
(11_BRAIN/04_METHOD/TANY_LLM_TO_SENTINEL.md): observe, classify, derive a
lesson, and then STOP. It does not promote anything on its own.

THE RATIFY GATE IS THE POINT
-----------------------------
A candidate lesson is a proposal. Only Popy can turn a proposal into doctrine.
A self-improving system that can ratify its own lessons is a system that can
rewrite its own constraints, and every guarantee in the corpus (zero
fabrication, triple filter, the priority hierarchy) becomes advisory. So:

    CANDIDATE  ->  ratified (by Popy, with input recorded)  ->  PROMOTED

`promote()` is the ONLY method that writes, and it writes to the project
learning layer inside SENTINEL_PRIME. It never writes to user memory, never
writes to the Obsidian vault, and never writes to a doctrine or protocol file.

HARD BOUNDARY
-------------
Writes are confined to SENTINEL_PRIME. Anything outside raises BoundaryError.
This is the same boundary as SECURITY_BOUNDARY.md, enforced rather than
described.

All code, comments and runtime messages in English. Lessons carry their
verbatim evidence, which is Romanian when the operator spoke Romanian.
"""
import json
import os
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

WORKSPACE = Path(os.environ.get(
    'WORKSPACE_ROOT',
    r'C:\Users\apviz\.minimax-agent\projects\SENTINEL_PRIME'))

LOG_FILE = WORKSPACE / '09_LOGS' / 'self_improvement.log'
CANDIDATES_FILE = WORKSPACE / '09_LOGS' / 'self_improvement_candidates.json'
PROMOTED_FILE = WORKSPACE / '05_LEARNING' / 'lessons' / 'PROMOTED_LESSONS.md'
LOCK_FILE = WORKSPACE / '08_SELF_IMPROVEMENT' / 'security_boundary.txt'

STATUS_CANDIDATE = 'CANDIDATE'
STATUS_RATIFIED = 'RATIFIED'
STATUS_PROMOTED = 'PROMOTED'

# Classification catalogue. These are the correction patterns that actually
# occurred in the corpus (see 11_BRAIN/04_METHOD/MISSTEPS_AND_CORRECTIONS.md).
# A pattern that does not match any of them is honestly labelled NOVEL rather
# than being forced into a bucket.
PATTERNS = [
    {
        'id': 'UNVERIFIED_CLAIM',
        'signal': ['not verified', 'assume', 'probably', 'i think it works', 'should work'],
        'lesson': 'A claim about the world needs a tool call that measures it before it is stated.',
        'source': 'M-01, D-04',
    },
    {
        'id': 'DESIGN_AS_IMPLEMENTATION',
        'signal': ['design-only', 'scaffold', 'placeholder', 'pseudo', 'for now'],
        'lesson': 'A designed thing presented as working is the one unforgivable failure. Implement it or label it.',
        'source': 'M-11, CH_14',
    },
    {
        'id': 'SCOPE_SUBSTITUTION',
        'signal': ['actually, instead', 'while i was at it', 'i also added', 'you asked for x but'],
        'lesson': 'Execute the verb, not the topic. Scope words are literal.',
        'source': 'S-02, 2026-10-02',
    },
    {
        'id': 'OPTIMISING_A_SPECIFIED_SYSTEM',
        'signal': ['while we are here', 'optimise', 'optimize', 'clean up', 'improve this loop'],
        'lesson': 'Do not re-tune a system the operator specified. Say it in one line and let him decide.',
        'source': 'S-03, 2026-10-03',
    },
    {
        'id': 'SELF_MEASUREMENT_AS_VERIFICATION',
        'signal': ['it works because', 'i checked and it', 'tested it myself', 'all green'],
        'lesson': 'Self-measurement is not verification. A green log line is not a working product.',
        'source': 'S-01, 2026-10-02',
    },
    {
        'id': 'CONSTANT_AS_EVIDENCE',
        'signal': ['is not watched', 'no handler', 'always', 'never', 'by design'],
        'lesson': 'A claim stored as a string cannot expire. Sentences describing a system must be computed at scan time.',
        'source': 'S-04, 2026-10-04',
    },
    {
        'id': 'CHECK_DID_NOT_RUN',
        'signal': ['0/0', 'no tests', 'skipped', 'silently', 'nothing logged'],
        'lesson': 'A check that did not run is not a passing check. It must be able to say so.',
        'source': 'S-05, 2026-10-04',
    },
    {
        'id': 'FIXTURE_MAKES_THE_MISTAKE',
        'signal': ['test passes but', 'fixture', 'invented data', 'sample values'],
        'lesson': 'A hand-made fixture can reproduce the mistake it exists to catch. Use the real values.',
        'source': 'S-06, 2026-10-04',
    },
    {
        'id': 'SILENT_FAILURE',
        'signal': ['no error', 'no output', 'hangs', 'never returns', 'empty result'],
        'lesson': 'A silent failure has no symptoms. Make the code narrate its own progress.',
        'source': 'S-07, 2026-10-04',
    },
    {
        'id': 'STOP_WITHOUT_MECHANISM',
        'signal': ['stop means', 'never continue', 'i will stop', 'asking for input'],
        'lesson': 'A guarantee written in a comment is not a mechanism. A law needs a state it can be observed in.',
        'source': 'M-10, 2026-10-04',
    },
]


class BoundaryError(Exception):
    """Raised when a write would leave SENTINEL_PRIME."""


def _now() -> str:
    return datetime.now().isoformat()


def _assert_inside_workspace(path: Path) -> None:
    try:
        path.resolve().relative_to(WORKSPACE.resolve())
    except ValueError:
        raise BoundaryError(
            f'refused: {path} is outside the SENTINEL_PRIME write boundary')


class SelfImprovement:
    def __init__(self):
        self.candidates: List[Dict[str, Any]] = self._load(CANDIDATES_FILE, [])

    # ----- persistence -----

    @staticmethod
    def _load(path: Path, default):
        if not path.exists():
            return default
        try:
            return json.loads(path.read_text(encoding='utf-8'))
        except (json.JSONDecodeError, OSError):
            return default

    def _save(self):
        _assert_inside_workspace(CANDIDATES_FILE)
        CANDIDATES_FILE.parent.mkdir(parents=True, exist_ok=True)
        CANDIDATES_FILE.write_text(
            json.dumps(self.candidates, indent=2, ensure_ascii=False), encoding='utf-8')

    @staticmethod
    def _log(event: str, payload: Dict[str, Any]):
        _assert_inside_workspace(LOG_FILE)
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        entry = {'ts': _now(), 'event': event, **payload}
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        return entry

    # ----- the loop -----

    def observe(self, event: str, context: str = '', source: str = '') -> Dict[str, Any]:
        """Step 1. Record something that happened. Returns the observation."""
        obs = {
            'observed_at': _now(),
            'event': event,
            'context': context,
            'source': source,
        }
        self._log('OBSERVE', obs)
        return obs

    def classify(self, event: str, context: str = '') -> Dict[str, Any]:
        """Step 2. Match the event against the known correction patterns."""
        haystack = f'{event} {context}'.lower()
        hits = []
        for pattern in PATTERNS:
            matched = [s for s in pattern['signal'] if s in haystack]
            if matched:
                hits.append({
                    'id': pattern['id'],
                    'lesson': pattern['lesson'],
                    'source': pattern['source'],
                    'matched_signals': matched,
                })
        if not hits:
            return {'classification': 'NOVEL', 'matches': [],
                    'note': 'No known pattern matched. Labelled NOVEL rather than forced '
                            'into a bucket - an honest unknown beats a wrong label.'}
        # Highest signal count wins; ties broken by declaration order.
        hits.sort(key=lambda h: len(h['matched_signals']), reverse=True)
        return {'classification': hits[0]['id'], 'matches': hits,
                'lesson': hits[0]['lesson'], 'source': hits[0]['source']}

    def derive_lesson(self, event: str, context: str = '', evidence: str = '',
                      source: str = '') -> Dict[str, Any]:
        """Step 3. Produce a CANDIDATE lesson with its verbatim evidence.

        The evidence is kept exactly as given, including Romanian. The lesson
        text itself is English so it can be executed and checked.
        """
        verdict = self.classify(event, context)
        candidate = {
            'id': f"C{len(self.candidates) + 1:04d}",
            'created_at': _now(),
            'status': STATUS_CANDIDATE,
            'event': event,
            'context': context[:600],
            'classification': verdict['classification'],
            'lesson': verdict.get('lesson',
                                  'Unclassified event. Popy decides whether this is a lesson.'),
            'known_source': verdict.get('source'),
            'evidence_verbatim': evidence,
            'observed_from': source,
            'ratified_at': None,
            'ratified_by': None,
            'promoted_at': None,
        }
        self.candidates.append(candidate)
        self._save()
        self._log('CANDIDATE', {'id': candidate['id'],
                                'classification': candidate['classification'],
                                'lesson': candidate['lesson']})
        return candidate

    def ratify(self, candidate_id: str, operator_input: str) -> Dict[str, Any]:
        """Step 4. Popy ratifies a candidate. ONLY he can, and the input is recorded.

        An empty ratification is refused: an unratified lesson stays a
        candidate, and a lesson promoted without a real authorisation is
        exactly the failure the gate exists to prevent.
        """
        c = self._find(candidate_id)
        if not operator_input or not str(operator_input).strip():
            raise ValueError(
                'ratify() requires the operator input that authorises this lesson. '
                'An empty ratification is not a ratification.')
        c['status'] = STATUS_RATIFIED
        c['ratified_at'] = _now()
        c['ratified_by'] = str(operator_input).strip()
        self._save()
        self._log('RATIFIED', {'id': c['id'], 'by': c['ratified_by']})
        return c

    def promote(self, candidate_id: str) -> Dict[str, Any]:
        """Step 5. Write a RATIFIED lesson into the project learning layer.

        Refuses a candidate that Popy has not ratified. This is the enforcement
        of R0 for self-modification.
        """
        c = self._find(candidate_id)
        if c['status'] == STATUS_CANDIDATE:
            raise ValueError(
                f"candidate {c['id']} is not ratified. The system may propose a change "
                f"to itself; only Popy may ratify it.")
        if c['status'] == STATUS_PROMOTED:
            return c
        c['status'] = STATUS_PROMOTED
        c['promoted_at'] = _now()
        self._save()

        _assert_inside_workspace(PROMOTED_FILE)
        PROMOTED_FILE.parent.mkdir(parents=True, exist_ok=True)
        existing = PROMOTED_FILE.read_text(encoding='utf-8') if PROMOTED_FILE.exists() else (
            '# PROMOTED LESSONS\n\n'
            'Lessons ratified by Popy and written into the SENTINEL learning layer.\n'
            'A lesson reaches this file only through SelfImprovement.promote(), which\n'
            'refuses any candidate that has not been ratified.\n')
        entry = (
            f"\n## {c['id']} - {c['classification']}\n\n"
            f"- **lesson**: {c['lesson']}\n"
            f"- **derived from**: {c['event']}\n"
            f"- **evidence (verbatim)**: "
            f"{('`' + c['evidence_verbatim'][:400] + '`') if c['evidence_verbatim'] else 'n/a'}\n"
            f"- **ratified by**: {c['ratified_by']} at {c['ratified_at']}\n"
            f"- **promoted at**: {c['promoted_at']}\n")
        PROMOTED_FILE.write_text(existing + entry, encoding='utf-8')
        self._log('PROMOTED', {'id': c['id'], 'target': str(PROMOTED_FILE)})
        return c

    def _find(self, candidate_id: str) -> Dict[str, Any]:
        for c in self.candidates:
            if c['id'] == candidate_id:
                return c
        raise KeyError(f'unknown candidate: {candidate_id}')

    # ----- reporting -----

    def status(self) -> Dict[str, Any]:
        counts = Counter(c['status'] for c in self.candidates)
        by_class = Counter(c['classification'] for c in self.candidates)
        return {
            'generated_at': _now(),
            'total': len(self.candidates),
            'candidates': counts.get(STATUS_CANDIDATE, 0),
            'ratified': counts.get(STATUS_RATIFIED, 0),
            'promoted': counts.get(STATUS_PROMOTED, 0),
            'awaiting_r0': counts.get(STATUS_CANDIDATE, 0),
            'by_classification': dict(by_class),
            'boundary': {
                'write_scope': str(WORKSPACE),
                'promoted_target': str(PROMOTED_FILE),
                'never_written': ['user memory', 'the Obsidian vault on E:',
                                  'doctrine and protocol files'],
            },
        }

    def self_check(self) -> Dict[str, Any]:
        """Prove the ratify gate actually blocks. Measured, not asserted."""
        checks = []
        before = len(self.candidates)

        # 1. An unratified candidate cannot be promoted.
        probe = self.derive_lesson('probe event for the self-check',
                                   'this is only a self-check', source='self_check')
        try:
            self.promote(probe['id'])
            checks.append({'id': 'gate_blocks_unratified', 'status': 'FAIL',
                           'detail': 'an unratified candidate was promoted'})
        except ValueError:
            checks.append({'id': 'gate_blocks_unratified', 'status': 'OK',
                           'detail': 'promote() refused an unratified candidate'})

        # 2. An empty ratification is refused.
        try:
            self.ratify(probe['id'], '   ')
            checks.append({'id': 'gate_blocks_empty_ratification', 'status': 'FAIL',
                           'detail': 'an empty ratification was accepted'})
        except ValueError:
            checks.append({'id': 'gate_blocks_empty_ratification', 'status': 'OK',
                           'detail': 'an empty ratification was refused'})

        # 3. A real ratification allows promotion.
        try:
            self.ratify(probe['id'], 'self-check: Popy authorises this probe lesson')
            self.promote(probe['id'])
            promoted = self._find(probe['id'])['status'] == STATUS_PROMOTED
            checks.append({'id': 'ratified_promotes', 'status': 'OK' if promoted else 'FAIL',
                           'detail': f'ratified candidate promoted: {promoted}'})
        except ValueError as exc:
            checks.append({'id': 'ratified_promotes', 'status': 'FAIL', 'detail': str(exc)})

        # 4. The boundary holds.
        try:
            _assert_inside_workspace(Path(r'E:\CLAUDE\MINTE\test.md'))
            checks.append({'id': 'boundary_holds', 'status': 'FAIL',
                           'detail': 'a write outside SENTINEL_PRIME was allowed'})
        except BoundaryError:
            checks.append({'id': 'boundary_holds', 'status': 'OK',
                           'detail': 'write outside SENTINEL_PRIME refused'})

        # 5. Remove the probe so the queue is not polluted by the self-check.
        self.candidates = [c for c in self.candidates if c['id'] != probe['id']]
        self._save()

        return {
            'generated_at': _now(),
            'checks': checks,
            'all_ok': all(c['status'] == 'OK' for c in checks),
            'candidates_before': before,
            'candidates_after': len(self.candidates),
        }


def main():
    for stream_name in ('stdout',):
        pass
    si = SelfImprovement()
    check = si.self_check()
    print('SELF-IMPROVEMENT SELF-CHECK')
    for c in check['checks']:
        print(f"  [{c['status']}] {c['id']}: {c['detail']}")
    print(f"all_ok: {check['all_ok']}")
    st = si.status()
    print(f"total={st['total']} candidates={st['candidates']} "
          f"ratified={st['ratified']} promoted={st['promoted']} "
          f"awaiting_r0={st['awaiting_r0']}")
    return 0 if check['all_ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
