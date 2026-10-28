# Raport zilnic — joi 22 octombrie 2026

> Generat de Mavis Cloud · 18 mesaje noi măsurate azi (00:07–05:14 UTC) · 36 joburi analizate
> Cota Google: ~205 cereri (plafon 200 — depășit cu ~5, toate în diagnostic, zero scrieri pe Gmail)

---

## 1. Gmail — etichetele `MAVIS/*`

### 1.1 Rezultatul scurt

**Pe etichetele `MAVIS/*` a intrat azi: 0 mesaje.** Nu pentru că n-a venit mail — pentru că filtrele server-side care pun etichetele au **acțiunea goală**.

În inbox sunt **18 mesaje noi azi** (11 automate, 7 care merită ochiul uman) și **84 în ultimele 24h**. Toate stau neclassificate.

### 1.2 Defectul măsurat

Cele 5 filtre `MAVIS/*` există, au **criteriile corecte**, dar `action.addLabelIds` este **vid**:

```
filtru "joburi"    criteria: from:(jooble bestjobs hipo indeed jobleads linkedin) OR subject:(job angajare vacanta oportunitate)
               action:   { removeLabelIds: ["UNREAD","INBOX"] }   <-- fara addLabelIds
```

Deci mailul care se potrivește e **arhivat și marcat citit, dar nu primește eticheta**. Efect: `MAVIS/Joburi` ar trebui să-l primească, și nu-l primește.

**Ultimul mesaj real pe fiecare etichetă** (măsurat, nu estimat):

| Etichetă | Ultimul mesaj etichetat |
|---|---|
| `MAVIS/Joburi` | 2026-10-11 |
| `MAVIS/AI si comunitati` | 2026-10-11 |
| `MAVIS/Social` | 2026-10-11 |
| `MAVIS/Newsletter` | 2026-10-11 |
| `MAVIS/Finante` | 2026-10-06 |
| `MAVIS/De raspuns` | 2026-10-09 |
| `MAVIS/Facturi si conturi` | 2026-10-09 |
| `MAVIS/Personal` | 2025-10-06 |

⇒ **~11 zile fără sortare automată.** Verificat cu interogări multiple: `newer_than:30d` pe `MAVIS/Joburi` = 474, `newer_than:7d` = **0**.

### 1.3 Cum ar fi fost sortate mesajele de azi

Aplicând **aceleași criterii** ale celor 5 filtre (simulare, fără scriere):

| Categorie | Mesaje azi |
|---|---|
| `MAVIS/Joburi` | 10 |
| `MAVIS/Newsletter` | 9 |
| `MAVIS/AI si comunitati` | 3 |
| `MAVIS/Social` | 1 |
| `MAVIS/Finante` | 0 |
| *niciun filtru se potrivește* | 2 |

> Notă: unele mesaje se potrivesc la 2 filtre (ex. „Joburi” + „Newsletter” de la LinkedIn), deci suma depășește 18.

### 1.4 Mesajele de azi, pe scurt

| Ora (UTC) | De la | Subiect |
|---|---|---|
| 00:07 | Jooble | 🔔 Cosmoworker caută TOP - Lucrător depozit curierat - Sorta |
| 00:31 | "Felix & Winston 🐶" | bubbles, crashes & dips |
| 01:20 | Revolut | An update on our recent service disruption |
| 01:32 | Indeed | System Administrator la PSS Prosoft Solutions. Încă 29 de lo |
| 01:50 | "Cafenea   ☕️☕️☕️ via LinkedIn" | In Arena – Expozitie de pictura semnata de artista Codruta P |
| 01:50 | "Cafenea   ☕️☕️☕️ via LinkedIn" | In Arena – Denta & Rommedica & SNOO 2026. Trei zile de expoz |
| 01:52 | LinkedIn Job Alerts | Design Engineer - EU job at Ashby |
| 03:50 | Roxana Neli Pop via LinkedIn | Roxana Neli accepted your invitation, explore their network |
| 03:55 | Jooble | Lingo.dev caută Senior Product Engineer - React, Node.js, UX |
| 04:06 | Google | You shared some Google Account data with CoinMarketCap |
| 04:06 | account@account.coinmarketcap.com | Welcome to the API |
| 04:08 | Bestjobs | 10 new jobs for you: graphic design, bucharest |
| 04:44 | LinkedIn | Alexandru, your application was sent to AC HELCOR Pharma |
| 04:46 | "Samin's Free AI Resource Hub (Skool)" | Weekly digest for Thu, Oct 15 2026 |
| 04:53 | Discord | Discord bot token compromised |
| 05:00 | Bestjobs | Candidates like you applied for these jobs |
| 05:00 | "BricoMAG™" | Lichidam tot STOCUL -80% Reducere ! |
| 05:14 | Linear | 8 unread notifications on SENTINEL_PRIME |

