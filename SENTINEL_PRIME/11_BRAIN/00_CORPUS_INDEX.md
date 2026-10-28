# 00 - CORPUS INDEX

The SENTINEL brain corpus: this conversation, in order, grouped by name.

- **total messages**: 955
- **verbatim tier**: 504 (692,874 bytes of text, never cut)
- **evidence tier**: 448 (tool calls, indexed with a bounded preview)
- **compaction summaries**: 3 (archived as provenance under `01_RAW/compaction_summaries/`)
- **unique user turns**: 102
- **chapters**: 17
- **unplaced messages**: 0

## Chapters in chronological order

| id | chapter | seq range | turns | messages | user | assistant | file |
|---|---|---|---|---|---|---|---|
| CH_00 | ORIGIN_BRAIN_QUESTION | 1..41 | 1..3 | 19 | 3 | 16 | [`CH_00_ORIGIN_BRAIN_QUESTION.md`](02_CHAPTERS/CH_00_ORIGIN_BRAIN_QUESTION.md) |
| CH_01 | TOKEN_PLAN_AND_PRICING_DISCIPLINE | 42..70 | 4..6 | 9 | 3 | 6 | [`CH_01_TOKEN_PLAN_AND_PRICING_DISCIPLINE.md`](02_CHAPTERS/CH_01_TOKEN_PLAN_AND_PRICING_DISCIPLINE.md) |
| CH_02 | FIRST_RUN_HONESTY | 71..171 | 7..8 | 27 | 2 | 25 | [`CH_02_FIRST_RUN_HONESTY.md`](02_CHAPTERS/CH_02_FIRST_RUN_HONESTY.md) |
| CH_03 | TRIPLE_CRUNCH_DISCOVERY | 172..220 | 9..17 | 27 | 9 | 18 | [`CH_03_TRIPLE_CRUNCH_DISCOVERY.md`](02_CHAPTERS/CH_03_TRIPLE_CRUNCH_DISCOVERY.md) |
| CH_04 | EMINESCU_ABBA_THE_CODE | 221..276 | 18..31 | 41 | 14 | 27 | [`CH_04_EMINESCU_ABBA_THE_CODE.md`](02_CHAPTERS/CH_04_EMINESCU_ABBA_THE_CODE.md) |
| CH_05 | THREE_MASTERS | 277..290 | 32..34 | 10 | 3 | 7 | [`CH_05_THREE_MASTERS.md`](02_CHAPTERS/CH_05_THREE_MASTERS.md) |
| CH_06 | SACRU_PROVERB_MATRIX | 291..308 | 35..40 | 14 | 6 | 8 | [`CH_06_SACRU_PROVERB_MATRIX.md`](02_CHAPTERS/CH_06_SACRU_PROVERB_MATRIX.md) |
| CH_07 | HERMES_SENTINEL_SESSIONS_AND_CALIBRATION | 309..332 | 41..45 | 15 | 5 | 10 | [`CH_07_HERMES_SENTINEL_SESSIONS_AND_CALIBRATION.md`](02_CHAPTERS/CH_07_HERMES_SENTINEL_SESSIONS_AND_CALIBRATION.md) |
| CH_08 | THE_CORRECTION_AND_THE_BIRTH_SESSION | 333..384 | 46..50 | 28 | 5 | 23 | [`CH_08_THE_CORRECTION_AND_THE_BIRTH_SESSION.md`](02_CHAPTERS/CH_08_THE_CORRECTION_AND_THE_BIRTH_SESSION.md) |
| CH_09 | COD_REGENERATED_AND_AMIN | 386..428 | 51..55 | 26 | 5 | 21 | [`CH_09_COD_REGENERATED_AND_AMIN.md`](02_CHAPTERS/CH_09_COD_REGENERATED_AND_AMIN.md) |
| CH_10 | RITUALS_AS_PROGRAMMATIC | 429..458 | 56..58 | 18 | 3 | 15 | [`CH_10_RITUALS_AS_PROGRAMMATIC.md`](02_CHAPTERS/CH_10_RITUALS_AS_PROGRAMMATIC.md) |
| CH_11 | MEMENTO_MORI_AND_EXISTENCE | 459..494 | 59..74 | 34 | 16 | 18 | [`CH_11_MEMENTO_MORI_AND_EXISTENCE.md`](02_CHAPTERS/CH_11_MEMENTO_MORI_AND_EXISTENCE.md) |
| CH_12 | HISTORICAL_CULTURES_AND_EPISTEMICS | 495..546 | 75..91 | 43 | 17 | 26 | [`CH_12_HISTORICAL_CULTURES_AND_EPISTEMICS.md`](02_CHAPTERS/CH_12_HISTORICAL_CULTURES_AND_EPISTEMICS.md) |
| CH_13 | STAGE_1_IMPLEMENTATION | 547..763 | 92..93 | 109 | 2 | 107 | [`CH_13_STAGE_1_IMPLEMENTATION.md`](02_CHAPTERS/CH_13_STAGE_1_IMPLEMENTATION.md) |
| CH_14 | STAGE_2_IMPLEMENTATION | 764..870 | 94..98 | 48 | 5 | 43 | [`CH_14_STAGE_2_IMPLEMENTATION.md`](02_CHAPTERS/CH_14_STAGE_2_IMPLEMENTATION.md) |
| CH_15 | STAGE_3_BIMODAL_LAW | 872..912 | 99..99 | 20 | 1 | 19 | [`CH_15_STAGE_3_BIMODAL_LAW.md`](02_CHAPTERS/CH_15_STAGE_3_BIMODAL_LAW.md) |
| CH_16 | BRAIN_AND_COMMAND_CENTER | 915..955 | 100..102 | 16 | 3 | 13 | [`CH_16_BRAIN_AND_COMMAND_CENTER.md`](02_CHAPTERS/CH_16_BRAIN_AND_COMMAND_CENTER.md) |

