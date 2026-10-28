# WORKFLOWS — cum se lucrează în CI

> **Complementul lui `CI-POLICY.md`.** Politica spune *ce* e permis; aici
> spune *cum se execută*, cu comenzi, porți și coduri de ieșire.
>
> **Măsurat 2026-10-27.** Fiecare flux are o poartă care **poate eșua**.

---

## W0 — Deschiderea sesiunii

```powershell
node C:\Users\apviz\QWEN_BACKUP\core\kernel.js --intent "<ce urmează să fac>"
powershell -NoProfile -File scripts\mavis-drive-bridge-selfcheck.ps1
powershell -NoProfile -File scripts\scan-staged-secrets-selfcheck.ps1
git status --short
```

**Citește, în ordine:** `README.md` → `DOCTRINA-CI.md` → `MAPARE-SISTEM.md` →
`docs/MAPARE-FOLDERE.md` → acest document.

**Nu declara nimic înainte de măsurat.** La început se citește; la final se
raportează.

---

## W1 — Schimbare în proiect → commit

**Automat, pe `main`, fără R0.** Popy nu aprobă comituri.

```
1. editezi (write/edit)
2. git add -A
3. poarta de secrete rulează AUTOMAT prin hook-ul pre-commit
4. git commit
```

| Cod al porții | Ce înseamnă | Ce faci |
|---|---|---|
| `0` | `BLOCKS=0 WARNS=0 SCAN_OK` | comitezi |
| `1` | cel puțin un `BLOCK` — **commit refuzat** | vezi `BLOCK <pattern> @ <fișier>:<linie>` |
| `2` | scanarea **nu a putut rula** — commit refuzat | e o eroare, nu un bloc. Nu rescrie secretul; repară scannerul |

> **Regula:** `2` ≠ `1`. O poartă care *acuză* trebuie să dovedească
> imputabilitatea; o aruncare nu e o dovadă.

**Proba porții, la schimbarea ei:**
```powershell
powershell -NoProfile -File scripts\scan-staged-secrets-selfcheck.ps1
```
7 probe, în ambele sensuri: o cheie plantată e **blocată**, un placeholder
**nu** e blocat, o cheie privată e blocată, liniile goale **nu** aruncă
excepție, scannerul **nu** se blochează pe propriul cod, indexul real e curat.

---

## W2 — Publicarea către Cloud

```powershell
powershell -NoProfile -File scripts\mavis-drive-bridge.ps1 -Publish -Title "<subiect>" -Body "<text>"
```

**Ce se întâmplă:** se scrie **același `TASK_ID`** în ambele canale —
`BRIDGE-DRIVE/TASKURI-PENTRU-CLOUD.md` (Drive, primar) și
`QUEUE/TASKS-FOR-CLOUD.md` (GitHub, secundar) — și se emite un receipt în
`state/drive-bridge-last-publish.json`.

| Cod | Ce înseamnă |
|---|---|
| `0` | `SYNCED` — confirmat în indexul de cloud |
| `2` | input lipsă (fără `-Title`, fără python) |
| `3` | ținta nu a fost găsită în Drive |
| `4` | **scris, neconfirmat** — onestul „unknown" |
| `5` | transportul Drive e jos — canalul activ trece pe GitHub |

**Regula:** `UNVERIFIED` **nu e succes**. Nu raporta „am publicat" pe baza
scrierii — raportează pe baza măsurătorii.

**De ce ambele canale, la aceeași publicare:** o cădere de transport nu
trebuie să coste timp.

---

## W3 — Push pe GitHub

**Singurul lucru care cere R0.**

```
1. Popy dă R0 explicit
2. scripts\git-autopush.ps1 -Acord          # singura cale de push
3. git ls-remote origin main               # verificarea, NICIODATĂ prin exit code
```

| Cod | Ce înseamnă |
|---|---|
| `0` | hash-ul server **==** hash-ul HEAD local |
| `1` | **poarta a refuzat** push-ul: `POARTA: acest repo nu se impinge fara acordul lui Popy` |

> `git push` scris cu mâna **ocolesc** poarta? Nu — poarta e un hook
> `pre-push`, nu un switch. Dar și așa, calea corectă e `git-autopush.ps1
> -Acord`: un `-Acord` = o singură împungere.

**Divergența se documentează, nu se rezolvă cu forță.** Măsurat 2026-10-27:
**17 commituri local / 5 remote** (cele 5 remote sunt lucrarea CD). **Azi:
0 / 0** — divergența s-a închis cu `merge --no-ff` (ambele istorice păstrate,
commitul de combinare `86669d9` cu doi părinți), nu prin rescriere.

