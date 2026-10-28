# mavis-sync-selfcheck.ps1
# The gate for the daily Local<->Cloud bridge (mavis-sync.ps1).
#
# What it checks, and why each one exists:
#
#   1. ASCII purity + parse + exit-code contamination.
#   2. PATH INDEPENDENCE: the script must resolve its own root from
#      $PSScriptRoot. MEASURED 2026-10-27: the path was hardcoded on
#      '...\projects\Mavis-Optimus-Continuous-Integration' - a folder that
#      was REMOVED in the E: consolidation. The daily bridge (08:30 task)
#      printed "clone-ul Cloud lipseste" and exited 1: a working transport,
#      with a dead path inside it. A hardcoded path is a path that dies.
#   3. OWN EXIT CODE: the script must end with an explicit `exit`. A script
#      that ends without one INHERITS $LASTEXITCODE from the last native
#      command - and an inherited verdict belongs to the previous gate.
#   4. HONEST LABEL: the commit message must not claim content it does not
#      carry. MEASURED 2026-10-27: cloud-ingest/ is gitignored, so the
#      commit can never contain cloud bytes - yet the message said
#      "cloud: ingest ... (citire read-only din MAVIS-CLOUD)". The first
#      run labelled a script repair as an ingest.
#
# The probe is bidirectional: the checks must PASS on the real script, and
# a DOCTORED copy must FAIL them. A check that cannot fail is not a check.
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

$Sync = Join-Path $ScriptsDir 'mavis-sync.ps1'
if (-not (Test-Path -LiteralPath $Sync)) {
    Write-Output ('EROARE: lipseste ' + $Sync)
    exit 2
}

$problems = 0
$unknown = 0
$falsified = 0

function Test-Text {
    param([string]$Text)
    $results = @{}
    # Doar CODUL EXECUTABIL conteaza. Un comentariu poate si trebuie sa
    # NUMEASCA calea veche - altfel istoricul defectului s-ar pierde. Un
    # detector care citeste comentariile ar reprosa propria documentatie.
    $code = ($Text -split "`n" |
             Where-Object { $_ -notmatch '^\s*#' } |
             Where-Object { $_ -notmatch '^\s*$' }) -join "`n"
    $results.PathHardcoded = ($code -match 'Mavis-Optimus-Continuous-Integration')
    $results.NoPSScriptRoot = (-not ($code -match '\$PSScriptRoot'))
    $results.HasExit = ($Text -match '(?m)^\s*exit\s+\d')
    $results.FalseIngestLabel = ($code -match 'cloud:\s*ingest')
    return $results
}

# --- 1. static checks ----------------------------------------------------
$bytes = [System.IO.File]::ReadAllBytes($Sync)
$nonAscii = 0
$firstBad = -1
for ($i = 0; $i -lt $bytes.Count; $i++) {
    if ($bytes[$i] -gt 127) {
        $nonAscii++
        if ($firstBad -lt 0) { $firstBad = $i }
    }
}
$errs = $null
$null = [System.Management.Automation.Language.Parser]::ParseFile($Sync, [ref]$null, [ref]$errs)
$parseCount = 0
if ($errs) { $parseCount = $errs.Count }

$raw = [System.IO.File]::ReadAllText($Sync)
$exitVar = [regex]::Match($raw, '(?m)^\s*exit\s+\$(\w+)\s*$')
$contaminated = $false
if ($exitVar.Success) {
    $name = $exitVar.Groups[1].Value
    $fromCall = [regex]::IsMatch($raw, ('(?m)^\s*\$' + $name + '\s*=\s*[A-Za-z_][A-Za-z0-9_\-]*\s*$'))
    $usesStream = [regex]::IsMatch($raw, '(?m)^\s*Write-Output\b')
    if ($fromCall -and $usesStream) { $contaminated = $true }
}

if ($nonAscii -gt 0 -or $parseCount -gt 0 -or $contaminated) {
    $problems++
    Write-Output ('FAIL mavis-sync.ps1 - bytes=' + $bytes.Count + ' nonascii=' + $nonAscii + ' parseErrors=' + $parseCount + ' exitContaminated=' + $contaminated)
    if ($nonAscii -gt 0) { Write-Output ('     primul octet > 0x7F la pozitia ' + $firstBad) }
    if ($errs) {
        foreach ($e in $errs) {
            Write-Output ('     L' + $e.Extent.StartLineNumber + 'C' + $e.Extent.StartColumnNumber + ': ' + $e.Message)
        }
    }
} else {
    Write-Output ('OK   mavis-sync.ps1 - bytes=' + $bytes.Count + ' nonascii=0 parseErrors=0 exitContaminated=false')
}

