# Bridge — Gemini

**Status**: 🟡 PARTIAL — Gemini API key is in Hermes's env (`AQ.A...WjUQ`) so Hermes can dispatch Gemini directly. Standalone `gemini` CLI is **NOT installed** on PATH. Mavis-side `google-ai` MCP not yet wired (would need an HTTP endpoint + API key).

## Role in the swarm

Gemini handles **multimodal vision**, **long-context reasoning**, and **Google Workspace integration**. Mavis dispatches to Gemini when the task exceeds Mavis's strengths or needs Google's ecosystem (Drive, Docs, Gmail, Calendar).

## Surface (live-verified 2026-09-18)

- **Web**: https://aistudio.google.com / https://gemini.google.com — accessible via Chrome
- **CLI**: `gemini` **NOT on PATH** (use via Hermes or via web)
- **API**: Google AI Studio / Vertex AI endpoints
- **MCP to Mavis**: **NOT wired standalone** (no `gemini` CLI binary). However:
  - Hermes has Google API key in its env → can dispatch Gemini via `hermes-mcp-router`
  - `gdrive-mcp`, `gmail-mcp`, `google-workspace-mcp`, `google-calendar-mcp` are wired (disabled pending OAuth)
- **Skill**: `google-workspace` skill installed (covers Gmail/Drive/Calendar/Docs once OAuth is bootstrapped)

## Activation (Hermes-side already done)

- ✅ Hermes has Google/Gemini API key
- [ ] Decide whether to wire a direct `google-ai` MCP to Mavis, or always go via Hermes
- [ ] If direct: need Gemini API key in Mavis env + an HTTP MCP endpoint

## Use cases

- Image understanding (vision tasks)
- 1M+ token context reasoning (long docs, video transcripts)
- Google Workspace automation (Drive, Docs, Sheets, Gmail) — via Hermes or Workspace MCP
- Cross-checking Mavis's analysis with a second perspective

## Dispatch protocol

**Prefer dispatch via Hermes** for now:

1. Construct the task contract
2. Dispatch via `hermes-mcp-router` MCP or `hermes-bridge` skill
3. Receive response with attribution
4. Integrate

If a direct Gemini MCP is wired later, use that instead.

## Cost awareness

Popy already has Google Pro access (Flow Studio). Check whether Gemini API calls cost extra or fall under existing quota before dispatching. **Never fabricate pricing** — verify in current Google AI pricing page if asked.

## JURNAL_OGLINDA

| Date | Event | Notes |
|---|---|---|
| 2026-09-18 | Bridge partially wired | 🟡 Hermes has Gemini key; standalone CLI not installed; Mavis-side direct Gemini MCP not wired. Use via Hermes for now. |

## Open questions for Popy (R0)

1. Wire a direct `google-ai` MCP to Mavis (needs API key in Mavis env), or always go via Hermes?
2. OAuth bootstrap for Gmail/Drive/Workspace MCPs — defer or prioritize?
3. Which Gemini model tier should be the default dispatch target (Flash, Pro, Ultra)?