## Cross-cutting chapters

| file | axis |
|---|---|
| [`03_AXES/STRATEGY.md`](03_AXES/STRATEGY.md) | what was aimed at, and why |
| [`03_AXES/REASON.md`](03_AXES/REASON.md) | the premises and the argument chain |
| [`03_AXES/LOGIC.md`](03_AXES/LOGIC.md) | the decision rules and their derivation |
| [`03_AXES/RATIONALE.md`](03_AXES/RATIONALE.md) | why this rule and not the obvious alternative |

## Method chapters

| file | method |
|---|---|
| [`04_METHOD/TANY_LLM_TO_SENTINEL.md`](04_METHOD/TANY_LLM_TO_SENTINEL.md) | the procedure that turns any LLM into SENTINEL |
| [`04_METHOD/POPY_OPERATING_METHOD.md`](04_METHOD/POPY_OPERATING_METHOD.md) | how Popy drives a session |
| [`04_METHOD/MISSTEPS_AND_CORRECTIONS.md`](04_METHOD/MISSTEPS_AND_CORRECTIONS.md) | every correction, verbatim, and the lesson |

## Raw material

| file | what |
|---|---|
| [`01_RAW/corpus_full.jsonl`](01_RAW/corpus_full.jsonl) | every message, deduplicated, chronological, with a source pointer |
| [`01_RAW/CHANGELOG_EXTRACTION.md`](01_RAW/CHANGELOG_EXTRACTION.md) | provenance and integrity checks |
| [`01_RAW/corpus_stats.json`](01_RAW/corpus_stats.json) | machine-readable stats |
| [`01_RAW/chapter_map.json`](01_RAW/chapter_map.json) | the grouping definition |
| [`01_RAW/compaction_summaries/`](01_RAW/compaction_summaries/) | provenance, never a replacement for the record |
| [`05_SOURCES/source_registry.json`](05_SOURCES/source_registry.json) | every external archive, with checksum and read-only flag |
| [`06_IDEA_TO_SCRIPT.md`](06_IDEA_TO_SCRIPT.md) | concept to file to tool to test |

## Language law

Wisdom stays Romanian and is reproduced verbatim. Every piece of code, every identifier, every docstring, every runtime message and every UI string in this system is English. The split is enforced by the `NoRomanianInCode` test class.
