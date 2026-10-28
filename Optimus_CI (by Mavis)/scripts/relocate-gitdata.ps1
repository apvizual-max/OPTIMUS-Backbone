# relocate-gitdata.ps1
# Move a repository's local git data OUT of a synced tree (Google Drive
# mirror), and leave a standard `gitdir:` pointer in its place.
#
# WHY
# Google Drive for Desktop administers the space under its mirror root while
# it synchronises: it materialises, replaces and removes files. A live .git
# directory (index, refs, objects, HEAD) is a collection of ordinary files to
# DriveFS. The repository survives the drive; the git data may not.
#
# The fix is the `gitdir:` pointer: the worktree keeps a small text file, and
# the real git data lives outside the synced tree. This script performs the
# move SAFELY: copy, verify equivalence, THEN remove the original - and only
# if the copy is provably equivalent.
#
# WHAT IT GUARANTEES (all measured, not assumed)
#   - the copy has the same file count and byte total as the source
#   - `git fsck` on the copy exits 0
#   - HEAD, every ref, and the worktree status are IDENTICAL between source
#     and copy
#   - the source is removed only AFTER those checks pass, through the
#     recoverable Trash - never a permanent delete
#   - the pointer file is written LAST, and the result is re-verified after
#
# USAGE
#   powershell -File relocate-gitdata.ps1 -RepoPath <worktree> `
#              -GitDataRoot E:\Google\GitData-Optimus-CI -GitDataName <subfolder>
#
# ONE ROOT PER PROJECT. All git data of a project lives under a single root
# folder, each repository getting a subfolder of it:
#
#   E:\Google\GitData-Optimus-CI\
#     repo\                    gitdir of the project repo
#     clone-MAVIS-CLOUD\        gitdir of a clone
#     clone-MAVIS-OPTIMUS-CI\   gitdir of a clone
#     scratch\                  fixture scratch root
#
# The subfolder name defaults to the repository folder name; pass
# -GitDataName 'repo' for the project repository itself.
#
# ASCII ONLY: executed by Windows PowerShell 5.1.

param(
    [Parameter(Mandatory = $true)][string]$RepoPath,
    [string]$GitDataRoot = 'E:\Google\GitData-Optimus-CI',
    [string]$GitDataName = '',
    [switch]$KeepOriginal
)

$ErrorActionPreference = 'Stop'

function Write-Step { param([string]$m) [Console]::Out.WriteLine('STEP|' + $m) }
function Write-Ok   { param([string]$m) [Console]::Out.WriteLine('OK|' + $m) }
function Write-Bad  { param([string]$m) [Console]::Out.WriteLine('FAIL|' + $m) }

$RepoPath = (Resolve-Path -LiteralPath $RepoPath).Path
$leaf = Split-Path -Leaf $RepoPath
if (-not $GitDataName) { $GitDataName = $leaf }

$src = Join-Path $RepoPath '.git'
$dst = Join-Path $GitDataRoot $GitDataName

if (-not (Test-Path -LiteralPath $src)) { Write-Bad ('no .git at ' + $src); exit 1 }
if (Test-Path -LiteralPath $dst)        { Write-Bad ('destination exists: ' + $dst); exit 1 }

# --- 0. the source must be a real git data directory, not a pointer ------
$srcIsDir = (Get-Item -LiteralPath $src -Force).PSIsContainer
if (-not $srcIsDir) {
    Write-Bad ('the .git here is already a pointer file: ' + (Get-Content -Raw $src).Trim())
    exit 1
}

Write-Step ('source   ' + $src)
Write-Step ('dest     ' + $dst)

# --- 1. copy --------------------------------------------------------------
New-Item -ItemType Directory -Path $dst -Force | Out-Null
& robocopy $src $dst /E /COPY:DAT /DCOPY:T /R:2 /W:1 /NFL /NDL /NJH /NP | Out-Null
if ($LASTEXITCODE -ge 8) { Write-Bad ('robocopy exit ' + $LASTEXITCODE); exit 1 }

