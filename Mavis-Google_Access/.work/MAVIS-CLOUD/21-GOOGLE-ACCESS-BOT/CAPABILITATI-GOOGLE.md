# CAPABILITĂȚILE GOOGLE — matrice măsurată

> **Măsurat live din cloud la 2026-10-28**, cu `mavis-tools/google-capabilities.js`
> (36 de teste, apeluri reale, dovezi păstrate pe Drive în `_PROOF`).
> **Nu e estimare și nu e listă de scope-uri** — e ce a răspuns HTTP 200.

---

## 1. Rezumat

**Rezultatul final: 36 OK · 0 blocate · 2 eșuate (din 38 de teste).**

Cele 2 eșecuri sunt **ambele aceeași limită reală**: Docs API direct e blocat de
anti-bot din cloud (pagină HTML la HTTP 400). **Workaround-ul trece** — deci
scrierea de Google Docs native e posibilă, doar pe altă rută.

La prima rulare au picat 5; **3 erau bug-uri ale probe-ului** (nu limite
reale) și au fost reparate + retestate. Restul, 2, erau limită reală.

```
9 OK · 1 blocat · 1 eșuat      (google-verify.js — verificare de servicii)
36 OK · 0 blocate · 2 eșuate   (google-capabilities.js — probe de scriere)
```

**Doveza curentă:** `mavis-tools/.capabilities.json` · folderul `_PROOF` pe Drive.

---

## 2. Matricea pe serviciu

### DRIVE — 100%

| Operație | Stare | Doi | Note |
|---|---|---|---|
| listare children | ✅ | | `q='<id>' in parents` |
| search pe nume | ✅ | | `q=name contains 'X' and trashed=false` |
| about / cotă | ✅ | 107,78 GB | |
| **create folder** | ✅ | | |
| **upload text/markdown** | ✅ | 104 B | multipart cu metadata în partea JSON |
| read back conținut | ✅ | | `?alt=media` / `export` |
| rename | ✅ | | |
| **move între foldere** | ✅ | | `addParents` + `removeParents` |
| copy | ✅ | | acceptă și `mimeType` → **conversie** |
| **trash + untrash** | ✅ | | reversibil, `trashed:false` reface |
| permissions.list | ✅ | | |
| **share (create permission)** | ✅ | | id fix `anyoneWithLink` |
| **create Google Doc NATIV** | ✅ | | `mimeType: application/vnd.google-apps.document` |
| **conversie → Google Doc nativ** | ✅ | 53 char | `files.copy` cu `mimeType` nativ + export: **conținut corect** |

### GMAIL — complet

| Operație | Stare | Doi |
|---|---|---|
| profile | ✅ | 82.877 mesaje (după golirea Trash-ului) |
| list / read mesaj | ✅ | |
| **etichete (read)** | ✅ | 51 etichete, 36 de utilizator |
| **messages.modify** | ✅ | `labels=DRAFT,IMPORTANT` |
| **messages.batchModify** | ✅ | |
| create draft | ✅ | **nu trimite** |
| **filtre: list** | ✅ | 19 filtre |
| **filtre: create + delete** | ✅ | **doveadă `gmail.settings.basic`** |

> `users.drafts.modify` → **404**. Calea funcțională: `messages.modify` pe
> id-ul mesajului din draft.

### CALENDAR — complet

| Operație | Stare |
|---|---|
| list calendare | ✅ 4 calendare |
| list evenimente | ✅ |
| **create event** | ✅ |
| **read back** | ✅ |
| **update** | ✅ summary modificat |
| delete | ✅ |

### SHEETS — complet

| Operație | Stare | Doi |
|---|---|---|
| **create spreadsheet** | ✅ | |
| **write** | ✅ | `updatedRange: Probe!A1:C2` |
| **read** | ✅ | `A1=Mavis Cloud` |
| **append** | ✅ | |
| move în alt folder | ✅ | |

### SLIDES — cu scriere

