# publish-ci.ps1
# The one operation that puts the CI work on GitHub - measured, not hoped for.
#
# Why it exists
# -------------
# The CI repository is worked on by another AI in parallel (the CD session),
# so `main` and `origin/main` have two histories. Combining them is the only
# irreversible step left in the CI chain, and it used to be a sequence of
# hand-typed commands. A hand-typed sequence is where mistakes live: a
# rebase that replays 26 commits, a merge with a conflict nobody looked at, a
# push whose success is judged by an exit code.
#
# So the sequence became ONE script, with the measurement in front of the
# mutation:
#
#   1. fetch the live remote          (a verdict on a stale ref is a false verdict)
#   2. measure the merge with merge-check.ps1 - the gate is the oracle
#   3. if the merge is NOT clean -> name the files, change nothing, exit 1
#   4. merge --no-ff (both sides kept), push, then VERIFY by `git ls-remote`
#
# The merge keeps BOTH histories. The remote's commits stay in the history and
# the local commits stay in the history; nothing is rebased away, nothing is
# force-pushed, nothing is dropped.
#
# Usage:
#   powershell -NoProfile -File publish-ci.ps1                 # dry run: measure only
#   powershell -NoProfile -File publish-ci.ps1 -Push           # the R0 operation
#
# -Push IS the R0 expression. It is the one switch that changes the world, and
# it exists so that "publish" is never a side effect of "measure". When the
# repo has a pre-push gate installed, -Push satisfies it with the same
# one-shot marker file that scripts\git-autopush.ps1 -Acord writes
# (PUSH-ACORD inside the git dir). The marker is removed again in a finally
# block, whether the push succeeded or not: an unused agreement left on disk
# is a hole, not a safety.
#
# Exit codes:
#   0 = measured and clean; with -Push, pushed AND verified on the remote
#   1 = the merge CONFLICTS - the files are named; nothing was changed, nothing pushed
#   2 = not measurable / not publishable (no git, no remote, dirty tree);
#       nothing was pushed. This is UNKNOWN, not a clean verdict
#   3 = the push ran, but `git ls-remote` does not show the local HEAD.
#       UNKNOWN - the report says so. It is NOT a success
#   4 = the push was REFUSED (the R0 gate, the remote, or the auth). Measured
#       against the remote: the remote does NOT carry the local HEAD, so
#       nothing was published. The reason git gave is printed.
#
# What it will NEVER do: force push, `git reset --hard`, `git clean`,
# rebase, delete anything, or bypass the pre-push gate.
#
# ASCII ONLY: executed by Windows PowerShell 5.1.

param(
    [string]$RepoPath = '',
    [string]$Remote = 'origin',
    [string]$Branch = 'main',
    [switch]$Push
)

$ErrorActionPreference = 'Stop'

