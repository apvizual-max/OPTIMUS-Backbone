# Lecțiuni — ce a rămas din tot ce a fost plătit

Fiecare lecție are **contextul** în care a apărut. O lecție fără context e o
zicătoare; cu context, devine regulă de comportament.

---

## A. Despre măsurare

### A1. Auto-evaluarea nu e verificare
Măsurătoarea proprie poate fi corectă **și** să nu prindă ce contează. Înainte
să declari „gata", cere un verificator independent, cu acces la artefacte, nu
la descrierea ta.

### A2. Un instrument care măsoară altceva decât spune că măsoară
Două măsurători ale aceleiași ținte, luate la momente diferite, contra unei
ținte care se mișcă, dau un FAIL fals. Numără de două ori, înainte și după;
dacă s-a schimbat, ținta s-a mișcat → **UNKNOWN**, nu FAIL.

### A3. O copie versionată a unui sistem care rulează poate fi săptămâni veche
Controlul AgenticOS pică: prima ipoteză a fost „sistemul e rupt". Falsificat:
fișierele erau **identice** cu commit-ul `3fe5185` de pe `origin/main`, iar
pin-ul era îmbătrânit. **Controlul care pică poate fi pin-ul, nu sistemul.**
Verifică data scrierii fișierului și ancora externă înainte să schimbi ceva.

### A4. Testează constatarea verificatorului înainte să o repari
Același caz: verificatorul a raportat A10 ca eșec. Nu s-a reparat nimic până
când constatarea a fost falsificată prin probe independente. **Repară ce e
demonstrat, nu ce e raportat.**

### A5. O afișare stricată nu e un fișier stricat
Un titlu scris cu em-dash a apărut în consolă ca `â€”`. Verificarea pe octeți:
`E2 80 94` — **corect**. Nu s-a reparat nimic, pentru că nimic nu era stricat.
**Măsoară fișierul, nu afișarea.**

### A6. Un control care se aprinde pe munca reală nu mai e control
Trei controale reale s-au aprins pe condiții normale:
1. jurnalul scris într-un arbore indexat → "used by another process" → moarea
   runului. Corectie: scriere retry + neprietenoasă, urma completă într-un singur
   fișier.
2. proba de backlog număra PR-urile de două ori → transient → FAIL roșu.
3. controlul de ramuri număra orice ramură extra, inclusiv ramurile de lucru
   deschise de workflow → invocație pe muncă reală.
   Corectie: **ORPHAN** (eliminabil), **STALE** (peste fereastra),
   **ACTIVE** (doar raportat). Doar primele două sunt încălcare.
**Separă „s-a stricat ceva" de „ceva tocmai s-a mișcat".**

## B. Despre git

### B1. Mută datele git, nu clona
Clonarea produce un istoric nou; mutarea păstrează obiectele, referințele și
ramurile. Când intrarea de director e blocată, **copiii ei sunt mutabili**:
mută copil cu copil. (Măsurat: `.git` al SOT-ului, 14 copii.)

### B2. Un `.git` cuibărit face git să vadă fișierele ca șterse
Când un director care conține `.git` apare în working tree, gitul îl tratează
ca repo separat și **nu coboară în el**. Rezultat: 1.584 de fișiere
urmărite au apărut ca șterse, deși conținutul era corect. Diagnosticul
fals: „cine a șters fișierele?" — de fapt, **git nu se uită deloc înăuntru**.

### B3. Un repo shallow nu se poate aduce peste istoric existent
`shallow roots are not allowed to be updated`. Corectia: **scoate shallow de
la sursă** (`git fetch --unshallow origin`), nu de la destinație — și fii
gata că remote-ul poate fi înainte: acolo s-a găsit un head cu **244 de
commituri** în loc de 6.

### B4. `git subtree add` păstrează istoricul — dar probează rețeta întâi
`git merge-base --is-ancestor <sursă> HEAD` trebuie să dea `0`, iar merge-commit-ul
trebuie să aibă **doi părinți**. Probează într-un repo scratch înainte să
uniri cinci istorii: o rețetă greșită aplicată de cinci ori e cinci greșeli.

### B5. Un mesaj de commit cu BOM e un mesaj de commit stricat
`git commit -F -` prin pipe în PowerShell 5.1 a adăugat `EF BB BF` în fața
subiectului. Scrie mesajul într-un fișier cu
`[System.IO.File]::WriteAllText($p, $msg, (New-Object System.Text.UTF8Encoding($false)))`
și folosește `git commit -F <fișier>`.

