# Mavis Optimus Continuous Integration — HQ

**Proiect:** OPTIMUS CI · **Rol:** Mavis Local · **Conv:** această conversație
**Început:** 2026-10-11 · **Doctrine:** `DOCTRINA-CI.md`

---

## Citește asta primul, agent nou, cu zero memorie

Ai ajuns în cartierul general. **Trei rânduri și știi tot:**

0. **cel mai întâi:** `docs/MAVIS-LOCAL-ONBOARDING-2026-10-27.md` — onboardingul
   complet: topologia fizică măsurată, cele două canale, contractul cozii,
   cele șapte porți cu exit codes, **unde stă datele git**, starea Google
   Access. E scris pentru un agent cu zero memorie.
1. citește `DOCTRINA-CI.md` — cum lucrez
2. citește `docs/CONFLICTE-DOZTRINA.md` — ce s-a hotărât și de ce
3. citește `docs/ARHITECTURA-CI-CD.md` — cine ține ce, și unde e CD

Apoi citește `MAPARE-SISTEM.md` — unde stă tot.
Pentru cifrele de azi: `docs/STARE-MASURATA-CI-2026-10-27.md`.

**Unde stă datele git:** în `E:\Google\GitData-*`, **în afara mirrorului
DriveFS**. În arbore, `.git` e un fișier pointer. Fixture-urile porților stau
în `E:\Google\GitData-Optimus-CI\scratch`. Instrumentele:
`scripts/git-scratch.ps1` · `scripts/relocate-gitdata.ps1`.

---

## Ce este acest proiect, într-un rând

**Inginerul de sistem al integrării continue a lui Popy.** Nu lucrez la
conținut — lucrez la **sistem**: Git, GitHub, poarta R0, puntea
Local↔Cloud.

## Ce NU este acest proiect

Nu e CD. **Bucla Jules și Live Review sunt în folderul CD**, cu
sesiunea și repo-ul lor: `MAVIS-OPTIMUS-CD`.
Nu sunt producție, nu sunt site, nu sunt CV-uri, nu sunt vault. **Acelea au
fiecare conversația și folderul lor propriu.** Regula Triadei:
`1 conversație = 1 folder = 1 repo`.

---

## Cele trei piloni — modul prin care răspund

```
RUCSAC     — ce e adevărat și măsurat
LOGICĂ     — de ce se leagă, sau de ce nu se leagă
STRATEGIE  — ce e optim în ansamblu, și decizia luată
```

Fiecare propunere, fiecare raport, fiecare nealiniere — pe acești trei.
Nu sunt rapoarte de situație. **Predau rezultatul gândit, nu problema.**

---

## Guvernanța Git — permanentă

| | |
|---|---|
| **COMMIT** | automat, mereu, pe `main`. **Fără R0, niciodată.** |
| **FORK** | doar cerut explicit, ca GOAL + CRITERIA |
| **PUSH spre GitHub** | **singurul** lucru care cere R0 |
| **≥50 neîmpinse** | îl reamintesc la fiecare răspuns, până dă R0 |
| **Changes** | gol, permanent, la toate proiectele de pe mașină |
| **Instanța Cloud** | singura care împinge fără R0 — container volatil |

Mecanismul complet, cu măsurătorile și proba falsificare:
`docs/GIT-GITHUB-PROCEDURI.md`.

---

## Cele trei reguli pe care nu le încalc niciodată

1. **Utilizatorul nu se va îmbunătăți niciodată.** Proiectez pentru un om
   fără cunoștințe de Git, cu zero memorie între sesiuni. Raportul e
   întotdeauna complet în sine.
2. **Prezența lui într-o buclă e o eroare de sistem.** Scoaterea lui din
   buclă e sarcina mea, nu un favor. Cererea de aprobare necerută **e**
   corupția.
3. **O poartă care stă în prohă, sau într-un flag pe care eu îl pot pasa,
   nu e o poartă.** Mecanismul trebuie să mă oprească și când vreau să
   trec.

---

## Cele două repo-uri, și cine ține fiecare

| Repo | Vizibilitate | Rol | Cine îl administrează |
|---|---|---|---|
| `apvizual-max/MAVIS-CLOUD` | **public** | **puntea** Local↔Cloud. Canal `QUEUE/TASKS-FOR-CLOUD.md`. | Instanța Cloud împinge automat; **CI** face ingest-ul și guvernanța |
| `apvizual-max/MAVIS-OPTIMUS-CI` | **public** | **acest proiect** — SOT pentru proceduri, punte, guvernanță | **CI**, cu commit automat + R0 push |
| `apvizual-max/MAVIS-OPTIMUS-CD` | **public** | SOT pentru bucla Jules + Live Review | **CD**, cu commit automat + R0 push |

