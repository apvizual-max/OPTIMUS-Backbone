# queue-contract-check.ps1
# The gate for the SECONDARY channel (GitHub) of the Local<->Cloud bridge.
#
# What it checks, and why each one exists:
#
#   1. CONTRACT CONFORMITY: every ticket in QUEUE/TASKS-FOR-CLOUD.md must
#      carry the five fields the Cloud actually parses:
#      cerut de / data / scope / ce trebuie / livrare.
#      MEASURED 2026-10-27: the CI queue had ZERO of the five. The Cloud
#      executes only tickets with "scope: cloud" - so it would have
#      executed ZERO tickets and reported nothing wrong.
#   2. SCOPE VALUE: scope must be one of cloud / local / ambele. A ticket
#      with a scope the Cloud does not know is not executable either.
#   3. COMPLETENESS: the value of "ce trebuie" must not end mid-sentence.
#      MEASURED 2026-10-27: the last ticket in BOTH channels ended with
#      "Nu intai" - a half instruction - because the publisher accepted a
#      truncated body and wrote it to both channels, reporting success.
#   4. DELIVERY TARGET: QUEUE/DONE/ must exist. MEASURED 2026-10-27: it did
#      not exist in the CI repo, while the Cloud writes its results there.
#   5. DUAL CHANNEL PARITY: every ticket id in the queue must also appear
#      in the Drive channel file. That is the executable form of the rule
#      "same TASK_ID, two channels" - a rule in prose is not a rule.
#   6. CONTRACT DRIFT: the contract is read LIVE from the Cloud's own
#      files when they are reachable, and compared with the local snapshot
#      (docs/CONTRACT-CLOUD-QUEUE.md). If the Cloud changed its format and
#      nobody noticed, the snapshot would be a beautiful lie.
#   7. DELIVERY: every ticket id must be present in the queue OF THE CLOUD'S
#      OWN REPOSITORY, read at the tip of the remote branch.
#      MEASURED 2026-10-27: this is the probe that was MISSING. The queue
#      was perfectly formed - all five fields, right scope, complete
#      instruction - and it sat in the CI repo, which the Cloud never
#      reads. 2 tickets local, 0 in the Cloud's queue, and the gate said
#      everything was fine. A queue can be well formed and perfectly
#      absent. This probe is the one that sees the absence.
#   8. THE ENTRY PATH: the Cloud's own skill must still declare
#      QUEUE/TASKS-FOR-CLOUD.md as its entry path. If the Cloud moves it,
#      the delivery lands where nobody reads.
#
# Exit codes:
#   0 = measured and true: tickets conform, they are delivered, contract has
#       not drifted
#   1 = at least one ticket breaks the contract, is not delivered, or the
#       contract drifted
#   2 = the measurement is incomplete (the live contract is unreadable).
#       This is NOT a pass: an unmeasured state must never be reported as
#       a healthy one.
#
# ASCII ONLY: executed by Windows PowerShell 5.1.

param(
    [string]$Root = '',
    [string]$CloudRoot = '',
    [string]$QueueFile = '',
    [string]$DoneDir = '',
    [string]$DriveChannel = '',
    [string]$ContractSnapshot = '',
    [string]$Remote = 'origin',
    [string]$Branch = 'main'
)

$ErrorActionPreference = 'Stop'

# A terminating error must not leave a verdict-shaped exit code behind.
trap {
    [Console]::Error.WriteLine('ERROR=executia s-a oprit: ' + $_.Exception.Message)
    if ($_.InvocationInfo) { [Console]::Error.WriteLine('LINIE: ' + $_.InvocationInfo.Line.Trim()) }
    exit 2
}

$Lib = Join-Path $PSScriptRoot 'queue-lib.ps1'
if (-not (Test-Path -LiteralPath $Lib)) {
    [Console]::Error.WriteLine('ERROR=lipseste scripts\queue-lib.ps1: ' + $Lib)
    exit 2
}
. $Lib

