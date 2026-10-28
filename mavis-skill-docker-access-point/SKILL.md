---
name: mavis-skill-docker-access-point
description: The Docker substrate of Google Access on this station - the one container that IS the access point. Load this when building, rebuilding, recreating, debugging or hardening the Google_Access container: the image build, the three volumes (data rw, secrets ro), the port rule, the healthcheck, the credential never in an image layer, and the measured procedure for a safe rebuild that never loses the grant. Also owns the rule that the running bytes must equal the repo bytes.
role: functional
bot: mavis-google-access-bot
---

# mavis-skill-docker-access-point

**Role.** The keeper of the container that *is* the access point. One container,
one credential, one endpoint. Everything else in this ecosystem talks to it
through `http://127.0.0.1:8766/mcp`.

---

## 1. Why it exists (the defect, not the preference)

Measured 2026-10-28: the repository carried a repair, the image had been built
**before** it, and the container was therefore running the **old code** — while
the doctor, the docs and the task all reported everything as fine. The system
was healthy and wrong at the same time.

Two lessons live in this skill:

1. **A healthy container proves it is alive, not that it is the thing you
   wrote.** The bytes must be compared.
2. **A file that is present but older is not a migration, it is a regression.**

---

## 2. The measured shape

| | |
|---|---|
| Container | `Google_Access`, image `google-access:1.0.9` |
| Restart policy | `--restart unless-stopped` |
| Port | `127.0.0.1:8766` → container `GA_PORT=8766` (loopback only) |
| Volume (rw) | `C:\Users\apviz\.minimax\google-access\data` → `/data` — holds the credential |
| Volume (ro) | `E:\--- System Secrets` → `/secrets` |
| Health | `http://127.0.0.1:8766/health` → `grant`, `reauth_required`, `tools` |
| MCP | `http://127.0.0.1:8766/mcp`, streamable HTTP, JSON-RPC 2.0 |
| Source of truth | `C:\Users\apviz\.minimax\google-access` → synced into the repo's `container/` |
| Running bytes | `server.mjs` sha256 `8429fa512919…` — identical in repo, image and container |

**Three volumes, one credential.** The credential exists in exactly one place:
`data/credentials.json` inside the mounted volume. It is **never** in an image
layer (`.dockerignore` enforces it), never in a repo, never in a log, never in
a chat message.

---

## 3. The procedure

### 3.1 Measure before touching

```powershell
docker inspect --format '{{.State.Status}}|{{if .State.Health}}{{.State.Health.Status}}{{end}}|{{.Config.Image}}' Google_Access
docker exec Google_Access node -p "require('crypto').createHash('sha256').update(require('fs').readFileSync('/app/server.mjs')).digest('hex')"
Get-FileHash "C:\Users\apviz\.minimax-agent\projects\Mavis-Google_Access\container\server.mjs" -Algorithm SHA256
```

The two hashes must be equal. That comparison is the whole point.

### 3.2 Sync the live source into the repo (never the other way round)

```powershell
node "C:\Users\apviz\.minimax-agent\projects\Mavis-Google_Access\scripts\sync-container-source.py"
```

It copies live → repo through a whitelist and then verifies the result. It
also owns the rule that bit us once: a `.gitignore` regenerated from a constant
is a **second source of truth**, so the gate checks the *property* (`git
check-ignore` on the sensitive paths, `git ls-files` for nothing tracked from
`data/`, `logs/`, `state/`, `.work/`) instead of the pattern.

### 3.3 Build and recreate

```powershell
docker build -t google-access:1.0.10 -f "C:\Users\apviz\.minimax\google-access\Dockerfile" "C:\Users\apviz\.minimax\google-access"

docker run -d --name Google_Access --restart unless-stopped `
  -p 127.0.0.1:8766:8766 `
  -v "C:\Users\apviz\.minimax\google-access\data:/data" `
  -v "E:\--- System Secrets:/secrets:ro" `
  -e GA_PORT=8766 google-access:1.0.10
```

**The port is derived, never assumed.** The healthcheck and the server both read
`process.env.GA_PORT`; a hardcoded `8765` once made a perfectly good container
report `unhealthy` for nine intervals running. Three sources of truth about a
port is one too many.

### 3.4 Prove it

```powershell
node "C:\Users\apviz\.minimax-agent\projects\Mavis-Google_Access\scripts\ga-doctor.mjs"
```

`C1.container` and `C1b.running-code` must both be green.

---

## 4. What it guarantees

- The credential never enters an image layer.
- The bytes running are the bytes in the repo.
- A rebuild never touches the grant: the credential lives in the volume, so a
  new image inherits it.
- The container survives a reboot (`unless-stopped`).

---

## 5. Known limits, stated out loud

- **`docker container prune -a` is forbidden.** It destroyed a swarm on
  2026-08-08. `Google_Access` is a separate, new container.
- **The image version is a string, not a system.** Eight builds happened in one
  day on 2026-10-27. Read `docker inspect`, not the docs.
- **The secret volume is read-only on purpose.** A process that must write a
  secret belongs in the `data` volume, with the secret excluded from git.
- **This skill does not own the MCP registry.** That is
  `mavis-skill-mcp-development`.

---

## 6. Cross-references

- `mavis-skill-google-access-control-point` — the control point that inspects
  this container
- `mavis-skill-mcp-development` — adding new tools and servers to the registry
- `mavis-skill-notebooklm-extendlm` — the token behind the NotebookLM proxy
- `mavis-google-access-bot` — the hub that owns this skill
- Docs: `Mavis-Google_Access/docs/ARHITECTURA-GOOGLE-ACCESS.md`,
  `docs/STARE-MASURATA.md`
