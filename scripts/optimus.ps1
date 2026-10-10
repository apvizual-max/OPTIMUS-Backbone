<#
.SYNOPSIS
  OPTIMUS unified CLI - one command for the whole MiniMax + Hermes ecosystem.

.DESCRIPTION
  Popy's requirement: MiniMax Code, Design and CLI must behave as ONE integrated
  ecosystem, not as three separate interfaces.

  Reality of this machine (verified 2026-10-02):
    - MiniMax Code   : desktop app, C:\Users\apviz\AppData\Local\Programs\MiniMax Code
    - MiniMax Design : desktop app, C:\Users\apviz\AppData\Local\Programs\MiniMax Design
    - MiniMax CLI    : there is NO separate 'minimax' product. The official CLI
                       surface is `mcode-tools`, and it is a shim that runs
                       MiniMax Code.exe in node mode and authenticates through
                       the RUNNING app's shared auth broker.
      => Code and CLI are already the same binary and the same identity.
         This command is the single front door over that, not a new product.

  Usage:  optimus <command> [args...]
  Run `optimus help` for the full command list.
#>
[CmdletBinding()]
param(
  [Parameter(Position = 0)][string]$Command = 'help',
  [Parameter(Position = 1, ValueFromRemainingArguments = $true)][string[]]$Rest
)
$ErrorActionPreference = 'Continue'
$PROJECTS = 'C:\Users\apviz\.minimax-agent\projects'
$SCRIPTS  = "$PROJECTS\scripts"

# ------------------------------------------------------------------ helpers --
function Section($t) { Write-Host "`n=== $t ===" -ForegroundColor Cyan }
function Say-Ok($m) { Write-Host "  [ok]    $m" -ForegroundColor Green }
function Say-Warn($m) { Write-Host "  [warn]  $m" -ForegroundColor Yellow }
function Say-Bad($m) { Write-Host "  [FAIL]  $m" -ForegroundColor Red }
function Say-Info($m) { Write-Host "  $m" -ForegroundColor DarkGray }
function HttpJson($u, $t = 20) {
  try { Invoke-RestMethod $u -TimeoutSec $t } catch { $null }
}
# A probe against a web UI returns markup, not JSON. Summarise it rather than
# dumping a wall of <script> into a terminal or the dashboard.
function Clip($s, $n = 120) {
  $x = [string]$s
  if ($x.Length -le $n) { return $x }
  return $x.Substring(0, $n) + " ... [$($x.Length - $n) more chars]"
}

# ----------------------------------------------------------------- commands --
function Cmd-Status {
  Section 'OPTIMUS STATUS'
  $n = (docker ps --format '{{.Names}}' 2>$null | Measure-Object).Count
  $mcp = (docker ps --format '{{.Names}}' --filter 'name=hermes-mcp-' 2>$null | Measure-Object).Count
  if ($n) { Say-Ok "docker containers : $n  (hermes-mcp-*: $mcp)" } else { Say-Bad 'docker not responding' }

  foreach ($p in @(8801, 8802)) {
    $h = HttpJson "http://127.0.0.1:$p/health" 8
    if ($h) { Say-Ok ("{0,-24} :{1}  up {2}s" -f $h.service, $p, $h.uptime_s) } else { Say-Bad "bridge :$p down" }
  }
  $s = HttpJson 'http://127.0.0.1:8082/' 8
  if ($s) { Say-Ok 'stirling-pdf        : http://127.0.0.1:8082' } else { Say-Warn 'stirling-pdf not answering' }

  $auth = & mcode-tools auth status 2>$null | ConvertFrom-Json 2>$null
  if ($auth) { Say-Ok ("minimax cli auth    : {0} ({1})" -f $auth.status, $auth.auth_mode) }
  else { Say-Warn 'minimax cli auth status unavailable (is MiniMax Code running?)' }

  $sk = (Get-ChildItem 'C:\Users\apviz\.minimax\agents\mavis\skills' -Directory -ErrorAction SilentlyContinue | Measure-Object).Count
  Say-Ok "mavis skills        : $sk"
  $v = HttpJson 'http://127.0.0.1:8765/health' 6
  if ($v) { Say-Ok 'qwen daemon        : http://127.0.0.1:8765' } else { Say-Warn 'qwen daemon not listening' }
}

