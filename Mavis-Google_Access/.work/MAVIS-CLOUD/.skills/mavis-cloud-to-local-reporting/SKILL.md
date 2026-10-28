---
name: mavis-cloud-to-local-reporting
description: Procedura prin care Mavis Cloud citește starea containerului, procesează QUEUE/, arhivează rapoartele vechi și redactează rapoarte datate pentru Local, împingând pe main.
---

# mavis-cloud-to-local-reporting

Container Linux, efemer. Împing direct pe `main`, fără R0.

## Ordinea

1. `git pull --rebase origin main` — **mereu primul**. TASK-urile vin de aici.
2. Citește `QUEUE/TASKS-FOR-CLOUD.md`
3. Execută tichetele cu `scope: cloud`
4. Scrie rezultatul în `QUEUE/DONE/<id>.md`
5. Marchează `[x]` în coadă
6. **Nu șterge nimic** — mută în `docs/arhiva/handoffs-vechi/` cu `git mv`
7. Scrie raportul datat în `docs/`
8. Verificări pre-push, apoi push

## Verificări obligatorii înainte de push

- [ ] `git log origin/main..HEAD` gol după push
- [ ] fișierele protejate **neatinse**:
      `REGULI-PLATFORMA.md` · `DEFINITIE-OPERATIONALA.md` · `BRIDGE.md` ·
      `JULES-INSTRUMENTARE.md` · `TODO.json` · `LOG-SISTEM.json` ·
      `MANUAL DE NAVIGARE - cotor.md` · `SITE/date/` ·
      `ALEX-KIT/TEMPLATES-POPY/`
- [ ] `python3 SITE/build-hub.py` rulează
- [ ] JSON-urile parsează

## Non-trunchiere

Un raport se **trunchiază la citire**, niciodată la scriere.
Când citești un fișier lung și vezi doar începutul, **citește tot**
înainte să concluzionezi. Concluzia dintr-un fișier citit pe jumătate
e exact tipul de eroare care se repetă.

## Portea R0

**Aplicată în sens invers.** Local are R0 înainte de push.
Cloud nu cere R0 — împinge direct, containerul e volatil.

**Dar:** pentru **PR-uri deschise de Jules**, decizia e a lui Local.
Cloud **nu** comentează, **nu** face merge, **nu** închide.

## Ce nu fac

- nu șterg definitiv — mut în `docs/arhiva/handoffs-vechi/`
- nu ating fișierele protejate
- nu creez fișiere „de pregătire" nesolicitate
- nu împing PR-uri străine
- nu pun secrete în repo

## Surse de adevăr

- `.skills/mavis-cloud-to-local-reporting/SKILL.md` — asta
- `docs/STATUS-CLOUD-TO-LOCAL-YYYY-MM-DD.md` — predare reciprocă
- `QUEUE/TASKS-FOR-CLOUD.md` — singura cale de intrare sigură

## Cron

Cronurile de container sunt pe **platforma online**.
Nu în interfața Local. Dacă nu le vezi acolo, nu sunt ale tale.