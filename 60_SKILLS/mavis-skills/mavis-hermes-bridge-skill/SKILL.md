---
name: mavis-hermes-bridge-skill
description: Bridge to Hermes v0.21.3 — the orchestrator/sub-agent layer of OPTIMUS Prime. Use for tool orchestration, MCP routing, profile switching, and dispatching work to the 33 hermes-mcp-* Docker containers. Trigger when: task needs multi-step tool work that Mavis would rather delegate, or when the 33-container fleet should handle a domain. Hermes is exposed to Mavis via the `hermes-mcp-router` MCP server (stdio).
---

# Hermes Bridge

Hermes v0.21.3 is the **tool orchestration and sub-agent layer** of the OPTIMUS Prime swarm. Mavis delegates to Hermes for tasks that span multiple tools, multi-step container orchestration, or work that should be handled by the 33 `hermes-mcp-*` Docker containers.

## Two ways to call Hermes

### 1. Via MCP (preferred for in-session tool calls)

The `hermes-mcp-router` MCP server is already configured and enabled. Use the `mcp_invoke` tool against `hermes-mcp-router` to dispatch tool calls. Hermes returns results as MCP tool results.

### 2. Via shell (for one-shot prompts, profile ops, status)

The `hermes.exe` CLI is at `C:\Users\apviz\AppData\Local\hermes\hermes-agent\venv\Scripts\hermes.exe`.

Common invocations:

```powershell
# Status of all components
& 'C:\Users\apviz\AppData\Local\hermes\hermes-agent\venv\Scripts\hermes.exe' status

# One-shot prompt
& 'C:\Users\apviz\AppData\Local\hermes\hermes-agent\venv\Scripts\hermes.exe' -z "your prompt here"

# Profile list / switch
& 'C:\Users\apviz\AppData\Local\hermes\hermes-agent\venv\Scripts\hermes.exe' profile list
& 'C:\Users\apviz\AppData\Local\hermes\hermes-agent\venv\Scripts\hermes.exe' profile use prime

# MCP server list (Hermes-side view)
& 'C:\Users\apviz\AppData\Local\hermes\hermes-agent\venv\Scripts\hermes.exe' mcp list

# Pause/resume cron and gateway dispatch
& 'C:\Users\apviz\AppData\Local\hermes\hermes-agent\venv\Scripts\hermes.exe' pause
& 'C:\Users\apviz\AppData\Local\hermes\hermes-agent\venv\Scripts\hermes.exe' resume

# Doctor (health check)
& 'C:\Users\apviz\AppData\Local\hermes\hermes-agent\venv\Scripts\hermes.exe' doctor
```

## Profiles (Hermes-side)

- `default` — orchestrator
- `prime` — wise-brain
- `assist` — Popy's PA
- 6 others — brothers/specialists

Romanian output at Popy + Prime + Assist profile; below translator gate = English.

## Hard rules (NEVER violate)

- 🚫 `hermes` does NOT need `docker container prune -a`. Hermes itself manages its containers — never invoke prune against them from Mavis.
- 🚫 NEVER `docker rm -f hermes-mcp-*` — the 33 containers are load-bearing. Lost swarm 2026-08-08 was caused by this.
- 🚫 NEVER `--force` recreate the full `hermes-mcp-*` stack without Popy R0. If one container is sick, fix one container via `hermes mcp test <name>`.
- ✅ Diagnose first, restart second, rebuild last.
- ✅ Coordinate with Gordon (`docker-mcp` MCP) for any container-level diagnosis.

## When NOT to use Hermes

- Read-only ops Mavis can do directly (file reads, web search, simple commands)
- Tasks that need Mavis's own context (the user is talking to Mavis, not asking for delegation)
- Anything destructive — always R0 first, then dispatch

## Dispatch protocol (per SENTINEL_OPERATIONAL_DOCTRINE §9)

1. Declare the bridge target and reason.
2. Hand off a clean task contract (scope, acceptance, constraints, output format).
3. Capture the result with attribution.
4. Log to `10_BRIDGES/10_hermes.md` JURNAL_OGLINDA.

## Reference

- Bridge file (Mavis orchestration): `C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\10_BRIDGES\10_hermes.md`
- Doctrine: `SENTINEL_OPERATIONAL_DOCTRINE.md §9, §10`
- Hermes config: `C:\Users\apviz\.hermes\`
