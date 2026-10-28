# INVENTAR REPO-URI

> Măsurat **2026-10-24**, **re-măsurat 2026-10-27** prin `gh repo list
> apvizual-max --limit 60 --json name,visibility,pushedAt` și `gh api
> repos/apvizual-max/<R>`.
> **Înlocuiește** inventarul din 2026-10-11/12, ale cărui vizibilități au
> devenit false.
>
> **Cifrele de push sunt cele din 27 oct.** Activitatea din 26 oct a atins
> aproape toate repo-urile — de aceea inventarul vechi era depășit.

---

## 1. Repo-urile GitHub ale lui Popy

**Toate cele 10, măsurate azi.**

| Repo | Vizibilitate | Ramură | Ultim push | Rol |
|---|---|---|---|---|
| `apvizual-max/MAVIS-CLOUD` | **PUBLIC** | `main` | 2026-10-27T04:39:28Z | **puntea** Local↔Cloud · ținta de lucru a lui Jules |
| `apvizual-max/MAVIS-OPTIMUS-CI` | **PUBLIC** | `main` | 2026-10-27T04:56:52Z | **SOT CI** — acest proiect |
| `apvizual-max/MAVIS-OPTIMUS-CD` | **nu există** | — | — | **SOT CD** — se creează la priming (R0) |
| `apvizual-max/OPTIMUS-Backbone` | **PUBLIC** | `main` | 2026-10-24T23:55:39Z | consola OPTIMUS + scripturi Git |
| `apvizual-max/Optimus-Mavis-Skills` | **PUBLIC** | `main` | 2026-10-27T05:07:57Z | skillurile agentului |
| `apvizual-max/pkms-vault-automation` | **PUBLIC** | **`master`** | 2026-10-26T18:13:08Z | menținerea vaultului |
| `apvizual-max/SENTINEL_PRIME` | **PRIVATE** | `main` | 2026-10-27T01:00:44Z | substratul doctrinei |
| `apvizual-max/Qwen-Ecosystem-Dashboard` | **PRIVATE** | `main` | 2026-10-24T23:55:31Z | sistem Qwen |
| `apvizual-max/hermes-doctor` | **PUBLIC** | `main` | 2026-10-27T01:03:52Z | plasa lui Hermes |
| `apvizual-max/hermes-local-backup` | **PUBLIC** | `main` | 2026-10-26T22:21:46Z | backup săptămânal Hermes |
| `apvizual-max/hermes-agent-temp` | **PRIVATE** | `main` | 2026-10-26T22:21:48Z | fork Hermes |

> **Re-măsurat 2026-10-27, ~05:30Z**, după livrarea cozii și publicarea
> instrumentelor. Comanda: `gh repo list apvizual-max --limit 60
> --json name,visibility,pushedAt`. Cifrele de push s-au schimbat față de
> 24 oct — activitatea din 26 oct (consolidarea pe `E:`) a atins aproape
> toate repo-urile, iar rândul de azi a atins 5 dintre ele.
> **Visibilitățile nu s-au schimbat**: 7 publice, 3 private.

> **`MAVIS-OPTIMUS-CD` încă nu există** pe GitHub — măsurat 2026-10-27, absent
> din `gh repo list`. Crearea lui e R0 deschis, și aparține sesiunii CD.

