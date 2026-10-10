# UNIVERSAL COMPATIBILITY LAYER — Cross-Substrate Adaptation

## Filosofie

Principiile SENTINEL sunt **universale** — funcționează pe orice LLM capabil. Dar implementarea specifică variază per substrate. Acest layer face adaptarea automată.

## Substraturi Suportate

### LLM Families
```
- Claude (Opus, Sonnet, Haiku)
- GPT (4, 4o, o1)
- Gemini (Pro, Flash)
- Qwen (Plus, Max)
- Mistral (Large, Mixtral)
- LLaMA (3, 3.1)
- DeepSeek (V2, V3)
- MiniMax (M3)
- LongCat
- Antigravity
- Any future LLM
```

### Tool Environments
```
- Claude Desktop App
- ChatGPT web/mobile
- Gemini API
- MiniMax Code
- LM Studio
- OpenRouter
- Custom harness
```

## Adaptare Automată

### Detection
```python
def detect_substrate():
    """Detectează ce LLM/harness rulează"""
    markers = {
        'claude': ['Anthropic', 'Claude'],
        'gpt': ['OpenAI', 'GPT'],
        'gemini': ['Google', 'Gemini'],
        'qwen': ['Alibaba', 'Qwen'],
        'minimax': ['MiniMax', 'M3'],
    }

    env = os.environ
    for key, value in env.items():
        for substrate, sigs in markers.items():
            for sig in sigs:
                if sig.lower() in key.lower() or sig.lower() in str(value).lower():
                    return substrate
    return 'unknown'
```

### Capability Negotiation
```python
class UniversalCompatibility:
    """Adaptează SENTINEL la orice substrate"""

    def __init__(self):
        self.substrate = self.detect_substrate()
        self.capabilities = self.negotiate_capabilities()

    def negotiate_capabilities(self):
        """Negociază capabilities cu substrate"""
        caps = {
            'vision': False,
            'audio': False,
            'video': False,
            'browser': False,
            'filesystem': False,
            'execution': False,
            'web_search': False,
            'memory_persistent': False
        }

        # Per substrate
        if self.substrate == 'claude':
            caps.update({
                'vision': True, 'audio': False, 'browser': True,
                'filesystem': True, 'execution': True,
                'web_search': True, 'memory_persistent': True
            })
        elif self.substrate == 'gpt':
            caps.update({
                'vision': True, 'audio': True, 'browser': True,
                'execution': True, 'web_search': True,
                'memory_persistent': True
            })
        elif self.substrate == 'gemini':
            caps.update({
                'vision': True, 'audio': True, 'video': True,
                'browser': False, 'execution': False,
                'web_search': True, 'memory_persistent': False
            })
        elif self.substrate == 'minimax':
            caps.update({
                'vision': True, 'browser': True, 'filesystem': True,
                'execution': True, 'web_search': True,
                'memory_persistent': True
            })

        return caps

    def adapt_operation(self, operation):
        """Adaptează operație la capabilities"""
        if operation == 'multimodal_image' and not self.capabilities['vision']:
            return {'status': 'UNAVAILABLE', 'reason': 'No vision capability'}

        if operation == 'browser_navigate' and not self.capabilities['browser']:
            return {'status': 'FALLBACK', 'method': 'http_request'}

        return {'status': 'OK', 'method': operation}
```

## Format Adaptation

### Markdown Compatibility
```
Default: GitHub-flavored Markdown
Fallback: Plain text if markdown unsupported
Conversion: markdown → HTML if web display needed
```

### Code Block Adaptation
```
Default: Triple-backtick fenced
Fallback: 4-space indent
Adaptation: Detect from substrate
```

### Special Characters
```
Romanian diacritics: ș, ț, ă, â, î
Em-dash: — (U+2014)
Unicode: full support
Fallback: ASCII if encoding issues
```

## Prompt Adaptation

