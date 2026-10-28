# Istoricul migrării — ce s-a întâmplat, măsurat

Tot ce mai jos e **măsurat în sesiunea din 28 octombrie 2026**, cu comanda
care a produs numărul. Când o valoare e o estimare, scrie `NOT_MEASURED`.

---

## 0. Problema

`C:\Users\apviz\.minimax-agent\projects` era rădăcina de lucru și, în același
timp, rădăcina git — și acolo erau înglobate **trei repo-uri git cu remote
propriu** (`SENTINEL_PRIME`, `60_SKILLS/_links/mavis-skills`, plus
`Mavis-Google_Access`), la același nivel de folder. Structura era împrăștiată
pe mai multe proiecte: `projects\`, `AI_Tools\`, `E:\Google\GDrive\...`,
`C:\Users\apviz\.minimax\...`.

Cerința: **un singur punct de adevăr**, în care să stea toate datele — fără
trunchiere, fără ștergere — și totul pe un singur branch, un singur repo, în
GitHub și local.

## 1. Decizia: mutare, nu copiere

SOT-ul a fost creat de Popy: `projects\Mavis-Optimus-Dashboard`. Tot ce a
fost în `projects\` a fost **mutat** în el, prin
`[System.IO.Directory]::Move` (renumare atomică pe același volum), nu copiat
și șters.

- **61 de elemente** de top-level mutate direct.
- **902 de elemente** suplimentare mutate în parcurgerea recursivă
  (`SENTINEL_PRIME` are peste 3.000 de fișiere).

## 2. Git: datele au fost mutate, nu reclonate

Intrarea de director `.git` era ** blocată** de aplicația desktop (watcher).
Soluția măsurată: conținutul ei (14 copii) era mutabil, deci fiecare copil a
fost mutat individual în `SOT\.git`.

Rezultat verificat imediat după mutare:

| | |
|---|---|
| toplevel | `C:/Users/apviz/.minimax-agent/projects/Mavis-Optimus-Dashboard` |
| branch | `main` |
| commituri | 76 (în acel moment) |
| remote | `https://github.com/apvizual-max/OPTIMUS-Backbone.git` |
| fișiere urmărite | 326 |
| branchuri și tag-uri | toate păstrate |

**Nu s-a clonat.** Clonarea ar fi produs un istoric nou, fără obișele
locale. Mutarea păstrează obiectele, referințele și ramurile.

## 3. Repararea căilor: 198 de fișiere

Toate referințele la calea veche a rădăcinii au fost rescrise:
`C:\Users\apviz\.minimax-agent\projects` → `...\projects\Mavis-Optimus-Dashboard`
(și forma cu slash invers), **păstrând encoding-ul și starea BOM**-ului.

Verificare: **77 de `.ps1` și 124 de `.js` parse-clean**. Singurele erori
rămase sunt cele 7 din `_gen-docs.ps1`, demonstrate identice în `HEAD` — deci
preexistente, nu regresie.

## 4. Referințele externe, updatate

| Ce | Câți | Metodă |
|---|---|---|
| Taskuri Windows | 9 | `Set-ScheduledTask` |
| Servere MCP în `mcp.json` | 9 | **prin interfața `mavis mcp update`**, nu editare manuală |
| `C:\Users\apviz\.minimax\AGENTS.md` (global) | 8 căi | editare directă, LF și BOM păstrate |
| Registry live de skill-uri | 44 fișiere | editare directă |
| Hook-uri `pre-push` pe `E:` | 3 | editare directă |
| Alte | `provision-grant.cjs`, `core\state.json` din QWEN, `fleet_health_check.ps1`, `SENTINEL Command Center.bat` | editare directă |

Serverele MCP s-au respawnat **automat** din noile căi — verificat, nu
presupus.

## 5. Defect găsit pe drum: %TEMP% epuizat

Control Center-ul răspundea **HTTP 500**. Cauza, măsurată:

- `%TEMP%` ținea **111.417 de fișiere** (65.662 `.tmp` + 36.254 `.wav` + 6.201
  fără extensie), 318,5 MB, scurgere între 06 și 10 octombrie.
- `GetTempFileName` eșua **0/12** cu TEMP-ul original și **12/12** cu un TEMP
  curat → cauza e resursa epuizată, **nu** migrarea.

Corectia: helper nou în proiect, `scripts\lib\mavis-temp.ps1`, cu nume GUID
(pure ASCII, 0 octeți >127), folosit în cele 6 fișiere de runtime. În
`server.ps1`, dot-source-ul e **înainte** de `New-MavisTempFile` — un runspace
separat nu moștenește funcții dot-sourced.

