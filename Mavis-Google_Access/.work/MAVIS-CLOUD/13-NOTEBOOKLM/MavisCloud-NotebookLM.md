# MavisCloud-NotebookLM

**Document pentru încărcare în notebookul `MavisCloud-NotebookLM`**
Pregătit de Mavis Cloud · 2026-10-12 · gata de încărcare, nu mai trebuie editat

---

## 1. Ce este NotebookLM și de ce contează pentru POPY

Sistemul Google care ia documente și răspunde la întrebări **pe baza lor, cu citare
la sursă**. Exact ce POPY cere repetat: *„pregătire fără să invente".*

Răspunsul vine cu trimitere la documentul din care a venit. **Dacă informația nu e
în surse, nu o inventează** — pentru că nu are de unde.

---

## 2. Limită de platformă — verificată, nu presupusă

| | NotebookLM personal | NotebookLM Enterprise |
|---|---|---|
| Adresă | `notebooklm.google.com` | `notebook.cloud.google.com` |
| **API oficial** | **NU există** | există |
| Autentificare | cont Google + **cookie-uri de browser** | token Google Cloud |
| Cost | gratuit | **licențe plătite** + IdP + proiect Cloud |

Conectorii disponibili în cloud: `github`, `matrix`, `cloudflare`, `figma`.
**Niciun NotebookLM.** De aceea Cloud nu creează notebook-uri.

---

## 3. Cine face ce

```
CLOUD    pregătește documentele MavisCloud-*.md, le comitează în repo
LOCAL    deschide notebooklm.google.com → creează notebook-ul → încarcă fișierele
```

---

## 4. Convenția de denumire

Un notebook per folder, nume standard: **`MavisCloud-(subiect)`**

| Folder | Notebook |
|---|---|
| `10-GMAIL/` | `MavisCloud-Gmail` |
| `11-JULES/` | `MavisCloud-Jules` |
| `12-LIVEREVIEW/` | `MavisCloud-Livereview` |
| `13-NOTEBOOKLM/` | `MavisCloud-NotebookLM` |
| `14-LINKEDIN/` | `MavisCloud-Linkedin` |
| `15-SITE-B2B/` | `MavisCloud-SiteB2B` |
| `16-SITE-SYSTEMS/` | `MavisCloud-SiteSystems` |
| `17-SKILLS/` | `MavisCloud-Skills` |
| `18-GOOGLE/` | `MavisCloud-Google` |
| `07-SITEURI-NIVEL1/` | `MavisCloud-SiteNivel1` |
| `ALEX-KIT/` | `MavisCloud-CV` |

---

## 5. Ce pui în fiecare notebook

**1.** Documentele din folderul respectiv (`MavisCloud-*.md`)
**2.** CV-ul master: `ALEX-KIT/TEMPLATES-POPY/TEMPLATE - CV - ... - LONG.md`
**3.** Pentru notebookul CV: și șabloanele de scrisoare cu `{Company_Name_Here}`

---

## 6. Ce NU pui

- ❌ Parole, tokenuri, chei — **nici măcar într-un notebook privat**
- ❌ `credentials.json`
- ❌ Date personale care nu-s necesare CV-ului
- ❌ Conținut din Vault-ul personal — ăla e cu altă cheie

---

## 7. Întrebări utile pentru notebook

Când documentele sunt încărcate, întreabă lucruri pe care nu ți le-am dat eu de mână:

- „Ce am scris despre `{firma}` în CV-ul meu lung?"
- „Ce proiecte am la `{Aderma Protect / City Grill / ROMEXPO}`?"
- „Ce diferență e între rolul de la Skin Media și cel de la Smite?"
- „Ce am spus despre experiența cu AI, pe scurt?"
- „Ce cuvinte-cheie folosesc pentru rolul de Art Director?"

---

*2026-10-12 · Mavis Cloud · fișier gata de încărcare*