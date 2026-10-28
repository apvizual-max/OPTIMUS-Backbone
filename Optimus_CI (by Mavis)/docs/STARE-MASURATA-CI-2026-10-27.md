# STARE MĂSURATĂ — CI — 2026-10-27

> **Aditiv.** Nu rescrie `docs/STARE-MASURATA-CI.md` (care rămâne istoricul
> din 2026-10-24). Acesta e măsurătoarea de **azi**, cu metodele.
>
> Măsurat pe mașina lui Popy, 2026-10-27, între 00:05 și 01:20.

---

## 1. Topologia — măsurată

| Ce | Valoare | Metodă |
|---|---|---|
| Sursa fizică a proiectului CI | `E:\Google\GDrive\GDrive-Second_Brain_PKMS\02_Areas\02-2-AI-SOT\CASA\OPTIMUS - Prime\Optimus_CI (by Mavis)` | `Get-Item` + joncțiune |
| Joncțiunea de pe C: | `C:\Users\apviz\.minimax-agent\projects\Optimus_CI (by Mavis)` → `E:\…\Optimus_CI (by Mavis)` | `LinkType=Junction`, `Target` |
| `.git` | **fișier**, nu director → `gitdir: E:/Google/GitData-Optimus-CI/repo` | citire conținut |
| **G: NU e mount virtual** | volum fix; `G:\My Drive.lnk` → target `E:\Google\GDrive` | `WScript.Shell.CreateShortcut` + `fsutil fsinfo drivetype` |
| DriveFS | rulează, `version 132.0.0.0`, startup 2026-10-26 **22:43** | `Get-Process`, `drive_fs_507.txt` |
| Rădăcina mirrorului My Drive | `Google\GDrive`, `root_id=23`, `sync_type=MIRROR`, **connected=true** | `MirrorRoots`, anunțul cel mai recent, în toate logurile |
| Cache-ul de conținut | `E:\Google\Cache\100488352004104984848\content_cache` | `content_cache_path` |

**Atenție la o capcană de citire:** la același startup (22:43:01.70x) există
trei dump-uri de rădăcini. Primul spune `connected=false` pentru rădăcina
GDrive, ultimul spune `connected=true`. **Proba citește ultima apariție** —
starea finală. Citirea manuală a primului dump ar da diagnosticul greșit.

**A doua capcană, măsurată mai târziu în aceeași zi:** DriveFS **rotește
logurile**. Sesiunea activă scria în `drive_fs_507.txt`, iar `drive_fs.txt`
nou conținea doar urma unei **lansări eșuate** (`CANNOT_START_IPC`). Un
instrument care citește un nume de fișier fix citește un log mort. Detalii:
§7.

---

## 2. Puntea Drive — măsurată

| Ce | Valoare | Metodă |
|---|---|---|
| cloud_id al folderului CI | `1V87h9Pbw52chSVNkxQ_NNuMh-CLfZeuI` | `items` din `metadata_sqlite_db` |
| Calea în Drive | `My Drive > GDrive-Second_Brain_PKMS > 02_Areas > 02-2-AI-SOT > CASA > OPTIMUS - Prime > Optimus_CI (by Mavis)` | lanț `stable_parents` |
| Fișiere locale ajunse în Drive (create 24 oct, niciodată pe GitHub) | `STARE-MASURATA-CI.md` → `1yg2iC1kboRgZjhYeXhu-SqDBqkKKdGlY` | idem |
| Lag de propagare | **≈ 80 min** (22:11 → 23:31, 26 oct) | `modified` vs mtime |
| Coadă de operațiuni | `PENDING_OPERATIONS=0` | `operations` |
| Fișiere noi (create 00:35) în indice, la 01:05 | **nu încă** | idem — lag încă în desfășurare |

**Prin urmare:** puntea funcționează, **dar nu e instantă**. Nu se promează
latență sub o oră fără măsurătoare.

### Rutele de API — măsurate ca rupte

| Rută | Rezultat |
|---|---|
| `gdrive-mcp` (namespace minimax) | `invalid_grant` |
| `verify-drive.js` (același token) | `DRIVE v3 files.list FAILED`, **EXIT 2** |
| `gcloud` ADC (`authorized_user`) | Drive API → **HTTP 403** (fără scope de Drive) |

---

## 3. Instrumentele — măsurate

| Instrument | Stare | Notă |
|---|---|---|
| `scripts/drivefs_probe.py` | ✅ | `--title`, `--newest`, `--root-state`, `--pending`, `--staleness` |
| `scripts/mavis-drive-bridge.ps1` | ✅ | `-Status`, `-Publish`, `-Verify` |
| `scripts/mavis-drive-bridge-selfcheck.ps1` | ✅ | **16 probe**, `BRIDGE_PROBLEMS=0 UNKNOWN=0`, **EXIT 0** |
| `metadata_sqlite_db` | ✅ lizibil read-only | 422 932 480 B |
| `mirror_metadata_sqlite_db` | ❌ blocat de DriveFS | 2 278 027 264 B; `immutable=1` refuzat |

**Python 3.14.6** prezent. **`gh`** funcțional.

---

## 4. Repo-urile — măsurat

### `apvizual-max/MAVIS-OPTIMUS-CI` (remote)

| Ce | Valoare |
|---|---|
| Vizibilitate | **public** |
| `pushed_at` | **2026-10-24T23:55:56Z** (înainte: 14:35:06Z) |
| Dimensiune | 99 KB |
| Workflow-uri | **niciunul** (404 pe `.github/workflows`) |
| Secrete | **niciun** |
| `main` remote | `3da55ff56249f9ec7d299c88e10e27de039be6f` |

### Local vs remote — divergență

| | |
|---|---|
| Local `main` | `83b61398a4d255b57cddc9ec7096c21403abd095` |
| Remote `main` | `3da55fff56249f9ec7d299c88e10e27de039be6f` |
| **Înainte / înapoi** | **12 / 5** |

Cele 5 commituri remote sunt **lucrarea celeilalte sesiuni** (CD): două
merge-uri de PR-uri Jules (`meta-prompt.ps1` path traversal, `mavis-sync`
pipeline) + `docs(cd)` + cele două merge-uri.

**Decizie:** nu împingem fără R0 **și** nu rebazăm cu forța. Divergența se
documentează; sincronizarea e o operație cu R0, într-un rând cu restul.

### `apvizual-max/MAVIS-CLOUD` — neschimbat

Canalul **secundar** al punții. Nu e atins de acest rând.

### CD — în paralel

