# MiniMax OPTIMUS Control Center

Live operations console for the whole MiniMax → OPTIMUS integration.

**Design:** built on the Hermes design SOT — "Obsidian Telemetry Dark".
Source (**never touch**): `C:\Users\apviz\AppData\Local\hermes\desktop-plugins\design-system\Design_Schema\`
Working copy for the MiniMax side: `projects\95_DESIGN_SOT\`
Captured as a skill: `mavis-hermes-design-sot`

## Start it

```bat
cc start
```
or double-click `bat\start-dashboard.bat`

Opens `http://127.0.0.1:8900/`. Close the console window to stop the server.

> **Open it over HTTP, never by double-clicking `index.html`.** A page loaded as
> `file://` has no server behind it and can never reach the API. The page detects
> this and tells you so, but the fix is the URL above.

## Version control

`bat\manage-versions.ps1` keeps frozen rollback snapshots in `backups\versions\`.

```powershell
.\bat\manage-versions.ps1 -List
.\bat\manage-versions.ps1 -Note "what changed and why"
.\bat\manage-versions.ps1 -PruneOldest     # ONLY when Popy says so
```

Rules it enforces:

- A snapshot is **frozen** once written. Never edited, never moved.
- **Maximum five.** A sixth is **refused**, and the script names the oldest and
  stops. It never auto-deletes — deciding when a baseline dies is Popy's call.
- `-PruneOldest` exists so deletion is always an explicit instruction.

| Version | What it is |
|---|---|
| v0.1 | Baseline before the descriptive-text and design makeover |
| v0.2 | Descriptive legend + Obsidian makeover. Functionality identical. |

## Routes

| Route | Purpose |
|---|---|
| `GET /` | the dashboard |
| `GET /api/state` | live state JSON, refreshed every ~35 s by a background worker |
| `POST /api/action` | run a whitelisted action, return its output |
| `GET /api/health` | server self-check + action list |

`/api/state` is **genuinely live**: a persistent background job re-collects and
writes `api\live-state.json`; requests only ever read that file, so a poll costs
~0.01 s. The UI shows the data age beside the clock, so a stale snapshot can
never masquerade as live.

## Security posture

- Binds **127.0.0.1 only** — never reachable off-box.
- `POST /api/action` takes only an **id**, never a command. The id is looked up
  in a whitelist defined in `api\server.ps1`, so a crafted request cannot
  execute arbitrary shell. Verified: an unknown or injected id returns **400**.
- Action output is size-capped.

## Tabs

Eleven tabs. Each carries a heading stating the question it answers, a note on
what it contains, and a domain colour from the design SOT chromatic wheel.

Overview · Docker · Bridges · Services · Qwen · Hermes Update · MiniMax ·
Skills · Projects Sections · Documentation · Command Center

The **Command Center** is the action cockpit: 14 buttons, each with its title, a
plain-English description, and the exact command line underneath so anything can
be re-run by hand from a normal shell.

## Files

| File | Role |
|---|---|
| `index.html` | the dashboard (self-contained, no external assets) |
| `api\collect-state.ps1` | measures the whole system, emits JSON |
| `api\server.ps1` | loopback HTTP server, action whitelist, live refresh worker |
| `api\guard-compose.ps1` | validates and, if needed, rebuilds `docker-compose.yml` |
| `api\live-state.json` | written by the refresh worker; what requests actually read |
| `bat\cc.bat` | the command bar |
| `bat\manage-versions.ps1` | version snapshots, five-cap, explicit prune |
| `bat\start-dashboard.bat` | launches the server and the browser |
| `bat\guard-compose.bat` | the compose guardian |
| `backups\versions\` | frozen rollback snapshots |

## Command bar

`cc <command>` is on PATH and mirrors the dashboard actions:

```
cc start            open the dashboard
cc guard            check / repair docker-compose.yml
cc status           one-screen system status
cc doctor           deep health check
cc census           container counts
cc bridge health    both bridges
cc sot list         show the SOT links
cc refresh          rebuild the SOT index
cc skills           list Mavis skills
cc qwen status      Qwen diagnosis
cc compose          validate docker-compose.yml
cc ai auth          MiniMax CLI auth
```

`optimus <command>` is the broader entry point and covers much more.

## The compose guardian

`docker-compose.yml` was found **deleted** on 2026-10-02, leaving 18 running
containers as orphans with no definition on disk — unrecoverable by a prune, a
Docker restart, or `compose up --remove-orphans`.

`cc guard` proves the file is present, proves it parses, keeps a dated backup of
every good copy, and rebuilds it from live container state if it ever vanishes.
Recovery is verified: 18/18 services, with containers untouched.
