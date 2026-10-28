# Arhivă memorie agent

**De ce:** optimizarea memoriei fără arhivarea a ce ai tăiat se cheamă **EROARE**,
nu optimizare. Trunchierea memoriei pierde detalii care uneori contează — și
nu se vede că le-ai pierdut decât peste săptămâni, când ai nevoie de ele.

**Regula (POPY, 2026-10-24):** cât timp versiunea precedentă e păstrată aici,
în repo, optimizarea e validă. Altfel e trunchiere.

**Procedura completă:** `docs/PROCEDURA-OPTIMIZARE-MEMORIE.md`

## Convenția

```
docs/arhiva/memorie/
  README.md                                  ← suntem aici
  <AAAA-LL-ZZ>-<etichetă>/
    MEMORY.md                                ← stratul HOT, pre-tăiere
    topics/<nume>.md                        ← topicurile, pre-editare/ștergere
    MANIFEST.md                              ← ce s-a tăiat, unde e acum, de ce
```

- Etichete uzuale: `pre-optimizare`, `snapshots-automat`, `post-curatare`.
- **Append-only.** Nu se șterge nimic din arhivă.
- Fiecare snapshot include `sha256` al fiecărui fișier → se poate verifica
  că nu s-a modificat ceva.

## Cum se scrie

```bash
# din fișiere
node mavis-tools/memory-snapshot.js --from <dir> --label <etichetă>

# din stdin (JSON: { "MEMORY.md": "...", "topics": { "nume.md": "..." } })
cat snapshot.json | node mavis-tools/memory-snapshot.js --label <etichetă>

# R0 înainte de orice tăiere: există arhiva?
node mavis-tools/memory-snapshot.js --verify <etichetă>   # exit 1 dacă nu

# listă
node mavis-tools/memory-snapshot.js --list
```

## Ordinea obligatorie

```
SNAPSHOT → MANIFEST → COMMIT → PUSH → APOI taie din memorie → COMMIT → PUSH
```

Push-ul arhivei **înainte** de tăiere. Fără push, tăierea nu se face.

## Atenție la secrete

Repo-ul e **public**. Arhiva memoriei conține ce a fost în memorie. Deci
**mai întâi se elimină secretele din memorie, apoi se arhivează** — altfel
tăiatul dintr-o cheie ajunge în repo public. Secretul nu ajunge niciodată în
arhivă.
