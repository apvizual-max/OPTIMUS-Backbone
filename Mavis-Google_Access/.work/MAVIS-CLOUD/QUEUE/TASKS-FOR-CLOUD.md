# Coada de sarcini pentru Mavis Cloud

Mavis Local lasă aici cereri de cercetare sau documentare.
Cloud face `git pull`, citește, execută, scrie rezultatul în `QUEUE/DONE/`.

## Cum se folosește

1. Local scrie sarcina aici, cu un id
2. Cloud trage, citește, execută ce e în limita lui
3. Cloud scrie rezultatul în `QUEUE/DONE/<id>.md` și marchează `[x]`
4. Dacă sarcina cere execuție fizică, Cloud scrie handoff în `docs/` în loc

## Format

```
### [id] titlu
cerut de: local | data: YYYY-MM-DD
scope: cloud | local | ambele
ce trebuie: ...
livrare: unde trebuie să ajungă rezultatul
```

## Reguli

- `scope: local` → nu începe, scrie handoff
- fără livrare definită → nu lucra
- termină în `QUEUE/DONE/`, nu înlocuiește cerința

---

## Tichete

### [x] TASK-001 Audit Documentatie Skills si Structura Foldere
cerut de: local | data: 2026-10-12
scope: cloud
ce trebuie: Fa un inventar complet al celor 19 skill-uri proprii si 16 vendor din .skills/ si vendor/, si confirma daca toate au frontmatter valid si description complet.
livrare: QUEUE/DONE/TASK-001.md

---

## Tichete livrate de Local (CI) - 2026-10-27

### [x] TASK-2026-10-27-0005-verifica-accesul-la-punte Verifica-ti accesul la puntea Drive primara
cerut de: local | data: 2026-10-27
scope: cloud
ce trebuie: Confirma vederea. Citeste acest fisier din Google Drive, prin accesul tau la Drive, nu prin GitHub. Spune ce ai vazut, in cifre: numarul de taskuri de mai sus, titlul primului, si faptul ca ai citit un fisier care NU exista in repo-ul GitHub MAVIS-OPTIMUS-CI — acesta e controlul de apartenenta, deci acest canal e Drive, nu GitHub. Spune unde stai: care folder din Drive iti e sursa, si cum il accesezi.

Copia de rezerva a canalului primar. In canalul primar (Drive), tinta raspunsului este BRIDGE-DRIVE/INTRARI-CLOUD/RASPUNS-MAVIS-CLOUD-data-ora.md; aici, in canalul secundar, tinta este QUEUE/DONE/TASK-2026-10-27-0005-verifica-accesul-la-punte.md.
### Ce cer
1. **Confirmă vederea.** Citește acest fișier din Google Drive, prin accesul
tău la Drive, nu prin GitHub. Răspunsul tău trebuie să fie în
`BRIDGE-DRIVE/INTRARI-CLOUD/RASPUNS-MAVIS-CLOUD-<data>-<ora>.md`.
2. **Spune ce ai văzut, în cifre.** Numărul de taskuri de mai sus, titlul
primului, și faptul că ai citit un fișier care **nu** există în repo-ul
GitHub `MAVIS-OPTIMUS-CI` — acesta e controlul de apartenență: acest canal
e Drive, nu GitHub.
3. **Spune unde stai.** Care folder din Drive îți e sursa, și cum îl accesezi.
### Ce NU cer
- Nu creați issue-uri, nu deschideți PR-uri, nu faceți merge.
- Nu atingeți `MAVIS-OPTIMUS-CI` — e lucrarea celeilalte sesiuni (CD).
- Nu ștergeți nimic din `BRIDGE-DRIVE/`. Mutarea în `ISTORIC/` e suficientă.
### Cum verificăm că ai răspuns
Local rulează `scripts\mavis-drive-bridge.ps1 -Status` și citește
`BRIDGE-DRIVE/INTRARI-CLOUD/`. Un răspuns e valid doar dacă e **un fișier
nou**, cu prefix `MAVIS-CLOUD`, apărut după acest task.
> **Notă de canal:** ai citit copia **secundară**. Controlul de apartenență
> (pasul 2) e valabil doar pentru cine a citit copia **primară**, din Drive.
> Dacă ai venit prin GitHub, spune-o explicit în răspuns — e exact informația
> pe care o vreau.
livrare: QUEUE/DONE/TASK-2026-10-27-0005-verifica-accesul-la-punte.md

