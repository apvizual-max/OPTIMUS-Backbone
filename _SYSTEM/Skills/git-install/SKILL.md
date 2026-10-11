---

<!-- NUCLEU-GIT v1 -->
RAMURA = main. Nu creezi ramuri.
COMMIT = imediat la fiecare pas, inclusiv pe modificarile mele. Nu intrebi.
PUSH = peste prag, doar cu acordul meu. -Force doar cand eu spun "faci push".
LIVEREVIEW = doar DUPA push, pe ce a ajuns pe GitHub. Niciodata inainte, niciodata la comit.
DOUA CAI = calea 1 cu LiveReview, calea 2 fara. Rate limit nu blocheaza push-ul.
VERIFICARE = git ls-remote. Niciodata prin codul de iesire.
PERETE = tabelul se repeta in fiecare raport pana la push.
INTERFATA = nu se atinge.
<!-- /NUCLEU-GIT -->
name: mavis-git-install-skill
description: "Punerea pe picioare a infrastructurii Git + GitHub într-un proiect nou, fără .git. Măsoară (git --version, gh --version, gh auth status, remote -v) și continuă fără să întrebi. git init pe ramura main, core.autocrlf false, core.eol native, core.filemode false — per repo, nu global. lrc hooks disable imediat după git init, ca poarta LiveReview să nu poată bloca primul comit. .gitignore prin NEGARE (/* interzice totul, deschizi explicit căile reale), verificat cu git check-ignore în AMBELE sensuri. Primul comit, gh repo create --private --push, primul push face parte din instalare. Verifici cu git ls-remote, niciodată prin ieșirea shell-ului. Fără ramuri: se lucrează pe main. Rulează o singură dată, înaintea lui mavis-git-autonom-skill; retrimis, face un al doilea repo pe același proiect."
---

# SKILL: git-install

**Cum se pune pe picioare Git + GitHub, de la zero, o singură dată.**

| | |
|---|---|
| **Perechea** | skill: `git-install` · prompt: `PROMPT git install.md` |
| **Se încarcă** | la proiect nou, sau proiect fără `.git`, sau fără remote pe GitHub |
| **Rulează** | o singură dată, la ridicare — **nu** la fiecare ședință |
| **Nu e** | funcționarea de zi cu zi — aceea e skillul `git-autonom` |
| **Copie vie** | `C:\Users\apviz\.minimax\agents\mavis\skills\mavis-git-install-skill\SKILL.md` |

---

## Cum aleg între cele două skilluri

| Situația | Skill |
|---|---|
| proiectul n-are încă `.git` | **`git-install`** — îl ridici |
| proiectul are deja istoric | **`git-autonom`** — îl folosești |

Nu se rulează amândouă. `git-install` e o dată, `git-autonom` e restul vieții
proiectului.

## REGULA DE AUTORITATE — nu întrebi nimic

**Tu faci totul, tu decizi totul, eu doar primesc raportul.**

Popy nu e programator. Nu știe Git, nu vrea să știe, și nu mai apucă el
butoane. Orice întrebare în care aleg între două variante pe care le-am putea
numi eu înainte e o întrebare construită greșit — și îl costă efort pe ceva
ce eu aveam voie să-l decid.

| Situație | Ce faci |
|---|---|
| `git` sau `gh` lipsesc | îi instalezi. Permisiunea e deja dată — asta e sarcina ta |
| nu ai drept de administrator | instalezi ce poți, termini tot ce se poate, raportzi restul |
| nu ești autentificat pe GitHub | încerci `gh auth login`; dacă cere interacțiune, e **singurul** motiv pentru care te oprești |
| nu știi numele repo-ului | îl derivi din numele folderului |
| nu știi ce ramură | **`main`**, o setezi explicit, nu întrebi |
| nu știi ce `.gitignore` | scrii cel cu **negație**, îl verifici, îl corectezi |
| nu știi unde merge push-ul | îl măsori cu `git ls-remote` |

**Singurul motiv legitim de oprire:** ai nevoie de ceva ce numai omul îți poate
da — un cod de autentificare, o plată, o acțiune fizică. Atunci spui exact
ce lipsește, într-o propoziție, și te oprești. **Nu pentru nume, nu pentru
opțiuni, nu pentru „nu sunt sigur".**

## Ordinea, fără întreruperi

1. **Măsoară** `git --version`, `gh --version`, `gh auth status`, identitatea
   globală, dacă există `.git`, ce remote are. Nu raporta și aștepta —
   continuă.

