# 02 — Gaps: BUGS and SCAFFOLDING

Every open item in the build, sorted into the two categories that mean different things.

The distinction is the operator's, and it is the most useful distinction in the project:

> **A bug is obvious and makes no sense in the system. Scaffolding raises the question of what is
> missing.** A bug is something that has gone wrong. Scaffolding is a piece of the building that has
> not been raised yet. Different stories altogether.

**A bug** gets fixed. **Scaffolding** gets built — and never removed.

Source of truth: `12_PROGRAM\GAP_REGISTER.json` (18 entries) plus the monitor's non-OK checks.
All 18 register entries are currently `OPEN`.

---

## PART A — SCAFFOLDING (9 entries)

Not faults. Declared work that has not been built. Each one closes by **constructing the thing**.

### A1 — The nine Hermes gateway profiles

**The design, stated by the operator:** the Hermes gateway is to carry **one server per Hermes profile
— nine profiles, nine servers**. Each is infrastructure that has to be created in Hermes.

Full plan: `12_PROGRAM\HERMES_GATEWAY_PROFILE_PLAN.md`. All nine are registered as individual
`HPROF_*` tickets so each can be built and closed on its own.

**Measured state of the nine:**

| # | Declared server | Kind | Measured state |
|---|---|---|---|
| 1 | `filesystem` | npm | **resolves** — `@modelcontextprotocol/server-filesystem 2026.8.31` |
| 2 | `browser` | npm | **resolves** — `@playwright/mcp 0.0.83` |
| 3 | `prime-bridge` | python | not constructed — `prime_bridge_server.py` absent |
| 4 | `sentinel-state` | python | not constructed — `sentinel_state_server.py` absent |
| 5 | `rule-triggers` | python | not constructed — `rule_triggers_server.py` absent |
| 6 | `learning-loop` | python | not constructed — `learning_loop_server.py` absent |
| 7 | `context-pressure` | python | not constructed — `context_pressure_server.py` absent |
| 8 | `web-tools` | npm | **package does not resolve** — `@modelcontextprotocol/server-fetch` 404 |
| 9 | `git` | npm | **package does not resolve** — `@modelcontextprotocol/server-git` 404 |

**So: 2 of 9 resolve, 7 to build.** The blueprint is unmodified — SHA256 `86989B62…`, 4,565 bytes,
mtime 2026-09-12. It was not edited to make anything look finished.

**A note on the two dead packages.** These are *scaffolding with a broken dependency name attached*.
They are not defects in the build — they are the one place where the plan itself names something that
does not exist upstream. Building them requires choosing a real package (or writing the server), which
is an operator decision. Until then the declaration stays, because deleting it would delete the
requirement.

### A2 — The four Hermes profile mailboxes (scaffolding, present and populated by history)

**Measured — all four exist, and none of them is empty:**

| Profile | Files | Bytes | Contents |
|---|---|---|---|
| `SENTINEL-DESKTOP` | 276 | 58,403 | 274 `test` · 1 `alert` · 1 `state_share` |
| `SENTINEL-COWORK` | 138 | 29,077 | 137 `test` · 1 `alert` |
| `SENTINEL-CHAT` | 138 | 28,801 | 137 `test` · 1 `alert` |
| `CODER-APP` | 138 | 28,249 | 137 `test` · 1 `alert` |

