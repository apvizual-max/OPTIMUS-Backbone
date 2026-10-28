#!/usr/bin/env python3
"""
`rule-triggers` - R-2, R-9 and R-10 trigger monitoring.

Declared in OPTIMUS_MCP_CONFIG.json as: "R-2, R-9, R-10 trigger monitoring si
execution".

Three rules, two tools, and the mapping is deliberate rather than accidental:

  * R-9 ("BAH ESTI PROST") and R-10 ("ESTI ILOGIC") are what
    `sentinel_check_r_triggers` decides - it is their entire subject.
  * R-2 is the evidence rule, and it is enforced inside
    `sentinel_check_mimicry`, whose detectors include A6, A4 and R-2.

The coverage table in `monitor.py` maps this capability to
`sentinel_check_r_triggers` alone. The config's own description names R-2 as
well, and a declaration is a promise about capability, not about one tool name.
Serving only the narrower list would leave R-2 unreachable from the server that
exists precisely to expose it.

Requires WORKSPACE_ROOT.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import sentinel_mcp_slice as slices  # noqa: E402

TOOLS = (
    'sentinel_check_r_triggers',  # R-9 / R-10
    'sentinel_check_mimicry',     # R-2 and the anti-mimicry detectors
)

if __name__ == '__main__':
    slices.main('rule-triggers', TOOLS)