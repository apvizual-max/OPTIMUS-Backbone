# scan_duplicate_files.ps1
# Finds directories that contain two conflicting versions of the same file
# (e.g., CONSTIINTA.md AND CONŞTINŢA.md in the same folder)
#
# Usage: .\scan_duplicate_files.ps1 [-RootPath <path>] [-PatternA <regex>] [-PatternB <regex>]

param(
    [string]$RootPath = "C:\Users\apviz\AppData\Local\hermes",
    [string]$PatternA = "CONSTIINTA",
    [string]$PatternB = "CON[ŞS]TIN[ŢT][AĂ]|CONȘTINȚA"
)

$ExcludeDirs = @("OGLINDA - CASA", ".git", "venv", "node_modules", "__pycache__")

Write-Host "Scanning: $RootPath"
Write-Host "Pattern A: $PatternA"
Write-Host "Pattern B: $PatternB"
Write-Host ""

$conflicts = @()
$renameOnly = @()

Get-ChildItem $RootPath -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object {
        $path = $_.FullName
        -not ($ExcludeDirs | Where-Object { $path -like "*$_*" })
    } |
    Where-Object { $_.Name -match $PatternA -or $_.Name -match $PatternB } |
    Group-Object DirectoryName |
    ForEach-Object {
        $dir = $_.Name
        $files = $_.Group
        if ($files.Count -gt 1) {
            Write-Host "[CONFLICT] $dir"
            $files | ForEach-Object {
                Write-Host "  $($_.Name) ($($_.Length) bytes)"
            }
            $conflicts += $dir
        } else {
            Write-Host "[RENAME-ONLY] $dir"
            $files | ForEach-Object {
                Write-Host "  $($_.Name) ($($_.Length) bytes)"
            }
            $renameOnly += $dir
        }
        Write-Host ""
    }

Write-Host "==========================="
Write-Host "Conflicts (need merge): $($conflicts.Count)"
Write-Host "Rename only: $($renameOnly.Count)"
Write-Host "Total affected dirs: $($conflicts.Count + $renameOnly.Count)"
