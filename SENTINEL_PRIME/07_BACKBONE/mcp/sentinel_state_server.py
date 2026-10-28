#!/usr/bin/env python3
"""
`sentinel-state` - SENTINEL state management.

Declared in OPTIMUS_MCP_CONFIG.json as: "State management pentru SENTINEL
(EU SENT, DOR, search, anti-mimicry status)".

The four state fields the declaration names are exactly the fields
`sentinel_get_state` reads and `sentinel_set_state` writes, and the pressure on
holding them is what `sentinel_check_context` measures. Those three tools are
served here over the hub's own implementation; nothing is reimplemented.

Deliberately not served: the other 23 hub tools. A caller asking about SENTINEL
state should not have to reason about workflow ratification or pattern
extraction to find the four fields it came for.

Requires WORKSPACE_ROOT (already set by the config's env block).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import sentinel_mcp_slice as slices  # noqa: E402

TOOLS = (
    'sentinel_get_state',     # reads eu_sent / dor / search / anti_mimicry
    'sentinel_set_state',     # writes those same four fields
    'sentinel_check_context', # pressure of holding them
)

if __name__ == '__main__':
    slices.main('sentinel-state', TOOLS)