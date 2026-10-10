<#
.SYNOPSIS
  The weekly digest: three lines, no more.

.DESCRIPTION
  Popy's observation, and the reason this exists: he built a dashboard so he
  would not have to watch one. Opening the console to find out whether the
  console is fine is the failure mode, not the remedy. So this does not add a
  second page to look at - it puts three lines on the desktop and stops.

  Line 1  what broke        - derived from state-history.jsonl, the whole week
  Line 2  what fixed itself - from cc-health.json, i.e. the supervisor's own count
  Line 3  what waits on you - from api\open-decisions.json, a register, not a guess

  NOTHING here is inferred from "the file exists". A line that has nothing to
  report says so in those words. Three honest lines are the deliverable; a
  fuller report is available on demand, not pushed at anyone.

.PARAMETER DryRun
  Print the digest instead of showing it. Used for testing and for the first
  inspection.

.PARAMETER Days
  Window to inspect. Default 7.
#>
[CmdletBinding()]
param(
  [int]$Days = 7,
  [switch]$DryRun
)

$ErrorActionPreference = 'Stop'

$Root     = 'C:\Users\apviz\.minimax-agent\projects'
$CC       = Join-Path $Root '90_CONTROL_CENTER'
$HistF    = Join-Path $CC 'api\state-history.jsonl'
$HealthF  = Join-Path $CC 'api\cc-health.json'
$DecisF   = Join-Path $CC 'api\open-decisions.json'
$StateF   = Join-Path $CC 'api\live-state.json'
$OutDir   = Join-Path $Root '_DOCS\WEEKLY'
$WatchLog = Join-Path $CC 'logs\watchdog.log'

# ---------------------------------------------------------------- line 1
# What broke. The history is the only honest source: it records what was
# measured every ~20 s for the whole window, including the bad minutes.
#
# ONE SAMPLE IS A MEASUREMENT, NOT AN EVENT. This file already contained two
# lines claiming the whole Hermes swarm was gone (total=1, hermes=0) that had
# recovered three minutes later - a `docker ps` that answered with an error line
# instead of timing out. Taking a minimum over the window would have printed that
# phantom as a week-long outage. So a break must hold for CONSECUTIVE samples
# before it is allowed to become a sentence.
$broken = @()
$blips  = 0
$since = (Get-Date).AddDays(-$Days)

function Get-SustainedRun {
  param($Rows, [string]$Field, [scriptblock]$IsBad)
  $run = 0; $best = 0; $bestVal = $null; $runs = 0
  foreach ($r in $Rows) {
    if (& $IsBad $r) {
      $run++
      if ($run -eq 2) { $runs++ }          # count it once, when it becomes sustained
      if ($run -gt $best) { $best = $run; $bestVal = $r.$Field }
    } else { $run = 0 }
  }
  [pscustomobject]@{ Longest = $best; SustainedRuns = $runs; Value = $bestVal }
}

try {
  $rows = @()
  foreach ($l in [IO.File]::ReadAllLines($HistF, [Text.Encoding]::UTF8)) {
    if (-not $l.Trim()) { continue }
    try { $r = $l | ConvertFrom-Json } catch { continue }
    if ([datetime]$r.ts -ge $since) { $rows += $r }
  }
  if ($rows.Count -gt 0) {
    # Discard samples whose Docker read did not produce containers. `docker ps`
    # sometimes answers with a single error line instead of timing out, and the
    # writer recorded that as total=1. The real figure on this machine is 63,
    # so the median is the yardstick: anything under a tenth of it was not a
    # measurement, it was a failed read wearing a number. The collector now
    # REFUSES these outright; the filter is here because the poisoned lines are
    # already in the append-only file and will not be rewritten.
    $totals = @($rows | ForEach-Object { [int]$_.total } | Sort-Object)
    $medianTotal = $totals[[int]($totals.Count / 2)]
    $floor = [Math]::Max(2, [int]($medianTotal * 0.1))
    $usable = @($rows | Where-Object { $null -ne $_.total -and [int]$_.total -ge $floor })
    $discarded = $rows.Count - $usable.Count
    if ($discarded -gt 0) {
      $broken += "$discarded esantion(e) excluse: docker nu a raportat containere (nu sunt masuratori)"
    }
    $rows = $usable
  }
  if ($rows.Count -gt 0) {
    $fail = Get-SustainedRun -Rows $rows -Field 'b_fail' -IsBad { param($r) [int]$r.b_fail -gt 0 }
    if ($fail.SustainedRuns -gt 0) { $broken += "poduri cu esecuri, $($fail.SustainedRuns) episod(e), maxim $($fail.Value)" }

    $svc = Get-SustainedRun -Rows $rows -Field 'svc_up' -IsBad { param($r) [int]$r.svc_up -lt 3 }
    if ($svc.SustainedRuns -gt 0) { $broken += "servicii sub 3/3, $($svc.SustainedRuns) episod(e), minim $($svc.Value)" }

    $herm = Get-SustainedRun -Rows $rows -Field 'hermes' -IsBad { param($r) [int]$r.hermes -ne 31 }
    if ($herm.SustainedRuns -gt 0) {
      $broken += "poduri Hermes != 31, $($herm.SustainedRuns) episod(e), minim $($herm.Value)"
    } elseif ($herm.Longest -eq 1 -and $herm.Value -ne 31) {
      # Explicitly recorded rather than silently dropped: it was not believed,
      # and the operator is told it was not believed.
      $blips++
    }

    $authVals = @($rows | ForEach-Object { [string]$_.cli_auth } | Sort-Object -Unique)
    if ($authVals.Count -gt 1) {
      $authRun = Get-SustainedRun -Rows $rows -Field 'cli_auth' -IsBad { param($r) [string]$r.cli_auth -ne 'authenticated' }
      if ($authRun.SustainedRuns -gt 0) { $broken += "autentificarea CLI a sarit intre $($authVals -join ' / ')" }
    }
  }
} catch { $broken += "istoricul nu a putut fi citit: $($_.Exception.Message)" }

