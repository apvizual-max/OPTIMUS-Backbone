<#
.SYNOPSIS
  Proves the SENTINEL Command Center actually works, rather than being assumed to.

.DESCRIPTION
  The reference Command Center this was copied from was DOWN when this was built
  (connection refused on 8900). "It starts" is therefore a claim that has to be
  measured, on this machine, repeatedly - not inherited from a design document.

  This script does the full lifecycle N times and records the evidence:

    0. stop   the deployment through the orchestrator and prove BOTH planes
              are actually down, so every cycle starts from a known state
    1. start  the deployment through the orchestrator
    2. planes prove the front is the CONTAINER (by deployment header, not by
              status code) and that the backend answers on its own port
    3. probe  every route over real HTTP through the front, and assert on the
              CONTENT, not only on the status code
    4. refuse POST injected action ids and require a 400 that NAMES the payload
    5. gate   POST the STOP acknowledgement with no argument and require the
              refusal to come back as text
    6. stop   the deployment again and prove the teardown took effect

  A route that answers 200 with an empty body counts as a failure here, because
  that is exactly the shape of a server that is up and serving nothing.

  It writes api\verify-report.json and serves it at /api/verify, which the
  Ecosystem panel reads, so the panel shows the last real run rather than a
  claim about one.

  Two things it reports but deliberately does NOT gate on:
    - the monitor's own verdict, printed as a [note] and carried in the report
      as monitor_overall. "Does the deployment serve the health report" and
      "is the system healthy" are different systems.
    - the verdict /api/verify serves mid-cycle, which is the PREVIOUS run by
      definition. Asserting PASS there would assert a stale file is fresh.

.TOPOLOGY - WHY THIS SCRIPT DRIVES AN ORCHESTRATOR
  The deployment has two planes and they are NOT interchangeable:

    FRONT    127.0.0.1:8910  the container. It owns the address Popy has
                             bookmarked, and it is the only surface shaped
                             like a public deployment.
    BACKEND  127.0.0.1:8912  a Windows PowerShell HttpListener. It owns every
                             measurement, because everything it measures is a
                             Windows fact.

  An earlier single-plane version of this script bound 8910 ITSELF. It collided
  with the container, killed the live backend in its pre-clean, and then
  measured sixteen 502s coming out of an nginx it did not own. Every one of
  those FAILs pointed at the product. None of them were about the product.

  So this script never starts a server of its own. It calls
  sentinel-hub.ps1, which owns both planes, and judges the result end to end
  through the front - the same path Popy's browser takes.

  It is called the lifecycle verifier for that reason: it proves the
  orchestrator's verbs actually work, which is the thing that has to survive a
  real logon.

.PARAMETER Port
  The FRONT port - the container's published loopback address. Default 8910.

.PARAMETER BackPort
  The BACKEND port - the Windows data plane. Default 8912.

.PARAMETER Cycles
  How many start/probe/stop cycles to prove. Default 3.

.PARAMETER SkipActions
  Skip the read-only whitelisted-action probes (route probes still run). Useful
  while iterating on the UI, because each action costs real time.

.EXAMPLE
  powershell -NoProfile -ExecutionPolicy Bypass -File verify-server.ps1
#>
[CmdletBinding()]
param(
  [int]$Port = 8910,
  [int]$BackPort = 8912,
  [int]$Cycles = 3,
  [switch]$SkipActions
)

$ErrorActionPreference = 'Stop'
$API_DIR = $PSScriptRoot
$ROOT = Split-Path -Parent $API_DIR
$WORKSPACE = Split-Path -Parent $ROOT
$ORCHESTRATOR = Join-Path $API_DIR 'sentinel-hub.ps1'
$CONTAINER = 'mavis-sentinel-hub'
$DEPLOYMENT_HEADER = 'X-SENTINEL-Deployment'
$REPORT_PATH = Join-Path $API_DIR 'verify-report.json'
# Ports that belong to OTHER systems on this machine and are never this
# deployment's business. 8900/8901 are the OPTIMUS Control Center
# (projects\90_CONTROL_CENTER), which is read-only for us.
$RESERVED_PORTS = @(8900, 8901)

$results = New-Object System.Collections.ArrayList
$script:failures = 0
$script:notRun = 0
$script:monitorOverall = 'NOT_RUN'

