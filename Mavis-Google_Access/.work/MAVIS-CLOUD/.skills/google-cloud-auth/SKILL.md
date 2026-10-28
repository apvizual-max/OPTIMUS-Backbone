---
name: google-cloud-auth
description: Cum conectezi Mavis Cloud la Google (Drive, Gmail, Calendar, Docs, Sheets, Slides) cu credentialele proprii. Când cauți chei Google lipsă, eroare invalid_grant, sau "de ce nu văd credentiale Google".
---

# Google Cloud Credentials

Google pentru Mavis Cloud = **OAuth propriu, cu 4 chei în secret manager**.
Nu conector nativ (nu există în Marketplace MiniMax).

## Cele 4 chei

Accepta si forma cu sufix: `GOOGLE_CLIENT_ID_MAVIS_CLOUD`, `GOOGLE_CLIENT_SECRET_MAVIS_CLOUD`,
`GOOGLE_REFRESH_TOKEN_MAVIS_CLOUD`.

```
GOOGLE_CLIENT_ID      = <client id, forma xxx.apps.googleusercontent.com>
GOOGLE_CLIENT_SECRET  = <client secret>
GOOGLE_REFRESH_TOKEN  = <1//...>
GOOGLE_EMAIL          = apvizual@gmail.com
```

Nu se scriu în repo, în chat, sau prin Jules/GitHub.

## Ordinea fluxului

1. **Local, cu browserul** — `node mavis-tools/google-setup.js`
   - deschide browserul, consimțământ, scrie `~/.google-mcp/tokens/mavis.json`
   - scrie `~/.google-mcp/cloud-secret.env` cu cele 4 linii `CHEIE=VALOARE`
2. **POPY copiază** cele 4 linii în secret manager (Mavis Cloud)
3. **Cloud** — `node mavis-tools/google-verify.js`
   - verificare read-only, un cod HTTP real per serviciu
4. **Local și Cloud folosesc același `kit.js`** — diferă doar unde stau cheile

## Diagnostic rapid

**PRIMUL PAS, întotdeauna:** `node mavis-tools/google-preflight.js`
→ un singur verdict: credentiale / client la token / client la authorize / token viu.
10 secunde. Nu mai cheltui ore cu „de ce nu merge".

| Simptom | Cauză | Repar |
|---|---|---|
| `lipsesc: GOOGLE_CLIENT_ID, ...` | cheile nu sunt în secret manager | pasul 2 |
| `Error 400: invalid_scope` | API-ul unui scope **nu e activat** în proiectul Cloud (de ex. Photos Library API). Google nu te redirecționează înapoi → scriptul aștepta | activează API-ul în Cloud Console, apoi `--with-photos`; sau rulează fără Photos (default) |
| `invalid_grant` | app-ul OAuth e în **Testing** → tokenul moare în 7 zile; **sau** client_id și refresh_token din clienti diferiți | `Publishing status → In production`, apoi reia `google-setup.js` |
| **`Error 401: invalid_client` / „The OAuth client was not found" in browser** | **client_id din secret manager apartine ALTUI client** (ex. al unui alt CLI) — sau clientul a fost sters | vezi „Capcana client_id" mai jos |
| `HTTP 403 insufficient authentication scopes` | scope lipsește | reia `google-setup.js` cu scope-ul complet |
| `HTTP 404` la Docs/Sheets/Slides | host greșit | `docs.googleapis.com` / `sheets.googleapis.com` / `slides.googleapis.com` — **nu** `www.googleapis.com` |
| `http=000` pe photos sau `*mcp.googleapis.com` | host blocat de egress din cloud | rulează de la Local |
| `Client network socket disconnected before secure TLS` | `https.request` nu onoreaza proxy-ul de sandbox — **pare** "nu am acces" dar e fals | folosește `fetch` (fixat in `kit.js`, commit `0d5bfe5`) |

## Capcana client_id — 2026-10-22 (a costat 3 ore)

Secretul manager tinea `client_id` + `client_secret` de la **un alt client**
(al lui Hermes CLI). Tablul se poate **simula** perfect:

| Endpoint | Ce a raspuns | Ce pare |
|---|---|---|
| token | `invalid_grant: Bad Request` | „tokenul e mort, totul e bine" |
| authorize (browser) | `Error 401: invalid_client` | „am dat un link stricat" |

**Deci: `invalid_grant` la token NU dovedeste ca clientul e corect.**
Clientul strain si clientul bun dau același raspuns pe calea token.

