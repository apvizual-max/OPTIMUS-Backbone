# SKILLS INDEX — ce contează pentru Google Access

Toate skill-urile de mai jos sunt **pe disc, la aceste căi**, și au fost
verificate în această sesiune (folderul există, `SKILL.md` se citește,
frontmatter-ul nu contrazice numele folderului).

**Botul central:**
`C:\Users\apviz\.minimax\agents\mavis\skills\mavis-google-access-bot\SKILL.md`

```powershell
node "C:\Users\apviz\.minimax\agents\mavis\skills\mavis-google-access-bot\scripts\bot-registry.mjs" list
node "C:\Users\apviz\.minimax\agents\mavis\skills\mavis-google-access-bot\scripts\bot-registry.mjs" verify
```

---

## 1. Membrii botului — deținuți, cu verificator propriu

Fiecare membru are `SKILL.md` + `runs.md` + `scripts/verify-*.mjs`. Verificatorul
reinteroghează sistemul și **poate aprinde roșu**.

| Skill | Cale | Deține | Verificat |
|---|---|---|---|
| `mavis-skill-google-access-control-point` | `skills\mavis-skill-google-access-control-point\` | punctul de control (11 verificări, verdict unic) + contractul de permanență | `VERDICT=PASS` (4/4) — doctorul: 11 checks, failed=0; falsificat cu `--self-test --fail` → exit 2 |
| `mavis-skill-docker-access-point` | `skills\mavis-skill-docker-access-point\` | containerul: build, volumele, portul, „octeții rulați = octeții din repo" | `VERDICT=PASS` (5) — running sha256 `8429fa512919` = repo sha256 |
| `mavis-skill-browser-mcp` | `skills\mavis-skill-browser-mcp\` | stratul de browser: `minimax-notebooklm`, fereastra pickerului, **planul Browser MCP** | `VERDICT=PASS` (5) — handshake real, server=minimax-notebooklm, tools=4 |
| `mavis-skill-mcp-development` | `skills\mavis-skill-mcp-development\` | cum intră următorul MCP în punctul central; contractul registry-ului; **planul MCP-urilor viitoare** | `VERDICT=PASS` (5) — 23 căi, dead=0 |
| `mavis-skill-photo-picker` | `skills\mavis-skill-photo-picker\` | singura ușă spre biblioteca foto; starea „consumată" | `VERDICT=PASS` (5) — 6 fișiere, toate JPEG reale |
| `mavis-skill-notebooklm-extendlm` | `skills\mavis-skill-notebooklm-extendlm\` | rotația tokenului, snapshotul Cloud, limitele ambelor drumuri | `VERDICT=PASS` — token 133 min, secret Cloud 17 min |
| `mavis-skill-google-keep-sites` | `skills\mavis-skill-google-keep-sites\` | cele două refuzuri + **planul automatizării amânate** | `VERDICT=PASS` — ambele scope absente din `FULL_SCOPES`, ambele `STATUS=REFUSED` |
| `mavis-skill-access-handoff` | `skills\mavis-skill-access-handoff\` | protocolul de predare cu 0 context | `VERDICT=PASS` — 33 căi verificate, dead=0 |
| `mavis-skill-background-task-verdict` | `skills\mavis-skill-background-task-verdict\` | cum se judecă o măsurătoare lungă: **pe marcajele tipărite**, nu pe codul de ieșire al shell-ului | `VERDICT=PASS` — 17 checks, failed=0, falsified=4; inversia măsurată: exit interior 2 cu marcajul prezent → wrapper exit 0 |

*(Rădăcina: `C:\Users\apviz\.minimax\agents\mavis\skills\`)*

---

## 2. Referințele — există, contează, dar nu sunt deținute de acest bot

| Skill | Ce aduce |
|---|---|
| `mavis-google-access-skill` | micro-skill-ul preexistent: istoricul, defectul celor două granturi, cele patru interdicții |
| `mavis-google-workspace-skill` | accesul Google pe partea Workspace, cu grantul și scope-urile lui |
| `mavis-notebooklm-bridge-skill` | puntea NotebookLM, din familia de punți |
| `mavis-mcp-management-skill` | managementul MCP de pe stație: flota, registry-ul, regulile de transport |
| `mavis-docker-gordon-skill` | operațiuni Docker și diagnosticul |
| `mavis-antigravity-docker-admin-skill` | administrarea Docker din partea Antigravity |
| `mavis-chrome-browser-skill` | automatizarea browserului, general |
| `mavis-shared-local-mcp-swarm-skill` | cum se coordonează mai multe servere locale fără a împărți credentiale |
| `mavis-autonomous-operator-skill` | cum acționează operatorul fără să fie întrebat |
| `mavis-full-intent-execution-skill` | ducerea unei intenții până la capăt |
| `mavis-session-lifecycle-skill` | ciclul de viață al sesiunii — granița pe care o traversează acest handoff |
| `mavis-memory-curator-skill` | ce merită păstrat în memorie și ce e doar un fapt temporar |
| `mavis-search-before-write` | regula permanentă: caută întâi, scrie pe urmă |
| `mavis-backbone-skill` | backbone-ul în care stă acest ecosistem |
| `mavis-cloud-bridge-skill` | puntea Local↔Cloud |
| `mavis-local-to-cloud-reporting` | raportarea Local→Cloud și contractul canalului |
| `mavis-skill-index` | indexul master al tuturor skill-urilor pe care le poate apela Mavis |
| `mavis-bundle-operations` | bundle-ul din care e dispecedat acest bot |
| `mavis-minimax-index-folder-update` | păstrarea adevărului în folderele de index |
| `mavis-jules-contract-skill` | contractul Jules, consumat de partea Cloud |
| `mavis-doc-bridge-skill` | puntea documentelor |
| `mavis-instruction-fidelity-skill` | executarea unei instrucțiuni așa cum e scrisă |
| `mavis-git-autonom-skill` | git autonom + poarta de push |
| `mavis-triple-crunch-skill` | disciplina filtrului triplu |
| `mavis-r33-bimodal-skill` | contractul workflow bimodal |
| `mavis-antigravity-ecosystem-integrations-skill` | integrațiile între ecosisteme |
| `mavis-skill-repair-manifest-skill` | calea de recuperare când instalarea unui membru pică: repară fișierele instalate și actualizează `manifest.json` |

---

## 3. Skilluri din afara arborelui de mai sus, utile aici

| Skill | De ce |
|---|---|
| `mavis-session-extract-bot-skill` | **tiparul de structură** al acestui bot: contract, registry executabil, buclă de actualizare |
| `mavis-bot-creator-skill` | procesul de creare a unui membru + checklist-ul „definition of done" |
| `mavis-deliverable-handoff-skill` | cum ajung fișierele la Popy (`<media />`) |
| `mavis-session-transcript-skill` | extragerea transcriptului unei sesiuni — utilă dacă predarea trebuie probată |

---

## 4. Ce NU este în listă, și de ce

| Nu e aici | De ce |
|---|---|
| Fișierele de proiect din `Mavis-Google_Access\` | nu sunt skill-uri; sunt **sursa** pe care skill-urile o verifică (`scripts\ga-doctor.mjs`, `scripts\probe-mcp-stdio.mjs`, `container\`, `google-layer\`) |
| Skill-urile personale (1.308 la `C:\Users\apviz\.minimax\skills\`) | sunt indexate de `mavis-skill-index`; aici sunt doar cele care ating acest ecosistem |
| `notebooklm-mcp` | e pachetul pe care îl rulează **Hermes**, fără configurație și fără credential. **Deliberat nu** e o capabilitate minimax. Duplicarea e corectă; partajarea nu. |

---

## 5. Cum verifici totul, dintr-o comandă

```powershell
# 1. registrul botului
node "C:\Users\apviz\.minimax\agents\mavis\skills\mavis-google-access-bot\scripts\bot-registry.mjs" verify

# 2. fiecare membru, unul câte unul
$s = "C:\Users\apviz\.minimax\agents\mavis\skills"
Get-ChildItem "$s\mavis-skill-*\scripts\verify-*.mjs" | ForEach-Object {
  Write-Output ("--- " + $_.Directory.Parent.Name)
  node $_.FullName
  Write-Output ("exit=" + $LASTEXITCODE)
}

# 3. sistemul însuși
node "C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\Mavis-Google_Access\scripts\ga-doctor.mjs"
```
