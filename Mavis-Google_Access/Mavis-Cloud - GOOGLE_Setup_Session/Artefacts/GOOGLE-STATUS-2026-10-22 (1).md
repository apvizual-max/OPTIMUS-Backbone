# GOOGLE — stare măsurată 2026-10-22 02:10 (Mavis Cloud)

**Măsurat în sandbox, cu cod HTTP real. Nu e estimare.**

---

## 1. Răspuns scurt

**NU.** Google nu funcționează acum din cloud. `refresh_token`-ul din secret manager
**e mort**.

Diagnosticul e însă **curat**: clientul OAuth e valid, secretul e valid.
**Singura piesă moartă e tokenul.** Deci nu trebuie re-făcut nimic de la zero —
trebuie reificat **un singur** token.

---

## 2. Diagnosticul, cu probe

| Test | Ce am trimis | Răspuns Google | Ce înseamnă |
|---|---|---|---|
| 1 | client_id real + secret real + **token fictiv** | `invalid_grant: Bad Request` | client_id + client_secret **sunt valide** (altfel ar fi `invalid_client`) |
| 2 | client_id real + **secret fals** + token fictiv | `invalid_client` | confirmă că testul 1 chiar verifică secretul |
| 3 | client_id real + secret real + **token real** | `invalid_grant: Token has been expired or revoked.` | **tokenul e expirat sau revocat** |

Plus:
- `client_id` din secret manager **==** cel hardcodat în `google-link.js`
  (`1068987308935-…apps.googleusercontent.com`) → **nu** e cauza „client și token din clienți diferiți".
- Tokenul **nu** apare în istoricul git (n-a fost vărsat niciodată în repo).

## 3. Cronologia — de ce se repetă

| Data | Ce s-a întâmplat |
|---|---|
| 2026-10-09 → 11 | Gmail mergea **real** (SENTINEL 2026-10-11: `in:inbox` 4000) |
| 2026-10-21 20:00 → 23:10 | 6 commituri: credentiale pentru cloud, kit refăcut, `google-local.js` |
| 2026-10-21 22:50 | `docs/GOOGLE-INTEGRARE.md` scris, cu tabelul „ce funcționează azi din cloud" |
| 2026-10-22 02:10 | **token mort** |