**Testul care chiar separa:** cere un cod de autorizare **fals**
(`grant_type=authorization_code`, `code=FAKE`):
- `invalid_grant: Malformed auth code` → clientul + secretul sunt **ok**
- `invalid_client: The OAuth client was not found` → clientul **nu e cel bun**

**Al doilea test, la authorize endpoint** (fara login, cu `redirect: manual`):
clientul rezolvat → redirectul contine `opparams=` si `dsh=`; clientul strain
→ redirect scurt, fara ele. Comparator instant, fara sa-l deranjez pe POPY.

**Reguli:**
- **Niciun `client_id` hardcodat** in repo. Fara exceptie. (A stat unul, a
  fost cauza. `google-link.js` acum se opreste cu mesaj daca lipseste.)
- Verifica **mereu** client_id-ul din secret manager cu cel din
  Cloud Console → Google Auth Platform → Clients, **inainte** de orice link.
- Un client poate fi sters din consola; se poate restaura pana la 30 de zile.
- Retelua din cloud pica ~1 din 5 cereri. `kit.js` si `google-connect.js` au
  retry. Un cod de autorizare e de unica folosinta — nu-l consuma pe un timeout.

## Testul decisiv: cine e mort, clientul sau tokenul?

**ATENTIE: `invalid_grant` cu token fictiv NU dovedeste ca clientul e valid.**
Controlul l-am facut: un `client_id` complet strain + secret strain + token
fictiv da tot `invalid_grant`. Deci raspunsul asta nu separa nimic.

Testul care separa, la **token endpoint** — cere un cod de autorizare fals:

| # | Ce trimiți | Răspuns | Concluzie |
|---|---|---|---|
| 1 | client_id + secret reali, `grant_type=authorization_code`, `code=FAKE` | `invalid_grant: Malformed auth code` | clientul + secretul **valide** |
| 2 | client_id + secret **falsi** | `invalid_client: The provided client secret is invalid.` | control — secretul chiar se verifica |
| 3 | **client_id strain** + secret real | `invalid_client: The OAuth client was not found.` | control — clientul chiar se verifica |
| 4 | client_id + secret reali, `refresh_token` **real** | `invalid_grant: Token has been expired or revoked.` | **tokenul e mort** |

Daca 1 da `invalid_grant` si 4 da la fel → **doar tokenul** e problema.
Daca 1 da `invalid_client` → clientul din secret manager e cel gresit.
Nu re-face setup-ul de la zero inainte de a rula testul asta.

`google-preflight.js` ruleaza exact aceste teste si iti da verdictul intr-un
rand. Ruleaza-l **intotdeauna** inainte de orice operatiune Google.

## Bucla „7 zile" — de ce se repetă

Măsurat 2026-10-22: setup-ul făcut pe 2026-10-21 pusese în secret manager
**tokenul vechi, deja mort**. Consimțământul era din ~2026-10-09, app-ul era în
**Testing** → tokenul expira în jur de 2026-10-16.

Bucla: re-setup → token nou → moare în 7 zile → re-setup → …

**O singură regulă:** înainte de orice consimțământ nou,
`Publishing status → In production`. Altfel nu ai reparat nimic, doar ai mutat
ceasul. Statusul măsurat + fixul exact: `docs/GOOGLE-STATUS-2026-10-22.md`.

## Scope-uri

**Implicit (6, funcționează fără API-uri suplimentare):** drive, gmail.modify, calendar,
documents, spreadsheets, presentations.

**Opțional:** `photoslibrary.readwrite` — **doar** cu `--with-photos` și **doar** dacă
Photos Library API e activată în proiect. Altfel Google răspunde `invalid_scope`.

## Regula „7 zile"

OAuth consent screen în **Testing** → refresh token-ul expiră în 7 zile.
Excepție doar pentru `userinfo.email` / `userinfo.profile` / `openid` — nu ne interesează.
Fix: `Publishing status → In production`. Atunci tokenul nu expiră (decât revocat sau ~6 luni nefolosit).
Sursă: https://support.google.com/cloud/answer/15549945

## Regula de aur: NICIO SECRET PRIN CHAT

**Platforma mascheaza valorile din secret manager in mesajele mele.**
`GOOGLE_CLIENT_ID_MAVIS_CLOUD` ajunge la tine ca `{{ARCHON_SECRET:...}}`.

