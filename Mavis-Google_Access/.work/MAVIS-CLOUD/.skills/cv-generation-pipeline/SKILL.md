---
name: cv-generation-pipeline
description: Fluxul complet de la un anunt de job la un CV de o pagina gata de trimit. Include toate corectiile de pe parcurs.
---

# De la anunt la CV de trimis

```
anunt real
   ↓  scoring.gs          scor + secțiune (1, 2, 3 sau drop)
   ↓  family              'graphic-designer' → FAMILY_TITLE → titlu
   ↓  cv-mutator.js       header, 9 competențe, 3 realizări, linkuri
   ↓  letter-engine.js    scrisoare, 203 cuvinte, 4 paragrafe
   ↓  {rol}.json          stratul de date al site-ului
   ↓  make-cv-docx.py     DOCX 1 pagină + scrisoare pag 2
   ↓  Drive/ALEX-KIT/CV-URI
```

## Formula de scoring

```
0.35 × S  (potrivire rol)
0.30 × D  (disciplină)
0.20 × L  (locatie)
0.15 × E  (experiență cerută)
```

Semnul de întrebare e **diminuant**: contează *ce* e jobul, nu *unde* e.
Secțiunile: 1 = master stream, 2 = contracte, 3 = sub-senioritate.

## Circuit breaker-uri

Un rol e **dropat**, nu punctat, dacă:
- e junior / entry / intern — nu se negociază
- disciplina nu se potrivește niciunui tier
- e necorelabil cu portofoliul

## Normalizarea AI-ului după vârsta domeniului

„5+ ani în AI" **nu** înseamnă middle. Designul are 20+ ani, AI-ul are 4. Un rol
care cere 5 ani de AI e, pentru el, **senior**, nu entry.

## Familiile de rol — 9

`art-director` · `brand-designer` · `product-designer` · `graphic-designer` ·
`ai-design-lead` · `video-motion` · `print-dtp` · `presentation` · `social-content`

## Erorile care au apărut, și reparul

### Substring în loc de limite de cuvânt

```js
// GREȘIT — 'ai' se potrivește în 'said', 'captain', 'detail'
/app|ui|ux|ing/.test(text)

// CORECT
function hasWord(text, w) {
  var esc = w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  return new RegExp('(^|[^a-z0-9])' + esc + '($|[^a-z0-9])', 'i').test(text);
}
```

Apărea în **două locuri**: în `cv-mutator.js` și în `scoring.gs`. Căutarea de
discipline din `scoring.gs` folosea `indexOf`, nu limite.

### Titlu dedus din text — orice cuvântă câștigă

La rolul `[ROLE]`, titlul se deduce din textul anunțului. Într-un anunț de
**graphic design** apărea și „print" → câștiga greșit, și CV-ul devenea
„Senior Print & DTP Specialist".

**Repar:** `FAMILY_TITLE[family]` — rolul spune familia, textul doar colorează.
Determinist, nu ghicit.

### Ordinea verificărilor în `cleanTitle`

„Comfy **UI**" declanșa ramura UX și trimitea un „Product Designer" la un rol de AI.
**AI se verifică primul.**

### `HARD` și `SOFT` au primit aceeași cheie

Adăugând `social` în două obiecte, ambele intrări au ajuns în `SOFT`, iar
`HARD['social']` rămănea `undefined` → `TypeError` pe orice rol social.
**Repar:** cheie explicită în ambele, plus `achievements.social` și `summary.social`.
O cheie nouă de specializare trebuie să existe în **toate cele patru** tabele.

### Markeri markdown rămași în Word

`**Production Acceleration:**` trecea ca text literal. **Repar:** `.replace('**','')`
înainte de formatare, cu `:` în primele 60 de caractere ca reper de bold.

## Limitele care rămân valabile

- Titlu: **≤10 cuvinte**
- Rezumat: **≤80 cuvinte**, framework CAR
- Competențe: **exact 9** (5 hard + 4 soft)
- Realizări: **exact 3**
- Scrisoare: **~203 cuvinte**, 4 paragrafe
- CV-ul final: **1 pagină**, scrisoarea **~jumătate de pagină**
- **ATS-friendly:** o coloană, Calibri 10pt, fără tabele, secțiuni cu nume standard

## Proof of work

Textul fix, în două forme:
- engleză: `Proof of work provided on request.`
- română: `Dovada de lucru, la cerere.`

**Niciodată** linkuri video inventate.
