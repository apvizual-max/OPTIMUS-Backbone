# `handoff/` — pachetul de predare

Acest folder există pentru un singur motiv: **sesiunea precedentă avea tot
contextul în memorie, iar sesiunea nouă nu îl are.** Fără acest pachet, orice
început de sesiune ar fi o ghicire — unde stau fișierele, ce rulează, ce e
unit într-un repo, ce e doar o oglindă, ce împiedică un push nedorit, și ce
lecții au costat timp și au fost plătite.

Regula de aur a acestui folder: **tot ce e scris aici e măsurat.** Fiecare
număr, fiecare cale, fiecare hash are o comanda care l-a produs și o dată.
Când nu s-a putut măsura, scrie `NOT_MEASURED` și spune de ce. Nu există
estimări frumos împachetate ca fapte.

---

## Cum se citește

**Start cu `01_PRIMING_PROMPT.md`.** E textul pe care îl primește sesiunea
noua, cu context zero și memorie zero. Conține regulile care nu se negociază
și primul pas obligatoriu.

Apoi, în ordine:

| Fișier | Ce acoperă |
|---|---|
| `00_README.md` | acest document — ce e folderul, cum se folosește |
| `01_PRIMING_PROMPT.md` | promptul de primare + cele 10 reguli + primul pas |
| `02_STRUCTURA_SOT.md` | harta arborelui, modelul oglindă, junction-urile, ce e canonic |
| `03_ISTORIC_MIGRARE.md` | ce s-a întâmplat la unificare, cu măsurători și dovezi |
| `04_SISTEME_SERVICII.md` | sistemele, daemonii, porturile, lanțul de supraveghere |
| `05_GIT_GITHUB.md` | starea git, poarta de push, regulile de commit/push, istoricul |
| `06_LICENSIUNI.md` | lecțiile care au rămas, cu contextul în care au apărut |
| `07_DECIZII_DESCHISE.md` | deciziile care îmi aparțin și care încă așteaptă |
| `08_VERIFICARE.md` | dovezile măsurate ale stării de acum |
| `_inventory/` | inventarul măsurat: structură, skilluri, conectori, dependențe |
| `_git_history/` | starea **necomitată** a celor 4 repo-uri, ca patch-uri + status |
| `_runtime/` | starea proceselor înainte de migrare |

## Ce **nu** e aici, și unde e în schimb

- **Bundle-urile git complete** (toate ref-urile: branchuri, tag-uri, istoric
  care nu e pe `main`) sunt în `SOT\backups\_git_history\*.bundle`, **ignorate
  de git**. Motivul: istoria nu conține copii ale sursei. Sunt totuși pe disc,
  la un `git bundle` de distanță.
- **Copiile de lucru ale repo-urilor** (cu `.git` propriu) sunt în
  `C:\Users\apviz\_sot_stage\held\`. Nu sunt șterse, nu sunt în istorie, nu
  sunt în arhivă. Sunt reziduul operațional al unirii.
- **Junction-urile** (`projects\SENTINEL_PRIME`, `projects\scripts\git-hooks`,
  `60_SKILLS\_links\mavis-skills`) nu sunt fișiere — sunt legături pe disk.
  Nu apar în `git status` și nici în istorie.

## Cum verifici că pachetul e adevărat

Orice afirmație din acest folder se poate verifica în 10 secunde. Exemplu:

```powershell
cd C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard
git merge-base --is-ancestor 3757b53 HEAD ; $LASTEXITCODE   # -> 0
git rev-list --count HEAD                                     # -> 590
git status --porcelain                                        # -> gol
Invoke-WebRequest http://127.0.0.1:8900/api/state -UseBasicParsing | Select-Object StatusCode
```

Dacă un număr din folder nu se mai reproduce, **numărul e învechit, nu
realitatea**. Corectează folderul, nu sistemul — și consemnează data.

## Convenția numelor

`NN_nume.md` — `NN` e zero-padded, ordinea e ordinea de citire. În română
textul; în original rămân căile, comenzile, identificatorii și numele de
fișiere.
