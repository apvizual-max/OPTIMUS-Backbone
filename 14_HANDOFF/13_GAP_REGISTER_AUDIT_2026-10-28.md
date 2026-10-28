# 13 — Gap Register Audit, 2026-10-28

**What this is.** The verification the takeover prompt asked for, focused on the one
instrument that was quietly wrong: `12_PROGRAM\GAP_REGISTER.json` and the tool that
writes it. Everything else in the build verified green — both suites, the live page,
the remote clone. This document records what was measured, what was repaired, and what
is still open.

**Owner:** Popy. **Author:** Mavis (agent). **Date:** 2026-10-28, 05:00–07:40.

---

## 1. The finding in one paragraph

The gap register is the project's source of truth for what is outstanding. It was last
written on **2026-10-06**. Its nine `HPROF_*` entries said the Hermes profile gateway
servers were "declared and not yet constructed", with `target_present=False`. Measured
on 2026-10-28, **all nine exist and answer a real MCP stdio handshake**. The ledger had
become history while still being the source of truth, because nothing was writing to
it. Worse, the tool that regenerates it **destroyed** it: one run of
`build_program_matrix.py` reduced the register from 18 entries to 7.

## 2. The timeline, measured

| when | what | evidence |
|---|---|---|
| 2026-10-06 22:50 | the register was written, 18 entries, all `OPEN` | mtime of `12_PROGRAM\GAP_REGISTER.json` |
| 2026-10-07 04:32 | `14_HANDOFF\02_GAPS.md` described that state | mtime; the package README already says files 01–09 are a 2026-10-06 snapshot |
| 2026-10-10 15:09–15:10 | four profile servers built (`sentinel_state`, `rule_triggers`, `learning_loop`, `context_pressure`) | mtimes of the four files; the blueprint's own `builtFromScaffolding` block |
| 2026-10-10 17:13 | the blueprint was updated to declare 7 `.py` servers + 2 npm | mtime of `OPTIMUS_MCP_CONFIG.json` |
| 2026-10-28 02:19 | `prime_bridge`, `web_tools`, `git_tools` (and the hub, and the slice facade) rewritten | mtimes of those five files |
| 2026-10-28 04:30 | the session handoff listed "the seven unbuilt Hermes servers" as an open decision of Popy's | `11_SESSION_HANDOFF_2026-10-28.md` §6, item 11 |
| 2026-10-28 06:52 | measured: all nine present, all nine handshake | this audit, §3 |

**The contradiction that went unnoticed for three weeks:** the blueprint's own
`builtFromScaffolding` block (written 2026-10-10) says the servers were built at their
declared paths, and its `corrections` block says the "superseded" claim was false
because "the five servers START and SERVE". The register said the opposite. Both were
in the same project, three weeks apart, and the register was the one that was quoted.

## 3. The nine servers, measured on 2026-10-28 06:52

Handshake method: a real MCP stdio `initialize` + `tools/list`, with the exact
`command`, `args` and `env` from `OPTIMUS_MCP_CONFIG.json` — not a file read.

| server | kind | target | tools served | registered in the live profile |
|---|---|---|---|---|
| `prime-bridge` | python | 8 533 B, 2026-10-28 02:19:34 | 4 | yes (`prime-bridge`) |
| `sentinel-state` | python | 1 184 B, 2026-10-10 15:09:46 | 3 | no — deliberately, tools already served by `sentinel-hub` |
| `rule-triggers` | python | 1 212 B, 2026-10-10 15:09:53 | 2 | no — deliberately |
| `learning-loop` | python | 1 225 B, 2026-10-10 15:09:58 | 3 | no — deliberately |
| `context-pressure` | python | 1 143 B, 2026-10-10 15:10:03 | 1 | no — deliberately |
| `web-tools` | python | 11 661 B, 2026-10-28 02:19:34 | 3 | yes (`web-tools`) |
| `git` | python | 16 453 B, 2026-10-28 02:19:34 | 6 | yes, as `git-tools` |
| `filesystem` | npm | `@modelcontextprotocol/server-filesystem` | package resolves (registry control answered 19.3.1) | yes, as `mcp-server-filesystem` |
| `browser` | npm | `@playwright/mcp` | package resolves | yes, as `agent-browser-mcp` |

