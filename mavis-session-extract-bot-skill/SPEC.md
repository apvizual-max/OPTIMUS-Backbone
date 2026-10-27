# SPEC — Mavis Session Extract Bot

**Version:** 1.0 · **Status:** WIRED (1 functional member + 1 meta member) · **Owner:** `mavis-session-extract-bot-skill`

The technical contract behind `SKILL.md`. `SKILL.md` says *what the bot is and how it
behaves*; this file says *what a member skill must produce and how it is checked*.
A member skill that does not satisfy this contract is not linkable.

---

## 1. Scope

The bot extracts **session transcripts**. A "session" is a conversation between a human
(or an agent) and an AI runtime, as recorded by that runtime. The bot covers any source
whose conversation can be traced — local stores, databases, cloud APIs, browser sessions.

**Out of scope:** summarising, analysing, scoring, or re-authoring a session. The bot
produces the record. Interpretation is somebody else's job.

---

## 2. The universal data model

Every source is normalised into the same model. A member skill's job is to produce it.

```
Session
 ├─ id            string   the source's own session identifier
 ├─ title         string   display title (requester may override)
 ├─ agent         string   which AI produced the session
 ├─ runtime       string   the harness ("pi-agent", "cli", "web", ...)
 ├─ created_at    int64    epoch ms
 ├─ updated_at    int64    epoch ms
 ├─ workspace     string   the working directory, if the source records one
 └─ messages[]    Message   ordered by the source's own sequence
```

```
Message
 ├─ seq           int      1-based position in the extracted transcript
 ├─ id            string   the source's own message id (row id, uuid, ...)
 ├─ role          enum     user | assistant | tool-result | system-event
 ├─ turn_id       string   the turn/session grouping, if the source has one
 ├─ timestamp_ms  int64    epoch ms
 ├─ content       string   the visible text
 ├─ thinking      string   the reasoning text, if the source records it
 ├─ tool_calls[]  ToolCall
 └─ usage         object   token counts, if the source records them
```

```
ToolCall
 ├─ tool_name     string
 ├─ tool_call_id  string
 ├─ status        int|enum
 ├─ args          string   raw arguments, verbatim
 └─ result        Result
```

```
Result
 ├─ text          string   the output the model actually saw
 ├─ artifact      object   externalised output: { status, path, resolved, bytes, sha256, text }
 └─ text_file     object   a pointer the source truncated: { path }
```

**Normalisation rules**

1. **Order is the source's order.** Never re-sort by timestamp — a source's sequence is
   authoritative and timestamps can tie or skew.
2. **Arguments and results are verbatim.** The bot normalises structure, never content.
3. **A receipt is not content.** If a tool result says the output was externalised, the
   real payload must be fetched and embedded (see §5).
4. **A missing thing is `UNKNOWN`, not empty.** If the source does not record it, the field
   is absent and the fact is stated — never silently dropped.
5. **The original row is preserved.** The JSONL keeps the source's raw payload alongside the
   normalised one, so any normalisation decision can be audited.

---

## 3. Output shape (fixed for every member skill)

```
<target>\
  <title>.md          full readable transcript text
  <title>.jsonl       full machine-readable transcript, one object per message
  manifest.json       provenance, byte accounting, explicit gaps[]
  raw\                verbatim copies of the source session's own sidecar files
```

