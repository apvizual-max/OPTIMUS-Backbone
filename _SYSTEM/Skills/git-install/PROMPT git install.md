# PROMPT GIT INSTALL — punerea pe picioare a infrastructurii

Trimite-l o singură dată, la începutul unei sesiuni noi, într-un proiect unde Git nu s-a atins niciodată. Copiază blocul ca atare.

Se folosește înaintea lui `PROMPT git autonom.md`. Acesta ridică infrastructura; celălalt spune ce faci cu ea, în fiecare zi. Skillul pereche: `git-install`.

---

```text
SETUP GIT + GITHUB, de la zero. Nu știi nimic despre Git. Proiectul are nevoie
de versionare și de o copie pe GitHub. Instalează tot ce trebuie, pas cu pas,
până la capăt, și verifică tot ce ai făcut.

=== REGULA DE AUTORITATE ===

TU FACI TOTUL. TU DECIZI TOTUL. EU DOAR PRIMESC RAPORTUL.

Nu mă întrebi nimic. Nu te oprești la mijloc. Nu alegi între variante pe
care le-am putea numi eu înainte: numele repo-ului, ramura, extensiile,
mesajul de comit, conținutul .gitignore — le alegi tu, corect, și îmi spui
ce ai ales și de ce.

Dacă nu știi ceva, alegi tu ce e mai sigur și continui. O întrebare pusă
din nevoie este o eșec, nu o politețe.

Singurul motiv real de oprire: ai nevoie de ceva ce numai eu îți pot da — un
cod de autentificare, o plată, o acțiune fizică. Atunci spui ce lipsește,
într-o proluză, și te oprești acolo. Nimic altceva.

=== REGULA DE BAZĂ, valabilă de la prima zi și peste tot ===

RAMURĂ = main. Nu faci ramuri. Am obosit să spun asta.
COMMIT = treaba ta, automată, la fiecare pas.
PUSH   = decizia mea — cu singura excepție a primului push din instalare, care
        face parte din ce ai construit acum.

1. MĂSOARĂ, APOI CONTINUĂ FĂRĂ SĂ AȘTEPTI.

   Rulează: git --version · gh --version · gh auth status ·
   git config --global user.name / user.email ·
   rev-parse --is-inside-work-tree · remote -v.
   Nu ceri permisiune pentru ce urmează. Continuă imediat.

2. DACĂ LIPSEȘTE CEVA, ÎL INSTALEZI.

   Dacă git sau gh nu sunt pe mașină, îi instalezi cu winget. Nu e o decizie
   a mea — e sarcina ta. Dacă nu ai drept de administrator, instalezi ce poți
   și termini tot restul; spui la final că a rămas ceva.

3. IDENTITATEA — NU O SCHIMBA, NU O CERE.

   Citește user.name și user.email globale și lasă-le cum sunt. Identitatea
   e a mașinii. Dacă ambele chiar lipsesc, alegi tu una stabilă pentru
   proiect și o spui în raport.

4. PROIECTUL — de la zero, fără întrebări:

   git init -b main
   git config core.autocrlf false      ← vezi secțiunea 7, nu le sări
   git config core.eol native
   git config core.filemode false

   `git init -b main` face ramura din prima secundă. NU apeți `checkout -b`
   și NU faci ramuri de lucru: proiectul se lucrează direct pe `main`, iar
   orice ramură nesolicată îmi strică fluxul de lucru.

5. LIVREVIEW — ÎL SCOATE DE PE COMIT. ÎNAINTE DE PRIMUL COMIT.

       lrc hooks disable        ← scrie .git\lrc\disabled, DOAR acest repo

   **Nu sări peste asta.** `core.hooksPath` e global, deci poarta LiveReview
   e armată automat în ORICE repo nou. În context non-interactiv (agent, CI,
   butonul aplicației) `pre-commit` cere un fișier de atestare și iese cu 1,
   iar acel fișier nu are de unde veni — nici fără nimic în staging, nici cu
   `--allow-empty`. Primul comit se blochează și pierzi timp căutând de ce.

   Nu e o defecțiune de reparat prin ocolișuri: dacă te lovește, rulezi
   `lrc hooks disable` în repo și continui. NU `lrc hooks disable` global.
   Reversibil: `lrc hooks enable`. Vizibil: `lrc hooks status`. Nu se șterge
   nimic — se scrie un marcaj în `.git\lrc\`, care nu ajunge niciodată în comit.

   LiveReview nu se pierde: se mută pe push. Și abia DUPĂ push — vezi
   `PROMPT git autonom.md`, secțiunea 5. Contul free are o limită, și de aceea
   există două căi de push.

6. .gitignore — ÎL SCRII TU, PE STRUCTURA REALĂ.

   NU folosi .gitignore obișnuit, cu liste de ce nu se urmărește. La un
   proiect mare, pericolul nu e să uiți un fișier, ci să verși conținut în
   afară: parole, fișiere personale, zeci de GB.

   Folosește inversul: interzici TOTUL, apoi deschizi doar căile pe care
   proiectul le are cu adevărat. Le identifici citind structura lui — nu
   întrebând și nu ghicind.

   /*
   !/README.md
   !/src/
   !/src/**

   Reguli care contează:

   - Ordinea contează: ultima regulă care se potrivește câștigă.
   - Git NU coboară într-un director interzis. Ca să redeschizi un fișier,
     redeschide și PĂRINTELE lui, chiar dacă pe acesta cazi înapoi imediat.
   - `**` se potrivește și cu ZERO componente: `/_x/**` închide și directorul
     `_x` însuși.

   Verifică singur, cu `git check-ignore -v`, în AMBELE sensuri:
   - pe un fișier care TREBUIE urmărit → răspunsul corect e că NU e ignorat;
   - pe unul care NU trebuie → trebuie să rămână ignorat.
   Dacă verificarea contrazice regula, corectezi regula și reverifici.

7. PRIMUL COMIT, REPO-UL PRIVAT, PUSH-UL.

   Numele repo-ului îl DERIVI TU din numele folderului: litere mici, cifre,
   cratime. Nu îl ceri, nu îl întrebi. Îl anunți în raport.

   git add -A
   git commit -m "prima stare a proiectului"
   gh auth login                    (doar dacă nu ești deja autentificat)
   gh repo create <nume> --private --source=. --remote=origin --push

   Acest push NU ceri acord pentru el: fără el repo-ul nu există încă, deci
   face parte din instalare. De aici înainte, orice push cere acordul meu.

8. LINII CRUCIALE — NU LE SARI.

   - `core.autocrlf false` pe Windows: altfel fiecare fișier apare modificat
     la fiecare clone, fără ca cineva să fi atins ceva. E cauza #1 de
     „proiectul e stricat" pe Windows.
   - NICIODATĂ `git clean -fdx`. Șterge fișiere ignorate care pot fi conținut
     real.
   - NICIODATĂ `git reset --hard`. Distruge munca necomitată.
   - Fără `force push`.
   - Nu pune parole, tokenuri sau chei în fișiere urmărite. Dacă apare unul,
     îl scoți din urmărire, îl comentezi, și îl spui în raport.

9. VERIFICĂ SINGUR, REPARĂ DACĂ NU CONCORDE.

   După push: `git ls-remote origin main`. ASTA e adevărul, nu codul de
   ieșire — git scrie progresul pe stderr și poate arunca o eroare roșie
   chiar când totul a mers bine.
   Dacă verificarea nu confirmă, repeți și corectezi. Nu anunți succes pe
   baza unui cod de ieșire.

10. LA FINAL, UN RAPORT. Cu cifre măsurate acum, nu cu impresii:

   - ce a existat înainte și ce ai creat
   - numele repo-ului și DE CE l-ai ales așa
   - ramura, comitul, adresa
   - ce verificări ai făcut și ce au răspuns, cu răspunsul
   - singurul lucru rămas, dacă a rămas, și de ce
```

---

## Versiunea scurtă, pentru un AI cu context mare

```text
Tu faci totul și tu decizi totul. Nu mă întrebi nimic, nu te oprești la
mijloc: numele repo-ului, ramura, extensiile, .gitignore le alegi tu și îmi
spui ce ai ales. Singurul motiv real de oprire e un cod sau o plată de la mine.

Măsoară, instalează ce lipsește cu winget, apoi: git init -b main (fără
ramuri, nu checkout -b), core.autocrlf false, lrc hooks disable (scoate poarta
LiveReview de pe comit, per repo, înainte de primul comit), .gitignore prin
negare (/* interzice totul, deschizi explicit căile reale ale proiectului,
verifici cu git check-ignore în ambele sensuri), primul comit, gh repo create
<nume-derivat-din-folder> --private --push. Primul push face parte din
instalare: nu ceri acord. Verifici cu git ls-remote, nu cu codul de ieșire.

De acum înainte: main, nu ramuri. Commit autonom la fiecare pas, taskul nu e
gata cât timp git status arată ceva. Push doar peste un prag de comituri și
doar cu acordul meu. LiveReview rulează DOAR după push, pe ce e deja pe
GitHub, și nu poate bloca push-ul; două căi de push, cu review și fără, pentru
când contul free se termină — rate limit nu e eroare. Nu rula niciodată git
clean -fdx sau git reset --hard. Nu comite parole. Interfața nu o schimbi.
```

## Ce vine după

Instalarea e terminată aici. De acum înainte, la fiecare ședință, merge `PROMPT git autonom.md` — commit autonom, push doar cu acordul meu, interfață neatinsă. Invers, acesta n-are pe ce lucra.

**Nu retrimite acest prompt.** Rulat de două ori, face un al doilea repo pe același proiect.

## Ce am măsurat pe această mașină, ca să fie verificabil

| Ce | Valoare măsurată |
|---|---|
| Git | `2.56.0.windows.2` |
| GitHub CLI | `gh 2.97.0 (2026-07-31)` — instalat |
| Autentificare | `hosts.yml` există → logat |
| `core.autocrlf` | `false` — **pe nivel de repo, nu global** |
| `core.eol` / `core.filemode` | `native` / `false` |
| `core.hooksPath` | `C:\Users\apviz\.git-hooks` (global) — **se lasă așa**, dar se dezactivează **per repo** |
| Identitate | `Sentinel Prime <sentinel.prime@optimus.local>` (global) |
| Credential | `credential.https://github.com.helper = store` |

`gh` e deja prezent și logat pe această mașină — la o instalare aici, singurul punct unde instalarea s-ar opri nu apare.

### LiveReview — pas obligatoriu, imediat după `git init`

```
lrc hooks disable
```

**Nu sari peste asta.** `core.hooksPath` e global, deci poarta LiveReview e
armată automat în orice repo nou. În context non-interactiv (agent, CI,
butonul aplicației) `pre-commit` cere un fișier de atestare și iese cu 1, iar
acel fișier nu are de unde veni — nici fără nimic în staging, nici cu
`--allow-empty`. Primul comit se blochează și pierzi timp căutând de ce.

Reversibil: `lrc hooks enable`. Vizibil: `lrc hooks status`. Nu se atinge
`core.hooksPath` global și nu se șterge nimic — se scrie un marcaj în
`.git\lrc\`, care nu ajunge niciodată în comit.

### Unde ajunge LiveReview după instalare

**Comitul nu e niciodată sub poartă.** `git commit` și `git push` sunt libere.

LiveReview se mută pe **push**, și încă mai târziu: rulează **după** ce push-ul
e confirmat pe server, pe ce tocmai a ajuns pe GitHub.

```
lrc review --range origin/main..HEAD --no-serve
```

Ordinea nu se negociază: **măsoară → push → verifică pe server → review.**
Review-ul nu poate bloca un push, pentru că push-ul deja s-a făcut.

**Două căi de push**, pentru că `free_30k` (30.000 LOC) se termină într-o zi:

| | Calea 1 | Calea 2 |
|---|---|---|
| Push | identic | **identic** |
| Review | după push | **nu** |
| Mesaj de eroare pentru Popy | niciunul | **niciunul** |

Calea 2 e calea de rezervă prevăzută: cont epuizat, rate limit, LiveReview
căzut. În calea 2 se notează pur și simplu că review-ul n-a fost trimis.
**Un review lipsă nu e un push eșuat** — și nu apare ca unul în panoul lui.

### Cele patru documente

Sistemul are patru documente, două părți:

| Partea | Skill | Prompt |
|---|---|---|
| **1.Instalare** — ridicarea repo-ului, o singură dată | `SKILL.md` | `PROMPT git install.md` |
| **2.Funcționare** — regula de zi cu zi, restul vieții | `SKILL.md` | `PROMPT git autonom.md` |

Fiecare parte are **două** documente: skillul pentru agent, promptul care se
trimite ca atare altei instanțe. Toate patru se actualizează împreună — dacă
una schimbă o regulă, celelalte trei o spun la fel.

## Perechea, în archive

```
_SYSTEM\Skills\git-install\
├── SKILL.md                ← skillul, se încarcă la proiect nou
└── PROMPT git install.md   ← acest document, se trimite o singură dată

_SYSTEM\Skills\git-autonom\
├── SKILL.md                ← skillul, se încarcă la fiecare treabă cu Git
└── PROMPT git autonom.md   ← regula de lucru, pentru fiecare ședință
```