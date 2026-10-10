# PROCEDURE TREE

**How the first one was actually built, as a structural procedure.** Not a
summary of the result — the *method*, with the order, the reasoning, and the
places it went wrong.

Follow this with [`../PROCESS/`](../PROCESS/) and the result is reproducible. The
other three trees describe the machine; this one describes the **act of making it**.

---

```
0  GIVEN
   a wish, in the operator's words, and a machine
        │
        ▼
1  UNDERSTAND ───── questions, batched, until the purpose is one sentence
        │            exit: "what decision does this change?"
        ▼
2  RESEARCH ─────── reference taken apart, both directions
        │            system inventoried, every cost MEASURED
        │            load-bearing things named as prohibitions
        │            loop back to 1 for the new questions — twice, usually
        ▼
3  PLAN + R0 ────── architecture with the refresh budget computed
        │            build order argued from rework cost
        │            5 theoretical failure questions answered on paper
        │            every dependency executed and versioned
        │            risks and gaps written down
        │            ═══ HUMAN APPROVES ═══
        ▼
4  BUILD ────────── collector → server → page → supervisor → self-test
        │            each piece run and read in a terminal before the next
        │            atomic writes; trace mode on from the first line
        │            INTERRUPT only for the 3 reasons; everything else → list
        ▼
5  VERIFY ───────── parse · in-page · behavioural
        │            every control pressed, result read
        │            watched across a re-render
        │            good / bad / slow / late / stale / absent made distinct
        │            kill-and-recover; cold reboot
        ▼
6  ITERATE ─────── six passes from different angles
        │            stop after two consecutive passes find nothing
        ▼
7  DELEGATE RISK ── backup (hashed, sampled, links by kind)
        │            containment (isolation, no nesting)
        │            quarantine (proven restorable, self-describing)
        ▼
8  HAND OVER ────── the blueprint, the skill, and the honest list
                     of what was found and deliberately not done
```

---

## Why this order and not another

**Collector first.** It is the only piece that knows the system. Run alone in a
terminal, it is where every assumption meets reality. In the worked example the
collector found that one health check cost **8.5 seconds**, that a background job
was **deadlocked**, and that a fleet expected to be "the best local models" held
**one 1.5 B model**. All three changed the design. None was visible in the code.

**Page last of the visible pieces.** Every hour spent making it beautiful against
mock data is an hour spent twice. The page should meet real numbers that
disagree with the assumptions.

**Supervisor after the page.** A supervisor for something not yet stable is a
supervisor that restarts you mid-edit.

**Self-test last.** A test written before the thing exists tests your imagination.
The structural pass is written with the page; the *behavioural* pass is written
**after a defect has been found**, because that is when you learn what a check has
to be capable of catching.

---

## Where it went wrong, and what each failure taught about the *method*

| # | What happened | What it teaches about procedure |
|---|---|---|
| 1 | Built page-first against a mock | assumptions survived to meet real data — never do this |
| 2 | Collector "fast" in the plan; 8.5 s measured | **measure before planning**, not during |
| 3 | 5-hour deadlock logged as "collector too slow" | trace mode is not a debugging luxury |
| 4 | AI Analyst shipped broken, 7/7 green throughout | a check that cannot run the handler cannot catch this |
| 5 | `history.length` read instead of `window.history.length` | the test shared a name with the defect |
| 6 | Shadowing audit missed a multi-declarator `let` | **an audit has the same blind spot as a bug** — test the audit |
| 7 | Proven fix applied without permission; console returned 0 bytes | R0 governs behaviour changes, not just the build |
| 8 | "Ollama is down" reported by reading a field that does not exist | the ninth false positive, and the same one |
| 9 | A 30 MB backup stalled the console it protected | the method must include **its own cost** |

Failures 5, 6 and 8 are one family: **a measurement that is confidently wrong.**
They account for a large share of the wasted effort in this project, and the only
durable defence is the three questions in
[`../PRINCIPLES.md`](../PRINCIPLES.md) #3.

---

## The procedure is the deliverable

A dashboard is a build. **A method that can be repeated is the asset.**

The test of this document: hand it to a competent engineer who has never seen the
system, give them a different subject, and see whether they produce something of
the same standard. If the answer is no, this file is missing a step — and the step
is usually one that got skipped the first time.
