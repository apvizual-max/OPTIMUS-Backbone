---
name: mavis-autostart-docker-swarm-skill
description: |
  Manages Docker Compose 18-container MCP Swarm, 48 CPU / 48GB RAM WSL2 allocation,
  pre-compiled Dockerfile base image (mcp==1.3.0), Grafana Tempo trace persistence,
  Datacloud MCP Proxy disabling (context, notebooks, visualization),
  Windows startup autostart integration, and 1-click System Save-Point restoration.
license: proprietary
metadata:
  version: v5
  publisher: apviz
---

# Autostart Docker Swarm & System Save-Point Maintenance Skill

Maintains autostart infrastructure, workstation hardware allocation (48 CPUs / 48GB RAM), pre-compiled Docker image builds, Grafana Tempo tracing, Antigravity IDE Datacloud MCP proxy disabling, and 1-click System Save-Point restoration.

## Infrastructure Matrix & System Save-Point

- **Hardware Allocation (`.wslconfig`)**: `C:\Users\apviz\.wslconfig` (`processors=48`, `memory=48GB`, `swap=4GB`)
- **Docker Compose Spec**: `C:\Users\apviz\AppData\Local\hermes\mcp-servers\docker-compose.mcp.yml` (18 Services, `restart: always`, `stdin_open: true`, `tty: true`)
- **Pre-Compiled Base Image (`Dockerfile`)**: `C:\Users\apviz\AppData\Local\hermes\mcp-servers\Dockerfile` (`hermes-mcp-base:latest`, `mcp==1.3.0`, `pyyaml`, `fastmcp`, `httpx`, `aiohttp`, `asyncpg`, `hvac`, `boto3`, `psutil`)
- **Grafana Tempo Tracing Config**: `C:\Users\apviz\AppData\Local\hermes\scripts\tempo-config.yaml`
- **Antigravity IDE MCP Config**: `C:\Users\apviz\.gemini\config\mcp_config.json` (`context`, `notebooks`, `visualization` set to `"disabled": true`)
- **Windows Startup Integration**: `C:\Users\apviz\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\start_docker_desktop.vbs`
- **Reference Save-Point Directory**: `C:\Users\apviz\Documents\Antigravity_Folder\Antigravity_Projects\Docker_Config_SavePoint`
- **1-Click System Restore Script**: `C:\Users\apviz\Documents\Antigravity_Folder\Antigravity_Projects\Docker_Config_SavePoint\restore_docker_setup.py`

## Recovery & Save-Point Restoration Command
To restore the entire Docker setup, IDE MCP configuration, and container swarm to the verified reference save-point:
```powershell
python "C:\Users\apviz\Documents\Antigravity_Folder\Antigravity_Projects\Docker_Config_SavePoint\restore_docker_setup.py"
```
