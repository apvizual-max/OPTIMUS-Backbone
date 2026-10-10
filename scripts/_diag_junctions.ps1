$ErrorActionPreference = 'Stop'
$Root = 'C:\Users\apviz\.minimax-agent\projects'
$Name = 'FULL_BACKUP_2026-10-03'
$dest = Join-Path $Root $Name
$mf = Get-Content -LiteralPath (Join-Path $dest 'BACKUP-MANIFEST.json') -Raw | ConvertFrom-Json

Write-Host "=== JUNCTION AUDIT (manifest-driven, not a rescan) ===" -ForegroundColor Cyan
$j = @($mf.junctions)
Write-Host ("manifest junction entries : {0}" -f $j.Count)

$exists = 0; $missing = @(); $deadTarget = @(); $duplicatePaths = @()
$seen = @{}
foreach ($e in $j) {
  if ($seen.ContainsKey($e.path)) { $duplicatePaths += $e.path }
  $seen[$e.path] = 1
  $p = Join-Path $dest $e.path
  $it = Get-Item -LiteralPath $p -Force -ErrorAction SilentlyContinue
  if ($null -eq $it) { $missing += $e.path; continue }
  if (-not $it.LinkType) { $missing += ("[not-a-junction] " + $e.path); continue }
  $exists++
  if (-not (Test-Path -LiteralPath $p)) { $deadTarget += $e.path }
}
Write-Host ("present as junction       : {0}" -f $exists) -ForegroundColor Green
Write-Host ("NOT present               : {0}" -f $missing.Count) -ForegroundColor $(if ($missing.Count) { 'Red' } else { 'Green' })
Write-Host ("present but target dead   : {0}" -f $deadTarget.Count) -ForegroundColor $(if ($deadTarget.Count) { 'Yellow' } else { 'Green' })
Write-Host ("duplicate manifest paths  : {0}" -f $duplicatePaths.Count) -ForegroundColor $(if ($duplicatePaths.Count) { 'Red' } else { 'Green' })

if ($missing.Count) {
  Write-Host ""
  Write-Host "first 25 missing:" -ForegroundColor Red
  $missing | Select-Object -First 25 | ForEach-Object { Write-Host "  $_" }
}
if ($duplicatePaths.Count) {
  Write-Host ""
  Write-Host "first 10 duplicates:" -ForegroundColor Red
  $duplicatePaths | Select-Object -First 10 | ForEach-Object { Write-Host "  $_" }
}

Write-Host ""
Write-Host "=== how many junctions does the SOURCE really have? ===" -ForegroundColor Cyan
$srcLinks = @(Get-ChildItem -LiteralPath $Root -Recurse -Force -ErrorAction SilentlyContinue |
  Where-Object { $_.LinkType } | Select-Object -ExpandProperty FullName)
Write-Host ("source junctions found by rescan : {0}" -f $srcLinks.Count)
$srcTop = @(Get-ChildItem -LiteralPath $Root -Force | Where-Object { $_.LinkType })
Write-Host ("source junctions at top level    : {0}" -f $srcTop.Count)

Write-Host ""
Write-Host "=== files in backup that the manifest does not list ===" -ForegroundColor Cyan
$known = New-Object System.Collections.Generic.List[string]
foreach ($f in @($mf.files)) { $known.Add($f.rel) }
Write-Host ("manifest file entries : {0}" -f $known.Count)
$extra = 0
Get-ChildItem -LiteralPath $dest -Recurse -File -Force -ErrorAction SilentlyContinue | ForEach-Object {
  $rel = $_.FullName.Substring($dest.Length + 1)
  if (-not $known.Contains($rel)) { $extra++; if ($extra -le 15) { Write-Host ("  unlisted: {0}" -f $rel) } }
}
Write-Host ("total unlisted files  : {0}" -f $extra)
