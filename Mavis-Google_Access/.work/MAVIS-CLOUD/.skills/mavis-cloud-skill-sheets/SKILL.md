---
name: mavis-cloud-skill-sheets
description: Capabilitatea Sheets a botului mavis-cloud-google-access-bot. Cum creez spreadsheet, scriu valori, citesc si adaug randuri din Mavis Cloud. Trigger-uri: "Google Sheets", "tabel", "randuri", "valori", "Design_Jobs_Community_Board", "joburi tabel".
---

# Sheets — tabele din cloud

Scope: `spreadsheets` (full). Plus `drive` pentru a muta fișierul unde trebuie.

## Ce e măsurat ca funcțional (28 oct 2026)

| Operație | Endpoint | Rezultat măsurat |
|---|---|---|
| **create spreadsheet** | `POST sheets.googleapis.com/v4/spreadsheets` | ✅ id returnat |
| **write** | `PUT .../values/{range}?valueInputOption=USER_ENTERED` | ✅ `updatedRange` corect |
| **read** | `GET .../values/{range}` | ✅ 2 rânduri, A1 corect |
| **append** | `POST .../values/{range}:append?valueInputOption=USER_ENTERED` | ✅ |
| **move în alt folder** | Drive `PATCH files/{id}?addParents=&removeParents=` | ✅ |

## API-ul

```js
// creare cu sheet-uri si tab-uri proprii
const s = await kit.req('POST', 'https://sheets.googleapis.com/v4/spreadsheets', {
  properties: { title: 'MavisCloud-Tabel' },
  sheets: [{ properties: { title: 'Probe' } }],
});
const id = s.spreadsheetId;

// scrie
await kit.sheets.update(id, 'Probe!A1:C2', [['Mavis Cloud', 'probe', stamp], ['ok', 1, 2]]);

// citește
const v = await kit.sheets.values(id, 'Probe!A1:C2');   // v.values[]

// adaugă la final
await kit.sheets.append(id, 'Probe!A1', [['rand nou', 'probe', stamp]]);
```

## Ce măsurat la POPY

- `Design_Jobs_Community_Board` — `'Design Jobs'!A1:Z50` = 27 rânduri
  (era 23 pe 22 oct — crește singur, e alimentat de pipeline-ul local).

## Capcane

- **`valueInputOption=USER_ENTERED`** vs `RAW`: cu `RAW`, textul care începe cu
  `=` e luat ca literal. Pentru date și formule vrei `USER_ENTERED`.
- **Range-ul trebuie să includă numele tab-ului** (`Probe!A1:C2`), altunci
  Google merge pe primul tab.
- **`sheets.append` returnează `updatedRange` inconsistent** (uneori
  `undefined`). Nu te baza pe el — citește înapoi ca să confirmi.
- **Un spreadsheet creat prin Sheets API aterizează în root**, nu în folderul
  dorit. Mută-l imediat cu Drive `PATCH`.
- **CITĂRI** = `values` (valorile calculate) vs `formulas` (formulele). Pentru
  audit, citește `formulas` **și** `values`.

## Reguli

- **Nu suprascriu rânduri existente fără să le citesc întâi** și să raportez ce
  era acolo.
- Sheets e sursa de adevăr pentru „Design Jobs" — pipeline-ul local scrie,
  Mavis Cloud citește și raportează. **Nu rescriu acele rânduri din cloud**
  fără acord explicit: ar fi o cursă cu procesul local.
- Nume de tabel nou: `MavisCloud-(subiect)`.

## Legături

Skill central: `mavis-cloud-google-access-bot` · sibling: `mavis-cloud-skill-drive`,
`mavis-cloud-skill-verification`
