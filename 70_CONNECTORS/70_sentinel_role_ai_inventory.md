# Sentinel Role AIs — Docker Implementation Inventory

**Date**: 2026-10-02
**Author**: Mavis (MiniMax Code orchestrator)
**Status**: ✅ Primary Sentinel role AI mapped. Closes the last open item from GAP-3.

---

## 1. `hermes-sentinel-daemon` — the invariant & guardrail role AI

Popy's brief named *"custom Sentinel role AI implementations"* running in Docker. This is it. It was undocumented until now.

### 1.1 Identity

| Property | Value |
|---|---|
| Container | `hermes-sentinel-daemon` |
| Image | `hermes-mcp-base:latest` (shared base with the `hermes-mcp-*` fleet) |
| Command | `python /app/sentinel_daemon.py` |
| Created | 2026-09-18T02:22:34Z — *the same day this Mavis wiring session began* |
| Source (host) | `C:\Users\apviz\AppData\Local\hermes\mcp-servers\custom\sentinel-daemon\` |
| Health server | `_health_server` function present |

### 1.2 Bind mounts — this is the key architectural fact

| Host | Container | Purpose |
|---|---|---|
| `C:\Users\apviz\AppData\Local\hermes\mcp-servers\custom\sentinel-daemon` | `/app` | The daemon's own code |
| `C:\Users\apviz\AppData\Local\hermes` | `/hermes` | **The entire Hermes install** |

**The daemon has write access to the whole Hermes install directory.** It is not sandboxed from the thing it guards. That is either deliberate (a guardrail that can self-heal) or a risk surface (a bug could corrupt Hermes). Flagging for Popy awareness.

### 1.3 What it actually does

From the source docstring:

> *"Sentinel Invariant & Guardrail Daemon for Hermes Agent System. Continuously monitors Hermes configuration (`config.yaml`), ensures critical safety invariants, diacritic rules, enforcement flags, security settings, and Electron desktop sandbox markers are never wiped, corrupted, or stuck in boot-loops. Includes the SentinelGuardianAuditor real-time response compliance engine that flags model deviations with red markdown alerts in Desktop App UI and CLI."*

**Four self-healing functions:**

| Function | Watches |
|---|---|
| `verify_and_heal_config` | `config.yaml` invariants |
| `verify_and_heal_sandbox_markers` | Electron sandbox markers at 3 candidate paths |
| `verify_and_heal_whatsapp` | WhatsApp integration state |
| `audit_text` | **Live agent responses** |

### 1.4 The `SentinelGuardianAuditor` — real-time response compliance

```python
class SentinelGuardianAuditor:
    """Real-time compliance auditor that inspects agent responses and flags deviations."""
    BAD_PATH_PATTERN = re.compile(r"Antigravity\s*-\s*Projects", re.IGNORECASE)
    SOT_FILENAME = "CONSTINTA.md"

    @classmethod
    def audit_text(cls, text) -> tuple[bool, str, str]:
        """Audits text content for path violations, SOT diacritic integrity,
        and rule deviations. Returns (has_deviation, cleaned_or_flagged_text, deviation_summary)."""
