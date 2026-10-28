# 01 — Structura SOT-ului (inventar masurat)

Masurat: **2026-10-28**, intre 19:05 si 19:20 (ora locala, +02:00).
Radacina SOT: `C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard`
Repo git: ramura `main`, remote `https://github.com/apvizual-max/OPTIMUS-Backbone.git`, HEAD `d286e6396e1599f9604d4b63f5e7e27d96fb88c3` ("SENTINEL: bytecode-ul si test_sentinel.md ies din urmarire").

Toate valorile de mai jos provin din comenzi rulate in aceasta sesiune. Fiecare comanda de reverificare este listata la final.

## 1. Continut de top-level

Masurat cu `Get-ChildItem -LiteralPath <SOT> -Force`:
**25 directoare + 27 fisiere = 52 intrari de top-level.**

### 1.1 Directoare

| Nume | Tip | Mod | Tinta (daca este reparse point) |
|---|---|---|---|
| `.git` | dir | d----- | — |
| `.Jules` | dir | d----- | — |
| `_DOCS` | dir | d----- | — |
| `_SYSTEM` | dir | d----- | — |
| `00_INDEX` | dir | d----- | — |
| `10_BRIDGES` | dir | d----- | — |
| `20_BRIDGES` | dir | d----- | — |
| `20_PROTOCOLS` | dir | d----- | — |
| `30_WORKFLOWS` | dir | d----- | — |
| `40_REGISTRIES` | dir | d----- | — |
| `50_TEMPLATES` | dir | d----- | — |
| `60_SKILLS` | dir | d----- | — |
| `70_CONNECTORS` | dir | d----- | — |
| `90_CONTROL_CENTER` | dir | d----- | — |
| `95_DESIGN_SOT` | dir | d----- | — |
| `backups` | dir | d----- | — |
| `handoff` | dir | d----- | — |
| `Mavis-Google_Access` | dir | d----- | — |
| `MINIMAX OPTIMUS CONTROL CENTER BLUEPRINT` | dir | d----- | — |
| `Optimus_CD (by Jules)` | **Junction** | d-r--l | `E:\Google\GDrive\GDrive-Second_Brain_PKMS\02_Areas\02-2-AI-SOT\CASA\OPTIMUS - Prime\Optimus_CD (by Jules)` |
| `Optimus_CI (by Mavis)` | dir | d----- | — |
| `scripts` | dir | d----- | — |
| `SENTINEL_PRIME` | dir | d----- | — |
| `sites` | dir | d----- | — |
| `tests` | dir | d----- | — |

### 1.2 Fisiere

| Nume | Tip | Mod | Octeti |
|---|---|---|---|
| `.gitignore` | file | -a---- | 8300 |
| `_gate_reply.txt` | file | -a---- | 2884 |
| `_gate_reply2.txt` | file | -a---- | 2180 |
| `_gate_reply3.txt` | file | -a---- | 4524 |
| `AGENTS.md` | file | -a---- | 10609 |
| `code_review_rules.md` | file | -a---- | 16013 |
| `find_test_gaps.py` | file | -a---- | 499 |
| `HERMES_DEFECT_relaunch_loop_venv_sync.md` | file | -a---- | 9324 |
| `JULES_HANDOFF.md` | file | -a---- | 4616 |
| `MAVIS_FULL_SYSTEMS_REPORT.md` | file | -a---- | 14976 |
| `memory_summary.md` | file | -a---- | 7658 |
| `minimax-h3-skills_assessment.md` | file | -a---- | 6997 |
| `OPTIMUS_CURRENT_STATE.md` | file | -a---- | 4635 |
| `OPTIMUS_INDEX.md` | file | -a---- | 5419 |
| `OPTIMUS_MINIMAX_HERMES_ANTIGRAVITY_INTEGRATION_REPORT.md` | file | -a---- | 12435 |
| `OPTIMUS_MINIMAX_INTEGRATION_GAP_REPORT.md` | file | -a---- | 23932 |
| `OPTIMUS_SYSTEM_TIMELINE.md` | file | -a---- | 12953 |
| `POPY_MiniMax_OPTIMUS_Status_Report-10-02-2026.md` | file | -a---- | 13451 |
| `pr_description.txt` | file | -a---- | 1406 |
| `ralph-loop.md` | file | -a---- | 3834 |
| `RAPORT DE STARE — OPTIMUS CONTROL CENTER - 2026-10-11 01-42.md` | file | -a---- | 5295 |
| `RAPORT DE STARE — SISTEMUL GIT GITHUB - 2026-10-11 18-58.md` | file | -a---- | 5147 |
| `README.md` | file | -a---- | 7172 |
| `README_SYSTEM_TOPOLOGY_AND_AGENT_GUIDELINES.md` | **SymbolicLink** | -a---l | 0 (link) → `C:\Antigravity - SYSTEM_TOPOLOGY - 3 Partition System\README_SYSTEM_TOPOLOGY_AND_AGENT_GUIDELINES.md` |
| `SENTINEL_OPERATIONAL_DOCTRINE.md` | file | -a---- | 27492 |
| `test_find_test_gaps.py` | file | -a---- | 777 |
| `verify_ui.py` | file | -a---- | 2243 |