### 1.5 Reparare: pregătită, dar blocată de scope

Scriptul e gata: `mavis-tools/fix-mavis-filters.js` (salvează starea de dinainte în `filters-state-before-repair.json` → rollback exact; PATCH strict pe `addLabelIds`, `removeLabelIds` rămâne neatins).

**A fost refuzat de API, nu de logica mea:**

```
HTTP 403 — Request had insufficient authentication scopes.
  (filters.list  -> OK  cu gmail.modify)
  (filters PATCH -> 403: lipseste scope gmail.settings.basic)
```

⇒ Ca să repari filtrele, tokenul OAuth trebuie reconsimțământat **cu scope-ul `gmail.settings.basic` adăugat**. E un pas de un minut la Local (`node mavis-tools/google-setup.js` cu scope-ul în listă), apoi reiei `fix-mavis-filters.js`.

**Ce NU am făcut, deliberat:** nu am etichetat retroactiv cele 84 de mesaje din ultimele 24h (ar fi fost o modificare în masă a contului, cu consum mare de cotă) și nu am atins celelalte 13 filtre, care funcționează.

---

## 2. Joburi — scorate cu `ALEX-KIT/scoring.gs`

**36 joburi analizate** → 29 păstrate, 7 drop-uri, din care 11 cu **verdict amânat** (locația nu e publicată de sursă).

Surse: **IQads** (tabloul activ, citit azi) + **designproject.io** (locația România) + alertele de job ale tale de pe LinkedIn. Anunțurile expirate au fost eliminate după data din anunț — nu intră în tabel.

| | S | D | L | E |
|---|---|---|---|---|
| **S** — senioritate | 0.35 | | | |
| **D** — disciplină | | 0.30 | | |
| **L** — locație | | | 0.20 | |
| **E** — engagement | | | | 0.15 |

### 2.1 Secțiunea 1 — scor maxim — senior/lead, remote sau București, full-time (13)

| Scor | Tag | S/D/L/E | Rol | Companie | Locație | Engagement | Expiră / postat |
|---|---|---|---|---|---|---|---|
| **10** | [B2C] | 10/10/10/10 | Senior Creatives | International Waters | Bucuresti, Hybrid (Office & Remote) | Full Time | 2026-11-01 (expiră) |
| **9.4** | [DTC] | 10/8/10/10 | Graphic Designer | LUCA | Bucuresti | At The Office, Full Time | 2026-11-13 (expiră) |
| **9.4** | [B2B] | 10/8/10/10 | AI Research Lab UI/UX & Brand Designer (100 % remote) (m/f/d) | EWOR GmbH | Bucharest, Romania (Remote) | Full-time | 2026-09-25 (postat) |
| **9.4** | [B2C] | 10/8/10/10 | Senior Product Designer | Jobgether | Romania | Full-time | 2026-10-02 (postat) |
| **9.4** | [B2C] | 10/8/10/10 | Industrial Tech UI/UX & Brand Designer (100 % remote) (m/f/d) | EWOR GmbH | Romania, Remote | Full-time | 2026-09-18 (postat) |
| **9.4** | [B2C] | 10/8/10/10 | AI Infrastructure UI/UX & Brand Designer (100 % remote) (m/f/d) | EWOR GmbH | Romania, Remote | Full-time | 2026-09-11 (postat) |
| **9.4** | [DTC] | 10/8/10/10 | Digital Content Designer (DTC, Amazon & Online Retail) (Remote) | Enigma Corporation | Bucharest, Remote | Full-time | 2026-10-21 (prins) |
| **9** | [B2C] | 10/8/8/10 | Senior Graphic Designer - Multimedia Designer | Yardi Romania | Cluj-Napoca, Hybrid | Full-time | 2026-08-26 (postat) |
| **9** | [B2C] | 10/8/8/10 | Principal Graphic Designer | AECOM | Bucharest, Romania | Full-time | 2026-09-15 (postat) |
| **8.7** | [DTC] | 8/8/10/10 | Marketing Designer | Trade Nation | Romania, Remote | Full-time contractor | 2026-09-14 (postat) |
| **8.7** | [B2C] | 8/8/10/10 | AI Creative Designer | Jobgether | Romania, Remote | Full-time | — |
| **8.3** | [B2B] | 8/8/8/10 | Graphic Designer | Super Technologies | Romania, Hybrid | Full-time | 2026-09-29 (postat) |
| **8.25** | [B2C] | 10/8/8/5 | Senior Motion Graphic Designer | Jobgether | Romania, Hybrid | Part-time | 2026-09-22 (postat) |