function Add-Result($cycle, $name, $pass, $detail) {
  $script:results.Add([pscustomobject]@{
    cycle = $cycle; name = $name; pass = [bool]$pass; detail = [string]$detail
  }) | Out-Null
  if (-not $pass) { $script:failures++ }
  $tag = if ($pass) { 'PASS' } else { 'FAIL' }
  $col = if ($pass) { 'Green' } else { 'Red' }
  Write-Host ("  [{0}] c{1} {2,-36} {3}" -f $tag, $cycle, $name, $detail) -ForegroundColor $col
}

function Add-NotRun($cycle, $name, $why) {
  # NOT_RUN is a distinct outcome from FAIL and from OK. A check that could not
  # execute did not pass, and it did not fail either - reporting it as either
  # is a lie in one of two directions.
  $script:results.Add([pscustomobject]@{
    cycle = $cycle; name = $name; pass = $null; detail = [string]$why
  }) | Out-Null
  $script:notRun++
  Write-Host ("  [----] c{1} {2,-36} {3}" -f $cycle, $name, $why) -ForegroundColor Yellow
}

function Test-Port([int]$OnPort) {
  $c = New-Object Net.Sockets.TcpClient
  try {
    $iar = $c.BeginConnect('127.0.0.1', $OnPort, $null, $null)
    $ok = $iar.AsyncWaitHandle.WaitOne(1200, $false)
    if ($ok) { try { $c.EndConnect($iar) } catch { } }
    return $ok
  } catch { return $false }
  finally { try { $c.Close() } catch { } }
}

function Test-HttpOk([string]$Url, [int]$Timeout = 10) {
  try {
    $r = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec $Timeout
    return ($r.StatusCode -eq 200)
  } catch { return $false }
}

function Wait-UrlOk([string]$Url, [int]$TimeoutSec = 60) {
  $deadline = (Get-Date).AddSeconds($TimeoutSec)
  while ((Get-Date) -lt $deadline) {
    if (Test-HttpOk -Url $Url -Timeout 6) { return $true }
    Start-Sleep -Milliseconds 500
  }
  return $false
}

function Wait-UrlDead([string]$Url, [int]$TimeoutSec = 45) {
  $deadline = (Get-Date).AddSeconds($TimeoutSec)
  while ((Get-Date) -lt $deadline) {
    if (-not (Test-HttpOk -Url $Url -Timeout 4)) { return $true }
    Start-Sleep -Milliseconds 500
  }
  return $false
}

function Invoke-Orchestrator([string]$Action) {
  # The orchestrator is the ONLY thing allowed to start or stop a plane. Calling
  # it, instead of spawning a private server, is what keeps this verifier from
  # fighting the deployment it is supposed to be checking.
  #
  # Note on the captured output: sentinel-hub.ps1 reports with Write-Host, and
  # in Windows PowerShell 5.1 Write-Host writes to the HOST, not to the output
  # stream, so `2>&1` does not capture its report lines. The exit code is the
  # reliable signal, and every fact this script reports is measured here
  # directly rather than parsed out of the orchestrator's prose. That is why
  # the plane checks below exist instead of being skipped.
  try {
    & $ORCHESTRATOR -Action $Action -FrontPort $Port -BackPort $BackPort 2>&1 | Out-Null
    $rc = $LASTEXITCODE
    if ($null -eq $rc) { $rc = 0 }
    return @{ rc = [int]$rc }
  } catch {
    return @{ rc = 1; error = $_.Exception.Message }
  }
}

