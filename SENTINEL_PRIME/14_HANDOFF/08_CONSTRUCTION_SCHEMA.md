# 08 — Construction Schema

**Read this before building anything.** It is how to add work to this project without damaging it.

The failure mode this file exists to prevent was real and mine: I resolved an accurate measurement by
deleting the thing the measurement was about. Everything below is the countermeasure.

---

## The rule

> **We do not solve a gap by removing the gap; we solve it by upgrading the system. If you want to build
> something, you play scaffolding and then raise the building. You do not take the scaffolding down if
> the building is not finished.**

---

## 1. Bug or scaffolding? — decide before you act

> **A bug is obvious and makes no sense in the system. Scaffolding raises the question of what is
> missing.** Different stories.

| | BUG | SCAFFOLDING |
|---|---|---|
| What it is | Something that went wrong | Something not yet built |
| Looks like | A contradiction inside the design | A gap where something is absent |
| Fix | Correct it | **Build it** |
| Never | — | Edit the declaration to hide it |
| Example | A declared server that exists but is broken | A declared server that does not exist yet |

**A red dashboard does not tell you which you have.** Two of the monitor's FAILs are scaffolding. A
future reader must be able to tell them apart from a fault — that is why this file, and why every check
carries its own evidence string.

---

## 2. Adding a gap

Append to `12_PROGRAM\GAP_REGISTER.json`. **Append only** — the file is a ledger, and rewriting it
destroys history.

```json
{
  "id": "UPPER_SNAKE_ID",
  "area": "wiring | concept | dependency | logs | hermes-gateway-profile | architecture",
  "status": "OPEN",
  "what": "one line, in plain words, naming what is missing",
  "evidence": "the check id, file path or measurement that shows it",
  "impact": "what it prevents",
  "fix_requires": "what closing it actually takes - including 'DOCUMENTED ONLY' when that is correct",
  "owner": "Popy | Mavis"
}
```

There are **18 entries, all `OPEN`**. Areas in use: `hermes-gateway-profile` 9 · `concept` 5 ·
`dependency` 1 · `wiring` 1 · `logs` 1 · `architecture` 1.

**`fix_requires` is mandatory.** A gap whose closing action is unclear is not ready to be tracked.

---

## 3. Closing a gap

1. **Build the thing.**
2. Re-measure — `python survey_build.py` or the relevant check.
3. Set that entry's `status` to `CLOSED-BUILT`.
4. **Do not delete the entry, and do not edit the blueprint to match.**

The gap's history is the record that the work was decided and then done. Deleting it leaves no trace
that the requirement ever existed.

---

## 4. Before you call anything done

The standing rule for this project:

> **Hand the result to a `verifier` subagent before calling it done.**

Self-measurement is not verification. A green log line is not a working product. Three rounds of
adversarial verification on this build found **seven defects**, three of them in code the previous round
had just written as "complete" — and one false PASS shipped because a check searched for evidence after
the newest marker when the failing run had written no marker at all.

The verifier must be told to try to **refute** the claim, not confirm it, and must be given the
reproduction steps for anything it should attack.

### Two polarities, always

Every guard needs **both** directions proven:

- the **polarity** — the wrong input is caught;
- the **control** — the right input still passes.

A guard that only ever fires is as useless as one that never fires. During this build, adding a
correctness check invented a **false FAIL on three of four live routes**, and only the paired controls
caught it — the unit suite could not, because those payloads are not its inputs.

---

## 5. Recording a mistake

Append to `11_BRAIN\04_METHOD\MISSTEPS_AND_CORRECTIONS.md`. **Append only, always.** A correction is a
new entry that references the old one by timestamp and excerpt. Editing history is forbidden.

There were **27 entries, M-01 … M-27**; M-01 … M-27 were destroyed by a truncating write on
`2026-10-06` and the file now holds only **M-28 and M-29** (see M-29 for the full account and the three
rules it puts in force). Each entry states what went wrong, the
evidence, the correction now *in force*, and a control that proves the correction cannot regress.

**If your correction invalidates something an earlier entry claims, do not edit it.** Write a new entry
that says so. M-25 exists because M-24's claim that a self-audit "paid for itself" turned out to be
wrong.

---

## 6. Language and encoding rules

| Rule | Enforced by |
|---|---|
| English in all code, identifiers, comments, messages, UI, tests | review + `NoRomanianInCode` (54 assertions) |
| Romanian only in wisdom, doctrine, quotations | same |
| **Zero Romanian diacritics in `.py` and `.ps1`** | `NoRomanianInCode` |
| PowerShell 5.1 only | hard constraint — no PS7 syntax |
| `_PATH` / `_PID` suffixes — variables are case-insensitive | `no_case_shadowed_params` |
| BOM-less UTF-8 for `.py` | measured by the survey |
| **CRLF for `.bat`** — `cmd` mis-parses LF | `every_bat_is_crlf` |
| Use `-File`, never `-Command`, in startup | `startup_uses_file_not_command` |

---

## 7. The honesty law — non-negotiable

> **Never invent a number. Measure it, or say `NOT_MEASURED` / `NOT_RUN` / `NOT_AVAILABLE`.**

The vocabulary is load-bearing:

| Term | Means |
|---|---|
| `MEASURED` | Measured on this run |
| `NOT_MEASURED` | Not yet measured. **Not** "probably fine" |
| `NOT_AVAILABLE` | The thing does not exist to measure |
| `NOT_RUN` | The check could not execute — falsified nothing |
| `UNVERIFIED` | Could not be held against its source |
| `SCAN INCOMPLETE` | A walk hit its budget; the result is not clean |

**Always show the age of a measurement.** A value without a timestamp is a claim, not a measurement.

### Known instances where this law was nearly broken, and what caught them

- A collector recorded its result on only one branch, so **4 real probes reported `probed: 0`**.
- A race inside the writer's window turned **one failure into a false FAIL and a false PASS** in the
  same run.
- An exemption with nothing behind it reported **compliance**.
- A fix wired to a key the producer never writes made an exemption **inert**, so a payload declaring
  99 while shipping 30 reported clean.

In every case the rule that caught it was a **test that could fail**, not a review.

---

## 8. Definition of done

A piece of work is done when:

1. It is **built**, not declared.
2. A **test covers it**, with both a polarity and a control.
3. The suites pass: `502 / 0 / 0` and `40 / 0 / 1` (or `43 / 0 / 0` with `--coldstart`).
4. The cold start still passes: `43 / 0 / 0`.
5. A **verifier** has tried to refute it and reported honestly.
6. Any mistake is appended to the doctrine, not edited away.
7. `python survey_build.py` has been re-run and the handoff documents refreshed.
8. If it closed a gap, the register entry is `CLOSED-BUILT` and **still present**.