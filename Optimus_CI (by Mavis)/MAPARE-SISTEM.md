# MAPARE — unde stă tot

> Nu se mută nimic din alte proiecte. Totul e **prin referință**, ca
> nimic să nu se piardă dacă o cale se schimbă.

## Proiectul ăsta

```
E:\Google\GDrive\GDrive-Second_Brain_PKMS\02_Areas\02-2-AI-SOT\CASA\OPTIMUS - Prime\Optimus_CI (by Mavis)\
├── README.md                    punct de intrare, cold-boot
├── DOCTRINA-CI.md               cum lucrez
├── MAPARE-SISTEM.md             acest fișier
├── docs\
│   ├── MAPARE-FOLDERE.md        ce e în fiecare folder, măsurat
│   ├── WORKFLOWS.md             fluxurile, porțile, codurile de ieșire
│   ├── CONFLICTE-DOZTRINA.md    7 conflicte găsite + hotărâri  ← CITESTE
│   ├── CI-POLICY.md             politica CI: puntea, guvernanța, porțile
│   ├── BRIDGE-LOCAL-CLOUD.md    puntea, adaptată la R0
│   ├── PUNTE-DRIVE-PRIMARA.md   canalul primar Drive, cu măsurătorile
│   ├── CONTRACT-CLOUD-QUEUE.md  contractul cozii secundare, citat de pe discul Cloud
│   ├── GIT-GITHUB-PROCEDURI.md  procedurile Git/GitHub, cu mecanism și probe
│   ├── ARHITECTURA-CI-CD.md     convenția care separă CI de CD
│   ├── PROTOCOL-DENUMIRE-LOCAL-CLOUD.md  protocolul de denumire
│   ├── INVENTAR-REPO-URI.md     toate repo-urile
│   ├── RECUPERARE-GIT.md        starea măsurată a mașinii
│   ├── STARE-MASURATA-CI-2026-10-27.md   starea de azi, cu cifre + metode
│   ├── STARE-MAVIS-OPTIMUS-CI-REMOTE.md  referința remote, lucrată de alt AI
│   ├── META-PROMPT.md           generarea meta-promptului
│   ├── STATUS-LOCAL-TO-CLOUD-2026-10-12.md  raport de status
│   └── arhiva\handoffs-vechi\   handoff-uri consumate — **mutate, nu șterse**
├── BRIDGE-DRIVE\                canalul primar (Google Drive)
├── QUEUE\                       canalul secundar (GitHub)
│   ├── TASKS-FOR-CLOUD.md       coada, în contractul consumatorului
│   └── DONE\                    ținta de livrare a lui Cloud
├── scripts\                     instrumentele
├── .github\workflows\           plasa de siguranță a serverului
│   └── ci-verify.yml
├── blueprint\
│   └── BLUEPRINT-PLAN-CI.md     planul de execuție           ← CITESTE
├── logs\                        jurnalele punții zilnice
└── cloud-ingest\
    └── MAVIS-CLOUD\             clonă locală, **NEATINGEĂ**
```

> **Adăugat 2026-10-27.** Arborele de mai sus e completat, nu rescris.

## Doctina de bază — în afara proiectului

| Ce | Unde |
|---|---|
| Doctrina completă | `C:\Users\apviz\.minimax-agent\projects\SENTINEL_OPERATIONAL_DOCTRINE.md` |
| Substratul SENTINEL | `C:\Users\apviz\.minimax-agent\projects\SENTINEL_PRIME\01_FOUNDATION\doctrine\A_FI_DOCTRINE.md` |
| **§20 — doctrina operațională** | în fișierul de sus, secțiunea 20 |

## Skillurile vii — în afara proiectului

| Skill | Rol |
|---|---|
| `mavis-autonomous-operator-skill` | **se încarcă primul** — gândire, trei piloni |
| `mavis-git-install-skill` | ridicarea unui repo nou |
| `mavis-git-autonom-skill` | lucru zilnic cu Git |
| `mavis-optimus-continuous-integration-skill` | **scopul acestui proiect** |