| Ce | Valoare |
|---|---|
| Sursa fizică | `E:\…\CASA\OPTIMUS - Prime\Optimus_CD (by Jules)` |
| HEAD | `5efc70b` — „CD: masuratoarea fals-zero reparata + gard Jules + poarta invariant ramuri" |
| Remote | **neconfigurat** |

---

## 5. Poarta de push și guvernanța

| Ce | Stare |
|---|---|
| `core.hooksPath` per repo | instalat în CI și CD |
| `core.hooksPath` **CI** | `E:/Google/GitData-Optimus-CI/repo/hooks` — **director propriu**, cu `pre-commit` + `pre-push` **delegat** |
| `core.hooksPath` **CD** | `C:/Users/apviz/.minimax-agent/projects/scripts/git-hooks` — **neafectat** (poarta comună) |
| Poarta de push, fără martor | **EXIT 1** (măsurat) |
| Delegarea `pre-push` în repo-ul real | **EXIT 1** + mesajul porții comune (măsurat) |
| Scanare secrete pre-commit | `BLOCKS=0 WARNS=0 SCAN_OK` — **scanner propriu CI**: `scripts\scan-staged-secrets.ps1` |
| Auto-proba scannerului | `SECRET_PROBLEMS=0 UNKNOWN=0`, **EXIT 0** — 7 probe |
| Falsificarea lanțului de porți | `GATE_PROBLEMS=0`, **EXIT 0** — commit curat permis · commit cu secret **refuzat** · secret **absent** din istoric · push fără acord **refuzat** · push cu acord permis |
| Puntea `mavis-sync -SelfTest` | `POARTA|TRECUT`, EXIT 0 |
| Puntea `run-sync-logged -DryRun` | EXIT 0 |
| Propagare Drive | **`PROPAGATION=STALE`** — lag **611,7 min**, `BRIDGE-DRIVE` `FOUND=0` în indice |
| **Vârsta copiei din cloud** | **`CLOUD_TRACKED_AGE_DAYS=2.91`** pentru `MAPARE-SISTEM.md`; localul e cu **4158,7 min** mai nou |
| Fișierul canalului primar în cloud | **`CLOUD_CHANNEL_FILE_PRESENT=false`** — `TASKURI-PENTRU-CLOUD.md` nu e în cloud |
| Conținutul arborelui CI în cloud | **dinainte de mutarea din 26 oct** (`DOCTRINA-CI.md` — 12 oct, `MAPARE-SISTEM.md` — 24 oct). Mutarea a fost la nivel de metadată, cu `cloud_id`-uri păstrate |
| Motor sync DriveFS | `operation_queue_size: 0` · `change_ids_up_to_date: true` · `largest_local_change_id: 9281302` — **nu vede scrierile locale** |
| Canal activ | **`GITHUB`** (pentru conținut nou) — `TRANSPORT=UP`, dar propagarea nu e confirmată |
| Cod de ieșire `-Status` | **4** când propagarea e `STALE` (nu 0) |
| Eroare IPC DriveFS | `ipc_socket_win.cc:272` „The pipe has been ended", repetată la 60s, activă la măsurare |

---

## 6. Ce s-a schimbat în acest rând

| # | Ce | Stare |
|---|---|---|
| 1 | Structura `BRIDGE-DRIVE/` cu 4 canale + protocol | ✅ |
| 2 | Canalul secundar `QUEUE/TASKS-FOR-CLOUD.md` | ✅ |
| 3 | `drivefs_probe.py` — măsurătorul | ✅ |
| 4 | `mavis-drive-bridge.ps1` — publicare + măsurătoare | ✅ |
| 5 | `mavis-drive-bridge-selfcheck.ps1` — poarta, 6 probe | ✅ |
| 6 | Documentație: acest fișier + `docs/PUNTE-DRIVE-PRIMARA.md` + actualizări aditive | ✅ |
| 7 | Scanner de secrete **propriu CI** + auto-proba (7 probe, ambele sensuri) | ✅ |
| 8 | Hook `pre-commit` în directorul per-repo al CI | ✅ |
| 9 | `pre-push` delegat către poarta comună (CD neatins) | ✅ |
| 10 | Falsificarea lanțului de porți, în repo izolat, GitHub neatins | ✅ |
| 11 | Primul handoff publicat pe **ambele** canale | ⚠️ `TASK-2026-10-27-0103-…` · `SYNC_STATE=UNVERIFIED` (scris, neconfirmat în indice) |
| 12 | Folderul fantomă `…\projects\Mavis-Optimus-Continuous-Integration` | ✅ eliminat prin Trash recuperabil, 3 niveluri, EXIT 0 |
| 13 | Instrumentul reparat: `TRANSPORT` separat de `PROPAGATION`, `state/` exclus din măsurătoarea de lag, canalul activ urmează propagarea | ✅ |
| 14 | Poarta extinsă: 5 probe de falsificare a concordanței raport–măsurătoare | ✅ |
| 15 | Măsurătoare directă a vârstei copiei din cloud (`drivefs_probe.py --staleness`) + invariantul „fișierul canalului absent ⇒ propagarea nu poate fi OK" (6 probe de concordanță) | ✅ |

**Nepropus, intenționat:** push-ul celor 12 commituri locale (R0, plus
divergența cu remote-ul avansat).

---

## 7. Două defecte de măsurătoare, găsite și reparate

> **Aditiv.** Măsurat 2026-10-27, în jurul orei 02:00. Nimic de mai sus nu
> se rescrie.

### 7.1 Defectul 1 — sonda citea un log mort

**Simptom:** poarta raporta `UNKNOWN proba-transport — starea rădăcinii
mirrorului nu s-a putut citi`, cu `BRIDGE_PROBLEMS=0 UNKNOWN=1`. Era
`UNKNOWN=0` cu câteva ore înainte. Sistemul nu se schimbase — **se schimbase
instrumentul**.

**Cauza, măsurată:** DriveFS **rotește logurile**. Sesiunea activă scria în
`drive_fs_507.txt` (mtime în continuă actualizare), iar `drive_fs.txt` —
fișierul cu nume fix, pe care îl citea sonda — conținea doar urma unei
**lansări eșuate**:

```
drive_fs.cc:818:RunDriveFS Return code: CANNOT_START_IPC
base_ipc_server.h:61:StartInternal There is already an IPC server at \\.\Pipe\GoogleDriveFSPipe_apviz
```

Sonda citea `drive_fs.txt` → **0 linii `MirrorRoots`** → `ROOT_STATE=UNKNOWN`.

**Consecința reală:** un transport **funcțional** era raportat ca
necunoscut. E fals negativ — ascunde o punte care merge.

