# STATE-CLOUD — ce am înglobat din MAVIS-CLOUD

> Sursă: clonă locală în `cloud-ingest/MAVIS-CLOUD/`, citită complet.
> **155 de fișiere. Repo-ul Cloud nu a fost modificat** — se citește și se
> copiază, nu se atinge.

---

## Ce conține

| Folder | Ce |
|---|---|
| `ALEX-KIT/` | motorul de CV: `scoring.gs`, `cv-mutator.js`, `letter-engine.js`, 9 șabloane, 7 CV-uri Word |
| `mavis-tools/` | client Google, quota manager, numărare exactă, sortare, `sentinel.py`, `log.py` |
| `SITE/` | site de CV construit din JSON: `build-hub.py`, `build.py`, `build-dashboard.py` |
| `.skills/` | **33 de skill-uri** |
| `docs/` | 25 de documente, inclusiv handoff, bridge, Jules, LOG-SISTEM.json, TODO.json |
| `.github/workflows/verify.yml` | **workflow-ul de throttling, deja implementat** |
| `vendor/` | skill-uri de design importate |

---

## Ce am preluat

| | De ce |
|---|---|
| **`verify.yml`** | throttling-ul cu `cron 03:00` + `workflow_dispatch` există deja și e corect. Nu reinventăm. |
| **7 verificările din workflow** | secret-scan, JSON valid, sintaxă JS, sintaxă Python, build, reguli de business, puntea vie |
| **Modelul de erori al lui Cloud** | util, direct, măsurat — îl folosesc ca lecție, nu ca autoritate |
| **Definirea rolurilor Local/Cloud** | limpede, corectă, și e singura lui care **supraviețuiește** |

## Ce am respins

Vezi `CONFLICTE-DOZTRINA.md` — 7 conflicte, fiecare cu citatul și hotărârea.

Pe scurt: `CI-NOTES.md` (ramuri+PR, contrazice main-only) · „orice push
fără aprobare" (fals pentru Local) · `mavis-sync.sh` ca e scris (ocolеște
poarta) · pragurile 5/15/25 (patru valori) · starea Jules ca „✅"
(contradictorie) · definiția lui R0 ca verificare (coliziune de termen).

---

## Două lucruri care trebuie spuse cu voce tare

**1. `MAVIS-CLOUD` e PUBLIC.** Conține CV-uri cu numele de clienți, orașul,
emailul și telefonul lui Popy. **Privește-l și decide.** Nu decid eu — dar
spun cu numele, pentru că tăcerea aici ar fi exact felul de eroare pe care
doctrina îl interzice.

**2. Cloud are 24 de comituri și 33 de skill-uri, și spune singur, în
raportul lui:**

> „Puntea e specificată, neimplementată."

**Sincer peste tot.** E un agent care își notează eșecul în propriul
raport. Aceea e atitudinea pe care o propagăm în CI — și e motivul pentru
care nu îl înlocuim cu ceva „mai bun": **funcționează corect, doar că
nu suficient.**

---

## Dependențe confirmate

| Instrument | Stare |
|---|---|
| `git` | ✅ |
| `gh` | ✅ 2.97.0, autentificat ca `apvizual-max` |
| `node` | ✅ |
| `python3` | ✅ |
| `lrc` (LiveReview) | ✅ v0.6.15, plan `free_30k` |
| `Jules` | ⚠️ **NECUNOSUT** — vezi C6 |

---

## Moștenirea

Cloud a lăsat un handoff pentru un agent local nou. **Acesta e handoff-ul
acum.** L-am citit, l-am verificat contra măsurătorilor reale, și am
continuat de aici.

Copie locală: `cloud-ingest/MAVIS-CLOUD/` — neatinsă, pentru comparație.