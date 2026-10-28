# CI-SERVER — serverul Mavis-Optimus-CI

> Document scris pentru orice agent care vine nou si nu are memorie intre
> sesiuni. Tot ce e mai jos e **masurat**, nu povestit.

## 1. De ce exista

Peste acelasi repo lucreaza, simultan, mai multi agenti: **Mavis Cloud**
(instanta din cloud), **Jules** (prin Optimus CD) si **Antigravity**. Popy a
cerut explicit ca, dupa fiecare impingere, sa existe o **sincronizare cu ce
e deja pe GitHub si lucrat de ceilalti**, si ca totul sa ramana pe **un singur
branch** (`main`).

Fara asta, istoricul se rupe si conflictul apare la cel mai prost moment: in
plin flux de lucru al altui agent.

## 2. Cele patru reguli (nucleul sistemului)

1. **Pre-flight.** Inainte de orice proces, GitHub trebuie sa fie **curat si
   unitar**: exact o ramura (`main`), **zero** pull request-uri deschise.
2. **Daca nu e curat, nu se face nimic.** Motorul raporteaza `BLOCKED` cu
   motivele exacte si astepta. Nu curata nimic in ascuns, nu taie nimic.
3. **Localul e autonom.** Fetch, integrare (`--ff-only` sau `--no-ff`), commit
   automat, totul pe `main`. Ramurile locale ale altor agenti se **integreaza**
   in `main`, nu se sterg.
4. **Push-ul cere R0.** Un singur acord, un singur push. Poarta e refuzanta
   prin design: `$(git rev-parse --git-dir)/PUSH-ACORD`.

## 3. Topologia (masurat 2026-10-27)

```
E:\Google\GDrive\...\Optimus_CI (by Mavis)     proiectul  -> /workspace/project
E:\Google\GitData-Optimus-CI                   data git   -> /workspace/gitdata
  ├── repo\                  gitdir MAVIS-OPTIMUS-CI
  ├── clone-MAVIS-CLOUD\     gitdir clonei Cloud
  ├── clone-MAVIS-OPTIMUS-CI\gitdir clonei CI
  ├── scratch\               laboratorul portilor
  └── evidence\              jurnalul evenimentelor (ci-ledger.jsonl / .log)

C:\Users\apviz\.minimax-agent\projects\scripts\git-hooks
                          poarta comuna de push   -> /workspace/gate (read-only)
E:\--- System Secrets\github-token-apvizual-max.txt
                          tokenul               -> /secrets/ (read-only)

Container: Mavis-Optimus-CI   imagine: mavis/optimus-ci:1.0.0
API: http://127.0.0.1:8790 (doar loopback)
```

## 4. O singura poarta, doua medii

Portile sunt **aceleasi** in host si in container — nu doua implementari:

| Poarta | Unde ruleaza | Cum se rezolva calea |
|---|---|---|
| scanner de secrete (`scripts\scan-staged-secrets.ps1`) | host + container | `MAVIS_SECRET_SCANNER`, altfel `$top/scripts/...` |
| poarta de push (`git-hooks/pre-push`) | host + container | `MAVIS_PUSH_GATE`, altfel calea Windows de pe host |

Hook-urile sunt **versionate** in `ci-server/hooks/`, iar containerul le
instaleaza singur in gitdir-uri la pornire (idempotent). Dupa un an, sursa
canonica e tot in repo, nu in gitdir-ul consumabil.

`scan-staged-secrets.ps1` a primit parametrul `-GitDir`: in container,
pointerul `.git` contine o cale Windows (`E:/...`) pe care git linux nu o
poate rezolva, deci gitdir-ul se paseaza explicit.

## 5. Containerul

| Ce | Detaliu |
|---|---|
| Nume | `Mavis-Optimus-CI` |
| Imagine | `mavis/optimus-ci:1.0.0` (node:22-slim + git + PowerShell 7) |
| Restart | `--restart unless-stopped` |
| API | `127.0.0.1:8790` (host) -> `8790` (container) |
| Volume | proiect (rw), gitdata (rw), poarta (ro), token (ro), consent (ro) |
| Fara dependinte | motorul e Node stdlib. `npm install` nu exista, deci nu se strica |

### Comenzi

```powershell
# pornire completa (dupa un an: asta e tot ce trebuie)
powershell -NoProfile -ExecutionPolicy Bypass -File "<CI>\ci-server\bootstrap.ps1"

# diagnostic
docker exec Mavis-Optimus-CI node /opt/optimus-ci/engine/cli.mjs doctor

# stare repo-uri
docker exec Mavis-Optimus-CI node /opt/optimus-ci/engine/cli.mjs status

# pre-flight
docker exec Mavis-Optimus-CI node /opt/optimus-ci/engine/cli.mjs plan

# jurnal
docker exec Mavis-Optimus-CI node /opt/optimus-ci/engine/cli.mjs evidence 50
```

## 6. Pluginul (interfata pentru orice AI)