## 2. Foldere de top-level urmarite de git, cu numarul de fisiere urmarite

Masurat cu `git -c core.quotepath=false ls-files` grupat pe primul segment de cale.
**Total fișiere urmărite in repo: 1777.** Suma pe directoare: 1751. Restul 26 sunt fisiere de top-level urmarite.

| Folder de top-level | Nr. de fisiere urmarite |
|---|---|
| `.Jules` | 3 |
| `_DOCS` | 19 |
| `_SYSTEM` | 4 |
| `00_INDEX` | 4 |
| `10_BRIDGES` | 9 |
| `20_BRIDGES` | 86 |
| `20_PROTOCOLS` | 40 |
| `30_WORKFLOWS` | 5 |
| `40_REGISTRIES` | 4 |
| `50_TEMPLATES` | 4 |
| `60_SKILLS` | 410 |
| `70_CONNECTORS` | 7 |
| `90_CONTROL_CENTER` | 17 |
| `95_DESIGN_SOT` | 5 |
| `handoff` | 9 |
| `Mavis-Google_Access` | 560 |
| `MINIMAX OPTIMUS CONTROL CENTER BLUEPRINT` | 37 |
| `Optimus_CI (by Mavis)` | 128 |
| `SENTINEL_PRIME` | 344 |
| `scripts` | 50 |
| `tests` | 6 |
| `backups` | 0 (ne-urmărit) |
| `Optimus_CD (by Jules)` | 0 (juncție către alt proiect) |
| `sites` | 0 (director gol) |
| `.git` | 0 (meta-date, ne-urmărite) |

Sub-descompunere masurată:
- `60_SKILLS/mavis-skills` = 409 fișiere urmarite; `60_SKILLS/60_skill_blueprints.md` = 1.
- `70_CONNECTORS` = 7 fișiere `.md` la top-level (niciun subfolder).
- `handoff` = 9 fișiere, toate în `handoff/_git_history/` (5 patch + 4 status) și `handoff/_runtime/processes-before-migration.json`.

## 3. Harta de reparse points (juncții și linkuri simbolice)

Enumerare completă cu `cmd /c dir /AL /S /B` plus rezolvarea țintelor prin `Get-Item`.

| Cale (relativ la SOT) | Tip | Țintă rezolvată | Ce este |
|---|---|---|---|
| `Optimus_CD (by Jules)` | Junction | `E:\Google\GDrive\GDrive-Second_Brain_PKMS\02_Areas\02-2-AI-SOT\CASA\OPTIMUS - Prime\Optimus_CD (by Jules)` | **Proiect diferit**, al lui Jules, pe volumul E:. Nu este urmărit de acest repo (0 fișiere). Ieșirea din SOT. |
| `60_SKILLS/_links/mavis-skills` | Junction | `C:\Users\apviz\.minimax\agents\mavis\skills` | **Registry-ul live de skill-uri** al runtime-ului Mavis. Face vizibilă din repo colecția live (93 skill-uri). |
| `scripts/_jtest` | Junction | `C:\Users\apviz\.minimax\agents\mavis\skills` | Artefact de test/probă (joncție spre același registry live). |
| `README_SYSTEM_TOPOLOGY_AND_AGENT_GUIDELINES.md` | SymbolicLink (fisier) | `C:\Antigravity - SYSTEM_TOPOLOGY - 3 Partition System\README_SYSTEM_TOPOLOGY_AND_AGENT_GUIDELINES.md` | Link simbolic cu **0 octeti** catre un fisier din afara SOT-ului. Nu este urmarit de git. |
| `backups/FULL_BACKUP_*` (11 intrari) | Junction | `D:\Backups_Archive\minimax_projects_backups\...` | Vezi sectiunea 4. |

### 3.1 Cele patru cai cerute in enunt — rezultat masurat

