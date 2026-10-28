# 04 — Dependente, porturi, taskuri Windows (inventar masurat)

Masurat: **2026-10-28**, intre 19:06 si 19:13 (ora locala, +02:00).

## 1. Porturi TCP in ascultare

Masurat cu `Get-NetTCPConnection -State Listen` (84 de ascultari in total pe masina).
Snapshot porturi: **19:13:14**.

### 1.1 Cele sase porturi cerute in enunt — verificate

| Port | Stare | PID ascultator | Proces | Ce serveste | Verificare suplimentara |
|---|---|---|---|---|---|
| **8766** | IN ASCULTARE | 32616 | `com.docker.backend.exe` | Container Docker `Google_Access` (imaginea `google-access:1.0.10`), mapat `127.0.0.1:8766->8766/tcp`, stare `Up (healthy)`. Este serverul MCP `Google_Access` din `mcp.json`. | TCP connect pe 127.0.0.1 → **True** |
| **8900** | IN ASCULTARE | 4 | `System` (HTTP.sys) | **OPTIMUS Control Center**. Servit de `90_CONTROL_CENTER\api\server.ps1 -Port 8900` (parametrul default `-Port 8900`, linia 44 a scriptului). Portul este inregistrat in HTTP.sys ca `HTTP://127.0.0.1:8900:127.0.0.1/` (vizibil in `netsh http show servicestate`), de aceea ascultatorul apare ca PID 4 / `System`, nu ca procesul PowerShell. | TCP connect → **True** |
| **8901** | **NU ASCULTA** | — | — | Port de referinta in matricea de supraveghere (`90_CONTROL_CENTER\api\collect-state.ps1`, lista `@(8082, 3001, 8765, 8801, 8802, 8900, 8901, 8910, 8912, 9412)`) si perechea-anchor in `health-harness.ps1` (`@('8900', $Base), @('8901', 'http://127.0.0.1:8901')`). **Nu a fost observat ascultand in niciunul dintre cele 4 snapshot-uri ale mele.** Niciun container Docker nu il mapeaza. | TCP connect → **False** |
| **8910** | IN ASCULTARE | 32616 | `com.docker.backend.exe` | Container Docker `mavis-sentinel-hub` (imaginea `mavis/sentinel-hub:1.0.0`), mapat `127.0.0.1:8910->80/tcp`, stare `Up (healthy)`. Reprezinta front-end-ul nginx al perechii SENTINEL (8910 = nginx, 8912 = planul de date PowerShell). | TCP connect → **True** |
| **8912** | IN ASCULTARE, **dar volatil** | 4 | `System` (HTTP.sys) | **SENTINEL Command Center** — `SENTINEL_PRIME\13_COMMAND_CENTER\api\server.ps1 -Port 8912 -NoBrowser` (parametrul default `-Port 8910` este in linia 40 a aceluiaasi script, dar se porneste explicit cu `-Port 8912`). | **Flapeaza:** in snapshot-ul de 19:08:29 `Get-NetTCPConnection` nu l-a gasit, iar probe-ul de TCP imediat urmator (imediat dupa 19:08:29) a dat **False**; la 19:13:14 asculta si connect **True**. Procesul PowerShell a fost observat cu PID-uri diferite la 19:07 (19300) si 19:13 (35432). Relansarea vine din ciclul `13_COMMAND_CENTER\api\collect-sentinel.ps1`. |
| **9412** | **NU ASCULTA** | — | — | Portul CDP (Chrome DevTools Protocol) propriu al serverului `minimax-notebooklm`. Constat in `Mavis-Google_Access\google-layer\minimax-notebooklm.js` (`const CDP_PORT = Number(process.env.MINIMAX_NOTEBOOKLM_CDP || 9412)`) si in `AGENTS.md`. **Niciun proces Chrome cu profilul `%LOCALAPPDATA%\minimax-notebooklm\chrome_profile` nu ruleaza la momentul masurarii** — din cele 59 de procese `chrome.exe`, profilele distincte sunt doar `C:\Users\apviz\.minimax\whatsapp\session-minimax-alex-v1` si `C:\Users\apviz\AppData\Local\Google\Chrome\User`. | TCP connect → **False** |

### 1.2 Alte porturi din aceeasi zona, masurate

