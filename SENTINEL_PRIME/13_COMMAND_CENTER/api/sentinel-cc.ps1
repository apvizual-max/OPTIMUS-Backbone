<#
.SYNOPSIS
  SENTINEL Command Center - launcher. Starts, stops and reports the local server.

.DESCRIPTION
  Written 2026-10-04 because the Command Center kept dying and Popy was left
  with a dead link and no way to bring it back.

  The previous launcher (bat\sentinel-cc.bat) ran the server in the foreground
  of a console window. That has three failure modes, all of which occurred:

    1. It dies with its window. An agent-launched shell exiting took the server
       with it, and the link Popy had open went to connection-refused.
    2. Two invocations collide. The second bind on 8910 throws, so "just start
       it again" made things worse and looked like a broken build.
    3. There is no way to ask what is running. `status` is now a first-class
       verb rather than something you infer from a browser error.

  So: idempotent start, a PID file, an explicit stop, and a status that probes
  the PORT rather than trusting the PID file. A stale PID file with a dead
  process is cleaned up and reported, not treated as running.

  Detachment. The server is launched via Start-Process, which creates an
  independent process rather than a child that dies with this shell. That is
  enough to survive a shell exiting. It is NOT enough to survive the process
  tree being killed (an agent harness, a logoff, a scheduled task that ends).
  For that, register the scheduled task - see -InstallTask below, and note it
  is a system-level change that is reversible in one command.

.PARAMETER Action
  start | stop | restart | status | install-task | uninstall-task

.EXAMPLE
  powershell -NoProfile -ExecutionPolicy Bypass -File sentinel-cc.ps1 start
  powershell -NoProfile -ExecutionPolicy Bypass -File sentinel-cc.ps1 status
#>
[CmdletBinding()]
param(
  [ValidateSet('start', 'stop', 'restart', 'status', 'install-task', 'uninstall-task')]
  [string]$Action = 'status',
  [int]$Port = 8910,
  [switch]$NoBrowser,
  # Seconds to wait for the port to answer before declaring the start failed.
  [int]$WaitSeconds = 45
)

$ErrorActionPreference = 'Stop'
$ROOT = Split-Path -Parent $PSScriptRoot          # 13_COMMAND_CENTER
$API = Join-Path $ROOT 'api'
$STATE_DIR = Join-Path $ROOT 'api'
# _PID suffix because PowerShell variable names are case-insensitive and a
# bare $pid is the automatic current-process variable.
$PID_FILE = Join-Path $STATE_DIR 'sentinel-cc.pid'
$LOG_FILE = Join-Path $STATE_DIR 'sentinel-cc.log'
$ERR_FILE = Join-Path $STATE_DIR 'sentinel-cc.err.log'
$TASK_NAME = 'SENTINEL_CommandCenter'

function Test-Listening {
  param([int]$OnPort)
  try {
    $c = New-Object Net.Sockets.TcpClient
    $iar = $c.BeginConnect('127.0.0.1', $OnPort, $null, $null)
    $ok = $iar.AsyncWaitHandle.WaitOne(800, $false)
    if ($ok) { $c.EndConnect($iar) }
    $c.Close()
    return $ok
  } catch { return $false }
}

function Get-ServerProcess {
  # Match on the script path, never on a bare pid: a stale pid file must
  # never make this kill something unrelated that inherited the number.
  #
  # DO NOT "SIMPLIFY" THIS TO Get-NetTCPConnection -LocalPort 8910.
  # I did that, and it killed the running server. `HttpListener` on Windows
  # binds through the HTTP.sys kernel driver, so the listening socket is owned
  # by **pid 4 (System)** - not by the PowerShell process that serves it.
  # netstat agrees: "TCP 127.0.0.1:8910 ... LISTENING  4". Every "which process
  # owns the port" heuristic therefore returns System, and acting on it takes
  # down every server on the machine that uses HttpListener.
  # The filter is pushed INTO the WMI query, not applied afterwards: listing
  # every powershell.exe and filtering in PowerShell cost ~15 s of a 19.7 s
  # status call. The port is probed separately by Test-Listening, which is the
  # only thing here that answers "is it serving" - and it is the evidence this
  # whole script is built to trust.
  Get-CimInstance Win32_Process `
    -Filter "Name='powershell.exe' AND CommandLine LIKE '%server.ps1%'" `
    -ErrorAction SilentlyContinue |
    Where-Object { $_.CommandLine -like "*$Port*" }
}

