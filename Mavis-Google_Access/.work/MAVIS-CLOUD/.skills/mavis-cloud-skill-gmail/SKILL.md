---
name: mavis-cloud-skill-gmail
description: Capabilitatea Gmail a botului mavis-cloud-google-access-bot. Cum citesc mesaje, aplic etichete, modific, creez drafturi si repar filtrele server-side din Mavis Cloud. Trigger-uri: "etichete Gmail", "filtre Gmail", "draft", "cauta in mail", "repara clasificarea", "MAVIS/Joburi", "sortare mail".
---

# Gmail — citit, clasificat, reparat

**Măsurat 2026-10-28.** Gmail are `gmail.modify` + **`gmail.settings.basic`** →
**filtrele se pot crea și șterge din cloud** (până pe 28 oct era imposibil:
scope-ul lipsea și `filters PATCH` dădea 403).

Scope-uri: `gmail.modify` · `gmail.readonly` · `gmail.compose` · `gmail.settings.basic`
· `mail.google.com/`

## Ce e măsurat ca funcțional

| Operație | Endpoint |
|---|---|
| profil | `GET gmail/v1/users/me/profile` |
| listare | `GET .../messages?q=<query>&maxResults=` |
| citire mesaj | `GET .../messages/{id}?format=full` |
| **etichete** | `GET .../labels` · `GET .../labels/{id}` (mesaje + thread-uri per etichetă) |
| **modify** | `POST .../messages/{id}/modify` `{addLabelIds, removeLabelIds}` |
| **batchModify** | `POST .../messages/batchModify` `{ids:[], addLabelIds}` |
| draft | `POST .../drafts` · `GET/DELETE .../drafts/{id}` |
| **filtre** | `GET/POST/DELETE .../settings/filters` — **UPDATE NU EXISTĂ** |
| trash mesaj | `POST .../messages/{id}/trash` (**reversibil**) |

## Numărarea corectă

`resultSizeEstimate` e **plafonat** — raportează 201 pentru orice interogare,
inclusiv Trash cu 626 de mesaje. **Nu e numărătoare.**

```js
async function exact(q) {
  let n = 0, pt = null;
  do {
    const r = await kit.req('GET', `https://gmail.googleapis.com/gmail/v1/users/me/messages?maxResults=500${pt ? `&pageToken=${pt}` : ''}&q=${encodeURIComponent(q)}`);
    n += (r.messages || []).length; pt = r.nextPageToken;
  } while (pt);
  return n;
}
```

**Regula de aur:** nu număra în timp ce rulează altă operațiune Gmail. Zero
înseamnă „n-am putut măsura", nu „nu există". Contorul se ciocnește cu
sortările și raportează greșit.

## Filtrele — repararea

**Cele două defecte clasice (măsurate oct 2026):**
1. `from:(a b c)` înseamnă **ȘI** în căutarea Gmail. `{}` înseamnă **SAU**.
   → cer un expeditor cu TOATE cuvintele → 0 mesaje.
2. `addLabelIds` vid → chiar dacă filtrul lovește, nu pune eticheta.

**Regulă:** când rearanjezi etichete, mută filtrele în aceeași zi.

```js
// CREATE cu acțiune reală (o acțiune goală -> 400 "Filter doesn't have any actions")
const f = await kit.req('POST', 'https://gmail.googleapis.com/gmail/v1/users/me/settings/filters', {
  criteria: { query: 'from:{jooble bestjobs indeed}' },
  action: { addLabelIds: ['Label_27'], removeLabelIds: ['INBOX'] },
});
```

**Test sigur de write:** creează un filtru cu un criteriu care **nu poate
potrivi** (`subject:"maviscloud-write-probe-9x8y7z-never-matches-anything"`) și o
acțiune inofensivă, verifică 200, apoi îl ștergi. Efect zero, dovadă reală.

**MĂSURAT 28 oct 2026 — ciclul complet de write e CONFIRMAT:**
`CREATE` (200) → `LIST` (apare, 20 filtre) → `GET` single (200) →
`DELETE` (200, 19 filtre). **Scrierea pe filtre e reală.**

### ⚠️ LIMITARE REALĂ: filtrele **nu se pot modifica** — `filters.update` nu există

| Metodă | Rezultat |
|---|---|
| `POST /settings/filters` (create) | ✅ 200 |
| `GET /settings/filters` (list) | ✅ 200 |
| `GET /settings/filters/{id}` | ✅ 200 |
| `DELETE /settings/filters/{id}` | ✅ 200 |
| **`PUT /settings/filters/{id}`** | ❌ **404** (pagină HTML de la UploadServer) |
| **`PATCH /settings/filters/{id}`** | ❌ **404** JSON „Method not found" |

**Deci: pentru a modifica un filtru → `DELETE` + `CREATE`.** Exact asta face
`mavis-tools/fix-mavis-filters.js` din partea locală. **Salvează starea
curentă înainte** (`filters-state-before-repair.json`) ca să poți rollback.

## Capcane măsurate

- **`users.drafts.modify` → 404.** Calea funcțională e
  `messages.modify` pe id-ul mesajului din draft.
- **Filtre cu acțiune goală → 400** „Filter doesn't have any actions".
- **`objectId` de obiect Gmail** — id-urile de etichetă sunt case-sensitive.
  Citește etichetele live, nu din documentație.
- **Taxonomia se schimbă.** La 27 oct 2026: 7 din 8 etichete `MAVIS/*` au fost
  redenumite, au apărut 4 familii noi (`WORK | AP-ID/`, `Knowledge/`,
  `Crypto | Trade | News/`, `JOBS-Interview/`). Doar `MAVIS/Joburi` a supraviețuit.
  **Citește etichetele live, nu numele vechi din documente.**
  Lista curentă: `10-GMAIL/TAXONOMIE-2026-10-27.md`.

## Reguli

- **Nu trimit mail.** Draft da. Send doar la comanda explicită a lui POPY.
- **Nu șterg definitiv.** Trash + motiv scris.
- Nu aplic etichete în masă fără să existe filtrul care le populează.
- Nu raporțez „filtrele sunt OK" fără verificare live.

## Legături

Skill central: `mavis-cloud-google-access-bot` · sibling: `mavis-cloud-skill-drive`,
`mavis-cloud-skill-verification`
