---
name: mavis-cloud-skill-security
description: Cum livreaza Mavis Cloud valori sensibile fara sa le trimita prin chat, cum gestioneaza secretele, vizibilitatea repo-urilor si izolarea fisierelor tale. Trigger-uri: "secret", "parola", "api key", "token", "nu trimite in chat", "vizibilitate repo", "audit", "private", "public".
---

# Security — secrete, vizibilitate, izolare

## Regula #1 — nicio valoare de secret prin chat

Platforma **maschează** valorile din secret manager în `{{ARCHON_SECRET:…}}`.
Browserul primește placeholder → `Error 401: invalid_client`.

**Asta a fost cauza rădăcină a problemei inițiale de OAuth**, și a costat o
sesiune de diagnosticare. Se repară livrând prin repo:

1. Scriptul scrie valoarea într-un **fișier din repo**.
2. Scriptul **comitează și împinge singur** (fără permisiune).
3. Ii dai lui POPY **URL-ul de repo**, nu valoarea:
   `https://github.com/apvizual-max/MAVIS-CLOUD/blob/main/18-GOOGLE/AUTORIZARE-LINK.txt`

**Excepție — scrierea în secret manager:** tool-ul `secret` acceptă valoarea ca
argument. Acolo e calea corectă, pentru că nu iese în conversație.

**Client ID e identificator public**, nu secret. Stă în
`mavis-tools/google-client.json` — de proposit. `client_secret` și
`refresh_token` rămân în secret manager.

## Regula #2 — nicio valoare de secret într-un repo public

**Nici revocată. Nici de rotit.** Doar prefix + referință:
`AIzaSyAyimku…(restul in secret manager: GOOGLE_API_KEY_EXPOSED_HERMES_TEMP)`

**Măsurat 28 oct 2026:** am scris două refresh token-uri și o cheie API cu
valoarea completă într-un document dintr-un repo public. **GitHub secret
scanning a refuzat push-ul** — corect, și exact pentru motivul care contează.

Dacă ai scris deja o valoare reală într-un commit **neîmpins**:
```bash
git reset --soft HEAD~1      # nu a fost împins → nu există de șters
# redactează → git add -A → commit nou
```
Dacă ai **împins** deja: rescrie istoricul **și** roagă valoarea. Rotirea e
obligatorie oricum — rescrierea istoricului nu anulează o valoare deja clonată.

## Regula #3 — vizibilitatea repo-urilor

**Înainte de a schimba vizibilitatea: audit pe istoricul COMPLET.**
```bash
git fetch --unshallow
git log --all --oneline
```
Un clone `--depth 1` ascunde exact ce cauți.

**Starea la 28 oct 2026:**
- **7 publice:** `MAVIS-CLOUD` · `pkms-vault-automation` · `hermes-doctor` ·
  `MAVIS-OPTIMUS-CI` · `OPTIMUS-Backbone` · `Optimus-Mavis-Skills` ·
  `hermes-local-backup`
- **3 private:** `hermes-agent-temp` · `Qwen-Ecosystem-Dashboard` ·
  `SENTINEL_PRIME`

**Verifică dacă o valoare e vie**, nu doar prezentă — vezi
`mavis-cloud-skill-verification`.

**Fals pozitivuri confirmate** (nu te speria):
`ghp_xxxx…` · `GOCSPX-aaaa…` · `AKIAIOSFODNN7EXAMPLE` (cheia exemplu AWS) ·
`glpat-AbCdEf…` · `xoxb-your-slack-bot-token` · un șir `1//…` găsit **în
interiorul unui JPEG base64** · fixture-uri din auto-testul detectorului de
secrete.

## Regula #4 — izolarea fișierelor tale

Vaultul `GDrive-Second_Brain_PKMS` e read-only pentru cloud. 8 reguli
integrale în `19-GDRIVE/REGULI-VAULT.md`. Rezumat:

- **Nu șterge** nimic din vault.
- **Nu muți** nimic fără R0 (cerință explicită de la POPY).
- `00_INDEX.md` **nu se editează manual** — se generează.
- **Nu scrii** căi de referință cu mână.
- `Knights Templar` · `_SYSTEM` · `.obsidian` · `.trash` · `.vault-intelligence`
  · `.claudian` · `.neural_memory` — **neatinse**.

Singura excepție la scriere: `drive-vault.js quarantine` — care **mută** (nu
șterge) și cere `--confirm` + motiv scris.

## Regula #5 — GitHub Actions

Workflow-ul nu rulează pe `pull_request` → secretul nu e accesibil dintr-un
PR. **Nu adăuga `pull_request_trigger` la workflow-uri care materializează
secrete.**

## Legături

Skill central: `mavis-cloud-google-access-bot` · sibling: `mavis-cloud-skill-auth-lifecycle`,
`mavis-cloud-skill-verification`
