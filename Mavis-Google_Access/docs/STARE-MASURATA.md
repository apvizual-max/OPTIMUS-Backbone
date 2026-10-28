# STARE MASURATA - Google_Access (27 octombrie 2026)

Tot ce mai jos este **măsurat**, nu declarat. Fiecare afirmație are o probă
repetabilă în `scripts/` sau în `container/`.

## 1. Containerul

| | |
|---|---|
| Nume | `Google_Access` |
| Imagine | `google-access:1.0.5` (build 2026-10-27 08:58 UTC) |
| Stare | `running` · `healthy` · `FailingStreak=0` |
| MCP | `http://127.0.0.1:8766/mcp` (Streamable HTTP, JSON-RPC 2.0, **stateless**) |
| Health | `GET http://127.0.0.1:8766/health` → `{"service":"Google_Access","grant":"live","reauth_required":false,"tools":26}` |
| Volum credential | `C:\Users\apviz\.minimax\google-access\data` → `/data` (rw) |
| Volum secrete | `E:\--- System Secrets` → `/secrets` (ro) |
| Secret în imagine | **nu** - `.dockerignore` exclude `data/` |

## 2. Grantul

| | |
|---|---|
| Cont | `apvizual@gmail.com` |
| Client | `Sentinel Hermes CLI` (Desktop) - `1068987308935-5b7h17gt…apps.googleusercontent.com` |
| Proiect | `gen-lang-client-0284509562` ("Sentinel Prime") |
| Scope-uri cerute | 30 |
| Scope-uri efectiv pe token | 30 (măsurat la `oauth2.googleapis.com/tokeninfo`) |
| Status publicare | **In production** (era *Testing* - vezi §5) |
| Verificare | **neefectuată** - aplicația cere verificare pentru distribuție publică (restricționat/sensitive scopes + logo) |
| API-uri activate | `books.googleapis.com` și `chat.googleapis.com` au fost activate de mine pe 27 oct (nu erau active) |

## 3. Proba reală pe fiecare serviciu

`node container/probe-services.mjs` - apelează fiecare unealtă și clasifică
**răspunsul**, nu cererea.

| Serviciu | Unealtă | Rezultat | Doi |
|---|---|---|---|
| Identity | `google_auth_status` | OK | `grant_live=true` |
| Drive | `gdrive_list` | OK | fișiere reale |
| Gmail | `gmail_list` | OK | mesaje reale |
| Calendar | `gcalendar_list` | OK | evenimente reale |
| Books | `gbooks_search` | OK | volume reale |
| Tasks | `gtasks_list` | OK | 1 listă |
| Contacts | `gcontacts_list` | OK | 5 contacte |
| Docs | `gdocs_get` | OK | document real |
| Sheets | `gsheets_read` | OK | foaie reală |
| Apps Script | `gscript_list` | OK | 1 proiect (listat prin Drive) |
| YouTube | `youtube_my_videos` | OK | canal real |
| Photos | `gphotos_list` | **refuz măsurat** | `403 insufficient authentication scopes` ( vezi §4) |
| Chat | `gchat_spaces` | **refuz măsurat** | `403 ACCESS_TOKEN_SCOPE_INSUFFICIENT` → reparat prin `chat.spaces.readonly` (vezi §4) |
| Keep | `gkeep_list` | **refuz măsurat** | Google nu publică scope de utilizator pentru Keep API |
| Sites | `gsites_list` | **refuz măsurat** | API-ul Google Sites a fost retras |
| NotebookLM | `notebooklm_ask` | dependent de ExtendLM | token la `data/extendlm.json` |

`REFUSED` este un răspuns **măsurat** al API-ului, nu o eroare. Probe-ul
distinge: `OK` (date) · `REFUSED` (API-ul a refuzat, cu codul lui) · `ERROR`
(n-a răspuns) · `SKIP` (nu există obiect de probat).

## 4. Ce a refuzat Google și de ce (măsurat, nu presupus)

| Scope cerut | Verdict Google | Sursa verificării |
|---|---|---|
| `auth/sites` | **invalid** - „not added because they are invalid" | consola + directorul oficial de API-uri: `sites.googleapis.com` nu mai există (doar `siteverification`) |
| `auth/keep` | **invalid** - aceeași eroare | `keep.googleapis.com` e activ, dar scope-ul nu e în registrul public de scope-uri Google (Keep API e doar pentru admini de workspace) |
| `auth/chat.messages` pentru `chat.spaces.list` | **insuficient** | discovery doc: `spaces.list` cere `chat.bot` / `chat.spaces` / `chat.spaces.readonly` |
| `auth/photoslibrary.readonly` pentru `/v1/mediaItems` | **insuficient** | API-ul a refuzat chiar cu scope-ul prezent pe token → s-a cerut și scope-ul complet `photoslibrary` |