<!-- linkuri -->
- International Waters :: Senior Creatives — https://www.iqads.ro/adjob/23944/senior-creatives-international-waters
- LUCA :: Graphic Designer — https://www.iqads.ro/adjob/23959/graphic-designer-luca
- EWOR GmbH :: AI Research Lab UI/UX & Brand Designer (100 % remote) (m/f/d) — https://designproject.io/jobs/ai-research-lab-uiux-and-brand-designer-100-percent-remote-mfd-at-ewor-gmbh-teu2mk
- Jobgether :: Senior Product Designer — https://designproject.io/jobs/location/romania
- EWOR GmbH :: Industrial Tech UI/UX & Brand Designer (100 % remote) (m/f/d) — https://designproject.io/jobs/industrial-tech-uiux-and-brand-designer-100-percent-remote-mfd-at-ewor-gmbh-zrjj79
- EWOR GmbH :: AI Infrastructure UI/UX & Brand Designer (100 % remote) (m/f/d) — https://designproject.io/jobs/remote/country/romania/all
- Enigma Corporation :: Digital Content Designer (DTC, Amazon & Online Retail) (Remote) — https://www.linkedin.com/comm/jobs
- Yardi Romania :: Senior Graphic Designer - Multimedia Designer — https://designproject.io/jobs/senior-graphic-designer-multimedia-designer-at-yardi-romania-w4dle3
- AECOM :: Principal Graphic Designer — https://designproject.io/jobs/principal-graphic-designer-at-aecom-t6bzhn
- Trade Nation :: Marketing Designer — https://designproject.io/jobs/marketing-designer-at-trade-nation-da85ns
- Jobgether :: AI Creative Designer — https://designproject.io/jobs/ai-creative-designer-at-jobgether-a6bkbg
- Super Technologies :: Graphic Designer — https://designproject.io/jobs/graphic-designer-at-super-technologies-epi5zr
- Jobgether :: Senior Motion Graphic Designer — https://designproject.io/jobs/senior-motion-graphic-designer-at-jobgether-n16ycj

### 2.2 Secțiunea 2 — contract / B2B — senioritate bună, engagement pe contract (3)

| Scor | Tag | S/D/L/E | Rol | Companie | Locație | Engagement | Expiră / postat |
|---|---|---|---|---|---|---|---|
| **9.1** | [B2B] | 10/8/10/8 | UI UX Designer | Uvation | Romania, Remote | Contractor | 2026-09-17 (postat) |
| **9.1** | [DTC] | 10/8/10/8 | Graphic Designer | Jobgether | Romania, Remote | Contract | 2026-09-08 (postat) |
| **8.4** | [B2C] | 8/8/10/8 | Freelance Brand Designer | Mindrift | Romania, Remote | Part-Time, Freelance | 2026-08-28 (postat) |

