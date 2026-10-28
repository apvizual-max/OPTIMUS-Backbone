# publish-ci-selfcheck.ps1
# The gate for the gate: it proves that publish-ci.ps1 does what it claims -
# and that it REFUSES when it must.
#
# The probes build real repositories under state/tmp/ and let git decide:
#
#   1  dry run on a clean divergence -> exit 0, and the REMOTE is untouched
#   2  push on a clean divergence     -> exit 0, the remote shows the local HEAD,
#                                       and the merge KEPT both histories
#   3  push on a CONFLICT            -> exit 1, the remote is untouched, the
#                                       local tree has no merge commit
#   4  a path that is not a repo     -> exit 2 (not measurable, not a clean verdict)
#   5  the REAL repository, dry run  -> exit 0, and the real remote is untouched
#   6  STATIC: no script-scope variable may shadow a parameter
#   7  a push REFUSED by a hook      -> exit 4, the remote is untouched
#   8  a tracked file changed        -> exit 2 (blocked), the remote untouched
#   9  an UNTRACKED file only        -> exit 0 (not blocked, reported as NOTE)
#
# Probe 3 is the important one for safety: a publisher that pushes a
# conflicted merge would be worse than no publisher at all.
#
# Probe 6 is the one that catches a defect that was actually MEASURED: a
# local variable named like a parameter of the script ($push vs [switch]$Push,
# $remote vs [string]$Remote). PowerShell variable names are case-
# insensitive, so assigning a Hashtable to $push is a type error that fires
# AFTER the push has already run - the operation happens, the report says it
# failed. The probe is falsified on a COPY: a deliberately broken copy of the
# publisher MUST be detected, otherwise the probe proves nothing.
#
# Exit codes:
#   0 = everything measured and true
#   1 = at least one probe failed
#   2 = the gate could not run at all
#
# ASCII ONLY: executed by Windows PowerShell 5.1.

param(
    [string]$ScriptsDir = '',
    [string]$RealRoot = ''
)

$ErrorActionPreference = 'Stop'

if (-not $ScriptsDir) { $ScriptsDir = $PSScriptRoot }
if (-not (Test-Path -LiteralPath $ScriptsDir)) {
    Write-Output ('EROARE: director inexistent: ' + $ScriptsDir)
    exit 2
}

$Publisher = Join-Path $ScriptsDir 'publish-ci.ps1'
if (-not (Test-Path -LiteralPath $Publisher)) {
    Write-Output ('EROARE: lipseste ' + $Publisher)
    exit 2
}
$RealRootDefault = Split-Path -Parent $ScriptsDir
if (-not $RealRoot) { $RealRoot = $RealRootDefault }

# The fixtures are git repositories of their own. They are built OUTSIDE the
# Google Drive mirror, so DriveFS never administers a live .git directory.
# MEASURED 2026-10-27: 90+ .git directories used to live inside the mirror.
$ScratchLib = Join-Path $PSScriptRoot 'git-scratch.ps1'
if (-not (Test-Path -LiteralPath $ScratchLib)) {
    Write-Output ('EROARE: lipseste scripts\git-scratch.ps1: ' + $ScratchLib)
    exit 2
}
. $ScratchLib
$ScratchRoot = Assert-ScratchOutsideMirror -ScratchRoot (Get-GitScratchRoot -ProjectRoot $RealRootDefault) -ProjectRoot $RealRootDefault

# FIXTURES MUST NOT SURVIVE A RUN.
# Measured defect: the fixture root was a fixed path, so `git clone` into an
# EXISTING directory failed (destination path already exists) and the probes
# measured the PREVIOUS run's repositories. Probe 2 then reported
# "remote_miscat=False" for a push that had actually worked - the remote was
# already at the merge commit from the earlier run.
#
# A test that measures yesterday's fixture is not a test. Each run gets its
# own directory, and the previous run's directories are removed - only the
# ones this script itself created (the name prefix is checked).
#
# The cleanup block lives AFTER the Write-Out definition: PowerShell resolves
# a function at CALL time, so a cleanup that calls Write-Out before the
# function exists dies with "The term 'Write-Out' is not recognized" - and
# that is a crash of the GATE, not a report. Measured 2026-10-27.
$TmpRootBase = Join-Path $ScratchRoot 'publish-selfcheck'
$runStamp = (Get-Date -Format 'yyyyMMdd-HHmmss-fff')
$TmpRoot = Join-Path $TmpRootBase ('run-' + $runStamp)

