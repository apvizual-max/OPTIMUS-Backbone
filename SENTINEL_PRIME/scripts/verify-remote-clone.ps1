<#
.SYNOPSIS
    Proves that the remote main of a repository is actually usable: the tree carries
    no invalid path component, the remote is reachable, and a fresh clone succeeds
    on the expected commit with a clean working tree.

.DESCRIPTION
    A commit can be perfectly valid and still impossible to check out on Windows.
    The check that matters is not `git log`; it is a fresh clone. This script is the
    executable form of that rule, so it can be run after every push made by the
    continuous development pipeline (Jules + Antigravity CD Engine), which writes
    directly to `main`.

    The script never deletes anything and never touches the working tree of the
    repository it inspects. It updates no ref and writes no file inside the
    repository: the only thing it writes is a disposable probe clone, whose path is
    printed at the end.

    Every check reports the measured value next to its name, so a FAIL always says
    which measurement failed and what the value was.

.PARAMETER Repo
    Repository to inspect. Defaults to the parent directory of this script.

.PARAMETER Remote
    Name of the remote to resolve. Defaults to 'origin'.

.PARAMETER RemoteUrl
    Explicit URL used for both the remote query and the probe clone. Use it to check
    a local path instead of the network, or to point the probe at a specific URL.

.PARAMETER CloneRoot
    Directory the probe clone is created in. Defaults to $env:TEMP. A unique,
    timestamped sub-directory is used; the probe clone is KEPT and its path printed.

.PARAMETER ExpectFiles
    Repository-relative paths that must exist in the probe clone, comma separated.
    (A comma separated string, not an array: with `powershell -File` a list of
    separate arguments does not bind to a [string[]] parameter.)

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File scripts\verify-remote-clone.ps1

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File scripts\verify-remote-clone.ps1 `
        -ExpectFiles '14_HANDOFF\10_PRIMING_PROMPT.md','README.md'
#>
[CmdletBinding()]
param(
    [string]$Repo = (Split-Path -Parent $PSScriptRoot),
    [string]$Remote = 'origin',
    [string]$RemoteUrl = '',
    [string]$CloneRoot = '',
    [string]$ExpectFiles = ''
)

$ErrorActionPreference = 'Stop'
$checks = New-Object System.Collections.ArrayList
$failures = New-Object System.Collections.ArrayList

function Add-Check {
    param([string]$Name, [string]$Value, [bool]$Ok, [string]$Detail = '')
    $status = 'PASS'
    if (-not $Ok) {
        $status = 'FAIL'
        [void]$failures.Add($Name)
    }
    $line = "CHECK $Name $Value $status"
    if ($Detail) { $line += " | $Detail" }
    Write-Output $line
    [void]$checks.Add([pscustomobject]@{
        name = $Name; value = $Value; ok = $Ok; status = $status; detail = $Detail
    })
}

# Runs a native command and captures stdout+stderr as text, WITHOUT ever letting a
# native error record terminate the script. A native tool writing to stderr is not
# an exception; treating it as one is what breaks verification scripts.
#
# NOTE: the helper is deliberately NOT named `Git`. PowerShell resolves a function
# name before the executable on PATH, so a function called `Git` shadows the `git`
# binary and calls itself forever (measured: CallDepthOverflow).
function Invoke-Native {
    param([string]$Exe, [string[]]$NativeArgs)
    $prev = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    $out = $null
    $code = 0
    try {
        $out = & $Exe @NativeArgs 2>&1
        $code = $LASTEXITCODE
    } catch {
        $out = $_.Exception.Message
        $code = 1
    } finally {
        $ErrorActionPreference = $prev
    }
    $text = (@($out) | ForEach-Object {
        if ($_ -is [System.Management.Automation.ErrorRecord]) { $_.ToString() } else { [string]$_ }
    }) -join "`n"
    return @{ code = $code; out = $text }
}

function Get-FirstSha {
    param([string]$Text)
    # anchored at the start of the line, and NOT requiring trailing whitespace:
    # `git rev-parse HEAD` prints the bare SHA with nothing after it.
    foreach ($line in (@($Text) -split "`r?`n")) {
        if ($line -match '^\s*([0-9a-f]{40})\b') { return $Matches[1] }
    }
    return ''
}

# --- 0. the repository under inspection ------------------------------------
$Repo = (Resolve-Path -LiteralPath $Repo).Path
Add-Check 'repo_exists' $Repo (Test-Path -LiteralPath (Join-Path $Repo '.git')) `
    "inspected repository: $Repo"

if (-not $RemoteUrl) {
    $remoteQuery = Invoke-Native 'git' @('-C', $Repo, 'remote', 'get-url', $Remote)
    $RemoteUrl = $remoteQuery.out.Trim()
    if ($remoteQuery.code -ne 0 -or -not $RemoteUrl) {
        Add-Check 'remote_url' 'UNRESOLVED' $false `
            "remote '$Remote' could not be resolved in $Repo"
        Write-Output 'VERDICT=FAIL'
        Write-Output ("FAILURES=" + ($failures -join ','))
        exit 2
    }
}
Add-Check 'remote_url' $RemoteUrl $true "remote '$Remote'"

# --- 1. what the remote actually has ----------------------------------------
$remoteLs = Invoke-Native 'git' @('ls-remote', $RemoteUrl, 'refs/heads/main')
$remoteSha = Get-FirstSha $remoteLs.out
Add-Check 'remote_main_sha' $(if ($remoteSha) { $remoteSha } else { 'UNRESOLVED' }) `
    ($remoteSha -ne '') "git ls-remote $RemoteUrl refs/heads/main"

$heads = Invoke-Native 'git' @('ls-remote', '--heads', $RemoteUrl)
$headNames = @()
foreach ($line in (@($heads.out) -split "`r?`n")) {
    if ($line -match '\s+(refs/heads/\S+)\s*$') { $headNames += $Matches[1] }
}
Add-Check 'remote_branches' $headNames.Count `
    ($headNames.Count -eq 1 -and $headNames[0] -eq 'refs/heads/main') ($headNames -join ',')

