# SENTINEL PRIME — MINIMAX SENTINEL BRAIN Command Center

**The correlation of the discussion, the programme, and the system monitoring itself, in one
browser surface, driven only by measured data.**

This directory is the third act. `11_BRAIN/` holds the conversation; `12_PROGRAM/` holds what
was built from it; this holds the live view that ties both to the machine as it actually runs.

---

## Start it

```
powershell -NoProfile -ExecutionPolicy Bypass -File 13_COMMAND_CENTER\api\sentinel-hub.ps1 start
```

Then open <http://127.0.0.1:8910/>. The server is **loopback only** and is never reachable
off this box. The same thing happens automatically at logon, via
`%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\SENTINEL Command Center.bat`.

> **Do not start `server.ps1` directly. Double-clicking `bat\sentinel-cc.bat` is
> supported — but only as of 2026-10-09.**
>
> `bat\sentinel-cc.bat` used to start `server.ps1 -Port 8910` — the port the
> **container** owns. `sentinel-cc.ps1` never mentions Docker or the container name;
> it binds a PowerShell server straight onto the front port, opens your browser, and
> reports success. The result is a `HIJACKED` deployment: everything looks up, every
> liveness probe says healthy, and the thing answering is not the deployment. That is
> the exact state `Test-FrontIsHijacked` and `test_front_not_hijacked` exist to
> catch, and it cost a real debugging cycle once already.
>
> **That launcher has since been rewritten, and the correction is worth stating
> precisely** because the old one looked fine from the outside. It now delegates to
> `sentinel-hub.ps1`, so both planes come up in the right order, and then it
> *measures* `http://127.0.0.1:8910/readyz` before opening anything. If the probe
> does not answer 200 it opens no browser and prints a two-plane diagnosis. It is no
> longer on the wrong side of the hijack, so the prohibition above no longer applies
> to it. `server.ps1` itself is still never a thing to launch by hand.
>
> `sentinel-hub.ps1` remains the single supported *programmatic* entry point: it
> owns **both** planes (backend `127.0.0.1:8912`, container front `127.0.0.1:8910`),
> it is what the Startup entry invokes, and it is what the launcher now calls.
>
> If you need the backend alone, for debugging, pass the backend's own port
> explicitly — `-Port 8912`, never the default:
>
> ```powershell
> powershell -NoProfile -ExecutionPolicy Bypass -File 13_COMMAND_CENTER\api\server.ps1 -NoBrowser -Port 8912
> ```

## Stop it

```
powershell -NoProfile -ExecutionPolicy Bypass -File 13_COMMAND_CENTER\api\sentinel-hub.ps1 stop
```

This stops the container, stops the backend, and clears stray listeners found by
command line. `status` reports `UP`, `DEGRADED`, `DOWN` or `HIJACKED` and exits
non-zero for anything that is not `UP`.

## Prove it works

Do not trust the start banner. Run the verifier:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File 13_COMMAND_CENTER\api\verify-server.ps1 -Cycles 3
```

It drives the deployment through `sentinel-hub.ps1` — the same verbs the Startup `.bat` uses — and
stops it first, so every cycle begins from a known-down state. Each cycle then proves both planes
independently (the front is the container *by its deployment header*, the backend answers on its own
port), probes every route over real HTTP, attempts injected action ids, checks the STOP
acknowledgement gate, stops, and confirms the teardown took effect. It writes
`api\verify-report.json`, which the Ecosystem panel reads through `/api/verify`. Exit code 0 means
every check passed.

Two facts this script reports but does **not** gate on, because they belong to different systems:
the monitor's own verdict (shown as a `[note]` line, and carried in the report as
`monitor_overall`), and the previous run's verdict served by `/api/verify` mid-cycle — asserting
PASS on that would be asserting that a stale file is fresh.

The verifier exists because the Command Center this was modelled on was **down** when the work
started (connection refused on port 8900, two watchdog restarts). "It starts" is a claim that has
to be measured on this machine, every time.

### Prove it RENDERS — the check that actually mattered

`verify-server.ps1` proves the **routes** answer. It does not prove a person can see anything.
On 2026-10-04 this surface served HTTP 200 / 43,077 bytes / 55-of-55 checks across three start-stop
cycles with zero console errors — **and rendered a completely blank page**, because
`buildTabs()` marked the first tab `aria-selected` but nothing ever added `.active` to a panel, and
the stylesheet is `.panel{display:none}` / `.panel.active{display:block}`.

Presence in the DOM is not appearance on screen. Run the browser proof, with the server up:

```powershell
# terminal 1 - start it (orchestrator, not server.ps1 - see the warning above)
powershell -NoProfile -ExecutionPolicy Bypass -File 13_COMMAND_CENTER\api\sentinel-hub.ps1 start

