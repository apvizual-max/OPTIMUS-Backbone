---
name: mavis-skill-background-task-verdict
description: The discipline of running a long measurement in the background and judging it by WHAT IT PRINTED, not by the exit code of the shell that ran it. Load this when a background task is reported as failed and the output looks complete, when a probe is SUPPOSED to exit non-zero, when a falsification has to run and be reported as a success, or before writing any background runner. Owns the reusable instrument bg-verdict.mjs, the rule that the verdict is the MARKERS in the output, the three exit codes of the wrapper, and the measured evidence that a shell exit code is not a verdict.
role: functional
bot: mavis-google-access-bot
---

# mavis-skill-background-task-verdict

**Role.** The discipline of running a long measurement in the background and
judging it by **what it printed**. It owns one reusable instrument
(`scripts/bg-verdict.mjs`), the rule that the verdict lives in the markers, and
the fact that the exit code of a compound shell command is a **detail of the
inner command**, never the verdict.

---

## 1. Why it exists (the defect, not the preference)

Measured on this station, reported **2026-10-28**:

- roughly **100 background tasks** were reported as **failed** while their
  output was complete and correct.
- a batch of **6 live probes** printed all six result lines and was then
  reported `failed` with exit code **4294967295** (-1).
- the falsification probe `--self-test --fail C1.container` printed
  `VERDICT=FAIL` and exited **2** — *the falsification worked* — and was
  still reported as a failed task.
- diagnostic probes that are **supposed** to return **1 / 2 / 3 / 4 / 128**
  were reported as failed tasks although they did their job.

The exit code of a compound shell command is not a verdict. **A measurement's
verdict is the MARKERS in its output.**

While the operator cannot tell *"the measurement failed"* from *"the
measurement succeeded and the shell exited oddly"*, failures get trained out of
attention — and that is the real damage. A gate that cries wolf is not a gate.

---

## 2. The rule

> **The verdict is in the output. The exit code is only a detail of the inner
> command.**

Read it twice, because it is counter-intuitive for anyone raised on
`if (exit != 0) fail`:

| Situation | The inner command | The verdict |
|---|---|---|
| a measurement that did its job | exits **2**, prints `VERDICT=FAIL` | **PASS** — the falsification worked |
| a measurement that broke | exits **0**, prints nothing useful | **FAIL** — the output says so |
| a wrapper misuse | — | **FAIL**, and it is called a misuse, not a measurement |

---

## 3. The procedure

### 3.1 The instrument

```
node bg-verdict.mjs --out <logfile> --expect "<marker>" [--expect "<marker>"]... \
     [--forbid "<marker>"]... [--expect-exit <code>] -- <command> [args...]
```

Node >= 22, zero dependencies, ASCII source, UTF-8 without BOM, LF endings.

### 3.2 The steps

1. **Name the markers first.** What must the output contain? What must it
   never contain? Write them down before the run, not after.
2. **Name the expected exit code.** Without `--expect-exit`, an exit code of 0
   is required. With it, that exact code is required — use `--expect-exit 2`
   for a probe whose whole purpose is to fail.
3. **Run the command through the wrapper**, with the log file inside a folder
   the run owns.
4. **Read the summary line**, not the exit code of the inner command:
   `EXIT=<code> EXPECTED_EXIT=<code> MARKERS=<passed>/<total> VERDICT=PASS|FAIL`.
5. **On FAIL, read the named line**: `MISSING=<marker>`,
   `UNEXPECTED=<marker>` or `EXIT_MISMATCH got=<code> want=<code>`.

### 3.3 The example that matters

The falsification probe of the Google Access control point. The inner command
is *supposed* to fail, so the inner exit code is **2** and the marker is
`VERDICT=FAIL`:

```powershell
node "C:\Users\apviz\.minimax\agents\mavis\skills\mavis-skill-background-task-verdict\scripts\bg-verdict.mjs" `
  --out "C:\Users\apviz\.minimax\google-access\logs\ga-doctor-selftest.log" `
  --expect "VERDICT=FAIL" --expect "CHECK C1.container FAIL" --expect-exit 2 `
  -- node "C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\Mavis-Google_Access\scripts\ga-doctor.mjs" --self-test --fail C1.container
