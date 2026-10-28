# GOOGLE — checklist: din Testing în In production

**De ce contează:** cu consent screen-ul în **Testing**, Google omoară refresh
token-ul în **7 zile de la consimțământ**. Fără asta, oricât de bine arată
setup-ul, într-o săptămână trebuie reluat tot fluxul. Cu **In production**,
tokenul trăiește până la revocare sau ~6 luni de inactivitate.

Sursa oficială: https://support.google.com/cloud/answer/15549945

---

## Ordine

1. **Consimțământul** — întâi. Ca să existe un token viu.
2. **Clientul Desktop** — există deja: `Mavis_Cloud`
   (`1068987308935-bp47aoerh6gu1aohm74blfhnccnku773…`), creat 21 Oct 2026.
3. **Consent screen → In production.**
4. **Verificare** — `node mavis-tools/google-verify.js` din cloud.
5. **Consimțământ nou, dacă e nevoie** — dacă tokenul a fost obținut înainte
   de publicare, un token nou în Production nu mai are limita de 7 zile.

---

## Pasul 1 — ce verificăm înainte

În Cloud Console → **APIs & Services → OAuth consent screen**:

| Setare | Valoarea corectă | De ce |
|---|---|---|
| **User type** | External | altfel nu apare pe conturi gmail.com |
| **App name** | ceva lizibil (ex. „Mavis Cloud") | apare pe ecranul de consimțământ |
| **User support email** | apvizual@gmail.com | obligatoriu |
| **Developer contact email** | apvizual@gmail.com | obligatoriu |
| **Logo** | opțional | apare pe ecran |
| **Application homepage** | opțional | polită Google pentru verificare |
| **Application privacy policy** | opțional, dar recomandat | polită Google |
| **Authorized domains** | gol e OK pentru uz personal | nu ai nevoie de domeniu |

**Test users** (doar relevant cât timp e în Testing):
`apvizual@gmail.com` trebuie să fie în listă. În Production nu mai contează.

---

## Pasul 2 — de ce „Publish app" poate fi refuzat

Google cere **„Setup branding"** și **„Audience"** completate. Dacă lipsesc
Publicații/Publicare, butonul „Publish app" poate fi acolo dar să dea erori.
Verifică:

- Application name — nevid
- User support email — setat
- Developer contact email — setat
- **Audience** — External

Apoi: **Publish app → In production**.

> Pentru uz personal, poate apărea „Google hasn't verified this app".
> **E normal** și nu blochează nimic. Verificarea completă (green check)
> se cere doar dacă app-ul e folosit de alți oameni.

---

## Pasul 3 — după publicare

```bash
# din cloud
node mavis-tools/google-preflight.js     # verdict pe un singur rand
node mavis-tools/google-verify.js        # masuratoare reala per serviciu
```

Dacă tokenul a fost obținut **înainte** de publicare, e deja „mort" în
sensul lui Google după 7 zile de la consimțământ. Fă un consimțământ nou:

```bash
node mavis-tools/google-link.js          # da linkul, deschide in browser
node mavis-tools/google-connect.js "<url>"   # cod -> refresh_token
```

Tokenul nou intră în secret manager → trăiește mult.

---

## Cum nu se mai strică

| Situație | Detectare | Repar |
|---|---|---|
| client_id greșit în secret manager | `google-preflight.js` → pasul 2 sau 3 FAIL | pune clientul Desktop corect |
| token expirat / revocat | `google-preflight.js` → pasul 4 FAIL | consimțământ nou |
| client șters din Cloud Console | preflight FAIL | refă clientul Desktop (2 min) |
| rețea din cloud pică | retry inclus în `kit.js` și `google-connect.js` | automat |

**Regula de aur:** înainte de orice operațiune Google, rulează
`node mavis-tools/google-preflight.js`. Un singur verdict, în 10 secunde.
Nu mai cheltui ore cu „de ce nu merge".

---

*Pregătit 2026-10-22 · Mavis Cloud*
