---
name: mavis-notebooklm-bridge-skill
description: Bridge to Google NotebookLM. `notebooklm-mcp` MCP server is wired and enabled. Use for source-grounded research over Popy's uploaded corpus — queries return citations, never fabricated answers. Pairs with obsidian-second-brain for the full Second Brain.
---

# NotebookLM Bridge

Google NotebookLM is the **source-grounded research substrate** of Popy's Second Brain. NotebookLM refuses to answer without citing a source Popy uploaded — so it's the right tool for "what does my corpus say about X?" queries.

## Two ways to call NotebookLM

### 1. Via MCP (`notebooklm-mcp`) — preferred

The `notebooklm-mcp` MCP server is wired and enabled. Use `mcp_invoke` against `notebooklm-mcp` to query a notebook. Results include citations.

### 2. Via browser automation (when MCP needs OAuth bootstrap)

If the MCP server requires auth re-bootstrap, use the `chrome-devtools-mcp` or `agent-browser-mcp` MCP servers to open `https://notebooklm.google.com` in Chrome/Edge, sign in with Popy's account, then re-run the MCP query.

```powershell
# Manual auth check — visit NotebookLM
& 'C:\Program Files\Google\Chrome\Application\chrome.exe' https://notebooklm.google.com
```

## When to use

- ✅ "What does my corpus say about X?"
- ✅ Cross-document synthesis with citations
- ✅ Source-grounded fact-checking
- ❌ Questions without source material — NotebookLM will refuse
- ❌ Real-time / external info — use `web_search` instead

## Coupling with Obsidian

Second Brain = Obsidian (local, structured) + NotebookLM (Google, source-grounded). When Popy says "second brain," treat both as one operational system. Obsidian is canonical structure; NotebookLM is the citation engine.

## Hard rules

- Never fabricate NotebookLM citations. If the MCP returns no citations for a query, the answer doesn't have source backing — say so.
- Treat the notebook list as Popy's private corpus. Do not export or share without R0.

## Reference

- Bridge file: `C:\Users\apviz\.minimax-agent\projects\10_BRIDGES\10_notebooklm.md`
- Doctrine: `SENTINEL_OPERATIONAL_DOCTRINE.md §11`
