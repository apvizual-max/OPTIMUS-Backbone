<#
.SYNOPSIS
  Repairs double-encoded (mojibake) UTF-8 in Markdown files. Targeted, not global.

.DESCRIPTION
  BUG I INTRODUCED. stamp-doc-status.ps1 read each file with
  `Get-Content -Raw` (ANSI for a BOM-less file in PowerShell 5.1) and wrote it
  back with `Set-Content -Encoding UTF8`, double-encoding every non-ASCII
  character.

  A GLOBAL re-decode is wrong for mixed files: it repairs the broken sequences
  but corrupts characters that were already correct. The timeline is exactly
  that case - it holds both real mojibake (the middle-dot separators from the
  original file) and correct em-dashes I appended later. Re-encoding the whole
  string turned the correct ones into U+FFFD.

  So this walks the string and repairs ONLY runs of characters in the
  Windows-1252 high range (U+0080..U+00FF) that decode to valid UTF-8. Correctly
  encoded characters (em dash U+2014, middle dot U+00B7) are left untouched.

  PURE ASCII ON PURPOSE: a BOM-less .ps1 is read as ANSI by PowerShell 5.1, so
  literal mojibake in this file would corrupt the repair tool itself.
#>
[CmdletBinding()]
param(
  [switch]$Apply,
  [string]$Root = 'C:\Users\apviz\.minimax-agent\projects',
  # Walk subfolders too. The first version only scanned the root, so mojibake
  # introduced into 40_REGISTRIES\, 70_CONNECTORS\ and 10_BRIDGES\ survived the
  # repair unnoticed.
  [switch]$Recurse
)

$ErrorActionPreference = 'Stop'
# Build the "possible mis-decoded byte" character class FROM cp1252 itself.
# Guessing the range is what broke the first detector: the sequence for an em
# dash is U+00E2, U+20AC, U+201D -- the euro and the curly quote are ABOVE
# U+00FF, so a [U+00A0-U+00FF] class silently missed every em dash.
$REPLACEMENT = [char]0xFFFD
$cp1252 = [Text.Encoding]::GetEncoding(1252)
$utf8 = [Text.Encoding]::UTF8

$hi = @()
for ($b = 0x80; $b -le 0xFF; $b++) {
  $ch = $cp1252.GetString([byte[]]$b)
  if ($ch.Length -eq 1) { $hi += [regex]::Escape($ch) }
}
$HI_CLASS = '[' + ($hi -join '') + ']'

# 2-3 characters from that set: exactly the shape a doubled encoding produces
# (1 original char -> 2 or 3 mis-decoded chars).
$RUN = [regex]($HI_CLASS + '{2,3}')

function Repair-Text([string]$s) {
  $sb = New-Object Text.StringBuilder
  $pos = 0
  foreach ($m in $RUN.Matches($s)) {
    if ($m.Index -gt $pos) { [void]$sb.Append($s.Substring($pos, $m.Index - $pos)) }
    $run = $m.Value
    $decoded = $utf8.GetString($cp1252.GetBytes($run))
    # Accept only if it is genuinely valid UTF-8 and is shorter (2-3 chars -> 1)
    if ($decoded -notmatch [regex]::Escape($REPLACEMENT) -and $decoded.Length -lt $run.Length) {
      [void]$sb.Append($decoded)
    } else {
      [void]$sb.Append($run)      # not a mojibake run; leave as-is
    }
    $pos = $m.Index + $run.Length
  }
  if ($pos -lt $s.Length) { [void]$sb.Append($s.Substring($pos)) }
  return $sb.ToString()
}

function Count-Mojibake([string]$s) {
  $n = 0
  foreach ($m in $RUN.Matches($s)) {
    $decoded = $utf8.GetString($cp1252.GetBytes($m.Value))
    if ($decoded -notmatch [regex]::Escape($REPLACEMENT) -and $decoded.Length -lt $m.Value.Length) { $n++ }
  }
  return $n
}

$rows = @()
$scan = Get-ChildItem $Root -Filter '*.md' -File -EA SilentlyContinue
if ($Recurse) {
  $scan = Get-ChildItem $Root -Filter '*.md' -File -Recurse -EA SilentlyContinue |
          Where-Object { $_.FullName -notmatch '\\(_links|external|node_modules|logs|scratch)\\' }
}
$scan | ForEach-Object {
  $f = $_
  $text = [IO.File]::ReadAllText($f.FullName, $utf8)
  $before = Count-Mojibake $text
  if ($before -eq 0) { return }
  $fixed = Repair-Text $text
  $after = Count-Mojibake $fixed
  $introducedFffd = ([regex]::Matches($fixed, [regex]::Escape($REPLACEMENT))).Count
  $ok = ($after -lt $before) -and ($introducedFffd -le ([regex]::Matches($text, [regex]::Escape($REPLACEMENT))).Count)
  $rows += [pscustomobject]@{
    File = $f.Name; Runs = $before; After = $after
    BytesBefore = $f.Length
    BytesAfter  = if ($ok) { $utf8.GetByteCount($fixed) } else { 0 }
    WouldFix = $ok
  }
  if ($ok -and $Apply) {
    [IO.File]::WriteAllText($f.FullName, $fixed, (New-Object Text.UTF8Encoding($false)))
  }
}

$rows | Format-Table -AutoSize
$bad = @($rows | Where-Object { -not $_.WouldFix })
Write-Host ""
if ($bad.Count -eq 0) {
  Write-Host ("All {0} file(s) with mojibake repair cleanly, none degraded." -f $rows.Count) -ForegroundColor Green
} else {
  Write-Host ("{0} file(s) NOT improved, left alone:" -f $bad.Count) -ForegroundColor Yellow
  $bad | ForEach-Object { Write-Host ("   {0}: {1} -> {2}" -f $_.File, $_.Runs, $_.After) -ForegroundColor Yellow }
}
if ($Apply) { Write-Host "APPLIED." -ForegroundColor Cyan }
else { Write-Host "Dry run. Re-run with -Apply." -ForegroundColor DarkGray }
