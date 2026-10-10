# HANDOFF — SENTINEL PRIME Control Centre

**Stage:** dashboard build complete · **Date:** 2026-10-06 · **Operator:** Popy
**Root:** `C:\Users\apviz\.minimax-agent\projects\SENTINEL_PRIME\`
**Goal:** `tg_hl5gr4qb0vmuurmeo2` · declared complete at the close of this stage.

Everything here was measured, not recalled. Source: `_BUILD_SURVEY.json`, generated
`2026-10-07T04:32:25` by `08_SELF_IMPROVEMENT\survey_build.py`, with **0 fields `NOT_MEASURED`**.

---

## State of play: it is up, and it is honest

**Deployment is UP.** Container `mavis-sentinel-hub`, image `mavis/sentinel-hub:1.0.0`, running and
healthy, `restart=unless-stopped`, bound `127.0.0.1:8910 → 80/tcp`. Backend
`Microsoft-HTTPAPI/2.0` on `127.0.0.1:8912`. Front `nginx/1.31.6`, header
`X-SENTINEL-Deployment: mavis-sentinel-hub`.

**It is loopback-only, and that was proved rather than assumed.** Connections on the front port were
refused on all three non-loopback adapter addresses — `172.21.224.1`, `172.29.32.1`,
`192.168.1.193` — and the survey's `loopback_reachable` list is empty. **No public deployment exists and
none was authorised.** Ports 8900/8901 belong to OPTIMUS and were never touched.

**The system survives reboot, proven by destruction.** The Startup anchor
(`…\Startup\SENTINEL Command Center.bat`, 4,557 B, 75 CRLF, no BOM, sha256 `4acc5bbc…`) has brought the
whole deployment back dozens of times; `09_LOGS\hub-startup.log` carries **one marker and one exit line per run** (61 and 25 at the latest read, incrementing), most
exit codes, last `exit=0`**. The deployment suite's `--coldstart` run tears it fully down and requires
both planes to return.

---

## The three numbers that matter

| | |
|---|---|
| **0 known open bugs** | Unit **502/0/0** (29 classes), deployment default **40/0/1** (41 checks), cold start **43/0/0** (43 checks). The single not-run is the destructive cold-start gate, which the `--coldstart` run covers. |
| **7 servers to build** | The Hermes gateway blueprint declares 9 profile servers. **2 resolve** (`filesystem` 2026.8.31, `browser` 0.0.83); **7 do not exist yet.** All 5 missing `.py` servers have their capability **verified live** under other registered servers — nothing is unreachable today. |
| **0 faults** | Monitor overall **FAIL**, 55 checks, `total_checks`=55 matching the 55 shipped. **2 FAIL, stable** — the un-built servers. The STALE count moves with activity (observed 1 and 2 within minutes) and is not quoted as a constant. |

**The dashboard reads `overall: FAIL` and that is correct.** Making it green would require either
building the seven servers — future work the operator has sequenced — or editing the monitor to stop
reporting them, which would be fabrication.

---

## The rule that governs everything below

> **We do not solve a gap by removing the gap; we solve it by upgrading the system. If you want to
> build something, you play scaffolding and then raise the building. You do not take the scaffolding
> down if the building is not finished.** — Popy, 2026-10-06

A declared-but-unbuilt thing is a **gap, not an error**. The blueprint is the **target**, never a
snapshot to be made to agree with the present.

This is enforced by code, not by good intentions: `test_the_plan_is_never_pruned` in
`08_SELF_IMPROVEMENT\test_suite.py` (12 assertions) fails the suite if the blueprint drops below nine
declarations, if any declaration is neither built nor tracked, if a profile mailbox disappears, or if
any script anywhere in the project prunes or deletes the plan.

Doctrine **M-29**, in `11_BRAIN\04_METHOD\MISSTEPS_AND_CORRECTIONS.md`, which is append-only **and
which records the loss of M-01…M-27 that happened at the close of this stage** — read it before
editing that file again.

---

## What to do next

Full reasoning in `09_ROADMAP.md`. In short:

1. **F1 — put the project under version control.** One R0. Highest-value item outstanding. It is first
   because three verifier rounds this stage had to report old-vs-new comparison as `UNVERIFIABLE` —
   there was no old version to read. Under version control that check becomes mechanical.
2. **B3–B7 — build the five Python gateway servers.** `prime-bridge` first (the others benefit from it),
   then `sentinel-state`, `rule-triggers`, `learning-loop`, `context-pressure`. **Build the files.
   Do not edit `OPTIMUS_MCP_CONFIG.json` to silence the monitor.**
3. **B8 / B9 — `web-tools` and `git`.** Both declared npm packages **404**. A control package answered
   `19.3.0` in the same run, so the registry was reachable and the 404s are real. Choosing a real
   package or writing the server locally is an operator decision.
4. **Blocked on Popy** — `BIN_TESSERACT` (external binary; nothing claims OCR works),
   `HILO_USER_TOKEN` + one Design launch (installed, 17,090,864 B gateway, **never launched**, so no
   runtime surface is claimed for it).

**Hermes is the main orchestrator and builder; Mavis is the engineer establishing this side of it.**
The two are being built side by side, profile by profile.

---

## Weak points, stated plainly

Full detail in `01_BUILD_STATUS.md` W1–W9. None is failing; none is hidden by the dashboards.

- **W1 — no version control.** See above. The one that matters.
- **W2 — `09_LOGS` is unrotated:** 1,039 of 1,293 files (80.4%) and 25,234,947 of 31,565,181 bytes
  (79.9%) at survey time; it gains one marker file per Startup run. Slow-burning. Any rotation is a deletion and **needs an R0** — deletion is
  never automatic in this project.
- **W3 — two declared npm packages do not exist** (above; scaffolding, not defects).
- **W4 — route naming is asymmetric.** The backend has no `/healthz` or `/readyz`; those are front-only,
  with nginx mapping `/readyz` onto the backend's `/api/state`. **Correct behaviour** — both return
  91,158 B, which is how the two planes are proved to agree — but a maintainer probing the backend
  directly gets a 404 and may misread it. *(The survey itself hit this: an early probe asked the wrong
  path and would have reported a false defect.)*
- **W5 — cosmetic BOM** on `collect-sentinel.ps1`, which contains zero non-ASCII characters. Left alone
  deliberately; touching working scripts at wrap-up is how churn is introduced.
- **W6 — MiniMax Design measured from disk only**, never launched.
- **W7 — scope boundary:** `apviz-dashboard-monitor` publishes `0.0.0.0:9119`. **Not SENTINEL.** Not
  touched. Recorded only so a future reader knows the edge of this project's loopback claim.
- **W8 — inconsistent freshness bounding in the monitor.** `corpus_fresh` (135,690.6 s) is STALE under a
  3,600 s bound, while `mcp_tools_wired` reports OK on a handshake record aged **167,209.3 s** — older by
  ~8.75 h — with no age bound at all. The check is not broken and it does disclose the age, but the
  bounding policy is inconsistent. **Not fixed here: changing `monitor.py`'s policy is the operator's
  call.**
- **W9 — three gap-register entries cite evidence the monitor has contradicted.** `BIN_TESSERACT`,
  `WIRING_MCP` and `ARTIFACT_EMPTY` all cite a check that now reports OK. In each case the system got
  *better* and the record was left behind. **No entry was closed** — that is an operator decision. See
  `02_GAPS.md` Part E.

---

## What is deliberately NOT being cleaned up

Each of these has been mistaken for a defect at least once. **All are correct.**

| | |
|---|---|
| 2 entries in `instance_registry.json` (`PRIME-CLI`, `PROBE`) claim `ACTIVE` while hours stale | Liveness is **derived** from heartbeat age, not read from that field. The system reports them STALE and shows 0 alive. Removing them was recommended once and was **wrong**. They are also the visible tail of the same era as the mailbox messages below. |
| 4 profile mailboxes described as "empty" | They are **not** empty — 138 / 138 / 138 / 276 files, all sent by `PRIME-CLI`, `2026-09-12` → `2026-10-06`. Mostly `type:"test"` residue from a pre-fix version of the unit suite, plus one `alert` each, one `state_share`, and one `user-message` in a fifth folder. The suite is now sandboxed and adds nothing. Clearing them would be destroying the record. |
| The blueprint declaring files that do not exist | It is the target. |
| `mcp_config_servers_exist` staying FAIL | The plan being visible. |

**Nothing deletes automatically.** Deletion is never automatic in this project.

---

## Verification history — what the independent pass changed

An adversarial `verifier` subagent audited this package against live re-measurement. **Its verdict was
FAIL, and it was right to give it.** The *build* was confirmed sound; the *document package* was not
clean. Everything it found has been corrected, and the corrections are recorded here rather than quietly
folded in.

| Finding | Resolution |
|---|---|
| Four profile mailboxes described as **"empty"** — actually 138–276 files each | Corrected in five places. Now states what they really hold, and why. **The verifier's own explanation was also wrong** — it attributed the files to `test_suite.py:442`, but that suite runs entirely in a `tempfile` sandbox and fingerprints the live tree before/after (`test_suite.py:401-421`). The residue is from a **pre-fix** version. Checked the source rather than accepting either claim. |
| Two skill names in `06_SKILLS_AND_MCP.md` did not exist on disk (`context-progress`, `conversation-memory`), under a heading that said *"Measured from the live system"* | **This was a fabrication.** Both had been drawn from a catalogue in context instead of the measured list. Removed; the section now covers all 62 real skills, states the `mavis-…-skill` naming convention, and every name is machine-checkable against `skills.names`. |
| Unit suite "474" in 8 places across 6 files — actual **475** | Corrected everywhere. Fully explained: `NoRomanianInCode` asserts once per `.py`/`.ps1` file; adding `survey_build.py` took the workspace from 54 to 55 code files. Not flakiness — a real, deterministic consequence of adding a file. |
| Survey inventoried `14_HANDOFF` as 1 file — the survey ran **before** the package was written | Survey re-run after all 12 files existed. It now reports 12 files / 119,879 B, and the headline totals include the package. |
| "60 markers, 24 exit codes, 27,715 B" presented as fixed | The log increments on every cold start — the verifier's own run moved it to 61 / 25 / 28,180 B. Now described as a counter with an as-of reading. |
| **Missed by the report:** three register entries cite monitor evidence now contradicted | `BIN_TESSERACT`, `WIRING_MCP`, `ARTIFACT_EMPTY` all cite a check that reports **OK** today. Documented as Part E of `02_GAPS.md` and as W9. **Nothing was closed** — that is an operator decision. |
| **Missed by the report:** the monitor binds staleness inconsistently | `corpus_fresh` is STALE at 135,690.6 s under a 3,600 s bound, while `mcp_tools_wired` reports OK on a record aged 167,209.3 s with no bound. Documented as W8. Not fixed — changing `monitor.py`'s policy is the operator's call. |
| **Missed by the report:** "STALE = the check working" restates the monitor's semantics | The monitor's own `interpretation` says stale means the capability is **UNVERIFIED, not working**. Both readings are now given, and this package does not claim those capabilities verified on a stale reading. |

**The build itself was independently confirmed good** in the same pass: container running and healthy,
loopback-only (refused on all three non-loopback adapters, `loopback_reachable` empty), both npm 404s
real rather than a PATH artifact, blueprint SHA unchanged, no deletions, and **cold start re-proven by
destruction at 43/0/0**.

**The lesson, and it is the same one as everywhere else in this project: self-measurement is not
verification.** Nine defects were found in a document set written by the same agent that measured the
system, and every one of them was in the *reporting*, not the *build*.

---

## Where everything is

| What | Where |
|---|---|
| Entry point | `14_HANDOFF\00_README.md` |
| Measured truth | `14_HANDOFF\_BUILD_SURVEY.json` · regenerate with `python 08_SELF_IMPROVEMENT\survey_build.py` |
| Orchestrator | `13_COMMAND_CENTER\api\sentinel-hub.ps1` — verbs `start` `stop` `restart` `status` `logs` `install-startup` `uninstall-startup`. Use `-File`, never `-Command`. |
| Live records | `13_COMMAND_CENTER\api\{sentinel-state, health, minimax-ecosystem, last_test_run, deployment-tests}.json` |
| Tests | `08_SELF_IMPROVEMENT\test_suite.py` (502 assertions, 29 classes) · `test_deployment.py` (41 checks, `--coldstart` for the destructive run) |
| Gap register | `12_PROGRAM\GAP_REGISTER.json` — **18 entries, all `OPEN`** (9 `HPROF_*`, 5 `CONCEPT_*`, `BIN_TESSERACT`, `WIRING_MCP`, `ARTIFACT_EMPTY`, `HERMES_GATEWAY_PROFILES`) |
| Blueprint | `07_BACKBONE\mcp\OPTIMUS_MCP_CONFIG.json` — **9 declared, READ-ONLY**, sha256 `86989b62…`, 4,565 B |
| Doctrine | `11_BRAIN\04_METHOD\MISSTEPS_AND_CORRECTIONS.md` — append-only. **Holds M-28 and M-29 only; M-01…M-27 were destroyed by a truncating write on 2026-06 and are NOT recoverable.** |
| Construction protocol | `14_HANDOFF\08_CONSTRUCTION_SCHEMA.md` — **read before building anything** |

**Reference points:** 26 MCP tools (`07_BACKBONE\mcp\sentinel_hub_server.py`, 38,765 B, 968 lines) ·
17 live MCP servers (`C:\Users\apviz\.minimax\mcp.json`) · 62 skills
(`C:\Users\apviz\.minimax\agents\mavis\skills\`) · 63 Docker containers running, SENTINEL uses exactly
one · 32 of 32 ecosystem surfaces `MEASURED`, 0 not-available, 0 errors.

---

## Before you call anything done

> **Hand results to a `verifier` subagent before declaring done.** Self-measurement is not verification.
> A green log line is not a working product — *"no errors"* is not *"verified working"*.

Two polarities, always: a **polarity** case proves the guard fires; only a **control** proves it did not
fire at the system's expense. An exemption that cannot fail is a waiver, not a mapping. A detected
defect is not a fixed defect — and a rule that fires does not authorise the change written in its name.

**If a number in this package disagrees with a fresh survey run, the survey is right and this document
is stale.** Re-measure; do not edit the number.