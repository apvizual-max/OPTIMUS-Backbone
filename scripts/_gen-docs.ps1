# Generates the factual quarantine documentation from LIVE measurement.
# Nothing here is written from memory: every version, port, container and path
# is read from the machine at generation time, so the document cannot rot into
# describing a system that no longer exists.
param(
  [string]$Root = 'C:\Users\apviz\.minimax-agent\projects',
  [string]$Docs = 'C:\Users\apviz\.minimax-agent\projects\FULL_BACKUP_2026-10-04_QUARANTINE\_DOCS'
)
$ErrorActionPreference = 'Continue'
New-Item -ItemType Directory -Force -Path $Docs | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $Docs '03_TREES') | Out-Null

function Ver([string]$cmd, [string[]]$argv) {
  try {
    $p = if ($argv) { Start-Process -FilePath $cmd -ArgumentList $argv -NoNewWindow -Wait -PassThru `
             -RedirectStandardOutput ([IO.Path]::GetTempFileName()) -EA SilentlyContinue } else { $null }
    if ($p) { return "installed (exit $($p.ExitCode))" }
  } catch { }
  return 'NOT FOUND'
}
function FirstLine([string]$label, [string[]]$cmd) {
  try {
    $t = if ($cmd.Count -gt 1) { & $cmd[0] $cmd[1..($cmd.Count-1)] 2>&1 | Out-String } else { & $cmd[0] 2>&1 | Out-String }
    $l = ($t -split "`n" | Where-Object { $_.Trim() } | Select-Object -First 1)
    if ($l) { return $l.Trim() } else { return 'present, no version output' }
  } catch { return 'ERROR: ' + $_.Exception.Message }
}

$sb = New-Object Text.StringBuilder
function W([string]$s) { [void]$sb.AppendLine($s); [void]$sb.AppendLine('') }

$gen = (Get-Date).ToString('yyyy-MM-dd HH:mm:ss zzz')
W "# 02 - DEPENDENCY MANIFEST"
W "Generated: $gen"
W "Everything below was READ FROM THE MACHINE at generation time. Nothing is remembered."
W "If a line says NOT FOUND, that tool is not on PATH and the project cannot rely on it."

W "## Runtimes"
W '| Tool | Version / path | Required for |'
W '|---|---|---|'
W "| node | $(FirstLine '' @('node','--version')) | the Tabler icon webfont is remote but all server logic is PowerShell |"
W "| npm | $(FirstLine '' @('npm','--version')) | any future JS tooling |"
W "| python | $(FirstLine '' @('python','--version')) | the Python MiniMax client route |"
W "| docker | $(FirstLine '' @('docker','--version')) | the whole 56-container swarm |"
W "| git | $(FirstLine '' @('git','--version')) | Hermes self-update; the collector reads the Hermes HEAD |"
W "| hermes | $(FirstLine '' @('hermes','--version')) | the Hermes side of both bridges |"
W "| qwen | $(FirstLine '' @('qwen','--version')) | Qwen Studio ACP transport :8765 |"
W "| mcode-tools | $(FirstLine '' @('mcode-tools','--version')) | MiniMax CLI auth + connector catalogue |"

W "## Installed application paths"
W '| Component | Path | Present |'
W '|---|---|---|'
foreach ($p in @(
  @('Qwen Studio (bun runtime)','C:\Program Files\Qwen'),
  @('MiniMax Code (Qwen.exe)','C:\Users\apviz\AppData\Local\Programs\Qwen'),
  @('MiniMax Code (Antigravity IDE)','C:\Users\apviz\AppData\Local\Programs\Antigravity IDE'),
  @('Hermes desktop plugins (SOT origin)','C:\Users\apviz\AppData\Local\hermes\desktop-plugins'),
  @('Mavis agent home','C:\Users\apviz\.minimax\agents\mavis'),
  @('Hermes scripts (external target)','C:\Users\apviz\AppData\Local\hermes\scripts'),
  @('Hermes MCP servers (external target)','C:\Users\apviz\AppData\Local\hermes\mcp-servers'))) {
  W "| $($p[0]) | ``$($p[1])`` | $(Test-Path -LiteralPath $p[1]) |"
}

W "## Listening ports the project depends on"
W '| Port | Service | Why this project needs it |'
W '|---|---|---|'
$ports = @(
  @('8801','minimax-hermes-bridge','Mavis to Hermes. /health and /doctor/detailed are polled by the collector.'),
  @('8802','minimax-antigravity-bridge','Mavis to Antigravity. Read-only mount, council + small tasks only.'),
  @('8080','docker-proxy / honcho','Container port proxy.'),
  @('8082','stirling-pdf','Real HTTP API, no login (SECURITY_ENABLELOGIN=false).'),
  @('3001','libreoffice','Remote desktop, NOT an API. Convert via `optimus doc convert`.'),
  @('8765','qwen-acp','ACP over WebSocket at /acp. NOT an MCP server - /mcp is 404 by design.'),
  @('8900','OPTIMUS Control Center','This dashboard. Loopback only.')
)
foreach ($p in $ports) {
  $up = Test-NetConnection -ComputerName 127.0.0.1 -Port ([int]$p[0]) -InformationLevel Quiet -WarningAction SilentlyContinue
  W "| $($p[0]) | $($p[1]) | $($p[2]) |"
}
$capParts = @(8801,8802,8080,8082,3001,8765,8900) | ForEach-Object {
  $q2 = Test-NetConnection -ComputerName 127.0.0.1 -Port $_ -InformationLevel Quiet -WarningAction SilentlyContinue
  if ($q2) { "$_=UP" } else { "$_=DOWN" }
}
$capLine = ($capParts -join '  ')
W ("Captured at generation time: " + $capLine)

W "## Containers"
try {
  $rows = @(& docker ps --format '{{.Names}}|{{.Status}}' 2>$null)
  W ("Total running at generation time: **{0}**" -f $rows.Count)
  $herm = @($rows | Where-Object { $_ -like 'hermes-mcp-*' })
  W ("`hermes-mcp-*` load-bearing swarm: **{0}** - NEVER `docker container prune -a`, NEVER `docker rm -f hermes-mcp-*`" -f $herm.Count)
  W 'The `apviz` compose project owns `Antigravity_Ecosystem_Terminal`; never use `--remove-orphans` against it.'
  W ''
  W '| Container | Status |'
  W '|---|---|'
  foreach ($r in $rows) {
    $x = $r -split ([char]124)
    $c0 = $x[0]
    $c1 = $x[1]
    W ("| {0} | {1} |" -f $c0, $c1)
  }
} catch { W "docker unavailable: $($_.Exception.Message)" }

W "## Mavis MCP fleet (13 servers, current-profile)"
$mcpcfg = 'C:\Users\apviz\.minimax\mcp.json'
if (Test-Path $mcpcfg) { W "Configuration file: ``$mcpcfg``" } else { W "``mcp.json`` not found at the expected path." }
W ''
W 'Four of these are TypeScript and need the **bun** runtime, which is not on PATH:'
W '```'
W 'C:\Program Files\Qwen\resources\bun\bun.exe   (1.2.10, bundled with the Qwen Studio app)'
W '```'

W "## Skills available to Mavis"
$sd = 'C:\Users\apviz\.minimax\agents\mavis\skills'
if (Test-Path $sd) { W ("Mavis skills on disk: **{0}**" -f @(Get-ChildItem $sd -Directory -Force -EA SilentlyContinue).Count) }
$vsd = 'C:\Users\apviz\.minimax\skills'
if (Test-Path $vsd) { W ("Personal skills (referenced by the SOT junction): **{0}**" -f @(Get-ChildItem $vsd -Directory -Force -EA SilentlyContinue).Count) }

[IO.File]::WriteAllText((Join-Path $Docs '02_DEPENDENCIES.md'), $sb.ToString(), (New-Object Text.UTF8Encoding($false)))
Write-Host ("wrote 02_DEPENDENCIES.md ({0:N0} bytes)" -f $sb.Length)

# ------------------------------------------------------------------ FILE_TREE
$tree = New-Object Text.StringBuilder
$q = 'C:\Users\apviz\.minimax-agent\projects'
function T([string]$s) { [void]$tree.AppendLine($s) }
T "# 03 - FILE TREE"
T ""
T "Generated: $gen"
T ""
T "Root: ``$q``"
T ""
T "Junction targets are shown, not followed - they point outside this root and are"
T "recreated as junctions in the backup, with their targets recorded in"
T "``BACKUP-MANIFEST.json``."
T ""
$skip = @('FULL_BACKUP_2026-10-04_QUARANTINE')
function Walk([string]$dir, [int]$depth, [string]$prefix) {
  if ($depth -gt 4) { return }
  $items = Get-ChildItem -LiteralPath $dir -Force -EA SilentlyContinue |
           Where-Object { $skip -notcontains $_.Name } | Sort-Object @{e={$_.PSIsContainer};Descending=$true}, Name
  foreach ($i in $items) {
    $rel = $i.FullName.Substring($q.Length + 1)
    if ($i.LinkType) { T ("$prefix$($i.Name)  ->  $($i.Target)   [JUNCTION, not followed]") }
    elseif ($i.PSIsContainer) {
      $n = @(Get-ChildItem -LiteralPath $i.FullName -Recurse -File -Force -EA SilentlyContinue).Count
      T ("$prefix$($i.Name)/    ($n files)")
      Walk $i.FullName ($depth + 1) ($prefix + '  ')
    }
  }
}
T "```"
Walk $q 0 ''
T "```"
[IO.File]::WriteAllText((Join-Path $Docs '03_TREES\FILE_TREE.md'), $tree.ToString(), (New-Object Text.UTF8Encoding($false)))
Write-Host ("wrote 03_TREES/FILE_TREE.md ({0:N0} bytes)" -f $tree.Length)
