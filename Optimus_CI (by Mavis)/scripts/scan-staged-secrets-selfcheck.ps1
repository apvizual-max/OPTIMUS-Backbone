# scan-staged-secrets-selfcheck.ps1
# The gate's own proof. A gate that cannot fail is not a gate, so every check
# here is run in BOTH directions: the detector must BLOCK what is planted and
# must NOT block what is harmless.
#
# Probe fixtures live in state/tmp/ which is gitignored, so a planted secret
# never enters the index. The fixture strings are built by concatenation on
# purpose: this file is itself staged, and it must not trip its own detector.
#
# ASCII ONLY: executed by Windows PowerShell 5.1.

$ErrorActionPreference = 'Stop'

$ScriptRoot = Split-Path -Parent $PSScriptRoot
$Scanner = Join-Path $ScriptRoot 'scripts\scan-staged-secrets.ps1'
$ScratchLib = Join-Path $PSScriptRoot 'git-scratch.ps1'
if (-not (Test-Path -LiteralPath $ScratchLib)) {
    Write-Output ('ERROR=lipseste scripts\git-scratch.ps1: ' + $ScratchLib)
    exit 2
}
. $ScratchLib
# The fixtures include a real git repository (diff-mode-repo). They are built
# OUTSIDE the Google Drive mirror, so DriveFS never administers a live .git
# directory.
$ScratchRoot = Assert-ScratchOutsideMirror -ScratchRoot (Get-GitScratchRoot -ProjectRoot $ScriptRoot) -ProjectRoot $ScriptRoot
$TmpDir = Join-Path $ScratchRoot 'secrets-selfcheck'

$problems = 0
$unknown = 0

function Write-Out {
    param([Parameter(Mandatory = $true)][string]$Message)
    [Console]::Out.WriteLine($Message)
}

function Fail {
    param([string]$Message)
    Write-Out ('FAIL ' + $Message)
    $script:problems++
}

function Unknown {
    param([string]$Message)
    Write-Out ('UNKNOWN ' + $Message)
    $script:unknown++
}

function Invoke-Scanner {
    param([string]$ProbeFile)
    $prev = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    $out = & powershell -NoProfile -File $Scanner -ProbeFile $ProbeFile 2>&1
    $ErrorActionPreference = $prev
    $code = $LASTEXITCODE
    if ($null -eq $code) { $code = -1 }
    return @{ Code = $code; Out = ($out -join "`n") }
}

# The scanner over a repository, in the index-wide mode or in the diff mode.
function Invoke-ScannerRepo {
    param(
        [Parameter(Mandatory = $true)][string]$Repo,
        [switch]$StagedDiff
    )
    $prev = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    if ($StagedDiff) {
        $out = & powershell -NoProfile -File $Scanner -StagedDiff -RepoPath $Repo 2>&1
    } else {
        $out = & powershell -NoProfile -File $Scanner -RepoPath $Repo 2>&1
    }
    $ErrorActionPreference = $prev
    $code = $LASTEXITCODE
    if ($null -eq $code) { $code = -1 }
    return @{ Code = $code; Out = ($out -join "`n") }
}

# --- check 1: static shape of the scanner ---------------------------------
if (-not (Test-Path -LiteralPath $Scanner)) {
    Fail 'scanner file missing'
} else {
    $bytes = [System.IO.File]::ReadAllBytes($Scanner)
    $nonAscii = 0
    foreach ($b in $bytes) { if ($b -gt 127) { $nonAscii++ } }
    $src = [System.IO.File]::ReadAllText($Scanner)
    $parseErrors = $null
    [void][System.Management.Automation.Language.Parser]::ParseInput($src, [ref]$null, [ref]$parseErrors)
    $exitOwn = $src -match '(?m)^\s*exit\s+\$code\s*$'
    $contaminated = ($src -match 'Write-Output')
    if ($nonAscii -eq 0 -and $parseErrors.Count -eq 0 -and $exitOwn -and -not $contaminated) {
        Write-Out ('OK   scan-staged-secrets.ps1 - bytes=' + $bytes.Length + ' nonascii=' + $nonAscii + ' parseErrors=' + $parseErrors.Count + ' exitOwn=' + $exitOwn + ' writeOutputContamination=' + $contaminated)
    } else {
        Fail ('scanner static check - nonascii=' + $nonAscii + ' parseErrors=' + $parseErrors.Count + ' exitOwn=' + $exitOwn + ' writeOutputContamination=' + $contaminated)
    }
}

