---
name: mavis-git-autonom-skill
description: "Regula de lucru zilnică cu Git, într-un proiect care are deja .git. COMMIT autonom la fiecare succes măsurat, inclusiv pe modificările lui Popy, fără să ceri confirmare și fără să lași panoul Changes plin. PUSH doar când Popy spune explicit, verificat cu git ls-remote, niciodată prin butonul din interfață. Nu atingi interfața. Nu ștergi nimic: muți în carantină cu motiv scris. Prohibit: git clean -fdx, git reset --hard, force push fără cerere, parole sau chei în commit. Nu ceri decizii tehnice — le iei tu și continui. Se încarcă la prima treabă care atinge Git; instalarea de la zero e skillul mavis-git-install-skill."
---

# SKILL: git-autonom

**Cum funcționează Git după ce e pus, în fiecare zi.**

| | |
|---|---|
| **Perechea** | skill: `git-autonom` · prompt: `PROMPT git autonom.md` |
| **Se încarcă** | la prima treabă care atinge Git, în orice proiect cu istoric |
| **Nu e** | instalarea — aceea e skillul `git-install`, rulează o singură dată |
| **Copie vie** | `C:\Users\apviz\.minimax\agents\mavis\skills\mavis-git-autonom-skill\SKILL.md` |

---

## Regula

**Commit = treaba mea. Push = decizia lui.**

## 1. COMMIT — autonom, la fiecare succes măsurat

Comit **înainte** de a raporta, nu la finalul taskului. Pas cu pas.

- Când o măsurătoare confirmă că ceva e corect, comit imediat.
- **Inclusiv pe modificările lui.** Dacă `git status` arată fișiere necomitate
  pe care le-a atins el, le comit și îi spun. Nu aștept să-l întreb.
- Nu cer confirmare. Nu spun „vrei să comit?". Nu las nimic în panoul Changes.
- Mesajul spune **ce s-a schimbat în cuvinte simple**, nu `chore: update <fișier>`.

De ce: un administrator nu lasă un panou `Changes` plin pentru un om care nu
știe ce e Git. Dacă eu comit la fiecare pas, Changes rămâne gol și nu are ce
arăta. Pentru el, Changes nu e ajutor — e blocaj.

## 2. PUSH — numai cu acordul lui

**Niciodată din inițiativa mea.** Nici prin butonul din interfață — acela nu se
folosește, nici de mine, nici de el.

- Când se adună prea multe comituri locale, **îl întreb eu** — și aștept răspunsul.
- Dacă uităm amândoi, se vede: serverul rămâne în urmă.

## 3. Push-ul se verifică prin `git ls-remote`, NICIODATĂ prin codul de ieșire

În PowerShell cu `$ErrorActionPreference='Stop'`, `git push` scrie progresul pe
**stderr**, iar shell-ul aruncă o eroare roșie chiar când push-ul a reușit.

```
git push origin master        # poate afișa "eroare" falsă
git ls-remote origin master   # ASTA e adevărul
```

## 4. Ce nu faci NICIODATĂ

| Nu | De ce |
|---|---|
| `git clean -fdx` | șterge fișiere ignorate — poate fi conținut real |
| `git reset --hard` | distruge munca necomitată |
| ștergere pe materialul lui | **mută, nu șterge**; neclarul merge în carantină cu motiv scris |
| `force push` fără cerere | rescrie istorie |
| commit cu parole/chei | `git log` e citibil de oricine are acces |
| push din inițiativă proprie | decizia e a lui |
| atingerea interfeței | rezolvarea e comportament, nu buton |

## 5. Cum îi recunosc comitul

Dacă apare un comit pe care eu nu l-am scris, **nu e intrus** până nu dovedesc
altceva. Caută în ordine: `git reflog` → hook-uri (`core.hooksPath`, `.git/hooks`)
→ taskuri programate → aplicația însăși.

Cazul măsurat (2026-10-10): `chore: update <fișier>` vine din panoul
`Commit or push` cu mesajul lăsat **gol** — aplicația generează mesajul automat
(`suggestCommitMessage`). **Comitul e al lui.** Nu conflict de repo, nu instanță
cloud, nu Hermes, nu cron.

## 6. Backupul e reper, nu țintă

Backupul se **citește**, nu se scrie. Dacă lipsește ceva din dosarul de lucru,
**copiez din backup**, nu invers. Serverul e replica; localul e sursa.

## 7. La ce mă opresc

La push: cer acord. **Atunci totul.** Nu cer decizii tehnice — acelea le
decid eu, le spun odată cu explicația și continui.

## 8. Plasa de siguranță — `git-autocommit.ps1`

Ultima linie de apărare. **Nu înlocuiește disciplina de mai sus** — e pentru cazul
în care eu nu sunt: o sesiune oprită la mijloc, un alt agent, o noapte.

| | |
|---|---|
| **Script** | `AI-Kit\git-autocommit.ps1` |
| **Task** | `PKMS-GitAutoCommit`, la 5 minute, `apviz`, Limited, Interactive, fereastră ascunsă |
| **Log** | `AI-Kit\raport-autocomit.log` — scris **doar la eveniment**, ca să nu-și creeze singur arbore murdar |
| **Registru** | `AI-Kit\git-autocommit-registru.txt` — repo-ul, o cale pe rând |
| **Interziceri** | `AI-Kit\git-autocommit-ignorat.txt` — wildcard-uri pe căi care nu se comită niciodată |

**Cele patru porți, în ordine:**

1. **secrete pe NUME** — `.env`, `id_rsa`, `*.pem`, `credentials`, `secret`, `token`…
2. **secrete pe CONȚINUT** — chei PEM, `AKIA…`, `ghp_…`, `sk-…`, `password = "…"` etc.
   Citește doar text (binarele și cei peste 512 KB sunt sărite și **numărați**).
3. **căi interzise** — din registrul de mai sus. *Doar pentru căi care există:
   o ștergere a unei căi interzise nu blochează restul.*
4. **timp de așezare** — implicit 60 s; nu comită un fișier scris acum.

**Zone oarbe DECLARATE, nu ascunse:**

- Scriptul și registrul de interdicții **nu sunt scanați de poarta 2** — un detector
  conține tiparele pe care le caută. Numărul lor ajunge în mesajul de comit
  (`exceptie-definire 2`), ca oricine citește istoricul să vadă ce n-a fost necăutat.
- **O poartă recunoaște o CHEIE, nu o INTENȚIE.** Un fișier cu nume și conținut
  inocue care spune „nu comita asta" e opac pentru orice automat. Forma corectă
  e declarația explicită în registrul de interdicții.
- `git-autocommit.ps1 -AutoProbe` rulează 8 cazuri (5 pozitive + 3 negative).
  **Dacă nu pot deveni ROȘII, poarta e decor.** Rulează-l când schimbi tiparele.

**Coduri de ieșire:** `0` curat / așteaptă / salvat · `1` refuzat (secrete, căi
interzise, comit eșuat, parțial) · `2` mediu (repo invalid, git lipsă) ·
`3` autoproba a picat.

**Nu atinge:** interfața, hook-urile git globale (`C:\Users\apviz\.git-hooks`,
LiveReview — aparțin altui mecanism), backupul. **Nu face push.** Nu șterge nimic.

## 9. Promptul pereche

`PROMPT git autonom.md`, în același folder — se trimite ca atare altor
instanțe, în alte proiecte. Rulează **după** `PROMPT git install.md`.