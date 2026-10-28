# ACT XII — Docker local deployment (the container that makes it a system)

**Mandate:** anchor the Command Center in two places — the Docker environment and the
Windows startup environment — deployed as it would be publicly, reachable on this
machine, not public yet. Built by **Mavis**. Public deployment was explicitly
**declined** by Popy in the mandate, so the loopback-only constraint stands and is
now *proven* rather than asserted.

---

## 1. The architecture, and why it is shaped this way

Two planes, deliberately in different places:

| Plane | Where | Owns | Why there |
|---|---|---|---|
| **Backend** (data plane) | Windows PowerShell, `127.0.0.1:8912` | every measurement | it reads Windows-only facts — WMI, `Get-NetTCPConnection`, the Docker Windows engine, the runtime's own files. A Linux container cannot read those. |
| **Front** (web plane) | container **`mavis-sentinel-hub`**, publishes `127.0.0.1:8910` | the address, health gating, the TLS position | it is the same shape a public deployment takes. |

**The front holds no copy of the dashboard.** It proxies to the backend. This was not a
shortcut — it was the only defensible choice. A baked-in copy would drift from the data
that was actually measured, and a dashboard reporting numbers nobody measured is worse
than no dashboard. The suite asserts it from inside the image (`image_has_no_data`).

**The pattern was learned, not invented.** The sibling project
`90_CONTROL_CENTER` (read-only, never touched) already runs `mavis-optimus-control-center`
as an nginx deployment front on 8901 proxying a host PowerShell service on 8900, with
`/healthz` and `/readyz` separated for exactly the reason above. That precedent was
verified live before being copied.

**8910 stayed constant on purpose.** It is the address already in Popy's browser, in the
skills, in the UI text and in the reports. The backend moved to 8912 *internally*, so the
deployment changed and nothing he reads had to.

---

## 2. What was built