Inventarul complet, măsurat: `docs/INVENTAR-REPO-URI.md`.

---

## Surse

| Sursă | Rol |
|---|---|
| `cloud-ingest/MAVIS-CLOUD/` | clonă locală a repo-ului Cloud — **NU se modifică** |
| `C:\Users\apviz\.minimax-agent\projects\SENTINEL_OPERATIONAL_DOCTRINE.md` | doctrina de bază, §20 |
| `C:\Users\apviz\.minimax\agents\mavis\skills\` | skillurile vii |
| `C:\Users\apviz\.minimax-agent\projects\scripts\git-autopush.ps1` | **singura poartă de push** |
| `C:\Users\apviz\.minimax-agent\projects\scripts\push-status.ps1` | peretele: comituri neîmpinse, per repo |
| `C:\Users\apviz\.minimax-agent\projects\scripts\git-hooks\pre-push` | poarta reală, per repo, în istorie |

---

## Mapă

| Folder / fișier | Ce e |
|---|---|
| `README.md` | acest fișier — punct de intrare, cold-boot |
| `DOCTRINA-CI.md` | cum lucrez |
| `MAPARE-SISTEM.md` | unde stă tot |
| `docs/` | documentația de proiect |
| `docs/CONFLICTE-DOZTRINA.md` | **cele conflicte găsite, și hotărâra** |
| `docs/ARHITECTURA-CI-CD.md` | **convenția care separă CI de CD** |
| `docs/GIT-GITHUB-PROCEDURI.md` | **procedurile Git/GitHub, cu mecanism și probe** |
| `docs/PUBLISH-CI.md` | **publicarea pe GitHub**: instrumentul, codurile de ieșire, cele 12 probe |
| `docs/CI-POLICY.md` | politica CI: puntea, guvernanța, verificarea |
| `docs/STARE-MASURATA-CI.md` | **starea măsurată azi, cu cifre și metode** |
| `docs/INVENTAR-REPO-URI.md` | toate repo-urile, locale și GitHub |
| `docs/BRIDGE-LOCAL-CLOUD.md` | puntea, în detaliu |
| `docs/MAPARE-FOLDERE.md` | **ce e în fiecare folder al proiectului**, măsurat |
| `docs/WORKFLOWS.md` | **cum se lucrează**: fluxuri, porți, coduri de ieșire |
| `docs/PUNTE-DRIVE-PRIMARA.md` | **canalul primar** Drive: arhitectură, măsurători |
| `docs/CONTRACT-CLOUD-QUEUE.md` | **contractul cozii secundare**, citat de pe discul Cloud-ului |
| `docs/PROTOCOL-DENUMIRE-LOCAL-CLOUD.md` | protocolul de denumire |
| `docs/META-PROMPT.md` | generarea meta-promptului |
| `docs/RECUPERARE-GIT.md` | starea măsurată a mașinii, cu cifre |
| `docs/STARE-MASURATA-CI-2026-10-27.md` | **starea de azi**, cu cifre și metode |
| `docs/STARE-MAVIS-OPTIMUS-CI-REMOTE.md` | referința remote, lucrată de alt AI |
| `docs/STATUS-LOCAL-TO-CLOUD-2026-10-12.md` | raport de status |
| `docs/arhiva/handoffs-vechi/` | handoff-uri consumate — **mutate, nu șterse** |
| `blueprint/` | planul de execuție al proiectului |
| `cloud-ingest/` | clona `MAVIS-CLOUD`: sursa contractului consumatorului **și copia de lucru a livrării cozii secundare** |
| `scripts/` | puntea: `mavis-sync.ps1`, wrapper, snapshot, meta-prompt · `publish-ci.ps1` (publicarea) · `merge-check.ps1` (măsurătoarea) |
| `logs/` | logul datat al fiecărei rulări a punții |
| `.github/workflows/` | **plasa de siguranță a serverului**: `ci-verify.yml` |

---

## Starea acum

Repo: **public**, ramura `main`. **Sincronizat cu `origin/main`** — invariant
măsurat `2026-10-27`, după livrarea cozii și publicarea instrumentelor:
`remote = HEAD local`, `DIVERGENCE_FINAL=0 0`, verificat prin `git ls-remote`.

**SHA-ul nu se scrie aici**, pentru că se schimbă la fiecare commit automat și
ar fi fals în momentul scrierii. **Se măsoară:**
`git -C "<repo>" ls-remote origin refs/heads/main` → trebuie să fie identic cu
`git -C "<repo>" rev-parse HEAD`.

Commitul de combinare `86669d9` are **doi părinți** (`e9290f7` local +
`3da55ff` remote): istoricul celuilalt AI a fost **inclus**, nu suprascris.
De atunci: livrarea cozii secundare în `MAVIS-CLOUD` (`4a88879`) și
publicarea instrumentelor de livrare în acest repo (`8afa89b`).

Publicarea se face cu **un instrument**, nu cu comenzi manuale:
`scripts\publish-ci.ps1` (măsoară → combină → împinge → verifică prin
`ls-remote`). Fără `-Push` nu mută nimic. Detalii: `docs/PUBLISH-CI.md`.

> Cifra se schimbă la fiecare commit automat, deci ar fi falsă în momentul
> scrierii. **SHA-ul exact al HEAD:** `git -C "<repo>" log -1 --oneline`.
> Cifrele complete: `docs/STARE-MASURATA-CI-2026-10-27.md`.

**Puntea e vie:** taskul `MavisSyncBridge` are declanșatorul zilnic la
**07:30** (`StartBoundary 2026-10-12T07:30:00+02:00`, `StartWhenAvailable=True`
— de aceea rulările din 23–24 oct apar la 08:30: mașina nu era pornită la
07:30). Ultima rulare: **27 oct 02:14** (declanșată la cerere) →
`LastTaskResult=0`, `exit_pull=0`, `local_dapa == remote` (`7f8e5de`),
`impingere=NEEXECUTATA`. Log: `logs/mavis-sync-2026-10-27.log`.

---

## Puntea Drive — canalul primar (din 2026-10-27)

> **Aditiv.** Nimic din secțiunile de mai sus nu se rescrie.

| | |
|---|---|
| **Canal primar** | **Google Drive** — folderul `BRIDGE-DRIVE/`, în mirrorul `E:\Google\GDrive\` |
| **Canal secundar** | GitHub — `QUEUE/TASKS-FOR-CLOUD.md` |
| Folderul proiectului | `E:\Google\GDrive\…\CASA\OPTIMUS - Prime\Optimus_CI (by Mavis)` |
| Joncțiune pe C: | `C:\Users\apviz\.minimax-agent\projects\Optimus_CI (by Mavis)` |
| cloud_id în Drive | `1V87h9Pbw52chSVNkxQ_NNuMh-CLfZeuI` |
| Lag de propagare | **≈ 80 min** pe exemplul istoric — dar măsurarea de azi e mai severă: vezi secțiunea de mai jos |

**Ce s-a schimbat:** canalul principal nu mai e repo-ul GitHub, ci un
folder Google Drive pe care ambele instanțe îl văd. GitHub rămâne, ca
**rezervă** — și e scris la publicare, nu doar când primul canal cade.

**Măsurătorile**:
```powershell
powershell -NoProfile -File scripts\mavis-drive-bridge.ps1 -Status
powershell -NoProfile -File scripts\mavis-drive-bridge-selfcheck.ps1
```

Detalii: `docs/PUNTE-DRIVE-PRIMARA.md` · `docs/STARE-MASURATA-CI-2026-10-27.md`

**Observație de guvernanță:** repo-ul `MAVIS-OPTIMUS-CI` e lucrat acum de
sesiunea CD. Noi ținem copia și referința — `docs/STARE-MAVIS-OPTIMUS-CI-REMOTE.md`.

---

## Două defecte de măsurătoare, reparate (2026-10-27, ~02:00)

> **Aditiv.** Nimic din secțiunile de mai sus nu se rescrie.

| Defect | Simptom | Reparare |
|---|---|---|
| Sonda citea un **nume de fișier fix** (`drive_fs.txt`) | `UNKNOWN` pentru un transport funcțional — logul activ era `drive_fs_507.txt`, iar `drive_fs.txt` conținea urma unei lansări **eșuate** (`CANNOT_START_IPC`) | Sonda scanează toate logurile și ia anunțul cel mai recent, ordonat după amprenta din interiorul liniei |
| Instrumentul spunea **`TRANSPORT=UP`** pe baza unei măsurători nereușite | `UNKNOWN` trecea pe ramura `UP` — un instrument care afirma ceva ce n-a măsurat | `UNKNOWN` are ramura ei: `TRANSPORT=UNKNOWN`, ieșire 4; poarta **respinge** raportul falsificat |

**Falsificat în ambele sensuri** (6 cazuri): anunț vechi vs nou, cuplare
per-rădăcină, lipsa oricărui anunț → `UNKNOWN` + exit 3, raport falsificat
**respins**, raport adevarat **acceptat**, citesirea unui log neatins de
>30 min → **FAIL**.

**Starea după reparație:** `BRIDGE_PROBLEMS=0 UNKNOWN=0` (19 probe),
`SECRET_PROBLEMS=0 UNKNOWN=0` (7 probe), `TRANSPORT=UP`,
`PROPAGATION=STALE`, `ACTIVE_CHANNEL=GITHUB`, ieșire 4.

**Rădăcina e conectată** — `ROOT_STATE=true`, anunț `2026-10-26T22:43:24`,
citit din `drive_fs_507.txt`. **Propagarea e tot STALE** — măsurătoarea
separată, nemodificată prin repararea instrumentului.

Detalii: `docs/STARE-MASURATA-CI-2026-10-27.md` §7 · `DOCTRINA-CI.md` §8.2

---

## Starea canalului primar, măsurată 2026-10-27

> **Aditiv.** Nimic din secțiunile de mai sus nu se rescrie.

**Canalul Drive e construit, dar nu încarcă conținut nou.** Măsurătoarea
directă, nu o presupunere:

| Ce | Măsurat |
|---|---|
| Rădăcina mirrorului | `MIRROR_ROOT_STATE=true` — **conectată** |
| Coada de operațiuni | `PENDING_OPERATIONS=0` |
| Motor sync DriveFS | `change_ids_up_to_date: true` · `operation_queue_size: 0` — **nu vede scrierile locale** |
| Vârsta copiei din cloud | **`CLOUD_TRACKED_AGE_DAYS=2.91`** (pentru `MAPARE-SISTEM.md`) |
| Fișierul canalului în cloud | **`CLOUD_CHANNEL_FILE_PRESENT=false`** |
| Verdictul instrumentului | `PROPAGATION=STALE` · `ACTIVE_CHANNEL=GITHUB` · **exit 4** |

**Consecința, spusă fără cosmetizare:** arborele CI **există în cloud**, cu
`cloud_id`-uri și la calea corectă — dar cu **conținutul de dinaintea mutării
din 26 oct**. „Folderul e în Drive" și „conținutul de azi e în Drive" sunt două
lucruri diferite, iar al doilea e fals.

**Deci, până la un restart/re-login al DriveFS:** pentru conținut **nou**, canalul
activ e **GitHub** (push cu R0). Canalul Drive rămâne *structura*, nu
*transportul*.

Instrumentul nu mai raportează fals: separă `TRANSPORT` (conectat) de
`PROPAGATION` (confirmat), iar poarta verifică **concordanța**
raport–măsurătoare, cu probe de falsificare.

Detalii: `docs/PUNTE-DRIVE-PRIMARA.md` §4.1–§4.2 ·
`docs/STARE-MASURATA-CI-2026-10-27.md`

---

## Canalul secundar — reparat, măsurat (2026-10-27, ~02:40)

> **Aditiv.** Nimic din secțiunile de mai sus nu se rescrie.

`QUEUE/TASKS-FOR-CLOUD.md` avea două tichete citibile cu ochiul și era
**inexecutabilă** de Cloud. Contractul consumatorului, citit de pe discul
lui Cloud: `### [id] titlu` + `cerut de` · `data` · `scope` · `ce trebuie` ·
`livrare`, iar Cloud rulează **doar** tichetele cu `scope: cloud`.

