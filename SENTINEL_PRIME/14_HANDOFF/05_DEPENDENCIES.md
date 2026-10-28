# 05 — Dependencies

Every external dependency SENTINEL relies on, measured. Nothing here is inferred.

---

## 1. Runtime — measured on this machine

| Dependency | Measured version | State |
|---|---|---|
| **Docker** | server **29.8.1** | running; **63 containers** up |
| **Python** | **3.14.6** at `…\Python\pythoncore-3.14-64\python.exe` | working; all suites run |
| **PowerShell** | **5.1** | working; hard constraint — no PowerShell 7 syntax |
| **Node.js** | present (containers `node-22-slim`, `node-20-slim`) | used by the MCP fleet |
| **npm** | on PATH via `npm.cmd` | resolves packages; **two blueprint packages 404** |

**PowerShell 5.1 is a hard constraint, not a preference.** Variable names are case-insensitive, so
`$_path` and `$_PATH` collide; `Set-Content -Encoding UTF8` writes a BOM; and `&&`/`||` do not exist.
Scripts in this project are written to those rules and a test enforces that no script shadows a
parameter by case alone.

---

## 2. SENTINEL's own container

| Property | Measured |
|---|---|
| Name | `mavis-sentinel-hub` |
| Image | `mavis/sentinel-hub:1.0.0` |
| State | `running`, health `healthy` |
| Restart policy | `unless-stopped` — survives Docker restart and reboot |
| Port mapping | `127.0.0.1:8910 → 80/tcp` |
| Server | `nginx/1.31.6` |
| Identity header | `X-SENTINEL-Deployment: mavis-sentinel-hub` |
| Uptime at survey | 22 minutes (it had just been cold-started) |

**The image contains no application data.** Verified every run by `find` across the image filesystem:
no corpus, no `sentinel-state.json`. This is what prevents an image from drifting from disk.

---

## 3. npm packages

### Declared in the blueprint — measured against the registry

| Package | Version | State |
|---|---|---|
| `@modelcontextprotocol/server-filesystem` | **2026.8.31** | **resolves** |
| `@playwright/mcp` | **0.0.83** | **resolves** |
| `@modelcontextprotocol/server-fetch` | — | **does not resolve** |
| `@modelcontextprotocol/server-git` | — | **does not resolve** |

The last two returned a hard 404 while a control package answered `19.3.0` **in the same run** — so the
registry was reachable and the failures are real, not a network artefact.

### Used by the test suites — measured by running them

| Package | State | Consequence if missing |
|---|---|---|
| `playwright` (Python) | **present** — browser checks ran, all 12 tabs rendered | `dom_injection_guarded` reports `NOT_RUN`, never `FAIL` |

This distinction is load-bearing: an absent browser falsifies nothing, so the check reports `NOT_RUN`
rather than pretending the dashboard is verified.

---

## 4. Python modules

| Module | Used for | State |
|---|---|---|
| `ast`, `json`, `re`, `pathlib`, `subprocess`, `shutil`, `urllib`, `socket`, `hashlib` | stdlib | present |
| `PIL` | image processing test | present |
| `pypdf` | document processing test | present |
| `playwright` | browser rendering checks | present |
| `yaml` | Design config reading | present |

---

## 5. External binaries — one gap

| Binary | State | Consequence |
|---|---|---|
| **Tesseract** | **not on PATH** | OCR is unverified even if `pytesseract` were installed |

Registered as `BIN_TESSERACT`, `owner: Popy`, `fix_requires: R0 — external binary install`. It has not
been installed because it is an external dependency and installing software needs the operator's
approval. **Nothing in the dashboard claims OCR works.**

---

## 6. The live MCP profile — 16 servers

Read from `C:\Users\apviz\.minimax\mcp.json`, measured:

```
agent-browser-mcp      chrome-devtools-mcp     docker-mcp
gdrive-mcp             git-mcp                 gmail-mcp
google-calendar-mcp    google-workspace-mcp    hermes-mcp-router
mcp-server-filesystem  minimax-notebooklm      notebooklm-mcp
obsidian-mcp           qwen-acp-adapter        qwen-mcp-http
sentinel-hub
```

`sentinel-hub` is SENTINEL's own, verified by a real MCP handshake — **26 tools returned over the wire**,
and a probe call to `sentinel_confirm_identity` succeeded.

**Namespace note that matters for anyone continuing this:** MiniMax's tools and Hermes's tools are
separate universes. MiniMax's MCP servers, skills and connectors are not Hermes's. Duplication is the
correct answer when MiniMax needs something Hermes already has — two independent instances cannot
destroy each other. Any cross-link between them must be a designed artifact with named endpoints, never
implicit.

---

## 7. The wider Docker environment

63 containers are running. **SENTINEL uses exactly one.** The rest belong to other systems and were not
touched.

Visible in the environment, for orientation only: a Hermes MCP fleet (`hermes-mcp-*`), `minimax-hermes-bridge`
on `127.0.0.1:8801`, `minimax-antigravity-bridge` on `127.0.0.1:8802`, `mavis-optimus-control-center`
on `127.0.0.1:8901`, plus postgres, redis, vault, elasticsearch, prometheus, open-webui, searxng and
others.

**One boundary statement, measured and scoped:** `apviz-dashboard-monitor` publishes `0.0.0.0:9119` and
`[::]:9119`. It is **not part of SENTINEL**. SENTINEL's own front refused connection on all three
non-loopback adapter addresses. This project makes no claim about that container's exposure.

---

## 8. Startup anchor — measured

`%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\SENTINEL Command Center.bat`

| Property | Measured |
|---|---|
| Size | **4,557 bytes** |
| Line endings | **75 CRLF** — required; `cmd` mis-parses LF-only batch files |
| BOM | none |
| SHA256 | `4acc5bbc…` |
| Invokes | `sentinel-hub.ps1 -Action start` — brings up **both** planes |
| Log | `09_LOGS\hub-startup.log` |

---

## Dependency failure modes, and what happens when each fails

| If this fails | What the system does |
|---|---|
| Docker unavailable | tests report `NOT_RUN`, never `FAIL` — an absent engine has falsified nothing |
| Registry unreachable | npm check reports `NOT_RUN`, never `FAIL` |
| Playwright missing | browser check reports `NOT_RUN` |
| A collector cannot measure a surface | reports `NOT_AVAILABLE`, never a healthy default |
| Backend down | front reports `DEGRADED`, not `DOWN` |
| A scan truncates | reports "scan incomplete — UNVERIFIED", never clean |

**The pattern: an unmeasured thing is never reported as a working thing.** That is the single most
consistent property of this build.