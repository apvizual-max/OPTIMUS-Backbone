# SENTINEL Command Center — local deployment

**Status: MEASURED and live.** Every number below was produced by running the
thing, not by reading it. The commands to reproduce each one are given.

Deployment built by **Mavis** (MiniMax Code agent) for Popy.
Container: `mavis-sentinel-hub` · Image: `mavis/sentinel-hub:1.0.0` · Front: `127.0.0.1:8910`

---

## The two planes

| Plane | Where | What it owns | Why there |
|---|---|---|---|
| **Backend** (data plane) | Windows PowerShell, `127.0.0.1:8912` | every measurement | it reads Windows-only facts: WMI, `Get-NetTCPConnection`, the Docker Windows engine, the runtime's own files. A Linux container cannot read those. |
| **Front** (web plane) | container `mavis-sentinel-hub`, publishes `127.0.0.1:8910` | the address, health gating, TLS position | it is the same shape a public deployment takes. |

The front holds **no copy** of the dashboard. It proxies to the backend. A
baked-in copy would drift from the data that was actually measured, and a
dashboard reporting numbers nobody measured is worse than no dashboard. The
test suite asserts this from inside the image (`image_has_no_data`).

**Why the front owns 8910 and not the backend:** 8910 is the address already in
Popy's browser, in the skills, in the UI text and in the reports. Keeping the
published port constant meant the deployment changed and nothing he reads had
to. Port **8900 belongs to the separate OPTIMUS Control Center** and its front
is 8901; nothing here reads or writes either.

### Naming: what was built, and what the spec text said — UNRESOLVED

The 10-section harness document Popy supplied specifies a different identity
from the one that is deployed. **This is recorded, not decided.** Popy has not
yet ruled, and the config deliberately follows his own spoken instruction.

| Element | Harness document says | What is deployed | Origin of the deployed name |
|---|---|---|---|
| Container | `gemini-minimax-hub` | `mavis-sentinel-hub` | Popy: *"include your name so we know you made it"* |
| Image | `gemini/minimax-hub:1.0.0` | `mavis/sentinel-hub:1.0.0` | same |
| Deployment header | `X-GEMINI-Deployment` | `X-SENTINEL-Deployment` | same |
| Orchestrator script | `gemini-hub.ps1` | `sentinel-hub.ps1` | same |
| Container label | `sentinel.owner=gemini` | `sentinel.owner=mavis` | same |
| Startup entry | `GEMINI MINIMAX Control Center.bat` | `SENTINEL Command Center.bat` | same |

Why the deployed names were chosen: the instruction to include the builder's
name is Popy's own, given directly. The `gemini-*` names appear only inside a
pasted specification that reads as though written for a different assistant to
execute. A direct instruction outranks a quoted document, and a rename would
also break Popy's bookmark, the UI text and the skills for no functional gain.

The functional requirements of that section are met in full regardless of the
prefix: dual-plane topology, loopback-only binding, the anti-hijack header gate,
zero baked-in data, and the 3-cycle lifecycle verifier. **If Popy rules for the
`gemini-*` names, the change is a rename plus a rebuild — the architecture does
not move.**

---

## Operating it

```powershell
$hub = 'C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\SENTINEL_PRIME\13_COMMAND_CENTER\api\sentinel-hub.ps1'

powershell -NoProfile -ExecutionPolicy Bypass -File $hub status     # both planes + verdict
powershell -NoProfile -ExecutionPolicy Bypass -File $hub start
powershell -NoProfile -ExecutionPolicy Bypass -File $hub stop
powershell -NoProfile -ExecutionPolicy Bypass -File $hub restart
powershell -NoProfile -ExecutionPolicy Bypass -File $hub logs       # container logs
```

`status` names **which plane** is missing, because a gateway that is up while
its app is down is a different fault with a different fix:

```
VERDICT  DEGRADED (front up, backend down)
```

Exit code is `0` for `UP` and `1` for anything else, so it can gate a script.

### Endpoints

| Path | Served by | Meaning |
|---|---|---|
| `/` | front → backend | the dashboard |
| `/healthz` | **front only** | is the gateway alive. Answers even when the backend is dead — that separation is the point. |
| `/readyz` | front → backend `/api/state` | is the thing behind the gateway alive |
| `/api/state`, `/api/health`, `/api/corpus`, `/api/history` | backend | the measured data |
| `/api/stream` | backend | Server-Sent Events |
| `/api/minimax` | backend | the local MINIMAX ecosystem snapshot |

---

## At logon

`%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\SENTINEL Command Center.bat`

No elevation, no scheduled task, no service, no registry. **To remove it,
delete that one file.** It runs `sentinel-hub.ps1 -Action start`, which brings
up the backend and then the container, in that order — starting the front first
would produce a gateway that answers `/healthz` while `/readyz` says no, which
looks like a working deployment for exactly as long as nobody reads the second
path.