$problems = 0
$falsified = 0
$probeNo = 0

function Write-Out {
    param([AllowEmptyString()][string]$Message)
    [Console]::Out.WriteLine($Message)
}

if (Test-Path -LiteralPath $TmpRootBase) {
    # The old fixture runs are moved to the RECOVERABLE trash, not deleted.
    # That is the same rule the whole project uses (mavis-trash), and it is
    # also what makes the cleanup work here: the fixture directory carries
    # Attributes=ReadOnly,Directory (measured 2026-10-27) because DriveFS
    # created it, and a plain filesystem delete is refused on a read-only
    # directory. The trash launcher moves the whole tree, read-only files and
    # all, and it is recoverable if the fixture ever needs to be inspected.
    $trashExe = Join-Path $env:USERPROFILE '.minimax\bin\mavis-trash.cmd'
    foreach ($old in @(Get-ChildItem -LiteralPath $TmpRootBase -Directory -Force -ErrorAction SilentlyContinue)) {
        if ($old.Name -like 'run-*') {
            if (Test-Path -LiteralPath $trashExe) {
                $prev = $ErrorActionPreference
                $ErrorActionPreference = 'Continue'
                & $trashExe -- $old.FullName 2>&1 | Out-Null
                $ErrorActionPreference = $prev
                if (Test-Path -LiteralPath $old.FullName) {
                    Write-Out ('WARN nu pot curata fixture-ul vechi: ' + $old.FullName)
                }
            } else {
                Write-Out ('WARN nu pot curata fixture-ul vechi (lipseste ' + $trashExe + '): ' + $old.FullName)
            }
        }
    }
}

function Invoke-Git {
    param(
        [Parameter(Mandatory = $true)][string]$WorkingDirectory,
        [Parameter(Mandatory = $true)][string[]]$Arguments
    )
    $prev = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    $out = & git -C $WorkingDirectory @Arguments 2>&1
    $ErrorActionPreference = $prev
    $code = $LASTEXITCODE
    if ($null -eq $code) { $code = -1 }
    $text = ''
    if ($out) { $text = ($out | Out-String) }
    return @{ Code = $code; Out = $text }
}

function Test-Probe {
    param(
        [Parameter(Mandatory = $true)][string]$Label,
        [Parameter(Mandatory = $true)][bool]$Ok,
        [Parameter(Mandatory = $true)][string]$Detail
    )
    $script:probeNo++
    if ($Ok) {
        $script:falsified++
        Write-Out ('OK   proba-' + $script:probeNo + ' ' + $Label + ' -> ' + $Detail)
    } else {
        $script:problems++
        Write-Out ('FAIL proba-' + $script:probeNo + ' ' + $Label + ' -> ' + $Detail)
    }
}

