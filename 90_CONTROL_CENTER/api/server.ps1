<#
.SYNOPSIS
  Local server for the MiniMax OPTIMUS Control Center.

.DESCRIPTION
  A file:// HTML page cannot execute PowerShell, so "live daemon monitoring"
  and "clickable command buttons" both require a local HTTP origin. This
  server provides it and is deliberately small.

  Routes
    GET  /                        -> index.html
    GET  /api/state               -> live state JSON, READ-ONLY: the file the
                                     background refresher wrote, never a fresh
                                     measurement. See Get-StateJson's contract.
    POST /api/ask                 -> start an analyst job, return its id in ms
    GET  /api/ask/<id>            -> that job's result (running / done / error)
    GET  /api/journal             -> bridge journal, bounded at 15s
    POST /api/action              -> start a whitelisted action, return its id
    GET  /api/action/<id>         -> that job's output (running / done / error)
    GET  /api/health              -> server self-check

  The single listener thread is the system's scarcest resource, so the request
  paths are read-only and the slow ones are background JOBS that return an id.
  See Start-AskJob and Start-ActionJob; a route that can start a measurement or
  wait on a subprocess is a freeze for everyone behind it, not just the caller.

  Two paths can still occupy the listener, and both are BOUNDED rather than
  removed, which is a deliberate trade rather than an oversight:
    - /api/journal runs a bounded docker exec inline (15 s ceiling). Nothing in
      the page calls it; the Journal tab reads the cache.
    - Get-StateJson falls through to a collect only when live-state.json is
      MISSING. The startup pre-warm writes it before the browser opens, so this
      is the bootstrap path, not a recurring one.

  SECURITY
    - Binds 127.0.0.1 only. Never reachable off-box.
    - Actions are resolved from a WHITELIST keyed by id, taken from
      collect-state.ps1. The HTTP body supplies only an id, never a command,
      so a crafted request cannot execute arbitrary shell.
    - Action output is size-capped, and every action has a hard timeout.
#>
[CmdletBinding()]
param(
  [int]$Port = 8900,
  [switch]$NoBrowser,
  # Machine-specific paths, defaulted from the environment. Override when the
  # layout differs - see the assignments below.
  [string]$ComposeFile,
  [string]$AiPython,
  # Ceiling for an operator-triggered action. The dashboard is single-threaded,
  # so an action that runs unbounded is an outage for every other reader. 120 s
  # is far longer than any of the real actions needs (doctor --deep is ~8 s) and
  # is a backstop, not a budget.
  [int]$ActionTimeoutSec = 120
)

$ErrorActionPreference = 'Stop'
$ROOT = Split-Path -Parent $PSScriptRoot
$COLLECT = Join-Path $PSScriptRoot 'collect-state.ps1'
$INDEX = Join-Path $ROOT 'index.html'

# Machine-specific locations, derived rather than hardcoded, so this file is
# portable and the blueprint template can be a verbatim copy of what ran.
# Verified to resolve to the same two paths as the literals they replaced.
$COMPOSE = if ($ComposeFile) { $ComposeFile } else { Join-Path $env:USERPROFILE 'docker-compose.yml' }
$AIPY    = if ($AiPython)   { $AiPython   } else { Join-Path $env:LOCALAPPDATA 'hermes\hermes-agent\venv\Scripts\python.exe' }

if (-not (Test-Path $INDEX)) { throw "index.html not found at $INDEX" }

# Resolve an action id to a COMMAND STRING. The id comes from the collector, so
# this is the single place a command is ever defined for the dashboard.
#
# STRINGS, not scriptblocks, and that is a correctness requirement rather than a
# style one. An action used to run as a closure directly on the request thread
# with no timeout at all, so `doctor --deep` (8 s on its own) or a wedged Docker
# daemon froze every other request for as long as it cared to. The bounded runner
# below needs a command it can hand to a separate process, and a scriptblock
# cannot cross that boundary.
#
# The page may only ever send an IDENTIFIER. It never sends a command.
$ACTIONS = @{
  'status'        = '"{0}\..\scripts\optimus.cmd" status' -f $ROOT
  'doctor'        = '"{0}\..\scripts\optimus.cmd" doctor --deep' -f $ROOT
  'census'        = '"{0}\..\scripts\optimus.cmd" docker census' -f $ROOT
  'bridge_health' = '"{0}\..\scripts\optimus.cmd" bridge health' -f $ROOT
  'sot_list'      = '"{0}\..\scripts\optimus.cmd" sot list' -f $ROOT
  'skills'        = '"{0}\..\scripts\optimus.cmd" skills list' -f $ROOT
  'qwen_status'   = '"{0}\..\scripts\optimus.cmd" qwen status' -f $ROOT
  'qwen_doctor'   = '"{0}\..\scripts\optimus.cmd" qwen doctor' -f $ROOT
  'state_doc'     = 'powershell -NoProfile -ExecutionPolicy Bypass -File "{0}\..\scripts\build-current-state.ps1"' -f $ROOT
  'mojibake'      = 'powershell -NoProfile -ExecutionPolicy Bypass -File "{0}\..\scripts\repair-mojibake.ps1"' -f $ROOT
  # Raw JSONL, deliberately. The formatted, parsed, paged view is the Journal
  # TAB, which reads /api/journal; this button is a quick console peek.
  'journal'       = 'docker exec minimax-hermes-bridge sh -c "tail -n 40 /opt/optimus/journal/minimax-hermes-bridge.jsonl 2>/dev/null"'
  # The `if errorlevel` form, not `echo exit=%ERRORLEVEL%`: cmd.exe expands
  # %ERRORLEVEL% BEFORE the first command runs, so that variant always prints
  # the inherited 0 and reports success for a failed check. An action that
  # reports success it did not achieve is worse than one that prints nothing.
  'compose_check' = 'docker compose -f "{0}" config --quiet & if errorlevel 1 (echo exit=FAILED) else (echo exit=OK)' -f $COMPOSE
  'app_status'    = '"{0}\..\scripts\optimus.cmd" app status' -f $ROOT
  'ai_auth'       = 'mcode-tools auth status'
  'ai_tools'      = 'mcode-tools connector tools'
}
# The bounded runner lives in its own file so that this script AND a background
# job can both use one implementation. A scriptblock does not cross into a
# Start-Job, so keeping it inline would have forced the action runner to either
# duplicate the timeout logic or lose it. One implementation, two callers.
. (Join-Path $PSScriptRoot 'run-bounded.ps1')

Write-Host "OPTIMUS Control Center" -ForegroundColor Cyan
Write-Host "  state  : GET  http://127.0.0.1:$Port/api/state" -ForegroundColor DarkGray
Write-Host "  ui     : GET  http://127.0.0.1:$Port/" -ForegroundColor DarkGray
Write-Host "  loopback only. Ctrl+C to stop." -ForegroundColor DarkGray

function Send($ctx, $status, $contentType, $body) {
  $bytes = [Text.Encoding]::UTF8.GetBytes($body)
  Send-Bytes $ctx $status $contentType $bytes
}

# Raw bytes, no text round-trip.
#
# Send() above takes a STRING and encodes it. Handing it a byte[] makes
# PowerShell convert bytes -> string -> bytes, which silently destroyed the
# icon font: a 504,296-byte woff2 came back as 1,799,036 bytes. It still returned
# HTTP 200, so nothing looked wrong. Binary needs its own path.
function Send-Bytes($ctx, $status, $contentType, [byte[]]$bytes, [switch]$NoCache) {
  # Headers before the body, and only once - a client that hung up leaves the
  # response already committed and re-setting ContentLength64 throws.
  try {
    $ctx.Response.StatusCode = $status
    $ctx.Response.ContentType = $contentType
    $ctx.Response.ContentLength64 = $bytes.Length
    # Assets are small, local, and must never be stale. Without this the browser
    # held the OLD icon subset and a newly added glyph rendered blank while the
    # file on disk was already correct - a fix that appears not to have worked.
    if ($NoCache) {
      $ctx.Response.Headers['Cache-Control'] = 'no-store, must-revalidate'
      $ctx.Response.Headers['Pragma']        = 'no-cache'
    }
  } catch {
    Write-Host "  (response already committed; client gone: $($_.Exception.Message))" -ForegroundColor DarkGray
    return
  }
  try {
    $ctx.Response.OutputStream.Write($bytes, 0, $bytes.Length)
    $ctx.Response.OutputStream.Close()
  } catch {
    Write-Host "  (client disconnected during response - normal)" -ForegroundColor DarkGray
  }
}

