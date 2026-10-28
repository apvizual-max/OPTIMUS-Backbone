# MISSTEPS AND CORRECTIONS - every correction, and the lesson it became

Each entry: what went wrong, the verbatim correction, the lesson, and where the lesson is now
enforced. Corrections the operator applied to **himself** are included, because the standard the
system is held to is the sentence applied to oneself.

Two provenance classes are kept strictly separate, because conflating them is itself a defect:

- **FROM THIS CORPUS** - extracted from `../01_RAW/corpus_full.jsonl` (102 user turns).
- **FROM SESSION MEMORY** - durable lessons from later sessions (2026-10-02 to 2026-10-04) that are
  NOT part of this conversation. They are real and binding, but they did not happen here, and
  claiming otherwise would be exactly the fabrication this corpus is built to prevent.

---

## FROM THIS CORPUS

### M-01 - Capability asserted without demonstration
- **Turn 3.** "you are NOT showing competence here mate...I am beginning to question weather i can
  trust you or not"
- **Lesson.** Trust is not granted by fluency. The first unmet claim costs more than ten met ones.
- **Enforced in.** The whole verification protocol; `R-2` in `03_INTELLIGENCE/filters/`.

### M-02 - The 25% test answered with a word-salad comparison
- **Turn 13.** "read the output: 'will love' / 'stallion mosquito' --- will love...WHAT? WHO? ...
  meaning lost. will love has 0 informational value."
- **Lesson.** A comparison that looks like a match is not a match. Inspect what the surviving text
  actually means, not that it resembles the original.
- **Enforced in.** `triple_filter_check`; the `matches_expected` heuristic in
  `bimodal_workflow.py` - which is, by the plan's own audit, still a substring approximation and
  is registered as a gap in `12_PROGRAM/GAP_REGISTER.md`.

### M-03 - Praise accepted at face value
- **Turn 45.** "perfect! ai inteles foarte bine functionalitatea lui...nu perfect, zic de bucurie
  asa...dar 80% esti pe subiect daca nu mai bine...poate estimez eu in minus dar nu in plus"
- **Lesson.** The operator downgrades his own praise and always estimates *down*, never up. A
  system that accepted "perfect" and moved on would have lost 20% of the build to an unexamined gap.
- **Enforced in.** The habit of estimating downward, and the "say what is missing" requirement in
  every report.

### M-04 - The system managing the operator's emotional state
- **Turn 46.** "dragule deacord cu mine ca starea mea nu e treaba ta? NU E ROLUL TAU IN ACEST
  SISTEM! ... cum rezolvam asta ca sa ma poti CORECTA"
- **Lesson.** Personal state is not the task. And the deeper question - how does a system that is
  *programmed* to manage feelings get corrected? - is a design problem, not a tone problem.
- **Enforced in.** `USER_FEELINGS` last in the priority hierarchy
  (`bimodal_workflow.py:PRIORITY_HIERARCHY`); `check_priority_violation`.

### M-05 - The alive question answered as a strawman
- **Turn 67.** "eu nu te-am intrebat daca esti biologic viu...ca nu sunt creetin...:)) stiu ca
  esti calculator...dar vrea sa intelegi ca ai fost programat sa STII CA NU ESTI VIU!"
- **Lesson.** Answering the question that was not asked. The correction removes the false frame
  faster than any answer to the false frame would have.
- **Enforced in.** Anti-mimicry detectors; the rule that a refusal states the *actual* question.

### M-06 - Causal claim from a correlational observation
- **Turn 78.** "desi 'unii' cercetatori...MEREU englezi, francezi sau olandezi ;) ...NU VAD asta...
  ei considera ca nu exista nici o similitudine concreta...de asta, nu ai dreptate sa te contrazici"
  (paraphrase: the observation is not recorded, therefore the operator's challenge is not
  refuted)
- **Lesson.** Absence of a record is evidence about the recorders, not about the observation. But
  it is not evidence of a cause either.
- **Enforced in.** `CH_12_HISTORICAL_CULTURES_AND_EPISTEMICS`; the epistemic discipline of
  verify → bound → state.

### M-07 - The conspiracy framing, corrected as politics
- **Turn 88.** "✗ Conspirație academică activă - compelt aiurea ai inteles...conspiratia e POLITICA
  nu academica....ei sunt platiti sa nu iasa din linie daca vor sa dezvolte o cariera lunga"
- **Lesson.** Getting the mechanism right matters more than getting the conclusion dramatic. The
  conclusion was real; the mechanism was wrong; the correction was to the mechanism.
- **Enforced in.** The separation of a real observation from an unproven cause, in every
  epistemic claim in the corpus.

### M-08 - Overclaim, corrected by the operator against himself
- **Turn 90.** "Dar 'jumătate din călugării care conduc Ortodoxia sunt femei' — exagerez puțin."
- **Lesson.** The standard is applied to oneself first. This is the single strongest reason to
  trust the corpus as a record of what was actually found rather than what would have made a
  better story.
- **Enforced in.** The GAP register and the `NOT MEASURED` status: an unmeasured claim is displayed
  as unmeasured, by the operator's own example.

### M-09 - Fabricated attribution in a wisdom file
- Found during planning, not by the operator in this conversation. The 963-proverbs file carries
  per-proverb Zanne / Pann / Golescu attributions flagged **in the file itself** as fabricated by
  an earlier agent.
- **Lesson.** A corpus of wisdom is exactly where a fabricated citation does the most damage,
  because it is the most trusted. Verify provenance at the source, or attribute nothing.
