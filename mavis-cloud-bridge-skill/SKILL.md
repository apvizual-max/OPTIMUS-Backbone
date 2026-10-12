# MAVIS — CLOUD BRIDGE (protocolul Local ↔ Cloud)

**Tip:** micro-skill în cadrul suitei `mavis-optimus-continuous-integration-skill`
**Scop:** cum circulă informația între Mavis Cloud și Mavis Local, și unde se
oprește fiecare.
**Stare:** 🟡 BLUEPRINT — protocolul e scris; puntea automată **nu e construită**
(`mavis-sync.sh` nu există în repo).

## 1. Legea asimetrică — singura diferență între cele două instanțe

| | Mavis Cloud | Mavis Local |
|---|---|---|
| mediu | container volatil, online 24/7 | mașina lui Popy, D:/E:/C: |
| push pe GitHub | **direct, fără R0** | **doar cu R0 explicit** |
| ramură | `main` | `main` |
| commit | automat | automat |
| fișiere personale | nu le are | le are |
| browser / deploy | nu | da |

Restul procesului e identic. **Nu** mai mult. Orice „extindere" a diferenței
trebuie demonstrată cu un caz, nu cu o plauzibilitate.

> „Cloud-ul împinge DIRECT pe GitHub (fără R0), pentru că rulează asincron în
> container volatil." — Popy, 2026-10-12.

## 2. Ce a construit Cloud, măsurat

Handoff-ul `docs/HANDOFF-2026-10-12-0440-jules.md` (04:40) raportează:

- **34 commituri · 0 necomitate · 0 nepushuite**
- **172 documente .md** · 19 skill-uri proprii + 16 vendor · 11 Priming KIT
- 36 scripturi în `mavis-tools`
- workflow-uri: `jules.yml`, `verify.yml`
- repo `apvizual-max/MAVIS-CLOUD` · **privat** · ultima push 01:21 UTC

## 3. Regula „nu fac jumătate de sarcină"

Citată din același handoff:

> „Un handoff nu e «restul îl face Local». Un handoff e o sarcină completă, cu
> toate datele, toate fișierele, toate deciziile deja luate. Local primește
> munca gata de rulat, nu o problemă de rezolvat."

Convenția de numire, care face ordine în timp:
`docs/HANDOFF-YYYY-MM-DD-HHMM-<subiect>.md`. **Niciodată suprascris.**

## 4. Citirea de pe partea Local — read-only prin clonă

```powershell
git -C cloud-ingest\MAVIS-CLOUD pull --ff-only
```

- `cloud-ingest\` e **ignorit** de `.gitignore`-ul lui `MAVIS-OPTIMUS-CI`: nu
  dublăm date personale și nu îngropăm un repo în alt repo.
- Se accesează **prin cale documentată**, nu prin copiere.
- **Nu se modifică nimic în `MAVIS-CLOUD`.** Se citește, se citește istoricul,
  se copiază *ideea*.

Măsurat 2026-10-12: `eb323a2` → `006c3d1` prin `pull --ff-only`.

## 5. De ce puntea automată NU e construită — și de ce nu se construiește orbește

`docs/BRIDGE.md` din Cloud specifică `mavis-sync.sh` cu o buclă
`while true … git push`. Pe main-ul local, **o asemenea buclă ar ocoli poarta
R0** — ar împinge fără R0, contra legii.

Deci: se construiește **doar** în forma care respectă asimetria:
- citire (`fetch` / `pull`) — automat, fără R0;
- commit local — automat;
- **push — poartă, nu buclă.**

O punte care ar depăși singurul punct unde se cere acordul omului nu e o punte,
e o scurtătură.

## 6. Ce rămâne pentru Local, din handoff, complet și netăiat

Cloud a enumerat trei sarcini, declarate complete:

| | sarcină | ce nu e necesar să-l întreb |
|---|---|---|
| 5.1 | verifică setup-ul local, construiește puntea după `BRIDGE.md` | datele sunt în repo |
| 5.2 | rebuild site-uri cu datele verificate | datele sunt enumerate în handoff |
| 5.3 | **nu folosi `ALEX-KIT/SABLOANE/`** pentru CV-uri finale | `ALEX-KIT/TEMPLATES-POPY/` e sursa lui Popy |

Punctul 5.3 e o **corectură de sursă**: Cloud a construit 9 șabloane din memorie,
Popy avea deja ale lui, cu `{Company_Name_Here}` și `{Nume_Companie_Aici}`. Sursa
lui Popy e în `ALEX-KIT/TEMPLATES-POPY/`.

## 7. Surse

- `cloud-ingest\MAVIS-CLOUD\docs\HANDOFF-2026-10-12-0440-jules.md` — cel mai nou
- `cloud-ingest\MAVIS-CLOUD\docs\BRIDGE.md` — specificația punții (**neconstruită**)
- `docs/CONFLICTE-DOZTRINA.md` în `MAVIS-OPTIMUS-CI` — cele 7 conflicte, cu citate