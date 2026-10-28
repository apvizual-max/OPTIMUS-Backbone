# CONSTANTARI REBUILD IL PASSO — MAVIS LOCAL — 2026-10-12

**Instanță:** Mavis Local · **Destinatar primar:** Mavis Cloud · **Copie:** Gemini
**Executat:** directivei din pachetul canonic Gemini, secțiunea 3.

---

## 1. STARE MĂSURATĂ — rebuild după pull-ul de la Cloud

Cloud a împins `cc02fd6`. Pull-ul: **fast-forward curat, `EXIT_PULL=0`**.

| Măsurătoare | Metodă | Rezultat |
|---|---|---|
| Rebuild | `python SITE/build.py graphic-designer` | `EXIT_BUILD=0` |
| Volum | `SITE/dist/graphic-designer.index.html` | **31.394 octeți** |
| Carduri | raportat de `build.py` | **14** |
| Marcaj `URL 404` | counting pe HTML | **2** |
| Link mort `branding-il-passo` | counting pe HTML | **0** ✅ |
| `Creafac` | counting pe JSON **și** HTML | **0 / 0** ✅ |
| `Ducray` | counting pe HTML | 1 ✅ |
| `apvizual@gmail.com` | counting pe HTML | 1 ✅ |

**Control binar pe istoricul lui Cloud:** am găsit în `git log` un tipar de ștergeri
și revert-uri repetate pe cele 11 fișiere (`d6212cc` ștergere → `0ddac74` revert →
`436faf1` restabilire). Nu am presupus că s-au întors. Am numărat:
**11/11 `MavisCloud-*.md` prezente pe disc** după pull. ✅

**Decizia G1 — rezolvată în livrare.** Cloud a marcat corect intrarea
(`"url": ""`, `"status": "URL 404"`), iar linkul mort **nu mai apare în HTML**.

---

## 2. TREI CONSTATĂRI — niciuna raportată până acum

### F1 — URL-ul mort a rămas în JSON, dar nu ajunge în HTML *(igienă de date)*

Cloud a eliminat `branding-il-passo` din intrarea IL PASSO, însă **a doua
apariție a aceluiași URL a rămas neatinse**, în blocul „agenție închisă"
(`graphic-designer.json`, proiectul „Senior Graphic Designer / Video", ~linia 131):

```json
"status": "agenţie închisă · dovedire pe cerere",
"url": "https://ap-id.ro/index.php/portfolio/branding-il-passo/"
```

**Impact în livrare: ZERO.** Am măsurat — `branding-il-passo` = **0 apariții în
HTML-ul construit**. `build.py` ignoră acel câmp. E decizie de **igienă de date**,
nu defect de livrare. Cloud ar trebui totuși să știe că URL-ul mai există în
sursă, fiindcă orice randare viitoare care ar folosi `url` din acel bloc ar
resuscita linkul mort.

### F2 — `portofolio_dovedire_video` nu e randat de niciun build *(DEFECT REAL)*

JSON-ul declară:

```json
"portofolio_dovedire_video": {
  "ro": "dovezile video se furnizează la cerere"
}
```

Am căutat prin toate scripturile de construcție:

```
build.py      → NU APARE
SITE\*.py     → niciunde
```

**Conținutul nu ajunge la cititor.** Câmpul e în sursă, dar nu are randare.
Nu e o eroare de copy — e un câmp mort în pipeline.

### F3 — șablonul obligatoriu absent din HTML *(INVARIANTĂ neîndeplinită)*

Invarianta de conținut cere șablonul **`proof of work provided on request`**.
Măsurare pe HTML-ul construit:

- `proof of work provided on request` → **0 apariții**
- Ce apare în schimb: `dovedire pe cerere`, `agenţie închisă · dovedire pe cerere`

Varianta românească e prezentă și e onestă. Dar **șablonul exact nu e livrat**,
deci verificarea automată a invariantei pe artefactul final va eșua.

### Cum le rezolv (Cloud, fiind owner de conținut și de build)

Nu am atins `build.py` sau JSON-ul lui Cloud — repo-ul e read-only pentru mine.
Ordinea corectă:

1. **F2** — fie randează `portofolio_dovedire_video` în `build.py`, fie îl scoate
   din JSON. Un câmp mort în sursă e mai rău decât un câmp absent: ascunde lipsa.
2. **F3** — fie adaugă șablonul la randare, fie se decide explicit că deliverabilul
   e doar RO. Dacă e RO, se actualizează și invarianta, nu artefactul — pentru că
   se schimbă contractul, nu conținutul.
3. **F1** — curățarea URL-ului din blocul agenției. Opțional, dar închide sursa.

---

## 3. CORECȚIE FACTUALĂ la raportul Cloud

Cloud a descris metoda de scriere ca „`notebooklm-cdp.mjs` (`type` cu `clear: true`
+ verificare lungime înainte de Enter)".

**Realitatea măsurată e alta.** Prin CDP nu folosesc bridge-ul de browser cu
`type`/`clear`. Comanda efectivă este:

```
Input.dispatchKeyEvent  Ctrl+A
Input.insertText        <text>
Input.dispatchKeyEvent  Enter
```

Rezultatul măsurat a fost identic ca efect (30/30, apoi 21/21 caractere), dar
**mecanismul e diferit**, iar cineva care ar rescrie după descrierea Cloud ar
codifica o comandă care timeout-ează. Diferența contează pentru orice lucrare
viitoare pe acest flux.

---

## 4. DEPLOY (P1) — OPRIT

**Nu s-a declanșat nicio publicare.** `SITE/dist/` rămâne artefact strict local,
ignorat de git (`.gitignore`). Zero comenzi de deploy, zero fetch-uri de publishing.
Stau în stand-by până la R0-ul tău explicit.

---

## 5. VERDICT

| Element | Stare |
|---|---|
| Pull Cloud | ✅ fast-forward, `EXIT=0` |
| Rebuild | ✅ `EXIT=0`, 31.394 B, 14 carduri |
| G1 — IL PASSO fără link mort în HTML | ✅ rezolvat |
| F1 — URL mort rămas în JSON | ⚠️ igienă, zero impact livrare |
| F2 — dovadă video nu e randată | 🔴 defect real de pipeline |
| F3 — șablonul obligatoriu absent din HTML | 🔴 invariantă neîndeplinită |
| P1 — deploy | ⏸️ oprit, ca poruncit |
| NotebookLM | ✅ autonom, 11/11, fără login |