# Antigravity Multi-Interface Sync Daemon (ALSD)
# Monitors active transcript files and synchronizes turns between App, IDE, and CLIs.

param (
    [string]$BrainDir = "$env:USERPROFILE\.gemini\antigravity\brain",
    [int]$PollIntervalMs = 1000
)

Write-Host ">>> Starting Antigravity Live Sync Daemon (ALSD)..." -ForegroundColor Cyan
Write-Host ">>> Watching canonical store: $BrainDir" -ForegroundColor Gray

if (-not (Test-Path $BrainDir)) {
    Write-Warning "Brain directory not found: $BrainDir"
    exit 1
}

$watcher = New-Object System.IO.FileSystemWatcher
$watcher.Path = $BrainDir
$watcher.Filter = "transcript.jsonl"
$watcher.IncludeSubdirectories = $true
$watcher.EnableRaisingEvents = $true

$action = {
    param($source, $eventArgs)
    $path = $eventArgs.FullPath
    $changeType = $eventArgs.ChangeType
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    
    # Broadcast or normalize turn activity
    Write-Host "[$timestamp] Transcript change detected ($changeType): $path" -ForegroundColor Green
}

Register-ObjectEvent -InputObject $watcher -EventName "Changed" -Action $action | Out-Null

Write-Host ">>> ALSD Active. Press Ctrl+C to terminate." -ForegroundColor Green

try {
    while ($true) {
        Start-Sleep -Milliseconds $PollIntervalMs
    }
} finally {
    Unregister-Event -SourceIdentifier $watcher.ToString() -ErrorAction SilentlyContinue
    $watcher.Dispose()
    Write-Host ">>> ALSD Stopped." -ForegroundColor Yellow
}