| Operație | Stare | Doi |
|---|---|---|
| **create prezentare** | ✅ | 1 slide |
| read | ✅ | slide-uri, titlu, pageElements |
| **batchUpdate: add slide** | ✅ | 2 slide-uri |
| **batchUpdate: insert text** | ✅ | text citit înapoi: `["Titlu scris de Mavis Cloud.","Corp scris de Mavis Cloud."]` |

### DOCS — prin workaround

| Cale | Stare |
|---|---|
| `docs.googleapis.com` direct | ❌ **HTTP 400 cu pagină HTML anti-bot** |
| `drive/v3/files/{id}/export` (citire) | ✅ |
| **write prin conversie Drive** | ✅ — sursa → `files.copy` nativ → export: **conținut corect** |

---

## 3. Ce NU merge din cloud — și de ce nu e problemă

| Serviciu | Stare | Decizia lui POPY (28 oct) |
|---|---|---|
| **Photos Library** | ❌ 403 scope | Automatizat pe Mavis Local. Pentru cloud: Gemini direct. **Nu cer `photoslibrary.readonly` în token.** |
| **Maps** | ⛔ API key + billing | Rezolvat pe partea locală. Nu intră în token. |
| **NotebookLM** | ⛔ fără API oficial | Vezi `mavis-cloud-skill-notebooklm` — 3 căi reale. |
| **Docs API direct** | ❌ anti-bot | **Workaround-ul merge.** Nu e limitare reală. |

---

## 4. Ce s-a câștigat cu tokenul nou (27 scope-uri, era 6)

**Câștigul decisiv: `gmail.settings.basic`.**
Până pe 28 oct, `filters PATCH/POST` răspundeau **403**, deci filtrele Gmail se
puteau repara **doar de pe mașina lui POPY**. Acum se pot repara din cloud.
**Măsurat:** filtru creat cu criteriu inofensiv → 200 → șters imediat.

Restul: `mail.google.com/` · `gmail.readonly` · `gmail.compose` · `gmail.send` ·
`drive.readonly` · `drive.appdata` · `calendar.events` · `contacts` ·
`chat.spaces.readonly` · `chat.messages` · `forms.body` ·
`forms.responses.readonly` · `script.projects` · `books` · `youtube.readonly` ·
`youtube.upload` · `photospicker.mediaitems.readonly` · `userinfo.email` ·
`userinfo.profile` · `openid`

---

## 5. Capcane măsurate — nu se repetă

| Eroare | Cauza reală | Soluție |
|---|---|---|
| 400 „Filter doesn't have any actions" | acțiunea filtrului nu poate fi goală | `addLabelIds:['IMPORTANT']` + criteriu inofensiv |
| 404 `users.drafts.modify` | endpoint nefuncțional | `messages.modify` pe id-ul mesajului |
| 400 „object ID length should not be less than 5" | Slides `objectId` scurt | `probeSlide2` (≥5 char) |
| „The object does not allow text editing" | placeholder căutat greșit | `element.shape.placeholder`, nu `element.placeholder` |
| „Unknown name 'size'/'transform'" în `createShape` | altă formă de parametri | folosește layout predefinit, nu `createShape` |
| 400 cu **HTML** | blocare de rețea/anti-bot | distinge de 403 JSON (scope) |
| multipart ignorat | metadata trimisă ca JSON simplu | `kit.drive.upload()` construiește corect cele 2 părți |

---

## 6. Probe-ul rulează oricând

```bash
node mavis-tools/google-capabilities.js                    # implicit: folderul botului
node mavis-tools/google-capabilities.js --parent <id>      # alt folder
node mavis-tools/google-capabilities.js --json rezultat.json
```

Dovezile rămân pe Drive în `_PROOF`. Artefactele tranzitorii (draft, eveniment,
filtru throwaway, permisiune temporară) **se curăță la final** — contul lui
POPY nu se poluează.

---

*2026-10-28 · Mavis Cloud · măsurat live*
