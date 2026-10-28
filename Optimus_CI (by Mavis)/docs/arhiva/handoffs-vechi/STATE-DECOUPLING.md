# STATE-DECOUPLING — 2026-10-12, 05:40

Decuplarea vaultului brut de repo-ul de automatizare. Toate cifrele măsurate.

## 1. Ce s-a decis și ce s-a făcut

| directivă | stare |
|---|---|
| Vault = teritoriu local, **nu** se împinge | ✅ făcut |
| `PKMS Automation` = singurul versionat pe GitHub | ✅ făcut — repo-ul e chiar `pkms-vault-automation` |
| `.gitignore` decuplează conținutul brut | ✅ făcut, pe bază de măsurătoare |
| `git rm --cached`, fără atingerea fișierelor | ✅ făcut prin `git read-tree --empty` + `git add -A` |
| Manualul de cotor + schema de navigare | ✅ făcut: `MANUAL DE NAVIGARE - cotor.md` |

## 2. Dimensiunea finală a repo-ului de automatizare

| | înainte | după |
|---|---|---|
| fișiere urmărite | **50.404** | **43** |
| volum urmărit | ~12 GB | **438,8 KB** |
| `.git` pe disc | **17,40 GB** | **0,29 MB** |
| commituri reachable | 93 (cu conținut brut) | **92, dintre care 0 cu conținut brut** |

Cele 43 de fișiere, grupate:

| grup | fișiere |
|---|---|
| `AI-Kit/` — motorul (18 scripturi + documente) | 18 |
| documentație din rădăcină (inclusiv cele două noi) | 12 |
| `_SYSTEM/Skills/git-autonom` + `git-install` | 6 |
| `_SYSTEM/GORDON - Docker AI` (workflow-uri de delegare) | 4 |
| `_SYSTEM` (index + altele) | 2 |
| `.gitignore` | 1 |

## 3. Verificări făcute

- **conținut brut în istoric**: `git ls-tree -r` pe fiecare dintre cele 92 de
  commituri reachable → **0 commituri cu peste 5.000 de fișiere**. Deci niciun
  blob de conținut nu a supraviețuit rescrierii.
- **secrete în cele 43 de urmărite**: un singur potrivire, la
  `AI-Kit\git-autocommit.ps1:137`, 34 de caractere — e **pattern-ul detectorului
  însuși**, nu o cheie (un token Telegram real are 46). **Niciun secret real.**
- **date personale în cele 43**: `+40 7…`, `apvizual@gmail`, `apvizual-max` →
  **0 potriviri**. `INDEX CENTRAL.md` rămâne exclus, tocmai pentru că ăsta e
  singurul document cu nume de foldere și clienți.
- **conținut pe disc**: 52.463 fișiere, față de 52.949 la snapshot. Diferența
  e **doar `.git`**: 524 → 35 de fișiere interne, după `gc`. Restul: `05_Attachments`
  **+2** (capturile tale de azi). **Zero fișiere de conținut pierdute.**

## 4. Două capcane măsurate, care se repetă

1. **`.gitignore` nu se aplică fișierelor deja urmărite.** `git add -A` le ține
   în index oricât de des se rescrie regula. Singura cale curată:
   `git read-tree --empty`, apoi `git add -A`. `git rm -r --cached .` **eșuează**
   pe repo-uri imbricate („use -f to force removal") și **anulează tot** — nu
   șterge nimic, iar agentul care raportează „am decuplat" a mint.
2. **Deschiderea unui părinte redeschide tot subarborele.** `!/_SYSTEM/Skills/`
   a readus 9.740 de fișiere din `Skills_Archive` până când copiii nedoriti au
   fost închiși **după** deschideri. Ultima regulă care se potrivește câștigă.

3. **Părintele se ia înainte de comit, nu după.** Am luat `HEAD~1` după commit și
   am descoperit că părintele era chiar comitul cu conținutul brut — deci
   rescrierea nu eliminase nimic, doar mutase comitul. Corect: `HEAD~3`.

## 5. Starea remoting-ului

`pkms-vault-automation` are **61 de commituri neîmpinse**. **Nu s-a împins** — și
nu se cere automat: R0-ul „vault nu se împinge" a fost dat pentru 9,84 GB de
conținut personal. Acum e altă situație, măsurată:

| | |
|---|---|
| ce ar urca | 43 de fișiere · 438,8 KB · motor |
| scanare de secrete | curată |
| scanare de date personale | curată |

**Punctul de decizie e al lui Popy**, pentru că e o schimbare de natură a
obiectului împins, nu o decizie tehnică.

## 6. Ce NU am făcut

- Nu am atins conținutul: niciun `rm`, niciun `Move-Item`, nicio ștergere.
- Nu am modificat `MAVIS-CLOUD` (read-only).
- Nu am împins niciun repo nou.
- Nu am rulat `build-index.ps1` — cotorul e derivat și se regenerează la cerere.