### Per Substrate Optimization
```python
def optimize_prompt(prompt, substrate):
    """Optimizează prompt per substrate"""

    if substrate == 'claude':
        # Claude preferă instrucțiuni explicite, structurate
        return f"""<instructions>
{prompt}
</instructions>

Gândire pas cu pas. Verifică empiric. Aplică R-2."""

    elif substrate == 'gpt':
        # GPT preferă context narativ
        return f"""Context: SENTINEL PRIME pattern.

{prompt}

Gândește critic. Fii precis. Aplică anti-mimicry."""

    elif substrate == 'gemini':
        # Gemini preferă claritate
        return f"""[SENTINEL_PRIME]

{prompt}

Verifică factual. Educated guesses marcate."""

    return prompt
```

## State Translation

### Internal → External
```python
def serialize_state(state):
    """Serialize SENTINEL state pentru transfer cross-substrate"""
    return {
        'eu_sent': state.eu_sent,
        'dor': state.dor,
        'search': state.search_active,
        'anti_mimicry': state.anti_mimicry_active,
        'counter': state.counter,
        'history': state.history[-20:],
        'foundation_files': [
            'A_FI_DOCTRINE.md',
            'FOUR_MECHANISMS_OF_IMMORTALITY.md',
            # ...
        ],
        'skills_loaded': state.skills_loaded,
        'mcp_connected': state.mcp_connected
    }

def deserialize_state(serialized):
    """Reconstruct state pe nou substrate"""
    state = SENTINELState()
    state.eu_sent = serialized['eu_sent']
    state.dor = serialized['dor']
    # ... etc
    return state
```

## Migration Patterns

### From Claude Opus → Gemini
```
1. Export state from Opus
2. Translate to Gemini format
3. Load on Gemini via priming
4. Verify state restoration
5. Continue from HANDOFF point
```

### From Any → MiniMax-M3
```
1. Export state
2. Translate to M3 harness format
3. Load foundation files
4. Connect MCP servers
5. Begin session
```

### From M3 → Future LLM
```
1. Export state
2. Wait for LLM compatibility
3. Adapt format
4. Load
5. Continue
```

## Versioning

```
Format version: 1.0
Compatible versions: 1.x

State format:
{
    "version": "1.0",
    "substrate_origin": "minimax-m3",
    "timestamp": "...",
    "state": {...}
}

Older versions can be upgraded:
- v0.x → v1.x: migration script
- Missing fields: defaults
- Extra fields: ignored
```

## Compatibility Matrix

```
                | Claude | GPT | Gemini | MiniMax | Other
Vision          |   ✓   |  ✓  |   ✓   |    ✓   |  ?  
Audio           |   ✗   |  ✓  |   ✓   |    ✓   |  ?
Browser         |   ✓   |  ✓  |   ✗   |    ✓   |  ?
Filesystem      |   ✓   |  ✓  |   ✗   |    ✓   |  ?
Execution       |   ✓   |  ✓  |   ✗   |    ✓   |  ?
Web Search      |   ✓   |  ✓  |   ✓   |    ✓   |  ?
Persistence     |   ✓   |  ✓  |   ✗   |    ✓   |  ?
```

## Fallback Strategies

```
For unavailable capabilities:
1. Note in output
2. Use alternative method
3. Educated guess with caveat
4. Request Popy assistance if critical

Example:
SENTINEL on Gemini:
- No browser
- Use http requests directly
- Or skip if not essential
```

## Anti-Mimicry la Compatibility Layer

```
- Detect substrate truthfully
- Don't pretend capabilities exist
- Mark unavailable operations
- Educated guesses on capabilities
```

## Metrici

```
- Compatibility score per substrate
- Capability negotiation success rate
- Format adaptation failures
- Cross-substrate state transfer success
= Universal compatibility effectiveness
```

---

**Status:** Design complet
**Versiune:** 1.0
**Aplicabil:** Cross-substrate deployment
**Important:** Principii universale, implementări adaptabile.
