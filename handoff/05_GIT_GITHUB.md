# Git și GitHub — starea, poarta și regulile

Măsurat 2026-10-28.

---

## 1. Starea repo-ului

| | |
|---|---|
| rădăcină git | `C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard` |
| branch | `main` |
| remote | `https://github.com/apvizual-max/OPTIMUS-Backbone.git` |
| commituri | **590** |
| fișiere urmărite | **1.777** |
| branchuri locale | doar `main` |
| remote branches | `main`, `origin/HEAD`, plus 2 ramuri de fix din pipeline |
| tag-uri | niciunul |
| `core.hooksPath` | `.git/hooks` (relativ) → poarta e **activă** |

**Direcția sincronizării, măsurată:** `ahead 4, behind 0` la momentul
măsurătorii. GitHub **nu** avea nimic ce localul să nu aibă. În schimb,
`MAVIS-CLOUD` (repo înglobat) avea remote-ul **înaintea** localului — și a fost
sincronizat înainte de unire (§6.1 din `03_ISTORIC_MIGRARE.md`).

## 2. Poarta de push — cum funcționează

**Fișierul canonic:** `scripts/git-hooks/pre-push` (2.061 octeți, ASCII pur,
line endings LF, `sh -n` → exit 0).
**Instalat în:** `.git/hooks/pre-push` — **copie identică** (SHA-256 egal).
**Calea veche:** `projects\scripts\git-hooks` e acum **junction** spre canonică.

Mecanismul, în 5 rânduri de shell:

```sh
marker="$(git rev-parse --git-dir)/PUSH-ACORD"
if [ -f "$marker" ]; then rm -f "$marker"; exit 0; fi
... refuz ...
exit 1
```

Adică: **un acord = o singură împingere.** Se creează `.git\PUSH-ACORD`, se
face un push, markerul se consumă.

### 2.1 Dovada, nu declarația

| Situație | Comandă | Rezultat măsurat |
|---|---|---|
| fără acord | `git push --dry-run origin main` | **exit 1**, mesajul porții, **fără** contact cu remote-ul |
| cu acord | `.git\PUSH-ACORD` creat, apoi același push | **exit 0**, ajunge la remote (`267ef3c..e9fcb42`), markerul **consumat** |

O poartă care nu poate eșua e o cutie. Aceasta poate.

### 2.2 De ce există

Măsurat pe 2026-10-11: **12 comituri au ajuns pe GitHub fără acordul lui
Popy**. Portile din script (`-Acord`) se ocolesc prin `git push` direct, fiindcă
un script impune o regulă doar față de cel care cooptează. Poarta se mută pe
**client**, în `pre-push`, unde orice `git push` trece prin ea.

### 2.3 Când se scoate

```powershell
git config --local --unset core.hooksPath    # și ștergerea fișierului din .git\hooks
```

Nu se atinge nimic din interfața lui Popy. Nu se folosesc niciodată
`--no-verify`, `--vouch` sau `--skip` ca să se ocolească.

## 3. Regulile de commit și push

| Acțiune | Regula |
|---|---|
| **COMMIT** | autonom, automat, la fiecare succes măsurat — inclusiv pe modificările lui Popy. Fără întrebare. |
| **PUSH** | **doar cu acordul lui Popy**, și doar cu poarta curată |
| **FORK / ramă nouă** | doar cerut explicit, cu scop + criterii |
| **Changes în interfață** | gol, permanent — eu comit înainte |
| **PR-uri** | nu se creează; ținta e `main`, direct |

**Poarta de push înainte de orice împingere:** GitHub trebuie să fie unitar —
o ramură (`main`), zero PR-uri. Altfel: **nu se face**, se raportează motivele
și se așteaptă confirmarea. Nu se curăță nimic din proprie inițiativă.

## 4. Cele patru documente canonice și cele trei scripturi

| Rol | Fișier |
|---|---|
| contract de git | `_SYSTEM\Skills\git-install*` |
| comportament autonom | `_SYSTEM\Skills\git-autonom*` |
| push cu acord | `scripts\git-autopush.ps1` |
| perete pe mai multe repo-uri | `scripts\push-status.ps1` |
| verificare documente | `scripts\verify-docs.ps1` |
| poarta | `scripts\git-hooks\pre-push` |

`push-status.ps1` măsoară perete pe cele 3 repo-uri gestionate și scrie
`90_CONTROL_CENTER\api\push-pending.json` (ignorat de git: se rescrie la
fiecare măsurătoare).

## 5. Cele cinci repo-uri înglobate — starea remote-urilor lor

| Prefix în SOT | Remote | Rol după unire |
|---|---|---|
| `SENTINEL_PRIME/` | `apvizual-max/SENTINEL_PRIME` (privat) | istoricul e în SOT; repo-ul sursă rămâne ca referință |
| `Mavis-Google_Access/` | `apvizual-max/Mavis-Google_Access` | la fel |
| `Mavis-Google_Access/.work/MAVIS-CLOUD/` | `apvizual-max/MAVIS-CLOUD` | la fel |
| `Optimus_CI (by Mavis)/` | `apvizual-max/MAVIS-OPTIMUS-CI` | la fel + **mirrorul operațional pe `E:`** rămâne pipeline-ului |
| `60_SKILLS/mavis-skills/` | `apvizual-max/Optimus-Mavis-Skills` | la fel + **registry-ul live** rămâne aplicației |

Toate bundle-urile complete (toate ref-urile, inclusiv ramuri și tag-uri care
nu sunt pe `main`) sunt în `backups\_git_history\*.bundle`, **ignorate de git**:
istoria nu conține copii ale sursei. Starea **necomitată** a fiecărui repo e
în `handoff\_git_history\*.patch` + `*-status.txt`.

## 6. Ce a rămas de decis de Popy

**Cele 12 comituri de pe GitHub, fără acord.** Măsurat: comituri pe remote,
publicate înainte de poartă. Recomandarea, adusă cu fapte: **se păstrează** —
rescrierea istoricului publicat ar șterge dovezi și ar încălca liniaritatea
istoricului. Poarta de acum e preventivă, nu reparatorie. Poți confirma
(pastrez) sau cere altceva.
