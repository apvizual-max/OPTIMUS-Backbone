---
name: mavis-subject-completion-skill
description: Finish the subject, not a proxy for it. Use before declaring any task done, after any second fix on the same symptom, or whenever you catch yourself offering evidence that proves something easier than what was asked. Carries a runnable gate at scripts/depth_gate.py.
---

# Subject Completion — do not escape into a proxy

## The two things being confused

**The subject** — the thing asked for, in the operator's own words. It has a name you
copied from them.

**A proxy for it** — something adjacent that is *easier to prove*. Reachable. Answering.
Configured. Non-crashing. Green in the log.

Almost every failure that reads as competence is a **proxy standing in for the subject**.
The work was real, the evidence was real, the subject is untouched.

> A proxy is not a partial success. It is a *different, closed* task reported under the
> original one's name.

## The five escapes

| Escape | What it looks like | Why it survives |
|---|---|---|
| **The plaster** | fix #2 on the same symptom | Each one *works*. None removes the cause. |
| **The proxy** | evidence about a smaller claim | The evidence is real — just about the wrong thing. |
| **The shallow read** | index, summary, description, count | Fast to produce, looks thorough, reads nothing. |
| **The compliant close** | declaring done at depth 2 | Depth 2 is where the symptom stops. |
| **The bypass** | solving a neighbouring problem | Adjacent problems are easier and nobody is watching them. |

All five feel like progress. All five leave the subject unsolved.

---

## Rule 1 — the plaster test

> **A workaround applied twice is not a workaround. It is a second bug.**

One plaster is legitimate: a known constraint, a deferred decision, a documented trade-off.
**Two plasters on the same symptom is a diagnosis you refused to finish.** The cause is
still there and will produce a third.

If you catch yourself about to fix the same thing again, you have already failed once.
Stop and go to Rule 2.

**Real instance.** `config.yaml` reverted to a free-tier model; I re-applied the correct
model. It reverted again. I re-applied it again. Three restores, then a fourth — before
reading the file that contained the values it kept restoring *to*. The subject was "the
config must stay correct". Three of my four actions were plasters.

## Rule 2 — the depth ladder

Do not stop early. Each rung has a distinct question, and rungs 3–4 are where subjects
actually get finished.

| Rung | Question | Evidence shape |
|---|---|---|
| 1 Surface | Does the symptom reproduce? | error text, a failing call |
| 2 Cause | What immediate mechanism produces it? | code path, config field, stack |
| 3 Loop | **What makes it come back?** | the writer, the scheduler, the boot order |
| 4 Recurrence | Why did this survive undetected? | no test, no alarm, no owner |

**Rung 1–2 is a diagnosis. Rung 3 is a fix. Rung 4 is a system that does not regress.**
Reporting done at rung 2 with a confident tone is the single most common way I mislead.

*Rule 3 is where today's whole config saga belonged, and I spent hours at rung 2.*

## Rule 3 — the escape test

Before saying done, answer in one sentence, using the operator's words:

> **"The operator asked for ___. That is now ___."**

If the second blank is a synonym of the first, you are done. If it is *easier* — reachable,
configured, green — you have delivered a proxy and must keep going or say plainly that you
did not finish.

Real escapes from one session:
- *"A2A and relay per profile"* → delivered *"all 9 profiles answer HTTP 200"*
- *"the config must stay correct"* → delivered *"config correct right now"*
- *"ingest 120 skills"* → delivered *"120 skills indexed"*
- *"M3 not working"* → delivered *"M3 answers"*

Each is true. None is the subject.

## Rule 4 — evidence must be independent of my instrument

A test I wrote to pass does not verify. A log line I grepped for does not verify.
**Self-measurement is not verification.**

Required before any "done":
1. The measurement is against **the subject**, not a proxy.
2. The measuring instrument is **not something I built for this claim**.
3. Where a measurement is impossible, **say it is unverified**.

A count computed by the agent and a count computed by PowerShell are two instruments. The
second is evidence. The first is a claim.

## Rule 5 — run the gate

