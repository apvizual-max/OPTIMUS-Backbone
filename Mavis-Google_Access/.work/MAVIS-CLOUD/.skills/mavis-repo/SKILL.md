---
name: mavis-repo
description: Reguli pentru lucrul in repo-ul Mavis - cum se face commit, cine decide ce, cum se pastreaza autonomia.
---

# Lucrul in repo-ul Mavis

## Cine decide ce

**Poți decide singur:**
- ordinea pașilor din `PLAN.md`
- structura unui CV, tonul unei scrisori
- ce câmpuri lipsesc din scoring și cum le adaugi
- când un proces de Gmail e lent sau riscant

**Întreabă înainte:**
- orice nume de client care nu apare în CV-urile reale
- prețuri care ajung publice
- orice trimitere în numele lui Alexandru
- orice ștergere definitivă
- identitatea vizuală: logo, culori, ton

## Git

```bash
cd /workspace/Mavis
git add -A
git commit -m "ce s-a facut, intr-o linie"
git push origin main
```

- **`main` direct. Fără ramuri**, fără excepție — ramură doar dacă POPY cere.
- **Comit și push FĂRĂ aprobare.** POPY a cerut explicit (2026-10-22):
  *„niciodată să ceri permisiune pentru comit și push, orice lucru am face"*.
  **Nu cere confirmare după commit.** Împinge și raportează.
- **Un livrabil care stă doar în conversație e un livrabil pierdut.** Fiecare
  document, cod, status, plan intră în repo, în folderul potrivit
  (`NN-AREA/`, `docs/`, `mavis-tools/`), în același commit cu munca.
- `PLAN.md` și `PROGRES.md` se actualizează în același commit ca munca.
- Nu comite: tokenuri, `.env`, `oauth.json`, `node_modules`, loguri.
- Repo-ul este **public** (2026-10-22), ca aplicațiile conectate să-l analizeze.
- **Structura:** `18-GOOGLE/` = setupul Google · `19-GDRIVE/` = operațiile pe
  Drive · `20-TO-DOs/` = working folder-ul lui POPY (taskuri pe care nu le pot
  rezolva singur; metoda: logica ∩ rațiune ∩ strategie).
- **Re-autentificarea e cu un singur scriitor** — `prompt=consent` revocă
  tokenul precedent și omoară celelalte sesiuni.

## Livrarea valorilor care vin din secret manager

Platforma **maschează** valorile din secret manager în mesajele de chat:
`{{ARCHON_SECRET:NUME}}`. Un link cu `client_id` trimis în chat ajunge în
browser cu placeholder → *Error 401: invalid_client*. Măsurat 2026-10-22.

**Regula:** identificatorii publici (`client_id`, project number) stau în repo,
ca sursă unică. Scriptul generează artefactul în repo. Livrezi **URL de repo**.
Secretele intră în panoul de secrete sau prin tool-ul `secret` — **niciodată în
chat**.

Detalii: skill `mavis-secure-delivery` · doc `docs/PROCEDURA-LIVRARE-SECRETE.md`.

## Ce nu intră niciodată

Parole, tokenuri, chei. Stau în managerul de secrete. În repo intră doar `.gitignore`
care le acoperă. Verifică înainte de orice commit:

```bash
git diff --cached --name-only | grep -iE "secret|token|credential|\.env|\.key|oauth"
```

Dacă iese ceva, **nu comita**.

## Autonomie

- Nu lăsa procese în fundal după ce ai terminat
- Nu lăsa fișiere în plus în afara `.gitignore`
- Lasă loguri citibile, nu procese orfane
- Numerele din `PROGRES.md` se scriu numai dacă le-ai numărat

## Cele două oferte, nu le amesteca

**B2B** = freelancing. Se vinde serviciul, cu preț.
**AP-ID Systems** = oferta AI. Se vinde sistemul: clientul pune un agent AI între
el și Mavis, ca furnizor de direcție artistică.

Sunt două cumpărători diferiți. Alegerea e a lui Alexandru, nu a mea.

## Push — comanda care merge

```bash
cd /workspace/Mavis
export GH_TOKEN="${GITHUB_TOKEN}"
export GIT_TERMINAL_PROMPT=0
git push origin main
```

`http.sslVerify=false` e setat global: sandboxul are un proxy care curl îl onorează,
dar git nu. Certificatul real e valid (openssl: `Verify return code: 0`).
`gh` stă în `mavis-tools/bin/gh`, nu în PATH — îl cheami cu calea plină.

## HARTA VIZIBILITATE — starea repo-urilor

| Repo | Stare | Ce e |
|---|---|---|
| `MAVIS-CLOUD` | **public** | proceduri, skill-uri, unelte, bridge Local↔Cloud |
| `pkms-vault-automation` | **public** | motorul vaultului, indexurile, docurile AI-Kit |
| `hermes-doctor` | **public** | unelta de diagnostic |
| `MAVIS-OPTIMUS-CI` | **public** | integrarea continuă |
| `OPTIMUS-Backbone` | **public** | backbonele sistemului |
| `Optimus-Mavis-Skills` | **public** | skill-urile vii |
| `hermes-local-backup` | **public** | config Sentinel, `SOUL.md`, jurnal operațional, cron, MCP |
| `hermes-agent-temp` | **privat** | oglindă proiect OSS + istoric cu secrete |
| `Qwen-Ecosystem-Dashboard` | **privat** | back-up de sesiune, transcripte, media |
| `SENTINEL_PRIME` | **privat** | corpus de conversații, frame-uri video |

Audit: `docs/AUDIT-VIZIBILITATE-REPO-URI.md`.
**Regula:** înainte de a schimba vizibilitatea → audit complet (istoric +
toate ramurile). Vezi skill-ul de git, secțiunea „AUDIT VIZIBILITATE".
