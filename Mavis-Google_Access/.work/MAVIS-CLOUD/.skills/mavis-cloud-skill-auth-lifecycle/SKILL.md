---
name: mavis-cloud-skill-auth-lifecycle
description: Ciclul de viata al autentificarii Google pentru Mavis Cloud - cum re-autentifici, cum detectezi daca appul OAuth e publicat, cum eviti degradarea scope-urilor si cum repari un token mort. Trigger-uri: "re-autentifica", "token expirat", "invalid_grant", "invalid_client", "publica app", "Testing", "production", "7 zile", "scope-uri lipsa".
---

# Auth — ciclul de viață al tokenului

## Diagnosticul în 6 pași

```bash
node mavis-tools/google-preflight.js
```

```
[0] drift client_id   OK    env si repo coincid
[1] credentiale       OK
[2] client la token   OK
[3] client la auth    OK
[4] refresh token     OK
[5] expirare          fara limita de 7 zile  (appul e IN PRODUCTION)
[6] scope-uri         OK    (27, identice cu lista canonica)
```

**Coduri de ieșire:** `0` = totul ok · `1` = client greșit · `2` = token mort /
fără token · `3` = rețea.

---

## Cele 4 erori, cu diagnosticul lor

| Eroare | Ce înseamnă | Ce faci |
|---|---|---|
| `invalid_client: The OAuth client was not found` | client_id greșit sau inexistent | verifică `mavis-tools/google-client.json` + Cloud Console → Credentials |
| `invalid_grant: Malformed auth code` | codul nu e pt acest client | regenerează linkul cu același client |
| `invalid_grant: Token has been expired or revoked` | token real, dar mort | re-autentificare (mai jos) |
| `CERT_HAS_EXPIRED` / `UND_ERR_CONNECT_TIMEOUT` | **proxy de sandbox**, nu credentiale | retry; nu atinge tokenul |

---

## Cum detectezi dacă appul e publicat

Răspunsul la `POST oauth2.googleapis.com/token` conține
`refresh_token_expires_in` **doar când consent screen-ul e în „Testing"**
(limita de 7 zile). După publicare, câmpul **dispare**.

```js
if (j.refresh_token_expires_in === undefined) → IN PRODUCTION, fără limită de 7 zile
else → încă Testing, expiră la +refresh_token_expires_in
```

**Măsurat 28 oct 2026: appul e în „In production".** Precondiție: tokenul trebuie
să fie **viv** la momentul consimțământului, altfel Google nu întoarce câmpul.
**Câmpul e șters de Gmail după re-consimțământ** → la fiecare re-auth, măsoară
din nou. O valoare veche de 604800 nu dovedește că appul e încă în Testing.

---

## Re-autentificarea

**1. generează linkul** (îl scrie, comitează și împinge singur):
```bash
node mavis-tools/google-refresh.js link
```
Dă-i lui POPY **URL-ul de repo**, nu linkul:
`https://github.com/apvizual-max/MAVIS-CLOUD/blob/main/18-GOOGLE/AUTORIZARE-LINK.txt`

**2. POPY** deschide linkul → Allow → copiază bara de adresa (are `?code=…`).

**3. schimb codul:**
```bash
node mavis-tools/google-refresh.js code "<url cu ?code=...>"
```

**4. scrie tokenul** în secret manager, ca `GOOGLE_REFRESH_TOKEN_MAVIS_CLOUD`,
**prin tool-ul `secret`** — niciodată în chat.

**5. verifică:**
```bash
node mavis-tools/google-verify.js
node mavis-tools/google-preflight.js
```

### Reguli critice

- **Linkul nu se trimite prin chat.** Platforma maschează valorile din secret
  manager în `{{ARCHON_SECRET:…}}` → browserul primește placeholder →
  `Error 401: invalid_client`. **Aceasta a fost cauza rădăcină a problemei
  inițiale**, costând o sesiune de diagnosticare.
- **`prompt=consent` revocă tokenul anterior.** E o operație single-writer:
  nu rulezi doi agenți în paralel pe același client.
  `google-refresh.js` folosește automat `prompt=select_account` (non-revoking)
  când există un token viu.
- **Nu trimite codul prin chat nici el** — e un credential de unică folosință.

---

## Publicarea appului (doar POPY poate)

Cloud Console → APIs & Services → OAuth consent screen → **Publish app** →
**In production**. Checklist: `docs/GOOGLE-PRODUCTION-CHECKLIST.md`.

După publicare, **un consimțământ nou e necesar o singură dată** — tokenul
obținut *înainte* de publicare păstra limita de 7 zile.

---

## Degradarea scope-urilor — capcana care a fost închisă

Până la 28 oct 2026, **cinci scripturi aveau fiecare lista lui de 6 scope-uri**.
Orice re-consimțământ generat de ele ar fi adus un token degradat, pierzând
`gmail.settings.basic` (→ filtrele Gmail n-ar mai fi reparabile din cloud).

**Regula permanentă:** lista de scope-uri trăiește **doar** în
`mavis-tools/google-scopes.js`. Scripturile importă din el. Dacă un workflow
nou cere un scope, îl adaugi ACOLO, cu motiv, apoi regenerezi linkul.

**Control:** pasul `[6]` din preflight compară scope-urile tokenului cu lista
canonică și raportează `DRIFT` + ce lipsește. Deci degradarea se vede
**înainte** să se întâmple.

## Legături

Skill central: `mavis-cloud-google-access-bot` · sibling: `mavis-cloud-skill-security`,
`mavis-cloud-skill-verification`
