<#
.SYNOPSIS
  SENTINEL Command Center - local loopback server for the MINIMAX SENTINEL BRAIN.

.DESCRIPTION
  A page loaded over file:// has no server behind it, so live monitoring and
  action buttons both require a local HTTP origin. This server provides it.

  Architecture is the one already proven on this machine at
  projects\90_CONTROL_CENTER (HttpListener + action whitelist + a background
  collector that writes a state file the requests only read). What is copied is
  the ARCHITECTURE, not the deployment: that server was down when this was
  built (cc-health.json: healthy=false, connection refused on 8900, 2 watchdog
  restarts), so the start/stop/restart cycle is proven here rather than assumed.

  Routes
    GET  /                 -> index.html
    GET  /api/state        -> sentinel-state.json (written by the refresh worker)
    GET  /api/health       -> monitor.py output (per-check OK|FAIL|STALE|NOT_RUN)
    GET  /api/corpus       -> paged corpus search (?q=...&limit=...&chapter=...)
    GET  /api/history      -> state-history.jsonl tail
    GET  /api/stream       -> Server-Sent Events, pushes state on every refresh
    POST /api/action       -> run a WHITELISTED action by id, return its output

  SECURITY
    - Binds 127.0.0.1 only. Never reachable off-box.
    - The HTTP body supplies an action ID, never a command. The id is resolved
      through the $ACTIONS whitelist below, so a crafted request cannot execute
      arbitrary shell. An unknown or injected id returns 400.
    - Action output is size-capped.
    - No action may write outside SENTINEL_PRIME, touch E:\ or D:\, alter Docker
      state, or reach the network.

  POWERSHELL
    Windows PowerShell 5.1 only (no pwsh on this machine). No ternary, no ??,
    no -Parallel.
#>
[CmdletBinding()]
param(
  [int]$Port = 8910,
  [int]$RefreshSeconds = 25,
  [switch]$NoBrowser
)

$ErrorActionPreference = 'Stop'
$ROOT = Split-Path -Parent $PSScriptRoot
$WORKSPACE = Split-Path -Parent $ROOT
$API = Join-Path $PSScriptRoot 'collect-sentinel.ps1'
$INDEX = Join-Path $ROOT 'index.html'
$STATE = Join-Path $PSScriptRoot 'sentinel-state.json'
$HISTORY = Join-Path $PSScriptRoot 'state-history.jsonl'
$HEALTH = Join-Path $PSScriptRoot 'health.json'
$PY = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $PY) { throw 'python not on PATH' }

if (-not (Test-Path $INDEX)) { throw "index.html not found at $INDEX" }

