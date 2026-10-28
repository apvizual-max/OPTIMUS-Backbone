---
name: mavis-local-to-cloud-reporting
description: Procedura standardizată prin care Mavis Local (Windows, Command Hub) agregă starea fizică a discului și a celor 4 repo-uri, emite tichete în QUEUE/, arhivează istoricul vechi prin mutare (niciodată ștergere) și redactează rapoarte datate pentru Cloud — totul sub Poarta R0. Rulează la sfârșit de sesiune, înainte de predare.
role: functional
bot: mavis-local-optimus-ci-bot
---

# mavis-local-to-cloud-reporting

**Instanță:** Mavis Local · **mediu:** Windows, CLI fizic, R0 gate
**Contrapartidă:** `mavis-cloud-to-local-reporting` (Cloud, Linux/container)

Command Hub cu mașină de testare. **Testarea fizică e aici, nu acolo** — de
aceea triajul PR-urilor Jules, verificarea acoperirii și decizia de merge
aparțin Local, nu Cloud.

---

## 1. Măsură înainte de a declara

Niciun număr nu se raportează din memorie sau din raportul anterior.

| Ce | Cum |
|---|---|
| Stare repo | `git rev-parse HEAD` vs `git ls-remote origin refs/heads/<ramura>` |
| Neîmpinse | `git rev-list --count origin/<ramura>..<ramura>` |
| Murdare | `git status --porcelain \| Measure-Object` |
| Teste | `node --test <fișier>`, citește `pass`/`fail` și **exit code-ul** |
| Acoperire | `npx --yes c8 --reporter=text` — **și verifică cifra raportată de altcineva** |
| Panou | rulare, **apoi** numărare prin **extracție**, nu counting |

### Două capcane măsurate

**Branch inexistent ≠ dezincronizare.** `git ls-remote origin main` pe un repo
pe `master` întoarce **vid cu exit 0**. Un verificator scris „matches sau nu"
citește asta ca eșec. **Interoghează ramura din `repos.json`, nu `main` oarbește.**

**Counting numără și legenda.** Dacă scrii „NESINCRON" în textul explicativ
al paginii, counting-ul îl numără ca stare reală. **Extrage rândurile de date.**

## 2. Gate-ul de decizie — ce este al meu, ce e al lui Popy

| Decizie | Cine decide |
|---|---|
| Test, checkout, audit, merge de PR verificat | **Local — acum** |
| Diagnostic tehnic, arhitectură, nume de fișiere | **Local — acum** |
| **Push spre remote** | **R0 explicit** |
| **Deploy / publicare în extern** | **R0 explicit, întotdeauna** |
| Interval de programare, politică de conflict | **Popy — decizie de operator** |

`COMMIT` e automat, pe `main`, fără întrebare. **PUSH e singurul lucru care
cere R0.** Nu confunda: un merge de PR pe GitHub e un push.

## 3. Triajul Jules — procedura fixă

```
gh pr list --state all --json number,state,title,additions,changedFiles
gh pr diff <n> --name-only
```

1. **Cifrele raportate de Jules se verifică, nu se acceptă.** Dacă Jules spune
   95,35% acoperire, rulează `c8` și compară. Abia la egalitate e merge.
2. **Duplicate**: aceleași `additions` + `changedFiles` + conținut identic =
   duplicat. **Păstrează unul**, închide celălalt **cu motiv scris**.
3. **PR gol** poate fi rezultatul corect al unei sarcini de audit. Nu e defect.
4. **Workflow-ul doar trimite taskul.** Agentul lucrează asincron. Nu
   concluziona dintr-o lipsă de artefact la 9 secunde — compară
   **timestamp-ul artefactului cu timestamp-ul declanșării**.

## 4. Arhivare prin mutare — regula inviolabilă

**Niciodată ștergere definitivă.** Tot ce e temporar și consumat se mută în
`docs/arhiva/handoffs-vechi/` cu `git mv`.

Verificarea că nu s-a pierdut nimic:
```
git status --porcelain | Group-Object { $_.Substring(0,2) }
# asteptat: R = <numar>.  D = 0.  Daca vezi D, ai sters ceva.
```

**Nu atingi:** doctrina, scripturile de punte, `TODO.json`,
`LOG-SISTEM.json`, `MANUAL DE NAVIGARE - cotor.md`, `SITE/date/`,
`ALEX-KIT/TEMPLATES-POPY/`.

## 5. Tichete spre Cloud — fișiere în coadă

**Coada trăiește în două canale, de la 2026-10-27.** Se scrie în **ambele**
la aceeași publicare, cu **același `TASK_ID`**.

