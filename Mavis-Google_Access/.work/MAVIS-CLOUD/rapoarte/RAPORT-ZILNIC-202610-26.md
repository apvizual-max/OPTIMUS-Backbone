# Raport zilnic — luni 26 octombrie 2026

> Generat de Mavis Cloud · 10 mesaje noi măsurate azi (00:00–09:12 EEST) · 65 joburi analizate
> Cota Google: **106 cereri** (plafon 200 — **în limita plafonului**). Zero scrieri pe Gmail; tot consumul a fost măsurare și diagnostic. Detaliu în §5.

---

## 1. Gmail — etichetele `MAVIS/*`

### 1.1 Rezultatul scurt

**Pe etichetele `MAVIS/*` a intrat azi: 0 mesaje.** Nici în ultimele 24h (0), nici în ultimele 7 zile (0).

Nu pentru că n-a venit mail. Azi au intrat **10 mesaje** în total, iar în inbox sunt **10**. **10 dintre ele nu au primit nicio etichetă**.

### 1.2 Măsurătoarea pe etichete (numărare exactă, cu paginare)

| Etichetă | azi | 24h | 7z | 30z | Ultimul mesaj etichetat |
|---|---|---|---|---|---|
| `MAVIS/Joburi` | 0 | 0 | 0 | 362 | Sun, 11 Oct 2026 |
| `MAVIS/AI si comunitati` | 0 | 0 | 0 | 134 | Sun, 11 Oct 2026 |
| `MAVIS/Social` | 0 | 0 | 0 | 222 | Sun, 11 Oct 2026 |
| `MAVIS/Newsletter` | 0 | 0 | 0 | 251 | Sun, 11 Oct 2026 |
| `MAVIS/Finante` | 0 | 0 | 0 | 6 | Tue, 6 Oct 2026  |
| `MAVIS/Personal` | 0 | 0 | 0 | 0 | n/a |
| `MAVIS/De raspuns` | 0 | 0 | 0 | 38 | Fri, 9 Oct 2026  |
| `MAVIS/Facturi si conturi` | 0 | 0 | 0 | 2 | Fri, 09 Oct 2026 |

**Concluzie:** etichetarea automată e oprită de **14 zile** (pe `MAVIS/Finante` = **06.10.2026**; pe `MAVIS/De raspuns`, `MAVIS/Facturi si conturi` = **09.10.2026**; pe `MAVIS/Joburi`, `MAVIS/AI si comunitati`, `MAVIS/Social`, `MAVIS/Newsletter` = **11.10.2026**).

> Zero pe o fereastră nu înseamnă "etichetă goală" — înseamnă "eticheta nu mai primește nimic". Verificat pe 4 ferestre.

### 1.3 Defectul, măsurat azi

Filtrele `MAVIS/*` există: **5** filtre cu criteriu de interogare, din 18 total pe cont. **0** dintre ele are `addLabelIds`, iar **0** atinge o etichetă `MAVIS/*`. Criteriul celui de joburi, citit live azi:

```
from:(jooble bestjobs hipo indeed jobleads linkedin) OR subject:(job angajare vacanta oportunitate)
```

**Cauza reală, măsurată azi pe Gmail:** în căutarea Gmail, `()` înseamnă **ȘI**, iar `{}` înseamnă **SAU**. Cele 5 filtre folosesc `from:(jooble bestjobs ...)` — deci cer un expeditor care să conțină **toate** cuvintele simultan. Rezultat: **0 mesaje lovite în 30 de zile, din oricare categorie.**

| Filtru | cum e scris acum | cum ar trebui scris (`{}`) |
|---|---|---|
| `from:(jooble bestjobs hipo indeed jobleads linkedin) OR su…` | **0** | **1087** |
| `from:(substack goatacademy aiautomationsociety sadhguru be…` | **0** | **380** |
| `from:(skool facebook instagram pinterest tiktok polibrawl)` | **0** | **153** |
| `from:(noreply no-reply newsletter digest mail@ info@ news@…` | **0** | **1253** |
| `from:(kraken tradingview bitunix coinbase binance) OR subj…` | **0** | **36** |

