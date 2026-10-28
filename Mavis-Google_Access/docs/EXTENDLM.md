# EXTENDLM / NotebookLM prin MCP

NotebookLM nu are API Google public. Itinerariul real este **ExtendLM** - un
server MCP care expune funcțiile NotebookLM (notebooks, surse, note,
chat, căutare) printr-un flux OAuth cu dynamic client registration.

## Ce s-a măsurat (nu e documentație citită, e răspuns primit)

Metadata-ul serverului de autorizare
(`https://api.extendlm.com/.well-known/oauth-authorization-server`):

| Câmp | Valoare |
|---|---|
| `issuer` | `https://api.extendlm.com` |
| `authorization_endpoint` | `/rest/v1/mcp/oauth/authorize` |
| `token_endpoint` | `/rest/v1/mcp/oauth/token` |
| `revocation_endpoint` | `/rest/v1/mcp/oauth/revoke` |
| `registration_endpoint` | `/rest/v1/mcp/oauth/register` |
| `code_challenge_methods_supported` | `S256` |
| `token_endpoint_auth_methods_supported` | `none` (client public), `private_key_jwt` |
| `client_id_metadata_document_supported` | `true` |
| `scopes_supported` | 30 de valori (`notebooks:read`, `sources:read`, … `automations:write`) |

**Dynamic client registration + PKCE + client public** înseamnă că containerul
se înregistrează singur: **nu trebuie creat niciun client ID de mână** și nu
există niciun client secret care să se scurgă.

## Defect măsurat: `scope: "mcp"` este invalid

Prima încercare de înregistrare a fost respinsă:

```
POST /rest/v1/mcp/oauth/register  ->  400 {"error":"invalid_client_metadata"}
```

Cauza: corpul RFC 7591 trimis conținea `scope: "mcp"`, care nu e o valoare
din `scopes_supported`. Serverul acceptă corpul **fără** câmpul `scope` și își
asignează singur scope-ul (cele 30 de valori). Corecția e în
`container/extendlm-provision.mjs`: corpul nu mai conține `scope`, iar cererea
de autorizare cere **exact scope-ul întors de server**.

`scripts/extendlm-register-probe.mjs` probează 9 variante de metadata și
tipărește care e acceptată - pentru ca următoarea încercare să nu fie o
ghicitoare.

## Fluxul complet

```
node container/extendlm-provision.mjs --port 8799
  1. citește metadata-ul serverului
  2. se înregistrează dinamic (POST /register) -> client_id public
  3. generează PKCE (S256) + state
  4. tipărește AUTH_URL
  5. ascultă pe http://127.0.0.1:8799/callback
  6. schimbă codul (POST /token, code_verifier)
  7. scrie data/extendlm.json  { token, access_token, refresh_token, expires_at, client_id, ... }
```

Un singur pas rămâne al utilizatorului: **logarea pe extendlm.com și
autorizarea**. Restul (schimbul codului, scrierea tokenului) e automat.

## Tokenul

`data/extendlm.json` (volum montat, ca Google):

| Câmp | Folosire |
|---|---|
| `token` | token de acces, așa cum îl citește unealta `notebooklm_ask` |
| `refresh_token` | reînnoire la expirare (`grant_type=refresh_token`) |
| `expires_at` | momentul expirării, calculat din `expires_in` |
| `client_id` | clientul dinamic înregistrat |
| `token_endpoint` | pentru reînnoire |
| `mcp_url` | `https://mcp.extendlm.com/mcp` |

## De ce `notebooklm_ask` trebuie să apeleze unelte reale

O implementare care face doar `initialize` + `tools/list` **nu dovedește**
conexiunea: poate răspunde la fel și cu un token mort, pentru că listează
unelte fără să le execute. De aceea unealta trebuie să:
1. să mintă un token (prin refresh, dacă e expirat),
2. să deschidă sesiunea MCP,
3. să **apeleze** o unealtă reală și să întoarcă răspunsul ei.

Verificarea stă în `scripts/probe-token.mjs` și în probe-ul de servicii, care
raportează `NO_EXTENDLM_TOKEN` dacă fișierul lipsește.

### Implementat și măsurat (27 oct 2026, 12:35)
Exact acest defect a fost găsit în implementarea reală: unelta făcea
`initialize` + `tools/list` și **nu trimitea întrebarea** - returna lista de
unelte plus șirul întrebării. Reparația (în `container/server.mjs`) apelează,
în ordine, `list_notebook_users` -> `list_notebooks` -> `ask_notebook`, cu
formele măsurate ale răspunsurilor (`connections[].extension_connection`,
`items[].id`). Proba: `notebook_title=JULES`, `answer_chars=8139`,
`is_error=false`.

## Ce rămâne deschis (măsurat, nu presupus)

