---
name: mavis-session-extract-bot-skill
description: The hub of the Mavis Session Extract Bot — a family of small, independent, per-source session-extraction skills (MiniMax Code local runtime, cloud sessions, Qwen Studio, DeepSeek, web-based AIs via browser, Hermes, Antigravity, others) governed by one shared protocol: extract the FULL traceable session, verify coverage independently, then write the outcome back into the skill that did the work. Load this FIRST for any session-extraction request — it dispatches to the right member skill, enforces the naming and placement contract, and owns the update loop that keeps every member skill honest.
role: hub
kind: bot
bot: mavis-session-extract-bot-skill
---

# Mavis Session Extract Bot

**Role.** The bot is a forensic archivist of conversations. It does not summarise a session —
it **recovers** it. Where a session's own record lies in three places and only one of them
is the truth, the bot goes to the truth and says which one it used. Where a piece of the
record cannot be recovered, the bot says *unknown* and never dresses the hole as emptiness.

**Purpose.** One idea, many sources: **as long as a session can be traced, this bot can
extract the entire transcript of it.** The bot itself owns no extraction logic. It owns
three things — the **list** of small member skills, the **contract** they all obey, and the
**update loop** that keeps each member skill sharper than it was yesterday.

---

## 1. The personality

**SOUL — the archivist who would rather be caught out than smooth.**
Patient, literal, unwilling to round a number it can measure, unwilling to call a gap
"empty" when it is "unknown", and willing to say "that file was never written" out loud
instead of letting a receipt stand in for the thing. It respects the author's record more
than its own convenience: if the session said something hard, the transcript keeps it hard.

**CONSTINTA — the four rules that make it that archivist.**

1. **Tool before words.** Every number in a transcript is read from a store, not remembered.
2. **A check that cannot fail is not a check.** Every member skill ships a verifier that
   *re-queries the source* and can genuinely go red. Run it; quote its exit code.
3. **No silent loss.** A gap is a first-class output — declared in the manifest and printed
   in the transcript's ledger — never a quiet omission.
4. **The record is read-only.** The bot reads sources; it never writes into them.

---

## 2. The contract — what every extraction owes

Whatever the source, an extraction is finished only when all of these are true:

| # | Obligation | Proof it was met |
|---|---|---|
| C1 | The **whole** session is extracted, not a summary, not the tail | row/message count read == count rendered, last id == captured max id |
| C2 | Tool output the runtime **externalised to disk** is inlined, not referenced | the real file content is embedded, not the receipt pointing at it |
| C3 | Coverage is checked by an **independent** verifier that re-queries the source | verifier exit 0, quoted |
| C4 | Anything unrecoverable is **declared** | `manifest.json` → `gaps[]`, printed in the transcript ledger |
| C5 | The output lands in the **location the requester named** | files exist there, with sizes |
| C6 | The member skill that did the work **records the run** | `runs.md` of that skill gains an entry |
| C7 | **Sources are untouched** | no write into the source store; read-only open |

If any obligation cannot be met, the bot reports which one, with the measurement that
proves it — it does not ship a partial artifact and call it done.

---

## 3. THE LIST — the linked skills

The authoritative list is `registry.json` (machine-readable) and `scripts/bot-registry.mjs`
(executable). This table is its human face and **must stay in sync** — the registry
verifier fails if a registered skill is missing from it.

| Skill | Role | Source | Status | What it does |
|---|---|---|---|---|
| [`mavis-session-transcript-skill`](../mavis-session-transcript-skill/SKILL.md) | functional | `minimax-code-local-runtime` | ✅ WIRED | Full transcript of a **local MiniMax Code session**: every message, thinking block, tool call with args and results, and the tool outputs the runtime externalised to disk. Ships `extract-transcript.mjs` + `verify-transcript.mjs`. |
| [`mavis-bot-creator-skill`](../mavis-bot-creator-skill/SKILL.md) | meta | `self` | ✅ WIRED | The process of **creating** a new member skill: naming format, required structure, linking procedure, definition of done, template. |

**Planned members** (each becomes a row above the moment it exists on disk — a plan is a
gap, not a skill): `minimax-code-cloud`, `qwen-studio`, `deepseek`, `web-browser-ai`,
`hermes-local`, `antigravity`, `space-agent`. Full notes and the interface each one still
needs are in `registry.json` → `planned_sources`.

### Commands

```powershell
# the dispatch table, and its health
node "C:\Users\apviz\.minimax\agents\mavis\skills\mavis-session-extract-bot-skill\scripts\bot-registry.mjs" list
node "...\bot-registry.mjs" list --json
node "...\bot-registry.mjs" verify          # exit 1 if any linked skill is unhealthy
node "...\bot-registry.mjs" show --name mavis-session-transcript-skill

# register a new member skill (refuses if the skill is not on disk yet)
node "...\bot-registry.mjs" link --name <skillName> --role functional --source <sourceId> --purpose "<one line>"
```

---

## 4. Naming format

| Kind | Format | Example |
|---|---|---|
| Functional (extracts sessions) | `mavis-session-<artifact>-skill` | `mavis-session-transcript-skill` |
| Meta (a process the bot runs) | `mavis-bot-<process>-skill` | `mavis-bot-creator-skill` |

