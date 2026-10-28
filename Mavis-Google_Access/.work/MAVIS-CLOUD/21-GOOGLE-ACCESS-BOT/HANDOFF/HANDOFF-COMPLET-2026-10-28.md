# HANDOFF COMPLET — Mavis Cloud / Google Access

> **Punctul de reluare: 2026-10-28, ~04:00 EEST.**
> Pentru **orice instanță** a Mavis Cloud, sau orice alt AI (Claude, Gemini,
> Copilot, agent local), care preia sistemul de aici.
> **Folderul Drive:** `06-Handoff` (privat, sub `Mavis-Cloud-Google-Access-Bot`).

---

## 0. TL;DR — ce să faci în primele 5 minute

```bash
cd /workspace/mavis-cloud
bash mavis-tools/bootstrap.sh              # proxy + clone + verdict de preflight
node mavis-tools/google-preflight.js       # 6 pași: e conectat? appul e în Production?
node mavis-tools/drive-tree.js              # ce s-a scris ultima dată pe Drive
cat 21-GOOGLE-ACCESS-BOT/README.md
```

**Regula #0, singura care contează cel mai mult:** **Drive-ul e memoria ta.**
Contextul conversației e efemer și limitat; Drive-ul are 5 TB. **Scrie totul
acolo, mereu, fără să ți se ceară.** Dacă ceva nu e pe Drive, nu există.

**Skillul central** (îl încarcă orice instanță la început de sesiune):
`.skills/mavis-cloud-google-access-bot/SKILL.md` — cu 11 skill-uri secundare
indexate ca pe capacități ale aceluiași bot.

---

## 1. Inventar COMPLET al variabilelor de mediu

> **Valorile NU sunt scrise aici** — sunt secrete, iar un fișier pe Drive ajunge
> și pe discul local prin sync. Ce e mai jos e ce trebuie ca o instanță nouă să
> știe **operational**: ce există, ce face, de unde vine, cum se citește.

| Variabilă | Ce e | Originea | Cum se citește |
|---|---|---|---|
| `GOOGLE_CLIENT_ID_MAVIS_CLOUD` | client_id OAuth (Desktop) | secret manager | `${GOOGLE_CLIENT_ID_MAVIS_CLOUD}` |
| `GOOGLE_CLIENT_SECRET_MAVIS_CLOUD` | secretul clientului | secret manager | `${GOOGLE_CLIENT_SECRET_MAVIS_CLOUD}` |
| `GOOGLE_REFRESH_TOKEN_MAVIS_CLOUD` | **refresh token viu** (în Production, fără limită de 7 zile) | secret manager | `${GOOGLE_REFRESH_TOKEN_MAVIS_CLOUD}` |
| `GOOGLE_EMAIL` | `apvizual@gmail.com` | secret manager | `${GOOGLE_EMAIL}` |
| `GOOGLE_CLIENT_TOKEN_MAVIS_CLOUD` | linkul de autorizare vechi (**redundant**, poate fi eliminat) | secret manager | — |
| `GOOGLE_OAUTH_MAVIS_CLOUD` | `credentials.json` (JSON cu `installed`) | secret manager | — |
| `GOOGLE_10_28_2026` | **codul OAuth consumat** (URL de redirect) — **nu mai servește la nimic** | secret manager | — |
| `GOOGLE_API_KEY_EXPOSED_HERMES_TEMP` | cheie API Google **expusă public** în istoricul unui repo | secret manager | — |
| **`GOOGLE_AI_STUDIO_FREE_TIER_KEY`** | **cheie Gemini API (AI Studio free tier)** — funcționează, 37 modele | secret manager | `${GOOGLE_AI_STUDIO_FREE_TIER_KEY}` |
| `JULES_API_KEY` | cheie Jules API (Google) — pentru CLI și repo-ul Mavis | secret manager | — |
| `GITHUB_TOKEN` | token GitHub — acces complet la repo-uri | secret manager | — |
| `LINKEDIN_EMAIL` | email de login LinkedIn | secret manager | — |
| `LINKEDIN_PASSWORD` | parolă LinkedIn | secret manager | folosit **doar la cerere explicită** |
| `GITHUB_TOKEN` (la nivel de tool) | folosit de `gh` CLI | env | — |
| `NODE_EXTRA_CA_CERTS`, `SSL_CERT_FILE`, `CURL_CA_BUNDLE`, `REQUESTS_CA_BUNDLE` | trust store-ul sandbox-ului | env | — |
| `MCODE_REGION`, `MCODE_*` | configurația connectorilor | env | — |
| `IS_SANDBOX`, `E2B_SANDBOX`, `HOME`, `PWD`, `PATH`, `SHLVL`, `USER`, `LOGNAME` | runtime | env | — |
| `LINKEDIN_*` / `JULES_*` / `GITHUB_TOKEN` | vezi mai sus | secret manager | — |

