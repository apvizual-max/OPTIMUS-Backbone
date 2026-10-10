#!/usr/bin/env python3
"""
`git` - read-only git inspection for SENTINEL_PRIME.

Declared in OPTIMUS_MCP_CONFIG.json as: "Git operations pentru /checkpoint",
with `GIT_DIR` pointing at the SENTINEL_PRIME workspace root.

Why this file exists
--------------------
The config declared this server as `npx -y @modelcontextprotocol/server-git`.
That package returns HTTP 404 from the npm registry - measured 2026-10-10:

    @modelcontextprotocol/server-git  -> 404
    mcp-server-git                   -> 200, but dist-tag latest = 0.0.1-security

`0.0.1-security` is npm's placeholder for a squatted/unpublished name. Using it
would have turned a red health check green over a package that does nothing.

The declaration is also wrong in a second, quieter way, and this server is built
so that the error is visible rather than hidden. Measured 2026-10-10:

    git rev-parse --is-inside-work-tree   (in SENTINEL_PRIME)
      -> exit 128, "fatal: not a git repository"

There is no `.git` in SENTINEL_PRIME. So the declared `GIT_DIR` points at a
directory that is not a repository, and any "git status" a client asked for
would have had nothing true to say. This server says so explicitly, naming the
measured `rev-parse` output, instead of returning an empty change list that
reads like "clean working tree".

That is a real gap in the project (SENTINEL_PRIME is not under version control),
and it is Popy's to close - not something a monitoring check may paper over.

Read-only by construction
-------------------------
Only inspection subcommands are reachable: status, log, diff, branch, show,
rev-parse, ls-files. There is no commit, add, checkout, merge, reset, push or
fetch path in this file, so the config's own `security.no_force_push: true` and
`approval_required_for: ["force_push"]` cannot be violated from here. Every repo
path is resolved and confined to the workspace root.
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Annotated, List, Optional

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from pydantic import Field

_DEFAULT = r"C:\Users\apviz\.minimax-agent\projects\SENTINEL_PRIME"
ROOT = Path(os.environ.get('GIT_DIR')
            or os.environ.get('WORKSPACE_ROOT')
            or _DEFAULT).resolve()

MAX_LOG = 500
MAX_DIFF_BYTES = 200_000
MAX_PATHS = 300

# The complete set of subcommands this server may execute. Anything not in
# this tuple is not merely unused - it cannot be reached.
ALLOWED_SUBCOMMANDS = frozenset({
    'status', 'log', 'diff', 'branch', 'show', 'rev-parse', 'ls-files',
})

SKIP_DIRS = {'.git', 'node_modules', '__pycache__', '.venv', 'site-packages'}

# Belt and braces for the `--output` write primitive above. `_safe_token` guards
# the call sites; this guards argv itself, so a future tool added to this file
# cannot reintroduce the same write primitive by forgetting to call it.
# Every option this module is allowed to pass is enumerated here. Anything else
# beginning with '-' is refused before git ever sees it.
SAFE_LITERAL_OPTIONS = frozenset({
    '--no-color', '--stat', '--cached', '--', '--porcelain=v1', '--branch',
    '--is-inside-work-tree', '--abbrev-ref',
})
SAFE_LITERAL_PREFIXES = ('--max-count=', '--pretty=format:', '--format=')

server = MCPServer('git-tools', version='1.0.0')


def _inside(candidate: str) -> Path:
    """Resolve a repo path and refuse anything outside the workspace root."""
    path = Path(candidate)
    resolved = (path if path.is_absolute() else ROOT / path).resolve()
    if resolved != ROOT and ROOT not in resolved.parents:
        raise ToolError(
            f'refused: {candidate} resolves outside the workspace root {ROOT}')
    return resolved


def _run(repo: Path, args: List[str], timeout: int = 30) -> subprocess.CompletedProcess:
    """Run one allowed read-only git subcommand in `repo`."""
    if not args:
        raise ToolError('no git subcommand given')
    sub = args[0]
    if sub not in ALLOWED_SUBCOMMANDS:
        raise ToolError(
            f'refused: {sub!r} is not a read-only inspection subcommand. '
            f'Allowed: {sorted(ALLOWED_SUBCOMMANDS)}')
    if not shutil_which_git():
        raise ToolError('git executable not found on PATH')
    for token in args[1:]:
        if not str(token).startswith('-'):
            continue
        if (str(token) in SAFE_LITERAL_OPTIONS
                or any(str(token).startswith(p) for p in SAFE_LITERAL_PREFIXES)):
            continue
        raise ToolError(
            f'refused: {token!r} is not an option this server is allowed to pass. '
            f'This server is read-only by construction, so an unrecognised '
            f'option is refused rather than forwarded: git options such as '
            f'--output=<path> let the caller write or truncate files.')
    try:
        return subprocess.run(
            ['git', '-C', str(repo)] + args,
            capture_output=True, text=True, timeout=timeout,
            encoding='utf-8', errors='replace', env=_child_env())
    except subprocess.TimeoutExpired as exc:
        raise ToolError(f'git {sub} timed out after {timeout}s in {repo}') from exc
    except OSError as exc:
        raise ToolError(f'could not run git in {repo}: {exc}') from exc


def shutil_which_git() -> Optional[str]:
    from shutil import which
    return which('git')


# Git's own environment variables redirect where git looks for the repository.
# Measured 2026-10-10, this server had its own bug because of exactly this:
# it forwarded the configured GIT_DIR into every child process, and git read
# that value as "this IS the .git directory" rather than "the work tree is
# here". Proof, same repo, three invocations:
#
#     (no GIT_DIR)                      -> true,  exit 0
#     GIT_DIR=<worktree root>           -> fatal: not a git repository, 128
#     GIT_DIR=<worktree>/.git           -> true,  exit 0
#
# Every valid repo I tested was reported as "not a repository" until this was
# removed. A leaked GIT_DIR does not degrade the result, it destroys it - and
# it fails toward "not a repository", which looks like a data problem rather
# than a wiring one.
#
# Note the middle row is also the shape of the value in
# OPTIMUS_MCP_CONFIG.json: "GIT_DIR": "<workspace root>", i.e. a work tree
# path, not a .git path. That entry is malformed by this definition
# independently of whether the workspace is a repository at all.
GIT_ENV_VARS = ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE',
                'GIT_OBJECT_DIRECTORY', 'GIT_COMMON_DIR', 'GIT_ALTERNATE_OBJECT_DIRECTORIES',
                'GIT_NAMESPACE')


def _child_env() -> dict:
    """The parent environment with git's redirection variables removed."""
    return {k: v for k, v in os.environ.items() if k not in GIT_ENV_VARS}