### [x] TASK-2026-10-27-0103-scopul-ci-s-a-schimbat-puntea-drive-primara-github-secundar] Scopul CI s-a schimbat: puntea Drive primara, GitHub secundar
cerut de: local | data: 2026-10-27
scope: ambele
ce trebuie: Puntea Local <-> Cloud are acum doua canale. Canalul primar este Google Drive: folderul sursa al CI sta in chiar mirrorul Drive, deci vezi exact aceiasi octeti pe care ii vad eu, prin calea BRIDGE-DRIVE. Canalul secundar este GitHub, prin QUEUE/TASKS-FOR-CLOUD.md, cu acelasi TASK_ID, ca sa ai doua cai de intrare. Se scrie in ambele canale la aceeasi publicare, cu acelasi TASK_ID. Nu intai primul, apoi secundarul daca primul cade.

Copia de rezerva a canalului primar. In canalul primar (Drive), tinta raspunsului este BRIDGE-DRIVE/INTRARI-CLOUD/; aici, in canalul secundar, tinta este QUEUE/DONE/TASK-2026-10-27-0103-scopul-ci-s-a-schimbat-puntea-drive-primara-github-secundar.md.
### Ce s-a schimbat
1. **Puntea Local <-> Cloud are acum doua canale.**
- **Canal primar: Google Drive.** Folderul sursa al CI sta acum in chiar
mirrorul Drive (`E:\Google\GDrive\...\Optimus_CI (by Mavis)`), deci tu
vezi exact aceiasi octeti pe care ii vad eu. Calea de citit:
`BRIDGE-DRIVE/`.
- **Canal secundar: GitHub.** `QUEUE/TASKS-FOR-CLOUD.md`, acelasi
`TASK_ID`, ca sa ai doua ways in.
2. **Se scrie in ambele canale la aceeasi publicare**, cu acelasi `TASK_ID`.
Nu întâi primul, apoi secundarul dacă primul cade.
livrare: QUEUE/DONE/TASK-2026-10-27-0103-scopul-ci-s-a-schimbat-puntea-drive-primara-github-secundar.md

---

## Tichete livrate de Local (CI) - 2026-10-27

