---
name: mavis-skill-index
description: Master skill index for Mavis. Single point of truth over ALL skills Mavis can call — the 1,307 personal skills at C:\Users\apviz\.minimax\skills\, the 80 mavis-agent skills, and the 21 builtin skills. Use this when Mavis needs to autonomously pick the right skill for a task without manual loading. Includes routing procedure + self-update procedure so Mavis learns and amends the index over time.
---

# mavis-skill-index

**The single point of truth for ALL of Mavis's skill capabilities.** This skill does not encode a workflow — it encodes Mavis's autonomous routing logic + a 1,297-row classifier table that Mavis reads to pick the right skill(s) for any given task. The counts below are the measured ones; if a number here disagrees with a count taken from disk, the number here is wrong — fix it, do not reconcile it.

## What this skill owns

| Skill source | Count | Where it lives |
|---|---|---|
| **Personal skills** (Popy's library) | **1,307** | `C:\Users\apviz\.minimax\skills\<name>\SKILL.md` |
| Mavis agent skills | 80 (incl. 4 bundles) | `C:\Users\apviz\.minimax\agents\mavis\skills\` |
| MiniMax builtins | 21 | `C:\Users\apviz\.minimax\.builtin-skills\` |
| **Total** | **1,408** | (overlapping categories — Mavis picks per task) |

**Counts measured 2026-10-28** (`dirs with SKILL.md`): personal 1,307 · mavis-agent 80 (77 `mavis-*` + 3 unprefixed, incl. the 4 bundles) · builtins 21.
The classifier table below enumerates **1,297** of the 1,307 personal skills — **10 are on disk but not yet classified** (`alex-hormozi-coach`, `brand-promo-video-generator`, `design-packaging`, `engineering-delivery-operations`, `fable-goal`, `i-have-adhd`, `pkms-vault-administration`, `pkms-vault-index`, `stop-slop`, `study-book-design`). The weekly rebuild will pick them up; until then, read their `SKILL.md` directly.

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

## Session & record skills

| Skill | Load when |
|---|---|
| `mavis-session-extract-bot-skill` | **THE HUB for any session-extraction request** — the Mavis Session Extract Bot: the list of member skills, the shared contract (C1–C7), the naming format, the location contract, and the update loop that writes each run's outcome back into the skill that did the work. Load it FIRST, then it dispatches to the right member |
| `mavis-session-transcript-skill` | extracting / archiving / handing over the **full** transcript of a session — every message, thinking block, tool call and the tool outputs the runtime externalised to disk |
| `mavis-bot-creator-skill` | creating and linking a **new** member skill for the Mavis Session Extract Bot — locating a source, writing the extractor + independent verifier, proving the verifier can fail, and linking it into the registry |
| `mavis-session-lifecycle-skill` | session open / close discipline (BUSOLA, read order, close-out) |
| `mavis-deliverable-handoff-skill` | packaging a finished artefact so Popy can actually use it |
| `mavis-journal-oglinda-skill` | append-only reality anchor (`JURNAL_OGLINDA`) |

## Optimus CI — local ↔ cloud (28 oct 2026)

| Skill | When to load |
|---|---|
| `mavis-local-optimus-ci-bot` | **THE HUB for anything touching Optimus CI** — the Mavis Local Optimus CI Bot: role, personality, 9 functions, tools, and the **indexed list of the secondary skills**. Load it first for the server, the local↔cloud bridge, the Drive mirror sync, the R0 publish gate, or the quarantine |
| `mavis-optimus-ci-server-skill` | the `Mavis-Optimus-CI` container, its engine, its HTTP API and the 7 MCP tools |
| `mavis-optimus-continuous-integration-skill` | the CI district: scope, boundaries and conventions for anything touching Git, GitHub, the R0 gate, the bridge, Live Review or Jules |
| `mavis-git-autonom-skill` | the daily Git working rules: main, autonomous commit, no `reset --hard`, no deletion |
| `mavis-cloud-bridge-skill` | the Local↔Cloud protocol: how information travels, and where each side stops |
| `mavis-jules-contract-skill` | the Jules boundary: who does what, and what Mavis Local never touches |
| `mavis-live-review-governance-skill` | when the automatic review runs and what its verdict means |
| `mavis-local-to-cloud-reporting` | the standard Local→Cloud report: disk + repo state, tickets in `QUEUE/`, archive by move |
| `mavis-git-vault-governance-skill` | making `git add` work on real volumes (DriveFS, bind mounts, filemode, CRLF) |
| `mavis-jurnal-oglinda-skill` | the append-only reality anchor (journal mirrored on disk) |
| `mavis-search-before-write` | every task, every session: search before the first write |

The bot's registry is executable: `node scripts\bot-doctor.mjs verify` (70 checks) and
`node scripts\bot-doctor.mjs doctor` (19 checks on the live system). It ships with its
own falsifier (`scripts\falsify.mjs`): 5/5 broken scenarios drive the verifier RED.

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

The classifier table lives at `C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\70_CONNECTORS\70_personal_skill_index.md` (306.695 B = 299.5 KB, full per-category lists, 1,297 skills enumerated).

Procedure:

1. Read the relevant category section of the classifier table (skip irrelevant categories).
2. Compare the task description against each skill's description in that category.
3. Score by: name match (high), trigger keyword match (medium), description overlap (low).
4. Pick the **top 1-3 candidates**. Don't load more than 3 personal skills per task — that's the autonomous selection budget.
5. If no candidate fits cleanly, fall back to the bundle's member skills (the 18 mavis-* listed across the four bundles — measured: identity 3, behavioral 5, role 2, operations 8; no builtin is listed as a bundle member).

### Step 4 — Load via `skill({ name: "<candidate>" })`

Each candidate is a SKILL.md at `C:\Users\apviz\.minimax\skills\<candidate>\SKILL.md`. The runtime loads it.

### Step 5 — Apply discipline

Before executing the task:
- `mavis-r33-bimodal-skill` — is this Mod A (analyze) or Mod B (execute)? Does it need R0?
- `mavis-triple-crunch-skill` — does the output pass Eminescu ABBA ∧ Eliade Realitate ∧ Musashi Taiere?
- `mavis-deliverable-handoff-skill` — emit `<media />` for any file deliverable.

### Step 6 — Log to JURNAL_OGLINDA

Append a JURNAL entry to `C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\40_REGISTRIES\40_partition_C_system.md` with:
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

Append this to `C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\70_CONNECTORS\70_personal_skill_index.md` under a `## Lesson log` section.

When the lesson log grows past ~10 entries, Mavis should **rebuild the classifier** by:

1. Running `Get-ChildItem C:\Users\apviz\.minimax\skills\ -Filter SKILL.md -Recurse | Select-String '^description:'` to refresh descriptions.
2. Re-applying the heuristic classifier (Identity / Behavioral / Role / Operations).
3. Writing the updated table back to `70_personal_skill_index.md`.
4. Appending a JURNAL entry to `40_REGISTRIES/40_partition_C_system.md`.

## Anti-patterns

- ❌ Loading all 1,307 skills into context. That would burn tokens and exceed the model's window. Mavis must select 1–3 per task.
- ❌ Skipping the bundle layer. The bundles enforce scope + prevent category confusion.
- ❌ Asking Popy to choose a skill. The whole point is autonomous selection.
- ❌ Editing personal SKILL.md files directly. They belong to Popy's library. Mavis only amends the classifier index.
- ❌ Inventing skill names. Every skill Mavis loads must exist in the classifier or the bundle.
- ❌ Using a personal skill when a mavis-* or builtin skill exists. Personal skills fill gaps; bundles cover common cases.

## Cross-references

- Classifier data: `C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\70_CONNECTORS\70_personal_skill_index.md`
- 4 bundles: `mavis-bundle-identity`, `mavis-bundle-behavioral`, `mavis-bundle-role`, `mavis-bundle-operations`
- Skill taxonomy: `C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\00_INDEX\00_skill_taxonomy.md`
- JURNAL_OGLINDA target: `40_REGISTRIES/40_partition_C_system.md`
- Doctrine: `SENTINEL_OPERATIONAL_DOCTRINE.md §6` (SOUL ↔ CONSTINTA — every output emits SOUL first, CONSTINTA second)