# Collect the state to a FILE, never through the console pipe.
#
# Piping a child PowerShell through Out-String runs its output through the
# console encoding, which mangles every non-ASCII character (the U+00B7
# separator became "Â·", the ellipsis became "â€¦"). Writing to a temp file and
# reading it back as UTF-8 bypasses the console entirely.
$script:StateFile   = Join-Path $PSScriptRoot 'live-state.json'
$script:StateAgeSec = 20
$script:CollectTimeoutSec = 240
$script:ActionTimeoutSec = $ActionTimeoutSec

# Run the collector with a HARD timeout.
#
# It walks 56 containers, probes two bridges and shells out to mcode-tools
# twice, so any one of those can block for an unbounded time. It used to be
# invoked with a bare `& cmd /c powershell ...`, which meant ONE wedged
# collector froze /api/state forever - and because the supervisor was watching
# that same endpoint, a single slow collect produced a restart loop that took
# the entire dashboard down. A dependency must never be able to hold hostage
# the thing that depends on it.
function Invoke-Collector {
  param([int]$TimeoutSec = 90)
  $outFile = [IO.Path]::GetTempFileName()
  try {
    $p = Start-Process -FilePath 'powershell.exe' `
      -ArgumentList '-NoProfile','-ExecutionPolicy','Bypass','-File',"`"$COLLECT`"" `
      -RedirectStandardOutput $outFile -WindowStyle Hidden -PassThru
    if (-not $p.WaitForExit($TimeoutSec * 1000)) {
      try { $p.Kill(); $p.WaitForExit(5000) } catch { }
      Write-Host "  collector exceeded ${TimeoutSec}s - killed it, keeping the last good state" -ForegroundColor Yellow
      return $null
    }
    if (Test-Path $outFile) {
      $txt = [IO.File]::ReadAllText($outFile, [Text.Encoding]::UTF8)
      if ($txt.Trim()) { return $txt }
    }
    return $null
  } catch {
    Write-Host "  collector failed: $($_.Exception.Message)" -ForegroundColor Yellow
    return $null
  } finally {
    if (Test-Path $outFile) { try { [IO.File]::Delete($outFile) } catch { } }
  }
}

# Atomic state write.
#
# The refresher job and the request handler's inline fallback both wrote
# live-state.json in place, so they collided and the log filled with
# "The process cannot access the file because it is being used by another
# process". Worse, a reader could catch a half-written file. Write to a
# sibling temp file and Rename-over: a rename within a volume is atomic, so a
# reader sees either the whole old file or the whole new one, and two writers
# never touch the same bytes.
function Write-StateFile {
  param([string]$Text)
  $dir = Split-Path $script:StateFile -Parent
  $tmp = Join-Path $dir ("live-state.{0}.tmp" -f $PID)
  [IO.File]::WriteAllText($tmp, $Text, (New-Object Text.UTF8Encoding($false)))
  try {
    [IO.File]::Replace($tmp, $script:StateFile, $null, $true)
  } catch {
    # Replace needs an existing destination; on a first run there is none.
    Move-Item -LiteralPath $tmp -Destination $script:StateFile -Force
  }
}

function Get-StateJson {
  param([int]$MaxAgeSec = 0)
  # A full collect runs docker inspect + two bridge doctors + the MiniMax
  # connector catalogue and takes 10-20s. Serves a fresh file when present.
  # $MaxAgeSec is a THREE-MODE contract. /api/state depends on the first mode.
  #   -1  READ-ONLY: serve whatever the refresher last wrote, however old, and
  #       NEVER start a collect. This is the guarantee that a request cannot
  #       run a measurement and therefore cannot block or starve the worker.
  #    0  FORCE: always collect now (startup pre-warm, explicit refresh).
  #   >0  Serve the cache only when it is younger than this, else collect.
  # The previous test was `-gt 0`, which made EVERY negative value fall through
  # to a full collect. Passing -1 under that test would not have made the cache
  # "never too old"; it would have made the 10-24s inline collect UNCONDITIONAL
  # and permanent. The mode has to exist in the function, not just in the call.
  if ((Test-Path $script:StateFile) -and $MaxAgeSec -ne 0) {
    $age = ((Get-Date) - (Get-Item $script:StateFile).LastWriteTime).TotalSeconds
    if ($MaxAgeSec -lt 0 -or $age -lt $MaxAgeSec) {
      return [IO.File]::ReadAllText($script:StateFile, [Text.Encoding]::UTF8)
    }
  }
  $txt = Invoke-Collector -TimeoutSec $script:CollectTimeoutSec
  if ($txt) { Write-StateFile $txt; return $txt }

  # The collector failed or timed out. Serving the LAST GOOD state, clearly
  # marked as no longer current, is strictly better than going dark: the
  # operator can still see what the system looked like AND can see that it is
  # stale. A dead dashboard tells you nothing; a stale one tells you something.
  if (Test-Path $script:StateFile) {
    try {
      $stale = [IO.File]::ReadAllText($script:StateFile, [Text.Encoding]::UTF8) | ConvertFrom-Json
      $stale | Add-Member -NotePropertyName stale        -NotePropertyValue $true -Force
      $stale | Add-Member -NotePropertyName stale_reason -NotePropertyValue 'collector timed out or failed - this is the last known good state' -Force
      return ($stale | ConvertTo-Json -Depth 12 -Compress)
    } catch { }
  }
  throw 'state collector produced no output and no cached state exists'
}

