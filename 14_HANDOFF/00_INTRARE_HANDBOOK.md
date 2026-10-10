# SENTINEL PRIME — handbook de intrare

**Citește asta primul.** E scris pentru un agent care nu are nimic: zero
context, zero memorie, zero conversație anterioară. Dacă ești acel agent, ai nevoie
de exact acest fișier și de nimic altceva ca să preiei proiectul.

Ultima actualizare: **2026-10-10**.

---

## 1. Ce este proiectul

**SENTINEL** e un sistem de operare pentru un operator uman — discuție, program și
auto-observare, ținute într-un singur arbore și afișate într-un centru de comandă
care se poate citi ca un panou de instalație.

Operatorul: **Popy** (Alexandru Popescu), designer și arhitect de sisteme. **Nu
programator.** Nu îi ceri decizii tehnice — nu le înțelege și nu e treaba lui. Nu îi
arăți un panou de aprobări. Nu îi ceri să apese ceva.

Când ceri ceva, spune-i ce s-a schimbat, în cuvinte simple, și continuă.

---

## 2. Două reguli care nu se negociazăază

### 2.1 COMMIT = treaba ta. PUSH = decizia lui.

- **Comiți singur**, imediat ce o măsurătoare confirmă ceva. Nu la final, ci pas
  cu pas. Dacă el a modificat ceva și nu e comitat, îl comiți și îi spui.
- Nu întrebi niciodată „vrei să comit?". **Changes trebuie să rămână gol.**
- Mesajul spune ce s-a schimbat în cuvinte simple, nu `chore: update x`.
- **Împingi numai când el spune.** Nici din inițiativă, nici prin butonul din
  interfață.

Protocolul complet e în skill-ul `mavis-git-autonom-skill`.

### 2.2 Zero fabricăție

Nu inventa: nume de unelte, căi, flag-uri, versiuni, prețuri, fapte. Dacă nu
poți verifica, spune „nu știu, iată cum aș verifica".

**Fiecare cifră pe care o raportezi e măsurată în sesiunea raportului** sau e
`NOT_MEASURED`. Un raport cu cifre vechi nedenotate e exact defectul care a
costat 27 de intrări în acest proiect.

---

## 3. Starea acum

| | |
|---|---|
| Suite unit | **505 passed / 0 failed / 0 skipped** |
| Suite deployment | **41 passed / 0 failed / 1 not-run** (`startup_cold_start`, distrugător prin design) |
| Backend live | `127.0.0.1:8910` (loopback) · `/api/health` și `/api/state` · 56 check-uri |
| Hub MCP | 26 tool-uri · handshake confirmat |
| Fișiere | ~1.350 · 32,4 MB · **nimic exclus din control de versiune** |
| Ultimul commit | vezi `git log` |

Rulare: `bat\sentinel-cc.bat`, apoi dashboard-ul pe `http://127.0.0.1:8910`.

---

## 4. Harta arborelui

```
SENTINEL_PRIME/
├── 01_FOUNDATION/      doctrina, principii, proverbe, protocoale   (substratul)
├── 02_OPERATIONAL/     ritualuri și scripturi
├── 03_INTELLIGENCE/    filtre (triple filter, anti-mimicry)
├── 04_PARTNERSHIP/     acordul cu operatorul
├── 05_LEARNING/        lecțiile învățate
├── 07_BACKBONE/        serverele MCP + OPTIMUS_MCP_CONFIG.json
├── 08_SELF_IMPROVEMENT/ suitele de test + backs + jurnale
├── 09_LOGS/            jurnalele (24 MB, inclusiv corpus_freeze)
├── 10_DOCS/            documentație
├── 11_BRAIN/           corpusul + MISSTEPS_AND_CORRECTIONS.md
├── 12_PROGRAM/         programul, GAP_REGISTER
├── 13_COMMAND_CENTER/  dashboard-ul (index.html) + api/ + logs/
├── 14_HANDOFF/         pachetul de predare
└── raport + README
```