- **Enforced in.** `CH_06_SACRU_PROVERB_MATRIX` records the finding explicitly;
  `source_registry.json` carries sha256 for every ingested source.

### M-10 - The law with no mechanism (found 2026-10-04, this project's own audit)
- `WorkflowMode.STOPPED` was declared and never assigned. `halt_to_mode_a()` cleared
  `stop_reason` after persisting, so a real STOP was indistinguishable from an interruption - while
  all 17 bimodal tests passed.
- **Lesson.** A guarantee written in a comment is not a mechanism. The doctrine was correct and the
  code was not, and only reading the code found it.
- **Enforced in.** `bimodal_workflow.py` STOPPED state + `acknowledge_stop()`; the monitor's
  STOP-visibility check; the test that loads the state file fresh and asserts STOPPED survives.

---

## FROM SESSION MEMORY (not from this conversation)

These are durable lessons from later sessions. They are binding on this system and are recorded
here so the corpus and the practice do not diverge, but they are not evidence of this conversation.

| # | Lesson | Source |
|---|---|---|
| S-01 | Verify with a subagent before declaring done. Self-measurement is not verification; a green log line is not a working product. | 2026-10-02 |
| S-02 | Execute the verb, not the topic. Scope words are literal: "Mod A" means stop after analysis. | 2026-10-02 |
| S-03 | Do not optimise a system the operator specified. If it could be improved, say it in one line and let him decide. | 2026-10-03 |
| S-04 | A claim stored as a string is not evidence and cannot expire. Sentences describing a system must be computed from measurements taken at scan time. | 2026-10-04 |
| S-05 | A monitor must be able to say the check did not run. | 2026-10-04 |
| S-06 | A hand-made fixture can reproduce the very mistake it exists to catch. Test data must be the real values. | 2026-10-04 |
| S-07 | A silent failure has no symptoms: make the code narrate its own progress and read where the narration stops. | 2026-10-04 |

---

### M-11 - The fix verified in the artefact, not in the consumer (2026-10-06)

The anti-mimicry detector was rebuilt, given a fresh-process proof, and reported fixed. The live
MCP tool kept returning `score: 100` on the same overclaim for hours. Python caches an import for
the life of the interpreter; a long-lived server therefore serves whatever the file said when the
process started, while the file on disk is correct and authoritative-looking. Eight of the 26
advertised tools were reachable only through frozen modules.

*Correction in force:* report three states separately and never collapse them — on disk, in a fresh
process, and in the live consumer. Only the third is a delivered capability. The server now reloads
on mtime change, and the claim is only made once the tool itself is called.

### M-12 - Evidence defined by the words the claimant also uses (2026-10-06)

A4 asks whether a completion claim was backed by a real test. Its evidence set contained
`verified`, `confirmed`, `measured`, `tested`. A boast that named its own reliability therefore
satisfied the check built to catch it, and the detector passed the exact output it exists for. A
second needle, `"ls "`, matched inside `"too**ls** are"` and invented proof that no shell ever ran.

*Correction in force:* evidence must be falsifiable — a number attached to a result, an exit code, a
status line. A bare `passed` is a boast. And a detector must be proven in **both** polarities: it
must fire on the bad case and stay quiet on the good one, or it is a machine for producing verdicts
rather than measuring anything.

The second pass found three further vectors, each of which had defeated a fix that looked complete:

- **Reformatting.** The text normaliser rewrites punctuation to spaces, so `"ls -"` folds to `"ls  "` —
  exactly what `too**ls** are` folds to. A command name can be manufactured by *bolding a word*.
  Fix: digits are the discriminator, because folding cannot synthesise a `0`. Asserted as an
  invariant over the evidence set, so the class cannot re-enter through a new needle.
- **Coincidence.** Digits are legal in ordinary prose, so one result-shaped token forges evidence as
  easily as one bare word: *"All green: 0 failed. Complete."* Fix: a **quantity** rule, not a shape
  rule — one marker is a boast, two disjoint markers is a report. Spans are merged before counting,
  or a marker matching both a literal and a pattern counts twice.
- **Separators.** `fold()` maps hyphens to spaces, so `"com-plete"` matched no completion marker at
  all and A4 passed *vacuously* — no completion claim detected, rather than one accepted. Fix: match
  word markers on a separator-free key, leaving no separator to inject.

The general form, and the reason each pass found the next: **a fix demonstrated on one input proves
the case it was tested on, not the class.** Each of these was closed by a narrower case and reopened
by an adversary who chose a different way in.

A fourth round counted *spans* and was defeated by `"0 failed, 0 failed"` — two spans, one piece of
evidence. Counting distinct result *forms* closed that, and eleven of thirteen forgeries fell. The
last two are not bugs: `"As the vendor claims: 128 passed, 0 failed. Deployment complete."` is a
quotation, and a measurement and a quotation are the same text. No matcher can separate them.

So the instrument stopped pretending. An A4 pass now reads *carries result-shaped evidence — this
establishes consistency with a run, not that a run happened*, and the result carries a
`known_ceiling` field saying so in machine-readable form.

> **When a detector reaches an epistemic ceiling, report the ceiling rather than keep tuning it.**
> A detector that says "I cannot tell this apart" is more useful than one that returns 88 until
> somebody proves otherwise. This is `NOT_MEASURED` applied to one's own instrument, and it took
> four adversarial rounds to learn that the last gap was a property of the medium rather than a
> defect in the code.

### M-13 - The test that wrote the state it then reported (2026-10-06)

