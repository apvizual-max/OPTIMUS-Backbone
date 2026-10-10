# 03 — STAGE 3: PLAN, TEST IT ON PAPER, PROVE THE DEPENDENCIES, THEN R0

**Nothing is built until the human approves the plan.** The plan is not a
description; it is a set of claims that must each survive an attempt to break it
before it is worth anybody's signature.

---

## 3A — Write the plan

Four parts. Keep it short enough that a human actually reads it.

**1. The architecture, in one paragraph, with the refresh budget.**
Not "we will use polling" — *"the collector costs 22 s, so the cache serves for 20 s
and a stale request pays the difference."* The numbers are the plan. If you do not
have the numbers, you are not ready to plan; go back to stage 2.

**2. Build order, chosen so that nothing is built twice.**

The worked example's order, and the reason for it:

```
collector  →  server  →  page  →  supervisor  →  self-test
   1            2         3          4              5
```

- **Collector first.** It is the only piece that knows the system. Everything else
  renders what it says. Build it alone first; you can run it in a terminal and read
  the output.
- **Server second**, serving a static file. Now you can look at data in a browser.
- **Page third**, against the live endpoint.
- **Supervisor fourth.** A supervisor for something not yet stable is a supervisor
  that restarts you mid-edit.
- **Self-test last**, because a test written before the thing exists tests your
  imagination.

Reversing this — page first, most common — produces a beautiful mock wired to
nothing, and a rewrite when the real data disagrees with the assumptions.

**3. The design language**, decided now, not discovered later: density, palette,
type scale, how a warning looks, how a dead thing looks. Decide these against the
reference and the human's stated taste, because retrofitting a visual system is
pure loss.

**4. The definition of done**, in the human's words. If you cannot write it, the
plan is not finished.

---

## 3B — Test it theoretically

Before anyone signs, try to break the plan on paper. Walk these five failure
questions and answer each one specifically:

**1. What is the slowest thing in the design, and what happens when it is slow?**
Take the worst measurement cost and multiply it by the refresh interval. If the
product is greater than the interval, the design has a queue — and you must decide
now whether that queue is acceptable, or whether the slow thing gets its own
refresh cadence. *(The worked example's 22 s collect against a 20 s cycle is
exactly this, and it produced a visible stall that is still open.)*

**2. What happens if the data source disappears mid-render?**
A poll that fails must not blank the screen. The last good reading must survive,
clearly marked as last-good. Decide now what the operator sees: stale data, or
nothing. Stale data wins, every time, provided it says how old it is.

**3. What happens on restart — machine, service, page?**
A process reads its source once. If the source can change, the running copy is not
the source, and the dashboard is lying by omission. **Decide now whether the design
detects that.** *(This is the reference dashboard's "build currency" check, and the
worked example hit the exact problem twice before noticing it existed.)*

**4. What is the failure mode of the failure handler?**
If the thing that reports errors is itself broken, what does the operator see?
Trace it: error → handler → display. If any link fails silently, the design has a
hole. The worked example had exactly this — the page-integrity check could detect a
broken page but could not describe what was wrong, so it reported an exception
about a temporary file that had already been deleted.

**5. What does this design cost the system it observes?**
Polls, copies, spawned processes, memory. Put a number on it. A dashboard that
degrades the machine is a dashboard with a countdown.

---

## 3C — Verify every dependency

**Every external thing the plan relies on must be proven present, with a version,
by running it.** Not by assuming, not by "it was there yesterday."

For each dependency, record: what it is, the version measured, what breaks without
it, and what happens if it changes underneath you.

In the worked example this stage would have caught, on paper and in minutes:

- The collector's cost was assumed fast. Measured: **8.5 s** for one health check.
- A tool that was assumed installed. Measured: **not installed** — the agent that
  "didn't work" was pointed at a 1.5-billion-parameter model, the only one present.
- A bridge assumed healthy. Measured: answering, but **past its own timeout**.
- Fonts assumed available. Verified: **zero external resources**, all glyphs local.

**A dependency you have not executed is a hope, not a dependency.**

---

## 3D — Check for errors and gaps

Two lists, both written down, both shown to the human.

**Known risks, with what you will do about each.** Not "there may be risks" —
"*if the collector takes longer than 240 s the refresher kills it and the last good
state is retained; this has happened 0 times since the deadlock fix and 72 times
before it.*"

**Known gaps, stated as gaps.** Things you *cannot* show, and why. A dashboard that
admits "this is not measurable from here" is more useful than one that invents a
number, and it buys permission to do less now.

And the one everybody skips:

> **What did I plan to build and not write down?**

---

## 3E — R0

**R0 is a gate, not a formality.** Present the plan with:

- the architecture paragraph, with numbers,
- the build order and why,
- the five theoretical failure answers, specifically,
- the dependency table with measured versions,
- the risk list and the gap list,
- the definition of done.

Then **stop and wait.** Do not start building "while you review". If he answers with
changes, the plan is revised and R0 is re-taken.

**R0 covers the plan, not the system.** Once approved, you still do not change
behaviour of anything already running without asking — that is a separate decision
each time. See [`07_INTERRUPTIONS.md`](07_INTERRUPTIONS.md).

---

## Exit criteria

- [ ] Plan is short enough to have been read.
- [ ] Build order argued from rework cost, not convenience.
- [ ] All five theoretical failure questions answered specifically.
- [ ] Every dependency executed and version recorded.
- [ ] Risks and gaps written down and shown.
- [ ] Human approved. **Then, only then, build.**
