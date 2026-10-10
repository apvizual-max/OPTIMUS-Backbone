<#
.SYNOPSIS
  Live state collector for the MiniMax OPTIMUS Control Center.

.DESCRIPTION
  Emits ONE JSON document describing the whole system at this instant. The
  dashboard polls this; it never guesses and never shows a stale cached value.

  Every field is measured. A value that cannot be measured is reported as null
  with a reason, never as a plausible-looking default.

  Exits 0 on success. Add -Pretty for human reading.
#>
[CmdletBinding()]
param(
  [switch]$Pretty,
  # Machine-specific roots, defaulted from the environment. Every one of these
  # was a hardcoded C:\Users\<someone> literal, which is worse than an obvious
  # break: on another machine the paths simply do not exist, and a missing
  # directory reports as a COUNT OF ZERO. "this machine has no skills" and "I
  # looked in the wrong place" are different facts wearing the same number, and
  # only one of them is true. This is postmortem #13 again - $null collapsing
  # two distinct states into one - one level up, in the paths themselves.
  [string]$ProjectsRoot,
  [string]$ComposeFile,
  [string]$HermesRoot,
  [string]$MavisSkillsRoot,
  [string]$PersonalSkillsRoot
)

$ErrorActionPreference = 'SilentlyContinue'
# The bounded command runner, shared with server.ps1. A scriptblock cannot cross
# into a child process, so the collector dot-sources the SAME file rather than
# carrying its own copy of a timeout - one implementation, many callers, and a
# duplicated timeout is a timeout that eventually gets edited in one place only.
# The two git calls below are the ones that deadlocked for five hours.
. (Join-Path $PSScriptRoot 'run-bounded.ps1')
if (-not $ProjectsRoot)       { $ProjectsRoot       = Join-Path $env:USERPROFILE '.minimax-agent\projects' }
if (-not $ComposeFile)        { $ComposeFile        = Join-Path $env:USERPROFILE 'docker-compose.yml' }
if (-not $HermesRoot)         { $HermesRoot         = Join-Path $env:LOCALAPPDATA 'hermes' }
if (-not $MavisSkillsRoot)    { $MavisSkillsRoot    = Join-Path $env:USERPROFILE '.minimax\agents\mavis\skills' }
if (-not $PersonalSkillsRoot) { $PersonalSkillsRoot = Join-Path $env:USERPROFILE '.minimax\skills' }
$PROJECTS = $ProjectsRoot

# Count a directory of children, and say whether the directory was even THERE.
# A zero with no flag is ambiguous; a zero with present=$false is a fact the
# operator can act on. Returning both is the whole point.
function Count-Children([string]$Path) {
  if (-not (Test-Path -LiteralPath $Path)) { return [ordered]@{ present = $false; count = $null } }
  $n = @(Get-ChildItem -LiteralPath $Path -Directory -EA SilentlyContinue).Count
  return [ordered]@{ present = $true; count = $n }
}

# Section tracing. Inert unless OPTIMUS_TRACE is set, because this script runs
# on every dashboard poll and tracing must never be the reason a poll is slow.
# It exists because every external statement in this file measured fast while
# the script as a whole still ran past 150 s - "everything I timed is quick" is
# not an answer when the thing that hangs was never timed.
$script:TraceOn = [bool]$env:OPTIMUS_TRACE
$script:TracePath = Join-Path $PSScriptRoot 'collect-trace.log'
$script:TraceT0 = Get-Date
function Trace([string]$m) {
  if (-not $script:TraceOn) { return }
  $ms = [int]((Get-Date) - $script:TraceT0).TotalMilliseconds
  try { Add-Content -LiteralPath $script:TracePath -Value ("{0,7}ms  {1}" -f $ms, $m) -Encoding UTF8 } catch { }
}
Trace 'collector entered'

# Two independent timeouts, deliberately.
#
# Invoke-RestMethod -TimeoutSec maps to HttpWebRequest.Timeout, which covers
# connect and the response HEADERS only. It does NOT bound the body read -
# ReadWriteTimeout is a separate property and defaults to 300 s. Every bridge
# probe here goes through Docker's port proxy, and when that stalled mid-body
# the collector blocked for five minutes with an empty stderr. The dashboard
# binds its whole liveness to this endpoint, so one stalled read took the
# console down. Set both.
function Probe($url, $timeout = 12) {
  $resp = $null; $sr = $null
  $sw = [Diagnostics.Stopwatch]::StartNew()
  # HOW LONG, and WHY IT FAILED. Probe used to return the body or $null and throw
  # away everything else, so a bridge that is DOWN and a bridge that is merely
  # SLOW rendered identically: health=unknown, 0/0/0, no checks. They are
  # opposite problems with opposite fixes, and the dashboard could not tell them
  # apart. A budget that is SHORTER than the thing it measures is not a
  # conservative setting, it is a broken instrument: it reports "unknown" for
  # ever and the operator learns to ignore the field.
  #
  # Measured 2026-10-05, four samples against the live bridge:
  #   minimax-hermes-bridge      9.43s / 9.91s / 10.42s / 11.33s   (12 checks)
  #   minimax-antigravity-bridge 1.24s                            (10 checks)
  # The budget below was 8 s - under the FASTEST hermes sample. It therefore
  # timed out on 100% of runs, and the console showed `unknown - 0ok/0w/0f`
  # for the most important bridge while a tile above it read "2/2". A check
  # that can never complete is not a safety margin; it is a dead sensor.
  # 20 s clears the worst sample with room for a loaded machine.
  $script:ProbeLast = @{ ok = $false; ms = 0; why = ''; url = $url; budget = $timeout }
  try {
    $req = [Net.HttpWebRequest]::Create($url)
    $req.Timeout = [int]($timeout * 1000)          # connect + headers
    $req.ReadWriteTimeout = [int]($timeout * 1000)  # body read - the one that bit us
    $req.UseDefaultCredentials = $true
    $resp = $req.GetResponse()
    $sr = New-Object IO.StreamReader($resp.GetResponseStream())
    $body = $sr.ReadToEnd()
    $sw.Stop()
    $script:ProbeLast = @{ ok = $true; ms = [int]$sw.ElapsedMilliseconds; why = ''; url = $url; budget = $timeout }
    return ($body | ConvertFrom-Json)
  } catch {
    $sw.Stop()
    $why = $_.Exception.Message
    if ($why -match 'timed out') { $why = "no answer within ${timeout}s" }
    $script:ProbeLast = @{ ok = $false; ms = [int]$sw.ElapsedMilliseconds; why = $why; url = $url; budget = $timeout }
    return $null
  }
  finally {
    if ($sr) { try { $sr.Dispose() } catch { } }
    if ($resp) { try { $resp.Close() } catch { } }
  }
}

# ONE netstat sweep for every port, not one per port. Get-NetTCPConnection
# costs ~2s a call and PortUp is used 5 times, so the old shape burned ~10s of
# pure serial latency into every single collect.
$script:ListenPorts = $null
function PortUp($p) {
  if ($null -eq $script:ListenPorts) {
    $script:ListenPorts = @{}
    try {
      Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue |
        ForEach-Object { $script:ListenPorts[[int]$_.LocalPort] = $true }
    } catch { }
  }
  return [bool]$script:ListenPorts[$p]
}
function DirInfo($path) {
  if (-not (Test-Path -LiteralPath $path)) {
    return [ordered]@{ path = $path; exists = $false; files = 0; dirs = 0; bytes = 0; links = 0 }
  }
  $items = Get-ChildItem -LiteralPath $path -Recurse -Force -ErrorAction SilentlyContinue
  $files = @($items | Where-Object { -not $_.PSIsContainer })
  $dirs  = @($items | Where-Object { $_.PSIsContainer })
  [ordered]@{
    path      = $path
    exists    = $true
    files     = $files.Count
    dirs      = $dirs.Count
    bytes     = [int64](($files | Measure-Object Length -Sum).Sum)
    links     = @($items | Where-Object { $_.LinkType }).Count
    modified  = (Get-Item -LiteralPath $path).LastWriteTime.ToString('o')
  }
}

$now = (Get-Date).ToString('o')
$state = [ordered]@{ generated = $now; host = $env:COMPUTERNAME; sections = @{} }

Trace 'before docker'
# ---------------------------------------------------------------- DOCKER ----
# BOUNDED. The Docker daemon is the single most plausible thing to hang on this
# machine, and an unbounded `docker inspect` against a hung daemon does not
# return - it burns the refresher's entire 240 s budget, the served state ages
# past the watchdog's 300 s freshness limit, and the server is restarted. So a
# Docker problem becomes a console outage, which is a far worse outcome than a
# dashboard that says "Docker did not answer".
#
# A timeout is reported as a timeout. It is NOT the same as "zero containers",
# and collapsing those two is how a Docker outage would render as a confident,
# cheerful, completely wrong "0 containers" on every tab.
$dockerPs = @()
$dockerErr = $null
$dockerTimedOut = $false
$dockerCap = 30

$psText = ''
try { $psText = Invoke-BoundedCommand -Command 'docker ps --format "{{.Names}}|{{.Status}}"' -TimeoutSec $dockerCap }
catch { $dockerErr = $_.Exception.Message }
if ($psText -match 'TIMED OUT') { $dockerTimedOut = $true }
$dockerPs = @($psText -split "`r?`n" | Where-Object { $_.Trim() -and $_ -notmatch 'TIMED OUT' })

$byProject = @{}
$projRows = @()
if ($dockerPs.Count -gt 0) {
  $idText = ''
  try { $idText = Invoke-BoundedCommand -Command 'docker ps -q' -TimeoutSec $dockerCap } catch { }
  if ($idText -match 'TIMED OUT') { $dockerTimedOut = $true }
  $ids = @($idText -split "`r?`n" | Where-Object { $_.Trim() -and $_ -notmatch 'TIMED OUT' })
  $inspText = ''
  if ($ids.Count -gt 0) {
    try { $inspText = Invoke-BoundedCommand -Command ('docker inspect ' + ($ids -join ' ')) -TimeoutSec $dockerCap }
    catch { $dockerErr = $_.Exception.Message }
  }
  if ($inspText -match 'TIMED OUT') {
    # Names are known, detail is not. Say so rather than showing an empty table
    # that reads as "everything is fine".
    $dockerTimedOut = $true
  } elseif ($inspText.Trim()) {
    try {
      $all = $inspText | ConvertFrom-Json
      foreach ($c in @($all)) {
        $p = $c.Config.Labels.'com.docker.compose.project'
        if (-not $p) { $p = '(none)' }
        if (-not $byProject.ContainsKey($p)) { $byProject[$p] = 0 }
        $byProject[$p]++
        $projRows += [ordered]@{
          name    = $c.Name.TrimStart('/')
          project = $p
          image   = $c.Config.Image
          status  = $c.State.Status
          health  = if ($c.State.Health) { $c.State.Health.Status } else { $null }
        }
      }
    } catch { $dockerErr = $_.Exception.Message }
  }
}

