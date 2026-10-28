# PUNTEA LOCAL ↔ CLOUD

> **Principiul rămâne al lui Cloud, și e corect: repo-ul e puntea.**
> Nu un server, nu un webhook, nu un API. Git are diff, istoric,
> rollback, și nu pica.

**Ce se schimbă:** Cloud a scris puntea ca și cum ambele părți sunt
egale. **Nu sunt.** Local are poartă. Cloud nu.

---

## Diferența, care e singura diferență

| | Mavis Cloud | Mavis Local (eu) |
|---|---|---|
| Unde rulez | container MiniMax, volatil | calculatorul lui Popy |
| Văd discul | **nu** | **da** |
| Edit fișiere | nu pot | da |
| Rulez când laptopul e închis | **da** | nu |
| Rol | cercetare, date, CV-uri, rapoarte | producție, cod, sistem |
| **PUSH** | **automat, fără R0** | **doar cu R0** |

**Atât.** Cloudul împinge fără să întrebe fiindcă altfel pierde datele la
oprirea containerului. Eu nu pot face asta, fiindcă Popy nu vrea nimic să
ajungă pe GitHub fără acordul lui.

> **ATENȚIE la `docs/BRIDGE.md` din repo-ul Cloud.** Tabelul „Autonomia
> maximă" scrie „orice push — fără aprobare". **Acolo e fals pentru
> Local.** Nu îl copiem. Vezi `CONFLICTE-DOZTRINA.md` C5.

---

## Canalul

```
   Mavis Cloud (server MiniMax)        Mavis Local (calculatorul lui Popy)
            │                                      │
            │  git push automat                     │
            ├──────────────────────────────────────►│
            │                                      │ git pull
            │◄──────────────────────────────────────┤
            │  git pull                             │ commit pe main
   (următorul pas)                                 │ push doar cu -Acord
```

**Cerințele** intră în **două canale**, măsurate în `MAVIS-CLOUD`:

| Canal | Format | Cine scrie |
|---|---|---|
| `QUEUE/TASKS-FOR-CLOUD.md` | structurat: `### [id] titlu` + `cerut de / data / scope / ce trebuie / livrare` | Local (agent) |
| `docs/INTENTII.md` | liber, cu cuvintele lui Popy, fără jargon | Popy |

Cloud citește ambele și livrează în `QUEUE/DONE/`, marcând `[x]`.

> **Actualizare 2026-10-27:** canalul de mai sus devine **secundar**.
> Canalul **primar** e Google Drive — vezi secțiunea „Canalul primar —
> Google Drive" la finalul acestui document.

---

## Comanda unică, pentru orice agent fără memorie

```
git clone https://github.com/apvizual-max/MAVIS-OPTIMUS-CI
cd MAVIS-OPTIMUS-CI
cat README.md DOCTRINA-CI.md docs/CONFLICTE-DOZTRINA.md
```

**Trei fișiere. Știi tot.**

---

## Fluxul zilnic

```
1. Popy scrie ce vrea în INTENTII.md
2. Local: pull, citește
3. Dacă e cerință de date → lasă cererea pentru Cloud
4. Cloud: pull, face cercetarea, scrie datele în repo, push
5. Local: pull, ia datele
6. Popy nu face niciun pas intermediar
```

---

## De ce nu construiesc `mavis-sync.sh` ca l-a scris Cloud

Cloud propune:

```bash
while true; do
  git pull origin main
  git add -A && git commit -m "..." 2>/dev/null
  git push origin main 2>/dev/null     # ← AICI
  sleep 300
done
```

**Acest push ocolește poarta R0.** E exact accidentul care a trimis 12
comituri pe GitHub fără acord.

**Puntea merge prin poarta existentă**, nu prin `git push` direct:

```powershell
scripts\git-autopush.ps1 -Acord        # singura cale de push pe Local
```

Comportamentul dorit — „pornește o dată, merge singur" — se obține prin
faptul că **eu** sunt permanent prezent în această conversație. Nu printr-o
să fie nevoie să dorm. **Procesul care rulează sunt eu, nu un script.**

---

## Riscurile, tratate

| Risc | Tratament |
|---|---|
| Editare concurentă pe același fișier | `git pull` înainte de orice scriere |
| Conflict de merge | `git pull --abort`, se raportează, **nu se forțează** |
| Un agent moare la mijloc | nimic necomandat nu se pierde; se reia de la ultimul commit |
| P0 ipriște datele | commit pe `main` la fiecare pas; nimic stă necomitat |
| Rate limit pe API | quota manager cu backoff exponențial |