# terminal 2 - look at it
python 08_SELF_IMPROVEMENT\final_browser_proof.py
```

It reads the tab list **from the page** rather than from a hardcoded list, clicks
every one of the resulting 12 tabs for real, and requires each to be displayed,
non-zero height, holding visible text, and free of coercion artefacts
(`[object Object]`, `undefined`, `NaN`) and stale verdicts. Exit 0 means all 12
render. The count is the app's, not the test's: an earlier version compared a
hardcoded list of 11 against itself and printed "11/11" while silently skipping
a panel. A screenshot is captured — but the screenshot is **not** the evidence; a
screenshot of a blank page is still a successful screenshot.

### Prove the claims behind the panels

```powershell
# 26 MCP tools answering over stdio, not 26 names in a file
python 08_SELF_IMPROVEMENT\mcp_handshake.py

# the corpus is intact and byte-idempotent
python 08_SELF_IMPROVEMENT\corpus_extractor.py verify

# 279 assertions, 0 failed, 0 skipped
python 08_SELF_IMPROVEMENT\test_suite.py
```

`mcp_handshake.py` writes `09_LOGS\mcp_handshake.json`, which is what makes the Wiring panel's
"MCP wired" tile a **measurement** rather than a count of declarations. Its probe asserts that the
arguments it sent were echoed by the handler — a tool that answers politely without receiving
anything is not proof of a working tool.

---

## Routes

| Route | Method | Returns |
|---|---|---|
| `/` | GET | `index.html` — 11 panels, Obsidian Telemetry Dark |
| `/api/state` | GET | `sentinel-state.json`, written by the collector |
| `/api/health` | GET | `health.json` — every check as `OK`/`FAIL`/`STALE`/`NOT_RUN` |
| `/api/history` | GET | tail of `state-history.jsonl` (trend data) |
| `/api/corpus` | GET | paged corpus search (`?q=…&limit=…`) |
| `/api/stream` | GET | Server-Sent Events; pushes state on every collector refresh |
| `/api/action` | POST | `{"id":"<whitelisted id>"}` — runs it, returns its output |

The UI uses SSE when available and falls back to polling when it is not.

---

## The security boundary

The HTTP body supplies an **action id**, never a command. The id is resolved through the
`$ACTIONS` whitelist in `api\server.ps1`; an unknown or injected id returns **400** and runs
nothing.

```powershell
Invoke-WebRequest -Uri http://127.0.0.1:8910/api/action -Method POST `
  -Body '{"id":"rm -rf"}' -ContentType application/json -UseBasicParsing
# -> 400 {"error":"unknown or forbidden action id","id":"rm -rf"}
```

This is asserted by `verify-server.ps1` on every cycle, and re-asserted statically by
`test_dashboard_surface`, which checks the *property* (the id is resolved through
`$ACTIONS.ContainsKey` and the raw body is never invoked) rather than one literal source line.

Rules the actions obey:

- nothing writes outside `SENTINEL_PRIME/`
- nothing touches `E:\`, `D:\`, or Docker state
- nothing reaches the network
- action output is capped at 200 000 characters

---

## Actions

Read-only unless marked. `wf_stop_ack` is the only one that changes workflow state, and it
refuses to do so without the operator's own words.

| id | Changes state? | What it does |
|---|---|---|
| `wf_state` | no | Live bimodal state via the read-only `status` verb |
| `wf_stop_report` | no | The STOP record: reason, timestamp, context |
| `wf_stop_ack` | **yes** | The only exit from STOPPED. Asks for your words, records them, refuses an empty one |
| `tests_run` | no | Full suite; also writes `api\last_test_run.json` for the Tests panel |
| `corpus_verify` | no | Re-extracts and compares the SHA256 — proves idempotency |
| `corpus_digest` | no | The 102 user messages (95 turns) in order |
| `matrix_dump` | no | The full idea → file → tool → test correlation |
| `mcp_wiring` | no | Declared MCP tools, and the fact that none are wired |
| `deps_check` | no | Every optional capability, marked unverified when absent |
| `self_check` | no | Proves the self-improvement ratify gate blocks an unratified lesson |
| `skills_list` | no | Skill files under `07_BACKBONE\skills` |
| `logs_tail` | no | Last 25 workflow transitions |
| `versions_list` | no | The frozen rollback snapshots (five at most) |

> **Why `wf_state` is read-only.** It used to invoke `bimodal_workflow.py` with no arguments, and
> the module's default entry point was a state-changing **demo**. A button labelled "Workflow
> status" was therefore overwriting the live workflow with a fiction, including a fabricated R0
> contract — and could have cleared a genuine STOP. The engine now defaults to a read-only
> `status` verb and the demo requires an explicit `demo`.

---

## How the data flows

```
monitor.py ──writes──> api\health.json
collect-sentinel.ps1 ──reads health.json, corpus stats, chapter map,
                       bimodal_state.json, the matrix, the gap register──writes──> api\sentinel-state.json
                                                                                   + state-history.jsonl