if (-not (Test-Path -LiteralPath $TmpDir)) {
    New-Item -ItemType Directory -Path $TmpDir -Force | Out-Null
}

# --- check 2: a planted secret MUST be blocked ----------------------------
# Built by concatenation: this source file is staged, and a literal secret
# here would block the very commit that introduces the gate.
$planted = @(
    ('AKIA' + 'IOSFODNN7EXAMPLE'),
    ('ghp_' + ('a1b2c3d4e5f6' + 'g7h8i9j0k1l2m3n4o5p6q7r8')),
    ('api' + '_key = "' + ('zYx' + 'wVuT' + 'sRqP' + 'oNmL') + '"')
) -join "`n"
$secretFixture = Join-Path $TmpDir 'probe-secret.txt'
[System.IO.File]::WriteAllText($secretFixture, $planted, (New-Object System.Text.UTF8Encoding($false)))

$r = Invoke-Scanner -ProbeFile $secretFixture
$blocks = 0
if ($r.Out -match 'BLOCKS=(\d+)') { $blocks = [int]$Matches[1] }
if ($r.Code -eq 1 -and $blocks -ge 1) {
    Write-Out ('OK   proba-secret - o cheie plantata e blocata (BLOCKS=' + $blocks + ', EXIT 1)')
} elseif ($r.Code -eq 2) {
    Unknown ('proba-secret - scannerul nu a putut rula (EXIT 2)')
} else {
    Fail ('proba-secret - asteptat EXIT 1 cu BLOCKS>=1, obtinut EXIT ' + $r.Code + ' BLOCKS=' + $blocks)
}

# --- check 2b: a private key header MUST be blocked -----------------------
# Built by concatenation, for the same reason as check 2.
$pkHeader = ('-----BEGIN ' + 'RSA ' + 'PRIVATE KEY-----')
$pkFixture = Join-Path $TmpDir 'probe-privatekey.txt'
[System.IO.File]::WriteAllText($pkFixture, ($pkHeader + "`n" + 'MIIEow...'), (New-Object System.Text.UTF8Encoding($false)))

$r2b = Invoke-Scanner -ProbeFile $pkFixture
$blocks2b = 0
if ($r2b.Out -match 'BLOCKS=(\d+)') { $blocks2b = [int]$Matches[1] }
if ($r2b.Code -eq 1 -and $blocks2b -ge 1) {
    Write-Out ('OK   proba-cheie-privata - un header de cheie privata e blocat (BLOCKS=' + $blocks2b + ', EXIT 1)')
} elseif ($r2b.Code -eq 2) {
    Unknown 'proba-cheie-privata - scannerul nu a putut rula (EXIT 2)'
} else {
    Fail ('proba-cheie-privata - asteptat EXIT 1 cu BLOCKS>=1, obtinut EXIT ' + $r2b.Code + ' BLOCKS=' + $blocks2b)
}

# --- check 3: a placeholder MUST NOT be blocked ---------------------------
$harmless = @(
    ('api' + '_key = "your-key-here"'),
    ('password' + ' = "changeme"'),
    ('JULES' + '_API_KEY este o variabila de mediu, nu o valoare.'),
    ('token = "<' + 'TOKEN_AICI>' + '"'),
    'nothing to see here'
) -join "`n"
$cleanFixture = Join-Path $TmpDir 'probe-clean.txt'
[System.IO.File]::WriteAllText($cleanFixture, $harmless, (New-Object System.Text.UTF8Encoding($false)))

