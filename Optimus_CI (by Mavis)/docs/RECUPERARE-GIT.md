# STAREA MĂSURATĂ A MAȘINII — recuperare Git

> **Măsurătorile: 2026-10-11/12.** 121 repo-uri găsite, 76 măsurate
> (45 erau ritualuri Temp). Cifrele sunt de acolo, nu de memorie.

---

## 1. Vault-ul — problema principală

```
D:\Alex_Knowlege_Vault
  fișiere pe disc         : 52.933
  fișiere urmărite de git :     36
  comituri                :     58
  remote                  : pkms-vault-automation.git
```

**52.897 de fișiere nu au intrat niciodată în istoric.**

Cauza: `.gitignore` prin **negație** (`/*` interzice totul, apoi
redeschizi explicit căile reale). La 52.933 de fișiere, redeschiderea a
acoperit un procent infim.

Și cel mai rău: auto-salvarea a raportat **58 de ori** „1 cale(i)
modificate" și a creat 58 de comituri — comitând un fișier de log.
**Conținutul nu a intrat niciodată, iar sistemul a raportat succes de 58
de ori.**

> Un senzor mort care raportează sănătate e mai prost decât un senzor
> care lipsește. Exact asta s-a întâmplat.

**Stare: neatins.** Nevoia de snapshot înainte de orice scriere.

---

## 2. Config global — blast radius

`~/.gitconfig` conține:

```
core.hooksPath   = C:\Users\apviz\.git-hooks
core.editor      = ...\lrc\lrc_editor.sh
credential.helper= (GOLIT)
user.name        = Sentinel Prime
user.email       = sentinel.prime@optimus.local
```

`credential.helper` **golit** = niciun helper de credențiale la nivel
global. Doar cel pentru `github.com`, cu `store`.

---

## 3. Câți repo-uri moștenesc configurația stricată

| Situație | Repo-uri |
|---|---|
| moștenesc `hooksPath` **global** | **~70 din 76** |
| au `core.autocrlf = true` | **~70 din 76** |
| au `autocrlf = false` (conform spec) | **6** |
| au `hooksPath` **local** | **4** |
| au hook `pre-push` | **1** — în `OPTIMUS-Backbone` |

### Efect măsurat

Un repo nou, gol, returnează:
```
LiveReview: review attestation missing
exit 128 — niciun comit
```

**LiveReview e în calea comitului**, pe toate mașinile. Poarta corectă
e **după** push, niciodată la comit.

### Corecție de onestitudine

Am afirmat la un moment dat că **nu există niciun `pre-push`**. **Fals.**
Am scris un check care nu putea raporta corect — un `$_` suprascris într-un
`ForEach-Object` imbricat. Hook-ul era în `OPTIMUS-Backbone\.git\hooks`
începând cu 18:23 și a funcționat: când am încercat `git push` direct, **a
refuzat mesajul**.

> **Un check care nu poate eșua nu e check.**

---

## 4. Repo-uri cu ștergeri masive

| Cale | Urmărite | Șterse | Pe disc | Remote |
|---|---|---|---|---|
| `.minimax\vault-manifest\git-parked-2026-10-07` | 13.581 | 13.581 | 9.845 | **niciunul** |
| `E:\CLAUDE\MINTE\OLD DATA...\- OLD Work Files` | 58.296 | 58.237 | 834 | `prime-sentinel.git` **greșit** |

`git-parked` e un `git add -A` **necomitat** — conținutul e în index, nu
pierdut. Se scoate înapoi fără a atinge git: se citește din index într-un
folder nou, se compară, și abia apoi se decide.

`OLD Work Files` are **toate** fișierele în istoric, dar e atașat la
`prime-sentinel.git` — **același remote** ca
`D:\GitHub backup 2026-10-08\prime-sentinel`. Două foldere, un remote.

---

## 5. Comituri neîmpinse înainte de astăzi

| Repo | Neîmpinse |
|---|---|
| `Alex_Knowlege_Vault` | 58 |
| `OPTIMUS-Backbone` | 4 |
| `SENTINEL_PRIME` | 4 |

**Rezolvat 2026-10-12:** toate trei au fost împinse și verificate cu
`git ls-remote`. Vezi planul, Pasul 0.

---

## 6. Zgomot

**31 de clone de backup** „GitHub backup 2026-10-08", dublate pe `C:` și
`D:`. Plus 45 de repo-uri de ritual în `Temp`. Nu periculoase — dar
îngropă inventarul și fac orice măsurătoare să pară mai rău decât e.

---

## Ce e rezolvat, și ce nu

| | Stare |
|---|---|
| Push blocat pe cele 3 repo-uri OPTIMUS | ✅ rezolvat și verificat pe server |
| Changes gol în cele 3 repo-uri | ✅ rezolvat |
| Doctrina operațională §20 | ✅ scrisă |
| Skillul de operator autonom | ✅ creat și commit-at |
| Vault: 52.933 → istoric | ❌ **neatins** |
| Config global stricat | ❌ neatins |
| `autocrlf` pe ~70 repo-uri | ❌ neatins |
| Puntea Local↔Cloud | ✅ **construită și măsurată** (2026-10-24) — rulează 08:30, `LastTaskResult=0` |
| Starea Jules | ⚠️ **parțial măsurată**: triajul e complet (99 PR-uri, verdict definitiv); starea din panoul Jules (Memories / Setup script / Env vars) rămâne **NECUNOSUT** |