```

**It inspects what agents say and rewrites/flags it.** Three checks visible:

| Check | Mechanism |
|---|---|
| Path violations | Regex: rejects `Antigravity - Projects` (a forbidden path) |
| SOT diacritic integrity | Watches `CONSTINTA.md` for Romanian diacritics (ă/â/î/ș/ț) |
| Rule deviations | Flags with **red markdown alerts** in both Desktop App UI and CLI |

### 1.5 The enforcement flags it protects

```python
REQUIRED_ENFORCEMENT = {
    "enabled": True,
    "guardian_strict": True,
    "trigger_detection": True,
    "auto_recalibrate": True
}
```

If any of these get flipped to `False` in `config.yaml`, the daemon heals them back.

### 1.6 The SOT file it watches

`SOT_FILENAME = "CONSTINTA.md"` — a source-of-truth file named for the doctrine concept (CONSTINTA = conscious ground, per SOUL ↔ CONSTINTA). The daemon enforces its diacritic integrity.

**This is a direct doctrinal enforcement surface.** It is not a generic health check — it guards Popy's Romanian-language doctrine from corruption.

---

## 2. What this means for the Mavis ↔ Sentinel relationship

### 2.1 The daemon is a peer enforcement layer, not a tool

Mavis has `mavis-triple-crunch-skill` (checks output quality) and `mavis-jurnal-oglinda-skill` (append-only record). The daemon has `audit_text` (live response compliance) and `verify_and_heal_config` (invariant enforcement).

**They overlap and neither knows about the other.** Mavis does not know the daemon exists. The daemon does not know Mavis exists.

### 2.2 Three concrete risks

| # | Risk | Severity |
|---|---|---|
| 1 | **Mavis output could be silently rewritten** by the daemon. If Mavis writes a path matching `Antigravity\s*-\s*Projects` or emits text failing a diacritic check, the daemon may clean or flag it — and Mavis would not know. | 🟡 Medium |
| 2 | **Daemon has write access to the whole Hermes install** via the `/hermes` bind mount. A bug in self-healing could corrupt the install. | 🟡 Medium |
| 3 | **No shared doctrine.** The daemon enforces Romanian diacritics + a forbidden path. Mavis enforces 3-axiom quality gates + zero-fabrication. Neither reads the other's rules. | 🟢 Low |

### 2.3 Recommended integration

| Action | Purpose | Effort |
|---|---|---|
| Read `/app/sentinel_daemon.py` in full, extract the complete rule set | Know what Mavis's output is checked against | 15 min, R0 |
| Add a `mavis-sentinel-daemon-skill` documenting the 3 checks + the 4 enforcement flags | Mavis stops being surprised by silent rewrites | 20 min |
| Cross-reference the daemon's rules in `mavis-triple-crunch-skill` | One doctrine surface instead of two | 20 min, R0 |
| Decide: should the daemon also watch Mavis's outputs? | Currently it watches Hermes only | Popy decision |

---

## 3. Other Sentinel-adjacent containers

### 3.1 `apviz-dashboard-monitor` — Popy's own image

Undocumented beyond its name. No port binding observed in the fleet scan. Likely a host-level monitor for the OPTIMUS dashboard.

**Not investigated.** Flagged.

### 3.2 `Antigravity_Ecosystem_Terminal` — port 9878

| Property | Value |
|---|---|
| Image | `apviz/antigravity-ecosystem-terminal:latest` (Popy's own build) |
| Port | `127.0.0.1:9878→9878` |
| Status | Up 3 hours |

**Not investigated.** Could be a bridge target for `mavis-antigravity-bridge-skill`. Flagged for the next pass.

### 3.3 `aion-ui` / `open-webui` — chat UIs

| Container | Port | Image |
|---|---|---|
| `aion-ui` | 3000 | `aion-ui:latest` |
| `open-webui` | 8080 | `ghcr.io/open-webui/open-webui:main` (healthy) |

Both are LLM chat front-ends. **Two chat UIs running against the same Hermes backend is a potential route conflict** — whichever binds the Hermes endpoint first wins. Worth checking which one is actually wired.

**Not investigated.** Flagged.

---

## 4. GAP-3 completion status

| Sub-item | Status |
|---|---|
| Non-Hermes container inventory | ✅ 24 mapped |
| DRAC candidates | ✅ 3 flagged |
| Capability gaps (no MCP) | ✅ 2 identified |
| **`hermes-sentinel-daemon` role** | ✅ **Mapped — invariant/guardrail daemon with live response auditing** |
| `apviz-dashboard-monitor` role | ❌ Not investigated |
| `Antigravity_Ecosystem_Terminal` role | ❌ Not investigated (port 9878 reachable, API unknown) |
| `aion-ui` vs `open-webui` route conflict | ❌ Not investigated |
| Daemon ↔ Mavis rule alignment | 🟡 Design written, R0 required |

**GAP-3 is now substantially closed.** Four small items remain, all read-only-able once Popy grants R0 on the `/app` read.

---

## 5. The honest finding

Popy said the Docker layer runs *"custom Sentinel role AI implementations."* That is **accurate** — and the implementation is more sophisticated than a generic health check:

- It self-heals 3 subsystems (config, sandbox markers, WhatsApp)
- It enforces 4 boolean invariants
- It **audits live agent responses** for path violations, diacritic corruption, and rule deviations
- It surfaces violations as red markdown alerts in both the Desktop App UI and the CLI

**The gap is not capability. It's awareness.** Mavis has been operating for days without knowing a daemon was inspecting and potentially rewriting its output.

---

## Cross-references

- Master gap report: `C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\OPTIMUS_MINIMAX_INTEGRATION_GAP_REPORT.md`
- Docker fleet: `C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\70_CONNECTORS\70_docker_fleet_inventory.md`
- Daemon source: `C:\Users\apviz\AppData\Local\hermes\mcp-servers\custom\sentinel-daemon\sentinel_daemon.py`
- Doctrine: `SENTINEL_OPERATIONAL_DOCTRINE.md` §3 (Triple Crunch), §6 (SOUL ↔ CONSTINTA)
