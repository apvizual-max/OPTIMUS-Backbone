# `ALEX-KIT/scoring.gs` v1.0 — buguri MĂSURATE (2026-10-16)

Port JS rulat diferențial contra originalului: **acord 16/16** pe joburile cu
locație cunoscută. Deci cifrele de mai jos sunt ale engine-ului tău, nu ale
unei aproximări.

## 1. `'ai'` se potrivește ca SUBSTRING — `youngSectors.keywords`

Verificarea e `has(kw, txt)` → `indexOf(kw) !== -1`. `'ai'` e primul din listă.

Măsurat pe 25 joburi reale: **15/25** declanșează normalizarea de „sector
tânăr". **Doar 3** sunt roluri de AI adevărate.

Declanșatori falși: `mai`, `ai` (=*„eu am"*), `tailors`, `traininguri`,
`campaigns`, `email`, `claim`, `against`, `explain`, `daily`, `straight`,
`blockchain`, `hai`, `aici`, `aib`.

`mai` și `ai` sunt primele două cuvinte dintr-un anunț românesc oarecare.
Asta e exact clasa de bug notată pentru `ing|bt|taxi`. `hasWord` există în
același fișier (linia ~49) — lista de sectoare tinere nu-l folosește.

**Impact azi: 1 job** (6.70 → 5.65). Distribuția pe secțiuni nu se schimbă.
Nu arde acum, dar e bombă.

Corecție de o linie, **verificată** (15 → 3 declanșări):
```js
if (hasWord(txt, y))   // în loc de has(y, txt)
```

**NU am aplicat** — portul e fidel, decizia e a lui.

### Măsurătoare 2026-10-19 — cât de mult strică AZI

Rulare paralelă (port fidel vs. port cu `hasWord`), 57 joburi, 40 păstrate:

| Secțiune | cu bug | cu fix | delta |
|---|---|---|---|
| 1 | 15 | 14 | −1 |
| 2 | 6 | 5 | −1 |
| 3 | 3 | 5 | +2 |

`'ai'` a declanșat la **30 din 40** joburi păstrate (cuvinte românești ca
„campanii", „câștigă", „email", „real-estate"). Doar **2 joburi își schimbă
secțiunea**: Super Technologies (1→3), Jobgether Graphic Designer (2→3).
**Distribuția nu se schimbă fundamental.** Fix-ul rămâne neaplicat — decizia
e a lui.

## 2. Locație necunoscută e tratată ca on-site în afara Bucureștiului

```js
if (!isRemote && !inBU) { ... return {dropped:true, ...} }
```

Locația lipsă (`''` sau orice text fără keyword) → `isRemote=false`,
`inBU=false` → **circuit breaker cu concluzie falsă**.

**iqads.ro nu publică orașul pe 8 din 12 anunțuri de design.** Deci nu e
ipoteză, e măsurătoare pe sursa reală.

În port am adăugat ramura `locUnknown → L=0, section 0, partial`, grup
separat „Verdict amânat", scor parțial. Diferența: **1 job** (Body Tailors
Pilates) ar fi fost drop-at fals.

**Ramura `locUnknown` se aplică ÎNAINTE de excepția pentru Secțiunea 4.**
(2026-10-19: prima variantă punea `locUnknown` după, și joburi fără oraș
publicat intrau în Secțiunea 4 = „on-site în afara Bucureștiului", ceea ce
e o afirmație falsă despre sursă. Corectat: locație necunoscută → întotdeauna
Secțiunea 0, **inclusiv** când S=10/D≥8/E≥8.)

**De ce contează:** IQads nu publică orașul (49 active → doar 8 îl spun).
Fără această ramură, cele mai bune roluri creative ale zilei (Saatchi,
Stefanini ×2, ontheroof) ar fi fost fie drop-ate, fie puse greșit în Secțiunea 4.

## 3. Tier-ul Emerging Sectors nu acoperă rolurile AI hibride

`AI Native Storyteller` @ Smartheads → drop-at, *„disciplina nu se potrivește
niciunui tier"*. Tier 4 are `ai designer`, `ai creative`, `ai strategist`,
`prompt engineer` — **nu** `storyteller`, `ai native`, `content lead`.

