# GOOGLE — stare măsurată la 2026-10-27

> Măsurat live din cloud la `2026-10-27 14:40 UTC`. Nu estimat.
> Succesorul lui `GOOGLE-STATUS-2026-10-22.md` (care rămâne istoric).

---

## 1. Verdictul

**Conectat și funcțional. Dar cu 35 de ore de marjă.**

```
=== GOOGLE PREFLIGHT ===
  [0] drift client_id  OK      (env si repo coincid)
  [1] credentiale      OK      (1068987308935…nt.com)
  [2] client la token   OK
  [3] client la auth    OK
  [4] refresh token    OK
  [5] expirare         35.0 ore  (2026-10-29T01:39:36Z)
      appul e INCA IN "Testing" -> tokenul moare in 7 zile de la consimtamant.
  VERDICT: Google e conectat.
```

---

## 2. Ce e nou față de 22 octombrie

### a) Am putut **măsura** starea appului — nu mai e o presupunere

Răspunsul la `POST oauth2.googleapis.com/token` conține câmpul
`refresh_token_expires_in`. **Câmpul e prezent DOAR când consent screen-ul e în
„Testing"** (limita de 7 zile). Dacă appul ar fi în Production, câmpul ar lipsi.

```
refresh_token_expires_in: 126088 secunde  (1,5 zile)
tokenul expira la: 2026-10-29T01:39:36Z
```

**Verificare automată, în orice sesiune:** `node mavis-tools/google-preflight.js`
— pasul 5 spune direct dacă appul mai e în Testing și câte ore rămân.
Nu mai trebuie ghicit dacă POPY a publicat sau nu.

### b) Pasul 5 a fost adăugat în `google-preflight.js`

```
[5] expirare         fara limita de 7 zile  (appul e IN PRODUCTION)
[5] expirare         35.0 ore  (2026-10-29T01:39:36Z)   ← acum
```

### c) Taxonomia Gmail a fost rearanjată

7 din 8 etichete `MAVIS/*` redenumite, 4 hierarhii noi, 19 filtre mutate
împreună și verificate — **0 sparte**. Detalii:
`10-GMAIL/TAXONOMIE-2026-10-27.md`.

### d) Δ cont Gmail: −811 mesaje

83.505 mesaje (era 84.316), Trash 626, Spam 2. **De confirmat cu POPY** — vezi
secțiunea 4 din documentul de taxonomie.

### e) Drive: 3 foldere la rădăcină, 107,80 GB

`GDrive-Second_Brain_PKMS` · `AITimeline_Backup` · `Gemini`. Pe 22 oct era un
singur folder la rădăcină.

---

## 3. Ce funcționează acum (măsurat)

| Serviciu | Stare | Valoare |
|---|---|---|
| Gmail | ✅ | 83.505 mesaje · 77.701 thread-uri · 51 etichete (36 de utilizator) |
| Drive | ✅ | 107.804.992.393 / 5.497.558.138.880 bytes · 3 foldere la rădăcină |
| Calendar | ✅ | 4 calendare |
| Sheets | ✅ | `Design_Jobs_Community_Board` — 27 rânduri |
| Slides | ✅ | `441DPH-Brief slides for GD senior_sep 2026` — 7 slide-uri |
| Docs | ⚠️ | API blocat din cloud (anti-bot) — conținutul merge prin **Drive export** (8.547 caractere) |
| Photos | ❌ | HTTP 403 — scope insuficient, **nu e blocare de rețea** (s-a schimbat) |
| Maps | ⛔ | cere API key + billing, nu OAuth |

**Photos s-a schimbat de la „blocat" la „scope lipsă"** — deci API-ul e
accesibil, doar nu am cerut scope-ul `phot library`. Se poate adăuga
re-consentând cu scope-ul suplimentar, dar până la publicarea appului oricum
se reia consimțământul.

**9 OK · 1 blocat (maps) · 1 eșuat (photos, scope).**

---

## 4. Ce trebuie făcut de POPY — un singur lucru

**Publish la OAuth consent screen → In production.**

Checklist: `docs/GOOGLE-PRODUCTION-CHECKLIST.md`

Pași scurt: Cloud Console → APIs & Services → OAuth consent screen →
**Publish app** → **In production**. (User type External, app name, support
email, developer contact email, audience External.)

**Fără publicare, tokenul moare la `2026-10-29 01:39 UTC`.** Cu publicare,
tokenul nou nu mai are limita de 7 zile și problema dispare definitiv.

---

## 5. Cum arată procedura de re-consimțământ (pregătită)

1. `node mavis-tools/google-refresh.js link`
   → scrie `18-GOOGLE/AUTORIZARE-LINK.txt`, comitează și împinge.
2. POPY deschide linkul din
   `https://github.com/apvizual-max/MAVIS-CLOUD/blob/main/18-GOOGLE/AUTORIZARE-LINK.txt`
   → Allow → copiază bara de adresa (are `?code=…`).
3. `node mavis-tools/google-refresh.js code "<url>"`
4. Tokenul se scrie în secret manager ca `GOOGLE_REFRESH_TOKEN_MAVIS_CLOUD`
   **prin tool-ul `secret`, niciodată în chat.**
5. `node mavis-tools/google-verify.js`

**Linkul nu se trimite niciodată prin chat** — platforma maschează valorile din
secret manager în `{{ARCHON_SECRET:…}}`, browserul primește placeholder și
răspunde `Error 401: invalid_client`. Asta a fost cauza rădăcină a problemei
inițiale.

Procedura completă: `docs/PROCEDURA-LIVRARE-SECRETE.md`

---

*2026-10-27 · Mavis Cloud · măsurat live*
