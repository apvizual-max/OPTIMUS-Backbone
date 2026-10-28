---
name: mavis-cloud-skill-drive
description: Capabilitatea Drive a botului mavis-cloud-google-access-bot. Cum citesc, creez, mut, redenumesc,Sharesc, caut si convertesc fisiere pe Google Drive din Mavis Cloud, cu dovezi masurate. Trigger-uri: "creeaza in Drive", "fisier pe Drive", "Google Doc nativ", "muta fisier", "cauta in Drive", "share", "sterge din Drive", "export".
---

# Drive — acces complet din cloud

**Măsurat 2026-10-28: 31/36 teste OK pe Drive.** Nu e „merge cu copilul" — merge
cu tot cu tot, inclusiv creare de fișiere native Google.

Scope-uri: `drive` (full) · `drive.appdata` (datele aplicației) · `drive.readonly`

## Ce e măsurat ca funcțional

| Operație | Cum |
|---|---|
| listare children | `drive.v3/files?q='<folderId>' in parents` |
| search | `q=name contains 'X' and trashed=false` |
| about / cotă | `drive.v3/about` |
| create folder | `POST drive.v3/files` `{mimeType:'application/vnd.google-apps.folder', parents:[id]}` |
| upload text/markdown | `POST drive/v3/files?uploadType=multipart` — **metadata în partea JSON** |
| read back | `GET files/{id}?alt=media` (text) sau `files/{id}/export?mimeType=` (nativ) |
| rename | `PATCH files/{id}` `{name}` |
| move | `PATCH files/{id}?addParents=&removeParents=` |
| copy | `POST files/{id}/copy` `{name, parents, mimeType}` |
| trash + untrash | `PATCH files/{id}` `{trashed:true/false}` — **reversibil** |
| permissions.list | `GET files/{id}/permissions` |
| share | `POST files/{id}/permissions` `{role:'reader', type:'anyone'}` |
| **creare Google Doc NATIV** | `POST drive.v3/files` cu `mimeType:'application/vnd.google-apps.document'` |
| **conversie → Google Doc nativ** | `POST files/{id}/copy` cu `mimeType:'application/vnd.google-apps.document'` |

## Workflow-ul care contează: scrie un Google Doc nativ

Docs API direct e **blocat din cloud** (anti-bot, HTML 400). Dar Drive API
convertește:

```js
// 1. scrie sursa ca text/markdown
const tmp = await kit.drive.upload('SURSA.md', '# Titlu\n\nCorp.\n', 'text/markdown', parentId);
// 2. converteste in Google Doc nativ
const doc = await kit.req('POST', `https://www.googleapis.com/drive/v3/files/${tmp.id}/copy`, {
  name: 'MavisCloud-Document', mimeType: 'application/vnd.google-apps.document',
});
// 3. citeste inapoi (Drive export, nu Docs API)
const text = await kit.docs.text(doc.id);
```

**Măsurat:** export 53 caractere, conținut corect. Asta e calea de scris Docs
din cloud, nu una ideală — dar merge și e permanentă.

## Capcane măsurate

- **Multipart**: un corp JSON obișnuit e acceptat, dar **metadata e IGNORATĂ**
  → fișierul rămâne „Untitled", fără părinte, cu mimeType greșit. Folosește
  `kit.drive.upload()`, care construiește corect cele două părți.
- **Docs API ≠ Drive export**: `docs.get` (docs.googleapis.com) → 400 cu HTML
  anti-bot. `docs.text()` merge, pentru că folosește `drive/v3/files/{id}/export`.
- **Trash ≠ ștergere**: `driveHardDelete` există în `kit.danger` pentru
  existență, **nu se apelează**. Trash e reversibil prin `{trashed:false}`.
- **Permission „anyoneWithLink"** la creare: id-ul e fix (`anyoneWithLink`),
  nu un id nou. Curăță-l imediat după test.

## Reguli

- Nume de fișiere create din cloud: **`MavisCloud-(subiect)`**.
- Un folder nou de la zero: **dă-i un număr** (`00-`, `01-`) ca să ordoneze.
- Nu rescrie ceva ce există fără să-l citești întâi.
- Vaultul `GDrive-Second_Brain_PKMS` e **read-only** — reguli în
  `19-GDRIVE/REGULI-VAULT.md`. singura excepție e `quarantine`, care **mută**
  și cere `--confirm` + motiv scris.

## Unelte

```bash
node mavis-tools/drive-vault.js root
node mavis-tools/drive-vault.js ls "01_Projects"
node mavis-tools/drive-vault.js read "COTOR.md"
node mavis-tools/drive-vault.js find "termen"
node mavis-tools/google-capabilities.js   # probe complet
```

## Legături

Skill central: `mavis-cloud-google-access-bot` · sibling: `mavis-cloud-skill-sync-bridge`,
`mavis-cloud-skill-verification`
