# 00 — PRINCIPLES

Seven rules. Everything else in this blueprint is a consequence of these, and every
anti-pattern in `../PATTERNS/ANTI_PATTERNS.md` is a breach of one of them.

---

## 1 — The dashboard is a witness, not an advocate

It did not build the system. It did not choose the thresholds. It cannot fix
anything at 3 a.m. Its only power is to be **right in front of a human who will act
on it.**

So the whole craft is one question:

> **If this is wrong, does it say so — loudly, specifically, and without making me
> go and find out?**

Every design decision is judged by that. A beautiful panel that quietly shows
`unknown` for a service that is answering is worse than no panel, because it spends
trust. The worked example shipped a bridge panel reading `health=unknown · 0/0/0`
for **five hours** while the bridge was up, healthy, and returning *9 ok / 3 warn /
0 fail across 12 checks*. The data existed. The dashboard threw it away.

**Corollary: discarding information is a design decision, not an omission.** The
moment you drop a field, you have chosen what the operator cannot know.

---

## 2 — Measure the thing, not the layer above it

This is where nearly every real bug hides, and it is the single most expensive
lesson of the worked example.

The layer above the failure is almost always green. The API answered. The server
was healthy. Every tab rendered. The self-test passed **7/7** — while the AI
Analyst had never once produced a visible answer in its entire life.

**The rule:** when something does not work, go and look at *that thing*. Do not
accept the neighbour's report that it is fine.

- A page that renders is not a page that **works**.
- A green suite is evidence about the suite.
- A `200 OK` is evidence about the transport, and about nothing else — a
  syntactically broken page answers `200` forever and writes nothing to any log,
  because no statement ever ran.

Three of the thirteen defects in the worked example were invisible to every
existing check, and all three died the moment someone looked at the actual object.

---

## 3 — A check that cannot fail is worse than no check

A test that passes on broken code is worse than no test, because it is *trusted*.

Three ways that happens, all encountered for real:

- **It shares an identifier with the thing under test.** `history.length` was read
  where `window.history.length` was meant — the assertion passed, and the object it
  measured *was the defect*.
- **It cannot fail because render re-binds first.** Removing 85 event handlers left
  `controls are wired` reading "all bound", because the check calls `render()`,
  which re-attaches everything before it looks.
- **It is a structural check standing in for a behavioural one.** "Every control has
  a handler" cannot catch "the handler writes to a detached node" — which is exactly
  how the Analyst stayed broken.

**Before believing a check, ask three questions:**

1. *Could this produce the same answer if the system were healthy?* If yes, it
   cannot detect the fault.
2. *Could it produce the same answer if the fault were fixed?* If yes, it is
   decoration.
3. *Am I measuring the object, or a neighbour of it?*

And the countermeasure that actually works: **change one thing about the instrument
and see whether the answer moves.** If it does not, the instrument is not looking at
the thing.

---

## 4 — Separate what is broken from what is slow from what is late

The most expensive diagnostic error is a category error: reading one fault as
another because they look the same from outside.

The worked example's worst outage logged, 13 times an hour for five hours:

```
collector exceeded 240s - killed, previous state kept
```

Read literally, that says the collector is slow. It was not slow. **It was
deadlocked**, waiting on a pipe it had inherited — `0 s CPU for 226 seconds`, while
a *running* `git` command does that work in `0.22 s`. A blocked process and a slow
process look identical from outside. Only a CPU reading tells them apart.

The log message is also part of the defect: it asserted a *cause*, and the wording
kept the real cause invisible for five hours. **A log line is a claim about a cause,
and it is worth exactly as much as the evidence behind it.**

So the design requirement is: a failure result must carry **which** failure, never
just *that* it failed. `null` is not a report; it is the absence of one.

---

## 5 — The scope is the human's, not yours

You will find improvements. You will find them while building something else. You
will be certain about the mechanism.

**Certainty about a mechanism is not a mandate.**

The worked example broke its own console this way. A diagnosis was *proven* — a
correlation so clean it looked unarguable — a one-character fix was applied without
asking, and the result was 34 stalls out of 34 requests and a `/api/state` that
returned **zero bytes**. The reasoning had been written down, repeated, and was
still wrong in the one way that mattered: the change was *inside the system the
measurement was taken from*.

Three rules, learned the expensive way:

- **Do not change a running system's behaviour without authorisation.** Threshold,
  timeout, kill policy, task config. These are the human's decisions.
- **A fix proven in isolation is not proven safe.** Before changing anything that
  consumes a resource, ask **what else shares that resource.**
- **Report the improvement; let them decide.** One line. Then carry on with the
  work you were given.

Adding a *new* read-only capability is different from changing behaviour — but
that distinction is worth stating out loud rather than assumed.

---

## 6 — Make the machine tell on itself

A dashboard is a polling machine. It has no events, so everything it wants to know
has to be a number it can fetch, and everything it wants to say has to be a number
someone can read at a glance.

Design consequences that follow:

- **Freshness is a first-class fact.** The age of the data belongs on screen,
  always, next to the data. An unlabelled number is a rumour.
- **A count with no denominator is a lie.** `7 checks` is not information; `6 of 7
  answering` is.
- **Round numbers hide their own precision.** Prefer `8.03s of 8s budget` over
  "slow".
- **The blank, the loading, the stale, the dead and the slow are five different
  states.** Collapsing them is how a healthy service gets reported as an outage.
- **Write the failure down where it can be read.** A log the operator never sees
  is a log nobody wrote.

---

## 7 — Look until there is nothing left

Not "until it works". **Until there is nothing left to find.**

The worked example passed 7/7 at 18:00 and still had a five-hour outage, a feature
that had never worked, and a supervisor that could not describe its own failures.
It was "done" and green, and the defects were found anyway, by pressing buttons
nobody had pressed and asking questions nobody had asked.

The finish line is not a passing test. It is the moment you genuinely cannot find
another thing wrong — and that moment is rarer than it looks, and it is only
reachable by looking deliberately for it.

See [`PROCESS/06_ITERATE.md`](PROCESS/06_ITERATE.md) for how to look without
spending forever.

---

## The test that collapses all seven

> If this dashboard is wrong, will it say so — loudly, specifically, and without
> making me go and find out?

If the answer is no, the work is not finished. It does not matter how it looks.
