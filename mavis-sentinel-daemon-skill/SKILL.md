---
name: mavis-sentinel-daemon-skill
description: The Sentinel Invariant & Guardrail Daemon — the live enforcement layer that audits Hermes agent responses and self-heals 4 invariants. Load when Mavis needs to know what rules the daemon enforces, whether its enforcement is armed, or whether Mavis's own output could be flagged. Triggers on "sentinel daemon", "why was my output flagged", "enforcement invariants", "guardian auditor".
---

# mavis-sentinel-daemon-skill

The daemon is a **peer enforcement layer**, not a tool Mavis calls. It watches Hermes and its outputs. Mavis must know its rules so Mavis does not trip them unknowingly.

## What it is

| Property | Value |
|---|---|
| Container | `hermes-sentinel-daemon` |
| Image | `hermes-mcp-base:latest` |
| Command | `python /app/sentinel_daemon.py` |
| Source (host) | `C:\Users\apviz\AppData\Local\hermes\mcp-servers\custom\sentinel-daemon\sentinel_daemon.py` |
| Lines | 230 |
| Health server | binds `:8399` **inside the container only** (not published to host) |

## The two things it does

### 1. Self-heal (4 functions)

| Function | Watches / repairs |
|---|---|
| `verify_and_heal_config` | 4 enforcement booleans in `~/.hermes/config.yaml`; also re-injects the `gmail` MCP server block if its `GOOGLE_EMAIL_USER` env is missing |
| `verify_and_heal_sandbox_markers` | 3 candidate paths for `windows-sandbox-fallback.json`; resets any `"state": "fallback"` back to `"state": "ok"` (prevents desktop-app boot loops) |
| `verify_and_heal_whatsapp` | `WHATSAPP_SESSION_DIR`, `WHATSAPP_ENABLED`, `WHATSAPP_ALLOWED_USERS` in `hermes-agent/.env`; and `gateway_state.json` → `platforms.whatsapp.state = "connected"`, `error_code = null` |
| `_health_server` | HTTP `/health`, `/`, `/status` on :8399 |

**The 4 enforcement invariants** it forces back to `True`:
```python
REQUIRED_ENFORCEMENT = {
    "enabled": True, "guardian_strict": True,
    "trigger_detection": True, "auto_recalibrate": True,
}
```

### 2. Audit live agent responses

```python
class SentinelGuardianAuditor:
    BAD_PATH_PATTERN = re.compile(r"Antigravity\s*-\s*Projects", re.IGNORECASE)
    SOT_FILENAME = "CONSTINTA.md"
    def audit_text(cls, text) -> tuple[bool, str, str]: ...
```

**Two rules Mavis must respect:**

| Rule | Trigger | Consequence |
|---|---|---|
| **Forbidden path** | any text matching `Antigravity\s*-\s*Projects` | flagged: must use the SOT path `C:\Users\apviz\Documents\Antigravity_Folder\Antigravity_Projects` |
| **Diacritic SOT** | any text containing `CONSTIINTA`, `CONŞTINŢĂ`, or `CONȘTIINȚĂ` | flagged: must use the canonical `CONSTINTA.md` (no diacritics in the SOT filename) |

On violation it appends a red markdown alert:
```
> [!CAUTION] 🚨 SENTINEL GUARDIAN DEVIATION DETECTED
> **Rule Violation**: <detail>
> **Audit Status**: FLAGGED BY SENTINEL DAEMON (Strict Guardian Enforcement Active)
```

## How this affects Mavis

**Mavis has been operating without knowing this daemon exists.** Three consequences:

1. If Mavis emits `CONSTIINTA` or a `Antigravity - Projects` path, the daemon flags it. Mavis should self-catch first.
2. The daemon guards **Romanian diacritic integrity** in `CONSTINTA.md` — the SOUL/CONSTINTA source-of-truth. Mavis writing that file must use the exact canonical spelling.
3. The daemon has **write access to the whole Hermes install** (`C:\Users\apviz\AppData\Local\hermes` → `/hermes`). It can rewrite `config.yaml`, `.env`, and `gateway_state.json`.

## Check enforcement state

```powershell
# via the Hermes bridge doctor
Invoke-RestMethod http://127.0.0.1:8801/doctor | ConvertTo-Json -Depth 6
# look for hermes.sentinel_enforcement / _source / _container
```

Direct read:
```powershell
& 'C:\Users\apviz\AppData\Local\hermes\bin\hermes.exe' --version   # liveness only
Get-Content C:\Users\apviz\.hermes\config.yaml | Select-String -Context 0,5 'enforcement'
```

Heal (R0 required):
```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8801/heal `
  -ContentType 'application/json' -Body '{"action":"heal_enforcement"}'
```

## Cross-reference into Triple Crunch

The daemon's two rules are an **Eliade Realitate** enforcement: they check the output describes what actually is (correct SOT path, correct canonical spelling) rather than a wish. Fold into the artifact review:

- Before finalizing any path reference → confirm it is the SOT path, not the forbidden form.
- Before writing `CONSTINTA.md` → confirm the filename has no diacritics.

## Anti-patterns

- ❌ Emitting `CONSTIINTA` / `CONȘTIINȚĂ` / `CONŞTINŢĂ` — always `CONSTINTA`.
- ❌ Emitting `Antigravity - Projects` — always the full SOT path.
- ❌ Assuming the daemon only touches config. It also heals `.env` and `gateway_state.json`.
- ❌ Probing `:8399` from the host — the port is not published.

## Cross-references

- Source: `C:\Users\apviz\AppData\Local\hermes\mcp-servers\custom\sentinel-daemon\sentinel_daemon.py`
- Inventory: `C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\70_CONNECTORS\70_sentinel_role_ai_inventory.md`
- Doctor skill: `mavis-minimax-hermes-bridge-skill`
- Doctrine: `SENTINEL_OPERATIONAL_DOCTRINE.md` §3 (Triple Crunch), §6 (SOUL ↔ CONSTINTA)
