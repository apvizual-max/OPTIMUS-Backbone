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
| Ramură locală | `main` | 09:36 |
| `HEAD` local | `git rev-parse HEAD` (la 09:36: `aa49c72`, comitul cu cadența handshake-ului pe ceas) | 09:36 |
| `origin/main` | `git ls-remote origin refs/heads/main` → `7cf6d4b` (starea de dinaintea push-ului) | 09:36 |
| Ahead / behind | **0 / 7** — șapte comituri locali neîmpinși | 09:36 |
| Comituri pe `main` | **73** | 09:36 |
| Fișiere urmărite | 1.547 | 09:36 |
| Obiecte git | 1.481, `size-pack` 1,54 MiB | 02:34 |
| Stash | `stash@{0}` — snapshot pre-sync, păstrat | 09:36 |
| Ramuri (local / remote) | `main` / `origin`, `origin/main` — **una singură**, fără ramuri de feature | 09:36 |
| PR-uri pe remote | **59 în total — 36 MERGED, 23 CLOSED, 0 OPEN** | 09:36 |

**Verificarea porții înainte de push, măsurată la 09:36** (nu presupusă):

```
git ls-remote origin refs/heads/main   ->  7cf6d4b4a6002d5581a93258661ecb1bfc0f2499
git rev-list --left-right --count origin/main...HEAD   ->  0    7
git merge-base --is-ancestor origin/main HEAD   ->  exit 0   (0 = local conține remote-ul)
git ls-remote --heads origin   ->  o singură ramură: refs/heads/main
gh pr list --state open        ->  []
```

`0 în urmă / 7 în față` înseamnă că arborele local conține **tot** ce e pe GitHub și
împinge doar ce a apărut după. Nu e nevoie de merge: `origin/main` e strămoș, deci
push-ul e o fast-forward.

**SHA-ul nu e scris ca cifră aici pentru că s-ar invalida singur** la fiecare
commit. Se citește:

```powershell
git rev-parse HEAD          # local
git ls-remote origin main   # remote  <- asta e verificarea de push
```

Cifrele de mai sus sunt cele măsurate la **03:12 pe 28 oct**, plus re-măsurarea de
la **07:50 pe 28 oct** (sesiunea de preluare: auditul registrului de gap-uri).
După ultimul commit al sesiunii, SHA-ul final e în mesajul de commit.

### Ce a rămas neîmpins la 07:50 pe 28 oct

| comit | ce | de ce |
|---|---|---|
| `a80bf49` | `chore: update health.json` — starea runtime rescisa de daemon | era deja neîmpins la începutul sesiunii |
| `8b7be11` | registrul de gap-uri reparat: 13 intrări închise prin măsurătoare, constructorul îmbinează în loc să suprascrie, control falsificat | sesiunea de preluare |

**Push = R0.** Nimic nu s-a împins. Verificarea de push rămâne
`scripts\verify-remote-clone.ps1` — instrument, nu ochi: `VERDICT=PASS` / `FAIL`
(exit 0 / 2).

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

### Push-ul din 09:38, pe 28 oct

**20 de comituri** peste `e89887f`, dintre care 13 erau deja pe remote (împinși de
pipeline-ul CD, care a ajuns la `7cf6d4b`) și **7 sunt noi**, locali:

| Commit | Ce conține |
|---|---|
| `8b7be11` | registrul de gap-uri reparat: cele 9 servere Hermes sunt construite, iar constructorul nu mai distruge ledgerul |
| `9e417ea` | starea Git și deciziile deschise, re-măsurate după auditul registrului |
| `158872d` | starea runtime re-măsurată: panoul arată 6 gap-uri deschise |
| `aa49c72` | cadența handshake-ului pe ceas + verdictul `STALE` acoperit (suite 612/0/0) |

Ce conțin cei 13 comituri ai pipeline-ului (la fel de ai noștri, în istoric):
`50253b4` pachetul de predare, `27023fd` raportul de la 02:43, `956485e` handshake pe
bucla de refresh, `122dccf` raportul final, `d81ffe9`/`ce6b0ed` skillurile
reîmprospătate, `80390d7` verificarea cu clonă nouă, `2ee62af` trei skilluri noi,
`98f22d6` auditul primei uși (R17), `dc5f356` ghilimelele duble în PowerShell 5.1,
`7cf6d4b` verificarea remote-ului după push.

