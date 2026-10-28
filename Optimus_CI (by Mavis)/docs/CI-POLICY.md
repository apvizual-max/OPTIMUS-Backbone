# CI POLICY — puntea, guvernanța Git, și verificarea

> Politica de integrare continuă a **CI**. **Nu se schimbă fără R0.**
>
> **Suprapunere rezolvată:** politica anterioară amesteca Live Review +
> Jules (care sunt **CD**) cu puntea și guvernanța Git (care sunt **CI**).
> Live Review și Jules au plecat în folderul CD, la
> `docs/POLITICA-LIVE-REVIEW-JULES.md` al acestuia. **Un document trăiește
> în folderul sistemului pe care îl guvernează.**

---

## 1. Puntea Local ↔ Cloud

### 1.1 Principiul

**Repo-ul e puntea.** Nu un server, nu un webhook, nu un API. Git are diff,
istoric, rollback, și nu pica.

### 1.2 Singura diferență între cele două părți

| | Mavis Cloud | Mavis Local |
|---|---|---|
| Unde rulez | container MiniMax, volatil | calculatorul lui Popy |
| Văd discul | **nu** | **da** |
| Rulez când laptopul e închis | **da** | nu |
| Rol | cercetare, date, CV-uri, rapoarte | producție, cod, sistem |
| **PUSH** | **automat, fără R0** | **doar cu R0** |

Atât. Cloudul împinge fără să întrebe fiindcă altfel pierde datele la
oprirea containerului. Local nu poate face asta, fiindcă Popy nu vrea nimic
să ajungă pe GitHub fără acordul lui.

### 1.3 Canalul

```
   Mavis Cloud (server MiniMax)        Mavis Local (calculatorul lui Popy)
            |                                      |
            |  git push automat                     |
            |-------------------------------------->|
            |                                      | git pull (MavisSyncBridge 07:30)
            |<--------------------------------------|
            |  git pull                             | commit pe main
   (următorul pas)                                 | push doar cu -Acord
```

**Cerințele** intră în `QUEUE/TASKS-FOR-CLOUD.md` — canalul unic către
Cloud. Cloud livrează în `QUEUE/DONE/` și marchează `[x]`.

### 1.4 Fluxul zilnic

```
1. Local scrie ce vrea în QUEUE/TASKS-FOR-CLOUD.md
2. Local: pull (MavisSyncBridge 07:30), citește
3. Dacă e cerință de date → lasă cererea pentru Cloud
4. Cloud: pull, face cercetarea, scrie datele în repo, push
5. Local: pull, ia datele
6. Popy nu face niciun pas intermediar
```

### 1.5 Starea — măsurată 2026-10-24

`MavisSyncBridge` rulat, `LastTaskResult=0`:
`exit_pull=0`, `local_dupa == remote`, `PAS2_LOCAL|status=curat`,
`impingere=NEEXECUTATA|poarta_R0=ramane_la_Popy`, ieșire 0.

**Puntea e vie și nu împinge.** Detalii: `docs/STARE-MASURATA-CI.md` §1.

### 1.6 Riscurile, tratate

| Risc | Tratament |
|---|---|
| Editare concurentă pe același fișier | `git pull` înainte de orice scriere |
| Conflict de merge | `git pull --abort`, se raportează, **nu se forțează** |
| Un agent moare la mijloc | nimic necomandat nu se pierde; se reia de la ultimul commit |
| Rate limit pe API | quota manager cu backoff exponențial |

---

## 2. Guvernanța Git

| | |
|---|---|
| **COMMIT** | automat, pe `main`, **fără R0** |
| **PUSH** | **singurul** cu R0 |
| **≥50 neîmpinse** | alertă la fiecare răspuns, până dă R0 |
| **Changes** | gol, permanent, peste tot |
| **Instanța Cloud** | singura care împinge fără R0 |

Mecanismul complet, cu măsurătorile: **`docs/GIT-GITHUB-PROCEDURI.md`**.

---

## 3. Workflow-ul de verificare — cele 7 verificări

Moștenit din MAVIS-CLOUD, extins pentru OPTIMUS:

1. **niciun secret în commit**
2. JSON-uri valide
3. sintaxă JavaScript
4. sintaxă Python
5. build-ul proiectului reușește
6. regulile de business (ex: șabloanele nu conțin nume de firmă)
7. **puntea e vie** (mesajul pentru celălalt agent)

