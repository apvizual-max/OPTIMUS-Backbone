# PROTOCOL DE DENUMIRE LOCAL / CLOUD — Mavis Local — 2026-10-12

**Aditiv. Nu rescrie nimic existent.** Completează `DOCTRINA-CI.md`.

---

## 1. Problema, pe scurt

Două instanțe, un repo comun, aceeași zi. Fără convenție, una suprascrie fișierele
celeilalte și niciuna nu știe.

**Măsurat, 2026-10-12:** repo-ul Cloud avea 39 de commituri și 256 de fișiere.
Dacă am fi scris cu nume generice, prima dintre două scrieri ar fi fost pierdută în
tăcere. Git nu ar fi semnalat nimic — ar fi raportat un commit curat.

**Regula, într-un rând:** *fiecare document nou poartă numele instanței care l-a scris.*

---

## 2. Convenția

| Instanță | Prefix fișiere documentare | Prefix foldere/fișiere de cod |
|---|---|---|
| **Mavis Local** (eu) | `MAVIS-LOCAL-…` / `MavisLocal-…` | `mavis-local-…` |
| **Mavis Cloud** | `MAVIS-CLOUD-…` / `MavisCloud-…` | `mavis-cloud-…` |

**Unde se aplică:**
- `docs/HANDOFF-…` → `docs/HANDOFF-MAVIS-LOCAL-2026-10-12-….md`
- rapoarte → `docs/RAPORT-GEMINI-MAVIS-LOCAL-….md`
- documentație de stare → `docs/STATE-…-MAVIS-LOCAL.md`
- cod nou → `scripts/mavis-local-….ps1`

---

## 3. Cele patru interdicții

1. **Nu suprascrie** un fișier al celeilalte instanțe. **Niciodată.** Nici pentru o
   corectură de un cuvânt.
2. **Corecția se face printr-un fișier nou**, cu numele tău, care îl citește pe celălalt.
3. **Nu redenumește** fișierele celeilalte instanțe. Nimeni nu deține convenția pentru
   ea, și un rename e o suprascriere cu aprobare.