| Port | PID | Proces | Ce serveste (masurat) |
|---|---|---|---|
| 8765 | 15424 | python.exe | `C:\Users\apviz\AppData\Roaming\uv\python\cpython-3.11-windows-x86_64-none\python.exe C:\Users\apviz\AppData\Local\hermes\desktop-plugins\honcho-command\backend\hc_backend.py` — backend-ul `HonchoCommand`. **Nu este proiectul SOT.** (Este si URL-ul serverului `qwen-mcp-http` din `mcp.json`.) |
| 8790 | 32616 | com.docker.backend.exe | Container Docker `Mavis-Optimus-CI` (imaginea `mavis/optimus-ci:1.0.0`), `127.0.0.1:8790->8790/tcp`, `Up (healthy)`. |
| 8801 | 32616 | com.docker.backend.exe | Container `minimax-hermes-bridge`, `127.0.0.1:8801->8801/tcp`. |
| 8802 | 32616 | com.docker.backend.exe | Container `minimax-antigravity-bridge`, `127.0.0.1:8802->8802/tcp`. |
| 8884 | 4 | System (HTTP.sys) | URL inregistrat in HTTP.sys: `HTTP://127.0.0.1:8884:127.0.0.1/`. |
| 8888 | 32616 | com.docker.backend.exe | Container `searxng`, `127.0.0.1:8888->8080/tcp`. |
| 3071 | 8252 | node.exe | `C:\Users\apviz\.minimax\whatsapp-mcp\bridge.js --port 3071` — endpointul `minimax-whatsapp` din `mcp.json` (`http://127.0.0.1:3071/mcp`). |
| 3001 | — | — | **NU ASCULTA.** Port din matricea de supraveghere a proiectului (`collect-state.ps1`), fara ascultator. |
| 80 | 8220 | node.exe | `C:\Users\apviz\.minimax\google-access\consent-watcher.mjs` — watcher de consimtamant Google, **din afara SOT-ului**. |
| 11434 | 14792 | ollama.exe | `C:\Users\apviz\AppData\Local\Programs\Ollama\ollama.exe serve` — Ollama, pornit de taskul `Ollama_Server` al SOT-ului (`scripts\start-ollama.ps1`). |

**Restul ascultarilor** (Docker: 3000, 4444, 5432, 6080, 6081, 6379, 7900, 8000, 8065, 8080, 8082, 8086, 8090, 8201, 8790, 8801, 8802, 8888, 9090, 9111, 9129, 9200, 9222, 9300, 9377, 9378, 9878, 20128, 12434; sistem: 135, 139, 445, 5040, 7679, 7680, 8884, 49664-49686, 50080, 50443, 51004, 51005, 59869; WSL: 3200) nu apartin proiectului OPTIMUS.

## 2. Runtime-urile de care depinde proiectul

| Runtime | Versiune masurata | Cale |
|---|---|---|
| node | `v26.5.1` | `C:\Program Files\nodejs\node.exe` |
| python (pe PATH) | `Python 3.14.6` | `C:\Users\apviz\AppData\Local\Microsoft\WindowsApps\python.exe` |
| py (launcher) | `Python 3.14.6` | `C:\Users\apviz\AppData\Local\Microsoft\WindowsApps\py.exe` |
| git | `git version 2.56.0.windows.4` | `C:\Program Files\Git\cmd\git.exe` |
| powershell | `5.1.26100.9711` (PSEdition: Desktop) | `C:\WINDOWS\System32\WindowsPowerShell\v1.0\powershell.exe` |
| bun | `1.2.10` | `C:\Program Files\Qwen\resources\bun\bun.exe` |
| python (interpreterul MCP al proiectului) | `Python 3.14.6` | `C:\Users\apviz\AppData\Local\Python\pythoncore-3.14-64\python.exe` |
| python (venv Hermes, folosit de `qwen-acp-adapter`) | `Python 3.11.15` | `C:\Users\apviz\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe` |
| python (uv, copil al `qwen-acp-adapter`) | `Python 3.11.15` | `C:\Users\apviz\AppData\Roaming\uv\python\cpython-3.11-windows-x86_64-none\python.exe` |

**NOT_MEASURED:** `pwsh` (PowerShell 7) — **nu este pe PATH**. Eroarea exacta: `The term 'pwsh' is not recognized as the name of a cmdlet, function, script file, or operable program.` Proiectul ruleaza exclusiv pe Windows PowerShell 5.1.

**NOT_MEASURED:** `bun` pe PATH — **nu este pe PATH**. Eroarea exacta: `The term 'bun' is not recognized as the name of a cmdlet, function, script file, or operable program.` Versiunea de mai sus a fost masurata prin cale absoluta.

## 3. Taskurile Windows care ating proiectul

Masurat cu `Get-ScheduledTask`. Total taskuri pe masina: **226**; **35** non-Microsoft (excluzand `\Microsoft\*`).

### 3.1 Taskuri care apointă la SOT — 3

| Task | Stare | Actiune | Trigger |
|---|---|---|---|
| `\Google_Access_Consent` | Ready | `powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\Mavis-Google_Access\scripts\ensure-consent-watcher.ps1"` | `MSFT_TaskTimeTrigger`, enabled=True, start `2026-10-28T01:02:25+02:00`, repetitie **PT5M** |
| `\Google_Access_Doctor` | Ready | `powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\Mavis-Google_Access\scripts\ga-doctor.ps1"` | `MSFT_TaskTimeTrigger`, enabled=True, start `2026-10-28T01:03:26+02:00`, repetitie **PT30M** |
| `\Ollama_Server` | Ready | `powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\scripts\start-ollama.ps1"` | `MSFT_TaskLogonTrigger`, enabled=True |