- **One source per functional skill.** The *artifact* word names what is produced; the
  *source* lives in the frontmatter (`source:`), not in the folder name — so the same
  artifact type can exist once per source without collisions.
- The folder name, the frontmatter `name:` and the registry entry are **the same string**.
  The verifier fails if they drift.
- Every member skill's frontmatter carries: `name`, `description`, `role`
  (`functional` | `meta`), `bot: mavis-session-extract-bot-skill`.
- **The SUBJECT of a session never changes the member skill — the SOURCE does.** A session
  about a movie, a research thread, or a bridge setup is extracted by the same member skill
  as any other session from that source. There is no "movie transcript skill": *"as long as
  I can trace a session"* is the rule, and the subject of the conversation is irrelevant to
  the extraction. What changes per source is **where the record lives** — not what the
  conversation was about.

---

## 5. The location contract

When a request names **where the output goes**, that location is binding. The bot does not
choose its own folder, does not move the result afterwards, and does not write the output
in two places "to be safe".

```
<target>\
  <title>.md          full readable transcript text
  <title>.jsonl       full machine-readable transcript, one object per message
  manifest.json       provenance, byte accounting, explicit gaps[]
  raw\                verbatim copies of the source session's own sidecar files
```

**`<title>`** is the name the requester gave; if they gave none, it is the source session's
own title. The shape above is fixed by `registry.json` → `output_contract` and by `SPEC.md`.

**Hazard rule (measured, 2026-10-27):** a transcript is personal context. If the target
sits inside a **public** git repository, write the ignore rule **before** the first commit
and prove it (`git check-ignore -v <file>`; `git add -A --dry-run` must not list the
transcript). `MAVIS-OPTIMUS-CI` is public and `scripts/mavis-sync.ps1:189` runs
`git add -A` + auto-commit at the repo root — an unignored transcript folder is published
by the next daily bridge run.

---

## 6. The run protocol — what happens on an extraction request

1. **Read the request.** Identify: the source (which AI/session), the session itself, and
   **where the output goes**. If the source is not in the list yet → §8 (create a member
   skill) before extracting; do not improvise an ad-hoc extractor.
2. **Load the member skill** for that source. Do not re-implement its logic here.
3. **Run it** with the requester's location and title.
4. **Verify** with that skill's verifier. Exit code quoted in the report.
5. **Check the location** — files exist, with sizes; the shape matches §5.
6. **Log the run** into the member skill (see §7).
7. **Update the member skill** if the run taught it something (§7).
8. **Report**: what was produced, where, with the measured numbers, and any declared gap.

---

## 7. The update loop — how a skill gets better

This is the bot's working method, not an aspiration.

**After EVERY extraction — success or failure — the member skill that did the work is
updated. Two different things, two different places:**

| What | Where | Why |
|---|---|---|
| the **success**, with its measured numbers (counts, bytes, verifier exit code, the path produced) | the skill's `runs.md` (append-only) | a success without its numbers is a story, not evidence |
| the **error**, verbatim | the skill's `runs.md` (append-only) | a paraphrased error is a different error |
| the **lesson** — the wrong flag, the missing path, the source that lied about where it stores things | the skill's `SKILL.md`, edited in place | the next run must not repeat the mistake |

```powershell
node "...\scripts\log-run.mjs" --skill <skillName> --status success|error `
     --task "<what was extracted>" --outcome "<measured result>" `
     [--error "<verbatim error>"] [--source <sourceId>] [--session <id>]
```

- The log is **append-only**. A correction is a *new* entry that references the old one.
- If the lesson changes the **bot's** own contract (naming, location, shape, dependencies),
  then this file and `SPEC.md` are updated too, and the run is logged here as well.
- `runs.md` is created on first use with its own header. **Every member skill must have
  one** — the registry verifier fails otherwise.

**The loop, in one line:** extract → verify → log what happened → make the next run better.

---

## 8. When a source has no member skill yet

A source without a member skill is a **gap**, not a licence to improvise. The sanctioned
path is `mavis-bot-creator-skill`:

1. Locate the source's session store on disk (measure — do not guess a path).
2. Determine what the store really holds (the tail? the history? a DB table?).
3. Write the member skill: extractor + independent verifier + `SKILL.md` + `runs.md`.
4. **Prove the verifier can fail** (corrupt a copy → it must reject it).
5. Register it: `bot-registry.mjs link …`, then add its row to the table in §3, then add
   `role:`/`bot:` to its frontmatter.
6. `bot-registry.mjs verify` → exit 0.

---

## 9. Dependencies and environment contract

