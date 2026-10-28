#!/usr/bin/env python3
"""
ACT VIII - run the extraction paths against REAL fixtures.

Why this exists: every multimodal path was proven only by "installed and
importable". An installed library is a claim about a package, not about the
code path that calls it. This runs the actual processors over real files from
Popy's own SENTINEL media library and records what actually came back.

Rules this harness obeys:
  * Real fixtures only. Never synthesise a file to make a path look proven.
  * A format with no available real fixture is reported NOT_RUN. It is never
    reported PASS and never reported FAIL -- those are different claims.
  * Every number printed is measured, not expected.
  * stdout is reconfigured to UTF-8. The fixtures carry Romanian diacritics in
    their filenames and content, and cp1252 raises UnicodeEncodeError on them.
  * Read-only against D:. Nothing outside SENTINEL_PRIME is written.
"""
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# The cp1252 trap, fixed before anything prints. Three separate paths died on
# this during the build; this is the guard for the fourth.
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, str(Path(__file__).parent))
from multimodal_processor import MultiModalProcessor  # noqa: E402

WORKSPACE = Path(__file__).resolve().parent.parent
EVIDENCE = WORKSPACE / '09_LOGS' / 'real_extraction_evidence.json'
MEDIA_ROOT = Path(r'D:\Alex_Knowlege_Vault\03_Resources\03_7-SENTINEL_Character')

# Real fixtures, chosen for cost. The video is 5.0 s; the audio is 10.9 min.
# Both are genuine files from Popy's library, unmodified and read-only.
FIXTURES = {
    'document': [
        # A real manual that carries Romanian diacritics in prose.
        WORKSPACE / '01_FOUNDATION' / 'doctrine' / 'A_FI_DOCTRINE.md',
    ],
    'video': [
        MEDIA_ROOT / 'BRAIN' / 'VIDEOS - Sentinel Brain' /
        '05e3d85a-a649-43a2-99a4-9024db8525ae.mp4',
    ],
    'audio': [
        # The filename itself carries Romanian diacritics, so it is written with
        # escapes. The language law is "code is English; wisdom is Romanian":
        # a .py file must contain zero Romanian diacritics, and the monitor's
        # code_no_romanian check enforces it. These escapes resolve to the exact
        # same string, so the path is unchanged and the source stays ASCII.
        MEDIA_ROOT / 'AUDIO' / 'Logica_proverbelor_rom'
        '\u00e2ne\u0219ti_\u00een_sistemul_Optimus.m4a',
    ],
}

# Declared by the processor's DOC_FORMATS, but no real file of these kinds was
# found in the accessible registries. Reported NOT_RUN, never PASS.
NO_FIXTURE_AVAILABLE = ['.pdf', '.docx', '.xlsx', '.pptx']


def probe_duration(path):
    """Measure duration independently, so the claim is not the caller's."""
    try:
        out = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
             '-of', 'default=noprint_wrappers=1:nokey=1', '--', str(path)],
            capture_output=True, text=True, encoding='utf-8', errors='replace',
            timeout=60)
        return round(float(out.stdout.strip()), 2)
    except Exception as e:
        return f'NOT_MEASURED ({e})'


def main():
    print('=' * 78)
    print('ACT VIII - REAL-FIXTURE EXTRACTION PROOF')
    print('  A capability is proven when the code path runs on real data.')
    print('=' * 78)

    proc = MultiModalProcessor()
    evidence = {
        'generated_at': datetime.now().isoformat(),
        'purpose': 'run extraction paths against real files, not synthetic ones',
        'fixtures_root': str(MEDIA_ROOT),
        'results': [],
        'no_real_fixture': NO_FIXTURE_AVAILABLE,
    }

    for kind, paths in FIXTURES.items():
        for p in paths:
            if not p.exists():
                print(f'\n[{kind.upper()}] NOT_RUN - fixture absent: {p.name}')
                evidence['results'].append({
                    'type': kind, 'fixture': str(p), 'status': 'NOT_RUN',
                    'reason': 'fixture file not found on disk',
                })
                continue

            size = p.stat().st_size
            print(f'\n[{kind.upper()}] {p.name}')
            print(f'  bytes   : {size:,}')
            print(f'  detected: {proc.detect_type(str(p))}')
            if kind in ('audio', 'video'):
                print(f'  duration: {probe_duration(p)}s (measured by ffprobe)')

            try:
                if kind == 'document':
                    r = proc.process_document(str(p))
                elif kind == 'audio':
                    r = proc.process_audio(str(p))
                else:
                    r = proc.process_video(str(p))
            except Exception as e:
                print(f'  RAISED  : {type(e).__name__}: {e}')
                evidence['results'].append({
                    'type': kind, 'fixture': str(p), 'status': 'ERROR',
                    'error': f'{type(e).__name__}: {e}',
                })
                continue

            # Report what the code path actually returned, not what it should.
            print(f'  status  : {r.get("status")}')
            for field in ('text_length', 'duration', 'language',
                          'language_probability', 'fps', 'frames_extracted',
                          'page_count', 'structure'):
                if r.get(field) not in (None, '', {}):
                    print(f'  {field:<22}: {r[field]}')

            text = r.get('transcription') or r.get('audio_transcription') \
                or r.get('text_extracted') or ''
            if text:
                sample = ' '.join(str(text).split())[:180]
                print(f'  text sample          : {sample}')

            if r.get('error'):
                print(f'  error   : {r["error"]}')

            rec = {k: v for k, v in r.items()
                   if k not in ('text_extracted', 'transcription',
                                'audio_transcription')}
            rec['text_chars_returned'] = len(text)
            rec['text_sample'] = ' '.join(str(text).split())[:180]
            rec['type'] = kind
            rec['fixture'] = str(p)
            evidence['results'].append(rec)

    print('\n' + '=' * 78)
    print('NOT_RUN (declared by the processor, no real file available):')
    for ext in NO_FIXTURE_AVAILABLE:
        print(f'  {ext:<8} no real fixture in the accessible registries')
    print('These are unproven. Not PASS. Not FAIL. Not claimed.')
    evidence['note_not_run'] = (
        'These formats have no real fixture available, so the path is unproven. '
        'Reported NOT_RUN rather than assumed working.')

    EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE.write_text(json.dumps(evidence, indent=2, ensure_ascii=False),
                        encoding='utf-8')
    print(f'\nevidence: {EVIDENCE}')

    ok = [r for r in evidence['results'] if r.get('status') == 'OK']
    err = [r for r in evidence['results'] if r.get('status') in ('ERROR', 'PARTIAL')]
    nr = [r for r in evidence['results'] if r.get('status') == 'NOT_RUN']
    print(f'\nRESULT: {len(ok)} OK, {len(err)} ERROR/PARTIAL, {len(nr)} NOT_RUN '
          f'(+ {len(NO_FIXTURE_AVAILABLE)} formats with no fixture)')
    print('=' * 78)
    return 0 if (ok and not err) else 1


if __name__ == '__main__':
    sys.exit(main())
