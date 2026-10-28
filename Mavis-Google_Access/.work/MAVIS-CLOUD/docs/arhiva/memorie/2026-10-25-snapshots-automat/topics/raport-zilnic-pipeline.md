# Raport zilnic pentru Alex — pipeline, reguli și măsurători

Raportul **nu se mai construiește ad-hoc**: e o secvență de scripturi în
`apvizual-max/MAVIS-CLOUD`.

## Ordinea scripturilor

```bash
node mavis-tools/scrape-iqads.js            # catalog AdJob complet
node mavis-tools/scrape-designproject.js    # JSON-LD JobPosting
node mavis-tools/report-mail-count.js 2026/10/23   # etichete MAVIS/* (4 ferestre)
node mavis-tools/report-inbox-counts.js     # numarătoare exactă inbox
node mavis-tools/report-simulate-sort.js    # simularea sortării + mesajele de azi
node mavis-tools/report-score.js            # port fidel scoring.gs + diagnostice
node mavis-tools/report-build.js 2026-10-23 <FOLDER_ID>   # scrie .md + urcă pe Drive
```

Destinație Drive: `Alex Work/00-INTRARE` = `1sAs2ktJhGanKeGv87LIxkTD34S7P5XvT`.
Raportul se **actualizează in place**, nu se creează duplicat.

## Reguli de pipeline

- **Nu șterge, nu trimite, nu modifică Gmail.** Orice acțiune e anulabilă.
- **Cota de 200 cereri Google/rulare** se raportează explicit, cu defalcare pe etape.
- `.api-usage.json` (scris de `kit.js` la ieșirea procesului) ține contul — regula
  "max 200 cereri" se respectă **fără estimări**.
- **Șablonul e complet data-driven.** Nicio cifră sau narativă scrisă cu mâna în
  cod (motivul rescrierii din 2026-10-24: template-ul avea „a intrat azi: 0
  mesaje", „12 zile", „48 joburi IQads" scrise de mână → mâine ar fi repostat
  cifrele de azi).
  - `report-build.js --dry` scrie raportul local, **nu atinge Drive**.
  - `report-score.js --save-set` salvează setul normalizat (`jobs-AAAA-LL-ZZ.json`)
    ca PREV; `prevRunDate` și `prevRes` se derivă din numele fișierului PREV.
  - `mavis-tools/email-leads-AAAA-LL-ZZ.json` (opțional) — leads verificate;
    raportul sare peste secțiune dacă fișierul nu există.
  - `report-inbox-counts.js` și `report-simulate-sort.js` iau data ca argument.

## Triage (`mavis-tools/report-triage.js`)

Clasifică mesajele DIN DATE în 5 clase: `needs-reply` / `needs-action` /
`job-alert-other` / `fyi` / `noise`.

**Ordinea regulilor contează:** newsletter se verifică **înainte** de semnalul de
„răspuns" — altfel un digest cu cuvântul „interview" în snippet era clasificat
ca needs-reply.

Ultima rulare (2026-10-24): 1 needs-reply, 2 needs-action, **116 noise**
(Jules + GitHub Actions pe repo-uri proprii).

## Economisirea de cereri

- **`messages.list` întoarce ID-urile în ordine descrescătoare** după data
  internă ⇒ `c.ids[0]` e deja cel mai nou. În `report-mail-count.js` erau 25
  `messages.get`/etichetă doar ca să afli „ultimul mesaj etichetat" = **200 de
  cereri singure**, peste buget. Redus la 4/etichetă ⇒ scriptul a coborât de
  **403 la 60 cereri**.
  *Regulă:* înainte să ceri corpul unui mesaj, verifică dacă lista nu ți-a dat
  deja ordinea. `threads.list` la fel.
- **`report-inbox.js` (105 cereri) nu era folosit de nimeni** — ieșirea
  (`report-inbox.json`) nu e citită de `report-build.js` sau de alt script.
  Numărătoarea exactă vine din `report-inbox-counts.js` (8 cereri).
  *Regulă:* când un pas costă mult, verifică întâi dacă ieșirea lui e consumată
  înainte să-l optimizezi. Optimizarea unui script mort e muncă pierdută.

## Scor

`mavis-tools/score-port.js` — port fidel al `ALEX-KIT/scoring.gs` (vezi topicul
`scoring-gs-buguri-masurate`).

## `validThrough` la designproject.io = expirare REALĂ

