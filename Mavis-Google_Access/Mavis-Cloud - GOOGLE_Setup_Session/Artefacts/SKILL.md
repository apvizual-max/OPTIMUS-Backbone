---
name: mavis-secure-delivery
description: Cum livrezi o valoare care vine din secret manager fara sa o trimiti prin chat. Platforma o mascheaza in {{ARCHON_SECRET:...}} si livrezarea se strica. Reguli, procedura si teste.
---

# Livrare fără secrete — procedura care merge

## Regula, într-o propoziție

**O valoare care vine din secret manager nu trece prin chat.**
Platforma o înlocuiește cu `{{ARCHON_SECRET:NUME}}` în mesajele mele.
Ce ajunge la om e un placeholder, nu valoarea.

## Cum arată simptomul

| Ce am trimis | Ce a ajuns | Ce a răspuns destinatarul |
|---|---|---|
| link OAuth cu `client_id` real | `client_id=%7B%7BARCHON_SECRET%3A...%7D%7D` | *Error 401: invalid_client* |
| cheie API în chat | `{{ARCHON_SECRET:API_KEY}}` | „nu merge" |
| URL cu token | `{{ARCHON_SECRET:TOKEN}}` | 401 / invalid_grant |

**Nu da vina utilizatorului și nu schimba credentialele.** Verifică mai întâi
dacă valoarea pe care i-ai dat-o era deja mascată. Costă o oră de diagnostic
pe 2026-10-22.

## Testul: e mascat sau e real?

```bash
# 1. valoarea reala (din env) — se vede corect
node -e 'console.log(process.env.GOOGLE_CLIENT_ID_MAVIS_CLOUD)'
# 2. aceeasi valoare scrisa in mesajul de chat -> {{ARCHON_SECRET:...}}
```

Dacă (1) e plin și (2) e placeholder → **livrare mascată**, nu credential greșit.

## Procedura corectă (asta a mers)

1. **Ce valoare e secretă?**
   - `client_secret`, `refresh_token`, `access_token`, parole, API keys → **secret**
   - `client_id`, project number, nume de etichetă → **identificator public** → poate în repo

2. **Identificatorii publici stau în repo**, ca sursă unică de adevăr.
   Exemplu: `mavis-tools/google-client.json`.

3. **Scriptul generează artefactul în repo**, nu în chat.
   Exemplu: `mavis-tools/google-link-file.js` → `18-GOOGLE/AUTORIZARE-LINK.txt`.

4. **Comit + push.** Fără aprobare. Regula lui POPY: *„nu cere permisiune pentru
   comit și push"*.

5. **Livreză un URL de repo**, nu valoarea:
   `https://github.com/<owner>/<repo>/blob/main/<cale>` — un URL nu conține
   secret și nu se maschează.

6. **Destinatarul copiază valoarea din pagină** și o întoarce prin canalul
   potrivit (chat: doar dacă nu e secret; panoul de secrete: dacă e secret).

7. **Eu scriu secretul în secret manager** cu tool-ul `secret` (create/update).
   Nu îl pun niciodată în chat nici în repo.

## Ce se poate cere prin chat, sigur

| Tip | Prin chat? |
|---|---|
| cod de autorizare OAuth (obiect temporar, nu e în secret manager) | ✅ da |
| numere, etichete, IDs, linkuri fără secret | ✅ da |
| `client_id`, project number | ✅ da (identificator public) |
| `client_secret`, `refresh_token`, parole, API keys | ❌ **nu** |

## Dacă secretul trebuie neapărat să ajungă la mine

Panoul de secrete al platformei (`secret` tool) e singura cale sigură.
Nu cer niciodată lui POPY să trimită un secret în chat.

## Anti-patternuri

- ❌ `Adresa este: https://...&client_id=1068987308935-...` în chat
- ❌ „am trimis codul, dă-mi și secretul"
- ❌ Fișier cu secrete pus în repo „temporar"
- ❌ URL cu token într-un mesaj de raport

## Verificare înainte de orice livrare

```bash
cd /workspace/mavis-cloud
node mavis-tools/google-preflight.js    # exemplu: client + token + retea
```

Dacă verdictul e „client la auth OK", **livreză prin repo**.
Dacă e „client la auth FAIL", problema e în credential, nu în livrare.

## Legături

- Skill: `google-cloud-auth` — aplicația concretă (OAuth Google)
- Skill: `sandbox-gotchas` — mascarea + proxy + `curl -k`
- Doc: `docs/PROCEDURA-LIVRARE-SECRETE.md` — procedura în format lung
