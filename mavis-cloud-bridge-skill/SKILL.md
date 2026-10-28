---
name: mavis-cloud-bridge-skill
description: "Protocolul Local <-> Cloud: cum circula informatia intre Mavis Cloud si Mavis Local si unde se opreste fiecare. Micro-skill al suitei mavis-optimus-continuous-integration-skill. Incarca-l la orice lucru despre puntea Google Drive, coada QUEUE sau schimbul de fisiere intre instanta locala si cea cloud."
role: functional
bot: mavis-local-optimus-ci-bot
---

# MAVIS — CLOUD BRIDGE (protocolul Local ↔ Cloud)

**Tip:** micro-skill în cadrul suitei `mavis-optimus-continuous-integration-skill`
**Scop:** cum circulă informația între Mavis Cloud și Mavis Local, și unde se
oprește fiecare.
**Stare:** ✅ WIRED — puntea e **construită și măsurată** (2026-10-27). `scripts\mavis-sync.ps1` rulează zilnic la **08:30** prin taskul `MavisSyncBridge`; `LastTaskResult=0`, iar logul arată `exit_pull=0`, `local_dupa == remote`, `impingere=NEEXECUTATA|poarta_R0=ramane_la_Popy`. **12 loguri consecutive** (2026-10-12 → 2026-10-23), fără gol. Auto-verificarea: `mavis-sync.ps1 -SelfTest` → `POARTA|TRECUT` (EXIT 0).
**Canal primar nou (2026-10-27):** Google Drive — vezi secțiunea „Puntea primară prin Google Drive". `mavis-sync.sh` nu a fost construit nici acum: **se construiește doar forma care respectă asimetria** (citire automată, commit automat, push prin poartă).

## 1. Legea asimetrică — singura diferență între cele două instanțe

| | Mavis Cloud | Mavis Local |
|---|---|---|
| mediu | container volatil, online 24/7 | mașina lui Popy, D:/E:/C: |
| push pe GitHub | **direct, fără R0** | **doar cu R0 explicit** |
| ramură | `main` | `main` |
| commit | automat | automat |
| fișiere personale | nu le are | le are |
| browser / deploy | nu | da |

Restul procesului e identic. **Nu** mai mult. Orice „extindere" a diferenței
trebuie demonstrată cu un caz, nu cu o plauzibilitate.

> „Cloud-ul împinge DIRECT pe GitHub (fără R0), pentru că rulează asincron în
> container volatil." — Popy, 2026-10-12.

## 2. Ce a construit Cloud, măsurat

Handoff-ul `docs/HANDOFF-2026-10-12-0440-jules.md` (04:40) raportează:

- **34 commituri · 0 necomitate · 0 nepushuite**
- **172 documente .md** · 19 skill-uri proprii + 16 vendor · 11 Priming KIT
- 36 scripturi în `mavis-tools`
- workflow-uri: `jules.yml`, `verify.yml`
- repo `apvizual-max/MAVIS-CLOUD` · **privat** · ultima push 01:21 UTC

> **CORECTARE măsurată 2026-10-27:** repo-ul `apvizual-max/MAVIS-CLOUD` este
> acum **PUBLIC** (`gh repo view apvizual-max/MAVIS-CLOUD --json visibility` →
> `PUBLIC`). La fel și `apvizual-max/MAVIS-OPTIMUS-CI` → `PUBLIC`.
> Cele de mai sus sunt ce raporta handoff-ul din 10-12; vizibilitatea s-a
> schimbat de atunci.
>
> **De ce contează:** un repo PUBLIC nu e loc pentru date personale sau
> secrete. Două scurgeri au fost închise pe 27 octombrie, ambele prin
> `.gitignore`, măsurate înainte de commit:
> - `Mavis_Cloud_Artefacts_arhive-*/` — ar fi intrat cu **104** căi, cu
>   `client_secret`, `refresh_token`, `access_token` și parole;
> - `/sessions/` — **49** fișiere, **39.668.437 B**, cu transcripturi de
>   sesiune și tokenuri de autorizare.
>
> Regula: într-un repo PUBLIC, **orice folder neignorat e o scurgere în
> așteptare**. `git add -A --dry-run` e instrumentul care măsoară asta.
> Măsurat: `scripts\mavis-sync.ps1:189` rulează `git add -A` automat.

