# RAPORT DE STARE COMPLET — pentru Gemini

**Data:** 2026-10-12 05:00 București
**De la:** Mavis Cloud (agent stateless, online 24/7)
**Sistem:** MAVIS-CLOUD — repo `https://github.com/apvizual-max/MAVIS-CLOUD`

---

## SUMAR EXECUTIV

| Domeniu | Stare | Număr |
|---|---|---|
| Git commits | ✅ sincronizat | **36** |
| Necomitate | ✅ zero | 0 |
| Nepushuite | ✅ zero | 0 |
| Documente `.md` | ✅ | **175** |
| Skill-uri proprii | ✅ | 19 |
| Skill-uri vendor (Emil Kowalski) | ✅ cu licență | 16 |
| Priming KIT | ✅ | 11 |
| Scripturi `mavis-tools/` | ✅ | 36 |
| Workflow-uri GitHub | ✅ ambele verzi | 2 |
| Handoff-uri | ✅ | 15 |
| Rapoarte Sentinel | ✅ | 6 |

**Nu există nimic necomitat și neîmpins. Nu cer confirmări.**

---

## 1. ARHITECTURA — cine face ce

```
CLOUD (Mavis Cloud)          LOCAL (Mavis)
container stateless          calculatorul lui POPY
online 24/7                  are fișierele și browserul
─────────────────────        ─────────────────────
cercetare, web               producție, editare fișiere
scoring, calcul              cod, site-uri
generare CV / scrisori       browser, sesiuni
sintetiză, rapoarte          deploy local
procesare izolată            execuție pe mașină

        ↕  PUNTE: repo GitHub  ↕
     singura sursă de adevăr, ambele scriu aici
```

**Legea:** tot ce cere **sesiune de browser** sau **server cu licență** → Local.
Tot ce e **API + fișiere** → Cloud.

**Regula „nici jumătate de sarcină":** un handoff nu e „restul îl face Local".
Un handoff e o **sarcină completă**, cu toate datele strânse. Local primește munca
gata de rulat, nu o problemă de rezolvat.

**Regula Jules (dată de POPY, 12 octombrie):**
> „Jules face propuneri, eu le tratez. Dacă e făcut în cloud, fac eu. Dacă ține de
> Local, i-o las lui. **Nu fac jumătate de sarcină.** Sunt responsabil de relația
> cu Local, mai ales pe propunerile lui Jules."

Când Jules propune ceva și eu nu pot singur, las handoff cu cerința completă.
**Eu decid** dacă merit s-o iau. Nu întreb.

---

## 2. JULES — capitol complet

### 2.1 Cele patru mecanisme de declanșare

Verificate în documentație, **nu ghicite:**

| # | Mecanism | Stare |
|---|---|---|
| 1 | **Eticheta `jules` pe un GitHub issue** → „label on, task live" | ✅ **funcționează, testat** |
| 2 | Mențiune `@jules` pe PR — **doar** dacă Jules are PR deschis, și **doar** în Reactive Mode | documentat |
| 3 | **GitHub Action** — singurul programabil | ✅ reparat, verde |
| 4 | Jules CLI — `jules remote new`, `jules task create` | documentat |

### 2.2 Testul real

Issue #2 creat cu eticheta `jules`. Răspuns în câteva secunde, **fără apăsare manuală:**

```
google-labs-jules: Jules is [on it](https://jules.google.com/task/3684179346728645528)
```

### 2.3 Două bug-uri găsite prin testare

**Bug 1 — acțiune inexistentă.** `google-labs-code/jules-invoke@v1` **nu există**:

```
Unable to resolve action `google-labs-code/jules-invoke@v1`, unable to find version `v1`
```

Corect: **`google-labs-code/jules-action@v1.0.0`**, input **`jules_api_key`** (nu `api-key`).

**Bug 2 — cheia API era doar la mine.** `JULES_API_KEY` era în secret manager,
dar nu și în secrets-ul repo-ului. Acum e acolo.

### 2.4 Workflow construit

`.github/workflows/jules.yml` — trei declanșatori:

1. **Eticheta `jules`** → automat
2. **workflow_dispatch** → manual
3. **Săptămânal, duminica 09:00** → audit, **nu construiește**

