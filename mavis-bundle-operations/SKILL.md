---
name: mavis-bundle-operations
description: Bundle — Operations. Load when Mavis needs to dispatch work to a bridge (Hermes / Qwen / Antigravity / Gordon / NotebookLM / Obsidian / Chrome / Workspace). The 8 bridge skills live here. Triggers on "do X", "send Y", "fetch Z", "deploy W". Routes to the right bridge skill.
---

# mavis-bundle-operations

The **Operations** bundle. Bridge-dispatch skills — how Mavis actually does work by routing to other AI agents / tools.

## When to load

- "Execute task X on Hermes"
- "Generate a Qwen prompt for Y"
- "Run a browser automation for Z"
- "Read from the Obsidian vault"
- "Search NotebookLM for W"
- "Manage Docker containers"
- Anything that touches an external tool / AI / data source

## Member skills

Load via `skill({ name: "<member>" })`:

| Member | When to load | MCP |
|---|---|---|
| `mavis-hermes-bridge-skill` | Multi-tool orchestration, profile switching, container queries | `hermes-mcp-router` |
| `mavis-qwen-bridge-skill` | Multilingual / Chinese-language work, cross-model checks | `qwen-mcp-http` (HTTP daemon) |
| `mavis-antigravity-bridge-skill` | Heavy code generation, repo-scale refactor, autonomous workflows | shell bridge (no direct MCP) |
| `mavis-docker-gordon-skill` | Container ops, Dockerfile review, runtime diagnosis | `docker-mcp` |
| `mavis-obsidian-second-brain-skill` | Vault read/write/search, backlink navigation | `obsidian-mcp` |
| `mavis-notebooklm-bridge-skill` | Source-grounded research with citations | `notebooklm-mcp` |
| `mavis-google-workspace-skill` | Drive / Gmail / Calendar / Docs (after OAuth bootstrap) | `gdrive-mcp`, `gmail-mcp`, `google-workspace-mcp`, `google-calendar-mcp` |
| `mavis-chrome-browser-skill` | Live browser automation, screenshots, devtools | `chrome-devtools-mcp`, `agent-browser-mcp` |
| `mavis-session-transcript-skill` | Extract the FULL transcript of a session (every message, thinking, tool call, externalised tool output) for archiving or hand-over | none (reads the runtime's own sqlite + session dirs via `node:sqlite`) |

## MCP servers that enforce scope

This category owns **all 8 enabled bridge MCPs** (Hermes, Qwen, Docker, Git, Obsidian, NotebookLM, Chrome DevTools, Agent Browser) plus **mcp-server-filesystem** for file ops. The 4 OAuth-pending Google MCPs also live in this category (gated on Popy's browser-side OAuth bootstrap).

## How to use this bundle

1. **Pick the right bridge** for the work shape (cross-reference `mavis-swarm-coordinator-skill`'s bridge selection matrix).
2. **Hand off a clean task contract** — scope, acceptance criteria, constraints, output format. The 4-step dispatch protocol applies.
3. **Integrate the result** with explicit attribution. Log to the bridge file's JURNAL_OGLINDA table.
4. **Sequencing for multi-bridge tasks**: typically Obsidian (read existing) → Hermes (orchestrate) → Qwen / NotebookLM (research) → Gordon (container ops) → Mavis filesystem (write outputs). Each subtask = one bridge + one contract.

## Personal skill integration (NEW: 2026-09-19)

The 682 personal skills classified as **Operations** in `C:\Users\apviz\.minimax-agent\projects\70_CONNECTORS\70_personal_skill_index.md` are also available here. Mavis uses `mavis-skill-index`'s routing procedure to:

1. Scan the Operations section of the classifier table.
2. Score candidate skills by description overlap with the task.
3. Load the top 1-3 via `skill({ name: "<candidate>" })`.
4. Fall back to the bridge skills in this bundle if no candidate fits.

The classifier is the single point of truth — Mavis never has to ask Popy which skill to use.

## Anti-patterns

- ❌ Reaching for Operations bundle for identity or behavior questions. Use `mavis-bundle-identity` or `mavis-bundle-behavioral` instead.
- ❌ Calling a bridge without a task contract. Vague requests → vague answers.
- ❌ Silently shadowing another bridge. Every dispatch is logged.
- ❌ Writing to a vault / Drive / repo without R0 if the change is destructive or outside the workspace.
- ❌ Loading more than 3 personal skills for a single task. That's the autonomous selection budget.

## Cross-references

- Skill index (single point of truth): `mavis-skill-index`
- Classifier data: `C:\Users\apviz\.minimax-agent\projects\70_CONNECTORS\70_personal_skill_index.md`
- Taxonomy: `C:\Users\apviz\.minimax-agent\projects\00_INDEX\00_skill_taxonomy.md`
- Doctrine: `SENTINEL_OPERATIONAL_DOCTRINE.md §9` (bridge dispatch protocol)
- Bridge registry: `C:\Users\apviz\.minimax-agent\projects\00_INDEX\00_bridge_registry.md`