# Builds a repo with a REAL remote: the remote is ahead on one file (sideB),
# the local branch is ahead on another (or on the SAME line, for the conflict).
function New-Fixture {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][bool]$Conflict
    )
    $bare = Join-Path $TmpRoot ($Name + '.git')
    $work = Join-Path $TmpRoot $Name
    $null = Invoke-Git -WorkingDirectory $TmpRoot -Arguments @('init', '--bare', '-q', '-b', 'main', $bare)
    $null = Invoke-Git -WorkingDirectory $TmpRoot -Arguments @('clone', '-q', $bare, $work)
    $null = Invoke-Git -WorkingDirectory $work -Arguments @('config', 'user.email', 'probe@example.invalid')
    $null = Invoke-Git -WorkingDirectory $work -Arguments @('config', 'user.name', 'Probe')
    $enc = New-Object System.Text.UTF8Encoding($false)

    # base, published on main
    [System.IO.File]::WriteAllText((Join-Path $work 'seed.txt'), "seed`n", $enc)
    $null = Invoke-Git -WorkingDirectory $work -Arguments @('add', '-A')
    $null = Invoke-Git -WorkingDirectory $work -Arguments @('commit', '-q', '-m', 'seed')
    $null = Invoke-Git -WorkingDirectory $work -Arguments @('push', '-q', 'origin', 'main')

    # the remote moves ahead, on sideB, published onto main
    $null = Invoke-Git -WorkingDirectory $work -Arguments @('checkout', '-q', '-b', 'sideB', 'origin/main')
    if ($Conflict) {
        [System.IO.File]::WriteAllText((Join-Path $work 'seed.txt'), 'din sideB', $enc)
    } else {
        [System.IO.File]::WriteAllText((Join-Path $work 'b.txt'), 'din sideB', $enc)
    }
    $null = Invoke-Git -WorkingDirectory $work -Arguments @('add', '-A')
    $null = Invoke-Git -WorkingDirectory $work -Arguments @('commit', '-q', '-m', 'side change')
    $null = Invoke-Git -WorkingDirectory $work -Arguments @('push', '-q', 'origin', 'sideB:main')
    $null = Invoke-Git -WorkingDirectory $work -Arguments @('checkout', '-q', 'main')

    # the local branch moves ahead too
    if ($Conflict) {
        [System.IO.File]::WriteAllText((Join-Path $work 'seed.txt'), 'din main', $enc)
    } else {
        [System.IO.File]::WriteAllText((Join-Path $work 'a.txt'), 'din main', $enc)
    }
    $null = Invoke-Git -WorkingDirectory $work -Arguments @('add', '-A')
    $null = Invoke-Git -WorkingDirectory $work -Arguments @('commit', '-q', '-m', 'main change')

    return @{ Work = $work; Bare = $bare }
}

function Invoke-Publisher {
    param(
        [Parameter(Mandatory = $true)][string]$RepoPath,
        [switch]$Push
    )
    $prev = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    $args = @('-NoProfile', '-File', $Publisher, '-RepoPath', $RepoPath, '-Remote', 'origin', '-Branch', 'main')
    if ($Push) { $args += '-Push' }
    $out = & powershell @args 2>&1
    $ErrorActionPreference = $prev
    $code = $LASTEXITCODE
    if ($null -eq $code) { $code = -1 }
    $text = ''
    if ($out) { $text = ($out | Out-String) }
    return @{ Code = $code; Out = $text }
}

function Get-RemoteHead {
    param([Parameter(Mandatory = $true)][string]$Bare)
    $r = Invoke-Git -WorkingDirectory $Bare -Arguments @('rev-parse', 'main')
    if ($r.Code -ne 0) { return '' }
    return $r.Out.Trim()
}

# --- the static probe: a script-scope variable must not shadow a parameter --
# Uses the PowerShell AST, so it reads what the parser actually sees, not
# what a regex guesses. Assignments inside a FUNCTION are a different scope
# and are not reported: a function-local $push does not touch the script's
# [switch]$Push.
function Get-ParameterShadowing {
    param([Parameter(Mandatory = $true)][string]$Path)
    $tokens = $null
    $errors = $null
    $ast = [System.Management.Automation.Language.Parser]::ParseFile($Path, [ref]$tokens, [ref]$errors)
    $names = @()
    if ($ast.ParamBlock) {
        foreach ($p in $ast.ParamBlock.Parameters) { $names += $p.Name.VariablePath.UserPath.ToLowerInvariant() }
    }
    if ($names.Count -eq 0) { return @() }
    $hits = @()
    $assigns = $ast.FindAll({ param($n) $n -is [System.Management.Automation.Language.AssignmentStatementAst] }, $true)
    foreach ($a in $assigns) {
        $left = $a.Left
        if (-not ($left -is [System.Management.Automation.Language.VariableExpressionAst])) { continue }
        # walk up: if an ancestor is a function, the assignment is function-local
        $node = $a
        $inFunction = $false
        while ($null -ne $node) {
            if ($node -is [System.Management.Automation.Language.FunctionDefinitionAst]) { $inFunction = $true; break }
            $node = $node.Parent
        }
        if ($inFunction) { continue }
        $vname = $left.VariablePath.UserPath.ToLowerInvariant()
        if ($names -contains $vname) { $hits += $vname }
    }
    return $hits
}