Output and the exit code go to `09_LOGS\hub-startup.log`.

**Measured, from fully down:** the entry brought both planes up in under 180 s
(`startup_cold_start` in the suite). It was tested from a known-down state
because a startup path that has only ever been checked while everything is
already running is not a path.

### Two startup failures that had to be found this way

Both were **silent** — the deployment simply came up dead at logon:

1. `start "" /min powershell -Command "& '...' -Action start"`. `start` applies
   its own quoting rules and a multi-line quoted `-Command` argument is
   precisely what it mangles. Now uses `-File` with one quoted path, and the
   suite has a permanent guard that **fails** if `-Command` reappears.
2. The generator built the `.bat` with `+` concatenation inside an `@( … )`
   array literal. That is not concatenation: `'a' + $x + 'b', 'c'` makes
   `'b', 'c'` an *array*, and `string + array` coerces with spaces, so the
   lines merged and the ports landed in the wrong place. Replaced with a
   here-string plus `.Replace()` placeholders.

The generator now **refuses to install** a file it has not structurally
verified: exactly two well-formed `set` lines, exactly one whole
`powershell …` line containing the action and both ports, no unsubstituted
placeholder, and CRLF throughout (`Set-Content` does not normalise newlines
*inside* a multi-line string, so a `.bat` can be written with bare LF endings
that `cmd.exe` does not reliably honour).

---

## Not public — and proven, not assumed

Bound to `127.0.0.1`. The suite connects to this machine's own routable
addresses and requires refusal:

```
loopback_only: 8910 refused on 3 non-loopback address(es):
               172.18.240.1, 172.21.224.1, 192.168.1.193
```

The first version of that check reported `NOT_RUN` on a machine that plainly
has a LAN IP: the PowerShell one-liner it used to enumerate addresses returned
**nothing** while exiting 1, because `subprocess` re-quotes the argument and
the nested quotes do not survive. An empty result was read as "no non-loopback
address exists". It now enumerates in pure Python. A check that cannot run is
worse than no check when it silently skips the claim that matters most.

Public deployment is **not authorised** and is deliberately not done: it would
expose the verbatim corpus on the open internet.

---

## Rebuilding the front

```powershell
cd C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\SENTINEL_PRIME\13_COMMAND_CENTER\deploy
docker build -t mavis/sentinel-hub:1.0.0 -t mavis/sentinel-hub:latest .
docker stop mavis-sentinel-hub; docker rm mavis-sentinel-hub
docker run -d --name mavis-sentinel-hub --restart unless-stopped `
  -p 127.0.0.1:8910:80 `
  --label sentinel.role=deployment-front --label sentinel.owner=mavis `
  --label sentinel.public=false mavis/sentinel-hub:1.0.0