Nu e eroare de potrivire, e lipsă de acoperire. Decizia e a lui.

## Metodă reutilizabilă

Nu porta `scoring.gs` și nu declara corect fără test. E Apps Script; rulează
`scoreJob`/`scoreBatch` ca JS pur (nu ating funcțiile cu `SpreadsheetApp` /
`DriveApp`) într-un fișier separat, apoi **dif-test** pe cazuri cu locație
cunoscută. Așa s-a prins că portul e corect: 16/16, zero diferențe.

## Ozon de corectitudine

Axa `L` depinde de `location`, iar `REMOTE_KW` se verifică contra **ambelor**
(`loc` și `txt`), dar `BUCHAREST_KW` **doar** contra `loc`. Deci ceea ce
trebuie populat cu atenție e exact câmpul `location` — nu textul anunțului.
Acolo se hotărăște dacă un rol intră în secțiuni sau e drop-at.


## 4. BUG NOU: „remote" în negatie — fals pozitiv (măsurat 2026-10-21)

`REMOTE_KW` se verifică contra `loc` ȘI contra `txt`, cu `indexOf` (substring).
O frază **negată** declanșează fals:

> „activitatea se desfasoara exclusiv la sediul din BUCURESTI, **nu se lucreaza remote/hybrid**"

→ `has('remote', txt)` = true → `isRemote = true` → **L=10 în loc de L=8**.
Scor 7.65 în loc de 7.25. Secțiunea nu se schimbă (3).

Măsurător: IQads (LUCA, `adjob/23959`). Diferența apare doar dacă textul conține
cuvântul „remote" negat. Corecția ar fi negare-aware, dar engine-ul e Apps Script
și nu are parser de propoziții. **Neaplicat** — portul rămâne fidel.

## 5. Impactul bug-ului 'ai' — măsurătoare 2026-10-21

Port fidel vs. port cu `hasWord` pe `youngSectors`, 59 joburi, 40 păstrate:

| Secțiune | fidel | cu fix |
|---|---|---|
| 1 | 22 | 20 |
| 2 | 3 | 1 |
| 3 | 8 | 12 |

**4 joburi își schimbă secțiunea:** Mindrift Freelance Brand Designer (1→3),
Uvation UI UX Designer (2→3), Jobgether Graphic Designer (2→3),
Super Technologies Graphic Designer (1→3).

Concluzie: bugul **mătură azi topul**, nu doar coada. Super Technologies și
Mindrift apar în Secțiunea 1 doar din cauza lui. Decizia de a repara e a lui Alex —
o linie: `hasWord(txt, y)` în loc de `has(y, txt)`.

## 6. Metodă: port fără transcriere

Nu rescrie `scoring.gs` în JS. Îl citește, aplică **o singură inserție** cu
`String.replace` pe un anchor exact, apoi îl evaluează cu `new Function(...)`.
Anchor-ul e verificat: dacă nu se găsește, portul **refuză să ruleze** (`throw`),
în loc să dea cifre greșite. Asta elimină orice divergență port↔original.
Fișier: `mavis-tools/score-port.js` în repo-ul `apvizual-max/MAVIS-CLOUD`.


## 7. Măsurătoare 2026-10-22 — portul e în repo, bug-ul 'ai' urcă roluri mid-level

**`mavis-tools/score-port.js` există acum în `apvizual-max/MAVIS-CLOUD`** (commit
`44ee1ef`). Nu era acolo când am căutat — topicul îl descria ca existent, dar
nu se găsea în niciun repo. L-am reconstruit după metoda documentată: citește
`ALEX-KIT/scoring.gs`, inserări pe anchor-uri EXACTE (refuză să ruleze dacă
anchor-ul lipsește sau e ambiguu), evaluează cu `new Function`. Inserția
funcțională unică e ramura `locUnknown` (L=0, secțiune 0, înainte de excepția
pentru Secțiunea 4).