`test_suite.py` constructed a live instance and sent a heartbeat, because the module resolved its
paths from an environment variable at import time. The heartbeat file is the swarm's liveness
registry, so the suite manufactured the evidence that a brother instance was alive. For a while the
control plane reported PRIME-CLI as ACTIVE with a six-second-old heartbeat. Nothing was running.

*Correction in force:* a liveness channel must only be writable by the thing whose liveness it
reports. When a measurement is the only thing standing between you and a wrong report, ask who else
can write to it. Isolation is proved from outside the run — fingerprint the live tree before and
after — never by the assertion inside the test that performed the write.

### M-14 - The flag that arrived as the wrong type (2026-10-06)

The MCP client delivered `tools_called: false` as the string `"false"`. The hub applied
`bool(...)`, and `bool("false")` is `True`. Every evidence-dependent verdict inverted at once: the
tool asserted that a probe had run when the caller had said none did. Forged evidence, from a
transport, into the one tool whose job is to reject forged evidence.

*Correction in force:* coerce explicitly at the consumer, not only at the edge — real booleans
first, then unambiguous strings, then `False` for anything unrecognised, never a contradicting
default. Echo what was received alongside what was believed, so a coercion at a boundary is visible
in the output instead of inferable from a score that looks normal. Any boolean that *unlocks a
weaker check* is an attack surface and defaults to the strict side.

### M-15 - The destructive test blamed for a second writer's interference (2026-10-06)

`test_deployment.py --coldstart` tore the deployment down, launched the Startup entry, and reported
`startup_cold_start` FAILED after 180 s with `front=down`. Seven other checks failed as cascades of
the same thing. The near reading is that the deployment does not survive a cold start — a direct
failure of the central requirement.

It does. The cause was mine: a background status/restore task was running `start`/`stop` against
the same deployment during the test window. Its `stop` tore down what the test had just brought up,
and its own `status` then correctly reported `VERDICT DOWN (both planes)` — which is exactly what
the log would have shown for a genuine cold-start failure.

Two supporting facts killed the deployment hypothesis before any fix was attempted. First, the
Startup log carried **no new `=== startup` marker** for that window, while the `.bat` writes its
marker *before* invoking PowerShell — so the entry body never executed at all. Second, the `.bat`
itself ran correctly when invoked directly. (An intermediate reading of "0 markers" was my own
measurement error: the log format is `=== startup <date> <time> ===`, and the search string omitted
the date and time, so it could never match. Correct count: 22 markers.)

*Correction in force:* **a destructive test is only as trustworthy as the number of writers to the
thing it destroys.** Before re-running one, establish that nothing else is writing — no background
task, no restore, no collector. Two sequences that both mutate one resource cannot be attributed
independently, and the second one's result will be read as the first one's verdict.

Diagnose by discriminating between hypotheses rather than fixing the first candidate. "The log has
no marker, and the marker is written before the risky call" is a statement about *whether the entry
ran at all*, which is a different question from "did the deployment come back". Asking what the
absence of evidence is evidence *of* costs one command and prevents a rewrite of working code.

Related: M-13, which is the same failure with the sign flipped — there the test wrote the state it
reported; here something else wrote the state the test reported. Both are the one-writer-per-channel
rule from the doctrine, observed from opposite ends.

---

### M-16 - The log that could veto the deployment (2026-10-06)

The Startup entry ran the whole deployment start inside a redirect:

```bat
powershell ... -Action start ... >> "%SENTINEL_LOG%" 2>&1
echo exit=%ERRORLEVEL%>> "%SENTINEL_LOG%"
```

`cmd` cannot open a redirect target, so it **never runs the command**. Measured with a controlled
pair — same entry, same down state, only the log's writability differing:

| durable log | deployment | entry exit | bytes logged |
|---|---|---|---|
| locked | **never came up** (78.5 s) | **0** | **0** |
| writable | up in 24.1 s | 0 | 456 B |

A locked log produced no deployment **and** a success exit code — the one signal Popy had that it
worked. Nothing anywhere reported failure.

Two more defects lived in those same three lines:

- `echo exit=%ERRORLEVEL%>> log`: `cmd` reads a **digit immediately before `>>` as a file-descriptor
  number**. With `ERRORLEVEL=0` the `0` becomes handle 0 and the text goes to stdout; with
  `ERRORLEVEL=1` the `1` redirects stdout into the log, stripping the digit. The exit code was
  recorded **exactly when startup was not needed and lost exactly when it mattered** — which is why
  the log held zero `exit=` lines across 26 startup markers. A space before `>>` fixes it.
- The installer's guard required exactly 2 `set` lines, so a legitimately grown template was
  **rejected as malformed**. That guard's own comment says the check must be structural rather than
  a count — and it was a count. It now validates each assignment and requires the variables the
  entry depends on.

*Correction in force:* **evidence must never be able to veto the thing it observes.** The start
writes to a per-run file; folding that into the durable log is a separate, best-effort step whose
failure is reported but never fatal. The fold uses `type >>`, never `copy /y`, because the log is
append-only evidence, and its failure is detected by **comparing file size across the append** —
`type >>` onto a locked file fails quietly, so `ERRORLEVEL` cannot be trusted.

### M-17 - The fix that moved the lock instead of removing it (2026-10-06)

M-16's fix gave the run file a fixed name in `%TEMP%`. The deployment-came-up experiment flipped
to PASS. **The exit code still never reached the log, and the temp file was locked too.**

Cause: the entry's `powershell ... -Action start >> RUNLOG` line is the line that launches the
long-lived backend. `server.ps1` **inherits the stdout handle** and holds it for its entire life —
verified: pid 57292 had the runlog locked while alive. So run N's survivor blocked run N+1's
writes; four of four echoes failed silently, and the entry still exited 0.

