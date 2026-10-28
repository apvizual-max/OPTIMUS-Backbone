<#
.SYNOPSIS
  One command that certifies the Control Center, with fault injection.

.DESCRIPTION
  verify-ui.ps1 is FILE-LEVEL: it proves the page parses and the endpoints answer.
  The in-page self-test is BEHAVIOURAL: it proves a handler reaches a connected
  node. Neither proves the system SURVIVES being abused, and neither knows
  whether it is capable of failing at all.

  This harness adds the third thing:

    1. The fault-injection pass. Deliberately hand the system bad input - a
       corrupt job marker, a missing id, a malformed body, an unknown action,
       a job that will never finish - and require that each one produces a
       CLEAN, REPORTED failure rather than a hang, a 500, or a lie.

    2. The self-check. Before it certifies anything, it proves it CAN fail, by
       asserting a deliberately-wrong expectation and requiring the runner to
       catch it. A suite that has never reported a failure has not been shown
       to be able to, and a green run from such a suite is not evidence.

    3. The streak. Certification requires N CONSECUTIVE clean runs. One clean run
       is a sample; a streak is a habit, and only the second distinguishes a
       system that works from one that got lucky once.

  ASCII-only on purpose: PowerShell 5.1 reads a BOM-less .ps1 as ANSI, so a
  non-ASCII literal here is a parse hazard rather than a cosmetic one.

.PARAMETER Runs
  Consecutive clean runs required to certify. Default 3.

.PARAMETER SelfCheck
  Run only the self-check, to prove the harness can detect a failure.

.EXAMPLE
  .\health-harness.ps1
.EXAMPLE
  .\health-harness.ps1 -Runs 5
#>
[CmdletBinding()]
param(
  [int]$Runs = 3,
  [switch]$SelfCheck,
  [switch]$SelfTestScanner
)

$ErrorActionPreference = 'Stop'
$Root   = 'C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard'
$CC     = Join-Path $Root '90_CONTROL_CENTER'
$StateF = Join-Path $CC 'api\live-state.json'
$HistF  = Join-Path $CC 'api\state-history.jsonl'
$AskDir = Join-Path $CC 'api\ask'
$Base   = 'http://127.0.0.1:8900'
$Tmp    = Join-Path $env:TEMP 'cc-harness'
if (-not (Test-Path -LiteralPath $Tmp)) { New-Item -ItemType Directory -Path $Tmp -Force | Out-Null }

$script:Results = New-Object System.Collections.Generic.List[object]

function Check {
  param([string]$Dim, [string]$Name, [bool]$Ok, [string]$Detail = '')
  $script:Results.Add([pscustomobject]@{ Dim = $Dim; Name = $Name; Ok = $Ok; Detail = $Detail })
}

function Get-Http {
  param([string]$Url, [int]$TimeoutSec = 20, [string]$Method = 'GET', [string]$BodyFile)
  $o = Join-Path $Tmp ('r' + [guid]::NewGuid().ToString('N').Substring(0, 8) + '.json')
  $args = @('-s', '-o', $o, '-w', '%{http_code}', '--max-time', "$TimeoutSec")
  if ($Method -ne 'GET') { $args += @('-X', $Method, '-H', 'Content-Type: application/json', '--data-binary', "@$BodyFile") }
  $args += $Url
  $code = & curl.exe @args 2>$null
  $body = ''
  if (Test-Path $o) { try { $body = [System.IO.File]::ReadAllText($o, [Text.Encoding]::UTF8) } catch { } }
  return [pscustomobject]@{ Code = [string]$code; Body = $body; Bytes = $body.Length }
}

function New-Body {
  param([string]$Text)
  $p = Join-Path $Tmp ('b' + [guid]::NewGuid().ToString('N').Substring(0, 8) + '.json')
  [System.IO.File]::WriteAllText($p, $Text, (New-Object Text.UTF8Encoding($false)))
  return $p
}

# Return a PowerShell file with its COMMENTS removed, so a scanner looks at code
# rather than at prose describing the defect it is hunting. A '#' only starts a
# comment when it is not inside a single- or double-quoted string, so quote
# state is tracked per line. Unlike a naive split, this does not discard a line
# that merely contains a '#' inside a string.
function Get-CodeOnly {
  param([string]$Path)
  $out = New-Object System.Collections.Generic.List[string]
  foreach ($line in [System.IO.File]::ReadAllLines($Path, [Text.Encoding]::UTF8)) {
    $sb = ''
    $inS = $false; $inD = $false
    for ($i = 0; $i -lt $line.Length; $i++) {
      $c = $line[$i]
      if ($c -eq "'" -and -not $inD) { $inS = -not $inS; $sb += $c; continue }
      if ($c -eq '"' -and -not $inS) { $inD = -not $inD; $sb += $c; continue }
      if ($c -eq '#' -and -not $inS -and -not $inD) { break }
      $sb += $c
    }
    $out.Add($sb)
  }
  return ($out -join "`n")
}