function Write-StatusLine {
  param($Label, $Value, $Colour = 'Gray')
  Write-Host ("  {0,-14} {1}" -f $Label, $Value) -ForegroundColor $Colour
}

function Show-Status {
  $listening = Test-Listening -OnPort $Port

  # Read the pid file BEFORE any WMI. A status call was taking ~22 s and
  # virtually all of it was Get-CimInstance initialising the WMI provider - to
  # answer a question the pid file and the port had already answered. WMI is now
  # consulted only when it is the last remaining source of truth.
  $raw = $null; $alive = $false
  if (Test-Path $PID_FILE) {
    $raw = (Get-Content $PID_FILE -Raw).Trim()
    if ($raw -match '^\d+$') { $alive = [bool](Get-Process -Id ([int]$raw) -ErrorAction SilentlyContinue) }
  }
  # Only pay for WMI when the port says "running" but the pid file cannot
  # corroborate it.
  $procs = $null
  if ($listening -and (-not $raw -or -not $alive)) { $procs = @(Get-ServerProcess) }

  Write-Host ''
  Write-Host '  SENTINEL Command Center - status' -ForegroundColor Cyan
  Write-Host '  ' + ('-' * 46)
  Write-StatusLine 'URL' ("http://127.0.0.1:$Port/") 'White'
  # The parentheses are load-bearing: without them PowerShell binds
  # 'port ', + and $Port as three positional arguments, and $Port lands in
  # the $Colour slot and fails to convert to ConsoleColor. Caught by running
  # it, not by reading it.
  Write-StatusLine ('port ' + $Port) $(if ($listening) { 'LISTENING' } else { 'not answering' }) `
    $(if ($listening) { 'Green' } else { 'Red' })
  if ($null -ne $procs) {
    Write-StatusLine 'server proc' ("$($procs.Count) found (via WMI)") $(if ($procs.Count) { 'Green' } else { 'Red' })
  }
  if ($raw) {
    # Say plainly when the file lies. A pid file that is not corroborated by a
    # listening port is exactly the unmoveable-verdict mistake.
    Write-StatusLine 'pid file' ("$raw " + $(if ($alive) { '(process alive)' } else { '(STALE - process gone)' })) `
      $(if ($alive -and $listening) { 'Green' } else { 'Yellow' })
  } else {
    Write-StatusLine 'pid file' 'none' 'DarkGray'
  }
  if (Test-Path $ERR_FILE) {
    $err = Get-Content $ERR_FILE -Raw -ErrorAction SilentlyContinue
    if ($err -and $err.Trim()) {
      Write-StatusLine 'stderr' 'NON-EMPTY (see file)' 'Yellow'
    } else { Write-StatusLine 'stderr' 'empty' 'DarkGray' }
  }
  Write-Host ''
  return $listening
}

