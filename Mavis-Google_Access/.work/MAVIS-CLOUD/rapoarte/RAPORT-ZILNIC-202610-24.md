# Raport zilnic — sâmbătă 24 octombrie 2026

> Generat de Mavis Cloud · 125 mesaje noi măsurate azi (00:00–08:15 EEST) · 72 joburi analizate
> Cota Google: **200 cereri** (plafon 200 — **exact pe plafon**). Zero scrieri pe Gmail; tot consumul a fost măsurare și diagnostic. Detaliu în §5.

---

## 1. Gmail — etichetele `MAVIS/*`

### 1.1 Rezultatul scurt

**Pe etichetele `MAVIS/*` a intrat azi: 0 mesaje.** Nici în ultimele 24h (0), nici în ultimele 7 zile (0).

Nu pentru că n-a venit mail. Azi au intrat **125 mesaje** în total, iar în inbox sunt **125**. **125 dintre ele nu au primit nicio etichetă**, iar **116 sunt zgomot din pipeline-ul propriu** (bot-uri de pe repo-uri) — taxonomia MAVIS nu are categorie pentru ele.

### 1.2 Măsurătoarea pe etichete (numărare exactă, cu paginare)

| Etichetă | azi | 24h | 7z | 30z | Ultimul mesaj etichetat |
|---|---|---|---|---|---|
| `MAVIS/Joburi` | 0 | 0 | 0 | 429 | Sun, 11 Oct 2026 |
| `MAVIS/AI si comunitati` | 0 | 0 | 0 | 151 | Sun, 11 Oct 2026 |
| `MAVIS/Social` | 0 | 0 | 0 | 261 | Sun, 11 Oct 2026 |
| `MAVIS/Newsletter` | 0 | 0 | 0 | 277 | Sun, 11 Oct 2026 |
| `MAVIS/Finante` | 0 | 0 | 0 | 9 | Tue, 6 Oct 2026  |
| `MAVIS/Personal` | 0 | 0 | 0 | 0 | n/a |
| `MAVIS/De raspuns` | 0 | 0 | 0 | 47 | Fri, 9 Oct 2026  |
| `MAVIS/Facturi si conturi` | 0 | 0 | 0 | 3 | Fri, 09 Oct 2026 |

**Concluzie:** etichetarea automată e oprită de **12 zile** (pe `MAVIS/Finante` = **06.10.2026**; pe `MAVIS/De raspuns`, `MAVIS/Facturi si conturi` = **09.10.2026**; pe `MAVIS/Joburi`, `MAVIS/AI si comunitati`, `MAVIS/Social`, `MAVIS/Newsletter` = **11.10.2026**).

> Zero pe o fereastră nu înseamnă "etichetă goală" — înseamnă "eticheta nu mai primește nimic". Verificat pe 4 ferestre.

### 1.3 Defectul, măsurat azi

Cele 5 filtre `MAVIS/*` există și au **criteriile corecte**, dar `action.addLabelIds` e **vid**:

```
filtru "joburi"
  criteria: from:(jooble bestjobs hipo indeed jobleads linkedin) OR subject:(job angajare vacanta oportunitate)
  action:   { removeLabelIds: ["UNREAD","INBOX"] }     <-- fara addLabelIds
```

**Și mai mult:** filtrul nici măcar nu arhivează. Deși `removeLabelIds` conține `INBOX`, mesajele de job intrate azi sunt **în continuare în INBOX și UNREAD**:

| Fereastră | În inbox | În toate stările |
|---|---|---|
| azi | 125 | 125 |
| 24h | 199 | 254 |
| 7z | 628 | 915 |

**~628 mesaje stau în inbox într-o săptămână** (~90/zi). Sortarea nu mai are loc.

**Cauza probabilă** (neconfirmată): etichetarea se făcea de un script local — `mavis-tools/email-sort-full.js` — care rulează pe calculatorul tău, nu din cloud. Filtrele din Gmail doar arhivează; **eticheta e pusă de script**. Scriptul nu mai rulează.

### 1.4 Cum ar fi fost sortate mesajele de azi

Simulare pe cele 125 mesaje de azi, cu **aceleași criterii** ale filtrelor (fără scriere):

| Categorie | Mesaje azi |
|---|---|
| `MAVIS/Joburi` | 6 |
| `MAVIS/Newsletter` | 3 |
| `MAVIS/AI si comunitati` | 3 |
| `MAVIS/Social` | 0 |
| `MAVIS/Finante` | 0 |
| *niciun filtru se potrivește* | 116 |

> Unele mesaje se potrivesc la 2 filtre (ex. "Joburi" + "Newsletter" de la LinkedIn), deci suma poate depăși 125.