Cu acoladele, aceleași filtre ar fi prins **2909 mesaje în 30 de zile**. Diferența dintre 0 și 2909 e cauza pentru care etichetele sunt goale de două săptămâni.

**Două defecte, în ordine:**
1. **Criteriile nu pot lovi nimic** — paranteze în loc de acolade. (defect descoperit și măsurat azi)
2. **`addLabelIds` e vid** — nici măcar cu criterii corecte n-ar eticheta ceva. (defect cunoscut din 11.10)

**De ce nu le-am reparat azi:** tokenul din cloud are `gmail.modify`, dar **nu** `gmail.settings.basic` — fără acest scope, `filters PATCH` răspunde 403. Repararea e pregătită ca script (`mavis-tools/fix-mavis-filters.js`, cu `--dry-run` și cu salvarea stării de dinainte pentru rollback) și trebuie rulată de pe mașina ta, unde scope-ul există.

**Și mai mult:** filtrul nici măcar nu arhivează. Deși `removeLabelIds` conține `INBOX`, mesajele de job intrate azi sunt **în continuare în INBOX și UNREAD**:

| Fereastră | În inbox | În toate stările |
|---|---|---|
| azi | 10 | 10 |
| 24h | 143 | 144 |
| 7z | 874 | 1162 |

**~874 mesaje stau în inbox într-o săptămână** (~125/zi). Sortarea nu mai are loc.

**Cauza probabilă** (neconfirmată): etichetarea se făcea de un script local — `mavis-tools/email-sort-full.js` — care rulează pe calculatorul tău, nu din cloud. Filtrele din Gmail doar arhivează; **eticheta e pusă de script**. Scriptul nu mai rulează.

### 1.4 Cum ar fi fost sortate mesajele de azi

Simulare pe cele 10 mesaje de azi, cu **aceleași criterii** ale filtrelor (fără scriere):

| Categorie | Mesaje azi |
|---|---|
| `MAVIS/Joburi` | 6 |
| `MAVIS/Newsletter` | 3 |
| `MAVIS/AI si comunitati` | 0 |
| `MAVIS/Social` | 1 |
| `MAVIS/Finante` | 0 |
| *niciun filtru se potrivește* | 2 |

> Unele mesaje se potrivesc la 2 filtre (ex. "Joburi" + "Newsletter" de la LinkedIn), deci suma poate depăși 10.

**Observație:** din cele 2 mesaje fără filtru, **0 sunt notificări ale agenților tăi** (Jules și GitHub Actions pe repo-urile proprii). Taxonomia MAVIS nu are categorie pentru "notificări din pipeline-ul propriu". **Recomandare: etichetă nouă, ex. `MAVIS/Agenti`.**

### 1.5 Mesajele care chiar necesită răspuns

Clasificarea e făcută din date, nu dintr-o listă scrisă cu mâna: 0 cer răspuns explicit, 3 cer o decizie, 3 sunt alerte de job care nu ating profilul tău, 4 sunt newsletter/promoție, 0 sunt zgomot de pipeline.

**Niciun mesaj nu cere explicit un răspuns.**

**Ceres o decizie (alerte de job care bat cu profilul tău):**

- **LinkedIn Job Alerts** — 05:50 UTC. *Concentrix Experience Design Manager* — Concentrix Experience Design Manager: Job TitleExperience Design ManagerJob… ͏ ͏ ͏ ͏ ͏ ͏ ͏ ͏ ͏ ͏ ͏ ͏ ͏ ͏ ͏ ͏ ͏ ͏ ͏ ͏ ͏ ͏ ͏ ͏ ͏ ͏ ͏ ͏ ͏ ͏ ͏ ͏ ͏ ͏ ͏ ͏ ͏ ͏ ͏ ͏ ͏ ͏
- **Bestjobs** — 05:43 UTC. *AGRESIV MEDIA is hiring Colaboratori design grafic creatie si grafica* — Top jobs according to your activity: CV entries, job applications and job searches. BestJobs Hi there, Alexandru Popescu! Bestie, your career friend, is on What
- **Bestjobs** — 05:22 UTC. *13 graphic design, bucharest jobs available on bestjobs* — Top jobs according to your activity: CV entries, job applications and job searches. BestJobs Hi there, Alexandru Popescu! Bestie, your career friend, is on What