# --------------------------------------------------------- scanner unit test --
# Get-CodeOnly decides whether a hardcoded path is CODE or PROSE, and a scanner
# that is wrong in either direction is worse than no scanner: one that reads
# comments fails on the comment explaining what it hunts, and one that strips too
# much misses the defect. So it is tested here, in the harness, rather than by
# extracting the function with a regex from a test file elsewhere - which is what
# was tried first, and which silently grabbed the wrong span and reported five
# False answers that looked like five broken behaviours.
#
# It must be correct in BOTH directions: ignore a path in a comment, and still
# find one that is really there.
function Invoke-ScannerSelfTest {
  $probe = Join-Path $Tmp 'scanner-fixture.ps1'
  $lines = @(
    '# prose mentioning C:\Users\someone must be stripped',
    '$real = ''C:\Users\actualuser\.thing''   # trailing C:\Users\nope',
    '$h = ''#0B0F17''   # a # inside a string must survive',
    '$z = 1  # done'
  )
  [System.IO.File]::WriteAllText($probe, ($lines -join "`r`n"), (New-Object Text.UTF8Encoding($false)))
  $out = (Get-CodeOnly -Path $probe) -join "`n"

  $planted = Join-Path $Tmp 'scanner-planted.ps1'
  [System.IO.File]::WriteAllText($planted, "# prose only`r`n`$a = 'C:\Users\planted\x'`r`n", (New-Object Text.UTF8Encoding($false)))
  $detectsPlanted = ((Get-CodeOnly -Path $planted) -join "`n") -match 'C:\\Users\\planted'

  $t = [ordered]@{
    'strips a path inside a comment'      = (-not ($out -match 'someone'))
    'keeps a real path in code'           = ($out -match 'actualuser')
    'strips a path in a trailing comment' = (-not ($out -match 'nope'))
    'keeps a # inside a quoted string'    = ($out -match '#0B0F17')
    'detects a genuinely planted path'    = [bool]$detectsPlanted
  }
  $bad = @($t.GetEnumerator() | Where-Object { -not $_.Value })
  # Write-Host, NOT Write-Output. A function's uncaptured output joins its return
  # value, so the five detail lines were being collected INTO the boolean: the
  # test passed while printing no evidence at all, and $ok silently became a
  # six-element array that merely happened to be truthy. A check that hides the
  # reason it passed is the same defect one level up.
  $t.GetEnumerator() | ForEach-Object { Write-Host ("  {0,-36} {1}" -f $_.Key, $(if ($_.Value) { 'ok' } else { 'WRONG' })) }
  return [bool]($bad.Count -eq 0)
}

# ---------------------------------------------------------------- self-check --
# Runs FIRST, and gates the whole harness. If the runner cannot detect a known
# bad expectation, nothing it says about the product means anything.
function Invoke-SelfCheck {
  $s = New-Object System.Collections.Generic.List[object]
  $s.Add([pscustomobject]@{ Name = 'detects a wrong boolean'; Ok = ($false -eq $true) })
  $s.Add([pscustomobject]@{ Name = 'detects a wrong number';   Ok = ((@(1, 2, 3).Count -eq 4)) })
  $s.Add([pscustomobject]@{ Name = 'detects a wrong string';   Ok = ('abc' -eq 'abd') })
  $s.Add([pscustomobject]@{ Name = 'reports the right count';  Ok = (@(1, 2, 3).Count -eq 3) })
  # Negative controls: deliberately WRONG. A correct runner must mark every one
  # of these as a failure. If it marks none, the runner is blind.
  #
  # The fourth one was originally `'7' -eq 7` - a "wrong type" check. It was NOT
  # wrong. PowerShell's -eq coerces the left operand to the right operand's type,
  # so `'7' -eq 7` is TRUE, the control passed, and the self-check reported 3 of 4
  # on its own first run. The instrument was right and the fixture was lying: a
  # planted fault that is actually a PASS, which is the single most dangerous
  # shape a test defect can take. Replaced with a membership test, which has no
  # coercion path to accidentally satisfy.
  $neg = @(
    [pscustomobject]@{ Name = 'catches a wrong boolean';  Ok = ($false -eq $true) },
    [pscustomobject]@{ Name = 'catches a wrong number';    Ok = (@(1, 2, 3).Count -eq 4) },
    [pscustomobject]@{ Name = 'catches a wrong string';    Ok = ('abc' -eq 'abd') },
    [pscustomobject]@{ Name = 'catches a wrong membership'; Ok = (@(1, 2, 3) -contains 4) }
  )
  # Positive control: deliberately RIGHT. A correct runner must NOT flag it.
  # Without this, a runner that simply marked everything failed would satisfy the
  # negative controls perfectly and certify a broken system - a watchdog that
  # cries wolf, which is worse than no watchdog at all.
  #
  # The first version of this self-check asserted that ALL FOUR entries had to
  # be caught, positive control included, and it failed on its own first run. The
  # TEST was wrong, not the runner: a deliberately correct expectation sat in a
  # list of deliberately incorrect ones and got counted as a defect. An
  # instrument whose own expectations are wrong is the exact failure this file
  # exists to catch - and this one caught it on the first run, which is the
  # evidence that the idea was worth building.
  $pos = @(
    [pscustomobject]@{ Name = 'does not cry wolf'; Ok = (@(1, 2, 3).Count -eq 3) }
  )

  $negCaught = @($neg | Where-Object { -not $_.Ok }).Count
  $posAlarms = @($pos | Where-Object { -not $_.Ok }).Count

  $ok = ($negCaught -eq $neg.Count) -and ($posAlarms -eq 0) -and ($neg.Count -gt 0) -and ($pos.Count -gt 0)
  Check -Dim 'HARNESS' -Name 'harness detects planted failures' -Ok ($negCaught -eq $neg.Count) -Detail ("{0}/{1} caught" -f $negCaught, $neg.Count)
  Check -Dim 'HARNESS' -Name 'harness does not cry wolf' -Ok ($posAlarms -eq 0) -Detail ("{0} false alarm(s) on {1} correct value" -f $posAlarms, $pos.Count)
  Check -Dim 'HARNESS' -Name 'harness is capable of failing' -Ok $ok -Detail ("{0}/{1} faults caught, {2} false alarms" -f $negCaught, $neg.Count, $posAlarms)
  return $ok
}