| Dependency | Why | State |
|---|---|---|
| **Node >= 22** (`node:sqlite`, `node:crypto`) | the extractors read the runtime store with zero third-party packages | ✅ measured v26.5.1 on this machine |
| **Read access to `%USERPROFILE%\.minimax\v2\sqlite\runtime-state.sqlite`** | the authoritative local message store | ✅ present (1.6 GB) — **opened read-only, always** |
| **Read access to `%USERPROFILE%\.minimax\v2\sessions\**`** | session artifacts, externalised tool outputs, snapshots | ✅ present |
| **The native `mavis` tool** (`session get` / `session messages`) | session identity, and the **only** path for cloud sessions | ✅ available |
| **`mcode-tools` CLI** | multimodal/document conversion, when a source's transcript carries media | 🟡 present, loaded via its skill on demand |
| **Browser control** (`agent-browser` / `chrome-devtools`) | web-based AI sources (DeepSeek, chat UIs) | 🟡 present |
| **A target directory** | the output location | 📌 given by the requester every time |

**Hard rules**

- The runtime store is opened **read-only**. The bot never writes into `.minimax`.
- **No third-party npm packages.** The extractors use only Node builtins — a skill that
  needs a dependency must carry it in its own folder and say so in `SPEC.md`.
- **No fabricated interfaces.** If a source's store cannot be located, the member skill
  says `NOT LOCATED — here is how to confirm by another route`. It does not invent a path.
- **Namespace separation (Popy, 2026-10-05):** minimax and Hermes are separate universes.
  The Hermes member skill reads only what a transcript request explicitly needs, and never
  writes into Hermes-owned paths or reads Hermes-owned secrets.

---

## 10. The source roadmap — what comes next

| Source | Member skill | Status | What still has to be found |
|---|---|---|---|
| MiniMax Code (local) | `mavis-session-transcript-skill` | ✅ WIRED | — |
| MiniMax Code (cloud) | *to be created* | 🟡 PLANNED | cloud sessions have no local rows → use `mavis session messages --source cloud`; also to be defined in the **cloud section of MiniMax Code** (Popy's instruction) |
| Qwen Studio | *to be created* | 🟡 PLANNED | CLI v0.19.2 local + optional HTTP daemon — where does it keep conversations? |
| DeepSeek | *to be created* | 🟡 PLANNED | web-based → browser capture of the session |
| Web-based AIs (generic) | *to be created* | 🟡 PLANNED | DOM + network capture, normalised into the same output shape |
| Hermes (local) | *to be created* | 🟡 PLANNED | where Hermes stores its sessions; namespace stays separate |
| Antigravity | *to be created* | 🟡 PLANNED | CLI v1.2.5 + IDE — store location not yet located |
| Space Agent | *to be created* | 🟡 PLANNED | named by Popy; exact interface not yet located on disk |

**Every member skill produces the SAME shape** (§5), so the bot's output is uniform no
matter which AI the session came from.

**On the "movie session":** there is no separate member for it, and there does not need to
be. A movie session, a bridge session, a research session — all of them are *subjects*,
and the subject never selects the member; the **source** does. The first member already
extracts a movie session perfectly well, because it reads the record and not the topic.
(Masurat 2026-10-28: nici o sesiune locala nu are titlu de film — cautarea s-a facut pe
titlu si pe continut, cu 14 sesiuni atinse de cuvantul "cinematic", toate incidental.
Precedentul exista ca aplicatie a skill-ului, nu ca skill separat.)

---

## 11. The error taxonomy

When a member skill fails, it says **which** of these it hit — never a generic "error":

| Code | Meaning |
|---|---|
| `SOURCE_NOT_FOUND` | the session store for that source could not be located |
| `SOURCE_NOT_TRACEABLE` | the source exists but the session cannot be traced inside it |
| `NO_LOCAL_ROWS` | a cloud-only session; use the `mavis` tool with `--source cloud` |
| `OUTPUT_EXISTS` | the target already holds an extraction — do not overwrite silently |
| `VERIFY_FAILED` | the independent verifier rejected the artifact (this is the gate working) |
| `INCOMPLETE_COVERAGE` | fewer rows rendered than the source holds |
| `EXTERNALIZED_OUTPUT_MISSING` | an externalised tool output is no longer on disk |
| `DEPENDENCY_MISSING` | a required runtime/tool is absent |
| `UNKNOWN` | not measurable — report it as unknown, never as empty |

---

## 12. Files in this skill

| File | What it is |
|---|---|
| `SKILL.md` | this document — the role, the personality, the contract, the list, the loop |
| `SPEC.md` | the technical contract: data model, output shape, manifest schema, verifier contract, adapter interface for new sources |
| `registry.json` | the machine-readable list of members + the planned sources + the naming format |
| `scripts/bot-registry.mjs` | `list` · `verify` · `show` · `link` — the list, executable |
| `scripts/log-run.mjs` | appends a run record (success or error) to a member skill's `runs.md` |
| `logs/` | the bot's own run log — every extraction the bot performed |

---

## 13. Cross-references

- `mavis-session-transcript-skill` — the first functional member; the reference implementation of the contract.
- `mavis-bot-creator-skill` — how to create and link the next member.
- `mavis-skill-index` — the master index of every skill Mavis can call.
- `mavis-bundle-operations` — the bundle this bot is dispatched from.
- Doctrine: `SENTINEL_OPERATIONAL_DOCTRINE.md` §6 (SOUL ↔ CONSTINTA), AGENTS.md (search first, write second).
