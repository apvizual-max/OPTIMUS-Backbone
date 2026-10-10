<#
.SYNOPSIS
  Self-healing supervisor for the OPTIMUS Control Center.

.DESCRIPTION
  The Control Center was started by hand in a console window. Nothing owned it.
  When that process ended - a closed window, a crash, a logoff - port 8900 went
  dead and stayed dead. On 2026-10-04 the state file was found 19.5 hours stale
  with a single line in the log and no indication of why.

  This is the component that makes the product survive. It answers one
  question on a timer: is the dashboard actually serving, and is what it
  serves actually fresh? A listening socket is not proof - a wedged process
  keeps the port open while the state behind it rots - so health is measured
  end to end, and a failure restarts the thing.

  It also writes cc-health.json, which the dashboard renders as its own
  "Resilience" tab. The system reports on itself instead of asking to be
  checked.

.PARAMETER Port
  The port the Control Center binds. Default 8900.

.PARAMETER IntervalSec
  How often to check. Default 30.

.PARAMETER MaxStateAgeSec
  How old the served state may be before the server counts as unhealthy. A
  collect takes 10-20s and refreshes on a 20s cycle, so 5 minutes is generous
  enough to absorb one slow collect and tight enough to catch a dead refresher.

.PARAMETER Once
  Check a single time and exit. Used for diagnosis, not supervision.

.EXAMPLE
  .\cc-watchdog.ps1
.EXAMPLE
  .\cc-watchdog.ps1 -Once
#>
[CmdletBinding()]
param(
  [int]$Port = 8900,
  [int]$IntervalSec = 30,
  [int]$MaxStateAgeSec = 300,
  [int]$ConsecutiveFails = 3,
  [int]$GraceSec = 150,
  [switch]$Once
)

$ErrorActionPreference = 'Stop'

$Root     = 'C:\Users\apviz\.minimax-agent\projects'
$CC       = Join-Path $Root '90_CONTROL_CENTER'
$Server   = Join-Path $CC 'api\server.ps1'
$LogDir   = Join-Path $CC 'logs'
$StateF   = Join-Path $CC 'api\live-state.json'
$HealthF  = Join-Path $CC 'api\cc-health.json'
$OutLog   = Join-Path $LogDir 'server.out.log'
$ErrLog   = Join-Path $LogDir 'server.err.log'
$WatchLog = Join-Path $LogDir 'watchdog.log'

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

function Write-Watch([string]$m, [string]$lvl = 'INFO') {
  $line = '{0:o} [{1}] {2}' -f (Get-Date), $lvl, $m
  try { Add-Content -LiteralPath $WatchLog -Value $line -Encoding UTF8 } catch { }
  Write-Host $line
}

# The test a listening socket cannot pass on its own: can the server actually
# produce a FRESH state? A wedged process holds the port open indefinitely.
function Test-Health {
  try {
    $c = New-Object Net.Sockets.TcpClient
    $iar = $c.BeginConnect('127.0.0.1', $Port, $null, $null)
    if (-not $iar.AsyncWaitHandle.WaitOne(3000)) { $c.Close(); return @{ ok = $false; why = 'port not accepting connections' } }
    $c.EndConnect($iar); $c.Close()

    # Generous, because /api/state can block behind an inline collect that
    # itself takes 10-20s. A 20s client timeout produced a FALSE POSITIVE once:
    # the server was alive and healthy, mid-collect, and the watchdog killed it
    # and restarted it for no reason. A watchdog that cries wolf is worse than
    # no watchdog, because it destroys the thing it is protecting.
    $r = Invoke-WebRequest -Uri "http://127.0.0.1:$Port/api/state" -UseBasicParsing -TimeoutSec 60
    if ($r.StatusCode -ne 200) { return @{ ok = $false; why = "api returned HTTP $($r.StatusCode)" } }

    $j = $r.Content | ConvertFrom-Json
    $age = [math]::Round(((Get-Date) - [datetime]$j.generated).TotalSeconds, 1)
    if ($age -gt $MaxStateAgeSec) {
      return @{ ok = $false; why = "served state is $([math]::Round($age/60,1)) min old (limit $([math]::Round($MaxStateAgeSec/60,1)) min) - the refresher is wedged" }
    }
    return @{ ok = $true; why = ''; age = $age; state = $j }
  } catch {
    return @{ ok = $false; why = $_.Exception.Message }
  }
}

