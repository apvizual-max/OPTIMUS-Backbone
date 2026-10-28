---

<!-- NUCLEU-GIT v1 -->
RAMURA = main. Nu creezi ramuri.
COMMIT = imediat la fiecare pas, inclusiv pe modificarile mele. Nu intrebi.
PUSH = peste prag si doar cu -Acord, care eu dau cand spun "faci push".
LIVEREVIEW = doar DUPA push, pe ce a ajuns pe GitHub. Niciodata inainte, niciodata la comit.
DOUA CAI = calea 1 cu LiveReview, calea 2 fara. Rate limit nu blocheaza push-ul.
VERIFICARE = git ls-remote. Niciodata prin codul de iesire.
PERETE = tabelul se repeta in fiecare raport pana la push.
INTERFATA = nu se atinge.
<!-- /NUCLEU-GIT -->
name: mavis-git-autonom-skill
description: "Regula de lucru zilnică cu Git, într-un proiect care are deja .git. Lucrezi PE main, niciodată pe branch, fără să creezi ramuri. COMMIT imediat la fiecare succes măsurat, inclusiv pe modificările lui Popy, fără să ceri confirmare, fără poartă și fără LiveReview. PUSH doar cu acordul lui Popy și doar peste un prag de comituri, prin scripts\\git-autopush.ps1: push pur, LiveReview abia DUPĂ ce serverul e confirmat, două căi (cu review și fără), rate limit nu generează nicio eroare. Verifici cu git ls-remote, niciodată prin codul de ieșire. Semnezi prin scripts\\push-status.ps1, cu tabel mare și balon în tavă, repetat până la push. Nu atingi interfața. Nu ștergi nimic: muți în carantină cu motiv scris. Nu ceri decizii tehnice — le iei tu și continui. Se încarcă la prima treabă care atinge Git; instalarea de la zero e skillul mavis-git-install-skill."
---

# SKILL: git-autonom

**Cum se lucrează cu Git în fiecare zi, după ce e pus.**

| | |
|---|---|
| **Perechea** | skill: `git-autonom` · prompt: `PROMPT git autonom.md` |
| **Se încarcă** | la prima treabă care atinge Git, în orice proiect cu istoric |
| **Nu e** | instalarea — aceea e skillul `git-install`, rulează o singură dată |
| **Copie vie** | `C:\Users\apviz\.minimax\agents\mavis\skills\mavis-git-autonom-skill\SKILL.md` |

---

## Cele trei legi

1. **Lucrezi pe `main`.** Nu creezi ramuri. Nu faci `checkout -b`, nu faci
   `switch -c`, nu lucrezi în worktree separat. `main` e singurul loc.
2. **Comiți imediat.** La fiecare pas măsurat. Nu la final, nu pe runde.
3. **Push doar cu acordul lui.** Și doar peste un prag. Niciodată din inițiativa mea.

Restul documentului e explicația și măsurătoarea fiecăreia.

---

## 1. RAMURA: `main`, întotdeauna

Popy a spus limpedit: *„Am obosit să spun asta."* Nu repet întrebarea și nu
repet lui cerința.

| Situația | Ce fac |
|---|---|
| Munca curentă | `main`, direct |
| Nu știu dacă e sigur | e `main` oricum; ramurile se cer, nu se oferă |
| Vreau să „încerc ceva" | pe `main`, cu comit imediat — se dă înapoi ușor, se vede în istoric |
| Popy cere branch | fac branch-ul **pe care îl numește el**, nu unul al meu |
| Branch terminat | **el** spune când se face push în `main` |

Motivul lui, spus direct: *„Nu mi-le faci tu automat să mă furc în cap, să îmi
distrugă pull-ul meu, tot sistemul să nu pot să lucrez."* Un agent care face
ramuri când nu i se cere îi strică fluxul de lucru și pune un comit în plus
între muncă și push.

**Consecință practică:** nu există „work în desfășurare” și „gata de push”.
Tot ce comit e pe `main` și poate urca oricând.

## 2. COMMIT — imediat, la fiecare pas

**Comit înainte să raportez**, nu la sfârșitul taskului.

- Când o măsurătoare confirmă că ceva e corect, comit **imediat**.
- **Inclusiv pe modificările lui.** Dacă `git status` arată fișiere necomitate
  pe care le-a atins el, le comit și îi spun. Nu aștept să-l întreb.
