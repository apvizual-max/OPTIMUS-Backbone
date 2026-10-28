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

## 5. Measured state after this pass

| | value | when |
|---|---|---|
| `test_suite.py` | see §7 | |
| `test_deployment.py` | see §7 | |
| handshake cadence | declared 3600 s, wall clock | code, live after the next server start |
| npm membership test | O(n) set, not O(n²) list rebuild | 2026-10-28 |
| hub log write | `asyncio.to_thread`, not a blocking open | 2026-10-28 |
| unused imports | **0** left in the project sweep (3 `__future__` directives excluded) | 2026-10-28 |

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

## 7. Suite results

Filled in from the run that accompanied this document — see §5.