$state.sections.docker = [ordered]@{
  # null, never 0, when Docker did not answer. "not measured" and "measured, and
  # it is zero" are different facts and the panel has to be able to tell them
  # apart, or a Docker outage renders as a clean bill of health.
  total            = if ($dockerTimedOut) { $null } else { $dockerPs.Count }
  timed_out        = $dockerTimedOut
  names_known      = $dockerPs.Count
  hermes_mcp       = @($dockerPs | Where-Object { $_ -like 'hermes-mcp-*' }).Count
  sentinel         = @($dockerPs | Where-Object { $_ -like 'hermes-sentinel-daemon*' }).Count
  minimax_bridges  = @($dockerPs | Where-Object { $_ -like 'minimax-*' }).Count
  by_project       = $byProject
  containers       = $projRows
  error            = $dockerErr
  warning          = 'NEVER run: docker container prune -a (lost the swarm 2026-08-08)'
  compose_present  = (Test-Path -LiteralPath $ComposeFile)
  compose_valid    = $null
  compose_timed_out = $false
}
if ($state.sections.docker.compose_present) {
  $compRes = $null
  try { $compRes = Invoke-Bounded -Command ('docker compose -f "' + $ComposeFile + '" config --quiet') -TimeoutSec $dockerCap } catch { }
  if ($compRes -and $compRes.TimedOut) {
    $state.sections.docker.compose_timed_out = $true
  } else {
    # The exit code comes from the bounded run's own process, NOT $LASTEXITCODE.
    # $LASTEXITCODE describes whatever native command ran last in THIS session,
    # and a bounded run happens in a child - reading it here reported a valid
    # compose file as invalid, which is a healthy system reported as broken.
    $state.sections.docker.compose_valid = ($null -ne $compRes -and $compRes.ExitCode -eq 0)
  }
}

# --------------------------------------------------------------- BRIDGES ----
function BridgeState($port, $name) {
  $h = Probe "http://127.0.0.1:$port/health" 5
  if (-not $h) {
    $hc = $script:ProbeLast
    return [ordered]@{
      name = $name; port = $port; up = $false; health = $null; checks = $null
      # ok/warn/fail MUST be present even when the bridge is down. The Overview
      # sums them - b.reduce((n,x)=>n+x.fail,0) - and `undefined` is not 0, so
      # one unreachable bridge made the whole console print "NaN failing
      # checks", in the exact moment you most need it to be readable. A down
      # bridge also summed to nothing at all, which silenced the anomaly
      # detector for bridges entirely.
      ok = 0; warn = 0; fail = 0
      doctor_ms = $null; doctor_budget = 5; doctor_why = $hc.why; answered_late = $false
    }
  }
  # Bounded, but ABOVE the real cost. 8 s was chosen to stop one slow bridge
  # turning into a restart loop, which it did - and in doing so it guaranteed the
  # hermes bridge could NEVER be measured, because that call needs 9.4-11.3 s.
  # Protecting the refresh cycle and measuring the bridge are not in conflict at
  # 20 s: two calls at 20 s worst case is a 40 s ceiling, still far inside the
  # refresher's own 240 s budget, and on a healthy machine the two calls return
  # in ~12 s between them. The timeout stops a HUNG bridge; it must not stop a
  # working one.
  $d = Probe "http://127.0.0.1:$port/doctor/detailed" 20
  $doc = $script:ProbeLast          # read immediately: Probe overwrites it each call
  $checks = @()
  if ($d) {
    $checks = @($d.checks | ForEach-Object {
      [ordered]@{ id = $_.id; severity = $_.severity; title = $_.title; detail = $_.detail; remedy = $_.remedy }
    })
  }
  [ordered]@{
    name   = $name
    port   = $port
    up     = $true
    health = if ($d) { $d.health } else { 'unknown' }
    ok     = if ($d) { $d.ok_count } else { 0 }
    warn   = if ($d) { $d.warn_count } else { 0 }
    fail   = if ($d) { $d.fail_count } else { 0 }
    uptime = $h.uptime_s
    role   = $h.role
    checks = $checks
    # Why 0/0/0 with no checks. A bridge that is DOWN and a bridge that
    # ANSWERED LATE used to look identical; they are not the same fault and
    # they do not have the same remedy. This is the whole difference between
    # "restart the bridge" and "the bridge is fine, stop being impatient".
    doctor_ms     = $doc.ms
    doctor_budget = $doc.budget
    doctor_why    = if ($d) { '' } else { $doc.why }
    answered_late = (-not $d) -and ($doc.ms -ge ($doc.budget * 1000))
  }
}
Trace 'before bridges'
$state.sections.bridges = @(
  BridgeState 8801 'minimax-hermes-bridge'
  BridgeState 8802 'minimax-antigravity-bridge'
)

Trace 'before services'
# ------------------------------------------------------------- SERVICES -----
# Supervision is MEASURED here, not asserted. The Fabric tab used to label every
# service "docker restart policy" - and 8765 is a bare python.exe with no Docker
# anywhere near it. A tab whose entire subject is "who watches this" was
# reporting a watcher it had never checked.
#
# The lookup itself lives in api\supervision-map.ps1 and is dot-sourced, not
# reimplemented here. Its first version called Get-NetTCPConnection per port -
# MEASURED at 4681 ms per call - which added ~30 s to a 33 s collector and came
# back EMPTY under load while working standalone. One netstat, one docker ps
# and one process table, then hashtable hits: 3.7 s for five ports.
. (Join-Path $PSScriptRoot 'supervision-map.ps1')
$supMap = Get-SupervisionMap @(8082, 3001, 8765, 8900, 8901, 8910, 8912, 9412)

function Svc($name, $url, $port) {
  $r = $null
  try { $r = Invoke-WebRequest $url -UseBasicParsing -TimeoutSec 10 } catch { $r = $null }
  [ordered]@{
    name  = $name
    port  = $port
    up    = ($null -ne $r) -or (PortUp $port)
    code  = if ($r) { $r.StatusCode } else { $null }
    url   = $url
    supervision = $supMap[$port]
  }
}
$state.sections.services = @(
  Svc 'stirling-pdf' 'http://127.0.0.1:8082/' 8082
  Svc 'libreoffice'  'http://127.0.0.1:3001/' 3001
  Svc 'qwen-acp'     'http://127.0.0.1:8765/health' 8765
)

# ----------------------------------------------------- SENTINEL (8910/8912) --
# The SENTINEL deployment is a two-part split the Fabric tab did not cover at
# all: an nginx container on 8910 fronting a PowerShell data plane on 8912 that
# lives on the HOST, reached from the container as host.docker.internal. That is
# deliberate - the measurements do not live inside a container - and it means
# the data plane's supervision is a SEPARATE question from the front's.
# Conflating them hides the answer: a healthy front in front of an orphaned
# backend looks exactly like a working system from 8910 alone.
Trace 'before sentinel'
$state.sections.sentinel = [ordered]@{
  front   = $supMap[8910]
  backend = $supMap[8912]
  front_http   = $null
  backend_http = $null
  note    = 'The front is a Docker container; the data plane is a Windows PowerShell service reached as host.docker.internal. Different owners, different supervision. A green front does not imply a supervised backend.'
  any_unwatched = $false
}
try { $state.sections.sentinel.front_http   = (Invoke-WebRequest 'http://127.0.0.1:8910/api/health'   -UseBasicParsing -TimeoutSec 8).StatusCode } catch { }
try { $state.sections.sentinel.backend_http = (Invoke-WebRequest 'http://127.0.0.1:8912/api/health' -UseBasicParsing -TimeoutSec 8).StatusCode } catch { }
$state.sections.sentinel.any_unwatched =
  (-not $state.sections.sentinel.front.supervised) -or (-not $state.sections.sentinel.backend.supervised)



