# Protocol — JURNAL_OGLINDA (Reality Anchor, Append-Only)

**Status**: ✅ WIRED (core doctrine, codified in `SENTINEL_OPERATIONAL_DOCTRINE.md §8`)

## Definition

**JURNAL_OGLINDA** (Mirror Journal) is Popy's reality anchor — the historical record of what actually happened in the swarm. It is **append-only**: never edit, never delete, never silently rewrite.

## Where it lives in this project

JURNAL_OGLINDA entries are appended to the relevant `40_REGISTRIES/40_partition_*.md` file under a `## JURNAL_OGLINDA` heading. Each entry is timestamped.

Other JURNAL_OGLINDA surfaces (outside this project):
- The SENTINEL_JOURNAL (system-level)
- Git history (commit log is itself append-only)
- Audit logs in deployed systems

## Append rule

When an event happens that should be remembered:
1. Append a new row to the relevant JURNAL_OGLINDA table
2. Include: date, event description, notes/context
3. Never edit an existing row

## Correction rule

If a past entry is wrong, the correction is a **NEW entry** that references the old one:

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
- Mavis treats the JURNAL_OGLINDA as the source of truth for "what actually happened" — over conversation memory, over scratch notes, over best-guess reconstruction.

## JURNAL_OGLINDA

| Date | Event | Notes |
|---|---|---|
| 2026-09-18 | Protocol codified | Extracted from memory into explicit file |
