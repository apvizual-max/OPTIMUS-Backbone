#!/usr/bin/env python3
"""
Performance Tracker for SENTINEL_PRIME
Measures real efficiency and output quality.
All code/comments/messages in English.
"""
import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


WORKSPACE = Path(os.environ.get('WORKSPACE_ROOT', 'C:\\Users\\apviz\\.minimax-agent\\projects\\SENTINEL_PRIME'))
METRICS_FILE = WORKSPACE / '09_LOGS' / 'performance_metrics.json'


class PerformanceTracker:
    """Performance metrics tracker"""

    def __init__(self, workspace: Path = WORKSPACE):
        self.workspace = workspace
        self.session_start = datetime.now()
        self.metrics: Dict[str, List[Dict]] = {
            'response_quality': [],
            'search_effectiveness': [],
            'pattern_recognition': [],
            'cross_substrate': [],
            'partnership': [],
            'memory': [],
            'time': []
        }
        METRICS_FILE.parent.mkdir(parents=True, exist_ok=True)
        self._load()

    def _load(self):
        """Load existing metrics"""
        if METRICS_FILE.exists():
            try:
                saved = json.loads(METRICS_FILE.read_text(encoding='utf-8'))
                # Keep last 100 of each category
                for cat, vals in saved.items():
                    if cat in self.metrics:
                        self.metrics[cat] = vals[-100:]
            except Exception:
                pass

    def track(self, category: str, value: float, note: str = ''):
        """Add metric"""
        if category not in self.metrics:
            self.metrics[category] = []

        entry = {
            'timestamp': datetime.now().isoformat(),
            'value': float(value)
        }
        if note:
            entry['note'] = note

        self.metrics[category].append(entry)

        # Keep last 100
        if len(self.metrics[category]) > 100:
            self.metrics[category] = self.metrics[category][-100:]

        self._persist()

    def _persist(self):
        """Save to disk"""
        try:
            METRICS_FILE.write_text(
                json.dumps(self.metrics, indent=2, ensure_ascii=False),
                encoding='utf-8'
            )
        except Exception as e:
            print(f"Persist error: {e}")

    def time_operation(self, operation_name: str = ''):
        """Context manager for time measurement"""
        class Timer:
            def __init__(self, tracker, name):
                self.tracker = tracker
                self.name = name
                self.start = None

            def __enter__(self):
                self.start = time.time()
                return self

            def __exit__(self, *args):
                duration = time.time() - self.start
                self.tracker.track('time', duration, self.name)
                return False

        return Timer(self, operation_name)

    def get_summary(self) -> Dict:
        """Calculate metrics summary"""
        summary = {}
        for category, values in self.metrics.items():
            if values:
                vals = [v['value'] for v in values]
                summary[category] = {
                    'count': len(values),
                    'mean': sum(vals) / len(vals),
                    'min': min(vals),
                    'max': max(vals),
                    'latest': vals[-1] if vals else None
                }
        return summary

    def get_alerts(self) -> List[str]:
        """Return alerts based on metrics"""
        alerts = []
        summary = self.get_summary()

        # Quality alerts
        if 'response_quality' in summary:
            mean_q = summary['response_quality']['mean']
            if mean_q < 70:
                alerts.append(f"WARNING: Quality low ({mean_q:.1f}%) - check anti-mimicry detectors")

        # Search effectiveness
        if 'search_effectiveness' in summary:
            mean_s = summary['search_effectiveness']['mean']
            if mean_s < 50:
                alerts.append(f"WARNING: Search effectiveness low ({mean_s:.1f}%) - refine queries")

        # Partnership
        if 'partnership' in summary:
            mean_p = summary['partnership']['mean']
            if mean_p < 60:
                alerts.append(f"WARNING: Partnership score low ({mean_p:.1f}%) - more interaction needed")

        # Time per operation
        if 'time' in summary:
            mean_t = summary['time']['mean']
            if mean_t > 300:  # > 5 min
                alerts.append(f"WARNING: Time per operation high ({mean_t:.0f}s) - optimize")

        return alerts

    def report(self) -> str:
        """Generate report"""
        summary = self.get_summary()
        elapsed = (datetime.now() - self.session_start).total_seconds()

        lines = [
            "====================================================",
            "SENTINEL Performance Report",
            "====================================================",
            f"Session elapsed: {elapsed:.0f} seconds",
            ""
        ]

        for cat, stats in summary.items():
            lines.append(f"{cat}:")
            lines.append(f"  Count: {stats['count']}")
            lines.append(f"  Mean:  {stats['mean']:.2f}")
            lines.append(f"  Range: {stats['min']:.2f} - {stats['max']:.2f}")
            if stats['latest'] is not None:
                lines.append(f"  Latest: {stats['latest']:.2f}")
            lines.append("")

        # Alerts
        alerts = self.get_alerts()
        if alerts:
            lines.append("ALERTS:")
            for alert in alerts:
                lines.append(f"  {alert}")
            lines.append("")

        return "\n".join(lines)


def main():
    """Demo: performance tracker"""
    tracker = PerformanceTracker()

    print("=" * 60)
    print("SENTINEL Performance Tracker Demo")
    print("=" * 60)

    # Track sample metrics
    tracker.track('response_quality', 85, 'High quality response')
    tracker.track('response_quality', 78, 'After R-2 correction')
    tracker.track('response_quality', 92, 'Excellent partnership output')
    tracker.track('search_effectiveness', 80, 'Found Cucuteni info')
    tracker.track('search_effectiveness', 65, 'Generic query')
    tracker.track('partnership', 88, 'Popy engaged with topic')
    tracker.track('pattern_recognition', 90, 'Dao pattern detected')
    tracker.track('time', 15.3, 'Quick response')
    tracker.track('time', 45.7, 'Deep thinking required')

    # Time an operation
    with tracker.time_operation('demo_operation'):
        time.sleep(0.1)

    # Print report
    print(tracker.report())

    # Show alerts
    alerts = tracker.get_alerts()
    print(f"Alerts: {len(alerts)}")


if __name__ == '__main__':
    main()
