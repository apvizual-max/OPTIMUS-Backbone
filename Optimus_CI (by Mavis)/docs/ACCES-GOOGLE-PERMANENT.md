# ACCES GOOGLE — de ce nu mai trebuie re-autentificare (2026-10-27)

> **SOT al problemei**: accesul Google pe mașina lui Popy.
> **Stare măsurată**: reparat, cu mecanism, fără niciun clic în browser.
> **Instrumentele**: `C:\Users\apviz\.minimax-agent\projects\google-layer\`
> (namespace **Mavis / minimax**, nu Hermes).

---

## 1. Simptomul

Popy, citit: *„de ce nu am deja acces și de ce nu mă pot baza și folosi
setările când le fac odată … nu pot lucra că tu IAR NU AI ACCES … de fiecare
dată iar te loghezi și te autentifici."*

Cuvintele-cheie: **de fiecare dată**. Nu „o dată nu a mers" — o buclă.

---

## 2. Cauza, măsurată (nu presupună)

Mașina are **două granturi OAuth Google**, și fiecare server MCP citește
**propriul magazaur**:

| Magazaur | Scris | Rezultatul exchange-ului | Stare |
|---|---|---|---|
| `~/.config/gws/mcp-secrets.json` → `gdrive-mcp/refresh_token` | 6 oct | HTTP **400** `invalid_grant` | **MORT** |
| `~/.google-mcp/tokens/apvizual.json` → `refresh_token` | 24 oct | HTTP **200**, `expires_in=3599` | **VIU** |

Verificări care exclud explicațiile ieftine:

- **Contul**: același (`apvizual@gmail.com`).
- **Clientul OAuth**: același `client_id`
  (`1068987308935-…apps.googleusercontent.com`).
- **Client secret**: același — comparat prin SHA-256, toate trei surile
  `00E7CD8ABE288488`.

Deci: contul e OK, clientul e OK, aplicația e OK. **Un singur grant a fost
revocat sau expirat** — și totuși simptomul era „trebuie să te autentifici".

**Cauza reală:** nimeni nu copiase grantul viu în magazaurul mort. Fiecare
server își citește cutia lui, iar cutia lui era goală sau moartă.

**Cine mai cerea autentificare, și de ce:**

| Server | Mecanism | De ce cerea |
|---|---|---|
| `gdrive-mcp` | `Bun.secrets.get` → shim → `mcp-secrets.json` | magazaurul lui era **mort** |
| `gmail-mcp` | `process.env.GOOGLE_ACCESS_TOKEN` (stdio) | un access token trăiește **~1 oră**; nu poate fi durabil |
| `google-calendar-mcp` | `GOOGLE_CLIENT_ID/SECRET` + `token.json` în **cwd** | token.json într-un cwd nestabil → nu e găsit → cere login |
| `google-workspace-mcp` | `~/.google-mcp/tokens/` | **OK** — era singurul cu grant viu |

---

## 3. Repararea: un singur grant viu → toți serverii

### 3.1 Principiul

> **Nu se cere consent cât timp există un grant viu pe mașină.** Consentul
> e necesar doar când nu există **niciun** grant viu nicăieri — o situație
> diferită și rară.

### 3.2 Instrumentele

| Fișier | Rol |
|---|---|
| `google-grant.js` | **modulul comun**: găsește toate granturile, le **măsoară**, publică grantul viu |
| `google-auth-hub.js` | CLI: rulează provisionarea și raportează |
| `verify-google-credentials.js` | proba independentă: măsoară + verifică Drive |
| `mcp-probe.js` | proba **live**: handshake MCP real + apel de tool real |
| `gdrive-launcher.js` | pornește gdrive-mcp, **auto-vindecându-se** la fiecare pornire |
| `gmail-launcher.js` | pornește gmail-mcp cu un access token **nou**, cumpărat din grantul durabil |
| `calendar-launcher.js` | pornește calendar-mcp cu `token.json` în directorul corect |

### 3.3 Ce s-a măsurat după reparare

```
verify-google-credentials.js:
  REFRESH_EXCHANGE_HTTP=200
  DURABLE_GRANT=VALID
  DRIVE_ABOUT_HTTP=200   account=apvizual@gmail.com
  LIVE  google-workspace-mcp ... expires_in=3599s
  LIVE  gdrive-mcp ...          expires_in=3599s
  RESULT=ALL_OK