# CRITICAL, found by verifier 2026-10-10: `ALLOWED_SUBCOMMANDS` gates the
# SUBCOMMAND, not the arguments, and that was not enough to make this server
# read-only. `git_diff(ref=...)` was appended to argv unvalidated, so
#
#     git_diff(ref="--output=C:\\somewhere\\file.txt")
#
# made git CREATE that file, and truncate an existing 42-byte file to 0 bytes,
# while reporting is_error=false. `git_show(revision=...)` had the same shape.
# The subcommand allowlist said "diff" and was satisfied; the write happened in
# an option nobody inspected.
#
# Git's own model: a token beginning with '-' is an OPTION, not a value. So any
# caller-supplied text is refused outright if it could be read as one. The
# literals this module builds itself (`--no-color`, `--pretty=...`) are not
# caller text and are unaffected.
_SAFE_TOKEN = re.compile(r'^[A-Za-z0-9][A-Za-z0-9._/~^@{}+-]*$')


def _safe_token(value: str, field: str) -> str:
    """Refuse caller text that git could parse as an option or a redirect."""
    text = str(value).strip()
    if not text:
        raise ToolError(f'{field} must not be empty')
    if text.startswith('-'):
        raise ToolError(
            f'refused: {field}={value!r} starts with "-", which git reads as an '
            f'OPTION rather than a value. This server passes no caller text to '
            f'git without this check, because options like --output=<path> let '
            f'the caller write or truncate files while this server claims to be '
            f'read-only.')
    if '=' in text:
        raise ToolError(
            f'refused: {field}={value!r} contains "=", which git also uses to '
            f'pass option values (--output=<path>).')
    if not _SAFE_TOKEN.match(text):
        raise ToolError(
            f'refused: {field}={value!r} is not a plain git revision. Allowed '
            f'characters are letters, digits and . _ / ~ ^ @ {{ }} + - , and it '
            f'may not begin with "-" or contain "=".')
    return text


def _require_repo(repo: Path) -> None:
    """Fail loudly and specifically when `repo` is not a git repository.

    This is the case the declaration hides. `git status` in a non-repository
    exits 128; the empty stdout of that failure is exactly what an unchanged
    working tree looks like, so the check below refuses to let the two be
    confused.
    """
    if not (repo / '.git').exists():
        probe = _run(repo, ['rev-parse', '--is-inside-work-tree'])
        if probe.returncode != 0:
            raise ToolError(
                f'{repo} is not a git repository (git rev-parse exit '
                f'{probe.returncode}: '
                f'{(probe.stderr or probe.stdout).strip()}). No status, log or '
                f'diff exists to report. Returning an empty list here would be '
                f'indistinguishable from a clean tree, so this refuses instead.')
    probe = _run(repo, ['rev-parse', '--is-inside-work-tree'])
    if probe.returncode != 0:
        raise ToolError(
            f'{repo} has a .git entry but git does not recognise it as a work '
            f'tree (git rev-parse exit {probe.returncode}: '
            f'{(probe.stderr or probe.stdout).strip()}). Treating that as an '
            f'empty repository would report a clean tree that was never '
            f'inspected.')


