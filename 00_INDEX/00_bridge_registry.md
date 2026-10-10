# 00 — Bridge Registry

Tracks activation status of each AI bridge in the swarm. Live snapshot as of 2026-09-18 (after full wire-up).

## Bridges

| Bridge | Surface | Status | CLI / binary | MCP equivalent | File |
|---|---|---|---|---|---|
| **Antigravity** | CLI v1.2.5 + IDE | ✅ WIRED | `C:\Users\apviz\AppData\Local\agy\bin\agy.exe` | Hermes has `antigravity-bridge` MCP; shell skill on Mavis side | `10_BRIDGES/10_antigravity.md` |
| **Gemini** | via Hermes + Workspace MCPs | ✅ WIRED | Hermes-routed; Gemini API key in Hermes env | Workspace MCPs enabled (await OAuth bootstrap) | `10_BRIDGES/10_gemini.md` |
| **Hermes v0.21.3** | CLI + 31 Docker + 33 MCP servers | ✅ WIRED | `C:\Users\apviz\AppData\Local\hermes\hermes-agent\venv\Scripts\hermes.exe` | `hermes-mcp-router` (Mavis); 33 of its own (Hermes) | `10_BRIDGES/10_hermes.md` |
| **Gordon** | Docker Desktop AI + docker CLI | ✅ WIRED | `C:\Program Files\Docker\Docker\resources\bin\docker.exe` v29.8.0 | `docker-mcp` (Mavis); `docker-mcp` + `docker-gordon-bridge` (Hermes) | `10_BRIDGES/10_gordon.md` |
| **NotebookLM** | web + MCP | ✅ WIRED | n/a (browser) | `notebooklm-mcp` (Mavis); `notebooklm` (Hermes) | `10_BRIDGES/10_notebooklm.md` |
| **Obsidian (Second Brain)** | vault filesystem + MCP | ✅ WIRED | n/a (filesystem) | `obsidian-mcp` (Mavis); `obsidian` (Hermes) | `10_BRIDGES/10_obsidian.md` |
| **Qwen Studio** | CLI v0.19.2 + HTTP daemon | ✅ WIRED | `C:\Users\apviz\AppData\Local\qwen-code\bin\qwen.cmd` | `qwen-mcp-http` on `:8765` (Mavis, daemon running); `qwen` (Hermes) | `10_BRIDGES/10_qwen_studio.md` |
| **SACRU corpus** | local markdown | ✅ WIRED (located) | `E:\CLAUDE\MINTE\00_KV_SECOND BRAIN\- ORCHESTRATOR - Sys Folder - Hermes Default\SF_IA - IDENTITATE_AXIOMA\SF_IA - 963_PROVERBE_COMPLET.md` | n/a | `40_REGISTRIES/40_sacru_corpus.md` |

## Mavis MCP servers (13 wired, 13 enabled)

| Name | Status | Source |
|---|---|---|
| `hermes-mcp-router` | ✅ enabled | Hermes v0.21.3 stdio |
| `qwen-mcp-http` | ✅ enabled (daemon up on :8765) | HTTP localhost:8765 |
| `docker-mcp` | ✅ enabled | npm mcp-docker v1.0.0 |
| `git-mcp` | ✅ enabled | npm mcp-git v0.0.4 |
| `obsidian-mcp` | ✅ enabled | npm mcp-obsidian v1.0.0 |
| `notebooklm-mcp` | ✅ enabled | npm notebooklm-mcp v2.0.0 |
| `chrome-devtools-mcp` | ✅ enabled | npm chrome-devtools-mcp v1.6.0 |
| `agent-browser-mcp` | ✅ enabled | npm agent-browser-mcp-server v0.14.2 |
| `mcp-server-filesystem` | ✅ enabled | npm mcp-server-filesystem |
| `gdrive-mcp` | ✅ enabled (OAuth boot pending) | bun + gdrive-mcp v1.0.2 |
| `gmail-mcp` | ✅ enabled (OAuth boot pending) | bun + gmail-mcp v2.4.0 |
| `google-workspace-mcp` | ✅ enabled (OAuth boot pending) | bun + google-workspace-mcp v2.3.6 |
| `google-calendar-mcp` | ✅ enabled (OAuth boot pending) | node + google-calendar-mcp v1.0.9 |

## Mavis Skills (10 installed at `C:\Users\apviz\.minimax\agents\mavis\skills\`)

- `hermes-bridge` — Hermes via MCP + shell
- `qwen-bridge` — Qwen via HTTP daemon + shell
- `antigravity-bridge` — Antigravity via shell
- `docker-gordon` — Docker via MCP + shell
- `obsidian-second-brain` — Obsidian vault via MCP
- `notebooklm-bridge` — NotebookLM via MCP
- `google-workspace` — Workspace MCP (after OAuth)
- `chrome-browser` — Chrome DevTools + Agent Browser
- `optimus-backbone` — Backbone entry point for this project
- `sacru-corpus` — 963-proverb wisdom substrate (live)

## Runtimes discovered (and useful)

| Runtime | Path | Used by |
|---|---|---|
| `bun` 1.2.10 | `C:\Program Files\Qwen\resources\bun\bun.exe` | gdrive-mcp, gmail-mcp, google-workspace-mcp (bun-based MCPs) |
| `node` | via npm wrappers | google-calendar-mcp, file-system MCPs |

## Remaining user-side actions (gated, not blocking wiring)

1. **Google OAuth bootstrap** — open Chrome to each Google service, sign in, accept OAuth scope. The MCPs will start returning live data once tokens exist.
2. **Qwen OAuth** — `qwen auth qwen-oauth`
3. **Gordon `docker ai`** — Docker Desktop sign-in
4. **Token Plan Plus → Hermes as M3 brain** — UI choice in MiniMax Code plans; subscription action

## Deactivation (DRAC) protocol

When Popy says a bridge is to be removed:
1. Verify no in-flight dispatches depend on it
2. Disable the MCP server: `mavis mcp update <name> --enabled false`
3. Mark status 🔴 BLOCKED in all three locations
4. Append a JURNAL_OGLINDA entry explaining the severance

## Cross-references

- Bridge dispatch protocol → `20_PROTOCOLS/20_bridge_protocol.md`
- Per-bridge detail → `10_BRIDGES/10_<name>.md`
- Settings locations → `optimus-backbone` skill (at Mavis skills dir)

## 10_BRIDGES/ — per-AI status in the swarm

| Bridge | Status | Verified | File |
|---|---|---|---|
| **Wayland** (agentic cowork) | 🔴 INVENTORIED, not integrated | 2026-10-02: 71 workflows (37 content-creation, 34 business-ops), 4 routines, no CLI on PATH | 10_BRIDGES/10_wayland.md |