function Get-ServerOnPort {
  # Every PowerShell process running a `server.ps1`, with the port it was told
  # to use, and what this function can say about its identity.
  #
  # Identification is by COMMAND LINE, never by the listening socket: a
  # PowerShell HttpListener is hosted in http.sys, so Get-NetTCPConnection
  # reports OwningProcess = 4 (System) for 8912 no matter which PowerShell
  # opened it. "Kill the owner of the socket" would target the kernel, leave
  # the real server running, and make every later cycle test a stale process.
  #
  # WHY THIS SCANS EVERYTHING, AND SAYS WHAT IT CANNOT PROVE
  # The first version required SENTINEL_PRIME in the command line. That removed
  # four false failures - it was blaming the OPTIMUS Control Center on 8900, a
  # different system - but it also introduced a blind spot the verifier
  # demonstrated by simulation: a server launched with a RELATIVE path
  # (`-File 13_COMMAND_CENTER\api\server.ps1`, which is how the verifier itself
  # invoked this suite), a copy at another path, or one started through
  # `sentinel-cc.ps1` would carry no SENTINEL_PRIME token and be invisible.
  #
  # So the scan is wide, and identity is carried as a FACT ABOUT THE EVIDENCE
  # rather than as a silent filter: `PathMatch` is reported, and callers
  # classify by port. A process that cannot be attributed is returned and named,
  # never dropped - a check that reports PASS because its filter found nothing
  # is reporting its own method, not the system's state.
  param([switch]$IncludeForeign)
  $found = @()
  try {
    $all = @(Get-CimInstance Win32_Process -Filter "Name='powershell.exe'" -ErrorAction SilentlyContinue |
      Where-Object { $_.CommandLine -like '*server.ps1*' -and $_.ProcessId -ne $PID })
    foreach ($proc in $all) {
      # $procPort, NOT $port. PowerShell variable names are case-insensitive, so
      # a local `$port` here is the SAME VARIABLE as this script's $Port (8910) -
      # assigning it silently rewrote the front port for the rest of the run.
      # Every `IsFront` test then compared 8900 against itself and returned
      # true, so the OPTIMUS Control Center on 8900 was reported as squatting
      # the front port. Four FAILs, all of them this one shadowed variable, and
      # all of them reintroducing the exact false positive the previous round
      # removed.
      $procPort = 0
      if ($proc.CommandLine -match '-Port\s+(\d+)') { $procPort = [int]$Matches[1] }
      $found += [pscustomobject]@{
        ProcessId  = $proc.ProcessId
        Port       = $procPort
        PathMatch  = ($proc.CommandLine -like '*SENTINEL_PRIME*')
        OnReserved = ($RESERVED_PORTS -contains $procPort)
        IsFront    = ($procPort -eq $Port)
        IsBack     = ($procPort -eq $BackPort)
      }
    }
  } catch { }
  return @($found)
}

function Get-FrontHealth {
  # Status and deployment header in one call, because they are one question:
  # "is the thing answering on the front port the container, or a stray?"
  # A 200 alone cannot tell those apart - that is the whole point of the
  # anti-hijack gate.
  try {
    $r = Invoke-WebRequest -Uri "http://127.0.0.1:$Port/healthz" -UseBasicParsing -TimeoutSec 8
    return [pscustomobject]@{
      status = [int]$r.StatusCode
      header = [string]$r.Headers[$DEPLOYMENT_HEADER]
      err = ''
    }
  } catch {
    $code = 0
    try { $code = [int]$_.Exception.Response.StatusCode } catch { $code = 0 }
    return [pscustomobject]@{ status = $code; header = ''; err = $_.Exception.Message }
  }
}

