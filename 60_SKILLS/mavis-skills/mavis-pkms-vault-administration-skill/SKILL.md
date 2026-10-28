---
name: pkms-vault-administration
description: >
  Administrarea, lintul și reconfigurarea sistemului PKMS (Personal Knowledge Management
  System) al lui Popy — vaultul de pe Google Drive. Se declanșează la orice cerință despre
  administrarea vaultului, despre rearanjare când vaultul crește, despre convenția de
  denumire NN-Name, despre cele 6 porți (lint, census, health-check, build-index,
  align-index, verifica-schema), despre cele 4 automatizări zilnice (PKMS-Aliniere,
  PKMS-Watch, PKMS-GitAutoCommit, PKMS-DriveFS-AutoRepair), despre rearanjarea bazelor
  00–09, despre backupul H:, despre „nu șterge, nu muta fără R0", despre repo-ul GitHub
  ca save point și despre restaurarea sistemului din repo. Include incidentul măsurat
  din 19.10.2026: jurnalele vii ale motorului intrau în cifre și țineau arborele de
  indexuri permanent nealiniat.
license: Proprietar — Popy / OPTIMUS PRIME
---

# PKMS — Administrarea sistemului

> **Poziția:** acesta e sistemul, nu un document despre el. Un AI care nu are memorie
> trebuie să poată **administra** vaultul, nu doar să îl citească.

## 0. Ce e vaultul, în cinci rânduri

