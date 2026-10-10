# LOGIC TREE

**What the dashboard concludes, from what it measures.** If a conclusion is not
reachable from a measurement, it is a guess, and it does not belong here.

Every leaf is a fact someone can re-derive from the screen. Every branch is a rule
you can name. That is the whole discipline.

---

```
MEASURED
  port listening?          file mtime          process alive?
  HTTP status              value + timestamp   config present
  probe elapsed ms         count of X         registry says Y
  response body            lock file           process start time
        │
        ▼
OBSERVED  ── one fact, one verb, no adjectives
  "8801 /doctor/detailed answered in 8029 ms"
  "index.html parses; every container is counted; the state carries a timestamp"
        │
        ▼
CLASSIFIED ── which failure?  (this is where dashboards lose honesty)
  answered within budget      → OK
  answered past the budget    → LATE      ← distinct from BAD
  not answered at all         → DOWN
  not measured here           → UNKNOWN   ← distinct from BAD
  data exists but is old      → STALE
  measurement in flight       → CHECKING
        │
        ▼
JUDGED  ── only from classified facts, with the numbers attached
  "up, but slower than its budget — and slower than the thing that reads it"
  "down, and nobody restarts it, so it stays down"
  "configured, but the file changed after the process started — stale build"
        │
        ▼
RECOMMENDED ── and, critically, what NOT to do
  "restarting it will not help — it is healthy and slow"
        │
        ▼
SHOWN  ── the human reads it in one pass, bad thing first
```

---

## The classification layer is where honesty is won or lost

A dashboard that returns one failure value — `null`, `false`, `error` — has
collapsed six states into one. Every one of those six has a different remedy, and
the operator is left guessing.

**The rule:** *a failure result must carry which failure, never just that it
failed.* This is a single design decision with more effect on trustworthiness than
any visual choice in the whole system.

| collapsed into "unknown" | actually | the operator should |
|---|---|---|
| unknown | healthy but late | nothing, or raise the budget |
| unknown | down | restart it |
| unknown | unmeasurable here | fix the measurement, not the service |
| unknown | stale | wait, or check the refresher |
| unknown | never loaded | look for a wiring fault |
| unknown | failed validation | investigate the config |

---

## Derivations worth having

Rules that no single measurement gives you, and that a person would otherwise have
to compute at 3 a.m.

**Blast radius.** *If X dies, what else stops?* Follow the supervision edges from
the measurement's own registry. The answer is not in any status field; it is in the
graph.

**Restartability.** *Will this come back?* A process whose parent is gone and
whose owner is "nothing" stays dead. Say so, on the row.

**Truthfulness of a process.** *Is the running code the code on disk?* Compare
process start time to source mtime. A process older than its own source is
executing something that no longer exists. **This catches a whole class of
confident wrongness that no functional test can.**

**Budget compliance.** *Is the measurement inside its own budget?* The collector
that takes 22 s on a 20 s cycle is not slow — it is saturated, and it will feel
like flakiness to the operator forever.

**Honesty of a page.** *Is this thing actually alive?* Parse its script in-page.
A page that does not parse still returns 200, still serves perfect data, and still
logs nothing, because no statement ever ran.

---

## The rule that governs the whole tree

> **Every conclusion must be traceable to a measurement, and every measurement must
> be re-derivable by the human from the screen.**

The moment a branch ends in something the human cannot check, it stops being
information and becomes a rumour — and a rumour on a dashboard at 3 a.m. is worse
than nothing, because it spends trust.