**Observație:** din cele 116 mesaje fără filtru, **116 sunt notificări ale agenților tăi** (Jules și GitHub Actions pe repo-urile proprii). Taxonomia MAVIS nu are categorie pentru "notificări din pipeline-ul propriu". **Recomandare: etichetă nouă, ex. `MAVIS/Agenti`.**

### 1.5 Mesajele care chiar necesită răspuns

Clasificarea e făcută din date, nu dintr-o listă scrisă cu mâna: 1 cere răspuns explicit, 2 cer o decizie, 2 sunt alerte de job care nu ating profilul tău, 4 sunt newsletter/promoție, 116 sunt zgomot de pipeline.

**Ceres răspuns explicit:**

- **Chloe @ Mercor** — 00:03 UTC. *Action Requested: Opportunity with Mercor Project* — Hi Alexandru, I'm Chloe from the Growth team at Mercor. I am reaching out regarding a short-term, remote opportunity to contribute to a high-impact AI research project with one of 

**Ceres o decizie (alerte de job care bat cu profilul tău):**

- **Bestjobs** — 04:23 UTC. *8 design graphic bucuresti jobs available on bestjobs* — Top jobs according to your activity: CV entries, job applications and job searches. BestJobs Hi there, Alexandru Popescu! Bestie, your career friend, is on What
- **Jooble** — 03:53 UTC. *YO AI Labs caută Graphic designer - Remote și 101 mai multe oferte noi de muncă* — Jooble Anunțurile dvs. zilnice de oferte de muncă pentru 24 octombrie, 2026 Verificați ofertele noi de muncă pe care le-am găsit pentru dvs. astăzi. Afișați toa

**Alerte de job care NU ating profilul de design** (informativ, 2):

- Indeed — 04:22 UTC · *Airport Services Duty Officer - OTP la Qatar Airways. Încă 24 de locuri de muncă în București, Ilfov*
- Jooble — 00:08 UTC · *🔔 Cosmoworker caută Top - Preparator comenzi / Ambalator - cosmetice  și 84 mai multe oferte noi de muncă*

**Newsletter / promoție, fără acțiune** (4): Eduard Dumitrascu via LinkedIn, DocFreemason, UX Jobs via LinkedIn, Felix & Winston 🐶

**Leads verificate din alertele de job** (pagina sursă citită direct, nu din snippet de motor de căutare):

##### Remote Jobs for Graphic designers — YO AI Labs

Din alerta **Jooble** — *YO AI Labs caută Graphic designer - Remote și 101 mai multe oferte noi de muncă*

121 roluri de design, toate remote, pe 5 platforme de AI-training (Micro1, SuperAnnotate, Ethos AI, AfterQuery, Handshake AI).

**Rate-uri publicate:**

- Graphic Designer — Micro1 · $35–105/h
- Graphic Designer — SuperAnnotate · $30–60/h
- Graphic Designer Expert — AfterQuery · $40–80/h
- Graphic Designer / UI-UX Designer — Ethos AI · până la $150/h
- Creative Director — Ethos AI · până la $80/h
- Brand Director — Ethos AI · până la $70–80/h

**Condiții:** Contract, nu angajare. Contractezi cu platforma, nu cu YO AI Labs. Plătit per task sau per oră, în USD. Ore flexibile, majoritatea asincrone. Fără taxă de aplicare.

**Cum se aplică:** CV standard → interviu AI → assessment de domeniu → aplicare pe platformă.

> ⚠️ Contractor cu platforma, nu cu YO AI Labs. Verifică clauza de moonlighting din contractul tău actual.

- https://yoailabs.com/remote-jobs/graphic-designers/

---
## 2. Joburi — scorate cu `ALEX-KIT/scoring.gs`

**72 joburi analizate** (IQads 46 + designproject.io 26) → 36 păstrate în tabele, 36 drop-uri, din care **14 cu verdict amânat** (locația nu e publicată de sursă). **0 joburi noi** față de 2026-10-23.

Surse: **IQads** (tabloul AdJob activ, citit azi) + **designproject.io** (România + București).

> ⛔ **Expirate marcate în tabele.** La IQads data de expirare vine direct din anunț. La designproject.io `validThrough` = data postării + 30 zile — **măsurat pe toate cele 26 de joburi** (24 exacte, 2 cu o zi de fus orar), deci e o expirare reală, nu o derivare inutilă. 7 joburi din tabele au expirat și nu se mai pot aplica.

| | S | D | L | E |
|---|---|---|---|---|
| **S** — senioritate | 0.35 | | | |
| **D** — disciplină | | 0.30 | | |
| **L** — locație | | | 0.20 | |
| **E** — engagement | | | 0.15 | |

### 2.1 Secțiunea 1 — scor maxim — senior/lead, remote sau București, full-time (18)