# ----------------------------------------------------------------- dimensions --
function Invoke-Dimensions {
  # D1 syntax / rendering
  $idx = Join-Path $CC 'index.html'
  $html = [System.IO.File]::ReadAllText($idx, [Text.Encoding]::UTF8)
  $m = [regex]::Match($html, '(?s)<script>(.*?)</script>')
  Check -Dim 'D1' -Name 'inline script present' -Ok ($m.Success -and $m.Groups[1].Value.Length -gt 500) -Detail ("{0} chars" -f $(if ($m.Success) { $m.Groups[1].Value.Length } else { 0 }))
  $js = Join-Path $Tmp 'inline.mjs'
  [System.IO.File]::WriteAllText($js, $m.Groups[1].Value, (New-Object Text.UTF8Encoding($false)))
  & node --check $js *> $null
  Check -Dim 'D1' -Name 'inline script parses' -Ok ($LASTEXITCODE -eq 0) -Detail "node exit=$LASTEXITCODE"
  Check -Dim 'D1' -Name 'no U+FFFD in page' -Ok (-not $html.Contains([char]0xFFFD)) -Detail ''
  Check -Dim 'D1' -Name 'no external resources' -Ok (-not [regex]::IsMatch($html, '(?i)(src|href)\s*=\s*["'']https?://')) -Detail 'offline requirement'

  # D5 api / stalls - the real test is that the REQUEST path stays fast
  $sw = [Diagnostics.Stopwatch]::StartNew()
  $st = Get-Http -Url "$Base/api/state" -TimeoutSec 15
  $sw.Stop()
  $ms = [math]::Round($sw.ElapsedMilliseconds, 1)
  Check -Dim 'D5' -Name '/api/state under 2000 ms' -Ok ($st.Code -eq '200' -and $ms -lt 2000) -Detail ("{0} http={1} {2:N0}B" -f $ms, $st.Code, $st.Bytes)
  $hasSections = $false
  try { $j = $st.Body | ConvertFrom-Json; $hasSections = ($null -ne $j.sections) } catch { }
  Check -Dim 'D5' -Name '/api/state is real JSON with sections' -Ok $hasSections -Detail ''
  $age = -1
  try { $j = $st.Body | ConvertFrom-Json; $age = [math]::Round(((Get-Date) - [datetime]$j.generated).TotalSeconds, 1) } catch { }
  Check -Dim 'D5' -Name 'served state is fresh' -Ok ($age -ge 0 -and $age -lt 180) -Detail "age ${age}s"

  # D6 storage lockout - reading a file that a writer may be replacing
  $r1 = Get-Http -Url "$Base/api/state" -TimeoutSec 15
  $r2 = Get-Http -Url "$Base/api/state" -TimeoutSec 15
  $b1 = 0; $b2 = 0
  try { $null = $r1.Body | ConvertFrom-Json; $b1 = 1 } catch { }
  try { $null = $r2.Body | ConvertFrom-Json; $b2 = 1 } catch { }
  Check -Dim 'D6' -Name 'two back-to-back reads both parse' -Ok ($b1 -eq 1 -and $b2 -eq 1) -Detail ''

  # D7 buffer capacity - the FIFO bound must actually hold
  $lines = 0
  if (Test-Path -LiteralPath $HistF) { $lines = @(Get-Content -LiteralPath $HistF -Encoding UTF8 -ErrorAction SilentlyContinue).Count }
  Check -Dim 'D7' -Name 'history is bounded' -Ok ($lines -le 500) -Detail ("{0} lines, cap 400 + 50 slack" -f $lines)
  $unparsed = 0
  if (Test-Path -LiteralPath $HistF) {
    foreach ($l in (Get-Content -LiteralPath $HistF -Encoding UTF8 -ErrorAction SilentlyContinue)) {
      if ($l.Trim()) { try { $null = $l | ConvertFrom-Json } catch { $unparsed++ } }
    }
  }
  Check -Dim 'D7' -Name 'every history line parses' -Ok ($unparsed -eq 0) -Detail "$unparsed unparseable"

  # D8 cold start - the artefacts a fresh boot must have created
  Check -Dim 'D8' -Name 'state file exists' -Ok (Test-Path -LiteralPath $StateF) -Detail ''
  Check -Dim 'D8' -Name 'job directory exists' -Ok (Test-Path -LiteralPath $AskDir) -Detail ''

  # D4 system drift - machine-bound paths. A hardcoded C:\Users\<someone> is not a
  # portability nit; it is a SILENT failure, because on another machine the path
  # is simply absent and a missing directory reports as a count of zero. "This
  # machine has no skills" and "I looked in the wrong place" are different facts
  # wearing the same number. This check exists because the collector carried
  # eight such literals AFTER server.ps1 had already been made portable - a fix
  # with a second copy nobody looked for, which is postmortem #15 exactly.
  #
  # COMMENTS ARE STRIPPED FIRST. The first version of this check scanned the raw
  # text and failed on the comment explaining why hardcoded paths are forbidden -
  # which contained the very string it was looking for. A scanner that reads
  # prose describing a defect as an instance of that defect is not a weak check,
  # it is a wrong one, and it will be disabled by the first person it annoys.
  $stray = @()
  foreach ($f in @((Join-Path $CC 'api\server.ps1'), (Join-Path $CC 'api\collect-state.ps1'), (Join-Path $CC 'api\run-bounded.ps1'))) {
    if (Test-Path -LiteralPath $f) {
      $code = Get-CodeOnly -Path $f
      if ([regex]::IsMatch($code, 'C:\\Users\\[^\\''"]+')) { $stray += (Split-Path $f -Leaf) }
    }
  }
  Check -Dim 'D4' -Name 'no machine-bound paths in server or collector' -Ok ($stray.Count -eq 0) -Detail ("{0} file(s): {1}" -f $stray.Count, ($stray -join ', '))

  # A count of zero must be distinguishable from a root that was never there.
  $sk = $null
  try { $sk = ([System.IO.File]::ReadAllText($StateF, [Text.Encoding]::UTF8) | ConvertFrom-Json).sections.skills } catch { }
  $hasPresence = ($null -ne $sk) -and ($null -ne $sk.PSObject.Properties['mavis_present'])
  Check -Dim 'D4' -Name 'skill counts say whether the root existed' -Ok $hasPresence -Detail $(if ($hasPresence) { "mavis_present=$($sk.mavis_present) count=$($sk.mavis_count)" } else { 'no presence flag in state' })

  # The git calls are bounded, and a bounded call that timed out must SAY so.
  # Both of these branches were wrong on first write: the timeout notice was
  # itself a non-empty line and got reported as the HEAD COMMIT, and a status
  # call killed part way through reported its partial file list as the count.
  # A hung measurement that renders as data is worse than one that renders as
  # nothing, so the state must carry the distinction or the guard is worthless.
  $hu = $null
  try { $hu = ([System.IO.File]::ReadAllText($StateF, [Text.Encoding]::UTF8) | ConvertFrom-Json).sections.hermes_update } catch { }
  $huOk = ($null -ne $hu) -and ($null -ne $hu.PSObject.Properties['git_timed_out'])
  Check -Dim 'D4' -Name 'git reports whether it timed out' -Ok $huOk -Detail $(if ($huOk) { "head_timed_out=$($hu.head_timed_out) status_timed_out=$($hu.status_timed_out) count=$($hu.modified_count)" } else { 'no timeout flag in state' })
  $headIsData = ($null -eq $hu) -or ($null -eq $hu.head) -or ($hu.head -notmatch 'TIMED OUT')
  Check -Dim 'D4' -Name 'a timeout notice is never reported as the head commit' -Ok $headIsData -Detail "head=$($hu.head)"

  # Every external call in the collector is now bounded, and each one that can
  # time out says so. A bounded measurement that renders as a plain value when
  # it did not complete is worse than an unbounded one, because it looks
  # confident. Three of them: Docker, the compose check, and the mcode-tools
  # catalogue.
  $st8 = $null
  try { $st8 = [System.IO.File]::ReadAllText($StateF, [Text.Encoding]::UTF8) | ConvertFrom-Json } catch { }
  $dk = if ($st8) { $st8.sections.docker } else { $null }
  $mm = if ($st8) { $st8.sections.minimax } else { $null }
  $dockerFlagged = ($null -ne $dk) -and ($null -ne $dk.PSObject.Properties['timed_out'])
  Check -Dim 'D4' -Name 'docker reports whether it timed out' -Ok $dockerFlagged -Detail $(if ($dockerFlagged) { "timed_out=$($dk.timed_out) total=$($dk.total)" } else { 'no flag' })
  $notZeroLie = ($null -ne $dk) -and (($dk.timed_out -eq $true) -or ($null -ne $dk.total))
  Check -Dim 'D4' -Name 'a docker timeout never renders as "0 containers"' -Ok $notZeroLie -Detail "total=$($dk.total) timed_out=$($dk.timed_out)"
  $mmFlagged = ($null -ne $mm) -and ($null -ne $mm.PSObject.Properties['timed_out'])
  Check -Dim 'D4' -Name 'mcode-tools reports whether it timed out' -Ok $mmFlagged -Detail $(if ($mmFlagged) { "timed_out=$($mm.timed_out) cli_auth=$($mm.cli_auth)" } else { 'no flag' })

  # compose_valid must be a REAL answer, not a stale $LASTEXITCODE. It was True,
  # went False the moment the call was moved into a child process, and would
  # have stayed silently wrong if the before/after comparison had not been run.
  $composeOk = ($null -ne $dk) -and ($null -ne $dk.PSObject.Properties['compose_valid'])
  Check -Dim 'D4' -Name 'compose validity is reported' -Ok $composeOk -Detail "compose_present=$($dk.compose_present) compose_valid=$($dk.compose_valid) timed_out=$($dk.compose_timed_out)"

  # The watchdog's kill scope. This is not a style rule: on 2026-10-05 03:03 a
  # legitimate restart of 8900 also killed the unsupervised SENTINEL_PRIME server
  # on 8910, which nothing restarts, and it stayed dead. The filter was
  # `CommandLine -like '*server.ps1*'` - every server on the machine. A guard
  # here is worth more than a comment there, because the watchdog is the one
  # component whose bug takes out other people's processes by design.
  $wdPath = Join-Path $Root 'scripts\cc-watchdog.ps1'
  $wdCode = ''
  if (Test-Path -LiteralPath $wdPath) { $wdCode = Get-CodeOnly -Path $wdPath }
  $unscoped = $wdCode -match "CommandLine\s*-like\s*'\*server\\?\.ps1\*'"
  Check -Dim 'D4' -Name 'the watchdog does not kill every server.ps1 on the box' -Ok (-not $unscoped) -Detail $(if ($unscoped) { "unscoped wildcard present in $wdPath" } else { 'kill scope is the supervised server' })

  # Three separate places define what an action is: the page's button table, the
  # server's runnable whitelist, and the list the collector advertises. They
  # agree today. Nothing keeps them agreeing - and the failure is silent in the
  # worst direction: the page renders a button that the server answers with a
  # 400, so the console looks complete and one control is dead. Verified equal
  # (15 / 15 / 15) before this check existed; now it cannot drift.
  $pageSrc = [System.IO.File]::ReadAllText((Join-Path $CC 'index.html'), [Text.Encoding]::UTF8)
  $pageBlk = [regex]::Match($pageSrc, '(?s)const ACTIONS = \{(.*?)\r?\n\};')
  $pageIds = @(); if ($pageBlk.Success) { foreach ($m in [regex]::Matches($pageBlk.Groups[1].Value, '(?m)^\s{2}([a-z_]+)\s*:')) { $pageIds += $m.Groups[1].Value } }
  $srvIds = @(); foreach ($l in [System.IO.File]::ReadAllLines((Join-Path $CC 'api\server.ps1'), [Text.Encoding]::UTF8)) { if ($l -match "^\s*'([a-z_]+)'\s*=\s*") { $srvIds += $Matches[1] } }
  $colIds = @(); foreach ($l in [System.IO.File]::ReadAllLines((Join-Path $CC 'api\collect-state.ps1'), [Text.Encoding]::UTF8)) { if ($l -match "@\{ id = '([a-z_]+)'") { $colIds += $Matches[1] } }
  $orphanBtns = @($pageIds | Where-Object { $srvIds -notcontains $_ })
  $orphanRuns = @($srvIds | Where-Object { $pageIds -notcontains $_ })
  $orphanAds = @($colIds | Where-Object { $srvIds -notcontains $_ })
  Check -Dim 'D4' -Name 'every button has a runnable action behind it' -Ok ($orphanBtns.Count -eq 0) -Detail ("page={0} server={1} collector={2}; orphan buttons: {3}" -f $pageIds.Count, $srvIds.Count, $colIds.Count, $(if ($orphanBtns) { $orphanBtns -join ',' } else { 'none' }))
  Check -Dim 'D4' -Name 'no runnable action is unreachable from the page' -Ok ($orphanRuns.Count -eq 0) -Detail $(if ($orphanRuns) { $orphanRuns -join ',' } else { 'none' })
  Check -Dim 'D4' -Name 'nothing is advertised that the server cannot run' -Ok ($orphanAds.Count -eq 0) -Detail $(if ($orphanAds) { $orphanAds -join ',' } else { 'none' })

  # Icons. There are TWO tables - IC for svg() and TIC for tic() - and BOTH
  # functions silently fall back to a generic icon on a miss:
  #     ${IC[k] || IC.gauge}      ${TIC[k] || TIC.gauge}
  # So a typo does not error, does not blank, and does not show up in any fault
  # sweep. It just quietly renders the wrong picture. A "Model fleet" card
  # shipped with tic('sparkles') against a table that only defines 'sparkle',
  # and read as a gauge for several passes before this check looked.
  #
  # The two tables are NOT formatted alike: IC is one key per line, TIC is
  # several keys per line. A line-anchored regex reads IC perfectly and reads
  # only 15 of TIC's 54 - which manufactures 15 false misses and hides the
  # one real one. So the key scan is deliberately UNANCHORED, and the check
  # below re-proves that property on a synthetic table every run: a scanner
  # that cannot see a multi-key line must fail, not pass quietly.
  $pg = [System.IO.File]::ReadAllText((Join-Path $CC 'index.html'), [Text.Encoding]::UTF8)
  function Get-IconKeys([string]$src, [string]$name) {
    $blk = [regex]::Match($src, "(?s)const\s+$name\s*=\s*\{(.*?)\n\};").Groups[1].Value
    if (-not $blk) { return @() }
    return @([regex]::Matches($blk, '([a-zA-Z_0-9]+)\s*:') | ForEach-Object { $_.Groups[1].Value } | Sort-Object -Unique)
  }
  # A guard that has never been seen to fire has not been shown to work: prove
  # the scanner reads several keys off one line, which is the exact blind spot
  # that hid the real defect.
  $probe = "const P = {`n  a:'1', b:'2', c:'3',`n  d:'4'`n};"
  $probeKeys = @(Get-IconKeys $probe 'P')
  Check -Dim 'D4' -Name 'icon scanner reads a multi-key line (self-test)' -Ok ($probeKeys.Count -eq 4 -and $probeKeys -contains 'b' -and $probeKeys -contains 'd') -Detail ("saw {0} of 4: {1}" -f $probeKeys.Count, ($probeKeys -join ','))
  $icHave  = Get-IconKeys $pg 'IC'
  $ticHave = Get-IconKeys $pg 'TIC'
  $svgMiss = @([regex]::Matches($pg, "svg\('([a-zA-Z_0-9]+)'") | ForEach-Object { $_.Groups[1].Value } | Sort-Object -Unique | Where-Object { $icHave -notcontains $_ })
  $ticMiss = @([regex]::Matches($pg, "tic\('([a-zA-Z_0-9]+)'") | ForEach-Object { $_.Groups[1].Value } | Sort-Object -Unique | Where-Object { $ticHave -notcontains $_ })
  Check -Dim 'D4' -Name 'every svg() icon exists (no silent gauge fallback)' -Ok ($svgMiss.Count -eq 0) -Detail ("IC has {0}; missing: {1}" -f $icHave.Count, $(if ($svgMiss) { $svgMiss -join ',' } else { 'none' }))
  Check -Dim 'D4' -Name 'every tic() icon exists (no silent gauge fallback)' -Ok ($ticMiss.Count -eq 0) -Detail ("TIC has {0}; missing: {1}" -f $ticHave.Count, $(if ($ticMiss) { $ticMiss -join ',' } else { 'none' }))

  # BOTH anchors must serve the page that is actually on disk. The deployment
  # is anchored in two places - the PowerShell server on 8900 and the nginx
  # container on 8901 - and nothing forces the container to track the file. It
  # bind-mounts today, so it does; but a rebuild that COPYED the page in would
  # serve a stale copy forever while every other check stayed green. Nothing
  # else in this file can see that, because both anchors answer 200 either way.
  # Hash what each one RETURNS, not what it claims to serve.
  $anchorDetail = 'no anchor was reachable'
  $anchorOk = $true
  try {
    $diskHash = (Get-FileHash -LiteralPath (Join-Path $CC 'index.html') -Algorithm SHA256).Hash
    $t = [IO.Path]::GetTempFileName()
    $parts = @("disk $($diskHash.Substring(0,8))")
    foreach ($pair in @(@('8900', $Base), @('8901', 'http://127.0.0.1:8901'))) {
      $port = $pair[0]; $url = $pair[1]
      # AND, never OR, and never "last writer wins": a stale 8900 followed by a
      # good 8901 must still fail. Overwriting the verdict per iteration is how
      # a guard ends up green because the last thing it looked at was fine.
      try {
        $body = (Invoke-WebRequest -Uri "$url/" -UseBasicParsing -TimeoutSec 20).Content
        [IO.File]::WriteAllText($t, $body, (New-Object Text.UTF8Encoding $false))
        $h = (Get-FileHash -LiteralPath $t -Algorithm SHA256).Hash
        if ($h -eq $diskHash) { $parts += ":$port matches" } else { $parts += ":$port STALE($($h.Substring(0,8)))"; $anchorOk = $false }
      } catch { $parts += ":$port ERR"; $anchorOk = $false }
    }
    $anchorDetail = $parts -join ' | '
  } catch { $anchorOk = $false; $anchorDetail = 'probe failed: ' + $_.Exception.Message }
  Check -Dim 'D8' -Name 'both anchors serve the page on disk' -Ok $anchorOk -Detail $anchorDetail

  # supervisor
  $hf = Join-Path $CC 'api\cc-health.json'
  $supOk = $false; $supDetail = ''
  if (Test-Path -LiteralPath $hf) {
    try { $h = [System.IO.File]::ReadAllText($hf, [Text.Encoding]::UTF8) | ConvertFrom-Json; $supOk = [bool]$h.healthy; $supDetail = "healthy=$($h.healthy) page_ok=$($h.page_ok) restarts=$($h.restarts)" } catch { $supDetail = 'unparseable' }
  } else { $supDetail = 'no health file' }
  Check -Dim 'D8' -Name 'supervisor reports healthy' -Ok $supOk -Detail $supDetail
}

