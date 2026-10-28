---
name: job-sourcing-methods
description: Cum se gasesc joburi reale pe piata romaneasca. Scraping direct esueaza; cautarea cu interogare pe domeniu trece.
---

# Cum se găsesc joburi reale

## Constatarea care a schimbat metoda

Am încercat scraping direct pe platformele de joburi. Rezultat:

| Platformă | Ce s-a întâmplat |
|---|---|
| IQads | 403 |
| eJobs | 403 / răspuns gol |
| BestJobs | 403 |
| Jooble | 503 |
| bestjobs.eu | `page load failed` |

Motive: protecție anti-bot, liste randate client-side, rate limiting. **Nu merită încercat.**

## Ce funcționează: căutare cu interogare pe domeniu

```bash
web_search "site:iqads.ro \"art director\" 2026"
web_search "site:iqads.ro adjob \"creative director\" octombrie 2026"
```

Interogarea pe domeniu trece pe unde scraping-ul nu trece, **și întoarce textul complet
al anunțului** — nu doar linkul. Asta e exact ce are nevoie scoring-ul.

## Alternative confirmate

- `designproject.io` — merge prin `web_fetch`. 46 poziții RO, cu salariu, remote, visa sponsorship
- `uiuxjobsboard.com`, `euremotejobs.com`, `Nomado24`, `DailyRemote` — design remote
- `Jobgether` — agregator; a dat Senior Product Designer RO la $70–80k

## Regexul practic

```bash
site:iqads.ro "art director" 2026
site:designproject.io romania design
site:iqads.ro "senior graphic" "2026-1"     # filtrează după lună
```

## Verificarea zilei de expirare

IQads pune **„Anunț valabil până la data de ..."** în text. **Întotdeauna verifică
data înainte să scrii ceva într-un raport.** Un anunț expirat e exact la fel de inutil
ca unul inexistent, dar pare nou.

## Ce faci cu ce găsești

1. Copiezi textul integral în `jd`
2. Îl treci prin `scoring.gs`
3. Ie într-una din 4 secțiuni
4. **Din secțiunea 1 ieși CV-ul** prin `cv-mutator.js`

Nu inventa anunțuri ca să ai de unde lucra. Dacă nu s-a găsit nimic proaspăt, spune
„nu s-a găsit nimic proaspăt azi" — e o informație, nu o eșec.

## Ce a funcționat exemplar

Am citit 6 anunțuri reale și am extras **limbajul pieței**, citat:

- **Saatchi:** „viteză în execuție, dar și atenție la detalii. Care dă și prompturi bune"
- **Bell Studio:** „researchul și ideile bune stau la baza oricărui proiect reușit, indiferent de unelte"
- **pastel:** „diferența dintre AI slop și AI care te ajută să fii mai eficient"
- **Line Agency:** „Nu ești doar un executant — ești omul care definește standardul", 7–10 ani

**Asta e poziționarea lui POPY, în cuvintele pieței, nu ale mele.** Se folosește ca
axiomă în CV-uri și scrisori.
