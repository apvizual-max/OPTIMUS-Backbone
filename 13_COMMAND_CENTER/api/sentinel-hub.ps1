<#
.SYNOPSIS
  SENTINEL Command Center - deployment orchestrator. Manages BOTH planes.

.DESCRIPTION
  The SENTINEL deployment has two halves, and they live in different places on
  purpose:

    BACKEND  127.0.0.1:8912  a Windows PowerShell service. It owns every
                             measurement, because everything it measures is a
                             Windows fact: WMI, Get-NetTCPConnection, the mavis
                             and Hermes CLIs, the Docker Windows engine. It is
                             single-threaded HttpListener.

    FRONT    127.0.0.1:8910  the container 'mavis-sentinel-hub', nginx. It owns
                             the address Popy has bookmarked, and it is the only
                             thing that is shaped like a public deployment:
                             a real web tier, a gateway liveness path, a
                             readiness path, and one place to add TLS later.

  The front holds NO copy of the dashboard. A copy would drift from the data
  that was actually measured, and a dashboard reporting numbers nobody measured
  is worse than no dashboard. So the front proxies to the backend.

  Why 8910 for the front and not the backend: 8910 is the address already in
  Popy's browser, in the skills, in the UI text and in the reports. Keeping the
  published port constant means the deployment changed and nothing he reads had
  to. 8900 belongs to the separate OPTIMUS Control Center and is never touched.

  Port 8900/8901 note: the reference project 90_CONTROL_CENTER is a DIFFERENT
  system. Its front is 8901. Nothing here reads or writes either.

.PARAMETER Action
  start | stop | restart | status | install-startup | uninstall-startup | logs

.EXAMPLE
  powershell -NoProfile -ExecutionPolicy Bypass -File sentinel-hub.ps1 start
  powershell -NoProfile -ExecutionPolicy Bypass -File sentinel-hub.ps1 status
#>
[CmdletBinding()]
param(
  [ValidateSet('start', 'stop', 'restart', 'status', 'install-startup', 'uninstall-startup', 'logs')]
  [string]$Action = 'status',
  [int]$FrontPort = 8910,
  [int]$BackPort = 8912,
  [int]$WaitSeconds = 60,
  [int]$LogLines = 60
)

$ErrorActionPreference = 'Stop'
$API = $PSScriptRoot
$ROOT = Split-Path -Parent $API
# _PID suffix: PowerShell variable names are case-insensitive and a bare $pid
# is the automatic current-process variable.
$LAUNCHER = Join-Path $API 'sentinel-cc.ps1'
$CONTAINER = 'mavis-sentinel-hub'
$STARTUP_DIR = Join-Path $env:APPDATA 'Microsoft\Windows\Start Menu\Programs\Startup'
$STARTUP_BAT = Join-Path $STARTUP_DIR 'SENTINEL Command Center.bat'

function Test-Listening {
  param([int]$OnPort)
  try {
    $c = New-Object Net.Sockets.TcpClient
    $iar = $c.BeginConnect('127.0.0.1', $OnPort, $null, $null)
    $ok = $iar.AsyncWaitHandle.WaitOne(900, $false)
    if ($ok) { $c.EndConnect($iar) }
    $c.Close()
    return $ok
  } catch { return $false }
}

function Get-ContainerState {
  # Returns 'running' | 'exited' | 'absent' | 'no-docker'. Never throws:
  # a missing Docker engine is a state to report, not an error to propagate.
  $raw = docker inspect --format '{{.State.Status}}' $CONTAINER 2>$null
  if ($LASTEXITCODE -ne 0) {
    $raw = docker ps -a --filter "name=^$CONTAINER$" --format '{{.Status}}' 2>$null
    if ($LASTEXITCODE -ne 0 -or -not $raw) { return 'no-docker-or-absent' }
    $raw = ($raw -split ' ')[0]
  }
  if ($raw) { return $raw.Trim() } else { return 'absent' }
}

function Get-ContainerHealth {
  $h = docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}' $CONTAINER 2>$null
  if ($LASTEXITCODE -eq 0 -and $h) { return $h.Trim() } else { return 'unknown' }
}

function Test-HttpOk {
  param([string]$Url, [int]$Timeout = 10)
  try {
    $r = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec $Timeout
    return ($r.StatusCode -eq 200)
  } catch { return $false }
}

