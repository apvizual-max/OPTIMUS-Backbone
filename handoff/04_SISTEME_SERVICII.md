# Sisteme, servicii, daemoni — ce rulează și cine îl veghează

Măsurat 2026-10-28. Porturile sunt din
`handoff/_inventory/04_DEPENDENCIES_PORTS.md`; aici e semantica.

---

## 1. Cele două console

| | Control Center OPTIMUS | SENTINEL Command Center |
|---|---|---|
| port | **8900** | **8912** |
| server | `90_CONTROL_CENTER\api\server.ps1` | `SENTINEL_PRIME\13_COMMAND_CENTER\api\server.ps1` |
| launcher | `90_CONTROL_CENTER\bat\cc.bat` / `start-dashboard.bat` | `SENTINEL_PRIME\13_COMMAND_CENTER\api\sentinel-cc.ps1` |
| supraveghetor | `scripts\cc-watchdog.ps1` | `scripts\sentinel-guardian.ps1` |
| API | `/api/state`, `/api/health`, `/api/action` | `/api/health`, `/api/state` |
| stare măsurată | HTTP 200, 176.529 octeți | HTTP 200, 21.144 octeți |

`/api/state` produce măsurători la fiecare ~40 s și scrie
`90_CONTROL_CENTER\api\live-state.json` (ignorat de git — e runtime, nu
conținut).

**Observație esențială despre porturi:** serverele folosesc `HttpListener`, deci
socketul de ascultare e deținut de **pid 4 (System)**, nu de procesul
PowerShell. Orice heuristic de tip „cine deține portul 8900" care folosește
`Get-NetTCPConnection` întoarce System — și cine acționează pe baza asta
oprește toate serverele de pe mașină. De aceea `sentinel-cc.ps1` caută
procesul după **calea scriptului**, nu după port.

## 2. Lanțul de supraveghere

```
[Windows Task]  OPTIMUS_ControlCenter ──► QWEN\scripts\cc-watchdog.ps1
                                             (supervizeaza arborele QWEN)

[Windows Task]  OPTIMUS_SentinelGuardian ──► QWEN\scripts\sentinel-guardian.ps1
                                             (supervizeaza arborele QWEN)

[manual, la sesiune]  SOT\scripts\cc-watchdog.ps1 ──► server 8900 (SOT)
[manual, la sesiune]  SOT\scripts\sentinel-guardian.ps1 ──► server 8912 (SENTINEL)
```

### 2.1 Defect real, măsurat: SOT-ul nu are supraveghere la logon

Taskurile `OPTIMUS_ControlCenter` și `OPTIMUS_SentinelGuardian` rulează
scripturile din **`C:\Users\apviz\AI_Tools\QWEN_Optimus_System_Dashboard`** —
un junction spre un **alt proiect** (pe `E:`). Copiile alea au `$Root` =
arborele QWEN, deci supervizează **serviciile QWEN**, nu ale SOT-ului.

Procesele SOT-ului (8900, 8912) rulează deocamdată doar pentru că au fost
pornite manual în această sesiune. **La următoarea deconectare, SOT-ul ar
rămâne fără supraveghere.**

Corectia: două taskuri noi, cu nume distincte, care pornesc **copiile din
SOT**: `OPTIMUS_ControlCenter_SOT` și `OPTIMUS_SentinelGuardian_SOT`. Cele
QWEN rămân neatinse — sunt ale altui proiect.

**Neaplicat, pentru că cere privilegii administrative.** Măsurat: atât
`Register-ScheduledTask`, cât și `schtasks /create` au răspuns
„Access is denied" (exit 1). Comanda exactă e în `07_DECIZII_DESCHISE.md`
(D10) — o singură rulare ca administrator închide lacuna.

### 2.2 Gardianul SENTINEL — îngust, cu re-verificare înainte de kill

