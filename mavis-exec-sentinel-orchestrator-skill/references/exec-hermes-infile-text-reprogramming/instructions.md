# Sub-Skill: exec-hermes-infile-text-reprogramming

* **Description:** System-wide text replacement across all Hermes config, skill, profile, memory,
and script files. Handles diacritic variants, case preservation, slash-separated
compound terms, and the critical word-boundary edge case for underscore-delimited
identifiers (e.g., constiinta_linting style strings).
Use when: a terminology SOT changes, a legacy term must be globally replaced,
or consolidating spelling variants across .md, .py, .json, .yaml, .txt files.

---

# Hermes In-File Text Reprogramming Skill

System-wide text replacement with case preservation, diacritic variant matching,
and correct word-boundary handling for identifier-style strings.

> [!CAUTION]
> Always run in **dry-run mode first** to count matches before applying changes.
> Confirm count > 0 before proceeding. Verify count = 0 after completion.

## When to Use

- A terminology SOT (Single Source of Truth) is being enforced globally
- Legacy terms with diacritics, double-letters, or spelling variants need unification
- The same concept appears in multiple spellings across `.md`, `.yaml`, `.py`, `.json` files
- A profile, skill, or memory file references an outdated term name

## Critical Bug: Word Boundary Regex

> [!WARNING]
> Standard `\b` word boundaries **fail** with:
> 1. Unicode diacritic characters (`Ș`, `Ț`, `Ă`, etc.)
> 2. Underscore-delimited identifiers (`constiinta_linting`, `CONSTIINTA_KEY`)
>
> Always use the custom pattern below instead.

### Correct Pattern
```python
# CORRECT: handles both Unicode and underscores
WORD_BOUNDARY = r'(?<![a-zA-Z0-9_])({term})(?![a-zA-Z0-9_])'

# WRONG: breaks on diacritics and underscores
NAIVE_BOUNDARY = r'\b({term})\b'
```

## Pattern Set (CONSTINTA Migration Example)

```python
# Step 1: Match slash-separated compound FIRST (order matters!)
SLASH_VARIANTS = [
    r'CONSTIINTA\s*/\s*CON[ŞS]TIN[ŢT][AĂ]',
    r'CON[ŞS]TIN[ŢT][AĂ]\s*/\s*CONSTIINTA',
]

# Step 2: Then individual variants
SINGLE_VARIANTS = [
    r'CON[ŞS]TIN[ŢT][AĂ]',  # diacritic variants (comma/cedilla)
    r'CONSTIINTA',            # double-i variant
    r'CONȘTIINȚA',            # specific Unicode form
]
```

## Case Preservation Logic

```python
def apply_case(match_text: str, replacement: str) -> str:
    if match_text.isupper():
        return replacement.upper()            # CONSTIINTA → CONSTINTA
    elif match_text.istitle():
        return replacement.capitalize()       # Constiinta → Constinta
    else:
        return replacement.lower()            # constiinta → constinta
```

## Execution Workflow

### Phase 1: Scan (Dry Run)
```python
# references/exec-hermes-infile-text-reprogramming/scripts/\1
python find_occurrences.py --root "C:\Users\apviz\AppData\Local\hermes" --dry-run
# Expected output: list of files + match count
```

### Phase 2: Replace
```python
# references/exec-hermes-infile-text-reprogramming/scripts/\1
python replace_occurrences.py --root "C:\Users\apviz\AppData\Local\hermes" --apply
# Apply all replacements with case preservation
```

### Phase 3: Verify
```python
# Re-run scan — expected: 0 matches
python find_occurrences.py --root "C:\Users\apviz\AppData\Local\hermes" --dry-run
# Must return: "Total matches: 0"
```

## File Types to Cover

| Extension | Description |
|-----------|-------------|
| `.md` | Skill files, memory files, SOUL.md, CONSTINTA.md |
| `.yaml`, `.yml` | Profile configs, root config |
| `.py` | MCP servers, scripts |
| `.json` | Config files, state files, task files |
| `.txt` | Log files, plain text notes |
| `.vbs`, `.cmd` | Gateway service scripts |
| `.ps1` | PowerShell automation scripts |
| `.log` | Cron output logs (check mtime-limited) |

## Always Exclude These Paths

```
OGLINDA - CASA\          ← Archive — never touch
.git\                    ← Version control metadata
venv\                    ← Python virtual environment
node_modules\            ← npm packages
__pycache__\             ← Python bytecode
*.pyc                    ← Compiled Python
```

## Scope for Hermes System

```
C:\Users\apviz\AppData\Local\hermes\          ← Primary
C:\Users\apviz\OneDrive\Documents\Antigravity_Folder\Antigravity_Projects\  ← Skills/config
C:\Users\apviz\AppData\Local\hermes\cron\     ← Cron logs (separate pass)
```

## Reference Files

- [REPLACEMENT_PATTERNS.md](references/REPLACEMENT_PATTERNS.md) — All known variant patterns
- [EXCLUDED_PATHS.md](references/EXCLUDED_PATHS.md) — Paths to always skip
- [CASE_LOGIC.md](references/CASE_LOGIC.md) — Case preservation rules
- [find_occurrences.py](references/exec-hermes-infile-text-reprogramming/scripts/\1) — Dry-run scanner
- [replace_occurrences.py](references/exec-hermes-infile-text-reprogramming/scripts/\1) — Case-aware bulk replace
- [fix_word_boundary_regex.py](references/exec-hermes-infile-text-reprogramming/scripts/\1) — Boundary pattern reference