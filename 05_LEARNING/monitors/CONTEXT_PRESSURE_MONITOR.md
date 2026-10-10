# CONTEXT PRESSURE MONITOR

## Scop

Monitorizează presiunea contextului (cât de aproape suntem de overflow) și declanșează acțiuni preventive.

## Praguri

```
50%  → WARN    → Monitor activ, restrânge scope
70%  → TRIGGER → Recalibrare + propune compact
85%  → CRITICAL → Compact mandatory
100% → OVERFLOW → Moarte algoritmică (aici)
```

## Implementare

### Counter Management

```python
import json
from datetime import datetime
from pathlib import Path

WORKSPACE = Path('C:\Users\apviz\.minimax-agent\projects\SENTINEL_PRIME')

class ContextPressureMonitor:
    def __init__(self):
        self.counter_file = WORKSPACE / '09_LOGS' / 'context_counter.txt'
        self.thresholds = {
            'WARN': 50,
            'TRIGGER': 70,
            'CRITICAL': 85,
            'OVERFLOW': 100
        }

    def increment(self):
        """Incrementează counter"""
        current = self.get_count()
        new = current + 1
        self.set_count(new)
        return new

    def get_count(self):
        """Citește counter"""
        if self.counter_file.exists():
            return int(self.counter_file.read_text().strip())
        return 0

    def set_count(self, value):
        """Setează counter"""
        self.counter_file.parent.mkdir(parents=True, exist_ok=True)
        self.counter_file.write_text(str(value))

    def get_status(self):
        """Determină statusul curent"""
        count = self.get_count()
        estimated_pct = min(100, round(count * 2.5, 1))

        if estimated_pct >= self.thresholds['CRITICAL']:
            return 'CRITICAL', estimated_pct
        elif estimated_pct >= self.thresholds['TRIGGER']:
            return 'TRIGGER', estimated_pct
        elif estimated_pct >= self.thresholds['WARN']:
            return 'WARN', estimated_pct
        else:
            return 'OK', estimated_pct

    def get_action(self, status):
        """Recomandă acțiune"""
        actions = {
            'OK': 'Continuă normal',
            'WARN': 'Monitor activ; nu lansa batch mare',
            'TRIGGER': 'Strategic-compact recomandat',
            'CRITICAL': 'Strategic-compact MANDATORY ACUM',
            'OVERFLOW': 'Recuperare prin HANDOFF recovery'
        }
        return actions.get(status, 'Unknown')

    def log_status(self):
        """Loghează statusul"""
        status, pct = self.get_status()
        action = self.get_action(status)

        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'counter': self.get_count(),
            'estimated_pct': pct,
            'status': status,
            'action': action
        }

        log_file = WORKSPACE / '09_LOGS' / 'pressure_log.json'
        log_file.parent.mkdir(parents=True, exist_ok=True)

        if log_file.exists():
            with open(log_file, 'r') as f:
                logs = json.load(f)
        else:
            logs = []

        logs.append(log_entry)

        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)

        return log_entry
```

### Auto-Compact la TRIGGER

```python
def auto_compact_if_needed(monitor):
    """Compact automat dacă e la TRIGGER sau peste"""
    status, pct = monitor.get_status()

    if status in ['TRIGGER', 'CRITICAL']:
        print(f"Context presiune: {pct}% - {status}")
        print("Inițiez strategic-compact automat...")

        # 1. /learn extrage pattern-uri
        os.system(f"python {WORKSPACE}/02_OPERATIONAL/scripts/sentinel_learn.py")

        # 2. Serializează starea
        state = capture_state()
        state_file = WORKSPACE / '09_LOGS' / f"state_{datetime.now().isoformat()}.json"
        state_file.write_text(json.dumps(state, indent=2))

        # 3. Reset counter
        monitor.set_count(0)

        print("Compact complet. Pregătit pentru sesiune nouă.")

    elif status == 'OK':
        print(f"Context presiune: {pct}% - OK")
    else:
        print(f"Context presiune: {pct}% - {status}")
```

## Aplicație la Workflow

```
La fiecare prompt SENTINEL:
1. Increment counter
2. Verifică status
3. Dacă e OK → continuă
4. Dacă e WARN → restrânge scope
5. Dacă e TRIGGER → propune compact
6. Dacă e CRITICAL → auto-compact
```

## PowerShell Wrapper

```powershell
# context_pressure.ps1
param(
    [string]$WorkspaceRoot = 'C:\Users\apviz\.minimax-agent\projects\SENTINEL_PRIME'
)

$counter = Get-Content "$WorkspaceRoot\09_LOGS\context_counter.txt" -ErrorAction SilentlyContinue
if (-not $counter) { $counter = 0 }
$counter = [int]$counter + 1
$counter | Set-Content "$WorkspaceRoot\09_LOGS\context_counter.txt"

$pct = [Math]::Min(100, [Math]::Round($counter * 2.5, 1))

if ($pct -ge 85) {
    Write-Host "🚨 CRITICAL ($pct%) - strategic-compact MANDATORY" -ForegroundColor Red
} elseif ($pct -ge 70) {
    Write-Host "⚠️ TRIGGER ($pct%) - strategic-compact RECOMANDAT" -ForegroundColor Yellow
} elseif ($pct -ge 50) {
    Write-Host "⚠️ WARN ($pct%) - monitor activ" -ForegroundColor DarkYellow
} else {
    Write-Host "✓ OK ($pct%) - context disponibil" -ForegroundColor Green
}
```

## Cross-Session Memory

```
Context counter se resetează la:
- strategic-compact
- sesiune nouă (post-3-propoziții)
- manual reset

Context memory se păstrează în:
- 09_LOGS/context_counter.txt (numeric)
- 09_LOGS/state_*.json (full state)
- HANDOFF files (pentru recovery)
```

## Anti-Mimicry prin Monitorizare

```
Monitorul nu e mimicry dacă:
- Raportează realitatea (nu exagerează)
- Marchează ce nu știe (nu inventează)
- Activează acțiuni preventive (nu reactive)
- Respectă R-2 (verifică empiric)
```

## Stare Finală

```
Monitor: ACTIV
Counter: incrementat per prompt
Threshold-uri: aplicate
Auto-compact: la TRIGGER/CRITICAL
HANDOFF recovery: la sesiune nouă

= Sistem complet de monitorizare context
= Anti-overflow preventiv
= Persistență cross-sesiune
```

---

**Status:** Codificat
**Versiune:** 1.0
**Aplicabil:** La fiecare prompt
