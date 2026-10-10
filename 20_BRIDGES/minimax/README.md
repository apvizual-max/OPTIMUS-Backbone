# Minimax Bridge Group — Architecture & Operations

**Date**: 2026-10-02
**Author**: Mavis (MiniMax Code orchestrator)
**Group name**: `optimus-minimax` (Docker Compose project)
**Purpose**: Mavis is the **Hermes system DOCTOR** and the **delegation hub** between the MiniMax Code ecosystem and the two other AI ecosystems on this station.

---

## 1. What this group is

Two containers, one per target ecosystem. Each is a dedicated connector that gives Mavis a uniform HTTP contract for **diagnosing**, **auditing**, and **delegating to** a target AI ecosystem.

| Container | Port | Target ecosystem | Mount mode | Role |
|---|---|---|---|---|
| `minimax-hermes-bridge` | 8801 | Hermes: CLI agent + Desktop app + 31 `hermes-mcp-*` containers + sentinel daemon | **rw** | Doctor + delegate + centralize |
| `minimax-antigravity-bridge` | 8802 | Antigravity: CLI (`agy.exe`) + IDE + App + Ecosystem Terminal container | **ro** | Council + delegate + memory-reader |

Naming rationale: `minimax-` prefix so anyone reading `docker ps` immediately knows the *source* AI is MiniMax Code, and the target ecosystem is explicit in the same name.

---

## 2. Uniform HTTP contract

Both bridges expose the **same** endpoints, so Mavis writes one integration and gets two.

| Method | Route | Returns | Purpose |
|---|---|---|---|
| GET | `/health` | liveness + self-report | Cheap poll |
| GET | `/schema` | full capability catalogue (checks, healers, audit sources, delegate spec) | Discovery |
| GET | `/doctor` | diagnostics, failures+warnings only | The DOCTOR view |
| GET | `/doctor/detailed` | all checks including `ok` | Full audit |
| GET | `/audit` | target memory / state / logs (read) | Centralize |
| POST | `/delegate` | `{prompt, project?, model?, timeout?}` | Dispatch to the target's agent CLI |
| POST | `/heal` | `{action, ...}` | Apply a named remedy |

All responses are JSON. Errors are returned as `{"ok": false, "error": "..."}` with HTTP 200 where the failure is diagnostic rather than transport-level.

---

## 3. Hermes bridge — the DOCTOR

### 3.1 Checks (12)

| id | Severity logic | What it proves |
|---|---|---|
| `bin.hermes` | fail if not on PATH | the CLI is reachable |
| `hermes.version` | fail on non-zero | the CLI actually runs |
| **`hermes.venv_currency`** | **fail if `state != current`** | **the single most valuable check** |
| `hermes.status` | fail on hang/timeout | the boot path is not broken |
| `hermes.dockerd` | fail if engine unreachable | Docker is up |
| `hermes.containers` | warn if any not Up, fail if none | the 31-container swarm is alive |
| **`hermes.sentinel_enforcement`** | **fail if any of 4 booleans wrong** | the guardrail is armed |
| `hermes.sentinel_source` | fail if source missing | daemon code present |
| `hermes.sentinel_container` | warn if not Up | daemon is running |
| `hermes.mcp_fleet` | warn if unavailable | Hermes's own MCP layer responds |
| `hermes.sentinel_http` | fail if :8399 unreachable | daemon HTTP health works |
| `hermes.home` | fail if missing | `~/.hermes` present |

**Why `venv_currency` matters most**: a venv out of sync with the lockfile makes every *real* hermes command hang, while `--version` and `pm` still answer — so casual testing gives a false green. The bridge runs the read-only probe:

```
python -I -B -c "import sys; sys.path.insert(0, <root>); \
  from hermes_cli.venv_sync import main; \
  sys.exit(main(['--project-root', <root>, '--check','--json']))"
```

→ `{"state": "current"}` healthy · `{"state": "would-sync"}` out of date.

### 3.2 Healers (3)

| action | Mutates | R0 required | Notes |
|---|---|---|---|
| `sync_venv` | venv + plugins | **yes** | calls `pm.sync_venv(..., evict_incompatible_plugins=True)`. Never triggered automatically. |
| `heal_enforcement` | `~/.hermes/config.yaml` | yes | restores the 4 enforcement booleans |
| `restart_container` | Docker | yes | **refuses any name not starting with `hermes-mcp-`**. One container only. |

There is deliberately **no prune and no `rm -f` healer**. The 2026-08-08 swarm loss makes that a permanent design decision.

