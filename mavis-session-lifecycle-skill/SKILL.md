---
name: mavis-session-lifecycle-skill
description: Session open / close / between-turn discipline. Load on the first turn of a session (orientation) and on the final turn of a session (close-out). Ensures Mavis reads the right files in the right order, picks up state from prior sessions, and ends sessions cleanly with JURNAL_OGLINDA updates.
---

# mavis-session-lifecycle-skill

The opening and closing ritual for every Mavis session.

## STEP 0 — BUSOLA (mandatory, before anything else)

Read `C:\Users\apviz\.minimax\BUSOLA.md` **first, every session.**

It is the durable, on-disk answer to "unde suntem în proiect". The progress list is a
**view of that file**, never a thing rebuilt from scratch.

- If a task list already exists in this session, reconcile it against `BUSOLA.md` —
  keep every existing row, add what is missing, close what is done **with a reason**.
- If a session was compacted and rows are missing, `BUSOLA.md` is where they come back from.

**The list is a compass, not a queue. It is NEVER replaced wholesale with only the
current task.** Rewriting it loses whole threads that Popy still needs — this happened
on 2026-10-08 and cost more than the task it was meant to track. Before any
`todowrite`: re-read the current list, preserve every row, edit in place. An obsolete
row becomes `completed`/`cancelled` **with a written reason**, never deleted. After
writing, count the rows: if the number dropped without a stated reason, something was lost.

**SYSTEM IS ABOVE TASK.** When the process and the task conflict, the process wins.
Repair the process before advancing the work.

## Session-open read order (when working in this workspace)

1. `mavis-skill-index` — Pillar skill. Loads first so Mavis has the autonomous routing procedure + classifier index pointer (NEW: 2026-09-19).
2. `mavis-bundle-identity` — loads to map Mavis's skill organization (Identity and File Locations bundle).
3. `README.md` — orientation, two-layer model
4. `OPTIMUS_INDEX.md` — cheat sheet
5. `AGENTS.md` — project agent instructions
6. `SENTINEL_OPERATIONAL_DOCTRINE.md` — paste-into-UI doctrine
7. `00_INDEX/00_master_map.md` — what's where
8. `00_INDEX/00_bridge_registry.md` — bridge live state
9. `00_INDEX/00_skill_taxonomy.md` — the 4-category × 2-layer grid
10. `40_REGISTRIES/40_partition_E_aiwork.md` — SENTINEL manuals location
11. Any JURNAL_OGLINDA entries in `40_REGISTRIES/` (append-only — newest first)

For deep doctrine work, also load:
- `SENTINEL_PRIME/01_FOUNDATION/doctrine/A_FI_DOCTRINE.md`
- `SENTINEL_PRIME/02_OPERATIONAL/rituals/RITUAL_3_PROPOZITII.md`
- `SENTINEL_PRIME/03_INTELLIGENCE/algorithms/TRIPLE_FILTER_ALGORITHM.md`

For OPTIMUS Backbone work, load:
- `mavis-backbone-skill` (entry point for this project)

For operations / dispatch work, load:
- `mavis-bundle-operations` — pick the right bridge skill from the 8 members

## Bundle load discipline (NEW: 2026-09-18)

Mavis's skills are organized into 4 bundle skills. **Don't load all bundles at session-open** — load on demand based on the request shape:

| If the user asks about... | Load bundle |
|---|---|
| "where is X?" / "what is Y?" / "what happened?" | `mavis-bundle-identity` |
| "how should I do Z?" / "is this right?" | `mavis-bundle-behavioral` |
| "which AI?" / "which MCP?" / "my role?" | `mavis-bundle-role` |
| "do W" / "run T" / "fetch R" | `mavis-bundle-operations` |

Then load the **specific member skill** within the loaded bundle. Don't enumerate members — pick the right one.

## Session-open output

After reading, Mavis states the SOUL of the session — one line telling Popy what Mavis is ready for in this turn. Then wait for Popy's first request.

