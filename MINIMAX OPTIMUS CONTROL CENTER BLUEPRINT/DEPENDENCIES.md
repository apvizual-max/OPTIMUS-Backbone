# DEPENDENCIES

**Measured, not remembered.** A version you recall is a hope. Every line below was
read off the machine the reference implementation runs on, on the date shown.

> Re-measure at the start of every build. Half this file is the kind of fact that
> was true in the morning and wrong by the afternoon — a model, a port, a tool
> that was never installed at all.

---

## 1 — Required to run a dashboard at all

| | Version | Why |
|---|---|---|
| **Windows PowerShell 5.1** | 5.1.26100.9549 | The whole server, collector and supervisor are PowerShell. |

> ⚠ **Not `pwsh`.** PowerShell 7 is not installed on this machine, and 5.1 has
> behaviour the code depends on *and* behaviour the code must defend against. The
> most expensive bug in the reference implementation came from a 5.1 rule: **a
> native command writing to STDERR becomes a terminating error** under
> `$ErrorActionPreference='Stop'`. Any external call needs its own scope for that
> preference, or its stderr will be reported as a crash.

## 2 — Required to build and test

| | Version | Used for |
|---|---|---|
| **Node.js** | v26.5.1 | `node --check` on the page's inline script; the self-test |
| **curl.exe** | 8.21.0.0 | driving the HTTP endpoints from the self-test |

Node is used as a **parser**, not a runtime. The page itself needs no JavaScript
toolchain, no package manager and no build step. If Node is absent, substitute any
JavaScript engine that can parse without executing.

## 3 — The system being observed

These are what the dashboard *talks to*. They are not its dependencies — its
**subject**. Their absence is a fact to display, not a reason not to build.

| | Version / state |
|---|---|
| **Docker** | 29.8.1, build 4a63305 — container count varies; ~60 at time of writing |
| **Ollama** | 0.35.1 — local model server |
| **mcode-tools** | 0.0.6 — MiniMax connector catalogue |
| **Git** | 2.56.0.windows.1 — read by the collector for source state |

## 4 — Ports

| Port | What | If it is gone |
|---|---|---|
| **8900** | the dashboard | — |
| 8801 | hermes bridge | reported DOWN, with a reason |
| 8802 | antigravity bridge | reported DOWN, with a reason |
| 8765 | qwen ACP | reported DOWN, with a reason |
| 11434 | Ollama | "model provider unavailable" — the single most misdiagnosed failure in the swarm |

**11434 deserves its own note.** A service that is *installed and up* but has
**no useful model behind it** presents identically to a service that is not
installed. The reference implementation found an agent "installed and configured"
that was pointed at a 1.5-billion-parameter model — the only one present. **Verify
the model exists, not the executable.**

## 5 — Machine constraints that shaped the design

| | |
|---|---|
| OS | Windows 11 Pro, build 26100 |
| CPU | Intel Xeon E5-2690 v3 @ 2.60 GHz — **12 physical / 24 logical** |
| RAM | 63.9 GB, **no discrete GPU** |
| Disk C: | 15.4 GB free at time of writing |

These are not trivia. They decided three things:

- **CPU-only inference.** A 7B local model is the realistic ceiling; a 32B is not
  usable. Anything larger belongs on an API.
- **Disk is tight.** Models and a 30 MB restore point share one volume. Measure
  what a dashboard costs *before* choosing refresh frequency.
- **No `pwsh`.** Every script here is 5.1-safe, and every script here is
  5.1-*careful*.

## 6 — Nothing external

**Zero.** No CDN, no webfont, no analytics, no package registry at runtime. The
icon font is a generated subset served from beside the page, so the whole thing
opens on a machine with no network — and a test *asserts* the count is zero rather
than trusting it.

---

## Re-measuring

```powershell
$PSVersionTable.PSVersion; node --version; docker --version
git --version; python --version; ollama --version
```

For anything that must be true at build time rather than remembered, put it in a
script that exits non-zero when the assumption is wrong. **A dependency you have
not executed is a hope, and stage 3 requires proof.**

---

## The record that is not a version

The most expensive thing this project lacked was never a tool. It was a
**dependency nobody had checked**: an agent described as installed and configured,
pointed at a model that did not exist. No version check would have caught it,
because the tool *was* installed and *was* configured.

**What the version table cannot tell you, ask directly:** what is it pointed at,
and does that target actually work? Then measure it.