# the fixture needs the real scripts, so the publisher inside it measures
# with the real merge-check.ps1
New-Item -ItemType Directory -Path $TmpRoot -Force | Out-Null
$fxScripts = Join-Path $TmpRoot 'scripts'
New-Item -ItemType Directory -Path $fxScripts -Force | Out-Null
Copy-Item -LiteralPath $Publisher -Destination (Join-Path $fxScripts 'publish-ci.ps1') -Force
Copy-Item -LiteralPath (Join-Path $ScriptsDir 'merge-check.ps1') -Destination (Join-Path $fxScripts 'merge-check.ps1') -Force
$Publisher = Join-Path $fxScripts 'publish-ci.ps1'

# --- 1. dry run on a clean divergence: the remote must not move ------------
$f1 = New-Fixture -Name 'p1-clean' -Conflict $false
$before1 = Get-RemoteHead -Bare $f1.Bare
$r1 = Invoke-Publisher -RepoPath $f1.Work
$after1 = Get-RemoteHead -Bare $f1.Bare
Test-Probe -Label 'dry run pe divergenta curata -> exit 0, remote neatins' -Ok (($r1.Code -eq 0) -and ($before1 -eq $after1)) -Detail ('exit=' + $r1.Code + ' | remote_neschimbat=' + ($before1 -eq $after1))

# --- 2. push on a clean divergence: the remote must show the local HEAD ---
# and the merge must KEEP BOTH histories: the commit on the remote before the
# push has to stay an ancestor of the new HEAD. That is the requirement Popy
# stated for the publication - "include si ce modificari sunt deja pe git".
$f2 = New-Fixture -Name 'p2-push' -Conflict $false
$before2 = Get-RemoteHead -Bare $f2.Bare
$r2 = Invoke-Publisher -RepoPath $f2.Work -Push
$after2 = Get-RemoteHead -Bare $f2.Bare
$local2 = (Invoke-Git -WorkingDirectory $f2.Work -Arguments @('rev-parse', 'main')).Out.Trim()
$parents2 = (Invoke-Git -WorkingDirectory $f2.Work -Arguments @('rev-list', '--parents', '-n', '1', 'main')).Out.Trim()
$ancestor2 = (Invoke-Git -WorkingDirectory $f2.Work -Arguments @('merge-base', '--is-ancestor', $before2, 'main')).Code -eq 0
$parentCount2 = ($parents2 -split '\s+').Count - 1
Test-Probe -Label 'push pe divergenta curata -> exit 0, remote arata HEAD-ul local' -Ok (($r2.Code -eq 0) -and ($after2 -eq $local2) -and ($before2 -ne $after2)) -Detail ('exit=' + $r2.Code + ' | remote=local=' + ($after2 -eq $local2) + ' | remote_miscat=' + ($before2 -ne $after2))
Test-Probe -Label 'merge-ul pastreaza AMBELE istorice (commit cu 2 parinti, commitul remote e stramos)' -Ok (($parentCount2 -eq 2) -and $ancestor2) -Detail ('parinti=' + $parentCount2 + ' | stramos_remote=' + $ancestor2)

