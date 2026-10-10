<#
.SYNOPSIS
  Find, and optionally reap, leaked MCP server processes.

.DESCRIPTION
  Every MCP client spawns its own copy of every server, and nothing reaps them.
  Measured on 2026-10-04: 164 node.exe processes holding 9.1 GB of working set,
  chrome-devtools alone running about twelve copies. That is very likely why the
  Control Center died unattended - the machine was carrying that much dead
  weight while nothing was watching.

  SAFETY MODEL, because this kills processes:
    * dry run by default. Nothing is stopped unless -Apply is passed.
    * the six MCP bridge listeners (ports 3011-3017) are NEVER touched - they
      are the servers Qwen actually connects to, and killing them looks like a
      fix while breaking the thing being fixed.
    * for every server family, the OLDEST instance is kept and the rest are
      candidates. Keeping one is safer than keeping none, and safer than
      killing everything and hoping a client respawns.
    * -KeepAll is the full escape hatch.
    * nothing here runs automatically. It is a tool you invoke on purpose.

.PARAMETER Apply
  Actually stop the processes. Without it, this only reports.

.PARAMETER KeepAll
  Report only; never suggest a kill. Useful for a first look.

.EXAMPLE
  .\reap-mcp.ps1                 # dry run, prints what WOULD go
.EXAMPLE
  .\reap-mcp.ps1 -Apply          # actually reap the duplicates
#>
[CmdletBinding()]
param(
  [switch]$Apply,
  [switch]$KeepAll,
  [int]$Passes = 4
)

$ErrorActionPreference = 'Continue'

# Ports owned by bridges that clients genuinely depend on.
$PROTECTED_PORTS = @(3011, 3012, 3013, 3015, 3016, 3017)

function Get-Family([string]$cmd) {
  # Collapse an npx wrapper, a .bin shim and the real entry point down to the
  # one family name, so "mcp-google-drive" and its npx launcher count as one
  # server rather than as several unrelated things.
  if ($cmd -match 'npx-cli\.js') { return 'npx-wrapper' }
  if ($cmd -match 'node_modules\\([@\w\-\.]+(?:[\\/][\w\-\.]+)*)\\') { return $Matches[1] }
  if ($cmd -match 'AI_Tools\\([\w\-]+\.js)') { return $Matches[1] }
  if ($cmd -match '_npx\\([a-f0-9]+)\\node_modules\\\.\.\\([^\s"\\]+)') { return $Matches[1] }
  return 'other'
}

Write-Host '=== MCP PROCESS REAPER ===' -ForegroundColor Cyan
if ($Apply) { Write-Host 'MODE: APPLY - processes will be stopped' -ForegroundColor Red }
else        { Write-Host 'MODE: DRY RUN - nothing will be stopped (pass -Apply to act)' -ForegroundColor Yellow }
Write-Host ''

$protected = @()
foreach ($p in $PROTECTED_PORTS) {
  $protected += @(Get-NetTCPConnection -LocalPort $p -State Listen -ErrorAction SilentlyContinue)
}
Write-Host ("protected bridge listeners : {0} on ports {1}" -f $protected.Count, ($PROTECTED_PORTS -join ',')) -ForegroundColor DarkGray
Write-Host ''

$all = @(Get-CimInstance Win32_Process -Filter "Name='node.exe'" -ErrorAction SilentlyContinue)
if (-not $all.Count) { Write-Host 'no node.exe processes found' -ForegroundColor Yellow; exit 0 }

# ONE full snapshot of the process table, read once and reused for everything:
# liveness, the parent -> children map, and working sets. MEASURED: a full
# enumeration costs ~2000 ms; a per-node
#   Get-CimInstance Win32_Process -Filter "ParentProcessId=$pid0"
# costs ~1270 ms, so asking per node is what made this tool exceed 180 s and
# print nothing. The snapshot also replaces a per-candidate Get-Process
# fallback, which is a round-trip per row for the same answer.
$snapshot = @()
$byParent = @{}
$wsByPid  = @{}
try {
  $snapshot = @(Get-CimInstance Win32_Process -ErrorAction SilentlyContinue)
  foreach ($p in $snapshot) {
    $pp = [int]$p.ParentProcessId
    if (-not $byParent.ContainsKey($pp)) { $byParent[$pp] = New-Object System.Collections.ArrayList }
    $null = $byParent[$pp].Add($p)
    $wsByPid[[int]$p.ProcessId] = [int64]$p.WorkingSetSize
  }
} catch {
  Write-Host 'could not snapshot the process table - child safety cannot be evaluated' -ForegroundColor Red
  Write-Host 'refusing to act on an unverifiable picture rather than risk live work' -ForegroundColor Yellow
  exit 1
}