Every one of those messages was sent by **`PRIME-CLI`**, spanning `2026-09-12T15:18:09` →
`2026-10-06T15:56:28`. A fifth folder, `20261001_234648_c2d562\`, holds one `user-message` from the
same sender.

**What that history actually is — and this corrects an earlier draft of this document, which called
these mailboxes "empty". They are not.**

The overwhelming majority are `type: "test"`: the residue of an **older version of the unit suite**
that wrote cross-instance messages into production state. That defect was found and fixed. The current
`test_cross_instance` runs entirely inside a `tempfile.TemporaryDirectory` sandbox, binds
`CrossInstance(instance_id='PRIME-CLI', root=sandbox)`, and fingerprints the live state tree before and
after to prove it is byte-identical (`test_suite.py:401-421`). **Proof the fix holds:** the newest
message in all four mailboxes is `2026-10-06T15:56:28`, and the unit suite has been run repeatedly since
then — including two full runs during independent verification tonight — without adding a single file.

**So they are not empty, and they are not purely test residue.** Each mailbox also carries one `alert`,
`SENTINEL-DESKTOP` carries one `state_share`, and the separate folder holds one `user-message`. These
are the historical record of the one instance that ever spoke.

This also explains the stale `PRIME-CLI` entry in `instance_registry.json` (Part D): it is the residue
of that era, not evidence of a running instance. **Deleting the mailboxes or the registry entry would
be destroying the history** — and deletion is never automatic here.

No Hermes profile has been configured yet, which the operator has deferred: *"the swarm is under
construction; we have not yet set up the other Hermes profiles."* Each profile still needs its gateway
server (A1) and then a heartbeat under its own name.

### A3 — Concepts designed but not implemented

Five register entries. All are **documentation-only by design**, and each says so in its own
`fix_requires` field:

| ID | What | Measured |
|---|---|---|
| `CONCEPT_C18` | Partnership protocol | doctrine exists, implementation does not |
| `CONCEPT_C19` | 3-Propozitii ritual as an invocable command | described, not wired to a command |
| `CONCEPT_C21` | Context pressure monitor | partially implemented, not surfaced |
| `CONCEPT_C23` | Historical cultures corpus | correctly a corpus, not a program |
| `CONCEPT_C24` | 963 Hz / SACRU proverbs | doctrine only |

**`CONCEPT_C24` carries an honest finding that should not be lost:** the source file is a *25-axis
decision matrix*, not a 963-proverb enumeration, and its per-proverb attributions are flagged in-file
as fabricated by an earlier agent. The register records this rather than repeating the claim.

---

## PART B — BUGS

### Zero open bugs

**No bug is currently known to be open.** This is a claim, so here is its basis:

- Unit suite: **502 passed / 0 failed / 0 skipped** (29 classes). The two newest classes are
  `AppendOnlyIntegrity` and `Project references resolve`, both added after the doctrine loss — see W10
  and W11.
- Deployment suite, default run: **40 passed / 0 failed / 1 not-run** (41 checks, run
  `2026-10-06T22:56:00`) — the not-run is `startup_cold_start`, which requires the destructive flag.
- Deployment suite, `--coldstart` run: **43 passed / 0 failed / 0 not-run** (43 checks, most recent,
  `2026-10-06T23:2x`). Both are green. `deployment-tests.json` records whichever ran last, so it
  currently holds the 43/0/0 cold-start result, not the 40/0/1 default.
- The monitor's non-OK checks are **two scaffolding items and at most one staleness signal**.
  See below. None is a fault.

That is not the same as "no bugs exist". It is: none are known, and the systems that would reveal them
are running and passing.

---

## PART C — The monitor's non-OK checks, explained

These are the only red and amber signals on the dashboard. Each is accounted for.

**This set moves — and it moved while this paragraph was being written.** The STALE count was observed at
**2**, then **1** after the bimodal workflow state was touched, then **2** again. A number that changes
that fast does not belong in a document as a fixed claim. So: **the two FAILs are the stable signal** and
the STALE is a live reading. Quote the FAILs; re-measure the rest.

55 checks, `total_checks`=55 matching the 55 actually shipped, overall **FAIL**.

| Check | Status | Measured value vs bound | What it actually is |
|---|---|---|---|
| `mcp_config_servers_exist` | **FAIL — stable** | 5 referenced `.py` servers, 5 missing | **Scaffolding.** Its own evidence adds: all 5 capabilities are *verified live* under other registered servers and 0 are uncovered, so nothing is unreachable — the separate server files are simply not built yet. |
| `mcp_npx_packages_resolve` | **FAIL — stable** | 2 of 4 declared npm packages resolve | **Scaffolding.** A registry control package answered `19.3.0` in the same run, so the registry was reachable and the two 404s are real. |
| `corpus_fresh` | **STALE — persistent** | ~152,000 s vs bound `< 3600s` | **Correct behaviour.** The corpus is a frozen extraction snapshot, older than its bound *because the conversation moved on*. This one does not self-clear mid-session, because nothing re-extracts the corpus while we work. |
| `workflow_state_fresh` | **STALE — intermittent** | varies; bound `< 300s` | **Correct behaviour, and the reason the STALE total moves.** It measures how long since the bimodal workflow last wrote its state. Writing that state clears it; a stretch of authoring without it brings the STALE back. It is the check working, not a fault. |

Neither FAIL is currently a reason to change anything. Both are the to-do list, correctly reported.
No STALE is a fault either: each is an honest signal that something has not been touched recently.

**A precise note on what `STALE` means, because a reader should not have to guess.** `health.json` carries
its own interpretation string: *"OK means every check ran and passed. **DEGRADED** means at least one check
could not run or **is stale — the capability is UNVERIFIED, not working.** FAIL means at least one
measured value is out of bounds."*

So by the monitor's own semantics, a STALE check means the capability is **UNVERIFIED** — not that it is
broken, and not that it is confirmed working. Saying "the check is working" describes the *check*; saying
"the capability is verified" would describe something the monitor explicitly refuses to claim. Both of the
STALE capabilities here are genuinely exercised elsewhere — the corpus by the collector, the workflow by
this session's own MODE_B — but this report does not claim them verified on the strength of a stale
reading.

**A note on the dashboard being `FAIL` overall.** That is the correct state of this build, and it should
not be made green. Green would require either building the seven missing servers — which is future work
the operator has sequenced — or editing the monitor to stop reporting them, which would be fabrication.

---

## PART D — Things that are neither, and must not be "fixed"

Recorded because they have all been mistaken for defects at least once in this project's history.

| Item | Why it looks wrong | Why it is not |
|---|---|---|
| 2 stale entries in `instance_registry.json` (`PRIME-CLI`, `PROBE`) claiming `status: ACTIVE` | They claim to be active and are hours stale | Liveness is **derived** from heartbeat age, not read from that field. `sentinel_cross_instance_active` reports them STALE and correctly shows 0 alive. The claim in the file is a writer's leftover; the system does not trust it. Removing them was recommended once and was **wrong**. |
| 4 profile mailboxes described as "empty" | They are **not** empty — 138–276 files each | **Correction.** They hold the message history of `PRIME-CLI`, mostly `type:"test"` residue from a pre-fix version of the unit suite, plus one `alert` each, one `state_share`, and one `user-message` in a fifth folder. See A2. |
| `mcp_config_servers_exist` staying FAIL | A red on the dashboard | It is the plan being visible. Turning it green without building the servers would be fabrication. |
| Blueprint declaring files that do not exist | Stale config | It is the target, not a snapshot. |

---

## PART E — Three register entries whose stated evidence is no longer true

Found by independent verification, not by inspection. Each entry is still `OPEN`, but **the evidence it
cites has been contradicted by the monitor since the entry was written.** They are not bugs in the
build and not scaffolding — they are **stale records**, and the honest thing is to say so rather than to
repeat them as current.

| Entry | What the entry claims | What the monitor says now |
|---|---|---|
| `BIN_TESSERACT` | "OCR engine not on PATH", evidence: *monitor.py `bin_tesseract` check* | **`bin_tesseract` = OK.** Found at `C:\Users\apviz\AppData\Local\TesseractOCR\tesseract.exe`, `found_via: known_location` — located, not assumed. |
| `WIRING_MCP` | "no Hermes handshake has been performed; monitor reports `mcp_tools_wired` as **NOT_RUN**" | **`mcp_tools_wired` = OK.** 26 tools returned over stdio; probe `sentinel_confirm_identity` `ok=True`, arguments arrived. |
| `ARTIFACT_EMPTY` | "**50 empty result files** in `09_LOGS/scraped`" | **`logs_empty_artifacts` = OK.** 154 artefacts inspected, **0 empty**, 0 unreadable, 1 navigation-only target that has no content by definition. |

**What this does and does not mean.** It does **not** mean the build regressed — every one of these is a
case where the system got *better* and the record was left behind. It means the register is no longer a
reliable index of what is outstanding, and an agent reading it cold would be misled on all three points.

**No change has been made.** Closing a register entry is an operator decision, and per the project's
standing rule nothing is deleted or rewritten automatically. What is required is either a re-verification
pass over each entry's evidence or an explicit decision to close them.

The nine `HPROF_*` entries and `HERMES_GATEWAY_PROFILES` were written this session against live
measurement and are not affected.

---

## The count, plainly

- **9 scaffolding gaps** — 7 Hermes gateway servers to build, plus the profiles that need them.
- **0 known open bugs.**
- **Monitor signals** — **2 scaffolding FAIL (stable)** plus **1–2 honest STALE depending on recent
  activity**. The FAILs are the number to quote; the STALE count moves and is documented as moving.
- **9 register entries outside the profile plan** — external dependency (`BIN_TESSERACT`), MCP wiring
  (`WIRING_MCP`), architecture (`HERMES_GATEWAY_PROFILES`, the umbrella that spawned the nine
  `HPROF_*` tickets), the five `CONCEPT_*` entries of A3, and log artifacts (`ARTIFACT_EMPTY`).
  All `OPEN`.
- **3 of those 9 carry evidence the monitor has since contradicted** — see Part E. Stale records, not
  build faults, and deliberately left for an operator decision.

Deletion is never automatic in this project. `ARTIFACT_EMPTY` in particular says so in its own record:
*"explicit operator decision — deletion is never automatic."*