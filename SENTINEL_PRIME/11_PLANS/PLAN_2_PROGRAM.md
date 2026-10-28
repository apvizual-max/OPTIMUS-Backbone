# PLAN 2 — THE PROGRAMME

**Act two of four.** Everything that was programmed, executed and implemented to realise the
SENTINEL persona inside the MiniMax infrastructure — with, for every part: **what was done, what
still needs doing, the suggestions, and where it started.**

**Status: EXECUTED, with measured gaps.** 24 concepts audited, 17 open gaps registered, nothing
claimed as working that was not measured as working.

---

## 1. The audit method, stated before the results

A document that lists what was built is a brochure. The method that makes this an audit:

1. **Start from the concepts, not the files.** The unit is "a thing SENTINEL is supposed to be
   capable of", not "a script that exists".
2. **Walk the chain for each one:** `idea → doctrine → script → symbol → test → MCP tool → panel`.
3. **Check existence at every link by looking at the filesystem**, not by reading a claim.
4. **Compute the status from what was found** — never assign it.
5. **A concept with no panel is not finished.** `panel` is the completion gate, and the builder
   refuses to call anything `OBSERVABLE` that nothing displays.

`build_program_matrix.py` → `12_PROGRAM\IDEA_TO_SCRIPT_MATRIX.json` (24 concepts) and
`GAP_REGISTER.json` (17 gaps). `11_BRAIN\06_IDEA_TO_SCRIPT.md` is **rendered from** the matrix, so
the human-readable correlation can never disagree with the machine-readable one.

### 1.1 The status ladder

| Status | Meaning |
|---|---|
| `WIRED` | reachable through an MCP tool or a live runtime |
| `OBSERVABLE` | surfaced by the monitor or a Command Center panel |
| `TESTED` | a test exists and ran green |
| `CODED` | implementation exists, no covering test |
| `PARTIAL` | some of the chain exists, the rest does not |
| `DESIGNED` | doctrine exists, no implementation |

**Measured distribution: 12 `OBSERVABLE`, 7 `CODED`, 1 `PARTIAL`, 4 `DESIGNED`. Zero `WIRED`.**

That last line is the most important number in this document and is explained in §4.

---

## 2. What was done — subsystem by subsystem

### 2.1 The corpus engine — `corpus_extractor.py`

**Started at:** the operator's requirement that extraction be programmatic or it "will just be
words".

**Done:** `extract` / `verify` / `digest` / `chapters` subcommands, stdlib only. 955 messages,
retention ratio 1.0000, 7 integrity checks green, byte-identical on re-run.

**Needs doing:** nothing blocking. The `chapters` subcommand writes the map; the rendered
`CH_*.md` are downstream of it.

