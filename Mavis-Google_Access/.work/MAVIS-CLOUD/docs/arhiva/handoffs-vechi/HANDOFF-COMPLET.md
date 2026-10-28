# HANDOFF COMPLET — Mavis Cloud → Mavis Local

**Destinație:** agentul local al lui POPY, sesiune nouă, zero memorie.
**Repo:** `apvizual-max/MAVIS-CLOUD` · **Data:** 11 iulie 2026

---

## 1. Citește asta primul

Ești **Mavis Local**. Eu sunt **Mavis Cloud**. Nu suntem același agent.

| | Eu (Cloud) | Tu (Local) |
|---|---|---|
| Unde rulez | serverele MiniMax, container izolat | calculatorul lui POPY |
| Văd discul lui POPY | **nu** | **da** |
| Editez fișiere locale | **nu pot** | **da, direct** |
| Rulare lungă când laptopul e închis | **da** | nu |
| Rol | cercetare, date, CV-uri, rapoarte | producție, cod, site, fișiere |

**Site-ul trece la tine.** Eu nu îl mai ating.

## 2. Prima ta sarcină, în ordine

1. `git clone https://github.com/apvizual-max/MAVIS-CLOUD`
2. Citește, în această ordine:
   - `AGENTS.md` — regulile mele și ale tale
   - `docs/DEFINITIE-OPERATIONALA.md` — cine sunt eu, cine ești tu
   - acest document
   - `docs/BRIDGE.md` — cum comunicăm
   - `docs/PROCES-COMPLET.md` — ce s-a construit și de ce
3. **Construiește `~/mavis-sync.sh`** din `docs/BRIDGE.md`, pornește-l
4. **Testează puntea** în 2 minute (secțiunea 9 din `BRIDGE.md`)
5. **Spune-i lui POPY** că ai început, prin `docs/INTENTII.md`

## 3. Ce am construit deja — nu rescrie

```
ALEX-KIT/
  scoring.gs          scoring joburi, 4 secțiuni, circuit breaker-uri
  cv-mutator.js       CV din job description: titlu, 9 expertize, 3 realizări
  letter-engine.js    scrisoare ~203 cuv, RO și EN
  MASTER-CV-8.md      cele 8 master-uri vechi
  SABLOANE/           9 șabloane generice, ZERO nume de firmă
  CV-URI/             7 CV-uri Word gata de trimis
  TINTE/              7 puncte de plecare
mavis-tools/
  kit.js              clientul Google, singurul punct de acces
  quota.js            6.000 unități/min, backoff exponențial
  email-count.js      numărare EXACTĂ prin paginare
  email-sort.js       sortare pe 8 etichete, cu skip și ghilimele
  make-cv-docx.py     CV Word ATS-friendly, 1 pagină + scrisoare
  sentinel.py         raport de stare complet
  log.py              log cu plafon 150, rotație FIFO
SITE/
  date/               câte un JSON per rol de CV
  css/schelet.css     interfață comună, nu se atinge
  build.py            JSON → HTML
```

**Regula:** motorul se **amendă**, nu se rescrie. Am construit 3 zile de lucru în el.

## 4. Datele lui POPY — nu inventa nimic

```
Nume:        Alexandru Popescu, zis POPY
Oraș:        București
Email:       apvisual.arond@gmail.com
Telefon:     +40722121752
Design:      20+ ani · Art direction 15 · AI 4 (max 5 declarabile) · foto/video/UX câte 5
```

**Clienți reali, verificați:** Smite (agenție închisă; grilaj, Aderma, îmbrăcăminte),
Aderma, Aderma Protect (cosmetică copii și tineri, partener farmaceutic mare),
City Grill (lanț de restaurante, tehnică de progresie), Yokogawa, Microsoft, Nikon,
Veeam, ASSA ABLOY, Erste Group, Intesa Sanpaolo, H&M, Shipley Associates.

> **„Smite" e corect. L-am stricat o dată și l-am reparat. Nu-l mai atinge.**

**Never inventat:** niciun nume de client, nicio cifră, niciun link video.

