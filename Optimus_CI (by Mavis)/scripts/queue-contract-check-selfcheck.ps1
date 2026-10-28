# queue-contract-check-selfcheck.ps1
# The gate for the gate: it proves that queue-contract-check.ps1 can both
# PASS and FAIL, and that it never reports a healthy state it did not
# measure.
#
# The probes run against FIXTURES, not against the real queue, so a broken
# ticket can be tested without touching the real one. Each fixture is a
# complete miniature repo: queue, delivery target, primary channel, contract
# snapshot and - optionally - the live contract of the Cloud.
#
# The probes, and what each one proves:
#
#   1  a conforming queue, live contract present   -> exit 0  (can pass)
#   2  a ticket with no scope                        -> exit 1  (caught)
#   3  a ticket with an unknown scope                -> exit 1  (caught)
#   4  a ticket with no livrare                      -> exit 1  (caught)
#   5  a ticket whose instruction ends mid-sentence  -> exit 1  (caught)
#   6  no QUEUE/DONE directory                       -> exit 1  (caught)
#   7  a ticket id absent from the primary channel   -> exit 1  (caught)
#   8  the live contract unreadable                  -> exit 2  (UNKNOWN, not a pass)
#   9  the live contract drifted from the snapshot   -> exit 1  (caught)
#  10  a ticket written in a format the contract cannot read -> exit 1 (caught)
#  11  the real repository                           -> reported, never assumed
#  12  the ticket is NOT in the Cloud's own queue    -> exit 1  (caught)
#      MEASURED 2026-10-27: this is the probe that was missing. A perfect
#      queue in the CI repo, zero tickets in the queue the Cloud actually
#      reads, and the gate said everything was fine.
#  13  the Cloud's skill no longer declares the queue -> exit 1  (caught)
#  14  the Cloud's skill unreadable                  -> exit 2  (UNKNOWN, not a pass)
#
# Exit codes:
#   0 = everything measured and true
#   1 = at least one probe failed
#   2 = the gate could not run at all
#
# ASCII ONLY: executed by Windows PowerShell 5.1.

param(
    [string]$ScriptsDir = ''
)

$ErrorActionPreference = 'Stop'

if (-not $ScriptsDir) { $ScriptsDir = $PSScriptRoot }

$Gate = Join-Path $ScriptsDir 'queue-contract-check.ps1'
if (-not (Test-Path -LiteralPath $Gate)) {
    Write-Output ('EROARE: lipseste ' + $Gate)
    exit 2
}

$RealRoot = Split-Path -Parent $ScriptsDir
$RealSnapshot = Join-Path $RealRoot 'docs\CONTRACT-CLOUD-QUEUE.md'
if (-not (Test-Path -LiteralPath $RealSnapshot)) {
    Write-Output ('EROARE: lipseste snapshotul contractului: ' + $RealSnapshot)
    exit 2
}

$problems = 0
$unknown = 0
$falsified = 0
$probeNo = 0

