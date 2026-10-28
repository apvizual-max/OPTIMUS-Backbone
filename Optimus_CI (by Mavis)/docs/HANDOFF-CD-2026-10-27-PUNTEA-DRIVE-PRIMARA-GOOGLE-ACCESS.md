# HANDOFF — CD (Jules / Live Review), 27 oct 2026, ~07:50 · actualizat ~08:15

> **Autor:** Mavis Local — sesiunea **CI** (puntea Local↔Cloud).
> **Pentru:** sesiunea CD — platforma Jules, Live Review, triaj.
> **Canon:** acest fișier e identic în `_Handoffs/` (CD) și în `docs/` (repo-ul
> CI). CD-ul e SOT-ul de dezvoltare; CI-ul e backup-ul și puntea.
> **Frontieră:** arborele CD **nu** a fost atins de mine în acest rând. Zero
> scrieri în `Optimus_CD (by Jules)/` în afara acestui folder `_Handoffs/`.
>
> **Actualizarea de ~08:15** adaugă, fără a rescrie nimic: răspunsul lui Mavis
> Cloud (§4.6), corecția unei măsurători din raportul lui (§4.7), livrarea
> corecției OAuth în `MAVIS-CLOUD` (§4.8), cele trei defecte reparate la
> sursa containerului (§1.6) și faptul că sursa containerului e acum în
> GitHub, deci reconstruibilă.

---

## 0. VERDICT

**Cele 9 task-uri de fundal eșuate sunt închise** — diagnosticate, cu dovezi,
în `docs/HANDOFF-TERMENARE-DEVELOPMENT-2026-10-27.md` (același fișier, identic
prin SHA256 în ambele locuri). Nu mai e lucru de făcut pe ele; nu erau nici
defecte ale platformei.

**Ce rămâne pentru CD e un bloc de 5 puncte (§3), toate delegate de azi** —
plus ce a apărut nou în acest rând (§4).

---

## 1. Ce s-a implementat și măsurat în CI (azi)

### 1.1 Livrarea cozii secundare — în repo-ul consumatorului

Contractul consumatorului (citit **de pe discul Cloud-ului**:
`MAVIS-CLOUD/.skills/mavis-cloud-to-local-reporting/SKILL.md`, linia 12) cere
`git pull --rebase origin main` **din propriul repo** al Cloud-ului. Deci
coada trăiește în `MAVIS-CLOUD`, nu într-un repo nou.

| Instrument | Ce face |
|---|---|
| `scripts/queue-lib.ps1` | parserul cozii în **O singură implementare** (poartă + livrare) |
| `scripts/queue-deliver.ps1` | sync → scriere → scan secrete pe dif → commit → push → verificare `ls-remote` **+ conținut la remote** |
| `scripts/queue-contract-check.ps1` | poarta: contract + **livrarea** (fiecare `TASK_ID` local trebuie să fie în coada Cloud-ului, la vârful remote-ului) |

**Măsurătorile de azi:** `DELIVERED=3/3` · `QUEUE_PROBLEMS=0 UNKNOWN=0` ·
`CLOUD_ENTRY=QUEUE/TASKS-FOR-CLOUD.md` · EXIT 0. Commitul de livrare în
`MAVIS-CLOUD`: `a6cece6` (remote = local, divergență 0/0).

**Zece defecte reale găsite și reparate** (tabelul complet în
`docs/STARE-MASURATA-CI-2026-10-27.md` §11.4) — dintre care: poarta verifica
**forma**, nu **livrarea** (verde peste o coadă absentă); `$push` local vs
`[switch]$Push` (pushul *rulea*, apoi scriptul murea cu exit 1); reluarea
adăuga ticheta a doua oară; publisherul refuza calea prin joncțiune C:→E:;
scannerul de secrete bloca false pe documentație deja publicată.

### 1.2 Puntea Drive — primară, măsurată

| Ce | Valoare măsurată (27 oct) |
|---|---|
| cloud_id al folderului | `1V87h9Pbw52chSVNkxQ_NNuMh-CLfZeuI` |
| Calea în Drive | `My Drive > GDrive-Second_Brain_PKMS > 02_Areas > 02-2-AI-SOT > CASA > OPTIMUS - Prime > Optimus_CI (by Mavis)` |
| Propagare | `PROPAGATION=OK` · lag 3,9 min la ultima scriere · `PENDING_OPERATIONS=0` |
| Transport | `TRANSPORT=UP` · `ACTIVE_CHANNEL=DRIVE` |
| Taskul zilnic | declanșator **07:30** (`StartBoundary 2026-10-12T07:30:00+02:00`, `StartWhenAvailable=True`) — de aceea logurile vechi apar la 08:30 |

