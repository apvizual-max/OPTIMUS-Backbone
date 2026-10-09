# Container Taxonomy: APVIZ & Hermes MCP Infrastructure

Authoritative catalog of all 50 running Docker containers on the host station.

## 1. APVIZ Production Stack (19 Containers)
Managed via `C:\Users\apviz\docker-compose.yml` (`com.docker.compose.project=apviz`).

| # | Container Name | Image / Base | Published Host Port | Function |
|---|---|---|---|---|
| 01 | `aion-ui` | `ghcr.io/dan-albers/aion-ui:latest` | `127.0.0.1:3000->3000` | AI Chat & Agent UI |
| 02 | `alpine` | `alpine:latest` | Internal | Utility / Sandbox Container |
| 03 | `camofox-browser-beta` | `camofox:beta` | `127.0.0.1:6081->6080`, `9378->9377` | Anti-Detect Browser (Beta) |
| 04 | `camofox-browser-latest` | `camofox:latest` | `127.0.0.1:6080->6080`, `9377->9377` | Anti-Detect Browser (Stable) |
| 05 | `elasticsearch` | `elasticsearch:8.15.0` | `127.0.0.1:9200->9200`, `9300->9300` | Full-Text & Vector Search |
| 06 | `golang` | `golang:1.23-alpine` | Internal | Go Tooling Environment |
| 07 | `hermes-mcp-git-base` | `hermes-mcp-base:latest` | Internal | Base Image & Git Runner |
| 08 | `libreoffice` | `linuxserver/libreoffice:latest` | `127.0.0.1:3001->3000` | Document Conversion & Office Suite |
| 09 | `node-20-slim` | `node:20-slim` | Internal | Node.js 20 Execution Context |
| 10 | `node-22-slim` | `node:22-slim` | Internal | Node.js 22 Execution Context |
| 11 | `open-webui` | `ghcr.io/open-webui/open-webui:main` | `127.0.0.1:8080->8080` | Web UI for Local LLMs |
| 12 | `postgres` | `postgres:15` | `127.0.0.1:5432->5432` | Relational Database Engine |
| 13 | `prometheus` | `prom/prometheus:latest` | `127.0.0.1:9090->9090` | System Metrics Collector |
| 14 | `redis` | `redis:7-alpine` | `127.0.0.1:6379->6379` | High-Speed Cache & Session Store |
| 15 | `searxng` | `searxng/searxng:latest` | `127.0.0.1:8888->8080` | Privacy-Preserving Metasearch Engine |
| 16 | `selenium-chrome` | `selenium/standalone-chrome:latest` | `127.0.0.1:4444->4444`, `7900->7900` | Headless Chrome Automation |
| 17 | `stirling-pdf` | `stirlingtools/stirling-pdf:latest` | `127.0.0.1:8082->8080` | Local PDF Processing & OCR |
| 18 | `vault` | `hashicorp/vault:latest` | `127.0.0.1:8201->8200` | HashiCorp Vault (Remapped for OpenWhispr) |
| 19 | `whatsmeow-bui` | `whatsmeow-bridge:latest` | `127.0.0.1:8086->8085` | WhatsApp Web Gateway Service |

## 2. Hermes MCP Container Swarm (31 Containers)
Managed via `C:\Users\apviz\AppData\Local\hermes\mcp-servers\docker-compose.mcp.yml` (`com.docker.compose.project=mcp-servers`).