- `<target>` — **the location the requester named.** Binding; never overridden.
- `<title>` — the requester's name, else the source session's own title.
- `raw\` — whatever the source itself kept (message log, snapshots, externalised tool
  outputs, catalogs, locators). Copied byte-for-byte, never rewritten.

---

## 4. `manifest.json` schema

```jsonc
{
  "schemaVersion": 1,
  "artifact": "<source-specific artifact kind>",
  "title": "...",
  "session_id": "...",
  "original_title": "...",
  "agent_name": "...",
  "runtime": "...",
  "created_at_ms": 0, "updated_at_ms": 0,
  "window_local": ["YYYY-MM-DD HH:MM:SS", "..."],
  "workspace_dir": "...",
  "extracted_at": "ISO-8601",
  "extractor": "<script name + version>",
  "sources": {
    "sqlite": "<path or null>",
    "table": "<table name or null>",
    "row_id_max": 0,            // the frozen boundary of a live session
    "session_dir": "<path or null>"
  },
  "counts": {
    "message_rows_read": 0,
    "messages_rendered": 0,
    "by_role": { "user": 0, "assistant": 0 },
    "tool_calls": 0,
    "externalized_artifacts": 0,
    "externalized_artifacts_inlined": 0,
    "inline_artifact_bytes": 0,
    "distinct_read_file_pointers": 0,
    "tokens_in": 0, "tokens_out": 0, "tokens_cache_read": 0
  },
  "outputs": { "markdown": "...", "jsonl": "...", "manifest": "...", "raw_copies": [] },
  "gaps": [],                   // EMPTY IS A MEASURED RESULT, NEVER AN ASSUMPTION
  "read_file_pointers": []
}
```

**Mandatory keys:** `session_id`, `extracted_at`, `extractor`, `sources`, `counts`,
`gaps`. A member skill that omits any of them is not linkable.

---

## 5. Externalised output — the rule that decides whether a transcript is real

A source that writes large tool output to a file and leaves a **pointer** in the message
has produced a receipt, not content. A transcript that keeps the receipt has lost the data.

**Required behaviour of every member skill:**

1. Detect the pointer (`[Tool output externalized`, `rawOutputPath`, `textFile`, or the
   source's equivalent).
2. Resolve it to a real path. If the pointer is **relative**, it may name an artifact
   written while a *different* session was active — resolve it against the source's own
   artifact directory **and** against a global index of that directory (names are
   content-addressed, so the same name is the same bytes).
3. Embed the file's content, with its byte count and sha256.
4. If it cannot be resolved → push a gap of kind `EXTERNALIZED_OUTPUT_MISSING` into
   `gaps[]`, naming the path. **Never** silently keep the receipt as if it were the output.

---

## 6. Coverage verification contract

Every member skill ships a verifier that **re-queries the source** — it must not read the
extractor's own output and declare itself right.

**Mandatory checks**

| # | Check | Fails when |
|---|---|---|
| V1 | rows read == rows rendered | any message dropped |
| V2 | last rendered id == the frozen max id | the snapshot's boundary is not honoured |
| V3 | tool-call count: source == transcript | any call dropped or invented |
| V4 | per-tool-name counts: source == transcript | calls silently swapped between tools |
| V5 | one markdown section per message | the readable text lost a message |
| V6 | every user message's opening text present in the markdown | text truncated or dropped in rendering |
| V7 | `gaps[]` empty **or** every gap explicitly declared | a silent hole |
| V8 | JSONL lines parse | a corrupt line |

**Exit codes:** `0` = coverage proven · `1` = a gap exists (named) · `2` = not measurable.

**Falsification is mandatory.** Before a member skill is linked, prove its verifier can
fail: corrupt a copy (drop rows) → the verifier must reject it and name the defects.
A verifier that has never gone red is not evidence of anything.

---

## 7. The adapter interface — what a new member skill must implement

Any member skill is runnable as:

```
node <skill>/<extractor>.mjs --session <id> --out <dir> --title <name> [...]
```

and must accept at least:

| Flag | Meaning |
|---|---|
| `--session <id>` | the source's session identifier |
| `--out <dir>` | target directory (created if absent) |
| `--title <name>` | the output name |
| `--data-dir <path>` | where the source's store lives (default: the runtime's own) |

and must exit with the taxonomy in §9.

**The member skill must also ship:**
`SKILL.md` (frontmatter + procedure + measured facts + known limits) · the extractor ·
the verifier · `runs.md` · `SPEC` additions if it introduces a new source shape.

---

## 8. Registry and run-log schemas

**`registry.json`** (in the bot skill) — see §3 of the bot's `SKILL.md` for the human table.
Machine shape:

```jsonc
{
  "schemaVersion": 1,
  "bot": "mavis-session-extract-bot-skill",
  "naming": { "functional": "...", "meta": "...", "rule": "..." },
  "frontmatter_required": ["name", "description", "role", "bot"],
  "output_contract": { "md": "...", "jsonl": "...", "manifest": "...", "raw": "..." },
  "skills": [
    { "name": "...", "role": "functional|meta", "source": "...", "purpose": "...",
      "status": "WIRED|BLUEPRINT|BLOCKED", "path": "", "added_at": "...", "verified": "..." }
  ],
  "planned_sources": [ { "source": "...", "status": "PLANNED", "note": "..." } ]
}
```

**`<skill>/runs.md`** — append-only. One entry per use:

```markdown
## 2026-10-28 01:20:33 — success — <what was attempted>
- source: <sourceId>
- session: <id>
- outcome: <measured result>
- error: <verbatim, only on failure>
- logged-by: mavis-session-extract-bot-skill
```

**Rules:** success entries carry their **numbers** (counts, bytes, verifier exit code, the
path produced). Error entries carry the error **verbatim**. A correction is a new entry
that references the old one — nothing above is rewritten.

---

## 9. Error taxonomy (machine codes)

| Code | Exit | Meaning |
|---|---|---|
| `SOURCE_NOT_FOUND` | 2 | the source's store could not be located |
| `SOURCE_NOT_TRACEABLE` | 2 | the session could not be traced inside the store |
| `NO_LOCAL_ROWS` | 3 | cloud-only session → use `mavis session messages --source cloud` |
| `OUTPUT_EXISTS` | 2 | the target already holds an extraction; do not overwrite silently |
| `VERIFY_FAILED` | 1 | the independent verifier rejected the artifact |
| `INCOMPLETE_COVERAGE` | 1 | fewer rows rendered than the source holds |
| `EXTERNALIZED_OUTPUT_MISSING` | 0 (declared as a gap) | an externalised output is no longer on disk |
| `DEPENDENCY_MISSING` | 2 | a required runtime/tool is absent |
| `UNKNOWN` | 2 | not measurable — reported as unknown, never as empty |

---

## 10. Environment and dependencies

| Dependency | Used by | Constraint |
|---|---|---|
| Node >= 22 (`node:sqlite`, `node:crypto`) | every extractor | **no third-party npm packages** |
| the source's own store | per source | opened **read-only**; never written |
| the native `mavis` tool | session identity, cloud sources | `session get` / `session messages --source cloud` |
| `mcode-tools` CLI | media/document conversion | loaded via its own skill on demand |
| browser control | web-based sources | loaded via its own skill on demand |

---

## 11. The update loop (normative)

1. After **every** extraction, `log-run.mjs` appends to the member skill's `runs.md`.
2. If the run taught the member skill a **lesson** (a wrong path, a missing flag, a source
   that misreports its storage), the member's `SKILL.md` is updated in place — additively,
   with the evidence.
3. If the lesson changes the **bot's** contract (shape, naming, location, dependencies),
   this file and the bot's `SKILL.md` are updated too, and the run is logged in the bot's
   own `logs/`.
4. `bot-registry.mjs verify` must exit 0 after every change.

---

## 12. Provenance requirements

- The manifest must name the **exact source paths** and the **table** read, so a third
  party can re-derive the artifact.
- The frozen boundary (`row_id_max`) must be recorded for any live session, so the
  artifact is a reproducible snapshot and not a moving target.
- The extractor name and version go in `extractor`.
- Byte counts are **measured**, never estimated.