# ------------------------------------------------------------ fault injection --
# Every one of these is a thing a real client, a stale file, or a race can do.
# Each must produce a CLEAN reported failure. A hang, a 500, or a fabricated
# success is a fail - which is the whole point of injecting them.
function Invoke-Faults {
  # F1 unknown job id -> clean error, not a 500
  $r = Get-Http -Url "$Base/api/ask/000000000000"
  $clean = $false
  try { $j = $r.Body | ConvertFrom-Json; $clean = ($j.state -eq 'error') } catch { }
  Check -Dim 'FAULT' -Name 'unknown job id is a clean error' -Ok ($clean -and $r.Code -eq '200') -Detail ("http={0} body={1}" -f $r.Code, $r.Body.Substring(0, [Math]::Min(60, $r.Body.Length)))

  # F2 malformed id -> must not reach a handler and must not 200 with a lie
  $r = Get-Http -Url "$Base/api/ask/ZZZZ-not-hex"
  Check -Dim 'FAULT' -Name 'malformed job id does not 200' -Ok ($r.Code -ne '200') -Detail ("http={0}" -f $r.Code)

  # F3 malformed JSON body -> 400, not a 500 carrying a raw exception
  $b = New-Body '{not valid json'
  $r = Get-Http -Url "$Base/api/action" -Method POST -BodyFile $b -TimeoutSec 15
  Check -Dim 'FAULT' -Name 'malformed action body is 4xx' -Ok ($r.Code -match '^4') -Detail ("http={0}" -f $r.Code)
  # F4 unknown action id -> rejected, with the allowlist
  $b = New-Body '{"id":"definitely-not-an-action"}'
  $r = Get-Http -Url "$Base/api/action" -Method POST -BodyFile $b -TimeoutSec 15
  $allowed = 0
  try { $j = $r.Body | ConvertFrom-Json; $allowed = @($j.allowed).Count } catch { }
  Check -Dim 'FAULT' -Name 'unknown action rejected with allowlist' -Ok ($r.Code -eq '400' -and $allowed -gt 0) -Detail ("http={0} allowed={1}" -f $r.Code, $allowed)

  # F5 a job marker containing GARBAGE -> must not take the console down, and
  # must not be echoed back under a JSON content-type. 200 alone is too weak:
  # the first version of this check passed while the route served unparseable
  # bytes, so the poller reported "lost contact with the console" - a symptom
  # that describes the wrong thing. Assert the SHAPE, not just the status.
  $junk = Join-Path $AskDir 'aabbcceeddff.json'
  $probeJob = 'aabbcceeddff'
  [System.IO.File]::WriteAllText($junk, '{{{ this is not json at all', (New-Object Text.UTF8Encoding($false)))
  $r = Get-Http -Url "$Base/api/ask/$probeJob"
  $junkClean = $false
  try { $j = $r.Body | ConvertFrom-Json; $junkClean = ($j.state -eq 'error' -and $j.error -match 'unreadable') } catch { $junkClean = $false }
  Check -Dim 'FAULT' -Name 'corrupt job marker returns a clean error, not garbage' -Ok ($r.Code -eq '200' -and $junkClean) -Detail ("http={0} parsed={1}" -f $r.Code, $junkClean)
  $after = Get-Http -Url "$Base/api/state" -TimeoutSec 15
  Check -Dim 'FAULT' -Name 'server still serves state after corruption' -Ok ($after.Code -eq '200') -Detail ("http={0}" -f $after.Code)
  # Overwrite with inert content rather than deleting: this is a fixture.
  [System.IO.File]::WriteAllText($junk, '{"state":"done","answer":"harness fixture"}', (New-Object Text.UTF8Encoding($false)))

  # F5b the same corruption on the ACTION route - a second copy of the same
  # route shape is exactly where postmortem #15's bug lived, so the check is
  # written twice on purpose rather than assumed to be covered.
  $junkA = Join-Path $AskDir 'act-ffeeddccbbaa.json'
  [System.IO.File]::WriteAllText($junkA, 'not json either', (New-Object Text.UTF8Encoding($false)))
  $r = Get-Http -Url "$Base/api/action/ffeeddccbbaa"
  $junkAClean = $false
  try { $j = $r.Body | ConvertFrom-Json; $junkAClean = ($j.state -eq 'error' -and $j.error -match 'unreadable') } catch { $junkAClean = $false }
  Check -Dim 'FAULT' -Name 'corrupt action marker returns a clean error' -Ok ($r.Code -eq '200' -and $junkAClean) -Detail ("http={0} parsed={1}" -f $r.Code, $junkAClean)
  [System.IO.File]::WriteAllText($junkA, '{"state":"done","output":"harness fixture"}', (New-Object Text.UTF8Encoding($false)))

  # F6 a job marker that claims to be running but is older than any job
  $staleId = 'aabbccddee01'
  $sf = Join-Path $AskDir "$staleId.json"
  [System.IO.File]::WriteAllText($sf, '{"state":"running"}', (New-Object Text.UTF8Encoding($false)))
  (Get-Item -LiteralPath $sf).LastWriteTime = (Get-Date).AddHours(-2)
  $r = Get-Http -Url "$Base/api/ask/$staleId"
  $abandoned = $false
  try { $j = $r.Body | ConvertFrom-Json; $abandoned = ($j.state -eq 'error' -and $j.error -match 'abandoned') } catch { }
  Check -Dim 'FAULT' -Name 'stale running marker is reported abandoned' -Ok $abandoned -Detail $r.Body.Substring(0, [Math]::Min(70, $r.Body.Length))
  [System.IO.File]::WriteAllText($sf, '{"state":"done","answer":"harness fixture"}', (New-Object Text.UTF8Encoding($false)))

  # F7 the async contract itself: POST must return a JOB ID, not an answer
  $b = New-Body '{"question":"harness probe: how many hermes-mcp containers are running?"}'
  $sw = [Diagnostics.Stopwatch]::StartNew()
  $r = Get-Http -Url "$Base/api/ask" -Method POST -BodyFile $b -TimeoutSec 20
  $sw.Stop()
  $job = $null
  try { $j = $r.Body | ConvertFrom-Json; $job = $j.job } catch { }
  Check -Dim 'FAULT' -Name 'POST /api/ask returns a job id, not an answer' -Ok ([bool]$job -and $r.Code -eq '200') -Detail ("{0:N0}ms job={1}" -f $sw.ElapsedMilliseconds, $job)
  Check -Dim 'FAULT' -Name 'POST /api/ask is fast' -Ok ($sw.ElapsedMilliseconds -lt 3000) -Detail ("{0:N0}ms" -f $sw.ElapsedMilliseconds)
}

