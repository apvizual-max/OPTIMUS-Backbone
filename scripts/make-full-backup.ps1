<#
.SYNOPSIS
  Full backup of the OPTIMUS projects root, taken from inside that same root.

.DESCRIPTION
  Popy's instruction: go into the root folder, create a new isolated folder,
  and put a full backup of everything inside it, so there is a restore point
  that can be inspected on the hard disk.

  Three things this must get right, none of them obvious:

  1. RECURSION. The backup lives INSIDE the folder it is backing up. Without an
     explicit exclusion the copy walks into itself forever. Every pass skips any
     path that is the backup root or lives under it.

  2. JUNCTIONS. There are 13 of them, and they point OUTSIDE this root - the
     1159 personal skills, the Hermes script trees, the MCP servers. Copying
     their CONTENT would drag in tens of thousands of foreign files and bloat
     the archive with data that does not live here. Copying nothing would lose
     the structure. So each junction is RECREATED as a junction in the backup,
     and every target is written to the manifest so a restore knows where it
     pointed. The SOT design survives, and the manifest carries the meaning.

  3. PROOF. A backup nobody can trust is decoration. Every copied file gets a
     SHA-256 recorded, and the run re-reads a sample afterwards to prove the
     bytes on disk are the bytes that were promised.

.EXAMPLE
  .\make-full-backup.ps1
#>
[CmdletBinding()]
param(
  [string]$Root = 'C:\Users\apviz\.minimax-agent\projects',
  [string]$Name = '',
  [int]$VerifySample = 40,
  [switch]$AllowExisting
)

$ErrorActionPreference = 'Stop'

if (-not $Name) { $Name = 'FULL_BACKUP_' + (Get-Date -Format 'yyyy-MM-dd_HHmmss') }
$dest = Join-Path $Root $Name

if (Test-Path -LiteralPath $dest) {
  if (-not $AllowExisting) {
    throw "Backup destination already exists: $dest. Choose a different -Name, or pass -AllowExisting to refresh it in place."
  }
  Write-Host "refreshing existing destination in place: $dest" -ForegroundColor Yellow
} else {
  New-Item -ItemType Directory -Force -Path $dest | Out-Null
}
Write-Host "destination: $dest" -ForegroundColor Cyan
Write-Host ""

$started = Get-Date
$files   = New-Object System.Collections.Generic.List[object]
$dirs    = New-Object System.Collections.Generic.List[string]
$links   = New-Object System.Collections.Generic.List[object]
$skipped = New-Object System.Collections.Generic.List[string]
$failures = New-Object System.Collections.Generic.List[string]
$hardlinks = New-Object System.Collections.Generic.List[string]

# A REDIRECT points somewhere else: a Junction, or a symlink to a directory.
# A HARD LINK does not. A hard link is an ordinary file that happens to share an
# inode with another file; it has real content living here and it MUST be copied.
# PowerShell reports LinkType = 'HardLink' for it, which is truthy - so testing
# `if ($item.LinkType)` silently classifies 76 real files as junctions and drops
# them from the backup while the manifest claims they were recreated.
function Is-Redirect($item) {
  if (-not $item.LinkType) { return $false }
  if ($item.LinkType -eq 'Junction') { return $true }
  if ($item.LinkType -eq 'SymbolicLink' -and $item.PSIsContainer) { return $true }
  return $false
}

function Get-LinkTarget($item) {
  $t = $item.Target
  if ($null -eq $t) { return '' }
  if ($t -is [array]) { return ($t -join '') }
  return [string]$t
}

# Create the junction, but be idempotent. New-Item -ItemType Junction removes an
# existing entry first, and a junction that resolves to a populated directory
# looks "not empty" - so re-running against an existing backup fails on all 13.
# If the junction is already there and already points at the right target, that
# is the desired end state: keep it. If something else is in the way, say so.
function Ensure-Junction($path, $target) {
  $ex = Get-Item -LiteralPath $path -Force -ErrorAction SilentlyContinue
  if ($null -ne $ex) {
    if ($ex.LinkType -eq 'Junction' -and (Get-LinkTarget $ex) -eq $target) { return 'kept' }
    throw "destination exists but is not the expected junction: $path (LinkType=$($ex.LinkType) target=$(Get-LinkTarget $ex))"
  }
  New-Item -ItemType Junction -Path $path -Target $target | Out-Null
  return 'created'
}

# Everything directly under the root, except this backup folder AND except any
# other restore point. A backup must never contain another backup: it doubles
# the size, and worse, a stale/defective earlier run would be archived inside
# the new one as if it were current truth.
#
# The pattern matters. It matched only FULL_BACKUP_* until a run used the name
# VERSION_REFERINTA_*, which slipped straight through - and each backup then
# contained the previous one. Measured across three runs: 1,737 -> 3,497 ->
# 7,005 files, 36 MB -> 73 MB -> 147 MB. Doubling, every time, for no gain.
$top = Get-ChildItem -LiteralPath $Root -Force | Where-Object {
  ($_.FullName -ne $dest) -and
  -not ($_.PSIsContainer -and (
        $_.Name -like 'FULL_BACKUP_*' -or
        $_.Name -like 'VERSION_REFERINTA_*' -or
        $_.Name -like 'RESTORE_POINT_*'))
}

