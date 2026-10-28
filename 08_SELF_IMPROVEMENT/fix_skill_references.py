"""Repair the stale self-references inside the SENTINEL skill sources.

WHY
---
On 2026-10-04 the four skills were installed into the runtime skill root for
the first time. Loading them immediately exposed a second class of defect that
a file-existence check could never have found: the bodies referred to each
other by names that do not exist.

    skill(name="bimodal-workflow")      ->  no such skill; the installed name
                                            is mavis-sentinel-bimodal-workflow-skill

A skill that tells the reader to invoke a name the runtime cannot resolve is
a pointer to nowhere - the same "path exists, target does not" shape as the
Command Center link Popy lost. It only became visible because the skills were
loaded rather than listed.

It also surfaced two stale figures: "279 assertions", superseded when the
crash-reporting fix landed (now 288).

Every replacement below is an exact literal pair, and the script prints what it
changed. It is idempotent: a second run finds no anchors and reports SKIP.
"""
import pathlib
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except AttributeError:
    pass

SRC = pathlib.Path(
    r'C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\SENTINEL_PRIME\07_BACKBONE\skills')

B = chr(96)  # backtick, kept out of the literals so nothing has to escape it

FIX = [
    ('bimodal-workflow.SKILL.md',
     'skill(name="bimodal-workflow")',
     'skill(name="mavis-sentinel-bimodal-workflow-skill")',
     'self-reference to a name the runtime cannot resolve'),
    ('bimodal-workflow.SKILL.md',
     'see ' + B + 'sentinel-prime-on-minimax.SKILL.md' + B,
     'see ' + B + 'mavis-sentinel-prime-on-minimax-skill' + B,
     'stale sibling filename'),
    ('tany-llm-to-sentinel.SKILL.md',
     '**' + B + 'sentinel-prime-on-minimax.SKILL.md' + B + '**',
     '**' + B + 'mavis-sentinel-prime-on-minimax-skill' + B + '**',
     'stale sibling filename'),
    ('sentinel-prime-on-minimax.SKILL.md',
     '**Skill:** ' + B + 'sentinel-prime-on-minimax' + B,
     '**Installed as:** ' + B + 'mavis-sentinel-prime-on-minimax-skill' + B,
     'declares a name the runtime cannot load'),
    ('sentinel-prime-on-minimax.SKILL.md',
     B + 'tany-llm-to-sentinel' + B + ' teaches',
     'The ' + B + 'mavis-tany-llm-to-sentinel-skill' + B + ' teaches',
     'stale sibling name'),
    ('sentinel-prime-on-minimax.SKILL.md',
     '| ' + B + 'test_suite.py' + B + ' | 279 assertions |',
     '| ' + B + 'test_suite.py' + B + ' | 288 assertions |',
     'stale figure after the crash-reporting fix'),
    ('sentinel-prime-role.SKILL.md',
     '**' + B + 'sentinel-prime-on-minimax.SKILL.md' + B + '** - the embodiment',
     '**' + B + 'mavis-sentinel-prime-on-minimax-skill' + B + '** - the embodiment',
     'stale sibling filename'),
    ('sentinel-prime-role.SKILL.md',
     '**279 assertions, 0 failed, 0 skipped**',
     '**288 assertions, 0 failed, 0 skipped**',
     'stale figure'),
    ('sentinel-prime-role.SKILL.md',
     '**Load ' + B + 'sentinel-prime-on-minimax' + B + ' when',
     '**Load ' + B + 'mavis-sentinel-prime-on-minimax-skill' + B + ' when',
     'stale skill name in prose'),
]


def main():
    print('=' * 78)
    print('STALE SELF-REFERENCE REPAIR - project skill sources')
    print('=' * 78)
    fixed = skipped = 0
    for fn, old, new, why in FIX:
        p = SRC / fn
        text = p.read_text(encoding='utf-8')
        if old not in text:
            print(f'\n[SKIP] {fn}\n      anchor absent: {why}')
            skipped += 1
            continue
        count = text.count(old)
        p.write_text(text.replace(old, new), encoding='utf-8')
        print(f'\n[FIX ] {fn}  ({count} replacement{"" if count == 1 else "s"})\n'
              f'      {why}\n      {old[:60]}\n   -> {new[:60]}')
        fixed += 1
    print(f'\n{"=" * 78}\n{fixed} fixed, {skipped} already absent.')
    print('Re-run install_skills.py to push the repairs into the runtime root.')
    print('=' * 78)
    return 0


if __name__ == '__main__':
    sys.exit(main())
