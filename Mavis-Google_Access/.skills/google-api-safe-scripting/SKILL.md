---
name: google-api-safe-scripting
description: Rulează API-uri Google (Gmail, Drive, Calendar, Sheets) fără să arzi cota. Folosește-l ÎNAINTE de orice script, task în fundal, buclă sau procesare în masă pe contul lui Alex.
---

# Google API — scripting fără să arzi cota

## 1. ÎNTÂI: identică metoda, APOI calculează costul

Costul nu depinde de câte cereri faci, ci de **ce metodă** apeși.

| Metodă | Unități | Când |
|---|---|---|
| `history.list` | **2** | sincronizare incrementală |
| `messages.list` | **5** | **lista ID-uri. 95% din cazuri.** |
| `messages.modify` | 5 | etichete, arhivare, mark-read |
| `messages.batchModify` | 5 | etichete în masă — **în loc să apelezi modify de mii de ori** |
| `messages.get` | **20** | **doar dacă ai nevoie de conținut** |
| `messages.trash` | 20 | coș |
| `threads.list` | 5 | **lista thread-uri — nu itera mesaje unul câte unul** |
| `threads.get` | 40 | conținut de thread |
| `messages.delete` | 10 | ⚠️ **interzis fără comanda lui** |
| `messages.send` | 100 | ⚠️ **interzis fără comanda lui** |

## 2. Limitele oficiale (documentație Google, actualizată 01.05.2026)

| Limită | Valoare |
|---|---|
| Per minut, per utilizator | **6.000 unități** |
| Per minut, per proiect | 1.200.000 unități |
| Prag zilnic de facturare | 80.000.000 unități |

## 3. Formula de planificare — calculează ÎNAINTE să rulezi

```
unități_estimate = (nr_listări × 5) + (nr_get × 20) + (nr_modify × 5) + (nr_trash × 20)
timp_minut      = unități_estimate / 6.000
```

Exemplu: 34.000 de mesaje
- ❌ `messages.get` × 34.000 = **680.000 unități = 113 minute** → arzi câtă în 2
- ✅ `threads.list` × 68 pagini = 340 unități → **instant**

## 4. Managerul de cotă — folosește-l, nu improviza

`/workspace/mavis-tools/quota.js` — buget de unități per minut de 60 sec, cu reset automat.

```js
const QUOTA = require('./quota.js');
await QUOTA.reserve('messages.list');   // așteaptă dacă nu e buget
```

## 5. Backoff — obligatoriu la 429 sau 403 rateLimitExceeded

```js
if (resp.statusCode === 429 || (resp.statusCode === 403 && /rateLimit|Quota/i.test(body))) {
  const wait = resp.headers['retry-after']
    ? +resp.headers['retry-after'] * 1000
    : Math.min(32000, 1000 * 2 ** attempt) + Math.random() * 500;
  // max 5 încercări
}
```

**429 e retry-abil. Nu opri procesul, încetinește.**

## 6. Regulile de aur

1. **`list` înainte de `get`, mereu.** Dacă nu ai nevoie de corpul mesajului, `list` ajunge.
2. **Iterează pe thread-uri, nu pe mesaje**, când vrei să lucrezi pe conversații.
3. **`batchModify` / `batchTrash` / filtre pe server** — în loc de mii de apeluri individuale.
4. **Filtrul pe server > scriptul care rulează.** Un filtru Gmail se aplică singur, la fiecare mail, pentru totdeauna. **Când se poate, folosește filtru, nu buclă.**
5. **Rulările lungi: în fundal, cu log.** Nu bloca sesiunea, nu pierde output-ul.
6. **Verifică `resp.statusCode` la scriere.** Un 403 ignorat arată ca succes fals.
7. **Niciodată `messages.delete` sau `messages.send` într-un script.** Doar la comanda lui, în momentul ăla.

## 8. Curăț după tine

Orice folder, etichetă, document de test creat pentru verificare → **mutat în Trash**, nu șters definitiv. Și raportează ce ai lăsat.

## 9. Când ceva e blocat

**Citește mesajul de eroare complet, înainte să reacționezi.** E poartă la cauză.
- `403 insufficient authentication scopes` → scope, nu rată
- `403 Quota exceeded` → cost, nu rată
- `401 invalid authentication credentials` → token, **refresh înainte să reformulezi ceva**
- `404 fileNotDownloadable` → Google Docs vrea **export**, nu `alt=media`
- Timeout / ENOTFOUND → rețea, nu logică

**Niciun hardcod fără sursă.** Niciun timeout, niciun delay, niciun `maxGap` care nu vine dintr-un document oficial sau dintr-o măsurătoare.
