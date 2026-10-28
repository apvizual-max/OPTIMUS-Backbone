# ensure-consent-watcher.ps1 - keep the re-consent listener alive.
#
# WHY IT EXISTS
# -------------
# The Google consent screen is a physical authorization, so it stays with
# Popy. Everything after the click is machine work, and that work needs a
# listener on http://localhost:80 to catch the callback.
#
# MEASURED 2026-10-28: the listener was started by hand and died with the
# session that started it. The grant was still fine, but the RECOVERY PATH was
# gone: a future re-consent would have had no listener to catch the code, and
# the fix would have been "rebuild the setup" instead of "click Allow". The
# system was connected but not permanent - and permanence is the whole point
# of the container being there at all.
#
# So: this script starts the listener if it is not already running, and a
# scheduled task calls it every few minutes. The window is long (12 h) so the
# listener stays up between runs instead of flapping.
#
# ASCII ONLY (Windows PowerShell 5.1).
param(
    [string]$Node     = 'C:\Program Files\nodejs\node.exe',
    [string]$Watcher  = 'C:\Users\apviz\.minimax\google-access\consent-watcher.mjs',
    [string]$Fallback = 'C:\Users\apviz\.minimax-agent\projects\Mavis-Google_Access\container\consent-watcher.mjs',
    [int]$WindowMinutes = 720,
    [int]$Port = 80,
    [string]$LogDir = 'C:\Users\apviz\.minimax\google-access\logs'
)

$ErrorActionPreference = 'Continue'

$LogFile = Join-Path $LogDir 'ensure-consent-watcher.log'
if (-not (Test-Path $LogDir)) { New-Item -ItemType Directory -Path $LogDir -Force | Out-Null }

function Write-Log {
    param([string]$Line)
    $stamp = (Get-Date).ToString('yyyy-MM-dd HH:mm:ss')
    $text = '[' + $stamp + '] ' + $Line
    Add-Content -LiteralPath $LogFile -Value $text -Encoding UTF8
    [Console]::Out.WriteLine($text)
}

# 1. is a listener process already running?
$alive = @(Get-CimInstance Win32_Process -Filter "Name='node.exe'" |
    Where-Object { $_.CommandLine -like '*consent-watcher*' })
if ($alive.Count -gt 0) {
    Write-Log ('LISTENER=already_alive processes=' + $alive.Count)
    exit 0
}

# 2. is the source there?
$script = $Watcher
if (-not (Test-Path -LiteralPath $script)) { $script = $Fallback }
if (-not (Test-Path -LiteralPath $script)) {
    Write-Log ('FATAL=watcher_not_found tried=' + $Watcher + ' and ' + $Fallback)
    exit 2
}
if (-not (Test-Path -LiteralPath $Node)) {
    Write-Log 'FATAL=node_not_found'
    exit 2
}

# 3. start it, detached, with the window it should wait for
$env:CONSENT_PORT = "$Port"
$env:CONSENT_WINDOW_MIN = "$WindowMinutes"
Start-Process -FilePath $Node -ArgumentList $script -WindowStyle Hidden -WorkingDirectory (Split-Path -Parent $script)

# 4. prove the port is actually open - a started process is not a listener
$open = $false
for ($i = 0; $i -lt 30; $i++) {
    Start-Sleep -Milliseconds 500
    $c = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    if ($c) { $open = $true; break }
}
if ($open) {
    Write-Log ('LISTENER=started port=' + $Port + ' window_min=' + $WindowMinutes + ' script=' + $script)
    exit 0
}
Write-Log ('LISTENER=start_failed port=' + $Port + ' script=' + $script)
exit 2
