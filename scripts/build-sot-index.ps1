<#
.SYNOPSIS
  Builds the OPTIMUS central Source-Of-Truth (SOT) index for C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard.

.DESCRIPTION
  Popy's rule: one place to reach every custom script, every skill source and
  every connector source, with NO DUPLICATES.

  On this machine symbolic links require elevation, and the agent is not
  elevated. The elevation-free equivalents are used instead:

    directories -> NTFS JUNCTIONS   (transparent, resolve like real dirs)
    files       -> NTFS HARD LINKS  (same inode, zero extra disk)

  A hard link is not a copy: editing the linked file edits the original, and
  deleting one entry leaves the other intact. That satisfies "no duplicates"
  more literally than a shortcut would.

  Safe to re-run: links are only ever CREATED when absent. Nothing is deleted.

  DELETION CONSTRAINT (verified 2026-10-02): an NTFS junction CANNOT be removed
  by this agent. mavis-trash deliberately refuses reparse points, and the shell
  policy blocks both Remove-Item and rmdir. Creating a junction is therefore
  one-way for Mavis, so this script never deletes one -- it checks whether a
  link already points at the correct target and leaves it alone. To repoint a
  junction, delete it from Explorer (right-click > Delete, which removes only
  the link and never the target tree) and re-run this script.

.PARAMETER What
  Which SOT tree to (re)build. Default: all.
#>
[CmdletBinding()]
param(
  [ValidateSet('all', 'scripts', 'skills', 'connectors')]
  [string]$What = 'all'
)

$ErrorActionPreference = 'Stop'
$PROJECTS = 'C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard'
$started  = Get-Date
$stats    = [ordered]@{ junction = 0; hardlink = 0; kept = 0; skipped = 0; missing = 0; conflict = 0 }