- **Corectat:** extensiile Chrome ExtendLM/NotebookLM **sunt conectate** -
  măsurat `extension_status.connected=true`, contul `apvizual@gmail.com`
  selectat, tier `NOTEBOOKLM_TIER_PRO_CONSUMER_USER`. Portul 9412 (profilul
  local `minimax-notebooklm`) e închis și **irrelevant**: extensia din
  Chrome-ul obișnuit al utilizatorului e cea care contează.
- **Corectat 27 oct 2026, 13:30-13:43**: reînnoirea automată **există și e
  măsurată**. `POST /token` cu `grant_type=refresh_token` rulează în container
  (`extendlmAccessToken()`, cu deviere de 120 s) și în
  `scripts/publish-extendlm-secret.mjs`. `data/extendlm.json` scade la
  **1164 B**, `token_len=87`, `refresh_token` prezent, `expires_at` +5 h de la
  ultima reînnoire. La expirare, `notebooklm_ask` **nu** răspunde 401: tokenul
  e reînnoit înainte de expirare. Detalii: „Stare măsurată 27 oct 2026,
  13:29-13:43" mai jos.
- **Real**: `notebooklm_ask` ia primul notebook vizibil dacă nu i se dă
  `notebook_id`; răspunsul întoarce `notebook_title`, ca alegerea să fie
  vizibilă, nu implicită.

## Stare măsurată 27 oct 2026, ~12:00

- Client dinamic înregistrat: `mcp_client_tJn6NvAfuMWEoT287NtRcyj72b7aI4sODEWMn9jD5UI`
  (public, fără secret; PKCE S256; 30 scope-uri returnate de server).
- Ascultător pe `127.0.0.1:8799`, redirect `http://127.0.0.1:8799/callback`.
- Fereastra de așteptare: **180 min** (era 60 - un răspuns uman se pierdea).
- `data/extendlm.json`: **ABSENT**. `notebooklm_ask` răspunde `NO_EXTENDLM_TOKEN`
  - verdict corect, nu tăcere.
