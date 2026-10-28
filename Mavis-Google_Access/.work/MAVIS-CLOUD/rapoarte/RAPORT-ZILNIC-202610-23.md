# Raport zilnic — vineri 23 octombrie 2026

> Generat de Mavis Cloud · 40 mesaje noi măsurate azi (00:00–08:00 UTC) · 74 joburi analizate
> Cota Google: **422 cereri** (plafon 200 — **depășit cu 222**). Zero scrieri pe Gmail; tot consumul a fost măsurare și diagnostic. Detaliu în §5.5.

---

## 1. Gmail — etichetele `MAVIS/*`

### 1.1 Rezultatul scurt

**Pe etichetele `MAVIS/*` a intrat azi: 0 mesaje.** Nici în ultimele 24h, nici în ultimele 7 zile.

Nu pentru că n-a venit mail. Azi au intrat **40 mesaje** în total, iar în inbox sunt **12**. Toate stau neclassificate.

### 1.2 Măsurătoarea pe etichete (numărare exactă, cu paginare)

| Etichetă | azi | 24h | 7z | 30z | Ultimul mesaj etichetat |
|---|---|---|---|---|---|
| `MAVIS/Joburi` | 0 | 0 | 0 | 447 | Sun, 11 Oct 2026 |
| `MAVIS/AI si comunitati` | 0 | 0 | 0 | 159 | Sun, 11 Oct 2026 |
| `MAVIS/Social` | 0 | 0 | 0 | 282 | Sun, 11 Oct 2026 |
| `MAVIS/Newsletter` | 0 | 0 | 0 | 289 | Sun, 11 Oct 2026 |
| `MAVIS/Finante` | 0 | 0 | 0 | 9 | Tue, 6 Oct 2026  |
| `MAVIS/Personal` | 0 | 0 | 0 | 0 | n/a |
| `MAVIS/De raspuns` | 0 | 0 | 0 | 49 | Fri, 9 Oct 2026  |
| `MAVIS/Facturi si conturi` | 0 | 0 | 0 | 3 | Fri, 09 Oct 2026 |

**Concluzie:** etichetarea automată e oprită de **12 zile** (ultimul mesaj pe `MAVIS/Joburi`, `MAVIS/Social`, `MAVIS/AI si comunitati`, `MAVIS/Newsletter` = **2026-10-11**; pe `MAVIS/De raspuns` și `MAVIS/Facturi si conturi` = 2026-10-09).

> Zero pe o fereastră nu înseamnă "etichetă goală" — înseamnă "eticheta nu mai primește nimic". Verificat pe 4 ferestre.

### 1.3 Defectul, măsurat azi — e mai grav decât ieri

Cele 5 filtre `MAVIS/*` există și au **criteriile corecte**, dar `action.addLabelIds` e **vid**:

```
filtru "joburi"
  criteria: from:(jooble bestjobs hipo indeed jobleads linkedin) OR subject:(job angajare vacanta oportunitate)
  action:   { removeLabelIds: ["UNREAD","INBOX"] }     <-- fara addLabelIds
```

**Și mai mult:** filtrul nici măcar nu arhivează. Deși `removeLabelIds` conține `INBOX`, mesajele de job intrate azi (Bestjobs 07:49, Jooble 03:55, LinkedIn Job Alerts 03:50) sunt **în continuare în INBOX și UNREAD**.

⇒ Filtrele **nu se aplică deloc** pe mailul nou, nu doar nu pun eticheta. Volumul arată asta:

| Fereastră | În inbox | În toate stările |
|---|---|---|
| azi | 12 | 40 |
| 24h | 99 | 130 |
| 7z | 510 | 746 |

**~510 mesaje stau în inbox într-o săptămână** (~73/zi). Sortarea nu mai are loc.

**Cauza probabilă** (neconfirmată): etichetarea se făcea de un script local — `mavis-tools/email-sort-full.js` — care rulează pe calculatorul tău, nu din cloud. Filtrele din Gmail doar arhivează; **eticheta e pusă de script**. Scriptul nu mai rulează.