`sentinel-guardian.ps1` se identifică după tokenul
`SENTINEL_PRIME\13_COMMAND_CENTER\api\server.ps1` și **nu** după
`server.ps1` — pentru că și Control Center-ul rulează un `server.ps1`, iar un
gardian cu pattern prea larg ar omorî console-ul pe care ar trebui să-l
protejeze. Înainte de orice `Stop-Process`, tabelul de procese e reconstruit
**imediat** și tokenul e re-verificat pe procesul însuși.

Sănătatea e măsurată cu un `GET /api/health` real, nu cu „portul e deschis".

## 3. Daemonii SENTINEL

| Daemon | Script | Ce face |
|---|---|---|
| monitor de self-improvement | `08_SELF_IMPROVEMENT\monitor.py --write` | scrie lecții, evoluție, `test_sentinel.md` |
| collector de stare | `13_COMMAND_CENTER\api\collect-sentinel.ps1` | adună starea sistemului |
| handshake MCP | `08_SELF_IMPROVEMENT\mcp_handshake.py` | verifică serverele MCP |

**Atenție:** motorul de self-improvement **scrie în propriile fișiere sursă**
(`test_suite.py`, `test_sentinel.md`, `11_BRAIN\04_METHOD\MISSTEPS_AND_CORRECTIONS.md`,
`13_COMMAND_CENTER\EVOLUTION.md`). Măsurat: rescrie `test_suite.py` la fiecare
ciclu. De aceea acele două fișiere au fost scoase din urmărire — altfel arborele
nu poate sta curent. Restul modificărilor motorului sunt **conținut real** și
se comit.

## 4. Serverele MCP care trăiesc în SOT

Nouă servere din `C:\Users\apviz\.minimax\mcp.json` indică înăuntrul SOT-ului
(vezi `_inventory/03_CONNECTORS_MCP.md`):

`minimax-notebooklm`, `gdrive-mcp`, `gmail-mcp`, `google-calendar-mcp`,
`qwen-acp-adapter`, `sentinel-hub`, `prime-bridge`, `web-tools`, `git-tools`.

Serverele care indică **în afara** SOT-ului nu au fost atinse: `hermes-mcp-router`
(spațiul Hermes), `qwen-mcp-http`, `docker-mcp`, `git-mcp`, `obsidian-mcp`,
`notebooklm-mcp`, `chrome-devtools-mcp`, `agent-browser-mcp`,
`mcp-server-filesystem`, `google-workspace-mcp`, `minimax-whatsapp`,
`Google_Access`, `optimus-ci-server`.

**Regula de namespace:** minimax ≠ Hermes. Serverele Hermes
(`hermes-mcp-router`, `qwen-acp-adapter` folosesc venv-ul Hermes) rămân
acolo unde sunt; folderele `70_CONNECTORS/_links/`, `scripts/external/` și
`scripts/hermes-custom/` nu intră în istoria acestui repo.

## 5. Ce rulează pe lângă SOT

- `8766` — `Google_Access` (MCP streamable-http), în Docker.
- `8765` — `qwen-mcp-http`.
- `8910` — `mavis-sentinel-hub` (container Docker), în fața backendului SENTINEL.
- Porturi Docker: 8790, 8801, 8802, 8884, 8888, 9090, 9111, 9129, 9200.

**Riscul măsurat pe 8900:** watchdog-ul din arborele QWEN și cel din SOT
supervizează **același port, 8900**. Cine pornește primul când serverul cade
câștigă portul — și atunci dashboardul servit poate fi celălalt, nu al SOT-ului.
Watchdog-ul QWEN nu omoară servere străine (`Stop-Stale` e restrâns la propriul
server), deci nu distruge nimic, dar poate „câștiga" portul. **De rezolvat:
supraveghetorul SOT-ului trebuie să verifice că serverul care răspunde pe 8900
e al lui**, nu doar că portul răspunde.

## 6. Curățenie și housekeeping

`%TEMP%` conține în continuare **111.417 de fișiere** (318,5 MB). Control
Center-ul nu mai depinde de `GetTempFileName` (helper cu GUID), deci nu e
blocant, dar e un rest de igienă: ștergerea în masă e blocată de politica
instrumente (`mavis-trash` pe 111k de fișiere e nepractic).
