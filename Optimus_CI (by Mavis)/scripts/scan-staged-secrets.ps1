# scan-staged-secrets.ps1
# Scans a git repo's INDEX (the staged content) for secrets that must never
# enter a public repo.
#
# Why this exists in CI: the scanner that used to live here (jules-scan-staged)
# moved to the CD folder with the Jules platform. CI's own Git/GitHub procedure
# kept pointing at it, which is a broken reference and a missing gate. This is
# CI's own instrument, with no dependency on another project.
#
# Modes:
#   default          : scan the staged index of the repo at -RepoPath
#   -ProbeFile <f>   : scan one file's content. Used by the selfcheck to prove
#                      the detector CAN FAIL. A gate that cannot fail is not a
#                      gate.
#   -StagedDiff      : scan ONLY the lines the staged change adds. The
#                      question is "does this change introduce a secret", not
#                      "does this repository contain the string AKIA".
#   -GitDir <dir>    : use this gitdir explicitly instead of the one the
#                      worktree points to. The container Mavis-Optimus-CI needs
#                      it: there the .git pointer holds a Windows path (E:/...)
#                      that linux git cannot resolve.
#
# Exit codes (the script's OWN, never inherited):
#   0 = clean (no blocking secret)
#   1 = BLOCKED - at least one secret shape found
#   2 = error (git missing, repo missing, probe file missing)
#
# ASCII ONLY: executed by Windows PowerShell 5.1.

param(
    [string]$RepoPath = '',
    [string]$ProbeFile = '',
    [string]$GitDir = '',
    [switch]$StagedDiff
)

$ErrorActionPreference = 'Stop'

function Write-Out {
    param([Parameter(Mandatory = $true)][string]$Message)
    [Console]::Out.WriteLine($Message)
}

function Write-Err {
    param([Parameter(Mandatory = $true)][string]$Message)
    [Console]::Error.WriteLine($Message)
}

# --- pattern table --------------------------------------------------------
# Fixed shapes: a match is a secret, no interpretation needed.
$FixedPatterns = @(
    @{ Name = 'private-key-block'; Regex = '-----BEGIN [A-Z ]*PRIVATE KEY-----' },
    @{ Name = 'aws-access-key-id'; Regex = '(^|[^A-Za-z0-9])AKIA[0-9A-Z]{16}([^A-Za-z0-9]|$)' },
    @{ Name = 'github-token'; Regex = '(^|[^A-Za-z0-9])gh[pousr]_[A-Za-z0-9]{36,}' },
    @{ Name = 'github-pat'; Regex = '(^|[^A-Za-z0-9])github_pat_[A-Za-z0-9_]{40,}' },
    @{ Name = 'google-api-key'; Regex = '(^|[^A-Za-z0-9])AIza[0-9A-Za-z_-]{35}' },
    @{ Name = 'openai-style-key'; Regex = '(^|[^A-Za-z0-9])sk-[A-Za-z0-9]{20,}' },
    @{ Name = 'slack-token'; Regex = '(^|[^A-Za-z0-9])xox[baprs]-[A-Za-z0-9-]{10,}' },
    @{ Name = 'telegram-bot-token'; Regex = '(^|[^A-Za-z0-9])[0-9]{8,10}:[A-Za-z0-9_-]{35}' },
    @{ Name = 'jwt'; Regex = '(^|[^A-Za-z0-9])eyJ[A-Za-z0-9_-]{10,}[.][A-Za-z0-9_-]{10,}[.][A-Za-z0-9_-]{10,}' }
)

# The assignment shape needs interpretation: a quoted value after a key name.
$AssignRegex = '(api[_-]?key|secret[_-]?key|client[_-]?secret|password|passwd|auth[_-]?token|access[_-]?token|api[_-]?token)[[:space:]]*[:=][[:space:]]*["''][^"'']{8,}["'']'

