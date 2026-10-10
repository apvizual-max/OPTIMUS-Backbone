# OPERATIONS TREE

Everything an operator or a new AI has to be able to *do*, and the order to do it
in. This is the "and then what?" tree.

## Day-zero: bring the console up from nothing

```
console is down
  │
  ├─ 1. is the machine up?              Get-CimInstance Win32_OperatingSystem
  │     └─ down → nothing else matters
  │
  ├─ 2. is the supervisor alive?        Get-CimInstance Win32_Process |
  │     │                                  Where-Object CommandLine -like '*cc-watchdog*'
  │     ├─ yes → it will self-heal; wait 30 s, go to step 5
  │     └─ no  → cc watchdog
  │
  ├─ 3. supervisor running but console down?  read 90_CONTROL_CENTER\logs\watchdog.log
  │     ├─ repeated "UNHEALTHY" → the collector is failing; run step 4 by hand
  │     └─ silent               → server never bound; check server.err.log
  │
  ├─ 4. is the collector healthy?       Measure-Command { powershell -File
  │     │                                api\collect-state.ps1 > $null }
  │     ├─ ~18 s, prints JSON  → healthy
  │     └─ hangs past 240 s   → collect-state is blocked; see 05_POSTMORTEMS §1
  │
  └─ 5. verify                          cc health
        ├─ "supervised: HEALTHY"     → done
        └─ "NOT SUPERVISED"          → cc install  (registers the logon task)
```

## Everyday commands

| Command | What it does | When |
|---|---|---|
| `cc start` | opens the dashboard in a console window | manual, when not auto-started |
| `cc watchdog` | runs the supervisor in the foreground | debugging supervision |
| `cc install` / `cc uninstall` | registers / removes the logon task | one-time setup |
| `cc health` | supervised? how many restarts? exit 0 healthy / 1 unhealthy / 2 unsupervised | scripts, cron, quick check |
| `cc status` | one-screen system status | "is anything on fire" |
| `cc doctor --deep` | every diagnostic from both bridges | something looks wrong |
| `cc guard` | check / repair `docker-compose.yml` | after any compose edit |
| `cc bridge health` | both MiniMax bridges | bridge questions |
| `cc qwen doctor` | transport / session / model provider | Qwen prompt failures |
| `cc sot list` | junctions + hard links in the SOT index | SOT questions |

## Investigating a change

```
something changed
  │
  ├─ Trends & Incidents  → what moved, when, and what else moved with it
  │     median baselines, not averages, so one spike cannot hide behind itself
  │
  ├─ "samples" line       → if it is 0 or tiny, the baseline is still building.
  │                         A quiet system records a sample only on a REAL change.
  │
  └─ container drill-down → click any row on Docker for its full record
```

## Diagnosis order that actually holds up

1. **Is it up at all?** `cc health`. A dead console explains everything else.
2. **Is the data fresh?** the `age` beside the clock, and the Resilience tab.
3. **Is the collector the problem?** time it by hand (§day-zero step 4).
4. **Is a bridge the problem?** `cc bridge health`, then read the check `detail`
   — that string used to be silently dropped from the AI briefing.
5. **Only then** chase the specific container or service.

## The escalation ladder

| Symptom | First move | Never |
|---|---|---|
| console blank / white page | open it as `http://`, not `file://` | double-clicking `index.html` |
| "collector unreachable" | `cc watchdog` | deleting `live-state.json` by hand |
| numbers frozen | check `age`; the refresher is a separate job | restarting the server — it will not fix a dead refresher |
| a container vanished | `cc guard`, then `docker ps` | `docker container prune -a` |
| Qwen prompts fail | `cc qwen doctor` — the model provider is the blocker, not the protocol | re-enabling an MCP transport that does not exist |

## Maintenance rhythm

| Cadence | Task |
|---|---|
| every 5 s (automatic) | collector → state file |
| every 30 s (automatic) | supervisor health check |
| every 20 s (automatic) | browser polls `/api/state` |
| weekly | `scripts\repair-mojibake.ps1 -Recurse` — checks encoding, changes nothing |
| on demand | `cc doctor --deep` |
| before any risky change | the quarantine backup (see `00_REBUILD_FROM_SCRATCH.md`) |
