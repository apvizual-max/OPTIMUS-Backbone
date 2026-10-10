---
name: minimax-optimus-dashboard
description: |
  Build a MiniMax OPTIMUS dashboard — a human–machine interface over a running
  system. Use whenever Popy asks for a dashboard, a console, a control panel, a
  monitoring surface, "something I can look at", or asks to copy or reuse the
  approach of the existing Control Center at http://127.0.0.1:8900/.

  This is the first of many. It is both a builder and a standard: the result must
  match the Control Center in accuracy, thoroughness, concept and strategy, even
  when the subject matter is entirely different.

  The method: ask everything first, research, iterate on questions, plan and get
  R0 approval only after testing the plan on paper, then build — and do not stop
  until there is nothing left to find.

  Carries a FAULT CATALOGUE of thirty mechanisms (A1-A4 product, B1-B26 harness)
  the Qwen dashboard, in the harness as often as in the product. The two that
  matter most: seeding state is not driving state (a suite that seeds proves the
  read path and nothing about the write path), and a trailing argument is a
  silent no-op, not a compile error.

  The worked example is `qwen-ecosystem-dashboard` — open it for real paths, real
  clause names and a measured build state.

  The method is also EXECUTABLE: `dashboard-build.dsl.js` in this same folder is the
  seven-phase build workflow, registered in the dynamic-workflows panel as
  "Dashboard Build — zero-context, seven phases" (status `pending_review`). When Popy
  asks for a dashboard for a system you have never seen, load this skill for the method
  and that workflow for the run.
license: proprietary
metadata:
  blueprint: C:\Users\apviz\.minimax-agent\projects\MINIMAX OPTIMUS CONTROL CENTER BLUEPRINT
  reference_implementation: C:\Users\apviz\.minimax-agent\projects\90_CONTROL_CENTER
  restore_point: C:\Users\apviz\.minimax-agent\projects\FULL_BACKUP_2026-10-04_QUARANTINE
  executable_workflow: C:\Users\apviz\.minimax\agents\mavis\skills\minimax-optimus-dashboard\dashboard-build.dsl.js
  workflow_run_id: 6b698fa6-1060-402d-a224-d07ed4bfb630
  workflow_name: Dashboard Build — zero-context, seven phases
  worked_example: C:\Users\apviz\.minimax\agents\mavis\skills\qwen-ecosystem-dashboard\SKILL.md
---

# MINIMAX OPTIMUS DASHBOARD

## The three artefacts, and which one you actually need

| Artefact | What it is | Load it when |
|---|---|---|
| **this skill** | The method, plus a fault catalogue of 26 mechanisms (A1-A4, B1-B22), each with the gate that catches it. | Always. It is the reasoning. |
| **`dashboard-build.dsl.js`** | The same method as an executable 7-phase workflow, registered for one-click start. | You are BUILDING a dashboard for a system you have never seen. |
| **`qwen-ecosystem-dashboard`** | The worked example — real paths, real ports, real clause names, a measured build state, and the R0 queue. | You are working on the QWEN dashboard specifically. |

A fourth thing exists and is easy to confuse with the third: `mavis-qwen-bridge-skill`
covers the Qwen Studio CLI and the `qwen-mcp-http` server. That is the QWEN *product*.
This is the dashboard built *over* the ecosystem. They are not the same system, and a
session that conflates them will edit the wrong file.

## The job

Build a **human–machine interface over a running system** — not a UI. Something
that tells the truth about a system you did not build, do not control and cannot
test, while re-rendering itself in front of a human who will act on it.

**One sentence decides everything:**

> If this dashboard is wrong, will it say so — loudly, specifically, and without
> making me go and find out?

If the answer is no, the work is not finished, however good it looks.

---

## The shape of every one of these

```
 collector  →  server  →  page  →  supervisor  →  self-test
 measures     writes     renders  keeps alive    proves it
              atomically          across reboots
```

Five pieces. The proportions change with the subject; the shape does not. Full
contract list: `BLUEPRINT/DESIGN/ARCHITECTURE.md`.

---

# THE SIX STAGES

## STAGE 1 — UNDERSTAND

**You cannot research what you have not asked about.** Ask everything at once,
batch it, and let him answer in one sitting.

Cover: **purpose** (who reads it, what decision it changes, how often, what must
never be wrong, what is explicitly not wanted) · **domain** (entities, exhaustive
state lists, what "healthy" means concretely, relationships, who restarts what) ·
**measurability** (what already exposes this, what has no interface, **how long
one read of each takes**) · **constraints** (where it runs, what's on the machine,
what must survive reboot, what must not be touched) · **standards** (what "good"
means to him, a reference, what the last attempt got wrong) · **risk** (what
happens if this is wrong, where the restore point is, who may run destructive
actions).

Full questionnaire: `BLUEPRINT/PROCESS/01_UNDERSTAND.md`.

**Do not leave until you can state the purpose in one sentence naming the decision
it supports.** If you cannot, you are still in stage 1.

---

## STAGE 2 — RESEARCH

Two halves. The visible one is mining a reference; the invisible one is
**inventorising the real system**, and that is the half that decides whether the
dashboard can be true at all.

**From the reference** extract, in order: navigation model · information hierarchy
· vocabulary · **its states** (empty / loading / stale / error / never-loaded —
six or more in one panel is a good sign) · live-update mechanism · **what it does
not have**, and **what you have that it does not**. One-directional gap lists
become scorecards.

> **Read it. Never write to it.** It is live work. Ideas to consider, not tasks.

**From the system** — walk every process, port, data source and failure you have
already seen in the logs. For every candidate number, **get a real figure for both
its source and its cost.** Assume a health check is fast; measure it. Assume an
agent's model is fine; measure it. Assume a background refresh works; watch it for
an hour.

**Name the load-bearing things as explicit prohibitions.** In the reference
implementation a 31-container swarm had already been lost once to a prune, and
that single prohibition shaped every command for the rest of the project.

**Ask what the dashboard itself costs** — processes, memory, bytes copied. An
instrument is not free, and the operator is owed the bill.