function Get-ServerOnPort {
  # Every `server.ps1` process on the box, with the port it was told to use.
  #
  # Used to find STRAYS: a backend that bound the FRONT port is always wrong,
  # because that port belongs to the container.
  #
  # SCANNED WIDE, CLASSIFIED BY PORT, ON PURPOSE. An earlier version required
  # SENTINEL_PRIME in the command line. That filter evades itself: a server
  # started with a relative path (`-File 13_COMMAND_CENTER\api\server.ps1`),
  # a copy at another path, or one launched through `sentinel-cc.ps1` carries
  # no SENTINEL_PRIME token - and the worst case is precisely the one that
  # matters, a squatter holding 8910. The `stop` verb uses this to clear
  # strays, so a filter that misses a squatter leaves a HIJACKED deployment in
  # place and reports the stop as clean.
  #
  # A backend bound to the FRONT port is a deployment fault regardless of which
  # project it belongs to: that address is the container's, and the honest
  # response is to name the pid. Callers that need to be careful about other
  # systems use the port, not the path, to decide.
  param([string]$Marker = 'server.ps1')
  $found = @()
  try {
    $all = @(Get-CimInstance Win32_Process `
      -Filter "Name='powershell.exe' AND CommandLine LIKE '%$Marker%'" `
      -ErrorAction SilentlyContinue | Where-Object { $_.ProcessId -ne $PID })
    foreach ($proc in $all) {
      $p = 0
      if ($proc.CommandLine -match '-Port\s+(\d+)') { $p = [int]$matches[1] }
      $found += [pscustomobject]@{
        ProcessId = $proc.ProcessId
        Port      = $p
        # Reported, not filtered on: it is evidence about identity, and a
        # caller may legitimately need to know it is unavailable.
        PathMatch = ($proc.CommandLine -like '*SENTINEL_PRIME*')
      }
    }
  } catch { }
  return @($found)
}

function Get-NonLoopbackIPv4 {
  # Every routable IPv4 on this machine. Loopback and link-local (169.254.x.x)
  # are excluded because binding them is not "reachable off-box" - they are not
  # off-box at all.
  $addrs = @()
  try {
    $addrs = @([System.Net.NetworkInformation.NetworkInterface]::GetAllNetworkInterfaces() |
      Where-Object { $_.OperationalStatus -eq 'Up' } |
      ForEach-Object { $_.GetIPProperties().UnicastAddresses } |
      ForEach-Object { $_.Address } |
      Where-Object { $_.AddressFamily -eq 'InterNetwork' } |
      ForEach-Object { $_.ToString() } |
      Where-Object { $_ -notlike '127.*' -and $_ -notlike '169.254.*' })
  } catch { }
  return @($addrs)
}

function Test-PortReachable {
  # TRUE only if a TCP connect actually completes within the timeout.
  # A connect that times out and a connect that is refused are both "not
  # reachable", and both are the answer we want; only a completed connection
  # counts as reachable, so a firewall cannot be mistaken for exposure.
  param([string]$Address, [int]$Port, [int]$TimeoutMs = 1200)
  $client = $null
  try {
    $client = New-Object System.Net.Sockets.TcpClient
    $iar = $client.BeginConnect($Address, $Port, $null, $null)
    if (-not $iar.AsyncWaitHandle.WaitOne($TimeoutMs, $false)) { return $false }
    $client.EndConnect($iar)
    return $true
  } catch {
    return $false
  } finally {
    if ($null -ne $client) { try { $client.Close() } catch { } }
  }
}

function Test-FrontIsHijacked {
  # TRUE when the front port answers but is NOT the container.
  #
  # Found in anger: a stray `sentinel-cc.ps1` had bound 8910 directly, so
  # 8910 kept answering with 200 long after the container was stopped. Every
  # "is the link up" probe said yes, and the cold-start teardown could never
  # take effect because the thing it was trying to stop was not the thing
  # holding the port. A hijacked front is indistinguishable from a healthy
  # front by status code alone - only the deployment header tells them apart.
  if (-not (Test-Listening -OnPort $FrontPort)) { return $null }
  try {
    $r = Invoke-WebRequest -Uri "http://127.0.0.1:$FrontPort/healthz" -UseBasicParsing -TimeoutSec 8
    if ($r.Headers['X-SENTINEL-Deployment'] -eq $CONTAINER) { return $null }
  } catch { }
  $squatters = @(Get-ServerOnPort | Where-Object { $_.Port -eq $FrontPort })
  return $squatters
}

