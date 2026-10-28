# 01 — Build Status

**Survey:** `2026-10-07T04:32:25` (regenerated after this package was written, so the package itself
is included in the inventory) · all figures from `_BUILD_SURVEY.json`.

**One line:** the control centre is deployed, running, self-healing across reboot, and green on both
test suites. Seven declared Hermes gateway servers are not built. Nothing is broken.

---

## Verdict

| Dimension | State |
|---|---|
| Deployment | **UP** — container running and healthy, both planes answering |
| Cold start | **PROVEN** — 60 startup markers, last exit code `0` |
| Unit suite | **502 passed / 0 failed / 0 skipped**, 29 classes |
| Deployment suite | **40 passed / 0 failed / 1 not-run**, 41 checks _(default run)_ |
| Cold start | **43 passed / 0 failed / 0 not-run**, 43 checks _(`--coldstart`; this is what `deployment-tests.json` holds right now, being the most recent run)_ |
| Self-monitor | **overall FAIL** of 55: **2 FAIL, stable** — the un-built servers. The STALE count **moves** with activity (seen 1 and 2 within minutes) and is not a fixed figure. See `02_GAPS.md` Part C. |
| Ecosystem | **32 of 32 surfaces MEASURED**, 0 not-available, 0 errors |
| Hermes gateway | **2 of 9 servers resolve; 7 to build** — the main body of outstanding work |

The monitor reports `overall: FAIL`. That is correct and intended: two FAILs are the un-built gateway
servers, which are work to do, not faults.

---

## Strong points

These are the things that would be expensive to rebuild and are genuinely working.

1. **Dual anchoring actually works, and is proven by destruction.** The system was torn fully down and
   brought back by the Startup entry alone. That is not an inference — the deployment suite runs
   `--coldstart`, stops everything, invokes the Startup anchor, and requires both planes to return. It
   has passed on every run. The Startup log carries one marker and one exit line per run; both were
   **60 markers / 24 exit codes at the time of the survey**, and each further cold start increments
   them. Latest read: **61 markers, 25 exit lines, 28,180 B, last `exit=0`**. The count is a measure of
   how many times it has been proven, not a fixed property.

2. **Loopback confinement is measured, not assumed.** Three non-loopback adapter addresses
   (`172.21.224.1`, `172.29.32.1`, `192.168.1.193`) were connected to on the front port and **all three
   were refused**. `loopback_reachable` in the survey is an empty list. There is no reachable
   non-loopback surface belonging to this project.

3. **The image carries no data.** The container is a pure reverse proxy — `find` across the image
   finds no corpus and no state file. This is asserted every run (`image_has_no_data`). It means there
   is exactly one source of truth for state and no drift is possible between an image and a disk.

4. **The self-monitor is genuinely adversarial about itself.** Three rounds of independent adversarial
   verification were run against the inventory-integrity check. Round 1 found three defects, round 2
   found a fourth of the same class in the code round 2 had just written. All are fixed; round 3
   attempted 20+ refutations and none landed. The checks are known to be able to fail — that was
   demonstrated by deliberately breaking them, not assumed.

5. **Every number carries its own age and its own failure modes.** Where a surface could not be
   measured it reports `NOT_AVAILABLE`, never a healthy default. Where a scan was truncated it says so.
   A check that cannot run reports `NOT_RUN`, never `FAIL` — an offline machine has falsified nothing.

6. **Documentation is doctrine, not commentary.** `MISSTEPS_AND_CORRECTIONS.md` is append-only: each
   entry states what went wrong, why, and the correction now *in force*. It is the single most valuable
   asset in the project, because it is why the mistakes above were caught at all.

   **It also suffered a real loss at the close of this stage, and the number must be read carefully.**
   See W10 below. M-01 … M-27 (44,576 B / 673 lines) were destroyed by a truncating write on
   `2026-10-06`; the file now holds only M-28 and M-29 (**6,406 B / 97 lines**). **Do not cite the old figures.**

7. **The build reports its own weaknesses honestly.** The monitor's own evidence string says
   *"Rewriting or pruning the config is an operator decision"* — it does not pretend to have authority
   it does not have.

---

## Weak points

