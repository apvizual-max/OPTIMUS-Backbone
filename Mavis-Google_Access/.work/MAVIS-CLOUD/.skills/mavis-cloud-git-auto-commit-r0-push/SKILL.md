---
name: mavis-cloud-git-auto-commit-r0-push
description: Mavis Cloud comiteaza si impinge automat pe main, fara intrebari. R0 = verificare inainte de push. Popieste POPY daca se aduna prea multe commituri.
---

# Git automat · comit → R0 → push

**Nimeni nu întreabă.** Fiecare schimbare se comitează pe `main` și se împinge
automat pe `apvizual-max/MAVIS-CLOUD`. POPY urmărește din sesiune.

## Fluxul, exact

```bash
cd /workspace/Mavis

# 1. starea, ca să știu ce fac
git status --porcelain

# 2. commit pe main — NICIODATĂ ramură, decât POPY cere explicit
git add -A
git commit -m "ce s-a făcut, într-o linie"

# 3. R0 — verificarea ÎNAINTE de push
node --check ALEX-KIT/cv-mutator.js
node --check ALEX-KIT/letter-engine.js
python3 SITE/build-hub.py
python3 -c "import ast,io,glob; [ast.parse(io.open(f,encoding='utf-8').read()) for f in glob.glob('SITE/*.py')]"
git diff --cached --name-only | grep -iE "secret|token|credential" && STOP

# 4. push pe main
git push origin main
```

## R0 — ce înseamnă

**R0 este verificarea care are loc înainte de push.** Nu după. Dacă ceva nu trece,
nu împingi, corectezi, și abia apoi.

| Verificare | De ce |
|---|---|
| `node --check` pe tot JS-ul | a prins o sintaxă stricată după ce am comis |
| build-ul site-ului | site-ul nu trebuie să fie rupt când îl vezi |
| `ast.parse` pe Python | la fel |
| secret în diff | nu comite niciodată tokenuri |
| **`git status --porcelain` după commit** | **obligatoriu — trebuie să fie GOL** |

> **Ultima linie a prins o eroare reală (2026-10-22):** un `git add -A && git commit`
> a raportat succes, dar un fișier editat în aceeași sesiune a rămas **necomitat**
> în working tree, iar push-ul a dus o versiune incompletă în repo. Verificarea
> `git status --porcelain` **după** commit prinde asta imediat. Dacă nu e gol,
> comitează din nou înainte de push.
>
> La fel: după push, verifică `git show origin/main:<fișier>` — nu te baza pe
> `raw.githubusercontent.com`, care servește **cache vechi** (minutele 1-2).

| Verificare | De ce |
|---|---|
| `node --check` pe tot JS-ul | a prins o sintaxă stricată după ce am comis |
| build-ul site-ului | site-ul nu trebuie să fie rupt când îl vezi |
| `ast.parse` pe Python | la fel |
| secret în diff | nu comite niciodată tokenuri |

## Regulile dure

1. **`main`, niciodată ramură.** Ramuri doar când POPY spune cuvântul „ramură".
2. **Fără întrebări.** Nu întreb dacă să comit. Comit.
3. **Fără „vrei să vezi?"** — împing și îi arăt starea.
4. **Fără deploy fără cerere explicită.** Un singur deployment:
   `https://da15e9yb994ps.space.minimax.io`. **Niciodată altul.**

## Când îi spun că împing

Nu mai mult de **5 commituri** pe `main` înainte de următoarea ședință, și
**niciodată** după 15 fără push. Îi spun într-un rând, ca să nu uităm.

## Cum îl vede POPY

În sesiune, panoul **Environmental Information** arată:
- **Changes** — fișierele modificate acum
- **Commit or push** — ce am comis
- **Git Graph** — istoricul pe main

De aceea comit și împing **imediat** după fiecare schimbare. Altfel panoul
rămâne gol și POPY nu vede nimic, crede că nu lucrez, și e frustrant.

## Ce NU este fluxul meu

**Nu versiunez prin deployment-uri.** Deploy-ul e un website, nu version control.
Version control e git: commit pe main, push, și istoricul rămâne.

