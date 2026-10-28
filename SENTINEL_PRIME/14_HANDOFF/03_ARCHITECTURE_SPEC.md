# 03 — Architecture Spec

The system as **actually built**, with measured sizes. Where something is designed but not built, it
says so rather than describing an intention.

All figures from `_BUILD_SURVEY.json`.

---

## The two planes

```
                    ┌──────────────────────────────────────────────┐
                    │  Docker container: mavis-sentinel-hub         │
   browser  ──────► │  nginx/1.31.6   127.0.0.1:8910 → 80/tcp     │
                    │  image mavis/sentinel-hub:1.0.0              │
                    │  restart: unless-stopped                     │
                    │  header: X-SENTINEL-Deployment              │
                    └───────────────┬──────────────────────────────┘
                                    │ proxies to
                    ┌───────────────▼──────────────────────────────┐
                    │  Windows data plane: server.ps1               │
                    │  Microsoft-HTTPAPI/2.0  127.0.0.1:8912       │
                    │  27,374 B · 570 lines                        │
                    └───────────────┬──────────────────────────────┘
                                    │ reads
                    ┌───────────────▼──────────────────────────────┐
                    │  13_COMMAND_CENTER\api\*.json                │
                    │  sentinel-state.json  ·  health.json         │
                    │  minimax-ecosystem.json · last_test_run.json │
                    └──────────────────────────────────────────────┘
```

**The container holds no data.** A `find` across the image returns no corpus and no state file. It is a
pure reverse proxy, so the image can never drift from disk.

### Ports — measured

| Port | Owner | Binding | Measured |
|---|---|---|---|
| 8910 | SENTINEL front (container) | `127.0.0.1` | refused on 3 non-loopback addresses |
| 8912 | SENTINEL backend | `127.0.0.1` | loopback only |
| 8900 | OPTIMUS control centre | — | **not touched by this project** |
| 8901 | OPTIMUS (docker) | — | **not touched by this project** |

---

## Routes — measured

| Route | Front | Backend | Bytes | Purpose |
|---|---|---|---|---|
| `/` | 200 | 200 | 64,805 | The dashboard (`index.html`) |
| `/healthz` | 200 | *n/a* | 87 | Front liveness, served by nginx |
| `/readyz` | 200 | *maps to* `/api/state` | 91,158 | Front readiness = backend state |
| `/api/state` | 200 | 200 | 91,158 | Full state tree |
| `/api/health` | 200 | 200 | 21,079 | 55 monitor checks with evidence |
| `/api/minimax` | 200 | 200 | 21,153 | 32 ecosystem surfaces |
| `/api/verify` | 200 | 200 | 20,385 | Lifecycle verifier results |
| `/api/corpus` | 200 | 200 | 18,916 | Paged corpus search |
| `/api/action` | POST | POST | — | Whitelist-only action runner |

**Route-name asymmetry (documented, not a defect):** the backend has no route literally named
`/healthz` or `/readyz`. Those names are front-only; nginx maps `/readyz` onto the backend's
`/api/state`. The two planes are proved to agree by **byte equality** — both return 91,158.

**`/api/action` security:** the HTTP body supplies an *action id*, never a command. The id is resolved
through a whitelist, so a crafted request cannot execute arbitrary shell. Measured: **all 7
unapproved/injection payloads were refused by the whitelist itself**, not by a missing-field guard —
and the whitelist was separately proved to *admit* a valid action, so the rejection test is not
satisfied by a route that refuses everything.

---

## The dashboard

`13_COMMAND_CENTER\index.html` — **64,805 bytes, 1,178 lines**, 12 tabs, no build step, no
dependencies, served from disk.

Tabs: Overview · Brain · Method · Axes · Doctrine · Program · Workflow · Tests · Wiring · Learning ·
Ecosystem · Cockpit.

Every tab was clicked and rendered by the deployment suite, which requires visible, non-empty content
and zero string-coercion errors (`[object Object]`, `NaN`). That check passes.

---

## Data producers