Stated plainly. None of these are hidden by the dashboards, and none are currently failing.

### W1 — The project is not under version control

**Measured:** the workspace is not a git repository. There is no commit history, no branch, no
revert path.

**Why it matters more than usual here:** the entire doctrine is append-only and integrity-dependent, and
three verifier rounds could not compare old against new logic because **there was no old version to
read**. One verifier round reported the old-vs-new regression check as `UNVERIFIABLE` for exactly this
reason. A bug introduced tonight is not currently reversible by anything except memory.

**This is the highest-value thing not yet done.**

### W2 — `09_LOGS` holds 4 of every 5 files and is not managed

**Measured at survey time (`2026-10-07T04:32:25`):** **1,039 of 1,293 files (80.4%)** and
**25,234,947 of 31,565,181 bytes (79.9%)** live in `09_LOGS`. The two percentages differ because the
directory holds many small files.

It holds scraped artifacts, historical state snapshots and the startup log. It grows without bound and
nothing rotates it. This is slow-burning, not urgent.

*`09_LOGS` grows by one marker file per Startup run, so its count moves every time the deployment
comes up. Every other figure here is a snapshot of the survey and is superseded by re-running it.*

### W3 — Two npm packages in the blueprint do not exist

**Measured live against the registry:** `@modelcontextprotocol/server-fetch` and
`@modelcontextprotocol/server-git` do not resolve. A control package (`19.3.0`) answered in the same
run, so the registry was reachable and the 404s are real.

Consequence: `npx -y @modelcontextprotocol/server-fetch` fails exactly the way the missing `.py` files
do — a declared capability that cannot start.

**These are part of the plan, not defects.** See `02_GAPS.md` — they are scaffolding with a broken
dependency name recorded against them.

### W4 — Route naming is asymmetric between the two planes

**Measured:** the backend serves `/`, `/api/state`, `/api/health`, `/api/minimax`, `/api/verify`,
`/api/corpus`. It has **no route named `/healthz` or `/readyz`**. Those two names exist only on the
container front, where nginx maps `/readyz` onto the backend's `/api/state`.

This is **correct behaviour, not a defect** — front `/readyz` and backend `/api/state` both return
`91,158` bytes, which is how the two planes are proved to agree. But a future maintainer who probes
the backend directly at `/readyz` gets a `404` and may read it as a fault. Documented here so it is
not rediscovered as one. *(This was caught in the survey itself: an early version of the probe asked
the wrong path and would have reported a false defect.)*

### W5 — One script carries an unnecessary byte-order mark

**Measured:** `13_COMMAND_CENTER\api\collect-sentinel.ps1` has a UTF-8 BOM while the other four
PowerShell scripts in the project do not. It contains **zero non-ASCII characters**, so the BOM is
currently harmless — and for a pure-ASCII file PowerShell 5.1 does not need it.

**Left in place deliberately.** It is cosmetic, and touching working scripts at wrap-up is how churn is
introduced. Recorded here so it is a known inconsistency rather than a surprise.

### W6 — MiniMax Design is measured but never exercised

**Measured:** installed at `%LOCALAPPDATA%\Programs\MiniMax Design\current\resources`, gateway bundle
`17,090,864` bytes, `external_api_conf.yaml` `2,867` bytes. The app **has never been launched**, so no
runtime surface is claimed for it, and no `HILO_USER_TOKEN` is provisioned.

Four surfaces in the ecosystem snapshot describe its cloud seam from the files on disk. They are
accurate *about the files*. They say nothing about a running Design, and the snapshot does not pretend
otherwise.

### W7 — One container in the wider environment is bound to all interfaces

**Measured:** `apviz-dashboard-monitor` publishes `0.0.0.0:9119` and `[::]:9119`. That container is
**not part of SENTINEL** and was not touched. Recorded only because the project takes loopback
confinement seriously enough that a future reader should know the boundary of this claim: SENTINEL's own
front is loopback-only; that container is somebody else's, and this project makes no claim about it.

### W8 — The monitor binds staleness on one artefact and not another