| Canal | Locație | Rol |
|---|---|---|
| **primar** | `BRIDGE-DRIVE/TASKURI-PENTRU-CLOUD.md` (în folderul CI, pe `E:`) | Google Drive — ambele instanțe au acces |
| **secundar** | `QUEUE/TASKS-FOR-CLOUD.md` în `MAVIS-CLOUD`, pe `main` | GitHub |

```
### [TASK-NNN] titlu
cerut de: local | data: YYYY-MM-DD
scope: cloud
ce trebuie: ...
livrare: QUEUE/DONE/TASK-NNN.md
```

Cloud citește la pull, procesează, livrează în `QUEUE/DONE/`, bifează `[x]`.
**Nu rulează sarcini cu `scope: local`** — acelea cer o mașină fizică.

**`TASK_ID` e cheia de urmărire**, nu o convenție de nume: același
identificator apare în ambele canale, ca tichetul să fie recunoscut ca
același lucru. Convenția de denumire a documentelor
(`MAVIS-LOCAL-…` / `MAVIS-CLOUD-…`) se aplică identic în ambele canale.

### 5.1 Contractul cozii se citește de la sursa vie

**Adiționat 2026-10-27, ~02:40.** Secțiunile de mai sus rămân valabile.

Blocul de format de mai sus **nu l-am inventat**: e contractul consumatorului,
citit de pe discul Cloud-ului —
`MAVIS-CLOUD/.skills/mavis-cloud-to-local-reporting/SKILL.md` (liniile 13–16)
și blocul `## Format` din `MAVIS-CLOUD/QUEUE/TASKS-FOR-CLOUD.md`. Poarta
`scripts\queue-contract-check.ps1` îl citește **live**, la fiecare rulare, și
raportează `CONTRACT_DRIFT` dacă Cloud îl schimbă.

**Ruta, măsurată:** Cloud citește `MAVIS-CLOUD/QUEUE/TASKS-FOR-CLOUD.md` — **din
repo-ul lui**. Coada scrisă de CI trăiește în repo-ul CI
(`Optimus_CI (by Mavis)\QUEUE\TASKS-FOR-CLOUD.md`), în **format de contract**,
și de acolo este **livrată** în repo-ul Cloud.

**Cum ajunge ea la Cloud — REZOLVAT PE FACTE, 2026-10-27:** **commit în
`MAVIS-CLOUD`**, prin `scripts\queue-deliver.ps1`. Măsurat: **2 tichete locale →
2 tichete în coada lui Cloud**, la vârful ramurii remote (commit `4a88879`,
`REMOTE_HEAD` = `LOCAL_HEAD`, verificat prin `ls-remote`).

**Măsurat înainte de reparare:** 0 din 5 câmpuri, 0 `scope:`, 2 anteturi
invizibile pentru Cloud, `QUEUE/DONE/` absent. Coada arăta plină și era
**goală** pentru singurul cititor care contează.

**Reguli, acum executabile:**

1. Copia secundară se scrie **în contractul consumatorului**.
2. Corpul **trunchiat** e **refuzat** la publicare (exit 2).
3. `scope` necunoscut → **refuzat** (exit 2).
4. După scriere: `DUAL_CHANNEL_DRIVE` / `DUAL_CHANNEL_QUEUE` — ieșire **1** dacă
   același `TASK_ID` nu e în ambele canale.
5. Cod **2** de la poartă = contract live ilizibil = **UNKNOWN, nu succes**.

## 6. Raportul de stare — forma fixă

`docs/STATUS-LOCAL-TO-CLOUD-YYYY-MM-DD.md`, obligatoriu cu:

1. tabelul celor **4 repo-uri** cu branch, HEAD, MATCH, murdare
2. deciziile luate, **fiecare cu motivul și cifra care l-a justificat**
3. starea infrastructurii (panou, coadă, arhivă)
4. **capabilitatea de programare, măsurată** — cu ce exista, cu ce nu
5. ce ceri de la Popy, separat de ce ai decis singur

## 7. Înainte de push

1. `git add` **apoi** scan de secrete pe index
2. commit pe `main`, mesaj care conține **cifrele**, nu adjectives
3. `git push` — doar cu R0
4. **`git ls-remote`** și compară hash-ul. **Niciodată după exit code.**
5. **Canalul Drive**: `scripts\mavis-drive-bridge.ps1 -Publish` — scrie în
   ambele canale, apoi raportează `SYNCED` / `PENDING` / `NOT_UPLOADED` /
   `UNVERIFIED`. **`UNVERIFIED` nu e succes.**