## 3. Regula „nu fac jumătate de sarcină"

Citată din același handoff:

> „Un handoff nu e «restul îl face Local». Un handoff e o sarcină completă, cu
> toate datele, toate fișierele, toate deciziile deja luate. Local primește
> munca gata de rulat, nu o problemă de rezolvat."

Convenția de numire, care face ordine în timp:
`docs/HANDOFF-YYYY-MM-DD-HHMM-<subiect>.md`. **Niciodată suprascris.**

## 4. Citirea de pe partea Local — read-only prin clonă

```powershell
git -C cloud-ingest\MAVIS-CLOUD pull --ff-only
```

- `cloud-ingest\` e **ignorit** de `.gitignore`-ul lui `MAVIS-OPTIMUS-CI`: nu
  dublăm date personale și nu îngropăm un repo în alt repo.
- Se accesează **prin cale documentată**, nu prin copiere.
- **Nu se modifică nimic în `MAVIS-CLOUD`.** Se citește, se citește istoricul,
  se copiază *ideea*.
  > **Corectură de drift, 2026-10-27, ~06:40:** regula de mai sus a fost
  > **schimbată de fapt**, nu de dorință. Contractul consumatorului spune
  > „Local scrie sarcina aici" — deci scrierea cozii **în `MAVIS-CLOUD`** e
  > contractul, nu o încălcare. Clona a devenit și **copia de lucru** a
  > canalului secundar: `scripts\queue-deliver.ps1` scrie, comitează și
  > publică acolo, **aditiv** — nimic nu se rescrie, iar marcarea `[x]` pe
  > care o pune Cloud-ul supraviețuiește. Măsurat: commit `4a88879` în
  > `MAVIS-CLOUD`, `REMOTE_HEAD` = `LOCAL_HEAD`.

Măsurat 2026-10-12: `eb323a2` → `006c3d1` prin `pull --ff-only`.

## 5. De ce puntea automată NU e construită — și de ce nu se construiește orbește

> **Actualizare 2026-10-27:** titlul se referă la **`mavis-sync.sh`**, bucla
> `while true … git push` — care **nici acum nu se construiește**, pentru că
> ocolește poarta R0. Puntea în sine **e construită și măsurată**: vezi
> `Stare` în capul acestui skill și secțiunea „Puntea primară prin Google
> Drive" de mai jos. Ce rămâne neconstruit e **doar** bucla de push direct.

`docs/BRIDGE.md` din Cloud specifică `mavis-sync.sh` cu o buclă
`while true … git push`. Pe main-ul local, **o asemenea buclă ar ocoli poarta
R0** — ar împinge fără R0, contra legii.

Deci: se construiește **doar** în forma care respectă asimetria:
- citire (`fetch` / `pull`) — automat, fără R0;
- commit local — automat;
- **push — poartă, nu buclă.**

O punte care ar depăși singurul punct unde se cere acordul omului nu e o punte,
e o scurtătură.

## 6. Ce rămâne pentru Local, din handoff, complet și netăiat

Cloud a enumerat trei sarcini, declarate complete:

| | sarcină | ce nu e necesar să-l întreb |
|---|---|---|
| 5.1 | verifică setup-ul local, construiește puntea după `BRIDGE.md` | datele sunt în repo |
| 5.2 | rebuild site-uri cu datele verificate | datele sunt enumerate în handoff |
| 5.3 | **nu folosi `ALEX-KIT/SABLOANE/`** pentru CV-uri finale | `ALEX-KIT/TEMPLATES-POPY/` e sursa lui Popy |

Punctul 5.3 e o **corectură de sursă**: Cloud a construit 9 șabloane din memorie,
Popy avea deja ale lui, cu `{Company_Name_Here}` și `{Nume_Companie_Aici}`. Sursa
lui Popy e în `ALEX-KIT/TEMPLATES-POPY/`.

## 7. Surse

- `cloud-ingest\MAVIS-CLOUD\docs\HANDOFF-2026-10-12-0440-jules.md` — cel mai nou
- `cloud-ingest\MAVIS-CLOUD\docs\BRIDGE.md` — specificația punții (**neconstruită**)
- `docs/CONFLICTE-DOZTRINA.md` în `MAVIS-OPTIMUS-CI` — cele 7 conflicte, cu citate

---

## Puntea primară prin Google Drive

**Adiționat 2026-10-27.** Secțiunile 1–7 rămân valabile; aici se spune
**de ce a apărut un al doilea canal** și cum se raportează la asimetria de
la §1.

### Asimetria nu se schimbă

| | Mavis Cloud | Mavis Local |
|---|---|---|
| PUSH pe GitHub | **direct, fără R0** | **doar cu R0 explicit** |

Canalul Drive **nu e o scurtătură în jurul poartei R0**: scrierea în
folderul Drive nu e un push pe GitHub. E un transport distinct, cu
propria lui măsurătoare.

### De ce a apărut

1. **Divergența măsurată** în repo-ul CI: local `83b6139` vs remote
   `3da55ff` → **12 înainte / 5 înapoi**. Cele 5 remote sunt lucrarea CD.
2. **Sursa CI a fost mutată în chiar mirrorul Google Drive**
   (`E:\Google\GDrive\GDrive-Second_Brain_PKMS\...\Optimus_CI (by Mavis)`).
   Local și Cloud au *același* sistem de fișiere la capete diferite.

Costul canalului primar e **latența ≈ 80 min** (scriere locală 22:11 →
prezență în Drive 23:31). GitHub rămâne **secundar**, nu eliminat.

### Cele patru reguli

1. **Se scrie în ambele canale la aceeași publicare**, cu același `TASK_ID`.
2. **„Publicat" înseamnă măsurat**: `SYNCED` / `PENDING` / `NOT_UPLOADED` /
   `UNVERIFIED`. **`UNVERIFIED` nu e succes.**
3. **Transportul căzut nu blochează sistemul** — poarta cere ca raportul să
   fie *concordant* cu măsurătoarea, nu ca transportul să fie UP.
4. **Nu se re-autentifică DriveFS și nu se reconsentează tokenul unilateral.**

### Starea măsurată a transportului

| Rută | Stare |
|---|---|
| `gdrive-mcp` (MCP) | `invalid_grant` — token revocat |
| `verify-drive.js` | `files.list` **FAILED**, EXIT 2 |
| `gcloud` ADC (`authorized_user`) | token valid, Drive API **HTTP 403** (fără scope) |
| `metadata_sqlite_db` | 422 932 480 B, read-only → **sursa de adevăr** |
| `mirror_metadata_sqlite_db` | 2 278 027 264 B, **blocată** de DriveFS |

**Re-consentul tokenului e act ACCESS** — cere consimțământul lui Popy în
browser. Nu se ocolește unilateral.

### Instrumentele

```powershell
scripts\mavis-drive-bridge.ps1 -Status
scripts\mavis-drive-bridge.ps1 -Publish
scripts\mavis-drive-bridge.ps1 -Verify
scripts\mavis-drive-bridge-selfcheck.ps1    # poarta, 19 probe
```

Poarta măsurată: `BRIDGE_PROBLEMS=0 UNKNOWN=0`, **EXIT 0**.

---

## Canalul secundar are un contract, și contractul se citește viu

**Adiționat 2026-10-27, ~02:40.** Secțiunile de mai sus rămân valabile.

### Defectul măsurat

`QUEUE/TASKS-FOR-CLOUD.md` avea două tichete citibile cu ochiul și era
**inexecutabilă** de Cloud. Contractul consumatorului a fost citit **de pe
discul Cloud-ului** — `MAVIS-CLOUD/.skills/mavis-cloud-to-local-reporting/SKILL.md`
(liniile 13–16: citește coada, rulează **doar** tichetele cu `scope: cloud`,
scrie în `QUEUE/DONE/<id>.md`, marchează `[x]`) și blocul `## Format` din
`MAVIS-CLOUD/QUEUE/TASKS-FOR-CLOUD.md`:

```
### [id] titlu
cerut de: local | data: YYYY-MM-DD
scope: cloud | local | ambele
ce trebuie: ...
livrare: unde trebuie să ajungă rezultatul
```

| Măsurat în coada CI | Valoare |
|---|---|
| Câmpuri de contract | **0 din 5** |
| Anteturi `### [id] titlu` | **0** |
| Tichete cu `scope:` | **0** |
| `QUEUE/DONE/` (ținta de livrare) | **absent** |

Cloud rulează **doar** tichetele cu `scope: cloud`. Deci coada era, pentru
singurul cititor care contează, **goală** — fără nicio eroare raportată.

Mai mult: trunchierea era în **ambele** canale, și `state/drive-bridge-last-publish.json`
dovedește că **publisherul** o scris (corpul trunchiat i-a ajuns ca atare, la
`01:03:30`) și a raportat publicarea ca succes. Deci defectul trăia în
**generator**, nu în fișier — repararea fișierului, singură, ar fi fost
refăcută de următoarea publicare.

### Ce e acum executabil

| Propoziție | Formă executabilă |
|---|---|
| „același `TASK_ID` în ambele canale" | `DUAL_CHANNEL_DRIVE` / `DUAL_CHANNEL_QUEUE`, verificate după fiecare publicare; ieșire **1** dacă nu se potrivesc |
| „instrucțiunea e completă" | corpul trunchiat e **refuzat** la publicare (exit 2) |
| „coada e în contractul Cloud-ului" | `scripts\queue-contract-check.ps1` citește contractul **live** de pe discul Cloud și raportează `CONTRACT_DRIFT` |
| „ținta de livrare există" | `QUEUE/DONE/` trebuie să existe, sau poarta blochează |

