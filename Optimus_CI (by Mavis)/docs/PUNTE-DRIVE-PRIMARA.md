# PUNTEA DRIVE — specificația completă

> **Aditiv.** Nu rescrie nimic existent. Completează `docs/CI-POLICY.md`
> §1 și `docs/BRIDGE-LOCAL-CLOUD.md`.
>
> Măsurat: **2026-10-27**. Metodă: `gh api`, baza de metadate DriveFS,
> logurile DriveFS, rularea scripturilor.

---

## 1. De ce s-a schimbat

| | Până acum | De acum |
|---|---|---|
| Canal primar | repo-ul `MAVIS-CLOUD` pe GitHub | **folder Google Drive** |
| Canal secundar | — | repo-ul, prin `QUEUE/TASKS-FOR-CLOUD.md` |
| De ce | Git e bun la istoric, diff, rollback | **ambele instance au acces la Drive**; Cloud-ul îl are deja |
| Ce pierde canalul Drive | — | **instantaneitatea** (≈ 80 min, măsurat) |

Regula lui Popy, 2026-10-27: *„You don't need to — you can both connect to
the Drive. If you work locally, Google Drive app will automatically sync
everything to Drive."* **Verificat și corectat unde trebuie**: automat
înseamnă *eventual*, nu *instant*. Diferența e măsurată mai jos.

---

## 2. Topologia, măsurată

```
Drive (server)
   │  contul Google al lui Popy, id 100488352004104984848
   ▼
E:\Google\GDrive\                 ← mirrorul (rădăcină: Google\GDrive, root_id=23, MIRROR)
   └── GDrive-Second_Brain_PKMS\02_Areas\02-2-AI-SOT\CASA\OPTIMUS - Prime\
       └── Optimus_CI (by Mavis)   ← folderul CI, cloud_id 1V87h9Pbw52chSVNkxQ_NNuMh-CLfZeuI
              ├── BRIDGE-DRIVE\   ← PUNTEA
              ├── QUEUE\          ← canal secundar (GitHub)
              └── docs\, scripts\ ← SOT-ul CI
```

**Joncțiune pentru acces rapid:**
`C:\Users\apviz\.minimax-agent\projects\Optimus_CI (by Mavis)` → sursa de
pe `E:`. **Nu e o copie** — e aceiași octeți. Editarea se face oriunde.

**Corectare a topologiei documentate:** `G:` **nu** e un mount virtual Google
Drive. E un volum fix, iar `G:\My Drive.lnk` e o scurtătură cu ținta
`E:\Google\GDrive`. Mirrorul real e pe `E:`.

**Date git:** `.git` e un **fișier** (worktree link) →
`gitdir: E:/Google/GitData-Optimus-CI/repo`. Istoricul nu stă în folderul
sincronizat, ci pe `E:`, în afara mirrorului.

---

## 3. Ce se măsoară, și cu ce

| Întrebare | Instrument | Sursa de adevăr |
|---|---|---|
| Folderul există în Drive? | `drivefs_probe.py --title <nume>` | `items` din `metadata_sqlite_db` |
| Fișierul a ajuns în Drive? | `drivefs_probe.py --title <nume>` | id cloud + lanț de părinți |
| Rădăcina mirrorului e conectată? | `drivefs_probe.py --root-state` | `drive_fs.txt`, `ReceiveMirrorRoots` |
| Cât a durat propagarea? | `--newest <folder>` vs mtime local | `modified` din indice |
| Coada de upload | `--pending` | `operations` |

**De ce nu prin API-ul Drive?** Pentru că ruta de API e ** ruptă** pe această
mașină, măsurat:

| Rută | Rezultat |
|---|---|
| `gdrive-mcp` (namespace minimax) | `invalid_grant` la `files.list` — tokenul de reîmprospătare e revocat |
| `verify-drive.js` (același token) | `userinfo failed: invalid_grant`, `DRIVE v3 files.list FAILED`, **EXIT 2** |
| `gcloud` ADC | `authorized_user`, dar Drive API → **HTTP 403** (nu are scope de Drive) |

Reînnoirea tokenului cere **consimțământul lui Popy în browser** — e un act
ACCESS, nu o decizie tehnică. Până atunci, **baza locală a DriveFS e sursa de
adevăr**, și funcționează: `metadata_sqlite_db` (422 932 480 B) se citește
read-only; `mirror_metadata_sqlite_db` (2 278 027 264 B) e blocată de
DriveFS și **nu** e accesibilă.

