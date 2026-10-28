# 03 — Conectori, servere MCP si procesele care le servesc (inventar masurat)

Masurat: **2026-10-28**, intre 19:07 si 19:13 (ora locala, +02:00).
Sursa registru: `C:\Users\apviz\.minimax\mcp.json` (parsat cu `ConvertFrom-Json`).

## 1. Serverele MCP inregistrate

**Numar total de servere inregistrate: 22.**
Legenda: *In SOT?* = da daca **comanda sau primul argument** al serverului indica o cale din `C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard`.

| # | Nume | Transport | Comanda / URL | Argument relevant | In SOT? | Calea exista? | enabled |
|---|---|---|---|---|---|---|---|
| 1 | `hermes-mcp-router` | stdio | `C:\Users\apviz\AppData\Local\hermes\hermes-agent\venv\Scripts\hermes.exe` | `mcp serve` | nu | da | true |
| 2 | `qwen-mcp-http` | http | `http://localhost:8765/mcp` | — | nu | n/a (URL) | true |
| 3 | `docker-mcp` | stdio | `node` | `C:\Users\apviz\AppData\Roaming\npm\node_modules\mcp-docker\build\index.js` | nu | da | true |
| 4 | `git-mcp` | stdio | `C:\Users\apviz\AppData\Roaming\npm\mcp-git.cmd` | — | nu | da | true |
| 5 | `obsidian-mcp` | stdio | `C:\Users\apviz\AppData\Roaming\npm\mcp-obsidian.cmd` | — | nu | da | true |
| 6 | `notebooklm-mcp` | stdio | `C:\Users\apviz\AppData\Roaming\npm\notebooklm-mcp.cmd` | — | nu | da | true |
| 7 | `minimax-notebooklm` | stdio | `C:\Program Files\nodejs\node.exe` | `...Mavis-Optimus-Dashboard\Mavis-Google_Access\google-layer\minimax-notebooklm.js` | **DA** | da | true |
| 8 | `chrome-devtools-mcp` | stdio | `C:\Users\apviz\AppData\Roaming\npm\chrome-devtools-mcp.cmd` | — | nu | da | true |
| 9 | `agent-browser-mcp` | stdio | `C:\Users\apviz\AppData\Roaming\npm\agent-browser-mcp-server.cmd` | — | nu | da | true |
| 10 | `mcp-server-filesystem` | stdio | `C:\Users\apviz\AppData\Roaming\npm\mcp-server-filesystem.cmd` | — | nu | da | true |
| 11 | `gdrive-mcp` | stdio | `C:\Program Files\Qwen\resources\bun\bun.exe` | `...Mavis-Optimus-Dashboard\Mavis-Google_Access\google-layer\gdrive-launcher.js` | **DA** | da | true |
| 12 | `gmail-mcp` | stdio | `C:\Program Files\Qwen\resources\bun\bun.exe` | `...Mavis-Optimus-Dashboard\Mavis-Google_Access\google-layer\gmail-launcher.js` | **DA** | da | true |
| 13 | `google-workspace-mcp` | stdio | `C:\Program Files\Qwen\resources\bun\bun.exe` | `C:\Users\apviz\AppData\Roaming\npm\node_modules\google-workspace-mcp\dist\cli.js serve --read-only` | nu | da | true |
| 14 | `google-calendar-mcp` | stdio | `node` | `...Mavis-Optimus-Dashboard\Mavis-Google_Access\google-layer\calendar-launcher.js` | **DA** | da | **false** (dezactivat) |
| 15 | `qwen-acp-adapter` | stdio | `C:\Users\apviz\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe` | `...Mavis-Optimus-Dashboard\scripts\qwen_acp_mcp.py` | **DA** | da | true |
| 16 | `sentinel-hub` | stdio | `C:\Users\apviz\AppData\Local\Python\pythoncore-3.14-64\python.exe` | `...Mavis-Optimus-Dashboard\SENTINEL_PRIME\07_BACKBONE\mcp\sentinel_hub_server.py` | **DA** | da | true |
| 17 | `minimax-whatsapp` | streamable-http | `http://127.0.0.1:3071/mcp` | — | nu | n/a (URL) | true |
| 18 | `prime-bridge` | stdio | `C:\Users\apviz\AppData\Local\Python\pythoncore-3.14-64\python.exe` | `...Mavis-Optimus-Dashboard\SENTINEL_PRIME\07_BACKBONE\mcp\prime_bridge_server.py` | **DA** | da | true |
| 19 | `web-tools` | stdio | `C:\Users\apviz\AppData\Local\Python\pythoncore-3.14-64\python.exe` | `...Mavis-Optimus-Dashboard\SENTINEL_PRIME\07_BACKBONE\mcp\web_tools_server.py` | **DA** | da | true |
| 20 | `git-tools` | stdio | `C:\Users\apviz\AppData\Local\Python\pythoncore-3.14-64\python.exe` | `...Mavis-Optimus-Dashboard\SENTINEL_PRIME\07_BACKBONE\mcp\git_tools_server.py` | **DA** | da | true |
| 21 | `Google_Access` | streamable-http | `http://127.0.0.1:8766/mcp` | — | nu (container Docker) | n/a (URL) | true |
| 22 | `optimus-ci-server` | stdio | `node` | `C:\Users\apviz\.minimax\skills\optimus-ci-server\bin\optimus-ci-mcp.mjs` | nu | da | true |