function Stop-Stale {
  $stopped = 0
  # SCOPED TO THE SERVER THIS WATCHDOG OWNS. The original filter was
  # `CommandLine -like '*server.ps1*'`, which matched EVERY PowerShell running
  # any server.ps1 anywhere on the machine.
  #
  # That was not theoretical. On 2026-10-05 03:03 this watchdog restarted the
  # 8900 server for a legitimate reason - the refresher had stopped writing - and
  # in the same breath killed the SENTINEL_PRIME server on port 8910, which it
  # does not supervise and does not restart. Nothing else brings that one back,
  # so it simply stayed dead until it was noticed. The log line for the restart
  # reads "cleared 2 stale process(es)", which is the whole problem in six
  # words: ONE of those was not stale, and was not ours.
  #
  # The fix is not a narrower heuristic, it is the thing the function always
  # meant: kill the server THIS watchdog started, and nothing else. $Server is
  # the exact path passed to Start-Server below, so the match is precise rather
  # than approximate - a sibling server in another project has a different path
  # and cannot match it.
  $owned = [IO.Path]::GetFullPath($Server)
  Get-CimInstance Win32_Process -Filter "Name='powershell.exe' OR Name='pwsh.exe'" -ErrorAction SilentlyContinue |
    Where-Object { $_.CommandLine -and $_.CommandLine -like "*$owned*" } |
    ForEach-Object {
      if ($_.ProcessId -ne $PID) {
        try { Stop-Process -Id $_.ProcessId -Force -ErrorAction Stop; $stopped++ } catch { }
      }
    }
  return $stopped
}

function Start-Server {
  Write-Watch "starting the server on port $Port" 'ACTION'
  $p = Start-Process -FilePath 'powershell.exe' `
    -ArgumentList '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', "`"$Server`"", '-Port', $Port, '-NoBrowser' `
    -RedirectStandardOutput $OutLog -RedirectStandardError $ErrLog -WindowStyle Hidden -PassThru
  return $p.Id
}

# health.json is what the dashboard's Resilience tab renders. It is written on
# every pass, so the tab shows the supervisor's own current verdict rather than
# a snapshot of when it last felt like checking.
function Write-Health($h, $extra) {
  $o = [ordered]@{
    generated            = (Get-Date).ToString('o')
    healthy              = [bool]$h.ok
    reason               = $h.why
    port                 = $Port
    state_age_sec        = $(if ($null -ne $h.age) { $h.age } else { $null })
    max_state_age_sec    = $MaxStateAgeSec
    interval_sec         = $IntervalSec
    watchdog_pid         = $PID
    watchdog_started     = $script:Started.ToString('o')
    restarts             = $script:Restarts
    last_restart         = $script:LastRestart
    last_restart_reason  = $script:LastReason
    chrome_started_us    = $script:ChromeStart
    next_check           = (Get-Date).AddSeconds($IntervalSec).ToString('o')
  }
  foreach ($k in $extra.Keys) { $o[$k] = $extra[$k] }
  $tmp = "$HealthF.$PID.tmp"
  try {
    [IO.File]::WriteAllText($tmp, ($o | ConvertTo-Json -Depth 4), (New-Object Text.UTF8Encoding($false)))
    try { [IO.File]::Replace($tmp, $HealthF, $null, $true) } catch { Move-Item -LiteralPath $tmp -Destination $HealthF -Force }
  } catch { }
}

