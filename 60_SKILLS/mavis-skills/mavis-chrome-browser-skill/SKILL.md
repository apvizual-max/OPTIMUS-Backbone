---
name: mavis-chrome-browser-skill
description: Bridge to Chrome DevTools MCP and Agent Browser MCP for live browser automation. Use for: screenshots, scraping, devtools protocol, headless browser tasks, OAuth bootstrap flows, NotebookLM / web apps that need a real browser.
---

# Chrome / Browser Bridge

Two browser-automation MCPs are wired and enabled:

- `chrome-devtools-mcp` (v1.6.0) — Chrome DevTools Protocol. Live browser, screenshots, network inspection, console.
- `agent-browser-mcp` (v0.14.2) — Agent Browser headless automation.

## When to use

- ✅ Screenshots / visual verification of a running app
- ✅ Scraping a website that needs JavaScript
- ✅ OAuth bootstrap (open the auth URL, capture the token, store it)
- ✅ NotebookLM / web app automation that needs a real browser
- ✅ Frontend debugging (DevTools console / network)
- ❌ Pure HTTP API calls — use `web_fetch` instead
- ❌ Static HTML scraping — use `curl` or `web_fetch`

## Common operations

### Screenshot a URL

```text
mcp_invoke: chrome-devtools-mcp.take_screenshot({ url: "https://..." })
```

### Run a JS expression in the page

```text
mcp_invoke: chrome-devtools-mcp.evaluate({ url: "https://...", expression: "document.title" })
```

### Headless scrape

```text
mcp_invoke: agent-browser-mcp.run({ url: "https://...", selector: "...", action: "extract" })
```

## Hard rules

- Rate-limit browser operations. Do not hammer a target site.
- Respect `robots.txt` and target site's terms.
- Do not use the browser for credential stuffing or any auth-bypass.

## Reference

- Doctrine: `SENTINEL_OPERATIONAL_DOCTRINE.md §9`
- Chrome binary path: `C:\Program Files\Google\Chrome\Application\chrome.exe`
