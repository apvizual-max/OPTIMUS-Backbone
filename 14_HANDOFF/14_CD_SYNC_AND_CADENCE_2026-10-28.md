# 14 — CD sync, the push gate, and a daemon running at a sixth of its declared rate

**What this is.** The second pass of the takeover, on Popy's instruction: check the
GitHub state before pushing, synchronise with the continuous pipeline's work, push,
and then keep improving the build — gaps, errors, bugs, silent failures,
misalignments, the monitors and the daemons.

**Owner:** Popy. **Author:** Mavis (agent). **Date:** 2026-10-28, 08:40–10:10.

---

## 1. The push gate, measured before anything was pushed

Popy's instruction: GitHub is worked on by the continuous pipeline (Optimus CD), so
check whether GitHub is ahead of the local tree before pushing, and merge if it is.

| | measured | how |
|---|---|---|
| `origin/main` | `7cf6d4b4a6002d5581a93258661ecb1bfc0f2499` | `git ls-remote origin refs/heads/main` |
| local `main` | `ea249604f6361214703c86844b9123b4eaf580e1` | `git rev-parse main` |
| ahead / behind | **0 behind / 6 ahead** | `git rev-list --left-right --count origin/main...HEAD` |
| is `origin/main` an ancestor of local? | **YES** | `git merge-base --is-ancestor origin/main HEAD` → exit 0 |
| branches (local / remote) | `main` / `origin`, `origin/main` — one branch | `git branch`, `git branch -r` |
| open PRs | **0** | `gh pr list --state open` |
| PRs total | **59** — 36 MERGED, 23 CLOSED | `gh pr list --state all --json number,mergedAt` |

**Verdict: the local tree is not behind. Nothing to merge from GitHub.** The local
`main` contains `origin/main` and six commits on top of it, so a push is a
fast-forward on the remote, not a reconciliation.

### The 23 PRs that were closed without merge

These are the pipeline's work that never landed. Each was compared against the local
tree, file by file, blob by blob — not by title, because the pipeline opens competing
PRs for the same item and merges the best one while closing the duplicates.

The pipeline's two **security** findings are in this tree, merged:

- **#5** — arbitrary code execution in `git_tools_server` → MERGED
- **#9** — path traversal in `SelfModifyEngine` → MERGED

The 23 unmerged ones were all code health, test coverage and micro-performance. The
ones whose change was still missing were **taken** (see §3); the ones a merged PR had
already superseded were not, because taking them would have re-applied what the
pipeline had already decided against.

The pipeline's scratch files (`patch.diff`, `plan.txt`, `benchmark_test.py`,
`09_LOGS/scraped/*`, its own `pr_desc.md`) were left where they were: they are the
pipeline's working files, not project code, and `09_LOGS/scraped` is a runtime
artefact directory the project already tracks.

## 2. The mirror: `.github-repo` was six commits behind

Popy requires `.github-repo` to be the continuous pipeline's synchronised build
location. Measured before the push: HEAD `7cf6d4b` (= the old `origin/main`),
`dirty=0`, 1 514 files. It was therefore **six commits behind** the local tree, and
would have made the pipeline build from a stale base. It is fast-forwarded to the
new `main` after the push, and the check is repeated there: same SHA as `main`,
`dirty=0`, same file count.

## 3. What was taken from the pipeline, and what was left

| PR | change | decision |
|---|---|---|
| #50 | `monitor.py` rebuilt a list of packages for every candidate it tested — a quadratic membership test | **TAKEN** — now a set |
| #26 | the hub wrote its event log with a blocking `open()` inside an async tool handler | **TAKEN** — now `asyncio.to_thread` |
| #28 | three regexes recompiled for every script and every line of it | **TAKEN** — compiled once, outside the loop |
| #27 | unused `Callable` in `monitor.py` | superseded — the file uses it now |
| #33 | unused imports in `build_program_matrix.py` | superseded — that file was rewritten today |
| #2, #56 | split a long test method | already merged as #56 |
| #19, #23 | type hints on two scripts | not worth the churn; the files changed since |
| 10 test-coverage PRs | error-path tests for the servers | the merged set already covers the same paths |
| 14 hygiene PRs | unused imports | superseded by the sweep below |

**A local sweep replaced the waiting.** 47 Python files scanned with `ast`: **20
unused imports across 14 files**, removed in one pass — each with a byte-faithful
`.bak`, each re-parsed afterwards to prove it still compiles, and the whole thing
re-proven by both suites. `from __future__ import annotations` was excluded: it is a
compiler directive, not an import, and a scanner cannot tell the difference.