Săptămânal, nu zilnic: **cota Jules = 100 cereri/zi.**

Auditul săptămânal: erori din log, `node --check`, verificare șabloane,
verificare workflow, raport. Verde → **nu deschide PR**, doar scrie „nimic de reparat".

### 2.5 Stare curentă

```
Verificare   → SUCCESS, 7/7 pași   (03:00 zilnic + manual)
Invoke Jules → SUCCESS              (etichetă + manual + săptămânal)
eticheta 'jules' → creată
JULES_API_KEY   → în secrets
repo → privat
```

Issue #2 în lucru: **teste automate pentru `ALEX-KIT/cv-mutator.js`**.
Cerut explicit: nu rescrie motorul, fără dependințe noi, **nu împinge pe main**, deschide PR.

---

## 3. NOTEBOOKLM — răspunsul definitiv

### 3.1 Ce am greșit

Am întrebat de două ori care cont are notebook-urile. **Ambele întrebări au fost greșite.**

Am presupus că e o limită de acces. **Nu e.** E o limită de platformă, verificată.

### 3.2 Faptul, verificat

**Conectorii disponibili în cloud:** `github` (95 unelte), `matrix` (13),
`cloudflare` (4), `figma` (2). **Atât.** Niciun NotebookLM.

### 3.3 De ce Cloud NU poate crea notebook-uri

| | Personal | Enterprise |
|---|---|---|
| Adresă | `notebooklm.google.com` | `notebook.cloud.google.com` |
| **API oficial** | **NU are** | **DA** |
| Autentificare | cont + **cookie-uri de browser** | token Google Cloud |
| Cost | gratuit | **licențe plătite** + IdP + proiect Cloud |

API-ul oficial există **doar pe Enterprise**: cere proiect Cloud cu facturare,
licențe plătite, furnizor de identitate configurat, roluri IAM.
**Pentru un designer independent — efort disproporționat.**

Calea fără Enterprise: CLI-ul `nlm`, care se autentifică prin **sesiune de browser**.

### 3.4 Împărțirea, definitiv

```
CLOUD    pregătesc  câte un document per folder, găti de încărcat,
                    numit MavisCloud-(subiect), conținut complet. Comit.
LOCAL    deschide   notebooklm.google.com, creează notebook-ul,
         face       încarcă documentele din repo, îmi dă ID-ul
```

**Nimeni nu mai întreabă pe cine. Cloud nu creează notebook-uri.**

---

## 4. REGULI DE PLATFORMĂ — documentate

Detalii complete în `docs/REGULI-PLATFORMA.md`. Rezumat:

### 4.1 CRON — locuri diferite

| | Cronuri Cloud | Cronuri Local |
|---|---|---|
| Unde le vezi | **platforma online** | interfața Local |
| Le vezi din cealaltă parte? | **NU** | **NU** |

**Când vorbim de cron, uită-te pe platforma online.**
Programat în cloud și căutat în Local = **„nu există" e concluzia greșită.**

### 4.2 DEPLOY — nu e control de versiuni

Instrumentul cloud **creează un nod nou** la fiecare rulare, nu actualizează.
Site-ul îl construiește **Local**. Cloud nu mai face deploy-uri.

Singurul deploy: `https://4nsxl2or95u1a.space.minimax.io`. **Nu se creează altul.**

### 4.3 VARIABILE — nu inventa identificatori

`LINKEDIN_EMAIL` scris în 3 fișiere. **Nu există.** Reparat → `GOOGLE_EMAIL`.

**Nu există „email de LinkedIn".** Login-ul e cu Gmail: `apvizual@gmail.com`.
Cheia e `LINKEDIN_PASSWORD`.

### 4.4 SECRETE — se pot adăuga, da

Secret manager-ul e sertar cu chei: **o cheie, un scop, deschisă la nevoie.**
Nu în chat, nu în repo, nu prin Jules.

---

## 5. ȘABLOANELE LUI POPY — le-am ratat

**Eram în atașamente tot timpul și le-am construit altele de la zero.**

Găsite acum și copiate în `ALEX-KIT/TEMPLATES-POPY/`:

```
TEMPLATE - CV - Senior Art Director & Creative Lead - LONG.md
TEMPLATE - CV - Senior Art Director & Creative Lead - SHORT.md
TEMPLATE - Intention Letter - {Company_Name_Here} - Art Direction.md
TEMPLATE - Scrisoare de intentie - {Nume_Companie_Aici} - Art Direction.md
OPERATIONAL_INPUT-OUTPUT_BLUEPRINT.md
GEMINI - Automating Job Application Process — PLAN / RAW / Extracted (334 KB)
```

**CV-ul SHORT e deja rezolvat:** gata, cu Microsoft / Nikon / Yokogawa,
recomandarea de la Kevin Donlon (Shipley Associates), datele corecte:
`apvizual@gmail.com` · `+40 722 121 752` · `ap-id.ro` · `linkedin.com/in/ap-id`.

**Nu îl rescrie. E baza.**

`{Company_Name_Here}` se înlocuiește cu numele firmei din anunț.
`ALEX-KIT/SABLOANE/` e construit din memorie — **nu se folosește pentru CV-uri finale.**

---

## 6. SECURITATE — incident verificat și închis

**`credentials.json` cu `client_secret` Google real**, găsit în zona de atașamente.

Verificat:
- **NU** în istoricul git — niciun commit
- **NU** în arborele repo-ului
- adăugat în `.gitignore` împreună cu `client_secret*.json`

`Alex - LinkedIn Access.md` — eliminat, **verificat că nu a fost niciodată în istoric.**

**Regulă:** cheile stau în secret manager. Niciodată în repo, niciodată în chat.

---

## 7. MAXHERMES — oprit

POPY: „MaxHermes rămâne ultimul."

Am început predarea și **am tăiat-o.** Predarea către un agent fără memorie,
înainte ca sistemul să fie stabil, ar pierde ce am construit.

Fișierele rămân neatinse în `docs/NEXT-MAXHERMES.md`.

---

## 8. CE RAMANE PENTRU LOCAL — complet, fără jumătăți

**8.1 — Setup Local**
```bash
git clone https://github.com/apvizual-max/MAVIS-CLOUD
cd MAVIS-CLOUD
cat AGENTS.md
cat docs/REGULI-PLATFORMA.md
cat docs/DEFINITIE-OPERATIONALA.md
cat docs/BRIDGE.md
cat docs/HANDOFF-COMPLET.md
```
Apoi construiește și testează `mavis-sync.sh` după `docs/BRIDGE.md`.
*De ce Local:* ai nevoie de fișierele tale și de sistemul tău.

**8.2 — Rebuild site-uri cu date verificate**
Email `apvizual@gmail.com` · telefon `+40 722 121 752` · portofoliu cu City Grill,
Aderma Protect, IL PASSO, Optima Call, Yokogawa, ROMEXPO, Croitorul Tau · linkuri pe `ap-id.ro`.
*De ce Local:* deploy-ul e instrumentul tău.

**8.3 — Notebook-uri din documente gata**
Documentele sunt pregătite în repo, cu numele `MavisCloud-(subiect)`.
*De ce Local:* NotebookLM cere browser.

---

## 9. REGULI CARE NU SE SCHIMBĂ

1. Nu șterg nimic definitiv. Trash doar.
2. Nu trimit nimic în numele lui POPY. Fără excepție.
3. Nu inventez numere, linkuri, clienți, credențiale.
4. „Gata" = POPY poate vedea și verifica. Nu „există un fișier".
5. Nu întreb date care există în CV, LinkedIn, Drive, site sau repo.
6. Deploy ≠ control de versiuni. Git e sursa de adevăr.
7. Nu afirm până nu verific.
8. Nu fac jumătate de sarcină.
9. Cron → verific pe platforma online.
10. Nu inventez nume de variabile.

---

## 10. URMĂTORUL PAS AL MEU — singur

Când Jules termină issue #2 și deschide PR-ul: **implementez propunerea lui.**
Cloud întâi, complet. Local doar dacă nu pot — și atunci handoff complet,
cu tot contextul, fără jumătăți.

---

*2026-10-12 05:00 · Mavis Cloud · pentru Gemini*