# Background refresher. WITHOUT THIS the dashboard is a frozen snapshot: the
# cache was only ever filled once at startup, so every number went stale within
# minutes while still looking live. One persistent job re-collects on a timer;
# the request handler only ever reads the file, so no request ever blocks.
function Start-RefreshWorker {
  param([string]$Collect, [string]$Target, [int]$EverySec = 20)
  Start-Job -ArgumentList $Collect, $Target, $EverySec -ScriptBlock {
    param($collect, $target, $every)
    # Same atomic write as the request handler. This is a separate process, so
    # the function is not visible here - inline the identical logic. Without it
    # the worker and the inline fallback corrupt each other's file.
    $dir = Split-Path $target -Parent
    $errLog = Join-Path $dir 'refresher.err.log'
    while ($true) {
      $tmp = [IO.Path]::GetTempFileName()
      $stdin = Join-Path $dir 'live-state.stdin'
      $staging = Join-Path $dir ("live-state.{0}.tmp" -f $PID)
      try {
        # Hard timeout, same reason as the request handler: a collector that
        # hangs must not wedge the refresher forever. On a kill the previous
        # state file is left untouched, so the dashboard keeps serving the last
        # good snapshot instead of going blank.
        #
        # -RedirectStandardInput is NOT optional, and its absence cost five hours.
        # This worker is a Start-Job, so it runs on PowerShell's remoting pipes.
        # Without an explicit stdin the collector inherits that pipe, the console
        # apps it spawns (git, docker) inherit it too, and the whole tree
        # deadlocks reading a stream nobody drains. Measured: the same collector
        # takes 21.6 s run directly and never returns at all when spawned from
        # inside the job. That is what the 240 s kill was reporting, 13-14 times
        # an hour, as a mystery "collector too slow". It was not slow - it was
        # blocked, and every cycle stranded a stuck git.exe (128 of them had
        # piled up, the oldest four hours).
        if (-not (Test-Path $stdin)) { [IO.File]::WriteAllText($stdin, '') }
        $cp = Start-Process -FilePath 'powershell.exe' `
          -ArgumentList '-NoProfile','-ExecutionPolicy','Bypass','-File',"`"$collect`"" `
          -RedirectStandardOutput $tmp -RedirectStandardInput $stdin -WindowStyle Hidden -PassThru
        if (-not $cp.WaitForExit(240000)) {
          try { $cp.Kill(); $cp.WaitForExit(5000) } catch { }
          try { Add-Content -LiteralPath $errLog -Value ("{0:o} collector exceeded 240s - killed, previous state kept" -f (Get-Date)) } catch { }
        } elseif (Test-Path $tmp) {
          $t = [IO.File]::ReadAllText($tmp, [Text.Encoding]::UTF8)
          if ($t.Trim()) {
            [IO.File]::WriteAllText($staging, $t, (New-Object Text.UTF8Encoding($false)))
            try { [IO.File]::Replace($staging, $target, $null, $true) }
            catch { Move-Item -LiteralPath $staging -Destination $target -Force }
          } else {
            # LOGGED, because the alternative is invisible. This branch ran with
            # no output at all, nothing was written, and the served state simply
            # aged until the watchdog failed the server for "the refresher is
            # wedged" - a conclusion that pointed at the refresher, five minutes
            # after the thing that actually went wrong, with no evidence at all.
            #
            # A collect that produced NOTHING and a collect that is still
            # running look identical from outside. This is the only place the
            # difference is observable, and it was silent.
            try { Add-Content -LiteralPath $errLog -Value ("{0:o} collector produced NO output (exit {1}) - state NOT updated, previous kept" -f (Get-Date), $cp.ExitCode) } catch { }
          }
        }
      } catch {
        # Never swallow a collect failure again. An empty catch here is how the
        # refresher died silently once and the whole dashboard froze at 19.5h
        # old with nothing in the log to say why.
        try { Add-Content -LiteralPath $errLog -Value ("{0:o} {1}" -f (Get-Date), $_.Exception.Message) } catch { }
      } finally {
        if (Test-Path $tmp) { Remove-Item -LiteralPath $tmp -Force -ErrorAction SilentlyContinue }
        if (Test-Path $staging) { Remove-Item -LiteralPath $staging -Force -ErrorAction SilentlyContinue }
      }
      Start-Sleep -Seconds $every
    }
  } | Out-Null
}

# ------------------------------------------------------------- AI JOBS -----
# A long operation must never run on the request thread. The ask path returns a
# job id in milliseconds and the page polls for the result, so the single
# listener thread is only ever doing file-sized work.
$script:AskDir = Join-Path $PSScriptRoot 'ask'

# ------------------------------------------------- NOTEBOOK INTERROGATION
# A long operation must never run on the request thread, and the same
# guarantees the /api/ask job carries apply here: a running marker written
# BEFORE the work starts, an atomic result write, and a budget that EXCEEDS the
# measured cost. Measured: 41 s for a real answer, so 240 s leaves room for the
# slow tail. A timeout shorter than what it measures is a dead sensor.
$script:NbDir = Join-Path $PSScriptRoot 'nbask'
if (-not (Test-Path -LiteralPath $script:NbDir)) {
  try { New-Item -ItemType Directory -Path $script:NbDir -Force | Out-Null } catch { }
}

function Start-NbAskJob {
  param([string]$Notebook, [string]$Question, [string]$Script, [int]$TimeoutSec = 240)
  $id = [guid]::NewGuid().ToString('N').Substring(0, 12)
  $out = Join-Path $script:NbDir "$id.json"
  $req = Join-Path $script:NbDir "$id.req.json"
  $raw = "$out.raw"
  $err = "$out.err"
  [IO.File]::WriteAllText($out, '{"state":"running"}', (New-Object Text.UTF8Encoding($false)))
  # The request travels as a FILE. A native Windows argument holding quotes and
  # Romanian diacritics is exactly what produces a plausible WRONG answer rather
  # than an error, and a file cannot be re-parsed by the shell.
  [IO.File]::WriteAllText($req, (@{ notebook = $Notebook; question = $Question } | ConvertTo-Json -Compress), (New-Object Text.UTF8Encoding($false)))

  Start-Job -ArgumentList $Script, $req, $out, $raw, $err, $TimeoutSec -ScriptBlock {
    param($scriptPath, $reqFile, $out, $raw, $err, $timeoutSec)
    $res = $null
    $prevEnc = $null
    try {
      $prevEnc = [Console]::OutputEncoding
      try { [Console]::OutputEncoding = [Text.Encoding]::UTF8 } catch { }
      $p = Start-Process -FilePath 'node' -ArgumentList "`"$scriptPath`"", "`"$reqFile`"" `
        -RedirectStandardOutput $raw -RedirectStandardError $err -WindowStyle Hidden -PassThru
      if (-not $p.WaitForExit(($timeoutSec * 1000))) {
        try { $p.Kill(); $p.WaitForExit(5000) } catch { }
        $res = @{ state = 'error'; error = "notebook.google.com did not answer within ${timeoutSec}s" }
      } else {
        $txt = ''
        if (Test-Path -LiteralPath $raw) { $txt = [IO.File]::ReadAllText($raw, [Text.Encoding]::UTF8) }
        if (-not $txt.Trim()) {
          $e2 = ''
          if (Test-Path -LiteralPath $err) { $e2 = [IO.File]::ReadAllText($err, [Text.Encoding]::UTF8) }
          $res = @{ state = 'error'; error = "the query returned nothing$(if($e2.Trim()){': ' + $e2.Trim().Substring(0,[Math]::Min(200,$e2.Trim().Length))})" }
        } else {
          try {
            $parsed = $txt | ConvertFrom-Json
            if ($parsed.ok -eq $true) {
              $res = @{ state = 'done'; ok = $true; answer = [string]$parsed.answer; notebook = [string]$parsed.notebook }
            } elseif ($parsed.outcome -eq 'UNAUTHENTICATED') {
              # The §10.2 breaker. A correct answer about the STATE, and NOT an
              # answer to the question - so it gets its own outcome, never a
              # blank answer that reads like "nothing found".
              $res = @{ state = 'unauthenticated'; ok = $false; outcome = 'UNAUTHENTICATED'; retry_after_sec = $parsed.retry_after_sec; error = $parsed.remedy }
            } else {
              $res = @{ state = 'error'; ok = $false; error = [string]$parsed.error }
            }
          } catch {
            $res = @{ state = 'error'; ok = $false; error = 'the query result was not parseable JSON' }
          }
        }
      }
    } catch {
      $res = @{ state = 'error'; ok = $false; error = "$($_.Exception.GetType().FullName): $($_.Exception.Message)" }
    } finally {
      if ($prevEnc) { try { [Console]::OutputEncoding = $prevEnc } catch { } }
    }
    try {
      $tmp = "$out.$PID.tmp"
      [IO.File]::WriteAllText($tmp, ($res | ConvertTo-Json -Depth 6 -Compress), (New-Object Text.UTF8Encoding($false)))
      Move-Item -LiteralPath $tmp -Destination $out -Force
    } catch { }
    foreach ($scratch in @($raw, $err, $req)) {
      try { if (Test-Path -LiteralPath $scratch) { Remove-Item -LiteralPath $scratch -Force -ErrorAction SilentlyContinue } } catch { }
    }
  } | Out-Null
  return $id
}