# ----------------------------------------------------------------------- main --
$fail = 0
$pass = 0
foreach ($c in $script:Results) { if ($c.Ok) { $pass++ } else { $fail++ } }
$script:Results.Clear()

if ($SelfTestScanner) {
  Write-Output '=== Get-CodeOnly unit test (code vs prose) ==='
  $ok = Invoke-ScannerSelfTest
  Write-Output ''
  if ($ok) { Write-Output 'SCANNER OK - correct in both directions.'; exit 0 }
  Write-Output 'SCANNER WRONG - the hardcoded-path guard cannot be trusted.'
  exit 1
}

if ($SelfCheck) {
  $ok = Invoke-SelfCheck
  $script:Results | Format-Table -AutoSize | Out-String | Write-Output
  if ($ok) { Write-Output 'SELF-CHECK PASS - the harness detects a deliberate fault.'; exit 0 }
  Write-Output 'SELF-CHECK FAIL - this harness cannot be trusted to certify anything.'
  exit 1
}

Write-Output '=== Control Center health harness ==='
Write-Output ("server   : {0}" -f $Base)
Write-Output ("required : {0} consecutive clean runs" -f $Runs)
Write-Output ''

if (-not (Invoke-SelfCheck)) {
  Write-Output 'ABORT: the harness failed its own self-check. No result it could produce would mean anything.'
  $script:Results | Format-Table -AutoSize | Out-String | Write-Output
  exit 1
}

