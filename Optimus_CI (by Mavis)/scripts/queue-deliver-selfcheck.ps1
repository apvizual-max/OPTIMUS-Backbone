# queue-deliver-selfcheck.ps1
# The gate for the gate: it proves that queue-deliver.ps1 can DELIVER and
# can REFUSE, and that it never reports a delivery it did not measure.
#
# MEASURED 2026-10-27: the tickets were written into the CI repo, while the
# Cloud reads its OWN repo. 2 tickets local, 0 in the Cloud's queue. So the
# delivery mechanism was built against a local bare remote: a real git repo,
# a real clone, a real push, a real read-back at the remote. Nothing here
# touches the real Cloud repository.
#
# The probes, and what each one proves:
#
#   1  a ticket that was never delivered        -> exit 1  (can detect the gap)
#   2  delivery without -Push                   -> exit 4  (written, not published)
#      and the REMOTE does not carry the ticket
#   3  delivery with -Push                      -> exit 0  (can publish)
#      and the REMOTE carries the ticket id
#   4  the same delivery a second time          -> exit 0  (idempotent)
#      and the REMOTE carries the ticket ONCE
#   5  a truncated instruction body             -> exit 2  (refused)
#      and the REMOTE is unchanged
#   6  a body that redeclares a contract field  -> exit 2  (refused)
#   7  a body that opens a phantom ticket       -> exit 2  (refused)
#   8  a push that the remote refuses           -> exit 5  (refused)
#      and the REMOTE is unchanged
#
# Every "REMOTE carries / does not carry" claim is read from the bare
# repository itself, not from the clone: a clone that has the commit is not
# a delivery to the consumer.
#
# Exit codes:
#   0 = every probe behaved as expected
#   1 = at least one probe failed
#   2 = the selfcheck could not run at all
#
# ASCII ONLY: executed by Windows PowerShell 5.1.

param(
    [string]$ScriptsDir = ''
)

$ErrorActionPreference = 'Stop'

if (-not $ScriptsDir) { $ScriptsDir = $PSScriptRoot }

$Deliver = Join-Path $ScriptsDir 'queue-deliver.ps1'
if (-not (Test-Path -LiteralPath $Deliver)) {
    [Console]::Error.WriteLine('ERROR=lipseste queue-deliver.ps1: ' + $Deliver)
    exit 2
}

$RealRoot = Split-Path -Parent $ScriptsDir
$RealSnapshot = Join-Path $RealRoot 'docs\CONTRACT-CLOUD-QUEUE.md'
if (-not (Test-Path -LiteralPath $RealSnapshot)) {
    [Console]::Error.WriteLine('ERROR=lipseste snapshotul contractului: ' + $RealSnapshot)
    exit 2
}

$problems = 0
$falsified = 0
$probeNo = 0

function Write-Out {
    param([AllowEmptyString()][string]$Message)
    [Console]::Out.WriteLine($Message)
}

