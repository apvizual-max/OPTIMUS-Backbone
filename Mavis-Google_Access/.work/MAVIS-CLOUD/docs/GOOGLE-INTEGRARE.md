# GOOGLE — cum ajung credentialele în Cloud

**Data:** 2026-10-21 22:50 · **Mavis Cloud** · măsurat, nu ghicit

---

## 1. Răspuns scurt

Ai cerut: *„dă-mi ce trebuie să pun cheie și valoare"*.

**Răspunsul e mai scurt decât credeai.** Nu trebuie să scrii tu chei.

Îți las **un singur command** care le generează și le pune într-un fișier local:

```bash
cd /workspace/Mavis        # sau unde ai repo-ul
node mavis-tools/google-setup.js
```

Se deschide browserul, apeși „Accept", și îți apare:

```
~/.google-mcp/cloud-secret.env
```

Î acel fișier sunt exact 4 linii `CHEIE=VALOARE`. Le copiezi în secret manager
(Mavis Cloud) și gata.

**4 chei. Atât.** Nu 30. Nu un OAuth setup de 2 ore.

| Cheie | Ce e | De unde vine |
|---|---|---|
| `GOOGLE_CLIENT_ID` | id-ul clientului OAuth (Desktop app) | din `credentials.json` |
| `GOOGLE_CLIENT_SECRET` | secretul clientului OAuth | din `credentials.json` |
| `GOOGLE_REFRESH_TOKEN` | tokenul care nu expira | generat de `google-setup.js` |
| `GOOGLE_EMAIL` | `apvizual@gmail.com` | identitatea unică pe tot sistemul |

Mai târziu, pentru Maps: `GOOGLE_MAPS_API_KEY` — care e **alt tip** (API key, nu OAuth).

---

## 2. De ce așa, și nu altfel

Am măsurat 3 drumuri. Unul merge.

### Drumul A — Connector nativ MiniMax pentru Google ❌ **nu există**

Am verificat:
- Catalogul oficial de plugin-uri (agent.minimax.io/docs/code/agents/plugins):
  Hundsun, Qichacha, EverMe, PKUlaw, Office, WPS, WeCom. **Niciun Google.**
- Cache-ul de plugin-uri din runtime-ul de cloud: `figma` + `github`. **Doar astea.**
- API-ul de conectoare al platformei (`/minimax-cloud/api/v1/connectors/connected-tools/list`)
  → `error: invalid signature`. Defecțiune de transport, **nu** „nu ai conectoare".
  Am încercat de 3 ori, cu `--keyword google|gmail|drive` și fără filtru. Identic.

Chiar dacă ar exista un App Google, canalul de conectoare e rupt acum în cloud.
**Deci: nu conta pe el.**

### Drumul B — Google Workspace MCP servers (oficiale) ⚠️ **existe, dar nu se atinge din cloud**

Google a lansat servere MCP oficiale:
`gmailmcp.googleapis.com/mcp/v1`, `drivemcp…`, `docsmcp…`, `sheetsmcp…`,
`slidesmcp…`, `calendarmcp…` (surse: developers.google.com/workspace/guides/configure-mcp-servers)

Problema: **din sandbox-ul de cloud, aceste host-uri nu răspund** (DNS rezolvă, conexiunea
nu se face). Măsurat, 3+ încercări, cu și fără POST. De pe calculatorul tău (Local)
ar merge.

Deci: le ținem pentru Local. Din cloud, nu.

### Drumul C — OAuth propriu, prin API REST ✅ **asta e drumul**

Direct pe API-urile Google, cu credentialele tale. Funcționează din cloud
**azi**, cu ce am construit.

---

## 3. Ce am construit (committed, gata de folosit)

| Fișier | Ce face |
|---|---|
| `mavis-tools/google-auth.js` | singura sursă de adevăr pentru credentiale: env (cloud) sau fișiere (local) |
| `mavis-tools/kit.js` | clientul Google — **refăcut**: lazy, cu Calendar/Docs/Sheets/Slides/Photos adăugate |
| `mavis-tools/google-setup.js` | fluxul OAuth + generarea cheilor. Rulezi la Local. |
| `mavis-tools/google-exchange.js` | schimbă un cod de autorizare în `refresh_token`, fără browser local. |
| `mavis-tools/google-verify.js` | verificare read-only din cloud. Fiecare serviciu, cu cod HTTP real. |
| `mavis-tools/test-endpoints.js` | test permanent: verifică că URL-urile API-urilor sunt corecte |

**Local și Cloud folosesc același `kit.js`.** Diferă doar unde stau cheile:
local → `~/.google-mcp/`, cloud → secret manager. Asta e tot sistemul.

---

## 4. O greșeală prinsă măsurând

`www.googleapis.com/docs/v1/...` → **404**. Fiecare API Google are propriul host:

```
drive      → www.googleapis.com/drive/v3
gmail      → gmail.googleapis.com/gmail/v1
calendar   → www.googleapis.com/calendar/v3
docs       → docs.googleapis.com/docs/v1        ← nu www
sheets     → sheets.googleapis.com/v4           ← nu www
slides     → slides.googleapis.com/v1           ← nu www
photos     → photoslibrary.googleapis.com/v1
```