**Rezumat: 9 intreri din 22 apointă direct în SOT** (nr. 7, 11, 12, 14, 15, 16, 18, 19, 20), **dintre care 8 sunt active** (`enabled: true`) si 1 este dezactivata (`google-calendar-mcp`, nr. 14). Cele 13 intreri restante folosesc binare sau pachete npm din afara SOT-ului, sau sunt endpoint-uri HTTP.

**Transporturi masurate:** 19 × `stdio`, 1 × `http` (`qwen-mcp-http`), 2 × `streamable-http` (`minimax-whatsapp`, `Google_Access`).

### 1.1 Variabile de mediu (`env`) din registru

| Cheie | Valoare | Server | Unde se foloseste |
|---|---|---|---|
| `PRIME_HOME` | `C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\SENTINEL_PRIME` | `prime-bridge` | Rădăcina workspace-ului SENTINEL; **în SOT** |
| `WORKSPACE_ROOT` | `C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\SENTINEL_PRIME` | `git-tools` | Rădăcina permisă pentru operațiile git; **în SOT** |
| `PYTHONIOENCODING` | `utf-8` | `prime-bridge`, `web-tools`, `git-tools` | — |
| `HOME` | `C:\Users\apviz` | `google-workspace-mcp` | — |

`PRIME_HOME` si `WORKSPACE_ROOT` au **aceeași valoare**: amândoi indică `SENTINEL_PRIME` din SOT.

## 2. Folderul `70_CONNECTORS\` din repo

Masurat cu `Get-ChildItem -LiteralPath <SOT>\70_CONNECTORS -Force`.
**7 intrari, toate fisiere `.md` la top-level; niciun subfolder.**

| Intrare | Tip | Nr. de fisiere | Octeti |
|---|---|---|---|
| `70_connector_blueprints.md` | file | 1 | 4336 |
| `70_docker_fleet_inventory.md` | file | 1 | 7967 |
| `70_mcp_mirror_plan.md` | file | 1 | 13993 |
| `70_obsidian_karpathy_audit.md` | file | 1 | 10845 |
| `70_personal_skill_index.md` | file | 1 | 306813 |
| `70_plugin_universe_survey.md` | file | 1 | 9892 |
| `70_sentinel_role_ai_inventory.md` | file | 1 | 8534 |

## 3. Folderul `SENTINEL_PRIME\07_BACKBONE\mcp\`

Masurat cu `Get-ChildItem -LiteralPath <SOT>\SENTINEL_PRIME\07_BACKBONE\mcp -Force`.

### 3.1 Fiecare fisier `.py` de server, cu dimensiunea

**9 fisiere `.py`:**