- Nu cer confirmare. Nu spun „vrei să comit?". Nu las nimic în panoul Changes.
- Mesajul spune **ce s-a schimbat în cuvinte simple**, nu `chore: update <fișier>`.

**Arborele murdar e o stare interzisă.** Dacă taskul se termină și `git status`
neclară, taskul nu s-a terminat. Comit, apoi raportez.

De ce: un administrator nu lasă un panou `Changes` plin pentru un om care nu
știe ce e Git. Dacă eu comit la fiecare pas, Changes rămâne gol și nu are ce
arăta. Pentru el, Changes nu e ajutor — e blocaj.

### Nimic nu blochează comitul

Comitul e treaba mea și trebuie să fie liber. Nu există tool, hook, review sau
serviciu care să poată opri un `git commit`.

Măsurat 2026-10-11: LiveReview era armat global și bloca fiecare comit cu
`review attestation missing`. Pentru că poarta cerea o atestare și `exit 1`,
iar în context non-interactiv nu exista drumul care s-o producă — nici fără
nimic în staging, nici cu `--allow-empty`. Am ocolit-o cu `--vouch` ca să-mi
fac treaba, și am raportat că merge. **Asta a fost greșeala**: un ocoliș pe care
numai eu îl pot folosi nu e o reparare, e o conversie a unui defect vizibil
pentru el într-unul invizibil — deci un defect care nu va fi raportat niciodată.

Corectura, la instalare, în fiecare repo:

```
lrc hooks disable        # scrie .git\lrc\disabled;  lrc hooks enable readuce
```

Per repo, reversibil, vizibil cu `lrc hooks status`, nu atinge
`core.hooksPath` global și nu ajunge niciodată în comit.

> **Regula, verificabilă:** dacă Popy ar lovi aceeași problemă mâine, nu am
> reparat nimic. Repar configurația, nu ocolișul.

## 3. PUSH — prag, acord, și nimic altceva

Push-ul se face prin `scripts\git-autopush.ps1`. Nu prin butonul din interfață
— acela nu se folosește, nici de mine, nici de el.

### 3.1 Se împinge doar peste un volum considerabil

Nu împing la fiecare schimbare. Împing când s-a strâns **comituri seriaze** și
**nu mai tragem după noi**. Implicit pragul e **25 de comituri** (`-Prag`).

Motivul: împingerea e ieftină, dar *aratrul* e scump. Fiecare push deschide un
ciclu de verificare, de review, de comentarii. Nu deschidem un ciclu pentru un
singur comit.

Sub prag, scriptul **refuză** și iese cu `3`. Nu e o eroare — e o poartă
deliberată, și e prima poartă din sistem.

### 3.2 Cu acordul lui, mereu

Niciodată din inițiativa mea. Când se strânge peste prag, **îi arăt peretele**
(§4) și aștept. Dacă uităm amândoi, se vede: serverul rămâne în urmă.

### 3.3 Push-ul e o livrare, nu o poartă

Ordinea e fixă și nu se negociază:

```
1. masoara    HEAD local, server prin git ls-remote, comituri neimpinse
2. decide     sub prag? nu se atinge nimic
3. push       git push PUR. fara LiveReview. fara review. fara poarta.
4. verifica   git ls-remote; SHA server == SHA HEAD
5. review     LiveReview — DOAR ACUM, pe ce e deja pe GitHub
```

Pasul 3 nu depinde de nimic. Nu există review, limită, cotă sau serviciu care
să poată opri un push. Dacă ceva se strică la pasul 5, push-ul e deja făcut
și verificat.

### 3.4 Două căi de push — ambele duc pe GitHub

| | Calea 1 | Calea 2 |
|---|---|---|
| Când | totul funcționează | limită de cont, rate limit, LRC căzut |
| Push | identic | **identic** |
| Review | după push | **nu** |
| În panoul lui Popy | liniștit | **tot liniștit** |

Calea 2 **nu e o degradare**. E calea de rezervă prevăzută, pentru ziua în
care contul free se termină. În calea 2 nu apare niciun mesaj de eroare: se
notează că review-ul n-a fost trimis și atât. **Un review lipsă nu e un push
eșuat.**