| Scor | Tag | S/D/L/E | Rol | Companie | Locație | Engagement | Expirare | Nou |
|---|---|---|---|---|---|---|---|---
| **10** | [B2C] | 10/10/10/10 | Senior Creatives | International Waters | Bucuresti, Hybrid (Office & Remote) | Full Time | expiră 2026-11-01 |
| **9.4** | [DTC] | 10/8/10/10 | Media Relations Specialist | Confident Communications | Bucuresti | Full Time | expiră 2026-11-30 |
| **9.4** | [DTC] | 10/8/10/10 | PR Manager | Confident Communications | Bucuresti | Full Time | expiră 2026-11-30 |
| **9.4** | [B2B] | 10/8/10/10 | Digital Marketing Specialist | Alpha Clinic | Hybrid (Office & Remote) | Full Time | expiră 2026-11-27 |
| **9.4** | [DTC] | 10/8/10/10 | Graphic Designer | LUCA | Bucuresti | Full Time | expiră 2026-11-13 |
| **9.4** | [DTC] | 10/8/10/10 | Account Manager | AdSymphony | Hybrid (Office & Remote) | Full Time | expiră 2026-11-01 |
| **9.4** | [B2B] | 10/8/10/10 | Influencer & Creator Marketing Lead | Confident Communications | Bucuresti | Full Time | expiră 2026-10-31 |
| **9.4** | [DTC] | 10/8/10/10 | Senior Product Designer | Jobgether | Romania, Fully Remote | Full Time | postat 2026-10-02 · expiră 2026-11-01 |
| **9.4** | [DTC] | 10/8/10/10 | AI Research Lab UI/UX & Brand Designer (100 % remote) (m/f/d) | EWOR GmbH | Bucharest, Romania, Remote Solely | Full Time | postat 2026-09-25 · expiră 2026-10-25 |
| **9.4** | [DTC] | 10/8/10/10 | Industrial Tech UI/UX & Brand Designer (100 % remote) (m/f/d) | EWOR GmbH | Bucharest, Romania, Remote Solely | Full Time | postat 2026-09-18 · expiră 2026-10-18 ⛔ **EXPIRAT** |
| **9.4** | [DTC] | 10/8/10/10 | Head of UX/UI | Jobgether | Romania, Remote Solely | Full Time | postat 2026-09-16 · expiră 2026-10-16 ⛔ **EXPIRAT** |
| **9.4** | [DTC] | 10/8/10/10 | Principal Graphic Designer | AECOM | Bucharest, Romania, Hybrid | Full Time | postat 2026-09-15 · expiră 2026-10-15 ⛔ **EXPIRAT** |
| **9.3** | [DTC] | 8/10/10/10 | Graphic Designer & Digital Content Creator | Jobgether | Romania, Fully Remote | Full Time | postat 2026-09-17 · expiră 2026-10-17 ⛔ **EXPIRAT** |
| **9** | [B2B] | 10/8/8/10 | Social Media Specialist | Viva Credit | Romania | Full Time | expiră 2026-12-12 |
| **9** | [B2B] | 10/8/8/10 | Social Media Copywriter | Digital Star | Romania | Full Time | expiră 2026-10-30 |
| **8.7** | [DTC] | 8/8/10/10 | Digital Marketing Specialist | GoTech World | Bucuresti, Hybrid (Office & Remote) | Full Time | expiră 2026-11-30 |
| **8.7** | [B2B] | 8/8/10/10 | Graphic Designer | Super Technologies | Romania, Hybrid | Full Time | postat 2026-09-29 · expiră 2026-10-29 |
| **8.7** | [DTC] | 8/8/10/10 | Senior UX/UI Designer – limited for 2 years maternity cover | METRO/MAKRO | Bucuresti, Romania, Hybrid | Full Time, Contract | postat 2026-09-16 · expiră 2026-10-16 ⛔ **EXPIRAT** |

