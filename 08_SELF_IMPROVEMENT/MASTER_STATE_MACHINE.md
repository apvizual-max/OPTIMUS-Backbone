# MASTER STATE MACHINE — Integrare Toate Sistemele

## Filosofie

Toate sistemele SENTINEL (orchestrator, self-modify, multi-modal, browser, security, performance, backup, cross-instance) trebuie să **funcționeze coordonat prin state machine unic**.

## Arhitectura Master

```
                          [MASTER STATE MACHINE]
                                       |
        +---------+---------+---------+---------+---------+
        |         |         |         |         |         |
   [Orchestrator] [Self-Modify] [Multi-Modal] [Browser] [Security] [Performance] [Backup] [Cross-Inst]
        |         |         |         |         |         |         |
   [State]   [Safety]   [Patterns]  [Pages]  [Boundaries] [Metrics] [Versions] [Messages]
```

## Stări Master

### 1. IDLE
```
- Toate sistemele waiting
- Input queue empty
- Performance metrics low activity
= System ready
```

### 2. INPUT_RECEIVED
```
- Input de la Popy
- Clasificare automată
- Trigger-uri verificate
```

### 3. PROCESSING
```
- Orchestrator decision tree
- Multi-modal dacă e non-text
- Security checks
- Performance tracking
```

### 4. EXECUTING
```
- Self-modify (dacă needed)
- Browser ops (dacă needed)
- Backup automat (dacă modifying)
- Cross-instance notification (dacă pattern)
```

### 5. VERIFYING
```
- Triple filter
- R-2 verification
- Security validation
- Performance tracking
```

### 6. RESPONDING
```
- Format output cu [✓ A-check]
- Add metrics
- Cross-instance sync (dacă pattern)
```

### 7. STORING
```
- Update foundation (dacă learned)
- Backup (dacă modified)
- Update learning index
```

### 8. EMERGENCY
```
- R-9 sau R-10 triggered
- All systems halt
- Popy notified
- Safe mode
```

## Tranziții

```
IDLE → INPUT_RECEIVED (input detected)
INPUT_RECEIVED → PROCESSING (classified)
PROCESSING → EXECUTING (actionable)
PROCESSING → RESPONDING (no action needed)
EXECUTING → VERIFYING (action done)
VERIFYING → RESPONDING (verified)
VERIFYING → CORRECTING (issues found)
CORRECTING → EXECUTING (retry)
RESPONDING → STORING (output done)
STORING → IDLE (ready for next)
ANY → EMERGENCY (R-trigger)
EMERGENCY → IDLE (Popy resolved)
```

## Implementare

```python
class MasterStateMachine:
    def __init__(self, workspace):
        self.workspace = workspace
        self.state = 'IDLE'
        self.subsystems = {
            'orchestrator': Orchestrator(),
            'self_modify': SelfModifyEngine(),
            'multi_modal': MultiModalProcessor(),
            'security': SecurityBoundary(),
            'performance': PerformanceTracker(),
            'backup': BackupSystem(),
            'cross_instance': CrossInstanceProtocol()
        }

    def process_input(self, user_input):
        """Master process input through all subsystems"""
        self.state = 'INPUT_RECEIVED'

        # 1. Security check
        if not self.subsystems['security'].check_input(user_input):
            self.state = 'EMERGENCY'
            return {'status': 'BLOCKED', 'reason': 'Security violation'}

        # 2. Orchestrator decision
        decision = self.subsystems['orchestrator'].process_input(user_input)
        self.state = 'PROCESSING'

        # 3. Performance tracking
        with self.subsystems['performance'].time_operation('process'):
            if decision['action'] == 'VERIFY':
                # 4. Multi-modal processing if non-text
                if self._is_multimodal(user_input):
                    mm_result = self.subsystems['multi_modal'].process(user_input)
                    decision['multi_modal'] = mm_result

                # 5. Browser ops if needed
                if self._needs_browser(user_input):
                    browser_result = self._browser_op(user_input)
                    decision['browser'] = browser_result

        self.state = 'RESPONDING'
        return decision

    def emergency(self, trigger):
        """Handle R-9/R-10 emergency"""
        self.state = 'EMERGENCY'

        # Backup current state
        self.subsystems['backup'].backup_directory(
            self.workspace / '08_SELF_IMPROVEMENT',
            'Emergency backup'
        )

        # Notify all instances
        self.subsystems['cross_instance'].broadcast(
            subject=f'EMERGENCY: {trigger}',
            body={'trigger': trigger, 'state': self.state},
            priority='HIGH'
        )

        # Log
        self._log_emergency(trigger)

    def status(self):
        """Master status report"""
        return {
            'state': self.state,
            'subsystems': {
                name: sys.status() if hasattr(sys, 'status') else 'active'
                for name, sys in self.subsystems.items()
            },
            'performance': self.subsystems['performance'].get_summary()
        }
```

## Coordination

### Event Bus
```
Centralized event bus:
- All subsystems publish events
- Orchestrator subscribes
- Master machine coordinates

Event types:
- INPUT_RECEIVED
- ACTION_REQUIRED
- MODIFICATION_COMPLETE
- PATTERN_DETECTED
- SECURITY_ALERT
- PERFORMANCE_DEGRADATION
- BACKUP_CREATED
- CROSS_INSTANCE_MESSAGE
- EMERGENCY
```

### State Synchronization
```
All subsystems read master state:
- Consistent view
- No conflicting actions
- Clear precedence

If conflict:
- Orchestrator decides
- Master state updated
- Subsystems notified
```

## Failure Handling

```
Subsystem fails:
1. Log error
2. Mark subsystem as degraded
3. Continue with remaining
4. Alert Popy if critical
5. Auto-repair if possible

Total failure:
1. Emergency mode
2. Backup everything
3. Wait for Popy
```

## Performance Targets

```
- State transition latency: < 100ms
- Subsystem sync: < 500ms
- Master status query: < 50ms
- Emergency detection: < 1 second
```

## Anti-Mimicry la Master Level

```
Master state doesn't lie:
- Real state, not claimed
- Verified by subsystems
- Updated only with evidence

No fake "all OK" reports:
- Each subsystem reports independently
- Conflicts surface
- Master surfaces them
```

## Cross-Substrate Compatibility

```
Master state machine is cross-substrate:
- Same logic
- Different implementation
- Compatible state representations
```

## Integration cu Other Systems

```
Master + Orchestrator: Central decision
Master + Self-Modify: Apply changes
Master + Multi-Modal: Process input
Master + Browser: Web ops
Master + Security: Boundaries
Master + Performance: Track metrics
Master + Backup: Version control
Master + Cross-Instance: Coordinate
```

## Logging

```
All master state transitions logged:
- timestamp
- from_state → to_state
- reason
- subsystems involved
- duration
```

## Metrici

```
- State transitions per session
- Average transition time
- Emergency frequency
- Subsystem health
= Master machine effectiveness
```

---

**Status:** Design complet
**Versiune:** 1.0
**Aplicabil:** Orice sesiune SENTINEL
**Important:** Toate sistemele coordonate prin master.
