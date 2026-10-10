# Bridge — Hermes v0.21.3

**Status**: ✅ WIRED (live verified 2026-09-18)

## Role in the swarm

Hermes is the **tool orchestration and MCP routing layer** — 31 `hermes-mcp-*` Docker containers running + 2 host-native processes. Hermes also runs its own 33 MCP servers (see "Hermes-side MCP fleet" below). Hermes turns abstract "dispatch a tool" into "execute this specific MCP call against this specific container."

## Surface (live-verified 2026-09-18)

- **CLI**: `C:\Users\apviz\AppData\Local\hermes\hermes-agent\venv\Scripts\hermes.exe` — **v0.21.3** confirmed
- **MCP to Mavis**: `hermes-mcp-router` MCP server wired and enabled (stdio, `hermes mcp serve`)
- **Container stack**: 31 `hermes-mcp-*` Docker containers (live roster below)
- **Profiles**: 9 — `default`=orchestrator, `prime`=wise-brain, `assist`=Popy's PA, 6 brothers/specialists
- **Context**: `desktop-linux`

## Live container roster (31 running, verified 2026-09-18)

`telegram-bot, elasticsearch, memory, redis, notebooklm, google-workspace, postgresql, antigravity-bridge, telegram, vault, windows-system, searxng, goal-judge, docker, browser, qwen, google-drive, agent-browser, docker-gordon-bridge, filesystem, obsidian, chrome-devtools, sequential-thinking, git, prometheus, hermes-profile, discord, whatsapp, optimus-orchestrator, session-replay, git-base`

## Hermes-side MCP fleet (33 servers, verified via `hermes mcp list`)

All enabled EXCEPT `gmail`:
agent-browser, antigravity-bridge, browser, chrome-devtools, comfy-cloud (HTTP), discord, docker-gordon-bridge, docker-mcp, elasticsearch-mcp, figma (HTTP), filesystem, git, **gmail (DISABLED)**, google-drive, google-workspace, hermes-profile, memory, notebooklm, obsidian, optimus-orchestrator, postgresql-mcp, prometheus-mcp, qwen, redis-mcp, searxng, sequential-thinking, session-replay, telegram, telegram-bot, vault-mcp, whatsapp-mcp, windows-system, goal-judge.

## Status of Mavis-side wiring

- ✅ `hermes-mcp-router` MCP server (Mavis profile) — enabled, exposes Hermes to Mavis
- ✅ `hermes-bridge` skill installed at `C:\Users\apviz\.minimax\agents\mavis\skills\hermes-bridge\`
- ✅ Hermes CLI on PATH

## Hard rules (NEVER violate)

- 🚫 **NEVER `docker container prune -a`** — Popy lost the entire swarm on 2026-08-08 because of this. Pruning individual stopped containers requires R0.
- 🚫 **NEVER `docker rm -f hermes-mcp-*`** — same reason.
- 🚫 **NEVER `--force` recreate the whole `hermes-mcp-*` stack** without R0. If one container is sick, fix one container.
- ✅ **Diagnose first, restart second, rebuild last.**
- ✅ Coordinate with Gordon (`docker ai`) for any container-level diagnosis.

## Use cases

- Dispatching MCP tool calls (each `hermes-mcp-*` likely maps to a tool category)
- Profile switching (`hermes profile use prime` etc.)
- Cross-container orchestration
- Routing Mavis's tool requests to the right container

## Dispatch protocol

1. Identify target profile + target container
2. Construct the MCP call per that container's contract
3. Execute via Hermes (Mavis → `hermes-mcp-router` MCP or `hermes-bridge` skill)
4. Capture result + container name for the JURNAL_OGLINDA log

## Language rule

Hermes outputs Romanian at Popy + Prime + Assist profile. Below translator gate = English.

## Hermes auth (live, verified 2026-09-18)

- Nous Portal: ✓ logged in (model: `meituan/longcat-2.0:free`)
- OpenAI Codex: ✓ logged in
- API keys active: OpenRouter, Google/Gemini, GitHub
- Qwen OAuth: ✗ NOT logged in (run `qwen auth qwen-oauth`)
- Tool Gateway: ✗ blocked — Nous Portal has no paid credits

## Token Plan Plus wiring

Popy's target: **Token Plan Plus ($22/mo)** wired to Hermes as the M3 brain. When this is active, Hermes's reasoning layer is MiniMax M3. **Currently NOT wired** — Hermes is on Nous Portal / LongCat.

## JURNAL_OGLINDA

| Date | Event | Notes |
|---|---|---|
| 2026-09-18 | Bridge file upgraded | ✅ WIRED. Hermes v0.21.3 (not v0.21.1). 31 containers + 33-server MCP fleet verified. Mavis-side MCP + skill wired. |
| 2026-08-08 | **Swarm loss incident** | NEVER `docker container prune -a`. The containers were rebuilt from scratch after this. |

## Open questions for Popy (R0)

1. Should we wire Token Plan Plus → Hermes as M3 brain now, or stay on Nous Portal / LongCat?
2. List the 2 host-native processes and what they do. (Hermes status didn't enumerate them explicitly — need `Get-Process | Where-Object` targeted.)
3. Tool Gateway is credit-blocked. Add credits to Nous Portal, or migrate to a paid model?
