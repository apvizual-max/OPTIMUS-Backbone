# PLAN 4 — MASTER BLUEPRINT

**Act four of four.** The three preceding plans as working steps: what depends on what, in what
order, how each is proven, and what the ten adversarial passes found.

**Status: EXECUTED.** The sequence below was the plan *and* the record of what was run.

---

## 1. The three acts and the spine that joins them

| Act | Plan | Output | Feeds |
|---|---|---|---|
| I | [PLAN_1](PLAN_1_DOCUMENTATION.md) | the corpus, chapters, axes, method | Brain · Method · Axes panels |
| II | [PLAN_2](PLAN_2_PROGRAM.md) | the programme matrix, gap register, engines | Program · Workflow · Learning panels |
| III | [PLAN_3](PLAN_3_COMMAND_CENTER.md) | backend, frontend, actions, verification | everything, live |
| **IV** | this document | the spine: order, dependencies, proof | — |

**The spine is one direction:** `conversation → corpus → concepts → matrix → panel`. Each link is
checkable, and a break anywhere is a registered gap rather than a silence.

```
09_LOGS\corpus_freeze ──▶ corpus_extractor ──▶ corpus_full.jsonl
                                                    │
                            ┌───────────────────────┼───────────────────────┐
                            ▼                       ▼                       ▼
                     chapter_map.json        corpus_stats.json         corpus_digest
                            │                       │                       │
                     CH_00..CH_16             (7 integrity checks)   (102 turns)
                            │
                  ┌─────────┴─────────┐
                  ▼                   ▼
           03_AXES × 4        04_METHOD × 3
                                        │
                                        ▼
                          tany-llm-to-sentinel.SKILL.md
                                        │
   12_PROGRAM ◀── build_program_matrix ◀──┘
        │                  (24 concepts, 9 links each)
        ├── IDEA_TO_SCRIPT_MATRIX.json ──▶ 06_IDEA_TO_SCRIPT.md  (GENERATED)
        └── GAP_REGISTER.json
                                        │
   13_COMMAND_CENTER ◀──────────────────┘
        ├── monitor.py ──▶ health.json
        ├── collect-sentinel.ps1 ──▶ sentinel-state.json + state-history.jsonl
        ├── server.ps1 ──▶ 127.0.0.1:8910
        ├── index.html ──▶ 11 panels
        └── verify-server.ps1 ──▶ verify-report.json
```

**The generated-file rule.** `06_IDEA_TO_SCRIPT.md` is rendered from the matrix by a script, never
written by hand. A human-written correlation document starts agreeing with itself and stops
agreeing with the code. Every claim in it is a lookup.

---

## 2. Execution order, with the gate each step had to pass

| # | Step | Gate — not "done", a measurement | Result |
|---|---|---|---|
| P0 | Freeze the corpus | 96 files + `SHA256SUMS.txt` | 18,666,312 B, 95 hashes |
| P1 | Extract + chapter + axis + method | 7 integrity checks, ratio ≥ 0.95, tiling 1..102 | 955 msgs, **1.0000**, 17 chapters, 0 unplaced |
| P2 | Fix the STOP defect | sabotage: revert `_stop` → suite must fail | 28 assertions; sabotage **drops it to 10 and fails** |
| P3 | Audit the programme | every link checked on disk, status computed not assigned | 24 concepts, 17 gaps |
| P4 | Self-improvement gate | must block an unratified promotion | 3 boundaries held |
| P5 | Self-monitor | a family that raises becomes `NOT_RUN`, never a pass | 8 → 9 families |
| P6 | Backend | routes answer with real content | 7 routes |
| P7 | Frontend | 11 panels render `NOT_MEASURED` | `index.html` 41 KB |
| P8 | Integration | **3 start/stop cycles, every route, 4 injections** | `verify-report.json` |
| P9 | Hardening | five-snapshot store, runbook, action wiring | `README.md` |
| P10 | Ratification | suite + monitor + verification all measured | this document set |

**P0 before everything, because extraction against a moving target proves nothing.** The freeze
must precede the extract, or a compaction between the two yields a corpus matching no one.

**P2 before P3, because the matrix's status depends on the engine actually having the states it
claims.**

**P8 last, because a start banner is not evidence.** The reference Control Center was *down* when
this began; the only honest response to "it starts" is to start it three times and watch.

---

## 3. The ten adversarial passes

The brief required testing the plan against gaps "at least ten times… without touching the
system". Each pass below found something real.

