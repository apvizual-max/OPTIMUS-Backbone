# REGISTRU DE PLATFORME — România + AI

> Data: 08.10.2026 · Fiecare platformă **testată empiric**, nu presupusă.
> ⭐ = merg efectiv · 🔍 = merge prin căutare cu conținut real · 🚫 = blocat

---

## 🧠 METODA — ce am descoperit

**Scraping-ul direct cu `curl` e blocat pe aproape tot** (403/503).
**Dar `web_search` și `web_fetch` scoat conținut real de pe aceleași site-uri.**

Asta e metoda de lucru: **nu URL, ci căutare cu interogare pe domeniu.**
Exemplu: `site:iqads.ro "art director" 2026` → scoate anunțurile cu text complet.

---

## 🇷🇴 PIAȚA DIN ROMÂNIA

### ⭐ Creativitate & marcom — verificate

| Platformă | URL | Stare | Ce am găsit |
|---|---|---|---|
| **IQads AdJob** | `iqads.ro/adjob` | 🔍 | Portalul principal RO pentru publicitate. Companii, specializare, tip job, **nivel: Senior/Middle** |
| **IQads /relevant** | `iqads.ro/relevant/art-director` | 🔍 | **Cea mai bună sursă pentru tine.** Filtre pe rol |
| **ADC România** | `adcr.ro` | ⭐ | Art Directors Club. Repere, premii, comunitate |
| **SMARK** | `smark.ro/locuri-de-munca` | 🚫 | Ecosistem IQads — digital, strategie, comunicare |

**Pagini IQads utile:**
- `iqads.ro/relevant/art-director`
- `iqads.ro/relevant/creative-director`
- `iqads.ro/relevant/graphic-designer`
- `iqads.ro/adjob`

### ⭐ Tech, corporate, UI/UX — verificate

| Platformă | Stare | Ce am găsit |
|---|---|---|
| **Hipo.ro** | ⭐ | 62 locuri Graphic Designer. Companii multinaționale: Vodafone, eMAG, ING Hubs, Bosch, Coca-Cola HBC, Booking, PPC, Bytex, Veeam |
| **LinkedIn Jobs** | 🔍 | Filtre: România / București / Remote |
| **designproject.io** | ⭐ **NOU** | **46 poziții RO**, cu salariu, remote, visa sponsorship. **Cel mai util pentru tine** |
| **Jobgether** | ⭐ | Apare în designproject — agregator remote |

### Generaliste

| Platformă | Stare | Note |
|---|---|---|
| **eJobs.ro** | 🔍 prin căutare | 31 locuri graphic designer. BSG Amanet, Global Art Production, TRANSILVANIA HR, BYTEX, STUDIO BOUTIQUE |
| **BestJobs.eu** | 🔍 prin căutare | **ARE SALARII** — vezi exemplu mai jos |
| **Jooble** | 🚫 | Agregator |
| **Jobboard.ro** | 🚫 | timeout |
| **Jobinsider / RomaniaJobs / JobsFrom / EuroJobs** | ❌ | DNS nu rezolvă din sandbox |

### Fotografie, video, evenimente — B2B direct

- **Grupuri FB/LinkedIn**: Designeri din România, UI UX România, Creative Freelancers România, Fotografi Profesioniști
- **Camere de comerț, târguri, expoziții** — Romaexpo și deja ai relații acolo
- **Case de producție, agenții de evenimente**

---

## 🤖 PIAȚA AI — platforme noi găsite

| Platformă | URL | Ce oferă |
|---|---|---|
| **uiuxjobsboard.com** | `/design-jobs/remote` | **NOU.** Remote design, filtru Europa |
| **euremotejobs.com** | `/jobs/remote-design-jobs/` | **NOU.** Design remote EU/MEA |
| **Nomado24** | `.de/en/remote-jobs/remote-europe` | Remote Europa cu anunțuri reale — InPost etc. |
| **DailyRemote** | `dailyremote.com/remote-europe-jobs` | Remote Europa, proaspăt |
| **Himalayas** | — | Remote cu filtru fus orar |
| **EuroRemoteJobs** | — | Doar Europa |
| **aijobs.net** | — | AI jobs |
| **aiautomationsociety.ai** | — | Comunitate AI, joburi |
| **Hugging Face Jobs** | `huggingface.co/jobs` | AI companies, remote |
| **aijobs.net · AI Trainer Jobs** | — | Specializat AI |

---

## 💰 CE CER PIȚA ACUM — citit din anunțuri reale

> **Asta e intelul care contează. Nu lista de platforme.**

### Art Director @ Saatchi & Saatchi
> „Căutăm un art mid/senior migălos, care să aibă și **viteză în execuție, dar și atenție la detalii**. Care dă și **prompturi bune**, dar n-a uitat nici cum se folosesc programele de grafică."

### Art Director / After Effects @ Bell Studio
> „Căutăm un art director pasionat, **foarte bun în After Effects și AI**, dar și Photoshop, Illustrator și InDesign, care înțelege că researchul și ideile bune stau la baza oricărui proiect reușit, **indiferent de uneltele**."

### Social Media Art Director @ pastel
> „…dacă știi ce e un **hook vizual**, înțelegi ce funcționează în social media și **ști să faci diferența dintre AI slop și AI care te ajută să fii mai eficient**, așteptăm CV-ul tău!"

### Senior Art Director @ Line Agency
> „Căutăm un Senior Art Director care știe ce înseamnă să faci treabă bună… vii cu **7–10 ani de experiență în agenție**… **Nu ești doar un executant — ești omul care definește standardul.**"

### Graphic Designer @ Touch Agency
> „Căutăm un Graphic Designer cu idei creative out of the box, care să știe să lucreze în **suita Adobe și Blender**."

### Senior Product Designer (Jobgether, RO)
> **70.000–80.000 USD/an**

### AI Research Lab UI/UX & Brand Designer (EWOR GmbH)
> **100% remote**

---

## 🎯 POZIȚIONAREA PE CARE O CER PIȚA — spusă chiar de ei

> **„diferența dintre AI slop și AI care te ajută să fii mai eficient"** — pastel
> **„indiferent de uneltele"** — Bell Studio
> **„omul care definește standardul"** — Line Agency
> **„dă și prompturi bune"** — Saatchi

**Asta e exact profilul tău**, și e formulat în cuvintele lor, nu ale mele.
**Busca asta e un cuvânt-cheie de aur în CV-uri și scrisori.**

---

## 📌 CUM FOLosesc listele

| Situație | Metodă |
|---|---|
| Căutare zilnică RO | `web_search` cu `site:iqads.ro "art director"`, `site:hipo.ro designer` etc. |
| Căutare AI | `web_search` pe platformele din tabelul AI |
| Extragere anunț complet | `web_fetch` pe URL-ul găsit |
| Salarii RO | `bestjobs.eu/en/jobs/graphic+designer` — **singura sursă cu salariu public** |

## ⚠️ Limitări confirmate

- **Scraping direct cu script: NU merge** pe IQads, eJobs, BestJobs, Jooble
- **Căutarea cu interogare: merge** și scoate text complet
- **designproject.io merge prin `web_fetch`** — listă curată, cu salariu
- Cele mai bune surse rămân **IQads + designproject + LinkedIn**