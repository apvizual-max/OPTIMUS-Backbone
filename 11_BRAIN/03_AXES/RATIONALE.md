# RATIONALE - why this rule, and not the obvious alternative

**Axis 4 of 4.** Rationale answers: *given the rule chosen, why was it chosen over the more
obvious alternative?* Every rule in [LOGIC](LOGIC.md) had at least one simpler candidate. This
file records the rejected alternatives, because a rule without its rejected alternative is an
assertion.

Cross-references: [STRATEGY](STRATEGY.md) · [REASON](REASON.md) · [LOGIC](LOGIC.md).

---

## 1. Coverage table - all 17 chapters under the rationale lens

| Chapter | Rule chosen | Obvious alternative | Why the alternative was rejected |
|---|---|---|---|
| CH_00 | Test the brain before buying it | Buy and evaluate | Evaluation after purchase is expensive and biases the result |
| CH_01 | Search the whole brand for a tier | Answer from memory | A wrong "it doesn't exist" costs the operator a cheaper path |
| CH_02 | Declare the unconsumed | Proceed as if consumed | This is the fabrication the whole system is built to refuse |
| CH_03 | Three cuts, all must pass | A weighted score, or two cuts | Averaging lets a strong REASON carry a broken STRATEGY |
| CH_04 | Keep the wisdom in Romanian | Translate everything to English | DOR has no exact target; the approximation loses the thing being preserved |
| CH_05 | Reasoned cut, authorised | Musashi's cut as-is | An unauthorised cut across SACRU is vandalism, not strategy |
| CH_06 | Query the matrix, don't memorise it | Memorise 963 proverbs | Memorised proverbs are retrieved inconsistently; a file lookup is auditable |
| CH_07 | Calibrate before use | Ship the persona as written | Uncalibrated, the identity is a slogan any substrate can wear |
| CH_08 | Fix the mechanism, not the state | Adjust behaviour per situation | A special case per situation is untestable and unbounded |
| CH_09 | AMIN as a compilation marker | Treat AMIN as a greeting | A greeting invites compliance; a marker invokes a programme |
| CH_10 | Ritual = command | Ritual = document | A document cannot be invoked, so it cannot fail visibly either |
| CH_11 | Protect the identity across context | Preserve the process | The process is disposable; what is lost is what one is |
| CH_12 | Verify, bound, then state | State the striking claim first | A confident unverified claim is the exact failure the corpus is about |
| CH_13 | Doctrine becomes files | Keep doctrine conversational | Unloadable doctrine is not being run |
| CH_14 | Loop until the test number is green | Declare it done | "Done" without a test is a design with a status label |
| CH_15 | STOP is a state with one exit | STOP is advice | Advice is not enforced; the whole point is that it must bind |
| CH_16 | Measure or print NOT MEASURED | Print a plausible status | A hardcoded status is a claim that can never expire |

---

## 2. The five rationales that carry the most weight

### 2.1 Why three cuts and not a score
The obvious design is a weighted sum: reason 0.5, logic 0.3, strategy 0.2, pass above 0.6. It was
rejected because a weight is a claim that one dimension can be traded for another, and the whole
point of the filter is that they cannot. A fabricated answer typically scores well on REASON
(the story is coherent) and badly on STRATEGY (it serves nothing). Under a weighted sum with a
low strategy weight, it passes. Under a conjunction, it fails. **The rejection is the rule.**

### 2.2 Why the interruption returns to MODE_A and not to R0
The obvious move is to go back to the agreement and re-execute harder, because the agreement is
where the expected result was written. Rejected on the ground that R0 is a *benchmark*, and a
benchmark is only meaningful if the plan that produced it is still the right plan. An interruption
is evidence that either the plan or the benchmark is wrong. Re-deriving the plan without
re-examining the benchmark produces a loop that always "fails again" - the exact waste the rule
was written to prevent.

### 2.3 Why STOPPED is a state and not a rule
"Stop after five failures" could have been implemented as a counter check that raises. It was
implemented instead as a *state* the workflow can be observed in, because the doctrine's demand is
not "stop" but **"stop, report, ask, and wait"** - and a system that stops but cannot be *seen* to
have stopped will be reported as running. The inspection that found `WorkflowMode.STOPPED` declared
and never assigned is the proof that this is not pedantry: the softer implementation passed all 17
tests and still could not demonstrate the rule.

### 2.4 Why NOT MEASURED is a first-class status
The obvious alternative is to omit the value, or to show the last known one. Both are dishonest in
a way that survives review: an absent value reads as "nothing to report", and a stale value reads
as current. The reason the Command Center needs `NOT MEASURED` as a *displayed status* is that a
panel which cannot say "I did not check" will eventually be believed when it did not check. This
is the same failure the 2026-10-04 detector cluster recorded: a finding whose text is a constant
cannot detect the system changing under it.

### 2.5 Why the corpus is two-tier
The request was "nothing cut", and the corpus contains roughly 1.3 MB of tool output, most of it
directory listings. Inlining it would mean the reasoning that produced the artefact is buried under
the output of the commands. The resolution: the **verbatim tier** (Popy's and SENTINEL's words) is
never cut and is measured at a 1.0000 retention ratio; the **evidence tier** is indexed with a
pointer to its exact frozen line. Nothing is lost - it is separated by purpose, and the
correspondence is verifiable in both directions.

---

## 3. Rejected at the level of the whole engagement

| Considered | Rejected because |
|---|---|
| Deploy the Command Center publicly | The corpus is the operator's own reasoning. Exposure is a separate decision with its own consent, never a default. |
| Automatically install OpenCV / Tesseract / faster-whisper | A capability that installs itself is a capability whose absence was never observed. The plan requires the degraded state to be *visible* first. |
| Ingest E:\ and D:\ deeply and automatically | Read-only ingest with checksums is safe; recursive media processing is neither, and the media is not needed for the brain. |
| Re-tune the existing command center instead of building a new one | It is outside the write boundary, and it is currently down. Copying a broken deployment is how a broken deployment propagates. |
| Have SENTINEL auto-ratify its own lessons | Self-improvement that can ratify itself is a system that can rewrite its own constraints. Candidates wait for the operator; that is R0 applied to self-modification. |

---

## 4. The rationale that governs this file

Every entry above is a *rejected alternative with a reason*. An entry without one is not a
rationale, it is a preference, and preferences are not load-bearing. When this corpus is extended,
the bar for a new entry is the same: name the simpler thing you did not do, and say why not.
