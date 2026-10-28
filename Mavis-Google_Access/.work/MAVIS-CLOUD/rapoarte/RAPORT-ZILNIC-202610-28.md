# Raport zilnic — miercuri 28 octombrie 2026

> Generat de Mavis Cloud · 20 mesaje noi măsurate azi (00:00–09:22 EEST) · 57 joburi analizate
> Cota Google: **201 cereri** (plafon 200 — **depășit cu 1**). Zero scrieri pe Gmail; tot consumul a fost măsurare și diagnostic. Detaliu în §5.

---

## 1. Gmail — etichetele de categorie

### 1.1 Rezultatul scurt
**Pe etichetele de categorie a intrat azi: 18 etichete.** În ultimele 24h: 128; în 7 zile: 710.

Azi au intrat **20 mesaje** în total, iar în inbox sunt **17**. **4 dintre ele nu au primit nicio etichetă de categorie** (nu se potrivesc niciunui filtru de categorie — deci rămân în inbox, neetichetate).

> **18 etichete pe 16 mesaje** — 2 mesaje primesc două etichete de categorie (ex. o alertă de job care intră și la „Joburi" și la „Newsletter"). De aceea suma pe etichete e mai mare decât numărul de mesaje distincte.

### 1.2 Măsurătoarea pe etichete (numărare exactă, cu paginare)

| Etichetă | azi | 24h | 7z | 30z | Ultimul mesaj etichetat |
|---|---|---|---|---|---|
| `MAVIS/Joburi` | 5 | 39 | 39 | 350 | Wed, 28 Oct 2026 |
| `AI Folder/AI si Comunitati` | 3 | 18 | 18 | 128 | Wed, 28 Oct 2026 |
| `Socials` | 3 | 4 | 4 | 212 | Wed, 28 Oct 2026 |
| `Newsletter` | 6 | 50 | 50 | 271 | Wed, 28 Oct 2026 |
| `Finante` | 0 | 3 | 3 | 8 | Tue, 27 Oct 2026 |
| `Personal` | 0 | 0 | 0 | 0 | n/a |
| `De raspuns` | 0 | 0 | 0 | 28 | Fri, 9 Oct 2026  |
| `Facturi si Conturi` | 0 | 0 | 0 | 1 | Fri, 09 Oct 2026 |
| `Optimus CD` | 1 | 14 | 596 | 650 | Tue, 27 Oct 2026 |

**Concluzie:** 6 categorii primesc mesaje (`MAVIS/Joburi`, `AI Folder/AI si Comunitati`, `Socials`, `Newsletter`, `Finante`, `Optimus CD`); 2 categorii nu primesc nimic de **18 zile** (pe `De raspuns`, `Facturi si Conturi` = **09.10.2026**); o categorie n-a fost folosită niciodată (0 pe 30 de zile, fără istoric) (`Personal`).

> Zero pe o fereastră nu înseamnă "etichetă goală" — înseamnă "eticheta nu mai primește nimic". Verificat pe 4 ferestre.

### 1.3 Filtrele, măsurate azi

Filtre cu criteriu de interogare pe cont: **6**, din 19 total. **6** dintre ele are `addLabelIds`, iar **6** atinge o etichetă de categorie. Criteriul celui de joburi, citit live azi:

```
from:{jooble bestjobs hipo indeed jobleads linkedin} OR subject:{job angajare vacanta oportunitate}
```

#### 6 filtre FUNCȚIONEAZĂ

**6 dintre 6 filtre lovesc efectiv mesaje.** `from:(notifications@github.com OR *jules*) OR subj…` → **929** mesaje în 30 de zile, etichetează `agenti`; `from:{jooble bestjobs hipo indeed jobleads linkedi…` → **1098** mesaje în 30 de zile, etichetează `joburi`; `from:{substack goatacademy aiautomationsociety sad…` → **389** mesaje în 30 de zile, etichetează `ai`; `from:{skool facebook instagram pinterest tiktok po…` → **146** mesaje în 30 de zile, etichetează `social`; `from:{noreply no-reply newsletter digest mail@ inf…` → **1215** mesaje în 30 de zile, etichetează `newsletter`; `from:{kraken tradingview bitunix coinbase binance}…` → **9** mesaje în 30 de zile, etichetează `finante`


**Inboxul nu se golește.** Măsurat pe cele 20 mesaje de azi, etichetele lor reale: **17 sunt încă în INBOX**, dar **doar 5 au rămas UNREAD**. Deci filtrele **curăță „necitit"**, dar **nu scoate mesajele din inbox**:

| Fereastră | În inbox | În toate stările |
|---|---|---|
| azi | 17 | 20 |
| 24h | 83 | 97 |
| 7z | 643 | 1331 |

**~643 mesaje stau în inbox într-o săptămână** (~92/zi).

