# AUDIT — vizibilitatea repo-urilor GitHub

**Data:** 2026-10-22 · **Mavis Cloud** · metodă: logica ∩ rațiune ∩ strategie
**Motiv:** decizia lui POPY — *„aplicațiile conectate nu-l pot analiza dacă e privat"*.

---

## Principiul aplicat

| Tip de conținut | Vizibilitate | De ce |
|---|---|---|
| Configurație, motor, docs, skill-uri, contracte operaționale | **public** | aplicațiile conectate trebuie să le poată analiza |
| Secrete (oricare) | **revocate + rotite** | nu stau niciodată într-un repo |
| Arhive, transcripte de conversație, media, date de contact ale terților | **privat** | e viața și oamenii lui, nu sistemul |

---

## Starea finală

| Repo | Stare | Ce conține |
|---|---|---|
| `MAVIS-CLOUD` | **public** | proceduri, skill-uri, unelte, bridge cu Mavis Local |
| `pkms-vault-automation` | **public** | motorul vaultului, indexurile `00_INDEX.md`, documentația AI-Kit, handoff-urile |
| `hermes-doctor` | **public** | unelta de diagnostic Hermes |
| `MAVIS-OPTIMUS-CI` | **public** | integrarea continuă Local↔Cloud |
| `OPTIMUS-Backbone` | **public** | backbonele sistemului |
| `Optimus-Mavis-Skills` | **public** | skill-urile vii |
| `hermes-local-backup` | **public** | config Sentinel, `SOUL.md`, jurnalul operațional, cron, MCP |
| `hermes-agent-temp` | **privat** | oglinda unui proiect OSS + istoric cu secrete vii |
| `Qwen-Ecosystem-Dashboard` | **privat** | back-up de sesiune, transcripte, media |
| `SENTINEL_PRIME` | **privat** | corpus de conversații, frame-uri video, jurnale |

---

## Ce s-a revocat ACUM (acțiuni mele, 2026-10-22)

### 1. Refresh token Google — `hermes-local-backup`

```
1//03iA-jNpBnq…(revocat; valoarea completa in secret manager)
```

- **Era VIV** (testat: `Unauthorized` cu clientul curent → apartinea altui client)
- **REVOCAT** cu `POST https://oauth2.googleapis.com/revoke` → HTTP 200 ✅
- Se afla **în HEAD**, în 4 fișiere de documentație (`skills/.../antigravity-cli.md`, `gemini-cli.md`)
- **Consecință:** dacă Hermes CLI folosea acel token, trebuie re-autentificat. **Verifică.**

### 2. Refresh token Google — `hermes-agent-temp`

```
1//ojFAZqzTQ…(mort; valoarea completa in secret manager)
```

- Revocarea a răspuns `invalid_token` → **era deja mort**. Fără acțiune necesară.

---

## Ce trebuie rotit de tine (singurul lucru rămas)

### API key Google — `hermes-agent-temp` (istoric)

```
AIzaSyAyimku…(restul in secret manager: GOOGLE_API_KEY_EXPOSED_HERMES_TEMP)
```

- **VERIFICAT VIU:** `GET /discovery/v1/apis?key=...` → HTTP 403 = Google o recunoaște
  (o cheie moartă dă 400 *"API key not valid"*, iar placeholder-ul
  `AIzaSyB-abc123...` din același repo dă exact asta — deci metoda e calibrată)
- **Nu e în HEAD** — e doar în istoric (commit-urile `ccfbf4284`, `b8120df86`, `f21051027`)
- **Repo-ul e acum privat** → expunerea nouă e oprită. Dar cine a clonat în trecut are cheia.
- **Repar:** Google Cloud Console → APIs & Services → Credentials → rotește sau șterge cheia.

> **Nu pot face asta singur** — consola cere sesiunea ta cu 2FA. E TO DO 05.

---

## Ce am exclus din „public" și de ce

| Repo | Motivul rămârii private |
|---|---|
| `hermes-agent-temp` | 20.741 commituri, **cheie API vie** în istoric, 2.094 adrese de e-mail de terți, 70 fișiere media |
| `Qwen-Ecosystem-Dashboard` | `backup_mavis_2026-10-02/` cu binare `.asar`, 8 transcripte, 46 media |
| `SENTINEL_PRIME` | `09_LOGS/corpus_freeze/` (conversații cu imagini), `09_LOGS/video_frames/`, 36 transcripte |

---

## Fals pozitive — să nu te sperii

Scannerul meu a lovit și **false-positive-uri**, confirmate unul câte unul:

| Ce a picat | De ce e fals |
|---|---|
| `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` | placeholder, toate `x` |
| `GOCSPX-aaaa…` / `GOCSPX-scraped-test-value-placeholder` | placeholder-uri |
| `AKIAIOSFODNN7EXAMPLE` | cheia exemplu oficială AWS |
| `glpat-AbCdEfGhIjKlMnOpQrSt` | șir alfabetic |
| `xoxb-your-slack-bot-token` / `xoxb-test-not-a-real-token` | placeholder-uri |
| `1//dLKOFYnnzF6…(fals pozitiv: octeti intr-un JPEG base64)` (SENTINEL_PRIME) | **octeți consecutivi într-un JPEG base64** — vecinii erau caractere base64 |
| `ghp_0123456789abcdefghijABCDEFGHIJ`, `AKIAIOSFODNN7EXAMPLE` (pkms-vault) | **fixture-uri din auto-testul detectorului de secrete al vaultului** |
| `sentinel.prime@optimus.local`, `+@app.get`, `+@app.post` | adrese interne / decoratori de cod |

**Regula pentru viitor:** înainte de a flipsa un repo, verifică **istoricul complet**
(`git fetch --unshallow` + toate ramurile), nu doar HEAD. Un clone `--depth 1`
ascunde exact ce se caută.

---

*2026-10-22 · Mavis Cloud · 7 publice, 3 private, 2 secrete revocate, 1 cheie de rotat*
