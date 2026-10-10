<#
.SYNOPSIS
  Guardian for C:\Users\apviz\docker-compose.yml.

.DESCRIPTION
  That file was found deleted on 2026-10-02, leaving 18 running containers as
  orphans with no definition on disk. This script makes that state impossible
  to miss and cheap to repair.

  It NEVER stops, recreates or removes a container. It only reads state,
  validates the file, keeps backups, and rebuilds the file if it vanished.

  Exit codes
    0  compose present and valid
    1  compose missing
    2  compose present but INVALID
#>
[CmdletBinding()]
param([switch]$Quiet)

$ErrorActionPreference = 'Stop'
$COMPOSE = 'C:\Users\apviz\docker-compose.yml'
$BACKUPS = 'C:\Users\apviz\.minimax-agent\projects\90_CONTROL_CENTER\backups'

function Say($m, $c = 'Gray') { if (-not $Quiet) { Write-Host $m -ForegroundColor $c } }

# ---------------------------------------------------------------- validate --
$exists = Test-Path -LiteralPath $COMPOSE
if ($exists) {
  $tmp = [IO.Path]::GetTempFileName()
  docker compose -f $COMPOSE config --quiet 2>$tmp | Out-Null
  $valid = ($LASTEXITCODE -eq 0)
  $err = if (Test-Path $tmp) { (Get-Content $tmp -Raw) } else { '' }
  if (Test-Path $tmp) { & rm -- $tmp 2>$null }

  if ($valid) {
    # keep a dated copy of every good state
    New-Item -ItemType Directory -Force -Path $BACKUPS | Out-Null
    $stamp = (Get-Date -Format 'yyyyMMdd-HHmmss')
    Copy-Item -LiteralPath $COMPOSE -Destination (Join-Path $BACKUPS "docker-compose.$stamp.yml") -Force
    Say "[ok]   compose present and valid" 'Green'
    Say "       backup -> $BACKUPS\docker-compose.$stamp.yml" 'DarkGray'
    exit 0
  }
  Say "[FAIL] compose present but INVALID" 'Red'
  Say "       $err" 'DarkYellow'
  exit 2
}

# ------------------------------------------------------------------ missing --
Say "[FAIL] $COMPOSE IS MISSING" 'Red'
$containers = @(docker ps --format '{{.Names}}' 2>$null)
$orphans = @()
if ($containers.Count -gt 0) {
  try {
    $ids = @(docker ps -q 2>$null)
    $all = docker inspect $ids 2>$null | ConvertFrom-Json
    $orphans = @($all | Where-Object {
      $_.Config.Labels.'com.docker.compose.project' -and
      $_.Config.Labels.'com.docker.compose.project.config_files' -like '*docker-compose.yml'
    } | ForEach-Object { $_.Name.TrimStart('/') })
  } catch { }
}
Say "       $($orphans.Count) running containers have NO definition on disk:" 'Yellow'
$orphans | Select-Object -First 25 | ForEach-Object { Say "         $_" 'Yellow' }

# ------------------------------------------------------------------ rebuild --
Say "" 'Gray'
Say "Rebuilding the compose file from live container state..." 'Cyan'
New-Item -ItemType Directory -Force -Path $BACKUPS | Out-Null
try {
  $rebuilt = & powershell -NoProfile -ExecutionPolicy Bypass `
    -File 'C:\Users\apviz\.minimax-agent\projects\scripts\rebuild-compose-from-state.ps1' 2>&1
  $rebuilt | ForEach-Object { Say "  $_" 'DarkGray' }
  if (Test-Path -LiteralPath $COMPOSE) {
    Say "[ok]   compose restored: $COMPOSE" 'Green'
    Say "       IMPORTANT: review it before running 'docker compose up -d'." 'DarkYellow'
    exit 0
  }
} catch {
  Say "       rebuild failed: $($_.Exception.Message)" 'Red'
}
exit 1