switch ($Action) {

  'start' {
    if (Test-Listening -OnPort $Port) {
      Write-Host ''
      Write-Host "  Already listening on $Port - not starting a second." -ForegroundColor Yellow
      Write-Host "  http://127.0.0.1:$Port/" -ForegroundColor White
      Write-Host ''
      exit 0
    }
    # Clear a pid file left by a process that died, so status cannot lie later.
    if (Test-Path $PID_FILE) { Remove-Item $PID_FILE -Force }

    Write-Host ''
    Write-Host '  Starting SENTINEL Command Center...' -ForegroundColor Cyan
    # -NoBrowser: opening a browser from an agent shell is how the previous
    # launches littered windows. The URL is printed instead.
    $argList = @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File',
                 (Join-Path $API 'server.ps1'), '-Port', $Port, '-NoBrowser')
    $proc = Start-Process -FilePath 'powershell' -ArgumentList $argList `
      -WindowStyle Hidden -PassThru `
      -RedirectStandardOutput $LOG_FILE -RedirectStandardError $ERR_FILE
    $childId = $proc.Id
    # Release the .NET Process object and the handles it cached. With
    # -RedirectStandardOutput the object owns streams tied to a child that is
    # still running, and PowerShell's exit sequence blocks on them - so the
    # server came up correctly and the launcher still hung forever. The pid is
    # taken first because Dispose() makes the object unusable.
    try { $proc.Dispose() } catch { }
    $childId | Out-File -FilePath $PID_FILE -Encoding ascii -Force

    $deadline = (Get-Date).AddSeconds($WaitSeconds)
    $up = $false
    $childExited = $false
    while ((Get-Date) -lt $deadline) {
      Start-Sleep -Milliseconds 500
      if (Test-Listening -OnPort $Port) { $up = $true; break }
      # Record liveness but DO NOT break on it. This server collects state
      # before it binds, which takes ~13 s; an early "the child pid is gone"
      # break reported a slow-but-healthy start as FAILED while the port was in
      # fact answering a second later. The port is the evidence, and a pid check
      # must not be able to contradict it. If the server really is dead we wait
      # out the deadline and report stderr, which is the real diagnosis.
      if (-not (Get-Process -Id $childId -ErrorAction SilentlyContinue)) {
        $childExited = $true
      }
    }
    if ($up) {
      Write-Host "  UP   http://127.0.0.1:$Port/   (pid $childId)" -ForegroundColor Green
      Write-Host ''
      exit 0
    }
    # Distinguish a process that DIED from one that is merely SLOW. Both fail
    # this script's own bound, but they are different facts, and calling the
    # second one "FAILED" in red is a claim this script did not measure: the
    # orchestrator polls longer and brings the same process up a few seconds
    # later. A 3-cycle run printed "FAILED to come up" above a cycle that then
    # passed every single check.
    if ($childExited) {
      Write-Host "  FAILED to come up within $WaitSeconds s (pid $childId; the server process exited)." -ForegroundColor Red
    } else {
      Write-Host "  not up within $WaitSeconds s (pid $childId; still starting, NOT failed - the caller may keep waiting)." -ForegroundColor Yellow
    }
    if (Test-Path $ERR_FILE) {
      $e = (Get-Content $ERR_FILE -Raw -ErrorAction SilentlyContinue)
      if ($e -and $e.Trim()) {
        Write-Host '  --- stderr ---' -ForegroundColor Red
        Write-Host $e
      }
    }
    exit 1
  }

  'stop' {
    $procs = @(Get-ServerProcess)
    if ($procs.Count -eq 0) {
      Write-Host '  No server process found.' -ForegroundColor DarkGray
      if (Test-Path $PID_FILE) { Remove-Item $PID_FILE -Force }
      exit 0
    }
    foreach ($p in $procs) {
      # try/catch/else is not valid PowerShell - `else` binds to `if`, never to
      # `catch`. The original version used it, which made `stop` and `restart`
      # fail while `start` and `status` worked, because the bad statement sat
      # in a branch those two never entered. The file parses, so a
      # syntax-level audit of the whole script would not have found it either:
      # only running every verb does.
      $stopped = $false
      try {
        Stop-Process -Id $p.ProcessId -Force -ErrorAction Stop
        $stopped = $true
      } catch {
        $stopped = $false
      }
      if ($stopped) { Write-Host "  stopped pid $($p.ProcessId)" -ForegroundColor Green }
      else { Write-Host "  could not stop pid $($p.ProcessId)" -ForegroundColor Yellow }
    }
    if (Test-Path $PID_FILE) { Remove-Item $PID_FILE -Force }
    exit 0
  }

  'restart' {
    & $PSCommandPath -Action stop -Port $Port
    Start-Sleep -Seconds 1
    & $PSCommandPath -Action start -Port $Port -NoBrowser:$NoBrowser
    exit $LASTEXITCODE
  }

  'status' {
    $up = Show-Status
    if ($up) { exit 0 } else { exit 1 }
  }

  'install-task' {
    # A scheduled task is started by the Task Scheduler service, so the server
    # is NOT a descendant of any agent shell and cannot be killed by one. This
    # is the only construction here that survives the process tree dying.
    Write-Host ''
    Write-Host '  This registers a per-user scheduled task that starts the' -ForegroundColor Cyan
    Write-Host '  Command Center at logon. It is reversible:' -ForegroundColor Cyan
    Write-Host "    schtasks /delete /tn $TASK_NAME /f" -ForegroundColor DarkGray
    Write-Host ''
    $target = Join-Path $PSCommandPath '-Action start -Port 8910'
    schtasks /create /tn $TASK_NAME /tr $target /sc onlogon /rl limited /f | Out-Host
    if ($LASTEXITCODE -eq 0) {
      Write-Host "  Registered: $TASK_NAME" -ForegroundColor Green
      exit 0
    }
    Write-Host "  schtasks failed (exit $LASTEXITCODE)" -ForegroundColor Red
    exit 1
  }

  'uninstall-task' {
    schtasks /delete /tn $TASK_NAME /f 2>&1 | Out-Host
    exit $LASTEXITCODE
  }
}
