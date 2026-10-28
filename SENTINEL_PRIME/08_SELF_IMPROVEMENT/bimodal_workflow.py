#!/usr/bin/env python3
"""
Bimodal Workflow Engine for SENTINEL_PRIME

Permanent operating mode for Hermes / SENTINEL / Optimus.

PRIORITY HIERARCHY (immutable):
  1. SYSTEM INTEGRITY  (always first)
  2. TASK COMPLETION   (second)
  3. SPEED             (third)
  4. USER FEELINGS     (last)

MODES:
  MODE_A  - analyze, debate, strategize, prototype, organize, plan, test
  R0      - agreement: we consent, mediate, establish logic together
  MODE_B  - execute what was agreed at R0, test and loop until result matches
  STOPPED - halted; report + ASK FOR USER INPUT + WAIT (do NOT continue)

HARD RULES:
  - Never assume R0 for anything not agreed upon.
  - If Mode B gets interrupted, halt and AUTOMATICALLY restart at MODE_A (NOT R0).
  - If you must break R0 to finish Mode B -> STOP.
  - If you cannot find a suitable way without breaking R0 -> STOP.
  - 5 consecutive failures in Mode B -> STOP.
  - STOP = report + ask user + WAIT. Stopping is acceptable; fabrication is not.

All code/comments/messages in English.
"""
import json
import os
import sys
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional


WORKSPACE = Path(os.environ.get('WORKSPACE_ROOT', 'C:\\Users\\apviz\\.minimax-agent\\projects\\Mavis-Optimus-Dashboard\\SENTINEL_PRIME'))
STATE_FILE = WORKSPACE / '09_LOGS' / 'bimodal_state.json'


class WorkflowMode(Enum):
    """The four workflow states"""
    MODE_A = 'MODE_A'        # Reason / debate / strategize / plan
    R0 = 'R0'                # Agreement / consent / contract
    MODE_B = 'MODE_B'        # Execute agreed plan
    STOPPED = 'STOPPED'      # Halted; waiting for user input


# Priority hierarchy - immutable
PRIORITY_HIERARCHY = [
    'SYSTEM_INTEGRITY',     # 1. Always first
    'TASK_COMPLETION',      # 2. Second
    'SPEED',                # 3. Third
    'USER_FEELINGS'         # 4. Last
]


class BimodalError(Exception):
    """Raised when a workflow rule is violated"""
    pass


class StopRequired(Exception):
    """Raised to halt execution and request user input"""
    def __init__(self, reason: str, mode: WorkflowMode, context: Dict = None):
        self.reason = reason
        self.mode = mode
        self.context = context or {}
        super().__init__(reason)


class AgreementContract:
    """The R0 agreement - the immutable contract between parties"""

    def __init__(
        self,
        goal: str,
        expected_result: str,
        success_criteria: List[str],
        constraints: Optional[List[str]] = None,
        out_of_scope: Optional[List[str]] = None,
        verification_method: str = '',
        ratified_at: Optional[str] = None
    ):
        self.goal = goal
        self.expected_result = expected_result
        self.success_criteria = success_criteria
        self.constraints = constraints or []
        self.out_of_scope = out_of_scope or []
        self.verification_method = verification_method
        self.ratified_at = ratified_at or datetime.now().isoformat()

    def to_dict(self) -> Dict:
        return {
            'goal': self.goal,
            'expected_result': self.expected_result,
            'success_criteria': self.success_criteria,
            'constraints': self.constraints,
            'out_of_scope': self.out_of_scope,
            'verification_method': self.verification_method,
            'ratified_at': self.ratified_at
        }

    def would_break(self, action_description: str) -> bool:
        """Check if an action would break the agreement"""
        action_lower = action_description.lower()
        # Out of scope = automatic break
        for oos in self.out_of_scope:
            if oos.lower() in action_lower:
                return True
        # Constraint violation
        for constraint in self.constraints:
            if f'violate {constraint.lower()}' in action_lower or \
               f'break {constraint.lower()}' in action_lower or \
               f'ignore {constraint.lower()}' in action_lower:
                return True
        return False

    def matches_expected(self, actual_result: str) -> bool:
        """Check if the actual result matches the expected criteria"""
        actual_lower = actual_result.lower()
        # All success criteria must appear in the result
        for criterion in self.success_criteria:
            if criterion.lower() not in actual_lower:
                # Check key terms (extract first significant word)
                key_word = criterion.lower().split()[0] if criterion.split() else ''
                if key_word and key_word not in actual_lower:
                    return False
        return True


