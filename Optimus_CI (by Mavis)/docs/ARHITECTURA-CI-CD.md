# ARHITECTURA CI ↔ CD — latura CI

> Oglinda documentului cu același nume din folderul CD
> (`…\Mavis-Optimus-Continuous-Development\docs\ARHITECTURA-CI-CD.md`).
> **Convenția e aceeași, privită din CI.**
>
> Decizie măsurată 2026-10-24. Pentru motivul separării și pentru ce s-a
> mutat efectiv, vezi latura CD.

---

## 1. Separarea e definitivă

| | **CI — Continuous Integration** | **CD — Continuous Development** |
|---|---|---|
| **Sesiune** | aceasta | sesiunea CD paralelă |
| **Folder** | `…\Mavis-Optimus-Continuous-Integration\` → **`…\Optimus_CI (by Mavis)`** (mutat pe `E:` în 2026-10-27; vezi §8) | `…\Mavis-Optimus-Continuous-Development\` |
| **Repo** | `apvizual-max/MAVIS-OPTIMUS-CI` | `apvizual-max/MAVIS-OPTIMUS-CD` |
| **Puntea** | Local ↔ Cloud: **Drive = canal primar**, `MAVIS-CLOUD` = canal secundar (vezi §8) | — |
| **Bucla de dezvoltare** | — | Jules + Live Review |
| **Task zilnic** | `MavisSyncBridge` 07:30 | `JulesDailyLoop` 09:00 |
| **Cota Jules** | nu e bugetul CI | 100 taskuri/zi, bugetul CD |

---

## 2. Ce ține CI

- **Puntea Local ↔ Cloud** și scriptul `scripts/mavis-sync.ps1`
- **Ingestul** din `MAVIS-CLOUD` (`cloud-ingest/`) — read-only pentru conținut,
  **și copia de lucru a livrării cozii secundare**
- **Canalul `QUEUE/TASKS-FOR-CLOUD.md`** — rămâne canalul Cloud
- **Procedurile Git/GitHub** pentru repo-ul Cloud
- **Guvernanța Git/GitHub** a repo-ului CI
- **Inventarul repo-urilor** de pe mașină

## 3. Ce ține CD

- **Platforma Jules**: `dispatch`, `verify`, `triage`, `adapt`, `daily`,
  `install`, `selfcheck`, `scan-staged`
- **Registrul repo-urilor** pentru Jules, contextul canonic, cardurile de task
- **Politica Live Review** și workflow-urile `jules.yml` / `verify.yml`
- **Verdicturile de triaj** și rapoartele de adaptare
- **Guvernanța Git/GitHub** a repo-ului CD

---

## 4. Punctul de contact

**`MAVIS-CLOUD` e comun, dar nu e al nimănui.**

- CD îl folosește ca **țintă** de lucru pentru Jules (triaj, adaptare).
- CI îl folosește ca **punte** (ingest + livrare cozii secundare, cereri de la Cloud).

**CD nu scrie în `MAVIS-CLOUD`.** Regula rămâne: `MAVIS-CLOUD` e **sursă
read-only pentru conținut**, cu excepțiile autorizate explicit. **A doua
excepție (27 oct):** Localul scrie ticheta cozii secundare în formatul de
contract — cerută de contractul consumatorului, aditivă, cu poartă de livrare.

**Instanța Cloud nu are rol în CD.** Nu triază, nu propune, nu
merge-uiește. Singura ei interacțiune cu CD e canalul `QUEUE/`.

---

## 5. Mișcarea efectivă — măsurată

| | |
|---|---|
| Subfolderul platformei | `Mavis-Optimus-Continuous-Integration\_JULES-Optimus_CI\` → `Mavis-Optimus-Continuous-Development\JULES - Optimus CD\` |
| Ștergeri în arborele CI la mutare | **33** (`git status --porcelain`) |
| Fișiere în folderul CD | **9 810** · **89 729 822 octeți** |
| Modificări de cale necesare în platformă | **2**, ambele reparate (§6) |

---

## 6. Cele două referințe la calea veche, reparate

Amândouă erau defecte latente: **nu se vedeau până când platforma se muta.**

### 6.1 `jules-scan-staged.ps1` — prefix hardcodat

Lista prefixelor platformei era
`_JULES-Optimus_CI/scripts/` și `_JULES-Optimus_CI/config/`.
După mutare, poarta ar fi aplicat regula brand-ului **chiar pe fișierele
care declară regula** — un fals pozitiv produs de o constantă veche.

Reparat: prefixul se **derivează** din numele folderului platformei.

### 6.2 `jules-install.ps1` — cale în mesaj

Mesajul sursei de context scria calea veche în `JULES-CONTEXT.md`, într-un
repo **public**. Reparat: se scrie calea **relativă, derivată**.

### 6.3 Verificarea reparărilor

Nu prin citire — prin rulare:

| Verificare | Rezultat |
|---|---|
| `jules-selfcheck.ps1` din locația CD | `FILES=10 PROBLEMS=0`, **EXIT 0**, 5 probe verzi |
| `jules-scan-staged.ps1 -RepoPath <CD>` | `STAGED=56 SCANNED=56 BLOCKS=0 WARNS=0 SCAN_OK`, **EXIT 0** |
| Scurgerile raportate de poartă | `JULES - Optimus CD/scripts/...` — prefixul derivat, corect |

Platforma e **independentă de cale** prin construcție:
`jules-lib.ps1:12` → `$script:JulesRoot = Split-Path -Parent $PSScriptRoot`.

---

## 7. Regula Triadei, reținută

```
1 conversație  =  1 folder local  =  1 repo GitHub
```

Proiectele nu se ating între ele. Când celălalt are nevoie de ceva, îi
dau un prompt, Popy îl duce în sesiunea respectivă, care are contextul
complet.

**Aceasta e și motivul pentru care nu ating repo-urile altor proiecte:**
nu am contextul lor, și un agent fără context într-un repo străin e exact
defectul pe care îl reparăm.

---

## 8. Topologia măsurată — 2026-10-27

Sesiunea CI a fost realocată pe `E:`. Aceasta nu e o schimbare de *conținut*,
ci de *suport*: acum sursa stă în chiar mirrorul Google Drive, ceea ce face
posibil canalul primar de mai jos.

| Element | Valoare măsurată |
|---|---|
| Sursa CI | `E:\Google\GDrive\GDrive-Second_Brain_PKMS\02_Areas\02-2-AI-SOT\CASA\OPTIMUS - Prime\Optimus_CI (by Mavis)` |
| Joncțiune locală | `C:\Users\apviz\.minimax-agent\projects\Optimus_CI (by Mavis)` → `E:` (`LinkType=Junction`) |
| `.git` | **fișier** (worktree link) → `gitdir: E:/Google/GitData-Optimus-CI/repo` |
| Calea veche | `…\projects\Mavis-Optimus-Continuous-Integration\` — **nu mai există** |
| `G:` | volum fix, **nu** mount virtual; `G:\My Drive.lnk` → `E:\Google\GDrive` |
| Rădăcina mirrorului | `Google\GDrive`, `root_id=23`, `sync_type=MIRROR` |
| Starea mirrorului | `connected=true` (starea finală = ultimul dump; primul dump din startup dă `false` — **capcană de citire**) |
| Folderul CI în Drive | `cloud_id 1V87h9Pbw52chSVNkxQ_NNuMh-CLfZeuI` |
| Latență de propagare | **≈ 80 min** (scriere locală 22:11 → prezență în Drive 23:31) |

Lanțul în Drive, măsurat pe `local_title` + `stable_parents`:

```
My Drive > GDrive-Second_Brain_PKMS > 02_Areas > 02-2-AI-SOT
        > CASA > OPTIMUS - Prime > Optimus_CI (by Mavis)