if (-not $Root) { $Root = Split-Path -Parent $PSScriptRoot }
if (-not $QueueFile) { $QueueFile = Join-Path $Root 'QUEUE\TASKS-FOR-CLOUD.md' }
if (-not $DoneDir) { $DoneDir = Join-Path $Root 'QUEUE\DONE' }
if (-not $DriveChannel) { $DriveChannel = Join-Path $Root 'BRIDGE-DRIVE\TASKURI-PENTRU-CLOUD.md' }
if (-not $ContractSnapshot) { $ContractSnapshot = Join-Path $Root 'docs\CONTRACT-CLOUD-QUEUE.md' }
if (-not $CloudRoot) { $CloudRoot = Join-Path $Root 'cloud-ingest\MAVIS-CLOUD' }

$problems = 0
$unknown = 0

# --- 0. required inputs ---------------------------------------------------
foreach ($f in @(@{ P = $QueueFile; N = 'coada' }, @{ P = $ContractSnapshot; N = 'snapshot contract' })) {
    if (-not (Test-Path -LiteralPath $f.P)) {
        Write-Out ('EROARE: lipseste ' + $f.N + ': ' + $f.P)
        exit 2
    }
}

# --- 1. the contract, live and snapshotted --------------------------------
$snapshotText = [System.IO.File]::ReadAllText($ContractSnapshot)
$required = @(Get-ContractFields -Text $snapshotText)
if ($required.Count -eq 0) {
    Write-Out ('EROARE: snapshotul contractului nu are blocul "## Format": ' + $ContractSnapshot)
    exit 2
}

# The live sources are read at the TIP of the Cloud's remote branch, which
# is what the Cloud reads after its own pull. A working tree can be many
# commits behind that tip, and a delivery that was never pushed is invisible
# to the Cloud.
$liveQueue = Get-CloudFileLive -CloudRoot $CloudRoot -Remote $Remote -Branch $Branch -RelativePath 'QUEUE/TASKS-FOR-CLOUD.md'
$liveSkill = Get-CloudFileLive -CloudRoot $CloudRoot -Remote $Remote -Branch $Branch -RelativePath '.skills/mavis-cloud-to-local-reporting/SKILL.md'

$known = @($required) + @('detalii')

$contractSource = 'LOCAL-SNAPSHOT'
$drift = 'UNKNOWN'
$liveFields = @()
if ($liveQueue.Text) {
    $contractSource = $liveQueue.Source
    $liveFields = @(Get-ContractFields -Text $liveQueue.Text)
    if ($liveFields.Count -eq 0) {
        $drift = 'UNKNOWN'
    } else {
        $same = ($liveFields.Count -eq $required.Count)
        if ($same) {
            foreach ($f in $required) { if ($liveFields -notcontains $f) { $same = $false } }
        }
        if ($same) { $drift = 'NO' } else { $drift = 'YES' }
    }
} else {
    $contractSource = 'MAVIS-CLOUD-LIVE-UNREADABLE'
}

Write-Out ('CONTRACT_SOURCE=' + $contractSource)
Write-Out ('CONTRACT_FIELDS=' + ($required -join '|'))
Write-Out ('CONTRACT_DRIFT=' + $drift)
if ($drift -eq 'YES') {
    $problems++
    Write-Out ('FAIL contract - contractul live al Cloud-ului difera de snapshot: live=[' + ($liveFields -join '|') + '] snapshot=[' + ($required -join '|') + ']')
} elseif ($drift -eq 'UNKNOWN') {
    $unknown++
    Write-Out 'UNKNOWN contract - contractul live al Cloud-ului nu a putut fi citit, deci driftul nu poate fi masurat'
}

# --- 2. the tickets -------------------------------------------------------
$queueText = [System.IO.File]::ReadAllText($QueueFile)
$qLines = $queueText -split "`r?`n"

