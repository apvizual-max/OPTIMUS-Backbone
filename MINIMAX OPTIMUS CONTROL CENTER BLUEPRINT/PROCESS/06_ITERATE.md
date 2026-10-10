# 06 — STAGE 6: ITERATE

**You are not done when it works. You are done when you genuinely cannot find
another thing wrong — and that takes deliberate, structured looking, not another
hour of the same tests.**

The worked example passed 7/7 and had a five-hour outage, a feature that had never
worked, and a monitor that could not describe its own failures. It was green and
broken at the same time, for hours. The defects were found anyway — by pressing
buttons nobody had pressed, asking questions nobody had asked, and looking at
things everybody had assumed.

---

## The loop

```
        ┌──────────────────────────────────────────┐
        │  it works. tests pass. it is green.       │
        └──────────────────┬───────────────────────┘
                           ▼
        look for something wrong. deliberately.
                           │
        ┌──────────────────┴───────────────────────┐
        │  found it        │  cannot find it        │
        ▼                  ▼                       │
   fix + verify        one more pass, from a        │
        │              DIFFERENT angle              │
        └──────────────────┬───────────────────────┘
                           ▼
              anything left on the list?
```

---

## Six passes, each from a different angle

Running the same checks again finds nothing. **Change what you are looking at.**

**Pass 1 — press everything.** Every tab, every button, every shortcut, every
row. Read what appears. The worked example's most valuable find came from pressing
`Ask` on a panel it had looked at a hundred times.

**Pass 2 — the shape sweep.** Take the defect you most recently fixed and grep for
its *shape* everywhere, not its symptom. One bug was "`getElementById` captured
before an `await`". The sweep found a second instance in the same function, and
clean elsewhere — nine of ten sites were already correct. *A fix is not done until
you have found the other implementations of the pattern.*

**Pass 3 — make it lie.** A check that has never failed is untested. Deliberately
break the thing in a way you can undo, and confirm each layer goes red: the
collector, the file, the page, the supervisor, the self-test. Anything that stays
green is not a check.

**Pass 4 — the numbers.** Every figure on screen, traced to its source. Is it
still true? Does it have a denominator? Is it rounded into a lie? The worked
example found its own container count stated as 56 in three files while the system
had 58 — *six separate times* the same class of error appeared in a different file.

**Pass 5 — the cost.** What does the dashboard consume? Processes spawned, bytes
copied, memory held, requests made. Then ask whether a *maintenance action you take
often* is itself a burden. Copying 30 MB on every change measurably stalled the very
console it was protecting.

**Pass 6 — the handover.** Give it to someone with no context. Can they tell what
is broken at 3 a.m.? This is the same test as the rebuild docs, run early.

---

## When to stop

Stop when **two consecutive passes from different angles find nothing new.**

Not one pass. One pass finds something most of the time; two in a row is a signal
that the surface has been swept. And keep the list of things you noticed but did
not do — that list is the honest handover, and it is what the next person reads
first.

---

## The standing rule

> **Look until the goal is absolutely satisfied. Do not stop until it is. That is
> the entire point.**

Not because more testing is always better, but because the failure mode of this
work is *confident and early*. The most dangerous state is not "broken". It is
"green, and believed finished".
