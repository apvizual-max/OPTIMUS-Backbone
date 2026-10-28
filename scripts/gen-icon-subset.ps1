<#
.SYNOPSIS
  Regenerate the LOCAL Tabler icon subset from what index.html actually uses.

.DESCRIPTION
  The console ships its own woff2 and a generated CSS subset, because a remote
  webfont means every glyph becomes a blank box the moment the machine is
  offline - and a blank box is indistinguishable from a design choice.

  The subset must therefore be regenerated whenever an icon is added. The front
  end self-test on the Fabric tab checks for blank glyphs and fails loudly, which
  is how a missing player-play was caught.

  Two things this script must get right, both of which bit me:
    1. tic('play') passes an ALIAS. The real Tabler name is the TIC map's VALUE
       for that key. Resolving aliases wrongly is how six icons silently vanish.
    2. A name is only added if its codepoint is found upstream. A name that does
       not resolve is REPORTED, never written as a dead rule.

.EXAMPLE
  .\gen-icon-subset.ps1
#>
$ErrorActionPreference = 'Stop'
$root    = 'C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard'
$cc      = Join-Path $root '90_CONTROL_CENTER'
$page    = Join-Path $cc 'index.html'
$cssOut  = Join-Path $cc 'assets\tabler-icons.css'
$UPSTREAM= 'https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@3.48.0/dist/tabler-icons.min.css'

$html = [IO.File]::ReadAllText($page, [Text.Encoding]::UTF8)
# Search the RAW html, not a comment-stripped copy. The stripper is a non-greedy
# /\* ... \*/ and something earlier in the file opens a block comment inside a
# string or a path, so the stripper swallows everything up to the next */ -
# including the entire TIC map. The result: zero aliases resolved, every
# tic('alias') fell through as the alias, and seven icons came out missing.
# The TIC map contains nothing that needs stripping, so it is read directly.
$noComment = $html

$alias = @{}
# 1. alias -> real name, taken from the TIC map's VALUES.
#    The terminator must NOT require a newline before "};". The first version
#    used \r?\n\}; and matched nothing, so every tic('alias') fell through as the
#    alias itself and seven icons came out unresolved. A regex that quietly
#    matches nothing is the same failure as a check that quietly passes.
$m = [regex]::Match($noComment, 'const\s+TIC\s*=\s*\{([\s\S]*?)\};')
if ($m.Success) {
  # The TIC map keys are UNQUOTED JavaScript object keys: gauge:'gauge'.
  # Demanding quotes on the key side matched the block and then found zero
  # entries inside it, which is worse than not matching at all. Double-quoted
  # here so the inner single quotes around the VALUE stay literal.
  [regex]::Matches($m.Groups[1].Value, "([a-z0-9-]+)\s*:\s*'([a-z0-9-]+)'") |
    ForEach-Object { $alias[$_.Groups[1].Value] = $_.Groups[2].Value }
} else { Write-Host '  WARNING: the TIC map was not found - aliases cannot be resolved' -ForegroundColor Red }
Write-Host ("TIC aliases resolved : {0}" -f $alias.Count)

# 2. every real name the page can emit
$used = New-Object System.Collections.Generic.List[string]
[regex]::Matches($noComment, "tic\('([a-z0-9-]+)'") | ForEach-Object {
  $a = $_.Groups[1].Value
  if ($alias.ContainsKey($a)) { [void]$used.Add($alias[$a]) } else { [void]$used.Add($a) }
}
[regex]::Matches($noComment, 'class="ti ti-([a-z0-9-]+)') | ForEach-Object { [void]$used.Add($_.Groups[1].Value) }
$alias.Values | ForEach-Object { [void]$used.Add($_) }
$uniq = @($used | Sort-Object -Unique)
Write-Host ("distinct real names   : {0}" -f $uniq.Count)

# 3. resolve each against upstream
$up = (Invoke-WebRequest -Uri $UPSTREAM -UseBasicParsing -TimeoutSec 60).Content
$rules = New-Object System.Collections.Generic.List[string]
$unresolved = @()
foreach ($n in $uniq) {
  $mm = [regex]::Match($up, '\.ti-' + [regex]::Escape($n) + ':before\{content:"\\([0-9a-fA-F]+)"\}')
  if ($mm.Success) { $rules.Add(('.ti-{0}:before{{content:"\{1}"}}' -f $n, $mm.Groups[1].Value)) }
  else { $unresolved += $n }
}
Write-Host ("resolved to codepoints: {0}" -f $rules.Count)
if ($unresolved.Count) { Write-Host ("  NOT IN THE UPSTREAM SET: " + ($unresolved -join ', ')) -ForegroundColor Yellow }

$head = @(
'/* Tabler Icons 3.48.0 (MIT, https://tabler.io) - LOCAL SUBSET, GENERATED',
'',
'   Served from /assets so this console needs NO NETWORK. Loaded remotely, every',
'   glyph becomes a blank box the moment the machine is offline, and a blank box',
'   is indistinguishable from a deliberate design choice.',
'',
'   Regenerate with scripts\gen-icon-subset.ps1 after adding an icon. The',
'   front-end self-test on the Fabric tab fails loudly on any blank glyph.',
'*/',
'@font-face{font-family:"tabler-icons";font-style:normal;font-weight:400;',
'  src:url("tabler-icons.woff2") format("woff2");font-display:swap}',
'.ti{font-family:"tabler-icons" !important;speak:none;font-style:normal;font-weight:normal;',
'  font-variant:normal;text-transform:none;line-height:1;-webkit-font-smoothing:antialiased}'
)
[IO.File]::WriteAllLines($cssOut, ($head + $rules), (New-Object Text.UTF8Encoding($false)))
Write-Host ("wrote {0} ({1} rules, {2:N0} bytes)" -f $cssOut, $rules.Count, (Get-Item $cssOut).Length)

if ($unresolved.Count) { exit 1 } else { exit 0 }