function Write-Out {
    param([AllowEmptyString()][string]$Message)
    [Console]::Out.WriteLine($Message)
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
$TmpRoot = Join-Path $ScratchRoot 'queue-selfcheck'
if (-not (Test-Path -LiteralPath $TmpRoot)) {
    New-Item -ItemType Directory -Path $TmpRoot -Force | Out-Null
}
$stamp = (Get-Date).ToString('yyyyMMdd-HHmmss')

$ValidQueue = @(
    '# Coada de test',
    '',
    '### [TASK-TEST-001] Ticheta de test',
    'cerut de: local | data: 2026-10-27',
    'scope: cloud',
    'ce trebuie: Fa un lucru oarecare, in cifre, si spune ce ai masurat.',
    'livrare: QUEUE/DONE/TASK-TEST-001.md',
    ''
) -join "`n"

$ValidDrive = @(
    '# TASKURI PENTRU CLOUD',
    '',
    '## TASK-TEST-001',
    '',
    '- **Emit:** Mavis Local',
    ''
) -join "`n"

# The live contract of the Cloud, WITH the ticket already delivered. A
# fixture where the ticket is missing in the Cloud's queue is probe 12.
$LiveContract = @(
    '# Coada Cloud (fixture)',
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
    '## Tichete',
    '',
    '### [TASK-TEST-001] Ticheta de test',
    'cerut de: local | data: 2026-10-27',
    'scope: cloud',
    'ce trebuie: Fa un lucru oarecare, in cifre, si spune ce ai masurat.',
    'livrare: QUEUE/DONE/TASK-TEST-001.md',
    ''
) -join "`n"

# The same contract, but the ticket never arrived.
$LiveContractNoTicket = @(
    '# Coada Cloud (fixture)',
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
    ''
) -join "`n"

$DriftedContract = @(
    '# Coada Cloud (fixture, contract derivat)',
    '',
    '## Format',
    '',
    '```',
    '### [id] titlu',
    'cerut de: local | data: YYYY-MM-DD',
    'scope: cloud | local | ambele',
    'ce trebuie: ...',
    'output: unde trebuie sa ajunga rezultatul',
    '```',
    '',
    '## Tichete',
    '',
    '### [TASK-TEST-001] Ticheta de test',
    'cerut de: local | data: 2026-10-27',
    'scope: cloud',
    'ce trebuie: Fa un lucru oarecare, in cifre, si spune ce ai masurat.',
    'livrare: QUEUE/DONE/TASK-TEST-001.md',
    ''
) -join "`n"

$ValidSkill = @(
    '# mavis-cloud-to-local-reporting',
    '',
    '1. `git pull --rebase origin main` - mereu primul.',
    '2. Citeste `QUEUE/TASKS-FOR-CLOUD.md`',
    '3. Executa tichetele cu `scope: cloud`',
    ''
) -join "`n"

$SkillWithoutQueue = @(
    '# mavis-cloud-to-local-reporting',
    '',
    '1. Citeste fisierul de sarcini de la adresa configurata.',
    '2. Executa sarcinile.',
    ''
) -join "`n"

function New-Fixture {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [string]$QueueText = '',
        [string]$DriveText = '',
        [bool]$WithDone = $true,
        [bool]$WithLive = $true,
        [string]$LiveText = '',
        [bool]$WithSkill = $true,
        [string]$SkillText = ''
    )
    $r = Join-Path $TmpRoot $Name
    New-Item -ItemType Directory -Path (Join-Path $r 'QUEUE') -Force | Out-Null
    New-Item -ItemType Directory -Path (Join-Path $r 'BRIDGE-DRIVE') -Force | Out-Null
    New-Item -ItemType Directory -Path (Join-Path $r 'docs') -Force | Out-Null
    $enc = New-Object System.Text.UTF8Encoding($false)
    if (-not $QueueText) { $QueueText = $ValidQueue }
    if (-not $DriveText) { $DriveText = $ValidDrive }
    if (-not $LiveText) { $LiveText = $LiveContract }
    if (-not $SkillText) { $SkillText = $ValidSkill }
    [System.IO.File]::WriteAllText((Join-Path $r 'QUEUE\TASKS-FOR-CLOUD.md'), $QueueText, $enc)
    [System.IO.File]::WriteAllText((Join-Path $r 'BRIDGE-DRIVE\TASKURI-PENTRU-CLOUD.md'), $DriveText, $enc)
    [System.IO.File]::Copy($RealSnapshot, (Join-Path $r 'docs\CONTRACT-CLOUD-QUEUE.md'), $true)
    if ($WithDone) {
        New-Item -ItemType Directory -Path (Join-Path $r 'QUEUE\DONE') -Force | Out-Null
    }
    if ($WithLive) {
        New-Item -ItemType Directory -Path (Join-Path $r 'cloud-ingest\MAVIS-CLOUD\QUEUE') -Force | Out-Null
        [System.IO.File]::WriteAllText((Join-Path $r 'cloud-ingest\MAVIS-CLOUD\QUEUE\TASKS-FOR-CLOUD.md'), $LiveText, $enc)
    }
    if ($WithSkill) {
        $skillDir = Join-Path $r 'cloud-ingest\MAVIS-CLOUD\.skills\mavis-cloud-to-local-reporting'
        New-Item -ItemType Directory -Path $skillDir -Force | Out-Null
        [System.IO.File]::WriteAllText((Join-Path $skillDir 'SKILL.md'), $SkillText, $enc)
    }
    return $r
}

