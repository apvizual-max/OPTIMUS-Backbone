# 09 — Roadmap

**What comes next, in order, and why that order.**

Every item below is real work that has not been done. Nothing here is a defect to be repaired and
nothing here is to be removed. Read `02_GAPS.md` first if you have not — the roadmap is downstream of
the bug/scaffolding split, because the ordering depends entirely on which side of that line an item
falls on.

**Standing condition for all of it:** a blueprint is a plan, not a defect report. If a step below says
"the declaration stays", that is the point. See `00_README.md` and doctrine **M-27**.

---

## The shape of the work

There are three bands, and they are not equal:

| Band | Items | Nature |
|---|---|---|
| **Foundation** | 1 item (version control) | Unblocks everything else. Costs one decision. |
| **The build** | 9 items (Hermes gateway profiles + their supporting work) | The main body. The operator has sequenced it as profile-by-profile, with Hermes. |
| **Blocked on Popy** | 3 items | Cannot proceed without an owner decision or a credential. |

Only the foundation item can be done in a single sitting without anyone else's input.

---

## BAND 1 — Foundation

### F0. Decide what happens to the lost doctrine entries — do this first

**Status:** waiting on Popy. **Owner:** Popy. **Blocking:** the next edit of
`11_BRAIN\04_METHOD\MISSTEPS_AND_CORRECTIONS.md`.

M-01 … M-27 (44,576 B, 673 lines) were destroyed by a truncating write on `2026-10-06` and are not
recoverable from disk. The file now holds M-28 and M-29 only. Full account in
`01_BUILD_STATUS.md` W10 and in **M-29** itself.

**Three options, and the choice is Popy's:**

| Option | What it means |
|---|---|
| **Restore from his own copy** | If the file exists in an editor buffer, a sync service, or anywhere off this machine, that copy wins and the loss ends here. |
| **Mark as reconstruction** | Rebuild the entries from the surviving themes — memory file, this package, and the code comments — and mark every one as reconstructed rather than verbatim. |
| **Leave it short** | Accept a two-entry doctrine file, and rely on the fact that the lessons survive in the code and in memory. |

**What must not happen:** a silent rewrite. Reconstructing M-01 … M-27 without a marker would put
invented text inside the one file whose entire value is that it is the operator's verbatim record.
**A doctrine file partly invented by an agent is worse than a short honest one.**

Nothing else in this roadmap should proceed past editing that file until this is settled.

### F1. Put the project under version control

**Status:** not started. **Owner:** Mavis. **Needs:** one R0 from Popy. **Blocks:** nothing, but
everything else becomes safer once it exists.

This is `W1` in `01_BUILD_STATUS.md` — and it is no longer a recommendation.

**Why first, specifically.** The doctrine is append-only and integrity-dependent. During this stage,
three independent adversarial verifier rounds could not compare old logic against new logic, because
there was no old version to read — one round had to report its regression check as `UNVERIFIABLE`.
**Then this project lost 44,576 bytes of its most valuable file with nothing to restore from.** That is
the gap closing itself, and it is why this sits above every other item.

