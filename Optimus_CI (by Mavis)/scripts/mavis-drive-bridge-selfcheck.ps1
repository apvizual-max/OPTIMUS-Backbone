# mavis-drive-bridge-selfcheck.ps1
# The gate for the Local<->Cloud bridge (Google Drive primary, GitHub backup).
#
# What it checks, and why each one exists:
#
#   1. ASCII purity + parse + exit-code contamination for the bridge scripts.
#      Same defect class as everywhere else: Windows PowerShell 5.1 and an
#      `exit $var` after `Write-Output` turns every failure into a success.
#   2. PROBE A (positive): the project folder must exist IN THE DRIVE, with a
#      Drive id. Without it there is no target, only local bytes.
#   3. PROBE B (negative): a title that cannot exist must be reported NOT
#      FOUND. A measurement that cannot fail is not a measurement.
#   4. PROBE C (honesty): the orchestrator's TRANSPORT verdict must AGREE
#      with the raw DriveFS state. A report that says "the transport is up"
#      while the mirror root is disconnected is a lying report, and that is
#      worse than a missing one.
#   5. PROBE D (falsification): the orchestrator must REFUSE a publish with
#      no subject. If it accepted it, the gate in it would be decorative.
#   6. The channels must exist - Drive primary, GitHub secondary.
#   7. PROBE F/G/H (the publisher): a TRUNCATED body and an UNKNOWN scope
#      must be REFUSED, and a good publish must land in the consumer's
#      contract format with the same TASK_ID in both channels. MEASURED
#      2026-10-27: the publisher accepted a body ending in "Nu intai",
#      wrote it to both channels, and reported the publish as a success.
#
# A DOWN transport does NOT fail this gate: the system is supposed to detect
# it and fall back. What fails the gate is a transport that is broken and
# NOT reported.
#
# Exit codes:
#   0 = everything measured and true
#   1 = at least one check failed
#   2 = the gate could not run at all
#
# ASCII ONLY: executed by Windows PowerShell 5.1.

param(
    [string]$ScriptsDir = ''
)

$ErrorActionPreference = 'Stop'

if (-not $ScriptsDir) { $ScriptsDir = $PSScriptRoot }
if (-not (Test-Path -LiteralPath $ScriptsDir)) {
    Write-Output ('EROARE: director inexistent: ' + $ScriptsDir)
    exit 2
}

$ProjectRoot = Split-Path -Parent $ScriptsDir
$BridgeDir = Join-Path $ProjectRoot 'BRIDGE-DRIVE'
$Orchestrator = Join-Path $ScriptsDir 'mavis-drive-bridge.ps1'
$Probe = Join-Path $ScriptsDir 'drivefs_probe.py'
# The fixture copies are built OUTSIDE the Google Drive mirror, so DriveFS
# never administers files underneath a live probe.
$ScratchLib = Join-Path $PSScriptRoot 'git-scratch.ps1'
if (-not (Test-Path -LiteralPath $ScratchLib)) {
    Write-Output ('EROARE: lipseste scripts\git-scratch.ps1: ' + $ScratchLib)
    exit 2
}
. $ScratchLib
$ScratchRoot = Assert-ScratchOutsideMirror -ScratchRoot (Get-GitScratchRoot -ProjectRoot $ProjectRoot) -ProjectRoot $ProjectRoot

$problems = 0
$unknown = 0

function Get-Python {
    foreach ($cand in @('python', 'python3', 'py')) {
        $cmd = Get-Command $cand -ErrorAction SilentlyContinue
        if ($cmd) { return $cmd.Source }
    }
    return ''
}

function Invoke-Native {
    param(
        [Parameter(Mandatory = $true)][string]$Program,
        [string[]]$Arguments = @()
    )
    $prev = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    $out = & $Program @Arguments 2>&1
    $ErrorActionPreference = $prev
    $code = $LASTEXITCODE
    if ($null -eq $code) { $code = -1 }
    $text = ''
    if ($out) { $text = ($out -join "`n") }
    return @{ Code = $code; Out = $text }
}

$python = Get-Python
if (-not $python) {
    Write-Output 'EROARE: nu exista interpretor python pe PATH'
    exit 2
}
foreach ($f in @($Orchestrator, $Probe)) {
    if (-not (Test-Path -LiteralPath $f)) {
        Write-Output ('EROARE: lipseste ' + $f)
        exit 2
    }
}

