---
name: mavis-antigravity-docker-admin-skill
description: Sovereign Docker admin fallback when Gordon is unreachable.
version: 1.0.0
author: Alex / Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [docker, administrator, fallback, mcp, container, sovereign]
    category: devops
---

# Antigravity Docker Administrator Skill

Sovereign Docker administration protocol for the Antigravity assistant when Gordon (Docker Desktop cagent) is offline, unreachable, crashing, or fails >3 retry loops. This skill equips Antigravity with full direct authority to monitor, heal, configure, and maintain all 50 Docker containers across the APVIZ Production Stack and the Hermes MCP Swarm. Under normal conditions, Docker management is delegated to Gordon; this skill executes sovereign control only upon explicit fallback triggers or direct R0 user instruction.

## When to Use
- Gordon is unresponsive, offline, or returns execution errors.
- A delegated task to Gordon via `antigravity-gordon-bridge` exceeds 3 iteration loops without satisfying requirements.
- Urgent or direct Docker management commands are issued by Alex with explicit R0 approval.
- Post-update verification or auto-healing of container dependencies (e.g. MCP Python 2.0+ SDK decorator recovery).
- Resolving port collisions (such as OpenWhispr on 8200 vs HashiCorp Vault on 8201) and ensuring 100% loopback binding (`127.0.0.1`).

## Prerequisites
- Docker Engine / Docker Desktop running on the Windows host.
- Python 3.10+ in system PATH or active virtual environment.
- Access to Docker compose definitions:
  - APVIZ Production Stack: `C:\Users\apviz\docker-compose.yml`
  - Hermes MCP Swarm: `C:\Users\apviz\AppData\Local\hermes\mcp-servers\docker-compose.mcp.yml`
- Access to sovereign backup repository: `C:\Users\apviz\DOCKER_BACKUP`.

## How to Run
- Run system-wide health audit:
  `python scripts/verify_docker_system.py`
- Inspect container statuses:
  `docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"`
- Manage APVIZ stack:
  `docker compose -f C:\Users\apviz\docker-compose.yml up -d`
- Manage MCP Swarm:
  `docker compose -f C:\Users\apviz\AppData\Local\hermes\mcp-servers\docker-compose.mcp.yml up -d`
- Auto-heal Hermes MCP servers:
  `python "C:\Users\apviz\AppData\Local\hermes\Hermes Local Configuration Engine\server.py" --silent`

## Quick Reference
| Operation | Command | Target / Scope |
|---|---|---|
| Complete Health Audit | `python scripts/verify_docker_system.py` | 50 containers + 18 ports |
| Restart APVIZ Service | `docker restart <service>` | APVIZ Stack (19 containers) |
| Restart MCP Container | `docker restart hermes-mcp-<service>` | MCP Swarm (31 containers) |
| Hardened Port Check | `netstat -ano \| findstr "0.0.0.0:"` | Must return 0 Docker ports |
| Vault Port Invariant | `127.0.0.1:8201->8200/tcp` | Evades OpenWhispr PID collision |
| Host Bridge Invariant | `host.docker.internal:host-gateway` | Inter-container host routing |

## Procedure
1. **Assess System State & Container Census**:
   - Execute `python scripts/verify_docker_system.py`.
   - Ensure all 50 containers (19 APVIZ + 31 MCP) are running or identified in expected state.
2. **Enforce Port Hardening & Security Invariants**:
   - Inspect exposed ports. All published ports MUST bind to `127.0.0.1`, never `0.0.0.0`.
   - Check port 8200/8201. If OpenWhispr is running on port 8200, ensure HashiCorp Vault is strictly bound to `127.0.0.1:8201:8200`.
3. **Handle Container Failure or CrashLoop**:
   - Retrieve container logs: `docker logs --tail 50 <container_name>`.
   - If Python MCP container throws `AttributeError: Server object has no attribute decorator` or validation errors:
     - Run `python "C:\Users\apviz\AppData\Local\hermes\Hermes Local Configuration Engine\server.py" --silent`.
     - Restart container: `docker restart <container_name>`.
4. **Manage Compose Lifecycle**:
   - APVIZ Compose file: `C:\Users\apviz\docker-compose.yml`.
   - Hermes MCP Compose file: `C:\Users\apviz\AppData\Local\hermes\mcp-servers\docker-compose.mcp.yml`.
   - Use `docker compose -f <path> restart <service>` for targeted restarts.
5. **Harmonize with Backup Repository**:
   - After any configuration change, update manifests in `C:\Users\apviz\DOCKER_BACKUP`.
   - Update `CONTAINER_MANIFEST.json` and recalculate `BACKUP_CHECKSUMS.txt`.

## Pitfalls
- **Do not bind ports to `0.0.0.0`**: Exposing containers to all network interfaces violates station security boundaries. Always use `127.0.0.1:<port>:<container_port>`.
- **Do not start Vault on port 8200**: OpenWhispr desktop app runs on host port 8200. Starting Vault on 8200 causes port binding collision error. Always use `8201`.
- **Do not bypass Gordon unnecessarily**: Gordon is the primary Docker manager. Antigravity acts as administrator ONLY on Gordon failure, timeout, or explicit escalation.
- **Do not destroy persistent volumes**: Named volumes (`apviz_stirling-data`, `apviz_postgres-data`, etc.) contain live application state. Never run `docker compose down -v`.

## Verification
- Run `python scripts/verify_docker_system.py` and confirm 100% pass:
  - 50/50 containers running.
  - 18/18 published ports bound to `127.0.0.1`.
  - Zero `0.0.0.0` bindings.
  - Vault responsive on `http://127.0.0.1:8201`.