class BimodalWorkflow:
    """
    The bimodal workflow engine.

    Lifecycle:
      MODE_A -> [reasoning] -> R0 -> [ratification] -> MODE_B -> [execution] -> result
      Any interruption in MODE_B -> halt + AUTOMATIC restart at MODE_A
      STOP = halt + report + ask user + wait
    """

    MAX_CONSECUTIVE_FAILURES = 5  # 5 failures in a row -> STOP

    def __init__(self):
        self.mode = WorkflowMode.MODE_A
        self.agreement: Optional[AgreementContract] = None
        self.execution_attempts = 0
        self.consecutive_failures = 0
        self.last_success: Optional[str] = None
        self.history: List[Dict] = []
        self.stop_reason: Optional[str] = None
        self.stopped_at: Optional[str] = None
        self.stop_context: Optional[Dict] = None
        self.acknowledgements: List[Dict] = []
        self.priority = list(PRIORITY_HIERARCHY)

    # ----- State persistence -----

    def persist(self):
        """Persist state to disk. Called after EVERY state mutation."""
        state = {
            'mode': self.mode.value,
            'agreement': self.agreement.to_dict() if self.agreement else None,
            'execution_attempts': self.execution_attempts,
            'consecutive_failures': self.consecutive_failures,
            'last_success': self.last_success,
            'stop_reason': self.stop_reason,
            'stopped_at': self.stopped_at,
            'stop_context': self.stop_context,
            'acknowledgements': self.acknowledgements[-20:],
            'priority': self.priority,
            'history_tail': self.history[-50:],
            'updated_at': datetime.now().isoformat()
        }
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding='utf-8')

    def load(self) -> bool:
        """Load state from disk"""
        if not STATE_FILE.exists():
            return False
        try:
            data = json.loads(STATE_FILE.read_text(encoding='utf-8'))
            self.mode = WorkflowMode(data['mode'])
            if data.get('agreement'):
                a = data['agreement']
                self.agreement = AgreementContract(
                    goal=a['goal'],
                    expected_result=a['expected_result'],
                    success_criteria=a['success_criteria'],
                    constraints=a.get('constraints', []),
                    out_of_scope=a.get('out_of_scope', []),
                    verification_method=a.get('verification_method', ''),
                    ratified_at=a.get('ratified_at')
                )
            self.execution_attempts = data.get('execution_attempts', 0)
            self.consecutive_failures = data.get('consecutive_failures', 0)
            self.last_success = data.get('last_success')
            self.stop_reason = data.get('stop_reason')
            self.stopped_at = data.get('stopped_at')
            self.stop_context = data.get('stop_context')
            self.acknowledgements = data.get('acknowledgements', [])
            self.priority = data.get('priority', list(PRIORITY_HIERARCHY))
            self.history = data.get('history_tail', [])
            return True
        except Exception:
            return False

    # ----- Mode transitions -----

    def enter_mode_a(self, reason: str = '', force: bool = False):
        """Enter MODE_A - the analysis / debate / plan phase.

        REFUSES while STOPPED unless `force=True`. STOP means report, ask and
        wait, so the only way out of STOPPED is acknowledge_stop(), which
        records the user input that authorised resuming. A plain transition to
        MODE_A from STOPPED would silently cancel a STOP that the operator
        never saw, which is the exact failure this state machine exists to
        prevent.
        """
        if self.mode == WorkflowMode.STOPPED and not force:
            raise StopRequired(
                'Workflow is STOPPED. acknowledge_stop(user_input) is the only '
                'legal exit. Nothing was changed.',
                self.mode,
                {'stop_reason': self.stop_reason, 'stopped_at': self.stopped_at}
            )
        old = self.mode
        self.mode = WorkflowMode.MODE_A
        # When returning to Mode A, the agreement is invalidated
        # because the situation has changed
        self.agreement = None
        self.consecutive_failures = 0
        self.execution_attempts = 0
        self._log_transition(old, WorkflowMode.MODE_A, reason)
        self.persist()

    def propose_r0(
        self,
        goal: str,
        expected_result: str,
        success_criteria: List[str],
        constraints: Optional[List[str]] = None,
        out_of_scope: Optional[List[str]] = None,
        verification_method: str = ''
    ) -> AgreementContract:
        """
        Propose an R0 agreement.
        Only allowed from MODE_A. If in another mode, AUTOMATICALLY go to MODE_A first
        (because we cannot assume R0 for anything not properly agreed upon).

        REFUSES while STOPPED: proposing a new agreement is a way of continuing
        without asking, and STOP is defined as asking first.
        """
        if self.mode == WorkflowMode.STOPPED:
            raise StopRequired(
                'Cannot propose R0 while STOPPED. Report, ask, and wait for '
                'acknowledge_stop(user_input) first.',
                self.mode,
                {'stop_reason': self.stop_reason}
            )
        if self.mode != WorkflowMode.MODE_A:
            # Rule: Never assume R0 for anything not agreed upon
            # First go back to Mode A to reason properly
            self.enter_mode_a('Cannot propose R0 from current mode')

        contract = AgreementContract(
            goal=goal,
            expected_result=expected_result,
            success_criteria=success_criteria,
            constraints=constraints,
            out_of_scope=out_of_scope,
            verification_method=verification_method
        )

        old = self.mode
        self.mode = WorkflowMode.R0
        self.agreement = contract
        self._log_transition(old, WorkflowMode.R0, f'Agreement proposed: {goal}')
        self.persist()
        return contract

    def ratify_r0(self) -> bool:
        """
        Ratify the R0 agreement - both parties consent.
        Transitions to MODE_B for execution.
        Returns True on success, False if no agreement exists.
        """
        if self.mode != WorkflowMode.R0:
            return False
        if self.agreement is None:
            return False

        old = self.mode
        self.mode = WorkflowMode.MODE_B
        self.execution_attempts = 0
        self.consecutive_failures = 0
        self._log_transition(old, WorkflowMode.MODE_B, 'Agreement ratified')
        self.persist()
        return True

    def halt_to_mode_a(self, reason: str):
        """
        Halt execution and AUTOMATICALLY return to MODE_A.
        This is the correct response to a Mode B INTERRUPTION.
        Returning to R0 would just loop - we need fresh reasoning.

        This is deliberately NOT what a STOP does. An interruption means "keep
        thinking"; a STOP means "report, ask, and wait". Before 2026-10-04 both
        paths ended in MODE_A with stop_reason cleared, so a real STOP was
        indistinguishable from a routine interruption to every observer, the
        MCP tools and the persistence layer. A STOP now lands in
        WorkflowMode.STOPPED and is only left through acknowledge_stop().
        """
        if self.mode == WorkflowMode.STOPPED:
            raise StopRequired(
                'Cannot halt to MODE_A from STOPPED. Use acknowledge_stop().',
                self.mode, {'stop_reason': self.stop_reason}
            )
        old = self.mode
        self.enter_mode_a(f'HALT from {old.value}: {reason}')
        # An interruption is not a stop, so any stale stop state is cleared and
        # the change is persisted. Previously this assignment happened AFTER
        # persist() and was never written to disk.
        self.stop_reason = None
        self.stopped_at = None
        self.stop_context = None
        self.persist()

    # ----- Mode B execution -----

    def execute_step(self, action: str, executor: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Execute a step in MODE_B.
        Validates against agreement and tracks failures.

        HARD RULES enforced here:
        1. Action must not break R0 -> else STOP
        2. Result must match expected -> else count failure
        3. 5 consecutive failures -> STOP (and back to MODE_A)
        4. Interruption -> STOP + back to MODE_A

        Returns dict with status, mode, attempts, and stop_reason if halted.
        """
        if self.mode == WorkflowMode.STOPPED:
            return {
                'status': 'BLOCKED_BY_STOP',
                'mode': self.mode.value,
                'stop_reason': self.stop_reason,
                'stopped_at': self.stopped_at,
                'awaiting_user_input': True,
                'message': 'STOPPED: the workflow is waiting for user input. '
                           'acknowledge_stop(user_input) is the only exit. '
                           'Nothing was executed.'
            }

        if self.mode != WorkflowMode.MODE_B:
            return {
                'status': 'NOT_IN_MODE_B',
                'mode': self.mode.value,
                'message': f'Cannot execute: current mode is {self.mode.value}, not MODE_B'
            }

        if self.agreement is None:
            self._stop('No active agreement in MODE_B')
            return {'status': 'STOPPED', 'mode': self.mode.value,
                    'stop_reason': self.stop_reason, 'stopped_at': self.stopped_at}

        # Rule: if action would break R0 -> STOP
        if self.agreement.would_break(action):
            self._stop(f'Action would break R0 agreement: {action}')
            return {
                'status': 'STOPPED_R0_BREACH',
                'mode': self.mode.value,
                'stop_reason': self.stop_reason,
                'stopped_at': self.stopped_at,
                'awaiting_user_input': True,
                'message': 'STOP: this action would break the R0 agreement. The workflow is '
                           'STOPPED and waiting for user input. It does not fall back to MODE_A.'
            }

        # Execute (if executor provided, otherwise just record the action)
        self.execution_attempts += 1
        result = ''
        executor_error = None

        if executor:
            try:
                result = executor(action) or ''
            except Exception as e:
                executor_error = str(e)
                result = f'EXECUTOR_ERROR: {executor_error}'
        else:
            # No executor: record the action as a planning step
            result = f'PLANNED: {action}'

        # Check if result matches expected
        matches = self.agreement.matches_expected(result) and executor_error is None

        if matches:
            self.consecutive_failures = 0
            self.last_success = result
        else:
            self.consecutive_failures += 1
            if self.consecutive_failures >= self.MAX_CONSECUTIVE_FAILURES:
                self._stop(
                    f'{self.MAX_CONSECUTIVE_FAILURES} consecutive failures in MODE_B. '
                    f'Last attempt: {action[:100]}. Reverting to MODE_A for fresh analysis.'
                )
                return {
                    'status': 'STOPPED_MAX_FAILURES',
                    'mode': self.mode.value,
                    'stop_reason': self.stop_reason,
                    'stopped_at': self.stopped_at,
                    'consecutive_failures': self.consecutive_failures,
                    'awaiting_user_input': True,
                    'message': f'STOP: {self.MAX_CONSECUTIVE_FAILURES} failed attempts. '
                               f'The workflow is STOPPED and waiting for user input; it does '
                               f'not continue on its own.'
                }

        self._log_event({
            'event': 'execution_attempt',
            'attempt': self.execution_attempts,
            'action': action,
            'result': result[:200],
            'matches_expected': matches,
            'consecutive_failures': self.consecutive_failures
        })
        self.persist()

        return {
            'status': 'OK' if matches else 'MISMATCH',
            'mode': self.mode.value,
            'attempt': self.execution_attempts,
            'consecutive_failures': self.consecutive_failures,
            'result': result[:500],
            'message': 'Success' if matches else 'Result does not match expected criteria. Continuing attempts.'
        }

    def report_interruption(self, reason: str):
        """
        Called when Mode B execution is cut off or interrupted.
        Per protocol: AUTOMATICALLY restart at MODE_A (NOT R0).
        Because returning to R0 would loop without fresh context.
        """
        self.halt_to_mode_a(f'INTERRUPTION: {reason}')

    # ----- STOP -----

    def _stop(self, reason: str):
        """Enter the STOPPED state: report, ask for user input, and WAIT.

        The workflow does NOT continue and does NOT fall back to MODE_A. The
        doctrine distinguishes an interruption (keep reasoning) from a STOP
        (wait for the operator), and collapsing the two makes the strongest
        safety rule in the system unobservable.
        """
        previous = self.mode
        self.mode = WorkflowMode.STOPPED
        self.stop_reason = reason
        self.stopped_at = datetime.now().isoformat()
        self.stop_context = {
            'previous_mode': previous.value,
            'consecutive_failures': self.consecutive_failures,
            'execution_attempts': self.execution_attempts,
            'agreement_goal': self.agreement.goal if self.agreement else None,
        }
        self._log_transition(previous, WorkflowMode.STOPPED, f'STOP: {reason}')
        self._log_event({
            'event': 'STOP',
            'reason': reason,
            'stopped_at': self.stopped_at,
            'previous_mode': previous.value,
            'consecutive_failures': self.consecutive_failures,
            'awaiting': 'user input - acknowledge_stop() is the only exit',
        })
        self.persist()

    def acknowledge_stop(self, user_input: str):
        """The ONLY legal exit from STOPPED. Records the input that authorised resuming.

        STOP means report, ask, and wait. This method is that wait ending: the
        operator's answer is stored with a timestamp, and only then does the
        workflow return to MODE_A for fresh reasoning.
        """
        if self.mode != WorkflowMode.STOPPED:
            raise StopRequired(
                f'Not STOPPED (mode={self.mode.value}); nothing to acknowledge.',
                self.mode, {'stop_reason': self.stop_reason}
            )
        if not user_input or not str(user_input).strip():
            raise StopRequired(
                'acknowledge_stop requires the user input that authorised resuming. '
                'An empty acknowledgement is not an acknowledgement.',
                self.mode, {'stop_reason': self.stop_reason}
            )
        record = {
            'acknowledged_at': datetime.now().isoformat(),
            'user_input': str(user_input),
            'stop_reason': self.stop_reason,
            'stopped_at': self.stopped_at,
            'stop_context': self.stop_context,
        }
        self.acknowledgements.append(record)
        self._log_event({'event': 'STOP_ACKNOWLEDGED', **record})
        self.stop_reason = None
        self.stopped_at = None
        self.stop_context = None
        self.enter_mode_a(
            f'RESUME after STOP (acknowledged): {str(user_input)[:120]}', force=True)
        return record

    def stop_report(self) -> Dict[str, Any]:
        """What an observer (MCP tool, monitor, dashboard) must be able to read.

        This exists so "the system has stopped" is a queryable fact rather than
        an inference from a log line.
        """
        return {
            'is_stopped': self.is_stopped(),
            'mode': self.mode.value,
            'stop_reason': self.stop_reason,
            'stopped_at': self.stopped_at,
            'stop_context': self.stop_context,
            'awaiting_user_input': self.mode == WorkflowMode.STOPPED,
            'exit_method': 'acknowledge_stop(user_input)',
            'consecutive_failures': self.consecutive_failures,
            'max_consecutive_failures': self.MAX_CONSECUTIVE_FAILURES,
        }

    def is_stopped(self) -> bool:
        """Check if workflow is currently in STOPPED state"""
        return self.mode == WorkflowMode.STOPPED or self.stop_reason is not None

    def get_stop_reason(self) -> Optional[str]:
        """Return the stop reason if any"""
        return self.stop_reason

    # ----- Priority checks -----

    def check_priority_violation(self, proposed_action: str) -> Optional[str]:
        """
        Check if a proposed action violates the priority hierarchy.
        Priority: SYSTEM > TASK > SPEED > USER_FEELINGS.
        Returns the violated priority or None.
        """
        action_lower = proposed_action.lower()
        # Sacrificing system integrity for task speed = violation
        if ('skip' in action_lower or 'bypass' in action_lower) and \
           ('safety' in action_lower or 'integrity' in action_lower or 'check' in action_lower):
            return 'SYSTEM_INTEGRITY'
        # Sacrificing system for user feelings (fabrication to please) = violation
        if 'pretend' in action_lower and ('done' in action_lower or 'complete' in action_lower):
            return 'SYSTEM_INTEGRITY'
        if 'fabricate' in action_lower or 'make up' in action_lower:
            return 'SYSTEM_INTEGRITY'
        return None

    # ----- Logging -----

    def _log_transition(self, old: WorkflowMode, new: WorkflowMode, reason: str):
        """Log a state transition"""
        entry = {
            'event': 'transition',
            'timestamp': datetime.now().isoformat(),
            'from': old.value,
            'to': new.value,
            'reason': reason
        }
        self.history.append(entry)
        self._write_log(entry)

    def _log_event(self, entry: Dict):
        """Log a generic event"""
        entry = {'timestamp': datetime.now().isoformat(), **entry}
        self.history.append(entry)
        self._write_log(entry)

    def _write_log(self, entry: Dict):
        """Write to bimodal log file"""
        log_file = WORKSPACE / '09_LOGS' / 'bimodal_workflow.log'
        log_file.parent.mkdir(parents=True, exist_ok=True)
        line = f"[{entry['timestamp']}] {json.dumps(entry, ensure_ascii=False)}\n"
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(line)

    # ----- Reporting -----

    def status_report(self) -> str:
        """Generate status report"""
        agreement_str = 'None'
        if self.agreement:
            a = self.agreement
            agreement_str = (
                f'Goal: {a.goal}\n'
                f'    Expected: {a.expected_result}\n'
                f'    Criteria: {", ".join(a.success_criteria)}'
            )

        return f"""
====================================================
BIMODAL WORKFLOW - Status Report
====================================================
Mode: {self.mode.value}
Stopped: {'YES - waiting for user input' if self.is_stopped() else 'no'}
Stop reason: {self.stop_reason or 'None'}
Stopped at: {self.stopped_at or 'None'}
Stop context: {json.dumps(self.stop_context, ensure_ascii=False) if self.stop_context else 'None'}
Acknowledgements: {len(self.acknowledgements)}
Exit from STOPPED: acknowledge_stop(user_input) - the only legal exit
Execution attempts: {self.execution_attempts}
Consecutive failures: {self.consecutive_failures}/{self.MAX_CONSECUTIVE_FAILURES}
Last success: {(self.last_success or 'None')[:80]}

Priority hierarchy (immutable):
  1. {self.priority[0]}
  2. {self.priority[1]}
  3. {self.priority[2]}
  4. {self.priority[3]}

Agreement: {agreement_str}
History entries: {len(self.history)}
====================================================
"""


def _demo():
    """State-changing walkthrough. NOT what `status` does, and never the default.

    This walks the workflow through a full MODE_A -> R0 -> MODE_B -> interruption
    cycle and writes every transition to the live state file. It exists to show
    the engine working, so calling it against a live workspace overwrites the real
    workflow state with a fiction ("Translate code to English"). That is why the
    default CLI verb is `status` and not this.
    """
    print("=" * 60)
    print("SENTINEL Bimodal Workflow Demo")
    print("=" * 60)

    wf = BimodalWorkflow()

    # 1. MODE_A: reason
    print("\n1. Entering MODE_A (analyze, plan)")
    wf.enter_mode_a('Starting fresh analysis')
    print(f"   Mode: {wf.mode.value}")

    # 2. R0: propose agreement
    print("\n2. Proposing R0 agreement")
    contract = wf.propose_r0(
        goal='Translate code to English',
        expected_result='All Romanian diacritics removed from .py files',
        success_criteria=['zero diacritics in test output'],
        constraints=['do not modify .md wisdom files'],
        out_of_scope=['modify foundation doctrine content']
    )
    print(f"   Mode: {wf.mode.value}")
    print(f"   Goal: {contract.goal}")

    # 3. Ratify R0 -> MODE_B
    print("\n3. Ratifying R0 -> entering MODE_B")
    ratified = wf.ratify_r0()
    print(f"   Ratified: {ratified}")
    print(f"   Mode: {wf.mode.value}")

    # 4. Execute a successful step
    print("\n4. Executing successful step")
    result = wf.execute_step('Run translation on file 1', lambda _: 'zero diacritics in test output: PASS')
    print(f"   Status: {result['status']}")

    # 5. Simulate interruption -> back to MODE_A
    print("\n5. Reporting interruption (network failure)")
    wf.report_interruption('Network timeout during execution')
    print(f"   Mode: {wf.mode.value}")

    # 6. Print status
    print(wf.status_report())

    print("\n" + "=" * 60)
    print("Bimodal workflow demo complete")
    print("=" * 60)


USAGE = """usage: bimodal_workflow.py [verb] [args]

  status                 read-only. Print the workflow status report. DEFAULT.
  stop-report            read-only. Print the STOP report as JSON.
  ack-stop "<input>"     the ONLY exit from STOPPED. Requires the operator's words.
                         An empty acknowledgement is refused, by design.
  interrupt "<reason>"   MODE_B interrupted -> back to MODE_A (never R0).
  demo                   state-changing walkthrough. Overwrites live state.

The default verb is `status` because a command whose name does not mention
mutation must not mutate. See _demo() for why that distinction is load-bearing.
"""


def main(argv: Optional[List[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    verb = argv[0] if argv else 'status'
    rest = argv[1:]

    if verb in ('-h', '--help', 'help'):
        print(USAGE)
        return 0

    if verb == 'status':
        wf = BimodalWorkflow()
        wf.load()
        print(wf.status_report())
        return 0

    if verb == 'stop-report':
        wf = BimodalWorkflow()
        wf.load()
        print(json.dumps(wf.stop_report(), indent=2, ensure_ascii=False))
        return 0

    if verb == 'ack-stop':
        if not rest or not rest[0].strip():
            # Deliberately not defaulted. The exit from STOPPED is the operator's
            # words being recorded; accepting "" would make the gate a no-op while
            # still looking like one.
            print('REFUSED: ack-stop requires the operator input that authorised '
                  'resuming. Pass it as a quoted argument.', file=sys.stderr)
            return 3
        wf = BimodalWorkflow()
        wf.load()
        try:
            wf.acknowledge_stop(rest[0])
        except StopRequired as exc:
            print('REFUSED: %s' % exc, file=sys.stderr)
            return 4
        print(wf.status_report())
        return 0

    if verb == 'interrupt':
        # Named for what halt_to_mode_a actually does. There is deliberately no
        # CLI verb that force-enters STOPPED: a stop is the engine's response to
        # five failed steps or a broken contract, not something an operator
        # triggers by command.
        reason = rest[0] if rest else 'interruption reported from CLI'
        wf = BimodalWorkflow()
        wf.load()
        wf.halt_to_mode_a(reason)
        print(wf.status_report())
        return 0

    if verb == 'demo':
        _demo()
        return 0

    print('unknown verb: %s\n' % verb, file=sys.stderr)
    print(USAGE, file=sys.stderr)
    return 2


if __name__ == '__main__':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass
    sys.exit(main())
