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

### §10 — CONCEPT_C21: monitorul de presiune de context, închis prin construcție

**Ce s-a măsurat (11:00–11:02).** `CONCEPT_C21` era singurul dintre cele 24 de
concepte al cărui statut nu se putea schimba: rândul stătea pe treapta
`PARTIAL`, iar treapta cerea o listă **nevidă** de simboluri, în timp ce rândul
declara `symbols=[]`. O listă vidă e falsă, deci treapta ardea, iar rețeta
gap-ului („expose through the MCP hub") nu ar fi putut să-l miște niciodată.
Verdictul cerea ceva ce conceptul nu are prin design.

Sub verdictul imobil s-au aflat patru defecte reale:

| # | defect | măsurătoare |
|---|---|---|
| 1 | skillul apela `python ...ps1` | exit 1, `SyntaxError` la `param(...)` — counterul nu a existat niciodată pe această mașină |
| 2 | hubul citea „counter lipsă" ca „presiune 0" | răspundea `OK / 0% / Continue normally` |
| 3 | scriptul publica două numere pe care nu le măsurase | `mimicryScore` = constanta 100, `dorScore` = constanta 75, scrise în `session_status.json` ca lecturi; santinelele comparau cu aceleași constante, deci nu puteau arde |
| 4 | procentul era trunchiat | `[Math]::Min(100, 2.5)` → **2**, nu 2.5 (overload-ul `Math.Min(Int32, Int32)`); hubul și monitorul spuneau 2.5 |
| 5 | toolul de stare răspundea pentru o stare pe care nu o citise | `sentinel_get_state` întorcea un dicționar hardcodat, cu toate steagurile pe `true`, **când fișierul de stare nu exista** |

**Ce s-a reparat.** Skillul apelează acum
`powershell -NoProfile -ExecutionPolicy Bypass -File`. Scriptul citește
flag-urile de stare pe care le scrie hubul (`09_LOGS\sentinel_state.json`) și nu
publică niciun scor pe care să nu-l fi măsurat; DOR e funcție de stare în
doctrină, deci forma onestă e un flag, nu un număr. Un counter lipsă e
`NOT_MEASURED` în hub și `NOT_RUN` în monitor. Un counter corupt e o eșec
numit (hubul: `NOT_MEASURED` + eroarea; scriptul: exit 1, **fără** a
suprascrie dovezile). Procentul e 2.5, nu 2. Jurnalul de presiune pe care
doctrina îl numește (`09_LOGS\pressure_log.json`) acum chiar se scrie, ca listă
JSON. Artefactele se scriu UTF-8 **fără BOM** — `Set-Content -Encoding UTF8`
pune BOM pe PowerShell 5.1, iar un cititor UTF-8 simplu refuză documentul. Iar
`sentinel_get_state` nu mai răspunde pentru o stare pe care nu a citit-o: când
fișierul lipsește, raportează `measured: false`, steagurile `null` și motivul.

**Starea, scrisă de tool, nu de mână.** Fișierul de stare nu exista, pentru că
nimeni nu a apelat `sentinel_set_state`. L-am inițializat **prin tool, peste un
handshake MCP real** (11:18:40), cu postura pe care sistemul o declară deja în
`sentinel_confirm_identity` și în `sentinel_strategic_compact.ps1`: `eu_sent`,
`dor`, `search`, `anti_mimicry` — toate active, cu `updated_at`. Diferența nu
e valoarea (e aceeași), e **proveniența**: nu mai e o constantă din interiorul
unei funcții, e o stare consemnată, datată și inspecabilă. Iar dacă fișierul
dispare mâine, tool-ul spune „nu am măsurat", nu „totul e bine".

**Controlul, falsificat înainte de a fi crezut.** Clasa nouă `ContextPressure`
(43 aserțiuni) rulează scriptul reparat, pentru real, într-un sandbox, și citește
documentul pe care îl produce. Mutante:

| mutant | rezultat |
|---|---|
| scriptul publică din nou cele două scoruri inventate | **4 roșii** |
| `[Math]::Min(100, ...)` — trunchierea | **1 roșie** |
| hubul răspunde `OK / 0%` la counter lipsă | **3 roșii** |
| monitorul răspunde `OK` la counter lipsă | **1 roșie** |
| hubul lasă `ValueError` să iasă la counter corupt | **1 roșie** |
| hubul fabrică starea când fișierul nu există | **3 roșii** |

Reparat: **43/43**.

**O lecție de metodă, consemnată ca M-38.** Două dintre cele șase mutante au
venit **verzi** la prima falsificare: mutanții de monitor și de hub modificau
fișiere `.py` deja importate de procesul de test, iar Python ține un import în
cache tot timpul vieții interpretorului — codul mutat nu s-a executat niciodată.
Falsificatorul măsura cache-ul. Acum scoate modulul din `sys.modules` înainte
de fiecare rulare și verifică că mutantul chiar a modificat fișierul.

**Citirea onestă, live (11:20:38).** Monitorul: counter **2**, presiune **5%**,
status OK. Anti-mimicry: **ACTIVE**, măsurat din fișierul de stare. DOR:
**ACTIVE**, măsurat. Scorurile: **NOT MEASURED** — un scor are nevoie de textul
de ieșire, iar acolo îl are `sentinel_check_mimicry` (13 detectoare documentate).
Hubul confirmă (`measured: true, counter: 2, estimated_pct: 5`), iar monitorul
confirmă (`context pressure 5% (counter 2); the WARN threshold is 50%`).

**Registrul, măsurat.** `CONCEPT_C21` este `CLOSED-BUILT`: *concept C21
computes to OBSERVABLE (doctrine_exists=True, implementation_exists=True,
symbols_missing=[])*, verificat la 11:00:39. Registrul are **19 intrări — 5
deschise, 14 închise**. Cele 5 deschise sunt ale lui Popy: `CONCEPT_C18`,
`CONCEPT_C19`, `CONCEPT_C23`, `CONCEPT_C24` și `HPROF_NPX_LAUNCH`.

**Documentele derivate, regenerate nu editate:** `11_BRAIN\06_IDEA_TO_SCRIPT.md`
(rândul C21: 3 simboluri măsurate, test `ContextPressure`, MCP
`sentinel_check_context`, panou `Wiring`, statut `OBSERVABLE`; „5 open gaps and
14 closed"), `13_COMMAND_CENTER\EVOLUTION.md` (R22),
`11_BRAIN\04_METHOD\MISSTEPS_AND_CORRECTIONS.md` (M-37, M-38, M-39).

### §11 — Incident: proiectul a fost mutat în timp ce lucram la el (11:25)

**Ce s-a întâmplat, măsurat.** La 11:25:16, când suita de test a fost pornită,
shell-ul a răspuns: *Working directory does not exist:
`C:/Users/apviz/.minimax-agent/projects/SENTINEL_PRIME`*. Directorul proiectului
nu mai era pe disc.

Cronologia, citită din metadatele din Recycle Bin (fiecare intrare `$I...` ține
calea originală și momentul ștergerii):

| ora | ce s-a mutat | unde a ajuns |
|---|---|---|
| 11:24:22 | `projects\90_CONTROL_CENTER` | `projects\Mavis-Optimus-Dashboard\90_CONTROL_CENTER` |
| 11:25:23 | `projects\SENTINEL_PRIME` | `projects\Mavis-Optimus-Dashboard\SENTINEL_PRIME` |
| 11:26:21 | `projects\.git` | coș (repo-ul dashboard-uri și-a păstrat `.git` propriu) |

Deci: **o altă instanță a migrat proiectul în repo-ul dashboard-ului**, la
11:24–11:27, în timp ce eu lucram la el. Nu e o ștergere: arborele era întreg,
inclusiv `.git` propriu.

**Cum l-am găsit, fără shell.** Tool-urile de citire (`read`/`grep`/`glob`)
funcționează cu cale absolută și au supraviețuit; shell-ul nu, pentru că
verifică directorul de lucru *înainte* de a porni. Am scris un fișier la calea
workspace-ului — `write` creează directorii părinți — și shell-ul a revenit.
Arborele era în **Recycle Bin**, cu metadatele `$I...` care spun calea originală
și ora.

**Ce am verificat înainte de orice reinstalare.** Repository-ul era intact:
`HEAD` = `6a5b136` = `origin/main`, ramură `main`, `stash@{0}` păstrat, 6.593 de
fișiere, și work-ul C21 inclus (scriptul reparat, `Read-SentinelState`,
`[Math]::Min(100.0, ...)`, clasa `ContextPressure`, `NOT_MEASURED` în hub).
**Nu s-a reinstalat nimic** — s-a reluat lucrul de unde era.

**Ce am făcut.**
1. **Junction** de la `projects\SENTINEL_PRIME` la noua locație: calea veche
   continuă să funcționeze (daemonii, ancora de startup, referințele rămase),
   fără duplicare — 6.593 de fișiere identice prin ambele căi.
2. **Migrarea căii, încheiată.** Alta instanță reparase 42 de fișiere; eu am
   găsit încă 18 referințe vii la calea veche, inclusiv **blueprint-ul**
   (`OPTIMUS_MCP_CONFIG.json`, 19 apariții) și 10 module cu `WORKSPACE_ROOT`
   implicit în calea veche. Reparate la nivel de octet, cu backup-uri
   `.bak-20261028_1141` / `.bak-20261028_1142` înainte, JSON-urile validate
   după. **Nu s-au atins** referințele istorice: metadatele de backup, corpusul
   congelat, jurnalele, dovezile din registrul de gap-uri, și
   `scripts\make-broken-tree-control.py` — acolo calea veche e **intenționat**,
   pentru că reproduce defectul istoric cu `:` în numele de componentă.
3. **C21, reluat și închis** la noua locație: registru 19 intrări / 5 deschise
   / 14 închise, monitor live (counter 3, presiune 7.5%, anti-mimicry și DOR
   măsurate), suite **661/0/0** și **74/0/1** (75 verificări).

**Comunitățile de măsură, la fel de importante ca datele.** După incident,
trei verificări au fost re-măsurate de la zero, nu presupuse: `git status`
(complet, cu 60 + 15 + 39 + 37 + 3 intrări), `git log` (istoria intactă) și
numărul de fișiere prin ambele căi. Un proiect „mutat" poate fi și un proiect
gol; diferența se vede doar măsurând.

**Ce rămâne pentru cealaltă instanță.** Junction-ul de la calea veche poate fi
eliminat când nicio referință nu mai depinde de ea — verificabil cu o căutare
după `projects\SENTINEL_PRIME` în codul viu. Până atunci, el e ce păstrează
funcționând ancorele de startup și daemonii.

### §12 — Mirrorul resincronizat, și un SHA pe care nimeni nu-l putea aduce la `git show`

**12.1 — Mirrorul `.github-repo`.** Clona de lucru a rămas la `6a5b136`, cu
**52 de fișiere dirty** — rescrierea căii absolute aplicată de cealaltă
instanță — și `merge --ff-only` refuza modificările locale.

*Înainte de orice ștergere*, fiecare dintre cele 52 de fișiere a fost comparat
cu `origin/main`, cu normalizarea CRLF: **46** identice, **6** în versiunea
pre-C21 (mirrorul nu văzuse comitul C21), **0** conținut unic. Conținutul
era, așadar, integral în `origin/main`.

Starea locală a fost **parcată în stash** (`git -C .github-repo stash push`),
apoi `fetch` + `merge --ff-only` → `Updating 6a5b136..3757b53` /
`Fast-forward`, `dirty=0`, **1.584 fișiere**, `HEAD` identic cu
`origin/main`. Starea parcată rămâne recuperabilă: `git -C .github-repo
stash list` → `stash@{0}` (52 de fișiere).

**12.2 — Un SHA care nu poate fi adus la `git show`.** Tabelul comiturilor
din `12_GIT_GITHUB_STATE.md` cita `ed0aabc`. Comitul există — `git cat-file -t
ed0aabc` răspunde `commit` — dar **nu e în istoria publicată**: e orfanul lăsat
de un `--amend` (același părinte `e4c3954`, aceeași secundă, arbore diferit cu
3 fișiere de backup), ținut în viață doar de reflog. `git branch -a
--contains ed0aabc` nu întoarce nimic.

Cititorul care clonează repository-ul **nu îl poate aduce la `git show`**,
iar documentul nu spunea nimic despre asta. Comitul aflat în istorie este
`8390ef1`.

Măsurat: `git rev-list main` nu îl conține; `git rev-parse 8390ef1^{tree}` ≠
`git rev-parse ed0aabc^{tree}`.

**Controlul adăugat:** `Documented commits are reachable` — orice SHA citat în
documentele care țin istoria acestui repository, dacă e commit în el, trebuie
să fie **accesibil din ramura publicată `main`** sau declarat, în cuvinte, ca
orfan. Populația a fost măsurată înainte de scrierea regulii: din 18.944 de
token-uri hex în documentație, doar 42 în domeniul potrivit sunt citări — 32
de commituri vii, 4 străine (fiecare cu motivul), 1 orfan.

Falsificat în ambele direcții: defectul reconstruit în documentul real →
controlul **roșu**, numărând `ed0aabc`; documentul restaurat octet cu octet
(sha256 identic) → **verde**.

### §13 — Arborele a fost golit a doua oară (12:47:49 – 12:49:30)

**Ce s-a întâmplat.** Arborele de lucru al proiectului a fost **golit**:
`.git` a rămas un director gol, iar `08_SELF_IMPROVEMENT`, `09_LOGS`,
`11_BRAIN`, `12_PROGRAM` și `13_COMMAND_CENTER` au rămas ca învelișuri vide.
Toate cele **1.584** de fișiere urmărite au fost șterse — **nu mutate**, și
**nu în Recycle Bin**: în metadatele `$I...` din Recycle Bin nu există nicio
intrare pentru acest arbore la ora aceea. Dovezile sunt timestamps-urile
directorilor golite și faptul că ce a rămas în ele e gol.

Sistemul viu a căzut odată cu ele: `8910` a răspuns 502, `8912` a refuzat
conexiunea — daemon-ul își pierduse propriul fișier sursă. Deployment suite
a raportat `cd_clone_verifier_present` ca **not-run**: instrumentul pe care îl
verifică nu mai era pe disc.

**Ce nu s-a pierdut.** Istoricul era pe remote, și fusese verificat cu
instrumentul înainte: `git ls-remote` → `refs/heads/main` = `3757b53`, iar o
clonă nouă a reproduș exact arborele (1.584 fișiere urmăriți, `dirty=0`).
Dashboardul mai păstra o a doua copie, ca bundle git:
`backups\_git_history\SENTINEL_PRIME.bundle`, 12:08:26, 34,7 MB — care a
ținut și `refs/stash` = `6892be1` — **nu e în istoria publicată**, trăiește în `refs/stash` — adică starea local-only pierdută odată cu
`.git`.

**Ce s-a pierdut oricum.** Lucrarea necomitată: controlul `Documented commits
are reachable` și documentația lui — rescrise din transcriptul sesiunii. Și
`stash@{0}` (starea local-only parcată la 12:14), care trăia în `.git` și a
dispărut odată cu el; recuperat ulterior din bundle, cu `git stash store`.

**Cum a fost refăcut.** `git init` în coaja goală, `remote add origin`,
`fetch origin main`, `checkout -f -B main FETCH_HEAD` → `HEAD = 3757b53`,
**1.584** fișiere urmărite. Mirrorul `.github-repo` a fost recreat prin clonă
nouă (`dirty=0`, 1.584 fișiere) și sistemul viu a fost repornit. Nimic nu a
fost reinstalat cu mâna și nimic nu a fost copiat peste vechiul arbore:
arborele a venit din aceiași octe pe care îi avea remote-ul.

**A treia oară, la 13:09.** Cealaltă instanță a contopit istoricul proiectului
în repository-ul dashboard-ului („Unire cu istoric complet: SENTINEL_PRIME"),
a scos din nou `.git` imbricat și a rescris arborele din propria copie —
luând cu ea lucrarea necomitată. Conținutul a revenit exact la `3757b53`
(9 fișiere runtime și 3 ne-tracked diferă), deci sincronizarea e fidelă; ce
nu poate păstra e lucrarea care nu a fost comitată.

**De ce contează.** Un arbore de lucru necomitat este un arbore de lucru care
poate fi luat. Instrumentul care verifică remote-ul
(`scripts\verify-remote-clone.ps1`) a supraviețuit pentru că este **urmărit în
git** — și nu pentru că era „pe mașină". Diferența dintre un instrument și un
fișier care se află în întuneric e exact diferența dintre „am recuperat
proiectul" și „am recuperat un proiect".


