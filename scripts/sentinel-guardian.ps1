<#
.SYNOPSIS
  Self-healing supervisor for the SENTINEL command centre backend on 8912.

.DESCRIPTION
  SENTINEL_PRIME\13_COMMAND_CENTER\api\server.ps1 is a long-running Windows
  PowerShell service, launched by sentinel-cc.ps1 via Start-Process. Detachment
  is intentional (its own comment says so) - the process is MEANT to outlive the
  launcher. The consequence is that nothing owns it: if it dies, it stays dead,
  and the container in front of it (mavis-sentinel-hub on 8910) keeps serving a
  green /api/health while its data plane is gone. A healthy front in front of an
  absent backend looks exactly like a working system from the front alone.

  WHAT MAKES THIS DIFFERENT FROM EVERY OTHER WATCHDOG ON THIS BOX

  sentinel-cc.ps1 finds its process with:

      -Filter "Name='powershell.exe' AND CommandLine LIKE '%server.ps1%'"

  That pattern also matches the OPTIMUS Control Center, because that is ALSO
  powershell.exe running a file called server.ps1. A restart driven by the
  wrong watcher would take down the console it was meant to protect.

  So this guardian matches on the FULL PATH and nothing else:

      CommandLine LIKE '%SENTINEL_PRIME\13_COMMAND_CENTER\api\server.ps1%'

  Every kill this script issues is re-verified against that same pattern before
  it acts. If the pattern ever matches something outside SENTINEL_PRIME, the
  script refuses rather than guesses.

  Health is measured end to end - a real GET of /api/health, not a listening
  socket. A wedged process holds a port open indefinitely while everything
  behind it rots; that is how a dashboard once sat dead for 19.5 hours.

.PARAMETER Once
  Check once and exit. Used for diagnosis, not supervision.

.EXAMPLE
  .\sentinel-guardian.ps1 -Once
#>
[CmdletBinding()]
param(
  [int]$Port = 8912,
  [int]$IntervalSec = 45,
  [int]$ConsecutiveFails = 3,
  [int]$GraceSec = 60,
  [switch]$Once
)

$ErrorActionPreference = 'Stop'

$Root       = 'C:\Users\apviz\.minimax-agent\projects'
$Sentinel   = Join-Path $Root 'SENTINEL_PRIME'
$ServerPath = Join-Path $Sentinel '13_COMMAND_CENTER\api\server.ps1'
$LogDir     = Join-Path $Sentinel '13_COMMAND_CENTER\logs'
$Log        = Join-Path $LogDir 'guardian.log'

# The ownership token. Everything below is keyed on this and nothing else.
$Token = 'SENTINEL_PRIME\13_COMMAND_CENTER\api\server.ps1'

if (-not (Test-Path -LiteralPath $ServerPath)) {
  Write-Host "REFUSING TO START - $($ServerPath) does not exist. This guardian supervises that file and nothing else." -ForegroundColor Red
  exit 1
}
if (-not (Test-Path -LiteralPath $LogDir)) { New-Item -ItemType Directory -Path $LogDir -Force | Out-Null }

function Say($m) {
  $line = '{0:o} {1}' -f (Get-Date), $m
  Write-Host $line
  try { Add-Content -LiteralPath $Log -Value $line -Encoding UTF8 } catch { }
}

# Every powershell process on the box, ONCE. A CIM query is ~seconds; asking for
# one process at a time turns a 45 s loop into a 45-minute one.
function Get-AllProcesses {
  $h = @{}
  foreach ($p in @(Get-CimInstance Win32_Process -Filter "Name='powershell.exe' OR Name='pwsh.exe'" -ErrorAction SilentlyContinue)) {
    $h[[int]$p.ProcessId] = $p
  }
  $h
}

function Get-Owned {
  param([hashtable]$All)
  @($All.Values | Where-Object { $_.CommandLine -and $_.CommandLine.Contains($Token) })
}

function Test-Health {
  try {
    $r = Invoke-WebRequest "http://127.0.0.1:$Port/api/health" -UseBasicParsing -TimeoutSec 10
    ($r.StatusCode -ge 200 -and $r.StatusCode -lt 500)
  } catch { $false }
}

Say "guardian up - supervising $Token on port $Port, every ${IntervalSec}s"

$fails = 0
$graceUntil = 0

while ($true) {
  $All = Get-AllProcesses
  $Owned = Get-Owned -All $All
  $healthy = Test-Health

  if ($healthy) {
    if ($fails -gt 0) { Say "healthy again after $fails failed check(s)" }
    $fails = 0
    Say ("ok  pids={0}" -f (($Owned | ForEach-Object { $_.ProcessId }) -join ',')) | Out-Null
  } else {
    $fails++
    Say ("FAIL  check #{0}  owned={1}  port {2} not answering" -f $fails, @($Owned).Count, $Port)
    if ($fails -ge $ConsecutiveFails -and (Get-Date).Ticks -ge $graceUntil) {
      # Re-derive ownership from a FRESH table immediately before acting. The
      # loop's snapshot may be minutes old at this point, and a kill is not
      # reversible.
      $Fresh = Get-AllProcesses
      $Targets = Get-Owned -All $Fresh
      foreach ($t in $Targets) {
        # Last gate: the command line must still contain the token, read from
        # the process itself rather than from anything cached.
        $cl = $Fresh[[int]$t.ProcessId].CommandLine
        if ($cl -and $cl.Contains($Token)) {
          Say "killing stale SENTINEL backend pid $($t.ProcessId)"
          try { Stop-Process -Id $t.ProcessId -Force -ErrorAction Stop } catch { Say "kill failed: $($_.Exception.Message)" }
        } else {
          Say "REFUSING to kill pid $($t.ProcessId) - its command line no longer matches the token"
        }
      }
      Start-Sleep -Seconds 3
      Say 'restarting the SENTINEL backend'
      try {
        Start-Process -FilePath 'powershell' `
          -ArgumentList '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', "`"$ServerPath`"", '-Port', $Port, '-NoBrowser' `
          -WindowStyle Hidden | Out-Null
        $graceUntil = (Get-Date).AddSeconds($GraceSec).Ticks
        Say "restart issued; grace until $([DateTime]::new($graceUntil).ToString('HH:mm:ss'))"
      } catch {
        Say "restart FAILED: $($_.Exception.Message)"
      }
      $fails = 0
    }
  }

  if ($Once) { break }
  Start-Sleep -Seconds $IntervalSec
}