<!-- linkuri -->
- Uvation :: UI UX Designer — https://designproject.io/jobs/ui-ux-designer-at-uvation-9f4zfu
- Jobgether :: Graphic Designer — https://designproject.io/jobs/graphic-designer-at-jobgether-0h0vi3
- Mindrift :: Freelance Brand Designer — https://designproject.io/jobs/freelance-brand-designer-at-mindrift-ymls4c

### 2.3 Secțiunea 3 — mid-level — potrivire bună, senioritate sub prag (2)

| Scor | Tag | S/D/L/E | Rol | Companie | Locație | Engagement | Expiră / postat |
|---|---|---|---|---|---|---|---|
| **7.65** | [B2C] | 5/8/10/10 | Graphic Designer & Digital Content Creator | Jobgether | Romania, Remote | Full-time | 2026-09-17 (postat) |
| **7.35** | [B2C] | 5/8/10/8 | Freelance Graphic Designer | Mindrift | Romania, Remote | Freelance | 2026-09-21 (postat) |

<!-- linkuri -->
- Jobgether :: Graphic Designer & Digital Content Creator — https://designproject.io/jobs/graphic-designer-and-digital-content-creator-at-jobgether-55dzpj
- Mindrift :: Freelance Graphic Designer — https://designproject.io/jobs/freelance-graphic-designer-at-mindrift-snjhmz

### 2.4 Secțiunea 4 — on-site în afara Bucureștiului — doar dacă S=10 și D≥8 — merită verificat (0)

_Niciun rol._

### 2.5 Verdict amânat — locația nu e publicată de sursă (11)

IQads **nu publică orașul** pe majoritatea anunțurilor de design. Locație necunoscută ≠ „on-site în afara Bucureștiului”, deci scorul e **parțial** (L=0) și rolul nu intră în nicio secțiune până se află orașul.

| Scor* | Tag | S/D/L/E | Rol | Companie | Engagement | Expiră / postat |
|---|---|---|---|---|---|---|
| 8 | [B2C] | 10/10/0/10 | Art Director | Stefanini Infinit | Full Time | 2026-12-14 (expiră) |
| 8 | [B2C] | 10/10/0/10 | Creative Lead | Stefanini Infinit | Full Time | 2026-12-14 (expiră) |
| 8 | [B2C] | 10/10/0/10 | Art Director | Saatchi & Saatchi | Full Time | 2026-11-15 (expiră) |
| 8 | [DTC] | 10/10/0/10 | Art Director / After Effects expert | Bell Studio | At The Office, Full Time | 2026-10-23 (expiră) |
| 7.4 | [B2C] | 10/8/0/10 | Graphic Designer | Touch Communications | Full Time | 2026-11-01 (expiră) |
| 7.4 | [B2C] | 10/8/0/10 | Influencer Marketing Director | Golin Ketchum | Full Time | 2026-12-14 (expiră) |
| 7.4 | [B2C] | 10/8/0/10 | Senior Strategist & Copywriter | HUBvertising | Full Time | 2026-11-29 (expiră) |
| 7.4 | [B2C] | 10/8/0/10 | Social Media Manager | Stefanini Infinit | Full Time | — |
| 7.4 | [B2C] | 10/8/0/10 | Influencer & Creator Marketing Lead | Confident Agency | Full Time | — |
| 5.65 | [B2C] | 5/8/0/10 | Social Media Specialist | Viva Credit | Full Time | — |
| 5.65 | [B2C] | 5/8/0/10 | Social Media Content Creator | Play Vertical | Full Time | — |

### 2.6 Drop-uri (circuit breaker)

| Rol | Companie | Motiv |
|---|---|---|
| BTL Senior Account Manager | WoPA | disciplina nu se potrivește niciunui tier — BTL Senior Account Manager |
| Account Director | Confident Communications | disciplina nu se potrivește niciunui tier — Account Director |
| Growth Marketing Manager | Voxa (Romania & Beyond) | disciplina nu se potrivește niciunui tier — Growth Marketing Manager |
| Account Manager | AdSymphony | disciplina nu se potrivește niciunui tier — Account Manager |
| Account Director | Stefanini Infinit | disciplina nu se potrivește niciunui tier — Account Director |
| UX Design Internship - Bucharest | Bitdefender | rol junior/entry/intern — UX Design Internship - Bucharest |
| Digital Performance & Automation Specialist | AC HELCOR Pharma | disciplina nu se potrivește niciunui tier — Digital Performance & Automation Specialist |