**Alerte de job care NU ating profilul de design** (informativ, 3):

- Jooble — 04:54 UTC · *Travel Planner caută Full-Stack Engineer (Laravel + Vue.js), UX-focused, Customer-Facing Web și 100 mai multe oferte noi de muncă*
- Indeed — 02:40 UTC · *IT - Internship la Provident Romania. Încă 18 locuri de muncă în București, Ilfov*
- Jooble — 00:08 UTC · *🔔 Toennies company caută Lucrător la ambalare și 84 mai multe oferte noi de muncă*

**Newsletter / promoție, fără acțiune** (4): MagazinulGospodarului™, Ollama, Numerologist, AI Money Lab (Skool)

**Leads verificate din alertele de job** (pagina sursă citită direct, nu din snippet de motor de căutare):

##### UX/UI Designer (Contract, AI training) — micro1

Din alerta **Bestjobs** — *13 graphic design, bucharest jobs available on bestjobs*

micro1 angajează UX/UI Designeri ca CONTRACTORI pentru antrenarea modelelor AI pe task-uri de adnotare video (brațe robotice). Postarea apare în lista Bestjobs de azi cu 3000 EUR, dar pe pagina oficială micro1 plata e în USD pe oră. Se încadrează direct pe Traseul 2 (bani din proiecte + AI) — nu e un job de angajare clasic.

**Cerințe:**

- Experiență în UX și/sau UI design (obligatoriu)
- Atenție foarte bună la detalii
- Scris în engleză — comunicare excelentă
- Bună înrindere și time management în mediu 100% remote
- Experiență anterioară în video annotation / data labeling = plus, nu obligatoriu
- Background acceptat și în: web design, video/muzică editare, fotografie, filmare, producție audiovisuală, robotică, inginerie

**Rate-uri publicate:**

- $50 – $90 / oră (pe pagina oficială micro1)
- 3000 (EUR) — cât apare în lista Bestjobs

**Condiții:** Contractor, 100% remote. Eligibil din Europa (și America de Nord, America Latină, UK, Oceania). 3000 de locuri deschise.

**Cum se aplică:** Aplicare direct pe jobs.micro1.ai → assessment scurt → onboarding în fluxul de review. Fără experiență anterioară în AI — micro1 face onboarding-ul.

> ⚠️ Pagina oficială micro1 spune „Europe, UK, Oceania" — România se încadrează, dar confirmă la aplicare că proiectul nu are excluderi de țară. E tot același micro1 găsit pe 25.10 ca YO AI Labs, dar acum cu jobul de design identificat direct.

- https://jobs.micro1.ai/post/d02122f3-eaec-42b2-ad3f-edc218b94294

##### Digital Content Designer (DTC, Amazon & Online Retail) (Remote) — Concentrix

Din alerta **Bestjobs** — *13 graphic design, bucharest jobs available on bestjobs*

Rol NOU, verificat azi: Concentrix angajează un Digital Content Designer pentru eCommerce DTC (Amazon A+ Content, Brand Store, imagini de produs) — 100% remote, eligibil din România (RON Work-at-Home). Concentrix are 27 de joburi deschise în București pe Indeed, inclusiv acesta.

**Cerințe:**

- Portofoliu puternic în design digital și eCommerce
- Figma, Adobe Photoshop, Adobe Illustrator — nivel avansat
- Experiență cu conținut digital orientat pe conversie, în mediu DTC eCommerce
- Cunoașterea customer journey, UX și best practices de design digital
- Tografie, layout, compoziție și ierarhie vizuală — solide
- Experiență cu design systems și brand guidelines
- Engleză C1; MS Office / Google Workspace; platforme DAM
- Bonus: Amazon A+ Content, Brand Stores, imagini PDP, CMS, WCAG/ADA, After Effects, unelte creative cu AI

