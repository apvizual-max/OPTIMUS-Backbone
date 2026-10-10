#!/usr/bin/env python3
"""
`context-pressure` - context pressure monitoring.

Declared in OPTIMUS_MCP_CONFIG.json as: "Monitor presiune context cu
auto-compact".

`sentinel_check_context` is the pressure measurement: how close the session is
to overflow. It is served here directly from the hub's implementation.

KNOWN GAP, stated rather than papered over: the declaration also says
"auto-compact", and no hub tool compacts anything. Inventing a compaction tool
here would advertise a capability that changes a live session and that nothing
measured. Compaction is a decision, not a measurement - it belongs to the
operator, and it belongs in the hub if it is ever built.

That leaves this server with one tool, which is honest. A one-tool server that
measures pressure correctly is worth more than a two-tool server whose second
tool does nothing verifiable.

Requires WORKSPACE_ROOT.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import sentinel_mcp_slice as slices  # noqa: E402

TOOLS = ('sentinel_check_context',)

if __name__ == '__main__':
    slices.main('context-pressure', TOOLS)