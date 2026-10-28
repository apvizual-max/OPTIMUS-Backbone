# BLUEPRINT — Mavis Optimus Continuous Integration

> Plan de execuție. **Nu o listă — un document de inginerie.**
> Fiecare fază are: ce, unde, verificare, anulare.

**Data:** 2026-10-12 · **Autor:** Mavis · **Instanță:** LOCAL (R0 la push)
**Stare:** fazele 0–2 încheiate și verificate. Restul neexecutate.

---

## 0. Scopul și raza

**În rază:** Git și GitHub ca sistem, poarta R0, puntea Local↔Cloud,
Live Review, Jules, inventarul de repo-uri, recuperarea stării mașinii,
doctrina operațională.

**În afara razei:** conținutul altor proiecte. Nu ating repo-urile lor. Când
un proiect are nevoie, dau prompt, Popy îl duce acolo.

**Regula Triadei:** `1 conversație = 1 folder = 1 repo`. Nu se încalcă.

---

## 1. Arhitectura

```
                    Popy (designer)
                          │  dă GOAL
                          ▼
        ┌─────────────────────────────────┐
        │  Mavis Local  (acest proiect)   │
        │  inginer de sistem              │
        │  · trei treceri înainte         │
        │  · commit autonom               │
        │  · push DOAR cu R0              │
        └───────────┬─────────────────────┘
                    │  git, prin poartă
                    ▼
        ┌─────────────────────────────────┐
        │  GitHub                          │
        │  = singura sursă de adevăr       │
        └───┬─────────────────────────┬───┘
            │                         │
   R0: da   │                         │  R0: nu
            ▼                         ▼
   ┌─────────────────┐      ┌──────────────────────┐
   │  Mavis Cloud    │      │  Jules               │
   │  cercetare,     │      │  auditor asincron    │
   │  date, volum    │      │  la cerere           │
   │  push direct    │      │                      │
   │  (container     │      └──────────────────────┘
   │   volatil)      │
   └─────────────────┘
            │
            ▼
   ┌──────────────────────┐
   │  Live Review         │
   │  raportează, nu oprește│
   │  1×/zi + la cerere   │
   └──────────────────────┘
```

**De ce așa:** repo-ul ca punte, nu un server. Git are diff, istoric,
rollback, e gratuit și nu pica. Un server custom pica. Un webhook n-are
coadă. Sheets nu are diff.

---

## 2. Dependențe

| Instrument | Stare | De ce-l trebuie |
|---|---|---|
| `git` | ✅ | version control |
| `gh` 2.97.0 | ✅ autentificat | repo-uri, PR, Actions |
| `node` | ✅ | instrumente Cloud |
| `python3` | ✅ | workflow + site |
| `lrc` v0.6.15 | ✅ | LiveReview — **doar după push** |
| PowerShell 5.1 | ✅ | scriptele de poartă |
| `bash` | ⚠️ | **hook-urile sunt sh** — dependență fragilă |

**Riscul bash:** hook-urile `pre-push` sunt scripturi `sh`. Pe Windows,
Git le rulează prin shell-ul disponibil. **Dacă nu există un `sh`
funcțional, poarta se scoate din funcțiune fără erori vizibile** — și
atunci nimeni nu mai e protejat. De verificat explicit la Pasul 5.

---

## 3. Decizii luate, cu motiv

| # | Decizie | Motiv |
|---|---|---|
| D1 | `main` only, fără ramuri | Popy nu poate urmări o ramură. O ramură nemonitorizată e lucru care încetează să existe. Reversibil fără pierderi; ireversibil cu pierderi. |
| D2 | Prag **50**, un singur număr | Patru valori în patru locuri = nor, nu poartă |
| D3 | Commit autonom, fără R0 | Dirty tree = panoul plin = panic. El nu poate fi în buclă. |
| D4 | Push doar cu R0 | Singurul lucru unde consimțămța lui e necesară |
| D5 | Poarta e **locală**, per repo | Un global a stricat ~70 repo-uri |
| D6 | `R0` = acordul lui. Verificarea = alt cuvânt. | Două sensuri, un cuvânt, un accident |
| D7 | Live Review doar după push, 1×/zi | Nu arde cota, nu blochează nimic |
| D8 | Cloud împinge fără R0 | Container volatil — altfel pierde date |
| D9 | Workflow-ul lui Cloud e template | Nu reinventăm ce ce e măsurat că merge |
| D10 | Doctrina trăiește în repo | O regulă în afara repo-ului nu e citită de nimeni |