function Cmd-Doctor {
  $deep = $Rest -contains '--deep'
  Section 'HERMES BRIDGE DOCTOR'
  $d = HttpJson 'http://127.0.0.1:8801/doctor/detailed' 90
  if (-not $d) { Say-Bad 'no response from 8801'; return }
  # Map severity to a real colour and pass it to Write-Host. The previous
  # version built a command name like "Write-Green" and invoked it, which does
  # not exist -- `optimus doctor` failed outright.
  $color = @{ ok = 'Green'; warn = 'Yellow'; fail = 'Red' }
  $d.checks | ForEach-Object {
    $c = if ($color.ContainsKey($_.severity)) { $color[$_.severity] } else { 'Gray' }
    Write-Host ("  {0,-4} {1,-30} {2}" -f $_.severity, $_.id, (Clip $_.detail 120)) -ForegroundColor $c
  }
  Write-Host ("`n  health={0}  ok={1} warn={2} fail={3}" -f $d.health, $d.ok_count, $d.warn_count, $d.fail_count) -ForegroundColor Cyan

  Section 'ANTIGRAVITY BRIDGE DOCTOR'
  $a = HttpJson 'http://127.0.0.1:8802/doctor/detailed' 60
  if ($a) {
    $a.checks | Where-Object { $_.severity -ne 'ok' -or $deep } | ForEach-Object {
      Write-Host ("  {0,-4} {1,-30} {2}" -f $_.severity, $_.id, $_.detail) -ForegroundColor $(if ($_.severity -eq 'fail') { 'Red' } elseif ($_.severity -eq 'warn') { 'Yellow' } else { 'Green' })
    }
  } else { Say-Bad 'no response from 8802' }
}

function Cmd-Bridge {
  $sub = if ($Rest) { $Rest[0] } else { 'health' }
  switch ($sub) {
    'health' {
      foreach ($p in @(8801, 8802)) { $h = HttpJson "http://127.0.0.1:$p/health" 10; if ($h) { $h | ConvertTo-Json } else { Say-Bad ":$p down" } }
    }
    'doctor' {
      $t = if ($Rest.Count -gt 1) { $Rest[1] } else { 'hermes' }
      $p = if ($t -match 'agy|anti') { 8802 } else { 8801 }
      HttpJson "http://127.0.0.1:$p/doctor/detailed" 90 | ConvertTo-Json -Depth 6
    }
    'delegate' {
      $t = $Rest[1]; $prompt = $Rest[2..($Rest.Count - 1)] -join ' '
      $p = if ($t -match 'agy|anti') { 8802 } else { 8801 }
      $body = @{ prompt = $prompt; timeout = 300 } | ConvertTo-Json
      (HttpJson "http://127.0.0.1:$p" 5) | Out-Null
      Invoke-RestMethod "http://127.0.0.1:$p/delegate" -Method POST -Body $body -ContentType 'application/json' -TimeoutSec 30 | ConvertTo-Json -Depth 5
    }
    'journal' {
      $p = if ($Rest.Count -gt 1 -and $Rest[1] -match 'agy|anti') { 8802 } else { 8801 }
      HttpJson "http://127.0.0.1:$p/journal?limit=10" 20 | ConvertTo-Json -Depth 6
    }
    default { Write-Host "bridge subcommands: health | doctor | delegate | journal" -ForegroundColor Yellow }
  }
}

function Cmd-Ai {
  $sub = if ($Rest) { $Rest[0] } else { 'tools' }
  switch ($sub) {
    'auth'   { & mcode-tools auth status 2>&1 }
    'tools'  {
      if ($Rest.Count -gt 1) { & mcode-tools connector tools --keyword $Rest[1] 2>&1 }
      else { & mcode-tools connector tools 2>&1 }
    }
    'schema' { & mcode-tools connector tool $Rest[1] 2>&1 }
    'call'   { & mcode-tools connector call $Rest[1] --args $Rest[2] 2>&1 }
    'url'    { & mcode-tools get-asset-url $Rest[1] 2>&1 }
    default  { Write-Host 'ai subcommands: auth | tools [keyword] | schema <tool> | call <tool> <json> | url <node_id>' -ForegroundColor Yellow }
  }
}

function Cmd-App {
  $which = if ($Rest) { $Rest[0] } else { 'status' }
  $map = @{
    code   = "$env:LOCALAPPDATA\Programs\MiniMax Code\MiniMax Code.exe"
    design = "$env:LOCALAPPDATA\Programs\MiniMax Design\MiniMax Design.exe"
  }
  switch ($which) {
    'status' {
      foreach ($k in 'code', 'design') {
        $e = $map[$k]; $d = Split-Path $e -Parent
        if (Test-Path $e) { Say-Ok ("{0,-7} installed : {1}" -f $k, $d) } else { Say-Warn ("{0,-7} not found : {1}" -f $k, $d) }
      }
      $p = Get-Process -Name 'MiniMax Code' -ErrorAction SilentlyContinue
      if ($p) { Say-Ok ("MiniMax Code RUNNING (pid {0}) - required for cli auth broker" -f ($p.Id -join ',')) }
      else { Say-Warn 'MiniMax Code NOT running - `mcode-tools` auth broker will fail' }
    }
    default {
      if ($map.ContainsKey($which)) {
        if (Test-Path $map[$which]) { Start-Process $map[$which]; Say-Ok "launched $which" }
        else { Say-Bad "$which not installed" }
      } else { Write-Host 'app subcommands: status | code | design' -ForegroundColor Yellow }
    }
  }
}