**Measured** (`health.json` @ `2026-10-06T23:29:39`): `corpus_fresh` reads **135,690.6 s** against a bound
of `< 3600 s` and is correctly reported **STALE**. In the same file, `mcp_tools_wired` reports **OK** on a
handshake record whose own `record_age_seconds` is **167,209.3 s — older than the corpus snapshot by
~31,500 s (~8.75 h) — and it carries no age bound at all.**

**Why it matters.** The monitor holds one artefact to a freshness bound and trusts a strictly older one
without one. A check that says "this is OK" on evidence that is 46 hours old is making a different, and
stronger, claim than the one it makes for the corpus. This is not a false reading today — the handshake
record's own `evidence` string does disclose the age (`"Measured 167209s ago by mcp_handshake.py, not
asserted here"`), and the capability genuinely works, as a live handshake re-run confirms. **It is an
inconsistency in the bounding policy, not a broken check.**

**Not fixed here.** Adding a bound is a change to `monitor.py`'s policy, which is a design decision and
belongs to the operator. Recorded so the next person sees it rather than inheriting it silently.

### W9 — Three gap-register entries cite evidence that has since been contradicted

**Measured:** `BIN_TESSERACT`, `WIRING_MCP` and `ARTIFACT_EMPTY` each cite a monitor check that now
reports **OK** where the entry says it reports a defect. In every case the system got *better* and the
record was left behind. The register is therefore no longer a reliable index of what is outstanding.

Full detail in `02_GAPS.md` Part E. **No entry was closed or rewritten** — that is an operator decision.

### W10 — The doctrine file was destroyed in this session, and W1 is why

**This is the most serious item in this document and it is stated first among the weak points for that
reason.**

**What happened.** At `2026-10-06T23:36:58`, appending an entry to
`11_BRAIN\04_METHOD\MISSTEPS_AND_CORRECTIONS.md` **overwrote it**. The file went from **44,576 bytes /
673 lines / 27 entries (M-01 … M-27)** to **2,912 bytes / 1 entry**. M-01 through M-27 are gone.
There is no version control in this project, no backup of this file, and Volume Shadow Copies are not
readable without elevation. The content is **not recoverable from disk.**

**The mechanism.** The append was `$entry` written as `[IO.File]::WriteAllText($f, $t + $entry, ...)`,
where `$t` — the existing content — had been read in a *previous* tool call and never read in this one.
Each shell call is a fresh process; variables do not persist. `$t` was `$null`, so the write wrote only
the new entry. **It raised no error. Exit code 0.** A truncating write and a correct write are
indistinguishable at the call site unless the resulting length is checked.

**Why this belongs under W1.** This project has carried "no version control" as the highest-value
outstanding item for weeks. This is the receipt. **The gap was not theoretical**, and the file that was
lost is the one the project describes as its most valuable asset.

**What survives, and what does not.** The *themes* survive in three places: the memory entries under
`C:\Users\apviz\.minimax\agents\mavis\memory\MEMORY.md`, the doctrine quotes inside this handoff package,
and the source comments in the code each lesson produced. What is gone is the narrative record — Popy's
corrections as written, in the order they happened.

**What must not happen next.** The tempting repair is to rewrite M-01 … M-27 from those summaries.
That would be the worst outcome available: it would manufacture a record of the operator's corrections
that he did not write, inside the one file whose entire value is that it is his verbatim.
**A doctrine file partly invented by an agent is worse than a short honest one.** If those entries
return, they return from Popy, or they are marked as reconstruction. **That decision is his, and it has
not been made.**

The loss is recorded in full in the surviving file as **M-29**, in the same append-only format as
everything else — because a record that hides its own damage is the last thing this project should
produce.

**Build impact at the time: none — and that was the uncomfortable part.** `test_suite.py:990` asserted only
that the file exists and is larger than 500 bytes, and the suite passed straight through a 92% content
loss. **A size threshold is not an integrity check** — the same lesson as M-24 and M-27, arriving in its
most expensive possible form.

**The guard now exists and is proven.** `AppendOnlyIntegrity` (28th class, 14 assertions) checks every
append-only record against an append-only baseline in
`08_SELF_IMPROVEMENT\integrity_baseline.jsonl`. A record may grow freely; it may never shrink or lose an
entry id. The baseline file is **append-only**, so accepting a loss by writing a new baseline record does
not absorb it — the old record keeps failing, and the loss stays visible.

