# ga-doctor.ps1 - the control point, on a schedule.
#
# ga-doctor.mjs is the instrument: one command, one verdict, nine checks.
# This wrapper is what the Task Scheduler runs, so the system keeps proving
# itself even when no session is open:
#
#   1. run the doctor,
#   2. append ONE dated line to logs\ga-doctor.log (UTF-8, no BOM),
#   3. exit with the doctor's own code, so a red system is visible in the
#      Task Scheduler's LastTaskResult and not only in a log.
#
# ASCII ONLY (Windows PowerShell 5.1). Write-Output contaminates
# $LASTEXITCODE here, so the line goes straight to the console handle.
param(
    [string]$Repo   = 'C:\Users\apviz\.minimax-agent\projects\Mavis-Google_Access',
    [string]$Data   = 'C:\Users\apviz\.minimax\google-access\data',
    [string]$LogDir = 'C:\Users\apviz\.minimax\google-access\logs'
)

$ErrorActionPreference = 'Continue'

$doctor = Join-Path $Repo 'scripts\ga-doctor.mjs'
if (-not (Test-Path -LiteralPath $doctor)) {
    [Console]::Error.WriteLine('FATAL doctor not found: ' + $doctor)
    exit 3
}

function Resolve-Node {
    $cmd = Get-Command node -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
    foreach ($p in @('C:\Program Files\nodejs\node.exe', 'C:\Program Files (x86)\nodejs\node.exe')) {
        if (Test-Path $p) { return $p }
    }
    return $null
}

$node = Resolve-Node
if (-not $node) {
    [Console]::Error.WriteLine('FATAL node not found')
    exit 3
}

$prevEap = $ErrorActionPreference
$ErrorActionPreference = 'Continue'
$out = & $node $doctor --data $Data 2>&1 | Out-String
$code = $LASTEXITCODE
$ErrorActionPreference = $prevEap
if ($null -eq $code) { $code = 0 }

$flat = ($out -replace "`r`n", ' ' -replace "`n", ' ' -replace "`r", ' ').Trim()
# No credential may reach the log.
$flat = [regex]::Replace($flat, '[A-Za-z0-9+/=]{80,}', '[REDACTED_B64]')
$stamp = (Get-Date).ToString('yyyy-MM-dd HH:mm:ss')
$line = '[' + $stamp + '] EXIT=' + $code + ' ' + $flat

if (-not (Test-Path -LiteralPath $LogDir)) { New-Item -ItemType Directory -Path $LogDir -Force | Out-Null }
$logFile = Join-Path $LogDir ('ga-doctor-' + (Get-Date).ToString('yyyy-MM-dd') + '.log')
[System.IO.File]::AppendAllText($logFile, $line + [Environment]::NewLine, (New-Object System.Text.UTF8Encoding($false)))
[Console]::Out.WriteLine($line)

exit $code