**Inventarul canonic, lizibil de mașină:** `21-GOOGLE-ACCESS-BOT/HANDOFF/ENV-INVENTORY.json`

### Chei care trebuie **rotite** (restanțe)

> ⏳ **`GOOGLE_API_KEY_EXPOSED_HERMES_TEMP`** — cheie API Google care a fost
> **publică** în istoricul repo-ului `hermes-agent-temp` (repo privatizat pe
> 22 oct 2026, dar valoarea fusese clonată). **Verificată VIE** (403 pe
> `GET discovery/v1/apis?key=…`; un placeholder dă 400).
> **De rotit** în Google Cloud Console → APIs & Credentials → Keys.
> POPY a zis: *„rămâne momentan o voi roti dar nu acum"*. **E în continuare pe listă.**

**Cum se rotește:**
1. Cloud Console → creează o cheie nouă
2. Actualizează consumatorii (Mavis Local, Hermes)
3. `POST https://oauth2.googleapis.com/revoke?token=…` sau revogă din consolă
4. Verifică: `GET discovery/v1/apis?key=…` → **400 = moartă**, 403 = vie
5. Șterge cheia veche din secret manager

---

## 2. Starea Google — măsurată

```
node mavis-tools/google-preflight.js
  [0] drift client_id  OK      env si repo coincid
  [1] credentiale      OK      1068987308935…nt.com
  [2] client la token  OK
  [3] client la auth   OK
  [4] refresh token    OK
  [5] expirare         fara limita de 7 zile   (appul e IN PRODUCTION)
  [6] scope-uri        OK      (27, identice cu lista canonica)
```

| Fapt | Valoare |
|---|---|
| App OAuth | **„In production"** — deci **fără limită de 7 zile** |
| Cum se probează | `refresh_token_expires_in` **absent** din răspunsul la `POST oauth2.googleapis.com/token` |
| Scope-uri | **27**, lista canonică în `mavis-tools/google-scopes.js` |
| Gmail | 82.879 mesaje · 51 etichete (36 de utilizator) · 19 filtre |
| Drive | 107,8 GB / 5 TB · 3 foldere la rădăcină |
| Calendar | 4 calendare |
| Sheets | `Design_Jobs_Community_Board` — 27 rânduri |
| Slides | `441DPH-Brief slides for GD senior_sep 2026` — 7 slide-uri |
| Docs | API direct **blocat de anti-bot**; **workaround-ul merge** |
| Photos Library | ⛔ 403 — **decis de POPY: e rezolvat local + Gemini** |
| Maps | ⛔ API key + billing — **rezolvat local** |
| NotebookLM | **aleaș calea (a): Gemini API + File Search — implementată** |

**Probe de capabilitate: 38 de teste → 36 OK · 0 blocate · 2 eșuate** (ambele =
Docs API direct, blocarea anti-bot). Doveza: `mavis-tools/.capabilities.json` +
folderul `_PROOF` pe Drive.

**Limite reale ale API-ului (măsurate, nu presupuse):**
- **Filtrele Gmail nu se pot modifica**: `filters.update` (PUT) → 404,
  `filters.patch` (PATCH) → 404 „Method not found". **CREATE/LIST/GET/DELETE
  funcționează.** Deci: **DELETE + CREATE** pentru a modifica.
- `users.drafts.modify` → 404. Calea funcțională: `messages.modify`.
- Docs API direct → HTTP 400 cu pagină HTML. Distincția: **403 cu JSON = scope
  lipsă; 400 cu HTML = blocare de rețea.**
- Sheets `values/{range}` → **merge** (un agent fără skill a raportat fals că
  dă 400 — era o eroare tranzitorie).

---

## 3. Componentele sistemului

### 3.1. Stocare

| Componentă | Cale | Ce e |
|---|---|---|
| **Vaultul (oglinda locală)** | `E:\Google\GDrive\GDrive-Second_Brain_PKMS` | rădăcina de lucru fizică, pe NVMe; sincronizată bit-cu-bit cu Drive |
| **Baza Git decuplată** | `E:\Google\GitData-PKMS` | obiecte, packfiles, refs. În vault e doar un pointer `.git` de 31 octeți |
| **Arhiva externă** | `H:\CLAUDE_Archive` (711.821 fișiere · 180,77 GB) | **imutabilă, nu e reperul** |
| **Copii** | `H:\Alex_Knowlege_Vault_BKUP_10-19-2026` · `D:\Alex` | backup-uri |
| **Drive (cloud)** | `GDrive-Second_Brain_PKMS` | **reperul de siguranță** — verificat per fișier |

