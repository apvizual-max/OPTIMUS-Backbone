---
name: mavis-notebooklm-bridge-skill
description: Autonomous NotebookLM workflow for Mavis — read AND write without ever asking Popy to log in. Use for any NotebookLM operation (list, create, rename, upload sources, query with citations). Supersedes the old browser-login path, which is FORBIDDEN.
---

# NotebookLM Workflow — autonom, fără login uman

**Stare: măsurată 2026-10-12.** Tot ce e mai jos a fost rulat și verificat, nu presupus.
Dacă o cifră de aici nu se reproduce, tratată ca `MĂSURĂTURĂ INCOMPLETĂ` — nu completa cu presupunere.

> **Interzis absolut:** NU cere lui Popy să se autentifice vreodată în NotebookLM.
> Nu deschide browserul grafic în acest scop. Nu folosi `mcp__notebooklm-mcp__*`
> — e neautentificat și nu e o cale de scris. Dacă simți nevoia de login, calea
> de mai jos e cea greșită; citește „Diagnostic" înainte să acționezi.

---

## 1. Cele două servere MCP — și care e real

| Server | Stare măsurată | Verdict |
|---|---|---|
| `minimax-notebooklm` | `authenticated: true`, cont `apvizual@gmail.com`, **4 unelte de citire** | ✅ singurul server MCP viu |
| `notebooklm-mcp` | `authenticated: false`, `notebook_url: "not configured"` | ❌ mort — nu e o cale |

**Uneltele singure ale serverului viu:** `nblm_health`, `nblm_list_notebooks`,
`nblm_get_sources`, `nblm_ask`. **Toate de citire.** Nu există `add_source` sau
`create_notebook` — și n-a fost adăugat, pentru că nu e necesar (vezi §3).

## 2. De ce funcționează fără login

Serverul MCP pornește Chrome **headless** cu un profil **deja autentificat, aflat pe disc**:

- Profil: `C:\Users\apviz\AppData\Local\minimax-notebooklm\chrome_profile`
- Port CDP: **9412** (`NBLM_CDP_PORT` poate override)
- Endpoint: `http://127.0.0.1:9412/json/version` → Chrome/155.0.8059.39
- Node: **v26.5.1** — `WebSocket` e global, **zero pachete externe necesare**

Profilul e pe disc → sesiunea supraviețuiește repornirii. **E o cheie de ușă, nu o barieră.**

## 3. Scriptul autonom — calea de scris

```
C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Continuous-Integration\scripts\notebooklm-cdp.mjs
```

Commit-at în `MAVIS-OPTIMUS-CI` la `65c11d2`.

| Comandă | Ce face |
|---|---|
| `node scripts/notebooklm-cdp.mjs auth` | probe de autentificare → `signedIn`, cont, nr notebook-uri |
| `node scripts/notebooklm-cdp.mjs list` | aceeași, fără re-nav |
| `node scripts/notebooklm-cdp.mjs rename <id> <titlu>` | redenumește un notebook |

**Marcajul de autentificare e un marker de CONT, nu absența unui buton.**
Un check care întreabă „există buton de login?" nu poate eșua — e un check fals.
Se caută `[aria-label*="Google Account"]` și se raportează contul real.

## 4. Cum se scrie pe inputul NotebookLM (neîncercat, dar dedus din măsurătoare)

Inputul de titlu e **Angular controlat** (`input.title-input`). Pe acest tip de input:

- **`fill` → TIMEOUT.** Nu scrie nimic. Nu-l folosi niciodată.
- **`Control+A` / `Shift+Home` → CORUP TITLUL.** Selecția se oprește la **limită de
  cuvânt**, deci textul nou se inserează în mijlocul celui vechi. Măsurat: un titlu
  de 65 de caractere a rămas 65 după „scriere", doarece noul s-a lipit peste el.
- **Ce funcționează:** focus → `Input.dispatchKeyEvent` Ctrl+A → `Input.insertText`.

**Verifică `textLength` înainte de Enter.** 21 de caractere = scriere corectă.
45 când așteptai 22 = text lipit peste unul existent. Fără cifra asta, corupția
trece drept succes — exact cum s-a întâmplat.

## 5. Regula de aur: verifică cu alt instrument

Aceeași unealtă **nu e arbitru pentru propria scriere.** Un `verified: true`
de la un write dovedește doar că apelul a fost acceptat, nu că starea s-a schimbat.

Măsurat asta: scris prin CDP → verificat prin `mcp__minimax-notebooklm__nblm_list_notebooks`
→ titlul restaurat, `updated: 12 Oct 2026`.

## 6. Inventarul curent — 11 notebook-uri, 24 surse, convenție strictă