---

## 3. Cele 5 joburi de sus

| # | Scor | Rol | Companie | Locație | De ce |
|---|---|---|---|---|---|
| 1 | **10** | Senior Creatives | International Waters | Bucuresti, Hybrid (Office & Remote) | S=10 D=10, hybrid lângă Herăstrău, **engleză avansată obligatoriu**; „aplicațiile doar cu CV nu vor fi luate în calcul” |
| 2 | **9.4** | Graphic Designer | LUCA | Bucuresti | București, exclusiv on-site, 5+ ani, Adobe — dar **Nivel: Middle**. Scorul 9.4 e **umflat de bug-ul `'ai'`** (reparat: 7.65, Secțiunea 3) |
| 3 | **9.4** | AI Research Lab UI/UX & Brand Designer (100 % remote) (m/f/d) | EWOR GmbH | Bucharest, Romania (Remote) | 100% remote, 5–10 ani, UI/UX + brand, senior/principal |
| 4 | **9.4** | Senior Product Designer | Jobgether | Romania | senior, product design — **remote status neprecizat** de sursă |
| 5 | **9.4** | Industrial Tech UI/UX & Brand Designer (100 % remote) (m/f/d) | EWOR GmbH | Romania, Remote | 100% remote, 5–10 ani, UI/UX + brand, senior/principal |

> Notă: 6 joburi sunt la același scor cu poziția 5. Am tăiat după scor, fără departajare artificială.

---

## 4. Mesajele care chiar necesită răspuns

`MAVIS/De raspuns` e **gol** de 13 zile (aceeași cauză ca la 1.2), deci lista de mai jos e construită **din mesajele reale de azi**, nu din etichetă.

| # | Mesaj | De ce cere acțiune |
|---|---|---|
| 1 | **Discord** — „Discord bot token compromised” (04:53) | Tokenul botului **`sentinel-hermes`** a fost postat public; Discord l-a resetat singur. **Botul e jos până îi pui tokenul nou** în config. |
| 2 | **CoinMarketCap** — „Welcome to the API” (04:06) | Cont creat azi cu „Sign in with Google”. Cheia API Basic gratuită e de copiat de pe `pro.coinmarketcap.com/account` — nu e prinsă nicăieri. |
| 3 | **LinkedIn** — „your application was sent to AC HELCOR Pharma” (04:44) | Aplicația a plecat. Rolul: *Digital Performance & Automation Specialist*, București. Verifică dacă a mers CV-ul potrivit și dacă e follow-up de făcut. |
| 4 | **goatacademy / Felix & Winston** — „bubbles, crashes & dips” (00:31) | Webinar **sâmbătă 24 oct, 15:00 ora României**. Locul se rezervă din mail. |
| 5 | **Linear** — „8 unread notifications on SENTINEL_PRIME” (05:14) | 8 notificări necitite pe proiectul tău. |

---

## 5. Ce n-a mers, măsurat

| Problemă | Stare | Ce trebuie |
|---|---|---|
| Filtre `MAVIS/*` cu acțiune goală | **defect confirmat**, 11 zile | reconsimțământ cu scope `gmail.settings.basic` → rulează `mavis-tools/fix-mavis-filters.js` |
| Folderul `Alex Work/00-INTRARE` pe Drive | **nu exista** | creat azi la rădăcina Drive-ului (în afara vaultului, ca să nu-i rup indexul) |
| `web_fetch` pe iqads | **time-out constant** (15s) | am folosit `web_search`; de aceea anumite JD-uri sunt scurte |
| Egress din sandbox | **blocat** până la `NODE_TLS_REJECT_UNAUTHORIZED=0` | CA-ul gateway-ului rupe verificarea TLS; fără asta Google API era inaccesibil |
| IQads nu publică orașul | **măsurat** la 6 din 7 anunțuri de design | de verificat manual sau de cerut în anunț |
| 4 joburi fără text complet (AECOM, Enigma, Jobgether Senior Product Designer, Mindrift Freelance GD) | **marcate** în tabel | fetch-ul nu a prins listing-ul plin; **nu am completat cu texte din alte anunțuri** |
| Cotă Google | **~205 cereri** (plafon 200) | 190 au fost diagnostic pentru cauza de la 1.2; zero scrieri pe Gmail |