# Split by PARENTAGE, not by count.
#
# The first version of this tool called every duplicate a leak and offered to
# kill 140 of them. That was wrong. Measured 2026-10-04: 140 of the 164 node
# processes have a LIVE parent - there are 141 shell processes running, so that
# is one MCP server set per live agent session, which is what SHOULD be running.
# Only 24 are genuinely orphaned (their parent has exited).
#
# Killing the "duplicates" would have severed live MCP connections across every
# active agent while looking exactly like a fix. A process is a leak when its
# parent is GONE, not when it has siblings.
$live = @{}
foreach ($p in $snapshot) { $live[[int]$p.ProcessId] = $true }

$rows = @()
foreach ($p in $all) {
  $cmd = [string]$p.CommandLine
  $pp  = [int]$p.ParentProcessId
  $parentAlive = ($pp -ne 0 -and $live.ContainsKey($pp))
  # A process that still has LIVE CHILDREN is the root of a working tree, not
  # debris. qwen-system\supervisor.js is orphaned at the top and parents six live
  # MCP bridges; guardrail.js parents sixteen. Parentage alone would authorise
  # killing both, and the bridges would die with them. "Orphan" is a diagnosis,
  # not a warrant - it does not by itself authorise the kill.
  $kids = 0
  if ($byParent.ContainsKey([int]$p.ProcessId)) { $kids = $byParent[[int]$p.ProcessId].Count }
  $rows += [pscustomobject]@{
    Pid = $p.ProcessId; Family = (Get-Family $cmd); Started = $p.CreationDate
    MB = [math]::Round($wsByPid[[int]$p.ProcessId] / 1MB, 1); Parent = $pp
    Orphan = (-not $parentAlive); Kids = $kids
    SafeToKill = ((-not $parentAlive) -and $kids -eq 0)
    Cmd = $cmd
  }
}

$orphans = @($rows | Where-Object { $_.Orphan })
$attached = @($rows | Where-Object { -not $_.Orphan })

Write-Host ("total node.exe processes    : {0}" -f $rows.Count)
Write-Host ("  parent STILL RUNNING       : {0,3}  {1,7:N0} MB  legitimate - one set per live agent" -f $attached.Count, (($attached | Measure-Object MB -Sum).Sum))
Write-Host ("  parent HAS EXITED (orphan) : {0,3}  {1,7:N0} MB  the actual leak" -f $orphans.Count, (($orphans | Measure-Object MB -Sum).Sum))
$shells = @(Get-Process powershell, pwsh, cmd -ErrorAction SilentlyContinue)
Write-Host ("  live shell processes       : {0}" -f $shells.Count)
Write-Host ''

Write-Host '=== orphans by family ==='
foreach ($g in ($orphans | Group-Object Family | Sort-Object Count -Descending)) {
  Write-Host ("  {0,-46} {1,2} orphan(s)  {2,7:N0} MB" -f $g.Name, $g.Count, (($g.Group | Measure-Object MB -Sum).Sum)) -ForegroundColor Yellow
}

# Only orphans are ever candidates. A process with a live parent is someone's
# working MCP server and is not ours to stop.
#
# And an orphan is not automatically ours to stop either. qwen-system\supervisor.js
# and guardrail.js are both orphaned at the top AND actively parent live MCP
# bridges (6 and 16 children respectively). Killing either would sever working
# infrastructure while every parentage metric still said "leak". So a candidate
# must be a leaf: parent gone AND no live children. The ones that are orphaned
# but still parenting are reported and RETAINED - that is a decision for a
# human, not something this tool should take by default.
$roots = @()
$candidates = @()
if (-not $KeepAll) {
  $roots    = @($orphans | Where-Object { -not $_.SafeToKill })
  $candidates = @($orphans | Where-Object { $_.SafeToKill })
}
if ($roots.Count -gt 0) {
  $rootMB = ($roots | Measure-Object MB -Sum).Sum
  $rootKids = ($roots | Measure-Object Kids -Sum).Sum
  Write-Host ''
  Write-Host ("RETAINED, not reaped: {0} orphan(s) holding {1:N0} MB but still parenting {2} live process(es)" -f $roots.Count, $rootMB, $rootKids) -ForegroundColor Red
  Write-Host '  a process with live children is the root of a working tree, not debris.' -ForegroundColor Yellow
  $roots | Select-Object -First 10 | ForEach-Object {
    $c = $_.Cmd; if ($c.Length -gt 78) { $c = $c.Substring(0, 78) }
    Write-Host ("    pid {0,-7} {1,5:N0} MB  {2,3} live child(ren)  {3}" -f $_.Pid, $_.MB, $_.Kids, $c) -ForegroundColor DarkYellow
  }
  Write-Host '  killing these would take the MCP servers they supervise with them.' -ForegroundColor Yellow
}

