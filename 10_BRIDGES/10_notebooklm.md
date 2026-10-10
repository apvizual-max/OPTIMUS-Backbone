# Bridge — Google NotebookLM

**Status**: ✅ WIRED — `notebooklm-mcp` MCP server wired and enabled (npm `notebooklm-mcp` v2.0.0). Hermes also has its own `notebooklm` MCP. `notebooklm-bridge` skill installed.

## Role in the swarm

NotebookLM is the **source-grounded research substrate** of Popy's Second Brain. When Mavis needs to query Popy's uploaded corpus (notes, PDFs, transcripts) with **citations**, NotebookLM is the bridge. It does not invent — it answers only from sources Popy gave it.

## Surface (live-verified 2026-09-18)

- **Web**: https://notebooklm.google.com (requires Chrome/Edge with Popy's Google account)
- **MCP to Mavis**: `notebooklm-mcp` MCP server wired and enabled (npm `notebooklm-mcp` v2.0.0, stdio)
- **MCP via Hermes**: `notebooklm` MCP server already in Hermes's 33-server fleet
- **Skill**: `notebooklm-bridge` installed at `C:\Users\apviz\.minimax\agents\mavis\skills\notebooklm-bridge\`

## Activation (live)

- ✅ MCP server binary present
- ✅ Both Mavis-side and Hermes-side MCP wired
- [ ] Verify Chrome/Edge auth session is signed in to Popy's Google account
- [ ] Verify notebooks exist and document naming convention
- [ ] First smoke-test query (read-only, e.g., list notebooks)

## Use cases

- "What does Popy's corpus say about X?" queries
- Cross-document synthesis with citations
- Source-grounded fact-checking (NotebookLM refuses to answer without source)
- Generating audio overviews / study guides from the corpus

## Dispatch protocol

1. Construct the query (Romanian or English per language rule)
2. Dispatch via `notebooklm-mcp` MCP tool (preferred) or via the notebooklm-bridge skill
3. Capture the response + the cited sources
4. Integrate into Mavis's output with full citation chain

## Second Brain coupling

NotebookLM is one of two substrates of the Second Brain. The other is the **Obsidian vault** at `E:\CLAUDE\MINTE\00_KV_SECOND BRAIN\` (wired via `obsidian-mcp`). When Popy says "second brain," Mavis treats both as one operational system.

## JURNAL_OGLINDA

| Date | Event | Notes |
|---|---|---|
| 2026-09-18 | Bridge wired | ✅ `notebooklm-mcp` MCP wired (Mavis side) + Hermes's own notebooklm MCP live + notebooklm-bridge skill installed. Browser auth verification pending. |
