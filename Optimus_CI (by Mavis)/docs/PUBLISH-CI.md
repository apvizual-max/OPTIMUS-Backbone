# PUBLISH-CI — procedura de publicare (aditiv, 2026-10-27)

> Scop: documentul descrie **cum se publică** pe `apvizual-max/MAVIS-OPTIMUS-CI`
> cu o singură operație măsurată. Nu înlocuiește `docs/GIT-GITHUB-PROCEDURI.md`
> (regulile generale) și nu înlocuiește `docs/CI-POLICY.md` (guvernanța R0).
> **Aditiv**: acolo unde spune altceva, spune despre instrument, nu despre regulă.

---

## 1. De ce a apărut

Repo-ul CI este lucrat **în paralel** de alt AI (sesiunea CD), deci `main` și
`origin/main` au două istorice. Combinarea lor era o secvență de comenzi
tipărite manual — exact acolo unde se nasc greșelile: un rebase care reia 26
commituri, un merge cu un conflict pe care nimeni nu l-a privit, un push al
cărui succes e judecat dintr-un cod de ieșire.

Secvența a devenit **un singur script**, cu măsurătoarea înainte de mutare.

| Instrument | Rol | Locație |
|---|---|---|
| `scripts/merge-check.ps1` | măsurătoarea: fetch + divergență + `merge-tree` (dry-run) + diff per parte | repo CI |
| `scripts/merge-check-selfcheck.ps1` | auto-proba măsurătorii (5 probe) | repo CI |
| `scripts/publish-ci.ps1` | **operația**: măsoară → combină → împinge → verifică | repo CI |
| `scripts/publish-ci-selfcheck.ps1` | auto-proba publisher-ului (12 probe) | repo CI |

---

## 2. Secvența, măsurată

```
powershell -NoProfile -File scripts\publish-ci.ps1            # DOAR măsură
powershell -NoProfile -File scripts\publish-ci.ps1 -Push      # operația R0
```

1. **fetch** al remote-ului viu — o măsurătoare făcută pe un ref vechi e o
   măsurătoare falsă.
2. **verificare de curățenie**: fișierele **urmărite** trebuie necomitate
   (altfel rezultatul nu aparține nimănui); fișierele **neurmărite** doar se
   raportează, nu blochează.
3. **calea trebuie să fie rădăcina repo-ului** — `git rev-parse --show-toplevel`
   trebuie să fie chiar calea dată. `git rev-parse --git-dir` *urcă* în arbore,
   deci un subdirector de repo ar publica alt repo decât cel cerut.
4. **măsurătoarea e poarta**: `merge-check.ps1` decide. Nu scriptul.
5. **merge `--no-ff`** → ambele istorice rămân în istoric. Nimic nu e
   rebased, nimic nu e șters, nimic nu e forțat.
6. **push**, cu poarta `pre-push` satisfăcută (marker `PUSH-ACORD`, consumat
   și eliminat).
7. **verificare prin `git ls-remote`** — adevărul e pe remote, nu în codul de
   ieșire. Se repetă de 4 ori, cu 2s pauză, pentru că un server (sau un proxy)
   poate răspunde din cache.

---

## 3. Codurile de ieșire (contractul)

| Cod | Semnificație | Ce s-a întâmplat |
|---|---|---|
| `0` | măsurat și curat; cu `-Push` = împins **și verificat** | `VERDICT=publicat` |
| `1` | **conflict** — fișierele sunt numite | nimic schimbat, nimic împins |
| `2` | nemăsurabil / nepublicabil | nimic împins — **UNKNOWN**, nu verdict curat |
| `3` | pushul a rulat, dar `ls-remote` nu arată HEAD-ul local | **UNKNOWN**, nu succes |
| `4` | push **refuzat** (poarta R0, remote-ul, sau auth-ul) | remote-ul **nu** poartă HEAD-ul → nimic publicat |

> **Regula:** marcajul transportă sensul (`VERDICT=...`), codul de ieșire
> doar clasifică. „Push refuzat" și „împins dar neverificat" sunt stări
> diferite și au coduri diferite — refuzul înseamnă că nimic nu a fost
> publicat și se poate reîncerca.

---

## 4. Măsurătoarea de pe repo-ul real (2026-10-27)

| | |
|---|---|
| HEAD înainte | `a4a1277` |
| remote înainte | `3da55ff` |
| divergență | 5 înapoi / 26 înainte |
| `merge-tree` | `39661fa…` · `MERGE_CLEAN=yes` · `CONFLICT_FILES=0` |
| merged vs local | 6 fișiere (+74 / −13) — lucrul celuilalt AI |
| merged vs remote | 43 fișiere (+8862 / −230) — lucrul meu |
| commit de merge | `86669d9`, **2 părinți**: `e9290f7` (local) + `3da55ff` (remote) |
| verificare | `ls-remote` = `86669d9` = HEAD local · `DIVERGENCE_FINAL=0 0` |
| istoricul remote vechi | `merge-base --is-ancestor` → **exit 0** (e strămoș) |

