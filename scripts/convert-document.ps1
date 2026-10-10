<#
.SYNOPSIS
  OPTIMUS document conversion bridge — host-side driver for the LibreOffice container.

.DESCRIPTION
  The libreoffice container is a LinuxServer Selkies web-desktop (VNC-in-browser on
  127.0.0.1:3001). It exposes NO REST API, so scripted conversion is driven by
  `docker exec libreoffice soffice --headless`.

  Flow: docker cp in -> soffice --convert-to -> docker cp out.

  A private -env:UserInstallation profile is used on every run. Without it,
  concurrent or repeated calls collide on the shared LibreOffice profile lock and
  the second call silently produces no output.

  VERIFIED CAPABILITY MATRIX (probed 2026-10-02, LibreOffice 25.8.7.3, isolated
  runs -- one fresh output dir per target, because a shared dir silently reports
  a stale leftover file as a success):

    txt -> pdf, docx, odt, html, txt, rtf, md     OK
    txt -> csv                                    FAIL (csv is a Calc format)
    pdf -> html                                   OK   (Draw export)
    pdf -> docx, odt, txt                         FAIL ("no export filter")

  A .pdf SOURCE is therefore only usable for an HTML export. For PDF -> Word use
  scripts\stirling-pdf.ps1 -Operation word. Everything else is driven by the
  normal attempt-and-report path below, which surfaces the raw soffice error.

.PARAMETER InputPath
  Source document on the Windows host.

.PARAMETER Format
  Target format. Defaults to pdf.

.PARAMETER OutputDir
  Where to place the converted file. Defaults to the input's directory.

.PARAMETER Container
  Container name. Defaults to libreoffice.

.PARAMETER AsJson
  Emit a single-line JSON object instead of a formatted object, for callers that
  parse the result (Mavis, cron, other scripts).

.EXAMPLE
  .\convert-document.ps1 -InputPath .\brief.docx -Format pdf
#>
[CmdletBinding()]
param(
  [Parameter(Mandatory = $true)][string]$InputPath,
  [ValidateSet('pdf', 'docx', 'xlsx', 'pptx', 'html', 'txt', 'csv', 'odt', 'ods', 'odp', 'rtf', 'md')]
  [string]$Format = 'pdf',
  [string]$OutputDir,
  [string]$Container = 'libreoffice',
  [switch]$AsJson
)

$ErrorActionPreference = 'Stop'

if (-not (Test-Path -LiteralPath $InputPath -PathType Leaf)) {
  throw "Input file not found: $InputPath"
}
$src = (Resolve-Path -LiteralPath $InputPath).Path

# Fail fast on the PDF-source combinations this build cannot do at all, instead
# of letting soffice fail later with an opaque "no export filter" message.
# Only 'html' is reachable from a PDF source.
$srcExt = ([System.IO.Path]::GetExtension($src)).ToLowerInvariant()
$pdfSourceBlocked = @('docx', 'xlsx', 'pptx', 'odt', 'ods', 'odp', 'rtf', 'txt', 'csv')
if ($srcExt -eq '.pdf' -and ($pdfSourceBlocked -contains $Format)) {
  $alt = if ($Format -in @('docx', 'odt', 'rtf', 'txt')) {
    " Use the Stirling-PDF bridge instead: .\stirling-pdf.ps1 -Operation word -InputPath '$src'"
  } else { '' }
  throw ("LibreOffice cannot convert a PDF source to '.$Format' (no such export " +
         "filter in this build). PDF -> html is supported.$alt")
}

if (-not $OutputDir) { $OutputDir = Split-Path -Parent $src }
if (-not (Test-Path -LiteralPath $OutputDir)) {
  New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
}
$outDirFull = (Resolve-Path -LiteralPath $OutputDir).Path

# Unique per-run name so parallel calls never collide in the container.
$base   = [System.IO.Path]::GetFileNameWithoutExtension($src)
$runId  = [guid]::NewGuid().ToString('N').Substring(0, 8)
$stem   = "${base}_${runId}"
$inName = "$stem$([System.IO.Path]::GetExtension($src))"
$outName = "$stem.$Format"

docker inspect $Container *> $null
if ($LASTEXITCODE -ne 0) { throw "Container '$Container' is not available." }

$work = "/tmp/optimus-doc-$runId"
docker exec $Container mkdir -p $work *> $null

try {
  docker cp $src "${Container}:$work/$inName" *> $null
  if ($LASTEXITCODE -ne 0) { throw "docker cp (upload) failed." }

  $log = docker exec $Container soffice --headless --norestore `
      "-env:UserInstallation=file://$work/profile" `
      --convert-to $Format --outdir $work "$work/$inName" 2>&1
  if ($LASTEXITCODE -ne 0) { throw "soffice exited $LASTEXITCODE`n$log" }

  docker exec $Container test -f "$work/$outName" *> $null
  if ($LASTEXITCODE -ne 0) {
    throw "Expected output '$outName' was not produced.`nsoffice said:`n$log"
  }

  $dest = Join-Path $outDirFull "$base.$Format"
  if (Test-Path -LiteralPath $dest) {
    # Never silently clobber an existing artifact.
    $dest = Join-Path $outDirFull "$base`_$runId.$Format"
  }
  docker cp "${Container}:$work/$outName" $dest *> $null
  if ($LASTEXITCODE -ne 0) { throw "docker cp (download) failed." }

  $len = (Get-Item -LiteralPath $dest).Length
  # Field names match scripts\stirling-pdf.ps1 so one parser handles both bridges:
  #   ok / source / output / format / bytes / via
  $result = [pscustomobject]@{
    ok        = $true
    source    = $src
    output    = $dest
    format    = $Format
    bytes     = $len
    via       = "docker exec $Container soffice --headless"
  }
  if ($AsJson) { $result | ConvertTo-Json -Compress } else { $result }
}
finally {
  docker exec $Container rm -rf $work *> $null
}
