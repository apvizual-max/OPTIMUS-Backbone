"""Does the Tests panel actually SHOW a partial run, or only store it?

The collector fix carries `partial` / `not_run` / `green` into STATE.tests.
Carrying them is not the same as rendering them, and this is the exact
one-layer-down mistake that was already made twice in this build. So: plant a
partial record, collect, load the live page in Chromium, and read the text a
person would see.

The real last_test_run.json is saved and restored, and the collector is re-run
at the end, so the Command Center is never left displaying a fabricated run.
"""
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(r'C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\SENTINEL_PRIME')
API = ROOT / '13_COMMAND_CENTER' / 'api'
RUN_JSON = API / 'last_test_run.json'
COLLECT = API / 'collect-sentinel.ps1'
INDEX = ROOT / '13_COMMAND_CENTER' / 'index.html'
PY = r'C:\Users\apviz\AppData\Local\Python\pythoncore-3.14-64\python.exe'
URL = 'http://127.0.0.1:8910/'

BACKUP = RUN_JSON.with_suffix('.json.bak_probe')


def collect():
    return subprocess.run(['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass',
                    '-File', str(COLLECT)],
                   capture_output=True, text=True, timeout=300, check=True)


def read_tests_panel():
    """Open the live page, click the Tests tab, return what it shows."""
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        try:
            page = b.new_page()
            page.goto(URL, wait_until='domcontentloaded', timeout=30000)
            page.wait_for_timeout(1500)
            page.evaluate("""() => {
                const t = Array.from(document.querySelectorAll('[role=tab]'))
                    .find(e => /tests/i.test(e.textContent||''));
                if (t) t.click();
            }""")
            page.wait_for_timeout(900)
            return page.evaluate("""() => {
                const panel = document.getElementById('p-Tests');
                const vis = panel && getComputedStyle(panel).display !== 'none';
                // Read the verdict tile BY LABEL. The first version of this
                // probe substring-matched 'PASS' over the whole panel, which
                // fires on the tile LABEL "PASSED" - a blob match satisfied by
                // the wrong element, the same mistake the guard under test
                // exists to prevent.
                const tileVal = (label) => {
                  const t = Array.from(panel.querySelectorAll('.tile'))
                    .find(e => (e.querySelector('.k')||{}).textContent ===
                           label);
                  const v = t && t.querySelector('.v');
                  return v ? v.textContent.trim() : null;
                };
                return {
                    visible: !!vis,
                    height: panel ? Math.round(panel.getBoundingClientRect().height) : 0,
                    text: panel ? panel.innerText : '',
                    verdict: tileVal('Verdict'),
                    passed_label: tileVal('Passed'),
                };
            }""")
        finally:
            b.close()


def main():
    shutil.copy2(RUN_JSON, BACKUP)
    try:
        print('=' * 78)
        print('PARTIAL SURFACE PROOF - collector -> STATE -> rendered panel')
        print('=' * 78)

        real = json.loads(RUN_JSON.read_text(encoding='utf-8'))
        print(f'\nREAL run: passed={real["passed"]} failed={real["failed"]} '
              f'skipped={real["skipped"]} green={real["green"]} '
              f'partial={real["partial"]} not_run={real["not_run"]}')

        # --- 1. the honest run, as it stands -----------------------------
        collect()
        honest = read_tests_panel()
        print(f'\n--- HONEST RUN RENDERED (visible={honest["visible"]}, '
              f'{honest["height"]}px) ---')
        print('\n'.join('    ' + l for l in honest['text'].splitlines()[:14]))

        # --- 2. a planted partial run ------------------------------------
        planted = json.loads(json.dumps(real))
        planted['passed'] = 272
        planted['skipped'] = 2
        planted['green'] = False
        planted['partial'] = ['DashboardBoot', 'UiNoObjectCoercion']
        planted['not_run'] = ['BrowserAutomation']
        for c in planted['classes']:
            if c['name'] in planted['partial']:
                c['skipped'] = 1
                c['partial'] = True
            if c['name'] in planted['not_run']:
                c['passed'] = 0
                c['failed'] = 0
                c['not_run'] = True
        RUN_JSON.write_text(json.dumps(planted, indent=2), encoding='utf-8')
        collect()
        shown = read_tests_panel()
        print(f'\n--- PLANTED PARTIAL RUN RENDERED (visible={shown["visible"]}, '
              f'{shown["height"]}px) ---')
        print('\n'.join('    ' + l for l in shown['text'].splitlines()[:16]))

        text = shown['text']
        checks = [
            ('panel is visible', shown['visible'] and shown['height'] > 0),
            ('the Verdict tile is present', shown['verdict'] is not None),
            ('the Verdict tile is not PASS',
             shown['verdict'] not in (None, 'PASS')),
            ('the honest run rendered Verdict = PASS',
             honest['verdict'] == 'PASS'),
            ('the partial run names PARTIAL on screen', 'PARTIAL' in text),
            ('the partial run names NOT_RUN on screen', 'NOT_RUN' in text),
            ('the partial classes are named by name',
             'DashboardBoot' in text and 'UiNoObjectCoercion' in text),
            ('the unrun class is named', 'BrowserAutomation' in text),
        ]
        print(f'\n  Verdict tile - honest: {honest["verdict"]!r}   '
              f'planted partial: {shown["verdict"]!r}')
        print('\n--- ASSERTIONS ---')
        ok = True
        for name, passed in checks:
            print(f'  [{"PASS" if passed else "FAIL"}] {name}')
            ok = ok and passed
        return 0 if ok else 1
    finally:
        shutil.move(str(BACKUP), str(RUN_JSON))
        collect()
        print('\nreal last_test_run.json restored and re-collected.')


if __name__ == '__main__':
    sys.exit(main())