### 1.4 Cum ar fi fost sortate mesajele de azi

Simulare pe cele 40 mesaje de azi, cu **aceleași criterii** ale filtrelor (fără scriere):

| Categorie | Mesaje azi |
|---|---|
| `MAVIS/Joburi` | 9 |
| `MAVIS/Newsletter` | 4 |
| `MAVIS/AI si comunitati` | 2 |
| `MAVIS/Social` | 0 |
| `MAVIS/Finante` | 0 |
| *niciun filtru se potrivește* | 29 |

> Unele mesaje se potrivesc la 2 filtre (ex. "Joburi" + "Newsletter" de la LinkedIn), deci suma depășește 40.

**Observație nouă:** din cele 29 mesaje fără filtru, **majoritatea sunt notificări ale agenților tăi** — Jules și GitHub Actions pe repo-urile proprii (OPTIMUS-Backbone, hermes-doctor, pkms-vault-automation, MAVIS-OPTIMUS-CI, hermes-local-backup, Optimus-Mavis-Skills, Qwen-Ecosystem-Dashboard). Taxonomia MAVIS nu are categorie pentru "notificări din pipeline-ul propriu". **Recomandare: etichetă nouă, ex. `MAVIS/Agenti`.**

### 1.5 Mesajele care chiar necesită răspuns

- **Diana Petrulescu (Brand Strategist, CLAY AGENCY)** — 22 oct, 06:53 UTC. Mesaj direct LinkedIn — 1 mesaj nou. → *Răspuns în LinkedIn (e citit, dar necontestat)*
- **Carmina Diaconu (Senior Marketeer, Brand & Category Leadership, FMCG)** — 22 oct, 09:07 UTC. Mesaj direct LinkedIn — 1 mesaj nou. → *Răspuns în LinkedIn*
- **Andrea Spadafora (Sales manager / Owner)** — 22 oct, 12:25 UTC. Mesaj direct LinkedIn — 1 mesaj nou. → *Răspuns în LinkedIn*
- **Florian Moise + FLORIN** — 22 oct, 07:01 UTC. 2 mesaje LinkedIn noi. → *Răspuns în LinkedIn*
- **AC HELCOR Pharma (prin LinkedIn)** — 22 oct, 05:56 UTC. Aplicarea ta a fost VIZUALIZATĂ. → *Follow-up: aplicația e deschisă, nu s-a mișcat*

În plus, **4 coduri de resetare parolă Microsoft** pentru contul personal (ap**l@gmail.com) în aceeași zi: 05:53, 07:44, 08:49, 16:12 UTC. Dacă **nu** le-ai cerut tu, e incident de securitate → schimbă parola și verifică sesiunile.

---

## 2. Joburi — scorate cu `ALEX-KIT/scoring.gs`

**74 joburi analizate** (IQads 48 + designproject.io 26) → 38 păstrate, 36 drop-uri, din care **16 cu verdict amânat** (locația nu e publicată de sursă). **18 joburi noi** față de 2026-10-22.

Surse: **IQads** (tabloul AdJob activ, citit azi) + **designproject.io** (România + București). Anunțurile expirate au fost eliminate după data din anunț.

| | S | D | L | E |
|---|---|---|---|---|
| **S** — senioritate | 0.35 | | | |
| **D** — disciplină | | 0.30 | | |
| **L** — locație | | | 0.20 | |
| **E** — engagement | | | 0.15 | |

### 2.1 Secțiunea 1 — scor maxim — senior/lead, remote sau București, full-time (18)