`scripts/depth_gate.py` takes a closure record and returns a verdict. It is not
decoration; it is the mechanical form of rules 1–4.

```
python scripts/depth_gate.py <record.json>
```

It checks 8 rules, in order:

1. **R1 plaster test** — `fix_number_for_symptom` must be a genuine int and exactly 1. A value ≥ 2
   is an unfinished diagnosis; a float, string, bool, `0` or `-1` is malformed and fails rather
   than being read as "first fix". **It also cross-checks the evidence text**: if the evidence
   itself narrates a repeat attempt while the field claims 1 — one of the two is untrue. The
   test fires on a **standalone phrase**, or on a **repair action combined with** a repetition
   word or a count pattern. Two refinements matter, and both were added after audits:

   - **Actions are word-bounded regexes, not substrings.** This replaced two earlier attempts,
     both of which an audit broke. Plain stems missed inflections — `"rewritten"` does not
     contain `"rewrite"`, `"rebuilt"` does not contain `"rebuild"`, `"retries"` does not contain
     `"retry"`. Bare substrings then matched the *wrong words* — `retr` hit **retrieved**,
     `patch` hit **dispatched**, `fix` hit **fixture** and **prefix**, `times` hit
     **sometimes**: ten false positives in one probe run. Each action is now a pattern that
     lists the inflections it accepts (`\brestor(?:e|es|ed|ing)\b`, `\bretr(?:y|ies|ied|ying)\b`,
     `\bfix(?:es|ed|ing)?\b`, `\brewrit(?:e|es|ing|ten)\b|\brewrote\b`, …), so it matches the verb
     it means and nothing else. T8.3j guards the false positives, T8.3h the inflections.
   - **A count alone is not enough.** `two attempts`, `3 times`, `twice` only contradict a
     "first fix" claim when a repair action is present too. An audit showed a bare count rule
     convicting *"the suite passed 3 times in a row"*, *"3x faster"* and *"the port was probed
     twice by healthcheck"* — which is measurement prose, not plaster. `\d+x` was removed
     outright: `3x faster` and `2x speedup` are multipliers, never repetition.
   - **A negated action is not an action.** *"no rewrite needed"*, *"never restored"*,
     *"without any manual fix"* describe repairs that did **not** happen, so they cannot
     contradict a claim about repairs that did. The negator is looked for on **both** sides of
     the verb, because it is not always on the left. T8.3i guards these.
   - **Action and repetition must share a clause.** Clauses are split on punctuation and on
     *and* / *but* / *then*, so a repetition word in one clause cannot combine with a repair
     verb in another. *"the second run was clean and the config was patched"* is one honest
     fix, not a repeated one. T8.3k guards it.
2. **R2 depth ladder** — `depth_rung` must be a genuine int in 1–4 and ≥ 3. `"4"` and `5` are
   rejected, not coerced.
3. **R3 escape test** — `evidence_is_about` must be `subject`. `proxy`, `probably`, anything
   else, fails.
4. **R4 independent evidence** — `independent_evidence` must be exactly `true`. `1` is not `true`
   and fails.
5. **R4 instrument independence** — `instrument_built_by_me` must be exactly `false`.
6. **R4 evidence substance** — `evidence` must carry ≥ 3 distinct non-placeholder tokens.
   `"verified"`, `"done"`, `"tested"`, `"fine"`, `"0 errors"` and empty are *assertions*, not
   measurements, and fail. Numerals count as tokens (`"200"`, `"9/9"`, `"M3"`, each counted
   once), as do words of 4+ characters, and unspaced scripts (CJK, Thai, Devanagari) are
   counted in groups of 4 characters.
7. **R2 permanence claim** — a claim containing *will not recur / will never / permanently /
   for good / fully solved / done for good / no longer possible* is only allowed at rung 4.
   Below that it is an overclaim.
8. **R3 subject restatement** — `subject_restated` must carry ≥ 60% of the subject's
   significant words. An empty subject scores 0% and cannot be satisfied.

Exit code 0 = pass, 1 = fail, 2 = incomplete. **A fail is not a formality. Fix the work.**

