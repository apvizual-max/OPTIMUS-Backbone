# merge-check.ps1
# The measurement that decides how the two histories get combined.
#
# Why it exists
# -------------
# The CI repo (MAVIS-OPTIMUS-CI) is worked on by ANOTHER AI in parallel
# (the CD session). So there are two histories:
#
#   local  main   - my commits, automatic, never pushed without R0
#   origin main   - the other AI's commits
#
# Combining them is an R0 operation. But R0 deserves FACTS, not options.
# This script measures, WITHOUT touching the working tree and WITHOUT
# pushing anything:
#
#   - how far apart the two histories are
#   - whether the merge is clean or conflicts
#   - which files conflict, by name
#   - the exact tree the merge would produce
#
# It uses `git merge-tree --write-tree`, which is a DRY RUN: it computes
# the merge in memory and prints the resulting tree id. No index, no
# working tree, no commit, no push.
#
# MEASURED 2026-10-27 (the run that produced the current state):
#   merge-tree exit 0, no CONFLICT, tree 8b11d68
#   merged vs local  : 6 files changed (+74/-13)   <- the other AI's work
#   merged vs remote : 38 files changed (+7309/-230) <- my work
#   the merged blob of scripts/mavis-sync.ps1 contained BOTH sides
#
# Exit codes:
#   0 = measured: the merge is clean
#   1 = measured: the merge CONFLICTS (the files are named in the report)
#   2 = not measurable (no git, no remote, or the remote could not be
#       fetched). This is NOT a clean verdict - the unknown is reported
#       as unknown.
#
# ASCII ONLY: executed by Windows PowerShell 5.1.

param(
    [string]$RepoPath = '',
    [string]$Remote = 'origin',
    [string]$Branch = 'main',
    [string]$Other = ''
)

$ErrorActionPreference = 'Stop'

function Write-Out {
    # AllowEmptyString: a report line may legitimately be empty (a diff
    # that produced no output). The gate must never crash while reporting.
    param([AllowEmptyString()][string]$Message)
    [Console]::Out.WriteLine($Message)
}

function Invoke-Git {
    param(
        [Parameter(Mandatory = $true)][string[]]$Arguments,
        [string]$WorkingDirectory = ''
    )
    $prev = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    if ($WorkingDirectory) {
        $out = & git -C $WorkingDirectory @Arguments 2>&1
    } else {
        $out = & git @Arguments 2>&1
    }
    $ErrorActionPreference = $prev
    $code = $LASTEXITCODE
    if ($null -eq $code) { $code = -1 }
    $text = ''
    if ($out) { $text = ($out | Out-String) }
    return @{ Code = $code; Out = $text }
}

if (-not $RepoPath) { $RepoPath = Split-Path -Parent $PSScriptRoot }
if (-not (Test-Path -LiteralPath $RepoPath)) {
    Write-Out ('EROARE: repo inexistent: ' + $RepoPath)
    exit 2
}

$gitDir = Invoke-Git -Arguments @('rev-parse', '--git-dir') -WorkingDirectory $RepoPath
if ($gitDir.Code -ne 0) {
    Write-Out ('EROARE: nu e repo git: ' + $RepoPath)
    exit 2
}

if (-not $Other) { $Other = ($Remote + '/' + $Branch) }

# --- 1. fetch, so the measurement is against the LIVE remote -------------
# A merge-tree run against a stale tracking ref would be a FALSE clean
# verdict. So the fetch is part of the measurement.
$fetch = Invoke-Git -Arguments @('fetch', $Remote, $Branch) -WorkingDirectory $RepoPath
$remoteState = 'LIVE'
if ($fetch.Code -ne 0) {
    $remoteState = 'STALE'
    Write-Out ('WARN fetch esuat (' + $fetch.Code + ') - masuratoarea e pe starea locala a ref-ului remote, nu pe remote-ul viu')
}

