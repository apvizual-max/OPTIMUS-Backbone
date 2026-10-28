# PLAN 3 — THE COMMAND CENTER

**Act three of four.** *"A central dashboard that SENTINEL Prime Minimax should be related to
everything we discussed, everything you programmed, everything you documented… a dashboard
working in my browser called Sentinel Prime Minimax."*

**Status: EXECUTED and MEASURED.** Running on `http://127.0.0.1:8910/`, loopback only, 11 panels,
verified by an independent lifecycle harness rather than by inspection.

---

## 1. The requirement, restated as constraints

| # | Requirement | Design consequence |
|---|---|---|
| C1 | "display real-time data" | a collector that measures continuously; no cached verdicts |
| C2 | "adapt" | SSE/polling with a fallback, not a hard dependency on one transport |
| C3 | "show every detail of the SENTINEL role and persona" | 11 panels, one per axis of the system |
| C4 | "we need to tweak it, change it, and add actions" | a whitelisted action endpoint, extendable without touching the loop |
| C5 | "everything must come together" | panels read the *generated* correlation documents, never a private copy |
| C6 | "full backend … front end … integrate perfectly" | three layers with a one-writer-per-file rule |
| C7 | "consider all necessary dependencies" | §7, the dependency audit |

---

## 2. Architecture

```
  monitor.py ──────────writes──▶ api\health.json
        │
        ▼
  collect-sentinel.ps1 ──reads──▶ health.json, corpus_stats.json, chapter_map.json,
        │                          UNPLACED.md, bimodal_state.json,
        │                          IDEA_TO_SCRIPT_MATRIX.json, GAP_REGISTER.json,
        │                          last_test_run.json
        │                              │
        │                              ▼
        └──────────writes──▶ api\sentinel-state.json   +   state-history.jsonl
                                       │
                                       ▼
  server.ps1  ──reads──▶ those files, serves them over 127.0.0.1:8910
                                       │
                                       ▼
  index.html  ──reads──▶ /api/state · /api/health · /api/stream · /api/corpus
                        and POSTs /api/action
```

### 2.1 The one-writer rule

**The collector writes the state file and never touches `bimodal_state.json`. The workflow engine
is the only writer of that one.**

Two writers would corrupt the single file the dashboard trusts most, and the corruption would be
intermittent — the worst kind. This is a structural decision, not a style preference.

### 2.2 The request/measure split

The collector runs on its own 25-second cadence and writes a file. Requests only ever *read* that
file. A poll therefore costs ~0.01 s regardless of how slow the measurement is, and a slow
measurement can never make the dashboard hang.

---

## 3. Routes

| Route | Method | Returns |
|---|---|---|
| `/` | GET | `index.html` |
| `/api/state` | GET | the collected state, `no-store` |
| `/api/health` | GET | every check as `OK`/`FAIL`/`STALE`/`NOT_RUN` |
| `/api/history` | GET | trend tail |
| `/api/corpus` | GET | paged verbatim search |
| `/api/stream` | GET | SSE — see §5, deliberately short-lived |
| `/api/action` | POST | run a **whitelisted** id, return its output |

---

## 4. The security boundary

The body supplies an **id**, never a command. The id is resolved through `$ACTIONS`. Unknown or
injected → **400**, and the refusal *names what it refused*.

**Measured, raw over a socket:**

```
POST /api/action   {"id":"rm -rf / --no-preserve-root"}

HTTP/1.1 400 Bad Request
Content-Type: application/json

{"error":"unknown or forbidden action id","id":"rm -rf / --no-preserve-root"}
```

Verified on every one of three start/stop cycles, alongside a smuggled id
(`deps_check; whoami`), a shell-shaped id (`Invoke-Expression`), and an empty body.

### 4.1 A verifier that could have lied

The first version of the security check used `Invoke-WebRequest`, which **throws** on 400 and does
not reliably expose the response body. It reported `http=400 body=` — indistinguishable from a
bare refusal with no explanation.

The check now reads the response over a raw socket and asserts on the **body**: the code, *and*
that the server echoed the offending id. A refusal that does not say what it refused is half a
refusal.

### 4.2 Static assertion, as a property

`test_dashboard_surface` asserts that dispatch resolves through `$ACTIONS.ContainsKey`, that no
`Invoke-Expression`/`iex` appears, and that the raw body is never invoked — **not** on a literal
source line. The earlier version pinned `ConvertFrom-Json).id` and therefore failed a *security*
test when the parser was refactored without weakening anything.

---

## 5. SSE: why it is short-lived

The obvious implementation holds the response open and pushes on every refresh. **It cannot work
here.** The listener loop is single-threaded and the handler runs inside it, so one connected
browser would block every other route — including the `/api/state` call that same page needs. The
dashboard would connect, then hang itself.

So: send the current state, flush, **close**. The browser's native `EventSource` reconnects
automatically, the UI updates at the collector's cadence, and the listener is free in between.

The data cannot be fresher than the collector makes it (25 s), so a persistent pipe would add risk
without adding freshness.

**`SendChunked = $true` is required.** Without it HttpListener buffers the response and the client
receives nothing. That was the original bug: `/api/stream` answered **0 bytes**, and an **empty
`catch` block swallowed the exception**, so it failed silently for an entire build.

The handler now names its errors, and the verifier asserts the property that actually matters:

```
GET /api/stream (SSE)          PASS   bytes=...  has-event=True
API still live after SSE       PASS   http=200 in 12ms
```

The second line is the regression guard for the blocking design.

---

## 6. The 11 panels

