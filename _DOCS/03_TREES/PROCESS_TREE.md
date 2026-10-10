# PROCESS TREE

What is actually running, what started it, and what it depends on. Measured live
on 2026-10-04; container names and versions are real, not illustrative.

```
WINDOWS
│
├── powershell.exe  (supervisor)            ← scripts\cc-watchdog.ps1
│     │  started by:  scheduled task OPTIMUS_ControlCenter at logon
│     │  started by:  cc watchdog
│     │  loop: every 30 s -> Test-Health
│     │        ├─ TCP connect 127.0.0.1:8900            (3 s cap)
│     │        ├─ GET /api/state                          (60 s cap)
│     │        └─ served state younger than 300 s?       (else unhealthy)
│     │  on 3 CONSECUTIVE failures (not one - a slow collect is not a dead server):
│     │        ├─ Stop-Stale   kill leftover server.ps1 processes
│     │        └─ Start-Server powershell -File api\server.ps1 -Port 8900
│     │  on seeing chrome.exe with the console DOWN -> start it and show the page
│     └─ writes api\cc-health.json  (atomic Replace)
│
├── powershell.exe  (dashboard server)      ← api\server.ps1
│     │  binds 127.0.0.1:8900 ONLY via HttpListener (kernel: HTTP.sys, pid 4)
│     │        ⚠ the port is owned by System, NOT by this process. Killing pid 4
│     │          is not how you stop it - kill the powershell process instead.
│     │  request loop (single-threaded, one request at a time):
│     │        GET  /               -> index.html as UTF-8
│     │        GET  /api/state      -> read api\live-state.json, refresh if stale
│     │        GET  /api/health     -> action list + supervisor health
│     │        POST /api/action     -> run a real command, return its real output
│     │        POST /api/ask        -> MiniMax-M3 answers from a pre-digested state
│     │        GET  /api/journal    -> tail the bridge journal from the container
│     │
│     └─ Start-Job  (background refresher, every 20 s)
│           └─ powershell -File api\collect-state.ps1
│                 240 s HARD TIMEOUT - on expiry the child is killed and the
│                 previous state file is left untouched
│
├── powershell.exe  (collector)             ← api\collect-state.ps1   ~18 s
│     ├── docker ps / docker inspect            (58 containers, ~2 s)
│     ├── GET :8801/health + /doctor/detailed   (5 s + 8 s, BOTH timeouts set)
│     ├── GET :8802/health + /doctor/detailed   (5 s + 8 s)
│     ├── service probes 8080 / 8082 / 3001
│     ├── mcode-tools auth status               (~3 s)
│     ├── mcode-tools connector tools           (~3 s)
│     ├── git -C <hermes> log / status
│     ├── Get-NetTCPConnection  ONCE for all ports (was 5 calls = 10 s)
│     ├── append to api\state-history.jsonl     (only when a value CHANGED)
│     └── print one JSON blob to stdout
│           → server writes it to api\live-state.json atomically
│
├── docker  (the 58-container swarm)
│     ├── hermes-mcp-*  × 31   LOAD-BEARING. Never prune, never rm -f.
│     ├── minimax-hermes-bridge       :8801  Mavis ↔ Hermes
│     ├── minimax-antigravity-bridge  :8802  Mavis ↔ Antigravity (read-only mount)
│     ├── stirling-pdf                :8082  real HTTP API, no login
│     ├── libreoffice                 :3001  remote desktop, NOT an API
│     ├── apviz-honcho-db / -memory / -redis    app state store
│     └── apviz project owns Antigravity_Ecosystem_Terminal
│            ⚠ never `--remove-orphans` against the apviz project
│
├── qwen-acp-adapter                 :8765  ACP over WebSocket at /acp
│     │     ⚠ NOT an MCP server. /mcp is 404 by design. qwen-mcp-http is enabled
│     │       on purpose and still cannot connect - enabled ≠ working.
│     └── Qwen Studio 0.19.2 (no MCP transport exists)
│
└── chrome.exe
      └─ opens http://127.0.0.1:8900/  ← supervisor's hook, only if console was down
```

## Startup order that actually matters

1. Windows logon fires `OPTIMUS_ControlCenter` → supervisor starts.
2. Supervisor starts the server, then **waits 150 s before judging it** (grace).
3. Server pre-warms one collect inline (~18 s) before the browser is opened.
4. Refresher job takes over on a 20 s cycle; the server only ever *reads* the
   state file, so no request ever blocks on a collect.
5. From then on the supervisor only intervenes on 3 consecutive failures.

## Kill / restart semantics

| Symptom | What to do | What NOT to do |
|---|---|---|
| Server wedged, port open, state stale | `cc watchdog` (or wait 30 s) | kill pid 4 |
| Server process gone | nothing — supervisor restarts it | start a second copy |
| Container missing | `docker ps` to see which | `docker container prune -a` |
| Everything down | `cc watchdog` | deleting `_links` junctions |