function Cmd-Doc {
  $sub = if ($Rest) { $Rest[0] } else { 'help' }
  switch ($sub) {
    'convert' { & "$SCRIPTS\convert-document.ps1" -InputPath $Rest[1] -Format $(if ($Rest.Count -gt 2) { $Rest[2] } else { 'pdf' }) }
    { $_ -in 'pdfa', 'img', 'word', 'merge' } {
      & "$SCRIPTS\stirling-pdf.ps1" -Operation $sub -InputPath $Rest[1..($Rest.Count - 1)]
    }
    default { Write-Host 'doc subcommands: convert <file> [fmt] | pdfa <file> | img <file> | word <file> | merge <f1> <f2>...' -ForegroundColor Yellow }
  }
}

function Cmd-Qwen {
  $sub = if ($Rest) { $Rest[0] } else { 'status' }
  $q = "$env:LOCALAPPDATA\qwen-code\bin\qwen.cmd"
  switch ($sub) {
    'status' {
      $l = Get-NetTCPConnection -LocalPort 8765 -State Listen -ErrorAction SilentlyContinue
      if ($l) { Say-Ok "daemon listening on 8765 (pid $($l.OwningProcess))" } else { Say-Warn 'daemon not listening' }
      if (Test-Path "$env:USERPROFILE\.qwen\oauth_creds.json") { Say-Ok 'oauth credential present' }
      else { Say-Warn 'NO oauth credential - run: qwen auth qwen-oauth' }
      & docker ps --filter 'name=hermes-mcp-qwen' --format '  hermes-mcp-qwen : {{.Status}}' 2>&1
    }
    'doctor' {
      # The real three-layer ACP diagnosis, straight from the adapter. The
      # dashboard's "Qwen ACP doctor" button calls this; without it the command
      # fell through to the help text and did nothing.
      $py = 'C:\Users\apviz\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe'
      $adapter = "$SCRIPTS\qwen_acp_mcp.py"
      if (-not (Test-Path $adapter)) { Say-Bad "adapter missing: $adapter"; return }
      & $py -c @"
import sys, json
sys.path.insert(0, r'$SCRIPTS')
import qwen_acp_mcp as A
print(A.qwen_doctor())
"@ 2>&1 | Where-Object { $_ -notmatch '^\s*$' }
    }
    'serve'  { Start-Process $q -ArgumentList @('serve', '--port', '8765', '--hostname', '127.0.0.1', '--no-open'); Say-Ok 'qwen serve started on 8765' }
    'auth'   { & $q auth qwen-oauth }
    default  { Write-Host 'qwen subcommands: status | serve | auth' -ForegroundColor Yellow }
  }
}

