# Reference Specification: Antigravity Desktop App Integrated Terminal

## 1. Objective
Provide a fully interactive terminal workspace directly inside the Antigravity Desktop App, allowing seamless execution of PowerShell, Antigravity CLI (`agy`), and Gemini CLI without needing external windows or IDE switching.

## 2. Architecture
- **Frontend Panel:** Embedded `xterm.js` viewport rendered within the Desktop App layout.
- **Backend Bridge:** Lightweight WebSocket server connected to `node-pty` running on `localhost:9877`.
- **Environment Ingestion:**
  - PATH configured with Python virtual environments, Git, Node, and Google Cloud SDK.
  - Default Shell: PowerShell 7 (`pwsh.exe`) or Windows PowerShell 5.1 (`powershell.exe`).
  - Terminal Session Multiplexing: Support for multiple concurrent tabs (e.g. Tab 1: PowerShell, Tab 2: `agy` CLI, Tab 3: Gemini CLI).

## 3. Pre-Configured CLI Commands
- `agy`: Launches the Antigravity CLI agent in the current workspace directory.
- `gemini`: Interacts with the Gemini CLI runner.
- Hotkey integration for toggling terminal focus (`Ctrl + \``).