### 1.4 Cum ar fi fost sortate mesajele de azi

Simulare pe cele 20 mesaje de azi, cu **aceleași criterii** ale filtrelor (fără scriere):

| Categorie | Mesaje azi |
|---|---|
| `MAVIS/Joburi` | 6 |
| `AI Folder/AI si Comunitati` | 3 |
| `Socials` | 4 |
| `Newsletter` | 6 |
| `Finante` | 0 |
| `Personal` | 0 |
| `De raspuns` | 0 |
| `Facturi si Conturi` | 0 |
| `Optimus CD` | 1 |
| *niciun filtru se potrivește* | 4 |

> Unele mesaje se potrivesc la 2 filtre (ex. "Joburi" + "Newsletter" de la LinkedIn), deci suma poate depăși 20.

**Observație:** **0 mesaje** de azi sunt notificări ale agenților tăi (Jules și GitHub Actions pe repo-urile proprii). Categoria dedicata lor e `Optimus CD`, care a primit 1 mesaj azi, iar filtrul ei functioneaza efectiv. In rest, **6 din 9 categorii** primesc mesaje, iar 3 nu primesc.


### 1.5 Mesajele care chiar necesită răspuns

Clasificarea e făcută din date, nu dintr-o listă scrisă cu mâna: 0 cer răspuns explicit, 6 cer o decizie, 1 este alerte de job care nu ating profilul tău, 13 sunt newsletter/promoție, 0 sunt zgomot de pipeline.

**Niciun mesaj nu cere explicit un răspuns.**

**Ceres o decizie sau o acțiune:**

- **Bestjobs** — 06:10 UTC. *New opportunities in top companies* _(alerta de job cu rol de design)_ — Hello Alexandru Popescu! Here are some new jobs we think you would like. Update your CV to receive the most relevant jobs! | Colaboratori design grafic creatie si grafica -----------------------------
- **Bestjobs** — 05:06 UTC. *13 new jobs for you: graphic design, bucharest* _(alerta de job cu rol de design)_ — Hello Alexandru Popescu! Here are some new jobs we think you would like. Update your CV to receive the most relevant jobs! | Graphic Designer ---------------------------------- ELBI ElectricLighting B
- **Jooble** — 04:52 UTC. *Travel Planner caută Full-Stack Engineer (Laravel + Vue.js), UX-focused, Customer-Facing Web și 100 mai multe oferte noi de muncă* _(alerta de job cu rol de design)_ — Anunțurile dvs. zilnice de oferte de muncă pentru 28 octombrie, 2026 Verificați ofertele noi de muncă pe care le-am găsit pentru dvs. astăzi. <text></text> Afișați toate ofertele noi de muncă UX Desig
- **Joburi Hipo.ro** — 04:33 UTC. *Alex - 7 Joburi noi adaugate pentru tine pe hipo.ro* _(contul cere o actiune (parola / confirmare))_ — Peste 5000 de Locuri de munca si Joburi pentru profesionisti, studenti si absolventi. Intra in contul tau CV-urile mele Domeniile selectate ( modifica ) Orasele selectate ( modifica ) Publicitate - Ag
- **Google** — 00:35 UTC. *Security alert* _(alerta de securitate — cere verificare umana)_ — [image: Google] You allowed Sentinel Hermes Google Access access to some of your Google Account data apvizual@gmail.com If you didn't allow Sentinel Hermes Google Access access to some of your Google 
- **apvizual-max** — 00:32 UTC. *[apvizual-max/MAVIS-OPTIMUS-CI] Run failed: CI-verify - main (1c5ec27)* _(workflow CI esuat — cere actiune)_ — [apvizual-max/MAVIS-OPTIMUS-CI] CI-verify workflow run Repository: apvizual-max/MAVIS-OPTIMUS-CI Workflow: CI-verify Duration: 18.0 seconds Finished: 2026-10-28 00:32:36 UTC View results: Jobs: * Port

**Alerte de job care NU ating profilul de design** (informativ, 1):

- Jooble — 00:20 UTC · *🔔 Toennies company caută Lucrător la ambalare și 84 mai multe oferte noi de muncă*

**Newsletter / promoție, fără acțiune** (13): Project 720 (Skool), The RoboNuggets Network (free) (Skool), Isha News, AI Automation Society (Skool), DocFreemason, Alerta eJobs, Bitdefender, Numerologist.com, AI Money Lab (Skool), David, Mikki Willis, Alexandru Popescu (via Google Drive), Felix & Winston 🐶

**Leads din alertele de job.** Fiecare poartă propria cale de verificare, declarată mai jos — nu toate sunt citite direct de pe pagină:

##### Graphic Designer — part-time 15h (remote) @ CreativeEd Media (NOU)

Din alerta **Bestjobs** — *13 new jobs for you: graphic design, bucharest*

