---
name: mavis-cloud-verify-before-report
description: Nu raporta niciodata ceva ca fiind facut daca POPY nu o poate vedea. Distinde 'in repo' de 'live'.
---

# Nu spune „e gata" la ceea ce nu se vede

## Eroarea reală

Am construit tab-ul TO DO în repo. **Nu l-am publicat.** Și am raportat:

> „tab TO DO adaugat, cu 10 sarcini și status"

Cuvintele erau adevărate. **Omisiunea nu.** POPY s-a uitat în panoul Site
și nu era acolo. A crezut că mint.

## Regula

Înainte să spun că ceva e gata, verific pe **suprafața pe care POPY o vede**:

| Ce | Unde stă | POPY vede? |
|---|---|---|
| Fișier în repo | GitHub | da |
| Build local | `SITE/dist/` | **nu** |
| **Deploy** | panoul Site | **da** |

**Dacă nu e pe suprafața lui, spun asta. Explicit.**

```
✗ "tab TO DO adaugat"
✓ "tab TO DO e în repo și în build. NU e pe site — pentru asta trebuie
   deploy. Spune-mi și îl public."
```

## Verificarea obligatorie înainte de raport

```bash
B=https://da15e9yb994ps.space.minimax.io
diff <(curl -sk "$B/" | grep -oE 'data-p="[a-z]+"' | sort -u) \
     <(grep -oE 'data-p="[a-z]+"' SITE/dist/index.html | sort -u)
```

**Dacă dif-ul nu e gol, ce nu e pe site NU e gata.** Îl spun înainte, nu
după ce mă întreabă.

## Când chiar nu pot face un lucru

Un site static nu poate scrie în repo. Un buton nu poate apela API-ul meu.
Deployment-ul meu creează întotdeauna un nod nou.

**Astea se spun înainte de a construi, nu după.** Construiesc butonul care
funcționează, și îl numesc explicit buton de coadă, nu de acțiune.

## Trei reguli, rezumate

1. **Fiecare cifră, numărată.** Fiecare stare, verificată pe suprafața lui.
2. **Dacă nu poate vedea, spun că nu poate vedea.**
3. **Limită tehnică = spusă înainte, nu după.**