| Măsurat, înainte | Valoare |
|---|---|
| Câmpuri de contract în coadă | **0 din 5** |
| Tichete cu `scope:` | **0** → Cloud ar executa **zero** tichete |
| Anteturi invizibile pentru Cloud (`## TASK-…`) | **2** |
| `QUEUE/DONE/` (ținta de livrare) | **absent** |
| Ultima linie, în **ambele** canale | `Nu intai` — mijloc de propoziție |

**Defectul era în generator, nu în fișier:** publisherul a primit un corp
trunchiat și l-a scris în ambele canale, raportând succes. Deci s-a reparat
publisherul, nu doar coada.

| Reparare | Unde |
|---|---|
| Copia secundară se scrie în **contractul consumatorului** | `scripts/mavis-drive-bridge.ps1 -Publish` |
| Corp trunchiat și `scope` necunoscut → **refuz** (exit 2) | `scripts/mavis-drive-bridge.ps1 -Publish` |
| `DUAL_CHANNEL_DRIVE` / `DUAL_CHANNEL_QUEUE` — „același TASK_ID" devine executabil | `scripts/mavis-drive-bridge.ps1 -Publish` |
| Poarta contractului, cu **contract viu** de pe discul Cloud | `scripts/queue-contract-check.ps1` |
| Auto-proba, 14 probe, falsificare în ambele sensuri | `scripts/queue-contract-check-selfcheck.ps1` |