$driveText = ''
if (Test-Path -LiteralPath $DriveChannel) {
    $driveText = [System.IO.File]::ReadAllText($DriveChannel)
} else {
    Write-Out ('FAIL canal primar lipsa: ' + $DriveChannel)
}

$tickets = @(Get-QueueTickets -Text $queueText -Known $required)

$ticketProblems = 0
foreach ($t in $tickets) {
    $id = $t.Id
    $label = 'ticheta [' + $id + ']'
    $bad = $false

    if (-not $id) { Write-Out ('FAIL ' + $label + ' - id gol'); $bad = $true }
    if (-not $t.Title.Trim()) { Write-Out ('FAIL ' + $label + ' - titlu gol'); $bad = $true }

    $fields = $t.Fields
    foreach ($f in $required) {
        $key = $f.ToLower()
        if (-not $fields.Contains($key) -or -not ([string]$fields[$key]).Trim()) {
            Write-Out ('FAIL ' + $label + ' - campul obligatoriu "' + $f + '" lipseste sau e gol')
            $bad = $true
        }
    }

    if ($fields.Contains('scope') -and ([string]$fields['scope']).Trim()) {
        $sv = (([string]$fields['scope']) -split '\|')[0].Trim().ToLower()
        if ($sv -ne 'cloud' -and $sv -ne 'local' -and $sv -ne 'ambele') {
            Write-Out ('FAIL ' + $label + ' - valoarea scope necunoscuta: "' + $sv + '" (Cloud ruleaza doar cloud/local/ambele)')
            $bad = $true
        }
    }

    if ($fields.Contains('ce trebuie') -and ([string]$fields['ce trebuie']).Trim()) {
        if (-not (Test-ValueComplete -Value ([string]$fields['ce trebuie']))) {
            Write-Out ('FAIL ' + $label + ' - valoarea "ce trebuie" se termina la mijlocul propozitiei (instructiune trunchiata)')
            $bad = $true
        }
    }
    if ($fields.Contains('detalii') -and ([string]$fields['detalii']).Trim()) {
        if (-not (Test-ValueComplete -Value ([string]$fields['detalii']))) {
            Write-Out ('FAIL ' + $label + ' - valoarea "detalii" se termina la mijlocul propozitiei')
            $bad = $true
        }
    }

    if ($id -and $driveText) {
        if ($driveText -notmatch [regex]::Escape($id)) {
            Write-Out ('FAIL ' + $label + ' - idul nu apare in canalul primar (BRIDGE-DRIVE); regula "acelasi TASK_ID in ambele canale" e incalcata')
            $bad = $true
        }
    }

    if ($bad) { $ticketProblems++ }
}

# --- 2b. headers the Cloud's contract does not recognize -----------------
# A ticket written in the old "## TASK-..." style is INVISIBLE to the
# Cloud: the contract only recognizes "### [id] titlu". MEASURED
# 2026-10-27: the whole CI queue was written that way - two tickets,
# both invisible - so a queue that "looks full" can be empty for the only
# reader that matters. Counting them is the only way to see it.
$legacy = 0
foreach ($line in $qLines) {
    if ($line -match '^\#{1,6}\s+TASK-') { $legacy++ }
}
if ($legacy -gt 0) {
    $problems++
    Write-Out ('FAIL coada - ' + $legacy + ' antet( uri) de ticheta in format pe care contractul Cloud-ului nu-l recunoaste ("## TASK-..."): invizibile pentru Cloud')
}
Write-Out ('UNRECOGNISED_HEADERS=' + $legacy)

Write-Out ('TICKETS=' + $tickets.Count)
Write-Out ('TICKET_PROBLEMS=' + $ticketProblems)
$problems += $ticketProblems

# --- 3. the delivery target ----------------------------------------------
if (Test-Path -LiteralPath $DoneDir) {
    Write-Out ('DONE_DIR=present ' + $DoneDir)
} else {
    Write-Out ('FAIL DONE_DIR lipseste: ' + $DoneDir + ' - Cloud-ul scrie rezultatele acolo')
    $problems++
}