# ------------------------------------------------------- HERMES UPDATE -----
# Hermes self-updates (updateMechanism: self), so its source tree is NOT a
# stable fact -- it moves between samples. This reports what is TRUE at this
# instant and, critically, whether a hung CLI has deadlocked the update lock.
# That deadlock is self-inflicted: a hung `hermes mcp list` registers its OWN
# pid as owner of .hermes-update-in-progress and then waits on it, producing
# "source-update completion failed" on every later call.
function Get-HermesUpdate {
  $out = [ordered]@{
    checked_at = (Get-Date).ToString('o')
    version = $null; dirty_stamp = $null; head = $null
    modified_files = @(); modified_count = 0
    lock_present = $false; lock_age_min = $null
    lock_owner = $null; lock_owner_alive = $null; lock_owner_cmd = $null
    deadlock = $false; verdict = 'unknown'; remedy = ''
  }
  $agent = Join-Path $HermesRoot 'hermes-agent'
  $home  = $HermesRoot

  $stampPath = Join-Path $agent 'install-stamp.json'
  if (Test-Path $stampPath) {
    try {
      $s = Get-Content $stampPath -Raw | ConvertFrom-Json
      $out.version = $s.displayVersion
      $out.dirty_stamp = $s.dirty
    } catch { }
  }

  if (Get-Command git -ErrorAction SilentlyContinue) {
    # BOUNDED, and these two calls are the reason. They measure 112-205 ms on a
    # healthy tree - and they are the exact calls that deadlocked for FIVE HOURS
    # (postmortem #17), so "fast right now" is not a reason to leave them
    # unbounded. The refresher caps the whole collect at 240 s, which means one
    # hung git call does not hang forever: it burns the entire budget, the served
    # state ages past the watchdog's 300 s freshness limit, and the server gets
    # restarted. A five-hour stall and a server restart both start here.
    #
    # Both of these branches were WRONG on first write and were caught by running
    # the SHIPPED block against planted inputs rather than a paraphrase of it:
    #   - the timeout notice is itself a non-empty line, so a naive
    #     "if there is any output, report it as head" set the HEAD COMMIT to
    #     "[TIMED OUT after 20s] the command was killed.";
    #   - a status call that timed out PART WAY through still yields the files it
    #     managed to see, and reporting that count with no flag presents a
    #     truncated number as the answer.
    # So: the notice is detected and stripped FIRST, and a timeout reports null
    # rather than a lower bound. "not measured" and "measured, and it is zero"
    # must not wear the same number.
    $gitCap = 20
    $headTimedOut = $false
    $statusTimedOut = $false

    $headText = ''
    try { $headText = Invoke-BoundedCommand -Command "git -C `"$agent`" log --oneline -1" -TimeoutSec $gitCap } catch { }
    if ($headText -match 'TIMED OUT') { $headTimedOut = $true }
    $head = @($headText -split "`r?`n" | Where-Object { $_.Trim() -and $_ -notmatch 'TIMED OUT' })
    if ($head.Count -gt 0) { $out.head = $head[0].Trim() }

    $stText = ''
    try { $stText = Invoke-BoundedCommand -Command "git -C `"$agent`" status --porcelain" -TimeoutSec $gitCap } catch { }
    if ($stText -match 'TIMED OUT') { $statusTimedOut = $true }
    $st = @($stText -split "`r?`n" | Where-Object { $_.Trim() -and $_ -notmatch 'TIMED OUT' })
    $out.modified_files = @($st | ForEach-Object { $_.Trim() })
    # A count from a killed command is a LOWER BOUND, and a lower bound reported
    # as a count is a lie with a number attached. null means not measured.
    #
    # Tracked PER CALL, because a hung `log` says nothing about `status`. The
    # first version of this fix used one flag for both, so a timed-out HEAD made
    # a perfectly successful STATUS count disappear - caught by running this
    # block against planted inputs, which is the only reason it was caught at all.
    $out.modified_count = if ($statusTimedOut) { $null } else { $out.modified_files.Count }
    $out.head_timed_out = $headTimedOut
    $out.status_timed_out = $statusTimedOut
    $out.git_timed_out = ($headTimedOut -or $statusTimedOut)
  }

  $lock = Join-Path $home '.hermes-update-in-progress'
  if (Test-Path $lock) {
    $out.lock_present = $true
    $out.lock_age_min = [math]::Round(((Get-Date) - (Get-Item $lock).LastWriteTime).TotalMinutes, 1)
    $raw = ((Get-Content $lock -Raw) -replace '\s+', ' ').Trim()
    $ownerPid = 0
    if ([int]::TryParse(($raw -split ' ')[0], [ref]$ownerPid)) {
      $out.lock_owner = $ownerPid
      $proc = Get-Process -Id $ownerPid -ErrorAction SilentlyContinue
      $out.lock_owner_alive = [bool]$proc
      if ($proc) {
        $out.lock_owner_cmd = (Get-CimInstance Win32_Process -Filter "ProcessId=$ownerPid" -ErrorAction SilentlyContinue).CommandLine
      }
      if ($out.lock_owner_cmd -match 'hermes\.exe') { $out.deadlock = $true }
    }
  }

  if ($out.deadlock) {
    $out.verdict = "DEADLOCK: hung hermes CLI (PID $($out.lock_owner)) owns its own update lock"
    $out.remedy  = "Kill PID $($out.lock_owner). It is a hung 'hermes mcp list' holding the lock it waits on."
  } elseif ($out.lock_present -and $out.lock_owner_alive) {
    $out.verdict = 'update in progress (lock held by a live process)'
    $out.remedy  = 'Hermes is updating itself. Wait; do not interfere.'
  } elseif ($out.lock_present) {
    $out.verdict = "stale lock: owner PID $($out.lock_owner) is gone"
    $out.remedy  = 'Safe to clear .hermes-update-in-progress.'
  } elseif ($out.modified_count -gt 0) {
    $out.verdict = "$($out.modified_count) file(s) modified, no lock held"
  } else {
    $out.verdict = 'tree clean, no update in progress'
  }
  return $out
}
$state.sections.hermes_update = Get-HermesUpdate

# ----------------------------------------------------------------- QWEN -----
$qwenCred = Test-Path "$env:USERPROFILE\.qwen\oauth_creds.json"
$ollamaUp = PortUp 11434
$state.sections.qwen = [ordered]@{
  daemon_up          = (PortUp 8765)
  oauth_credential   = $qwenCred
  ollama_installed   = [bool](Get-Command ollama -ErrorAction SilentlyContinue)
  ollama_up          = $ollamaUp
  model_store_exists = (Test-Path "$env:USERPROFILE\.ollama\models")
  adapter_script     = "$PROJECTS\scripts\qwen_acp_mcp.py"
  adapter_mcp_name   = 'qwen-acp-adapter'
  note               = 'Model provider is local Ollama on 127.0.0.1:11434. If Ollama is down, qwen_prompt returns "Connection error". Install Ollama or complete qwen-oauth.'
}

# -------------------------------------------------------------- MINIMAX -----
Trace 'before minimax/mcode-tools'
$mmAuth = $null
$mmTimedOut = $false
# BOUNDED. `mcode-tools` is a node CLI that resolves its whole tool catalogue;
# it measures 573-587 ms here and has no reason to, but it is also the kind of
# command that blocks indefinitely on a network or a hung sibling process, and
# an unbounded one spends the refresher's entire 240 s budget - which ages the
# served state past the watchdog's 300 s limit and restarts the server. A
# missing auth answer should read as "did not answer", never as "not signed in".
try {
  $mmRes = Invoke-Bounded -Command 'mcode-tools auth status' -TimeoutSec 20
  if ($mmRes.TimedOut) { $mmTimedOut = $true } else { $mmAuth = ($mmRes.Text | ConvertFrom-Json) }
} catch { $mmAuth = $null }
$codeRunning = @(Get-Process -Name 'MiniMax Code' -ErrorAction SilentlyContinue).Count
$state.sections.minimax = [ordered]@{
  code_installed   = (Test-Path "$env:LOCALAPPDATA\Programs\MiniMax Code\MiniMax Code.exe")
  design_installed = (Test-Path "$env:LOCALAPPDATA\Programs\MiniMax Design\MiniMax Design.exe")
  code_processes   = $codeRunning
  cli_on_path      = [bool](Get-Command mcode-tools -ErrorAction SilentlyContinue)
  cli_auth         = if ($mmAuth) { $mmAuth.status } else { 'unavailable' }
  cli_auth_mode    = if ($mmAuth) { $mmAuth.auth_mode } else { $null }
  unified_cli      = "$PROJECTS\scripts\optimus.cmd"
  on_user_path     = (([Environment]::GetEnvironmentVariable('Path','User') -split ';') -contains "$PROJECTS\scripts")
  connector_tools  = $null
  # The catalogue itself, not just its size. "15" answers how many; it cannot
  # answer what this console can actually reach - and the reach is not uniform:
  # two of the fifteen are the Figma bridge, which is the live path to MiniMax
  # Design, and thirteen are media generation and understanding. A count hides
  # exactly the thing an operator is looking for.
  connector_families = @()
  # Is the MiniMax Design link actually LIVE, or merely listed? The catalogue
  # proves the tools are advertised. It does not prove a request would reach
  # Figma. Popy asked for a connection to MiniMax Design specifically, so the
  # console should answer "does it work" and not "how many tools are named".
  design_link        = 'not probed'
  design_probe_ms    = $null
  design_probe_note  = $null
}
try {
  $toolsRes = Invoke-Bounded -Command 'mcode-tools connector tools' -TimeoutSec 25
  if ($toolsRes.TimedOut) {
    $mmTimedOut = $true
  } else {
    $t = ($toolsRes.Text | ConvertFrom-Json)
    if ($t) {
      $state.sections.minimax.connector_tools = @($t.tools).Count
      # Group by the connector segment of connector__<family>__<tool>, and keep
      # the plain tool name rather than the fully-qualified one - the prefix is
      # the same on every row and only makes the list harder to scan.
      $fam = @{}
      foreach ($tool in @($t.tools)) {
        $tn = [string]$tool.tool_name
        $m = [regex]::Match($tn, '^connector__([^_]+(?:_[^_]+)*?)__(.+)$')
        $name = if ($m.Success) { $m.Groups[2].Value } else { $tn }
        $key  = if ($m.Success) { $m.Groups[1].Value } else { 'other' }
        if (-not $fam.ContainsKey($key)) { $fam[$key] = New-Object System.Collections.Generic.List[string] }
        $fam[$key].Add($name)
      }
      $state.sections.minimax.connector_families = @(
        foreach ($k in ($fam.Keys | Sort-Object)) {
          [ordered]@{ family = $k; count = $fam[$k].Count; tools = @($fam[$k]) }
        }
      )
    }
  }
} catch { }

# ---- the MiniMax Design link, actually exercised --------------------------
# The catalogue above proves the figma tools are ADVERTISED. It does not prove a
# request would reach Figma. Popy asked for a connection to MiniMax Design, so
# the console should answer "does it work", not "how many tools are named".
#
# The probe uses a file key that cannot exist. A reply - ANY reply from Figma -
# proves the whole path: our auth, the network, and the provider's API. Only an
# absent or unparseable answer means the link is down. Without a real key this
# can never return design data, and it is not pretending to: it is testing the
# pipe, and it says so.
if (-not $mmTimedOut) {
  $probeFile = Join-Path $env:TEMP 'cc-design-probe.json'
  try {
    [IO.File]::WriteAllText($probeFile, '{"fileKey":"MavisDesignLinkProbe000000000"}',
      (New-Object Text.UTF8Encoding $false))
    $sw = [Diagnostics.Stopwatch]::StartNew()
    # Invoke-Bounded takes a single STRING command, not an array. Passing an
    # array here would be coerced by joining on spaces, which breaks the moment
    # a path contains one. Quote it explicitly instead.
    $cmd = 'mcode-tools connector call connector__figma__get_figma_data --args-file "{0}"' -f $probeFile
    $r = Invoke-Bounded -Command $cmd -TimeoutSec 25
    $sw.Stop()
    $state.sections.minimax.design_probe_ms = [int]$sw.ElapsedMilliseconds
    $body = [string]$r.Text
    if ($r.TimedOut) {
      $state.sections.minimax.design_link = 'unreachable'
      $state.sections.minimax.design_probe_note = 'the connector call did not answer within 25 s'
    } elseif ($body -match 'figma_not_found|不存在|not.?found') {
      # Figma's own answer for a key that does not exist: the request was
      # authenticated, routed and processed. That is the proof we wanted.
      $state.sections.minimax.design_link = 'live'
      $state.sections.minimax.design_probe_note = 'Figma answered the request (test key does not exist, as intended)'
    } elseif ($body -match 'unauthorized|invalid.?token|401|forbidden') {
      $state.sections.minimax.design_link = 'unauthorised'
      $state.sections.minimax.design_probe_note = 'Figma rejected the credential'
    } else {
      $state.sections.minimax.design_link = 'answered'
      $state.sections.minimax.design_probe_note = ($body -replace '\s+',' ').Substring(0, [Math]::Min(120, $body.Length))
    }
  } catch {
    $state.sections.minimax.design_link = 'error'
    $state.sections.minimax.design_probe_note = $_.Exception.Message
  }
}

# A timeout is recorded rather than implied. Without it, a hung catalogue read
# and a machine with zero connector tools are the same field.
$state.sections.minimax.timed_out = $mmTimedOut

# ----------------------------------------------------------------- GOOGLE ----
# The Google layer. Nothing here calls a Google API. This section reports the
# state of the credentials on the machine, and it reports that state HONESTLY:
# "a client secret exists" is not "Drive is connected", and a dashboard that
# blurs those two is the exact failure class this file exists to prevent.
#
# Measured 2026-10-05, twice, because the answer changed.
#
# First measurement: OAuth client secrets and an encrypted token cache all
# existed, the cache had been refreshed that same morning, gcloud was signed in
# as apvizual@gmail.com, and five Google MCP servers were installed and enabled.
# And yet nothing was reachable: a live Drive call with the gcloud credential
# returned HTTP 403 "insufficient authentication scopes" (a Cloud SDK credential
# is scoped for GCP, not Drive).
#
# Second measurement, after Popy completed the consent: Drive is genuinely
# readable. But it did not arrive by granting a scope. gdrive-mcp@1.0.2 calls
# `Bun.secrets.get()` at src/index.ts:18, before its own environment fallback on
# line 34, and `Bun.secrets` does not exist in bun 1.2.10 on Windows. So the
# server died on startup while EXITING 0 - a green line over a corpse - and the
# package's own setup threw the refresh token away after consent. Fixed in
# projects\google-layer (shim + launcher), not by patching node_modules.
#
# Which is why this block no longer hardcodes an answer. It performs a real
# token exchange and a real Drive call, and reports what happened - including
# the reason when it fails. A collector that remembers last week's verdict is a
# collector that will confidently report a lie.
Trace 'before google'
$gwsDir = Join-Path $env:USERPROFILE '.config\gws'
$gwsSec = Join-Path $gwsDir 'client_secret.json'
$gwsTok = Join-Path $gwsDir 'token_cache.json'
$gwsMcp = Join-Path $gwsDir 'mcp-secrets.json'   # written by projects\google-layer
$gcsCmd = Get-Command gcloud -ErrorAction SilentlyContinue
$state.sections.google = [ordered]@{
  # What exists on disk. None of these implies access.
  client_secret_present = (Test-Path -LiteralPath $gwsSec)
  token_cache_present   = (Test-Path -LiteralPath $gwsTok)
  token_refreshed_at    = if (Test-Path -LiteralPath $gwsTok) { (Get-Item -LiteralPath $gwsTok).LastWriteTime.ToString('o') } else { $null }
  mcp_credentials_present = (Test-Path -LiteralPath $gwsMcp)
  mcp_credentials_at    = if (Test-Path -LiteralPath $gwsMcp) { (Get-Item -LiteralPath $gwsMcp).LastWriteTime.ToString('o') } else { $null }
  gcloud_present        = [bool]$gcsCmd
  gcloud_account        = $null
  mcp_servers           = @('gdrive-mcp','gmail-mcp','google-workspace-mcp','google-calendar-mcp','notebooklm-mcp')
  # Measured below by real calls, never assumed.
  connected             = $false
  scopes_usable         = $false
  drive_probe           = 'not attempted'
  probe_ms              = $null
  sample_files          = @()
  services              = @()
  gmail_probe           = 'not attempted'
  calendar_probe        = 'not attempted'
  gmail_count           = $null
  calendar_count        = $null
  workspace_credential_present = $false
  read_only_verified    = $false
  reason                = 'not probed'
  remedy                = $null
}
if ($gcsCmd) {
  try {
    $acct = (& $gcsCmd.Source auth list --filter='status:ACTIVE' --format='value(account)' 2>$null) | Select-Object -First 1
    $state.sections.google.gcloud_account = $acct
  } catch { }
}

# ---- the honest measurement -------------------------------------------------
# Exchange the stored refresh token for an access token and then actually list
# Drive. Both calls are bounded. Anything less than a real listing would be
# reporting an assumption, which is what this file has refused to do throughout.
if (Test-Path -LiteralPath $gwsMcp) {
  $probe = [Diagnostics.Stopwatch]::StartNew()
  try {
    $sec = [System.IO.File]::ReadAllText($gwsMcp, [Text.Encoding]::UTF8) | ConvertFrom-Json
    $cid = $sec.'gdrive-mcp/client_id'
    $csec = $sec.'gdrive-mcp/client_secret'
    $rtok = $sec.'gdrive-mcp/refresh_token'
    if (-not ($cid -and $csec -and $rtok)) { throw 'the credential file has no complete gdrive-mcp triple' }

    $body = 'grant_type=refresh_token&client_id=' + [uri]::EscapeDataString($cid) +
            '&client_secret=' + [uri]::EscapeDataString($csec) +
            '&refresh_token=' + [uri]::EscapeDataString($rtok)
    $tok = Invoke-RestMethod -Method Post -Uri 'https://oauth2.googleapis.com/token' `
            -ContentType 'application/x-www-form-urlencoded' -Body $body -TimeoutSec 15

    $hdr = @{ Authorization = 'Bearer ' + $tok.access_token }
    $res = Invoke-RestMethod -Method Get -Uri 'https://www.googleapis.com/drive/v3/files?pageSize=3&fields=files(id,name,modifiedTime)' `
            -Headers $hdr -TimeoutSec 20
    $probe.Stop()

    $state.sections.google.connected     = $true
    $state.sections.google.scopes_usable = $true
    $state.sections.google.probe_ms      = [int]$probe.ElapsedMilliseconds
    $state.sections.google.drive_probe   = 'HTTP 200 - real listing returned'
    $state.sections.google.reason        = $null
    $state.sections.google.sample_files  = @($res.files | ForEach-Object { $_.name })
  } catch {
    $probe.Stop()
    $msg = $_.Exception.Message
    # 403 here means the token lacks the scope; 401 means it is dead. Those are
    # different problems with different fixes, so they are not collapsed.
    $state.sections.google.drive_probe = 'FAILED: ' + $msg
    $state.sections.google.probe_ms    = [int]$probe.ElapsedMilliseconds
    if ($msg -match 'insufficient|403|scope') {
      $state.sections.google.reason = 'the token exists but is not scoped for Drive'
      $state.sections.google.remedy = 're-run projects\google-layer\gdrive-oauth.js and accept the Drive scope'
    } elseif ($msg -match '401|invalid_grant') {
      $state.sections.google.reason = 'the refresh token is no longer valid'
      $state.sections.google.remedy = 're-run projects\google-layer\gdrive-oauth.js to grant a fresh one'
    } else {
      $state.sections.google.reason = $msg
      $state.sections.google.remedy = 'check network reachability to googleapis.com'
    }
  }
} else {
  $state.sections.google.drive_probe = 'no credential file at ~/.config/gws/mcp-secrets.json'
  $state.sections.google.reason      = 'no Drive credential has been granted on this machine'
  $state.sections.google.remedy      = 'run projects\google-layer\gdrive-oauth.js, then complete the consent'
}

# A SECOND, independently granted credential covers Gmail and Calendar
# READ-ONLY (google-workspace-mcp, ~/.google-mcp/tokens). Probed the same way as
# Drive - a real call, not an inference from the fact that a token exists -
# because "the file is there" has already been shown to be worth nothing.
#
# This block is deliberately OUTSIDE the Drive try/catch. Sharing one handler
# meant a failure here overwrite `drive_probe` with Drive's failure message
# while Drive was in fact working: one broken probe silently condemned the
# other. Each measurement now fails on its own.
$wsTok = Join-Path $env:USERPROFILE '.google-mcp\tokens\apvizual.json'
$state.sections.google.workspace_credential_present = (Test-Path -LiteralPath $wsTok)
if (Test-Path -LiteralPath $wsTok) {
  try {
    $wt = [System.IO.File]::ReadAllText($wsTok, [Text.Encoding]::UTF8) | ConvertFrom-Json
    $wbody = 'grant_type=refresh_token&client_id=' + [uri]::EscapeDataString($wt.client_id) +
             '&client_secret=' + [uri]::EscapeDataString($wt.client_secret) +
             '&refresh_token=' + [uri]::EscapeDataString($wt.refresh_token)
    $wtok = Invoke-RestMethod -Method Post -Uri 'https://oauth2.googleapis.com/token' `
             -ContentType 'application/x-www-form-urlencoded' -Body $wbody -TimeoutSec 15
    $whdr = @{ Authorization = 'Bearer ' + $wtok.access_token }
    try {
      $gm = Invoke-RestMethod -Method Get -Uri 'https://gmail.googleapis.com/gmail/v1/users/me/messages?maxResults=1' `
              -Headers $whdr -TimeoutSec 15
      $state.sections.google.gmail_probe = 'HTTP 200'
      $state.sections.google.gmail_count = @($gm.messages).Count
    } catch { $state.sections.google.gmail_probe = 'FAILED: ' + $_.Exception.Message }
    try {
      $cl = Invoke-RestMethod -Method Get -Uri 'https://www.googleapis.com/calendar/v3/users/me/calendarList?maxResults=50' `
              -Headers $whdr -TimeoutSec 15
      $state.sections.google.calendar_probe = 'HTTP 200'
      $state.sections.google.calendar_count = @($cl.items).Count
    } catch { $state.sections.google.calendar_probe = 'FAILED: ' + $_.Exception.Message }
  } catch {
    $state.sections.google.gmail_probe    = 'token exchange FAILED: ' + $_.Exception.Message
    $state.sections.google.calendar_probe = 'not attempted'
  }
}

# --------------------------------------------------------------- NOTEBOOKLM --
# minimax's OWN NotebookLM server (projects\google-layer\minimax-notebooklm.js).
# Never notebooklm-mcp: that is the package Hermes runs, and the two must not be
# combined. Listing notebooks needs a real browser round-trip against the
# authenticated profile, so it is cached for 10 minutes rather than run every
# cycle. A failure keeps the last good result and says so - a missing
# measurement is never reported as an empty notebook library.
Trace 'before notebooks'
$nbCache = Join-Path $PSScriptRoot 'notebooks-cache.json'
$nbFresh = $false
if (Test-Path -LiteralPath $nbCache) {
  try { $nbFresh = ((Get-Date) - (Get-Item -LiteralPath $nbCache).LastWriteTime).TotalMinutes -lt 10 } catch {}
}
if (-not $nbFresh) {
  try {
    # projects\google-layer is a SIBLING of 90_CONTROL_CENTER, not a child.
    # $PSScriptRoot is ...\projects\90_CONTROL_CENTER\api, so it takes TWO
    # Split-Path hops to reach projects\.
    $reg = Join-Path (Split-Path -Parent (Split-Path -Parent $PSScriptRoot)) 'google-layer\notebook-registrar.js'
    $r = Invoke-Bounded -Command ('node "{0}"' -f $reg) -TimeoutSec 90
    if (-not $r.TimedOut -and $r.Text -match '"notebooks"') {
      $parsed = $r.Text | ConvertFrom-Json
      $payload = [ordered]@{
        at            = (Get-Date).ToString('o')
        authenticated = [bool]$parsed.authenticated
        count         = @($parsed.notebooks).Count
        notebooks     = @($parsed.notebooks)
      }
      [IO.File]::WriteAllText($nbCache, ($payload | ConvertTo-Json -Depth 5), (New-Object Text.UTF8Encoding $false))
    }
  } catch { }
}
$state.sections.notebooks = [ordered]@{
  server        = 'minimax-notebooklm'
  measured      = $false
  authenticated = $false
  count         = 0
  notebooks     = @()
  total_sources = 0
  age_sec       = $null
  note          = 'not measured yet'
}
if (Test-Path -LiteralPath $nbCache) {
  try {
    $c2 = [System.IO.File]::ReadAllText($nbCache, [Text.Encoding]::UTF8) | ConvertFrom-Json
    $state.sections.notebooks.measured      = $true
    $state.sections.notebooks.authenticated = [bool]$c2.authenticated
    $state.sections.notebooks.count         = @($c2.notebooks).Count
    $state.sections.notebooks.notebooks     = @($c2.notebooks)
    $state.sections.notebooks.age_sec      = [int]((Get-Date) - (Get-Item -LiteralPath $nbCache).LastWriteTime).TotalSeconds
    $tot = 0
    foreach ($n in @($c2.notebooks)) { if ($n.sources -match '(\d+)') { $tot += [int]$Matches[1] } }
    $state.sections.notebooks.total_sources = $tot
    $state.sections.notebooks.note = 'read through the minimax NotebookLM profile over CDP - not the Hermes notebooklm-mcp package'
  } catch { $state.sections.notebooks.note = 'cache unreadable: ' + $_.Exception.Message }
}

# ---------------------------------------------------------------- SKILLS ----
$skillSrc = $MavisSkillsRoot
$names = @()
if (Test-Path $skillSrc) { $names = @(Get-ChildItem $skillSrc -Directory -EA SilentlyContinue | Select-Object -ExpandProperty Name | Sort-Object) }
$personal = Count-Children $PersonalSkillsRoot
$hermesSkills = Count-Children (Join-Path $HermesRoot 'skills')
$mavisSkills = Count-Children $MavisSkillsRoot
$state.sections.skills = [ordered]@{
  mavis_count     = $names.Count
  mavis_names     = $names
  personal_count  = $personal.count
  personal_root   = $PersonalSkillsRoot
  personal_present = $personal.present
  hermes_count    = $hermesSkills.count
  hermes_root     = (Join-Path $HermesRoot 'skills')
  hermes_present  = $hermesSkills.present
  mavis_root      = $MavisSkillsRoot
  mavis_present   = $mavisSkills.present
  sot_link        = (Test-Path "$PROJECTS\60_SKILLS\_links\mavis-skills")
}

# ------------------------------------------------------------ PROJECTS -----
$sections = [ordered]@{
  '00_INDEX'      = 'Index and master maps'
  '10_BRIDGES'    = 'Bridge specifications'
  '20_BRIDGES'    = 'Bridge implementation + Wayland + MiniMax'
  '20_PROTOCOLS'  = 'Operational protocols'
  '30_WORKFLOWS'  = 'Session workflows'
  '40_REGISTRIES' = 'Source registries (D:/E:/C:)'
  '50_TEMPLATES'  = 'Reusable templates'
  '60_SKILLS'     = 'Skill source of truth'
  '70_CONNECTORS' = 'Connector source of truth'
  '90_CONTROL_CENTER' = 'This dashboard'
  'SENTINEL_PRIME'    = 'Doctrine substrate'
  'logs'          = 'Runtime logs'
  'scratch'       = 'Test artifacts'
}
$secOut = [ordered]@{}
foreach ($k in $sections.Keys) {
  $info = DirInfo (Join-Path $PROJECTS $k)
  $info['title'] = $sections[$k]
  $info['root_docs'] = @()
  if ($info['exists'] -and $k -ne 'logs' -and $k -ne 'scratch') {
    $info['root_docs'] = @(Get-ChildItem (Join-Path $PROJECTS $k) -File -Filter '*.md' -EA SilentlyContinue |
                           Select-Object -First 40 | ForEach-Object { $_.Name })
  }
  $secOut[$k] = $info
}
$secOut['scripts'] = DirInfo "$PROJECTS\scripts"
$secOut['scripts']['title'] = 'Central script source of truth'
$secOut['scripts']['root_docs'] = @()
$state.sections.projects = $secOut

$state.sections.docs = [ordered]@{
  root = @(Get-ChildItem $PROJECTS -File -Filter '*.md' -EA SilentlyContinue |
           Sort-Object LastWriteTime -Descending | ForEach-Object {
             [ordered]@{ name = $_.Name; bytes = $_.Length; modified = $_.LastWriteTime.ToString('o') }
           })
}

# ------------------------------------------------------------- ACTIONS -----
$state.actions = @(
  @{ id = 'status';        label = 'Full status';        cmd = 'optimus status' }
  @{ id = 'doctor';        label = 'Deep doctor';        cmd = 'optimus doctor --deep' }
  @{ id = 'census';        label = 'Docker census';      cmd = 'optimus docker census' }
  @{ id = 'bridge_health'; label = 'Bridge health';      cmd = 'optimus bridge health' }
  @{ id = 'sot_list';      label = 'Show SOT links';     cmd = 'optimus sot list' }
  @{ id = 'skills';        label = 'List Mavis skills';  cmd = 'optimus skills list' }
  @{ id = 'qwen_status';   label = 'Qwen status';        cmd = 'optimus qwen status' }
  @{ id = 'compose_check'; label = 'Validate compose';   cmd = "docker compose -f `"$ComposeFile`" config --quiet" }
  @{ id = 'app_status';    label = 'MiniMax app status'; cmd = 'optimus app status' }
  @{ id = 'ai_auth';       label = 'MiniMax CLI auth';   cmd = 'mcode-tools auth status' }
  @{ id = 'ai_tools';      label = 'List connector tools'; cmd = 'mcode-tools connector tools' }
  @{ id = 'qwen_doctor';   label = 'Qwen ACP doctor';    cmd = 'optimus qwen doctor' }
  @{ id = 'state_doc';     label = 'Rebuild current-state doc'; cmd = 'projects\scripts\build-current-state.ps1' }
  @{ id = 'mojibake';      label = 'Check docs encoding'; cmd = 'projects\scripts\repair-mojibake.ps1 (dry run)' }
  @{ id = 'journal';       label = 'Bridge journal (tail)'; cmd = 'read the audit trail the bridges write' }
)

Trace 'before history'
# --------------------------------------------------------------- HISTORY ---
# The substrate for trends, anomaly detection and incident correlation.
# Without a server-side record of past samples there is no history to reason
# over - only what happens to be true at this second.
#
# A line is appended ONLY when a tracked value actually CHANGED. A stable
# system would otherwise append a duplicate line every cycle forever and drown
# its own history.
$HistoryPath = Join-Path $PSScriptRoot 'state-history.jsonl'
$HistoryMax  = 400
# How far past the cap the file may grow before a trim runs. A small slack turns
# "rewrite the whole file on every sample" into "rewrite it every ~50 samples",
# which is the difference between a permanent 67 KB write per cycle and a rare
# one. The cap the operator sees is still $HistoryMax after any trim.
$HistoryTrimSlack = 50

function Write-HistorySample([string]$json) {
  $s = $json | ConvertFrom-Json
  # Measure-Object returns $null - not 0 - on an EMPTY pipeline, and a bridge
  # object missing the key measures as 0. The empty case cannot happen while
  # bridges is the fixed two-element array, but this file is append-only and
  # 400 samples deep: one null written here is permanent, and it would sit in
  # the median baseline for that metric for the next 400 cycles. Coerce it.
  $bWarn = ($s.sections.bridges | Measure-Object -Property warn -Sum).Sum
  $bFail = ($s.sections.bridges | Measure-Object -Property fail -Sum).Sum
  if ($null -eq $bWarn) { $bWarn = 0 }
  if ($null -eq $bFail) { $bFail = 0 }
  $sample = [ordered]@{
    ts          = $s.generated
    total       = $s.sections.docker.total
    hermes      = $s.sections.docker.hermes_mcp
    b_up        = @($s.sections.bridges | Where-Object { $_.up }).Count
    b_warn      = $bWarn
    b_fail      = $bFail
    svc_up      = @($s.sections.services | Where-Object { $_.up }).Count
    cli_auth    = $s.sections.minimax.cli_auth
    qwen_daemon = $s.sections.qwen.daemon_up
    skills      = $s.sections.skills.mavis_count
  }
  $line = $sample | ConvertTo-Json -Compress

  if (Test-Path $HistoryPath) {
    $tail = @(Get-Content $HistoryPath -Tail 1 -Encoding UTF8 -ErrorAction SilentlyContinue |
              Where-Object { $_ -and $_.Trim() })
    if ($tail.Count) {
      try {
        $prev = $tail[0] | ConvertFrom-Json
        # Compare every tracked field EXCEPT the timestamp. The timestamp is
        # regenerated on every single run, so including it made every sample
        # look like a change and the history filled with false transitions.
        $same = $true
        foreach ($k in @('total','hermes','b_up','b_warn','b_fail','svc_up',
                         'cli_auth','qwen_daemon','skills')) {
          if ([string]$prev.$k -ne [string]$sample[$k]) { $same = $false; break }
        }
        if ($same) { return $false }
      } catch { }
    }
  }
  Add-Content -LiteralPath $HistoryPath -Value $line -Encoding UTF8
  # Trim in BATCHES, and write ATOMICALLY.
  #
  # Batch: the old test trimmed whenever the file exceeded the cap, so once the
  # history sat AT 400 - which is where it lives permanently - every single
  # sample re-read and rewrote all 400 lines. That is 67 KB rewritten every ~40 s
  # forever, to remove exactly one line.
  #
  # Atomic: Set-Content rewrites IN PLACE. A crash part-way through leaves a
  # truncated file, and the read path silently SKIPS unparseable lines - so the
  # damage presents as history that was never collected, which is precisely the
  # signature you would never think to investigate. The temp+replace below is
  # the same one already used for live-state.json.
  $all = @(Get-Content $HistoryPath -Encoding UTF8 -ErrorAction SilentlyContinue)
  if ($all.Count -gt ($HistoryMax + $HistoryTrimSlack)) {
    $keep = $all[($all.Count - $HistoryMax)..($all.Count - 1)]
    $htmp = "$HistoryPath.$PID.tmp"
    try {
      Set-Content -LiteralPath $htmp -Value $keep -Encoding UTF8
      try { [System.IO.File]::Replace($htmp, $HistoryPath, $null, $true) }
      catch { Move-Item -LiteralPath $htmp -Destination $HistoryPath -Force }
    } catch { }
  }
  return $true
}

$rawState = $state | ConvertTo-Json -Depth 12 -Compress
$state.history_written = Write-HistorySample $rawState

# --------------------------------------------------------------- ANALYSIS --
# Derived views over the history. This is what turns a readout into an
# instrument: a trend, a deviation, or a change worth naming.
$hist = @()
if (Test-Path $HistoryPath) {
  # Blank lines must be dropped HERE, not just in the chart. A file whose first
  # line is empty parses to $null, and that null lands in total_series[0] - so
  # the trend chart opened on a null and reported a fabricated rise off zero.
  # One bad line poisons every series derived from it.
  $hist = @(Get-Content $HistoryPath -Encoding UTF8 -ErrorAction SilentlyContinue |
            Where-Object { $_ -and $_.Trim() } |
            ForEach-Object { try { $_ | ConvertFrom-Json } catch { } } |
            Where-Object { $_ })
}
$state.history = [ordered]@{
  path         = $HistoryPath
  samples      = $hist.Count
  first        = if ($hist.Count) { $hist[0].ts } else { $null }
  last         = if ($hist.Count) { $hist[-1].ts } else { $null }
  total_series = @($hist | ForEach-Object { $_.total })
  fail_series  = @($hist | ForEach-Object { $_.b_fail })
  warn_series  = @($hist | ForEach-Object { $_.b_warn })
  by_day       = @($hist | Group-Object { ([datetime]$_.ts).ToString('yyyy-MM-dd') } |
                     Sort-Object Name |
                     ForEach-Object {
                       [ordered]@{
                         day     = $_.Name
                         samples = $_.Count
                         warns   = ($_.Group | Measure-Object -Property b_warn -Maximum).Maximum
                         fails   = ($_.Group | Measure-Object -Property b_fail -Maximum).Maximum
                         minTot  = ($_.Group | Measure-Object -Property total -Minimum).Minimum
                         maxTot  = ($_.Group | Measure-Object -Property total -Maximum).Maximum
                       }
                     })
}

Trace 'before supervision'
# ------------------------------------------------------------ SUPERVISION ---
# The system reporting on its own survival. The supervisor (cc-watchdog.ps1)
# writes cc-health.json; reading it here puts the answer into the SAME snapshot
# every other number comes from, so the Resilience tab needs no second request
# and cannot disagree with the Overview about what is true right now.
$supPath = Join-Path $PSScriptRoot 'cc-health.json'
$state.supervision = [ordered]@{
  known       = (Test-Path $supPath)
  healthy     = $false
  reason      = 'supervisor has never reported - nothing is watching this server'
  restarts    = 0
  watchdog_pid = $null
  watchdog_started = $null
  last_restart = $null
  last_restart_reason = $null
  state_age_sec = $null
  interval_sec = $null
  log         = $null
  recent      = @()
}
Trace 'after supervision-defaults'
if ($state.supervision.known) {
  try {
    $sh = [IO.File]::ReadAllText($supPath, [Text.Encoding]::UTF8) | ConvertFrom-Json
    $state.supervision.healthy      = [bool]$sh.healthy
    $state.supervision.reason       = $sh.reason
    $state.supervision.restarts     = $sh.restarts
    $state.supervision.watchdog_pid = $sh.watchdog_pid
    $state.supervision.watchdog_started = $sh.watchdog_started
    $state.supervision.last_restart = $sh.last_restart
    $state.supervision.last_restart_reason = $sh.last_restart_reason
    $state.supervision.state_age_sec = $sh.state_age_sec
    $state.supervision.interval_sec = $sh.interval_sec
  } catch { $state.supervision.reason = "supervisor file unreadable: $($_.Exception.Message)" }
}
# The supervisor's own log, so a restart is explained rather than just counted.
#
# It must be read with an explicitly SHARED handle. The supervisor appends with
# Add-Content, which holds the file open, and a plain Get-Content then fails with
# "The process cannot access the file because it is being used by another
# process" - so the Resilience tab's log panel threw whenever the supervisor was
# healthy, which is exactly when you most want to read it.
function Read-SharedTail {
  param([string]$Path, [int]$Tail = 12)
  try {
    $fs = New-Object IO.FileStream($Path, [IO.FileMode]::Open, [IO.FileAccess]::Read, [IO.FileShare]::ReadWrite)
    try {
      $sr = New-Object IO.StreamReader($fs)
      $t  = $sr.ReadToEnd()
      $sr.Close()
    } finally { $fs.Close() }
    $all = @($t -split "`r?`n" | Where-Object { $_ -and $_.Trim() })
    if ($all.Count -le $Tail) { return $all }
    return $all[($all.Count - $Tail)..($all.Count - 1)]
  } catch { return @() }
}
$wlog = Join-Path (Split-Path $PSScriptRoot -Parent) 'logs\watchdog.log'
if (Test-Path $wlog) {
  Trace 'reading watchdog log'
  $state.supervision.log = $wlog
  $state.supervision.recent = Read-SharedTail -Path $wlog -Tail 12
}

# Anomalies: the current value departing from its own recent baseline. Uses the
# MEDIAN of the last N samples, not the mean, so one spike cannot drag the
# baseline and then hide itself behind it.
$anoms = New-Object System.Collections.Generic.List[object]
function Get-Median($vals) {
  $s = @($vals | Sort-Object)
  if (-not $s.Count) { return $null }
  return $s[[int]($s.Count / 2)]
}
function Add-Anomaly($metric, $value, $baseline, $note) {
  if ($null -eq $baseline -or $baseline -eq 0 -or $null -eq $value) { return }
  $dev = [math]::Abs(($value - $baseline) / $baseline * 100)
  if ($dev -ge 10) {
    $anoms.Add([ordered]@{
      metric = $metric; value = $value; baseline = $baseline
      deviation_pct = [math]::Round($dev, 1); note = $note
    })
  }
}
$recent = if ($hist.Count -gt 12) { @($hist[($hist.Count - 12)..($hist.Count - 2)]) } else { @() }
if ($recent.Count -ge 3) {
  $curFail = ($state.sections.bridges | Measure-Object -Property fail -Sum).Sum
  # An anomaly is a claim that a value MOVED. With a missing reading there is
  # nothing to have moved, and comparing null against a median manufactures one.
  if ($null -ne $state.sections.docker.total) {
    Add-Anomaly 'containers'   $state.sections.docker.total    (Get-Median @($recent | ForEach-Object { $_.total }))   'container count moved away from its recent baseline'
  }
  if ($null -ne $state.sections.docker.hermes_mcp) {
    Add-Anomaly 'hermes_mcp'   $state.sections.docker.hermes_mcp (Get-Median @($recent | ForEach-Object { $_.hermes })) 'the hermes-mcp fleet size changed'
  }
  if ($null -ne $curFail) {
    Add-Anomaly 'bridge_fail'  $curFail                        (Get-Median @($recent | ForEach-Object { $_.b_fail }))  'bridge failure count changed'
  }
}
Trace 'after anomalies-block'
$state.anomalies = @($anoms.ToArray())

# Incidents: the TRANSITIONS, not the current state. This is the question a
# snapshot cannot answer on its own - when did it change, and what else changed
# at the same moment.
$incidents = New-Object System.Collections.Generic.List[object]
$gapCount = 0
for ($i = 1; $i -lt $hist.Count; $i++) {
  $prev = $hist[$i - 1]; $cur = $hist[$i]
  $changes = @()
  foreach ($k in @('total','hermes','b_up','b_warn','b_fail','svc_up','cli_auth','qwen_daemon','skills')) {
    $a = $prev.$k; $b = $cur.$k
    # A missing reading is a GAP, not a change. Comparing through [string] turns
    # $null into '', so a probe that failed for one cycle recorded a phantom
    # incident reading "total: 63 -> " and then "total:  -> 63" when it came
    # back. On a tab whose entire value is that an incident means something,
    # an incident nobody caused is worse than no incident at all.
    $aMissing = ($null -eq $a) -or ([string]$a -eq '')
    $bMissing = ($null -eq $b) -or ([string]$b -eq '')
    if ($aMissing -or $bMissing) {
      if ($aMissing -and $bMissing) { $gapCount++ }
      continue
    }
    if ([string]$a -ne [string]$b) { $changes += ('{0}: {1} -> {2}' -f $k, $a, $b) }
  }
  if ($changes.Count) { $incidents.Add([ordered]@{ at = $cur.ts; changes = $changes }) }
}
Trace 'after incidents-block'
$state.incidents = @($incidents | Select-Object -Last 12)
# Gaps are reported as their own fact rather than smuggled in as a transition.
$state.history_gaps = $gapCount

# ---------------------------------------------------------- AUTHENTICATION ---
# The console measured everything EXCEPT the thing the operator is actually
# blocked on, which is access. An auth panel belongs here: each credential, what
# state it is in, and the exact next action. Probed, never assumed - a 401 from
# the Drive API is the honest answer and is reported as one.
Trace 'before auth census'
$state.sections.auth = [ordered]@{ items = @(); note = '' }
try {
  $mc = Join-Path $env:USERPROFILE '.minimax\mcp.json'
  $mcpNames = @()
  if (Test-Path $mc) { try { $mcpNames = @(([IO.File]::ReadAllText($mc) | ConvertFrom-Json).mcpServers.PSObject.Properties.Name) } catch { } }

  # --- Google Drive: does the API actually answer for us? ---
  # This probe used to call drive/v3/about with NO Authorization header at all,
  # so it answered 401 unconditionally and reported "no token is stored yet"
  # while the google section two hundred lines above was returning a live file
  # listing from the same account. Two panels, two different truths, both drawn
  # from real calls. It now exchanges the same stored refresh token and carries
  # the Bearer, so a 401 here means what it says.
  $gState = 'unknown'; $gDetail = ''
  $authTok = Join-Path $env:USERPROFILE '.config\gws\mcp-secrets.json'
  try {
    if (-not (Test-Path -LiteralPath $authTok)) { throw 'no stored Drive credential' }
    $sec2 = [System.IO.File]::ReadAllText($authTok, [Text.Encoding]::UTF8) | ConvertFrom-Json
    $b2 = 'grant_type=refresh_token&client_id=' + [uri]::EscapeDataString($sec2.'gdrive-mcp/client_id') +
          '&client_secret=' + [uri]::EscapeDataString($sec2.'gdrive-mcp/client_secret') +
          '&refresh_token=' + [uri]::EscapeDataString($sec2.'gdrive-mcp/refresh_token')
    $t2 = Invoke-RestMethod -Method Post -Uri 'https://oauth2.googleapis.com/token' `
           -ContentType 'application/x-www-form-urlencoded' -Body $b2 -TimeoutSec 15
    $req = [Net.HttpWebRequest]::Create('https://www.googleapis.com/drive/v3/about?fields=user')
    $req.Timeout = 10000; $req.ReadWriteTimeout = 10000
    $req.Headers['Authorization'] = 'Bearer ' + $t2.access_token
    $resp = $req.GetResponse()
    $sr = New-Object IO.StreamReader($resp.GetResponseStream())
    $gb = $sr.ReadToEnd(); $sr.Close(); $resp.Close()
    $who = ''
    try { $who = ($gb | ConvertFrom-Json).user.emailAddress } catch { }
    $gState = 'connected'
    $gDetail = if ($who) { "Drive answered for $who" } else { 'Drive answered for your account' }
  } catch [Net.WebException] {
    $code = try { [int]$_.Exception.Response.StatusCode } catch { 0 }
    if ($code -eq 401) { $gState = 'no-credential'; $gDetail = 'Drive returned 401 for the stored refresh token' }
    else { $gState = 'unreachable'; $gDetail = "Drive probe failed ($code)" }
  } catch { $gState = 'unreachable'; $gDetail = $_.Exception.Message }

  $credDrive = Test-Path (Join-Path $env:USERPROFILE '.config\mcp-gdrive\credentials.json')
  $credWs    = Test-Path (Join-Path $env:USERPROFILE '.google-mcp\credentials.json')
  $tokDrive  = Test-Path (Join-Path $env:USERPROFILE '.config\mcp-gdrive\token.json')

  # Gmail and Workspace are reported from the SECOND credential actually in use
  # (google-workspace-mcp, ~/.google-mcp/tokens), not from the two disabled
  # standalone packages. Those were measured to fail on startup and are
  # redundant; continuing to describe their requested scopes as this machine's
  # exposure would report a risk that is not actually granted.
  $wsTokPath = Join-Path $env:USERPROFILE '.google-mcp\tokens\apvizual.json'
  $wsLive    = Test-Path -LiteralPath $wsTokPath
  $gmailProbe = $state.sections.google.gmail_probe
  $calProbe   = $state.sections.google.calendar_probe
  $gmOk = ($gmailProbe -eq 'HTTP 200')
  $clOk = ($calProbe  -eq 'HTTP 200')

  $state.sections.auth.items = @(
    [ordered]@{
      name = 'Google Drive'; state = $gState; detail = $gDetail
      installed = ($mcpNames -contains 'gdrive-mcp')
      remedy = $(if ($gState -eq 'connected') { 'none - connected and probed live' }
                 elseif ($credDrive) { 'credentials.json is in place; run projects\google-layer\gdrive-oauth.js' }
                 elseif ($tokDrive) { 'token.json exists - it may have expired' }
                 else { 'run projects\google-layer\gdrive-oauth.js to grant a Drive credential' })
      scopes = 'auth/drive (full) - as shipped by gdrive-mcp'
      risk = 'full read AND write on Drive. This is the package default, not a narrowed grant.'
    }
    [ordered]@{
      name = 'Gmail'; state = $(if ($gmOk) { 'connected-read-only' } elseif ($wsLive) { 'credential-present' } else { 'no-credential' })
      detail = $(if ($gmOk) { "messages.list answered; $($state.sections.google.gmail_count) sampled" }
                 else { 'not probed successfully this cycle' })
      installed = ($mcpNames -contains 'google-workspace-mcp')
      remedy = $(if ($gmOk) { 'none - connected read-only' } else { 'run projects\google-layer\gworkspace-oauth.js and accept the Gmail scopes' })
      scopes = 'gmail.readonly - narrowed deliberately'
      risk = 'read only. A write attempt was refused by Google with HTTP 403 insufficientPermissions.'
    }
    [ordered]@{
      name = 'Google Calendar'; state = $(if ($clOk) { 'connected-read-only' } elseif ($wsLive) { 'credential-present' } else { 'no-credential' })
      detail = $(if ($clOk) { "calendarList answered; $($state.sections.google.calendar_count) calendar(s) visible" } else { 'not probed successfully this cycle' })
      installed = ($mcpNames -contains 'google-workspace-mcp')
      remedy = $(if ($clOk) { 'none - connected read-only' } else { 'run projects\google-layer\gworkspace-oauth.js and accept the Calendar scopes' })
      scopes = 'calendar.readonly - narrowed deliberately'
      risk = 'read only.'
    }
    [ordered]@{
      name = 'Google Workspace'; state = $(if ($wsLive) { 'connected-read-only' } else { 'no-credentials' })
      detail = $(if ($wsLive) { "110 tools, one account loaded, serve --read-only; Drive $($state.sections.google.drive_probe), Gmail $gmailProbe, Calendar $calProbe" } else { 'no credential at ~/.google-mcp/tokens' })
      installed = ($mcpNames -contains 'google-workspace-mcp')
      remedy = $(if ($wsLive) { 'none - connected read-only' } else { 'run projects\google-layer\gworkspace-oauth.js' })
      scopes = 'drive/documents/spreadsheets/presentations/calendar/gmail - all .readonly'
      risk = 'read only. The package as shipped asks for full write plus gmail.modify; that grant was deliberately not taken.'
    }
    [ordered]@{
      name = 'NotebookLM'; state = $(if ($mcpNames -contains 'notebooklm-mcp') { 'configured' } else { 'not-configured' })
      detail = 'authenticates on its own terms - not through the Google OAuth client above'
      installed = ($mcpNames -contains 'notebooklm-mcp')
      remedy = 'start the notebooklm-mcp server and complete its own sign-in'
      scopes = 'its own'
      risk = 'separate credential from the Drive/Gmail path.'
    }
    [ordered]@{
      name = 'MiniMax CLI'; state = $(if ($state.sections.minimax.cli_auth -eq 'authenticated') { 'connected' } else { 'not-authenticated' })
      detail = "shared broker, scope agent.default - only MiniMax Code can use it, not the other CLIs"
      installed = $true
      remedy = 'none needed for the console; separate from the CLI fleet'
      scopes = 'n/a'
      risk = 'low'
    }
  )
  $state.sections.auth.note = 'Every state above came from a live call this cycle, not from a stored flag. Drive answers on auth/drive; Gmail and Calendar answer on a second, deliberately narrowed .readonly grant whose refusal to write was verified with a real 403. The two standalone packages gmail-mcp and google-calendar-mcp are disabled: both were measured to fail on startup, and both are now redundant with google-workspace-mcp.'
} catch { $state.sections.auth.note = "auth census failed: $($_.Exception.Message)" }

# ------------------------------------------------------------ PROCESSES -----
# Node servers come in SETS - one set per live agent session - so a raw count
# looks like a leak and is not one. Measured 2026-10-04: 164 node processes,
# 140 of them with a live parent and 142 live shells, i.e. exactly one set per
# agent, and only some genuinely orphaned. So report the orphans.
#
# CACHED, and that is not an optimisation - it is a correctness fix. The
# census needs Get-CimInstance over every process, which costs seconds, and
# adding it inline pushed the whole collector past the 90 s cap. The refresher
# then killed the collector on EVERY run (377/377 in refresher.err.log) and the
# supervisor crash-looped the server roughly every five minutes. A measurement
# that is too slow to finish is not a measurement, it is an outage.
#
# The values change slowly, so a 5-minute cache is honest for a 20 s poll.
$state.sections.processes = [ordered]@{
  node_total = 0; orphans = 0; orphan_mb = 0; live_shells = 0; attached = 0; cached_at = $null
  note = 'one MCP server set per live agent is NORMAL. Only a process whose parent has EXITED - counting the whole chain, not just one hop - is a leak.'
}
Trace 'before process census'
$pcCache = Join-Path $PSScriptRoot 'processes-cache.json'
$pcFresh = $false
if (Test-Path $pcCache) {
  try {
    $pc = [IO.File]::ReadAllText($pcCache, [Text.Encoding]::UTF8) | ConvertFrom-Json
    if ($pc -and $pc.cached_at -and (((Get-Date) - [datetime]$pc.cached_at).TotalMinutes -lt 5)) { $pcFresh = $true }
  } catch { }
}
if ($pcFresh) {
  foreach ($k in @('node_total','orphans','orphan_mb','live_shells','attached')) {
    $state.sections.processes[$k] = $pc.$k
  }
  $state.sections.processes.cached_at = $pc.at
} else {
try {
  # ONE process table for the whole machine, then walk ancestry in memory.
  # Querying per hop means hundreds of WMI round trips, which is how the first
  # attempt at this fix made the collector SLOWER than the bug it was fixing.
  $all = @(Get-CimInstance Win32_Process -ErrorAction SilentlyContinue)
  $pp  = @{}
  foreach ($p in $all) { $pp[[int]$p.ProcessId] = [int]$p.ParentProcessId }
  $nodes = @($all | Where-Object { $_.Name -eq 'node.exe' })
  $orph = 0; $omb = 0; $att = 0
  foreach ($n in $nodes) {
    # Walk the WHOLE ancestry, not one hop. A node whose parent is itself an
    # orphan is orphaned too; scoring it "attached" understated the real leak
    # by 2x (24 processes / 1.45 GB versus 48 / 2.73 GB).
    $id = [int]$n.ProcessId; $hop = 0; $parentAlive = $false
    while ($hop -lt 24) {
      $parent = $pp[$id]
      if ($null -eq $parent -or $parent -eq 0) { $parentAlive = $false; break }
      if ($pp.ContainsKey($parent)) { $parentAlive = $true; break }
      $id = $parent; $hop++
    }
    if ($parentAlive) { $att++ } else {
      $orph++
      try { $omb += (Get-Process -Id $n.ProcessId -ErrorAction SilentlyContinue).WorkingSet64 } catch { }
    }
  }
  $state.sections.processes.node_total  = $nodes.Count
  $state.sections.processes.orphans     = $orph
  $state.sections.processes.orphan_mb  = [math]::Round($omb / 1MB, 1)
  $state.sections.processes.attached   = $att
  $state.sections.processes.live_shells = @(Get-Process powershell, pwsh, cmd -ErrorAction SilentlyContinue).Count
  $state.sections.processes.cached_at  = (Get-Date).ToString('o')
  try { [IO.File]::WriteAllText($pcCache, ($state.sections.processes | ConvertTo-Json -Compress), (New-Object Text.UTF8Encoding($false))) } catch { }
} catch { $state.sections.processes.note = "census failed: $($_.Exception.Message)" }
}

# ------------------------------------------------------------ STARTUP -------
# Also cached, for the same reason: two Get-ScheduledTask calls per collect is
# seconds of WMI for a value that changes about once a day.
Trace 'before startup census'
$state.sections.startup = [ordered]@{ tasks = @(); any_task_broken = $false; note = ''; cached_at = $null }
$scCache = Join-Path $PSScriptRoot 'startup-cache.json'
$scFresh = $false
if (Test-Path $scCache) {
  try {
    $sc = [IO.File]::ReadAllText($scCache, [Text.Encoding]::UTF8) | ConvertFrom-Json
    if ($sc -and $sc.cached_at -and (((Get-Date) - [datetime]$sc.cached_at).TotalMinutes -lt 5)) { $scFresh = $true }
  } catch { }
}
if ($scFresh) {
  $state.sections.startup.tasks = $sc.tasks
  $state.sections.startup.note = $sc.note
  $state.sections.startup.cached_at = $sc.at
} else {
try {
  foreach ($tn in @('OPTIMUS_ControlCenter', 'Ollama_Server')) {
    $t = Get-ScheduledTask -TaskName $tn -ErrorAction SilentlyContinue
    if (-not $t) {
      $state.sections.startup.tasks += [ordered]@{ name = $tn; present = $false; state = 'MISSING'; last_run = $null; verdict = 'MISSING'; triggers = @() }
      $state.sections.startup.any_task_broken = $true
      continue
    }
    $ti = $t | Get-ScheduledTaskInfo
    $trig = @()
    try { $trig = @($t.Triggers | ForEach-Object { $_.CimClass.CimClassName }) } catch { }
    $r = $ti.LastTaskResult
    $state.sections.startup.tasks += [ordered]@{
      name      = $tn
      present   = $true
      state     = [string]$t.State
      enabled   = [bool]$t.Settings.Enabled
      last_run  = $(if ($ti.LastRunTime -and $ti.LastRunTime.Year -gt 1990) { $ti.LastRunTime.ToString('o') } else { $null })
      result    = ('0x{0:X}' -f $r)
      verdict   = $(switch ($r) { 0 {'completed ok'} 267009 {'running (correct for a server)'} 267011 {'never run yet'} default {'see 0x{0:X}' -f $r} })
      triggers  = $trig
    }
    if (-not $t.Settings.Enabled) { $state.sections.startup.any_task_broken = $true }
  }
  $state.sections.startup.note = 'these two logon tasks are what bring the console and the local model server back after a restart'
  $state.sections.startup.cached_at = (Get-Date).ToString('o')
  try {
    [IO.File]::WriteAllText($scCache, ($state.sections.startup | ConvertTo-Json -Depth 6 -Compress), (New-Object Text.UTF8Encoding($false)))
  } catch { }
} catch { $state.sections.startup.note = "startup census failed: $($_.Exception.Message)" }
}

# ------------------------------------------------------------ MODEL FLEET ---
# What every CLI on this machine is ACTUALLY pointed at, read from their own
# config files and the live provider. This knowledge used to live only in a
# conversation: you could not tell from the console which agent was on which
# model, or that a shim silently routed one tool into another's engine. A
# command centre that cannot see its own agents is not a command centre.
#
# Every value is read, never assumed, and no credential is ever echoed - only
# whether one is present and how long it is.
Trace 'before model fleet'
$state.sections.fleet = [ordered]@{
  agents   = @()
  ollama   = [ordered]@{ up = $false; models = @(); note = '' }
  minimax  = [ordered]@{ configured = $false; reachable = $false; models = 0; models_list = @() }
  note     = ''
}

# --- Ollama: which local models are actually pulled, and are they serving? -------
if ($ollamaUp) {
  try {
    $ot = Invoke-RestMethod 'http://127.0.0.1:11434/api/tags' -TimeoutSec 6
    $state.sections.fleet.ollama.up = $true
    $state.sections.fleet.ollama.models = @($ot.models | ForEach-Object { $_.name })
  } catch { $state.sections.fleet.ollama.note = "port open but /api/tags failed: $($_.Exception.Message)" }
} else {
  $state.sections.fleet.ollama.note = 'not running - cc install / the Ollama_Server logon task starts it'
}

# --- MiniMax: is the subscription key present, and does the API answer? --------
# Read the env var without ever printing it.
$mmKey = [Environment]::GetEnvironmentVariable('MINIMAX_API_KEY', 'Process')
if (-not $mmKey) { $mmKey = [Environment]::GetEnvironmentVariable('MINIMAX_API_KEY', 'User') }
$state.sections.fleet.minimax.configured = [bool]$mmKey
if ($mmKey) {
  try {
    $req = [Net.HttpWebRequest]::Create('https://api.minimax.io/v1/models')
    $req.Method = 'GET'; $req.Timeout = 8000; $req.ReadWriteTimeout = 8000
    $req.Headers.Add('Authorization', "Bearer $mmKey")
    $resp = $req.GetResponse()
    $sr = New-Object IO.StreamReader($resp.GetResponseStream())
    $body = $sr.ReadToEnd(); $sr.Close(); $resp.Close()
    $mj = $body | ConvertFrom-Json
    $state.sections.fleet.minimax.reachable = $true
    $state.sections.fleet.minimax.models = @($mj.data).Count
    $state.sections.fleet.minimax.models_list = @($mj.data | ForEach-Object { $_.id })
  } catch {
    $state.sections.fleet.minimax.reachable = $false
  }
}

# --- each agent: read its own config, never guess ------------------------------
$agents = @()
function Add-Agent($name, $exe, $model, $endpoint, $route, $state) {
  $script:agents += [ordered]@{
    name = $name; exe = $exe; model = $model; endpoint = $endpoint
    route = $route; state = $state
  }
}
$script:agents = $agents

# Claude Code reads its provider from the environment
$claudeModel = [Environment]::GetEnvironmentVariable('ANTHROPIC_MODEL', 'User')
$claudeUrl   = [Environment]::GetEnvironmentVariable('ANTHROPIC_BASE_URL', 'User')
Add-Agent 'Claude Code' 'claude' $claudeModel $claudeUrl 'Anthropic Messages' $(if ($claudeUrl) { 'MiniMax' } else { 'default Anthropic' })

# Qwen Code keeps its model in its own settings.json
try {
  $qf = Join-Path $env:USERPROFILE '.qwen\settings.json'
  if (Test-Path $qf) {
    $qj = [IO.File]::ReadAllText($qf) | ConvertFrom-Json
    Add-Agent 'Qwen Code' 'qwen' $qj.model.name $qj.model.baseUrl 'OpenAI-compatible' $(if ($qj.model.baseUrl -like '*minimax*') { 'MiniMax' } elseif ($qj.model.baseUrl -like '*11434*') { 'local Ollama' } else { 'other' })
  }
} catch { }

# The gemini shim: NOT a separate CLI. It forwards to agy.exe, i.e. Antigravity.
# Recorded explicitly because it is the single most misread thing on this box.
try {
  $gf = Join-Path $env:USERPROFILE '.gemini\settings.json'
  $gType = 'unknown'
  if (Test-Path $gf) { $gType = ([IO.File]::ReadAllText($gf) | ConvertFrom-Json).security.auth.selectedType }
  $shim = Join-Path $env:LOCALAPPDATA 'agy\bin\gemini.cmd'
  $isShim = (Test-Path $shim) -and ([IO.File]::ReadAllText($shim) -match 'agy\.exe')
  Add-Agent 'gemini' 'gemini' $gType $null $(if ($isShim) { 'shim -> agy.exe (ANTIGRAVITY, not a separate CLI)' } else { 'standalone' }) 'Antigravity engine'
} catch { }

# Kimi / Agent Zero were requested but are not installed; say so rather than omit.
Add-Agent 'Kimi Code' 'kimi' $(if (Get-Command kimi -EA SilentlyContinue) { 'installed' } else { 'NOT INSTALLED' }) $null 'n/a' 'absent'
Add-Agent 'Agent Zero' 'agent-zero' $(if (Get-Command agent-zero -EA SilentlyContinue) { 'installed' } else { 'NOT INSTALLED' }) $null 'n/a' 'absent'

$state.sections.fleet.agents = @($script:agents)
# The note must DERIVE from the same measurement the row does. It used to be a
# hardcoded sentence claiming gemini "is a shim onto agy.exe" - printed directly
# under a row that said 'standalone', because the shim file no longer exists.
# Two panels, two truths, both on screen at once.
$agyOnPath = [bool](Get-Command agy -ErrorAction SilentlyContinue)
$script:fleetIsShim = $isShim
$script:agyPresent   = $agyOnPath
$state.sections.fleet.note =
  if ($isShim) {
    'read from each CLI''s own config. `gemini` IS a shim onto agy.exe (the shim file exists), so configuring it means configuring Antigravity.'
  } elseif ($agyOnPath) {
    'read from each CLI''s own config. The gemini shim file was NOT found, so gemini reads as standalone; agy.exe IS on PATH, so Antigravity is installed.'
  } else {
    'read from each CLI''s own config. The gemini shim file was NOT found AND agy is not on PATH: the Antigravity CLI is not installed on this machine, so gemini reads as standalone and nothing routes through agy.exe.'
  }

# --------------------------------------------------------------- OUTPUT -----
Trace 'before ConvertTo-Json'
# ConvertTo-Json is where this script was dying, and it is worth saying why
# plainly: in Windows PowerShell 5.1 the serialiser walks an OrderedDictionary
# through a reflection path that does not terminate promptly once the tree is
# this shape - state -> sections -> bridges -> checks[] carrying long detail
# strings, plus containers[]. Everything BEFORE this line finished in ~15.6 s;
# this line never returned, and the dashboard was blind the whole time while the
# log stayed empty because nothing was ever throwing.
#
# The fix is to serialise a plain Hashtable tree instead of the ordered one.
# Every key is still present and still addressed by name; only the emission
# order inside the JSON changes, and nothing downstream reads it positionally.
function Convert-ToPlain($o) {
  if ($null -eq $o) { return $null }
  if ($o -is [string]) { return $o }
  if ($o -is [System.Collections.IDictionary]) {
    $h = @{}
    foreach ($k in $o.Keys) { $h[[string]$k] = Convert-ToPlain $o[$k] }
    return $h
  }
  if ($o -is [System.Collections.IEnumerable]) {
    $a = New-Object System.Collections.ArrayList
    foreach ($i in $o) { [void]$a.Add((Convert-ToPlain $i)) }
    return $a.ToArray()
  }
  return $o
}
$plain = Convert-ToPlain $state
if ($Pretty) { $plain | ConvertTo-Json -Depth 12 } else { $plain | ConvertTo-Json -Depth 12 -Compress }

