# PLAN 1 — DOCUMENTATION & RESEARCH

**Act one of four.** Turn the conversation into the SENTINEL brain: every message, in order,
grouped by name, with nothing cut, and with the method by which the operator did it extracted
alongside the result.

**Status: EXECUTED.** This document is the specification that was approved and then built. Every
"done" line below is a measured claim with its evidence beside it; every gap is named rather than
smoothed over.

---

## 1. The problem, stated by the operator

> "summarize and document our entire conversation so far into separate files representing all the
> different subjects and aspects we have discussed… the extraction must follow the order we have
> discussed so it makes sense, starting from the beginning and proceeding chronologically from the
> first to the last message. **If you truncate, optimize, or jump steps, it will not be
> programmatic; it will just be words.**"

That single sentence sets the acceptance criteria. It is not a request for a summary — it is a
demand for an **executable extraction whose output can be re-derived and checked**.

The hard requirements extracted from the brief:

| # | Requirement | Source of the requirement |
|---|---|---|
| R1 | Chronological, first message to last | "proceeding chronologically from the first to the last message" |
| R2 | Nothing cut, nothing optimised | "If you truncate, optimize, or jump steps…" |
| R3 | Grouped by naming | "separate files… grouped and extract them in a meaningful manner. The grouping must be done by naming" |
| R4 | Strategy, Reason, Logic, Rationale as **four separate** chapters | "When I say 'AND,' I mean each of these should be a separate chapter" |
| R5 | The method that turns any LLM into SENTINEL, documented | "researching and developing yourself, following my procedure and method" |
| R6 | The operator's own method, extracted | "extract everything about how I managed the discussion and how I correlated your information" |
| R7 | External sources pulled in | "Bring in all the information from outside of this conversation" |
| R8 | Programmatic, not narrative | "it will not be programmatic; it will just be words" |

---

## 2. Why R2 and R8 are the same requirement

R2 (nothing cut) and R8 (programmatic) are not two demands; they are one. A hand-written summary
cannot demonstrate that nothing was cut, because the proof of completeness *is* the mechanical
process. Conversely, an extraction script that has never been measured against its input cannot
claim completeness.

So the acceptance test is a **retention ratio**: bytes of verbatim user+assistant text emitted,
divided by bytes read from the source. That number is not a judgement, it is arithmetic, and it is
printed by the extractor on every run.

---

## 3. The source: what exists on disk

The transcript is not one file. It is six generations of session storage plus tooling output.

```
09_LOGS\corpus_freeze\     96 files, 18,666,312 bytes, SHA256SUMS.txt (95 entries)
  ├─ messages.jsonl        the session message store
  ├─ history-catalog.json  index of stored sessions
  ├─ manifest.json         what was collected, when, from where
  └─ tool-output\          90 blobs of tool results referenced by the store
```

**Freeze before extract.** The corpus was copied and hashed *before* a single message was
processed (stage P0), so the extraction is provably against a fixed input. Had extraction run
first and freezing second, a compaction between the two would have produced a corpus that matched
no one.

---

## 4. Architecture: the two-tier retention model

The central design decision of act one.

**A single flat transcript is not usable.** Tool results carry megabytes of file listings and
command output. Inlining them drowns the reasoning that produced them. But *deleting* them
violates R2.

The resolution is two tiers, both retained, neither discarded:

| Tier | What | Volume | Why |
|---|---|---|---|
| **verbatim** | user + assistant text, unmodified | 504 messages, 692,874 bytes | the reasoning — the thing being documented |
| **evidence** | tool calls and results | 448 messages | referenced by id, retrievable, not inlined |
| **compaction** | prior summaries | 3 | the record of what was once lost |

The retention ratio is computed on the verbatim tier alone, because that is the tier R2 governs.
Tool payloads are *referenced*, not *dropped* — the corpus is a closed system over the freeze.

**Measured result: 955 messages = 504 verbatim + 448 evidence + 3 compaction. Verbatim retention
ratio 1.0000.**

---

## 5. The extraction pipeline