## 4. The defect: a daemon at a sixth of its declared rate

**This is the find of the pass, and it is in a daemon, not in the dashboard.**

The refresh worker in `13_COMMAND_CENTER\api\server.ps1` exists to refresh the MCP
handshake record every hour, so the 24 hour freshness bound on `mcp_tools_wired` is
met by the system instead of by a human remembering. Measured on 2026-10-28, the
record refreshed every **5 hours 54 minutes**:

- the counter that drives the handshake sat inside the block that runs every
  **fourth** cycle, while the divisor that turned a counter into a period was
  computed **per** cycle — a factor of four;
- and a cycle outlasts its sleep (the collector takes about 12 s on top of a 25 s
  sleep), so one and a half times more.

The arithmetic matches the clock exactly: the record was written at `02:53:13` and
the next one at `08:47:50`.

**Why the dashboard stayed green.** Two instruments, each doing its job, neither able
to see the other. The 24 hour bound was met — with a 4x margin, and a bound met with
a 4x margin is not the bound anybody wrote down. And the worker's log recorded its
**start** and nothing else, so the gap was invisible from the worker's side as well.
What was missing was the comparison between the period the code **declared** and the
period the system **delivered**.

**The fix.** The cadence is now a wall-clock deadline
(`((Get-Date) - $lastHandshakeAt).TotalSeconds -ge $handshakePeriodSeconds`), and the
gate sits **outside** the every-fourth-cycle block, so neither the cost of a cycle nor
the nesting can multiply it. Every refresh is now written to the worker's log, so the
cadence is a record and not an assumption.

**The control, falsified before it was trusted.** The deployment check that guarded
this loop asserted that a period was *computed* and inside the bound. It passed the
whole time the period was six times longer than written down, because the formula was
present and the shape around it was not. The check now asserts the **shape** — a
wall-clock deadline, a gate outside the four-cycle block — and carries a control that
must **reject** the old cycle-count form. Run against the previous `server.ps1` it
reports FAIL; against the fixed one, PASS.

### The log line was a second lie, and it is now fixed too

The worker's own log records the cadence it starts with. Both lines are in
`09_LOGS\refresh-worker.log`:

```
[2026-10-28T02:53:13] refresh worker started: every 25s, ecosystem every 4th cycle, handshake every 144 cycle(s)
[2026-10-28T09:28:29] refresh worker started: every 25s, ecosystem every 4th cycle, handshake every 3600s (wall clock)
[2026-10-28T09:28:31] handshake refreshed (startup)
```

The old line announced **144 cycles** — the divisor. The period the system actually
delivered was **576 cycles** (144 × the four-cycle block), and at the measured ~37 s
per cycle that is the 5h54m measured on the clock. The log was therefore announcing
the number the code computed and not the number the system delivered — the same
class of error as the check that passed while the period was six times too long, in
the place where an operator would have looked for the answer. The new line announces
the delivered period, and the third line is the proof that the refresh is a record
and not an intention.

### The second defect: the branch that exists to stop the system lying had no test

After the hub source was edited (the log write moved into a thread), the handshake
record stopped describing the server as it stands, and the monitor said **`STALE`**.
The unit suite went from **607 passed / 0 failed** to **605 passed / 2 failed** — not
because the monitor was wrong, but because the suite's model of the verdict was
written as `'OK' if justified else 'FAIL'`, a two-valued expression that cannot name
a third answer. The monitor has four verdicts; the suite knew two.

**`STALE` is the verdict that exists to stop the system claiming the tools are wired
when the code has moved on, and it was the one branch no test reached on purpose.**
It was reached only by an accident, and the accident was reported as a broken
handshake — a wrong accusation of a healthy system.

Three things changed:

1. The suite's model derives the verdict from the facts the monitor reads — the
   record's content, its age, and the server's mtime against the record's — and names
   all four verdicts.
2. A new class, **`McpHandshakeStale`**, reaches `STALE` deliberately, on a synthetic
   workspace where the source is dated three days back, so each staleness trigger
   fires **alone**: superseded by a later edit, and expired against the 24h bound.
   Its control is falsified in both directions — against a monitor with the `STALE`
   branch removed it reports 2 reds, and against a monitor that answers `STALE` to
   everything it reports 2 reds.