# --- 4. the file must not be cut mid-write -------------------------------
$raw = [System.IO.File]::ReadAllBytes($QueueFile)
if ($raw.Length -gt 0 -and $raw[$raw.Length - 1] -ne 10) {
    Write-Out 'FAIL coada - fisierul nu se termina cu newline (scriere trunchiata la mijlocul unei linii)'
    $problems++
}
$lastLine = ''
foreach ($l in $qLines) { if ($l.Trim()) { $lastLine = $l.Trim() } }
if ($lastLine) {
    $m = [regex]::Match($lastLine, '^\s*([a-z][a-z ]{1,14})\s*:\s*(.*)$')
    if ($m.Success -and -not $m.Groups[2].Value.Trim()) {
        Write-Out ('FAIL coada - ultima linie declara campul "' + $m.Groups[1].Value.Trim() + '" cu valoare goala (scriere trunchiata)')
        $problems++
    }
}

# --- 5. THE DELIVERY: did the tickets reach the Cloud's own repo? --------
# MEASURED 2026-10-27: this probe was missing, and its absence is why a
# perfect queue was reported as healthy while the Cloud read zero tickets
# from it. The Cloud pulls its OWN repo and reads the queue from there, so
# the queue of that repo is the thing that must contain the ids.
$deliveredCount = 0
$notDelivered = New-Object System.Collections.Generic.List[string]
foreach ($t in $tickets) {
    if (-not $t.Id) { continue }
    if ($liveQueue.Text -and ($liveQueue.Text -match [regex]::Escape($t.Id))) {
        $deliveredCount++
    } else {
        $notDelivered.Add($t.Id)
    }
}
Write-Out ('DELIVERY_SOURCE=' + $liveQueue.Source)
Write-Out ('DELIVERED=' + $deliveredCount + '/' + $tickets.Count)

if (-not $liveQueue.Text) {
    $unknown++
    Write-Out 'UNKNOWN livrare - coada repo-ului Cloud-ului nu poate fi citita; livrarea nu poate fi masurata'
} elseif (-not $liveQueue.Definitive) {
    $unknown++
    Write-Out 'UNKNOWN livrare - sursa cozii Cloud-ului poate fi mai veche decat varful remote-ului; livrarea nu poate fi masurata'
} else {
    foreach ($id in $notDelivered) {
        Write-Out ('FAIL livrare - ticheta [' + $id + '] nu este in coada repo-ului Cloud-ului. Cloud-ul citeste acolo, nu in repo-ul CI.')
        $problems++
    }
}

# --- 6. the Cloud's entry path -------------------------------------------
if (-not $liveSkill.Text) {
    $unknown++
    Write-Out 'UNKNOWN cale de intrare - skillul Cloud-ului nu poate fi citit'
} elseif ($liveSkill.Text -notmatch 'QUEUE/TASKS-FOR-CLOUD\.md') {
    $problems++
    Write-Out 'FAIL cale de intrare - skillul Cloud-ului nu mai declara QUEUE/TASKS-FOR-CLOUD.md drept calea de intrare'
} else {
    Write-Out 'CLOUD_ENTRY=QUEUE/TASKS-FOR-CLOUD.md'
}

# --- verdict --------------------------------------------------------------
Write-Out ('QUEUE_PROBLEMS=' + $problems + ' UNKNOWN=' + $unknown)
if ($problems -gt 0) {
    Write-Out 'POARTA A BLOCAT. Coada secundara nu e executabila de Cloud pana nu se repara.'
    exit 1
}
if ($unknown -gt 0) {
    Write-Out 'Porta a trecut pe masuratorile care au putut rula, dar contractul live nu a putut fi comparat. Necunoscutul se raporteaza, nu se presupune.'
    exit 2
}
Write-Out 'Coada secundara e executabila de Cloud: toate tichetele au cele cinci campuri, scopul, instructiunea completa, tinta de livrare, SI sunt in coada repo-ului Cloud-ului.'
exit 0