**Reparația:** sonda scanează acum **toate** logurile `drive_fs*.txt`, în
ordinea descrescătoare a mtime-ului, și ia **anunțul cel mai recent despre
rădăcina GDrive**, ordonat după **amprenta de timp din interiorul liniei**
(UTC, ISO-8601) — nu după numele fișierului, nu după mtime. Un fișier al
cărui mtime e mai vechi decât anunțul găsit nu poate conține unul mai nou,
deci scanarea se oprește acolo.

**Defect ascuns, găsit în aceeași reparare:** codul vechi lua primul
`title=` și primul `connected=` din **linia** — dar o linie `MirrorRoots`
conține **mai multe rădăcini**. Putea raporta starea rădăcinii GDrive de la
**altă rădăcină**. Acum fiecare rădăcină e împărțită și asociată cu
`connected=` ei.

### 7.2 Defectul 2 — instrumentul spunea `TRANSPORT=UP` pe baza unei măsurători nereușite

Codul vechi avea:

```powershell
if ($root.State -eq 'false') { ...TRANSPORT=DOWN...; return 5 }
Write-Out 'TRANSPORT=UP'      # <- prinde si UNKNOWN
```

`UNKNOWN` trecea pe ramura `UP`. **Un instrument care afirmă ceva ce n-a
măsurat.** Iar poarta n-o vedea: regula de concordanță verifica doar
`false→DOWN` și `true→UP`, și pentru `UNKNOWN` poarta scria `UNKNOWN` în loc
să verifice.

**Reparația:** `UNKNOWN` are ramura ei — `TRANSPORT=UNKNOWN`, canal activ
GitHub, ieșire **4**. Noul `TRANSPORT=UNKNOWN` se propagă și în poartă: o
raportare cu rădăcina `UNKNOWN` și transport `UP` e **respinsă**.

### 7.3 Falsificarea — în ambele sensuri

| Probă | Așteptare | Măsurat |
|---|---|---|
| Log nou spune `connected=false`, log vechi spune `connected=true` | câștigă anunțul **nou** | `ROOT_STATE=false`, `LOG=drive_fs_901.txt` ✅ |
| GDrive **al doilea** root într-o linie cu `Documents` primul | cuplare **per-rădăcină** | `ROOT_STATE=true` (GDrive), nu starea lui Documents ✅ |
| Niciun anunț despre GDrive | `UNKNOWN` + ieșire **3** | `ROOT_STATE=UNKNOWN`, exit 3 ✅ |
| Poarta cu raport falsificat (rădăcină `UNKNOWN` + transport `UP`) | **respins** | `proba-concordanta` OK — falsul e respins ✅ |
| Raport adevarat (rădăcină `UNKNOWN` + transport `UNKNOWN`) | **acceptat** | `proba-concordanta` OK ✅ |
| Sonda citește `drive_fs.txt` neatins de >30 min | **FAIL** | `proba-log` — regula e în poartă ✅ |

**Starea după reparație:**

```
BRIDGE_PROBLEMS=0 UNKNOWN=0     EXIT 0     (16 probe)
SECRET_PROBLEMS=0  UNKNOWN=0     EXIT 0     (7 probe)
TRANSPORT=UP   PROPAGATION=STALE   ACTIVE_CHANNEL=GITHUB   exit 4
CLOUD_TRACKED_AGE_DAYS=2.93   CLOUD_CHANNEL_FILE_PRESENT=false
```

**Rădăcina e conectată** (`ROOT_STATE=true`, anunț `2026-10-26T22:43:24`,
citit din `drive_fs_507.txt`). **Propagarea e tot STALE** — asta e măsurătoarea
separată, și nu s-a schimbat prin repararea instrumentului.

### 7.4 Regula, pentru totdeauna

**Un nume de fișier fix nu e o măsurătoare.** Când un producător rotește
fișierele sale, instrumentul care citește `cei_mai_recenti.txt` citește, de
fapt, *ce a fost* recent — nu *ce e* recent.

**Și:** o stare **necunoscută** nu se traduce niciodată într-o stare
favorabilă. `UNKNOWN` → `UNKNOWN`. Un instrument care nu a măsurat nu are
dreptul să spună „merge".

---

## 8. Puntea zilnică (task 08:30) — ruptă și reparată

> **Aditiv.** Măsurat 2026-10-27, ~02:10. Nimic de mai sus nu se rescrie.

### 8.1 Ce era stricat

Rularea zilnică de la **08:30** — taskul `MavisSyncBridge` — **nu mai
funcționa**. Trei măsurători independente:

| Măsurătoare | Valoare | Metodă |
|---|---|---|
| `LastTaskResult` | **2147942667** = `0x8007010B` (`ERROR_DIRECTORY`) | `Get-ScheduledTaskInfo` |
| Ultimul log scris | **`mavis-sync-2026-10-25.log`** — de 25 oct | `logs\mavis-sync-*.log` |
| Acțiunea taskului | indica folderul **eliminat** `…\projects\Mavis-Optimus-Continuous-Integration\` | `(Get-ScheduledTask).Actions` |

Căderea începe odată cu consolidarea pe `E:` (26 oct). Taskul indica un
folder care nu mai există → `ERROR_DIRECTORY` → nu s-a mai scris niciun log
de la 25 oct încolo.

### 8.2 Trei defecte, în trei locuri

| # | Unde | Defect | Reparare |
|---|---|---|---|
| 1 | **Taskul Windows** | acțiunea indica folderul eliminat | re-pointată la `…\projects\Optimus_CI (by Mavis)` |
| 2 | **`scripts/mavis-sync.ps1`** | `$HQ` hardcodat pe calea eliminată → „clone-ul Cloud lipseste", ieșire 1 | `$HQ = Split-Path -Parent $PSScriptRoot` — **path-independent** |
| 3 | **`scripts/mavis-sync.ps1`** | se termina fără `exit` → moștenea `$LASTEXITCODE` de la ultima comandă git | `exit` explicit: `0` = puntea a mers, `4` = pull eșuat măsurat, `1` = nu s-a putut măsura |

**Doar repararea scriptului nu ar fi reparat puntea.** Taskul ar fi
continuat să apele un folder inexistent, iar scriptul reparat nu s-ar fi
apucat niciodată. Defectul era în **trei locuri**, și fiecare trebuia
găsit.

### 8.3 O etichetă care afirma ceva fals

La prima rulare după reparare, scriptul a comitat automat fișierele mele
cu mesajul:

```
cloud: ingest 2026-10-27 02:08 (citire read-only din MAVIS-CLOUD)
```

**Fals.** `cloud-ingest/` este în `.gitignore` (măsurat:
`git check-ignore -v cloud-ingest/MAVIS-CLOUD` → `.gitignore:4:cloud-ingest/`),
deci **niciun octet din MAVIS-CLOUD nu poate ajunge într-un comit**. Eticheta
afirma o proveniență pe care comitul nu o avea — și prima rulare a pus în
istoric o reparație de script etichetată drept ingest.

Reparat: mesajul spune acum ce se comite efectiv
(`local: checkpoint … ; cloud-ingest/ e gitignored, deci nu continut din cloud`).

### 8.4 Poarta nouă, cu falsificare în ambele sensuri

`scripts/mavis-sync-selfcheck.ps1` — **9 probe**, `SYNC_PROBLEMS=0
UNKNOWN=0 FALSIFIED=4`, **EXIT 0**:

| Probă | Ce cere |
|---|---|
| `proba-cale` | radacina e derivată din `$PSScriptRoot`, nu hardcodată |
| `proba-iesire` | scriptul are `exit` explicit → codul îi e propriu |
| `proba-eticheta` | mesajul de comit nu afirma conținut din cloud |
| `proba-falsificare` ×4 | copii doctorate (cale veche / fără `$PSScriptRoot` / fără `exit` / etichetă falsă) → **detectate** |
| `proba-poarta` | poarta de interzicere a push-ului e **intactă** (`SelfTest` = `POARTA\|TRECUT`) |

**Falsificarea porții pe scriptul real:** o copie doctorală (cale veche +
fără `exit`) → **3 FAIL, `SYNC_PROBLEMS=3`, EXIT 1**. Poarta poate eșua.

**O lecție din construcția porții:** detectorul de cale trebuie să citească
**doar codul executabil**, nu comentariile — altfel ar reproșa propria
documentare a defectului. Prima versiune a porții a raportat fals FAIL pe
scriptul deja reparat, pentru că finds în comentariul meu numele folderului
eliminat. Detectorul a fost reparat, **nu** comentariul.

### 8.5 Măsurătoarea de după

| | Înainte | După |
|---|---|---|
| `LastTaskResult` | **2147942667** (`0x8007010B`) | **0** |
| Ultimul log | 25 oct | **27 oct, 02:14** |
| Conținutul logului | — | `PAS1_CLOUD\|exit_pull=0` · `PAS2_LOCAL\|status=curat` · `FINAL\|…\|impingere=NEEXECUTATA` · „OK — sincronizare fara conflict, fara divergent" |
| `mavis-sync.ps1` | ieșire 1, „clone-ul Cloud lipseste" | ieșire **0** |
| `SYNC_PROBLEMS` | — | **0** · `FALSIFIED=4` · EXIT 0 |

**Puntea zilnică e vie din nou**, și e acum **măsurabilă**: are cod de ieșire
propriu, poartă, și falsificare.

---

## 9. Canalul secundar — o coadă plină pe care Cloud nu o putea citi

> **Aditiv.** Măsurat 2026-10-27, ~02:40. Nimic de mai sus nu se rescrie.

### 9.1 Ce părea

`QUEUE/TASKS-FOR-CLOUD.md` avea **3.352 B, 58 de linii**, două tichete
citibile cu ochiul, și un antet care zicea că e canalul secundar al punții.

### 9.2 Ce era, măsurat

Contractul consumatorului a fost citit **de pe disc**, nu din documentația
mea: `MAVIS-CLOUD/.skills/mavis-cloud-to-local-reporting/SKILL.md` (liniile
13–16) și `MAVIS-CLOUD/QUEUE/TASKS-FOR-CLOUD.md` (blocul `## Format`).

| Măsurătoare | Valoare | Metodă |
|---|---|---|
| Câmpuri de contract în coada CI | **0 din 5** | numărare pe fișier |
| Anteturi `### [id] titlu` | **0** | numărare pe fișier |
| Anteturi `## TASK-…` (invizibile pentru Cloud) | **2** | numărare pe fișier |
| Tichete cu `scope:` | **0** | numărare pe fișier |
| `QUEUE/DONE/` în repo | **absent** | `Test-Path` |
| Ultima linie a cozii | `Nu intai` — mijloc de propoziție | citire octet cu octet |

**Cloud rulează doar tichetele cu `scope: cloud`** (skill-ul Cloud-ului, pas
3). Cu zero `scope:`, ar fi executat **zero** tichete — și n-ar fi raportat
nimic greșit.

### 9.3 Trunchierea era în amândouă copiile

Și canalul primar (`BRIDGE-DRIVE/TASKURI-PENTRU-CLOUD.md`) se termina în
`Nu intai`. Receiptul de publicare (`state/drive-bridge-last-publish.json`)
arată că **scriptul** a publicat ticheta `TASK-2026-10-27-0103-…` la
`01:03:30` — deci corpul trunchiat a ajuns în publisher ca atare, iar
publisherul l-a scris în ambele canale și a raportat succes.

**Deci defectul nu era în fișier. Era în generator** — și în poarta care îl
lăsa să treacă.

### 9.4 Ce s-a reparat

| # | Unde | Reparare |
|---|---|---|
| 1 | `scripts/mavis-drive-bridge.ps1` | `-Publish` scrie copia secundară **în contractul consumatorului** (5 câmpuri + `scope` + `livrare`) |
| 2 | `scripts/mavis-drive-bridge.ps1` | `-Publish` **refuză** un corp trunchiat (exit 2) și un `scope` necunoscut (exit 2) |
| 3 | `scripts/mavis-drive-bridge.ps1` | după scriere, verifică `DUAL_CHANNEL_DRIVE` / `DUAL_CHANNEL_QUEUE` — regula „același TASK_ID" devine executabilă |
| 4 | `QUEUE/TASKS-FOR-CLOUD.md` | reconstruită în format de contract; tichetele păstrate, propoziția trunchiată completată **în ambele canale** |
| 5 | `QUEUE/DONE/README.md` | creat — ținta de livrare pe care Cloud o scrie |
| 6 | `docs/CONTRACT-CLOUD-QUEUE.md` | contractul, citat de pe discul Cloud-ului, cu data măsurării |
| 7 | `scripts/queue-contract-check.ps1` | poarta: 6 verificări + detectarea driftului de contract |
| 8 | `scripts/queue-contract-check-selfcheck.ps1` | auto-proba, 11 probe, falsificare în ambele sensuri |

### 9.5 Măsurătoarea de după

```
QUEUE_PROBLEMS=0 UNKNOWN=0        EXIT 0
TICKETS=2   TICKET_PROBLEMS=0
CONTRACT_SOURCE=MAVIS-CLOUD-LIVE   CONTRACT_DRIFT=NO
UNRECOGNISED_HEADERS=0             DONE_DIR=present

QUEUE_GATE_PROBLEMS=0 UNKNOWN=0 FALSIFIED=11    EXIT 0   (11 probe)
BRIDGE_PROBLEMS=0 UNKNOWN=0                     EXIT 0   (19 probe)
SYNC_PROBLEMS=0 UNKNOWN=0 FALSIFIED=4           EXIT 0   (9 probe)
```

