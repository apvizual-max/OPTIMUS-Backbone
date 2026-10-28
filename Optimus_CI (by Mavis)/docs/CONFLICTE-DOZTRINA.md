# CONFLICTE DE DOCTRINĂ — ce am găsit în MAVIS-CLOUD

> Citirea completă a repo-ului Cloud, 11.10.2026. Fiecare conflict e
> **măsurat**, cu citatul care îl dovedește, și cu hotărârea luată.

---

## C1 — `CI-NOTES.md` spune că Live Review are nevoie de ramură. Doctrina spune `main` only.

**Măsurat.** `docs/CI-NOTES.md` din MAVIS-CLOUD:

> „1. Modificarea se face pe **o ramură**, nu direct în `main`
> 2. Se face **push** pe ramură
> 3. Se deschide un **Pull Request** spre `main`
> **Fără pull request, reviewerul nu are ce vedea.**"

Doctrina aleasă: **`main` only, fără ramuri, fără cerere.**

**Aceste două nu pot fi adevărate în același timp.** Dacă ramurile sunt
interzise, nu există pull request, deci mecanismul descris în CI-NOTES nu
se declanșează niciodată.

**HOTĂRÂRE:** `CI-NOTES.md` e **stale și periculos** — induce un agent nou
într-o procedură pe care politica interzice. Nu se modifică repo-ul Cloud
(se citește doar), dar **nu îi dai lui Jules și nu îl copiem în CI-ul
nostru**. În Optimus CI, Live Review rulează pe `main`, prin workflow
programat, nu prin PR.

---

## C2 — „R0" înseamnă două lucruri diferite

**Măsurat.** În `.skills/mavis-cloud-git-auto-commit-r0-push/SKILL.md`:

> „**R0 este verificarea care are loc înainte de push.** Nu după."
> — apoi o listă de comenzi: `node --check`, build, `ast.parse`, secret scan.

Acolo, **R0 = verificare automată făcută de agent.**

În doctrina lui Popy, **R0 = acordul lui Popy, scris, înainte de push.**

Sunt două lucruri diferite cu același cuvânt. Un agent nou care citește
repo-ul Cloud și întâlnește „R0" va înțelege verificarea automată și va
crede că are voie să împingă fără Popy. **Exact accidentul pe care îl
plătim.**

**HOTĂRÂRE:** în Optimus CI, termenul e **doar** acordul lui Popy.
Verificarea automată înainte de push se numește **`VERIFICARE`**, niciodată
`R0`. Vocabularul e load-bearing: un cuvânt, două sensuri, un accident.

---

## C3 — pragul de commituri are patru valori în patru locuri

| Sursă | Prag |
|---|---|
| `git-autonom` (skills locale) | **25** |
| `docs/skill-mavis-cloud-git-auto-commit-r0-push` (Cloud) | **5**, niciodată după 15 |
| Propunerea Gemini | **50** |
| Popy, direct | **50** |

**HOTĂRÂRE: 50.** Și un singur număr, repetat, într-un singur loc — acesta.
Când un număr apare în patru locuri cu patru valori, nu e o poartă, e
nor. Exact boala „nu e niciodată același setup în două proiecte", dar
pătrunsă în interiorul sistemului.

---

## C4 — throttling-ul cu care vine Gemini **există deja**

**Măsurat.** `.github/workflows/verify.yml` din MAVIS-CLOUD:

```yaml
# PROTOCOL C3: Live Review NU ruleaza la fiecare push - arde cotele.
on:
  workflow_dispatch:
  schedule:
    - cron: '0 3 * * *'
```

**Identic** cu propunerea Gemini: fără `on: push`, `workflow_dispatch` plus
`cron` 03:00. Nu e o idee nouă — e **stare existentă**, măsurată acum.

Workflow-ul conține și 7 verificări reale: secret în commit, JSON-uri
valide, sintaxă JS, sintaxă Python, build-ul site-ului, șabloane
ne-generice, și puntea.

**STRATEGIE:** nu reinventăm. **Îl copiem și îl adaptăm** — workflow-ul
devine template-ul nostru, cu verificările extinse la proiectele OPTIMUS.
Aceasta e valoarea reală a lecturii repo-ului Cloud: nu teoria lui, ci
lucrurile lui care chiar merg.

---

## C5 — `BRIDGE.md` scrie că orice push nu cere aprobare

**Măsurat.** `docs/BRIDGE.md`, secțiunea „Autonomia maximă":

> **Ce nu are nevoie de aprobare:** ... orice commit pe `main` · **orice push**

Acolo e corect **pentru Cloud** (container volatil) și **fals pentru
Local** (poarta R0).

**HOTĂRÂRE:** în `BRIDGE-LOCAL-CLOUD.md` rescriem tabela: **Cloud** fără
R0, **Local cu R0**. Nu copiem tabelul original — îl corectăm.

---

## C6 — starea lui Jules e contradictorie în același repo

| Fișier | Ce spune |
|---|---|
| `docs/JULES-INSTRUMENTARE.md` §1 | Memories **gol**, Setup script **gol**, Env vars **gol** |
| `docs/RAPORT-DE-STARE.md` | toate trei **✅ făcute** |

Unul din ele e stale. Nu am acces la panoul Jules ca să verific care.

**HOTĂRÂRE:** se tratează ca **NECUNOSUT**, nu ca „făcut". Nu se raportează
verde până nu se măsoară în panoul Jules. **Un senzor mort care raportează
sănătate e mai prost decât unul lipsă.**

---

## C7 — puntea e specificată, nu construită

**Măsurat.** `BRIDGE.md` cere `~/mavis-sync.sh`. **Nu există.**
`RAPORT-DE-STARE.md` confirmă: „puntea e specificată, neimplementată".

Tot `BRIDGE.md` propune un `while true; do git pull; git push; sleep 300; done`
— un loop care ar împinge **fără poartă**, deci ar ocoli exact R0.

**HOTĂRÂRE:** scriptul nu se construiește ca e scris. Puntea se face prin
`git-autopush.ps1 -Acord`, care **are** poarta. O punte care ocolește
poarta nu e o punte, e o scurgere.

**STARE — 2026-10-24: hotărârea e aplicată.** Puntea rulează zilnic la
**08:30** prin `MavisSyncBridge` (`LastTaskResult=0`, `exit_pull=0`,
`local_dupa == remote`, `impingere=NEEXECUTATA`). Poarta de push e legată
**per repo** — `core.hooksPath` local + hook `pre-push` cu martor
`PUSH-ACORD`, globalul **gol** — și e probată **în ambele sensuri**. Vezi
`docs/GIT-GITHUB-PROCEDURI.md` și `docs/STARE-MASURATA-CI.md` §1.

---

## Rezumat — ce e adevărat din Cloud

| Luați | De ce |
|---|---|
| `verify.yml` | throttling deja implementat și real |
| `DEFINITIE-OPERATIONALA.md` | împărțirea de roluri, limpede |
| Handoff-ul și modelul de erori | util, direct |
| 33 de skill-uri | domeniu diferit (CV/joburi), nu CI |

| Nu luați | De ce |
|---|---|
| `CI-NOTES.md` | ramuri + PR — interzise de doctrină |
| „orice push fără aprobare" | fals pentru Local |
| `mavis-sync.sh` ca e scris | ar ocoli poarta R0 |
| Pragurile 5 / 15 / 25 | patru valori, un singur adevăr: 50 |
| Starea Jules ca „✅" | contradictorie cu documentul ei |
| Definiția lui R0 ca verificare | coliziune de termen cu R0-ul lui Popy |