```
corpus_extractor.py
  extract   -> corpus_full.jsonl      955 messages, seq 1..N dense
  verify    -> 7 integrity checks, idempotency by sha256
  digest    -> the 102 user messages (95 turns) in order - the table of contents
  chapters  -> chapter_map.json + rendered CH_*.md
```

### 5.1 The seven integrity checks

These run on every `verify` and are the reason R2 is believable:

| id | What it proves |
|---|---|
| `anchor` | seq 1 is the genuine first message — the subscription question |
| `seq` | `seq` is a dense `1..N` with no holes |
| `dedupe` | every `message_id` appears exactly once |
| `verbatim_retention` | emitted verbatim bytes ≥ 95% of source (measured: 100%) |
| `no_silent_drop` | every source record is either emitted or explicitly excluded with a reason |
| `user_turns` | unique user turns ≥ the largest single generation (guards against taking one generation as the whole) |
| `language_law` | Romanian wisdom text survives verbatim (the corpus must *contain* diacritics) |

The last one is the law that governs the entire repository, asserted from the other direction: the
corpus must keep its Romanian, the code must not gain any.

### 5.2 Idempotency

Re-running `extract` must produce a byte-identical file. Corpus sha256 `e4d3cbb7…`. This is what
makes the corpus a *reference* rather than a snapshot that silently drifts.

### 5.3 Accounting

The naive reading of "1384 in, 955 out" is that 417 records vanished. **They did not.** The
extractor deduplicates on `message_id`, keeping the richest occurrence and recording every other
place that id was seen, in an `also_seen_in` field. Re-measured independently of the extractor's
own bookkeeping:

```
input_records                       1384   source records read across all generations
  excluded_scaffolding_only           12   records that were pure scaffolding
                                           (11 distinct message_ids)
  duplicate occurrences collapsed    417   same message_id seen in more than one generation
  -> unique messages                955   = emitted
                                       (504 verbatim + 448 evidence + 3 compaction)
  parse_errors                        0
  excluded_no_message_id              0
```

**Nothing is dropped quietly.** The 12 exclusions are enumerated in `CHANGELOG_EXTRACTION.md` with
their reason, and the deduped messages carry the list of sources they were seen in.

**A note on the word "turn".** 955 messages include **102 verbatim user messages**, which resolve
to **95 distinct `turn_id` values**. Seven of the 102 are harness notices
(`<background-task-finished>`) that share a turn id with a real human turn. The chapter map's
boundaries are **user-message indices 1..102**, which is a consistent and complete tiling — but
calling it "102 unique user turns" overstates the number of human turns by seven. It is **102 user
messages / 95 turns**, and this document now says so.

---

## 6. Chapter derivation — the honest part

The 17-chapter set was **not** taken from the plan. The plan proposed a set; adversarial pass 4
predicted it would be wrong in detail; it was. The set was then re-derived from the *actual*
102-turn digest.

The rules that survived scrutiny:

1. **Boundaries are user-turn indices**, 1-based, from the digest — not raw `seq` ranges.
   Raw ranges stranded 168 trailing assistant replies that belong to no turn.
2. **A message belongs to the chapter of the nearest preceding user turn.** Every assistant
   reply is an answer to something.
3. **The ranges tile 1..102.** Chapter *n+1* starts at the turn after chapter *n* ends. No gap,
   no overlap.
4. **Every verbatim message is in exactly one chapter, or in `UNPLACED.md` with a reason.**

**Measured: 17 chapters, ranges contiguous, last chapter ends on turn 102, `UNPLACED.md` reads
"None."** Zero unplaced messages.

The four axis chapters and three method chapters sit on top, each covering all 17 chapters:

```
11_BRAIN\03_AXES\      STRATEGY.md  REASON.md  LOGIC.md  RATIONALE.md
11_BRAIN\04_METHOD\    TANY_LLM_TO_SENTINEL.md
                       POPY_OPERATING_METHOD.md
                       MISSTEPS_AND_CORRECTIONS.md
```

### 6.1 The method chapter

