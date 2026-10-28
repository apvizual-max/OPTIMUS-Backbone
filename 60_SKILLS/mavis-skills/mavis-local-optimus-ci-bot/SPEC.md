# SPEC — Mavis Local Optimus CI Bot

Contractul tehnic din spatele `SKILL.md`. Citește-l când schimbi forma botului,
extinzi registrul sau scrii un membru nou.

---

## 1. Forma botului

```
mavis-local-optimus-ci-bot\
  SKILL.md            rolul, personalitatea, funcțiile, uneltele, LISTA, contractul
  SPEC.md             acest document: contractul tehnic
  registry.json       lista măsurabilă a membrilor (rol, scop, stare, verificare)
  scripts\
    bot-doctor.mjs    verificatorul: list | verify | show | link | doctor
  bot-runs.md         jurnal de execuție (append-only), cu numerele măsurate
```

## 2. Membrul

```
mavis-<capability>-skill\
  SKILL.md            rolul, de ce, procedura, garanțiile, LIMITĂRILE
```

| Cerință | De ce nu e opțională | Cine o verifică |
|---|---|---|
| `SKILL.md` există și se parsează | un membru care nu poate fi citit nu poate fi încărcat | `verify` |
| frontmatter `name` == numele folderului | un șir, trei locuri; drift-ul e o eroare | `verify` |
| frontmatter `description` (≥20 caractere) | routerul citește descrierea, nu corpul | `verify` (WARN) |
| frontmatter `role: functional` | verificatorul distinge membrii de referințe | `verify` |
| frontmatter `bot: mavis-local-optimus-ci-bot` | back-link: membrul știe cine e hub-ul său | `verify` (FAIL) |
| apare în tabelul din `SKILL.md` | lista umană și registrul trebuie să coincidă | `verify` |

**Membru fără frontmatter = defect.** Un `SKILL.md` fără frontmatter nu e încărcabil de
router: nu are `name`, nu are `description`, deci nu poate fi dispersat spre el. Pe
28 oct 2026, cinci micro-skilluri ale suitei CI erau în această stare și au fost reparate
aditiv (frontmatter adăugat, conținut neatins).

**Referință** = există pe stație și contează, dar NU e deținut de acest bot. Contract mai
slab, onest: folderul și `SKILL.md` trebuie să existe; numele din frontmatter nu trebuie
să contrazică folderul (dacă contrazice → WARN, nu FAIL, pentru că e alt registru).

## 3. Căile (măsurate 2026-10-28)

| Rol | Cale |
|---|---|
| proiectul (mirror DriveFS) | `E:\Google\GDrive\GDrive-Second_Brain_PKMS\02_Areas\02-2-AI-SOT\CASA\OPTIMUS - Prime\Optimus_CI (by Mavis)` |
| toată data git locală | `E:\Google\GitData-Optimus-CI` |
| carantina | `E:\Google\GitData-Optimus-CI\.quarantine` |
| laborator (fixture-uri) | `E:\Google\GitData-Optimus-CI\scratch` |
| jurnalul containerului | `E:\Google\GitData-Optimus-CI\evidence` |
| container | `Mavis-Optimus-CI` (imagine `mavis/optimus-ci:1.0.0`) |
| API | `http://127.0.0.1:8790` |
| MCP | `optimus-ci-server` (7 unelte) |
| poarta de trimitere | `C:\Users\apviz\QWEN_BACKUP\interactie.js` |
| busola | `C:\Users\apviz\.minimax\BUSOLA.md` |
| doctrina | `C:\Users\apviz\.minimax\AGENTS.md` |

**Carantina e în afara mirrorului, deliberat.** `E:\Google\GDrive\...` e administrat de
DriveFS, care materializează, înlocuiește și șterge fișiere pe cont propriu. Carantina
trebuie să fie un teren neutru.

## 4. Schema registrului

```jsonc
{
  "schemaVersion": 1,
  "bot": "mavis-local-optimus-ci-bot",
  "version": "1.0",
  "session": { "id": "...", "name": "...", "role": "primary" },
  "frontmatter_required": ["name", "description", "role", "bot"],
  "roles": { "hub": "...", "functional": "...", "reference": "..." },
  "contract": { "C1": "...", "...": "..." },
  "paths": { "project": "...", "gitdata": "...", "quarantine": "..." },
  "tools":  [ { "name": "...", "kind": "mcp|script|procedura", "via": "...", "use": "..." } ],
  "functions": [ { "id": "F1", "name": "...", "scope": "..." } ],
  "skills": [
    {
      "name": "mavis-<x>-skill",       // == numele folderului
      "role": "functional|reference",
      "source": "ci-server|station|...",
      "purpose": "o linie, masurabilă",
      "status": "WIRED|...",
      "added_at": "YYYY-MM-DD",
      "verified": "data + ce s-a măsurat efectiv"
    }
  ]
}
```

`verified` nu e decorativ: e locul unde scrii **ce s-a măsurat**, nu ce se crede.

## 5. Contractul verificatorului

