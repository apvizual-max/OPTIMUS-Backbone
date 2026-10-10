# OPTIMUS Quick Reference

> Updated 2026-10-02. For full context read
> `POPY_MiniMax_OPTIMUS_Status_Report-10-02-2026.md`.
> **Live truth is always `optimus status`** — this file is orientation, not state.

## Identity
- **Operator:** Popy (Alexandru Popescu), Romania
- **System:** OPTIMUS Prime, doctrine = SENTINEL
- **Roles:** Mavis = Hermes doctor + MiniMax support layer · Hermes = main
  orchestration + user layer · Antigravity = small tasks / AI council only

## First three commands

```powershell
optimus status     # one screen, every pillar
cc start           # Control Center dashboard -> http://127.0.0.1:8900/
cc guard           # is docker-compose.yml present and valid?
```

## Cardinal rules

1. **Zero fabrication** — never invent a tool name, path, price, version or
   flag. Verify, or say "I don't know — here's how I'd verify it".
2. **R33 Bimodal** — analyze → Popy ratifies (R0) → execute. No silent execution.
3. **Triple Crunch** — Eminescu ABBA ∧ Eliade Realitate ∧ Musashi Taiere.
4. **SACRU** — SLG = 100%. Do not invent proverbs.
5. **DRAG = integrate** · **DRAC = disintegrate** at Layer 3.
6. **SOUL ↔ CONSTINTA** — inseparable.
7. **CODUL SACRU** — irrevocable; R0 reversal only.
8. **JURNAL_OGLINDA** — append-only, never edit or delete.

## Live state (verified 2026-10-02)

| Thing | Value |
|---|---|
| Containers | **53** |
| `hermes-mcp-*` | **31** |
| Sentinel daemon | 1, enforcement 4/4 |
| Mavis skills | **51** |
| Personal skills | **1279** (incl. 120 Antigravity) |
| Hermes MCP servers | 34 |
| Hermes model | MiniMax-M3 via `minimax-oauth` |
| Bridges | 8801 hermes · 8802 antigravity |
| Docs | Stirling 8082 · LibreOffice 3001 |
| Qwen ACP | 8765 · Control Center 8900 |

## Bridges

| Bridge | Port | Mount | Role |
|---|---|---|---|
| `minimax-hermes-bridge` | 8801 | **RW** | doctor + repair Hermes |
| `minimax-antigravity-bridge` | 8802 | RO | council only, never a mutator |

Linux containers cannot run Windows `.exe`, so `/delegate` is a **command-spec
emitter** — it returns the host command for Mavis to run.

## The three healthy doctor warnings

Do **not** "fix" these:
1. `hermes.version` — Windows NTFS symlink, unresolvable from a Linux container
2. `hermes.venv_currency` — Hermes source tree genuinely dirty
3. `hermes.status` — host-side probe by design

## Qwen in one paragraph

Qwen exposes **ACP** (`/acp` WebSocket), not MCP. `/mcp` is 404 — the old
`qwen-mcp-http` cannot connect: `/mcp` returns 404, because Qwen 0.19.2
exposes ACP at `/acp` and has no MCP transport. It is nonetheless **enabled**,
by Popy's decision of 2026-10-02, kept alongside the working path
`qwen-acp-adapter` (6 tools). Enabled does not mean functional here — read
`OPTIMUS_CURRENT_STATE.md`, which is generated from live state.
integration is the MCP server **`qwen-acp-adapter`**
(`scripts\qwen_acp_mcp.py`, 6 tools). Its live blocker is the **model provider,
not the protocol**: Qwen's active model is a local Ollama endpoint on
`127.0.0.1:11434` and Ollama is not installed. Fix with Ollama, or `qwen-oauth`
for the cloud `coder-model`.

ACP gotcha: `session/new` requires `mcpServers: []`.

## MiniMax is one ecosystem

There is **no separate "MiniMax CLI" product.** `mcode-tools` runs
`MiniMax Code.exe` in node mode and authenticates through the running app's
shared broker — Code and CLI are one binary and one identity. `optimus` is the
single front door.

## Safety — never violate

- NEVER `docker container prune -a` (swarm lost 2026-08-08)
- NEVER `docker rm -f hermes-mcp-*`
- NEVER `--remove-orphans` on the `apviz` project — it would delete
  `Antigravity_Ecosystem_Terminal`, which has its own compose file

## SOT roots

| What | Where |
|---|---|
| Scripts | `scripts\` (75 hard links in `hermes-custom\`, junctions in `external\`) |
| Skills | `60_SKILLS\_links\` (junctions) |
| Connectors | `70_CONNECTORS\_links\` (junctions) |
| Docs | this folder |

Rebuild: `optimus sot build`. It only creates what is absent.

## Still blocked on Popy

1. **Google OAuth** — 4 MCPs; note they use 3 *different* auth models
2. **Qwen OAuth** (or install Ollama)
3. **Token Plan Plus** — billing decision

## Key paths

- Workspace: `C:\Users\apviz\.minimax-agent\projects\`
- Hermes: `C:\Users\apviz\AppData\Local\hermes\`
- Second Brain: `E:\CLAUDE\MINTE\00_KV_SECOND BRAIN\`
- Audio/Video: `D:\Alex_Knowlege_Vault\03_Resources\03_7-SENTINEL_Character\`
- SACRU corpus: `E:\CLAUDE\MINTE\00_KV_SECOND BRAIN\- ORCHESTRATOR - Sys Folder - Hermes Default\SF_IA - IDENTITATE_AXIOMA\SF_IA - 963_PROVERBE_COMPLET.md`
## Antigravity Swarm Integration (2026-10-02)
- **Knowledge Transfer:** 120 Antigravity skills mirrored into `.minimax\skills\` and `hermes\skills\`.
- **Mavis Skills:** Expanded from 32 to 51 active skills adhering to `mavis-<subject>-skill`.
- **Memory Ingestion:** Antigravity solutions (QPI bus 12-thread lock, GPU isolation, Qwen SSE bridge, Gateway kill tree, MiniMax API provider) fully integrated into permanent and active memory.