```

The inner command prints `VERDICT=FAIL` and exits **2**
(`Mavis-Google_Access\scripts\ga-doctor.mjs:917,927,931`). The wrapper prints:

```
EXIT=2 EXPECTED_EXIT=2 MARKERS=2/2 VERDICT=PASS
```

and exits **0** — because the falsification *worked*. Run it without the
wrapper and the same event surfaces as a failed task.

That summary line is **derived** from the two markers and the two output lines
cited above, not measured here: this probe makes live calls (§6), so it was
not re-run inside this skill's own verification. The wrapper's behaviour on
the same shape **was** measured — see §3.4.

### 3.4 The verifier

```
node "C:\Users\apviz\.minimax\agents\mavis\skills\mavis-skill-background-task-verdict\scripts\verify-bg-verdict.mjs"
```

It prints one `OK`/`FAIL` line per check, then
`SUMMARY checks=<n> failed=<n> warnings=<n> falsified=<n>`, then a single
`VERDICT=PASS|FAIL`, and exits 0 only when every check passed. It runs against
**fixtures in a temp directory only** — never a real project, never a real
member's `runs.md`.

Measured **2026-10-28**: `SUMMARY checks=17 failed=0 warnings=0 falsified=4`,
`VERDICT=PASS`, exit **0**. The 4 falsified probes are the negative controls:
the missing marker, the forbidden marker, the exit mismatch and the missing
command — each of them must make the wrapper exit 1 and name the failure.

The verifier was itself falsified: against a deliberately broken copy of the
instrument (forced to always report PASS) **6 of its 17 checks went red**,
`VERDICT=FAIL`, exit **1**. A verifier that cannot go red is not a check.

---

## 4. The exit codes of the wrapper

| Exit | Meaning |
|---|---|
| **0** | the verdict is **PASS** — the measurement produced what it should |
| **1** | the verdict is **FAIL** — a marker was missing, a forbidden marker appeared, or the exit code did not match |
| **2** | **wrong usage** — you called it wrong (no `--out`, no `--expect`, no command after `--`) |

Code **2** is deliberately distinct from code **1**: *"the measurement failed"*
and *"you called me wrong"* are different events and must not be counted
together.

The inner command's exit code is reported as `EXIT=<code>` and compared
against `EXPECTED_EXIT=<code>`. It never decides the wrapper's verdict by
itself.

---

## 5. What it guarantees

- **A measurement that produced what it should never surfaces as a failed
  task**, even when the inner command exited non-zero.
- **The whole output is kept.** stdout *and* stderr go to the log file and to
  the console; nothing is hidden and nothing is silently dropped.
- **The log file is written even when the command fails or cannot be started**,
  so a failed run still leaves evidence behind.
- **The failure is named.** A red run says *which* marker was missing, not
  merely "it failed".
- **The verdict code and the usage code never get mixed up.**

---

## 6. Known limits, stated out loud

- **The whole output is held in memory** and then written. A measurement that
  prints gigabytes will cost gigabytes of RAM — redirect it to a file instead.
- **Markers are plain substrings, not regular expressions.** A marker that is a
  prefix of a legitimate line will match. Keep markers long enough to be
  unambiguous.
- **On Windows an exit status is an unsigned 32-bit value.** Measured
  2026-10-28: `process.exit(-1)` is reported by Node as **4294967295**. The
  wrapper accepts both spellings for the same status, and reports the value
  it observed (`EXIT=4294967295`).
- **The command must be startable as a program.** A shell built-in (`cd`, `set`)
  is not a program — run it through `powershell -NoProfile -Command ...`.
- **The `--fail` path of `ga-doctor.mjs` is NOT offline.** It runs the full
  live check sequence and injects the failure afterwards
  (`ga-doctor.mjs:901-919`), so the example in §3.3 makes live calls.
- **The verdict only covers what was asked.** A wrapper can prove that the
  markers were printed; it cannot prove that the measurement was *meaningful*.
  The markers still have to be the right ones.
- **The wrapper prints the command name only** — never its arguments, never
  its environment. If a secret has to travel, it travels in a file, not in the
  command line.

---

## 7. Cross-references

- `mavis-skill-access-handoff` — the sibling member: it hands work to a
  zero-context session, and it inherits this rule (a handoff that reports a
  falsification as a failure is a handoff that lies)
- `mavis-google-access-bot` — the hub that owns this skill
- `mavis-skill-google-access-control-point` — the control point whose
  falsification probe (`--self-test --fail C1.container`) is the canonical
  example in §3.3
- `mavis-skill-repair-manifest-skill` — the repair surface for a measurement
  that comes back red
- Docs: `Mavis-Google_Access/docs/PUNCT-DE-CONTROL.md`
