# 00 — REBUILD FROM SCRATCH

**You have no idea what this project is. Read this file first.** It is written for
exactly that situation. Everything you need is in this `_DOCS` folder plus the
code tree alongside it.

---

## 1. What you are looking at

A single-machine operations console for a 58-container AI swarm, served at
`http://127.0.0.1:8900/` on loopback. It is three files of real logic and one
static page:

| File | Role |
|---|---|
| `90_CONTROL_CENTER\api\server.ps1` | the HTTP server (PowerShell `HttpListener`, port 8900) |
| `90_CONTROL_CENTER\api\collect-state.ps1` | measures the machine, prints one JSON blob |
| `90_CONTROL_CENTER\index.html` | the entire UI — no framework, no build step |
| `scripts\cc-watchdog.ps1` | the supervisor that keeps the server alive |
| `90_CONTROL_CENTER\bat\cc.bat` | the `cc` command bar |

There is **no npm install, no package.json, no bundler**. If you find yourself
running `npm install`, you have misunderstood something.

---

## 2. The four files, in dependency order

```
collect-state.ps1   measures → prints JSON to stdout          (~18 s)
        ↓ stdout
server.ps1          runs it, writes api\live-state.json atomically,
        ↓          serves that file on GET /api/state
index.html          polls /api/state every 5 s, renders 15 tabs
        ↑                  ↑
cc-watchdog.ps1  keeps server.ps1 alive    cc.bat  the CLI
```

**Nothing calls `index.html` except a browser.** It is a static file. It has no
build step and no server-side templating.

---

## 3. To rebuild it from an empty machine

### First, choose your path — RESTORE or RECONSTRUCT

There are two, and they are not equivalent. Read this before touching anything.

**A. RESTORE** — copy this folder's code tree back over the live tree. Fastest,
and it reproduces the exact build that was verified.

**B. RECONSTRUCT** — ignore the files and rebuild from these documents and
`03_TREES\`. Slower, and it is the only path that works on a machine where the
junctions below cannot be satisfied.

**Whichever you pick, `BACKUP-MANIFEST.json` in the folder root is the authority
on what is real.** It records the exact files copied on the most recent pass
(path + byte count), the 13 junctions **with the target each one pointed at**, and
the 76 hard links that were copied as ordinary files. Five things it will not tell
you, all of which will bite you if you browse the folder instead of reading it:

- **The folder may hold files the manifest does not list.** The last refresh was
  an *overlay*, which copies but never deletes, so ~43 files that were deleted
  from the source since the previous run are still sitting here. They are ghosts.
  The manifest is right; the directory listing is not.
- **The 13 junctions point OUTSIDE this folder** — at absolute paths under
  `C:\Users\apviz\`. **This folder is not self-contained for them.** A restore
  recreates the junction *structure*; the *targets* have to be re-established
  separately or the links dangle and every skill/MCP tree reads as empty.
- **The `_DOCS` folder is not in the manifest**, by design: it lives inside the
  backup root, which the copy walk skips so the backup cannot contain itself.
- **`BACKUP-MANIFEST.json` describes one pass, not this folder's whole contents.**
- **A file being present is not a file being valid.** Before you trust the restore,
  extract the inline `<script>` from `index.html` and run `node --check` on it. A
  page whose script does not parse still answers `HTTP 200` forever, serves
  perfect `/api/state` data, writes nothing to any log, and renders a dead
  skeleton. That is not hypothetical — it happened here, and every transport-level
  signal stayed green. See `05_POSTMORTEMS.md` #8.

### Step 0 — know what you are assuming
Read `02_DEPENDENCIES.md`. It lists every tool with the version measured on the
machine this was built on. Anything marked `NOT FOUND` was not on PATH.

### Step 1 — the containers
```powershell
docker ps                                    # expect 58
docker ps --format '{{.Names}}' | Select-String 'hermes-mcp-'
```
The `hermes-mcp-*` fleet (31) is **load-bearing**. The compose project is at
`C:\Users\apviz\docker-compose.yml`.

> **NEVER** `docker container prune -a` — the swarm was lost this way on
> 2026-08-08. **NEVER** `docker rm -f hermes-mcp-*`. **NEVER** `--remove-orphans`
> against the `apviz` project; it owns `Antigravity_Ecosystem_Terminal`.

### Step 2 — write the collector
It must, in this order: docker → bridges → services → MiniMax → history →
supervision → one JSON to stdout. **Three non-negotiable rules:**

1. **Every external call gets a timeout.** Use `Start-Process` + `WaitForExit(ms)`
   for subprocesses. For HTTP, set **both** `Timeout` and `ReadWriteTimeout` —
   `Invoke-RestMethod -TimeoutSec` only bounds the headers; the body read is a
   separate 300 s default. This exact omission froze the dashboard for 19.5 hours.
2. **Serialise a plain `Hashtable`, not an `OrderedDictionary`.** In Windows
   PowerShell 5.1 `ConvertTo-Json` on an ordered tree of this shape can simply
   never return. Use the `Convert-ToPlain` helper at the bottom of the file.
3. **Do not add a log line by hand when a data file already says it.** The
   one place that went wrong is catalogued in `05_POSTMORTEMS.md`.

### Step 3 — write the server
`HttpListener` on `127.0.0.1:8900` only. Never `0.0.0.0`.

- Read `index.html` with `[IO.File]::ReadAllText(path, UTF8)` — **not**
  `Get-Content -Raw`, which assumes ANSI for a BOM-less file in PS 5.1 and
  mangles every `·` and `…` into `Â·` and `â€¦`.
- Write the state file atomically: temp file, then `[IO.File]::Replace`.
  Two writers writing in place collide ("used by another process") and a reader
  can catch a half-written file.
- Set response headers **before** writing the body, and guard the header write —
  a client that disconnects leaves the response already committed and re-setting
  `ContentLength64` throws.

### Step 4 — write the page
Copy `index.html` structure: a `:root` block of colour/scale tokens, a modular
1.25 type scale, one `<style id="pass-…">` layer per increment, and a
`<script>` holding the state fetch + render. Additive layers, ordered so later
rules win. Do not edit an existing rule to make a change — add a layer.

### Step 5 — wire the supervisor
Copy `cc-watchdog.ps1` verbatim if you can. If you rewrite it, keep all four of:

- health = port **and** fresh state (a listening socket proves nothing)
- **3 consecutive failures** before acting, never one
- **150 s grace** after any restart
- log every state change with a reason, so a restart is explained, not just counted

### Step 6 — make it survive the machine
```powershell
cc install        # registers scheduled task OPTIMUS_ControlCenter (at logon)
cc watchdog       # run it now
cc health         # must print "supervised: HEALTHY"
```

---

## 4. How to know you got it right

Do not trust a green message. Check these, in this order:

```powershell
# 1. the collector completes, and how long it takes.
#    Normal is ~20 s, and the bridges section alone is ~9 s of that - two serial
#    doctor probes. The hard timeout is 240 s ($CollectTimeoutSec), raised from
#    the original 90 s because a ~20 s collect on a 20 s cycle had zero headroom.
#    Past 240 s it is WEDGED, not merely slow: nothing has ever taken that long.
Measure-Command { powershell -NoProfile -File api\collect-state.ps1 > $null }