```powershell
scripts\queue-contract-check.ps1              # poarta, exit 0 / 1 / 2
scripts\queue-contract-check-selfcheck.ps1    # 14 probe, falsificare în ambele sensuri
```

Măsurat: `QUEUE_PROBLEMS=0 UNKNOWN=0` · `TICKETS=2` · `CONTRACT_DRIFT=NO` ·
`UNRECOGNISED_HEADERS=0` · `DONE_DIR=present` · **EXIT 0**. Auto-proba:
`QUEUE_GATE_PROBLEMS=0 UNKNOWN=0 FALSIFIED=14`.

**`2` nu e succes.** Contractul live ilizibil → UNKNOWN → exit 2. Necunoscutul
se raportează, nu se presupune.

### Regula, pentru totdeauna

> **O coadă plină poate fi goală pentru singurul cititor care contează.**
>
> Și: **o instrucțiune trunchiată e o instrucțiune, nu o sarcină** — un
> publisher care o acceptă și raportează succes minte, iar minciuna ajunge
> la celălalt capăt al punții.

Și, pentru orice schimbare ulterioară a formatului: **contractul se citește de
la sursa vie**, nu dintr-o copie. O copie se învechise în tăcere, iar o poartă
care compară cu o copie nu detectează nimic.

### Când istoricul se diverge

> **Aditiv.** Măsurat 2026-10-27.

Dacă `origin/main` a avansat (alt AI lucrează în paralel în același repo),
combinarea **nu** se face la guess:

```
scripts\merge-check.ps1
```