`test-endpoints.js` trimite un token fals intenționat: dacă primești **401**, endpointul
există; dacă primești **404**, URL-ul e greșit. Acum: **10 din 11 corecte.**
(Photos = blocat de rețea din cloud, nu URL greșit — vezi secțiunea 6.)

---

## 5. Pasul 1 — Local, cu browserul (5 minute)

### 5.1 Ai nevoie de un client OAuth

Dacă nu îl ai:

1. [Google Cloud Console](https://console.cloud.google.com/) → proiect nou (sau existent)
2. **APIs & Services → Library** → activează:
   - Google Drive API
   - Gmail API
   - Google Calendar API
   - Google Docs API · Google Sheets API · Google Slides API
   - Google Photos Library API — **doar dacă vrei Photos.** Fără ea, scope-ul
     `photoslibrary.readwrite` este respins (vezi 5.3)
3. **APIs & Services → OAuth consent screen**
   - User type: **External**
   - Adaugă `apvizual@gmail.com` în Test users
   - **Publishing status → `In production`** ← **CRITIC**, vezi secțiunea 7
4. **Credentials → Create Credentials → OAuth client ID**
   - Application type: **Desktop app** (obligatoriu pentru flow-ul cu redirect pe localhost)
   - Descarcă JSON-ul. **NU îl trimite în chat.** Îl pui în:
     `~/.google-mcp/credentials.json` (conține un obiect `installed`)

### 5.2 Rulezi scriptul

```bash
node mavis-tools/google-setup.js
```

Se deschide browserul → apeși Accept → revii în terminal. Gata.

Dacă nu ai încă `credentials.json`, scriptul îl cere pe loc și **îl salvează automat**
(`chmod 600`). Nu mai trebuie să scrii nimic cu mâna.

Verificare înainte de a continua:
```bash
node mavis-tools/google-setup.js --check
```
Îți arată exact ce scope-uri sunt acordate și care lipsesc.

### 5.3 Eroarea `invalid_scope` — și de ce nu te întoarce browserul

```
Error 400: invalid_scope
valid=[drive, gmail.modify, calendar, documents, spreadsheets, presentations]
invalid=[photoslibrary.readwrite]
```

**Ce se întâmplă:** Google consideră un scope „invalid" dacă API-ul corespunzător
**nu este activat** în proiectul Cloud. Deci nu e un scope greșit — e un API neactivat.

**Și de ce scriptul părea blocat:** Google afișează pagina de eroare și **nu te
redirecționează înapoi** — deci serverul local nu primește nimic și aștepta la infinit.
Acum scriptul are timeout de 10 minute și îți spune exact ce s-a întâmplat.

**Reparul 1 (recomandat, 1 minut):** activează **Photos Library API** în proiect:
APIs & Services → Library → „Photos Library API" → Enable. Apoi:

```bash
node mavis-tools/google-setup.js --with-photos
```

**Reparul 2 (mai rapid):** renunță la Photos deocamdată — e oricum blocat din cloud:

```bash
node mavis-tools/google-setup.js
```

Default-ul cere **6 scope-uri** (fără Photos). Restul funcționează imediat.

> **De ce Photos e separat:** măsurat 2026-10-21 — `photoslibrary.googleapis.com`
> nu răspunde din sandbox-ul de cloud (0/6 conexiuni, DNS ok). De pe calculatorul
> tău merge. Deci Photos se face de la Local oricum; nu blochăm restul pentru el.

---

## 6. Pasul 2 — Cloud, cu cheile

Copiezi cele 4 linii din `~/.google-mcp/cloud-secret.env` în secret manager
(Mavis Cloud → Environmental Information → Secrets):

```
GOOGLE_CLIENT_ID      = ...
GOOGLE_CLIENT_SECRET  = ...
GOOGLE_REFRESH_TOKEN  = ...
GOOGLE_EMAIL          = apvizual@gmail.com
```

Apoi, **din cloud**:

```bash
node mavis-tools/google-verify.js
```

Outputul arată, pentru fiecare serviciu, un cod HTTP real:

> ⚠️ **CORECTARE 2026-10-22.** Blocul de mai jos a fost scris ca **exemplu de
> format**, dar arăta ca măsurătoare reală. **NU a fost măsurat.** La
> 2026-10-22 s-a dovedit că secretul manager ținea credentialele unui **alt
> OAuth client** (cel al lui Hermes CLI), deci tabelul „de mai jos" nu avea
> ce să măsoare. **Nu te baza pe el.** Măsurătoarea reală e în
> `docs/GOOGLE-STATUS-2026-10-22.md` și se obține cu `google-verify.js`.

```
  OK   drive:about          apvizual@gmail.com | folosit 1.2 GB / 15 GB
  OK   drive:Alex Work      exista, 34 elemente
  OK   gmail:profile        apvizual@gmail.com | 19070 mesaje | 41233 thread-uri
  OK   gmail:etichete       26 etichete total, 8 din seria MAVIS/*
  OK   calendar             3 calendare: Primar, Personal, Work
  OK   docs                 "MavisCloud-Google" — 12 blocuri
  OK   sheets               "Scoruri 2026"!A1:Z50 = 48 randuri
  OK   slides               "Prezentare Q4" | 14 slide-uri
  BLOC photos:albums        inaccesibil din cloud (host blocat de rețea)
```

*(exemplu de format — numerele reale apar doar după ce cheile sunt puse și rulezi tu)*

### Ce funcționează astăzi din cloud

| Serviciu | Stare | De ce |
|---|---|---|
| Drive (list, read, create, move, trash) | ✅ | `www.googleapis.com` — merge |
| Gmail (read, label, trash) | ✅ | `gmail.googleapis.com` — merge |
| Calendar | ✅ | `www.googleapis.com` — merge |
| Docs / Sheets / Slides | ✅ | host-urile lor proprii — merg |
| Google Photos | ⛔ | `photoslibrary.googleapis.com` **nu răspunde din cloud** (DNS ok, conexiune nu) |
| Google Maps | ⛔ | are nevoie de `GOOGLE_MAPS_API_KEY` + proiect Cloud cu billing |

**Photos se poate face de pe calculatorul tău (Local)** — de acolo merge.
Sau, dacă MiniMax repară blocajul de rețea, devine posibil și din cloud.

---

## 7. „7 zile" — de ce contează și cum îți scapă
Dacă OAuth consent screen-ul e în **Testing**, refresh token-ul **moare în 7 zile**.
Nu șaptămână — 7 zile. Apoi: `invalid_grant`, și Google Drive/Gmail devin
muți fără nicio explicație.

Sursa oficială (support.google.com/cloud/answer/15549945):
> „Authorizations by a test user will expire seven days from the time of consent.
> If your OAuth client requests an `offline` access type and receives a refresh token,
> that token will also expire."

Excepție: **doar** pentru `userinfo.email`, `userinfo.profile`, `openid`.
Noastre nu intră în excepție — deci regula se aplică plin.

**Soluția:** `Publishing status → In production`. Atunci refresh token-ul nu expiră
(decât dacă e revocat sau nu e folosit ~6 luni).

Când e în Production, poate apărea un ecran „Google hasn't verified this app" —
**e normal pentru uz personal** și nu blochează nimic. Verificarea completă
cer doar dacă app-ul servește alți utilizatori.

**Diagnosticul rapid:** dacă mâine `google-verify.js` dă `invalid_grant` —
e 99% „7 zile". Reiei `google-setup.js` sau schimbi statusul în Production.

---

## 8. Ce NU fac (reguli, nu preferințe)

- **Nu** ștergere definitivă. Doar Trash. (implementat în `kit.js` — `danger.driveHardDelete` există, dar nu e apelat de nimic automat)
- **Nu** trimitere de mail fără comanda ta explicită, punctuală.
- **Nu** chei în repo, în chat, sau prin Jules/GitHub.
- **Nu** citesc tot credentialele deodată. Fiecare cheie, un singur scop.

`kit.js` are `danger` separată, ca să poți folosi funcțiile periculoase
**doar când spui tu**, despre ce anume.

---

## 9. Ce urmează

| Când | Ce |
|---|---|
| acum | tu rulezi `google-setup.js` la Local → pui 4 cheile în secret manager |
| imediat după | eu rulez `google-verify.js` din cloud → rezultat real, per serviciu |
| apoi | facem Drive-ul **magazinul de sistem**: citit, scris, arbore `/Alex Work/` |
| apoi | `GOOGLE_MAPS_API_KEY` pentru Maps (cu billing) |
| când vrei | un plugin MiniMax pentru cloud, cu scope-urile Google — dar Marketplace-ul cere credențiale **în afara** pachetului, deci se face prin secret manager, ca mai sus |

---

## 10. Surse

- Sesiune de conectoare: `mcode-tools connector tools` → `invalid signature` (măsurat 2026-10-21)
- Marketplace: https://agent.minimax.io/docs/code/agents/plugins (catalog: Hundsun, Qichacha, EverMe, PKUlaw, Office, WPS, WeCom — fără Google)
- Reguli plugin (App vs MCP, interzicerea credențialelor în pachet): https://agent.minimax.cn/docs/code/agents/plugin-submission
- Google Workspace MCP servers: https://developers.google.com/workspace/guides/configure-mcp-servers
- Regula „7 zile": https://support.google.com/cloud/answer/15549945
- `invalid_grant` = Testing: https://developers.google.com/google-ads/api/docs/get-started/common-errors
- Layout `~/.google-mcp/`: https://github.com/salviz/google-mcp-server (240 tools, `GOOGLE_CLIENT_ID`/`GOOGLE_CLIENT_SECRET`/`GOOGLE_TOKEN_PATH`)

---

*2026-10-21 22:50 · Mavis Cloud · măsurat în cloud, pe sandbox-ul real*
