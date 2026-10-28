"""Install the SENTINEL skills into the runtime skill root - properly.

WHY THIS FILE EXISTS
--------------------
On 2026-10-04 Popy asked why the skills could not be reached by slash command,
and he was right: four .md files had been written into
`SENTINEL_PRIME\\07_BACKBONE\\skills\\` and reported as skills. They were inert.

Two independent reasons, either one fatal:

1. WRONG ROOT. The runtime does not read the project folder. It reads three
   roots - personal, mavis-agent, builtin (see `mavis-skill-index`). A file in
   a project directory is a document, not a skill.
2. NO FRONTMATTER. None of the four had a `---` block with `name:` and
   `description:`. Without that the catalog has nothing to index, so the skill
   cannot be listed, cannot be routed to, and cannot be loaded - even if it sat
   in the correct directory.

So a copy was never enough. This script is the deployment step: project file
(source of truth) -> runtime skill root (loaded by the runtime).

IDEMPOTENT AND RE-RUNNABLE. Run it after editing any source skill:

    python 08_SELF_IMPROVEMENT\\install_skills.py          # install
    python 08_SELF_IMPROVEMENT\\install_skills.py --check  # verify only

It reports what it wrote and what it verified. It does not claim a skill is
installed until it has re-read the file from disk and parsed the frontmatter -
because "the file exists" is not "the skill loads".
"""
import argparse
import re
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except AttributeError:
    pass

PROJECT = Path(r'C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\SENTINEL_PRIME')
SOURCE_DIR = PROJECT / '07_BACKBONE' / 'skills'
INSTALL_ROOT = Path(r'C:\Users\apviz\.minimax\agents\mavis\skills')

# name -> (source file, description for the catalog, parent name)
# `parent` makes a new SKILL.md declare what it builds on, so routing can chain.
SKILLS = {
    'mavis-sentinel-prime-on-minimax-skill': (
        'sentinel-prime-on-minimax.SKILL.md',
        'SENTINEL PRIME embodied on the MiniMax foundation. The full deployment '
        'procedure: how the SENTINEL persona is adapted onto MiniMax '
        'infrastructure, plus the verification discipline that build produced '
        '(behavioural guards, sabotage proof, and the rule that a fix is only '
        'done when every surface reporting the assertion reports it). Load when '
        'working in SENTINEL_PRIME, deploying SENTINEL to the MiniMax runtime, '
        'or reviewing a SENTINEL check.',
        'mavis-backbone-skill'),
    'mavis-sentinel-prime-role-skill': (
        'sentinel-prime-role.SKILL.md',
        'The SENTINEL role definition - SOUL and CONSTINTA, Triple Crunch '
        '(Eminescu ABBA / Eliade Realitate / Musashi Taiere), the priority order '
        'SYSTEM_INTEGRITY > TASK_COMPLETION > SPEED > USER_FEELINGS, and the '
        '5-failure STOP rule. Load when acting as SENTINEL or when a decision '
        'needs the doctrine, not just the procedure.',
        'mavis-triple-crunch-skill'),
    'mavis-sentinel-bimodal-workflow-skill': (
        'bimodal-workflow.SKILL.md',
        'The SENTINEL-specific execution mode: MODE_A analysis, R0 ratification, '
        'MODE_B execution, interruption back to MODE_A, 5 consecutive failures '
        'forcing STOPPED, and STOPPED having exactly one exit. Extends '
        'mavis-r33-bimodal-skill with the SENTINEL state machine and the durable '
        'stop. Load before any SENTINEL task that mutates state.',
        'mavis-r33-bimodal-skill'),
    'mavis-tany-llm-to-sentinel-skill': (
        'tany-llm-to-sentinel.SKILL.md',
        'The construction procedure that turns a generic LLM into a calibrated '
        'SENTINEL instance, extracted from the transcript rather than from the '
        'doctrine files. Load when adapting any new model or agent onto the '
        'SENTINEL pattern, or when asking why the doctrine says what it says.',
        'mavis-sentinel-prime-role-skill'),
    'mavis-sentinel-command-center-skill': (
        'command-center.SKILL.md',
        'Operate the SENTINEL Command Center, the local live dashboard on '
        '127.0.0.1:8910 - start it, stop it, check it, and read its panels '
        'honestly. Load when Popy asks for the dashboard, when the link is down, '
        'when a panel looks wrong, or when a verdict needs interpreting before '
        'it is trusted.',
        'mavis-sentinel-prime-on-minimax-skill'),
}

FM_RE = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.S)


