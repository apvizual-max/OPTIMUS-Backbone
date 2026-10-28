---
name: sentinel-cd-pipeline-sync
description: "Sincronizarea SENTINEL_PRIME cu pipeline-ul de dezvoltare continua (Jules + Antigravity CD Engine) care scrie direct in main. Se incarca cand main-ul local si origin/main difera, cand o clona nu se poate checkout, cand pipeline-ul a adaugat commituri pe care nu le ai local, sau inainte de a inchide o sesiune cu proiectul. Contine rețeta reproductibila pentru repararea arborelui cu cale absoluta, care rupe orice clona pe Windows, si regulile de pastrare a istoricului liniar."
parent: mavis-sentinel-prime-on-minimax-skill
source_of_truth: SENTINEL_PRIME/07_BACKBONE/skills/
---

# Sincronizare cu pipeline-ul CD (Jules + Antigravity)

## 0. Cine scrie in acest repo, masurat

| Actor | Scrie ce | Unde |
|---|---|---|
| **Antigravity CD Engine** | starea runtime + commituri de sincronizare, direct in `main` | remote `main` |
| **google-labs-jules[bot]** | PR-uri de code health, teste, security — merge-uite direct in `main` | remote `main` |
| **Mavis (eu)** | lucrurul de produs: feature, reparatii, audit, handoff | `main` |

**Invariantul pipeline-ului: `main` este singura ramura activa.** Nu crea ramuri
pe remote. Ledgerul lui este `JULES_HANDOFF.md` in radacina — citeste-l inainte
sa schimbi ceva, el arata ce a intrat si cand.

Nu exista GitHub Actions pe acest repo: `gh run list` e gol, `.github/workflows`
nu exista. Pipeline-ul ruleaza in afara GitHub. Deci **nu exista CI care sa-ti
spuna ce a trecut** — trebuie sa rulezi tu suitele.

## 1. Regula de aur: verifica DOAR cu o clona noua

Un commit poate fi perfect valid si totusi **imposibil de checkout** pe Windows.
Verificarea care conteaza nu e `git log`, e o clona noua:

```powershell
git clone https://github.com/apvizual-max/SENTINEL_PRIME.git _clone_probe
# verdict: exit 0 SI dirty=0 SI fisierele asteptate prezente
```

Daca o clona nu se poate face, **repo-ul e rupt pentru toata lumea**, chiar daca
`git log` arata totul bine. Asta s-a intamplat: vezi sectiunea 3.

## 2. Sincronizarea obisnuita, cand arborele e sanatos

Localul e de obicei **strict in urma** de origin/main (pipeline-ul mergeaza
direct, tu nu faci push la fiecare schimbare). Pasii:

1. **Snapshot inainte de orice operatiune git.** Doua cai independente de
   recuperare, pentru ca un stash se poate pierde si un backup se poate uita:
   ```powershell
   git stash push -u -m "pre-sync <data>: state local-only"
   Copy-Item <continutul local-only> <quarantine> -Recurse -Force   # si fizic
   ```
2. **Traverseaza istoricul.** `git merge-base --is-ancestor <commit> origin/main`
   pentru fiecare commit local. Daca toate sunt in origin/main, nu ai nimic de
   fuzuit — doar de materializat.
3. **`git merge --ff-only origin/main`** dupa ce arborele e curat. Nu folosi
   `--rebase` si nu rescrie istoricul publicat: o ramura unica, istorica liniara.
4. **Restaurare selectiva** din stash: `git checkout 'stash@{0}^3' -- <cai>`
   pentru fisierele neurmarite. `stash@{0}^3` este commitul cu cele neurmarite;
   `stash@{0}` tine si modificarile urmarite. Restaurare selectiva, nu
   `stash pop` — pop-ul intra in conflict pe fisierele de runtime, pe care
   daemonul le rescrie oricum.
5. **Ruleaza ambele suite, secvential.** Nu niciodata concurrent.

## 3. Defectul care a rupt repo-ul: intrare de arbore cu cale absoluta

**Cum arata.** `origin/main` continea, la radacina, un director cu numele
literal:

```
"C:\\Users\\apviz\\.minimax-agent\\projects\\Mavis-Optimus-Dashboard\\SENTINEL_PRIME"
```

Git **refuza `:`** intr-o componenta de nume. Deci `read-tree`, `checkout` si
orice clona esueau cu:

```
error: invalid path 'C:\Users\...\SENTINEL_PRIME/08_SELF_IMPROVEMENT/test_sentinel.md'
fatal: make_cache_entry failed for path ...
```

**Cum se recunoaste.** Simptomele sunt insidiosite si NU seamana cu o problema de
repos:

| Simptom | De ce pacaleste |
|---|---|
| `git log` arata perfect | istoricul e valid; problema e in arbore, nu in istoric |
| `git status` merge | statusul foloseste indexul existent, nu scrie arbore nou |
| `git merge --ff-only` zice "untracked working tree file would be overwritten" | fisierele SUNT urmarite, dar git nu le poate indexa |
| `git clone` zice "Clone succeeded, but checkout failed" | clona se face, arborele nu |