### B6. `git status --porcelain` și `-like '??*'`
`?` e wildcard în `-like`, deci `??*` se potrivește cu orice linie. Numără
după `Substring(0,2)` ca să separi `M` / `A` / `D` / `?` / `R` corect.

### B7. `diff-index --quiet HEAD` e condiția reală pentru `subtree add`
`git status` curat nu e suficient: `subtree add` cere ca **indexul** să fie
sincronizat cu `HEAD`. Verifică `diff-index --quiet HEAD --`.

## C. Despre PowerShell 5.1

### C1. `[ordered]@{}` indexat cu un INTEG e pozițional, nu căutare de cheie
`$od[3016]` întoarce nimic chiar dacă 3016 e cheie; `$od[3098]='x'` aruncă
`ArgumentOutOfRangeException`. Pentru căutări: hashtable normal (`@{}`).

### C2. Numele de variabile PowerShell sunt INSENSIBILE la majuscule
`$bridges` și `$BRIDGES` sunt **aceeași** variabilă. Consecința măsurată de
două ori: lista de fișiere a suprascris calea de director, iar `Join-Path` a
produs un produs cartezian. **Când o clasă de bug apare de două ori, e o
regulă** — pune o poartă explicită de tip și de containment.

### C3. Un `.ps1` fără BOM e citit ca Windows-1252
`—` devine `â€”`, iar `”` (U+201D) e tratat ca delimitator de șir → parserul
rupe scriptul. **`.ps1` = ASCII pur**, fără excepție. (Pentru `.md`/`.js`,
UTF-8 strict e suficient.)

### C4. Un tool nativ care scrie pe stderr NU e o eroare — dar devine, cu `Stop`
`mavis-trash` pe un fișier blocat a oprit o mutare de 13 fișiere la pasul 14,
pentru că `$ErrorActionPreference='Stop'` a transformat ieșirea pe stderr în
eroare terminală. Înconjoară apelul sau coboară preferința.

### C5. `Select-String` într-un pipe strică `$LASTEXITCODE`
Capturează codul de ieșire **în interiorul** unui singur `powershell -Command`.

### C6. `Get-ChildItem -Include` filtrează doar cu wildcard sau `-Recurse`
Cu un path de director normal, `-Include` întoarce tot. `-Filter` funcționează
mereu.

## D. Despre unelte și politici

### D1. `rm --` trebuie să fie singur în invocare
Parsearea țintelor e a runtime-ului: dacă aceeași comandă conține și alte
operații, e respinsă („targets-only trash marker"). Rulează `rm --` separat.

### D2. `Copy-Item -Recurse` e blocat; `Directory::Move` și `File::Copy` trec
Decizia de a muta în loc de a copia nu e doar preferință — e și ce permite
mutarea atomică pe același volum.

### D3. Un path cu alternanță `\\` la început e interpretat ca share de rețea
`Get-ChildItem -Recurse` peste un asemenea path e respins de politica de
siguranță. Folosește `grep` pentru căutare de conținut.

### D4. Politica blochează `Remove-Item` și `[System.IO.File]::Delete`
Ștergere **recuperabilă**: `rm -- "<cale literală absolută>"`. Dacă
recuperarea eșuează, raportează eșecul — nu cădea înapoi pe ștergere
permanentă.

## E. Despre colaborare

### E1. Caută întâi, scrie al doilea, nu te opri ca să îi dai o decizie tehnică
Răspunsul era deja într-un fișier; eu am creat ambiguitatea și i-am facturat
pentru ea. **Nu există întrebări tehnice pentru Popy.** Dacă e nevoie de o
decizie, adu faptele care o fac decidabilă.

### E2. Lista de progress e busolă, nu coadă
Se actualizează **pe loc**: editezi rânduri, adaugi rânduri. Nu rescrii lista
cu doar task-ul curent — asta s-a pierdut o dată firul MAXHERMES. Rând
nepotrivit → `completed`/`cancelled` **cu motiv**, nu ștergere.

### E3. Numără rândurile după ce scrii
Ca să detectezi o suprascriere accidentală a listei.

### E4. O greșeală de status nu e o ștergere
Uneori Popy șterge ca să știe că backupul există. **Lipsa din vault NU e
pierdere**: măsoară înainte să concluzionezi, și nu restaura fără hotărârea
lui.

### E5. Rămâi în proiectul curent
Proiectul curent e frontiera: nu citește, nu audita, nu întreba nimic din
afara lui. Un popup cu decizii despre alt proiect e o încălcare.