---

## W4 — Sincronizarea zilnică

Rulează singură, la **07:30**, prin taskul `MavisSyncBridge`
(`StartBoundary 2026-10-12T07:30:00+02:00` + `StartWhenAvailable=True` — de
aceea logurile din 23–24 oct apar la 08:30: mașina nu era pornită la 07:30).

```powershell
powershell -NoProfile -File scripts\run-sync-logged.ps1 -DryRun
```

| Ce | Măsurat |
|---|---|
| Log zilnic | `exit_pull=0`, `local_dupa == remote`, `impingere=NEEXECUTATA|poarta_R0=ramane_la_Popy` |
| Consecvență | 12 loguri consecutive (12→23 oct), fără gol |
| Auto-verificare | `mavis-sync.ps1 -SelfTest` → `POARTA|TRECUT` (EXIT 0) |

**Sincronizarea nu împinge.** Citește, și lasă push-ul porții.

---

## W5 — Verificarea a ce vede Cloud

```powershell
powershell -NoProfile -File scripts\mavis-drive-bridge.ps1 -Status
python scripts\drivefs_probe.py --staleness "MAPARE-SISTEM.md" --folder "Optimus_CI (by Mavis)" --local "<rădăcină>"
```

| Câmp | Ce înseamnă |
|---|---|
| `TRANSPORT=UP` | rădăcina mirrorului e **conectată** |
| `PROPAGATION=OK` / `STALE` | scrierea locală e / nu e **confirmată** |
| `CLOUD_CHANNEL_FILE_PRESENT` | fișierul canalului e / nu e în indexul de cloud |
| `CLOUD_TRACKED_AGE_DAYS` | **cât de veche e copia** pe care Cloud ar citi-o |
| `ACTIVE_CHANNEL` | `DRIVE` doar dacă propagarea e `OK`; altfel `GITHUB` |

> **O rădăcină conectată nu e un transport care încarcă.** Măsurat: rădăcina
> `connected=true`, coada `PENDING_OPERATIONS=0`, dar motorul de sync al
> DriveFS raporta `change_ids_up_to_date: true` — nu vedea scrierile locale.

---

## W6 — Transport degradat

**Nu blochează sistemul.** Regula: poarta cere ca **raportul să fie
concordant cu măsurătoarea**, nu ca transportul să fie UP.

```
1. mavis-drive-bridge.ps1 -Status  →  PROPAGATION=STALE, ACTIVE_CHANNEL=GITHUB
2. conținutul NOU merge pe canalul secundar (push cu R0)
3. conținutul VECHI rămâne în cloud, și poate fi citit - dar e vechi
4. raportezi: ce e nou, unde, și cât de veche e ce vede Cloud
```

**Nu** re-autentifici DriveFS și **nu** reconsentezi tokenul unilateral:
act ACCESS, pe mașina lui Popy.

---

## W7 — Cerință nouă de la Popy

```
1. Popy scrie ce vrea în BRIDGE-DRIVE/INTENTII.md (liber, cu cuvintele lui)
   sau cererea e structurată și intră în TASKURI-PENTRU-CLOUD.md
2. Local: citește, măsoară, execută
3. Cloud: citește la pull, livrează în INTRARI-CLOUD/, marchează, mută în ISTORIC/
```

**Regula de numire:** `MAVIS-LOCAL-…` / `MAVIS-CLOUD-…` în ambele canale.
**Nu se suprascrie nimic.** Corecția = fișier nou.

---

## W8 — Verificarea pe server, peste conținutul aterizat

> **Aditiv.** Măsurat 2026-10-27.

```
.github/workflows/ci-verify.yml
  on: push (main) · workflow_dispatch · schedule '30 3 * * *'
  runs-on: windows-latest · permissions: contents: read
  → actions/checkout@v4
  → scannerul de secrete pe index
  → auto-proba
```

**Ce e diferit de W1:** W1 rulează **înainte** de commit, pe mașina lui Popy,
prin hook. W8 rulează **după** push, pe server, peste ce s-a aterizat.

| | W1 (hook) | W8 (server) |
|---|---|---|
| Când | înainte de commit | după push |
| Unde | calculatorul lui Popy | runner GitHub |
| Efect | **blochează** commitul | **raportează** (nu blochează) |
| Ce acoperă | indexul local | conținutul **public**, deja împins |

**De ce raportează, nu blochează:** acest repo e lucrat acum de alt AI. Un
workflow care blochează push-ul altcuia ar fi o poartă fără imputabilitate —
ar acuza conținut pe care eu nu l-am scris și pe care nu l-am măsurat. Regula
din `CI-POLICY.md` §5: *un verdict care acuză trebuie să dovedească
imputabilitatea.*

