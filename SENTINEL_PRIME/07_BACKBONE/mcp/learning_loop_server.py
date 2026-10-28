#!/usr/bin/env python3
"""
`learning-loop` - the derive, record, hand-off loop.

Declared in OPTIMUS_MCP_CONFIG.json as: "Auto-learning loop cu feedback si
metrics".

Three tools, in the order the loop actually runs:

  1. `sentinel_extract_patterns` - derive patterns from an input.
  2. `sentinel_log_event`        - record what happened, typed as correction,
                                  mimicry, pattern or decision.
  3. `sentinel_create_handoff`   - carry the loop into the next session.

KNOWN GAP, stated rather than papered over: the declaration also says
"metrics", and no hub tool reports loop metrics. Rather than invent one and let
the server advertise a capability nobody measured, this serves the three tools
the hub actually provides. If metrics are wanted, that is a hub capability to
build - not a stub to add here.

Requires WORKSPACE_ROOT.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import sentinel_mcp_slice as slices  # noqa: E402

TOOLS = (
    'sentinel_extract_patterns',  # derive
    'sentinel_log_event',         # record
    'sentinel_create_handoff',    # hand off
)

if __name__ == '__main__':
    slices.main('learning-loop', TOOLS)