**Research produces new questions. That is the process working.** Go back to
stage 1. Two passes is common, three means the system is more interesting than you
thought. Stop when a full pass produces nothing new.

Detail: `BLUEPRINT/PROCESS/02_RESEARCH.md`.

---

## STAGE 3 — PLAN, TEST IT ON PAPER, PROVE THE DEPENDENCIES, THEN R0

**Nothing is built until he approves.** The plan is a set of claims that must each
survive an attempt to break it.

**Write the plan in four parts:** the architecture in one paragraph **with the
refresh budget computed** · the build order argued from rework cost · the design
language decided now · the definition of done, in his words.

**Build order — collector first, page last of the visible pieces.** The collector
is the only piece that knows the system; run it alone in a terminal before anything
else exists. Building a page against mock data means meeting real numbers that
disagree with your assumptions, and rewriting.

**Test the plan on paper.** Answer these five specifically:

1. What is the slowest thing here, and what happens when it is slow? *Multiply
   measurement cost by interval. If ≥ 1, the design is saturated and the operator
   will feel it as intermittent freezing.*
2. What happens if the data source disappears mid-render? *(Last good must
   survive, marked old. Stale data beats a blank screen, always.)*
3. What happens on restart? *(A process reads its source once. If the source can
   change, the running copy is not the source. Decide now whether the design
   detects that.)*
4. What is the failure mode of the failure handler? *Trace error → handler →
   display. If any link fails silently, there is a hole.*
5. What does this design cost the system it observes?

**Verify every dependency by running it.** A dependency you have not executed is a
hope. Record what it is, the version measured, what breaks without it.

**Write down the risks and the gaps** — and *what did I plan and not write down?*

**Then R0, and stop.** Present it, wait, revise if he changes it, re-take R0. Do
not start building "while you review."

R0 covers **the plan**, not the system. Once approved you still do not change the
behaviour of anything already running without asking. That is a separate decision
each time.

Detail: `BLUEPRINT/PROCESS/03_PLAN_AND_R0.md`.

---

## STAGE 4 — BUILD

Collector → server → page → supervisor → self-test. Each piece run and read on its
own before the next exists.

**Four decisions that determine everything downstream:**

1. **The collector prints.** One JSON blob, no HTTP, no storage, no rendering. That
   is what makes it runnable in a terminal and believable. **Build trace mode from
   the first line** — an env-gated marker before each section. It is not a
   debugging luxury: in the reference implementation the trace is what proved a
   "slow collector" was healthy and the real cost was one endpoint.
2. **The state write is atomic.** Temp file, then rename over. Never in place.
3. **A request path must be UNABLE to start a measurement, and must not run slow
   work at all.** The most expensive rule in the architecture, and the one most
   often broken *in the wrong direction*. Two halves, and satisfying one while
   missing the other is the common failure:
   - *No measurement.* Read-only: `Get-StateJson -MaxAgeSec -1`; the refresh
     worker owns timing. Raising the threshold until its budget exceeds one
     measurement cycle was tried: it made every request past the limit collect
     inline, which starved the worker and left the cache permanently stale, and
     `/api/state` began returning a zero-byte body.
   - *No slow work.* A cache policy cannot shorten a 40-second model call. Any
     request that could take seconds — a model, a `docker exec`, a port probe —
     must return a **job id** immediately and let a background job do the work
     while the page polls. On the reference this was measured: a 26–70 s analyst
     call froze every poll for its full duration, and a *single* line of
     `Get-NetTCPConnection` ×7 (25.5 s of WMI) froze it just as thoroughly. The
     second one had been in the code the whole time, hidden behind a line that
     looked free.
   **Measure the cost of every call on a request path.** A function being "just
   a state read" says nothing about what else it calls. The freeze moved twice:
   once into a cache threshold, and then — after that was fixed — into a single
   line of port probing that had been sitting in the digest the whole time.

   **A timeout shorter than the thing it measures is not caution, it is a dead
   sensor.** The reference probed a bridge with an 8-second budget; four live
   samples came back at 9.43 / 9.91 / 10.42 / 11.33 s. It timed out on **100% of
   runs**, so that bridge's twelve checks had *never once* been recorded — while
   the tile above read `2/2 healthy` and the card beneath read
   `unknown · 0ok/0w/0f`. The file's own comment admitted it. Measure the
   subject, then set the budget above it; and when a field is permanently
   `unknown`, suspect the timeout before you trust the number next to it.
4. **Self-contained, or it is not done.** No CDN, no webfont, no network. It must
   work on a disconnected machine, and a test should *assert* zero external
   requests rather than hope for it.
5. **Cap what a layout can grow to.** A grid without `align-items:start` stretches
   every card to the tallest in its row, and a card with no `max-height` grows
   until the tab does — one status tab reached **5747 px** and needed a full
   scroll to read. Set the cap well above the tallest legitimate card so ordinary
   ones are untouched, and let runaway ones scroll internally. Long prose belongs
   in the documentation, not stacked inside a status console.
6. **Ask what a layout is hiding, not just what it shows.** A 35-day heatmap whose
   idle cells were `rgba(127,127,127,.10)` on a dark canvas made 30 of 35 days
   invisible: the grid read as "there is nothing here" when it meant "nothing
   changed that day". An empty state is information, and has to look like one.

**The actions boundary.** If the page can run commands it is a remote execution
surface aimed at the operator. Whitelist by **identifier**, resolved server-side
from the measurement. The page never sends a command. Read-only by default. Cap
the output. Never expose a prune. Echo the command back with its result.

**When the order turns out to be wrong:** stop, write one paragraph — what you
expected, what is true, what it costs, what you propose — and wait. Working around
it silently is how a five-hour outage ships with a green suite.

Detail: `BLUEPRINT/PROCESS/04_BUILD.md`.

---

## STAGE 5 — VERIFY

**The most-skipped stage, and the only one that can tell you whether you built
something or imagined one.** The reference implementation reported 7/7 for hours
while a headline feature had never once worked.

**Three layers, and you need all three:**

- **File-level** — does it parse? Proves almost nothing. A page that does not
  parse still answers 200, still serves perfect data, still logs nothing, because
  no statement ever ran.
