# Puntea Mavis Cloud ↔ Mavis Local

> **Scop:** să lucrăm împreună pe același proiect, cât mai autonom, cu un singur
> buton de comandă din ambele părți, și cu **repo-ul ca singură sursă de adevăr.**

---

## Principiul

**Repo-ul este puntea.** Nu un server, nu un webhook, nu un API custom.
`apvizual-max/MAVIS-CLOUD` — ambii agenți citesc și scriu acolo.

```
   Mavis Cloud (server MiniMax)        Mavis Local (calculatorul lui POPY)
            │                                      │
            │  git push                          │
            ├──────────────────────────────────────►│
            │                                      │ git pull
            │◄──────────────────────────────────────┤
            │  git pull                           │
   (următorul pas)                                 │ (aici se face producția)
```

## De ce repo, nu altceva

| Alternativa | De ce nu merge |
|---|---|
| Server custom | trebuie întreținut, costă, pica odată |
| Webhook | un singur sens, nu are coadă, nu are istoric |
| Google Sheets drept punte | nu are diff, nu are istoric, se suprascrie |
| **GitHub** | **diff, istoric, ramuri, rollback, gratuit, deja funcționează** |

## Cum se comută între ei

**Protocolul, în trei rânduri:**

1. **Cerințele** intră în `docs/INTENTII.md`
2. **Iese din repo** în forma concretă: date, fișiere, cod
3. **Fiecare parte trece prin git**, pe `main`, fără ramuri

**Cine poate scrie:** amândoi. **RISC:** ediții concurente pe același fișier.
**Mitigare:** `git pull` înainte de orice scriere, obligatoriu.

## Comanda unică

Pentru **oricare agent, fără memorie, fără context:**

```
git clone https://github.com/apvizual-max/MAVIS-CLOUD
cd MAVIS-CLOUD
cat AGENTS.md docs/HANDOFF-COMPLET.md docs/DEFINITIE-OPERATIONALA.md
```

**Trei fișiere. Știi tot.** Nu ai nevoie de nimic altceva.

## Comanda zilnică a fiecăruia

### Mavis Cloud (eu)
```bash
cd /workspace/Mavis
git pull origin main          # ia ce a scris Local
# ... lucrez: cercetare, date, CV-uri, rapoarte ...
git add -A && git commit -m "..."
git push origin main          # împing fără întrebări
```

### Mavis Local
```bash
cd ~/Mavis
git pull origin main          # ia ce am scris eu
# ... lucrez: cod, site, fișiere, deploy local ...
git add -A && git commit -m "..."
git push origin main
```

## Fluxul unei sarcini zilnice

```
1. POPY scrie ce vrea în INTENTII.md
2. Mavis Local face pull, citește, vede că e cerință de date
3. Mavis Local scrie: "ne trebuie 7 joburi de la X, Y, Z"
4. Mavis Cloud face pull, citește, CULEGE joburile, aplică scoring
5. Mavis Cloud scrie datele + CV-urile în repo și pe Drive
6. Mavis Cloud face push, scrie în INTENTII.md ce a livrat
7. Mavis Local face pull, ia CV-urile, le pregătește pentru aplicație
8. POPY deschide Drive, trimite cu mâna lui
```

**POPY nu face niciun pas intermediar.** Doar scrie ce vrea și trimite ce primește.

## Ce face Cloud și ce face Local — fără suprapunere

| Cloud (eu) | Local |
|---|---|
| Culeg joburi de pe web | Editează fișiere |
| Aplic scoring | Scrie cod |
| Scriu CV-uri și scrisori | Modifică site-ul |
| Compar, sintetizez, raportez | Face deploy local |
| Prelucră grele, rulează în fundal | Interacționează cu browserul lui |
| Accesez API-uri Google | Ține fișiere pe disc |

## Autonomia maximă

**Ce nu are nevoie de aprobare:**
- orice schimbare de fișier în repo
- orice commit pe `main`
- orice push
- orice document nou
- orice actualizare de `PROGRES.md` sau `TODO.json`

**Ce cere POPY explicit:**
- deploy (creează site nou)
- ștergere definitivă
- trimitere de email în numele lui
- prețuri publice

## Ce trebuie construit de Local

Fișierul de pornire. **Unul singur**, pe calculatorul lui:

```bash
#!/usr/bin/env bash
# ~/mavis-sync.sh — pornit o dată, merge singur
while true; do
  cd ~/Mavis
  git pull origin main
  # ... dacă e cerință nouă în INTENTII.md, o execută ...
  git add -A && git commit -m "local: $(date '+%H:%M')" 2>/dev/null
  git push origin main 2>/dev/null
  sleep 300
done
```

**POPY nu are nevoie să știe git.** doar pornește scriptul o dată.

## Riscuri și cum sunt tratate

| Risc | Tratament |
|---|---|
| Editare concurentă pe același fișier | `git pull` obligatoriu înainte de scriere |
| Conflict de merge | `git pull` înainte de `push`; dacă nu merge, se oprește și se raportează |
| Un agent moare în mijloc | nimic necomandat se pierde; `git pull --abort` și reluat |
| Repo-ul devine haos | `docs/CI-NOTES.md` — un commit, o treabă |
| Rate limit pe API | quota manager cu backoff exponențial |

## Cum verificăm că funcționează

1. Cloud scrie un fișier de test, face push
2. Local face pull, verifică că îl are
3. Local scrie înapoi, face push
4. Cloud face pull, verifică

**Un test de 2 minute. Îl face Local la prima rulare.**