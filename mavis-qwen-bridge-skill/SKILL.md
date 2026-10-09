---
name: mavis-qwen-bridge-skill
description: Bridge to Qwen Studio CLI 0.19.2 — multilingual + cross-model reasoning. Use for Chinese-language tasks, cross-model sanity checks, backup reasoning when other bridges saturated. Currently configured as `qwen-mcp-http` MCP server (DISABLED — must start daemon first).
---

# Qwen Bridge

Qwen Studio CLI 0.19.2 is the **multilingual + cross-model reasoning bridge**. Dispatched for Chinese-language work, second-opinion cross-model checks, and as backup when Hermes/Gemini are saturated.

## Two ways to call Qwen

### 1. Via MCP (HTTP daemon) — currently DISABLED

The `qwen-mcp-http` MCP server is configured at `http://localhost:8765/mcp` but is **disabled**. To enable:

```powershell
# Start the Qwen HTTP daemon in another shell (or background it)
& 'C:\Users\apviz\AppData\Local\qwen-code\bin\qwen.cmd' serve --http-bridge --port 8765

# Then enable in Mavis
mavis({ command: "mcp update", args: { name: "qwen-mcp-http", enabled: true } })
```

### 2. Via shell (one-shot prompts)

```powershell
# One-shot prompt
& 'C:\Users\apviz\AppData\Local\qwen-code\bin\qwen.cmd' -p "your prompt here"

# Specific model
& 'C:\Users\apviz\AppData\Local\qwen-code\bin\qwen.cmd' -p "..." -m qwen-max

# Interactive mode (use with care)
& 'C:\Users\apviz\AppData\Local\qwen-code\bin\qwen.cmd' -i "..."
```

## When to dispatch Qwen

- ✅ Chinese-language generation, translation, summarization
- ✅ Second-opinion cross-model check (compare Qwen's answer to Mavis's)
- ✅ Backup when Hermes / Gemini are unavailable
- ❌ Routine Romanian / English tasks — prefer Mavis/Hermes/Gemini
- ❌ Vision tasks — Qwen doesn't have first-class vision via the CLI here

## Language note

Qwen's strength is Chinese. For Romanian/English tasks, Mavis/Hermes/Gemini are stronger and more idiomatic.

## Hard rules

- R0 before dispatch unless pre-authorized.
- Always log to `10_BRIDGES/10_qwen_studio.md` JURNAL_OGLINDA.
- Never fabricate pricing — verify in current Alibaba Cloud / Dashscope pricing if asked.

## Reference

- Bridge file: `C:\Users\apviz\.minimax-agent\projects\10_BRIDGES\10_qwen_studio.md`
- Doctrine: `SENTINEL_OPERATIONAL_DOCTRINE.md §9`
