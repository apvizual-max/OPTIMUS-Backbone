#!/usr/bin/env python3
"""
`prime-bridge` - a read-only bridge to the SENTINEL_PRIME workspace.

Declared in OPTIMUS_MCP_CONFIG.json as: "Bridge pentru filesystem si workspace
SENTINEL_PRIME".

Why this one is not a slice
---------------------------
The other four declared servers each name capabilities that already existed as
named tools inside `sentinel_hub_server.py`, so they delegate. This one does
not: the hub has no filesystem tools, because the hub is not the thing that
owns the workspace. So this is new capability, built here, and it is held to a
higher bar than a facade would be.

What makes it safe
------------------
It is read-only. Nothing here writes, moves or deletes, which matches the
config's own `capabilities.filesystem.delete: false` and `security.no_modify_external:
true`. Every path is resolved and rejected if it leaves the workspace root, so a
caller cannot use this to read the rest of the machine. Every listing is capped,
and when a cap truncates a result the response SAYS it did - a truncated scan
that does not announce itself is a measurement that quietly lies.

Why refusals raise ToolError, not ValueError
-------------------------------------------
Measured on 2026-10-10, before this change, a caller could not tell WHY a call
failed. Both of these returned the byte-identical body
`Error executing tool prime_read_text_file` with is_error=true:

    prime_read_text_file(path="..\\..\\..\\..\\Windows\\win.ini")    # refused
    prime_read_text_file(path="09_LOGS\\definitely_not_here.json")  # missing

The real reason - `refused: ... resolves outside the workspace root` - existed
only as an `UnexpectedToolError` traceback on the server's stderr, which the
caller never sees. A security refusal that is indistinguishable from a typo is
a control that cannot be audited by the thing it protects.

The MCP SDK draws exactly this line: `ToolError` is an anticipated failure whose
message reaches the model in `content`; anything else is treated as a crash and
its message is withheld on purpose. These four raises are all anticipated, so
they are `ToolError`. Do not "simplify" them back to `ValueError`.

Requires PRIME_HOME (set by the config's env block), falling back to
WORKSPACE_ROOT and then to the project's default location.
"""
import json
import os
import re
from pathlib import Path
from typing import Optional

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from pydantic import Field
from typing_extensions import Annotated

_DEFAULT = r"C:\Users\apviz\.minimax-agent\projects\SENTINEL_PRIME"
ROOT = Path(os.environ.get('PRIME_HOME')
            or os.environ.get('WORKSPACE_ROOT')
            or _DEFAULT).resolve()

MAX_ENTRIES = 200          # per listing, before truncation is announced
MAX_READ_BYTES = 200_000   # a text read never returns more than this

# Directories that are never useful to a caller and are expensive to walk.
SKIP_DIRS = {'.git', '__pycache__', '.venv', 'node_modules', '.pytest_cache'}

server = MCPServer('prime-bridge', version='1.0.0')


def _inside(candidate: Path) -> Path:
    """Resolve `candidate` and refuse anything outside the workspace root."""
    resolved = (ROOT / candidate).resolve() if not candidate.is_absolute() \
        else candidate.resolve()
    if resolved != ROOT and ROOT not in resolved.parents:
        raise ToolError(
            f'refused: {candidate} resolves outside the workspace root {ROOT}')
    return resolved


def _walk(limit: int):
    """Yield workspace paths, skipping build noise, up to `limit`."""
    seen = 0
    for path in ROOT.rglob('*'):
        if set(path.parts) & SKIP_DIRS:
            continue
        yield path
        seen += 1
        if seen >= limit:
            return