| Notebook | ID | Surse |
|---|---|---|
| MavisCloud-CV | `e85e532c-812c-4292-b0c3-6d7ded621002` | 5 |
| MavisCloud-NotebookLM | `c1734673-e376-4298-8671-1c8f9e5c59cf` | 1 |
| MavisCloud-Gmail | `fd9d444e-614f-4cd2-b6a2-58749a85678b` | 2 |
| MavisCloud-Jules | `f7ea4298-8604-4df3-ab3f-a6d634d4cbc6` | 2 |
| MavisCloud-Livereview | `85f0b620-ca40-4a84-9f0f-998a9fe1e049` | 2 |
| MavisCloud-Linkedin | `f8b1406e-5fd5-41d7-95b8-61abda3da353` | 2 |
| MavisCloud-SiteSystems | `c933e547-d370-47ff-9e9b-297b84bfa356` | 2 |
| MavisCloud-Skills | `bb80fbf3-394c-40f8-ae5f-aed67dd5c9b0` | 2 |
| MavisCloud-Google | `20d6e75b-0d53-4ea5-b784-7236501804b8` | 2 |
| MavisCloud-SiteB2B | `a91d846d-1dd2-4bab-95eb-56339977d52f` | 2 |
| MavisCloud-SiteNivel1 | `2e23c70c-07b9-431b-ac7f-deb61b5c761f` | 2 |

**Convenție de denumire — obligatorie:** `MavisCloud-(subiect)` = creat de instanța
Cloud · `MavisLocal-(subiect)` = creat de instanța Local. Fiecare instanță își
numește propriile fișiere, ca să nu se suprascrie în repo-urile comune.

## 7. Ce se poate încărca — și ce nu

- ✅ **Doar** documente din repo-ul `MAVIS-CLOUD`. Observat ca read-only de Local.
- ❌ **Niciun secret** — parole, tokenuri, chei API, coduri. Niciun `.env`, niciun `Secrets.md`.
- ❌ **Niciun fișier din Vault** (`D:\Alex_Knowlege_Vault`) — e zăvorât și nu se
  încarcă, nici măcar fișiere de configurare.
- ❌ **Zero scanări brute** pe cele ~52.000 de fișiere din Vault — navighează prin Cotor.

**Invariante de conținut la încărcare** (verifică înainte și după):
- `Creafac` — **strict interzis**, brand corect: **Ducray**
- email canonic unic: `apvizual@gmail.com`
- Skin Media = Nikon / Aiper / Ninja · Smite = City Grill / Aderma Protect / Ducray
- șablon de dovedire: **`dovedire pe cerere`** / `dovezile video se furnizează la cerere`.
  Ratificat de Popy 2026-10-12 ca echivalent contractual pentru deliverabilul RO.
  `proof of work provided on request` este forma EN, **nu se mai cere în HTML-ul RO**.
- sursa ATS exclusiv: `ALEX-KIT/TEMPLATES-POPY/` · `ALEX-KIT/SABLOANE/` = `DEPRECATED.md`

## 8. Starea reală — ce e probat și ce NU

| Operație | Stare | Măsurătoare |
|---|---|---|
| Citire listă | ✅ probat | 22 notebook-uri în cont |
| Citire conținut | ✅ probat | `nblm_get_sources`, `nblm_ask` cu citări |
| Auth fără login | ✅ probat | 2 rulări consecutive, `signedIn: true` |
| **Scriere: rename** | ✅ **probat** | 30/30 și 21/21 caractere; persistență confirmată de alt instrument |
| Scriere: creare notebook | ⚠️ **NEPROBAT** | — |
| Scriere: upload fișiere | ⚠️ **NEPROBAT** | altă suprafață de UI decât rename |
| Query cu citări | ✅ probat | `nblm_ask` |

**Cele două neprobate se testează pe conținut de test, niciodată direct pe cele
24 de surse ale lui Popy.** Nu raporta succes până când valoarea n-a fost citită înapoi.

## 9. Diagnostic — când ceva nu merge

```powershell
# Chrome-ul headless rulează?
Get-Process chrome | Select-Object Id, StartTime
# Portul CDP răspunde?
node scripts/notebooklm-cdp.mjs auth
Get-NetTCPConnection -LocalPort 9412
```

Dacă portul nu răspunde: Chrome-ul cu profilul notebooklm nu rulează. **Pornește-l
pornind serverul MCP** — profilul e deja autentificat, deci repornirea nu cere login.
Dacă `signedIn: false` după repornire, profilul a fost șters → **anunță-l pe Popy**,
nu încerca să te autentifici singur și nu cere parola lui.

## 10. Cuplarea cu Obsidian

Second Brain = Obsidian (structură locală, canonică) + NotebookLM (motor de citări).
Când Popy spune „second brain", tratează ambele ca un singur sistem operațional.

## Reguli dure

- **Nu cere niciodată login.** Nici parolă, nici cod de verificare, nici „apasă butonul".
- **Nu inventa citări.** Dacă un query se întoarce fără surse, spune că nu are suport.
- **Nu exporta și nu partajezi corpusul** fără R0 explicit.
- **Nu modifica serverul MCP** pentru a adăuga unelte de scris — scriptul CDP rezolvă
  treaba fără a atinge configurația.

## Referințe

- Script: `Mavis-Optimus-Continuous-Integration\scripts\notebooklm-cdp.mjs` @ `65c11d2`
- Bridge file: `10_BRIDGES\10_notebooklm.md`
- Doctrină: `SENTINEL_OPERATIONAL_DOCTRINE.md §11`
- Protocol denumire: `MAVIS-OPTIMUS-CI\docs\PROTOCOL-DENUMIRE-LOCAL-CLOUD.md`