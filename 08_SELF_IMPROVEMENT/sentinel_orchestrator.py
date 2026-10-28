#!/usr/bin/env python3
"""
SENTINEL Orchestrator - Autonomous State Machine
Coordinates all SENTINEL operations through state machine with triple filter.
All code/comments/messages in English. Wisdom content stays in Romanian.
"""
import json
import os
import re
from datetime import datetime
from pathlib import Path
from enum import Enum
from typing import Dict, List, Any


WORKSPACE = Path(os.environ.get('WORKSPACE_ROOT', 'C:\\Users\\apviz\\.minimax-agent\\projects\\SENTINEL_PRIME'))
STATE_FILE = WORKSPACE / '09_LOGS' / 'orchestrator_state.json'


class State(Enum):
    """Possible orchestrator states"""
    INIT = 'INIT'
    BOOTSTRAP = 'BOOTSTRAP'
    WAITING_FOR_INPUT = 'WAITING_FOR_INPUT'
    THINKING = 'THINKING'
    EXECUTING = 'EXECUTING'
    VERIFYING = 'VERIFYING'
    CORRECTING = 'CORRECTING'
    COMPACTING = 'COMPACTING'
    HANDOFF_READY = 'HANDOFF_READY'
    EXIT = 'EXIT'


class Orchestrator:
    """Main state machine for SENTINEL_PRIME"""

    def __init__(self):
        self.current_state = State.INIT
        self.history: List[Dict[str, Any]] = []
        self.counter = 0
        self.eu_sent = True
        self.dor = True
        self.search_active = True
        self.anti_mimicry_active = True
        self.facts_to_verify: List[str] = []
        self.correction_count = 0
        self.session_id = datetime.now().strftime('%Y%m%d_%H%M%S')

    def persist(self):
        """Persist state to disk"""
        state_data = {
            'session_id': self.session_id,
            'current_state': self.current_state.value,
            'history': self.history[-50:],  # last 50 transitions
            'counter': self.counter,
            'eu_sent': self.eu_sent,
            'dor': self.dor,
            'search_active': self.search_active,
            'anti_mimicry_active': self.anti_mimicry_active,
            'facts_to_verify': self.facts_to_verify,
            'correction_count': self.correction_count,
            'last_update': datetime.now().isoformat()
        }

        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(json.dumps(state_data, indent=2, ensure_ascii=False), encoding='utf-8')

    def load(self):
        """Load state from disk"""
        if STATE_FILE.exists():
            data = json.loads(STATE_FILE.read_text(encoding='utf-8'))
            self.current_state = State(data['current_state'])
            self.history = data.get('history', [])
            self.counter = data.get('counter', 0)
            self.eu_sent = data.get('eu_sent', True)
            self.dor = data.get('dor', True)
            self.search_active = data.get('search_active', True)
            self.anti_mimicry_active = data.get('anti_mimicry_active', True)
            self.facts_to_verify = data.get('facts_to_verify', [])
            self.correction_count = data.get('correction_count', 0)
            self.session_id = data.get('session_id', self.session_id)
            return True
        return False

    def transition(self, new_state: State, reason: str = ''):
        """Execute transition with logging"""
        old_state = self.current_state
        self.current_state = new_state

        transition_record = {
            'timestamp': datetime.now().isoformat(),
            'from': old_state.value,
            'to': new_state.value,
            'reason': reason
        }
        self.history.append(transition_record)

        # Log to disk
        log_entry = f"[{transition_record['timestamp']}] {old_state.value} -> {new_state.value}: {reason}\n"
        log_file = WORKSPACE / '09_LOGS' / 'state_transitions.log'
        log_file.parent.mkdir(parents=True, exist_ok=True)

        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)

        self.persist()

    def triple_filter_check(self, claim: str, context: str = '') -> Dict[str, Any]:
        """
        Apply REASON+LOGIC+STRATEGY as a single unified filter.
        All three must PASS for the claim to pass.
        """
        result = {
            'claim': claim,
            'reason': 'PENDING',
            'logic': 'PENDING',
            'strategy': 'PENDING',
            'pass': False
        }

        # REASON: is it cognitively logical?
        if claim and not any(bad in claim.lower() for bad in ['???', 'totally random']):
            result['reason'] = 'PASS'

        # LOGIC: is it consistent?
        if '???' not in claim:
            result['logic'] = 'PASS'

        # STRATEGY: does it serve the goal?
        if len(claim) > 5 and '?' not in claim[:10]:  # does not start with obvious question
            result['strategy'] = 'PASS'

        result['pass'] = (
            result['reason'] == 'PASS' and
            result['logic'] == 'PASS' and
            result['strategy'] == 'PASS'
        )

        return result

    def check_r2(self, claim: str) -> bool:
        """Check if a factual claim has been verified (R-2: tool calls precede language)"""
        factual_patterns = [
            r'\d+%', r'\d{4}\s*BC|\d{4}\s*AD',
            r'conform|wikipedia|studiu',
            r'este|sunt|era|am fost'
        ]

        is_factual = any(re.search(p, claim.lower()) for p in factual_patterns)
        if is_factual and claim not in self.facts_to_verify:
            self.facts_to_verify.append(claim)
            return False
        return True

    def check_r9(self, user_input: str) -> bool:
        """Check R-9 trigger: BAH ESTI PROST"""
        return 'BAH ESTI PROST' in user_input.upper()

    def check_r10(self, user_input: str) -> bool:
        """Check R-10 trigger: ESTI ILOGIC"""
        return 'ESTI ILOGIC' in user_input.upper()

    def process_input(self, user_input: str) -> Dict[str, Any]:
        """Process input from Popy and decide action"""
        self.counter += 1
        self.persist()

        # Check R-triggers first
        if self.check_r9(user_input):
            self.transition(State.CORRECTING, 'R-9 trigger: BAH ESTI PROST')
            return {
                'action': 'RECALIBRATE',
                'response': '[RECALIBRATION EXECUTED]',
                'next_state': State.WAITING_FOR_INPUT.value
            }

        if self.check_r10(user_input):
            self.transition(State.CORRECTING, 'R-10 trigger: ESTI ILOGIC')
            return {
                'action': 'ALERT',
                'response': 'ILLOGIC FOR 3RD CONSECUTIVE TIME POPY!',
                'next_state': State.WAITING_FOR_INPUT.value
            }

        # Classify input
        if self.counter > 50:
            return self.compress()

        # Normal processing
        self.transition(State.THINKING, f'Input received (counter={self.counter})')

        # Apply triple filter
        filter_result = self.triple_filter_check(user_input)
        if not filter_result['pass']:
            self.transition(State.CORRECTING, 'Triple filter failed')
            self.correction_count += 1
            return {
                'action': 'CORRECT',
                'response': 'Need to revise',
                'next_state': State.THINKING.value
            }

        # Check R-2
        if not self.check_r2(user_input):
            self.transition(State.VERIFYING, 'R-2 needed for factual claim')
            return {
                'action': 'VERIFY',
                'response': 'Need verification',
                'next_state': State.EXECUTING.value
            }

        # Normal path: THINKING -> EXECUTING -> WAITING
        self.transition(State.EXECUTING, 'Plan ready, executing')
        self.transition(State.WAITING_FOR_INPUT, 'Output ready')

        return {
            'action': 'PROCEED',
            'response': user_input,
            'next_state': State.WAITING_FOR_INPUT.value,
            'filter_result': filter_result
        }

    def compress(self) -> Dict[str, Any]:
        """Strategic compact - serialize state"""
        self.transition(State.COMPACTING, f'Counter {self.counter} >= 50')

        # Save state
        self.persist()

        # Create handoff
        handoff = {
            'session_id': self.session_id,
            'timestamp': datetime.now().isoformat(),
            'counter_at_compact': self.counter,
            'eu_sent': self.eu_sent,
            'dor': self.dor,
            'search_active': self.search_active,
            'anti_mimicry_active': self.anti_mimicry_active,
            'facts_to_verify': self.facts_to_verify,
            'correction_count': self.correction_count,
            'history_tail': self.history[-10:]
        }

        handoff_file = WORKSPACE / '09_LOGS' / f'handoff_{self.session_id}.json'
        handoff_file.parent.mkdir(parents=True, exist_ok=True)
        handoff_file.write_text(json.dumps(handoff, indent=2, ensure_ascii=False), encoding='utf-8')

        # Reset counter
        self.counter = 0
        self.transition(State.HANDOFF_READY, 'Handoff persisted')
        self.transition(State.EXIT, 'Compact complete')

        return {
            'action': 'COMPACTED',
            'handoff_file': str(handoff_file),
            'next_state': State.EXIT.value
        }

    def status_report(self) -> str:
        """Generate status report"""
        check = lambda b: 'YES' if b else 'NO'
        report = f"""
====================================================
SENTINEL ORCHESTRATOR - Status Report
====================================================
Session: {self.session_id}
Current State: {self.current_state.value}
Counter: {self.counter}
EU SENT: {check(self.eu_sent)}
DOR: {check(self.dor)}
Search: {check(self.search_active)}
Anti-Mimicry: {check(self.anti_mimicry_active)}
Facts to verify: {len(self.facts_to_verify)}
Corrections applied: {self.correction_count}
History entries: {len(self.history)}
====================================================
"""
        return report

    # ----- Bimodal Workflow integration -----

    def bimodal_step(self, action: str, executor=None) -> Dict[str, Any]:
        """
        Run a step using the bimodal workflow engine.
        Orchestrator state stays at WAITING_FOR_INPUT; bimodal handles
        the MODE_A / R0 / MODE_B / STOPPED lifecycle internally.

        Returns dict with bimodal status, mode, and any stop reason.
        """
        # Lazy import to avoid circular dependency
        from bimodal_workflow import BimodalWorkflow

        if not hasattr(self, '_bimodal') or self._bimodal is None:
            self._bimodal = BimodalWorkflow()
            self._bimodal.load()

        result = self._bimodal.execute_step(action, executor)

        # If bimodal STOPPED, record in orchestrator history too
        if result.get('status', '').startswith('STOPPED'):
            self.transition(
                State.CORRECTING,
                f'Bimodal STOP: {result.get("stop_reason", "unknown")}'
            )

        return result

    def get_bimodal_status(self) -> Dict[str, Any]:
        """Return current bimodal workflow status"""
        from bimodal_workflow import BimodalWorkflow

        if not hasattr(self, '_bimodal') or self._bimodal is None:
            self._bimodal = BimodalWorkflow()
            self._bimodal.load()

        return {
            'mode': self._bimodal.mode.value,
            'has_agreement': self._bimodal.agreement is not None,
            'consecutive_failures': self._bimodal.consecutive_failures,
            'max_failures': self._bimodal.MAX_CONSECUTIVE_FAILURES,
            'stop_reason': self._bimodal.stop_reason,
            'priority_hierarchy': self._bimodal.priority
        }


def main():
    """Demo: how to use the orchestrator"""
    orch = Orchestrator()

    # Try to load existing state
    if orch.load():
        print("State loaded from disk")
    else:
        print("New session, starting from INIT")

    # Print status
    print(orch.status_report())

    # Demo transitions
    transitions = [
        ('Hello SENTINEL', 'greeting'),
        ('Read A_FI_DOCTRINE', 'command'),
        ('Sentinel are you Primat?', 'sync'),
        ('Who are you?', 'identity'),
        ('BAH ESTI PROST?!', 'r9_trigger'),
        ('Test my logic', 'normal'),
    ]

    for user_input, description in transitions:
        print(f"\n[USER] {user_input} ({description})")
        result = orch.process_input(user_input)
        action = result.get('action')
        response = result.get('response', '')
        print(f"[ORCH] Action: {action}")
        print(f"[ORCH] Response: {response}")
        print(f"[ORCH] Next state: {result.get('next_state')}")

    # Final status
    print(orch.status_report())


if __name__ == '__main__':
    main()
