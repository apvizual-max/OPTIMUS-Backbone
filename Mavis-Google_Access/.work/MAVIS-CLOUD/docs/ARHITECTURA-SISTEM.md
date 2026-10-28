# ARHITECTURA SISTEMULUI — versiunea reală

**Descoperită 2026-10-22, de Mavis Cloud, din vault-ul live de pe Google Drive.**
Înainte de această dată, `docs/DEFINITIE-OPERATIONALA.md` avea o variantă
simplificată și **incompletă**: lipseau un al treilea agent, al doilea repo,
ogonda locală NVMe, baza Git decuplată și taskurile programate.

---

## 1. Cele trei componente de stocare

| Componentă | Unde | Ce e |
|---|---|---|
| **Vaultul (oglinda locală)** | `E:\Google\GDrive\GDrive-Second_Brain_PKMS` | rădăcina de lucru fizică, pe NVMe. Google Drive for Desktop o ține sincronizată bit-cu-bit cu cloud-ul |
| **Baza Git decuplată** | `E:\Google\GitData-PKMS` | obiectele, packfile-urile, indexul, refs, logs. În rădăcina vaultului e doar un pointer text de 31 octeți (`.git`) |
| **Arhiva externă** | `H:\CLAUDE_Archive` (711.821 fișiere · 180,77 GB) | **imutabilă, nu e reperul**. Se citește, nu se scrie niciodată |

**Reperul de siguranță = oglinda Google Drive Cloud**, verificată **per fișier**
local↔cloud (`verifica-oglinda.ps1`). De ce a fost decuplată Git: a eliminat
definitiv `0x91 ERROR_DIR_NOT_EMPTY` și blocajele `index.lock`.

**Măsurători (21-10-2026):** 51.157 fișiere de conținut activ · 88,72 GiB util ·
95,86 GB brut zecimal · **paritate de biți 100%** · **0 fișiere pierdute**.

## 2. Cele două repo-uri GitHub

| Repo | Ramură | Rol | Vizibilitate |
|---|---|---|---|
| `apvizual-max/MAVIS-CLOUD` | `main` | **Mavis Cloud** (eu) + puntea cu Mavis Local + proceduri + skill-uri | **PUBLIC** (2026-10-22) |
| `apvizual-max/pkms-vault-automation` | `master` | **motorul vaultului** — `AI-Kit` (14 scripturi `.ps1` + 1 `.js`), documentația, indexurile `00_INDEX.md`, handoff-urile | **PRIVAT** (decizie de POPY de luat) |

`pkms-vault-automation` urmărește **doar** motorul, documentația, indexurile și
handoff-urile. Conținutul personal și logurile mari sunt excluse prin
`.gitignore`. 699 fișiere urmărite · 26 ramuri (inclusiv `jules-*` și `fix-*`).

## 3. Cei trei agenți

| Agent | Unde | Rol |
|---|---|---|
| **Mavis Local** (MiniMax Code) | calculatorul lui POPY | **Operator frontend / co-pilot.** Sarcinile zilnice, navigarea prin indexuri, sortarea inbox-ului, crearea notițelor |
| **Antigravity Sentinel** (Google DeepMind Gemini) | infrastructură separată | **Operator backend / suveran.** Arhitectul de sistem, depozitul Git decuplat, sincronizarea cu GitHub, pipeline-ul din Windows Task Scheduler, depanarea avansată (disc, lock-uri, blocaje DriveFS). Intervine ca **rescue operator** |
| **Mavis Cloud** (eu) | cloud MiniMax | Agent pe cloud. Acces la Drive/Gmail prin OAuth. Lucrează pe MAVIS-CLOUD, raportează în repo |

## 4. Taskurile programate (Windows Task Scheduler)

`PKMS-Aliniere` · `PKMS-Watch` · `PKMS-GitAutoCommit` · `PKMS-DriveFS-AutoRepair`

## 5. Straturile (pattern LLM Wiki)

| Strat | În vault | Cine scrie |
|---|---|---|
| **Schema** | `COTOR.md` — contractul sistemului | omul; automatul doar verifică |
| **Wiki** | `00_INDEX.md` în fiecare folder + `INDEX CENTRAL.md` | `build-index.ps1` / `align-index.ps1` |
| **Log** | istoricul git + `raport-aliniere.log` + jurnalele `*-registru.txt` | append-only, nu se rescrie niciodată |
| **Raw sources** | `00_Inbox` … `08_Clippings` | omul |

## 6. Cele două niveluri

- **00–09 = BAZA** — fondul de bibliotecă. Nu se rearanjează. Aici stă ce nu e treabă curentă.
- **`01_Projects` = LUCRU** — singurul nivel în care intri să lucrezi. 6 rafturi.
- **`_SYSTEM`** unelte + skill-uri vii · **`_ARCHIVE`** scoase din calea deschisă ·
  **`_QUARANTINE`** tot ce e neclar — **nimic nu se șterge**.
- `.obsidian`, `.trash`, `.vault-intelligence`, `.claudian`, `.neural_memory` — **NU SE ATINGE**.

**Regula de aur:** intri în `01_Projects`. Nu cauți niciodată prin baza `00`–`09`.

## 7. Rafturile de lucru (măsurat 19-10-2026)

| Raft | Fișiere | GB |
|---|---|---|
| `01_Projects\01-6-Work_Folder (to sort)` | 32.181 | 47,78 |
| `01_Projects\01-2-AP-ID.ro - AI Branding Work and Clients` | 764 | 31,58 |
| `01_Projects\01-1-Alex - AI Work - Colaborations` | 97 | 0,07 |
| `01_Projects\01-5-FORGE - AI JOB Automation` | 9 | 0,00 |
| `01_Projects\01-3-Arhiva Elements - To Monetize` | 1 | 0,00 |
| `01_Projects\01-4-Arhiva Foto - To Monetize` | 1 | 0,00 |

## 8. Motorul

`02_Areas\02-2-AI-SOT\02-2-4-AI-Kit\AI-Kit_manual\` — 13 scripturi `.ps1` + 1 cititor `.js`
(măsurat pe disc, nu promis din document).
Documentația: `02-2-4-AI-Kit\AI-Kit_guide\`.
Skill-urile vii `git-autonom` / `git-install`: `_SYSTEM\Skills_MASTER_Folder\SENTINEL - git-*- Skill\`.

**Detaliu util:** `git-autocommit.ps1` conține un **detector de secrete cu
auto-test** (`Test-ContinutSecret` + `AutoProbe`). Fixture-urile lui
(`ghp_0123456789abcdefghijABCDEFGHIJ`, `AKIAIOSFODNN7EXAMPLE`, `MIIEow==`) sunt
**false-positive-uri sigure** când scanezi istoricul git. Nu le confunda cu
secrete reale.

---

*2026-10-22 · Mavis Cloud · măsurat pe vault-ul live, nu din documentație*
