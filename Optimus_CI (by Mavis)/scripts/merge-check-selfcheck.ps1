# merge-check-selfcheck.ps1
# The gate for the gate: it proves that merge-check.ps1 can tell a clean
# merge from a conflicting one, on real git repositories, not on theory.
#
# The probes build throwaway repos under state/tmp/ and let git decide:
#
#   1  two branches touching DIFFERENT files  -> exit 0 (clean)
#   2  two branches touching the SAME line     -> exit 1 (conflict)
#   3  the conflicted file is NAMED           -> the file appears in the report
#   4  a path that is not a git repo          -> exit 2 (not measurable)
#   5  the real repository                     -> MEASURED (0 or 1), never
#                                                assumed; 2 blocks the gate
#
# Probe 5 measures the real repository with ITS OWN ref (origin/main), not
# with the fixture's origin/sideB: a fixture ref does not exist in the real
# repository, and measuring an absent ref is a defect, not a measurement.
# On the real repository, exit 0 (clean) and exit 1 (conflicting) are both
# valid measurements - whether the two histories collide is a fact about the
# repository, not a defect of the gate. Only exit 2 (not measurable) blocks.
#
# A measurement that cannot fail is not a measurement, so the conflicting
# case is built for real: git itself has to produce the conflict.
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

$Gate = Join-Path $ScriptsDir 'merge-check.ps1'
if (-not (Test-Path -LiteralPath $Gate)) {
    Write-Output ('EROARE: lipseste ' + $Gate)
    exit 2
}

$RealRootDefault = Split-Path -Parent $ScriptsDir
if (-not $RealRoot) { $RealRoot = $RealRootDefault }
if (-not (Test-Path -LiteralPath $RealRoot)) {
    Write-Output ('EROARE: repo real inexistent: ' + $RealRoot)
    exit 2
}
# The fixtures are git repositories of their own. They are built OUTSIDE the
# Google Drive mirror, so DriveFS never administers a live .git directory.
$ScratchLib = Join-Path $PSScriptRoot 'git-scratch.ps1'
if (-not (Test-Path -LiteralPath $ScratchLib)) {
    Write-Output ('EROARE: lipseste scripts\git-scratch.ps1: ' + $ScratchLib)
    exit 2
}
. $ScratchLib
$ScratchRoot = Assert-ScratchOutsideMirror -ScratchRoot (Get-GitScratchRoot -ProjectRoot $RealRootDefault) -ProjectRoot $RealRootDefault
$TmpRoot = Join-Path $ScratchRoot 'merge-selfcheck'
if (Test-Path -LiteralPath $TmpRoot) { Remove-Item -LiteralPath $TmpRoot -Recurse -Force }
New-Item -ItemType Directory -Path $TmpRoot -Force | Out-Null

$problems = 0
$unknown = 0
$falsified = 0
$probeNo = 0

function Write-Out {
    # AllowEmptyString: a failing gate may print NOTHING, and the
    # diagnostic path must survive that. A self-check that crashes while
    # reporting a failure has no verdict - and an exit code coming from a
    # terminating exception is indistinguishable from the gate's own exit 1.
    param([AllowEmptyString()][string]$Message)
    [Console]::Out.WriteLine($Message)
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

# Build a real repo WITH A REAL REMOTE, so that the gate measures the same
# shape it measures in production: a remote-tracking ref (origin/sideB)
# against a local branch (main), with a fetch that actually works.
#
# The two shapes:
#   clean    - main changes file A, sideB changes file B
#   conflict - main and sideB change the SAME line of the same file
# git itself has to produce the conflict; the gate only has to see it.
function New-TestRepo {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][string]$MainFile,
        [Parameter(Mandatory = $true)][string]$MainLine,
        [Parameter(Mandatory = $true)][string]$SideFile,
        [Parameter(Mandatory = $true)][string]$SideLine
    )
    $bare = Join-Path $TmpRoot ($Name + '.git')
    $work = Join-Path $TmpRoot $Name
    $null = Invoke-Git -WorkingDirectory $TmpRoot -Arguments @('init', '--bare', '-q', '-b', 'main', $bare)
    $null = Invoke-Git -WorkingDirectory $TmpRoot -Arguments @('clone', '-q', $bare, $work)
    $null = Invoke-Git -WorkingDirectory $work -Arguments @('config', 'user.email', 'probe@example.invalid')
    $null = Invoke-Git -WorkingDirectory $work -Arguments @('config', 'user.name', 'Probe')
    $enc = New-Object System.Text.UTF8Encoding($false)

    # base
    [System.IO.File]::WriteAllText((Join-Path $work 'seed.txt'), "seed`n", $enc)
    $null = Invoke-Git -WorkingDirectory $work -Arguments @('add', '-A')
    $null = Invoke-Git -WorkingDirectory $work -Arguments @('commit', '-q', '-m', 'seed')

    # main: its own change
    [System.IO.File]::WriteAllText((Join-Path $work $MainFile), $MainLine, $enc)
    $null = Invoke-Git -WorkingDirectory $work -Arguments @('add', '-A')
    $null = Invoke-Git -WorkingDirectory $work -Arguments @('commit', '-q', '-m', 'main change')

    # sideB: branched from the base, so it does NOT contain main's change
    $null = Invoke-Git -WorkingDirectory $work -Arguments @('checkout', '-q', '-b', 'sideB', 'HEAD~1')
    [System.IO.File]::WriteAllText((Join-Path $work $SideFile), $SideLine, $enc)
    $null = Invoke-Git -WorkingDirectory $work -Arguments @('add', '-A')
    $null = Invoke-Git -WorkingDirectory $work -Arguments @('commit', '-q', '-m', 'side change')
    $null = Invoke-Git -WorkingDirectory $work -Arguments @('checkout', '-q', 'main')
    $null = Invoke-Git -WorkingDirectory $work -Arguments @('push', '-q', 'origin', 'sideB')
    # push main too, so the remote-tracking ref origin/main exists and the
    # gate's fetch succeeds -> REMOTE_STATE=LIVE, the production shape.
    $null = Invoke-Git -WorkingDirectory $work -Arguments @('push', '-q', 'origin', 'main')
    return $work
}