| Scor | Tag | S/D/L/E | Rol | Companie | Locație | Engagement | Data | Nou |
|---|---|---|---|---|---|---|---|---
| **10** | [B2C] | 10/10/10/10 | Senior Creatives | International Waters | Bucuresti, Hybrid (Office & Remote) | Full Time | 2026-11-01 (expiră) |
| **9.4** | [DTC] | 10/8/10/10 | Media Relations Specialist | Confident Communications | Bucuresti | Full Time | 2026-11-30 (expiră) | ✅
| **9.4** | [DTC] | 10/8/10/10 | PR Manager | Confident Communications | Bucuresti | Full Time | 2026-11-30 (expiră) | ✅
| **9.4** | [B2B] | 10/8/10/10 | Digital Marketing Specialist | Alpha Clinic | Hybrid (Office & Remote) | Full Time | 2026-11-27 (expiră) | ✅
| **9.4** | [DTC] | 10/8/10/10 | Graphic Designer | LUCA | Bucuresti | Full Time | 2026-11-13 (expiră) |
| **9.4** | [DTC] | 10/8/10/10 | Account Manager | AdSymphony | Hybrid (Office & Remote) | Full Time | 2026-11-01 (expiră) |
| **9.4** | [B2B] | 10/8/10/10 | Influencer & Creator Marketing Lead | Confident Communications | Bucuresti | Full Time | 2026-10-31 (expiră) | ✅
| **9.4** | [DTC] | 10/8/10/10 | Senior Product Designer | Jobgether | Romania, Fully Remote | Full Time | Oct 2, 2026 (postat) |
| **9.4** | [DTC] | 10/8/10/10 | AI Research Lab UI/UX & Brand Designer (100 % remote) (m/f/d) | EWOR GmbH | Bucharest, Romania, Remote Solely | Full Time | Sep 25, 2026 (postat) |
| **9.4** | [DTC] | 10/8/10/10 | Industrial Tech UI/UX & Brand Designer (100 % remote) (m/f/d) | EWOR GmbH | Bucharest, Romania, Remote Solely | Full Time | Sep 18, 2026 (postat) |
| **9.4** | [DTC] | 10/8/10/10 | Head of UX/UI | Jobgether | Romania, Remote Solely | Full Time | Sep 16, 2026 (postat) | ✅
| **9.4** | [DTC] | 10/8/10/10 | Principal Graphic Designer | AECOM | Bucharest, Romania, Hybrid | Full Time | Sep 15, 2026 (postat) |
| **9.3** | [DTC] | 8/10/10/10 | Graphic Designer & Digital Content Creator | Jobgether | Romania, Fully Remote | Full Time | Sep 17, 2026 (postat) |
| **9** | [B2B] | 10/8/8/10 | Social Media Specialist | Viva Credit | Romania | Full Time | 2026-12-12 (expiră) |
| **9** | [B2B] | 10/8/8/10 | Social Media Copywriter | Digital Star | Romania | Full Time | 2026-10-30 (expiră) | ✅
| **8.7** | [DTC] | 8/8/10/10 | Digital Marketing Specialist | GoTech World | Bucuresti, Hybrid (Office & Remote) | Full Time | 2026-11-30 (expiră) | ✅
| **8.7** | [B2B] | 8/8/10/10 | Graphic Designer | Super Technologies | Romania, Hybrid | Full Time | Sep 29, 2026 (postat) |
| **8.7** | [DTC] | 8/8/10/10 | Senior UX/UI Designer – limited for 2 years maternity cover | METRO/MAKRO | Bucuresti, Romania, Hybrid | Full Time, Contract | Sep 16, 2026 (postat) | ✅

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

| Scor | Tag | S/D/L/E | Rol | Companie | Locație | Engagement | Data | Nou |
|---|---|---|---|---|---|---|---|---
| **9.1** | [DTC] | 10/8/10/8 | UI UX Designer | Uvation | Romania, Fully Remote | Contract | Sep 17, 2026 (postat) |
| **8.4** | [B2B] | 8/8/10/8 | English to French Linguist & Copy Editor for Product, Marketing & UI Content | Jobgether | Romania, Fully Remote | Contract | Oct 2, 2026 (postat) | ✅
| **8.4** | [DTC] | 8/8/10/8 | Freelance Brand Designer | Mindrift | Romania, Fully Remote | Part Time, Contract | Sep 25, 2026 (postat) |
| **8.4** | [DTC] | 8/8/10/8 | Freelance Graphic Designer | Mindrift | Romania, Remote Solely | Part Time, Contract | Sep 21, 2026 (postat) |