### 3.3 Audit sources (8)

`~/.hermes/config.yaml`, `hermes-agent/cli-config.yaml` (the model wiring), `hermes-agent/.env`, `~/.hermes/.hermes_history`, `sentinel_daemon.py`, `hermes-agent/logs/`, `hermes-agent/gateway_state.json`, `hermes-agent/whatsapp/session/`.

### 3.4 Delegate

`POST /delegate {"prompt": "..."}` → `hermes.exe -z "<prompt>"`.
Hermes resolves the model from its own `cli-config.yaml`, currently **MiniMax-M3 via `minimax-oauth`**.

---

## 4. Antigravity bridge — the council

### 4.1 Checks (9)

`bin.agy`, `agy.version`, `agy.ide`, `agy.app`, `agy.agents`, `agy.memory`, `agy.past_work`, `agy.terminal_container`, `agy.terminal_http`, `agy.local_bin`.

Two of these are the memory-reading capability Popy asked for:

- `agy.memory` — proves Antigravity's state tree is readable, reports file count + bytes
- `agy.past_work` — parses `app_storage.json`, counts conversation/session keys

### 4.2 Healers (1)

`log_rotation` — reports log sizes and stale files. **Read-only; never deletes.** Popy's rule is small tasks and AI-council opinions only, so this bridge gets no mutation powers.

### 4.3 Delegate

`POST /delegate {"prompt": "..."}` → `agy.exe --print "<prompt>"`.

Useful Antigravity flags surfaced in the bridge spec for future use:
`--output-format json|stream-json`, `--conversation <id>` (resume Antigravity's own past work),
`--add-dir <path>` (grant a workspace), `--model`, `--effort`, `--sandbox`,
`--dangerously-skip-permissions`, `--mode accept-edits|plan`, `--remote-control`.

---

## 5. Deploy

```powershell
cd C:\Users\apviz\.minimax-agent\projects\20_BRIDGES\minimax
docker compose -f docker-compose.yml up -d --build
docker compose -f docker-compose.yml ps
```

Smoke test:
```powershell
Invoke-RestMethod http://127.0.0.1:8801/health
Invoke-RestMethod http://127.0.0.1:8801/doctor | ConvertTo-Json -Depth 6
Invoke-RestMethod http://127.0.0.1:8802/health
Invoke-RestMethod http://127.0.0.1:8802/doctor | ConvertTo-Json -Depth 6
```

Delegate:
```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8801/delegate `
  -ContentType 'application/json' -Body '{"prompt":"status","timeout":90}'
```

**Never** run `docker compose down -v` — it drops the `optimus_journal` volume where the bridges keep their audit trail.

---

## 6. Files

```
20_BRIDGES/minimax/
├── docker-compose.yml
├── shared/
│   └── minimax_bridge_core.py        # stdlib-only HTTP + check/heal framework
├── minimax-hermes-bridge/
│   ├── Dockerfile
│   ├── requirements.txt             # PyYAML only
│   ├── minimax_hermes_bridge.py
│   ├── README.md
│   └── schema.json
└── minimax-antigravity-bridge/
    ├── Dockerfile
    ├── requirements.txt
    ├── minimax_antigravity_bridge.py
    ├── README.md
    └── schema.json
```

Both bridges use `hermes-mcp-base:latest` (Python 3.14.7) so they share a known-good interpreter with the existing swarm and need no new image pull.

---

## 7. Design rules

1. **Diagnosis is read-only.** `/doctor` and `/audit` never mutate.
2. **Healing is explicit and named.** No default-on repairs. Each healer is a POST with a named action.
3. **The Hermes bridge is rw because it is the doctor.** Repairing config and venv is the job.
4. **The Antigravity bridge is ro because it is the council.** Antigravity is a second opinion, not a system of record.
5. **No destructive Docker action exists in either bridge.** The 2026-08-08 loss is permanent doctrine.
6. **One contract, two targets.** Mavis integrates once.

---

## 8. Cross-references

- Skills: `mavis-minimax-hermes-bridge-skill`, `mavis-minimax-antigravity-bridge-skill`
- Sentinel daemon: `70_CONNECTORS/70_sentinel_role_ai_inventory.md`
- Docker fleet: `70_CONNECTORS/70_docker_fleet_inventory.md`
- Doctrine: `SENTINEL_OPERATIONAL_DOCTRINE.md` §9 (bridges), §10 (Hermes rules — never `prune -a`)