Masurat 2026-10-22: un link de autorizare trimis prin chat a ajuns in browser cu
`client_id=%7B%7BARCHON_SECRET%3A...%7D%7D` → *Error 401: invalid_client*.
Clientul era **corect** — linkul era corect, mai ales valoarea lui.

**Solutia, in ordine:**
1. **Client ID e identificator public, nu secret** → sta in repo:
   `mavis-tools/google-client.json` (sursa unica de adevar).
2. **Linkul se livreaza prin repo**, nu prin chat:
   `node mavis-tools/google-link-file.js` → scrie `18-GOOGLE/AUTORIZARE-LINK.txt`.
   POPY deschide fisierul in browser.
3. **Refresh tokenul nu trece niciodata prin chat** → merge direct in secret
   manager (fie de catre mine cu tool-ul `secret`, fie de catre POPY in panou).
4. **Codul de autorizare** e OK prin chat — nu e secret, si nu e in secret manager.

**Regula de aur:** daca o valoare vine din secret manager, **nu o scrie in chat**.
Scrie-o intr-un fisier si da-i drumul prin repo.

## PROCEDURA — cum se livreaza un link care chiar merge

Aceasta e procedura care a mers, pas cu pas. **Repeta-o identic.**

```bash
cd /workspace/mavis-cloud

# 0. (doar in sesiune NOUA) bootstrap: config git + clone + verdict
bash mavis-tools/bootstrap.sh

# 1. verifica starea — verdict pe un singur rand, ~10 secunde
node mavis-tools/google-preflight.js
#    [0] drift client_id  OK / FAIL
#    [1] credentiale      OK / TOKEN LIPSA
#    [2] client la token  OK / FAIL / INDETERMINAT (retea)
#    [3] client la auth   OK / FAIL
#    [4] refresh token    OK / FAIL
#  -> [3] FAIL = problema e clientul, NU livrarea
#  -> [4] FAIL = trebuie re-autentificare (vezi mai jos)
#  -> INDETERMINAT (retea) = NU concluziona nimic, reia mai tarziu

# 2. genereaza linkul IN REPO + commit + push, fara aprobare
node mavis-tools/google-refresh.js link
#    -> scrie 18-GOOGLE/AUTORIZARE-LINK.txt, comiteaza, impinge
#    -> iti da URL-ul de repo pe care sa-l dai lui POPY

# 3. POPY deschide linkul -> Allow -> browserul moare pe 127.0.0.1:8976 (normal)
#    -> copiaza bara de adresa cu ?code=... -> trimite prin chat (codul NU e secret)

# 4. schimba codul in refresh_token
node mavis-tools/google-refresh.js code "http://127.0.0.1:8976/?code=..."

# 5. scrie tokenul in secret manager prin tool-ul `secret` (NU in chat)
#    create --name=GOOGLE_REFRESH_TOKEN_MAVIS_CLOUD --value=<token>

# 6. verifica live
node mavis-tools/google-verify.js
```

**REGULA CRITICA — o singura sesiune re-autentifica la un moment dat.**
`prompt=consent` **revoca** refresh token-ul precedent pentru aceeasi pereche
client+utilizator (docs oficiale Google). Deci daca doua sesiuni paralele se
re-autentifica simultan, a doua omoara tokenul primei — si prima moare si ea.
`google-refresh.js` foloseste automat `prompt=select_account` (non-revoking)
cand exista un token viu; cand tokenul e deja mort, `consent` e corect
(n-avem nimic de pierdut).

Detalii: skill `mavis-secure-delivery` · doc `docs/PROCEDURA-LIVRARE-SECRETE.md`

## Cum vezi dacă appul e publicat — `refresh_token_expires_in`

Răspunsul la `POST oauth2.googleapis.com/token` conține `refresh_token_expires_in`
**doar cât timp consent screen-ul e în „Testing"** (limita de 7 zile). După
publicare, câmpul **dispare**. Deci starea appului e **măsurabilă**, nu se
ghicește:

```js
// câmp prezent  => appul e INCA IN "Testing", tokenul expiră la +refresh_token_expires_in
// câmp absent   => appul e IN PRODUCTION, tokenul nu mai are limită de 7 zile
```

`node mavis-tools/google-preflight.js` → pasul `[5] expirare` spune direct.

## Scope-urile: O SINGURA SURSA DE ADEVAR