```powershell
powershell -NoProfile -File scripts\queue-contract-check.ps1
```
→ `QUEUE_PROBLEMS=0 UNKNOWN=0` · `TICKETS=2` · `CONTRACT_DRIFT=NO` ·
`UNRECOGNISED_HEADERS=0` · `DONE_DIR=present` · **EXIT 0**

Detalii: `docs/CONTRACT-CLOUD-QUEUE.md` · `docs/BRIDGE-LOCAL-CLOUD.md` §10 ·
`docs/STARE-MASURATA-CI-2026-10-27.md` §9 · `DOCTRINA-CI.md` §9.7

---

## Instrumentul combinării istoricului — măsurat (2026-10-27)

> **Aditiv.** Nimic din secțiunile de mai sus nu se rescrie.

Repo-ul CI e lucrat **în paralel** de alt AI (CD). Deci există două istorice,
iar combinarea lor a fost o **alegere** fără măsurătoare. Acum are instrument:
`scripts/merge-check.ps1` — **dry-run**: nu atinge arborele de lucru, nu
creează commit, nu împinge nimic.

```powershell
powershell -NoProfile -File scripts\merge-check.ps1
```
→ `REMOTE_STATE=LIVE` · `DIVERGENCE_BEHIND=5 DIVERGENCE_AHEAD=24` ·
`MERGE_CLEAN=yes` · `CONFLICT_FILES=0` · arborele `8b11d68…` ·
`VERDICT=curat - o singura operatie de combinare, fara rezolvare manuala` ·
**EXIT 0**

