# SENTINEL PRIME — Handoff Package

**Generated:** 2026-10-06 · **Stage:** dashboard build complete for this stage · **Owner:** Popy

This folder is the entry point for anyone — a person or an agent — picking SENTINEL up cold in a month.
It is written so that nothing here has to be taken on trust: every figure is measured, and the raw
measurement is included.

---

## The evidence policy this package follows

> **No claim in this folder is made from memory. Every number comes from
> `_BUILD_SURVEY.json`, which was produced by `08_SELF_IMPROVEMENT\survey_build.py` at the stated
> timestamp. Anything the survey could not measure is written `NOT_MEASURED`, never guessed.**

The survey reported **0 items as NOT_MEASURED**. Where something is genuinely unknown it is said to be
unknown in the text, not hidden by omission.

If you change the system and this folder becomes stale, re-run the survey rather than editing the
numbers by hand:

```
cd SENTINEL_PRIME\08_SELF_IMPROVEMENT
python survey_build.py
```

---

## Read in this order

| # | File | What it is for |
|---|---|---|
| 00 | this file | Orientation |
| **10** | **`10_PRIMING_PROMPT.md`** | **Start here for a new AI instance with zero memory and zero context. Copy it whole, paste it as the first message.** |
| **11** | **`11_SESSION_HANDOFF_2026-10-28.md`** | **The state as of the last session: what was found, what was fixed, what is left, what is Popy's decision.** |
| **12** | **`12_GIT_GITHUB_STATE.md`** | **Exact Git and GitHub state: branch, SHAs, what is pushed, who else writes to this repo, and the rules for pushing.** |
| **13** | **`13_GAP_REGISTER_AUDIT_2026-10-28.md`** | **The gap register, measured and repaired: why the ledger was three weeks stale, what the nine Hermes profile servers actually are, and why the tool that regenerates the ledger used to destroy it.** |
| **14** | **`14_CD_SYNC_AND_CADENCE_2026-10-28.md`** | **The GitHub synchronisation with the CD pipeline, and the two silent failures found in the live system: a handshake that refreshed every 5h54m instead of every hour, and a verdict branch with no test behind it.** |
| **—** | **`SKILLS/`** | **The 10 skills handed to the new instance, plus a manifest. Copies, so a fresh agent without a skills directory still has them.** |
| 01 | `01_BUILD_STATUS.md` | **Start here.** What is live, what is strong, what is weak. |
| 02 | `02_GAPS.md` | Every gap, sorted into **BUG** (went wrong) and **SCAFFOLDING** (not built yet). |
| 03 | `03_ARCHITECTURE_SPEC.md` | The system as actually built, with measured file sizes and routes. |
| 04 | `04_BLUEPRINTS.md` | The nine Hermes gateway profiles, and every future design. |
| 05 | `05_DEPENDENCIES.md` | Every external dependency, what it is, whether it resolves. |
| 06 | `06_SKILLS_AND_MCP.md` | The 26 SENTINEL tools (still 26 — re-measured 28 Oct), the live MCP profile, and the skill roster as it stood on 6 Oct. |
| 07 | `07_OPERATIONS.md` | How to run, stop, restart, test and troubleshoot this. |
| 08 | `08_CONSTRUCTION_SCHEMA.md` | **How to add work correctly.** Read before building anything. |
| 09 | `09_ROADMAP.md` | What comes next, in order, with dependencies between steps. |
| — | `HANDOFF.md` | The one-page state of play for the next session. |
| — | `00_INTRARE_HANDBOOK.md` | Handbook from the **6 Oct stage** (updated 10 Oct). It opens with "read this first" — **that order is superseded**: the current entry point is `10_PRIMING_PROMPT.md` above. Kept because it explains the project's *purpose* in a way nothing else does. |
| — | `Last_active_goal-28-10-2026.txt` | The goal of an **earlier** stage (UI maturation), kept as context for the long arc. It is **not** the current goal — the current one is the handoff itself. Valid UTF-8, no BOM; a terminal with the wrong codepage can make it look corrupted. |
| — | `_BUILD_SURVEY.json` | Raw measurement. 30,136 bytes. The source for every number above. |

**The `.bak-2026…` files in this folder are the session's backups**, kept per the
rule that an edited file keeps its previous version. They are not content and
are not part of the reading order; the same rule says nothing is deleted to
make a folder tidy.

### Nine things that changed after this package was written