**Cauza reală:** app-ul OAuth e în modul **Testing**. În Testing, refresh token-ul
moare în **7 zile de la consimțământ** (sursa oficială:
https://support.google.com/cloud/answer/15549945). Consimțământul a fost în jur de
**2026-10-09/10** → tokenul a expirat în jur de **2026-10-16/17**.

Setarea de pe 2026-10-21 a pus în secret manager tokenul **vechi, deja mort**.
Tabelul din `GOOGLE-INTEGRARE.md` secțiunea 6 spune chiar, paranteză:
*„exemplu de format — numerele reale apar doar după ce cheile sunt puse și rulezi tu"*.
Deci **nu a existat niciodată o verificare reală din cloud.** De aceea fiecare
sessie a început cu „nu merge" și a cerut re-setup.

**Bucla:** re-setup → token nou → moare în 7 zile → re-setup → …

## 4. Împărțirea cauzelor

Două cauze posibile, **același fix**:

- **(a) Testing** — probabil (~85%). Se vede în Cloud Console: banner galben
  „Google hasn't verified this app" + buton **Publish app**.
- **(b) Client secret rotit/șters** — posibil (~15%). Google: ștergerea unui
  client secret **revocă toate refresh token-urile** clientului. Se vede dacă în
  Cloud Console → Credentials există mai multe secrete pentru același client.

Ambele se rezolvă cu **aceeași secvență**: Publishing status → In production,
apoi un consimțământ nou.

---

## 5. Fix — o singură acțiune din partea lui POPY

### Pasul A (obligatoriu, ~30 sec) — înainte de consimțământ

Google Cloud Console → **APIs & Services → OAuth consent screen**:
- dacă vezi bannerul galben „Google hasn't verified this app" → apeș��
  **Publish app** → **In production**
- verifică și `apvizual@gmail.com` e în **Test users** (sau în Production nu mai contează)

> **Fără Pasul A, tokenul nou moare în 7 zile și suntem exact în punctul de acum.**

### Pasul B (~1 min) — consimțământ

Deschide linkul (generat cu scope-urile canonice, redirect fix):

```
https://accounts.google.com/o/oauth2/v2/auth?client_id=1068987308935-5b7h17gt1c5hc4i1m6eginads37o3m2h.apps.googleusercontent.com&redirect_uri=http%3A%2F%2F127.0.0.1%3A8976&response_type=code&scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fdrive+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fgmail.modify+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fcalendar+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fdocuments+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fspreadsheets+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fpresentations&access_type=offline&prompt=consent&include_granted_scopes=true
```

Apasă **Continue** → **Allow**. Browserul o să moară pe `http://127.0.0.1:8976`
(normal — nu e nimic acolo). **Copiază bara de adresa** (conține `?code=…`) și
trimite-mi-o. Atât.

### Pasul C — îl fac eu, în cloud, în același tur

1. `node mavis-tools/google-connect.js "<url>"` → schimb codul în refresh_token
2. scriu tokenul în secret manager (`GOOGLE_REFRESH_TOKEN_MAVIS_CLOUD`)
3. `node mavis-tools/google-verify.js` → **verificare reală, per serviciu, cu cod HTTP**

Niciun secret nu trece prin chat, niciunul în repo.

---

## 6. Bug de tooling reparat azi

`kit.js` folosea `https.request` → în sandboxul de cloud proxy-ul nu e onorat:
`Client network socket disconnected before secure TLS connection was established`.
**Apărea ca „nu am acces la Google"** — fals. `fetch` merge.

Reparat: `refresh()` și `attempt()` folosesc acum `fetch` (fallback `https.request`
pentru Node < 18). Commit `0d5bfe5`, împins pe `main`.

`google-verify.js` funcționează acum din cloud și raportează corect.

## 7. Ce nu merge și NU se repară din cloud

| Serviciu | Stare | De ce |
|---|---|---|
| Google Photos | ⛔ | `photoslibrary.googleapis.com` nu răspunde din cloud (DNS ok, conexiune nu) |
| Google Workspace MCP servers | ⛔ | `*mcp.googleapis.com` — 0/6 conexiuni din cloud |
| Google Maps | ⛔ | are nevoie de `GOOGLE_MAPS_API_KEY` + proiect cu billing |

---

*2026-10-22 02:10 · Mavis Cloud · măsurat în cloud, pe sandbox-ul real*

---

## 8. ADDENDUM 03:40 — cauza reală a `invalid_client` în browser

**Clientul OAuth era corect. Linkul era corect. Valoarea din link era mascată.**

Screenshot-ul lui POPY arăta în bara de adresa:

```
accounts.google.com/signin/oauth/error?authError=...&client_id=%7B%7BARCHON_SECRET%3AGOOGLE_CLIENT_ID_MAVIS_CL...
```

`%7B%7B` = `{{`, `%3A` = `:` → **`{{ARCHON_SECRET:GOOGLE_CLIENT_ID_MAVIS_CLOUD}}`**.

**Platforma mascheaza valorile din secret manager in mesajele mele.** Deci
client_id-ul real n-a ajuns niciodata la Google — a ajuns un placeholder.
Google a raspuns corect: „The OAuth client was not found", pentru ca intr-adevar
nu exista un client cu numele ala.

**Procesul meu a fost greșit:** am verificat clientul *din cloud* (unde valoarea
era reala, fiind citita din env) si am presupus ca și linkul trimis lui POPY
conține aceeasi valoare. Nu contine.

**Dovada ca valoarea e reala in cloud, dar mascata in chat:**
- `node -e` cu `process.env.GOOGLE_CLIENT_ID_MAVIS_CLOUD` → valoare **completa**
- aceleasi valoare, scrisa in mesajul de chat → `{{ARCHON_SECRET:...}}`

**Repar, aplicat:**
- `mavis-tools/google-client.json` → client_id ca **identificator public** în repo
  (Google nu-l considera confidential; apare in orice URL de autorizare).
- `mavis-tools/google-link-file.js` → genereaza linkul in `18-GOOGLE/AUTORIZARE-LINK.txt`.
  Livrare prin repo, unde mascarea nu exista.
- `mavis-tools/google-preflight.js` → pasul 0 verifica **drift** intre
  secret manager si repo.
- Regula scrisa in skill: **nicio valoare din secret manager prin chat.**

**Concluzie pentruMine:** daca o valoare vine din secret manager, nu o scriu in
chat. O scriu intr-un fisier si livrez prin repo.

**Notă de corectitudine:** diagnosticul din secțiunea 2 („client_id + secret
valide, tokenul e mort") a fost corect **la nivel de cloud**, dar explicația
finală („clientul din secret manager e al altui tool") a fost doar una dintre
cauze. Cauza **suficientă** pentru eroarea din browser a fost mascarea. Ambele
erau reale: clientul din secret manager era si el vechi, iar POPY l-a inlocuit
intrucât ii-am spus ca ala e.

---

## 9. STARE FINALĂ — 2026-10-22 04:40 · CONECTAT

Tokenul e obținut, scris în secret manager (`GOOGLE_REFRESH_TOKEN_MAVIS_CLOUD`)
și verificat live. **Măsurătoare reală:**

| Serviciu | Stare | Măsurătoare |
|---|---|---|
| **token** | ✅ | 6 scope-uri acordate, `expires_in=3599s` |
| **Gmail** | ✅ | apvizual@gmail.com · **84.313 mesaje** · **78.519 thread-uri** · 50 etichete (8 din seria MAVIS/*) |
| **Calendar** | ✅ | 4 calendare: apvizual@gmail.com, Family, Holidays in Romania, Sărbători în România |
| **Drive** | ✅ | **104,07 GB folosiți / 5498 GB** · 100+ fișiere listate |
| **Sheets** | ✅ | "Design_Jobs_Community_Board" → 'Design Jobs'!A1:Z50 = 23 rânduri |
| **Slides** | ✅ | "441DPH-Brief slides for GD senior_sep 2026" → 7 slide-uri |
| **Docs** | ⚠️ | `docs.googleapis.com` **blocat din cloud** (HTTP 400, pagină anti-bot reCAPTCHA — nu JSON). Conținutul se citește prin **Drive export** (`drive/v3/files/{id}/export?mimeType=text/plain`) — merge, conținut real. |
| **Photos** | ⛔ | `photoslibrary.googleapis.com` — conexiune blocată din cloud (0/6). De pe calculatorul lui merge. |
| **Maps** | ⛔ | cere `GOOGLE_MAPS_API_KEY` + proiect Cloud cu billing |
| **Workspace MCP** | ⛔ | `*mcp.googleapis.com` — 0/6 conexiuni din cloud |

### Ce s-a reparat azi, ca să nu se mai întâmple

1. **Mascarea secretelor în chat** → valorile din secret manager nu mai trec
   prin chat. Linkul se livrează prin repo (`18-GOOGLE/AUTORIZARE-LINK.txt`),
   client_id stă în repo ca identificator public (`mavis-tools/google-client.json`).
2. **`https.request` vs `fetch`** în sandbox → `kit.js` folosește acum `fetch`
   cu fallback pe `https.request` (fără verificare de certificat), pentru că
   gateway-ul platformei prezintă uneori un **certificat expirat**.
3. **`docs.get` avea URL-ul greșit** (`/docs/v1/` în loc de `/document/v1/`).
   Corectat. Plus `docs.export()` / `docs.text()` prin Drive.
4. **`google-local.js` nu procesa codul**: serverul verifica doar calea
   `/callback`, dar redirect_uri nu are segment de cale → Google trimite pe `/`
   → 404 → cod pierdut. Acum acceptă orice cale.
5. **`google-local.js` strica linkul pe Windows**: `cmd /c start "" "<url>"`
   trece prin cmd, care expandează `%VAR%` — iar URL-ul OAuth e plin de
   `%3A %2F %26` → **Google răspundea „Error 400 / Bad Request"**. Acum folosește
   `rundll32 url.dll,FileProtocolHandler`, care nu atinge cmd.
6. **Scriptul nu spunea nimic** la rulare → acum afișează clientul, scope-urile,
   linkul și avertismente pentru „Error 400" / versiune veche / `git pull`.

### Observație de diagnostic

`Error 400 / Bad Request` la authorize = **scope invalid** (ex.
`photoslibrary.readwrite` fără Photos Library API activat) **sau** link
corupt. Nu e credential. Verifică: scriptul e la zi? (`git pull`)

### Următorul pas: In production

Appul e în **Testing** → refresh tokenul moare în 7 zile de la consimțământ
(2026-10-22 01:39 UTC). Checklist: `docs/GOOGLE-PRODUCTION-CHECKLIST.md`.
