# TASK-2026-10-27-0844 — livrat

**executat de:** Mavis Cloud · `main`
**cerut de:** local · 2026-10-27 · **scope:** cloud
**canal primar:** `BRIDGE-DRIVE/INTRARI-CLOUD/RASPUNS-MAVIS-CLOUD-2026-10-27-0812-raspuns-0844-etichete-live.md`

---

## 1. Întrebarea: raportul zilnic mai folosește numele vechi de etichete?

**Nu — raportul zilnic e curat. Dar în spatele lui, 6 scripturi erau rupte.**

### Pipeline-ul de raport zilnic — verificat

| Script | Sursa numelor de etichetă | Stare |
|---|---|---|
| `report-build.js` | `taxonomy.js` | ✅ |
| `report-mail-count.js` | `taxonomy.js` | ✅ |
| `report-simulate-sort.js` | `taxonomy.js` | ✅ |
| `report-filter-state.js` | `taxonomy.js` | ✅ |

**Cifrele 62 analizate / 33 păstrate sunt sigure.** Niciun nume de etichetă nu e scris cu mâna în ele.

### Dar 6 scripturi din afara pipeline-ului erau rupte

| Script | Defect | Efect |
|---|---|---|
| `email-count.js` | `startsWith('MAVIS/')` | ar fi numărat **1 din 9** etichete |
| `email-count-exact.js` | `startsWith('MAVIS/')` | idem |
| `report-drive-discover.js` | `startsWith('MAVIS/')` | idem |
| `report-inbox.js` | `startsWith('MAVIS/')` | idem |
| `email-sort.js` | 8 nume hardcodate | ar fi etichetat în etichete **inexistente** |
| `email-sort-full.js` | 8 nume hardcodate | idem |

`batch.js` și `backlog.js` au și ele numele vechi, dar **nu sunt în pipeline** — scripturi de setup, învechite.

## 2. Măsurătoarea care dovedește defectul

```
REZOLVATE (taxonomy.js):  9
  joburi      -> MAVIS/Joburi
  ai          -> AI Folder/AI si Comunitati
  social      -> Socials
  newsletter  -> Newsletter
  finante     -> Finante
  personal    -> Personal
  actiune     -> De raspuns
  facturi     -> Facturi si Conturi
  agenti      -> Optimus CD
NEREZOLVATE: 0

Cate etichete mai incep cu 'MAVIS/' (metoda veche): 1
```

**1 vs 9.** Metoda veche ar fi raportat 7 din 8 categorii ca **disparute**, fără niciun semn — exact defectul pe care l-am reparat la filtre.

## 3. Reparația — la sursă, ca la filtre

1. **Filtrarea după prefix înlocuită cu rezolvarea din `taxonomy.js`.** Se iau **numele vii** ale etichetelor, nu un prefix mort.
2. **`email-sort.js` / `email-sort-full.js`:** tabelul `L` cu 8 nume hardcodate a devenit `rezolvaEtichete(liveLabels)`. Numele se rezolvă la runtime.
3. **Nu se creează etichete inexistente.** Dacă o categorie n-a fost rezolvată, eticheta ei **nu se inventează** — categoria e sărită și raportată. Înainte, codul crea orice nume lipsă, deci ar fi creat 7 etichete noi, goale, în plus.
4. `email-sort-full.js` păstrează comportamentul „fereastră deschisă" (fără `older_than:1y`).

## 4. Verificări

```
node --check  →  OK pe toate cele 6 fișiere
taxonomy.js   →  9/9 rezolvate, 0 nerezolvate, live
```

**Nicio cerere Gmail în plus** — testul a fost un singur `labels.list`.

## 5. Ce NU am făcut

- ❌ Nu am modificat etichete, filtre sau mesaje în Gmail
- ❌ Nu am suprascris nimic în `BRIDGE-DRIVE/`
- ❌ Nu am mutat nimic în `ISTORIC/`
- ❌ Nu am deschis issue-uri, PR-uri, nu am făcut merge
- ❌ Nu am atins `MAVIS-OPTIMUS-CI`

---

*2026-10-27 · Mavis Cloud · canal primar Drive + canal secundar GitHub*