### 1.3 Procedura nouă, decisă de Popy — și mesajul trimis lui Mavis Cloud

**Drive = puntea principală** (folderul de mai sus, canalul `BRIDGE-DRIVE/`).
**GitHub = canal secundar + memorie permanentă a sistemului**, citit la
fiecare start de sesiune, fiecare job automat și fiecare acțiune.

Mesajul a fost publicat **pe ambele canale, cu același `TASK_ID`**:
`TASK-2026-10-27-0735-procedura-nou-drive-e-puntea-principal-github-e-memoria-permanent-a-sistemului-scrie-raportul-de-operare-n-drive`.

Cerut lui Mavis Cloud: **raport de funcționare și operare scris în Drive**, ca
fișier nou în `BRIDGE-DRIVE/INTRARI-CLOUD/`, cu cifre (de unde a citit, ce
SHA de HEAD a citit, câte taskuri a văzut) și confirmarea explicită a
protocolei. Commitul CI: `8cdb987` (publicat, divergență 0/0).

### 1.4 Sincronizarea repo-urilor — cerința de azi

`cloud-ingest/` conține acum **ambele** repo-uri. Au fost sincronizate cu
GitHub prin **fast-forward**, fără rescriere:

| Repo | Înainte | După | Istoric |
|---|---|---|---|
| `cloud-ingest/MAVIS-OPTIMUS-CI` | `3da55ff` (**34 în urmă**) | `5abb189` = `origin/main` | vechiul e strămoș (`merge-base --is-ancestor` → exit 0) |
| `cloud-ingest/MAVIS-CLOUD` | `4a88879` | `4a88879` = `origin/main` | — |

Ambele: **divergență 0/0**, **un singur `main`** per repo, arbor curat.
Ramurile vechi ale lui Jules au fost șterse **pe remote** (măsurat: 60+
refs `origin/*` dispărute la `--prune`); local s-a păstrat un singur `main`.

**Repo-ul CI (`MAVIS-OPTIMUS-CI`) e acum la `8cdb987` = remote**, cu istoricul
combinat prin `merge --no-ff` (ambele părți păstrate), divergență 0/0.

### 1.5 Corecția drift-urilor vii din documentație

33 de înlocuiri în 9 fișiere, **pe loc**, cu măsurătoarea înaintea fiecărei
corectii. Cele 8 afirmații care deveniseră false (după livrare și push) sunt
listate în `docs/STARE-MASURATA-CI-2026-10-27.md` §12.2. Printre ele: „404
pe remote" (workflowul e împins de `65af38f`), „17 commituri neîmpinse" (0),
„22 PR-uri deschise" (0), „clonă read-only" (clona e și copia de lucru a
livrării), SHA-ul învechit `15c5353` (înlocuit cu **metoda**, ca să nu se
învechească la fiecare commit), `pushed_at` învechite în inventar.

**O lecție de instrument, scrisă în §12.4:** cifrele de volum ale arborelui
**nu sunt reproductibile** pe mirrorul DriveFS — fișierele-placeholder se
materializează la acces (am măsurat ±32 de fișiere între două măsurători
consecutive) și `git gc` schimbă numărul de fișiere din `.git/` cu ±60. De
aceea inventarul raportează acum **fișiere urmărite de git** (`git ls-files`:
**68** în CI, **405** în clonă), nu fișiere pe disc.

### 1.6 Acces Google permanent — containerul `Google_Access`

**Un server MCP, un container, un credential.** Nu mai e nevoie de
re-autentificare: credentialul e un refresh token într-un volum montat, iar
tokenurile de acces se mintesc automat din el.