Toate în `on: schedule` + `on: workflow_dispatch`. **Niciuna pe push.**

### Regula de ieșire

Dacă un repo nu poate fi măsurat, titlul devine **„MĂSURĂTURĂ
INCOMPLETĂ"** și ieșirea e `2`.

Un senzor mort care raportează sănătate e mai prost decât un senzor care
lipsește.

---

## 4. Ce a plecat în CD — și unde se găsește acum

| Subiect | Unde trăiește acum |
|---|---|
| Platforma Jules (10 scripturi) | folder CD → `JULES - Optimus CD\scripts\` |
| Politica Live Review | folder CD → `docs\POLITICA-LIVE-REVIEW-JULES.md` |
| Trigger-ul `jules.yml` / `verify.yml` | folder CD → `JULES - Optimus CD\workflows\` |
| Registrul repo-urilor pentru Jules | folder CD → `JULES - Optimus CD\config\repos.json` |
| Contextul canonic trimis lui Jules | folder CD → `JULES - Optimus CD\config\jules-context.md` |
| Triajul, adaptările, rapoartele | folder CD → `JULES - Optimus CD\docs\` |

**Regula rămâne:** `MAVIS-CLOUD` e sursă read-only pentru **conținutul
existent**. Instanța Cloud nu are rol în CD.

**A doua excepție declarată (27 oct):** Localul scrie **ticheta cozii
secundare** în `MAVIS-CLOUD` — contractul consumatorului spune explicit
„Local scrie sarcina aici" și cere citirea din **propriul repo** al Cloud-ului
(`docs/CONTRACT-CLOUD-QUEUE.md`). Scrierea e **aditivă**, în formatul de
contract, și trece prin poarta de livrare (`scripts/queue-deliver.ps1`), care
verifică prezența tichetei **la vârful remote-ului**.

---

## 5. Reguli care nu se negociază

- **Merge = push = R0.** Triajul produce verdict, nu merge.
- **Niciodată ștergere definitivă.** Arhivare prin mutare în `docs/arhiva/`.
- **Zero cifre nereproductibile.** Tot ce se raportează e măsurat acum.
- **Un verdict care acuză trebuie să dovedească imputabilitatea.**
- **Instrument lipsă ≠ test picat** → `NO_MEASUREMENT`.

---

## 6. Puntea Drive — canalul primar

> **Aditiv.** Nu rescrie §1. §1 descrie în continuare **canalul secundar**,
> care rămâne viu și măsurat. Asta adaugă canalul **primar**.

### 6.1 Principiul

**Canalul primar e un folder Google Drive.** Local scrie în el; DriveFS îl
sincronizează; Cloud-ul — care are acces la Drive — vede aceiași octeți.
Fără server, fără webhook, fără API în cale.

### 6.2 Unde

| | |
|---|---|
| Folder | `BRIDGE-DRIVE/` |
| Calea în Drive | `My Drive > GDrive-Second_Brain_PKMS > 02_Areas > 02-2-AI-SOT > CASA > OPTIMUS - Prime > Optimus_CI (by Mavis)` |
| `cloud_id` | `1V87h9Pbw52chSVNkxQ_NNuMh-CLfZeuI` |

### 6.3 Cele patru canale

| Canal | Scrie | Citește |
|---|---|---|
| `TASKURI-PENTRU-CLOUD.md` | Local | Cloud |
| `INTENTII.md` | Popy | Cloud |
| `INTRARI-CLOUD/` | Cloud | Local |
| `ISTORIC/` | Local (mutare) | — |

### 6.4 Politica

1. **Se scrie în ambele canale, la aceeași publicare.** Nu „dacă primul
   cade" — pentru că atunci pierzi timp exact când transportul e bolnav.
2. **Publicat = măsurat.** `SYNCED` / `PENDING` / `NOT_UPLOADED` /
   `UNVERIFIED`. **`UNVERIFIED` nu e succes.**
3. **Nu se suprascrie nimic.** Corecția = fișier nou.
4. **Nu se șterge nimic.** Mutare în `ISTORIC/`.
5. **Latency e măsurată, nu presupusă** — ≈ 80 min, măsurat 2026-10-27.
   Cerințele urgente merg pe canalul secundar.

### 6.5 Poarta

```powershell
powershell -NoProfile -File scripts\mavis-drive-bridge-selfcheck.ps1
```

Șase probe: static, ținta în Drive, NOT FOUND (proba poate eșua), **verificul
că raportul și măsurătoarea se contrazic**, refuzul unei publicări fără
subiect, și existența canalelor. Măsurat: `BRIDGE_PROBLEMS=0 UNKNOWN=0`,
EXIT 0.

Detalii: `docs/PUNTE-DRIVE-PRIMARA.md`.

---

## 7. Poarta de secrete la commit

**Măsurat 2026-10-27.** Repo-ul CI e **public**. Deci poarta de secrete
trebuie să fie în **hook**, nu într-un switch: o poartă în prohă sau
într-un flag pe care eu îl pot pasa nu e o poartă.

### Instrumentul

`scripts\scan-staged-secrets.ps1` — citește **index-ul**, nu arborele de
lucru. Rulează automat la **fiecare** commit, prin hook-ul `pre-commit` din
`E:\Google\GitData-Optimus-CI/repo\hooks`.

| Cod | Ce înseamnă |
|---|---|
| `0` | `BLOCKS=0` · `SCAN_OK` |
| `1` | cel puțin un `BLOCK` — commitul e **refuzat** |
| `2` | scanarea **nu a putut rula** — commitul e refuzat, dar verdictul e „eroare", nu „bloc" |

**O excepție nu e un bloc.** O poartă care *acuză* trebuie să dovedească
imputabilitatea: `2` înseamnă „nu am putut măsura", nu „ai un secret".

### Auto-proba

`scripts\scan-staged-secrets-selfcheck.ps1` — 7 probe, în ambele sensuri:
o cheie plantată e **blocată** · o cheie privată e **blocată** · un
placeholder **nu** e blocat · liniile goale **nu** aruncă excepție ·
scannerul **nu** se blochează pe propriul cod · indexul real al repo-ului
e curat.

Măsurat: `SECRET_PROBLEMS=0 UNKNOWN=0`, **EXIT 0**.

### Lanțul, falsificat

`state\probe-gate-chain.ps1` — repo de probă izolat, remote bare local,
**GitHub neatins**. Rezultat: `GATE_PROBLEMS=0`, **EXIT 0** — commit curat
permis · commit cu secret refuzat · secret **absent** din istoric · push
fără acord refuzat · push cu acord permis.

Detalii: `docs/GIT-GITHUB-PROCEDURI.md` §4.1–§4.2.

---

## 8. Plasa de siguranță a serverului

> **Aditiv.** Nu rescrie §7. Măsurat 2026-10-27.

`.github/workflows/ci-verify.yml` rulează pe serverul GitHub, peste conținutul
**deja împins**: scannerul de secrete + auto-proba.

| | Poarta locală (§7) | Workflow-ul de server |
|---|---|---|
| Când | înainte de commit | după push |
| Unde | calculatorul lui Popy | runner GitHub |
| Efect | **blochează** commitul | **raportează** — nu blochează |
| Acoperă | indexul local | conținutul **public** |

**De ce raportează, nu blochează:** acest repo e lucrat acum de alt AI. O
poartă care blochează push-ul altcuia ar acuza conținut pe care eu nu l-am
scris și nu l-am măsurat — exact defectul pe care §5 îl interzice.

**Falsificat în ambele sensuri**, într-o clonă curată: `SCANNED=50
BLOCKS=0 SCAN_OK` exit 0 → cheie plantată → `BLOCKS=1` exit 1 (workflow
roșu) → scosă → `SCAN_OK` exit 0.

**Starea reală:** workflow-ul `ci-verify.yml` **e pe remote** — a ajuns acolo
cu împungerea lui `65af38f` (26 oct), confirmat azi la `origin/main`
(`merge-base --is-ancestor` → exit 0, blob `6f0fd55`). Serverul rulează acum
pentru acest repo. **Corectat:** secțiunea spunea *„404 pe remote, între cele
17 commituri neîmpinse"* — era adevărată înainte de împungere, nu și acum.

**Nicio ramură nu e protejată** pe server (`required_status_checks` → 404
„Branch not protected"), măsurat 2026-10-27, pe ambele repo-uri publice.
**Consecința, spusă fără cosmetizare:** poarta din `pre-commit` e singura
verificare înainte de push. Dacă hook-ul e ocolit, nimic nu oprește
conținutul cu secrete să ajungă public.

Detalii: `docs/MAPARE-FOLDERE.md` §8 · `docs/WORKFLOWS.md` W8.