| | |
|---|---|
| **Unde** | `E:\Google\GDrive\GDrive-Second_Brain_PKMS` — oglinda locală NVMe a Google Drive Cloud |
| **Reper** | **oglinda Google Drive Cloud** (Decizia 1, 21-10-2026): fiecare fișier există în cloud și local, iar egalitatea se verifică **per fișier**, cu `verifica-oglinda.ps1` |
| **Arhivă** | `H:\CLAUDE_Archive` (711.821 fișiere · 180,77 GB, măsurat 21-10-2026) — **se citește, nu se atinge**; e ultimul rând de rezervă, nu reperul |
| **Motor** | `02_Areas\02-2-AI-SOT\02-2-4-AI-Kit\AI-Kit_manual\` — 13 scripturi + 1 cititor read-only |
| **Ghid** | `02_Areas\02-2-AI-SOT\02-2-4-AI-Kit\AI-Kit_guide\` — contractul + documentația |
| **Cotor** | `COTOR.md` la rădăcină (25.735 B) · `AGENTS.md` (4.357 B) · `INDEX CENTRAL.md` (derivat, neversionat) |

## 1. Cele trei adevăruri — și de ce nu se mai creează `index.md` / `log.md`

| Strat (LLM Wiki) | În acest vault | Cine îl scrie |
|---|---|---|
| **Schema** | `COTOR.md` — contractul sistemului | omul, prin reguli; automatul doar verifică |
| **Wiki** | `00_INDEX.md` în fiecare folder + `INDEX CENTRAL.md` | `build-index.ps1` / `align-index.ps1` |
| **Log** | istoricul git + `raport-aliniere.log` + jurnalele `*-registru.txt` | append-only; nu se rescrie niciodată |
| **Raw** | `00_Inbox` … `08_Clippings` | omul |

`index.md` și `log.md` **nu se creează**: fiecare ar fi o a doua adevăr despre același lucru
(`index.md` ar duplica `INDEX CENTRAL.md`, `log.md` ar duplica istoricul git). Puntea dintre
strat și AI este `AGENTS.md` din rădăcină.

**Operațiile, cum arată aici:**

| Operație | Cum arată în acest vault |
|---|---|
| **Ingest** (material nou) | intră în `00_Inbox` → alegi raftul → `align-index.ps1 -DoarCargol '<subarbore>'` reface cotorul acelui raft |
| **Query** | patru citiri, nu scanări: `COTOR.md` → `MANUAL DE NAVIGARE - cotor.md` → `START AICI.md` → `00_INDEX.md` din folderul în care lucrezi |
| **Evoluție** (vaultul crește) | vezi §6 — procedura exactă, în ordine |

## 2. Vocabularul — cele 10 baze, cele 6 rafturi, cele 5 rădăcini ale mașinii

**Baze (`00`–`09`)** — codul e poziția, nu eticheta:

| Cod | Bază | Ce e acolo |
|---|---|---|
| `00` | `00_Inbox` | captură neprocesată (15 la ultima măsurătoare) |
| `01` | `01_Projects` | proiecte cu client, pe rafturi |
| `02` | `02_Areas` | zone: `02-2-AI-SOT` → `02-2-4-AI-Kit` (motorul + ghidul) |
| `03` | `03_Resources` | resurse, biblioteci, insigne |
| `04` | `04_Archive` | arhivă de proiecte |
| `05` | `05_Attachments` | fișiere atașate (imagini, video, documente) |
| `06` | `06_Metadata` | șabloane, agenți, hooks, sarcini programate |
| `07` | `07_Canvas Bases` | baze Canvas (Obsidian) |
| `08` | `08_Clippings` | tăieturi din web |
| `09` | `09_raport-archive` | arhiva rapoartelor de stare |

**Rafturi** (în `01_Projects`): `01-1-Alex - AI Work - Colaborations` · `01-2-AP-ID.ro - AI
Branding Work and Clients` · `01-3-Arhiva Elements - To Monetize` · `01-4-Arhiva Foto - To
Monetize` · `01-5-FORGE - AI JOB Automation` · `01-6-Work_Folder (to sort)`.

**Mașina** (rădăcini cu `_`, **fără cod** — nu sunt „baze"): `_SYSTEM` (automatizare) ·
`_ARCHIVE` (material retras) · `_QUARANTINE` (material izolat, inclusiv `retirat-2026-10-10`).
`09_raport-archive` e singura excepție: are cod, pentru că e o bază, nu o rădăcină de
mașină.

## 3. Convenția de denumire — `NN-Name`

1. **Codul e poziția, nu eticheta.** `07_Canvas Bases` e a șaptea bază, nu „a șaptea
   canvas”. Când baza se rearanjează, codul se schimbă; numele rămâne.
2. **Numerotarea se oprește la al treilea nivel.** Rădăcină → bază → raft → subraft. Sub
   subraft nu mai primește cod.
3. **Rădăcinile cu `_` nu primesc cod** — sunt ale mașinii, nu ale omului.
4. **Sufixul `NN-` cu o cifră, doi cifre pentru nivelul doi** (`02-2-4-AI-Kit`), trei cifre
   la nivelul trei (`01-6-4-In Progress`).
5. **Spațiile sunt permise**; caracterele interzise în numele de folder nu există
   (`lint.ps1` verifică explicit).

## 4. Cele șapte porți — ce măsoară fiecare, și ce înseamnă exit code

Toate se rulează din `AI-Kit_manual` și au nevoie de `PKMS_VAULT`. `PKMS_BACKUP` e
**opțional**: e doar fallback-ul, folosit când oglinda cloud nu poate fi măsurată.

```powershell
$V = 'E:\Google\GDrive\GDrive-Second_Brain_PKMS'
$M = "$V\02_Areas\02-2-AI-SOT\02-2-4-AI-Kit\AI-Kit_manual"
$env:PKMS_VAULT = $V
# $env:PKMS_BACKUP = 'H:\CLAUDE_Archive'   # doar dacă există
```

| Poartă | Comandă | Ce verifică | Verde |
|---|---|---|---|
| **lint** | `lint.ps1` | convenția, indexurile prezente, encoding, backup neatins, documente cheie | `0 erori, 2 atenționi` + exit 0 |
| **census** | `align-index.ps1 -CeVad` | starea fiecărui index: LIPSA / CORUPT / INCOMPLET / **NEALINIAT** / CONFORM | `0 NEALINIAT` |
| **health** | `health-check.ps1` | cifrele vii: fișiere, octeți, pe bază/raft/mașină + stabilitatea măsurătorii | `diferenta 0` între două măsurători |
| **oglindă** | `verifica-oglinda.ps1` | starea reperului: local↔cloud per fișier (md5, dimensiune), sănătatea DriveFS (proces, cozi) | `0 divergente` + exit 0 |
| **build** | `build-index.ps1 [-Quiet]` | regenerează **toți** cei ~2.516 indexuri + `INDEX CENTRAL.md`. **Nu poate fi scoped** | exit 0 |
| **align** | `align-index.ps1 [-DoarCargol '<subarbore>']` | aliniază **doar blocurile derivate**; rândurile omului rămân. Scoped = uneltă sigură | `0 NEALINIAT` |
| **schema** | `verifica-schema.ps1` | contractul §18 — blocurile obligatorii, `De ce e aici`, cuvintele cheie | exit 0 |

**Regula de aur a porților:** o poartă care nu poate eșua nu e poartă. `lint.ps1` dă
`0 erori, 2 atenționi` — **atențiunea e fapt, nu verdict** (3.727 foldere au
`LastWriteTime` după pragul backupului; e consecința copierii, nu dovezi de conținut atins).

**A doua regulă de aur, a reperului:** *„md5 diferit" NU e divergență.* Măsurat pe
2026-10-21, cu experiment controlat: un fișier modificat local și încă neîncărcat în
cloud arată **exact** ca o divergență (md5 diferit, dimensiune diferită) — și se
rezolvă singur în ~5 secunde. Divergența reală e doar: md5 diferit, **nu** în coada de
upload, mtime-uri egale, și veche de peste 48h. Latența e ATENȚIE, nu EROARE — Popy a
acceptat-o explicit ca fiind normală a sistemului bidirectional. Iar o măsurătoare care
**nu a măsurat** (baza nu s-a deschis, arborele nu conține vaultul) raportează
„nemăsurat" și iese cu cod 2 — **niciodată** „0 divergente".

**Ce NU porțile fac:** nu șterg, nu mută, nu redenumesc conținut, nu ating backupul.

## 5. Automatizările — cele patru taskuri

| Task | Când | Ce face | Cum îl verifici |
|---|---|---|---|
| `PKMS-Aliniere` | zilnic 06:00 / 13:00 / 20:00 + **la logon** | `align-index.ps1` — realiniază indexurile | `LastTaskResult = 0` |
| `PKMS-Watch` | zilnic 03:30 | `watch.ps1` — reconciliere cu backupul | `LastTaskResult = 0` |
| `PKMS-GitAutoCommit` | la 5 minute | `git-autocommit.ps1` — comite singur | `LastTaskResult = 0` |
| `PKMS-DriveFS-AutoRepair` | la 5 minute | cârlig: repara DriveFS dacă e degradat | `LastTaskResult = 0` |

```powershell
Get-ScheduledTask -TaskName 'PKMS-*' | ForEach-Object {
  $i = Get-ScheduledTaskInfo -TaskName $_.TaskName
  "{0,-24} state={1} last={2} result={3} next={4}" -f $_.TaskName, $_.State, $i.LastRunTime, $i.LastTaskResult, $i.NextRunTime
}
```

**Defect măsurat, 19–20.10.2026 — cursa de pornire. Reparat și măsurat.** La logon,
`G:` (DriveFS) poate fi încă nemontat. Taskul pornește, calea de lucru nu există →
`ERROR_DIRECTORY` (2147942667 = 0x8007010B). Măsurat: `PKMS-Aliniere` a pornit la
**23:04:40** pe triggerul de logon și a murit cu 2147942667. **Nu e defect de
configurare a taskului** — rularea manuală a *exact* acelei comenzi a ieșit `EXIT=0`
în 629 s, cu 0 NEALINIAT; e o cursă între montarea volumului și pornirea taskului.
**Reparare:** `PKMS-Aliniere`, `PKMS-Watch` și `PKMS-GitAutoCommit` pornesc acum prin
`rula-din-task.ps1`, aflat pe `C:` (`C:\Users\apviz\.minimax\pkms\`), care
**așteaptă calea** (max 300 s), apoi rulează scriptul și îi propagă codul de ieșire.
Probă reală: rulat prin Task Scheduler la **00:48:56**, jurnalul a scris „rulez
watch.ps1". `PKMS-DriveFS-AutoRepair` nu e afectat — scriptul lui e deja pe `C:`.

**Gol de save point, găsit și închis 20.10.2026.** Scriptul cârligului
(`auto-repair-drivefs.ps1`, 9.582 B) exista **doar** pe `C:`. XML-ul lui
`PKMS-DriveFS-AutoRepair` pornește exact acest fișier, deci un restore din repo
înregistra 4 XML-uri, dar al patrulea task murea imediat — save pointul refăcea
**3 din 4** automatizări. Măsurat: `git ls-files` nu returna nimic pentru
`*auto-repair*`, iar RESTORE nu conținea mențiunea `drivefs` (0 potriviri).
**Repar:** scriptul e acum în `automations\` al acestui skill (deschis de
`.gitignore` la nivel de fișier), iar RESTORE §1.6 are pasul care îl copiază în
`C:\Users\apviz\.minimax\drivefs\` **înainte** de înregistrarea XML-urilor.

**Regula:** un `LastTaskResult` nenul la o automatizare e un incident de urmărit, chiar
dacă porțile manuale sunt verzi. Porțile manuale nu acoperă automatizările.

**Al doilea incident, măsurat 20.10.2026 — „raportul zilnic înghețat”.**
`_SYSTEM\rapoarte\raport-ultima-rulare.txt` era înghețat la **18.10.2026 13:21:13**, cu
textul „VOLTUL” și căile vechi de pe `D:`. Două cauze, ambele reale:
(1) `watch.ps1` scria raportul **doar la final** (după toate cele trei trepte);
(2) taskul `PKMS-Watch` avea `ExecutionTimeLimit = PT1H`, **mai scurtă decât o rulare pe
DriveFS** (lint ~2 min + health-check ~5 min + reconcile peste 50 min) — deci taskul era
oprit **înainte** să ajungă la scriere. O automatizare care nu lasă niciun urmă nu e o
automatizare, e o promisiune.
**Reparul:** (a) raportul se **rescrie după fiecare treaptă** (funcția `Actualizeaza-Raport`
în `watch.ps1`), cu verdictul prefixat `IN CURS - N/3 trepte rulate` cât timp nu s-au
terminat toate treptele — ca un raport pe jumătate să nu pară „OK”; (b) limita taskului
ridicată la `PT6H`.
**Probă:** bancă de test în `D:` cu trepte-stub — 15/15 probe. Proba decisivă e cea de
**oprire la mijloc**: procesul e omorât în timpul treptei 3, iar raportul rămâne **proaspăt**
(2/3, verdict „IN CURS”), nu vechi. Parse 0, BOM + LF păstrate, backup în `D:`.

## 6. Când vaultul crește — procedura, în ordine

Nu improviza o rearanjare. Ordinea asta e măsurată, nu preferință:

1. **Măsoară înainte.** `health-check.ps1` → cifrele vii pe bază/raft/mașină.
2. **Decide schema, nu etichetele.** Codul nou intră la poziția lui; baza veche rămâne
   la poziția ei.
3. **Renunmără înainte de a scrie indexuri.** Mutarea unui folder îi schimbă calea, deci
   toate indexurile care îl conțin devin STALE. **Ordinea corectă: mută → renumeră →
   aliniază → abia apoi măsoară cifrele noi.**
4. **Aliniază cu instrumentul, nu cu mâna:**
   `align-index.ps1 -DoarCargol '<subarbore>'` — rescrie **doar blocurile derivate**,
   păstrează rândul `**De ce e aici:**` scris de om.
5. **Regenerează centralul** cu `build-index.ps1` — fișier derivat, nu se patch-ează.
6. **Re-census:** `align-index.ps1 -CeVad` → trebuie să iasă `0 NEALINIAT`.
7. **Actualizează `COTOR.md`** cu cifrele NOI, nu cu cele vechi.
8. **Verifică porțile:** lint → census → health.
9. **Commit + push.** Commitul e automat și nu cere R0. Push-ul cere acordul lui Popy.

**Regula nr. 9 e cea care salvează timp:** după o rearanjare, *cifrele se schimbă* — de
aceea `INDEX CENTRAL.md` e regenerat, nu editat. Un „declarativ" editat manual ar fi
rescris la următoarea rulare a generatorului.

## 7. Regulile absolute — nu se negociază

1. **NIMIC NU SE ȘTERGE.** `Remove-Item` e interzis, inclusiv ca literal într-o comandă.
   Mutarea se face, ștergerea nu. Dacă ceva trebuie să dispară, se mută în `_QUARANTINE`
   **cu `MOTIV.txt`**, și numai cu R0 explicit.
2. **NU MUTI NIMIC fără R0.** (Popy, 19.10.2026) Mutările se propun, nu se execută.
3. **Arhiva se citește, nu se atinge.** `H:\CLAUDE_Archive` e
   reperul de comparație, nu o țintă de lucru.
4. **Backup înainte de fiecare scriere**, sub `D:\PKMS-tooling\handoff\backup\<data>\`.
5. **Encodingul e parte din contract:**
   - documentele `.md` la rădăcină: UTF-8 **fără BOM**, LF
   - scripturile `.ps1`: **BOM** UTF-8 obligatoriu (altfel PS 5.1 citește mojibake)
   - `Set-Content -Encoding UTF8` e interzis pe `.ps1` (scrie BOM + CRLF, strică LF-ul)
   - parse autoritativ: `[System.Management.Automation.Language.Parser]::ParseInput`
6. **Măsoară înainte de a vorbi.** Cifra care nu e măsurată în sesiunea raportului e
   `NOT_MEASURED`, nu o cifră.
7. **Apartenența directă batere similaritatea** pentru verificări de apartenență:
   `git rev-list` / `git ls-remote`, nu „arată cam așa”.
8. **Spațiile în cale se normalizează cu `\\`**, iar comparațiile de cale se fac pe
   numele citit de pe disc, nu tastat din memorie.

## 8. Incidentul de referință — „jurnalul viu intră în cifre"

19.10.2026. Stratul de indexuri nu se putea alinia. Nu oricând: **niciodată**. Două zile
de rulări, cu `align-index` pornit la câteva minute, tot 2 NEALINIAT.

Cauza, măsurată: `raport-autocomit.log` (17.902 B) crește la fiecare commit prin
`git-autocommit.ps1:133`. Logul intra în numărătoarea de fișiere a folderului. Deci:

> aliniere → scrie indexul → autocomitul comite → **logul crește** → indexul e din nou
> nealiniat → aliniere → …

Bucla nu se oprea. Nicio rulare manuală nu o oprea, fiindcă fiecare rulare **era** bucla.

**Reparul:** excluderea jurnalelor vii, **centralizată** în `paths.ps1` →
`Test-PkmsLiveLog` (4 nume: `raport-autocomit.log`, `raport-aliniere.log`,
`arhiva- raport aliniere.log`, `raport-wrapper-task.log`), aplicată **identic** în `build-index.ps1` (3 locuri),
`align-index.ps1` (2 locuri + `$bytes` aliniat cu `$realBytes`) și `verifica-schema.ps1`
(1 loc). Regula a fost scrisă și în contractul §18.7 — altfel contractul și codul s-ar
fi despărțit, exact ce §18.9 interzice.

**Lecția transferabilă:** *când o măsurătoare include un lucru care crește din cauza
măsurătorii, măsurătoarea nu converge.* Exclude cauza, nu doar simptomul.

**A doua lecție, tot din 19.10:** am raportat o „clipire" a fișierelor
`git-autocommit-ignorat.txt` și `git-autocommit-registru.txt`. Era un **typo al meu** —
numele real are `autocommit`, două litere „m". Măsurătoarea la nivel de cod de caracter a
infirmat ștergerea, nealinierea cache-ului DriveFS și caracterele Unicode lookalike.

### Incidentul al doilea, tot din 20.10.2026 — „verdictul orb"

**Aceasta a fost o regresie a mea, introdusă cu o oră mai devreme, în același segment.**
La rescrierea lui `watch.ps1` (pentru scrierea raportului după fiecare treaptă), obiectul
rezultat al fiecărei trepte a rămas cu trei proprietăți în loc de șapte:

```powershell
# forma REGRESATĂ (L285-287)
$rez.Add([pscustomobject]@{ Nume = $t.Nume; Durata = ...; Cod = $cod })
# forma CORECTĂ (pre-fix, L133-136, păstrată în backup)
$rez.Add([pscustomobject]@{ Nume = ...; Durata = ...; Cod = $cod
    Erori = $erori; Atentii = $atentii; Nota = $nota; Detalii = $detalii })
