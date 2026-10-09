---
name: mavis-sentinel-command-center-skill
description: Operate the SENTINEL Command Center, the local live dashboard on 127.0.0.1:8910 - start it, stop it, check it, and read its panels honestly. Load when Popy asks for the dashboard, when the link is down, when a panel looks wrong, or when a verdict needs interpreting before it is trusted.
parent: mavis-sentinel-prime-on-minimax-skill
installed_by: 08_SELF_IMPROVEMENT/install_skills.py
source_of_truth: SENTINEL_PRIME/07_BACKBONE/skills/
---

# SENTINEL Command Center — operation

The Command Center is the **face** of SENTINEL PRIME: 12 panels over loopback, every value
measured, data age always shown. This skill is how you start it, check it, and read it honestly.

## The one command that matters

```powershell
powershell -NoProfile -ExecutionPolicy Bypass `
  -File C:\Users\apviz\.minimax-agent\projects\SENTINEL_PRIME\13_COMMAND_CENTER\api\sentinel-hub.ps1 start
```

Then open **http://127.0.0.1:8910/**.

If Popy says *"the link is down"*, that command is the answer. Run `status` first to say
whether it is down or whether the browser is stale. `status` names **which plane** is
missing, because a gateway that is up while its app is down is a different fault with a
different fix.

## The two planes — read this before touching a port

| Plane | Where | Owns |
|---|---|---|
| **Backend** (data plane) | Windows PowerShell, `127.0.0.1:8912` | every measurement — it reads Windows-only facts (WMI, `Get-NetTCPConnection`, the runtime's own files) |
| **Front** (web plane) | container `mavis-sentinel-hub`, publishes `127.0.0.1:8910` | the address, health gating, the TLS position |

**8910 is the container, not PowerShell.** Running `sentinel-cc.ps1 start` without
`-Port` will collide with it. The front holds **no copy** of the dashboard — it proxies to
the backend, because a baked-in copy would drift from the data that was actually measured.

Port **8900 belongs to the separate OPTIMUS Control Center** (its own front is 8901).
Never touch either.

## The verbs

Use `sentinel-hub.ps1` — it manages **both** planes. `sentinel-cc.ps1` is the backend-only
launcher underneath it and takes an explicit `-Port`.

| Verb | What it does | Notes |
|---|---|---|
| `start` | backend first, then container; waits for both to answer | backend first **on purpose** — front first yields a gateway that answers `/healthz` while `/readyz` says no, which looks like a working deployment for exactly as long as nobody reads the second path |
| `stop` | stops the container, then the backend | |
| `restart` | stop, then start | measured end-to-end: `DEPLOYMENT UP` |
| `status` | reports both planes, the container health, and a **named** verdict | exit 0 for `UP`, 1 for `DEGRADED`/`DOWN`; names which plane is missing |
| `logs` | container logs | |
| `install-startup` | writes the Startup-folder entry | **self-verifying**: refuses to install a `.bat` it has not structurally checked |
| `uninstall-startup` | neutralises it | delete the file to remove it entirely |

Two paths on the front, and the distinction is the point:

- `/healthz` — **the gateway**, answered by nginx itself. Answers even when the backend
  is dead. A health check that only ever asks the app cannot tell a dead gateway from a
  dead app, and reports the wrong one.
- `/readyz` — **the app behind the gateway**.

`status` also reports a **stale pid file** explicitly (`STALE - process gone`) rather than
reporting a dead process as running. That is deliberate: a pid file is a claim, and the port
is the evidence.

## How it actually stays up — and the trap I fell into

`Start-Process` survives a **shell** exiting. It does **not** survive the **process tree** being
killed, which an agent harness does. The link was killed that way repeatedly, including once
immediately after a 16/16 self-test.

| Mechanism | Result |
|---|---|
| `schtasks /create /sc onlogon` | **Access denied** — not elevated |
| `Start-Process` from an agent shell | **Killed with the tree** |
| `explorer.exe <bat>` | Survives — explorer is not a descendant of the agent |
| **Docker `restart=unless-stopped`** | **Survives** Docker restart and reboot |
| **Startup-folder `.bat`** | **Installed** — returns at logon, no elevation needed |

Installed at
`%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\SENTINEL Command Center.bat`.
**To remove it, delete that one file.** No registry, no scheduled task, no service.

### An agent cannot leave a long-lived server running

A detached `Start-Process` server **does not stay up here.** It died three times, including
immediately after a 16/16 self-test, because an agent harness reaps the process tree it spawned
into.

> Only a process started by something **outside** that tree survives: the desktop shell
> (`explorer.exe`), the Startup folder at logon, or Docker.

So when the dashboard is down:

1. `sentinel-hub.ps1 start` — proves the launch path works, but the backend instance is
   **temporary** if you run it from an agent shell.
2. To leave it genuinely up: `sentinel-hub.ps1 install-startup` and let the next logon do it,
   or launch from outside the agent's tree with `explorer.exe "<bat>"`.

The `.bat`, the Startup entry and the container are **load-bearing**, not conveniences.

### The startup entry failed twice, silently

Both times the deployment simply came up **dead at logon** with nothing logged anywhere:

1. `start "" /min powershell -Command "& '...' -Action start"` — `start` applies its own
   quoting rules, and a multi-line quoted `-Command` argument is exactly what it mangles.
   Now `-File` with one quoted path, with a permanent suite guard that **fails** if
   `-Command` reappears.
2. The generator built the `.bat` with `+` inside an `@( … )` array literal. That is *not*
   concatenation: `'a' + $x + 'b', 'c'` makes `'b', 'c'` an **array**, and `string + array`
   coerces with spaces — so the lines merged and the ports landed in the wrong place.

> **A startup path that has only ever been checked while everything is already running is
> not a path.** Both of these passed review and both were found only by tearing the
> deployment down and running the real entry. The suite now has `startup_cold_start` for
> exactly this, and the entry writes `09_LOGS\hub-startup.log` so a future failure is not
> silent.

Also: `Set-Content` does **not** normalise newlines *inside* a multi-line string, so a
generated `.bat` can carry bare LF endings that `cmd.exe` does not reliably honour. The
installer now forces CRLF and refuses to write a file it has not structurally verified.

### `HttpListener` is not a normal socket — do not "find the owner"

When cleaning up stray processes I asked `Get-NetTCPConnection -LocalPort 8910` which process
owned the port. It answered **pid 4 (System)**. I killed both servers and the link went dead.

```
TCP    127.0.0.1:8910    0.0.0.0:0    LISTENING    4
```

**`HttpListener` binds through the HTTP.sys kernel driver.** The socket is owned by the kernel,
not by the serving process. Every "which process owns this port" heuristic returns System, and
acting on it takes down every HttpListener server on the machine.

**Match on the process you mean, never on the socket.** `sentinel-cc.ps1` identifies servers by
**command line** (`server.ps1` + port) and never by a bare pid or a socket. Use
`Test-Listening` to ask whether it is serving — that is the evidence.

> A destructive action justified by an **indirect** signal is the dangerous one. The pid file,
> the socket table and the process list are three different claims; I acted on the cheapest to
> query and the least likely to be what I assumed.


## Why the old launcher was replaced

`bat\sentinel-cc.bat` ran the server in the foreground of a console window. Three real failures
came out of that, all of which Popy hit:

1. **It died with its window.** An agent shell exiting took the server with it and the open
   link went to connection-refused — the failure reported as *"the link is down"*.
2. **Two invocations collided.** The second bind on 8910 threw, so the obvious repair
   (*start it again*) made it worse and looked like a broken build.
3. **No way to ask.** There was no `status`, so "is it running?" was answered by a browser
   error page.

`Start-Process` detachment fixes (1) for a shell exiting. It does **not** survive the whole
process tree being killed. Only a scheduled task does, because the Task Scheduler service —
not any agent shell — starts the process. Say that plainly rather than implying the launcher is
unkillable.

## The panels, and what each one is evidence of

| Panel | Reads | A FAIL here means |
|---|---|---|
| Overview | aggregate | rollup; the real number is on the panel that owns it |
| Brain | corpus stats | the memory is intact — 955 messages, retention 1.0000 |
| Method | the build method | documentary, not measured |
| Axes | 17 chapters | 0 unplaced messages |
| Doctrine | the gates | documentary |
| Program | concept matrix | concepts by computed status, never typed by hand |
| Workflow | `bimodal_state.json` | mode, failures toward STOP, and state **age** |
| Tests | `last_test_run.json` | 288 assertions, and a **Verdict** tile that is `PARTIAL` if anything was skipped |
| Wiring | `health.json` | declared vs. **wired** — a handshake that really answered |
| Learning | gaps register | 8 open gaps, each with its own evidence |
| Cockpit | actions | the only panel that mutates; it runs the R0 gate first |

**The panel that matters most is Tests**, because it is the one that can say *I did not
measure this*. If it renders `PARTIAL` or `NOT_RUN`, the capability is **unverified, not
working** — do not describe it as passing.

## The Desktop app, Design, and the cloud bridge

The Ecosystem panel measures 21 surfaces. Beyond the runtime, it reaches the
desktop family from its own install trees and Electron state:

| Surface | Reads |
|---|---|
| `desktop_code_processes` | live `MiniMax Code` processes + working set |
| `task_telemetry` | `%APPDATA%\MiniMax Agent\observability-outbox.jsonl` — event count, distinct kinds, age of the newest |
| `embedded_browser` | `embedded-browser-tabs.json` — sessions, tabs, hosts. **This is the local→cloud path** |
| `cloud_bridge_device` | `remote-control\state.json` — the `desktop_device_id` the cloud side addresses this machine by |
| `agent_identity` | `minimax-agent-config.json` — presence of the token block, **never its value** |
| `design_app` / `hub_app` | install + run state, and the reason when stopped |

Design ships a local gateway under `resources\gateway`. It is only measurable
while the app runs; when Design is stopped the surface says `NOT_AVAILABLE` and
names that, rather than reporting a port nothing is listening on.

**Never print a credential.** `agent_identity` reports *that* tokens are present
and states their values are never read. A control hub that printed one would be a
worse defect than a panel with one fewer number.

Three ways this went wrong, all silent:

- **A measurement that could not be taken is not a measurement of zero.** The
  first version reported "no Code process is running" while eleven ran: `wmic`
  rows were split on whitespace (`MiniMax Code.exe` is two tokens), `wmic` is not
  on PATH here, and `except: return []` turned a missing tool into an empty
  *finding*. Take process data from PowerShell `ConvertTo-Json`, and return
  `(rows, error)` so failure is reported rather than absorbed.
- **An array concatenated into a string prints empty, not a count.** A tile read
  `1 session(s), host(s)` because `hosts` was `[]`. It does not throw, so it
  looks fine. Guard with `Array.isArray(x) ? x.length : x`.
- **A missing `/favicon.ico` is a console error.** Requested by the browser, not
  the app, and it still means a page that is not clean. An inline
  `<link rel="icon" href="data:image/svg+xml,...">` cannot 404.

---

## Reading a verdict honestly
- `NOT_MEASURED` with a reason beats any number you could invent.
- Data age is always displayed. A panel showing a value from 40 minutes ago is showing a
  snapshot, and the header will say so.
- A red monitor is not automatically a broken system, and a green one is not automatically
  a working one. **Read which checks are red and why before characterising the system.**
  At the last measurement: 55 checks, 43 OK, 2 FAIL, 10 STALE. The 2 FAIL are the dead
  `OPTIMUS_MCP_CONFIG.json` entries, left red on purpose pending Popy's decision. The
  10 STALE are honest — the underlying files are ~2.1 h old against 300–3600 s bounds,
  because the system has been idle. A monitor is a measurement *at a moment*; the numbers
  age, so do not quote them as current without re-measuring.

## Verifying a change to the UI

Route tests do not prove a page renders. Two defects here — a **blank page** and a literal
`[object Object]` tile — passed 55/55 server checks, a 200 response, correct HTML and a clean
console, and were found **only by looking at it**.

```powershell
# needs the deployment up
cd C:\Users\apviz\.minimax-agent\projects\SENTINEL_PRIME\08_SELF_IMPROVEMENT
python final_browser_proof.py     # the 11 original panels
python test_deployment.py         # the deployment itself, non-destructive
python test_deployment.py --coldstart  # + proves logon recovery (destructive)
```

Use the full interpreter path — `Get-Command python` resolves to the Microsoft
Store stub on this machine, which is not an interpreter. Measured: 30 passed / 0
failed / 1 not-run non-destructive, 31 / 0 / 0 with `--coldstart`, exit 0 both.

There are now **12 tabs** (Ecosystem was added for the MINIMAX hub). **Open the page and
look at it as well** — that step found the two defects the script could not.

## Deployment lessons that cost real time

Each of these produced a *silent* failure. None of them announced itself.

- **`Out-Host` breaks a script driven with redirected output.** `docker stop … | Out-Host`
  worked from a console and did nothing through a pipe — and because
  `$ErrorActionPreference = 'Stop'`, the whole branch died *before* the command ran. A
  verification tool that only works when a human is watching it is not a verification
  tool. Write to the output stream instead.
- **Never let a `.bat` be built with `+` inside an `@( … )` array literal.** `'a' + $x + 'b', 'c'`
  makes `'b', 'c'` an *array*, and `string + array` coerces with spaces. The lines merge
  and the arguments land in the wrong place. Use a here-string with `.Replace()`.
- **`Set-Content` does not normalise newlines inside a multi-line string.** A generated
  `.bat` can come out with bare LF endings that `cmd.exe` does not reliably honour.
  Force CRLF and assert it.
- **`start "" … -Command "…"` is not the same as `-File "path"`.** `start` applies its own
  quoting rules and mangles a multi-line quoted `-Command`.
- **A generator must verify its own output.** `install-startup` now refuses to write a
  `.bat` it has not structurally checked, and reads the file back off disk rather than
  trusting the variable it just built.
- **A suite needs a precondition.** Run against a deployment that was not running, the
  first version reported 12 `FAIL`s that all said "connection refused". Every one was true
  and not one was a defect.
- **A check that cannot fail is not a check.** `front == back` passed green with both
  planes dead, because a refused connection returns `0` and `0 == 0`.
- **Enumerating addresses with a nested-quote PowerShell one-liner through `subprocess`
  returns nothing on Windows** — the quotes do not survive re-quoting, PowerShell exits 1,
  and an empty result reads as "no such address exists". That silently skipped the
  loopback claim. Enumerate in Python.
- **`/api/stream` reconnect cadence needs the SSE `retry:` field.** Without it Chromium
  reconnects every ~3 s and re-reads the whole state file to obtain bytes that cannot have
  changed — measured 21 deliveries in 62 s where 3 is correct.
- **A function that is defined but never called is not a code path.** The ecosystem
  refresh was written into `Start-RefreshWorker` — a complete, correct function that
  nothing ever invoked. The real worker was a `Start-Job` further down the same file. The
  panel served a snapshot that aged to 27 minutes and never moved, with no error anywhere
  and every other check green. It is invisible to the parser, the linter and the reader,
  and it looks exactly like working code. **Find the caller before you trust the callee.**
- **A `Start-Job` has its own session state.** `$PY`, `$WORKSPACE` and every other
  script-scoped variable are `$null` inside the job unless passed through `-ArgumentList`.
  A call wrapped in `try/catch` will not reveal that, because nothing throws — the
  variable is simply null.
- **A native command exiting non-zero does not throw in PowerShell 5.1.** `& $stub
  script.py` that does nothing at all looks identical to success from the outside. Check
  `$LASTEXITCODE` explicitly, or the failure is invisible forever.
- **A non-null tool path is a claim, not evidence.** `Get-Command python` here returns the
  Microsoft Store stub, which exists, is non-null, and is not an interpreter. Resolve,
  then *verify* the candidate actually runs.
- **A port that answers 200 is not proof of what is serving it.** A stray `sentinel-cc.ps1`
  once bound 8910 directly. 8910 kept answering 200 after the container stopped, every
  "is the link up" probe said yes, and **every teardown was unable to take effect** because
  the process being stopped was not the process holding the port. The failure got reported
  as a broken startup path — which was working perfectly — for several cycles.
  `status` now answers `VERDICT HIJACKED` and names the pid; `stop` clears strays on the
  front port; `test_deployment.py` asserts the deployment header. **Only the header
  distinguishes a hijacked front from a healthy one.**
- **`HttpListener` again.** A hijack must be identified by **command line**, never by the
  socket — see the HTTP.sys note above. The socket owner is pid 4.
- **A timeout is not a bound on a process that leaves something behind.** The
  cold-start suite "hung" three times at 290/900/1800 s and was not hanging at
  all — it runs in 134 s. `subprocess.run(..., capture_output=True)` waits for
  pipe EOF, and the `start` verb legitimately leaves a long-lived backend that
  inherits the pipes, so EOF never comes. `timeout=` does **not** rescue it:
  Python kills the already-exited direct child and re-enters the same blocking
  read, making the timeout decorative for exactly the case it appears to
  protect. Give the child a **file** and kill the **tree** on timeout.
  `run_tool()` in `test_deployment.py` is the reference implementation.
- **A failing child names a token, never the line that produced it.**
  `"-ExecutionPolicy Bypass"` written as one argv element is a *command* to
  PowerShell, not a switch/value pair; it dies with "the term
  '-ExecutionPolicy' is not recognized". That silently disabled the `stop` verb,
  so the cold-start teardown did nothing while reporting a plausible error.
  Log `subprocess.list2cmdline(argv)` untruncated — the list had 11 elements
  where it needed 12, and no amount of reading the child's error would show it.
- **A gateway answering 200 is not a serving deployment.** With the backend
  dead, `/healthz` returns 200 and every other route returns 502. Any
  precondition asking only the gateway reports "already serving" and judges a
  dozen checks against a dead app. Ask **both** planes, as `status` does.
- **A fix applied to the instance that failed is not a fix applied to the
  class.** The bare-LF `.bat` bug was fixed in the Startup entry; an audit
  found `bat\sentinel-cc.bat` and five version backups still LF-only.
  `every_bat_is_crlf` now walks the live tree. The `backups\versions\v*` copies
  are excluded **by decision**: they are inert historical snapshots and
  rewriting them to satisfy a lint would falsify the version record. Prove any
  such exclusion is not a no-op — the first version of it compared a
  non-normalised `..\` path against `abspath`'d paths, matched nothing, and
  shipped.
- **A line of output that looks like evidence but was decoration.** `status`
  printed `loopback  127.0.0.1 only - not reachable off-box` as a fixed string,
  whatever was true. It is now measured: every routable non-loopback IPv4 is
  probed with a 1.2 s connect, the line names the count and the addresses, and
  the verdict becomes `UP BUT EXPOSED` with exit 1 if any of them answers.
  Sabotage-proven in both directions. Timeout and refused both count as "not
  reachable", so a firewall cannot be mistaken for a leak.
- **A check that overstates what it proves buys confidence in the wrong
  place.** `install_skills.py --check` printed "matches the project source
  byte-for-byte" while actually proving that *re-rendering* the source
  reproduces the installed file. Same class of fault, same session.
- **A test that passes through a different code path than the one it is named
  after is worse than no test.** A security test sent `{"action": ...}` to a
  route that reads `$parsed.id`. Every payload came back 400 — so the test
  passed, seven times, having never once consulted the whitelist. It had been
  sitting unexecuted in the phase list the whole time. Assert on the refusal
  **body**, not just the status code, so a refusal from any other path cannot
  satisfy it. The same phase list also named a function that did not exist
  (`test_x_admits_approved` vs `test_x_admits`) — a `NameError` that would have
  killed the suite the first time that phase ran. Phases are now resolved **by
  string**, so one stale symbol reports itself and names itself, instead of
  destroying the evidence from every other phase.
- **A "find problems" check with no scoping finds other people's problems.**
  The stray-listener check matched every `server.ps1` on the machine, so it
  failed four times blaming this deployment for the OPTIMUS Control Center on
  port 8900 — a different system, read-only, never ours to touch. `Get-ServerOnPort`
  now requires `SENTINEL_PRIME` in the command line and refuses a
  `$RESERVED_PORTS` list outright, reporting those as "seen, deliberately not
  stopped". Always scope a fault-finder to your own system, and make the
  refusal visible.
- **A failure message that describes a probe nobody performed.** `container_health`
  read Docker's `Health.Status`, saw `starting`, and printed "the front is not
  answering /healthz" — while `/healthz` had answered 200 two checks earlier.
  `starting` is Docker's own start_period: an *unconcluded* measurement, not a
  negative one. The check now waits for the state to settle and reports the
  actually-measured `/healthz` status beside it.
- **A check must not record its own remedy as a failure.** `ensure_deployment_up`
  recorded FAIL for "not serving yet" — the precise condition it exists to fix
  — then PASS once the start worked, so a *successful* cold start exited 1.
- **A detector that fires on correct data is worse than no detector.** "Any list
  over 25 is an unbounded feed" flagged `checks=55`, which is a static inventory:
  one entry per check function in `monitor.py`, bounded by how much code exists
  rather than by elapsed time. Capping it would mean deleting real
  measurements. The check now separates **feeds** (streams, capped — the log
  tail, measured live) from **inventories** (complete, not capped — required to
  match the count the payload itself declares), and re-arms itself against a
  known-oversized list on every run, because a re-scoped detector nobody
  re-proved is the one most likely to be silently vacuous.
- **A panel must be measuring the instance that is answering it.** The ecosystem
  snapshot refreshed on every 4th worker cycle, so a freshly started server had
  no snapshot of its own for the first ~100 s and `/api/minimax` served the
  *previous* instance's file — correctly timestamped, which is the least useful
  state available: it looks like a live hub and is not. Measured: a cold start
  reported the snapshot as 1163 s old while the server serving it was 110 s old.
  The first collection now runs the ecosystem collector before the listener
  opens; the 4-cycle cadence is the steady-state refresh.
- **A background job's output stream is not a log.** `Start-Job` writes to a
  stream only `Receive-Job` can read, and nobody called it — so a collector that
  broke every cycle looked exactly like a healthy one. The refresh worker now
  appends to `09_LOGS\refresh-worker.log`. Staleness is the detector; that file
  is the diagnosis.
- **An artefact nothing can read is decoration with extra steps.** The lifecycle
  verifier wrote `verify-report.json` every run, and both its own docstring and
  `README.md` claimed the Overview panel displayed it. Nothing read it. Rather
  than delete the claim, the route `/api/verify` and an Ecosystem-panel tile were
  added — and the verifier now asserts its own report is *reachable*, not merely
  written.
- **`$port` and `$Port` are the same variable.** PowerShell variable names are
  case-insensitive, so a local `$port = 0` inside a function silently rewrote
  the script's `$Port` for the rest of the run. Every `IsFront` test then
  compared 8900 against itself and returned true, so the OPTIMUS Control Center
  on 8900 was reported as squatting the front port 8910 — four FAILs, and a
  precise reintroduction of the false positive the previous round had just
  removed. This constraint is written in the project's own conventions and was
  still walked into, so it now has a check:
  `no_case_shadowed_params` scans every `.ps1` for an assignment whose name
  collides in case with a *declared parameter*. Proven non-vacuous by
  re-injecting the exact line into a copy: 0 hits clean, 1 hit broken.
- **A filter that scopes a fault-finder can blind it.** Requiring
  `SENTINEL_PRIME` in a command line removed four false failures — and then
  evaded a real squatter launched by relative path, from a copy, or through
  `sentinel-cc.ps1`. Scans are now wide, identity is classified **by port**, and
  an unattributable process is *named* rather than dropped: a check that reports
  PASS because its own filter found nothing is reporting its method, not the
  system's state.
- **A detector that truncates its own walk is green while broken.** The FIFO
  audit recursed only into the first 25 elements of any list, so a 26-entry
  list at index 3 was caught and the identical list at index 30 was invisible —
  and its self-test used index 0, so the guard passed without ever reaching the
  hole. The recursion now visits every element under an explicit node budget,
  reports "scan incomplete" rather than reporting clean, and self-tests a case
  nested **past** position 25.
- **The documented start command must be the supported one.** `README.md` told
  the reader to run `bat\sentinel-cc.bat`, which binds `server.ps1` onto 8910 —
  the container's own port — recreating the exact `HIJACKED` state the anti-hijack
  gate exists to catch. Documentation that contradicts the architecture is a
  defect in the same class as code that does: a reader who follows it produces
  the failure. `sentinel-hub.ps1` is the only supported entry point, and the
  README now says so loudly, with the reason.

## Verifier scope, and what it deliberately does not gate

`verify-server.ps1` drives `sentinel-hub.ps1` — the same verbs the Startup
`.bat` uses — and stops the deployment first, so every cycle begins from a known
state. It never spawns a private server: an earlier single-plane version bound
8910 itself, collided with the container, killed the live backend in its
pre-clean, and then measured 502s from an nginx it did not own. Sixteen FAILs,
none of them about the product.

Two things it reports but does **not** gate, because each belongs to a different
system than the one it is testing:

- the **monitor's verdict**, printed as a `[note]` and carried in the report as
  `monitor_overall` — "does the deployment serve the health report" and "is the
  system healthy" are separate questions;
- the verdict `/api/verify` serves **mid-cycle**, which is the *previous* run by
  definition — asserting PASS there would assert a stale file is fresh.

The first version printed a green `PASS` tag directly beside `overall=FAIL`,
which is how a reader learns to stop believing the tag. A check is now named for
what it asserts (`GET /api/health (serves report)`) rather than for the route it
hits.

## Boundaries

- **Loopback only.** The container front publishes `127.0.0.1:8910`; the backend is
  `127.0.0.1:8912`. Port 8900 belongs to `90_CONTROL_CENTER` (its own front is 8901); none
  of the three may collide. `test_deployment.py` proves 8910 refuses on every non-loopback
  address on the machine, rather than assuming it.
- **Never deploy this publicly.** It would expose the verbatim corpus on the open internet.
  Popy declined public deployment for this phase. The container carries a TLS position
  ready for that day and nothing more.
- The Cockpit mutates. It is gated by R0. Do not invoke an action the operator has not
  ratified.
- `90_CONTROL_CENTER` is **read-only reference material**. Do not modify it.