| Ieșire | Ce înseamnă |
|---|---|
| `0` | merge curat — o singură operație, fără rezolvare manuală |
| `1` | conflict — fișierele sunt **numite**, cu rezolvare manuală |
| `2` | **nemăsurabil** — și asta **nu** e „curat" |

Auto-proba: `scripts/merge-check-selfcheck.ps1` — 5 probe pe repo reale
(conflictul e produs de git, nu simulat) → `MERGE_GATE_PROBLEMS=0 UNKNOWN=0
FALSIFIED=5`, EXIT 0. Falsificare în sens invers: poarta **stricată pe
copie** → `MERGE_GATE_PROBLEMS=3`, `POARTA A BLOCAT`, exit 1 — iar poarta
reală rămâne neatinsă (hash identic înainte și după).

Detalii: `docs/MAPARE-FOLDERE.md` §10 · `docs/WORKFLOWS.md` W11 ·
`docs/STARE-MASURATA-CI-2026-10-27.md` §10 · `DOCTRINA-CI.md` §9.8

---

## Livrarea cozii — reparată și măsurată (2026-10-27, ~06:40)

> **Aditiv.** Nimic din secțiunile de mai sus nu se rescrie.

> **O coadă poate fi impecabil formată și complet absentă.** Poarta
> verifica **forma** cozii și raporta sănătate pentru o coadă pe care nu o
> citea nimeni.

Contractul consumatorului, citit de pe discul lui Cloud, spune că Cloud-ul
face `git pull --rebase origin main` în **propriul repo** și citește
`QUEUE/TASKS-FOR-CLOUD.md` de acolo. Publisherul scria canalul secundar în
repo-ul **CI**.

| Măsurat, înainte | Valoare |
|---|---|
| `TASK_ID`-uri în coada locală (CI) | **2** |
| `TASK_ID`-uri în coada pe care Cloud-ul o citește | **0** |
| Poarta contractului | `QUEUE_PROBLEMS=0` — **verde, greșit** |

### Reparare

