# 21 · GOOGLE ACCESS BOT

**Folderul principal al accesului Google pentru Mavis Cloud.** Botul, capabilitățile
măsurate, transcriptul sesiunii și ghidul de workflow.

> Botul ca skill: `mavis-cloud-google-access-bot` (în `.skills/`).
> **Acesta e folderul principal de referință pentru tot ce lucrăm de acum încolo
> pe tema Google.** Drive: `Mavis-Cloud-Google-Access-Bot`
> (`1UQIxhctyJxBXIIFnpxSc5Jd0wvFxEylu`).

---

## Conținut

| Fișier | Ce |
|---|---|
| `CAPABILITATI-GOOGLE.md` | matricea **măsurată** (36 de teste, apeluri reale) |
| `GHID-WORKFLOW.md` | ce se poate construi ACUM, pe ce fundație |
| `TRANSCRIPT-SESIUNE-2026-10-28.md` | conținutul discuției + jurnalul deciziilor |
| `COMUNICARE/CANAL.md` | protocolul canalului cu agentul local |
| `EVAL-SKILL-VS-BASELINE.md` | evalul skill central vs baseline + ce a scos la iveală |
| `COMUNICARE/2026-10-28-001-*.md` | mesajele din canal |
| `probe/` | rezultatul brut al probe-ului (JSON) |

## Skill-urile

Central: **`.skills/mavis-cloud-google-access-bot/`** — reguli absolute, starea
măsurată, stack-ul de conectare, indexul de capacități, folderele Drive,
procedura de extindere.

Secundare (fiecare = o capacitate, indexate în central):

```
mavis-cloud-skill-drive            mavis-cloud-skill-gmail
mavis-cloud-skill-calendar         mavis-cloud-skill-sheets
mavis-cloud-skill-slides-docs      mavis-cloud-skill-notebooklm
mavis-cloud-skill-auth-lifecycle   mavis-cloud-skill-verification
mavis-cloud-skill-security         mavis-cloud-skill-sync-bridge
```

## Starea (2026-10-28)

- App OAuth: **„In production"** → fără limită de 7 zile.
- **27 scope-uri**, listă canonică unică: `mavis-tools/google-scopes.js`.
- Drive **100%** · Gmail **complet** (cu filtre) · Calendar **complet** ·
  Sheets **complet** · Slides **cu scriere** · Docs **prin conversie Drive**.
- **Probe: 36 OK · 0 blocate · 2 eșuate (din 38)** — cele 2 eșecuri = Docs API
  direct blocat de anti-bot; workaround-ul trece.
- NotebookLM: **fără API oficial** pentru cont normal → 3 căi, decizie la POPY.

## Comenzi

```bash
node mavis-tools/google-preflight.js       # 6 pași: conexiune, expirare, drift scope-uri
node mavis-tools/google-verify.js          # ce servicii merg acum
node mavis-tools/google-capabilities.js    # 36 de teste cu dovezi pe Drive
node mavis-tools/google-scopes.js          # lista canonică + motivele
node mavis-tools/google-refresh.js link    # regenerează linkul de autorizare
```

---

*Actualizat la 2026-10-28 · Mavis Cloud · tot ce aici e măsurat, nu estimat*