function Invoke-Gate {
    param([Parameter(Mandatory = $true)][string]$GateRoot)
    $prev = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    $out = & powershell -NoProfile -File $Gate -Root $GateRoot 2>&1
    $ErrorActionPreference = $prev
    $code = $LASTEXITCODE
    if ($null -eq $code) { $code = -1 }
    $text = ''
    if ($out) { $text = ([string]::Join("`n", @($out))) }
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

# --- 1. the gate must be able to PASS ------------------------------------
$f1 = New-Fixture -Name ('run-' + $stamp + '-p01')
$r1 = Invoke-Gate -GateRoot $f1
Test-Probe -Label 'coada conforma, contract live prezent, ticheta livrata' -Expected 0 -Actual $r1.Code

# --- 2. a ticket with no scope -------------------------------------------
$q2 = ($ValidQueue -split "`n" | Where-Object { $_ -notmatch '^scope:' }) -join "`n"
$f2 = New-Fixture -Name ('run-' + $stamp + '-p02') -QueueText $q2
$r2 = Invoke-Gate -GateRoot $f2
Test-Probe -Label 'ticheta fara scope' -Expected 1 -Actual $r2.Code

# --- 3. a ticket with an unknown scope -----------------------------------
$q3 = $ValidQueue -replace '(?m)^scope: cloud', 'scope: nebun'
$f3 = New-Fixture -Name ('run-' + $stamp + '-p03') -QueueText $q3
$r3 = Invoke-Gate -GateRoot $f3
Test-Probe -Label 'ticheta cu scope necunoscut' -Expected 1 -Actual $r3.Code

# --- 4. a ticket with no livrare -----------------------------------------
$q4 = ($ValidQueue -split "`n" | Where-Object { $_ -notmatch '^livrare:' }) -join "`n"
$f4 = New-Fixture -Name ('run-' + $stamp + '-p04') -QueueText $q4
$r4 = Invoke-Gate -GateRoot $f4
Test-Probe -Label 'ticheta fara livrare' -Expected 1 -Actual $r4.Code

# --- 5. the measured truncation: the instruction ends mid-sentence -------
$q5 = $ValidQueue -replace 'ce trebuie: .*', 'ce trebuie: Fa un lucru oarecare, in cifre, si spune ce ai masurat'
$q5 = $q5 -replace 'masurat\.', 'masurat'
$f5 = New-Fixture -Name ('run-' + $stamp + '-p05') -QueueText $q5
$r5 = Invoke-Gate -GateRoot $f5
Test-Probe -Label 'instructiune trunchiata la mijlocul propozitiei' -Expected 1 -Actual $r5.Code

# --- 6. no delivery target ----------------------------------------------
$f6 = New-Fixture -Name ('run-' + $stamp + '-p06') -WithDone $false
$r6 = Invoke-Gate -GateRoot $f6
Test-Probe -Label 'lipseste QUEUE/DONE' -Expected 1 -Actual $r6.Code

# --- 7. the ticket id is not in the primary channel ----------------------
$d7 = @('# TASKURI PENTRU CLOUD', '', '## TASK-ALTCEVA', '') -join "`n"
$f7 = New-Fixture -Name ('run-' + $stamp + '-p07') -DriveText $d7
$r7 = Invoke-Gate -GateRoot $f7
Test-Probe -Label 'id de ticheta absent din canalul primar' -Expected 1 -Actual $r7.Code

# --- 8. the live contract cannot be read: UNKNOWN, never a pass ----------
$f8 = New-Fixture -Name ('run-' + $stamp + '-p08') -WithLive $false
$r8 = Invoke-Gate -GateRoot $f8
Test-Probe -Label 'contract live ilizibil -> UNKNOWN, nu succes' -Expected 2 -Actual $r8.Code

# --- 9. the live contract drifted from the snapshot ----------------------
$f9 = New-Fixture -Name ('run-' + $stamp + '-p09') -LiveText $DriftedContract
$r9 = Invoke-Gate -GateRoot $f9
Test-Probe -Label 'contract live derivat fata de snapshot' -Expected 1 -Actual $r9.Code

# --- 10. a ticket written in a format the contract cannot read -----------
$q11 = (@('# Coada de test', '', '## TASK-VECHI-001', '', '- **Emit:** Mavis Local', '') -join "`n")
$f11 = New-Fixture -Name ('run-' + $stamp + '-p10') -QueueText $q11
$r11 = Invoke-Gate -GateRoot $f11
Test-Probe -Label 'antet de ticheta in format nerecunoscut (invizibil pentru Cloud)' -Expected 1 -Actual $r11.Code

# --- 11. the real repository ---------------------------------------------
$r10 = Invoke-Gate -GateRoot $RealRoot
if ($r10.Code -eq 0) {
    $falsified++
    Write-Out 'OK   proba-11 repo-ul real -> exit 0 (coada e conforma, contractul nu a derivat, tichetele sunt livrate)'
} elseif ($r10.Code -eq 2) {
    $unknown++
    Write-Out 'UNKNOWN proba-11 repo-ul real -> exit 2 (contractul live al Cloud-ului nu e accesibil de aici; conformitatea cozii a fost masurata, driftul nu)'
} else {
    $problems++
    Write-Out ('FAIL proba-11 repo-ul real -> exit ' + $r10.Code)
    Write-Out ($r10.Out.Trim())
}

# --- 12. the ticket never reached the Cloud's own queue ------------------
# MEASURED 2026-10-27: the queue was perfect and the Cloud read nothing
# from it. This probe is the one that sees the absence.
$f12 = New-Fixture -Name ('run-' + $stamp + '-p12') -LiveText $LiveContractNoTicket
$r12 = Invoke-Gate -GateRoot $f12
Test-Probe -Label 'ticheta nu a ajuns in coada repo-ului Cloud-ului' -Expected 1 -Actual $r12.Code

# --- 13. the Cloud moved its entry path ----------------------------------
$f13 = New-Fixture -Name ('run-' + $stamp + '-p13') -SkillText $SkillWithoutQueue
$r13 = Invoke-Gate -GateRoot $f13
Test-Probe -Label 'skillul Cloud-ului nu mai declara coada drept cale de intrare' -Expected 1 -Actual $r13.Code

# --- 14. the Cloud's skill cannot be read: UNKNOWN, never a pass ---------
$f14 = New-Fixture -Name ('run-' + $stamp + '-p14') -WithSkill $false
$r14 = Invoke-Gate -GateRoot $f14
Test-Probe -Label 'skillul Cloud-ului ilizibil -> UNKNOWN, nu succes' -Expected 2 -Actual $r14.Code

Write-Out ('QUEUE_GATE_PROBLEMS=' + $problems + ' UNKNOWN=' + $unknown + ' FALSIFIED=' + $falsified)
if ($problems -gt 0) {
    Write-Out 'POARTA A BLOCAT. Poarta cozii nu poate fi considerata de incredere pana nu se repara.'
    exit 1
}
Write-Out ('Fixture-urile probelor raman in ' + $TmpRoot + ' pentru inspectie.')
exit 0
