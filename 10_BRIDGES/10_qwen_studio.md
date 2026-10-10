# Bridge — Qwen Studio

**Status**: ✅ WIRED — CLI on PATH (0.19.2) + daemon running on :8765 + two MCP entries enabled (`qwen-acp-adapter` works, `qwen-mcp-http` cannot connect) + qwen-bridge skill installed. OAuth not bootstrapped.

## Role in the swarm

Qwen Studio is the **multilingual / Chinese-language reasoning bridge**. Dispatched when:
- The task involves Chinese-language content (Popy's swarm is bilingual)
- Mavis needs a second perspective from a different model family
- Backup reasoning when other bridges are saturated

## Surface (live-verified 2026-09-18)

- **CLI**: `C:\Users\apviz\AppData\Local\qwen-code\bin\qwen.cmd` — **v0.19.2** confirmed
- **Web**: https://studio.qwenlm.ai
- **API**: Dashscope / Alibaba Cloud
- **MCP to Mavis**: two entries, both **enabled** (Popy's decision, 2026-10-02):
  - `qwen-mcp-http` — HTTP, `http://localhost:8765/mcp`. **Cannot connect:** that path
    returns 404. Qwen 0.19.2 exposes ACP at `/acp` and has no MCP transport. Kept
    enabled deliberately; enabled does not mean functional here.
  - `qwen-acp-adapter` — stdio, `projects\scripts\qwen_acp_mcp.py`, 6 tools. **This is
    the working path.**
- **Daemon**: `qwen serve --port 8765` is **running**. The daemon serves ACP and the
  Web Shell; it does not serve `/mcp`.
- **Skill**: `qwen-bridge` installed at `C:\Users\apviz\.minimax\agents\mavis\skills\qwen-bridge\`

## Activation (CLI already active)

- ✅ `where qwen` returns path
- ✅ Daemon running: `qwen.cmd serve --port 8765 --hostname 127.0.0.1` (verified listening).
  It serves **ACP at `/acp`** and the Web Shell — it does **not** serve `/mcp`.
- ✅ `qwen-mcp-http` is **enabled** in `mcp.json` (Popy's decision, 2026-10-02) and will
  not connect, because `/mcp` is 404 on Qwen 0.19.2. The working path is
  `qwen-acp-adapter`, already enabled.
- [ ] Qwen OAuth bootstrap: `qwen auth qwen-oauth` (Popy to confirm when ready).
  Note: the device flow answers, but a *prompt* still fails with `Connection error`
  because Qwen's active model is a local Ollama endpoint and Ollama is not installed.
  Fix Ollama or complete OAuth.

## Use cases

- Chinese-language generation, translation, summarization
- Cross-model sanity check (compare Mavis's answer to Qwen's)
- Multilingual content pipelines
- Backup when Hermes / Gemini are unavailable

## Dispatch protocol

1. Identify target model variant
2. Attach minimal context (Qwen context window varies by model)
3. Receive response with attribution
4. Integrate — note that Qwen is a second-opinion bridge, not a primary one

## Language rule

Qwen's strength is Chinese. For Romanian/English tasks, prefer Mavis/Hermes/Gemini. Dispatch Qwen only when the language or cross-model need justifies it.

## JURNAL_OGLINDA

| Date | Event | Notes |
|---|---|---|
| 2026-09-18 | Bridge wired | ✅ CLI 0.19.2 confirmed. Mavis-side `qwen-mcp-http` MCP wired (disabled until daemon starts). `qwen-bridge` skill installed. OAuth not yet bootstrapped. |
| 2026-10-02 | Corrected | `qwen-mcp-http` is **enabled** per Popy, but `/mcp` returns 404 — Qwen 0.19.2 has no MCP transport. The working path is now `qwen-acp-adapter` (ACP, 6 tools). Daemon on 8765 serves ACP and the Web Shell, not `/mcp`. OAuth still not bootstrapped; the live blocker is that Qwen's active model is a local Ollama endpoint and Ollama is not installed. |

## Open questions for Popy (R0)

1. Qwen OAuth — bootstrap now (`qwen auth qwen-oauth`) or defer?
2. Which Qwen model variant should be the default dispatch target?
3. Want me to start the HTTP daemon automatically on session-open (via cron) or leave manual?
