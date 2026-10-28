# RAPORT DE STARE — JULES

**Data:** 12 iulie 2026 · **Stare:** 🟡 PAUZĂ — funcțional parțial

---

## 1. Ce e gata

| Element | Stare | Dovadă |
|---|---|---|
| Jules conectat la repo | ✅ | `apvizual-max/MAVIS-CLOUD` apare în lista lui de codebases |
| Setup script | ✅ | rulat cu succes, log complet în captura lui POPY |
| Knowledge → Memory | ✅ | POPY a confirmat |
| Environment variables | ✅ | POPY a confirmat, corecte |
| Network access | ✅ | pornit |
| Suggestions BETA | ✅ | arată deja 30+ de sugestii reale |

## 2. Ce NU e gata

| Ce | De ce | Cine |
|---|---|---|
| Trigger pe PR | nu s-a creat niciun PR | POPY sau Cloud |
| API apelată de Cloud | cheia e în secrets, nu s-a testat | Cloud |
| Memorie despre proiect | scriptul trece, dar nu știe despre ce discutăm | — |
| Memorie cu reguli | nu conține cele 8 reguli care nu se încalcă | POPY |

## 3. Ce a descoperit Jules — și e corect

Asta e cel mai important din tot folderul:

```
Blocking Async I/O in Loop          ← apelurile sequențiale în for-uri
Sequential API Calls in Loop        ← același tip, în email-sort
Missing Escaping/Sanitization in cv-mutator.js
Add tests for buildHeader / buildSummary / cleanTitle / detectStress /
            buildExpertise / buildAchievements / buildLetter / pickLinks
Unused Import: WD_ALIGN_PARAGRAPH
```

**Avea dreptate.** Nu am un singur test automat. Am verificat manual, cu
`node -e` și cu randare în browser. De aceea workflow-ul meu a prins o sintaxă
stricată **după** ce am comis, nu înainte.

**Concluzia strategică:** integrarea cu Jules nu e să-l atașez, ci să-l fac să
prindă ce eu uit.

## 4. Rolul lui Jules în sistem

> **Nu la fiecare virgulă.** Jules este **auditor de cod de nivel de sistem.**
> Cota lui: **100 de apeluri/zi** (Google AI Pro). Noi nu facem 100 de acțiuni/zi.

**Când se apelează:**
- refactorizare mare
- audit de arhitectură
- stabilizarea unui modul complet

**Când NU se apelează:**
- verificări de sintaxă (face workflow-ul)
- fiecare push
- curățenie de detaliu

## 5. Cum comunică cu el

**Doar prin GitHub.** POPY a stabilit asta:

| Cine | Push |
|---|---|
| **Mavis Cloud** | `git push origin main` — **automat, fără R0** |
| **Mavis Local** | `git push` — **BLOCAT de poarta R0**, doar la comandă scrisă |

Jules privește ce e pe GitHub. Cloud împinge imediat, deci **Jules vede
permanent** ce fac. Local trebuie să ceară R0 — și atunci Jules vede.

**Deci Jules funcționează cu amândoi, dar Local are un prag înainte.**

## 6. Configurația în Environment — setup script

E în `docs/JULES-SETUP-SCRIPT.sh`. **E corect și a rulat.**

Eroarea pe care o dădusem inițial:
```
E: Could not open lock file /var/lib/apt/lists/lock - Permission denied
```
**Cauza:** Jules rulează ca utilizator normal, **nu ca root**. `apt-get` are
nevoie de `sudo`, iar `set -e` oprea restul la prima eroare.

Rezultatul curent: `jules` drept utilizator, git 2.55, node v22.22.1,
npm 11.11.0, python 3.12.13, repo clonat, 7 documente în `docs/`.

## 7. Următorii pași

| # | Pas | Cine | Stare |
|---|---|---|---|
| 1 | Setup script | POPY | ✅ gata |
| 2 | Memory | POPY | ✅ gata |
| 3 | Variabile | POPY | ✅ gata |
| 4 | **Memory cu regulile proiectului** | POPY | ⬜ neintrodus |
| 5 | **Primul PR → Jules vede un modul complet** | POPY | ⬜ |
| 6 | **Cererea de teste** | Jules | ⬜ |
| 7 | Workflow cu teste | Cloud | ⬜ amânat |

## 8. Textul pentru Memory — de pus de POPY

```
MAVIS-CLOUD lucrează pentru Alexandru Popescu (POPY), designer și art director,
București. 20+ ani graphic design, 15 art direction, 4 ani AI.
Email apvisual.arond@gmail.com, telefon +40722121752.

Structura: ALEX-KIT/ (motor CV: scoring.gs, cv-mutator.js, letter-engine.js,
9 șabloane generice), mavis-tools/ (instrumente Google), SITE/ (site CV din JSON),
vendor/ (14 skill-uri de la emilkowalski/skills), docs/ (documentație).

REGULI CARE NU SE ÎNCALCĂ NICIODATĂ:
- niciodată ștergere definitivă, doar Trash
- niciodată trimitere în numele lui POPY
- niciun număr fără numărare reală (resultSizeEstimate din Gmail e plafonat)
- niciun nume de client care nu vine din materialul lui
- șabloanele sunt generice, niciodată cu nume de firmă
- main, fără ramuri, dacă POPY nu cere altfel
- "e gata" înseamnă "POPY poate vedea", nu "există în repo"
```

## 9. Semnalul

```
[PREDARE_TEHNICA::DOVEZI_STAGED::READY_FOR_JUDGE_REVIEW]
```

**Pașii 4 și 5 sunt singurele care lipsesc.** Restul e gata.