- **2026-10-28 — the repository was broken for every Windows clone.** `origin/main`
  carried a top-level directory whose name was the project's own absolute path,
  and git refuses `:` in a path component. Repaired in commit `e89887f`, verified
  by a fresh clone. Details in `12_GIT_GITHUB_STATE.md` and in
  `07_BACKBONE\skills\sentinel-cd-pipeline-sync.SKILL.md`.
- **2026-10-28 — a continuous development pipeline now writes to `main` directly**
  (Antigravity CD Engine and `google-labs-jules[bot]`). There are no branches on
  the remote and **no CI** — `gh run list` is empty. The test suites have to be
  run by hand, sequentially. Details in `12_GIT_GITHUB_STATE.md`.
- **2026-10-28 — the health-check freshness bounds were measured, not guessed.**
  Which module writes each artifact, and on what trigger, is now mapped: the
  `log_*` family and `workflow_state_fresh` are written **on demand** (by the
  test suites and by operator actions), not by a timer. **The bounds were not
  widened** — a STALE on an on-demand artifact is the system telling the truth
  about age, and widening the bound would have hidden exactly that. `corpus_fresh`
  is ~22.8 days old against a 1-hour bound and stays STALE by design.
  The full writer-to-artifact table and the decision are in
  `11_SESSION_HANDOFF_2026-10-28.md` §4, with the ratified quotations that
  settle it.
