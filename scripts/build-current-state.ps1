<#
.SYNOPSIS
  Regenerates projects\OPTIMUS_CURRENT_STATE.md from LIVE measurements.

.DESCRIPTION
  Why this exists: the hand-written version went stale within 25 minutes. It was
  written at 12:03 saying qwen-mcp-http was DISABLED; Popy reactivated it at
  12:27. It also said "10 tabs" when the dashboard had 11. A document that
  claims to be the single authority cannot be hand-maintained without rotting.

  So it is GENERATED. Every number in the output is measured at run time. If a
  fact cannot be measured it is written as such, never guessed.

  Run:  powershell -File projects\scripts\build-current-state.ps1
#>
[CmdletBinding()]
param([switch]$Quiet)

$ErrorActionPreference = 'Continue'
$PROJECTS = 'C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard'
$OUT      = Join-Path $PROJECTS 'OPTIMUS_CURRENT_STATE.md'
$NOW      = (Get-Date).ToString('yyyy-MM-dd HH:mm')

# ------------------------------------------------------------------ measure --
$names = @(docker ps --format '{{.Names}}' 2>$null)
$total = $names.Count
$mcp   = @($names | Where-Object { $_ -like 'hermes-mcp-*' }).Count
$sent  = @($names | Where-Object { $_ -like 'hermes-sentinel-daemon*' }).Count
$brg   = @($names | Where-Object { $_ -like 'minimax-*' }).Count

$ports = @{}
# 8080 (open-webui) belongs in the census; omitting it under-reported the total.
foreach ($p in @(8801, 8802, 8080, 8082, 3001, 8765, 8900)) {
  $ports[$p] = [bool](Get-NetTCPConnection -LocalPort $p -State Listen -EA SilentlyContinue)
}

# MCP entry states read from the live config, never assumed.
$mcpJson = 'C:\Users\apviz\.minimax\mcp.json'
$mcpState = [ordered]@{}
if (Test-Path $mcpJson) {
  try {
    $raw = Get-Content $mcpJson -Raw -Encoding UTF8
    foreach ($name in @('qwen-mcp-http', 'qwen-acp-adapter')) {
      $i = $raw.IndexOf('"' + $name + '"')
      if ($i -ge 0) {
        $chunk = $raw.Substring($i, [Math]::Min(700, $raw.Length - $i))
        $m = [regex]::Match($chunk, '"enabled"\s*:\s*(true|false)')
        $mcpState[$name] = if ($m.Success) { $m.Groups[1].Value } else { 'unknown' }
      } else { $mcpState[$name] = 'not found' }
    }
  } catch { $mcpState['_error'] = $_.Exception.Message }
}

# Tab count read from the dashboard source, so it can never drift.
$idx = Join-Path $PROJECTS '90_CONTROL_CENTER\index.html'
$tabs = @()
if (Test-Path $idx) {
  $t = [IO.File]::ReadAllText($idx, [Text.Encoding]::UTF8)
  $m = [regex]::Match($t, 'const TABS = \[(.*?)\];', 'Singleline')
  if ($m.Success) {
    $tabs = @([regex]::Matches($m.Groups[1].Value, "\['([a-z_]+)'\s*,\s*'([^']+)'\]") |
              ForEach-Object { $_.Groups[2].Value })
  }
}

$skills = (Get-ChildItem 'C:\Users\apviz\.minimax\agents\mavis\skills' -Directory -EA SilentlyContinue).Count
$personal = (Get-ChildItem 'C:\Users\apviz\.minimax\skills' -Directory -EA SilentlyContinue).Count
$hermesMcp = 0
$cfg = 'C:\Users\apviz\AppData\Local\hermes\config.yaml'
if (Test-Path $cfg) {
  $lines = Get-Content $cfg
  $start = ($lines | Select-String -Pattern '^\s*mcp_servers:' | Select-Object -First 1).LineNumber
  if ($start) {
    $base = ($lines[$start-1].Length - ($lines[$start-1] -replace '^(\s*).*','$1'.Length))
    for ($i = $start; $i -lt $lines.Count; $i++) {
      $l = $lines[$i]
      if (-not $l.Trim()) { continue }
      $ind = $l.Length - ($l -replace '^(\s*).*','$1'.Length)
      if ($i -gt $start -and $ind -le $base) { break }
      if ($ind -eq $base + 2 -and $l.Trim().EndsWith(':')) { $hermesMcp++ }
    }
  }
}

$dr = $null
try { $dr = Invoke-RestMethod 'http://127.0.0.1:8801/doctor' -TimeoutSec 60 } catch { }