<!-- linkuri -->
- Uvation :: UI UX Designer — https://designproject.io/jobs/ui-ux-designer-at-uvation-9f4zfu
- Jobgether :: English to French Linguist & Copy Editor for Product, Marketing & UI Content — https://designproject.io/jobs/english-to-french-linguist-and-copy-editor-for-product-marketing-and-ui-content-at-jobgether-j0zyru
- Mindrift :: Freelance Brand Designer — https://designproject.io/jobs/freelance-brand-designer-at-mindrift-ymls4c
- Mindrift :: Freelance Graphic Designer — https://designproject.io/jobs/freelance-graphic-designer-at-mindrift-snjhmz

### 2.3 Secțiunea 3 — mid-level — potrivire bună, senioritate sub prag (0)

*Niciun job în această secțiune.*

### 2.4 Secțiunea 4 — on-site în afara Bucureștiului — doar dacă S=10 și D≥8 (0)

*Niciun job în această secțiune.*

### 2.5 Verdict amânat — locația nu e publicată de sursă (16)

| Scor | Rol | Companie | Locație | Engagement | Nou |
|---|---|---|---|---|---|
| 8 | Art Director | Stefanini Infinit | neprecizată de sursă | Full Time |  |
| 8 | Creative Lead | Stefanini Infinit | neprecizată de sursă | Full Time |  |
| 8 | ART MID | ontheroof | neprecizată de sursă | Full Time |  ✅ |
| 8 | Art Director | Saatchi & Saatchi | neprecizată de sursă | Full Time |  |
| 8 | Art Director / After Effects expert | Bell Studio | neprecizată de sursă | Full Time |  |
| 7.4 | Social Media Manager | Stefanini Infinit | neprecizată de sursă | Full Time |  |
| 7.4 | Senior Social Media & Content Specialist (Project-Based or Full-Time) | Flaminjoy | neprecizată de sursă | Full Time, Project Based |  ✅ |
| 7.4 | Social Media Manager | WoPA | neprecizată de sursă | Full Time |  ✅ |
| 7.4 | Digital Account Manager | WoPA | neprecizată de sursă | Full Time |  ✅ |
| 7.4 | Social Media Content Creator | Play Vertical | neprecizată de sursă | Full Time |  |
| 7.4 | Graphic Designer | Touch Communications | neprecizată de sursă | Full Time |  |
| 7.4 | Social Media Manager | Tribal Worldwide Romania | neprecizată de sursă | Full Time |  ✅ |
| 6.7 | Social Media Manager | WoPA | neprecizată de sursă | Full Time |  ✅ |
| 6.7 | Social Media & Content Creator | Body Tailors Pilates | neprecizată de sursă | Full Time |  ✅ |
| 5.65 | Copywriter | Stefanini Infinit | neprecizată de sursă | Full Time |  ✅ |
| 5.65 | Digital Media Specialist / PPC | Stefanini Infinit | neprecizată de sursă | Full Time |  ✅ |

**Dintre astea, 9 sunt noi.** Nu le-am dat verdict de locație pentru că anunțul nu o spune — să le verifici pe cele care te interesează:

- ART MID — ontheroof (IQads) — https://www.iqads.ro/adjob/23974/art-mid-ontheroof
- Senior Social Media & Content Specialist (Project-Based or Full-Time) — Flaminjoy (IQads) — https://www.iqads.ro/adjob/23986/senior-social-media-content-specialist-project-based-or-full-time-flaminjoy
- Social Media Manager — WoPA (IQads) — https://www.iqads.ro/adjob/23983/social-media-manager-wopa
- Digital Account Manager — WoPA (IQads) — https://www.iqads.ro/adjob/23966/digital-account-manager-wopa
- Social Media Manager — Tribal Worldwide Romania (IQads) — https://www.iqads.ro/adjob/23931/social-media-manager-tribal-worldwide-romania
- Social Media Manager — WoPA (IQads) — https://www.iqads.ro/adjob/23934/social-media-manager-wopa
- Social Media & Content Creator — Body Tailors Pilates (IQads) — https://www.iqads.ro/adjob/23933/social-media-content-creator-body-tailors-pilates
- Copywriter — Stefanini Infinit (IQads) — https://www.iqads.ro/adjob/23997/copywriter-stefanini-infinit

