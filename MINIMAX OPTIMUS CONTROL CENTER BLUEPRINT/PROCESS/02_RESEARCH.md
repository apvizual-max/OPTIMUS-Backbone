# 02 — STAGE 2: RESEARCH

Research has two halves and both are frequently skipped. The visible half is
finding a reference. The invisible half is **inventorising the real system**, and
it is the half that decides whether the dashboard can be true at all.

---

## 2A — Mine the reference

You were pointed at something good. Take it seriously and take it apart.

### What to extract, in order

1. **Its navigation model.** One scroll page, or tabs? At what volume does each
   win? *(The worked example borrowed one property — zero external resources — and
   then diverged on structure, because the system it was observing had roughly
   **an order of magnitude more entities** than the reference's seven supervised
   ports. That ratio is the durable fact; the absolute count is not, and a
   document that quotes an absolute count is one that will be wrong by next
   month. **Prefer ratios and orders of magnitude in worked examples.**)*
2. **Its information hierarchy.** What does it put at the top, and why? The top of
   a dashboard is the answer to the most frequent question, not the most interesting
   one.
3. **Its vocabulary.** What does it call things, and does it ever use the system's
   own names? A dashboard that invents synonyms forces translation on every reader.
4. **Its states.** How does it distinguish empty, loading, stale, error, empty-because-
   broken, and empty-because-never-loaded? **Six or more distinct states in one
   panel is a good sign.** The worked example added *answered late* precisely because
   the reference's vocabulary did not have a word for it and the system needed one.
5. **Its live-update mechanism.** Polling interval, and what it does when the
   interval and the measurement cost disagree.
6. **What it does NOT have.** A reference shows you what the designer imagined. The
   gaps are where your specific system's problems live.

### The rule about references

> **Read it. Never write to it.** It is someone's live work. Every idea you take is
> an idea to *consider*, not a task to build.

And take the comparison **both ways.** Write down what the reference has that you
do not, *and what you have that it does not.* A one-directional gap list becomes a
scorecard and stops you seeing that you are already ahead somewhere.

---

## 2B — Inventorise the real system

This is where the work actually is. The page can only be as true as your knowledge
of the thing it describes.

### Walk it

- **Every process.** What starts it, what restarts it, what dies with it.
- **Every port.** What listens, who answers, who is supposed to answer and does not.
- **Every data source.** Files, sockets, CLIs, container APIs. For each: **how long
  does one read take?** Write the number down. It is architecture-determining.
- **Every failure you have already seen.** Check the logs. Logs are free evidence
  and everyone skips them.

### Measure, do not assume

For each candidate number, get a real figure. In the worked example:

| Thing | Assumed | Measured | Consequence |
|---|---|---|---|
| a health check | fast | **8.5 s** | 46% of a "fast" collect |
| `git log -1` | instant | 0.22 s | a 226 s process was *not* slow, it was blocked |
| a "background refresh" | works | deadlocked 5 h | a dashboard that only appeared alive |
| a system with "good models" | fine | one 1.5 B model | the real reason an agent "didn't work" |

**Every one of these changed the design.** None would have been found by reading
code.

### Find the load-bearing things

Identify what you are not allowed to break, and write it into the specification as
a prohibition. In the worked example this was a 31-container swarm that had already
been lost once to a prune. That prohibition shaped every command, every action
whitelist, and every reaper for the rest of the project.

### Look for the second-order costs

Ask: *what does the thing I am about to build cost the system it observes?*

The worked example's own answer, discovered the hard way:

- A background refresher that deadlocked silently for five hours.
- **130 stray `git` processes**, the oldest four hours old, all at 0% CPU — a
  feedback loop where more leaked processes made the machine slower, which made the
  deadlock likelier.
- ~10.9 GB of orphaned processes from tooling that was never told to clean up.
- A backup ritual that copied 30 MB and measurably **stalled the console it was
  protecting**.

A dashboard is an instrument. Instruments are not free, and the operator must be
told what the instrument costs.

---

## Exit criteria

- [ ] Reference taken apart: navigation, hierarchy, vocabulary, states, refresh, gaps — **both directions**.
- [ ] Every displayable number has a measured source **and a measured cost**.
- [ ] Load-bearing things named, and the prohibition written down.
- [ ] Second-order costs identified, including the cost of the dashboard itself.
- [ ] New questions this stage raised have been asked. **Then go back to stage 1.**

---

## The question-iteration loop

Research reliably produces new questions. That is the design working, not failing.

```
stage 1 questions → research → NEW questions → answer them → re-research
                    ↑                                              │
                    └──────────────────────────────────────────────┘
```

Two passes is common. Three means the system is more interesting than you thought,
which is usually good. Stop when a full pass produces no new questions — not when
you run out of patience.