function Start-AskJob {
  param([string]$Prompt, [string]$Py, [string]$Client, [int]$TimeoutSec = 180)
  $id = [guid]::NewGuid().ToString('N').Substring(0, 12)
  $out = Join-Path $script:AskDir "$id.json"
  $promptFile = Join-Path $script:AskDir "$id.prompt.txt"
  $raw = "$out.raw"
  $err = "$out.err"
  # The RUNNING marker is written BEFORE the job starts, so a poll can never
  # find nothing and mistake the gap for a failure.
  [IO.File]::WriteAllText($out, '{"state":"running"}', (New-Object Text.UTF8Encoding($false)))
  [IO.File]::WriteAllText($promptFile, $Prompt, (New-Object Text.UTF8Encoding($false)))
  Start-Job -ArgumentList $Prompt, $Py, $Client, $out, $promptFile, $raw, $err, $TimeoutSec -ScriptBlock {
    param($prompt, $py, $client, $out, $promptFile, $raw, $err, $timeoutSec)
    $res = $null
    $prevEnc = $null
    try {
      $prevEnc = [Console]::OutputEncoding
      try { [Console]::OutputEncoding = [Text.Encoding]::UTF8 } catch { }
      # The prompt goes in as a REAL FILE on stdin, not a pipe. Same lesson as
      # the refresher (postmortem #17): this is a Start-Job, so it runs on
      # PowerShell's remoting pipes, and a child inheriting an undrained stdin
      # deadlocks silently and forever. A file cannot deadlock. The prompt must
      # be on stdin rather than argv because a native argument containing
      # newlines and quotes gets mangled by Windows and argparse dies on a bare
      # "usage:" error.
      $p = Start-Process -FilePath $py `
        -ArgumentList "`"$client`"", 'ask', '-', '--max-tokens', '700' `
        -RedirectStandardInput $promptFile -RedirectStandardOutput $raw `
        -RedirectStandardError $err -WindowStyle Hidden -PassThru
      if (-not $p.WaitForExit(($timeoutSec * 1000))) {
        try { $p.Kill(); $p.WaitForExit(5000) } catch { }
        $res = @{ state = 'error'; error = "the model did not answer within ${timeoutSec}s" }
      } else {
        $answer = ''
        if (Test-Path -LiteralPath $raw) { $answer = [IO.File]::ReadAllText($raw, [Text.Encoding]::UTF8) }
        # Belt and braces on encoding. UTF-8 is already forced above, so this
        # should be a no-op; anything still double-encoded is re-decoded
        # cp1252 -> UTF-8 the same proven way repair-mojibake.ps1 does.
        # Deliberately ASCII-only in source: PS 5.1 reads a BOM-less script as
        # ANSI, so writing mojibake LITERALS into a .ps1 is itself a parse hazard.
        $repl = [char]0xFFFD
        $cp = [Text.Encoding]::GetEncoding(1252)
        try {
          $decoded = [Text.Encoding]::UTF8.GetString($cp.GetBytes($answer))
          $before = ([regex]::Matches($answer, '[\u00A0-\u00FF]{2,3}')).Count
          $after  = ([regex]::Matches($decoded, '[\u00A0-\u00FF]{2,3}')).Count
          if ($after -lt $before) { $answer = $decoded }
          # ORDER MATTERS, and the guard that used to sit here made it backwards.
          # A U+FFFD encoded as cp1252 arrives as THREE characters, and decoding
          # is what CONVERTS it into a single real U+FFFD - so the old
          # `if (-not $decoded.Contains($repl))` skipped the repair in exactly
          # the case that needed it, and a genuine U+FFFD reached the operator.
          # Decode first, then strip what the decode produced. The page has
          # carried this ordering, with this comment, since postmortem #5's
          # sibling; the server never did.
          $answer = $answer.Replace($repl, '-')
        } catch { }
        $res = @{ state = 'done'; answer = $answer.Trim() }
      }
    } catch {
      $res = @{ state = 'error'; error = "$($_.Exception.GetType().FullName): $($_.Exception.Message)" }
    } finally {
      if ($prevEnc) { try { [Console]::OutputEncoding = $prevEnc } catch { } }
    }
    # Atomic write. A poll must never read a half-written result and report it
    # as a malformed answer - the same reasoning as the state file's rename.
    try {
      $tmp = "$out.$PID.tmp"
      [IO.File]::WriteAllText($tmp, ($res | ConvertTo-Json -Depth 6 -Compress), (New-Object Text.UTF8Encoding($false)))
      Move-Item -LiteralPath $tmp -Destination $out -Force
    } catch { }
    foreach ($scratch in @($raw, $err, $promptFile)) {
      try { if (Test-Path -LiteralPath $scratch) { Remove-Item -LiteralPath $scratch -Force -ErrorAction SilentlyContinue } } catch { }
    }
  } | Out-Null
  # Prune this job directory only, and only files older than an hour, so the
  # scratch space cannot grow without bound and cannot touch anything else.
  # Deliberately NOT the only prune: this one only runs when someone asks a
  # question, so a quiet afternoon would leave yesterday's results on disk. The
  # startup prune below covers that case, and nothing else does.
  try {
    Get-ChildItem -LiteralPath $script:AskDir -File -ErrorAction SilentlyContinue |
      Where-Object { $_.LastWriteTime -lt (Get-Date).AddHours(-1) } |
      ForEach-Object { try { Remove-Item -LiteralPath $_.FullName -Force -ErrorAction SilentlyContinue } catch { } }
  } catch { }
  return $id
}

function Start-ActionJob {
  param([string]$Command, [int]$TimeoutSec = 120, [string]$WorkDir)
  $id = [guid]::NewGuid().ToString('N').Substring(0, 12)
  $out = Join-Path $script:AskDir "act-$id.json"
  # Marker before the job starts, so a poll never mistakes the gap for failure.
  [IO.File]::WriteAllText($out, '{"state":"running"}', (New-Object Text.UTF8Encoding($false)))
  Start-Job -ArgumentList $Command, $out, $TimeoutSec, $WorkDir, $PSScriptRoot, $script:AskDir, $id -ScriptBlock {
    param($command, $out, $timeoutSec, $workDir, $apiDir, $askDir, $jobId)
    $res = $null
    try {
      # The job cannot see this script's functions, so it dot-sources the SAME
      # file rather than carrying its own copy of the bounded runner. One
      # implementation, two callers - a duplicated timeout is a timeout that
      # will eventually be edited in one place only.
      # $apiDir holds run-bounded.ps1; $askDir holds the stdin scratch file.
      . (Join-Path $apiDir 'run-bounded.ps1')
      # Per-job stdin file, not a shared one. A single shared action.stdin means
      # two concurrent actions are reading the same handle, and whichever
      # creates it last wins for both.
      $stdin = Join-Path $askDir ("action-$jobId.stdin")
      $text = Invoke-BoundedCommand -Command $command -TimeoutSec $timeoutSec -WorkDir $workDir -StdinFile $stdin
      if ($text.Length -gt 60000) { $text = $text.Substring(0, 60000) + "`n...[truncated]" }
      $res = @{ state = 'done'; output = $text }
    } catch {
      $res = @{ state = 'error'; error = "$($_.Exception.GetType().FullName): $($_.Exception.Message)" }
    }
    # This job's own stdin scratch file, not the shared one. Left behind it is a
    # small leak that the hourly prune would eventually collect - which is how it
    # survived long enough to be noticed. The job that creates a file removes it.
    try { if ($stdin -and (Test-Path -LiteralPath $stdin)) { Remove-Item -LiteralPath $stdin -Force -ErrorAction SilentlyContinue } } catch { }
    # Atomic: a poll must never read a half-written result.
    try { Write-AtomicJson -Path $out -Value $res -Depth 6 } catch { }
  } | Out-Null
  return $id
}

