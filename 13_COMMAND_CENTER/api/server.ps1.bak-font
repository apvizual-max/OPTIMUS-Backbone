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
# The lifecycle verifier's own result. Served so the panel can display the last
# real run. Until this route existed, verify-server.ps1 wrote a report that
# nothing on this machine could read - its own docstring and the README both
# claimed the Overview panel displayed it, and neither was true.
$VERIFY = Join-Path $PSScriptRoot 'verify-report.json'
# The MINIMAX ecosystem snapshot. Same directory as the other JSON the server
# reads, but produced by a different collector on a different cadence - see
# the /api/minimax route for why it is not merged into the state file.
$MINIMAX = Join-Path $PSScriptRoot 'minimax-ecosystem.json'

# Resolve Python, then PROVE the resolution works.
#
# `Get-Command python` is not enough. On this machine it returns
#   C:\Users\apviz\AppData\Local\Microsoft\WindowsApps\python.exe
# which is the Microsoft Store STUB. The file exists, the path is non-null, and
# invoking it does nothing at all - it is not an interpreter. So `$PY` was
# truthy and useless.
#
# The failure was silent and long-lived: the refresh worker called the
# ecosystem collector every 4th cycle with that stub, the native command exited
# without doing anything and without raising, and the panel served a snapshot
# that aged past 27 minutes with no error anywhere. A non-null path is a claim
# about an interpreter, not evidence of one.
#
# So: try the candidates, and accept one only if it actually reports a Python
# version. Verified, not assumed. A path that cannot be verified is not used.
function Resolve-WorkingPython {
  $candidates = @(
    'C:\Users\apviz\AppData\Local\Python\pythoncore-3.14-64\python.exe'
  )
  $onPath = (Get-Command python -ErrorAction SilentlyContinue).Source
  if ($onPath) { $candidates += $onPath }

  foreach ($c in $candidates) {
    if (-not (Test-Path $c)) { continue }
    try {
      $v = & $c -c "import sys;print(sys.version.split()[0])" 2>$null
      if ($LASTEXITCODE -eq 0 -and $v -match '^\d+\.\d+') { return $c }
    } catch { continue }
  }
  return $null
}

$PY = Resolve-WorkingPython
if (-not $PY) { throw 'no working Python interpreter found (tried the known path and PATH)' }

if (-not (Test-Path $INDEX)) { throw "index.html not found at $INDEX" }