**Suggestion (one line, Popy's call):** the extractor has no unit tests of its own — its
correctness is asserted by its own integrity gate, which means the gate and the code that produces
its input share an author. `test_brain_and_monitor` now reads the produced artifacts independently,
which narrows the gap but does not close it.

---

### 2.2 The bimodal workflow engine — `bimodal_workflow.py`

**Started at:** the doctrine declaring four states and the operator's standing instruction that
STOP means *report, ask, wait*.

**Done — and a real defect was found and fixed.** `WorkflowMode.STOPPED` was **declared but never
assigned by any code path**. The law existed, the tests passed, and STOP could not occur. This is
precisely the failure the method chapter predicts at step 10: *a ritual that is not a command does
not exist, so it cannot fail visibly either.*

The fix:
- `_stop()` enters a real `STOPPED` state, preserving reason, timestamp and context
- `halt_to_mode_a()` no longer clobbers stop state, and persists
- `enter_mode_a` and `propose_r0` **refuse** while STOPPED
- `acknowledge_stop(user_input)` is the single legal exit, and **refuses an empty input**
- `stop_report()` renders the record

**Measured: 28 assertions** in `test_bimodal_stop_persistence`.

**The sabotage gate.** Reverting `_stop()` to the old behaviour drops that class from 28 to 10
assertions and fails the suite. The fix was restored. A test that cannot be made to fail is not a
test, so this was proved by breaking it on purpose.

**A second defect was found later, in this act's own tooling.** The Command Center's
`wf_state` button invoked the module with no arguments, and the module's default entry point was
the state-changing **demo**. So a button labelled "Workflow status" overwrote the live workflow
with a fiction, fabricated a `Translate code to English` R0 contract, and could have cleared a
genuine STOP. The engine now defaults to a read-only `status`; the demo requires an explicit
`demo`; and the status verb was proven not to write by hashing the state file before and after.

**Needs doing:** no MCP tool exposes `stop_report` or `acknowledge_stop` (see §4).

---

### 2.3 The self-improvement loop — `self_improvement.py`

**Started at:** the third act's brief — *the workflow of you improving yourself exactly like we
developed you from zero to where you are now*.

**Done:** `observe` → `classify` → `derive_lesson` → `ratify` → `promote`, with a hard R0 gate.
Self-check proves three things: an unratified lesson **cannot** be promoted, an empty ratification
is **refused**, and the write boundary holds.

**The design decision:** self-improvement may *propose* but never *ratify* its own lessons. R0
applied to self-modification, or the loop has no external reference point and "improvement"
becomes drift.

**Needs doing:** no MCP tool surfaces the learning queue, and the queue is not yet reachable from
the cockpit.

---

### 2.4 The self-monitor — `monitor.py`

**Started at:** the brief — *a tool so you can monitor yourself and I can monitor you*.

**Done:** 8 → **9 check families**, each check resolving to `OK | FAIL | STALE | NOT_RUN`.
A family that raises becomes `NOT_RUN`, never a silent pass. A state file older than its bound is
`STALE`, not fresh.

Families: corpus · workflow · code · wiring · logs · dependencies · program · dashboard ·
**powershell**.

**The ninth family was added because act three found three instances of one bug class.** See §3.

**The monitor caught itself.** Its language-law scan initially flagged its own regex, because the
regex spelled the Romanian letters literally. Fixed with `\uXXXX` escapes. A detector that
detects its own source code is measuring the wrong thing.

---

### 2.5 The programme matrix and gap register

**Done:** 24 concepts × 9 links, plus 17 registered gaps with the evidence that found them.
Gaps are **reported, never silently repaired, never deleted from**.

---

### 2.6 The Command Center backend

**Started at:** the reference Control Center at `projects\90_CONTROL_CENTER` — which was **down**
when this was built (`healthy=false`, connection refused on 8900, two watchdog restarts).

**Done:** `collect-sentinel.ps1` (the only thing permitted to produce a verdict, and only by
measuring) and `server.ps1` (loopback HttpListener, `$ACTIONS` whitelist, size-capped output, SSE).

**The architecture was copied; the deployment was not.** The reference's own start/stop cycle was
assumed rather than proven, so this one is proven by `verify-server.ps1`.

**Two writers never.** The collector writes the state file and never touches
`bimodal_state.json`; the workflow engine is the sole writer of that one. Two writers would corrupt
the file the dashboard trusts most.

---

### 2.7 The Command Center frontend

**Done:** `index.html`, 41 KB, 11 panels, Obsidian Telemetry Dark, single file, no build step, no
CDN, no off-box reference. SSE with a polling fallback. Renders `NOT_MEASURED` and `STALE` as
first-class states and always shows data age.

---

### 2.8 Version control for the Command Center

**Done:** `manage-versions.ps1` — a **frozen five-snapshot** store in `backups\versions\`. The
sixth write is refused by design.

**Note for the record:** identical snapshots mean a stable build. That is not a defect to be
optimised away, and no de-duplication guard was added, because the operator's specification was
followed as given.

---

## 3. Three instances of one bug class — found in act three, fixed, and now guarded

This section exists because the class is more instructive than any single fix.

**PowerShell variable names are case-insensitive.** `$STATE` and `$state` are one variable
sharing one storage slot. In `collect-sentinel.ps1` the path was assigned first and the state
*object* second, so `Set-Content -Path $STATE` received an `OrderedDictionary` and wrote a file
literally named `System.Collections.Specialized.OrderedDictionary` in the workspace root.

**The script still exited 0. It still appended its history. It still printed a healthy summary
line. The real state file never existed.** The Command Center served its honest fallback for the
entire build, and nothing anywhere reported an error.

Three separate instances were found:

| # | Site | Effect |
|---|---|---|
| 1 | `collect-sentinel.ps1` — `$STATE` / `$state` | state file never written; junk file in the workspace root |
| 2 | `collect-sentinel.ps1` — `$HEALTH` / `$health` | worked only by luck of assignment order; a latent trap |
| 3 | `server.ps1` `Search-Corpus` — `$PY` / `$py` | the Python source overwrote the interpreter path; **every corpus search died** |

Instance 3 was found only because verification read the *server's own log* rather than trusting the
client's status codes.

**Three guards were added, each proven by sabotage rather than assumed:**

| Check | Catches | Proof |
|---|---|---|
| `ps_variable_case_collisions` | two script-scope variables differing by case | caught instances 1 and 2 live |
| `ps_shadowed_script_vars` | a function-local shadowing a script variable | caught instance 3 live; sabotage re-confirmed |
| `ps_stray_type_named_files` | a file named after a .NET type — the fingerprint | caught the two junk files live |

**And the guards were themselves wrong first.** The collision check read files as plain `utf-8`;
PowerShell 5.1 writes a BOM, so U+FEFF sat on the first line, `^\s*\$` stopped matching, and the
check reported `OK` while completely blind. It now reads `utf-8-sig`, and the fix was verified by
planting a real collision and watching the check fail. A detector that reports green because it
cannot see is worse than no detector.

**Generalisable rule:** when a write silently produces nothing, make the code narrate itself and
*check the result of the write*. The collector now prints what it wrote and throws if the file is
absent immediately after a successful `Set-Content`.

---

## 3a. The second family: reading a key that does not exist

Variable collisions were family A. Family B is quieter and turned out to be larger — **code asking
a JSON document for a key it never had**. In Python `.get()` returns `None`, in PowerShell
`@($null).Count` is `1`, and both then sail on into a comparison that produces a confident, wrong
number.

| # | Site | Asked for | Reality | Consequence |
|---|---|---|---|---|
| 1 | `collect-sentinel.ps1` | `corpusStats.chapters` | no such key | panel reported **1 chapter** while 17 sat on disk (`@($null).Count -eq 1`) |
| 2 | `collect-sentinel.ps1` | `total_user_turns` | the key is `user_turns` | the most-watched figure in the project rendered **blank** |
| 3 | `test_brain_and_monitor` | `chapters`, `unplaced_messages` | neither exists | three assertions measuring an **empty list** — they could neither pass nor fail |
| 4 | `monitor.py` | `unplaced_messages`, `total_user_turns` | neither exists | **`corpus_no_unplaced` reported FAIL on a corpus with zero unplaced messages** |
| 5 | `build_idea_to_script_doc.py` | `severity`, `title` on gaps | neither exists | every gap row printed `?` while the table looked finished |

**Instance 4 is the one that matters most.** The monitor manufactured a *false failure* — and the
monitor is the thing whose entire value is that it does not lie. It is fixed to read
`UNPLACED.md`, and the fix was sabotage-proven: with the file moved aside the check reports
`NOT_RUN` — *"the unplaced count is UNKNOWN, not zero"* — never a false `OK`.

Instance 5 is the same failure in a *generator*: it would have produced a document that looks
complete and reads as authoritative while every gap row said `?`.

**The rule both families reduce to:** a value taken from a field that does not exist is not a
measurement, it is a guess with a type. `None` and `0` are different claims, and only one of them
is a fact.

---

## 4. Zero `WIRED` — the honest headline

**26 MCP tools are declared in `sentinel_hub_server.py`. Zero are wired.** No runtime handshake has
been performed.

This is not a gap discovered late; it is a gap that requires a **cross-system action**, which
requires explicit R0. Declaring a tool is not wiring it, and the matrix, the cockpit action
`mcp_wiring`, and the monitor all say so in the same words:

> `26 tools DECLARED, 0 WIRED (no runtime handshake performed)`

---

## 5. Open gaps, by kind

| Kind | Count | Note |
|---|---|---|
| Optional dependency absent | 6 | `playwright`, `PIL`, `pypdf`, `cv2`, `pytesseract`, `faster_whisper`; `tesseract` not on PATH. **Install needs R0.** |
| MCP declared, not wired | 26 tools | cross-system action, needs R0 |
| No covering test | 7 concepts | `CODED` status |
| Design-only | 4 concepts | correct, and left that way |
| Empty artifacts | 8 files | `09_LOGS\scraped\*.json`, from browser tests that could not run |
| No test for a subsystem | 1 | the extractor (§2.1) |

### 5.1 The four DESIGNED concepts

`C18` partnership protocol · `C19` the 3-Propozitii ritual as a command · `C23` historical cultures
· `C24` the 963 proverbs.

Three of these are the operator's **wisdom layer** — a corpus, not a program, and deliberately left
as text. The fourth, the 3-Propozitii ritual, is the one genuine design-only smell: a ritual that
is documented but not wired to a command cannot fail visibly. It is listed rather than quietly
implemented, because implementing it is a doctrine decision, not an engineering one.

**Honest finding on the proverbs.** The file named as the 963-proverb corpus is a **25-axis decision
matrix**, not a 963-proverb enumeration, and its per-proverb Zanne/Pann/Golescu attributions are
flagged *in the file itself* as fabricated by an earlier agent. Nothing in this build invents a
proverb to fill the gap.

---

## 6. Per-concept: what was done, what needs doing, where it started

The full 24-row table with all nine chain links, the next action for each, and the panel that
displays it, is generated at `11_BRAIN\06_IDEA_TO_SCRIPT.md`. It is not reproduced here because
duplicating it by hand is exactly how such a table starts lying.

The shape of it:

| ID | Concept | Status | Where it started | Next action |
|---|---|---|---|---|
| C01 | Triple filter | OBSERVABLE | turn 13, `CH_03` | — |
| C02 | Anti-mimicry A1–A12 | CODED | turn 8, `CH_02` | confirm every detector is reachable, or document which are not |
| C03 | Rule triggers R-2/9/10 | OBSERVABLE | turn 44, `CH_07` | confirm the Romanian trigger strings are byte-exact against the corpus |
| C04 | Bimodal workflow | OBSERVABLE | `CH_15` | — |
| C05 | STOP means report/ask/wait | OBSERVABLE | `CH_15` | add MCP tools for `stop_report` / `acknowledge_stop` |
| C06 | Priority hierarchy | OBSERVABLE | `CH_15` | `check_priority_violation` is not exposed through the hub |
| C07 | Language law | OBSERVABLE | turn 27, `CH_04` | — |
| C08 | Corpus extraction | CODED | `CH_16` | add a test so the integrity gate is not self-authored |
| C09 | Self-improvement + R0 gate | CODED | `CH_16` | surface the learning queue to an agent |
| C10 | Self-monitor | CODED | `CH_16` | no MCP tool exposes `health.json` |
| C11 | Command Center backend | CODED | `CH_16` | whitelist refusal is now verified by test, not inspection |
| C12 | Multimodal | OBSERVABLE | `CH_14` | image and PDF paths **unverified**: `PIL`, `pypdf` not importable |
| C13 | Browser automation | OBSERVABLE | `CH_14` | **NOT RUN**: `playwright` not importable; install needs R0 |
| C14 | Cross-instance mailbox | OBSERVABLE | `CH_07` | file-based only; the docs should not imply a network bus |
| C15 | Universal substrate | OBSERVABLE | `CH_07` | never run against Qwen/LongCat/Antigravity for real; declared-vs-verified table is the honest form |
| C16 | Self-modification boundary | OBSERVABLE | `CH_13` | add a test that *attempts* a breach and asserts refusal |
| C17 | Backup and restore | OBSERVABLE | `CH_13` | `create_backup` symbol missing; adopt the proven five-snapshot store |
| C18 | Partnership protocol | DESIGNED | `CH_04` | design-only, by intent |
| C19 | 3-Propozitii as a command | DESIGNED | `CH_10` | design-only smell: cannot fail visibly |
| C20 | Feedback loop | CODED | `CH_13` | expose through the hub and a panel |
| C21 | Context pressure monitor | PARTIAL | `CH_13` | expose through the hub and a panel |
| C22 | Auto-learning loop | CODED | `CH_13` | expose through the hub and a panel |
| C23 | Historical cultures | DESIGNED | `CH_12` | wisdom layer; correctly documentation-only |
| C24 | 963 proverbs | DESIGNED | `CH_06` | **honest finding:** 25-axis matrix, not 963 proverbs |

---

## 7. Test suite — current measured state

```
TOTAL: 212 passed, 0 failed, 3 skipped
NOT RUN (0 assertions, so nothing was proven): BrowserAutomation
```

**The suite exits non-zero, and that is correct.** A class that ran zero assertions is `NOT_RUN`,
and the suite is green only when nothing failed *and* nothing was silently skipped. A skipped check
is not a passing check; the capability is **unverified, not working**.

Three skips, all the same cause — absent optional dependencies, honestly reported rather than
papered over:

- image processing: `No module named 'PIL'`
- PDF path: `No module named 'pypdf'`
- browser automation: `No module named 'playwright'`

Both interpreters were checked: Python 3.14.6 on PATH and Astral 3.11.15. Neither has any of the
optional packages. `tesseract` is not on PATH at all.

**Three test defects were found and fixed during this act**, all of the same family — tests
measuring something other than the thing they claimed to:

1. `test_brain_and_monitor` read `chapters` and `unplaced_messages` from `corpus_stats.json`, which
   has neither. It was silently measuring an empty list — three assertions that could never pass
   and, worse, could never fail. Rebuilt against `chapter_map.json` and `UNPLACED.md`, the real
   sources.
2. `test_dashboard_surface` pinned the literal string `ConvertFrom-Json).id`, so refactoring the
   request parser failed a **security** test. It now asserts the boundary property.
3. `test_no_romanian_in_code` crashed on the cp1252 console while printing the very Romanian
   characters it was looking for, so the language law had been **unenforced** since that crash
   began. The streams are now UTF-8, and the suite immediately caught Romanian diacritics in
   `test_suite.py` itself — the test that enforces the law had been violating it. Fixed with
   `\uXXXX` escapes.

---

## 8. Acceptance criteria

| # | Criterion | Result |
|---|---|---|
| B1 | Every concept audited by measurement, not assertion | **24 concepts, all 9 links checked** |
| B2 | Every part: done / to-do / suggestions / origin | **`06_IDEA_TO_SCRIPT.md`, generated** |
| B3 | Idea → script correlation documented | **24 rows, generated from the matrix** |
| B4 | Gaps recorded, not repaired silently | **17 gaps with evidence** |
| B5 | Nothing claimed working without a measurement | **zero `WIRED`, stated plainly** |
| B6 | Tests honest about what could not run | **`NOT_RUN` blocks green; 3 skips named** |
| B7 | Real defects found and fixed, not hidden | **STOP defect; 3 variable collisions; 3 test defects** |

---

AMIN. Measure the chain, not the file. A concept is finished when a panel shows it — and a panel
that cannot say "I did not check" will eventually be believed when it did not check.