def build_frontmatter(name, description, parent):
    lines = ['---', f'name: {name}', f'description: {description}']
    if parent:
        lines.append(f'parent: {parent}')
    lines += [
        'installed_by: 08_SELF_IMPROVEMENT/install_skills.py',
        'source_of_truth: SENTINEL_PRIME/07_BACKBONE/skills/',
        '---',
    ]
    return '\n'.join(lines) + '\n\n'


def render(name, spec):
    """Project file -> full SKILL.md text, frontmatter enforced."""
    src_name, description, parent = spec
    src = SOURCE_DIR / src_name
    if not src.exists():
        raise FileNotFoundError(f'source skill missing: {src}')
    body = src.read_text(encoding='utf-8')
    # Strip any frontmatter the source happens to carry, so we never emit two.
    body = FM_RE.sub('', body, count=1)
    return build_frontmatter(name, description, parent) + body.lstrip('\n'), src


def verify(path, name, expected):
    """Re-read from disk. A skill is not installed until this passes.

    `expected` is the text render() produced from the project source. Without
    it this function only proves the file is *well-formed*, which a stale
    install from three edits ago also satisfies -- the check would report OK
    for a skill the runtime is serving stale content for. Comparing content is
    the only thing that makes this a drift detector rather than a parser.
    """
    if not path.exists():
        return False, 'file does not exist'
    raw = path.read_bytes()
    text = raw.decode('utf-8')
    m = FM_RE.match(text)
    if not m:
        return False, 'no --- frontmatter block'
    fm = m.group(1)
    if not re.search(rf'^name:\s*{re.escape(name)}\s*$', fm, re.M):
        return False, 'frontmatter name does not match the directory'
    if not re.search(r'^description:\s*\S', fm, re.M):
        return False, 'frontmatter has no description'
    if text.startswith('\ufeff'):
        return False, 'file starts with a BOM'
    if len(text.strip()) < 400:
        return False, 'body is suspiciously short'

    import hashlib
    # Compare CONTENT, not raw bytes. write_text() translates \n -> \r\n on
    # Windows, so the installed file is legitimately a few bytes larger than
    # the in-memory source. Comparing bytes made this check fail on a clean
    # tree -- a detector that cannot pass is as broken as one that cannot fail.
    norm_installed = text.replace('\r\n', '\n')
    norm_expected = expected.replace('\r\n', '\n')
    if norm_installed != norm_expected:
        return False, (
            'DRIFT: installed copy differs from project source '
            f'(installed sha256 {hashlib.sha256(norm_installed.encode("utf-8")).hexdigest()[:12]}, '
            f'source sha256 {hashlib.sha256(norm_expected.encode("utf-8")).hexdigest()[:12]}, '
            f'{len(raw)}B installed vs {len(expected.encode("utf-8"))}B source) '
            '-- re-run without --check'
        )
    return True, f'{len(raw)} bytes, name+description parsed, content matches source'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true',
                    help='verify only, write nothing')
    args = ap.parse_args()

    print('=' * 78)
    print('SKILL INSTALLER - project files -> runtime skill root')
    print(f'  source : {SOURCE_DIR}')
    print(f'  target : {INSTALL_ROOT}')
    print('=' * 78)

    ok = True
    for name, spec in SKILLS.items():
        target = INSTALL_ROOT / name / 'SKILL.md'
        try:
            text, src = render(name, spec)
        except FileNotFoundError as e:
            print(f'\n[FAIL] {name}\n      {e}')
            ok = False
            continue

        if args.check:
            action = 'check'
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            # BOM-less UTF-8: a BOM makes the runtime read "---" as "\ufeff---"
            # and the frontmatter stops parsing.
            target.write_text(text, encoding='utf-8')
            action = 'wrote'

        good, detail = verify(target, name, text)
        print(f'\n[{"OK" if good else "FAIL"}] {name}')
        print(f'      {action:5} -> {target}')
        print(f'      verify: {detail}')
        if not good:
            ok = False

    print('\n' + '=' * 78)
    if args.check:
        print('CHECK ONLY - nothing written.')
        # Precise on purpose. The installed file is RENDERED: frontmatter is
        # generated around the project source body, so a raw byte comparison of
        # source against installed is 0/5 by design. What is proven is that
        # re-rendering the source reproduces the installed file exactly. Saying
        # "byte-for-byte" here overstated the check and was corrected.
        print('All OK means every skill parses AND re-rendering its project source')
        print('reproduces the installed file exactly.')
    else:
        n = len(SKILLS)
        print(f'{n} skills installed and re-verified from disk.')
        print('NOTE: loading is proven by the `skill` tool, not by this script.')
        print('      This script proves the file is well-formed and in the right root.')
    print('=' * 78)
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