2. **Identitatea**: o citești, o lași. Nu o schimbi, nu o ceri, nu o inventezi.
   Dacă lipsește, alegi tu una stabilă pentru proiect și o spui în raport.

3. **Pregătește**: instalezi ce lipsește, `git init`, și configurezi **pe nivel
   de repo**, nu global:

```
git init -b main
git config core.autocrlf false
git config core.eol native
git config core.filemode false
```

`autocrlf false` e per-repo pentru că e decizie a proiectului. Global ar
forța toate proiectele de pe mașină, inclusiv ale altcuia.

Ramura e **`main`** de la început. Nu se fac ramuri de lucru: `git-autonom`
interzice, iar un repo care se facealtfel te împinge în workflow-uri pe care
Popy nu le vrea.

4. **LiveReview: îl scoate de pe comit înainte de primul comit.**

```
lrc hooks disable        # scrie .git\lrc\disabled — DOAR pentru acest repo
```

Făcut **imediat după `git init`**, înainte de orice comit. Altfel primul
comit se blochează și pierzi timp căutând de ce.

De ce e obligatoriu, măsurat pe 2026-10-11: `core.hooksPath` e global
(`C:\Users\apviz\.git-hooks`), deci poarta LiveReview e armată în **orice**
repo nou, automat. Iar `pre-commit` cere un fișier de atestare și iese cu 1
când nu e terminal — iar în context non-interactiv nu există drumul care să-l
producă. Nu e o eroare de configurare: e poarta funcționând exact cum a fost
scrisă, în locul greșit.