foreach ($item in $top) {
  if (Is-Redirect $item) {
    # a junction sitting at the top level
    $t = Join-Path $dest $item.Name
    $target = Get-LinkTarget $item
    Ensure-Junction $t $target | Out-Null
    $links.Add([pscustomobject]@{ path = $item.Name; target = $target; note = 'recreated as a junction, not copied' })
    continue
  }
  if (-not $item.PSIsContainer) {
    Copy-Item -LiteralPath $item.FullName -Destination (Join-Path $dest $item.Name) -Force
    $files.Add([pscustomobject]@{ rel = $item.Name; bytes = $item.Length })
    if ($item.LinkType -eq 'HardLink') { $hardlinks.Add($item.Name) }
    continue
  }

  # A real directory: walk it, but never into a junction and never into $dest.
  New-Item -ItemType Directory -Force -Path (Join-Path $dest $item.Name) | Out-Null
  $dirs.Add($item.Name)
  $stack = New-Object System.Collections.Stack
  $stack.Push($item.FullName)
  while ($stack.Count) {
    $cur = $stack.Pop()
    foreach ($c in (Get-ChildItem -LiteralPath $cur -Force -EA SilentlyContinue)) {
      $rel = $c.FullName.Substring($Root.Length + 1)
      if ($c.FullName -eq $dest -or $rel.StartsWith($Name)) { $skipped.Add($rel); continue }
      if (Is-Redirect $c) {
        $lt = Join-Path $dest $rel
        New-Item -ItemType Directory -Force -Path (Split-Path $lt -Parent) | Out-Null
        $target = Get-LinkTarget $c
        try {
          Ensure-Junction $lt $target | Out-Null
          $links.Add([pscustomobject]@{ path = $rel; target = $target; note = 'recreated as a junction, not copied' })
        } catch {
          # Loud, never silent. A junction the manifest claims but that is absent
          # from disk is a backup that lies to whoever restores it.
          $failures.Add("$rel :: $($_.Exception.Message)")
        }
        continue
      }
      if ($c.PSIsContainer) {
        New-Item -ItemType Directory -Force -Path (Join-Path $dest $rel) | Out-Null
        $stack.Push($c.FullName)
      } else {
        Copy-Item -LiteralPath $c.FullName -Destination (Join-Path $dest $rel) -Force
        $files.Add([pscustomobject]@{ rel = $rel; bytes = $c.Length })
        if ($c.LinkType -eq 'HardLink') { $hardlinks.Add($rel) }
      }
    }
  }
}

# ------------------------------------------------------------------ manifest --
$hashed = New-Object System.Collections.Generic.List[object]
foreach ($f in $files) {
  $p = Join-Path $dest $f.rel
  if (-not (Test-Path -LiteralPath $p)) { continue }
  $hashed.Add([pscustomobject]@{
    rel   = $f.rel
    bytes = (Get-Item -LiteralPath $p).Length
    sha   = (Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash
  })
}

$totalBytes = ($hashed | Measure-Object -Property bytes -Sum).Sum
$manifest = [ordered]@{
  backup_name       = $Name
  created           = (Get-Date).ToString('yyyy-MM-dd HH:mm:ss zzz')
  source_root       = $Root
  file_count        = $hashed.Count
  directory_count   = $dirs.Count
  junction_count    = $links.Count
  hardlink_count    = $hardlinks.Count
  hardlink_policy   = 'hard links are ordinary files that share an inode; they carry real content in this root, so they were copied as normal files rather than recreated as junctions'
  total_bytes       = [int64]$totalBytes
  recursion_guard   = "the backup folder '$Name' was excluded from its own copy"
  junction_policy   = 'junctions point outside this root, so they are recreated as junctions rather than copied; their targets are listed below so a restore can repoint them'
  junction_failures = $failures.ToArray()
  skipped           = $skipped.ToArray()
  junctions         = $links.ToArray()
  files             = $hashed.ToArray()
}
$manifest | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $dest 'BACKUP-MANIFEST.json') -Encoding UTF8

# ------------------------------------------------------------------- verify --
$verify = New-Object System.Collections.Generic.List[object]
$sample = $hashed | Get-Random -Count ([Math]::Min($VerifySample, $hashed.Count))
foreach ($f in $sample) {
  $p = Join-Path $dest $f.rel
  $actual = if (Test-Path -LiteralPath $p) { (Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash } else { 'MISSING' }
  $verify.Add([pscustomobject]@{
    rel    = $f.rel
    match  = ($actual -eq $f.sha)
    actual = $(if ($actual -eq $f.sha) { 'same' } else { $actual })
  })
}
$ok = @($verify | Where-Object { $_.match }).Count
Write-Host "=== BACKUP COMPLETE ===" -ForegroundColor Green
Write-Host ("  files        : {0}" -f $hashed.Count)
Write-Host ("  directories  : {0}" -f $dirs.Count)
Write-Host ("  junctions    : {0}  (recreated, not copied)" -f $links.Count)
Write-Host ("  hard links   : {0}  (copied as real files)" -f $hardlinks.Count)
if ($failures.Count) {
  Write-Host ("  JUNCTION FAILURES: {0}" -f $failures.Count) -ForegroundColor Red
  foreach ($f in $failures) { Write-Host ("    {0}" -f $f) -ForegroundColor Red }
}
Write-Host ("  total size   : {0:N0} bytes" -f $totalBytes)
Write-Host ("  manifest     : {0}\BACKUP-MANIFEST.json" -f $dest)
Write-Host ("  spot verify  : {0}/{1} sampled files hash-identical" -f $ok, $verify.Count) -ForegroundColor $(if ($ok -eq $verify.Count) { 'Green' } else { 'Yellow' })
$elapsed = (Get-Date) - $started
Write-Host ("  elapsed      : {0:N1}s" -f $elapsed.TotalSeconds)
Write-Host ""
Write-Host $dest -ForegroundColor Cyan