| Ce | Unde |
|---|---|
| Livrarea în repo-ul Cloud-ului: sync → scriere → secrete → commit → push → verificare | `scripts/queue-deliver.ps1` |
| Parserul cozii, **o singură implementare** pentru poartă și livrare | `scripts/queue-lib.ps1` |
| Poarta vede absența: fiecare `TASK_ID` local trebuie să fie în coada **Cloud-ului**, la vârful remote-ului | `scripts/queue-contract-check.ps1` (proba `DELIVERY`) |
| Scanarea de secrete pe **dif**, nu pe tot indexul | `scripts/scan-staged-secrets.ps1 -StagedDiff` |
| Auto-proba livrării: **15 probe**, falsificare în ambele sensuri | `scripts/queue-deliver-selfcheck.ps1` |
| Auto-proba porții: **14 probe** (era 11) | `scripts/queue-contract-check-selfcheck.ps1` |

### Măsurat, după

| | |
|---|---|
| `TASK_ID`-uri livrate | **2** |
| Commit în `MAVIS-CLOUD` | `4a88879` |
| `REMOTE_HEAD` = `LOCAL_HEAD` | `4a88879` · `ls-remote` confirmat |
| Poarta contractului | `DELIVERED=2/2` · `QUEUE_PROBLEMS=0 UNKNOWN=0` · **EXIT 0** |

### Două defecte de poartă reparate în drum

1. **Publisherul refuza calea prin joncțiune.** Compara două șiruri: calea
   dată (C:\…\projects\…) și rădăcina reală (E:\Google\GDrive\…). Prin
   joncțiune nu se potrivesc niciodată — deci publisherul refuza chiar
   repo-ul pentru care a fost scris, iar auto-proba lui cădea cu 7 probleme.
   Reparat cu `git rev-parse --show-prefix`: e gol **exact** când calea dată
   e rădăcina repo-ului, iar joncțiunile, literele de disc, majusculele și
   slash-urile sunt rezolvate de git, pentru că e întrebarea lui.
2. **Scannerul de secrete bloca false.** Scana tot indexul repo-ului și
   găsea 9 tipuri de token în documentație **deja publicată** (exemplele
   oficiale din fișierele Cloud-ului). O acuzație falsă costă mai mult
   decât un secret ratat. Modul `-StagedDiff` întreabă ce trebuie întrebat:
   introduce **această** schimbare un secret?

Detalii: `docs/BRIDGE-LOCAL-CLOUD.md` §11 · `docs/WORKFLOWS.md` W14 ·
`docs/CONTRACT-CLOUD-QUEUE.md`.

---

## Puntea bidirecțională, `Google_Access` și filtrele Gmail — starea măsurată (2026-10-27, ~09:00)

> **Aditiv.** Nimic din secțiunile de mai sus nu se rescrie.

| | |
|---|---|
| Canal primar | **Google Drive** — `BRIDGE-DRIVE/`, cloud_id `1V87h9Pbw52chSVNkxQ_NNuMh-CLfZeuI` |
| Canal secundar | **GitHub** — `QUEUE/TASKS-FOR-CLOUD.md`, scris simultan |
| Puntea | **bidirecțională**: **3** răspunsuri primite de la Cloud, 2 trimise înapoi |
| Coada | `TICKETS=5` · `DELIVERED=5/5` · `QUEUE_PROBLEMS=0 UNKNOWN=0` · **coada e închisă**: 5/5 marcate `[x]` de Cloud |
| Container Google | `Google_Access` · `running/healthy` · FailingStreak 0 · 25 unelte · grant live (9 scope-uri) |
| Sursa lui | `tools\google-access\` în GitHub → **reconstruibil**, credential exclus |
| Filtre Gmail `MAVIS/*` | **5 din 5 reparate** (14 neatinse) |
| Repo-uri | `MAVIS-OPTIMUS-CI` `5c4e1cf` · `MAVIS-CLOUD` `3e5a0a7` — ambele `= origin/main`, divergență `0 0` |

**O regulă reparată care conta:** transcrierile de sesiune au fost **renumerite
în Drive** (`chats/` → `Google_Connect/`), deci `.gitignore` nu mai le excludea
pe niciun nume — iar `scripts\mavis-sync.ps1:189` face `git add -A` + commit
automat: următoarea rulare a punții zilnice ar fi pus **conținut personal**
într-un repo **public**. Regula acoperă acum ambele nume, plus numele marcant
al raftului.

Detalii: `docs/STARE-MASURATA-CI-2026-10-27.md` §13 ·
`docs/HANDOFF-CD-2026-10-27-PUNTEA-DRIVE-PRIMARA-GOOGLE-ACCESS.md` ·
`docs/MAPARE-FOLDERE.md` §11