Write-Host ''
if (-not $candidates.Count) {
  if ($KeepAll) { Write-Host 'nothing selected (-KeepAll was set)' -ForegroundColor Gray }
  else { Write-Host 'no duplicates found - nothing to reap' -ForegroundColor Green }
  exit 0
}

# This variable was READ on the line below and ASSIGNED nowhere, so the summary
# printed "26 orphan process(es), about  MB" - a number that was never computed.
# The same class as a measurement nobody takes: the line promised a figure and
# delivered a blank, and a blank reads as "small" rather than "unknown".
$reclaim = ($candidates | Measure-Object MB -Sum).Sum

# Windows does NOT kill a process tree when the parent dies. Reaping an orphan
# node server reclaims the node and leaves every descendant holding its memory -
# and the biggest descendants here are headless Chrome, which is where most of
# the resident cost actually is. Say so, or the reaper looks complete when it
# is only half of the job.
#
# The whole DESCENDANT tree, not just direct children: a headless shell spawns
# its own renderers, so a one-level count understates the leak it is warning
# about - and an undercount on a warning is worse than no warning.
$seen = @{}
foreach ($c in $candidates) { $seen[[int]$c.Pid] = $true }
$frontier = @($candidates | ForEach-Object { [int]$_.Pid })
$kidMB = 0; $kidN = 0

# Build the parent -> children map ONCE - see the snapshot near the top; it is
# built once and reused here. The previous version asked WMI for the children of
# each node:
#
#     Get-CimInstance Win32_Process -Filter "ParentProcessId=$pid0"
#
# MEASURED on this machine: 1270 ms per call. A breadth-first walk over 32
# candidates and their descendants makes 50-100 of those, which is 60-130
# seconds of pure round-trip before the four reaping passes even begin - which
# is why this script used to exceed a 180 s budget and print nothing at all.
# One enumeration costs 2000 ms. The whole walk now costs nothing.
while ($frontier.Count -gt 0) {
  $next = @()
  foreach ($pid0 in $frontier) {
    if (-not $byParent.ContainsKey($pid0)) { continue }
    foreach ($k in $byParent[$pid0]) {
      $kid = [int]$k.ProcessId
      if ($seen.ContainsKey($kid)) { continue }   # guard against a cycle
      $seen[$kid] = $true
      $next += $kid
      $kidN++
      if ($wsByPid.ContainsKey($kid)) { $kidMB += $wsByPid[$kid] }
    }
  }
  $frontier = $next
}

Write-Host ("candidates for reaping    : {0} orphan process(es), about {1:N0} MB" -f $candidates.Count, $reclaim) -ForegroundColor Yellow
Write-Host '  only processes whose parent has EXITED are ever considered'
if ($kidN -gt 0) {
  Write-Host ("  WARNING: {0} child process(es) hold {1:N0} MB and WILL SURVIVE" -f $kidN, ($kidMB/1MB)) -ForegroundColor Red
  Write-Host '           Windows does not kill a tree when the parent dies. Reaping the'
  Write-Host '           node reclaims the node only - the children keep their memory'
  Write-Host '           until they are stopped separately.'
}
Write-Host ''

if (-not $Apply) {
  Write-Host 'DRY RUN. Nothing was stopped. Re-run with -Apply to act.' -ForegroundColor Yellow
  Write-Host ''
  Write-Host 'candidates:'
  $candidates | Select-Object -First 24 | ForEach-Object {
    $c = $_.Cmd; if ($c.Length -gt 88) { $c = $c.Substring(0, 88) }
    Write-Host ("  pid {0,-7} {1,6:N0} MB  parent {2,-7} {3}" -f $_.Pid, $_.MB, $_.Parent, $c)
  }
  Write-Host ''
  # Live figures, not the hardcoded "24 roots / 68 processes" this note carried
  # for months. A number frozen into a closing sentence goes stale silently and
  # then contradicts the live output printed directly above it.
  # $kidN counts descendants of $candidates, which are now leaves - so it is
  # legitimately 0 and says nothing about the RETAINED roots. Using it here
  # printed "hold 0 live processes" directly under a list of roots that were
  # holding forty. The retained count is $rootKids.
  $retainedKids = ($roots | Measure-Object Kids -Sum).Sum
  Write-Host ("NOTE: stopping a parent does NOT stop its children on Windows. The {0} retained" -f $roots.Count) -ForegroundColor DarkGray
  Write-Host ("root(s) listed above hold {0} live process(es) underneath them and are left alone." -f $retainedKids) -ForegroundColor DarkGray
  Write-Host ("The {0} leaf candidate(s) above have no live children, so stopping them orphans nothing." -f $candidates.Count) -ForegroundColor DarkGray
  Write-Host '-Apply repeats the scan until nothing new is safely reapable, up to a few passes.'
  exit 0
}

