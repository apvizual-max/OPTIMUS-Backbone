# PERMANENTA GOOGLE - cum rămâne conexiunea vie

Problema pe care o rezolvă acest document: „de ce se cere din nou autentificare
la fiecare 2 luni?" - și răspunsul măsurat.

## Anatomia expirării

O autentificare Google nu este un lucru permanent prin nature. Ea este un
**refresh token** cu o viață, iar viața depinde de trei lucruri măsurabile:

| Factor | Ce se întâmplă | Cum se măsoară |
|---|---|---|
| **Statutul de publicare al aplicației** | În `Testing`, refresh token-ul pentru scope-uri sensibile/restricționate expiră în **7 zile**. În `In production`, nu mai expiră pe termen. | Consola → Audience → „Publishing status" |
| **Revocarea de către utilizator** | Orice revocare din contul Google invalidează tokenul imediat. | cont → Permissions → Remove |
| **Inactivitatea** | Tokenul de refresh e revocat după 6 luni fără folosire; la prima folosire se reînnoiește. | `google_auth_status` din container |

## Cum stai acum

- Statut: **In production** (publicat 27 oct 2026, 08:50 UTC).
- Grant: **33 scope-uri** (era 30 la redactarea primei versiuni a acestui
  document; 32 după consimțământul #3, 33 după scope-ul Photo Picker), token de
  refresh în volum, emis după publicare.
- Consumul tokenului: `mintAccessToken()` citește credentialul **la fiecare
  apel** (`readCreds()` per request) → un credential nou e preluat fără
  restart, dar restartul e oricum sigur și e făcut automat de ascultător.

## Când cere Google re-autentificare (și cum se repară în 1 minut)

Containerul **nu ascunde** problema. `google_auth_status` raportează
`reauth_required`, iar orice uneltă care lovește o API cu token mort întoarce
`GOOGLE_HTTP_401: invalid_grant` - nu un stack trace.

Repararea e automată până la un singur click:

1. `node container/mcp-call.mjs google_scope_upgrade "@args.json"` → tipărește
   **un singur URL** de consimțământ, cu toate scope-urile într-o singură
   cerere.
2. Se deschide URL-ul în browserul deja autentificat → **Allow** (un singur
   click, al utilizatorului; eu nu pot apăsa butonul de autorizare).
3. `container/consent-watcher.mjs` rulează pe `http://localhost:80`: preia
   codul, îl schimbă cu **același client** și **același redirect_uri**,
   publică credentialul în volum, repornește containerul și rulează proba.
4. `data/consent-result.json` + `data/last-probe.txt` spun exact ce s-a
   întâmplat.

Deci: **un click**, nu o procedură. Nu există niciun cod de copiat, nicio
comandă de rulat de către utilizator.

## De ce nu se cere la fiecare 2 luni (mecanismele reale)

- **Clientul e Desktop**, nu Web. Redirectul e loopback (`http://localhost`),
  deci nu există niciun secret de client în fluxul de utilizator.
- **Un singur credential**, într-un volum montat. Containerul nu are nevoie
  de fișierul secret și nu-l caută la fiecare pornire.
- **Tokenul e proaspăt la fiecare apel** (refresh silent, prin `refresh_token`
  grant). Cheia de refresh nu e legată de o sesiune de browser.
- **Aplicația e în producție**, deci nu mai există expirarea de 7 zile.
- **Watchdog**: `container/watch-reauth.ps1` + notificarea ntfy detectează
  `reauth_required` și semnalează; nu re-autentifică singur (autorizarea e
  fizică, nu automată), dar face tot restul.

## Ce NU este rezolvat de automatizare

- Clickul de autorizare Google rămâne al utilizatorului. Politica runtime o
  cere (OAuth consent = autorizare fizică) și e corect: niciun agent nu ar
  trebui să apese „Allow" pe contul altcuiva.
- Dacă Google revizuiește sau retrage aplicația, se re-cere un click. Nu
  există nicio modalitate de a evita asta fără a falsifica identitatea
  utilizatorului.

## NotebookLM / ExtendLM - a doua expirare, rezolvată altfel

Grantul Google nu e singura expunere. Tokenul ExtendLM (NotebookLM prin MCP)
expiră în **ore**, nu în luni, iar endpoint-ul **rotește** refresh token-ul.

Cum e rezolvat, măsurat (27 oct 2026):

| Piesa | Mecanism |
|---|---|
| rotația | `extendlmAccessToken()` în container: reînnoire cu deviere de 120 s, scriere atomică |
| unicitatea rotației | un singur proprietar (hostul). Runnerul Cloud are `GA_EXTENDLM_NO_REFRESH=1` și doar consumă snapshotul |
| transportul spre Cloud | `scripts/publish-extendlm-secret.mjs` publică snapshotul în secretul `GOOGLE_EXTENDLM_CREDENTIAL_B64` și **citește înapoi** timestamp-ul |
| continuitatea | taskul Windows `MavisExtendLMHeartbeat` (30 min) - măsurat declanșat: `LAST_RESULT=0` |
| vizibilitatea | `logs/extendlm-heartbeat-YYYY-MM-DD.log`, o linie datată per rulare, tokenul **redactat** |

Cloudul rulează zilnic (`cron 17 6 * * *`) sau la cerere, construiește imaginea
din sursa publică și probează API-urile reale: run `40497337673` → `success`,
`notebooklm` **OK**, `PROBE_EXIT=0`.

## Cloud - ce rulează și cine îl rulează

`MAVIS-CLOUD/.github/workflows/google-access.yml`: clonează sursa publică,
materializează credentialul din secret, construiește imaginea, pornește
containerul și **probează API-urile reale** (nu verifică o listă de scope-uri).

De ce nu rulează pe `pull_request`: un secret nu trebuie să fie accesibil dintr-o
pull request. De ce workflow-ul e **compus**, nu copiat: `scripts/rebuild-cloud-workflow.py`
pornește de la versiunea demonstrată funcțional și verifică proprietățile
(BOM-strip, pas de diagnostic, absența triggerului `pull_request`) înainte de
a scrie - o copie „mai nouă" înseamnă aici „mai veche" decât istoricul ei.

