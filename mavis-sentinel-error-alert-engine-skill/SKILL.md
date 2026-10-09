---
name: mavis-sentinel-error-alert-engine-skill
description: |
  Real-time Sentinel Guardian Auditor & Toast Error Alert Engine. Detects D2_JUST_FAB fabrication markers,
  Romanian diacritics violations, forbidden diacritic terms, path invariant violations (Antigravity_Folder\Antigravity_Projects),
  and fake ASCII QR code hallucinations. Triggers top floating toast error bar (Fabrication detected: [...])
  and appends bold red markdown caution alert blocks (> [!CAUTION]) in Hermes Desktop App UI and TUI Gateway.
license: proprietary
metadata:
  version: v1
  publisher: apviz
---

# Sentinel Guardian System Error Alert Engine

Real-time compliance and error toast engine that flags AI model deviations across Hermes Desktop App UI, TUI Gateway, and CLI.

## Core Modules & Hooks

1. **guardian.py**: `C:\Users\apviz\AppData\Local\hermes\skills\optimus-prime-sentinel\sentinel-auto-recalibration\scripts\guardian.py`
   - Validates DLG/SLG banners, D2_JUST_FAB markers, diacritics, path invariants, and fake QR codes.
   - Formats error string: `Fabrication detected: ["..."]`.
2. **sentinel_daemon.py**: `C:\Users\apviz\AppData\Local\hermes\mcp-servers\custom\sentinel-daemon\sentinel_daemon.py`
   - Real-time text auditor `SentinelGuardianAuditor`.
   - Appends red markdown alert blocks: `> [!CAUTION] 🚨 SENTINEL GUARDIAN DEVIATION DETECTED`.
3. **tui_gateway/ws.py**: Intercepts outgoing WebSocket RPC frames and injects toast error details and audited text.
4. **agent/turn_finalizer.py**: Intercepts final turn execution results and stamps `result["error"]` when validation fails.