# Values that LOOK like secrets but are placeholders. They are reported as
# warnings, never as blocks.
$PlaceholderRegex = '(?i)^(x{3,}|\*{3,}|<[^>]*>|\{[^}]*\}|\$\{[^}]*\}|%[A-Za-z_]+%|changeme|change[_-]?me|placeholder|example|sample|dummy|redacted|your[_-]?\w*|insert[_-]?\w*|todo|none|null|secret|password|test|abc123|\.\.\.|\.\.\.\.)'

$ValueRegex = [regex]'["'']([^"'']{8,})["'']'

function Get-Git {
    $cmd = Get-Command git -ErrorAction SilentlyContinue
    if (-not $cmd) { return '' }
    return $cmd.Source
}

function Invoke-Git {
    param(
        [Parameter(Mandatory = $true)][string]$Git,
        [Parameter(Mandatory = $true)][string]$Repo,
        [string]$GitDir = '',
        [Parameter(Mandatory = $true)][string[]]$GitArgs
    )
    $prev = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    # -GitDir wins over -C: in container the .git pointer holds a Windows path
    # (E:/...) that linux git cannot resolve, so the gitdir is passed
    # explicitly. On the host both work; the explicit form is unambiguous.
    if ($GitDir) {
        $out = & $Git --git-dir=$GitDir @GitArgs 2>$null
    } else {
        $out = & $Git -C $Repo @GitArgs 2>$null
    }
    $ErrorActionPreference = $prev
    $code = $LASTEXITCODE
    if ($null -eq $code) { $code = -1 }
    return @{ Code = $code; Out = $out }
}

function Test-Placeholder {
    param([string]$Value)
    if ([string]::IsNullOrWhiteSpace($Value)) { return $true }
    return [regex]::IsMatch($Value, $PlaceholderRegex)
}

function Scan-Lines {
    param(
        [Parameter(Mandatory = $true)][AllowEmptyString()][string[]]$Lines,
        [Parameter(Mandatory = $true)][string]$Origin
    )
    $blocks = @()
    $warns = @()
    foreach ($line in $Lines) {
        if ([string]::IsNullOrEmpty($line)) { continue }
        foreach ($p in $FixedPatterns) {
            if ($line -match $p.Regex) {
                $blocks += ($p.Name + ' @ ' + $Origin)
                break
            }
        }
        if ($line -match $AssignRegex) {
            $value = ''
            $m = $ValueRegex.Match($line)
            if ($m.Success) { $value = $m.Groups[1].Value }
            if (Test-Placeholder -Value $value) {
                $warns += ('placeholder-value @ ' + $Origin)
            } else {
                $blocks += ('assigned-secret @ ' + $Origin)
            }
        }
    }
    return @{ Blocks = $blocks; Warns = $warns }
}