function Write-Out {
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

# NOTE: the resolved path goes into $repo, NOT back into the $RepoPath
# parameter. Assigning a parameter at script scope is the same defect class
# the static probe watches for; a [string] assignment happens to survive
# today, and that is exactly what makes it dangerous - it looks harmless
# until the type changes.
$repo = $RepoPath
if (-not $repo) { $repo = Split-Path -Parent $PSScriptRoot }
if (-not (Test-Path -LiteralPath $repo)) {
    Write-Out ('EROARE: repo inexistent: ' + $repo)
    exit 2
}

$gitDir = Invoke-Git -Arguments @('rev-parse', '--git-dir') -WorkingDirectory $repo
if ($gitDir.Code -ne 0) {
    Write-Out ('EROARE: nu e repo git: ' + $repo)
    exit 2
}

# --- 0a. the path must BE the repository root -----------------------------
# `git rev-parse` walks UP the tree. A path that is not a repository - or a
# SUBDIRECTORY of one - still resolves to the repository above it, and the
# publisher would then merge and push that repository while reporting on the
# path it was given. Measured: a "not a repo" folder inside the CI working
# tree resolved to the CI repo itself and the publisher returned exit 0.
#
# The truth is `git rev-parse --show-toplevel`. If it is not the path given,
# the caller asked for something else than what would be published.
$top = Invoke-Git -Arguments @('rev-parse', '--show-toplevel') -WorkingDirectory $repo
if ($top.Code -ne 0) {
    Write-Out ('EROARE: nu pot determina radacina repo-ului: ' + $repo)
    exit 2
}
$topPath = $top.Out.Trim()
$givenPath = (Resolve-Path -LiteralPath $repo).ProviderPath
# MEASURED 2026-10-27: comparing the two as STRINGS refuses the legitimate
# case. This repository is reached through a junction (C:\...\projects\...
# -> E:\Google\GDrive\...), git prints the PHYSICAL path, and the two strings
# never match - so the publisher refused to publish the very repository it
# was built for. The selfcheck went red with 7 problems for a gate that was
# right about its purpose and blind about how the operator spells the path.
#
# `git rev-parse --show-prefix` answers the same question the way git itself
# sees it: it is EMPTY exactly when the path given IS the repository root,
# and it carries the relative path otherwise. Junctions, drive letters, case
# and slashes are already resolved, because they are git's own question.
$prefix = Invoke-Git -Arguments @('rev-parse', '--show-prefix') -WorkingDirectory $repo
if ($prefix.Code -ne 0) {
    Write-Out ('EROARE: nu pot determina pozitia in repo: ' + $repo)
    exit 2
}
$prefixText = $prefix.Out.Trim()
if ($prefixText -ne '') {
    Write-Out ('EROARE: calea nu e radacina unui repo.')
    Write-Out ('  data   : ' + $givenPath)
    Write-Out ('  repo   : ' + $topPath)
    Write-Out ('  prefix : ' + $prefixText)
    Write-Out 'Publicarea e oprita: altfel s-ar publica alt repo decat cel cerut.'
    exit 2
}

# --- 0. the working tree must be clean (for TRACKED files) ------------------
# A merge on top of uncommitted changes to tracked files produces a result
# nobody can attribute. Files that git does not track cannot collide with the
# merge, so they are reported but do not block.
#
# NOTE: no local variable here may shadow a parameter of this script. A
# variable named like a [switch] parameter turns the assignment of a
# Hashtable into a type error - the operation happens, then the script dies
# reporting failure. PowerShell variable names are case-INSENSITIVE, so
# `$push` collides with `[switch]$Push` and `$remote` with `[string]$Remote`.
# The static probe in publish-ci-selfcheck.ps1 checks exactly that, by AST.
$status = Invoke-Git -Arguments @('status', '--porcelain') -WorkingDirectory $repo
$trackedDirty = @()
$untracked = @()
foreach ($l in @($status.Out -split "`r?`n")) {
    $s = $l.TrimEnd()
    if (-not $s.Trim()) { continue }
    if ($s.StartsWith('??')) { $untracked += $s.Substring(2).Trim() } else { $trackedDirty += $s.Trim() }
}
if ($trackedDirty.Count -gt 0) {
    Write-Out ('EROARE: ' + $trackedDirty.Count + ' fisiere urmarite au schimbari necomitate. Publicarea se opreste aici.')
    foreach ($d in $trackedDirty) { Write-Out ('  ' + $d) }
    exit 2
}
if ($untracked.Count -gt 0) {
    Write-Out ('NOTE: ' + $untracked.Count + ' fisiere fara urmarire in git (nu afecteaza push-ul).')
}

# --- 1. fetch the LIVE remote ---------------------------------------------
# Without the fetch, the measurement is made on a stale ref and can be wrong.
$fetch = Invoke-Git -Arguments @('fetch', $Remote, $Branch) -WorkingDirectory $repo
if ($fetch.Code -ne 0) {
    Write-Out ('EROARE: fetch esuat (' + $fetch.Code + '). Masuratoarea ar fi pe o stare veche; nimic nu s-a impins.')
    Write-Out ($fetch.Out.Trim())
    exit 2
}
Write-Out 'FETCH=LIVE'

# --- 2. the measurement is the gate, not this script -----------------------
$gate = Join-Path $PSScriptRoot 'merge-check.ps1'
if (-not (Test-Path -LiteralPath $gate)) {
    Write-Out ('EROARE: lipseste masuratoarea: ' + $gate)
    exit 2
}
$prev = $ErrorActionPreference
$ErrorActionPreference = 'Continue'
$out = & powershell -NoProfile -File $gate -RepoPath $repo -Remote $Remote -Branch $Branch 2>&1
$ErrorActionPreference = $prev
$gateCode = $LASTEXITCODE
if ($null -eq $gateCode) { $gateCode = -1 }
foreach ($l in @($out)) { Write-Out ('  ' + ([string]$l).Trim()) }

$tree = ''
$behind = 0
$ahead = 0
foreach ($l in @($out)) {
    $s = ([string]$l).Trim()
    if ($s -match '^MERGE_TREE=([0-9a-f]{40})$') { $tree = $Matches[1] }
    if ($s -match '^DIVERGENCE_BEHIND=(\d+)\s+DIVERGENCE_AHEAD=(\d+)$') {
        $behind = [int]$Matches[1]
        $ahead = [int]$Matches[2]
    }
}
Write-Out ('DIVERGENCE_BEHIND=' + $behind + ' DIVERGENCE_AHEAD=' + $ahead)

if ($gateCode -eq 1) {
    Write-Out 'VERDICT=conflict - nimic nu s-a schimbat, nimic nu s-a impins.'
    exit 1
}
if ($gateCode -eq 2) {
    Write-Out 'VERDICT=nemasurabil - nimic nu s-a impins.'
    exit 2
}
if ($gateCode -ne 0) {
    Write-Out ('VERDICT=poarta de masuratoare a esuat (' + $gateCode + ') - nimic nu s-a impins.')
    exit 2
}

if ($behind -eq 0 -and $ahead -eq 0) {
    Write-Out 'VERDICT=identice - nu e nimic de publicat.'
    exit 0
}

# --- 3. dry run: the plan, and nothing else -------------------------------
if (-not $Push) {
    Write-Out ('VERDICT=curat - plan: ' + $ahead + ' commituri locale + ' + $behind + ' commituri remote, fara conflicte.')
    Write-Out 'DRY-RUN: nimic nu s-a schimbat. Cu -Push se combina si se impinge.'
    exit 0
}

# --- 4. the mutation: merge, then push -------------------------------------
$other = ($Remote + '/' + $Branch)
if ($behind -gt 0) {
    $msg = 'merge: integreaza istoricul remote-ului in main (masurat: 0 conflicte, merge-check.ps1)'
    $merge = Invoke-Git -Arguments @('merge', '--no-ff', '-m', $msg, $other) -WorkingDirectory $repo
    if ($merge.Code -ne 0) {
        # A failed merge leaves conflict markers in the working tree. The tree
        # is restored to the state it had before, so the next run starts from a
        # known state instead of from a half-merged one.
        $abort = Invoke-Git -Arguments @('merge', '--abort') -WorkingDirectory $repo
        Write-Out ('EROARE: merge esuat (' + $merge.Code + '). Nimic nu s-a impins.')
        Write-Out ($merge.Out.Trim())
        if ($abort.Code -eq 0) {
            Write-Out 'Arborele a fost readus la starea de dinaintea combinarii (merge --abort).'
        } else {
            Write-Out 'ATENTIE: merge --abort a esuat. Verifica starea arborelui cu: git status'
        }
        exit 1
    }
    Write-Out ('MERGE=ok - ' + $other + ' integrat in ' + $Branch + ' (ambele istorice pastrate)')
}

$head = Invoke-Git -Arguments @('rev-parse', $Branch) -WorkingDirectory $repo
$localSha = $head.Out.Trim()
Write-Out ('LOCAL_HEAD=' + $localSha)

# --- 4b. the R0 gate, satisfied the way this repo expresses agreement ------
# The pre-push hook refuses a push without a one-shot marker. -Push is the
# explicit agreement, so the marker is written here and removed afterwards.
# The hook still runs and still decides - nothing is bypassed.
$marker = ''
$markerWritten = $false
$gitDirAbs = (Invoke-Git -Arguments @('rev-parse', '--absolute-git-dir') -WorkingDirectory $repo).Out.Trim()
if ($gitDirAbs) {
    $hookFile = Join-Path $gitDirAbs 'hooks\pre-push'
    $hooksCfg = Invoke-Git -Arguments @('config', '--get', 'core.hooksPath') -WorkingDirectory $repo
    if ($hooksCfg.Code -eq 0) {
        $hp = $hooksCfg.Out.Trim()
        if ($hp) {
            if (-not [System.IO.Path]::IsPathRooted($hp)) { $hp = Join-Path $repo $hp }
            $hookFile = Join-Path $hp 'pre-push'
        }
    }
    if (Test-Path -LiteralPath $hookFile) {
        $marker = Join-Path $gitDirAbs 'PUSH-ACORD'
        [System.IO.File]::WriteAllText($marker, [string](Get-Date -Format 'o'))
        $markerWritten = $true
        Write-Out 'R0_GATE=marker PUSH-ACORD scris (poarta pre-push ramane activa)'
    }
}

$pushResult = $null
try {
    $pushResult = Invoke-Git -Arguments @('push', $Remote, $Branch) -WorkingDirectory $repo
    Write-Out ('PUSH_EXIT=' + $pushResult.Code)
    if ($pushResult.Code -ne 0) { Write-Out ($pushResult.Out.Trim()) }
} finally {
    if ($markerWritten -and (Test-Path -LiteralPath $marker)) {
        Remove-Item -LiteralPath $marker -Force -ErrorAction SilentlyContinue
    }
}

# --- 5. the verification is the REMOTE, not the exit code ------------------
# ls-remote can answer from a cache and return the previous SHA right after a
# successful push. The measurement is repeated a few times before the verdict
# is declared, exactly like scripts\git-autopush.ps1 does.
$remoteSha = ''
$verified = $false
for ($i = 1; $i -le 4; $i++) {
    $lsRemote = Invoke-Git -Arguments @('ls-remote', $Remote, ('refs/heads/' + $Branch)) -WorkingDirectory $repo
    foreach ($l in @($lsRemote.Out -split "`r?`n")) {
        $s = $l.Trim()
        if ($s) { $remoteSha = ($s -split '\s+')[0]; break }
    }
    if ($remoteSha -and ($remoteSha -eq $localSha)) { $verified = $true; break }
    if ($i -lt 4) { Start-Sleep -Seconds 2 }
}
Write-Out ('REMOTE_HEAD=' + $remoteSha)

if ($verified) {
    $div = Invoke-Git -Arguments @('rev-list', '--left-right', '--count', ($other + '...' + $Branch)) -WorkingDirectory $repo
    Write-Out ('DIVERGENCE_FINAL=' + $div.Out.Trim())
    Write-Out 'VERDICT=publicat - HEAD-ul local este pe remote, verificat prin ls-remote.'
    exit 0
}

if ($pushResult -and ($pushResult.Code -ne 0)) {
    Write-Out 'VERDICT=push refuzat - remote-ul NU arata HEAD-ul local, deci nimic nu a fost publicat. Motivul, cum l-a scris git, e mai sus.'
    exit 4
}

Write-Out 'VERDICT=impins dar NEVERIFICAT - remote-ul nu arata HEAD-ul local. Necunoscut, NU succes.'
exit 3