| Fisier | Octeti | In registru `mcp.json`? |
|---|---|---|
| `sentinel_hub_server.py` | 46277 | da — `sentinel-hub` |
| `git_tools_server.py` | 16070 | da — `git-tools` |
| `web_tools_server.py` | 11382 | da — `web-tools` |
| `prime_bridge_server.py` | 8336 | da — `prime-bridge` |
| `sentinel_mcp_slice.py` | 3575 | nu |
| `learning_loop_server.py` | 1225 | nu |
| `sentinel_state_server.py` | 1184 | nu |
| `rule_triggers_server.py` | 1212 | nu |
| `context_pressure_server.py` | 1143 | nu |

### 3.2 Restul intrarilor din acelasi folder

| Intrare | Tip | Octeti |
|---|---|---|
| `OPTIMUS_MCP_CONFIG.json` | file | 15076 |
| `OPTIMUS_MCP_CONFIG.json.bak` | file | 6842 |
| `OPTIMUS_MCP_CONFIG.json.bak-20261028_1142` | file | 14601 |
| `OPTIMUS_MCP_CONFIG.json.bak2` | file | 12339 |
| `git_tools_server.py.bak` | file | 13959 |
| `git_tools_server.py.bak-20261028_0900` | file | 16067 |
| `prime_bridge_server.py.bak` | file | 7154 |
| `sentinel_hub_server.py.bak` | file | 38919 |
| `sentinel_hub_server.py.bak-20261028_1041` | file | 44268 |
| `sentinel_hub_server.py.bak-20261028_1142` | file | 46252 |
| `web_tools_server.py.bak` | file | 10415 |
| `__pycache__` | dir | — |

## 4. Procesele care servesc acum serverele MCP

Masurat cu `Get-CimInstance Win32_Process`, filtrat pe calea SOT. **Snapshot: 2026-10-28 19:13:02 (local).**
**13 procese cu linia de comanda in SOT**, dintre care **9 servesc serverele MCP din `mcp.json`**.

### 4.1 Servere MCP pornite din SOT (din `mcp.json`)

| PID | PPID | Proces | Linie de comanda | Server mcp.json |
|---|---|---|---|---|
| 29516 | 41800 | python.exe | `C:\Users\apviz\AppData\Local\Python\pythoncore-3.14-64\python.exe ...\SENTINEL_PRIME\07_BACKBONE\mcp\sentinel_hub_server.py` | `sentinel-hub` |
| 17384 | 41800 | python.exe | `C:\Users\apviz\AppData\Local\Python\pythoncore-3.14-64\python.exe ...\SENTINEL_PRIME\07_BACKBONE\mcp\git_tools_server.py` | `git-tools` |
| 39312 | 41800 | python.exe | `C:\Users\apviz\AppData\Local\Python\pythoncore-3.14-64\python.exe ...\SENTINEL_PRIME\07_BACKBONE\mcp\web_tools_server.py` | `web-tools` |
| 4112 | 41800 | python.exe | `C:\Users\apviz\AppData\Local\Python\pythoncore-3.14-64\python.exe ...\SENTINEL_PRIME\07_BACKBONE\mcp\prime_bridge_server.py` | `prime-bridge` |
| 41732 | 41800 | python.exe | `C:\Users\apviz\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe ...\scripts\qwen_acp_mcp.py` | `qwen-acp-adapter` |
| 21312 | 41732 | python.exe | `C:\Users\apviz\AppData\Roaming\uv\python\cpython-3.11-windows-x86_64-none\python.exe  ...\scripts\qwen_acp_mcp.py` | copil al lui `qwen-acp-adapter` |
| 9856 | 41800 | node.exe | `"C:\Program Files\nodejs\node.exe" ...\Mavis-Google_Access\google-layer\minimax-notebooklm.js` | `minimax-notebooklm` |
| 41836 | 41800 | bun.exe | `"C:\Program Files\Qwen\resources\bun\bun.exe" ...\Mavis-Google_Access\google-layer\gdrive-launcher.js` | `gdrive-mcp` |
| 41648 | 41800 | bun.exe | `"C:\Program Files\Qwen\resources\bun\bun.exe" ...\Mavis-Google_Access\google-layer\gmail-launcher.js` | `gmail-mcp` |

**Observatie:** PID-urile 4112, 17384, 29516, 39312, 9856, 41648, 41732, 41836 au parintele **41800** (host-ul Mavis), deci sunt servere stdio **per-sesiune**, nu daemoni permanenti. PID-urile se schimba intre sesiuni; pentru o stare curenta re-masurati.

