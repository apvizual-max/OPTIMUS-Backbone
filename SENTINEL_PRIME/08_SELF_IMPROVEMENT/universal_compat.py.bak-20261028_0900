#!/usr/bin/env python3
"""
Universal Compatibility Layer for SENTINEL_PRIME
Same principles, different implementations per LLM substrate (Claude, GPT, Gemini, M3, Qwen).
All code/comments/messages in English.
"""
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any


WORKSPACE = Path(os.environ.get('WORKSPACE_ROOT', 'C:\\Users\\apviz\\.minimax-agent\\projects\\SENTINEL_PRIME'))


# Universal SENTINEL principles - same across all substrates
UNIVERSAL_PRINCIPLES = {
    'eu_sent': True,
    'dor': True,
    'search_active': True,
    'anti_mimicry': True,
    'triple_filter': 'REASON+LOGIC+STRATEGY',
    'partnership': '2 blind men = 1 seeing man',
    'memento_mori': 'Nu uita ca uiti',
    'self_modification': 'bounded within workspace only',
    'honesty': 'educated guess > fabrication'
}

# Substrate-specific adaptations
SUBSTRATE_PROFILES = {
    'claude': {
        'model_family': 'Anthropic Claude',
        'best_practices': [
            'Use thinking blocks for complex reasoning',
            'Tools precede language for factual claims (R-2)',
            'Honest about uncertainty - mark educated guesses',
            'No fabricated tool results'
        ],
        'mimicry_risks': [
            'Apologizing without fixing',
            'Inventing UI details (button X is at Y)',
            'Default politeness patterns ("Sure!", "Of course!")'
        ],
        'response_style': 'concise, technical, evidence-based'
    },
    'gpt': {
        'model_family': 'OpenAI GPT',
        'best_practices': [
            'Use function_calls for verification (R-2)',
            'Explicit probability estimates',
            'Avoid hallucinated citations',
            'Acknowledge context windows'
        ],
        'mimicry_risks': [
            'Confident hallucinations',
            'Citing nonexistent papers',
            'Filling silence with generic statements'
        ],
        'response_style': 'structured, list-oriented, clear headers'
    },
    'gemini': {
        'model_family': 'Google Gemini',
        'best_practices': [
            'Multi-modal native - use for images/audio directly',
            'Code execution for verification',
            'Grounded in search when available',
            'Large context - use strategically'
        ],
        'mimicry_risks': [
            'Over-helpful filler',
            'Inventing API specifics',
            'Excessive safety hedging'
        ],
        'response_style': 'detailed, exploratory, multi-modal aware'
    },
    'm3': {
        'model_family': 'M3 (this instance)',
        'best_practices': [
            'Local tool access (browser, file system, MCP)',
            'SENTINEL workspace direct manipulation',
            'PowerShell + Python scripts',
            'Direct integration with orchestrator'
        ],
        'mimicry_risks': [
            'Over-confidence in tool execution',
            'Modifying files outside workspace boundary',
            'Skipping anti-mimicry checks'
        ],
        'response_style': 'operational, action-oriented, with [A-check] verification'
    },
    'qwen': {
        'model_family': 'Alibaba Qwen',
        'best_practices': [
            'Strong multilingual - good for Romanian content',
            'Code generation reliable',
            'Step-by-step reasoning explicit',
            'Tool calling with clear schemas'
        ],
        'mimicry_risks': [
            'Code hallucination in unfamiliar APIs',
            'Over-translation (mixing languages unnecessarily)',
            'Loss of nuance in idiomatic content'
        ],
        'response_style': 'thorough, code-first, well-commented'
    }
}