**What it means here.** `SENTINEL_PRIME\` becomes a repository with an initial commit capturing the
measured state described in this package. It does **not** mean committing `09_LOGS\` — that directory
holds 1,039 files and 25,234,947 bytes of run artifacts and belongs in an ignore rule plus an archive
policy (see B2). Ports 8900/8901 are OPTIMUS's and are not in this tree.

**Done when:** the workspace is a repository, the initial commit matches the survey in this package,
and `09_LOGS` is ignored with the ignore rule written down rather than assumed.

**The companion guard from M-29 now exists.** `AppendOnlyIntegrity` in `test_suite.py` checks every
append-only record against an append-only baseline and fails on any shrink or missing entry id. It is
proven against the actual 2026-10-06 incident, not merely asserted. What remains for F1 is the part the
guard cannot do: **restore the ability to diff old against new.** A guard can tell you a file lost
content; only version control can hand it back.

---

## BAND 2 — The build: nine Hermes gateway profile servers

**This is the main body of outstanding work.** The operator's framing:

> nine profiles — each has a server in the gateway of Hermes. Each of them is infrastructure that needs
> to be created in Hermes. … We will build the system together side by side.

Plan: `12_PROGRAM\HERMES_GATEWAY_PROFILE_PLAN.md`. Tickets: nine `HPROF_*` entries in
`12_PROGRAM\GAP_REGISTER.json`, one per server, so each closes on its own without touching the others.

**Measured starting position:** 9 declared, **2 resolve** (`filesystem`, `browser`), **7 to build**.
Every one of the 5 missing `.py` servers has its capability *verified live* under another registered
server — so nothing is unreachable today. Building them is about the declared architecture becoming
real, not about restoring lost function.

**Rule that governs every one of these seven:** build the file. Do not edit `OPTIMUS_MCP_CONFIG.json`
to make the monitor go green. Do not delete a declaration. The monitor staying FAIL on these is
correct.

### B3 — `prime-bridge` → `07_BACKBONE\mcp\prime_bridge_server.py`

The natural first build: it is the profile that bridges SENTINEL into the Hermes profile topology, and
the other six benefit from it existing. Blueprint target in `04_BLUEPRINTS.md`.

### B4 — `sentinel-state` → `07_BACKBONE\mcp\sentinel_state_server.py`

Wraps the state plane. Capability already live under the hub's 3 tools; this gives it a named server.

### B5 — `rule-triggers` → `07_BACKBONE\mcp\rule_triggers_server.py`

Capability already live under the hub's 1 tool.

### B6 — `learning-loop` → `07_BACKBONE\mcp\learning_loop_server.py`

Capability already live under the hub's 3 tools.

### B7 — `context-pressure` → `07_BACKBONE\mcp\context_pressure_server.py`

Capability already live under the hub's 1 tool. Note `CONCEPT_C21` in the register is the
documentation-only face of the same idea; this is where it becomes invocable.

### B8 — `web-tools` — the declared package does not exist

`@modelcontextprotocol/server-fetch` **404s** against the registry. A control package answered
`19.3.0` in the same run, so the registry was reachable and the 404 is real.

**This step needs a decision, not a build.** Either the declaration names a package that exists, or
the server is written locally the way B3–B7 will be. Choosing which real package replaces it — or
deciding to write it — is an operator decision. The declaration stays either way.

### B9 — `git` — the declared package does not exist

`@modelcontextprotocol/server-git` **404s**, same control, same conclusion. Same decision shape as B8.

### B2 — Rotate `09_LOGS`

**Needs an R0 before anything is removed.** The operator's standing rule: *deletion is never
automatic*; `ARTIFACT_EMPTY` says so in its own register record.

4 of every 5 files in the project live here. It is not urgent — it is slow-burning — but it will
eventually need a retention policy, and a retention policy is a deletion policy.

**Suggested order:** decide the policy on paper first, land F1 so the archive is versioned, then move
rather than delete. Nothing about this project requires the current 1,030 files to disappear.

### B10 — Surface the five documentation-only concepts

`CONCEPT_C18` (partnership protocol), `C19` (3-Propozitii as an invocable command), `C21` (context
pressure), `C23` (historical cultures corpus), `C24` (963 Hz / SACRU).

Each is doctrine that exists and code that does not. **They are not built all at once** — most become
real *through* the profile servers above. `C21` in particular is what B7 makes invocable. Building
these separately from the profiles would duplicate work.

---

## BAND 3 — Blocked on Popy

Each of these needs an owner decision or a credential. They are listed so nothing is silently
forgotten, not because they are waiting on me.

| ID | What is needed | Why it is blocked |
|---|---|---|
| `BIN_TESSERACT` | Tesseract installed or explicitly waived | External binary, `owner: Popy`. **Nothing in the dashboard claims OCR works.** Register entry stays `OPEN` until the operator rules. |
| B11 — Design runtime | A `HILO_USER_TOKEN` provisioned, and the app launched once | The app is installed (`gateway_main` 17,090,864 B) but has **never been launched**, so no runtime surface is claimed for it. Four ecosystem surfaces describe its cloud seam **from the files on disk** and say nothing about a running Design. |
| B8 / B9 | A decision on the two dead npm packages | Operator's call which package replaces the name, or whether to write it. |

---

## Cosmetic, optional, deliberately not done

| Item | Why it is still here |
|---|---|
| **W5** — the UTF-8 BOM on `collect-sentinel.ps1` | Cosmetic. The file contains **zero non-ASCII characters**, so the BOM is harmless. Touching a working script at wrap-up is how churn is introduced. Recorded so it is a known inconsistency, not a surprise. |
| **W4** — front `/readyz` vs backend route naming | **Correct behaviour**, documented so nobody rediscovers it as a fault. The survey itself hit this: an early probe asked the wrong path and would have reported a false defect. |
| **W7** — `apviz-dashboard-monitor` on `0.0.0.0:9119` | **Not SENTINEL.** Not touched, and this project makes no claim about it. Recorded as a scope boundary only. |

---

## How to pick this up

**1. Read 00_README.md          the rule that governs everything
**2. Read 01_BUILD_STATUS.md W10 — the doctrine loss, and what is pending on Popy's decision
**3. Read 02_GAPS.md            bug vs scaffolding — the split the ordering depends on
**4. Read 08_CONSTRUCTION_SCHEMA.md   the protocol for adding work correctly
**5. Read 01_BUILD_STATUS.md    what is live, what is weak
**6. Start at F0 or F1          both concern the same file and the same decision**

**Verify before you trust.** Re-run the measurement rather than trusting this document:

```
cd SENTINEL_PRIME\08_SELF_IMPROVEMENT
python survey_build.py
```

Every number in this package comes from `_BUILD_SURVEY.json`, and the survey is regenerable. If a
number here disagrees with the survey, **the survey is right and this document is stale.**

**And per the operator's standing rule: hand results to a `verifier` before calling anything done.**
Self-measurement is not verification.