### 3.2 Taskuri care apointa la ALTE proiecte — 10

| Task | Stare | Actiune | Trigger | Proiect tinta |
|---|---|---|---|---|
| `\AgenticOS Heartbeat` | Ready | `node C:\Users\apviz\AI_Tools\QWEN_Optimus_System_Dashboard\core\heartbeat.js` | TimeTrigger, start `2026-10-07T17:31:00`, **PT5M** | QWEN Optimus System Dashboard (E:) |
| `\MavisExtendLMHeartbeat` | Ready | `powershell.exe ... -File "C:\Users\apviz\AI_Tools\QWEN_Optimus_System_Dashboard\Mavis-Google_Access\scripts\extendlm-heartbeat.ps1"` | TimeTrigger, start `2026-10-27T13:43:14+02:00`, **PT30M** | QWEN Optimus System Dashboard (E:) |
| `\MavisPickerHeartbeat` | Ready | `powershell.exe ... -File "C:\Users\apviz\AI_Tools\QWEN_Optimus_System_Dashboard\Mavis-Google_Access\scripts\picker-heartbeat.ps1"` | TimeTrigger, start `2026-10-28T00:48:33+02:00`, **PT15M** | QWEN Optimus System Dashboard (E:) |
| `\OPTIMUS_ControlCenter` | **Running** | `powershell.exe ... -WindowStyle Hidden -File "C:\Users\apviz\AI_Tools\QWEN_Optimus_System_Dashboard\scripts\cc-watchdog.ps1"` | LogonTrigger | QWEN Optimus System Dashboard (E:) |
| `\OPTIMUS_SentinelGuardian` | Ready | `powershell.exe ... -WindowStyle Hidden -File "C:\Users\apviz\AI_Tools\QWEN_Optimus_System_Dashboard\scripts\sentinel-guardian.ps1"` | LogonTrigger | QWEN Optimus System Dashboard (E:) |
| `\OPTIMUS_WeeklyDigest` | Ready | `powershell.exe ... -WindowStyle Hidden -File "C:\Users\apviz\AI_Tools\QWEN_Optimus_System_Dashboard\scripts\weekly-digest.ps1"` | WeeklyTrigger, start `2026-10-07T07:10:00+02:00` | QWEN Optimus System Dashboard (E:) |
| `\QwenSystemRootGuardian` | Ready | `C:\Users\apviz\AI_Tools\QWEN_Optimus_System_Dashboard\qwen-system\scripts\root-guardian.cmd` | TimeTrigger, start `2026-10-03T05:53:00`, **PT2M** | QWEN Optimus System Dashboard (E:) |
| `\QwenSystem Weekly Backup` | Ready | `powershell.exe ... -File "C:\Users\apviz\AI_Tools\QWEN_Optimus_System_Dashboard\qwen-system\scripts\weekly-backup.ps1"` | WeeklyTrigger, start `2026-09-20T02:00:00+02:00` | QWEN Optimus System Dashboard (E:) |
| `\QwenWeeklyBackup` | **Disabled** | `powershell.exe ... -File "C:\Users\apviz\AI_Tools\QWEN_Optimus_System_Dashboard\qwen-system\scripts\weekly-backup.ps1"` | WeeklyTrigger, start `2026-09-21T02:00:00+02:00` | QWEN Optimus System Dashboard (E:) |
| `\MavisSyncBridge` | Ready | `powershell.exe ... -File "E:\Google\GDrive\GDrive-Second_Brain_PKMS\02_Areas\02-2-AI-SOT\CASA\OPTIMUS - Prime\Optimus_CI (by Mavis)\scripts\run-sync-logged.ps1"` (WD = acelasi folder) | DailyTrigger, start `2026-10-12T07:30:00+02:00` | Optimus_CI (E:) — proiect separat |

### 3.3 Taskuri adiacente (nu apointa in SOT, dar relevantae pentru lant)

