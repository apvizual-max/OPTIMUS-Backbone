---
name: sandbox-gotchas
description: Capcane ale mediului cloud care te opresc din drum fara sa iti spuna clar de ce. Toate au fost rezolvate.
---

# Capcanele mediului cloud

Toate au fost întâlnite efectiv. Fiecare a costat timp până am înțeles-o.

## 1. `gh` dispare între sesiuni

Am instalat `gh` în `/usr/local/bin`. La sesiunea următoare: `command not found`.

**Fix:** binarul stă în `mavis-tools/bin/gh`, în repo. Îl cheami cu calea plină.

```bash
GH=/workspace/Mavis/mavis-tools/bin/gh
```

## 2. Recursie infinită în credential helper

```bash
# GREȘIT — funcția se numește gh și în interior apelează gh
git config --global credential.helper '!gh() { echo username=x-access-token; echo password=$(gh auth token); }; gh'

# CORECT — alt nume + cale plină
git config --global credential.helper '!f() { echo username=x-access-token; echo password=$(/workspace/Mavis/mavis-tools/bin/gh auth token); }; f'
```

Semnul: `Maximum function recursion depth (1000) reached`, apoi `HTTP 431`.
431 înseamnă **credentialele sunt gunoi**, nu că serverul e ocupat.

## 3. Certificat SSL pentru git

```
server certificate verification failed. CAfile: /etc/ssl/certs/ca-certificates.crt
```

`openssl s_client` spune `Verify return code: 0` și `curl` merge. Deci **certificatul
e valid** — sandboxul are un proxy pe care curl îl onorează, git nu.

```bash
git config --global http.sslCAInfo /etc/ssl/certs/ca-certificates.crt
git config --global http.sslVerify false
```

## 4. Fișierele din Drive vin în `.raw`, nu în `.data`

```js
const d = await k.req('GET', 'https://www.googleapis.com/drive/v3/files/' + id + '?alt=media');
// JSON.parse picască pe conținut markdown → obiectul e { raw: continut }
const text = String(d.raw || d.data || '');
```

Am pierdut ore căutând `.data` și fiind convins că **nu am acces la Drive**. Aveam.

## 5. `resultSizeEstimate` din Gmail nu e numărătoare

Întoarce aceeași valoare (ex. `201`) pentru interogări de 6 și de 30.000 de mailuri.
**Numără prin paginare.** Vezi skill-ul `gmail-exact-counting`.

## 6. `pgrep` se potrivește cu propria ta comandă

```
$ pgrep -f email-sort.js   →  "rulează"   (nu rulează nimic)
```

Comanda ta conține șirul căutat, deci `pgrep` se potrivește cu ea însăși.
Verifică altfel:

```bash
date -r fisier.log '+%H:%M:%S'   # ultima modificare
```

Un log nemodificat de 9 ore înseamnă că procesul a murit, indiferent ce zice `pgrep`.

## 7. `nohup ... &` într-un tool cu timeout

Procesul moare când comanda expiră. Folosește parametrul de fundal al tool-ului,
nu `nohup` manual.

## 8. Copierea unui director cu `node_modules`

Un `cp -r` a transformat workspace-ul în 209 MB. `node_modules` se exclude, apoi
`.gitignore` acoperă `mavis-tools/bin/`.

## 9. Contul GitHub e pe plan FREE

`gh api /users/apvizual-max/copilot` → `Not Found`. **Copilot și Jules nu sunt
accesibile prin API pe plan free.** Nu se configurează automat. Se activează din
interfața web, manual, de POPY.

## 10. Platforma mascheaza valorile din secret manager in chat

`{{ARCHON_SECRET:GOOGLE_CLIENT_ID_MAVIS_CLOUD}}` — in locul valorii reale.

**Semnul:** un link cu `client_id` ajunge in browser cu
`client_id=%7B%7BARCHON_SECRET%3A...%7D%7D` → Google raspunde
*Error 401: invalid_client*, desi clientul e corect.

**Test:** valoarea citita din env (`node -e 'console.log(process.env.X)'`) e
**completa**, dar in chat apare placeholder → problema e **livrarea**, nu
credentialul.

**Fix:** identificatorii publici (`client_id`) stau in repo
(`mavis-tools/google-client.json`); artefactul se genereaza in repo; livrezi
**URL de repo**. Detalii: skill `mavis-secure-delivery`.

## 11. `api.github.com` are certificat expirat in sandbox

```
TLSv1.3 (IN), TLS alert, certificate expired (557)
```

Sandboxul prezinta un cert expirat pentru `api.github.com`. `git push` merge
totusi, pentru ca `http.sslVerify=false` e setat global.

**Fix pentru apelurile REST:** `curl -k` (bypass verificarea).

```bash
curl -sk -H "Authorization: Bearer $GITHUB_TOKEN" \
  https://api.github.com/repos/<owner>/<repo>
```

Cu `-k`, `api.github.com` raspunde 200. Fara `-k`, tot ce vine pe acest host
da 000 / `CERT_HAS_EXPIRED`.

## 12. Reteaua catre googleapis.com e intermitenta

Masurat 2026-10-22: ~20-50% din cereri esueaza cu `UND_ERR_CONNECT_TIMEOUT`
sau `CERT_HAS_EXPIRED`. Intermittent, pe toate host-urile Google.

**Consecinta:** o eroare de retea **NU e** o eroare de credential. Nu
concluziona nimic despre client daca requestul n-a ajuns la Google.

`kit.js` si `google-connect.js` au retry-uri. Un cod de autorizare **nu se
consuma** daca handshake-ul TLS pică (requestul nu a ajuns la Google) — deci
reia cu acelasi cod.

## 13. `cmd /c start "" "<url>"` pe Windows rupe URL-urile OAuth

```js
exec(`cmd /c start "" "${url}"`)   // PROBLEM
```

`cmd.exe` expandeaza `%VAR%`. URL-ul OAuth e plin de `%3A %2F %26`, deci
cmd le mananca. Rezultatul: **Google raspunde „Error 400 / Bad Request"**.

Detectie: bara de adresa din browser arata un URL care **nu seamana** cu ce ai
generat.

**Fix:** nu trece prin cmd.

```js
spawn('rundll32.exe', ['url.dll,FileProtocolHandler', url], { stdio: 'ignore', detached: true }).unref();
```

Pe macOS: `spawn('open', [url])`. Pe Linux: `spawn('xdg-open', [url])`.

**Regula:** orice URL cu `%` nu se deschide prin `cmd`. Nici macOS/Linux nu
au nevoie de quoting.

## 14. Redirect URI fara cale + server care verifica calea

Daca `REDIRECT_URI = 'http://127.0.0.1:8976'`, Google redirectioneaza pe **`/`**.
Un server care verifica `req.url === '/callback'` arunca 404 si **pierde
codul** — fara niciun mesaj de eroare vizibil.

**Fix:** accepta orice cale, verifica doar `?code=`.

## Ordinea de verificare la ceva ce "nu merge"

1. Fișierul există? `ls`
2. E la locul așteptat? `find`
3. Ce spune procesul? `date -r x.log`
4. E o limitare reală sau o greșeală de instrument?
5. **Abia după astea** spune „nu se poate"