**Proven against this incident, not just asserted.** The production checker `_integrity_violations` was
run against the pre-loss facts (44,576 B, entries M-01…M-27). It reported:

```
MISSTEPS_AND_CORRECTIONS.md: shrank - baseline recorded 44576 B, now 6406 B (38170 B lost)
MISSTEPS_AND_CORRECTIONS.md: entry ids absent that the baseline recorded -
  ['M-01', 'M-02', ... 'M-27']
```

**It would have caught this.** The suite also carries a polarity case that replays the incident on a
copy of the real file, and a control proving a record that only grows is still accepted — because a
guard that fires on everything is not a guard, it is a nuisance.

---

### W11 - A registry naming something that no longer exists reports itself as fine

**The class.** Three gap-register entries cite monitor evidence that has since been contradicted
(W9 above). Nothing was red; the record was simply wrong, and anyone following it would have been
misled. That is the general shape of a silent failure in an inventory-driven system: a stale reference
is indistinguishable from a correct one until someone follows it.

**Measured.** I swept every project path named in GAP_REGISTER.json,
IDEA_TO_SCRIPT_MATRIX.json, PROGRAM_SPEC.md, the three backend scripts and this whole handoff
package, and resolved each against disk. **No genuine dangling reference exists.** The only absent
files are the six the blueprint declares and that are not built yet (W3 / A1) and one conditional
input the code correctly guards.

**Now enforced, not just measured.** Project references resolve (29th class, 13 assertions) does
this on every run, and it classifies each reference into one of four buckets rather than a single
pass/fail:

| Bucket | Meaning |
|---|---|
| concrete | starts at a real top-level directory and is expected to exist \u2014 **asserted** |
| glob | a pattern such as CH_*.md, not a reference |
| optional | read behind a Test-Path guard nearby, so an absent file is a supported input |
| ragment | a partial path like  2_CHAPTERS\UNPLACED.md, relative to a parent named elsewhere |

**Every classification is derived, never hand-listed**, and each non-concrete bucket has a bound the
suite asserts on \u2014 so if the exemption set grows silently, the assertion is what notices. That is the
whole point: **an exemption nobody can see is a waiver.**

The one real exemption is the blueprint-declared unbuilt servers, computed by crossing
OPTIMUS_MCP_CONFIG.json with the disk, so a typo or a renamed file cannot enter it. When a declared
server is finally built the exemption disappears, which is harmless \u2014 an existing file passes anyway.

**Writing this cost two defects in the checker itself**, both caught by its own polarity cases: a
regex that truncated CH_*.md to CH_ and then reported its own truncated fragment as a missing file,
and a polarity fixture that created the very file it was asserting was absent. A checker that
manufactures defects out of its own pattern is worse than no checker, because it trains you to ignore
it.

---
## Numbers, for the record

| Thing | Value |
|---|---|
| Workspace (at survey time) | 15 directories · 1,293 files · 31,565,181 bytes — including this package, **12 files** in `14_HANDOFF` |
| Command Centre UI | `index.html`, 64,805 B, 1,178 lines, 12 tabs |
| Backend orchestrator | `sentinel-hub.ps1`, 32,713 B, 668 lines |
| Backend server | `server.ps1`, 27,374 B, 570 lines |
| SENTINEL MCP hub | `sentinel_hub_server.py`, 38,765 B, 968 lines, **26 tools** |
| Live MCP profile | **17 servers** (volatile — re-measure; a server can be added between runs) |
| Skills installed | **62** |
| Gap register | **18 entries, all OPEN** |
| Docker containers running | **63** (SENTINEL uses exactly one) |
| Ports owned by SENTINEL | `8910` (front), `8912` (backend) — both loopback |
| Startup anchor | 4,557 B, 75 CRLF, no BOM, sha256 `4acc5bbc…` |
| Startup log | 61 markers, 25 exit lines, 28,180 B, last `exit=0` _(increments on every cold start)_ |

`8900` and `8901` belong to OPTIMUS and were never touched by this project.