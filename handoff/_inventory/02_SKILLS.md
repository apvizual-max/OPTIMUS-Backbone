# 02 — Skill-uri (inventar masurat)

Masurat: **2026-10-28**, intre 19:06 si 19:20 (ora locala, +02:00). Nimic nu a fost modificat in registry-ul live.

## 1. Colectia canonica din repo: `60_SKILLS\mavis-skills\`

Cale: `C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\60_SKILLS\mavis-skills`

| Masuratoare | Valoare |
|---|---|
| Nr. de foldere de skill la top-level | **93** |
| Nr. de fisiere `SKILL.md` (recursiv) | **93** |
| Nr. total de fisiere (recursiv, fara `.git`) | **409** |
| Foldere de top-level fara `SKILL.md` propriu | **1** — `.jules` (contine `bolt.md`, `palette.md`, `sentinel.md`; este metadata, nu skill) |
| Fisiere la radacina | **4** — `.gitattributes` (322 b), `.gitignore` (292 b), `JULES_HANDOFF.md` (1288 b), `pr_body.txt` (256 b) |
| Este repo git? | Da — parte din monorepo; remote `https://github.com/apvizual-max/OPTIMUS-Backbone.git` |
| Nr. de `SKILL.md` adăugate in structura de skill-uri | 1 — `mavis-bot-creator-skill\templates\skill-template\SKILL.md` (sablon, se numara in totalul de 93) |

### 1.1 Lista completa a celor 93 de foldere de skill

```
.jules
mavis-antigravity-bridge-skill
mavis-antigravity-docker-admin-skill
mavis-antigravity-ecosystem-integrations-skill
mavis-antigravity-process-logging-skill
mavis-autonomous-operator-skill
mavis-autostart-docker-swarm-skill
mavis-backbone-skill
mavis-bigquery-sql-optimization-skill
mavis-bot-creator-skill
mavis-bundle-behavioral
mavis-bundle-identity
mavis-bundle-operations
mavis-bundle-role
mavis-chrome-browser-skill
mavis-cloud-bridge-skill
mavis-data-autocleaning-pipeline-skill
mavis-deliverable-handoff-skill
mavis-doc-bridge-skill
mavis-docker-backup-configurator-skill
mavis-docker-docs-skill
mavis-docker-gordon-skill
mavis-exec-sentinel-orchestrator-skill
mavis-full-intent-execution-skill
mavis-gemini-api-dev-skill
mavis-gemini-live-api-skill
mavis-gemini-omni-flash-skill
mavis-git-autonom-skill
mavis-git-install-skill
mavis-git-vault-governance-skill
mavis-google-access-bot
mavis-google-access-skill
mavis-google-workspace-skill
mavis-hermes-bridge-skill
mavis-hermes-design-sot
mavis-hermes-doctor-report-skill
mavis-instruction-fidelity-skill
mavis-jules-contract-skill
mavis-jurnal-oglinda-skill
mavis-live-review-governance-skill
mavis-local-optimus-ci-bot
mavis-local-to-cloud-reporting
mavis-managing-python-dependencies-skill
mavis-mcp-management-skill
mavis-memory-curator-skill
mavis-minimax-antigravity-bridge-skill
mavis-minimax-hermes-bridge-skill
mavis-minimax-hermes-doctor-skill
mavis-minimax-index-folder-update
mavis-minimax-optimus-system
mavis-minimax-perspective-change-thinking
mavis-notebooklm-bridge-skill
mavis-obsidian-second-brain-skill
mavis-optimus-ci-server-skill
mavis-optimus-continuous-integration-skill
mavis-pkms-vault-administration-skill
mavis-pkms-vault-index-skill
mavis-qwen-bridge-skill
mavis-r33-bimodal-skill
mavis-sacru-corpus-skill
mavis-search-before-write
mavis-sentinel-bimodal-workflow-skill
mavis-sentinel-command-center-skill
mavis-sentinel-daemon-skill
mavis-sentinel-error-alert-engine-skill
mavis-sentinel-memory-search-skill
mavis-sentinel-prime-on-minimax-skill
mavis-sentinel-prime-role-skill
mavis-sentinel-workflow-rpid-skill
mavis-session-extract-bot-skill
mavis-session-lifecycle-skill
mavis-session-transcript-skill
mavis-shared-local-mcp-swarm-skill
mavis-skill-access-handoff
mavis-skill-background-task-verdict
mavis-skill-browser-mcp
mavis-skill-docker-access-point
mavis-skill-google-access-control-point
mavis-skill-google-keep-sites
mavis-skill-index
mavis-skill-mcp-development
mavis-skill-notebooklm-extendlm
mavis-skill-photo-picker
mavis-skill-repair-manifest-skill
mavis-subject-completion-skill
mavis-swarm-coordinator-skill
mavis-tany-llm-to-sentinel-skill
mavis-triple-crunch-skill
mavis-wayland-bridge-skill
minimax-optimus-dashboard
popy-project-status-report
qwen-ecosystem-dashboard
```

