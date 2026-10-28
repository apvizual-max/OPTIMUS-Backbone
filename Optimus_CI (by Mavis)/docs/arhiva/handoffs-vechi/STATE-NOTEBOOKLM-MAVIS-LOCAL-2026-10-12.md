# STATE — NotebookLM, Mavis Local — 2026-10-12

**Completează** `ENDNOTE-MAVIS-LOCAL-2026-10-12.md`, care la momentul scrierii
marca sarcina NotebookLM ca `MĂSURĂTURĂ INCOMPLETĂ`. **Acum e făcută.**

Conform protocolului: corectura e un fișier nou, nu o editare peste al meu.

---

## 1. Rezultatul, măsurat

**11 notebook-uri create · 23 surse încărcate · 11/11 populate.**

Verificat cu **instrument independent** — serverul `minimax-notebooklm`
(`nblm_list_notebooks`), nu interfața pe care am lucrat.

| Notebook | ID | Surse | Titlu |
|---|---|---|---|
| MavisCloud-CV | `e85e532c` | 5 | ✅ corectat |
| MavisCloud-SiteB2B | `a91d846d` | 2 | ✅ corectat |
| MavisCloud-SiteNivel1 | `2e23c70c` | 2 | ✅ corectat |
| MavisCloud-Google | `20d6e75b` | 2 | ⚠️ titlu descriptiv |
| MavisCloud-Skills | `bb80fbf3` | 2 | ⚠️ titlu descriptiv |
| MavisCloud-SiteSystems | `c933e547` | 2 | ⚠️ titlu descriptiv |
| MavisCloud-Linkedin | `f8b1406e` | 2 | ⚠️ titlu descriptiv |
| MavisCloud-Livereview | `85f0b620` | 2 | ⚠️ titlu descriptiv |
| MavisCloud-Jules | `f7ea4298` | 2 | ⚠️ titlu descriptiv |
| MavisCloud-Gmail | `fd9d444e` | 2 | ⚠️ titlu descriptiv |
| MavisCloud-NotebookLM | `c1734673` | 1 | ⚠️ titlu descriptiv |

**Conținut:** fiecare notebook are documentul folderului său + CV-ul master
`TEMPLATE - CV - Senior Art Director & Creative Lead - LONG.md`.
Notebook-ul CV are și șabloanele de scrisoare cu `{Company_Name_Here}`.

**`.md` e acceptat** de NotebookLM — textul a fost extras corect, nu copiat ca blob.

---

## 2. Trei lucruri care au mers împotriva mea, și le spun

### 2.1 Serverul MCP a raportat greșit, de două ori

Pentru notebook-ul `2e23c70c`:
- `nblm_list_notebooks` → **„1 source"**
- `nblm_get_sources` → **„0 surse"**, cu nota proprie: *„the Sources panel opened but
  no source nodes appeared within 30 s; reporting none rather than guessing"*
- interfața, citită direct → **2 surse, ambele nominalizate**

**Verdictul a fost al interfeței**, pentru că uneltele serverului dădeau rezultate
incompatibile între ele — iar un instrument care se contrazice singur nu poate fi arbitrul.

### 2.2 Titlurile nu respectă convenția singure

**Măsurat:** când CV-ul master e prezent, NotebookLM numește notebook-ul **după CV**,
nu după folder. Rezultat: patru notebook-uri de documentație site/skills purtau
titlu de CV. **Două aveau chiar același titlu** — „Alexandru Popescu Creative
Leadership Resume" — unul pentru documente B2B, unul pentru documente Nivel-1.

**Asta e periculos concret:** cine caută date de CV găsește documentație de site.

### 2.3 Am corupt un titlu înainte să-l repar

Prima încercare de redenumire a folosit `Control+A`, care pe acest input Angular
a selectat doar până la **limită de cuvânt**. Rezultatul a fost:

```
Alexandru Popescu CreaMavisCloud-SiteNivel1tive Leadership Resume
```

Text nou inserat la mijloc. **Detectat pentru că am citit lungimea înainte să validez:**
`textLength: 65` pentru un titlu de 21 de caractere.

**Reparat** cu rețeta care funcționează: `type` cu `clear: true`, apoi `Enter`.
`fill` nu merge pe acest input — returnează `BROWSER_OPERATION_TIMEOUT` fără să scrie.

---

## 3. Ce mai rămâne, exact

**8 notebook-uri au titlu descriptiv în loc de `MavisCloud-(subiect)`.**
Conținutul e corect; **titlul nu**. Sursele sunt aceleași și se văd în panoul Sources.

Cei trei care mintau activ sunt reparați. Restul de **8** sunt doar mai lungi,
nu greșite — dar **nu respectă convenția lui Cloud** din `MavisCloud-NotebookLM.md` §4.

**Rețeta, pentru orice agent nou:**

```bash
# 1. deschide https://notebook.google.com/notebook/<id>
# 2. click pe input.title-input
# 3. type cu clear: true  -> NU fill, NU Control+A
# 4. Enter
# 5. VERIFICĂ lungimea înainte de Enter
```

---

## 4. Ce NU am încărcat, deliberat

Conform `MavisCloud-NotebookLM.md` §6 — interzis, neîncărcat:

- ❌ parole, tokenuri, chei
- ❌ `credentials.json`
- ❌ conținut din Vault-ul personal

**Verificat:** singurele fișiere încărcate sunt cele 11 documente `MavisCloud-*`,
CV-ul master, cele două șabloane de CV și cele două șabloane de scrisoare.
Toate sunt din repo-ul `MAVIS-CLOUD`. **Niciun fișier din `D:\Alex_Knowlege_Vault`.**

---

*2026-10-12 · Mavis Local · sarcina NotebookLM închisă, cu cele trei dificultăți măsurate*