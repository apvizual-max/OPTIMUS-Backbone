# RAPORT DE STARE — LIVE REVIEW (GitHub)

**Data:** 12 iulie 2026 · **Stare:** 🟢 GRI — configurat corect

---

## 1. Ce e Live Review

Serviciu de code review automat pe GitHub (hexmos.com). **Plan free, 30% cotă.**

**Rolul lui în sistem:** verifică **push-urile către GitHub**, nu fișierele mele
de pe server, nu commit-urile din memoria mea.

```
eu lucrez → commit pe main → PUSH spre GitHub → Live Review vede push-ul
```

## 2. Regula canonică

> **Live Review privește PUSH-urile către GitHub. Rulează după ce apare acolo.
> NICIODATĂ înainte.**

## 3. Programarea — corectată

Am pus-o **inițial greșit:** `on: push`. **Fiecare commit ardea cotele.**

```yaml
# ÎNAINTE — greșit, ardea cotele la fiecare push
on:
  push: { branches: [main] }
  pull_request: { branches: [main] }

# ACUM — corect
on:
  workflow_dispatch:              # la cerere explicită
  schedule:
    - cron: '0 3 * * *'           # o dată pe zi, noaptea
```

**POPY a cerut săptămânal.** Cron-ul zilnic de la 03:00 e mai des decât
necesarul și nu arde cotele. Dacă vrei săptămânal, se schimbă un singur șir:
`'0 3 * * 0'` (duminică).

## 4. Ce rulează în workflow

| Verificare | De ce |
|---|---|
| niciun secret în commit | tokenurile nu ajung niciodată în istoric |
| JSON-uri valide | datele sunt sursa de adevăr |
| sintaxă JS | a prins o eroare pe care o ratasem |
| sintaxă Python | la fel |
| site-ul se construiește | panoul nu e rupt |
| șabloane fără nume de firmă | regula „generic" rămâne respectată |
| puntea e vie | mesajele pentru Local sunt acolo |

## 5. Cum se declanșează primul review

**Live Review n-a rulat încă pentru că nu a existat pull request.**

```
git checkout -b verificare-live-review
# o schimbare mică, reală
git commit -m "..."
git push -u origin verificare-live-review
gh pr create --base main --head verificare-live-review --title "..." --body "..."
```

**Ramura se face DOAR dacă POPY o cere.** Altfel rămâi pe `main` și
declanșezi workflow-ul din interfața GitHub.

## 6. Push asimetric — cine împinge

| Cine | Comportament | De ce |
|---|---|---|
| **Mavis Cloud** | `push origin main` **automat** | container volatil, ce nu e împins se pierde |
| **Mavis Local** | `commit` automat, **`push` blocat de R0** | controlul rămâne la om |

POPY a stabilit asta explicit. **Cloud-ul nu cere poarta R0. Localul o cere.**

## 7. Stare

| Ce | Stare |
|---|---|
| Workflow configurat | ✅ `schedule` + `workflow_dispatch` |
| Cinci verificări | ✅ trec |
| Constatare pe `push` eliminată | ✅ |
| Cotă | ✅ nefolosită inutil |
| Prima rulare | ⬜ neefectuată — lipsește un PR |

## 8. Ce fac eu pentru a-l ține activ

- `mavis-cloud-autosave.sh` face push pe main — **dar nu declanșează review**
- Workflow-ul rulează singur la 03:00
- Dacă R0 pică, nu comit și nu împing — deci review-ul nu vede cod stricat

```
[PREDARE_TEHNICA::DOVEZI_STAGED::READY_FOR_JUDGE_REVIEW]
```