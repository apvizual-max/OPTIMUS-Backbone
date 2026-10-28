# GMAIL — catalogul complet

> Un singur folder pentru tot ce ține de Gmail. Ca să știm ce am făcut,
> când, și de ce — separat de restul proiectului.

---

## 1. Ce am făcut, în ordine

| Data | Ce | Rezultat |
|---|---|---|
| 09 iul | Conectare Gmail, teste de capacități | ✅ funcționează |
| 09 iul | 8 etichete `MAVIS/*` create | ✅ |
| 09 iul | 5 filtre server-side | ✅ prind mailul nou fără cereri API |
| 09 iul | Reciclare 5+ ani → Trash | POPY a golit manual, confirmat `in:trash` = 0 |
| 09 iul | Sortare fereastra 1–3 ani | 14.146 mesaje pe 8 etichete |
| 10 iul | **6 minciuni de numărătoare reparate** | vezi secțiunea 3 |
| 11 iul | Redenumire etichetă cu liniuță | `MAVIS/Actiune - de raspuns` → `MAVIS/De raspuns` |
| 12 iul | Spam → inbox, flaguri scoase | 106 mesaje |
| 12 iul | **Sortare completă, fără fereastră de vârstă** | tot inbox-ul |
| 27 oct | **Rearanjare taxonomie** — 7 din 8 etichete `MAVIS/*` redenumite (prefixul căzut), 4 hierarhii noi: `WORK \| AP-ID/`, `Knowledge/`, `Crypto \| Trade \| News/`, `JOBS-Interview/` | ✅ filtre mutate împreună, 0 sparte |
| 27 oct | **Verificare filtre** — 19 filtre, toate țintele valide | ✅ 0 sparte |
| 27 oct | **Δ cont** — 84.316 → 83.505 mesaje (−811), Trash 626, Spam 2 | ⏳ de confirmat cu POPY |

## 1b. Numere LIVE, contorizate la sortarea completă

```
MAVIS/Joburi               8.062
MAVIS/Newsletter           4.103
MAVIS/Social               2.818
MAVIS/AI si comunitati     2.398
MAVIS/De raspuns           1.345
MAVIS/Facturi si conturi      97
MAVIS/Personal               176
MAVIS/Finante                 71
GUNOI                         0
SPAM                           0
                              ─────
                       19.070 total etichetat
```

**Crește pe măsură ce sortarea completă rulează** — fereastra de vârstă a fost
eliminată, deci ia tot ce a rămas în inbox, indiferent de vârstă.

**Atenție la măsurare:** nu număra în timp ce sortarea rulează. Cererile se
ciocnesc, cota se atinge, `threads.list` întoarce gol și **raportă 0 cînd
de fapt sunt mii.** Verificat: am măsurat 0 în mijlocul sortării, și 18.731
după. **Zero în timpul unei operații înseamnă „n-am putut măsura", nu
„nu există".**

## 2. Etichetele finale

```
MAVIS/Joburi               joburi, de pe toate portalurile
MAVIS/AI si comunitati    newsletter-e, comunități, tot ce e AI
MAVIS/Social              rețele sociale, reclame sociale
MAVIS/Newsletter          buletine, oferte, digest-uri
MAVIS/Finante             bănci, exchange, facturi
MAVIS/Personal            corespondență personală reală
MAVIS/De raspuns           ⭐ cu stea sau important+necitit — cere atenție
MAVIS/Facturi si conturi  facturi și conturi
```

## 3. Cele șase capcane — de ce au existat

**Toate au fost erori ale mele, nu ale contului lui POPY.**

| # | Capcană | Simptom | Cauză reală | Repar |
|---|---|---|---|---|
| 1 | `resultSizeEstimate` | raportam 201 pentru orice | **plafonat**, nu e numărătoare | numărare prin paginare |
| 2 | `.replace(' ','')` | 3 etichete raportate ca 0 | ștergea **doar primul** spațiu | ghilimele în interogare |
| 3 | liniuță în nume | etichetă invizibilă | Gmail citește `-` ca operator NOT | redenumit fără liniuță |
| 4 | ghilimele lipsă | 0 rezultate | spațiile rup interogarea | `label:"..."` mereu |
| 5 | `in:inbox` + `is:starred` | 0 rezultate | căutam ce eu mutasem din inbox | fără `in:inbox` pentru acțiuni |
| 6 | 4 condiții cu AND | 0 rezultate | prea restrictiv | `SAU` când e alternativă |

**Regula:** când o interogare întoarce 0, **întreabă de ce** — nu concluziona „e gol".

## 4. Fereastra de vârstă — de ce a stricat AI-ul

Am pus tot sistemul pe `older_than:1y newer_than:3y`. Corect pentru arhivă,
**catastrofal pentru newsletter-e** care vin zilnic:

```
AI fără fereastră : 201+   ← există
AI cu fereastră   : 0      ← totul e NOU
```

**Repar:** fereastra e per categorie. Categoriile zilnice nu au fereastră.

## 5. Costul și cotele

| Operație | Cost |
|---|---|
| `threads.list` | **5 unități** pe pagină de 500 |
| `messages.get` | **100 unități** fiecare |
| `messages.trash` | 20 unități |
| Cota | 6.000 unități/utilizator/minut |

**Deci:** număr și sortez prin `threads.list`, **nunca** prin `messages.get`.
Diferența la 3.000 de mesaje: 15.000 vs. 300.000 de unități.

## 6. Fișiere

| Fișier | Ce face |
|---|---|
| `mavis-tools/kit.js` | clientul Gmail, singurul punct de acces |
| `mavis-tools/quota.js` | cotă + backoff exponențial |
| `mavis-tools/email-count.js` | numărare exactă prin paginare |
| `mavis-tools/email-sort.js` | sortare pe categorii, cu skip |
| `mavis-tools/email-sort-full.js` | sortare completă, fără fereastră |
| `mavis-tools/fix-labels.js` | reclasificări |
| `docs/SENTINEL-LATEST.md` | numere contorizate |

## 7. Ce a rămas

- **Inbox-ul trebuie gol complet** ca să poată fi organizat dintr-un loc.
  Sortarea curentă procesează tot; verificăm după ce termină.
- **Reguli noi pentru etichete** — `AI si comunitati`, `De raspuns` și
  `Facturi si conturi` acum au reguli, dar nu am verificat câte prinde fiecare.

## 8. Ce nu se face niciodată

- **ștergere definitivă** — doar Trash
- **trimitere** — POPY apasă butonul
- **pornirea sortării de gunoi** după ce POPY l-a golit
- **raportarea unui număr** fără numărare reală

---

## 9. Taxonomia curentă (27 oct 2026)

Nu mai sunt 8 etichete `MAVIS/*` — sunt **36 etichete de utilizator** în 7
familii. Detalii complete, cu numere măsurate și cu corespondența
veche→nouă: **`10-GMAIL/TAXONOMIE-2026-10-27.md`**.

Familii: `MAVIS/Joburi` · `Newsletter` · `Socials` · `AI Folder/` ·
`De raspuns` · `Facturi si Conturi` · `Personal` · `Finante` ·
`WORK | AP-ID/` · `Knowledge/` · `Crypto | Trade | News/` ·
`Home | Car | Shopping/` · `JOBS-Interview/` · `Optimus CD` · `SCAMS`

**IMPORTANT pentru orice workflow nou:** citește etichetele noi, nu vechile
`MAVIS/*`. Doar `MAVIS/Joburi` a supraviețuit.

---

*Actualizat la fiecare schimbare reală. Numerele se numără, nu se estimează.*