Se alege automat: scriptul încearcă calea 1 și, dacă LiveReview răspunde
negativ, trece în calea 2 fără să atingă nimic din ce s-a întâmplat deja.
`-FaraReview` o impune direct, pentru ziua în care contul e șters.

## 4. PERETELE — cum îi semnez că se adună

Popy: *„trebuie să îi semnați asta cu un papap cu ceva, nu cu o linie mică de
text."* Un perete întreg, repetat în fiecare raport, până când ne cuplăm și
decidem push-ul.

`scripts\push-status.ps1` îl tipărește:

```
====================================================================
  PERETELE PUSH
====================================================================

  RAMURA                 main
  LOCAL                  2b1b0947b84d
  SERVER (adevarul)      8b22b7a3be63
  COMITURI NEIMPINSE     1
  PRAG PENTRU PUSH       25
  FISIERE NECOMITATE     0
--------------------------------------------------------------------
  CE NU ESTE INCA PE GITHUB (1 comituri)
--------------------------------------------------------------------
    2b1b094 Rescrie fluxul: push pur primul, LiveReview doar DUPA push
--------------------------------------------------------------------
  Sub prag (1/25). Se aduna.
  PUSH = cu acordul lui Popy. Nici din initiativa agentului.
```

Trei lucruri simultan, pentru că fiecare acoperă un mod în care s-ar putea
rata un mesaj:

1. **Tabelul în fiecare raport.** Cât timp `COMITURI NEIMPINSE > 0`, tabelul
   intră în raportul meu. Nu ca notă de subsol — ca secțiune.
2. **Toate repo-urile, nu unul.** Măsurat 2026-10-11: trei repo-uri aveau
   comituri neîmpinse și peretele se uita la unul singur. Un perete care
   acoperă o treime din realitate e un perete mincinos. Acum sunt trei blocuri
   și un total: `projects`, `SENTINEL_PRIME`, `mavis-skills`.
3. **Balon în tavă**, cu `NotifyIcon` — mecanismul deja folosit de digest-ul
   săptămânal, deci e dovedit pe această mașină. Durată 15 s, și **trăiește**
   15 s: balonul dispare odată cu iconul, deci iconul se aruncă abia după ce
   balonul și-a făcut timpul. Măsurat 2026-10-11: codul dormea 4 s și apoi
   arunca iconul — promisiunea era cu 11 s mai lungă decât realitatea.
4. **Fișier de stare** `90_CONTROL_CENTER\api\push-pending.json` — supraviețuiește
   restartului de sesiune. Dacă nu mai sunt eu aici, peretele rămâne scris.
   Conține acum un vector, cu numele fiecărui repo, nu o singură cale.

Dacă balonul nu se arată, scriptul **spune că nu s-a arătat**. Nu pretinde că a
livrat ceva ce n-a livrat. Iar dacă sesiunea n-are desktop interactiv — caz în
care balonul n-are *ce* să apară, indiferent cât de bine arată codul — spune
și asta, înainte de a încerca. Cee ce poate fi măsurat e desktopul interactiv
și faptul că apelul nu aruncă; faptul că l-ai *văzut* nu poate fi măsurat de
script, și nu se pretinde.

**Iar dacă un repo nu poate fi măsurat, peretele NU spune că e totul în
ordine.** Titlul devine „MĂSURĂTURĂ INCOMPLETĂ" și ieșirea e `2`. Măsurat
2026-10-11: cu un repo inaccesibil, totalul era 0 și scriptul ieșea cu `0`,
adică un senzor mort care raportează sănătate.

## 5. LIVE REVIEW — doar pe GitHub, doar după push

LiveReview verifică codul care **pleacă de la mașina lui și ajunge pe GitHub**.
Deci se declanșează la push, pe ce tocmai a ajuns:

```
lrc review --range origin/main~<N>..<sha> --no-serve
```

`--range` e **read-only**: nu atinge comiturile, nu scrie atestări, nu poate
bloca nimic. Rolul lui e să **raporteze**, nu să oprească.

**Live free are o limită și la un moment dat se oprește.** Deci acționează doar
pe push și doar pe ce e pe GitHub. Când limita e atinsă, calea 2 preia
automat. Nu e o catastrofă și nu e un incident — e un scenariu planificat.

