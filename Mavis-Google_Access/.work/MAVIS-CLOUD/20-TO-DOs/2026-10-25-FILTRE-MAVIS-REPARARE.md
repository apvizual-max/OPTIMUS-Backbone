# 07 · Filtrele Gmail MAVIS/*: repararea pregătită, rulată de pe Local

**Data:** 2026-10-25 · **Tip:** acces + configurări · **Perspectivă lipsă:** acces (scope OAuth)
**Stare:** ⏳ așteaptă pe tine · **repararea e gata, doar scope-ul lipsește din cloud**

---

## De ce e aici

Etichetele `MAVIS/*` nu primesc **nimic** de 13 zile (ultima etichetare: **11.10.2026**).
Raportul zilnic din 24.10 zicea „filtrele au `addLabelIds` vid". Azi am măsurat
**cauza reală, care e mai profundă** — și pentru ea am nevoie de scope pe care
tokenul din cloud nu îl are.

## Context măsurat

Cele 5 filtre `MAVIS/*` există în Gmail și au criteriile scrise de mână. Testate
live pe API-ul de căutare, azi:

| Filtru | cum e scris acum | cum ar trebui scris (`{}`) |
|---|---|---|
| joburi | **0** | **1110** |
| ai si comunitati | **0** | **383** |
| social | **0** | **154** |
| newsletter | **0** | **1284** |
| finante | **0** | **36** |

**În căutarea Gmail, `()` = ȘI, `{}` = SAU.** Cele 5 filtre cer un expeditor care să
conțină *toate* cuvintele simultan (`from:(jooble bestjobs hipo indeed jobleads linkedin)`).
Deci **nu pot lovi niciun mesaj**, niciodată. Diferența dintre 0 și 2967 mesaje
în 30 de zile e exact golul din inbox-ul tău.

Al doilea defect, mai vechi: `action.addLabelIds` e **vid** pe toate cele 5.
Nici măcar cu criterii corecte n-ar eticheta ceva.

## Ce am încercat

1. `filters.list` + `labels.list` — citit starea reală (2 cereri).
2. Testat semantica Gmail pe API-ul de căutare: `from:(jooble bestjobs)` → **0**,
   `from:{jooble bestjobs}` → **18**, `from:jooble` → **14**. Confirmat.
3. Verificat scope-ul tokenului (`tokeninfo`): `gmail.modify`, `drive`, `calendar`,
   `documents`, `spreadsheets`, `presentations` — **fără `gmail.settings.basic`**.

## De ce nu pot singur

`filters PATCH` cere `gmail.settings.basic`. Fără el, API-ul răspunde **403
insufficient scopes** — și nu există o cale ocolitoare: singura cheie de client
funcțională e cea care a generat refresh token-ul, iar re-consimțământul se face
pe mașina ta (browser + cont Google).

## Ce am nevoie concret — un singur command, pe mașina ta

```bash
node mavis-tools/fix-mavis-filters.js --dry-run   # arată exact ce schimbă
node mavis-tools/fix-mavis-filters.js             # aplică
```

Scriptul:
- salvează starea curentă în `mavis-tools/filters-state-before-repair.json` → **rollback exact**;
- atinge **doar** cele 5 filtre MAVIS/*; celelalte 13 rămân neatinse;
- rescrie `from:(...)` → `from:{...}` și adaugă `addLabelIds` cu eticheta MAVIS/* corectă
  (rezolvată live din `labels.list`, nu hardcodată);
- **nu șterge nimic, nu trimite nimic**;
- are `--rollback` care readuce starea salvată.

## Ce fac eu după

- rulez sondele de măsurare peste filtre ca să confirm că prind mesaje;
- re-etichetez retroactiv mesajele din inbox care ar fi intrat în categorii
  (batchModify — scriere reversibilă, eticheta se poate scoate oricând);
- urmăresc dacă inbox-ul scade în 2-3 zile, ca să vedem că funcționează.

## Cum verificăm că s-a rezolvat

1. `node mavis-tools/report-filter-state.js` → filtrul de joburi trebuie să arate
   **0 acum / >0 cu acolade**, iar `withAddLabelIds` = **5**.
2. Mâine, raportul zilnic trebuie să arate `MAVIS/*` cu **mesaje noi azi > 0**
   (astăzi e 0).
3. Inbox-ul la 7 zile trebuie să scadă față de **770** (măsurat azi).

---

*2026-10-25 · Mavis Cloud · reparare pregătită și măsurată; rulează tu partea de scope*