- **In-page** — is it alive *from inside*? Script executed, tabs render, icons
  paint, font loaded, zero external resources, data fresh, every control wired.
  But **a structural check cannot catch a handler that writes to a dead node.**
- **Behavioural** — *run the thing, from the outside.* Load it in a real browser.
  Read rendered **geometry**, not element existence. **Press every control and
  read what appears.** Watch across a re-render — the failure that hides best
  appears and is then wiped by the next poll.

**Verify honesty, not just function.** Prove a good state reads good; prove a bad
state reads bad **and differently**; prove numbers move when the measurement moves;
prove an absent number is *explained*.

**Prove survival:** kill it, reboot it, break the source, throttle the link, fill
the disk. **The real test of a supervisor is that the machine recovers with no
human present.**

**Break your own checks.** A verification suite nobody has seen go red is a
decoration. And before believing a check: *could it pass on broken code? could it
pass on fixed code? is it reading the object or a neighbour?*

Detail: `BLUEPRINT/PROCESS/05_VERIFY.md`.

---

## STAGE 6 — ITERATE

**You are not done when it works. You are done when you can no longer find
anything wrong.**

Six passes, each from a **different angle** — running the same tests again finds
nothing:

1. **Press everything.** Read what appears.
2. **The shape sweep.** Take your most recent defect and grep for its *shape*, not
   its symptom. A fix is not done until you have found its siblings.
3. **Make it lie.** Deliberately break it, confirm each layer goes red.
4. **The numbers.** Every figure traced to source. Any denominator missing? Any
   number rounded into a lie?
5. **The cost.** What does the dashboard consume — including your own maintenance
   habits?
6. **The handover.** Could a stranger use this with no context?

**Stop after two consecutive passes from different angles find nothing.** Keep the
list of things noticed and not done — that list is the honest handover, and it is
what the next person reads first.

Detail: `BLUEPRINT/PROCESS/06_ITERATE.md`.

---

# FAULT CATALOGUE

Fifteen faults that each happened for real on the Qwen dashboard over runs 19–30, and
each cost a day or more to find. Not principles — **mechanisms**, so that the next
build recognises one on sight instead of rediscovering it.

The rule that governs all of them:

> **Before repairing a red, ask whose defect it is.**
>
> In those runs more reds were the *harness* than the product, and every one was
> reported as a product defect with total confidence. Sixteen independent clauses
> agreed with each other, which reads as a strong signal rather than a weak one.

---

## A — Faults in the PRODUCT that a passing suite did not see

### A1 · A trailing argument is not a compile error, it is a silent no-op

A driver declared `(fx, openId, ledgerRaw)` and five call sites passed **four**
arguments. JavaScript discards the fourth without a sound, without a stack, without a
type error. The fixture was silently never seeded. 16 clauses went red against a
product that was correct on every one of three separately measured links.

> Order mismatches are checkable. Count mismatches are not, so nothing checked it.

**Gate:** assert arity *inside* the function and throw. Then call it with the offending
shape inside a test and require the throw — a guard nobody has seen fire is a comment.

### A2 · `hasPrev` derived from the wrong half of a comparison

A flag meaning "there is an earlier sample" was computed from `newest`. With a
one-sample history it said yes, and two dozen lines later dereferenced `null`. The
function was `async`, so the `TypeError` surfaced as one unhandled rejection and
silently cancelled **every statement after it** — including a panel nine lines below.
**The whole tab rendered blank after every page refresh.**

**Gate:** test the second load, not the first. A state that only appears once history
exists is a state a fresh-profile suite never visits.

### A3 · A button that passes no arguments to a defaulted writer

`record` called `save(id)` where `save` defaults missing fields to *empty*. Pressing it
overwrote a good record with an empty one and then deleted the draft. The chip still
rendered, so the loss was invisible on screen — not just to tests.

**Gate:** press every control in a real browser and read what appears.

### A4 · One throw cancels every later statement in a render chain

Order of statements in a render function is a dependency nobody wrote down. A guard that
**catches and drops** trades a blank tab for a quiet one. Paint the failure into that
panel's own container, in the UNKNOWN red used for a reading it could not take.

> And then: a guard **changes what a fault looks like**. A mutation survived with zero
> red after the guard landed, because the missing panel no longer went missing — it went
> *red and labelled*. The clause has to follow the fault to where it now shows.

---

## B — Faults in the HARNESS, reported as product defects

### B1 · A clause whose id, matcher and surface disagree

The clause's id was written from the note's wording, its regex from the drawer's, and it
read the note. It went red against a correct panel — and the drawer's actual wording was
measured by **nothing at all**.

> A clause pointed at the wrong surface is worse than no clause: it reports a defect
> that is not there, and leaves the real surface unmeasured.

**Gate:** grep the source for the phrase before touching the product.

### B2 · A flag and its explanation sampled at different instants

`failed` was recorded per test case; the text explaining it was dumped at the end, by
which time the page belonged to a later case. The explanation described a different run
than the flag beside it.

**Gate:** a flag and its reason come from the same snapshot, or neither is evidence.

### B3 · `await` unwraps the promise

Detecting "is this a thenable" *after* an `await` is never true. A counter printed **0
awaited pairs** while every async renderer was in fact being awaited. The verdict was
right; the number describing it was a lie.

### B4 · The exact fixture constant, hand-typed twice

The expectation was written out by hand and disagreed with the fixture on two of three
elements. 21 correct measurements reported red.

**Gate:** when an exact-match clause fails, diff the two strings character by character
*before* touching the product.

### B5 · A mutation marked SURVIVED by the wrong clause

A `mustBreak` list named a second clause the mutation could not affect. The mutation
changed behaviour and was reported as surviving. The clause was right; the expectation
wrong.

> Padding `mustBreak` past what a mutation can distinguish reports a denominator larger
> than the coverage. Name only clauses that discriminate.

### B6 · A failure with no name

A sabotage reported "3 of 4 caught" and the file could not say where. The run that
revealed the cause also carried the lesson: **print the names of the red clauses, not
only the count.** A count with no names is a question without an answer.

### B7 · A fixed time budget under load