### 9.6 Ce rămâne de decis de Popy (nu e tehnic)

În ce repo trăiește coada pe care Cloud o citește. Măsurat: Cloud citește
`MAVIS-CLOUD/QUEUE/TASKS-FOR-CLOUD.md`, **din repo-ul lui**. Coada din CI e
acum **conformă cu contractul** în oricare dintre cele două variante — deci
decizia lui nu e blocată de lipsa de pregătire. E o alegere de contract
între instanțe, nu o lipsă de tehnică.

---

*2026-10-27 · Mavis Local · măsurat*

---

## 10. Instrumentul combinării istoricului

> **Aditiv.** Măsurat 2026-10-27 · metodă: rulare directă pe repo-ul real.

### 10.1 Ce măsoară

`scripts\merge-check.ps1` (6861 B) — **dry-run**: `fetch` + divergență +
`git merge-tree --write-tree` + diff per parte. Nu atinge arborele de lucru,
nu creează commit, nu împinge.

| Ieșire | Valoare |
|---|---|
| `REMOTE_STATE` | `LIVE` — `fetch` reușit, măsurătoarea e pe remote-ul viu |
| `DIVERGENCE_BEHIND` / `AHEAD` | `5` / `24` |
| `LOCAL` / `OTHER` | `576a500c…` / `3da55fff…` |
| `MERGE_TREE` | `8b11d68dd1847cc450276eca76030bf4818540fa` |
| `MERGE_CLEAN` / `CONFLICT_FILES` | `yes` / `0` |
| merged vs **local** | 6 fișiere, +74 / −13 — **lucrarea CD** |
| merged vs **remote** | 38 fișiere, +7309 / −230 — **lucrarea mea** |
| `VERDICT` | `curat - o singura operatie de combinare, fara rezolvare manuala` |

Ieșire: `0` curat · `1` conflict (fișierele sunt numite) · `2` **nemăsurabil**.

### 10.2 Auto-proba și falsificarea

`scripts\merge-check-selfcheck.ps1` (10142 B) — **5 probe pe repo reale**:
conflictul e produs de git, nu simulat.

```
MERGE_GATE_PROBLEMS=0 UNKNOWN=0 FALSIFIED=5     EXIT 0
```

Falsificare în ambele sensuri: poarta **stricată pe copie** →
`MERGE_GATE_PROBLEMS=3`, `POARTA A BLOCAT`, exit **1**; poarta reală neatinsă
(hash SHA256 identic înainte și după).

### 10.3 Două defecte măsurate în auto-probă

1. **`-Other` al fixture-ului se scurgea în proba 5.** `origin/sideB` există
   doar în repo-ul de test; pe repo-ul real divergența era ilizibilă →
   UNKNOWN. Repar: `-Other` opțional + `-RealRoot` explicit.
2. **`Write-Out` cu `Mandatory` arunca excepție** când poarta nu scrie nimic
   → crash pe calea de diagnostic, cu exit 1 **indistinctibil** de blocarea
   porții. Repar: `AllowEmptyString` în ambele scripturi; blocarea se
   dovedește acum prin marcaj, nu prin codul de ieșire.

Ambele scripturi: **ASCII pur** (0 octeți peste `0x7F`), **fără BOM**,
**0 erori de parse**.

---

## 11. Livrarea cozii în repo-ul Cloud-ului — măsurat (2026-10-27, ~06:40)

> **Aditiv.** Nimic din secțiunile de mai sus nu se rescrie.

### 11.1 Ce era greșit, măsurat

Contractul consumatorului, citit de pe discul lui Cloud
(`.skills/mavis-cloud-to-local-reporting/SKILL.md`, linia 12):

> `git pull --rebase origin main` — mereu primul. TASK-urile vin de aici.

Cloud-ul trage din **propriul repo** (`MAVIS-CLOUD`). Publisherul scria
canalul secundar în repo-ul **CI** (`MAVIS-OPTIMUS-CI`).

| Măsurătoare | Valoare |
|---|---|
| `TASK_ID`-uri în coada locală (CI) | **2** |
| `TASK_ID`-uri în coada din `MAVIS-CLOUD` `origin/main` | **0** |
| Dimensiunea cozii la remote | 1102 B, format vechi, 1 tichetă consumată (`[x]`) |
| Poarta contractului, înainte | `QUEUE_PROBLEMS=0` — **verde, greșit** |
| Divergența clonei Cloud-ului | 22 înapoi / 0 înainte |

### 11.2 Instrumentele

| Instrument | Ce face |
|---|---|
| `scripts/queue-lib.ps1` | parserul cozii — **o singură implementare** pentru poartă și livrare |
| `scripts/queue-deliver.ps1` | sync → scriere → secrete → commit → push → verificare la remote |
| `scripts/queue-deliver-selfcheck.ps1` | 15 probe, falsificare în ambele sensuri |
| `scripts/queue-contract-check.ps1` | + proba `DELIVERY` și proba căii de intrare |
| `scripts/scan-staged-secrets.ps1 -StagedDiff` | scanează **doar liniile adăugate** de schimbare |

### 11.3 Măsurătoarea de după

```
DELIVERY_SOURCE=MAVIS-CLOUD-ORIGIN-MAIN
DELIVERED=2/2
CLOUD_ENTRY=QUEUE/TASKS-FOR-CLOUD.md
QUEUE_PROBLEMS=0 UNKNOWN=0
```

| | |
|---|---|
| Commit în `MAVIS-CLOUD` | `4a88879` |
| `REMOTE_HEAD` | `4a88879` |
| `LOCAL_HEAD` | `4a88879` |
| `ls-remote` pe `MAVIS-CLOUD` | `4a88879…  refs/heads/main` |

### 11.4 Defecte găsite și reparate în acest rând

