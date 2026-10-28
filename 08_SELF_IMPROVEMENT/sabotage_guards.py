"""Sabotage harness: do the repaired guards actually catch the verifier's defeats?

Each mutation reintroduces a real defect, the suite is run, and the run is
judged. CAUGHT means the suite went red or reported the class as PARTIAL / NOT
RUN. A mutation that still reports PASS is a live hole in the guard.

Every mutation is reverted in a finally block. If this script dies mid-run the
files are still restored, because restore is not conditional on success.

Run:  python 09_LOGS\\sabotage_round3.py
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(r'C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\SENTINEL_PRIME')
SUITE = ROOT / '08_SELF_IMPROVEMENT' / 'test_suite.py'
INDEX = ROOT / '13_COMMAND_CENTER' / 'index.html'
PY = r'C:\Users\apviz\AppData\Local\Python\pythoncore-3.14-64\python.exe'


def run_suite():
    """Return (exit_code, combined_output)."""
    p = subprocess.run([PY, str(SUITE)], cwd=str(SUITE.parent),
                       capture_output=True, text=True, encoding='utf-8',
                       errors='replace', timeout=900)
    return p.returncode, (p.stdout or '') + (p.stderr or '')


def verdict_of(out, class_name):
    """Pull one class's reported status out of the run output."""
    m = re.search(r'=== ' + re.escape(class_name) + r' ===\s*\nStatus: (\w+)', out)
    return m.group(1) if m else 'ABSENT'


# (id, description, file, old, new, class to inspect)
MUTATIONS = [
    ('S1', 'crash mid-test: remove the boot marker so src.rindex raises',
     SUITE,
     "src.rindex('/* ---------- boot ---------- */')",
     "src.rindex('/* ---------- this marker was deleted ---------- */')",
     'DashboardBoot'),

    ('S2', 'visibility:hidden on the active panel (blank page, old guard missed)',
     INDEX,
     '.panel.active{display:block}',
     '.panel.active{display:block}\nsection.panel.active{visibility:hidden}',
     'DashboardBoot'),

    ('S3', 'opacity:0 on the active panel (blank page, old guard missed)',
     INDEX,
     '.panel.active{display:block}',
     '.panel.active{display:block}\nsection.panel.active{opacity:0}',
     'DashboardBoot'),

    ('S4', 'color:transparent on every panel (old guard missed)',
     INDEX,
     '.panel.active{display:block}',
     '.panel.active{display:block}\nsection.panel{color:transparent}',
     'DashboardBoot'),

    ('S5', 'String(wired.value) in the wiring PROSE (verifier M11)',
     INDEX,
     "+ 'sentinel-hub over stdio: ' + wired.value.tools_over_the_wire + ' tools came back on '",
     "+ 'sentinel-hub over stdio: ' + String(wired.value) + ' tools came back on '",
     'UiNoObjectCoercion'),
]

print('=' * 78)
print('SABOTAGE ROUND 3 - do the repaired guards catch the verifier defeats?')
print('=' * 78)

baseline_code, baseline_out = run_suite()
print(f'\nBASELINE: exit={baseline_code} '
      f'{re.search(r"TOTAL: .*", baseline_out).group(0) if re.search(r"TOTAL: .*", baseline_out) else ""}')
if baseline_code != 0:
    print('!! baseline is not green - the rest of this run is meaningless.')
    sys.exit(1)

results = []
for mid, desc, target, old, new, cls in MUTATIONS:
    original = target.read_text(encoding='utf-8')
    if old not in original:
        results.append((mid, 'SKIPPED', desc, 'mutation anchor not found'))
        print(f'\n[{mid}] SKIPPED - anchor not found: {desc}')
        continue
    try:
        target.write_text(original.replace(old, new, 1), encoding='utf-8')
        code, out = run_suite()
        status = verdict_of(out, cls)
        caught = (code != 0) or (status in ('FAIL', 'PARTIAL', 'NOT_RUN'))
        results.append((mid, 'CAUGHT' if caught else 'DEFEATED', desc,
                        f'exit={code} {cls}={status}'))
        print(f'\n[{mid}] {"CAUGHT" if caught else "*** DEFEATED ***"}: {desc}')
        print(f'      exit={code}  {cls}={status}')
        if not caught:
            for line in out.splitlines():
                if line.startswith('TOTAL:'):
                    print(f'      {line}')
    finally:
        target.write_text(original, encoding='utf-8')
        print('      (reverted)')

print('\n' + '=' * 78)
caught = sum(1 for r in results if r[1] == 'CAUGHT')
defeated = [r for r in results if r[1] == 'DEFEATED']
skipped = [r for r in results if r[1] == 'SKIPPED']
print(f'CAUGHT {caught}/{len(results)}   DEFEATED {len(defeated)}   SKIPPED {len(skipped)}')
for r in results:
    print(f'  {r[0]:4} {r[1]:9} {r[3]}')
print('=' * 78)

final_code, final_out = run_suite()
m = re.search(r'TOTAL: .*', final_out)
print(f'RESTORED: exit={final_code}  {m.group(0) if m else ""}')
sys.exit(1 if (defeated or final_code != 0) else 0)