```

Consecința, măsurată pe raportul scris la 01:34:55: `Erori` era `$null`, deci
`$r.Erori -gt 0` era **fals mereu**. Așadar:
- verdictul era **orb** la numărul de erori — o treaptă cu 7 erori și cod de ieșire 0
  ar fi raportat „Erori deocamdata: 0", adică o afirmație **nemasurată**;
- randurile `erori:` și `attentioni:` rămăneau **goale** la fiecare treaptă;
- rândul `masura:` (cifra vie a health-check) nu apărea deloc;
- secțiunea „ATENTII care cer ochiul omului" nu se umplea niciodată.

**Repar:** cele patru proprietăți puse înapoi. `watch.ps1` 14.011 → 14.533 B, parse 0,
BOM UTF-8 + LF păstrate.

**Proba — bancă de 3 probe, cu contra-probă (3/3):**

| Probe | Ce se impune | Ce se cere | Rezultat |
|---|---|---|---|
| 1 — cale fericită | totul 0 | raportul arată NUMERE, verdict `OK`, exit 0 | TRECUT |
| 2 — **decisivă** | lint: 3 erori + 1 atenție, **cod de ieșire 0** | raportul arată 3 și 1, verdict `ATENȚIE:`, exit 1 | TRECUT |
| 3 — **contra-probă** | același lint, cu watch.ps1-**ul regresat** | câmpurile goale și verdict `OK` — **defectul se reproduce** | TRECUT |

Proba 3 e cea care contează: ea arată că proba 2 **poate eșua**. Fără ea, „3/3" ar fi
fost o cifră fără putere de a dezamăgi.

**Lecția transferabilă:** *un automatism care raportează „0" fără să fi măsurat nimic
e mai periculos decât unul care tace.* Câmpul gol arată repede; câmpul plin cu o
valoare nereală minte. Deci: **un verdict care nu poate vedea un număr nu e verdict.**
Verificarea asta intră în §11, la „cum verifici că ai terminat".


## 9. Semne de alarmă — când ceva e rupt

| Semn | Ce înseamnă | Ce faci |
|---|---|---|
| `align-index` raportează NEALINIAT **la nesfârșit** | buclă de măsurătoare (vezi §8) | caută ce **crește** în timp ce măsoară |
| `LastTaskResult` nenul la un task PKMS | incident de automatizare | citește `Microsoft-Windows-TaskScheduler/Operational` |
| `build-index` produce un diff mare | cele două generatoare nu se recunosc | **revert** pe indexuri (git le urmărește), apoi compară octet cu octet |
| `lint` dă erori de encoding | BOM lipsă sau CRLF stricat | verifică primii 3 octeți: `EF BB BF` = BOM |
| `health-check` raportează `diferenta 0` fals | măsurătoarea nu e stabilă | nu raporta cifra până nu e stabilă |
| `git status` arată fișiere care „nu există" | typo în nume | citește numele **de pe disc**, nu din memorie |
| raportul zilnic are câmpuri **goale** (`erori:`, `attentioni:`) | verdictul nu mai vede numărul de erori — regresie în obiectul rezultat | citește `watch.ps1`, obiectul `$rez.Add([pscustomobject]@{...})`: are `Erori`/`Atentii`/`Nota`/`Detalii`? |


## 10. Save point — repo-ul GitHub ca reconstrucție

`https://github.com/apvizual-max/pkms-vault-automation` (ramura `master`) nu e o copie de
conținut. E **programarea sistemului**: motorul, contractul, ghidul, skillurile, definiția
automatizărilor, `.gitignore` cu motivele lui.