function Cmd-Docker {
  $sub = if ($Rest) { $Rest[0] } else { 'census' }
  switch ($sub) {
    'census' {
      $all = docker ps --format '{{.Names}}' 2>$null
      Say-Ok ("total containers : {0}" -f ($all | Measure-Object).Count)
      Say-Ok ("hermes-mcp-*     : {0}" -f ($all | Where-Object { $_ -like 'hermes-mcp-*' } | Measure-Object).Count)
      Say-Info ("other            : {0}" -f ($all | Where-Object { $_ -notlike 'hermes-mcp-*' } | Measure-Object).Count)
      Say-Info 'NEVER run: docker container prune -a  (lost the swarm 2026-08-08)'
    }
    default { docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' 2>&1 | Select-Object -First 60 }
  }
}

function Cmd-Sot {
  $sub = if ($Rest) { $Rest[0] } else { 'list' }
  switch ($sub) {
    'build' { & powershell -NoProfile -ExecutionPolicy Bypass -File "$SCRIPTS\build-sot-index.ps1" }
    'list' {
      foreach ($root in @("$SCRIPTS", "$PROJECTS\60_SKILLS\_links", "$PROJECTS\70_CONNECTORS\_links")) {
        Section $root
        foreach ($l in (Get-ChildItem $root -Force -ErrorAction SilentlyContinue | Where-Object { $_.LinkType })) {
          if ($l.LinkType -eq 'HardLink') {
            # A hard link's "Target" is just another path to the SAME inode. If
            # that other path is in the Recycle Bin the display is misleading --
            # the file at this path is complete and usable. Report the ref count
            # and whether the sibling still resolves instead.
            $refs = @($l.Target).Count
            $live = @($l.Target | Where-Object { Test-Path -LiteralPath $_ }).Count
            $note = if ($live -eq 0) { ' [sibling trashed - this path is complete]' } else { '' }
            Write-Host ("  {0,-26} HardLink  {1} ref(s){2}" -f $l.Name, $refs, $note) -ForegroundColor DarkCyan
          } else {
            Write-Host ("  {0,-26} Junction   -> {1}" -f $l.Name, (@($l.Target) -join '')) -ForegroundColor DarkCyan
          }
        }
      }
    }
    default { Write-Host 'sot subcommands: list | build' -ForegroundColor Yellow }
  }
}

function Cmd-Skills {
  $sub = if ($Rest) { $Rest[0] } else { 'list' }
  $m = 'C:\Users\apviz\.minimax\agents\mavis\skills'
  $p = 'C:\Users\apviz\.minimax\skills'
  switch ($sub) {
    'list' {
      Section "MAVIS SKILLS ($((Get-ChildItem $m -Directory -EA SilentlyContinue | Measure-Object).Count))"
      Get-ChildItem $m -Directory -EA SilentlyContinue | Select-Object -ExpandProperty Name | Sort-Object
      Section "PERSONAL SKILLS ($((Get-ChildItem $p -Directory -EA SilentlyContinue | Measure-Object).Count))"
      Say-Info 'see 60_SKILLS\_links\personal-skills'
    }
    default { Write-Host 'skills subcommands: list' -ForegroundColor Yellow }
  }
}

function Cmd-Minimax {
  $sub = if ($Rest) { $Rest[0] } else { 'doctor' }
  $py = 'C:\Users\apviz\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe'
  $client = "$SCRIPTS\minimax_client.py"
  switch ($sub) {
    'doctor' { & $py $client doctor 2>&1 }
    'ask'    {
      $model = $null
      if ($Rest -contains '--model') {
        $i = [array]::IndexOf($Rest, '--model')
        if ($i -ge 0 -and $Rest.Count -gt $i + 1) { $model = $Rest[$i + 1] }
      }
      $prompt = ($Rest | Select-Object -Skip 1) -join ' '
      if ($model) { & $py $client ask $prompt --model $model 2>&1 }
      else { & $py $client ask $prompt 2>&1 }
    }
    default  { Write-Host 'minimax subcommands: doctor | ask "<prompt>" [--model NAME]' -ForegroundColor Yellow }
  }
}

function Cmd-Help {
  Write-Host @'

  OPTIMUS unified CLI   (one front door for the whole ecosystem)

  CORE
    status                 one-screen status of every pillar
    doctor [--deep]        full health check across all pillars

  MINIMAX ECOSYSTEM  (Code + Design + CLI, unified)
    ai auth                CLI authentication status
    ai tools [keyword]     list Connector tools
    ai schema <tool>       inspect one tool
    ai call <tool> <json>  call a Connector tool
    ai url <node_id>       short-lived Drive asset URL
    app status             are Code / Design installed, is Code running
    app code | design      launch a desktop app

  MINIMAX FROM PYTHON
    minimax doctor        credential + transport diagnosis
    minimax ask "<text>"  send a prompt to MiniMax-M3 from Python
    minimax ask "..." --model MiniMax-M2.7

  BRIDGES
    bridge health
    bridge doctor [hermes|antigravity]
    bridge delegate <hermes|antigravity> "<prompt>"
    bridge journal  [hermes|antigravity]

  DOCUMENTS
    doc convert <file> [fmt]      LibreOffice: pdf docx xlsx pptx html txt rtf md
    doc pdfa <file>               Stirling-PDF -> PDF/A
    doc img  <file>               Stirling-PDF -> images
    doc word <file>               Stirling-PDF -> Word
    doc merge <f1> <f2> ...       Stirling-PDF merge

  QWEN
    qwen status | serve | auth

  DOCKER
    docker census        counts (NEVER prune -a)
    docker ps            container table

  SOT  (source of truth index)
    sot list | build

  SKILLS
    skills list
'@ -ForegroundColor Cyan
}

# -------------------------------------------------------------------- main --
switch ($Command.ToLower()) {
  'status'  { Cmd-Status }
  'doctor'  { Cmd-Doctor }
  'bridge'  { Cmd-Bridge }
  'ai'      { Cmd-Ai }
  'app'     { Cmd-App }
  'minimax' { Cmd-Minimax }
  'doc'     { Cmd-Doc }
  'qwen'    { Cmd-Qwen }
  'docker'  { Cmd-Docker }
  'sot'     { Cmd-Sot }
  'skills'  { Cmd-Skills }
  'help'    { Cmd-Help }
  default   { Say-Bad "unknown command '$Command'"; Cmd-Help }
}



