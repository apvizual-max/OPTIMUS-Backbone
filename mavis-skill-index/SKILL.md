---
name: mavis-skill-index
description: Master skill index for Mavis. Single point of truth over ALL skills Mavis can call — the 1,279 personal skills at C:\Users\apviz\.minimax\skills\, the 60 mavis-* skills, and the 21 builtin skills. Use this when Mavis needs to autonomously pick the right skill for a task without manual loading. Includes routing procedure + self-update procedure so Mavis learns and amends the index over time.
---

# mavis-skill-index

**The single point of truth for ALL of Mavis's skill capabilities.** This skill does not encode a workflow — it encodes Mavis's autonomous routing logic + a 1,279-row classifier table that Mavis reads to pick the right skill(s) for any given task. The counts below are the measured ones; if a number here disagrees with a count taken from disk, the number here is wrong — fix it, do not reconcile it.

## What this skill owns

| Skill source | Count | Where it lives |
|---|---|---|
| **Personal skills** (Popy's library) | **1,279** | `C:\Users\apviz\.minimax\skills\<name>\SKILL.md` |
| Mavis agent skills | 60 (incl. 4 bundles) | `C:\Users\apviz\.minimax\agents\mavis\skills\` |
| MiniMax builtins | 21 | `C:\Users\apviz\.minimax\.builtin-skills\` |
| **Total** | **1,339** | (overlapping categories — Mavis picks per task) |

## SENTINEL PRIME skills (installed 2026-10-04)

Five skills covering the SENTINEL persona and its embodiment. They were written
into `SENTINEL_PRIME\07_BACKBONE\skills\` and **were not loadable** — a project
folder is not a skill root, and they had no `name:`/`description:` frontmatter.
Both defects are fixed; `install_skills.py` now deploys project → runtime root.

| Skill | Load when |
|---|---|
| `mavis-sentinel-prime-on-minimax-skill` | deploying SENTINEL to MiniMax, or reviewing a SENTINEL check |
| `mavis-sentinel-prime-role-skill` | acting as SENTINEL; the doctrine, not the procedure |
| `mavis-sentinel-bimodal-workflow-skill` | a SENTINEL task mutates state (MODE_A/R0/MODE_B/STOP) |
| `mavis-tany-llm-to-sentinel-skill` | adapting a model or agent onto the SENTINEL pattern |
| `mavis-sentinel-command-center-skill` | the dashboard, the link, or interpreting a panel verdict |

**Re-install after editing any of them:**
`python SENTINEL_PRIME\08_SELF_IMPROVEMENT\install_skills.py` — a file in the
project folder is a document until that runs.

## Routing procedure (autonomous, no user input needed)

When a user request arrives, Mavis follows this exact algorithm — **every step, every turn, no shortcuts**:

### Step 1 — Classify the task into one of 4 categories

| Category | Trigger keywords | What it is |
|---|---|---|
| **Identity and File Locations** | "where is", "find", "locate", "path", "which file", "what's in", "memory" | A question about WHERE something lives or WHAT Mavis knows |
| **Behavioral** | "review", "evaluate", "validate", "audit", "plan", "decide", "should I" | A question about HOW to act / what's the discipline |
| **Role Definition** | "expert", "specialist", "master", "agent persona", "voice", "tone" | A question about WHO Mavis is or who the bridge should play |
| **Operations** | "do", "create", "generate", "build", "make", "send", "fetch", "run", "deploy", "search for" | A task to be DONE — produce, transform, or act |

If the task spans categories, **load bundles from each relevant category** — they don't conflict.

### Step 2 — Load the bundle for the category

Each bundle's SKILL.md lists the right member skills for that scope. Bundles are meta-skills that don't carry content — they point at the right member:

| Category | Bundle to load |
|---|---|
| Identity and File Locations | `mavis-bundle-identity` |
| Behavioral | `mavis-bundle-behavioral` |
| Role Definition | `mavis-bundle-role` |
| Operations | `mavis-bundle-operations` |

### Step 3 — Pick the right SKILL from the full classifier table

The classifier table lives at `C:\Users\apviz\.minimax-agent\projects\70_CONNECTORS\70_personal_skill_index.md` (242 KB, full per-category lists).

Procedure:

1. Read the relevant category section of the classifier table (skip irrelevant categories).
2. Compare the task description against each skill's description in that category.
3. Score by: name match (high), trigger keyword match (medium), description overlap (low).
4. Pick the **top 1-3 candidates**. Don't load more than 3 personal skills per task — that's the autonomous selection budget.
5. If no candidate fits cleanly, fall back to the bundle's member skills (the 18 mavis-* + 22 builtins).

### Step 4 — Load via `skill({ name: "<candidate>" })`

Each candidate is a SKILL.md at `C:\Users\apviz\.minimax\skills\<candidate>\SKILL.md`. The runtime loads it.

### Step 5 — Apply discipline

Before executing the task:
- `mavis-r33-bimodal-skill` — is this Mod A (analyze) or Mod B (execute)? Does it need R0?
- `mavis-triple-crunch-skill` — does the output pass Eminescu ABBA ∧ Eliade Realitate ∧ Musashi Taiere?
- `mavis-deliverable-handoff-skill` — emit `<media />` for any file deliverable.

### Step 6 — Log to JURNAL_OGLINDA

Append a JURNAL entry to `C:\Users\apviz\.minimax-agent\projects\40_REGISTRIES\40_partition_C_system.md` with:
- Task description (1 line)
- Skills loaded (which candidates + which bundles)
- Outcome (PASS / FAIL / partial)
- Any lesson learned → triggers Step 7

### Step 7 — Self-update (the lesson loop)

If a skill was **especially useful or useless** for the task, Mavis records it:

```
## YYYY-MM-DD: Skill scoring update

| Skill | Was useful? | Why | Action |
|-------|-------------|-----|--------|
| <skill-name> | YES / NO | <reason> | NOTE / DEMOTE / REPLACE |
```

Append this to `C:\Users\apviz\.minimax-agent\projects\70_CONNECTORS\70_personal_skill_index.md` under a `## Lesson log` section.

When the lesson log grows past ~10 entries, Mavis should **rebuild the classifier** by:

1. Running `Get-ChildItem C:\Users\apviz\.minimax\skills\ -Filter SKILL.md -Recurse | Select-String '^description:'` to refresh descriptions.
2. Re-applying the heuristic classifier (Identity / Behavioral / Role / Operations).
3. Writing the updated table back to `70_personal_skill_index.md`.
4. Appending a JURNAL entry to `40_REGISTRIES/40_partition_C_system.md`.

## Anti-patterns

- ❌ Loading all 1,159 skills into context. That would burn tokens and exceed the model's window. Mavis must select 1–3 per task.
- ❌ Skipping the bundle layer. The bundles enforce scope + prevent category confusion.
- ❌ Asking Popy to choose a skill. The whole point is autonomous selection.
- ❌ Editing personal SKILL.md files directly. They belong to Popy's library. Mavis only amends the classifier index.
- ❌ Inventing skill names. Every skill Mavis loads must exist in the classifier or the bundle.
- ❌ Using a personal skill when a mavis-* or builtin skill exists. Personal skills fill gaps; bundles cover common cases.

## Cross-references

- Classifier data: `C:\Users\apviz\.minimax-agent\projects\70_CONNECTORS\70_personal_skill_index.md`
- 4 bundles: `mavis-bundle-identity`, `mavis-bundle-behavioral`, `mavis-bundle-role`, `mavis-bundle-operations`
- Skill taxonomy: `C:\Users\apviz\.minimax-agent\projects\00_INDEX\00_skill_taxonomy.md`
- JURNAL_OGLINDA target: `40_REGISTRIES/40_partition_C_system.md`
- Doctrine: `SENTINEL_OPERATIONAL_DOCTRINE.md §6` (SOUL ↔ CONSTINTA — every output emits SOUL first, CONSTINTA second)