```

```
google-auth-hub.js:
  PROVISIONED gdrive-mcp store -> C:\Users\apviz\.config\gws\mcp-secrets.json  (updated)
  RESULT=PROVISIONED
```

```
mcp-probe.js:
  PASS gdrive-mcp  step=tool_call  tools=9
       OK: Found 3 file(s): dashboard_data.js ... Owner: Alexandru Popescu
  PASS gmail-mcp   step=tool_call  tools=36
       OK: { "emailAddress": "apvizual@gmail.com", "messagesTotal": 83443, ... }
  RESULT=ALL_PASS
```

**Asta e dovada**: handshake MCP complet și apel de tool real, cu date reale
(3 fișiere în Drive, owner „Alexandru Popescu"; 83.443 mesaje în Gmail).

---

## 4. Falsificarea: mecanismul trebuie să **refuze**

Un mecanism care scrie orbește nu e o reparație, e o grijă mai bună.

Probă: cu `FAKE_HOME` temporar, ambele magazauri conțin **numai** un refresh
token mort:

```
candidates found: 2
  DEAD    gdrive-mcp ...              invalid_client
  DEAD    google-workspace-mcp ...    invalid_client
RESULT=NO_LIVE_GRANT - niciun grant de pe masina nu mai e acceptat de Google.
CONSENT_NEEDED=yes - ACESTA e singurul caz in care Popy trebuie sa re-autentifice.
EXIT=1
store_refresh_still_dead=True      <- nu s-a scris nimic
```

**De ce contează:** fără această falsificare, „hub-ul a scris un token" ar
fi putut însemna „hub-ul a scris un token care nu funcționează".

---

## 5. Ce s-a schimbat în configurație

| Server | Înainte | Acum |
|---|---|---|
| `gdrive-mcp` | launcher fără auto-vindecare | `gdrive-launcher.js` — **auto-vindecător** |
| `gmail-mcp` | `dist/main.js` direct (cerea token în env, imposibil) | `gmail-launcher.js` — token nou la fiecare pornire |
| `google-calendar-mcp` | `bin/run.js` (nu e server stdio) | **dezactivat** — măsurat: e server HTTP pe portul 3000; un entry stdio nu poate face handshake. E și redundant (workspace-mcp acoperă Calendarul) |
| `google-workspace-mcp` | neatins | neatins — era singurul cu grant viu |

`google-calendar-mcp` rămâne dezactivat **pentru că măsurarea o spune**, nu
pentru că aș prefera: `calendar-launcher.js` a fost scris și rulat, iar
importul a eșuat cu `ERR_UNSUPPORTED_ESM_URL_SCHEME` — serverul pornește pe
HTTP, nu pe stdio.

---

## 6. Limită declarată

Grantul viu are scope **mai larg** decât cerea inițial `gdrive-mcp`
(`drive.readonly`): acum include `drive` complet + `gmail.modify` +
`calendar` + `documents` + `spreadsheets` + `presentations`.

Asta e un **trunchiut deliberat**: un consent deja dat de Popy, în loc de un
al doilea ecran de consent. Scope-ul este **raportat**, nu ascuns.

---

## 7. Cum verifici singur, oricând

```
node C:\Users\apviz\.minimax-agent\projects\google-layer\verify-google-credentials.js
node C:\Users\apviz\.minimax-agent\projects\google-layer\mcp-probe.js
```

Primul spune dacă **credentialele** sunt vii. Al doilea spune dacă
**serverele** chiar funcționează. Diferența e importantă: un magazaur
populat nu e acces.

---

*2026-10-27 · Mavis Local · măsurat · falsificat · namespace minimax (nu Hermes)*