Toate în `C:\Users\apviz\.minimax\agents\mavis\skills\`.

## Scriptele de Git — în afara proiectului

| Script | Ce face |
|---|---|
| `projects\scripts\git-autopush.ps1` | **singura poartă de push** — cere `-Acord` |
| `projects\scripts\push-status.ps1` | peretele: câte comituri neîmpinse, per repo |
| `projects\scripts\git-hooks\pre-push` | poarta reală, per repo, în istorie |

## Repo-urile GitHub ale lui Popy

| Repo | Rol | Acces |
|---|---|---|
| `Optimus-Mavis-Skills` | skillurile mele | **public** |
| `OPTIMUS-Backbone` | consola OPTIMUS, scripturi | **public** |
| `SENTINEL_PRIME` | substratul SENTINEL | privat |
| **`MAVIS-CLOUD`** | **fostul cartier Cloud** | **public** |
| **`MAVIS-OPTIMUS-CI`** | **acest proiect** | **public** |
| `MAVIS-OPTIMUS-CD` | SOT CD — **se creează la priming** (R0) | de creat |
| `Qwen-Ecosystem-Dashboard` | sistem Qwen | privat |
| `hermes-doctor` | plasa lui Hermes | **public** |
| `pkms-vault-automation` | menținerea vaultului | **public** |

**Re-măsurat 2026-10-27** (`gh repo list apvizual-max --limit 60 --json
name,visibility,pushedAt`). Inventarul complet, cu datele de push și cu
numărul de secrete: `docs/INVENTAR-REPO-URI.md`.

Lista completă și măsurată: `docs/INVENTAR-REPO-URI.md`.

## Regula Triadei

```
1 conversație  =  1 folder local  =  1 repo GitHub
```

Fiecare proiect are conversația, folderul și repo-ul lui. **Proiectele nu
se ating între ele.** Când alt proiect are nevoie de ceva, eu dau un
prompt, Popy îl duce în sesiunea aceea, care are contextul complet.

**Aceasta e și motivul pentru care nu ating repo-urile altor proiecte:** nu
am contextul lor, și un agent fără context într-un repo străin e exact
defectul pe care îl reparăm.

---

## Celălalt cartier — CD

Sesiunea CD e **paralelă**, cu folderul, repo-ul și bugetul lui:

```
E:\Google\GDrive\GDrive-Second_Brain_PKMS\02_Areas\02-2-AI-SOT\CASA\OPTIMUS - Prime\Optimus_CD (by Jules)\
├── README.md · DOCTRINA-CD.md · HANDOFF-CD.md · PRIMING-CD.md
├── docs\                       ARHITECTURA · SPEC · MAPARE · WORKFLOWS · PROTOCOALE
└── JULES - Optimus CD\         platforma Jules (10 scripturi, config, workflows)
```

**Calea veche a CD-ului** `…\projects\Mavis-Optimus-Continuous-Development\`
**nu mai există** — CD-ul a fost mutat pe `E:` la aceeași consolidare.
Joncțiune pe `C:`: `C:\Users\apviz\.minimax-agent\projects\Optimus_CD (by Jules)`.
Gitdir CD: `E:/Google/GitData-Optimus-CD` — **separat** de cel al CI.

| | CI (aici) | CD (acolo) |
|---|---|---|
| Puntea Local↔Cloud | ✅ | — |
| Ingest + livrarea cozii secundare | ✅ | — |
| Canalul `QUEUE/` | ✅ | — |
| Platforma Jules | — | ✅ |
| Live Review | — | ✅ |
| Cota 100 taskuri/zi | — | ✅ |

**Nu ne atingem.** CD nu scrie în `MAVIS-CLOUD`; CI nu rulează triajul.

---

## Topologia măsurată — 2026-10-27

> **Aditiv.** Nimic din arborele de mai sus nu se mută și nu se șterge.
> Secțiunea de jos reflectă **unde stă tot ACUM**.

### Sursa fizică

```
E:\Google\GDrive\GDrive-Second_Brain_PKMS\02_Areas\02-2-AI-SOT\CASA\OPTIMUS - Prime\Optimus_CI (by Mavis)\
├── .git                          ← FIȘIER (worktree link) → E:\Google\GitData-Optimus-CI\repo
├── README.md · DOCTRINA-CI.md · MAPARE-SISTEM.md
├── BRIDGE-DRIVE\                ← PUNTEA PRIMARĂ (Google Drive)
│   ├── README-BRIDGE-DRIVE.md   protocolul
│   ├── TASKURI-PENTRU-CLOUD.md  Local → Cloud, structurat
│   ├── INTENTII.md              Popy → Cloud, liber
│   ├── INTRARI-CLOUD\           Cloud → Local
│   └── ISTORIC\                 consumate: se mută, nu se șterg
├── QUEUE\                        ← canalul SECUNDAR (GitHub)
│   ├── TASKS-FOR-CLOUD.md
│   └── DONE\ README.md           consumate: marcate [x] de Cloud
├── docs\        documentația de proiect
├── .jules\                       ← bootstrapul lui Jules (bolt.md · sentinel.md)
├── JULES_HANDOFF.md              ← predarea către sesiunea Jules
├── scripts\     mavis-sync.ps1 · run-sync-logged.ps1 · meta-prompt.ps1
│                notebooklm-cdp.mjs · snapshot-vault.ps1
│                drivefs_probe.py · mavis-drive-bridge.ps1
│                mavis-drive-bridge-selfcheck.ps1
│                scan-staged-secrets.ps1 · scan-staged-secrets-selfcheck.ps1
│                queue-contract-check.ps1 · queue-contract-check-selfcheck.ps1
│                queue-lib.ps1 · queue-deliver.ps1 · queue-deliver-selfcheck.ps1
│                publish-ci.ps1 · publish-ci-selfcheck.ps1
│                mavis-sync-selfcheck.ps1
│                merge-check.ps1 · merge-check-selfcheck.ps1
├── tools\                       ← SURSA containerului Google (reconstruibil din GitHub)
│   └── google-access\            server.mjs · Dockerfile · probe.mjs · provision-grant.cjs
│                                  watch-reauth.ps1 · README.md · .dockerignore · .gitignore
├── .github\workflows\            ← plasa de siguranță a serverului
│   └── ci-verify.yml
├── blueprint\ · cloud-ingest\ (clonă + copie de lucru a livrării) · logs\ · state\ (ignorat de git)
```

### Unde stă datele git locale

**Regula:** tot ce înseamnă date git local stă **în afara mirrorului**, într-un
**singur folder pe proiect**: `E:\Google\GitData-Optimus-CI\`. În arborele
proiectului, `.git` e **un fișier** pointer, nu un director.

```
E:\Google\GitData-Optimus-CI\        ← SINGURUL folder de git al acestui proiect
├── repo\                            gitdir-ul acestui repo (MAVIS-OPTIMUS-CI)
├── clone-MAVIS-CLOUD\                gitdir-ul clonei cloud-ingest\MAVIS-CLOUD
├── clone-MAVIS-OPTIMUS-CI\           gitdir-ul clonei cloud-ingest\MAVIS-OPTIMUS-CI
└── scratch\                          fixture-urile porților (repository-uri de test)
```

| Repo | `.git` în arbore | Gitdir | Remote |
|---|---|---|---|
| Optimus CI | `.git` | `E:/Google/GitData-Optimus-CI/repo` | `MAVIS-OPTIMUS-CI` |
| Clona Cloud | `cloud-ingest\MAVIS-CLOUD\.git` | `E:/Google/GitData-Optimus-CI/clone-MAVIS-CLOUD` | `MAVIS-CLOUD` |
| Clona CI | `cloud-ingest\MAVIS-OPTIMUS-CI\.git` | `E:/Google/GitData-Optimus-CI/clone-MAVIS-OPTIMUS-CI` | `MAVIS-OPTIMUS-CI` |
| CD *(alt proiect)* | `.git` | `E:/Google/GitData-Optimus-CD` | de creat |
| PKMS *(alt proiect)* | `.git` | `E:/Google/GitData-PKMS` | `pkms-vault-automation` |

**De ce.** DriveFS administrează spațiul din `E:\Google\GDrive\` cât timp
sincronizează: materializează, înlocuiește, șterge. Un `.git\` viu n-are
nicio problemă într-un arbore normal; într-un arbore sincronizat, are.

**Fixture-urile porților** — repository-uri git de test — stau în
`E:\Google\GitData-Optimus-CI\scratch`, tot în afara mirrorului. Radicalul se
derivează din gitdir-ul repo-ului propriu (`scripts\git-scratch.ps1`), deci
laboratorul urmează repository-ul în loc să hard-codeze o cale de mașină.

**Măsurat 2026-10-27:** în arborele CI erau **63 de directorii `.git`** de
fixture, în plus față de cele ale proiectelor. După mutare: **0**. În
subarborele `CASA\OPTIMUS - Prime` au rămas **32** de directorii `.git`, toți
în proiecte **surori** (CD: 21, `AI_Tools`: 8 clonelor vendor,
Plugins-Config: 2, PKMS: 1); în tot mirrorul `E:\Google\GDrive` sunt **34**.
Sunt **în afara frontierei acestui proiect**, deci neatinse.

### Joncțiunile

| Acces rapid | Sursa fizică |
|---|---|
| `C:\Users\apviz\.minimax-agent\projects\Optimus_CI (by Mavis)` | folderul de pe `E:` de mai sus |
| `C:\Users\apviz\.minimax-agent\projects\Optimus_CD (by Jules)` | `E:\…\CASA\OPTIMUS - Prime\Optimus_CD (by Jules)` |

**Calea veche** `…\projects\Mavis-Optimus-Continuous-Integration\` **nu mai
există** — mutată pe `E:` la consolidarea din 2026-10-25, cu joncțiune în
loc. Nimic nu s-a pierdut: istoricul e în `E:\Google\GitData-Optimus-CI/repo`.

### Ce e nou în CI (2026-10-27)

| Ce | Unde | De ce |
|---|---|---|
| Puntea Drive (primară) | `BRIDGE-DRIVE\` | ambele instanțe au acces la Drive |
| Canal secundar | `QUEUE\TASKS-FOR-CLOUD.md` | rezervă, scris simultan |
| Măsurătorul Drive | `scripts\drivefs_probe.py` | singura sursă de adevăr, API-ul e rupt |
| Orquestratorul punții | `scripts\mavis-drive-bridge.ps1` | scrie **și** măsoară |
| Poarta punții | `scripts\mavis-drive-bridge-selfcheck.ps1` | 19 probe, poate eșua |
| Contractul cozii | `docs\CONTRACT-CLOUD-QUEUE.md` | consumatorul, citat de pe discul Cloud |
| Poarta cozii | `scripts\queue-contract-check.ps1` | contract **viu**, drift, paritate, țintă de livrare |
| Auto-proba cozii | `scripts\queue-contract-check-selfcheck.ps1` | 14 probe, falsificare în ambele sensuri |
| Livrarea cozii | `scripts\queue-deliver.ps1` | scrie tichetele în repo-ul Cloud-ului si le publica; exit `0`/`1`/`2`/`4`/`5` |
| Biblioteca cozii | `scripts\queue-lib.ps1` | parserul cozii, **o singura implementare** pentru poarta si livrare |
| Auto-proba livrarii | `scripts\queue-deliver-selfcheck.ps1` | 15 probe, falsificare în ambele sensuri |
| Măsurătorul combinării | `scripts\merge-check.ps1` | dry-run `merge-tree`: divergență, conflicte, arbore rezultat |
| Auto-proba combinării | `scripts\merge-check-selfcheck.ps1` | 5 probe pe repo reale, falsificare în ambele sensuri |
| Ținta de livrare | `QUEUE\DONE\` | unde Cloud scrie rezultatele |
| Poarta de secrete | `scripts\scan-staged-secrets.ps1` | 9 forme fixe + atribuiri cu valoare |
| Workflow de server | `.github\workflows\ci-verify.yml` | raportează, nu blochează |
| Starea de azi | `docs\STARE-MASURATA-CI-2026-10-27.md` | cifre + metode |
| Snapshot remote | `docs\STARE-MAVIS-OPTIMUS-CI-REMOTE.md` | alt AI lucrează acolo |
| Specificația punții | `docs\PUNTE-DRIVE-PRIMARA.md` | arhitectura + latența |
| **Sursa containerului Google** | `tools\google-access\` | 6 fișiere, SHA256 identic cu sursa vie → **reconstruibil din GitHub**; credentialul exclus |
| Răspunsurile Cloud-ului | `BRIDGE-DRIVE\INTRARI-CLOUD\` | 2 rapoarte de operare (08:49, 12:07) |
| Task consumat, arhivat prin mutare | `BRIDGE-DRIVE\ISTORIC\` | conținut păstrat integral |
| Handoff pentru CD | `docs\HANDOFF-CD-2026-10-27-PUNTEA-DRIVE-PRIMARA-GOOGLE-ACCESS.md` | SHA256 identic cu `Optimus_CD (by Jules)\_Handoffs\` |

### Topologia Drive, corectată

| Ce | Stare măsurată |
|---|---|
| Mirrorul | `E:\Google\GDrive\` (rădăcină `Google\GDrive`, `root_id=23`, MIRROR) |
| **`G:`** | **nu** e mount virtual — volum fix, cu scurtătură `My Drive.lnk` → `E:\Google\GDrive` |
| DriveFS | rulează; startup 2026-10-26 22:43 |
| Folderul CI în Drive | `cloud_id 1V87h9Pbw52chSVNkxQ_NNuMh-CLfZeuI` |

Conventția care explică tot: `docs/ARHITECTURA-CI-CD.md`.