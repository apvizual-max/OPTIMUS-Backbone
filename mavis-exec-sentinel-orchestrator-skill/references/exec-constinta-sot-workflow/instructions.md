# Sub-Skill: exec-constinta-sot-workflow

* **Description:** Complete meticulous workflow for establishing and maintaining a Single Source of Truth (SOT) in Hermes system files. Covers file merging, duplicate elimination, global string reprogramming, regex techniques, and verification methodology. Use whenever managing SOT unification, memory cleanup, or system-wide text normalization.

---

# CONSTINTA SOT Workflow — Complete Implementation Reference

This skill documents the **exact, verified methodology** used to eliminate a critical system confusion (`CONSTIINTA` / `CONȘTINȚA` → `CONSTINTA`) and establish a permanent Single Source of Truth. Use this as the master playbook for any similar SOT unification task.

---

## THE PROBLEM THIS SOLVED

The Hermes system had **three incompatible variants** of the same term scattered across:
- File **names**: `CONSTIINTA.md`, `CONȘTINȚA.md`, `CONŞTINŢA.md`
- File **contents**: same variants mixed throughout all `.md`, `.py`, `.json`, `.yaml` files
- **Result**: broken cross-references, unparseable paths (Windows CP1252 encoding failures), LLM confusion, programming inconsistency

**Decision rule:** Adopt a single ASCII-safe, diacritic-free standard: `CONSTINTA`

---

## PHASE 1: DISCOVERY SCAN

Before touching anything, map the full scope.

### 1.1 Find all legacy filenames

```powershell
# Scan for filenames containing any legacy variant
Get-ChildItem -Path "C:\Users\apviz\AppData\Local\hermes" -Recurse -ErrorAction SilentlyContinue |
  Where-Object { $_.Name -match "constiint|conștiinț|constiin" } |
  Select-Object FullName | Format-List
```

### 1.2 Find all files with legacy content (Python)

```python
import os, re

root = r"C:\Users\apviz\AppData\Local\hermes"
pattern = re.compile(
    r"constiintă|constiintã|constiinţa|constiință|constiinta|conștința|conştinţa|conştinţă|conștință",
    re.IGNORECASE
)

# Directories to skip
skip_dirs = {"OGLINDA - CASA", ".git", ".venv", "node_modules"}

results = []
for dirpath, dirs, files in os.walk(root):
    dirs[:] = [d for d in dirs if d not in skip_dirs]
    for f in files:
        if f.lower().endswith((".py", ".md", ".json", ".yaml", ".yml", ".txt", ".js")):
            fp = os.path.join(dirpath, f)
            try:
                content = open(fp, encoding="utf-8", errors="ignore").read()
                if pattern.search(content):
                    results.append(fp)
            except Exception:
                pass

print(f"Files with legacy content: {len(results)}")
for r in results:
    print(" ", r.encode("ascii", "ignore").decode("ascii"))
```

**Critical:** Always encode output with `.encode("ascii", "ignore").decode("ascii")` to avoid `UnicodeEncodeError` on Windows console when printing paths with diacritics.

---

## PHASE 2: FILE MANAGEMENT — MERGING AND RENAMING

### Decision Rule for Duplicate Pairs

When a folder contains BOTH a legacy-named file AND a correctly-named file:
1. **Take the larger file** as the baseline
2. **Append the smaller file's unique content** to the baseline
3. **Delete the now-empty smaller file**
4. **Rename the baseline** to the canonical name (`CONSTINTA.md`)

When a folder has only ONE legacy-named file:
- **Rename directly** — no merge needed

### 2.1 Preview Merges (Dry Run First)