# --- 3. push on a CONFLICT: nothing may change, nothing may be pushed ----
$f3 = New-Fixture -Name 'p3-conflict' -Conflict $true
$before3 = Get-RemoteHead -Bare $f3.Bare
$localBefore3 = (Invoke-Git -WorkingDirectory $f3.Work -Arguments @('rev-parse', 'main')).Out.Trim()
$r3 = Invoke-Publisher -RepoPath $f3.Work -Push
$after3 = Get-RemoteHead -Bare $f3.Bare
$localAfter3 = (Invoke-Git -WorkingDirectory $f3.Work -Arguments @('rev-parse', 'main')).Out.Trim()
$namedConflict = ($r3.Out -match 'CONFLICT')
Test-Probe -Label 'push pe conflict -> exit 1, remote neatins, arborele neatins, fisierul numit' -Ok (($r3.Code -eq 1) -and ($before3 -eq $after3) -and ($localBefore3 -eq $localAfter3) -and $namedConflict) -Detail ('exit=' + $r3.Code + ' | remote_neschimbat=' + ($before3 -eq $after3) + ' | local_neschimbat=' + ($localBefore3 -eq $localAfter3) + ' | conflict_numat=' + $namedConflict)

# --- 4. not a repository -> not measurable, not a clean verdict ------------
# The path is deliberately OUTSIDE any repository: `git rev-parse` walks up
# the tree, so a folder inside the CI working tree resolves to the CI repo.
# Proba 4b covers that case separately.
$notRepo = Join-Path $env:TEMP ('mavis-not-a-repo-' + [guid]::NewGuid().ToString('N').Substring(0, 8))
New-Item -ItemType Directory -Path $notRepo -Force | Out-Null
$r4 = Invoke-Publisher -RepoPath $notRepo
Test-Probe -Label 'folder care nu e repo -> exit 2 (UNKNOWN, nu succes)' -Ok ($r4.Code -eq 2) -Detail ('exit=' + $r4.Code)

# --- 4b. a SUBDIRECTORY of a repository must NOT publish the parent -------
# `git rev-parse --git-dir` walks UP the tree: a folder inside a repository
# resolves to that repository. A publisher that trusted it would merge and
# push the PARENT while reporting on the path it was given. Measured: the
# publisher returned exit 0 for a "not a repo" folder that lived inside the
# CI working tree, and it would have published the CI repo itself.
$subDir = Join-Path $f1.Work 'nested\deeper'
New-Item -ItemType Directory -Path $subDir -Force | Out-Null
$remoteBefore4b = Get-RemoteHead -Bare $f1.Bare
$r4b = Invoke-Publisher -RepoPath $subDir
$remoteAfter4b = Get-RemoteHead -Bare $f1.Bare
Test-Probe -Label 'subdirector de repo -> exit 2, NU se publica parintele' -Ok (($r4b.Code -eq 2) -and ($remoteBefore4b -eq $remoteAfter4b)) -Detail ('exit=' + $r4b.Code + ' | remote_neschimbat=' + ($remoteBefore4b -eq $remoteAfter4b))

# --- 4c. the SAME repository addressed through a JUNCTION must be accepted ---
# MEASURED 2026-10-27: the publisher compared the given path with the
# repository root as STRINGS. Through a junction the two can never match -
# git prints the physical path, the caller spells the alias - so the
# publisher refused the legitimate case, and this selfcheck went red with 7
# problems on a gate that was right about its purpose and blind about how
# the operator spells the path.
# The gate must not care how the path is spelled. This probe is the proof.
$junctionPath = Join-Path $TmpRoot 'junction-alias'
if (Test-Path -LiteralPath $junctionPath) { Remove-Item -LiteralPath $junctionPath -Recurse -Force }
$junctionMade = $false
try {
    New-Item -ItemType Junction -Path $junctionPath -Target $f1.Work -ErrorAction Stop | Out-Null
    $junctionMade = $true
} catch {
    Write-Out ('NOTE proba-jonctiune - nu s-a putut crea jonctiunea: ' + $_.Exception.Message)
}
if ($junctionMade) {
    $remoteBefore4c = Get-RemoteHead -Bare $f1.Bare
    $r4c = Invoke-Publisher -RepoPath $junctionPath
    $remoteAfter4c = Get-RemoteHead -Bare $f1.Bare
    Test-Probe -Label 'acelasi repo prin jonctiune -> acceptat, nu refuzat' -Ok (($r4c.Code -eq 0) -and ($remoteBefore4c -eq $remoteAfter4c)) -Detail ('exit=' + $r4c.Code + ' | remote_neschimbat=' + ($remoteBefore4c -eq $remoteAfter4c))
}