function New-JunctionSafe([string]$Link, [string]$Target) {
  if (-not (Test-Path -LiteralPath $Target)) {
    $stats.missing++
    Write-Host "  MISSING TARGET: $Target" -ForegroundColor DarkYellow
    return $false
  }
  if (Test-Path -LiteralPath $Link) {
    $existing = Get-Item -LiteralPath $Link -Force
    $dest = @($existing.Target) -join ''
    if ($existing.LinkType -and $dest -eq $Target) {
      $stats.kept++
      Write-Host ("  [kept]      {0}  ->  {1}" -f (Split-Path $Link -Leaf), $Target) -ForegroundColor DarkGray
      return $true
    }
    # Not auto-resolvable: deleting a junction is unavailable to this agent.
    $stats.conflict++
    Write-Host ("  [CONFLICT]  {0} exists (type={1}, target={2})" -f `
                (Split-Path $Link -Leaf), $existing.LinkType, ($dest -or '<not a link>')) -ForegroundColor Yellow
    Write-Host "              delete it in Explorer, then re-run. Skipped." -ForegroundColor DarkYellow
    return $false
  }
  try {
    New-Item -ItemType Junction -Path $Link -Target $Target -ErrorAction Stop | Out-Null
    $stats.junction++
    Write-Host ("  [junction]  {0}  ->  {1}" -f (Split-Path $Link -Leaf), $Target) -ForegroundColor DarkCyan
    return $true
  } catch {
    $stats.skipped++
    Write-Host ("  [FAILED]    {0} : {1}" -f $Link, $_.Exception.Message) -ForegroundColor Red
    return $false
  }
}

function New-HardLinkSafe([string]$Link, [string]$Target) {
  if (-not (Test-Path -LiteralPath $Target -PathType Leaf)) { $stats.missing++; return $false }
  # Hard links only work inside one volume.
  if ((Split-Path $Link -Qualifier) -ne (Split-Path $Target -Qualifier)) { $stats.skipped++; return $false }
  if (Test-Path -LiteralPath $Link) {
    $existing = Get-Item -LiteralPath $Link -Force
    if ($existing.LinkType -eq 'HardLink' -and $existing.Length -eq (Get-Item $Target).Length) {
      $stats.kept++
      Write-Host ("  [kept]      {0}  (hardlink current)" -f (Split-Path $Link -Leaf)) -ForegroundColor DarkGray
      return $true
    }
    # A hard link is an ordinary file, so mavis-trash CAN remove it safely.
    & rm -- $Link 2>&1 | Out-Null
  }
  try {
    New-Item -ItemType HardLink -Path $Link -Target $Target -ErrorAction Stop | Out-Null
    $stats.hardlink++
    return $true
  } catch {
    $stats.skipped++
    Write-Host ("  [FAILED]    {0} : {1}" -f (Split-Path $Link -Leaf), $_.Exception.Message) -ForegroundColor DarkYellow
    return $false
  }
}

# ---------------------------------------------------------------- scripts ---
function Build-Scripts {
  $root = "$PROJECTS\scripts"
  $ext  = "$root\external"
  $cus  = "$root\hermes-custom"
  New-Item -ItemType Directory -Force -Path $root, $ext, $cus | Out-Null

  Write-Host "`n== SCRIPTS SOT : $root ==" -ForegroundColor Green

  # Whole-folder junctions for the large upstream trees. A per-file link for 96
  # Hermes scripts would bury the handful anyone actually runs.
  $folders = @(
    @{ link = "$ext\hermes-scripts";       target = 'C:\Users\apviz\AppData\Local\hermes\scripts' },
    @{ link = "$ext\hermes-agent-scripts"; target = 'C:\Users\apviz\AppData\Local\hermes\hermes-agent\scripts' },
    @{ link = "$ext\sentinel-operational"; target = "$PROJECTS\SENTINEL_PRIME\02_OPERATIONAL\scripts" },
    @{ link = "$ext\mcp-servers";          target = 'C:\Users\apviz\AppData\Local\hermes\mcp-servers' }
  )
  foreach ($f in $folders) { New-JunctionSafe $f.link $f.target | Out-Null }

  # Per-file hard links for the CUSTOM Hermes scripts. These are the ones
  # Popy actually invokes; they deserve a first-class entry, not a dig.
  $src = 'C:\Users\apviz\AppData\Local\hermes\scripts'
  if (Test-Path $src) {
    $custom = Get-ChildItem $src -File -ErrorAction SilentlyContinue |
              Where-Object { $_.Extension -in '.ps1', '.py', '.sh', '.bat', '.cmd' }
    foreach ($file in $custom) {
      New-HardLinkSafe "$cus\$($file.Name)" $file.FullName | Out-Null
    }
    Write-Host ("  hardlinked {0} custom Hermes scripts into hermes-custom\" -f $custom.Count) -ForegroundColor DarkCyan
  }
}

# ----------------------------------------------------------------- skills ---
function Build-Skills {
  $root = "$PROJECTS\60_SKILLS"
  $lnk  = "$root\_links"
  New-Item -ItemType Directory -Force -Path $root, $lnk | Out-Null
  Write-Host "`n== SKILLS SOT : $root ==" -ForegroundColor Green

  $folders = @(
    @{ link = "$lnk\mavis-skills";    target = 'C:\Users\apviz\.minimax\agents\mavis\skills' },
    @{ link = "$lnk\personal-skills"; target = 'C:\Users\apviz\.minimax\skills' },
    @{ link = "$lnk\hermes-skills";  target = 'C:\Users\apviz\AppData\Local\hermes\skills' },
    @{ link = "$lnk\builtin-skills";  target = 'C:\Users\apviz\.minimax\.builtin-skills' }
  )
  foreach ($f in $folders) { New-JunctionSafe $f.link $f.target | Out-Null }
}

# ------------------------------------------------------------- connectors ---
function Build-Connectors {
  $root = "$PROJECTS\70_CONNECTORS"
  $lnk  = "$root\_links"
  New-Item -ItemType Directory -Force -Path $root, $lnk | Out-Null
  Write-Host "`n== CONNECTORS SOT : $root ==" -ForegroundColor Green

  $folders = @(
    @{ link = "$lnk\hermes-mcp-servers"; target = 'C:\Users\apviz\AppData\Local\hermes\mcp-servers' },
    @{ link = "$lnk\minimax-integrations"; target = 'C:\Users\apviz\.minimax\integrations' },
    @{ link = "$lnk\minimax-bin";         target = 'C:\Users\apviz\.minimax\bin' },
    @{ link = "$lnk\hermes-desktop-plugins"; target = 'C:\Users\apviz\AppData\Local\hermes\desktop-plugins' }
  )
  foreach ($f in $folders) { New-JunctionSafe $f.link $f.target | Out-Null }
}

# ------------------------------------------------------------------- main ---
switch ($What) {
  'scripts'    { Build-Scripts }
  'skills'     { Build-Skills }
  'connectors' { Build-Connectors }
  'all'        { Build-Scripts; Build-Skills; Build-Connectors }
}

$elapsed = (Get-Date) - $started
Write-Host "`n== DONE in $([math]::Round($elapsed.TotalSeconds,1))s ==" -ForegroundColor Cyan
Write-Host ("   junctions : {0}" -f $stats.junction)
Write-Host ("   hardlinks : {0}" -f $stats.hardlink)
Write-Host ("   skipped   : {0}" -f $stats.skipped)
Write-Host ("   missing   : {0}" -f $stats.missing)