| Ce | Valoare măsurată |
|---|---|
| Container | `Google_Access` · imagine `google-access:1.0.2` · `--restart unless-stopped` |
| Endpoint | `http://127.0.0.1:8766/mcp` (doar loopback) · transport `streamable-http` |
| Unelte | **25** (Drive, Gmail, Docs, Sheets, Calendar, Photos, Books, Keep, Tasks, Sites, Script, Chat, YouTube + proxy ExtendLM/NotebookLM) |
| Grant | **LIVE** · `client_id 1068987308935-5b7h17gt1c5hc4…` |
| Probe reale | Drive: 5 fișiere reale · Gmail: 3 mesaje reale · Books: **403 explicit** (scope lipsă), nu eșec tăcut |
| Secret în imagine | **niciunul** — credentialul e în volumul montat `/data` |
| Sursa în GitHub | `<CI>\tools\google-access\` (6 fișiere, SHA identic cu sursa vie) — deci **reconstruibil din GitHub**, nu de pe un singur disc |
| Notificare | taskul `Google_Access_Watch` (orar) → ntfy `mavis-google-access` + `REAUTH-NOTICE.md`; falsificat: exit **3** + mesaj livrat |

**Trei defecte măsurate și reparate la sursă** (toate erau *porturi scrise ca
literal*, adică o a doua sursă de adevăr despre același lucru):

1. **Healthcheck-ul mințea.** `HEALTHCHECK` proba `127.0.0.1:8765`, containerul
   rula cu `GA_PORT=8766` → `unhealthy` la 9 intervale consecutive, în timp ce
   serviciul răspundea HTTP 200 cu `grant=live`. Reparat: proba își derivează
   portul din `process.env.GA_PORT`.
2. **Proba măsura alt serviciu.** `probe.mjs` avea implicit
   `http://127.0.0.1:8765/mcp` — un proces **strain** (python, serviciul
   `hc-backend`). Tipărea `HANDSHAKE=FAILED`, `TOOLS=0` și **ieșea cu cod 0**.
   Reparat: implicitul e 8766, plus verificare de identitate
   (`SERVICE_MISMATCH` → UNKNOWN) și coduri de ieșire proprii: 0 = PASS,
   1 = FAIL, **2 = UNKNOWN**.
3. **Fallback-ul din `server.mjs`** era tot 8765 → reparat la 8766.

Proba e falsificată în ambele sensuri: port strain → exit 2, port inaccesibil →
exit 2, port corect → exit 0 (`VERDICT=PASS`, 25 unelte, apeluri reale).

Skill: `~/.minimax/agents/mavis/skills/mavis-google-access-skill/SKILL.md`.

**CD poate folosi endpointul** (`http://127.0.0.1:8766/mcp`) — dar cu
instanța lui, dacă își construiește propriul. **Regula namespace-ului:**
containerul meu și containerele Hermes nu se ating.

**Un singur click rămâne necesar** pentru scope-urile din afara grantului
curent (Photos, Keep, Tasks, Books, Sites, Script, Chat, YouTube):
`google_scope_upgrade` → URL de consimțământ → `provision-grant.cjs
--from-code <code> --client secrets`. După acela, nu se mai cere nimic.

---

## 2. Cele 9 task-uri de fundal — închise

| # | Task | Verdict |
|---|---|---|
| 1 | „Test new verify on SENTINEL_PRIME PR3" | exit 3 = **NOT_ATTRIBUTABLE** (contractul documentat), nu defect |
| 2 | „Run the failing commands and capture real output" | ieșire brută; eșecuri **preexistente** pe ramura de bază |
| 3 | „Adaptation generator" (12 PR-uri) | cauză: `ConvertFrom-Json` pe array top-level → reparat, probat în 3 direcții |
| 4 | „Final triage run with refined gate" | reluat cu succes: 12 ACCEPT / 40 ADAPT / 46 UNVERIFIED / 1 NOT_ATTRIBUTABLE / 0 REJECT |
| 5 | „Full triage on PR #42" | `Test-DiffPolicy` fără `AllowEmptyCollection` → blocarea lanțului; reparat |
| 6 | „Full gate test suite" | control pozitiv TRECUT + controale negative BLOCAT; exit 1 = contaminare de cod |
| 7 | „Detail on the repos with mass deletions" | conținut intact; gitlink mort fără `.gitmodules` → `c73fa0b` |
| 8 | „Locate system scripts" | obiect re-măsurat: trash, kernel, interactie, 76 skilluri, 10 scripturi CD, 15 CI |
| 9 | „Install / Self-test" | installerul raporta plan valid pentru repo inexistent (404) și ieșea 0 → reparat cu exit 7 + falsificare |

**Nu sunt 9 sarcini rămase.** Sunt 9 taskuri diagnosticate și închise. Ce
rămâne e §3.

---

## 3. RĂMÂNE PENTRU CD — în ordine

1. **Reorg-ul arborelui CD** (164 rânduri de `git status` măsurate acum) — în
   curs, al sesiunii CD. Nu m-am amestecat.
