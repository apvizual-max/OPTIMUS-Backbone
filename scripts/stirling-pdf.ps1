<#
.SYNOPSIS
  OPTIMUS Stirling-PDF bridge — host-side HTTP client for the stirling-pdf container.

.DESCRIPTION
  Stirling-PDF (v2.14.3) is a Spring Boot app on 127.0.0.1:8082. Its API is
  POST-only multipart under /api/v1/... . Auth is DISABLED via
  SECURITY_ENABLELOGIN=false (see C:\Users\apviz\docker-compose.yml).

  Careful: the Angular SPA serves index.html for unknown paths, so a 200 on an
  invented path means nothing. A real route answers 415 when the body is not
  multipart, 404 when the route does not exist, and 401 if login came back on.
  This script validates the magic bytes of the response so an HTML page is never
  mistaken for a converted PDF.

.PARAMETER Operation
  Supported: pdfa | img | word | merge

.PARAMETER InputPath
  One file (pdfa/img/word) or two+ files (merge).

.PARAMETER OutputPath
  Destination for the result. Defaults to the input name with a new extension.

.PARAMETER Dpi
  Resolution for the `img` operation. REQUIRED by Stirling-PDF: without it the
  endpoint dereferences a null getDpi() and answers HTTP 500 with
  "Cannot invoke Integer.intValue() ... getDpi() is null". Ignored by the
  other operations.

.PARAMETER AsJson
  Emit a single-line JSON object instead of a formatted object.

.EXAMPLE
  .\stirling-pdf.ps1 -Operation pdfa -InputPath .\in.pdf
#>
[CmdletBinding()]
param(
  [Parameter(Mandatory = $true)]
  [ValidateSet('pdfa', 'img', 'word', 'merge')]
  [string]$Operation,

  [Parameter(Mandatory = $true)][string[]]$InputPath,

  [string]$OutputPath,
  [string]$BaseUrl = 'http://127.0.0.1:8082',
  [ValidateRange(50, 1200)][int]$Dpi = 150,
  [int]$TimeoutSec = 180,
  [switch]$AsJson
)

$ErrorActionPreference = 'Stop'

$files = @()
foreach ($p in $InputPath) {
  if (-not (Test-Path -LiteralPath $p -PathType Leaf)) { throw "Input not found: $p" }
  $files += (Resolve-Path -LiteralPath $p).Path
}
if ($Operation -eq 'merge' -and $files.Count -lt 2) {
  throw "Operation 'merge' needs at least 2 input files."
}

$endpoint = switch ($Operation) {
  'pdfa'  { '/api/v1/convert/pdf/pdfa' }
  'img'   { '/api/v1/convert/pdf/img' }
  'word'  { '/api/v1/convert/pdf/word' }
  'merge' { '/api/v1/general/merge-pdfs' }
}

if (-not $OutputPath) {
  $stem = [System.IO.Path]::GetFileNameWithoutExtension($files[0])
  switch ($Operation) {
    'pdfa'  { $ext = '.pdf' }
    'img'   { $ext = '.zip' }
    'word'  { $ext = '.docx' }
    'merge' { $ext = '.pdf' }
  }
  $OutputPath = Join-Path (Split-Path -Parent $files[0]) "$stem$ext"
}

$curl = (Get-Command curl.exe -ErrorAction SilentlyContinue).Source
if (-not $curl) { throw 'curl.exe not found on PATH.' }

$argsList = @('-sS', '--max-time', "$TimeoutSec", '-o', $OutputPath,
              '-w', '%{http_code}', '-X', 'POST')
foreach ($f in $files) { $argsList += @('-F', "fileInput=@$f") }

switch ($Operation) {
  'pdfa'  { $argsList += @('-F', 'colorType=color', '-F', 'outputType=pdfa-2b') }
  'img'   { $argsList += @('-F', 'imageFormat=png', '-F', 'singleOrMultiple=zip', '-F', "dpi=$Dpi") }
  'word'  { $argsList += @('-F', 'outputFormat=docx') }
  'merge' { }
}
$argsList += "$BaseUrl$endpoint"

$code = (& $curl @argsList 2>&1 | Select-Object -Last 1)

if ($code -eq '401') {
  throw ('Stirling-PDF returned 401: login is enabled again. Check that ' +
         'SECURITY_ENABLELOGIN=false is still set on the container.')
}
if ($code -ne '200') {
  $body = if (Test-Path -LiteralPath $OutputPath) {
    (Get-Content -LiteralPath $OutputPath -Raw -ErrorAction SilentlyContinue)
  } else { '' }
  throw "Stirling-PDF $Operation failed: HTTP $code`n$($body.Substring(0, [Math]::Min(400, $body.Length)))"
}

# Reject the SPA catch-all: a real artefact never starts with '<!doctype'.
$head = [System.IO.File]::ReadAllBytes($OutputPath) | Select-Object -First 8
$magic = [System.Text.Encoding]::ASCII.GetString([byte[]]$head).Trim()
if ($magic.StartsWith('<')) {
  throw "Stirling-PDF returned HTML, not a document (route or login wall)."
}

$len = (Get-Item -LiteralPath $OutputPath).Length
$result = [pscustomobject]@{
  ok        = $true
  operation = $Operation
  endpoint  = "$BaseUrl$endpoint"
  inputs    = $files
  output    = (Resolve-Path -LiteralPath $OutputPath).Path
  bytes     = $len
  magic     = $magic
}
if ($AsJson) { $result | ConvertTo-Json -Compress } else { $result }
