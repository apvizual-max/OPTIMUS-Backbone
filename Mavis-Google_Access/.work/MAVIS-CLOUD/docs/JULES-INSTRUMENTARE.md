# Jules — documentație de instrumentare

Repo: **apvizual-max/MAVIS-CLOUD**. CLAUDE: acest document îl configurezi în Jules,
ca să știe ce are de făcut și cum.

---

## 1. Ce este deja conectat

Din capturile tale:

| Element | Stare |
|---|---|
| Repo `apvizual-max/Mavis` (acum `MAVIS-CLOUD`) | ✅ conectat |
| Suggestions BETA | ✅ pornit — arată deja sugestii reale |
| Knowledge → Memories | ⚠️ **gol** — trebuie umplut |
| Environment → Setup script | ⚠️ **gol** — trebuie completat |
| Network access | ✅ pornit |
| Environment variables | ⚠️ **gol** — necesare pentru Google API |
| Limita zilnică | 0/100 sesiune, 5 repo-uri max |

## 2. Sugestiile pe care Jules le-a găsit deja — și sunt **corecte**

Am citit lista din captura ta. Nu sunt false pozitive:

```
Blocking Async I/O in Loop          ← în kit.js, apelurile sequențiale în for
Sequential API Calls in Loop        ← același tip, în email-sort.js
Missing Escaping/Sanitization for Process Argument in cv-mutator.js
Missing Escaping/Sanitization for Process Argument in JSON.parse
Unused Import: WD_ALIGN_PARAGRAPH    ← în make-cv-docx.py
Add tests for buildHeader / buildSummary / cleanTitle / detectStress /
            classifyBusiness / buildLetter / pickLinks / hasWord / refresh
```

**Asta spune exact ce nu am făcut: nu există un singur test automat.**
Am verificat manual, cu `node --e` și cu randare în browser. Jules are dreptate
că nimic din aia nu e prins în CI, și de aceea workflow-ul meu a prins o
sintaxă stricată **după** ce o comitem, nu înainte.

**Concluzia: cea mai bună integrare nu e să-l atașez, ci să-l fac să prindă
ce eu uit.**

## 3. Ce configurezi în Environment → Setup script

**Eroarea pe care ai primit-o:**
```
E: Could not open lock file /var/lib/apt/lists/lock - open (13: Permission denied)
E: Unable to lock directory /var/lib/apt/lists/
```

**Cauza:** Jules rulează ca utilizator normal, **nu ca root**. `apt-get` are nevoie
de `sudo`. Scriptul meu punea `apt-get update -qq` fără `sudo`, și cu `set -e`
se oprea la prima eroare.

Scriptul reparat e în `docs/JULES-SETUP-SCRIPT.sh` din repo. **Copiază-l în întregime:**

```bash
#!/usr/bin/env bash
# Setup pentru Jules - MAVIS-CLOUD
# REPARAT: Jules ruleaza ca utilizator normal, NU ca root.
# De aceea apt-get si pip au nevoie de sudo explicit.
set -uo pipefail

echo "1/6  cine sunt: $(whoami)"
cd /app 2>/dev/null || { echo "nu pot intra in /app"; exit 1; }

echo "2/6  instalez dependintele..."
# TOATE comenzile de sistem au sudo. Fara, primesc 'Permission denied'
# pe /var/lib/apt/lists/lock - exact eroarea pe care ai vazut-o.
if ! sudo -n true 2>/dev/null; then
  echo "     sudo fara parola NU merge. Ramane fara instalare de sisteme."
else
  sudo apt-get update -qq 2>&1 | tail -2
  sudo apt-get install -y -qq git ripgrep 2>&1 | tail -2
fi

echo "3/6  verific node si python..."
command -v node  && node --version  || echo "     node LIPSA - deja instalat in imagine"
command -v npm   && npm --version   || echo "     npm LIPSA"
command -v python3 && python3 --version || echo "     python3 LIPSA - deja instalat"

echo "4/6  dependinte npm locale, fara sudo..."
npm install --silent --no-audit --no-fund 2>&1 | tail -3 || echo "     fara package.json, se sare"

echo "5/6  dependinte python, cu --user..."
pip3 install --quiet --user requests 2>&1 | tail -2 || echo "     requests deja e acolo"

echo "6/6  verific ca proiectul e complet..."
echo "     commit: $(git rev-parse --short HEAD 2>/dev/null || echo 'fara git')"
echo "     docs/: $(ls docs/*.md 2>/dev/null | wc -l) documente"
echo "     site/: $(ls SITE/dist/*.html 2>/dev/null | wc -l) pagini"

echo ""
echo "Mediu pregatit."
```