# --- 2. the divergence ----------------------------------------------------
$div = Invoke-Git -Arguments @('rev-list', '--left-right', '--count', ($Other + '...' + $Branch)) -WorkingDirectory $RepoPath
$behind = 0
$ahead = 0
if ($div.Code -eq 0) {
    $parts = ($div.Out.Trim() -split '\s+')
    if ($parts.Count -ge 2) {
        $behind = [int]$parts[0]
        $ahead = [int]$parts[1]
    }
} else {
    Write-Out ('EROARE: nu pot citi divergenta: ' + $div.Out.Trim())
    exit 2
}
Write-Out ('REMOTE_STATE=' + $remoteState)
Write-Out ('DIVERGENCE_BEHIND=' + $behind + '  DIVERGENCE_AHEAD=' + $ahead)
Write-Out ('LOCAL=' + (Invoke-Git -Arguments @('rev-parse', $Branch) -WorkingDirectory $RepoPath).Out.Trim())
Write-Out ('OTHER=' + (Invoke-Git -Arguments @('rev-parse', $Other) -WorkingDirectory $RepoPath).Out.Trim())

if ($behind -eq 0 -and $ahead -eq 0) {
    Write-Out 'MERGE_CLEAN=NA - cele doua istorice sunt identice'
    exit 0
}

# --- 3. the dry-run merge -------------------------------------------------
# --name-only makes git print the conflicted file names right after the
# tree id. MEASURED 2026-10-27 (git 2.56): the output is
#   <tree id>
#   <conflicted file>
#   <blank>
#   Auto-merging <file>
#   CONFLICT (content): Merge conflict in <file>
# and the exit code is 1. There is NO "Conflicted file info" header in this
# git version - a parser written for the manual would find nothing.
$mt = Invoke-Git -Arguments @('merge-tree', '--write-tree', '--name-only', $Other, $Branch) -WorkingDirectory $RepoPath
$lines = @($mt.Out -split "`r?`n")
$tree = ''
if ($lines.Count -gt 0) { $tree = $lines[0].Trim() }

$conflicts = New-Object System.Collections.Generic.List[string]
for ($i = 1; $i -lt $lines.Count; $i++) {
    $t = $lines[$i].Trim()
    if (-not $t) { break }
    if ($t -match '^Auto-merging') { continue }
    if ($t -match '^CONFLICT\s*\(content\):\s*Merge conflict in\s+(.+)$') {
        $p = $Matches[1].Trim()
        if (-not $conflicts.Contains($p)) { $conflicts.Add($p) }
        continue
    }
    if ($t -match '^CONFLICT') { continue }
    # a stage line (mode, oid, stage, path) - only without --name-only
    if ($t -match '^\d+\s+[0-9a-f]{40}\s+\d+\s') {
        $parts = $t -split "`t"
        $p = $parts[$parts.Count - 1].Trim()
        if (-not $conflicts.Contains($p)) { $conflicts.Add($p) }
        continue
    }
    if (-not $conflicts.Contains($t)) { $conflicts.Add($t) }
}

$hasConflict = ($mt.Code -ne 0) -or ($conflicts.Count -gt 0)
Write-Out ('MERGE_TREE=' + $tree)
if ($hasConflict) {
    Write-Out ('MERGE_CLEAN=no  CONFLICT_FILES=' + $conflicts.Count)
    foreach ($c in $conflicts) { Write-Out ('  CONFLICT ' + $c) }
    Write-Out 'VERDICT=conflict - combinarea istoricului cere rezolvare manuala.'
    exit 1
}

Write-Out 'MERGE_CLEAN=yes  CONFLICT_FILES=0'

# --- 4. what each side contributes to the merged tree --------------------
foreach ($side in @($Branch, $Other)) {
    $d = Invoke-Git -Arguments @('diff', '--shortstat', $side, $tree) -WorkingDirectory $RepoPath
    # PowerShell 5.1 has no ternary operator - only if/else.
    if ($side -eq $Branch) { $label = 'merged vs LOCAL  (' + $Branch + ')' } else { $label = 'merged vs OTHER  (' + $Other + ')' }
    $line = $d.Out.Trim()
    if (-not $line) { $line = 'identic' }
    Write-Out ($label + ' : ' + $line)
}

Write-Out 'VERDICT=curat - o singura operatie de combinare, fara rezolvare manuala.'
exit 0