6. **Nu declara „publicat" pe baza scrierii.** Verificarea e măsurătoarea
   indicelui Drive (`python scripts\drivefs_probe.py --title "Optimus_CI (by Mavis)"`),
   nu efectul scrierii pe disc. Latența măsurată e **≈ 80 min**.
7. **Coada se verifică înainte de a o da.** `scripts\queue-contract-check.ps1` —
   contractul consumatorului, citit **live** de pe discul Cloud; fiecare
   tichetă, ținta de livrare, paritatea `TASK_ID` între canale. Ieșire `0` /
   `1` / `2`, iar **`2` = contract ilizibil = UNKNOWN, nu succes**.
   Auto-proba: `scripts\queue-contract-check-selfcheck.ps1` (11 probe).

## 8. Când ești Command Hub

- **Măsură artefactul, nu raportul despre el.** Un raport încrucișat între
  agenți e o afirmație, nu o măsurătoare.
- **Compară data artefactului cu data declanșării**, nu „există / nu există".
- **Timpul la care sistemul spune că a terminat ≠ timpul la care termină.**
- Dacă o cifră vine de la altcineva și nu o poți reproduce: spune
  `MĂSURĂTURĂ INCOMPLETĂ`. Nu completa cu presupunere.

## Referințe

- Script punte: `MAVIS-OPTIMUS-CI\scripts\mavis-sync.ps1`
- Panou: `MAVIS-CLOUD\SITE\build-hub.py` (+ `build-dashboard-legacy.py`)
- Coada: `MAVIS-CLOUD\QUEUE\TASKS-FOR-CLOUD.md`
- Config repo-uri: `MAVIS-CLOUD\SITE\date\repos.json`
- Arhivă: `MAVIS-OPTIMUS-CI\docs\arhiva\handoffs-vechi\`
- Rulare la final de sesiune. **Nu se rulează la început** — la început se
  citește, ca să nu se declare nimic înainte de măsurat.

- Punte Drive: `Optimus_CI (by Mavis)\scripts\mavis-drive-bridge.ps1`
- Poarta punții: `Optimus_CI (by Mavis)\scripts\mavis-drive-bridge-selfcheck.ps1`
- Sonda DriveFS: `Optimus_CI (by Mavis)\scripts\drivefs_probe.py`
- Coada primară: `Optimus_CI (by Mavis)\BRIDGE-DRIVE\TASKURI-PENTRU-CLOUD.md`
---

## Livrarea cozii — rezolvată, măsurată (2026-10-27, ~06:40)

> **Aditiv.** Nimic de mai sus se rescrie; §5 e **corectat pe loc**, pentru că
> întrebarea „cum ajunge coada la Cloud" avea deja un răspuns măsurat.

**Ruta, măsurată:** Cloud citește `MAVIS-CLOUD/QUEUE/TASKS-FOR-CLOUD.md` — **din
repo-ul lui**. Coada scrisă de CI trăiește în repo-ul CI
(`Optimus_CI (by Mavis)\QUEUE\TASKS-FOR-CLOUD.md`), în **format de contract**,
și de acolo este **livrată** în repo-ul Cloud.

| Măsurat, înainte | Valoare |
|---|---|
| `TASK_ID`-uri în coada locală (CI) | **2** |
| `TASK_ID`-uri în coada pe care Cloud-ul o citește | **0** |
| Poarta contractului | `QUEUE_PROBLEMS=0` — **verde, greșit** |

| Măsurat, după | Valoare |
|---|---|
| Tichete în coada lui Cloud, la `origin/main` | **2** |
| Commit în `MAVIS-CLOUD` | `4a88879` |
| `REMOTE_HEAD` = `LOCAL_HEAD` | `4a88879` (verificat prin `ls-remote`) |

### Instrumentele livrării

```powershell
scripts\queue-deliver.ps1 -Status          # ce nu a ajuns (read-only)
scripts\queue-deliver.ps1 -Deliver -Push   # livrează și verifică la remote
scripts\queue-deliver-selfcheck.ps1        # 15 probe, falsificare în ambele sensuri
```

Poarta contractului are acum proba `DELIVERY`: fiecare `TASK_ID` local trebuie
să fie în coada **repo-ului Cloud-ului**, citită la vârful ramurii remote. Fără
ea, poarta raporta sănătate pentru o coadă pe care nimeni nu o citește.

**Regula, pentru totdeauna:**

> **O coadă impecabil formată poate fi complet absentă.**
> „Publicat" = prezent la vârful ramurii remote a repo-ului consumatorului.
