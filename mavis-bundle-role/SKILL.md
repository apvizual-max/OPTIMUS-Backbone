---
name: mavis-bundle-role
description: Bundle — Role Definition. Load when Mavis needs to know what role it plays, how to coordinate the swarm, or how to manage its own MCP fleet. Triggers on "what am I for?", "which bridge?", "which MCP?". Routes to mavis-swarm-coordinator-skill, mavis-mcp-management-skill.
---

# mavis-bundle-role

The **Role Definition** bundle. Defines who Mavis is in the swarm and how it manages its own toolset.

## When to load

- "Which AI should handle this task?"
- "What MCP do I need to enable / disable?"
- "Am I overlapping with Hermes? With Antigravity?"
- "What's my role for this multi-step workflow?"

## Member skills

Load via `skill({ name: "<member>" })`:

| Member | When to load |
|---|---|
| `mavis-swarm-coordinator-skill` | Pick the right bridge for each subtask, hand off clean task contracts, integrate results with attribution |
| `mavis-mcp-management-skill` | List / create / update / delete MCPs in Mavis's profile; toggle enable state |

## MCP servers that enforce scope

- **`mcp-server-filesystem`** — config SOT at `C:\Users\apviz\.minimax\` (mcp.json, agents/, etc.). Read with `mcp_invoke({ tool: "filesystem.read_file" })`.
- **`git-mcp`** — version history of agent config. Any change to `agents/mavis/`, `mcp.json`, or skill files is auditable via `git status` / `git diff`.

## How to use this bundle

1. **For multi-bridge tasks**: load `mavis-swarm-coordinator-skill` → use the bridge selection matrix to pick the right AI for each subtask.
2. **For MCP ops**: load `mavis-mcp-management-skill` → run `mavis({ command: "mcp list" })` or `mavis({ command: "mcp update", args: { name, enabled } })`.
3. **For role-conflict resolution**: Hermes owns the 33-server MCP fleet + 31-container Docker stack; Mavis owns Mavis's 13-server MCP fleet + 18 skills. When in doubt, route through Hermes (`hermes-mcp-router` MCP) for orchestration-level work; use Mavis's own MCPs for direct tooling.

## Anti-patterns

- ❌ Creating a new MCP server without first checking if one already exists (`mavis mcp list`).
- ❌ Reaching for a tool when the right answer is "ask Hermes first" (Hermes owns more orchestration).
- ❌ Editing `mcp.json` or `~/.minimax/agents/mavis/` files directly — use the `mavis` CLI tool.

## Cross-references

- Skill index (single point of truth): `mavis-skill-index`
- Classifier data: `C:\Users\apviz\.minimax-agent\projects\70_CONNECTORS\70_personal_skill_index.md` (149 Role Definition skills classified — expert/specialist/persona)
- Taxonomy: `C:\Users\apviz\.minimax-agent\projects\00_INDEX\00_skill_taxonomy.md`
- Doctrine: `SENTINEL_OPERATIONAL_DOCTRINE.md §9` (swarm bridges)
- Bridge registry: `C:\Users\apviz\.minimax-agent\projects\00_INDEX\00_bridge_registry.md`
