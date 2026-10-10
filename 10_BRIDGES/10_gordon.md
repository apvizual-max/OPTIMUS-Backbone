# Bridge — Gordon (Docker AI)

**Status**: ✅ WIRED — Docker Desktop 4.91.0 + Docker CLI 29.8.0 + `docker-mcp` MCP wired + `docker-gordon` skill installed.

## Role in the swarm

Gordon is Docker's built-in AI assistant for **container-level operations**: Dockerfile review, image suggestions, runtime diagnosis, compose troubleshooting. Mavis dispatches to Gordon when a task is container-shaped and Gordon's specialized knowledge outperforms generic reasoning.

## Surface (live-verified 2026-09-18)

- **Docker Desktop**: 4.91.0 (build 239619)
- **Docker CLI**: v29.8.0 (API 1.56, Go 1.26.8)
- **Context**: `desktop-linux`
- **MCP to Mavis**: `docker-mcp` MCP server wired and enabled (npm `mcp-docker` v1.0.0)
- **MCP via Hermes**: `docker-mcp` and `docker-gordon-bridge` already running in Hermes's fleet
- **Skill**: `docker-gordon` installed at `C:\Users\apviz\.minimax\agents\mavis\skills\docker-gordon\`

## Activation (live)

- ✅ Docker CLI reachable at `C:\Program Files\Docker\Docker\resources\bin\docker.exe`
- ✅ 31 `hermes-mcp-*` containers running and visible via `docker ps -a --filter "name=hermes-mcp-"`
- ✅ `docker-mcp` MCP wired in Mavis profile
- [ ] Gordon (`docker ai` subcommand) availability TBD — Docker Desktop 4.x has it, but may need Docker Desktop sign-in

## Use cases

- Dockerfile optimization review
- Diagnosing container crashes / OOM / network issues
- Compose-file suggestions
- Image-size and layer analysis
- **Hermes container health checks** (coordinate with `10_BRIDGES/10_hermes.md`)

## Dispatch protocol

1. State the container concern clearly
2. Attach relevant `docker inspect` / log output as needed
3. Receive Gordon's recommendation
4. **NEVER auto-apply destructive suggestions** (volume delete, image prune, etc.) — R0 required

## Cross-bridge coordination

Gordon and Hermes are tightly coupled:
- Hermes owns the 31 `hermes-mcp-*` containers at the orchestration layer
- Gordon owns the runtime/container-level view
- When a `hermes-mcp-*` container misbehaves, **Gordon diagnoses, Hermes coordinates the fix**

## JURNAL_OGLINDA

| Date | Event | Notes |
|---|---|---|
| 2026-09-18 | Bridge wired | ✅ Docker Desktop 4.91.0, CLI 29.8.0. 31 hermes-mcp-* containers live. `docker-mcp` MCP wired (Mavis side). `docker-gordon` skill installed. Gordon subcommand availability TBD. |
