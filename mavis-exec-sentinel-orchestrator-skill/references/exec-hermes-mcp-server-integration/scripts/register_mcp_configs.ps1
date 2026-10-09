# register_mcp_configs.ps1
# Registers a new MCP server entry in all Hermes profile configs
#
# Usage:
#   .\register_mcp_configs.ps1 -ServerName "my-server" -PackageName "my_server" `
#       -ServerPath "C:\...\mcp-servers\custom\my-server"

param(
    [Parameter(Mandatory=$true)]
    [string]$ServerName,

    [Parameter(Mandatory=$true)]
    [string]$PackageName,

    [Parameter(Mandatory=$true)]
    [string]$ServerPath,

    [int]$Timeout = 60,
    [switch]$DryRun = $false
)

$HERMES_HOME = "C:\Users\apviz\AppData\Local\hermes"

$AllConfigs = @(
    "$HERMES_HOME\config.yaml",
    "$HERMES_HOME\profiles\default\config.yaml",
    "$HERMES_HOME\profiles\prime\config.yaml",
    "$HERMES_HOME\profiles\assist\config.yaml",
    "$HERMES_HOME\profiles\cli-prime\config.yaml",
    "$HERMES_HOME\profiles\coder\config.yaml",
    "$HERMES_HOME\profiles\cowork\config.yaml",
    "$HERMES_HOME\profiles\designer\config.yaml",
    "$HERMES_HOME\profiles\trader\config.yaml",
    "$HERMES_HOME\profiles\translator\config.yaml",
    "$HERMES_HOME\state-snapshots\20260711-095000-optimal-config\config.yaml"
)

$NewBlock = @"
  ${ServerName}:
    args:
    - -m
    - ${PackageName}.server
    command: python
    cwd: ${ServerPath}
    timeout: ${Timeout}
"@

Write-Host "Registering MCP server: $ServerName"
if ($DryRun) { Write-Host "[DRY RUN] No files will be modified`n" }

$updated = 0
$skipped = 0
$notFound = 0

foreach ($config in $AllConfigs) {
    if (-not (Test-Path $config)) {
        Write-Host "NOT FOUND: $config"
        $notFound++
        continue
    }

    $content = Get-Content $config -Raw

    if ($content -match [regex]::Escape($ServerName + ":")) {
        Write-Host "SKIP (already registered): $config"
        $skipped++
        continue
    }

    # Find insertion point: after windows-system block
    $pattern = "(  windows-system:[\s\S]*?timeout: 60)(\r?\n)(moa:|[a-z])"
    if ($content -match $pattern) {
        if (-not $DryRun) {
            $newContent = $content -replace $pattern, "`$1`$2$NewBlock`$3"
            # Fix potential merge artifact
            $newContent = $newContent -replace "${Timeout}moa:", "${Timeout}`r`nmoa:"
            Set-Content $config $newContent -Encoding UTF8 -NoNewline
        }
        Write-Host "UPDATED: $config"
        $updated++
    } else {
        Write-Host "PATTERN NOT MATCHED: $config"
    }
}

Write-Host ""
Write-Host "==========================="
Write-Host "Updated:   $updated"
Write-Host "Skipped:   $skipped"
Write-Host "Not found: $notFound"

if (-not $DryRun -and $updated -gt 0) {
    Write-Host ""
    Write-Host "IMPORTANT: Verify YAML is valid with:"
    Write-Host "  python verify_yaml_configs.py"
    Write-Host ""
    Write-Host "Then restart Hermes for changes to take effect."
}