**22 tools over stdio** from the seven python servers. The four that are not registered
in the live profile are Popy's ratified decision of 2026-10-10, recorded in the
blueprint's `liveProfileRegistration.notRegisteredAndWhy`: their tools are already
served by `sentinel-hub` (26 tools), and registering them would put duplicate tool
names in front of every session.

## 4. The landmine, measured in a sandbox

`build_program_matrix.py` wrote the register with the gaps it had measured and nothing
else. One run, against a copy:

```
register entries : 18
generator output : 7
LOST (in register, not generated): 11
   BIN_TESSERACT, HPROF_prime_bridge, HPROF_sentinel_state, HPROF_rule_triggers,
   HPROF_learning_loop, HPROF_context_pressure, HPROF_web_tools, HPROF_filesystem,
   HPROF_browser, HPROF_git, HERMES_GATEWAY_PROFILES
```

Nothing announced it: the blueprint stayed intact, every suite stayed green, and the
next reader saw a shorter, tidier register and believed it.

Three smaller faults in the same tool:

1. `ARTIFACT_EMPTY` was predicted by **file size** (`<= 400 bytes`). Measured on
   2026-10-28: **224 artefacts inspected by content, 0 empty, 0 unreadable.** The
   monitor already carries the content rule and a regression test for it; the builder
   carried the proxy the monitor had killed.
2. `WIRING_MCP` said "no Hermes handshake has been performed; monitor reports
   `mcp_tools_wired` as NOT_RUN". Measured: `mcp_tools_wired` = **OK**, 26 tools
   returned over stdio, probe `sentinel_confirm_identity` ok=True.
3. `mcp_wired` was **hardcoded `False`** in the programme matrix, so the generated
   report printed "**0 are wired**" while the wire was busy. Measured: **8 of the 8**
   concepts that declare an MCP tool are served.

## 5. What was repaired

Every file below has its previous version kept as `<file>.bak-20261028_0705`.

| file | what changed |
|---|---|
| `08_SELF_IMPROVEMENT\build_program_matrix.py` | the builder **merges** the ledger instead of overwriting it; every measurable gap has a probe; a probe that cannot run reports NOT_MEASURED and changes no status; a closed entry keeps the record of its closure, so a second run leaves the file byte-identical; `mcp_wired` is measured from the handshake artefact |
| `12_PROGRAM\GAP_REGISTER.json` | 19 entries: **6 open, 13 `CLOSED-BUILT`**, each closed entry carrying the dated measurement that closed it, the original claim kept visible above it |
| `13_COMMAND_CENTER\api\collect-sentinel.ps1` | the panel is handed the **open** entries; the closed ones are counted and named beside them (`gaps_closed_count`, `gaps_closed_ids`) |
| `08_SELF_IMPROVEMENT\test_suite.py` | new class `Gap register integrity` (9 assertions) |
| `08_SELF_IMPROVEMENT\test_deployment.py` | new phase `gap_count_matches_ledger` — runs the collector, then checks the live `/api/state` against the ledger |
| `08_SELF_IMPROVEMENT\build_idea_to_script_doc.py` | the report renders the measured wired count and the open/closed split, and carries the measurement column |
| `11_BRAIN\06_IDEA_TO_SCRIPT.md` | regenerated from the above |
| `11_BRAIN\04_METHOD\MISSTEPS_AND_CORRECTIONS.md` | M-31, M-32, M-33 (append-only) |
| `13_COMMAND_CENTER\EVOLUTION.md` | R18 (append-only) |

**The blueprint was not touched.** `OPTIMUS_MCP_CONFIG.json` is the target, not a
snapshot, and repointing a declaration is an operator decision.

## 6. The control, falsified rather than merely passed