A 10-second polling window missed once, beside a suite holding twelve Chrome instances.
The panel was never broken — it painted in 250 ms, and three clean runs confirmed it.
The budget was the fault, not the product. But widening the budget alone only makes the
next failure slower to notice, so a failure must also **report what it saw**.

### B8 · `innerText` read as content

`innerText` is the **rendered** text: raised by `text-transform`, reflowed by wrapping.
A 150-character register line came back as three newlines, so a drawer holding exactly
three lines read as six. The panel was right; the reader was reflowing it.

**Gate:** `textContent`, per element, for content equality.

### B9 · A counter that writes a literal

"0 true" as fixed text is a claim the panel cannot be caught making false. And a
condition that was true but had no matching row disappeared silently, so the empty state
would have asserted the opposite of what had just been measured.

**Gate:** compute the number, and add a self-consistency guard that renders the
inconsistency in red.

### B10 · `Start-Process` without `-Wait`

`$p.ExitCode` is empty. The suite reported green it had never measured.

**Gate:** always `-Wait`, and report a **measured** exit code or none at all.

### B11 · Backticks inside a comment inside a Node template literal

Four times. A backtick closes the literal and compiles the remainder as Node source, so
the error names variables from the *page's* scope and points at a line that is fine.

**Gate:** `node --check` the harness **before** running it. That is the only thing that
has ever caught it, and it costs a second.

### B12 · `libuv UV_HANDLE_CLOSING` at exit

A script died before printing its summary, so the runner recorded "no matching summary
line" instead of a verdict. **Gate:** `ws.close()` before `proc.kill()`.

### B13 · `WriteAllLines` on an LF file

`[System.IO.File]::WriteAllLines` joins with `Environment.NewLine` — CRLF on Windows.
A 0-CR `index.html` became 7557 CRs. The tool meant to help destroyed the invariant.

**Gate:** `WriteAllText` / `WriteAllBytes` / the edit tool. Verify CR after **every**
write, not at the end of the session.

### B14 · A count typed by hand, where the CLAIM was the thing to check

Twelve checks in one runner asserted `all 105 contract clauses hold` and `21/21
click-through clauses hold`, with the numbers written out by hand. Two clauses were added
to the click-through suite. The suite correctly printed **23/23**. The runner asserted the
literal 21, found no match, and failed the entire regression as *"no matching summary
line"* — a message naming a symptom that has nothing to do with the cause. **Zero red
clauses. Zero product defects.** A check had simply grown.

The fix was not to retype `23`. It was to capture the number and verify the claim
instead: `N/N` with `N > 0`. Two neighbours were already capturing their counts and
comparing nothing — `caught=3/5 mutations caught` printed the expected shape and was
scored PASS. **The count was read, and then never read.**

> **Assert the property, never the instance.** A literal goes stale the moment the thing
> it describes gets better, and it fails for a reason that has nothing to do with the
> thing you are watching.

**Gate:** capture the number, assert the relation, and prove the rule can reject before
trusting it.

### B15 · The diagnostic and the gate computed the same fact separately

Fixing B14 introduced B14's own twin inside the same file. The verdict called
`parseVerdict(..., countRule)`; the line printed beside it called `parseVerdict(...)`
without. So three cases declared `ok: false` were **printed** `ok=true` directly above a
`PASS`. The report contradicted the report — and the copy a human reads is the copy that
gets believed.

Same shape as B1 and B2, one level up: a clause whose matcher and whose surface disagree.

> **If two places compute the same fact, one of them will drift — and the one a human
> reads is the one that will be believed.** Compute once, read it twice.

**Gate:** parse once per case; the gate and the diagnostic consume the same value.

### B16 · Killing a run mid-mutation leaves the product sabotaged

A regression was stopped to save time, while it was inside the sabotage phase. The
sabotage harness restores from an **in-memory** copy taken at the start of the run — so
killing the process kills the only undo. The mutation stayed on the live file.

The next run reported **four reds across suites that were green twenty minutes earlier**,
and the SHA no longer matched any known state. Read as a product regression. It was one
line, `const hasPrev = !!sample;` — a deliberate mutation of a repair — still sitting on
disk. Repairing that one line reproduced the previous SHA **byte for byte**, which is what
proved the mutation was the whole difference.

> **A restore that lives in the process's memory is not a restore point; it is a
> countdown.** Any run that mutates the live artefact needs its undo on **disk**, written
> and hash-verified *before* the first mutation, so an interrupted run is recoverable by
> an outsider who knows nothing about the run.

The tell that this is what happened: **a suite that was green minutes ago goes red, and
the reds are spread across unrelated suites.** That is not a product change. That is a
file that changed underneath you. Check the SHA against the pre-run value first, and
compare against **every** backup, not the newest-looking one — the state you want may
have no backup at all, in which case the repair is a one-line reconstruction proved by
the SHA returning to its known value.

**Gate:** never stop a mutating run without confirming which phase it is in; and keep the
undo on disk, not in the process.

### B17 · The one time a safety rule binds is the one time it is tested

There was an explicit authorisation to clean the disk, urgently, and the disk was at
98.8% with 5,5 GB free. The only sanctioned deletion route, `rm --` → `mavis-trash`,
calls `SendToRecycleBin` — **on the same volume**. It therefore frees exactly zero
bytes, and it also failed outright on the two largest candidates.

A permanent delete would have freed ~28 GB on the spot. It was not used, and the block
was reported instead: what was actually freed, measured, plus the exact commands the
operator can run himself.

> **A shortcut that relieves pressure and a rule forbids is not a solution — it is a
> decision that belongs to the operator.** What you owe him is the number you really
> freed, not a bigger number obtained by ignoring the constraint you were handed.

The tell that this was handled correctly is not that the disk got smaller. It is that
the report said **"I could not free space, here is exactly why"** — a sentence that
costs more to write than the one it replaces, and is the only sentence that hands the
decision back where it belongs.

Pressure is the point, not an exception to it. A rule obeyed on a calm day proves
nothing; the only moment it carries information is the moment it is inconvenient and
the person is visibly urging you on. **A bypass is least forgivable at exactly the
moment it would be most useful**, because that is also when the operator has least
capacity to check what you did.