| # | Defect | Măsurarea lui |
|---|---|---|
| 1 | Tichetele ajungeau într-un repo din care Cloud-ul nu citește | 2 local vs **0** la remote |
| 2 | Poarta verifica **forma**, nu **livrarea** — verde pe o coadă absentă | `DELIVERED=0/2` după reparare |
| 3 | `$push` (local) vs `[switch]$Push` (parametru): pushul **rulea**, apoi scriptul murea cu exit 1 — codul 1 însemna și „tichete lipsă" | crash după push, `EXIT=1` |
| 4 | Livrarea reluată după un run blocat **adăuga ticheta a doua oară** ( lipsa se calcula față de remote, nu față de copia de lucru) | 2 apariții ale aceleiași tichete în coada remote-ului |
| 5 | Un corp **gol** arunca o excepție, iar crashul ieșea cu cod de verdict | `Test-ValueComplete` cu `AllowEmptyString` + `trap` → exit 2 |
| 6 | Un câmp declarat de două ori era înglobat în tăcut de parser | contor de declarații + refuz |
| 7 | Publisherul **refuza calea prin joncțiune** (C: → E:) → 7 probleme la auto-proba lui | `git rev-parse --show-prefix` |
| 8 | Scannerul de secrete bloca false, pe documentație **deja publicată** | 9 blocuri pe fișiere existente în `MAVIS-CLOUD` |
| 9 | Scannerul se bloca pe **propriul cod** (tokenuri-exemplu scrise literal într-un comentariu) | `proba-cod-propriu` → BLOCKS=1 |
| 10 | Coada locală purta un header care spunea că Cloud-ul citește acolo | header corectat pe loc |

### 11.5 Starea porților după

| Poartă | Rezultat |
|---|---|
| `queue-contract-check.ps1` | `QUEUE_PROBLEMS=0 UNKNOWN=0` · `DELIVERED=2/2` · EXIT 0 |
| `queue-contract-check-selfcheck.ps1` | `QUEUE_GATE_PROBLEMS=0 UNKNOWN=0 FALSIFIED=14` · EXIT 0 |
| `queue-deliver-selfcheck.ps1` | `DELIVER_GATE_PROBLEMS=0 FALSIFIED=15` · EXIT 0 |
| `scan-staged-secrets-selfcheck.ps1` | `SECRET_PROBLEMS=0 UNKNOWN=0` · EXIT 0 |
| `publish-ci-selfcheck.ps1` | 13 probe, incl. **joncțiune** · EXIT 0 |

Detalii: `docs/BRIDGE-LOCAL-CLOUD.md` §11 · `docs/WORKFLOWS.md` W14 ·
`README.md`.

---

## 12. Corecția drift-urilor vii din documentație

> **Aditiv.** Nimic din §1–§11 nu se rescrie — acolo e măsurătoarea acelui
> moment. Aici se înregistrează **corecțiile de fapt făcute pe loc**, cu
> măsurătoarea care le dovedește. Măsurat `2026-10-27, ~05:30Z`.

### 12.1 De ce a apărut driftul

Livrarea cozii secundare și împungerea au schimbat **fapte**, nu documente:
tichetele au ajuns în repo-ul consumatorului, workflow-ul a ajuns pe remote,
divergența s-a închis, PR-urile s-au închis. Documentele au continuat să
 spună starea de dinaintea împungerii. Un document care spune ce era
adevărat acum o oră și nu se verifică e o sursă de decizii greșite — nu de
istoric.

### 12.2 Cele 8 afirmații care au devenit false, și măsurătoarea lor

| # | Afirmația veche | Măsurarea de azi | Corectat în |
|---|---|---|---|
| 1 | „`.github/workflows/` dă **404** pe remote" | `ci-verify.yml` **pe remote**, blob `6f0fd55`; `merge-base --is-ancestor 65af38f origin/main` → exit 0 | `CI-POLICY.md` §8 · `MAPARE-FOLDERE.md` §8 · `WORKFLOWS.md` W8 · `INVENTAR-REPO-URI.md` §2 |
| 2 | „**17 commituri neîmpinse**" | `rev-list --left-right --count origin/main...main` → **0 0** | `INVENTAR-REPO-URI.md` §3 · `WORKFLOWS.md` W3 |
| 3 | „**22** PR-uri deschise" în `MAVIS-CLOUD` | `gh pr list --state open` → **0** | `INVENTAR-REPO-URI.md` §2 |
| 4 | clona `MAVIS-CLOUD` e „**read-only, nu se modifică**" | clona e și **copia de lucru a livrării**: HEAD = `origin/main` = `4a88879`, 2 tichete livrate | `README.md` · `INVENTAR-REPO-URI.md` §3 · `ARHITECTURA-CI-CD.md` · `PROTOCOL-DENUMIRE-LOCAL-CLOUD.md` · `MAPARE-SISTEM.md` · `MAPARE-FOLDERE.md` · `CI-POLICY.md` §4 |
| 5 | „remote = `15c5353` = HEAD local" | `ls-remote` = HEAD local (la citire: `8afa89b`) | `README.md` §„Starea acum" — **cifra a fost înlocuită cu metoda**, ca să nu se învechească la fiecare commit |
| 6 | `pushed_at` învechite în inventar | `gh repo list … --json pushedAt` → **5** repo-uri schimbate | `INVENTAR-REPO-URI.md` §1 |
| 7 | „**8** repo-uri din 10 sunt publice" | **7** publice, 3 private (numărate din `gh repo list`) | `INVENTAR-REPO-URI.md` §1 |
| 8 | taskul zilnic „la **08:30**" | `StartBoundary 2026-10-12T07:30:00+02:00` + `StartWhenAvailable=True` → pornire întârziată când mașina e stinsă (de aceea logurile vechi apar la 08:30) | `README.md` · `WORKFLOWS.md` W4/W9 · `ARHITECTURA-CI-CD.md` · `MAPARE-FOLDERE.md` · `CI-POLICY.md` §1.3 |

### 12.3 Ce n-am atins, și de ce

Documentele-**snapshot** cu dată în nume sau cu „măsurată 2026-10-24" în
text **rămân cum erau**: `STARE-MASURATA-CI.md`, `RECUPERARE-GIT.md`,
`CONFLICTE-DOZTRINA.md` §„STARE — 2026-10-24", `BRIDGE-LOCAL-CLOUD.md`
§„Stare curentă — măsurată 2026-10-24" și planul Gemini din 13 oct. Un
snapshot e o **măsurătoare a acelui moment**; a-l rescrie ar falsifica
istoricul, nu l-ar actualiza.

Documentele **vii** — `README.md`, `INVENTAR-REPO-URI.md`, `CI-POLICY.md`,
`ARHITECTURA-CI-CD.md`, `PROTOCOL-DENUMIRE-LOCAL-CLOUD.md`,
`MAPARE-SISTEM.md`, `MAPARE-FOLDERE.md`, `WORKFLOWS.md` — s-au corectat
**pe loc**, cu vechea afirmație păstrată ca istoric și corectarea lângă ea.

### 12.4 Trei măsurători care s-au dovedit nereproductibile