Până la 2026-10-24 raportul trata `validThrough` ca fiind gunoi (`expKind='postat'`,
justificare „e derivat și uneori în trecut"). **Justificarea era greșită.**

Măsurat pe toate cele 26 de joburi: `validThrough` = `datePosted` + **30 zile**
exact (24/26 exacte; 2 cu o zi diferență de fus orar). Deci e o fereastră de
postare de 30 de zile, nu o valoare derivată fără sens.

Consecință: **7 din cele 36 joburi din tabele erau deja expirate**, fără niciun
semn, pentru că raportul afișa data postării, nu data expirării. Corectat:
`expKind='expiră'` pentru ambele surse, flag `expired`, marcajul `⛔ **EXPIRAT**`.

**Regulă generală:** când o valoare „derivată" se dovedește constantă față de
alta, e o relație reală, nu gunoi — și merită folosită. Verifică relația pe
TOATĂ setul înainte să o ignori.

## Capcană: descrierile rescrise cu AI

2026-10-22 → 2026-10-23, designproject.io și-a rescris descrierile de la
71–1484 la **24.000–33.000 de caractere** (inclusiv „📝 Enhancement Note").
Diferența de scor față de ieri nu înseamnă că jobul s-a schimbat. A stricat 2 din
3 surse de engagement — vezi skill-ul `job-sourcing-methods` („care e adevărul
despre engagement").

## Măsurători

| Zi | Mesaje | MAVIS/* | Joburi analizate | Păstrate | Verdict amânat | Postări noi | Cereri Google |
|---|---|---|---|---|---|---|---|
| 2026-10-23 | 125 (00:00–08:15 EEST) | 0 | 72 (46 IQads + 26 DP) | 36 | 14 | 0 | 422 (depășit) |
| 2026-10-24 | — | 0 (sorting oprit de 12 zile) | 72 | 36 | 14 | 0 | 200 (exact) |

0 postări noi: max ID IQads 23997 neschimbat; cel mai recent designproject.io
e din 2026-10-06. **Nu e blocaj de scraping — e realitate de piață.**

## Lead nou, verificat pe pagină (2026-10-24)

Alerta Jooble „YO AI Labs caută Graphic designer - Remote" →
`yoailabs.com/remote-jobs/graphic-designers` — **121 roluri de design remote,
contract, 5 platforme** (Micro1, SuperAnnotate, Ethos AI, AfterQuery, Handshake AI).

Rate-uri publicate: Graphic Designer $30–105/h, Graphic Designer / UI-UX Designer
(Ethos AI) **până la $150/h**, Creative Director până la $80/h, Brand Director
până la $70–80/h. Contract cu **platforma**, nu cu YO AI Labs. Interviu AI +
assessment de domeniu.

**Batează direct cu Traseul 2** (bani din proiecte + produse / freelance + AI).

## Istoric relevant

- 2026-10-21: 59 joburi analizate (12 IQads + 47 DP) → 40 păstrate, 7 verdict
  amânat, 19 drop-ate; scor top 9.6 (International Waters :: Senior Creatives).
  Livrat ca mirror local în workspace, pentru că Drive era încă inaccesibil.
- 2026-10-24: rescriere completă a `report-build.js` (commit `439c678`).


## Sonde noi (25.10) — raportul nu mai repetă cifrele de ieri

- `mavis-tools/report-source-probe.js` → `report-source-probe.json`: măsoară azi
  comportamentul surselor (lungimea descrierilor designproject.io, `employmentType`
  vs linia „Job Type:", paginatia IQads/designproject). **Zero cereri Google.**
- `mavis-tools/report-filter-state.js` → `report-filter-state.json`: citește
  filtrele live și **testează** semantica Gmail (cum e scris acum vs cum ar trebui
  scris cu `{}`). 20 cereri — e cea mai scumpă sondă, rulează-o doar dacă e nevoie.
- `mavis-tools/report-folder-discover.js`: găsește pe Drive folderul de livrare
  pe CALE (fără id-uri hardcodate). 4 cereri.
- `report-build.js` citește sondele în locul cifrelor scrise cu mâna. La rulare
  **reia contorul** `.api-usage.json` (nu-l reseta între rulări) — altfel
  raportul raportează greșit.

**Cost real măsurat 25.10:** 198 cereri Google pentru o rulare completă
(folder-discover 4 + inbox-counts 9 + mail-count 59 + simulate-sort 89 +
filter-state 20 + inline 11 + build/upload 6). Plafonul de 200 e atins aproape —
dacă adaugi o sondă nouă, scoate altă una.
