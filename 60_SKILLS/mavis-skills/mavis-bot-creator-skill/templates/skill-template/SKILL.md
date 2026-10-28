---
name: mavis-session-<artifact>-skill
description: <ONE PARAGRAPH — what it extracts, from which source, when to load it, and exactly what it produces. Written so the router can decide from this line alone whether this is the right skill.>
role: functional
source: <source-id>
bot: mavis-session-extract-bot-skill
---

# mavis-session-<artifact>-skill

<One sentence: what this extracts and from where.>

## Why this skill exists

<The real defect it solves, not the feature it adds. What was being done wrong or lost
before it existed — with the measurement that proves it.>

## STEP 1 — resolve the session

<How the session is identified and what the command is.>

## STEP 2 — extract

<The exact command, with its real flags and defaults.>

```powershell
node "<abs path>\<extractor>.mjs" --session <id> --out "<dir>" --title "<name>"
```

| Flag | Meaning |
|---|---|
| `--session <id>` | ... |
| `--out <dir>` | ... |
| `--title <name>` | ... |

## STEP 3 — verify (do not skip)

```powershell
node "<abs path>\<verifier>.mjs" --session <id> --out "<dir>" --title "<name>"
```

<What it re-queries and what it proves.>

## What the extractor guarantees

1. ...
2. ...
3. ...

## Known limits — say them out loud, do not hide them

- **...** — <the limit, and what to do instead.>

## Measured facts

| Fact | Measured | When |
|---|---|---|
| ... | ... | ... |

## Doctrine this skill obeys

- **Tool before words.**
- **A check that cannot fail is not a check.**
- **No silent loss.**

## Run log

Every use of this skill is recorded in [`runs.md`](runs.md) — append-only: the measured
success with its numbers, or the error verbatim. When a run teaches this skill something
new, this file is updated in place with the evidence.

**Bot:** [`mavis-session-extract-bot-skill`](../mavis-session-extract-bot-skill/SKILL.md) —
the hub that owns the list, the contract and this update loop.
