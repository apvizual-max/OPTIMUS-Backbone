# MavisCloud-Google

**Document pentru încărcare în notebookul `MavisCloud-Google`**
Pregătit de Mavis Cloud · actualizat 2026-10-22 · stare reală, măsurată

Google Workspace: Gmail, Drive, Calendar, Docs, Sheets, Slides

---

**Stare** — ✅ **CONECTAT** (măsurat 2026-10-22 04:40). Tokenul e în secret
manager, cele 6 scope-uri sunt acordate, verificarea live trece.

| Serviciu | Stare | Măsurătoare |
|---|---|---|
| Gmail | ✅ | 84.313 mesaje · 78.519 thread-uri · 50 etichete (8 MAVIS/*) |
| Drive | ✅ | 104,07 GB / 5498 GB |
| Calendar | ✅ | 4 calendare |
| Sheets | ✅ | "Design_Jobs_Community_Board" → 23 rânduri |
| Slides | ✅ | "441DPH-Brief slides…" → 7 slide-uri |
| Docs | ⚠️ | API-ul blocat din cloud (anti-bot) — **conținutul merge prin Drive export** |
| Photos | ⛔ | blocat din cloud — merge de pe calculatorul lui POPY |
| Maps | ⛔ | cere `GOOGLE_MAPS_API_KEY` + billing |

**Următorul pas:** Testing → **In production**, ca tokenul să nu moară în
7 zile (consimțământul a fost 2026-10-22 01:39 UTC). Checklist:
`docs/GOOGLE-PRODUCTION-CHECKLIST.md`.

**Ce e măsurat acum** (din sandbox-ul de cloud, cu cod HTTP real):
- Google Drive API → merge
- Gmail API → merge
- Calendar API → merge
- Docs / Sheets / Slides → merge
- Google Photos → ⛔ host blocat de rețea din cloud (`photoslibrary.googleapis.com`, 0/6)
- Google Workspace MCP servers (oficiale) → ⛔ tot blocate din cloud (`*mcp.googleapis.com`, 0/6)

**Conector nativ MiniMax pentru Google** → nu există în Marketplace
(catalog: Hundsun, Qichacha, EverMe, PKBC, Office, WPS, WeCom; cache runtime: figma, github).

**Cum se rezolvă** → OAuth propriu. Client ID = identificator public, stă în
`mavis-tools/google-client.json`. Secretele stau în secret manager:
`GOOGLE_CLIENT_SECRET_MAVIS_CLOUD`, `GOOGLE_REFRESH_TOKEN_MAVIS_CLOUD`, `GOOGLE_EMAIL`.

**Setup** →
1. `node mavis-tools/google-preflight.js` — verdict pe un singur rând
2. `node mavis-tools/google-link-file.js` — scrie linkul în `18-GOOGLE/AUTORIZARE-LINK.txt`
3. consimțământ în browser → codul de autorizare
4. `node mavis-tools/google-connect.js "<url>"` → tokenul
5. `node mavis-tools/google-verify.js` — măsurătoare reală per serviciu

**Regulă** — NUNCIODATĂ ștergere definitivă. Trash doar, și se poate restaura.

**Identitate** — apvizual@gmail.com — singurul email pe tot sistemul.

**Detalii complete** — `docs/GOOGLE-INTEGRARE.md` ·
`docs/GOOGLE-STATUS-2026-10-22.md` (diagnostic + forensică) ·
`docs/GOOGLE-PRODUCTION-CHECKLIST.md` (Testing → In production) ·
`docs/PROCEDURA-LIVRARE-SECRETE.md` (livrare fără secrete)

---

## Arhitectura — unde se lucrează

| Suprafață | Ce e | Cine lucrează acolo |
|---|---|---|
| **Google Drive** | PKM personal + **munca efectivă** (Gmail, GDrive) | POPY + Mavis Cloud |
| **Acest repo** | **configurația** sistemului + back-up + puntea Cloud↔Local | Mavis Cloud + Mavis Local |
| **Mavis Local** | administrează configurația | agentul de pe calculatorul lui POPY |

Repo-ul **nu** e locul de muncă. E locul unde sistemul e definit și versionat.
Folderul `Alex Work/` nu mai există — a fost înlocuit de Drive.

Repo-ul este **public** (2026-10-22), ca aplicațiile conectate să-l analizeze.

---

## PROCEDURA — cum se livrează un link de autorizare care merge

**Regula:** valorile din secret manager **nu trec prin chat** — platforma le
maschează în `{{ARCHON_SECRET:...}}` și linkul ajunge în browser cu
placeholder → *Error 401: invalid_client* (2026-10-22).

```bash
cd /workspace/mavis-cloud

# 1. verifica starea — verdict pe un singur rand, ~10 secunde
node mavis-tools/google-preflight.js

# 2. genereaza linkul IN REPO (nu in chat)
node mavis-tools/google-link-file.js     # -> 18-GOOGLE/AUTORIZARE-LINK.txt

# 3. comit + push, fara aprobare
git add -A && git commit -m "..." && git push origin main

# 4. livreaza URL-ul de repo
#    https://github.com/apvizual-max/MAVIS-CLOUD/blob/main/18-GOOGLE/AUTORIZARE-LINK.txt
```

POPY deschide linkul → Allow → browserul moare pe `127.0.0.1:8976` (normal) →
copiază bara de adresa cu `?code=...` → o trimite prin chat (codul **nu** e
secret) → eu schimb codul, scriu tokenul în secret manager și verific live.

Detalii: `docs/PROCEDURA-LIVRARE-SECRETE.md` · skill `mavis-secure-delivery`

---

*2026-10-22 · Mavis Cloud · măsurat, nu estimat*