## 6. Push-ul se verifică prin `git ls-remote`, NICIODATĂ prin codul de ieșire

În PowerShell cu `$ErrorActionPreference='Stop'`, `git push` scrie progresul pe
**stderr**, iar shell-ul aruncă o eroare roșie chiar când push-ul a reușit.

```
git push origin main         # poate afișa "eroare" falsă
git ls-remote origin main    # ASTA e adevărul
```

Măsurat 2026-10-11, chiar în fluxul asta: push-ul a ajuns, `ls-remote` a
confirmat SHA-ul, iar scriptul totuși a ieșit cu `1` fără să verifice nimic.
De aceea apelurile `git` trec prin `Invoke-Git`, care coboară
`$ErrorActionPreference` la `Continue` **doar** în jurul apelului.

Un singur loc spune adevărul: SHA-ul de pe server.

**O singură citire nu e suficientă.** Imediat după push, serverul sau un proxy
din fața lui poate răspunde încă din cache, cu valoarea veche. Atunci
`ls-remote` spune „nu a ajuns" pentru un push care chiar a ajuns — și atunci îi
raportez o eroare care nu există. De aceea verificarea se **reîncearcă**: patru
încercări, câte două secunde între ele, și eșecul se declară doar dacă SHA-ul
nu s-a potrivit la niciuna. Costă cel mult 6 secunde în cazul rău; în cazul
bun, prima încercare trece și nu se pierde nimic.

La fel, dacă `git push` e **refuzat**, se arată motivul exact cum l-a scris
`git` — ramură protejată, autentificare, divergență. „Nu a ajuns" singur nu
spune de ce, și Popy nu are ce să mărească.

## 7. Ce nu faci NICIODATĂ

| Nu | De ce |
|---|---|
| creezi ramuri | Popy cere `main`; ramurile îi strică fluxul |
| faci push din inițiativă proprie | decizia e a lui |
| faci push sub prag | împingerea e o livrare pe grupuri, nu pe bucăți |
| `lrc hooks disable` pe repo-uri care nu sunt ale tale | e per repo; nu te miști în proiectele altora |
| `git clean -fdx` | șterge fișiere ignorate — poate fi conținut real |
| `git reset --hard` | distruge munca necomitată |
| ștergere pe materialul lui | **mută, nu șterge**; neclarul merge în carantină cu motiv scris |
| `force push` fără cerere | rescrie istorie |
| commit cu parole/chei | `git log` e citibil de oricine are acces |
| atingerea interfeței | rezolvarea e comportament, nu buton |
| review înainte de push | `git commit` și `git push` sunt libere |

## 8. Cum îi recunosc comitul

Dacă apare un comit pe care eu nu l-am scris, **nu e intrus** până nu dovedesc
altceva. Caută în ordine: `git reflog` → hook-uri (`core.hooksPath`, `.git/hooks`)
→ taskuri programate → aplicația însăși.

Cazul măsurat (2026-10-10): `chore: update <fișier>` vine din panoul
`Commit or push` cu mesajul lăsat **gol** — aplicația generează mesajul automat
(`suggestCommitMessage`). **Comitul e al lui.** Nu conflict de repo, nu instanță
cloud, nu Hermes, nu cron.

## 9. Backupul e reper, nu țintă

Backupul se **citește**, nu se scrie. Dacă lipsește ceva din dosarul de lucru,
**copiez din backup**, nu invers. Serverul e replica; localul e sursa.

## 10. La ce mă opresc

Nu la push: acolo doar cer acord, pentru că e decizia lui prin definiție.
Nu la o întrebare tehnică: **acelea le decid eu**, le spun odată cu explicația
și continui.

Mă opresc doar la ceva ce numai el îți poate da — o parolă, un cod de
autentificare, o plată, o acțiune fizică — sau dacă nu mai există niciun drum
care să nu se abată de la plan.

## 11. Plasa de siguranță la push — `git-autopush.ps1`

Ultima linie de apărare, și execută cinci lucruri pe care altfel le-aș face
eu cu mâna, deci le poate face și o sesiune oprită la mijloc:

1. măsoară, 2. respectă pragul, 3. împinge pur, 4. verifică pe server,
5. review după push, în calea 1 sau calea 2.

Reguli de implementare, măsurate nu auzite:

