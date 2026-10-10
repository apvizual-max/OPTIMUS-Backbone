# CHECKLIST — the definition of done

Not "it works". **A dashboard is done when it cannot be caught lying, and its
handover is usable by someone who knows nothing about it.**

Work down the list. Anything unticked is not a caveat — it is unfinished.

---

## 1 — Truthfulness

- [ ] Every displayed number traces to a live measurement taken in this cycle
- [ ] **Down, slow, late, stale, unknown and empty all look different**
- [ ] No value is shown without a denominator
- [ ] No duration is rounded into a different magnitude
- [ ] Data age is on screen, always, beside the data
- [ ] A blank is always *explained*, never unexplained
- [ ] No conclusion is shown that the reader cannot re-derive from the screen
- [ ] No failure path returns a value that collapses several causes into one

## 2 — Function

- [ ] Every tab renders with real data
- [ ] **Every control pressed, and the result read**
- [ ] Results survive at least one re-render
- [ ] Anything typed survives a poll
- [ ] Keyboard paths work, and do not fire while typing
- [ ] Deep links restore the state they name
- [ ] Actions are whitelisted by identifier, output capped, command echoed

## 3 — Self-contained

- [ ] **Zero external resources — asserted by a test, not hoped for**
- [ ] Fonts served locally, including the icon subset
- [ ] Works with the network disconnected
- [ ] Opens over HTTP, and says so usefully if opened as a file

## 4 — Self-verifying

- [ ] File-level parse clean
- [ ] In-page self-test green **and demonstrably capable of failing**
- [ ] A behavioural pass that **runs a real handler** against a stubbed
      dependency and asserts the result reached a *connected* node
- [ ] Every check answered: could it pass on broken code? on fixed code? is it
      reading the object or a neighbour?

## 5 — Survives reality

- [ ] Killed → recovers, unaided
- [ ] Rebooted → returns on its own, without a human
- [ ] Source edited → the running/stale mismatch is *visible*
- [ ] Data source broken → last-good served, marked old, never blank
- [ ] Measurement slow → the operator is told, not left waiting
- [ ] Rapid clicking → no duplicate requests, no lost state

## 6 — Cost

- [ ] Processes spawned by the dashboard, counted
- [ ] Memory held, measured
- [ ] Bytes copied per maintenance action, known
- [ ] A heavy *maintenance habit* has been measured — copying 30 MB on every
      change measurably stalled the console it was protecting
- [ ] Nothing the dashboard does is worse than the problem it reports

## 7 — Restore point

- [ ] Every file hashed into a manifest
- [ ] A sample **re-read from disk** and compared — hashing the buffer you just
      wrote proves nothing
- [ ] Links handled **by kind, not by truthiness** (a hard link is not a junction)
- [ ] Zero nested backups
- [ ] Separate from the live tree
- [ ] **Proven restorable** — not merely created
- [ ] Refreshed at checkpoints, not after every change

## 8 — The handover

- [ ] A stranger can rebuild this **from the folder alone**
- [ ] Dependencies listed with versions **measured, not remembered**
- [ ] The trees describe the system as it is now
- [ ] The postmortem lists every defect, with the measurement that convicted it
- [ ] The anti-patterns are recorded for the *next* build
- [ ] **The "found, not done" list exists**, each item with whose decision it is
- [ ] The blueprint is updated with what this build taught the method

---

## The last question

Two passes from different angles found nothing new, **and** you cannot name
another thing wrong.

If you can, keep looking. The dangerous state is not "broken" — it is **green, and
believed finished.**

> When you think you are done, look for improvements. Look until the goal is
> absolutely satisfied, and do not stop until it is. That is the whole point.
