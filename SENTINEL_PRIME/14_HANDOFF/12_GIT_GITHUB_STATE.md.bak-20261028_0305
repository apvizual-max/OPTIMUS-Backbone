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

**`core.hooksPath` e gol** — configul local a fost rescris de pipeline-ul CD
(la 28 oct) și direcția hook-urilor LiveReview s-a pierdut. Hook-urile încă
există în `C:\Users\apviz\.git-hooks\`, dar nu mai sunt invocate de acest repo.
Atestation-ul se face manual: `lrc review --vouch --staged` înainte de commit.

## 2. Starea ramurii

| | Valoare | Ora |
|---|---|---|
| Ramură locală | `main` | 02:34 |
| `HEAD` local | `e89887f` (commit de reparare) | 02:34 |
| `origin/main` | `e89887f` — **identic** | 02:34 |
| Ahead / behind | **0 / 0** | 02:34 |
| Comituri pe `main` | **53** | 02:34 |
| Fișiere urmărite | 1.436 | 02:34 |
| Obiecte git | 1.481, `size-pack` 1,54 MiB | 02:34 |
| Stash | `stash@{0}` — snapshot pre-sync, păstrat | 02:34 |

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
| Statut | se sincronizează la `main`-ul final după ultimul push |
| În `.gitignore` | **da**, cu motiv scris — e copie de lucru, nu conținut de proiect |

## 6. Ce trebuie știut înainte de orice push

1. **Git scrie progresul pe stderr și aruncă o eroare roșie chiar la push
   reușit.** Verificarea de push e `git ls-remote`, niciodată exit code-ul.
2. **Verifică cu o clonă nouă**, nu doar cu `git log`. Un commit poate fi valid
   și totuși imposibil de checkout.
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
