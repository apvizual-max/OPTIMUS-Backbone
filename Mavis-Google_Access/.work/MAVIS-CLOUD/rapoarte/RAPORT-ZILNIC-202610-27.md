# Raport zilnic — marți 27 octombrie 2026

> Generat de Mavis Cloud · 21 mesaje noi măsurate azi (00:00–09:15 EEST) · 62 joburi analizate
> Cota Google: **209 cereri** (plafon 200 — **depășit cu 9**). Zero scrieri pe Gmail; tot consumul a fost măsurare și diagnostic. Detaliu în §5.

---

## 1. Gmail — etichetele de categorie

### 1.1 Rezultatul scurt

**Pe etichetele de categorie a intrat azi: 8 mesaje.** În ultimele 24h: 201; în 7 zile: 582.

Azi au intrat **21 mesaje** în total, iar în inbox sunt **17**. **13 dintre ele nu au primit nicio etichetă de categorie**. Cele 8 **au fost** etichetate ca zgomot de pipeline (bot-uri de pe repo-urile tale) — deci cele 13 rămase sunt mesaje reale, fără etichetă de categorie.

### 1.2 Măsurătoarea pe etichete (numărare exactă, cu paginare)

| Etichetă | azi | 24h | 7z | 30z | Ultimul mesaj etichetat |
|---|---|---|---|---|---|
| `MAVIS/Joburi` | 0 | 0 | 0 | 333 | Sun, 11 Oct 2026 |
| `AI Folder/AI si Comunitati` | 0 | 0 | 0 | 115 | Sun, 11 Oct 2026 |
| `Socials` | 0 | 0 | 0 | 216 | Sun, 11 Oct 2026 |
| `Newsletter` | 0 | 0 | 0 | 235 | Sun, 11 Oct 2026 |
| `Finante` | 0 | 0 | 0 | 5 | Tue, 6 Oct 2026  |
| `Personal` | 0 | 0 | 0 | 0 | n/a |
| `De raspuns` | 0 | 0 | 0 | 30 | Fri, 9 Oct 2026  |
| `Facturi si Conturi` | 0 | 0 | 0 | 2 | Fri, 09 Oct 2026 |
| `Optimus CD` | 8 | 201 | 582 | 638 | Mon, 26 Oct 2026 |

**Concluzie:** o categorie primește mesaje (`Optimus CD`); 8 categorii sunt moarte de **15 zile** (pe `Finante` = **06.10.2026**; pe `De raspuns`, `Facturi si Conturi` = **09.10.2026**; pe `MAVIS/Joburi`, `AI Folder/AI si Comunitati`, `Socials`, `Newsletter` = **11.10.2026**).

> Zero pe o fereastră nu înseamnă "etichetă goală" — înseamnă "eticheta nu mai primește nimic". Verificat pe 4 ferestre.

### 1.3 Filtrele, măsurate azi

Filtre cu criteriu de interogare pe cont: **6**, din 19 total. **1** dintre ele are `addLabelIds`, iar **1** atinge o etichetă de categorie. Criteriul celui de joburi, citit live azi:

```
from:(jooble bestjobs hipo indeed jobleads linkedin) OR subject:(job angajare vacanta oportunitate)
```

#### Un filtru FUNCȚIONEAZĂ

**1 dintre 6 filtre lovesc efectiv mesaje.** `from:(notifications@github.com OR *jules*) OR subj…` → **917** mesaje în 30 de zile, etichetează `agenti`


**Cauza reală, măsurată azi pe Gmail:** în căutarea Gmail, `()` înseamnă **ȘI**, iar `{}` înseamnă **SAU**. Cele 5 filtre nefuncționale folosesc `from:(jooble bestjobs ...)` — deci cer un expeditor care să conțină **toate** cuvintele simultan. Rezultat: **0 mesaje lovite în 30 de zile.**