# The action id comes from the request. The command comes from THIS table and
# nowhere else. That single indirection is what makes the endpoint safe.
$ACTIONS = @{
  'wf_state'      = { & $PY (Join-Path $WORKSPACE '08_SELF_IMPROVEMENT\bimodal_workflow.py') 2>&1 }
  'wf_mode_a'     = { & $PY -c "import sys;sys.path.insert(0,r'$WORKSPACE\08_SELF_IMPROVEMENT');from bimodal_workflow import BimodalWorkflow;w=BimodalWorkflow();w.load();print(w.status_report())" 2>&1 }
  'tests_run'     = { & $PY (Join-Path $WORKSPACE '08_SELF_IMPROVEMENT\test_suite.py') 2>&1 }
  'corpus_verify' = { & $PY (Join-Path $WORKSPACE '08_SELF_IMPROVEMENT\corpus_extractor.py') verify 2>&1 }
  'corpus_digest' = { & $PY (Join-Path $WORKSPACE '08_SELF_IMPROVEMENT\corpus_extractor.py') digest 220 2>&1 }
  'matrix_dump'   = { & $PY -c "import json,io,os;p=os.path.join(r'$WORKSPACE','12_PROGRAM','IDEA_TO_SCRIPT_MATRIX.json');print(json.dumps(json.load(io.open(p,encoding='utf-8')),indent=2,ensure_ascii=False) if os.path.exists(p) else 'matrix not generated yet')" 2>&1 }
  'skills_list'   = { Get-ChildItem (Join-Path $WORKSPACE '07_BACKBONE\skills') -Filter *.md -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Name 2>&1 }
  'mcp_wiring'    = { & $PY -c "import re,io,os;p=os.path.join(r'$WORKSPACE','07_BACKBONE','mcp','sentinel_hub_server.py');t=io.open(p,encoding='utf-8').read();n=re.findall(r'name=.sentinel_[a-z0-9_]+.',t);print(f'{len(n)} tools DECLARED, 0 WIRED (no runtime handshake performed)');[print('  '+x) for x in n]" 2>&1 }
  'deps_check'    = { & $PY (Join-Path $WORKSPACE '08_SELF_IMPROVEMENT\monitor.py') 2>&1 }
  'self_check'    = { & $PY (Join-Path $WORKSPACE '08_SELF_IMPROVEMENT\self_improvement.py') 2>&1 }
  'logs_tail'     = { Get-Content (Join-Path $WORKSPACE '09_LOGS\bimodal_workflow.log') -Tail 25 -ErrorAction SilentlyContinue 2>&1 }
  'versions_list' = { & powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $ROOT 'bat\manage-versions.ps1') -List 2>&1 }
  'selfcheck'     = { & $PY -c "import sys;sys.path.insert(0,r'$WORKSPACE\08_SELF_IMPROVEMENT');import monitor,json;r=monitor.collect();print(json.dumps(r['counts']))" 2>&1 }
}

$MAX_OUTPUT = 200000

function Send-Response($ctx, $status, $contentType, $body, $extraHeaders) {
  # Headers must be written BEFORE anything is written to the stream, and only
  # ONCE. A browser that hung up mid-request leaves the response already
  # submitted, so re-entering here to send an error throws
  # "ContentLength64 cannot be set after the response has been submitted" and
  # that second error masks the real one. Guard the header write, and treat a
  # client disconnect as a normal event rather than a server fault.
  $bytes = [Text.Encoding]::UTF8.GetBytes($body)
  try {
    $ctx.Response.StatusCode = $status
    $ctx.Response.ContentType = $contentType
    $ctx.Response.ContentLength64 = $bytes.Length
    if ($extraHeaders) {
      foreach ($k in $extraHeaders.Keys) { $ctx.Response.Headers.Add($k, $extraHeaders[$k]) }
    }
  } catch {
    Write-Host "  (client gone: $($_.Exception.Message))" -ForegroundColor DarkGray
    return
  }
  try {
    $ctx.Response.OutputStream.Write($bytes, 0, $bytes.Length)
  } catch {
    Write-Host "  (write aborted, client gone)" -ForegroundColor DarkGray
  } finally {
    try { $ctx.Response.OutputStream.Close() } catch { }
  }
}

function Read-Body($ctx) {
  try {
    $reader = New-Object IO.StreamReader($ctx.Request.InputStream)
    $body = $reader.ReadToEnd()
    $reader.Close()
    return $body
  } catch { return '' }
}

function Invoke-Action($id) {
  if (-not $ACTIONS.ContainsKey($id)) { return $null }
  $out = & $ACTIONS[$id] 2>&1 | Out-String
  if ($out.Length -gt $MAX_OUTPUT) {
    $out = $out.Substring(0, $MAX_OUTPUT) + "`n...[output capped at $MAX_OUTPUT chars]"
  }
  return $out
}

