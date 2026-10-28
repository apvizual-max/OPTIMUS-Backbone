---
name: mavis-cloud-skill-sync-bridge
description: Cum circula deliverable-ele intre Mavis Cloud, repo-ul GitHub, Google Drive si agentul local - reguli de naming, folderul principal de referinta, arhivare inainte de taiere si canalul de comunicare. Trigger-uri: "salveaza pe Drive", "sync", "repo", "commit", "push", "unde salvez", "folderul de proiect", "comunicare", "arhiva".
---

# Sync Bridge — repo ↔ Drive ↔ agent local

Trei suprafețe, un singur set de reguli. Un deliverable care stă doar în
conversație e **un deliverable pierdut**.

## Cele trei suprafețe

| Suprafață | Rol | Regula |
|---|---|---|
| **Repo** `apvizual-max/MAVIS-CLOUD` (main, public) | configurație, cod, documentație, puntea | **totul se comitează și împinge, fără permisiune** |
| **Drive** | **MEMORIA MEA +** suprafața de execuție + arhivă | **scriu ACOLO mereu, fără să mi se ceară** |
| **Conversație** | rezumat + decizii | **nu e loc de stocare** |

## REGULA 0 — Drive e memoria. Scriu acolo mereu.

**Contextul conversației e efemer și limitat. Drive-ul are 5 TB.**

**Deci, de acum înainte, fără excepție și fără să mi se ceară:**
- tot ce discutăm, măsurăm sau livrăm → **se scrie pe Drive imediat**
- informația care nu a ajuns pe Drive **nu există**
- **nu cer permisiune** pentru asta

**La începutul fiecărei sesiuni:**
```bash
node mavis-tools/drive-tree.js     # ce s-a scris ultima dată
```
Continuitatea se reconstruiește **de acolo**, nu din memoria conversației.

## Foldere Drive — reperul permanent

| Folder | ID | Rol |
|---|---|---|
| `Mavis-Cloud-Google-Access-Bot` | `1UQIxhctyJxBXIIFnpxSc5Jd0wvFxEylu` | **FOLDER PRINCIPAL DE REFERINȚĂ** |
| `_Connect-to-Google` | `1ea51IvZRtt7eDPbzKXotguCYg7I4kXB4` | părintele |
| `_PROOF` | `1NrkHRRSo1OFvVaueFT8AAiD53nR5nlg1` | dovezi probe |
| `GDrive-Second_Brain_PKMS` | — | vault PKM, **read-only** |

Subfolderele principale ale botului:
```
_MavisCloud-Google-Access-Bot/
├── 01-Transcript/      sesiunea completă
├── 02-Deliverables/    ce livrez
├── 03-Skills/          skill-urile (SKILL.md)
├── 04-Capabilitati/    matricea de capabilitate, probe, jurnale
└── 05-Comunicare/      canala cu agentul local
```

## Naming — obligatoriu

- **Tot ce creez din cloud:** `MavisCloud-(subiect)`.
  Exemple: `MavisCloud-Document`, `MavisCloud-Slides`, `MavisCloud-Tabel`.
- **Folderele nou:** cu număr în față (`00-`, `01-`) ca să ordoneze.
- **Fișierele de probe:** `PROBE-(serviciu)-(timestamp)`.
- **Skill-urile:** `mavis-cloud-skill-{subiect}`.

## Fluxul unui deliverable

1. **Scrie în repo**, în folderul de arie potrivit (`NN-AREA/`, `docs/`,
   `mavis-tools/`, `.skills/`).
2. **Comitează + împinge** — `main`, fără întrebare.
3. **Publică pe Drive** în folderul de referință, cu numele canonic.
4. **Raportează** în conversație cu linkul de repo și cel de Drive.

**Flux invers** (de la Drive în repo): citește → scrie fișierul → comitează.

## Arhivare înainte de tăiere

**Regulă permanentă:** înainte de orice optimizare a memoriei mele sau de
curățare de conținut, **arhivezi versiunea precedentă** în
`docs/arhiva/memorie/` cu un MANIFEST: ce s-a tăcut → unde trăiește acum.

Fără arhivă, tăierea e trunchiere de memorie și pierdere de context — pentru
POPY ăsta e EROARE, nu optimizare.

## Canalul de comunicare

Folderul `05-Comunicare/` din folderul principal. Reguli:
- **Un fișier per mesaj**, cu formatul:
  ```
  ## <subiect> — <timestamp> — <autor>
  [cerere / răspuns / decizie]
  ```
- **Deciziile se scriu acolo**, nu se pierd în chat.
- **Autorul** e `MavisCloud` sau `MavisLocal` — ca să nu se amestece.
- Citirea: `drive-vault.js read` pe calea din folder, sau
  `GET drive/v3/files?q='<id>' in parents`.

**Notă despre Drive Sync:** tot ce pun pe Drive ajunge **și pe calculatorul
lui POPY** (prin sync) — deci agentul local vede tot ce livrez. Folderul lui
local e în altă locație, dar conținutul e același. **Deci tot ce scriu aici
trebuie să fie suficient de clar pentru un cititor nou.**

## Git — reguli care nu se negociază

- `main`, push direct, **fără permisiune**.
- `git status --porcelain` trebuie să fie **gol** după fiecare commit.
- Verificare înainte de push: `node --check` pe toate `mavis-tools/*.js`.
- **Nicio valoare de secret** — vezi `mavis-cloud-skill-security`.
- Dacă push-ul e refuzat, **nu forțezi**: citește motivul. Secret-scanning
  refuză corect.
- Dacă remote-ul are commituri noi: `git fetch` + compară **înainte** de
  merge. Nu suprascrii lucra altcuia.

## Legături

Skill central: `mavis-cloud-google-access-bot` · sibling: `mavis-cloud-skill-drive`,
`mavis-cloud-skill-security`