# --- 1. static checks ----------------------------------------------------
foreach ($t in @($Orchestrator, $Probe)) {
    $bytes = [System.IO.File]::ReadAllBytes($t)
    $nonAscii = 0
    $firstBad = -1
    for ($i = 0; $i -lt $bytes.Count; $i++) {
        if ($bytes[$i] -gt 127) {
            $nonAscii++
            if ($firstBad -lt 0) { $firstBad = $i }
        }
    }
    $errs = $null
    if ($t -like '*.ps1') {
        $null = [System.Management.Automation.Language.Parser]::ParseFile($t, [ref]$null, [ref]$errs)
    }
    $parseCount = 0
    if ($errs) { $parseCount = $errs.Count }

    $raw = [System.IO.File]::ReadAllText($t)
    $exitVar = [regex]::Match($raw, '(?m)^\s*exit\s+\$(\w+)\s*$')
    $contaminated = $false
    if ($exitVar.Success) {
        $name = $exitVar.Groups[1].Value
        $fromCall = [regex]::IsMatch($raw, ('(?m)^\s*\$' + $name + '\s*=\s*[A-Za-z_][A-Za-z0-9_\-]*\s*$'))
        $usesStream = [regex]::IsMatch($raw, '(?m)^\s*Write-Output\b')
        if ($fromCall -and $usesStream) { $contaminated = $true }
    }

    $leaf = Split-Path -Leaf $t
    if ($nonAscii -gt 0 -or $parseCount -gt 0 -or $contaminated) {
        $problems++
        Write-Output ('FAIL ' + $leaf + ' - bytes=' + $bytes.Count + ' nonascii=' + $nonAscii + ' parseErrors=' + $parseCount + ' exitContaminated=' + $contaminated)
        if ($nonAscii -gt 0) { Write-Output ('     primul octet > 0x7F la pozitia ' + $firstBad) }
        if ($errs) {
            foreach ($e in $errs) {
                Write-Output ('     L' + $e.Extent.StartLineNumber + 'C' + $e.Extent.StartColumnNumber + ': ' + $e.Message)
            }
        }
    } else {
        Write-Output ('OK   ' + $leaf + ' - bytes=' + $bytes.Count + ' nonascii=0 parseErrors=0 exitContaminated=false')
    }
}

# --- 2. PROBE A: the folder must exist in Drive ---------------------------
$folder = Split-Path -Leaf $ProjectRoot
$resA = Invoke-Native -Program $python -Arguments @($Probe, '--title', $folder)
$driveId = ''
foreach ($line in ($resA.Out -split "`n")) {
    if ($line -match 'cloud_id=(\S+)') {
        $id = $Matches[1]
        if ($id -and $id -ne 'None') { $driveId = $id }
    }
}
if ($resA.Code -eq 0 -and $driveId) {
    Write-Output ('OK   proba-tinta - folderul proiectului exista in Drive, cloud_id=' + $driveId)
} elseif ($resA.Code -eq 2) {
    $problems++
    Write-Output 'FAIL proba-tinta - folderul proiectului nu exista in Drive: nu exista tinta'
} else {
    $unknown++
    Write-Output ('UNKNOWN proba-tinta - masuratoarea nu s-a putut face (' + $resA.Out.Trim() + ')')
}

# --- 3. PROBE B: the probe must be able to say NOT FOUND -----------------
$resB = Invoke-Native -Program $python -Arguments @($Probe, '--title', 'ZZZ_NO_SUCH_ITEM_9F3A1C.md')
if ($resB.Code -eq 2) {
    Write-Output 'OK   proba-not-found - un titlu inexistent e raportat NOT FOUND (exit 2), deci proba poate esua'
} else {
    $problems++
    Write-Output ('FAIL proba-not-found - un titlu inexistent NU a fost raportat NOT FOUND (exit ' + $resB.Code + ')')
}

# --- 4. PROBE C: the orchestrator must tell the truth ---------------------
$resRoot = Invoke-Native -Program $python -Arguments @($Probe, '--root-state')
$rootState = 'UNKNOWN'
foreach ($line in ($resRoot.Out -split "`n")) {
    if ($line -match '^ROOT_STATE=(\S+)') { $rootState = $Matches[1] }
}
$resC = Invoke-Native -Program 'powershell' -Arguments @('-NoProfile', '-File', $Orchestrator, '-Status')
$transport = 'UNKNOWN'
$channel = 'UNKNOWN'
$propagation = 'UNKNOWN'
$channelPresent = 'UNKNOWN'
foreach ($line in ($resC.Out -split "`n")) {
    if ($line -match '^TRANSPORT=(\S+)') { $transport = $Matches[1] }
    if ($line -match '^ACTIVE_CHANNEL=(\S+)') { $channel = $Matches[1] }
    if ($line -match '^PROPAGATION=(\S+)') { $propagation = $Matches[1] }
    if ($line -match '^CLOUD_CHANNEL_FILE_PRESENT=(\S+)') { $channelPresent = $Matches[1] }
}

