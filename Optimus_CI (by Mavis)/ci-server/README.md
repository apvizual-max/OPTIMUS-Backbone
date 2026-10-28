# Mavis-Optimus-CI — serverul de Continuous Integration

Sursa containerului care tine toata data git locala a proiectului Optimus CI
si o sincronizeaza cu GitHub.

| Fisier | Ce e |
|---|---|
| `Dockerfile` | imaginea (node:22-slim + git + PowerShell 7) |
| `gitconfig` | configul de sistem al gitului in container (autocrlf, ca pe host) |
| `engine/lib.mjs` | primitive: git cu --git-dir/--work-tree, token, evidenta |
| `engine/engine.mjs` | motorul: doctor, plan (pre-flight), sync, arm-r0, push |
| `engine/cli.mjs` | CLI + serverul HTTP pentru plugin |
| `engine/entrypoint.sh` | instaleaza hook-urile portilor in gitdir-uri |
| `hooks/pre-commit` | poarta de secrete (sursa canonica, versionata) |
| `hooks/pre-push` | delegator catre poarta comuna de push (R0) |
| `gate/pre-push` | oglinda exacta a portii comune (bit-identica) |
| `bootstrap.ps1` | pornire completa in 5 minute (host) |
| `request-push.ps1` | armeaza acordul R0 (host) |

Arhitectura completa: `docs\CI-SERVER.md` (in proiect).
Skillul de operare: `mavis-optimus-ci-server-skill`.
Pluginul (MCP): `~/.minimax/skills/optimus-ci-server/`.

## Pornește

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File ".\bootstrap.ps1"
```