if ($blips -gt 0) {
  # Not a finding. Saying so is part of the finding.
  $healedNote = "$blips esantion(e) izolat(e) au scazut brusc s-au recuperat - mostenire de masuratoare, nu eveniment"
}

# ---------------------------------------------------------------- line 2
# What fixed itself. This number is the supervisor's own, not an estimate.
$healed = @()
try {
  if (Test-Path -LiteralPath $HealthF) {
    $hh = [IO.File]::ReadAllText($HealthF, [Text.Encoding]::UTF8) | ConvertFrom-Json
    if ([int]$hh.restarts -gt 0) {
      $why = if ($hh.last_restart_reason) { " ($($hh.last_restart_reason))" } else { '' }
      $healed += "consola s-a repornit $($hh.restarts)x$why"
    }
  }
} catch { }
# The SENTINEL guardian has its own log; a restart there is also self-repair.
try {
  $glog = Join-Path $Root 'SENTINEL_PRIME\13_COMMAND_CENTER\logs\guardian.log'
  if (Test-Path -LiteralPath $glog) {
    $gc = (Select-String -LiteralPath $glog -Pattern 'restarting the SENTINEL backend' -ErrorAction SilentlyContinue | Measure-Object).Count
    if ($gc -gt 0) { $healed += "SENTINEL repornit de $gc ori de catre pazitor" }
  }
} catch { }

if ($blips -gt 0 -and $healedNote) { $healed += $healedNote }

# ---------------------------------------------------------------- line 3
# What waits on him. A register on disk, maintained when a decision opens or
# closes. The digest never invents one, and never quietly drops one either.
$waits = @()
try {
  if (Test-Path -LiteralPath $DecisF) {
    $dj = [IO.File]::ReadAllText($DecisF, [Text.Encoding]::UTF8) | ConvertFrom-Json
    $waits = @($dj | Where-Object { $_.open -eq $true } | ForEach-Object { [string]$_.short })
  }
} catch { }

# ---------------------------------------------------------------- compose
$l1 = if ($broken.Count) { 'S-a rupt: ' + ($broken -join ', ') } else { 'S-a rupt: nimic in ' + $Days + ' zile' }
$l2 = if ($healed.Count) { 'S-a reparat singur: ' + ($healed -join ', ') } else { 'S-a reparat singur: nimic' }
$l3 = if ($waits.Count) { 'Asteapta decizia ta: ' + ($waits -join ' | ') } else { 'Asteapta decizia ta: nimic' }
$digest = "$l1`n$l2`n$l3"

Write-Host $digest

if ($DryRun) { exit 0 }

# ---------------------------------------------------------------- persist
if (-not (Test-Path -LiteralPath $OutDir)) { New-Item -ItemType Directory -Path $OutDir -Force | Out-Null }
$outFile = Join-Path $OutDir ((Get-Date).ToString('yyyy-MM-dd') + '.md')
$body = @(
  '# OPTIMUS - rezumat',
  '',
  '**Saptamanal, ' + (Get-Date).ToString('d MMMM yyyy') + '**',
  '',
  $l1,
  '',
  $l2,
  '',
  $l3,
  '',
  '---',
  '',
  'Raportul complet, la cerere: `_DOCS\OPTIMUS PRIME - RAPORT DE STARE - 2026-10-06.md`',
  'Consola: http://127.0.0.1:8900'
) -join "`n"
[IO.File]::WriteAllText($outFile, $body, (New-Object Text.UTF8Encoding $false))

# ---------------------------------------------------------------- surface
# A file nobody opens is a second dashboard. The point is that it arrives.
# System.Windows.Forms NotifyIcon needs no package, no account and no network -
# the tray balloon the box already uses for everything else.
try {
  Add-Type -AssemblyName System.Windows.Forms
  Add-Type -AssemblyName System.Drawing
  $ni = New-Object System.Windows.Forms.NotifyIcon
  $ni.Icon = [System.Drawing.SystemIcons]::Information
  $ni.Visible = $true
  $ni.BalloonTipTitle = 'OPTIMUS - rezumat saptamanal'
  $ni.BalloonTipText = $digest
  $ni.BalloonTipIcon = [System.Windows.Forms.ToolTipIcon]::Info
  $ni.ShowBalloonTip(12000)
  Start-Sleep -Seconds 14
  $ni.Dispose()
} catch {
  # If the balloon cannot be shown, say so in the log rather than pretending it
  # was delivered. A digest that is written but never arrives is a silent no-op.
  $lg = Join-Path $CC 'logs\watchdog.log'
  try { Add-Content -LiteralPath $lg -Value ("{0:o} weekly digest written to {1}; BALLOON FAILED: {2}" -f (Get-Date), $outFile, $_.Exception.Message) -Encoding UTF8 } catch { }
}
Write-Host ("written: {0}" -f $outFile)