$r2 = Invoke-Scanner -ProbeFile $cleanFixture
$blocks2 = 0
if ($r2.Out -match 'BLOCKS=(\d+)') { $blocks2 = [int]$Matches[1] }
if ($r2.Code -eq 0 -and $blocks2 -eq 0) {
    Write-Out ('OK   proba-placeholder - un placeholder NU e blocat (BLOCKS=0, EXIT 0)')
} elseif ($r2.Code -eq 2) {
    Unknown ('proba-placeholder - scannerul nu a putut rula (EXIT 2)')
} else {
    Fail ('proba-placeholder - asteptat EXIT 0 cu BLOCKS=0, obtinut EXIT ' + $r2.Code + ' BLOCKS=' + $blocks2)
}

# --- check 3b: blank lines MUST NOT crash the scanner ---------------------
# Regression probe. Measured 2026-10-27: a mandatory [string[]] parameter
# rejects an empty string, so a file with blank lines made the scanner THROW.
# A throw used to exit 1 - which looked like "blocked", i.e. the gate
# accused a file that had no secret in it. A crash must be exit 2.
$blankFixture = Join-Path $TmpDir 'probe-blank-lines.txt'
[System.IO.File]::WriteAllText($blankFixture, ("`n`nline with content`n`n" + 'another line' + "`n`n"), (New-Object System.Text.UTF8Encoding($false)))

$r3b = Invoke-Scanner -ProbeFile $blankFixture
if ($r3b.Code -eq 0 -and $r3b.Out -match 'SCAN_OK') {
    Write-Out 'OK   proba-linii-goale - liniile goale nu arunca exceptie (EXIT 0, SCAN_OK)'
} else {
    Fail ('proba-linii-goale - asteptat EXIT 0 cu SCAN_OK, obtinut EXIT ' + $r3b.Code)
}

# --- check 4: the scanner must not block its own source -------------------
$ownFixture = Join-Path $TmpDir 'probe-own-source.txt'
$ownSrc = [System.IO.File]::ReadAllText($Scanner)
[System.IO.File]::WriteAllText($ownFixture, $ownSrc, (New-Object System.Text.UTF8Encoding($false)))
$r3 = Invoke-Scanner -ProbeFile $ownFixture
$blocks3 = 0
if ($r3.Out -match 'BLOCKS=(\d+)') { $blocks3 = [int]$Matches[1] }
if ($r3.Code -eq 0 -and $blocks3 -eq 0) {
    Write-Out 'OK   proba-cod-propriu - scannerul nu se blocheaza pe propriul cod'
} elseif ($r3.Code -eq 2) {
    Unknown 'proba-cod-propriu - scannerul nu a putut rula (EXIT 2)'
} else {
    Fail ('proba-cod-propriu - asteptat EXIT 0, obtinut EXIT ' + $r3.Code + ' BLOCKS=' + $blocks3)
}

# --- check 5: the real index of this repo must be clean --------------------
$prev = $ErrorActionPreference
$ErrorActionPreference = 'Continue'
$out5 = & powershell -NoProfile -File $Scanner -RepoPath $ScriptRoot 2>&1
$ErrorActionPreference = $prev
$code5 = $LASTEXITCODE
if ($null -eq $code5) { $code5 = -1 }
$text5 = ($out5 -join "`n")
if ($text5 -match 'SCAN_OK') {
    Write-Out 'OK   proba-index-real - indexul repo-ului e curat'
} elseif ($code5 -eq 2) {
    Unknown 'proba-index-real - scannerul nu a putut citi indexul (EXIT 2)'
} else {
    Fail ('proba-index-real - indexul repo-ului are secrete sau scanarea a esuat')
    foreach ($l in @($out5)) { Write-Out ('   ' + $l) }
}