function Wait-HttpOk {
  # Poll an HTTP endpoint until it answers 200, or the deadline passes.
  # Used wherever the question is "is this service actually serving" rather than
  # "is something bound to this port". Returns $true/$false; never throws.
  param([string]$Url, [int]$TimeoutSec = 60, [int]$PollMs = 500)
  $deadline = (Get-Date).AddSeconds($TimeoutSec)
  while ((Get-Date) -lt $deadline) {
    if (Test-HttpOk -Url $Url -Timeout 6) { return $true }
    Start-Sleep -Milliseconds $PollMs
  }
  return $false
}

function Write-Line {
  param($Label, $Value, $Colour = 'Gray')
  # The parentheses around the -f expression are load-bearing: without them
  # PowerShell binds ', ' and $Value as two more positional arguments and
  # $Value lands in the $Colour slot, which fails to convert to ConsoleColor.
  Write-Host ("  {0,-16} {1}" -f $Label, $Value) -ForegroundColor $Colour
}

switch ($Action) {

  'start' {
    Write-Host ''
    Write-Host '  Starting SENTINEL deployment (backend + container)...' -ForegroundColor Cyan

    # ---- backend first -------------------------------------------------
    # The front is useless without it, and starting the front first would
    # produce a gateway that answers /healthz while /readyz says no - which
    # looks like a working deployment for exactly as long as nobody reads the
    # second path.
    & $LAUNCHER -Action start -Port $BackPort -NoBrowser | Out-Null

    # A bound port is not a started service. The backend is an HttpListener:
    # the socket is bound before the listener is ready to answer, so a single
    # Test-Listening taken right after launch returns true while HTTP is still
    # failing. That produced "backend LISTENING" and "readyz BACKEND NOT
    # ANSWERING" in the same report, and an exit code 1 for a deployment that
    # was healthy a second later. Poll the thing we actually depend on.
    $backServing = Wait-HttpOk -Url "http://127.0.0.1:$BackPort/api/health" -TimeoutSec $WaitSeconds
    $backBound = Test-Listening -OnPort $BackPort
    $backUp = $backBound
    $backLabel = if ($backServing) { 'SERVING' }
                elseif ($backBound) { 'BOUND BUT NOT ANSWERING' }
                else { 'NOT ANSWERING' }
    Write-Line 'backend' ("127.0.0.1:$BackPort  $backLabel") `
      $(if ($backServing) { 'Green' } elseif ($backBound) { 'Yellow' } else { 'Red' })

    # ---- front ---------------------------------------------------------
    $state = Get-ContainerState
    if ($state -eq 'running') {
      Write-Line 'container' 'already running (idempotent)' 'Yellow'
    } else {
      if ($state -eq 'no-docker-or-absent') {
        docker ps -a --filter "name=^$CONTAINER$" --format '{{.Names}}' 2>$null | Out-Null
        if ($LASTEXITCODE -eq 0) {
          Write-Line 'container' 'starting existing' 'Cyan'
          docker start $CONTAINER | Out-Null
        } else {
          Write-Line 'container' 'Docker engine not reachable' 'Red'
        }
      } else {
        Write-Line 'container' 'starting existing' 'Cyan'
        docker start $CONTAINER | Out-Null
      }
      Start-Sleep -Seconds 2
    }

    $state = Get-ContainerState
    Write-Line 'container' ("$CONTAINER  $state") $(if ($state -eq 'running') { 'Green' } else { 'Red' })

    # ---- wait for the published address --------------------------------
    $deadline = (Get-Date).AddSeconds($WaitSeconds)
    $frontUp = $false
    while ((Get-Date) -lt $deadline) {
      if (Test-HttpOk -Url "http://127.0.0.1:$FrontPort/healthz" -Timeout 5) { $frontUp = $true; break }
      Start-Sleep -Seconds 2
    }
    Write-Line 'front' ("127.0.0.1:$FrontPort  " + $(if ($frontUp) { 'SERVING' } else { 'NOT ANSWERING' })) `
      $(if ($frontUp) { 'Green' } else { 'Red' })

    $backOk = Test-HttpOk -Url "http://127.0.0.1:$FrontPort/readyz" -Timeout 12
    Write-Line 'readyz' $(if ($backOk) { 'backend answering behind the front' } else { 'FRONT UP, BACKEND NOT ANSWERING' }) `
      $(if ($backOk) { 'Green' } else { 'Red' })

    Write-Host ''
    if ($frontUp -and $backOk) {
      Write-Host "  DEPLOYMENT UP   http://127.0.0.1:$FrontPort/" -ForegroundColor Green
      Write-Host ''
      exit 0
    }
    Write-Host '  DEPLOYMENT INCOMPLETE - see the two lines above.' -ForegroundColor Red
    Write-Host "  Open http://127.0.0.1:$FrontPort/healthz and /readyz to see which plane is missing." -ForegroundColor DarkGray
    Write-Host ''
    exit 1
  }

  'stop' {
    Write-Host ''
    Write-Host '  Stopping SENTINEL deployment...' -ForegroundColor Cyan
    $state = Get-ContainerState
    if ($state -eq 'running' -or $state -eq 'exited') {
      # NO `| Out-Host` HERE, and the reason is a measured failure.
      #
      # `docker stop $CONTAINER 2>&1 | Out-Host` worked perfectly from an
      # interactive console and did nothing at all when this script was driven
      # with its output REDIRECTED - which is how the test harness invokes it,
      # and how any scheduled task or CI step would. Out-Host targets the
      # console host explicitly; with stdout a pipe there is no console, the
      # statement never completed, and because $ErrorActionPreference is
      # 'Stop' the whole `stop` branch died BEFORE `docker stop` ran and
      # before the backend was touched. The deployment stayed fully up.
      #
      # That produced a test failure that pointed at the wrong thing: the
      # cold-start check reported "teardown did not take effect" and it was
      # right, but the cause was in the teardown tool, not in the startup
      # path being tested.
      #
      # Writing to the output stream instead works identically on a console
      # and through a pipe. Do not "restore" Out-Host here for tidiness.
      docker stop $CONTAINER 2>&1
    } else {
      Write-Host "  container not present ($state)" -ForegroundColor DarkGray
    }
    & $LAUNCHER -Action stop -Port $BackPort | Out-Null
    Write-Line 'backend' ("127.0.0.1:$BackPort  stopped") 'DarkGray'

    # Clear STRAYS. A backend bound to the FRONT port is a deployment fault:
    # that address belongs to the container. Left alone, it keeps answering
    # after the container stops, which makes a stopped deployment look alive and
    # makes any teardown unable to take effect. It is also the exact thing that
    # made a cold-start test fail for many cycles while the startup path itself
    # was working perfectly.
    $strays = @(Get-ServerOnPort | Where-Object { $_.Port -eq $FrontPort })
    foreach ($s in $strays) {
      $killed = $false
      try { Stop-Process -Id $s.ProcessId -Force -ErrorAction Stop; $killed = $true } catch { $killed = $false }
      if ($killed) {
        Write-Line 'stray' ("killed pid $($s.ProcessId) - a backend on the FRONT port $FrontPort") 'Yellow'
      } else {
        Write-Line 'stray' ("could NOT kill pid $($s.ProcessId) squatting $FrontPort - stop it by hand") 'Red'
      }
    }
    if ($strays.Count -eq 0) { Write-Line 'stray' 'none - no backend squatting the front port' 'DarkGray' }

    Write-Host ''
    exit 0
  }

  'restart' {
    & $PSCommandPath -Action stop -FrontPort $FrontPort -BackPort $BackPort
    Start-Sleep -Seconds 2
    & $PSCommandPath -Action start -FrontPort $FrontPort -BackPort $BackPort -WaitSeconds $WaitSeconds
    exit $LASTEXITCODE
  }

  'status' {
    $backUp = Test-Listening -OnPort $BackPort
    $state = Get-ContainerState
    $health = Get-ContainerHealth
    $frontUp = Test-HttpOk -Url "http://127.0.0.1:$FrontPort/healthz" -Timeout 6
    $readyOk = Test-HttpOk -Url "http://127.0.0.1:$FrontPort/readyz" -Timeout 12

    Write-Host ''
    Write-Host '  SENTINEL Command Center - deployment status' -ForegroundColor Cyan
    Write-Host '  ' + ('-' * 52)
    Write-Line 'URL' ("http://127.0.0.1:$FrontPort/") 'White'
    Write-Line 'container' ("$CONTAINER  $state  health=$health") `
      $(if ($state -eq 'running' -and $health -eq 'healthy') { 'Green' } elseif ($state -eq 'running') { 'Yellow' } else { 'Red' })
    Write-Line 'front' ("127.0.0.1:$FrontPort  " + $(if ($frontUp) { 'SERVING' } else { 'not answering' })) `
      $(if ($frontUp) { 'Green' } else { 'Red' })
    Write-Line 'backend' ("127.0.0.1:$BackPort  " + $(if ($backUp) { 'LISTENING' } else { 'not answering' })) `
      $(if ($backUp) { 'Green' } else { 'Red' })
    Write-Line 'readyz' $(if ($readyOk) { 'both planes agreeing' } else { 'FRONT/BACKEND DISAGREE' }) `
      $(if ($readyOk) { 'Green' } else { 'Red' })
    # Loopback isolation is a CLAIM until something connects to the port from
    # outside the loopback range. This line used to print the reassurance as a
    # fixed string in DarkGray - it looked like a result and was decoration,
    # which is the one thing a status verb must never be. So it is measured
    # here, with a short timeout, and it says NOT_MEASURED rather than guessing
    # if it cannot be measured.
    $exposed = $false
    $nonLoop = @(Get-NonLoopbackIPv4)
    if ($nonLoop.Count -eq 0) {
      Write-Line 'loopback' 'NOT_MEASURED - no non-loopback IPv4 address on this machine' 'DarkGray'
    } else {
      $reachable = @()
      foreach ($a in $nonLoop) {
        if (Test-PortReachable -Address $a -Port $FrontPort -TimeoutMs 1200) { $reachable += $a }
      }
      if ($reachable.Count -gt 0) {
        $exposed = $true
        Write-Line 'loopback' ("REACHABLE OFF-BOX on $($reachable -join ', ') - NOT loopback-only") 'Red'
      } else {
        Write-Line 'loopback' ("refused on $($nonLoop.Count) non-loopback address(es) - loopback-only") 'Green'
      }
    }

    # A front port that answers but is NOT the container is the most deceptive
    # state this system can be in: every status probe says "up" and the thing
    # serving is not the deployment. Name it, and name the pid.
    $hijack = Test-FrontIsHijacked
    if ($null -ne $hijack) {
      if ($hijack.Count -gt 0) {
        Write-Line 'HIJACKED' ("front $FrontPort is answered by " + (($hijack | ForEach-Object { "pid $($_.ProcessId)" }) -join ', ') + " - NOT the container") 'Red'
      } else {
        Write-Line 'HIJACKED' ("front $FrontPort answers but is not the container") 'Red'
      }
    } else {
      Write-Line 'front owner' 'the container (deployment header present)' 'DarkGray'
    }

    # The verdict names WHICH plane is missing. "Something is wrong" is not an
    # answer; a gateway that is up while its app is down is a different fault
    # with a different fix, and an operator who cannot tell them apart will fix
    # the wrong one.
    $verdict = 'UP'
    $vColour = 'Green'
    if ($exposed) { $verdict = 'UP BUT EXPOSED (front port reachable off-box)'; $vColour = 'Red' }
    elseif ($null -ne $hijack) { $verdict = 'HIJACKED (front port served by a non-container process)'; $vColour = 'Red' }
    elseif (-not $frontUp -and -not $backUp) { $verdict = 'DOWN (both planes)'; $vColour = 'Red' }
    elseif (-not $frontUp) { $verdict = 'DEGRADED (backend up, container front down)'; $vColour = 'Red' }
    elseif (-not $backUp -or -not $readyOk) { $verdict = 'DEGRADED (front up, backend down)'; $vColour = 'Red' }
    elseif ($state -ne 'running') { $verdict = "DEGRADED (serving, container state=$state)"; $vColour = 'Yellow' }
    Write-Line 'VERDICT' $verdict $vColour
    Write-Host ''

    # `exit`, not `return`. In a -File script `return 0` both sets the exit
    # code AND writes 0 to the output stream, so `status` printed a bare "0"
    # under its own report. Cosmetic, but a status command that emits a
    # stray value is the kind of thing that makes people stop reading it.
    if ($verdict -eq 'UP') { exit 0 } else { exit 1 }
  }

  'logs' {
    Write-Host ''
    Write-Host "  container logs ($CONTAINER), last $LogLines lines:" -ForegroundColor Cyan
    docker logs --tail $LogLines $CONTAINER 2>&1
    exit 0
  }

  'install-startup' {
    # No elevation, no scheduled task, no service. A file in the Startup
    # folder is the one persistence mechanism on Windows that needs none of
    # those, and it is removable by deleting that single file.
    if (-not (Test-Path $STARTUP_DIR)) { New-Item -ItemType Directory -Path $STARTUP_DIR -Force | Out-Null }
    $logDir = Join-Path (Split-Path -Parent $ROOT) '09_LOGS'
    if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir -Force | Out-Null }
    $logPath = Join-Path $logDir 'hub-startup.log'

    # Two hard-won constraints are baked into this file.
    #
    # 1. -File, NOT -Command with an inline quoted script. The first version
    #    used `start "" /min powershell ... -Command "& '...' -Action start"`,
    #    and it FAILED AT LOGON: both planes stayed down and nothing anywhere
    #    said why. `start` has its own quoting rules and a multi-line quoted
    #    argument is exactly the case it gets wrong. -File with one quoted path
    #    is the form that survives.
    #
    # 2. It logs, and it logs the exit code. The failure above was SILENT -
    #    a startup entry that cannot work and cannot say so is a trap, and the
    #    only reason this one was found is that it was tested from a known-down
    #    state. A path never executed is not a path.
    # 3. THE GENERATOR ITSELF WAS WRONG, twice, and both times it wrote a
    #    corrupt .bat that failed at logon. Do not use `+` to build lines
    #    inside an @( ... ) array literal:
    #
    #        @('set "X=' + $p + '"', 'next line') -join "`r`n"
    #
    #    reads like concatenation but is not. `'next line'` and the following
    #    literal form an ARRAY, and `string + array` coerces the array with
    #    spaces, so the two "lines" merge and the ports land in the wrong
    #    place. The output looked plausible in a console and was unreadable to
    #    cmd.exe. A single-quoted here-string with .Replace() placeholders
    #    cannot fail this way, so that is what is used below.
    $tmpl = @'
@echo off
REM SENTINEL Command Center - brings up the whole deployment at logon:
REM the Windows data plane (127.0.0.1:__BACK__) and the container front
REM (127.0.0.1:__FRONT__). Installed by Mavis.
REM
REM To remove: delete this one file.
REM   %APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\SENTINEL Command Center.bat
set "SENTINEL_HUB=__HUB__"
set "SENTINEL_LOG=__LOG__"
REM A per-run UNIQUE file, not a fixed one. The backend is launched by the very
REM line below while this redirect is open, so the long-lived server.ps1 process
REM INHERITS the stdout handle and holds it for its whole lifetime. With a fixed
REM name, run N+1 then cannot write to the file run N's server still holds - every
REM echo fails, silently, and the evidence for that run is lost. Measured: the
REM fixed %TEMP%\sentinel-startup-last.txt was locked by pid 57292 and 4 of 4
REM writes in the next run failed while the entry still reported success.
REM A name unique to the run can never be held by a previous run's survivor.
set "SENTINEL_RUNLOG=%TEMP%\sentinel-startup-%RANDOM%%RANDOM%-%RANDOM%.txt"
REM
REM THE LOG MUST NEVER BE ABLE TO STOP THE DEPLOYMENT.
REM
REM Measured 2026-10-06 with a controlled experiment: two identical launches of
REM this entry, the only difference being whether the durable log could be
REM written. With the log locked, the deployment did NOT come up (78.5 s, nothing
REM bound) and the log gained 0 bytes - yet the entry still exited 0. With the log
REM writable it was up in 24.1 s and logged 456 B.
REM
REM Cause: `cmd ... >> log` cannot open the redirect target, so cmd never runs
REM the command. The whole start was inside the redirect, so a locked log meant
REM no deployment AND a success exit code. A log is evidence; evidence must not
REM be able to veto the thing it observes.
REM
REM So the start writes to a private per-run file that no survivor holds, and the
REM fold into the durable log is a separate, best-effort step whose failure is
REM reported but never fatal.
echo. >> "%SENTINEL_RUNLOG%" 2>nul
echo === startup %DATE% %TIME% === >> "%SENTINEL_RUNLOG%" 2>nul

REM A SPACE before >> is load-bearing: cmd reads a digit immediately preceding a
REM redirection operator as a FILE DESCRIPTOR number, so `echo x=1>>log`
REM redirects handle 1 and the text never reaches the file. Do not tidy it.
powershell -NoProfile -ExecutionPolicy Bypass -File "%SENTINEL_HUB%" -Action start -FrontPort __FRONT__ -BackPort __BACK__ >> "%SENTINEL_RUNLOG%" 2>&1
set "SENTINEL_RC=%ERRORLEVEL%"

REM THE EXIT CODE IS WRITTEN TO THE DURABLE LOG, NOT TO THE RUNLOG.
REM The backend inherits this entry's stdout - the runlog handle - and holds it
REM for its whole life WITHOUT FILE_SHARE_DELETE. So `echo >> RUNLOG` after that
REM line cannot reopen the file: measured 2026-10-06, every run that actually
REM started a backend lost its exit line (6 idempotent runs logged one, 4 fresh
REM starts logged none - the runs whose whole job is to start it). The durable
REM log is held by nobody, so this write succeeds.
REM
REM It is written AFTER the fold so the log reads in the order things happened:
REM marker, transcript, then the verdict on that run. The fold can only fail
REM while the durable log is held, and then this write fails with it - reported
REM by the fold's own size check below.
REM
REM NOTHING may sit inside the if/else block below except commands. Inside a
REM parenthesised block cmd does NOT treat a REM line as a comment - it EXECUTES
REM it. Prose placed there became a command and printed "'TEMP' is not
REM recognized" on 2026-10-06. Comments belong above the block, never within it.
for %%A in ("%SENTINEL_LOG%") do set "SENTINEL_LOG_PREV=%%~zA"
type "%SENTINEL_RUNLOG%" >> "%SENTINEL_LOG%" 2>nul
for %%A in ("%SENTINEL_LOG%") do set "SENTINEL_LOG_NOW=%%~zA"
if "%SENTINEL_LOG_NOW%"=="%SENTINEL_LOG_PREV%" (
  echo WARNING: the deployment was started, but the startup log could not be written.
  echo          %SENTINEL_LOG% is locked by another process.
  echo          This run's output is preserved at %SENTINEL_RUNLOG%
  echo          Check http://127.0.0.1:__FRONT__/ to confirm the deployment is up.
) else (
  del "%SENTINEL_RUNLOG%" >nul 2>&1
)
REM The exit code is the one value that says whether THIS startup worked.
echo exit=%SENTINEL_RC% >> "%SENTINEL_LOG%" 2>nul
exit /b %SENTINEL_RC%
'@
    $content = $tmpl.Replace('__HUB__', $PSCommandPath).Replace('__LOG__', $logPath).
                 Replace('__FRONT__', [string]$FrontPort).Replace('__BACK__', [string]$BackPort)

    # Force CRLF. The here-string above is stored in this file with whatever
    # line endings the file itself has, and Set-Content does NOT normalise the
    # newlines INSIDE a multi-line string. So the .bat was being written with
    # bare LF endings, which cmd.exe does not reliably honour - the exact class
    # of defect that produced the two silent failures above. Normalise
    # explicitly rather than trusting the editor that wrote this script.
    $content = $content.Replace("`r`n", "`n").Replace("`n", "`r`n")

    # Refuse to install a file we have not read back. Both prior failures were
    # silent, and both produced a .bat that was structurally wrong in a way
    # that is obvious only when the bytes are inspected. A generator that
    # cannot verify its own output is a generator that will fail at logon.
    #
    # The checks are STRUCTURAL, not a line count. A magic number is just the
    # previous correct answer with a hardcoded expiry: the first version of
    # this guard compared against a count taken from the broken file, and it
    # "worked" by rejecting a correct one. What actually matters is that the
    # lines that must be whole, are whole.
    $badTokens = @()
    $lines = $content -split "`r?`n"
    if ($content -match '__[A-Z]+__') { $badTokens += 'unsubstituted placeholder' }

    # Each 'set' must be a well-formed quoted assignment. The COUNT is not
    # asserted: a magic number here would reject the correct file the moment
    # the template legitimately grows a variable, which is exactly the failure
    # mode the CRLF check below was written to avoid. What must hold is that
    # every set is whole - closed quote, name and value - not how many there are.
    $setLines = @($lines | Where-Object { $_ -like 'set *' })
    if ($setLines.Count -lt 2) { $badTokens += "expected at least 2 'set' lines, found $($setLines.Count)" }
    foreach ($l in $setLines) {
      if (-not $l.TrimEnd().EndsWith('"')) { $badTokens += ("unterminated set line: " + $l) }
      # set "NAME=value" - the name must be present and non-empty.
      if ($l -notmatch '^set\s+"([^=]+)=') { $badTokens += ("set line without NAME=value: " + $l) }
    }

    # The variables the entry depends on must all be assigned. A missing one
    # makes cmd expand an empty path, which fails in a way that names no cause.
    foreach ($v in @('SENTINEL_HUB', 'SENTINEL_LOG', 'SENTINEL_RUNLOG')) {
      $assigned = @($setLines | Where-Object { $_ -match "^set\s+`"$v=" }).Count
      if ($assigned -ne 1) { $badTokens += "variable $v must be assigned exactly once, found $assigned" }
    }

    # Nothing but commands inside a parenthesised block. Inside ( ) cmd does NOT
    # treat a REM line as a comment - it EXECUTES it, so prose placed in a block
    # becomes a command and prints "'X' is not recognized" at logon. This shipped
    # once already (2026-10-06) and the file installed cleanly. Track block depth
    # and reject any comment or blank line that appears while depth > 0.
    $depth = 0
    for ($i = 0; $i -lt $lines.Count; $i++) {
      $ln = $lines[$i]
      $trim = $ln.Trim()
      # A comment line contributes NO parentheses. Prose about `cmd ( ) blocks`
      # contains unbalanced brackets that would otherwise move the depth counter
      # and make this guard reject a valid file - which is worse than the defect
      # it exists to catch, because it blocks every future install.
      if ($trim -eq '' -or $trim -match '^(REM|::)') {
        if ($depth -gt 0 -and $trim -match '^(REM|::)') {
          $badTokens += ("comment inside a (...) block at line $($i + 1) - cmd executes it: " + $trim)
        }
        continue
      }
      $opens = ([regex]::Matches($ln, '\(')).Count
      $closes = ([regex]::Matches($ln, '\)')).Count
      $depth += $opens - $closes
      if ($depth -lt 0) { $depth = 0 }
    }

    # CRLF, and no bare LF anywhere. Verified on the string we are about to
    # write, because a .bat that looks right and is LF-only fails at logon and
    # says nothing.
    $lf = ($content.ToCharArray() | Where-Object { $_ -eq "`n" }).Count
    $cr = ($content.ToCharArray() | Where-Object { $_ -eq "`r" }).Count
    if ($lf -ne $cr) { $badTokens += "line endings are not CRLF (LF=$lf CR=$cr) - cmd.exe may mis-parse this" }

    $psLines = @($lines | Where-Object { $_ -like 'powershell -NoProfile*' })
    if ($psLines.Count -ne 1) {
      $badTokens += "the powershell invocation must be exactly 1 line, found $($psLines.Count) - a wrapped line will not execute"
    } else {
      $pl = $psLines[0]
      foreach ($needle in @('-Action start', "-FrontPort $FrontPort", "-BackPort $BackPort", '-File "%SENTINEL_HUB%"')) {
        if ($pl -notlike "*$needle*") { $badTokens += ("powershell line is missing: " + $needle) }
      }
    }

    if ($badTokens.Count -gt 0) {
      Write-Host ''
      Write-Host '  REFUSING to install a malformed startup entry:' -ForegroundColor Red
      foreach ($b in $badTokens) { Write-Host ("    - " + $b) -ForegroundColor Red }
      exit 1
    }

    Set-Content -Path $STARTUP_BAT -Value $content -Encoding ASCII

    # Read it back off the DISK, not out of the variable. The variable is what
    # we intended; the file is what cmd.exe will execute.
    $onDisk = Get-Content $STARTUP_BAT -Raw
    if ($onDisk -notmatch [regex]::Escape($PSCommandPath)) {
      Write-Host '  REFUSING to install: the path is not on disk in the written file.' -ForegroundColor Red
      exit 1
    }

    Write-Host ''
    Write-Host "  Installed: $STARTUP_BAT" -ForegroundColor Green
    Write-Host "  Logs to  : $logPath" -ForegroundColor Green
    Write-Host '  Remove with:  -Action uninstall-startup' -ForegroundColor DarkGray
    Write-Host ''
    exit 0
  }

  'uninstall-startup' {
    if (Test-Path $STARTUP_BAT) {
      Set-Content -Path $STARTUP_BAT -Value 'REM removed by Mavis' -Encoding ASCII
      Write-Host "  Neutralised: $STARTUP_BAT" -ForegroundColor Green
      Write-Host '  Delete that file to remove it entirely.' -ForegroundColor DarkGray
      exit 0
    }
    Write-Host '  No startup entry found.' -ForegroundColor DarkGray
    exit 0
  }
}
