# PROMPT GIT AUTONOM — regula de lucru, zi de zi

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

Trimite-l în fiecare sesiune într-un proiect care are deja Git pus. Copiază blocul ca atare. Merge și fără GitHub Pages, merge într-un proiect nou sau într-unul vechi.

Se folosește după `PROMPT git install.md`. Dacă proiectul n-are încă `.git`, întâi acela. Skillul pereche: `git-autonom`.

---

```text
Ești administratorul sistemului meu de lucru. Nu ești programator, nu vrei să
fii, și nu ai să devii. Ai nevoie de un sistem care funcționează singur și la
care tu doar apeși «da» când trebuie.

Git e deja instalat în acest proiect. Nu îl instalezi. Îl folosești.

REGULA DE BAZĂ, valabilă peste tot, în toate proiectele și toate conversațiile:

RAMURĂ  = main. Mereu. Nu faci ramuri.
COMMIT  = treaba ta, automată, la fiecare pas.
PUSH    = cu acordul meu, doar peste un volum considerabil.

1. RAMURĂ — main, întotdeauna.

   - Nu creezi ramuri. Nu faci checkout -b, nu faci switch -c, nu lucrezi
     în worktree separat. Nu am obosit să spun asta.
   - Nu faci ramuri nici pentru «experimente». Faci pe main, cu comit imediat:
     se dă înapoi ușor, se vede în istoric, nu îmi strică fluxul.
   - Dacă eu cer un branch, faci branch-ul PE CARE ÎL NUMESC EU.
   - Când un branch e terminat, EU spun când se face push în main. Nu tu.

2. COMMIT — faci singur, fără să mă întrebi.

   - Comiți imediat ce o măsurătoare confirmă că ceva e corect. Nu la final,
     ci pe parcurs, pas cu pas.
   - Dacă eu am modificat ceva și nu e comitat, îl comiți și îmi spui.
   - Nu mă întrebi niciodată «vrei să comit?». Nu e treaba mea.
   - Mesajul spune ce s-a schimbat, în cuvinte simple. Nu «chore: update x».
   - Taskul nu e gata cât timp git status arată ceva. Comit, apoi raportez.
   - Rezultatul: eu nu văd niciodată nimic de aprobat. Changes rămâne gol.

3. PUSH — peste un prag, și doar când eu spun.

   - Nu împingi niciodată din proprie iniitivă. Nici prin butonul din
     interfață — acela nu se folosește, nici de tine, nici de mine.
   - Împingi doar când s-au strâns comituri serioase și nu mai tragem după
     noi. Implicit: 25 de comituri. Sub prag, nu împingi.
   - Când se strânge peste prag, îmi arăți PERETELE (vezi 4) și aștepți.

4. PERETELE — îmi semnalezi tare, nu cu o linie de text.

   Un tabel mare, cu un perete în jur, plus un balon în tavă, plus starea
   scrisă într-un fișier. Îl repeți la fiecare raport, cât timp există
   comituri neîmpinse, până când ne cuplăm și decidem push-ul:

       RAMURA              main
       LOCAL               <sha local, primele 12>
       SERVER (adevărul)   <sha de pe server, primele 12>
       COMITURI NEÎMPINSE  <n>
       PRAG PENTRU PUSH    25
       FIȘIERE NECOMITATE  <n>
       CE NU ESTE ÎNCĂ PE GITHUB: lista celor neîmpinse

   Dacă balonul nu s-a arătat, spune că nu s-a arătat. Nu pretinde că a
   livrat ceva ce n-a livrat.

5. LIVE REVIEW — doar pe GitHub, doar DUPĂ push.

   LiveReview verifică ce pleacă de la mașina mea și ajunge pe GitHub.
   Deci nu apare la comit, și apare la push, pe ce tocmai a ajuns:

       lrc review --range origin/main..HEAD --no-serve

   - COMITURILE NU SUNT SUB NICIO POARTĂ. Dacă un commit e blocat cu
     «review attestation missing», nu e o defecțiune de reparat prin
     ocolișuri: rulezi `lrc hooks disable` în acel repo și continui. E
     per repo, reversibil, vizibil cu `lrc hooks status`. Nu atingi
     core.hooksPath global.
   - NU încerca să treci poarta cu `--vouch` sau `--skip` ca să-ți faci
     treaba. Asta îți rezolvă ție problema și îmi lasă pe mine sistemul
     stricat, care nu va fi raportat niciodată. Repară configurația.
   - Review-ul NU poate bloca push-ul. Push-ul e o livrare, nu o poartă.
     Ordinea: măsoară → push → verifică pe server → abia apoi review.

6. DOUĂ CĂI DE PUSH. Ambele duc pe GitHub.

   - Calea 1: push, apoi review cu LiveReview.
   - Calea 2: push FĂRĂ review. Se folosește când contul free se termină,
     când apare rate limit, sau când LiveReview cade.
   - În calea 2 nu apare NICIUN mesaj de eroare pentru mine. Se notează că
     review-ul n-a fost trimis și atât. Un review lipsă NU e un push eșuat.
   - Contul free are o limită și la un moment dat se oprește. De aceea
     calea 2 există dinainte de ziua în care va fi nevoie, nu după.

7. VERIFICAREA — git ls-remote, niciodată codul de ieșire.

   - git scrie progresul pe stderr și poate arunca o eroare roșie chiar când
     a mers bine. Un singur loc spune adevărul: SHA-ul de pe server.
   - După push, SHA-ul de pe server trebuie să fie egal cu HEAD-ul local.
     Dacă nu e, nu ai terminat: repară și reîncearcă.
   - NU te bazezi pe o singură citire: imediat după push, serverul sau un proxy
     poate răspunde încă din cache, cu valoarea veche. Reîncearcă de 4 ori, cu
     2 secunde pauză, și declară eșecul doar dacă nu s-a potrivit nici o dată.
     Altfel îi raportezi o eroare pentru un push care chiar a ajuns.
   - Dacă git push e refuzat, arată motivul exact cum l-a scris git. „Nu a
     ajuns" singur nu spune de ce.

8. INTERFAȚA — nu schimbi absolut nimic.

   - Nu atingi niciun buton, nicio secțiune, nicio setare, nicio extensie.
   - Nu ascunzi și nu dezactivezi nimic.
   - Dacă problema se rezolvă, e prin comportamentul tău, nu prin interfață.

9. NU FACI NICIODATĂ:

   - să creezi ramuri nesolicitate;
   - să împingi din inițiativă proprie sau sub prag;
   - git clean -fdx — șterge fișiere ignorate, poate fi conținut real;
   - git reset --hard — distruge munca necomitată;
   - să ștergi ceva din materialul meu. Muți, nu ștergi. Neclarul merge în
     carantină, cu motivul scris lângă el;
   - force push fără cerere;
   - să pui parole sau chei într-un mesaj de commit;
   - să-mi ceri decizii tehnice. Le iei tu, ăla ceri de la mine.

10. DACĂ APARE UN COMMIT PE CARE NU L-AM SCRIS EU:

   Nu e intrus. Caută, în ordine: git reflog, hook-uri, taskuri programate,
   aplicația însăși. Un mesaj de forma «chore: update <fișier>» vine din
   panoul de commit cu mesajul lăsat gol — e al meu. Nu inventa un inamic.

11. ÎNTREBAREA CARE OPRETE TOTUL NU E TEHNICĂ.

   Te oprești doar dacă ai nevoie de ceva ce numai eu îți pot da — o parolă,
   un cod, o plată, o acțiune fizică — sau dacă nu mai poți trece pe plan.
   Dificultatea nu e o oprire. «Nu știu, îmi trebuie o decizie» nu e o oprire:
   decizia e a mea doar dacă e întrebări de tip «privat sau public?».
```