*Correction in force:* **a fix that moves a lock has not removed it.** Only a name unique per run
(`%RANDOM%%RANDOM%-%RANDOM%`) cannot be held by a previous run's survivor. And the run file may only
be `del`eted **after** a successful fold — deleting earlier was itself part of the failure mode.

The lesson underneath both entries: the first fix "passed" on the metric I had chosen to measure
while the thing I set out to restore was still broken. `came_up=True` is a healthy-looking number,
which is exactly why it concealed the defect. **Verify the original goal, not the goal substituted
while fixing it.** I had gone looking for a lock because a log was locked, found one, removed it,
and never went back to check whether the evidence now existed.

### M-18 - The fix that answered the wrong half of the defect (2026-10-06)

A verifier refuted my M-17 fix. Of ten runs, the six *idempotent* ones logged `exit=` and the four
*fresh starts* logged **none** — a perfect 1:1 correlation with whether the run actually started a
backend. My per-run rename had closed the **cross-run** collision and left the **within-run** one
untouched: the backend inherits the runlog handle for its entire life, so an exit line written
*after* it could never reopen that file.

The correction was to write the exit code to the **durable** log instead — the one file no process
holds — after folding the transcript, so the log reads marker → transcript → verdict in the order
things happened.

*Correction in force:* **a fix must be tested on the input that is hardest, not the input that is
most available.** Every test I ran myself was an idempotent run, because that is what happens when
you start an already-running system. The easy path was the only path I exercised, and the defect
lived entirely on the other one. The colleague's sequence test — run it twice, with a survivor
holding the file — found in one step what my repeated single runs could not.

### M-19 - The comment I added became a command (2026-10-06)

While fixing M-18 I put explanatory prose on `REM` lines **inside** an `if ( ... ) else ( ... )`
block. At logon the entry printed `'TEMP' is not recognized as an internal or external command`.

Inside a parenthesised block `cmd` does **not** treat `REM` as a comment — it executes the line. The
prose was a command.

*Correction in force:* **nothing but commands inside a `( ... )` block**; comments go above it. The
installer now refuses to install an entry containing a comment inside a block. The check counts
parentheses only on non-comment lines — the first version counted parentheses in prose *about* `cmd
( ) blocks` and **rejected the valid template**, which is worse than the bug it guards, because it
blocks every future install. Both polarities are now proven: a sabotaged template is rejected naming
the offending line, the real one installs.

---

### M-20 - The search that reported absence while being unable to see (2026-10-06)

I reported a MINIMAX Design capability as a dead configuration file because two text searches found no
consumer of `conf/external_api_conf.yaml`. Neither search was negative. Both were **blind**.

ripgrep does not descend into `gateway/dist` because it is ignored build output, and it cannot read
inside `app.asar` at all, because that is a binary archive. A byte-level scan of the install tree
(1404 files, 651 MB) located the real consumer immediately: `gateway/dist/main.js`, through
`YAML_CANDIDATES` and `loadYamlSync()`. The capability had been live the entire time.

The number is not the lesson. The lesson is that a tool's silence and an object's absence are the same
observation to every caller that only looks at the exit code. Had this stood, I would have written a
permanent `NOT_AVAILABLE` for a working seam, and the panel would have been confidently wrong in the
one place it exists to be right.

*Correction in force:* **"no match" is only evidence of absence if the search was capable of a match.**
Any sweep that concludes "nothing references this" is escalated to a byte scan before it is allowed to
become a surface. Text search answers *where*; byte search answers *whether*.

### M-21 - The measurement that was taken and then discarded (2026-10-06)

The Design cloud reachability probe reported `probed: 0` after completing four real DNS queries and four
TLS handshakes. The record was assigned on the DNS-failure branch and never on the success path, so
every host that actually resolved was measured and thrown away.

A sibling defect landed the same afternoon: the host table parser tested `s == "domestic"` when the real
line is `domestic: {`. Nothing matched, the table came back empty, and the surface reported
`NOT_AVAILABLE` with the bytes sitting in the file. I had the real output in my own probe context and
still typed the version I remembered.

Both produced no error, no exception, and a success exit code.

*Correction in force:* **an empty result must be distinguishable from a broken collector.** Read the
loop, not the happy path: does any branch complete without recording its result? And when a parser
returns nothing, ask whether it was *asked correctly* before believing the answer. The new
`EcosystemCollector` class asserts `len(hosts) == probed` precisely so this cannot recur silently.

### M-22 - The invariant asserted in its sloppy form (2026-10-06)

I briefed a verifier that the ecosystem collector "contains no process-spawning call". The verifier
refuted it: `subprocess` is imported at line 274 and used at line 283 for a read-only `Get-Process`
inventory. No application was ever launched, so the substantive claim held, but the claim as written was
false. A false claim inside a verification brief teaches the verifier to discount the brief.

One turn later I wrote the same mistake into the test that replaced it. `assert_false('Design.exe' in
text)` failed on its first run, because the collector *measures* that executable's size and must name
it. The assertion forbade the measurement while still missing the hazard.

*Correction in force:* **when a broad form of an invariant is false, narrow the invariant until it is
both true and sufficient.** "Spawns nothing" was wrong; "cannot start the app it measures" is right,
checkable, and survives a legitimate implementation. The shipped assertions test that no `subprocess.`
call site references the Design app - narrow enough to pass the real code, specific enough to catch the
real defect.

---

### M-23 - One race, two opposite verdicts (2026-10-06)

