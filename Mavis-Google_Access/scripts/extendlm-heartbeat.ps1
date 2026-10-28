# extendlm-heartbeat.ps1 - keep the ExtendLM snapshot alive for the Cloud.
#
# What it does, once per run:
#   1. rotates the ExtendLM token if the current one is close to expiry
#      (the endpoint rotates the refresh token, so the owner - this host -
#      is the only one that may rotate),
#   2. publishes the snapshot to the Cloud repository secret,
#   3. appends one dated line to a log and exits with the publisher's code.
#
# MEASURED 2026-10-27: Write-Output contaminates $LASTEXITCODE in Windows
# PowerShell 5.1 when the output is captured, so a gate that ends with
# Write-Output cannot fail. The line therefore goes straight to the console
# handle and the file, and the exit code is the publisher's own.
param(
    [string]$DataDir  = "C:\Users\apviz\.minimax\google-access\data",
    [string]$Repo     = "apvizual-max/MAVIS-CLOUD",
    [int]$MinValidMinutes = 60,
    [string]$LogDir   = "C:\Users\apviz\.minimax\google-access\logs"
)

$ErrorActionPreference = 'Stop'

$publisher = Join-Path $PSScriptRoot 'publish-extendlm-secret.mjs'
if (-not (Test-Path $publisher)) {
    [Console]::Error.WriteLine("FATAL publisher not found: " + $publisher)
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
    [Console]::Error.WriteLine("FATAL node not found")
    exit 3
}

if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

$stamp   = (Get-Date).ToString('yyyy-MM-dd HH:mm:ss')
$logFile = Join-Path $LogDir ('extendlm-heartbeat-' + (Get-Date).ToString('yyyy-MM-dd') + '.log')

# MEASURED 2026-10-27: with $ErrorActionPreference='Stop', a native command
# that writes to stderr (gh failing on a bad repository) becomes a TERMINATING
# error, so the wrapper died BEFORE it wrote its log line: the heartbeat failed
# and left no trace. A failure nobody can read is a failure nobody repairs.
# Around the call the preference is therefore relaxed and the child's exit
# code is read directly.
$prevEap = $ErrorActionPreference
$ErrorActionPreference = 'Continue'
$out = & $node $publisher --data $DataDir --repo $Repo --min-valid-minutes $MinValidMinutes 2>&1 | Out-String
$code = $LASTEXITCODE
$ErrorActionPreference = $prevEap
if ($null -eq $code) { $code = 0 }

$flat = ($out -replace "`r`n", ' ' -replace "`n", ' ' -replace "`r", ' ').Trim()
# Safety net: nothing that looks like a base64 payload may reach the log.
# The publisher already redacts its own errors; this catches anything a tool
# prints that was not under its control.
$flat = [regex]::Replace($flat, '[A-Za-z0-9+/=]{80,}', '[REDACTED_B64]')
$line = '[' + $stamp + '] EXIT=' + $code + ' ' + $flat

# UTF-8 without BOM, so the log stays readable by every tool.
[System.IO.File]::AppendAllText($logFile, $line + [Environment]::NewLine, (New-Object System.Text.UTF8Encoding($false)))
[Console]::Out.WriteLine($line)

exit $code
