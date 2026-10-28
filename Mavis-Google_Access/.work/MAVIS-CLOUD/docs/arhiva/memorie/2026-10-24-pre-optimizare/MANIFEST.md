---
description: "[ARHIVĂ] Snapshot memorie agent — pre-optimizare"
---

# MANIFEST — snapshot memorie, pre-optimizare

| | |
|---|---|
| Etichetă | `pre-optimizare` |
| Creat | 2026-10-24T06:31:19.190Z |
| Sursă | ../../../../../../workspace/.staging/pre-opt |
| Fișiere | 3 |
| Notă | Arhivă de recuperare a tăierii din 2026-10-24 (memorie ~23KB -> 9,9KB). Reconstruită din output memory_read; client secret Google redacționat (repo public). Vezi secțiunea de fidelitate. |

## Fișiere

| Fișier | Bytes | sha256 (primele 16) |
|---|---|---|
| `MEMORY.md` | 21347 | `2390a96835d7d127` |
| `topics/google-access-in-cloud-absent.md` | 5404 | `ddfea0472c8ef26c` |
| `topics/scoring-gs-buguri-masurate.md` | 13908 | `312da10798142257` |

## Ce s-a tăiat din această versiune

**De ce există arhiva:** sesiunea din 2026-10-24 a tăiat din memoria de agent
~13KB (≈23KB → 9,9KB) **fără arhivare** — deci trunchiere, nu optimizare.
POPY a stabilit regula: optimizare = versiunea precedentă păstrată în repo.

### Tăiat din HOT → unde trăiește acum

| Tăiat din HOT | Unde trăiește acum | Tip |
|---|---|---|
| Blocaj Gmail 2026-10-19 (catalog 116 tooluri) | topic `google-cloud-access` → „De ce părea inaccesibil" | topic |
| IQads: script curl, loop de test, blocaj TLS | **păstrat** în HOT (2 linii) | — |
| Raport zilnic 2026-10-21 (59 joburi, scor top 9.6) | topic `raport-zilnic-pipeline` → „Istoric relevant" | topic |
| Google în cloud: contract credentiale, 4 chei, marketplace, MCP | topic `google-cloud-access` | topic |
| Secret masking: 2h loop, 4 scripturi, clientul care merge | topic `google-cloud-access` + HOT (2 linii) | topic |
| **Client secret Google în plaintext** | **eliminat** (nu e secret în memorie) | — |
| Egress TLS: explicație + code block + lista de hosturi | **păstrat** în HOT (comprimat) + skill `sandbox-gotchas` | — |
| Filtrele MAVIS/* (defect, 403, capcana 2 ferestre) | topic `gmail-sorting-filters` | topic |
| `kit.js` upload metadata | **păstrat** în HOT (1 linie) | — |
| `scoring.gs` port | **păstrat** în HOT (1 linie) + topic `scoring-gs-buguri-masurate` | topic |
| Pipeline 2026-10-23 (7 scripturi, reguli, capcana AI) | topic `raport-zilnic-pipeline` | topic |
| Pipeline 2026-10-24 (triage, `--dry`, `--save-set`, quota) | topic `raport-zilnic-pipeline` | topic |
| Lead YO AI Labs (121 roluri, până la $150/h, 5 platforme) | topic `raport-zilnic-pipeline` → „Lead nou" | topic |
| `validThrough` = datePosted + 30 zile | **păstrat** în HOT (1 linie) + topic §11 | topic |

### Topic șters

| Topic | Motiv | Înlocuit cu |
|---|---|---|
| `google-access-in-cloud-absent` | Afirma o concluzie **falsă** („Google e inaccesibil din cloud") — cauza reală era TLS | `google-cloud-access` |

**Regulă aplicată:** un topic nu se șterge fără ca informația lui să fie
depusă undeva. Și **întotdeauna** se arhivează înainte.

### Fidelitatea arhivei

Fișierele au fost reconstruite din output-ul `memory_read` al sesiunii, nu
copiate de pe disc (memoria trăiește pe host, nu în sandbox). `memory_read`
**normalizează** unele cuvinte la afișare (ex. în fișierul stocat e
„prezintat", view-ul arăta „prezentat"). Conținutul e fidel, dar **nu e
byte-identic** cu originalul. De acum înainte arhiva se scrie **din fișier**,
prin `mavis-tools/memory-snapshot.js`.

**Redacție:** client secret-ul Google care era în memorie (`GOCSPX-…`) a fost
**eliminat din arhivă înainte de push** — repo-ul e public. Regula: secretele
se elimină din memorie **înainte** de arhivare, nu după.

## Regulă

Arhiva e append-only. Nu se șterge nimic din ea.


_(se completează în sesiunea de optimizare: ce a fost comprimat, mutat în topic
sau șters, și unde trăiește acum)_

**Regulă:** arhiva e append-only. Nu se șterge nimic din ea.