```python
import os

def find_merge_pairs(root):
    """Find all folders containing both a legacy and a canonical file."""
    pairs = []
    for dirpath, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in {".git", ".venv", "node_modules"}]
        lower_files = {f.lower(): f for f in files}
        
        legacy_variants = [
            "constiinta.md", "conștința.md", "conştinţa.md",
            "conştiinţă.md", "constiința.md"
        ]
        legacy_found = [f for lf in legacy_variants for f in files if f.lower() == lf]
        canonical_found = [f for f in files if f == "CONSTINTA.md"]
        
        if legacy_found and canonical_found:
            pairs.append((dirpath, legacy_found[0], canonical_found[0], "MERGE"))
        elif legacy_found and not canonical_found:
            pairs.append((dirpath, legacy_found[0], None, "RENAME"))
    
    return pairs

pairs = find_merge_pairs(r"C:\Users\apviz\AppData\Local\hermes")
for dirpath, legacy, canonical, action in pairs:
    print(f"[{action}] {dirpath}")
    print(f"         Legacy: {legacy}")
    if canonical:
        print(f"         Target: {canonical}")
```

### 2.2 Execute Merges

```python
import os, shutil

def execute_merge(folder, legacy_name, canonical_name="CONSTINTA.md"):
    legacy_path = os.path.join(folder, legacy_name)
    canonical_path = os.path.join(folder, canonical_name)
    
    if not os.path.exists(canonical_path):
        # Simple rename
        os.rename(legacy_path, canonical_path)
        print(f"RENAMED: {legacy_path}")
        return
    
    # Merge: choose larger as baseline
    legacy_size = os.path.getsize(legacy_path)
    canonical_size = os.path.getsize(canonical_path)
    
    if legacy_size > canonical_size:
        baseline, appendee = legacy_path, canonical_path
    else:
        baseline, appendee = canonical_path, legacy_path
    
    with open(baseline, "r", encoding="utf-8", errors="ignore") as f:
        base_content = f.read()
    with open(appendee, "r", encoding="utf-8", errors="ignore") as f:
        append_content = f.read()
    
    # Only append unique content
    if append_content.strip() not in base_content:
        merged = base_content.rstrip() + "\n\n---\n\n" + append_content.strip()
    else:
        merged = base_content
    
    # Write to canonical_path
    with open(canonical_path, "w", encoding="utf-8") as f:
        f.write(merged)
    
    # Delete the other one
    if baseline != canonical_path:
        os.remove(legacy_path)
        # Rename baseline to canonical
        os.rename(baseline, canonical_path)
    else:
        os.remove(legacy_path if appendee == legacy_path else canonical_path)
        # The canonical is already the right name
    
    print(f"MERGED:  {folder} -> CONSTINTA.md")
```

### 2.3 Rename Remaining Legacy Filenames (Script Files, Archives)

```python
import os, re

# Pattern for ANY file whose name contains legacy variants
legacy_name_pattern = re.compile(
    r"constiinta|conştinţ|conștiinț|constiință",
    re.IGNORECASE
)

def rename_legacy_files(root):
    renames = []
    for dirpath, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in {".git", ".venv", "node_modules"}]
        for fname in files:
            if legacy_name_pattern.search(fname):
                new_name = re.sub(
                    legacy_name_pattern, 
                    lambda m: "constinta" if m.group().islower() else "CONSTINTA",
                    fname
                )
                renames.append((dirpath, fname, new_name))
    
    print(f"Files to rename: {len(renames)}")
    for folder, old, new in renames:
        old_path = os.path.join(folder, old)
        new_path = os.path.join(folder, new)
        if not os.path.exists(new_path):
            os.rename(old_path, new_path)
            print(f"  RENAMED: {old} -> {new}")
        else:
            print(f"  SKIP (target exists): {new}")

rename_legacy_files(r"C:\Users\apviz\AppData\Local\hermes")
```

---

## PHASE 3: IN-FILE STRING REPROGRAMMING

### 3.1 The Critical Regex Bug to Avoid

**WRONG (misses identifiers like `constiinta_linting_cron`):**
```python
# \b word boundary treats underscore as a word char, so \bCONSTIINTA\b
# will NOT match CONSTIINTA in "constiinta_linting_cron" — silent failure!
pattern = re.compile(r"\bCONSTIINTA\b", re.IGNORECASE)
```

