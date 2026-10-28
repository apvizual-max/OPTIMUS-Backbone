# request-push.ps1 - armeaza acordul R0 al lui Popy pentru impingere.
#
# ATENTIE: asta NU impinge. doar armeaza. Un acord = o impingere: markerul
# PUSH-ACORD e consumat de poarta comuna la primul push reusit.
#
# Se apeleaza DOAR la cererea explicita a lui Popy. Nu se apeleaza singur.
#
# Daca vrei ca serverul sa impinga, apeleaza pluginul (ci_arm_push), sau
# foloseste poarta sanitizata de pe host: scripts\git-autopush.ps1 -Acord
#
# ASCII ONLY: executat de Windows PowerShell 5.1.

[CmdletBinding()]
param(
    [switch]$Acord,
    [string[]]$Repo = @('ci', 'cloud', 'ciclone')
)

$ErrorActionPreference = 'Stop'

$GitData = 'E:\Google\GitData-Optimus-CI'
$Map = @{
    'ci'      = 'repo'
    'cloud'   = 'clone-MAVIS-CLOUD'
    'ciclone' = 'clone-MAVIS-OPTIMUS-CI'
}

if (-not $Acord) {
    Write-Host ''
    Write-Host '  POARTA: fara -Acord nu se armeaza nimic.'
    Write-Host '  Calea corecta:  ci-server\request-push.ps1 -Acord'
    Write-Host ''
    exit 3
}

$stamp = (Get-Date).ToString('o')
foreach ($r in $Repo) {
    if (-not $Map.ContainsKey($r)) {
        Write-Host ('ERROR: repo necunoscut: ' + $r + ' (ci|cloud|ciclone)')
        exit 2
    }
    $gitdir = Join-Path $GitData $Map[$r]
    if (-not (Test-Path -LiteralPath $gitdir)) {
        Write-Host ('ERROR: gitdir inexistent: ' + $gitdir)
        exit 2
    }
    $marker = Join-Path $gitdir 'PUSH-ACORD'
    Set-Content -LiteralPath $marker -Value ($stamp + ' Popy') -Encoding ASCII -NoNewline
    Write-Host ('ARMAT: ' + $r + '  ->  ' + $marker)
}

Write-Host ''
Write-Host 'Acord armat. Un singur push per repo. Impinge apoi cu:'
Write-Host '  docker exec Mavis-Optimus-CI node /opt/optimus-ci/engine/cli.mjs push'
exit 0