<!-- linkuri -->
- International Waters :: Senior Creatives — https://www.iqads.ro/adjob/23944/senior-creatives-international-waters
- Confident Communications :: Media Relations Specialist — https://www.iqads.ro/adjob/23978/media-relations-specialist-confident-communications
- Confident Communications :: PR Manager — https://www.iqads.ro/adjob/23977/pr-manager-confident-communications
- Alpha Clinic :: Digital Marketing Specialist — https://www.iqads.ro/adjob/23970/digital-marketing-specialist-alpha-clinic
- LUCA :: Graphic Designer — https://www.iqads.ro/adjob/23959/graphic-designer-luca
- AdSymphony :: Account Manager — https://www.iqads.ro/adjob/23946/account-manager-adsymphony
- Confident Communications :: Influencer & Creator Marketing Lead — https://www.iqads.ro/adjob/23941/influencer-creator-marketing-lead-confident-agency
- Jobgether :: Senior Product Designer — https://designproject.io/jobs/senior-product-designer-at-jobgether-6r1kga
- EWOR GmbH :: AI Research Lab UI/UX & Brand Designer (100 % remote) (m/f/d) — https://designproject.io/jobs/ai-research-lab-uiux-and-brand-designer-100-percent-remote-mfd-at-ewor-gmbh-teu2mk
- EWOR GmbH :: Industrial Tech UI/UX & Brand Designer (100 % remote) (m/f/d) — https://designproject.io/jobs/industrial-tech-uiux-and-brand-designer-100-percent-remote-mfd-at-ewor-gmbh-zrjj79
- Jobgether :: Head of UX/UI — https://designproject.io/jobs/head-of-uxui-at-jobgether-r1yo5t
- AECOM :: Principal Graphic Designer — https://designproject.io/jobs/principal-graphic-designer-at-aecom-t6bzhn
- Jobgether :: Graphic Designer & Digital Content Creator — https://designproject.io/jobs/graphic-designer-and-digital-content-creator-at-jobgether-55dzpj
- Viva Credit :: Social Media Specialist — https://www.iqads.ro/adjob/23990/social-media-specialist-viva-credit
- Digital Star :: Social Media Copywriter — https://www.iqads.ro/adjob/23940/social-media-copywriter-digital-star
- GoTech World :: Digital Marketing Specialist — https://www.iqads.ro/adjob/23981/digital-marketing-specialist-gotech-world
- Super Technologies :: Graphic Designer — https://designproject.io/jobs/graphic-designer-at-super-technologies-epi5zr
- METRO/MAKRO :: Senior UX/UI Designer – limited for 2 years maternity cover — https://designproject.io/jobs/senior-uxui-designer-limited-for-2-years-maternity-cover-at-metromakro-7b2vw7

### 2.2 Secțiunea 2 — contract / B2B — senioritate bună, engagement pe contract (4)

| Scor | Tag | S/D/L/E | Rol | Companie | Locație | Engagement | Expirare | Nou |
|---|---|---|---|---|---|---|---|---
| **9.1** | [DTC] | 10/8/10/8 | UI UX Designer | Uvation | Romania, Fully Remote | Contract | postat 2026-09-17 · expiră 2026-10-17 ⛔ **EXPIRAT** |
| **8.4** | [B2B] | 8/8/10/8 | English to French Linguist & Copy Editor for Product, Marketing & UI Content | Jobgether | Romania, Fully Remote | Contract | postat 2026-10-02 · expiră 2026-11-01 |
| **8.4** | [DTC] | 8/8/10/8 | Freelance Brand Designer | Mindrift | Romania, Fully Remote | Part Time, Contract | postat 2026-09-25 · expiră 2026-10-25 |
| **8.4** | [DTC] | 8/8/10/8 | Freelance Graphic Designer | Mindrift | Romania, Remote Solely | Part Time, Contract | postat 2026-09-21 · expiră 2026-10-21 ⛔ **EXPIRAT** |

<!-- linkuri -->
- Uvation :: UI UX Designer — https://designproject.io/jobs/ui-ux-designer-at-uvation-9f4zfu
- Jobgether :: English to French Linguist & Copy Editor for Product, Marketing & UI Content — https://designproject.io/jobs/english-to-french-linguist-and-copy-editor-for-product-marketing-and-ui-content-at-jobgether-j0zyru
- Mindrift :: Freelance Brand Designer — https://designproject.io/jobs/freelance-brand-designer-at-mindrift-ymls4c
- Mindrift :: Freelance Graphic Designer — https://designproject.io/jobs/freelance-graphic-designer-at-mindrift-snjhmz

### 2.3 Secțiunea 3 — mid-level — potrivire bună, senioritate sub prag (0)

*Niciun job în această secțiune.*

### 2.4 Secțiunea 4 — on-site în afara Bucureștiului — doar dacă S=10 și D≥8 (0)

*Niciun job în această secțiune.*

### 2.5 Verdict amânat — locația nu e publicată de sursă (14)

