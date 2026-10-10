# Bridge — Obsidian Second Brain

**Status**: ✅ WIRED — `obsidian-mcp` MCP server wired and enabled (npm `mcp-obsidian` v1.0.0). Hermes also has its own `obsidian` MCP. `obsidian-second-brain` skill installed.

## Role in the swarm

Obsidian holds Popy's **local** Second Brain — markdown vault at `E:\CLAUDE\MINTE\00_KV_SECOND BRAIN\`. Pairs with NotebookLM (Google-side, source-grounded). When Mavis needs to read / write / link / search local notes, Obsidian is the bridge.

## Surface (live-verified 2026-09-18)

- **Vault path**: `E:\CLAUDE\MINTE\00_KV_SECOND BRAIN\` — verified 2026-09-18
- **MCP to Mavis**: `obsidian-mcp` MCP server wired and enabled (npm `mcp-obsidian` v1.0.0, stdio)
- **MCP via Hermes**: `obsidian` MCP server already in Hermes's 33-server fleet
- **Skill**: `obsidian-second-brain` installed at `C:\Users\apviz\.minimax\agents\mavis\skills\obsidian-second-brain\`

## Activation (live)

- ✅ Vault root exists and is reachable
- ✅ MCP server binary present
- ✅ Both Mavis-side and Hermes-side MCP wired
- [ ] First smoke-test: read a known note, verify the MCP returns content

## Use cases

- Read / search / propose new note entries
- Cross-reference SENTINEL materials between Obsidian and the SENTINEL_PRIME project at `C:\Users\apviz\.minimax-agent\projects\`
- Anchor doctrine (R33, TRIPLE CRUNCH, etc.) to the local vault

## Hard rules

- **Propose before writing.** No silent writes into the vault.
- R0 for any destructive operation (move, rename, delete).

## JURNAL_OGLINDA

| Date | Event | Notes |
|---|---|---|
| 2026-09-18 | Bridge wired | ✅ `obsidian-mcp` MCP wired (Mavis side) + Hermes's own obsidian MCP live + obsidian-second-brain skill installed. Vault at E:\CLAUDE\MINTE\00_KV_SECOND BRAIN\ confirmed. |