# Refresh the bridge journal in the BACKGROUND and cache it on disk.
#
# This endpoint used to run `docker exec` inline behind a 15 s cap. A cap makes
# a freeze bounded; it does not remove it, and a wedged Docker daemon would
# still stall every other reader of this console for the full cap. Nothing in
# the page calls /api/journal, but "nothing calls it" is how a request thread
# quietly keeps a hazard nobody is looking for.
#
# So the endpoint now serves the last known journal - a file read, microseconds -
# and kicks off a refresh. The first call after a restart returns an empty,
# explicitly-flagged `refreshing` result rather than blocking for the answer.
# The response SHAPE is unchanged, so any future caller is unaffected.
function Start-JournalRefresh {
  param([string]$Which, [int]$TimeoutSec = 15)
  $cache = Join-Path $script:AskDir "journal-$Which.json"
  $flag  = Join-Path $script:AskDir "journal-$Which.running"
  Start-Job -ArgumentList $Which, $cache, $flag, $TimeoutSec, $script:AskDir -ScriptBlock {
    param($which, $cache, $flag, $timeoutSec, $askDir)
    $recs = @()
    $tmp = [IO.Path]::GetTempFileName()
    $stdin = Join-Path $askDir 'journal.stdin'
    try {
      # A Start-Job is a SEPARATE runspace: it does not inherit anything this
      # script dot-sourced. Calling Read-SharedText here without this line
      # throws, the catch swallows it, and the journal silently never caches -
      # so the endpoint would answer `refreshing: true` for ever and look like a
      # daemon problem rather than a missing function.
      . (Join-Path (Split-Path $askDir -Parent) 'run-bounded.ps1')
      if (-not (Test-Path $stdin)) { [IO.File]::WriteAllText($stdin, '') }
      $argStr = 'exec minimax-' + $which + '-bridge sh -c "tail -n 40 /opt/optimus/journal/minimax-' + $which + '-bridge.jsonl 2>/dev/null"'
      $dp = Start-Process -FilePath 'docker.exe' -ArgumentList $argStr `
        -RedirectStandardOutput $tmp -RedirectStandardInput $stdin -WindowStyle Hidden -PassThru
      if ($dp.WaitForExit(($timeoutSec * 1000))) {
        $raw = Read-SharedText -Path $tmp
        foreach ($l in ($raw -split "`n")) { if ($l.Trim()) { try { $recs += ($l | ConvertFrom-Json) } catch { } } }
      }
      # Only a COMPLETED read is cached. Caching an empty result because the
      # daemon was slow would turn a transient hiccup into a permanent "no
      # journal", which is the exact class of silent failure this file exists to
      # stop: a later reader cannot tell "nothing was written" from "we did not
      # manage to look".
      $payload = @{ ok = $true; bridge = "minimax-$which-bridge"; count = $recs.Count; records = $recs }
      $stage = "$cache.$PID.tmp"
      [IO.File]::WriteAllText($stage, ($payload | ConvertTo-Json -Depth 6 -Compress), (New-Object Text.UTF8Encoding($false)))
      Move-Item -LiteralPath $stage -Destination $cache -Force
    } catch { }
    finally {
      try { if (Test-Path $tmp) { Remove-Item -LiteralPath $tmp -Force -ErrorAction SilentlyContinue } } catch { }
      # The flag is what stops a second refresh stacking on top of this one. If
      # the job died before clearing it, the age check in the route treats a
      # stale flag as not-in-flight, so it cannot wedge the endpoint forever.
      try { if (Test-Path $flag) { Remove-Item -LiteralPath $flag -Force -ErrorAction SilentlyContinue } } catch { }
    }
  } | Out-Null
}

# ---------------------------------------------------------------- start up --
# Everything above must be DEFINED before it is CALLED. PowerShell runs
# top-to-bottom, so the listener and the pre-warm both live down here -- the
# earlier version called Get-StateJson before its definition existed and the
# pre-warm silently failed.
# A compact, human-readable digest of the live state.
#
# Sending the raw 21 KB state JSON was wrong twice over: it failed (the prompt
# got too large for the API) and it is a bad briefing - the model has to dig
# through a full container list and file inventory to find the one number you
# asked about. Give it the facts, already summarised.
function Get-StateDigest {
  # READ-ONLY, for the same reason as /api/state. This is the /api/ask path: if
  # the cache were ever older than one cycle it would start a collect here, on
  # the shared listener thread, and a question would block everyone else's poll
  # for 10-24s. The digest already opens with `measured_at`, so the model is
  # told exactly how old the facts are rather than being handed a silent lie.
  $s = (Get-StateJson -MaxAgeSec -1) | ConvertFrom-Json
  $L = New-Object System.Collections.Generic.List[string]
  $d = $s.sections
  $L.Add("measured_at: $($s.generated)")
  $L.Add("containers.total: $($d.docker.total)")
  $L.Add("containers.hermes_mcp: $($d.docker.hermes_mcp)")
  $L.Add("containers.sentinel: $($d.docker.sentinel)")
  $L.Add("containers.by_project: " + (($d.docker.by_project.PSObject.Properties | ForEach-Object { "$($_.Name)=$($_.Value)" }) -join ', '))
  $L.Add("compose.present: $($d.docker.compose_present)  compose_valid: $($d.docker.compose_valid)")
  foreach ($b in $d.bridges) {
    $L.Add("bridge.$($b.name): up=$($b.up) health=$($b.health) ok=$($b.ok) warn=$($b.warn) fail=$($b.fail)")
    foreach ($c in @($b.checks | Where-Object { $_.severity -ne 'ok' })) {
      # This used to read $(Clip $c.detail 110), intending "truncate to 110
      # chars". No such function existed, so PowerShell resolved `Clip` to the
      # Windows clip.exe Clipboard binary and ran
      #     clip.exe "<detail>" 110
      # which printed "Invalid argument/option" to stderr and substituted
      # nothing. The handover briefing therefore silently dropped the detail of
      # every non-ok bridge check - the single most useful diagnostic in the
      # system - and the only trace was CLIP /? noise in the log.
      # Truncate explicitly, and never rely on a name that a system binary owns.
      $det = [string]$c.detail
      if ($det.Length -gt 110) { $det = $det.Substring(0, 110) + ' [truncated]' }
      $L.Add("   bridge.$($b.name).check.$($c.id): $($c.severity) - $det")
    }
  }
  foreach ($v in $d.services) { $L.Add("service.$($v.name): up=$($v.up) http=$($v.code) port=$($v.port)") }
  $L.Add("qwen.daemon_up: $($d.qwen.daemon_up)  oauth_credential: $($d.qwen.oauth_credential)  ollama_installed: $($d.qwen.ollama_installed)  ollama_up: $($d.qwen.ollama_up)")
  $L.Add("minimax.code_installed: $($d.minimax.code_installed)  design_installed: $($d.minimax.design_installed)  cli_auth: $($d.minimax.cli_auth)  connector_tools: $($d.minimax.connector_tools)")
  $L.Add("skills.mavis: $($d.skills.mavis_count)  personal: $($d.skills.personal_count)  hermes: $($d.skills.hermes_count)")

  # NotebookLM. This was MISSING ENTIRELY: the console displayed 11 notebooks
  # and the AI Analyst could not see one of them. Popy can ask "what is in my
  # CV notebook" and get an answer that silently omits that the notebook exists
  # - the exact class of omission this file exists to prevent.
  if ($d.notebooks) {
    $nb = $d.notebooks
    $L.Add("notebooks.server: $($nb.server)  measured: $($nb.measured)  authenticated: $($nb.authenticated)  count: $($nb.count)  total_sources: $($nb.total_sources)")
    if (-not $nb.measured) {
      # An unmeasured surface is reported as unmeasured. Never as zero.
      $L.Add("   notebooks: NOT MEASURED - do not assume an empty library ($($nb.note))")
    } elseif (-not $nb.authenticated) {
      $L.Add("   notebooks: session is NOT signed in; the library below may be the last known list, not a live one")
    } else {
      foreach ($n in @($nb.notebooks)) {
        $L.Add("   notebook: $($n.name)  id=$($n.id)  updated=$($n.updated)  sources=$($n.sources)")
      }
    }
  } else {
    $L.Add("notebooks: section absent from the state file - say UNKNOWN, do not say zero")
  }
  if ($d.hermes_update) {
    $h = $d.hermes_update
    $L.Add("hermes.version: $($h.version)  live_modified_files: $($h.modified_count)  update_lock: $($h.lock_present)  verdict: $($h.verdict)")
  }
  # MEASURED: seven Get-NetTCPConnection calls took 25.5 s on this machine
  # (~3.3 s each, WMI under the hood). That is exactly how long the /api/ask POST
  # was taking, because this line runs while building the prompt on the request
  # thread - so making the state read-only did NOT make asking cheap, and the
  # freeze simply moved somewhere quieter. A probe that costs as much as the
  # thing it measures is not a probe, it is a stall.
  #
  # One .NET call replaces all seven: 0.014-0.119 s, and it returns the same
  # seven ports as both netstat -ano and Get-NetTCPConnection. Verified against
  # all three on the same machine before choosing it.
  $listening = @{}
  try {
    [System.Net.NetworkInformation.IPGlobalProperties]::GetIPGlobalProperties().GetActiveTcpListeners() |
      ForEach-Object { $listening[[int]$_.Port] = $true }
  } catch { }
  $L.Add("ports_up: " + ((8801,8802,8080,8082,3001,8765,8900,8901,8910,8912,9412 | Where-Object { $listening.ContainsKey([int]$_) }) -join ','))
  return ($L -join "`n")
}

