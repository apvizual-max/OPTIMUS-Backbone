---
name: registru-extern
description: Tot ce a fost luat de pe GitHub/GitLab si instalat, cu versiune, data si scop. Nimic nu dispare din registru.
---

# Registrul extern

**Orice lucru primit de pe GitHub, GitLab sau orice altă sursă externă intră aici.**
Nu se șterge niciodată din registru — se mută în `SCOS`.

Formatul unei linii:

```
| componentă | sursă | versiune/commit |instalat | scop | stare |
```

`stare` ∈ `ACTIV` · `SCOS` · `JAM FOLOSIT`

## Motivul

POPY: „sunt build-uri, sunt... e poveste lungă. Oamenii bucurăm de trei luni de zile
în nevoie doar cap că trebuie să am da tâmpit cei aici."

Asta se referă la materiale care nu mai sunt în uz, dar ale căror **decizii** contează.
Registrul arată ce a existat, când a intrat, și **când a ieșit și de ce.**

## Ce se înregistrează

- repo-uri clonate, cu commit-ul exact
- skill-uri importate
- biblioteci, pachete, plugin-uri
- snippet-uri de cod preluate din altă parte
- **inclusiv surse de pe GitLab și din orice loc cu cod custom**

## La ce extragi un link

POPY va da **videoclipuri, linkuri de repo, mai multe odată**. Din fiecare se
extrage sursa, se identifică ce e util, se implementează, și **se înregistrează aici
înainte de a se considera gata.** O componentă care nu e în registru nu există.

## La ce se scoate o componentă

Nu se șterge din registru. Se mută la `SCOS` cu:
- data scoaterii
- motivul (înlocuit / nefolosit / defect)
- ce l-a înlocuit

**Știind ce a fost și de ce a ieșit, eviți să-l reinstalezi peste șase luni** crezând
că e nou.