- Ce lipsește e un singur lucru, de la om: autentificarea pe `extendlm.com`
  („Continue with Google") și autorizarea aplicației. Restul - schimbul codului,
  scrierea tokenului în volum, repornirea containerului - e automat.

## Stare măsurată 27 oct 2026, 12:29-12:40 - NotebookLM LIVE

**Loginul și autorizarea sunt două lucruri diferite.** Măsurat: la 12:29
`data/extendlm.json` era absent, deși Popy se autentificase; procesul
ascultător (node `extendlm-provision.mjs --port 8799`, pornit 11:37:14) era
**viu** - `LISTENING pid=55620`. Diferența: loginul de pe `extendlm.com` îți
duce la ecranul de consimțământ; doar acolo se generează `code`-ul pe care
ascultătorul îl schimbă în token. Am deschis URL-ul de autorizare cu
`code_challenge` + `state` legate de procesul viu, iar consimțământul a fost
dat.

| Măsurătoare | Valoare |
|---|---|
| callback | `http://127.0.0.1:8799/callback?code=…&state=…` - `state` **identic** cu cel ținut de proces (valoarea nu se publică: nonce de CSRF, consumat) |
| `data/extendlm.json` | **1118 B**, scris 12:33:24 - `token_len=87`, `refresh_token` prezent, `scope` 436 caractere |
| `expires_at` | +3 h de la obținere |
| portul 8799 după schimb | **închis** (`server.close()`) - comportament corect |
| `TOOL_COUNT` | **160** unelte |
| `extension_status.connected` | **true** |
| contul selectat | `apvizual@gmail.com`, `auth_user_id=0`, `is_selected=true` |
| tier | `NOTEBOOKLM_TIER_PRO_CONSUMER_USER` (`notebook_limit=500`, `source_limit=300`) |

**Leție de măsurare:** taskul de fundal a fost raportat `status=lost`, dar
procesul node a supraviețuit. *Task pierdut* ≠ *proces mort* - verificarea s-a
făcut pe obiect (port + PID + command line), nu pe raportul tracker-ului.

**Defect reparat în aceeași zi:** `notebooklm_ask` răspundea `HTTP=200` fără să
întrebe nimic (făcea doar `initialize` + `tools/list`). Reparația, la sursă:
`list_notebook_users` -> `list_notebooks` -> `ask_notebook`, cu formele
măsurate (`connections[].extension_connection`, `items[].id`).
Proba: `notebook_title=JULES`, `answer_chars=8139`, `is_error=false`.

**Sonda permanentă:** `scripts/probe-notebooklm.mjs` - numără uneltele, citește
starea extensiei și a contului, tipărește *nume* de unelte (niciodată tokenul),
și poate cere schema unei unelte (`--schema ask_notebook,list_notebooks`).

## Stare măsurată 27 oct 2026, 13:29-13:43 - rotația, singurul proprietar, heartbeat

**Endpoint-ul rotește refresh token-ul.** Măsurat: `rotated_refresh=true` la
`POST /token` cu `grant_type=refresh_token`. Două instanțe care se reînnoiesc
din aceeași copie se distrug: a doua rotație invalidează tokenul pe care prima
l-a scris. Deci rotația are **un singur proprietar**, iar ceilalți consumă
copii.

| Rol | Instanță | Comportament |
|---|---|---|
| **proprietar** | hostul (`Google_Access` + `publish-extendlm-secret.mjs`) | rotește, persistă atomic (`tmp` + `rename`), publică snapshotul |
| **consumator** | runnerul Cloud (`MAVIS-CLOUD`) | `GA_EXTENDLM_NO_REFRESH=1` - **nu** rotează, folosește snapshotul |

Cu `GA_EXTENDLM_NO_REFRESH=1`, o instanță al cărei token a expirat **spune
exact asta** (`EXTENDLM_TOKEN_EXPIRED_NO_REFRESH: … the owner instance has to
publish a fresh snapshot`) în loc să se zbate cu o rotație care ar strica
copia gazdei.

### Rotația măsurată

| Măsurătoare | Valoare |
|---|---|
| `REFRESH_HTTP` | 200 |
| `TOKEN_LEN` | 87 |
| `ROTATED_REFRESH` | **1** (deci persistența e obligatorie) |
| `expires_in` | 17999 s |
| fișier | `data/extendlm.json`, **1164 B**, `token_len=87`, `refresh_len=87` |
| `TOOL_COUNT` după reînnoire | 160 |
| verdict | `REFRESH_WORKS` |

`refreshExtendlmToken()` scrie fișierul **atomic** (`tmp` + `rename`), iar
`readExtendlmConfig()` citește de pe disc la fiecare apel - deci o instanță
preia imediat tokenul scris de alta, fără restart.

### Mecanismul permanent

`scripts/publish-extendlm-secret.mjs` - rotește **doar când e nevoie** (token
valid cu >60 min → nu rotește), publică snapshotul în secretul Cloud și
**citește înapoi** timestamp-ul secretului (`SECRET_READBACK=present`,
`age_seconds=14`): o scriere neconfirmată nu e o scriere.

`scripts/extendlm-heartbeat.ps1` - rulează publicatorul, scrie **o linie datată**
în `logs/extendlm-heartbeat-YYYY-MM-DD.log` (UTF-8 fără BOM) și propagă exit
code-ul.

Taskul Windows **`MavisExtendLMHeartbeat`** (repetiție 30 min) - măsurat
declanșat de planificator: `LAST_RUN=13:43:14`, `LAST_RESULT=0`,
`NEXT_RUN=14:13:14`, log +1 linie `EXIT=0`.

Falsificare (poarta trebuie să poată eșua): repo inexistent → `EXIT=2`;
director de date inexistent → `EXIT=3`.

**Redacție:** logul nu primește niciodată tokenul. `gh` ecolează linia de
comandă la eșec, iar linia conține `--body <snapshot>`; publicatorul redactă
payload-ul (`[REDACTED_SNAPSHOT]`), iar wrapper-ul aplică o plasă suplimentară
(`[A-Za-z0-9+/=]{80,}` → `[REDACTED_B64]`).

### Cloud

Run `40497337673` (concluzie **success**): `SOURCE_COMMIT=f589f82`,
`EXTENDLM_FIELDS=…token_len=87…refresh=yes`, `SERVICE=notebooklm STATUS=OK`,
`VERDICT=PASS`, `PROBE_EXIT=0`. Secretul Cloud: `GOOGLE_EXTENDLM_CREDENTIAL_B64`.

## Al doilea drum spre NotebookLM - serverul de browser

Drumul de mai sus e proxy-ul ExtendLM din container. Există și un drum
independent prin browser, cu profil Chrome propriu (nu token, ci sesiune).

**DEFECT MĂSURAT 27 oct 2026:** serverul `minimax-notebooklm` era înregistrat și
activ în profilul MCP, dar cu o cale care nu există
(`projects\google-layer\…`, folder absent) - deci nu pornea deloc. Corecția
calei + proba: `scripts/probe-minimax-notebooklm.mjs` →
`INITIALIZE_OK=1` (minimax-notebooklm 1.0.0), `TOOL_COUNT=4`
(`nblm_health`, `nblm_list_notebooks`, `nblm_get_sources`, `nblm_ask`),
`nblm_health` → `authenticated=true`, `notebook_list=true`, `circuit=closed`, iar
`nblm_list_notebooks` a întors notebook-urile reale (`JULES` 182 surse,
`GEMINI & AI Studio` 251, `CV-Automation` 98, `AGENTS` 8, `TRADE` 1,
`CV-Notebook` 99, `SENTINEL Role` 225, `OPTIMUS System` 5, `CLIENTS` 2).

Chrome pornește de server, la nevoie, pe `127.0.0.1:9412`, cu profilul
`%LOCALAPPDATA%\minimax-notebooklm\chrome_profile`. Serverul are circuit breaker
pentru sesiunea neautentificată: răspunde din ultima stare cunoscută, fără să
atingă rețeaua, și lasă o singură sondă pe cooldown.