# 2. the server binds
Test-NetConnection 127.0.0.1 -Port 8900

# 3. the API answers, and the data is FRESH
(Invoke-RestMethod http://127.0.0.1:8900/api/state).generated

# 4. supervision is real
cc health

# 5. the page renders — open it in a BROWSER. An HTTP 200 proves nothing
#    about rendering. Screenshot it.
```

Then the real test: **kill the server process and time how long until it is
back.** If that is more than ~60 s, the supervisor is not doing its job.

---

## 5. The traps, in the order they will bite you

| Trap | Symptom | Fix |
|---|---|---|
| `ConvertTo-Json` on an `OrderedDictionary` | collector never returns, no error | serialise a plain hashtable |
| `Invoke-RestMethod -TimeoutSec` | body read blocks up to 300 s | set `ReadWriteTimeout` too |
| `Get-Content -Raw` on a BOM-less file | `·` becomes `Â·` | `[IO.File]::ReadAllText(…, UTF8)` |
| `@{ k = @($genericList) }` | `ArgumentException: Argument types do not match` | `.ToArray()` |
| `if ($item.LinkType)` | hard-linked FILES treated as junctions and silently dropped | test `LinkType -eq 'Junction'` |
| a name a system binary owns (`Clip`) | PowerShell runs `clip.exe` instead of your function | never name a helper after a Windows binary |
| a `[style*="…"]` substring matcher | matches a longer unintended value | use a real class |
| a single-element array through JSON | `.map is not a function` in the browser | normalise with `Array.isArray` |

Each of these is a real bug that shipped in this project. All are written up
with evidence in `05_POSTMORTEMS.md`.

### One warning about the tools themselves

**The browser tool you will reach for leaks.** Every `agent-browser` navigation
spawns an `agent-browser-mcp-server`, and each one holds a headless Chrome open
for the life of the client session. **Calling `browser_close` does not help** — it
closes the tab, not the process (measured: 31 -> 30 shells, RAM free unchanged).

Eight had accumulated over fifteen hours, holding ~3 GB, on a 63.9 GB machine that
was already showing 5.7 GB of Windows Memory Compression. If you are investigating
memory pressure, **the instrument is part of what you are measuring** — say so
before recommending a fix.

And the reaper cannot clean it up on its own: `reap-mcp.ps1` rescans with
`Name='node.exe'` on every pass, so orphaned `chrome-headless-shell` children are
**never candidates**. As of this writing it reports the gap rather than hiding it,
but closing it needs a second candidate set — Popy's call, because it widens what
the tool is allowed to stop.

---

## 6. Where to go next

| You want to… | Read |
|---|---|
| understand the running system | `03_TREES\PROCESS_TREE.md` |
| understand why it exists | `03_TREES\STRATEGIC_TREE.md` |
| operate it / fix something | `03_TREES\OPERATIONS_TREE.md` |
| change it without breaking it | `03_TREES\LOGIC_TREE.md` |
| find a file | `03_TREES\FILE_TREE.md` (generated from disk) |
| know what to install | `02_DEPENDENCIES.md` (measured, not remembered) |
| learn from our mistakes | `05_POSTMORTEMS.md` |

**Read the postmortems before you write code.** Every one of those bugs produced
green output while being wrong. That is the single most important thing to know
about this project.