This is B16 seen from the other side. B16 was breaking a rule by stopping a run badly.
B17 is breaking a rule by "helping" too well. Both are the same failure: optimising
for the appearance of progress over the integrity of the mechanism.

**Gate:** when a guard blocks a task the operator authorised, report the block with a
measurement, hand over the exact command, and stop. Urgency is the signal to slow
down, never to route around.

### B18 · A window narrower than the slowest participant passes by luck

The certification harness observed for a fixed **40 s** and required **three** complete
owner cycles before it would call a lock held. The owner's real cadence, measured live,
was **15.014 ms** — so 40 s is **2,66 cycles**. Every run therefore returned `UNKNOWN`, and
`UNKNOWN` blocks certification. The suite was not detecting a defect; it was structurally
unable to observe one, and it looked like caution.

The window had been chosen *before* anyone measured the cadence. Repaired by deriving the
window from the measurement (`planObservationWindow()`), with the old 40 s kept as the
**floor** — so the new code can never observe less than the old code did. Measured live
after the repair: **46,5 s = 3,10 cycles**.

> A `PASS` obtained inside a window shorter than the slowest participant's cycle is not a
> measurement, it is a coincidence. If you cannot state **who** writes, **how often**, and
> **how long one full cycle takes**, the verdict is `UNKNOWN` — never `PASS`.

**Gate:** before reading any verdict based on timed observation, measure the cycle time of
the slowest participant first. The window must cover at least three complete cycles, and it
is derived from the measurement, never chosen before it.

### B19 · A tree containing copies of itself counts the same byte more than once

Three enumerators measured one backup tree and produced three different numbers:
`Get-ChildItem -Recurse` → 37.473 files / 4.047 MB · `cmd /s` → 37.587 / 4.257.916.462 B ·
`robocopy` → 3.040 / 20,4 MB. **Git** → 3.236 entries / **22,1 MB**.

The backups contain their own `backups/` directory, so every enumerator descended into each
nested copy and re-counted the same physical content. The ratio was the tell: 3.040 → 37.473
is ≈12×, suspiciously round, because it is the number of nesting levels.

The number you can trust is the one produced by the tool that will actually carry the
payload. For "how much will this upload to", that is `git ls-files` + `git cat-file -s`.

**Gate:** when a tree contains copies of itself, no enumerator yields unique bytes. Measure
with the destination's instrument, not with `dir`, not with `Get-ChildItem`, and never
report a size you did not measure with the tool that moves the data.

### B20 · A gate that cannot function is a broken machine, not a project decision

A global git dispatcher required attestation on every commit in every repository. The
attestation tool was **installed and had never been configured** — no config file, no
credentials, no env vars, its port occupied by an unrelated service. It could not let
anyone through, anywhere, ever.

The tempting moves were `--skip` and `--vouch`. Both make the gate green while **a
verification that never happened**. The move used instead was `hooks disable` — scoped to
the one repository, one sentinel file, nothing uninstalled, other repos untouched,
reversible by deleting that file.

> `--skip` and `--vouch` **lie** about a check that did not run. `hooks disable`
> **tells the truth**: the gate is broken, take it off this repository so someone can work.
> One hides; the other clarifies. Before reporting a tool block as ACCESS — something only
> the operator can supply — read that tool's `--help` for a scope-limited, reversible,
> non-minting option. On this machine the subcommand that mattered had never been read.

**Gate:** search the disk for credentials and config before calling a block an
authentication problem, and check the tool's own command surface before presenting options
that ask the operator to choose.

### B21 · A document that states a now-false invariant teaches the next agent to break things

A project skill asserted: *"`server.js` has been untouched across runs 19–30 and must stay
that way."* It was false — the file had been repaired that same day, deliberately,
correctly, with a snapshot taken first. A session with zero context would have read the
invariant, seen a modified file, and restored it from the newest-looking backup — silently
undoing the repair.

Documentation written during a healthy phase decays into a lie during the unhealthy one,
and the lie is acted on by whoever arrives next. The fix is additive: the old invariant
stays, marked `SUPERSEDED`, with the reason and the current hash beside it, plus an explicit
"do not restore this from a pre-repair backup".

**Gate:** when an invariant changes, mark it superseded in place — never delete it, never
silently rewrite it, and always state what a reader must *not* do with the old rule.

### B22 · A repair that waits for a restart is a conditional repair

Split-brain in the guardrail process was resolved twice in one day: pid 18920, then an
orphan 24560 that only became visible **because the first repair made the instrument
sharper enough to detect it**. Neither repair removed the cause: three `supervisor.js`
processes still ran the pre-T48 code, so the next restart re-introduces it.

> A repair that depends on a restart is a repair with a precondition. Writing it as
> "fixed" without naming the precondition converts an open fault into a closed one on paper.

**Gate:** state the precondition with the repair. If the defect can return, say so where the
next reader will find it, not only in the message that announced the fix.

### B23 · A mechanism that explains silence is not a cause found

The supervisor "wouldn't start". `supervisor.js` compared the pid it had read back from disk
with its own — `readOwnerPid() === process.pid` — where `readOwnerPid()` returns a **string**
(`readFileSync(..., 'utf8').trim()`) and `process.pid` is a **number**. That read as a
complete, satisfying, self-contained answer. It was reported to the operator as the cause,
with a request for access attached. It was not the cause.

> A mechanism explains the silence. A cause explains why nothing came. They are different
> things, and they are easy to confuse because both are true and both sound like
> explanations. A repair built on a mechanism fixes the thing that was already quiet.

**Gate:** an explanation you can complete without changing anything about what happens next
is a mechanism, not a cause. When you write "I don't know why X happens", name what would
explain it if your explanation were complete — "I don't know" is a claim about a search, and
it is honest only when the search reached the end of the function, not the first promising
line.

### B24 · One occurrence is not all occurrences

The same defect lived at **two** sites in `supervisor.js`: the ownership *claim* (L104, where
a process that had just written its own pid was told it was not the owner — it exited 0 and
left a fresh lock owned by a dead pid, which the next five minutes of starts refused to
clear), and the ownership *release* (L118, where the legitimate holder could never delete its
own lock, so locks accumulated).

