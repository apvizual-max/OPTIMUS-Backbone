---
name: mavis-skill-browser-mcp
description: The browser layer of the Google Access ecosystem - the MCP servers that drive a real browser on this station, and the plan for extending them. Load this when working on minimax-notebooklm, chrome-devtools-mcp, agent-browser-mcp, the Photo Picker window, or any future browser-side capability of the central access point. Owns the CDP port rule (9412), the own-Chrome-profile rule, the namespace separation from Hermes, and the rule that a browser MCP must be proven by a real stdio handshake, not by the file existing.
role: functional
bot: mavis-google-access-bot
---

# mavis-skill-browser-mcp

**Role.** The browser side of the access point. Google has no public API for
NotebookLM, and the Photo Picker needs a signed-in browser to open at all — so
the browser is a **first-class part of the access point**, not an accessory.

---

## 1. Why it exists (the defect, not the preference)

Two measured facts made the browser layer mandatory:

1. **The `minimax-notebooklm` entry pointed at a folder that did not exist.**
   The registry said "enabled"; the file was gone. The registration could not
   start. Fixing it required *proving the server answers* — a file that exists
   is not a server that runs.
2. **The Photo Picker's `pickerUri` opens only in the browser signed in as the
   account that owns the session**, and never inside an iframe. The same
   message ("Couldn't open Google Photos") means two different things, so
   guessing was worthless — the URI had to be opened in a controlled context
   and the page read.

---

## 2. What is on the station, measured

| Server | Transport | What it is | Measured state |
|---|---|---|---|
| `minimax-notebooklm` | stdio (`node`) | **minimax's own** NotebookLM server; own Chrome profile at `%LOCALAPPDATA%\minimax-notebooklm\chrome_profile`, own CDP port **9412** | `initialize` OK, **4 tools** (`nblm_health`, `nblm_list_notebooks`, `nblm_get_sources`, `nblm_ask`), `authenticated=true`, circuit closed |
| `chrome-devtools-mcp` | stdio (`chrome-devtools-mcp.cmd`) | live browser automation, DevTools protocol | registered, enabled |
| `agent-browser-mcp` | stdio (`agent-browser-mcp-server.cmd`) | headless browser automation | registered, enabled |
| `notebooklm-mcp` | stdio (`notebooklm-mcp.cmd`) | the **same package Hermes runs**, with no configuration and no credential | **deliberately not a minimax capability** — see §5 |

### The two rules

- **Own profile, own port.** `minimax-notebooklm` runs Chrome with a profile
  that belongs to minimax and nothing else, on CDP **9412**. Closing its last
  tab kills the browser; the CDP endpoint then refuses connections and the
  server has to be relaunched.
- **A link bound to an OAuth session is opened in the account that owns it.**
  The agent opens the window, in the right profile, and reads what the page
  answers — it does not hand the user a link and ask for feedback.

---

## 3. The procedure

### 3.1 Prove a registered browser server actually starts

```powershell
node "C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\Mavis-Google_Access\scripts\probe-mcp-stdio.mjs" --name minimax-notebooklm
```

It spawns the **exact** command and arguments from the global registry, speaks a
real MCP handshake over stdio and reports what answered:

```
PROBE=minimax-notebooklm TRANSPORT=stdio INIT_OK=1 SERVER=minimax-notebooklm TOOLS=4 MS=90 EXIT=0
```

### 3.2 The health of the NotebookLM browser session

```powershell
node "C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\Mavis-Google_Access\scripts\probe-minimax-notebooklm.mjs" --call nblm_health
node "C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\Mavis-Google_Access\scripts\probe-notebooklm.mjs"
```

The second one lists the real notebooks (JULES 182 sources, GEMINI & AI Studio
251, CV-Automation 98, SENTINEL Role 225, AGENTS 8, TRADE 1, CV-Notebook 99,
CLIENTS 2, OPTIMUS System 5) and the ExtendLM extension status. It prints
names and counts — **never a token**.

### 3.3 The Photo Picker window

The agent opens the picker URI in Chrome **with the own profile**, so the
account that owns the session is the one signed in. The user selects and
presses Done; everything after that is mechanical (see
`mavis-skill-photo-picker`).

---

## 4. The plan — where the browser layer goes next

| Planned | Why | What it needs |
|---|---|---|
| **Picker window automation** | the selection step still needs a human (by Google's design), but the *opening* could be triggered by the bot instead of by a link | a CDP call that opens the URI in the own profile, verified by reading the page title |
| **NotebookLM source ingestion** | the browser server can read a notebook; ingesting a *new* source still goes through the web UI | a scripted interaction, proven by a re-read of the notebook's source count |
| **A shared browser session** | today each browser server owns its own profile; a shared, explicitly-owned profile would let the Cloud side reuse the session | profile ownership must stay inside minimax's namespace — never Hermes's |
| **CDP health in the control point** | `C5` proves the stdio handshake; the CDP port itself is not yet a check | add a check that port 9412 answers and reports the profile it owns |

**A browser capability is added the same way any MCP is added** — see
`mavis-skill-mcp-development`: register it globally, prove the handshake, add a
check to the control point, then declare it in the docs.

---

## 5. What it guarantees

- The browser servers minimax owns are separate instances, not shared toys.
- Every registered browser server is proven by a handshake, not by a file.
- A browser session is opened in the account that owns it.

---

## 6. Known limits, stated out loud

- **The picker step is not automatable.** Google's design: a human chooses the
  photos. Everything after the click is automatable, and is.
- **The browser MCP needs a real Chrome instance.** A headless provider has no
  visible surface and cannot be handed to a user for the one click that
  matters.
- **`chrome-devtools-mcp` and `agent-browser-mcp` are registered but not
  handshaken by the control point** — only `minimax-notebooklm` is, because it
  is the one the Google Access path depends on.
- **Killing the last tab of the own-profile Chrome kills the browser.** The
  CDP endpoint then refuses connections; relaunch Chrome, do not debug the
  server.

---

## 7. Cross-references

- `mavis-skill-google-access-control-point` — checks `C5` (the handshake)
- `mavis-skill-mcp-development` — how a browser MCP joins the registry
- `mavis-skill-photo-picker` — the human-in-the-loop surface
- `mavis-skill-notebooklm-extendlm` — the second, API-side route to NotebookLM
- `mavis-google-access-bot` — the hub that owns this skill
