# STARE GIT ȘI GITHUB — măsurată 2026-10-28

**Toate cifrele din acest document sunt măsurate**, cu ora indicată. Când nu
era măsurat, scrie `NOT_MEASURED`.

---

## 1. Identitate și configurație

| | Valoare | Ora |
|---|---|---|
| Repository | `https://github.com/apvizual-max/SENTINEL_PRIME.git` | 02:34 |
| Vizibilitate | **PRIVATE** | 02:34 |
| Ramură implicită | `main` | 02:34 |
| Creat pe GitHub | 2026-10-10 18:23:20 UTC | 02:34 |
| Utilizator `gh` | `apvizual-max` (keyring) | 02:34 |
| Identitate git | `Sentinel Prime <sentinel.prime@optimus.local>` | 02:34 |
| `core.hooksPath` local | **gol** | 02:34 |
| `core.longpaths` | `true` | 02:34 |
| `core.autocrlf` | `true` (system) | 02:34 |
| Disco GitHub | 12.180 KB | 02:34 |

**`core.hooksPath` e gol — și asta e starea corectă.** Măsurat la 02:50 pe 28
oct: `lrc hooks status` arată că hook-urile LiveReview sunt înregistrate pe
repo-ul **exterior** `projects` și **dezactivate** (`.git/lrc/disabled` = True).
Skill-ul `mavis-git-autonom-skill` spune explicit: *„LIVEREVIEW = doar DUPA
push, pe ce a ajuns pe GitHub. Niciodata inainte, niciodata la comit"* — pentru
că pe 2026-10-11 bloca fiecare commit. Așadar: `core.hooksPath` gol **nu e un
defect**, e configurația intenționată.

