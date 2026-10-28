---
name: google-drive-file-organization
description: Cum se construieste arborele de fisiere pe Drive si de ce Google Drive este stocul de sistem, nu doar un dosar.
---

# Organizarea pe Drive

## De ce Drive e stocul de sistem

CV-urile, pachetele de aplicare și documentația trebuie să fie unde POPY le
**deschide efectiv** — nu unde se află fișierul pe serverul meu. Drive e interfața
lui cu tot ce producem.

## Arborele

```
Alex Work/
├── 00-INTRARE/        ← aici cad rapoartele zilnice și CV-urile noi
├── 01-IDENTITATE/     ← cine e POPY, bio, date de contact
├── 02-CERERI/         ← CV-uri și documente de aplicare
├── 03-PROIECTE/       ← câte un folder per client
├── 04-ARHIVA/         ← ce nu mai e activ
├── 90-SETUP/          ← instrucțiuni, contor, configurație
└── ALEX-KIT/          ← motorul: scoruri, șabloane, scripturi
    ├── TINTE/         ← câte un punct de plecare per țintă
    ├── CV-URI/        ← DOCX gata de trimis
    └── SABLOANE/      ← cele 9 șabloane generice
```

## Reguli

1. **Numele încep cu cifră și liniuță** — Drive le ordonează alfabetic, nu cronologic
2. **`90-` la final** — configurare, nu conținut
3. **`04-ARHIVA` nu se șterge** — se mută
4. **CV-urile de trimis stau în `02-CERERI`** — nu în `04-ARHIVA`

## Etichetele Gmail — 36 (nu mai sunt 8)

**Taxonomia s-a schimbat pe 27 oct 2026.** Prefixul `MAVIS/` a căzut de pe 7 din
8 etichete, și au apărut 4 hierarhii noi. Lista curentă, cu numere măsurate:
`10-GMAIL/TAXONOMIE-2026-10-27.md`.

```
MAVIS/Joburi            Newsletter              Socials
AI Folder/AI si Comunitati                     De raspuns
Facturi si Conturi     Personal                Finante
WORK | AP-ID/*          Knowledge/*             Crypto | Trade | News/*
Home | Car | Shopping/* JOBS-Interview/*       Optimus CD    SCAMS
```

**19 filtre server-side** prind mailul nou, ca să nu fie nevoie de cereri API
la fiecare rulare. Costă `messages.list` 5 unități, nu 100. Toate validate
27 oct: **0 sparte**.

**Regulă:** când rearanjezi etichete, mută filtrele în aceeași zi — altfel
mailul nou dispare din sistem.

## Curățenie

- **Trash da, `delete` nu.** POPY a golit manual gunoiul după 11.655 de elemente —
  corect, și confirmat: `in:trash` = 0 după.
- **Jobul de gunoi se oprește** imediat ce POPY spune că a golit. Altfel îi umple
  din nou tot ce tocmai a șters.
- Numerele se citesc prin `email-count.js`, niciodată din `resultSizeEstimate`.

## Un identificator, o singură categorie

Vezi `gmail-label-correction`. Aceeași regulă se aplică și aici: **o sursă aparține
unei singure etichete.** Suprapunerile produc dosare goale și conținut pierdut.