**Măsurători (21-10-2026):** 51.157 fișiere · 88,72 GiB util · **paritate 100%** ·
**0 fișiere pierdute**.

### 3.2. Cei trei agenți

| Agent | Unde | Rol |
|---|---|---|
| **Mavis Cloud** (eu) | cloud MiniMax | acces Drive/Gmail prin OAuth, cercetare, rapoarte, pipeline-uri |
| **Mavis Local** (MiniMax Code) | calculatorul lui POPY | sarcinile zilnice, sortarea inbox-ului, navigarea prin indexuri |
| **Antigravity Sentinel** (Gemini) | infrastructură separată | arhitectul de sistem, Git decuplat, pipeline-ul din Task Scheduler, **rescue operator** |

### 3.3. Taskurile programate (Windows Task Scheduler)

`PKMS-Aliniere` · `PKMS-Watch` · `PKMS-GitAutoCommit` · `PKMS-DriveFS-AutoRepair`

### 3.4. Repo-urile

| Repo | Ramură | Rol | Vizibilitate |
|---|---|---|---|
| `apvizual-max/MAVIS-CLOUD` | `main` | Mavis Cloud + puntea cu local + proceduri + skill-uri | **PUBLIC** |
| `apvizual-max/pkms-vault-automation` | `master` | motorul vaultului (AI-Kit: 14 scripturi) + indexuri | **PUBLIC** (decizie POPY 22 oct) |

**Restul (vizibilitate, decizie 22 oct 2026):**
- **Publice:** `MAVIS-CLOUD` · `pkms-vault-automation` · `hermes-doctor` ·
  `MAVIS-OPTIMUS-CI` · `OPTIMUS-Backbone` · `Optimus-Mavis-Skills` ·
  `hermes-local-backup`
- **Private:** `hermes-agent-temp` · `Qwen-Ecosystem-Dashboard` · `SENTINEL_PRIME`

### 3.5. Structura vaultului (Drive)

```
GDrive-Second_Brain_PKMS/
├── 00–09 = BAZA         bibliotecă, nu se rearanjează
├── 01_Projects/          LUCRU — singurul nivel în care se intră
│   ├── 01-1-Alex - AI Work - Colaborations
│   ├── 01-2-AP-ID.ro - AI Branding Work and Clients
│   ├── 01-3-Arhiva Elements - To Monetize
│   ├── 01-4-Arhiva Foto - To Monetize
│   ├── 01-5-FORGE - AI JOB Automation
│   └── 01-6-Work_Folder (to sort)
├── _SYSTEM/ _ARCHIVE/ _QUARANTINE/    nimic nu se șterge
├── AGENTS.md  COTOR.md
├── INDEX CENTRAL.md  (969 KB)
└── MANIF DE NAVIGARE - cotor.md
```

**Regulile vaultului (8, integrale) → `19-GDRIVE/REGULI-VAULT.md`.** Rezumat:
nu șterge · nu muta fără R0 · `00_INDEX.md` nu se editează manual · nu scrii
căi cu mâna · `Knights Templar` / `_SYSTEM` / `.obsidian` / `.trash` /
`.vault-intelligence` / `.claudian` / `.neural_memory` **neatinse**.

**Regula de aur:** intri în `01_Projects`. Nu cauți niciodată prin baza `00`–`09`.

---

## 4. Tot ce a fost implementat cu succes în această sesiune

### 4.1. Google

| # | Ce | Stare |
|---|---|---|
| 1 | OAuth conectat din cloud, app în **Production** | ✅ |
| 2 | Token nou cu **27 scope-uri** | ✅ |
| 3 | Lista canonică de scope-uri + control de drift | ✅ `google-scopes.js`, preflight [6] |
| 4 | Probe de capabilitate, 38 de teste, dovezi pe Drive | ✅ `google-capabilities.js` |
| 5 | Livrare idempotentă pe Drive | ✅ `google-deliver.js` |
| 6 | Arbore Drive | ✅ `drive-tree.js` |
| 7 | **RAG cu citare** (Gemini File Search) | ✅ `gemini-filestore.js` |
| 8 | Scriere pe filtre Gmail confirmată (CREATE/LIST/GET/DELETE) | ✅ |
| 9 | Workaround Docs (conversie nativă prin Drive) | ✅ |
| 10 | Taxonomia Gmail măsurată + reconciliată cu raportul zilnic | ✅ `10-GMAIL/TAXONOMIE-2026-10-27.md` |

