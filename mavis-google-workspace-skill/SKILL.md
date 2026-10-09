---
name: mavis-google-workspace-skill
description: Bridge to Google Workspace via the `google-workspace-mcp` MCP server (gwmcp alias). Covers Calendar, Drive, Docs, Sheets, Gmail. Currently DISABLED — requires Google OAuth bootstrap before enable.
---

# Google Workspace Bridge

The `google-workspace-mcp` MCP server is wired (gwmcp alias). Covers the full Google Workspace: Calendar, Drive, Docs, Sheets, Gmail, Contacts. Currently **disabled** because Google OAuth must be bootstrapped first.

## Activation steps

1. **OAuth bootstrap** — run the gwmcp OAuth flow once to grant Drive/Gmail/Calendar scopes:

   ```powershell
   & 'C:\Users\apviz\AppData\Roaming\npm\google-workspace-mcp.cmd' auth
   # or whatever the package's auth subcommand is
   ```

2. **Verify** the OAuth token is persisted.
3. **Enable the MCP server**:

   ```text
   mavis({ command: "mcp update", args: { name: "google-workspace-mcp", enabled: true } })
   ```

4. **Smoke-test** with a read-only operation (list today's calendar events).

## Alternative: per-service MCPs

If you prefer narrower OAuth scopes (one per service), use these instead — all wired but disabled:

- `gdrive-mcp` — Drive only
- `gmail-mcp` — Gmail only
- `google-calendar-mcp` — Calendar only

Each needs its own OAuth bootstrap.

## Hard rules

- 🚫 Never enable Google Workspace MCPs without OAuth being set up first — the tool calls will fail in confusing ways.
- R0 before any send / create / delete operation on Google's side.
- Treat all tokens as secrets. Do not log them.

## Reference

- Bridge file: `C:\Users\apviz\.minimax-agent\projects\10_BRIDGES\10_gemini.md` (Gemini shares the Google ecosystem)
- Doctrine: `SENTINEL_OPERATIONAL_DOCTRINE.md §9`