def _inside_repo(repo: Path, candidate: str) -> Path:
    """Resolve a path RELATIVE TO THE REPO, and refuse anything outside it.

    This is separate from `_inside` on purpose. `_inside` resolves against the
    workspace ROOT, which is correct for choosing WHICH repository to look at.
    It is wrong for `path_filter`: git runs with the repository as its working
    directory, so a pathspec is interpreted relative to the REPO, not to the
    workspace. Resolving the filter against the root meant that for every
    repository below the root the filter pointed somewhere git could not match,
    and `git log` failed outright. `path_filter` could therefore only ever work
    when repo == root, which is not the case this server is used in.
    """
    path = Path(candidate)
    resolved = (repo / path).resolve()
    if resolved != repo and repo not in resolved.parents:
        raise ToolError(
            f'refused: path_filter {candidate} resolves outside the repository '
            f'{repo}')
    return resolved


def _capped(text: str, cap: int) -> dict:
    body = text if len(text) <= cap else text[:cap]
    return {
        'text': body,
        'chars_total': len(text),
        'chars_returned': len(body),
        'truncated': len(text) > cap,
        'truncated_note': (f'capped at {cap} characters of {len(text)}'
                           if len(text) > cap else 'complete output'),
    }


@server.tool()
def git_discover() -> str:
    """Report whether the configured root is a git repository, and where repos are."""
    root_is_repo = (ROOT / '.git').exists()
    root_probe = _run(ROOT, ['rev-parse', '--is-inside-work-tree'])
    found: List[str] = []
    truncated = False
    for path in sorted(ROOT.rglob('.git')):
        # Skip build noise in the ANCESTORS only. Testing the full path against
        # SKIP_DIRS - which contains '.git', because that is what we are
        # searching for - discarded every hit and made this tool report zero
        # repositories on a workspace that had one. A filter that removes the
        # thing it is looking for is a filter that always returns "not found".
        ancestor_parts = set(path.parent.relative_to(ROOT).parts)
        if ancestor_parts & SKIP_DIRS:
            continue
        found.append(str(path.parent.relative_to(ROOT)))
        if len(found) >= MAX_PATHS:
            truncated = True
            break
    return json.dumps({
        'configured_root': str(ROOT),
        'root_has_dot_git': root_is_repo,
        'root_is_inside_work_tree': root_probe.stdout.strip() == 'true',
        'root_rev_parse_exit': root_probe.returncode,
        'root_rev_parse_stderr': (root_probe.stderr or '').strip() or None,
        'repositories_found': len(found),
        'repositories_truncated': truncated,
        'repositories_truncated_note': (
            f'capped at {MAX_PATHS} repositories' if truncated
            else 'complete scan'),
        'repositories': found,
        'verdict': ('root is a git repository' if root_is_repo else
                    'root is NOT a git repository - SENTINEL_PRIME is not under '
                    'version control, so git tools here have nothing true to say '
                    'about it'),
    }, indent=2)


@server.tool()
def git_status(
    repo: Annotated[str, Field(description=(
        'Repository path, workspace-relative or absolute. Defaults to the '
        'configured root.'))] = '.',
) -> str:
    """Show porcelain working-tree status for a repository."""
    target = _inside(repo)
    _require_repo(target)
    result = _run(target, ['status', '--porcelain=v1', '--branch'])
    if result.returncode != 0:
        raise ToolError(f'git status failed in {target}: {result.stderr.strip()}')
    lines = [ln for ln in result.stdout.splitlines() if ln.strip()]
    return json.dumps({
        'repo': str(target),
        'clean': not any(not ln.startswith('##') for ln in lines),
        'branch_line': next((ln for ln in lines if ln.startswith('##')), None),
        'changed_count': sum(1 for ln in lines if not ln.startswith('##')),
        'entries': lines,
    }, indent=2)


