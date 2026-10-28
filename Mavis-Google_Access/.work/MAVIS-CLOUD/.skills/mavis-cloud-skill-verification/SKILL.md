---
name: mavis-cloud-skill-verification
description: Cum verifica Mavis Cloud o capacitate inainte sa o afirme - probe de capabilitate, verificare de servicii, preflight, numarare exacta si audit de repo-uri. Trigger-uri: "verifica", "functioneaza", "probe", "audit", "confirma", "demonstreaza", "nu raporta fara verificare".
---

# Verificare — nu afirma, măsoară

## Regula

**Nu raportez o capacitate fără un apel real care o dovedește.** „Ar trebui să
funcționeze" nu e un rezultat. Un HTTP 200 e.

Când am verificat filtrele Gmail la 27 oct, primele mele le-am numit „intacte" —
**erau moarte de 16 zile.** Le-am văzut abia după ce am citit raportul zilnic și
am comparat cu starea live. Verificarea făcută *la momentul potrivit* a rămas
la o eroare de 5 ore.

## Cele 3 niveluri

### 1. Conexiune — `google-preflight.js`
6 pași: client, credentiale, token, expirare, drift scope-uri. Răspunde
„e conectat?" și „e încă Testing?". **Rulează la începutul fiecărei sesiuni.**

### 2. Servicii — `google-verify.js`
Apeluri reale pe fiecare serviciu (Drive about, Gmail profile, Calendar list,
Sheets read, Slides read, Docs export, Photos, Maps). Nu verifică scope-uri —
verifică **funcționare**. Ultimul rezultat: **9 OK · 1 blocat · 1 eșuat**.

### 3. Capacitate de scriere — `google-capabilities.js`
**38 de teste** (36 OK · 0 blocate · 2 eșuate — ambele = Docs API direct
blocat de anti-bot), cu dovezi păstrate pe Drive în folderul `_PROOF`. Cele care
contează: create, update, delete, move, share, copy, trash+untrash, draft,
batchModify, filter create+delete, event create/update/delete, sheet
write/append, slide create+text, Docs convert.

```bash
node mavis-tools/google-capabilities.js
node mavis-tools/google-capabilities.js --parent <folderId>
```

**Probe-ul lasă dovezi pe Drive** (dosare, fișiere, spreadsheet, prezentare,
Google Doc nativ) și curăță **doar artefactele tranzitorii proprii** (draft,
eveniment, filtru throwaway, permisiune temporară).

## Capcane de măsurătoare

- **`resultSizeEstimate` e plafonat** (201 pentru orice). Numără cu paginare.
- **Nu număra în timp ce rulează altă operațiune Gmail** — contorul se ciocnește
  și raportează 0 când sunt mii. Zero = „n-am putut măsura", nu „nu există".
- **Nu presupune că un folder gol e un folder fără conținut** — verifică
  copilii prin `q='<id>' in parents`.
- **Testul prin „eșec" e incomplet**: un 403 poate însemna scope lipsă **sau**
  API blocat din cloud. Distinge după forma răspunsului: JSON cu
  `PERMISSION_DENIED` = scope; **HTML** = blocare de rețea/robot.
- **Un API poate fi parțial**: Docs API direct e blocat (HTML), dar Drive
  export merge. Nu generalizezi dintr-un eșec.

## Audit de repo-uri și secrete

Când schimbi vizibilitatea unui repo:
```bash
git fetch --unshallow          # un clone --depth 1 ascunde exact ce cauți
git log --all --oneline        + toate ramurile
```
Apoi: **valoare de secret într-un repo public → nici revocată, nici de rotit.**
Doar prefix + referință la secret manager. GitHub secret-scanning blochează
push-ul și **are dreptate**.

**Verifică dacă o valoare e vie**, nu doar prezentă:
- refresh token → `POST oauth2.googleapis.com/token` (200 = vie)
- cheie API → `GET discovery/v1/apis?key=` → **400 = moartă, 403 = vie**

Revocare fără credențiale: `POST https://oauth2.googleapis.com/revoke?token=...`

## Rezultatul unui eval (28 oct 2026) — de ce contează

Agentul **fără** skill a raportat că Sheets `values/{range}` dă 400 cu HTML
(„folosește batchUpdate obligatoriu") — **fals**, probe-ul dă 200 consistent.
A raportat și că a trimis un email de test — **`in:sent` = 0**, nu s-a întâmplat.
Și a lăsat fișiere în Drive-ul lui POPY.

Cu skill: aceleași concluzii, dar **verificate**, plus un efect colateral — a
găsit o listă de scope-uri hardcodată în `google-preflight.js` pe care eu o
lăsasem. **Skillul nu te apără doar de greșeli străine — te apără de ale tale.**

## Probe-uri care au costat timp — nu le mai repeta

| Eroare | Cauza reală |
|---|---|
| 400 „Filter doesn't have any actions" | acțiunea filtrului nu poate fi goală |
| 404 pe `users.drafts.modify` | endpointul nu e funcțional; folosește `messages.modify` |
| 400 „object ID length should not be less than 5" | Slides `objectId` ≥ 5 caractere |
| „The object does not allow text editing" | placeholder-ul e la `element.shape.placeholder` |
| „Unknown name 'size'" în `createShape` | altă formă de parametri; folosește layout predefinit |
| „Invalid JSON payload… Unknown name" | payload cu `transform` — neacceptat în această versiune |

## Legături

Skill central: `mavis-cloud-google-access-bot` · sibling: `mavis-cloud-skill-auth-lifecycle`,
`mavis-cloud-skill-security`
