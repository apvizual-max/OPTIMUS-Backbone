# Examples: Planning Artifacts (Implementation Plans & Learning Proposals)

This reference file provides concrete templates for both Implementation Plans and Learning Proposals to show how they should look in practice.

---

## 1. Example Implementation Plan

```markdown
# Implementation Plan - Refactor Cache System

This plan details the changes to migrate our temporary in-memory image cache to a persistent SQLite-backed cache database.

## User Review Required
> [!IMPORTANT]
> The database migration requires write access to the user's Local AppData folder. Ensure Developer Mode is active.

## Proposed Changes

### Database Layer
- **[NEW] [cache_db.py](file:///C:/Users/apviz/projects/cache_db.py)**: SQLite schema definition and access methods.

### Application Logic
- **[MODIFY] [image_loader.py](file:///C:/Users/apviz/projects/image_loader.py)**: Replace the `dict` cache with calls to `cache_db.py`.

## Verification Plan
- Run `pytest tests/test_cache.py` to verify caching logic.
```

---

## 2. Example Learning Proposal

```markdown
# Learning Proposal: Enforce Path Separator Rules

This proposal defines new system guidelines to ensure path separators are always written as single backslashes on Windows platforms.

## 1. Classification
* **Type**: Global Rule.
* **Target**: Append to `AGENTS.md`.

## 2. Rationale
* **Issue**: The agent occasionally writes doubled `\\` in paths, breaking NTFS link resolution.
* **Fix**: Force a strict rule enforcing single backslashes `\`.

## 3. Proposed Additions
Append the following to `AGENTS.md`:
```diff
+ ### 5. Path Separators Rule
+ - Always use single backslashes (`\`) for Windows paths (e.g. `C:\Users\apviz\Local`). Never use double backslashes (`\\`).
```
```
