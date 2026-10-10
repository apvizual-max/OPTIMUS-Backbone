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

COMMIT = treaba ta, automată, la fiecare pas.
PUSH = decizia mea — cu singura excepție a primului push din instalare, care
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

   git init
   git config core.autocrlf false      ← vezi secțiunea 7, nu le sări
   git config core.eol native
   git config core.filemode false
   git checkout -b main                ← alegi tu `main`, nu întrebi

5. .gitignore — ÎL SCRII TU, PE STRUCTURA REALĂ.

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

6. PRIMUL COMIT, RAMURA, REPO-UL PRIVAT, PUSH-UL.

   Numele repo-ului îl DERIVI TU din numele folderului: litere mici, cifre,
   cratime. Nu îl ceri, nu îl întrebi. Îl anunți în raport.

   git add -A
   git commit -m "prima stare a proiectului"
   gh auth login                    (doar dacă nu ești deja autentificat)
   gh repo create <nume> --private --source=. --remote=origin --push

   Acest push NU ceri acord pentru el: fără el repo-ul nu există încă, deci
   face parte din instalare. De aici înainte, orice push cere acordul meu.

7. LINII CRUCIALE — NU LE SARI.

   - `core.autocrlf false` pe Windows: altfel fiecare fișier apare modificat
     la fiecare clone, fără ca cineva să fi atins ceva. E cauza #1 de
     „proiectul e stricat" pe Windows.
   - NICIODATĂ `git clean -fdx`. Șterge fișiere ignorate care pot fi conținut
     real.
   - NICIODATĂ `git reset --hard`. Distruge munca necomitată.
   - Fără `force push`.
   - Nu pune parole, tokenuri sau chei în fișiere urmărite. Dacă apare unul,
     îl scoți din urmărire, îl comentezi, și îl spui în raport.

8. VERIFICĂ SINGUR, REPARĂ DACĂ NU CONCORDE.

   După push: `git ls-remote origin main`. ASTA e adevărul, nu codul de
   ieșire — git scrie progresul pe stderr și poate arunca o eroare roșie
   chiar când totul a mers bine.
   Dacă verificarea nu confirmă, repeți și corectezi. Nu anunți succes pe
   baza unui cod de ieșire.

9. LA FINAL, UN RAPORT. Cu cifre măsurate acum, nu cu impresii:

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

Măsoară, instalează ce lipsește cu winget, git init, core.autocrlf false,
checkout -b main, .gitignore prin negare (/* interzice totul, deschizi
explicit căile reale ale proiectului, verifici cu git check-ignore în ambele
sensuri), primul comit, gh repo create <nume-derivat-din-folder> --private
--push. Primul push face parte din instalare: nu ceri acord. Verifici cu git
ls-remote, nu cu codul de ieșire. Nu rula niciodată git clean -fdx sau git
reset --hard. Nu comite parole. Commit autonom, push doar cu acordul meu de
acum înainte. Interfața nu o schimbi.
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
| `core.hooksPath` | `C:\Users\apviz\.git-hooks` (global) |
| Identitate | `Sentinel Prime <sentinel.prime@optimus.local>` (global) |
| Credential | `credential.https://github.com.helper = store` |

`gh` e deja prezent și logat pe această mașină — la o instalare aici, singurul punct unde instalarea s-ar opri nu apare.

## Perechea, în archive

```
_SYSTEM\Skills\git-install\
├── SKILL.md                ← skillul, se încarcă la proiect nou
└── PROMPT git install.md   ← acest document, se trimite o singură dată

_SYSTEM\Skills\git-autonom\
├── SKILL.md                ← skillul, se încarcă la fiecare treabă cu Git
└── PROMPT git autonom.md   ← regula de lucru, pentru fiecare ședință
```