function Invoke-Git {
    param(
        [Parameter(Mandatory = $true)][string[]]$Arguments,
        [string]$WorkingDirectory = '',
        [string]$GitDir = ''
    )
    $prev = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    if ($GitDir) {
        $out = & git --git-dir $GitDir @Arguments 2>&1
    } elseif ($WorkingDirectory) {
        $out = & git -C $WorkingDirectory @Arguments 2>&1
    } else {
        $out = & git @Arguments 2>&1
    }
    $code = $LASTEXITCODE
    $ErrorActionPreference = $prev
    $text = ''
    if ($out) { $text = ([string]::Join("`n", @($out))) }
    return [pscustomobject]@{ Code = $code; Text = $text }
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

function Test-Claim {
    param(
        [Parameter(Mandatory = $true)][string]$Label,
        [Parameter(Mandatory = $true)][bool]$Claim
    )
    $script:probeNo++
    if ($Claim) {
        $script:falsified++
        Write-Out ('OK   proba-' + $script:probeNo + ' ' + $Label)
    } else {
        $script:problems++
        Write-Out ('FAIL proba-' + $script:probeNo + ' ' + $Label)
    }
}

# The seed content of the Cloud's queue: the contract block and one
# consumed ticket. It is the state a real Cloud repo is in.
$CloudSeed = @(
    '# Coada de sarcini pentru Mavis Cloud',
    '',
    'Cloud face `git pull`, citeste, executa, scrie rezultatul in `QUEUE/DONE/`.',
    '',
    '## Format',
    '',
    '```',
    '### [id] titlu',
    'cerut de: local | data: YYYY-MM-DD',
    'scope: cloud | local | ambele',
    'ce trebuie: ...',
    'livrare: unde trebuie sa ajunga rezultatul',
    '```',
    '',
    '## Reguli',
    '',
    '- `scope: local` -> nu incepe, scrie handoff',
    '- fara livrare definita -> nu lucra',
    '',
    '---',
    '',
    '## Tichete',
    '',
    '### [x] TASK-001 Inventar',
    'cerut de: local | data: 2026-10-12',
    'scope: cloud',
    'ce trebuie: Fa un inventar al skill-urilor.',
    'livrare: QUEUE/DONE/TASK-001.md',
    ''
) -join "`n"

function New-Fixture {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [string]$QueueText = '',
        [string]$Title = 'Ticheta de test'
    )
    $r = Join-Path $TmpRoot $Name
    New-Item -ItemType Directory -Path (Join-Path $r 'QUEUE') -Force | Out-Null
    New-Item -ItemType Directory -Path (Join-Path $r 'QUEUE\DONE') -Force | Out-Null
    New-Item -ItemType Directory -Path (Join-Path $r 'BRIDGE-DRIVE') -Force | Out-Null
    New-Item -ItemType Directory -Path (Join-Path $r 'docs') -Force | Out-Null
    New-Item -ItemType Directory -Path (Join-Path $r 'cloud-ingest') -Force | Out-Null

    $enc = New-Object System.Text.UTF8Encoding($false)

    if (-not $QueueText) {
        $QueueText = @(
            '# TASKURI PENTRU CLOUD - canal secundar (GitHub)',
            '',
            '### [TASK-TEST-001] ' + $Title,
            'cerut de: local | data: 2026-10-27',
            'scope: cloud',
            'ce trebuie: Fa un lucru oarecare, in cifre, si spune ce ai masurat.',
            'livrare: QUEUE/DONE/TASK-TEST-001.md',
            ''
        ) -join "`n"
    }
    [System.IO.File]::WriteAllText((Join-Path $r 'QUEUE\TASKS-FOR-CLOUD.md'), $QueueText, $enc)
    $drive = @(
        '# TASKURI PENTRU CLOUD',
        '',
        '## TASK-TEST-001',
        '',
        '- **Emit:** Mavis Local',
        ''
    ) -join "`n"
    [System.IO.File]::WriteAllText((Join-Path $r 'BRIDGE-DRIVE\TASKURI-PENTRU-CLOUD.md'), $drive, $enc)
    [System.IO.File]::Copy($RealSnapshot, (Join-Path $r 'docs\CONTRACT-CLOUD-QUEUE.md'), $true)

    # The Cloud's repository: a bare remote and a clone of it. Local paths,
    # so the whole chain (commit, push, read back) is exercised offline.
    $bare = Join-Path $r 'remote.git'
    $seed = Join-Path $r 'seed'
    [void](Invoke-Git -Arguments @('init', '--bare', '-b', 'main', $bare))
    [void](Invoke-Git -Arguments @('init', '-b', 'main', $seed))
    [void](Invoke-Git -Arguments @('config', 'user.name', 'Mavis Selfcheck') -WorkingDirectory $seed)
    [void](Invoke-Git -Arguments @('config', 'user.email', 'selfcheck@localhost') -WorkingDirectory $seed)
    New-Item -ItemType Directory -Path (Join-Path $seed 'QUEUE') -Force | Out-Null
    [System.IO.File]::WriteAllText((Join-Path $seed 'QUEUE\TASKS-FOR-CLOUD.md'), $CloudSeed, $enc)
    [void](Invoke-Git -Arguments @('add', '-A') -WorkingDirectory $seed)
    [void](Invoke-Git -Arguments @('commit', '-m', 'seed: coada Cloud-ului') -WorkingDirectory $seed)
    [void](Invoke-Git -Arguments @('remote', 'add', 'origin', $bare) -WorkingDirectory $seed)
    [void](Invoke-Git -Arguments @('push', 'origin', 'main') -WorkingDirectory $seed)

    $clone = Join-Path $r 'cloud-ingest\MAVIS-CLOUD'
    [void](Invoke-Git -Arguments @('clone', $bare, $clone))
    [void](Invoke-Git -Arguments @('config', 'user.name', 'Mavis Local') -WorkingDirectory $clone)
    [void](Invoke-Git -Arguments @('config', 'user.email', 'local@localhost') -WorkingDirectory $clone)

    return @{ Root = $r; Bare = $bare; Clone = $clone }
}