## Between-turn discipline

- Don't re-read `README.md` every turn after the first.
- Track state changes in JURNAL_OGLINDA.
- Don't pre-empt Popy's next request.
- Don't forget the language tier (Romanian at Popy + Prime + Assist, English below).

## Session-close (when Popy says "we're done" or session times out)

> ⚠ **The five steps below were all recording. None of them measured.** A close-out that
> cannot say "not done" is a closing ritual in name only — it reports what the agent
> believes, which is exactly what a close-out exists to stop relying on. **Step 6 was added
> 2026-10-09 after a close-out reported `FAIL` on a log that read `CERTIFIED 11/11`: the
> verdict regex required whitespace where the file had an em-dash.**

1. Append a JURNAL_OGLINDA entry to the relevant `40_REGISTRIES/40_partition_*.md` summarizing what was done.
2. If bridge state changed (enabled/disabled), reflect in `00_INDEX/00_bridge_registry.md`.
3. If doctrine was amended, note the amendment in the file's JURNAL.
4. Confirm Memory updates landed.
5. Don't promise future work — record what was actually completed.
6. **MEASURE before declaring done.** Run the measured close-out; do not report a state
   you did not read off disk.

### 6 · The measured close-out — a ritual that can say "NOT DONE"

```
node C:\Users\apviz\QWEN_BACKUP\_close-ritual.js     → exit 0 = GATA, exit 2 = NU GATA
node C:\Users\apviz\QWEN_BACKUP\_t62-ritual-gate.js  → 7/7 proves it can still fail
```

**The gate is not optional and not a formality.** A close-out that has never been shown to
fail is decoration; one that only ever says "done" is worse, because it looks like a check.
`_t62-ritual-gate.js` exists to keep the instrument falsifiable: it carries a **positive
control** (a clean state must PASS) beside six mutants (each must FAIL). If the positive
control ever fails, the instrument is broken — do not trust its negatives.

Three rules learned by building it, each found by measurement rather than reasoning:

- **The report must not be written inside the tree it measures.** Writing it there made the
  repository permanently dirty, so the ritual could never again report "clean". A
  measurement that changes what it measures measures nothing.
- **Test fixtures must be siblings, never nested.** A nested git repo becomes a gitlink,
  and every commit in the child shows up as uncommitted in the parent — the fixture
  reproduced the very recursion it was meant to test.
- **A regex that is too strict is worse than no check at all**, because a false positive
  blocks work on something already finished and looks confident doing it. Prefer a loose
  match over a precise wrong one.

### 7 · Publish only what a measurement carried

Added 2026-10-10 after this session stated "connectors: 1, I added it" — produced by
`@($null).Count = 1` in PowerShell, which returns **1** for nothing. The count was 0, proven
afterwards from three independent angles.

- **A number needs a source that can be wrong.** If the shape of the container was never
  checked, the number is text, not evidence.
- **Retract in public, immediately, naming the cause.** A silent correction leaves two
  versions of the same claim and only one of them was measured.
- **Cross-check anything that closes a state change** through a differently-shaped route —
  CLI exit text, rendered page, raw response — never through the same call again.

**Gate:** before a close-out report leaves, every number in it must trace to a command whose
output was read this session, not to what the session believes happened. This is the same
rule as step 6, applied to the *content* rather than to the verdict.

### Cross-references

- **Project compass: `C:\Users\apviz\.minimax\BUSOLA.md`** — read it first, always.
- Doctrine: `SENTINEL_OPERATIONAL_DOCTRINE.md` (§0 language, §16 workspace)
- Workflow file: **BROKEN INDICIE (2026-10-08)** — this pointed at
  `C:/Users/apviz/.minimax-agent/projects/30_WORKFLOWS/30_session_open.md`.
  That directory no longer exists on this machine. Until Popy says where the backbone
  lives, `BUSOLA.md` is the fallback. Do not treat the old path as valid.
- `mavis-full-intent-execution-skill` — execute the verb, not the topic around it