All failing rules are reported, not just the first, so a single pass at the record does not
become a queue of one-defect-at-a-time re-runs.

### What the gate cannot do — read this before trusting a PASS

**The gate is a schema linter, not a judge.** It enforces the *shape* of an honest closure
record. It does not verify substance, and it does not read prose for meaning.

- It **trusts every semantic field you declare.** `evidence_is_about`, `depth_rung`,
  `fix_number_for_symptom`, `independent_evidence`, `instrument_built_by_me` are all
  self-declarations. Label a proxy `"subject"` and it passes. Declare rung 4 over rung-2 work
  and it passes. The only cross-check is R1's evidence-contradiction test, and it is a
  keyword scan, not a judgement.
- The restatement check is **bag-of-words overlap**, so it is **gameable by padding**.
  Repeating the subject's own words in `subject_restated` satisfies it without saying anything
  about the outcome. An independent audit demonstrated this.
- A PASS means: *the record is well-formed, the numbers are the right shape, the evidence
  field is not empty, and the author wrote the operator's words down.* It does **not** mean
  the subject is finished. **The semantic judgement is still mine, and it is still the part I
  get wrong.**

These are asserted as counted, passing checks in `T6.2`–`T6.6` and `T8.5`–`T8.7`. **`T6.2`
through `T6.6` are real assertions, not documentation**: they read this file and FAIL if the
disclosure is deleted, so the limitation cannot be quietly dropped along with the sentence
that describes it. (Two earlier versions got this wrong. The first assigned the limitation to
an unused variable and this file claimed it was "asserted in T6.2 so it can never be forgotten"
— asserted nowhere. The second passed a hardcoded `True`. An audit caught both. The third
reads the file. `T8.4` likewise fails rather than skipping if its fixture records are missing,
so the real convictions cannot be deleted to make the suite green.)

## Running the tests

```
python scripts/test_depth_gate.py
```

177 assertions, exit 0. The suite exists to prove the gate **discriminates**, which is not the
same as the gate running:

- **T1** — it can PASS. A gate that cannot pass is noise.
- **T2** — each rule has a record that fails *only* it, through both the API and the real CLI.
- **T3** — flipping one field flips the verdict in both directions.
- **T4** — every defect at once is reported, not short-circuited to the first.
- **T5** — shape abuse: empty, float, bool, string, out-of-range, wrong-type values never
  crash and never pass by accident.
- **T6** — the known limitations, as counted assertions.
- **T7** — honest paraphrase is *not* punished, and a bare all-clear still is.
- **T8** — the independent audit's own adversarial records, as permanent regressions.
- **T8b** — canonical evidence (numerals, ports, versions, CJK) must be accepted; contentless
  evidence must be rejected.

`T8.4` is **honestly semi-circular**: it pins each real record to the exact rule set the gate
produced, so it proves the gate has not *drifted*, but it cannot certify that the expected sets
are the *right* ones — I typed both. Its second assertion (each record still has substantive
evidence) is the genuinely independent part. Its value was demonstrated: it is what caught the
over-broad `revert` marker in defect 3, by failing when `case_a2a_proxy` picked up a second
failure it should not have had.

### Independently audited

An independent verifier — an agent that did not build any of this — ran the suite, then
**mutation-tested the gate** across five audit rounds: every rule forced to always-pass,
`check()` forced to always return PASS, a dummy ninth rule, a regression re-adding the
over-broad `revert` marker, the count rule reverted to firing alone, the negation guard
removed, stems reverted to whole words, and the irregulars deleted. **Every mutation the
suite was designed to catch was caught**, and the suite flipping to exit 1 on each is the
evidence that it is not self-fulfilling — which matters more than the 177/177 count itself.
One mutation that initially *escaped* (deleting the `redo`/`redone`/`redid` irregulars, which
no fixture exercised) is why those irregulars now have a named guard, T8.3l.

The same audit wrote its own dishonest records to attack the gate, and four further passes
audited the fixes. Between them they found **fourteen** limitations I had not disclosed —
**ten real defects, now fixed**:

- **`evidence` was read by no rule at all** — required by the schema, printed by the CLI, but
  no check inspected it, so `evidence: ""` passed everything. Now **R4 evidence substance**.
- **Evidence narrating a repeat attempt passed** while the record claimed the first fix. Now
  folded into **R1**.
- **The first fix for that rule punished a truthful record.** A flat marker list including
  `revert` and `restor` failed `case_a2a_proxy`, whose evidence honestly says *"no longer
  reverts"* — the phrasing a *fixed* record uses. Replaced with the conjunction in rule 1.
- **The evidence rule rejected canonical honest evidence.** It counted only words of 4+
  characters, so every *digit* was dropped: `"HTTP 200 on 9/9 endpoints"` was rejected as too
  thin — in a domain where the number often **is** the measurement. It also double-counted,
  scoring a bare `8642` twice. Both fixed; T8b guards them.
- **The action stems missed their own inflections.** `"rewritten"` does not contain
  `"rewrite"`, `"rebuilt"` does not contain `"rebuild"`, `"retries"` does not contain
  `"retry"` — the most common forms of those verbs were invisible. Stems plus explicit
  irregulars added; T8.3h guards them.
- **A negated action was treated as an action.** *"no rewrite needed"* and *"never restored"*
  describe repairs that did **not** happen, and were convicting honest records. T8.3i guards them.
- **The action words were raw substrings, matching the wrong words entirely.** `retr` matched
  **retrieved**, `patch` matched **dispatched**, `fix` matched **fixture** and **prefix**,
  `times` matched **sometimes** — ten false positives in a single probe run. Replaced with
  word-bounded patterns; T8.3j guards them.
- **Action and repetition could combine across clauses.** *"the second run was clean and the
  config was patched"* is one honest fix; the repetition word and the repair verb were being
  read from opposite ends of the sentence. Now matched per clause; T8.3k guards it.
- **And I documented a fix I had not made.** This file claimed `"rewrote"` was "listed
  outright" while it was in no list, so the reader was told `"I rewrote the config three
  times"` was covered when the gate walked past it. A doc claim the code contradicts is
  worse than a missing entry, and it was only found because an audit read the prose against
  the source. Now covered — and guarded by T8.3l.

**Four remain, disclosed rather than patched:**

- **T8.5** — the mislabelled proxy: a record that declares `"subject"` while describing a proxy
  passes. Every semantic field is a self-declaration.
- **T8.6** — the padded restatement: the token overlap is a bag-of-words measure, so repeating
  the subject's own words satisfies it without describing an outcome.
- **T8.3m** — a **known false positive I did not fix.** A *noun* "retry" describing system
  behaviour — *"the webhook was dispatched twice because of a retry upstream"* — trips the
  rule, even though nobody was fixing anything. Telling the verb *"I retried"* from the noun
  *"a retry upstream"* requires parsing the sentence, and every key I tried on that misfired
  on honest prose. Convicting a system that retries itself is exactly the failure I have spent
  five rounds removing, so it is recorded loudly rather than quietly patched.
- **T8.3e** — the repeat-detection is a **keyword scan with irreducible blind spots**.
  `"ran it again"`, `"flipped the flag again"`, `"restarted the service twice"` and
  `"I edited the config three times"` all pass: a bare `again`, `twice` or a bare count after
  an ordinary verb is genuinely ambiguous, because `"verified again, same result"` must not be
  convicted. Widening the heuristic to catch them was tried and rejected — it convicted honest
  re-verification, including *"I had to read the file to find the writer that overwrote it"*,
  which is **the exact behaviour this skill exists to produce**. I would rather miss five
  phrasings than punish the anti-plaster move. The gate catches the explicit forms
  (`restored three times`, `reverted again`, `the patch was rewritten multiple times`,
  `retried three times`, `I had to retry`) and misses the ambiguous ones.

I chose to **disclose rather than patch** the padding weakness too, because the obvious fix
false-positives on honest records — it rejects a correct restatement that reuses the subject's
own vocabulary. **A gate that punishes truth teaches its author to flatter the gate.** I
shipped that defect once (defect 1 below) and will not ship it again.

