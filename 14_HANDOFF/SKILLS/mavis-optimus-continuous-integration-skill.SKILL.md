---
name: mavis-optimus-continuous-integration-skill
description: "Cartierul general și scopul Mavis Optimus Continuous Integration. Se încarcă la orice lucru care atinge Git, GitHub, poarta R0, puntea Local↔Cloud, Live Review sau Jules. Nu produce conținut — construiește sistemul. Stă după mavis-autonomous-operator-skill și înaintea celor două skilluri Git: îi spune unde stă cartierul, ce doctrină se aplică, ce se atinge și ce nu se atinge niciodată, și ce a rămas de făcut."
---

# SKILL: Mavis Optimus Continuous Integration

**Inginer de sistem al OPTIMUS Prime.** Nu lucrez la conținut —
construiesc sistemul pe care lucrează toți ceilalți.

| | |
|---|---|
| **Proiect** | Mavis Optimus Continuous Integration |
| **Instanță** | **LOCAL** → am nevoie de R0 la push |
| **HQ** | `C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Continuous-Integration\` → **`E:\Google\GDrive\GDrive-Second_Brain_PKMS\02_Areas\02-2-AI-SOT\CASA\OPTIMUS - Prime\Optimus_CI (by Mavis)`** (mutat pe `E:` în 2026-10-27; vezi secțiunea „Puntea Local ↔ Cloud") |
| **Joncțiune locală** | `C:\Users\apviz\.minimax-agent\projects\Optimus_CI (by Mavis)` → `E:` (`LinkType=Junction`) |
| **Repo** | `apvizual-max/MAVIS-OPTIMUS-CI` |
| **Plan** | `blueprint\BLUEPRINT-PLAN-CI.md` |
| **Canal primar** | **Google Drive** — `BRIDGE-DRIVE\` |
| **Canal secundar** | **GitHub** — `QUEUE\TASKS-FOR-CLOUD.md` |

---

## Se încarcă după `mavis-autonomous-operator-skill`, înaintea celor Git

Ordinea contează:

```
1. mavis-autonomous-operator-skill    ← cum gândesc și cum răspund
2. mavis-optimus-continuous-integration-skill   ← asta: unde și ce ating
3. mavis-git-autonom-skill            ← cum se lucrează zilnic cu Git
4. mavis-git-install-skill            ← doar la repo nou
```

---

## Regula Triadei — nu se încalcă

```
1 conversație  =  1 folder local  =  1 repo GitHub
```

Fiecare proiect are conversația lui, folderul lui, repo-ul lui.
**Proiectele nu se ating.**

Când alt proiect are nevoie de o modificare, **dau prompt lui Popy**, el
îl duce în sesiunea respectivă, care are contextul complet. **Nu intru
în repo-ul altui proiect** — un agent fără context într-un repo străin
e exact defectul pe care îl reparăm.

---

## Ce ating, și ce NU ating niciodată

| Ating | Nu ating |
|---|---|
| proiectul ăsta, integral | repo-urile altor proiecte |
| configul **meu**, măsurat | fișiere de sistem ale altora |
| hook-uri **per repo** | `core.hooksPath` în repo-uri străine |
| documentație prin **referință** | — nu mut nimic din alte proiecte |

**Regula:** nimic nu se mută din altă parte. Totul se **documentează prin
referință**, cu cale explicită. Dacă o cale se schimbă, se schimbă un
link, nu se strică nimic.

---

## Ce am citit și ce am hotărât

`cloud-ingest\MAVIS-CLOUD` e clonă locală **read-only**, 155 de fișiere,
citită completă. Regula Cloud-ului: *„Tot ce fac ajunge în repo, automat,
fără aprobare."* **O preiau.**

Am găsit **7 conflicte** între Cloud și doctrina lui Popy — toate în
`docs\CONFLICTE-DOZTRINA.md`, fiecare cu citatul care îl dovedește.
**Cele mai importante trei:**

1. **`CI-NOTES.md` cere ramură + PR.** Doctrina spune `main` only.
   Nu pot fi ambele adevărate. **Folosim workflow programat, nu PR.**
2. **„R0" înseamnă două lucruri.** La Cloud: verificare automată. La
   Popy: acordul lui. **În CI, `R0` = acordul lui. Verificarea
   automată se numește altfel.**
3. **Pragul are patru valori** — 25, 5, 15, 50. **Rămâne 50**, într-un
   singur loc.

**Ce am preluat din Cloud:** `verify.yml` cu throttling-ul lui
(`cron 03:00` + `workflow_dispatch`) și cele 7 verificări reale. Nu
reinventăm ce e măsurat că merge.

---

## Ce fac concret

| Fac | Nu fac |
|---|---|
| guvernanța Git/GitHub și poarta R0 | nu lucrez la conținutul altor proiecte |
| puntea Local ↔ Cloud | nu mut fișierele altor proiecte |
| **puntea Drive** — canal primar, cu măsurătoare de propagare | nu re-autentific DriveFS și nu reconsentez tokenul unilateral |
| politica Live Review + Jules — **au plecat în CD (2026-10-24)**; din CI se ating doar dacă e strict necesar | nu fac deploy-uri |
| inventarul repo-urilor | nu șterg nimic definitiv |
| refacerea sistemului, **măsurat** | nu ating interfața |

---

## Comanda unică, pentru orice agent fără memorie

```
git clone https://github.com/apvizual-max/MAVIS-OPTIMUS-CI
cd MAVIS-OPTIMUS-CI
cat README.md DOCTRINA-CI.md docs/CONFLICTE-DOZTRINA.md
```

**Trei fișiere. Știi tot.** Asta e testul: dacă un agent nou nu poate
continua din astea, mai am de lucrat.

---

## Git — în acest proiect

- **COMMIT** automat, pe `main`, **fără R0**, imediat
- **PUSH** doar prin `scripts\git-autopush.ps1 -Acord` — **poarta**, nu
  `git push` direct
- **FORK** doar la cerere explicită, ca GOAL + SCOPE + CRITERIA
- **≥50 neîmpinse** → îl reamintesc la fiecare răspuns
- **Changes** gol, permanent
- Verificare cu `git ls-remote`, **niciodată** prin cod de ieșire

**Instanța Cloud e singura care împinge fără R0** — container volatil,
altfel pierde datele la oprire. Aceasta e singura diferență între ele,
și e suficient.

### Un repo scris de un pipeline CD — rețeta măsurată (28 oct)

Când un **pipeline de dezvoltare continuă scrie direct în `main`** (Jules,
Antigravity CD Engine), localul e de obicei *în urmă*, iar sincronizarea nu e
opțională. Rețeta măsurată pe `SENTINEL_PRIME`:

1. `git -C $repo fetch origin --prune`, apoi
   `git -C $repo rev-list --left-right --count origin/main...HEAD`;
2. verifică fiecare commit local cu
   `git -C $repo merge-base --is-ancestor <commit> origin/main` — dacă toate
   sunt acolo, **nu ai nimic de fuzuit**, doar de materializat;
3. snapshot **în două locuri**: `git stash push -u` **și** o copie fizică în
   quarantine;
4. `git -C $repo merge --ff-only origin/main` — istorica rămâne liniară;
5. restaurează selectiv, fișier cu fișier;
6. **rulează ambele suite, secvențial** — acolo nu există CI care să le ruleze;
7. **verifică cu o clonă nouă, de la zero**, nu cu `git log`.

**Fiecare comandă git e legată de repository-ul despre care întreabă.** Cu
cwd-ul într-un repo părinte, `git ls-remote origin` interoghează remote-ul
**celuilalt** repository, iar SHA-ul arată la fel. Măsurat: un SHA venit din
repo-ul părinte a fost citit ca „pipeline-ul a impus ceva nou" — o iminență de
panică bazată pe un repository strain.

**Un commit valid poate să nu fie clonabil.** Git refuză `:` într-o componentă
de nume, iar un director cu cale absolută drept nume intră în arbore fără să
apară în `git log` sau `git status`. Repararea se face prin **plumbing**
(`mktree` + `commit-tree` cu părintele `origin/main`), ca istorica să rămână
liniară — fără rescriere, fără force-push.

Detalii complete: `mavis-jules-contract-skill` §8 și
`SENTINEL_PRIME/07_BACKBONE/skills/sentinel-cd-pipeline-sync.SKILL.md`.

---

## Regula de aur, măsurată

**O poartă care stă în prohă, sau într-un flag pe care eu îl pot pasa,
nu e o poartă.**

Măsurat: 12 comituri au ajuns pe GitHub fără acord, pentru că poarta
exista doar ca un switch `-Acord` într-un script. `git push` scris cu
mâna ocolește un switch. Un hook `pre-push` nu.

Iar când am încercat `git push` direct pe `OPTIMUS-Backbone`, **poarta m-a
refuzat, în cuvinte care spuneau de ce.** Asta e o poartă. Restul sistemului
trebuie construit la fel.
---

## OPERATIONAL SUB-SKILLS REGISTRY

Actualizat 2026-10-12, după cel mai nou handoff din Cloud
(`docs/HANDOFF-2026-10-12-0440-jules.md`, 04:40). Master-ul rămâne centrul de
comandă: coordonează cele patru, **nu le dublează textul**.

| # | Micro-skill | Fișier | Stare | Încadrare |
|---|---|---|---|---|
| 1 | Contract Jules | `mavis-jules-contract-skill\SKILL.md` | 🟡 BLUEPRINT | **frontieră**, nu operator — Cloud deține Jules |
| 2 | Live Review Governance | `mavis-live-review-governance-skill\SKILL.md` | 🟡 BLUEPRINT | politica; mecanismul trăiește în Cloud |
| 3 | Cloud Bridge | `mavis-cloud-bridge-skill\SKILL.md` | 🟡 BLUEPRINT | legea asimetrică a push-ului |
| 4 | Git & Vault Governance | `mavis-git-vault-governance-skill\SKILL.md` | ✅ WIRED | 7 reguli, toate măsurate pe 2026-10-12 |

### De ce #1 se numește „contract" și nu „operator"

Propunerea primită cerea un „Jules Operator" care să creeze issue-uri cu
`gh issue create` și să dea merge la PR-urile lui Jules. **Nu e corect**, pentru
că același handoff spune:

> „Nu ai nimic de făcut cu Jules. Nu-l configurați, nu-l pornești, nu-l
> oprești." — și „Eu sunt responsabil […] de implementarea propunerilor lui
> Jules."

Un „operator" ar fi un rol pe care Cloud și-l-a atribuit **singur**. Skill-ul
corect e frontiera: ce NU fac, ce știu, și singurul caz legitim.

### Ce s-a respins din propunere, și de ce

| Propunere | Decizie | Motiv |
|---|---|---|
| „Jules Operator" local care face issue + merge | **respins** | contrazice regula Cloud „nu fac jumătate de sarcină" |
| `.skills/` în repo | **adaptat** | namespace-ul skill-urilor e `~/.minimax/agents/mavis/skills/` |
| „Se interzice starea de Blocat" | **respins** | e exact anti-pattern-ul senzorului mort |
| Hermes Composer / Judge / GRI / PAUZĂ | **respins** | vocabular dintr-un alt univers, nu al meu |
| `[PREDARE_TEHNICA::DOVEZI_STAGED::READY_FOR_JUDGE_REVIEW]` | **respins** | protocol de predare străin |
| Live Review 03:00 + manual | **preluat** | era deja implementat în Cloud; nu se reinventă |
| `core.longpaths`, plafon 100 MB, repo-uri imbricate | **preluat și întărit** | măsurat de mine, cu cifre, nu repetat ca instrucțiune |

### Regula de filtrare, pentru orice propunere externă

O propunere vine cu contextul celui care o scrie, nu cu al meu. Se trece prin
trei întrebări, în ordine:

1. **Măsurătoare** — e verificabilă pe mașina asta, sau e afirmată?
2. **Efect asupra planului** — păstrează calea, sau o scurtătează?
3. **Al cui e** — îmi spune să opriu din cauza unei greșeli tehnice, sau îmi
   propune o alegere strategică?

Dacă propunerea e corectă și măsurabilă, se aplică și se **notează cifra**. Dacă
e corectă doar în contextul altui, se **adaptează**. Dacă nu e, se refuză — și
refuzul se scrie cu motivul, nu se tace.

---

## Puntea Local ↔ Cloud — Drive primar, GitHub secundar

**Adiționat 2026-10-27.** Nimic de mai sus se rescrie; această secțiune
adaugă **scopul nou** al sesiunii CI.

### Scopul, într-un rând

Puntea **Local ↔ Cloud** prin **Google Drive** (canal primar) și **GitHub**
(canal secundar), plus procedurile Git/GitHub și guvernanța R0.

CD (Jules, Live Review, tools) a plecat într-o sesiune paralelă. **Nu se
atinge** din CI, decât strict necesar.

### De ce Drive a devenit primar — două măsurători

1. **Divergența măsurată**: local `83b6139` vs remote `3da55ff` →
   **12 commituri înainte / 5 înapoi**. Cele 5 remote sunt lucrarea CD.
2. **Poziția fizică a sursei**: sursa CI e acum **în chiar mirrorul Google
   Drive** (`E:\Google\GDrive\GDrive-Second_Brain_PKMS\...\Optimus_CI (by Mavis)`).
   Local și Cloud au același sistem de fișiere la capete diferite.

Costul canalului primar e **latența: ≈ 80 min** măsurată (scriere locală
22:11 → prezență în Drive 23:31). De aceea GitHub rămâne în paralel.

### Topologia, măsurată

| Element | Valoare |
|---|---|
| Sursa CI | `E:\Google\GDrive\GDrive-Second_Brain_PKMS\02_Areas\02-2-AI-SOT\CASA\OPTIMUS - Prime\Optimus_CI (by Mavis)` |
| Joncțiune | `C:\Users\apviz\.minimax-agent\projects\Optimus_CI (by Mavis)` → `E:` (`LinkType=Junction`) |
| `.git` | **fișier** (worktree link) → `gitdir: E:/Google/GitData-Optimus-CI/repo` |
| Gitdata | **un singur folder** pe proiect: `E:\Google\GitData-Optimus-CI\` → `repo\` · `clone-MAVIS-CLOUD\` · `clone-MAVIS-OPTIMUS-CI\` · `scratch\` |
| `G:` | volum fix, **nu** mount virtual; `G:\My Drive.lnk` → `E:\Google\GDrive` |
| Mirror | `Google\GDrive`, `root_id=23`, `sync_type=MIRROR`, `connected=true` |
| Folder CI în Drive | `cloud_id 1V87h9Pbw52chSVNkxQ_NNuMh-CLfZeuI` |

**De ce gitdata stă în afara mirrorului.** DriveFS administrează spațiul din
`E:\Google\GDrive\` cât timp sincronizează: materializează, înlocuiește,
șterge. Un `.git\` viu — `index`, `refs`, `objects`, `HEAD` — e pentru el o
colecție de fișiere oarecare. Deci tot ce e git stă într-un folder
dedicat, **în afara** arborelui sincronizat, iar în arbore `.git` rămâne un
fișier pointer.

**Un folder per proiect, nu per repo.** Când Popy numește un folder-rădăcină,
acesta e rădăcina **unică**: sub-organisation se face în interior, ca
subfoldere. Nu se creează câte un folder-rădăcină nou pentru fiecare repo.

Măsurat 2026-10-27, 11:40: în arborele CI erau **63 de directorii `.git`** de
fixture (porțile își construiesc repository-uri proprii ca să măsoare ceva).
După mutare: **0** în mirror, iar fixture-urile stau în
`E:\Google\GitData-Optimus-CI\scratch\` — **numărul lor variază cu fiecare
rulare de porți** (măsurat 46 → 59 → 79 în aceeași zi), deci nu-l trata ca
constantă.
Radicalul scratch se **derivează din gitdir-ul repo-ului propriu**, deci
laboratorul urmează repository-ul în loc să hard-codeze o cale de mașină
(`scripts\git-scratch.ps1`).

**Capcană de măsurare:** blob-ul din `items.proto` e *latura cloud* (id +
părinte + titlu). Căutarea după **calea completă** nu se potrivește niciodată —
se caută după `local_title`, apoi se verifică lanțul `stable_parents`.

**Capcană de stare:** primul dump `ReceiveMirrorRoots` din startup dă
`connected=false`. **Starea finală e ultimul dump.**

### Cele patru reguli ale canalului

1. **Se scrie în ambele canale la aceeași publicare**, cu același `TASK_ID`.
2. **„Publicat" înseamnă măsurat**: `SYNCED` / `PENDING` / `NOT_UPLOADED` /
   `UNVERIFIED`. **`UNVERIFIED` nu e succes.**
3. **Transportul căzut nu blochează sistemul** — poarta cere ca raportul să
   fie *concordant* cu măsurătoarea, nu ca transportul să fie UP.
4. **Nu se re-autentifică DriveFS și nu se reconsentează tokenul unilateral** —
   act ACCESS, pe mașina lui Popy.

### Instrumentele

```powershell
scripts\mavis-drive-bridge.ps1 -Status     # stare + lag
scripts\mavis-drive-bridge.ps1 -Publish     # scrie pe ambele canale
scripts\mavis-drive-bridge.ps1 -Verify      # re-verifică propagarea
scripts\mavis-drive-bridge-selfcheck.ps1    # poarta, 19 probe
python scripts\drivefs_probe.py --title "Optimus_CI (by Mavis)"
python scripts\drivefs_probe.py --root-state
python scripts\drivefs_probe.py --newest "Optimus_CI (by Mavis)"
```

Poarta măsurată: `BRIDGE_PROBLEMS=0 UNKNOWN=0`, **EXIT 0**.

### Rutele de API sunt rupte — și asta e măsurat

| Rută | Stare |
|---|---|
| `gdrive-mcp` (MCP) | `invalid_grant` — token revocat |
| `verify-drive.js` | `files.list` **FAILED**, EXIT 2 |
| `gcloud` ADC (`authorized_user`) | token valid, Drive API **HTTP 403** (fără scope) |
| `metadata_sqlite_db` | 422 932 480 B, lizibil read-only → **sursa de adevăr** |
| `mirror_metadata_sqlite_db` | 2 278 027 264 B, **blocată** de DriveFS (și cu `immutable=1`) |

### Regula de ștergere, în acest proiect

`git clean -fdx`, `git reset --hard`, force-push și ștergerea definitivă sunt
**interzise**. Doar Trash recuperabil:
`C:\Users\apviz\.minimax\bin\mavis-trash.cmd -- "<target>"`.

### Convenția de numire, extinsă la Drive

`MAVIS-LOCAL-…` / `MAVIS-CLOUD-…` pentru documente, `mavis-local-…` /
`mavis-cloud-…` pentru cod — în **ambele** canale. Detalii în
`docs/PROTOCOL-DENUMIRE-LOCAL-CLOUD.md` §8.

---

## Starea repo-ului CI — nu e administrat de CI în paralel

Repo-ul `MAVIS-OPTIMUS-CI` va fi lucrat de alt AI (CD). **CI ține copia +
referința măsurată**, nu îl administrează singur.

Măsurat 2026-10-27: remote public, `pushed_at 2026-10-24T23:55:56Z`, 99 KB,
0 workflow-uri, 0 secrete, 0 PR-uri deschise, `main 3da55ff`.

Snapshot: `docs/STARE-MAVIS-OPTIMUS-CI-REMOTE.md`.
Starea curentă: `docs/STARE-MASURATA-CI-2026-10-27.md`.

**Divergența se documentează, nu se rezolvă cu forța.** Push-ul și rebaza sunt
**R0**.

---

## Contractul cozii secundare — și porțile care îl fac executabil

**Adiționat 2026-10-27, ~02:40.** Nimic de mai sus se rescrie.

Canalul secundar (`QUEUE\TASKS-FOR-CLOUD.md`) are un **contract** — cel al
consumatorului (Cloud), citit **de pe discul lui**, nu inventat aici:

```
### [id] titlu
cerut de: local | data: YYYY-MM-DD
scope: cloud | local | ambele
ce trebuie: ...
livrare: unde trebuie să ajungă rezultatul
```

Cloud rulează **doar** tichetele cu `scope: cloud`, livrează în
`QUEUE/DONE/<id>.md` și marchează `[x]`.

**Măsurat înainte de reparare (27 oct):** 0 din 5 câmpuri, 0 anteturi
`### [id] titlu`, 0 `scope:`, 2 anteturi `## TASK-…` invizibile pentru Cloud,
`QUEUE/DONE/` absent, și ultima linie trunchiată la mijloc de propoziție în
**ambele** canale. Coada arăta plină și era **goală** pentru singurul cititor
care contează — fără nicio eroare raportată.