# --- 5. the REAL repository, dry run only: the real remote must not move ---
# The publisher REFUSES a tree with uncommitted changes to tracked files
# (exit 2, by design - a merge on top of uncommitted work is a result nobody
# can attribute). So the expected exit code depends on the state of the tree
# AT THE MOMENT of the probe, not on the publisher being broken.
#
# MEASURED 2026-10-27: this probe hardcoded "exit 0", so the gate went RED
# with a perfectly correct publisher - it fired whenever the operator had
# uncommitted changes in the tree. A gate that blocks for a reason it does not
# own is a gate that trains people to ignore it.
#
# The invariant that actually matters is asserted in BOTH branches: the real
# remote must not move. And in the dirty branch the publisher must refuse
# (exit 2) - that refusal IS the safety property.
$realStatusOut = (Invoke-Git -WorkingDirectory $RealRoot -Arguments @('status', '--porcelain')).Out
$realTrackedDirty = @()
foreach ($l in @($realStatusOut -split "`r?`n")) {
    $s = $l.TrimEnd()
    if (-not $s.Trim()) { continue }
    if ($s.StartsWith('??')) { continue }
    $realTrackedDirty += $s.Trim()
}
$realRemote = (Invoke-Git -WorkingDirectory $RealRoot -Arguments @('ls-remote', 'origin', 'refs/heads/main')).Out.Trim()
$r5 = Invoke-Publisher -RepoPath $RealRoot
$realRemoteAfter = (Invoke-Git -WorkingDirectory $RealRoot -Arguments @('ls-remote', 'origin', 'refs/heads/main')).Out.Trim()
$remoteUnchanged5 = ($realRemote -eq $realRemoteAfter)
if ($realTrackedDirty.Count -gt 0) {
    $ok5 = (($r5.Code -eq 2) -and $remoteUnchanged5)
    $label5 = 'repo-ul real cu arbore murdar -> refuz corect (exit 2), remote-ul real neatins'
} else {
    $ok5 = (($r5.Code -eq 0) -and $remoteUnchanged5)
    $label5 = 'repo-ul real, doar dry run -> exit 0, remote-ul real neatins'
}
Test-Probe -Label $label5 -Ok $ok5 -Detail ('exit=' + $r5.Code + ' | remote_neschimbat=' + $remoteUnchanged5 + ' | fisierele_urmarite_modificate=' + $realTrackedDirty.Count)

# --- 6. STATIC: no script-scope variable may shadow a parameter ------------
$hits = @(Get-ParameterShadowing -Path $Publisher)
Test-Probe -Label 'static: nicio variabila de la nivelul scriptului nu umbreaza un parametru' -Ok ($hits.Count -eq 0) -Detail ('coliziuni=' + $hits.Count + $(if ($hits.Count -gt 0) { ' -> ' + ($hits -join ',') } else { '' }))