**Proba:** falsificat în ambele sensuri într-o clonă curată (runner simulat) —
`SCANNED=50 BLOCKS=0 SCAN_OK` exit 0 → cheie plantată → `BLOCKS=1` exit 1
(workflow roșu) → scosă → `SCAN_OK` exit 0.

**Starea reală:** workflow-ul `ci-verify.yml` **e pe remote** (a ajuns cu
împungerea lui `65af38f`, 26 oct; azi confirmat la `origin/main`, blob
`6f0fd55`). **Serverul rulează acum pentru acest repo.** Secțiunea spunea
*„404 pe remote, între cele 17 commituri neîmpinse"* — era adevărată înainte
de împungere.

---

## W9 — Puntea zilnică (task 07:30)

> **Aditiv.** Măsurat 2026-10-27.

Rulează singură, la **07:30**, prin taskul Windows `MavisSyncBridge`
(`StartBoundary 2026-10-12T07:30:00+02:00` + `StartWhenAvailable=True` — de
aceea logurile din 23–24 oct apar la 08:30: mașina nu era pornită la 07:30).

```
MavisSyncBridge (task Windows)
  → scripts\run-sync-logged.ps1     ← wrapper cu log datat
    → scripts\mavis-sync.ps1        ← puntea propriu-zisa
      PAS1: pull read-only din MAVIS-CLOUD (cloud-ingest\)
      PAS2: commit LOCAL automat, fara impingere
      FINAL: impingere=NEEXECUTATA, poarta_R0=ramane_la_Popy
```

| Cod | Ce înseamnă |
|---|---|
| `0` | puntea a mers: pull reușit, comit făcut sau nimic de comitat |
| `4` | **măsurat**: pull-ul a eșuat (divergență, conflict) |
| `1` | **nu s-a putut măsura**: clone-ul Cloud lipsește sau remote inaccesibil |
| `2` | poarta a refuzat: scriptul conține un verb interzis |

**Codul de ieșire e propriu**, nu moștenit de la ultima comandă git.

### Verificarea

```powershell
powershell -NoProfile -File scripts\mavis-sync-selfcheck.ps1
```

Noua poartă, **9 probe**: cale derivată din `$PSScriptRoot` · `exit` explicit
· etichetă de comit onestă · 4 falsificări (copii doctorate → detectate) ·
poarta de interzicere a push-ului intactă.

Măsurat: `SYNC_PROBLEMS=0 UNKNOWN=0 FALSIFIED=4`, **EXIT 0**. Pe o copie
doctorală: `SYNC_PROBLEMS=3`, **EXIT 1**.

> **Defect reparat 2026-10-27:** puntea zilnică era ruptă în **trei locuri**
> simultan — taskul Windows, calea hardcodată din `mavis-sync.ps1`, și lipsa
> unui `exit` propriu. Doar repararea scriptului nu ar fi reparat-o: taskul
> ar fi continuat să apele un folder inexistent. Detalii:
> `docs/STARE-MASURATA-CI-2026-10-27.md` §8.

---

## W10 — Publicarea unei tichete în ambele canale, în format de contract

> **Aditiv.** Măsurat 2026-10-27.

O cerință pentru Cloud pornește din **coada secundară** și se scrie în
**ambele** canale, cu același `TASK_ID`:

```
scripts\mavis-drive-bridge.ps1 -Publish -Title "<subiect>" -Body "<text>" [-Scope cloud]
  → BRIDGE-DRIVE\TASKURI-PENTRU-CLOUD.md   ← canalul primar (Drive)
  → QUEUE\TASKS-FOR-CLOUD.md                ← canalul secundar (GitHub)
  → verifică: DUAL_CHANNEL_DRIVE / DUAL_CHANNEL_QUEUE
```

| Ce | Cum |
|---|---|
| Corp trunchiat (se oprește la mijloc de propoziție) | **refuzat**, exit 2 |
| `scope` în afara setului `cloud`/`local`/`ambele` | **refuzat**, exit 2 |
| Corp valid | scris în ambele, `DUAL_CHANNEL_*=True` |
| `TASK_ID` absent dintr-un canal | **exit 1** — publicare incompletă |

**Copia secundară se scrie în contractul consumatorului**, nu în formatul
canalului primar: `### [id] titlu` + `cerut de` · `data` · `scope` ·
`ce trebuie` · `livrare`. Contractul: `docs/CONTRACT-CLOUD-QUEUE.md`.

### Verificarea

```powershell
powershell -NoProfile -File scripts\queue-contract-check.ps1
```

