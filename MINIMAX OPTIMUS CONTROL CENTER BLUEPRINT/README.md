# MINIMAX OPTIMUS CONTROL CENTER — BLUEPRINT

**This is the source of truth for how a MiniMax OPTIMUS dashboard is designed, built,
verified, and handed over.** The Control Center at `http://127.0.0.1:8900/` was the
first one. It is the worked example; this folder is the method.

Nothing here is a description of *that* dashboard's functions. It is the **concept
that produced them**, packaged so the next one can be built by starting from a
single prompt and following the same staged path — with the same accuracy,
thoroughness, and strategy — and arriving somewhere just as good for a completely
different subject.

---

## What this is for

A dashboard is not a UI. It is a **human–machine interface over a running system**,
and the hard part is not the layout. It is that the thing is telling the truth
about something it did not build, did not control, and cannot test — while it
re-renders itself every few seconds in front of a human who will act on it.

Everything in this blueprint derives from that one sentence.

---

## Read in this order

| # | File | What it gives you |
|---|---|---|
| 00 | [`PRINCIPLES.md`](PRINCIPLES.md) | The seven rules. If you break one, you get one of the anti-patterns. |
| — | [`DEPENDENCIES.md`](DEPENDENCIES.md) | What this needs, measured. Start here before you plan. |
| 01 | [`PROCESS\01_UNDERSTAND.md`](PROCESS/01_UNDERSTAND.md) | **Stage 1** — the questions to ask before writing anything. |
| 02 | [`PROCESS\02_RESEARCH.md`](PROCESS/02_RESEARCH.md) | **Stage 2** — mining a reference, and when the reference is a liability. |
| 03 | [`PROCESS\03_PLAN_AND_R0.md`](PROCESS/03_PLAN_AND_R0.md) | **Stage 3** — the plan, the theoretical test, dependency proof, gap check, R0. |
| 04 | [`PROCESS\04_BUILD.md`](PROCESS/04_BUILD.md) | **Stage 4** — the build, and the order that avoids rework. |
| 05 | [`PROCESS\05_VERIFY.md`](PROCESS/05_VERIFY.md) | **Stage 5** — proving it works. The most-skipped stage in the world. |
| 06 | [`PROCESS\06_ITERATE.md`](PROCESS/06_ITERATE.md) | **Stage 6** — "look until satisfied". Where the real quality comes from. |
| 07 | [`PROCESS\07_INTERRUPTIONS.md`](PROCESS/07_INTERRUPTIONS.md) | The **only three** reasons to stop mid-build. |
| 08 | [`PROCESS\08_RISK_AND_CONTAINMENT.md`](PROCESS/08_RISK_AND_CONTAINMENT.md) | Backups, quarantine, containment. When you delegate risk. |
| 09 | [`CHECKLIST.md`](CHECKLIST.md) | Definition of done. Check it or it is not done. |

Then the reference library:

| Folder | What is in it |
|---|---|
| [`DESIGN/`](DESIGN/) | Architecture, design language, component catalogue, interaction model. |
| [`TREES/`](TREES/) | Logic, process, strategic, **procedure** trees. |
| [`PATTERNS/`](PATTERNS/) | Anti-patterns — 18 real ones, each with the measurement that convicted it. |
| [`TEMPLATES/`](TEMPLATES/) | Working starting code: page, server, collector, supervisor, self-test. |
| [`SKILLS/`](SKILLS/) | The `minimax-optimus-dashboard` skill that runs this whole thing. |

---

## The shape of the thing, in one page

```
        ┌─────────────────────────────────────────────┐
        │  the human asks for a dashboard              │
        └───────────────────┬─────────────────────────┘
                            ▼
   1 UNDERSTAND ── questions, until nothing is unknown
                            ▼
   2 RESEARCH ──── mine a reference, inventory the real system
                            ▼
   3 PLAN + R0 ─── the plan, tested on paper, deps proven, gaps named
                   ══ APPROVED BY THE HUMAN ══
                            ▼
   4 BUILD ─────── collector → server → page → supervisor, in that order
                            ▼
   5 VERIFY ────── does it tell the truth? does the human SEE it?
                            ▼
   6 ITERATE ───── look again. and again. until there is nothing left
                            ▼
        ┌─────────────────────────────────────────────┐
        │  quarantine + blueprint + skill captured     │
        └─────────────────────────────────────────────┘
```

**During stage 4, stop for exactly three reasons.** They are in
[`07_INTERRUPTIONS.md`](PROCESS/07_INTERRUPTIONS.md) and there are no others.
"I noticed something else" is not one of them; write it down and carry it.

---

## What the worked example actually produced

The Control Center was 15 tabs, one HTML file, three PowerShell files, and one
scheduled task. It found and fixed **thirteen real defects**, of which three would
have been invisible to any amount of green test output:

- The **AI Analyst had never worked, not once.** The API was perfect; the answer was
  written into a DOM node that a 5-second poll had already detached. It looked
  healthy in every screenshot.
- The **supervisor's own page check could not say why it had caught a fault** — a
  PowerShell 5.1 behaviour turned a syntax error into an exception about a deleted
  temp file.
- A **five-hour silent degradation** where a background job deadlocked on a pipe it
  inherited, stranding 130 processes, while the log cheerfully said *"collector
  too slow"* 13 times an hour.

All three are in [`PATTERNS/ANTI_PATTERNS.md`](PATTERNS/ANTI_PATTERNS.md), and all
three were found by the same move: **stop trusting the layer above the thing, and
look at the thing.**

That move is the skill.

---

## The one-line test for any decision in here

> *If this dashboard is wrong, will it say so — loudly, specifically, and without
> making me go and find out?*

If the answer is no, the decision is not finished. Every principle, tree, template
and anti-pattern below exists to serve that one question.
