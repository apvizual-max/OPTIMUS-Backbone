# GHID DE WORKFLOW — ce se poate construi ACUM, pe ce fundație

> Toate capabilitățile de mai jos sunt **măsurate**, nu asumate.
> Matricea completă: `CAPABILITATI-GOOGLE.md`.
> Botul: skill `mavis-cloud-google-access-bot`.

---

## 1. Fundația disponibilă

| Piesa | Stare |
|---|---|
| OAuth | app în **„In production"** — fără limită de 7 zile |
| Scope-uri | **27**, lista canonică unică |
| Drive | **100%** — citit, scris, creat, mutat, share, conversie nativă |
| Gmail | **complet** — cu **creare/ștergere filtre din cloud** (`gmail.settings.basic`) |
| Calendar | **complet** — create, update, delete |
| Sheets | **complet** — create, write, read, append |
| Slides | **cu scriere** — add slide + text |
| Docs | **prin conversie Drive** (API direct blocat de anti-bot) |
| Etichete Gmail | **36 de utilizator**, 19/19 filtre validate |
| NotebookLM | ⛔ fără API oficial pentru cont normal → 3 căi, decizie la POPY |

---

## 2. Workflow-uri care se pot construi imediat

### 2.1. Sortare + clasificare Gmail (autonomă, cu filtre)

**De ce merge acum:** filtrele se pot crea din cloud, deci Mavis Cloud își poate
**repasta singur** clasificarea când se schimbă ceva.

```
Workflow: raport zilnic
  1. citește etichetele LIVE (nu din documentație)
  2. verifică fiecare filtru: țintă existentă + criteriu valid
  3. filtre cu criteriu mort → raportează (NU rescrie fără acord)
  4. măsoară cu paginare, pe cont quiet
  5. scrie raportul pe Drive + commit în repo
```

**Regula dură:** când rearanjezi etichete, mută filtrele în aceeași zi.
Cauza celor 16 zile de blackout: `from:(a b c)` = ȘI, plus `addLabelIds` vid.

### 2.2. Pipeline joburi → Sheets → raport

**De ce merge acum:** Sheets e complet (write + append + read), iar
`Design_Jobs_Community_Board` există deja (27 rânduri).

```
Workflow: feed de joburi
  1. descoperire (job-sourcing-methods / scrape-iqads — partea locală)
  2. deduplicare + scor (scoring.gs / ALEX-KIT)
  3. APPEND în Sheets (nu suprascrie)
  4. raport zilnic pe Drive + commit
```

**Atenție:** Sheets e sursă de adevăr pentru „Design Jobs" și e alimentat de
procesul **local**. Nu rescriu rânduri din cloud fără acord — ar fi o cursă.

### 2.3. Arhivare pe Drive cu context

**De ce merge acum:** Drive 100% + creare de Google Doc nativ prin conversie.

```
Workflow: înapoiere informațională
  1. culege (web / Drive / Gmail)
  2. scrie sursa markdown
  3. convergește la Google Doc nativ (files.copy + mimeType)
  4. mută în folderul de referință
  5. commit + push în repo
```

### 2.4. Prezentări generate

```
Workflow: brief de client / prezentare job
  1. create prezentare
  2. createSlide cu predefinedLayout + insertText în placeholder-uri
  3. citește înapoi și verifică textul
```

### 2.5. Calendar pentru interviuri

```
Workflow: pregătire interviu
  1. citește jobul din Sheets
  2. verifică disponibilitatea (calendar list + events)
  3. creează evenimentul PROBAT
  4. cere confirmare înainte de a-l lăsa definitiv
```

### 2.6. Research cu citare (varianta oficială, fără NotebookLM)

```
Workflow: cercetare client / pregătire interviu
  1. culege documente pe Drive
  2. Gemini API + File Search (cheie separată, de la POPY)
  3. întrebări cu citare
```

**Fără cheie Gemini, asta nu merge.** E singurul lucru care blochează calea
oficială. Alternativa plătită: useapi.net (NotebookLM real).

---

## 3. Ce **nu** se construiește din cloud

| Nu aici | De ce | Unde |
|---|---|---|
| Photos Library | 403, scope neacordat, decis de POPY | Mavis Local + Gemini |
| Maps | API key + billing | Mavis Local |
| Docs API direct | blocat de anti-bot | se ocolește prin Drive |
| NotebookLM | fără API oficial pentru cont normal | decizie la POPY |
| Trash-ul golit | făcut de POPY, manual | — |

---

## 4. Regulile care traversează toate workflow-urile

1. **Nu trimite mail.** Draft da; send doar la comanda explicită.
2. **Nu șterge definitiv.** Trash + motiv scris.
3. **Nu scrie în contul lui POPY ca să „testeze"** — artefactele de probe se
   curăță, conținutul lui nu se atinge.
4. **Măsoară înainte să afirmi.** `google-preflight.js` → `google-verify.js` →
   `google-capabilities.js`.
5. **Totul ajunge în repo + Drive.** Conversația e rezumatul, nu stocarea.
6. **Fără permisiune pentru commit/push** — dar **cu R0** înainte.

---

## 5. Ordinea propusă

1. **TO DO 03** — direcția workflow-urilor Gmail/Drive (alege din §2).
2. **TO DO 04** — profilul de designer → CV-uri (pot construi scheletul singur).
3. **TO DO 05** — rotirea cheii API expuse (POPY, Cloud Console).
4. **NotebookLM** — alegerea căii: Gemini API / useapi / local.

---

*2026-10-28 · Mavis Cloud · fundația e măsurată, workflow-urile propuse sunt construibile acum*