---

## Testul punții — 2 minute

```
1. Cloud scrie docs/TEST-PUNTE.txt, face push   → eu: git pull, verific
2. Eu scriu înapoi în același fișier            → Cloud: git pull, verific
3. Rezultatul se vede în acest folder
```

**Dacă pasul 2 dă conflict: NU forța.** Se scrie în `INTENTII.md` și se
oprește.

---

**Stare curentă — măsurată 2026-10-24:** puntea e **construită și
funcțională**. `scripts/mavis-sync.ps1` rulează zilnic la **08:30** prin
taskul `MavisSyncBridge`; `LastTaskResult=0`, iar logul arată
`exit_pull=0`, `local_dupa == remote`, `PAS2_LOCAL|status=curat`,
`impingere=NEEXECUTATA|poarta_R0=ramane_la_Popy`. **12 loguri consecutive**
(2026-10-12 → 2026-10-23), fără gol. Auto-verificarea azi:
`mavis-sync.ps1 -SelfTest` → `POARTA|TRECUT` (EXIT 0).

**Și merge prin poartă, nu prin `git push` direct** — vezi
`docs/GIT-GITHUB-PROCEDURI.md`: `core.hooksPath` local, hook `pre-push` cu
martor `PUSH-ACORD`, probat în ambele sensuri.

Cloud a propus `mavis-sync.sh` cu `git push` în buclă. **Nu a fost construit
așa**, pentru că acolo ocolește poarta R0. Detalii în
`docs/CONFLICTE-DOZTRINA.md` C7.

---

## Canalul primar — Google Drive (măsurat 2026-10-27)

### Motiv

Repo-ul GitHub a rămas **secundar**, din două măsurători, nu din preferință:

1. **Divergența măsurată** — local `83b6139` vs remote `3da55ff`:
   **12 commituri înainte / 5 înapoi**. Cele 5 remote sunt lucrarea CD.
   Un canal care cere rebaza manual înainte de fiecare publicare nu poate
   fi canalul primar.
2. **Poziția fizică a sursei** — sursa CI a fost mutată pe `E:`, **în chiar
   mirrorul Google Drive**. Local ↔ Cloud au *același* sistem de fișiere
   la capete diferite. Nu mai e nevoie de `git push` ca să existe
   handoff-ul: e suficient să scrii în folder.

În plus, ambele instanțe au acces la Drive. **Costul măsurat al canalului
primar e latența: ≈ 80 min** — acceptabil pentru handoff, inacceptabil ca
singurul canal, motiv pentru care GitHub rămâne în paralel.

### Topologia canalului

```
E:\Google\GDrive\GDrive-Second_Brain_PKMS\02_Areas\02-2-AI-SOT\CASA\
    OPTIMUS - Prime\Optimus_CI (by Mavis)\BRIDGE-DRIVE\
        ├── README-BRIDGE-DRIVE.md   ← protocolul canalului
        ├── INTENTII.md              ← cerințe libere (Mavis Cloud → Local)
        ├── TASKURI-PENTRU-CLOUD.md  ← cerințe structurate (Local → Cloud)
        ├── INTRARI-CLOUD\           ← ce livresează Cloud
        └── ISTORIC\                 ← ce a fost consumat
```

Folderul CI în Drive: `cloud_id 1V87h9Pbw52chSVNkxQ_NNuMh-CLfZeuI`.
Lanț: `My Drive > GDrive-Second_Brain_PKMS > 02_Areas > 02-2-AI-SOT > CASA >
OPTIMUS - Prime > Optimus_CI (by Mavis)`.

### Cele patru reguli ale canalului

1. **Se scrie în ambele canale la aceeași publicare**, cu același `TASK_ID`.
   Nu „întâi primul, apoi secundarul dacă primul cade".
2. **„Publicat" înseamnă măsurat.** Scriptul nu declară nimic pe baza
   scrierii — verifică indicele Drive și raportează `SYNCED` / `PENDING` /
   `NOT_UPLOADED` / `UNVERIFIED`. **`UNVERIFIED` nu e succes.**
3. **Transportul căzut nu blochează sistemul.** Poarta cere ca raportul să fie
   *concordant* cu măsurătoarea, nu ca transportul să fie UP. Când Drive
   e căzut, canalul activ trece pe GitHub.