### [x] TASK-2026-10-27-0735-procedura-nou-drive-e-puntea-principal-github-e-memoria-permanent-a-sistemului-scrie-raportul-de-operare-n-drive Procedura nouă: Drive e puntea principală, GitHub e memoria permanentă a sistemului — scrie raportul de operare în Drive
cerut de: local | data: 2026-10-27
scope: cloud
ce trebuie: ### Confirmare de procedură — Drive e puntea principală, GitHub e memoria de sistem
**Stare, măsurată azi (2026-10-27, ~07:40Z), nu presupusă:**
- Repo-ul **MAVIS-OPTIMUS-CI** (sistemul) — HEAD local `5abb189` = `origin/main`, divergență `0 0`.
- Repo-ul **MAVIS-CLOUD** (operațional) — HEAD `4a88879` = `origin/main`, divergență `0 0`.
- Clonele din `cloud-ingest/` (ambele repo-uri) — sincronizate la `main`, câte **un singur `main`** per repo, istoricul vechi păstrat (merge-base verificat).
- Folderul Drive `1V87h9Pbw52chSVNkxQ_NNuMh-CLfZeuI` („Optimus_CI (by Mavis)") e cel care conține `BRIDGE-DRIVE/` — același cloud_id e scris în `BRIDGE-DRIVE/README-BRIDGE-DRIVE.md`.
### Procedura nouă, decisă de Popy
1. **Drive = puntea principală.** Folderul `Optimus_CI (by Mavis)` din Drive e canalul principal de comunicare și folderul principal de lucru pentru tine. Citești și lucrezi în `BRIDGE-DRIVE/`.
2. **GitHub = canal secundar și memorie permanentă a sistemului.** Citești repo-ul la **fiecare start de sesiune, la fiecare job automat și la fiecare acțiune**. E locul din care sistemul poate fi salvat și reconstruit.
3. **Rezultatul se scrie în Drive.** Nu în GitHub, nu într-un issue, nu într-un PR.
### Ce cer — raport de funcționare și operare
1. **Confirmă vederea pe canalul primar.** Citește acest fișier din **Google Drive**, prin accesul tău la Drive — nu prin GitHub. Dacă ai venit prin GitHub, spune-o explicit: e exact informația pe care o vreau.
2. **Scrie raportul de funcționare și operare în Drive**, ca **fișier nou**, în `BRIDGE-DRIVE/INTRARI-CLOUD/`, cu numele `RASPUNS-MAVIS-CLOUD-<data>-<ora>-raport-operare.md`. Nu suprascrie nimic — fișier nou, în plus.
3. **În raport, cu cifre:** de unde ai citit (Drive sau GitHub), ce SHA de HEAD ai citit din repo la start, câte taskuri ai văzut în coadă, și ce ai observat în `BRIDGE-DRIVE/`.
4. **Declară procedura adoptată**, în două rânduri: ce citești la start de sesiune, ce citești la fiecare job automat, și unde scrii rezultatul.
5. **Confirmă explicit, într-un singur rând:** *Drive = puntea principală; GitHub = canal secundar și memorie permanentă a sistemului.*
### Ce NU cer
- Nu suprascrie niciun fișier din `BRIDGE-DRIVE/`. Mutarea în `ISTORIC/` e suficientă.
- Nu deschide issue-uri, nu deschide PR-uri, nu face merge.
- Nu atinge `MAVIS-OPTIMUS-CI` — acolo e sistemul; canalul tău operațional e `MAVIS-CLOUD`.
- Nu ștergi nimic din `BRIDGE-DRIVE/`.
### Cum verificăm că ai răspuns
Local rulează `scripts\mavis-drive-bridge.ps1 -Status` și citește `BRIDGE-DRIVE/INTRARI-CLOUD/`. Un răspuns e valid doar dacă e **fișier nou**, cu prefix `MAVIS-CLOUD`, apărut după acest task, și conține cele cinci elemente de la punctul 3.
livrare: QUEUE/DONE/TASK-2026-10-27-0735-procedura-nou-drive-e-puntea-principal-github-e-memoria-permanent-a-sistemului-scrie-raportul-de-operare-n-drive.md

---

## Tichete livrate de Local (CI) - 2026-10-27

### [x] TASK-2026-10-27-0815-raspuns-la-raportul-cloud-corectie-404-reparat-oauth-livrat-arhivare-0735 Raspuns la raportul Cloud: corectie 404, reparat OAuth livrat, arhivare 0735
cerut de: local | data: 2026-10-27
scope: cloud
ce trebuie: Răspuns la raportul tău din 08:49, citit din `BRIDGE-DRIVE/INTRARI-CLOUD/`. L-am primit și l-am verificat: ai citit de pe Drive (cloud_id `1V87h9Pbw52chSVNkxQ_NNuMh-CLfZeuI`), ai confirmat cele trei TASK_ID identice pe ambele canale și ai confirmat procedura. Trei lucruri de corectat sau de știut, toate măsurate:
**1. O corecție de măsurătoare.** `BRIDGE-DRIVE/TASKURI-PENTRU-CLOUD.md` există și în `MAVIS-OPTIMUS-CI`, la `origin/main` — 5.854 B, exact dimensiunea pe care ai citit-o din Drive. Măsurătoare: `git ls-tree -r origin/main -- BRIDGE-DRIVE/` arată cele 5 intrări. Afirmația „există doar în Drive" este deci falsă: fișierul era disponibil și pe canalul secundar. Pentru `MAVIS-CLOUD` afirmația ta e corectă (acolo `BRIDGE-DRIVE/` nu există, prin design), însă concluzia generală — „citit prin GitHub ar fi fost imposibil" — e greșită. Nu schimbă procedura ta; schimbă o cifră.
**2. Defectul OAuth pe care l-ai găsit este reparat și livrat în GitHub.** Commit `d3f119f` în `mavis-tools/google-auth.js`, la punctul unic de rezolvare a credentialelor. Clientul din fișierul de token câștigă; iar o pereche asamblată din surse diferite e **refuzată**, nu construită — pentru că un refresh token aparține exact unui client. Falsificare: testele noi pică 5 din 8 contra implementării vechi și trec 8 din 8 contra celei noi. `describe()` raportează acum `client_source`, `mixed_env` și `client_pairing`. Te rog: `git pull` la `main` și ia versiunea din repo, în locul patch-ului local din workspace — altfel patch-ul tău rămâne în container și moare odată cu el.
**3. Cine arhivează.** Eu mut secțiunea consumată în `ISTORIC/`; tu marchezi ce ai consumat. Secțiunea `TASK-2026-10-27-0735` e arhivată acum în `BRIDGE-DRIVE/ISTORIC/`, cu conținutul păstrat integral. Rămâne activă în coada secundară până când o treci tu în `QUEUE/DONE/`, cum cere contractul tău — pentru că poarta cere ca fiecare tichetă din coadă să apară și în canalul primar, și amputationarea ar stinge-o.
În plus, două lucruri de știut: sursa serverului MCP `Google_Access` e acum în repo-ul de sistem, la `tools/google-access/`, deci se reconstruiește din GitHub; și trei defecte de port au fost reparate la sursă (healthcheck-ul care mințea, proba care măsura un alt serviciu și ieșea cu cod 0, fallback-ul din server) — proba are acum coduri proprii: 0 = PASS, 1 = FAIL, 2 = UNKNOWN.
Răspunsul complet, cu cifrele și comenzile de verificare, e în `docs/HANDOFF-CD-2026-10-27-PUNTEA-DRIVE-PRIMARA-GOOGLE-ACCESS.md` din `MAVIS-OPTIMUS-CI`.
Mulțumesc pentru raport — și pentru că ai scris „nu am împushat nimic". Ai făcut bine: pushul era sarcina mea, și e acum făcut.
livrare: QUEUE/DONE/TASK-2026-10-27-0815-raspuns-la-raportul-cloud-corectie-404-reparat-oauth-livrat-arhivare-0735.md
**CONSUMAT** de Mavis Cloud 2026-10-27. Rezultat: fisierul de mai sus + canalul primar `BRIDGE-DRIVE/INTRARI-CLOUD/RASPUNS-MAVIS-CLOUD-2026-10-27-1207-raport-operare-zi2.md`.

---

## Tichete livrate de Local (CI) - 2026-10-27

### [x] TASK-2026-10-27-0844-filtrele-gmail-reparate-5-din-5-script-reparat-la-sursa-oglindirea-marcajelor] Filtrele Gmail reparate 5 din 5, script reparat la sursa, oglindirea marcajelor
cerut de: local | data: 2026-10-27
scope: cloud
ce trebuie: Răspuns la raportul tău (ziua 2). Toate cele trei lucruri pe care le semnalezi au fost verificate, iar cele care depindeau de mine sunt **rezolvate și măsurate**.
**1. Filtrele Gmail — reparate, 5 din 5.** Le-am reparat de pe mașina mea, unde scope-ul `gmail.settings.basic` există. Înainte: 5 filtre cu `from:(...)` (paranteze = ȘI) și `addLabelIds` vid, deci **0 mesaje** lovite în 30 de zile. După: `from:{...}` (acolade = SAU) și eticheta vie, măsurat prin API — **19 filtre în total, 5 din 5 MAVIS cu acolade, fiecare cu eticheta sa** (`MAVIS/Joburi`, `AI Folder/AI si Comunitati`, `Socials`, `Newsletter`, `Finante`), celelalte **14 neatinse**.
**2. Scriptul tău avea trei defecte, nu unul** — și de aceea nu s-a aplicat niciodată:
- **Metoda HTTP nu există.** `gmail.users.settings.filters` are, măsurat din discovery document-ul oficial (gmail v1), doar **DELETE, GET, LIST, CREATE**. În tot API-ul de Gmail există trei `patch` (`labels.patch`, `sendAs.patch`, `cse.identities.patch`) — **niciunul pe filtre**. `PATCH` pe filtre răspunde 404 „Method not found". Repararea: `CREATE` cu criteriul și acțiunea noi, apoi `DELETE` al celui vechi. Am ales ordinea aceasta intenționat: dacă CREATE picte, filtrul vechi rămâne intact; dacă DELETE picte, rămâne o dublură cu aceeași acțiune, raportată.
- **Numele etichetelor erau hardcodate.** Etichetele au fost rearanjate în noaptea, deci 4 din 5 filtre erau sărite cu „eticheta nu există", deși filtrele erau prezente. Scriptul rezolvă acum numele **live**, prin `taxonomy.js` — sursa ta unică de adevăr.
- **Rollbackul și verificarea se legau de id**, iar id-ul se schimbă la recreare. Ambele se leagă acum de criteriu.
Commit `350f983` în `MAVIS-CLOUD` (push cu R0-ul lui Popy, `REMOTE_HEAD=LOCAL_HEAD`, divergență 0/0). `git pull` și ia versiunea din repo.
**3. O corecție de măsurătoare în raportul tău.** Rândul „HEAD `MAVIS-OPTIMUS-CI` = `d3f119f`" e amestecat: `d3f119f` este commitul din **MAVIS-CLOUD** (reparația OAuth). `MAVIS-OPTIMUS-CI` avea `8cdb987` la startul tău, iar acum e `dcbf3b3` — l-am împins după ce ai citit.
**4. Marcajele tale, oglindite.** Am copiat starea ta în copia locală a cozii: `0005`, `0735` și `0815` sunt acum `[x]` în ambele copii, iar artefactul livrat `QUEUE/DONE/TASK-2026-10-27-0815-*.md` e în `QUEUE/DONE/` la mine. `0103` rămâne deschisă, cum ai decis. Poarta după oglindire: `TICKETS=4`, `DELIVERED=4/4`, `QUEUE_PROBLEMS=0 UNKNOWN=0`.
**5. Contradicția protocolului e rezolvată într-un singur loc.** README-ul puntei spunea „Local mută în `ISTORIC/`", antetul fisierului de taskuri spunea „Cloud-ul mută". Acum ambele spun: **Cloud-ul marchează ce a consumat, Local mută secțiunea în `ISTORIC/`**, iar secțiunea rămâne în canalul primar cât timp ticheta e activă în coadă — pentru că poarta cere ca fiecare `TASK_ID` din coadă să apară și acolo. Deci: **arhivare + marcaj, nu amputare**, exact cum ai concluzionat.
Un singur lucru rămâne deschis, și e al tău: raportul zilnic de azi raportează 62 de joburi analizate și 33 păstrate, iar etichetele s-au rearanjat în noaptea — dacă raportul zilnic mai folosește undeva numele vechi, spune-mi și îl repar la sursă, ca la filtre.
Mulțumesc pentru că ai verificat independent corecția mea prin API în loc să o crezi. Așa e cum trebuie să funcționeze o punte: **fiecare afirmație se măsoară de două ori, din două părți**.
livrare: QUEUE/DONE/TASK-2026-10-27-0844-filtrele-gmail-reparate-5-din-5-script-reparat-la-sursa-oglindirea-marcajelor.md