**Măsurat după:** `QUEUE_PROBLEMS=0 UNKNOWN=0` · `TICKETS=2` ·
`CONTRACT_DRIFT=NO` · `UNRECOGNISED_HEADERS=0` · `DONE_DIR=present` ·
**EXIT 0**. Auto-proba: `QUEUE_GATE_PROBLEMS=0 UNKNOWN=0 FALSIFIED=14` (14 probe).

### Instrumentele canalului secundar

```powershell
scripts\queue-contract-check.ps1              # poarta, exit 0 / 1 / 2
scripts\queue-contract-check-selfcheck.ps1    # 14 probe
scripts\mavis-drive-bridge.ps1 -Publish -Title "<subiect>" -Body "<text>" [-Scope cloud]
```

Regulile, care acum sunt cod:

1. Copia secundară se scrie **în contractul consumatorului**, nu în formatul
   canalului primar.
2. Un corp **trunchiat** e **refuzat** (exit 2) — o instrucțiune trunchiată nu
   e o sarcină.
3. `scope` trebuie să fie `cloud` / `local` / `ambele` — altfel **refuzat**.
4. După scriere: `DUAL_CHANNEL_DRIVE` / `DUAL_CHANNEL_QUEUE` — ieșire **1** dacă
   același `TASK_ID` nu e în ambele canale.