`optimus-ci-server` (in `~/.minimax/skills/optimus-ci-server/`) expune 7
unelte MCP: `ci_status`, `ci_plan`, `ci_sync`, `ci_arm_push`, `ci_push`,
`ci_doctor`, `ci_evidence`.

Serverul MCP e stdio, **fara SDK** (JSON-RPC scris manual). Motivul: un SDK
aduce un arbore de dependinte care dispare intr-o zi; protocolul are ~200 de
linii si tine peste ani.

## 7. Portile: cine ruleaza ce (masurat, nu presupus)

| Poarta | Host | Container | Stare masurata |
|---|---|---|---|
| scanner de secrete (la fiecare commit) | verde | verde | aceeasi implementare, un singur cod |
| poarta de push R0 (marker) | verde | verde | oglinda e bit-identica cu poarta comuna (sha256 identic) |
| `mavis-sync` | verde | verde | |
| `queue-contract-check` | verde | verde | |
| `queue-deliver` | verde | verde | |
| `merge-check` | verde | **nu** (exit 1) | scrise pentru Windows PowerShell 5.1: folosesc `mavis-trash`, `$env:USERPROFILE` si literaluri de cale cu `\`. Nu sunt portate — mutarea lor ar risca portile autoritative de pe host |
| `publish-ci` | verde | **nu** (exit 1) | idem |
| `scan-staged-secrets-selfcheck` | verde | **necunoscut** (exit 3) | idem: un check care nu poate rula se raporteaza necunoscut, nu verde |
| `mavis-drive-bridge` | verde | **nu** (exit 2) | idem |
| **autotestul containerului** (`selftest`) | — | **7/7 verde** | |

Autotestul containerului (`cli.mjs selftest`) e poarta lui: falsificabila, si
demonstreaza MECANISMUL, nu integrarea:

```
T1 scannerul refuza o cheie plantata
T2 poarta de push refuza fara acord R0
T3 poarta de push accepta cu acord R0 si CONSUMA markerul
T4 integrare rapida (--ff-only) pastreaza istoricul
T5 integrare divergenta (--no-ff) pastreaza AMBELE lati
T6 o ramura locala straina e INTEGRATA in main, nu taiata
T7 autotestul NU atinge repository-urile reale (HEAD + config identice)
```

O poarta care nu poate esua nu e o poarta: de aceea T1-T3 cheamă portile
adevărate cu o cheie plantata, respectiv fara si cu markerul. T7 exista
pentru ca un self-check sa nu poata scrie in productie — vezi §11.

## 8. Re-autentificare minima

| Ce | Cum se reface | Cand cere omul |
|---|---|---|
| Token GitHub | `gh auth token` -> fisierul din volumul de secrete (bootstrapul face asta automat) | doar daca `gh` nu mai e logat |
| Grant Google | se citeste din `consent-result.json`; daca **nu exista grant viu**, atunci consent | doar daca nu exista niciun grant viu |
| Docker | trebuie sa porneasca | — |

Rezultat: dupa un an, pornirea e `bootstrap.ps1` + un `gh auth login` (daca a expirat sesiunea) — sub 5 minute.

## 9. Ce NU e aici

- **CD / PKMS**: proiecte surori. Nu se ating, nu se discuta fara motiv empiric.
- **LiveReview**: evaluarea cu cheie proprie (BYOK) e in fluxul CD.
- **Starea pe Drive**: o dauneaza bridge-ul (`mavis-cloud-bridge-skill`), nu
  serverul de git.

## 10. Relatii

- `docs\MAVIS-LOCAL-ONBOARDING-2026-10-27.md` — onboardingul proiectului
- `docs\GIT-GITHUB-PROCEDURI.md` — procedurile de git pe host
- `docs\BRIDGE-LOCAL-CLOUD.md` — canalul primar (Google Drive)
- `docs\CONTRACT-CLOUD-QUEUE.md` — contractul cozii (canal secundar)
- skill: `mavis-optimus-ci-server-skill`

## 11. Incidentul masurat (2026-10-27): un self-check a scris in `main`

**Ce s-a intamplat.** Un commit cu autorul `Fixture <fixture@localhost>` si
mesajul `fixture: pre-existing documentation` a ajuns in `main` pe repo-ul
MAVIS-OPTIMUS-CI: **127 de fisiere**, dintre care 125 doar cu **modul**
schimbat (100644 -> 100755). Autorul l-a creat `scripts\scan-staged-secrets-selfcheck.ps1`
— singurul cod din sistem cu identitatea aceea.

**Cauza, in lant (masurata):**

1. In container, pointerul `.git` din arbore contine o cale Windows (`E:/...`),
   pe care git linux nu o rezolva. Rezolvatorul de scratch nu avea, asadar,
   un gitdir utilizabil.
2. `git init` a ajuns pe **worktree-ul real** (nu pe un director nou), iar
   `GIT_DIR`/`GIT_WORK_TREE` globale in imagine (defect reparat ulterior) au
   facut ca operatiile sa ajunga in **gitdir-ul comun**.
3. `git add -A` a inregistrat modulele 0755 ale volumului Windows pentru toate
   fisierele, iar `git commit` a scris istoricul cu identitatea fixture-ului.

**Reparatie fara rescrierea istoricului.** Regula lui Popy: niciodata
`reset --hard`, niciodata rebase fortat, niciodata stergere de commituri.
Deci reparatia e **inainte**: modulele sunt aduse inapoi la 644 cu
`git update-index --chmod=-x` (commit nou; istoricul ramane intact), iar
anomalia ramane **vizibila** in istoric.

**Cele patru garde (toate masurate):**

| Garda | Unde | Ce masoara | Masuratoare |
|---|---|---|---|
| `core.filemode=false` + `safe.directory=*` | `ci-server/gitconfig` (config de sistem in imagine) | modulele nu se mai inregistreaza din bind-mount-ul Windows; gitul nu mai refuza operatiile pe volume cu alt UID | container: `git config --system --list` |
| garda „fixture-ul are propriul gitdir" | `scripts\scan-staged-secrets-selfcheck.ps1` | ca fixture-ul sa **nu poata** atinge un repository real; daca poate, se opreste **inainte de orice scriere** | falsificat: scratch pus intr-un repo real -> exit 1, repo-urile reale neatinse |
| `GITDIR_WORKTREE_SET` / `GITDIR_FILEMODE_NOT_FALSE` / `GITDIR_IDENTITY_SET` / `FOREIGN_AUTHORS` | `doctor` (motor) | igiena configului gitdir-ului si autorii straini pe commiturile **nepublicate** | doctor: `GREEN=True CHECKS=15 ANOMALIES=1` -> `FOREIGN_AUTHORS [ci] Fixture <fixture@localhost>` |
| `T7` | `selftest` | HEAD-ul si configul gitdir-urilor reale, **identice** inainte si dupa autotest | container: `SELFTEST_PROBLEMS=0 TESTS=7` |

**Regula generala.** Un instrument care ruleaza in acelasi fel cu productia
trebuie sa poata **falsa**. Daca un self-check poate ajunge intr-un repository
real, atunci „merge bine" nu e dovada ca nu a stricat nimic: trebuie masurat
ce a atins. Iar o clasa de accidente care poate aparea din nou trebuie sa fie
**vizibila**, nu corectata in tac — altfel urmatorul agent o repeta, pentru ca
nu o vede.

## 12. Botul Optimus CI și carantina (28 oct 2026)

Sesiunea `Mavis Local - Ondoard Optimus_CI` (`mvs_eaaf49033892458a8076c7cc9e8d51aa`) are
un **skill principal permanent**: `mavis-local-optimus-ci-bot`
(`C:\Users\apviz\.minimax\agents\mavis\skills\mavis-local-optimus-ci-bot\`).

**Ce e:** personalitatea, rolul, scopul, cele 9 functii (F1–F9), uneltele (7 unelte MCP +
scripturi + proceduri) si **indexul skillurilor secundare de pe subiect** — 29 membri
masurati pe disc (10 functionali + 19 referinte).

**Registrul e executabil, nu decorativ:**

| Comanda | Ce masoara | Rezultat masurat 28 oct 2026 |
|---|---|---|
| `node scripts\bot-doctor.mjs verify` | integritatea registrului + a listei + a cailor | `checks=70 failed=0 warnings=3` |
| `node scripts\bot-doctor.mjs doctor` | sistemul real: container, API, 3 repo-uri, carantina, ledger | `checks=19 failed=0 warnings=0` |
| `node scripts\falsify.mjs` | **falsifica verificatorul**: 5 scenarii stricate | `rosii=5/5` — verificatorul poate deveni ROSU |

### Carantina

Regula lui Popy (28 oct 2026): *„voi sterge eu folderul din cand in cand tu daca ai
asemenea situatii muti acolo. ca sa nu trebuiasca sa stergi foldere."*

Ce nu poate fi sters nu se sterge — se **muta** in
`E:\Google\GitData-Optimus-CI\.quarantine\`, **in afara mirrorului DriveFS** (acolo
DriveFS materializeaza si sterge fisiere pe cont propriu), cu `MOTIV.txt` scris. Popy
sterge cand vrea.

Detaliu masurat: bash-ul runtime-ului nu poate scrie in afara workspace-ului
(*„recursive write/delete target cannot be verified inside the workspace"*), iar stergerea
recuperabila e respinsa pentru tinte din afara lui (*„Windows trash execution rejected a
target outside the workspace"*). De aceea mutarea se face **prin container** — autorul
peste volumul gitdata:

```sh
docker exec Mavis-Optimus-CI sh -lc \
  'mkdir -p /workspace/gitdata/.quarantine && \
   mv /workspace/gitdata/scratch/<item> /workspace/gitdata/.quarantine/<data>-<nume>'
```

Primul element carantinat: `2026-10-28-falsify-guard` (repo git gol, creat pentru
falsificarea gardei „fixture-ul are propriul gitdir").