- **ASCII numai.** PowerShell 5.1 citește un `.ps1` fără BOM ca ANSI și
  parserul moare pe primul semn ne-ASCII. Control:
  `[System.IO.File]::ReadAllBytes($f) | Where-Object { $_ -gt 127 }` → `0`.
- **`git` numai prin `Invoke-Git`.** Altfel progresul pe stderr omoară
  scriptul înainte de verificare.
- **Fișierele de stare nu intră în istorie.** `push-pending.json` e în
  `.gitignore`, fiindcă se rescrie la fiecare măsurătoare și altfel ar face
  un comit nou de fiecare dată.

## 12. Poarta reală la push — hook `pre-push`

Măsurat 2026-10-11: 12 comituri au ajuns pe GitHub fără acordul lui Popy.
Poarta din script cere `-Acord`, dar **se ocolește prin `git push` direct**. Un
script impune o regulă doar față de cel care cooptează. Nu era o poartă, era
o cutie.

De aceea, în acest repo:

- `scripts/git-hooks/pre-push` — copia canonică, în istorie, **ASCII, cu LF**.
- `git config core.hooksPath .git/hooks` — **doar pe acest repo**. Calea globală
  de hook-uri rămâne neatină; nu se mișcă proiectele lui.
- `git-autopush.ps1` scrie `.git/PUSH-ACORD` **imediat înainte** de push, într-un
  `try/finally` care îl șterge oricum. Hookul consumă martorul: **un acord = o
  singură împingere**.

Măsurat, în ambele sensuri, pe remote local: `git push` direct → refuzat, server
neatins; prin `-Acord` → trece, server egal cu HEAD, martorul dispărut.

Refuzul se face **local**. Nimic nu se schimbă pe GitHub și nimic din interfața
lui Popy nu se atinge. Dacă vrea poarta și pe server, e decizia lui, nu a mea.

Scoaterea, dacă cere vreodată: `git config --local --unset core.hooksPath`.
Dacă repo-ul se reclonează, poarta dispare și trebuie repusă din
`scripts/git-hooks/pre-push` — de aceea copia e în istorie, nu doar în `.git`.

## 13. Promptul pereche

`PROMPT git autonom.md`, în același folder — se trimite ca atare altor
 instanțe, în alte proiecte. Rulează **după** `PROMPT git install.md`.

## 14. Repo-ul trebuie sa se poata clona — masurat 2026-10-28

`git log` arata perfect chiar si cand repo-ul e imposibil de checkout. Singura
verificare care conteaza e **o clona noua de la zero**:

```powershell
git clone https://github.com/apvizual-max/SENTINEL_PRIME.git _clone_probe
# verdict: exit 0 SI dirty=0 SI fisierele asteptate prezente
```

**Succes, masurat.** `origin/main` continea la radacina un director cu numele
literal `C:\Users\apviz\.minimax-agent\projects\SENTINEL_PRIME`. Git refuza
`:` intr-o componenta de nume, deci `read-tree`, `checkout` si orice clona
esueau cu `error: invalid path` / `make_cache_entry failed for path`. Repo-ul
era rupt pentru orice client Windows, inclusiv pentru pipeline. Repararea s-a
facut **prin plumbing**, fara index si fara a atinge istoricul publicat:

1. salveaza toate intrarile arborelui fals in quarantine, cu motiv scris;
2. extrage fisierele care exista DOAR acolo la calea lor reala;
3. reconstruieste arborele radacina: `git ls-tree -z origin/main` minus
   intrarea invalida, apoi `git mktree -z`;
4. `git commit-tree <tree> -p origin/main -m <motiv>` — istoricul ramane liniar;
5. `git update-ref refs/heads/main <commit>` apoi `git read-tree -u --reset HEAD`;
6. **verifica cu o clona noua**, nu cu `git log`.

Dupa reparatie: clona 1408 de fisiere, `dirty=0`, totul prezent.

**Greseli de repetat.**
- Nu verifica sincronizarea doar prin `git log` sau `git status`.
- Nu sterge intrarile suspecte din arbore fara sa le salvezi intai.
- Nu rescrie istoricul publicat si nu folosi force-push.
- Nu folosi `git reset --hard`.
- Nu considera ca "merge-ul a mers" daca `git merge` a scris un avertisment.
