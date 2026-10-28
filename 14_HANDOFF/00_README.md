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
| **—** | **`SKILLS/`** | **The 7 skills handed to the new instance, plus a manifest. Copies, so a fresh agent without a skills directory still has them.** |
| 01 | `01_BUILD_STATUS.md` | **Start here.** What is live, what is strong, what is weak. |
| 02 | `02_GAPS.md` | Every gap, sorted into **BUG** (went wrong) and **SCAFFOLDING** (not built yet). |
| 03 | `03_ARCHITECTURE_SPEC.md` | The system as actually built, with measured file sizes and routes. |
| 04 | `04_BLUEPRINTS.md` | The nine Hermes gateway profiles, and every future design. |
| 05 | `05_DEPENDENCIES.md` | Every external dependency, what it is, whether it resolves. |
| 06 | `06_SKILLS_AND_MCP.md` | The 26 SENTINEL tools, the live MCP profile, 62 skills. |
| 07 | `07_OPERATIONS.md` | How to run, stop, restart, test and troubleshoot this. |
| 08 | `08_CONSTRUCTION_SCHEMA.md` | **How to add work correctly.** Read before building anything. |
| 09 | `09_ROADMAP.md` | What comes next, in order, with dependencies between steps. |
| — | `HANDOFF.md` | The one-page state of play for the next session. |
| — | `_BUILD_SURVEY.json` | Raw measurement. 30,136 bytes. The source for every number above. |

### Four things that changed after this package was written

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

**Figures in files 01–09 are from 2026-10-06** and are a snapshot, not the
current state. The live numbers are in file 11 and in the status report at the
repository root.

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