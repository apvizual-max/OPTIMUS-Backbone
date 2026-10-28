# 20_PROTOCOLS / agentic-os — Autonomous Agentic Operating System

**Ce e:** un protocol operațional în formă **executabilă**. Nu e un document
care spune „te oprești în trei situații" — e un program care **refuză** o oprire
fabricată și întoarce cod de ieșire.

Regula care stă la baza: *o regulă spusă nu e legată de nimic*. Proza nu oprește
nimic; un program care întoarce `3`/`4`/`5` oprește.

## Ce conține

| Calea | Rol |
|---|---|
| `core/kernel.js` | funcția de decizie. Refuză opriri fără dovezi, legate de task |
| `core/state.json` | singura sursă de adevăr: scop, sarcini, limite, dovezi |
| `core/heartbeat.js` | kernelul rulează fără mine în conversație; își raportează și lipsa |
| `core/kernel.test.js` · `core/restart.test.js` | 10 + 9 controale; restartul **omoară și repornește**, nu inspectează |
| `core/acceptance.js` | o comandă, cele 10 criterii de acceptare, re-măsurate acum |
| `interactie.js` | poarta pe răspunsul care iese: cifre fără sursă, întrebări la care discul răspunde |
| `wire-boundary.js` | blocaj între procese + capcană de conținut (10 controale) |
| `_gate-run.js` | cele 4 controale ale porții |
| `audit/` | jurnalul interacțiunii + auditorul care recalculează suma din fișier |
| `SKILL-mavis-search-before-write.md` | skill-ul: blochează constante numite fără sursă pe disc |

**Unitatea se mută întreagă.** `core/acceptance.js` calculează
`ROOT = path.join(__dirname, '..')` — urcă un nivel ca să găsească `audit/` și
cele trei porți din rădăcină. Despărțirea pe mai multe foldere ale structurii ar
rupe-o. Deci `agentic-os/` e un folder, nu o dispersie.

## Cum verifici

```powershell
cd C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\20_PROTOCOLS\agentic-os
node core\acceptance.js
```

Trebuie să dea `pass=10 fail=0 total=10`, ieșire **0**. **Rulează-l de trei ori**:
o trecere curată e o mostră, trei consecutive sunt o măsurătoare.

Măsurat 2026-10-28, din acest folder: `pass=10 fail=0`, ieșire 0, de trei ori
consecutive.

## Unde rulează de fapt

| | Locație | Rol |
|---|---|---|
| **Rulare** | `C:\Users\apviz\QWEN_BACKUP\` | task-ul Windows `AgenticOS Heartbeat`, la 5 minute |
| **Versionare** | `20_PROTOCOLS/agentic-os/` (aici) | copia de proiect, în git, cu istoric |

Sunt două copii ale aceluiași motor. **Aceasta nu e locul care bate** — locul
care bate e `QWEN_BACKUP`. Diferențele dintre ele sunt măsurate în
`_DOCS/AGENTIC_OS_HANDOFF.md` §13.

## Ce nu s-a atins

- `C:\Users\apviz\AI_Tools\qwen-system\` — **citit, niciodată scris**. Controlul
  A10 verifică prin sumă, la fiecare rulare, că bytesii sunt cei măsurați.
- `C:\Users\apviz\QWEN_BACKUP\` — nu s-a mutat, nu s-a șters, nu s-a scris în el.
- Hermes, containerele, configurația altora — neatinse.

## Proveniența pin-ului A10

Controlul A10 fixează prin sumă 5 fișiere din `qwen-system`: 1 read-only
(`dashboard/index.html`) și 4 scrise de sesiunea respectivă
(`lib/measured-census.js`, `lib/j-total.js`, `lib/lineage-supervision.js`,
`dashboard/server.js`).

Pin-urile au fost **re-pinate pe 2026-10-09**, când lucrarea legitimă pe
`qwen-system` le-a schimbat pe toate cinci. Înainte de re-pinare, falsificat:
fișierele sunt curate în `git status`, identice octet cu octet cu commit-ul
`3fe5185`, și acel commit e pe `origin/main` al repo-ului
`Qwen-Ecosystem-Dashboard` — deci ancorat în GitHub, nu doar pe această mașină.
Bytesii erau deja comiși și împinși înainte de editare: re-pinformul înregistrează
realitate, nu mută o poartă.