Reversibil, per repo, vizibil: `lrc hooks status`. `lrc hooks enable` îl
readuce. **Nu se atinge** `core.hooksPath` global și **nu se șterge** nimic —
se scrie un singur marcaj, în `.git\lrc\`, care nu ajunge niciodată în comit.

5. **`.gitignore` prin NEGARE, nu enumerare.** Interzici totul cu `/*`, apoi
   deschizi **tu**, singur, căile pe care le conține proiectul — le afli
   citind structura lui, nu întrebând.

6. **Primul comit, repo-ul privat:**

```
git add -A
git commit -m "prima stare a proiectului"
gh auth login                      (doar dacă nu ești deja autentificat)
gh repo create <nume-derivat-din-folder> --private --source=. --remote=origin --push
```

Nume-ul îl derivi tu din numele folderului: litere mici, cifre, cratime.
**Primul push face parte din instalare** — fără el repo-ul nu există încă,
deci nu ceri acord pentru el și îl anunți în raport.

7. **Verifică singur**, cu `git ls-remote origin main`. Nu cu codul de ieșire:
   `git` scrie progresul pe stderr și poate arunca o eroare roșie chiar când a
   mers bine. Dacă verificarea nu confirmă, **repară și reîncearci**, nu
   raportezi succes.

8. **Predă către `git-autonom`.** Ridicarea e gata; de acum înainte regulile
   de fiecare zi sunt ale skillului `git-autonom`.

## LiveReview după instalare

Review-ul lui LiveReview **nu s-a pierdut** — doar s-a mutat de pe comit pe
push, unde are rost:

```
lrc review --range origin/main..HEAD --no-serve
```

Rulează în `git-autonom`, **după** ce push-ul e confirmat pe GitHub. Comitul
nu e niciodată sub poartă.

### Rate limit nu blochează push-ul

`free_30k` (30.000 LOC) se termină într-o zi, și atunci LiveReview răspunde
negativ. **Asta nu e o eroare și nu blochează nimic.** De aceea există două
căi, de la început, nu de la ziua în care va fi nevoie:

| | **Calea 1** | **Calea 2** |
|---|---|---|
| Când | totul funcționează | limită de cont, rate limit, LRC căzut |
| Push | identic | **identic** |
| Review | după push | **nu** |
| Mesaj de eroare pentru Popy | niciunul | **niciunul** |

Calea 2 e calea de rezervă prevăzută. În ea se notează pur și simplu că
review-ul n-a fost trimis, și atât. **Un review lipsă nu e un push eșuat** — și
nu apare ca unul în panoul lui.

## Regula `.gitignore` care costă cel mai mult — măsurată, nu auzită

Pe 2026-10-10, în acest vault, prima excepție scrisă corect **nu a funcționat**.
Două comituri consecutive au raportat doar logul, fără niciun avertisment.
Cauza, găsită prin măsură cu `git check-ignore -v`:

- Git nu coboară într-un director interzis. Ca să redeschizi un fișier,
  redeschide și **părintele** lui.
- `**` se potrivește și cu **zero componente**: `/_x/**` închide și directorul
  `_x` însuși, nu doar conținutul lui.
- Ultima regulă care se potrivește câștigă. Redeschiderile puse **înaintea**
  regulii de excludere sunt anulate de aceasta.

```
/_x/**
!/_x/
!/_x/sub/
!/_x/sub/**
```

Verifică cu `git check-ignore -v`: pe un fișier care trebuie urmărit,
răspunsul corect e că **NU** e ignorat. Pe unul care nu trebuie, trebuie să
rămână ignorat. **Verifică ambele sensuri** — fără control pe partea a doua,
poarta nu poate deveni roșie.

Aceeași regulă se aplică fișierelor de stare: ce se rescrie la fiecare
măsurătoare (`push-pending.json`, `live-state.json`) **nu intră în istorie**,
fiindcă altfel fiecare măsurătoare ar produce un comit nou.

## Prohibit, fără excepție

`git clean -fdx` · `git reset --hard` · `force push` fără cerere · secrete în
fișiere urmărite · ștergerea conținutului utilizatorului (muți, cu motiv
scris, în carantină) · **ramuri de lucru nesolicitate**.

## De la prima zi, fără excepție

**`main`, nu ramuri. Commit autonom la fiecare succes măsurat, inclusiv pe
modificările mele, fără să mă întrebi. Push peste un prag de comituri și doar
cu acordul lui — cu singura excepție a primului push din instalare. LiveReview
doar după push, pe ce e pe GitHub, și niciodată înainte. Interfața aplicației
nu se atinge:** rezolvarea e comportament, nu buton.

Taskul nu e gata cât timp `git status` arată ceva. Comit, apoi raportez.

### Peretele de push — nu e opțional, se predă odată cu infrastructura

`git-autonom` nu poate semnala ce nu are. I se predă aici, la ridicare:

```
scripts\push-status.ps1     → PERETELE PUSH: tabel mare cu ramura, SHA local,
                             SHA server, comituri neîmpinse, prag, necomitate,
                             lista neîmpinse + balon în tavă + stare pe disc
```

- **Cât timp `COMITURI NEIMPINSE > 0`, tabelul intră în raport** ca secțiune,
  nu ca notă de subsol, și se repetă până când decidem push-ul.
- Dacă balonul nu se arată, se spune că nu s-a arătat. Nu se pretinde ceva ce
  nu s-a livrat.

### Ce nu pot face cu push-ul

- **`-Force` nu e o scurtătură, e traducerea cuvântului lui Popy.** Îl folosesc
  numai când el spune explicit „faci push". Nu pentru a sări peste prag din
  inițiativă mea, și nu ca să îmi fac treaba mai repede.
- **Nu împing sub prag fără acord.** Sub prag, scriptul refuză și iese cu `3`.
  Nu e o eroare — e o poartă, și e prima din sistem.
- **Nu schimb ramura ca să evadez o poartă.** Se repară poarta, nu se ocolește.

## Ce raportezi la final

Un raport, cu cifre măsurate acum, nu cu impresii:

- ce a existat înainte și ce ai creat
- numele repo-ului și **de ce l-ai ales așa**
- ramura, comitul, adresa
- `lrc hooks status` — poarta, scoasă de pe comit, vizibilă
- ce verificări ai făcut și ce au răspuns, cu răspunsul
- singurul lucru rămas, dacă a rămas ceva, și de ce nu l-ai putut face

## Măsurat pe această mașină (2026-10-10, reconfirmat 2026-10-11)

git `2.56.0.windows.2` · `gh 2.97.0`, instalat și autentificat ·
`credential.https://github.com.helper=store` · identitate și `core.hooksPath`
la nivel global · **`gh` e deja prezent și logat** — așa că la o instalare pe
această mașină, singurul punct unde te-ai opri nu apare.

`lrc` v0.6.12, plan `free_30k` (30.000 LOC): review-ul **se trimite și e
acceptat**, dar `ai_mode: BYOK required on free plan` — analiza AI cere o cheie
a utilizatorului. De aceea contul se va epuiza: de aceea ambele căi de push
există.

## Promptul pereche

`PROMPT git install.md`, în același folder — se trimite ca atare într-o
sesiune nouă. Rulează **o singură dată**; retrimiterea lui face un al doilea
repo pe același proiect.