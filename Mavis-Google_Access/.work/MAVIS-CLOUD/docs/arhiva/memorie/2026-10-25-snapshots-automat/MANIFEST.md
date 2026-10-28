---
description: "[ARHIVĂ] Snapshot memorie agent — snapshots-automat"
---

# MANIFEST — snapshot memorie, snapshots-automat

| | |
|---|---|
| Etichetă | `snapshots-automat` |
| Creat | 2026-10-25T21:05:06.524Z |
| Sursă | ../../../../../../workspace/.staging/memorie-snapshot |
| Fișiere | 6 |
| Notă | Snapshot săptămânal automat (task cloud). Nu s-a tăiat nimic. |

## Fișiere

| Fișier | Bytes | sha256 (primele 16) |
|---|---|---|
| `MEMORY.md` | 11089 | `6eeee3dbe461de78` |
| `topics/gmail-sorting-filters.md` | 3412 | `599ae32619dad560` |
| `topics/google-cloud-access.md` | 4879 | `08c0b7cc80d82232` |
| `topics/memory-maintenance-tooling.md` | 3224 | `1e72832ee2b39603` |
| `topics/raport-zilnic-pipeline.md` | 7390 | `a1db73e0b27589b6` |
| `topics/scoring-gs-buguri-masurate.md` | 13107 | `f7568ca35865a814` |

## Ce s-a tăiat din această versiune

**Nimic.** Acesta e snapshotul săptămânal automat (task cloud
`455764418027683`, duminica 23:00) — doar arhivează, **nu taie**, nu comprimă,
nu modifică nimic din memorie.

| Ce s-a tăiat | Unde trăiește acum |
|---|---|
| — (nimic) | — |

Arhiva e ca să existe o copie recentă a memoriei **înainte** de orice tăiere
viitoare, nu ca o urmă de optimizare. Orice optimizare ulterioară își taie
versiunea precedentă din arhiva asta.

**Fidelitate:** conținutul a fost scris din output-ul `memory_read` /
`memory_topic_read` (memoria trăiește pe host, nu în sandbox). `memory_read`
normalizează unele cuvinte la afișare ⇒ conținutul e fidel, dar **nu e
byte-identic** cu fișierul de pe host.

**Secrete:** verificate înainte de snapshot — nicio valoare de cheie (client
secret, refresh token, API key) în conținut. Doar identificatori publici
(client_id Google, id-uri de folder Drive), care există deja în repo.

**Regulă:** arhiva e append-only. Nu se șterge nimic din ea.