### 4.2 Alte procese din SOT care nu sunt servere MCP

| PID | PPID | Proces | Scop |
|---|---|---|---|
| 35432 | 35784 | powershell.exe | `SENTINEL_PRIME\13_COMMAND_CENTER\api\server.ps1 -Port 8912 -NoBrowser` (planul de date SENTINEL) |
| 42760 | 11332 | powershell.exe | `SENTINEL_PRIME\13_COMMAND_CENTER\api\collect-sentinel.ps1 -Quiet` (colector) |
| 20812 | 42760 | python.exe | `SENTINEL_PRIME\08_SELF_IMPROVEMENT\monitor.py --write` |
| 34544 | 20812 | python.exe | `SENTINEL_PRIME\08_SELF_IMPROVEMENT\monitor.py --write` (copil) |

### 4.3 Servere MCP din registru care ruleaza, dar din AFARA SOT-ului

| PID | Proces | Comanda | Server |
|---|---|---|---|
| 34212 | cmd.exe | `C:\Users\apviz\AppData\Roaming\npm\mcp-git.cmd` | `git-mcp` |
| 18348 | cmd.exe | `C:\Users\apviz\AppData\Roaming\npm\notebooklm-mcp.cmd` | `notebooklm-mcp` |
| 12036 | cmd.exe | `C:\Users\apviz\AppData\Roaming\npm\chrome-devtools-mcp.cmd` | `chrome-devtools-mcp` |
| 36092 | cmd.exe | `C:\Users\apviz\AppData\Roaming\npm\agent-browser-mcp-server.cmd` | `agent-browser-mcp` |
| 15964 | cmd.exe | `C:\Users\apviz\AppData\Roaming\npm\mcp-server-filesystem.cmd` | `mcp-server-filesystem` |
| 35748 | node.exe | `node C:\Users\apviz\AppData\Roaming\npm\node_modules\mcp-docker\build\index.js` | `docker-mcp` |
| 32460 | bun.exe | `"C:\Program Files\Qwen\resources\bun\bun.exe" C:\Users\apviz\AppData\Roaming\npm\node_modules\google-workspace-mcp\dist\cli.js serve --read-only` | `google-workspace-mcp` |
| 41740 | node.exe | `node C:\Users\apviz\.minimax\skills\optimus-ci-server\bin\optimus-ci-mcp.mjs` | `optimus-ci-server` |
| 8252 | node.exe | `"C:\Program Files\nodejs\node.exe" C:\Users\apviz\.minimax\whatsapp-mcp\bridge.js --port 3071 --session C:\Users\apviz\.minimax\whatsapp\session` | `minimax-whatsapp` (HTTP) |

**Nu ruleau la momentul masurarii:** `hermes-mcp-router` (`hermes.exe`), `obsidian-mcp` (`mcp-obsidian.cmd`), `google-calendar-mcp` (dezactivat), `qwen-mcp-http` (endpoint HTTP, procesul apartine altui stack).

### 4.4 Note de volatilitate

La 19:07 existau si procesele `scripts\cc-watchdog.ps1` (PID 58804), `scripts\sentinel-guardian.ps1` (PID 49860), `90_CONTROL_CENTER\api\server.ps1 -Port 8900` (PID 57464) si `90_CONTROL_CENTER\api\collect-state.ps1` (PID 11620) — la 19:08:29 acestea erau deja **gone** (verificat cu `Get-CimInstance Win32_Process -Filter "ProcessId=..."` → PID inexistent). Supravietuitorii sunt relansati de watchdogs; PID-urile trebuie re-masurate la preluare.

## 5. Comenzi de reverificare

```powershell
$j = Get-Content "C:\Users\apviz\.minimax\mcp.json" -Raw | ConvertFrom-Json
$j.mcpServers.PSObject.Properties | ForEach-Object {
  [pscustomobject]@{ Name=$_.Name; Type=$_.Value.type; Cmd=$_.Value.command; Url=$_.Value.url; Env=($_.Value.env | ConvertTo-Json -Compress) }
}
Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*Mavis-Optimus-Dashboard*' } | Select-Object ProcessId, ParentProcessId, Name, CommandLine
```
