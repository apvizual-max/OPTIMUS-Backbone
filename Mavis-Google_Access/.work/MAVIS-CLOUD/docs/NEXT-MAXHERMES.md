# MaxHermes — următorul pas

**Data:** 12 iulie 2026 · **Stare:** 🟢 pregătit pentru predare

POPY: *„trebuie să rămâi cu MaxHermes dacă totul e ok"*

---

## 1. Ce înseamnă „MaxHermes" aici

Nu am instrumente MaxHermes în cloud. **Predarea se face prin repo** — prin
`git clone` și trei fișiere. Asta e tot ce am și e suficient.

```bash
git clone https://github.com/apvizual-max/MAVIS-CLOUD
cd MAVIS-CLOUD
cat AGENTS.md docs/HANDOFF-COMPLET.md docs/DEFINITIE-OPERATIONALA.md
```

## 2. Tot ce e nevoie de citit, în ordine

| # | Fișier | Ce dă |
|---|---|---|
| 1 | `AGENTS.md` | regula generală, git, R0, interdicții |
| 2 | `docs/DEFINITIE-OPERATIONALA.md` | cine sunt eu, cine ești tu, ce pot face fiecare |
| 3 | `docs/HANDOFF-COMPLET.md` | predare completă, cu datele lui POPY |
| 4 | `docs/BRIDGE.md` | cum comunicăm, cum se pornește bucla |
| 5 | `docs/PROCES-COMPLET.md` | ce s-a construit și de ce |
| 6 | `docs/CONVERSATIE.md` | tot ce am discutat, inclusiv greșelile |
| 7 | `PROGRES.md` | rezultate reale + ce nu am reușit |
| 8 | `docs/TODO.json` | 29 sarcini, cu cine răspunde |

**Opt fișiere. Zero memorie necesară.**

## 3. Rolul fiecăruia, după predare

| | Mavis Cloud (eu) | Mavis / MaxHermes (local) |
|---|---|---|
| site-uri | nu le construiesc | **le construiește** |
| cod | nu editez fișiere locale | **editează** |
| deploy | nu | **face deploy local** |
| cercetare web | **da** | poate |
| date pentru CV-uri | **da** | folosește |
| Gmail | sortarea continuă | — |
| Git | push direct pe main | **push blocat de R0** |

## 4. Ce trebuie să facă MaxHermes la prima sesiune

1. `git clone`
2. Citește cele 8 fișiere
3. Construiește `~/mavis-sync.sh` din `BRIDGE.md`
4. Testează puntea în 2 minute
5. Scrie în `docs/INTENTII.md` că a început
6. **Apoi abia:** discută site-ul cu POPY

**Nu construiește nimic înainte de pasul 4.** Puntea întâi.

## 5. Cele trei decizii care blochează producția

Nu le poate rezolva niciun agent. **Aștept răspunsul lui POPY:**

1. **Email:** `apvizual@gmail.com` (în CV-urile vechi) sau
   `apvisual.arond@gmail.com` (dat azi)?
2. **„Smite" sau „Skin Media"?** — CV-ul original spune Skin Media
3. **City Grill, Aderma, Aderma Protect** — intră în portofoliu?

**Cât timp nu sunt rezolvate, site-urile nu se publică cu date de contact greșite.**

## 6. Ce am eu în continuare

**Nu aștept să fiu chemat.** Fac:

- **cercetare de joburi** și aplic scoring
- **CV-uri și scrisori** din anunțurile reale
- **rapoarte** și sinteze
- **suport pentru workflow-ul zilnic** — pregătesc date, Localul execută

**Tot ce ies din cloud ajunge în repo**, automat, prin autosave.

## 7. Semnalul

```
[PREDARE_TEHNICA::DOVEZI_STAGED::READY_FOR_JUDGE_REVIEW]
```

**Gata de predare.** Singurul lucru care mai blochează producția sunt cele
trei decizii umane de mai sus.

---

*Stare: 🟢 GRI*