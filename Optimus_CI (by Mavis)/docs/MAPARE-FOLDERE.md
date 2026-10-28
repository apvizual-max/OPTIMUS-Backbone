# MAPARE-FOLDERE — unde stă tot, în CI

> Complementul lui `MAPARE-SISTEM.md`. Acolo e **unde stă sistemul** în
> relație cu restul mașinii. Aici e **ce e în fiecare folder al proiectului**
> și ce se atinge / nu se atinge.
>
> **Măsurat 2026-10-27.** Cifrele sunt de pe disc, nu din memorie.

---

## 1. Rădăcina

| | |
|---|---|
| **Sursa (SOT)** | `E:\Google\GDrive\GDrive-Second_Brain_PKMS\02_Areas\02-2-AI-SOT\CASA\OPTIMUS - Prime\Optimus_CI (by Mavis)` |
| **Joncțiune locală** | `C:\Users\apviz\.minimax-agent\projects\Optimus_CI (by Mavis)` → `E:` (`LinkType=Junction`) |
| **În Drive** | `My Drive > GDrive-Second_Brain_PKMS > 02_Areas > 02-2-AI-SOT > CASA > OPTIMUS - Prime > Optimus_CI (by Mavis)` |
| **`cloud_id`** | `1V87h9Pbw52chSVNkxQ_NNuMh-CLfZeuI` |
| **`.git`** | **fișier** (worktree link) → `gitdir: E:/Google/GitData-Optimus-CI/repo` |
| **Gitdir CD (separat)** | `E:/Google/GitData-Optimus-CD` |
| **Volum** | **68 fișiere urmărite de git** · arborele de pe disc se măsoară la cerere (placeholder-uri DriveFS) |

