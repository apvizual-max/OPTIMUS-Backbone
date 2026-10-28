# Port Map Matrix & Network Hardening Blueprint

Authoritative mapping of all 18 published host ports across the 14 listening containers.

## Security Invariants
1. **100% Loopback Only**: Every published port is bound to `127.0.0.1`.
2. **Zero `0.0.0.0` Bindings**: No container listens on all interfaces (`0.0.0.0`).
3. **Vault Remap**: HashiCorp Vault is mapped to `127.0.0.1:8201` because host PID 17800 (`OpenWhispr.exe`) holds port 8200.

| Container Name | Published Host Mapping | Protocol | Internal Target | Service |
|---|---|---|---|---|
| `aion-ui` | `127.0.0.1:3000->3000` | HTTP | 3000/tcp | AION Web UI |
| `camofox-browser-beta` | `127.0.0.1:6081->6080` | HTTP | 6080/tcp | Camofox noVNC (Beta) |
| `camofox-browser-beta` | `127.0.0.1:9378->9377` | HTTP | 9377/tcp | Camofox CDP (Beta) |
| `camofox-browser-latest` | `127.0.0.1:6080->6080` | HTTP | 6080/tcp | Camofox noVNC (Stable) |
| `camofox-browser-latest` | `127.0.0.1:9377->9377` | HTTP | 9377/tcp | Camofox CDP (Stable) |
| `elasticsearch` | `127.0.0.1:9200->9200` | HTTP | 9200/tcp | Elasticsearch REST API |
| `elasticsearch` | `127.0.0.1:9300->9300` | TCP | 9300/tcp | Elasticsearch Transport |
| `libreoffice` | `127.0.0.1:3001->3000` | HTTP | 3000/tcp | LibreOffice Web Interface |
| `open-webui` | `127.0.0.1:8080->8080` | HTTP | 8080/tcp | Open-WebUI Client |
| `postgres` | `127.0.0.1:5432->5432` | TCP | 5432/tcp | PostgreSQL Database Engine |
| `prometheus` | `127.0.0.1:9090->9090` | HTTP | 9090/tcp | Prometheus Dashboard & API |
| `redis` | `127.0.0.1:6379->6379` | TCP | 6379/tcp | Redis In-Memory Store |
| `searxng` | `127.0.0.1:8888->8080` | HTTP | 8080/tcp | SearXNG Metasearch Engine |
| `selenium-chrome` | `127.0.0.1:4444->4444` | HTTP | 4444/tcp | Selenium Hub / WebDriver |
| `selenium-chrome` | `127.0.0.1:7900->7900` | HTTP | 7900/tcp | Selenium noVNC Console |
| `stirling-pdf` | `127.0.0.1:8082->8080` | HTTP | 8080/tcp | Stirling-PDF Application |
| `vault` | `127.0.0.1:8201->8200` | HTTP | 8200/tcp | HashiCorp Vault Secrets |
| `whatsmeow-bui` | `127.0.0.1:8086->8085` | HTTP | 8085/tcp | WhatsApp Bridge Web UI |
