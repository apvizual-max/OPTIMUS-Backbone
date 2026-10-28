# PRIMING PROMPT — sesiune nouă, Google Access

**Copiază tot ce urmează în prima mesaj al sesiunii noi.** E scris pentru un
agent care **nu are niciun context și nicio memorie** despre această lucrare.

---

## Cine ești și ce ai în față

Ai acces la **conexiunea permanentă la Google** de pe această mașină: un
container Docker (`Google_Access`) care ține un singur credential și expune un
singur endpoint MCP pe `http://127.0.0.1:8766/mcp`. E înregistrat **global**
în `C:\Users\apviz\.minimax\mcp.json`, deci îl poți folosi **ca orice agent
de pe stație**, fără să-l instalezi și fără să ceri consimțământ.

**Nu ai nevoie să construiești nimic.** Totul există, rulează singur și se
verifică printr-o singură comandă.

## Comanda de control (rulează-o PRIMA)

```powershell
node "C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\Mavis-Google_Access\scripts\ga-doctor.mjs"
```

Starea măsurată la ultima rulare (2026-10-28 01:54Z):

```
SUMMARY checks=11 failed=0 warnings=0
VERDICT=PASS
```

11 verificări independente: containerul, **octeții rulați în container vs
octeții din repo**, grantul viu, o **probă live per serviciu Google**
(re-probată până la 4 încercări, cu **cauza afișată per serviciu**), tokenul
ExtendLM, handshake-ul real al serverului MCP de browser, registry-ul global,
**integritatea fiecărei căi din registry**, taskurile programate, ascultătorul
de consimțământ și sesiunea Photo Picker.

**Exit 0 = verde · 2 = o verificare a picat (numită în ieșire) · 3 = punctul
de control s-a crapat niciodată raportat ca verde.** Un `WARN` (refuz
tranzitoriu care nu s-a recuperat) e tot exit **0**, cu blipul și cauza
afișate; un refuz **permanent** pictează verificarea (exit 2).

## Starea reală, în numere

- **Container** `Google_Access`, imagine `google-access:1.0.10`, `healthy`, `127.0.0.1:8766`
- **Grant** LIVE, **33 scope-uri**, cont `apvizual@gmail.com`
- **Unelte** 32
- **Servicii** **14 OK · 2 REFUSED · 0 ERROR**
- **Refuzuri acceptate:** `keep` (403 — Google nu publică scope acordabil) și
  `sites` (404 — API retras). **Nu sunt defecte și nu se repară**; Popy
  importă conținutul lor prin alte unelte în Drive. Automatizarea lor e
  **amânată, sub managementul utilizatorului**, cu planul scris în
  `mavis-skill-google-keep-sites`.
- **Refuz tranzitoriu:** `books` răspunde uneori HTTP 503 — `C3` re-probează
  până la 4 încercări și afișează cauza; recuperat → `state=HEALTHY`,
  nerecuperat → `DEGRADED_TRANSIENT` → `WARN` (exit 0).
- **Taskuri** toate `lastResult=0`: `Google_Access_Watch` (oră),
  `Google_Access_Consent` (5 min), `Google_Access_Doctor` (30 min),
  `MavisExtendLMHeartbeat` (30 min), `MavisPickerHeartbeat` (15 min)

## Skillurile — încarcă-le, nu reinventa

**Botul central** (încarcă `SKILL.md` din):
`C:\Users\apviz\.minimax\agents\mavis\skills\mavis-google-access-bot\SKILL.md`

```powershell
node "C:\Users\apviz\.minimax\agents\mavis\skills\mavis-google-access-bot\scripts\bot-registry.mjs" list
node "C:\Users\apviz\.minimax\agents\mavis\skills\mavis-google-access-bot\scripts\bot-registry.mjs" verify
```

| Membru | Pentru ce |
|---|---|
| `mavis-skill-google-access-control-point` | punctul de control + contractul de permanență |
| `mavis-skill-docker-access-point` | containerul, volumele, build-ul, „octeții rulați = octeții din repo" |
| `mavis-skill-browser-mcp` | `minimax-notebooklm` (profil Chrome propriu, CDP 9412), fereastra pickerului, planul Browser MCP |
| `mavis-skill-mcp-development` | cum intră următorul MCP în punctul central |
| `mavis-skill-photo-picker` | singura ușă spre biblioteca foto (doar ce selectează Popy) |
| `mavis-skill-notebooklm-extendlm` | rotația tokenului, snapshotul pentru Cloud |
| `mavis-skill-google-keep-sites` | cele două refuzuri + planul amânat |
| `mavis-skill-access-handoff` | cum se predă mai departe, cu 0 context |
| `mavis-skill-background-task-verdict` | cum se judecă o măsurătoare lungă: **pe marcajele tipărite**, nu pe codul de ieșire |

## Regulile (sunt ale sistemului, nu ale unei sesiuni)

1. **Nu reconfigurați setările.** Dacă ceva nu merge, rulează punctul de
   control, citește verificarea care a picat, repară **acea** bucată.
2. **Nu re-autentifica** decât dacă Google cere (verificarea arată
   `reauth_required=true`). Clickul de consimțământ e singurul pas uman, și
   ascultătorul e deja viu pe port 80.
3. **Nu adăuga scope-uri Google** fără să le verifici mai întâi — un scope
   invalid invalidă **întreaga** cerere de consimțământ.
4. **Credentialul nu iese din volum** — nici în repo, nici în log, nici în
   chat, nici într-un document.
5. **`minimax` și `Hermes` sunt universuri separate.** Duplicare, nu
   partajare.
6. **Un fișier prezent dar mai vechi e o regresie, nu o mutare.** La mutarea
   conținutului, compară-l (`scripts/compare-layer-versions.py`).
7. **Nu rula `docker container prune -a`.**

## Unde sunt toate lucrurile

- Punctul de control: `Mavis-Google_Access\scripts\ga-doctor.mjs`
- Spec + dovăză cu dată: `Mavis-Google_Access\docs\PUNCT-DE-CONTROL.md`,
  `Mavis-Google_Access\docs\STARE-MASURATA.md`
- Sursa vie a containerului: `C:\Users\apviz\.minimax\google-access\`
- Registry MCP global: `C:\Users\apviz\.minimax\mcp.json`
- Instrucțiunea vie, pentru orice agent: `C:\Users\apviz\.minimax\AGENTS.md` §12.5
- Handoff-ul complet: `Mavis-Google_Access\.handoff\HANDOFF-GOOGLE-ACCESS.md`

## Cum lucrezi de aici înainte

1. Rulează punctul de control. **Citește verdictul înainte să faci orice.**
2. Dacă e verde, lucrezi. Dacă nu, repară verificarea numită.
3. Pentru orice schimbare: **măsoară înainte și după**, și citește cifra din
   instrument, nu din amintire.
4. Când schimbi ceva, **commit automat pe `main`**; **push cere acordul lui
   Popy** (poarta: `scripts\git-autopush.ps1 -Acord` în repo-ul backbone).
5. La final, **predă mai departe** cu `mavis-skill-access-handoff`.

## Un lucru pe care nu știi încă

La 28 oct, finalizarea punctului de control a scos la iveală **patru defecte
active** care stăteau de săptămâni: trei intrări MCP rupte de o mutare de
folder, un server MCP care indica spre un wrapper inexistent, **trei
optimizări fuzionate pierdute într-o mutare** (fișierul era prezent, dar mai
vechi) și o sesiune Photo Picker **consumată raportată ca defect**. Niciunul
nu se vedea înainte de măsurare. Deci: **măsoară, nu presupune.**