→ `QUEUE_PROBLEMS=0 UNKNOWN=0`, **EXIT 0** · 2 tichete · `CONTRACT_DRIFT=NO` ·
`UNRECOGNISED_HEADERS=0` · `DONE_DIR=present`.

Auto-proba: `scripts\queue-contract-check-selfcheck.ps1` — **11 probe**,
`QUEUE_GATE_PROBLEMS=0 UNKNOWN=0 FALSIFIED=11`, EXIT 0. Falsificare în
ambele sensuri: coadă conformă → 0; tichetă fără `scope` / cu `scope`
necunoscut / fără `livrare` / trunchiată; `QUEUE/DONE` lipsă; id absent din
canalul primar; contract live ilizibil → **2 (UNKNOWN, nu succes)**; contract
derivat → 1.

---

## W11 — Combinarea istoricului, măsurată înainte de R0

> **Aditiv.** Măsurat 2026-10-27.

Când `origin/main` a avansat (alt AI lucrează în paralel), istoriculele **nu**
se combină la guess. Se măsoară întâi:

```
powershell -NoProfile -File scripts\merge-check.ps1
```

→ `REMOTE_STATE=LIVE` · `DIVERGENCE_BEHIND=… DIVERGENCE_AHEAD=…` ·
`MERGE_CLEAN=yes` · `CONFLICT_FILES=0` · `VERDICT=curat`

| Situație | Ieșire | Ce înseamnă |
|---|---|---|
| Istorice identice | `MERGE_CLEAN=NA` | nimic de combinat |
| Merge curat | exit **0** | o singură operație, fără rezolvare manuală |
| Conflict | exit **1** | fișierele sunt **numite**; rezolvare manuală |
| Nemăsurabil (remote neatins, git absent, ref inexistent) | exit **2** | **nu** e „curat" |

**`fetch` e partea măsurătorii.** Un verdict „curat" luat de pe un ref remote
învechit e un verdict fals. De aceea măsurătoarea face `fetch` înainte și
raportează `REMOTE_STATE=LIVE` sau `STALE`.

### Verificarea

```
powershell -NoProfile -File scripts\merge-check-selfcheck.ps1
```

→ `MERGE_GATE_PROBLEMS=0 UNKNOWN=0 FALSIFIED=5`, EXIT 0. Falsificare în
ambele sensuri: poarta **stricată pe copie** → `MERGE_GATE_PROBLEMS=3`,
`POARTA A BLOCAT`, exit 1 — iar poarta reală rămâne neatinsă (hash identic
înainte și după).

---

## Fluxuri pe care CI **nu** le atinge

