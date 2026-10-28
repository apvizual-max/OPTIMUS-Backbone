<#
.SYNOPSIS
  Self-test for the OPTIMUS Control Center front end.

.DESCRIPTION
  Exists because of two real failures. A stray apostrophe inside a single-quoted
  string, and an unclosed parenthesis in a ternary arm, each killed the entire
  <script> block. In BOTH cases the page still rendered its static skeleton, the
  HTTP response was 200, and the console reported ZERO errors - because no
  statement ever ran to throw.

  That is the trap: a diagnostic that only fires after code starts running cannot
  detect code that never started. So this test asserts EFFECTS, not the absence
  of symptoms:

    1. the inline script is syntactically valid          (node --check)
    2. no mojibake has crept back in                    (encoding regression)
    3. the referenced icon subset and font are on disk   (offline stand-alone)
    4. the live /api/state is valid JSON                 (not a bare boolean)
    5. the supervisor is reporting                       (self-awareness)

  It does NOT drive a browser. Run cc selftest for the DOM-level checks, which
  need a real page load.

.EXAMPLE
  .\verify-ui.ps1
#>
$ErrorActionPreference = 'Continue'
$root = 'C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard'
$cc   = Join-Path $root '90_CONTROL_CENTER'
$page = Join-Path $cc 'index.html'
$pass = 0; $fail = 0

function Check([string]$name, [bool]$ok, [string]$detail) {
  if ($ok) { $script:pass++; Write-Host ("  PASS  {0,-42} {1}" -f $name, $detail) -ForegroundColor Green }
  else     { $script:fail++; Write-Host ("  FAIL  {0,-42} {1}" -f $name, $detail) -ForegroundColor Red }
}

Write-Host '=== CONTROL CENTER SELF-TEST ===' -ForegroundColor Cyan

# 1 — inline script must parse
$html = [IO.File]::ReadAllText($page, [Text.Encoding]::UTF8)
$blocks = [regex]::Matches($html, '(?s)<script>(.*?)</script>')
$js = $null
foreach ($b in $blocks) { if ($b.Groups[1].Value.Trim().Length -gt 500) { $js = $b.Groups[1].Value } }
if ($js) {
  $tmp = Join-Path $env:TEMP 'cc-selftest.js'
  [IO.File]::WriteAllText($tmp, $js, (New-Object Text.UTF8Encoding($false)))
  $out = & node --check $tmp 2>&1 | Out-String
  $nodeExit = $LASTEXITCODE
  $msg = if ($nodeExit -eq 0) { '{0:N0} chars parse clean' -f $js.Length }
         else { ($out -split "`n" | Where-Object { $_ -match 'Error' } | Select-Object -First 1) }
  Check 'inline script parses' ($nodeExit -eq 0) $msg
} else {
  Check 'inline script present' $false 'no <script> block over 500 chars'
}

# 2 — encoding regression.
# The detector is built from CODE POINTS, never from literal mojibake characters.
# Writing those characters into this file re-encodes them on the way in, which is
# precisely the bug being tested for - the first version of this very check
# shipped broken in exactly the way it was meant to catch. Codepoints cannot be
# mangled by an editor or by PowerShell's default encoding.
$mojiPattern = '[' + ([string][char]0x00E2) + ([string][char]0x00C2) + ([string][char]0x00C3) +
                ([string][char]0x00EF) + ([string][char]0x00FE) + ([string][char]0x00F0) + ']'
$moji = ([regex]::Matches($html, $mojiPattern)).Count
Check 'no mojibake' ($moji -eq 0) "$moji suspect character(s)"

# 3 — stand-alone assets
$cssOk = Test-Path (Join-Path $cc 'assets\tabler-icons.css')
$woffOk = Test-Path (Join-Path $cc 'assets\tabler-icons.woff2')
$cdn = ([regex]::Matches($html, 'https?://(?!127\.0\.0\.1)')).Count
Check 'local icon font on disk' ($cssOk -and $woffOk) "css=$cssOk woff2=$woffOk"
Check 'no external resources' ($cdn -eq 0) "$cdn external URL(s) in the page"

# 4 — the live API must return JSON, never a bare boolean
try {
  $r = Invoke-WebRequest -Uri 'http://127.0.0.1:8900/api/state' -UseBasicParsing -TimeoutSec 60
  $j = $r.Content | ConvertFrom-Json
  $age = [math]::Round(((Get-Date) - [datetime]$j.generated).TotalSeconds, 0)
  $hasSections = $null -ne $j.sections
  Check '/api/state returns real JSON' ($hasSections) ("{0:N0} bytes, sections present" -f $r.Content.Length)
  Check 'state is fresh' ($age -lt 120) "age ${age}s"
} catch {
  Check '/api/state answers' $false $_.Exception.Message
}

# 5 — supervision
try {
  $h = (Invoke-WebRequest -Uri 'http://127.0.0.1:8900/api/health' -UseBasicParsing -TimeoutSec 20).Content | ConvertFrom-Json
  Check 'supervisor present' ([bool]$h.supervised) ("healthy={0} restarts={1}" -f $h.supervisor.healthy, $h.supervisor.restarts)
} catch {
  Check 'supervisor present' $false $_.Exception.Message
}

Write-Host ''
if ($fail -eq 0) {
  Write-Host ("SELF-TEST PASS  ({0}/{0})" -f $pass) -ForegroundColor Green
  exit 0
} else {
  Write-Host ("SELF-TEST FAIL  ({0} pass, {1} fail)" -f $pass, $fail) -ForegroundColor Red
  exit 1
}
