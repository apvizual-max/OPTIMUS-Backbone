# picker-heartbeat.ps1 - capture whatever the user picked, without a conversation.
#
# The Photo Picker needs a human to choose the photos - that is Google's design
# and it stays that way. But everything after the "Done" click is mechanical,
# and it must not depend on a session being open. So this runs on a schedule:
#
#   1. reads the active session id from data\picker-session.json,
#   2. polls it; if the user finished picking, the picked items are listed and
#      written to data\picked-media.json,
#   3. downloads the media into the project's state\picked folder,
#   4. deletes the session (the API asks clients to do exactly that),
#   5. appends one dated line to the log and exits with the script's code.
#
# Same discipline as extendlm-heartbeat.ps1: stdout direct (Write-Output
# contaminates $LASTEXITCODE in Windows PowerShell 5.1), the native call
# wrapped with the error preference relaxed, and the exit code propagated.
param(
    [string]$DataDir = "C:\Users\apviz\.minimax\google-access\data",
    [string]$Repo    = "C:\Users\apviz\.minimax-agent\projects\Mavis-Google_Access",
    [string]$LogDir  = "C:\Users\apviz\.minimax\google-access\logs"
)

$ErrorActionPreference = 'Stop'

$sessionFile = Join-Path $DataDir 'picker-session.json'
$logFile = Join-Path $LogDir ('picker-heartbeat-' + (Get-Date).ToString('yyyy-MM-dd') + '.log')

function Write-HeartbeatLine([string]$text, [int]$code) {
    $stamp = (Get-Date).ToString('yyyy-MM-dd HH:mm:ss')
    $flat = ($text -replace "`r`n", ' ' -replace "`n", ' ' -replace "`r", ' ').Trim()
    # No credential may reach the log.
    $flat = [regex]::Replace($flat, '[A-Za-z0-9+/=]{80,}', '[REDACTED_B64]')
    $line = '[' + $stamp + '] EXIT=' + $code + ' ' + $flat
    if (-not (Test-Path $LogDir)) { New-Item -ItemType Directory -Path $LogDir -Force | Out-Null }
    [System.IO.File]::AppendAllText($logFile, $line + [Environment]::NewLine, (New-Object System.Text.UTF8Encoding($false)))
    [Console]::Out.WriteLine($line)
}

if (-not (Test-Path $sessionFile)) {
    Write-HeartbeatLine 'NO_SESSION_FILE (no picker session registered)' 0
    exit 0
}

$sessionId = $null
try {
    $sessionId = (Get-Content $sessionFile -Raw | ConvertFrom-Json).session_id
} catch {
    Write-HeartbeatLine ('SESSION_FILE_UNREADABLE ' + $_.Exception.Message) 2
    exit 2
}
if (-not $sessionId) {
    Write-HeartbeatLine 'NO_ACTIVE_SESSION' 0
    exit 0
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
    Write-HeartbeatLine 'FATAL node not found' 3
    exit 3
}

$watcher = Join-Path $Repo 'scripts\picker-watch.mjs'
$downloader = Join-Path $Repo 'scripts\picker-download.mjs'

$prevEap = $ErrorActionPreference
$ErrorActionPreference = 'Continue'
$out = & $node $watcher --session $sessionId --data $DataDir --delete-after 2>&1 | Out-String
$code = $LASTEXITCODE
$ErrorActionPreference = $prevEap
if ($null -eq $code) { $code = 0 }

$flat = ($out -replace "`r`n", ' ' -replace "`n", ' ' -replace "`r", ' ').Trim()
$picked = 0
if ($flat -match 'PICKED=(\d+)') { $picked = [int]$Matches[1] }

if ($picked -gt 0) {
    $ErrorActionPreference = 'Continue'
    $dl = & $node $downloader --picked (Join-Path $DataDir 'picked-media.json') --out (Join-Path $Repo 'state\picked') 2>&1 | Out-String
    $dlCode = $LASTEXITCODE
    $ErrorActionPreference = $prevEap
    if ($null -eq $dlCode) { $dlCode = 0 }
    $flat = $flat + ' || ' + (($dl -replace "`r`n", ' ' -replace "`n", ' ' -replace "`r", ' ').Trim())
    if ($dlCode -ne 0) { $code = $dlCode }
}

Write-HeartbeatLine $flat $code
exit $code
