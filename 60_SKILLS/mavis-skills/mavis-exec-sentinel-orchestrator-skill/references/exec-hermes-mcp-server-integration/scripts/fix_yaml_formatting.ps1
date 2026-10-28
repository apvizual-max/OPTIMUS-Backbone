# fix_yaml_formatting.ps1
# Fixes common YAML merge artifacts left by PowerShell regex bulk insertions.
# 
# Known artifacts:
#   1. "60moa:" — newline stripped between timeout: 60 and the moa: section
#   2. "60aggregator:" — same issue with aggregator section
#   3. Trailing spaces in YAML values
#
# Usage:
#   .\fix_yaml_formatting.ps1 [-DryRun]

param(
    [switch]$DryRun = $false
)

$HERMES_HOME = "C:\Users\apviz\AppData\Local\hermes"
$PYTHON = "C:\Users\apviz\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe"

$AllConfigs = @(
    "$HERMES_HOME\config.yaml"
) + (Get-ChildItem "$HERMES_HOME\profiles\*\config.yaml" -ErrorAction SilentlyContinue | Select-Object -ExpandProperty FullName) +
    (Get-ChildItem "$HERMES_HOME\state-snapshots\*\config.yaml" -ErrorAction SilentlyContinue | Select-Object -ExpandProperty FullName)

Write-Host "Checking $($AllConfigs.Count) config files for YAML artifacts..."
if ($DryRun) { Write-Host "[DRY RUN] No files will be modified`n" }

$fixed = 0
$clean = 0

foreach ($config in $AllConfigs) {
    if (-not (Test-Path $config)) { continue }

    $content = Get-Content $config -Raw
    $original = $content
    $changed = $false

    # Fix 1: "60moa:" → "60\r\nmoa:"
    if ($content -match '\d+moa:') {
        $content = $content -replace '(\d+)(moa:)', "`$1`r`n`$2"
        $changed = $true
        Write-Host "FIXED (60moa artifact): $config"
    }

    # Fix 2: "60aggregator:" → "60\r\naggregator:"
    if ($content -match '\d+aggregator:') {
        $content = $content -replace '(\d+)(aggregator:)', "`$1`r`n`$2"
        $changed = $true
        Write-Host "FIXED (60aggregator artifact): $config"
    }

    # Fix 3: "60model:" → "60\r\nmodel:"
    if ($content -match '\d+model:') {
        $content = $content -replace '(\d+)(model:)', "`$1`r`n`$2"
        $changed = $true
        Write-Host "FIXED (timeout+key artifact): $config"
    }

    if ($changed) {
        if (-not $DryRun) {
            Set-Content $config $content -Encoding UTF8 -NoNewline
        }
        $fixed++
    } else {
        $clean++
    }
}

Write-Host ""
Write-Host "==========================="
Write-Host "Fixed:  $fixed files"
Write-Host "Clean:  $clean files"

if ($fixed -gt 0 -and -not $DryRun) {
    Write-Host ""
    Write-Host "Validating all configs with Python yaml.safe_load()..."
    $validateScript = @"
import yaml, glob, sys
errors = []
for f in glob.glob(r'$HERMES_HOME\**\config.yaml', recursive=True):
    try:
        yaml.safe_load(open(f, encoding='utf-8'))
    except Exception as e:
        errors.append(f + ': ' + str(e))
if errors:
    [print('ERROR:', e) for e in errors]
    sys.exit(1)
else:
    print('All configs valid - YAML OK')
"@
    & $PYTHON -c $validateScript
}
