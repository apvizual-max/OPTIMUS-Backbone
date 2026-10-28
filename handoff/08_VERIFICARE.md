# Verificare — dovezi măsurate

Fiecare afirmație de mai jos are **comanda** care o produce și **ieșirea
reală**. Măsurat pe 2026-10-28, după unirea celor cinci repo-uri.

---

## 1. Unirea — istoricul nu e copiat, e legat

Criteriul: commit-ul fiecărui repo sursă trebuie să fie **strămoș** al
`main`-ului. Testul: `git merge-base --is-ancestor <commit> HEAD` → exit `0`.

```powershell
git merge-base --is-ancestor 3757b53 HEAD ; $LASTEXITCODE   # SENTINEL_PRIME
git merge-base --is-ancestor 549c348 HEAD ; $LASTEXITCODE   # Mavis-Google_Access
git merge-base --is-ancestor 3b6b7dc HEAD ; $LASTEXITCODE   # MAVIS-CLOUD (head vechi)
git merge-base --is-ancestor fb38972 HEAD ; $LASTEXITCODE   # Optimus_CI
git merge-base --is-ancestor 8e90b56 HEAD ; $LASTEXITCODE   # mavis-skills
git merge-base --is-ancestor b611b95 HEAD ; $LASTEXITCODE   # MAVIS-CLOUD (head nou)
```

**Rezultat: toate șase → `0`.** Și aceeași verificare, făcută **pe remote**:

```powershell
git merge-base --is-ancestor <commit> 402f2f0
```

**Rezultat: toate șase → `0`.** Istoricul e pe GitHub, nu doar în local.

Merge-commit-urile au **doi părinți** (verificat cu
`git log -1 --format='%h parents=[%p]'`):

| Prefix | Merge-commit | Părinți |
|---|---|---|
| `SENTINEL_PRIME/` | `b54e827` | `[f3099ea 3757b53]` |
| `Mavis-Google_Access/` | `08c017f` | `[b54e827 549c348]` |
| `Optimus_CI (by Mavis)/` | `82143c2` | `[08c017f fb38972]` |
| `60_SKILLS/mavis-skills/` | `dd9b2aa` | `[82143c2 8e90b56]` |
| `Mavis-Google_Access/.work/MAVIS-CLOUD/` | `1ba9416` | `[8142f43 b611b95]` |

## 2. Starea git

| Măsurătoare | Valoare |
|---|---|
| `git rev-parse HEAD` | `402f2f07df4e20052ed50a6a717b86898afba31b` |
| `git ls-remote origin refs/heads/main` | `402f2f07df4e20052ed50a6a717b86898afba31b` |
| **identice** | **da** |
| `git rev-list --count HEAD` | 592 |
| `git ls-files \| Measure-Object` | 1.782 |
| `git rev-list --left-right --count origin/main...HEAD` | `0  0` |
| `git status --porcelain` | **gol (0 intrări)** |
| ramuri pe remote | `main` — una singură |
| PR-uri deschise | `[]` — zero |
| intrări în arborele remote (`gh api .../trees/main?recursive=1`) | 2.370 |
| fișiere > 100 MB | niciunul (cel mai mare: 2.388.756 B) |
| gitlink-uri (submodule) | niciunul |
| suma fișierelor din arbore | 36.169.103 B (34,5 MB) |

## 3. Serviciile

| Verificare | Rezultat |
|---|---|
| `GET http://127.0.0.1:8900/` | **HTTP 200**, 176.529 octeți |
| `GET http://127.0.0.1:8900/api/state` | **HTTP 200**, 39.052 octeți, `generated=2026-10-28T13:19:30` |
| `GET http://127.0.0.1:8912/api/health` | **HTTP 200**, 21.144 octeți |
| gardianul SENTINEL | `guardian up - supervising ... on port 8912, every 45s` → `ok pids=59664` |
| serverele MCP din SOT | 9 înregistrate, cu calea în SOT (vezi `_inventory/03`) |

## 4. Poarta de push — dovedită în ambele sensuri

| Situație | Măsurătoare | Rezultat |
|---|---|---|
| fără acord | `git push --dry-run origin main` | **exit 1**, mesajul porții, **fără** contact cu remote-ul |
| cu acord | `.git\PUSH-ACORD` creat, apoi push | **exit 0**, ajunge la remote, markerul **consumat** |
| sintaxă | `sh -n scripts/git-hooks/pre-push` | exit 0 |
| instalare | `core.hooksPath` | `.git/hooks` (poarta e activă) |
| identitate | SHA-256 canonic vs `.git\hooks\pre-push` | **identice** |

## 5. Un eveniment de pe parcurs — prima împingere a fost respinsă

Prima încercare de push a fost respinsă cu
`! [remote rejected] main -> main (push declined due to repository rule violations)`
— cu mesajele serverului **goale**. A doua încercare, cu același arbore, a
trecut: `267ef3c..402f2f0 main -> main`, exit 0.

Ce s-a exclus prin măsurătoare, înainte de a reîmpinge:

- fără branch protection (`404 Branch not protected`)
- fără rulesets (`[]`)
- fără push protection (`secret_scanning_push_protection: disabled`)
- fără fișiere peste 100 MB (cel mai mare: 2,4 MB)
- fără gitlink-uri
- repo public, toate tipurile de merge permise

Concluzie: **respingerea a fost tranzitorie**, nu o regulă de conținut.
**NOT_MEASURED**: nu am reținut codul exact al primului refuz — dacă se repetă,
se cere capturarea completă a ieșirii serverului înainte de orice diagnostic.

## 6. Igiena arborelui — ce a ieșit din urmărire și de ce

| Grup | Fișiere | Motiv scris în `.gitignore` |
|---|---|---|
| `09_LOGS/`, `13_COMMAND_CENTER/logs/` | 331 | loguri și stare runtime |
| `13_COMMAND_CENTER/api/*.json`, `state-history.jsonl` | 12 | măsurători regenerate la ~40 s |
| `08_SELF_IMPROVEMENT/{backups,backup_metadata}/` | 892 | copii de rezervă |
| `13_COMMAND_CENTER/backups/versions/` | 18 | store de versiuni (copii ale sursei) |
| `__pycache__/` | 6 | bytecode derivat |
| `test_suite.py`, `test_sentinel.md` | 2 | rescrise de motor la fiecare ciclu (măsurat în două runde) |

**Toate rămân pe disk.** Istoricul lor e în commit-urile anterioare. Ce s-a
schimbat: nu mai sunt urmărite de git — pentru că un monorepo cu starea
runtime urmărită **nu poate avea arborele curat**, deci nu poate fi nici
auditat, nici împins.

## 7. Lacune consemnate (nu remediate, cu motiv)

| Lacună | Măsurătoare | De ce nu s-a reparat |
|---|---|---|
| Supraveghere la logon pentru SOT | `Register-ScheduledTask` și `schtasks /create` → „Access is denied" | cere privilegii administrative (D10) |
| Curățenia din `%TEMP%` | 111.417 fișiere, 318,5 MB | ștergerea în masă e blocată de politica instrumentelor |
| Dubla proprietate pe 8900 | două watchdogs, port identic | soluția presupune oprirea unui server dintr-un alt proiect (D7) |
| Token GitHub în clar | `scripts/hermes-custom/` | acțiune de cont, pe numele tău (D3) |
