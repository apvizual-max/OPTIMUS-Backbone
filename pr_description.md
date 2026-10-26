🎯 **What:**
The issue highlighted a missing test for the error handling path within `_bridge_for` inside `07_BACKBONE/mcp/sentinel_hub_server.py:984`. Specifically, the code was missing assertions to ensure errors present in tool payloads correctly trigger `isError=True` inside `CallToolResult`.

📊 **Coverage:**
The test suite now properly asserts that `_bridge_for`:
*   Detects and parses JSON string text blocks reporting `{"error": ...}` setting `isError=True`.
*   Tolerates valid JSON success strings without `error` property, correctly leaving `isError=False`.
*   Safely falls through when reading malformed/invalid JSON `text` blocks, resulting in `isError=False`.
*   Ignores block types other than `text` (e.g. images).

✨ **Result:**
The `sentinel_hub_server.py` file is now fully regression-tested for tool error handling mapping to MCP payloads. `McpBridgeErrorHandling` passes with a 4/4 assertions result in the custom test suite.