$streak = 0
for ($i = 1; $i -le $Runs; $i++) {
  $script:Results.Clear()
  Invoke-Dimensions
  Invoke-Faults
  $f = @($script:Results | Where-Object { -not $_.Ok }).Count
  $p = $script:Results.Count - $f
  if ($f -eq 0) { $streak++ } else { $streak = 0 }
  Write-Output ("--- run {0}/{1}: {2} passed, {3} failed (streak {4})" -f $i, $Runs, $p, $f, $streak)
  if ($f -gt 0) {
    $script:Results | Where-Object { -not $_.Ok } | ForEach-Object { Write-Output ("    FAIL [{0}] {1} :: {2}" -f $_.Dim, $_.Name, $_.Detail) }
  }
}

Write-Output ''
$script:Results | Format-Table -AutoSize -Wrap | Out-String -Width 150 | Write-Output
$allOk = (@($script:Results | Where-Object { -not $_.Ok }).Count -eq 0)

# PERSIST THE VERDICT. "I ran it and it passed" leaves nothing behind, so the
# next reader has to re-run the whole thing to check a claim - and a run that
# was skipped is indistinguishable from a run that was never attempted. The
# report is the evidence.
# scripts\ is a CHILD of projects\, so ONE hop reaches projects\. Two hops
# overshoots into .minimax-agent and the report lands nowhere. (Same class of
# mistake as the google-layer path: assuming a sibling is a child.)
$projectsRoot = Split-Path -Parent $PSScriptRoot
$reportPath = Join-Path $projectsRoot '90_CONTROL_CENTER\api\health-report.json'
Write-Output ("report target: {0}" -f $reportPath)
try {
  # Built as plain strings on purpose. Serialising the result objects through
  # ConvertTo-Json threw "Argument types do not match" on real harness data even
  # though the identical operation succeeded in isolation - and a certificate
  # that can fail to write itself is not evidence. Each check becomes one line
  # of text, which cannot fail whatever is in a Detail field.
  # Escape what would break the JSON string. One check is literally named
  #  'a docker timeout never renders as "0 containers"' - quotes included - so
  # stripping pipes alone produced a file that was not valid JSON.
  $lines = New-Object System.Collections.Generic.List[string]
  $passedN = 0
  function Scrub([object]$v) {
    ([string]$v).Replace("`r", ' ').Replace("`n", ' ').Replace('|', '/').Replace('\', '/').Replace('"', "'")
  }
  foreach ($r in $script:Results.ToArray()) {
    if ($r.Ok) { $passedN++ }
    $lines.Add((Scrub $r.Dim) + '|' + (Scrub $r.Name) + '|' + ([bool]$r.Ok) + '|' + (Scrub $r.Detail))
  }
  $json = '{' +
    '"at":"' + (Get-Date).ToString('o') + '",' +
    '"server":"' + ([string]$Base).Replace('"', "'") + '",' +
    '"runs_required":' + [int]$Runs + ',' +
    '"best_streak":' + [int]$streak + ',' +
    '"total_checks":' + [int]$lines.Count + ',' +
    '"passed":' + [int]$passedN + ',' +
    '"failed":' + ([int]$lines.Count - [int]$passedN) + ',' +
    '"certified":' + ([bool]($streak -ge $Runs)).ToString().ToLower() + ',' +
    '"format":"dim|name|ok|detail (pipe-delimited, newline-free)",' +
    '"checks":[' + (($lines.ToArray() | ForEach-Object { '"' + $_ + '"' }) -join ',') + ']' +
    '}'
  [System.IO.File]::WriteAllText($reportPath, $json, (New-Object Text.UTF8Encoding $false))
  Write-Output ("report written: {0}  ({1} checks, certified={2})" -f $reportPath, $lines.Count, ($streak -ge $Runs))
} catch {
  Write-Output ("could not write the report: {0}  (at line {1})" -f `
    $_.Exception.Message, $_.InvocationInfo.ScriptLineNumber)
}

if ($streak -ge $Runs) {
  Write-Output ("CERTIFIED - {0} consecutive clean runs." -f $Runs)
  exit 0
}
Write-Output ("NOT CERTIFIED - best streak {0} of {1} required. The last run's failures are listed above." -f $streak, $Runs)
exit 1