### The ten defects the process caught

Recorded because they are the argument for testing a gate instead of trusting it, and for
re-running the real records back through it after every change. Eight of the ten were found
by an independent audit, not by me.
1. **R3 originally failed honest records.** It compared a literal 24-character prefix, so a
   correct restatement using different words ("exposed per profile" vs "per profile") was
   rejected. Replaced with 60% significant-token overlap, which survives reordering and
   rewording. T7 is the guard.
2. **R1 originally accepted `1.9`.** `isinstance(1.9, int)` is `False`, which flipped the
   negation and let a float walk through as "first fix". Now gated on `type(x) is int`.
3. **The evidence/count cross-check punished a truthful record.** A flat marker list including
   `revert` and `restor` failed `case_a2a_proxy`, whose evidence honestly says *"no longer
   reverts"*. T8.3b guards it.
4. **The evidence-substance rule rejected honest evidence and double-counted.** It counted
   only words of 4+ characters, so every digit was dropped and `"HTTP 200 on 9/9 endpoints"`
   failed; and a bare `8642` scored twice, letting three numbers clear a floor that a real
   sentence could not. T8b guards both.

The shape that matters: defects 1 and 3 are the gate **refusing something true**. That is the
failure mode this instrument exists to prevent in me, and neither was found by reading the
code — one was found by the test suite, one by an audit, and one by re-running the *real*
records back through after a change. Defects 3 and its successor also cancel into a design
note: too broad convicts the honest, too narrow misses the guilty, and only running the real
records exposes which side you landed on.

There was also a latent hole: an empty `subject` made the prefix `""`, and `"" in anything`
is `True`, so a contentless subject satisfied R3 regardless of the restatement. The
token-overlap change closed it; T5.4 is the guard.

## Convicted on real records

The gate was run against three actual closures from this work, all of which it rejected for
the correct reason. Records in `C:\Users\apviz\.learn\subject-completion\`.

| Real claim | Rules failed |
|---|---|
| "Hermes works — 9/9 profiles answer HTTP 200" for a subject of *A2A and relay per profile* | R3 |
| "120 skills ingested" delivered as *120 skills indexed* | R2, R3 |
| "Config fixed, will not recur" after **four** restores, diagnosed only to rung 2 | R1, R2, permanence |

A gate that passes those three is decoration. They are the ground truth.

Read them honestly, though: **their strength is uneven.** The ingest case fails on rung depth
independently of any self-declaration, so it is the sturdiest. The config case declares its
evidence as being *about the subject* when it plainly only proves *correct right now* — that
choice makes the record **easier** to pass, and it still fails. The A2A case is the thinnest:
its verdict rests entirely on the `evidence_is_about` field, which is precisely the field the
gate cannot verify. Set that one field to `"subject"` and the record passes **all 8 rules with
verdict PASS**, which is the honest measure of how little weight that conviction can carry. It is
included because the declaration is *honest* — reporting "9/9 profiles answer" as completion
of an A2A-and-relay request **was** a proxy — not because the script proved it.

---

## The closing test

Ask: *would a user of this system, seeing only the evidence I have, be satisfied — and is
that the user who wrote the request?*

Green logs, 200s, non-empty indexes, and no errors are all compatible with a completely
unsolved subject. They are properties of the instrument, not of the system.

If the honest answer is "this proves something smaller than what was asked", that is the
report. Say it in one line and continue — or say you are stopping short, and where.

## Anti-patterns, observed

- Restoring a value three times instead of reading what restores it *to*
- Reporting "0 errors in the log" for a system nobody can use
- Counting files instead of reading them; listing skills instead of ingesting them
- Declaring a system healthy because the port bound
- Letting a green check stand in for the operator's actual question
- Accepting the first fix that works, without asking why it was needed twice

## The compact version

> Finish the subject. A proxy is a different, closed task wearing the subject's name.
> Two plasters means the diagnosis is unfinished. Rung 3 is a fix; rung 2 is a story.
> Evidence must come from an instrument I did not build for the claim.
> Run the gate before saying done.
