<#
.SYNOPSIS
  Independent verification of a full backup, comparing BACKUP against SOURCE.

.DESCRIPTION
  Three traps this script exists to avoid:

  1. The backup script hashes the COPIED file and compares it to the hash it
     recorded FROM THAT SAME COPIED FILE. That proves the copy is stable, not
     that it matches the original. This script hashes SOURCE and BACKUP
     independently and compares the two.

  2. The manifest is written AFTER the file census, so it never lists itself.
     Comparing disk count to manifest count naively reports a 1-file mismatch.
     The manifest file is excluded from the disk side of that comparison.

  3. Live service logs under logs\ are held open by running processes and cannot
     be hashed. An unreadable file is reported as such, never silently counted
     as a pass.

.EXAMPLE
  .\verify-full-backup.ps1 -Name 'FULL_BACKUP_2026-10-03_FINAL'
#>
[CmdletBinding()]
param(
  [string]$Root = 'C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard',
  [string]$Name = 'FULL_BACKUP_2026-10-03_FINAL',
  [int]$Sample = 150
)

$ErrorActionPreference = 'Stop'
$dest = Join-Path $Root $Name
$manifestName = 'BACKUP-MANIFEST.json'

if (-not (Test-Path -LiteralPath $dest)) { throw "No backup at $dest" }

Write-Host "=== INDEPENDENT VERIFICATION ===" -ForegroundColor Cyan
Write-Host "backup : $dest"
Write-Host ""

# ---- 1. the manifest ------------------------------------------------------------
$manifestPath = Join-Path $dest $manifestName
if (-not (Test-Path -LiteralPath $manifestPath)) { throw "$manifestName is missing" }
$mf = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
$mfBytes = (Get-Item -LiteralPath $manifestPath).Length