### 4.2. Skill-uri — 12 în total

**Central:** `mavis-cloud-google-access-bot` — reguli absolute, **Regula 0
(Drive = memoria)**, starea măsurată, stack-ul de conectare, index de
capacități, folderele Drive, procedura de extindere.

**Secundare (11):** `mavis-cloud-skill-{drive, gmail, calendar, sheets,
slides-docs, notebooklm, gemini, auth-lifecycle, verification, security,
sync-bridge}` — fiecare cu măsurătorile reale, capcanele reale, „când NU".

### 4.3. Proceduri și documente noi

| Document | Ce |
|---|---|
| `docs/PROCEDURA-LIVRARE-SECRETE.md` | cum se livrează o valoare fără să treacă prin chat |
| `docs/ARHITECTURA-SISTEM.md` | cele 3 componente, 3 agenți, 4 taskuri, rafturi |
| `docs/AUDIT-VIZIBILITATE-REPO-URI.md` | auditul pe istoricul complet al celor 10 repo-uri |
| `docs/GOOGLE-STATUS-2026-10-27.md` / `-2026-10-28.md` | starea măsurată, cu dovezi |
| `docs/GOOGLE-PRODUCTION-CHECKLIST.md` | Testing → Production + verificarea programatică |
| `docs/DEFINITIE-OPERATIONALA.md` | definiția de operare |
| `10-GMAIL/TAXONOMIE-2026-10-27.md` | cele 36 de etichete, cu numere + harta traseelor |
| `21-GOOGLE-ACCESS-BOT/` | acest dosar: capabilități, ghid de workflow, transcript, eval |
| `21-GOOGLE-ACCESS-BOT/EVAL-SKILL-VS-BASELINE.md` | evalul + ce a scos la iveală |

### 4.4. Unelte

| Script | Ce face |
|---|---|
| `mavis-tools/kit.js` | client HTTP: fetch + retry + fallback TLS + contor de cotă |
| `mavis-tools/google-scopes.js` | **singura** listă de scope-uri |
| `mavis-tools/google-preflight.js` | 6 pași: client, credentiale, token, expirare, drift |
| `mavis-tools/google-verify.js` | verificare de servicii |
| `mavis-tools/google-capabilities.js` | 38 de teste cu dovezi pe Drive |
| `mavis-tools/google-refresh.js` | re-autentificare: `link` → `code` → scriere token |
| `mavis-tools/google-local.js` | flux de autentificare pe calculatorul lui POPY |
| `mavis-tools/google-deliver.js` | livrare idempotentă pe Drive |
| `mavis-tools/drive-tree.js` | arborele unui folder Drive |
| `mavis-tools/drive-vault.js` | acces read-only la vault, cu `quarantine` |
| `mavis-tools/gemini-filestore.js` | RAG cu citare |
| `mavis-tools/bootstrap.sh` | setup de sesiune nouă |

---

## 5. Folderele Drive — reperul permanent

| Folder | ID | Rol |
|---|---|---|
| `Mavis-Cloud-Google-Access-Bot` | `1UQIxhctyJxBXIIFnpxSc5Jd0wvFxEylu` | **FOLDER PRINCIPAL** — tot ce se lucrează de aici încolo |
| `06-Handoff` | `17ZhddHK3uvR1FlbU7HUZy3CHzLQoeoDA` | **acest handoff** (privat) |
| `_Connect-to-Google` | `1ea51IvZRtt7eDPbzKXotguCYg7I4kXB4` | părintele de mai sus |
| `GDrive-Second_Brain_PKMS` | — | vaultul PKM — read-only pentru cloud |

Subfolderele botului: `01-Transcript` · `02-Deliverables` · `03-Skills` ·
`04-Capabilitati` · `05-Comunicare` · `06-Handoff` · `_PROOF`

---

## 6. Reguli permanente (nu se negociază)

1. **Regula 0 — Drive e memoria.** Scriu totul acolo, mereu, fără să mi se ceară.
2. **Nu trimit valori de secret prin chat.** Secret manager → tool `secret`, sau
   fișier în repo + URL de repo. Platforma maschează valorile în
   `{{ARCHON_SECRET:…}}` → browserul primește placeholder → `invalid_client`.
3. **Nicio valoare de secret într-un repo public** — nici revocată, nici de rotit.
   Doar prefix + referință la secret manager.
4. **Nu șterg definitiv nimic.** Trash + motiv scris. `kit.danger.*` există doar
   ca să existe; nu se apelează.