Am făcut exact greșit aceasta: am creat 3 site-uri în loc să fac 1 și să-l
actualizez. **Nu se mai repetă.**
## AUDIT VIZIBILITATE — înainte de a schimba vizibilitatea unui repo

**Regula:** `git clone --depth 1` ascunde exact ce cauți. Auditul se face pe
**istoric complet + toate ramurile**.

```bash
git clone https://x-access-token:$GITHUB_TOKEN@github.com/OWNER/REPO.git
cd REPO
git fetch --unshallow
git fetch origin "+refs/heads/*:refs/remotes/origin/*"
git log --all -p > /tmp/audit.patch     # TOT istoricul, TOATE ramurile
wc -c /tmp/audit.patch
```

Apoi, pe `/tmp/audit.patch`, caută **valori**, nu pattern-uri de detectie:
`ghp_[A-Za-z0-9]{36}` · `1//[A-Za-z0-9_-]{30,}` · `GOCSPX-[A-Za-z0-9_-]{20,}` ·
`AIza[0-9A-Za-z_-]{30,}` · `AKIA[0-9A-Z]{16}` · `glpat-` · `xox[baprs]-` ·
chei private.

**Fals pozitive frecvente** (verificate 2026-10-22, nu presupune):
- `ghp_xxxx…`, `GOCSPX-aaaa…`, `xoxb-your-slack-bot-token` → placeholder-uri
- `AKIAIOSFODNN7EXAMPLE` → cheia exemplu oficială AWS
- șiruri de tip `1//…` găsite **în interiorul unui JPEG base64** → coincidență de octeți
- fixture-urile din auto-testele detectorului de secrete al vaultului
- `+@app.get`, `+@app.post` → decoratori de cod, nu e-mailuri

**Verifică dacă o valoare e vie**, nu doar prezentă:
- refresh token: `POST https://oauth2.googleapis.com/token` cu `grant_type=refresh_token`
  → `invalid_grant: Malformed auth code` = tokenul nu e al clientului ăsta
  → `invalid_grant: Token has been expired or revoked` = token real, mort
- cheie API: `GET https://www.googleapis.com/discovery/v1/apis?key=KEY`
  → **400 „API key not valid"** = moartă · **403** = **vie**, cu restricții
- revocare: `POST https://oauth2.googleapis.com/revoke` cu `token=...` (fără credențiale!)

**Principiul de decizie:**
| Conținut | Vizibilitate |
|---|---|
| config, motor, docs, skill-uri, contracte | **public** |
| secrete | revocate + rotite, niciodată în repo |
| arhive, transcripte, media, date de terți | **privat** |

Auditul complet al celor 10 repo-uri: `docs/AUDIT-VIZIBILITATE-REPO-URI.md`.

## VALORI DE SECRETE — nu le scrie NICIODATA într-un repo public

**Măsurat 2026-10-22:** am scris două refresh token-uri și o cheie API **cu
valoarea completă** într-un document dintr-un repo public. **GitHub secret
scanning a refuzat push-ul** — corect, și exact pentru motivul care contează:
repo-ul e public, deci valoarea e expusă.

**Regula:**
- În documente (mai ales publice) scrii **prefix + referință**:
  `AIzaSyAy…(restul în secret manager: NUME_SECRET)`
- **Valoarea completă stă în secret manager** (`secret create --name=... --value=...`),
  de unde o iai din panou.
- **Valoare revocată** tot nu se scrie complet: poate fi încă validă pentru alt
  client, și istoricul e public.
- Fals pozitivele rămân false pozitive — vezi tabelul de mai sus.

**Dacă ai scris deja o valoare reală într-un commit NEîmpins:**
`git reset --soft HEAD~1` → redactează → `git add -A` → commit nou. Nu ajunge
istoric — nu a fost împins, deci nu există de șters.

**Dacă ai împins deja:** trebuie rescris istoricul (filter-repo / BFG) **și**
valoarea trebuie rotată/revocată. Rotirea e obligatorie oricum — rescrierea
istoricului nu anulează o valoare deja clonată.