**Cum a fost verificat:** Text integral al anuntului, obtinut din indexarea motorului de cautare pe bestjobs.eu/loc-de-munca/graphic-designer-part-time-15h-remote. Pagina /en/job/ raspunde 403 pentru acces automat, deci NU am deschis pagina direct.

Angajator: CreativeEd Media. Rol de Graphic Designer creativ, 100% remote, part-time 15 ore pe saptamana. Materiale pentru campanii de marketing, bannere, flyere, cataloage, carti de vizita, evenimente, mock-up-uri si continut vizual pentru mediul digital. Echipa internationala.

**Cerințe:**

- Graphic Designer creativ, cu atentie la detalii si simt estetic
- Transformarea ideilor in materiale vizuale moderne, attractive, cu personalitate
- Persoana organizata, atenta la detalii, creativa si eficienta
- Capabilitatea de a livra materiale de calitate intr-un timp scurt, respectand termenele-limita, inclusiv la solicitari urgente

**Rate-uri publicate:**

- 525 EURO/luna (publicat de angajator)
- Part-time, 15 ore pe saptamana, zilele de lucru stabilite de comun acord

**Condiții:** 100% remote. Remuneratie 525 EUR/luna, plata la timp. Flexibilitate, dar se cere seriozitate si respectarea termenelor-limita.

**Cum se aplică:** Aplicare direct pe anuntul Bestjobs. Echipa internationala.

> ⚠️ La 525 EUR/luna pentru 15h/saptamana, iesitul orar e sub 9 EUR/h — mult sub rata micro1 (50–90 USD/h) si sub ce plateste YO AI Labs. E o masa de baza, nu un venit. Merita doar daca e fundal sau intrare in platforma.

- https://www.bestjobs.eu/en/job/graphic-designer-part-time-15h-remote

##### Graphic Designer @ ELBI ElectricLighting (NOU)

Din alerta **Bestjobs** — *13 new jobs for you: graphic design, bucharest*

**Cum a fost verificat:** Sumat de pe pagina de listare Bestjobs (accesibila prin indexarea motorului de cautare): titlu, angajator, localizare si interval de plata estimat. Pagina de anunt /en/job/graphic-designer-723 raspunde 403 — NU am deschis-o.

ELBI ElectricLighting angajeaza Graphic Designer. Localizare: Bragadiru, Romania (Bucuresti — zona Ilfov).

**Cerințe:**

- Necesa in anunt (pagina de anunt este blocata pentru acces automat; vezi caveat)

**Rate-uri publicate:**

- 1195 - 1325 (Estimare — valoarea afisata de Bestjobs, nu de angajator)

**Condiții:** Bragadiru, Romania.

**Cum se aplică:** Aplicare pe anuntul Bestjobs.

> ⚠️ Salariul e ESTIMAT de Bestjobs, nu publicat de angajator. Nu am putut citi cerintele de pe pagina anuntului (403 la acces automat) — le-am dedus din pagina de listare, care n-are sectiunea de cerinte. Bragadiru = Ilfov, deci nu e fix la centrul orasului.

- https://www.bestjobs.eu/en/job/graphic-designer-723

##### UX/UI Designer — Video Annotation Remote (micro1 / AI training) (REAPĂRUT)

Din alerta **Bestjobs** — *13 new jobs for you: graphic design, bucharest*

**Cum a fost verificat:** Text integral al anuntului, obtinut din indexarea motorului de cautare pe bestjobs.eu/loc-de-munca/ux-ui-designer-video-annotation-remote-2. Pagina /en/job/ raspunde 403 pentru acces automat, deci NU am deschis pagina direct.

micro1 cauta UX/UI Designeri si profesionisti cu experienta in domenii vizuale/digitale pentru un proiect international de AI Training, axat pe video annotation si robotica. Participantii analizeaza videoclipuri in care brate robotice executa proceduri si evalueaza/anoteaza fiecare sesiune conform unor guideline-uri clare. Rolul se potriveste cu persoane atente la detalii, cu experienta in UX/UI, web design, video editing, fotografie, filmmaking, audiovisual production, robotics sau engineering.

**Cerințe:**

- Experienta intr-unul sau mai multe dintre: UX/UI Design, Web Design, Video Editing, Filmmaking, productie audiovizuala
- Experienta anterioara in: Video Annotation, Data Labeling, AI Training, Machine Learning datasets, evaluarea continutului video, robotica — avantaj important, dar NU obligatoriu
- Atentie la detalii si consistenta calitatii: marcarea exacta a actiunilor, comportamentelor si rezultatelor conform guideline-urilor primite
- Documentarea clara a observatiilor si justificarea fiecarei evaluari
- Feedback catre traineri si mentinerea unui nivel constant de calitate
- Livrarea taskurilor in termenele solicitate
- Engleză avansată (cerută explicit)