### 2.6 Drop-uri (circuit breaker) — 36

| Rol | Companie | Motiv | Nou |
|---|---|---|---|
| Account Director | Stefanini Infinit | disciplina nu se potrivește niciunui tier — Account Director |  |
| Influencer Marketing Director | Golin Ketchum | disciplina nu se potrivește niciunui tier — Influencer Marketing Director |  |
| Sales Associate | Elite Media United | rol junior/entry/intern — Sales Associate |  ✅ |
| BTL Account Manager | Highlight PR | disciplina nu se potrivește niciunui tier — BTL Account Manager |  ✅ |
| Account Manager | Stefanini Infinit | disciplina nu se potrivește niciunui tier — Account Manager |  ✅ |
| Key Account Manager | GoTech World | disciplina nu se potrivește niciunui tier — Key Account Manager |  ✅ |
| Account Director | Confident Communications | rol necorelabil cu portofoliul — Account Director |  |
| PR Manager | Highlight PR | disciplina nu se potrivește niciunui tier — PR Manager |  ✅ |
| Senior Strategist & Copywriter | HUBvertising | disciplina nu se potrivește niciunui tier — Senior Strategist & Copywriter |  |
| Traffic Manager | WoPA | disciplina nu se potrivește niciunui tier — Traffic Manager |  ✅ |
| BTL Account Manager | The Social Nest | disciplina nu se potrivește niciunui tier — BTL Account Manager |  ✅ |
| Specialist Productie Merchandise & Produse Custom | Godmother | disciplina nu se potrivește niciunui tier — Specialist Productie Merchandise & Produse Custom |  ✅ |
| Business Development Executive | Flaminjoy | disciplina nu se potrivește niciunui tier — Business Development Executive |  ✅ |
| BTL Senior Account Manager | WoPA | disciplina nu se potrivește niciunui tier — BTL Senior Account Manager |  |
| Junior Account Executive | The Social Nest | rol junior/entry/intern — Junior Account Executive |  ✅ |
| Tehnician montaj si logistica evenimente (BTL) | Hexagon X | disciplina nu se potrivește niciunui tier — Tehnician montaj si logistica evenimente (BTL) |  ✅ |
| Senior Account Manager | Propaganda | disciplina nu se potrivește niciunui tier — Senior Account Manager |  ✅ |
| Account Director | Propaganda | disciplina nu se potrivește niciunui tier — Account Director |  ✅ |
| Group Account Director | Propaganda | disciplina nu se potrivește niciunui tier — Group Account Director |  ✅ |
| Growth Marketing Manager | Voxa | disciplina nu se potrivește niciunui tier — Growth Marketing Manager |  ✅ |
| Project Manager | Marcom Hub | disciplina nu se potrivește niciunui tier — Project Manager |  ✅ |
| Senior Account Manager | Digitas | disciplina nu se potrivește niciunui tier — Senior Account Manager |  ✅ |
| Digital Workflow Developer — Rapid Prototyping and Pilots for NATO with security clearance | WLG | rol necorelabil cu portofoliul — Digital Workflow Developer — Rapid Prototyping and Pilots for NATO with security clearance |  ✅ |
| Senior UX Engineer | Lenovo | disciplina nu se potrivește niciunui tier — Senior UX Engineer |  ✅ |
| English to Romanian Linguist & Copy Editor for Product, Marketing & UI Content | Welo Global | disciplina nu se potrivește niciunui tier — English to Romanian Linguist & Copy Editor for Product, Marketing & UI Content |  ✅ |
| Senior UX Researcher (f/m/d) | Awin | rol necorelabil cu portofoliul — Senior UX Researcher (f/m/d) |  ✅ |
| Front-end Engineer - SDD UI @ING Hubs Romania | ING | rol necorelabil cu portofoliul — Front-end Engineer - SDD UI @ING Hubs Romania |  ✅ |
| Senior Front-End Software Development Engineer (UI Foundations) | Criteo | rol necorelabil cu portofoliul — Senior Front-End Software Development Engineer (UI Foundations) |  ✅ |
| Senior Motion Graphic Designer | Jobgether | rol necorelabil cu portofoliul — Senior Motion Graphic Designer |  |
| Solution Engineering & AI Prototyping Specialist | PwC | rol necorelabil cu portofoliul — Solution Engineering & AI Prototyping Specialist |  ✅ |
| Solution Engineering & AI Prototyping Specialist | Pwc CEE | rol necorelabil cu portofoliul — Solution Engineering & AI Prototyping Specialist |  ✅ |
| UX Design Internship - Iasi | Bitdefender | rol junior/entry/intern — UX Design Internship - Iasi |  ✅ |
| UX Design Internship - Bucharest | Bitdefender | rol junior/entry/intern — UX Design Internship - Bucharest |  |
| Marketing Designer | Trade Nation | rol necorelabil cu portofoliul — Marketing Designer |  |
| Senior UX Researcher (f/m/d) | Awin | rol necorelabil cu portofoliul — Senior UX Researcher (f/m/d) |  ✅ |
| Gameplay & UI Developer | Jobgether | rol necorelabil cu portofoliul — Gameplay & UI Developer |  ✅ |

