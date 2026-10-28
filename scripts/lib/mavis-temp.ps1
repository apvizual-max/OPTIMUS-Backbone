# ---------------------------------------------------------------- mavis-temp.ps1
# A temporary file whose name cannot collide.
#
# WHY THIS FILE EXISTS.
#
# [IO.Path]::GetTempFileName() generates a name from a small alphabet and asks
# the OS for a free one. It FAILS with "The file exists" once the shared system
# temp folder is crowded. Measured 2026-10-28 on this machine:
#
#   %TEMP% held 111,417 files (65,662 .tmp + 36,254 .wav + 6,201 extensionless)
#   GetTempFileName against the original temp folder : 0 of 12 attempts worked
#   GetTempFileName against a clean temp folder        : 12 of 12 attempts worked
#
# The Control Center's state collector calls it, so the dashboard answered
# HTTP 500 for a reason that had nothing to do with the dashboard. The leak
# that filled the folder stopped around 2026-10-10, but the residue stayed.
#
# A control that depends on a resource any other process on the machine can
# exhaust is not a control. So the directory is still the system temp folder
# (always available, no permissions to fight over) but the NAME is generated
# here, from a GUID, which cannot collide with anything.
#
# USAGE:
#   . (Join-Path (Split-Path $PSScriptRoot -Parent) 'scripts\lib\mavis-temp.ps1')
#   $tmp = New-MavisTempFile '.js'
#
# The file is CREATED, because several callers pass it straight to
# Start-Process -RedirectStandardOutput, which refuses a path that does not
# exist. Callers that own their file should delete it when done.
#
# ASCII-ONLY ON PURPOSE. PowerShell 5.1 reads a BOM-less .ps1 as ANSI, so a
# non-ASCII literal here is a parse hazard, not a cosmetic one.

function New-MavisTempFile {
  param(
    [string] $Extension = '.tmp',
    [string] $Directory
  )
  if (-not $Directory) {
    $Directory = Join-Path ([IO.Path]::GetTempPath()) 'optimus-sot-temp'
  }
  if (-not (Test-Path -LiteralPath $Directory)) {
    New-Item -ItemType Directory -Path $Directory -Force -ErrorAction SilentlyContinue | Out-Null
  }
  $path = Join-Path $Directory ([Guid]::NewGuid().ToString('N') + $Extension)
  [IO.File]::WriteAllText($path, '')
  return $path
}
