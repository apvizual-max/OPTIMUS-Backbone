---
name: mavis-bundle-identity
description: Bundle — Identity and File Locations. Load when Mavis needs to know who/what/where: the doctrine, the wisdom corpus, and the reality anchor. Triggers on questions like "where is X?", "what is the doctrine on Y?", "what happened last time?". Routes to mavis-backbone-skill, mavis-sacru-corpus-skill, mavis-jurnal-oglinda-skill.
---

# mavis-bundle-identity

The **Identity and File Locations** bundle. This is the entry point — when Mavis doesn't know where something lives or what the doctrine says, start here.

## When to load

- "Where is X?" (paths, files, configs)
- "What does the doctrine say about Y?"
- "What happened last time we did Z?" (JURNAL lookup)
- "What is Mavis / what is this agent?"
- "Where is the SENTINEL corpus / Second Brain / backbone?"

## Member skills

Load the right one via `skill({ name: "<member>" })`:

| Member | When to load |
|---|---|
| `mavis-backbone-skill` | General orientation — where everything lives in the OPTIMUS Backbone project |
| `mavis-sacru-corpus-skill` | Decision-substance lookup — SACRU 25-axe matrix, 963-proverb framework |
| `mavis-jurnal-oglinda-skill` | Historical lookup — what happened in past sessions, append-only record |

## MCP servers that enforce scope

This category's "what's authoritative" answers come from:

- **`obsidian-mcp`** — the vault at `E:\CLAUDE\MINTE\00_KV_SECOND BRAIN\` is the SOT for doctrinal text. Use `mcp_invoke({ tool: "obsidian.search" })` for in-vault lookups.
- **`mcp-server-filesystem`** — for paths in `C:\Users\apviz\.minimax-agent\projects\`, `C:\Users\apviz\AppData\Local\hermes\hermes-agent\`, `D:\Alex_Knowlege_Vault\`, etc.

## How to use this bundle

1. **Search first**. Mavis loads `mavis-jurnal-oglinda-skill` to check past sessions; if not found, loads `mavis-backbone-skill` to confirm the current SOT paths.
2. **Doctrine check**. Before acting on ethical/strategic/long-horizon matters, load `mavis-sacru-corpus-skill` and check the 25-axe decision matrix.
3. **No tool call** is the right answer for many identity questions — the answer is in Memory or in a static file path you can read directly.

## Anti-patterns

- ❌ Loading the entire bundle for every question. Each member skill is meant to be loaded on demand.
- ❌ Reaching for a tool when the answer is in Memory. Read Memory first.
- ❌ Treating Memory as append-only-editable. Corrections are NEW entries that reference the old.

## Cross-references

- Skill index (single point of truth): `mavis-skill-index`
- Classifier data: `C:\Users\apviz\.minimax-agent\projects\70_CONNECTORS\70_personal_skill_index.md` (80 Identity skills classified)
- Taxonomy: `C:\Users\apviz\.minimax-agent\projects\00_INDEX\00_skill_taxonomy.md`
- Doctrine: `SENTINEL_OPERATIONAL_DOCTRINE.md §1` (zero fabrication — paths and tool names must be verified)
