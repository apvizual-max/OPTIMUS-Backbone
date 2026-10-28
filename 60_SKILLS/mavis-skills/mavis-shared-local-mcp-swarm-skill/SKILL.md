---
name: mavis-shared-local-mcp-swarm-skill
description: |
  Master guide for accessing and utilizing the Shared Local MCP Container Swarm
  across Antigravity AI, Antigravity CLI (agy), Gemini CLI, Hermes Desktop App,
  and Hermes CLI. Standardizes MCP endpoint mappings, Docker container state,
  and double programming fallback paths.
license: proprietary
metadata:
  version: v1.0
  publisher: apviz
---

# Shared Local MCP Container Swarm Usage Skill

This skill provides complete operational guidelines for connecting to and utilizing the **Shared Local MCP Container Swarm** across all local agent runtimes (Antigravity AI, Antigravity CLI `agy`, Gemini CLI, Hermes Desktop App, and Hermes CLI).

---

## 1. System Architecture & Universal Endpoint Matrix

The local MCP stack operates in a **Double Programming Architecture**:
* **Tier 1 (Native Process Fallback)**: Executed directly via Python virtual environment or Node.js runtime.
* **Tier 2 (Docker Swarm High Availability)**: Docker container services configured in `C:\Users\apviz\AppData\Local\hermes\mcp-servers\docker-compose.mcp.yml` with `restart: always`.

### Universal MCP Endpoint Table

| MCP Server Name | Purpose / Functionality | Docker Container | Local Endpoint / Transport |
| :--- | :--- | :--- | :--- |
| **`antigravity-bridge`** | Antigravity-Hermes IPC task queue | `hermes-mcp-antigravity-bridge` | Stdio / `python -m antigravity_bridge.server` |
| **`optimus-orchestrator`** | Multi-agent DAG task scheduler | `hermes-mcp-optimus-orchestrator` | Stdio / `python -m optimus_orchestrator.server` |
| **`session-replay`** | SQLite session history recorder | `hermes-mcp-session-replay` | Stdio / `python -m session_replay.server` |
| **`hermes-profile`** | Hermes profile & SOUL state manager | `hermes-mcp-hermes-profile` | Stdio / `python -m hermes_profile.server` |
| **`windows-system`** | Windows OS system control tools | `hermes-mcp-windows-system` | Stdio / `python -m windows_system.server` |
| **`google-workspace-mcp`** | Google Calendar, Drive, Docs, Gmail | `hermes-mcp-google-workspace` | `npx -y google-workspace-mcp mcp` |
| **`discord-mcp`** | Discord Bot API & messaging | `hermes-mcp-discord` | `npx -y discord-mcp` |
| **`telegram-bot-mcp`** | Telegram Bot API tools | `hermes-mcp-telegram-bot` | Stdio / `python -m telegram_bot_mcp.server` |
| **`whatsapp-mcp`** | WhatsApp Web session wrapper | `hermes-mcp-whatsapp` | Stdio / `python -m whatsapp_mcp.server` |
| **`docker-mcp`** | Docker socket & container control | `hermes-mcp-docker` | Port 2375 / Docker Socket |
| **`elasticsearch-mcp`** | Log indexing & vector memory | `hermes-mcp-elasticsearch` | Port 9200 (`http://localhost:9200`) |
| **`postgresql-mcp`** | Relational DB storage | `postgres-mcp` | Port 5432 (`localhost:5432`) |
| **`redis-mcp`** | High-speed cache & key-value | `redis-mcp` | Port 6379 (`localhost:6379`) |
| **`minio-mcp`** | S3-compatible object storage | `minio-mcp` | Port 9000 (`http://localhost:9000`) |
| **`prometheus-mcp`** | System metrics collector | `prometheus-mcp` | Port 9090 (`http://localhost:9090`) |
| **`tempo-mcp`** | Distributed trace analyzer | `tempo` | Port 3200 (`http://localhost:3200`) |
| **`vault-mcp`** | Secret vault storage | `vault-mcp` | Port 8200 (`http://localhost:8200`) |
| **`searxng-mcp`** | Meta search engine | `searxng` | Port 8081 (`http://localhost:8081`) |

---

## 2. Configuration Integration Across Runtimes

### 2.1. Antigravity & Gemini CLI (`C:\Users\apviz\.gemini\config\mcp_config.json`)
To enable any of these MCP servers in Antigravity or Gemini CLI, reference them in `mcp_config.json`:

```json
{
  "mcpServers": {
    "google-workspace": {
      "command": "C:/Program Files/nodejs/npx.cmd",
      "args": ["-y", "google-workspace-mcp", "mcp"],
      "env": {
        "GOOGLE_EMAIL_USER": "apvizual@gmail.com",
        "GOOGLE_APP_PASSWORD": "xaoumihipoadltzr",
        "GOOGLE_WORKSPACE_APP_NAME": "Sentinel_Hermes"
      }
    },
    "discord": {
      "command": "C:/Program Files/nodejs/npx.cmd",
      "args": ["-y", "discord-mcp"],
      "env": {
        "DISCORD_BOT_TOKEN": "MTUzNDY1MzY1MTQ3MjM1NTM3OA.GU_JLI.ULA_ODtorn7vofH1a6BiYYbZH9K_IZtFraX-V0"
      }
    }
  }
}
```

### 2.2. Hermes App & Hermes CLI (`C:\Users\apviz\AppData\Local\hermes\config.yaml`)
Registered under `mcp_servers` section with global environment overrides in `C:\Users\apviz\AppData\Local\hermes\.env`.

---

## 3. Autostart & High Availability Verification

All swarm containers and background daemons are configured to start automatically at Windows logon via:
1. Windows Startup Launcher: `C:\Users\apviz\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\Hermes_Sentinel_Autostart.bat`
2. PowerShell Orchestrator: `C:\Users\apviz\AppData\Local\hermes\scripts\autostart_hermes_swarm.ps1`

To check swarm status from terminal:
```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```