function Test-PageIntegrity {
  # The API being healthy says nothing about the PAGE being renderable. A
  # JavaScript parse error leaves /api/state serving perfectly while the console
  # shows a dead skeleton, the response is 200, and the console log is empty
  # because no statement ever ran. That combination is invisible to Test-Health
  # and it is exactly what happened on 2026-10-04.
  #
  # So the supervisor also parses the served page. Cheap, and it turns the
  # worst failure mode from silent into a line in the log.
  $idx = Join-Path (Split-Path $PSScriptRoot -Parent) '90_CONTROL_CENTER\index.html'
  try {
    if (-not (Test-Path $idx)) { return @{ ok = $false; why = 'index.html is missing' } }
    $html = [IO.File]::ReadAllText($idx, [Text.Encoding]::UTF8)
    $m = [regex]::Match($html, '(?s)<script>(.*?)</script>')
    $blocks = [regex]::Matches($html, '(?s)<script>(.*?)</script>')
    $js = $null
    foreach ($b in $blocks) { if ($b.Groups[1].Value.Trim().Length -gt 500) { $js = $b.Groups[1].Value } }
    if (-not $js) { return @{ ok = $false; why = 'no inline script block found' } }
    $tmp = [IO.Path]::GetTempFileName() + '.js'
    [IO.File]::WriteAllText($tmp, $js, (New-Object Text.UTF8Encoding($false)))
    # Windows PowerShell 5.1 promotes a native command's STDERR to a TERMINATING
    # error whenever $ErrorActionPreference is 'Stop'. node --check reports every
    # syntax error on stderr, so this call THREW on precisely the input the
    # function exists to detect: the `if ($rc -ne 0)` branch below was
    # unreachable, and the outer catch reported a TEMP PATH that the very next
    # line deletes. It said "tmpDE13.tmp.js:413" instead of naming index.html.
    # Drop to Continue for the call, take the verdict from the exit code, and
    # relabel the temp path so the operator gets a line they can actually open.
    $nodeOut = @()
    $prevEA = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try { $nodeOut = & node --check $tmp 2>&1 } finally { $ErrorActionPreference = $prevEA }
    $rc = $LASTEXITCODE
    # The line number is relative to the EXTRACTED script, not to index.html.
    # Saying otherwise would send the reader to the wrong line of a 1900-line file.
    $detail = (@($nodeOut) | ForEach-Object { [string]$_ } |
               Where-Object { $_ -and $_ -notmatch 'RemoteException' } |
               Select-Object -First 1) -replace [regex]::Escape($tmp), 'index.html <inline script>'
    try { [IO.File]::Delete($tmp) } catch { }
    if ($rc -ne 0) {
      $why = 'index.html inline script does not parse - the page will render nothing'
      if ($detail) { $why += " | $detail" }
      return @{ ok = $false; why = $why }
    }
    $moji = ([regex]::Matches($html, '[' + [char]0x00E2 + [char]0x00C2 + [char]0x00C3 + [char]0x00EF + ']')).Count
    if ($moji -gt 0) { return @{ ok = $false; why = "$moji mojibake character(s) in index.html" } }
    return @{ ok = $true; why = ''; bytes = $html.Length }
  } catch {
    return @{ ok = $false; why = "page check failed: $($_.Exception.Message)" }
  }
}

$script:Started   = Get-Date
$script:Restarts  = 0
$script:LastRestart = $null
$script:LastReason  = $null
$script:WasHealthy = $null
$script:GraceUntil = $null
$script:Fails = 0
$script:ChromeStart = $null
# Detect a browser LAUNCH (no chrome -> chrome), not merely "chrome exists".
#
# This used to be a one-shot latch ($SawChrome) plus a startup-time guard
# ($ChromeWasRunningAtStart). Both are per-process and permanent, and together
# they meant the hook could fire at most ONCE in the supervisor's whole life -
# and not at all if a browser happened to be open when the supervisor started.
# At every logon a browser is open, so in practice it never fired. The
# requirement is "as soon as I start my browser", which recurs every time he
# opens one; a once-forever flag cannot express that.
#
# Seed from the CURRENT state so the supervisor's own start never looks like a
# launch, then compare each tick: a rising edge is the user opening a browser.
$script:ChromePrev = (@(Get-Process chrome -ErrorAction SilentlyContinue).Count -gt 0)
$script:ChromeOpens = 0

Write-Watch "watchdog up on port $Port, checking every ${IntervalSec}s" 'START'

