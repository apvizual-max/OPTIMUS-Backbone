<#
.SYNOPSIS
  Frozen version snapshots for the SENTINEL Command Center.

.DESCRIPTION
  A snapshot is FROZEN once written. It is never edited and never moved.

  Maximum five. A sixth is REFUSED, and the script names the oldest and stops.
  It never auto-deletes, because deciding when a baseline dies is Popy's
  decision, not the tool's. -PruneOldest exists so that deletion is always an
  explicit instruction.

  This is the same store already proven at 90_CONTROL_CENTER, adopted rather
  than reinvented.

.PARAMETER List
  Show the snapshots and their notes.

.PARAMETER Note
  Human-readable note describing what changed and why. Required when writing.

.PARAMETER PruneOldest
  Remove the oldest snapshot to make room. Without this, a sixth is refused.
#>
[CmdletBinding()]
param(
  [switch]$List,
  [string]$Note = '',
  [switch]$PruneOldest
)

$ErrorActionPreference = 'Stop'
$ROOT = Split-Path -Parent $PSScriptRoot
$VERSIONS = Join-Path $ROOT 'backups\versions'
$MAX = 5

New-Item -ItemType Directory -Force -Path $VERSIONS | Out-Null

function Get-Snapshots {
  if (-not (Test-Path $VERSIONS)) { return @() }
  return @(Get-ChildItem $VERSIONS -Directory -ErrorAction SilentlyContinue |
    Sort-Object { [int]($_.Name -replace '^v','') })
}

if ($List) {
  $snaps = Get-Snapshots
  Write-Host ''
  Write-Host 'SENTINEL Command Center - frozen snapshots' -ForegroundColor Cyan
  Write-Host ("  root   : {0}" -f $VERSIONS)
  Write-Host ("  count  : {0} of a maximum {1}" -f $snaps.Count, $MAX)
  if (-not $snaps.Count) { Write-Host '  (none yet)' -ForegroundColor DarkGray }
  foreach ($s in $snaps) {
    $noteFile = Join-Path $s.FullName 'NOTE.txt'
    $note = if (Test-Path $noteFile) { (Get-Content $noteFile -Raw).Trim() } else { '(no note)' }
    $bytes = (Get-ChildItem $s.FullName -Recurse -File -ErrorAction SilentlyContinue |
      Measure-Object Length -Sum).Sum
    Write-Host ("  {0,-5} {1,10:N0} B  {2}" -f $s.Name, ($bytes / 1), $note)
  }
  Write-Host ''
  return
}

$snaps = Get-Snapshots

# ---- prune (only ever explicitly) ----
if ($PruneOldest) {
  if ($snaps.Count -lt $MAX) {
    Write-Host ("nothing to prune: {0} of {1} snapshots" -f $snaps.Count, $MAX) -ForegroundColor Yellow
    return
  }
  $oldest = $snaps[0]
  Write-Host ("pruning oldest snapshot: {0}" -f $oldest.Name) -ForegroundColor Yellow
  Write-Host "this was an explicit instruction. Proceeding." -ForegroundColor DarkGray
  Remove-Item $oldest.FullName -Recurse -Force
  $snaps = Get-Snapshots
}

# ---- refuse a sixth ----
if ($snaps.Count -ge $MAX) {
  Write-Host ''
  Write-Host 'REFUSED: the snapshot store is full.' -ForegroundColor Red
  Write-Host ("  maximum : {0}" -f $MAX)
  Write-Host ("  held    : {0}" -f (($snaps | ForEach-Object { $_.Name }) -join ', '))
  Write-Host ("  oldest  : {0}" -f $snaps[0].Name)
  Write-Host ''
  Write-Host 'A baseline is not deleted automatically. Deciding that this one dies is' -ForegroundColor Yellow
  Write-Host 'an operator decision. To prune it explicitly:' -ForegroundColor Yellow
  Write-Host '  .\bat\manage-versions.ps1 -PruneOldest' -ForegroundColor Cyan
  Write-Host ''
  exit 1
}

if ([string]::IsNullOrWhiteSpace($Note)) {
  Write-Host 'refused: -Note is required. A snapshot without a reason is not a baseline.' -ForegroundColor Red
  exit 1
}

# ---- write the snapshot ----
$next = 1
if ($snaps.Count) { $next = ([int]($snaps[-1].Name -replace '^v','')) + 1 }
$name = 'v{0}' -f $next
$dest = Join-Path $VERSIONS $name

New-Item -ItemType Directory -Force -Path $dest | Out-Null
foreach ($item in @('index.html', 'api', 'bat')) {
  $src = Join-Path $ROOT $item
  if (Test-Path $src) { Copy-Item $src -Destination $dest -Recurse -Force }
}
Set-Content -Path (Join-Path $dest 'NOTE.txt') -Value $Note -Encoding UTF8
Set-Content -Path (Join-Path $dest 'FROZEN.txt') `
  -Value ("frozen {0}`nThis snapshot is never edited. To change it, write a new one.`n" -f (Get-Date).ToString('o')) `
  -Encoding UTF8

Write-Host ''
Write-Host ("snapshot {0} written" -f $name) -ForegroundColor Green
Write-Host ("  note    : {0}" -f $Note)
Write-Host ("  store   : {0} of {1}" -f ((Get-Snapshots).Count), $MAX)
Write-Host ''
