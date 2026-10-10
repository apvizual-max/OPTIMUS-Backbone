# make-ollama-machine-wide.ps1
#
# WHY THIS IS A FILE AND NOT A COMMAND I RAN
# The session that wrote this is not elevated. That is not a preference, it is a
# hard OS boundary, and it was measured rather than assumed:
#     elevated                                      -> False
#     [Environment]::SetEnvironmentVariable(...,'Machine')
#                                                   -> "Requested registry access is not allowed."
#     New-Item -ItemType Directory C:\Program Files -> "Access to the path is denied."
# So the All Users install cannot be performed from where it was requested. This
# script performs it, and it must be run from an elevated PowerShell.
#
# WHAT IT DOES, AND WHAT IT DELIBERATELY DOES NOT
# Ollama is already installed per-user and already serving on 127.0.0.1:11434
# with three models. The gap is SCOPE: the binary and its PATH entry live under
# the user profile, so any other account, service, or scheduled task running as
# SYSTEM or a different user cannot find it. This makes the existing install
# reachable machine-wide.
#
# It does NOT silently relocate the binary. The Ollama Windows installer puts a
# per-machine copy in C:\Program Files\Ollama and registers the tray app and
# service; moving the user copy by hand can orphan the uninstaller entry and the
# log path. So the mode is explicit and yours to choose. Nothing is forced.
#
# RUN:  Open PowerShell as Administrator, then:
#         powershell -ExecutionPolicy Bypass -File make-ollama-machine-wide.ps1 -WhatIf
#       read the plan, then run it again without -WhatIf.

[CmdletBinding(SupportsShouldProcess)]
param(
  # 'path' - add the existing per-user install directory to the MACHINE PATH only.
  # 'copy' - also copy the whole Ollama folder to C:\Program Files\Ollama.
  # 'both'  - both of the above.
  [ValidateSet('path', 'copy', 'both')]
  [string]$Mode = 'path'
)

$ErrorActionPreference = 'Stop'

$id = [Security.Principal.WindowsIdentity]::GetCurrent()
$isAdmin = (New-Object Security.Principal.WindowsPrincipal($id)).IsInRole(
  [Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
  Write-Host 'NOT ELEVATED - nothing has been changed.' -ForegroundColor Red
  Write-Host 'Machine PATH and Program Files both require an elevated session.' -ForegroundColor Red
  Write-Host 'Re-open PowerShell with "Run as administrator" and run this again.' -ForegroundColor Yellow
  exit 1
}

$userDir = Join-Path $env:LOCALAPPDATA 'Programs\Ollama'
$userExe = Join-Path $userDir 'ollama.exe'
if (-not (Test-Path -LiteralPath $userExe)) {
  Write-Host "No per-user Ollama install at $userExe - nothing to promote." -ForegroundColor Red
  exit 1
}
Write-Host "Found per-user install: $userExe" -ForegroundColor Green
Write-Host "Mode: $Mode" -ForegroundColor Cyan

$targetDir = Join-Path $env:ProgramFiles 'Ollama'
$targetExe = Join-Path $targetDir 'ollama.exe'

if ($Mode -in @('copy', 'both')) {
  if (-not (Test-Path -LiteralPath $targetDir)) {
    if ($PSCmdlet.ShouldProcess($targetDir, 'create directory')) {
      New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
    }
  }
  if ($PSCmdlet.ShouldProcess($targetExe, 'copy the Ollama folder to Program Files')) {
    Copy-Item -Path (Join-Path $userDir '*') -Destination $targetDir -Force -Recurse
  }
  Write-Host "Machine copy: $targetExe" -ForegroundColor Green
}

# The PATH entry is what actually decides whether a service or another user can
# find the binary. Appending rather than prepending keeps the existing user
# entry authoritative for this account, so nothing that works today breaks.
$pathToAdd = if ($Mode -in @('copy', 'both') -and (Test-Path -LiteralPath $targetExe)) {
  $targetDir
} else {
  $userDir
}

$machinePath = [Environment]::GetEnvironmentVariable('Path', 'Machine')
$already = @($machinePath -split ';') | Where-Object { $_.TrimEnd('\') -ieq $pathToAdd.TrimEnd('\') }
if ($already.Count -gt 0) {
  Write-Host "Machine PATH already contains $pathToAdd - no change needed." -ForegroundColor Green
} elseif ($PSCmdlet.ShouldProcess('Machine PATH', "append $pathToAdd")) {
  $newPath = $machinePath.TrimEnd(';') + ';' + $pathToAdd
  [Environment]::SetEnvironmentVariable('Path', $newPath, 'Machine')
  Write-Host 'Machine PATH updated. New shells and services will find it; THIS shell will not.' -ForegroundColor Green
}

Write-Host ''
Write-Host 'VERIFY (in a NEW elevated PowerShell):' -ForegroundColor Cyan
Write-Host '  [Environment]::GetEnvironmentVariable("Path","Machine") -split ";" | ? { $_ -like "*Ollama*" }'
Write-Host '  & "$env:ProgramFiles\Ollama\ollama.exe" list'
Write-Host ''
Write-Host 'NOTE: the Ollama tray app and the Ollama_Server scheduled task still run as' -ForegroundColor Yellow
Write-Host 'the current user. This changes reachability, not ownership.' -ForegroundColor Yellow
