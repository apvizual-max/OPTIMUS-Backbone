# GOOGLE — stare măsurată la 2026-10-28

> Măsurat live din cloud la `2026-10-28 01:40 UTC`.
> **Succesorul** lui `GOOGLE-STATUS-2026-10-27.md` (care rămâne istoric).
> **Ciclu de 7 zile: încheiat.**

---

## 1. Verdictul

```
=== GOOGLE PREFLIGHT ===
  [0] drift client_id  OK      (env si repo coincid)
  [1] credentiale      OK      (1068987308935…nt.com)
  [2] client la token  OK
  [3] client la auth   OK
  [4] refresh token    OK
  [5] expirare         fara limita de 7 zile  (appul e IN PRODUCTION)
  [6] scope-uri        OK      (27, identice cu lista canonica)
  VERDICT: Google e conectat.
```

**Conectat, în Production, cu 27 scope-uri, fără expirare săptămânală.**

---

## 2. Ce s-a întâmplat în noaptea asta

POPY a introdus `GOOGLE_10_28_2026` în secret manager. **Nu era o cheie — era un
URL.** L-am determinat după formă (1437 caractere, începe cu `htt`, fără spații
sau newline-uri) și am extras parametrii:

```
host: 127.0.0.1:8976 | parametri: iss, code, scope, authuser, prompt
```

Adică **redirect-ul de autorizare cu `?code=…`** — codul de consimțământ.

**L-am schimbat imediat** (codurile de autorizare sunt de unică folosință):

```
POST oauth2.googleapis.com/token  →  HTTP 200
scope-uri obtinute: 27
refresh_token_expires_in: ABSENT  =>  APPUL E IN PRODUCTION
```

**Câmpul `refresh_token_expires_in` a dispărut** → appul a fost publicat. Asta
e dovada, și e verificabilă de oricine, nu o afirmație.

Tokenul nou a fost scris în secret manager ca `GOOGLE_REFRESH_TOKEN_MAVIS_CLOUD`
(prin tool-ul `secret`, **nu prin chat**).

---

## 3. Ce a câștigat tokenul nou: 27 scope-uri (era 6)

### De ce contează cel mai mult

**`gmail.settings.basic`** — până azi lipsea. Fără el, `filters PATCH` și
`filters POST` răspund **403**, de aceea reparația filtrelor trebuia rulată
**de pe mașina lui POPY**, nu din cloud. Acum e în token.

> **Nu am scris nimic în contul lui POPY ca să testez asta.** Citirea filtrelor
> funcționează, și scope-ul e prezent în token — dar prefer să nu fac
> scrieri în Gmail-ul lui fără să fie nevoie. Când va fi nevoie de reparație,
> se testează pe un filtru throwaway și se șterge imediat.

### Restul scope-urilor noi

| Scope | Ce deblochează |
|---|---|
| `mail.google.com/` | acces complet Gmail, inclusiv gestionarea filtrelor la nivel de cont |
| `gmail.send` / `gmail.compose` | trimitere / drafturi — **regula rămâne: POPY apasă butonul** |
| `drive.appdata` | datele aplicației în Drive — configure Mavis Cloud fără să-i atingă fișierele |
| `contacts` | Google Contacts |
| `chat.spaces.readonly`, `chat.messages` | Google Chat |
| `calendar.events` | creare/modificare evenimente |
| `forms.body`, `forms.responses.readonly` | Google Forms |
| `script.projects` | Google Apps Script |
| `books` | Google Books |
| `youtube.readonly`, `youtube.upload` | YouTube |
| `photospicker.mediaitems.readonly` | Photos **Picker** (nu Photos **Library**) |
| `userinfo.email`, `userinfo.profile`, `openid` | identitate |

---

## 4. Capcana pe care o-am închis la timp

Până azi, **cinci scripturi fiecare aveau propria listă de 6 scope-uri**
(`google-client.json`, `google-local.js`, `google-link-file.js`,
`google-refresh.js`, `google-setup.js`).

**Consecința:** orice re-consimțământ generat de ele ar fi adus un token cu
**doar 6 scope-uri** — pierzând `gmail.settings.basic` și restul. Adică
următoarea re-autentificare ar fi **cât un downgrade silent**.

**Reparat:** singura sursă de adevăr este acum `mavis-tools/google-scopes.js`
(27 scope-uri, fiecare cu motivul pentru care e cerut). Toate scripturile
importă din el.

**Verificat:** lista canonică și scope-urile tokenului sunt **identice** —
`lipsă: NIMIC · în plus: NIMIC`.

### Control de drift permanent

`google-preflight.js` are acum pasul **[6]**: compară scope-urile tokenului cu
lista canonică și raportează `DRIFT` + ce lipsește. Drift-ul se vede **înainte**
să te treacă, nu după.

---

## 5. Capacități verificate acum

| Serviciu | Stare | Valoare |
|---|---|---|
| Gmail | ✅ | 83.532 mesaje · 77.727 thread-uri · 51 etichete |
| Drive | ✅ | 107.805.424.699 / 5.497.558.138.880 bytes · 3 foldere la rădăcină |
| Calendar | ✅ | 4 calendare |
| Sheets | ✅ | `Design_Jobs_Community_Board` — 27 rânduri |
| Slides | ✅ | `441DPH-Brief slides for GD senior_sep 2026` — 7 slide-uri |
| Docs | ⚠️ | API blocat din cloud (anti-bot) — conținutul merge prin **Drive export** (8.547 caractere) |
| Photos Library | ❌ | 403 — **scope lipsă**: avem `photospicker.mediaitems.readonly`, API-ul Library cere `photoslibrary.readonly` (deprecated) |
| Maps | ⛔ | cere API key + billing, nu OAuth |

**9 OK · 1 blocat (maps) · 1 eșuat (photos, scope).**

---

## 6. Ce se schimbă din punct de vedere operațional

1. **Ciclu de 7 zile: încheiat.** Nu mai re-autentificăm săptămânal.
2. **Filtrele Gmail se pot repara din cloud** — `gmail.settings.basic` e în token.
3. **Un singur loc de adevăr pentru scope-uri** + control de drift în preflight.
4. **Linkul de autorizare e regenerat** cu cele 27 scope-uri — un viitor
   re-consimțământ reproduce exact aceleași capabilități.

---

## 7. Ce rămâne de făcut (nimic urgent)

- **TO DO 03** — direcția workflow-urilor Gmail/Drive. Etichetele noi sunt
  gata (`10-GMAIL/TAXONOMIE-2026-10-27.md`).
- **TO DO 04** — profilul de designer. Pot construi scheletul de CV singur.
- **TO DO 05** — rotirea cheii API Google expuse. Cheia e în secret manager
  ca `GOOGLE_API_KEY_EXPOSED_HERMES_TEMP`.
- **Întrebare pentru POPY** — ai golit Trash-ul între 22 și 27 octombrie?
  (Δ de −811 mesaje, cauza nedeterminată de date.)

---

*2026-10-28 · Mavis Cloud · măsurat live din cloud*
