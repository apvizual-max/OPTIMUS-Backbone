# verify_filenames.ps1
# Post-merge filename verification — confirms zero legacy filenames remain
#
# Usage: .\verify_filenames.ps1 [-RootPath <path>] [-Strict]
# Exit code: 0 = PASSED, 1 = FAILED (legacy filenames found)

param(
    [string]$RootPath = "C:\Users\apviz\AppData\Local\hermes",
    [switch]$Strict = $false
)

$ExcludeDirs = @("OGLINDA - CASA", ".git", "venv", "node_modules", "__pycache__")

# All legacy patterns to check
$LegacyPatterns = @(
    "CONSTIINTA",
    "CONŞTINŢĂ",
    "CONŞTINŢA",
    "CONȘTIINȚĂ",
    "CONȘTINȚA",
    "CON\xc5\x9etiin\xc5\xa3a"  # UTF-8 encoded variant
)

$found = @()

foreach ($pat in $LegacyPatterns) {
    $matches = Get-ChildItem $RootPath -Recurse -File -ErrorAction SilentlyContinue |
        Where-Object {
            $path = $_.FullName
            -not ($ExcludeDirs | Where-Object { $path -like "*$_*" })
        } |
        Where-Object { $_.Name -match $pat }

    foreach ($m in $matches) {
        $found += $m.FullName
        Write-Host "[LEGACY FILENAME] $($m.FullName)"
    }
}

Write-Host ""
Write-Host "================================="
Write-Host "Legacy filenames found: $($found.Count)"

if ($found.Count -eq 0) {
    Write-Host "STAGE 1: PASSED - No legacy filenames" -ForegroundColor Green
    exit 0
} else {
    Write-Host "STAGE 1: FAILED - $($found.Count) legacy filename(s) remain" -ForegroundColor Red
    exit 1
}