3. The **liveness** of the live record moved to where it belongs: a new deployment
   phase, `handshake_record_is_current`, holds the record's **age** against twice the
   daemon's refresh period (7200 s against a declared 3600 s). The old cadence
   reached 21240 s — 5.9x — so the bound separates the two regimes. That is the
   outcome the panel's "wired" claim rests on, and it was the part nothing measured.


## 5. Measured state after this pass

| | value | when |
|---|---|---|
| `test_suite.py` | see §7 | |
| `test_deployment.py` | see §7 | |
| handshake cadence | declared 3600 s, wall clock | **live since 09:28:29** — the worker's log line and the startup refresh are in `09_LOGS\refresh-worker.log` |
| handshake verdict | `STALE` whenever the hub source is newer than the record | **OK** after the re-measure at 09:28:31 — `record_age_seconds 99.5`, `record_superseded_by_server_edit false` |
| `McpHandshakeStale` | did not exist | **5 assertions**, control falsified in both directions (2 reds against each mutant) |
| `LogsParseAgeIndependent` | did not exist | **6 assertions**, control falsified against the mutant with the age condition restored (2 reds) |
| `logs_parse` | parsed only while the artefact was under 1 hour old — so in the normal state it never parsed | **unconditional**, with an unreadable artefact reported instead of raising |
| who writes the `logs` artefacts | only the test suites and operator actions | measured: all seven written **09:24:16–09:24:28** by the unit suite; the daemon writes none |
| `handshake_record_is_current` | did not exist | new deployment phase — bound 7200 s against a declared 3600 s |
| npm membership test | O(n) set, not O(n²) list rebuild | 2026-10-28 |
| hub log write | `asyncio.to_thread`, not a blocking open | 2026-10-28 |
| unused imports | **0** left in the project sweep (3 `__future__` directives excluded) | 2026-10-28 |
| live dashboard after the restart | 13 tabs, **0 console messages**, 12 requests all 2xx, `DEGRADED · 54 ok / 0 fail / 2 stale / 0 not-run` | 09:29, re-measured |
| deployment | `healthz` 200, `readyz` 200, `/api/health` 200, backend pid 29300 | after the restart through `sentinel-hub.ps1 restart` |

## 6. What the next instance should know

1. **The push gate has a real procedure now, and it is written down here**: check
   `origin/main` against local `main` with `merge-base --is-ancestor`, list the PRs
   with `gh pr list --state all --json number,mergedAt`, and compare every
   unmerged PR's blobs against the tree before deciding it is superseded. A title is
   not evidence.
2. **The pipeline's closed PRs are not garbage**: 23 of them were still unapplied
   code-health work. Two more were still open in the tree. The sweep in §3 is how to
   find them without waiting for a PR.
3. **A period that is derived must be compared with the period that is delivered.**
   The new check is `handshake_refresh_period_is_wall_clock`, and it can be run
   against any copy of `server.ps1`.
4. **The worker's log is now a cadence record.** `09_LOGS\refresh-worker.log` carries
   a line per refresh, so a gap is visible without waiting for a bound to lapse.
5. **A number in a log line is not a measurement.** The old startup line said
   "handshake every 144 cycle(s)" while the delivered period was 576 cycles. If a log
   line announces a period, check it against a timestamp before believing it.
6. **The monitor has four verdicts, not two: `OK`, `FAIL`, `STALE`, `NOT_RUN`.**
   `STALE` means the measurement is real but too old to speak about the code as it
   stands. It is not a failure, and it is not a success — and before 2026-10-28 no
   test reached it on purpose.
7. **`sentinel-cc.ps1` is the live launcher**, not a leftover: `sentinel-hub.ps1`
   starts and stops the backend through it, and after the restart its `.pid` held
   the new pid (29300) and its `.log` was rewritten. The `.pid` / `.log` /
   `.err.log` files were stale only because the backend had been started by another
   path (the guardian). **Do not quarantine them.**
8. **`sentinel-hub.ps1 restart` prints everything it has to print, but an
   invocation that waits on the process tree does not come back.** Measured on
   28 Oct: the command produced its full output (up to `DEPLOYMENT UP`), the
   deployment was then verified live — `healthz` / `readyz` / `api/health` all
   200, backend pid 29300 — and the invocation still had not returned after
   600 s. The reason is that the backend it starts is a long-lived process inside
   that tree. Run it backgrounded, or with the output redirected to a file.
   This is **not** a defect in the instrument: the launcher already redirects the
   child's output (`-RedirectStandardOutput $LOG_FILE`) and disposes the .NET
   process object precisely so that it does not hang on its own.


## 7. Suite results