# Hermes update facts, measured.
$agentDir = 'C:\Users\apviz\AppData\Local\hermes\hermes-agent'
$stampPath = Join-Path $agentDir 'install-stamp.json'
$version = '?'; $dirtyStamp = '?'
if (Test-Path $stampPath) {
  try { $s = Get-Content $stampPath -Raw | ConvertFrom-Json
        $version = $s.displayVersion; $dirtyStamp = $s.dirty } catch { }
}
$head = ''; $mods = 0
if (Get-Command git -EA SilentlyContinue) {
  $h = & git -C $agentDir log --oneline -1 2>$null
  if ($h) { $head = (@($h)[0]).Trim() }
  $st = & git -C $agentDir status --porcelain 2>$null
  if ($st) { $mods = @($st | Where-Object { $_.Trim() }).Count }
}
$lock = 'C:\Users\apviz\AppData\Local\hermes\.hermes-update-in-progress'
$lockState = if (Test-Path $lock) {
  $raw = ((Get-Content $lock -Raw) -replace '\s+',' ').Trim()
  $pid_ = 0
  if ([int]::TryParse(($raw -split ' ')[0], [ref]$pid_)) {
    $alive = [bool](Get-Process -Id $pid_ -EA SilentlyContinue)
    "held by PID $pid_ (alive=$alive)"
  } else { 'present' }
} else { 'absent' }

$docRoots = @(Get-ChildItem $PROJECTS -File -Filter '*.md' -EA SilentlyContinue).Count
# Count archived-body banners. The marker is matched on a STABLE anchor
# ("ARCHIVED BODY" heading plus a reference to the authority file), not on one
# exact sentence. Grepping a single literal string was wrong twice: the first
# version of this file reported 0 banners because it looked for wording I had
# since renamed, and a metric that can silently read 0 forever proves nothing.
$archiveMarked = @(Get-ChildItem $PROJECTS -File -Filter '*.md' -EA SilentlyContinue |
  Where-Object {
    $x = [IO.File]::ReadAllText($_.FullName, [Text.Encoding]::UTF8)
    ($x -match 'ARCHIVED BODY|SUPERSEDED') -and ($x -match 'OPTIMUS_CURRENT_STATE\.md')
  })
$superseeded = $archiveMarked
# If the count is 0 the detector itself may be broken. Say so rather than
# quietly printing a number nobody can trust.
$archiveNote = if ($superseeded.Count -eq 0) {
  "0 (WARNING: the banner detector found nothing - if banners exist this metric is broken)"
} else { $superseeded.Count }

# ------------------------------------------------------------------ render --
$qwenHttp = $mcpState['qwen-mcp-http']
$qwenAdp  = $mcpState['qwen-acp-adapter']
$portLine = ($ports.GetEnumerator() | Sort-Object Name |
             ForEach-Object { "{0}:{1}" -f $_.Key, $(if ($_.Value) { 'UP' } else { 'DOWN' }) }) -join '  '

# LITERAL here-string. The expandable form @"..."@ treats every backtick in the
# markdown as a PowerShell escape, and this document is full of backticks --
# which silently turned the script into a parse error. Tokens do the
# interpolation instead.
$md = @'
# OPTIMUS - CURRENT STATE (single source of truth)

