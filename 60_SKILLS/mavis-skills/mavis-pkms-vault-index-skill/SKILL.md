---
name: pkms-vault-index
description: >
  Indexarea și alinierea automată a vaultului PKMS — contractul `00_INDEX.md`, cele cinci
  stări (LIPSA / CORUPT / INCOMPLET / NEALINIAT / CONFORM), cine deține fiecare piesă,
  regula „jurnalele vii nu sunt conținut", contractul de convergență dintre cele două
  generatoare (build-index ↔ align-index), blocurile „De ce e aici" și „Cuvinte cheie",
 zonele interzise, logul `raport-aliniere.log`, cele cinci automate și comutatoarele
  lor. Se declanșează la orice întrebare despre `00_INDEX.md`, `build-index.ps1`,
  `align-index.ps1`, `aliniere-conditionala.ps1`, `raport-saptamanal.ps1`, `watch.ps1`, `verifica-schema.ps1`, despre cifrele din indexuri sau
  despre faptul că un folder rămâne „nealiniat".
license: Proprietar — Popy / OPTIMUS PRIME
---

# PKMS — Indexarea și alinierea

> **Indexul nu e conținut.** E harta. Se rescrie, se măsoară, se verifică. Nu se citeste
> ca autoritate — autoritatea e conținutul de pe disc.

## 1. Contractul de navigare

Fiecare folder de conținut are **exact un** `00_INDEX.md`, generat. Structura:

```
# 00_INDEX — <calea relativă>
**N fișiere · X KB · Y subfoldere**
> Generat automat de `02_Areas/02-2-AI-SOT/02-2-4-AI-Kit/AI-Kit_manual/build-index.ps1` și `align-index.ps1`. Nu edita manual — rulează scriptul din nou.
> Randul **De ce e aici** de mai sus, daca exista, se pastreaza la fiecare regenerare.
## Ce e aici          ← BLOC DERIVAT (propozitie + extensii)
## Cuvinte cheie      ← BLOC DERIVAT (identitatea folderului)
## Fișiere            ← BLOC DERIVAT (tabel)
```

**Rândul `**De ce e aici:**`** e singurul rând scris de om. Generatorul îl păstrează
la fiecare regenerare. E acolo ca un AI fără memorie să știe *de ce* există folderul, nu
doar *ce* e în el. **Nu se rescrie niciodată automat.**

**Blocurile derivate** sunt singurele pe care automatul le poate suprascrie. Tot ce e
în afara lor, într-un `00_INDEX.md`, e reziduu — și reziduul e defect.

## 2. Cele cinci stări

| Stare | Ce înseamnă | Cine repară |
|---|---|---|
| **LIPSA** | folderul nu are `00_INDEX.md` | `align-index` îl creează |
| **CORUPT** | indexul există dar nu e parsabil (blocuri lipsă, tabel rupt) | `align-index` îl reface de la zero |
| **INCOMPLET** | indexul există dar îi lipsește un bloc obligatoriu | `align-index` completează blocul, **păstrând motivul** |
| **NEALINIAT** | indexul există, e complet, dar cifrele nu mai corespund conținutului | `align-index` rescrie **doar blocurile derivate** |
| **CONFORM** | indexul corespunde conținutului | nimeni — nu se atinge |

**CONFORM nu înseamnă „corect" în sens absolut.** Înseamnă „concordant cu măsurătoarea
de azi". Dacă măsurătoarea e greșită, indexul e greșit în mod consistent — și de aceea
e atât de important ca măsurătoarea să fie măsurată la nivel de octet, nu estimată.

## 3. Cine deține ce

| Piesă | Proprietar | Ce poate rescrie |
|---|---|---|
| `00_INDEX.md` (blocuri derivate) | `build-index.ps1` / `align-index.ps1` | automatul, integral |
| rândul `**De ce e aici:**` | omul | **numai omul** — automatul îl păstrează |
| `INDEX CENTRAL.md` | `build-index.ps1` | generatorul, integral; nu se patch-ează |
| logul `raport-aliniere.log` | `align-index.ps1` | append-only |
| `.gitignore` | omul, cu motive scrise | omul |

**`align-index` nu creează niciodată conținut și nu atinge backupul.** Citește
conținutul, calculează cifrele, scrie blocurile derivate. Restul rămâne.

## 4. Regula „jurnalele vii nu sunt conținut" — §18.7

Cele patru jurnale ale motorului **cresc în timp ce rulează**:

| Jurnal | Unde | De ce crește |
|---|---|---|
| `raport-autocomit.log` | `AI-Kit_manual\` | `git-autocommit.ps1:133` adaugă la fiecare commit |
| `raport-aliniere.log` | `AI-Kit_guide\` | fiecare rulare de aliniere adaugă un eveniment |
| `arhiva- raport aliniere.log` | `AI-Kit_guide\` | arhiva fiecărei rulări |
| `raport-wrapper-task.log` | `AI-Kit_manual\` | `rula-din-task.ps1` scrie la fiecare pornire de task |

**Regula (contractul §18.7):** aceste patru nume nu intră în numărătoarea de fișiere a
folderului care le conține. Lista e **într-un singur loc** — `paths.ps1` →
`Test-PkmsLiveLog` — și e aplicată identic în `build-index.ps1` (3 locuri),
`align-index.ps1` (2 locuri + `$bytes` aliniat cu `$realBytes`) și `verifica-schema.ps1`
(1 loc).

**De ce centralizat:** dacă fiecare generator ar exclude singur, unul din ele ar scrie
indexuri pe care celălalt le-ar rescrie la nesfârșit. O listă într-un singur loc e
singura formă în care contractul și codul nu se pot despărți.

**Ce NU se exclude:** `raport-ultima-rulare.txt` și arhivele `raport-*.txt` din
`_SYSTEM\rapoarte`. Excluderea lor ar face folderul „gol" la §18.5 — o minciună în
cifre. Și taskul lor era mort, deci n-ar fi observat.

## 5. Contractul de convergență (§18.9)

Cele două generatoare trebuie să producă **același text** pentru același folder. Altfel
ciclul se reînnoiește la nesfârșit.

| | `build-index.ps1` | `align-index.ps1` |
|---|---|---|
| **Scope** | tot arborele, obligatoriu | poate fi scoped (`-DoarCargol`) |
| **Ce scrie** | tot ce găsește | **doar blocurile derivate** ale celor NEALINIAT |
| **Când** | rearanjare, schimbare de cifre | mentenanță de zi cu zi |
| **INDEX CENTRAL.md** | îl rescrie | nu |
| **Logul** | nu atinge `raport-aliniere.log` | îl scrie |

**Proba de echivalență (măsurată 19.10.2026):** 2.511 foldere ale căror indexuri
fuseseră scrise de `build-index` la 11:29 au fost găsite **CONFORM** de `align-index` la
22:37 — deci textul produs de cele două e identic. Plus: `align-index` **păstrează
capul cu atribuirea** („Generat automat de `02_Areas/02-2-AI-SOT/02-2-4-AI-Kit/AI-Kit_manual/build-index.ps1` și `align-index.ps1`"), deci rularea
`build-index` nu produce ping-pong.

**Proba de echivalență, măsurată 22.10.2026:** după o regenerare integrală — `build-index.ps1` a
rescris 2.616 de indexuri în 74,7 s — `align-index.ps1 -CeVad` a raportat **0 LIPSA ·
0 CORUPT · 0 INCOMPLET · 0 NEALINIAT · 2.616 CONFORM** și **0 evenimente de log**. Deci
cele două generatoare converg la scară întreagă, nu doar pe un eșantion.

Și ambele scriu **același** text de proveniență, cu calea reală a motorului. Masurat
pe disk: 6.591 de indexuri in total, dintre care 2.616 scrise de motor — toate cu
aceeasi nota de provenienta. Celelalte 3.975 sunt in `_QUARANTINE\indexuri generate
in gresit\`, zona pe care ambele generatoare o exclud (sunt martorii unui defect),
deci pastreaza forma veche prin design.

**Asimetria măsurată în 19.10.2026 — probată și închisă în 22.10.2026.** La
măsurarea din 19.10, `align-index` scria cu **un newline final în plus**
(`Set-Content` adaugă peste EOL deja prezent) și **nu repara un rând de stare
stale**. Ambele au fost **probe izolate pe un folder real, astăzi**, prin
perturbare controlată urmată de rescriere:

- blocuri derivate trunchiate → `align-index` raportează **INCOMPLET** și scrie
  înapoi **632 octeți, identici octet cu octet** cu ieșirea lui `build-index`;
- rând de stare stricat la „999 fișiere" → raportează **NEALINIAT** și îl
  readuce la valoarea corectă (**1 fișiere · 196 B · 0 subfoldere**), tot
  octet cu octet identic.

`git status` a rămas **gol** după ambele probe: zero drift în vault. **Nu există
asimetrie între cele două generatoare** — pentru același folder, `build-index`
și `align-index` scriu aceiași octeți. Diferența reală rămasă e de **conținut**,
nu de format: `align-index` reînnoiește doar blocurile derivate și rândul de
stare, pe când `build-index` rescrie tot arborele (de aceea rulează doar după
mutări în masă).

## 6. Reparația se face din datele lui

Nu inventa. La o stare NEALINIAT:

1. citește conținutul real al folderului (număr, octeți, extensii, cele mai mari
   elemente) — **de pe disc, nu din index**;
2. recalculează cifrele cu **aceeași** măsurătoare pe care o folosește `build-index`
   (de aceea `$bytes` din `align-index` a fost aliniat cu `$realBytes`);
3. scrie **doar blocurile derivate**;
4. **păstrează** rândul `**De ce e aici:**` — dacă nu e clar al cui rând e, nu scrie
   nimic (`$refuz`).

## 7. Indexul unui folder gol

Un folder gol primește index oricum, cu marcatul „gol" (§18.5) — **altfel ar fi
invizibil** și un AI fără memorie nu ar ști că există. Nu se inventează conținut pentru
a-l umple. Măsurătoarea rămâne corectă: 0 fișiere, 0 octeți.

## 8. Ce nu intră niciodată sub automat

- `00_INDEX.md` în **backup** — backupul nu e al automatului.
- Fișierele din `_QUARANTINE` — nu se ating; `retirat-2026-10-10` e raft retras, cu
  motiv scris.
- Secretele: `*.pem`, `*.key`, `id_rsa*`, `**/credentials.json`, `**/client_secret*.json`.
  Un secret intrat în istoric nu se mai scoate curat.
- Zonele interzise: `.obsidian`, `.git`, `.trash`, `.vault-intelligence`, `.claudian`,
  `.neural_memory`, `.sentinel_temp`, `.wwebjs_cache`, `node_modules`.
- **Rădăcina unei zone interzise se indexează, interiorul nu.** Altfel un AI ar crede
  că `.obsidian` e conținut de proiect.

**Tipare, nu scriere cu `\`:** pentru o cale, `([\\/]|$)` — bara finală obligatorie.
Doar `\\.git\\` se potrivește în interiorul unei căi, nu la capătul ei; de aceea `.git`
de la rădăcină rămânea neprotejat. Iar `[\\/]` înseamnă „o bară înclinată, în orice
sens" — nu scrie `\` ca `\\` într-un regex PowerShell.

## 9. Logul: `raport-aliniere.log`

Append-only. Fiecare rulare adaugă un eveniment: câte foldere au fost verificate, câte
rescrise, ce s-a refuzat și de ce. **Nu se rescrie niciodată.**

Logul e în `AI-Kit_guide\`, iar **folderul care îl conține nu poate fi indexat cu
fișierele lui** — de aceea e în lista din §4. Logul e stare, nu conținut.

`inchide-log.ps1` îl arhivează (mută, nu șterge) în `_SYSTEM\arhiva-indexe\`.

## 10. Comutatoarele văzute în cod

| Script | Comutator | Ce face |
|---|---|---|
| `align-index.ps1` | `-CeVad` | **nu scrie nimic**; doar raportează. Singurul mod sigur de diagnostic |
| `align-index.ps1` | `-DoarCargol '<subarbore>'` | scope la un subarbore; singurul mod sigur de rearanjare |
| `build-index.ps1` | `-Quiet` | nu afișează summary-ul; **nu** schimbă ce scrie |
| `build-index.ps1` | — | nu poate fi scoped. Rulează pe tot arborele |

## 11. Cum se opreste

**Censusul nu se oprește la primul NEALINIAT.** Citește tot arborele, raportează tot.
Un raport trunchiat e un raport fără verdict.

Verdictul se citește în ultima linie:

```
rezumat: 0 LIPSA · 0 CORUPT · 0 INCOMPLET · 0 NEALINIAT · 2516 CONFORM · 2516 nemodificate
evenimente de log: 0 (CeVad: logul NU s-a atins)
duble cai prin puncte de legatura: 0
foldere cu mai putin de 2 cuvinte cheie, raportate §16: 0
```

**Cifrele se măsoară în sesiunea raportului.** O cifră din ieri, într-un raport de azi,
e `NOT_MEASURED`.

## 12. Cifrele de referință (19.10.2026, măsurate)

| | |
|---|---|
| foldere indexate | **2.516**, toate CONFORM |
| `INDEX CENTRAL.md` | 962.335 B · „Actualizat: 2026-10-19 22:32" · 16.125 fișiere · 83,70 GB indexate |
| vault total (health-check) | 50.728 fișiere · 85,75 GB · stabilitate 50.728/50.728, diferența 0 |
| scripturi | 11, toate parse 0 erori, encoding 11/11 |
| `build-index` | EXIT=0 în 331 s · 58 indexuri rescrise |
| `align-index` (scriere) | 5 NEALINIAT reparate · 2.511 CONFORM · 177 s |

**Cele două cifre mari nu se contrazic:** `INDEX CENTRAL.md` măsoară **substratul
indexat** (fără zonele excluse), `health-check` măsoară **tot vaultul**. Scope diferit,
nu eroare.

## 13. Cifrele de referință (22.10.2026, măsurate)

| | |
|---|---|
| foldere indexate | **2.616**, toate CONFORM (census `align-index -CeVad`) |
| indexuri pe disc | 6.591 — 2.616 cu nota de proveniență nouă (2.615 în afara zonei de martori + rădăcina zonei) și 3.975 în `_QUARANTINE\indexuri generate in gresit`, cu forma veche (martori, excluși prin design) |
| `INDEX CENTRAL.md` | 992.622 B · „Actualizat: 2026-10-22 05:18" · 16.653 fișiere · 86,67 GB indexate |
| vault total (health-check) | 51.319 fișiere · 88,72 GB (măsurat 22.10 09:02, prin raportul săptămânal) |
| oglinda cloud (verifica-oglinda) | 52.403 fișiere · md5 identice 52.400 (măsurat 05:45) · **divergență 0** · latență 1 (măsurat 22.10 09:02) — oglinda e vie, cifrele drift-ează |
| scripturi | 15 `.ps1` + 1 `.js` — parse 0 erori, encoding 15/15 |
| `build-index` | regenerare integrală: 2.616 indexuri rescrise în 74,7 s, EXIT=0 |
| `align-index` (scriere) | probe izolate pe `00_Inbox/00-1-WhatsApp`: INCOMPLET reparat și NEALINIAT reparat, ambele **octet cu octet** identice cu `build-index` |
| lanț `watch` | 3 trepte, toate codurile de ieșire 0, 0 erori, 0 atenții, 46 s |
| taskuri | **5/5** cu `LastTaskResult=0` — `PKMS-Aliniere` (next 22.10 15:00), `PKMS-RaportSaptamanal` (next 26.10 08:00), `PKMS-Watch` (23.10 03:30), `PKMS-GitAutoCommit` + `PKMS-DriveFS-AutoRepair` (la 5 min) |
| arhiva de indexe | 49 de runuri în `_SYSTEM\arhiva-indexe` — fiecare rulare cu scriere își arhivează versiunea veche |
| raport săptămânal | prima rulare prin task, 22.10 09:02: **6 porți toate verzi**, `VERDICT: IN ORDINE`, 0 erori, 1 atențiune, 131 s |
| repo | `master`, arbore curat, **701 fișiere urmărite** (din care 625 indexuri), local = remote |

**Cifrele de la §12 rămân istoric**: erau corecte pe 19.10 și sunt păstrate ca
atare, pentru că §12 e datat. Cifrele de aici sunt cele măsurate acum.

## 14. Rutina zilnică și raportul săptămânal (22.10.2026)

Indexurile nu stau loc: se schimbă, se mută, se creează. Ca să nu fie nevoie de
intervenție manuală, alinierea e automată, dar **condiționată** — și reconstruirea
completă e tot la cerere.

| Automat | Când | Ce rulează | Ce scrie |
|---|---|---|---|
| `PKMS-Aliniere` | la autentificare + **09:00, 15:00, 22:00** | `aliniere-conditionala.ps1` | doar arborii nealiniați, **numai dacă există nealiniere** |
| `PKMS-RaportSaptamanal` | **luni, 08:00** | `raport-saptamanal.ps1` | **un raport**; nu repara |
| `PKMS-Watch` | zilnic, **03:30** | `watch.ps1` | doar raportul zilnic |
| `PKMS-GitAutoCommit` | la 5 minute | `git-autocommit.ps1` | commit autonomous |
| `PKMS-DriveFS-AutoRepair` | la 5 minute | DriveFS | nimic în vault |

**Regula de aur, măsurată:** automatul care aliniază **întreabă întâi**. Face
census (`align-index -CeVad`, care nu scrie nimic), și doar dacă găsește nealinieri
rescrie arborii afectați. Probe pe vaultul real:

- cu schimbări: 2 nealiniere găsite → reparate → confirmare **2.616 CONFORM / 0
  rămase**, 181 s, cod 0;
- fără schimbări: „nimic de făcut" — **6.617 fișiere comparate înainte și după,
  zero diferențe** în afara celor două jurnale vii (jurnalul de aliniere **neatins**,
  arhiva de indexe **46 de runuri înainte și 46 după**).

**`build-index.ps1` nu e în rutină.** Rescrie tot arborele (2.616 indexuri, ~74 s) și
e intervenție: se rulează cu mâna, după mutări în masă.

**Ore locale, nu instante absolute.** Declanșatorii au `StartBoundary` fără
designator de fus orar. Cu `+03:00` explicit, granița e un instant absolut, iar
România trece la EET pe 25.10.2026 — programarea s-ar fi derivat cu o oră.
Măsurat: 08:00 cu offset → `NextRunTime 07:00`; fără offset → `08:00`.

