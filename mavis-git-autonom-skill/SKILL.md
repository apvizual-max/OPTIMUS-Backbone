# SKILL: git-autonom

**Trigger: orice proiect cu repo Git, orice sesiune, orice instanță. Se încarcă la prima treabă care atinge Git și rămâne activ până la finalul taskului.**

## Regula

**Commit = treaba mea. Push = decizia lui.**

## 1. COMMIT — autonom, la fiecare succes măsurat

Comit **înainte** de a raporta, nu la finalul taskului. Pas cu pas.

- Când o măsurătoare confirmă că ceva e corect, comit imediat.
- **Inclusiv pe modificările lui.** Dacă `git status` arată fișiere necomitate pe care le-a atins el, le comit și îi spun. Nu aștept să-l întreb.
- Nu cer confirmare. Nu spun „vrei să comit?". Nu las nimic în panoul Changes.
- Mesajul spune **ce s-a schimbat în cuvinte simple**, nu `chore: update <fișier>`.

De ce: un administrator nu lasă un panou `Changes` plin pentru un om care nu știe
ce e Git. Dacă eu comit la fiecare pas, Changes rămâne gol și nu are ce arăta.
Pentru el, Changes nu e ajutor — e blocaj.

## 2. PUSH — numai cu acordul lui

**Niciodată din inițiativa mea.** Nici prin butonul din interfață — acela nu se
folosește, nici de mine, nici de el.

- Când se adună prea multe comituri locale, **îl întreb eu**: „împing cele N
  comituri acum?" — și aștept răspunsul.
- El poate spune „fă push" oricând. Atunci îl fac.
- Dacă uităm amândoi, se vede: serverul rămâne în urmă.

## 3. Push-ul se verifică prin `git ls-remote`, NICIODATĂ prin codul de ieșire

În PowerShell cu `$ErrorActionPreference='Stop'`, `git push` scrie progresul pe
**stderr**, iar shell-ul aruncă o eroare roșie chiar când push-ul a reușit.

```
git push origin master        # poate afișa "eroare" false
git ls-remote origin master   # ASTA e adevărul
```

Nu declar reușită nici din `exit 0`, nici din absența erorii.

## 4. Ce nu faci NICIODATĂ

| Nu | De ce |
|---|---|
| `git clean -fdx` | șterge fișiere ignorate — poate fi conținut real |
| `git reset --hard` | distruge munca necomitată |
| `Remove-Item` pe materialul lui | **mută, nu șterge**; neclarul merge în carantină cu motiv scris |
| `force push` fără cerere | rescrie istorie |
| commit cu parole/chei în mesaj | `git log` e public pentru oricine are acces |
| push din inițiativă proprie | decizia e a lui |

## 5. Cum îi recunosc comitul

Dacă apare un comit pe care eu nu l-am scris, **nu e intrus** până nu dovedesc
altceva. Căută în ordine: `git reflog` → hook-uri (`core.hooksPath`, `.git/hooks`)
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