# PROCEDURĂ — Optimizarea memoriei de agent (arhivare obligatorie înainte de tăiere)

**Regulă, formulată de POPY, 2026-10-24:**

> Optimizarea memoriei **fără arhivarea a ce ai tăiat** se cheamă **EROARE**,
> nu optimizare. Cât timp versiunea precedentă e păstrată undeva în **repo,
> în secțiunea arhivă**, atunci e optimizare. Altfel e trunchiere de memorie și
> pierdere de context — și așa se pierd detalii care uneori contează.

**Motivul practic:** în sesiunea din 2026-10-24 am tăiat ~13KB din memoria de
agent fără să arhivez nimic în repo. Detalii care **conteau** (de ce era
blocat Gmail, cum arată defectul filtrelor, ce erau cele 4 chei Google, ce
spunea topicul șters) au dispărut din memorie și din topicuri. Pierderea nu se
vede imediat — se vede peste 3 săptămâni, când ai nevoie de context și nu-l ai.
Arhiva e plătită acum, ca să nu plătești atunci.

---

## Fluxul, exact. Fără excepții.

```
1. SNAPSHOT   →  memorie curentă → docs/arhiva/memorie/<DATA>-<etichetă>/
2. MANIFEST   →  ce s-a tăiat, unde e acum, de ce
3. COMMIT     →  arhiva
4. PUSH       →  main          ←  arhiva e în repo ACUM
5. TAIE       →  abia acum modifici memoria
6. COMMIT     →  memoria optimizată
7. PUSH       →  main
```

**Punctul 4 e obligatoriu înainte de punctul 5.** Dacă push-ul eșuează, **nu
 tai nimic** — o tăiere fără arhivă în repo nu se poate anula.

**Procesul automat e interzis înaintea arhivei:** prima rulare a unui
optimizer de memorie *trece prin backup*. Dacă optimizerul e capabil să taie
fără să verifice existența arhivei, e o armă care se împușcă singură.

## Formatul arhivei

```
docs/arhiva/memorie/
  README.md                                  ← convenția
  2026-10-24-pre-optimizare/
    MEMORY.md                                ← stratul HOT, pre-tăiere
    topics/
      <topic>.md                             ← topicurile, pre-tăiere
    MANIFEST.md                              ← ce s-a tăiat, unde, de ce
```

- **`<DATA>-<etichetă>/`** — data + motiv: `2026-10-24-pre-optimizare`,
  `2026-11-02-post-curatare`, `2026-11-09-snapshots-automat`.
- **`MEMORY.md`** — copie **exactă**, byte cu byte, a stratului HOT înainte de
  orice tăiere.
- **`topics/`** — copiile topicurilor **înainte** de orice editare/ștergere.
  Un topic șters se arhivează **înainte** de `memory_topic_delete`.
- **`MANIFEST.md`** — tabelul „tăiat → unde e acum". Fără manifest, arhiva e
  o grămadă de fișiere fără hartă.

**Nu se șterge niciodată din arhivă.** Arhiva e append-only.

## Automatizarea

### 1. Scriptul: `mavis-tools/memory-snapshot.js`

```bash
# snapshot din fișiere (calea normală, la Local sau în sandbox cu fixture)
node mavis-tools/memory-snapshot.js --from <dir> --label <etichetă>

# snapshot din stdin (JSON cu { MEMORY.md, topics: {...} })
cat snapshot.json | node mavis-tools/memory-snapshot.js --label <etichetă>

# verifică: există arhivă pentru o etichetă? (R0 înainte de tăiere)
node mavis-tools/memory-snapshot.js --verify <etichetă>

# listă arhivele
node mavis-tools/memory-snapshot.js --list
```

Scrie în `docs/arhiva/memorie/<DATA>-<etichetă>/`, cu `MANIFEST.md` generat
automat (dimensiuni, hash-uri SHA-256 ale fiecărui fișier, timestamp) și
`--verify` care întoarce exit code ≠ 0 dacă arhiva lipsește.

### 2. Task programat: snapshot săptămânal

Task cloud, rulează **duminica la 23:00** (ora Europe/Bucharest), id
`455764418027683`: citește memoria curentă, scrie snapshotul în repo, comitează,
împinge.

**Nu taie nimic.** Doar arhivează. Optimizarea e o decizie de sesiune, cu
opțional R0 de la POPY — nu ceva ce face un cron în tăcere.

> **Cronurile Cloud și Local sunt în locuri diferite.** Taskul ăsta e în
> **cloud** → se vede pe platforma online, nu în interfața Local. POPY trebuie
> să știe unde e.

### 3. R0 înainte de push (din `mavis-cloud-git-auto-commit-r0-push`)

```bash
node --check mavis-tools/memory-snapshot.js
git diff --cached --name-only | grep -iE "secret|token|credential"   # trebuie gol
git status --porcelain                                              # trebuie gol după commit
```

**Regula pentru secrete rămâne:** arhiva memoriei poate conține ce a fost
scris în memorie. **Tăiatul din memorie înainte de arhivare = secret în repo
public.** Deci: **mai întâi se elimină secretele din memorie, apoi se
arhivează.** Secretul nu ajunge niciodată în arhivă.

## Ce e permis și ce nu

| Acțiune | Permis? |
|---|---|
| Comprimare (mai multe detalii → topic) | ✅ |
| Mutare din HOT în topic | ✅ |
| Ștergere de topic redundant, **cu arhivare înainte** | ✅ |
| Ștergere de topic fără arhivare | ❌ **EROARE** |
| Tăiere de HOT fără arhivare | ❌ **EROARE** |
| Eliminare de secret din memorie înainte de arhivare | ✅ (dar nu se scrie niciodată în repo) |

## Legături

- Arhiva: `docs/arhiva/memorie/`
- Script: `mavis-tools/memory-snapshot.js`
- Regulile generale de repo: `AGENTS.md` (Regula 2 — comit + push fără aprobare)
- Skill git: `.skills/mavis-cloud-git-auto-commit-r0-push/`
- Memorie agent: topic `memory-maintenance-tooling`
