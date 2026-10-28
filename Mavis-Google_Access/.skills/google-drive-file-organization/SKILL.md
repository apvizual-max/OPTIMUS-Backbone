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

## Etichetele Gmail — 8

```
MAVIS/Joburi            MAVIS/AI si comunitati
MAVIS/Social            MAVIS/Newsletter
MAVIS/Finante           MAVIS/Personal
MAVIS/Facturi si conturi MAVIS/Actiune - de raspuns
```

**Cinci filtre server-side** prind mailul nou, ca să nu fie nevoie de cereri API
la fiecare rulare. Costă `messages.list` 5 unități, nu 100.

## Curățenie

- **Trash da, `delete` nu.** POPY a golit manual gunoiul după 11.655 de elemente —
  corect, și confirmat: `in:trash` = 0 după.
- **Jobul de gunoi se oprește** imediat ce POPY spune că a golit. Altfel îi umple
  din nou tot ce tocmai a șters.
- Numerele se citesc prin `email-count.js`, niciodată din `resultSizeEstimate`.

## Un identificator, o singură categorie

Vezi `gmail-label-correction`. Aceeași regulă se aplică și aici: **o sursă aparține
unei singure etichete.** Suprapunerile produc dosare goale și conținut pierdut.