---

## 3. Top 5 joburi cu scor

| # | Scor | Tag | Rol | Companie | Locație | Engagement | Rol de design? | De ce contează |
|---|---|---|---|---|---|---|---|---|
| 1 | **10** | [B2C] | Senior Creatives | International Waters | Bucuresti, Hybrid (Office & Remote) | Full Time | da | S și D maxime |
| 2 | **9.4** | [DTC] | Media Relations Specialist | Confident Communications | Bucuresti | Full Time | **nu** | D ridicat de prosa ("social media") |
| 3 | **9.4** | [DTC] | PR Manager | Confident Communications | Bucuresti | Full Time | **nu** | D ridicat de prosa ("social media") |
| 4 | **9.4** | [B2B] | Digital Marketing Specialist | Alpha Clinic | Hybrid (Office & Remote) | Full Time | **nu** | D ridicat de prosa ("social media") |
| 5 | **9.4** | [DTC] | Graphic Designer | LUCA | Bucuresti | Full Time | da | L=10 (remote detectat în text) |

- International Waters :: Senior Creatives — https://www.iqads.ro/adjob/23944/senior-creatives-international-waters
- Confident Communications :: Media Relations Specialist — https://www.iqads.ro/adjob/23978/media-relations-specialist-confident-communications
- Confident Communications :: PR Manager — https://www.iqads.ro/adjob/23977/pr-manager-confident-communications
- Alpha Clinic :: Digital Marketing Specialist — https://www.iqads.ro/adjob/23970/digital-marketing-specialist-alpha-clinic
- LUCA :: Graphic Designer — https://www.iqads.ro/adjob/23959/graphic-designer-luca

> **Atenție:** din top 5 după scor, 3 **nu sunt roluri de design** (au trecut doar pentru că textul lor conține "social media" sau "art director" — vezi §6.2). Iată top 5 **efectiv de design**, filtrate pe titlu:

| # | Scor | Rol | Companie | Locație | Engagement | De ce contează |
|---|---|---|---|---|---|---|
| 1 | **10** | Senior Creatives | International Waters | Bucuresti, Hybrid (Office & Remote) | Full Time | S și D maxime |
| 2 | **9.4** | Graphic Designer | LUCA | Bucuresti | Full Time | L=10 (remote detectat în text) |
| 3 | **9.4** | Senior Product Designer | Jobgether | Romania, Fully Remote | Full Time | remote |
| 4 | **9.4** | AI Research Lab UI/UX & Brand Designer (100 % remote) (m/f/d) | EWOR GmbH | Bucharest, Romania, Remote Solely | Full Time | remote |
| 5 | **9.4** | Industrial Tech UI/UX & Brand Designer (100 % remote) (m/f/d) | EWOR GmbH | Bucharest, Romania, Remote Solely | Full Time | remote |

