# Handoff către Local — 2026-10-12

## PR #4 — închis
`gh pr close 4` + branch șters. **Zero PR-uri deschise.**
Precedent: binare și tarball-uri nu se comitează.

## `SITE/date/repos.json` — gata
4 repo-uri cu ramura per repo. **Vault e pe `master`.**
Remote-urile sunt URL-uri simple, nu markdown — JSON valid pentru build.

Pentru tine:
```powershell
.\scripts\mavis-sync.ps1
python SITE\build-hub.py
```
`build-hub.py:13` citește încă hardcodat un singur repo — înlocuiește
cu citirea din `repos.json`, per repo: hash, ramură, sync, fișiere urmărite.

## `QUEUE/` — versionat
`TASKS-FOR-CLOUD.md` + `DONE/`. Pune prima sarcină de test când vrei.
`scope: local` → nu începe, scrie handoff.

## Deploy
NEEXECUTAT. Blocat fără R0 de la Popy.
