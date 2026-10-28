# Reference Specification: Real-Time Multi-Interface Sync Daemon (ALSD)

## 1. Objective
Establish seamless, bidirectional, real-time synchronization of conversations across the Antigravity Desktop App, Antigravity IDE, Antigravity CLI, and Gemini CLI.

## 2. Synchronization Topography
```text
+-----------------------+       +---------------------+
| Antigravity CLI (agy) |       |     Gemini CLI      |
+-----------+-----------+       +----------+----------+
            |                              |
            +-------------->+<-------------+
                            |
           +----------------v-----------------+
           |   Canonical Transcript Store     |
           | (~/.gemini/antigravity/brain/)   |
           +----------------+-----------------+
                            |
           +----------------v-----------------+
           | Antigravity Live Sync Daemon     |
           |        (WebSocket :9876)         |
           +-------+------------------+-------+
                   |                  |
    +--------------v----+       +-----v---------------+
    | Desktop App UI    |       | Antigravity IDE UI  |
    +-------------------+       +---------------------+
```

## 3. Rate-Limit Normalization Protocol
1. When an agent invocation in any client hits a 429 rate limit or network abort, the transport stream is severed.
2. The Sync Daemon monitors active file handles on `transcript.jsonl`.
3. If an unclosed turn delta is observed with no activity for 5000ms following an API error:
   - The daemon writes a synthetic closing record:
     ```json
     {"step_index": -1, "type": "SYSTEM_NOTE", "status": "PAUSED_RATE_LIMIT", "content": "Session paused due to rate limit. Context preserved."}
     ```
4. This closes the IDE extension's internal state machine, restoring the "Recent Conversations" item to a clickable, healthy state and preventing the greyed-out freeze.