Both suites were run **sequentially**, never concurrently, against the tree committed
as `aa49c72` and against the live system after the restart — and then re-run after the
second repair (the `logs_parse` one, §8).

| suite | result | when |
|---|---|---|
| `08_SELF_IMPROVEMENT\test_suite.py` | **612 passed / 0 failed / 0 skipped** | 09:26 |
| `08_SELF_IMPROVEMENT\test_suite.py` | **618 passed / 0 failed / 0 skipped** | 10:00 |
| `08_SELF_IMPROVEMENT\test_deployment.py` | **74 passed / 0 failed / 1 not-run (75 checks)** | 09:34 |
| `08_SELF_IMPROVEMENT\test_deployment.py` | **74 passed / 0 failed / 1 not-run (75 checks)** | 10:10 |

The unit suite went **607 → 612 → 618**. The five extra assertions in the first
step are the class `McpHandshakeStale`, which reaches `STALE` deliberately —
where nothing had reached it before. The six in the second are
`LogsParseAgeIndependent`, which reaches the corrupt-file path that the old
parse could never take.

The single `not-run` in the deployment suite is **`startup_cold_start`**, and it is
destructive by design: it tears the deployment down to prove the Startup entry
brings it back. Its own record says so — *"destructive: re-run with --coldstart"*.
It is not a gap and it is not a failure.

Two of the new deployment checks, as they were measured:

```
[ok] handshake_record_is_current: handshake record age 252s, rewritten by the daemon every 3600s (bound 7200s)
[ok] handshake_record_control_discriminates: the same predicate refuses a record aged past the bound, so this check measures the age and not the presence of a file
```

The live system, measured after the restart:

| | value |
|---|---|
| `GET /healthz`, `/readyz`, `/api/health` | **200 / 200 / 200** |
| health checks | **56 total — 54 OK, 0 FAIL, 2 STALE, 0 NOT_RUN** |
| the 2 STALE | `corpus_fresh` (1 990 002 s ≈ 23 days, by design — the corpus is a snapshot) and `workflow_state_fresh` (620 s, written on demand). Neither is the handshake. |
| `mcp_tools_wired` | **OK** — 26 tools over the wire, probe ok, `record_age_seconds 99.5`, `record_superseded_by_server_edit false` |
| open gaps served | **6**, and the ledger holds 6 — the `gap_count_matches_ledger` phase reads the two numbers against each other, not against a constant |
| live page | **13 tabs**, **0 console messages**, 12 requests all 2xx, `DEGRADED · 54 ok / 0 fail / 2 stale / 0 not-run` |

## 8. The third defect: the check that catches a corrupt state file had not opened it

**The `logs` family of the monitor holds seven artefacts and one integrity check
over the three JSON ones.** The check is `logs_parse`, and its own evidence reads
*"every state JSON must parse; a corrupt state file is a silent failure"*, with
the bound *"no parse errors"*.

The parse was wrapped in `if a < MAX_STATE_AGE` — **one hour**. The three
artefacts (`bimodal_state.json`, `orchestrator_state.json`,
`performance_metrics.json`) are written **on demand**: by the test suites and by
operator actions. Nothing else writes them — the collector says so explicitly
about `bimodal_state.json`: *"this script only reads it. Two writers would"* be
a problem.

**Measured.** All seven `logs` artefacts were last written between **09:24:16
and 09:24:28** — by the unit suite — and the daemon writes none of them. So on a
machine that is simply running, those files are routinely older than an hour,
and the check was, in the normal state of the system, **reporting OK for state
files it had never opened**. The sibling `log_*` check was reporting the same
file as STALE at the same moment: one report said *"this file is too old to
trust"* and *"this file is valid"* without having looked at it.

**The payoff, stated honestly: nothing was actually corrupt.** All three
artefacts parse today, and so do the live `sentinel-state.json`, `health.json`
and `mcp_handshake.json`. No corruption was being hidden — the control simply
had never done its job. That is the harder case, because a control that is off
in the normal state is indistinguishable, in the output, from a control that has
nothing to report.

**The fix.** The age was removed from the parse. Validity does not expire, and
the freshness verdict is already carried, with its own bound, by the sibling
`log_*` check — so **no bound was moved and no check was deleted**. An
unreadable artefact is now reported as a parse error instead of being allowed
to escape: an escaping exception would turn the whole family into NOT_RUN and
hide the other six artefacts with it.