**Măsurătoare de azi: 36 joburi, 29 păstrate, 7 drop-uri, 11 cu verdict amânat.**

Declanșatori falși ai lui `'ai'` întâlniți azi, toți reali:
`cel **ai**lt nivel` · `c**ai** să aibă` · `dacă **ai** cel puțin doi ani` ·
`em**ai**l` · `campa**ai**gns` · `m**ai**ntaining` · `ret**ai**l` · `con**ai**ns`.
**12 declanșări false din 14 joburi atinse.**

**Impactul azi: 5 joburi își schimbă secțiunea** — și ăsta e semnalul important,
pentru că **toate 5 urcă în Secțiunea 1 sau 2 doar din cauza bug-ului**:

| Rol | fidel | reparat |
|---|---|---|
| LUCA — Graphic Designer | Sec. 1, 9.4 (S=10) | Sec. 3, 7.65 (S=5) |
| Enigma Corporation — Digital Content Designer | Sec. 1, 9.4 (S=10) | Sec. 3, 7.65 (S=5) |
| Uvation — UI UX Designer | Sec. 2, 9.1 (S=10) | Sec. 3, 7.35 (S=5) |
| Jobgether — Graphic Designer | Sec. 2, 9.1 (S=10) | Sec. 3, 7.35 (S=5) |
| Super Technologies — Graphic Designer | Sec. 1, 8.3 (S=8) | Sec. 3, 7.25 (S=5) |

**Concluzia azi e mai puternică decât pe 19 și 21 oct:** bug-ul nu mută joburi
din coadă în vârf — **promovează roluri MID-LEVEL în Secțiunea 1**, adică exact
topul raportului zilnic. Un designer mid cu 5 ani ajunge să pară senior doar
pentru că „dacă **ai** cel puțin doi ani" conține șirul „ai".

**Decizia rămâne a lui Alex** (o linie: `hasWord(txt, y)` în loc de `has(y, txt)`).
Portul oferă deja comparația: `loadEngine({ fixAi: true })`.

