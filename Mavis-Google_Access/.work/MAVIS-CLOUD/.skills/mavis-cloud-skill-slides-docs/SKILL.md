---
name: mavis-cloud-skill-slides-docs
description: Capabilitatea Slides si Docs a botului mavis-cloud-google-access-bot. Cum creez prezentari, adaug slide-uri cu text, si cum scriu Google Docs nativ din cloud cand Docs API direct e blocat. Trigger-uri: "prezentare", "slides", "slide-uri", "Google Doc", "document", "export in format".
---

# Slides & Docs — prezentări și documente nativ

Scope-uri: `presentations` · `documents` · `drive`

---

## SLIDES — măsurat funcțional

| Operație | Endpoint | Rezultat |
|---|---|---|
| **create prezentare** | `POST slides.googleapis.com/v1/presentations` `{title}` | ✅ id + 1 slide |
| **read** | `GET slides.googleapis.com/v1/presentations/{id}` | ✅ slide-uri, titlu, pageElements |
| **batchUpdate** | `POST .../{id}:batchUpdate` | ✅ createSlide + insertText |

### Cele trei reguli care au costat probe-uri reale

1. **`objectId` ≥ 5 caractere.** `probeSlide2` merge; `s2` → 400 „object ID
   length should not be less than 5".
2. **Placeholder-ul stă la `element.shape.placeholder`**, NU la
   `element.placeholder`. Greșeala asta dă „fara placeholders" și te face să
   crezi că n-a mers.
3. **`createSlide` cu layout predefinit**, apoi `insertText` **în placeholder-urile
   layout-ului**. Un slide gol (`createSlide` fără layout) nu acceptă text.

```js
const p = await kit.req('POST', 'https://slides.googleapis.com/v1/presentations', { title: 'MavisCloud-Slides' });
await kit.req('POST', `https://slides.googleapis.com/v1/presentations/${p.presentationId}:batchUpdate`, {
  requests: [{ createSlide: { objectId: 'probeSlide2', slideLayoutReference: { predefinedLayout: 'TITLE_AND_BODY' } } }],
});
const g = await kit.slides.get(p.presentationId);
const sl = g.slides.find(s => s.objectId === 'probeSlide2');
const ph = sl.pageElements.filter(e => e.shape && e.shape.placeholder);
// ph[0] = TITLE, ph[1] = BODY
await kit.req('POST', `https://slides.googleapis.com/v1/presentations/${p.presentationId}:batchUpdate`, {
  requests: ph.map((e, i) => ({ insertText: { objectId: e.objectId, text: i === 0 ? 'Titlu' : 'Corp' } })),
});
```

**Citirea textului înapoi:** `element.shape.text` e un
`TextContent`, nu un string. Textul real e la
`element.shape.text.textElements[].textRun.content`. Citirea greșită dă „"
și pare o lipsă de scriere, deși scrierea a mers.

**`createShape` are altă formă de parametri** (`size` cu `unit:'EMU'`) și
respinge `transform` în această versiune de API. Nu e necesar pentru fluxul
de bază — layout-urile predefinite acoperă cazul.

---

## DOCS — API direct e blocat, workaround-ul merge

**Măsurat:** `docs.googleapis.com/document/v1/documents` → **HTTP 400 cu pagină
HTML anti-bot** din cloud. Nu e o limitare reală, e o blocare de rețea/robot.

**Calea care merge: Drive API.**

```js
// 1. scrie sursa
const tmp = await kit.drive.upload('SURSA.md', '# Titlu\n\nCorp.\n', 'text/markdown', parentId);
// 2. converteste in Google Doc NATIV
const doc = await kit.req('POST', `https://www.googleapis.com/drive/v3/files/${tmp.id}/copy`, {
  name: 'MavisCloud-Document', mimeType: 'application/vnd.google-apps.document',
});
// 3. citeste inapoi prin Drive export (NU Docs API)
const text = await kit.docs.text(doc.id);
```

**Măsurat:** 53 caractere exportate, conținut corect.

**Limitare asumată:** conversia face un **snapshot**, nu o editare in-place.
Pentru a actualiza, creezi din nou (nou document) — deci păstrează sursa
master în Drive și regenerează.

### Export în orice format

`kit.docs.export(id, mime)` merge prin `drive/v3/files/{id}/export`:
`text/plain` · `text/markdown` · `application/pdf` ·
`application/vnd.openxmlformats-officedocument.wordprocessingml.document` ·
`application/vnd.openxmlformats-officedocument.presentationml.presentation` ·
`text/csv` · `application/vnd.google-apps.document` (round-trip Google Doc).

## Reguli

- Prezentări create din cloud: `MavisCloud-(subiect)`.
- La conversie Docs, păstrează **sursa** (markdown) — documentul nativ e derivat.
- Nu construiesc prezentări de la zero pentru fluxuri existente: `441DPH-Brief
  slides for GD senior_sep 2026` există deja (7 slide-uri).

## Legături

Skill central: `mavis-cloud-google-access-bot` · sibling: `mavis-cloud-skill-drive`