```

`restart=unless-stopped` is the swarm convention here, and it is what makes the
container return after a Docker restart or a reboot.

### Gate the build, do not trust it

```powershell
docker run --rm --entrypoint sh  mavis/sentinel-hub:1.0.0 -c "wc -c < /etc/nginx/conf.d/default.conf"
docker run --rm --entrypoint nginx mavis/sentinel-hub:1.0.0 -t
```

This exists because of a bug that cost one build: the Dockerfile did
`COPY nginx.conf …/default.conf` and then `RUN rm -f …/default.conf`, which
deletes **this project's** config and leaves nginx with no server block — it
starts cleanly and 404s everything, which reads as a routing bug in the host.

---

## Tests

```powershell
cd C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\SENTINEL_PRIME\08_SELF_IMPROVEMENT
python test_deployment.py             # non-destructive
python test_deployment.py --coldstart # also tears down and proves logon recovery
```

**Measured 2026-10-05, with `--coldstart`:** `39 passed / 0 failed / 0 not-run`,
exit 0, including a real teardown and real recovery (front back in 42.3 s).

The counts in this paragraph have been superseded twice, and the history is
kept because a number in a document that nobody re-measures is a false claim
quietly becoming true:

| Written | Measured | State |
|---|---|---|
| "0 not-run" unconditionally | non-destructive `30 / 0 / 1` | wrong — `startup_cold_start` is `NOT_RUN` without the flag |
| `30 / 0 / 1` and `31 / 0 / 0` | — | superseded 2026-10-05 |
| — | `39 / 0 / 0` with `--coldstart` | current |

See `deployment-tests.json`.

The five checks added since that count was taken, and what each one is really
for:

- `action_missing_id_refused` — a body with no `id` is refused for its **own**
  reason. Separate from the whitelist on purpose, so neither can be satisfied by
  the other. The whitelist test used to send `{"action": …}` to a route that
  reads `$parsed.id`; every payload came back 400, so it passed seven times
  having never consulted the whitelist.
- `action_whitelist_admits` — a whitelisted action (`logs_tail`) is **accepted**.
  Without this, a route that refuses everything would satisfy the rejection test.
- `telemetry_detector_armed` — the FIFO detector re-proves it can still fail,
  every run, against a 26-entry list. A re-scoped detector nobody re-armed is the
  one most likely to be silently vacuous.
- `log_feed_within_bound` — the actual 25-entry bound, measured live on the one
  stream the harness governs. The log feed returned exactly 25 lines.
- `inventories_complete` — inventory lists are **not** capped, but must match the
  count the payload itself declares, which catches a truncated report. The first
  version flagged `checks=55` as an unbounded feed; that is a static inventory,
  and a detector that fires on correct data is worse than no detector.

Run it with the full interpreter path. `Get-Command python` on this machine
resolves to the Microsoft Store stub, which is not an interpreter:

```powershell
$py = 'C:\Users\apviz\AppData\Local\Python\pythoncore-3.14-64\python.exe'
& $py -u test_deployment.py --coldstart
```

`--coldstart` is destructive by design: it stops the deployment, waits for both
ports to actually free, then launches the Startup entry and requires the
deployment to return on its own. It takes about three and a half minutes, most of
it the 62 s SSE reconnect window and the bring-up polls. Phase boundaries are
traced to stderr, flushed, so a stall names the phase it stalled in rather than
just timing out.

Five rules the suite keeps:

- **A precondition is established first.** The first version had none, and
  reported 12 `FAIL`s that all said "connection refused" because it had been
  run against a deployment that was not running. Every one was true and none
  was a defect. If the deployment cannot be brought up, that is one `FAIL` and
  the dependent checks are `NOT_RUN`.
- **A precondition must be able to fail in the direction that matters.** Asking
  only the gateway was not enough: with the backend dead, `/healthz` answers
  **200** while every other route answers 502. The precondition now requires
  both planes, as `status` does.
- **A check that cannot fail is not a check.** `front_matches_backend`
  originally asserted `front == back`, and `http_code()` returns `0` when the
  connection is refused — so **0 == 0 passed green with both planes dead**. It
  now requires both to be serving. Proven by sabotage in all three directions.
- **A switch and its value are separate argv elements.** `"-ExecutionPolicy
  Bypass"` written as one string is a *command* to PowerShell, not a
  switch/value pair; it fails with "the term '-ExecutionPolicy' is not
  recognized", which blames a token and hides the line that produced it. That
  silently disabled the `stop` verb, so the cold-start teardown did nothing.
  `verb_argv_not_joined` now fails the suite if a pair is ever fused again.
- **Every `.bat` in the project is CRLF, not just the one under test.** An
  independent audit found the superseded `bat\sentinel-cc.bat` still LF-only
  long after the identical bug was fixed in the Startup entry — the shape of a
  fix applied to the instance that failed rather than to the class.
  `every_bat_is_crlf` now walks the whole project. `.ps1` and `.py` are excluded
  deliberately: they read LF correctly, and a check that flags correct files is
  a check you learn to ignore.
- **The command line that was actually built is logged, untruncated.** A failing
  child names a token, never the line that produced it. `run_tool` writes
  `subprocess.list2cmdline(argv)` into the log header before anything runs.

One trap worth knowing before you script this yourself: do **not** run the
orchestrator from Python with `subprocess.run(..., capture_output=True)`. The
`start` verb leaves a long-lived backend behind, that server inherits the pipes,
and `communicate()` waits for an EOF that never comes. The `timeout=` argument
does not rescue it — Python kills the already-exited direct child and re-enters
the same blocking read. Give the child a **file**, and kill the process **tree**
on timeout. `run_tool()` in `test_deployment.py` is the working reference.

---

## Known limits, stated rather than hidden

- **An agent cannot leave a long-lived process running.** Agent-spawned
  processes are reaped with the process tree. The durable instances are the
  Startup-folder entry and `explorer.exe`-launched ones; both are outside the
  agent's tree.
- **`/api/stream` is short-lived by design.** The backend is a single-threaded
  `HttpListener`; holding a response open would block every other route. It
  sends state, flushes, closes, and `EventSource` reconnects. The reconnect
  interval is pinned with the SSE `retry:` field to the collector cadence —
  without it Chromium reconnected every ~3 s and re-read a 76 KB state file to
  obtain bytes that could not have changed (**measured 21 deliveries in 62 s;
  now 3**).
- **The MINIMAX live roster/session list is `NOT_AVAILABLE`.** There is no
  `mavis`/`mcodectl` executable on PATH, so a host-side collector cannot ask
  for it. Everything else in that panel is read from the runtime's own files
  and is measured regardless.
