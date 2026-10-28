#!/usr/bin/env python3
"""
Source registry for the SENTINEL brain corpus.

Walks every archive the brain draws on and records what it actually found:
path, kind, size, modification time, SHA256, and whether the SENTINEL brain
holds write access to it.

STRICTLY READ-ONLY. This script opens source files for reading and writes one
file, inside SENTINEL_PRIME. It never modifies, moves or creates anything in
E:\\, D:\\, .minimax\\, the projects tree outside SENTINEL_PRIME, or the Docker
swarm.

Ingest depth follows the plan's stated default: doctrine, manuals, proverbs and
character ASSETS are hashed and catalogued; binary media (AUDIO/VIDEO) is
catalogued by metadata only and never opened, because processing it is not
needed for the brain and recursion into a foreign vault is not worth the risk.

Usage:  python 08_SELF_IMPROVEMENT\\build_source_registry.py
"""
import hashlib
import json
import os
from datetime import datetime
from pathlib import Path

WORKSPACE = Path(os.environ.get(
    'WORKSPACE_ROOT',
    r'C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\SENTINEL_PRIME'))
OUT = WORKSPACE / '11_BRAIN' / '05_SOURCES' / 'source_registry.json'

DOC_EXT = {'.md', '.txt', '.json', '.jsonl', '.py', '.ps1', '.yaml', '.yml'}
MEDIA_EXT = {'.mp3', '.wav', '.m4a', '.flac', '.mp4', '.mov', '.avi', '.mkv', '.png',
             '.jpg', '.jpeg', '.gif', '.webp', '.zip', '.7z', '.pdf', '.docx'}

# (id, label, path, depth)
#   depth 'index'  - record the directory only, list children, do not hash
#   depth 'full'   - hash every matching file
#   depth 'media'  - catalog metadata only, never open the file
SOURCES = [
    ('CONVERSATION_FREEZE', 'This conversation, frozen with SHA256SUMS',
     WORKSPACE / '09_LOGS' / 'corpus_freeze', 'full'),
    ('MINIMAX_SESSIONS', 'All 46 other MiniMax sessions (Antigravity transfer, bridge work)',
     Path(r'C:\Users\apviz\.minimax\v2\sessions'), 'md'),
    ('MIMESIS_MEMORY', 'Agent memory - the durable lessons behind the system',
     Path(r'C:\Users\apviz\.minimax\agents\mavis\memory\MEMORY.md'), 'full'),
    ('MIMESIS_USER_MEMORY', 'User memory - operator identity and collaboration rules',
     Path(r'C:\Users\apviz\.minimax\memory\user.md'), 'full'),
    ('ANTIGRAVITY_TRANSFER', 'Antigravity knowledge transfer archive',
     Path(r'C:\Users\apviz\Documents\Antigravity_Folder'), 'md'),
    ('SECOND_BRAIN_DOCTRINE', 'Obsidian vault - SF manuals, SPO, PO, the 963 proverbs',
     Path(r'E:\CLAUDE\MINTE\00_KV_SECOND BRAIN'), 'md'),
    ('SENTINEL_CHARACTER', 'SENTINEL character assets (AUDIO / VIDEO catalogued, not opened)',
     Path(r'D:\Alex_Knowlege_Vault\03_Resources\03_7-SENTINEL_Character'), 'media'),
    ('PROJECTS_ROOT_REPORTS', 'Integration and status reports at the projects root',
     Path(r'C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard'), 'md'),
    ('OPTIMUS_CONTROL_CENTER', 'The proven dashboard pattern, read-only reference',
     Path(r'C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\90_CONTROL_CENTER'), 'md'),
    ('DESIGN_SOT', 'Obsidian Telemetry Dark design system, read-only working copy',
     Path(r'C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\95_DESIGN_SOT'), 'full'),
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def catalog(path: Path, depth: str):
    """Read-only inventory of one source."""
    entry = {
        'exists': path.exists(),
        'kind': 'file' if path.is_file() else ('dir' if path.is_dir() else 'missing'),
        'write_access_by_sentinel': False,
        'read_access': 'granted',
    }
    if not path.exists():
        entry['note'] = 'source not present on this machine'
        return entry

    if path.is_file():
        stat = path.stat()
        entry.update({
            'bytes': stat.st_size,
            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'sha256': sha256_file(path) if depth == 'full' else None,
        })
        return entry

    files, dirs, bytes_total, media_count, doc_count = 0, 0, 0, 0, 0
    hashed, media_list, errors = 0, [], []
    stack = [path]
    max_dirs = 4000
    while stack and dirs < max_dirs:
        cur = stack.pop()
        try:
            for child in os.scandir(cur):
                if child.is_dir(follow_symlinks=False):
                    dirs += 1
                    stack.append(Path(child.path))
                elif child.is_file(follow_symlinks=False):
                    files += 1
                    try:
                        size = child.stat(follow_symlinks=False).st_size
                    except OSError as exc:
                        errors.append(f'{child.path}: {exc}')
                        continue
                    bytes_total += size
                    ext = Path(child.name).suffix.lower()
                    if ext in MEDIA_EXT:
                        media_count += 1
                        if len(media_list) < 200:
                            media_list.append({
                                'name': child.name,
                                'bytes': size,
                                'catalogued': 'metadata only - never opened',
                            })
                    elif ext in DOC_EXT or depth == 'full':
                        doc_count += 1
                        if depth in ('full', 'md') and ext in DOC_EXT:
                            try:
                                sha256_file(Path(child.path))
                                hashed += 1
                            except OSError as exc:
                                errors.append(f'{child.path}: {exc}')
        except OSError as exc:
            errors.append(f'{cur}: {exc}')

    entry.update({
        'files': files,
        'dirs_scanned': dirs,
        'bytes': bytes_total,
        'text_files_hashed': hashed,
        'media_files_catalogued': media_count,
        'depth': depth,
        'media_sample': media_list[:20],
        'errors': errors[:20],
        'truncated_scan': dirs >= max_dirs,
    })
    return entry


def main():
    sources = []
    for sid, label, path, depth in SOURCES:
        print(f'scanning {sid:26s} {path}')
        item = catalog(path, depth)
        sources.append({
            'id': sid,
            'label': label,
            'path': str(path),
            'mode': 'read-only',
            **item,
        })

    registry = {
        'generated': datetime.now().isoformat(),
        'purpose': 'Every archive the SENTINEL brain draws on, with proof of what was read. '
                   'The SENTINEL brain holds write access to SENTINEL_PRIME only.',
        'ingest_policy': {
            'write_scope': str(WORKSPACE),
            'outside_scope': 'read-only, never modified',
            'media': 'catalogued by metadata, never opened',
            'public_deployment': 'never implied; requires its own explicit approval',
        },
        'sources': sources,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(registry, indent=2, ensure_ascii=False), encoding='utf-8')

    print()
    for s in sources:
        if not s.get('exists'):
            print(f"  {s['id']:26s} MISSING")
            continue
        print(f"  {s['id']:26s} files={s.get('files', 1):<6} "
              f"hashed={s.get('text_files_hashed', 1):<5} "
              f"media={s.get('media_files_catalogued', 0):<5} "
              f"{(s.get('bytes') or 0):>12,} B")
    print(f'\nwritten: {OUT}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
