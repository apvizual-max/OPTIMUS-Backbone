"""
merge_and_rename.py
===================
Merges conflicting file pairs in Hermes profile directories and renames
the merged result to the canonical SOT filename.

Usage:
    python merge_and_rename.py --root <path> --canonical CONSTINTA.md --dry-run
    python merge_and_rename.py --root <path> --canonical CONSTINTA.md --apply

Merge strategy:
    1. Find all directories containing both PatternA and PatternB filenames
    2. Identify the larger file as the baseline
    3. Append unique lines from the smaller file
    4. Write merged content to canonical filename
    5. Delete both source files
"""

import argparse
import re
import shutil
from pathlib import Path
from datetime import datetime

PATTERN_A = re.compile(r'CONSTIINTA', re.IGNORECASE)
PATTERN_B = re.compile(r'CON[ŞS]TIN[ŢT][AĂ]|CONȘTINȚA', re.IGNORECASE)
EXCLUDE_DIRS = {'OGLINDA - CASA', '.git', 'venv', 'node_modules', '__pycache__'}


def find_conflict_dirs(root: Path):
    """Find directories containing both pattern A and pattern B files."""
    conflicts = []
    all_files = {}

    for f in root.rglob('*'):
        if f.is_file() and not any(ex in str(f) for ex in EXCLUDE_DIRS):
            if PATTERN_A.search(f.name) or PATTERN_B.search(f.name):
                all_files.setdefault(f.parent, []).append(f)

    for dir_path, files in all_files.items():
        has_a = any(PATTERN_A.search(f.name) for f in files)
        has_b = any(PATTERN_B.search(f.name) for f in files)
        if has_a and has_b:
            conflicts.append((dir_path, files))
        else:
            # Rename-only
            conflicts.append((dir_path, files))

    return conflicts


def merge_files(larger: Path, smaller: Path) -> str:
    """Merge two files: larger is baseline, append unique lines from smaller."""
    base_content = larger.read_text(encoding='utf-8')
    extra_content = smaller.read_text(encoding='utf-8')

    base_lines = base_content.splitlines(keepends=True)
    extra_lines = extra_content.splitlines(keepends=True)

    # Only append lines that are not already in the base (stripped comparison)
    base_stripped = {l.strip() for l in base_lines if l.strip()}
    unique_extra = [l for l in extra_lines if l.strip() not in base_stripped]

    merged = base_content
    if unique_extra:
        merged += f'\n\n<!-- Merged from: {smaller.name} -->\n'
        merged += ''.join(unique_extra)

    return merged


def process(root: Path, canonical: str, dry_run: bool = True):
    """Main processing loop."""
    groups = find_conflict_dirs(root)
    print(f"Found {len(groups)} affected directories")

    for dir_path, files in groups:
        print(f"\nDirectory: {dir_path}")
        canonical_path = dir_path / canonical

        if len(files) == 1:
            # Rename only
            src = files[0]
            print(f"  RENAME: {src.name} → {canonical}")
            if not dry_run:
                src.rename(canonical_path)
        else:
            # Merge: larger is baseline
            files.sort(key=lambda f: f.stat().st_size, reverse=True)
            larger, smaller = files[0], files[1]
            print(f"  MERGE: {larger.name} ({larger.stat().st_size}B) + "
                  f"{smaller.name} ({smaller.stat().st_size}B) → {canonical}")
            if not dry_run:
                merged = merge_files(larger, smaller)
                # Write merged to canonical path
                canonical_path.write_text(merged, encoding='utf-8')
                # Remove both source files if they're not the canonical
                for f in files:
                    if f.name != canonical:
                        f.unlink()
                print(f"  DONE: wrote {len(merged)} chars to {canonical_path.name}")

    if dry_run:
        print("\n[DRY RUN] No files were modified. Run with --apply to execute.")
    else:
        print("\n[DONE] All files processed.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Merge and rename conflicting file pairs')
    parser.add_argument('--root', default=r'C:\Users\apviz\AppData\Local\hermes')
    parser.add_argument('--canonical', default='CONSTINTA.md')
    parser.add_argument('--dry-run', action='store_true', default=True)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()

    root = Path(args.root)
    dry_run = not args.apply
    process(root, args.canonical, dry_run=dry_run)