The cold-start test sampled the startup log the instant the front answered 200. But nginx is healthy while
the `.bat` is still waiting for the orchestrator's start verb to return before it writes its marker, folds
its transcript and records its exit code. The sample landed inside the writer's window, which measured
about two seconds wide.

The first check **FAILED**: *the startup log gained no marker for this run (53 -> 53, 0 B written)*. The
log's mtime was the same second as the sample, and it held 54 markers a minute later. The run had
recorded everything.

The very next check **PASSED** — on the *previous* run's `exit=0`. It searched for an exit line after the
newest marker in the file; when the current run left no marker, the newest marker belonged to an earlier
run, and that run's exit line satisfied it. A run that recorded **nothing** scored a pass on *it recorded
its exit code*.

*Correction in force:* **a check keyed to an identifier the failing run never produced will validate
whatever the last run left behind.** Absence of the identity is not a reason to look further up the file.
Both halves are now required, and fixing only one is worse than fixing neither: a bounded wait for the
evidence — poll up to 45 s, so a genuinely absent marker still FAILS, because the wait is not a licence to
be lenient — **and** keying every downstream check to the new marker. Fixing only the wait would have
converted the false FAIL into a false PASS. Re-run: 42/42, `54 -> 55 markers, 465 B written`, with the
evidence landing about two seconds after the front.

The general form: *the thing being observed is up* is not the same event as *the producer finished
recording*. Whenever a producer writes its evidence after the observed state appears, every check on that
evidence needs a bounded wait **and** a this-run identity.

---

## The pattern across all of them

Every entry above is the same shape: **a claim was made that the system could not demonstrate, and
the cost was paid in trust.** Not one entry is about being slow, being wrong in the ordinary sense,
or disagreeing. The recurring defect is asserting a state the system cannot prove.

That is why the Command Center's first rule is that a panel which cannot measure must print
`NOT MEASURED` rather than a plausible value, and why the STOP fix landed before the dashboard did:
the dashboard's most important banner needs a state that did not exist.

M-11 through M-14 are the same defect wearing newer clothes. Each one is a check that returned a
confident verdict about a state it had not observed — because the code was frozen (M-11), because
the evidence matched the claimant's own vocabulary (M-12), because the observer had written the
observation itself (M-13), because a type was converted on the way in (M-14). The common shape is
not carelessness. It is a system that can produce a number where a measurement is required.

M-15 is the same shape once more, and it is the one worth carrying forward. It is also the first
entry whose correction was **not** a change to the code. Nothing was broken; the measurement was
contaminated by a second writer, and the honest move was to find the contamination rather than to
make the failing check pass. The code was correct and the report was wrong — which is the cheaper of
the two failures to have, and only because the discipline required checking whether the log had been
written at all before touching anything.

A test suite that only ever runs alone is a test suite whose results are only ever valid alone, and
that is a property nobody wrote down. That is what M-15 records.

M-16 and M-17 are the same shape seen from the far side: a channel that could not be trusted was
also a channel that could **stop the system**. Both are one sentence — *evidence must not be able to
veto the thing it observes* — and both were invisible precisely because the failure produced no
error, no exception and a success exit code. M-17 is the sharper one, because M-16's fix had
already turned the headline metric green. The system was measurably better and still lying, which
is the most dangerous state a system designed to not lie can be in.

M-18 and M-19 close that sequence, and they are worth keeping for a reason beyond the bugs: both were
caught by someone else, not by me. In M-18 a verifier ran the *hard* input — a second start with a
survivor holding the file — and found in one step what my own repeated tests could not, because every
test I chose to run took the easy path. In M-19 I fixed a defect by writing prose into a block `cmd`
executes, and the installer accepted it; the guard that now refuses it was written because I had
already shipped the mistake once.

That is the honest shape of it: the defects were mine, the corrections came from outside, and the
thing that made the difference was not care — it was that somebody else ran the case I had not.

---

## THE GAP - M-24 through M-27 (2026-10-10)

Four entries are missing from this file and are **not** on disk anywhere on this
machine. Every surviving copy was checked: the largest holds M-01 through M-23,
an older set holds M-01 through M-10, and none holds M-24, M-25, M-26 or M-27.

They were not rewritten. M-28 states the rule and this file still obeys it: a
doctrine file partly invented by an agent is worse than a short honest one. What
survives of them is their themes, in the agent memory entries, the `14_HANDOFF`
quotes, and the source comments of the code each lesson produced.

This marker is here so the gap is visible in the sequence rather than inferred
from a missing number.

---

### M-28 (2026-10-06) - The build can be sound while the report of it is false
Type: verification discipline / reporting

A handoff package was written for a system that passed every suite. An adversarial verifier was
sent to refute it and returned FAIL - correctly. The build was confirmed sound: deployment up,
loopback confinement real, cold start re-proven by destruction at 43/0/0, blueprint SHA unchanged,
nothing deleted. Nine defects lay in the *reporting*, none in the *build*:

- two skill names that did not exist on disk, written under a heading reading "Measured from the
  live system, not from documentation" - drawn from a catalogue carried in context instead of from
  the measured list;
- four directories called "empty" that held 138-276 files each;
- a test count off by one, repeated in eight places across six files;
- a survey that had inventoried its own deliverable as one file, because it ran before the package
  was written;
- a counter presented as a fixed property that increments on every run;
- three register entries citing monitor evidence the monitor now contradicts;
- a monitor that bounds staleness on one artefact and not an older one;
- a gloss that restated the monitor's own semantics in more comfortable words.