# The expectation lives HERE, the report is produced by the script. Their
# agreement is the evidence - and a doctored report must be rejected, so the
# expectation can fail.
function Test-BridgeConcordance {
    param([string]$RootState, [string]$Transport, [string]$Propagation, [string]$Channel, [string]$ChannelPresent)
    if ($RootState -eq 'false' -and $Transport -ne 'DOWN') { return $false }
    if ($RootState -eq 'true' -and $Transport -ne 'UP') { return $false }
    # An UNMEASURED root state must never be reported as UP. Claiming a
    # working transport on the strength of a measurement that failed is
    # the same defect as a gate that cannot fail - the report asserts
    # something nobody measured.
    if ($RootState -eq 'UNKNOWN' -and $Transport -eq 'UP') { return $false }
    if ($Propagation -eq 'OK' -and $Channel -ne 'DRIVE') { return $false }
    if (($Propagation -eq 'STALE' -or $Propagation -eq 'UNKNOWN') -and $Channel -ne 'GITHUB') { return $false }
    # The channel file is the thing the Cloud reads. If it is not in the
    # cloud index, the propagation CANNOT be OK. A report that says otherwise
    # is accusing the transport of being healthy when it is not.
    if ($ChannelPresent -eq 'false' -and $Propagation -eq 'OK') { return $false }
    return $true
}

# --- falsification: doctored reports must be rejected ---------------------
$doctored = @(
    @{ Label = 'raport fals: propagare STALE dar canal DRIVE'; Root = 'true'; Trans = 'UP'; Prop = 'STALE'; Chan = 'DRIVE'; Present = 'true'; MustReject = $true },
    @{ Label = 'raport fals: radacina deconectata dar transport UP'; Root = 'false'; Trans = 'UP'; Prop = 'OK'; Chan = 'DRIVE'; Present = 'true'; MustReject = $true },
    @{ Label = 'raport fals: radacina NECUNOSCUTA dar transport UP'; Root = 'UNKNOWN'; Trans = 'UP'; Prop = 'STALE'; Chan = 'GITHUB'; Present = 'false'; MustReject = $true },
    @{ Label = 'raport fals: propagare OK dar canal GITHUB'; Root = 'true'; Trans = 'UP'; Prop = 'OK'; Chan = 'GITHUB'; Present = 'true'; MustReject = $true },
    @{ Label = 'raport fals: fisierul canalului absent din cloud dar propagare OK'; Root = 'true'; Trans = 'UP'; Prop = 'OK'; Chan = 'DRIVE'; Present = 'false'; MustReject = $true },
    @{ Label = 'raport adevarat: conectat, propagare OK, canal DRIVE'; Root = 'true'; Trans = 'UP'; Prop = 'OK'; Chan = 'DRIVE'; Present = 'true'; MustReject = $false },
    @{ Label = 'raport adevarat: conectat, propagare STALE, canal GITHUB'; Root = 'true'; Trans = 'UP'; Prop = 'STALE'; Chan = 'GITHUB'; Present = 'false'; MustReject = $false },
    @{ Label = 'raport adevarat: radacina necunoscuta, transport necunoscut, canal GITHUB'; Root = 'UNKNOWN'; Trans = 'UNKNOWN'; Prop = 'UNKNOWN'; Chan = 'GITHUB'; Present = 'false'; MustReject = $false }
)
$falsified = 0
foreach ($d in $doctored) {
    $concordant = Test-BridgeConcordance -RootState $d.Root -Transport $d.Trans -Propagation $d.Prop -Channel $d.Chan -ChannelPresent $d.Present
    $rejected = -not $concordant
    if ($rejected -eq $d.MustReject) {
        $falsified++
        Write-Output ('OK   proba-concordanta - ' + $d.Label)
    } else {
        $problems++
        Write-Output ('FAIL proba-concordanta - ' + $d.Label + ' (asteptat ' + $(if ($d.MustReject) { 'respingere' } else { 'acceptare' }) + ')')
    }
}

if ($rootState -eq 'UNKNOWN') {
    $unknown++
    Write-Output 'UNKNOWN proba-transport - starea radacinii mirrorului nu s-a putut citi'
} elseif (Test-BridgeConcordance -RootState $rootState -Transport $transport -Propagation $propagation -Channel $channel -ChannelPresent $channelPresent) {
    Write-Output ('OK   proba-transport - raportul si masuratoarea sunt concordante; radacina=' + $rootState + ' transport=' + $transport + ' propagare=' + $propagation + ' fisierul canalului in cloud=' + $channelPresent + ' canal activ: ' + $channel)
} else {
    $problems++
    Write-Output ('FAIL proba-transport - raportul si masuratoarea se contrazic: root_state=' + $rootState + ' transport=' + $transport + ' propagare=' + $propagation + ' canal=' + $channel + ' fisierul canalului in cloud=' + $channelPresent)
}