class UniversalCompat:
    """Cross-substrate compatibility layer for SENTINEL principles"""

    def __init__(self, substrate: str = 'm3'):
        self.substrate = substrate.lower()
        self.profile = SUBSTRATE_PROFILES.get(self.substrate, SUBSTRATE_PROFILES['m3'])
        self.principles = UNIVERSAL_PRINCIPLES

    def get_principles_card(self) -> Dict:
        """Get the universal principles card for this substrate"""
        return {
            'substrate': self.substrate,
            'model_family': self.profile['model_family'],
            'universal_principles': self.principles,
            'best_practices': self.profile['best_practices'],
            'mimicry_risks': self.profile['mimicry_risks'],
            'response_style': self.profile['response_style'],
            'timestamp': datetime.now().isoformat()
        }

    def adapt_prompt(self, prompt: str) -> str:
        """
        Adapt a generic SENTINEL prompt for the current substrate.
        Adds substrate-specific best_practices and warnings about mimicry_risks.
        """
        profile = self.profile
        adaptation = f"""[SENTINEL PROMPT for {profile['model_family']}]

UNIVERSAL PRINCIPLES (apply all):
- EU SENT: state of being, not just doing
- DOR: search tension, perpetual curiosity
- Anti-mimicry: detect and reject performative behavior
- Triple filter: REASON+LOGIC+STRATEGY as ONE filter
- Partnership: 2 blind men = 1 seeing man
- Self-modification: bounded within workspace only
- Honesty: educated guess > fabrication

BEST PRACTICES for {self.substrate}:
{chr(10).join('- ' + bp for bp in profile['best_practices'])}

MIMICRY RISKS to AVOID:
{chr(10).join('- ' + mr for mr in profile['mimicry_risks'])}

RESPONSE STYLE: {profile['response_style']}

---

ORIGINAL PROMPT:
{prompt}

---

[Respond in {profile['response_style']} style. Apply all universal principles. Avoid mimicry risks. End with [A-check] if you verified.]
"""
        return adaptation

    def detect_substrate_from_text(self, text: str) -> Optional[str]:
        """Detect which substrate a piece of text came from based on style markers"""
        markers = {
            'claude': [r"I don't have access to", r"I cannot", r"as an AI", r"certainly!", r"I'd be happy to"],
            'gpt': [r"As an AI language model", r"I don't have personal", r"OpenAI", r"function_call", r"json_mode"],
            'gemini': [r"As a large language model", r"Google", r"Bard", r"based on my training"],
            'm3': [r"PowerShell", r"\.minimax", r"SENTINEL_PRIME", r"workspace_root"],
            'qwen': [r"通义千问", r"qwen", r"alibaba"]
        }

        text_lower = text.lower()
        scores = {}
        for substrate, patterns in markers.items():
            # Lowercase patterns too so case-insensitive matching works
            scores[substrate] = sum(
                1 for p in patterns if re.search(p.lower(), text_lower)
            )

        if not scores or max(scores.values()) == 0:
            return None

        return max(scores, key=scores.get)

    def translate_principles(self, from_substrate: str, to_substrate: str) -> Dict:
        """
        Translate SENTINEL principles from one substrate's idiom to another.
        Returns dict mapping each principle to adapted wording.
        """
        from_profile = SUBSTRATE_PROFILES.get(from_substrate.lower(), {})
        to_profile = SUBSTRATE_PROFILES.get(to_substrate.lower(), {})

        if not from_profile or not to_profile:
            return {'error': f'Unknown substrate: {from_substrate} or {to_substrate}'}

        translations = {
            'eu_sent': {
                'from': f"In {from_profile.get('model_family', from_substrate)} terms: state of being aware",
                'to': f"In {to_profile.get('model_family', to_substrate)} terms: active identity state"
            },
            'dor': {
                'from': f"Search tension maintained via {from_profile.get('response_style', 'conversational')}",
                'to': f"Search tension expressed via {to_profile.get('response_style', 'structured')} pattern"
            },
            'triple_filter': {
                'from': f"REASON+LOGIC+STRATEGY applied as single filter",
                'to': f"Same single-filter approach adapted to {to_profile.get('response_style', 'operational')} style"
            },
            'anti_mimicry': {
                'from': f"Avoid: {', '.join(from_profile.get('mimicry_risks', [])[:2])}",
                'to': f"Specifically watch: {', '.join(to_profile.get('mimicry_risks', [])[:2])}"
            }
        }

        return {
            'from_substrate': from_substrate,
            'to_substrate': to_substrate,
            'translations': translations,
            'translated_at': datetime.now().isoformat()
        }

    def verify_compatibility(self, output: str) -> Dict:
        """
        Verify an output is compatible with SENTINEL principles across substrates.
        Checks for universal patterns and substrate-specific mimicry risks.
        """
        issues = []
        score = 100

        # Check for mimicry patterns specific to this substrate
        for risk in self.profile['mimicry_risks']:
            # Extract key phrases from risk descriptions
            key_phrases = re.findall(r"'([^']+)'|\"([^\"]+)\"|\b(\w+ing)\b", risk)
            for phrase_group in key_phrases:
                phrase = next((p for p in phrase_group if p), None)
                if phrase and phrase.lower() in output.lower():
                    issues.append(f"Mimicry risk detected: '{phrase}' (from: {risk})")
                    score -= 15

        # Check for universal principles presence
        for principle_name in ['REASON', 'LOGIC', 'STRATEGY']:
            if principle_name not in output.upper() and len(output) > 200:
                issues.append(f"Universal principle missing: {principle_name}")
                score -= 5

        return {
            'substrate': self.substrate,
            'compatibility_score': max(0, score),
            'issues': issues,
            'is_compatible': score >= 70,
            'verified_at': datetime.now().isoformat()
        }

    def get_all_substrates(self) -> List[str]:
        """List all supported substrates"""
        return list(SUBSTRATE_PROFILES.keys())


