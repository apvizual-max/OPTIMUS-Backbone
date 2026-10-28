---
name: mavis-optimus-ci-server-skill
description: Serverul Mavis-Optimus-CI - containerul Docker care tine toata data git locala a proiectului Optimus CI, o sincronizeaza cu GitHub si impinge doar cu acordul lui Popy. Foloseste-l cand trebuie sincronizat, verificat sau impins ceva in MAVIS-CLOUD / MAVIS-OPTIMUS-CI, sau cand sistemul trebuie repus in vi after a year.
role: functional
bot: mavis-local-optimus-ci-bot
---

# MAVIS — SERVERUL OPTIMUS CI (Mavis-Optimus-CI)

## 1. Ce e, in trei randuri

Un container Docker (`Mavis-Optimus-CI`) care detine **toata** data git locala a
proiectului Optimus CI si o sincronizeaza cu GitHub. Localul e autonom: fetch,
integrare, commit, mereu pe `main`. **Push-ul cere acordul lui Popy** si nimic
altceva.

Proiectul are **doua** repo-uri pe GitHub, ambele publice:
`apvizual-max/MAVIS-OPTIMUS-CI` (sistemul) si `apvizual-max/MAVIS-CLOUD`
(instanta Cloud). Plus `apvizual-max/Optimus-Mavis-Skills` (skillurile).

## 2. REGULA DE AUR (motiva pentru care exista serverul)

Mai multi agenti lucreaza simultan pe aceleasi repo-uri: Mavis Cloud, Jules prin
CD, Antigravity. Daca fiecare impinge cand vrea, istoricul se rupe.

1. **Pre-flight.** GitHub trebuie sa fie **curat si unitar**: exact o ramura
   (`main`), **zero** pull request-uri deschise.
2. Daca **nu** e asa, motorul **nu face nimic** si raporteaza `BLOCKED` cu
   motivele exacte. Nu se curata nimic in ascuns, nu se taie nimic.
3. Daca e curat, procesul merge: sync local (autonom) apoi push (cu R0).

## 3. Unde stau lucrurile

| Ce | Unde |
|---|---|
| Proiectul (tot) | `E:\Google\GDrive\...\Optimus_CI (by Mavis)` → container: `/workspace/project` |
| Data git (tot) | `E:\Google\GitData-Optimus-CI` → container: `/workspace/gitdata` |
| Poarta de push (comuna cu CD) | `C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\scripts\git-hooks` → `/workspace/gate` (read-only) |
| Token GitHub | `E:\--- System Secrets\github-token-apvizual-max.txt` → `/secrets/` (read-only) |
| Evidenta | `E:\Google\GitData-Optimus-CI\evidence\ci-ledger.{jsonl,log}` |
| API locala | `http://127.0.0.1:8790` (doar loopback) |

## 4. Cum se opereaza (pluginul `optimus-ci-server`)

| Unealta | Ce face | Cand |
|---|---|---|
| `ci_status` | HEAD local vs server, dirty, divergenta, ramuri | oricand, inainte de orice |
| `ci_plan` | pre-flight: `READY` sau `BLOCKED` cu motive | **inainte** de sync si push |
| `ci_sync` | sincronizare autonoma locala | cand planul e `READY` |
| `ci_arm_push` | armeaza acordul R0 (marker `PUSH-ACORD`) | **doar** la cererea explicita a lui Popy |
| `ci_push` | impingere; refuza fara R0 | dupa `ci_arm_push` |
| `ci_doctor` | diagnostic complet: monturi, token, poarta, grant Google | dupa o pana, sau peste un an |
| `ci_evidence` | jurnalul de evenimente | cand trebuie predat altui AI |

## 5. Cum se reincepe sistemul (5 minute, dupa un an)

```powershell
# 1. porneste serverul (construiește imaginea daca nu exista,Monteaza, verifica)
powershell -NoProfile -ExecutionPolicy Bypass -File "<CI>\ci-server\bootstrap.ps1"

# 2. vezi diagnosticul
docker exec Mavis-Optimus-CI node /opt/optimus-ci/engine/cli.mjs doctor
```

Re-autentificarea e **rare**: tokenul GitHub e refacut automat din `gh auth`
(daca lipseste, `bootstrap.ps1` il creeaza), iar grantul Google se verifica din
`consent-result.json`. Consentul se cere **numai** daca nu exista niciun grant
viu — nu pentru că s-a sters un magazin de credentiale.

## 6. Disciplina R0 (regula lui Popy)

- **Local git e complet autonom.** Fetch, integrare, commit: fara cerere.
- **Push spre GitHub cere R0 explicit.** Se da prin `ci_arm_push` sau prin
  poarta sanitizata de pe host (`scripts\git-autopush.ps1 -Acord`).
- Un acord = o impingere: markerul `PUSH-ACORD` e consumat de poarta comuna.
- **Nu se sterg** ramuri, commituri sau fiere. Ramurile locale ale altor agenti
  se **integreaza** in `main`; stergerea e distructiva si cere R0.
- **CD e alt proiect.** Nu se atinge nimic din `Optimus_CD (by Jules)` si nu se
  discuta CD aici fara motiv empiric absolut.

## 7. Portile (scriptele .ps1) ruleaza si in container

Cele 7 porti ale proiectului (`scripts\*-selfcheck.ps1`) ruleaza cu PowerShell 7
in container, pe aceeasi logica ca pe host — **o implementare, doua medii**.
Hook-urile sunt versionate in `ci-server/hooks/` si se instaleaza singure la
pornirea containerului.

## 8. Grupul de skilluri (Optimization CI)

- `mavis-optimus-ci-server-skill` — **serverul** (acest skill)
- `mavis-optimus-continuous-integration-skill` — scopul proiectului si doctrinele
- `mavis-cloud-bridge-skill` — canalele Local <-> Cloud
- `mavis-google-access-skill` — accesul Google permanent (grantul viu)

## 9. Ce NU e acoperit aici

- CD / PKMS: proiecte surori, frontiera lor. Nu se ating.
- LiveReview: evaluarea cu cheie proprie (BYOK) e in fluxul CD, nu aici.
- Starea pe Google Drive: o dauneaza bridge-ul (`mavis-cloud-bridge-skill`),
  nu serverul de git.