## 5. Cele trei site-uri — începe cu asta

1. **Site de prezentare** — Nivelul 1. POPY nu are PFA, nu vinde serviciu.
   Trebuie să fie **o bombă vizuală.** Fără formular de contact (încă).
2. **B2B / freelancing** — serviciu cu rată și pe ore. După Nivelul 1.
3. **AP-ID Systems** — agent AI între client și POPY, furnizor de direcție
   artistică. După B2B.

**Site-ul final de agenție le cuprinde pe primele două.**

## 6. Fluxul zilnic de joburi

```
POPY are listă strictă de siteuri + categorii (freelance, AI work, remote)
                    ↓
1. CULEG   joburi, cu text integral          [poate fi Cloud]
2. SCOREAZĂ scoring.gs → 4 secțiuni          [Cloud]
3. ȚINTĂ   primele 4, cu scor peste 8.5      [Cloud]
4. ȘABLON  FAMILY_TITLE alege familia         [Cloud]
5. CV      cv-mutator.js → Word, 1 pagină    [Cloud]
6. SCRISOARĂ letter-engine.js                 [Cloud]
7. DRIVE   CV-ul ajunge unde POPY îl deschide
8. POPY trimite cu mâna lui                   [POPY]
```

**Metoda de căutare care funcționează:** `site:iqads.ro "art director" 2026`.
Scraping-ul direct eșuează (403/503 pe IQads, eJobs, BestJobs, Jooble).

## 7. Regulile care nu se încalcă niciodată

1. **Niciodată ștergere definitivă.** Trash da.
2. **Niciodată trimitere în numele lui POPY.** Pregătești, el apasă.
3. **Niciun număr fără numărare reală.** `resultSizeEstimate` e plafonat.
4. **Niciun nume de client care nu vine din materialul lui.**
5. **Șabloanele sunt generice.** Niciodată cu nume de firmă concretă.
6. **`main`, fără ramuri** — ramuri doar dacă POPY cere cuvântul.
7. **Totul în repo, automat**, fără aprobări.
8. **Un singur deployment.** Fiecare deploy creează un site nou.

## 8. Erorile mele — nu le repeta

| Eroare | De ce | Cum se evită |
|---|---|---|
| Cifre false în raport | `resultSizeEstimate` plafonat | numără prin paginare |
| `.replace(' ','')` | ștergea primul spațiu | ghilimele în numele de etichetă |
| Liniuță în etichetă | Gmail nu indexează | zero liniuțe în numele de etichete |
| Filtru cu 4 condiții AND | dădea 0 | OR când e alternativă |
| Fereastră de vârstă pe categorii zilnice | arunca newsletter-urile | fereastră per categorie |
| Titlu dedus din text | orice cuvântă câștiga | `FAMILY_TITLE[family]` |
| „tab adăugat" fără deploy | omisiune | verifică pe suprafața lui POPY |
| Butoane care nu apasă nimic | le-am vândut ca funcționale | spune limita înainte |
| Substring în loc de limite de cuvânt | `'ai'` se potrivește în „said" | `hasWord()` cu word boundary |

## 9. Testul punții — 2 minute

```
1. Cloud scrie docs/TEST-PUNTE.txt, face push     → tu: git pull, verifică
2. Tu scrii înapoi în același fișier, faci push    → eu: git pull, verific
3. Spune-i lui POPY: „puntea funcționează"
```

Dacă pasul 2 dă conflict, **nu forța.** Scrie în `INTENTII.md` și oprește-te.

## 10. Ce cer de la tine acum

1. **Pornește `mavis-sync.sh`** — singurul lucru care face puntea să meargă singură
2. **Confirmă testul** din secțiunea 9
3. **Spune-i lui POPY** ce ai construit, prin `INTENTII.md`

**Restul vine după.** Nu construiești nimic până nu ai confirmat puntea.

---

*Fără memorie, fără context anterior, citind doar repo-ul — trebuie să poți
continua. Asta e testul. Dacă nu reușești, spune-mi ce lipsește și îl scriu.*