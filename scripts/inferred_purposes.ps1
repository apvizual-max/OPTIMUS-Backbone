# inferred_purposes.ps1
# Generates inferred purposes for the 176 personal skills with empty descriptions,
# by inferring purpose from the skill name. Marked SPECULATION in the output.
# Appends a "## Inferred purposes (SPECULATION)" section to the classifier file.

$ErrorActionPreference = 'Stop'

$out = 'C:\Users\apviz\.minimax-agent\projects\70_CONNECTORS\70_personal_skill_index.md'
# Use $env:TEMP (same as rebuild-classifier.ps1) so the two scripts agree on any profile.
# If the CSV is missing (rebuild-classifier cleans it up), regenerate it from the skills tree.
$csv = Join-Path $env:TEMP 'personal_skills_index.csv'
if (-not (Test-Path $csv)) {
  $pskills = 'C:\Users\apviz\.minimax\skills'
  $csb = [System.Text.StringBuilder]::new()
  [void]$csb.AppendLine('dir,desc_first_400')
  foreach ($d in Get-ChildItem -Path $pskills -Directory -Force -ErrorAction SilentlyContinue) {
    $skillFile = Join-Path $d.FullName 'SKILL.md'
    if (-not (Test-Path $skillFile)) { continue }
    $skLines = Get-Content $skillFile -TotalCount 30 -ErrorAction SilentlyContinue
    if ($null -eq $skLines) { continue }
    $dsc = ''
    $collecting = $false
    foreach ($line in $skLines) {
      if ($line -match '^description:\s*(.+)$') { $dsc = $matches[1].Trim(); $collecting = $false }
      elseif ($line -match '^description:\s*(>|\|)?\s*$') { $collecting = $true }
      elseif ($collecting -and $line -match '^\s+(.+)$') {
        $apnd = $matches[1].Trim() -replace '^[-`"'']\s*',''
        if ($apnd.Length -gt 0) { $dsc += ' ' + $apnd }
      }
    }
    if ($dsc.Length -gt 400) { $dsc = $dsc.Substring(0, 397) + '...' }
    $dscSafe = $dsc -replace '"','""' -replace ',',';'
    $nmSafe = $d.Name -replace '"','""'
    [void]$csb.AppendLine('"' + $nmSafe + '","' + $dscSafe + '"')
  }
  [System.IO.File]::WriteAllText($csv, $csb.ToString(), [System.Text.Encoding]::UTF8)
}

# Collect empty-desc skills
$empties = @()
$lines = Get-Content $csv -ErrorAction SilentlyContinue
for ($i = 1; $i -lt $lines.Count; $i++) {
  $line = $lines[$i]
  $match = [regex]::Match($line, '^"((?:[^"]|"")*)","((?:[^"]|"")*)"$')
  if (-not $match.Success) { continue }
  $dir = $match.Groups[1].Value -replace '""','"'
  $desc = $match.Groups[2].Value -replace '""','"'
  if ($desc.Length -lt 5) { $empties += $dir }
}

# Heuristic name → inferred purpose mapping
$map = @{
  'acc-thinker'              = 'Accounting/finance thinking and decision frameworks (SPECULATION - inferred from name "acc" + "thinker").'
  'adhd-vs-action'           = 'Comparing ADHD-style hyperactive cognition vs deliberate action-taking (SPECULATION).'
  'advanced-prompting'      = 'Advanced prompt-engineering patterns and frameworks for LLM/agent use (SPECULATION).'
  'agent-chatrooms'         = 'Designing or operating multi-agent chat-room / collaborative-agent topology (SPECULATION).'
  'agentic-pro-design'      = 'Agentic product / design workflow with auto-design discipline (SPECULATION).'
  'agentmemory'             = 'Agent memory architecture - episodic / semantic / procedural memory layout (SPECULATION).'
  'api-gateway'             = 'API gateway design - routing, auth, rate-limiting, observability (SPECULATION).'
  'arabic-supreme-research' = 'Arabic-language deep research at high rigor / "supreme" depth (SPECULATION).'
  'architects-brain'        = 'Architect / principal-engineer mindset - system-design rationale (SPECULATION).'
  'archon-operator'         = 'Archon-style operator pattern - top-level orchestrator for sub-agents (SPECULATION).'
  'assessment-coach'        = 'Coaching on assessments / evaluations / rubrics (SPECULATION).'
  'ats-cargo-objetivo'      = 'ATS-targeted resume / job-application targeting (Portuguese: "cargo objetivo" = objective position) (SPECULATION).'
  'ats-cv-evaluator'        = 'ATS-aware CV / resume scoring and feedback (SPECULATION).'
  'audit-methodology'       = 'Audit methodology - formal review frameworks for systems / processes (SPECULATION).'
  'aws-skills'              = 'AWS cloud skills - EC2, S3, IAM, Lambda, etc. (SPECULATION - likely MiniMax-bundled AWS suite).'
  'blogger-genius-architect'= 'Blog / content-site architecture and copy engineering (SPECULATION).'
  'book-editor'             = 'Book-length manuscript editing - structure, pacing, voice (SPECULATION).'
  'buffett'                 = 'Warren Buffett investment style - value investing, moat analysis, long-term thinking (SPECULATION).'
  'bulk-email-hyperpersonal'= 'Bulk email with per-recipient hyper-personalization at scale (SPECULATION).'
  'c-cpp-programmer'        = 'Deep C / C++ programming - systems-level work, memory, pointers (SPECULATION).'
  'career-pivot-roadmap'    = 'Career-pivot planning - transition paths, skill mapping, timelines (SPECULATION).'
  'cavecrew'                = 'Cavecrew programming style - terse / minimal-output variant (SPECULATION, see caveman-*).'
  'caveman'                 = 'Caveman programming style - minimal, terse, no-fluff output (SPECULATION).'
  'caveman-commit'          = 'Caveman commit-message style - minimal git commit messages (SPECULATION).'
  'caveman-compress'        = 'Caveman compression - minimal responses / token compression (SPECULATION).'
  'caveman-help'            = 'Caveman help - terse, blunt answers without preamble (SPECULATION).'
  'caveman-review'          = 'Caveman code-review style - terse, blunt feedback (SPECULATION).'
  'caveman-stats'           = 'Caveman statistics - minimal-numbers reporting style (SPECULATION).'
  'chart-of-accounts'       = 'Accounting chart of accounts - GAAP / IFRS structure (SPECULATION).'
  'cinematic-micro-film'    = 'Cinematic short-film production pipeline (SPECULATION).'
  'clap-dev'                = 'clap-rs / CLI development for Rust (SPECULATION).'
  'code-reviewer'           = 'Code-review skill - produces structured review output (SPECULATION).'
  'comprehensive-seo-audit' = 'SEO site audit - comprehensive on-page + technical + content (SPECULATION).'
  'comprehensive-valuation' = 'Comprehensive financial valuation (DCF, comps, precedents) (SPECULATION).'
  'computer-forensics'      = 'Computer forensics - evidence acquisition, chain of custody (SPECULATION).'
  'context-progress'       = 'Conversation / context-window progress tracking (SPECULATION).'
  'corpus-linguist'         = 'Corpus linguistics - frequency analysis, collocations, n-grams (SPECULATION).'
  'crud-rest-controller'    = 'CRUD REST controller scaffolding (SPECULATION).'
  'crypto-chart-analyst'    = 'Crypto price-chart analysis (SPECULATION).'
  'csv-summarizer'          = 'CSV summarization - statistics + natural-language summary (SPECULATION).'
}

