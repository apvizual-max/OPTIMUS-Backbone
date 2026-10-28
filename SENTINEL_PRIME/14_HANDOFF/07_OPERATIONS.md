# 07 — Operations

Everything needed to run, stop, verify and troubleshoot this build.

---

## 1. Daily commands

All commands are run from `SENTINEL_PRIME\13_COMMAND_CENTER\api\`.

```powershell
# Is it up?
powershell -File .\sentinel-hub.ps1 -Action status

# Start both planes
powershell -File .\sentinel-hub.ps1 -Action start

# Stop both planes
powershell -File .\sentinel-hub.ps1 -Action stop

# Atomic restart
powershell -File .\sentinel-hub.ps1 -Action restart

# Tail the container log
powershell -File .\sentinel-hub.ps1 -Action logs

# (Re)install the Startup anchor
powershell -File .\sentinel-hub.ps1 -Action install-startup
```

**Use `-File`, never `-Command`.** Multi-line `-Command` gets mangled by the Startup environment, and
`every_bat_is_crlf` plus `startup_uses_file_not_command` enforce this.

**Expected `status` values:** `UP` · `DEGRADED` (front up, backend down) · `DOWN` · `HIJACKED` (front
port served by a non-container process).

---

## 2. Running the tests

From `SENTINEL_PRIME\08_SELF_IMPROVEMENT\`:

```powershell
python test_suite.py              # unit suite  — 502 assertions, 29 classes
python test_deployment.py         # deployment  — 41 checks, no cold start
python test_deployment.py --coldstart   # + tears everything down and proves Startup restores it
python survey_build.py            # re-measure everything -> 14_HANDOFF\_BUILD_SURVEY.json
```

**Never run two of these at once.** A destructive test's verdict depends on the writer count, and the
suites write live records. Establish that nothing else is writing first.

### Reading the output

| Line | Meaning |
|---|---|
| `[ok]` | passed |
| `[fail]` | failed — read the reason, it names the cause |
| `[----]` | **NOT_RUN** — could not be measured. Never a pass and never a fail |

Exit code `0` with a `[----]` line is a correct, complete run. A missing browser, an absent Docker
engine or an unreachable registry produce `NOT_RUN`, because none of them falsified anything.

---

## 3. Measured current state

| Check | Result |
|---|---|
| Container | `mavis-sentinel-hub` running, healthy |
| Front | `http://127.0.0.1:8910` → 200, `nginx/1.31.6`, `X-SENTINEL-Deployment` present |
| Backend | `http://127.0.0.1:8912` → 200 |
| Non-loopback | **refused** on `172.21.224.1`, `172.29.32.1`, `192.168.1.193` |
| Unit suite | 502 / 0 / 0 |
| Deployment suite (default) | 40 / 0 / 1 (the 1 is the cold-start gate) |
| Cold start | 43 / 0 / 0 |
| Monitor | overall FAIL · 2 FAIL (stable) · 0 NOT_RUN · STALE count moves |
| Startup log | 61 markers, 25 exit lines, last `exit=0` _(increments each run)_ |

---

## 4. Troubleshooting

### The dashboard is empty

The dashboard renders from `/api/state`. If the panel is blank, the problem is the **state file**, not
the page. Check:

```
13_COMMAND_CENTER\api\sentinel-state.json   — does it exist, and when was it written?
09_LOGS\bimodal_state.json                  — the collector's input
```

`collect-sentinel.ps1` logs its own writes and reports `UNVERIFIED` if a step fails. A silent write
failure is a known historical defect: it was fixed, and the fix is logged rather than assumed.

### `/api/state` returns 404

The backend does not serve `/readyz` or `/healthz` — those are front-only names. Use `/api/state`.
See `01_BUILD_STATUS.md` W4.

### The monitor says 2 FAIL, and 1 or 2 STALE

Expected. The two FAILs are the un-built Hermes gateway servers. The STALE, when present, is the
frozen corpus snapshot reporting "not exercised recently" rather than "broken". Neither is a fault.
See `02_GAPS.md` Part C.

### The front port answers but is not ours

```
docker ps --filter publish=8910
```

If another process holds 8910, `status` reports `HIJACKED`. Stray listeners are identified by **command
line**, not by socket PID — on Windows, `HttpListener` sockets are attributed to PID 4, which is the
kernel and tells you nothing.

### The Startup anchor did not run

Read `09_LOGS\hub-startup.log`. It holds one marker per run and one recorded exit code. The marker is
written *after* the orchestrator's start verb returns, which is roughly a two-second window — a check
that samples the log the instant the front answers 200 can race it. **Both** halves are required: a
bounded wait *and* a key to this run's marker. See doctrine **M-23**.

If the log has no new marker and no new exit line, the anchor did not run at all.

### Cold start hangs

The measured ceiling is **180 seconds** from cold boot to fully operational. If it exceeds that, check
in order: Docker started (the anchor depends on it) → `sentinel-hub.ps1 -Action status` → the container
log via `-Action logs`.

---

## 5. Constraints to respect when changing anything

1. **Ports 8900 and 8901 belong to OPTIMUS.** Never touch them.
2. **`07_BACKBONE\mcp\OPTIMUS_MCP_CONFIG.json` is a blueprint.** Do not edit it to match disk. There is
   a test that fails if you do.
3. **The four profile mailboxes are scaffolding.** Do not delete them for being empty. There is a test.
4. **Nothing deletes automatically.** `Remove-Item` is blocked; deletions need approval; recoverable
   trash only.
5. **One writer per file.** The collector is the sole writer of `sentinel-state.json`.
6. **No fabrication, ever.** A surface that cannot be measured reports `NOT_AVAILABLE`, not a default.
7. **English in code.** Identifiers, comments, messages, UI and tests are English. Romanian is
   preserved only in wisdom, doctrine and quotations. Zero Romanian diacritics in `.py` and `.ps1` —
   enforced by a test class.
8. **Encoding.** PowerShell 5.1, BOM-less UTF-8 for `.py`. Batch files are CRLF — `cmd` mis-parses
   LF. Writing a UTF-8 file from PowerShell 5.1 requires
   `[IO.File]::WriteAllText($p,$t,(New-Object Text.UTF8Encoding $false))`.

---

## 6. What to do first when resuming

1. `python survey_build.py` — re-measure. Do not trust these documents if the system has moved.
2. Read `01_BUILD_STATUS.md`, then `09_ROADMAP.md`.
3. Read `08_CONSTRUCTION_SCHEMA.md` **before** building anything.
4. Pick one `HPROF_*` gap and build it. Close it by constructing the server, never by editing the
   declaration.