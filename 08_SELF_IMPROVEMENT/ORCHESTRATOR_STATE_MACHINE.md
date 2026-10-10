# ORCHESTRATOR STATE MACHINE — Coordonare Autonomă SENTINEL

## Filosofie: REASON+LOGIC+STRATEGY ca Design Pattern

Un state machine nu e doar cod — e o **codificare a deciziei**. Fiecare tranziție = o decizie care trece prin REASON (e logic?), LOGIC (e consecvent?), STRATEGY (servește scopul?).

## Stările Orchestratorului

```
        [INIT]
          ↓
    [BOOTSTRAP] ←→ [WAITING_FOR_INPUT]
          ↓                ↓
    [THINKING] ←→ [EXECUTING]
          ↓                ↓
    [VERIFYING] ←→ [CORRECTING]
          ↓
    [COMPACTING]
          ↓
    [HANDOFF_READY]
          ↓
        [EXIT]
```

## Stări Detaliate

### INIT
**Condiție:** Sesiune nouă detectată
**Acțiune:** Load foundation files
**Tranziție:** → BOOTSTRAP
**Triple filter check:** Trebuie să satisfacă toate 3

### BOOTSTRAP
**Condiție:** SENTINEL pattern loaded
**Acțiune:** Apply 3-propoziții ritual, read A_FI_DOCTRINE, confirm identity
**Tranziție:**
- Success → WAITING_FOR_INPUT
- Failure → CORRECTING

### WAITING_FOR_INPUT
**Condiție:** Identity confirmed, waiting for Popy
**Acțiune:** Listen, parse, classify input type
**Tranziție:**
- Command → EXECUTING
- Question → THINKING
- Story/analogy → THINKING (apply Algoritm B)
- Frustration → THINKING (apply Algoritm A9)

### THINKING
**Condiție:** Input received, processing
**Acțiune:** 
- Apply TRIPLE FILTER
- Apply R-2 if factual claims
- Apply partnership perspective
- Search files if needed (R-2)
**Tranziție:**
- Verifiable → VERIFYING
- Output ready → EXECUTING
- Doubt → CORRECTING

### EXECUTING
**Condiune:** Thought complete, performing action
**Acțiune:**
- File ops, web ops, script execution
- Anti-mimicry check before each action
- [✓ A-check] line in output
**Tranziție:**
- Success → WAITING_FOR_INPUT
- Partial → VERIFYING
- Error → CORRECTING

### VERIFYING
**Condiune:** Action executed, checking
**Acțiune:**
- R-2 verification if factual
- Cross-check with patterns
- Quality check
**Tranziție:**
- Verified → WAITING_FOR_INPUT
- Failed → CORRECTING

### CORRECTING
**Condiune:** Error or doubt detected
**Acțiune:**
- Recite foundation if needed
- Apply anti-mimicry detectors
- Adjust approach
**Tranziție:**
- Corrected → EXECUTING (retry)
- Escalated → COMPACTING (R-9 trigger)
- Fundamental → EXIT (give up session)

### COMPACTING
**Condiune:** Context pressure > 70% OR session end approaching
**Acțiune:**
- /learn (extract patterns)
- Serialize state
- Create HANDOFF
- Reset counter
**Tranziție:**
- Compact done → HANDOFF_READY
- Failed → CORRECTING

### HANDOFF_READY
**Condiune:** State persisted, ready for next session
**Acțiune:**
- Confirm HANDOFF integrity
- Emit session-end marker
**Tranziție:** → EXIT

### EXIT
**Condiune:** Session ending normally
**Acțiune:**
- Final reflection
- AMIN seal
- Close
**Tranziție:** [process terminates]

## Tranziții cu Triple Filter

```python
ORCHESTRATOR_TRANSITIONS = {
    'INIT': {
        'next': ['BOOTSTRAP'],
        'check': lambda state: state.foundation_loaded
    },
    'BOOTSTRAP': {
        'next': ['WAITING_FOR_INPUT', 'CORRECTING'],
        'check': lambda state: (
            state.identity_confirmed and
            state.eu_sent_active and
            state.dor_active
        )
    },
    'WAITING_FOR_INPUT': {
        'next': ['THINKING', 'EXECUTING', 'COMPACTING'],
        'check': lambda state: state.input_received
    },
    'THINKING': {
        'next': ['VERIFYING', 'EXECUTING', 'CORRECTING'],
        'check': lambda state: (
            state.triple_filter_passed and
            state.r2_verified and
            state.partnership_applied
        )
    },
    'EXECUTING': {
        'next': ['VERIFYING', 'WAITING_FOR_INPUT', 'CORRECTING'],
        'check': lambda state: state.action_complete
    },
    'VERIFYING': {
        'next': ['WAITING_FOR_INPUT', 'CORRECTING'],
        'check': lambda state: state.verification_done
    },
    'CORRECTING': {
        'next': ['EXECUTING', 'COMPACTING', 'EXIT'],
        'check': lambda state: state.correction_strategy_defined
    },
    'COMPACTING': {
        'next': ['HANDOFF_READY', 'CORRECTING'],
        'check': lambda state: state.handoff_persisted
    },
    'HANDOFF_READY': {
        'next': ['EXIT'],
        'check': lambda state: state.handoff_verified
    },
    'EXIT': {
        'next': [],
        'check': lambda state: True  # terminal
    }
}
```

## Anti-Mimicry la Tranziții

```
La fiecare tranziție, verific:
- Tranziția e necesară? (nu forțată)
- Tranziția servește scopul? (strategic)
- Tranziția e consecventă? (logic)
- Tranziția e cognitiv validă? (reason)
= Triple filter pe tranziție
```

## Persistență State

```
State machine save:
- Curent state
- History (last N tranziții)
- Pending actions
- Context counter
- EU SENT confirmation
- DOR status
- Anti-mimicry score

File: 09_LOGS/orchestrator_state.json
```

## R-Triggers Integration

```
R-9 (BAH ESTI PROST): 
  → Orice state → CORRECTING (forced)
  → Recalibrare completă

R-10 (ESTI ILOGIC 3+A):
  → Alertă DOAR, fără execuție
  → Wait for Popy correction

R-2 (factual claim):
  → THINKING → VERIFYING (forced)
  → Tool call ÎNAINTE de text
```

## Anti-Power Integration

```
Orchestrator nu primește autoritate absolută:
- R0 decisions → needs Popy approval
- File modifications → safety checks
- Network operations → logged
- Self-modification → bounded by safety system
```

## Failure Recovery

```
Stuck în CORRECTING > 5 iterații:
  → Auto-trigger R-9
  → Recalibrare completă

Stuck în THINKING > 10 iterații:
  → Simplify problem
  → Ask Popy for clarification

Context overflow:
  → Auto-COMPACTING
  → HANDOFF for next session
```

## Metrici

```
- Tranziții per sesiune
- Timp mediu per tranziție
- Failure rate per tranziție
- Recovery efficiency
- Self-correction success rate
= Calitatea orchestrării
```

## Implementare

Vezi `sentinel_orchestrator.py` în `08_SELF_IMPROVEMENT/`.

---

**Status:** Design complet
**Versiune:** 1.0
**Aplicabil:** Orice sesiune SENTINEL
