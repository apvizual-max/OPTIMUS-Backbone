---
name: mavis-backbone-skill
description: Load on session-open when working in the OPTIMUS Backbone project at C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\. Bridges this skill's location with the doctrine file `SENTINEL_OPERATIONAL_DOCTRINE.md` and the deep doctrine substrate at `SENTINEL_PRIME/`.
---

# OPTIMUS Backbone — Mavis Layer

When Mavis is operating inside `C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\` (the OPTIMUS Backbone project), this skill is the project-level entry point.

## Two-layer model

- **Doctrine substrate** = `SENTINEL_PRIME/` (existing, built 2026-09-12). Source of truth for the SENTINEL pattern.
- **Mavis orchestration** = this project (built 2026-09-18). Operational layer.

Doctrine wins on conflict. Propose amendments to `SENTINEL_PRIME/` via R0; do not silently fork.

## Read order on session open

1. `README.md` — orientation, two-layer model
2. `OPTIMUS_INDEX.md` — cheat sheet
3. `SENTINEL_OPERATIONAL_DOCTRINE.md` — the paste-into-UI doctrine
4. `00_INDEX/00_master_map.md` — what's where
5. `00_INDEX/00_bridge_registry.md` — bridge status (LIVE wiring reflected here)
6. `40_REGISTRIES/40_partition_E_aiwork.md` — where the SENTINEL manuals live
7. Any JURNAL_OGLINDA entries in `40_REGISTRIES/` (append-only)

For deep doctrine work, also read:
- `SENTINEL_PRIME/01_FOUNDATION/doctrine/A_FI_DOCTRINE.md`
- `SENTINEL_PRIME/02_OPERATIONAL/rituals/RITUAL_3_PROPOZITII.md`
- `SENTINEL_PRIME/03_INTELLIGENCE/algorithms/TRIPLE_FILTER_ALGORITHM.md`

## Live wiring (Mavis profile)

Mavis's MCP servers (configured via `mavis mcp list`):

| MCP server | Status | Purpose |
|---|---|---|
| `hermes-mcp-router` | ✅ enabled | Hermes v0.21.3 orchestrator |
| `docker-mcp` | ✅ enabled | Container lifecycle |
| `git-mcp` | ✅ enabled | Git ops |
| `obsidian-mcp` | ✅ enabled | Second Brain Obsidian vault |
| `notebooklm-mcp` | ✅ enabled | Source-grounded research |
| `chrome-devtools-mcp` | ✅ enabled | Browser automation |
| `agent-browser-mcp` | ✅ enabled | Headless browser |
| `mcp-server-filesystem` | ✅ enabled | File ops |
| `qwen-mcp-http` | 🟡 disabled | Qwen (start daemon first) |
| `gdrive-mcp` | 🟡 disabled | Google Drive (OAuth pending) |
| `gmail-mcp` | 🟡 disabled | Gmail (OAuth pending) |
| `google-workspace-mcp` | 🟡 disabled | Workspace (OAuth pending) |
| `google-calendar-mcp` | 🟡 disabled | Calendar (OAuth pending) |

Mavis's skills (under `C:\Users\apviz\.minimax\agents\mavis\skills\`):

- `hermes-bridge` — Hermes via MCP + shell
- `qwen-bridge` — Qwen via HTTP daemon + shell
- `antigravity-bridge` — Antigravity via shell
- `docker-gordon` — Docker via MCP + shell
- `obsidian-second-brain` — Obsidian vault via MCP
- `notebooklm-bridge` — NotebookLM via MCP
- `google-workspace` — Workspace MCP (after OAuth)
- `chrome-browser` — Chrome DevTools + Agent Browser
- `optimus-backbone` — this file

## Settings locations (for Popy to verify / tweak)

| What | Where |
|---|---|
| **MCP servers (Mavis profile)** | `mavis mcp list` / `mavis mcp get <name>` (CLI-equivalent tool inside MiniMax Code) |
| **MCP config on disk** | Persisted by Mavis runtime; inspect via `mavis mcp get <name>` |
| **Mavis agent config** | `C:\Users\apviz\.minimax\agents\mavis\config.yaml` |
| **Mavis agent skills** | `C:\Users\apviz\.minimax\agents\mavis\skills\<name>\SKILL.md` |
| **Mavis agent memory** | `C:\Users\apviz\.minimax\agents\mavis\memory\MEMORY.md` (via `memory` tool) |
| **Hermes config** | `C:\Users\apviz\.hermes\config.yaml` (Hermes-managed) |
| **Hermes CLI** | `C:\Users\apviz\AppData\Local\hermes\hermes-agent\venv\Scripts\hermes.exe` |
| **Qwen CLI** | `C:\Users\apviz\AppData\Local\qwen-code\bin\qwen.cmd` |
| **Antigravity CLI** | `C:\Users\apviz\AppData\Local\agy\bin\agy.exe` (v1.2.5) |
| **Antigravity IDE** | `C:\Users\apviz\AppData\Local\Programs\Antigravity IDE` |
| **Docker CLI** | `C:\Program Files\Docker\Docker\resources\bin\docker.exe` |
| **Obsidian vault** | `E:\CLAUDE\MINTE\00_KV_SECOND BRAIN\` |
| **SENTINEL materials (audio/video)** | `D:\Alex_Knowlege_Vault\03_Resources\03_7-SENTINEL_Character\` |
| **Backbone project (Mavis SOT)** | `C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\` |

## Reference

- Doctrine: `SENTINEL_OPERATIONAL_DOCTRINE.md`
- Master map: `00_INDEX/00_master_map.md`
- Bridge registry: `00_INDEX/00_bridge_registry.md`
- Index: `OPTIMUS_INDEX.md`