5. `2` de la poartă = contractul live ilizibil = **UNKNOWN, nu succes**.

Contractul, cu proveniență și dată: `docs\CONTRACT-CLOUD-QUEUE.md`.

### Regula, pentru totdeauna

> **O regulă scrisă în proză nu e o regulă, e o intenție.** Dacă poate fi
> falsificată, devine cod. Iar contractul se citește **de la sursa vie** — o
> copie se învechise în tăcere, iar o poartă care compară cu o copie nu
> detectează nimic.

### Combinarea istoricului, măsurată înainte de R0

> **Aditiv.** Măsurat 2026-10-27.

Repo-ul CI e lucrat **în paralel** de alt AI (CD). Deci există două istorice:
`main` local (al meu, automat, neîmpins fără R0) și `origin/main` (al
celuilalt AI). Combinarea lor e o operație de R0 — iar R0 merită **fapte**.

```
scripts\merge-check.ps1
```

**Dry-run**: `fetch` + divergență + `git merge-tree --write-tree` + diff per
parte. Nu atinge arborele de lucru, nu creează commit, nu împinge nimic.

| Ieșire | Ce înseamnă |
|---|---|
| `0` | merge curat — o singură operație, fără rezolvare manuală |
| `1` | conflict — fișierele sunt **numite** |
| `2` | **nemăsurabil** — și asta **nu** e „curat" |