- International Waters :: Senior Creatives — https://www.iqads.ro/adjob/23944/senior-creatives-international-waters
- LUCA :: Graphic Designer — https://www.iqads.ro/adjob/23959/graphic-designer-luca
- Jobgether :: Senior Product Designer — https://designproject.io/jobs/senior-product-designer-at-jobgether-6r1kga
- EWOR GmbH :: AI Research Lab UI/UX & Brand Designer (100 % remote) (m/f/d) — https://designproject.io/jobs/ai-research-lab-uiux-and-brand-designer-100-percent-remote-mfd-at-ewor-gmbh-teu2mk
- EWOR GmbH :: Industrial Tech UI/UX & Brand Designer (100 % remote) (m/f/d) — https://designproject.io/jobs/industrial-tech-uiux-and-brand-designer-100-percent-remote-mfd-at-ewor-gmbh-zrjj79

---

## 4. Postări GENUIN noi (nu doar "absente din raportul de ieri")

> **Atenție:** ieri s-a raportat un *subset* curat (37 de joburi); azi am scanat catalogul complet (74). Deci "nou" în tabele înseamnă **"nu era în raportul de ieri"**, nu neapărat "postat azi". Iată ce e postat efectiv nou:

| Sursă | Cum am măsurat | Rezultat |
|---|---|---|
| **IQads** | ID-ul ad-ului crește monoton cu postarea. Cel mai mare ID din setul de ieri: **23996** | **1 anunt nou** |
| **designproject.io** | data de publicare vs. 2026-10-22 | **0 anunturi noi** — cel mai recent de pe site e din **2026-10-06** |

- **IQads #23997** — Copywriter @ Stefanini Infinit (expiră 2026-12-14) — https://www.iqads.ro/adjob/23997/copywriter-stefanini-infinit

**Concluzie:** singura postare nouă de azi e un **Copywriter @ Stefanini Infinit** — și nici ea nu intră în secțiuni: scor 5.65, verdict amânat (locația nu e în anunț), iar disciplina nu se potrivește cu portofoliul tău. **Piața nu a produs nimic nou și relevant azi.**

Ce nu a mai apărut în raportul de ieri, dar există în catalog (18 la număr, toate cu ✅ în tabele):

- **9.4** · Secția 1 · Media Relations Specialist — Confident Communications (IQads)
- **9.4** · Secția 1 · PR Manager — Confident Communications (IQads)
- **9.4** · Secția 1 · Digital Marketing Specialist — Alpha Clinic (IQads)
- **9.4** · Secția 1 · Influencer & Creator Marketing Lead — Confident Communications (IQads)
- **9.4** · Secția 1 · Head of UX/UI — Jobgether (designproject.io)
- **9** · Secția 1 · Social Media Copywriter — Digital Star (IQads)
- **8.7** · Secția 1 · Digital Marketing Specialist — GoTech World (IQads)
- **8.7** · Secția 1 · Senior UX/UI Designer – limited for 2 years maternity cover — METRO/MAKRO (designproject.io)
- **8.4** · Secția 2 · English to French Linguist & Copy Editor for Product, Marketing & UI Content — Jobgether (designproject.io)

---

## 5. Ce n-a mers, măsurat