- **2026-10-28 — the skills were refreshed with the closing block's lessons, and
  the copies in `SKILLS\` were regenerated from them.** The rule that came out of
  it: **a freshness bound needs a writer behind it — if there is none, add the
  writer; if the writer is on demand, keep the bound.** The copies are
  byte-identical to their sources, and the previous versions are in git history.
  `SKILLS\MANIFEST.md` says what each one now carries.
- **2026-10-28 — "verify the remote with a fresh clone" became an instrument.**
  `scripts\verify-remote-clone.ps1` measures ten things (invalid tree entries,
  a fresh clone from zero, `dirty=0`, probe HEAD equal to the remote SHA, one
  branch, the required files present) and prints `VERDICT=PASS` / `VERDICT=FAIL`
  — exit 0 / 2. It is **falsified, not merely passed**:
  `scripts\make-broken-tree-control.py` builds, on demand, a repository carrying
  the exact defect that broke this repo on 28 October, and the verifier has to
  refuse it. Measured: control → `VERDICT=FAIL` (`invalid_tree_entries 1`,
  `clone_exit 128`), real repository → `VERDICT=PASS`. Both directions are
  tested by the `cd_clone_verify` phase in
  `08_SELF_IMPROVEMENT\test_deployment.py`. **Run it after every pipeline push**
  — see `12_GIT_GITHUB_STATE.md` §6.
- **2026-10-28 — the gap register stopped being a ledger.** `12_PROGRAM\GAP_REGISTER.json`
  had not been written since **6 October**, and its nine `HPROF_*` entries still said the
  Hermes profile servers "are not yet constructed". Measured: all nine exist and answer
  a real MCP stdio handshake — 22 tools over stdio. The tool that regenerates the
  register used to **overwrite** it, and one run destroyed 11 of the 18 entries; it now
  merges, re-measures what it can measure, and preserves what it cannot. The ledger holds
  19 entries: **5 open, 14 closed**, each closed entry carrying the measurement that
  closed it. The control was falsified — red on the old builder, naming the 12 lost
  entries. Details in `13_GAP_REGISTER_AUDIT_2026-10-28.md`.
- **2026-10-28 — the context pressure monitor had never watched anything.**
  `CONCEPT_C21` was the only one of the 24 concepts whose status could not change: it sat
  on a rung that asked for a non-empty list of symbols while the row declared `symbols=[]`.
  Under that unchangeable verdict: the role skill invoked a `.ps1` with `python` (exit 1,
  `SyntaxError`), so the counter was never written; the hub read a missing counter as a
  pressure of zero and answered `OK / 0%`; the script published two scores it had never
  measured (`mimicryScore` = 100, `dorScore` = 75) as if they were readings; and
  `[Math]::Min(100, 2.5)` truncated the pressure figure to 2 while the hub and the monitor
  said 2.5. Repaired and re-measured: `CONCEPT_C21` is `CLOSED-BUILT` — the register now
  holds **5 open, 14 closed** — the live reading is counter 2 / 5% with anti-mimicry and
  DOR **measured** (the state file is now written, by the system's own tool, over a real
  MCP handshake), and the new class `ContextPressure` (43 assertions) was falsified against
  six mutants, each of which goes red. Details in R22 and in
  `14_CD_SYNC_AND_CADENCE_2026-10-28.md` §10.
- **2026-10-28 — a document cited a commit that no reader could reach.** The local-commit
  table in `12_GIT_GITHUB_STATE.md` named `ed0aabc`, a commit that exists in the
  repository but is **not in the published history**: it is the orphan left behind by an
  `--amend` (same parent, same second, different tree), kept alive only by the reflog.
  No branch contains it, so a reader who clones cannot `git show` it — and the document
  said nothing about that. Corrected to `8390ef1` (the commit that is in the history),
  and the new control `Documented commits are reachable`
  (`08_SELF_IMPROVEMENT\test_suite.py`) now requires every commit SHA cited in the
  project's own history documents to be reachable from the published branch `main` — or
  to be declared, in words, as an orphan. The scope was measured, not guessed: of 18,944
  hex tokens in the documentation, only 42 in the documents that record this
  repository's history are citations at all. The control is falsified in both
  directions. Details in R23 and in `14_CD_SYNC_AND_CADENCE_2026-10-28.md` §12.
- **2026-10-28 — the working tree was emptied, and the remote is why the project
  survived.** Between 12:47:49 and 12:49:30 the project's working tree was deleted:
  `.git` reduced to an empty directory, five project directories left as empty shells,
  all 1,584 tracked files gone, not moved and not in the Recycle Bin. The live daemon
  died with its own source file, and the deployment suite reported its clone-verifier
  as missing because the instrument was gone from the disk. Nothing that had been
  pushed was lost: the remote held `3757b53`, a fresh clone reproduced the tree
  exactly, and the tree was rebuilt from the remote with `git init` + `fetch` +
  `checkout -f` — 1,584 files, `HEAD` unchanged, the mirror recreated, the daemon
  restarted. The work that had **not** been committed was lost and had to be rewritten;
  so was `stash@{0}`, which lived inside the emptied `.git` — recovered afterwards from
  the dashboard's git bundle. The same thing happened again at 13:09, when the other
  instance merged this project's history into the dashboard repository and rewrote the
  tree from its own copy. Details in R24 and in
  `14_CD_SYNC_AND_CADENCE_2026-10-28.md` §13.

**Figures in files 01–09 are from 2026-10-06** and are a snapshot, not the
current state. The live numbers are in file 11 and in the status report at the
repository root.

**Which report is the current one.** The repository root can hold more than one
status report: **the current one is the newest by date** —
`RAPORT DE STARE — SENTINEL PRIME DASHBOARD - 2026-10-28 03-31.md`. All
superseded reports live in `raport-archive\`. One older copy is still at the
root: `… 2026-10-10 20-04.md`, whose content is identical to
`raport-archive\raport-2026-10-10_20-04.md`. **It was left in place on
purpose** — removing material from the project root is not a call this session
makes on its own. Nothing is lost either way: the content is in the archive and
in the git history.

---

## The single most important rule in this project

Stated by the operator, 2026-10-06:

> **We do not solve a gap by removing the gap; we solve it by upgrading the system. If you want to
> build something, you play scaffolding and then raise the building. You do not take the scaffolding
> down if the building is not finished.**

In practice, for anyone continuing this work:

1. A declared-but-unbuilt thing is a **gap**, not an error. It closes by constructing the missing
   thing, never by editing the declaration that names it.
2. **Never make a blueprint agree with the present.** The blueprint is the target.
3. Existing scaffolding is left standing, contents and all. A profile mailbox is where the work will
   land — and the four that exist already hold `PRIME-CLI`'s message history, which is not ours to
   clear.
4. **Never delete or merge.** A separate profile stays separate.
5. Nothing is an optimisation target unless the operator says so.

This is not a stylistic preference. It is enforced by a test — `test_the_plan_is_never_pruned` in
`08_SELF_IMPROVEMENT\test_suite.py` — which fails the suite if the blueprint shrinks below nine
declarations, if a declaration is neither built nor tracked, if a profile mailbox disappears, or if any
script in the project deletes the plan. Full doctrine in
`11_BRAIN\04_METHOD\MISSTEPS_AND_CORRECTIONS.md`, entry **M-27**.

---

## What this build is

A local, loopback-only control centre for the MiniMax ecosystem, dual-anchored so it comes up with the
machine:

- a **container web plane** (`mavis-sentinel-hub`, publishing `127.0.0.1:8910`), and
- a **Windows Startup anchor** (a `.bat` in the Startup folder, which brings up both planes).

It is deliberately **not** public. It is the local half of a larger system that will include Hermes,
and it was built to the level and shape of the Hermes build so the two can sit side by side.

Next step: Hermes is the main orchestrator and builder; Mavis is the engineer establishing this side of
it. See `09_ROADMAP.md`.