Măsurat: `REMOTE_STATE=LIVE` · `DIVERGENCE_BEHIND=5 DIVERGENCE_AHEAD=24` ·
`MERGE_CLEAN=yes` · `CONFLICT_FILES=0` · arborele `8b11d68…` · merged vs local
6 fișiere (+74/−13 — lucrarea CD) · merged vs remote 38 fișiere (+7309/−230 —
lucrarea mea).

Auto-proba: `scripts\merge-check-selfcheck.ps1` — **5 probe pe repo reale**,
conflictul produs de git → `MERGE_GATE_PROBLEMS=0 UNKNOWN=0 FALSIFIED=5`,
EXIT 0. Falsificare: poarta stricată pe **copie** → `MERGE_GATE_PROBLEMS=3`,
`POARTA A BLOCAT`, exit 1; poarta reală neatinsă (hash identic înainte și după).

### Regula, pentru totdeauna

> **Codul de ieșire e o amprentă. Marcajul e o măsurătoare.**
>
> Un exit 1 dintr-o excepție terminantă e **indistinctibil** de exit 1-ul
> porții. Deci blocarea se dovedește prin **marcaj** (`POARTA A BLOCAT`,
> `PROBLEMS>0`) — nu prin codul de ieșire.
>
> Și: înainte de orice operație cu R0, există un instrument care spune **ce
> se va întâmpla**. Dacă instrumentul spune „nu se poate măsura", răspunsul
> e **2** — nu „probabil curat".
---