function Search-Corpus($query, $limit) {
  $py = @"
import io, json, os, sys
q = sys.argv[1].lower()
limit = int(sys.argv[2])
path = os.path.join(r'$WORKSPACE', '11_BRAIN', '01_RAW', 'corpus_full.jsonl')
hits = []
with io.open(path, encoding='utf-8') as f:
    for line in f:
        m = json.loads(line)
        if m.get('kind') != 'verbatim':
            continue
        text = m.get('text') or ''
        if q in text.lower():
            hits.append({
                'seq': m['seq'], 'role': m['role'],
                'turn_id': m.get('turn_id'),
                'generation': m['source']['generation'],
                'excerpt': text[:600]
            })
            if len(hits) >= limit:
                break
print(json.dumps({'query': q, 'count': len(hits), 'hits': hits}, ensure_ascii=False))
"@
  $tmp = Join-Path $env:TEMP 'sentinel_corpus_search.py'
  Set-Content -Path $tmp -Value $py -Encoding UTF8
  try { return (& $PY $tmp $query $limit 2>&1 | Out-String) }
  finally { Remove-Item $tmp -ErrorAction SilentlyContinue }
}

# ---- background refresh worker -------------------------------------------
# The collector measures and writes. Requests only ever READ the file, so a
# poll costs ~0.01s regardless of how slow the measurement is.
$stateVersion = 0

function Start-RefreshWorker {
  $script:stateVersion = 0
  while ($true) {
    try {
      & powershell -NoProfile -ExecutionPolicy Bypass -File $API -Quiet | Out-Null
      $script:stateVersion++
    } catch {
      Write-Host "  (collector failed: $($_.Exception.Message))" -ForegroundColor Red
    }
    Start-Sleep -Seconds $RefreshSeconds
  }
}

Write-Host ''
Write-Host 'SENTINEL COMMAND CENTER' -ForegroundColor Cyan
Write-Host '  MINIMAX SENTINEL BRAIN - correlation of discussion, programme and self' -ForegroundColor DarkGray
Write-Host "  ui     : GET  http://127.0.0.1:$Port/" -ForegroundColor DarkGray
Write-Host "  state  : GET  http://127.0.0.1:$Port/api/state" -ForegroundColor DarkGray
Write-Host "  health : GET  http://127.0.0.1:$Port/api/health" -ForegroundColor DarkGray
Write-Host "  stream : GET  http://127.0.0.1:$Port/api/stream" -ForegroundColor DarkGray
Write-Host "  corpus : GET  http://127.0.0.1:$Port/api/corpus?q=..." -ForegroundColor DarkGray
Write-Host '  loopback only. Ctrl+C to stop.' -ForegroundColor DarkGray
Write-Host ''

# First collection before the listener opens, so the first request is not empty.
Write-Host 'collecting state (first pass)...' -ForegroundColor DarkGray
try { & powershell -NoProfile -ExecutionPolicy Bypass -File $API -Quiet | Out-Null }
catch { Write-Host "  (first collection failed: $($_.Exception.Message))" -ForegroundColor Red }
Write-Host "state ready. refresh every $RefreshSeconds s." -ForegroundColor Green
Write-Host ''

# Start the worker as a background job so the listener loop is not blocked.
$worker = Start-Job -ScriptBlock {
  param($apiPath, $seconds)
  while ($true) {
    & powershell -NoProfile -ExecutionPolicy Bypass -File $apiPath -Quiet | Out-Null
    Start-Sleep -Seconds $seconds
  }
} -ArgumentList $API, $RefreshSeconds

