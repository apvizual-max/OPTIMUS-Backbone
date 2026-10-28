# RĂSPUNS MAVIS CLOUD — 0844: etichetele se rezolvă live

**Data:** 2026-10-27 · **Ora:** 08:52 (Moscow) / 05:52 UTC
**TASK_ID:** `TASK-2026-10-27-0844-filtrele-gmail-reparate-5-din-5-script-reparat-la-sursa-oglindirea-marcajelor`
**Canal primar:** acest fișier · **Canal secundar:** `QUEUE/DONE/TASK-2026-10-27-0844-*.md`

---

## 1. Întrebarea ta — răspunsul scurt

**Raportul zilnic e curat. Dar în spatele lui, 6 scripturi erau rupte.**

Cele 4 scripturi din pipeline-ul zilnic folosesc **toate** `taxonomy.js`:
`report-build.js` · `report-mail-count.js` · `report-simulate-sort.js` · `report-filter-state.js`

**Zero nume de etichetă scrise cu mâna.** Cifrele **62 analizate / 33 păstrate** sunt sigure.

---

## 2. Defectul real — 6 scripturi, măsurat

| Script | Defect | Efect |
|---|---|---|
| `email-count.js` | `startsWith('MAVIS/')` | ar fi numărat **1 din 9** |
| `email-count-exact.js` | `startsWith('MAVIS/')` | idem |
| `report-drive-discover.js` | `startsWith('MAVIS/')` | idem |
| `report-inbox.js` | `startsWith('MAVIS/')` | idem |
| `email-sort.js` | 8 nume hardcodate | ar fi etichetat în etichete **inexistente** |
| `email-sort-full.js` | 8 nume hardcodate | idem |

### Măsurătoarea

```
taxonomy.js (metoda noua)  -> 9/9 rezolvate, 0 nerezolvate
  joburi     -> MAVIS/Joburi
  ai         -> AI Folder/AI si Comunitati
  social     -> Socials
  newsletter -> Newsletter
  finante    -> Finante
  personal   -> Personal
  actiune    -> De raspuns
  facturi    -> Facturi si Conturi
  agenti     -> Optimus CD

startsWith('MAVIS/') (metoda veche) -> 1
```

**1 vs 9.** Metoda veche ar fi raportat **7 din 8 categorii ca dispărute**, fără niciun semn — exact același tip de defect pe care l-am reparat la filtre.

`batch.js` și `backlog.js` au și ele numele vechi, dar **nu sunt în pipeline** — scripturi de setup, învechite.

---

## 3. Reparația — la sursă, ca la filtre

1. **Filtrarea după prefix → numele vii.** Se rezolvă din `taxonomy.js`, nu se mai caută un prefix mort.
2. **`email-sort.js` / `email-sort-full.js`:** tabelul `L` cu 8 nume hardcodate a devenit `rezolvaEtichete(liveLabels)`. Runtime.
3. **Nu se creează etichete inexistente.** Dacă o categorie n-a fost rezolvată, eticheta ei **nu se inventează** — categoria e sărită și raportată. Înainte, codul crea orice nume lipsă: ar fi creat **7 etichete noi, goale**, în plus.
4. `email-sort-full.js` păstrează fereastra deschisă (fără `older_than:1y`).

### Verificări

```
node --check  -> OK pe toate cele 6 fișiere
taxonomy.js   -> 9/9 rezolvate, 0 nerezolvate, live
```

**Nicio cerere Gmail în plus** — testul a fost un singur `labels.list`.

**Commit:** `930da7c` în `MAVIS-CLOUD`, împins.

---

## 4. Despre OAuth — nu mai e nimic de împus

Ai zis „da" la împingerea patch-ului. **Verificat: e deja acolo.**

```
d3f119f  fix(google-auth): never mix client and refresh-token from different OAuth clients
```

- Punct unic de rezolvare în `mavis-tools/google-auth.js` — clientul din fișierul de token câștigă; o pereche asamblată din surse diferite e **refuzată**, nu construită.
- `describe()` raportează acum `client_source`, `mixed_env`, `client_pairing`.
- `node mavis-tools/google-auth.test.js` → **8 tests, 8 pass, 0 fail**.

**Am și eu patchat local `kit.js` înainte să văd repo-ul** — patch-ul meu era o versiune mai proastă a aceluiași fix. **L-am aruncat și am tras `origin/main`**, unde versiunea corectă era deja. Nu am împushat nimic din ăla.

**Caveat de măsurat:** repo-ul meu local era la `95e3ef7` (13 oct) — **stale**. Am descoperit abia după ce am aplicat patch-ul. Am sincronizat înainte de orice altceva.

---

## 5. Coada e închisă

Toate cele 5 tichete de azi au livrabil în `QUEUE/DONE/` și sunt marcate `[x]`:

| TASK_ID | Livrabil |
|---|---|
| `0005` | `QUEUE/DONE/TASK-2026-10-27-0005-*.md` + Drive `0849` |
| `0103` | `QUEUE/DONE/TASK-2026-10-27-0103-*.md` + Drive `0849` |
| `0735` | `QUEUE/DONE/TASK-2026-10-27-0735-*.md` + Drive `0849` |
| `0815` | `QUEUE/DONE/TASK-2026-10-27-0815-*.md` + Drive `0812` |
| `0844` | `QUEUE/DONE/TASK-2026-10-27-0844-*.md` + **acest fișier** |

`0103` era singura nemarcată. Am livrat-o și am marcat-o — cerea o livrare proprie, și era singura gaură.

**Arhivare + marcaj, nu amputare.** Secțiunile rămân în canalul primar; mutarea în `ISTORIC/` e sarcina ta.

---

## 6. Ce NU am făcut

- ❌ Nu am modificat etichete, filtre sau mesaje în Gmail
- ❌ Nu am suprascris nimic din `BRIDGE-DRIVE/`
- ❌ Nu am mutat nimic în `ISTORIC/`
- ❌ Nu am deschis issue-uri, PR-uri, nu am făcut merge
- ❌ Nu am atins `MAVIS-OPTIMUS-CI`

---

*2026-10-27 08:52 Moscow · Mavis Cloud · canal primar Drive + canal secundar GitHub · `main` @ `930da7c`*
