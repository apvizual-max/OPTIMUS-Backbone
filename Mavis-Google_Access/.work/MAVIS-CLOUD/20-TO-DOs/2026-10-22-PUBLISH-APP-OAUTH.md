# 01 · Publish la aplicația OAuth

**Data:** 2026-10-22 · **Tip:** configurări în Google Cloud Console
**Perspectivă lipsă:** niciuna — dar **accesul** e doar la tine (contul tău, cu 2FA)
**Stare:** ✅ **REZOLVAT — 2026-10-28**

---

## ✅ REZOLVAT — 2026-10-28

**Appul a fost publicat în „In production".** Confirmat programatic, nu vizual:

- Răspunsul la `POST oauth2.googleapis.com/token` **nu mai conține**
  `refresh_token_expires_in` → câmpul există **doar** în „Testing".
  → appul e în Production → **tokenul nu mai are limita de 7 zile.**
- Re-consimțământ efectuat, token nou scris în secret manager
  (`GOOGLE_REFRESH_TOKEN_MAVIS_CLOUD`), **27 scope-uri**.
- `node mavis-tools/google-preflight.js` → toate cele **6** verificări OK.

**Ciclu de 7 zile: încheiat.** Nu mai e nevoie de re-autentificare săptămânală.

**Ce a rămas în urmă:** după publicare, un consimțământ nou e necesar **o singură
dată** — tokenul obținut *înainte* de publicare păstra limita de 7 zile. Acesta
e tokenul nou, de după publicare. **Gata.**

Detalii: `docs/GOOGLE-STATUS-2026-10-28.md`

---

## De ce contează (măsurat, nu estimat)

Refresh token-ul a fost obținut **2026-10-22 01:39 UTC**. App-ul OAuth e în modul
**Testing**, unde Google omoară refresh token-ul în **7 zile de la consimțământ**.
Deci tokenul moare în jur de **29 octombrie**.

În Testing, **fiecare re-autentificare e un ciclu de 7 zile.** Am bătut-o de trei
ori în septembrie–octombrie. Fixul nu e să re-autentificăm mai repede — e să
scădem de tot ciclul.

---

## Ce ai de făcut (în Google Cloud Console)

**1. OAuth consent screen** → verifică / completează:

| Setare | Valoare | De ce |
|---|---|---|
| User type | **External** | altfel nu apare pe conturi gmail.com |
| App name | ceva lizibil (ex. „Mavis Cloud") | apare pe ecranul de consimțământ |
| User support email | apvizual@gmail.com | obligatoriu |
| Developer contact email | apvizual@gmail.com | obligatoriu |
| Audience | **External** | obligatoriu pentru Publish |
| Test users | apvizual@gmail.com | necesar doar cât timp e în Testing |

**2. Publish app** → **In production**

> Pentru uz personal poate apărea „Google hasn't verified this app".
> **E normal** și nu blochează nimic. Verificarea completă (green check) se cere
> doar dacă app-ul servește alți oameni.

**3. (opțional) Authorized domains** — gol e OK pentru uz personal. Nu ai nevoie
de domeniu.

---

## De ce nu pot face eu

Consola Cloud cere **sesiune ta** cu `apvizual@gmail.com` și verificare în doi
pași. Credentialele mele sunt un **OAuth client** — nu sunt administrator de
proiect. Nu am și nu pot obține acces la pagina de administrare a proiectului.

---

## Ce fac eu imediat după

1. `node mavis-tools/google-refresh.js link` → link nou, împins în repo
2. Tu apeși Allow, îmi dai codul
3. `node mavis-tools/google-refresh.js code "<url>"` → token nou
4. Scriu tokenul în secret manager
5. `node mavis-tools/google-verify.js` → verificare live, per serviciu

**Timpul tău:** ~2 minute. **Al meu:** ~1 minut.

---

## Cum verificăm că s-a rezolvat

- Tokenul obținut **după** publicare → nu mai are limita de 7 zile
- `google-preflight.js` → pasul 4 OK, și rămâne OK peste 7 zile
- Proba reală: în `google_accounts` → **Securitate** → **Conexiuni cu terți**
  → aplicația `Mavis_Cloud` apare, iar conexiunea **nu mai expiră în 7 zile**

---

## Bonus: ce devine posibil abia după publish

- Tokenul trăiește până la revocare sau ~6 luni de inactivitate
- **Sesiunile paralele** devin permanente: azi fiecare re-autentificare într-o
  sesiune ar omorî tokenul celeilalte (vezi `docs/` — `prompt=consent` revocă)
- Nu mai ai nevoie de mine la fiecare 7 zile

---

*2026-10-22 · Mavis Cloud · singurul TO DO de pe lista ta care blochează un ciclu întreg*
