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
license: proprietary
metadata:
  blueprint: C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\MINIMAX OPTIMUS CONTROL CENTER BLUEPRINT
  reference_implementation: C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\90_CONTROL_CENTER
  restore_point: C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\FULL_BACKUP_2026-10-04_QUARANTINE
---

# MINIMAX OPTIMUS DASHBOARD

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
