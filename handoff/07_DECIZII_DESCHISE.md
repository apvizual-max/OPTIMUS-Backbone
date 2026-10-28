# Decizii deschise — ale lui Popy, nu ale mele

Am rezolvat partea tehnică acolo unde se putea. Ce rămâne aici e **al tău**,
pentru că schimbă direcția sistemului, nu doar o implementare. Fiecare are
faptele măsurate și o recomandare — ca să poți spune „da" sau „altfel", nu
să alegi între variante tehnice pe care nu le înțelegi.

Formatul recomandat de tine: **raport** = scop, cifre măsurate acum sau
`NOT_MEASURED`, decizii, verdict.

---

## D1. Cele 12 comituri de pe GitHub, publicate fără acord

**Fapt.** Măsurat pe 2026-10-11: 12 comituri au ajuns pe `main` fără acordul
tău. Poarta de push de azi e **preventivă** (blochează împingerile viitoare),
nu reparatorie.

**Recomandare: se păstrează.** Rescrierea istoricului publicat ar șterge dovezi
și ar încălca liniaritatea. E o decizie despre istorie, nu despre cod.

**Ce trebuie știut:** nu s-a făcut *force-push* și nu s-a rescris nimic. Poarta
de azi e dovedită (vezi `05_GIT_GITHUB.md` §2.1).

## D2. Poarta de push pe server (în repo-ul GitHub)

**Fapt.** Poarta de acum rulează pe client, în `pre-push`. Pe server
(`apvizual-max/OPTIMUS-Backbone`) **nu există** nimic care să oprească o
împingere făcută din altă clonă sau din interfața GitHub.

**Recomandare: se pune.** E singurul loc unde poarta chiar oprește *pe
server*. Sunt contul și repo-ul tăune — de aceea nu le-am atins în unilateral.

**Ce e necesar:** un workflow GitHub Actions care refuză push-urile care
nu vin prin poarta locală (de exemplu, verificând un commit-semnat sau
absența unui commit marcat).

## D3. Rotirea tokenului GitHub din `scripts/hermes-custom/`

**Fapt.** `backup-hermes.py` și `weekly-backup.bat` conțin un token personal
`ghp_` **hardcodat ca valoare implicită**. Folderul e ignorat de git, deci
tokenul **nu** e în istorie — dar e în clar pe disk.

**Recomandare: rotești tokenul** (din contul tău) și muti valoarea într-o
variabilă de mediu. E o acțiune de cont, nu de cod — de aceea e a ta.

## D4. Cheia AI (BYOK) pentru analiză reală în dashboard

**Fapt.** Control Center-ul colectează și afișează stare **măsurată**. Analiza
AI efectivă (interpretarea stării) n-are o cheie — de aceea nu apare în
dashboard.

**Recomandare: pune o cheie**, dacă vrei ca dashboardul să și *interpreteze*,
nu doar să arate. Fără ea, tot ce apare în „anomalii" e măsurătoare, nu
concluzie — și e etichetat ca atare.

## D5. Ce se întâmplă cu cele cinci repo-uri de pe GitHub

**Fapt.** După unire, conținutul lor e în SOT. **Remote-urile lor nu mai primesc
nimic** — deci, în timp, vor deveni mai vechi decât SOT-ul. Excepție:
`MAVIS-OPTIMUS-CI` (mirrorul de pe `E:`) e folosit de pipeline și are nevoie de
remote-ul lui.

**Recomandare:**
- `MAVIS-OPTIMUS-CI` → **se păstrează** (pipeline-ul are nevoie de el).
- `SENTINEL_PRIME`, `Mavis-Google_Access`, `MAVIS-CLOUD`,
  `Optimus-Mavis-Skills` → **se arhivează ca istoric** (bundle-urile sunt deja
  în `backups\_git_history\`) și se retrag din fluxul zilnic. SOT-ul devine
  singura sursă de adevăr, cum ai cerut.

## D6. Direcția propagării pentru oglinda de skill-uri

**Fapt.** `60_SKILLS\_links\mavis-skills` → registry-ul **live**
(`C:\Users\apviz\.minimax\agents\mavis\skills`), care e și repo git cu
remote propriu. Canonicul e în SOT (409 fișiere). Astăzi: **93 de foldere de
skill în canonic, 94 în live** — diferența e `state`, un folder de runtime, nu
de skill.

**Întrebarea:** cine propagă spre cine, la o modificare? Recomandarea mea:
**live → canonic**, cu comit explicit, pentru că registry-ul live e cel pe
care îl consumă aplicația și acolo apare prima schimbare.

## D7. Cine deține portul 8900

**Fapt.** Doă watchdogs îl urmăresc: cel din SOT și cel din arborele QWEN
(alt proiect). Niciunul nu omoară serverul celuilalt — dar cine pornește primul
câștigă portul, și atunci dashboardul servit poate fi **celălalt**.

**Recomandare:** supraveghetorul SOT-ului să verifice că serverul care răspunde
pe 8900 e **al SOT-ului** (nu doar că portul răspunde) și să îl repornească
dacă nu e. E o schimbare în `scripts\cc-watchdog.ps1`, în scope-ul SOT-ului —
spune-mi dacă vrei s-o aplic.

## D8. Curățenia din `%TEMP%`

**Fapt.** 111.417 de fișiere, 318,5 MB, scurgere din 06-10 octombrie. Nu mai
blochează nimic (helperul cu GUID a rezolvat dependența), dar e murdărie.

**De ce nu am șters:** ștergerea în masă e blocată de politica instrumentelor
(`mavis-trash` pe 111k de fișiere). Se poate face cu un script dedicat, cu
confirmare.

## D9. Proiectul lui Jules

**Fapt.** `Optimus_CD (by Jules)` e un **junction** spre `E:\Google\GDrive\...`,
ignorat de git, neatins. Nu intră în istorie și nu a fost modificat.

**Decizia:** păstrăm junction-ul (nu costă nimic) sau îl scoatem ca SOT-ul
să nu mai aibă legături în afara lui? Recomandarea: **îl păstrăm** — e
conveniența lui Jules, și proiectul lui, nu al nostru.

---

## Ce **nu** mai e decizia ta

Rezolvat tehnic în această sesiune, cu măsurători:

- **Starea runtime SENTINEL** (rescrisă la ~40 s) → 1.239 de fișiere scoase
  din urmărire, rămân pe disk, istoricul păstrat, motiv scris în `.gitignore`
  și în mesajul de commit.
- **`test_suite.py` și `test_sentinel.md`** (rescrise de motor la fiecare ciclu)
  → la fel, măsurat în două runde consecutive.
- **Dubla proprietate pe 8900** → încă deschis, pentru că soluția presupune
  să omâți un server dintr-un alt proiect (vezi D7).
- **Supravegherea SOT-ului la logon** → taskuri noi, `..._SOT`, cu nume
  distincte; cele QWEN neatinse.
