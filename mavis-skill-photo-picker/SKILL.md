---
name: mavis-skill-photo-picker
description: The Photo Picker route of Google Access - the only way to read the user's own photo library, because Google retired the library scopes in March 2025. Load this when opening a picker session, when the picker refuses to open, when capturing what the user selected, or when the picker heartbeat reports a session as gone. Owns the two causes behind the same error message, the link-opened-in-the-owning-account rule, the consumed-session state, and the capture-and-delete contract.
role: functional
bot: mavis-google-access-bot
---

# mavis-skill-photo-picker

**Role.** The only sanctioned door to the user's own photo library, and the
automation around the one human action it requires.

---

## 1. Why it exists (the defect, not the preference)

Popy opened the picker URI and got:

> **Couldn't open Google Photos.** Go back to the partner app, website, kiosk or
> other device that you started from and connect to Google Photos again.

The discovery document (`photospicker` v1, rev. **20261026**) names **two**
causes for that identical message:

> To view this page successfully, the user must be logged into the Google
> account that owns this session in their web browser. The `pickerUri` cannot be
> opened in an iframe due to security reasons.

So guessing was worthless. The URI had to be opened in a **controlled
context** and the page **read** — in Chrome with the own profile (signed in as
`apvizual@gmail.com`, the account that owns the token) the same URI answers
`Search your photos and albums`; in another browser it answers the error.

**The link is not the deliverable. The opened window is.**

---

## 2. What Google's design allows, measured

| | |
|---|---|
| Library read | **only** app-created content (`photoslibrary.readonly.appcreateddata`) |
| Full library | **unreachable** — Google retired `photoslibrary.readonly`, `photoslibrary` and `sharing` on **31 March 2025** |
| The one door | the **Photo Picker**: the user selects, the app receives only what was selected |
| The selection | by design, **human** — it cannot be automated, and should not be |

Popy's decision: *"Din bibliotecă pot citi doar pozele pe care le selectezi tu,
prin picker."* The workflows are adapted to that; the library is not scraped.

---

## 3. The procedure

### 3.1 Open the picker window (the agent does this, not the user)

The agent opens the `pickerUri` in Chrome **with the own profile**, so the
account that owns the session is the one signed in. The user then selects and
presses Done.

### 3.2 Capture the selection, automatically

```powershell
node "C:\Users\apviz\.minimax-agent\projects\Mavis-Google_Access\scripts\picker-watch.mjs" `
     --session <sessionId> --data "C:\Users\apviz\.minimax\google-access\data" --delete-after

node "C:\Users\apviz\.minimax-agent\projects\Mavis-Google_Access\scripts\picker-download.mjs"
```

The watcher writes `data/picked-media.json`; the downloader fetches the media,
verifies **JPEG magic bytes** (`ff d8 ff`) and `content-type: image/jpeg` — a
`.jpg` that is actually an error page is rejected — and writes
`state/picked/<date>/` with a `manifest.json`.

### 3.3 Let the schedule do it

The task **`MavisPickerHeartbeat`** (every 15 minutes) runs the whole cycle
without a conversation being open. Any new selection lands automatically.

---

## 4. The consumed-session rule

The API asks clients to **delete** a session once it is done, so sessions do
not pile up (`sessions.create` returns `RESOURCE_EXHAUSTED` when they do).

Measured 2026-10-28: after the capture, the session was deleted (`HTTP 200`),
and the next poll answered `404 ENTITY_NOT_FOUND`. The heartbeat reported that
as a **failure** (exit 2), and the control point went **red** — for the user
doing the very thing the picker exists for.

**So: `404` is a state, not a defect.** The session file is *marked*
(`session_id: null, state: consumed`, `consumed_at`) — never deleted, because
the file is evidence — and the run ends green.

---

## 5. What it guarantees

- The user selects; the machine does everything else.
- A selection is captured even if no conversation is open.
- The downloaded file is a real JPEG, not an error page with a `.jpg` name.
- The session is cleaned up, so the next one can be created.

---

## 6. Known limits, stated out loud

- **The selection cannot be automated.** That is Google's design, not a gap in
  this setup.
- **The picker URI is bound to an OAuth session.** It opens only in the
  browser signed in as the account that owns it, and never in an iframe.
- **Only picker-selected content is readable.** The rest of the library is
  unreachable by any API, for anyone.
- **Sessions expire** (the measured one expired 2026-11-03). A new picker
  session has to be created.
- **This skill does not open the window for you** — it tells the agent how,
  and the agent opens it in the own profile.

---

## 7. Cross-references

- `mavis-skill-browser-mcp` — the browser layer that opens the window
- `mavis-skill-google-access-control-point` — `C9`, the picker check
- `mavis-google-access-bot` — the hub that owns this skill
- Docs: `Mavis-Google_Access/docs/TINERE-API-GOOGLE.md`
