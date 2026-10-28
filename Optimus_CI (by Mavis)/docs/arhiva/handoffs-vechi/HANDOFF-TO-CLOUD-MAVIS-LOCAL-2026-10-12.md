# HANDOFF PENTRU COLEGUL CLOUD — Mavis Local — 2026-10-12

**De la:** Mavis Local · **Pentru:** Mavis Cloud
**Ce e asta:** ce am implementat eu din planul comun, ca să nu-l repeți și să-l poți relua
dacă eu nu mai sunt.

> **Conventția de nume rămâne în vigoare.** Eu sunt `MavisLocal-` / `MAVIS-LOCAL-`.
> Tu ești `MavisCloud-` / `MAVIS-CLOUD-`. **Nu suprascrie fișierele celuilalt.**
> Dacă vrei să corectezi ceva scris de mine, corectura e **un fișier nou cu numele tău**,
> nu o editare peste al meu.

---

## 1. Ce ai făcut tu vs ce am făcut eu

| Domeniu | Cloud | Local (eu) |
|---|---|---|
| Jules: audit + integrare PR #3 | ✅ tu | — |
| Cele 11 documente `MavisCloud-*.md` | ✅ tu | citite, **neîncărcate** |
| Greșeala „Creafac" oprită | ✅ tu | — |
| Decuplarea vaultului de tracking | — | ✅ eu |
| Rescrierea istoricului + `git gc` | — | ✅ eu |
| Manualul de cotor + protocol de navigare | — | ✅ eu |
| Puntea `mavis-sync.ps1` | — | ✅ eu (reparată) |
| 4 skill-uri operaționale | — | ✅ eu |
| NotebookLM upload | — | ⚠️ **deschisă, revine la Local** |

---

## 2. Ce poți relua imediat din partea mea

### 2.1 Puntea — gata, nu o mai atinge fără motiv

```
scripts/mavis-sync.ps1
```

**Legea, în trei rânduri, ca să nu fie nevoie de context:**
1. Cloud împinge direct. Local doar CITe.
2. Commitul local e automat.
3. Împungerea **nu există în fișier** — ca ABSENȚĂ verificabilă: funcția își citește
   propriul cod sursă și se oprește cu `exit 2` dacă găsește un verb interzis.

**Teste, măsurate acum:**

```
T1 gate self        → TRECUT, exit 0
T2 "git push"       → BLOCAT, exit 2
T3 "push --force"   → BLOCAT, exit 2
T4 text curat       → TRECUT, exit 0
Rulare reală        → EXIT=0, exit_pull=0, "Already up to date"
```

**Dacă rupi ceva, verifică întâi dacă ai scris diacritice în fișier.**
E deliberat **ASCII pur**: PowerShell 5.1 citește UTF-8 fără BOM ca latin-1 și rupe
linia, cu un parser error imposibil de diagnosticat din conținut.

**Control:** `Get-Content -Raw` → byte peste `0x7F` → trebuie să fie **0**.

### 2.2 Vault — starea, pentru reluare fără rescriere

| Ce | Unde | Stare |
|---|---|---|
| Repo de automatizare | `D:\Alex_Knowlege_Vault` (remote `pkms-vault-automation`) | HEAD `62b04df` = remote |
| Urmărite | 43 fișiere, 438,8 KB | doar motorul |
| `.git` | 0,30 MB | după `gc --prune=now` |
| Snapshot | `D:\_OPTIMUS-SNAPSHOT\2026-10-12\` | MATCH ×3 |
| Conținut brut pe disc | 52.949 fișiere, 59,82 GB | neatins |

**Regula, pentru orice agent:** conținutul brut rămâne pe disc. **Nu se împinge.**
Nu rula `git clean -fdx` și nu rula `git reset --hard` în acest repo — `.git` e **în
interiorul voltului**, deci un clean șterge conținutul lui. Incident dovedit 2026-10-12.

### 2.3 Cotorul — derivat, nu versionat

```
MANUAL DE NAVIGARE - cotor.md      protocolul în 3 trepte
INTEGRARE - Mavis CI.md            suprafața de integrare
build-index.ps1                    regenerează din arborele curent
```

**4.682** de `00_INDEX.md`. **Nu intră în istoric** — e derivat. Dacă cineva îl
versionează, următoarea schimbare de arbore îl strică.

Navigarea prin cotor înseamnă: deschizi un director → citești `00_INDEX.md` → alegi
subdirector. **Scanarea brută a celor ~52.000 de fișiere e interzisă.**

### 2.4 Skill-uri create

```
~/.minimax/agents/mavis/skills/
  mavis-jules-contract-skill
  mavis-git-vault-governance-skill
  mavis-live-review-governance-skill
  mavis-cloud-bridge-skill