`mavis-tools/google-scopes.js` — 27 scope-uri, fiecare cu motivul pentru care
e cerut. **Niciun script nu mai are propria listă.** Până la 28 oct 2026,
cinci scripturi aveau fiecare lista lui de 6 — deci orice re-consimțământ
generat de ele ar fi adus un token **degradat** (fără
`gmail.settings.basic` → filtrele Gmail n-ar mai fi reparabile din cloud).

**Regulă:** nu adăuga un scope într-un script. Se adaugă în
`mavis-tools/google-scopes.js` și se propagă.

**Verificare:** `node mavis-tools/google-preflight.js` → pasul **[6]** compară
scope-urile tokenului cu lista canonică și raportează `DRIFT` + ce lipsește.
Deci un downgrade se vede **înainte** să te treacă, nu după.

## Cum vezi dacă appul e publicat — `refresh_token_expires_in`

✅ **Gmail** — 83.505 mesaje · 77.701 thread-uri · 51 etichete (36 de utilizator)
✅ **Drive** — 107,80 GB / 5498 GB · 3 foldere la rădăcină
✅ **Calendar** — 4 calendare
✅ **Sheets** — "Design_Jobs_Community_Board" → 27 rânduri
✅ **Slides** — "441DPH-Brief slides…" → 7 slide-uri
⚠️ **Docs** — `docs.googleapis.com` BLOCAT din cloud (HTTP 400, pagină anti-bot
reCAPTCHA, nu JSON). **Contentul se citește prin Drive export**:
`kit.docs.text(id)` → `drive/v3/files/{id}/export?mimeType=text/plain`. Merge.
⚠️ **Photos** — `photoslibrary.googleapis.com` — API-ul e ACESIBIL din cloud, dar
tokenul n-are scope `phot library` → HTTP 403 «insufficient authentication scopes».
(S-a schimbat din «conexiune blocată».)
⛔ **Maps** — cere `GOOGLE_MAPS_API_KEY` + proiect Cloud cu billing
⛔ **Workspace MCP** — `*mcp.googleapis.com` — 0/6 conexiuni din cloud

## Trapele reparate pe 2026-10-22 (nu le mai face)

| Trapă | Simptom | Repar |
|---|---|---|
| Platforma maschează valorile din secret manager în chat | `Error 401: invalid_client` în browser | livrare prin repo (`google-link-file.js`) |
| `cmd /c start "" "<url>"` pe Windows expandează `%VAR%` | **`Error 400 / Bad Request`** — linkul stricat | `rundll32 url.dll,FileProtocolHandler` |
| Serverul verifica doar calea `/callback`, redirect_uri nu are cale | codul pierdut, scriptul nu face nimic | acceptă orice cale |
| `https.request` nu onorează proxy-ul; gateway-ul dă **certificat expirat** | `CERT_HAS_EXPIRED` | `fetch` + fallback `https.request` fără verificare |
| `docs.get` cu URL greșit `/docs/v1/` | 404 / anti-bot | `/document/v1/` + fallback prin Drive export |
| Scriptul rulează o versiune veche (fără `git pull`) | Error 400 / comportament ciudat | `git pull` înainte, mesaj în script |

**Regulă generală:** înainte să rulezi orice script Google Local:
`git pull` obligatoriu. Versiunile vechi au scope-ul `photoslibrary` inclus,
care dă `invalid_scope` → Error 400.

## Reguli

- NUNCIODATĂ ștergere definitivă. Doar Trash.
- Nu trimite mail fără comanda explicită a lui POPY, punctuală.
- Nu citi toate cheile deodată. Fiecare cheie, un singur scop.
- Cota: `list` înainte de `get`. `threads.list` (5 unități) nu `messages.get` (20).
  Vezi skill-ul `google-api-safe-scripting`.

## Fișiere

| Fișier | Ce face |
|---|---|
| `mavis-tools/google-auth.js` | rezolvarea credentialelor: env (cloud) sau fișiere (local) |
| `mavis-tools/kit.js` | clientul Google — Drive, Gmail, Calendar, Docs, Sheets, Slides, Photos |
| `mavis-tools/google-setup.js` | fluxul OAuth + generarea cheilor (rulezi la Local) |
| `mavis-tools/google-exchange.js` | transforma un cod de autorizare in refresh_token (fara browser local) |
| `mavis-tools/google-verify.js` | verificare read-only per serviciu (rulezi în Cloud) |
| `mavis-tools/test-endpoints.js` | test permanent: URL-urile API-urilor sunt corecte? |
| `docs/GOOGLE-INTEGRARE.md` | ghidul complet, cu surse |