**Rate-uri publicate:**

- 3000 EUR/luna (cum apare pe anuntul Bestjobs)
- Contractor, nu angajare. Fără experiență anterioară în AI cerută

**Condiții:** Remote, contractor. Proiect internațional de AI training. Fără experiență anterioară în AI.

**Cum se aplică:** Aplicare pe anuntul Bestjobs („Aplică & Începe interviul”). Platforma micro1 conduce interviul, cu assessment de domeniu. Aceleași joburi apar și ca 'Xperteez Technology' pe designproject.io — NU confunda platforma cu jobul.

> ⚠️ Bestjobs afișează 3000 EUR/luna; pe platforma micro1 același tip de rol apare la 50–90 USD/oră. Diferența e de metodă de tarifare (lună vs. oră) și de agregator, nu de job — verifică rata reală direct pe jobs.micro1.ai înainte să te bazezi pe 3000 EUR. Platforma a mai apărut și pe 26.10 cu un rol similar, dar nu același titlu.

- https://www.bestjobs.eu/loc-de-munca/ux-ui-designer-video-annotation-remote-2

##### Editor imagine TV Junior @ Aleph News (NOU)

Din alerta **Hipo.ro** — *Alex - 7 Joburi noi adaugate pentru tine pe hipo.ro*

**Cum a fost verificat:** Pagina HiPo.ro citita DIRECT (HTTP 200) — salariul, cerintele si conditiile sunt textul paginii de anunt, nu un snippet.

Aleph News angajeaza Editor imagine TV Junior, full-time, on-site in Bucuresti. Munca de montaj pentru stiri si productii editoriale: montarea materialelor video pentru stiri, organizarea si editarea secventelor video pentru impact maxim, sincronizarea muzicii si efectelor sonore, arhiva video, statia de editare. Ritm alert, specific productiei de stiri.

**Cerințe:**

- Adobe Premiere Pro, Adobe After Effects si Adobe Photoshop — folosite foarte bine
- Baza solida de montaj video (chiar daca nu ai experienta in TV)
- Rapid, organizat si atent la detalii
- Dispozitie de a invata constant si de a-ti imbunatati tehnica
- Familiarizare ( sau curiozitatea de a invata ) cu DaVinci Resolve si instrumente moderne de editare cu AI
- UNATC sau similar = avantaj, nu obligatoriu
- Portofoliul conteaza mai mult decat anii de experienta

**Rate-uri publicate:**

- 4000 - 5000 RON NET/luna (publicat de angajator, confirmat pe pagina HiPo)

**Condiții:** Bucuresti, full-time, on-site. Nivel job: 0-1 ani experienta.

**Cum se aplică:** Aplicare pe HiPo.ro. Portofoliu cerut explicit.

> ⚠️ Este rol de EDITOR VIDEO, nu de design grafic — nu atinge direct profilul de art direction. Totuși: 4000-5000 RON net cu doar 0-1 ani cerință e un prag real de intrare pe piata de continut, iar portofoliul conteaza mai mult decat anii de experienta — deci e o usa de intrare cu prag mic, nu un job de design. On-site, la ritm de productie de stiri.

- https://www.hipo.ro/locuri-de-munca/locuri_de_munca/268926/Aleph-News/Editor-imagine-TV-Junior

##### Junior Mid-Level Graphic Designer & DTP Specialist @ BRAYTRON SRL (NEVERIFICAT PE PAGINA)

Din alerta **eJobs** — *Un job nou te asteapta azi pe eJobs.ro!*

**Cum a fost verificat:** DOAR corpul emailului de alerta (snippet inclus). Pagina eJobs.ro raspunde 403 pentru acces automat, iar motorul de cautare nu a indexat anuntul — deci nu am putut citi niciun camp al anuntului.

BRAYTRON SRL — Junior Mid-Level Graphic Designer & DTP Specialist. Singurul anunt din alerta de azi de pe eJobs, cu 1 job potrivit profilului. Anuntul a venit fara text/plain (doar HTML), deci informatiile vin din continutul de tip snippet.

**Cerințe:**

- Necesa in anunt — pagina eJobs raspunde 403 pentru acces automat, deci NU am putut citi cerintele

**Condiții:** Necunoscute — anuntul nu a fost citit pe pagină.

**Cum se aplică:** Aplicare pe eJobs.ro.

> ⚠️ NEVERIFICAT. eJobs.ro raspunde 403 (Forbidden) la acces automat, iar cautarea nu a indexat anuntul. Tot ce se stie aici vine din corpul emailului de alerta. Fara salariu, fara cerinte, fara oras — deschide anuntul manual inainte sa iei in calcul. Titlul promite junior-to-mid, adica sub pragul de senioritate pe care-l cauti.

