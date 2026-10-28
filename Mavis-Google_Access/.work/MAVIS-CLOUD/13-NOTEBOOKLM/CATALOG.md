# NOTEBOOKLM — proprietatea lui POPY, prioritatea 1

**Data:** 12 iulie 2026 · **Stare:** 🟢 funcțional, de personalizat

---

## 1. Ce e NotebookLM

Sistemul lui Google care ia documente și răspunde la întrebări pe baza lor,
cu citare la sursă. **Funcționează pe Google Drive.**

## 2. De ce e prioritatea 1 pentru POPY

> „asta e pentru mine proprietatea ta numărul 1"

Pentru că răspunde la nevoia centrală: **pregătire fără să invente**.
Pune documente, întreabă, primește răspuns **cu citare**. Exact ce POPY cere
repetat: *„fiecare cu citările corecte... și NU FABULA."*

## 3. Cele patru utilizări

| Utilizare | Ce pui | Ce primești |
|---|---|---|
| **Cercetare** | surse, linkuri, articole | sinteză cu citare |
| **Pregătire interviu** | CV, descrierea jobului, compania | întrebări probabile, răspunsuri |
| **Cercetare client** | site, brand, sector | ce cer, cum comunică, ce îi doare |
| **Design schema** |brief, context, restricții | structuri, variante, raționament |

**Toate patru au nevoie de documente corecte în Drive.** De aceea motorul de
CV-uri contează: **el produce documentele care intră în NotebookLM.**

## 4. Cum se leagă de Cloud și de Local

```
       CLOUD (eu)                    NOTEBOOKLM                LOCAL
          │                              │                      │
    culeg documente ──────────────────►  │                      │
    (cercetare web, PDF, surse)          │                      │
          │                        răspunde cu citări           │
          │                              │                      │
    pregătesc interviul ◄───────────────┘                      │
          │                                                      │
          └──────────────────► commit pe repo ─────────────────►
                                              (Local vede tot)
```

**Cloud-ul aprovizionează cu date.** Localul le folosește.
**Drive-ul e puntea** — ambii au acces la el.

## 5. Ce am făcut deja

- ✅ Google Drive conectat și verificat (12/12 teste)
- ✅ Arbore `Alex Work/` creat, cu `00-INTRARE` pentru documente noi
- ✅ Cron 08:00 scrie raportul pe Drive în `Alex Work/00-INTRARE`

## 6. Ce trebuie făcut, de POPY

**Personalizarea se face într-o discuție separată**, după ce modelul de
configurare e stabilit aici. **Nu e blocant.**

Ordinea sugerată:
1. Creează un notebook pentru **fiecare** din cele patru utilizări
2. Pune-i documentele de bază (CV-urile tale, profilul, portofoliul)
3. Notează convenția de citare — vrei română sau engleză?
4. Notează: răspuns pe română, termeni tehnici în engleză?

## 7. Fișiere care intră în NotebookLM

| Document | De unde |
|---|---|
| CV-urile tale (9) | `ALEX-KIT/CV-ORIGINALE-POPY/` |
| matricea de linkuri | `ALEX_LINK_MATRIX.json.md` |
| recomandări și testimonial | `Alex - Recommendations & Testimonials.md` |
| index discipline și industrie | `Alex - DESIGN/INDUSTRY INDEX` |
| profilul LinkedIn | `Alex - LinkedIn Profile Data.md` |
| registrul de joburi | din Drive, actualizat zilnic |

## 8. Reguli

- **Documentele intră curate.** Fără parole, fără tokenuri.
- **Citate, nu afirmații.** Dacă nu e în documente, spune că nu e.
- **Nu se completează goluri cu memorie.** Lasă gol și marchează.

---

*NotebookLM cere documente bune. Motorul de CV-uri le produce. Sunt legate.*