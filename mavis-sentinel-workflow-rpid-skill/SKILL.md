---
name: mavis-sentinel-workflow-rpid-skill
description: |
  Eternal reference engineering workflow for Research, Planning, Debugging,
  Execution, and Double Programming Integration. Demonstrates the complete
  end-to-end methodology developed during the Sentinel Hermes System Optimization.
license: proprietary
metadata:
  version: v1.0
  publisher: apviz
---

# Sentinel Engineering Workflow: Research, Plan, Debug & Implement

This skill documents the exact **7-Phase Engineering Workflow** established during the Sentinel Hermes System Optimization. It serves as an eternal reference model for complex system architecture, MCP containerization, credential vaulting, and double programming autostart deployment across all AI runtimes.

---

## The 7-Phase Workflow Blueprint

```
[ Phase 1: Research & Audit ]
       │  - Inspect logs, schema definitions, process tables, container statuses.
       ▼
[ Phase 2: Invariant & Path Enforcement ]
       │  - Enforce target root (C:\Users\apviz\Documents\Antigravity_Folder\Antigravity_Projects\).
       ▼
[ Phase 3: Package Manifest & Dependency Build ]
       │  - Create pyproject.toml, FastMCP scripts, install into virtualenv.
       ▼
[ Phase 4: Environment Credentials Vaulting ]
       │  - Inject App Passwords, 2FA backup codes, bot tokens into .env.
       ▼
[ Phase 5: High-Availability Docker Swarm ]
       │  - Compose yml with restart: always for containerized services.
       ▼
[ Phase 6: Double Programming & System Autostart ]
       │  - Create autostart PowerShell script + Windows Startup launcher (.bat).
       ▼
[ Phase 7: Empirical Verification & Audit ]
          - Run Python verification test suite to prove 100% operational status.
```

---

## 1. Phase-by-Phase Methodological Rules

### Phase 1: Research & Audit
- **Rule**: NEVER guess paths, schemas, or variable names.
- **Tools**: Use `list_dir`, `view_file`, `docker ps`, and empirical log inspection before making hypotheses.

### Phase 2: Invariant & Path Enforcement
- **Rule**: Enforce exact target paths without deviation.
- **Approved Root**: `C:\Users\apviz\Documents\Antigravity_Folder\Antigravity_Projects\`
- **Prohibited Path**: `Antigravity_Folder` (permanently disabled).

### Phase 3: Package Manifest & Dependency Build
- **Rule**: Standardize Python packages using PEP 517 `pyproject.toml` with `setuptools.build_meta`.
- **Installation**: Run `pip install -e` inside target virtual environment. Verify with direct python `import` tests.

### Phase 4: Environment Credentials Vaulting
- **Rule**: Store all sensitive keys, app passwords, backup codes, and bot tokens in `.env` using standard KEY=VALUE syntax.
- **Validation**: Use `dotenv_values` in Python to confirm key presence without exposing raw secrets in terminal logs.

### Phase 5: High-Availability Docker Swarm
- **Rule**: Containerize persistent services using `docker-compose.yml` with `restart: always` or `restart: unless-stopped`.
- **Scope**: Ensure database engines (PostgreSQL, Redis, Elasticsearch, MinIO, Vault) and custom MCP tools operate continuously.

### Phase 6: Double Programming & System Autostart
- **Rule**: Implement dual-tier redundancy:
  - Tier 1: Application-level config pointers (`config.yaml`).
  - Tier 2: Host OS Autostart via Windows Startup batch launcher (`C:\Users\apviz\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\Hermes_Sentinel_Autostart.bat`) invoking orchestrator PowerShell script (`autostart_hermes_swarm.ps1`).

### Phase 7: Empirical Verification & Audit
- **Rule**: NEVER declare completion without running automated verification scripts that return concrete, pass/fail test results.

---

## 2. Practical Example Script

```python
# Example Verification Runner
import os, sys, yaml, subprocess

print("Executing System Integrity Verification...")
assert os.path.exists(r"C:\Users\apviz\Documents\Antigravity_Folder\Antigravity_Projects")
with open(r"C:\Users\apviz\AppData\Local\hermes\config.yaml", encoding="utf-8") as f:
    cfg = yaml.safe_load(f)
assert len(cfg.get("mcp_servers", {})) >= 30
print("System Integrity Check: 100% PASSED!")
```