**Rate-uri publicate:**

- Salariu neprecizat de concentrix (competitive package)

**Condiții:** Full-time, RON Work-at-Home (remote din România). Deplasări în Bulgaria ~1 zi/lună sau 2 zile/trimestru, cheltuieli parțial rambursate. Postat pe 8 octombrie 2026.

**Cum se aplică:** Aplicare exclusiv prin Workday: cnx.wd1.myworkdayjobs.com/external_global/job/RON-Work--at--Home/Digital-Content-Designer--DTC--Amazon---Online-Retail---Remote-_R1770996

> ⚠️ Există și o versiune a aceluiași job cu sediul în Sofia, Bulgaria, care cere domiciu în Bulgaria — NU aplica acolo, ci varianta RON. Verificat pe jobgether și pe remowork.life.

- https://jobgether.com/offer/6ac7efa4480485773197d131-digital-content-designer-dtc-amazon-online-retail-remote

##### Senior Art Director — Leo Burnett Bucharest

Din alerta **Bestjobs** — *13 graphic design, bucharest jobs available on bestjobs*

Leo Burnett Romania (una dintre cele maiAnything prestigious agenții din piață, 5x „The Creative Agency of the Year") angajează Senior Art Director, listat pe LinkedIn, BeBee și Bestjobs. Rolul e la nivel de agenție de top, cu direcție vizuală pe TV, digital, print și OOH.

**Cerințe:**

- Portofoliu care arată versalitate, craft și gândire conceptuală
- Minimum 5 ani de experiență în mediu de agenție
- Adobe Creative Suite (Photoshop, Illustrator, InDesign) — Figma e plus
- Capacitate de a lucra sub presiune, la termene, și de a primi feedback cu eleganță
- Direcție vizuală pe TV, digital, print, OOH
- Colaborare cu copywriteri, strategi și echipe de account

**Rate-uri publicate:**

- Salariu neprecizat

**Condiții:** București, Hybrid / On-site. Full-time. Postat cu 4–6 zile în urmă.

**Cum se aplică:** Portofoliu + CV prin formularul oficial (easy apply pe BeBee / site-ul de cariere Publicis Groupe).

> ⚠️ Termenul afișat de BeBee e „Până la 09.08.2026" — o dată în trecut față de postarea recentă, deci e un termen de agregator, nu de angajator. Verifică pe formularul oficial. Anunțul e listat activ pe LinkedIn Jobs la data raportului.

- https://bebee.com/ro/jobs/senior-art-director-leo-bucharest-bucharest--theirstack-693146002

##### Proiectant Producție Publicitară — BD Lemntech (disponibil imediat)

Din alerta **Bestjobs** — *13 graphic design, bucharest jobs available on bestjobs*

BD Lemntech (producție de mobilier comercial și publicitară, lider regional) angajează Proiectant Producție Publicitară, marcat „DISPONIBIL IMEDIAT" — cel mai mare interval salarial din lista de azi și unul dintre puținele roluri de producție graphică de nivel înalt.

**Cerințe:**

- Proiectare graphică pentru producție publicitară (POSM, print, mobilier)
- Cunoștințe de pregătire de fișiere pentru tipărire
- Experiență similară în producție publicitară sau mobilier

**Rate-uri publicate:**

- 1405 – 2000 EUR/lună

**Condiții:** Popești-Leordeni / București. Se acceptă aplicație imediată.

**Cum se aplică:** Direct pe anunțul Bestjobs; compania are și pagină de cariere proprie (bdlemntech.ro/cariere).

> ⚠️ Locația e Popești-Leordeni, adică în afara Bucureștiului, dar anunțul listat include și „București, România" — merită confirmat în reply dacă e on-site în Popești sau cu deplasare în oraș.

- https://www.bdlemntech.ro/en/cariere/

##### AI Video Editor (Meta & AppLovin Performance Ads) — Apex Digital Alliance

Din alerta **Bestjobs** — *13 graphic design, bucharest jobs available on bestjobs*

Apex Digital Alliance (agenție de performance ads, 11–50 angajați, HQ pe Glădiței 42) angajează AI Video Editor pentru Meta și AppLovin. Batează cu Traseul 2: design + performance + AI, cu interval salarial bun.

**Cerințe:**

- Editare video pentru performance ads (Meta, AppLovin)
- Folosirea de unelte AI în producția video
- Experiență în agenție de performance marketing

**Rate-uri publicate:**

- 1200 – 1300 EUR/lună

**Condiții:** București, Strada Glădiței 42 (Clădire T6, etaj/demarcare). Hybrid, cu un alt rolJunior Media Buyer la același angajator (700–1200 EUR).

**Cum se aplică:** Direct pe anunțul Bestjobs. Compania are un profil public pe LinkedIn.

> ⚠️ Rolul e de editare video cu AI, mai aproape de motion/content decât de design static — îți convine dacă ai profilul de motion.

- https://www.linkedin.com/company/apex-digital-alliance1

##### Colaboratori design grafic, creație și grafică — AGRESIV MEDIA (REAPARIȚIT, cu salariu)

Din alerta **Bestjobs** — *AGRESIV MEDIA is hiring Colaboratori design grafic creatie si grafica*

Același anunț ca pe 25.10, dar azi am citit corpul COMPLET al emailului (ieri s-a văzut doar snippet-ul) — și Bestjobs publică în corp **salariul 780 – 1020 EUR** și **București, România**. Ieri raportul spunea că anunțul nu publică orașul și salariul; era corect pentru snippet, greșit pentru anunț.

**Cerințe:**

- Design grafic și creație publicitară (logo/siglă, cărți de vizită, pliante, brosuri, materiale de prezentare)
- Grafica vectorială, webdesign, bannere web, prezentări interactive
- Producție grafică: print offset și digital, signalistică, panouri, totemuri

**Rate-uri publicate:**

- 780 – 1020 EUR (salariu publicat de Bestjobs pentru acest rol)

**Condiții:** București, România. Agenție fullservice de publicitate, print și branding, activă din 2003, sediul în Sector 2 (Str. Zambilelor 62-64, zona Lacul Tei).

**Cum se aplică:** Direct pe anunțul Bestjobs sau contact direct: office@agresivmedia.ro / 0724.331.791.

> ⚠️ Salariul apare acum, dar tipul de colaborare (angajare vs. colaborator/freelance) nu e precizat. Anunțul e real și verificabil — de aceea merită un reply, cu întrebarea despre tipul de contract.

- https://www.bestjobs.eu/en/job/colaboratori-design-grafic-creatie-si-grafica

---
## 2. Joburi — scorate cu `ALEX-KIT/scoring.gs`

**65 joburi analizate** (IQads 42 + designproject.io 23) → 34 păstrate în tabele, 31 drop-uri, din care **12 cu verdict amânat** (locația nu e publicată de sursă). **0 joburi noi** față de 2026-10-25.

Surse: **IQads** (tabloul AdJob activ, citit azi) + **designproject.io** (România + București).

> ⛔ **Expirate marcate în tabele.** La IQads data de expirare vine direct din anunț. La designproject.io `validThrough` = data postării + 30 zile — măsurat pe toate cele 23 de joburi (23 exacte, 0 cu o zi de fus orar, 0 altfel), deci e o expirare reală, nu o derivare inutilă. 9 joburi din tabele au expirat și nu se mai pot aplica.

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
| **9.4** | [DTC] | 10/8/10/10 | AI Research Lab UI/UX & Brand Designer (100 % remote) (m/f/d) | EWOR GmbH | Bucharest, Romania, Remote Solely | Full Time | postat 2026-09-25 · expiră 2026-10-25 ⛔ **EXPIRAT** |
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
| **8.4** | [DTC] | 8/8/10/8 | Freelance Brand Designer | Mindrift | Romania, Fully Remote | Part Time, Contract | postat 2026-09-25 · expiră 2026-10-25 ⛔ **EXPIRAT** |
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

### 2.6 Drop-uri (circuit breaker) — 31

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
| 4 | **9.4** | AI Research Lab UI/UX & Brand Designer (100 % remote) (m/f/d) | EWOR GmbH | Bucharest, Romania, Remote Solely | Full Time | ⛔ da | remote |
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

1. **Etichetele MAVIS/* nu mai primesc nimic de 14 zile.** Două cauze, măsurate azi: filtrele folosesc `from:(...)` unde Gmail cere `from:{...}` (paranteze = ȘI, acolade = SAU), deci nu pot lovi niciun mesaj — ar fi prins 2909 mesaje în 30 de zile; și `addLabelIds` e vid pe toate. ~874 mesaje/7 zile stau în inbox.
2. **designproject.io servește descrieri foarte inegale** (363–31446 de caractere pe cele 23 de joburi, măsurat azi). Cele mai lungi sunt rescrise de AI și injectează cuvinte-cheie care ridică axele — vezi §6.2.
3. **Celelalte două câmpuri de engagement ale designproject.io sunt inutilizabile.** `employmentType` din JSON-LD spune `FULL_TIME` pentru 23 din 23, iar badge-ul din listing spune "Full-time" pentru 23 din 23. Singura sură corectă e linia **"Job Type:"** din descriere — prezentă la 23 din 23. Am folosit asta.
4. **Paginatia IQads nu funcționează.** `?page=2` și `?page=3` servesc exact pagina 0 (aceleași 42 de linkuri — verificat azi pe 0, 2, 3). Catalogul complet e pe pagina 0 — nu iterez pagini.
5. **Cota Google: 106 cereri pe 200** (în limita plafonului). Consumul pe etape:

| Etapă | Cereri |
|---|---|
| `report-mail-count.js` | 59 |
| `report-filter-state.js` | 16 |
| `report-simulate-sort.js` | 11 |
| `report-inbox-counts.js` | 9 |
| `report-folder-discover.js` | 4 |
| `inline` | 4 |
| **total** | **106** |

> Rulare 2026-10-26 (raport zilnic). Contor pornit de la zero.

Ce a consumat cel mai mult: corpurile complete ale mesajelor de azi (10) — fără corp, nu se poate distinge un mesaj care cere răspuns de o alertă automată. **Zero scrieri pe Gmail** — niciun mail trimis, marcat sau arhivat, niciun filtru modificat.

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

- `rapoarte/RAPORT-ZILNIC-202610-26.md` — raportul acesta (și în repo)
- `mavis-tools/scoring-result-2026-10-26.json` — scoruri + secțiuni + diagnostice
- `mavis-tools/jobs-iqads-2026-10-26.json` — joburi IQads, text integral
- `mavis-tools/jobs-designproject-2026-10-26.json` — joburi designproject.io, JSON-LD
- `mavis-tools/jobs-2026-10-25.json` — setul normalizat de ieri (cu care s-a comparat)
- `mavis-tools/report-mail-count.json` — numărătoare pe etichete MAVIS/*
- `mavis-tools/report-inbox-counts.json` — numărătoare exactă inbox
- `mavis-tools/report-simulate-sort.json` — simularea sortării + mesajele de azi
- `mavis-tools/report-source-probe.json` — sonda de surse (comportamentul iqads.ro / designproject.io, măsurat azi)
- `mavis-tools/report-filter-state.json` — starea filtrelor Gmail MAVIS/* + testul paranteze-vs-acolade (măsurat azi)
- `mavis-tools/report-triage.js` — clasificatorul mesajelor (needs-reply / needs-action / fyi / noise)

---

*Generat de Mavis Cloud. Nimic nu a fost șters, nimic nu a fost trimis, nimic nu a fost modificat în Gmail sau Drive. Totul e anulabil.*
