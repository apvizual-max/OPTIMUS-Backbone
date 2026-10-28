---
name: gmail-label-correction
description: Cum se repara o clasificare gresita in Gmail cand exista suprapuneri intre filtre, si de ce batchModify poate da 404.
---

# Repararea clasificărilor greșite

> ⚠️ **Exemplele de mai jos folosesc numele VECHI de etichete** (`MAVIS/Social`,
> `MAVIS/Personal`, `MAVIS/Actiune - de raspuns`). Din **27 oct 2026** taxonomia
> e alta: `Socials`, `Personal`, `De raspuns`. Lista curentă:
> `10-GMAIL/TAXONOMIE-2026-10-27.md`. **Verifică numele înainte să aplici o
> reparație** — o etichetă care nu există dă 404 la `batchModify`.

## Problema de bază: suprapuneri

Am construit 6 categorii cu filtre `from:`. Două dintre ele se intersectau:

```js
['social',  `{from:linkedin from:skool from:facebook ...}`]
['joburi',  `{from:jooble from:bestjobs ... from:linkedin}`]   // ← linkedin in amandoua
```

Cum `social` rula primul, **alertele de job de la LinkedIn ajungeau în Social** — unde
nu se văd. IQads era clasificat ca `personal` — un portal de joburi, nu corespondență
personală. **722 de mesaje de joburi stăteau în „Personal".**

## Regula

**Un identificator aparține unei singure categorii.** Dacă apare în două filtre, prima
categorie care rulează îl fură, și cealaltă nu va funcționa niciodată. Alege **una**.

## Repararea

```js
// 1. filtrele se corecteaza, ca nu se mai repete
['social', `{from:skool from:facebook from:instagram ...}`]        // linkedin scos
['joburi', `{from:jooble ... from:linkedin from:iqads ...}`]      // primeste si el
['personal',`{from:happyadv from:alexfiloti from:family ...}`]     // iqads scos

// 2. se muta efectiv ce a fost clasificat gresit
const FIX = [
  ['MAVIS/Personal', 'MAVIS/Joburi', '{from:iqads from:designproject}'],
  ['MAVIS/Social',   'MAVIS/Joburi', '{from:linkedin}'],
];
// pentru fiecare: cauta cu in:inbox, scoate eticheta veche, pune-o pe cea noua
```

## `batchModify` dă 404

```
POST gmail/v1/users/me/threads/batchModify  →  404
POST gmail/v1/users/me/threads/{id}/modify  →  funcționează
```

`batchModify` e cu 100 de unități indiferent de câte id-uri trimiți; `/modify` e cu
**100 de unități fiecare**. Diferența la 722 de thread-uri: 100 vs. 72.200 de unități.

Cum `batchModify` nu e disponibil pe acest cont, varianta funcțională e per-thread,
cu pauză între cereri:

```js
for (const t of batch) {
  await k.req('POST',
    'https://gmail.googleapis.com/gmail/v1/users/me/threads/' + t + '/modify',
    { addLabelIds: [toId], removeLabelIds: [fromId] });
  await new Promise(s => setTimeout(s, 150));
}
```

Rulează în fundal, cu log. Durata e de 12+ minute pentru 722 de thread-uri. **Normal.**

## Verificarea: numără, nu presupune

```js
// dupa reparație, ambele trebuie să fie 0
count('in:inbox from:iqads label:MAVIS/Personal')     // 0
count('in:inbox from:linkedin label:MAVIS/Social')    // 0
count('in:inbox from:iqads label:MAVIS/Joburi')      // 722
```

**Verifică de fiecare dată toate cele trei**, nu doar numărul nou. Altfel rămâne
posibil ca o direcție să fie reparată și cealaltă nu.

## Ce a rămas nerezolvat, intenționat

`MAVIS/Actiune - de raspuns` = **0**. Eticheta există, dar nicio regulă nu o populează.
Un astfel de etichetă goală e mai rea decât nicio etichetă: **te induce în eroare că
ai un sistem când de fapt nu ai.** Fie se scrie regula, fie se șterge eticheta.


## Etichetele cu liniuță sunt de neindexat

`MAVIS/Actiune - de raspuns` a fost aplicat cu succes — `labelIds` conținea `Label_33` —
dar **nicio interogare nu îl găsea**:

| Interogare | Rezultat |
|---|---|
| `label:"MAVIS/Actiune - de raspuns"` | 0 |
| `label:"MAVIS/Actiune"` | 0 |
| `label:MAVIS/Actiune` | 0 |
| `is:starred label:"MAVIS/Actiune - de raspuns"` | 0 |

Gmail **nu poate indexa** o etichetă al cărei nume conține o liniuță. Ghilimele nu
ajută. Singura soluție: **redenumești fără liniuță.**

```js
PATCH gmail/v1/users/me/labels/{id}   { name: 'MAVIS/De raspuns' }
// imediat: 500 thread-uri devin găsibile
```

## Spațiul cere ghilimele, liniuța cere alt nume

| În nume | Ce se întâmplă |
|---|---|
| spațiu | funcționează **cu ghilimele**, fără se strică |
| liniuță | **nu merge deloc**, nici cu ghilimele |

## Regula: zero liniuțe în numele etichetelor

```
MAVIS/De raspuns          ✅
MAVIS/Actiune - de raspuns ❌ de neindexat
```

## Mai multe capcane de interogare, în aceeași zi

1. `resultSizeEstimate` — plafonat, minte
2. `in:inbox` — contrazice „mailuri cu stea", pentru că acestea le-am scos din
   inbox la sortare. **Căutam lucruri pe care eu le mutasem.**
3. `.replace(' ','')` — șterge **doar primul** spațiu, deci rupe orice etichetă cu
   spațiu, și raportează 0 pentru un folder plin

## Diagnosticul de zero

Când o interogare întoarce 0, **întreabă de ce**, nu concluziona „e gol".
Verifică în ordine: numele are liniuță? → spațiu fără ghilimele? → `in:inbox`
exclus? → contorul manipulează corect numele?
