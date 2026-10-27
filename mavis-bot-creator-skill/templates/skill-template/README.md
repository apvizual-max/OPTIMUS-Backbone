# What a member skill's folder contains

Copy `skill-template/` and fill it in. This file explains the shape.

```
mavis-session-<artifact>-skill\
  SKILL.md            the procedure: how to run it, what it guarantees, what it cannot do
  <extractor>.mjs     reads the source, writes the fixed output shape
  <verifier>.mjs      re-queries the source, proves coverage, exits non-zero on a gap
  runs.md             append-only log: every use, with its numbers or its verbatim error
  raw\                (created at run time) verbatim copies of the source's sidecar files
```

## The rules each file lives by

**`SKILL.md`** — frontmatter must carry `name` (== folder name), `description`, `role`
(`functional` | `meta`), `source`, and `bot: mavis-session-extract-bot-skill`. The body
must state the procedure, the guarantees, and the **known limits**. The bot's registry
verifier fails a member whose `SKILL.md` does not mention the bot.

**The extractor** — Node builtins only. Opens the source **read-only**. Freezes the
boundary of a live session. Emits `<title>.md`, `<title>.jsonl`, `manifest.json`, `raw\`.
Inlines externalised tool output. Declares gaps instead of dropping them. Exits non-zero
if its own accounting does not add up.

**The verifier** — a **separate** script that re-queries the source. It must not share
the extractor's parsing code, or it verifies itself. Checks V1–V8 are in the bot's
`SPEC.md` §6. Exit `0` = proven, `1` = a named gap, `2` = not measurable.

**`runs.md`** — append-only. One entry per use. Successes carry their numbers; errors
carry the error verbatim. A correction is a new entry that references the old one.

## The fixed output shape (identical for every member)

```
<target>\
  <title>.md          full readable transcript text
  <title>.jsonl       full machine-readable transcript, one object per message
  manifest.json       provenance, byte accounting, explicit gaps[]
  raw\                verbatim copies of the source session's own sidecar files
```