Rezultat: Control Center → **HTTP 200**, 40.190 octeți.

## 6. Unirea celor cinci repo-uri

Fiecare repo a intrat ca **merge-commit cu doi părinți** — al doilea părinte
e commit-ul sursei. Recipe-ul a fost **probat înainte**, într-un repo scratch:
`git subtree add` păstrează istoricul (`merge-base --is-ancestor` = 0) și
suportă prefixe imbricate.

| Prefix | Commit sursă | Merge-commit | Doveză |
|---|---|---|---|
| `SENTINEL_PRIME/` | `3757b53` | `b54e827` | `is-ancestor` = 0 |
| `Mavis-Google_Access/` | `549c348` | `08c017f` | `is-ancestor` = 0 |
| `Optimus_CI (by Mavis)/` | `fb38972` | `82143c2` | `is-ancestor` = 0 |
| `60_SKILLS/mavis-skills/` | `8e90b56` | `dd9b2aa` | `is-ancestor` = 0 |
| `Mavis-Google_Access/.work/MAVIS-CLOUD/` | `b611b95` | `1ba9416` | `is-ancestor` = 0 |

Toate cele șase referințe (inclusiv `3b6b7dc`, head-ul vechi al MAVIS-CLOUD)
sunt **strămoși** ai `main` la final: **590 de commituri, 1.777 de fișiere
urmărite**.

### 6.1 MAVIS-CLOUD era shallow

Repo-ul avea **6 commituri** și `.git\shallow` — o clonă `--depth`. Git
refuză fetch dintr-un repo shallow peste istoric existent
(`shallow roots are not allowed to be updated`).

Rezolvat pe sursă, nu în SOT: `git fetch --unshallow origin` → **244 de
commituri**, iar remote-ul era **înaintea** noastră (`b611b95` vs `3b6b7dc`).
Am făcut `merge --ff-only` pe sursă, apoi am unit rezultatul. **Conținutul
local nu era cel mai nou** — asta era exact condiția pe care o indicase
obiectivul.

### 6.2 Trei incidente reale, întâlnite pe parcurs

**a) Intrarea de director blocată.** `SENTINEL_PRIME` nu putea fi redenumit:
`Access denied` / `in use by another process`. Soluția măsurată: mutarea
**copiilor**, copil cu copil, recursiv; coșurile rămase goale s-au încercat
ulterior. Conținutul nu s-a pierdut: 7.061 de elemente în staging.

**b) Un `.git` cuibărit strică vederea git-ului.** După unire, un proces
extern a clonat din nou `apvizual-max/SENTINEL_PRIME` în `SENTINEL_PRIME`
(la 12:56:46). Gitul a tratat directorul ca repo cuibărat și a raportat
1.584 de fișiere ca **șterse** din working tree — deși conținutul era corect
(același commit `3757b53`). `.git`-ul cuibărit a fost scos (recuperabil), iar
arborele s-a realiniat cu index-ul. `diff-index --quiet HEAD` → 0.

**c) Starea runtime vs. arborele curat.** Repo-ul SENTINEL era murdar
permanent (17 intrări schimbate la fiecare ciclu). Într-un monorepo, asta
înseamnă că arborele nu poate sta curent niciodată. S-au scos **1.239 de
fișiere de stare din urmărire** — **rămân pe disk**, istoricul lor e în
commit-urile anterioare, iar motivul e scris în `.gitignore` și în mesajul
de commit. Două fișiere sursă rescise de motor (`test_suite.py`,
`test_sentinel.md`) au fost scoase la fel, măsurat: motorul le rescrie la
fiecare ciclu.

## 7. Poarta de push — demonstrată, nu declarată

`scripts/git-hooks/pre-push` e **canonică** (2.061 octeți, ASCII, LF).
Varianta cu `NOTA` incidentului nu se afla în niciun ref
(`git log --all -S 'NOTA 2026-10-28'` → gol) și a fost recuperată din copia
rămasă la `projects\scripts\git-hooks\pre-push` — acum e varianta canonică,
versionată, iar calea veche e un junction spre ea.

Cele două comportamente, măsurate:

| Situație | Rezultat |
|---|---|
| `git push --dry-run` fără acord | **exit 1**, mesajul porții, fără contact cu remote-ul |
| `git push --dry-run` cu `.git\PUSH-ACORD` | **exit 0**, ajunge la remote, markerul e consumat |

Sinteza: `sh -n` → exit 0. Poarta e **activă** (`core.hooksPath = .git/hooks`)
 și **capabilă să eșueze**.
