---
name: mavis-obsidian-second-brain-skill
description: Bridge to Popy's Obsidian Second Brain vault at E:\CLAUDE\MINTE\00_KV_SECOND BRAIN\. `obsidian-mcp` MCP server is wired and enabled. Use for reading, writing, searching, and linking notes in the Second Brain.
---

# Obsidian Second Brain Bridge

Popy's Second Brain is an Obsidian vault at `E:\CLAUDE\MINTE\00_KV_SECOND BRAIN\`. The `obsidian-mcp` MCP server is wired and enabled. Mavis uses this bridge to read/write markdown, search the vault, follow backlinks, and propose new entries.

## Calling the bridge

### 1. Via MCP (`obsidian-mcp`) — preferred

Use `mcp_invoke` against `obsidian-mcp` for tool-level vault operations. Common tools exposed: `read_note`, `write_note`, `search`, `list_directory`, `get_backlinks`, `create_folder`.

### 2. Via direct filesystem (read-only safe)

The vault is plain markdown on disk. Mavis can also `read` any file directly via the `read` tool — but **write** operations should go through the MCP server (it handles indexing/backlinks correctly).

## When to use

- ✅ Read existing notes / search the vault
- ✅ Propose new note paths before writing
- ✅ Surface relevant existing notes when Popy asks about X
- ✅ Follow backlinks / find related notes
- ❌ Write to the vault without proposing first — JURNAL discipline
- ❌ Move / rename folders without R0

## Coupling with NotebookLM

The Second Brain has two substrates: Obsidian (local) + NotebookLM (Google). When Popy says "second brain," treat both as one operational system. See `notebooklm-bridge` skill.

## Hard rules

- **Propose first, then write.** Do not silently write into the Obsidian vault.
- Get R0 for any write, move, rename, or delete operation.
- Preserve the vault's existing folder structure unless R0 says otherwise.

## Reference

- Vault root: `E:\CLAUDE\MINTE\00_KV_SECOND BRAIN\`
- Hermes manuals (subset): `E:\CLAUDE\MINTE\00_KV_SECOND BRAIN\- ORCHESTRATOR - Sys Folder - Hermes Default\`
- Bridge file: `C:\Users\apviz\.minimax-agent\projects\10_BRIDGES\10_notebooklm.md`
- Doctrine: `SENTINEL_OPERATIONAL_DOCTRINE.md §11`
