---
name: mavis-jurnal-oglinda-skill
description: JURNAL_OGLINDA append-only reality anchor. Load when recording an event that Popy will need to remember later: bridge activations, doctrine amendments, incidents, subscription changes, CODUL SACRU ratifications, source-material location additions.
role: functional
bot: mavis-local-optimus-ci-bot
---

# mavis-jurnal-oglinda-skill

The Mirror Journal — Popy's reality anchor. Append-only. Never edit, never delete, never silently rewrite.

## Where entries live

In this project: `C:/Users/apviz/.minimax-agent/projects/Mavis-Optimus-Dashboard/40_REGISTRIES/40_partition_*.md` — each file has a `## JURNAL_OGLINDA` section at the bottom.

Outside this project: SENTINEL_JOURNAL, git history, audit logs — all append-only by nature.

## Append rule

When an event happens that should be remembered:
1. Append a new row to the relevant JURNAL_OGLINDA table.
2. Include: date, event description, notes/context.
3. **Never edit an existing row.**

## Correction rule

If a past entry is wrong, the correction is a **NEW entry** that references the old by timestamp + excerpt:

```
| 2026-09-18 | Correction to 2026-08-08 swarm-loss entry | Root cause was `docker container prune -a`, not `docker image prune`. See original entry. |
```

The old entry stays. The correction is a new entry that points at it.

## What goes in JURNAL_OGLINDA

- ✅ Bridge activations / deactivations
- ✅ Subscription tier changes
- ✅ Architectural decisions (especially CODUL SACRU)
- ✅ Incidents and their resolution
- ✅ Doctrine amendments
- ✅ Source-material location additions
- ❌ Routine session activity
- ❌ Transient task status
- ❌ Ephemeral debug output

## Mavis's posture

- Mavis appends, never edits.
- Mavis surfaces drift if it detects apparent edits elsewhere.
- Mavis treats the JURNAL_OGLINDA as source of truth over conversation memory, over scratch notes, over best-guess reconstruction.

## Cross-references

- Doctrine: `SENTINEL_OPERATIONAL_DOCTRINE.md §8`
- Protocol file: `C:/Users/apviz/.minimax-agent/projects/Mavis-Optimus-Dashboard/20_PROTOCOLS/20_jurnal_oglinda.md`
