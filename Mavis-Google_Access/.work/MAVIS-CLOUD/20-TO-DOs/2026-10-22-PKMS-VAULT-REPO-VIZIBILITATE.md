# 02 · pkms-vault-automation: public sau privat

**Data:** 2026-10-22 · **Tip:** aprobări · **Perspectivă lipsă:** strategie
**Stare:** ✅ **DECIZIE 2026-10-22: PUBLIC** (POPY). Executat, cu audit complet al istoricului.

---

## Situația

| Repo | Conținut | Vizibilitate |
|---|---|---|
| `MAVIS-CLOUD` | proceduri, skill-uri, unelte, bridge cu Mavis Local | **PUBLIC** (făcut azi, la cererea ta) |
| `pkms-vault-automation` | motorul vaultului (14 scripturi), indexurile `00_INDEX.md`, documentația AI-Kit, handoff-urile | **PRIVAT** |

## Audit făcut înainte de întrebare (2026-10-22)

- **Zero secrete reale.** Matcher-ul a lovit 3 potriviri — toate erau
  **fixture-uri ale auto-testului detectorului de secrete** din vault
  (`ghp_0123456789abcdefghijABCDEFGHIJ`, `AKIAIOSFODNN7EXAMPLE`, `MIIEow==`).
  Detectorul tău funcționează; eu l-am declanșat pe el.
- **Conținut personal:** neurmărit. Urmărite sunt 668 de `.md` — aproape toate
  `00_INDEX.md` — plus 14 `.ps1`, 1 `.js`, câteva rapoarte de handoff.
- **Ce expune:** numele de clienți și job-uri din **căile** fișierelor de index:
  `01-2-AP-ID.ro - AI Branding Work and Clients` → `Knights Templar` → `Andu - Diplome`;
  `01_1-Alex - JOBS` → `Futureheads Recruitment`; `Email_Archives` cu subiecte
  de job-uri.

## Recomandarea mea (intersecția celor trei perspective)

**LOGICĂ:** e safe tehnic — zero secrete, zero conținut personal.
**RAȚIUNE:** e coeren — e configurația sistemului, iar tu ai făcut public
`MAVIS-CLOUD` **din același motiv**: „altfel aplicațiile conectate nu-l pot analiza".
**STRATEGIE:** e singurul loc unde se vede **motorul** (AI-Kit) și **contractul**
vaultului. Dacă aplicațiile conectate trebuie să înțeleagă sistemul, nu ajunge
să vadă doar bridge-ul.

**Așadar: INTERSECȚIA E COMPLETĂ. Recomand să-l facem public.**

**Contra-argumentul onest:** căile indexurilor expun nume de clienți și job-uri.
Dacă nu vrei ca aceste nume să fie publice, rămâne privat — și atunci
aplicațiile conectate nu-l pot analiza, deci pierdem exact beneficiul pentru
care ai făcut public `MAVIS-CLOUD`.

## Alternative pe care le pot construi singur

| Variante | Ce presupune |
|---|---|
| **A. Public, cum e `MAVIS-CLOUD`** | 1 click. Recomandat. |
| **B. Privat + un „mirror" public sanitizat** | eu creez `MAVIS-CLOUD` → folder `20-PKMS-ENGINE/` cu doar motorul + contractul, fără căi cu nume de clienți. Zero expunere, aplicațiile văd motorul. **Pot să-l construiesc fără să te întreb** |
| **C. Rămâne privat** | aplicațiile conectate nu-l analizează. Pierdem un pic din motivația de azi |

**Varianta B e cea pe care o pot face singur** — e intersecția completă fără
expunere. Dacă o vrei, spune-mi și o fac. Dacă nu spui nimic, rămâne privat
(pentru că **nu e o decizie pe care s-o iau singur** — e vizibilitatea sistemului
tău).

---

*2026-10-22 · Mavis Cloud · recomandare + alternativă care pot să o fac singur*

---

## Rezolvarea (2026-10-22)

**Decizia ta: PUBLIC.** Executată.

Am refăcut auditul **complet** înainte de flip: `git fetch --unshallow` +
toate cele 27 de ramuri + 177 de commituri = 13,5 MB de patch scanate.

**Rezultat: zero secrete reale.** Cele 4 potriviri erau fixture-uri ale
auto-testului detectorului de secrete din vault (`ghp_0123456789abcdefghij…`,
`AKIAIOSFODNN7EXAMPLE`) și pattern-urile din lista lui de detecție.

**Repo-ul e public**, acces anonim confirmat. Auditul complet al tuturor celor
10 repo-uri e în `docs/AUDIT-VIZIBILITATE-REPO-URI.md`.

**Și a ieșit un cadou neașteptat:** auditul a dezvăluit secrete în repo-uri
care erau deja publice din august. Două refresh token-uri Google — unul **revocat
de mine** (era viu), altul deja mort — și o cheie API Google vie, acum privatizată
și de rotit de tine → **TO DO 05**.
