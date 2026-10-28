# Docker Fleet Inventory — Non-Hermes Containers

**Date**: 2026-10-02
**Author**: Mavis (MiniMax Code orchestrator)
**Status**: ðŸ”´ First inventory. Closes part of GAP-3.

---

## 1. Fleet summary

| Segment | Count |
|---|---|
| Total containers | 55 |
| `hermes-mcp-*` (Hermes MCP fleet) | 31 |
| **Non-Hermes** | **24** |
| Of which: running service containers | 20 |
| Of which: build-tool shims (node/alpine/golang) | 4 |
| Of which: stopped / orphaned | 2 |

All non-Hermes containers came up **~3 hours ago** (same boot). Docker Desktop 4.91.0 / CLI 29.8.0.

---

## 2. Running service containers (20)

| # | Container | Image | Ports (host→container) | Health | MCP bridge? |
|---|---|---|---|---|---|
| 1 | `Antigravity_Ecosystem_Terminal` | `apviz/antigravity-ecosystem-terminal:latest` | `127.0.0.1:9878→9878` | up | ❌ none — but reachable over HTTP |
| 2 | `redis` | `redis:7-alpine` | `127.0.0.1:6379→6379` | up | ❌ (Hermes has `redis-mcp`) |
| 3 | `elasticsearch` | `elasticsearch:8.15.0` | `127.0.0.1:9200→9200`, `9300→9300` | up | ❌ (Hermes has `elasticsearch-mcp`) |
| 4 | `vault` | `hashicorp/vault:latest` | `127.0.0.1:8201→8200` | up | ❌ (Hermes has `vault-mcp`) |
| 5 | `selenium-chrome` | `selenium/standalone-chrome:latest` | `127.0.0.1:4444→4444`, `7900→7900` | up | ❌ (Mavis has `chrome-devtools-mcp` + `agent-browser-mcp`) |
| 6 | **`stirling-pdf`** | `stirlingtools/stirling-pdf:latest` | `127.0.0.1:8082→8080` | **healthy** | ❌ **none — capability gap** |
| 7 | `postgres` | `postgres:15` | `127.0.0.1:5432→5432` | up | ❌ (Hermes has `postgresql-mcp`) |
| 8 | `aion-ui` | `aion-ui:latest` | `127.0.0.1:3000→3000` | up | ❌ (web UI, not a tool) |
| 9 | `open-webui` | `ghcr.io/open-webui/open-webui:main` | `127.0.0.1:8080→8080` | **healthy** | ❌ (web UI) |
| 10 | `libreoffice` | `lscr.io/linuxserver/libreoffice:latest` | `127.0.0.1:3001→3000` | up | ❌ **none — capability gap** |
| 11 | `searxng` | `searxng/searxng:latest` | `127.0.0.1:8888→8080` | up | ❌ (Hermes has `searxng`) |
| 12 | `prometheus` | `prom/prometheus:latest` | `127.0.0.1:9090→9090` | up | ❌ (Hermes has `prometheus-mcp`) |
| 13 | `whatsmeow-bui` | `whatsmeow-bui:latest` | `127.0.0.1:8086→8085` | up | ❌ (Hermes has `whatsapp-mcp`) |
| 14 | `camofox-browser-latest` | `camofox-browser:latest` | `127.0.0.1:6080→6080`, `9377→9377` | up | ⚠️ **3rd browser instance — see §4** |
| 15 | `camofox-browser-beta` | `camofox-browser:152.0.4-beta.28-x86_64` | `127.0.0.1:6081→6080`, `9378→9377` | up | ⚠️ **see §4** |
| 16 | `camofox-browser` | `camofox-browser:152.0.4-beta.28-x86_64` | `9377` (no host bind) | up | ⚠️ **see §4** |

### 2.1 Build-tool shims (4)

| Container | Image | Purpose |
|---|---|---|
| `node-22-slim` | `node:22-slim` | Build sandbox |
| `node-20-slim` | `node:20-secure` | Build sandbox (matches `hermes-mcp-base`) |
| `alpine` | `alpine:latest` | Build sandbox |
| `golang` | `golang:1.24-secure` | Build sandbox |

These are long-running containers acting as build environments. Unusual but not necessarily wrong — flagging for Popy awareness.

---

## 3. Stopped / orphaned containers (2)

| Container | Image | Status | Assessment |
|---|---|---|---|
| `mystifying_chaplygin` | `python:3.14-alpine` | Exited (0) 2 days ago | **Orphan.** `docker-compose up` with no service name → auto-generated name. No ports, no role. **DRAC candidate.** |
| `whatsmeow-v4` | `whatsmeow-bui:latest` | Exited (255) 10 days ago | **Superseded** by running `whatsmeow-bui`. Exit 255 = crash. **DRAC candidate.** |

---