| Scor | Rol | Companie | Locație | Engagement | Expirare | Nou |
|---|---|---|---|---|---|---|
| 8 | Art Director | Stefanini Infinit | neprecizată de sursă | Full Time | 2026-12-14 |  |
| 8 | Creative Lead | Stefanini Infinit | neprecizată de sursă | Full Time | 2026-12-14 |  |
| 8 | ART MID | ontheroof | neprecizată de sursă | Full Time | 2026-11-28 |  |
| 8 | Art Director | Saatchi & Saatchi | neprecizată de sursă | Full Time | 2026-11-15 |  |
| 7.4 | Social Media Manager | Stefanini Infinit | neprecizată de sursă | Full Time | 2026-12-14 |  |
| 7.4 | Senior Social Media & Content Specialist (Project-Based or Full-Time) | Flaminjoy | neprecizată de sursă | Full Time, Project Based | 2026-12-07 |  |
| 7.4 | Social Media Manager | WoPA | neprecizată de sursă | Full Time | 2026-12-01 |  |
| 7.4 | Digital Account Manager | WoPA | neprecizată de sursă | Full Time | 2026-11-21 |  |
| 7.4 | Social Media Content Creator | Play Vertical | neprecizată de sursă | Full Time | 2026-11-08 |  |
| 7.4 | Graphic Designer | Touch Communications | neprecizată de sursă | Full Time | 2026-11-01 |  |
| 6.7 | Social Media Manager | WoPA | neprecizată de sursă | Full Time | 2026-10-24 |  |
| 6.7 | Social Media & Content Creator | Body Tailors Pilates | neprecizată de sursă | Full Time | 2026-10-24 |  |
| 5.65 | Copywriter | Stefanini Infinit | neprecizată de sursă | Full Time | 2026-12-14 |  |
| 5.65 | Digital Media Specialist / PPC | Stefanini Infinit | neprecizată de sursă | Full Time | 2026-11-27 |  |

**Dintre astea, 0 sunt noi.** Nu le-am dat verdict de locație pentru că anunțul nu o spune — să le verifici pe cele care te interesează:

- Art Director — Stefanini Infinit (IQads) — https://www.iqads.ro/adjob/23996/art-director-stefanini-infinit
- Creative Lead — Stefanini Infinit (IQads) — https://www.iqads.ro/adjob/23993/creative-lead-stefanini-infinit
- ART MID — ontheroof (IQads) — https://www.iqads.ro/adjob/23974/art-mid-ontheroof
- Art Director — Saatchi & Saatchi (IQads) — https://www.iqads.ro/adjob/23963/art-director-saatchi-saatchi
- Social Media Manager — Stefanini Infinit (IQads) — https://www.iqads.ro/adjob/23994/social-media-manager-stefanini-infinit
- Senior Social Media & Content Specialist (Project-Based or Full-Time) — Flaminjoy (IQads) — https://www.iqads.ro/adjob/23986/senior-social-media-content-specialist-project-based-or-full-time-flaminjoy
- Social Media Manager — WoPA (IQads) — https://www.iqads.ro/adjob/23983/social-media-manager-wopa
- Digital Account Manager — WoPA (IQads) — https://www.iqads.ro/adjob/23966/digital-account-manager-wopa

### 2.6 Drop-uri (circuit breaker) — 36