server.ps1 ──reads──> those files, and serves them
index.html ──reads──> /api/state, /api/health, /api/stream, /api/corpus
```

Two rules make the numbers trustworthy:

1. **One writer per file.** The collector writes the state file and never touches
   `bimodal_state.json`; the workflow engine is the only writer of that one.
2. **A missing source is `NOT_MEASURED`, never a healthy default.** Every panel shows the data
   age, and marks itself stale past the bound.

---

## Panels

Overview · Brain · Method · Axes · Doctrine · Program · Workflow · Tests · Wiring · Learning ·
Cockpit

Brain and Program read the generated corpus and matrix. The Program panel is fed by
`11_BRAIN\06_IDEA_TO_SCRIPT.md`, which is **rendered from** `IDEA_TO_SCRIPT_MATRIX.json` — never
hand-edited, so it cannot drift into describing a system that no longer exists.

---

## What the panels will tell you is broken

The Command Center is not a trophy. On the current run it reports, honestly — **51 OK · 2 FAIL ·
0 NOT_RUN · 2 STALE**, overall `FAIL`:

- **2 FAIL** — both in the same place, and both real: `mcp_config_servers_exist` (5 `.py` servers
  declared by `OPTIMUS_MCP_CONFIG.json` that are not on disk) and
  `mcp_npx_packages_resolve` (2 of 4 declared packages 404 at the registry). The other
  optional dependencies this section used to describe as failing — `playwright`, `PIL`, `pypdf`,
  `docx`, `openpyxl`, `pptx`, `cv2`, `pytesseract`, `faster_whisper`, `tesseract` — are now
  present, so those checks pass.
- **2 STALE** — state files past their age bound, which means nothing has written them
  recently. That is a statement about idle time, not a fault.
- **0 NOT_RUN** — nothing was skipped.

> **This block previously claimed `40 OK · 11 FAIL · 1 NOT_RUN · 0 STALE` and attributed the 11
> failures to absent optional dependencies.** Every one of those dependencies is now installed,
> so the claim had become false in the generous direction: it described failures that no longer
> existed and missed the two that do. A number in a document that nobody re-measures does not
> stay true.

The two live FAILs are awaiting a decision — see `11_PLANS\MCP_DECISION_BRIEF.md` (option **A**
prune all seven dead entries, or **B** prune and add real fetch/git providers). The
`OPTIMUS_MCP_CONFIG.json` has deliberately **not** been edited.

An overall `FAIL` is the correct reading of a system that is honest about itself. Do not "fix" it
by widening the checks.

---

## Versions

`bat\manage-versions.ps1` keeps a **frozen five-snapshot** store in `backups\versions\`. A sixth
write is refused by design — this is a rollback mechanism, not a backup spool, and identical
snapshots mean a stable build.

```powershell
bat\manage-versions.ps1 -List
```

---

## Files

| File | Role |
|---|---|
| `index.html` | The whole UI, single file, no build step, no CDN |
| `api\server.ps1` | Loopback HTTP server, action whitelist, SSE |
| `api\collect-sentinel.ps1` | The only thing allowed to produce a verdict, and only by measuring |
| `api\verify-server.ps1` | Proves the lifecycle and every route, three cycles by default |
| `api\health.json` | Monitor output (generated) |
| `api\sentinel-state.json` | Collector output (generated) |
| `api\last_test_run.json` | Test suite result (generated) |
| `api\verify-report.json` | Last verification run (generated) |
| `bat\sentinel-cc.bat` | Manual launcher — starts **both** planes via `sentinel-hub.ps1`, then opens the browser only after `/readyz` answers 200 |
| `bat\manage-versions.ps1` | Frozen five-snapshot store |

---

## Tracked defects this surface exposed

Kept here because the evidence matters more than the fix. **Thirteen defects**, all found by
measurement during this build.

1. **`$STATE` / `$state` collision** (2026-10-04). PowerShell variable names are
   case-insensitive, so the state *path* and the state *object* were one variable.
   `Set-Content -Path $STATE` wrote a file literally named
   `System.Collections.Specialized.OrderedDictionary` in the workspace root. The script exited 0,
   appended its history, printed a healthy summary, and the real state file never existed — so
   the dashboard served its honest fallback for the entire build with no error anywhere.
   Fixed by renaming the path to `$STATE_PATH`; guarded permanently by
   `ps_variable_case_collisions` in `monitor.py`.
2. **`$HEALTH` / `$health` collision.** Same class, latent: it worked only because the path was
   read before the object overwrote it. Renamed to `$HEALTH_PATH`.
3. **`$PY` / `$py` collision.** `Search-Corpus` assigned its Python here-string to `$py` while the
   interpreter path was `$PY` — one variable. Every corpus search then executed the source text as
   a PowerShell command. Found only by reading **the server's own log** after the client saw
   nothing but a status code. Guarded by `ps_shadowed_script_vars`.
4. **SSE returned 0 bytes.** `SendChunked` was missing, so `HttpListener` buffered the response,
   and an **empty `catch` block** swallowed the exception. `/api/stream` failed silently for a
   whole build. The handler now names its errors.
5. **A persistent SSE stream would have wedged the server.** The listener is single-threaded and
   the handler runs inside it, so one connected browser would block every other route —
   including the `/api/state` call that same page needs. The stream is now short-lived by design
   and guarded by `API still live after SSE`.
6. **A read-only button that wrote.** `wf_state` invoked the module with no arguments, and the
   default entry point was the state-changing demo. See the Actions section.
7. **`@($null).Count` is 1.** The chapter count came from a `corpus_stats.json` key that does not
   exist, so the panel reported "1 chapter" beside 17 `CH_*.md` files. Now counted from disk.
8. **The monitor reported a false FAIL.** `corpus_no_unplaced` asked for a key that is not in the
   file; `None == 0` is False, so a corpus with zero unplaced messages was flagged. Now reads
   `UNPLACED.md`, and the fix is sabotage-proven: with the file moved aside the check says
   `NOT_RUN` — *unknown, not zero* — never a false `OK`.
9. **A detector that went blind on a BOM.** PowerShell 5.1 writes a UTF-8 BOM; read as plain
   `utf-8` the collision check reported OK while seeing nothing. Now `utf-8-sig`, proved by
   planting a collision.
10. **A generator printing `?`.** The gap renderer asked for `severity` and `title`, which the
    gap register does not have, so every row rendered `?` inside a table that looked finished.
11. **A test pinning a literal.** `test_dashboard_surface` asserted on the exact string
    `ConvertFrom-Json).id`, so refactoring the request parser failed a *security* test. It now
    asserts the boundary property — and the body of the 400 refusal is read over a raw socket,
    because `Invoke-WebRequest` throws on 400 and does not expose the body.

### Post-R0: two more, and both survived every check above

12. **The dashboard rendered a blank page.** `buildTabs()` marked the first tab
    `aria-selected="true"` — so the tab strip looked correct — but nothing ever called `select()`, so
    no panel ever received `.active`. With `.panel{display:none}`, **all 11 panels stayed hidden.**
    This passed HTTP 200, 43,077 bytes, 55/55 server checks across 3 cycles, "11 panels present in
    the DOM with content", and zero console errors. Only a screenshot showed it. Fixed by calling
    `select(TABS[0])` in boot; guarded by `test_dashboard_boot_activates_a_panel`.
13. **`[object Object]`, and a panel asserting something it had not measured.** When the MCP
    handshake became a *record* rather than the integer `0`, the Wiring tile concatenated it and
    printed `[object Object]`. The same panel still carried hardcoded prose — *"No runtime
    handshake has been performed with Hermes"* — on a screen showing a completed handshake, under a
    footer claiming *"no panel renders a verdict it did not measure."* The tile now reads the record
    by its keys, and the prose is derived from the measurement. Guarded by
    `test_ui_never_stringifies_an_object`.

**The lesson these two share:** 12 and 13 were invisible to every route test, every DOM-presence
check, and every console-error check in this README above. A renderer must be verified by what it
*shows*, not by what it *serves*.

AMIN. System > Task > Speed > User. Measure before you claim; render what you measured, even
when it is ugly.