# --- 2. local state ---------------------------------------------------------
$localHeadRes = Invoke-Native 'git' @('-C', $Repo, 'rev-parse', 'HEAD')
$localHead = Get-FirstSha $localHeadRes.out
Add-Check 'local_head' $(if ($localHead) { $localHead } else { 'UNRESOLVED' }) `
    ($localHead -ne '') "HEAD of $Repo"

$ahead = 'n/a'
$behind = 'n/a'
if ($remoteSha) {
    # make the remote commit object available locally, WITHOUT moving any ref
    $has = Invoke-Native 'git' @('-C', $Repo, 'cat-file', '-e', "$remoteSha^{commit}")
    if ($has.code -ne 0) {
        Invoke-Native 'git' @('-C', $Repo, 'fetch', '--no-tags', '--no-write-fetch-head',
                               $RemoteUrl, 'refs/heads/main') | Out-Null
    }
    $counts = Invoke-Native 'git' @('-C', $Repo, 'rev-list', '--left-right', '--count',
                                    "$remoteSha...HEAD")
    if ($counts.code -eq 0) {
        $parts = ($counts.out.Trim() -split '\s+')
        if ($parts.Count -ge 2) {
            $behind = $parts[0]
            $ahead = $parts[1]
        }
    }
}
Add-Check 'behind_ahead' "$behind/$ahead" $true `
    'remote main relative to local HEAD (behind/ahead)'

# --- 3. is the remote tree checkoutable at all? -----------------------------
$invalid = @()
if ($remoteSha) {
    $treePaths = Invoke-Native 'git' @('-C', $Repo, 'ls-tree', '-r', '--name-only', $remoteSha)
    if ($treePaths.code -eq 0) {
        $invalid = @((@($treePaths.out) -split "`r?`n") |
            Where-Object { $_ -and $_.Contains(':') })
    }
}
Add-Check 'invalid_tree_entries' $invalid.Count ($invalid.Count -eq 0) `
    $(if ($invalid.Count) { ($invalid | Select-Object -First 3) -join ' | ' }
      else { 'no path component contains a colon' })

# --- 4. the decisive test: a fresh clone ------------------------------------
if (-not $CloneRoot) { $CloneRoot = $env:TEMP }
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$probe = Join-Path $CloneRoot "clone-probe-$stamp-$PID"
$cloneRes = Invoke-Native 'git' @('clone', '--quiet', '--no-tags', $RemoteUrl, $probe)
$cloneCode = $cloneRes.code
Add-Check 'clone_exit' $cloneCode ($cloneCode -eq 0) `
    $(if ($cloneCode -ne 0) { ((@($cloneRes.out) -split "`r?`n" | Where-Object { $_ }) |
          Select-Object -First 2) -join ' | ' } else { "probe clone: $probe" })

$cloneHead = ''
$cloneDirty = -1
$cloneBranches = @()
$cloneFiles = 0
if ($cloneCode -eq 0) {
    $cloneHead = Get-FirstSha (Invoke-Native 'git' @('-C', $probe, 'rev-parse', 'HEAD')).out
    $dirty = Invoke-Native 'git' @('-C', $probe, 'status', '--porcelain')
    $cloneDirty = @((@($dirty.out) -split "`r?`n") | Where-Object { $_ }).Count
    $br = Invoke-Native 'git' @('-C', $probe, 'branch', '--format=%(refname:short)')
    $cloneBranches = @((@($br.out) -split "`r?`n") | Where-Object { $_ })
    $lf = Invoke-Native 'git' @('-C', $probe, 'ls-files')
    $cloneFiles = @((@($lf.out) -split "`r?`n") | Where-Object { $_ }).Count
}
Add-Check 'clone_head_sha' $(if ($cloneHead) { $cloneHead } else { 'NONE' }) `
    ($cloneHead -ne '' -and $cloneHead -eq $remoteSha) 'probe HEAD must equal remote main'
Add-Check 'clone_dirty' $cloneDirty ($cloneDirty -eq 0) 'lines reported by git status --porcelain'
Add-Check 'clone_branches' ($cloneBranches -join ',') `
    ($cloneBranches.Count -eq 1 -and $cloneBranches[0] -eq 'main') 'local branches in the probe clone'
Add-Check 'clone_tracked_files' $cloneFiles ($cloneFiles -gt 0) 'files tracked in the probe clone'

# --- 5. the files that must be there ----------------------------------------
$expect = @(@($ExpectFiles -split ',') | ForEach-Object { $_.Trim() } | Where-Object { $_ })
$missing = @()
foreach ($rel in $expect) {
    $target = Join-Path $probe $rel
    if (-not (Test-Path -LiteralPath $target)) { $missing = @($missing + $rel) }
}
Add-Check 'expect_files_missing' $missing.Count ($missing.Count -eq 0) `
    $(if ($missing.Count) { $missing -join ' | ' } else { "$($expect.Count) required paths present" })

# --- verdict -----------------------------------------------------------------
Write-Output "PROBE_CLONE=$probe"
if ($failures.Count -eq 0) {
    Write-Output 'VERDICT=PASS'
    Write-Output 'FAILURES='
    exit 0
}
Write-Output 'VERDICT=FAIL'
Write-Output ("FAILURES=" + ($failures -join ','))
exit 2