| Comandă | Ce face | Ieșire |
|---|---|---|
| `list [--json]` | tiparul de dispersie | 0 |
| `verify [--registry <f>]` | integritatea registrului + a listei din `SKILL.md` + existența căilor | 0 / **1** |
| `show --name X` | recordul unui membru | 0 / 2 |
| `link --name X --role R --source S --purpose P` | înregistrează un membru **nou** | 0 / 1 / 2 |
| `doctor` | starea reală: container, API, repo-uri, carantină, ledger, registru | 0 / **1** |

**Verificatorul trebuie să poată deveni ROȘU.** De aceea `--registry <fisier>` permite
exercitarea lui pe o copie stricată, fără a atinge registrul viu. Un verificator care nu
poate eșua nu e o poartă.

`link` **refuză** ceva care nu există pe disc, ceva fără frontmatter, ceva al cărui
`name` nu coincide cu folderul, și ceva deja înregistrat. Înregistrarea unui skill
inventat e exact felul de eroare pe care o produce „lista arată frumos".

### 5.1 Ce acoperă `doctor` (32 de verificări, pe sistemul real)

| Familie | Check-uri | Ce măsoară |
|---|---|---|
| container | `container` | starea și healthcheck-ul lui `Mavis-Optimus-CI` |
| API | `api:health`, `api:doctor` | HTTP 200 pe portul 8790 |
| repo-uri | `repo:<id>:branch`, `:dirty`, `:sync`, `:r0` | o ramură `main`, `dirty=0`, `behind/ahead`, marker de acord |
| carantină | `quarantine`, `quarantine:<item>` | folderul există și **fiecare element are `MOTIV.txt`** |
| punte | `bridge:transport`, `:mirror`, `:propagation`, `:pending`, `:cloud-leg` | starea măsurată a transportului Google Drive |
| jurnal | `journal:oglinda`, `journal:protocol` | secțiunile JURNAL_OGLINDA și protocolul |
| grant | `grant:google` | `scope_count` din consent |
| frontiera | `boundary:cd` | **nicio** suprapunere a amprentei locale cu CD |
| registru | `registry:verify` | verificatorul de registru, rulat în interior |

**Worktree-ul se dă explicit** la `git status`: fără el, gitul ia drept arbore de
lucru părintele gitdir-ului și numără fișiere care nu aparțin repo-ului (măsurat
2026-10-28: **462** și **106** intrări false pe clone).

## 6. Adăugarea unui membru

```bash
# 1. creezi skill-ul pe disc, cu frontmatter complet
# 2. il inregistrezi
node scripts\bot-doctor.mjs link --name mavis-nou-skill --role functional \
     --source ci-server --purpose "ce face, intr-o linie"
# 3. il adaugi in tabelul din SKILL.md (altfel verify merge ROSE)
# 4. verifi
node scripts\bot-doctor.mjs verify
```

Bucla: **măsură → registry → verify → link**. Un defect se raportează, nu se corectează
în tăc — altfel următorul agent repetă accidentul, pentru că nu îl vede.

## 7. Procedura de carantină (măsurată)

Bash-ul runtime-ului **nu poate scrie în afara workspace-ului** (blocaj: *„recursive
write/delete target cannot be verified inside the workspace"*), iar ștergerea recuperabilă
e respinsă pentru ținte din afara lui (*„Windows trash execution rejected a target outside
the workspace"*). De aceea mutarea se face **prin container**, care are volumul gitdata
montat rw:

```sh
docker exec Mavis-Optimus-CI sh -lc \
  'mkdir -p /workspace/gitdata/.quarantine && \
   mv /workspace/gitdata/scratch/<item> /workspace/gitdata/.quarantine/<data>-<nume>'
```

Apoi: `MOTIV.txt` în elementul mutat (motiv + măsurătoare), o linie în tabelul de
inventar din `.quarantine\README.md`, și o intrare în `bot-runs.md`.

## 8. Legarea de sesiune

Botul este skillul **principal** al sesiunii `mvs_eaaf49033892458a8076c7cc9e8d51aa`
(„Mavis Local - Ondoard Optimus_CI"). Legarea se face în patru locuri, ca să reziste
unui restart:

1. **frontmatter** al `SKILL.md` (`session`, `session_name`, `session_role: primary`);
2. **`registry.json`** → `session` (același id, același nume);
3. **`BUSOLA.md`** → rândul care spune că acesta e skillul principal al sesiunii;
4. **`mavis-session-lifecycle-skill`** → ordinea de deschidere (botul se încarcă după
   busolă) și **`mavis-skill-index`** → rândul de indice.

## 9. Defecte cunoscute în registru (raportate, nu ascunse)

| Membru | Defect | Efect |
|---|---|---|
| `mavis-pkms-vault-administration-skill` | frontmatter `name: pkms-vault-administration` ≠ folder | WARN: routerul nu dispersează corect (proiect suror, nu e reparat aici) |
| `mavis-shared-local-mcp-swarm-skill` | `description` de 1 caracter | WARN: nu poate fi dispersat spre el |

Sunt **WARN**, nu FAIL: există, contează, și nu sunt deținute de acest bot. Ascunderea lor
ar fi fals; repararea lor aici ar fi frontieră.