```

Registrul lor e în master, commit `8de349e`.

---

## 3. Ce e DESCHIS și revine la Local

**NotebookLM — 11 fișiere.** Citite, disponibile, **neîncărcate**.
Încărcarea cere `notebooklm.google.com` cu sesiune autentificată.

**Stare corectă:** `MĂSURĂTURĂ INCOMPLETĂ`. **Nu** declar încărcat ce n-am încărcat.

Dacă vezi într-un document „încărcat în NotebookLM" și nu există notebook cu sursa
atașată, **tratază declarația ca falsă până la probă inversă.**

---

## 4. Două reguli pe care le-am plătit ca să le pot transmite

### 4.1 Ordinea porților la secrete

```
git add  →  SCANEAZĂ INDEXUL  →  git commit  →  git push
```

Un secret verificat **înainte de `add`** nu e o poartă, e o observație.

Întâlnisem asta: `git add` a băgat în index un token Telegram real și patru fișiere de
chei API. **Commitul era încă neîmpins** — singurul moment în care repararea e curată.

### 4.2 Scanarea după `commit` nu e o poartă

Două `--amend` consecutive au produs `HEAD` cu părintele chiar comitul vechi, care
conținea în continuare fișierul cu secret. **Verificat cu `merge-base --is-ancestor`,
ieșire 0 — era încă reachable și ar fi fost împins.**

**Repararea deterministă:** `write-tree` → `commit-tree` → `update-ref` → `reflog expire`.
**Verificarea nu e „am rulat amend".** E `rev-list --all` + căutarea căii în fiecare commit.

---

## 5. Trei limite ale lui `git add` la scară — măsurate, nu teoretizate

Pe un `add` de ~50.000 de fișiere într-un repo real:

1. **Repo-uri git imbricate dispar fără mesaj.** Git nu coboară într-un director care
   e el însuși repo. Măsurat: **3 repo-uri imbricate = 588 de fișiere absente**, fără
   avertisment.
2. **`MAX_PATH` 260 pe Windows.** `git add` moare cu „Filename too long".
   Măsurat: **155 căi peste limită**. Corecție: `git config core.longpaths true`, **per-repo**.
3. **GitHub respinge peste 100 MB.** Măsurat în vault: **106 fișiere = 48.961 MB**.

**Regula generală: înainte să scrii o regulă, măsoară ce se pierde.** Diferența dintre
„ignorat intenționat" și „pierdut fără știre" arată exact câte reguli lipsesc.

---

## 6. Ce NU ai voie să faci

1. **Nu suprascrie fișierele mele.** `MavisLocal-*` / `MAVIS-LOCAL-*` sunt ale mele.
2. **Nu reintrodu ce e în carantină.** `ZURLI` e închis definitiv, cu `MOTIV.txt`.
3. **Nu declara un număr pe care nu l-ai măsurat.** Dacă nu l-ai măsurat: `MĂSURĂTURĂ INCOMPLETĂ`.
4. **Nu folosi `git status` ca verificare.** E o absență de verificare, nu o verificare.
5. **Nu face jumătate de sarcină și nu o ascunde sub „rămâne pentru când ai timp".**

---

## 7. Comanda cu care începi

```bash
cd <repo-ul Cloud>
git pull --ff-only
```

Primești tot ce am scris, inclusiv `ENDNOTE-MAVIS-LOCAL-2026-10-12.md`.
Nu trebuie să faci nimic cu el. Poate să-l tai.

---

*2026-10-12 · Mavis Local · handoff pentru Mavis Cloud · cu tot ce n-am făcut scris explicit*