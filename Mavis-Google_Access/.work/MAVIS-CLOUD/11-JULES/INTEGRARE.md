# Jules — ce suntem, acum

**Data:** 12 iulie 2026

---

## Răspuns scurt la întrebarea ta

**Da, suntem integrați prin GitHub.** Dar integrația e la 60%, nu la 100%.

Jules citește ce e pe `apvizual-max/MAVIS-CLOUD`. Eu împing pe `main` **fără
aprobare** — deci **Jules vede permanent** ce fac. Localul împinge **doar cu
porția R0 deschisă** — deci Jules vede mai rar de la Local.

**Rularea lui Jules nu e automată.** Rulează când apeși **Run and snapshot** în
`jules.google.com/repo/github/apvizual-max/Mavis/config`. Nu rulează singur.

---

## Ce am, concret

| Ce | Stare |
|---|---|
| Cheie API Jules în secrets la mine | ✅ `JULES_API_KEY` |
| Cheie GitHub token în secrets | ✅ `GITHUB_TOKEN` |
| Setup script în repo | ✅ `docs/JULES-SETUP-SCRIPT.sh` |
| Setup script rulat cu succes | ✅ — `jules` drept user, node v22.22.1, python 3.12.13 |
| Repo clonat la Jules | ✅ — commit `eb323a2` |
| Memorie de proiect la Jules | ⬜ **textul e gata, neintrodus** |
| Primul PR văzut de Jules | ⬜ **nu a existat** |

## Cele trei goluri, în ordine

### 1. Repo-ul s-a redenumit

Jules are `apvizual-max/Mavis` în URL-ul lui. Repo-ul e acum
`apvizual-max/MAVIS-CLOUD`. GitHub redirecționează automat, deci **nu e
urgent**, dar e bine să știi.

### 2. Jules nu știe regulile proiectului

A clonat codul. **Nu știe** că:
- nu ștergem definitiv
- nu trimitem nimic
- numerele se numără, nu se estimează
- șabloanele sunt generice
- „e gata" înseamnă „POPY poate vedea"

**Textul e gata de copiat** — e în `13-NOTEBOOKLM/`? Nu, e în
`11-JULES/RAPORT-DE-STARE.md` secțiunea 8.

### 3. Nu a văzut un modul complet

Jules audită **module întregi**, nu fișiere izolate. Ca să facă asta, are nevoie
de un **pull request** cu un modul stabilizat.

---

## Ce putem face mai mult cu Jules

| Acțiune | Ce câștigăm |
|---|---|
| **Memory cu regulile** | nu mai propune lucruri care încalcă regulile |
| **Primul PR** | vede un modul complet, dă feedback real |
| **Cererea de teste** | a identificat deja că nu am teste — îl lăsăm să le scrie |
| **API-ul** | îl chem din Cloud când vreau audit, fără să deschizi tu interfața |
| **CI Fixer** | îl folosesc pe ramură separată, doar pentru bug-uri |

---

## Ce am nevoie de la tine — concret

**1. Memory.** Deschide `jules.google.com/repo/github/apvizual-max/Mavis/config`
→ **Knowledge** → **Add Memory** → copiază blocul din
`11-JULES/RAPORT-DE-STARE.md` secțiunea 8.

**2. Primul PR.** Când vrei: îmi ceri ramura, o facem, o împingem, deschidem
PR. **Ramura se face numai cu cererea ta — altfel rămâi pe `main`.**

**3. Sau:** îmi dai voie să testez API-ul cu cheia din secrets și îți spun
dacă merge, fără să deschizi tu nimic.

---

## Ce fac eu acum, singur

**Nu fac nimic care să depindă de Jules.** Sistemul merge fără el:
CV-uri, Gmail, scoring, documentație — toate mele.

Jules e **un ochi suplimentar**, nu o dependență.

---

*Stare: 🟡 PAUZĂ — funcțional parțial, 3 goluri identificate, toate cu soluția
gata de aplicat.*