| Cale ceruta | Rezultat masurat |
|---|---|
| `projects\SENTINEL_PRIME` | **NU EXISTA** ca subfolder `projects\` in SOT (`Test-Path` → `False`). Exista `SENTINEL_PRIME` la radacina SOT-ului, dar este **director real** (`Mode=d-----`, `LinkType` gol), **nu** joncție. Contine motorul SENTINEL (01_FOUNDATION … 14_HANDOFF), inclusiv `07_BACKBONE\mcp\` (serverele MCP) si `13_COMMAND_CENTER\api\server.ps1`. 344 fișiere urmarite. |
| `projects\scripts\git-hooks` | **NU EXISTA** ca subfolder `projects\` (`Test-Path` → `False`). Exista `scripts\git-hooks` la radacina SOT-ului, dar este **director real** (`Mode=d-----`, `LinkType` gol), **nu** joncție. Contine un singur fisier: `pre-push` (2061 octeti) — hook-ul git de pre-push al proiectului. |
| `60_SKILLS\_links\mavis-skills` | **Junction** → `C:\Users\apviz\.minimax\agents\mavis\skills` (vezi mai sus). |
| `Optimus_CD (by Jules)` | **Junction** → proiectul lui Jules pe E: (vezi mai sus). |

### 3.2 Joncție externă relevantă pentru taskurile Windows

| Cale | Tip | Țintă |
|---|---|---|
| `C:\Users\apviz\AI_Tools` | Junction | `E:\Google\GDrive\GDrive-Second_Brain_PKMS\02_Areas\02-2-AI-SOT\CASA\OPTIMUS - Prime\AI_Tools` |

Subfolderul `C:\Users\apviz\AI_Tools\QWEN_Optimus_System_Dashboard` este un **director real** in interiorul acestei joncții (nu o joncție in Sine), pe volumul E:. In interiorul lui, `AI_Tools\qwen-system` este joncție → `E:\Google\GDrive\...\AI_Tools\QWEN_Optimus_System_Dashboard\qwen-system`.

## 4. Folderul `backups\`

Masurat cu `Get-ChildItem -LiteralPath <SOT>\backups -Force`. **15 intrari**: 11 joncții + 4 directoare reale.

| Intrare | Tip | Tinta | Nr. de elemente directe |
|---|---|---|---|
| `FULL_BACKUP_2026-10-03` | Junction | `D:\Backups_Archive\minimax_projects_backups\FULL_BACKUP_2026-10-03` | — |
| `FULL_BACKUP_2026-10-03_021532` | Junction | `D:\Backups_Archive\minimax_projects_backups\FULL_BACKUP_2026-10-03_021532` | — |
| `FULL_BACKUP_2026-10-03_FINAL` | Junction | `D:\Backups_Archive\minimax_projects_backups\FULL_BACKUP_2026-10-03_FINAL` | — |
| `FULL_BACKUP_2026-10-04` | Junction | `D:\Backups_Archive\minimax_projects_backups\FULL_BACKUP_2026-10-04` | — |
| `FULL_BACKUP_2026-10-04_QUARANTINE` | Junction | `D:\Backups_Archive\minimax_projects_backups\FULL_BACKUP_2026-10-04_QUARANTINE` | — |
| `FULL_BACKUP_2026-10-05_042054` | Junction | `D:\Backups_Archive\minimax_projects_backups\FULL_BACKUP_2026-10-05_042054` | — |
| `FULL_BACKUP_2026-10-05_100216` | Junction | `D:\Backups_Archive\minimax_projects_backups\FULL_BACKUP_2026-10-05_100216` | — |
| `FULL_BACKUP_2026-10-05_102017` | Junction | `D:\Backups_Archive\minimax_projects_backups\FULL_BACKUP_2026-10-05_102017` | — |
| `FULL_BACKUP_probe` | Junction | `D:\Backups_Archive\minimax_projects_backups\FULL_BACKUP_probe` | — |
| `FULL_BACKUP_probe2` | Junction | `D:\Backups_Archive\minimax_projects_backups\FULL_BACKUP_probe2` | — |
| `FULL_BACKUP_probe3` | Junction | `D:\Backups_Archive\minimax_projects_backups\FULL_BACKUP_probe3` | — |
| `VERSION_REFERINTA_2026-10-06` | dir | — | 2 elemente directe |
| `VERSION_REFERINTA_2026-10-06_DIPLOID` | dir | — | 3 elemente directe |
| `VERSION_REFERINTA_2026-10-07_DIGEST` | dir | — | 4 elemente directe |
| `_git_history` | dir | — | 5 fișiere (bundle-uri git) |

Detaliu `_git_history` (5 fișiere, masurate): `MAVIS-CLOUD.bundle` (1696785 b), `Mavis-Google_Access.bundle` (289838 b), `mavis-skills.bundle` (1165997 b), `Optimus_CI.bundle` (1716927 b), `SENTINEL_PRIME.bundle` (34695040 b).

Juncțiile din `backups\` sunt tot pe D: (arhivă externă, nu în SOT). Directorul `backups\` in sine are **0 fișiere urmarite** de git.

## 5. Note de stare

- `git status --porcelain=v1` la începutul sesiunii arăta deja: ` M SENTINEL_PRIME/08_SELF_IMPROVEMENT/test_sentinel.md` (modificare preexistentă) și fișiere neurmărite în `handoff/`. Modificarea `test_sentinel.md` este **anterioară** acestei sesiuni și nu a fost atinsă.
- `sites\` este un director **gol** (0 intrări).

## 6. Comenzi de reverificare

```powershell
Set-Location "C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard"
Get-ChildItem -Force | Select-Object Name, Mode, LinkType, Target
git -c core.quotepath=false ls-files | Measure-Object -Line
cmd /c "dir /AL /S /B"
Get-ChildItem -LiteralPath ".\backups" -Force | Select-Object Name, Mode, LinkType, Target
```
