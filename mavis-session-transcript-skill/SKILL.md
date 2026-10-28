---
name: mavis-session-transcript-skill
description: Extract the FULL transcript of any MiniMax Code session — every user and assistant message, thinking blocks, tool calls with arguments and results, and the tool outputs the runtime externalised to disk. Use when asked to export / extract / archive / hand over a conversation, to send a session's record to Mavis Cloud or another AI, or to rebuild what a session actually said and did. Produces readable transcript text (.md), a machine-readable transcript (.jsonl), a provenance manifest, and a self-verifying coverage check.
role: functional
source: minimax-code-local-runtime
bot: mavis-session-extract-bot-skill
---

# mavis-session-transcript-skill

Extract the **complete** record of a session — not a summary, not the tail.

## Why this skill exists

A session's transcript lives in **three different places**, and reading only one of them
silently loses most of the conversation:

| Source | What it holds | Why it is not enough alone |
|---|---|---|
| `<dataDir>\v2\sessions\<yyyy>\<mm>\<dd>\<ts>-session_<b64>\messages.jsonl` | the **tail** of the session (post-compaction) | only the messages after the last compaction — 340 rows where the real session has 2 800 |
| `<dataDir>\v2\sessions\...\snapshots\g*.jsonl` | the **compacted working context** at each generation | 172 rows — the summarised context, not the history |
| `<dataDir>\v2\sqlite\runtime-state.sqlite` → `local_runtime_message_rows` | **every message row of the session**, in order, with full payloads | the authoritative source — read this |

`messages.jsonl` is the file everyone reaches for first, and it is the wrong one. The
database is the record.

## STEP 1 — resolve the session

```powershell
mavis session get --session-id <sessionId>
```

gives the title, agent, window and status. The session directory on disk is the
`history_relative_dir` column of `local_runtime_sessions`, relative to `<dataDir>\v2\sessions\`.
The folder name ends in `session_<base64 of the session id>`.

## STEP 2 — extract

```powershell
node "C:\Users\apviz\.minimax\agents\mavis\skills\mavis-session-transcript-skill\extract-transcript.mjs" `
  --session <sessionId> `
  --out "<target dir>" `
  --title "<the name you want the transcript to carry>"
```

| Flag | Meaning |
|---|---|
| `--session <id>` | the session id (required) |
| `--out <dir>` | where to write (required) |
| `--title <name>` | names the `.md` / `.jsonl`; defaults to the session's own title |
| `--inline-textfile` | also inline the files that `read` only partially returned (off by default — it can be tens of MB) |
| `--max-inline-bytes <n>` | cap for inlined artifacts (default 262144) |
| `--data-dir <path>` | runtime data dir (default `%USERPROFILE%\.minimax`) |
| `--quiet` | suppress progress lines |

**Output shape**

```
<out>\
  <title>.md          full readable transcript text
  <title>.jsonl       full machine-readable transcript, one JSON object per message
  manifest.json       provenance, byte accounting, and an explicit list of gaps
  raw\                verbatim copies of the session's own sidecar files
    messages.jsonl, manifest.json, history-catalog.json,
    user-message-locators.jsonl, reply-final.txt
    tool-outputs\     every externalised tool output the session owns
```

## STEP 3 — verify (do not skip)

```powershell
node "...\mavis-session-transcript-skill\verify-transcript.mjs" --session <sessionId> --out "<target dir>" --title "<name>"
```

The verifier re-queries the database independently and checks that **every** message row
and **every** tool call survived into the transcript. It exits non-zero on any gap. A
transcript that was not verified is a claim, not a deliverable.

## What the extractor guarantees

1. **Every message row is rendered.** Row count read == row count rendered, and the last
   rendered id equals the captured max id. The session may still be live: the extractor
   freezes `MAX(id)` at start so the snapshot is internally consistent.
2. **Tool outputs that the runtime externalised are inlined.** When a tool result says
   `[Tool output externalized` and points at `reports/tool-outputs\<name>.txt`, the real
   payload is read from disk and embedded in the transcript — otherwise the transcript
   would carry only a receipt saying "there is a file somewhere".
3. **Branch sessions resolve against sibling sessions.** A relative `tool-outputs\X.txt`
   reference may name an artifact written while a *different* session was active. The
   extractor indexes every `tool-outputs` directory under the sessions tree (filenames
   are content-addressed, so the same name is the same bytes) and resolves it there.
4. **Gaps are declared, never hidden.** Anything that cannot be resolved is written to
   `manifest.json` → `gaps[]` and printed in the transcript's *Completeness ledger*.
   An empty `gaps` array is a measured result, not an assumption.
5. **Everything else is preserved verbatim** — thinking blocks, token usage, tool-call
   arguments, `source` (api / background-task / questionnaire / thread-goal), and the
   full original row under `raw` in the JSONL.

## Known limits — say them out loud, do not hide them

- **Cloud-only sessions have no local rows.** The extractor exits 3 and says so; use the
  native `mavis session messages --source cloud` tool for those.
- **`read` results that were truncated by the runtime stay truncated.** The transcript
  carries the pointer the runtime produced, plus the target's existence, size and
  sha256 at extraction time. `--inline-textfile` inlines the body of files that still
  exist; files deleted since the session are reported as `NOT ON DISK AT EXTRACTION TIME`.
  This is a limit of the *session record*, not of the extractor.
- **The transcript can be large.** A 16-day session with 3 200+ tool calls is ~17 MB of
  markdown and ~18 MB of JSONL. That is the size of the record, not padding. Measured
  ceiling so far — a **46-day** branch session (2026-09-11 → 2026-10-28, 5 716 rows,
  5 492 tool calls) came out at **21 479 246 B** markdown + **23 362 364 B** JSONL +
  **10 690 867 B** of raw sidecars = **55 582 434 B across 126 files** (53,01 MB).
  Budget ~60 MB per extraction and check the free space before starting.
- **Branch sessions reach outside their own folder.** The artifact index for the run
  above covered **570 files across 10 `tool-outputs` directories** — files written by
  sibling sessions, resolved by content-addressed name. The `raw\` folder in the
  deliverable carries only what this session owns (123 files in that run); the rest are
  inlined into the transcript body.
- **Times are Europe/Bucharest** in the rendered text; the JSONL carries both the epoch
  ms and the local rendering.
- **Cleaning the falsification copy on Windows needs the recoverable route.** The
  PowerShell shell resolves `rm` to the `Remove-Item` alias, which the safety gate
  refuses (permanent delete, no Recycle Bin). Use the trusted launcher instead:
  `ELECTRON_RUN_AS_NODE=1` + `MiniMax Code.exe` + `bin\mavis-trash.js` — the same call
  `bin\mavis-trash.cmd` makes. The scratch copy of a control must not be deleted with a
  permanent command.

## Doctrine this skill obeys

- **Tool before words.** The counts in the ledger are measured from the store, not typed.
- **A check that cannot fail is not a check.** `verify-transcript.mjs` is written to fail
  when coverage drops; run it and quote its exit code.
- **No silent loss.** A gap is a first-class output, not an omission.

## Run log

Every use of this skill is recorded in [`runs.md`](runs.md) — append-only: the measured
success with its numbers, or the error verbatim. When a run teaches this skill something
new, this file is updated in place, with the evidence.

**Bot:** [`mavis-session-extract-bot-skill`](../mavis-session-extract-bot-skill/SKILL.md) —
the hub that owns the list of member skills, the shared contract, and this update loop.
Create a new member through
[`mavis-bot-creator-skill`](../mavis-bot-creator-skill/SKILL.md).