Regula `.gitignore`: **repo de automatizare, nu de conținut**. Se deschide explicit
motorul + `**/00_INDEX.md` + `/*.md` + skillurile. Conținutul de client, jurnalele vii,
`INDEX CENTRAL.md` (derivat) și secretele rămân închise. **Fiecare regulă de închidere
poartă motivul ei, măsurat** — o regulă fără motiv e o presupunere, nu o corectie.

**Ce trebuie să fie în repo ca refacerea sistemului să fie posibilă:**

1. cele 12 scripturi din `AI-Kit_manual`
2. contractul `SPECIFICATII - contractul vaultului.md` + documentația din `AI-Kit_guide`
3. `COTOR.md`, `AGENTS.md`, `MANUAL DE NAVIGARE - cotor.md`
4. **skillurile** (`_SYSTEM\Skills_MASTER_Folder\`) — inclusiv acest fișier
5. **XML-urile celor 4 taskuri** — altfel automatizările nu se pot reface
6. `.gitignore` cu motivele lui
7. procedura de restaurare: `RESTORE - reconstructia sistemului.md`
8. **pachetul de handoff** — `handoff-prompt.md` (portul de intrare pentru o sesiune nouă, cu 0 memorie) și `handoff-harta-implementarii.md` (harta construcției, §1–§14). **Măsurat 20.10.2026: erau ABSENȚI din repo** — `git ls-files` dădea 0 intrări, închise de regula `**/*`. Fără ei, restore-ul dădea motor fără doctrină. Deschise prin regula 4c a `.gitignore`; transcriptul (30.412.803 B) rămâne închis, fiindcă e dovada unei sesiuni, nu programarea sistemului.

## 11. Cum verifici că ai terminat

```powershell
# 1. porțile
& "$M\lint.ps1"                       # 0 erori
& "$M\align-index.ps1" -CeVad         # 0 NEALINIAT
& "$M\health-check.ps1"               # stabilitate: diferenta 0

# 2. automatizările vii
Get-ScheduledTask -TaskName 'PKMS-*' | ForEach-Object {
  $i = Get-ScheduledTaskInfo -TaskName $_.TaskName
  "{0,-24} result={1}" -f $_.TaskName, $i.LastTaskResult
}

# 3. git — apartenența directă, nu „arată cam așa"
git -C $V rev-list -n 1 HEAD
git -C $V ls-remote origin master
git -C $V status --porcelain         # gol

# 4. backupul neatins
& "$M\lint.ps1" | Select-String 'backup neatins'
```

## 12. Ce nu s-a făcut, încă

- **Cauza `0x91` în logurile DriveFS** (9.422 apariții, `145 = „The directory is not
  empty"`): necunoscută. Cârligul tratează simptomul, nu cauza. Consemnat ca atare.
- **API-ul Google Drive e rupt** (`invalid_grant`). Operațiile pe Drive se fac prin
  DriveFS; ID-urile de folder se rezolvă din `metadata_sqlite_db`, nu din API.
- **De ce se resetează `pagefile.sys`**: neidentificabil. Restabilirea pe `D:` cere
  privilegii elevate.