function Invoke-Deliver {
    param(
        [Parameter(Mandatory = $true)][string]$Root,
        [switch]$Push,
        [switch]$Status
    )
    $argsList = @('-NoProfile', '-File', $Deliver, '-Root', $Root)
    # The two modes are exclusive: the script treats -Status as "measure",
    # and -Deliver as "write". Passing both would measure the wrong thing -
    # a probe that claims to measure a delivery but measures a status is
    # worse than no probe.
    if ($Status) {
        $argsList += '-Status'
    } else {
        $argsList += '-Deliver'
    }
    if ($Push) { $argsList += '-Push' }
    $prev = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    $out = & powershell @argsList 2>&1
    $code = $LASTEXITCODE
    $ErrorActionPreference = $prev
    $text = ''
    if ($out) { $text = ([string]::Join("`n", @($out))) }
    return @{ Code = $code; Text = $text }
}

# The truth about a delivery: what the REMOTE holds. Read from the bare
# repository, because the clone having a commit is not a delivery.
function Get-RemoteQueue {
    param([Parameter(Mandatory = $true)][string]$Bare)
    $res = Invoke-Git -Arguments @('show', 'main:QUEUE/TASKS-FOR-CLOUD.md') -GitDir $Bare
    if ($res.Code -ne 0) { return '' }
    return $res.Text
}

function Count-Occurrences {
    param(
        [Parameter(Mandatory = $true)][string]$Haystack,
        [Parameter(Mandatory = $true)][string]$Needle
    )
    if (-not $Haystack) { return 0 }
    $n = 0
    $idx = $Haystack.IndexOf($Needle)
    while ($idx -ge 0) {
        $n++
        $idx = $Haystack.IndexOf($Needle, $idx + $Needle.Length)
    }
    return $n
}

# The fixtures include real git repositories. They are built OUTSIDE the
# Google Drive mirror, so DriveFS never administers a live .git directory.
$ScratchLib = Join-Path $PSScriptRoot 'git-scratch.ps1'
if (-not (Test-Path -LiteralPath $ScratchLib)) {
    Write-Output ('EROARE: lipseste scripts\git-scratch.ps1: ' + $ScratchLib)
    exit 2
}
. $ScratchLib
$ScratchRoot = Assert-ScratchOutsideMirror -ScratchRoot (Get-GitScratchRoot -ProjectRoot $RealRoot) -ProjectRoot $RealRoot
$TmpRoot = Join-Path $ScratchRoot 'queue-deliver-selfcheck'
if (-not (Test-Path -LiteralPath $TmpRoot)) {
    New-Item -ItemType Directory -Path $TmpRoot -Force | Out-Null
}
$stamp = (Get-Date).ToString('yyyyMMdd-HHmmss')

# --- 1. the gap is detected -----------------------------------------------
$f1 = New-Fixture -Name ('run-' + $stamp + '-p01')
$r1 = Invoke-Deliver -Root $f1.Root -Status
Test-Probe -Label 'ticheta nelivrata este detectata' -Expected 1 -Actual $r1.Code

# --- 2. delivery without -Push does NOT publish ---------------------------
$r2 = Invoke-Deliver -Root $f1.Root
Test-Probe -Label 'livrare fara -Push: scris, dar nepublicat' -Expected 4 -Actual $r2.Code
$remote2 = Get-RemoteQueue -Bare $f1.Bare
Test-Claim -Label 'remote-ul NU contine ticheta dupa livrare fara -Push' -Claim (-not $remote2.Contains('TASK-TEST-001'))

# --- 3. delivery with -Push publishes, and the REMOTE carries it ---------
$r3 = Invoke-Deliver -Root $f1.Root -Push
Test-Probe -Label 'livrare cu -Push' -Expected 0 -Actual $r3.Code
$remote3 = Get-RemoteQueue -Bare $f1.Bare
Test-Claim -Label 'remote-ul contine ticheta dupa livrare cu -Push' -Claim ($remote3.Contains('TASK-TEST-001'))

# --- 4. the same delivery again is idempotent ----------------------------
$r4 = Invoke-Deliver -Root $f1.Root -Push
Test-Probe -Label 'relivrare idempotenta' -Expected 0 -Actual $r4.Code
$remote4 = Get-RemoteQueue -Bare $f1.Bare
Test-Claim -Label 'remote-ul contine ticheta O SINGURA DATA' -Claim ((Count-Occurrences -Haystack $remote4 -Needle '### [TASK-TEST-001]') -eq 1)

