---
name: mavis-docker-gordon-skill
description: Bridge to Docker + Gordon (Docker AI). Docker MCP server is wired (`docker-mcp`). Use for container lifecycle ops, image builds, Docker Compose, runtime diagnosis. Coordinate with Hermes for hermes-mcp-* container issues.
---

# Docker / Gordon Bridge

Docker CLI is at `C:\Program Files\Docker\Docker\resources\bin\docker.exe`. The `docker-mcp` MCP server is wired and enabled. Gordon (Docker AI) is part of Docker Desktop and is invoked via the `docker ai` subcommand.

## Two ways to call Docker

### 1. Via MCP (`docker-mcp`)

Use `mcp_invoke` against `docker-mcp` for tool-level container operations.

### 2. Via shell

```powershell
# List running containers
& 'C:\Program Files\Docker\Docker\resources\bin\docker.exe' ps

# List all containers (incl. stopped)
& 'C:\Program Files\Docker\Docker\resources\bin\docker.exe' ps -a

# Inspect hermes-mcp-* fleet
& 'C:\Program Files\Docker\Docker\resources\bin\docker.exe' ps -a --filter "name=hermes-mcp-"

# Gordon (Docker AI) — requires Docker Desktop 4.x+
& 'C:\Program Files\Docker\Docker\resources\bin\docker.exe' ai "ping"

# Image operations
& 'C:\Program Files\Docker\Docker\resources\bin\docker.exe' images
& 'C:\Program Files\Docker\Docker\resources\bin\docker.exe' build -t myimage .
```

## Hard rules (NEVER violate)

- 🚫 `docker container prune -a` — **NEVER** (lost the Hermes swarm 2026-08-08).
- 🚫 `docker rm -f hermes-mcp-*` — never against the load-bearing fleet.
- 🚫 `--force` operations on Hermes containers without R0.
- ✅ Diagnose first: `docker inspect`, `docker logs`, `docker stats`.
- ✅ Restart ONE container if needed: `docker restart <container>`.
- ✅ Coordinate with Hermes (`hermes mcp test <name>`) for hermes-mcp-* issues.

## Cross-bridge coordination

- **Hermes** owns the 33 `hermes-mcp-*` containers at the orchestration layer.
- **Docker / Gordon** owns the runtime / container-level view.
- When a `hermes-mcp-*` misbehaves: **Gordon diagnoses, Hermes coordinates the fix**.

## Reference

- Bridge file: `C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\10_BRIDGES\10_gordon.md`
- Doctrine: `SENTINEL_OPERATIONAL_DOCTRINE.md §9, §10`