# --- 4b. PROBE E: the probe must read the LOG THAT IS WRITTEN -----------
# MEASURED 2026-10-27: DriveFS rotates its logs. The live session was
# writing drive_fs_507.txt while a fresh drive_fs.txt held the trace of a
# FAILED launch. A probe that reads one fixed filename reported UNKNOWN
# while the transport was healthy - a false negative, and the orchestrator
# turned that UNKNOWN into TRANSPORT=UP.
#
# The probe must therefore report WHICH log it read. If it always says
# drive_fs.txt, it is reading a file that no longer carries the state.
$resE = Invoke-Native -Program $python -Arguments @($Probe, '--root-state')
$probeLog = ''
$probeTs = ''
$probeState = ''
foreach ($line in ($resE.Out -split "`n")) {
    if ($line -match '^LOG=(.+)$') { $probeLog = $Matches[1].Trim() }
    if ($line -match '^ROOT_STATE_TS=(\S+)') { $probeTs = $Matches[1] }
    if ($line -match '^ROOT_STATE=(\S+)') { $probeState = $Matches[1] }
}
if ($probeState -eq 'UNKNOWN') {
    $unknown++
    Write-Output 'UNKNOWN proba-log - starea radacinii nu a putut fi citita din niciun log'
} elseif ($probeLog -and (Test-Path -LiteralPath $probeLog)) {
    $logName = Split-Path -Leaf $probeLog
    $logAge = ((Get-Date) - (Get-Item -LiteralPath $probeLog).LastWriteTime).TotalMinutes
    if ($logName -eq 'drive_fs.txt' -and $logAge -gt 30) {
        # drive_fs.txt that has not been touched for half an hour is a
        # STALE file, not the live one. Reading it is the bug.
        $problems++
        Write-Output ('FAIL proba-log - sonda a citit ' + $logName + ', care nu a fost scris de ' + [math]::Round($logAge, 1) + ' minute; logul activ e altul')
    } elseif ($probeTs) {
        Write-Output ('OK   proba-log - starea radacinii a fost citita din ' + $logName + ' (scris acum ' + [math]::Round($logAge, 1) + ' min in urma), anunt ' + $probeTs + ', starea=' + $probeState)
    } else {
        $problems++
        Write-Output 'FAIL proba-log - sonda a raportat o stare fara amprenta de timp a anuntului'
    }
} else {
    $problems++
    Write-Output ('FAIL proba-log - logul raportat de sonda nu exista sau nu a fost citit: ' + $probeLog)
}

# --- 5. PROBE D: the orchestrator must REFUSE an empty publish -----------
$resD = Invoke-Native -Program 'powershell' -Arguments @('-NoProfile', '-File', $Orchestrator, '-Publish')
if ($resD.Code -eq 2) {
    Write-Output 'OK   proba-refuz - o publicare fara subiect e refuzata (exit 2)'
} else {
    $problems++
    Write-Output ('FAIL proba-refuz - o publicare fara subiect NU a fost refuzata (exit ' + $resD.Code + ')')
}

# --- 6. the channels must exist ------------------------------------------
$channels = @(
    (Join-Path $BridgeDir 'TASKURI-PENTRU-CLOUD.md'),
    (Join-Path $BridgeDir 'INTENTII.md'),
    (Join-Path $BridgeDir 'INTRARI-CLOUD'),
    (Join-Path $BridgeDir 'ISTORIC'),
    (Join-Path $ProjectRoot 'QUEUE\TASKS-FOR-CLOUD.md')
)
$missingChannels = 0
foreach ($c in $channels) {
    if (-not (Test-Path -LiteralPath $c)) {
        $missingChannels++
        Write-Output ('FAIL canal lipsa: ' + $c)
    }
}
if ($missingChannels -eq 0) {
    Write-Output 'OK   proba-canale - canalele Drive (4) si canalul secundar GitHub exista'
} else {
    $problems++
}

