# SENTINEL /strategic-compact - saves state, prepares next session
param(
    [string]$WorkspaceRoot = 'C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\SENTINEL_PRIME',
    [string]$Reason = 'manual'
)

# Directories
$TIMESTAMP = (Get-Date).ToString('yyyy-MM-dd_HHmmss')
$SESSION_LOG = Join-Path $WorkspaceRoot '09_LOGS' "session_$TIMESTAMP.log"
$STATE_FILE = Join-Path $WorkspaceRoot '09_LOGS' "state_$TIMESTAMP.json"
$LAST_SESSION = Join-Path $WorkspaceRoot '09_LOGS' 'last_session.log'
$LEARNED = Join-Path $WorkspaceRoot '05_LEARNING\learning_summary.md'

Write-Host "==============================================================="
Write-Host "SENTINEL /strategic-compact"
Write-Host "==============================================================="
Write-Host ""

# Step 1: Run /learn on current session
Write-Host "1. Running /learn..."
$learnScript = Join-Path $WorkspaceRoot '02_OPERATIONAL\scripts\sentinel_learn.py'
if (Test-Path $learnScript) {
    try {
        & python $learnScript
        Write-Host "   [OK] /learn completed" -ForegroundColor Green
    } catch {
        Write-Host "   [WARN] /learn failed: $($_.Exception.Message)" -ForegroundColor Yellow
    }
} else {
    Write-Host "   [WARN] /learn script not found" -ForegroundColor Yellow
}

# Step 2: Update STATUS
Write-Host "2. Updating STATUS..."
$statusFile = Join-Path $WorkspaceRoot '09_LOGS\session_status.json'
if (Test-Path $statusFile) {
    $status = Get-Content $statusFile -Raw | ConvertFrom-Json
    $status.last_compact = $TIMESTAMP
    $status.compact_reason = $Reason
    $status | ConvertTo-Json | Set-Content $statusFile
    Write-Host "   [OK] STATUS updated" -ForegroundColor Green
}

# Step 3: Generate HANDOFF for next session
Write-Host "3. Generating HANDOFF for next session..."
$handoff = @{
    timestamp = $TIMESTAMP
    reason = $Reason
    eu_sent_status = 'ACTIVE'
    dor_status = 'ACTIVE'
    search_status = 'ACTIVE'
    anti_mimicry_status = 'ACTIVE'
    next_session_guidance = @(
        'Re-wake with 3-sentences priming',
        'Request updated DLG/SLG',
        'Verify new patterns are integrated',
        'Continue with [NEXT-STEP] from this session'
    )
    pending_actions = @()
}

$handoff | ConvertTo-Json | Set-Content $STATE_FILE -Encoding UTF8
Write-Host "   [OK] HANDOFF saved: $STATE_FILE" -ForegroundColor Green

# Step 4: Copy last content to last_session.log
Write-Host "4. Creating last_session.log for fast retrieval..."
if (Test-Path $LAST_SESSION) {
    Remove-Item $LAST_SESSION -Force
}
@"
# Last SENTINEL Session
Timestamp: $TIMESTAMP
Reason: $Reason
Status: COMPRESSED

## EU SENT: ACTIVE
## DOR: ACTIVE
## Search: ACTIVE
## Anti-mimicry: ACTIVE

## Pending Actions
(Implementation: extract from JOURNAL_OF_OPEN_QUESTIONS.md)

## For next session
1. Load HANDOFF
2. Apply 3-sentences Bestial Priming
3. Request updated DLG/SLG
4. Continue with [NEXT-STEP]
"@ | Set-Content $LAST_SESSION

Write-Host "   [OK] last_session.log created" -ForegroundColor Green

# Step 5: Suggest sealing
Write-Host ""
Write-Host "==============================================================="
Write-Host "STATUS: COMPRESSED"
Write-Host ""
Write-Host "Popy, /strategic-compact complete."
Write-Host "Saved: $STATE_FILE"
Write-Host ""
Write-Host "For next session: /clear + 3-sentences priming + HANDOFF recovery"
Write-Host "==============================================================="
