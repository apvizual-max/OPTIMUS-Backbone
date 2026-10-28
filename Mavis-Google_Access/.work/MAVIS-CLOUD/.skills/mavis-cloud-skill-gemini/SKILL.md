---
name: mavis-cloud-skill-gemini
description: RAG cu citare peste documentele tale, prin Gemini API + File Search. Cum creezi store, cum ingestezi surse din Drive, cum intrebi si cum citesti citatile. Este calea aleasa de POPY pentru research cu surse, in locul NotebookLM. Trigger-uri: "intreaba documentele", "research cu citari", "file search", "gemini", "RAG", "ce stiu despre", "din surse", "grounding".
---

# Gemini File Search — research cu citare

**Calea (a), aleasă de POPY pe 2026-10-28.** NotebookLM nu are API oficial
pentru un cont Google normal; asta dă **același rezultat**: întrebări cu citare
peste documente, din cloud, permanent.

**Cheie:** `GOOGLE_AI_STUDIO_FREE_TIER_KEY` (free tier AI Studio).

---

## 1. Ce funcționează, măsurat

| Operație | Stare | Note |
|---|---|---|
| `POST /v1beta/fileSearchStores` | ✅ | corpul = store **direct**: `{"displayName","embeddingModel"}` |
| upload în store | ✅ | **resumable, 2 pași** (vezi §3) |
| ingestie din Drive | ✅ | `docs.text()` / `sheets.values()` / `slides.get()` → text |
| ingestie de folder Drive | ✅ | `fromfolder` |
| `generateContent` cu `file_search` | ✅ | **citări în `groundingMetadata.groundingChunks`** |
| Interactions API | ✅ | funcționează, dar **fără citări explicite** în răspuns |

---

## 2. Comenzi

```bash
node mavis-tools/gemini-filestore.js list
node mavis-tools/gemini-filestore.js init "MavisCloud-Knowledge"
node mavis-tools/gemini-filestore.js add <store> <fisierLocal> ["nume vizibil"]
node mavis-tools/gemini-filestore.js fromdrive <store> <driveFileId> ["nume vizibil"]
node mavis-tools/gemini-filestore.js fromfolder <store> <folderId>
node mavis-tools/gemini-filestore.js ask <store> "întrebarea"
node mavis-tools/gemini-filestore.js delete <store>
```

**Store-ul curent:** `fileSearchStores/maviscloudknowledge-ca5rla3w4dnz`
(„MavisCloud-Knowledge", embedding `models/gemini-embedding-2`).

---

## 3. Capcanele măsurate — nu le mai ghicești

### Corpul de create e **direct**, neîmpachetat
```jsonc
// CORECT
POST /v1beta/fileSearchStores  {"displayName":"MavisCloud-Knowledge","embeddingModel":"models/gemini-embedding-2"}
// GREȘIT (400 "Cannot find field")
{"fileSearchStore":{"displayName":...}}   {"file_search_store":{"display_name":...}}
```

### Upload-ul e **resumable, în 2 pași** — nu multipart
```bash
# Pas 1 → primești headerul x-goog-upload-url
POST /upload/v1beta/{store}:uploadToFileSearchStore
  X-Goog-Upload-Protocol: resumable
  X-Goog-Upload-Command: start
  X-Goog-Upload-Header-Content-Length: N
  X-Goog-Upload-Header-Content-Type: text/plain
  body: {"displayName":"nume.txt"}

# Pas 2 → trimite conținutul la URL-ul primit
POST <x-goog-upload-url>
  X-Goog-Upload-Offset: 0
  X-Goog-Upload-Command: upload, finalize
  body: <conținut>
```
`/upload/v1beta/fileSearchStores/{id}/files` → **404** (nu exista).

### Modelul — lanț de fallback pe free tier
`gemini-2.5-flash` → *„no longer available to new users"*.
`gemini-3.8-flash` → *„project has exceeded a quota"* (free tier).
**`gemini-3-flash-preview` → merge.** Scriptul încearcă automat:
`gemini-3.8-flash` → `gemini-3-flash-preview` → `gemini-flash-latest`.

### Citările vin din `generateContent`, nu din Interactions API
```js
const gm = j.candidates[0].groundingMetadata;
gm.groundingChunks[].retrievedContext.title   // sursa
gm.groundingChunks[].retrievedContext.text    // fragmentul citat
```
Interactions API returnează `steps` cu `file_search_call` (dovada căutării),
dar **fără citări explicite**. Deci pentru răspunsuri cu surse, folosește
`generateContent`.

### `pageSize` la listare e max **20**
`pageSize=100` → 400 „must be between 1 and 20".

---

## 4. Fluxul complet, gata de rulat

```bash
# 1. store
node mavis-tools/gemini-filestore.js init "MavisCloud-Knowledge"

# 2. ingestează tot folderul principal de pe Drive
node mavis-tools/gemini-filestore.js fromfolder \
  fileSearchStores/maviscloudknowledge-ca5rla3w4dnz 1UQIxhctyJxBXIIFnpxSc5Jd0wvFxEylu

# 3. întreabă
node mavis-tools/gemini-filestore.js ask \
  fileSearchStores/maviscloudknowledge-ca5rla3w4dnz \
  "Ce a hotărât POPY despre etichete și filtre?"
```

**Cost:** free tier are cotă zilnică. La 3.8-flash ai hit de RPM. Nu arde
cota cu întrebări de test — o întrebare reală, o dată.

---

## 5. Reguli

- **Nu răspund din memorie** la întrebări despre conținutul documentelor lui
  POPY. E de fiecare dată **File Search cu citare**, ca răspunsul să fie
  verificabil.
- **Fiecare răspuns important poartă sursa** (titlul documentului).
- **Nu ingestiez tot Drive-ul** — doar folderul cu pricina. Fiecare document
  în plus costă cotă și timp de indexare.
- **Store-ul e permanent** (nu TTL ca fișierele din Files API, care se șterg
  în 48h). Datele indexate rămân până la `delete`.
- **Nu aleg modelul „cu cotă mare"** — lantul e definit în script.

## Legături

Skill central: `mavis-cloud-google-access-bot` · sibling: `mavis-cloud-skill-drive`
(furnizează sursele), `mavis-cloud-skill-sync-bridge`
