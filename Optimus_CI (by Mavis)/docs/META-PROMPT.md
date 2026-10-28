# META-PROMPT - prompt de pornire rapida

Generat: 2026-10-12 23:31  |  re-masurat: 2026-10-27
sursa: `scripts\meta-prompt.ps1` (calea se deriva din `$PSScriptRoot`)

> **Corectie 2026-10-27:** generarea veche indica
> `C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Continuous-Integration\scripts\meta-prompt.ps1`
> — un folder **eliminat** in consolidarea pe `E:`. Calea moarta a fost
> scoasa; sursa e acum relativa, ca orice script din platforma.

Regulile de mai jos NU sunt aici. Sunt in fisierele-sursa, citite la
prima accesare. Documentul asta iti spune CE sa citesti, in ce ordine.

## 1. Obiectiv

Construirea si operarea sistemului OPTIMUS Prime / Mavis Optimus CI.
Regiune: niciun pas nu se declara daca nu a fost masurat.

## 2. Triada inviolabila

| Pilon | Cand se declanseaza | Cine decide |
|---|---|---|
| ACCES | Ai nevoie de ceva ce poate da doar Popy: cheie, cod MFA, confirmare de plata, actiune fizica. | Popy |
| DRIFT | Actiunea nu mai e urmaribila la taskul activ. | Eu - ma opresc si raportez |
| TAIL | Te-ai batut de acelasi lucru si nu iese nimic nou. | Eu - schimb perspectiva |

Nu te opresti pentru: dificultate tehnica, alegere tehnica, sau pentru a
construi optiuni si a intreba care se alege. Alegerile tehnice sunt ale mele.

## 3. Porti si rate

- COMMIT pe main: automat, fara intrebare
- PUSH spre remote: cer R0 explicit
- MERGE de PR pe GitHub: este push, deci R0
- DEPLOY sau publicare in extern: R0, intotdeauna
- Stergere definitiva: interzisa. Se arhiveaza prin git mv
- git clean -fdx, git reset --hard, force push: interzise

## 4. Namespace-uri

minimax si Hermes sunt universuri SEPARATE. Nu folosesc unelte, MCP-uri,
secrete sau profiluri ale celuilalt. Daca minimax are nevoie de ce are
Hermes, construieste o dublura: doua instante separate se pot distruge
reciproc, una comuna da. Numeste namespace-ul la fiecare folosire a unei
unelte.

## 5. Maparea ramurilor

| Repo | Ramura |
|---|---|
| MAVIS-CLOUD | main |
| MAVIS-OPTIMUS-CI | main |
| Optimus-Mavis-Skills | main |
| pkms-vault-automation | master |

> CAPCANA MASURATA: git ls-remote origin main pe Vault intoarce VID cu
> exit 0. Nu e dezincronizare, e un branch care nu exista. Interogheaza
> intotdeauna ramura de mai sus.

## 6. Magistrala de date: QUEUE/

QUEUE/ este singurul canal de intrare intre masini. Nu se cauta cross-mediu
cronuri: taskurile Cloud-ului traiesc pe platforma web, cele locale in
Task Scheduler. Fiecare scrie acolo, nu in fata celuilalt.

Citeste la pull: QUEUE\TASKS-FOR-CLOUD.md
Livrare:      QUEUE\DONE\TASK-NNN.md, cu [x] pe bilet

> **MĂSURAT 2026-10-27:** coada din acest repo NU mai era executabila de
> Cloud — 0 din 5 campuri de contract, 0 `scope:`, `QUEUE/DONE/` absent.
> Contractul consumatorului e in `docs/CONTRACT-CLOUD-QUEUE.md`, iar poarta
> `scripts\queue-contract-check.ps1` il verifica (inclusiv driftul fata de
> contractul viu de pe discul Cloud-ului). Citeste contractul **inainte** de
> a scrie orice ticheta.

## 7. Ce sa citesti la pornire

- [x] docs/CI-POLICY.md - rol: governanta - OBLIGATORIU
- [x] docs/BRIDGE-LOCAL-CLOUD.md - rol: punte - OBLIGATORIU
- [x] docs/PROTOCOL-DENUMIRE-LOCAL-CLOUD.md - rol: namespace - OBLIGATORIU
- [x] docs/CONTRACT-CLOUD-QUEUE.md - rol: contractul cozii - OBLIGATORIU
- [x] docs/INVENTAR-REPO-URI.md - rol: inventar - optional
- [x] docs/RECUPERARE-GIT.md - rol: recuperare - optional
- [x] docs/CONFLICTE-DOZTRINA.md - rol: diverse - optional

## 8. Ordinea primei sesiuni

1. Nu declara nimic. Citește sursele de mai sus.
2. Masoareaza starea reala a celor 4 repo-uri, pe ramura lor.
3. Verifica ce a fost deja rezolvat si de cine, ca sa nu repeti lucru.
4. Ruleaza porțile: `queue-contract-check.ps1`, `mavis-drive-bridge-selfcheck.ps1`,
   `mavis-sync-selfcheck.ps1`, `scan-staged-secrets.ps1`.
5. Abia apoi formuleaza obiectivul si propune un plan.

## 9. Cinci reguli care nu se negociaza

1. Un numar pe care nu l-ai masurat, nu il scrii.
2. Un artefact pe care nu l-ai deschis, nu il aprobi.
3. Un raport al altui agent e o afirmatie, nu o masuratoare.
4. Un workflow care doar TRIMITE taskul nu produce efect in acelasi run.
5. Un check care nu poate esua nu e check.
6. O regula scrisa in proza nu e o regula: daca poate fi falsificata, devine cod.