# Render inferred-purpose section as text lines
$sb = [System.Text.StringBuilder]::new()
[void]$sb.AppendLine('')
[void]$sb.AppendLine('---')
[void]$sb.AppendLine('')
[void]$sb.AppendLine('## Inferred purposes (SPECULATION) for the ' + $empties.Count + ' skills with empty descriptions')
[void]$sb.AppendLine('')
[void]$sb.AppendLine('**Date**: ' + (Get-Date -Format 'yyyy-MM-dd HH:mm'))
[void]$sb.AppendLine('**Source**: Inferred from skill name only (no SKILL.md description available). All entries marked SPECULATION.')
[void]$sb.AppendLine('**How to fix permanently**: Popy can open each skill SKILL.md and add a `description:` line - the next rebuild (cron weekly) will pick it up and remove the inference.')
[void]$sb.AppendLine('')

$matched = @()
foreach ($name in ($empties | Sort-Object)) {
  if ($map.ContainsKey($name)) {
    $line = '- `' + $name + '` - ' + $map[$name]
    [void]$sb.AppendLine($line)
    $matched += $name
  }
}

# For unmatched names, use generic pattern inference
$unmatched = $empties | Where-Object { $_ -notin $matched }
[void]$sb.AppendLine('')
[void]$sb.AppendLine('### Generic pattern matches (' + $unmatched.Count + ')')
[void]$sb.AppendLine('')
[void]$sb.AppendLine('Patterns detected: `-expert`, `-specialist`, `-master`, `-agent`, `-coach`, `-advisor`, `-operator`, `-reviewer`, `-generator`, `-analyzer`, `-auditor`, `-engineer`, `-architect`.')
[void]$sb.AppendLine('')
foreach ($name in ($unmatched | Sort-Object)) {
  $parts = $name -split '-'
  $verb = ''
  $topic = ''
  if ($parts.Count -ge 2) {
    $verb = $parts[-1]
    $topic = ($parts[0..($parts.Count - 2)] -join ' ')
  } else {
    # Single-word skill name: no verb/topic split available.
    # Use the whole name as the topic so the row is never vacuous.
    $topic = $name
    $verb = ''
  }
  # Use single-quoted format string with -f to avoid PowerShell backtick escape bugs.
  # (A literal backtick inside a double-quoted PowerShell string is an escape char; `v is vertical tab.)
  if ($verb -eq '') {
    $purpose = 'Skill for {0} (SPECULATION - inferred from single-word skill name; load on demand to discover actual purpose).' -f $topic
  } else {
    $purpose = 'Specialized {0} skill for {1} (SPECULATION - inferred from name pattern verb + topic; load on demand to discover actual purpose).' -f $verb, $topic
  }
  $line = '- `' + $name + '` - ' + $purpose
  [void]$sb.AppendLine($line)
}
[void]$sb.AppendLine('')

Add-Content -Path $out -Value $sb.ToString() -Encoding UTF8
Write-Output "Appended inferred-purpose entries to $out"
Write-Output "  Direct matches: $($matched.Count)"
Write-Output "  Pattern matches: $($unmatched.Count)"
Write-Output "  Total empty-desc skills annotated: $($empties.Count)"