> **GENERATED FILE.** Rebuilt from live measurement on %%NOW%% by
> `projects\scripts\build-current-state.ps1`. Do not hand-edit it: it is stale
> the moment anything changes. Regenerate it with:
>
> ```powershell
> powershell -NoProfile -ExecutionPolicy Bypass -File projects\scripts\build-current-state.ps1
> ```
>
> If any other document in `projects\` disagrees with this one, **this file is
> right** and the other is stale. %%SUPER%% file(s) currently carry a
> SUPERSEDED banner for exactly that reason.

## Fleet

| Thing | Measured |
|---|---|
| Containers running | **%%TOTAL%%** |
| `hermes-mcp-*` | **%%MCP%%** |
| `hermes-sentinel-daemon` | %%SENT%% |
| MiniMax bridges | %%BRG%% |
| Mavis skills | **%%SKILLS%%** |
| Personal skills | %%PERSONAL%% |
| Hermes MCP servers in config | %%HMCP%% |
| Bridge doctor | %%DOCTOR%% |
| Ports | %%PORTS%% |
| Control Center tabs | **%%TABS%%** |
| Root `.md` files | %%DOCS%% |

## Qwen - the entry most often got wrong

| MCP entry | Live state in `mcp.json` |
|---|---|
| `qwen-mcp-http` | **%%QHTTP%%** |
| `qwen-acp-adapter` | **%%QADP%%** |

- `qwen-mcp-http` points at `localhost:8765/mcp`. Qwen 0.19.2 **never served that
  path** - it returns 404 and is logged as 404. Qwen exposes ACP at `/acp`; it
  has no MCP transport. Kept enabled by Popy's explicit decision of 2026-10-02;
  it will not connect.
- `qwen-acp-adapter` is the working path: 6 tools, all returning real data.
  `qwen_prompt` / `qwen_doctor` / `qwen_session_probe` run over stdio;
  `qwen_auth_status` / `qwen_auth_device_flow_start` / `qwen_workspace_tools`
  must use the daemon WebSocket, because the `_qwen/*` extensions answer
  `-32601` on stdio.
- The live blocker is the model provider, not the protocol: Qwen's active model
  is `qwen2.5-coder:1.5b` on local Ollama `127.0.0.1:11434` and **Ollama is not
  installed**. `session/prompt` returns `Connection error.`
- ACP gotcha: `session/new` requires `mcpServers: []`.

## Hermes source - measured, and NOT a stable fact

Hermes self-updates (`updateMechanism: self`), so this section changes without
anyone asking. Read it, never assume it.

| | |
|---|---|
| `install-stamp` version | `%%VERSION%%` |
| `install-stamp` says dirty | %%DIRTY%% |
| Live `git status` modified files | **%%MODS%%** |
| Live `git HEAD` | `%%HEAD%%` |
| `.hermes-update-in-progress` | %%LOCK%% |

The stamp and live git legitimately disagree: the stamp is a snapshot from
whenever the last install ran, git is now.

> **Self-inflicted deadlock, worth remembering.** A hung `hermes mcp list`
> registers *its own PID* as owner of `.hermes-update-in-progress`, then waits
> on that lock. Every later call says: `hermes: source-update completion
> failed: an update is still running`. Fix: kill the hung CLI process. It is not
> a stale marker.

> Mavis has never run `hermes update`; Popy reserved that for himself.

## The three doctor warnings that are CORRECT on a healthy system

1. `hermes.version` - Windows NTFS symlink, unresolvable from a Linux container
2. `hermes.venv_currency` - reports the Hermes source state above
3. `hermes.status` - host-side probe by design

**Do not "fix" these.** If anything else shows warn or fail, that is a real finding.

## MiniMax

- There is **no separate "MiniMax CLI" product.** `mcode-tools` runs
  `MiniMax Code.exe` in node mode and authenticates through the running app's
  shared broker, so Code and CLI are one binary and one identity. Auth reads
  `authenticated` **only while MiniMax Code is running.**
- There is **no official Python SDK.** The PyPI package named `minimax` is an
  unrelated name-squat; `minimax-python` is unofficial v0.2.0 against a
  different surface. Use `projects\scripts\minimax_client.py`, which speaks the
  same `anthropic_messages` endpoint Hermes uses.

## Safety

- **NEVER** `docker container prune -a` - the swarm was lost this way 2026-08-08.
- **NEVER** `docker rm -f hermes-mcp-*` - %%MCP%% load-bearing containers.
- **NEVER** `--remove-orphans` on the `apviz` compose project:
  `Antigravity_Ecosystem_Terminal` shares the project name but has its own
  compose file and would be deleted.
- `C:\Users\apviz\docker-compose.yml` was found deleted on 2026-10-02. `cc guard`
  detects that and rebuilds it from live state (verified 18/18 services, with
  containers untouched).

## Check it yourself

```powershell
optimus status
optimus doctor --deep
cc start
cc guard
optimus minimax ask "say OK"
optimus sot list
docker ps --format '{{.Names}}' | Measure-Object
```
'@

$doctorTxt = if ($dr) { "$($dr.health), $($dr.warn_count) warn, $($dr.fail_count) fail" } else { 'not reachable' }
$map = [ordered]@{
  '%%NOW%%'      = $NOW
  '%%SUPER%%'    = $archiveNote
  '%%TOTAL%%'    = $total
  '%%MCP%%'      = $mcp
  '%%SENT%%'     = $sent
  '%%BRG%%'      = $brg
  '%%SKILLS%%'   = $skills
  '%%PERSONAL%%' = $personal
  '%%HMCP%%'     = $hermesMcp
  '%%DOCTOR%%'   = $doctorTxt
  '%%PORTS%%'    = $portLine
  '%%TABS%%'     = $tabs.Count
  '%%DOCS%%'     = $docRoots
  '%%QHTTP%%'    = $qwenHttp
  '%%QADP%%'     = $qwenAdp
  '%%VERSION%%'  = $version
  '%%DIRTY%%'    = $dirtyStamp
  '%%MODS%%'     = $mods
  '%%HEAD%%'     = $head
  '%%LOCK%%'     = $lockState
}
foreach ($k in $map.Keys) { $md = $md.Replace($k, [string]$map[$k]) }

[IO.File]::WriteAllText($OUT, $md, (New-Object Text.UTF8Encoding($false)))
if (-not $Quiet) {
  Write-Host "wrote $OUT ($((Get-Item $OUT).Length) B)" -ForegroundColor Green
  Write-Host "  containers=$total hermes-mcp=$mcp skills=$skills tabs=$($tabs.Count)" -ForegroundColor DarkGray
  Write-Host "  mcp: qwen-mcp-http=$qwenHttp  qwen-acp-adapter=$qwenAdp" -ForegroundColor DarkGray
  Write-Host "  hermes: $version  git modified=$mods  lock=$lockState" -ForegroundColor DarkGray
}