**Verificarea după push** se face cu două comenzi, nu cu exit code-ul:

```powershell
git ls-remote origin refs/heads/main      # trebuie să fie identic cu `git rev-parse HEAD`
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\verify-remote-clone.ps1 `
    -Repo "$env:USERPROFILE\.minimax-agent\projects\SENTINEL_PRIME" `
    -ExpectFiles "14_HANDOFF\10_PRIMING_PROMPT.md,README.md,14_HANDOFF\11_SESSION_HANDOFF_2026-10-28.md,14_HANDOFF\12_GIT_GITHUB_STATE.md"
```

Instrumentul măsoară 10 lucruri (intrări de arbore invalide, clonă nouă de la zero,
`dirty=0`, HEAD-ul clonei egal cu SHA-ul remote-ului, o singură ramură, fișierele
cerute prezente) și spune `VERDICT=PASS` / `VERDICT=FAIL` (exit 0 / 2).

### Verificarea după push — măsurată la 09:40

```
remote main     = f01c76d320cc2b98e61d1fb92587736ec9b64786
local HEAD      = f01c76d320cc2b98e61d1fb92587736ec9b64786
IDENTICE        = True
behind / ahead  = 0 / 0
```

Instrumentul, pe o clonă nouă de la zero (nu pe arborele de lucru):

```
CHECK remote_main_sha        f01c76d320cc2b98e61d1fb92587736ec9b64786   PASS
CHECK remote_branches        1                                          PASS
CHECK local_head             f01c76d320cc2b98e61d1fb92587736ec9b64786   PASS
CHECK behind_ahead           0/0                                        PASS
CHECK invalid_tree_entries   0                                          PASS
CHECK clone_exit             0                                          PASS
CHECK clone_head_sha         f01c76d320cc2b98e61d1fb92587736ec9b64786   PASS
CHECK clone_dirty            0                                          PASS
CHECK clone_branches         main                                       PASS
CHECK clone_tracked_files    1547                                       PASS
CHECK expect_files_missing   0                                          PASS
VERDICT=PASS
```

SHA-ul de mai sus e **o citire cu ora indicată**, nu o stare: următorul comit îl
invalidă singur. Starea curentă se citește cu `git ls-remote origin refs/heads/main`.

## 5. Clona locală `.github-repo`

| | Valoare |
|---|---|
| Locație | `C:\Users\apviz\.minimax-agent\projects\SENTINEL_PRIME\.github-repo` |
| Origine | clonă a aceluiași repository, la `main` |
| Statut | **resincronizată**: `dirty=0`, **1.547 fișiere**, `HEAD` identic cu `main` local — SHA-ul se citește, nu se memorează: `git -C .github-repo rev-parse HEAD` |
| În `.gitignore` | **da**, cu motiv scris — e copie de lucru, nu conținut de proiect |

**Cum se resincronizează.** Cu `git -C .github-repo pull --ff-only` după orice push
nou. Când mirrorul trebuie adus la un commit **local, neîmpins încă**, se face
`git -C .github-repo fetch <calea repo-ului local> main` și apoi
`git -C .github-repo merge --ff-only FETCH_HEAD` — o fast-forward, niciodată un reset.
Măsurat pe 28 oct: `Updating 7cf6d4b..aa49c72` / `Fast-forward`, apoi încă o
fast-forward până la comitul de documentație; `dirty=0`, **1.547 fișiere** — același
număr ca arborele principal, și `HEAD` identic cu `main`.

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
- **Noua, 2026-10-28 07:50 — `HPROF_NPX_LAUNCH`.** Blueprintul pornește cele două
  servere de profil npm (`filesystem`, `browser`) cu comanda bare `npx`, care pe
  Windows e un batch file și nu s-a putut lansa dintr-un launcher fără shell
  (`WinError 2`, măsurat). Profilul MCP viu folosește shim-ul `.cmd` instalat.
  Repointarea unei declarații e decizia lui Popy; precedentul există și e ratificat
  (2026-10-10, `web-tools` și `git` repointate de la pachete npm fantomă la servere
  locale). Detalii: `13_GAP_REGISTER_AUDIT_2026-10-28.md` §8.