Ce **e** adevărat: scripturile `scripts\git-autopush.ps1` și
`scripts\push-status.ps1` pe care le numește același skill **nu există în acest
proiect** (are `02_OPERATIONAL\scripts\`, cu alte două scripturi). Nu e defect
al proiectului — e o trăsătură a skill-ului, și e consemnată aici ca instanța
nouă să nu le caute.

Atestation-ul se face manual: `lrc review --vouch --staged` înainte de commit.

## 2. Starea ramurii

| | Valoare | Ora |
|---|---|---|
| Ramură locală | `main` | 03:12 |
| `HEAD` local | `git rev-parse HEAD` (la 03:12: `956485e`, commitul de lucru) | 03:12 |
| `origin/main` | **identic** — `git ls-remote origin refs/heads/main` | 03:12 |
| Ahead / behind | **0 / 0** | 03:12 |
| Comituri pe `main` | **58** | 03:12 |
| Fișiere urmărite | 1.485 | 03:12 |
| Obiecte git | 1.481, `size-pack` 1,54 MiB | 02:34 |
| Stash | `stash@{0}` — snapshot pre-sync, păstrat | 02:34 |

**SHA-ul nu e scris ca cifră aici pentru că s-ar invalida singur** la fiecare
commit. Se citește:

```powershell
git rev-parse HEAD          # local
git ls-remote origin main   # remote  <- asta e verificarea de push
```

Cifrele de mai sus sunt cele măsurate la **03:12 pe 28 oct**. După ultimul
commit al sesiunii, SHA-ul final e în mesajul de commit.

### Comitul de reparare `e89887f`

```
e89887f  Repara: elimina directorul cu cale absoluta din radacina
         └─ parinte: 7290b26 (Jules, 27 oct) — istorica liniara
```

Cu **37 de comituri** înaintea lui, `origin/main` conținea la rădăcină un
director cu numele literal `C:\Users\apviz\.minimax-agent\projects\SENTINEL_PRIME`.
Git refuză `:` într-o componentă de nume, deci `read-tree`, `checkout` și
**orice clonă pe Windows** eșuau. Detalii complete în
`11_SESSION_HANDOFF_2026-10-28.md` §3 și în skill-ul
`07_BACKBONE\skills\sentinel-cd-pipeline-sync.SKILL.md`.

## 3. Cine mai scrie în acest repository

| Actor | Ce scrie | Unde |
|---|---|---|
| Antigravity CD Engine | starea runtime, commituri de sincronizare | direct în `main` |
| `google-labs-jules[bot]` | PR-uri code health, teste, security | direct în `main` |
| Mavis | feature, reparatii, audit, handoff | `main` |

**Invariant:** `main` e singura ramură activă. Nu crea ramuri pe remote.

**Nu există CI.** `gh run list` e gol, `.github/workflows` lipsește. Deci
**suitele trebuie rulate manual**, secvențial:

```powershell
python 08_SELF_IMPROVEMENT\test_suite.py
python 08_SELF_IMPROVEMENT\test_deployment.py
```

Ledgerul pipeline-ului: `JULES_HANDOFF.md` în rădăcină.

## 4. Ce s-a împins în această sesiune

| Commit | Ce conține |
|---|---|
| `e89887f` | repararea arborelui cu cale absolută (parinte: `7290b26`) |
| `50253b4` | pachetul de predare: priming prompt, session handoff, stare Git/GitHub, `SKILLS/` + manifest, index actualizat |
| `27023fd` | raportul de stare de la 02:43 |

Verificat cu `git ls-remote`, nu prin exit code:

```
local  = e89887fe97d71ac8882faa80124ef7af6512fd5d
remote = e89887fe97d71ac8882faa80124ef7af6512fd5d
IDENTICE = True
```

## 5. Clona locală `.github-repo`

| | Valoare |
|---|---|
| Locație | `C:\Users\apviz\.minimax-agent\projects\SENTINEL_PRIME\.github-repo` |
| Origine | clonă a aceluiași repository, la `main` |
| Statut | creată la `main`-ul final: **1.485 fișiere, `dirty=0`, SHA identic cu `main` și `origin/main`** (măsurat 03:12 pe 28 oct) |
| În `.gitignore` | **da**, cu motiv scris — e copie de lucru, nu conținut de proiect |

Se resincronizează după orice push nou, cu `git -C .github-repo pull --ff-only`.

## 6. Ce trebuie știut înainte de orice push

1. **Git scrie progresul pe stderr și aruncă o eroare roșie chiar la push
   reușit.** Verificarea de push e `git ls-remote`, niciodată exit code-ul.
2. **Verifică cu o clonă nouă**, nu doar cu `git log`. Un commit poate fi valid
   și totuși imposibil de checkout. Asta e acum un instrument, nu o rețetă:

   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File scripts\verify-remote-clone.ps1 `
       -ExpectFiles '14_HANDOFF\10_PRIMING_PROMPT.md,README.md'
   ```

   Măsoară 10 lucruri — intrări de arbore invalide, clonă nouă de la zero,
   `dirty=0`, HEAD-ul clonei egal cu SHA-ul remote-ului, o singură ramură,
   fișierele cerute prezente — și spune `VERDICT=PASS` / `VERDICT=FAIL`
   (exit 0 / 2). **Nu șterge nimic** și nu atinge arborele de lucru: lasă clona
   de probă în `%TEMP%` și-i afișează calea în `PROBE_CLONE=`.

   Un commit valid poate să nu fie clonabil: git **refuză `:`** într-o
   componentă de nume, iar un director cu cale absolută drept nume intră în
   arbore fără să apară în `git log` sau `git status`. Pipeline-ul a introdus
   exact așa o dată, în 3 zile, la comitul `3b3f9dd` (PR #14 al lui Jules).
   Rețeta de reparare e în `07_BACKBONE\skills\sentinel-cd-pipeline-sync.SKILL.md`.

   Instrumentul e **falsificat**, nu doar trecut: `scripts\make-broken-tree-control.py`
   construiește, la cerere, un repository cu exact defectul de mai sus, iar
   verificatorul trebuie să-l refuză:

   ```powershell
   python scripts\make-broken-tree-control.py
   powershell -NoProfile -ExecutionPolicy Bypass -File scripts\verify-remote-clone.ps1 `
       -Repo "$env:TEMP\sentinel-broken-tree-control" `
       -RemoteUrl "$env:TEMP\sentinel-broken-tree-control"
   # asteptat: VERDICT=FAIL, invalid_tree_entries 1, clone_exit 128
   ```

   Măsurat pe 28 oct: controlul → `VERDICT=FAIL` (exit 2), repo-ul real →
   `VERDICT=PASS` (exit 0). Ambele sensuri sunt testate în faza
   `cd_clone_verify` din `08_SELF_IMPROVEMENT\test_deployment.py`.
3. **Nu rescrie istoricul publicat.** Fără force-push, fără `git reset --hard`.
4. **`stash@{0}` e păstrat** ca a doua cale de recuperare a conținutului
   local-only. Nu se aruncă până când Popy nu confirmă că nu mai trebuie.
5. **Fișierele de stare runtime** (`09_LOGS\`, `13_COMMAND_CENTER\api\*.json`)
   sunt rescrise de daemon la ~17 minute. Se comitează, nu se ignoră — și
   pentru asta arborele e mereu murdăruit după fiecare commit.

## 7. Decizii ale lui Popy, încă deschise

- **Public sau privat.** Acum privat. Conține corpusul de conversații, adrese
  și log-uri. Se schimbă cu o comandă.
- **`.github-repo`** e cerut de Popy ca locul build-ului sincronizat. Nu se
  publică niciodată: conține corpusul.
