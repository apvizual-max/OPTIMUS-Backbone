# STATE-EXECUTIE — jurnalul de execuție, 2026-10-12

Adăugat ca **JURNAL_OGLINDA** (append-only). Corectările sunt intrări noi, nu
editări de intrări vechi. Fiecare cifră de mai jos a fost **măsurată**, nu
estimată; dacă o măsurătoare nu s-a putut face, scrie `MĂSURĂTURĂ INCOMPLETĂ`.

---

## 1. MAVIS-CLOUD trecut în privat — MĂSURAT

| | |
|---|---|
| Comanda | `gh repo edit apvizual-max/MAVIS-CLOUD --visibility private --accept-visibility-change-consequences` |
| `gh api` după comanda | `{"private":true,"visibility":"private"}` |
| Remote folosit | `https://github.com/apvizual-max/MAVIS-CLOUD.git` |

Prima încercare, `gh repo edit ... --visibility private` **fără**
`--accept-visibility-change-consequences`, a fost respinsă de gh cu mesajul
`use of --visibility flag requires --accept-visibility-change-consequences flag`
și repo-ul a rămas `PUBLIC`. Verificarea de după primul eșec a fost rulată, nu
presupusă — altfel am fi raportat reușită.

Toate cele patru repo-uri ale swarm-ului au fost verificate individual:

| Repo | Vizibilitate măsurată |
|---|---|
| `apvizual-max/MAVIS-CLOUD` | **private** |
| `apvizual-max/pkms-vault-automation` | private |
| `apvizual-max/prime-sentinel` | private |
| `apvizual-max/MAVIS-OPTIMUS-CI` | private |

## 2. `core.hooksPath` global eliminat — MĂSURAT

```
git config --global --unset core.hooksPath   → exit 0
```

Testul cerut explicit, rulat într-un repo nou, gol, inițializat cu `git init`:

| Măsurătoare | Valoare |
|---|---|
| Ieșire commit | `[master (root-commit) f4de22f] probe: verify commit runs clean…` |
| Cod de ieșire commit | **0** |
| `git config core.hooksPath` (local) | **vid** |
| Fișiere schimbate | 1 |

Commitul trece curat, fără blocaj de atestare. Probe-ul a fost aruncat ulterior
prin `mavis-trash` (`C:\Users\apviz\AppData\Local\Temp\hooktest_1739154624`).

## 3. Snapshot vault — MĂSURAT, MATCH pe toate trei surse

