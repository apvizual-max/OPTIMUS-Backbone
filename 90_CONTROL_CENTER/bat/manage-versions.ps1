<#
.SYNOPSIS
  Adds a Control Center version snapshot. Never modifies an existing one.

.DESCRIPTION
  Popy's rule: keep the newest five. When the sixth arrives, the FIRST becomes
  dead - but he decides WHEN, not this script. So:

    - a new version is refused if five already exist
    - the script names the oldest and stops
    - nothing is ever deleted automatically

  That is deliberate. "Manage this yourself" means maintain the version list
  and enforce the cap; it does not mean delete his baseline on a timer.

.EXAMPLE
  .\manage-versions.ps1 -Add -Note "descriptive text + Obsidian design"
#>
[CmdletBinding()]
param(
  [string]$Note = '',
  [switch]$List,
  [switch]$PruneOldest   # only run when Popy explicitly says so
)

$ErrorActionPreference = 'Stop'
$CC     = 'C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\90_CONTROL_CENTER'
$VER    = "$CC\backups\versions"
$MAX    = 5

function New-VersionName {
  $nums = @(Get-ChildItem $VER -Directory -EA SilentlyContinue |
            ForEach-Object { if ($_.Name -match '^v(\d+)\.(\d+)$') { [double]("$($Matches[1]).$($Matches[2])") } } |
            Sort-Object)
  if ($nums.Count -eq 0) { return 'v0.1' }
  $next = [math]::Round(($nums[-1] + 0.1), 2)
  return ('v{0:0.0}' -f $next)
}

if ($List -or (-not $Note)) {
  Write-Host "`n  Control Center versions  (cap $MAX, oldest-first)" -ForegroundColor Cyan
  $items = @(Get-ChildItem $VER -Directory -EA SilentlyContinue | Sort-Object Name)
  if ($items.Count -eq 0) { Write-Host "  (none)"; return }
  $i = 0
  foreach ($d in $items) {
    $i++
    $n = @(Get-ChildItem $d.FullName -Recurse -File).Count
    $b = (Get-ChildItem $d.FullName -Recurse -File | Measure-Object Length -Sum).Sum
    $tag = if ($i -eq 1) { '  <- oldest, becomes dead when the 6th arrives' } else { '' }
    Write-Host ("  {0,-8} {1,2} files {2,8:N0} B{3}" -f $d.Name, $n, $b, $tag) -ForegroundColor $(if($i -eq 1){'Yellow'}else{'Gray'})
    $m = Join-Path $d.FullName 'BACKUP.txt'
    if (Test-Path $m) {
      # Older snapshots predate the Note field, so read whichever line exists
      # rather than assuming one is there.
      $line = Get-Content $m | Where-Object { $_ -match '^\s*(Note|Purpose)\s*:' } | Select-Object -First 1
      if ($line) { Write-Host ("           {0}" -f $line.Trim()) -ForegroundColor DarkGray }
    }
  }
  Write-Host ("`n  {0} of {1} used." -f $items.Count, $MAX)
  Write-Host "  Versions are never modified and never auto-deleted.`n"
  return
}

# ----------------------------------------------------------------- add ----
if ($PruneOldest) {
  $items = @(Get-ChildItem $VER -Directory -EA SilentlyContinue | Sort-Object Name)
  if ($items.Count -eq 0) { throw 'nothing to prune' }
  $oldest = $items[0]
  Write-Host ("  deleting OLDEST on Popy's instruction: {0}" -f $oldest.Name) -ForegroundColor Yellow
  & rm -- $oldest.FullName 2>&1 | ForEach-Object { Write-Host "    $_" -ForegroundColor DarkGray }
}

$existing = @(Get-ChildItem $VER -Directory -EA SilentlyContinue)
if ($existing.Count -ge $MAX) {
  $oldest = @($existing | Sort-Object Name)[0]
  Write-Host ("  REFUSING: {0} versions already exist (cap {1})." -f $existing.Count, $MAX) -ForegroundColor Red
  Write-Host ("  The oldest is '{0}'. Tell me to delete it and I will." -f $oldest.Name) -ForegroundColor Yellow
  Write-Host "  Nothing was written. Versions are never auto-deleted.`n"
  exit 1
}

$name = New-VersionName
$dest = Join-Path $VER $name
New-Item -ItemType Directory -Force -Path $dest | Out-Null

Copy-Item "$CC\index.html" $dest -Force
Copy-Item "$CC\README.md"  $dest -Force
foreach ($d in @('api','bat')) {
  New-Item -ItemType Directory -Force -Path "$dest\$d" | Out-Null
  Get-ChildItem "$CC\$d" -File -EA SilentlyContinue |
    Where-Object { $_.Name -ne 'live-state.json' } |
    ForEach-Object { Copy-Item $_.FullName "$dest\$d" -Force }
}

$lines = @(
  "Control Center backup $name",
  "Captured : $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')",
  "Note     : $Note",
  "",
  "This snapshot is FROZEN. It is never edited after creation.",
  "It is a rollback target, not a working copy."
)
[IO.File]::WriteAllText("$dest\BACKUP.txt", ($lines -join "`n"), (New-Object Text.UTF8Encoding($false)))

$after = @(Get-ChildItem $VER -Directory | Sort-Object Name)
Write-Host ("  created {0}   ({1} of {2} versions in use)" -f $name, $after.Count, $MAX) -ForegroundColor Green
Write-Host "  Note: $Note`n"