| # | Container Name | Service Name | Channel / Network | Function |
|---|---|---|---|---|
| 20 | `hermes-mcp-agent-browser` | `agent-browser` | Host Bridge (`stdio`) | Persistent Browser Engine |
| 21 | `hermes-mcp-antigravity-bridge` | `antigravity-bridge` | Host Bridge (`stdio`) | Cross-Ecosystem Communication |
| 22 | `hermes-mcp-browser` | `browser` | Host Bridge (`stdio`) | Lightweight HTML Fetch & Scrape |
| 23 | `hermes-mcp-chrome-devtools` | `chrome-devtools` | Host Bridge (`stdio`) | CDP Interactive Control |
| 24 | `hermes-mcp-discord` | `discord` | Host Bridge (`stdio`) | Discord Bot Gateway & Moderation |
| 25 | `hermes-mcp-docker` | `docker` | Host Bridge (`stdio`) | Docker Engine API Inspector |
| 26 | `hermes-mcp-docker-gordon-bridge`| `docker-gordon-bridge` | Host Bridge (`stdio`) | Gordon A2A Delegation Bridge |
| 27 | `hermes-mcp-elasticsearch` | `elasticsearch` | Host Bridge (`stdio`) | ES Cluster RAG Connector |
| 28 | `hermes-mcp-filesystem` | `filesystem` | Host Bridge (`stdio`) | Sandboxed Local Filesystem |
| 29 | `hermes-mcp-git` | `git` | Host Bridge (`stdio`) | Git Automation Server |
| 30 | `hermes-mcp-goal-judge` | `goal-judge` | Host Bridge (`stdio`) | Autonomous Goal Compliance Judge |
| 31 | `hermes-mcp-google-drive` | `google-drive` | Host Bridge (`stdio`) | Google Drive Document Syncer |
| 32 | `hermes-mcp-google-workspace` | `google-workspace` | Host Bridge (`stdio`) | Docs, Sheets & Gmail Integration |
| 33 | `hermes-mcp-hermes-profile` | `hermes-profile` | Host Bridge (`stdio`) | 9-Profile Configuration Engine |
| 34 | `hermes-mcp-memory` | `memory` | Host Bridge (`stdio`) | Knowledge Graph Entity Memory |
| 35 | `hermes-mcp-notebooklm` | `notebooklm` | Host Bridge (`stdio`) | Google NotebookLM Assistant |
| 36 | `hermes-mcp-obsidian` | `obsidian` | Host Bridge (`stdio`) | Knowledge Vault RAG Connector |
| 37 | `hermes-mcp-optimus-orchestrator`| `optimus-orchestrator`| Host Bridge (`stdio`) | Sentinel Prime Coordination |
| 38 | `hermes-mcp-postgresql` | `postgresql` | Host Bridge (`stdio`) | MCP PostgreSQL SQL Engine |
| 39 | `hermes-mcp-prometheus` | `prometheus` | Host Bridge (`stdio`) | MCP Telemetry & Metrics |
| 40 | `hermes-mcp-qwen` | `qwen` | Host Bridge (`stdio`) | Qwen MCP Delegation Bridge |
| 41 | `hermes-mcp-redis` | `redis` | Host Bridge (`stdio`) | MCP Redis Command Executor |
| 42 | `hermes-mcp-searxng` | `searxng` | Host Bridge (`stdio`) | MCP Metasearch Aggregator |
| 43 | `hermes-mcp-sequential-thinking` | `sequential-thinking` | Host Bridge (`stdio`) | Multi-Step Reasoning Engine |
| 44 | `hermes-mcp-session-replay` | `session-replay` | Host Bridge (`stdio`) | Session Playback & Debugging |
| 45 | `hermes-mcp-telegram` | `telegram` | Host Bridge (`stdio`) | Telegram MTProto Userbot Client |
| 46 | `hermes-mcp-telegram-bot` | `telegram-bot` | Host Bridge (`stdio`) | Telegram Bot API Gateway |
| 47 | `hermes-mcp-vault` | `vault` | Host Bridge (`stdio`) | MCP HashiCorp Vault Secrets |
| 48 | `hermes-mcp-whatsapp` | `whatsapp` | Host Bridge (`stdio`) | WhatsApp Messaging Gateway |
| 49 | `hermes-mcp-windows-system` | `windows-system` | Host Bridge (`stdio`) | Native Windows OS Tooling |
| 50 | `hermes-sentinel-daemon` | `sentinel-daemon` | Host Bridge (`stdio`) | Invariant Guardian Daemon |
