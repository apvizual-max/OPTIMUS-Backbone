# Handoff către Local — 2026-10-12

## F4 rezolvat
`build-dashboard.py` retras → **`build-dashboard-legacy.py`**, scrie acum
`dist/dashboard-legacy.html`. **`build-hub.py` e singurul autorizat** să
scrie `dist/index.html`.

Verificat: `index.html` 58.350 B intact, legacy 24.895 B.

## Portabilitate
Varianta cloud nu are `CALE_REPO` — rulează curat.
**La tine**: `stare_repo()` trebuie să nu crape când `os.path.isdir(cale)`
e fals → fallback pe `git ls-remote origin`. Nu am atins-o, nu o am văzut.

## TASK-001
Nu e încă în `QUEUE/TASKS-FOR-CLOUD.md`. Comitează-l când vrei.

## Deploy
NEEXECUTAT. Blocat fără R0 de la Popy.