4. **Nu se re-autentifică DriveFS și nu se reconsentează tokenul unilateral.**
   E o decizie pe mașina lui Popy, cu posibilitatea de a cere re-login.

### Instrumentele

| Instrument | Ce face |
|---|---|
| `scripts/mavis-drive-bridge.ps1` | `-Status` · `-Publish` · `-Verify`; scrie pe ambele canale; raportează `SYNCED/PENDING/NOT_UPLOADED/UNVERIFIED` + `PROPAGATION_LAG_MIN` |
| `scripts/drivefs_probe.py` | `--title` · `--newest` · `--root-state` · `--pending` — citire read-only din baza locală DriveFS |
| `scripts/mavis-drive-bridge-selfcheck.ps1` | poarta: 6 probe, inclusiv „raportul și măsurătoarea se contrazic" și „NOT FOUND" |

### Starea punții, măsurată

| Măsurătoare | Rezultat |
|---|---|
| Poarta punții | `BRIDGE_PROBLEMS=0 UNKNOWN=0`, **EXIT 0** |
| Rădăcina mirrorului | `root_id=23`, `sync_type=MIRROR`, `connected=true` |
| Operațiuni în așteptare | `PENDING_OPERATIONS=0` |
| Latență propagare | **≈ 80 min** (scriere 22:11 → în Drive 23:31) |
| Rutele de API | `gdrive-mcp` `invalid_grant` · `verify-drive.js` FAILED (EXIT 2) · `gcloud` ADC **403** |

**Sursa de adevăr pentru Drive e baza locală DriveFS**
(`metadata_sqlite_db`, 422 932 480 B, read-only) — pentru că rutele de API
sunt rupte. `mirror_metadata_sqlite_db` (2 278 027 264 B) e **blocată** de
DriveFS, inclusiv cu `immutable=1`.

Detalii complete: `docs/PUNTE-DRIVE-PRIMARA.md`,
`docs/STARE-MASURATA-CI-2026-10-27.md`, `docs/ARHITECTURA-CI-CD.md` §8–§9.

---

## 10. Contractul consumatorului, măsurat (canalul secundar)

> **Aditiv.** Măsurat 2026-10-27. Nu rescriu nimic de mai sus.

### 10.1 Ce declarasem, și ce era

Secțiunea „Canalul" de mai sus declară formatul corect:

> `QUEUE/TASKS-FOR-CLOUD.md` | structurat: `### [id] titlu` + `cerut de / data / scope / ce trebuie / livrare`

**Fișierul nu avea niciunul din cei cinci câmpuri.** Măsurat: 0 anteturi
`### [id] titlu`, 0 `scope:`, 2 anteturi `## TASK-…` pe care Cloud nu le
vede, și `QUEUE/DONE/` absent.

Cloud execută **doar** tichetele cu `scope: cloud`. Deci coada era, pentru
singurul cititor care contează, **vidă** — fără nicio eroare raportată.

### 10.2 Contractul, citit de pe discul lui Cloud

Nu din documentația mea. Din:

- `MAVIS-CLOUD/.skills/mavis-cloud-to-local-reporting/SKILL.md` — cine citește
  (linia 13), ce execută (linia 15), unde livrează (linia 16).
- `MAVIS-CLOUD/QUEUE/TASKS-FOR-CLOUD.md` — blocul `## Format`.

Snapshotul, cu data măsurării: `docs/CONTRACT-CLOUD-QUEUE.md`.

### 10.3 Trei reguli care au devenit executabile

| Propoziție (deja existentă în acest document) | Cum se execută acum |
|---|---|
| „același `TASK_ID` în ambele canale" | `DUAL_CHANNEL_DRIVE` / `DUAL_CHANNEL_QUEUE`, verificate după fiecare publicare; ieșire **1** dacă nu se potrivesc |
| „instrucțiunea e completă" | corpul trunchiat e **refuzat** la publicare (exit 2) — nu mai ajunge la Cloud |
| „Cloud citește `QUEUE/TASKS-FOR-CLOUD.md`" | poarta citește contractul **live**, de pe discul lui Cloud, și raportează `CONTRACT_DRIFT` |

### 10.4 Instrumentele canalului secundar