| Flux | Unde trăiește |
|---|---|
| Triaj Jules, adaptări, Daily Loop | **CD** — `Optimus_CD (by Jules)\JULES - Optimus CD\` |
| Live Review, merge-uri de PR | **CD** |
| `JULES_API_KEY` în repo-uri | **CD** (R0 deschis) |

**Din CI se ating doar dacă e strict necesar** — și atunci se documentează.

---

## W12 — Publicarea pe GitHub (aditiv, 2026-10-27)

**Când:** când `main` local și `origin/main` au istorice diferite (alt AI
lucrează în paralel) și Popy a dat R0 pentru push.

```
powershell -NoProfile -File scripts\publish-ci.ps1            # DOAR măsură
powershell -NoProfile -File scripts\publish-ci.ps1 -Push      # operația R0
```

Instrumentul (`scripts/publish-ci.ps1`) face secvența în ordinea corectă:

1. **fetch** — măsurătoarea pe ref vechi e o măsurătoare falsă.
2. **arbore curat** pentru fișierele **urmărite**; cele **neurmărite** doar se
   raportează (nu pot intra în conflict cu un merge).
3. **verificare de rădăcină** — `git rev-parse --show-toplevel` trebuie să fie
   calea dată. `rev-parse --git-dir` urcă în arbore, deci un subdirector ar
   publica alt repo.
4. **măsurătoarea e poarta** — `merge-check.ps1` decide, nu scriptul.
5. **merge `--no-ff`** — ambele istorice rămân. Nimic rebased, nimic șters.
6. **push** — poarta `pre-push` satisfăcută cu markerul `PUSH-ACORD`, consumat
   și eliminat în `finally` (un acord nefolosit lăsat pe disc e o gaură).
7. **verificare prin `git ls-remote`** — repetată de 4 ori cu 2s pauză,
   pentru că serverul poate răspunde din cache.

### Codurile de ieșire

| Cod | Semnificație |
|---|---|
| 0 | împins **și verificat** (`VERDICT=publicat`) |
| 1 | **conflict** — fișierele sunt numite, nimic schimbat |
| 2 | nemăsurabil / nepublicabil — nimic împins, **UNKNOWN** |
| 3 | împins dar neverificat — **UNKNOWN**, nu succes |
| 4 | push **refuzat** — remote-ul nu poartă HEAD-ul, deci nimic publicat |

**Proba:** `scripts/publish-ci-selfcheck.ps1` → `PUBLISH_GATE_PROBLEMS=0
FALSIFIED=12` (12 probe pe repo-uri reale; falsificare pe copie pentru proba
statică; fixture curat per rulare).

Detalii complete: `docs/PUBLISH-CI.md`.

---

## W13 — Accesul Google fără re-autentificare (aditiv, 2026-10-27)

**Când:** când un server MCP Google nu reușește să se autentifice.

**NU se cere consentul întâi.** Mai întâi se măsoară:

```
node C:\Users\apviz\.minimax-agent\projects\google-layer\verify-google-credentials.js
node C:\Users\apviz\.minimax-agent\projects\google-layer\google-auth-hub.js
node C:\Users\apviz\.minimax-agent\projects\google-layer\mcp-probe.js
```

- `verify-google-credentials.js` — **măsoară** fiecare refresh token de pe
  mașină (exchange la `oauth2.googleapis.com/token`). Nu afișează niciun
  token: doar nume de chei, lungimi, coduri HTTP și motive.
- `google-auth-hub.js` — găsește grantul **viu** și îl publică în toate
  magazaurile pe care le citesc serverele. **Nu scrie nimic** dacă nu există
  grant viu (falsificat: cu tokenuri moarte, `RESULT=NO_LIVE_GRANT` și
  magazaurul rămâne neatins).
- `mcp-probe.js` — handshake MCP **real** + apel de tool **real**. Un magazaur
  populat nu înseamnă acces: handshake-ul trece și tool-ul pică.

**Cazul în care chiar trebuie consent:** nu există **niciun** grant viu
nicăieri pe mașină. Atunci, și numai atunci, `bun gdrive-oauth.js` cu consola
în browserul lui Popy.

**Launchere cu auto-vindecare** (se provisionează la fiecare pornire):
`gdrive-launcher.js` · `gmail-launcher.js` · `calendar-launcher.js`.

---

*2026-10-27 · Mavis Local · măsurat · aditiv*

---

## W14. Livrarea cozii în repo-ul Cloud-ului (2026-10-27)

> **Aditiv.** Nimic din secțiunile de mai sus nu se rescrie.

**Când:** după ce scrii o tichetă în coada locală (`QUEUE/TASKS-FOR-CLOUD.md`),
înainte să o consideri livrată.

**De ce:** Cloud-ul citește coasa din **propriul repo** (`MAVIS-CLOUD`), nu
din repo-ul CI. Măsurat 2026-10-27: 2 tichete locale, **0** la Cloud. Coada
era impecabil formată și nu ajungea nicăieri.

### Pași

```powershell
# 1. măsoară ce nu a ajuns (read-only; nu scrie nimic)
powershell -NoProfile -File scripts\queue-deliver.ps1 -Status

# 2. livrează: scrie, comitează în clona Cloud-ului, publică, verifică
powershell -NoProfile -File scripts\queue-deliver.ps1 -Deliver -Push

# 3. poarta vede absența și confirmă prezența
powershell -NoProfile -File scripts\queue-contract-check.ps1
```

### Când te oprește (toate măsurate)

| Situație | Cod | Ce s-a întâmplat |
|---|---|---|
| corp trunchiat sau gol | `2` | refuzat, nimic scris |
| corp care redeclară un câmp | `2` | refuzat, nimic scris |
| corp care ar deschide o tichetă fantomă | `2` | refuzat, nimic scris |
| secret în schimbare | `2` | refuzat, nimic comitat |
| fără `-Push` | `4` | scris local, **nepublicat** |
| push refuzat de remote | `5` | nimic publicat |

### Reguli

- Livrarea e **aditivă**: tichetele se adaugă, nu se rescriu. Marcarea `[x]`
  a Cloud-ului supraviețuiește.
- Sync-ul păstrează **ambele istorice**: `--ff-only` când clona nu are nimic
  propriu, `merge --no-ff` când are.
- Se verifică **la remote**, nu prin codul de ieșire al lui `git`.
- Dacă ticheta e deja în coada remote-ului, rularea e idempotentă: nu se
  adaugă a doua oară.

Detalii: `docs/BRIDGE-LOCAL-CLOUD.md` §11 · `docs/CONTRACT-CLOUD-QUEUE.md`.
