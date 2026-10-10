<#
.SYNOPSIS
  Rebuild C:\Users\apviz\docker-compose.yml from live container state.

.DESCRIPTION
  Recovery path for the 2026-10-02 incident where the compose file was deleted
  and 18 containers were left running as orphans.

  Everything written here is READ from `docker inspect`. Nothing is invented:
  images, restart policies, networks, entrypoints, commands, port bindings,
  binds, and named volumes all come from the running containers.

  Environment variables are DIFFED against each image's own defaults, so the
  file records what the operator actually set rather than a wall of image
  boilerplate. An env var that the image already provides is omitted.

  This script only WRITES the file. It never stops, recreates or removes a
  container. Review the output before running `docker compose up -d`.
#>
[CmdletBinding()]
param(
  [string]$Out = 'C:\Users\apviz\docker-compose.yml',
  [string]$Project = 'apviz',
  # Directory that legitimately owns the compose file. Services are matched on
  # the DIRECTORY of their config_files label, not on the filename, because
  # Antigravity_Ecosystem_Terminal's file is also called docker-compose.yml.
  [string]$ComposeDir = 'C:\Users\apviz'
)

$ErrorActionPreference = 'Stop'
Write-Host "reading live container state..." -ForegroundColor DarkGray

$ids = @(docker ps -q)
if ($ids.Count -eq 0) { throw 'no running containers to recover from' }
$all = docker inspect $ids | ConvertFrom-Json

# Only services defined by THIS compose file. A shared project name is not
# enough: Antigravity_Ecosystem_Terminal lives in project "apviz" but its
# config_files points at its own file under AI_Tools\, so matching on the
# filename suffix alone wrongly pulled it in.
$mine = $all | Where-Object {
  $l = $_.Config.Labels
  if ($l.'com.docker.compose.project' -ne $Project) { return $false }
  $cf = @($l.'com.docker.compose.project.config_files') -join ';'
  if (-not $cf) { return $false }
  ($cf -split ';') | Where-Object {
    (Split-Path $_ -Parent) -eq $ComposeDir
  } | Select-Object -First 1
}

if ($mine.Count -eq 0) {
  throw "no services matched project '$Project' with a compose file in '$ComposeDir'. Nothing written."
}
Write-Host "  $Project services recovered: $($mine.Count)" -ForegroundColor DarkGray

# cache image defaults for the env diff
$imgCache = @{}
function ImageEnv($img) {
  if (-not $imgCache.ContainsKey($img)) {
    try { $imgCache[$img] = @(docker image inspect $img --format '{{json .Config.Env}}' 2>$null | ConvertFrom-Json) }
    catch { $imgCache[$img] = @() }
  }
  $set = @{}
  foreach ($e in $imgCache[$img]) { if ($e) { $set[($e -split '=', 2)[0]] = $true } }
  return $set
}

$lines = [System.Collections.Generic.List[string]]::new()
$lines.Add('# ' + ('=' * 74))
$lines.Add("#  $Out")
$lines.Add('#')
$lines.Add('#  RECOVERED FROM LIVE CONTAINER STATE ' + (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'))
$lines.Add('#  This file was missing while its containers were still running.')
$lines.Add('#  Everything below was read from `docker inspect` - nothing invented.')
$lines.Add('#  Environment vars are diffed against each image own defaults.')
$lines.Add('#')
$lines.Add('#  REVIEW BEFORE `docker compose up -d`. Never use --remove-orphans on this')
$lines.Add('#  project: Antigravity_Ecosystem_Terminal shares the project name but is')
$lines.Add('#  defined by its own compose file and would be deleted.')
$lines.Add('# ' + ('=' * 74))
$lines.Add('')
$lines.Add("name: $Project")
$lines.Add('')
$lines.Add('services:')

$volumes = [System.Collections.Generic.List[string]]::new()
$seenVol = @{}

foreach ($c in ($mine | Sort-Object { $_.Config.Labels.'com.docker.compose.service' })) {
  $svc = $c.Config.Labels.'com.docker.compose.service'
  $lines.Add("  $svc`:")
  $lines.Add("    image: $($c.Config.Image)")
  $cn = $c.Name.TrimStart('/')
  if ($cn -ne $svc) { $lines.Add("    container_name: $cn") }
  if ($c.HostConfig.RestartPolicy.Name -and $c.HostConfig.RestartPolicy.Name -ne 'no') {
    $lines.Add("    restart: $($c.HostConfig.RestartPolicy.Name)")
  }
  if ($c.Config.Entrypoint) { $lines.Add("    entrypoint: " + (@($c.Config.Entrypoint) -join ' ')) }
  if ($c.Config.Cmd) { $lines.Add("    command: " + (@($c.Config.Cmd) -join ' ')) }

  $defs = ImageEnv $c.Config.Image
  $extra = @($c.Config.Env | Where-Object { -not $defs.ContainsKey(($_ -split '=', 2)[0]) })
  if ($extra.Count -gt 0) {
    $lines.Add('    environment:')
    foreach ($e in $extra) {
      $k, $v = $e -split '=', 2
      # Always single-quote. Windows paths contain backslashes, and a
      # double-quoted YAML scalar would read \U and \h as escape sequences
      # ("go-yaml load error ... unknown escape character"). Single-quoted
      # YAML does no escape processing; a literal quote is written twice.
      $lines.Add("      ${k}: '" + ($v -replace "'", "''") + "'")
    }
  }

  $pb = $c.HostConfig.PortBindings
  if ($pb -and $pb.PSObject.Properties.Count -gt 0) {
    $lines.Add('    ports:')
    foreach ($p in $pb.PSObject.Properties) {
      foreach ($b in @($p.Value)) {
        $hp = if ($b.HostIp -and $b.HostIp -ne '0.0.0.0') { "$($b.HostIp):$($b.HostPort)" } else { $b.HostPort }
        $lines.Add("      - `"$hp`:$($p.Name)`"")
      }
    }
  }

  if ($c.HostConfig.Binds -and $c.HostConfig.Binds.Count -gt 0) {
    $lines.Add('    volumes:')
    foreach ($b in $c.HostConfig.Binds) {
      $lines.Add("      - $b")
      if ($b -match '^([a-zA-Z0-9_.-]+):') {
        $v = $Matches[1]
        if ($v -like "$Project*" -and -not $seenVol.ContainsKey($v)) { $seenVol[$v] = $true; $volumes.Add($v) }
      }
    }
  }
  $lines.Add('')
}

$lines.Add('volumes:')
foreach ($v in $volumes) { $lines.Add("  $v`:") }

Set-Content -LiteralPath $Out -Value ($lines -join "`n") -Encoding UTF8
Write-Host "wrote $Out ($((Get-Item $Out).Length) bytes, $($mine.Count) services, $($volumes.Count) volumes)" -ForegroundColor Green
Write-Host "review it, then:  Set-Location C:\Users\apviz; docker compose config --quiet" -ForegroundColor Yellow