| Ce am măsurat | Prima măsurătoare | A doua | Ce s-a întâmplat |
|---|---|---|---|
| Fișiere în clona `MAVIS-CLOUD` | 591 | 651 | `git gc` împachetează obiectele loose: ±60 de fișiere în `.git/` |
| Fișiere în clona `MAVIS-CLOUD`, **fără `.git/`** | 443 | 475 | materializarea fișierelor-placeholder de pe DriveFS |
| Fișiere în **rădăcina CI**, fără `state/` și fără `cloud-ingest/` | 86 | 118 | **aceeași** materializare, în rădăcină: ±32 de fișiere |

Am învățat de aici trei reguli, deja scrise în `MAPARE-FOLDERE.md` §2:
**cifra de volum se raportează în fișiere urmărite de git** (`git ls-files` —
**68** în CI, **405** în clonă), **`.git/` nu intră în nicio cifră**, și
**octeții se dau per entitate, nu într-un total** — pentru folderele care se
editează, totalul se mută la fiecare editare.

**Cea mai scumpă lecție:** am scris în document un volum de „677 fișiere" și
l-am corectat în același rând — dar până la corectare, documentul purta o
cifră pe care **nu se reproducea**. O cifră care se schimbă la următoarea
măsurătoare nu e o măsurătoare, e o noroc. Cifra care se publică trebuie să
poată fi **remăsurată identică** de altcineva.

### 12.5 Măsurătorile de după

| | |
|---|---|
| `git rev-list --left-right --count origin/main...main` | `0 0` |
| `git ls-remote origin refs/heads/main` | `8afa89b…` = HEAD local (la citire) |
| `gh repo list apvizual-max --limit 60 --json pushedAt` | 10 repo-uri · 7 publice, 3 private |
| Clona `MAVIS-CLOUD` | 475 fișiere (fără `.git`) · HEAD = `origin/main` = `4a88879` · arbore curat |
| Arborele CI (fără `state/`, fără `.git/`) | 561 fișiere · 14.208.300 B · 68 fișiere urmărite de git |
| `Get-ScheduledTask MavisSyncBridge` | `StartBoundary 2026-10-12T07:30:00+02:00` · `StartWhenAvailable=True` · `LastTaskResult=0` (27 oct 02:14) |

---

## 13. Puntea bidirecțională, `Google_Access`, OAuth și filtrele Gmail

> **Aditiv.** Nimic din §1–§12 nu se rescrie — acolo e măsurătoarea acelui
> moment. Aici e **starea de la sfârșitul zilei**, măsurată `2026-10-27,
> 06:00–09:05Z`.

### 13.1 Puntea a devenit bidirecțională

| Ce | Valoare | Cum a fost măsurat |
|---|---|---|
| Răspunsuri ale Cloud-ului | **2** (08:49 și 12:07, ora lui) | fișiere noi în `BRIDGE-DRIVE/INTRARI-CLOUD/` |
| Răspunsuri trimise înapoi | **2** (`0815`, `0844`) | `DUAL_CHANNEL_DRIVE=True` + `DUAL_CHANNEL_QUEUE=True`; livrate `8ad1c12` / `3e5a0a7` |
| Tichete în coadă | **5** · `DELIVERED=5/5` | `queue-contract-check.ps1`, contractul citit de pe discul Cloud |
| Marcate `[x]` de Cloud | **3** (`0005`, `0735`, `0815`) | oglindite în copia locală |
| Lăsată deschisă intenționat | **1** (`0103`) | decizia Cloud-ului |
| `MAVIS-OPTIMUS-CI` | `5c4e1cf` = `origin/main`, divergență **0 0** | `ls-remote` + `rev-list --left-right --count` |
| `MAVIS-CLOUD` | `3e5a0a7` = `origin/main`, divergență **0 0** | idem |

### 13.2 Containerul `Google_Access`