do {
  # ---------------------------------------------------------------- CHROME --
  # He asked: "as soon as I start my browser, I want this to load, whether or
  # not my index is open or whatever." So it opens. I had previously narrowed
  # this to fire only when the console was already down, on the reasoning that
  # a tab on every browser launch is intrusive. That was me substituting my
  # judgement for an explicit instruction, which is the same mistake as
  # proposing a change to a system I was told to leave alone.
  #
  # Guard: once per Chrome session, and only when Chrome was not already running
  # when this supervisor started - otherwise the supervisor's own start would
  # immediately pop a tab on a browser he did not just launch.
  $chromeNow = (@(Get-Process chrome -ErrorAction SilentlyContinue).Count -gt 0)
  if ($chromeNow -and -not $script:ChromePrev) {
    $script:ChromeOpens++
    $live = Test-Health
    if (-not $live.ok) {
      Write-Watch "chrome opened onto a dead console - starting it first" 'ACTION'
      [void](Stop-Stale)
      $cp = Start-Server
      $script:ChromeStart = (Get-Date).ToString('o')
      Write-Health @{ ok = $false; why = 'started on Chrome launch'; age = $null } `
                  @{ chrome_triggered_start = $true; chrome_start_pid = $cp; chrome_opens = $script:ChromeOpens }
      Start-Sleep -Seconds 25
    } else {
      Write-Watch "chrome opened - showing the console (launch #$($script:ChromeOpens))" 'ACTION'
      $script:ChromeStart = (Get-Date).ToString('o')
      Write-Health $live @{ chrome_opened_console = $true; chrome_opens = $script:ChromeOpens }
    }
    $after = Test-Health
    if ($after.ok) {
      try { Start-Process "http://127.0.0.1:$Port/" } catch {
        Write-Watch "could not open the browser: $($_.Exception.Message)" 'WARN'
      }
    }
  }
  $script:ChromePrev = $chromeNow

  # After a restart, do not judge the new process until it has had time to bind
  # and complete its first collect. Checking earlier reads a healthy server's
  # startup as a failure, and a watchdog that restarts a healthy process is
  # destroying the thing it exists to protect.
  if ($null -ne $script:GraceUntil -and (Get-Date) -lt $script:GraceUntil) {
    if ($Once) { break }
    Start-Sleep -Seconds 5
    continue
  }

  $h = Test-Health

  if ($h.ok) {
    $script:Fails = 0
    if ($script:WasHealthy -ne $true) { Write-Watch "healthy - state $([math]::Round($h.age,1))s old" 'OK' }
    $script:WasHealthy = $true
    # second opinion: the API can be perfect while the page is dead
    $pg = Test-PageIntegrity
    if (-not $pg.ok) {
      # A broken page is NOT a reason to restart the server - the server is
      # fine and restarting would hide the real defect. Say it, loudly, and
      # keep the console serving so the operator can see what happened.
      Write-Watch "PAGE BROKEN: $($pg.why)" 'FAIL'
    }
    $extra = @{ page_ok = $pg.ok; page_reason = $pg.why }
    Write-Health $h $extra
  } else {
    $script:Fails++
    if ($script:Fails -lt $ConsecutiveFails) {
      # ONE slow check is not a dead server. A collect touches docker inspect for
      # 56 containers, two bridge doctors and two mcode-tools calls; under any
      # contention that can exceed a minute. Restarting on the first bad sample
      # produced a restart loop that killed a server which was merely slow, and
      # each kill spawned the next collect, which slowed the next one further.
      Write-Watch "unhealthy check $($script:Fails)/$ConsecutiveFails (not acting yet): $($h.why)" 'WARN'
      Write-Health @{ ok = $false; why = $h.why; age = $null } @{ consecutive_failures = $script:Fails }
      if ($Once) { break }
      Start-Sleep -Seconds $IntervalSec
      continue
    }

    if ($script:WasHealthy -ne $false) { Write-Watch "UNHEALTHY: $($h.why)" 'FAIL' }
    $script:WasHealthy = $false
    $killed = Stop-Stale
    $pid2 = Start-Server
    $script:Restarts++
    $script:LastRestart = (Get-Date).ToString('o')
    $script:LastReason  = $h.why
    Write-Watch "restarted as pid $pid2 (cleared $killed stale process(es)) because: $($h.why)" 'ACTION'
    $script:GraceUntil = (Get-Date).AddSeconds($GraceSec)
    $script:Fails = 0
    Write-Health @{ ok = $false; why = "restarting: $($h.why)"; age = $null } @{ restart_pending = $true }
    if ($Once) { break }
    Start-Sleep -Seconds 30
  }

  if ($Once) { break }
  Start-Sleep -Seconds $IntervalSec
} while ($true)