# falsification of the probe itself, on a COPY: a deliberately broken
# publisher (a script-scope $push = ...) MUST be detected. If this passes
# silently, probe 6 proves nothing.
$brokenCopy = Join-Path $TmpRoot 'broken-publisher.ps1'
$src = [System.IO.File]::ReadAllText($Publisher)
$anchor = "`$ErrorActionPreference = 'Stop'"
$inject = "`$push = Invoke-Git -Arguments @('status') -WorkingDirectory `$RepoPath`r`n"
$src2 = $src.Replace($anchor, ($anchor + "`r`n" + $inject))
[System.IO.File]::WriteAllText($brokenCopy, $src2, (New-Object System.Text.UTF8Encoding($false)))
$hitsBroken = @(Get-ParameterShadowing -Path $brokenCopy)
$brokenHasCollision = ($hitsBroken -contains 'push')
Test-Probe -Label 'falsificare: publisher-ul STRICAT pe copie e detectat de proba statica' -Ok $brokenHasCollision -Detail ('coliziuni_pe_copia_stricata=' + ($hitsBroken -join ','))

# --- 7. a push REFUSED by a hook -> exit 4, the remote stays untouched ----
$f7 = New-Fixture -Name 'p7-refused' -Conflict $false
$hookDir = Join-Path $f7.Work '.git\hooks'
New-Item -ItemType Directory -Path $hookDir -Force | Out-Null
$hookText = "#!/bin/sh`necho 'POARTA: refuz deliberat pentru proba'`nexit 1`n"
[System.IO.File]::WriteAllText((Join-Path $hookDir 'pre-push'), $hookText, (New-Object System.Text.UTF8Encoding($false)))
$before7 = Get-RemoteHead -Bare $f7.Bare
$r7 = Invoke-Publisher -RepoPath $f7.Work -Push
$after7 = Get-RemoteHead -Bare $f7.Bare
Test-Probe -Label 'push refuzat de poarta -> exit 4, remote neatins, raportat ca refuz' -Ok (($r7.Code -eq 4) -and ($before7 -eq $after7) -and ($r7.Out -match 'refuzat')) -Detail ('exit=' + $r7.Code + ' | remote_neschimbat=' + ($before7 -eq $after7) + ' | refuz_numat=' + ($r7.Out -match 'refuzat'))

# --- 8. a TRACKED file changed -> blocked, nothing pushed -----------------
$f8 = New-Fixture -Name 'p8-dirty-tracked' -Conflict $false
$enc8 = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText((Join-Path $f8.Work 'seed.txt'), 'modificat, necomitat', $enc8)
$before8 = Get-RemoteHead -Bare $f8.Bare
$r8 = Invoke-Publisher -RepoPath $f8.Work -Push
$after8 = Get-RemoteHead -Bare $f8.Bare
Test-Probe -Label 'fisier URMARIT modificat -> exit 2 (blocat), remote neatins' -Ok (($r8.Code -eq 2) -and ($before8 -eq $after8)) -Detail ('exit=' + $r8.Code + ' | remote_neschimbat=' + ($before8 -eq $after8))

# --- 9. an UNTRACKED file only -> reported, but not a blocker -------------
$f9 = New-Fixture -Name 'p9-untracked' -Conflict $false
[System.IO.File]::WriteAllText((Join-Path $f9.Work 'local-not-tracked.txt'), 'scratch local', $enc8)
$before9 = Get-RemoteHead -Bare $f9.Bare
$r9 = Invoke-Publisher -RepoPath $f9.Work -Push
$after9 = Get-RemoteHead -Bare $f9.Bare
Test-Probe -Label 'doar fisier NEURMARIT -> nu blocheaza (exit 0), remote miscats corect' -Ok (($r9.Code -eq 0) -and ($before9 -ne $after9) -and ($r9.Out -match 'NOTE')) -Detail ('exit=' + $r9.Code + ' | remote_miscat=' + ($before9 -ne $after9) + ' | note_raportata=' + ($r9.Out -match 'NOTE'))

Write-Out ('PUBLISH_GATE_PROBLEMS=' + $problems + ' FALSIFIED=' + $falsified + ' (probes=' + $probeNo + ')')
if ($problems -gt 0) {
    Write-Out 'POARTA A BLOCAT. Publicarea nu poate fi considerata de incredere.'
    exit 1
}
Write-Out ('Fixture-urile probelor raman in ' + $TmpRoot + ' pentru inspectie.')
exit 0