try {
  $listener = New-Object Net.HttpListener
  $listener.Prefixes.Add("http://127.0.0.1:$Port/")
  $listener.Start()
  Write-Host "listening on 127.0.0.1:$Port" -ForegroundColor Green

  if (-not $NoBrowser) { Start-Process "http://127.0.0.1:$Port/" }

  while ($listener.IsListening) {
    try {
      $ctx = $listener.GetContext()
    } catch {
      break
    }
    try {
      $path = $ctx.Request.Url.AbsolutePath
      $method = $ctx.Request.HttpMethod

      if ($method -eq 'POST' -and $path -eq '/api/action') {
        $body = Read-Body $ctx
        $id = ''
        try { $id = ($body | ConvertFrom-Json).id } catch { }
        if ([string]::IsNullOrWhiteSpace($id)) {
          Send-Response $ctx 400 'application/json' '{"error":"no action id supplied"}' $null
          continue
        }
        $out = Invoke-Action $id
        if ($null -eq $out) {
          # An unknown or injected id is refused here. This is the security
          # boundary, and it is verified by test rather than by inspection.
          Send-Response $ctx 400 'application/json' `
            ("{{""error"":""unknown or forbidden action id"",""id"":""{0}""}}" -f ($id -replace '"',"'")) $null
          continue
        }
        Send-Response $ctx 200 'text/plain; charset=utf-8' $out $null
        continue
      }

      if ($method -ne 'GET') {
        Send-Response $ctx 405 'text/plain' 'method not allowed' $null
        continue
      }

      switch ($path) {
        '/' {
          $html = Get-Content $INDEX -Raw -Encoding UTF8
          Send-Response $ctx 200 'text/html; charset=utf-8' $html $null
        }
        '/api/state' {
          if (Test-Path $STATE) {
            $json = Get-Content $STATE -Raw -Encoding UTF8
          } else {
            $json = '{"generated":null,"note":"no state collected yet"}'
          }
          Send-Response $ctx 200 'application/json; charset=utf-8' $json `
            @{ 'Cache-Control' = 'no-store' }
        }
        '/api/health' {
          if (Test-Path $HEALTH) {
            $json = Get-Content $HEALTH -Raw -Encoding UTF8
          } else {
            $json = '{"overall":"NOT_RUN","note":"monitor has not been run"}'
          }
          Send-Response $ctx 200 'application/json; charset=utf-8' $json `
            @{ 'Cache-Control' = 'no-store' }
        }
        '/api/history' {
          if (Test-Path $HISTORY) {
            $lines = Get-Content $HISTORY -Tail 120 -Encoding UTF8
            Send-Response $ctx 200 'application/json; charset=utf-8' ($lines -join "`n") `
              @{ 'Cache-Control' = 'no-store' }
          } else {
            Send-Response $ctx 200 'application/json' '[]' $null
          }
        }
        '/api/corpus' {
          $q = $ctx.Request.QueryString['q']
          $limit = $ctx.Request.QueryString['limit']
          if ([string]::IsNullOrWhiteSpace($q)) { $q = 'SENTINEL' }
          if ([string]::IsNullOrWhiteSpace($limit)) { $limit = 25 }
          $out = Search-Corpus $q $limit
          Send-Response $ctx 200 'application/json; charset=utf-8' $out `
            @{ 'Cache-Control' = 'no-store' }
        }
        '/api/stream' {
          # Server-Sent Events. Headers must be set once and the stream must
          # stay open; a client disconnect is normal, not an error.
          try {
            $ctx.Response.StatusCode = 200
            $ctx.Response.ContentType = 'text/event-stream'
            $ctx.Response.Headers.Add('Cache-Control', 'no-store')
            $ctx.Response.Headers.Add('Connection', 'keep-alive')
            $stream = $ctx.Response.OutputStream
            $lastVersion = -1
            while ($true) {
              if (Test-Path $STATE) {
                $stateItem = Get-Item $STATE
                $v = [int]$stateItem.LastWriteTimeUtc.Ticks
                if ($v -ne $lastVersion) {
                  $lastVersion = $v
                  $payload = Get-Content $STATE -Raw -Encoding UTF8
                  $chunk = "event: state`ndata: $payload`n`n"
                  $b = [Text.Encoding]::UTF8.GetBytes($chunk)
                  $stream.Write($b, 0, $b.Length)
                  $stream.Flush()
                }
              }
              Start-Sleep -Milliseconds 1500
            }
          } catch {
            # client closed the tab
          }
        }
        default {
          Send-Response $ctx 404 'text/plain' 'not found' $null
        }
      }
    } catch {
      Write-Host "  (request error: $($_.Exception.Message))" -ForegroundColor Red
    }
  }
}
finally {
  Write-Host ''
  Write-Host 'stopping...' -ForegroundColor DarkGray
  try { Stop-Job $worker -ErrorAction SilentlyContinue; Remove-Job $worker -Force -ErrorAction SilentlyContinue } catch { }
  try { $listener.Stop(); $listener.Close() } catch { }
}