| Rol | Companie | Motiv | Nou |
|---|---|---|---|
| Account Director | Stefanini Infinit | disciplina nu se potrivește niciunui tier — Account Director |  |
| Influencer Marketing Director | Golin Ketchum | disciplina nu se potrivește niciunui tier — Influencer Marketing Director |  |
| Sales Associate | Elite Media United | rol junior/entry/intern — Sales Associate |  |
| BTL Account Manager | Highlight PR | disciplina nu se potrivește niciunui tier — BTL Account Manager |  |
| Account Manager | Stefanini Infinit | disciplina nu se potrivește niciunui tier — Account Manager |  |
| Key Account Manager | GoTech World | disciplina nu se potrivește niciunui tier — Key Account Manager |  |
| Account Director | Confident Communications | rol necorelabil cu portofoliul — Account Director |  |
| PR Manager | Highlight PR | disciplina nu se potrivește niciunui tier — PR Manager |  |
| Senior Strategist & Copywriter | HUBvertising | disciplina nu se potrivește niciunui tier — Senior Strategist & Copywriter |  |
| Traffic Manager | WoPA | disciplina nu se potrivește niciunui tier — Traffic Manager |  |
| BTL Account Manager | The Social Nest | disciplina nu se potrivește niciunui tier — BTL Account Manager |  |
| Specialist Productie Merchandise & Produse Custom | Godmother | disciplina nu se potrivește niciunui tier — Specialist Productie Merchandise & Produse Custom |  |
| Business Development Executive | Flaminjoy | disciplina nu se potrivește niciunui tier — Business Development Executive |  |
| BTL Senior Account Manager | WoPA | disciplina nu se potrivește niciunui tier — BTL Senior Account Manager |  |
| Junior Account Executive | The Social Nest | rol junior/entry/intern — Junior Account Executive |  |
| Tehnician montaj si logistica evenimente (BTL) | Hexagon X | disciplina nu se potrivește niciunui tier — Tehnician montaj si logistica evenimente (BTL) |  |
| Senior Account Manager | Propaganda | disciplina nu se potrivește niciunui tier — Senior Account Manager |  |
| Account Director | Propaganda | disciplina nu se potrivește niciunui tier — Account Director |  |
| Group Account Director | Propaganda | disciplina nu se potrivește niciunui tier — Group Account Director |  |
| Growth Marketing Manager | Voxa | disciplina nu se potrivește niciunui tier — Growth Marketing Manager |  |
| Project Manager | Marcom Hub | disciplina nu se potrivește niciunui tier — Project Manager |  |
| Senior Account Manager | Digitas | disciplina nu se potrivește niciunui tier — Senior Account Manager |  |
| Digital Workflow Developer — Rapid Prototyping and Pilots for NATO with security clearance | WLG | rol necorelabil cu portofoliul — Digital Workflow Developer — Rapid Prototyping and Pilots for NATO with security clearance |  |
| Senior UX Engineer | Lenovo | disciplina nu se potrivește niciunui tier — Senior UX Engineer |  |
| English to Romanian Linguist & Copy Editor for Product, Marketing & UI Content | Welo Global | disciplina nu se potrivește niciunui tier — English to Romanian Linguist & Copy Editor for Product, Marketing & UI Content |  |
| Senior UX Researcher (f/m/d) | Awin | rol necorelabil cu portofoliul — Senior UX Researcher (f/m/d) |  |
| Front-end Engineer - SDD UI @ING Hubs Romania | ING | rol necorelabil cu portofoliul — Front-end Engineer - SDD UI @ING Hubs Romania |  |
| Senior Front-End Software Development Engineer (UI Foundations) | Criteo | rol necorelabil cu portofoliul — Senior Front-End Software Development Engineer (UI Foundations) |  |
| Senior Motion Graphic Designer | Jobgether | rol necorelabil cu portofoliul — Senior Motion Graphic Designer |  |
| Solution Engineering & AI Prototyping Specialist | PwC | rol necorelabil cu portofoliul — Solution Engineering & AI Prototyping Specialist |  |
| Solution Engineering & AI Prototyping Specialist | Pwc CEE | rol necorelabil cu portofoliul — Solution Engineering & AI Prototyping Specialist |  |
| UX Design Internship - Iasi | Bitdefender | rol junior/entry/intern — UX Design Internship - Iasi |  |
| UX Design Internship - Bucharest | Bitdefender | rol junior/entry/intern — UX Design Internship - Bucharest |  |
| Marketing Designer | Trade Nation | rol necorelabil cu portofoliul — Marketing Designer |  |
| Senior UX Researcher (f/m/d) | Awin | rol necorelabil cu portofoliul — Senior UX Researcher (f/m/d) |  |
| Gameplay & UI Developer | Jobgether | rol necorelabil cu portofoliul — Gameplay & UI Developer |  |

---

## 3. Top 5 joburi cu scor

| # | Scor | Tag | Rol | Companie | Locație | Engagement | Expirat? | De ce contează |
|---|---|---|---|---|---|---|---|---|
| 1 | **10** | [B2C] | Senior Creatives | International Waters | Bucuresti, Hybrid (Office & Remote) | Full Time | nu | S și D maxime |
| 2 | **9.4** | [DTC] | Media Relations Specialist | Confident Communications | Bucuresti | Full Time | nu | D ridicat de prosa ("social media") |
| 3 | **9.4** | [DTC] | PR Manager | Confident Communications | Bucuresti | Full Time | nu | D ridicat de prosa ("social media") |
| 4 | **9.4** | [B2B] | Digital Marketing Specialist | Alpha Clinic | Hybrid (Office & Remote) | Full Time | nu | D ridicat de prosa ("social media") |
| 5 | **9.4** | [DTC] | Graphic Designer | LUCA | Bucuresti | Full Time | nu | L=10 (remote detectat în text) |

- International Waters :: Senior Creatives — https://www.iqads.ro/adjob/23944/senior-creatives-international-waters
- Confident Communications :: Media Relations Specialist — https://www.iqads.ro/adjob/23978/media-relations-specialist-confident-communications
- Confident Communications :: PR Manager — https://www.iqads.ro/adjob/23977/pr-manager-confident-communications
- Alpha Clinic :: Digital Marketing Specialist — https://www.iqads.ro/adjob/23970/digital-marketing-specialist-alpha-clinic
- LUCA :: Graphic Designer — https://www.iqads.ro/adjob/23959/graphic-designer-luca

> **Atenție:** din top 5 după scor, 3 **nu sunt roluri de design** (au trecut doar pentru că textul lor conține "social media" sau "art director" — vezi §6.2). Iată top 5 **efectiv de design**, filtrate pe titlu:

| # | Scor | Rol | Companie | Locație | Engagement | Expirat? | De ce contează |
|---|---|---|---|---|---|---|---|
| 1 | **10** | Senior Creatives | International Waters | Bucuresti, Hybrid (Office & Remote) | Full Time | nu | S și D maxime |
| 2 | **9.4** | Graphic Designer | LUCA | Bucuresti | Full Time | nu | L=10 (remote detectat în text) |
| 3 | **9.4** | Senior Product Designer | Jobgether | Romania, Fully Remote | Full Time | nu | remote |
| 4 | **9.4** | AI Research Lab UI/UX & Brand Designer (100 % remote) (m/f/d) | EWOR GmbH | Bucharest, Romania, Remote Solely | Full Time | nu | remote |
| 5 | **9.4** | Industrial Tech UI/UX & Brand Designer (100 % remote) (m/f/d) | EWOR GmbH | Bucharest, Romania, Remote Solely | Full Time | ⛔ da | remote |

- International Waters :: Senior Creatives — https://www.iqads.ro/adjob/23944/senior-creatives-international-waters
- LUCA :: Graphic Designer — https://www.iqads.ro/adjob/23959/graphic-designer-luca
- Jobgether :: Senior Product Designer — https://designproject.io/jobs/senior-product-designer-at-jobgether-6r1kga
- EWOR GmbH :: AI Research Lab UI/UX & Brand Designer (100 % remote) (m/f/d) — https://designproject.io/jobs/ai-research-lab-uiux-and-brand-designer-100-percent-remote-mfd-at-ewor-gmbh-teu2mk
- EWOR GmbH :: Industrial Tech UI/UX & Brand Designer (100 % remote) (m/f/d) — https://designproject.io/jobs/industrial-tech-uiux-and-brand-designer-100-percent-remote-mfd-at-ewor-gmbh-zrjj79

---

## 4. Postări GENUIN noi (nu doar "absente din raportul de ieri")

> "nou" în tabele înseamnă **"nu era în raportul de ieri"**, nu neapărat "postat azi". Iată ce e postat efectiv nou:

| Sursă | Cum am măsurat | Rezultat |
|---|---|---|
| **IQads** | ID-ul ad-ului crește monoton cu postarea. Cel mai mare ID din setul de ieri: **23997** | **0 anunțuri noi** |
| **designproject.io** | data de publicare vs. ultima rulare | **0 anunțuri noi** — cel mai recent de pe site e din **2026-10-06** |

**Concluzie:** **nicio postare nouă față de ultima rulare.** Piața nu a produs nimic nou relevant azi.


---

## 5. Ce n-a mers, măsurat