`Gap register integrity` was run against the **old** builder (loaded from its `.bak`,
no file in the workspace was swapped) and it went red, naming the loss:

```
PASSED  : 7
FAILED  : 2
  ! an entry the builder does not measure survives a full run
  ! no entry of the ledger was lost by a builder run: expected [], got
    ['HPROF_filesystem', 'HPROF_context_pressure', 'HPROF_learning_loop',
     'HPROF_prime_bridge', 'HPROF_sentinel_state', 'HERMES_GATEWAY_PROFILES',
     'HPROF_rule_triggers', 'HPROF_git', 'HPROF_NPX_LAUNCH', 'HPROF_web_tools',
     'HPROF_browser', 'BIN_TESSERACT']
```

Against the new builder: **9/9 passed**. A control that has only ever passed has
proved nothing.

## 7. Measured state after the repair

| | value | when |
|---|---|---|
| `test_suite.py` | **607 passed / 0 failed / 0 skipped** (598 before, +9 new assertions) | 07:12 |
| `test_deployment.py` | **70 passed / 0 failed / 1 not-run** (71 checks, was 70) | 07:29 |
| ledger | 19 entries — 6 open, 13 closed | 07:07 |
| live `/api/state` | `gaps` = 6, `gaps_closed_count` = 13 | 07:24 |
| live `/api/health` | 56 checks, **0 FAIL**, 54 OK / 2 STALE at rest, 46 OK / 10 STALE when the on-demand artefacts age | 06:53 / 07:24 |
| `build_program_matrix.py` run twice | the file is byte-identical after the second run | 07:07 |

## 8. Still open — six entries, and they are real

| id | what it is | why it is open |
|---|---|---|
| `CONCEPT_C18` | Partnership protocol (two blind men) | documentation only, by design |
| `CONCEPT_C19` | The 3-Propozitii ritual as an invocable command | described, not wired to a command |
| `CONCEPT_C21` | Context pressure monitor | partially implemented, not surfaced |
| `CONCEPT_C23` | Historical cultures corpus | a corpus, not a program — correctly so |
| `CONCEPT_C24` | 963 Hz / SACRU proverbs | doctrine only; the source is a 25-axis matrix, and its per-proverb attributions are flagged in-file as fabricated by an earlier agent |
| `HPROF_NPX_LAUNCH` | **new, measured 2026-10-28** | the blueprint launches its two npm-backed profile servers with the bare command `npx`, which resolves to a batch file and failed to spawn from a non-shell launcher (`WinError 2`); the live profile launches the installed `.cmd` shims instead |

`HPROF_NPX_LAUNCH` needs Popy's R0, because the only honest fix is to repoint a
blueprint declaration. The precedent is on record: on 2026-10-10 `web-tools` and `git`
were repointed from phantom npm packages to local servers, by decision, with the
reasoning written into `builtFromScaffolding`.

## 9. What the next instance should know

1. **The register is now live.** Run `08_SELF_IMPROVEMENT\build_program_matrix.py` to
   re-measure it. It merges; it never deletes. If an entry you wrote is missing from
   the output, that is a bug in the builder, not a reason to re-add it by hand.
2. **Files 01–09 in this folder are dated 2026-10-06/07 and are a snapshot**, as the
   package README already says. The live numbers are in file 11, in file 13 (this one),
   and on the dashboard.
3. **`14_HANDOFF\02_GAPS.md` is not the current gap inventory.** It is the 7 October
   one, and its Part E describes three stale entries that were re-measured and closed
   today. The current inventory is `12_PROGRAM\GAP_REGISTER.json`.
4. **The two STALE checks are not faults.** `corpus_fresh` (~22.9 days against a 1-hour
   bound) and `workflow_state_fresh`, plus the `log_*` family when nothing has written
   it for a while: those artefacts are written on demand, and a STALE on an on-demand
   artefact is the system telling the truth about age. The bounds were not widened.
5. **Do not delete anything here.** The closed entries stay in the ledger: a gap that
   was decided and then done is the record that the work happened.