- https://www.ejobs.ro

---
## 2. Joburi — scorate cu `ALEX-KIT/scoring.gs`

**57 joburi analizate** (IQads 42 + designproject.io 15) → 29 păstrate în tabele, 28 drop-uri, din care **12 cu verdict amânat** (locația nu e publicată de sursă). **0 joburi noi** față de 2026-10-27.

Surse: **IQads** (tabloul AdJob activ, citit azi) + **designproject.io** (România + București).

> ⛔ **Expirate marcate în tabele.** La IQads data de expirare vine direct din anunț. La designproject.io `validThrough` = data postării + 30 zile — măsurat pe toate cele 15 de joburi (15 exacte, 0 cu o zi de fus orar, 0 altfel), deci e o expirare reală, nu o derivare inutilă. 4 joburi din tabele au expirat și nu se mai pot aplica.

| | S | D | L | E |
|---|---|---|---|---|
| **S** — senioritate | 0.35 | | | |
| **D** — disciplină | | 0.30 | | |
| **L** — locație | | | 0.20 | |
| **E** — engagement | | | 0.15 | |

### 2.1 Secțiunea 1 — scor maxim — senior/lead, remote sau București, full-time (14)

| Scor | Tag | S/D/L/E | Rol | Companie | Locație | Engagement | Expirare | Nou |
|---|---|---|---|---|---|---|---|---
| **10** | [B2C] | 10/10/10/10 | Senior Creatives | International Waters | Bucuresti, Hybrid (Office & Remote) | Full Time | expiră 2026-11-01 |
| **9.6** | [DTC] | 10/10/8/10 | Art Director | Mercury360 | Bucuresti | Full Time | expiră 2026-12-25 |
| **9.4** | [DTC] | 10/8/10/10 | Media Relations Specialist | Confident Communications | Bucuresti | Full Time | expiră 2026-11-30 |
| **9.4** | [DTC] | 10/8/10/10 | PR Manager | Confident Communications | Bucuresti | Full Time | expiră 2026-11-30 |
| **9.4** | [B2B] | 10/8/10/10 | Digital Marketing Specialist | Alpha Clinic | Hybrid (Office & Remote) | Full Time | expiră 2026-11-27 |
| **9.4** | [DTC] | 10/8/10/10 | Graphic Designer | LUCA | Bucuresti | Full Time | expiră 2026-11-13 |
| **9.4** | [DTC] | 10/8/10/10 | Account Manager | AdSymphony | Hybrid (Office & Remote) | Full Time | expiră 2026-11-01 |
| **9.4** | [B2B] | 10/8/10/10 | Influencer & Creator Marketing Lead | Confident Communications | Bucuresti | Full Time | expiră 2026-10-31 |
| **9.4** | [DTC] | 10/8/10/10 | Senior Product Designer | Jobgether | Romania, Fully Remote | Full Time | postat 2026-10-02 · expiră 2026-11-01 |
| **9.4** | [DTC] | 10/8/10/10 | AI Research Lab UI/UX & Brand Designer (100 % remote) (m/f/d) | EWOR GmbH | Bucharest, Romania, Remote Solely | Full Time | postat 2026-09-25 · expiră 2026-10-25 ⛔ **EXPIRAT** |
| **9.4** | [DTC] | 10/8/10/10 | Industrial Tech UI/UX & Brand Designer (100 % remote) (m/f/d) | EWOR GmbH | Bucharest, Romania, Remote Solely | Full Time | postat 2026-09-18 · expiră 2026-10-18 ⛔ **EXPIRAT** |
| **9** | [B2B] | 10/8/8/10 | Social Media Specialist | Viva Credit | Romania | Full Time | expiră 2026-12-12 |
| **9** | [B2B] | 10/8/8/10 | Social Media Copywriter | Digital Star | Romania | Full Time | expiră 2026-10-30 |
| **8.7** | [DTC] | 8/8/10/10 | Digital Marketing Specialist | GoTech World | Bucuresti, Hybrid (Office & Remote) | Full Time | expiră 2026-11-30 |

