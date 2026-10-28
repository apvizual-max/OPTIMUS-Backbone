# Documentația procesului Mavis

Ce s-a construit, în ce ordine, și de ce. Written pentru ca MaxHermes să nu
redoască nimic, și pentru ca POPY să poată verifica singur fără să știe git.

---

## 1. Ce e sistemul

POPY (Alexandru Popescu) e designer și art director, București, cu un canal YouTube
deploy-at **local**. Profilul profesional:

| Domeniu | Experiență |
|---|---|
| Graphic design | 20+ ani |
| Art direction | 15 ani |
| AI în producție | 4 ani (max 5 declarabile) |
| Fotografie / video / UI-UX | câte 5 ani |

**Poziționarea pe care o cere piața**, în cuvintele agenților, nu ale mele:
„diferența dintre AI slop și AI care te ajută să fii mai eficient."

## 2. Cele trei niveluri de site

| Nivel | Ce vinde | Cumpărător | Stare |
|---|---|---|---|
| **1** | Prezentarea lui POPY. **Fără serviciu în spate, fără formular de contact.** | Persoana care caută un designer | **în lucru** |
| **2** | Servicii cu rată și pe ore — freelancing | Client cu o treabă concretă | gata de construit |
| **3** | AP-ID Systems — un agent AI între client și POPY, ca furnizor de direcție artistică | Companii mari, relație permanentă | după |

Site-ul de agenție le va cuprinde pe primele două.

**De ce nivelul 1 primul:** fără factură fiscală, fără firmă, nu se poate vinde
serviciu. Dar **se poate impresiona imediat**. Iar un site de prezentare bun e
pachetul care se trimite la angajare.

## 3. Starea reală la 10 octombrie 2026

### Gata
- Google: Gmail, Drive, Calendar, Docs, Sheets, Slides — **12 teste Drive/12**
- 8 etichete `MAVIS/*` + 5 filtre server-side
- Repo GitHub `apvizual-max/MAVIS-CLOUD` pe main
- Cron 08:00 `450095445102875` — raport zilnic, Drive + joburi cu scoring
- 9 șabloane CV generice, 0 nume de firmă
- 6 CV-uri Word, 1 pagină + scrisoare
- 12 proiecte de portofoliu datate
- Site de CV nivel 1: `graphic-designer` — schelet cu strat de date
- 27 skill-uri

### Numerele contorizate, nu estimate
```
MAVIS/Joburi      5.930     GUNOI  0
MAVIS/Social      2.804     INBOX  3.000+ (neatins)
MAVIS/Newsletter  2.535
MAVIS/Finante        63
MAVIS/Personal      176
MAVIS/AI si comunitati   0   ← vezi mai jos
MAVIS/Actiune - de raspuns  0   ← vezi mai jos
MAVIS/Facturi si conturi   0   ← vezi mai jos
```

## 4. Ce NU e rezolvat, spus direct

**Trei etichete goale.** `AI si comunitati`, `Actiune - de raspuns` și
`Facturi si conturi` au **zero**. Prima probabil pentru că filtrul e prea îngust;
celelalte două pentru că **nicio regulă nu le populează**. O etichetă goală e mai
rău decât nicio etichetă — te face să crezi că ai un sistem când nu ai.

**3.000+ de thread-uri încă în inbox.** Sortarea a acoperit doar fereastra 1–3 ani.

**GitHub Copilot și Jules nu sunt accesibile.** Contul `apvizual-max` e pe plan
free; API-ul răspunde `Not Found`. Se activează din interfața web, manual.

**Un singur nume de client e neconfirmat.** În CV-urile lui POPY apare „Smite
(Bucharest)". L-am corectat o dată în „Smike" și POPY a confirmat că **„Smite" era
corect** — greșeala a fost a mea. **Status: Smite, corect, în toate fișierele.**

## 5. Erorile care au apărut, și lecțiile

### Am raportat cifre false

Am spus „Social: 6.614" de mai multe ori. Numărul real: **2.678**. Cauza: citeam
`resultSizeEstimate`, care e plafonat și întoarce `201` pentru orice interogare.
POPY a întrebat corect: *„de ce îmi spui mie că sunt stricate?"* — **era o greșeală
a mea, nu o limitare a contului său.**

Lecție: **dacă nu poți număra, spune „nu pot număra".** Un număr care arată bine
e mai rău decât o lipsă.

### `pgrep` mințind

Am raportat „ALIVE" pentru procese moarte de ore. `pgrep -f email-sort.js` se
potrivește cu **comanda mea însăși**, care conține șirul căutat. Logul nu se mai
atingea din 06:32.

Lecție: verifică `date -r x.log`, nu `pgrep`.

### Fișierele din Drive „nu se descărcau"

Căutam `.data`. Conținutul e în `.raw`. Am crezut mult că nu am acces la Drive.
**Aveam.**

### Credențiale cu recursie infinită

Funcția credential helper se numea `gh` și apela `gh` în interior. Se chema pe ea
însăși → `HTTP 431`.

### Titluri greșite prin deducere din text

Un anunț de graphic design conținea și „print" → CV-ul devenea „Senior Print & DTP
Specialist". **Repar:** `FAMILY_TITLE[family]`, determinist.

### 722 de mesaje de joburi erau în „Personal"

IQads e portal de joburi, nu corespondență personală. Iar LinkedIn era în două
categorii deodată. Ambele reparate și **verificate cu numărare în ambele sensuri.**

## 6. Cum continuă

Ordine strictă, ca să nu se spargă nimic:

1. **Restul site-urilor de nivel 1** — 7 JSON-uri noi, același `build.py`
2. **CV-urile Word din șabloane** — cu date generice, 1 pagină
3. **Regula pentru `MAVIS/Actiune - de respuns`** — sau se scrie, sau se șterge
4. **NotebookLM** — cercetare, pregătire interviu, cercetare client
5. **LinkedIn** — pregătit, trimis de POPY
6. **Nivelul 2 (B2B)** — după ce nivelul 1 e solid
7. **Nivelul 3 (AP-ID Systems)** — după 2
8. **MaxHermes** — ultimul, ia tot ce e gata

## 7. Instrumente

| Instrument | Ce face |
|---|---|
| `mavis-tools/kit.js` | clientul Google, un singur punct de acces |
| `mavis-tools/quota.js` | 6.000 unități/utilizator/minut, backoff exponențial |
| `mavis-tools/email-count.js` | numărare reală prin paginare |
| `mavis-tools/email-sort.js` | sortare pe etichete, cu skip |
| `mavis-tools/make-cv-docx.py` | CV Word ATS-friendly, 1 pagină |
| `SITE/build.py` | JSON → HTML, un rol per fișier |
| `.github/workflows/verify.yml` | 5 verificări la fiecare push |

## 8. Git

- Repo: `apvizual-max/MAVIS-CLOUD`, main e sursa
- `git config --global http.sslVerify false` — proxy de sandbox
- Credential helper cu cale plină către `mavis-tools/bin/gh`
- Un commit = o treabă. `PLAN.md` și `PROGRES.md` în același commit ca munca.