# The action id comes from the request. The command comes from THIS table and
# nowhere else. That single indirection is what makes the endpoint safe.
#
# Read-only actions are marked. The workflow verbs were WRONG here: `wf_state`
# invoked the module with no arguments, and the module's default entry point was
# the state-changing DEMO, so pressing a button labelled "Workflow status"
# overwrote the live workflow with a fiction. bimodal_workflow.py now defaults to
# a read-only `status` verb and the demo requires an explicit `demo`.
$ACTIONS = @{
  # --- read-only ---
  'wf_state'       = { & $PY (Join-Path $WORKSPACE '08_SELF_IMPROVEMENT\bimodal_workflow.py') status 2>&1 }
  'wf_stop_report' = { & $PY (Join-Path $WORKSPACE '08_SELF_IMPROVEMENT\bimodal_workflow.py') stop-report 2>&1 }
  # --- state-changing, gated on the operator's own words arriving as $arg ---
  'wf_stop_ack'    = {
    param($arg)
    if (-not $arg -or -not $arg.Trim()) {
      'REFUSED: acknowledging a STOP requires the operator input that authorised resuming.' + "`n" +
      'An empty acknowledgement is not an acknowledgement. Resupply it as: {"id":"wf_stop_ack","arg":"<the operator answer>"}'
      return
    }
    & $PY (Join-Path $WORKSPACE '08_SELF_IMPROVEMENT\bimodal_workflow.py') ack-stop $arg 2>&1
  }
  'tests_run'     = { & $PY (Join-Path $WORKSPACE '08_SELF_IMPROVEMENT\test_suite.py') 2>&1 }
  'corpus_verify' = { & $PY (Join-Path $WORKSPACE '08_SELF_IMPROVEMENT\corpus_extractor.py') verify 2>&1 }
  'corpus_digest' = { & $PY (Join-Path $WORKSPACE '08_SELF_IMPROVEMENT\corpus_extractor.py') digest 220 2>&1 }
  'matrix_dump'   = { & $PY -c "import json,io,os;p=os.path.join(r'$WORKSPACE','12_PROGRAM','IDEA_TO_SCRIPT_MATRIX.json');print(json.dumps(json.load(io.open(p,encoding='utf-8')),indent=2,ensure_ascii=False) if os.path.exists(p) else 'matrix not generated yet')" 2>&1 }
  'skills_list'   = { Get-ChildItem (Join-Path $WORKSPACE '07_BACKBONE\skills') -Filter *.md -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Name 2>&1 }
  'mcp_wiring'    = { & $PY (Join-Path $WORKSPACE '13_COMMAND_CENTER\api\mcp_handshake.py') 2>&1 }
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

function Invoke-Action($id, $arg) {
  if (-not $ACTIONS.ContainsKey($id)) { return $null }
  $out = & $ACTIONS[$id] $arg 2>&1 | Out-String
  if ($out.Length -gt $MAX_OUTPUT) {
    $out = $out.Substring(0, $MAX_OUTPUT) + "`n...[output capped at $MAX_OUTPUT chars]"
  }
  return $out
}

function Search-Corpus($query, $limit) {
  # NOTE: the here-string variable must NOT be named $py. The interpreter path
  # is $PY, PowerShell folds $py and $PY into one variable, and assigning the
  # source text overwrote the interpreter - so `& $PY $tmp ...` tried to run the
  # Python source as a PowerShell command and corpus search died on every call.
  # Found live, in the server log, during verification. Guarded by
  # ps_shadowed_script_vars in monitor.py.
  $pySource = @"
import io, json, os, sys
# The corpus contains Romanian on purpose - the language law requires the
# wisdom text to survive verbatim. Printing an excerpt containing U+0219 to a
# cp1252 stdout raises UnicodeEncodeError, so a search that happened to return
# Romanian text failed while an ASCII one succeeded. This made the failure
# QUERY-DEPENDENT, which is the worst kind: verification searched "design" and
# passed. Force UTF-8 on stdout before anything is printed.
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass
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
  Set-Content -Path $tmp -Value $pySource -Encoding UTF8
  try { return (& $PY $tmp $query $limit 2>&1 | Out-String) }
  finally { Remove-Item $tmp -ErrorAction SilentlyContinue }
}

# ---- background refresh worker -------------------------------------------
# The collector measures and writes. Requests only ever READ the file, so a
# poll costs ~0.01s regardless of how slow the measurement is.
#
# There is deliberately NO local `function Start-RefreshWorker` here any more.
# One existed, and it was DEAD CODE - defined, complete, correct, and never
# called once. The ecosystem refresh was written into it, and the Ecosystem
# panel therefore served a snapshot that aged to 27 minutes and never moved
# again, silently, with no error in any log.
#
# A function that is defined but never called is not a code path. It is
# invisible to the parser, to the linter and to every reader, and it reads
# exactly like a working one. The real worker is the Start-Job further down.
# If you add refresh work, add it THERE.
$ECO_SCRIPT = Join-Path $WORKSPACE '08_SELF_IMPROVEMENT\collect_minimax_ecosystem.py'

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

# The ecosystem snapshot is collected HERE too, before the listener opens, and
# this is a real fix rather than a nicety.
#
# The background worker below refreshes the ecosystem on every 4th cycle, which
# is right for a steady state - but it means a freshly started server has NO
# snapshot of its own for roughly the first four refresh intervals (~100 s).
# During that window /api/minimax serves the PREVIOUS instance's file, and the
# panel shows another process's measurements with a timestamp that says so.
#
# Measured: a cold start followed by the deployment suite reported the snapshot
# as 1163 s old while the server serving it was 110 s old. Nothing was broken;
# the panel was simply showing a dead instance's data, correctly timestamped,
# which is the least useful possible state - it looks like a live hub and is not.
#
# So the first pass is unconditional and the 4-cycle cadence is the steady-state
# refresh. A panel that is going to be looked at within two minutes of logon
# must be measuring the instance that is answering it.
try {
  & $PY $ECO_SCRIPT | Out-Null
  if ($LASTEXITCODE -ne 0) {
    Write-Host "  (ecosystem collection exited $LASTEXITCODE - the panel will show NOT_AVAILABLE)" -ForegroundColor Red
  }
} catch {
  Write-Host "  (ecosystem collection failed: $($_.Exception.Message))" -ForegroundColor Red
}

Write-Host "state ready. refresh every $RefreshSeconds s." -ForegroundColor Green
Write-Host ''

# Start the worker as a background job so the listener loop is not blocked.
#
# A Start-Job has its OWN session state. $PY, $WORKSPACE, $RefreshSeconds and
# every other variable in this script are NOT visible inside it unless they are
# passed through -ArgumentList. That is not a detail: an earlier version of this
# block referenced a script-scoped variable from inside the job, where it was
# silently $null, and the call it guarded appeared to work because it was
# wrapped in a try/catch that could not fail. Everything the job needs goes in
# the parameter list, and the job verifies what it was given before using it.
$worker = Start-Job -ArgumentList $API, $RefreshSeconds, $PY, $ECO_SCRIPT, (Join-Path (Join-Path $WORKSPACE '09_LOGS') 'refresh-worker.log') -ScriptBlock {
  param($apiPath, $seconds, $pyExe, $ecoScript, $logPath)

  # A job's own output stream is readable only by whoever calls Receive-Job, and
  # nobody does. Anything written there is as invisible as not writing it at all:
  # a collector that breaks every cycle would look exactly like a healthy one.
  # So the worker's status goes to a FILE, where a failing refresh can be
  # explained instead of merely detected. Staleness is the detector; this is
  # the diagnosis.
  $say = {
    param($msg)
    $line = "[{0}] {1}" -f (Get-Date).ToString('s'), $msg
    try { Add-Content -Path $logPath -Value $line -Encoding UTF8 -ErrorAction Stop } catch { }
  }

  # Non-terminating by design: a failed collection must not kill the worker,
  # or one bad cycle would stop every future refresh for the life of the server.
  $ErrorActionPreference = 'Continue'

  & $say "refresh worker started: every ${seconds}s, ecosystem every 4th cycle"

  # The ecosystem snapshot refreshes every 4th cycle, not every cycle. Not
  # because it is expensive - it is a directory-stat pass - but because
  # refreshing it every 25 s would make its displayed age meaningless. An agent
  # roster and an MCP config do not change 96 times an hour, and a panel
  # claiming to be 3 seconds old when the fact is stable is reporting the
  # collector's heartbeat, not the ecosystem's state.
  $cycles = 0
  $ecoBroken = $false

  while ($true) {
    & powershell -NoProfile -ExecutionPolicy Bypass -File $apiPath -Quiet | Out-Null

    $cycles++
    if ($cycles -ge 4) {
      $cycles = 0
      if (-not $pyExe -or -not (Test-Path $ecoScript)) {
        if (-not $ecoBroken) {
          & $say "NOT RUNNING: pyExe='$pyExe' script='$ecoScript'"
          $ecoBroken = $true
        }
      } else {
        & $pyExe $ecoScript | Out-Null
        if ($LASTEXITCODE -ne 0) {
          # A native command exiting non-zero does NOT throw in PowerShell 5.1.
          # Without this the whole failure is invisible - which is exactly how
          # a Microsoft Store python stub can run for hours doing nothing.
          if (-not $ecoBroken) {
            & $say "collector exited $LASTEXITCODE"
            $ecoBroken = $true
          }
        } elseif ($ecoBroken) {
          & $say 'collector recovered'
          $ecoBroken = $false
        }
      }
    }
    Start-Sleep -Seconds $seconds
  }
}

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
        $arg = ''
        try {
          $parsed = $body | ConvertFrom-Json
          $id = $parsed.id
          if ($parsed.PSObject.Properties.Name -contains 'arg') { $arg = [string]$parsed.arg }
        } catch { }
        if ([string]::IsNullOrWhiteSpace($id)) {
          Send-Response $ctx 400 'application/json' '{"error":"no action id supplied"}' $null
          continue
        }
        $out = Invoke-Action $id $arg
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
        '/api/verify' {
          # The last 3-cycle lifecycle verification. NOT_RUN when the verifier
          # has never run - which is a fact about the system, not a failure of
          # this route, so it is reported as such rather than as an empty 200
          # that a reader has to interpret.
          if (Test-Path $VERIFY) {
            $json = Get-Content $VERIFY -Raw -Encoding UTF8
          } else {
            $json = '{"verdict":"NOT_RUN","note":"verify-server.ps1 has not been run on this machine"}'
          }
          Send-Response $ctx 200 'application/json; charset=utf-8' $json `
            @{ 'Cache-Control' = 'no-store' }
        }
        '/api/history' {
          # Content-Type corrected (2026-10-09): this route returns JSONL -
          # newline-delimited objects - but declared itself application/json.
          # A correct client that trusted the label and called r.json() would
          # throw on the first newline, which is a contract defect rather than
          # a client bug: the label was a lie about the payload. The payload
          # shape is unchanged on purpose - only the label became true, so no
          # existing consumer had to be rewritten to accommodate a fix.
          if (Test-Path $HISTORY) {
            $lines = Get-Content $HISTORY -Tail 120 -Encoding UTF8
            Send-Response $ctx 200 'application/x-ndjson; charset=utf-8' ($lines -join "`n") `
              @{ 'Cache-Control' = 'no-store' }
          } else {
            Send-Response $ctx 200 'application/x-ndjson; charset=utf-8' '' $null
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
        '/api/minimax' {
          # The local MINIMAX ecosystem snapshot, written by
          # 08_SELF_IMPROVEMENT\collect_minimax_ecosystem.py, which reads the
          # runtime's own files. Served as a separate route rather than folded
          # into /api/state because it is a DIFFERENT cadence and a different
          # producer: the state file is rewritten every refresh by the
          # PowerShell collector, this one is written by a Python collector on
          # its own schedule. Merging them would make one stale producer
          # silently date-stamp the other.
          #
          # A missing file answers with an explicit NOT_AVAILABLE document, not
          # an empty object. An empty object renders as a panel of nothing,
          # which reads as "the ecosystem is empty" rather than "nothing was
          # measured" - and those are very different facts.
          if (Test-Path $MINIMAX) {
            Send-Response $ctx 200 'application/json; charset=utf-8' `
              (Get-Content $MINIMAX -Raw -Encoding UTF8) `
              @{ 'Cache-Control' = 'no-store' }
          } else {
            $miss = @{
              generated_at = (Get-Date).ToString('s')
              status       = 'NOT_AVAILABLE'
              reason       = 'collect_minimax_ecosystem.py has not written a snapshot yet'
              counts       = @{ measured = 0; not_available = 0; error = 0; total = 0 }
              surfaces     = @()
            } | ConvertTo-Json -Depth 6
            Send-Response $ctx 200 'application/json; charset=utf-8' $miss `
              @{ 'Cache-Control' = 'no-store' }
          }
        }
        '/api/stream' {
          # Server-Sent Events, SHORT-LIVED BY DESIGN.
          #
          # The obvious implementation - hold the response open and push on every
          # refresh - cannot work on this server. The listener loop is
          # single-threaded and this handler would run INSIDE it, so one connected
          # browser would block every other route, including the /api/state call
          # that same page needs. The dashboard would connect, then hang itself.
          #
          # Instead: send the current state, flush, close. The browser's native
          # EventSource reconnects automatically on close, so the UI still updates
          # without the listener ever being blocked.
          #
          # The `retry:` line is load-bearing, and it was missing. EventSource's
          # built-in reconnect delay is about 3 s in Chromium, so a browser with
          # the dashboard open reconnected every three seconds and re-read the
          # whole state file each time - measured at 21 deliveries in 62 s. The
          # claim "the UI updates at the collector's cadence" was false by a
          # factor of ~8, and it was false in the expensive direction: 76 KB
          # re-read roughly eight times per collector cycle to obtain bytes that
          # cannot have changed. The data is at most RefreshSeconds old, so a
          # shorter reconnect interval buys nothing and costs the most expensive
          # thing there is to waste, which is another reader's time.
          #
          # `retry:` is the SSE spec's own field for this. Emitting it makes the
          # documented claim true instead of aspirational.
          $retryMs = [int]($RefreshSeconds * 1000)
          $stream = $null
          try {
            $ctx.Response.StatusCode = 200
            $ctx.Response.ContentType = 'text/event-stream; charset=utf-8'
            $ctx.Response.Headers.Add('Cache-Control', 'no-store')
            $ctx.Response.SendChunked = $true
            # SendChunked is required: without it HttpListener buffers the
            # response and the client receives nothing. That was the original
            # bug - an empty catch block swallowed it, so /api/stream answered
            # 0 bytes forever and looked like a dead server rather than a dead
            # stream.
            $stream = $ctx.Response.OutputStream
            if (Test-Path $STATE) {
              $payload = Get-Content $STATE -Raw -Encoding UTF8
              $chunk = "retry: $retryMs`nevent: state`ndata: $payload`n`n"
            } else {
              $chunk = "retry: $retryMs`nevent: state`ndata: {`"generated`":null,`"note`":`"no state collected yet`"}`n`n"
            }
            $b = [Text.Encoding]::UTF8.GetBytes($chunk)
            $stream.Write($b, 0, $b.Length)
            $stream.Flush()
          } catch {
            # Named, never empty. An empty catch here is what hid the real
            # failure for the whole first build.
            Write-Host "  (stream aborted: $($_.Exception.Message))" -ForegroundColor DarkGray
          } finally {
            try { if ($stream) { $stream.Close() } } catch { }
          }
        }
        default {
          Send-Response $ctx 404 'text/plain' 'not found' $null
        }
      }
    } catch {
      # An exception here used to print a message and fall through WITHOUT
      # sending a response, so the client hung until its own timeout instead of
      # getting an error. A handler that fails must still answer.
      Write-Host "  (request error: $($_.Exception.Message))" -ForegroundColor Red
      Send-Response $ctx 500 'application/json; charset=utf-8' `
        '{"error":"the request could not be served; see the server log"}' `
        @{ 'Cache-Control' = 'no-store' }
    }
  }
}
finally {
  Write-Host ''
  Write-Host 'stopping...' -ForegroundColor DarkGray
  try { Stop-Job $worker -ErrorAction SilentlyContinue; Remove-Job $worker -Force -ErrorAction SilentlyContinue } catch { }
  try { $listener.Stop(); $listener.Close() } catch { }
}
