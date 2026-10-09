---
name: mavis-minimax-hermes-bridge-skill
description: Operate the minimax-hermes-bridge container (port 8801) — Mavis's Hermes system DOCTOR. Use when diagnosing Hermes (venv drift, container health, sentinel enforcement, MCP fleet), reading Hermes memory/config/logs, or delegating a task to the Hermes CLI agent. Triggers on "doctor Hermes", "is Hermes healthy", "why does hermes hang", "read Hermes config", "ask Hermes to do X".
---

# mavis-minimax-hermes-bridge-skill

Mavis is the **Hermes system DOCTOR**. This skill drives the `minimax-hermes-bridge` container.

## Container

| Property | Value |
|---|---|
| Name | `minimax-hermes-bridge` |
| Image | `optimus/minimax-hermes-bridge:1.0.0` |
| Port | `127.0.0.1:8801` |
| Network | `optimus-minimax_optimus` |
| Mounts | hermes agent (**rw**), hermes home (**rw**), sentinel daemon (ro), host bins (ro) |

## Start / stop

```powershell
cd C:\Users\apviz\.minimax-agent\projects\20_BRIDGES\minimax
docker compose -f docker-compose.yml up -d --build
docker compose -f docker-compose.yml ps
docker compose -f docker-compose.yml stop minimax-hermes-bridge
```

Never `docker compose down -v` (drops the audit journal volume).

## The four calls

```powershell
# 1. Liveness
Invoke-RestMethod http://127.0.0.1:8801/health

# 2. What can this bridge do
Invoke-RestMethod http://127.0.0.1:8801/schema

# 3. THE DOCTOR — run this first when anything is wrong
Invoke-RestMethod http://127.0.0.1:8801/doctor | ConvertTo-Json -Depth 6
Invoke-RestMethod http://127.0.0.1:8801/doctor/detailed | ConvertTo-Json -Depth 6

# 4. Read Hermes memory / state / logs
Invoke-RestMethod http://127.0.0.1:8801/audit | ConvertTo-Json -Depth 6
```

Delegate:
```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8801/delegate `
  -ContentType 'application/json' -Body '{"prompt":"status","timeout":120}'
```

## The one check that matters most

`hermes.venv_currency`. If it reports `state != current`, **every real hermes command hangs** while `--version` still answers — so casual testing gives a false green. Read-only probe:

```powershell
& 'C:\Users\apviz\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' -I -B -c `
  "import sys;sys.path.insert(0,r'C:\Users\apviz\AppData\Local\hermes\hermes-agent');` from hermes_cli.venv_sync import main;` sys.exit(main(['--project-root',r'C:\Users\apviz\AppData\Local\hermes\hermes-agent','--check','--json']))"
```

→ `{"state": "current"}` healthy · `{"state": "would-sync"}` out of date.

## Healing — R33: ask Popy first

Every healer mutates. `POST /heal` with a named `action`:

| action | Effect | R0 |
|---|---|---|
| `sync_venv` | `pm.sync_venv(..., evict_incompatible_plugins=True)` | required |
| `heal_enforcement` | restores the 4 sentinel booleans in `~/.hermes/config.yaml` | required |
| `restart_container` | restarts ONE container; **refuses non-`hermes-mcp-` names** | required |

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8801/heal `
  -ContentType 'application/json' -Body '{"action":"restart_container","name":"hermes-mcp-obsidian"}'
```

## Hard rules

- 🚫 **NEVER `docker container prune -a`** — the 2026-08-08 swarm loss.
- 🚫 The bridge has **no prune and no `rm -f` healer**, by design.
- ✅ Diagnose first, restart one container second, rebuild last.
- ✅ If `hermes.containers` warns, use `restart_container` for the named container only.

## Sentinel daemon awareness

The `hermes-sentinel-daemon` container audits **live agent responses** via
`SentinelGuardianAuditor.audit_text` and enforces 4 booleans. Checks
`hermes.sentinel_enforcement`, `hermes.sentinel_source`,
`hermes.sentinel_container`, `hermes.sentinel_http` cover it. See
`mavis-sentinel-daemon-skill` for the rule set.

## Cross-references

- Bridge source: `20_BRIDGES/minimax/minimax-hermes-bridge/`
- Group README: `20_BRIDGES/minimax/README.md`
- Sentinel: `mavis-sentinel-daemon-skill`
- Doctrine §10: `SENTINEL_OPERATIONAL_DOCTRINE.md`