```

> **Capcană de măsurare:** blob-ul din `items.proto` e *latura cloud* (id +
> părinte + titlu). Căutarea textuală după **calea completă** nu se potrivește
> niciodată. Se caută după `local_title`, apoi se verifică lanțul de părinți.

---

## 9. Cele două canale — Drive primar, GitHub secundar

### 9.1 De ce Drive a devenit primar

Ambele instanțe — Mavis Local și Mavis Cloud — au acces la același
Google Drive. GitHub rămâne **secundar** pentru că rămâne dependent de
push/rebase și de divergența dintre arbori.

| | Canal primar: **Drive** | Canal secundar: **GitHub** |
|---|---|---|
| Cale | `BRIDGE-DRIVE/` în mirrorul `E:\Google\GDrive` | `QUEUE/TASKS-FOR-CLOUD.md` → repo `MAVIS-CLOUD` |
| Transport | DriveFS (mirror) | `git push` |
| Latență măsurată | **≈ 80 min** | imediat, dar dependent de R0 |
| Blocaj | propagarea poate întârzia | divergența 12/5 (vezi `docs/STARE-MAVIS-OPTIMUS-CI-REMOTE.md`) |
| Protocol | `BRIDGE-DRIVE/README-BRIDGE-DRIVE.md` | `docs/PROTOCOL-DENUMIRE-LOCAL-CLOUD.md` |

### 9.2 Ambele canale se scriu la aceeași publicare

Nu „întâi primul, apoi secundarul dacă primul cade". O cădere de transport
nu trebuie să coste timp: la aceeași publicare se scrie **același `TASK_ID`**
în ambele canale.

### 9.3 „Publicat" înseamnă măsurat

`scripts/mavis-drive-bridge.ps1` nu declară nimic pe baza scrierii. Verifică
indicele Drive și raportează unul din:

| Cod | Semnificație |
|---|---|
| `SYNCED` | fișierul e în indicele Drive |
| `PENDING` | scris local, propagarea nu s-a produs încă |
| `NOT_UPLOADED` | scrierea locală nu s-a produs |
| `UNVERIFIED` | **nu e succes** — măsurătoarea nu a putut decide |

### 9.4 Transportul căzut nu blochează sistemul

Poarta cere ca **raportul să fie concordant cu măsurătoarea** — nu ca
transportul să fie UP. Când canalul primar e căzut, canalul activ trece pe
GitHub, iar sistemul continuă să funcționeze.

### 9.5 Rutele de API sunt rupte — sursa de adevăr e locală

| Rută | Stare măsurată |
|---|---|
| `gdrive-mcp` (MCP) | `invalid_grant` — token revocat |
| `verify-drive.js` (bun) | `files.list` **FAILED**, EXIT 2 |
| `gcloud` ADC (`authorized_user`) | token valid, dar Drive API **HTTP 403** (fără scope) |
| `metadata_sqlite_db` | **422 932 480 B**, lizibil read-only → **e sursa de adevăr** |
| `mirror_metadata_sqlite_db` | 2 278 027 264 B, **blocată** de DriveFS ( inclusiv cu `immutable=1`) |

Re-consentul tokenului e un act **ACCESS**: cere consimțământul lui Popy în
browser. Nu se ocolește unilateral.

### 9.6 Poarta punții

`scripts/mavis-drive-bridge-selfcheck.ps1` — **6 probe**, dintre care:
ASCII pur, parse, lipsa contaminării exit-code-ului, ținta e în Drive,
„NOT FOUND" (poate eșua), **concordanța raport-măsurătoare**, refuzul
publicării fără subiect, existența canalelor.

Rezultat măsurat: `BRIDGE_PROBLEMS=0 UNKNOWN=0`, **EXIT 0**.