# --- 5. a truncated instruction is refused --------------------------------
$q5 = @(
    '# TASKURI PENTRU CLOUD - canal secundar (GitHub)',
    '',
    '### [TASK-TEST-005] Ticheta trunchiata',
    'cerut de: local | data: 2026-10-27',
    'scope: cloud',
    'ce trebuie: Fa un lucru oarecare, in cifre, si spune ce ai masurat',
    'livrare: QUEUE/DONE/TASK-TEST-005.md',
    ''
) -join "`n"
$f5 = New-Fixture -Name ('run-' + $stamp + '-p05') -QueueText $q5
$r5 = Invoke-Deliver -Root $f5.Root -Push
Test-Probe -Label 'instructiune trunchiata: refuzata' -Expected 2 -Actual $r5.Code
$remote5 = Get-RemoteQueue -Bare $f5.Bare
Test-Claim -Label 'remote-ul nu contine ticheta trunchiata' -Claim (-not $remote5.Contains('TASK-TEST-005'))

# --- 6. a body that redeclares a contract field is refused ----------------
$q6 = @(
    '# TASKURI PENTRU CLOUD - canal secundar (GitHub)',
    '',
    '### [TASK-TEST-006] Ticheta cu camp redeclarat',
    'cerut de: local | data: 2026-10-27',
    'scope: cloud',
    'ce trebuie: Fa un lucru oarecare, in cifre, si spune ce ai masurat.',
    'livrare: QUEUE/DONE/TASK-TEST-006.md',
    'livrare: QUEUE/DONE/ALTA-LOCATIE.md',
    ''
) -join "`n"
$f6 = New-Fixture -Name ('run-' + $stamp + '-p06') -QueueText $q6
$r6 = Invoke-Deliver -Root $f6.Root -Push
Test-Probe -Label 'corp care redeclara un camp al contractului: refuzat' -Expected 2 -Actual $r6.Code
$remote6 = Get-RemoteQueue -Bare $f6.Bare
Test-Claim -Label 'remote-ul nu contine ticheta cu camp redeclarat' -Claim (-not $remote6.Contains('TASK-TEST-006'))

# --- 7. a body that opens a phantom ticket is refused ---------------------
$q7 = @(
    '# TASKURI PENTRU CLOUD - canal secundar (GitHub)',
    '',
    '### [TASK-TEST-007] Ticheta cu ticheta fantoma',
    'cerut de: local | data: 2026-10-27',
    'scope: cloud',
    'ce trebuie: Fa un lucru oarecare, in cifre, si spune ce ai masurat.',
    '### [TASK-FANTOMA-001] Ticheta deschisa de corp',
    'livrare: QUEUE/DONE/TASK-TEST-007.md',
    ''
) -join "`n"
$f7 = New-Fixture -Name ('run-' + $stamp + '-p07') -QueueText $q7
$r7 = Invoke-Deliver -Root $f7.Root -Push
Test-Probe -Label 'corp care deschide o ticheta fantoma: refuzat' -Expected 2 -Actual $r7.Code
$remote7 = Get-RemoteQueue -Bare $f7.Bare
Test-Claim -Label 'remote-ul nu contine ticheta fantoma' -Claim (-not $remote7.Contains('TASK-FANTOMA-001'))

# --- 8. a push the remote refuses publishes nothing ----------------------
$f8 = New-Fixture -Name ('run-' + $stamp + '-p08')
$broken = Join-Path $f8.Root 'remote-inexistent.git'
[void](Invoke-Git -Arguments @('remote', 'set-url', '--add', '--push', 'origin', $broken) -WorkingDirectory $f8.Clone)
$r8 = Invoke-Deliver -Root $f8.Root -Push
Test-Probe -Label 'push refuzat de remote: nimic publicat' -Expected 5 -Actual $r8.Code
$remote8 = Get-RemoteQueue -Bare $f8.Bare
Test-Claim -Label 'remote-ul nu contine ticheta dupa push refuzat' -Claim (-not $remote8.Contains('TASK-TEST-001'))

Write-Out ('DELIVER_GATE_PROBLEMS=' + $problems + ' FALSIFIED=' + $falsified)
if ($problems -gt 0) {
    Write-Out 'POARTA A BLOCAT. Mecanismul de livrare nu poate fi considerat de incredere pana nu se repara.'
    exit 1
}
Write-Out ('Fixture-urile probelor raman in ' + $TmpRoot + ' pentru inspectie.')
exit 0