---

## 4. Fazele executate

### ✅ Pasul 0 — Push-ul celor 3 repo-uri OPTIMUS

**Ce:** `Optimus-Mavis-Skills`, `OPTIMUS-Backbone`, `SENTINEL_PRIME`.
**Cum:** primele două direct; `OPTIMUS-Backbone` a refuzat — **poarta**.
Prin `scripts\git-autopush.ps1 -Acord`.
**Verificare:** `git ls-remote`, SHA server == SHA local, toate trei.
**Dovadă:** LiveReview a răspuns negativ → calea 2 → push confirmat,
**zero erori în panoul lui Popy**. Cele două căi au funcționat pe un
caz real, nu în teorie.

### ✅ Pasul 1 — Doctrina operațională

`SENTINEL_OPERATIONAL_DOCTRINE.md` §20 — 154 de linii, 11 subclauze.
Skillul `mavis-autonomous-operator-skill` creat. Două intrări în memory.
**Verificare:** fișierul e în repo și împins.

### ✅ Pasul 2 — HQ-ul Optimus CI

Folderul, clonarea lui `MAVIS-CLOUD`, lectura completă, cele 7 conflicte
identificate, documentația scrisă.

---

## 5. Fazele de executat

### PASUL 3 — Snapshot înainte de orice scrire

**PRIMUL MEREU.** Copie a trei zone cu risc:
- `D:\Alex_Knowlege_Vault` (52.933 fișiere)
- `E:\CLAUDE\MINTE\OLD DATA...\- OLD Work Files`
- `~/.minimax/vault-manifest/git-parked-2026-10-07`

**De ce primul:** Pașii 4 și 5 rescriu `.gitignore` pe mii de fișiere, și
un `.gitignore` scris greșit pe 52.933 de fișiere face daune
ireversibile.

| | |
|---|---|
| **Verificare** | număr de fișiere în copie **==** număr în original |
| **Anulare** | copia se șterge; originalul nu s-a atins |

### PASUL 4 — Repară Vault-ul

**Problema:** 36 urmărite din 52.933.

1. Rescrie `.gitignore` — **fără negație**: listă de excludere, nu de
   includere
2. `git check-ignore -v` pe **două** fișiere: unul care **trebuie**
   urmărit → „nu e ignorat"; unul care **nu** → rămâne ignorat
3. **Control de sensibilitate:** un fișier real de conținut, forțat
   ignorat, scos din `.gitignore` → **trebuie** să apară în `git status`.
   Dacă nu apare, testul nu dovedește nimic
4. Abia apoi `git add -A`, commit, raport cu numărul **real**

| | |
|---|---|
| **Verificare** | `git ls-files \| Measure-Object` → aproape de 52.933 |
| **Anulare** | `git reset --soft HEAD~1` |

### PASUL 5 — Config global: decizia lui Popy

Două variante, ambele reale:

**Varianta A** — scot `core.hooksPath` și `core.editor` din global.
Machine-wide, ~70 repo-uri respiră imediat. Contra: contrazice „nu se
atinge global" din skill — dar acea regulă era pentru *instalarea unui
proiect*, nu pentru igiena mașinii.

**Varianta B** — globalul rămâne, fiecare repo primește
`.git\lrc\disabled`. Contra: presupune să scriu în proiecte străine —
exact ce skillul interzice.

**Verificare:** repo nou, gol → `git commit` trebuie să reușească **fără**
atingere. Dacă eșuează, varianta aleasă n-a fost aplicată.
**Anulare:** o linie — `git config --global core.hooksPath <cale>`.

### PASUL 6 — `autocrlf` per repo

~70 de repo-uri au `true`; spec-ul cere `false` per repo. Se aplică
**doar** pe repo-urile lui Popy, identificate de el. Unu câte unu, cu
verificare.

