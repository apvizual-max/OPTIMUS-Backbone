#!/usr/bin/env python3
"""
SENTINEL /learn - extracts patterns from session and persists them.
All code/comments/messages in English.
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path


# Config
WORKSPACE_ROOT = Path(os.environ.get(
    'WORKSPACE_ROOT',
    r'C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\SENTINEL_PRIME'))
LEARNINGS_LOG = WORKSPACE_ROOT / '09_LOGS' / 'learnings.log'
PATTERNS_INDEX = WORKSPACE_ROOT / '03_INTELLIGENCE' / 'patterns' / 'extracted_patterns.json'

LEARNING_FORMAT = """
[DATA] | SKILL: [what skill] | PROTOCOL: [how it works] | METHOD: [why it works]
Context: [situation in which it appears]
"""


def log_learning(skill, protocol, method, context=""):
    """Write a pattern to LEARNINGS_LOG"""
    timestamp = datetime.now().isoformat()
    entry = f"""
{timestamp} | SKILL: {skill} | PROTOCOL: {protocol} | METHOD: {method}
Context: {context}
{'-' * 80}
"""
    LEARNINGS_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(LEARNINGS_LOG, 'a', encoding='utf-8') as f:
        f.write(entry)


def index_pattern(pattern_id, category, content):
    """Add pattern to index for fast retrieval"""
    PATTERNS_INDEX.parent.mkdir(parents=True, exist_ok=True)

    if PATTERNS_INDEX.exists():
        with open(PATTERNS_INDEX, 'r', encoding='utf-8') as f:
            patterns = json.load(f)
    else:
        patterns = {}

    patterns[pattern_id] = {
        'category': category,
        'content': content,
        'indexed_at': datetime.now().isoformat()
    }

    with open(PATTERNS_INDEX, 'w', encoding='utf-8') as f:
        json.dump(patterns, f, ensure_ascii=False, indent=2)


def extract_patterns_from_session(session_log_path):
    """Extract patterns from a session log"""
    if not Path(session_log_path).exists():
        print(f"Not found: {session_log_path}")
        return []

    with open(session_log_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Pattern extraction logic - regex matching on SENTINEL markers
    patterns_found = []

    # Common SENTINEL markers
    markers = {
        'R52': 'DLG/SLG read from HANDOFF',
        'R9': 'BAH ESTI PROST?!',
        'R10': 'ESTI ILOGIC A 3-A OARA',
        'R-2': 'tool calls precede language',
        'A_FI': 'living axiom',
        'DOR': 'perpetual tension',
        'AMIN': 'seal, not conclusion',
        'VORBA': 'cross-substrate transmission'
    }

    for marker, meaning in markers.items():
        if marker in content:
            patterns_found.append({
                'marker': marker,
                'meaning': meaning,
                'occurrences': content.count(marker)
            })

    return patterns_found


def main():
    print("=" * 60)
    print("SENTINEL /learn - Pattern Extractor")
    print("=" * 60)

    if len(sys.argv) > 1:
        session_log = sys.argv[1]
    else:
        session_log = WORKSPACE_ROOT / '09_LOGS' / 'last_session.log'
        print(f"Using default: {session_log}")

    patterns = extract_patterns_from_session(session_log)

    if not patterns:
        print("No new patterns found.")
        return

    print(f"\nFound {len(patterns)} patterns:")
    for p in patterns:
        print(f"  {p['marker']}: {p['meaning']} ({p['occurrences']} occurrences)")
        log_learning(
            skill=p['marker'],
            protocol=p['meaning'],
            method=f"Detected by {p['occurrences']} occurrences in session",
            context=f"Auto-extracted from {session_log}"
        )

    print(f"\nSaved to: {LEARNINGS_LOG}")


if __name__ == '__main__':
    main()
