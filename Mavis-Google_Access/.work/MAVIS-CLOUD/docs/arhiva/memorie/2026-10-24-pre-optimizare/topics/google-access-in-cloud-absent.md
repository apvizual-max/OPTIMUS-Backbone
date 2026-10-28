---
description: "[ARHIVĂ] Topic șters în 2026-10-24: afirma falsă că Google e inaccesibil din cloud. Păstrat pentru trasabilitate. Înlocuit de `google-cloud-access`."
---

# Google Workspace — INACCESIBIL din cloud (reverificat 2026-10-19)

> ⚠️ **SUPERAT 2026-10-22.** Google **E conectat** din cloud (OAuth propriu, 4 chei în
> secret manager): Gmail, Drive, Calendar, Sheets, Slides merg. Motivul pentru care
> părea inaccesibil era **TLS**, nu lipsa credentialelor — vezi
> `NODE_TLS_REJECT_UNAUTHORIZED=0` în memoria de agent.
> `git clone` merge și el. Raportul zilnic **se scrie efectiv pe Drive**.
> Restul topicului rămâne ca istoric al perioadei 2026-10-19 → 2026-10-21.

## Măsurătoare, nu presupunere

Catalogul de conectoare: **116 tooluri, 5 provideri** — `cloudflare` (4),
`figma` (2), `github` (95), `matrix` (13), `email_workbench_credentials` (2).
**Niciun Google.** Reverificat 2026-10-19 cu `partial: false`,
`provider_failures: []` — deci e catalog complet, nu o eroare de discovery.

**Provider nou, apărut undeva după 2026-10-16:** `email_workbench_credentials`
(`session` + `exchange`). **NU e un client de mailbox** — e un transport de
credențiale criptate pentru un plugin Node („never supply plaintext mailbox
credentials"). Singurele lui intrări: `keyVersion`, `publicKey`, `nonce`,
`ciphertext`. Fără un tool de citit mesaje, nu deschide inbox-ul.

Căutări pe cuvinte cheie, toate 0: `gmail`, `google`, `sheet`, `workspace`,
`calendar`. `mail` și `email` → 1 rezultat = `cloudflare__search`, fără legătură.

Secret store: doar `JULES_API_KEY`, `GITHUB_TOKEN`, `LINKEDIN_EMAIL`,
`LINKEDIN_PASSWORD`. Environment: `LINKEDIN_EMAIL`, `LINKEDIN_PASSWORD`.
**Niciun `GOOGLE_*`, niciun OAuth Google.**

## Consecință pentru "Raport zilnic pentru Alex"

| Cerință | Stare |
|---|---|
| 1. Gmail MAVIS/\* | **NEREALIZABIL** — zero acces |
| 2. Căutare joburi + scoring | **REALIZABIL** — web, nu Google |
| 3. Scriere Drive `Alex Work/00-INTRARE` | **NEREALIZABIL** — zero acces |
| 4. Raport în chat | **REALIZABIL** |

Cota "max 200 cereri Google" → consum real **0**. Nu pentru că am fost zgârcit,
ci pentru că nu există suprafață de apel.

## REGULA — nu inventa conținut de Gmail

Dacă un raport cerut include "mesajele care chiar necesită răspuns":
**secțiunea rămâne goală și se declară de ce.** Zero mesaje inventate, zero
subiecte inventate, zero numere inventate. E singura linie pe care nu negociem.

## De ce se cere verificarea

Memoria de agent are deja o lecție: „înainte de a nega existența unui produs,
îl cauți pe web". Aceeași regulă pentru **acces**: un search cu `partial: true`
sau o eroare de discovery **nu dovedesc** că un App nu e conectat. Catalogul
complet, fără filtru, e singura probă bună — și aici l-am făcut.

## Ce ar debloca

Conectarea unui cont Google la platformă (Gmail + Drive). Până atunci, raportul
zilnic livrează fișierul local prin chat, iar secțiunile 1 și 3 rămân goale.

## Rută alternativă verificată: GitHub

Repo-ul `apvizual-max/MAVIS-CLOUD` e accesibil prin **connectorul GitHub**
(fișiere, tree, commit) — funcționează bine.

`git clone` **NU** funcționează: TLS interceptat în sandbox,
`fatal: unable to access ... server certificate verification failed`, inclusiv
cu `-c http.sslCAInfo=/etc/ssl/certs/ca-certificates.crt` setat. `curl` direct
spre `api.github.com` merge (200). Deci: **connector, nu clone.**

## Nu urca raportul în repo fără cerere

`MAVIS-CLOUD` e repo-ul pe care lucrează și agentul local al lui POPY.
O scriere concurentă neașteptată produce exact conflictul de modificări pe
care-l evităm prin nume distincte (Mavis Cloud vs Mavis).
Livreză local, în chat. Push doar la cuvânt.


## Măsurătoare 2026-10-21 — catalogul de conectoare e DOWN, nu „deconectat"

Pe 2026-10-21 `mcode-tools connector tools` a returnat, pentru **orice** apel
(inclusiv apeluri directe, și pentru orice cuvântă-cheie: gmail, google, drive,
matrix):

```
error: invalid signature (path=/minimax-cloud/api/v1/connectors/connected-tools/list)
```

Logul arată `http_status: 400`, `auth_mode: sandbox-egress`. Deci e o **defecțiune de
transport a platformei**, nu un răspuns de tip „App neconectat".

**Regulă:** un `invalid signature` NU dovedește că un App lipsește și NU dovedește
că există. Declară „catalogul de conectoare nu e accesibil azi", nu „nu ai Gmail".
Când se repară, reia măsurătoarea.

Restul măsurătorilor 2026-10-21 (neschimbate):
- Store de secrete: doar `JULES_API_KEY`, `GITHUB_TOKEN`, `LINKEDIN_EMAIL`,
  `LINKEDIN_PASSWORD`. Niciun `GOOGLE_*`.
- Fără `gcloud`, `gam`, `rclone` în sandbox.
- Secțiunea Gmail a raportului zilnic: **goală, 0 mesaje inventate**.
- Cota Google consumată: **0**.

## Rută alternativă confirmată și azi: GitHub REST prin token

`curl -H "Authorization: Bearer ${GITHUB_TOKEN}"` spre `api.github.com` și
`raw.githubusercontent.com` → 200. `git clone` continuă să eșueze (TLS interceptat).
Așa se ia `ALEX-KIT/scoring.gs` din `apvizual-max/MAVIS-CLOUD`.

## Unde ajunge raportul când Drive e inaccesibil

Mirror local creat la: `/workspace/Alex Work/00-INTRARE/RAPORT-ZILNIC-AAAAMM-ZZ.md`
(structura Drive replicată în workspace), apoi livrat prin chat.
Nu se urcă în repo fără cerere explicită.