| Filtru | cum e scris acum | cum ar trebui scris (`{}`) |
|---|---|---|
| `from:(jooble bestjobs hipo indeed jobleads linkedin) OR su…` | **0** | **1086** |
| `from:(substack goatacademy aiautomationsociety sadhguru be…` | **0** | **379** |
| `from:(skool facebook instagram pinterest tiktok polibrawl)` | **0** | **151** |
| `from:(noreply no-reply newsletter digest mail@ info@ news@…` | **0** | **1198** |
| `from:(kraken tradingview bitunix coinbase binance) OR subj…` | **0** | **6** |

Cu acoladele, aceleași filtre ar fi prins **3737 mesaje în 30 de zile**.

**Două defecte, în ordine:**
1. **Criteriile nu pot lovi nimic** — paranteze în loc de acolade.
2. **`addLabelIds` e vid** — nici măcar cu criterii corecte n-ar eticheta ceva.

**De ce nu le-am reparat azi:** tokenul din cloud are `gmail.modify`, dar **nu** `gmail.settings.basic` — fără acest scope, `filters PATCH` răspunde 403. Repararea e pregătită ca script (`mavis-tools/fix-mavis-filters.js`, cu `--dry-run` și cu salvarea stării de dinainte pentru rollback) și trebuie rulată de pe mașina ta, unde scope-ul există.

**Inboxul nu se golește.** Deși `removeLabelIds` conține `INBOX`, mesajele intrate azi sunt **în continuare în INBOX și UNREAD**:

| Fereastră | În inbox | În toate stările |
|---|---|---|
| azi | 17 | 21 |
| 24h | 130 | 261 |
| 7z | 635 | 1322 |

**~635 mesaje stau în inbox într-o săptămână** (~91/zi).

### 1.4 Cum ar fi fost sortate mesajele de azi

Simulare pe cele 22 mesaje de azi, cu **aceleași criterii** ale filtrelor (fără scriere):

| Categorie | Mesaje azi |
|---|---|
| `MAVIS/Joburi` | 7 |
| `AI Folder/AI si Comunitati` | 2 |
| `Socials` | 2 |
| `Newsletter` | 3 |
| `Finante` | 0 |
| `Personal` | 0 |
| `De raspuns` | 0 |
| `Facturi si Conturi` | 0 |
| `Optimus CD` | 8 |
| *niciun filtru se potrivește* | 3 |

> Unele mesaje se potrivesc la 2 filtre (ex. "Joburi" + "Newsletter" de la LinkedIn), deci suma poate depăși 22.

**Observație:** **8 mesaje** de azi sunt notificări ale agenților tăi (Jules și GitHub Actions pe repo-urile proprii). Până azi taxonomia nu avea categorie pentru ele — **acum are**: eticheta `Optimus CD` primește 8 mesaje azi, iar filtrul ei funcționează efectiv. E singura categorie care primește ceva — restul sunt în continuare moarte.


### 1.5 Mesajele care chiar necesită răspuns

Clasificarea e făcută din date, nu dintr-o listă scrisă cu mâna: 0 cer răspuns explicit, 2 cer o decizie, 5 sunt alerte de job care nu ating profilul tău, 7 sunt newsletter/promoție, 8 sunt zgomot de pipeline.

**Niciun mesaj nu cere explicit un răspuns.**

**Ceres o decizie (alerte de job care bat cu profilul tău):**

- **Bestjobs** — 05:06 UTC. *13 graphic design, bucharest jobs available on bestjobs* — Top jobs according to your activity: CV entries, job applications and job searches. BestJobs Hi there, Alexandru Popescu! Bestie, your career friend, is on What
- **Jooble** — 04:52 UTC. *LUCA caută Graphic Designer @ LUCA și 101 mai multe oferte noi de muncă* — Jooble Anunțurile dvs. zilnice de oferte de muncă pentru 27 octombrie, 2026 Verificați ofertele noi de muncă pe care le-am găsit pentru dvs. astăzi. Afișați toa

