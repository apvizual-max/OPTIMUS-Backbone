# MavisCloud-Livereview

**Document pentru încărcare în notebookul `MavisCloud-Livereview`**
Pregătit de Mavis Cloud · 2026-10-12 · gata de încărcare

Live Review: de ce nu rulează la fiecare push și cum se declanșează

---

**Ce e** — Revizuire automată a codului la nivel de repo.

**REGULA** — NU rulează la fiecare push. Arde cotele.

**Cum rulează** — Doar manual (workflow_dispatch) și programat noaptea la 03:00.

**Status** — Neconfigurat încă pe contul apvizual-max. Copilot endpoints dau 'Not Found'.

**Cauză probabilă** — Cont/plan/configurație — trebuie verificat pe web de POPY.

**Workflow** — verify.yml: verifică secrete, JSON-uri, sintaxă JS și Python, construcția site-ului, șabloanele generice, testele cv-mutator.

---

*2026-10-12 · Mavis Cloud · fișier gata de încărcare în notebookul `MavisCloud-Livereview`*