> **Mutat în topicuri dedicated:** filtrele MAVIS/* (etichetare fără
> `addLabelIds`, scope lipsă `gmail.settings.basic`) → topicul
> `gmail-sorting-filters`. Contorul de cereri Google și regulile de economisire
> a API-ului (§10, §12, §13) → topicul `raport-zilnic-pipeline`.


## 8. Măsurătoare 2026-10-23 — două clase NOI de fals pozitiv

### 8.1 Axa D se calculează din PROSA anunțului, nu din titlul rolului

Tier-urile `DISCIPLINE` se verifică contra `txt` = rol + anunț + note. Consecință:
un rol care **nu** e de design intră în Secțiunea 1 cu 9.4 doar pentru că textul
lui conține „social media" (tier Core Design) sau „art director" (tier Creative
Leadership).

**Măsurat azi: 16 joburi / 20 semnalări.** Cele mai vizibile:
- *Graphic Designer & Digital Content Creator* @ Jobgether → **D=10** (Creative
  Leadership) doar fiindcă proza AI menționează „art director" o dată.
  Fără ea: D=8 → **8.7 în loc de 9.3**.
- 8 joburi de tip account/PR/media (Media Relations Specialist, PR Manager,
  Account Manager @ AdSymphony, Digital Account Manager @ WoPA, Copywriter și
  Digital Media Specialist @ Stefanini, Digital Marketing Specialist @ Alpha
  Clinic, Influencer & Creator Marketing Lead) intră în Secțiunea 1 cu **9.4**
  doar prin „social media" din text.

**Cazul e mai grav decât bug-ul 'ai'**, pentru că *proza* e generată de AI și
de aceea e plină de cuvinte de tier. 2026-10-22 → 2026-10-23, designproject.io
și-a rescris descrierile de la 71–1484 la **24.000–33.000 de caractere**
(inclusiv „📝 Enhancement Note"). Diferența de scor față de ieri nu înseamnă
că jobul s-a schimbat.

**Propunere (NEAPLICATĂ — decizia e a lui Alex):** ca `D` să se calculeze din
**titlul rolului**, sau ca un rol să poată intra într-o secțiune doar dacă
titlul conține o cheie de design.

### 8.2 „Remote Status: Hybrid" — eticheta declanșează fals `isRemote`

Variantă nouă a bug-ului #4 (negatia). designproject.io pune în descriere
linia `Remote Status: Hybrid`. `REMOTE_KW` include `'remote'` și se verifică
contra `txt` → `isRemote = true` → **L=10 în loc de L=8**.

Afectează azi: AECOM Principal Graphic Designer, Super Technologies Graphic
Designer, METRO/MAKRO Senior UX/UI Designer. Diferență 0.4 puncte/job.
**NEAPLICAT.**

## 9. Filtrele MAVIS/* nu se aplică DELOC (nu doar `addLabelIds` vid)

Măsurător azi: **510 mesaje în inbox în 7 zile** (azi 12, 24h 99). Mail de job
intrat azi (Bestjobs 07:49, Jooble 03:55, LinkedIn Job Alerts 03:50) e **în
continuare INBOX + UNREAD** — deci filtrul cu `removeLabelIds:["UNREAD","INBOX"]`
nici măcar nu arhivează. Criteriile lui sunt corecte (verificate pe criteria
completă). ⇒ filtrele nu se aplică pe mailul nou, nu doar nu pun eticheta.

**Cauza probabilă:** etichetarea se făcea de un script **local**
(`mavis-tools/email-sort-full.js`, rulează pe calculatorul lui Alex), iar
filtrele din Gmail doar arhivează. Scriptul nu mai rulează de 12 zile
(ultima etichetare reală: 2026-10-11).

## 10. Contor de cereri Google — instrumentat în `kit.js`

> Mutat în topicul `raport-zilnic-pipeline` (secțiunea „Economisirea de cereri").
> `mavis-tools/kit.js` numără fiecare apel spre `googleapis` și scrie
> `mavis-tools/.api-usage.json` la ieșirea procesului (per-script) — regula
> "max 200 cereri/rulare" se respectă **fără estimări**.


## 11. CORECTARE 2026-10-24 — `validThrough` la designproject.io E EXPIRARE REALA

Până azi raportul tratase `validThrough` ca fiind inutilizabil: `expKind='postat'`
pentru designproject.io, cu justificarea „e derivat și uneori în trecut, deci ar
însala tabelul". **Acea justificare e greșită.**

Măsurat pe toate cele 26 de joburi: `validThrough` = `datePosted` + **30 zile**
exact (24/26 exacte; 2 cu o zi diferență de fus orar). Deci e o fereastră de
postare de 30 de zile, nu o valoare derivată fără sens.

Consecință: **7 din cele 36 joburi din tabele erau deja expirate** și nu se
puteau aplica — fără niciun semn, pentru că raportul afișa data postării, nu
data expirării. Corectat: `expKind='expiră'` pentru ambele surse, plus flag
`expired` și marcajul `⛔ **EXPIRAT**` în tabele.

**Regulă generală:** când o valoare „derivată" se dovedește constantă față de
alta, e o relație reală, nu gunoi — și merită folosită. Verifică relația pe
TOATĂ setul înainte să o ignori. (Corectat și în `report-score.js`: `expKind`
a devenit `'expiră'` pentru ambele surse, iar `expiry` e normalizat la AAAA-LL-ZZ.)

## 12. `messages.list` întoarce ID-urile în ordine descrescătoare după data internă

> Mutat în topicul `raport-zilnic-pipeline` (secțiunea „Economisirea de cereri").
> Rezumat: `c.ids[0]` e deja cel mai nou ⇒ 25 `messages.get`/etichetă → 4
> (`report-mail-count.js` a coborât de 403 la 60 cereri).

## 13. `report-inbox.js` (105 cereri) nu era folosit de nimeni

> Mutat în topicul `raport-zilnic-pipeline` (secțiunea „Economisirea de cereri").
> Rezumat: ieșirea lui nu e citită de nimeni; numărătoarea exactă vine din
> `report-inbox-counts.js` (8 cereri).