| # | Attack | Finding | Consequence |
|---|---|---|---|
| 1 | "Retention 1.0 — did anything get dropped?" | 1384 in, 955 out — looked like 417 vanished | they were **deduplicated by `message_id`**; the `no_silent_drop` check was added to prove it |
| 2 | "Are the 17 chapters the ones in the plan?" | **No.** Pass 4 of the original review predicted this | chapter set re-derived from the actual digest |
| 3 | "Do the chapters cover every message?" | raw seq ranges stranded 168 trailing assistant replies | rule changed: a message belongs to the chapter of the **nearest preceding user turn** |
| 4 | "Is `STOPPED` reachable?" | **No.** Declared, never assigned | `_stop()` implemented; 28 assertions; sabotage-proven |
| 5 | "Does the suite actually pass?" | 3 tests measured something other than their subject | rebuilt against real artefacts |
| 6 | "Does the detector detect itself?" | the language-law scan flagged its own regex | `\uXXXX` escapes |
| 7 | "Does the monitor ever go blind?" | it flagged its own regex | escaped; Romanian still correctly detected in the corpus |
| 8 | "Does the collector really write state?" | **No** — `$STATE`/`$state`; wrote a file named after an `OrderedDictionary`; exit 0 | path renamed; 3 monitor checks added |
| 9 | "Does the corpus endpoint work?" | **No** — `$PY`/`$py`; the Python source ran as a PowerShell command | renamed; found only by reading the **server's log** |
| 10 | "Does SSE work, and does it block?" | 0 bytes (`SendChunked` missing, exception swallowed); a persistent stream **would** wedge the single-threaded listener | short-lived stream + `API still live after SSE` guard |

**Passes 8, 9 and 10 all share one root cause: a failure with no symptom.** In each case the
process exited 0, the surrounding steps succeeded, and nothing anywhere reported an error. The only
thing that found them was reading the evidence that a client actually received.

**And the guard built in pass 8 was itself wrong at first** — it read `.ps1` files as plain UTF-8
and went blind on the BOM that PowerShell 5.1 writes, reporting OK while seeing nothing. It was
fixed to `utf-8-sig` and then proved by planting a collision and watching it fail. Pass 10's lesson
applied to the detector built in pass 8.

**A second family surfaced during the final pass**, quieter and larger: code asking a document for
a key it never had. `.get()` returns `None`, `@($null).Count` is `1`, and both flow onward into a
confident wrong number. Five instances, including **a false `FAIL` reported by the monitor itself**
— the one component whose entire value is that it does not lie — and a *generated* gap table where
every row read `?` while looking finished. Details in [PLAN_2 §3a](PLAN_2_PROGRAM.md).

Both families reduce to one rule: **a value taken from a field that does not exist is not a
measurement, it is a guess with a type.** `None` and `0` are different claims, and only one is a
fact. The rule that caught the monitor was the same rule that caught the BOM-blind detector.

---

## 4. The generalisable findings

Four things this build learned that outlive the SENTINEL project.

**4.1 A silent failure has no symptoms, so the code must narrate itself.**
Three defects cost real time, and in all three the script exited 0 and printed a healthy summary.
A process that fails without throwing gives a log-based diagnosis nothing to find — the *absence*
of evidence reads as innocence. The collector now prints what it wrote and **throws if the file is
absent after a successful write**. An empty `catch` is a decision to never find out.

**4.2 Assert the property, not the text.**
`test_dashboard_surface` pinned the literal `ConvertFrom-Json).id`, so refactoring a request parser
failed a *security* test. The lesson generalises past PowerShell: a test that breaks when correct
code is rewritten is testing the text, not the boundary. Three tests were measured against
artefacts rather than against what the code claimed.

**4.3 A fixture must be built from the real values.**
The chapter test read `chapters` from `corpus_stats.json`, which has no such key. It silently
measured an **empty list** — assertions that could neither pass nor fail, and so proved nothing
while appearing to run. Any check comparing real-world values needs a case built from the actual
values, not a tidy stand-in.

**4.4 Prove a detector can fail.**
Every guard added here was proved by sabotage: revert the fix, watch the check fail, restore.
`ps_variable_case_collisions` was proved by planting a real collision. `ps_shadowed_script_vars`
was proved by re-creating instance 3 exactly. A detector that has never been seen to fail is a
detector of unknown sensitivity.

---

## 5. Dependencies

```
P0 freeze ──▶ P1 extract ──▶ P3 matrix ──▶ P6 backend ──▶ P7 frontend ──▶ P8 verify
                  │               │                                              │
                  └──▶ P2 engine ─┴──▶ P4 self-improvement                      │
                            │                                                     │
                            └──▶ P5 monitor ──────────────────────────────────────┘
                                                          P9 hardening ──▶ P10 ratification
```