function Invoke-Gate {
    param(
        [Parameter(Mandatory = $true)][string]$GateRoot,
        [string]$Other = ''
    )
    $prev = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    # -Other is OPTIONAL: the fixture compares origin/sideB against main,
    # but the real repository compares origin/main against main. Passing the
    # fixture's ref to the real repo would make the divergence unreadable
    # and would measure a branch that exists only in the throwaway fixture.
    $gateArgs = @('-NoProfile', '-File', $Gate, '-RepoPath', $GateRoot, '-Remote', 'origin', '-Branch', 'main')
    if ($Other) { $gateArgs += @('-Other', $Other) }
    $out = & powershell @gateArgs 2>&1
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
        [Parameter(Mandatory = $true)][int]$Expected,
        [Parameter(Mandatory = $true)][int]$Actual
    )
    $script:probeNo++
    if ($Actual -eq $Expected) {
        $script:falsified++
        Write-Out ('OK   proba-' + $script:probeNo + ' ' + $Label + ' -> exit ' + $Actual + ' (asteptat ' + $Expected + ')')
    } else {
        $script:problems++
        Write-Out ('FAIL proba-' + $script:probeNo + ' ' + $Label + ' -> exit ' + $Actual + ', asteptat ' + $Expected)
    }
}

# --- 1. different files -> the merge is clean ----------------------------
$clean = New-TestRepo -Name 'p1-clean' -MainFile 'a.txt' -MainLine 'din main' -SideFile 'b.txt' -SideLine 'din sideB'
$r1 = Invoke-Gate -GateRoot $clean -Other 'origin/sideB'
Test-Probe -Label 'ramuri pe fisiere diferite -> merge curat' -Expected 0 -Actual $r1.Code

# --- 2. same line -> git produces a conflict, the gate must see it -------
$conf = New-TestRepo -Name 'p2-conflict' -MainFile 'seed.txt' -MainLine 'din main' -SideFile 'seed.txt' -SideLine 'din sideB'
$r2 = Invoke-Gate -GateRoot $conf -Other 'origin/sideB'
Test-Probe -Label 'ramuri pe aceeasi linie -> conflict detectat' -Expected 1 -Actual $r2.Code

# --- 3. the conflicted file must be NAMED --------------------------------
$script:probeNo++
if ($r2.Out -match 'CONFLICT\s+seed\.txt') {
    $falsified++
    Write-Out ('OK   proba-' + $script:probeNo + ' fisierul in conflict e numit in raport (seed.txt)')
} else {
    $problems++
    Write-Out ('FAIL proba-' + $script:probeNo + ' fisierul in conflict NU e numit in raport')
    Write-Out ($r2.Out.Trim())
}

# --- 4. not a git repo -> not measurable, not "clean" --------------------
$notRepo = Join-Path $TmpRoot 'p4-not-a-repo'
New-Item -ItemType Directory -Path $notRepo -Force | Out-Null
$r4 = Invoke-Gate -GateRoot $notRepo -Other 'origin/sideB'
Test-Probe -Label 'folder care nu e repo -> UNKNOWN, nu succes' -Expected 2 -Actual $r4.Code

# --- 5. the real repository ----------------------------------------------
# The real repository is measured with ITS OWN ref (origin/main against
# main). Whether the merge is clean or conflicting is a FACT about the
# repository, not a defect of the gate: both 0 and 1 are valid measurements.
# Only 2 (not measurable) is a failure - a gate that cannot measure its
# own target is not a gate.
$r5 = Invoke-Gate -GateRoot $RealRoot
if ($r5.Code -eq 0) {
    $falsified++
    Write-Out 'OK   proba-5 repo-ul real -> exit 0 (masurat: merge curat)'
} elseif ($r5.Code -eq 1) {
    $falsified++
    Write-Out 'OK   proba-5 repo-ul real -> exit 1 (masurat: merge conflict, numele fisierelor in raport)'
    Write-Out ($r5.Out.Trim())
} else {
    $unknown++
    $problems++
    Write-Out ('FAIL proba-5 repo-ul real -> exit ' + $r5.Code + ' (nu s-a putut masura)')
    Write-Out ($r5.Out.Trim())
}

Write-Out ('MERGE_GATE_PROBLEMS=' + $problems + ' UNKNOWN=' + $unknown + ' FALSIFIED=' + $falsified)
if ($problems -gt 0) {
    Write-Out 'POARTA A BLOCAT. Instrumentul de combinare nu poate fi considerat de incredere.'
    exit 1
}
Write-Out ('Fixture-urile probelor raman in ' + $TmpRoot + ' pentru inspectie.')
exit 0