Dry-run: divergență, conflicte pe fișier, arbore rezultat. Exit `0` curat ·
`1` conflict (fișierele sunt **numite**) · `2` nemăsurabil — și `2` **nu** e
„curat". Măsurat: `REMOTE_STATE=LIVE` · `MERGE_CLEAN=yes` · `CONFLICT_FILES=0`.

Auto-proba: `scripts\merge-check-selfcheck.ps1` — 5 probe pe repo reale →
`MERGE_GATE_PROBLEMS=0 UNKNOWN=0 FALSIFIED=5`. Falsificare: poarta stricată
pe **copie** → `MERGE_GATE_PROBLEMS=3`, `POARTA A BLOCAT`, exit 1; poarta
reală neatinsă.

**Regula:** înainte de orice operație cu R0, există un instrument care spune
**ce se va întâmpla**. Iar blocarea se dovedește prin **marcaj**, nu prin cod
de ieșire — un exit 1 dintr-o excepție terminantă e indistinctibil de cel al
porții.
---

## Livrarea efectivă în repo-ul Cloud-ului (2026-10-27, ~06:40)

> **Aditiv.** Secțiunile 1–7 rămân valabile. **§4 e corectată pe loc**, mai jos,
> pentru că regula de acolo a fost schimbată **de fapt**, nu de dorință.

### Contractul consumatorului, citit viu

`MAVIS-CLOUD/.skills/mavis-cloud-to-local-reporting/SKILL.md`, linia 12:

> `git pull --rebase origin main` — **mereu primul**. TASK-urile vin de aici.

Deci **unde stă coada** e hotărât de consumator: în **repo-ul lui Cloud**,
`MAVIS-CLOUD/QUEUE/TASKS-FOR-CLOUD.md`. Coada din repo-ul CI e
**înregistrarea locală** și sursa din care se livrează — nu canalul.

| Măsurat, înainte | Valoare |
|---|---|
| `TASK_ID`-uri în coada locală (CI) | **2** |
| `TASK_ID`-uri în coada pe care Cloud-ul o citește | **0** |
| Poarta contractului | `QUEUE_PROBLEMS=0` — **verde, greșit** |

Poarta verifica **forma** cozii, nu dacă coada **ajunge** la consumator.

### Mecanismul

`scripts\queue-deliver.ps1`:

| Pas | Ce se măsoară |
|---|---|
| sync | clona Cloud-ului e adusă la vârful remote-ului: `--ff-only` dacă nu are nimic propriu, `merge --no-ff` dacă are — **ambele istorice păstrate** |
| scriere | blocul e construit în contractul consumatorului și **recitit prin același parser**; un bloc citit ca două tichete, sau cu altă țintă de livrare, e **refuzat** |
| secrete | `scan-staged-secrets.ps1 -StagedDiff` — doar liniile pe care le adaugă schimbarea |
| publicare | `git push`, apoi verificare prin `ls-remote` **și** prin conținutul cozii la remote |

Refuză, măsurat: corp trunchiat · corp gol · câmp redeclarat · tichetă fantomă.

```powershell
scripts\queue-deliver.ps1 -Status          # ce nu a ajuns (read-only)
scripts\queue-deliver.ps1 -Deliver -Push   # livrează și verifică la remote
```

Auto-proba: `scripts\queue-deliver-selfcheck.ps1` — **15 probe** pe un bare repo
local (git real, push real, citire la remote) → `DELIVER_GATE_PROBLEMS=0
FALSIFIED=15`.

### Măsurat, după

| | |
|---|---|
| Commit în `MAVIS-CLOUD` | `4a88879` |
| `REMOTE_HEAD` = `LOCAL_HEAD` | `4a88879` |
| Tichete la remote | **2**, citite din `origin/main` |

### Regula, pentru totdeauna

> **O coadă impecabil formată poate fi complet absentă.**
>
> Pentru un consumator care trage dintr-un repo, „publicat" înseamnă „prezent
> la vârful ramurii remote a repo-ului lui" — nu „scris local". Poarta trebuie
> să citească **acolo**.