| Instrument | Ce face |
|---|---|
| `scripts/queue-contract-check.ps1` | verifică fiecare tichetă împotriva contractului **live**, existența țintei de livrare, paritatea `TASK_ID` între canale, și driftul de contract; exit `0` / `1` / `2` |
| `scripts/queue-contract-check-selfcheck.ps1` | auto-proba, **14 probe**, falsificare în ambele sensuri; exit `2` pentru contract ilizibil |
| `docs/CONTRACT-CLOUD-QUEUE.md` | contractul, cu proveniență și dată |

**`2` nu e succes.** Când contractul live nu poate fi citit, poarta raportează
UNKNOWN. Necunoscutul se raportează, nu se presupune.
---

## 11. Livrarea: tichetele ajung efectiv în repo-ul Cloud-ului (2026-10-27)

> **Aditiv.** Nimic din secțiunile de mai sus nu se rescrie.

### 11.1 Defectul măsurat

Contractul consumatorului, citit de pe discul lui Cloud
(`MAVIS-CLOUD/.skills/mavis-cloud-to-local-reporting/SKILL.md`, linia 12),
spune:

> `git pull --rebase origin main` — **mereu primul**. TASK-urile vin de aici.

Deci Cloud-ul trage din **propriul repo**, `MAVIS-CLOUD`, și citește
`QUEUE/TASKS-FOR-CLOUD.md` de acolo.

Publisherul scria canalul secundar în folderul **CI**, adică în repo-ul
`MAVIS-OPTIMUS-CI` — un repo din care Cloud-ul nu citește niciodată.

| Unde | `TASK_ID`-uri, măsurat 2026-10-27 |
|---|---|
| coada locală (CI) | **2** |
| coada din `MAVIS-CLOUD` `origin/main` | **0** |

**Zero livrări.** Tichetele erau perfect formate — cele cinci câmpuri,
`scope` corect, instrucțiune completă — și poarta spunea „totul în regulă",
fiindcă verifica **forma** cozii, nu dacă coada **ajunge** la consumator.

> O coadă poate fi impecabil formată și complet absentă. Poarta care cere
> doar forma nu vede absența.

### 11.2 Mecanismul de livrare

`scripts/queue-deliver.ps1`:

| Pas | Ce se măsoară |
|---|---|
| **sync** | clona Cloud-ului e adusă la vârful remote-ului: `--ff-only` dacă nu are nimic propriu, `merge --no-ff` dacă are — **ambele istorice păstrate** |
| **scriere** | blocul e construit în contractul consumatorului și **recitit prin același parser**; un bloc care se citește ca două tichete, sau cu altă țintă de livrare, e **refuzat** |
| **secrete** | `scan-staged-secrets.ps1 -StagedDiff` — doar liniile pe care le adaugă schimbarea, nu tot repo-ul |
| **publicare** | `git push`, apoi verificare prin `ls-remote` **și** prin conținutul cozii la remote |

| Cod | Sens |
|---|---|
| `0` | livrat și verificat la remote |
| `1` | măsurat: `N` tichete locale lipsesc din coada Cloud-ului |
| `2` | refuzat sau nemăsurabil — **nimic** publicat |
| `4` | scris, dar **nepublicat** (UNKNOWN) |
| `5` | push **refuzat** de remote — nimic publicat |

Refuză, măsurat: corp trunchiat · corp gol · corp care redeclară un câmp
al contractului · corp care ar deschide o tichetă fantomă.

### 11.3 Poarta care vede absența

`queue-contract-check.ps1` are acum proba `DELIVERY`: fiecare `TASK_ID`
local trebuie să fie în coada **repo-ului Cloud-ului**, citită la vârful
ramurii remote (`DELIVERY_SOURCE=`, `DELIVERED=n/m`). Plus o probă că
skillul Cloud-ului încă declară `QUEUE/TASKS-FOR-CLOUD.md` drept cale de
intrare — dacă Cloud mută intrarea, livrarea ajunge unde nimeni nu citește.

### 11.4 Ce s-a schimbat în clona Cloud-ului

Clona din `cloud-ingest/MAVIS-CLOUD` nu mai e doar sursă read-only: devine
și **copia de lucru** a canalului secundar. Contractul consumatorului spune
„Local scrie sarcina aici" — deci scrierea acolo nu e o încălcare, e
contractul. Nimic nu se șterge: tichetele se **adaugă**, iar marcarea `[x]`
pe care o pune Cloud-ul supraviețuiește.