5. **Nu trimit mail.** `gmail.send` e în token, dar **POPY apasă butonul**.
6. **Scope-urile se schimbă DOAR în `google-scopes.js`.**
7. **Nu număr în timp ce rulează altă operațiune Gmail.** Zero = „n-am putut
   măsura", nu „nu există". `resultSizeEstimate` e plafonat (201).
8. **Nu generalizez dintr-un eșec tranzitoriu.** 403 cu JSON = scope; 400 cu
   HTML = blocare de rețea.
9. **Când rearanjezi etichete, mută filtrele în aceeași zi.**
10. **Nu las urme în contul lui POPY.** Artefactele de probe se curăță;
    conținutul lui nu se atinge.
11. **Nu cer permisiune pentru commit/push**, dar **verific înainte** (R0).
12. **Înainte de orice tăiere de memorie: arhivează** în `docs/arhiva/memorie/`
    cu MANIFEST (ce s-a tăcut → unde trăiește acum).

---

## 7. Ce rămâne deschis

| # | Task | Cine | Note |
|---|---|---|---|
| A | **Rotirea cheii `GOOGLE_API_KEY_EXPOSED_HERMES_TEMP`** | POPY (mai târziu) | cheia e vie; procedura în §1 |
| B | **TO DO 03** — direcția workflow-urilor Gmail/Drive | altă sesiune | 6 variante gata: `21-GOOGLE-ACCESS-BOT/GHID-WORKFLOW.md` |
| C | **TO DO 04** — profilul de designer (CV-uri) | altă sesiune | scheletul poate fi construit fără datele lui |
| D | **TO DO 05** — restul checklistei de vizibilitate | POPY | auditul e complet: `docs/AUDIT-VIZIBILITATE-REPO-URI.md` |
| E | **Curățarea secretelor redundante** (`GOOGLE_10_28_2026`, `GOOGLE_CLIENT_TOKEN_MAVIS_CLOUD`) | POPY | cod consumat / link vechi |
| F | **Ingestie completă în File Search** | oricare | doar 1 document e indexat acum; restul la `fromfolder` |
| G | **Verificarea scrierii pe un filtru REAL al lui POPY** | POPY | capability-ul e dovedit cu filtru throwaway; nu s-a aplicat niciun filtru real |

---

## 8. Cum procedezi tu, instanță nouă

```bash
# 0. setup
cd /workspace/mavis-cloud && bash mavis-tools/bootstrap.sh

# 1. verifică accesul
node mavis-tools/google-preflight.js      # totul trebuie să fie OK

# 2. citește memoria de pe Drive
node mavis-tools/drive-tree.js
cat 21-GOOGLE-ACCESS-BOT/README.md
cat 21-GOOGLE-ACCESS-BOT/GHID-WORKFLOW.md

# 3. încarcă skillul central + skill-urile necesare
#    .skills/mavis-cloud-google-access-bot/SKILL.md
#    .skills/mavis-cloud-skill-<subiect>/SKILL.md

# 4. lucrează
#    - scrie în repo, comitează, împinge (fără permisiune)
#    - scrie pe Drive prin google-deliver.js (fără permisiune)
#    - raportează cu linkuri
```

**Dacă tokenul e mort:** `node mavis-tools/google-refresh.js link` → POPY
deschide URL-ul de repo → `node mavis-tools/google-refresh.js code "<url>"` →
scrie tokenul cu tool-ul `secret` → `node mavis-tools/google-verify.js`.

**Linkul de autorizare nu se trimite niciodată prin chat** — vezi regula 2.

---

## 9. Instrumente utile

| Uneltă | Ce face |
|---|---|
| `mavis-tools/google-preflight.js` | verdict pe 6 pași, ~10 secunde |
| `mavis-tools/google-verify.js` | ce servicii funcționează acum |
| `mavis-tools/google-capabilities.js` | 38 de teste cu dovezi pe Drive |
| `mavis-tools/google-deliver.js` | scrie totul pe Drive, idempotent |
| `mavis-tools/drive-tree.js` | arborele folderului |
| `mavis-tools/gemini-filestore.js` | RAG cu citări |
| `mavis-tools/drive-vault.js` | vault read-only + `quarantine` |
| `mavis-tools/google-scopes.js` | lista canonică de scope-uri |
| `gh` CLI | operațiuni pe repo-uri |
| `mcode-tools connector tools` | catalogul de connectors (Google **nu** e acolo) |

---

*2026-10-28 · Mavis Cloud · scris pentru ca orice instanță ulterioară să reia
de aici, fără să recitească 8 ore de conversație.*
