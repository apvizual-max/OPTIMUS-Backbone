---
name: generic-vs-specific
description: Regula fundamentala a proiectului - tot ce se construieste se face GENERIC. Cumva concret e o cheltuiala, nu o economie de timp.
---

# Generic, nu punctual

## De ce conteaza

Un CV facut pentru o firma anume e **mort dupa ce il trimiti**. Daca faci altul pentru
urmatoarea firma, **ai lucrat de doua ori**: ai rescris aceeasi experienta, aceeasi
scrisoare, acelasi layout.

Sabloanele generice se scriu **o data** si se completeaza in 2 minute:
`[ROLE]`, `[COMPANY]`, si textul real al anuntului.

## Regula

**Orice lucru nou se construieste mai intai ca sablon generic.** Daca simti nevoia sa
scrii "Saatchi" intr-un fisier, e semn ca e la momentul gresit.

```
FISA  =  LOC + CUVINTE-CHEIE + CE VA REZOLVA
aplicare = fisa + job description + numele firmei
```

Cele 9 familii de rol: `art-director`, `brand-designer`, `product-designer`,
`graphic-designer`, `ai-design-lead`, `video-motion`, `print-dtp`, `presentation`,
`social-content`. Fiecare are fisierul lui de date si de CV.

## Exemple de separare corecta

| Particular (mort) | Generic (reutilizabil) |
|---|---|
| „Dear Saatchi & Saatchi team" | `Dear [COMPANY] team,` |
| „La Yokogawa am construit 200+ șabloane" | starea in `realizari[]`, se scoate când nu se aplică |
| `Art-Director-Saatchi-CV.docx` | `graphic-designer.json` + `build.py` |
| scor pentru un anunț | `scoring.gs` cu formula, aplicată oricărui anunț |

## Ce rămâne particular, intenționat

- **Numele de clienți și cifrele** — sunt ale lui POPY, nu ale sablonului
- **Realizările concrete** — Smite, City Grill, Aderma
- **Linkurile de portofoliu** — trebuie verificate, nu inventate

Astea stau în stratul de date, nu în UI. UI-ul nu conține niciodată un nume de firmă.

## Cum verifici

```bash
# niciun nume de firma in sabloane
grep -ril "saatchi\|bell studio\|ontheroof\|flaminjoy" ALEX-KIT/SABLOANE/
# trebuie sa nu returneze nimic
```

Workflow-ul `.github/workflows/verify.yml` face asta automat la fiecare push.

## Eroarea reală care a produs regula

Am construit 6 CV-uri cu nume concrete de firmă, le-am generat, le-am urcat pe Drive.
Apoi a trebuit să le transform în 9 șabloane. **Tot conținutul era refacabil, dar
structura motorului s-a păstrat** — de aceea s-a întâmplat în 5 minute, nu în 5 zile.

Lecția: **motorul e partea scumpă. Datele sunt partea ieftină.** Scrie motorul primul.
