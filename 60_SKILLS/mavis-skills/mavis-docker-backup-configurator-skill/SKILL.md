---
name: mavis-docker-backup-configurator-skill
description: Backup Docker configurator for queue and container recovery.
version: 1.1.0
author: Alex P., Antigravity
license: MIT
platforms: [windows, linux]
metadata:
  hermes:
    tags: [docker, devops, backup, gordon, mcp, container, security]
    category: devops
---

# Docker Backup Configurator Skill

Antigravity operates as the sovereign backup Docker Configurator when Gordon (the primary Docker AI manager) is rate-limited, unreachable, or failing. It executes tasks across the station's container infrastructure, arbitrates the operational queue, enforces security boundaries, and provides autonomous self-healing for MCP 2.0+ compatibility.

## When to Use

- When Gordon is rate-limited, down, or fails to complete Docker tasks.
- When processing pending requests in `C:\Users\apviz\DOCKER_QUEUE\requests\`.
- When auditing, maintaining, or synchronizing Docker MCP container swarms.
- When diagnosing SDK incompatibility or container crashes across MCP servers.
- When applying security hardening (localhost binding, host gateway resolution).
- When performing disaster recovery using `C:\Users\apviz\DOCKER_BACKUP`.

## Prerequisites

- Station Docker Engine running and responsive.
- Single Source of Truth configurations located at:
  - APVIZ Compose: `C:\Users\apviz\docker-compose.yml`
  - MCP Compose: `C:\Users\apviz\AppData\Local\hermes\mcp-servers\docker-compose.mcp.yml`
  - Hermes Config: `C:\Users\apviz\AppData\Local\hermes\config.yaml`
  - Operational Queue: `C:\Users\apviz\DOCKER_QUEUE\`
  - Golden Backup Root: `C:\Users\apviz\DOCKER_BACKUP\`

## Quick Reference

| Component | Path / Location | Target Scope |
|---|---|---|
| APVIZ Stack | `C:\Users\apviz\docker-compose.yml` | 19 Host system containers (Hardened to 127.0.0.1) |
| MCP Swarm | `...\hermes\mcp-servers\docker-compose.mcp.yml` | 31 Hermes & Sentinel AI containers |
| Queue Requests | `C:\Users\apviz\DOCKER_QUEUE\requests\` | Inbound operational tasks |
| Queue Responses | `C:\Users\apviz\DOCKER_QUEUE\responses\` | Completed task receipts |
| Queue Log | `C:\Users\apviz\DOCKER_QUEUE\logs\queue_operations.log` | Append-only execution audit |
| Backup Compose | `C:\Users\apviz\DOCKER_BACKUP\compose-files\` | Golden state replicas |

## Procedure

### 1. The Two-Tier Container Boundary Policy
The station's Docker ecosystem is strictly divided into two non-overlapping sections:
1. **Host Section (`APVIZ`)**: 19 containers managing databases, storage, browsers, and core host services (`C:\Users\apviz\docker-compose.yml`).
   - **Rule**: All exposed ports MUST bind to `127.0.0.1` (`127.0.0.1:PORT:PORT`) to prevent unauthenticated remote network exposure across Wi-Fi or LAN.
   - **Rule**: Containers needing host connectivity (e.g. `open-webui` reaching host Ollama) MUST define `extra_hosts: ["host.docker.internal:host-gateway"]`.
2. **AI Section (`MCP`)**: 31 containers running custom Sentinel and Hermes MCP microservices (`C:\Users\apviz\AppData\Local\hermes\mcp-servers\docker-compose.mcp.yml`).
   - **Rule**: Configuration MUST strictly mirror Hermes `config.yaml` as the Single Source of Truth (SOT).

### 2. Operational Queue Processing (`DOCKER_QUEUE`)
1. **Scan Inbound Requests**:
   - Inspect `C:\Users\apviz\DOCKER_QUEUE\requests\*.json`.
2. **Validate Request**:
   - Verify required fields (`id`, `timestamp`, `agent`, `action`, `params`).
   - Validate against `C:\Users\apviz\DOCKER_QUEUE\schemas\request_schema.json`.
3. **Execution**:
   - For low-risk inspection (`ps`, `logs`, `inspect`): execute immediately.
   - For swarm synchronization: run `docker compose -f ... up -d --remove-orphans`.
4. **Generate & Save Response**:
   - Build JSON matching `C:\Users\apviz\DOCKER_QUEUE\schemas\response_schema.json`.
   - Write to `C:\Users\apviz\DOCKER_QUEUE\responses\[REQUEST_ID]_response.json`.
5. **Append Audit Entry**:
   - Append standardized line to `C:\Users\apviz\DOCKER_QUEUE\logs\queue_operations.log`:
     `[TIMESTAMP] [AGENT] [ACTION] [REQUEST_ID] [STATUS] [DURATION] [DETAILS]`

### 3. Agentic & User-in-the-Loop Gordon Delegation
- **Normal Flow**: Delegate Docker tasks to Gordon by creating JSON requests in `DOCKER_QUEUE\requests\`. Prompt Gordon via desktop app or Docker CLI and await response in `responses\`.
- **Feedback Loop**: If Gordon returns partial success or errors, analyze Gordon's logs, iterate on parameters, and re-queue.
- **Failover to Backup Mode**: If Gordon is rate-limited or down:
  1. Assume sovereign backup configurator role.
  2. Parse the pending request directly.
  3. Execute necessary Docker commands.
  4. Write response and audit log.

### 4. Autonomous Universal MCP 2.0+ Compatibility Engine
When Python virtual environments update `mcp` to `>=2.0.0`, upstream decorators (`@server.list_tools()`, `@server.call_tool()`) and `request_context` are removed.
To reproduce the fix autonomously:
1. **Patch `mcp.server.lowlevel.server.py`**:
   - Define `_current_request_context = contextvars.ContextVar("_current_request_context", default=None)`.
   - Export `request_ctx = _current_request_context`.
   - Inject `_ctx_middleware` into `Server.middleware`:
     ```python
     async def _ctx_middleware(ctx, call_next):
         token = _current_request_context.set(ctx)
         try:
             return await call_next(ctx)
         finally:
             _current_request_context.reset(token)
     ```
   - Add backward-compatibility decorators to `class Server`:
     `list_tools()`, `call_tool()`, `list_prompts()`, `get_prompt()`, `list_resources()`, `read_resource()`, `list_resource_templates()`, and `@property def request_context(self): return _current_request_context.get()`.
2. **Export Compatibility Pointers**:
   - Export `request_ctx` in `mcp.server` and `mcp.server.lowlevel`.
   - Add `RequestContext = Any` in `mcp.shared.context`.
3. **Register Site-Packages `.pth` Links**:
   - Ensure `__editable__.hermes_profile_mcp-0.1.0.pth` points to `C:\Users\apviz\AppData\Local\hermes\mcp-servers\custom\hermes-profile\src`.
4. **Native Telegram Bot Architecture**:
   - Avoid `fastmcp` in `telegram-bot-mcp`. Use standard `Server("telegram-bot-mcp")` with native `list_tools` and `call_tool`.

### 5. APVIZ Security Hardening Protocol
1. **Localhost Binding**:
   - For all services in `C:\Users\apviz\docker-compose.yml`, prefix exposed ports with `127.0.0.1:`:
     - `127.0.0.1:5432:5432` (Postgres)
     - `127.0.0.1:6379:6379` (Redis)
     - `127.0.0.1:9200:9200` & `127.0.0.1:9300:9300` (Elasticsearch)
     - `127.0.0.1:8200:8200` (Vault)
     - `127.0.0.1:8080:8080` (Open-WebUI)
     - `127.0.0.1:8082:8080` (Stirling-PDF)
     - `127.0.0.1:8888:8080` (Searxng)
     - `127.0.0.1:9090:9090` (Prometheus)
     - `127.0.0.1:3000:3000` (Aion-UI)
     - `127.0.0.1:3001:3000` (LibreOffice)
     - `127.0.0.1:6080:6080` & `127.0.0.1:9377:9377` (Camofox Latest)
     - `127.0.0.1:6081:6080` & `127.0.0.1:9378:9377` (Camofox Beta)
     - `127.0.0.1:4444:4444` & `127.0.0.1:7900:7900` (Selenium)
     - `127.0.0.1:8086:8085` (Whatsmeow)
2. **Host Resolution**:
   - In `open-webui`: set `OLLAMA_BASE_URL=http://host.docker.internal:11434` and add `extra_hosts: ["host.docker.internal:host-gateway"]`.

## Pitfalls

- **Do NOT bind APVIZ ports to 0.0.0.0**: Binds without authentication expose databases and credentials to the local network.
- **Do NOT delete custom Hermes services**: Sentinel daemon, Antigravity bridge, Optimus orchestrator, Session replay, and Gordon bridge are vital system extensions.
- **Do NOT retain obsolete containers**: Third-party obsolete containers (`hermes-mcp-minio`, `hermes-mcp-tempo`) must be pruned when removed from SOT.
- **Do NOT touch APVIZ compose with MCP compose commands**: All MCP compose operations must explicitly specify `-f C:\Users\apviz\AppData\Local\hermes\mcp-servers\docker-compose.mcp.yml`.

## Verification

1. Run `docker ps` to verify 50 total containers (19 APVIZ + 31 MCP).
2. Test all listening ports on `127.0.0.1` using socket connections.
3. Run `hermes mcp test [name]` to verify tool discovery across all servers.
4. Validate written responses against `C:\Users\apviz\DOCKER_QUEUE\schemas\response_schema.json`.