@server.tool()
def git_log(
    repo: Annotated[str, Field(description=(
        'Repository path. Defaults to the configured root.'))] = '.',
    limit: Annotated[int, Field(description=(
        f'Maximum commits. Capped at {MAX_LOG}. Defaults to 20.'))] = 20,
    path_filter: Annotated[Optional[str], Field(description=(
        'Optional path to restrict the log to.'))] = None,
) -> str:
    """Show recent commits, newest first."""
    target = _inside(repo)
    _require_repo(target)
    args = ['log', f'--max-count={max(1, min(int(limit), MAX_LOG))}',
            '--pretty=format:%H%x1f%an%x1f%aI%x1f%s']
    if path_filter:
        # It is placed after `--`, so git reads it as a pathspec and never as an
        # option - which is why a value like "--output=x" is inert here even
        # though it is refused for `ref`. A leading '-' is still refused, as
        # cheap defence in depth, WITHOUT applying _safe_token: a legitimate
        # Windows path here can contain spaces and backslashes that _safe_token
        # would reject, and tightening it would break real use to defend
        # against something that is already unreachable.
        if str(path_filter).lstrip().startswith('-'):
            raise ToolError(
                f'refused: path_filter={path_filter!r} starts with "-", which '
                f'git could read as an option. It is passed after "--" so it is '
                f'treated as a pathspec, and this check is belt and braces.')
        # after '--' git treats this as a pathspec, but it is still caller text
        # and still confined to the repository.
        args += ['--', str(_inside_repo(target, path_filter))]
    result = _run(target, args)
    if result.returncode != 0:
        raise ToolError(f'git log failed in {target}: {result.stderr.strip()}')
    commits = []
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        parts = line.split('\x1f')
        commits.append({
            'sha': parts[0] if len(parts) > 0 else None,
            'author': parts[1] if len(parts) > 1 else None,
            'date': parts[2] if len(parts) > 2 else None,
            'subject': parts[3] if len(parts) > 3 else None,
        })
    return json.dumps({
        'repo': str(target),
        'count': len(commits),
        'requested_limit': limit,
        'commits': commits,
    }, indent=2)


@server.tool()
def git_diff(
    repo: Annotated[str, Field(description=(
        'Repository path. Defaults to the configured root.'))] = '.',
    ref: Annotated[Optional[str], Field(description=(
        'Optional ref to diff against, e.g. "HEAD" or a branch name.'))] = None,
    staged: Annotated[bool, Field(description=(
        'Diff the index instead of the working tree.'))] = False,
) -> str:
    """Show a diff, capped and truncation-honest."""
    target = _inside(repo)
    _require_repo(target)
    args = ['diff', '--no-color']
    if staged:
        args.append('--cached')
    if ref:
        args.append(_safe_token(ref, 'ref'))
    result = _run(target, args)
    if result.returncode != 0:
        raise ToolError(f'git diff failed in {target}: {result.stderr.strip()}')
    payload = _capped(result.stdout, MAX_DIFF_BYTES)
    return json.dumps({'repo': str(target), **payload}, indent=2)


@server.tool()
def git_branches(
    repo: Annotated[str, Field(description=(
        'Repository path. Defaults to the configured root.'))] = '.',
) -> str:
    """List local branches and the current one."""
    target = _inside(repo)
    _require_repo(target)
    listing = _run(target, ['branch', '--format=%(refname:short)%09%(objectname:short)%09%(upstream:short)'])
    if listing.returncode != 0:
        raise ToolError(f'git branch failed in {target}: {listing.stderr.strip()}')
    current = _run(target, ['rev-parse', '--abbrev-ref', 'HEAD'])
    branches = []
    for line in listing.stdout.splitlines():
        if not line.strip():
            continue
        bits = line.split('\t')
        name = bits[0]
        branches.append({
            'name': name,
            'sha': bits[1] if len(bits) > 1 else None,
            'upstream': bits[2] if len(bits) > 2 and bits[2] else None,
            'current': current.stdout.strip() == name,
        })
    return json.dumps({
        'repo': str(target),
        'current': current.stdout.strip() or None,
        'count': len(branches),
        'branches': branches,
    }, indent=2)


@server.tool()
def git_show(
    repo: Annotated[str, Field(description=(
        'Repository path. Defaults to the configured root.'))] = '.',
    revision: Annotated[str, Field(description=(
        'Commit-ish to show, e.g. "HEAD" or a sha.'))] = 'HEAD',
) -> str:
    """Show one commit's metadata and diff."""
    target = _inside(repo)
    _require_repo(target)
    meta = _run(target, ['show', '--no-color', '--pretty=format:%H%n%an%n%aI%n%s',
                         '--stat', _safe_token(revision, 'revision')])
    if meta.returncode != 0:
        raise ToolError(
            f'git show {revision} failed in {target}: {meta.stderr.strip()}')
    return json.dumps({'repo': str(target),
                       **_capped(meta.stdout, MAX_DIFF_BYTES)}, indent=2)


if __name__ == '__main__':
    import asyncio
    raise SystemExit(asyncio.run(server.run_stdio_async()) or 0)