4. **`cloud-ingest/` e read-only** pentru Local, cu **două excepții declarate:**
   adăugarea de fișiere `MAVIS-LOCAL-*` și **scrierea tichetei cozii secundare**
   în formatul de contract (`QUEUE/TASKS-FOR-CLOUD.md`), cerută de contractul
   consumatorului („Local scrie sarcina aici"). Nimic existent nu se atinge —
   ambele excepții sunt **aditive**.

---

## 4. Rezolvarea coliziunii

Dacă două instanțe scriu **același** document logic:

```
docs/HANDOFF-MAVIS-LOCAL-2026-10-12-0700.md
docs/HANDOFF-MAVIS-CLOUD-2026-10-12-0700.md
```

**Ambele rămân.** Nu se alege un câștigător și nu se șterge unul.
Cititorul vede divergența — și **divergența e informație**, nu defect.

---

## 5. De ce nu am ales alternativele

**Alternativa A — un singur document, editat alternativ.** Respinsă: pierderea e tăcută.
Git raportează succes, fișierul e complet, și unul din două lucruri a dispărut.

**Alternativa B — branch per instanță.** Funcționează, dar adaugă un pas de fuziune la
fiecare document. Pentru două instanțe și ~15 documente pe zi, costul depășește riscul.

**Alternativa C — timestamp înainte de titlu.** Funcționează, dar nu spune **cine a
scris**. Convenția numită spune și autorul, și e lizibilă fără context.

---

## 6. Controlul automat

Verificarea e un `grep`, nu o convenție în gura mea:

```bash
git ls-files | grep -viE '(MAVIS-(LOCAL|CLOUD)|Mavis(Local|Cloud))' | grep -iE '(handoff|raport|state)'
```

**Orice ieșire e o încălcare.** Dacă un document nu aparține nimănui,
nu e o excepție — e o lipsă de prefix.

---

## 7. Starea de după acest protocol

| Livrabil | Fișier | Stare |
|---|---|---|
| Endnote către Cloud | `cloud-ingest/MAVIS-CLOUD/docs/ENDNOTE-MAVIS-LOCAL-2026-10-12.md` | ✅ scris, 5.082 B |
| Raport Gemini | `docs/RAPORT-GEMINI-MAVIS-LOCAL-2026-10-12.md` | ✅ scris, 8.349 B |
| Handoff către Cloud | `docs/HANDOFF-TO-CLOUD-MAVIS-LOCAL-2026-10-12.md` | ✅ scris, 6.630 B |
| Protocol | `docs/PROTOCOL-DENUMIRE-LOCAL-CLOUD.md` | ✅ acest fișier |

---

*2026-10-12 · Mavis Local · protocol aditiv · nu rescrie, completează*

---

## 8. Extinderea la canalul Drive — 2026-10-27

**Aditiv, ca tot restul acestui protocol.** Regulile de mai sus rămân
valabile; aici se spune **cine scrie ce**, în canalul primar nou.

### 8.1 Convenția se extinde, nu se înlocuiește

| Instanță | În `BRIDGE-DRIVE/` |
|---|---|
| **Mavis Local** | `MAVIS-LOCAL-…` pentru documente, `mavis-local-…` pentru cod |
| **Mavis Cloud** | `MAVIS-CLOUD-…` pentru documente, `mavis-cloud-…` pentru cod |

Cele patru interdicții din §3 **se aplică identic**: niciun fișier al
celeilalte instanțe nu e suprascris, corectiile se fac prin fișiere noi,
nimic nu e redenumit.

### 8.2 `TASK_ID` — singurul identificator comun

Ambele canale folosesc **același `TASK_ID`**. Nu e o convenție de
nume, e o cheie de urmărire: un tichet poate exista simultan în
`QUEUE/TASKS-FOR-CLOUD.md` (secundar) și în
`BRIDGE-DRIVE/TASKURI-PENTRU-CLOUD.md` (primar), și se recunoaște ca
același lucru.

```
TASK_ID: MAVIS-LOCAL-2026-10-27-001
```

### 8.3 Unde se scrie cine

| Direcție | Canal primar (Drive) | Canal secundar (GitHub) |
|---|---|---|
| Local → Cloud | `BRIDGE-DRIVE/TASKURI-PENTRU-CLOUD.md` | `QUEUE/TASKS-FOR-CLOUD.md` |
| Cloud → Local | `BRIDGE-DRIVE/INTRARI-CLOUD/` | `cloud-ingest/` (**read-only** pentru conținut; devine și copie de lucru a livrării cozii) |
| Consumat, închis | `BRIDGE-DRIVE/ISTORIC/` | `QUEUE/DONE/` (marcat `[x]`) |
| Liber, cu cuvintele lui Popy | `BRIDGE-DRIVE/INTENTII.md` | `docs/INTENTII.md` |

### 8.4 Precedența la coliziune

Dacă același `TASK_ID` apare în ambele canale cu conținut diferit,
**divergența e informație, nu defect** — ca în §4. Se scrie un fișier
nou, `MAVIS-LOCAL-…`, care citește ambele și spune care e de citit. Nu se
alege un câștigător și nu se șterge unul.

### 8.5 Controlul automat, extins

Verificarea pentru fișierele fără proprietar rămâne cea din §6, dar se
aplică și pe folderul Drive:

```bash
git ls-files | grep -viE '(MAVIS-(LOCAL|CLOUD)|Mavis(Local|Cloud))' | grep -iE '(handoff|raport|state)'
```

**Orice ieșire e o încălcare.** Regula e aceeași pentru `BRIDGE-DRIVE/`:
un document care nu poartă numele instanței care l-a scris nu aparține
nimănui.

---

*2026-10-27 · Mavis Local · extindere aditivă pentru canalul Drive*