@server.tool()
def prime_workspace_summary(
    file_limit: Annotated[int, Field(description=(
        'Maximum files to count. The walk stops at this and reports whether '
        'the count is therefore a floor rather than a total.'))] = 50_000,
) -> str:
    """Summarise the workspace: one line per top-level area with counts and size."""
    areas = {}
    truncated = False
    for index, path in enumerate(_walk(file_limit)):
        try:
            rel = path.relative_to(ROOT)
        except ValueError:
            continue
        area = rel.parts[0] if len(rel.parts) > 1 else '(root)'
        bucket = areas.setdefault(area, {'files': 0, 'dirs': 0, 'bytes': 0})
        if path.is_dir():
            bucket['dirs'] += 1
        else:
            bucket['files'] += 1
            try:
                bucket['bytes'] += path.stat().st_size
            except OSError:
                pass
        if index + 1 >= file_limit:
            truncated = True
            break
    return json.dumps({
        'root': str(ROOT),
        'areas': dict(sorted(areas.items())),
        'file_limit': file_limit,
        'truncated': truncated,
        'truncated_note': (
            f'stopped at {file_limit} files; counts are a floor, not a total'
            if truncated else 'complete walk'),
    }, indent=2)


@server.tool()
def prime_list_area(
    area: Annotated[str, Field(description=(
        'Top-level directory name, or "(root)" for the workspace root.'))],
) -> str:
    """List the direct children of one top-level area of the workspace."""
    target = ROOT if area == '(root)' else _inside(Path(area))
    if not target.is_dir():
        raise ToolError(f'{area} is not a directory in the workspace')
    entries = sorted(target.iterdir(), key=lambda p: p.name)
    shown = entries[:MAX_ENTRIES]
    return json.dumps({
        'area': area,
        'path': str(target),
        'count': len(entries),
        'returned': len(shown),
        'truncated': len(entries) > len(shown),
        'truncated_note': (
            f'showing {MAX_ENTRIES} of {len(entries)}'
            if len(entries) > len(shown) else 'complete listing'),
        'entries': [{
            'name': p.name,
            'kind': 'dir' if p.is_dir() else 'file',
            'bytes': p.stat().st_size if p.is_file() else None,
        } for p in shown],
    }, indent=2)


@server.tool()
def prime_find_files(
    pattern: Annotated[str, Field(description=(
        'Substring or glob matched case-insensitively against file names, '
        'e.g. "server" or "*.md".'))],
) -> str:
    """Find workspace files whose name matches `pattern`."""
    try:
        regex = re.compile(pattern, re.IGNORECASE)
    except re.error as e:
        return f'ERROR: invalid pattern: {e}'

    hits = []
    truncated = False
    for path in _walk(MAX_ENTRIES * 20):
        if regex.search(path.name):
            hits.append(str(path.relative_to(ROOT)))
            if len(hits) >= MAX_ENTRIES:
                truncated = True
                break
    return json.dumps({
        'pattern': pattern,
        'count': len(hits),
        'truncated': truncated,
        'truncated_note': (f'capped at {MAX_ENTRIES} matches' if truncated
                           else 'complete search'),
        'files': sorted(hits),
    }, indent=2)


@server.tool()
def prime_read_text_file(
    path: Annotated[str, Field(description=(
        'Workspace-relative path to a text file.'))],
    max_bytes: Annotated[int, Field(description=(
        'Byte cap for the returned text. Defaults to 200000.'))] = MAX_READ_BYTES,
) -> str:
    """Read a UTF-8 text file from the workspace, capped, read-only."""
    target = _inside(Path(path))
    if not target.is_file():
        raise ToolError(f'{path} is not a file in the workspace')
    cap = min(int(max_bytes), MAX_READ_BYTES)
    try:
        data = target.read_bytes()[:cap]
        text = data.decode('utf-8', errors='replace')
        whole = target.stat().st_size
    except OSError as exc:
        raise ToolError(f'could not read {path}: {exc}') from exc
    return json.dumps({
        'path': str(target.relative_to(ROOT)),
        'bytes_total': whole,
        'bytes_returned': len(data),
        'truncated': whole > len(data),
        'truncated_note': (
            f'returning the first {len(data)} of {whole} bytes'
            if whole > len(data) else 'complete file'),
        'text': text,
    }, indent=2)


if __name__ == '__main__':
    import asyncio
    raise SystemExit(asyncio.run(server.run_stdio_async()) or 0)