**Cum se confirma, ieftin.** Compara arborele remote cu cel local, si cauta
intrari cu `:` sau cu separator de cale:

```powershell
git ls-tree -r --name-only origin/main | Select-String -Pattern ':'
# sau, la radacina:
git ls-tree origin/main | Select-String -Pattern 'C:'
```

**Cine a introdus.** `git log --diff-filter=A --name-only origin/main` arata
comitul exact. In acest caz: `3b3f9dd` — un PR code-health al lui Jules. Un
`git add` cu cale absoluta (sau un tool care a primit cale absoluta) creeaza
intrare de arbore cu nume de director.

## 4. Reparatia, prin plumbing, fara a atinge indexul

`read-tree` si `checkout` refuza arborele cu intrari invalide — de aceea
reparatia se face **prin construirea unui arbore nou**, nu prin indexare.

```python
# 1. salveaza tot ce e in arborele fals, inainte de orice scriere
# 2. extrage fisierele care exista DOAR acolo, la calea lor reala
# 3. reconstruieste arborele radacina fara intrarea invalida
raw  = git("ls-tree", "-z", "origin/main")     # NUL-separated, fara quoting
kept = [e for e in raw.split(b"\0")
        if e and not e.split(b"\t",1)[1].startswith(PREFIX)]
tree = git("mktree", "-z", input=b"\0".join(kept) + b"\0")
# 4. creeaza commitul de reparatie, ca parinte origin/main
fix  = git("commit-tree", tree, "-p", origin_main, "-m", msg)
```

Apoi, in repo:

```powershell
git update-ref -m "reparatie: elimina directorul cu cale absoluta" refs/heads/main $fix
git read-tree -u --reset HEAD      # materializeaza indexul + arborele de lucru
```

**De ce plumbing si nu `git rm`:** calea invalida nu poate fi indexata, deci nu
poate fi nici eliminata prin index. Se scoate din arbore.

**De ce `commit-tree` cu parintele `origin/main`:** istoricul ramane **liniar**.
Niciun merge-commit, nicio rescriere, niciun force-push. Commitul de reparatie
e pur si simplu urmatorul lui `origin/main`.

**Ce se face cu continutul din arborele fals** — masurat in acest caz:
2 intrari identice cu calea reala, 9 snapshoturi mai vechi ale fisierelor de
stare runtime, 1 fisier care exista **DOAR** acolo
(`09_LOGS/scraped/example_com_20261024_060614.json`) — **extras la calea lui
reala**. Restul, salvat in quarantine cu motiv scris. **Nu sterge nimic.**

## 5. Verificarea finala, obligatorie

Nu te bazai pe faptul ca ai vazut `git push` reusit. Verifica:

```powershell
$local  = git rev-parse main
$remote = ((git ls-remote origin refs/heads/main) -split '\s+')[0]
$local -eq $remote          # singura verificare care conteaza pentru push
```

Apoi **clona noua de proba**, de la zero, si verifica `dirty=0` si ca fisierele
asteptate exista acolo. Daca o clona noua nu se poate face, nu ai terminat.

**Legat obligatoriu de repository.** In SENTINEL_PRIME, cwd-ul sesiunii a fost
`...\projects`, care e el insusi un repository git (OPTIMUS-Backbone), iar
proiectul lucrat era `...\projects\SENTINEL_PRIME` — un repository **nested**.
`git ls-remote origin refs/heads/main` rula **fara `-C`** a interogat remote-ul
repository-ului **parinte** si a returnat un SHA care nu exista in
SENTINEL_PRIME. Citit ca "pipeline-ul a impus ceva nou intre doua verificari",
era o iminenta de panica bazata pe un repository strain.

Regula: orice comanda git care raspunde despre un repository **neclase** se
leaga explicit, iar inainte de a intelesi un SHA neasteptat, verifica ce remote
exista:

```powershell
git -C $repo remote -v
git -C $repo ls-remote origin refs/heads/main
```

La fel pentru starea unui **alt arbore** (o clona plasata in interiorul
proiectului): `git -C <clona> status --porcelain`.

## 6. Verificatorul executabil: `scripts\verify-remote-clone.ps1`

Regula de la sectiunile 1 si 5 are acum o forma care se ruleaza. Dupa fiecare push
al pipeline-ului (Jules + Antigravity CD Engine):

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\verify-remote-clone.ps1 `
    -ExpectFiles '14_HANDOFF\10_PRIMING_PROMPT.md,README.md'
```

Ce masoara - fiecare verificare raporteaza valoarea masurata, nu doar un verdict:

| Verificare | Ce inseamna | Asteptat |
|---|---|---|
| `remote_main_sha` | SHA-ul lui `refs/heads/main` pe remote, citit cu `ls-remote` | nevid |
| `remote_branches` | cate ramuri are remote-ul | 1, anume `main` |
| `behind_ahead` | remote-ul fata de HEAD-ul local | `0/0` cand e sincronizat |
| `invalid_tree_entries` | cate intrari de arbore contin `:` | **0** |
| `clone_exit` | codul de iesire al unei clone NOI, de la zero | 0 |
| `clone_head_sha` | HEAD-ul clonei noi | egal cu SHA-ul remote-ului |
| `clone_dirty` | `git status --porcelain` in clona noua | **0** |
| `clone_branches` | ramurile locale din clona noua | doar `main` |
| `clone_tracked_files` | cate fisiere urmarite sunt in clona noua | > 0 |
| `expect_files_missing` | cate din fisierele cerute lipsesc | **0** |

Verdictul se citeste din ultima linie: `VERDICT=PASS` sau `VERDICT=FAIL`, urmat de
`FAILURES=<lista>`. Codul de iesire: 0 = PASS, 2 = FAIL.

Scriptul **nu sterge nimic** si nu atinge arborele de lucru al repo-ului: nu muta
nicio referinta si nu scrie niciun fisier in repository. Singurul lucru pe care il
scrie este o clona de proba in `%TEMP%`, a carei cale o afiseaza in
`PROBE_CLONE=`. Curata manual, cand nu mai ai nevoie de dovada.

### Controlul falsificator

Un check care nu poate pici nu e un check. `scripts\make-broken-tree-control.py`
construieste, la cerere, un repository cu intrarea de arbore cu cale absoluta -
defectul real din 2026-10-28:

```powershell
python scripts\make-broken-tree-control.py
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\verify-remote-clone.ps1 `
    -Repo "$env:TEMP\sentinel-broken-tree-control" `
    -RemoteUrl "$env:TEMP\sentinel-broken-tree-control"
# asteptat: VERDICT=FAIL, invalid_tree_entries 1, clone_exit 128,
#   "error: invalid path 'C:\Users\...' - fatal: unable to checkout working tree"
```

Masurat pe 2026-10-28, pe aceeasi suma: controlul -> `VERDICT=FAIL` (exit 2),
repository-ul real -> `VERDICT=PASS` (exit 0).

Verificatorul este testat in ambele sensuri de faza `cd_clone_verify` din
`08_SELF_IMPROVEMENT\test_deployment.py`: controlul trebuie BLOCAT, iar
repository-ul real trebuie ACCEPTAT. O faza care poate trece doar pica, sau doar
trece, nu e o faza.

## 7. Greseli de repetat

- Nu verifica sincronizarea doar prin `git log` sau `git status`.
- Nu folosi `git reset --hard` si nu rescrie istoricul publicat.
- Nu face `stash pop` ca pas implicit, cand poate intra in conflict pe fisierele
  de runtime.
- Nu sterge intrarile suspecte din arborele fals fara sa le salvezi intai.
- Nu considera ca "merge-ul a mers" daca `git merge` a scris un avertisment.
- Nu folosi `git clone` ca test al starii repo-ului fara sa verifici si
  fisierele, nu doar exit code-ul.
- Nu rula comenzi git "din directorul curent" cand proiectul lucrat e altul:
  leaga-le cu `-C <repo>` si verifica `remote -v` inainte de a interpreta un
  SHA strain drept "push al pipeline-ului".
- Nu tine material de lucru temporar (mesaje de commit, scripturi) in radacina
  unui repository pe care il comiti cu `git add -A`; citeste lista de intrari
  cu `git diff --cached --name-status` inainte de commit.
- Nu numi o functie PowerShell ca un executabil aflat pe PATH. `function Git`
  umbreaza `git.exe`, iar apelul se autoapeleaza la infinit - masurat:
  `CallDepthOverflow`. Numele sigur: `Invoke-Native`.
- Nu confunda "un tool nativ a scris pe stderr" cu "a esuat". Cu
  `$ErrorActionPreference='Stop'`, un `git` care doar avertizeaza ridica o eroare
  terminanta si iti ascunde diagnosticul pe care voiai sa-l vezi. Captureaza
  stderr-ul intr-un string si citeste codul de iesire.
- Cu `powershell -File`, o lista de argumente separate NU se leaga la un parametru
  `[string[]]`: primeste un singur string cu virgule intre ele. Accepta un string
  separat prin virgule si descompune-l in interiorul scriptului.
- La parsarea unui SHA nu cere whitespace dupa el: `git rev-parse HEAD` afiseaza
  SHA-ul gol. Ancoreaza regexul la inceputul liniei: `^\s*([0-9a-f]{40})\b`.
- Nu itera peste rezultatul unui pipeline cu `Where-Object` fara sa-l convertesti
  in array: pe un singur element, PowerShell intoarce un scalar, iar `$x[0]` pe un
  scalar de tip string intoarce primul CARACTER, nu primul element. Masurat:
  SHA-ul parsat ca `"b"`.

## 8. Legaturi

- Skill-ul sursa al Command Center-ului: `command-center.SKILL.md`
- Reguli generale de git: `mavis-git-autonom-skill`
- Disciplina de masurare: `verification-and-falsification.SKILL.md`
- Verificatorul executabil: `scripts\verify-remote-clone.ps1`
- Controlul falsificator: `scripts\make-broken-tree-control.py`