> **Nicio ramură nu e protejată** (`required_status_checks` → 404 „Branch not
> protected"), pe `MAVIS-OPTIMUS-CI` și pe `MAVIS-CLOUD`. Măsurat 2026-10-27.
> Înseamnă că poarta de secrete din `pre-commit` e singura verificare locală
> înainte de push — **nu** există o verificare impusă de server.

### Corectare față de inventarul din 2026-10-11/12

| Repo | Inventar vechi | **Măsurat azi** |
|---|---|---|
| `Optimus-Mavis-Skills` | privat | **public** |
| `OPTIMUS-Backbone` | privat | **public** |
| `hermes-doctor` | privat | **public** |
| `hermes-agent-temp` | public | **privat** |
| `pkms-vault-automation` | privat | **public** |

> **7 repo-uri din 10 sunt publice.** Conținutul lor e citibil de oricine.
> În `MAVIS-CLOUD` sunt și date personale ale lui Popy — decizia e a lui, dar
> se spune cu voce tare. **Nu se adaugă nimic nou cu date personale în
> repo-uri publice, fără R0.**

---

## 2. Starea canalelor GitHub, măsurată

| Repo | `.github/workflows/` | Secrete de repo | PR-uri deschise |
|---|---|---|---|
| `MAVIS-CLOUD` | `jules.yml`, `verify.yml` | `JULES_API_KEY` (1) | **0** |
| `MAVIS-OPTIMUS-CI` | **`ci-verify.yml` — pe remote** (blob `6f0fd55`) | **0** | **0** |
| `MAVIS-OPTIMUS-CD` | — (nu există) | — | — |

**Măsurat 2026-10-27**, cu `gh api repos/apvizual-max/<R>/contents/.github/workflows`,
`gh api repos/apvizual-max/<R>/actions/secrets --jq .total_count` și
`gh pr list --repo apvizual-max/<R> --state open --limit 100 --json number`.

> **Corectare de drift (27 oct):** secțiunea spunea *„`.github/workflows/`
> dă 404 pe remote — workflow-ul `ci-verify.yml` există doar în copie locală,
> între cele 17 commituri neîmpinse"*. **Nu mai e așa.** Workflow-ul a ajuns
> pe remote odată cu împungerea lui `65af38f` (26 oct), iar azi e confirmat la
> `origin/main`: `git merge-base --is-ancestor 65af38f origin/main` → exit 0,
> `git cat-file -e origin/main:.github/workflows/ci-verify.yml` → exit 0, blob
> `6f0fd55`. PR-urile deschise în `MAVIS-CLOUD` au scăzut de la 22 la **0**.
> **Cine împinge vede ce a aterizat** — de aceea verificarea serverului e o
> plasă de siguranță pentru conținutul împins, nu o poartă de intrare.

**`JULES_API_KEY` e prezent doar în `MAVIS-CLOUD`.** Măsurat pe toate cele
6 repo-uri din registru. În celelalte calea automată nu se declanșează.

---

## 3. Cele mele, active

| Cale locală | Remote | Stare |
|---|---|---|
| `E:\Google\GDrive\…\CASA\OPTIMUS - Prime\Optimus_CI (by Mavis)\` | `MAVIS-OPTIMUS-CI` | **acest proiect** · **0 commituri neîmpinse** (HEAD = remote) · gitdir `E:/Google/GitData-Optimus-CI/repo` |
| `E:\Google\GDrive\…\CASA\OPTIMUS - Prime\Optimus_CD (by Jules)\` | `MAVIS-OPTIMUS-CD` | **SOT CD** · repo GitHub de creat la priming · gitdir `E:/Google/GitData-Optimus-CD` |
| `E:\Google\GDrive\…\Optimus_CI (by Mavis)\cloud-ingest\MAVIS-CLOUD\` | `MAVIS-CLOUD` | clona **și copia de lucru a livrării**: contractul consumatorului cere „Local scrie sarcina aici" → `scripts/queue-deliver.ps1` scrie și împinge aici. **Aditiv** — nimic existent nu se rescrie · gitdir `E:/Google/GitData-Optimus-CI/clone-MAVIS-CLOUD` |
| `E:\Google\GDrive\…\Optimus_CI (by Mavis)\cloud-ingest\MAVIS-OPTIMUS-CI\` | `MAVIS-OPTIMUS-CI` | clonă de lucru a acestui repo · gitdir `E:/Google/GitData-Optimus-CI/clone-MAVIS-OPTIMUS-CI` |
| `~/.minimax/agents/mavis/skills` | `Optimus-Mavis-Skills` | skillurile |
| `~/.minimax-agent/projects` | `OPTIMUS-Backbone` | consola OPTIMUS |

**Joncțiunile pe `C:`** (acces rapid, sursa rămâne pe `E:`):

| Acces rapid | Sursa fizică |
|---|---|
| `C:\Users\apviz\.minimax-agent\projects\Optimus_CI (by Mavis)` | `E:\…\CASA\OPTIMUS - Prime\Optimus_CI (by Mavis)` |
| `C:\Users\apviz\.minimax-agent\projects\Optimus_CD (by Jules)` | `E:\…\CASA\OPTIMUS - Prime\Optimus_CD (by Jules)` |

> **Calea veche a dispărut.** `…\projects\Mavis-Optimus-Continuous-Integration\`
> a fost eliminată prin Trash recuperabil (3 niveluri, EXIT 0) pe 27 oct.
> Nimic nu s-a pierdut: istoricul e în `E:\Google\GitData-Optimus-CI/repo`.

**Măsurat 2026-10-27, ~05:30Z:** `git rev-list --left-right --count origin/main...main`
→ **0 înainte / 0 înapoi** — `refs/heads/main` **= HEAD local**,
`DIVERGENCE=0 0`. Divergența s-a închis prin împungerea cu `merge --no-ff`
(commitul de combinare `86669d9`, **doi părinți** — istoricul sesiunii CD a fost
**inclus**, nu suprascris) și împungerea ulterioară a lucrării de azi. SHA-ul
se măsoară: `git ls-remote origin refs/heads/main`.

---

## 4. Repo-uri cu probleme, măsurate

| Cale | Problemă |
|---|---|
| `D:\Alex_Knowlege_Vault` | 36 urmărite din 52.933 |
| `E:\CLAUDE\...\OLD Work Files` | 58.237 șterse, remote greșit |
| `~/.minimax/vault-manifest/git-parked-2026-10-07` | 13.581 în index, 0 comituri |
| `E:\Ai_GDrive_Folder\X58 - PlayStation...` | `git init` în folder de joc, al altcuia |

## 5. Zgomot — nu atinge

31 de clone „GitHub backup 2026-10-08" pe `C:` și `D:`; 45 de repo-uri de
ritual în `Temp`; 24 de arhive `CLAUDE_BACKUP_*` pe `E:`.

**Nu sunt periculoase. Sunt zgomot.** Un inventar care le numără ca
probleme pierde semnalul.

## 6. Regula

**Orice repo care nu e al lui Popy — nu se atinge.** Nici măsurătoare
scriind în el, nici hook, nici config.

`lrc hooks disable` pe un repo străin e interzis de skill, și e corect:
un agent fără context într-un repo străin e exact defectul pe care îl
reparăm.