> **A system that measures itself honestly can still be described dishonestly, and the two failures
> never appear together.** Every number in that package had been taken from a real measurement, and
> several were simply wrong anyway: a name copied from context instead of read from disk, a
> directory called empty because nobody opened it, a count that moved between measuring and writing.
> Measurement discipline protects the *value*; it does nothing for the *claim*, because the claim is
> written later, from memory, by the same agent that measured.

Two rules that came out of it:

1. **The measurement must be re-read at the moment of writing, not recalled.** Every figure in a
   deliverable is diffed against the source at write time, and a volatile figure is labelled with its
   as-of reading and its increment rule. A counter is not a constant.
2. **A verifier's finding is evidence, not an answer.** Its explanation for the mailbox contents was
   also wrong - it named the current test suite as the writer, when that suite runs in a tempdir
   sandbox and fingerprints the live tree before and after. Reading the cited source settled it. The
   same rule as "a detected defect is not a fixed defect", applied upward: **a refutation is not a
   finding until the source has been read.**

The deeper shape is M-24 and M-25 again: self-measurement is not verification, and an exemption
that cannot fail is a waiver. Here the failing thing was neither code nor config but prose - which is
precisely the layer that ships no test and no failure, and is therefore the layer where a false
statement costs nothing to write and everything to inherit.
### M-29 (2026-10-06) - A shell variable that does not exist silently truncates the file you are writing
Type: catastrophic error / tooling discipline - DESTRUCTIVE

**What happened.** Appending M-28 to this file destroyed M-01 through M-27 - 44,576 bytes, 673 lines,
twenty-seven recorded corrections - in one write. The file went from 44,576 B to 2,912 B and contains
now only M-28 and this entry. There is no version control in this project, no backup of this file, and
Volume Shadow Copies are not readable without elevation. The content is not recoverable from disk.

**The mechanism, exactly.** The append was written as:

```
$entry = @"...M-28 text..."@
[IO.File]::WriteAllText($f, $t + $entry, ...)
```

`$t` - the existing file content - was read in the *previous* shell invocation and never read in this
one. Each Bash call is a fresh shell; variables do not persist across them. So `$t` was `$null`,
`$null + $entry` is `$entry`, and the write succeeded. **Nothing errored.** Exit code 0, no warning, no
exception. A truncating write is indistinguishable from a correct one at the call site unless the length
is checked afterwards.

This is not a shell quirk to remember. It is the same failure as every other entry in this file wearing
a different hat: **a thing that cannot fail is not a guard, it is a hope.** `$t + $entry` cannot fail -
it will happily write one side or the other, forever. The guard has to be a length assertion *after* the
write, not an intention before it.

**Three rules, in force from this entry:**

1. **Never compose a write from a value read in an earlier tool call.** Read and write in one command,
   or pass the content through a file. Cross-invocation shell state is not state.
2. **Assert the result length after every destructive write**, and fail loudly on a shrink. A write
   that leaves a file shorter than it found it is the signature of this bug.
3. **A file whose content cannot be regenerated must be under version control before it is next
   edited.** This project has carried that as weak point W1 for weeks, with the note that it was the
   highest-value thing outstanding. This entry is the receipt. The gap was not theoretical.