Adică: ce era deja pe GitHub **a fost inclus**, nu suprascris.

---

## 5. Cele 12 probe ale publisher-ului

`PUBLISH_GATE_PROBLEMS=0 FALSIFIED=12`

| # | Probe | Ce dovedește |
|---|---|---|
| 1 | dry run pe divergență curată | exit 0, remote neatins |
| 2 | push pe divergență curată | exit 0, remote arată HEAD-ul local, **remote mutat** |
| 3 | merge-ul păstrează **ambele** istorice | commit cu 2 părinți; commitul remote e strămoș |
| 4 | push pe **conflict** | exit 1, remote neatins, arbor neatins, fișier numit |
| 5 | folder care nu e repo | exit 2 (UNKNOWN, nu succes) |
| 6 | **subdirector** de repo | exit 2, **NU** se publică părintele |
| 7 | repo-ul real, doar dry run | exit 0, remote-ul real neatins |
| 8 | **static**: nicio variabilă de la nivelul scriptului nu umbrează un parametru | coliziuni = 0 |
| 9 | falsificarea probei 8 | publisher-ul **strictat pe copie** e detectat |
| 10 | push **refuzat** de poartă | exit 4, remote neatins, raportat ca refuz |
| 11 | fișier **urmărit** modificat | exit 2 (blocat), remote neatins |
| 12 | doar fișier **neurmărit** | nu blochează (exit 0), raportat ca NOTE |

### 5.1 De ce probe 8 există

O variabilă locală cu același nume ca un parametru al scriptului e o
**coliziune** în PowerShell (nume sunt case-insensitive): `$push` vs
`[switch]$Push`, `$remote` vs `[string]$Remote`. Atribuirea unui Hashtable
devine o eroare de tip — **după** ce operația s-a executat. Rezultatul: operația
făcută, raportată ca eșec.

Proba citește **AST-ul** (ce vede parserul, nu ce ghică un regex), ignoră
atribuirile din interiorul funcțiilor (scope diferit) și se falsifică pe o
**copie**: un publisher stricat intenționat **trebuie** detectat, altfel proba
nu dovedește nimic.

### 5.2 De ce fixture-urile sunt unice per rulare

O cale fixă de fixture: `git clone` într-un director existent **eșuează**, iar
proba măsoară repo-urile din **rulingul precedent**. A fost măsurat: proba
„remote mutat" a raportat fals pentru un push care funcționa. Director
`run-<timestamp>` + curățarea rundelor anterioare create de același script.

---

## 6. R0 și poarta de push

- `PUSH` = singurul lucru care cere R0 explicit.
- `publish-ci.ps1` **fără** `-Push` nu mută nimic. Cu `-Push`, e operația R0.
- Poarta `pre-push` rămâne **activă**: publisher-ul îi scrie markerul
  `PUSH-ACORD` (un acord = o împungere) și îl elimină în `finally`, chiar dacă
  pushul eșuează. Un acord nefolosit lăsat pe disc e o gaură, nu o siguranță.
- Publisherul **nu** face: force push, `reset --hard`, `git clean`, rebase,
  ștergere de fișiere, și nu ocolește poarta.

---

## 7. Remedieri măsurate în aceeași sesiune

| Defect | Măsurare | Reparare |
|---|---|---|
| coliziune `$push`/`$remote` cu parametrii | crash **după** push, raportat ca eșec | variabile redenumite; probă statică AST (proba 8) |
| `$RepoPath = Split-Path …` (atribuire la parametru) | coliziune detectată de proba 8 | variabila locală `$repo` |
| cale ne-rădăcină acceptată | „nu e repo" din interiorul arborelui CI → exit 0, ar fi publicat CI-ul | verificare `rev-parse --show-toplevel` (proba 6) |
| push refuzat raportat ca „neverificat" | exit 3 pentru un refuz | exit 4, distinct (proba 10) |
| fișiere neurmărite blocau publicarea | ieșire 2 fără motiv real | doar raportate ca NOTE (proba 12) |
| fixture-uri supraviețuitoare | proba 2 raportă fals | director unic per rulare |
| **BOM** în subiectul commitului | `EF BB BF EF BB BF` la obiect | `--amend` cu fișier UTF-8 fără BOM |
| **emoji** în `mavis-sync.ps1` | 15 octeți non-ASCII → parser PS 5.1 moare | `[bolt]` ASCII pur, `parseErrors=0` |

---

*Aditiv. Măsurătoare: `scripts\publish-ci-selfcheck.ps1`, 12 probe, pe repo-uri
reale. Fără BOM, ASCII pur, PowerShell 5.1.*
