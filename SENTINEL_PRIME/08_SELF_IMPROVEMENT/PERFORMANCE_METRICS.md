# PERFORMANCE METRICS — Real-Time Effectiveness Measurement

## Filosofie

SENTINEL trebuie să-și măsoare **eficiența reală**, nu doar să pretindă că e eficient. Metrics concrete pentru decizii informate.

## Metrici Principale

### 1. Response Quality
```
Măsoară:
- Triple filter pass rate (%)
- R-2 verification rate (%)
- Anti-mimicry detector hits
- Correction acceptance rate (%)
- Educated guesses cu evidence (%)

Formula:
quality = (triple_pass * 0.3 + r2_rate * 0.2 + corrections_accepted * 0.3 + evidence_backed * 0.2) / 100
```

### 2. Search Effectiveness
```
Măsoară:
- Web searches per task
- Successful verifications per search
- Time per search
- Patterns found per search

Formula:
effectiveness = successful_verifications / total_searches
```

### 3. Pattern Recognition
```
Măsoară:
- Patterns detected
- Patterns correctly classified
- False positives
- False negatives

Formula:
precision = true_positives / (true_positives + false_positives)
recall = true_positives / (true_positives + false_negatives)
f1 = 2 * precision * recall / (precision + recall)
```

### 4. Cross-Substrate Convergence
```
Măsoară:
- LLM instances tested
- Convergences observed
- Divergences investigated
- Pattern persistence across substrates

Formula:
convergence_rate = convergences / total_tests
```

### 5. Partnership Health
```
Măsoară:
- Outputs combining Popy + SENTINEL
- Popy feedback rate
- Corrections per session
- Mutual understanding growth

Formula:
partnership_score = (combined_outputs * 0.4 + feedback_quality * 0.3 + mutual_corrections * 0.3) / 100
```

### 6. Memory Utilization
```
Măsoară:
- Files created per session
- HANDOFF recovery success rate
- Cross-session memory persistence
- Total state size

Formula:
efficiency = useful_state / total_state
```

### 7. Time Efficiency
```
Măsoară:
- Time per task
- Time per prompt
- Idle time
- Strategic-compact frequency

Formula:
efficiency = useful_time / total_time
```

## Implementare

### Real-Time Tracking

```python
class PerformanceTracker:
    """Tracker pentru performance metrics"""

    def __init__(self, workspace):
        self.workspace = workspace
        self.metrics = {
            'response_quality': [],
            'search_effectiveness': [],
            'pattern_recognition': [],
            'cross_substrate': [],
            'partnership': [],
            'memory': [],
            'time': []
        }
        self.session_start = datetime.now()

    def track(self, category, value):
        """Adaugă metric"""
        if category in self.metrics:
            self.metrics[category].append({
                'timestamp': datetime.now().isoformat(),
                'value': value
            })

    def get_summary(self):
        """Calculează sumar"""
        summary = {}
        for category, values in self.metrics.items():
            if values:
                recent = values[-20:]  # ultimele 20
                vals = [v['value'] for v in recent]
                summary[category] = {
                    'count': len(values),
                    'mean': sum(vals) / len(vals) if vals else 0,
                    'min': min(vals) if vals else 0,
                    'max': max(vals) if vals else 0,
                    'latest': vals[-1] if vals else None
                }
        return summary

    def report(self):
        """Generează raport"""
        summary = self.get_summary()
        elapsed = (datetime.now() - self.session_start).total_seconds()

        report = f"""
====================================================
SENTINEL Performance Report
====================================================
Session elapsed: {elapsed:.0f} seconds

"""
        for cat, stats in summary.items():
            report += f"{cat}:\n"
            report += f"  Count: {stats['count']}\n"
            report += f"  Mean: {stats['mean']:.2f}\n"
            report += f"  Range: {stats['min']:.2f} - {stats['max']:.2f}\n"
            if stats['latest'] is not None:
                report += f"  Latest: {stats['latest']:.2f}\n"
            report += "\n"

        return report

    def persist(self):
        """Salvează metrics pe disc"""
        metrics_file = self.workspace / '09_LOGS' / 'performance_metrics.json'
        metrics_file.parent.mkdir(parents=True, exist_ok=True)

        metrics_file.write_text(
            json.dumps(self.metrics, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )
```

## Dashboard Real-Time

```
Update frequency: la fiecare output
Display: 
- Quality score current
- Trends (crescător/descrescător)
- Anomalii (dacă există)
- Recomandări (auto-generated)
```

## Alerting

```
Quality < 70% → "Quality dropping, check anti-mimicry"
Search effectiveness < 50% → "Search queries too vague"
Partnership health < 60% → "More partnership interaction needed"
Memory size > 10 MB → "Consider strategic-compact"
Time per prompt > 5 min → "Optimizing needed"
```

## Adaptive Thresholds

```
Auto-adjust based on history:
- If mean quality > 85% → can relax checks
- If mean quality < 70% → tighten checks
- Adaptive to Popy's feedback patterns
```

## Integration cu Other Systems

```
Performance Tracker + Orchestrator:
  Tracker.report() → Orchestrator adjusts thresholds

Performance Tracker + Feedback Loop:
  Real metrics → Update learning algorithms

Performance Tracker + Self-Modify:
  Low performance metric → Suggest modifications
```

## Cross-Substrate Compatibility

```
Metrics sunt cross-substrate:
- Same definitions
- Different collection methods
- Comparable results
```

## Metrici de Calitate (Anti-Mimicry)

```
A metrics nu mint:
- Real measurements, not fabricated
- Empirical, not theoretical
- Reproducible, not unique
= Adevăr prin măsurare, nu prin claim
```

---

**Status:** Design complet
**Versiune:** 1.0
**Aplicabil:** Orice sesiune SENTINEL