### Ce s-a schimbat, și de ce

| Înainte | După | De ce |
|---|---|---|
| `apt-get update` | `sudo apt-get update` | **cauza erorii tale** — non-root |
| `set -euo pipefail` | `set -uo pipefail` | prima eroare oprea tot restul |
| `npm install -g claude-code` | scos | irelevant, lent, nu e nevoie |
| `cd /app \|\| cd "$REPO_DIR"` | doar `cd /app` | repo-ul e deja clonat acolo |
| `\|\| true` peste tot | `||` cu mesaj | nu ascunde ce nu merge |

**Node, npm și python3 sunt deja în imaginea Jules.** Nu trebuie instalate.
Am scris ca să le verific, nu ca să le pun — ca să nu mai mori pe un `apt-get`.

**Dacă `sudo` nu merge fără parolă**, scriptul sare peste instalare și continuă.
E preferabil să aibă un mediu parțial decât să moară complet.

## 4. Ce configurezi în Environment → Environment variables

**NU pune secrete aici.** Cheile stau în managerul de secrete și nu ajung în repo.

| Cheie | De ce |
|---|---|
| `JULES_API_KEY` | pentru apeluri Jules din CI |
| `GITHUB_TOKEN` | pentru operații pe repo |
| `GOOGLE_OAUTH` | pentru Gmail/Drive — **doar dacă vrei ca Jules să aibă acces** |

## 5. Ce configurezi în Knowledge → Memories

Gol înseamnă că **nu știe nimic despre proiect**, deși vede codul. Adaugă:

```
Mavis Cloud lucrează pentru Alexandru Popescu (POPY), designer și art director,
București. Repo-ul conține: motor de CV (cv-mutator.js, letter-engine.js),
scoring de joburi (scoring.gs), site de CV construit din date JSON (SITE/),
instrumente Google (mavis-tools/), 29 de skill-uri.

Reguli care NU se încalcă niciodată:
- niciodată ștergere definitivă, doar Trash
- niciodată trimitere în numele lui POPY
- niciun număr fără numărare reală (resultSizeEstimate din Gmail e plafonat)
- niciun nume de client care nu vine din materialul lui
- șabloanele sunt generice, niciodată cu nume de firmă concretă
- se lucrează pe main, fără ramuri, dacă POPY nu cere altfel
```

## 6. Live Review de la GitHub

**Funcționează deja** — hexmos.com, plan free 30%.

Singura condiție: **rulează pe pull request, nu pe push direct.**
În captura ta scrie „No review pipeline data yet" — pentru că încă nu a existat PR.

Ca să-l vezi prima dată:
```bash
git checkout -b o-verificare
# o schimbare mică
git commit -m "..."
git push -u origin o-verificare
gh pr create --base main --head o-verificare --title "Verificare" --body "..."
```

## 7. Ce cer de la Jules, formulat ca task

```
Creează teste pentru ALEX-KIT/cv-mutator.js și ALEX-KIT/letter-engine.js.
Funcțiile de acoperit: buildHeader, buildSummary, cleanTitle, detectStress,
buildExpertise, buildAchievements, buildLetter, pickLinks, hasWord, refresh.

Criterii de acceptare:
- testele rulează cu `node --test` sau un runner similar
- acoperă cel puțin: titlu determinist prin FAMILY_TITLE, hasWord cu limite
  de cuvânt (ai nu trebuie să se potrivească în 'said'), placeholder [ROLE],
  prăjina unică a fiecărei specializări
- niciun test nu depinde de rețea
- rulează în workflow, nu doar local

Restricții:
- nu rescrie motorul, doar adaugă teste
- nu introduce dependințe noi
```

## 8. Ordinea corectă a integrării

| Pas | Ce | Cine |
|---|---|---|
| 1 | Setup script în Environment | POPY, 5 minute |
| 2 | Memoriile în Knowledge | POPY, 3 minute |
| 3 | Primul pull request → vezi Live Review + Jules | POPY sau Mavis Cloud |
| 4 | Cererea de teste de la Jules | Jules |
| 5 | Workflow cu teste | Mavis Cloud |

**Se poate opri după pasul 2** dacă nu merge mai departe. **Nu se începe cu API-ul.** Se începe cu Environment + Knowledge, pentru că
acolo Jules chiar nu știe nimic. API-ul vine după, ca să automatizezi ce manual făcut.

## 9. Ce am nevoie înapoi de la tine

**Nimic urgent.** cheia Jules e deja la mine, în managerul de secrete.
Doar când ai făcut pasul 1 și 2, spune-mi, și eu verific dacă Jules prinde
sugestiile — prin API sau citind ce a scris în repo.