I cited the first, reported it, and moved on. Repairing only L104 would have unblocked
start-up while leaving the leak intact — a fix that works and is still wrong.

> The cost was not a misread. It was a reasoning error: the first explanation that fits is
> the most persuasive one on screen, and it fit perfectly.

**Gate:** when you cite a location from a file, count **every** occurrence before claiming
you found it.

### B25 · A count produced by the shell can be a false positive on nothing

PowerShell evaluates `@($null).Count` as **1**. Asked how many AI connectors LiveReview had,
the API returned `[]`; wrapped, the expression reported one. That became "connectors: 1, I
added it" — stated publicly, then retracted. The real count was 0, confirmed independently
from three angles: CLI exit text, the rendered UI page, the raw API body.

> The dangerous shape is not the wrong number. It is a number that came from something that
> was never a collection. It reads exactly like a measurement.

**Gate:** a count is a measurement. Name what was counted and prove the value was a
collection, not a scalar wrapper around null. Cross-check every count that closes a state
change through a second, differently-shaped route — never through the same call again.

### B26 · A gate built after the repair must declare that it was

`_t27-ownership-gate.js` — 7/7, with a mutant that runs the old and the new expression on the
same fixture and demands they disagree — was written **after** `supervisor.js` was repaired,
not before. It is honest and worth having: it proves the repair holds, and that the gate can
still go red. It cannot prove the repair was necessary.

> A gate written after the fact is a regression test, not evidence. Presenting one as the
> other is a small lie with a long shelf life — the next session reads the passing gate and
> concludes the diagnosis was settled before it was.

**Gate:** record in the ledger, at the point of the defect, whether the gate preceded the
repair. Not only in the commit message, and not only in the message that announced the fix.

---

## C — The two rules that would have saved the most time

> **1. Seeding state and driving state are different acts of testing.** A suite that
> seeds proves the read path and says nothing about the write path — and a read path can
> be perfect while the write path destroys data. 105 green clauses, and the form had never
> been pressed once.
>
> **2. Read the blast radius from the stack trace, not from a source window.** A clause
> asserting "exactly one panel fails" went red, and the stack showed a dependency that a
> 3000-character window had missed entirely. The clause asserted an independence the
> design did not have. Read the trace; infer nothing from a window.

---

## D — How these were found, which is the transferable part

| Source | What only it could see |
|---|---|
| Reading the live panel | Nothing. It renders four of five rows correctly forever. |
| A contract suite | Everything reachable by driving the render with fixtures. |
| **A click-through** | The write path, the reload path, anything only the second load takes. |
| **Fault injection** | Whether a guard contains, and whether it tells. |
| **Mutation sabotage** | Whether a check can go red at all. |
| A human eye on a screenshot | Escaping applied twice; a chip with no label. |
| Reading the failure message | Only if the harness prints a stack. |

Apply when: starting stage 5, and every time a clause goes red.

---

## INTERRUPTIONS — there are only three

During stage 4, stop **only** for:

1. **Information only he can provide** — a key, a credential, a decision, a path.
   Ask once, batched, with context: what you tried, what you found, exactly what
   you need.
2. **A tool, connector, or approach you do not have.** State the constraint and
   the options, not the distress.
3. **Risk that must be delegated** — destructive, irreversible, or affecting
   something load-bearing. *Delegating risk means building the containers first*:
   **backup** (hashed, sampled, links handled by kind not truthiness),
   **containment** (isolation; never a backup inside its own source), **quarantine**
   (proven restorable, self-describing, never nested, refreshed at checkpoints).

Everything else — "I noticed something else", "this would be an improvement",
"the evidence is very strong", "it's only a threshold" — **goes in the list and you
keep building.** Never edit an entry out; strike it through and say when.

> In the reference implementation a *proven* diagnosis was applied without asking
> and the console returned **zero bytes**. The reasoning was written down,
> repeated, and wrong in the one way that mattered: the change was inside the system
> the measurement came from. **Confidence in a mechanism is not a mandate.**

Detail: `BLUEPRINT/PROCESS/07_INTERRUPTIONS.md`, `08_RISK_AND_CONTAINMENT.md`.

---

## HANDOVER

The deliverable is not the dashboard. It is **the method, packaged**, so the next
one takes an afternoon instead of a month.

Produce:

- **the dashboard**, self-contained, verified, running
- **the restore point** — hashed, sampled, self-describing, provably restorable
- **the blueprint** — updated: what changed, what the next one should copy, what
  you learned that the method now says
- **the running list** — found, not done, with whose decision each item is

The test, always: **a stranger must be able to rebuild this from the folder
alone.** If they cannot, the handover is not finished — it is merely written.

---

## LOCATING THE BLUEPRINT

The full reference library lives in the folder recorded above as `blueprint`.
**If that path does not resolve — a different machine, a moved folder, a new
operator — do not proceed from memory and do not treat this skill as the whole
method.** Search for it, in this order:

1. the projects root, for `MINIMAX OPTIMUS CONTROL CENTER BLUEPRINT`
2. the parent of this skill file, for a `BLUEPRINT` folder
3. if neither exists, **say so before starting**, and work from the seven
   principles and the six stages in this file alone — which is enough to build
   correctly, but thinner than it should be

`reference_implementation` points at the worked example. It is useful to read and
**must not be modified** — it is a live system.

---

# SELF-CONTAINED REFERENCE

Everything below is here so the skill works **from this file alone**, with no
blueprint folder present. Where the folder exists it carries the full detail;
this is the part you must never have to look up.

---

## THE DEPENDENCIES DISCIPLINE

**Measured, not remembered.** A version you recall is a hope. A dependency you
have not executed is not a dependency.

Before planning, measure: `PowerShell`, `node`, `curl`, and whatever the subject
is made of. For every candidate number on screen, get **both its source and its
cost** — and *cost* is architecture-determining in a way that is easy to miss.

The question no version table can answer:

> **What is this tool pointed at, and does that target actually work?**