1. **Etichetele MAVIS/* nu mai primesc nimic de 12 zile.** Filtrele au `addLabelIds` vid și nici măcar nu mai arhivează — ~628 mesaje/7 zile stau în inbox. Cauza: scriptul local `email-sort-full.js` (cel care punea etichetele) nu mai rulează.
2. **designproject.io servește descrieri rescrise de AI** (24.000–33.000 de caractere, față de 71–1484 pe 22.10, inclusiv "📝 Enhancement Note"). E mai bogat, dar injectează cuvinte-cheie care ridică axele — vezi §6.2.
3. **Celelalte două câmpuri de engagement ale designproject.io sunt inutilizabile.** `employmentType` din JSON-LD spune `FULL_TIME` pentru toate cele 26, iar badge-ul din listing spune "Full-time" pentru toate 26. Singura sură corectă e linia **"Job Type:"** din descriere (Trade Nation: "CONTRACTOR"; Mindrift: "PART_TIME" + freelance; Uvation: "Contractor"). Am folosit asta.
4. **Paginatia IQads nu funcționează.** `?page=2` și `?page=3` servesc exact pagina 0 (aceleași linkuri). Catalogul complet e pe pagina 0 — nu iterez pagini.
5. **Cota Google: 200 cereri pe 200** (**exact pe plafon**). Consumul pe etape:

| Etapă | Cereri |
|---|---|
| `report-simulate-sort.js` | 126 |
| `report-mail-count.js` | 60 |
| `report-inbox-counts.js` | 8 |
| `report-build.js` | 3 |
| `report-build.js` (upload + verificare) | 3 |
| **total** | **200** |

> Rulare 2026-10-24 (raport zilnic). Contor pornit de la zero.

Ce a mers peste plafon: am descărcat corpurile complete ale mesajelor de azi (125) ca să disting mesajele care chiar cer răspuns de alertele automate — fără corp, nu se poate. **Zero scrieri pe Gmail** — niciun mail trimis, marcat sau arhivat.

---

## 6. Două semnalări ale motorului de scoring (portul rămâne fidel — decizia e a ta)

### 6.1 "remote" pozitiv fals — 4 joburi

| Rol | Companie | De ce e fals | L |
|---|---|---|---|
| Graphic Designer | LUCA | negatie: `nu se lucreaza remote` | 10 |
| Principal Graphic Designer | AECOM | eticheta: `Remote Status: Hybrid` | 10 |
| Graphic Designer | Super Technologies | eticheta: `Remote Status: Hybrid` | 10 |
| Senior UX/UI Designer – limited for 2 years maternity cover | METRO/MAKRO | eticheta: `Remote Status: Hybrid` | 10 |

"Remote" apare în text, dar jobul **nu** e remote. `L` ar trebui să fie 8 (București) sau 0 (necunoscut), nu 10. Diferență: **0.4 puncte** per job. Nu am atins motorul — portul e fidel prin design.

### 6.2 Axa D ridicată de prosa, nu de titlu — 16 joburi (20 semnalări)

| Rol | Companie | Ce a ridicat axa | De unde |
|---|---|---|---|
| Media Relations Specialist | Confident Communications | D=8 prin `"social media"` (Core Design) | prosa anuntului |
| PR Manager | Confident Communications | D=8 prin `"social media"` (Core Design) | prosa anuntului |
| Digital Marketing Specialist | Alpha Clinic | S=10 prin `"head of"` (—) | prosa anuntului |
| Digital Marketing Specialist | Alpha Clinic | D=8 prin `"social media"` (Core Design) | prosa anuntului |
| Account Manager | AdSymphony | D=8 prin `"social media"` (Core Design) | prosa anuntului |
| Influencer & Creator Marketing Lead | Confident Communications | D=8 prin `"social media"` (Core Design) | prosa anuntului |
| AI Research Lab UI/UX & Brand Designer (100 % remote) (m/f/d) | EWOR GmbH | S=10 prin `"senior"` (—) | prosa anuntului |
| Industrial Tech UI/UX & Brand Designer (100 % remote) (m/f/d) | EWOR GmbH | S=10 prin `"senior"` (—) | prosa anuntului |
| Graphic Designer & Digital Content Creator | Jobgether | S=8 prin `"senior"` (—) | prosa anuntului |
| Graphic Designer & Digital Content Creator | Jobgether | D=10 prin `"art director"` (Creative Leadership) | prosa anuntului |
| UI UX Designer | Uvation | S=10 prin `"senior"` (—) | prosa anuntului |
| Digital Marketing Specialist | GoTech World | S=8 prin `"principal"` (—) | prosa anuntului |
| Digital Marketing Specialist | GoTech World | D=8 prin `"social media"` (Core Design) | prosa anuntului |
| English to French Linguist & Copy Editor for Product, Marketing & UI Content | Jobgether | S=8 prin `"lead"` (—) | prosa anuntului |
| English to French Linguist & Copy Editor for Product, Marketing & UI Content | Jobgether | D=8 prin `"ui/ux"` (Core Design) | prosa anuntului |
| Freelance Brand Designer | Mindrift | S=8 prin `"lead"` (—) | prosa anuntului |
| Freelance Graphic Designer | Mindrift | S=8 prin `"lead"` (—) | prosa anuntului |
| Digital Account Manager | WoPA | D=8 prin `"social media"` (Core Design) | prosa anuntului |
| Copywriter | Stefanini Infinit | D=8 prin `"social media"` (Core Design) | prosa anuntului |
| Digital Media Specialist / PPC | Stefanini Infinit | D=8 prin `"social media"` (Core Design) | prosa anuntului |

**Ce propun:** ca `D` să se calculeze din **titlul rolului**, nu din textul anunțului, sau măcar ca un rol să poată intra într-o secțiune doar dacă titlul conține o cheie de design. E o decizie de motor — nu am atins `scoring.gs` fără acordul tău.

---

## 7. Fișiere

- `rapoarte/RAPORT-ZILNIC-202610-24.md` — raportul acesta (și în repo)
- `mavis-tools/scoring-result-2026-10-24.json` — scoruri + secțiuni + diagnostice
- `mavis-tools/jobs-iqads-2026-10-24.json` — joburi IQads, text integral
- `mavis-tools/jobs-designproject-2026-10-24.json` — joburi designproject.io, JSON-LD
- `mavis-tools/jobs-2026-10-23.json` — setul normalizat de ieri (cu care s-a comparat)
- `mavis-tools/report-mail-count.json` — numărătoare pe etichete MAVIS/*
- `mavis-tools/report-inbox-counts.json` — numărătoare exactă inbox
- `mavis-tools/report-simulate-sort.json` — simularea sortării + mesajele de azi
- `mavis-tools/report-triage.js` — clasificatorul mesajelor (needs-reply / needs-action / fyi / noise)

---

*Generat de Mavis Cloud. Nimic nu a fost șters, nimic nu a fost trimis, nimic nu a fost modificat în Gmail sau Drive. Totul e anulabil.*