# Iterate. Killing an orphan reparents its live children onto nothing, which
# makes THEM orphans. A single pass leaves most of the tree behind; the first
# version of this script had that bug written into its own comment.
$pass = 0
$totalStopped = 0
while ($pass -lt $Passes) {
  $pass++
  $rows = @()
  # Re-read the table each pass on purpose: killing a process changes what is
  # orphaned, so a cached snapshot would decide pass 2 from pass 1's world.
  # ONE full enumeration per pass, used for liveness AND the children map.
  $all = @(Get-CimInstance Win32_Process -Filter "Name='node.exe'" -ErrorAction SilentlyContinue)
  if (-not $all.Count) { Write-Host ("pass {0}: no node.exe processes left - done" -f $pass) -ForegroundColor Green; break }
  $aliveAll = @(Get-CimInstance Win32_Process -ErrorAction SilentlyContinue)
  $live = @{}; $kids = @{}; $wsM = @{}
  foreach ($p in $aliveAll) {
    $live[[int]$p.ProcessId] = $true
    $wsM[[int]$p.ProcessId] = [int64]$p.WorkingSetSize
    $pp2 = [int]$p.ParentProcessId
    if (-not $kids.ContainsKey($pp2)) { $kids[$pp2] = 0 }
    $kids[$pp2]++
  }
  $skipped = 0
  foreach ($p in $all) {
    $pp = [int]$p.ParentProcessId
    if ($pp -ne 0 -and $live.ContainsKey($pp)) { continue }
    # Same safety rule as the dry run: parent gone is a diagnosis, not a
    # warrant. A process that still parents live work is the root of a working
    # tree, and stopping it would take that work down with it.
    $id = [int]$p.ProcessId
    if ($kids.ContainsKey($id) -and $kids[$id] -gt 0) { $skipped++; continue }
    $ws = 0
    if ($wsM.ContainsKey($id)) { $ws = $wsM[$id] }
    $rows += [pscustomobject]@{ Pid = $p.ProcessId; MB = [math]::Round($ws/1MB,1) }
  }
  if ($skipped -gt 0) {
    Write-Host ("pass {0}: retained {1} orphan(s) that still parent live work" -f $pass, $skipped) -ForegroundColor DarkYellow
  }
  if (-not $rows.Count) { Write-Host ("pass {0}: nothing left safe to reap - done" -f $pass) -ForegroundColor Green; break }

  $stopped = 0; $failed = 0
  foreach ($c in $rows) {
    if ($protected | Where-Object { $_.OwningProcess -eq $c.Pid }) { continue }
    try { Stop-Process -Id $c.Pid -Force -ErrorAction Stop; $stopped++ }
    catch { $failed++; Write-Host ("  could not stop pid {0}: {1}" -f $c.Pid, $_.Exception.Message) -ForegroundColor DarkYellow }
  }
  $totalStopped += $stopped
  $mb = ($rows | Measure-Object MB -Sum).Sum
  Write-Host ("pass {0}: stopped {1} ({2:N0} MB){3}" -f $pass, $stopped, $mb, $(if ($failed) { ", $failed failed" } else { "" }))
  Start-Sleep -Seconds 3
}

Write-Host ''
Write-Host ("stopped {0} process(es) across {1} pass(es)" -f $totalStopped, $pass) -ForegroundColor Green
Write-Host 'the protected bridge listeners were not touched'
Write-Host ''
Write-Host '=== verifying the bridges still answer /sse ==='
foreach ($port in $PROTECTED_PORTS) {
  $ok = $false
  try {
    $c2 = New-Object Net.Sockets.TcpClient
    $c2.Connect('127.0.0.1', $port)
    $st = $c2.GetStream(); $st.ReadTimeout = 3000
    $req = [Text.Encoding]::ASCII.GetBytes("GET /sse HTTP/1.1`r`nHost: 127.0.0.1:$port`r`nAccept: text/event-stream`r`n`r`n")
    $st.Write($req, 0, $req.Length)
    $buf = New-Object byte[] 64
    $n = $st.Read($buf, 0, 64)
    $head = [Text.Encoding]::ASCII.GetString($buf, 0, [Math]::Max(0, $n))
    $ok = $head -match '200'
    $c2.Close()
  } catch { $ok = $false }
  Write-Host ("  :{0}  {1}" -f $port, $(if ($ok) { 'STILL SERVING' } else { 'NOT ANSWERING' })) `
    -ForegroundColor $(if ($ok) { 'Green' } else { 'Red' })
}
exit 0