| Panel | Reads | Shows |
|---|---|---|
| Overview | `health.json` | overall status, OK/FAIL/STALE/NOT_RUN counts, data age |
| Brain | `corpus_stats.json`, `UNPLACED.md`, chapter files | messages, turns, chapters, retention ratio, sha256 |
| Method | the 12 steps | the TANY-LLM → SENTINEL procedure |
| Axes | the four axis chapters | Strategy / Reason / Logic / Rationale |
| Doctrine | `sentinel_hub_server.py` | declared tools, and that none are wired |
| Program | `IDEA_TO_SCRIPT_MATRIX.json` | 24 concepts with their status |
| Workflow | `bimodal_state.json` | mode, stop reason, consecutive failures `/5` |
| Tests | `last_test_run.json` | passed / failed / skipped / **NOT_RUN** |
| Wiring | health checks | what is declared vs verified |
| Learning | `self_improvement_candidates.json` | lessons awaiting R0 |
| Cockpit | the whitelist | run an action, read its raw output |

### 6.1 Three rendering laws

1. **A missing source renders `NOT_MEASURED`, never a healthy default.**
2. **Data age is always shown**, and a panel past its bound shows `STALE`.
3. **The panel renders; it does not rule.** It never computes a verdict — it displays the one the
   monitor produced by measuring.

### 6.2 The STOP banner

When the workflow is STOPPED the Overview shows a banner, because STOP means *report, ask, wait*
and a screen that does not say so is a screen that invites the reader to keep working.

### 6.3 The corpus search box

Searches the **verbatim tier only**, with excerpts and turn ids. Tool payloads are excluded by
design: inlining 448 evidence messages would return noise instead of reasoning.

---

## 7. Dependencies — measured, not assumed

Both interpreters were checked: **Python 3.14.6** (PATH) and **Astral 3.11.15**.

| Package | Status | Consequence |
|---|---|---|
| `playwright` | MISSING | Browser automation `NOT_RUN` — 0 assertions |
| `PIL` | MISSING | image path unverified |
| `pypdf` | MISSING | PDF path unverified |
| `cv2`, `pytesseract`, `faster_whisper` | MISSING | OCR / transcription unverified |
| `tesseract` | not on PATH | as above |

**Installing any of these requires R0.** Until then they are reported as unverified capabilities.
Reporting them as working would be the one thing this dashboard must never do.

---

## 8. Actions

Fourteen whitelisted ids; thirteen read-only, one state-changing.

**`wf_stop_ack` is the only action that changes state, and it refuses without the operator's
words.** The cockpit prompts for them, and refuses locally on an empty answer so the refusal path
stays visible instead of being quietly pre-empted. The server refuses independently — the UI is
not a way around the gate.

> **Why the workflow verbs are read-only now.** `wf_state` used to invoke `bimodal_workflow.py`
> with no arguments, and the module's default entry point was a state-changing **demo**. A button
> labelled "Workflow status" was overwriting the live workflow with a fiction — including a
> fabricated R0 contract — and could have cleared a genuine STOP. The engine now defaults to a
> read-only `status` verb; the demo requires an explicit `demo`; and `status` was proven not to
> write by hashing the state file before and after (unchanged).

---

## 9. Verification

`api\verify-server.ps1` — the deliverable that makes "it works" a measurement.

Per cycle: clear any pre-existing server → start → probe 7 routes asserting on **content, not
just status** → attempt 4 injections → assert the STOP gate → run 2 actions → stop and wait for
the port to close. Three cycles by default. Writes `api\verify-report.json`.

### 9.1 What verification found that inspection did not

| # | Defect | How it surfaced |
|---|---|---|
| 1 | state file never written (`$STATE`/`$state`) | `/api/state` served its fallback; **the script still exited 0** |
| 2 | every corpus search dead (`$PY`/`$py`) | found by **reading the server's own log** after the client only reported a 400 |
| 3 | `/api/stream` returned 0 bytes | `SendChunked` missing, exception swallowed by an empty `catch` |
| 4 | a "status" button that overwrote state | caught by auditing what the id actually invoked |
| 5 | verifier could not read a 400 body | it reported `body=` and looked like a server bug |
| 6 | stop-by-listener targeted **PID 4 (System)** | `HttpListener` is hosted in `http.sys`; the listening socket is not owned by the PowerShell process |

Defect 6 is worth stating plainly: the natural way to stop this server — find the process owning
the listening port — targets the kernel, leaves the server running, and silently invalidates every
later test. The verifier now identifies the server by **command line**, and refuses to kill any
process whose command line is not `server.ps1`.

### 9.2 Current measured result

See `api\verify-report.json` and the ratification report. The headline: **every route, every
refusal and every stop passes on all three cycles**, and the health verdict it reports is `FAIL` —
correctly, because the system *is* degraded in the ways §7 lists.

---

## 10. Acceptance criteria

| # | Criterion | Status |
|---|---|---|
| D1 | Real-time data | collector every 25 s; age shown on every panel |
| D2 | Adapts | SSE with a polling fallback |
| D3 | Every detail of the role | 11 panels |
| D4 | Actions, tweakable | 14 whitelisted ids, 400 on anything else |
| D5 | Everything comes together | panels read the generated correlation documents |
| D6 | Full backend + front end, integrated | 3 layers, one writer per file |
| D7 | Dependencies considered | 6 measured missing, all needing R0 |
| D8 | Works, proven | 3 cycles, **55/55 PASS**, `verify-report.json` |

---

AMIN. Render what you measured, even when it is ugly. An overall `FAIL` on a system that is honest
about its missing dependencies is a better dashboard than a green one that lied.