$listener = [System.Net.HttpListener]::new()
$listener.Prefixes.Add("http://127.0.0.1:$Port/")
$listener.Start()

# Pre-warm BEFORE the browser opens, then keep it fresh forever.
Write-Host "  collecting state (about 10-15s, once)..." -ForegroundColor DarkYellow
try { $null = Get-StateJson -MaxAgeSec 0; Write-Host "  state ready." -ForegroundColor Green }
catch { Write-Host "  state collection failed: $($_.Exception.Message)" -ForegroundColor Red }

# The job directory must exist before the first question arrives, and it must
# be created HERE rather than lazily inside the handler: creating it on the
# request thread would be the one slow thing left on that path.
if (-not (Test-Path -LiteralPath $script:AskDir)) {
  try { New-Item -ItemType Directory -Path $script:AskDir -Force | Out-Null } catch { }
}
if (-not (Test-Path -LiteralPath $script:AskDir)) {
  Write-Host "  WARNING: could not create the job directory at $script:AskDir - Ask will return an error" -ForegroundColor Red
} else {
  Write-Host "  ask jobs: $script:AskDir" -ForegroundColor DarkGray
  # Prune here as well as in Start-AskJob. Without this, a day with no questions
  # leaves yesterday's results on disk forever, because the per-ask prune only
  # runs when a question arrives.
  try {
    $stale = @(Get-ChildItem -LiteralPath $script:AskDir -File -ErrorAction SilentlyContinue |
      Where-Object { $_.LastWriteTime -lt (Get-Date).AddHours(-1) })
    foreach ($s in $stale) { try { Remove-Item -LiteralPath $s.FullName -Force -ErrorAction SilentlyContinue } catch { } }
    if ($stale.Count) { Write-Host "  pruned $($stale.Count) stale job file(s)" -ForegroundColor DarkGray }
  } catch { }
}

$worker = Start-RefreshWorker -Collect $COLLECT -Target $script:StateFile -EverySec $script:StateAgeSec
Write-Host "  live refresh on: every $($script:StateAgeSec)s" -ForegroundColor DarkCyan

if (-not $NoBrowser) {
  try { Start-Process "http://127.0.0.1:$Port/" } catch { Write-Host "  (open the URL manually)" -ForegroundColor DarkYellow }
}

