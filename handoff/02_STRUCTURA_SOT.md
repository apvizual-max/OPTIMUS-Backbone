# Structura SOT-ului — hartă, oglinzi și junction-uri

Măsurat 2026-10-28. Rădăcina (SOT):
`C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard`

---

## 1. Vocabularul: trei lucruri diferite care se confundă ușor

| Termen | Ce înseamnă aici | Unde stă |
|---|---|---|
| **canonic** | conținutul urmărit de git, în acest repo | `SOT\...` |
| **operational** | copia pe care rulează procesele acum | la calea originală, în afara SOT-ului |
| **oglindă (mirror)** | legătură de pe disk, ca un `ln -s` pe Unix | junction / symlink |

Regula care le ține laolaltă: **canonicul e în repo, operaționalul rulează,
oglinda le face legătură fără să copieze nimic.** Când o copie operațională
se schimbă, se propagă ** spre canonic, nu în sens invers — și numai când
schimbarea e o decizie, nu un artefact de runtime.

## 2. Harta rădăcinii

```
Mavis-Optimus-Dashboard/          <- SOT, radacina git
├── 00_INDEX/                     <- indexul materialului
├── 10_BRIDGES/                   <- punti catre alte sisteme (Obsidian, Wayland)
├── 20_BRIDGES/                   <- punti implementate
├── 20_PROTOCOLS/                 <- protocoale (agentic-os inclus)
├── 30_WORKFLOWS/                 <- fluxuri de lucru
├── 40_REGISTRIES/                <- JURNAL_OGLINDA: append-only, nu se sterge
├── 50_TEMPLATES/                 <- template-uri de extindere
├── 60_SKILLS/
│   ├── mavis-skills/             <- CANONIC: 409 fisiere de skill-uri
│   ├── _links/mavis-skills       <- JUNCTION -> registry-ul live
│   └── 60_skill_blueprints.md
├── 70_CONNECTORS/                <- conectoare, _links/ ignorat (spatiu Hermes)
├── 90_CONTROL_CENTER/            <- Control Center OPTIMUS (port 8900)
├── 95_DESIGN_SOT/                <- design
├── MINIMAX OPTIMUS CONTROL CENTER BLUEPRINT/   <- blueprint-ul original
├── Optimus_CD (by Jules)/        <- JUNCTION -> proiectul lui Jules (E:), neatinse
├── SENTINEL_PRIME/               <- UNIT (subtree, 3757b53)
├── Mavis-Google_Access/          <- UNIT (subtree, 549c348)
│   └── .work/MAVIS-CLOUD/        <- UNIT, prefix imbricat (b611b95, 244 commituri)
├── Optimus_CI (by Mavis)/        <- UNIT (subtree, fb38972)
├── scripts/
│   ├── git-hooks/pre-push        <- POARTA canonica de push
│   ├── lib/mavis-temp.ps1        <- helper de temp (GUID), creat la migrare
│   ├── cc-watchdog.ps1           <- supraveghetorul Control Center-ului
│   ├── sentinel-guardian.ps1     <- supraveghetorul backendului SENTINEL (8912)
│   ├── git-autopush.ps1          <- push cu -Acord
│   ├── push-status.ps1           <- peretele de push pe mai multe repo-uri
│   └── verify-docs.ps1
├── handoff/                      <- ACEST pachet
├── backups/                      <- IGNORAT: 12 junction-uri catre D:\Backups_Archive
│   └── _git_history/             <- IGNORAT: 5 bundle-uri complete
├── sites/  tests/  _DOCS/  _SYSTEM/
├── AGENTS.md  OPTIMUS_INDEX.md  SENTINEL_OPERATIONAL_DOCTRINE.md  README.md
```

## 3. Cele cinci repo-uri unite

Fiecare a intrat în istoria SOT-ului ca **merge-commit cu doi părinți** — al
doilea părinte e commit-ul sursei. Nu e o copiere de fișiere, e o unire de
istorice.

| Prefix în SOT | Repo sursă | Commit de referință | Ce conține |
|---|---|---|---|
| `SENTINEL_PRIME/` | `apvizual-max/SENTINEL_PRIME` (privat) | `3757b53` | nucleul SENTINEL: doctrine, monitori, command center |
| `Mavis-Google_Access/` | `apvizual-max/Mavis-Google_Access` | `549c348` | containerul de acces Google |
| `Mavis-Google_Access/.work/MAVIS-CLOUD/` | `apvizual-max/MAVIS-CLOUD` | `b611b95` | latura cloud, prefix **imbricat** |
| `Optimus_CI (by Mavis)/` | `apvizual-max/MAVIS-OPTIMUS-CI` | `fb38972` | pipeline-ul CI |
| `60_SKILLS/mavis-skills/` | `apvizual-max/Optimus-Mavis-Skills` | `8e90b56` | colecția de skill-uri |