Write-Host ("manifest claims : {0} files, {1} junctions, {2} hard links, {3:N0} bytes" -f `
  $mf.file_count, $mf.junction_count, $mf.hardlink_count, [int64]$mf.total_bytes)
Write-Host ("manifest parses : YES ({0:N0} bytes of JSON)" -f $mfBytes)
if ($mf.junction_failures) {
  Write-Host ("JUNCTION FAILURES recorded in manifest : {0}" -f @($mf.junction_failures).Count) -ForegroundColor Red
  foreach ($x in $mf.junction_failures) { Write-Host ("    {0}" -f $x) -ForegroundColor Red }
} else {
  Write-Host "junction failures : 0" -ForegroundColor Green
}
Write-Host ""

# ---- 2. what is actually on disk ------------------------------------------------
# Get-ChildItem -Recurse descends into junctions and lands in the external trees,
# so it cannot be used to count junctions. Count FILES only, and drop the manifest.
$onDisk = @(Get-ChildItem -LiteralPath $dest -Recurse -File -Force -ErrorAction SilentlyContinue |
  Where-Object { $_.Name -ne $manifestName })
$diskCount = $onDisk.Count
$diskBytes = ($onDisk | Measure-Object -Property Length -Sum).Sum

Write-Host ("on disk         : {0} files, {1:N0} bytes   (+1 manifest excluded)" -f $diskCount, $diskBytes)
Write-Host ""

Write-Host "--- manifest vs disk ---" -ForegroundColor Yellow
$okCount = ($mf.file_count -eq $diskCount)
$okBytes = ([int64]$mf.total_bytes -eq [int64]$diskBytes)
Write-Host ("  file count   manifest {0} vs disk {1}  -> {2}" -f $mf.file_count, $diskCount, $(if ($okCount) { 'MATCH' } else { 'MISMATCH' })) -ForegroundColor $(if ($okCount) { 'Green' } else { 'Red' })
Write-Host ("  total bytes  manifest {0:N0} vs disk {1:N0}  -> {2}" -f [int64]$mf.total_bytes, $diskBytes, $(if ($okBytes) { 'MATCH' } else { 'MISMATCH' })) -ForegroundColor $(if ($okBytes) { 'Green' } else { 'Red' })
Write-Host ""

# ---- 3. junctions, audited FROM the manifest ------------------------------------
Write-Host "--- junctions (manifest-driven, each path probed) ---" -ForegroundColor Yellow
$j = @($mf.junctions)
$jPresent = 0; $jMissing = @()
foreach ($e in $j) {
  $p = Join-Path $dest $e.path
  $it = Get-Item -LiteralPath $p -Force -ErrorAction SilentlyContinue
  if ($null -ne $it -and $it.LinkType) { $jPresent++ } else { $jMissing += $e.path }
}
Write-Host ("  claimed       : {0}" -f $j.Count)
Write-Host ("  present       : {0}" -f $jPresent) -ForegroundColor $(if ($jPresent -eq $j.Count) { 'Green' } else { 'Red' })
Write-Host ("  MISSING       : {0}" -f $jMissing.Count) -ForegroundColor $(if ($jMissing.Count) { 'Red' } else { 'Green' })
foreach ($m in ($jMissing | Select-Object -First 20)) { Write-Host ("    ABSENT {0}" -f $m) -ForegroundColor Red }
$dead = @($j | Where-Object { -not (Test-Path -LiteralPath (Join-Path $dest $_.path)) })
Write-Host ("  dead targets  : {0}" -f $dead.Count) -ForegroundColor $(if ($dead.Count) { 'Yellow' } else { 'Green' })
Write-Host ""

# ---- 4. THE REAL TEST: source bytes vs backup bytes ------------------------------
Write-Host "--- source vs backup (independent SHA-256 on both sides) ---" -ForegroundColor Yellow
$mfFiles = @($mf.files)
$pick = $mfFiles | Get-Random -Count ([Math]::Min($Sample, $mfFiles.Count))

$match = 0; $mismatch = @(); $noSrc = @(); $noDst = @(); $locked = @()
foreach ($f in $pick) {
  $src = Join-Path $Root $f.rel
  $dst = Join-Path $dest $f.rel
  if (-not (Test-Path -LiteralPath $src)) { $noSrc += $f.rel; continue }
  if (-not (Test-Path -LiteralPath $dst)) { $noDst += $f.rel; continue }
  $hs = $null; $hd = $null
  try { $hs = (Get-FileHash -LiteralPath $src -Algorithm SHA256 -ErrorAction Stop).Hash } catch { $locked += $f.rel; continue }
  try { $hd = (Get-FileHash -LiteralPath $dst -Algorithm SHA256 -ErrorAction Stop).Hash } catch { $locked += $f.rel; continue }
  if ($hs -eq $hd) { $match++ } else { $mismatch += $f.rel }
}
$tested = $match + $mismatch.Count
Write-Host ("  sampled       : {0}" -f $pick.Count)
Write-Host ("  identical     : {0}/{1}" -f $match, $tested) -ForegroundColor $(if ($tested -gt 0 -and $match -eq $tested) { 'Green' } else { 'Red' })
Write-Host ("  MISMATCHED    : {0}" -f $mismatch.Count) -ForegroundColor $(if ($mismatch.Count) { 'Red' } else { 'Green' })
Write-Host ("  not in source : {0}" -f $noSrc.Count) -ForegroundColor $(if ($noSrc.Count) { 'Red' } else { 'Green' })
Write-Host ("  not in backup : {0}" -f $noDst.Count) -ForegroundColor $(if ($noDst.Count) { 'Red' } else { 'Green' })
Write-Host ("  unreadable    : {0}  (live logs held open by a running process)" -f $locked.Count) -ForegroundColor $(if ($locked.Count) { 'Yellow' } else { 'Green' })
foreach ($m in ($mismatch | Select-Object -First 20)) { Write-Host ("    MISMATCH {0}" -f $m) -ForegroundColor Red }
foreach ($m in ($noDst    | Select-Object -First 20)) { Write-Host ("    NO-BACKUP {0}" -f $m) -ForegroundColor Red }
foreach ($m in ($noSrc    | Select-Object -First 20)) { Write-Host ("    NO-SOURCE {0}" -f $m) -ForegroundColor Red }
Write-Host ""

# ---- 5. the deliverable is present ----------------------------------------------
Write-Host "--- key artifacts present in backup ---" -ForegroundColor Yellow
$must = @(
  '90_CONTROL_CENTER\index.html',
  '90_CONTROL_CENTER\api\server.ps1',
  '90_CONTROL_CENTER\api\collect-state.ps1',
  '90_CONTROL_CENTER\api\state-history.jsonl',
  '90_CONTROL_CENTER\backups\versions',
  '95_DESIGN_SOT',
  'scripts\make-full-backup.ps1',
  'scripts\verify-full-backup.ps1'
)
$bad = 0
foreach ($m in $must) {
  $ok = Test-Path -LiteralPath (Join-Path $dest $m)
  if (-not $ok) { $bad++ }
  Write-Host ("  {0}  {1}" -f $(if ($ok) { 'OK  ' } else { 'MISS' }), $m) -ForegroundColor $(if ($ok) { 'Green' } else { 'Red' })
}

# ---- 6. no backup nested inside the backup --------------------------------------
$nested = @(Get-ChildItem -LiteralPath $dest -Force -Directory -ErrorAction SilentlyContinue |
  Where-Object { $_.Name -like 'FULL_BACKUP_*' })
Write-Host ""
Write-Host ("  nested backups inside this backup : {0}" -f $nested.Count) -ForegroundColor $(if ($nested.Count) { 'Red' } else { 'Green' })

Write-Host ""
$verdict = $okCount -and $okBytes -and ($jMissing.Count -eq 0) -and (@($mf.junction_failures).Count -eq 0) `
  -and ($mismatch.Count -eq 0) -and ($noDst.Count -eq 0) -and ($noSrc.Count -eq 0) -and ($tested -gt 0) `
  -and ($match -eq $tested) -and ($bad -eq 0) -and ($nested.Count -eq 0)
if ($verdict) { Write-Host "VERDICT: PASS" -ForegroundColor Green }
else { Write-Host "VERDICT: FAIL" -ForegroundColor Red }
Write-Host ""
Write-Host $dest -ForegroundColor Cyan
