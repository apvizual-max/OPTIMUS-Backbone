# CV-uri — ale tale sunt sursa, nu ale mele

## Ce am greșit

CV-urile tale originale din `CV-ORIGINALE-POPY/` erau **complete, generale și
corecte.** Aveau experiență reală cu date, clienți, roluri.

**Eu le-am înlocuit cu versiuni reconstruite de la zero** și am introdus erori:

| Am scris eu | Tu ai scris corect |
|---|---|
| **„Smite"** | **Skin Media** |
| „Aiper and Pure" (ca și clienți de campanie) | Nikon, Aiper, Pure Electric — Skin Media |
| rezumat de 50 de cuvinte | rezumat complet, cu context și scope |
| 3 realizări | experiență reală cu 4+ roluri, date, clienți |

**Am pierdut informație reală și am introdus nume greșite.** Tu ai spus-o
corect: *„trebuia să fie deja generale... ce dracu ai căutat să le adaptezi."*

## Regula de acum

> **CV-urile tale sunt sursa. Nu reconstruiesc de la zero — actualizez.**

Fluxul corect:
```
CV-URI tale (generale, pline)      ← ALEX-KIT/CV-ORIGINALE-POPY/
        ↓  se copiază, NU se rescriu
copie de lucru                      ← ALEX-KIT/CV-URI/
        ↓  se schimbă DOAR: keywords, titlu, [COMPANY]
adaptare pentru un job
```

**Ce se schimbă la adaptare, nimic altceva:**
- `{nume firma}` în loc de nume concret
- keywords din job description
- accentul pe competențele din anunț

**Ce NU se schimbă niciodată:** experiența, datele, clienții, realizările.

## Ce conțin CV-urile tale

| Fișier | Rol |
|---|---|
| `Alex CV - Senior Graphic Designer.md` | graphic designer |
| `Alex CV - Senior Art Director & Creative Lead.md` | art direction |
| `Alex CV - Senior UX-UI & Digital Product Designer.md` | product design |
| `Alex CV - Video and Motion Designer.md` | video & motion |
| `Alex CV - Print & DTP Specialist .md` | print & DTP |
| `Alex CV - Creative Systems Arhitect.md` | sisteme creative |
| `Alex CV - AI-Driven Multimedia Systems.md` | sisteme AI |
| `Alex CV - Design Automation Specialist.md` | automatizare design |
| `Alex - DESIGN DISCIPLINE INDEX (A-Z).md` | index discipline |
| `Alex - INDUSTRY INDEX (A-Z).md` | index industrie |
| `Alex - Portfolio INDEX Map - General ART Direction.md` | hartă portofoliu |
| `Alex - Portfolio INDEX Map - UI-UX Role Adaptation.md` | adaptare rol |
| `ALEX_LINK_MATRIX.json.md` | matricea linkurilor |
| `Alex - Recommendations & Testimonials.md` | recomandări |
| `Alex - LinkedIn Profile Data.md` | date LinkedIn |

## Ce am construit la rândul meu

`cv-mutator.js`, `letter-engine.js`, `scoring.gs`, 9 șabloane.

**Păstrate, dar cu rol schimbat:** sunt **instrumente**, nu surse de adevăr.
Eleiau cuvinte și structură. **Conținutul vine de la tine.**

## Clienți reali — din CV-urile tale

```
Microsoft PCoE (via Shipley Associates)   H&M
Yokogawa                                    Erste Group
Skin Media                                  Intesa Sanpaolo
Nikon                                       Aiper
Pure Electric                               Ninja
Romexpo                                     SITA Africa
AP-ID.ro                                    UAE Ministry of Education
Serus Dacia   CRD Credit   Engino Toys
Optima Call  Auditeco      Soho Design
STEP IT Academy (profesor)
```

**Testimonial:** Kevin Donlan, VP of Strategic Alliances & Programs,
Shipley Associates (Microsoft PCoE Proposal Partner)

## Contact

```
Email:   apvisual.arond@gmail.com     ← cel confirmat de POPY
Telefon: +40722121752
Site:    ap-id.ro
LinkedIn: linkedin.com/in/ap-id
```

> ⚠️ **Fișierul `Alex - LinkedIn Access.md` conține parolă în clar.**
> **A fost șters din repo și nu a fost NICIODATĂ în istoric.**
> `.gitignore` acoperă acum `*Access*.md`. Cheile stau în managerul de secrete.

## Ce fac cu cele 7 CV-uri Word

**Nu le refac.** Le regenerez **din ale tale**, cu `{nume firma}` în loc de
nume concrete, păstrând toată experiența.

**Stare:** ⬜ de făcut — și se face **după** ce Local pornește, pentru că
CV-urile sunt un artefact de **producție**, nu de cercetare.

**Scop:** fiecare rol de CV e o **specializare de sector**, cu keywords și
informații specifice din portofoliul tău. Fotograf și designer nu sunt același
lucru. Nici art și designer. De aceea un template per rol — cu datele tale
păstrate intacte.