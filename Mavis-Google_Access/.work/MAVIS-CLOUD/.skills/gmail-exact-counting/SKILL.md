---
name: gmail-exact-counting
description: Cum numarzi exact thread-uri/mailuri in Gmail prin API. resultSizeEstimate e plafonat si nu se foloseste niciodata ca numaratoare.
---

# Numarare exacta in Gmail prin API

## De ce nu merge metoda obisnuita

Gmail `messages.list` si `threads.list` intorc `resultSizeEstimate`. **Este o estimare plafonata**, nu
o numaratoare. In practicile conturi de lucru mari intoarce aceeasi valoare mica (ex. `201`) pentru
interogari total diferite — un query pe 300 de mailuri si unul pe 30.000 de mailuri.

Daca vei folosi acea valoare ca numaratoare vei raporta cifre false si vei strange o gramada de
baza de date intr-un fel si altul fara sa stii.

**Regula: `resultSizeEstimate` se foloseste doar ca semnal de "mai sunt rezultate", niciodata ca numar.**

## Metoda corecta

Numara prin **paginare reala** cu `threads.list`, insumand efectiv thread-urile primite.

```js
async function count(query, cap) {
  let page = null, total = 0;
  do {
    const url = 'https://gmail.googleapis.com/gmail/v1/users/me/threads?q='
      + encodeURIComponent(query) + '&maxResults=500'
      + (page ? '&pageToken=' + encodeURIComponent(page) : '');
    const r = await req('GET', url);
    total += (r.threads || []).length;
    page = r.nextPageToken || null;
    if (total >= cap) return { total, capped: true };   // plafon: cifre mai mare, nu stiu exact
    if (page) await sleep(260);                          // 260ms intre pagini = sub limita de rata
  } while (page);
  return { total, capped: false };
}
```

Scriptul exista deja: `/workspace/mavis-tools/email-count.js` (plafon 4.000, rapid, pentru stare curenta)
si `/workspace/mavis-tools/email-count-exact.js` (plafon 60.000, lent, pentru numarare definitiva).

## Reguli deQuota

- `threads.list` costa **5 unitati** pe pagina de 500, deci o pagina e ieftina. Numarat e mult mai
  ieftin decat apelurile individuale pe `messages.get` (100 unitati fiecare).
- 260-320 ms intre pagini. Sub 200 ms riști sa primesti 429.
- Pune **intotdeauna un plafon** si raporteaza-l ca „4.000+" cand e atins. Nu inventezi cifra.

## Cei 3 arbori critici

Gmail are arbori ascunsi care **nu apar in nicio interogare obisnuita**:
- `in:anywhere` — include Spamma si Gunoi. `in:trash` prinde doar gunoiul.
- `in:sent`, `in:draft`
- `label:IMPORTANT`

Cand verifici „tot emailul", foloseste `in:anywhere` si **verifica separat** fiecare categorie.
Un cont bine organizat poate avea `in:inbox` = 0 si totusi 30.000 de mailuri — de aceea cleanup-ul
pe inbox nu e suficient.

## Regula de comunicare

Daca un numar vine dintr-o estimare plafonata sau dintr-un log de proces, **spune exact de unde vine**.
Nu prezenta un numar ca fact, daca nu l-ai numarat. Vezi protocolul din `alex-collaboration-protocol`:
Alex cere onestitudine despre limite, nu cifre care par bune.