try {
  while ($listener.IsListening) {
    $ctx = $listener.GetContext()
    $path = $ctx.Request.Url.AbsolutePath
    try {
      switch -Regex ($path) {
        '^/$' {
          # Read the file as UTF-8 explicitly. `Get-Content -Raw` uses the
          # PowerShell 5.1 default encoding, which is ANSI for a file with no
          # BOM, so every multi-byte character in the page (the U+00B7
          # separators, the ellipsis) was served mangled as "Â·" / "â€¦".
          Send $ctx 200 'text/html; charset=utf-8' ([IO.File]::ReadAllText($INDEX, [Text.Encoding]::UTF8))
        }
        '^/api/health$' {
          # This reported only the action list. It now ALSO reports whether the
          # supervisor is actually watching, and what it has had to restart.
          # A dashboard that cannot say whether it is being kept alive is
          # precisely the dashboard that silently stopped being alive for 19.5
          # hours with nothing to show for it. The action list is still here.
          $sup = $null
          $hf = Join-Path $PSScriptRoot 'cc-health.json'
          if (Test-Path $hf) {
            try { $sup = [IO.File]::ReadAllText($hf, [Text.Encoding]::UTF8) | ConvertFrom-Json } catch { $sup = $null }
          }
          $payload = [ordered]@{
            ok         = $true
            actions    = $ACTIONS.Keys
            port       = $Port
            supervised = ($null -ne $sup)
            supervisor = $sup
          }
          Send $ctx 200 'application/json; charset=utf-8' ($payload | ConvertTo-Json -Depth 6)
        }
        '^/assets/' {
          # Static assets (the local icon webfont). Serving them is what makes
          # this console STAND-ALONE: loaded from a CDN, every glyph becomes a
          # blank box the moment the machine is offline, and a blank box is
          # indistinguishable from a design choice.
          #
          # The full path is resolved and then checked to be INSIDE the assets
          # directory. Without that, "/assets/../../../../Windows/System32/…"
          # is a file disclosure. A file server is a security boundary, not a
          # convenience.
          # $PSScriptRoot is 90_CONTROL_CENTER\api, so the assets folder is one
          # level ABOVE it. Getting this wrong yields a clean 404 that looks
          # exactly like "the route is not registered" - which is how it cost
          # one round trip to spot.
          $assetsRoot = [IO.Path]::GetFullPath((Join-Path (Split-Path $PSScriptRoot -Parent) 'assets'))
          $rel = $path.Substring('/assets/'.Length)
          $full = [IO.Path]::GetFullPath((Join-Path $assetsRoot $rel))
          if (-not $full.StartsWith($assetsRoot, [StringComparison]::OrdinalIgnoreCase)) {
            Write-Host "  (rejected path escape: $path)" -ForegroundColor Red
            Send $ctx 403 'text/plain; charset=utf-8' 'forbidden'
            break
          }
          if (Test-Path -LiteralPath $full) {
            $ext = [IO.Path]::GetExtension($full).ToLowerInvariant()
            $ct = switch ($ext) {
              '.css'  { 'text/css; charset=utf-8' }
              '.woff2'{ 'font/woff2' }
              '.svg'  { 'image/svg+xml' }
              '.png'  { 'image/png' }
              '.ico'  { 'image/x-icon' }
              '.json' { 'application/json; charset=utf-8' }
              default { 'application/octet-stream' }
            }
            Send-Bytes $ctx 200 $ct ([IO.File]::ReadAllBytes($full)) -NoCache
          } else {
            Send $ctx 404 'text/plain; charset=utf-8' 'not found'
          }
        }
        '^/api/state$' {
          # READ-ONLY, STRUCTURALLY. This handler cannot start a measurement, so
          # it cannot take 10-24s and cannot starve the refresher that feeds it.
          #
          # The disease was never the THRESHOLD, it was the SHARED THREAD. This
          # handler and the refresher both ran inline collects on the one
          # single-threaded HttpListener, so a slow request made the cache older,
          # which made the NEXT request collect too, which made the cache older
          # again. Every tuning of the threshold moved WHERE the feedback loop
          # started; none of them removed the loop. Widening it to 5x measured
          # fine in isolation and starved the refresher into serving a ZERO-BYTE
          # body. A threshold cannot fix a shared queue.
          #
          # MaxAgeSec -1 = serve whatever the refresher last wrote, however old.
          # The one case that can still collect is a MISSING file, and that is
          # bounded to once: the startup pre-warm writes it before the browser is
          # opened. Age is no longer a trigger for work on the request path.
          #
          # A DEAD refresher is still caught, one level up where it belongs: the
          # supervisor fails the server when the served state passes
          # MaxStateAgeSec (300s) and restarts it. The page also shows the age.
          $json = Get-StateJson -MaxAgeSec -1
          # Never hand a non-JSON body to /api/state. The supervisor parses this
          # endpoint, and when the collector timed out it was served the bare
          # word "True" (PowerShell leaked a boolean out of a pipeline), so the
          # watchdog died on "Invalid JSON primitive" and never reached its
          # three-strike threshold - meaning the monitor broke at exactly the
          # moment it was needed. A monitoring endpoint that can return garbage
          # stops monitoring precisely when it matters.
          $okJson = $false
          try { $null = $json | ConvertFrom-Json; $okJson = $true } catch { $okJson = $false }
          if (-not $okJson) {
            Write-Host "  (state payload was not valid JSON - serving a minimal stub)" -ForegroundColor Red
            $json = ([ordered]@{
              generated = (Get-Date).ToString('o')
              stale = $true
              stale_reason = 'state payload could not be produced or parsed'
              sections = [ordered]@{}
              history = [ordered]@{ samples = 0; total_series = @(); fail_series = @(); warn_series = @(); by_day = @() }
            } | ConvertTo-Json -Depth 8 -Compress)
          }
          Send $ctx 200 'application/json; charset=utf-8' $json
        }
        '^/favicon\.ico$' {
          Send $ctx 200 'image/svg+xml' '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><rect width="16" height="16" rx="3" fill="#0b0f14"/><text x="8" y="12" font-size="10" text-anchor="middle" fill="#4da3ff">O</text></svg>'
        }
        # ------------------------------------------------- NOTEBOOK INTERROGATION
        # The console could SHOW the 11 notebooks and could not ASK them. The
        # capability already existed (nblm_ask) and was unreachable, which is the
        # same shape as every other defect in this project's history: the piece
        # exists, nothing calls it, and the screen looks finished.
        #
        # Async for the same reason /api/ask is. A measured NotebookLM answer
        # takes 41 s; on the single-threaded listener that starves /api/state,
        # and a dashboard that freezes while you ask it something is worse than
        # one that cannot ask. Job id out in ~5 ms, page polls.
        '^/api/notebook/ask$' {
          $nbName = ''; $nbQ = ''
          if ($ctx.Request.HasEntityBody) {
            $rawNb = (New-Object IO.StreamReader($ctx.Request.InputStream)).ReadToEnd()
            if ($rawNb.Trim()) {
              $nbBody = $rawNb | ConvertFrom-Json
              $nbName = [string]$nbBody.notebook
              $nbQ    = [string]$nbBody.question
            }
          }
          if (-not $nbName -or -not $nbQ) {
            Send $ctx 400 'application/json' (@{ ok = $false; error = 'notebook and question are both required' } | ConvertTo-Json)
            break
          }
          # Refuse an unknown notebook from the CACHED list rather than after a
          # 41 s browser round-trip that fails. The list is at most 10 minutes
          # old, which is the right trade for a spelling mistake; a genuinely
          # new notebook still gets through with its exact name once the cache
          # refreshes. A miss here is never reported as "no notebooks exist".
          $nbKnown = $false
          try {
            $nbState = [IO.File]::ReadAllText((Join-Path $ROOT 'api\live-state.json'), [Text.Encoding]::UTF8) | ConvertFrom-Json
            $nbKnown = @($nbState.sections.notebooks.notebooks | ForEach-Object { $_.name }) -contains $nbName
            $nbAuth = $nbState.sections.notebooks.authenticated
          } catch { $nbAuth = $null }
          if ($nbAuth -ne $true) {
            Send $ctx 200 'application/json' (@{ ok = $false; outcome = 'UNAUTHENTICATED'; job = $null;
              error = 'the NotebookLM session is not signed in - sign into notebook.google.com on the minimax profile' } | ConvertTo-Json)
            break
          }
          if (-not $nbKnown) {
            Send $ctx 400 'application/json' (@{ ok = $false; error = "no notebook is named '$nbName' - the name must match one shown in the console, exactly" } | ConvertTo-Json)
            break
          }
          $nbScript = Join-Path $ROOT '..\Mavis-Google_Access\google-layer\notebook-ask.js'
          if (-not (Test-Path -LiteralPath $nbScript)) {
            Send $ctx 500 'application/json' (@{ ok = $false; error = "notebook-ask.js is missing at $nbScript" } | ConvertTo-Json)
            break
          }
          $nbJob = Start-NbAskJob -Notebook $nbName -Question $nbQ -Script $nbScript
          Send $ctx 200 'application/json' (@{ ok = $true; notebook = $nbName; question = $nbQ; job = $nbJob; state = 'running' } | ConvertTo-Json)
        }
        '^/api/notebook/ask/([0-9a-f]{12})$' {
          $nbId = $Matches[1]
          $nbF = Join-Path $script:NbDir "$nbId.json"
          if (-not (Test-Path -LiteralPath $nbF)) {
            Send $ctx 200 'application/json' (@{ ok = $true; state = 'unknown'; error = 'this job id is not one of ours' } | ConvertTo-Json)
            break
          }
          $nbRaw = [IO.File]::ReadAllText($nbF, [Text.Encoding]::UTF8)
          $nbOk = $false
          try { $null = $nbRaw | ConvertFrom-Json; $nbOk = $true } catch { $nbOk = $false }
          if (-not $nbOk) {
            Send $ctx 200 'application/json' (@{ ok = $true; state = 'error'; error = 'this job result is unreadable - truncated or corrupted on disk' } | ConvertTo-Json)
            break
          }
          $nbRes = $nbRaw | ConvertFrom-Json
          # A 'running' marker older than the job's own budget is abandoned, not
          # running. Reporting it as running forever is the failure mode that
          # made a poll look like a hang.
          if ($nbRes.state -eq 'running') {
            try {
              $age = ((Get-Date) - (Get-Item -LiteralPath $nbF).LastWriteTime).TotalSeconds
              if ($age -gt 300) { $nbRes.state = 'abandoned'; $nbRes.error = "abandoned after $([int]$age)s without recording a result" }
            } catch { }
          }
          Send $ctx 200 'application/json' ($nbRes | ConvertTo-Json -Depth 6 -Compress)
        }
        '^/api/ask$' {
          # THE DIFFERENTIATOR - and the last place the console could still freeze.
          # A plain infrastructure dashboard just displays numbers. This one can be
          # ASKED about them: the live snapshot goes to MiniMax-M3 with the
          # question, and it answers in plain English with the measured values in hand.
          #
          # ASYNC, and that is the entire point. Measured before this change: this
          # call takes 26-70 s, and while one was running, a concurrent /api/state
          # got NO RESPONSE AT ALL - two probes were cut off at 12 s and 13.9 s -
          # because the listener is a single thread and the subprocess owned it.
          #
          # The state collect was fixed by making the state path read-only. A
          # subprocess cannot be fixed that way, because here the WORK is the
          # duration: no cache policy shortens a 40-second model call. So the
          # request now hands back a job id in ~5 ms and the page polls. Nothing
          # slow ever touches the request thread again.
          $question = ''
          if ($ctx.Request.HasEntityBody) {
            $raw = (New-Object IO.StreamReader($ctx.Request.InputStream)).ReadToEnd()
            if ($raw.Trim()) { $question = ($raw | ConvertFrom-Json).question }
          }
          if (-not $question) {
            Send $ctx 400 'application/json' (@{ ok = $false; error = 'question required' } | ConvertTo-Json)
            break
          }
          # minimax_client.py is Python, so it must be invoked THROUGH the
          # interpreter. Calling the .py directly with & does not execute it.
          $py = $AIPY
          $client = "$ROOT\..\scripts\minimax_client.py"
          if (-not (Test-Path $py) -or -not (Test-Path $client)) {
            Send $ctx 500 'application/json' (@{ ok = $false; error = "AI client unavailable (py=$([bool](Test-Path $py)), client=$([bool](Test-Path $client)))" } | ConvertTo-Json)
            break
          }
          # The digest is read-only now, so building the prompt here costs
          # milliseconds. Doing it on the request thread is safe precisely
          # BECAUSE the state path can no longer start a measurement.
          $prompt = @(
            'You are the operations analyst for the OPTIMUS system on this Windows machine.',
            'Answer ONLY from the measured facts below. Quote exact numbers.',
            'Be concise - three sentences at most unless asked for more.',
            'If something is wrong, say exactly what and what to do about it.',
            'If everything is healthy, say so plainly. Never invent problems, and',
            'never guess a number that is not stated.',
            '',
            'MEASURED FACTS:',
            (Get-StateDigest),
            '',
            "QUESTION: $question"
          ) -join "`n"
          $askJob = Start-AskJob -Prompt $prompt -Py $py -Client $client
          Send $ctx 200 'application/json' (@{ ok = $true; question = $question; job = $askJob; state = 'running' } | ConvertTo-Json)
        }
        '^/api/ask/([0-9a-f]{12})$' {
          $askId = $Matches[1]
          $askF = Join-Path $script:AskDir "$askId.json"
          if (Test-Path -LiteralPath $askF) {
            $askRaw = [IO.File]::ReadAllText($askF, [Text.Encoding]::UTF8)
            # Never hand a client a body that is not the JSON it was promised.
            # A job file can be truncated or corrupted by a crash, a full disk, or
            # outside interference, and this route previously echoed whatever was
            # on disk with a JSON content-type - so the poller received
            # unparseable bytes and reported "lost contact with the console",
            # which describes the wrong thing. /api/state already refuses to serve
            # a non-JSON payload for the same reason; a job result is the same
            # kind of contract and gets the same treatment.
            $askOk = $false
            try { $null = $askRaw | ConvertFrom-Json; $askOk = $true } catch { $askOk = $false }
            if (-not $askOk) {
              Send $ctx 200 'application/json' (@{ ok = $true; state = 'error'; error = 'this job result is unreadable - it was truncated or corrupted on disk' } | ConvertTo-Json)
              break
            }
            # A 'running' marker older than the job's own timeout means the job
            # died with the server and the file is all that survived it. Say so
            # here rather than leaving the page polling toward its own 4-minute
            # cap on a question that stopped existing minutes ago. The marker is
            # written before the job starts, so its age is the job's age.
            if ($askRaw -match '"state"\s*:\s*"running"') {
              $askAge = ((Get-Date) - (Get-Item -LiteralPath $askF).LastWriteTime).TotalSeconds
              if ($askAge -gt 240) {
                Send $ctx 200 'application/json' (@{ ok = $true; state = 'error'; error = "abandoned after $([math]::Round($askAge))s - the server restarted while this was answering" } | ConvertTo-Json)
                break
              }
            }
            Send $ctx 200 'application/json' $askRaw
          } else {
            # The RUNNING marker is written before the job starts, so reaching
            # here means the server restarted and lost the job. Say that plainly
            # rather than leave the page waiting forever.
            Send $ctx 200 'application/json' (@{ ok = $true; state = 'error'; error = 'this job no longer exists - the server restarted mid-answer' } | ConvertTo-Json)
          }
        }
        '^/api/journal$' {
          # The audit trail the bridges already write. Served from a CACHE that a
          # background job refreshes, so this route is a file read and cannot
          # block the listener no matter how the Docker daemon is behaving. The
          # response shape is unchanged.
          $which = 'hermes'
          if ($ctx.Request.QueryString -match 'b=antigravity') { $which = 'antigravity' }
          $jcache = Join-Path $script:AskDir "journal-$which.json"
          $jflag  = Join-Path $script:AskDir "journal-$which.running"
          # Refresh unless one is already in flight. The flag is aged out, so a
          # job that died without clearing it cannot wedge the endpoint forever.
          $busy = $false
          if (Test-Path $jflag) {
            $flagAge = ((Get-Date) - (Get-Item -LiteralPath $jflag).LastWriteTime).TotalSeconds
            $busy = ($flagAge -lt 60)
          }
          if (-not $busy) { try { Start-JournalRefresh -Which $which } catch { } }
          if (Test-Path $jcache) {
            $jbody = [IO.File]::ReadAllText($jcache, [Text.Encoding]::UTF8)
            $jok = $false
            try { $null = $jbody | ConvertFrom-Json; $jok = $true } catch { $jok = $false }
            # Echo the cached body only if it is still valid JSON - the same
            # contract the job routes use, because handing a client bytes that
            # are not the JSON it was promised helps nobody.
            if ($jok) { Send $ctx 200 'application/json' $jbody; break }
          }
          Send $ctx 200 'application/json' (@{ ok = $true; bridge = "minimax-$which-bridge"; count = 0; records = @(); refreshing = $true } | ConvertTo-Json -Depth 6)
        }
        '^/api/action$' {
          $body = @{ id = '' }
          if ($ctx.Request.HasEntityBody) {
            $raw = (New-Object IO.StreamReader($ctx.Request.InputStream)).ReadToEnd()
            if ($raw.Trim()) {
              # A malformed body is the CALLER's error, so it answers 400. Left
              # unguarded it became a 500 carrying a raw ArgumentException, which
              # reports a broken dashboard to a client that merely sent bad JSON
              # - and, per the same reasoning as /api/state, a monitoring
              # endpoint that returns garbage stops monitoring when it matters.
              try { $body = $raw | ConvertFrom-Json }
              catch { $body = @{ id = '' } }
            }
          }
          $id = $body.id
          if (-not $ACTIONS.ContainsKey($id)) {
            Send $ctx 400 'application/json' (@{ ok = $false; error = "unknown action '$id'"; allowed = $ACTIONS.Keys } | ConvertTo-Json)
            break
          }
          # ASYNC, and the reason is measured rather than theoretical. `doctor`
          # takes ~12 s on this machine. Run inline, even behind a 120 s cap, it
          # froze a concurrent /api/state for 10 030 ms - one probe hit its own
          # 10 s client timeout. A cap makes the freeze BOUNDED; it does not
          # remove it. The command is arbitrary - a doctor, a compose check, a
          # docker exec - so the work belongs off the request thread entirely,
          # exactly as the analyst's does.
          $cmd = $ACTIONS[$id]
          $actJob = Start-ActionJob -Command $cmd -TimeoutSec $script:ActionTimeoutSec -WorkDir $ROOT
          Send $ctx 200 'application/json' (@{ ok = $true; id = $id; job = $actJob; state = 'running' } | ConvertTo-Json)
        }
        '^/api/action/([0-9a-f]{12})$' {
          $actId = $Matches[1]
          $actF = Join-Path $script:AskDir "act-$actId.json"
          if (Test-Path -LiteralPath $actF) {
            $actRaw = [IO.File]::ReadAllText($actF, [Text.Encoding]::UTF8)
            # Same contract as the analyst route: a result that is not JSON is
            # reported, never echoed under a JSON content-type.
            $actOk = $false
            try { $null = $actRaw | ConvertFrom-Json; $actOk = $true } catch { $actOk = $false }
            if (-not $actOk) {
              Send $ctx 200 'application/json' (@{ ok = $true; state = 'error'; error = 'this action result is unreadable - it was truncated or corrupted on disk' } | ConvertTo-Json)
              break
            }
            if ($actRaw -match '"state"\s*:\s*"running"') {
              $actAge = ((Get-Date) - (Get-Item -LiteralPath $actF).LastWriteTime).TotalSeconds
              if ($actAge -gt ($script:ActionTimeoutSec + 60)) {
                Send $ctx 200 'application/json' (@{ ok = $true; state = 'error'; error = "abandoned after $([math]::Round($actAge))s - the server restarted while this was running" } | ConvertTo-Json)
                break
              }
            }
            Send $ctx 200 'application/json' $actRaw
          } else {
            Send $ctx 200 'application/json' (@{ ok = $true; state = 'error'; error = 'this job no longer exists - the server restarted mid-action' } | ConvertTo-Json)
          }
        }
        default { Send $ctx 404 'text/plain' 'not found' }
      }
    } catch {
      $why = "$($_.Exception.GetType().FullName): $($_.Exception.Message)"
      Write-Host "  ERROR on $path -> $why" -ForegroundColor Red
      $msg = @{ ok = $false; error = $why; path = $path } | ConvertTo-Json
      try { Send $ctx 500 'application/json' $msg } catch { Write-Host "  (could not send: $($_.Exception.Message))" -ForegroundColor Red }
    }
  }
}
finally {
  $listener.Stop()
  $listener.Close()
}