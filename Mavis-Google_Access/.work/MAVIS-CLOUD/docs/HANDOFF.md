# Handoff — Mavis → MaxHermes

Două secțiuni: una pentru alt agent, una pentru om. Aceeași informație, formate
diferite, pentru cititori diferiți.

---

## A2A — pentru agent

**Ești MaxHermes și preiești un sistem deja funcțional. Nu îl reproiecta.**

### Stare inițială
Repo: `apvizual-max/MAVIS-CLOUD`, totul pe `main`, nimic necomandat.
27 de skill-uri în `/workspace/.skills/`, plus 14 în `Mavis/vendor/`.

### Contractul
1. **Nu rescrie `scoring.gs`, `cv-mutator.js`, `letter-engine.js`.** Funcționează.
   Amendează, nu rescrie.
2. **Noul output se construiește GENERIC.** Orice șablon nou e o familie, nu o firmă.
3. **Niciun număr în `PROGRES.md` fără numărare reală.** `resultSizeEstimate` nu e
   numărătoare.
4. **Niciodată ștergere definitivă.** Trash da.
5. **Niciodată trimitere în numele lui POPY.** Pregătești, el apasă.
6. **Niciun nume de client care nu vine din materialul lui.** „Smite" e corect —
   am greșit eu o dată, s-a reparat.

### Ce e deja rezolvat, nu atinge
- Numarare Gmail prin paginare
- Sortare pe etichete, cu skip
- Reparare clasificări (`gmail-label-correction`)
- 9 șabloane CV
- Schelet de site cu strat de date
- Workflow de verificare pe GitHub

### Ce e în lucru
- Site-uri de nivel 1: 1 din 9 făcut (`graphic-designer`)
- CV-uri Word: 6 făcute, dar cu date particulare — **de regenerat din șabloane**

### Ce e neblocat
- 3 etichete Gmail goale, fără regulă
- 3.000+ thread-uri neatinse în inbox
- Copilot/Jules: indisponibile pe plan free

### Ordine
1. 7 JSON-uri de site → `build.py`
2. CV-uri Word din șabloane
3. Regula pentru `Actiune - de respuns`
4. NotebookLM
5. LinkedIn
6. Nivelul 2 (B2B)
7. Nivelul 3 (AP-ID Systems)
8. MaxClaw, dacă apare o nevoie reală de al doilea agent

### Verificare înainte de orice commit
```bash
node --check ALEX-KIT/cv-mutator.js
python3 SITE/build.py graphic-designer
git diff --cached --name-only | grep -iE "secret|token|credential"   # trebuie gol
```

---

## A2U — pentru om (POPY)

**Repo-ul e pe GitHub, la `github.com/apvizual-max/MAVIS-CLOUD`. Merge singur.** POPY
nu trebuie să știe git ca să-l folosească — și nici să-l folosească.

### Ce poți deschide acum, în browser
`SITE/dist/graphic-designer.index.html` — site-ul. Deschide fișierul, merge pe
`main`, vezi ce am făcut. Se schimbă cu `python3 SITE/build.py graphic-designer`.

### Ce se întâmplă singur
- **Cron 08:00** — raport zilnic, joburi noi cu scor, scris pe Drive
- **GitHub Actions** — verifică la fiecare push că nu s-a strecurat un secret,
  că JSON-urile sunt valide, că JavaScript-ul e corect, că site-ul se construiește
  și că șabloanele nu conțin nume de firmă

### Ce ai de completat, e doar în `PROGRES.md`
Nu ai de ținut minte nimic. Tot ce nu e gata e acolo, marcat.

### Ce am nevoie de la tine
- **Scriptul „Mavis Apple Design"** — ai zis că vine dintr-un link, nu l-am primit.
  Am preluat întreg repo-ul `emilkowalski/skills` (14 skill-uri) din acel moment.
- **Confirmare pe Copilot/Jules** — contul e pe plan free, nu le pot activa eu.
  Intră pe github.com/settings și vezi ce ai.

### Ce nu merge încă, spus direct
- 3 etichete Gmail sunt goale. Una din cauza filtrului, două pentru că nu au
  regulă. **Astea mă împiedică să-ți spun "e tot prins".**
- 3.000+ mailuri sunt încă în inbox, neatinse. Sortarea a acoperit doar 1–3 ani.
