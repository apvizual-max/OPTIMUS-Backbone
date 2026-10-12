# MAVIS — GIT & VAULT GOVERNANCE

**Tip:** micro-skill în cadrul suitei `mavis-optimus-continuous-integration-skill`
**Scop:** regulile care fac ca `git add` să funcționeze pe volume reale.
**Stare:** ✅ WIRED — fiecare regulă de mai jos a fost **măsurată în producție**,
nu dedusă. Data măsurătorii: **2026-10-12**, pe `D:\Alex_Knowlege_Vault`.

## 0. De ce există această skill

Pe 2026-10-11, `.gitignore`-ul vechi interzicea totul și redeschidea 4 căi.
Rezultatul măsurat: **36 de fișiere urmărite din 52.949 existente (0,07%)**,
`git status` curat, iar auto-salvarea a raportat **succes de 58 de ori** pentru
conținut care nu a intrat niciodată în istoric.

Acel sistem nu era lent. Era **fals**. Diferența dintre „ignorat intenționat" și
„pierdut fără știre" este exact diferența dintre o măsurătoare și o poveste.

## 1. Regula 1 — snapshot înainte de orice scriere care atinge mii de fișiere

Înainte de orice `git add -A`, orice rescriere de `.gitignore`, orice `git rm`:

```powershell
robocopy <sursa> <destinație> /E /COPY:DAT /DCOPY:DAT /R:1 /W:1 /MT:8 /XJ
```

apoi **numără fișierele în ambele locuri**. Nu „a reușit", ci `MATCH`.

Măsurat 2026-10-12: 52.949 / 52.949 · 834 / 834 · 9.845 / 9.845 — toate MATCH.
Snapshot-ul e la `D:\_OPTIMUS-SNAPSHOT\2026-10-12\`.

**Interzis absolut în acest vault:** `git clean -fdx` și `git reset --hard`.
`.git` e **în interiorul** vaultului — un clean ar șterge conținutul lui, nu
doar fișierele neversionate.

## 2. Regula 2 — limita Windows MAX_PATH: `core.longpaths`

Măsurat: **155 căi** depășeau 260 de caractere (maxim 329). Simptomul e un
`git add` care moare cu `fatal: adding files failed — Filename too long` și
raportează **0 fișiere adăugate** fără să spună de ce.

```powershell
git config core.longpaths true     # PER-REPO, nu global
```

Este per-repo pentru că e o proprietate a arborelui, nu a mașinii. O setare
globală uitată e o setare care lovește repo-uri care nu o cer.

## 3. Regula 3 — plafonul GitHub: 100 MB pe fișier

GitHub **respinge la push** orice fișier peste 100 MB. Măsurat în vault:
**106 fișiere, 48.961 MB**.

`.gitignore` **nu are operator de dimensiune**. Deci regula nu se scrie, se
**generează din măsurătoare**:

```powershell
Get-ChildItem <repo> -Recurse -Force -File |
  Where-Object { $_.Length -gt 100MB } |
  ForEach-Object { '/' + ($_.FullName.Substring($v.Length+1) -replace '\\','/') }
```

Rezultat: 103 căi explicite (dintre care 3 sunt deja în directoare excluse).

> **Consecința logică:** „cifra reală de urmărit" nu poate fi niciodată totalul de
> pe disc. Când o parte nu poate ajunge în istoric, cifra corectă e totalul
> minus partea măsurată. Nu tăiem cifre ca să arate bine — excludem fișierele
> pe care platforma le respinge.

## 4. Regula 4 — repo-urile git imbricate dispar fără mesaj

Git **nu coboară** într-un director care e el însuși un repo: îl tratează ca
gitlink și nu parcurge nimic din interior.

Măsurat în vault: **3 repo-uri imbricate = 588 de fișiere absente** din lista de
urmărire, **fără niciun avertisment**:

- `10_Work\…\Client Data sets\PLATEFUL - DTC - Niv`
- `_SYSTEM\Skills\Skills_Archive\_Skills_BackUp_Archive_2026-07-15\agent-browser`
- `_QUARANTINE\indexuri generate in gresit\Skills_Archive\…\agent-browser`

Fix: **regulă explicită de excludere în `.gitignore`**, sau repo-ul e repo.

## 5. Regula 5 — secretele se exclud, și se verifică DUPĂ indexare

Măsurat 2026-10-12: scanarea de după `git add` a găsit **un token Telegram real**
(46 de caractere, forma `NNNNNNNNNN:…`) și patru fișiere de chei API în
`_ARCHIVE\Secrets\` — **intrate în commit**, înainte de orice push.

Un secret ajuns în istoric nu se scoate curat. Ordinea corectă:

1. `git add`
2. **scanează conținutul indexului**, nu doar numele fișierelor
3. doar apoi `commit`
4. dacă a trecut ceva, rescrie istoricul înainte de push

Repararea făcută: `git rm -r --cached`, regulă nouă, rescriere deterministă a
ramurii prin `git commit-tree` + `git update-ref` + `git reflog expire`.
Verificat: **91 de commituri reachable, niciunul cu secretul**.

## 6. Regula 6 — stare vie nu se urmărește

`raport-aliniere.log` era urmărit și producea o buclă: scrie intrarea → schimbă
fișierul → fișierul schimbat se comitează din nou. **55 de comituri consecutive**
între 13:11 și 17:46 pe 2026-10-11.

Un fișier care se rescrie singur nu are istoric. Are buclă. Se exclude **și** se
scoate din index cu `git rm --cached` — altfel regula nu se aplică la el.

## 7. Regula 7 — `.gitignore` se măsoară, nu se inventează

`.gitignore` nu spune ce **ar** trebui exclus. Spune ce **a fost măsurat** că
trebuie exclus. Fiecare grup de linii poartă: numărul de fișiere, numărul de MB,
și motivul. O regulă fără cifră e o opinie.

## 8. Măsurătoarea corectă a diferenței

`git ls-files` afișează non-ASCII cu escape-uri octale. Comparând cu căi reale,
raportează zeci de fișiere „pierdute" care există.

```powershell
git -c core.quotePath=false ls-files
```

Diferența dintre `Get-ChildItem -Recurse` și lista git se împarte în trei, nu
în „p pierdute": **intenționat ignorate** · **blocate de git-uri imbricate** ·
**blocate de platformă**. Necategorizate, sunt invizibile.