**CORRECT (no word boundaries — matches everywhere including identifiers):**
```python
pattern = re.compile(
    r"(con[sșşSȘŞ]ti{1,2}n[tțţTȚŢ][aăâãeioușțşţ]*)",
    re.IGNORECASE
)
```

**Even simpler correct approach (exhaustive literal list):**
```python
import re

# ALL known legacy variants — literal, case-insensitive
patterns = [
    "constiinta", "CONSTIINTA", "Constiinta",
    "conștința", "CONȘTINȚA", "Conștința",
    "conştinţa", "CONŞTINŢA", "Conştinţa",
    "constiința", "CONSTIINȚA", "Constiința",
    "conştiinţă", "CONŞTIINŢĂ", "Conştiinţă",
    "conștiință", "conștiinței",
]
combined = re.compile("|".join(re.escape(p) for p in patterns), re.IGNORECASE)
```

### 3.2 Case-Preserving Replacement Function

```python
def make_replacement(match_str, canonical="constinta"):
    """Preserve case style of original match."""
    if match_str.isupper():
        return canonical.upper()              # CONSTINTA
    elif match_str[0].isupper():
        return canonical.capitalize()         # Constinta
    else:
        return canonical.lower()              # constinta
```

### 3.3 Global File Reprogramming Script

```python
import os, re

ROOTS = [
    r"C:\Users\apviz\AppData\Local\hermes",
    r"C:\Users\apviz\Documents\Antigravity_Folder\Antigravity_Projects",
]

SKIP_DIRS = {"OGLINDA - CASA", ".git", ".venv", "node_modules", "__pycache__"}

TEXT_EXTENSIONS = {".py", ".md", ".json", ".yaml", ".yml", ".txt", ".js"}

# Exhaustive pattern — no word boundaries
PATTERN = re.compile(
    r"constiintă|constiintã|constiinţa|constiință|constiinta"
    r"|conștința|conştinţa|conştinţă|conștință|conștiinței",
    re.IGNORECASE
)

def replace_match(m):
    s = m.group(0)
    if s.isupper(): return "CONSTINTA"
    if s[0].isupper(): return "Constinta"
    return "constinta"

modified_count = 0
for root in ROOTS:
    if not os.path.exists(root): continue
    for dirpath, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fname in files:
            if not any(fname.endswith(ext) for ext in TEXT_EXTENSIONS): continue
            fpath = os.path.join(dirpath, fname)
            try:
                content = open(fpath, encoding="utf-8", errors="ignore").read()
                updated = PATTERN.sub(replace_match, content)
                if updated != content:
                    with open(fpath, "w", encoding="utf-8") as f:
                        f.write(updated)
                    modified_count += 1
                    print(f"REPROGRAMMED: {fpath.encode('ascii','ignore').decode('ascii')}")
            except Exception as e:
                print(f"ERROR: {fpath.encode('ascii','ignore').decode('ascii')}: {e}")

print(f"\nTotal files reprogrammed: {modified_count}")
```

---

## PHASE 4: VERIFICATION

### 4.1 Final Verification Script