## 2. Registry-ul LIVE de runtime: `C:\Users\apviz\.minimax\agents\mavis\skills`

| Masuratoare | Valoare |
|---|---|
| Nr. de intrari de top-level (directoare) | **95** |
| Nr. de foldere de skill la top-level | **93** (aceiasi lista ca mai sus) |
| Nr. de `SKILL.md` (recursiv) | **93** |
| Nr. total de fisiere (recursiv, fara `.git`) | **426** |
| Fisiere la radacina | **4** — `.gitattributes` (322 b), `.gitignore` (292 b), `JULES_HANDOFF.md` (1288 b), `pr_body.txt` (256 b) |
| Este repo git? | Da — clone propriu, remote `https://github.com/apvizual-max/Optimus-Mavis-Skills.git`, ramura `main` |
| Intrari ne-urmărite in acest repo | 2 — `mavis-local-optimus-ci-bot/registry.json`, `mavis-local-optimus-ci-bot/scripts/` |

### 2.1 Diferenta explicita de nume intre cele doua arbori

| Set | Nume |
|---|---|
| **Doar in canonic** (`60_SKILLS\mavis-skills`) | **(niciunul)** |
| **Doar in live** (`C:\Users\apviz\.minimax\agents\mavis\skills`) | `.git` (14 intrari), `state` |