The reference implementation found an agent "installed and configured" that was
pointed at a 1.5-billion-parameter model — the only one present. Every version
check passed. The tool was installed. The configuration was correct. **The thing
it pointed at did not exist.** Verify the model, not the executable.

Also record what is **absent**. A dashboard that admits "not measurable from
here" is more useful than one that invents a number, and it buys permission to do
less now.

---

## THE DESIGN LANGUAGE

**Colour is reserved for meaning. Everything else is neutral.** If everything is
coloured, nothing is.

- **Dark surface by default** — long sessions, low light, the panels are the only
  light source. **A light theme is a peer, not an afterthought**: a console
  unreadable in daylight is unreadable.
- **One accent hue per entity**, chosen for distinguishability at small size in
  both themes. Adjacent tabs never share a hue.
- **`unknown` must be its own colour, distinct from `bad`.** If "we don't know"
  looks like "broken", the operator learns to distrust the whole panel. A
  dashboard that admits ignorance beats one that is confidently wrong.
- **Modular type scale**, ratio ≈1.25. Base ≈15px body. Anything an operator
  would copy — names, ports, paths, PIDs, durations, hashes — in **monospace**.
- **Tabular figures** for changing numbers, or columns shimmer on every poll.
- **Density is a feature**; whitespace is for the one thing that matters.
- **A card's title is a question it answers** — "What breaks if this dies", not
  "Status".

**The state vocabulary — six, and they must look different:**

| State | Means |
|---|---|
| OK | measured, within budget |
| WARN | answering, but late or degraded |
| BAD | not answering |
| STALE | data is old; the source may be fine |
| UNKNOWN | never measured, or not measurable here |
| CHECKING | in flight — say how long |

**The spark:** form an opinion and show the reasoning. *"Answered late, not
down — restarting it will not help, it is healthy and slow."* The cost is one
rule: **never form an opinion the human cannot re-derive from the screen.**

---

## THE ANTI-PATTERNS, CONDENSED

Every one of these produced **green output while being wrong.**

| Pattern | The sentence that convicts it |
|---|---|
| a silent hang inside a call nobody timed | no exception, no log — because nothing was throwing |
| `null` treated as a number | `Math.min.apply(null, [null,57,57])` is `0` |
| truthiness on an enumeration property | `LinkType` is truthy for a hard link too; 76 files vanished |
| a helper name that resolves to a system binary | `Clip` ran `clip.exe`; every diagnostic was discarded |
| an off-by-one index read as a different field | 13 tabs, 13 identical icons — the fallback was *reasonable* |
| a DOM node captured across a re-render | the answer went to a node the poll had already replaced |
| a computed insert offset into syntax | the page parsed to nothing, answered 200, logged nothing |
| a failure path that reports the wrong thing | it described a temp file that had been deleted |
| a `$null` for every kind of failure | *down* and *slow* rendered identically; the operator restarts what works |
| a local `let` shadowing a global you call | `let history = []` makes `history.replaceState` undefined |
| a once-ever latch for a recurring requirement | "whenever I start my browser" ≠ "the first time ever" |
| state set in only one of two branches | a cold load showed no active tab until the second render |
| a reaper that reaps the node, not the tree | 0 s CPU on a process four hours old |
| a background job blocking on an inherited pipe | 0 s CPU where a running command takes 0.22 s |
| a proven diagnosis treated as a mandate | the console returned **zero bytes** |

**Before you believe any check — yours or mine:**

1. *Could this pass if the system were healthy?*
2. *Could it pass if the defect were fixed?*
3. *Am I measuring the object, or a neighbour of it?*

And the countermeasure that works: **change one thing about the instrument and
see whether the answer moves.** If it does not, the instrument is not looking at
the thing.

---

## THE TEMPLATE INVARIANTS

The proven code is in the blueprint's `TEMPLATES/`. These are the lines that must
survive adaptation, each one a place where a plausible edit reintroduces a real
defect.

**Collector**
- Every external call has **its own** timeout.
- Trace mode from the first line: `Trace 'before <section>'` behind an env var.
- A failure result carries **which** failure, never just that one happened.
- Cast every number. `$null` in arithmetic becomes `0`.

**Server**
- State writes are **atomic** — temp file, then rename over. Never in place.
- A background job spawning a child **must redirect stdin**, or the whole tree
  inherits the remoting pipe and deadlocks with no error at all.
- A request path **cannot start a measurement at all** — read-only
  (`Get-StateJson -MaxAgeSec -1`), the refresh worker owns timing. There is no
  "if it must" branch: a bigger budget is the reverted fix, and it starved the
  worker into serving zero bytes.
- Actions resolve an **identifier** to a command server-side. The page never
  sends a command. Output is capped. Bind loopback only.

**Page**
- `render()` is **pure**: read state, return HTML. It never mutates.
- Anything the operator types, reads or waits for lives in a **variable**, never
  in a node a poll can replace.
- Every value into `innerHTML` goes through `esc()` — and `esc()` must cover the
  character that appears in **your** attribute context.
- `history.replaceState` (or `window.` qualified), never assignment.
- Entrance animations fire **once**, not on every re-render.

**Supervisor**
- Three consecutive failures before acting. One timeout is a slow system, not a
  dead one.
- A grace period after every start, long enough for a first measurement.
- It **restarts**; it never **repairs**.
- Verify liveness by evidence — a port, a probe — not by "I killed it".

**The freeze, and how it was actually fixed.** The reference `server.ps1` served
`/api/state` with a cache threshold smaller than one collect, so once per cycle a
request paid a full ~20 s collect on a single-threaded listener. Widening the
threshold was tried, reverted, and **starved the refresh worker into serving a
zero-byte body** — the threshold was never the disease, the shared thread was.

The fix is architectural, and it is one line at the call site plus one guard in
the function:

```powershell
# the contract, in the function — three modes, not two
if ((Test-Path $script:StateFile) -and $MaxAgeSec -ne 0) {
  if ($MaxAgeSec -lt 0 -or $age -lt $MaxAgeSec) { return ... }   # -1 = never collect
}

# every request path
$json = Get-StateJson -MaxAgeSec -1
```