**Alerte de job care NU ating profilul de design** (informativ, 5):

- LinkedIn Job Alerts — 05:50 UTC · *Mid-Level Thumbnail Designer job at There's An AI For That - 1 connection*
- Bestjobs — 05:18 UTC · *These employers are looking for people like you*
- Indeed — 05:07 UTC · *Administrator Clădiri & Responsabil Parc Auto la Sartorom. Încă 7 locuri de muncă în București, Ilfov*
- Jooble — 05:06 UTC · *Informații despre newsletter - Hippo recruitment și altele*
- Jooble — 00:08 UTC · *🔔 Intra Interim caută Camerista - Franta și 84 mai multe oferte noi de muncă*

**Newsletter / promoție, fără acțiune** (7): TikTok, PhiMolds, Felix & Winston 🐶, David, AI Money Lab (Skool), Render, body-store.ro

**Leads verificate din alertele de job** (pagina sursă citită direct, nu din snippet de motor de căutare):

##### Mid-Level Thumbnail Designer — There's An AI For That

Din alerta **LinkedIn Job Alerts** — *Mid-Level Thumbnail Designer job at There's An AI For That - 1 connection*

Lead NOU, verificat azi pe portalul de cariere oficial: platformă AI cu 54K+ abonați pe YouTube, angajează Thumbnail Designer full-time ON-SITE în București (Calea Victoriei). Contract de muncă permanent, 5.000–7.000 RON net/lună în funcție de experiență, portofoliu și testul practic. Se aplică cu link de portofoliu + test de design practic.

**Cerințe:**

- Minimum 2 ani de experiență în design de thumbnail-uri, design grafic sau rol creativ similar
- Adobe Photoshop foarte bun — în special manipulare foto, compoziție, retuș
- Instinct vizual puternic; compoziție, iluminare, contrast, culoare, tipografie, ierarhie vizuală
- Ridicare la standard, originalitate, viteza în producție fără să sacrifice calitatea
- Cunoaștințe de unelte AI creative (Midjourney, ChatGPT Image Generation) — sau rapiditate în a le învăța
- Engleză bună (brief-uri și cercetare de trenduri YouTube)
- Portofoliu relevant OBLIGATORIU + test practic de design în procesul de recrutare

**Rate-uri publicate:**

- 5.000 – 7.000 RON net/lună (publicat de angajator)
- ~$21.600 – $30.300 anual (echivalent, cum apare pe jobboard-urile de YouTube)

**Condiții:** București, Calea Victoriei — full-time, ON-SITE (nu remote). Contract de muncă permanent. Asigurare medicală privată Regina Maria după primele 3 luni, prânz zilnic asigurat de firmă.

**Cum se aplică:** Aplicare pe portalul oficial cu link de portofoliu în formular, apoi test practic de design. Contact: Adriana, HR Specialist. Postarea e pe LinkedIn ca alertă de job și listată activ pe portalul de cariere.

> ⚠️ E on-site, nu remote — nu se încadrează dacă vrei 100% remote. Portofoliul trebuie să conțină ceva relevant pentru thumbnail-uri/YouTube; un portofoliu de brand identity clasic nu arată la fel de puternic aici. Testul practic de design contează.

- https://careers.theresanaiforthat.com/jobs/8541446-mid-level-thumbnail-designer

##### Art Director — Mercury360 (IQads #23999)

Din alerta **IQads (scraping direct)** — *Art Director @ Mercury360 — postare nouă, ID 23999*