**De ce a contat:** o cerere de consimțământ cu UN scope invalid este respinsă
în întregime (`invalid_scope`, „Some requested scopes cannot be shown"). Deci
două scope-uri moarte blocau și celelalte 28.

## 5. Permanentizarea (măsurat)

- **27 oct, 08:35** - consimțământul a fost acordat cu aplicația în statut
  **Testing**. În acest statut, token-urile de refresh pentru scope-uri
  sensibile/restricționate expiră în **7 zile** (expirare ~3 noiembrie).
- **27 oct, 08:50** - Branding completat (nume aplicație „Sentinel Hermes
  Google Access", email suport, pagină principală, linkuri Privacy/Terms,
  domeniu autorizat `github.com`) și aplicația **publicată**: pagina Audience
  arată acum „Publishing status: In production".
- **27 oct, ~09:00** - al doilea consimțământ, cu 30 scope-uri, emis **după**
  publicare → tokenul de refresh nu mai are expirarea de 7 zile.

Condiția rămâne: dacă revoca accesul din contul Google, sau dacă Google îl
invalidază, apare `GOOGLE_HTTP_401` / `invalid_grant`. Containerul raportează
asta explicit prin `google_auth_status` (`reauth_required`), nu tace.

## 6. Limite reale, spuse fără cosmetizare

1. **Keep** și **Sites** nu sunt accesibile prin API cu un token de utilizator.
   Google nu mai publică scope-uri valide pentru ele. Uneltele există și
   raportează refuzul real, ca să nu pară că funcționează.
2. **WebMCP** (`webmcp.dev`) este o capabilitate de **browser**, nu de
   container. Nu poate fi „pusă în Docker" ca atare. Calea reală pentru
   aplicațiile web rămâne browser-ul (MCP de browser + Chrome DevTools).
3. **Verificarea OAuth** a aplicației nu e făcută. Nu e nevoie pentru uz
   personal, dar e nevoie dacă aplicația ar fi folosită de altcineva.
4. **Photos**: refuzul **nu** vine din grant și **nu** din verificarea aplicației.
   Măsurat: tokenul duce `photoslibrary` + `photoslibrary.readonly` +
   `photoslibrary.appendonly`, API-ul e activ în proiectul clientului OAuth,
   contul are bibliotecă reală (100,4 GB folosite), iar același token răspunde
   200 pe Drive (control). Cauza e regula Google: din **31 martie 2025**
   scope-urile `photoslibrary.readonly` / `photoslibrary` / `photoslibrary.sharing`
   au fost retrase - rămâne accesul doar la conținutul creat de aplicație
   (`photoslibrary.readonly.appcreateddata`), iar citirea bibliotecii trece prin
   Picker API, care cere un `pollingUri` public. Sursa:
   https://developers.google.com/photos/library/guides/authorization

## 7. 27 oct 2026, 11:19-12:05 - consimțământul #2, defectul de cale, cauza Photos

### 7.1 Clickul lui Popy a ajuns la capăt, dar schimbul codului a murit
Măsurat: `CODE_RECEIVED=1` de două ori (11:25:41, 11:25:56), `PROVISION_EXIT=1`
în ambele, `scope_count=0`. Cauza, cuvânt cu cuvânt, din `provision_output`:
`Cannot find module '...projects\google-layer\google-grant.js'`.
`provision-grant.cjs` cerea modulul printr-o **cale absolută hardcodată**, iar
folderul `google-layer` se mutase în `Mavis-Google_Access\google-layer` cu
consolidarea. Deci: clickul fusese consumat de două ori, iar schimbul nu se
putuse face - **defectul a apărut după ce omul acționase**.

Reparație, la sursă, nu prin mutarea unui literal: rezolvare prin listă de
candidați (`GA_LAYER_DIR` -> `google-layer` lângă script -> rădăcinile de
proiect) + ieșire **loud 7** cu lista căutată, în loc de stack trace; plus o
copie a modulului lângă script, ca hostul să nu depindă de locul repo-ului.
Probă: `GRANT_MODULE=<cale>` + `TOKEN_ENDPOINT_HTTP=400 invalid_grant` +
`NO_CHANGE=1` - modulul se încarcă, Google răspunde, credentialul nu e atins.

### 7.2 Consimțământul #2, cu 30 scope-uri - obținut
`CODE_RECEIVED=1` (11:37:52) -> `PROVISION_EXIT=0` -> `SCOPES=30` ->
`RESTART_EXIT=0` -> `PROBE_EXIT=0` -> `VERDICT=PASS`. Lanțul s-a dus singur
după click: schimb, publicare în volum, restart container, probă, notificare.
`photoslibrary` și `chat.spaces.readonly` au intrat în token.

### 7.3 Chat a trecut, Photos nu - și cauza nu e a mea
Probă pe 16 servicii: **chat OK** (15 spații; era REFUSED), **photos încă
REFUSED** (403). Izolat cu `scripts/probe-photos.mjs`: tokenul duce cele trei
scope-uri Photos, `mediaItems.list` și `albums.list` dau 403, iar Drive dă 200
pe același token (control). Contul e personal (gmail.com, fără hosted domain),
proiectul API-ului (`1068987308935`) e chiar proiectul clientului OAuth, iar
API-ul e activ. Regula oficială spune că din **31 martie 2025** acele scope-uri
au fost retrase: rămâne doar conținutul creat de aplicație.

Așadar, cerute `photoslibrary.readonly.appcreateddata` + `photoslibrary.edit.appcreateddata`
(32 scope-uri), iar uneltele Photos rescrise pe modelul real: `gphotos_list`,
`gphotos_albums`, `gphotos_create_album`, `gphotos_upload`, `gphotos_edit_item`.
Picker API **ne** legat: `sessions.create` cere un `pollingUri` pe care Google
însuși trebuie să-l ajungă - imposibil de la `127.0.0.1`. Documentat, nu
cosmetizat.

### 7.4 Cloud
Run `40479493605`: `SOURCE_COMMIT=3bd5420`, `CREDENTIAL_FIELDS` complete,
`scope_chars=1233`, `VERDICT=PASS`, 11 servicii cu date reale. Secretul merge:
corecția BOM (`sed '1s/^\xEF\xBB\xBF//' | tr -d '\r\n'`) a rezolvat
`base64: invalid input`.

### 7.5 Ascultătoare: 90/60 min -> **180 min**
Un răspuns uman nu trebuie să se piardă într-un timeout.

## 8. 27 oct 2026, 12:06-12:15 - consimțământul #3 și starea finală măsurată

### 8.1 Grant de 32 scope-uri
`CODE_RECEIVED=1` (12:06:54) -> `PROVISION_EXIT=0` -> `SCOPES=32` ->
`RESTART_EXIT=0` -> `PROBE_EXIT=0` -> `VERDICT=PASS`. Tokenul duce acum și
`photoslibrary.readonly.appcreateddata` + `photoslibrary.edit.appcreateddata`.

### 8.2 Proba pe 16 servicii - 13 OK
`identity`, `drive`, `gmail`, `calendar`, **`photos`**, `books`, `tasks`,
`apps-script`, `chat`, `contacts`, `youtube`, `docs`, `sheets` -> STATUS=OK cu
date reale. REFUSED, fiecare cu cauza măsurată:
- **keep** - 403: scope-ul nu există în registrul public de scope-uri Google
- **sites** - 404: API-ul a fost retras de Google
- **notebooklm** - `NO_EXTENDLM_TOKEN`: așteaptă autentificarea lui Popy pe
  extendlm.com

### 8.3 Photos: calea de scriere, probată fără să creeze nimic
API-ul Photos Library **nu are** `albums.delete` - un album creat se poate doar
redenumi sau depublicat. Un album de test ar fi fost gunoi permanent în
biblioteca lui Popy. Așadar proba s-a făcut cu un corp gol:
`POST /v1/albums` cu `{}` -> **400 „Request must have a title for the album."**
Dacă scope-ul ar fi lipsit, răspunsul ar fi fost 403. Deci 400 înseamnă că
autorizarea a trecut - și **nu s-a creat niciun album**.
`mediaItems.list` 200, `albums.list` 200, Drive 200 (control), `VERDICT=PASS`.

### 8.4 NotebookLM: nu există API public
Confirmat din două surse independente: directorul oficial Google
(`https://www.googleapis.com/discovery/v1/apis`) nu are nicio API `notebooklm`
- doar `notebooks` (Vertex AI) - iar `gcloud services list --available` nu
listează niciun serviciu NotebookLM. Deci ExtendLM e singurul drum prin MCP,
și e legat corect: client dinamic, PKCE S256, ascultător pe `127.0.0.1:8799`
cu fereastră de 180 de minute.

## 9. 27 oct 2026, 12:29-12:42 - NotebookLM a devenit LIVE

### 9.1 Loginul nu era pasul lipsă - autorizarea era
La 12:29 `data/extendlm.json` era **ABSENT**, iar portul `127.0.0.1:8799`
asculta în continuare. Diferența dintre „am făcut login" și „am autorizat" a
fost măsurată, nu ghicită: procesul ascultător (node
`extendlm-provision.mjs --port 8799`, pornit 11:37:14) ține `state` +
`code_verifier`; deschiderea URL-ului de autorizare produce callbackul cu
`code`. Loginul pe `extendlm.com` nu produce cod - doar îți permite să treci
de ecranul de consimțământ.

Rezultatul, măsurat:
- callbackul a ajuns: `http://127.0.0.1:8799/callback?code=…&state=…`, cu
  `state` **identic** cu cel ținut de procesul viu (valoarea nu se publică:
  e nonce de CSRF, consumat deja);
- `data/extendlm.json`: **1118 B**, scris la 12:33:24 - `token_len=87`,
  `refresh_token` prezent, `scope` 436 caractere, `obtained_at=2026-10-27T10:33:24Z`,
  `expires_at` = +3 h;
- portul `8799` s-a închis imediat după schimb (`server.close()`) - comportament
  corect, nu o cădere.

**Leție de măsurare:** taskul de fundal a fost raportat `status=lost` la 12:28,
dar procesul node a supraviețuit (măsurat la 12:29: `LISTENING pid=55620`,
pornit 11:37:14). *Task pierdut* ≠ *proces mort*. Verificarea s-a făcut pe
obiectul real (port + PID + command line), nu pe raportul tracker-ului.

### 9.2 DEFECT MĂSURAT: `notebooklm_ask` nu trimitea întrebarea
Cu tokenul prezent, unealta răspundea `HTTP=200` - dar **nu întreba nimic**:
implementarea făcea `initialize` + `tools/list` și returna lista de unelte
plus șirul întrebării. Era exact cazul pe care `docs/EXTENDLM.md` îl avertiza
(`## De ce notebooklm_ask trebuie să apeleze unelte reale`): o probă care
listează unelte poate trece cu un token mort, pentru că nu execută nimic.

Reparația, la sursă (`container/server.mjs`):
1. `list_notebook_users` -> `extension_connection` + `auth_user_id`
   (forma măsurată: `{connections:[{extension_connection, users:[{auth_user_id, is_selected}]}]}`);
2. `list_notebooks` -> primul notebook (forma măsurată: cheie **`items`**, câmp **`id`**);
3. `ask_notebook` -> întrebarea, cu răspunsul întors.

### 9.3 Starea măsurată a lanțului ExtendLM
| Măsurătoare | Valoare |
|---|---|
| `TOOL_COUNT` | **160** unelte |
| `TOOLS_HTTP` | 200 (`INIT_HTTP=400` - serverul e stateless, fără `mcp-session-id`) |
| `extension_status.connected` | **true** |
| contul selectat | `apvizual@gmail.com`, `auth_user_id=0`, `is_selected=true` |
| `get_notebooklm_capabilities` | `authenticated=true`, `tier=NOTEBOOKLM_TIER_PRO_CONSUMER_USER`, `notebook_limit=500`, `source_limit=300` |
| notebookuri vizibile | `JULES` (184 surse), `GEMINI & AI STUDIO` (251 surse), … |

**Corectură de drift:** `docs/EXTENDLM.md` lista ca „deschis" faptul că portul
9412 (profilul `minimax-notebooklm`) era închis. Măsurătoarea arată că aceasta
era o ipoteză greșită: extensia din Chrome-ul obișnuit al lui Popy **este
conectată** (`connected=true`). Portul 9412 e un profil local, nu canalul
extensiei.

### 9.4 Proba reală prin unealta reparată
`notebooklm_ask` cu întrebarea „In one short paragraph: what is this notebook
about, and what are its main sources?"` ->
`notebook_id=f7ea4298-8604-4df3-ab3f-a6d634d4cbc6`, `notebook_title=JULES`,
`answer_chars=8139`, `is_error=false`. Răspunsul e despre Google Jules, cu
numărul de surse și depozitele reale - nu un mesaj de eroare deghizat.

### 9.5 Bilanț: 14 OK / 2 REFUSED / 0 ERROR
`TALLY={"OK":14,"REFUSED":2,"ERROR":0,"SKIP":0}`, `VERDICT=PASS`, `PROBE_EXIT=0`.
`notebooklm` a trecut din REFUSED în OK. Rămân REFUSED doar cele două API-uri
retrase de Google: **keep** (403, scope inexistent) și **sites** (404, API
retiras).

Container: `google-access:1.0.7`, `running|healthy`, `grant=live`,
`reauth_required=false`, 30 unelte. Semnătura lui `/app/server.mjs` din imagine
e identică cu cea din repo (`c9605239322b420b…`) - `MATCH=True`.

### 9.6 DEFECT MĂSURAT: sync-ul ștergea regula `.work/` din `.gitignore`
`sync-container-source.py` scria `.gitignore` dintr-o constantă proprie care
nu conținea regula `.work/`. La rularea de după reparația serverului, regula a
dispărut din fișier, iar `git status` a expus o clonă de lucru a repo-ului
MAVIS-CLOUD (418 fișiere, 15 MB) - într-un repository **public**. Nu s-a
introdus nimic în istoric, pentru că poarta a oprit înainte de commit.

Reparația, la sursă: constanta conține acum regula completă, iar scriptul
**verifică** proprietatea reală în loc să o presupună:
- `git check-ignore` pentru `data/credentials.json`, `data/extendlm.json`,
  `.work/MAVIS-CLOUD/README.md`;
- `git ls-files` - nimic sub `data/`, `logs/`, `state/`, `.work/` să fie
  **urmărit** (o regulă de `.gitignore` nu scoate din index un fișier deja
  adăugat).

Falsificare pe copie: într-un repo-copy cu `data/credentials.json` adăugat forțat,
poarta a raportat `PROBLEMS=2` (`NOT_IGNORED` + `TRACKED_SENSITIVE_PATH`) și a
ieșit cu **2**; repo-ul real a rămas neatins. Pe repo-ul real:
`TRACKED_CHECK_OK files=79 sensitive=0`, `PROBLEMS=0`.

## 10. 27 oct 2026, 11:15-13:43 - imaginea reparată, Cloud verde, heartbeat

### 10.1 DRIFT MĂSURAT: repo-ul era în urmă, imaginea era veche

La începutul acestei etape, trei semnături diferite pentru `server.mjs`:

| Artefact | SHA256 (normalizat CRLF→LF) | Byte |
|---|---|---|
| imaginea `google-access:1.0.8` (`/app/server.mjs`) | `3f2cd1b1f827786d…` | 57.278 |
| sursa vie `~/.minimax/google-access/server.mjs` | `8429fa5129192899…` | 58.781 |
| repo `container/server.mjs` (la HEAD `3492655`) | `c9605239322b420b…` | 49.576 |

Cauza, măsurată: imaginea a fost construită la **11:15:03Z**, iar reparările
(`credentialFingerprint`, `GA_EXTENDLM_NO_REFRESH`) au fost scrise în sursa vie
la **11:20Z** - **după** build. Repo-ul nu fusese sincronizat. Deci containerul
rula codul fără amprenta credentialului, exact defectul care producea 403 cu
scope deja acordat.

Reparația: `sync-container-source.py` (live → repo) → `COPIED server.mjs
sha256=8429fa5129192899`, `PROBLEMS=0`, `TRACKED_CHECK_OK files=80 sensitive=0`;
apoi `google-access:1.0.9` construit din aceeași sursă.

Verificare a imaginii, **înainte** de a atinge containerul:
`/app/server.mjs` = `8429fa5129192899…` (identic cu sursa vie), `grep -c
GA_EXTENDLM_NO_REFRESH` = 3, `grep -c credentialFingerprint` = 3, `grep -c
photospicker` = 10.

Container recreat cu aceiași parametri (port `127.0.0.1:8766`, volum `data`
rw, `E:\--- System Secrets:/secrets:ro`, `GA_PORT=8766`):
`running|healthy`, `grant=live`, `reauth_required=false`, **32 unelte**,
semnătura în container `8429fa5129192899…` - containerul rulează codul reparat.

### 10.2 DEFECT MĂSURAT: cache-ul de token nu purta amprenta credentialului

După lărgirea consimțământului, credentialul din volum e înlocuit, dar tokenul
de acces rămă în cache - și aparținea grantului vechi. Containerul răspundea
`403 insufficient authentication scopes` deși scope-ul era acordat și prezent în
fișier. Reparație, la sursă: `credentialFingerprint(creds)` (lungimea +
ultimele 12 caractere ale refresh token-ului + `provisioned_at`) intră în cache,
iar `accessToken()` re-emite tokenul la schimbarea credentialului.

Probă că defectul e reparat, prin container, nu prin host:
`gphotos_picker_start` → `HTTP=200`, `session_id=c39d0b83-90b2-49a2-bc64-29dd63db92c0`,
`picker_uri` obținută, `expire_time=2026-11-03T11:28:05Z`.

### 10.3 Proba pe 16 servicii, după rebuild

`TALLY OK=14 REFUSED=2 ERROR=0 SKIP=0`, `VERDICT=PASS`, `PROBE_EXIT=0`.
Cele două refuzuri sunt ale Google, nu ale containerului: **keep** (403, scope
inexistent) și **sites** (404, API retras). `notebooklm` = OK.

### 10.4 REGESIE MĂSURATĂ: am publicat peste workflow-ul Cloud o copie mai veche

Publicarea workflow-ului în MAVIS-CLOUD a pornit din copia locală din repo.
Diff-ul măsurat contra **versiunii care trecuse** (blob `bbb3b162…`) a arătat că
copia locală pierduse două lucruri: pasul „Diagnose the secret shape" și
`sed '1s/^\xEF\xBB\xBF//'` înainte de `base64 -d`. Rezultatul, măsurat:
run-ul `40496656800` → **failure**, `base64: invalid input`.

Lecția: un workflow nu e un fișier de copiat în jur, e piesa care trebuie
demonstrată. Repararea, la sursă: `scripts/rebuild-cloud-workflow.py` **compune**
din versiunea care a trecut, adaugă pasul ExtendLM și `-e
GA_EXTENDLM_NO_REFRESH=1`, apoi **verifică 9 proprietăți** înainte de a scrie
(care ar fi inclus BOM-strip-ul pe ambele secrete, pasul de diagnostic, absența
triggerului `pull_request` citită din structura YAML parseată, nu din text) →
`PROBLEMS=0`.

Publicat: blob `66bbff554dd0d436…` în Cloud = blob local (identic), commit
`dc57899e`.

### 10.5 Cloud: run-ul verde, măsurat în Cloud

Run `40497337673` (push), concluzie **success**:

| Măsurătoare | Valoare |
|---|---|
| `SOURCE_COMMIT` | `f589f823fc7b89fe…` (sursa publică de adevăr) |
| `SECRET_LEN` / `SECRET_FOREIGN_CHARS` | 2596 / **0** (base64 curat, fără BOM) |
| `CREDENTIAL_FIELDS` | `client_id,client_secret,refresh_token,scope,provisioned_at,sourcescope_chars=1533` |
| `EXTENDLM_FIELDS` | `token_len=87`, `refresh=yes` |
| `SERVICE=notebooklm` | **OK** (bytes=2119) |
| bilanț | 14 OK / 2 REFUSED / 0 ERROR |
| `VERDICT` / `PROBE_EXIT` | `PASS` / **0** |

Secretul de credential Google a fost și re-publicat curat (base64 fără BOM,
scris cu `--body` pe o singură linie) - sursa **și** receptorul sunt acum
corecte: nu e suficient să cureți receptorul.

### 10.6 Heartbeat-ul permanent (mecanismul de reînnoire + publicare)

`scripts/publish-extendlm-secret.mjs` + `scripts/extendlm-heartbeat.ps1` +
taskul Windows **`MavisExtendLMHeartbeat`** (repetiție la 30 min).

Proprietatea măsurată a modelului: endpoint-ul **rotește** refresh token-ul
(`ROTATED_REFRESH=1`), deci rotația e o operație cu un singur proprietar.
Publicatorul rotește **doar când e nevoie** (token valid cu >60 min → nu
rotește), ca să nu se lupte cu containerul, care rotește și el și își
persistează rezultatul.

| Măsurătoare | Valoare |
|---|---|
| rotație | `REFRESH_HTTP=200`, `ROTATED_REFRESH=1`, `TOKEN_LEN=87` |
| publicare | `SECRET_WRITE=ok`, `SECRET_READBACK=present`, `age_seconds=14` |
| declanșare proprie a taskului | `LAST_RUN=13:43:14`, `LAST_RESULT=0`, `NEXT_RUN=14:13:14` |
| log | `C:\Users\apviz\.minimax\google-access\logs\extendlm-heartbeat-YYYY-MM-DD.log`, UTF-8 fără BOM |
| falsificare (repo inexistent) | `EXIT=2` |
| falsificare (director inexistent) | `EXIT=3` |

### 10.7 DEFECT MĂSURAT: logul a primit credentialul, prin mesajul de eroare

La falsificare, `gh` a eșuat și a **ecoulat linia de comandă**, care conține
`--body <snapshot>` - snapshotul fiind chiar tokenul. Logul a primit credentialul.
Reparație în două locuri: publicatorul redactă payload-ul înainte să-l
tiprească (`[REDACTED_SNAPSHOT]`), iar wrapper-ul aplică o plasă de siguranță
(`[A-Za-z0-9+/=]{80,}` → `[REDACTED_B64]`). Logul existent a fost rescris:
`LONG_B64_BEFORE=1` → `AFTER=0`, iar falsificarea repetată a produs `EXIT=2`
**fără** niciun șir lung în log.

### 10.8 Starea la 13:43

- Container `google-access:1.0.9`, `running|healthy`, `grant=live`, 32 unelte.
- Grant: **33 scope-uri** (inclusiv `photospicker.mediaitems.readonly`).
- ExtendLM: token proaspăt, rotație automată, snapshot publicat în secretul Cloud.
- Cloud: run `40497337673` verde, `notebooklm` OK măsurat în Cloud.
- Repo: `main` = `origin/main`, divergență 0/0.

## 11. Browser MCP - DEFECT MĂSURAT: înregistrat, activ, și imposibil de pornit

Punctul „Browser MCP" din scop nu era atins. Măsurarea lui a găsit altceva: serverul
`minimax-notebooklm` era **înregistrat și activ** în profilul MCP, cu o cale care
**nu există**.

| Ce | Măsurat |
|---|---|
| intrarea în `mcp.json` | `enabled=true`, `command=node.exe`, `args=[…\projects\google-layer\minimax-notebooklm.js]` |
| folderul `projects\google-layer\` | **ABSENT** - nu a existat niciodată |
| fișierul real | `projects\Mavis-Google_Access\google-layer\minimax-notebooklm.js` (urmărit în git) |
| portul CDP 9412 | **închis** |
| consecință | serverul nu pornește: „enabled" într-un fișier de configurare e o **declarație**, nu o măsurătoare |

Reparație: calea corectată în intrarea MCP, cu descrierea actualizată cu
măsurătorile de după reparație.

**Sonda permanentă:** `scripts/probe-minimax-notebooklm.mjs` pornește serverul ca
proces copil, vorbește JSON-RPC pe linii peste stdio (același protocol ca
serverul) și raportează ce a venit înapoi.

| Măsurătoare | Valoare |
|---|---|
| `INITIALIZE_OK` | 1 - `minimax-notebooklm` 1.0.0 |
| `TOOL_COUNT` | **4** - `nblm_health`, `nblm_list_notebooks`, `nblm_get_sources`, `nblm_ask` |
| `nblm_health` | `state=authenticated`, `authenticated=true`, `notebook_list=true`, `sign_in_cta=false`, `circuit=closed` |
| Chrome | pornit de server pe `127.0.0.1:9412` (pid măsurat) cu profilul propriu |
| `nblm_list_notebooks` | notebook-uri reale: `JULES` (182 surse), `GEMINI & AI Studio` (251), `CV-Automation` (98), `CLIENTS` (2), `AGENTS` (8), `TRADE` (1), `CV-Notebook` (99), `SENTINEL Role` (225), `OPTIMUS System` (5) + restul listei |
| verdict | `SERVER_ANSWERS`, exit 0 |

Deci sunt **două drumuri vii** spre NotebookLM, independente prin construcție:
proxy-ul ExtendLM din container (token, peste HTTPS, 160 unelte) și serverul
de browser cu profil Chrome propriu (4 unelte, sesiune deja autentificată).
Nu se amestecă: `minimax` și `Hermes` rămân universuri separate.

Descrierea intrării `Google_Access` din profilul MCP spunea „25 unelte" -
corectată la 32, cu numărul măsurat și cu starea Cloud-ului.

## 12. 28 oct 2026, 00:38-00:48 - Photo Picker: cauza măsurată, selecția capturată

### 12.1 Simptomul și cauza lui, din discovery document

Popy a deschis `pickerUri` și a primit: **„Couldn't open Google Photos. Go back
to the partner app, website, kiosk or other device that you started from and
connect to Google Photos again."**

Cauza, din discovery document-ul oficial (`photospicker` v1, rev. **20261026**),
câmpul `pickerUri`:

> To view this page successfully, the user must be logged into the Google
> account that owns this session in their web browser. The `pickerUri` cannot be
> opened in an iframe due to security reasons.

Deci există exact **două** cauze, care produc **același** mesaj: browserul nu
e conectat la contul care deține sesiunea, sau URI-ul a fost deschis într-un
cadru încorporat. Ghicirea între ele nu valorează nimic - de aceea probe-ul
de mai jos, cu același URI în două browsere.

Contul care deține sesiunea, măsurat pe obiect (tokeninfo pe tokenul
containerului): `apvizual@gmail.com`, 35 scope-uri, `HAS_PICKER=true`.

### 12.2 Proba controlată: același URI, două browsere

| Context | Rezultat |
|---|---|
| Chrome cu profilul propriu `minimax-notebooklm` (autentificat pe `apvizual@gmail.com`) | `PAGE_HEAD="Search your photos and albums Clear"`, `DETECT_BROKEN=0`, `VERDICT=PICKER_UI_LOADED` |
| fereastra în care a fost deschis linkul de Popy | „Couldn't open Google Photos" |

Concluzie măsurată: **sesiunea, scope-ul și URI-ul sunt corecte**; nuvelește
fereastra, nu API-ul. Sonda permanentă: `scripts/probe-picker-cdp.mjs`
(CDP 9412, creează tabul și citește ce răspunde pagina).

### 12.3 Reparația: fereastra, deschisă de mine, pe contul lui

Chrome **vizibil** (nu headless), cu profilul propriu al instalației,
pornit direct pe `pickerUri`:

```
chrome.exe --user-data-dir=%LOCALAPPDATA%\minimax-notebooklm\chrome_profile \
           --remote-debugging-port=9412 --window-size=1400,900 <pickerUri>
```

Rezultat: `PICKER_UI_LOADED`, o singură fereastră pe ecran, contul
`apvizual@gmail.com`. Popy a ales 4 poze și a apăsat „Done".

### 12.4 Captura, măsurată

| Măsurătoare | Valoare |
|---|---|
| `mediaItemsSet` | **true** |
| `PICKED` | **4** |
| fișiere descărcate | `FB_IMG_1567778444962.jpg` (32.016 B), `FB_IMG_1567778290609.jpg` (87.827 B), `FB_IMG_1662778826700.jpg` (57.899 B), `FB_IMG_1662778884985.jpg` (26.204 B) |
| verificare | `content-type: image/jpeg` + semnătură magică JPEG (`ff d8 ff`) - nu pagină de eroare cu extensie `.jpg` |
| scrise în | `state/picked/2026-10-27/` + `manifest.json` |

Scripturi: `scripts/picker-watch.mjs` (sondă sesiunea și scrie
`data/picked-media.json`), `scripts/picker-download.mjs` (descărcă și
verifică octeții).

### 12.5 Automatizarea, ca să nu depindă de o conversație deschisă

`scripts/picker-heartbeat.ps1` + taskul Windows **`MavisPickerHeartbeat`**
(repetiție 15 min): citește `data/picker-session.json`, sondează sesiunea,
dacă utilizatorul a terminat, scrie lista, descarcă media, **șterge sesiunea**
(API-ul cere exact asta ca să nu se acumuleze), și scrie o linie datată în
`logs/picker-heartbeat-YYYY-MM-DD.log`.

Proba manuală: `EXIT=0 … SESSION_ID=f4587e83… mediaItemsSet=false
VERDICT=NOT_PICKED_YET`. Captura de mai sus a trecut prin același cod.

### 12.6 Curățenia măsurată

Două sesiuni vechi au fost șterse prin `DELETE /v1/sessions/{id}` → **HTTP 200**,
iar sesiunea consumată (după „Done") a fost ștearsă la fel. Taburile și
ferestrele învechite au fost închise, iar pe ecran a rămas **o singură** fereastră
de picker, pe sesiunea curentă.

Notă de măsurare: în timpul curățării, scriptul a închis tabul **nou** în locul
celu consumat (o constantă de sesiune veche în cod). Corectat pe loc, apoi
verificat pe obiect: `PAGES_LEFT` conține doar sesiunea curentă.

## 13. 28 oct 2026, 23:30-23:52 - punctul de control și patru defecte măsurate

Finalizarea punctului de control a scos la iveală defecte care stăteau
active, nu defecte ipotetice. Toate au fost măsurate înainte de a fi reparate.

### 13.1 Trei intrări MCP rupte de mutarea `google-layer/`

Când `google-layer/` a fost mutat din repo-ul backbone în
`Mavis-Google_Access/google-layer/` (27 oct), **trei intrări din registry-ul
global `mcp.json` au continuat să indice spre vechea cale**:

| Intrare | Cale înregistrată | Fișier | Stare |
|---|---|---|---|
| `gdrive-mcp` | `projects\google-layer\gdrive-launcher.js` | inexistent | **enabled** |
| `gmail-mcp` | `projects\google-layer\gmail-launcher.js` | inexistent | **enabled** |
| `google-calendar-mcp` | `projects\google-layer\calendar-launcher.js` | inexistent | dezactivat |

Registry-ul spunea „enabled", fișierele nu existau, și **nimic nu semnala**.
Deoarece configurația MCP este **globală**, o cale moartă acolo stinge
capabilitatea pentru fiecare agent de pe stație, nu doar pentru sesiunea care a
scris-o.

Instrument nou: `scripts/probe-mcp-stdio.mjs` - pornește comanda și argumentele
**exact cum sunt în registry**, face handshake MCP real peste stdio și
raportează ce a răspuns. Falsificat în ambele sensuri înainte de a fi folosit:
`gdrive-mcp` → `INIT_OK=0 REASON=missing_on_disk(...)` (exit 2),
`minimax-notebooklm` → `INIT_OK=1 TOOLS=4` (exit 0).

După reparare (calea sancționată: interfața `mavis` pentru configurație MCP):

| Intrare | Măsurătoare după reparare |
|---|---|
| `gdrive-mcp` | `INIT_OK=1 SERVER=gdrive-mcp TOOLS=9` |
| `gmail-mcp` | `INIT_OK=1 SERVER=gmail-mcp TOOLS=36` |
| `google-calendar-mcp` | `INIT_OK=0` - **corect**: server HTTP, nu stdio; rămâne dezactivat |

### 13.2 `docker-mcp`: wrapper inexistent și dependențe lipsă

Intrare: `command = C:\Users\apviz\AppData\Roaming\npm\mcp-docker.cmd` -
**fișier inexistent** (pachetul `mcp-docker` nu are câmp `bin`, deci npm nu a
creat niciodată wrapperul). Răspunsul real al serverului:

```
Error [ERR_MODULE_NOT_FOUND]: Cannot find package '@modelcontextprotocol/sdk'
```

Pachetul a fost publicat cu `devDependencies` (SDK, dockerode, zod) și cu
`dependencies: { dotenv }` - deci nu are ce importa la runtime.

Reparat: dependințele de runtime instalate în pachetul existent (fără a atinge
nimic din Hermes), intrarea reorientată pe punctul de intrare real. Măsurat:
`INIT_OK=1 SERVER=docker-agent TOOLS=19`.

### 13.3 Regresia mutării: trei optimizări rămase în repo-ul vechi

Mutarea din 27 oct a fost verificată pentru **prezență**, nu pentru
**conținut**. Compararea linie cu linie (`scripts/compare-layer-versions.py`,
instrument nou) a arătat că trei fișiere au rămas înaintea optimizărilor
fuzionate pe 24 oct:

| Fișier | Optimizare | Pierdere măsurată |
|---|---|---|
| `bun-secrets-shim.js` | PR #11 - async I/O | 7 `await` → 0 |
| `gworkspace-oauth.js` | PR #31 - async OAuth client load | 4 `await` → 2 |
| `notebook-ask.js` | refactor async | 3 `await` → 2 |
| `verify-workspace.js` | PR #34 - async readLock | 5 `await` → 4 |

Toate cele patru au fost readuse din commitul fixat `9b96b69`
(`scripts/restore-layer-optimizations.py`), cu **verificare pe octeți**:
`disk_blob == src_blob` pentru toate patru, plus `node --check` curat pe toate
fișierele din `google-layer/` (`PARSE_FAILURES=0`).

Diferența măsurată nu a fost cosmetică: `gdrive-mcp` a răspuns în **2.264 ms**
după refacere, față de **29.452 ms** înainte - de **13× mai rapid** cu shim-ul
async.

### 13.4 O sesiune Picker consumată era raportată ca defect

La 01:18:39 heartbeat-ul a capturat **2 poze noi** alese de Popy și a șters
sesiunea (`SESSION_DELETE_HTTP=200`, așa cum cere API-ul). La 01:33:37
heartbeat-ul a sondat din nou sesiunea deja ștearsă, a primit `404
ENTITY_NOT_FOUND` și a ieșit cu **2**. Punctul de control a văzut acel 2 în
`C7` și a declarat **FAIL** - pentru faptul că utilizatorul terminase exact
acțiunea pentru care există pickerul.

Reparat la sursă: `404` este acum starea `SESSION_CONSUMED` (fișierul de
sesiune este **marcat** `session_id: null, state: consumed`, nu șters -
rămâne dovadă), cu ieșire 0. `C9` raportează „session consumed - nothing to
watch".

### 13.5 Două bug-uri în instrumentul de control, descoperite de el însuși

- **`__dirname is not defined`** - ESM nu are `__dirname`; prima rulare a
  doctorului extins a murit cu **exit 3**, distinct de verdict. Corectat cu
  `fileURLToPath(import.meta.url)`.
- **`Cannot read properties of undefined (reading 'OK')`** - în calea de
  re-probare tranzitorie se citea `v2.byStatus.OK`, dar `evaluate()` întoarce
  un obiect plat cu `oks`. Explicația a apărut în exact clipa în care Google
  Books a răspuns 503 - **un instrument care moare la o glimmă a Google nu mai
  măsoară nimic**. Corectat; re-probarea funcționează:
  `transient_recovered=books`.

### 13.6 Verdictul final, măsurat

```
CHECK C1.container   OK   status=running health=healthy image=google-access:1.0.9 restart=unless-stopped
CHECK C1b.running-code OK   repo=8429fa512919 running=8429fa512919 match=true
CHECK C2.health      OK   grant=live reauth=false tools=32
CHECK C3.services    OK   OK=14 REFUSED=2[keep,sites] ERROR=0[]
CHECK C4.extendlm    OK   token_minutes_left=235 refresh_token=yes cloud_secret_age_min=6
CHECK C5.browser-mcp OK   server=minimax-notebooklm tools=4
CHECK C6.mcp-registry OK  enabled=true url=http://127.0.0.1:8766/mcp
CHECK C10.mcp-paths  OK   checked=23 dead_total=0
CHECK C7.tasks       OK   count=4
CHECK C8.consent     OK   listener alive (processes=1)
CHECK C9.picker      OK   session consumed - nothing to watch

SUMMARY checks=11 failed=0 warnings=0
VERDICT=PASS
```

Rularea prin taskul programat: `lastResult=0`, linie nouă în
`logs/ga-doctor-2026-10-28.log`.

Falsificări (controlul de control poate să se aprindă roșu):

| Falsificare | Rezultat |
|---|---|
| `--self-test --fail C1.container` | `VERDICT=FAIL` exit **2** |
| `--self-test --fail C10.mcp-paths` | `VERDICT=FAIL` exit **2** |
| `--container NoSuchContainer_zzz` | `VERDICT=FAIL` exit **2** |

### 13.7 Ce a rămas în afara scopului, măsurat și raportat

- `README_SYSTEM_TOPOLOGY_AND_AGENT_GUIDELINES.md` din rădăcina backbone-ului
  are **0 octeți**, dar **nu e trunchiat**: este un **symlink** către
  `C:\Antigravity - SYSTEM TOPOLOGY - 3 Partition System\...`, ținta există
  (15.936 B). Adăugat în `.gitignore` - un symlink absolut pe o cale locală
  nu are ce căuta într-un repo PUBLIC.
- Trei repo-uri stăteau nesting în arborele backbone-ului
  (`Mavis-Google_Access/`, `Optimus_CD (by Jules)/`, `Optimus_CI (by Mavis)/`),
  fiecare cu istoria și remote-ul lui. Fără regulă în `.gitignore`, un
  `git add` le-ar fi transformat în **gitlink-uri** (mod 160000) - exact
  defectul reparat la `c73fa0b`. Adăugate și verificate cu `check-ignore`.
- `google-calendar-mcp` rămâne **dezactivat**, pe măsură: serverul său pornește
  pe HTTP, nu stdio, iar `google-workspace-mcp` acoperă deja Calendar cu un
  grant read-only și un apel calendarList real.

---

## 14. 28 oct 2026, 01:50-02:06Z - imaginea 1.0.10, defectul de tabele și roșul fals

### 14.1 Rebuild-ul 1.0.10: containerul recreat, grantul a supraviețuit

Imaginea `google-access:1.0.9` a fost reconstruită ca **`google-access:1.0.10`**,
din sursa vie `C:\Users\apviz\.minimax\google-access`, cu Dockerfile-ul
documentat. Containerul a fost recreat cu aceiași parametri: nume
`Google_Access`, `--restart unless-stopped`, `-p 127.0.0.1:8766:8766`,
`-e GA_PORT=8766`, volum rw `C:\Users\apviz\.minimax\google-access\data:/data`,
volum ro `E:\--- System Secrets:/secrets`. Măsurat:

| | Măsurat | Comanda |
|---|---|---|
| Container creat | `2026-10-28T01:50:31.196974092Z` | `docker inspect Google_Access --format {{.Created}}` |
| Imagine | `google-access:1.0.10` | `docker inspect` / `docker ps` |
| Stare | `healthy` | `docker inspect` |
| Grant | `grant=live`, `tools=32` — credentialul stă în volum, deci a supraviețuit recreării | `CHECK C2.health` |
| Octeți rulați | `server.mjs` sha256 `63e4ea8d2bbb…` | `CHECK C1b.running-code` |
| Octeți în repo | `server.mjs` sha256 `63e4ea8d2bbb…` | `Get-FileHash container\server.mjs` |

`repo=63e4ea8d2bbb running=63e4ea8d2bbb match=true` — incidentul 1.0.9 (imagine
veche, cod reparat în repo) nu se mai repetă.

### 14.2 DEFECT MĂSURAT: walker-ul de tabele al uneltei Docs arunca pe ORICE document cu tabel

În API-ul Google Docs, resursa `Table` are `rows` și `columns` ca **numere**
(numărul de rânduri / coloane); conținutul real stă în `tableRows` și
`tableCells`. Codul vechi parcurgea `table.rows.forEach(...)`, deci arunca pe
**orice** document care conține un tabel:

```
ERROR: el.table.rows.forEach is not a function
```

Defectul a devenit vizibil abia când un document de transcript cu **trei
tabele** a ajuns primul document din Drive — pe acela pe care îl citește
proba. Reparat în **sursa vie** și în copia din repo (`container/server.mjs`).

Dovada, măsurată: `gdocs_get` pe acel document întoarce acum
`title=MavisCloud-TRANSCRIPT-SESIUNE-2026-10-28` cu **5091 caractere**
extrase (înainte, aceeași apelare arunca).

Re-măsurat de două ori în această fereastră:
`SERVICE=docs TOOL=gdocs_get STATUS=OK DETAIL=keys=title+document_id+text bytes=5227`
(la 02:05:26Z).

### 14.3 DEFECT MĂSURAT: punctul de control dădea ROȘU FALS

Înainte de reparare, **8 din 8** rulări ale punctului de control au fost
**ROȘII** — nu din cauza lui Google, ci din cauza defectului de tabele de mai
sus: un eșec permanent nu se vindecă prin re-probare, dar nici nu putea fi
distins de o glimmă.

Una dintre acele rulări a arătat și un **tranzitoriu**
(`transport: fetch failed`), produs de recrearea containerului în timpul
ferestrei. Logica nouă de re-probare l-a recuperat → `state=HEALTHY`.

### 14.4 Comportamentul nou al lui C3, măsurat

- orice refuz neașteptat este **re-probat, până la 4 încercări în total**
  (3 extra), cu pauză între ele;
- **cauza este afișată mereu, per serviciu** — niciodată un `REFUSED` gol;
- refuz **permanent** (403 / 404 / `MISSING_SCOPE` / un refuz nerecunoscut) care
  nu se recuperează → `state=FAILED_PERMANENT` → verificarea **pică**, exit **2**;
- refuz **tranzitoriu** care se recuperează → `state=HEALTHY`, iar blipul
  **rămâne scris** (nu e ascuns);
- refuz **tranzitoriu** care nu se recuperează → `state=DEGRADED_TRANSIENT` →
  `CHECK C3.services WARN` → numărat ca **warning**, exit **0** — niciodată OK
  mut.

Linii măsurate, din auto-verificarea offline
(`node scripts\ga-doctor.mjs --self-test`):

```
CHECK C3.services FAIL state=FAILED_PERMANENT OK=13 REFUSED=3[books,keep,sites] ERROR=0[] attempts=4 unexpected_refused=books status=REFUSED kind=permanent attempts=4 detail[books]=GOOGLE_HTTP_403: {"code":403,"message":"Request had insufficient authentication scopes.",...
CHECK C3.services OK   state=HEALTHY OK=14 REFUSED=2[keep,sites] ERROR=0[] attempts=2 transient_recovered=books status=REFUSED kind=transient attempts=2 detail[books]=GOOGLE_HTTP_503: {"code":503,"message":"Service temporarily unavailable.",...
CHECK C3.services WARN state=DEGRADED_TRANSIENT OK=13 REFUSED=3[books,keep,sites] ERROR=0[] attempts=4 persistent_transient=books status=REFUSED kind=transient attempts=4 detail[books]=GOOGLE_HTTP_503: {"code":503,"message":"Service temporarily unavailable.",...
```

Pe defectul real de la 14.2, linia arată:
`unexpected_error=docs status=ERROR kind=permanent attempts=4 detail[docs]=ERROR: el.table.rows.forEach is not a function`
— adică un defect permanent rămâne ROȘU, chiar după 4 încercări.

Rezultatul auto-verificării, măsurat:
`SELFTEST probes=3 falsified=2 blocked=1 expectations_met=3/3`, `VERDICT=PASS`,
exit 0. Iar falsificarea rămâne roșie:
`--self-test --fail C1.container` → `SUMMARY checks=11 failed=1 warnings=0`,
`VERDICT=FAIL`, exit **2**.

**Rata de bază, măsurată:** blipul pe Google Books apare în ≈ **1 din 3**
probe-uri. Cu 4 încercări, probabilitatea unui roșu fals scade de la ≈
`(1/3)²` ≈ **11 %** la ≈ `(1/3)⁴` ≈ **1,2 %**. Re-măsurat în această
sesiune: **3 din 5** probe-uri brute au răspuns HTTP 503 (`01:59:41Z`,
`02:01:48Z`, `02:05:26Z`), iar `02:02:49Z` a răspuns `OK`.

### 14.5 Starea finală măsurată (punctul de control, 01:54Z)

```
=== Google Access - control point ===
host=OPTIMUS_PRIME at=2026-10-28T01:54:00.065Z
container=Google_Access mcp=http://127.0.0.1:8766/mcp data=C:/Users/apviz/.minimax/google-access/data

CHECK C1.container OK   status=running health=healthy image=google-access:1.0.10 restart=unless-stopped
CHECK C1b.running-code OK   repo=63e4ea8d2bbb running=63e4ea8d2bbb match=true
CHECK C2.health OK   grant=live reauth=false tools=32
CHECK C3.services OK   state=HEALTHY OK=14 REFUSED=2[keep,sites] ERROR=0[] attempts=1
CHECK C4.extendlm OK   token_minutes_left=109 refresh_token=yes cloud_secret_age_min=11
CHECK C5.browser-mcp OK   server=minimax-notebooklm tools=4 path=C:\Users\apviz\.minimax-agent\projects\Mavis-Google_Access\google-layer\minimax-notebooklm.js
CHECK C6.mcp-registry OK   enabled=true url=http://127.0.0.1:8766/mcp type=streamable-http
CHECK C10.mcp-paths OK   checked=23 dead_total=0
CHECK C7.tasks OK   count=4
CHECK C8.consent OK   listener alive (processes=1)
CHECK C9.picker OK   session consumed (2026-10-27T23:48:10.291Z) - nothing to watch

SUMMARY checks=11 failed=0 warnings=0
VERDICT=PASS
```

Exit **0**. Rulează repetată la 01:58:24Z, cu aceleași rezultate
(`image=google-access:1.0.10`, `repo=63e4ea8d2bbb running=63e4ea8d2bbb`,
`state=HEALTHY OK=14 REFUSED=2[keep,sites] ERROR=0[] attempts=1`,
`SUMMARY checks=11 failed=0 warnings=0`, `VERDICT=PASS`, exit 0).

### 14.6 Cum se reproduce fiecare cifră

| Cifră | Comanda |
|---|---|
| Imaginea, starea, volumul | `docker ps` · `docker inspect Google_Access` |
| Grantul viu, numărul de unelte | `node scripts\ga-doctor.mjs` (verificarea `C2.health`) |
| Octeții rulați = octeții din repo | `node scripts\ga-doctor.mjs` (verificarea `C1b.running-code`) |
| Tally-ul pe servicii, cu cauza per serviciu | `node scripts\ga-doctor.mjs` (verificarea `C3.services`) |
| Cele trei stări ale lui C3 | `node scripts\ga-doctor.mjs --self-test` |
| Roșu fals, la cerere | `node scripts\ga-doctor.mjs --self-test --fail C1.container` (exit 2) |
| Blipul tranzitoriu pe Books | `node container\probe-services.mjs` |
| Citirea documentului cu trei tabele | `gdocs_get` pe `MavisCloud-TRANSCRIPT-SESIUNE-2026-10-28` (5091 caractere) |
| Tokenul ExtendLM și vârsta secretului Cloud | `node scripts\ga-doctor.mjs` (verificarea `C4.extendlm`) |