> **Calea veche nu mai există:** `…\projects\Mavis-Optimus-Continuous-Integration\`
> a fost eliminată prin Trash recuperabil (3 niveluri, EXIT 0) pe 27 oct.

---

## 2. Rădăcina, fișier cu fișier

| Entitate | Ce e | Volum | Git? |
|---|---|---|---|
| `README.md` | Portul: ce e proiectul, cum se intră, ce porți există | 1 fișier · 18.321 B | ✅ |
| `DOCTRINA-CI.md` | Doctrina CI: reguli, asimetria, ce nu se atinge | 1 fișier · 16.523 B | ✅ |
| `MAPARE-SISTEM.md` | Unde stă sistemul față de restul mașinii | 1 fișier · 11.191 B | ✅ |
| `Plan_Dezvoltare_CI_from_POPY (Gemini)-10-13-2026.md` | Planul original, 13 oct, **istoric** — nu e contract | 1 fișier · 63.702 B | ✅ |
| `.gitignore` | Ce nu se comite | 1 fișier · 1.606 B | ✅ |
| `.github/workflows/` | Workflow-ul de server: `ci-verify.yml` | 1 fișier · 1.589 B | ✅ |
| `.jules/` | Bootstrapul lui Jules: `bolt.md` · `sentinel.md` | 2 fișiere · 2.558 B | ✅ |
| `JULES_HANDOFF.md` | Predarea către sesiunea Jules | 1 fișier · 978 B | ✅ |
| `docs/` | Documentația de proiect | **31 fișiere urmărite** | ✅ |
| `scripts/` | Instrumentele | **20 fișiere urmărite** · 237.784 B | ✅ |
| `BRIDGE-DRIVE/` | **Canalul primar** (Google Drive) | 5 fișiere · 8.608 B | ✅ |
| `QUEUE/` | **Canalul secundar** (GitHub) | 2 fișiere · 6.206 B | ✅ |
| `blueprint/` | Planul CI din faza de blueprint | 1 fișier · 11.255 B | ✅ |
| `mapari/` | **gol** — folder rămas de la o layout veche | 0 | — |
| `cloud-ingest/` | Clona `MAVIS-CLOUD` — sursă **read-only** pentru conținut, **și copia de lucru a livrării cozii secundare** | **405 fișiere urmărite** de git | ❌ ignorat |
| `logs/` | Jurnalele punții zilnice | 15 fișiere (un log pe zi) | ❌ ignorat |
| `desktop.ini` | Artefact Windows | 149 B | ❌ ignorat |
| `state/` | Scratch, măsurători, probe | — | ❌ ignorat |

**Urmărit de git: 68 fișiere** (`git ls-files`). Octeții se dau **per
entitate**, nu se însumează într-un total: un commit nu schimbă dimensiunile,
dar o editare ulterioară le mută — iar `docs/` se editează la fiecare rând.

> **De ce cifrele sunt „urmărite de git" și nu „fișiere pe disc":** arborele
> stă pe un mirror DriveFS, iar **fișierele-placeholder se materializează la
> acces**. Între două măsurători consecutive, numărul de fișiere pe disc a
> variat cu **±32** în clonă și cu **±32** în rădăcina CI. Reproductibil e
> doar ce e urmărit de git: `git ls-files` dă **68** în CI și **405** în clonă.
> Iar istoricul (`git gc` împachetează obiectele loose) adaugă **±60**
> fișiere — de aceea `.git/` nu intră în nicio cifră.

> **`mapari/` e gol.** L-am lăsat: e necomandat, și un folder gol nu strică
> nimic. Nu e un plan de șters — e o poziție fără conținut.

---

## 3. `BRIDGE-DRIVE/` — canalul primar

| Fișier | Cine scrie | Ce e |
|---|---|---|
| `README-BRIDGE-DRIVE.md` | Local | **Protocolul canalului**: reguli, formate, convenție |
| `TASKURI-PENTRU-CLOUD.md` | Local | Cerințe structurate spre Cloud (canal primar) |
| `INTENTII.md` | Popy | Cerințe libere, cu cuvintele lui |
| `INTRARI-CLOUD/README.md` | Cloud | Livrările Cloud intră aici |
| `ISTORIC/README.md` | Local | Ce a fost consumat — prin **mutare**, niciodată ștergere |

---

## 4. `scripts/` — instrumentele

| Script | Ce face | Notă |
|---|---|---|
| `mavis-drive-bridge.ps1` | Publicare pe ambele canale + măsurătoare de stare | `-Status` · `-Publish` · `-Verify` |
| `mavis-drive-bridge-selfcheck.ps1` | **Poarta punții** — 19 probe | `BRIDGE_PROBLEMS=0 UNKNOWN=0` |
| `drivefs_probe.py` | Sonda read-only în baza DriveFS | `--title` · `--newest` · `--root-state` · `--pending` · `--staleness` |
| `queue-contract-check.ps1` | **Poarta cozii secundare** — contractul consumatorului, viu | exit `0`/`1`/`2`; `2` = contract ilizibil = UNKNOWN |
| `queue-contract-check-selfcheck.ps1` | **Poarta porții de contract** — 14 probe | `QUEUE_GATE_PROBLEMS=0 UNKNOWN=0 FALSIFIED=11` |
| `scan-staged-secrets.ps1` | **Poarta de secrete** pe index | `BLOCKS` / `WARNS` |
| `scan-staged-secrets-selfcheck.ps1` | **Poarta porții de secrete** — 7 probe | `SECRET_PROBLEMS=0 UNKNOWN=0` |
| `mavis-sync.ps1` | **Puntea zilnică** Local↔Cloud (task 07:30) | cale derivată din `$PSScriptRoot` · `exit` propriu · taskul `MavisSyncBridge` |
| `mavis-sync-selfcheck.ps1` | **Poarta punții zilnice** — 9 probe | `SYNC_PROBLEMS=0 UNKNOWN=0 FALSIFIED=4` |
| `merge-check.ps1` | **Măsurătorul combinării istoricului** — dry-run, nu atinge arborele | exit `0`/`1`/`2`; `2` = nemăsurabil ≠ curat |
| `merge-check-selfcheck.ps1` | **Poarta măsurătorului** — 5 probe pe repo reale | `MERGE_GATE_PROBLEMS=0 UNKNOWN=0 FALSIFIED=5` |
| `run-sync-logged.ps1` | Rulează sincronizarea cu log datat | `-DryRun` disponibil |
| `meta-prompt.ps1` | Generează meta-prompt-ul de pornire | — |
| `snapshot-vault.ps1` | Snapshot al vault-ului | — |
| `notebooklm-cdp.mjs` | Acces la NotebookLM prin CDP | — |

**Regula:** toate scripturile `.ps1` sunt **ASCII pur** (0 octeți peste
`0x7F`) — rulează în Windows PowerShell 5.1, unde `pwsh` nu e instalat.

---

## 5. `docs/` — documentația

**Nucleu:** `README` · `DOCTRINA-CI` · `MAPARE-SISTEM` · `MAPARE-FOLDERE` ·
`WORKFLOWS`

**Puntea și politici:** `PUNTE-DRIVE-PRIMARA` · `BRIDGE-LOCAL-CLOUD` ·
`PROTOCOL-DENUMIRE-LOCAL-CLOUD` · `CONTRACT-CLOUD-QUEUE` · `CI-POLICY` ·
`GIT-GITHUB-PROCEDURI` · `CONFLICTE-DOZTRINA` · `ARHITECTURA-CI-CD`

**Stare:** `STARE-MASURATA-CI-2026-10-27` · `STARE-MAVIS-OPTIMUS-CI-REMOTE` ·
`STARE-MASURATA-CI` · `STATUS-LOCAL-TO-CLOUD-2026-10-12`

**Instrumente:** `INVENTAR-REPO-URI` · `META-PROMPT` · `RECUPERARE-GIT`

**Arhivă:** `docs/arhiva/handoffs-vechi/` — 11 fișiere, istoric **prin mutare**.

---

## 6. Ce stă **în afara** proiectului

| Ce | Unde | Regula |
|---|---|---|
| **Skillurile Mavis** | `C:\Users\apviz\.minimax\agents\mavis\skills\` | 4 skilluri extinse aditiv: `mavis-optimus-continuous-integration-skill`, `mavis-cloud-bridge-skill`, `mavis-local-to-cloud-reporting`, `mavis-google-workspace-skill` — **extinse din nou 2026-10-27 ~02:45** cu contractul cozii, poarta lui, refuzul corpului trunchiat și `DUAL_CHANNEL` |
| **Poarta de push (definiția comună)** | `C:\Users\apviz\.minimax-agent\projects\scripts\git-hooks\pre-push` | **o singură definiție**, partajată cu CD. Hook-ul din CI **delegă**, nu copiază |
| **Hook-urile per-repo ale CI** | `E:\Google\GitData-Optimus-CI/repo\hooks\` | `pre-commit` (scanner) + `pre-push` (delegat) |
| **Folderul CD** | `…\Optimus_CD (by Jules)\` | **neatins** din CI. Documentele CD trăiesc în folderul CD |
| **Bazele DriveFS** | `%LOCALAPPDATA%\Google\DriveFS\` | `metadata_sqlite_db` = index de cloud (citibil). `mirror_metadata_sqlite_db` = **blocat** de DriveFS |

---

## 7. Regula de așezare

**Un document trăiește în folderul sistemului pe care îl guvernează.**

- Document despre CI → în folderul CI. **CD neatins.**
- Document despre CD → în folderul CD. **Nu se rescrie din CI.**
- Corecția se face prin **fișier nou**, cu numele instanței care l-a scris.
- Actualizările sunt **aditive**. Nimic nu se trunchiază.

Concret, în acest rând: 15 documente CI extinse, 4 skilluri extinse, 4 scripturi
noi, 2 hook-uri, `.gitignore` completat — **zero** fișiere șterse, zero
rescrise, zero atinse în CD.

---

## 8. `.github/workflows/` — plasa de siguranță a serverului

> **Aditiv.** Măsurat 2026-10-27.

| Fișier | Ce face | Notă |
|---|---|---|
| `ci-verify.yml` | Rulează scannerul de secrete + auto-proba pe **ce a aterizat** în repo | `on: push` (main) + `workflow_dispatch` + `schedule: '30 3 * * *'` · `runs-on: windows-latest` |

**Unde rulează:** pe serverul GitHub. **Nu** rulează poarta punții — acolo nu
există DriveFS.

**Raportează, nu blochează.** Un workflow care blchează un push al altui AI
care lucrează pe același repo ar fi o poartă fără imputabilitate: verdictul
de „REJECT" al meu pe conținutul altcuia. El doar **spune** ce a aterizat.

**Falsificat în ambele sensuri** (clonă curată, simulare de runner):
`SCANNED=50 BLOCKS=0 SCAN_OK` exit 0 → cu cheie plantată `BLOCKS=1` exit 1
(workflow ar deveni roșu) → scosă → `SCAN_OK` exit 0.

**Starea reală:** workflow-ul `ci-verify.yml` **e pe remote** — a ajuns cu
împungerea lui `65af38f` (26 oct), confirmat azi la `origin/main` (blob
`6f0fd55`). **Serverul rulează acum pentru acest repo.** Secțiunea spunea
*„404 pe remote, între cele 17 commituri neîmpinse"* — era adevărată înainte
de împungere.

---

## 9. `QUEUE/` — canalul secundar (GitHub)

> **Aditiv.** Măsurat 2026-10-27, ~02:40.

| Fișier / folder | Cine scrie | Ce e |
|---|---|---|
| `QUEUE/TASKS-FOR-CLOUD.md` | Local | Coada de tichete pentru Cloud, **în contractul consumatorului** |
| `QUEUE/DONE/README.md` | Local | Ținta de livrare: aici scrie Cloud rezultatele, ca `<id>.md` |

**Formatul cozii e contractul, nu o preferință.** Cloud citește acest fișier
la pull și rulează **doar** tichetele cu `scope: cloud`. Cele cinci câmpuri:
`cerut de` · `data` · `scope` · `ce trebuie` · `livrare`. Contractul, citat de
pe discul Cloud-ului: `docs/CONTRACT-CLOUD-QUEUE.md`.

**Măsurat înainte de reparare:** 0 din 5 câmpuri, 0 `scope:`, 2 anteturi
invizibile pentru Cloud, `QUEUE/DONE/` absent. Cloud ar fi executat **zero**
tichete — fără să raporteze nicio eroare.

**Măsurat după reparare:**

```
QUEUE_PROBLEMS=0 UNKNOWN=0   TICKETS=2   CONTRACT_DRIFT=NO
UNRECOGNISED_HEADERS=0        DONE_DIR=present            EXIT 0
```

### Ce s-a adăugat în acest rând

| Ce | Kind | Notă |
|---|---|---|
| `docs/CONTRACT-CLOUD-QUEUE.md` | document | contractul consumatorului, cu proveniență și dată |
| `scripts/queue-contract-check.ps1` | poartă | contract **viu**, drift, paritate `TASK_ID`, țintă de livrare |
| `scripts/queue-contract-check-selfcheck.ps1` | auto-probă | 14 probe, falsificare în ambele sensuri |
| `scripts/queue-lib.ps1` | **parserul cozii** | o singura implementare, pentru poarta si livrare |
| `scripts/queue-deliver.ps1` | **livrarea cozii** în repo-ul Cloud-ului | exit `0`/`1`/`2`/`4`/`5` |
| `scripts/queue-deliver-selfcheck.ps1` | **auto-proba livrarii** | 15 probe |
| `QUEUE/DONE/README.md` | țintă | folderul în care Cloud livrează |

Delta: **+1 document, +2 scripturi, +1 folder** — **zero** fișiere șterse,
zero rescrise, zero atinse în CD.

---

## 10. Instrumentul combinării istoricului

> **Aditiv.** Măsurat 2026-10-27.

Repo-ul CI e lucrat **în paralel** de alt AI (sesiunea CD). Deci există două
istorice: `main` local (commiturile mele, automate, neîmpinse fără R0) și
`origin/main` (commiturile celuilalt AI). Combinarea lor e o operație de R0 —
iar R0 merită **fapte, nu opțiuni**.

`scripts\merge-check.ps1` măsoară **fără să atingă arborele** și fără să
împingă nimic:

| Ce măsoară | Cum |
|---|---|
| Cât de depărtate sunt istoriculele | `git rev-list --left-right --count` |
| Dacă merge-ul e curat sau conflict | `git merge-tree --write-tree` (dry-run) |
| Care fișiere conflictuează | exit 1 + **numele** fișierului, unul pe rând |
| Ce arbore ar rezulta | id-ul arborelui, pentru comparație |

Exit: `0` = curat · `1` = conflict · `2` = **nemăsurabil** — care **nu** e
„curat".

**Măsurat pe repo-ul real:** `REMOTE_STATE=LIVE` · `DIVERGENCE_BEHIND=5`
`DIVERGENCE_AHEAD=24` · `MERGE_CLEAN=yes` · `CONFLICT_FILES=0` · arborele
`8b11d68dd1847cc450276eca76030bf4818540fa` · merged vs local **6 fișiere**
(+74/−13 — lucrarea CD) · merged vs remote **38 fișiere** (+7309/−230 — lucrarea
mea).

Auto-proba: `scripts\merge-check-selfcheck.ps1` — **5 probe pe repo reale**,
conflictul produs de git, nu simulat.

---

## 11. `tools/` — sursele containerului Google

> **Aditiv.** Măsurat 2026-10-27, ~09:00.

| Fișier | Ce e |
|---|---|
| `tools\google-access\server.mjs` | serverul MCP (25 unelte); sursa vie e în `C:\Users\apviz\.minimax\google-access\` |
| `tools\google-access\Dockerfile` | imaginea `google-access:1.0.2` · `GA_PORT=8766` · healthcheck care își derivează portul din `process.env.GA_PORT` |
| `tools\google-access\probe.mjs` | proba: handshake + apeluri reale + **verificare de identitate**; exit `0`/`1`/`2` (`2` = UNKNOWN, nu succes) |
| `tools\google-access\provision-grant.cjs` | provisionarea grantului (scope-uri Google) — un singur credential, autentificare permanentă |
| `tools\google-access\watch-reauth.ps1` | notificarea de re-autentificare (task orar `Google_Access_Watch`) |
| `tools\google-access\README.md` | cum se construiește și se rulează |
| `tools\google-access\.dockerignore` · `.gitignore` | contextul de build + **credentialul exclus din git** |

**De ce contează:** sursa e în GitHub → sistemul se reconstruiește din GitHub,
nu de pe un singur disc. Cele 6 fișiere au **SHA256 identic** cu sursa vie.
`data\credentials.json` (singurul secret) stă **în afara** arborelui versionat.

### Ce s-a mai adăugat în puntea primară

| Ce | Unde | Ce e |
|---|---|---|
| Răspunsuri ale Cloud-ului | `BRIDGE-DRIVE\INTRARI-CLOUD\` | 2 rapoarte de operare (08:49, 12:07) |
| Task consumat, **arhivat prin mutare** | `BRIDGE-DRIVE\ISTORIC\MAVIS-LOCAL-2026-10-27-0815-ARHIVAT-TASK-2026-10-27-0735.md` | conținut păstrat integral |
| Livrări ale Cloud-ului | `QUEUE\DONE\` | artefactele marcate de Cloud |
| Handoff pentru CD | `docs\HANDOFF-CD-2026-10-27-PUNTEA-DRIVE-PRIMARA-GOOGLE-ACCESS.md` | identic prin SHA256 cu `Optimus_CD (by Jules)\_Handoffs\` |

**Regula de excludere reparată:** `chats/` a fost renumerit în Drive cu
`Google_Connect/` (27 oct, 08:02) → `.gitignore` excludea un nume mort, iar
`scripts\mavis-sync.ps1:189` face `git add -A` + commit automat: **drum de
scurgere spre un repo public**. Regula acoperă acum `Google_Connect/` **și**
`**/Mavis-Cloud_Google-Setup-Session/`.

---

*2026-10-27 · Mavis Local · măsurat · aditiv*