| File | Bytes | Lines | What it produces |
|---|---|---|---|
| `api\collect-sentinel.ps1` | 14,030 | 313 | `sentinel-state.json`, on a timer |
| `api\server.ps1` | 27,374 | 570 | The data plane |
| `api\sentinel-hub.ps1` | 32,713 | 668 | Orchestrator: start/stop/restart/status/logs/install-startup |
| `deploy\nginx.conf` | 6,149 | 131 | The front |
| `deploy\Dockerfile` | 2,417 | 47 | The image |

### The orchestrator

`sentinel-hub.ps1` exposes six verbs. `install-startup` generates the `.bat` and is the only thing in
the project that writes outside its own tree — and it writes only to the Startup folder.

**Startup anchor, measured:** `SENTINEL Command Center.bat`, 4,557 bytes, 75 CRLF line endings, no BOM,
SHA256 `4acc5bbc…`. It invokes `sentinel-hub.ps1 -Action start`, which brings up **both** planes — the
front alone would be a half-started system.

**Startup log, measured:** `09_LOGS\hub-startup.log` carries **one marker and one exit line per run**.
At survey time it held **60 markers and 24 exit codes, most recent `exit=0`**; the latest live read is
**61 markers, 25 exit lines, 28,180 B, still `exit=0`** — it increments on every cold start, so treat it
as a counter of how many times recovery has been proven, not a fixed figure.

---

## Measurement layer

| File | Bytes | Lines | Role |
|---|---|---|---|
| `monitor.py` | 54,975 | 1,178 | 55 self-checks → `health.json` |
| `collect_minimax_ecosystem.py` | 50,143 | 1,063 | 32 ecosystem surfaces |
| `test_suite.py` | 151,422 | 3,118 | 29 test classes, 502 assertions |
| `test_deployment.py` | 94,750 | 1,852 | 41 deployment checks |
| `07_BACKBONE\mcp\sentinel_hub_server.py` | 38,765 | 968 | **26 MCP tools** |

**Every collector has an explicit honesty law.** If a surface cannot be measured it reports
`NOT_AVAILABLE` — never a healthy default. If a check cannot run it reports `NOT_RUN` — never `FAIL`.
If a scan is truncated it says so. Measured on this run: 32 of 32 surfaces `MEASURED`, 0
`NOT_AVAILABLE`, 0 errors.

The ecosystem collector states its own cost in its docstring: it performs network probes (the only
surface that leaves the machine), makes no API call, uses no credential, launches nothing, caps each
host at 5 s, and reports an honest `unresolved` when the resolver fails. That admission is itself
checked — no `startfile`, no `Popen`, no reference to the Design app from any subprocess call site.

---

## State and persistence

| Store | Contents |
|---|---|
| `13_COMMAND_CENTER\api\*.json` | The four public records, regenerated on a timer |
| `09_LOGS\cross_instance\` | Instance registry, 4 profile mailboxes, heartbeats, mailbox |
| `09_LOGS\hub-startup.log` | 60 startup markers — the evidence that cold start happened |
| `09_LOGS\scraped\` | ~50 scrape artifacts (a known gap, `ARTIFACT_EMPTY`) |

**One writer per file.** The collector is the sole writer of `sentinel-state.json`. Concurrent writers
are prohibited, and a destructive test whose verdict depends on the writer count establishes that
nothing else is writing before it runs.

---

## The MCP surface

`sentinel_hub_server.py` — **26 tools**, hot-reloading by `(st_mtime_ns, st_size)`. Five workspace
modules reach eight of the 26 tools, so a fix written to the workspace would otherwise never reach the
tool that reads it. Full tool list in `06_SKILLS_AND_MCP.md`.

---

## What this architecture deliberately does not have

- **No public exposure.** Loopback only, verified by connection attempt on three real adapters.
- **No baked-in data.** Verified every run against the actual image.
- **No build step for the dashboard.** One static file, served directly. Nothing to break between edit
  and screen.
- **No command injection surface.** Actions are whitelisted by id, with both polarities proven.
- **No destructive default.** `Remove-Item` is blocked, deletions require approval, and nothing is
  pruned automatically.