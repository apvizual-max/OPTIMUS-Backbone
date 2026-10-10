# 07 — STAGE 7: INTERRUPTIONS

**During the build you stop for exactly three reasons. There is no fourth.**

The temptation is to stop constantly — a suspicious log line, an idea, a
refactor, a small improvement you noticed. Each one feels responsible. Collectively
they destroy the plan, the build order, and the person's trust in the estimate.

**So: note it, carry it, keep building.** The list at the end is the deliverable,
not the interruption.

---

## The three reasons

### 1 — You need information only the human can provide

A key, a credential, a decision between two designs, a path only they know, a
password. Anything that cannot be derived by measuring the machine.

**Ask once, in a batch, with context.** Say what you tried, what you found, and
exactly what you need. A question with no context is an interruption; a question
that lets someone answer in one sentence is a non-interruption.

### 2 — You need a tool, a connector, or a different approach

The measurement you need has no interface. The library you need is not installed.
The approach you planned turns out to be impossible.

**State the constraint, not the distress.** "X has no readable interface; I can
synthesise it from Y and Z, or I can mark it as a known gap" is a decision someone
can make in five seconds. "I'm stuck" is not.

### 3 — You need to delegate risk

The change is destructive, irreversible, or affects something load-bearing that is
not yours to risk.

**Delegation means containment, not permission-seeking:**

```
  BACKUP        a verified copy of everything you are about to touch
  CONTAINMENT   a folder that isolates the blast radius if it goes wrong
  QUARANTINE    where the backups live, proven restorable
```

The worked example has all three, and the discipline paid for itself the first time
a change took the console down: the revert restored it, and the supervisor brought
it back unattended. See [`08_RISK_AND_CONTAINMENT.md`](08_RISK_AND_CONTAINMENT.md).

---

## What is NOT a reason

| The thought | What to do |
|---|---|
| "I noticed something else" | Write it in the list. Keep building. |
| "This would be a small improvement" | Write it in the list. Apply it in stage 6. |
| "The evidence is very strong" | Still ask. Certainty about a mechanism is not a mandate. |
| "It's only a threshold" | It is behaviour of a running system. Ask. |
| "I'll just try it, it's reversible" | If it were reversible you would not hesitate. |
| "The test is probably wrong" | Fix the test, do not bypass the question. |
| "Let me check one more thing first" | You will check forty more. Write it down. |

**The worked example's own cautionary tale**, in one line: a diagnosis was *proven*,
a one-character fix was applied without asking, and the console returned **zero
bytes**. The reasoning had been written down, repeated, and was wrong in the one
way that mattered — the change was *inside* the system the measurement came from.

---

## The running list

Keep one file, append-only, from the first minute of the build:

```markdown
## Found, not done — <date>
- [ ] <thing>  · why it matters · what it would cost · whose decision it is
```

At handover, this list becomes the first thing the next person reads. It is more
valuable than a paragraph of praise, because it is the only part of the work that
is definitely not finished.

**Never edit an entry out of it.** If something is resolved, strike it through and
say when. The list of things you were tempted to do is a record of your judgement,
and that judgement is what someone else needs to inherit.