Verificarea că istoricul a rămas întreg (toate trebuie să dea `0`):

```powershell
git merge-base --is-ancestor 3757b53 HEAD ; $LASTEXITCODE
git merge-base --is-ancestor 549c348 HEAD ; $LASTEXITCODE
git merge-base --is-ancestor 3b6b7dc HEAD ; $LASTEXITCODE
git merge-base --is-ancestor fb38972 HEAD ; $LASTEXITCODE
git merge-base --is-ancestor 8e90b56 HEAD ; $LASTEXITCODE
git merge-base --is-ancestor b611b95 HEAD ; $LASTEXITCODE
```

## 4. Junction-urile — harta legăturilor

Un junction e o legătură de director: conținutul trăiește într-un singur loc,
nu se copiază. Când conținutul țintei se schimbă, se schimbă peste tot.

| Legătură | Țintă | Rol | De ce există |
|---|---|---|---|
| `projects\SENTINEL_PRIME` | `SOT\SENTINEL_PRIME` | compatibilitate | consumatori vechi care încă folosesc calea veche |
| `projects\scripts\git-hooks` | `SOT\scripts\git-hooks` | compatibilitate | **poarta de push canonică**, o singură copie |
| `60_SKILLS\_links\mavis-skills` | `C:\Users\apviz\.minimax\agents\mavis\skills` | vedere runtime | registry-ul live de skill-uri, folosit de aplicație |
| `Optimus_CD (by Jules)` | `E:\Google\GDrive\...\Optimus_CD (by Jules)` | **proiectul lui Jules** | **nu e al nostru**. Nu se atinge. Nu intră în istorie |
| `SOT\backups\*` (12 intrări) | `D:\Backups_Archive\minimax_projects_backups\*` | arhivă | copiile de backup nu se copiază înăuntru |

## 5. Modelul oglindă — și unde se rupe

**Canonic:** `60_SKILLS/mavis-skills/` (în git, 409 fișiere).
**Operațional:** `C:\Users\apviz\.minimax\agents\mavis\skills` (registry-ul
live, cu `.git` propriu, remote `Optimus-Mavis-Skills`).
**Oglindă:** `60_SKILLS/_links/mavis-skills` → registry-ul live.

Consecințe reale, măsurate:

- Dacă se editează în registry-ul live, **canonicul nu se schimbă** singur.
  Propagarea e manuală și **trebuie făcută în sensul: live → canonic**.
- `60_SKILLS/_links/` e în `.gitignore` — deci junction-ul nu intră în
  istoric, cum nu poate intra un pointer absolut pe altă mașină.
- `Optimus_CI (by Mavis)` a fost, înainte de unire, un junction spre repo-ul
  live de pe `E:`. După unire, prefixul e **director real, urmărit de git**.
  Repo-ul de pe `E:` rămâne operațional pentru pipeline; nu mai e legătură
  în arbore, pentru că un `.git` înăuntru ar face din director un „gitlink" și
  gitul nu ar mai urmări conținutul.

## 6. Ce e ignorat, și de ce

`.gitignore` e scris cu motiv la fiecare grup de reguli — nu e o listă goală.
Grupurile: backup-uri și store-uri de versiuni, repo-uri unit acum în istorie
(deci **nu** mai sunt ignorate), spațiul lui Hermes (`70_CONNECTORS/_links/`,
`scripts/external/`, `scripts/hermes-custom/`), secretele, starea runtime
(regenerată), fișierele de stare SENTINEL (`09_LOGS/`, `api/*.json`,
`logs/`, `__pycache__/`, store-ul de versiuni, `test_suite.py`).

**Regula SENTINEL_PRIME** spune „nothing is excluded on purpose". Acea a fost
regula corectă pentru un repo de sine stător, cu working tree separat. În
monorepo, regula devine „**nimic nu se ascunde fără motiv scris**" — motivul e
în `.gitignore` și în mesajul de commit
(`SENTINEL_PRIME: starea runtime nu se mai urmărește în istoricul monorepo-ului`).
Fișierele **rămân pe disk**; istoricul lor e în commit-urile anterioare.

## 7. Inventarul măsurat

`handoff/_inventory/` conține, măsurat de un agent separat:
`01_STRUCTURE.md`, `02_SKILLS.md`, `03_CONNECTORS_MCP.md`,
`04_DEPENDENCIES_PORTS.md`. Fiecare număr din ele vine dintr-o comandă, cu
data.