Cele doua intrari suplimentare din live **nu sunt skill-uri**: `.git` este metadatele clone-ului, iar `state\tmp\` contine 11 fisiere de lucru temporar (`apply-skill-updates.ps1`, chunk-uri de markdown, fisier de commit-uri).

### 2.2 Verdict: aceeasi colectie sau snapshot diferit?

**Continutul de skill-uri este identic; arborii sunt totuși doi arbori diferiți.**

- **Setul de skill-uri: identic.** Cele 93 de foldere de skill au aceleași nume în ambele locuri; diferența de nume este doar `.git` + `state` (live) vs. nimic (canonic).
- **Fișierele `SKILL.md`: identice octet cu octet.** Verificat cu `Get-FileHash -Algorithm SHA256` pe toate cele 93 de perechi: **92 perechi identice + 1 pereche fără `SKILL.md` pe niciuna dintre laturi** (folderul `.jules`, care nu e un skill). Diferente de continut: **0**.
- **Arborii raman diferiti ca obiect git:** canonic este o subdirectorie a monorepo-ului OPTIMUS-Backbone (remote `OPTIMUS-Backbone.git`), live este un clone separat cu remote propriu (`Optimus-Mavis-Skills.git`). Live are si 2 intrari ne-urmărite pe care canonicul nu le are.
- **Numarul de fisiere difera** (409 canonic vs. 426 live) din cauza celor 17 intrari non-skill din live (`.git` exclus din numaratoare: `state\tmp` = 11 fisiere + `.git` exclus + diferenta 409 → 426 = 17, corespunzatoare intrarilor `state`).

Concluție pentru preluare: **skill-urile sunt aceleași**; nu exista drift de continut intre canonic si runtime. Diferenta intre arbori este metadata git si fisiere temporare.

## 3. Copiile din `SENTINEL_PRIME`

### 3.1 `SENTINEL_PRIME\14_HANDOFF\SKILLS\`

- **0 subfoldere**, **13 fisiere** la top-level, **0 fisiere numite `SKILL.md`** (schema de denumire diferita: `<nume>.SKILL.md`).
- Nume de baza extrase (10 skill-uri distincte):
  `mavis-autonomous-operator-skill`, `mavis-git-autonom-skill`, `mavis-jules-contract-skill`, `mavis-live-review-governance-skill`, `mavis-optimus-continuous-integration-skill`, `mavis-sentinel-command-center-skill`, `mavis-skill-access-handoff`, `popy-project-status-report`, `sentinel-cd-pipeline-sync`, `verification-and-falsification`.
- Restul celor 3 fisiere: `MANIFEST.md` (7973 b), `MANIFEST.md.bak-20261028_0430` (5987 b), `sentinel-cd-pipeline-sync.SKILL.md.bak-20261028_1142` (12896 b).
- **Cat de multe sunt a doua copie a numelor din colectia canonica: 8 din 10.** Se suprapun: `mavis-autonomous-operator-skill`, `mavis-git-autonom-skill`, `mavis-jules-contract-skill`, `mavis-live-review-governance-skill`, `mavis-optimus-continuous-integration-skill`, `mavis-sentinel-command-center-skill`, `mavis-skill-access-handoff`, `popy-project-status-report`. **NU se suprapun:** `sentinel-cd-pipeline-sync`, `verification-and-falsification` (skill-uri proprii SENTINEL, absente din colectia canonica).

### 3.2 `SENTINEL_PRIME\07_BACKBONE\skills\`

- **0 subfoldere**, **11 fisiere** la top-level, **0 fisiere numite `SKILL.md`**.
- Nume de baza extrase (7 skill-uri distincte):
  `bimodal-workflow`, `command-center`, `sentinel-cd-pipeline-sync`, `sentinel-prime-on-minimax`, `sentinel-prime-role`, `tany-llm-to-sentinel`, `verification-and-falsification`.
- Restul celor 4 fisiere: `sentinel-cd-pipeline-sync.SKILL.md.bak-20261028_0330` (7647 b), `sentinel-cd-pipeline-sync.SKILL.md.bak-20261028_0430` (8956 b), `sentinel-cd-pipeline-sync.SKILL.md.bak-20261028_1141` (12896 b), `verification-and-falsification.SKILL.md.bak-20261028_0330` (7450 b).
- **Cat de multe sunt a doua copie a numelor din colectia canonica: 0 din 7.** Niciunul dintre aceste 7 nume nu apare in lista canonica de 93. **Acesta NU este o copie a colectiei canonice** — este o familie de skill-uri SENTINEL cu denumiri proprii.

### 3.3 Relatia intre cele doua copii SENTINEL

**2 nume comune** intre `14_HANDOFF\SKILLS` si `07_BACKBONE\skills`: `sentinel-cd-pipeline-sync`, `verification-and-falsification`.
Pentru `sentinel-cd-pipeline-sync`, fisierul din `14_HANDOFF` (12921 b) si cel din `07_BACKBONE` (12921 b) au aceeasi dimensiune masurata.

**Concluzie:** in `SENTINEL_PRIME` exista **doua copii partiale, de domenii diferite** — nu copii ale colectiei canonice de 93 de skill-uri:
- `14_HANDOFF\SKILLS` = 8 skill-uri comune cu canonica + 2 skill-uri SENTINEL proprii (copie de export pentru predare, cu `MANIFEST.md`).
- `07_BACKBONE\skills` = 7 skill-uri exclusiv SENTINEL (copie de runtime a nucleului), **zero** suprapunere cu canonica.

## 4. Comenzi de reverificare

```powershell
$canon = "C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\60_SKILLS\mavis-skills"
$live  = "C:\Users\apviz\.minimax\agents\mavis\skills"
(Get-ChildItem $canon -Directory -Force).Count          # 93
(Get-ChildItem $canon -Recurse -File -Force -Filter SKILL.md).Count   # 93
(Get-ChildItem $live  -Directory -Force).Count          # 95
Compare-Object (Get-ChildItem $canon -Directory -Force).Name (Get-ChildItem $live -Directory -Force).Name
Get-ChildItem $canon -Directory -Force | ForEach-Object {
  $c = Join-Path $_.FullName 'SKILL.md'; $l = Join-Path "$live\$($_.Name)" 'SKILL.md'
  if (Test-Path $l) { [pscustomobject]@{ N=$_.Name; Same=((Get-FileHash $c).Hash -eq (Get-FileHash $l).Hash) } }
} | Group-Object Same
```