**P2 and P5 are the bottleneck.** P3's statuses depend on P2 (does the engine have the states it
claims?), and P6's data depends on P5 (is there anything to collect?). Everything downstream of
those two is fast.

Nothing in the chain requires a network, a package install, or a cross-system action. That was
deliberate: the three things that *do* require R0 (§7) are all at the end, not in the middle.

---

## 6. Acceptance criteria for the whole build

| # | Criterion | Measured result |
|---|---|---|
| E1 | Nothing cut from the conversation | retention **1.0000**; 955 messages; 7/7 integrity checks |
| E2 | Chronological from message zero | seq dense `1..N`; seq 1 verified as the real first message |
| E3 | Grouped by naming | 17 chapters; tiling 1..102; **0 unplaced** |
| E4 | Strategy/Reason/Logic/Rationale separate | 4 axis chapters, each covering all 17 |
| E5 | The method documented | 12 steps, each with verbatim evidence **and** a counterfactual |
| E6 | Programmatic, not narrative | every artifact produced by a re-runnable script |
| E7 | Every part: done / to-do / suggestions / origin | 24-row generated correlation |
| E8 | Idea → script correlation | 24 concepts × 9 links, measurement-derived |
| E9 | Dashboard correlates all of it | 11 panels, 7 routes, live |
| E10 | Real-time, measured, never asserted | 9 check families; `NOT_MEASURED` / `NOT_RUN` first-class |
| E11 | Actions safe | 4 injections refused with 400 **and the body naming the id**, ×3 cycles |
| E12 | Tested against gaps ≥ 10 times | 10 adversarial passes, each with a real finding |
| E13 | Self-improvement gated by R0 | unratified promotion blocked; empty ratification refused |
| E14 | Boundaries held | 1 workspace only; nothing outside written |

---

## 7. What still needs R0 — and what happens if it is never given

**These three are the only blockers left, and none of them blocks the build from being used.**

| # | Action | Why it needs R0 | If never given |
|---|---|---|---|
| R0-1 | Install `playwright`, `PIL`, `pypdf`, `cv2`, `faster-whisper`, `tesseract` | packages into the system | those capabilities stay **unverified**; the dashboard keeps saying so |
| R0-2 | Wire the 26 MCP tools (runtime handshake) | **cross-system** action | 26 tools stay **DECLARED, 0 WIRED**; the hub stays unreachable from other agents |
| R0-3 | Public deployment of the Command Center | would expose the corpus on the open internet | stays **loopback-only** on 127.0.0.1:8910 |

None was performed. Each is reported in the same words by the matrix, the cockpit, and the
dashboard.

**Two things the system will not do on its own, by design:**

- **Ratify its own lessons.** Self-improvement may *propose*; only the operator ratifies. Without
  that, "improve yourself" has no external reference point and becomes drift.
- **Call itself green while anything is unverified.** The suite exits non-zero because
  `BrowserAutomation` ran zero assertions. That is the designed behaviour, not a bug.

---

## 8. How to re-verify this build yourself

```powershell
cd C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\SENTINEL_PRIME

# 1. the corpus is intact and nothing was cut
python 08_SELF_IMPROVEMENT\corpus_extractor.py verify

# 2. the correlation document matches the machine-readable matrix
python 08_SELF_IMPROVEMENT\build_idea_to_script_doc.py     # -> "unchanged (idempotent)"

# 3. the tests
python 08_SELF_IMPROVEMENT\test_suite.py                   # -> 212 passed, 0 failed, 3 skipped

# 4. the system health, honestly
python 08_SELF_IMPROVEMENT\monitor.py

# 5. the dashboard really works, three times over
powershell -NoProfile -ExecutionPolicy Bypass -File 13_COMMAND_CENTER\api\verify-server.ps1 -Cycles 3

# 6. look at it
13_COMMAND_CENTER\bat\sentinel-cc.bat
```

Step 3 **exits 1 by design** while `BrowserAutomation` is `NOT_RUN`. That is the suite correctly
refusing to call itself green.

---

## 9. Ratification

Ratified by the operator as *"Implement this plan"*, executed under the permanent bimodal law:
`MODE_A → R0 → MODE_B`, with nothing outside `SENTINEL_PRIME\` written, and every improvement
proposed rather than taken.

**AMIN.** System > Task > Speed > User. Stopping is acceptable; fabrication is not. Measure the
chain, not the file — and let the system read its own history, or "improve yourself" has no fixed
point to improve from.

---

### The whole of it, in one line

**Freeze before you extract, measure instead of asserting, refuse to call a thing green while it
is unverified, and let the system read the history of its own construction.**