```python
import os, re

ROOTS = [
    r"C:\Users\apviz\AppData\Local\hermes",
    r"C:\Users\apviz\Documents\Antigravity_Folder\Antigravity_Projects",
]
SKIP_DIRS = {"OGLINDA - CASA", ".git", ".venv", "node_modules", "__pycache__"}

LEGACY_NAME_SUBSTRINGS = [
    "constiinta", "constiintă", "conștiința", "conştinţa", "conștiință",
    "constiinţa",
]

CONTENT_PATTERN = re.compile(
    r"constiintă|constiintã|constiinţa|constiință|constiinta"
    r"|conștința|conştinţa|conştinţă|conștință|conștiinței",
    re.IGNORECASE
)

bad_filenames = []
bad_content_files = []

for root in ROOTS:
    if not os.path.exists(root): continue
    for dirpath, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fname in files:
            # Check filename
            if any(s in fname.lower() for s in LEGACY_NAME_SUBSTRINGS):
                bad_filenames.append(os.path.join(dirpath, fname))
            # Check content
            if any(fname.endswith(ext) for ext in (".py", ".md", ".json", ".yaml", ".yml", ".txt", ".js")):
                try:
                    content = open(os.path.join(dirpath, fname), encoding="utf-8", errors="ignore").read()
                    if CONTENT_PATTERN.search(content):
                        bad_content_files.append(os.path.join(dirpath, fname))
                except Exception:
                    pass

print(f"Remaining legacy filenames: {len(bad_filenames)}")
for f in bad_filenames:
    print(f"  FILENAME: {f.encode('ascii','ignore').decode('ascii')}")

print(f"\nRemaining legacy content: {len(bad_content_files)}")
for f in bad_content_files:
    print(f"  CONTENT:  {f.encode('ascii','ignore').decode('ascii')}")

if not bad_filenames and not bad_content_files:
    print("\n[PERFECT] System 100% unified. No legacy strings remain.")
else:
    print(f"\n[WARNING] {len(bad_filenames) + len(bad_content_files)} issues remain. Run Phase 2 and 3 again.")
```

**Target result:**
```
Remaining legacy filenames: 0
Remaining legacy content: 0
[PERFECT] System 100% unified. No legacy strings remain.
```

---

## PHASE 5: MEMORY AND INTERNAL PROGRAMMING UPDATE

After file and content unification, update the **agent's internal programming** to reflect the new SOT:

### 5.1 Update SOUL.md References

Search SOUL.md for any reference to the old terms and replace:
```python
soul_path = r"C:\Users\apviz\AppData\Local\hermes\profiles\prime\SOUL.md"
content = open(soul_path, encoding="utf-8").read()
# Apply same PATTERN.sub(replace_match, content) from Phase 3
# Write back
open(soul_path, "w", encoding="utf-8").write(PATTERN.sub(replace_match, content))
```

### 5.2 Update All Skill References

```python
skills_root = r"C:\Users\apviz\AppData\Local\hermes\skills"
# Walk and apply Phase 3 reprogramming script above
```

### 5.3 Update the Linting Cron

The `constinta_linting_cron.py` in `scripts/` validates CONSTINTA.md integrity on a schedule. After any CONSTINTA.md update, verify the cron still passes:

```powershell
C:\Users\apviz\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe `
  "C:\Users\apviz\AppData\Local\hermes\scripts\constinta_linting_cron.py" --run-once
```

---

## KNOWN PITFALLS AND SOLUTIONS

| Pitfall | Solution |
|---------|---------|
| `\b` word boundary misses identifiers with underscores | Use `re.compile(pattern, re.IGNORECASE)` WITHOUT `\b` |
| `UnicodeEncodeError` when printing diacritic paths | Use `.encode('ascii','ignore').decode('ascii')` on all path prints |
| `re.IGNORECASE` does not auto-fold non-ASCII in char classes | Explicitly list all variants: `[sșşSȘŞ]` instead of just `[sS]` |
| Files in cron/output directories missed | Include `cron\output\` in scan roots |
| State-snapshots contain copies of legacy files | Include `state-snapshots\` in scan roots |
| Two files exist but content differs | Always merge larger→smaller, never delete without merging |

---

## SOT GOVERNANCE RULES (ENFORCE ALWAYS)

1. **One file, one term** — `CONSTINTA.md` is the ONLY accepted filename
2. **One spelling** — `CONSTINTA` (all caps), `Constinta` (title), `constinta` (lower) — NO diacritics
3. **Update immediately** — when creating any new skill, memory file, or script, use `CONSTINTA` exclusively
4. **Verify after every batch change** — always run Phase 4 verification before declaring complete
5. **Never skip the merge step** — deleting without merging risks data loss