# --- check 6: the -StagedDiff mode measures THIS change --------------------
# MEASURED 2026-10-27: the index-wide scan reported 9 blocks in MAVIS-CLOUD
# for documentation that was ALREADY published, and it blocked a queue
# delivery that carried no secret at all. The diff mode answers the narrow
# question: does THIS change introduce a secret?
#
# Three probes, because the mode must be NARROWER, not WEAKER:
#   a clean diff in a repo that already holds example tokens -> not blocked
#   the same repo in the old index-wide mode                  -> still blocked
#   a diff that ADDS a secret                                  -> blocked
$diffRepo = Join-Path $TmpDir 'diff-mode-repo'
if (Test-Path -LiteralPath $diffRepo) { Remove-Item -LiteralPath $diffRepo -Recurse -Force }
New-Item -ItemType Directory -Path $diffRepo -Force | Out-Null
$enc = New-Object System.Text.UTF8Encoding($false)

$example = @(
    ('AWS key example: ' + ('AKIA' + 'IOSFODNN7EXAMPLE')),
    ('GitHub token example: ' + ('ghp_' + '0123456789abcdefghijABCDEFGHIJ'))
) -join "`n"
[System.IO.File]::WriteAllText((Join-Path $diffRepo 'docs-existing.md'), $example, $enc)
$prev = $ErrorActionPreference
$ErrorActionPreference = 'Continue'
# THE FIXTURE MUST OWN ITS OWN GITDIR. MEASURED 2026-10-27: this very file
# wrote a commit into the PRODUCTION repository - author "Fixture
# <fixture@localhost>", message "fixture: pre-existing documentation", 127
# files, every mode flipped 644 -> 755. Cause: `git init` landed on a real
# worktree (the scratch resolver had no usable gitdir inside the container),
# re-initialized the shared gitdir and committed the whole tree into main.
#
# The guard below refuses to continue the moment the fixture directory can
# still REACH a real repository. It runs BEFORE any write, so there is
# nothing to undo afterwards: a self-check that can damage production must
# fail loudly, not silently repair itself afterwards.
$guardPrev = $ErrorActionPreference
$ErrorActionPreference = 'Continue'
$reachable = ''
try {
    $reachable = ((& git -C $diffRepo rev-parse --absolute-git-dir 2>$null) -join '').Trim()
} catch {
    $reachable = ''
}
$ErrorActionPreference = $guardPrev
if ($reachable) {
    Write-Output ('FAIL proba-dif-control - FIXTURE INSIDE A REAL REPO: ' + $diffRepo + ' -> ' + $reachable)
    Write-Output 'The fixture would rewrite the history of a real repository. Aborting before any write.'
    exit 1
}

& git -C $diffRepo init -b main 2>&1 | Out-Null
& git -C $diffRepo config user.name 'Fixture' | Out-Null
& git -C $diffRepo config user.email 'fixture@localhost' | Out-Null
& git -C $diffRepo add -A | Out-Null
& git -C $diffRepo commit -m 'fixture: pre-existing documentation' 2>&1 | Out-Null
# After init: the gitdir must live INSIDE the fixture directory. A gitdir
# somewhere else means `git init` re-initialized a REAL repository, and the
# commit above did not land where it was supposed to land.
$ownPrev = $ErrorActionPreference
$ErrorActionPreference = 'Continue'
$ownGitDir = ''
try {
    $ownGitDir = ((& git -C $diffRepo rev-parse --absolute-git-dir 2>$null) -join '').Trim()
} catch {
    $ownGitDir = ''
}
$ErrorActionPreference = $ownPrev
# Comparatia trebuie sa fie AGNOSTICA de separator: git intoarce calea cu '/',
# iar $diffRepo o construieste cu '\'. Un check care compara altceva decat
# cea ce intentioneaza e un check care nu poate fi de incredere.
$ownNorm = ($ownGitDir -replace '\\', '/').TrimEnd('/')
$repoNorm = ($diffRepo -replace '\\', '/').TrimEnd('/')
if ($ownNorm -and $ownNorm.StartsWith($repoNorm + '/', [System.StringComparison]::OrdinalIgnoreCase)) {
    Write-Out ('OK   proba-dif-control - fixture-ul are propriul gitdir: ' + $ownGitDir)
} else {
    Fail ('proba-dif-control - fixture-ul NU are propriul gitdir: ' + $ownGitDir + ' (asteptat sub ' + $diffRepo + ')')
}
[System.IO.File]::WriteAllText((Join-Path $diffRepo 'clean.md'), 'nothing to see here', $enc)
& git -C $diffRepo add -- clean.md | Out-Null
$ErrorActionPreference = $prev

