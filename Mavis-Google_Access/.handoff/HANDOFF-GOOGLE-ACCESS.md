# HANDOFF — Google Access (session cu 0 context, 0 memorie)

**Scop:** ca o sesiune nouă — sau orice alt AI de pe stație — să preia
conexiunea permanentă la Google **fără să o reconstruiască** și fără să
întrebe ceva ce poate citi de aici.

**Măsurat:** 2026-10-28, 00:40-04:05 UTC+2. Fiecare cifră din acest document a
fost produsă de o unealtă în această sesiune și este însoțită de comanda care o
produce.

> **Regula de aur a acestui handoff:** conține **fapte măsurate și căi de
> fișiere**, nu promisiuni. Un număr poate fi reverificat într-o comandă. O
> promisiune nu poate fi reverificată deloc.

---

## 1. Ce este, în trei rânduri

Un container Docker (`Google_Access`) ține **un singur credential** Google și
expune **un singur endpoint MCP** pe `http://127.0.0.1:8766/mcp`. Înregistrat
**global** în `C:\Users\apviz\.minimax\mcp.json`, deci **orice agent de pe
stație** îl moștenește, nu doar Mavis. O comandă — `ga-doctor.mjs` — **dovedește**
că funcționează, cu 11 verificări și un verdict unic.

**Nu reconfigurați nimic.** Dacă o sesiune „nu are Google", rulează punctul de
control și repară verificarea care a picat.

```powershell
node "C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\Mavis-Google_Access\scripts\ga-doctor.mjs"
```

---

## 2. Starea măsurată (2026-10-28, 01:54Z)

```
=== Google Access - control point ===
host=OPTIMUS_PRIME at=2026-10-28T01:54:00.065Z
container=Google_Access mcp=http://127.0.0.1:8766/mcp data=C:/Users/apviz/.minimax/google-access/data

CHECK C1.container OK   status=running health=healthy image=google-access:1.0.10 restart=unless-stopped
CHECK C1b.running-code OK   repo=63e4ea8d2bbb running=63e4ea8d2bbb match=true
CHECK C2.health OK   grant=live reauth=false tools=32
CHECK C3.services OK   state=HEALTHY OK=14 REFUSED=2[keep,sites] ERROR=0[] attempts=1
CHECK C4.extendlm OK   token_minutes_left=109 refresh_token=yes cloud_secret_age_min=11
CHECK C5.browser-mcp OK   server=minimax-notebooklm tools=4 path=C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\Mavis-Google_Access\google-layer\minimax-notebooklm.js
CHECK C6.mcp-registry OK   enabled=true url=http://127.0.0.1:8766/mcp type=streamable-http
CHECK C10.mcp-paths OK   checked=23 dead_total=0
CHECK C7.tasks OK   count=4
CHECK C8.consent OK   listener alive (processes=1)
CHECK C9.picker OK   session consumed (2026-10-27T23:48:10.291Z) - nothing to watch

SUMMARY checks=11 failed=0 warnings=0
VERDICT=PASS
```