$s = Get-ChildItem -LiteralPath $src -Recurse -Force -File | Measure-Object -Property Length -Sum
$d = Get-ChildItem -LiteralPath $dst -Recurse -Force -File | Measure-Object -Property Length -Sum
Write-Ok ('copied {0} files / {1} bytes (source: {2} files / {3} bytes)' -f $d.Count, $d.Sum, $s.Count, $s.Sum)
if ($d.Count -ne $s.Count -or $d.Sum -ne $s.Sum) { Write-Bad 'copy is incomplete'; exit 1 }

# --- 2. verify equivalence ------------------------------------------------
$fsck = & git --git-dir=$dst --work-tree=$RepoPath fsck --no-progress 2>&1
$fsckCode = $LASTEXITCODE
if ($fsckCode -ne 0) {
    Write-Bad ('fsck on the copy exited ' + $fsckCode)
    $fsck | Select-Object -First 10 | ForEach-Object { [Console]::Out.WriteLine('FSCK|' + $_) }
    exit 1
}
Write-Ok 'fsck on the copy: exit 0'

$srcHead = ((& git --git-dir=$src --work-tree=$RepoPath rev-parse HEAD) -join '').Trim()
$dstHead = ((& git --git-dir=$dst --work-tree=$RepoPath rev-parse HEAD) -join '').Trim()
$srcRefs = ((& git --git-dir=$src for-each-ref --format='%(refname) %(objectname)') -join '|')
$dstRefs = ((& git --git-dir=$dst for-each-ref --format='%(refname) %(objectname)') -join '|')
$srcStat = ((& git --git-dir=$src --work-tree=$RepoPath status --porcelain) -join '|')
$dstStat = ((& git --git-dir=$dst --work-tree=$RepoPath status --porcelain) -join '|')

Write-Ok ('HEAD match   ' + ($srcHead -eq $dstHead) + '  (' + $dstHead + ')')
Write-Ok ('refs match   ' + ($srcRefs -eq $dstRefs))
Write-Ok ('worktree     ' + ($srcStat -eq $dstStat))

if ($srcHead -ne $dstHead -or $srcRefs -ne $dstRefs -or $srcStat -ne $dstStat) {
    Write-Bad 'the copy is NOT equivalent to the source - the original is left untouched'
    exit 1
}

# --- 3. remove the original, recoverably ---------------------------------
if ($KeepOriginal) {
    Write-Step 'original kept on request; the pointer was NOT written'
    Write-Bad ('both exist now: ' + $src + ' and ' + $dst)
    exit 1
}

# The original is removed through the RECOVERABLE launcher only. A permanent
# delete is forbidden by the doctrine, so if the launcher is missing the script
# refuses to continue - it never falls back to something irreversible.
$trash = 'C:\Users\apviz\.minimax\bin\mavis-trash.cmd'
if (-not (Test-Path -LiteralPath $trash)) {
    Write-Bad ('recoverable-delete launcher not found: ' + $trash)
    Write-Bad 'refusing to fall back to a permanent delete; the source is untouched'
    exit 1
}

Write-Step 'removing the original through the recoverable launcher (Trash)'
& $trash -- $src | Out-Null
if ($LASTEXITCODE -ne 0 -or (Test-Path -LiteralPath $src)) {
    Write-Bad ('the recoverable delete did not remove the original: ' + $src)
    Write-Bad ('the verified copy is intact at ' + $dst + ' - the original was NOT touched')
    exit 1
}
Write-Ok 'original moved to the Trash (recoverable)'

Write-Step 'writing the pointer'
$pointer = 'gitdir: ' + ($dst -replace '\\', '/')
[System.IO.File]::WriteAllText(
    $src,
    ($pointer + "`n"),
    (New-Object System.Text.UTF8Encoding($false))
)

# --- 4. re-verify from the worktree --------------------------------------
$got = ((& git -C $RepoPath rev-parse --absolute-git-dir) -join '').Trim()
$head = ((& git -C $RepoPath rev-parse HEAD) -join '').Trim()
$status = @(& git -C $RepoPath status --porcelain).Count
Write-Ok ('gitdir now  ' + $got)
Write-Ok ('HEAD now    ' + $head)
Write-Ok ('dirty files ' + $status)

if ($got -ne ($dst -replace '\\', '/')) { Write-Bad 'the pointer does not resolve to the new git data'; exit 1 }
if ($head -ne $srcHead) { Write-Bad 'HEAD changed during the move'; exit 1 }

Write-Ok 'relocation complete and verified'
exit 0