$rd = Invoke-ScannerRepo -Repo $diffRepo -StagedDiff
$blocksd = 0
if ($rd.Out -match 'BLOCKS=(\d+)') { $blocksd = [int]$Matches[1] }
if ($rd.Code -eq 0 -and $blocksd -eq 0) {
    Write-Out 'OK   proba-dif-curat - un diff curat NU e blocat, chiar daca repo-ul are deja documente cu exemple publicate'
} else {
    Fail ('proba-dif-curat - asteptat EXIT 0 cu BLOCKS=0, obtinut EXIT ' + $rd.Code + ' BLOCKS=' + $blocksd)
}

$ri = Invoke-ScannerRepo -Repo $diffRepo
$blocksi = 0
if ($ri.Out -match 'BLOCKS=(\d+)') { $blocksi = [int]$Matches[1] }
if ($ri.Code -eq 1 -and $blocksi -ge 1) {
    Write-Out ('OK   proba-dif-control - modul index detecteaza in continuare exemplele deja publicate (BLOCKS=' + $blocksi + '); diful este mai NARIC, nu mai slab')
} else {
    Fail ('proba-dif-control - asteptat EXIT 1 cu BLOCKS>=1, obtinut EXIT ' + $ri.Code + ' BLOCKS=' + $blocksi)
}

$introduced = @(
    ('AKIA' + 'IOSFODNN7EXAMPLE'),
    ('ghp_' + ('a1b2c3d4e5f6' + 'g7h8i9j0k1l2m3n4o5p6q7r8'))
) -join "`n"
[System.IO.File]::WriteAllText((Join-Path $diffRepo 'introduced.md'), $introduced, $enc)
$prev = $ErrorActionPreference
$ErrorActionPreference = 'Continue'
& git -C $diffRepo add -- introduced.md 2>&1 | Out-Null
$ErrorActionPreference = $prev

$rs = Invoke-ScannerRepo -Repo $diffRepo -StagedDiff
$blockss = 0
if ($rs.Out -match 'BLOCKS=(\d+)') { $blockss = [int]$Matches[1] }
if ($rs.Code -eq 1 -and $blockss -ge 1) {
    Write-Out ('OK   proba-dif-secret - un secret adus de ACEASTA schimbare e blocat (BLOCKS=' + $blockss + ')')
} else {
    Fail ('proba-dif-secret - asteptat EXIT 1 cu BLOCKS>=1, obtinut EXIT ' + $rs.Code + ' BLOCKS=' + $blockss)
}

# --- verdict --------------------------------------------------------------
Write-Out ('SECRET_PROBLEMS=' + $problems + ' UNKNOWN=' + $unknown)
if ($unknown -gt 0) {
    Write-Out 'Poarta nu poate decide: exista masuratori necompletate.'
    exit 3
}
if ($problems -gt 0) {
    Write-Out 'Poarta a esuat: scannerul de secrete nu se comporta cum trebuie.'
    exit 1
}
Write-Out 'Scannerul de secrete e functional si probat in ambele sensuri.'
exit 0