PRIMA postare GENUIN NOUă de la ultima rulare (IQads #23999, max ID anterior 23997). Agentie de advertising din București, scor 9.6 — al doilea din toate tabelele, și cel mai bine potrivit din categoria 'design efectiv' (titlu de rol, nu prosa). Hybrid în București, full-time, expiră 25 decembrie.

**Cerințe:**

- Minimum 7 ani de experiență în advertising
- Portofoliu relevant în ATL, Digital sau BTL
- Adobe Photoshop, Illustrator, Premiere și After Effects
- Motion design și editare video — obligatorii, fiindcă multe proiecte sunt video-first
- Folosirea uneltelor AI pentru cercetare, schițe sau retuș — un plus

**Rate-uri publicate:**

- Salariu neprecizat (anunțul nu îl publică)

**Condiții:** București, program hybrid. Full Time, nivel Senior. Specializări: Art, ATL, BTL, Digital, Marketing. Beneficii: asigurare medicală privată, Bookster, cafea gratuită. Valabil până pe 25.12.2026.

**Cum se aplică:** Prin linkul „Aplica la acest job" de pe anunț: https://www.iqads.ro/adjob/23999/aplica — portofoliu obligatoriu, CV opțional.

> ⚠️ Cerința de 7 ani e cea mai strictă dintre rolurile de azi, iar motion design e cerință explicită, nu opțională. Dacă portofoliul tău nu are video/motion, e un prag real de evaluat înainte să aplici.

- https://www.iqads.ro/adjob/23999/art-director-mercury360

##### Brand Executive — Imperial Brands (REAPARIȚIT, cu salariu estimat)

Din alerta **Bestjobs** — *These employers are looking for people like you*

Apare azi în lista Bestjobs cu 20 de roluri (email nou, diferit de alertele de job din 26.10). Brand Executive la Imperial Brands (FMCG tutun) — departamentul Consumer Marketing, cu accent pe branduri premium. Bestjobs publică salariul ca „confidential", dar listează o estimare pentru poziții similare: 1345–1485 EUR/lună.

**Cerințe:**

- Experiență în marketing, preferabil FMCG sau produse de lux
- Management de proiecte și organizare — mai multe inițiative în paralel
- Stakeholder management și colaborare puternică
- „Eye for premium" — capacitatea de a recunoaște, proteja și ridica calitatea execuției
- Română și engleză fluente (scris și vorbit)
- Cunoștințe de digital marketing — un avantaj

**Rate-uri publicate:**

- Salariu confidential, dar Bestjobs estimează 1345 – 1485 EUR/lună pentru poziții similare

**Condiții:** București. Full-time, parte din Consumer Marketing Team, raportează la Marketing Manager Combustibles.

**Cum se aplică:** Direct pe anunțul Bestjobs; contact zilnic cu agențiile de creație, media și activare.

> ⚠️ E un rol de brand management, nu de design propriu-zis — tu coordonezi agențiile, nu produci vizualele. Batează mai degrabă cu Traseul 1 (loc de muncă) decât cu portofoliul de design. Merită verificat dacă alegi să treci pe coordonare.

- https://www.bestjobs.eu/en/job/brand-executive-16

##### Colaboratori design grafic, creație și grafică — AGRESIV MEDIA (REAPARIȚIT)

Din alerta **Bestjobs** — *AGRESIV MEDIA is hiring Colaboratori design grafic creatie si grafica / These employers are looking for people like you*

Al patrulea email care conține acest rol, după cele trei de ieri. Salariul 780–1020 EUR e publicat de Bestjobs, iar orașul e București — date confirmate și azi, direct din corpul emailului. Poziția rămâne reală, la nivel de companie.

**Cerințe:**

- Design grafic și creație publicitară (logo/siglă, cărți de vizită, pliante, brosuri, materiale de prezentare)
- Grafica vectorială, webdesign, bannere web, prezentări interactive
- Producție grafică: print offset și digital, signalistică, panouri, totemuri

**Rate-uri publicate:**

- 780 – 1020 EUR (salariu publicat de Bestjobs, reconfirmat azi)

**Condiții:** București, România. Agenție fullservice de publicitate, print și branding, activă din 2003, sediul în Sector 2 (Str. Zambilelor 62-64, zona Lacul Tei).

**Cum se aplică:** Direct pe anunțul Bestjobs sau contact: office@agresivmedia.ro / 0724.331.791.

> ⚠️ Tipul de colaborare (angajare vs. colaborator/freelance) nu e precizat — întreabă în primul reply. E același anunț ca în 26.10, 25.10 și 24.10: 4 zile la rând, deci e stabil, nu o noutate de azi.

- https://www.bestjobs.eu/en/job/colaboratori-design-grafic-creatie-si-grafica

##### UX/UI Designer (Contract, AI training) — micro1 (REAPARIȚIT)

Din alerta **Bestjobs** — *13 graphic design, bucharest jobs available on bestjobs*

Apare din nou în lista de azi la „3000 EUR". Verificat ieri pe pagina oficială micro1 și pe aiannotationjobs.com: $50–90/oră, contractor, remote, eligibil Europa, 3.000 openings, fără experiență anterioară în AI. Aceleași joburi apar și ca „Xperteez Technology" pe designproject.io.

**Cerințe:**

- Experiență în UX și/sau UI design (obligatoriu)
- Atenție foarte bună la detalii
- Scris în engleză — comunicare excelentă
- Bună înrindere și time management în mediu 100% remote
- Experiență în video annotation / data labeling = plus, nu obligatoriu
- Background acceptat și în: web design, editare video/foto, filmare, producție audiovisuală, robotică, inginerie

**Rate-uri publicate:**

- $50 – $90 / oră (pe pagina oficială micro1)
- 3000 EUR — cât apare în lista Bestjobs

**Condiții:** Contractor, 100% remote. Eligibil din Europa (și America de Nord, America Latină, UK, Oceania). 3.000 de locuri deschise.

**Cum se aplică:** Aplicare direct pe jobs.micro1.ai → assessment scurt → onboarding în fluxul de review.

> ⚠️ E al patrulea email care îl conține (26.10, 25.10, 24.10, azi) — deci e un rol de durată, nu o urgență. Tot Traseul 2: bani din proiecte + AI, nu job de angajare.

- https://jobs.micro1.ai/post/d02122f3-eaec-42b2-ad3f-edc218b94294

---
## 2. Joburi — scorate cu `ALEX-KIT/scoring.gs`

**62 joburi analizate** (IQads 43 + designproject.io 19) → 33 păstrate în tabele, 29 drop-uri, din care **12 cu verdict amânat** (locația nu e publicată de sursă). **1 job nou** față de 2026-10-26.

Surse: **IQads** (tabloul AdJob activ, citit azi) + **designproject.io** (România + București).

> ⛔ **Expirate marcate în tabele.** La IQads data de expirare vine direct din anunț. La designproject.io `validThrough` = data postării + 30 zile — măsurat pe toate cele 19 de joburi (19 exacte, 0 cu o zi de fus orar, 0 altfel), deci e o expirare reală, nu o derivare inutilă. 7 joburi din tabele au expirat și nu se mai pot aplica.

| | S | D | L | E |
|---|---|---|---|---|
| **S** — senioritate | 0.35 | | | |
| **D** — disciplină | | 0.30 | | |
| **L** — locație | | | 0.20 | |
| **E** — engagement | | | 0.15 | |

### 2.1 Secțiunea 1 — scor maxim — senior/lead, remote sau București, full-time (17)

| Scor | Tag | S/D/L/E | Rol | Companie | Locație | Engagement | Expirare | Nou |
|---|---|---|---|---|---|---|---|---
| **10** | [B2C] | 10/10/10/10 | Senior Creatives | International Waters | Bucuresti, Hybrid (Office & Remote) | Full Time | expiră 2026-11-01 |
| **9.6** | [DTC] | 10/10/8/10 | Art Director | Mercury360 | Bucuresti | Full Time | expiră 2026-12-25 | ✅
| **9.4** | [DTC] | 10/8/10/10 | Media Relations Specialist | Confident Communications | Bucuresti | Full Time | expiră 2026-11-30 |
| **9.4** | [DTC] | 10/8/10/10 | PR Manager | Confident Communications | Bucuresti | Full Time | expiră 2026-11-30 |
| **9.4** | [B2B] | 10/8/10/10 | Digital Marketing Specialist | Alpha Clinic | Hybrid (Office & Remote) | Full Time | expiră 2026-11-27 |
| **9.4** | [DTC] | 10/8/10/10 | Graphic Designer | LUCA | Bucuresti | Full Time | expiră 2026-11-13 |
| **9.4** | [DTC] | 10/8/10/10 | Account Manager | AdSymphony | Hybrid (Office & Remote) | Full Time | expiră 2026-11-01 |
| **9.4** | [B2B] | 10/8/10/10 | Influencer & Creator Marketing Lead | Confident Communications | Bucuresti | Full Time | expiră 2026-10-31 |
| **9.4** | [DTC] | 10/8/10/10 | Senior Product Designer | Jobgether | Romania, Fully Remote | Full Time | postat 2026-10-02 · expiră 2026-11-01 |
| **9.4** | [DTC] | 10/8/10/10 | AI Research Lab UI/UX & Brand Designer (100 % remote) (m/f/d) | EWOR GmbH | Bucharest, Romania, Remote Solely | Full Time | postat 2026-09-25 · expiră 2026-10-25 ⛔ **EXPIRAT** |
| **9.4** | [DTC] | 10/8/10/10 | Industrial Tech UI/UX & Brand Designer (100 % remote) (m/f/d) | EWOR GmbH | Bucharest, Romania, Remote Solely | Full Time | postat 2026-09-18 · expiră 2026-10-18 ⛔ **EXPIRAT** |
| **9.3** | [DTC] | 8/10/10/10 | Graphic Designer & Digital Content Creator | Jobgether | Romania, Fully Remote | Full Time | postat 2026-09-17 · expiră 2026-10-17 ⛔ **EXPIRAT** |
| **9** | [B2B] | 10/8/8/10 | Social Media Specialist | Viva Credit | Romania | Full Time | expiră 2026-12-12 |
| **9** | [B2B] | 10/8/8/10 | Social Media Copywriter | Digital Star | Romania | Full Time | expiră 2026-10-30 |
| **8.7** | [DTC] | 8/8/10/10 | Digital Marketing Specialist | GoTech World | Bucuresti, Hybrid (Office & Remote) | Full Time | expiră 2026-11-30 |
| **8.7** | [B2B] | 8/8/10/10 | Graphic Designer | Super Technologies | Romania, Hybrid | Full Time | postat 2026-09-29 · expiră 2026-10-29 |
| **8.7** | [DTC] | 8/8/10/10 | Senior UX/UI Designer – limited for 2 years maternity cover | METRO/MAKRO | Bucuresti, Romania, Hybrid | Full Time, Contract | postat 2026-09-16 · expiră 2026-10-16 ⛔ **EXPIRAT** |

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

### 2.6 Drop-uri (circuit breaker) — 29

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
| **IQads** | ID-ul ad-ului crește monoton cu postarea. Cel mai mare ID din setul de ieri: **23997** | **1 anunț nou** |
| **designproject.io** | data de publicare vs. ultima rulare | **0 anunțuri noi** — cel mai recent de pe site e din **2026-10-06** |

- **IQads #23999** — Art Director @ Mercury360 (expiră 2026-12-25) — https://www.iqads.ro/adjob/23999/art-director-mercury360
**Concluzie:** 1 postare nou de la ultima rulare.

Ce nu a mai apărut în raportul anterior, dar există în catalog (1 la număr, toate cu ✅ în tabele):

- **9.6** · Secția 1 · Art Director — Mercury360 (IQads)

---

## 5. Ce n-a mers, măsurat

1. **8 din 9 categorii nu mai primesc nimic de 15 zile.** Două cauze, măsurate azi: filtrele folosesc `from:(...)` unde Gmail cere `from:{...}` (paranteze = ȘI, acolade = SAU), deci nu pot lovi niciun mesaj — ar fi prins 3737 mesaje în 30 de zile; și `addLabelIds` e vid pe ele. ~635 mesaje/7 zile stau în inbox.
2. **designproject.io servește descrieri foarte inegale** (363–30012 de caractere pe cele 19 de joburi, măsurat azi). Cele mai lungi sunt rescrise de AI și injectează cuvinte-cheie care ridică axele — vezi §6.2.
3. **Celelalte două câmpuri de engagement ale designproject.io sunt inutilizabile.** `employmentType` din JSON-LD spune `FULL_TIME` pentru 19 din 19, iar badge-ul din listing spune "Full-time" pentru 19 din 19. Singura sură corectă e linia **"Job Type:"** din descriere — prezentă la 19 din 19. Am folosit asta.
4. **Paginatia IQads nu funcționează.** `?page=2` și `?page=3` servesc exact pagina 0 (aceleași 43 de linkuri — verificat azi pe 0, 2, 3). Catalogul complet e pe pagina 0 — nu iterez pagini.
5. **Cota Google: 209 cereri pe 200** (**depășit cu 9**). Consumul pe etape:

| Etapă | Cereri |
|---|---|
| `report-mail-count.js` | 78 |
| `inline` | 71 |
| `report-simulate-sort.js` | 24 |
| `report-filter-state.js` | 20 |
| `report-inbox-counts.js` | 9 |
| `report-folder-discover.js` | 4 |
| **total** | **209** |

> Rulare 2026-10-27 (raport zilnic). Contor pornit de la zero.

**Ce a mers peste plafon:** diagnosticul rearanjării taxonomiei Gmail. Etichetele `MAVIS/*` au fost renumerotate peste noapte, iar raportul trebuia să măsoare noile nume — asta a cerut 71 cereri de diagnostic (liste de etichete, comparații de numere, verificarea filtrului nou funcțional).

Au fost cheltuite pe **înțelegerea** stării, nu pe măsurarea zilei. Zero scrieri pe Gmail — niciun mail trimis, marcat sau arhivat, niciun filtru modificat.

---

## 6. Două semnalări ale motorului de scoring (portul rămâne fidel — decizia e a ta)

### 6.1 "remote" pozitiv fals — 3 joburi

| Rol | Companie | De ce e fals | L |
|---|---|---|---|
| Graphic Designer | LUCA | negatie: `nu se lucreaza remote` | 10 |
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

- `rapoarte/RAPORT-ZILNIC-202610-27.md` — raportul acesta (și în repo)
- `mavis-tools/scoring-result-2026-10-27.json` — scoruri + secțiuni + diagnostice
- `mavis-tools/jobs-iqads-2026-10-27.json` — joburi IQads, text integral
- `mavis-tools/jobs-designproject-2026-10-27.json` — joburi designproject.io, JSON-LD
- `mavis-tools/jobs-2026-10-26.json` — setul normalizat de ieri (cu care s-a comparat)
- `mavis-tools/report-mail-count.json` — numărătoare pe etichetele de categorie
- `mavis-tools/report-inbox-counts.json` — numărătoare exactă inbox
- `mavis-tools/report-simulate-sort.json` — simularea sortării + mesajele de azi
- `mavis-tools/report-source-probe.json` — sonda de surse (comportamentul iqads.ro / designproject.io, măsurat azi)
- `mavis-tools/report-filter-state.json` — starea filtrelor Gmail + testul paranteze-vs-acolade (măsurat azi)
- `mavis-tools/report-triage.js` — clasificatorul mesajelor (needs-reply / needs-action / fyi / noise)
- `mavis-tools/taxonomy.js` — sursa unică pentru numele etichetelor de categorie (rezolvate live, nu hardcodate)

---

*Generat de Mavis Cloud. Nimic nu a fost șters, nimic nu a fost trimis, nimic nu a fost modificat în Gmail sau Drive. Totul e anulabil.*