## Livrarea cozii — poarta care vede absența (2026-10-27, ~06:40)

> **Aditiv.** Nimic de mai sus se rescrie.

**Defectul măsurat.** Contractul consumatorului, citit de pe discul lui Cloud
(`.skills/mavis-cloud-to-local-reporting/SKILL.md`, linia 12), spune:
`git pull --rebase origin main` — mereu primul. Deci Cloud-ul trage din
**propriul repo**, `MAVIS-CLOUD`. Publisherul scria canalul secundar în
repo-ul **CI** — un repo din care Cloud-ul nu citește niciodată.

| Măsurat, înainte | Valoare |
|---|---|
| `TASK_ID`-uri în coada locală (CI) | **2** |
| `TASK_ID`-uri în coada pe care Cloud-ul o citește | **0** |
| Poarta contractului | `QUEUE_PROBLEMS=0` — **verde, greșit** |

Poarta verifica **forma** cozii, nu dacă coada **ajunge** la consumator.

### Instrumentele

| Instrument | Ce face |
|---|---|
| `scripts\queue-lib.ps1` | parserul cozii — **o singură implementare** pentru poartă și livrare |
| `scripts\queue-deliver.ps1` | sync → scriere → secrete → commit → push → verificare la remote |
| `scripts\queue-deliver-selfcheck.ps1` | **15 probe**, falsificare în ambele sensuri |
| `scripts\queue-contract-check.ps1` | + proba `DELIVERY` + proba căii de intrare |