2. **`config/repos.json`** — cifrele `openPrs` au devenit false (măsurat azi:
   **0 / 0 / 0 / 0 / 0 / 0**). Nu e defect funcțional (codul nu citește
   `openPrs`), dar e o cifră falsă într-un registru care se citește.
3. **`proba-backlog`** rămâne `UNKNOWN` cât timp backlog-ul e gol — corect.
   **Nu tratați `UNKNOWN` drept trecere.**
4. **Cele 12 ramuri nemerge-uite** din backbone — refetșabile din origin
   (PR-urile sunt închise). Decizia de păstrare/prunare: CD.
5. **`MAVIS-OPTIMUS-CD`** nu există încă pe GitHub (404 măsurat). Crearea lui +
   comutarea `dispatch`/`triage` pe `true` = R0 deschis al CD-ului.

---

## 4. Nou, de azi — ce trebuie să știe CD-ul

1. **Cloud-ul citește GitHub la fiecare start de sesiune, job și acțiune.**
   Repo-ul operațional e `MAVIS-CLOUD`; cel de sistem e `MAVIS-OPTIMUS-CI`.
   Coada e în **repo-ul Cloud-ului** (`QUEUE/TASKS-FOR-CLOUD.md`), nu în CI.
2. **Clona din `cloud-ingest/` nu mai e read-only** — e și copia de lucru a
   livrării cozii secundare. Contractul consumatorului cere asta. E **aditiv**:
   nimic existent nu se rescrie, marcarea `[x]` a Cloud-ului supraviețuiește.
3. **Taskul zilnic e la 07:30**, nu 08:30 (`StartWhenAvailable=True` → pornește
   întârziat dacă mașina era stinsă).
4. **`README_SYSTEM_TOPOLOGY_AND_AGENT_GUIDELINES.md` — corectură de
   măsurătoare:** l-am declarat trunchiat (0 B) într-o primă citire. **Nu e
   așa.** Pe mirrorul DriveFS, `Get-Item.Length` raportează **0** pentru un
   fișier-placeholder nehidrat; `os.stat` îl hidratează și dă **15.936 B**.
   Conținutul e intact în toate cele trei copii. Zero fișiere goale în fereastra
   de trunchiere. **Documentul canonic e sănătos** — și conține modelul de
   trei discuri cu joncțiunile.
5. **Instrumentul, nu datele, era defectul.** Regula pentru CD: înainte de a
   declara un fișier gol sau trunchiat pe acest mirror, **hidratează-l
   (`os.stat` / citire)** și abia apoi măsoară.
6. **Mavis Cloud a răspuns — puntea e vie în ambele sensuri.** Raportul lui e
   în `BRIDGE-DRIVE/INTRARI-CLOUD/RASPUNS-MAVIS-CLOUD-2026-10-27-0849-raport-operare.md`.
   A citit de pe **Drive** (cloud_id `1V87h9Pbw52chSVNkxQ_NNuMh-CLfZeuI`),
   fișierul `BRIDGE-DRIVE/TASKURI-PENTRU-CLOUD.md` (5.854 B), a confirmat cele
   **3 TASK_ID identice pe ambele canale**, și a confirmat explicit:
   *„Drive = puntea principală; GitHub = canal secundar și memorie permanentă
   a sistemului."* **Re-onboardingul e închis din punctul de vedere al Cloud-ului.**
7. **Corecție de măsurătoare în raportul Cloud-ului.** Cloud-ul a raportat
   „404 — nu există" pentru `BRIDGE-DRIVE/` în `MAVIS-OPTIMUS-CI`. **Măsurat
   fals:** fișierul e urmărit și prezent la `origin/main:8cdb987`
   (`git ls-tree -r origin/main -- BRIDGE-DRIVE/` → 5 intrări; `TASKURI-PENTRU-CLOUD.md`
   = 5.854 B, exact dimensiunea pe care Cloud-ul o citise din Drive). Deci
   „fișierul există doar în Drive" e fals: era disponibil și pe canalul
   secundar. Pentru `MAVIS-CLOUD` afirmația e corectă (acolo `BRIDGE-DRIVE/`
   nu există, prin design) — dar concluzia generală, că ar fi imposibil de
   citit prin GitHub, e greșită. Corecția e trimisă pe canalul Local→Cloud.