<!-- linkuri -->
- International Waters :: Senior Creatives — https://www.iqads.ro/adjob/23944/senior-creatives-international-waters
- Mercury360 :: Art Director — https://www.iqads.ro/adjob/23999/art-director-mercury360
- Confident Communications :: Media Relations Specialist — https://www.iqads.ro/adjob/23978/media-relations-specialist-confident-communications
- Confident Communications :: PR Manager — https://www.iqads.ro/adjob/23977/pr-manager-confident-communications
- Alpha Clinic :: Digital Marketing Specialist — https://www.iqads.ro/adjob/23970/digital-marketing-specialist-alpha-clinic
- LUCA :: Graphic Designer — https://www.iqads.ro/adjob/23959/graphic-designer-luca
- AdSymphony :: Account Manager — https://www.iqads.ro/adjob/23946/account-manager-adsymphony
- Confident Communications :: Influencer & Creator Marketing Lead — https://www.iqads.ro/adjob/23941/influencer-creator-marketing-lead-confident-agency
- Jobgether :: Senior Product Designer — https://designproject.io/jobs/senior-product-designer-at-jobgether-6r1kga
- EWOR GmbH :: AI Research Lab UI/UX & Brand Designer (100 % remote) (m/f/d) — https://designproject.io/jobs/ai-research-lab-uiux-and-brand-designer-100-percent-remote-mfd-at-ewor-gmbh-teu2mk
- EWOR GmbH :: Industrial Tech UI/UX & Brand Designer (100 % remote) (m/f/d) — https://designproject.io/jobs/industrial-tech-uiux-and-brand-designer-100-percent-remote-mfd-at-ewor-gmbh-zrjj79
- Viva Credit :: Social Media Specialist — https://www.iqads.ro/adjob/23990/social-media-specialist-viva-credit
- Digital Star :: Social Media Copywriter — https://www.iqads.ro/adjob/23940/social-media-copywriter-digital-star
- GoTech World :: Digital Marketing Specialist — https://www.iqads.ro/adjob/23981/digital-marketing-specialist-gotech-world

### 2.2 Secțiunea 2 — contract / B2B — senioritate bună, engagement pe contract (3)

| Scor | Tag | S/D/L/E | Rol | Companie | Locație | Engagement | Expirare | Nou |
|---|---|---|---|---|---|---|---|---
| **8.4** | [B2B] | 8/8/10/8 | English to French Linguist & Copy Editor for Product, Marketing & UI Content | Jobgether | Romania, Fully Remote | Contract | postat 2026-10-02 · expiră 2026-11-01 |
| **8.4** | [DTC] | 8/8/10/8 | Freelance Brand Designer | Mindrift | Romania, Fully Remote | Part Time, Contract | postat 2026-09-25 · expiră 2026-10-25 ⛔ **EXPIRAT** |
| **8.4** | [DTC] | 8/8/10/8 | Freelance Graphic Designer | Mindrift | Romania, Remote Solely | Part Time, Contract | postat 2026-09-21 · expiră 2026-10-21 ⛔ **EXPIRAT** |

<!-- linkuri -->
- Jobgether :: English to French Linguist & Copy Editor for Product, Marketing & UI Content — https://designproject.io/jobs/english-to-french-linguist-and-copy-editor-for-product-marketing-and-ui-content-at-jobgether-j0zyru
- Mindrift :: Freelance Brand Designer — https://designproject.io/jobs/freelance-brand-designer-at-mindrift-ymls4c
- Mindrift :: Freelance Graphic Designer — https://designproject.io/jobs/freelance-graphic-designer-at-mindrift-snjhmz

### 2.3 Secțiunea 3 — mid-level — potrivire bună, senioritate sub prag (0)

*Niciun job în această secțiune.*

### 2.4 Secțiunea 4 — on-site în afara Bucureștiului — doar dacă S=10 și D≥8 (0)

*Niciun job în această secțiune.*

### 2.5 Verdict amânat — locația nu e publicată de sursă (12)

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

### 2.6 Drop-uri (circuit breaker) — 28

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
| Tehnician montaj si logistica evenimente (BTL) | Hexagon X | disciplina nu se potrivește niciunui tier — Tehnician montaj si logistica evenimente (BTL) |  |
| Senior Account Manager | Propaganda | disciplina nu se potrivește niciunui tier — Senior Account Manager |  |
| Account Director | Propaganda | disciplina nu se potrivește niciunui tier — Account Director |  |
| Group Account Director | Propaganda | disciplina nu se potrivește niciunui tier — Group Account Director |  |
| Growth Marketing Manager | Voxa | disciplina nu se potrivește niciunui tier — Growth Marketing Manager |  |
| Digital Workflow Developer — Rapid Prototyping and Pilots for NATO with security clearance | WLG | rol necorelabil cu portofoliul — Digital Workflow Developer — Rapid Prototyping and Pilots for NATO with security clearance |  |
| Senior UX Engineer | Lenovo | disciplina nu se potrivește niciunui tier — Senior UX Engineer |  |
| English to Romanian Linguist & Copy Editor for Product, Marketing & UI Content | Welo Global | disciplina nu se potrivește niciunui tier — English to Romanian Linguist & Copy Editor for Product, Marketing & UI Content |  |
| Senior UX Researcher (f/m/d) | Awin | rol necorelabil cu portofoliul — Senior UX Researcher (f/m/d) |  |
| Front-end Engineer - SDD UI @ING Hubs Romania | ING | rol necorelabil cu portofoliul — Front-end Engineer - SDD UI @ING Hubs Romania |  |
| Senior Front-End Software Development Engineer (UI Foundations) | Criteo | rol necorelabil cu portofoliul — Senior Front-End Software Development Engineer (UI Foundations) |  |
| Senior Motion Graphic Designer | Jobgether | rol necorelabil cu portofoliul — Senior Motion Graphic Designer |  |
| Solution Engineering & AI Prototyping Specialist | PwC | rol necorelabil cu portofoliul — Solution Engineering & AI Prototyping Specialist |  |
| Solution Engineering & AI Prototyping Specialist | Pwc CEE | rol necorelabil cu portofoliul — Solution Engineering & AI Prototyping Specialist |  |