`true` pe proiecte cu scripturi e cauza cea mai probabilă pentru
„îmi distruge build-urile locale". **Ipoteză, nu fapt** — se măsoară în
Pasul 3.

### PASUL 7 — Recuperează proiectul „distrus"

`git-parked-2026-10-07`: 13.581 în index, **zero comituri**.

**Nu `git checkout` direct** — dacă index-ul e inconsistent, pierzi
diferența. Se citește din index într-un **folder nou**, se compară cu ce
e pe disc, și abia apoi se decide.

| | |
|---|---|
| **Verificare** | recuperate == 13.581 din index |
| **Anulare** | folderul nou se șterge; originalul neatins |

### PASUL 8 — Repară `- OLD Work Files`

58.237 șterse, toate în istoric. **Remote greșit** — `prime-sentinel`,
același ca alt folder.

1. Se verifică cu `git cat-file`, **fără** scriere pe disc
2. Se scoate într-un folder **nou**, nu peste ce există
3. Se compară cu ce e acum (834 fișiere) și cu backup-ul

**Nu șterg nimic. Nu suprascriu nimic.** Mută, nu șterge.

### PASUL 9 — Sursa canonică în fiecare repo

Fiecare repo al lui Popy primește, **în istorie**, cele cinci lucruri:
**ce e** · **unde era** · **ce vine** · **cum e guvernat** ·
**cum se verifică**.

| | |
|---|---|
| **Testul** | repo clonat proaspăt, pe o mașină care nu l-a mai văzut → **continuă sau reîncepe?** |
| **Anulare** | un comit anulează; fișierul e versionat |

### PASUL 10 — Workflow-ul de verificare în Optimus CI

Se ia `verify.yml` din Cloud ca template, se extinde cu verificările
OPTIMUS. `schedule 03:00` + `workflow_dispatch`. **Niciodată pe push.**

### Pasul 11 — Puntea

Prin `git-autopush.ps1 -Acord`, **nu** prin `mavis-sync.sh` — acela ar
ocolește poarta. Testul de 2 minute, ambele sensuri.

### Pasul 12 — Inventar permanent

Script, un fișier: fiecare repo, cale, remote, ramură, urmărite,
neîmpinse, `hooksPath`, `autocrlf`. Rulează la sesiune. Repo
nemăsurabil → **„MĂSURĂTURĂ INCOMPLETĂ", exit 2**.

---

## 6. Protocol la eșec

| Situație | Ce faci |
|---|---|
| Push refuzat | arată motivul **exact cum l-a scris git**, nu „nu a ajuns" |
| `ls-remote` nu confirmă | **4 reîncercări**, 2s între ele, maxim 6s |
| Workflow eșuează | pushul e deja făcut și verificat. Nu e push eșuat. |
| Nu se poate măsura | **NECUNOSUT**, nu presupus. Se spune așa. |
| Scriptul nu pornește | cauza, într-un rând. Nu se încearcă altfel. |

**Nu se forțează niciodată.** Se repara cauza, nu se ocolește poarta.

---

## 7. Definiția de „gata"

- [ ] `MAVIS-OPTIMUS-CI` există, privat, pe GitHub
- [ ] README + DOCTRINA + BLUEPRINT în istorie
- [ ] Punctul de intrare: **3 fișiere, un agent nou știe tot**
- [ ] Un repo nou, gol, comită fără blocaj
- [ ] Vault-ul: `git ls-files` aproape de 52.933
- [ ] Niciun repo al lui Popy cu `hooksPath` global nerezolvat
- [ ] Zero hook-uri globale care blochează comituri
- [ ] Puntea testată în ambele sensuri
- [ ] Workflow-ul rulează la 03:00 și la cerere, **nu** la push
- [ ] Un agent nou, zero memorie, preia din README — **măsurat**

Ultima linie e singura care contează. **Restul e documentație.**

---

## 8. O singură decizie, la un moment dat

În acest plan există **o singură decizie care e a lui Popy**, și apare o
singură dată: **Pasul 5, varianta A sau B.**

Restul e tehnic, e luat de mine cu rucsac + logică + strategie, și
predat ca rezultat.

**Dacă o decizie nu se întâlnește între cele trei, o spun.** Altfel nu
întreb.