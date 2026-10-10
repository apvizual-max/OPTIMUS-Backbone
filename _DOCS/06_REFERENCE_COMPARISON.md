# 06 — REFERENCE COMPARISON (Qwen dashboard, `:3098`)

**Read-only. The reference is live work and must not be modified.** Everything below
was obtained by reading its DOM and its served HTML. Nothing was written, clicked
into a state, or triggered on it.

This file exists because a comparison you only ever read in a chat transcript is a
comparison that is gone. The list of ideas the reference still has that the Control
Center does not is worth keeping in the same place as everything else.

---

## 1. What was compared

| | Reference `:3098` | Control Center `:8900` |
|---|---|---|
| Title | Qwen Ecosystem Control Dashboard | MiniMax OPTIMUS Control Center |
| Model | **one scrolling page** | **15 tabs** |
| Served HTML | 320 KB | 137 KB |
| Cards / panels | 39 | 15 tab views |
| Buttons | 56 | 86 controls (all wired) |
| Inputs | 29 | 4 |
| Tables | 3 | 1 |
| Charts | 2 inline SVG | area charts + heatmap + sparklines |
| **External resources** | **0** | **0** |

**The one property we both have is zero external resources.** That was the original
inspiration and it held: both dashboards are fully self-contained, no CDN, no font
host, no network dependency. If you are reading this on a machine with no internet,
both still work.

Where the models genuinely differ: a single scroll page is *denser* and shorter to
grok; 15 tabs is *navigable* when the data set grows. The Control Center has 58
containers, 15 status cards and a reachability graph — the reference has 7
supervised ports. **At our volume tabs win; at theirs, the scroll would too.** The
right trigger for revisiting this is not taste, it is the moment a tab stops fitting
on one screen.

---

## 2. What the reference has that we do not

### 2.1 Build currency — **the one worth taking**

> *"A running process never re-reads the file it booted from. This compares the
> process start time against the deployed file mtime. If the process is older, your
> patched code is on disk but not running — a restart is required before any change
> can take effect."*

This is not a feature we lack for want of polish. **It is the exact class of mistake
made twice in this project on 2026-10-04** while fixing the refresher deadlock and
while reverting it: `api\server.ps1` was edited, and the running server kept
executing the previous version until someone remembered to kill it. The second time,
the console went down entirely before the restart was noticed.

The reference converts *"remember to restart"* from a discipline into a **red line
on a card**. For a system that is edited many times a day and supervised by a
watchdog, that is the difference between a convention and a guarantee.

What it would compare: `server.ps1` mtime vs the running server process start time;
`cc-watchdog.ps1` mtime vs `watchdog_started` (already in `cc-health.json`).
A process older than its own source is running code that no longer exists on disk.

**Not implemented.** It is a new capability on a system its owner is not currently
consulting, and it was found by reading someone else's work — the decision belongs
to him, not to the reader.

### 2.2 Command history

The reference keeps a **persistent, clearable history with a run count**
(`Command History — 12 runs`, with a Clear). The Control Center's action runner
shows output that survives the poll but **keeps no record**: after a re-render the
answer to "what did I just run, and did it change anything" is gone, and the only
evidence is scrollback or a log file on disk.

### 2.3 Interactive CLI terminal

A terminal in the page, with copy-transcript, download, and clear. Ours offers a
**whitelist of one-shot actions** — which is the safer design and the right default
for a console that runs unattended. The reference's runner is more powerful and
more dangerous. Worth considering only behind the same whitelist the actions
already use, and only if Popy wants a terminal rather than a menu.

### 2.4 Silent risk register

A standing register of known risks, scanning. This aligns almost exactly with the
purpose of `05_POSTMORTEMS.md` — the same discipline of *recording the things that
fail quietly* — expressed as a live panel rather than a document. Ours has the
knowledge but not the surface.

### 2.5 Configuration audit

Per-artifact verdicts with explicit **STALE / VALID** states and a `Last Checked`
timestamp. Ours reports the compose file as present and parsing, but has no notion
of a config being *stale* relative to what is running — see 2.1, which is the same
idea applied to code.

---

## 3. What the Control Center has that the reference does not

Recorded so this file is not mistaken for a scorecard in one direction. We are ahead
on:

- **Reachability & blast radius** — who restarts what, and what dies with it if one
  goes. The reference's port map lists ports; ours answers the 3 a.m. question.
- **Supervision tree** — who watches whom, rendered as a graph.
- **The down-vs-slow distinction** — a bridge that is up and answering late is
  reported differently from one that is down. The reference has no equivalent.
- **Build currency for the swarm** — a version store with a refusal past five.
- **Measured defect record** — 18 postmortems, each with the measurement that
  convicted it and the ones that did not.
- **A self-test that runs its own handlers** — the behavioural pass invokes
  `askAI` against a stubbed fetch and asserts the answer lands in a *connected*
  node. A file-level test cannot do that; it is why the AI Analyst shipped broken
  for its entire life without anyone noticing.

---

## 4. Standing rule for this file

**Read the reference; never write to it.** It is ongoing work by the same operator.
Everything in section 2 is an *idea to consider*, not a task list. Nothing here is
authorised, and nothing here has been built.
