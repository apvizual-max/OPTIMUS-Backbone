# ANTI-PATTERNS

Eighteen real defects from the worked example. Every one produced **green output
while being wrong.** The right column is the sentence that convicts it — because a
pattern you cannot state is a pattern you will not recognise the second time.

---

## The index

| # | Pattern | Caught by |
|---|---|---|
| 1 | A silent hang inside a call nobody timed | a trace marker before each section |
| 2 | A truthiness test on an enumeration property | a file census the script never ran |
| 3 | A helper name that resolves to a system binary | reading stderr nobody read |
| 4 | An off-by-one index read as a different field | a screenshot with 13 identical icons |
| 5 | A captured DOM node across a re-render | a timestamped timeline |
| 6 | `null` treated as a number | reading the axis label |
| 7 | A scalar where an array was promised | the tab failing to render |
| 8 | A computed insert offset into a syntax structure | a self-test reporting 1 failure of 7 |
| 9 | A failure path that reports the wrong thing | three correct detections nobody could act on |
| 10 | A local `let` shadowing a global API | **nothing** — the test read the shadow |
| 11 | A once-ever latch for a recurring requirement | a requirement that had never once run |
| 12 | State set in only one of two branches | clicking tabs and reading `button.on` |
| 13 | A failure value that discards *which* failure | a healthy bridge rendered as an outage |
| 14 | The instrument participating in the failure | a memory report made while the tool caused it |
| 15 | A reaper that reaps the node, not the tree | 0 s CPU on a process four hours old |
| 16 | The harness mistaken for the finding | changing the instrument and nothing moving |
| 17 | A job blocking on a pipe it inherited | 0 s CPU where a running command takes 0.22 s |
| 18 | A proven diagnosis treated as a mandate | the console returning zero bytes |

---

## The families, and what unifies them

### Family A — the measurement was not a measurement

**#1** `ConvertTo-Json` never returned, on a tree shaped so that a reflection path
did not terminate. Everything before it finished in 15.6 s; the hang was the one
statement nobody timed. No exception, no log line — **because nothing was throwing.**

**#6** `Math.min.apply(null, [null, 57, 57, 57, 57])` is `0`, not 57. A perfect
flat series rendered as `min 0 · now 57 · ▲ +57`.

**#7** PowerShell collapses a one-element array to a scalar through JSON. A panel
rendering exactly one incident threw.

> *A single bad sample poisons every series derived from it.* Filter at the
> boundary, not at the point of use.

### Family B — the code did something else, correctly

**#2** `if ($item.LinkType)` is true for a **hard link** as well as a junction. 76
real files were dropped, and the manifest recorded them as "recreated as a
junction" — an omission *and* a false record, which is worse.

**#3** `Clip $c.detail` resolved to `clip.exe`, the Windows clipboard utility. Every
diagnostic string in the handover briefing was silently discarded.

> *A wrong name is not a typo. It is a different program, running successfully.*

**#4** A tuple index read as the icon key when it held the description. All 13 tabs
rendered the same glyph, because the fallback was a *reasonable* default.
**A loud fallback would have caught it in one load.**

### Family C — correct code, wrong lifetime

**#5** An output element captured by reference, then a 5 s poll rebuilt the view.
Output written into a detached node at 16 poll cycles.

**#8** `$lines.Insert($swap - 3 + $k, …)` — a computed offset that landed *between*
a call and its argument list. The page rendered nothing, still returned 200, and
still logged nothing, because no statement ever ran.

**#12** Active-tab state was set in the `else` of the create branch, so a cold load
appended 15 buttons with **no** active one until the second render — up to 20 s
later, when a collect was in flight.

### Family D — the report could not describe its own failure

**#9** In PowerShell 5.1, a native command writing to stderr becomes a
*terminating* error under `$ErrorActionPreference='Stop'`. The page-integrity
check's sentence naming the fault was **unreachable**; it reported an exception
about a temp file that had been deleted two lines earlier.

**#13** A probe returning `$null` for every kind of failure, so a bridge that was
**down** and a bridge that was **healthy but answering 8.5 s** rendered
identically. The operator's instinct is then to restart something that is working.

> *A failure path that discards the information distinguishing causes makes every
> cause look the same.*

### Family E — the instrument was part of the system

**#10** A script-scope `let history = []` shadowed `window.history`. The call threw on
every render and fell through to a path that pushed a history entry per click. **My
test read `history.length` — the shadow — and passed.**

**#11** A once-per-process latch plus a startup-time guard. The requirement was
"as soon as I start my browser"; a flag that never resets expresses "the first time
ever". At every logon a browser is already open, so the guard suppressed it
permanently. **The requirement had never once run.**

**#14** The tool used to verify held a headless browser open per session and never
exited it. Eight had accumulated over 15 hours, ~3 GB — while I was investigating
memory pressure the instrument was causing it.

**#15** The reaper searched for `node.exe`. Correct for the question asked;
structurally blind to the `chrome-headless-shell` children holding 3 GB. **A filter
is a policy decision wearing the costume of an optimisation.**

### Family F — the meta-family

**#16** Four separate times, the *test* was the thing that was wrong: a pattern that
could not see multi-declarator `let`; a count-sweep that missed "14 real bugs"; a
2.5-second wait that declared a working feature broken; a keypress delivered to
the wrong target. Each looked like a finding. None was.

**#17** Five hours, 13 times an hour, logging `collector exceeded 240s`. Read
literally: the collector is slow. It was **deadlocked** on an inherited pipe. Two
theories died on measurement first — a blocked stderr pipe (0 bytes written) and
"it is just slow now" (21.4 s, sections identical to that morning).

**#18** A correlation so clean it felt unarguable, a one-character fix, applied
without asking. **34 stalls of 34 requests. `/api/state` returned zero bytes.**
The reasoning was right about the mechanism and wrong about the world, because the
change was *inside* the system the measurement came from.

> *A measurement tells you the mechanism. It cannot tell you the change is safe.*

---

## The three questions

Before you believe any of these — your checks, your metrics, your instruments:

1. *Could this produce the same answer if the system were healthy?*
2. *Could it produce the same answer if the defect were fixed?*
3. *Am I measuring the object, or a neighbour of it?*

And the countermeasure that actually works: **change one thing about the instrument
and see whether the answer moves.** If it does not, the instrument is not looking
at the thing.