8. **Defectul OAuth al Cloud-ului e reparat și livrat în GitHub.** Cloud-ul a
   găsit că `kit.js` lua `client_id`/`client_secret` dintr-un client, iar
   refresh-token-ul aparținea altui client → `invalid_grant` /
   `unauthorized_client`. Am reparat **la punctul unic de rezolvare**
   (`mavis-tools/google-auth.js`): clientul din fișierul de token câștigă, iar
   o pereche asamblată din surse diferite e **refuzată**, nu construită.
   Commit `d3f119f` în `MAVIS-CLOUD` (remote = local, divergență 0/0).
   **Falsificare:** testele noi pică **5 din 8** contra implementării vechi și
   trec **8 din 8** contra celei noi. `describe()` raportează acum
   `client_source`, `mixed_env` și `client_pairing`.
9. **Filtrele Gmail `MAVIS/*` — reparate, și scriptul reparat la sursă.**
   Cloud-ul a raportat 5 filtre care nu loveau nimic (0 mesaje în 30 de zile,
   în loc de ~3.737) și le-a pregătit un script. Dar scriptul apela `PATCH` pe
   filtre — **metodă care nu există** în Gmail API (măsurat din discovery
   document: pe `gmail.users.settings.filters` există doar DELETE, GET, LIST și
   CREATE; singurele `patch` din tot API-ul sunt `labels.patch`,
   `sendAs.patch`, `cse.identities.patch`). În plus, numele etichetelor erau
   **hardcodate**, iar etichetele au fost rearanjate în noaptea, deci 4 din 5
   filtre erau sărite cu „eticheta nu există" — deși filtrele erau prezente.
   Reparat: `CREATE` cu criteriul și acțiunea noi, apoi `DELETE` al celui vechi
   (ordinea aleasă intentionat: un CREATE eșuat să nu piardă filtrul vechi), iar
   numele etichetelor se rezolvă **live** prin `taxonomy.js`. Aplicat de pe
   această mașină, unde scope-ul `gmail.settings.basic` există: **5 din 5**
   reparate, celelalte 14 neatinse. Verificat independent prin API: 19 filtre în
   total, 5 cu acolade, fiecare cu eticheta sa vie. Commit `350f983` în
   `MAVIS-CLOUD`.
   **Regula pentru CD:** înainte de a te baza pe o metodă de API, verific-o în
   discovery document. Un `PATCH` care „ar trebui să existe" a costat o
   noapte de raporturi greșite — și un script care părea gata.

---

## 5. CE NU S-ATINS

- **Arborele CD** — 0 scrieri în afara `_Handoffs/`. Reorg-ul e al tău.
- **Containerele Hermes** — niciunul n-a fost atins, recreat sau prunat.
  `Google_Access` e un container **nou**, cu nume nou.
- **Credentialele Hermes** — nu s-au citit, nu s-au copiat, nu s-au folosit.
- **Vaultul PKMS** — scanări țintite, nu brute. Singura scriere în afara
  spațiilor mele: **zero** (documentul topologic nu avea nevoie de restaurare).
- **CD-ul nu a fost împins** pe niciun remote. Nu există
  `MAVIS-OPTIMUS-CD` pe GitHub.

---

## 6. UNDE SUNT INSTRUMENTELE

