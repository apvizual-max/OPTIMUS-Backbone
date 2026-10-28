# Google Workspace din Mavis Cloud — drumul real (măsurat 2026-10-21 → 2026-10-24)

Supersedează topicul vechi `google-access-in-cloud-absent` (2026-10-19 → 2026-10-21),
în care Google părea inaccesibil din cloud. **Acea concluzie a fost falsă**: cauza
era TLS-ul sandboxului, nu lipsa credentialelor.

## Cum e acum

OAuth propriu, cu 4 chei în secret manager:

| Cheie | Rol |
|---|---|
| `GOOGLE_CLIENT_ID_MAVIS_CLOUD` | client id (identificator public) |
| `GOOGLE_CLIENT_SECRET_MAVIS_CLOUD` | client secret |
| `GOOGLE_REFRESH_TOKEN_MAVIS_CLOUD` | refresh token |
| `GOOGLE_EMAIL` | `apvizual@gmail.com` |

**Merge din cloud:** Gmail, Drive, Calendar, Sheets, Slides.
**Nu merge din cloud:** Google Photos (`photoslibrary.googleapis.com`, 0/6),
`*.mcp.googleapis.com` (0/6), Docs API (blochează cu anti-bot din cloud →
citești conținutul prin `drive/v3/files/{id}/export`), Google Maps (cere
`GOOGLE_MAPS_API_KEY` + billing).

## Clientul care merge

Perechea din `~/.google-mcp/tokens/apvizual.json` (verificată în iulie, a făcut
Drive + Gmail): client_id `1068987308935-5b7h17gt1c5hc4i1m6eginads37o3m2h`.
Clientul e și în repo, în `mavis-tools/google-client.json`.

Celălalt client (`1068987308935-bp47aoerh6gu1aohm74blfhnccnku773`) vine dintr-un
proiect Google gestionat automat (familia `gen-lang-client-*`, Gemini CLI) — **nu
are consent pentru Drive/Gmail**.

**Regulă de secrete:** client_id e identificator public și poate sta în repo
public. Client secret-ul **nu** stă nici în memorie, nici în repo public — doar
prefix + referință la secret manager.

## Regula „7 zile"

OAuth consent screen în **Testing** ⇒ refresh token expiră în 7 zile de la
consimțământ ⇒ `invalid_grant` / „Token has been expired or revoked".
Excepție: doar `userinfo.email/profile/openid`. Fix: Publishing status → **In production**.
Sursă: support.google.com/cloud/answer/15549945.

⇒ Tokenul din iulie a expirat și **nu se moștenește** nici prin secret manager,
cât timp proiectul e în Testing.

## Fiecare API are propriul host

`www.googleapis.com/docs/v1/...` → **404** fals. Corect: `docs.googleapis.com`,
`sheets.googleapis.com`, `slides.googleapis.com`, `gmail.googleapis.com`,
`oauth2.googleapis.com`.

Test permanent: `mavis-tools/test-endpoints.js` — token fals → **401 = endpoint
există**, 404 = URL greșit, 0 = rețea. Legat în CI (`verify.yml`).

## Contractul de credentiale (din `mavis-tools/kit.js`)

Vechiul kit citea `~/.google-mcp/credentials.json` (obiect `installed`) +
`~/.google-mcp/tokens/mavis.json` (`refresh_token`) la `require()` → arunca dacă
lipseau. **Refăcut lazy** cu `google-auth.js`: env vars (cloud) sau fișiere
(local). Local și Cloud folosesc **același** `kit.js`.

## Scripturi (repo `apvizual-max/MAVIS-CLOUD`)

- `mavis-tools/google-local.js` — flux OAuth COMPLET, standalone (zero dependențe),
  rulează pe mașina lui Alex: citește `~/.google-mcp/credentials.json`, deschide
  linkul, prinde codul singur, schimbă în refresh_token, afișează cheile. Nu
  necesită repo la zi → se descarcă direct de pe raw.githubusercontent.
- `mavis-tools/google-link.js` — generează + autoverifică linkul.
- `mavis-tools/google-connect.js` — one-paste finisher (exchange + verificare live).
- `mavis-tools/google-exchange.js` — schimbă singur codul.
- `mavis-tools/google-setup.js` — generează cheile.
- `mavis-tools/test-endpoints.js` — test de endpoint (401/404/0).

## De ce părea inaccesibil (istoric)

- **Marketplace-ul MiniMax:** Hundsun, Qichacha, EverMe, PKUlaw, Office, WPS,
  WeCom — fără Google. Cache-ul de plugin-uri din runtime-ul de cloud: doar
  `figma` + `github`.
- **Catalogul de conectoare:** 116 tooluri, 5 provideri (`cloudflare` 4,
  `figma` 2, `github` 95, `matrix` 13, `email_workbench_credentials` 2) —
  **zero Google**. `partial: false`, `provider_failures: []` ⇒ catalog complet.
  `email_workbench_credentials` e transport de credențiale pentru plugin, **nu**
  client de mailbox.
- **API-ul de conectoare** a returnat `error: invalid signature`
  (`http_status: 400`, `auth_mode: sandbox-egress`) la orice apel, inclusiv
  direct ⇒ defecțiune de transport, nu „App neconectat".
- **MCP oficial Google există** (`gmailmcp/drivemcp/docsmcp/sheetsmcp/
  slidesmcp/calendarmcp.googleapis.com/mcp/v1`, sursă:
  developers.google.com/workspace/guides/configure-mcp-servers) — dar din cloud
  **0/6 conexiuni**. De pe Local merge.

## Reguli derivate

- Un `invalid signature` sau un search cu `partial: true` **nu dovedesc** că un
  App lipsește. Declară „catalogul nu e accesibil azi", nu „nu ai Gmail".
- Verifică întâi cu TLS-ul rezolvat (`NODE_TLS_REJECT_UNAUTHORIZED=0`) — concluzia
  „egress blocat" era falsă.
- `web_fetch` merge mai bine pe paginile `/docs` decât pe paginile de listare.
