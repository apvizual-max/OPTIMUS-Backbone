# Sub-Skill: exec-hermes-file-merge-reorganize

* **Description:** Merges, deduplicates, and renames conflicting file pairs in Hermes Agent's
profile directories, state-snapshots, and backup archives.
Use when: consolidating legacy filenames, resolving SOT (single source of truth)
conflicts, renaming files across profiles/prime/assist/default + snapshots + backups,
or whenever two files in the same directory represent the same concept under
different spellings, encodings, or diacritic variants.

---

# Hermes File Merge & Reorganization Skill

Merges, deduplicates, and renames conflicting file pairs across all Hermes
profile directories, state-snapshots, and backup archives.

> [!IMPORTANT]
> Always run a **dry-run scan first** (`scan_duplicate_files.ps1`) before
> making any changes. Never delete a file without first confirming the merge
> was successful.

## When to Use

- Two files in the same directory represent the same concept (different spelling/encoding)
- A SOT (Single Source of Truth) name is being enforced system-wide
- Profile files, snapshot files, or backup files need renaming after a terminology change
- You need to consolidate `CONSTIINTA.md` / `CONȘTINȚA.md` → `CONSTINTA.md` (or similar)

## Scope — Always Cover These Paths

```
HERMES_HOME = C:\Users\apviz\AppData\Local\hermes

profiles\assist\
profiles\prime\
profiles\default\
state-snapshots\*\profiles\assist\
state-snapshots\*\profiles\prime\
state-snapshots\*\profiles\default\
backups\*\profiles\*\
```

## Workflow

### Step 1 — Scan
Run `scripts\scan_duplicate_files.ps1` to identify all conflicting file pairs.
Note which directory has both files and their sizes.

### Step 2 — Merge Decision
For each directory with both files:
- **Both files exist** → merge (larger = baseline, append unique from smaller)
- **Only one file exists** → rename only, no merge needed
- **File is empty** → delete empty, rename the other

### Step 3 — Merge & Deduplicate
```python
# Merge strategy: keep larger as baseline, append unique lines from smaller
def merge_files(larger_path, smaller_path, output_path):
    with open(larger_path, encoding='utf-8') as f:
        base_lines = f.readlines()
    with open(smaller_path, encoding='utf-8') as f:
        extra_lines = f.readlines()
    
    # Deduplicate: only append lines not already in base
    base_set = set(l.strip() for l in base_lines if l.strip())
    unique_extra = [l for l in extra_lines if l.strip() not in base_set]
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.writelines(base_lines)
        if unique_extra:
            f.write('\n\n<!-- Merged from: ' + smaller_path.name + ' -->\n')
            f.writelines(unique_extra)
    
    # Delete the smaller file after merge
    smaller_path.unlink()
```

### Step 4 — Rename
```python
from pathlib import Path
output_path.rename(output_path.parent / 'CONSTINTA.md')  # use canonical name
```

### Step 5 — Verify
Run `scripts\verify_filenames.ps1` — expected result: **0 legacy filenames found**.

## Safety Rules

1. **Never delete without merge** — always write merged content before removing source
2. **Create `.bak` backup** for files over 5KB before overwriting
3. **PowerShell `Set-Content` gotcha**: always use `-Encoding UTF8 -NoNewline` to avoid extra trailing newlines in YAML files
4. **Check for YAML files**: if a `.yaml` or `.yml` file is being merged, validate it parses cleanly with `yaml.safe_load()` after merge
5. **Exclude**: `OGLINDA - CASA\`, `.git\`, `venv\`, `node_modules\`, `__pycache__\`

## Reference Files

- [MERGE_STRATEGY.md](references/MERGE_STRATEGY.md) — Decision tree for all merge scenarios
- [HERMES_PATHS.md](references/HERMES_PATHS.md) — All critical Hermes path references
- [scan_duplicate_files.ps1](references/exec-hermes-file-merge-reorganize/scripts/\1) — Filename conflict scanner
- [merge_and_rename.py](references/exec-hermes-file-merge-reorganize/scripts/\1) — Merge + dedup + rename script
- [verify_filenames.ps1](references/exec-hermes-file-merge-reorganize/scripts/\1) — Post-merge verification