---

## 4. Latentța, măsurată

| Scriere locală | Apariție în Drive | Lag |
|---|---|---|
| `README_SYSTEM_TOPOLOGY_AND_AGENT_GUIDELINES.md`, 2026-10-26 **22:11** | 2026-10-26 **23:31** | **≈ 80 min** |

**De ce atât?** DriveFS s-a repornit la **22:43** pe 26 octombrie (dovadă în
`drive_fs.txt`), în mijlocul propagării. O coadă de încărcare după un
restart explică cea mai mare parte a lag-ului. **Lag-ul în regim normal nu
e măsurat** — și nu e presupus nici el.

### 4.1 Re-măsurare 2026-10-27, ~01:15 local — propagarea nu a pornit

| Ce | Măsurat |
|---|---|
| Ultima confirmare în indice | `LAST_CONFIRMED_UPLOAD_MS=1793020483545` → **26 oct, 15:12 local** (era fișierul `.git`, scris la mutarea sursei) |
| Cea mai recentă scriere locală publicabilă | `LAST_LOCAL_WRITE_MS=1793056605455` → **27 oct, 01:16 local** |
| Lag | **602 min** |
| `BRIDGE-DRIVE` în indicele Drive | **FOUND=0** — nu e acolo |
| `PENDING_OPERATIONS` | **0** |
| `MIRROR_ROOT_STATE` | **`true`** — rădăcina e conectată |

**Rădăcina e conectată, dar nu încarcă.** Nu e o măsurătoare defectă: motorul
de sync al DriveFS scrie singur, în `drive_fs.txt`:

```
sync_engine.cc:2636: Sync engine activity state:
operation_queue_size: 0
all_downloads: 0
change_ids_up_to_date: true
largest_local_change_id: 9281302
fetching_changes: false
```

`change_ids_up_to_date: true` + `operation_queue_size: 0` = **DriveFS nu
vede scrierile mele locale**. Nu e o întârziere: e o lipsă de activitate —
`largest_local_change_id` nu s-a mișcat.

În plus, `drive_fs.txt` arată o eroare IPC repetată la fiecare 60 de secunde,
activă și la momentul măsurării:

```
ipc_socket_win.cc:272: GetOverlappedResult() failed:
shell_ipc_server.cc:256: OnRequestArrived Failed to receive/deserialize
ShellIpcRequest: FAILED_PRECONDITION ... The pipe has been ended
```

**Verdictul instrumentului, reparat în acest proces:** o rădăcină
conectată nu e un transport care încarcă. `mavis-drive-bridge.ps1 -Status`
raporta `TRANSPORT=UP` și `ACTIVE_CHANNEL=DRIVE` cât timp nu exista
confirmare — un **fals pozitiv**. Acum raportează separat:

| Câmp | Semnificație |
|---|---|
| `TRANSPORT=UP` | rădăcina mirrorului e conectată |
| `PROPAGATION=OK` | ultima scriere locală e confirmată în indice |
| `PROPAGATION=STALE` | scrieri locale mai noi decât ultima confirmare |
| `ACTIVE_CHANNEL` | `DRIVE` doar dacă propagarea e `OK`; altfel `GITHUB` |

Codul de ieșire al `-Status` e **4** (nu 0) când propagarea e `STALE`:
„scris, neconfirmat". Iar măsurătoarea lag-ului **nu mai numără `state/`**,
care e scratch ignorat de git — altfel orice fișier de probă ar face lag-ul
să pară infinit, ceea ce ar fi o măsurătoare falsă, nu o întârziere reală.

Poarta verifică acum **concordanța** raport–măsurătoare, cu 5 probe de
falsificare: un raport doctorit cu `PROPAGATION=STALE` dar
`ACTIVE_CHANNEL=DRIVE` este **respingat**.

### 4.2 Cât de veche e copia din cloud — măsurătoarea directă

Lag-ul de mai sus e un **proxy**: compară ultima confirmare cu ultima scriere.
Însă ce contează pentru Cloud e altceva — **cât de veche e conținutul pe care
l-ar citi**. Am adăugat măsurătoarea directă: `drivefs_probe.py --staleness`,
care ia itemul din indexul de cloud și îl compară cu fișierul local.