---

## 5. Cele șapte lecții care contează cel mai mult

Toate sunt în `11_BRAIN/04_METHOD/MISSTEPS_AND_CORRECTIONS.md`, dar astea sunt
cele care îți schimbă comportamentul în prima oră:

1. **M-01** — Competența se demonstrează, nu se afirmă. Prima afirmație
   neîndeplinită costă mai mult decât zece îndeplinite.
2. **M-12** — Dovada nu poate fi definită prin cuvintele pe care le folosește și
   cel care afirmă. Un detector trebuie demonstrat **în ambele polarități**.
3. **M-15** — O suită de teste care rulează doar singură e o suită ale cărei
   rezultate sunt valabile doar singură.
4. **M-18** — O soluție trebuie testată pe intrarea **cea mai grea**, nu pe cea
   mai disponibilă. Testul ușor e singurul drum pe care l-am parcurs.
5. **M-20** — „Nicio potrivire" e dovadă de absență **doar dacă căutarea era
   capabilă de o potrivire**. Căutarea text spune *unde*; căutarea pe octeți
   spune *dacă*.
6. **M-23** — *Observabilul e sus* nu e același eveniment ca *producătorul a
   terminat de scris*. Ambele jumătăți sunt obligatorii.
7. **M-30** — Un registru al pierderii e afirmația cea mai de încredere a unui
   proiect și cea mai puțin re-verificată. M-28 a spus „irecuperabil de pe
   disc"; **23 din 27 de intrări erau acolo tot timpul**, într-un snapshot de
   referință. Caută înainte să duci o pierdere în față ca întrebare.

---

## 6. Surse de adevăr, în ordine

1. **Discul măsurată** — ce se poate măsura acum, pe main.
2. Fișierele din arbore.
3. `EVOLUTION.md` în `13_COMMAND_CENTER/` — R1…R13, cu măsurători și cu
   **eroile mele consemnate**, nu doar cu victorii.
4. `11_BRAIN/04_METHOD/MISSTEPS_AND_CORRECTIONS.md`.

`OPTIMUS_MCP_CONFIG.json` conține un bloc `superseded` scris la 2026-10-10
15:29:35, neatribuibil de pe disc. **Nu îl șterge și nu îl rescrie.**

---

## 7. Ce NU e voie

- `git clean -fdx` — șterge fișiere ignorate, poate fi conținut real.
- `git reset --hard` — distruge munca necomitată.
- Ștergere de material al operatorului. **Muți, nu ștergi.** Neclarul merge în
  carantină, cu motivul scris lângă el.
- `force push` fără cerere.
- Parole sau chei într-un mesaj de commit.
- Deployment public al Command Center-ului. E **loopback only** prin design.
- atingerea lui Hermes, a Docker swarm-ului, a OPTIMUS 8900/8901.

---

## 8. Ce rămâne de făcut

1. **Perspectivele C1–C9** nu au fost re-verificate contra build-ului curent.
   Asta e lacuna reală, nu un detaliu.
2. **M-24, M-25, M-26, M-27** — irecuperabile. Marcate în fișier ca atare.
3. Repo-ul e acum **privit** pe GitHub. Dacă trebuie public, e o decizie de
   conținut, nu una tehnică.

---

## 9. Ce înseamnă „raport"

Când operatorul cere **raport**, nu cere o descriere a formatului. El cere un
document. Formatul e fix, în 7 secțiuni, și începe cu **scopul**:

```
RAPORT DE STARE — <PROIECT> DASHBOARD - <YYYY-MM-DD HH-MM>.md
```

1. **Scopul** — prima, mereu
2. Timeline scurt
3. Ce mai rămâne
4. Decizii necesare (doar ale lui)
5. De luat în considerare
6. **Verdictul: gata sau nu** — obligatoriu, cu voce tare
7. Pasul următor

Skill-ul complet: `popy-project-status-report`.