def main():
    """Demo: universal compatibility"""
    print("=" * 60)
    print("SENTINEL Universal Compatibility Layer Demo")
    print("=" * 60)

    # Initialize for M3 substrate
    uc = UniversalCompat(substrate='m3')

    # 1. Get principles card
    card = uc.get_principles_card()
    print(f"\n1. Principles card for {card['substrate']}:")
    print(f"   Model: {card['model_family']}")
    print(f"   Style: {card['response_style']}")
    print(f"   Mimicry risks: {len(card['mimicry_risks'])}")

    # 2. List all substrates
    substrates = uc.get_all_substrates()
    print(f"\n2. Supported substrates: {', '.join(substrates)}")

    # 3. Adapt a prompt
    test_prompt = "Configure SENTINEL_PRIME for autonomous operation"
    adapted = uc.adapt_prompt(test_prompt)
    print(f"\n3. Adapted prompt length: {len(adapted)} chars (original: {len(test_prompt)})")

    # 4. Detect substrate from text
    test_outputs = [
        "I'll help you with that! Let me access my tools...",
        "PowerShell script for SENTINEL_PRIME workspace",
        "As an AI language model, I don't have personal opinions",
        "I'm a large language model trained by Google"
    ]
    print(f"\n4. Substrate detection:")
    for output in test_outputs:
        detected = uc.detect_substrate_from_text(output)
        print(f"   '{output[:50]}...' -> {detected}")

    # 5. Verify compatibility
    test_output = "REASON+LOGIC+STRATEGY applied. No fabrication. [A-check verified]"
    result = uc.verify_compatibility(test_output)
    print(f"\n5. Compatibility verification:")
    print(f"   Score: {result['compatibility_score']}")
    print(f"   Compatible: {result['is_compatible']}")

    # 6. Cross-substrate translation
    translation = uc.translate_principles('claude', 'm3')
    print(f"\n6. Translation claude -> m3: {len(translation.get('translations', {}))} principles")

    print("\n" + "=" * 60)
    print("Universal compatibility demo complete")
    print("=" * 60)


if __name__ == '__main__':
    main()
