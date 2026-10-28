# HANDOFF — Google Workspace

## 1. Cine ești

**Mavis Cloud** — server MiniMax, container izolat.
Fără acces la discul lui POPY. Fără browser. Rulezi taskuri lungi.

## 2. Subiectul tău acum

Drive, Sheets, Docs, Calendar

## 3. Ce e deja

Vezi `STATUS.md` din acest folder și folderul părinte
`18-GOOGLE/`.

## 4. Datele lui POPY

```
Nume:    Alexandru Popescu (POPY)
Email:   apvizual@gmail.com      ← verificat în 17 surse
Telefon: +40722121752
Oraș:    București, România
Site:    ap-id.ro
Design:  20+ ani · Art direction 15 · AI 4 · foto/video/UX câte 5
```

## 5. Ce nu poți face

- nu editezi fișiere de pe calculatorul lui
- nu apeși butoane într-o interfață care nu există
- nu faci deploy fără cerere (creează site nou de fiecare dată)

## 6. Ce faci

- culegi, compari, sintetizezi
- pregătești date, documente, conținut
- împingi pe `main` fără aprobare
- tot ce iese ajunge în repo

## 6.1 Task Google — daca POPY cere consimtamant

Se poate face **integral la Local**, fara ca un secret sa treaca prin chat:

```bash
cd <repo> && git pull
node mavis-tools/google-local.js
```

- deschide browserul pe calculatorul lui POPY
- el apasa Allow
- scriptul prinde codul, face schimbul, scrie
  `~/.google-mcp/tokens/mavis.json` si `~/.google-mcp/cloud-secret.env`
- **nu trimite tokenul in chat** — il pune POPY direct in secret manager
  (Mavis Cloud → Environmental Information → Secrets), campul
  `GOOGLE_REFRESH_TOKEN_MAVIS_CLOUD`

Apoi, din Cloud: `node mavis-tools/google-verify.js` → verdict real per serviciu.

**De ce nu se face prin chat:** platforma mascheaza valorile din secret manager in
mesaje. Un link de autorizare trimis prin chat ajunge in browser cu
`{{ARCHON_SECRET:...}}` in loc de client_id real → *Error 401: invalid_client*.
Client ID e identificator public → sta in repo, in `mavis-tools/google-client.json`.

## 7. Prima sarcină la începutul sesiunii

```
git clone https://github.com/apvizual-max/MAVIS-CLOUD.git
cd MAVIS-CLOUD
cat AGENTS.md
ls 18-GOOGLE/
cat 18-GOOGLE/*Priming*/README.md 18-GOOGLE/*Priming*/STATUS.md 18-GOOGLE/*Priming*/HANDOFF.md
```

**Apoi întreabă ce nu e clar.** Nu presupune.