---

## 3. Top 5 joburi cu scor

| # | Scor | Tag | Rol | Companie | Locație | Engagement | Expirat? | De ce contează |
|---|---|---|---|---|---|---|---|---|
| 1 | **10** | [B2C] | Senior Creatives | International Waters | Bucuresti, Hybrid (Office & Remote) | Full Time | nu | S și D maxime |
| 2 | **9.6** | [DTC] | Art Director | Mercury360 | Bucuresti | Full Time | nu | S și D maxime |
| 3 | **9.4** | [DTC] | Media Relations Specialist | Confident Communications | Bucuresti | Full Time | nu | D ridicat de prosa ("social media") |
| 4 | **9.4** | [DTC] | PR Manager | Confident Communications | Bucuresti | Full Time | nu | D ridicat de prosa ("social media") |
| 5 | **9.4** | [B2B] | Digital Marketing Specialist | Alpha Clinic | Hybrid (Office & Remote) | Full Time | nu | D ridicat de prosa ("social media") |

- International Waters :: Senior Creatives — https://www.iqads.ro/adjob/23944/senior-creatives-international-waters
- Mercury360 :: Art Director — https://www.iqads.ro/adjob/23999/art-director-mercury360
- Confident Communications :: Media Relations Specialist — https://www.iqads.ro/adjob/23978/media-relations-specialist-confident-communications
- Confident Communications :: PR Manager — https://www.iqads.ro/adjob/23977/pr-manager-confident-communications
- Alpha Clinic :: Digital Marketing Specialist — https://www.iqads.ro/adjob/23970/digital-marketing-specialist-alpha-clinic

> **Atenție:** din top 5 după scor, 3 **nu sunt roluri de design** (au trecut doar pentru că textul lor conține "social media" sau "art director" — vezi §6.2). Iată top 5 **efectiv de design**, filtrate pe titlu:

| # | Scor | Rol | Companie | Locație | Engagement | Expirat? | De ce contează |
|---|---|---|---|---|---|---|---|
| 1 | **10** | Senior Creatives | International Waters | Bucuresti, Hybrid (Office & Remote) | Full Time | nu | S și D maxime |
| 2 | **9.6** | Art Director | Mercury360 | Bucuresti | Full Time | nu | S și D maxime |
| 3 | **9.4** | Graphic Designer | LUCA | Bucuresti | Full Time | nu | L=10 (remote detectat în text) |
| 4 | **9.4** | Senior Product Designer | Jobgether | Romania, Fully Remote | Full Time | nu | remote |
| 5 | **9.4** | AI Research Lab UI/UX & Brand Designer (100 % remote) (m/f/d) | EWOR GmbH | Bucharest, Romania, Remote Solely | Full Time | ⛔ da | remote |

- International Waters :: Senior Creatives — https://www.iqads.ro/adjob/23944/senior-creatives-international-waters
- Mercury360 :: Art Director — https://www.iqads.ro/adjob/23999/art-director-mercury360
- LUCA :: Graphic Designer — https://www.iqads.ro/adjob/23959/graphic-designer-luca
- Jobgether :: Senior Product Designer — https://designproject.io/jobs/senior-product-designer-at-jobgether-6r1kga
- EWOR GmbH :: AI Research Lab UI/UX & Brand Designer (100 % remote) (m/f/d) — https://designproject.io/jobs/ai-research-lab-uiux-and-brand-designer-100-percent-remote-mfd-at-ewor-gmbh-teu2mk

---

## 4. Postări GENUIN noi (nu doar "absente din raportul de ieri")

> "nou" în tabele înseamnă **"nu era în raportul de ieri"**, nu neapărat "postat azi". Iată ce e postat efectiv nou:

| Sursă | Cum am măsurat | Rezultat |
|---|---|---|
| **IQads** | ID-ul ad-ului crește monoton cu postarea. Cel mai mare ID din setul de ieri: **23999** | **0 anunțuri noi** |
| **designproject.io** | data de publicare vs. ultima rulare | **0 anunțuri noi** — cel mai recent de pe site e din **2026-10-06** |

