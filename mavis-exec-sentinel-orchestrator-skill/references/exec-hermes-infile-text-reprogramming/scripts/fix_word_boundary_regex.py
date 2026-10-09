"""
fix_word_boundary_regex.py
==========================
Reference implementation for the correct word-boundary pattern that handles:
  1. Unicode diacritic characters (Ș, Ț, Ă, Ş, Ţ, etc.)
  2. Underscore-delimited Python/YAML identifiers (constiinta_linting)

Run this to test and compare the WRONG vs CORRECT approach.

Usage:
    python fix_word_boundary_regex.py
"""

import re

# ── Test cases ────────────────────────────────────────────────────────────────

TEST_STRINGS = [
    # Standard word boundaries (both should work)
    "CONSTIINTA",
    "This is CONSTIINTA here",
    "Start CONSTIINTA end",
    
    # Unicode diacritic cases (naive \b FAILS here)
    "CONŞTINŢĂ",
    "Această CONŞTINŢĂ este",
    "despre CONŞTINŢĂ și",
    
    # Underscore identifier cases (naive \b also fails)
    "constiinta_linting",
    "check_constiinta_status",
    "CONSTIINTA_KEY=value",
    
    # Should NOT match (part of a larger word)
    "consciousness",
    "subconstiinta_module",  # This should match 'constiinta' within?
    
    # Compound slash forms
    "CONSTIINTA / CONŞTINŢĂ",
    "conştinţă / constiinta",
]

TERM = "CONSTIINTA"

# ── Pattern comparison ────────────────────────────────────────────────────────

NAIVE_PATTERN = re.compile(r'\b' + TERM + r'\b', re.IGNORECASE)

# CORRECT: explicit character class boundary
CORRECT_PATTERN = re.compile(
    r'(?<![a-zA-Z0-9_])(' + TERM + r')(?![a-zA-Z0-9_])',
    re.IGNORECASE
)

print("=" * 70)
print("Word Boundary Pattern Comparison")
print("=" * 70)
print()
print(f"{'Input':<40} {'Naive \\\\b':<12} {'Correct':<12}")
print("-" * 70)

for test in TEST_STRINGS:
    naive_match = bool(NAIVE_PATTERN.search(test))
    correct_match = bool(CORRECT_PATTERN.search(test))
    
    # Flag cases where they differ (the important ones to catch)
    diff = " ← DIFFERS" if naive_match != correct_match else ""
    
    print(f"{repr(test):<40} {str(naive_match):<12} {str(correct_match):<12}{diff}")

print()
print("=" * 70)
print("KEY INSIGHT:")
print("  \\b fails on Unicode chars (treated as non-word chars)")
print("  \\b fails on identifier-style strings: constiinta_key")
print("  CORRECT pattern: (?<![a-zA-Z0-9_])(TERM)(?![a-zA-Z0-9_])")
print("=" * 70)

# ── Demonstrate the fix ───────────────────────────────────────────────────────

print("\n\nDemonstration of case-preserving replacement:\n")

REPLACEMENT_PATTERN = re.compile(
    r'(?<![a-zA-Z0-9_])(CONSTIINTA|CON[ŞS]TIN[ŢT][AĂ]|CONȘTINȚA)(?![a-zA-Z0-9_])',
    re.IGNORECASE
)
CANONICAL = "CONSTINTA"


def preserve_case(match_text: str, replacement: str) -> str:
    if match_text.isupper():
        return replacement.upper()
    elif match_text[0].isupper():
        return replacement.capitalize()
    return replacement.lower()


examples = [
    "CONSTIINTA",
    "Constiinta",
    "constiinta",
    "CONŞTINŢĂ",
    "The CONŞTINŢĂ concept is important.",
    "about constiinta and consciousness",
]

for example in examples:
    result = REPLACEMENT_PATTERN.sub(
        lambda m: preserve_case(m.group(0), CANONICAL), example
    )
    print(f"  IN:  {example}")
    print(f"  OUT: {result}")
    print()