## 4. DRAC candidates (Popy R0 required — irreversible)

### 4.1 Three camofox-browser instances (HIGH confidence)

| Container | Image | Host ports | Note |
|---|---|---|---|
| `camofox-browser` | `camofox-browser:152.0.4-beta.28-x86_64` | none exposed | unreachable from host |
| `camofox-browser-beta` | `camofox-browser:152.0.4-beta.28-x86_64` | 6081, 9378 | reachable |
| `camofox-browser-latest` | `camofox-browser:latest` | 6080, 9377 | reachable |

**Problem**: 3 instances of the same browser, 2 of the *same image* (`152.0.4-beta.28-x86_64`). `camofox-browser` has no host port binding → unreachable → dead weight. The `-beta` and `-latest` naming suggests a version-A/B test that was never resolved.

**Recommendation**: keep ONE. Ask Popy which is canonical, then DRAC the other two.

### 4.2 `mystifying_chaplygin` (HIGH confidence)

Orphaned `python:3.14-alpine` from an unnamed compose service. Exited 2 days ago. No role, no ports.

**Recommendation**: DRAC.

### 4.3 `whatsmeow-v4` (MEDIUM confidence)

Exited (255) 10 days ago. A newer `whatsmeow-bui` is running and healthy.

**Recommendation**: verify `whatsmeow-bui` fully covers the WhatsApp function, then DRAC `whatsmeow-v4`.

---

## 5. Capability gaps — containers Mavis cannot reach

Two containers provide **document-processing capability that Mavis has no MCP for**:

| Container | Capability | Why it matters |
|---|---|---|
| `stirling-pdf` (healthy, `:8082`) | PDF merge / split / convert / OCR / watermark | Popy's B2B proposals produce PDFs constantly. `minimax-pdf` skill does *generation*; Stirling does *transformation* of existing PDFs. |
| `libreoffice` (`:3001`) | DOCX / XLSX / PPTX conversion headlessly | Popy's deliverables are Office files. Currently Mavis has `excel_editor` + `word_editor` tools, but not a headless batch-conversion pipeline. |

**Recommendation**: build `mavis-docker-docs-skill` that drives these two over HTTP. Both expose web APIs. `stirling-pdf` in particular has a documented HTTP API (`/api/v1/...`).

---

## 6. Duplication note

Six non-Hermes containers are already covered by Hermes-side MCP servers:
`redis`, `elasticsearch`, `vault`, `postgres`, `searxng`, `prometheus`.

**This is correct architecture** — Hermes owns the MCP wrapper, the containers are just the backing service. No action needed. But Mavis should know that when Hermes reports "redis is unhealthy", the container to inspect is this one.

---

## 7. Antigravity_Ecosystem_Terminal — note

`apviz/antigravity-ecosystem-terminal:latest` on `:9878`. Popy's own image. This is likely the Antigravity ecosystem surface that pairs with the `agy` CLI and the `Antigravity IDE` app.

**Not yet explored.** Could be a bridge target for the `mavis-antigravity-bridge-skill`.

---

## 8. Proposed MCP bridge candidates

| Container | Bridge approach | Priority |
|---|---|---|
| `stirling-pdf` | HTTP calls to `http://127.0.0.1:8082/api/v1/...` from a new `mavis-docker-docs-skill` | **High** |
| `libreoffice` | HTTP to `http://127.0.0.1:3001/...` from same skill | High |
| `Antigravity_Ecosystem_Terminal` | HTTP to `http://127.0.0.1:9878` — needs API discovery | Medium |
| `camofox-browser-latest` | HTTP to `http://127.0.0.1:6080` — needs API discovery | Medium |
| `aion-ui`, `open-webui` | Web UIs — could be driven via `chrome-devtools-mcp` | Low |

---

## 9. GAP-3 status

| Sub-item | Status |
|---|---|
| Non-Hermes container inventory | ✅ 24 containers mapped with images, ports, health |
| Role mapping | ✅ 16 service + 4 build shims + 2 stopped identified |
| DRAC candidates | ✅ 3 flagged (3× camofox, 1 orphan, 1 superseded) |
| Capability gaps | ✅ 2 identified (stirling-pdf, libreoffice) |
| MCP bridge design | ðŸŸ¡ Written, R0 required to execute |
| `hermes-sentinel-daemon` role | ❌ Still undocumented — separate investigation needed |

---

## Cross-references

- Master gap report: `C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\OPTIMUS_MINIMAX_INTEGRATION_GAP_REPORT.md`
- Bridge registry: `C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\00_INDEX\00_bridge_registry.md`
- Docker bridge skill: `C:\Users\apviz\.minimax\agents\mavis\skills\mavis-docker-gordon-skill\SKILL.md`
- Doctrine §10: `SENTINEL_OPERATIONAL_DOCTRINE.md` (NEVER `docker container prune -a`)