function Invoke-Api([string]$Path, [string]$Method = 'GET', $Body = $null, [int]$OnPort = 0) {
  $usePort = $OnPort
  if ($usePort -le 0) { $usePort = $Port }
  $uri = "http://127.0.0.1:$usePort$Path"
  try {
    if ($null -ne $Body) {
      $r = Invoke-WebRequest -Uri $uri -Method $Method -Body $Body `
        -ContentType 'application/json' -UseBasicParsing -TimeoutSec 90
    } else {
      $r = Invoke-WebRequest -Uri $uri -Method $Method -UseBasicParsing -TimeoutSec 90
    }
    return [pscustomobject]@{ status = [int]$r.StatusCode; body = [string]$r.Content; err = '' }
  } catch {
    $code = 0; $text = ''
    try {
      $resp = $_.Exception.Response
      $code = [int]$resp.StatusCode
      $sr = New-Object IO.StreamReader($resp.GetResponseStream())
      $text = $sr.ReadToEnd(); $sr.Close()
    } catch { $text = $_.Exception.Message }
    return [pscustomobject]@{ status = $code; body = $text; err = $_.Exception.Message }
  }
}

function Read-Http([string]$Method, [string]$Path, [string]$Body = '', [int]$OnPort = 0, [int]$Ms = 20000) {
  # Raw socket, because Invoke-WebRequest THROWS on 400 and its exception object
  # does not reliably expose the response body. The first version of this check
  # therefore reported "http=400 body=" and could not tell a correct refusal
  # from a bare one. The body is the evidence that the server NAMED what it
  # refused, so it has to be read.
  $usePort = $OnPort
  if ($usePort -le 0) { $usePort = $Port }
  $c = New-Object Net.Sockets.TcpClient
  try {
    $c.ReceiveTimeout = $Ms
    $c.Connect('127.0.0.1', $usePort)
    $st = $c.GetStream()
    $req = "$Method $Path HTTP/1.1`r`nHost: 127.0.0.1:$usePort`r`nAccept: */*`r`n"
    if ($Body) { $req += "Content-Type: application/json`r`nContent-Length: $($Body.Length)`r`n" }
    $req += "Connection: close`r`n`r`n$Body"
    $rb = [Text.Encoding]::UTF8.GetBytes($req)
    $st.Write($rb, 0, $rb.Length)
    $st.Flush()
    $buf = New-Object byte[] 65536
    $sb = New-Object Text.StringBuilder
    while ($true) {
      try { $n = $st.Read($buf, 0, $buf.Length) } catch { break }
      if ($n -le 0) { break }
      [void]$sb.Append([Text.Encoding]::UTF8.GetString($buf, 0, $n))
      if ($sb.ToString() -match '\r\n\r\n' -and $sb.ToString().Length -gt 4000) { break }
    }
    $raw = $sb.ToString()
    $status = 0
    if ($raw -match '^HTTP/1\.\d\s+(\d{3})') { $status = [int]$Matches[1] }
    $payload = ''
    $idx = $raw.IndexOf("`r`n`r`n")
    if ($idx -ge 0) { $payload = $raw.Substring($idx + 4) }
    if ($payload -match '^[0-9a-fA-F]+\r\n') { $payload = ($payload -split "\r\n", 2)[1] }
    return [pscustomobject]@{ status = $status; body = $payload; err = '' }
  } catch {
    return [pscustomobject]@{ status = 0; body = ''; err = $_.Exception.Message }
  } finally {
    try { $c.Close() } catch { }
  }
}

function Read-Sse([int]$OnPort, [int]$MaxMs = 25000) {
  # SSE cannot be read with Invoke-WebRequest: the response never ends, so the
  # call blocks forever. A raw socket with a read deadline is the only honest
  # way to prove the stream actually emits data.
  $client = New-Object Net.Sockets.TcpClient
  try {
    $client.ReceiveTimeout = 8000
    $client.Connect('127.0.0.1', $OnPort)
    $stream = $client.GetStream()
    $req = "GET /api/stream HTTP/1.1`r`nHost: 127.0.0.1:$OnPort`r`nAccept: text/event-stream`r`n`r`n"
    $b = [Text.Encoding]::ASCII.GetBytes($req)
    $stream.Write($b, 0, $b.Length)
    $stream.Flush()
    $buf = New-Object byte[] 65536
    $sb = New-Object Text.StringBuilder
    $sw = [Diagnostics.Stopwatch]::StartNew()
    while ($sw.ElapsedMilliseconds -lt $MaxMs) {
      try { $n = $stream.Read($buf, 0, $buf.Length) } catch { break }
      if ($n -le 0) { break }
      [void]$sb.Append([Text.Encoding]::UTF8.GetString($buf, 0, $n))
      if ($sb.ToString() -match 'event:\s*state') { break }
    }
    return $sb.ToString()
  } catch {
    return "SSE-ERROR: $($_.Exception.Message)"
  } finally {
    try { $client.Close() } catch { }
  }
}

# --------------------------------------------------------------------------
Write-Host ''
Write-Host 'SENTINEL COMMAND CENTER - DUAL-PLANE LIFECYCLE VERIFICATION' -ForegroundColor Cyan
Write-Host "  front=$Port (container $CONTAINER)   backend=$BackPort (PowerShell)   cycles=$Cycles" -ForegroundColor DarkGray
Write-Host ''

# ---- 0. known state ------------------------------------------------------
# A lifecycle test that starts from an unknown state cannot prove a teardown,
# because it never establishes that anything was up. So the deployment is put
# down FIRST, through the same verb the startup path uses, and both planes are
# confirmed down before cycle 1.
Write-Host 'pre-clean: stopping the deployment through the orchestrator...' -ForegroundColor DarkGray
$pre = Invoke-Orchestrator 'stop'
$preBackDead = Wait-UrlDead "http://127.0.0.1:$BackPort/api/health" -TimeoutSec 45
$preFrontDead = Wait-UrlDead "http://127.0.0.1:$Port/healthz" -TimeoutSec 45
$prePortFree = -not (Test-Port $BackPort)

if ($preBackDead -and $preFrontDead -and $prePortFree) {
  Add-Result 0 'pre-clean: both planes down' $true "backend $BackPort closed, front $Port not answering"
} else {
  Add-Result 0 'pre-clean: both planes down' $false `
    "backendClosed=$preBackDead frontDead=$preFrontDead portFree=$prePortFree"
}

$strays = @(Get-ServerOnPort)
$onFront  = @($strays | Where-Object { $_.IsFront })
$onBack   = @($strays | Where-Object { $_.IsBack })
$reserved = @($strays | Where-Object { $_.OnReserved })
$unknown  = @($strays | Where-Object { -not $_.IsFront -and -not $_.IsBack -and -not $_.OnReserved })

if ($onFront.Count -gt 0) {
  Add-Result 0 'pre-clean: no stray on the front port' $false `
    "pid(s) $($onFront.ProcessId -join ', ') bound the FRONT port $Port - that address belongs to the container"
} elseif ($onBack.Count -gt 0) {
  Add-Result 0 'pre-clean: no stray on the front port' $false `
    "pid(s) $($onBack.ProcessId -join ', ') still on $BackPort after stop - the teardown did not take effect"
} else {
  Add-Result 0 'pre-clean: no stray on the front port' $true `
    "no process is bound to $Port or $BackPort after stop"
}

# Processes we cannot attribute are reported, not dropped. A previous version
# filtered on SENTINEL_PRIME in the command line and treated "my filter found
# nothing" as proof that nothing was there; a relative-path launch, a copy, or
# anything started via sentinel-cc.ps1 all evade that filter, so the check was
# reporting its own method. These are named so the limit of the evidence is
# visible instead of implied.
if ($unknown.Count -eq 0) {
  Add-Result 0 'pre-clean: unattributed servers' $true 'every server.ps1 on the box is accounted for'
} else {
  $u = (($unknown | ForEach-Object { "pid $($_.ProcessId) on port $($_.Port)" }) -join ', ')
  Add-Result 0 'pre-clean: unattributed servers' $false `
    "found but cannot be attributed: $u - not on the front or back port, and not a reserved port. " +
    "Not this deployment's to stop, but this script cannot prove whose they are."
}

# The neighbours, named and left alone. The correct action toward someone
# else's service is no action.
if ($reserved.Count -eq 0) {
  Add-Result 0 'pre-clean: foreign services untouched' $true 'no process on a reserved port'
} else {
  $fdesc = (($reserved | ForEach-Object { "pid $($_.ProcessId) on $($_.Port)" }) -join ', ')
  Add-Result 0 'pre-clean: foreign services untouched' $true `
    "$fdesc - not ours, deliberately not stopped"
}

for ($cycle = 1; $cycle -le $Cycles; $cycle++) {
  Write-Host ''
  Write-Host "--- cycle $cycle ---" -ForegroundColor Cyan

  # ---- 1. start --------------------------------------------------------
  $t0 = Get-Date
  $started = Invoke-Orchestrator 'start'
  $startSecs = [math]::Round(((Get-Date) - $t0).TotalSeconds, 1)
  if ($started.rc -ne 0) {
    Add-Result $cycle 'start: orchestrator start' $false "exit=$($started.rc) after ${startSecs}s"
    $err = if ($started.error) { $started.error } else { 'see the orchestrator output above' }
    Write-Host "  $err" -ForegroundColor DarkRed
    continue
  }
  Add-Result $cycle 'start: orchestrator start' $true "exit=0 in ${startSecs}s"

  # ---- 2. the two planes, measured independently ------------------------
  # Measured rather than trusted: the orchestrator's own "DEPLOYMENT UP" is a
  # claim about itself. These are the two questions the dashboard's liveness
  # banner actually displays, asked straight.
  $fh = Get-FrontHealth
  $frontIsContainer = ($fh.status -eq 200) -and ($fh.header -eq $CONTAINER)
  Add-Result $cycle 'front: is the container' $frontIsContainer `
    "healthz=$($fh.status) header=$($fh.header)"

  $r = Invoke-Api '/api/health' 'GET' $null $BackPort
  $backOk = ($r.status -eq 200) -and ($r.body.Trim().Length -gt 0)
  Add-Result $cycle 'backend: answers on its own port' $backOk `
    "http=$($r.status) bytes=$($r.body.Trim().Length)"

  $readyOk = Wait-UrlOk "http://127.0.0.1:$Port/readyz" -TimeoutSec 20
  Add-Result $cycle 'readyz: front reaches the backend' $readyOk `
    $(if ($readyOk) { 'both planes agreeing through the gateway' } else { 'FRONT UP, BACKEND NOT ANSWERING' })

  # ---- 3. routes, through the front -------------------------------------
  $r = Invoke-Api '/'
  $isHtml = ($r.status -eq 200) -and ($r.body -match '(?i)<html|<!doctype html') -and ($r.body.Length -gt 5000)
  Add-Result $cycle 'GET /' $isHtml "http=$($r.status) bytes=$($r.body.Length) html=$isHtml"

  $r = Invoke-Api '/api/state'
  $gen = ''
  $mode = ''
  $keys = @()
  $hok = $false
  if ($r.status -eq 200) {
    try {
      $j = $r.body | ConvertFrom-Json
      $gen = [string]$j.generated
      $keys = @($j.PSObject.Properties.Name)
      # The mode lives under `workflow`, not at the top level. Asserting on a
      # field that does not exist is how a probe reports "" and looks broken
      # while the data is fine - the mirror image of the collector bug.
      $mode = [string]$j.workflow.mode
      $hok = ($gen -ne '') -and ($mode -ne '') -and
             (@('corpus', 'workflow', 'program', 'tests', 'gaps', 'learning') |
              Where-Object { $keys -notcontains $_ }).Count -eq 0
    } catch { $hok = $false }
  }
  Add-Result $cycle 'GET /api/state' ($r.status -eq 200 -and $hok) `
    "http=$($r.status) generated=$gen mode=$mode keys=$($keys.Count)"

  # This asserts the ROUTE serves a real report - which is the lifecycle
  # question, and the only one this script owns. It deliberately does NOT gate
  # on the monitor's own verdict, because "does the deployment serve the health
  # report" and "is the system healthy" are different systems.
  #
  # It is named "serves report" rather than "/api/health" on purpose. The first
  # run printed a green PASS directly beside "overall=FAIL checks=55", which is
  # how a reader learns to stop believing the tag. The verdict is surfaced on
  # its own line below, ungated, so it is visible and cannot be mistaken for
  # part of this check.
  $r = Invoke-Api '/api/health'
  $overall = ''
  $nchecks = 0
  $hok = $false
  if ($r.status -eq 200) {
    try {
      $j = $r.body | ConvertFrom-Json
      $overall = [string]$j.overall
      $nchecks = @($j.checks).Count
      $hok = ($nchecks -gt 0)
    } catch { }
  }
  Add-Result $cycle 'GET /api/health (serves report)' ($r.status -eq 200 -and $hok) `
    "http=$($r.status) checks=$nchecks"
  $script:monitorOverall = $overall
  Write-Host ("  [note] c{0} monitor verdict reported by that payload: {1} (not gated by this script)" -f $cycle, $overall) -ForegroundColor $(if ($overall -eq 'OK') { 'DarkGray' } else { 'Yellow' })

  $r = Invoke-Api '/api/history'
  $hok2 = ($r.status -eq 200) -and ($r.body.Trim().Length -gt 0)
  Add-Result $cycle 'GET /api/history' $hok2 "http=$($r.status) bytes=$($r.body.Trim().Length)"

  $r = Invoke-Api '/api/corpus?q=design&limit=5'
  $ccount = -1
  $cok = $false
  if ($r.status -eq 200) {
    try {
      $j = $r.body | ConvertFrom-Json
      $ccount = [int]$j.count
      $cok = ($j.PSObject.Properties.Name -contains 'hits')
    } catch { }
  }
  Add-Result $cycle 'GET /api/corpus (ascii query)' ($r.status -eq 200 -and $cok) "http=$($r.status) hits=$ccount"

  # The query-dependent case. The corpus carries Romanian ON PURPOSE, so any
  # search that returns a Romanian excerpt must still work: printing U+0219 to a
  # cp1252 stdout used to raise UnicodeEncodeError, and the request then hung
  # for 60 s. Searching only "design" (ASCII excerpts) hid it for the whole
  # build, so this case is asserted explicitly and every cycle.
  $sw2 = [Diagnostics.Stopwatch]::StartNew()
  $r = Invoke-Api '/api/corpus?q=sentinel&limit=3'
  $sw2.Stop()
  $ro = 0
  $rok = $false
  if ($r.status -eq 200) {
    try {
      $j = $r.body | ConvertFrom-Json
      $ro = [int]$j.count
      $rok = ($ro -ge 0) -and ($j.PSObject.Properties.Name -contains 'hits')
    } catch { }
  }
  Add-Result $cycle 'GET /api/corpus (Romanian-safe)' ($r.status -eq 200 -and $rok) `
    "http=$($r.status) hits=$ro in $($sw2.ElapsedMilliseconds)ms"

  # The ecosystem surface - the MINIMAX triad block. Asserted on the real
  # payload shape: `counts.error` is the field that says a collector surface
  # failed, and it must be zero. A dashboard full of surfaces where one threw
  # is still a working dashboard, so only the error count is a hard gate; the
  # surface count guards against the route silently returning a stub.
  $r = Invoke-Api '/api/minimax'
  $nsurf = 0; $nmeas = 0; $nerr = 0; $nna = 0
  $eok = $false
  if ($r.status -eq 200) {
    try {
      $j = $r.body | ConvertFrom-Json
      $nsurf = @($j.surfaces).Count
      $nmeas = [int]$j.counts.measured
      $nna = [int]$j.counts.not_available
      $nerr = [int]$j.counts.error
      $eok = ($nsurf -gt 0) -and ($nerr -eq 0) -and ($nsurf -eq [int]$j.counts.total)
    } catch { $eok = $false }
  }
  Add-Result $cycle 'GET /api/minimax (ecosystem)' $eok `
    "http=$($r.status) surfaces=$nsurf measured=$nmeas not_available=$nna error=$nerr"

  # The lifecycle report has to be REACHABLE, not merely written. A verifier
  # whose result is a file nothing can read is decoration: verify-server.ps1
  # claimed in its own docstring, and README.md repeated, that "the Overview
  # panel reads" this report - and nothing did. /api/verify is what makes that
  # true.
  #
  # The verdict it carries is deliberately NOT gated. During a cycle this route
  # serves the PREVIOUS run by definition - the current one is still being
  # written - so asserting PASS here would assert that a stale file is fresh.
  # What is gated is reachability and shape.
  $r = Invoke-Api '/api/verify'
  $vok = $false
  $vverdict = ''
  if ($r.status -eq 200) {
    try {
      $j = $r.body | ConvertFrom-Json
      $vverdict = [string]$j.verdict
      $vok = ($null -ne $j)
    } catch { $vok = $false }
  }
  Add-Result $cycle 'GET /api/verify (report reachable)' $vok `
    "http=$($r.status) serves-previous-verdict=$vverdict"

  $r = Invoke-Api '/api/does-not-exist'
  Add-Result $cycle 'GET /unknown -> 404' ($r.status -eq 404) "http=$($r.status)"

  # ---- 4. SSE -----------------------------------------------------------
  $sse = Read-Sse $Port
  $sseOk = ($sse -match 'event:\s*state') -and ($sse -match '"generated"')
  Add-Result $cycle 'GET /api/stream (SSE)' $sseOk "bytes=$($sse.Length) has-event=$($sse -match 'event:\s*state')"

  # The listener is single-threaded, so an SSE handler that never returned
  # would wedge every other route. This asserts the stream ENDS, and then
  # asserts the server still answers immediately - the property the dashboard
  # depends on.
  $tw = [Diagnostics.Stopwatch]::StartNew()
  $after = Invoke-Api '/api/health'
  $tw.Stop()
  $freeAfterStream = ($after.status -eq 200) -and ($tw.ElapsedMilliseconds -lt 8000)
  Add-Result $cycle 'API still live after SSE' $freeAfterStream `
    "http=$($after.status) in $($tw.ElapsedMilliseconds)ms"

  # ---- 5. security boundary --------------------------------------------
  # Read over a raw socket so the refusal BODY is visible, not just the code.
  $r = Read-Http 'POST' '/api/action' '{"id":"rm -rf / --no-preserve-root"}'
  $refused = ($r.status -eq 400) -and ($r.body -match 'unknown or forbidden') -and ($r.body -match 'rm -rf')
  Add-Result $cycle 'POST injected id -> 400 + names it' $refused "http=$($r.status) body=$($r.body.Trim())"

  $r = Read-Http 'POST' '/api/action' '{"id":"deps_check; whoami"}'
  $sm = ($r.status -eq 400) -and ($r.body -match 'unknown or forbidden')
  Add-Result $cycle 'POST smuggled id -> 400' $sm "http=$($r.status) body=$($r.body.Trim())"

  $r = Read-Http 'POST' '/api/action' '{"id":"Invoke-Expression"}'
  Add-Result $cycle 'POST shell-ish id -> 400' ($r.status -eq 400) "http=$($r.status)"

  $r = Read-Http 'POST' '/api/action' '{}'
  Add-Result $cycle 'POST empty body -> 400' ($r.status -eq 400) "http=$($r.status) body=$($r.body.Trim())"

  # ---- 6. STOP gate -----------------------------------------------------
  $r = Invoke-Api '/api/action' 'POST' '{"id":"wf_stop_ack"}'
  $gateOk = ($r.status -eq 200) -and ($r.body -match 'REFUSED')
  Add-Result $cycle 'POST wf_stop_ack no arg -> refuses' $gateOk "http=$($r.status) refused=$($r.body -match 'REFUSED')"

  if ($SkipActions) {
    Add-NotRun $cycle 'POST wf_state / skills_list' '-SkipActions was passed'
  } else {
    $r = Invoke-Api '/api/action' 'POST' '{"id":"wf_state"}'
    $sok = ($r.status -eq 200) -and ($r.body -match 'BIMODAL WORKFLOW')
    Add-Result $cycle 'POST wf_state (read-only)' $sok "http=$($r.status) bytes=$($r.body.Length)"

    $r = Invoke-Api '/api/action' 'POST' '{"id":"skills_list"}'
    $skok = ($r.status -eq 200) -and ($r.body -match 'tany-llm-to-sentinel')
    Add-Result $cycle 'POST skills_list' $skok "http=$($r.status)"
  }

  # ---- 7. stop, and prove the teardown took effect ----------------------
  $t1 = Get-Date
  $stopped = Invoke-Orchestrator 'stop'
  $stopSecs = [math]::Round(((Get-Date) - $t1).TotalSeconds, 1)
  $backDead = Wait-UrlDead "http://127.0.0.1:$BackPort/api/health" -TimeoutSec 45
  $frontDead = Wait-UrlDead "http://127.0.0.1:$Port/healthz" -TimeoutSec 45
  $portFree = -not (Test-Port $BackPort)
  $teardownOk = ($stopped.rc -eq 0) -and $backDead -and $frontDead -and $portFree
  Add-Result $cycle 'stop: both planes down' $teardownOk `
    ("exit=$($stopped.rc) backendClosed=$backDead frontDead=$frontDead portFree=$portFree in ${stopSecs}s")

  # After a stop, the ONLY processes that should remain are on reserved ports.
  # Anything left on the back port means the teardown did not take effect.
  $left = @(Get-ServerOnPort)
  $leftBad = @($left | Where-Object { $_.IsBack -or $_.IsFront })
  $leftUnknown = @($left | Where-Object { -not $_.IsBack -and -not $_.IsFront -and -not $_.OnReserved })
  if ($leftBad.Count -eq 0) {
    Add-Result $cycle 'stop: both planes released' $true `
      "nothing left on $BackPort or $Port" +
      $(if ($leftUnknown.Count -gt 0) { "; $($leftUnknown.Count) unattributed elsewhere (not ours)" } else { '' })
  } else {
    Add-Result $cycle 'stop: both planes released' $false `
      "pid(s) $($leftBad.ProcessId -join ', ') still on port(s) $((($leftBad | ForEach-Object { $_.Port }) -join ', ')) after stop"
  }
}

# --------------------------------------------------------------------------
$total = $results.Count
$passN = @($results | Where-Object { $_.pass -eq $true }).Count
$failN = @($results | Where-Object { $_.pass -eq $false }).Count
# `$report` (the object) and `$REPORT_PATH` (the file) must not differ only by
# case. PowerShell folds them into one variable, which is how the collector came
# to write its state to a file named after an OrderedDictionary. The
# ps_variable_case_collisions check in monitor.py guards this.
$report = [pscustomobject]@{
  generated    = (Get-Date).ToUniversalTime().ToString('o')
  topology     = 'dual-plane'
  front_port   = $Port
  back_port    = $BackPort
  container    = $CONTAINER
  cycles       = $Cycles
  actions      = (-not $SkipActions)
  total        = $total
  passed       = $passN
  failed       = $failN
  not_run      = $script:notRun
  # Carried through so the report can be read without cross-referencing the
  # live /api/health route. NOT part of this script's verdict - see the note
  # printed next to the health probe.
  monitor_overall = $script:monitorOverall
  verdict      = if ($failN -eq 0) { 'PASS' } else { 'FAIL' }
  results      = $results
}
# Windows PowerShell 5.1's -Encoding UTF8 writes a BOM, and `json.load` in
# Python rejects that with "Unexpected UTF-8 BOM". A report meant to be read by
# a machine must not need a magic argument, so it is written BOM-less.
$utf8NoBom = New-Object System.Text.UTF8Encoding $false
[IO.File]::WriteAllText($REPORT_PATH, ($report | ConvertTo-Json -Depth 6), $utf8NoBom)

$verdictColour = if ($failN -eq 0) { 'Green' } else { 'Red' }
Write-Host ''
Write-Host ("VERDICT: {0}   {1} passed / {2} failed / {3} not-run  ({4} checks, {5} cycle(s))" -f `
  $report.verdict, $passN, $failN, $script:notRun, $total, $Cycles) -ForegroundColor $verdictColour
Write-Host "report: $REPORT_PATH" -ForegroundColor DarkGray
Write-Host ''

exit $(if ($failN -eq 0) { 0 } else { 1 })