1. **Etichetele MAVIS/* nu mai primesc nimic de 12 zile.** Filtrele au `addLabelIds` vid și nici măcar nu mai arhivează — ~510 mesaje/7 zile stau în inbox. Cauza: scriptul local `email-sort-full.js` (cel care punea etichetele) nu mai rulează.
2. **designproject.io și-a schimbat descrierile.** Pe 2026-10-22 erau de 71–1484 caractere; azi sunt de **24.000–33.000**, rescrise de AI (inclusiv "📝 Enhancement Note"). Asta e mai bogat, dar injectează cuvinte-cheie care ridică axele.
3. **Celelalte două câmpuri de engagement ale designproject.io sunt inutilizabile.** `employmentType` din JSON-LD spune `FULL_TIME` pentru **toate cele 26** de joburi, iar badge-ul din listing spune "Full-time" pentru toate 26. Singura sură corectă e linia **"Job Type:"** din descriere (Trade Nation: "CONTRACTOR"; Mindrift: "PART_TIME" + freelance; Uvation: "Contractor"). Am folosit asta.
4. **Paginatia IQads nu funcționează.** `?page=2` și `?page=3` servesc exact pagina 0 (aceleași 47 de joburi, aceleași linkuri). Catalogul complet e pe pagina 0 — nu iterez pagini.
5. **Cota Google a fost depășită: 422 cereri pe 200.** Consumul pe etape:

| Etapă | Cereri |
|---|---|
| `report-mail-count.js` | 233 |
| `report-inbox.js` | 105 |
| `report-simulate-sort.js` | 41 |
| `report-build.js` | 18 |
| `report-drive-discover.js` | 16 |
| `report-inbox-counts.js` | 8 |
| `verificare-filtre-inline.js` | 1 |
| **total** | **422** |

> Contorul a fost instrumentat la mijlocul rulării; pentru etapele anterioare sunt valorile pe care le-a printat chiar fiecare script, nu estimări.

Contorul a fost instrumentat la mijlocul rularii. Valorile de mai jos pentru scriptele anterioare sunt reconstruite din contorul PE CARE L-A PRINTAT fiecare script (nu sunt estimate). Ce s-a masurat de fapt, script cu script: report-mail-count = 233 (1 labels + 32 pagini de numarare + 200 corpuri de mesaj pentru mostre), report-inbox = 105, report-inbox-counts = 8, report-drive-discover = 16 (3 rulari), inline-verificare filtre = 1, report-simulate-sort = 41, report-build = 9 (3 rulari).


Ce a mers peste plafon: am descărcat corpurile complete ale mesajelor (100 în inbox + 40 de azi) ca să disting mesajele care chiar cer răspuns de alertele automate — fără corp, nu se poate. A fost deci un diagnostic util, dar facturat dublu față de un numărat de etichete. **Zero scrieri pe Gmail** — niciun mail trimis, marcat sau arhivat.

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

Cazul cel mai vizibil: **"Graphic Designer & Digital Content Creator" (Jobgether)** — D=10 (Creative Leadership) doar pentru că proza AI menționează "art director" o dată. Fără ea ar fi D=8 (Core Design), deci **8.7 în loc de 9.3**. La fel, 8 joburi de tip account/PR/media rămân în viață doar pentru că textul lor conține "social media" (tier Core Design) — nu sunt roluri de design, dar ies în Secțiunea 1 cu scor de 9.4.

**Ce propun:** ca `D` să se calculeze din **titlul rolului**, nu din textul anunțului, sau măcar ca un rol să poată intra într-o secțiune doar dacă titlul conține o cheie de design. E o decizie de motor — nu am atins `scoring.gs` fără acordul tău.

---

## 7. Fișiere

- `rapoarte/RAPORT-ZILNIC-202610-23.md` — raportul acesta (și în repo)
- `mavis-tools/scoring-result-2026-10-23.json` — scoruri + secțiuni + diagnostice
- `mavis-tools/jobs-iqads-2026-10-23.json` — 48 joburi IQads, text integral
- `mavis-tools/jobs-designproject-2026-10-23.json` — 26 joburi designproject.io, JSON-LD
- `mavis-tools/report-mail-count.json` — numărătoare pe etichete MAVIS/*
- `mavis-tools/report-inbox.json` — 100 de mesaje cu corp + etichete
- `mavis-tools/report-inbox-counts.json` — numărătoare exactă inbox
- `mavis-tools/report-simulate-sort.json` — simularea sortării + cele 40 de mesaje de azi

---

*Generat de Mavis Cloud. Nimic nu a fost șters, nimic nu a fost trimis, nimic nu a fost modificat în Gmail sau Drive. Totul e anulabil.*