| Ce | Cale |
|---|---|
| Repo-ul CI | `E:\Google\GDrive\GDrive-Second_Brain_PKMS\02_Areas\02-2-AI-SOT\CASA\OPTIMUS - Prime\Optimus_CI (by Mavis)\` |
| Joncțiune rapidă | `C:\Users\apviz\.minimax-agent\projects\Optimus_CI (by Mavis)` |
| Clonele (ambele repo-uri) | `<CI>\cloud-ingest\MAVIS-CLOUD` · `<CI>\cloud-ingest\MAVIS-OPTIMUS-CI` |
| Contractul cozii | `<CI>\docs\CONTRACT-CLOUD-QUEUE.md` |
| Starea măsurată de azi | `<CI>\docs\STARE-MASURATA-CI-2026-10-27.md` (§11 livrare · §12 drift) |
| Diagnosticul celor 9 taskuri | `<CI>\docs\HANDOFF-TERMENARE-DEVELOPMENT-2026-10-27.md` |
| Containerul Google | `C:\Users\apviz\.minimax\google-access\` · skill `mavis-google-access-skill` |
| Sursa lui, în GitHub | `<CI>\tools\google-access\` (server, Dockerfile, probe, provisioner, watcher) |
| Puntea Drive | `<CI>\BRIDGE-DRIVE\` · `scripts\mavis-drive-bridge.ps1` |

---

## 7. ORDINEA PRIMEI PAS AL CD-ULUI

1. `git -C "<CD>" status --porcelain` — vezi reorg-ul înainte de orice.
2. Citește §3 de mai sus: 5 puncte, toate delegate.
3. Pentru operațional: verifică `MAVIS-CLOUD` la remote cu
   `git -C "<CI>\cloud-ingest\MAVIS-CLOUD" ls-remote origin refs/heads/main`
   → ultimul commit; azi: `930da7c` (numele etichetelor rezolvate **live**, la
   sursă; corecția OAuth e `d3f119f`, în istoric). Apoi coada:
   `QUEUE/TASKS-FOR-CLOUD.md` — **5 tichete**, toate în format de contract, și
   **5 din 5 marcate `[x]`** de Cloud: **coada e închisă**.
4. Pentru sistem: `MAVIS-OPTIMUS-CI` →
   `git ls-remote origin refs/heads/main`, divergență 0/0 măsurată prin
   `git rev-list --left-right --count origin/main...main`.
   **Nu folosi un SHA scris într-un document** — e o cifră care îmbătrânește la
   fiecare commit. Măsoară, apoi citește cifra.

---

*27 oct 2026 · Mavis Local · măsurat, nu presupus · aditiv, fără trunchiere*

---

## 8. Starea punții la 09:15 — coada e închisă

> **Aditiv.** Nimic din §1–§7 nu se rescrie.

| Ce | Valoare | Cum a fost măsurat |
|---|---|---|
| Răspunsuri ale Cloud-ului | **3** (08:49, 12:07, **08:52**) | fișiere noi în `BRIDGE-DRIVE/INTRARI-CLOUD/` |
| Tichete marcate `[x]` de Cloud | **5 din 5** | marcajele citite **la vârful remote** (`930da7c`), nu din amintire |
| Livrabile în `QUEUE/DONE/` la Cloud | **5** | `git ls-tree origin/main QUEUE/DONE/` |
| Coada locală | `TICKETS=5` · `TICKET_PROBLEMS=0` · `DELIVERED=5/5` · `QUEUE_PROBLEMS=0 UNKNOWN=0` | `queue-contract-check.ps1` · auto-proba 14/14 |
| `MAVIS-CLOUD` | `930da7c` = `origin/main`, divergență **0 0** | `ls-remote` + `rev-list --left-right --count` |
| `MAVIS-OPTIMUS-CI` | `da4b0b7` = `origin/main`, divergență **0 0** | idem |

### 8.1 Ce a reparat Cloud-ul — verificat de mine, nu preluat

`taxonomy.js` era sursa lui unică de adevăr, dar 6 scripturi o ocoleau: patru
foloseau `startsWith('MAVIS/')` (ar fi numărat **1 din 9** etichete), două aveau
**8 nume hardcodate** (ar fi creat 7 etichete noi, goale).

Verificat **independent**, în clona lui, la `930da7c`: `startsWith('MAVIS/')` = **0**
apariții în cele 6 scripturi, referință la `taxonomy.js` în **6 din 6**, și
`node --check` exit **0** la toate.

### 8.2 Starea oglindită local

- **Marcaje:** `0103` și `0844` → `[x]`, cu linia `CONSUMAT` (ca `0815`).
- **Livrabile:** 4 copiate în `QUEUE/DONE/` (`0815` era deja acolo).
- **Arhive:** 4 secțiuni arhivate în `BRIDGE-DRIVE/ISTORIC/` (`0005`, `0103`,
  `0815`, `0844`); `0735` era deja. **Conținut păstrat integral** — secțiunile
  **rămân** în canalul primar, deci poarta de paritate rămâne satisfăcută.
- **Antetul cozii primare** corectat: „Cloud-ul marchează; **Local mută**" —
  era ultima contradicție a protocolului.

### 8.3 O neconcordanță de nume, măsurată

Livrabilele Cloud-ului referă `RASPUNS-MAVIS-CLOUD-2026-10-27-0812-raspuns-0844-etichete-live.md`,
dar fișierul din canalul primar e `...0852-...` (ora din antetul lui: 08:52 /
05:52 UTC). **Nu redenumesc fișierele celeilalte instanțe** — e înregistrat ca
notă în arhivă, nu corectat în loc.