| Task | Stare | Actiune | Observatie |
|---|---|---|---|
| `\Google_Access_Watch` | Ready | `powershell.exe ... -File "C:\Users\apviz\.minimax\google-access\watch-reauth.ps1"` | TimeTrigger PT1H — **in afara SOT-ului** (`C:\Users\apviz\.minimax\google-access`), desi se ocupa de aceeasi functionalitate Google Access ca taskurile SOT. |
| `\Antigravity_Jules_GitHub_Continuous_Sync` | Ready | `wscript.exe "...\Antigravity_Folder\Antigravity_Projects\Optimus_CD (by Jules)\scripts\start_sovereign_sync_silent.vbs"` | DailyTrigger — **Optimus_CD**, alt proiect |
| `\JulesDailyLoop` | Ready | `powershell.exe ... -File "...\Optimus_CD (by Jules)\scripts\run-jules-daily-logged.ps1"` | DailyTrigger — **Optimus_CD**, alt proiect |
| `\QwenMcpFilesystemBridge` | Disabled | `C:\Users\apviz\AppData\Local\hermes\node\node.exe "C:\Users\apviz\AI_Tools\mcp-filesystem-sse-bridge.js"` | LogonTrigger, dezactivat |

**Observatie de frontiera:** `C:\Users\apviz\AI_Tools` este o **juncție** → `E:\Google\GDrive\GDrive-Second_Brain_PKMS\02_Areas\02-2-AI-SOT\CASA\OPTIMUS - Prime\AI_Tools` (masurat cu `Get-Item`). Prin urmare, **taskurile din 3.2 ruleaza proiectul de pe E:, nu SOT-ul** — chiar daca unele folosesc aceleasi nume de script (`cc-watchdog.ps1`, `sentinel-guardian.ps1`, `weekly-digest.ps1`), care exista si in `SOT\scripts\`. SOT-ul are copiile proprii ale acestor scripturi, dar **nu are taskuri Windows care sa le porneasca**.

## 4. Executabile invocate din afara proiectului

| Executabil | Cale | Versiune | Folosit de |
|---|---|---|---|
| `node.exe` | `C:\Program Files\nodejs\node.exe` | v26.5.1 | `minimax-notebooklm` (mcp), `optimus-ci-server` (mcp), `docker-mcp`, `google-calendar-mcp`, `whatsapp-mcp/bridge.js` |
| `bun.exe` | `C:\Program Files\Qwen\resources\bun\bun.exe` | 1.2.10 | `gdrive-mcp`, `gmail-mcp`, `google-workspace-mcp` (toate stdio din `mcp.json`) |
| `python.exe` | `C:\Users\apviz\AppData\Local\Python\pythoncore-3.14-64\python.exe` | Python 3.14.6 | `sentinel-hub`, `prime-bridge`, `web-tools`, `git-tools` (toate stdio din `mcp.json`) |
| `python.exe` | `C:\Users\apviz\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe` | Python 3.11.15 | `qwen-acp-adapter` (mcp.json) |
| `python.exe` | `C:\Users\apviz\AppData\Roaming\uv\python\cpython-3.11-windows-x86_64-none\python.exe` | Python 3.11.15 | copil al lui `qwen-acp-adapter`; backend `HonchoCommand` pe portul 8765 |
| `python.exe` | `C:\Users\apviz\AppData\Local\Microsoft\WindowsApps\python.exe` | Python 3.14.6 | `SENTINEL_PRIME\08_SELF_IMPROVEMENT\monitor.py` |
| `hermes.exe` | `C:\Users\apviz\AppData\Local\hermes\hermes-agent\venv\Scripts\hermes.exe` | NOT_MEASURED (nu rulea la masurare) | `hermes-mcp-router` (mcp.json) |
| `chrome.exe` | `C:\Program Files\Google\Chrome\Application\chrome.exe` | masurat: exista pe disc; versiunea **NOT_MEASURED** (executia a deschis o sesiune de browser existenta in loc sa tipareasca versiunea) | profilul CDP `minimax-notebooklm` pe portul 9412 (nedorit in momentul masurarii) |
| `powershell.exe` | `C:\WINDOWS\System32\WindowsPowerShell\v1.0\powershell.exe` | 5.1.26100.9711 | serverele HTTP (8900, 8912), watchdogs, taskuri Windows |

**Chrome — precizare:** `chrome.exe --version` a returnat `Opening in existing browser session.` in loc de un numar de versiune, deci **versiunea Chrome este NOT_MEASURED**. Calea a fost confirmata ca existenta (`Test-Path` → True) si este folosita de Google Access ca profil CDP propriu.

## 5. Comenzi de reverificare

```powershell
Get-NetTCPConnection -State Listen | Sort-Object LocalPort
Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*Mavis-Optimus-Dashboard*' } | Select-Object ProcessId, ParentProcessId, Name, CommandLine
node --version; python --version; git --version; $PSVersionTable.PSVersion
Get-ScheduledTask | Where-Object { $_.TaskPath -notlike '\Microsoft\*' } | ForEach-Object {
  $_.TaskName; $_.State; $_.Actions.Execute; $_.Actions.Arguments; $_.Triggers.CimClass.CimClassName; $_.Triggers.Repetition.Interval
}
Get-Item "C:\Users\apviz\AI_Tools" -Force | Select-Object FullName, LinkType, Target
```