function Invoke-Scan {
    $blocks = @()
    $warns = @()
    $scanned = 0

    if ($ProbeFile) {
        if (-not (Test-Path -LiteralPath $ProbeFile)) {
            Write-Err ('ERROR=probe file not found: ' + $ProbeFile)
            return 2
        }
        $lines = @(Get-Content -LiteralPath $ProbeFile -ErrorAction Stop)
        $scanned = 1
        $r = Scan-Lines -Lines $lines -Origin $ProbeFile
        $blocks += $r.Blocks
        $warns += $r.Warns
    } elseif ($StagedDiff) {
        # ONLY the lines this change ADDS.
        #
        # MEASURED 2026-10-27: the index-wide scan reported 9 blocks in a
        # repository whose files were ALREADY published - documentation that
        # lists EXAMPLE tokens (an AWS-style access key id and a GitHub
        # token placeholder, both with the official dummy values). Those are
        # pre-existing and public; blocking a queue delivery because of
        # them is a false accusation, and a false accusation costs more than
        # a missed secret.
        #
        # The question that matters is narrow and answerable: does THIS
        # change introduce a secret? The staged diff is exactly that.
        #
        # NOTE: the example values above are described, not written. A
        # literal in this file would make the scanner block its own source.
        $git = Get-Git
        if (-not $git) {
            Write-Err 'ERROR=no git on PATH'
            return 2
        }
        $repo = $RepoPath
        if (-not $repo) { $repo = (Get-Location).Path }
        $probe = Invoke-Git -Git $git -Repo $repo -GitDir $GitDir -GitArgs @('rev-parse', '--git-dir')
        if ($probe.Code -ne 0) {
            Write-Err ('ERROR=not a git repo: ' + $repo)
            return 2
        }
        $diff = Invoke-Git -Git $git -Repo $repo -GitDir $GitDir -GitArgs @('diff', '--cached', '-U0', '--no-color')
        if ($diff.Code -ne 0) {
            Write-Err ('ERROR=cannot read the staged diff: ' + $repo)
            return 2
        }
        $currentFile = '(staged)'
        $added = 0
        foreach ($l in @($diff.Out)) {
            $line = [string]$l
            if ($line -match '^\+\+\+ b/(.*)$') { $currentFile = $Matches[1]; continue }
            if ($line -match '^\+\+\+ ') { continue }
            if (-not $line.StartsWith('+')) { continue }
            $added++
            $r = Scan-Lines -Lines @($line.Substring(1)) -Origin $currentFile
            $blocks += $r.Blocks
            $warns += $r.Warns
        }
        $scanned = $added
        if ($added -eq 0) {
            Write-Out 'SCANNED=0 - nimic in index nu e nou; nu e verdict de curatenie, e lipsa de material.'
        }
    } else {
        $git = Get-Git
        if (-not $git) {
            Write-Err 'ERROR=no git on PATH'
            return 2
        }
        $repo = $RepoPath
        if (-not $repo) { $repo = (Get-Location).Path }
        $probe = Invoke-Git -Git $git -Repo $repo -GitDir $GitDir -GitArgs @('rev-parse', '--git-dir')
        if ($probe.Code -ne 0) {
            Write-Err ('ERROR=not a git repo: ' + $repo)
            return 2
        }
        # Search the INDEX, not the working tree: what is staged is what would
        # enter the commit. -I skips binary files.
        foreach ($p in $FixedPatterns) {
            $res = Invoke-Git -Git $git -Repo $repo -GitDir $GitDir -GitArgs @('grep', '-n', '-I', '-E', '-e', $p.Regex, '--cached')
            if ($res.Code -eq 0) {
                foreach ($l in @($res.Out)) {
                    $blocks += ($p.Name + ' @ ' + $l)
                }
            }
        }
        $res = Invoke-Git -Git $git -Repo $repo -GitDir $GitDir -GitArgs @('grep', '-n', '-I', '-E', '-e', $AssignRegex, '--cached')
        if ($res.Code -eq 0) {
            foreach ($l in @($res.Out)) {
                $value = ''
                $m = $ValueRegex.Match([string]$l)
                if ($m.Success) { $value = $m.Groups[1].Value }
                if (Test-Placeholder -Value $value) {
                    $warns += ('placeholder-value @ ' + $l)
                } else {
                    $blocks += ('assigned-secret @ ' + $l)
                }
            }
        }
        $scanned = @(Invoke-Git -Git $git -Repo $repo -GitDir $GitDir -GitArgs @('ls-files', '--cached')).Out.Count
    }

    Write-Out ('SCANNED=' + $scanned)
    Write-Out ('BLOCKS=' + $blocks.Count)
    Write-Out ('WARNS=' + $warns.Count)
    foreach ($b in $blocks) { Write-Out ('BLOCK ' + $b) }
    foreach ($w in $warns) { Write-Out ('WARN ' + $w) }

    if ($blocks.Count -gt 0) {
        Write-Out 'SCAN_BLOCKED - nu se comite cu secrete in index.'
        return 1
    }
    Write-Out 'SCAN_OK'
    return 0
}

# The exit code is this script's OWN. A crash must never look like a block:
# an accusation needs proof, so an unmeasurable run exits 2 (error), not 1.
$code = 0
try {
    $code = Invoke-Scan
} catch {
    Write-Err ('ERROR=' + $_.Exception.Message)
    Write-Err 'SCAN_ERROR - masuratoarea nu a putut rula. Nu e verdict.'
    $code = 2
}
exit $code