Copie cu `robocopy /E /COPY:DAT /DCOPY:DAT /R:1 /W:1 /MT:8 /XJ` în
`D:\_OPTIMUS-SNAPSHOT\2026-10-12\`. Originalele **nu au fost atinse**.

| Sursă → destinație | fișiere sursă | fișiere în backup | verdict |
|---|---|---|---|
| `D:\Alex_Knowlege_Vault` → `D-Alex_Knowlege_Vault` | 52.949 | 52.949 | **MATCH** |
| `E:\CLAUDE\MINTE\OLD DATA - To Adresss for Integration\- OLD Work Files` → `E-OLD-Work-Files` | 834 | 834 | **MATCH** |
| `~/.minimax\vault-manifest\git-parked-2026-10-07` → `git-parked-2026-10-07` | 9.845 | 9.845 | **MATCH** |

Volum: 61.258 MB · 419 MB · 136 MB — identice în sursă și în backup.
Raportul scris de robot: `D:\_OPTIMUS-SNAPSHOT\2026-10-12\SNAPSHOT-REPORT.txt`.
Toate cele trei copii au `robocopy_rc=1` (1 = fișiere copiate, fără erori).

## 4. `.gitignore` rescris ca listă de excludere — MĂSURAT

**Cauza măsurată a vechiului eșec:** regula veche interzicea totul și redeschidea
4 căi; rezultatul a fost **36 de fișiere urmărite din 52.949 existente (0,07%)**.
`git status` raporta curat, iar auto-salvarea a raportat succes de 58 de ori
pentru conținut care nu a intrat niciodată în istoric.

**Descoperire care nu era în plan:** în vault există **3 repo-uri git imbricate**.
Git nu coboară într-un director care e el însuși repo — îl tratează ca gitlink și
nu parcurge nimic din interior:

| Repo imbricat | efect masurat |
|---|---|
| `10_Work\…\Client Data sets\PLATEFUL - DTC - Niv` | 143 fișiere dispărute fără mesaj |
| `_SYSTEM\Skills\Skills_Archive\_Skills_BackUp_Archive_2026-07-15\agent-browser` | 445 fișiere dispărute fără mesaj |
| `_QUARANTINE\indexuri generate in gresit\Skills_Archive\_Skills_BackUp_Archive_2026-07-15\agent-browser` | restant |

**Limita de platformă, masurată:** GitHub **respinge la push orice fișier peste
100 MB**. În vault există **106 fișiere peste 100 MB, însumând 48.961 MB**.
Nu e preferință, e o limită: „cifra reală" de urmărit nu poate fi 52.949, pentru
că 106 dintre acele fișiere nu pot ajunge niciodată în istoricul git.

### Cazuri de excludere, toate măsurate

| Caz | ce exclude | număr |
|---|---|---|
| 1 | gunoaie tehnica: `.trash/`, `.sentinel_temp/`, `.wwebjs_cache/`, `.vault-intelligence/`, `raport-archive/`, `.obsidian/`, `node_modules/`, `desktop.ini`, `Thumbs.db`, `.DS_Store`, `*.tmp` | 1.197 fișiere |
| 2 | stare vie care se rescrie singură: cele 3 loguri de la rădăcină / în AI-Kit și `INDEX CENTRAL.md` | 3 fișiere |
| 3 | binare peste 100 MB | 103 fișiere / 47,40 GB |
| 4 | repo-uri git imbricate | 588 fișiere |

Logul `raport-aliniere.log` era **urmărit** înainte și a fost scos din index cu
`git rm --cached`; de aceea are nevoie de regulă, nu doar de excludere.

### Testele `check-ignore` cerute — rezultate

| # | Fișier | Așteptat | Măsurat |
|---|---|---|---|
| 1 | `10_Work\…\Andu_OD - Investire_RO.psd` (1.575 MB) | ignorat | `.gitignore:72` — **ignorat** |
| 2 | `COTOR.md` | urmărit | fără ieșire — **urmărit** |
| 3 | `AI-Kit\paths.ps1` | urmărit | fără ieșire — **urmărit** |
| 4 | `raport-aliniere.log` | ignorat | `.gitignore:42` — **ignorat** (după `git rm --cached`) |
| 5 | `.obsidian\workspace.json` | ignorat | `.gitignore:34` — **ignorat** |
| 6 | `10_Work\…\PLATEFUL - DTC - Niv\00_INDEX.md` | ignorat | `.gitignore:53` — **ignorat** |

Verificarea de scurgere a gunoaierii: `.obsidian`, `.trash`, `node_modules`,
`.wwebjs_cache`, `.vault-intelligence`, `.sentinel_temp` — **0 fișiere** fiecare
în lista candidaților.

### Numărul final urmărit

| | înainte | după |
|---|---|---|
| fișiere urmărite | **36** | **50.408** (măsurat după `git add`, nu estimat) |
| fișiere rămase neadăugate | 52.913 | **0** (`REMAINING_NOT_ADDED=0`) |
| arbore de lucru | curat | curat (`STATUS_LINES=0`) |

**Defect #2, descoperit la executare:** primul `git add -A` a eșuat cu
`fatal: adding files failed — Filename too long`. Măsurat: **155 căi depășesc
limita Windows de 260 de caractere** (maxim 329). Reparat cu
`git config core.longpaths true` în repo-ul vaultului; al doilea `git add` a
trecut fără nicio eroare, în 657 de secunde.

### Starea finală măsurată a repo-ului

| | valoare |
|---|---|
| commit nou | `0ed09f1b` |
| fișiere urmărite | 50.408 |
| commituri totale | 91 |
| commituri **neîmpinse** | **60** — dintre care **59 sunt comituri vechi „Salvare automata"** (13:11–20:06, 2026-10-11, inclusiv bucla de 55 de comituri pe `AI-Kit/raport-autocomit.log`) și **1 este al meu** |
| volum `.git` | **9,84 GB** |
| remote | `apvizual-max/pkms-vault-automation` (**private**) |

**Nimic nu a fost împins.** Următorul pas — push-ul celor 9,84 GB — **cere R0
explicit** și nu a fost cerut. Un push ca acesta trimite conținut personal
(CV-uri, dosare de clienți, documente de identitate) în istoricul unui repo
remot: odată împins, nu se mai poate șterge curat. Decizia e a lui Popy.

## 5. Punctul 2 — ștergerea referințelor la Pull Requests din `CI-NOTES.md` — NEEXECUTAT, din motiv măsurat

`CI-NOTES.md` se află în `MAVIS-CLOUD`, repo pe care Popy l-a declarat
**read-only**: „you do not touch Mavis's cloud repo. You just read them and copy
from them." Ordinul de ștergere și ordinul de read-only se contrazic. Nu aleg
unul în locul celuilalt — înregistrez aici, în repo-ul meu, decizia de aplicat
mai târziu când MAVIS-CLOUD va fi declarat scrisibil.

## 6. Gate-uri: ce nu s-a atins

- `git clean -fdx` și `git reset --hard` — **nu au fost rulate** în niciun repo.
- `scripts\git-autopush.ps1` — nu a fost invocat; niciun push nu a fost cerut.
- Alte proiecte — niciun repo din afara `D:\Alex_Knowlege_Vault` nu a fost
  modificat în această executare.