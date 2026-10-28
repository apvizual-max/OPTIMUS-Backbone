# -*- coding: utf-8 -*-
"""Adauga sectiunile noi din sesiunea 2026-10-11 / 2026-10-28 in skilluri.

Regula: succesele se descriu in detaliu, cu reteta reproductibila.
Greselile se mentioneaza intr-o linie fiecare, ca "nu repetati", fara alte
explicatii.
"""
import io
import os
import sys

SK = r"C:\Users\apviz\.minimax\agents\mavis\skills"

SECTIONS = [
    (
        "mavis-git-autonom-skill",
        u"""
## 14. Repo-ul trebuie sa se poata clona — masurat 2026-10-28

`git log` arata perfect chiar si cand repo-ul e imposibil de checkout. Singura
verificare care conteaza e **o clona noua de la zero**:

```powershell
git clone https://github.com/apvizual-max/SENTINEL_PRIME.git _clone_probe
# verdict: exit 0 SI dirty=0 SI fisierele asteptate prezente
```

**Succes, masurat.** `origin/main` continea la radacina un director cu numele
literal `C:\\Users\\apviz\\.minimax-agent\\projects\\SENTINEL_PRIME`. Git refuza
`:` intr-o componenta de nume, deci `read-tree`, `checkout` si orice clona
esueau cu `error: invalid path` / `make_cache_entry failed for path`. Repo-ul
era rupt pentru orice client Windows, inclusiv pentru pipeline. Repararea s-a
facut **prin plumbing**, fara index si fara a atinge istoricul publicat:

1. salveaza toate intrarile arborelui fals in quarantine, cu motiv scris;
2. extrage fisierele care exista DOAR acolo la calea lor reala;
3. reconstruieste arborele radacina: `git ls-tree -z origin/main` minus
   intrarea invalida, apoi `git mktree -z`;
4. `git commit-tree <tree> -p origin/main -m <motiv>` — istoricul ramane liniar;
5. `git update-ref refs/heads/main <commit>` apoi `git read-tree -u --reset HEAD`;
6. **verifica cu o clona noua**, nu cu `git log`.

Dupa reparatie: clona 1408 de fisiere, `dirty=0`, totul prezent.

**Greseli de repetat.**
- Nu verifica sincronizarea doar prin `git log` sau `git status`.
- Nu sterge intrarile suspecte din arbore fara sa le salvezi intai.
- Nu rescrie istoricul publicat si nu folosi force-push.
- Nu folosi `git reset --hard`.
- Nu considera ca "merge-ul a mers" daca `git merge` a scris un avertisment.
""",
    ),
    (
        "popy-project-status-report",
        u"""
## Git and GitHub status belongs in the report (Popy's correction, 2026-10-28)

He asked for a report and the file I wrote had **no Git or GitHub state in it**.
He was right: a status report for a version-controlled project that does not say
where the branch is, what is pushed, and what is not, is incomplete.

**Section 1 (SCOPUL) carries a Git/GitHub table**, measured in the turn the
report is written:

| Field | Example |
|---|---|
| branch | `main` |
| remote URL | `https://github.com/apvizual-max/SENTINEL_PRIME.git` |
| visibility | `PRIVATE` |
| last push (UTC) | `2026-10-10 22:46:32` |
| local commits on main | 13 |
| tracked files | 1.390 |
| **commits not on remote** | **3** |
| ahead / behind | `3 0` |
| dirty files | 5 (and say who wrote them) |
| git identity, hooks | `Sentinel Prime <sentinel.prime@optimus.local>`, hook path, coverage |
| repo disk usage | 15.442 KB |

**Rules that follow from it.**

- The file and the chat message carry the **same** content. The file is the
  deliverable; the chat is a delivery of it, not a different, shorter report.
- Name the file exactly as its H1, character for character, including the em
  dash. Time is `HH-MM`, never `HH:MM` — a colon is illegal in a Windows file
  name, and the same substitution goes in the H1.
- Archive the previous report before writing the new one:
  `raport-archive\\raport-<YYYY-MM-DD_HH-MM>.md`.
- If a figure was not re-measured this turn, it does not go in the table as a
  fact. Write `NOT_MEASURED` or give it its date. A status report that quotes
  yesterday's numbers without saying so is the defect the format exists to
  prevent.
- **A change in state between two reports is itself a report item.** When the
  stale count went from 2 to 10 between 02:15 and 18:45, that belongs in the
  report, plainly, not smoothed over.
""",
    ),
    (
        "mavis-jules-contract-skill",
        u"""
## 8. Masurat in SENTINEL_PRIME, 2026-10-28 — cum arata pipeline-ul de fapt

Aceasta este masurarea, nu Blueprint-ul.

| Fapt | Masurat |
|---|---|
| pipeline-ul | Antigravity CD Engine + `google-labs-jules[bot]` |
| tinta | `main`, direct. **Nu exista ramuri pe remote** |
| CI | **Nu exista.** `gh run list` gol, `.github/workflows` absent |
| ledger | `JULES_HANDOFF.md` in radacina — ce a intrat si cand |
| comituri | ~37 in 3 zile: code health, teste, security, plus starea runtime |
| Jules introduce si defecte | PR #14 a introdus o intrare de arbore cu cale absoluta |

**Succes, masurat — cum se sincronizeaza localul cu pipeline-ul.**

1. `git fetch --all --prune`, apoi compara: `git rev-list --left-right --count origin/main...HEAD`.
2. Verifica, pentru fiecare commit local, ca e in istoricul remote:
   `git merge-base --is-ancestor <commit> origin/main`. Daca toate sunt acolo,
   **nu ai nimic de fuzuit**, doar de materializat.
3. Snapshot inainte de orice operatiune: `git stash push -u` **si** o copie
   fizica in quarantine. Doua cai de recuperare.
4. `git merge --ff-only origin/main` pe arborele curat. Istorie liniara.
5. Restaureaza selectiv: `git checkout 'stash@{0}^3' -- <cai>` pentru
   fisierele neurmarite. `stash@{0}^3` e commitul cu cele neurmarite.
6. **Ruleaza ambele suite, secvential.** Nu exista CI care sa le ruleze.
7. **Verifica cu o clona noua**, nu cu `git log`.

**Foloseste skill-ul `sentinel-cd-pipeline-sync`** din
`SENTINEL_PRIME/07_BACKBONE/skills/` pentru reteta completa, inclusiv
reparatia arborelui cu cale absoluta.

**Greseli de repetat.**
- Nu presupune ca un commit valid inseamna repo clonabil.
- Nu crea ramuri pe remote; `main` e singura ramura activa.
- Nu folosi `stash pop` ca pas implicit.
""",
    ),
    (
        "mavis-sentinel-command-center-skill",
        u"""
## Server-side recipes that are proven (2026-10-11, all measured)

### The static route is an allowlist, not a path handler

`server.ps1` serveste **doua** fisiere: fonturile TTF. Poarta e o cheie
literala dintr-un tabel, comparata explicit, si **doar cheia** ajunge la
`Join-Path`:

```powershell
$ASSETS = @{ 'fonts/jetbrains-mono-400.ttf' = 'font/ttf'
             'fonts/jetbrains-mono-600.ttf' = 'font/ttf' }
$rel = $path.TrimStart('/')
$key = $null
foreach ($k in $ASSETS.Keys) {
  if ([string]::Equals($k, $rel, [StringComparison]::OrdinalIgnoreCase)) { $key = $k; break }
}
if ($key) { $file = Join-Path $ROOT ($key -replace '/', [IO.Path]::DirectorySeparatorChar) }
```

Atacatorul poate **selecta** un nume din tabel; nu poate **compune** o cale.
Verificat cu 33 de forme de atac, inclusiv traversare, traversare codificata,
cai absolute, NUL, ADS `::$DATA`, homoglifuri, cai de 300 de caractere.

### Binaries must be passed through as bytes

`Send-Response` transforma **orice** corp in string si il re-codifica UTF-8.
Un TTF de 21.088 de octeti devenea **37.816 de octeti** corupti, cu HTTP 200
sanatos. Reparatia: `if ($body -is [byte[]]) { ... }` — octetii trec neatins,
stringurile se re-codifica.

### The cross-origin gate on `/api/action`

Un `POST` cross-origin cu `Content-Type: text/plain` executa o actiune si
raspundea 200. E o cerere CORS "simple" — fara preflight, deci browserul nu
intreba. Poarta se pune **inaintea** stratului de actiuni:

```powershell
$origin = $ctx.Request.Headers['Origin']
if ($origin) {
  $allowedOrigins = @("http://127.0.0.1:$Port" "http://localhost:$Port"
                      'http://127.0.0.1:8910' 'http://localhost:8910')
  if ($allowedOrigins -notcontains $origin) { 403; continue }
}
```

**Origin absent e permis intentionat**: niciun browser nu poate fi fortat sa
nu trimita Origin, iar curl, PowerShell si ambele suite trimit none.
Origin literal `null` (iframe sandbox, `file://`) nu e in lista, deci e
refuzat.

**Probe-ul care nu executa nimic**: un id de actiune care nu exista. `403` =
poarta a blocat, `400` = cererea a ajuns in stratul de actiuni. Se poti
repeta oricand, fara efect lateral.

### A staleness bound is a real gate, not a decoration

`mcp_tools_wired` a devenit STALE la 26,5 ore peste o limita de 24, si **doua
verificari au dat rosu** din cauza lui. Remedierea era scrisa chiar in campul
`evidence` al verificarii. Verificarile de prospetime **scad in rosu** cand
ceva nu se reimprospateaza — nu e un defect, e sistemul spunand-o.

**Greseli de repetat.**
- Nu servi binare printr-o functie care le recodifica in string.
- Nu apuna realpath pe cale ceruta de utilizator inainte de a verifica
  apartenenta la allowlist.
- Nu inventa o metoda de a verifica ceva ce nu a fost masurat: masurabilitatea
  se testeaza cu un control, sau nu se afirma.
""",
    ),
]


def main():
    total = 0
    for name, text in SECTIONS:
        path = os.path.join(SK, name, "SKILL.md")
        if not os.path.exists(path):
            print("LIPSA:", path)
            continue
        with io.open(path, "r", encoding="utf-8") as fh:
            body = fh.read()
        if not body.endswith("\n"):
            body += "\n"
        marker = [ln for ln in text.strip().splitlines() if ln.strip()][0]
        if marker in body:
            print("deja prezent, sarit:", name)
            continue
        body += text
        with io.open(path, "w", encoding="utf-8", newline="") as fh:
            fh.write(body)
        print("actualizat:", name, "->", os.path.getsize(path), "B")
        total += 1
    print("actualizate:", total)
    return 0


if __name__ == "__main__":
    sys.exit(main())