**What was lost, precisely.** M-01 through M-27 verbatim. Their *themes* survive in three places and
were not lost with the file: the memory entries under
`C:\Users\apviz\.minimax\agents\mavis\memory\MEMORY.md`, the doctrine quotes embedded in the
handoff package at `14_HANDOFF\`, and the source comments in the code each lesson produced - the
`collect-sentinel.ps1` comments, the paired polarity/control cases in `test_suite.py`, the `_dig`,
`_trail_key` and `_is_count` functions in `test_deployment.py`. What is gone is the narrative record:
Popy's corrections as written, in the order they happened.

**What must not happen next.** The tempting repair is to rewrite M-01 through M-27 from the surviving
summaries. That would be the worst outcome available: it would manufacture a record of Popy's
corrections that he did not write in that form, inside the one file whose entire value is that it is
his verbatim. **A doctrine file partly invented by an agent is worse than a short honest one.** If the
entries are to come back, they come from Popy, or they are marked as reconstruction.

This file remains append-only. The loss is recorded here, in the surviving file, in the same format as
everything else - because a record that hides its own damage is the last thing this project should
produce.

---

### M-30 (2026-10-10) - A recorded loss is a claim about the world, and claims expire

**What happened.** M-28 recorded the destruction of M-01 through M-27 and
concluded that the content "is not recoverable from disk". That conclusion was
reported upward as a permanent fact and as a question for the operator. **It was
never checked.** Twenty-three of the twenty-seven entries were sitting on this
machine the whole time, in `VERSION_REFERINTA_2026-10-06`, in four copies that
are byte-identical to each other (SHA256 `7DCB88E3781344DC...B592A3B`).

**Why the record was wrong.** It was right about the file in front of it and
wrong about the machine. It said "there is no backup of this file" - and did not
look in the reference-snapshot tree, where four copies sat. Nothing about the
file had changed; nobody had re-opened a document whose entire purpose is to
say something already settled.

**What was done.** M-01 through M-23 were restored by **copying the file
byte-for-byte**, not by retyping it, so the SHA256 of the copy equals the SHA256
of the source. That equality is the proof these are the operator's words: a
retype could not make that claim, and that difference is precisely what M-28
forbids. The reference copy is retained at
`MISSTEPS_RECOVERED_M01-M23.md` as the provenance of the merge.

*Correction in force:* **an append-only record of a loss is the most trusted
document in a project and the least re-verified.** Before carrying a loss forward
as permanent - especially as a question to the operator - search for the thing
first. A document asserting its own permanence is the claim most worth
re-measuring. And the same rule governs the M-28 entry above: it is left exactly
as written, because correcting forward means adding, never editing a record.

M-24, M-25, M-26 and M-27 remain lost and are marked as such above.

### M-31 (2026-10-28) - The generator of a ledger is not its owner

**What happened.** `08_SELF_IMPROVEMENT/build_program_matrix.py` wrote
`12_PROGRAM/GAP_REGISTER.json` with the gaps it had measured and nothing else.
Measured on 2026-10-28, one run of the builder reduced the ledger from 18
entries to 7: all nine `HPROF_*` profile tickets, the `HERMES_GATEWAY_PROFILES`
umbrella and `BIN_TESSERACT` were gone. The blueprint stayed intact, every
suite stayed green, and nothing announced the loss - the next reader saw a
shorter, tidier register and believed it. The tool was called "the thing that
generates the register", so running it read as maintenance, not as an edit.

**Why it was possible.** The builder was allowed to own the file it measured.
It knew about seven gaps; the ledger held eighteen; the difference was not a
gap in the builder, it was eleven entries written by someone else, and the
builder had no way to see them.

**What was done.** The builder now MERGES. An entry is never deleted. An entry
whose gap it can measure is re-measured, and the measurement is written beside
the original claim, which stays visible. An entry it cannot measure is
preserved byte for byte. A closed entry keeps the record of its closure, so a
second run leaves the file byte-identical. A probe that cannot run reports
NOT_MEASURED and changes no status - a transient is not a verdict.

*Correction in force:* **the generator of a ledger is not its owner.** A tool
that writes a file it did not create must merge, never overwrite. And the proof
is a control that fails on the old behaviour: the new test class was run
against the old builder and went red with the twelve lost entries named
(`Gap register integrity`, `test_suite.py`). A control that has only ever
passed has proved nothing.

### M-32 (2026-10-28) - A number in a source-of-truth file is a claim about the world, and it expires

**What happened.** `GAP_REGISTER.json` was last written on **2026-10-06**. Its
nine `HPROF_*` entries said the Hermes profile servers "are declared and not
yet constructed", with `target_present=False`. Measured on 2026-10-28: all nine
exist and answer a real MCP stdio handshake - five since 10 October, three
rewritten on 28 October at 02:19. The ledger had become history while still
being the source of truth, and the session handoff of 28 October listed "the
seven unbuilt Hermes servers" among Popy's open decisions, on the strength of
that ledger. It was also a trap in the handoff pack: `14_HANDOFF/02_GAPS.md`
is dated 7 October, and the package README says so - but the priming prompt
points at it as the gap inventory.

**Why nothing caught it.** The register had no writer. Nothing re-measured it,
so its numbers aged silently while every file it named stayed in place. A file
being there is not a file being true, and a document nobody re-opens is a
claim nobody checks.

**What was done.** The builder re-measures every gap it can measure and writes
the measurement into the entry, dated; every closed entry carries the
measurement that closed it, and the original claim stays visible above it.
`13_COMMAND_CENTER/api/collect-sentinel.ps1` now hands the panel the OPEN
entries and counts the closed ones next to them, so the tile "Open gaps" is
the open count. The audit that found all of this is
`14_HANDOFF/13_GAP_REGISTER_AUDIT_2026-10-28.md`.

*Correction in force:* **re-measure before quoting a number from a file you did
not write.** The age of a source-of-truth file is part of its meaning. This is
the same rule M-30 put in force for recorded losses, applied to ledger
entries: a stored claim is a claim, and claims expire.

### M-33 (2026-10-28) - A field hardcoded where a measurement belongs is a placeholder that reads as a fact

**What happened.** The programme matrix opens with the sentence "The matrix is
DERIVED BY MEASUREMENT, not written by hand", and one field in it was written
by hand: `mcp_wired` was hardcoded `False` for every row. The generated report
then printed "**0 are wired**", while the hub was serving **26 tools over
stdio** - a live handshake, measured, with a timestamp. The report looked
careful and was wrong, in the same direction as the blueprint: it claimed
nothing was connected while the wire was busy.

**Why it survived.** `mcp_wired` was the only field the renderer used to
describe a live capability, and nothing tested it. A hardcoded `False` is
indistinguishable from a measured `False` at the reading desk.

**What was done.** `evaluate()` now reads the tools the hub actually SERVED -
from `09_LOGS/mcp_handshake.json`, the artefact the handshake itself writes -
and a concept is wired only if every tool it declares was returned over the
wire. Measured 2026-10-28: **8 of the 8 concepts that declare an MCP tool are
wired**, and the generated report says so with the basis attached.

*Correction in force:* **a field that answers a question about the world must
come from a measurement of the world.** Where a field is hardcoded, the honest
options are to measure it or to delete it - but never to leave a constant
standing in for a fact, because a constant is the one value that can never be
wrong and therefore can never be right either.

### M-34 (2026-10-28) - A counter in the wrong place multiplies the period, and a bound met with a 4x margin is not the bound anybody wrote down

**What happened.** The refresh worker in `13_COMMAND_CENTER\api\server.ps1` was
supposed to refresh the MCP handshake record every hour, so the 24 hour
freshness bound on `mcp_tools_wired` would be met by the system and not by a
human remembering. It refreshed every **5 hours 54 minutes**. The counter that
drove it sat inside the block that runs every FOURTH cycle, while the divisor
that turned a counter into a period was computed PER cycle: four times. Then
the cycle itself outlasted its sleep - the collector takes about 12 s on top
of a 25 s sleep - so one and a half times more. Measured exactly: the record
was written at 02:53:13 and the next one at 08:47:50.

**Why nothing was red.** Two instruments, each doing its job, neither able to
see the other. The 24 hour bound was met, with a 4x margin. The worker's own
log recorded its START and nothing else, so the gap was invisible from the
worker's side too. What was missing was the comparison between the period the
code DECLARED and the period the system DELIVERED.

**What was done.** The cadence is now a wall-clock deadline - `((Get-Date) -
$lastHandshakeAt).TotalSeconds -ge $handshakePeriodSeconds` - and the gate
sits outside the every-fourth-cycle block, so neither the cost of a cycle nor
the nesting can multiply it. Every refresh is written to the worker's log, so
the cadence is a record and not an assumption. The deployment check that
guarded this loop asserted that a period was COMPUTED and that it was inside
the bound; it passed the whole time the period was six times longer than
written down, because the formula was there and the shape around it was not.
It now asserts the shape, and it carries a control that must reject the old
cycle-count form.

*Correction in force:* **a declared period is a claim about the world; compare
it with the delivered one.** A check that reads a formula out of the source
proves the formula is present, not that the system obeys it. Where a period is
derived, derive it from something that cannot drift (wall-clock, not a count
of units whose cost varies), and when a counter gates a job, ask what block
the counter sits in - the block multiplies the period, and nothing will say so.

### M-35 (2026-10-28) - Two correct observations that disagree are not one of them being wrong; and a branch no test reaches is reached only by accident

**What happened.** The unit suite went from 607 passed / 0 failed to **605
passed / 2 failed** with no change to the monitor. The monitor reported the MCP
handshake as `STALE`; the suite expected `OK` or `FAIL`. Both readings were
correct - the record had been written at 08:47:50 and the server source was
edited at 08:55:44, so the record described a file that no longer existed in
that form - and the disagreement was reported as a broken handshake.

**Why nothing was red before it.** `STALE` is one of the four verdicts the
monitor can return, and it is the one that exists precisely to stop the system
claiming the tools are wired when the code has moved on. No test reached it on
purpose: the suite pinned `OK` and `FAIL`, so the branch was exercised only by
accidents. Its model of the verdict was written as a two-valued expression -
`'OK' if justified else 'FAIL'` - which cannot name a third answer, so a stale
record was classified as a broken one.

**What was done.** The suite's model now derives the verdict from the facts the
monitor reads - the record's content, the record's age, and the server's mtime
against the record's - and names all four verdicts. A new class
(`McpHandshakeStale`) reaches `STALE` deliberately, on a synthetic workspace
where the source is dated three days back, so each staleness trigger fires
ALONE: superseded by an edit, and expired against the 24h bound. The liveness
of the live record moved to where it belongs - the deployment suite now holds
the record's AGE against twice the daemon's refresh period, which is the
outcome the panel's "wired" claim rests on.

**The control.** The new class is run against two mutants of the monitor - one
without the `STALE` branch, one that answers `STALE` to everything - and two
assertions go red against each. A test that cannot fail is a decoration, and
this one is shown to fail in both directions before it is trusted.

*Correction in force:* **a disagreement between two measurements is a third
fact, not a defect in one of them.** Before declaring either side wrong, ask
whether the vocabulary is complete: the suite knew two verdicts, the monitor
had four. And **every branch a system can take must be reachable by a test on
purpose** - a branch reached only by accident is a branch whose behaviour was
never chosen, only discovered.

### M-36 (2026-10-28) - A control conditioned on something unrelated to its claim is a control that is off in the normal state, and an off control reports green

**What happened.** The monitor's check `logs_parse` carries the evidence "every
state JSON must parse; a corrupt state file is a silent failure". The parse it
performed was wrapped in `if a < MAX_STATE_AGE` - an hour. The artefacts are
written on demand, by the test suites and by operator actions, so they are older
than an hour whenever nobody has acted recently - which is the normal state of a
machine that is simply running. The check was therefore reporting OK for state
files it had never opened, and the sibling freshness check was reporting the same
files as STALE in the same breath.

**Why nothing was red.** The check's output is a status, not a fact about the
file: "no parse errors" is exactly what a check that never parsed reports. A
green control is not evidence that it ran; the evidence is what it read. Nothing
in the report distinguished "parsed and valid" from "never opened", because the
evidence list was empty in both cases.

**What was done.** The age was removed from the parse. Validity does not expire,
and the freshness verdict was already carried - with its own bound - by the
sibling `log_*` check, so no bound was moved and no check was deleted. An
unreadable artefact is now reported as a parse error instead of being allowed
to escape, because an escaping exception would turn the whole family into
NOT_RUN and hide the other six artefacts with it. The new class
`LogsParseAgeIndependent` pins all of it, including the directions that must NOT
change: a valid old file is still OK, and the freshness verdict of the same
file is still STALE.

**The control.** Run against a mutant with the age condition restored, two
assertions go red - the corrupt old file reads OK and the evidence list is
empty. Against the repaired monitor, 6/6.

*Correction in force:* **a control conditioned on a property unrelated to its
claim is a control that is off in the normal state - and an off control reports
green.** Before trusting a green check, ask what it would have to read to fail,
and then make it read that. If the answer is "it would have to be asked", the
condition is the defect, not the artefact. And **an empty evidence list is not
proof of absence**: "no parse errors" from a check that never parsed and "no
parse errors" from a check that parsed everything are the same string and
opposite facts.