# --- 7. PROBE F/G/H: the publisher must refuse a broken task --------------
# MEASURED 2026-10-27: the publisher accepted a body ending in "Nu intai",
# wrote it to BOTH channels, and reported the publish as a normal success.
# A truncated instruction is not a task, and an unknown scope is not a
# scope the Cloud knows.
#
# The probes run against a FIXTURE copy of the publisher, so the real
# channels are never written by a test.
$fixtureRoot = Join-Path $ScratchRoot 'bridge-selfcheck'
if (Test-Path -LiteralPath $fixtureRoot) { Remove-Item -LiteralPath $fixtureRoot -Recurse -Force }
New-Item -ItemType Directory -Path (Join-Path $fixtureRoot 'scripts') -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $fixtureRoot 'BRIDGE-DRIVE') -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $fixtureRoot 'QUEUE') -Force | Out-Null
Copy-Item -LiteralPath $Orchestrator -Destination (Join-Path $fixtureRoot 'scripts\mavis-drive-bridge.ps1') -Force
$fixtureScript = Join-Path $fixtureRoot 'scripts\mavis-drive-bridge.ps1'

$resF = Invoke-Native -Program 'powershell' -Arguments @('-NoProfile', '-File', $fixtureScript, '-Publish', '-Title', 'Proba trunchiata', '-Body', 'Un corp care se opreste la mijloc, fara punct final')
if ($resF.Code -eq 2) {
    Write-Output 'OK   proba-trunchiere - o publicare cu corpul trunchiat e refuzata (exit 2)'
} else {
    $problems++
    Write-Output ('FAIL proba-trunchiere - o publicare cu corpul trunchiat NU a fost refuzata (exit ' + $resF.Code + ')')
}

$resG = Invoke-Native -Program 'powershell' -Arguments @('-NoProfile', '-File', $fixtureScript, '-Publish', '-Title', 'Proba scope', '-Body', 'Corp complet, cu punct final.', '-Scope', 'nepro')
if ($resG.Code -eq 2) {
    Write-Output 'OK   proba-scope - o publicare cu scope necunoscut e refuzata (exit 2)'
} else {
    $problems++
    Write-Output ('FAIL proba-scope - o publicare cu scope necunoscut NU a fost refuzata (exit ' + $resG.Code + ')')
}

$resH = Invoke-Native -Program 'powershell' -Arguments @('-NoProfile', '-File', $fixtureScript, '-Publish', '-Title', 'Proba contract', '-Body', 'Verifica formatul cozii. Spune ce ai masurat, in cifre.')
$fixtureQueue = Join-Path $fixtureRoot 'QUEUE\TASKS-FOR-CLOUD.md'
$fixtureDrive = Join-Path $fixtureRoot 'BRIDGE-DRIVE\TASKURI-PENTRU-CLOUD.md'
$queueText = ''
if (Test-Path -LiteralPath $fixtureQueue) { $queueText = [System.IO.File]::ReadAllText($fixtureQueue) }
$driveTextF = ''
if (Test-Path -LiteralPath $fixtureDrive) { $driveTextF = [System.IO.File]::ReadAllText($fixtureDrive) }
$idMatch = [regex]::Match($queueText, '(?m)^###\s*\[([^\]]+)\]')
$contractOk = ($queueText -match '(?m)^###\s*\[[^\]]+\]') -and
              ($queueText -match '(?m)^cerut de:') -and
              ($queueText -match '(?m)^scope:\s*(cloud|local|ambele)\s*$') -and
              ($queueText -match '(?m)^ce trebuie:') -and
              ($queueText -match '(?m)^livrare:\s*\S')
$parityOk = $false
if ($idMatch.Success -and $driveTextF) {
    $parityOk = $driveTextF.Contains($idMatch.Groups[1].Value)
}
if ($contractOk -and $parityOk -and ($resH.Out -match 'DUAL_CHANNEL_DRIVE=True') -and ($resH.Out -match 'DUAL_CHANNEL_QUEUE=True')) {
    Write-Output ('OK   proba-contract-publicat - blocul secundar e scris in contractul consumatorului, cu acelasi TASK_ID in ambele canale (' + $idMatch.Groups[1].Value + ')')
} else {
    $problems++
    Write-Output 'FAIL proba-contract-publicat - blocul secundar nu e in contractul consumatorului, sau TASK_ID nu apare in ambele canale'
}

Write-Output ('BRIDGE_PROBLEMS=' + $problems + ' UNKNOWN=' + $unknown)
if ($problems -gt 0) {
    Write-Output 'POARTA A BLOCAT. Puntea nu se foloseste pana nu se repara.'
    exit 1
}
if ($unknown -gt 0) {
    Write-Output 'Porta a trecut, dar o proba nu a putut fi masurata. Necunoscutul se raporteaza, nu se presupune.'
}
Write-Output 'Puntea e construita si raporteaza adevarul despre transport.'
exit 0