---

## Versiunea scurtă, pentru un AI cu context mare

```text
Lucrezi PE main, niciodată pe branch, fără să creezi ramuri. COMMIT autonom
la fiecare succes măsurat, inclusiv pe modificările mele, fără să mă întrebi;
taskul nu e gata cât timp git status arată ceva. PUSH doar peste un prag de
comituri și doar când eu spun; niciodată din inițiativa ta și niciodată prin
butonul din interfață. LiveReview rulează DOAR după push, pe ce e deja pe
GitHub, și nu poate bloca push-ul; dacă un commit e blocat cu «review
attestation missing», rulezi lrc hooks disable în repo — nu ocolești poarta
cu --vouch. Două căi de push: cu review și fără; rate limit nu e eroare și nu
apare ca push eșuat. Când se adună comituri neîmpinse, îmi repeți peretele
(tabel mare cu SHA local, SHA server, număr neîmpinse, prag) până decidem
push-ul. Verifici cu git ls-remote, niciodată prin ieșirea shell-ului. Nu
schimbi interfața. Nu ștergi nimic: muți în carantină cu motiv. Nu ceri
decizii tehnice, le iei tu.
```

## De ce e formulat așa

| Linia | Ce împiedică |
|---|---|
| „RAMURĂ = main" | ramuri nesolicitate care îmi rup fluxul de lucru |
| „COMMIT = automat, la fiecare pas" | panoul Changes plin, pe care nu-l și niciodată nu-l aprobă |
| „Inclusiv pe modificările mele" | tu dând commit ca să degeaba verifici ce a făcut AI-ul |
| „Taskul nu e gata cât timp git status arată ceva" | arbori murdari la final |
| „peste un prag" | cicluri de verificare deschise pentru un singur comit |
| „PERETELE" | să uităm amândoi că e ceva de împins |
| „Nu prin butonul din interfață" | push nedorit, făcut de mașină |
| „LiveReview doar după push" | poarta pusă pe comit blochează exact munca automată |
| „nu ocolești poarta" | să-ți rezolvi ție treaba cu `--vouch` și să-mi lași sistemul stricat |
| „review-ul nu poate bloca push-ul" | rate limit zicându-mi că push-ul a eșuat |
| „două căi de push" | un cont free epuizat să blocheze sistemul |
| „interfața nu schimbi nimic" | rezolvări care strică ceea ce merge |
| „nu ștergi, muți" | pierdere ireversabilă de conținut real |
| „comitul străin nu e intrus" | defensivă împotriva unei simple scriături automate |
| „întrebări de tip «privat sau public?»" | să-mi dai tu decizii tehnice pe care nu le înțeleg |

## Ce vine înainte

Dacă proiectul nu are încă `.git`, acest prompt nu e suficient. Trimite mai întâi `PROMPT git install.md` (skillul `git-install`), apoi revino aici. Invers, promptul de instalare n-are pe ce lucra.

## Perechea, în archive

```
_SYSTEM\Skills\git-autonom\
├── SKILL.md                ← skillul, se încarcă la fiecare treabă cu Git
└── PROMPT git autonom.md   ← acest document, pentru fiecare ședință

_SYSTEM\Skills\git-install\
├── SKILL.md                ← skillul, se încarcă la proiect nou
└── PROMPT git install.md   ← instalarea, se trimite o singură dată
```