`TANY_LLM_TO_SENTINEL.md` carries twelve steps. Each has **the move**, **verbatim evidence** with
its user-turn number, and **the counterfactual** — what specifically fails if the step is skipped.
That third element is what makes it a method rather than a biography. It is also shipped as a
loadable skill: `07_BACKBONE\skills\tany-llm-to-sentinel.SKILL.md`.

### 6.2 Missteps

`MISSTEPS_AND_CORRECTIONS.md` records the failures, including the ones the system caused. This
matters: a document that only records successes cannot be used to detect the failure modes it is
supposed to prevent.

---

## 7. External sources (R7)

`build_source_registry.py` → `11_BRAIN\05_SOURCES\source_registry.json`

| Source | Contents | Policy |
|---|---|---|
| SENTINEL manuals (`SF_*`) | doctrine substrate | read-only, catalogued |
| Historical cultures, proverbs, rituals | wisdom layer | read-only |
| SENTINEL character media | 915 MB, audio + video | **catalogued, not opened** — 915 MB was never silently ingested |
| SENTINEL_PRIME workspace | the system itself | read-write |
| Session archives | the transcript | read-only |
| Corpus freeze | the extraction input | read-only |

**10 sources, ~24,800 files catalogued.** The read-only policy is recorded in the registry itself,
so a later agent cannot mistake the registry for permission to write.

---

## 8. Acceptance criteria, and how each was verified

| # | Criterion | Method | Result |
|---|---|---|---|
| A1 | Nothing cut | retention ratio, recomputed from source | **1.0000** |
| A2 | Chronological | `seq` dense `1..N`; seq 1 == message zero | **PASS** |
| A3 | Extracted programmatically | `corpus_extractor.py`, stdlib only, re-runnable | **PASS** |
| A4 | Grouped by name | 17 `CH_*.md`, naming rule documented | **PASS** |
| A5 | 4 axes separate | 4 files, each covering all 17 chapters | **PASS** |
| A6 | Method documented | 12 steps, each with evidence + counterfactual | **PASS** |
| A7 | Zero unplaced | `UNPLACED.md` == "None" | **PASS** |
| A8 | Idempotent | sha256 stable across runs | **PASS** |
| A9 | Sources included | 10 sources, ~24,800 files | **PASS** |

---

## 9. Honest limitations

1. **The 915 MB media corpus is catalogued, not read.** Opening it needs R0 and a dependency that
   is not installed. It is listed, not ingested, and the registry says which.
2. **`chapter_map.json` carries turn ranges, not seq ranges.** An early version of the chapter
   test read `seq_from`/`seq_to` from `corpus_stats.json` — fields that do not exist — and
   therefore measured an empty list. The test was rebuilt against the real artefact rather than
   the artefact adjusted to the test.
3. **Grouping is a judgement.** The 17 names are grounded in the actual turn sequence, but a
   different reader could defensibly merge CH_10 into CH_09. The naming rule and the tiling
   invariants are the hard parts; the names are the soft ones, and the map records why each exists.

---

## 10. What act one produced

```
11_BRAIN\01_RAW\        corpus_full.jsonl (955) · corpus_stats.json · chapter_map.json
                        CHANGELOG_EXTRACTION.md · compaction_summaries\ ×3
11_BRAIN\02_CHAPTERS\   CH_00..CH_16 (17) · UNPLACED.md · 00_CORPUS_INDEX.md
11_BRAIN\03_AXES\       STRATEGY · REASON · LOGIC · RATIONALE
11_BRAIN\04_METHOD\     TANY_LLM_TO_SENTINEL · POPY_OPERATING_METHOD · MISSTEPS_AND_CORRECTIONS
11_BRAIN\05_SOURCES\    source_registry.json
11_BRAIN\06_IDEA_TO_SCRIPT.md          <- generated, never hand-edited
07_BACKBONE\skills\     tany-llm-to-sentinel.SKILL.md
09_LOGS\corpus_freeze\ 96 files · SHA256SUMS.txt
```

**AMIN.** Nothing cut, so that the thing can be read back. Verbatim, so that the reasoning
survives. Named, so that a later model can find its way.