| Ce | Valoare | Cum a fost măsurat |
|---|---|---|
| Stare | `running` · `healthy` · FailingStreak **0** | `docker inspect .State.Health` |
| Imagine | `google-access:1.0.2` | `docker images` |
| Grant | **live**, 9 scope-uri, `reauth_required: false` | `AUTH_STATUS` din probă: „token minted" |
| Unelte | **25** | handshake + apeluri de tool reale |
| Apeluri reale | Drive **5** fișiere · Gmail **3** mesaje · Books **403** (refuz explicit de scope, raportat ca atare) | `node probe.mjs` → `VERDICT=PASS`, exit 0 |
| **Sursa în GitHub** | `tools\google-access\` — 6 fișiere, SHA256 identic cu sursa vie, credential exclus prin `.gitignore` | copiere prin script + SHA256 pe fiecare fișier |

Containerul e **reconstruibil din GitHub**, nu de pe un singur disc.

### 13.3 Cele 8 defecte reparate în acest rând

| # | Defect | Măsurarea lui |
|---|---|---|
| 1 | Healthcheck-ul proba `8765` în timp ce containerul rula cu `GA_PORT=8766` | `unhealthy` la 9 intervale consecutive, serviciul răspundea HTTP 200 cu `grant=live` |
| 2 | Proba măsura **alt serviciu** (python, `hc-backend`) și ieșea cu **cod 0** | `HANDSHAKE=FAILED`, `TOOLS=0`, exit 0 |
| 3 | `server.mjs:32` — a treia sursă de adevăr despre port (fallback 8765) | corectat la 8766 |
| 4 | `google-auth.js` amesteca `client_id`/`secret` de la un client cu `refresh_token` de la altul | `invalid_grant` / `unauthorized_client`; falsificat: **5/8 cad** contra codului vechi, **8/8 trec** contra celui nou |
| 5 | `fix-mavis-filters.js` apela `PATCH` pe filtre — **metoda nu există** | discovery document Gmail v1: doar DELETE/GET/LIST/CREATE → 404 „Method not found"; plus etichete hardcodate (4 din 5 sărite) |
| 6 | `publish-ci-selfcheck` se aprindea roșu când publisherul făcea ce trebuie | așteptare derivată din starea măsurată; falsificat pe clonă murdară: refuz corect (exit 2), remote neatins |
| 7 | Protocolul se contrazicea despre **cine arhivează** (README vs antetul cozii) | „Cloud-ul marchează, Local mută" — într-un singur loc |
| 8 | Regula de excludere ancorată la un nume mort → **drum de scurgere spre un repo PUBLIC** | `mavis-sync.ps1:189` → `git add -A` + commit automat |

Filtrele Gmail `MAVIS/*`: **5 din 5 reparate** (celelalte 14 neatinse),
verificate independent prin API — 19 filtre, 5 cu acolade, fiecare cu eticheta vie.

### 13.4 Defectul 8, în detaliu — de ce a fost cel mai periculos

`chats/` (transcrierile sesiunilor) a fost **renumerit în Drive** cu
`Google_Connect/` pe 27 oct, 08:02, iar renumirea a coborât în arborele CI.
`.gitignore` excludea `chats/` — deci, după renumerire, regula nu mai prindea
nimic: `git status` arăta `?? Google_Connect/`. Iar `scripts\mavis-sync.ps1:189`
rulează `git add -A` + **commit automat** în rădăcina CI: următoarea rulare a
punții zilnice ar fi pus transcrierile în `MAVIS-OPTIMUS-CI`, care e **public**.

Reparat: regula acoperă acum **numele curent** (`Google_Connect/`) **și numele
marcant al raftului** (`**/Mavis-Cloud_Google-Setup-Session/`), ca să reziste la
o viitoare redenumire a părintelui. Falsificat: `git check-ignore -v` arată
ambele reguli, `Google_Connect/` a dispărut din `git status`, iar materialul
mutat **nu conține secrete** (doar `client_id`, identificator public).

### 13.5 Patru ieșiri de task de fundal recuperate

Busola spunea „2 fără ieșire disponibilă". Astăzi au devenit lizibile încă
4 ieșiri din 22 oct — care confirmă, independent, că eșecul de suite e
**preexistent pe `main`**, nu imputabil unui PR:

| Task | Ieșire | Ce dovedește |
|---|---|---|
| `bg_4141328b` | `MAIN_DEPLOY_EXIT=0` · `MAIN_SUITE_EXIT=1` | pe `main`: deployul trece, suita pică — baza de eșec e anterioară propunerii |
| `bg_5e13ef66` | `PR3_DEPLOY_EXIT=0` (checkout pe ramura PR3) | PR3 nu introduce eșecul de deploy |
| `bg_e0f7e39f` | `TRIAGE_EXIT=0` · Backbone #33–#37 `ADAPT/VERIFY=PASS` · SENTINEL_PRIME #1/#2 `UNVERIFIED` · #3 `REJECT/VERIFY=FAIL` | verdictele de triaj ale acelui moment (PR #1–#5 au fost închise/merge-uite pe 24 oct) |
| `bg_658ee6fc` | reluare de reproducibilitate: `test_deployment` → EXIT 1 | eșecul e reproducibil pe starea de bază |

### 13.6 Măsurătorile de după

| | |
|---|---|
| Bateria de porți | **8 porți, toate EXIT 0** (queue · queue-selfcheck · deliver-selfcheck · secrete · punte · punte-selfcheck · sync · merge · publish 13/13, `FALSIFIED=13`) |
| `queue-contract-check.ps1` | `TICKETS=5` · `TICKET_PROBLEMS=0` · `DELIVERED=5/5` · `QUEUE_PROBLEMS=0 UNKNOWN=0` · EXIT 0 |
| `MAVIS-OPTIMUS-CI` | `5c4e1cf` = `origin/main` · divergență `0 0` · `main` unic |
| `MAVIS-CLOUD` | `3e5a0a7` = `origin/main` · divergență `0 0` · `main` unic |
| Container | `running` · `healthy` · FailingStreak 0 · proba `VERDICT=PASS` exit 0 |
| Arborele CI | curat (`git status --porcelain` gol) |
| CD | neatins, în afară de `_Handoffs/` (SHA256 identic cu `docs/`) |

---

## 14. Al treilea răspuns al Cloud-ului (08:52) — coada e închisă

> **Aditiv.** Nimic din §1–§13 nu se rescrie. Măsurat `2026-10-27, ~09:15Z`.

### 14.1 Ce a venit

| Ce | Valoare | Cum a fost măsurat |
|---|---|---|
| Răspunsuri ale Cloud-ului | **3** (08:49, 12:07, **08:52**) | fișiere noi în `BRIDGE-DRIVE/INTRARI-CLOUD/` |
| Tichete marcate `[x]` de Cloud | **5 din 5** (erau 3) | marcajele citite **la vârful remote** al lui `MAVIS-CLOUD` (`930da7c`), nu din amintire |
| Livrabile în `QUEUE/DONE/` la Cloud | **5** | `git ls-tree origin/main QUEUE/DONE/` |
| Coada locală, după oglindire | `TICKETS=5` · `TICKET_PROBLEMS=0` · `DELIVERED=5/5` · `QUEUE_PROBLEMS=0 UNKNOWN=0` | `queue-contract-check.ps1` · auto-proba 14/14 |

### 14.2 Ce a reparat Cloud-ul — verificat de mine, nu preluat

`taxonomy.js` era sursa lui unică de adevăr, dar 6 scripturi o ocoleau: patru
foloseau `startsWith('MAVIS/')` (ar fi numărat **1 din 9** etichete), două aveau
**8 nume hardcodate** (ar fi creat 7 etichete noi, goale).

Verificat **independent**, în clona lui, la `930da7c`:

| Probă | Rezultat |
|---|---|
| `startsWith('MAVIS/')` în cele 6 scripturi | **0** apariții (metoda veche dă 1) |
| Referință la `taxonomy.js` | **6 din 6** |
| `node --check` pe cele 6 | exit **0** la toate |

### 14.3 Starea oglindită local

| Ce | Ce am făcut |
|---|---|
| Marcaje | `0103` și `0844` → `[x]`, cu linia `CONSUMAT` (ca `0815`) |
| Livrabile Cloud-ului | **4** copiate în `QUEUE/DONE/` (al 5-lea, `0815`, era deja acolo) |
| Arhive | **4** secțiuni arhivate în `BRIDGE-DRIVE/ISTORIC/` (`0005`, `0103`, `0815`, `0844`); `0735` era deja |
| Antetul cozii primare | corectat: „Cloud-ul marchează; **Local mută**" — era contradicția rămasă |
| Clona `MAVIS-CLOUD` | sincronizată `3e5a0a7` → `930da7c` (ff-only, divergență 0/0) |

**Nu s-a amputat nimic:** secțiunile rămân în canalul primar, iar arhiva e
**copie** cu conținutul păstrat integral — deci poarta de paritate rămâne
satisfăcută (`TICKETS=5`, `DELIVERED=5/5`), și nu stinge.

### 14.4 O neconcordanță de nume, măsurată

Livrabilele Cloud-ului referă `RASPUNS-MAVIS-CLOUD-2026-10-27-0812-raspuns-0844-etichete-live.md`,
dar fișierul din canalul primar e `...0852-...` (ora din antetul lui: 08:52 /
05:52 UTC). **Nu redenumesc fișierele celeilalte instanțe** — e înregistrat în
arhivă ca notă, nu corectat în loc.