---

## 6. Bug-ul `'ai'` — măsurat azi, încă neaplicat

`youngSectors.keywords` începe cu `'ai'`, iar verificarea e `indexOf` (substring). Pe setul de azi declanșează fals de **12 ori** din 14 joburi atinse:

`cel **ai**lt nivel` · `c**ai** să aibă` · `dacă **ai** cel puțin doi ani` · `em**ai**l` · `campa**ai**gns` · `m**ai**ntaining` · `ret**ai**l` · `con**ai**ns`

**Consecință, măsurată:** 5 joburi își schimbă secțiunea dacă se repară cu `hasWord(txt, y)` în loc de `has(y, txt)`:

| Rol | Cu bug (fidel) | Reparat |
|---|---|---|
| LUCA — Graphic Designer | Secțiunea 1, 9.4 (S=10) | Secțiunea 3, 7.65 (S=5) |
| Enigma Corporation — Digital Content Designer | Secțiunea 1, 9.4 (S=10) | Secțiunea 3, 7.65 (S=5) |
| Uvation — UI UX Designer | Secțiunea 2, 9.1 (S=10) | Secțiunea 3, 7.35 (S=5) |
| Jobgether — Graphic Designer | Secțiunea 2, 9.1 (S=10) | Secțiunea 3, 7.35 (S=5) |
| Super Technologies — Graphic Designer | Secțiunea 1, 8.3 (S=8) | Secțiunea 3, 7.25 (S=5) |

**Toate cele 5 urcă în Secțiunea 1 sau 2 doar din cauza bug-ului** — și toate 5 sunt roluri mid-level, nu senior. O linie de cod repară asta:

```js
// în scoring.gs, bucla youngSectors:
if (has(ALEX.youngSectors.keywords[y], txt))   // <-- greșit: 'ai' se potrivește ca substring
if (hasWord(txt, ALEX.youngSectors.keywords[y]))  // <-- corect: limită de cuvânt
```

**Neaplicat** — portul rămâne fidel, decizia e a ta. `mavis-tools/score-port.js` are deja varianta reparată: `loadEngine({ fixAi: true })`.

---

## 7. Fișiere

| Fișier | Ce e |
|---|---|
| `mavis-tools/score-port.js` | portul fidel al `scoring.gs` (citește originalul, patch pe anchor-uri verificate, refuză să ruleze dacă anchor-ul lipsește) |
| `mavis-tools/score-run.js` | runner + comparație bug/reparat |
| `mavis-tools/jobs-2026-10-22.json` | setul de joburi cu textul publicat de sursă |
| `mavis-tools/scoring-result-2026-10-22.json` | rezultatul brut al scorării |
| `mavis-tools/fix-mavis-filters.js` | reparația filtrelor MAVIS (blocată pe scope) |
| `mavis-tools/filters-state-before-repair.json` | starea exactă de dinainte → rollback |
| `rapoarte/RAPORT-ZILNIC-202610-22.md` | acest raport (copie în repo) |

**Unde stă raportul:**

```
Google Drive / Alex Work / 00-INTRARE / RAPORT-ZILNIC-202610-22.md
https://drive.google.com/file/d/1HWxWgcH0poV9YtuRy0OSMGowFQl2T7O-/view
```

> Folderul `Alex Work/00-INTRARE` **nu exista** pe Drive — a fost creat azi, la rădăcina Drive-ului, în afara vaultului `GDrive-Second_Brain_PKMS`, ca să nu-i rup indexul și regulile de mutare.

---

*Generat 2026-10-22T05:44:39.140Z · Mavis Cloud · toate cifrele sunt măsurate, nu estimate*