**Concluzie:** **nicio postare nouă față de ultima rulare.** Piața nu a produs nimic nou relevant azi.


---

## 5. Ce n-a mers, măsurat

1. **3 din 9 categorii nu mai primesc nimic** (2 de 18 zile, 1 n-a fost folosită niciodată). Cauza pentru 3 dintre ele: **nu au filtru creat** (`Personal`, `De raspuns`, `Facturi si Conturi`) — deci nimic nu le poate eticheta, oricare ar fi criteriul. Starea filtrelor, masurata azi: **6 functioneaza, 0 sunt nefunctionale**. ~643 mesaje/7 zile stau in inbox.
2. **designproject.io servește descrieri foarte inegale** (16612–30012 de caractere pe cele 15 de joburi, măsurat azi). Cele mai lungi sunt rescrise de AI și injectează cuvinte-cheie care ridică axele — vezi §6.2.
3. **Celelalte două câmpuri de engagement ale designproject.io sunt inutilizabile.** `employmentType` din JSON-LD spune `FULL_TIME` pentru 15 din 15, iar badge-ul din listing spune "Full-time" pentru 15 din 15. Singura sură corectă e linia **"Job Type:"** din descriere — prezentă la 15 din 15. Am folosit asta.
4. **Paginatia IQads nu funcționează.** `?page=2` și `?page=3` servesc exact pagina 0 (aceleași 42 de linkuri — verificat azi pe 0, 2, 3). Catalogul complet e pe pagina 0 — nu iterez pagini.
5. **Cota Google: 201 cereri pe 200** (**depășit cu 1**). Consumul pe etape:

| Etapă | Cereri |
|---|---|
| `report-mail-count.js` | 68 |
| `report-simulate-sort.js` | 66 |
| `report-filter-state.js` | 24 |
| `report-inbox-counts.js` | 18 |
| `readbodies.js` | 10 |
| `inline` | 5 |
| `report-folder-discover.js` | 4 |
| `report-build.js` | 4 |
| `extract.js` | 2 |
| **total** | **201** |

> Rulare 2026-10-28 (raport zilnic). Contor pornit de la zero.

**Ce a mers peste plafon:** 17 cereri de **diagnostic** care NU sunt masurarea zilei (`readbodies.js` 10, `inline` 5, `extract.js` 2) — citirea manuala a corpurilor ca sa separ ce cere raspuns de ce e doar alerta. Restul consumului e pipeline-ul standard.

Au fost cheltuite pe **înțelegerea** stării, nu pe măsurarea zilei. Zero scrieri pe Gmail — niciun mail trimis, marcat sau arhivat, niciun filtru modificat.

---

## 6. Două semnalări ale motorului de scoring (portul rămâne fidel — decizia e a ta)

### 6.1 "remote" pozitiv fals — 1 joburi

| Rol | Companie | De ce e fals | L |
|---|---|---|---|
| Graphic Designer | LUCA | negatie: `nu se lucreaza remote` | 10 |

"Remote" apare în text, dar jobul **nu** e remote. `L` ar trebui să fie 8 (București) sau 0 (necunoscut), nu 10. Diferență: **0.4 puncte** per job. Nu am atins motorul — portul e fidel prin design.

### 6.2 Axa D ridicată de prosa, nu de titlu — 14 joburi (17 semnalări)

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

- `rapoarte/RAPORT-ZILNIC-202610-28.md` — raportul acesta (și în repo)
- `mavis-tools/scoring-result-2026-10-28.json` — scoruri + secțiuni + diagnostice
- `mavis-tools/jobs-iqads-2026-10-28.json` — joburi IQads, text integral
- `mavis-tools/jobs-designproject-2026-10-28.json` — joburi designproject.io, JSON-LD
- `mavis-tools/jobs-2026-10-27.json` — setul normalizat de ieri (cu care s-a comparat)
- `mavis-tools/report-mail-count.json` — numărătoare pe etichetele de categorie
- `mavis-tools/report-inbox-counts.json` — numărătoare exactă inbox
- `mavis-tools/report-simulate-sort.json` — simularea sortării + mesajele de azi
- `mavis-tools/report-source-probe.json` — sonda de surse (comportamentul iqads.ro / designproject.io, măsurat azi)
- `mavis-tools/report-filter-state.json` — starea filtrelor Gmail + testul paranteze-vs-acolade (măsurat azi)
- `mavis-tools/report-triage.js` — clasificatorul mesajelor (needs-reply / needs-action / fyi / noise)
- `mavis-tools/taxonomy.js` — sursa unică pentru numele etichetelor de categorie (rezolvate live, nu hardcodate)

---

*Generat de Mavis Cloud. Nimic nu a fost șters, nimic nu a fost trimis, nimic nu a fost modificat în Gmail sau Drive. Totul e anulabil.*
