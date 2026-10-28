---
name: mavis-skill-google-access-control-point
description: The permanent-verification contract of Google Access on this station. Load this FIRST for any Google Access question - whether something is broken, whether a re-auth is needed, or whether a new session can trust the connection. It owns the one command that proves the connection (ga-doctor.mjs, 11 checks, one verdict, exit 0/2/3), how to read that verdict, what each check means, which defect each check was born from, and the rule that a session never rebuilds the settings - it repairs the check that failed. Also owns the permanence contract: one container, one credential, one registry, one doctor.
role: functional
bot: mavis-google-access-bot
---

# mavis-skill-google-access-control-point

**Role.** The verifier of the permanent Google connection. It answers exactly one
question — *is the connection actually working right now, and if not, which
piece broke?* — and it answers it by measurement, never by reading a document.

---

## 1. Why it exists (the defect, not the preference)

Popy, 2026-10-28: *"nu mai suport să reiau asta de la capăt în altă sesiune
doar ca să-mi rezolv workflowurile."*

The failure mode was not "Google was down". It was that **nobody could tell**,
so every session started by rebuilding. A connection that cannot be proven is
indistinguishable from a connection that is broken.

So the connection got a **control point**: one command, one verdict.

---

## 2. The command

```powershell
node "C:\Users\apviz\.minimax-agent\projects\Mavis-Google_Access\scripts\ga-doctor.mjs"
```

| Exit | Meaning |
|---|---|
| **0** | every critical check passed (`VERDICT=PASS`) |
| **2** | at least one check failed (`VERDICT=FAIL`) — the failing check is named |
| **3** | the control point itself crashed — **never** reported as green |

It is also scheduled: the Windows task **`Google_Access_Doctor`** runs it every
30 minutes, writing a dated line to
`C:\Users\apviz\.minimax\google-access\logs\ga-doctor-YYYY-MM-DD.log`.
The system checks itself while nobody is in a conversation.

---

## 3. The eleven checks

| Check | What it proves |
|---|---|
| `C1.container` | the container exists, runs, is healthy, has the right image and restart policy |
| `C1b.running-code` | the **bytes running inside** the container are the **bytes in the repo** |
| `C2.health` | the grant is live, no re-auth pending, the tool count is real |
| `C3.services` | a **live** call per Google service, classified OK / REFUSED / ERROR |
| `C4.extendlm` | the NotebookLM token is alive and its snapshot is published to the Cloud secret |
| `C5.browser-mcp` | the registered Browser MCP path exists **and** the server answers over real stdio |
| `C6.mcp-registry` | `Google_Access` is registered globally, so every agent inherits it |
| `C10.mcp-paths` | every local path the global registry points to **exists on disk** |
| `C7.tasks` | the scheduled tasks that keep the system alive are all green |
| `C8.consent` | the re-consent listener is up, so a future re-consent is one click |
| `C9.picker` | the state of the Photo Picker session |

### The two checks that exist because of a real incident

- **`C1b.running-code`** — the 1.0.9 incident: the repo carried the repair, the
  image was built before it, and the container ran the **old code** while every
  document said it was fixed. A healthy container proves it is alive, not that
  it is the thing you wrote.
- **`C10.mcp-paths`** — three registered MCP entries pointed at a folder that had
  been moved. The registry said "enabled", the files did not exist, and nothing
  said so. The configuration is **global**: a dead path there breaks the
  capability for every agent on the station.

---

## 4. The permanence contract

| Concern | Where it lives | Owner |
|---|---|---|
| The credential | the mounted volume `data/credentials.json` | the container; **never** in an image layer |
| The MCP server | one Docker container, `Google_Access`, port 8766 | the host, `restart=unless-stopped` |
| The grant | one OAuth refresh token, 33 scopes, `apvizual@gmail.com` | Google; renewed silently |
| The registry | `C:\Users\apviz\.minimax\mcp.json` (global) | the station — every agent inherits it |
| The rules | `C:\Users\apviz\.minimax\AGENTS.md` §12.5 | every agent |
| The doctor | this skill's command + task `Google_Access_Doctor` | the station, every 30 min |
| NotebookLM | ExtendLM; token rotated by the host, snapshot published to the Cloud secret | the host |

**Re-authentication is rare by design.** Access tokens are minted silently from
the refresh token. When the grant itself expires, `google_auth_status` says so
and prints one consent URL; the consent listener (`Google_Access_Consent`,
every 5 minutes) is already waiting on port 80 to catch the callback. The
authorisation click is the user's, and it is the **only** human step left.

---

## 5. The procedure

1. **Run the control point.** Do not rebuild anything first.
2. **Read the failing check.** It names the piece, not a symptom.
3. **Repair that piece**, at its source — never by re-running setup.
4. **Re-run.** The verdict must return to `PASS`.
5. **If a check fails for a reason you cannot fix**, say so with the check's
   own output. Never report the system as green.

```powershell
# the whole point
node "C:\Users\apviz\.minimax-agent\projects\Mavis-Google_Access\scripts\ga-doctor.mjs"

# prove the control point can go red (a check that cannot fail is not a check)
node "C:\Users\apviz\.minimax-agent\projects\Mavis-Google_Access\scripts\ga-doctor.mjs" --self-test --fail C1.container

# verify one member skill of this bot
node "C:\Users\apviz\.minimax\agents\mavis\skills\mavis-skill-google-access-control-point\scripts\verify-control-point.mjs"
```

---

## 6. What it guarantees

- One command decides, and the decision carries an exit code.
- Every check is independent: one failure never hides another.
- The verdict is reproducible from a script, not from a claim.

---

## 7. Known limits, stated out loud

- **C3 needs the live Google APIs.** During a Google-side outage it reports
  `ERROR` for the affected services. That is the truth at that moment, not a
  defect in this setup — and it is exactly why a transient 503 is re-probed once
  before it is called a finding.
- **The task's recorded result lags by up to 30 minutes.** After a repair, run
  the doctor by hand; the scheduled task then re-consigns its own verdict.
- **`C9` cannot see a picker session the user has not started.** "Consumed" and
  "never started" are both legitimate end states.
- **The control point does not repair anything by itself.** It names the broken
  piece; the repair is manual and lives with the member skill that owns it.

---

## 8. Cross-references

- `mavis-skill-docker-access-point` — the container this control point inspects
- `mavis-skill-mcp-development` — how a new MCP joins the registry this checks
- `mavis-skill-notebooklm-extendlm` — the token behind `C4`
- `mavis-skill-photo-picker` — the session behind `C9`
- `mavis-google-access-bot` — the hub that owns this skill
- Docs: `Mavis-Google_Access/docs/PUNCT-DE-CONTROL.md`, `docs/STARE-MASURATA.md`