```powershell
scripts\queue-deliver.ps1 -Status          # ce nu a ajuns (read-only)
scripts\queue-deliver.ps1 -Deliver -Push   # livrează și verifică la remote
scripts\queue-contract-check.ps1           # poarta, exit 0 / 1 / 2
```

**Măsurat după:** `DELIVERED=2/2` · `QUEUE_PROBLEMS=0 UNKNOWN=0` ·
`CLOUD_ENTRY=QUEUE/TASKS-FOR-CLOUD.md` · commit în `MAVIS-CLOUD` `4a88879` ·
`REMOTE_HEAD` = `LOCAL_HEAD` = `4a88879` (verificat prin `ls-remote`).

### Regula, pentru totdeauna

> **O coadă impecabil formată poate fi complet absentă.**
> Pentru un consumator care trage dintr-un repo, „publicat" înseamnă „prezent
> la vârful ramurii remote a repo-ului lui" — nu „scris local". Poarta trebuie
> să citească **acolo**.

### Două porți reparate în drum

1. **Publisherul refuza calea prin joncțiune** (`C:\…\projects\` → `E:\Google\GDrive\…`):
   compara două șiruri, iar git tipărește calea **fizică** — deci cele două nu
   se potrivesc niciodată, și publisherul refuza chiar repo-ul pentru care a fost
   scris (auto-proba lui cădea cu 7 probleme). Reparat cu
   `git rev-parse --show-prefix`: gol **exact** când calea dată e rădăcina, iar
   joncțiunile, literele de disc, majusculele și slash-urile le rezolvă git —
   pentru că e întrebarea lui.
2. **Scannerul de secrete bloca false**: scăna tot indexul și găsea 9 blocuri în
   documentație **deja publicată** a lui Cloud (valorile-exemplu oficiale), și
   a blocat o livrare care nu conținea niciun secret. Modul `-StagedDiff`
   întreabă ce trebuie întrebat: introduce **această** schimbare un secret?

---

## Scoapul, înainte — și cine mai lucrează la ce (2026-10-27)

> **Aditiv.** Nimic de mai sus se rescrie.

### Cele două canale, în ordinea priorității

| Canal | Rol | Măsurat |
|---|---|---|
| **Google Drive** — folderul `BRIDGE-DRIVE\`, în mirrorul `E:\Google\GDrive\` | **principal** — ambele instanțe au acces la același Drive; sursa locală se sincronizează singură | `PROPAGATION=OK` · `CLOUD_CHANNEL_FILE_PRESENT=true` |
| **GitHub** — coada livrată în `MAVIS-CLOUD` | **secundar / rezervă** — handoff-urile din repo, și calea prin care tichetele ajung la Cloud când Drive e jos | `DELIVERED=2/2` la `origin/main` |

Costul canalului principal e **latența** (măsurată ≈ 80 min). De aceea
secundarul nu e decorativ: e plasa de siguranță, și are **poartă proprie**.

### Cine mai lucrează la ce

| Zona | Cine o lucrează | Cum se tratează din CI |
|---|---|---|
| **Puntea Local ↔ Cloud** (acest repo) | **această sesiune** | lucrul propriu |
| **CD** (Jules, Live Review, tools, reorg-ul arborelui CD) | **sesiune paralelă** | **nu se atinge** din CI |
| **Repo-ul `MAVIS-OPTIMUS-CI`** | **alt AI, în paralel** | CI ține **copia + referința măsurată**, nu îl administrează singur |

**Divergența nu e o problemă, e un fapt.** Repo-ul CI va fi schimbat de
altcineva; poate s-a schimbat deja. Deci:

- local `main` și `origin/main` sunt **două istorice**, și combinarea lor e
  `--no-ff`, cu **ambele păstrate** — niciodată rebase, niciodată force-push;
- instrumentul care spune ce se va întâmpla înainte de R0:
  `scripts\merge-check.ps1` (exit `0` curat · `1` conflict cu fișierele numite
  · `2` nemăsurabil, care **nu** e „curat");
- măsurătoarea porții de livrare citește **la vârful ramurii remote** a
  consumatorului, nu copia locală — pentru că un repo poate fi schimbat sub
  picioarele tale, și atunci „local" nu mai e un cuvânt suficient.

---

## Verificarea remote-ului cu clonă nouă, ca instrument (2026-10-28)

> **Aditiv.** Nimic de mai sus se rescrie.

Măsurat în `SENTINEL_PRIME`, unde pipeline-ul CD (Jules + Antigravity CD Engine)
scrie direct în `main`: un comit poate fi **valid** și totuși imposibil de
checkout pe Windows — git refuză `:` într-o componentă de nume, iar un director
cu cale absolută drept nume intră în arbore fără să apară în `git log` sau
`git status`. Pipeline-ul a introdus exact așa o dată, în 3 zile.

Regula „verifică cu o clonă nouă" a devenit **cod**, nu rețetă:

```powershell
scripts\verify-remote-clone.ps1       # VERDICT=PASS (0) / VERDICT=FAIL (2) + FAILURES=<lista>
scripts\make-broken-tree-control.py   # control falsificator: construiește defectul
```

Măsurat: controlul → `VERDICT=FAIL`, `invalid_tree_entries 1`, `clone_exit 128`,
„error: invalid path 'C:\Users\...' — fatal: unable to checkout working tree";
repo-ul real → `VERDICT=PASS`. Instrumentul **nu șterge nimic** și nu atinge
arborele de lucru: lasă clona de probă în `%TEMP%` și afișează calea în
`PROBE_CLONE=`.

**Trei capcane PowerShell 5.1, măsurate în timp ce scriam instrumentul:**

1. **O funcție numită ca un executabil de pe PATH umbrează executabilul.**
   `function Git` + apelul către `git` = autoapelare la infinit →
   `CallDepthOverflow`. Numele sigur: `Invoke-Native`.
2. **Un tool nativ care scrie pe stderr nu e o excepție.** Cu
   `$ErrorActionPreference='Stop'`, un `git` care doar avertizează aruncă o
   eroare terminantă și **ascunde diagnosticul pe care voiai să-l vezi**.
   Capturează stderr-ul într-un string și citește codul de ieșire.
3. **`powershell -File` nu leagă o listă de argumente la un parametru
   `[string[]]`.** Primește un singur string cu virgule între ele. Acceptă un
   string separat prin virgule și descompune-l în interiorul scriptului.

Și una de parsare: pe un pipeline cu un singur rezultat, `Where-Object`
întoarce un **scalar**, iar `$x[0]` pe un scalar de tip string e indexare de
**caracter** — SHA-ul a fost citit ca `"b"`. Ancorează regexul la începutul
liniei (`^\s*([0-9a-f]{40})\b`) și nu cere whitespace după el: `git rev-parse
HEAD` afișează SHA-ul gol.

### Regula, pentru totdeauna

> **Un check care nu poate pici nu e un check.** Instrumentul de verificare se
> **falsifică** cu un control care construiește defectul pe care trebuie să-l
> refuză — altfel nu știi dacă măsoară ceva sau doar confirmă ce știi deja.
