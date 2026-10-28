# Handoff — Google Access

Pentru o sesiune cu **0 context și 0 memorie**.

| Citește | când |
|---|---|
| **[PRIMING-PROMPT.md](PRIMING-PROMPT.md)** | **primul** — e promptul de pornire, copiabil |
| [HANDOFF-GOOGLE-ACCESS.md](HANDOFF-GOOGLE-ACCESS.md) | apoi — handoff-ul complet: contract, proceduri, limite |
| [SKILLS-INDEX.md](SKILLS-INDEX.md) | ce skilluri există și ce deține fiecare |
| [STATE-MEASURED.md](STATE-MEASURED.md) | starea cu cifre și cu dată |
| [MANIFEST.json](MANIFEST.json) | indexul machine-readable |

**O singură comandă spune dacă totul e în picioare:**

```powershell
node "C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\Mavis-Google_Access\scripts\ga-doctor.mjs"
```

Starea la predare (2026-10-28 00:48Z): `SUMMARY checks=11 failed=0 warnings=0`
· `VERDICT=PASS` · exit 0.

## Ce trebuie să știi înainte de orice altceva

1. **Nu reconstruiește nimic.** Conectarea există, rulează singură și se
   verifică cu o comandă.
2. **Singurele două lucruri care nu merg** sunt `keep` (403 — Google nu
   publică scope acordabil) și `sites` (404 — API retras). **Nu sunt defecte**,
   sunt decizii, și Popy le importă prin alte unelte în Drive.
3. **Singurele două acțiuni umane** rămase: clickul de consimțământ (doar când
   Google îl cere) și alegerea pozelor în Photo Picker.

## Botul central și membrii lui

```
C:\Users\apviz\.minimax\agents\mavis\skills\mavis-google-access-bot\
  SKILL.md            rolul, contractul, lista, bucla de actualizare
  SPEC.md             contractul tehnic: forma unui membru, schema registrului
  registry.json       lista machine-readable: membri + referințe + roadmap
  scripts\bot-registry.mjs   list · verify · show · link
  scripts\log-run.mjs        înregistrează o rulare în `runs.md`
  scripts\log-run-selfcheck.mjs   auto-proba loggerului (fixture, nu atinge loguri reale)
  logs\bot-runs.md           jurnalul propriu al botului
```

```powershell
node "C:\Users\apviz\.minimax\agents\mavis\skills\mavis-google-access-bot\scripts\bot-registry.mjs" list
node "C:\Users\apviz\.minimax\agents\mavis\skills\mavis-google-access-bot\scripts\bot-registry.mjs" verify
```

## Regula de măsurătoare (aici s-a câștigat timp)

La finalizarea punctului de control au ieșit la iveală patru defecte care
stăteau de săptămâni și **nu se vedeau**:

- trei intrări MCP rupte de o mutare de folder (registry-ul spunea „enabled");
- un server MCP care indica spre un wrapper pe care npm nu l-a creat niciodată;
- **trei optimizări fuzionate pierdute într-o mutare** — fișierele erau
  prezente, dar mai vechi;
- o sesiune Photo Picker **consumată**, raportată ca defect.

Deci: **măsoară, nu presupune.** Un fișier prezent nu e o migrare. O cale
moartă într-un registry nu e o înregistrare. O sesiune consumată nu e o
defecție.