| | before | after |
|---|---|---|
| the parse | only while the artefact was under 1 hour old | on every artefact, whatever its age |
| a corrupt state file older than an hour | **OK** — never opened | **FAIL**, and named in the evidence |
| a valid state file older than an hour | OK | OK — age is not corruption |
| the freshness verdict of the same file | STALE | STALE, same bound — no bound moved |
| an unreadable artefact | raised → the whole family NOT_RUN | reported as a parse error; the other six still checked |

**The control, falsified before it was trusted.** The new class
`LogsParseAgeIndependent` was run against a mutant of the monitor with the age
condition put back: **2 assertions go red** — the corrupt old file reads OK and
the evidence list is empty. Against the repaired monitor: **6/6**.

**What the sweep did not find.** The same shape — a control conditioned on a
property unrelated to its claim — was looked for across the project: `monitor.py`
and the collector were swept for age-gated conditions. The only remaining ones
are the freshness verdicts themselves, which is what they are for. No other
inert control of this class was found.

## 9. The writer map, re-measured by cadence — and the two rows that were wrong

The writer→artefact table in `11_SESSION_HANDOFF_2026-10-28.md` §4 is the
reference every freshness bound in the monitor hangs on. It was measured at
03:00 on 28 Oct. It has been **re-measured at 10:03–10:04**, by cadence rather
than by reading the code: two samples 52 s apart, and the difference in mtimes.

| Artefact | A scris în fereastra de 52 s? | Cadența observată | Scriitorul real | Cum e dovedit |
|---|---|---|---|---|
| `health.json` | da | ~25 s | worker-ul de refresh (`server.ps1`) | avansează o dată pe ciclu |
| `sentinel-state.json` | da | ~25 s | worker | idem |
| `state-history.jsonl` | da | ~25 s | worker | idem |
| `minimax-ecosystem.json` | **nu** | ~100 s (al 4-lea ciclu) | worker | neatins în 52 s, dar scris la fiecare al 4-lea ciclu |
| `guardian.log` | **da** | **~45 s** | **guardianul EXTERN** — `projects\scripts\sentinel-guardian.ps1`, task `OPTIMUS_SentinelGuardian`, pid 9976 | `server.ps1` nu conține niciun cuvânt „guardian", iar mtime-ul coincide cu timestamp-ul **propriei ultime linii** (10:03:00 → 10:04:31) |
| `refresh-worker.log` | nu | la fiecare refresh de handshake (oră) | worker | neatins în 52 s; ultima intrare la 09:28:31 |

**The row that was wrong.** The map said the refresh worker writes
`guardian.log`. It does not — and the proof does not depend on reading the
other repository: the worker cannot write a file whose name does not appear in
it, and `guardian.log`'s mtime is its own content timestamp.

**And the same map carried the same lie about the handshake.** Its row said the
record was rewritten *"at 144 cycles (~1 hour)"*. 144 was the **divisor**; the
delivered period was 144 × 4 = **576 cycles = 5h54m** (§4). The map repeated the
defect it was meant to describe — a period read off a number in the code instead
of off the clock. It is corrected there, and it now says 3600 s on the wall
clock, which is what the code does since the fix.

### Where the anchors that keep the deployment alive actually live

| Mecanism | Unde e codul | Starea măsurată |
|---|---|---|
| ancora de Startup (`.bat`) | generată de `sentinel-hub.ps1 install-startup` | prezentă, 4557 B, scrisă 2026-10-06 — și **validă față de codul de azi**: conține `-Action start -FrontPort 8910 -BackPort 8912` și `-File "%SENTINEL_HUB%"`, adică exact cheile pe care installerul le verifică înainte de a scrie |
| `OPTIMUS_SentinelGuardian` | `projects\scripts\sentinel-guardian.ps1` — repo **exterior** (HEAD `9c35528`, curat) | Running, pid 9976, scrie `guardian.log` la ~45 s |
| `OPTIMUS_ControlCenter` | `projects\scripts\cc-watchdog.ps1` — același repo exterior | Running, pid 10024 |
| `sentinel-cc.ps1 install-task` | **în acest repo** | **nu a fost rulat** — taskul `SENTINEL_CommandCenter` **nu există** pe mașină |

**Nu e o nealiniere ascunsă:** repo-ul documentează explicit că `install-task` nu
a fost rulat, ca decizie a lui Popy (`11_PLANS\DEPLOYMENT_GAP_CLOSURE.md`: *„is
not run … Popy's call"*). Dar e un fapt structural de reținut: **codul care ține
deploymentul viu trăiește în alt repository**, iar o clonă a acestui repo nu
conține ancorele de activare — doar mecanismul de a le instala.