`-1` read-only · `0` force a collect · `> 0` max-age. A dead refresher is still
caught one level up: the supervisor fails the server when the served state passes
`MaxStateAgeSec` and restarts it, and the page shows `stale` at 60 s / `down` at
180 s. Measured after the fix with the state file backdated past the old trigger:
5 requests at 200 s age → max 182 ms; 8 concurrent → max 350 ms; zero non-200.

**Read the function on disk before you plan a change to it.** The obvious
one-line fix here was to pass `-1` and call it done. Under the *existing* `-gt 0`
guard that does not mean "never too old to serve" — it falls through to the
inline collect, which would have made the freeze **unconditional and permanent**.
A new mode must be added where it is tested.

**And the freeze did not end there.** With the state path read-only, a
concurrent probe during a question still got **no response at all** — the
subprocess owned the listener. The general shape, which is what actually
transfers:

| Instead of | Do |
|---|---|
| running the work in the request | write a file, return a job id, poll for the result |
| piping data into a child of `Start-Job` | write it to a file and use `-RedirectStandardInput` (postmortem #17) |
| `Get-NetTCPConnection` on a request path | one `GetIPGlobalProperties().GetActiveTcpListeners()` call — 25.5 s → 0.014 s |
| a test stub answering the old shape | make it speak the new protocol, or it passes while proving nothing |

**Three layers of test, and the third is the one that finds things.**

| Layer | Proves | Cannot prove |
|---|---|---|
| file-level (`node --check`, parse checks) | the artefact parses | anything ran at all |
| in-page behavioural (stub a dependency, call the real handler) | a handler reaches a **connected** node | that the system survives abuse |
| **health harness** (fault injection + streak) | the system fails CLEANLY and consistently | — |

The third layer has two rules that are not optional:

1. **It plants its own faults first and refuses to certify if it cannot catch
   them.** A suite that has never reported a failure has not been shown to be
   *able* to, and a green run from such a suite is not evidence. Include a
   **positive control** too — a deliberately correct expectation that must NOT be
   flagged — or a runner that marks everything failed would pass every negative
   control and certify a broken system.
2. **It requires N consecutive clean runs, not one.** One clean run is a sample.

Run fault injection against the real thing: a corrupt job marker, a malformed
body, an unknown id, a job that will never finish. Each must produce a *clean,
reported* failure — never a hang, never a 500 carrying a raw exception, never a
fabricated success.

**Assert the shape, not just the status code.** A corrupt-file check that only
asserts `200` passes while the server echoes unparseable bytes under a JSON
content-type, and the client then reports "lost contact" — a symptom describing
the wrong thing. `200` was the wrong assertion; `200 AND parses AND says error`
is the right one.

**Exercise the failure path on purpose, while you can still fix it safely.** The
timeout branch that never fired was broken in three separate ways and had been
reviewed, commented, and shipped.

**Watch for fixtures that are secretly PASSING.** A "wrong type" control written
as `'7' -eq 7` is *true* in PowerShell, because `-eq` coerces. It looked like a
planted fault, it was a correct assertion, and the self-check reported it as a
defect. **A planted fault that is actually a pass is the most dangerous shape a
test defect can take** — it inverts the meaning of the whole suite.

**The concrete shape, which you should copy rather than re-invent:**

```powershell
# server.ps1 - one job, a marker written BEFORE it starts, a hard ceiling
$id = [guid]::NewGuid().ToString('N').Substring(0, 12)
[IO.File]::WriteAllText("$dir\$id.json", '{"state":"running"}', ...)
Start-Job -ArgumentList ... -ScriptBlock {
  $p = Start-Process -FilePath $py -ArgumentList "`"$client`"", 'ask', '-', ... `
    -RedirectStandardInput $promptFile -RedirectStandardOutput $raw -PassThru
  if (-not $p.WaitForExit(180000)) { $p.Kill(); $res = @{ state='error' } }
  # atomic write, or a poll reads half a result
  Move-Item "$out.$PID.tmp" $out -Force
}
return $id
```

```powershell
# the POST answers in milliseconds; the GET is a file read
POST /api/ask          -> @{ ok=$true; job=$id; state='running' }
GET  /api/ask/<id>     -> the job's @{state='running'|'done'|'error'}
```

```javascript
// the page owns the waiting, and never captures a node across an await
const done = await pollAsk(j.job);          // first poll immediate, then 1 s
aiAnswer = (done.state === 'done') ? done.answer : ('ERROR: ' + done.error);
```

**A request that returns "still working" is a feature, not a compromise.** The page must show a pending state distinct from "nothing asked yet", and a stale job must be reported as abandoned rather than polled until a cap.

The same discipline applies to **every** operator-triggered command, not just the
analyst. In the reference this is `Start-ActionJob` + `Invoke-BoundedCommand`
alongside `Start-AskJob`; both dot-source one shared file, `run-bounded.ps1`,
because a scriptblock cannot cross into a bounded child process. That is also
why the action table holds **command strings, not scriptblocks** — the timeout
cannot exist otherwise. A dashboard where one button can hold the single
listener hostage is an outage, and an action that times out *silently* is worse
than one that never returns: it looks like it worked.

**A cap is not the same as a fix.** Running the action inline behind a 120 s
ceiling still froze a concurrent reader for **10 030 ms** — the cap bounded the
freeze, it did not remove it. Measured on the reference: after going async, 57
concurrent probes during a 12 s `doctor` returned **0 non-200**, worst 3985 ms,
against a 274 ms idle baseline. The residual is scheduling contention from a
legitimately heavy command, not a blocked listener. Measure the baseline before
blaming the listener for a spike.

---

# THE STANDARD

Every OPTIMUS dashboard, whatever its subject:

- tells the truth, and **distinguishes down from slow from late from stale from
  unknown**
- runs with **zero external resources**, and a test asserts it
- **verifies itself from inside**, running real handlers against stubbed
  dependencies
- **survives a reboot** and recovers from a kill with no human present
- costs the system it observes a stated, measured, small amount
- forms opinions it can back, and shows its reasoning
- is built by this method, in this order, with R0 before code and questions
  before both

Full reference library: `MINIMAX OPTIMUS CONTROL CENTER BLUEPRINT\`