| Fișier | În cloud? | Vârsta copiei din cloud | Local mai nou cu |
|---|---|---|---|
| `MAPARE-SISTEM.md` (urmărit, în cloud) | **da** — `cloud_id 1I2W52G0Z0YALe-L5TAR68nQkkmx6zper` | **2,91 zile** | **4158,7 min** (≈ 69 h) |
| `DOCTRINA-CI.md` (urmărit, în cloud) | **da** — `cloud_id 1yP_8u-nC7wIpn1y05GuZ6u1O_RYCC-ni` | **~15 zile** (12 oct) | — |
| `TASKURI-PENTRU-CLOUD.md` (canalul primar) | **NU** | — | — |

**Ce înseamnă asta, fără cosmetizare:** arborele CI **există în cloud**, cu
`cloud_id`-uri și la calea corectă — dar cu **conținutul dinainte de mutarea
din 26 oct**. Mutarea a fost la nivel de metadată: itemii de cloud și-au
păstrat identificatorii, iar conținutul **nu s-a reîncărcat niciodată**.

Deci, dacă Mavis Cloud ar citi acum folderul din Drive, ar citi **un
instantaneu vechi**, nu conținutul de azi. „Folderul e în Drive" și „conținutul
de azi e în Drive" sunt două lucruri diferite — și al doilea e fals.

Instrumentul raportează acum asta direct, nu prin proxy:

```
CLOUD_TRACKED_AGE_DAYS=2.91
CLOUD_TRACKED_LOCAL_NEWER_MIN=4158.7
CLOUD_CHANNEL_FILE_PRESENT=false
PROPAGATION=STALE
ACTIVE_CHANNEL=GITHUB
```

iar poarta are acum și invariantul care leagă aceste cifre: **dacă fișierul
canalului nu e în cloud, propagarea NU poate fi `OK`**. Un raport care ar
spune altceva ar acuza fals transportul. Probe doctorat în acest sens:
`raport fals: fisierul canalului absent din cloud dar propagare OK` —
**respingut**.

Consecință de proiectare: **cerințele care cer răspuns imediat nu merg pe
Drive.** Ele merg pe canalul secundar (GitHub), care are R0 la push.

---

## 5. Regulile de funcționare

1. **Un task, două canale, același `TASK_ID`.** Scris simultan. Nu „dacă
   primul cade, atunci scriu în al doilea" — pentru că atunci pierzi timp
   exact când transportul e bolnav.
2. **Publicat = măsurat.** Scriptul verifică în indice și raportează
   `SYNCED` / `PENDING` / `NOT_UPLOADED` / `UNVERIFIED`. `UNVERIFIED` **nu**
   e succes.
3. **Nu se suprascrie nimic.** Corecția = fișier nou.
4. **Nu se șterge nimic.** Se mută în `ISTORIC/`.
5. **Zero secrete în punte.** Se scanază index-ul înainte de commit, ca
   peste tot.

---

## 6. Granța R0

| Operație | Cere R0? | De ce |
|---|---|---|
| Scriere în `BRIDGE-DRIVE/` | **nu** | e fișier local, se sincronizează |
| Scriere în `QUEUE/TASKS-FOR-CLOUD.md` | **nu** | idem |
| Commit local pe `main` | **nu** | regula permanentă |
| **Push spre GitHub** | **da** | singura operație externă |
| Re-autentificarea DriveFS | **nu** (tehnic), dar **necesită Popy** | poate cere re-login |

---

## 7. Ce rămâne de făcut, măsurat

| # | Ce | De ce nu l-am făcut eu |
|---|---|---|
| 1 | Re-consent pentru tokenul Drive (`gdrive-oauth.js`) | cere browserul lui Popy — ACCESS |
| 2 | Verificarea DriveFS: rădăcina e `connected=true`, dar motorul de sync nu vedea scrierile locale (`change_ids_up_to_date: true`, `operation_queue_size: 0`), iar logul arată o eroare IPC activă la fiecare 60s | DriveFS e procesul lui; un restart / re-login e decizie pe mașina lui |
| 3 | Re-măsurarea lag-ului în regim normal | nevoie de o propagare completă, ~1h+ |
| 4 | Push-ul celor 12 commituri locale în `MAVIS-OPTIMUS-CI` | **R0**, și remote-ul a avansat între timp |

---

*2026-10-27 · Mavis Local · aditiv · măsurat*