| Artefact | Path |
|---|---|
| Image | `mavis/sentinel-hub:1.0.0` (nginx:alpine, config baked in) |
| Container | `mavis-sentinel-hub`, `127.0.0.1:8910:80`, `restart=unless-stopped` |
| Dockerfile + nginx.conf | `13_COMMAND_CENTER\deploy\` |
| Orchestrator | `13_COMMAND_CENTER\api\sentinel-hub.ps1` (start/stop/restart/status/logs/install-startup/uninstall-startup) |
| Lifecycle verifier | `13_COMMAND_CENTER\api\verify-server.ps1` (3 cycles, both planes, 75 checks) |
| Deployment tests | `08_SELF_IMPROVEMENT\test_deployment.py` |
| Ecosystem collector | `08_SELF_IMPROVEMENT\collect_minimax_ecosystem.py` |
| Documentation | `13_COMMAND_CENTER\DEPLOYMENT.md`, `13_COMMAND_CENTER\README.md` |

The two counts in this table were first written as "26 checks" and "14 surfaces" and
both were **stale the moment they were written** — a plan that quotes a number it has
not re-measured becomes a false claim quietly. Corrected against the run of
2026-10-05:

| Figure | First written | Measured 2026-10-05 |
|---|---|---|
| Deployment checks | 26 | **39** (cold start: 39 passed / 0 failed / 0 not-run) |
| Ecosystem surfaces | 14 | **21** (20 `MEASURED`, 1 `NOT_AVAILABLE`, 0 errors) |
| Lifecycle verifier checks | not present | **75** passed / 0 failed / 0 not-run, 3 cycles |

Logon anchor: `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\SENTINEL Command Center.bat`
— no elevation, no scheduled task, no service, no registry. **Removed by deleting that one
file.** It writes `09_LOGS\hub-startup.log` including the exit code.

---

## 3. Defects found and fixed

### 32 — the Dockerfile deleted its own configuration *(caught before it shipped)*

`COPY nginx.conf /etc/nginx/conf.d/default.conf` followed by
`RUN rm -f /etc/nginx/conf.d/default.conf`. The COPY **overwrites** the stock file at that
path, so the `rm` deletes *this project's* config and leaves nginx with no server block.
nginx starts cleanly and 404s everything — a silent failure that reads as a routing bug
in the host. Removed, and the build is now gated: assert the config is inside the image,
then `nginx -t`, before anything publishes a port.

### 33 — a startup entry that could not work, and could not say so *(found only by running it)*

The Startup `.bat` used `start "" /min powershell -Command "& '...' -Action start"`. At
logon **both planes stayed down and nothing anywhere recorded why.** `start` applies its
own quoting rules and a multi-line quoted `-Command` argument is precisely what it mangles.
Now `-File` with a single quoted path, and `startup_uses_file_not_command` is a permanent
guard that **fails** if `-Command` reappears.

### 34 — the `.bat` generator produced structurally corrupt output

The generator built lines with `+` inside an `@( … )` array literal. That is not
concatenation: in `'a' + $x + 'b', 'c'`, `'b', 'c'` forms an **array**, and
`string + array` coerces with spaces — so lines merged and the ports landed in the wrong
place. Proved in isolation (both forms side by side), then replaced with a here-string and
`.Replace()` placeholders.

The installer now **refuses to write** a file it has not structurally verified: exactly
two well-formed `set` lines, exactly one whole `powershell …` line carrying the action and
both ports, no unsubstituted placeholder. It caught the very next defect by itself.

### 35 — a `.bat` with Unix line endings

`Set-Content` does **not** normalise newlines *inside* a multi-line string, so the generated
file carried bare LF endings that `cmd.exe` does not reliably honour. The generator now
forces CRLF and asserts `LF == CR` before writing.

### 36 — the loopback check silently skipped the claim that matters most

`loopback_only` reported `NOT_RUN` on a machine that plainly has a LAN IP. The PowerShell
one-liner used to enumerate addresses returned **nothing while exiting 1**: `subprocess`
re-quotes the argument on Windows and the nested quotes do not survive, so PowerShell
failed with `Unexpected token 'and'`. An empty result was read as "no non-loopback address
exists". Replaced with pure-Python enumeration (UDP `connect()` for the primary address —
sends no packets — plus `ipconfig` for every adapter). It now proves the claim on three
addresses including `192.168.1.193`.

### 37 — a check that could not fail

`front_matches_backend` asserted `front == back`. `http_code()` returns `0` when the
connection is refused, so **0 == 0 passed green with both planes dead.** It now requires
both to be serving. Proven by sabotage in all three directions (both dead, front dead,
backend dead → all FAIL; both live → PASS).

### 38 — a suite with no precondition

The first deployment run reported **12 FAILs that all said "connection refused"** because
it had been run against a deployment that was not running. Every one was true and not one
was a defect — a red that measures the wrong thing trains the reader to ignore red. The
suite now brings the deployment up first; if it cannot, that is one FAIL and the dependent
checks are `NOT_RUN`.

### 39 — a reconnect storm, and a false claim about it *(pre-existing, live)*

`/api/stream` is short-lived **by design** (single-threaded `HttpListener`; holding a
response open would block every other route), and `EventSource` reconnects. But the
`retry:` field was missing, so Chromium reconnected every ~3 s and re-read the 76 KB state
file each time — **measured 21 deliveries in 62 s**, while the code comment claimed "the UI
updates at the collector's cadence". The claim was false by ~8×, in the expensive
direction. Fixed at the producer with the SSE `retry:` field the spec provides:
**21 → 3 deliveries in 62 s**, exactly the 25 s cadence.

I first filed this as a truncation defect. It was not — the short close is deliberate and
documented. My probe's expectation was wrong, and the correct response was to correct the
expectation, not the product.

### 40 — a comment in `nginx.conf` describing a mechanism that does not exist

My own first draft justified a 24 h read timeout by claiming a 300 s timeout would "cut a
healthy stream and the UI would reconnect every five minutes forever". That describes a
stream that does not exist. Corrected in place, with the correction kept visible — a
mechanism written into a comment that the code does not have is the same defect as a
comment written where a check belongs.

### 45 — a stray backend squatting the front port, making a stopped deployment look alive *(the one that masked everything else)*

`startup_cold_start` failed across several consecutive runs. The teardown verb was
proven working (5.2 s, `rc=0`, front down in 2.0 s, container `exited`) — measured directly,
repeatedly. So the teardown was exonerated and something else was keeping the port.

A stray `sentinel-cc.ps1` had bound **8910 directly** (pid 26880, started 06:12:36) instead
of the backend's 8912. It had no `X-SENTINEL-Deployment` header, because it was not nginx.
Consequences:

- `8910` kept answering **200** long after the container was stopped, so the deployment
  looked alive when it was not.
- **Every teardown was unable to take effect** — the check was trying to stop a process
  that was not the process holding the port — and reported itself as a failure of the
  *startup path*, which was working perfectly. Several diagnostic cycles were spent
  chasing the wrong component.

> **A hijacked front is indistinguishable from a healthy one by status code alone.** Only
> the deployment header tells them apart. Every "is the link up" probe in the system said
> yes, and was wrong.

Fixed at both the tool and the test:

1. `Test-FrontIsHijacked` in `sentinel-hub.ps1` — probes the header, and on a mismatch names
   the squatter's pid. `status` now reports `VERDICT HIJACKED` and exits 1.
2. `stop` now clears strays: any SENTINEL `server.ps1` bound to the **front** port is
   ended, because that address belongs to the container. Verified — `killed pid 26880 - a
   backend on the FRONT port 8910`, after which both ports were genuinely free.
3. `test_deployment.py` gained **`front_not_hijacked`**, asserting the header and naming
   the pid, so this can never again be mistaken for a healthy front or a broken startup.

**Measured:** `status` on the hijacked system → `HIJACKED front 8910 answers but is not the
container`, exit 1. After `stop` → stray killed, 8910 and 8912 both free.

### 44 — a function that was defined and never called *(the deepest one)*

The ecosystem refresh was written into `function Start-RefreshWorker` in `server.ps1`.
That function was **dead code** — defined, complete, syntactically valid, commented, and
invoked exactly zero times. The real refresh worker was a `Start-Job` further down the same
file, which knew only about `collect-sentinel.ps1`.

So the Ecosystem panel served a snapshot that had aged to **27 minutes** and never moved
again. No error, no exception, no log line, and every other check in the deployment suite
green. Restarting the server could never have fixed it, because the code that was supposed
to run was not the code that ran.

> **A function that is defined but never called is not a code path.** It is invisible to the
> parser, to the linter and to every reader, and it looks exactly like working code. The
> only thing that exposed it was asking a question nothing had asked before: *how old is
> this file, and who is supposed to be writing it?*

Three fixes, all at the producer:

1. The dead function is **deleted**, with a comment at its old location saying it was dead
   and where the real worker is. Leaving it would be leaving the trap armed.
2. The ecosystem refresh moved into the `Start-Job`, with **everything passed through
   `-ArgumentList`** — a job has its own session state, so `$PY` and `$WORKSPACE` are
   `$null` inside it. The job now also checks `$LASTEXITCODE`, because a native command
   exiting non-zero does **not** throw in PowerShell 5.1 and the failure was therefore
   structurally invisible.
3. **`test_deployment.py` gained `ecosystem_snapshot_fresh`** — a check on the snapshot's
   *age*. Nothing was measuring it, which is precisely why a dead refresh path survived
   unnoticed. Plus `ecosystem_route`, which requires a non-empty surface list so an
   unmeasured ecosystem cannot render as an empty one.

**Proven fixed:** with the stale file moved aside and the server restarted, the worker's
own refresh wrote a new snapshot — **age 43 s** at first observation.

### 42 — a non-null interpreter path that was not an interpreter *(silent, and long-lived)*

`server.ps1` resolved Python with `Get-Command python`. On this machine that returns

```
C:\Users\apviz\AppData\Local\Microsoft\WindowsApps\python.exe
```

which is the **Microsoft Store stub**. The file exists, the path is non-null, and invoking
it does nothing — it is not an interpreter. The check `if (-not $PY) { throw }` therefore
passed on a value that could not run a single line of Python.

The failure was silent and had been for a long time: the refresh worker invoked the
ecosystem collector every 4th cycle with that stub, the native command exited without doing
anything and **without raising** (PowerShell 5.1 does not turn a non-zero native exit into
a terminating error), and the Ecosystem panel served a snapshot that had aged to **27
minutes** with no error in any log. `health.json` kept refreshing because
`collect-sentinel.ps1` resolves Python its own way — which is exactly why the fault hid:
the neighbouring file proved the system was alive.

> **A non-null path is a claim about a tool, not evidence of one.** The resolver now tries
> candidates and accepts one only if it actually prints a Python version, and it throws if
> none does. Verified on every start rather than trusted on every call.

### 43 — a cold-start check that probed once, 4 s after teardown

`startup_cold_start` reported "teardown did not take effect" even after the `Out-Host` fix,
while the identical teardown had just been measured working (5.3 s, both ports down,
container `exited`). The container stop and the port release are not simultaneous, and a
single probe landing in that gap reports a teardown that is merely **still in progress** as
one that did not happen. The check now polls for up to 45 s — still failing if the system
never goes down — and reports what it actually observed when it does.

---

## 4. The MINIMAX ecosystem bridge

A 12th panel, **Ecosystem**, served at `/api/minimax` from
`minimax-ecosystem.json`.

**The honest constraint that shaped it:** there is **no `mavis`/`mcodectl`/`minimax`/`mcode`
executable on PATH** (measured, not assumed). A collector that shelled out to one would
report a permanently empty panel, or worse, invent numbers. So it reads the runtime's own
files, and where a surface genuinely cannot be measured it says `NOT_AVAILABLE` and names
the reason.

**Measured: 13 surfaces MEASURED, 1 NOT_AVAILABLE, 0 errors** — 6 agents
(`coder, explore, general, mavis, verifier, worker`), 61 skills (10 SENTINEL), the live MCP
configuration, sessions, memory, integrations, config/permission/channel files.

A finding worth carrying: the **live** runtime `mcp.json` declares **14** MCP servers
(`hermes-mcp-router`, `qwen-mcp-http`, `docker-mcp`, `git-mcp`, `obsidian-mcp`,
`notebooklm-mcp`, `chrome-devtools-mcp`, `agent-browser-mcp`, `mcp-server-filesystem`,
`gdrive-mcp`, `gmail-mcp`, `google-workspace-mcp`, `google-calendar-mcp`,
`qwen-acp-adapter`). `SENTINEL_PRIME/07_BACKBONE/mcp/OPTIMUS_MCP_CONFIG.json` is a
**different** config with 9 entries, 7 of them dead. They are not the same thing, and the
7 dead ones are not what the runtime uses.

**Verified in a real browser** (a 200 proves nothing about whether a page renders):
12 tabs present, panel activates on click, 4 tiles, 14 rows, **0 console errors**, no
`[object Object]` coercion, no double-escaped entities. Every collector string goes through
`esc()` — `detail` is free prose assembled by a Python collector and is the most likely
place for a quote or `<` to reach the DOM.

---

## 5. Regression

| Suite | Result |
|---|---|
| `test_suite.py` (data plane) | **288 passed, 0 failed, 0 skipped, exit 0** |
| `DashboardBoot` / `DashboardSurface` / `UiNoObjectCoercion` | 10/10 · 31/31 · 12/12 |
| `corpus_extractor.py verify` | all integrity checks OK — 955 messages, retention 1.0000, sha256 `e4d3cbb7…7e0e42`, idempotent |
| `install_skills.py --check` | exit 0, 5/5 byte-identical to source |
| `test_deployment.py --coldstart` | see §3.11 — **26 passed / 1 FAILED**, then fixed and re-run |

### 41 — the teardown tool silently did nothing when redirected *(the one failure)*

The suite reported `startup_cold_start: teardown did not take effect - the test would
prove nothing`. The check **refused to claim a pass it had not earned**, which is why it
is written that way — but the cause was not the startup path under test.

`sentinel-hub.ps1 -Action stop` contained `docker stop $CONTAINER 2>&1 | Out-Host`. From
an interactive console that worked perfectly (measured 17.5 s, both ports down, container
`exited`, still down at +5 s and +20 s). Driven with its output **redirected** — which is
how the test harness invokes it, and how any scheduled task or CI step would — it did
nothing at all. `Out-Host` targets the console host explicitly; with stdout a pipe there
is no console, the statement never completed, and because `$ErrorActionPreference` is
`Stop` the entire `stop` branch died **before `docker stop` ran** and before the backend
was touched. The deployment stayed fully up, so the cold-start check correctly concluded
its own precondition had failed.

**Proven fixed by re-running the exact failing invocation:** redirected stop now returns
`returncode=0` in 5.3 s, front `200 → 0`, backend `200 → 0`, container `running → exited`.

> A verification tool that only works when a human is watching it is not a verification
> tool. The `stop` verb had been exercised many times from a console and had never once
> been exercised the way its only automated caller uses it. The test was not wrong to
> fail; it was the only thing in the system that had been honest about the state.

---

## 6. The cold-start gate: two defects behind one symptom

The cold-start gate had never completed in a single clean run. Three attempts were
truncated by my own Bash time limits at 290 s, 900 s and 1800 s, and I recorded
the cause as "the suite hangs". **That conclusion was wrong**, and it was wrong
in the most expensive way available: it was plausible, it fit the evidence I had,
and it sent three full runs into a wall.

Instrumenting the phase boundaries (flushed stderr, one timestamped line per
phase) disproved it on the first attempt. The suite runs in **134 s**. Nothing
was hanging. Two real defects were stacked underneath.

### Defect 46 — a timeout is not a bound on a process that leaves something behind

`ensure_deployment_up()` started the deployment with
`subprocess.run(..., capture_output=True, timeout=240)`. The `start` verb
legitimately leaves a long-lived backend server behind, and that server inherits
the stdout/stderr pipes. `communicate()` reads until EOF, EOF only arrives when
*every* holder of the write end has exited, so it never returned.

The decisive evidence was not the timeout, it was the process table: the suite
sat frozen at `+2.3s invoking the start verb`, far past its 240 s budget, while
`Get-CimInstance` showed the test process had **no descendants at all**. The
process holding the pipe was an orphan whose parent had already exited. And the
`timeout=` argument could not have helped — on expiry Python kills the *direct*
child, which has already exited, and re-enters the same blocking read. **The
timeout was decorative for precisely the case it appeared to protect.**

Fixed by `run_tool()`: the child's output goes to a **file**, never a pipe, so
waiting on the direct child is sufficient and correct; on timeout the whole
**process tree** is killed with `taskkill /T`, because a start that did not
finish must not leave half a deployment behind. The startup entry is now spawned
with `stdin/stdout/stderr=DEVNULL` for the same reason, one level up.

After the fix: `start verb returned rc=0` in 24.3 s.

### Defect 46b — a fused `"-Flag Value"` is a command, not a switch/value pair

With the hang gone, the cold-start check failed for a different reason: the
`stop` verb returned `rc=1` in 2.3 s with

```
-ExecutionPolicy : The term '-ExecutionPolicy' is not recognized ...
At line:1 char:1
+ -ExecutionPolicy Bypass -File C:\...\sentinel-hub.ps1 -Action stop ...
```

`run_ps` built its command list with `"-ExecutionPolicy Bypass"` as a **single
element containing a space**. PowerShell received one quoted argument, treated it
as the command to execute, and died blaming a token while hiding the line that
produced it. `start` was unaffected only because a different caller built its
list correctly — the same script, the same machine, one working verb and one
silently inert verb.

It survived because the failure evidence was truncated to 220 characters and
because the suite never logged the command line it actually built. Both are now
fixed: `run_tool` writes `subprocess.list2cmdline(argv)` into the log header
before anything runs, and the detail is no longer truncated. That single line
ended a two-hour bisect — the list had **11 elements where it needed 12**, which
no amount of reading the child's error message would ever have revealed.

The cold-start check itself behaved correctly throughout: it refused to claim a
pass when its teardown had not taken effect, and said so in the output. That
refusal is the reason this was found at all.

**New permanent gate:** `verb_argv_not_joined` asserts no argv element contains a
space unless it is an existing path, so a fused switch/value pair fails the suite
rather than quietly disabling a verb.

### Defect 47 — a gateway answering 200 is not a serving deployment

Found by accident, in the middle of the fix: with the backend killed and the
container up, `/healthz` returned **200** while `/readyz` and every other route
returned **502**. The precondition asked only the gateway, so it would have
reported "deployment already serving" and judged a dozen checks against a dead
app. Same family as the earlier `front == back` check that passed on `0 == 0`.

`ensure_deployment_up` now requires **both** planes, exactly as `status` does.

### Result

A single clean `--coldstart` run, end to end, with a real teardown underneath it:

```
31 passed / 0 failed / 0 not-run   (31 checks)     green=True
```

Regression, all measured after the fixes: `test_suite.py` **288 passed / 0 failed
/ 0 skipped** (exit 0); `corpus_extractor.py verify` all integrity checks OK
(exit 0, sha256 unchanged); `install_skills.py --check` exit 0, 5/5 byte-identical
to source; `sentinel-hub.ps1 status` → `VERDICT UP`, both planes agreeing.

> A run that is cut off by a timeout is not evidence of a hang. It is evidence
> that the thing being timed out could report where it stopped. The first
> question was never "why is it slow", it was "what is the last line it managed
> to print" — and that question had never been asked.

---

## 7. What the verifier found that I had not

The first independent verification returned **PARTIAL** — 9 of 10 claims plus the
cold start passed, and the failures were in *my claims*, not the deployment. All
three were real and are now fixed.

1. **An over-stated number.** I wrote "0 not-run" unconditionally. The
   non-destructive run is `30 passed / 0 failed / **1 not-run**` — `startup_cold_start`
   is skipped without the flag. `31/0/0` is only reachable with `--coldstart`.
2. **A fix applied to the instance that failed, not to the class.** The bare-LF
   `.bat` bug was fixed in the Startup entry. An audit found `bat\sentinel-cc.bat`
   still LF-only, plus five more under `backups\versions\v1..v5`. The live file is
   now CRLF and `every_bat_is_crlf` walks the whole project. The version backups are
   excluded **by decision, not by convenience**: they are inert historical
   snapshots, and rewriting them to satisfy a lint would falsify the record of what
   each version contained. The exclusion is proven non-vacuous — those five files
   each carry 27 bare LFs and would fail if included.
3. **An invariant covering 14 of 53 files.** `test_no_romanian_in_code` asserted
   against a hardcoded list. A file added after the list was written was simply
   never checked, so the check reported green while the guarantee it names did not
   hold. It is now a real `rglob` walk over every `.py`/`.ps1` (53 files, markdown
   exempt because the doctrine and quotes are *supposed* to carry diacritics).
   Suite total moved 288 → 327 for exactly this reason: +39 assertions.

The exclusion I first wrote for the backup tree **did not work** and I shipped it
into a run before noticing: `backup_root` was built from an unnormalised `..\` path
while the walked side was `abspath`'d, so the prefix could never match. An
exclusion that silently excludes nothing is worse than no exclusion, because it
reads as a decision and behaves as a no-op. Both sides are now normalised, and the
match is proven in both directions.

## 8. Two lines of output that looked like evidence and were not

The second verification passed all ten claims, then pointed at the same class of
defect in my own tooling: **decoration presented as measurement.** Both are fixed.

- **`status` printed `loopback  127.0.0.1 only - not reachable off-box` as a fixed
  DarkGray string.** It printed that regardless of reality. A status verb is read
  as evidence, and this line was a reassurance with nothing behind it — exactly the
  failure this system exists to remove. It is now measured: every routable non-loopback
  IPv4 is probed with a 1.2 s connect, and the line reports the count and the actual
  addresses. Proven by sabotage in both directions — with a listener on `0.0.0.0:8910`
  it goes **red** and names `192.168.1.193, 172.18.240.1, 172.21.224.1`; removing it
  restores green. A connect that times out and one that is refused both count as
  "not reachable", and only a completed connection counts as exposure, so a firewall
  cannot be mistaken for a leak. If it cannot be measured it says `NOT_MEASURED`
  rather than guessing.
- **A status verdict of `UP` while the port was reachable off-box.** Serving and
  *safe to serve* are different properties. `VERDICT` is now
  `UP BUT EXPOSED (front port reachable off-box)` with exit 1 in that case.
- **`install_skills.py --check` printed "matches the project source byte-for-byte".**
  It renders frontmatter around the source body, so a raw byte comparison is 0/5 by
  design. What is actually proven is that re-rendering reproduces the installed
  file exactly. The message now says that.

> A check that overstates what it proves is worse than no check, because it buys
> confidence in the wrong place. Three of these were mine, in this session, on a
> system whose entire purpose is that nothing reports green without having been
> measured.

---

## 9. The Desktop / Design / cloud-bridge bridge

The objective asked for a control hub over the local MINIMAX ecosystem, "including
the CLI agent and the desktop app for MINIMAX code", and specifically a
connection with MINIMAX Design. The first collector covered the *runtime* (agents,
skills, MCP, sessions, memory) and stopped there.

Discovery first, because a bridge to something that does not exist is worse than
no bridge. It all exists:

| Component | Where | Measured |
|---|---|---|
| MiniMax Code (desktop) | `%LOCALAPPDATA%\Programs\...`, 11-12 live processes | ~2.3 GB working set, largest 762 MB |
| MiniMax Design | `%LOCALAPPDATA%\Programs\MiniMax Design\MiniMax Design.exe` | installed, 3.0.21.85, **not running** |
| MiniMAX Hub | `C:\Program Files\MiniMaxHub` | installed, 2.0.3.219, not running |
| Task telemetry | `%APPDATA%\MiniMax Agent\observability-outbox.jsonl` | 462 events, 7 distinct kinds, newest minutes old |
| Embedded browser | `embedded-browser-tabs.json` | 1 session, 1 tab — the local→cloud path |
| Cloud bridge identity | `remote-control\state.json` | `desktop_device_id` present |
| Identity | `minimax-agent-config.json` | signed in; **token values never read** |

Seven new surfaces take the ecosystem panel from **14 to 21** (18 measured,
3 not-available, 0 errors), and the panel gained a *Desktop app, Design and cloud
bridge* block with tiles for live processes, telemetry volume, embedded tabs,
Design and Hub state, plus the bridge device id.

Design is installed but **not running**, so its local gateway under
`resources\gateway` is down and the surface says exactly that — `NOT_AVAILABLE`,
naming the reason — rather than reporting a port that is not listening.

**The collector's first version was wrong and caught itself.** It reported "no
MINIMAX Code process is running" while eleven were running. Three stacked causes:
`wmic` output parsed by splitting on whitespace, so the name `MiniMax Code.exe`
(two tokens) never matched; `wmic` is not on PATH on this machine at all, so the
query never ran; and `except Exception: return []` turned a missing tool into an
empty result that was then reported as a **finding**. Fixed by taking the data
from PowerShell `ConvertTo-Json` and by returning `(rows, error)` so a failed
query is reported as an error rather than absorbed into a zero. Verified against
`Get-Process` in the same instant — 12 processes, 2338 vs 2339 MB, agreeing — and
an earlier 11-vs-12 gap was confirmed to be genuine renderer churn, not a bug.

Two UI defects found by looking at the rendered page rather than the source:

- **An array concatenated into a string prints empty, not a count.** The tile read
  `1 session(s), host(s)` because `hosts` was `[]` and `[] + ' host(s)'` yields
  `' host(s)'`. It does not throw, so it looks correct. Same family as
  `[object Object]`.
- **The only console error on an otherwise clean page was a missing
  `/favicon.ico`**, requested by the browser rather than the app. Now an inline
  `data:` SVG, which cannot 404. Console: **0 errors, 0 warnings.**

The inline favicon then broke the suite's `no off-box resource is referenced`
check, because an SVG namespace declaration contains `http://www.w3.org/2000/svg`.
That check is a string scan and a namespace URI is a *name*, never a
dereferenced location, so the scan is imprecise rather than the product being
wrong. The whitelist gained exactly three literal strings (loopback origin, SVG
namespace, XHTML namespace) — not a pattern. **Proven non-vacuous by sabotage:** as
shipped 31/31; with a real `<img src="http://cdn.example.com/x.png">` injected it
drops to 30 and names it; restored, 31/31 again.

---

## 10. Still open

- **MCP A/B decision** — the 7 dead `OPTIMUS_MCP_CONFIG.json` entries. Deliberately left
  red and unedited; pruning or implementing them is Popy's call.
- **Public deployment** — declined in this mandate, as instructed.
- **Live agent roster / session list** — permanently `NOT_AVAILABLE` without a `mavis` CLI
  on PATH. Not a defect; stated in the panel.