# --- 2. PATH INDEPENDENCE ------------------------------------------------
$real = Test-Text -Text $raw
if ($real.PathHardcoded) {
    $problems++
    Write-Output 'FAIL proba-cale - scriptul contine calea absoluta a folderului eliminat'
} elseif ($real.NoPSScriptRoot) {
    $problems++
    Write-Output 'FAIL proba-cale - scriptul nu-si deriva radacina din $PSScriptRoot'
} else {
    Write-Output 'OK   proba-cale - radacina e derivata din $PSScriptRoot, nu hardcodata'
}

# --- 3. OWN EXIT CODE ----------------------------------------------------
if ($real.HasExit) {
    Write-Output 'OK   proba-iesire - scriptul are un exit explicit, deci codul lui e propriu'
} else {
    $problems++
    Write-Output 'FAIL proba-iesire - scriptul se termina fara exit, deci mosteneste $LASTEXITCODE'
}

# --- 4. HONEST LABEL -----------------------------------------------------
if ($real.FalseIngestLabel) {
    $problems++
    Write-Output 'FAIL proba-eticheta - mesajul de commit afirma continut din cloud, dar cloud-ingest/ e gitignored'
} else {
    Write-Output 'OK   proba-eticheta - mesajul de commit nu afirma continut din cloud'
}

# --- 5. FALSIFICATION: a doctored copy must be REJECTED ------------------
# The expectation lives HERE; the report is produced by the check above.
# Their agreement is the evidence, and a doctored script must be caught -
# otherwise the check above cannot fail.
$doctored = @(
    @{ Label = 'cale hardcodata pe folderul eliminat'; Text = "`$HQ = 'C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Continuous-Integration'`n"; Expect = 'PathHardcoded' },
    @{ Label = 'fara derivare din $PSScriptRoot'; Text = "`$HQ = 'C:\somewhere\else'`n"; Expect = 'NoPSScriptRoot' },
    @{ Label = 'fara exit explicit'; Text = "`$HQ = Split-Path -Parent `$PSScriptRoot`n"; Expect = 'NoExit' },
    @{ Label = 'eticheta care afirma continut din cloud'; Text = "`$msg = 'cloud: ingest ' + (Get-Date)`n"; Expect = 'FalseIngestLabel' }
)
foreach ($d in $doctored) {
    $t = Test-Text -Text $d.Text
    $caught = $false
    switch ($d.Expect) {
        'PathHardcoded' { $caught = $t.PathHardcoded }
        'NoPSScriptRoot' { $caught = $t.NoPSScriptRoot }
        'NoExit' { $caught = (-not $t.HasExit) }
        'FalseIngestLabel' { $caught = $t.FalseIngestLabel }
    }
    if ($caught) {
        $falsified++
        Write-Output ('OK   proba-falsificare - ' + $d.Label + ' -> detectat')
    } else {
        $problems++
        Write-Output ('FAIL proba-falsificare - ' + $d.Label + ' -> NU a fost detectat')
    }
}

# --- 6. the bridge must still refuse to push ------------------------------
# The gate that forbids the push must stay forbidden. If a repair to the
# path broke the gate, the bridge would push without Popy's R0.
$prev = $ErrorActionPreference
$ErrorActionPreference = 'Continue'
$out = & powershell -NoProfile -File $Sync -SelfTest 2>&1
$ErrorActionPreference = $prev
$code = $LASTEXITCODE
if ($code -eq 0 -and (($out | Out-String) -match 'POARTA\|TRECUT')) {
    Write-Output 'OK   proba-poarta - poarta de interzicere a push-ului e intacta (SelfTest = POARTA|TRECUT)'
} else {
    $problems++
    Write-Output ('FAIL proba-poarta - poarta de push nu mai e intacta (exit ' + $code + ')')
}

Write-Output ('SYNC_PROBLEMS=' + $problems + ' UNKNOWN=' + $unknown + ' FALSIFIED=' + $falsified)
if ($problems -gt 0) {
    Write-Output 'POARTA A BLOCAT. Puntea zilnica nu se considera functionala pana nu se repara.'
    exit 1
}
Write-Output 'Puntea zilnica e functionala, iar poarta ei spune adevarul despre ce a masurat.'
exit 0
