---
name: mavis-mcp-management-skill
description: Manage Mavis's MCP server fleet — list, get, create, update, enable/disable, delete. Load when wiring a new MCP, checking which MCPs are live, toggling MCPs on/off, or diagnosing why an MCP isn't responding. Uses the `mavis` CLI tool inside MiniMax Code sessions.
---

# mavis-mcp-management-skill

How Mavis manages its own MCP server fleet (13 servers currently live in the Mavis profile).

## Commands (via `mavis` CLI tool)

| Need | Command |
|---|---|
| List all MCPs | `mavis({ command: "mcp list" })` |
| Get one MCP's config | `mavis({ command: "mcp get", args: { name: "<name>" } })` |
| Create a new MCP | `mavis({ command: "mcp create", args: { name, transport, command/url, args, description, enabled } })` |
| Update / toggle enable | `mavis({ command: "mcp update", args: { name, enabled: true/false } })` |
| Delete an MCP | `mavis({ command: "mcp delete", args: { name: "<name>" } })` |

## Current Mavis fleet (13 wired, 13 enabled)

| Name | Transport | Endpoint |
|---|---|---|
| `hermes-mcp-router` | stdio | Hermes v0.21.3 stdio |
| `qwen-mcp-http` | http | `http://localhost:8765/mcp` (daemon up) |
| `docker-mcp` | stdio | npm mcp-docker v1.0.0 |
| `git-mcp` | stdio | npm mcp-git v0.0.4 |
| `obsidian-mcp` | stdio | npm mcp-obsidian v1.0.0 |
| `notebooklm-mcp` | stdio | npm notebooklm-mcp v2.0.0 |
| `chrome-devtools-mcp` | stdio | npm chrome-devtools-mcp v1.6.0 |
| `agent-browser-mcp` | stdio | npm agent-browser-mcp-server v0.14.2 |
| `mcp-server-filesystem` | stdio | npm mcp-server-filesystem |
| `gdrive-mcp` | stdio | bun + gdrive-mcp v1.0.2 |
| `gmail-mcp` | stdio | bun + gmail-mcp v2.4.0 |
| `google-workspace-mcp` | stdio | bun + google-workspace-mcp v2.3.6 |
| `google-calendar-mcp` | stdio | node + google-calendar-mcp v1.0.9 |

## Wiring a new MCP — checklist

1. Locate the binary / npm package on disk (npm globals at `C:\Users\apviz\AppData\Roaming\npm`).
2. Verify it works standalone (run it via shell or check its `package.json` `bin` field).
3. Decide transport: stdio (local process) or http (remote endpoint).
4. Compose `mavis mcp create` args.
5. Test by invoking a tool from the MCP.
6. Append JURNAL_OGLINDA entry to `40_REGISTRIES/40_partition_C_system.md`.

## bun-based MCPs — special note

Some MCPs (`gdrive-mcp`, `gmail-mcp`, `google-workspace-mcp`) are TypeScript and expect the bun runtime. The `.cmd` wrappers in npm fall back to global `bun` which isn't on PATH. Use `C:\Program Files\Qwen\resources\bun\bun.exe` directly as the command, with the package's source `.ts` (or compiled `.js`) file as the first arg.

## OAuth-gated MCPs (4)

- `gdrive-mcp`, `gmail-mcp`, `google-workspace-mcp`, `google-calendar-mcp` are wired but return empty data until Popy drives a browser-based OAuth flow once to mint tokens.

## Cross-references

- Settings locations: `mavis-backbone-skill`
- Bridge files: `C:/Users/apviz/.minimax-agent/projects/Mavis-Optimus-Dashboard/10_BRIDGES/`
- Registry: `C:/Users/apviz/.minimax-agent/projects/Mavis-Optimus-Dashboard/00_INDEX/00_bridge_registry.md`
