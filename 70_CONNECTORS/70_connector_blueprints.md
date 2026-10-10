# Connector (MCP Server) Blueprints

**Purpose**: Specs for the **MCP servers** Mavis should expose to integrate with the OPTIMUS Prime swarm. Each entry is a blueprint for an `mcp.json` entry — actual creation requires `mavis mcp create` and Popy R0.

**Important**: This file is **blueprints, not live connectors**. Mavis's MCP servers are configured in `C:\Users\apviz\.minimax\mcp.json` (or the active profile's equivalent) and must be created via the `mavis mcp create` command. Until Popy R0-ratifies each connector and the server is actually created, these are specs only.

---

## Connector: `hermes-mcp-router`

**Purpose**: Single MCP server that routes to the 33 `hermes-mcp-*` Docker containers based on tool namespace.

**Proposed mcp.json entry**:

```json
{
  "name": "hermes-mcp-router",
  "transport": "stdio",
  "command": "hermes",
  "args": ["mcp", "serve", "--profile", "default"],
  "description": "Routes MCP tool calls to the hermes-mcp-* container fleet.",
  "enabled": true
}
```

**Activation blockers**:
- `hermes` CLI on PATH not yet verified
- 33-container roster not yet enumerated
- profile-to-namespace mapping not yet documented

---

## Connector: `docker-ai-gordon`

**Purpose**: Expose Gordon (Docker AI) as an MCP tool.

**Proposed mcp.json entry**:

```json
{
  "name": "docker-ai-gordon",
  "transport": "stdio",
  "command": "docker",
  "args": ["ai", "serve"],
  "description": "Docker AI assistant (Gordon) for container-level diagnosis.",
  "enabled": true
}
```

**Activation blockers**:
- `docker ai serve` subcommand not yet verified
- Docker Desktop version not yet confirmed (Gordon requires 4.x+)

---

## Connector: `google-ai`

**Purpose**: Expose Google AI (Gemini) as an MCP server.

**Proposed mcp.json entry**:

```json
{
  "name": "google-ai",
  "transport": "http",
  "url": "https://generativelanguage.googleapis.com/v1beta",
  "headers": {
    "Authorization": "Bearer ${GOOGLE_API_KEY}"
  },
  "description": "Google AI Studio / Gemini API.",
  "enabled": true
}
```

**Activation blockers**:
- `GOOGLE_API_KEY` env var not yet confirmed present
- Endpoint URL not yet verified (may differ by Gemini version)

---

## Connector: `google-notebooklm`

**Purpose**: Expose NotebookLM as an MCP server.

**Proposed mcp.json entry**:

```json
{
  "name": "google-notebooklm",
  "transport": "http",
  "url": "https://notebooklm.google.com/_/mcp",
  "headers": {
    "Authorization": "Bearer ${GOOGLE_OAUTH_TOKEN}"
  },
  "description": "Google NotebookLM source-grounded queries.",
  "enabled": true
}
```

**Activation blockers**:
- NotebookLM does **not yet have a public MCP API** as of 2026-09. Verify before claiming this connector can exist.
- OAuth flow not yet designed

---

## Connector: `qwen`

**Purpose**: Expose Qwen Studio as an MCP server.

**Proposed mcp.json entry**:

```json
{
  "name": "qwen",
  "transport": "http",
  "url": "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
  "headers": {
    "Authorization": "Bearer ${QWEN_API_KEY}"
  },
  "description": "Qwen Studio API.",
  "enabled": true
}
```

**Activation blockers**:
- `QWEN_API_KEY` env var not yet confirmed
- Endpoint URL not yet verified
- Popy's Qwen subscription tier not known

---

## Connector: `antigravity`

**Purpose**: Expose Antigravity CLI as an MCP server (if it supports MCP).

**Proposed mcp.json entry** (placeholder — depends on Antigravity's surface):

```json
{
  "name": "antigravity",
  "transport": "stdio",
  "command": "antigravity",
  "args": ["mcp", "serve"],
  "description": "Antigravity CLI as MCP server (TBD).",
  "enabled": false
}
```

**Activation blockers**:
- Antigravity CLI binary name and surface not yet known to Mavis
- Whether Antigravity supports MCP at all is unknown

---

## How to activate a connector

1. Popy R0-ratifies the connector
2. Resolve all `activation_blockers`
3. Verify the proposed `mcp.json` entry actually works (test load)
4. Create via `mavis mcp create --name <name> --transport <t> ...` (see `mavis mcp help`)
5. Test the tool via Mavis MCP integration
6. Append a JURNAL_OGLINDA entry here
7. Update `OPTIMUS_INDEX.md`

## JURNAL_OGLINDA

| Date | Event | Notes |
|---|---|---|
| 2026-09-18 | Connector blueprints created | All connectors 🟡 blueprint, awaiting verification + Popy R0 |