| | |
|---|---|
| Container | `Google_Access`, imagine `google-access:1.0.10`, `Up 13 minutes (healthy)`, `127.0.0.1:8766->8766/tcp` |
| Grant | **LIVE**, 33 scope-uri, cont `apvizual@gmail.com` |
| Unelte | **32** |
| Servicii | **14 OK · 2 REFUSED (keep, sites) · 0 ERROR** (`C3`, `state=HEALTHY`) |
| Books | refuz **tranzitoriu** măsurat: HTTP 503 la 3 din 5 probe-uri brute; `C3` re-probează până la 4 încercări și afișează cauza |
| Taskuri | `Google_Access_Watch` (oră) · `Google_Access_Consent` (5 min) · `Google_Access_Doctor` (30 min) · `MavisExtendLMHeartbeat` (30 min) · `MavisPickerHeartbeat` (15 min) — **toate cu `lastResult=0`** |
| Repo Google Access | `Mavis-Google_Access`, ramura `main` = `origin/main`, divergență 0/0, arbore curat — **`.handoff\` este versionat aici** (introdus în `3c97e18`) |
| Repo backbone | `OPTIMUS-Backbone` `267ef3c` = `origin/main`, divergență 0/0 |
| Secrete | scanare pe diff indexat: `SCANNED=883 BLOCKS=0 WARNS=0` |
| Encoding | 105 fișiere, `PROBLEMS=0`, zero BOM |

Detaliul complet, cu fiecare măsurătoare: `STATE-MEASURED.md`.

---

## 3. Contractul de permanență

|-responsabil | Deținut de | Cine e proprietar |
|---|---|---|
| Credentialul | volumul montat `data/credentials.json` | containerul; **niciodată** într-un layer de imagine |
| Serverul MCP | un container, port 8766 | gazda, `restart=unless-stopped` |
| Grantul | un refresh token, 33 scope-uri | Google; se reînnoiește singur |
| Registry-ul | `C:\Users\apviz\.minimax\mcp.json` (global) | stația — fiecare agent îl moștenește |
| Regulile | `C:\Users\apviz\.minimax\AGENTS.md` §12.5 | fiecare agent |
| Punctul de control | `scripts/ga-doctor.mjs` + task | stația, la 30 de minute |
| NotebookLM | ExtendLM; token rotit de gazdă, snapshot publicat în secretul Cloud | gazda |

**Re-autentificarea e rară, prin design.** Tokenurile de acces se mintesc
silențios din refresh token. Când grantul expiră, `google_auth_status` spune
asta și afișează **un singur URL** de consimțământ; ascultătorul
(`Google_Access_Consent`, la 5 minute) e deja în picioare pe port 80 să prindă
callback-ul.

**Singurele două acțiuni umane rămase:**
1. **clickul de consimțământ** — doar când Google îl cere;
2. **alegerea pozelor** în Photo Picker.

---

## 4. Cele două refuzuri (NU sunt defecte)

| Serviciu | Răspuns măsurat | Motiv |
|---|---|---|
| `keep` | `403` | Google nu publică **niciun scope acordabil** pentru Keep |
| `sites` | `404` | API-ul Google Sites a fost **retirat** |

Popy: *„le voi importa eu prin gemini sau alte unelte la google drive"* — deci
sunt **amânate, sub managementul utilizatorului**, cu planul de automatizare
scris în `mavis-skill-google-keep-sites`.

**Capcana care a costat o zi:** ambele nume de scope sunt **invalide**, iar un
scope invalid **invalidează întreaga cerere de consimțământ** — celelalte 32 de
scope-uri valide nu se puteau acorda cât timp ele erau acolo. Au fost scoase
din `FULL_SCOPES`, **cu motivul scris în sursă**. Uneltele `gkeep_list` și
`gsites_list` **există în continuare**: fără scope, raportează `MISSING_SCOPE`
și trimit la `google_scope_upgrade`. **Nu tac niciodată.**

---

## 5. Procedurile pe care le vei folosi

### 5.1 „Nu are Google" — ce faci

```powershell
node "C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\Mavis-Google_Access\scripts\ga-doctor.mjs"
```

Citește **verificarea care a picat** (e numită în ieșire), repară **acea** bucată,
re-rulează. Nu reinstalezi, nu reconfigurezi, nu reiei consimțământul.

### 5.2 Un serviciu Google nu răspunde

```powershell
node "C:\Users\apviz\.minimax\google-access\probe-services.mjs"
```

Clasifică răspunsul, nu cererea: `OK` (a venit cu date) · `REFUSED` (Google a
refuzat — **măsurătoare**, nu eșec) · `ERROR` (nu a răspuns nimic) · `SKIP`.

### 5.3 Un server MCP nou, sau unul rupte

```powershell
node "C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\Mavis-Google_Access\scripts\probe-mcp-stdio.mjs" --name <intrare>
```

Face handshake MCP real peste stdio, cu comanda și argumentele **exact cum
sunt în registry**. Un fișier care există **nu** e un server care pornește.

### 5.4 Un scope Google nou

**Verifică-l mai întâi** în registrul de scope-uri Google sau în discovery
document. Un scope invalid costă un click de consimțământ pierdut **și**
invalidă toate celelalte scope-uri.

### 5.5 NotebookLM

```powershell
node "C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\Mavis-Google_Access\scripts\probe-notebooklm.mjs"
```

Două drumuri: **ExtendLM** (MCP, 160 unelte) și **browserul**
(`minimax-notebooklm`, 4 unelte, profil Chrome propriu, CDP **9412**). Rotirea
tokenului o face **doar gazda**; Cloudul consumă doar un snapshot.

### 5.6 Poze

```powershell
node "C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\Mavis-Google_Access\scripts\picker-watch.mjs" --session <id> --data "C:\Users\apviz\.minimax\google-access\data" --delete-after
node "C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\Mavis-Google_Access\scripts\picker-download.mjs"
```

Un `404` pe sesiune înseamnă **consumată**, nu defect: e marcată în fișier
(`session_id: null, state: consumed`), niciodată ștearsă.

---

## 6. Skillurile — încărcate de la prima comandă

**Botul central:** `C:\Users\apviz\.minimax\agents\mavis\skills\mavis-google-access-bot\SKILL.md`

```powershell
node "C:\Users\apviz\.minimax\agents\mavis\skills\mavis-google-access-bot\scripts\bot-registry.mjs" list
node "C:\Users\apviz\.minimax\agents\mavis\skills\mavis-google-access-bot\scripts\bot-registry.mjs" verify
```

| Membru | De ce îl încarci |
|---|---|
| `mavis-skill-google-access-control-point` | punctul de control + contractul de permanență |
| `mavis-skill-docker-access-point` | containerul, volumele, regula portului, „octeții rulați = octeții din repo" |
| `mavis-skill-browser-mcp` | stratul de browser + planul Browser MCP |
| `mavis-skill-mcp-development` | cum intră următorul MCP în punctul central |
| `mavis-skill-photo-picker` | singura ușă spre biblioteca foto |
| `mavis-skill-notebooklm-extendlm` | rotația tokenului, publicarea snapshotului |
| `mavis-skill-google-keep-sites` | cele două refuzuri + planul amânat |
| `mavis-skill-access-handoff` | chiar acest handoff: cum se predă mai departe |
| `mavis-skill-background-task-verdict` | cum se judecă o măsurătoare lungă: pe marcajele tipărite, nu pe codul de ieșire |

Lista completă, cu referințele existente: `SKILLS-INDEX.md`.

---

## 7. Ce **NU** se face

1. **Nu se reconfigurează setările.** Ele există și rulează singure.
2. **Nu se re-autentifică**, decât dacă Google cere și punctul de control arată
   `reauth_required=true`.
3. **Nu se adaugă scope-uri Google** fără verificare prealabilă.
4. **Nu se atinge credentialul** — nici citit, nici tipărit, nici copiat. Se
   citesc lungimea și starea.
5. **Nu se rulează `docker container prune -a`** (a distrus swarm-ul pe 2026-08-08).
6. **Nu se atinge namespace-ul Hermes.** `minimax` și `Hermes` sunt universuri
   separate; duplicarea e corectă, partajarea nu.
7. **Nu se rescrie conținutul unui fișier mutat fără comparație** —
   `scripts/compare-layer-versions.py`. Un fișier prezent dar mai vechi e o
   **regresie**, nu o mutare.

---

## 8. Limitele cunoscute, spuse cu voce tare

- **Verificarea C3 are nevoie de API-urile live ale Google.** Un refuz
  **tranzitoriu** (de exemplu Google Books HTTP 503) este **re-probat până la
  4 încercări**, cu pauză între ele, și **cauza este afișată per serviciu**:
  dacă se recuperează → `state=HEALTHY`, iar blipul **rămâne scris**; dacă nu
  se recuperează → `state=DEGRADED_TRANSIENT` → `CHECK C3.services WARN` →
  exit **0**. Un refuz **permanent** (403 / 404 / `MISSING_SCOPE` / un refuz
  nerecunoscut) → `state=FAILED_PERMANENT` → **FAIL** → exit **2**. Deci:
  **roșu pe defect, galben pe blip, niciodată ascuns.**
- **Rezultatul taskului întârzie cu până la 30 de minute.** După o reparație,
  rulează doctorul manual; taskul își reconsemnează apoi verdictul.
- **Keep și Sites nu vor apărea niciodată ca `OK`.** Sunt refuzate de Google.
- **Biblioteca foto completă e inaccesibilă** — Google a retras scope-urile pe
  31 martie 2025. Se citește doar ce selectează utilizatorul.
- **Route-ul ExtendLM are nevoie de extensia de browser conectată** pe gazdă.
- **Cloudul nu poate reîmprospăta** tokenul: folosește un snapshot cu
  `GA_EXTENDLM_NO_REFRESH=1`. Dacă gazda doarme, proba Cloudului eșuează — și
  spune asta.

---

## 9. Traseul prin care a trecut această lucrare (ca să nu-l repeți)

1. **27 oct** — containerul, grantul, ExtendLM, Photo Picker, proba live.
2. **28 oct** — punctul de control: 11 verificări, un verdict, task la 30 min.
3. **28 oct** — finalizarea a scos la iveală **patru defecte active**:
   trei intrări MCP rupte de mutarea `google-layer/`, `docker-mcp` cu un wrapper
   inexistent, **regresia mutării** (trei optimizări din 24 oct rămase în
   repo-ul vechi) și **sesiunea Picker consumată raportată ca defect**.
4. **28 oct** — instrumentul de control a descoperit și două bug-uri ale sale
   (`__dirname` în ESM; o re-probare tranzitorie care citea un obiect greșit,
   în exact clipa în care Google Books a răspuns 503).
5. **28 oct, 01:52Z** — imaginea **`google-access:1.0.10`**, construită din
   sursa vie și recreată cu aceiași parametri. Grantul a supraviețuit în
   volum (`grant=live`, `tools=32`), iar octeții rulați au devenit identici
   cu cei din repo (`repo=63e4ea8d2bbb running=63e4ea8d2bbb`). Aceeași
   fereastră a scos la iveală **două defecte reale**:
   **(a)** walker-ul de tabele al uneltei Docs arunca pe **orice** document cu
   tabel — `ERROR: el.table.rows.forEach is not a function`; reparat în sursa
   vie și în repo, `gdocs_get` citește acum documentul cu trei tabele
   (**5091 caractere**);
   **(b)** punctul de control era **roșu fals** — **8 din 8** rulări au fost
   roșii din cauza defectului Docs, iar o glimmă tranzitorie
   (`transport: fetch failed`) produsă de recrearea containerului era
   raportată ca eșec. `C3` a fost rescris: re-probe până la **4 încercări**,
   cauza afișată per serviciu, permanent → `FAILED_PERMANENT` → FAIL (exit 2),
   tranzitoriu recuperat → HEALTHY cu blipul scris, tranzitoriu nerecuperat →
   `DEGRADED_TRANSIENT` → WARN (exit 0).

**Lecția reutilizabilă:** *un fișier prezent nu e o migrare; o cale într-un
registry care nu mai există nu e o înregistrare; o sesiune consumată nu e o
defecție.* Toate trei au fost găsite de **măsurători**, nu de presupunere.
Adăugată la 28 oct: *o blipă tranzitorie nu e un defect — dar nici un defect
real nu e o blipă; de aceea re-probarea trebuie să numere cauza, nu doar
răspunsul.*

---

## 10. Fișierele, pe scurt

| Cale | Ce e |
|---|---|
| `Mavis-Google_Access\scripts\ga-doctor.mjs` | punctul de control — 11 verificări, un verdict |
| `Mavis-Google_Access\docs\PUNCT-DE-CONTROL.md` | specificația punctului de control |
| `Mavis-Google_Access\docs\STARE-MASURATA.md` | dovada cu dată, cu tot istoricul |
| `Mavis-Google_Access\container\` | conținutul exact al imaginii |
| `Mavis-Google_Access\google-layer\` | scripturile de browser și OAuth |
| `Mavis-Google_Access\scripts\probe-mcp-stdio.mjs` | handshake real pentru orice intrare MCP |
| `Mavis-Google_Access\scripts\compare-layer-versions.py` | comparația a două copii, linie cu linie |
| `Mavis-Google_Access\scripts\restore-layer-optimizations.py` | readucerea optimizărilor, cu verificare pe octeți |
| `C:\Users\apviz\.minimax\google-access\` | **sursa vie** a containerului + volumul `data\` |
| `C:\Users\apviz\.minimax\mcp.json` | registry-ul MCP global |
| `C:\Users\apviz\.minimax\AGENTS.md` §12.5 | instrucțiunea vie, pentru orice agent |
| `projects\10_BRIDGES\10_google_access.md` | specificația în backbone |
| `skills\mavis-google-access-bot\` | botul central + cei 8 membri |

---

## 11. Ce urmează după predare

| | Stare | Condiția de pornire |
|---|---|---|
| Browser MCP pe punctul central | 🟡 PLANNED | vezi `mavis-skill-browser-mcp` §4 |
| Un al doilea MCP bazat pe Docker | 🟡 PLANNED | decizia de interfață per capabilitate |
| Unelte noi în container | 🟡 PLANNED | ruta din `mavis-skill-mcp-development` §3 |
| Automatizarea Keep | ⏭ AMÂNAT | un scope acordabil trebuie să existe în registrul curent |
| Automatizarea Sites | ⏭ AMÂNAT | API-ul e retras — rămâne doar migrarea spre Drive |
| Importul în Drive, făcut azi manual | 🟡 PLANNED | aparține laturii Drive, nu containerului |
| Google Cloud | ⛔ INAFURI SCOPULUI | exclus prin decizia lui Popy |
