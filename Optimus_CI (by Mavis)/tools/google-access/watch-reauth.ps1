# watch-reauth.ps1 - the watcher that says WHEN a re-consent is needed.
#
# WHY IT EXISTS
# -------------
# Popy: "trebuie sa ne anunte cand are nevoie de reautentificare DESI NU VAD
# DE CE TREBUIE SA NE RECONECTAM ASA MEREU". The re-consent itself is a single
# click ONCE - the grant is a refresh token, it lasts until Popy revokes it.
# What must never happen again is a silent failure that looks like "sign in
# again" with no explanation.
#
# So this watcher measures the container and reports:
#   - the container is not running      -> it starts it (restart: unless-stopped
#                                        already covers a daemon restart)
#   - the grant is not live              -> ntfy notification + a notice file
#   - everything is fine                 -> nothing, and the notice is cleared
#
# It never asks for a token, never opens a browser, and never prints one.
#
# ASCII ONLY (Windows PowerShell 5.1).

param(
    [string]$Url = 'http://127.0.0.1:8766/health',
    [string]$Container = 'Google_Access',
    [string]$Root = 'C:\Users\apviz\.minimax\google-access',
    [string]$Ntfy = 'http://127.0.0.1:8090'
)

$ErrorActionPreference = 'Continue'

$LogDir = Join-Path $Root 'logs'
$LogFile = Join-Path $LogDir 'watch-reauth.log'
$Notice = Join-Path $Root 'REAUTH-NOTICE.md'
$DataDir = Join-Path $Root 'data'
$TopicFile = Join-Path $DataDir 'ntfy-topic.txt'

New-Item -ItemType Directory -Path $LogDir -Force | Out-Null

$topic = 'mavis-google-access'
if (Test-Path -LiteralPath $TopicFile) {
    $t = (Get-Content -LiteralPath $TopicFile -Raw -ErrorAction SilentlyContinue)
    if ($t) { $topic = $t.Trim() }
}

function Write-Log {
    param([string]$Line)
    $stamp = (Get-Date).ToString('yyyy-MM-dd HH:mm:ss')
    $text = '[' + $stamp + '] ' + $Line
    Add-Content -LiteralPath $LogFile -Value $text -Encoding UTF8
    [Console]::Out.WriteLine($text)
}

function Send-Ntfy {
    param([string]$Title, [string]$Message)
    try {
        $payload = @{ topic = $topic; title = $Title; message = $Message; tags = @('warning') }
        $json = $payload | ConvertTo-Json -Depth 4
        Invoke-WebRequest -Uri ($Ntfy + '/') -Method Post -Body $json -ContentType 'application/json' -TimeoutSec 10 -UseBasicParsing | Out-Null
        Write-Log ('NOTIFY=ntfy topic=' + $topic + ' title=' + $Title)
        return $true
    } catch {
        Write-Log ('NOTIFY_FAILED=' + $_.Exception.Message)
        return $false
    }
}

# 1. is the container up?
$running = @(docker ps --filter "name=^/$Container$" --format '{{.Names}}')
if ($running.Count -eq 0) {
    Write-Log ('CONTAINER=down name=' + $Container + ' -> starting it')
    docker start $Container 2>&1 | Out-Null
    Start-Sleep -Seconds 4
}

# 2. what does the container say about the credential?
$health = $null
try {
    $health = Invoke-RestMethod -Uri $Url -TimeoutSec 10
} catch {
    Write-Log ('HEALTH=unreachable ' + $_.Exception.Message)
}

if ($null -eq $health) {
    $msg = "Google_Access does not answer on $Url. The container may be down or the port moved."
    if (-not (Test-Path -LiteralPath $Notice)) {
        Set-Content -LiteralPath $Notice -Value ("# Google_Access needs attention`r`n`r`n" + $msg + "`r`n`r`n- Machine: " + $env:COMPUTERNAME + "`r`n- Checked: " + (Get-Date).ToString('yyyy-MM-dd HH:mm:ss') + "`r`n") -Encoding UTF8
        Send-Ntfy -Title 'Google_Access: nu raspunde' -Message $msg
    } else {
        Write-Log 'NOTICE=already present, not repeating the notification'
    }
    Write-Log 'VERDICT=unknown (not live, not proven dead)'
    exit 2
}

$grant = $health.grant
$reauth = [bool]$health.reauth_required

if ($grant -eq 'live' -and -not $reauth) {
    if (Test-Path -LiteralPath $Notice) {
        Remove-Item -LiteralPath $Notice -Force
        Write-Log 'NOTICE=cleared - the credential is live again'
    }
    Write-Log ('VERDICT=ok grant=' + $grant + ' tools=' + $health.tools)
    exit 0
}

$reason = 'the grant is not live'
$flag = Join-Path $DataDir 'REAUTH_REQUIRED'
if (Test-Path -LiteralPath $flag) {
    $raw = Get-Content -LiteralPath $flag -Raw -ErrorAction SilentlyContinue
    if ($raw) { $reason = $raw.Trim() }
}

$msg = "Google_Access needs a re-consent. Reason: " + $reason + " . One click fixes it: call google_scope_upgrade, open the consent_url, then on the host: node provision-grant.cjs --from-code <code> --client secrets"

if (-not (Test-Path -LiteralPath $Notice)) {
    Set-Content -LiteralPath $Notice -Value ("# Google_Access needs a re-consent`r`n`r`n" + $msg + "`r`n`r`n- Machine: " + $env:COMPUTERNAME + "`r`n- Checked: " + (Get-Date).ToString('yyyy-MM-dd HH:mm:ss') + "`r`n") -Encoding UTF8
    Send-Ntfy -Title 'Google_Access: re-autentificare necesara' -Message $msg
} else {
    Write-Log 'NOTICE=already present, not repeating the notification'
}

Write-Log ('VERDICT=reauth_required grant=' + $grant + ' reason=' + $reason)
exit 3
