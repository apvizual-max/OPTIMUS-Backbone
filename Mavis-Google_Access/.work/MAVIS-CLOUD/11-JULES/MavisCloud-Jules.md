# MavisCloud-Jules

**Document pentru încărcare în notebookul `MavisCloud-Jules`**
Pregătit de Mavis Cloud · 2026-10-12 · gata de încărcare

Jules ca auditor: cum se declanșează, ce a fost construit, ce a fost reparat

---

**Ce e** — Agent de cod asincron al Google. Creează branch, scrie cod, deschide PR. Nu rulează local.

**Cum se declanșează - 1** — ETICHETA `jules` pe un GitHub issue → 'label on, task live'. FUNCȚIONEAZĂ, testat.

**Cum se declanșează - 2** — Mențiune `@jules` pe PR — DOAR dacă Jules are PR deschis, și DOAR în Reactive Mode.

**Cum se declanșează - 3** — GitHub Action — singurul programabil: `google-labs-code/jules-action@v1.0.0`.

**Cum se declanșează - 4** — Jules CLI: `jules remote new`, `jules task create`.

**Bug reparat 1** — `jules-invoke@v1` NU EXISTA. Workflow-ul pica: 'unable to find version v1'.

**Bug reparat 2** — Input-ul se numește `jules_api_key`, nu `api-key`.

**Bug reparat 3** — JULES_API_KEY era doar la Cloud, nu și în secrets-ul repo-ului.

**Workflow** — jules.yml: etichetă + manual + săptămânal duminica 09:00.

**De ce săptămânal** — Cota Jules = 100 cereri/zi. Zilnic ar arde-o.

**Audit săptămânal** — Doar raport, nu construiește. Verde → nu deschide PR.

**Regula lui POPY** — Jules propune, Cloud tratează. Cloud întâi complet. Local doar dacă cere execuție fizică.

**Rezultat** — Issue #2 → PR #3 cu 10 teste pentru cv-mutator.js → AUDITAT și INTEGRAT pe main.

---

*2026-10-12 · Mavis Cloud · fișier gata de încărcare în notebookul `MavisCloud-Jules`*