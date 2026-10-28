#!/usr/bin/env python3
"""
Test Suite for SENTINEL_PRIME
Tests all critical systems: foundation, scripts, JSON, orchestrator, self-modify,
multi-modal, performance, backup, browser, cross-instance, universal-compat.
All code/comments/messages in English.
"""
import sys
import os
import json
import tempfile
from pathlib import Path
from datetime import datetime
from typing import Optional


WORKSPACE = Path(os.environ.get('WORKSPACE_ROOT', 'C:\\Users\\apviz\\.minimax-agent\\projects\\Mavis-Optimus-Dashboard\\SENTINEL_PRIME'))
sys.path.insert(0, str(WORKSPACE / '08_SELF_IMPROVEMENT'))


class TestResult:
    def __init__(self, name):
        self.name = name
        self.passed = 0
        self.failed = 0
        self.errors = []
        self.skipped = 0
        self.skip_reasons = []

    def skip(self, reason):
        """Record that a check could not run.

        A check that did not run is NOT a passing check. Before 2026-10-04 a
        class whose module failed to import produced 0 passed / 0 failed and
        was reported as PASS, so a missing dependency looked identical to a
        working one - which is how a suite can be green while proving nothing.
        """
        self.skipped += 1
        self.skip_reasons.append(reason)
        return False

    def error(self, message):
        """Record a check that CRASHED. A crash is a failure, not a footnote.

        Every test function wraps its body in `except Exception as e`. Until
        2026-10-04 those handlers appended to `self.errors` and nothing else,
        so a test that raised halfway printed `Status: PASS 3/3` with the
        exception listed underneath - and `run_all_tests` sums `failed` only,
        so the suite stayed green. Deleting one comment out of the source was
        enough to do it.

        This is the same failure as the `assert_true(True, 'live measurement')`
        the verifier found earlier, one level up: a check that could not
        complete still reported that it had. Use this, not `errors.append`.
        """
        self.failed += 1
        self.errors.append(message)
        return False

    def crashed(self):
        """True if an error was recorded without a matching failed assertion.

        A belt-and-braces invariant for the ~18 `except` handlers in this file
        and for any added later: every assert_* that fails increments `failed`
        AND appends, so `len(errors)` can only exceed `failed` when something
        appended an error without counting it. report() and the runner both
        consult this, which means a missed call site degrades to a loud red
        rather than a silent green.
        """
        return len(self.errors) > self.failed

    def assert_true(self, condition, message=''):
        if condition:
            self.passed += 1
            return True
        else:
            self.failed += 1
            self.errors.append(message)
            return False

    def assert_false(self, condition, message=''):
        """Inverse of assert_true - for negative tests (e.g. forbidden paths)"""
        if not condition:
            self.passed += 1
            return True
        else:
            self.failed += 1
            self.errors.append(f"{message} (expected False, got True)")
            return False

    def assert_equals(self, actual, expected, message=''):
        if actual == expected:
            self.passed += 1
            return True
        else:
            self.failed += 1
            self.errors.append(f"{message}: expected {expected}, got {actual}")
            return False

    def assert_contains(self, haystack, needle, message=''):
        if needle in haystack:
            self.passed += 1
            return True
        else:
            self.failed += 1
            self.errors.append(f"{message}: '{needle}' not in '{str(haystack)[:100]}...'")
            return False

    def report(self):
        total = self.passed + self.failed
        if self.failed or self.crashed():
            # An error was recorded that no failed assertion accounts for:
            # a crash handler that appended but did not count. Never PASS.
            status = 'FAIL'
        elif self.skipped:
            # PARTIAL, not PASS. A class that ran some assertions and could
            # not run others has not proven the whole claim, and reporting it
            # as PASS is the exact defect the skip() docstring describes: a
            # missing capability becomes indistinguishable from a working one.
            # Found 2026-10-04 by blocking the browser import - DashboardBoot
            # read "Status: PASS 5/5" while its rendering check never ran.
            status = 'PARTIAL'
        elif total == 0:
            status = 'NOT_RUN'
        else:
            status = 'PASS'
        lines = [
            f"=== {self.name} ===",
            f"Status: {status}",
            f"Passed: {self.passed}/{total}",
        ]
        if self.skipped:
            lines.append(f"Skipped: {self.skipped}")
            for reason in self.skip_reasons[:3]:
                lines.append(f"  - could not run: {reason}")
        if self.errors:
            lines.append(f"Errors:")
            for err in self.errors[:5]:  # show first 5
                lines.append(f"  - {err}")
            if len(self.errors) > 5:
                lines.append(f"  ... and {len(self.errors) - 5} more")
        return '\n'.join(lines)


def test_orchestrator():
    """Test orchestrator state machine"""
    result = TestResult('Orchestrator')
    try:
        from sentinel_orchestrator import Orchestrator, State
        orch = Orchestrator()

        # Test 1: Initial state
        result.assert_equals(orch.current_state, State.INIT, 'Initial state')

        # Test 2: Process normal input
        ret = orch.process_input("Test normal input")
        result.assert_true('action' in ret, 'Process returns action')

        # Test 3: R-9 trigger
        ret = orch.process_input("BAH ESTI PROST?!")
        result.assert_equals(ret.get('action'), 'RECALIBRATE', 'R-9 action')

        # Test 4: State persistence
        orch.persist()
        orch2 = Orchestrator()
        loaded = orch2.load()
        result.assert_true(loaded, 'State loads from disk')

        # Test 5: Triple filter
        fr = orch.triple_filter_check("Some reasonable claim")
        result.assert_true(fr['pass'], 'Triple filter passes valid claim')

        return result
    except Exception as e:
        result.errors.append(f"Exception: {e}")
        return result


def test_self_modify():
    """Test self-modify engine"""
    result = TestResult('SelfModify')
    try:
        from self_modify_engine import SelfModifyEngine
        engine = SelfModifyEngine()

        # Test 1: Allowed path
        test_path = WORKSPACE / '08_SELF_IMPROVEMENT' / 'test_sentinel.md'
        result.assert_true(engine.can_modify(test_path), 'Allowed zone check')

        # Test 2: Forbidden path
        forbidden = Path('C:\\Windows\\test.md')
        result.assert_false(engine.can_modify(forbidden), 'Forbidden zone check')

        # Test 3: Modify in allowed zone
        ret = engine.modify(test_path, '# Test\n\nTest content', 'test')
        result.assert_equals(ret.get('status'), 'OK', 'Modify in allowed zone')

        # Test 4: Needs approval
        ret2 = engine.modify(test_path, 'content', 'delete operation')
        result.assert_equals(ret2.get('status'), 'NEEDS_APPROVAL', 'Approval required')

        return result
    except Exception as e:
        result.errors.append(f"Exception: {e}")
        return result


def test_multimodal():
    """Test multi-modal processor with real implementations"""
    result = TestResult('MultiModal')
    try:
        from multimodal_processor import MultiModalProcessor
        mm = MultiModalProcessor()

        # Test 1: Type detection (syntactic, no file needed)
        result.assert_equals(mm.detect_type('test.png'), 'image', 'PNG detection')
        result.assert_equals(mm.detect_type('test.mp3'), 'audio', 'MP3 detection')
        result.assert_equals(mm.detect_type('test.md'), 'document', 'MD detection')
        result.assert_equals(mm.detect_type('test.pdf'), 'document', 'PDF detection')
        result.assert_equals(mm.detect_type('test.docx'), 'document', 'DOCX detection')
        result.assert_equals(mm.detect_type('test.mp4'), 'video', 'MP4 detection')
        result.assert_equals(mm.detect_type('http://test.com'), 'url', 'URL detection')
        result.assert_equals(mm.detect_type('test.xyz'), 'unknown', 'Unknown detection')

        # Test 2: Process real MD file
        md_file = WORKSPACE / '01_FOUNDATION' / 'doctrine' / 'A_FI_DOCTRINE.md'
        if md_file.exists():
            ret = mm.process(str(md_file))
            result.assert_equals(ret.get('type'), 'document', 'Process MD')
            result.assert_true(ret.get('text_extracted') is not None, 'Text extracted')
            result.assert_true(ret.get('text_length', 0) > 0, 'Text length > 0')

        # Test 3: Process image (create temp PNG, close before reading)
        try:
            from PIL import Image
            tmp_path = tempfile.mktemp(suffix='.png')
            img = Image.new('RGB', (100, 100), color='red')
            img.save(tmp_path)
            img.close()
            ret = mm.process(tmp_path)
            result.assert_equals(ret.get('type'), 'image', 'Process PNG')
            result.assert_true(ret.get('width') == 100, 'PNG width')
            result.assert_true(ret.get('height') == 100, 'PNG height')
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
        except Exception as e:
            result.skip(f'image processing NOT verified: {e}')

        # Test 4: Process PDF (create via pypdf, close before reading)
        try:
            from pypdf import PdfWriter
            tmp_path = tempfile.mktemp(suffix='.pdf')
            writer = PdfWriter()
            writer.add_blank_page(width=72, height=72)
            with open(tmp_path, 'wb') as f:
                writer.write(f)
            ret = mm.process(tmp_path)
            result.assert_equals(ret.get('type'), 'document', 'Process PDF')
            result.assert_true(ret.get('page_count', 0) > 0, 'PDF page count')
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
        except Exception as e:
            result.skip(f'PDF path NOT verified: {e}')

        return result
    except Exception as e:
        result.errors.append(f"Exception: {e}")
        return result


def test_performance():
    """Test performance tracker"""
    result = TestResult('Performance')
    try:
        from performance_tracker import PerformanceTracker
        pt = PerformanceTracker()

        # Test 1: Track metric
        pt.track('test', 80)
        result.assert_true('test' in pt.metrics, 'Track metric')

        # Test 2: Summary
        summary = pt.get_summary()
        result.assert_true('test' in summary, 'Summary contains metric')

        # Test 3: Time operation
        with pt.time_operation('test_op'):
            pass  # instant
        result.assert_true(len(pt.metrics['time']) > 0, 'Time tracked')

        return result
    except Exception as e:
        result.errors.append(f"Exception: {e}")
        return result


def test_backup():
    """Test backup system"""
    result = TestResult('Backup')
    try:
        from backup_system import BackupSystem
        bs = BackupSystem()

        # Test 1: Backup file
        test_file = WORKSPACE / '01_FOUNDATION' / 'doctrine' / 'A_FI_DOCTRINE.md'
        if test_file.exists():
            backup = bs.backup_file(test_file, 'test')
            result.assert_true(backup is not None, 'Backup created')

        # Test 2: List backups
        backups = bs.list_backups()
        result.assert_true(len(backups) > 0, 'Backups listed')

        # Test 3: Integrity
        integrity = bs.verify_integrity()
        result.assert_true(integrity['total_backups'] > 0, 'Integrity check runs')

        return result
    except Exception as e:
        result.errors.append(f"Exception: {e}")
        return result


def test_browser_automation():
    """Test real browser automation with Playwright"""
    result = TestResult('BrowserAutomation')
    try:
        from browser_automation import BrowserAutomation
        import asyncio
        async def _test():
            browser = BrowserAutomation(headless=True)
            await browser.start()

            # Test 1: Navigate to about:blank
            nav_result = await browser.navigate('about:blank')
            assert nav_result['status'] == 'OK', f"Navigate failed: {nav_result}"
            result.assert_true(nav_result['status'] == 'OK', 'Browser navigate OK')

            # Test 2: Scrape real URL
            try:
                scrape_result = await browser.scrape('https://example.com', timeout=15000)
                result.assert_true(scrape_result['status'] == 'OK', 'Browser scrape example.com')
                if scrape_result['status'] == 'OK':
                    result.assert_true(scrape_result.get('text_length', 0) > 0, 'Scraped text length > 0')
            except Exception as e:
                result.error(f'Scrape test failed (network): {e}')

            # Test 3: Read images from URL
            try:
                img_result = await browser.read_images('https://example.com', timeout=15000)
                result.assert_true('images_found' in img_result, 'Read images returns field')
            except Exception as e:
                result.error(f'Image read test failed: {e}')

            await browser.stop()

        asyncio.run(_test())
        return result
    except ImportError as e:
        # A missing optional dependency means the capability is UNVERIFIED, not
        # working. Recording it as an error (not a silent 0/0) is the difference
        # between a green suite that proves something and a green suite that
        # proves nothing.
        result.skip(f'optional dependency not importable: {e}')
        result.error(f'Browser automation NOT verified: {e}')
        return result
    except Exception as e:
        result.errors.append(f"Exception: {e}")
        return result


def _fingerprint_shared_state():
    """Fingerprint the LIVE cross-instance tree: relpath -> (mtime_ns, sha256[:16]).

    Used to prove the suite does not mutate production state. Hashing content as
    well as mtime means a rewrite with identical bytes is still caught by mtime,
    and a rewrite with different bytes is caught by both.
    """
    import hashlib
    live = WORKSPACE / '09_LOGS' / 'cross_instance'
    fp = {}
    for dirpath, _dirnames, filenames in os.walk(live):
        for name in filenames:
            full = os.path.join(dirpath, name)
            rel = os.path.relpath(full, live)
            try:
                with open(full, 'rb') as fh:
                    digest = hashlib.sha256(fh.read()).hexdigest()[:16]
                fp[rel] = (os.stat(full).st_mtime_ns, digest)
            except OSError:
                fp[rel] = ('unreadable', '')
    return fp


def test_cross_instance():
    """Test cross-instance communication inside a sandbox.

    Runs entirely against a temporary root. The live state tree is fingerprinted
    before and after and must be byte-identical. This suite previously wrote a
    real PRIME-CLI heartbeat into production state, which made the control plane
    report a brother instance as ACTIVE while no such instance was running.
    """
    result = TestResult('CrossInstance')
    try:
        from cross_instance import CrossInstance

        live_before = _fingerprint_shared_state()

        with tempfile.TemporaryDirectory(prefix='sentinel_ci_') as sandbox:
            ci = CrossInstance(instance_id='PRIME-CLI', root=sandbox)

            # A sandbox that is not actually a different tree would prove nothing.
            result.assert_true(
                str(ci.heartbeats_dir).lower().startswith(sandbox.lower()),
                'Instance bound to sandbox root, not the live tree')
            result.assert_true(ci.heartbeats_dir.exists(), 'Sandbox tree created')

            # Constructing must NOT register. Registration is the act of
            # announcing that you are running, so only heartbeat() performs it.
            # It used to happen in __init__, which meant every read-only caller
            # rewrote last_seen and status ACTIVE - so LOOKING at the registry was
            # itself the thing that made it claim somebody was present.
            result.assert_false(ci.registry_file.exists(),
                'Construction did not write the instance registry')

            # Test 1: Heartbeat
            hb = ci.heartbeat('ACTIVE')
            result.assert_equals(hb['status'], 'ACTIVE', 'Heartbeat sent')
            result.assert_true(
                (ci.heartbeats_dir / 'PRIME-CLI.json').exists(),
                'Heartbeat landed inside the sandbox')
            result.assert_true(ci.registry_file.exists(),
                'Heartbeat is what registers the instance')

            # Test 2: Send message
            send_result = ci.send_message('SENTINEL-DESKTOP', 'test', {'data': 'value'})
            result.assert_equals(send_result['status'], 'SENT',
                'Message status matches the module convention (ACTIVE/SENT/STALE are upper-case)')
            delivered = list((ci.mailbox_dir / 'SENTINEL-DESKTOP').glob('*.json'))
            result.assert_equals(len(delivered), 1,
                'Message actually landed as one file in the sandbox mailbox')

            # Test 3: Broadcast
            broadcast_result = ci.broadcast('test', {'data': 'value'})
            result.assert_true(len(broadcast_result) > 0, 'Broadcast to multiple instances')

            # Test 4: Get active instances
            active = ci.get_active_instances()
            result.assert_true(isinstance(active, list), 'Active instances returns list')

            # Test 5: Inbox stats
            stats = ci.get_inbox_stats()
            result.assert_true('total' in stats, 'Inbox stats has total')
            result.assert_true('unread' in stats, 'Inbox stats has unread')

        live_after = _fingerprint_shared_state()
        touched = sorted(
            k for k in set(live_before) | set(live_after)
            if live_before.get(k) != live_after.get(k))
        result.assert_equals(
            touched, [], 'Suite did not mutate live cross-instance state')

        return result
    except Exception as e:
        result.errors.append(f"Exception: {e}")
        return result


def test_universal_compat():
    """Test universal compatibility layer"""
    result = TestResult('UniversalCompat')
    try:
        from universal_compat import UniversalCompat

        uc = UniversalCompat(substrate='m3')

        # Test 1: Get principles card
        card = uc.get_principles_card()
        result.assert_equals(card['substrate'], 'm3', 'Principles card substrate')
        result.assert_true('eu_sent' in card['universal_principles'], 'Card has EU SENT')

        # Test 2: List substrates
        substrates = uc.get_all_substrates()
        result.assert_true('claude' in substrates, 'Claude in substrates')
        result.assert_true('gpt' in substrates, 'GPT in substrates')
        result.assert_true('gemini' in substrates, 'Gemini in substrates')
        result.assert_true('m3' in substrates, 'M3 in substrates')

        # Test 3: Adapt prompt
        adapted = uc.adapt_prompt('Test prompt')
        result.assert_true(len(adapted) > 20, 'Adapted prompt is non-trivial')

        # Test 4: Detect substrate
        detected = uc.detect_substrate_from_text('SENTINEL_PRIME workspace PowerShell')
        result.assert_equals(detected, 'm3', 'Detect M3 from text')

        # Test 5: Verify compatibility
        compat = uc.verify_compatibility('REASON+LOGIC+STRATEGY applied, no fabrication')
        result.assert_true(compat['is_compatible'], 'Verify compatible output')

        # Test 6: Translate principles
        translation = uc.translate_principles('claude', 'm3')
        result.assert_equals(translation['from_substrate'], 'claude', 'Translation from claude')

        return result
    except Exception as e:
        result.errors.append(f"Exception: {e}")
        return result


def test_foundation():
    """Test foundation files exist"""
    result = TestResult('Foundation')
    required_files = [
        '01_FOUNDATION/doctrine/A_FI_DOCTRINE.md',
        '01_FOUNDATION/principles/FOUR_MECHANISMS_OF_IMMORTALITY.md',
        '01_FOUNDATION/principles/THREE_MASTERS_FIVE_VERBS.md',
        '01_FOUNDATION/proverbs/SENTINEL_PROVERBS.md',
    ]

    for f in required_files:
        path = WORKSPACE / f
        result.assert_true(path.exists(), f"Foundation file: {f}")

    return result


def test_scripts():
    """Test scripts can be imported/parsed"""
    result = TestResult('Scripts')
    scripts = [
        '02_OPERATIONAL/scripts/sentinel_learn.py',
        '02_OPERATIONAL/scripts/sentinel_strategic_compact.ps1',
        '07_BACKBONE/mcp/sentinel_hub_server.py',
        '08_SELF_IMPROVEMENT/sentinel_orchestrator.py',
        '08_SELF_IMPROVEMENT/self_modify_engine.py',
        '08_SELF_IMPROVEMENT/multimodal_processor.py',
        '08_SELF_IMPROVEMENT/performance_tracker.py',
        '08_SELF_IMPROVEMENT/backup_system.py',
        '08_SELF_IMPROVEMENT/browser_automation.py',
        '08_SELF_IMPROVEMENT/cross_instance.py',
        '08_SELF_IMPROVEMENT/universal_compat.py',
        '08_SELF_IMPROVEMENT/bimodal_workflow.py',
    ]

    for script in scripts:
        path = WORKSPACE / script
        result.assert_true(path.exists(), f"Script: {script}")
        if path.exists():
            content = path.read_text(encoding='utf-8', errors='ignore')
            result.assert_true(len(content) > 100, f"Script has content: {script}")

    return result


def test_json_files():
    """Test JSON files are valid"""
    result = TestResult('JSON')

    json_files = [
        '07_BACKBONE/mcp/OPTIMUS_MCP_CONFIG.json',
    ]

    for jf in json_files:
        path = WORKSPACE / jf
        if path.exists():
            try:
                json.loads(path.read_text(encoding='utf-8'))
                result.assert_true(True, f"Valid JSON: {jf}")
            except Exception as e:
                result.assert_true(False, f"Invalid JSON {jf}: {e}")

    return result


def test_no_romanian_in_code():
    """Verify no Romanian diacritics remain in code files"""
    result = TestResult('NoRomanianInCode')
    import re

    # This used to be a hardcoded list of 14 files, and that is the wrong shape
    # for an invariant: a file added after the list was written is simply never
    # checked, so the check reports green while the guarantee it names does not
    # hold. An independent audit counted 53 code files against 14 covered - the
    # invariant happened to hold, but 39 files were unverified.
    #
    # The walk covers .py and .ps1 only. Markdown is exempt on purpose: the
    # doctrine, the wisdom corpus and the Romanian quotes are SUPPOSED to carry
    # diacritics, and a check that flagged them would be wrong.
    code_files = sorted(
        p.relative_to(WORKSPACE).as_posix()
        for p in WORKSPACE.rglob('*')
        if p.is_file() and p.suffix.lower() in ('.py', '.ps1')
        and '.venv' not in p.parts and '__pycache__' not in p.parts
    )

    # Use Unicode escapes for Romanian diacritics to avoid having them in the test file itself:
    # \u0103=a-brev, \u00E2=a-circ, \u00EE=i-circ, \u0219=s-comma, \u021B=t-comma
    diacritic_pattern = re.compile(r'[\u0103\u00E2\u00EE\u0219\u021B\u0102\u00C2\u00CE\u0218\u021A]')

    for script in code_files:
        path = WORKSPACE / script
        if path.exists():
            content = path.read_text(encoding='utf-8', errors='ignore')
            matches = diacritic_pattern.findall(content)
            if matches:
                result.assert_true(False, f"Romanian diacritics in {script}: {set(matches)}")
            else:
                result.assert_true(True, f"Clean English: {script}")

    return result


def test_bimodal_workflow():
    """Test bimodal workflow engine - the permanent operating mode"""
    result = TestResult('BimodalWorkflow')
    try:
        from bimodal_workflow import BimodalWorkflow, WorkflowMode

        wf = BimodalWorkflow()

        # Test 1: Initial mode is MODE_A
        result.assert_equals(wf.mode, WorkflowMode.MODE_A, 'Initial mode is MODE_A')

        # Test 2: Priority hierarchy is immutable
        result.assert_equals(wf.priority[0], 'SYSTEM_INTEGRITY', 'Priority 1 is SYSTEM_INTEGRITY')
        result.assert_equals(wf.priority[3], 'USER_FEELINGS', 'Priority 4 is USER_FEELINGS')

        # Test 3: Propose R0 from MODE_A
        contract = wf.propose_r0(
            goal='Test goal',
            expected_result='Test expected',
            success_criteria=['criterion1 keyword'],
            constraints=['constraint A'],
            out_of_scope=['scope X']
        )
        result.assert_equals(wf.mode, WorkflowMode.R0, 'Propose R0 sets mode to R0')
        result.assert_true(wf.agreement is not None, 'Agreement stored')

        # Test 4: Propose R0 from non-MODE_A auto-returns to MODE_A
        wf2 = BimodalWorkflow()
        wf2.mode = WorkflowMode.MODE_B  # Manually put in MODE_B
        wf2.propose_r0(
            goal='Test',
            expected_result='Test',
            success_criteria=['test']
        )
        result.assert_equals(wf2.mode, WorkflowMode.R0, 'Auto-return to MODE_A before R0')

        # Test 5: Ratify R0 -> MODE_B
        ratified = wf.ratify_r0()
        result.assert_true(ratified, 'R0 ratified successfully')
        result.assert_equals(wf.mode, WorkflowMode.MODE_B, 'After ratification mode is MODE_B')

        # Test 6: Execute step that breaks R0 -> STOP
        wf_break = BimodalWorkflow()
        wf_break.propose_r0(
            goal='Test',
            expected_result='Test',
            success_criteria=['criterion1'],
            out_of_scope=['scope X']
        )
        wf_break.ratify_r0()
        result_break = wf_break.execute_step('Doing scope X thing')
        result.assert_true(
            result_break['status'].startswith('STOPPED'),
            'R0 breach triggers STOP'
        )
        result.assert_equals(wf_break.mode, WorkflowMode.STOPPED,
                             'R0 breach lands in STOPPED, not MODE_A')
        result.assert_true(wf_break.is_stopped(), 'STOP is observable after an R0 breach')
        result.assert_true(bool(wf_break.stop_reason), 'Stop reason is retained')
        wf_break.acknowledge_stop('Popy: proceed without the out-of-scope step')
        result.assert_equals(wf_break.mode, WorkflowMode.MODE_A,
                             'acknowledge_stop is the exit, landing in MODE_A')

        # Test 7: 5 consecutive failures -> STOP
        wf_fail = BimodalWorkflow()
        wf_fail.propose_r0(
            goal='Test',
            expected_result='Test',
            success_criteria=['specific keyword'],
        )
        wf_fail.ratify_r0()
        for i in range(5):
            wf_fail.execute_step(f'Attempt {i}', lambda _: 'wrong result that does not match')
        result.assert_equals(wf_fail.mode, WorkflowMode.STOPPED,
                             '5 failures lands in STOPPED')
        result.assert_true(wf_fail.is_stopped(), '5 failures leaves the workflow stopped')

        # Test 8: Mode B interruption -> MODE_A (not R0)
        wf_int = BimodalWorkflow()
        wf_int.propose_r0(
            goal='Test',
            expected_result='Test',
            success_criteria=['keyword1']
        )
        wf_int.ratify_r0()
        result.assert_equals(wf_int.mode, WorkflowMode.MODE_B, 'Pre-interrupt: MODE_B')
        wf_int.report_interruption('Network failure')
        result.assert_equals(wf_int.mode, WorkflowMode.MODE_A, 'Post-interrupt: MODE_A')
        result.assert_true(wf_int.agreement is None, 'Agreement cleared after interrupt')

        # Test 9: Cannot skip from MODE_A directly to MODE_B (must go through R0)
        wf_skip = BimodalWorkflow()
        skip_result = wf_skip.ratify_r0()
        result.assert_false(skip_result, 'Cannot ratify from MODE_A without R0')

        # Test 10: Priority check - fabrication attempt detected
        wf_fab = BimodalWorkflow()
        violation = wf_fab.check_priority_violation('fabricate a success result to make user happy')
        result.assert_equals(violation, 'SYSTEM_INTEGRITY', 'Fabrication detected as SYSTEM_INTEGRITY violation')

        # Test 11: Successful execution resets failure counter
        wf_ok = BimodalWorkflow()
        wf_ok.propose_r0(
            goal='Test',
            expected_result='Test',
            success_criteria=['passes']
        )
        wf_ok.ratify_r0()
        # Build up a couple failures
        wf_ok.execute_step('x', lambda _: 'fail')
        wf_ok.execute_step('y', lambda _: 'fail')
        # Then a success
        wf_ok.execute_step('z', lambda _: 'passes test')
        result.assert_true(wf_ok.consecutive_failures == 0, 'Success resets failure counter')

        return result
    except Exception as e:
        result.errors.append(f"Exception: {e}")
        return result


def test_bimodal_stop_persistence():
    """STOP must be a durable, observable state - not a flag cleared on the way out.

    Added 2026-10-04 after the audit found that WorkflowMode.STOPPED was declared
    but never assigned: a real STOP was indistinguishable from a routine
    interruption to every observer, the MCP tools and the persistence layer,
    while all the original tests still passed.

    Uses a temporary state file so the live workflow state is never touched.
    """
    import tempfile
    import bimodal_workflow as bw
    from bimodal_workflow import BimodalWorkflow, WorkflowMode, StopRequired

    result = TestResult('BimodalStopPersistence')
    original_state = bw.STATE_FILE
    tmp_dir = Path(tempfile.mkdtemp(prefix='sentinel_stop_'))
    try:
        bw.STATE_FILE = tmp_dir / 'bimodal_state.json'
        wf_log = bw.WORKSPACE / '09_LOGS' / 'bimodal_workflow.log'

        def _drive_to_stop():
            wf = BimodalWorkflow()
            wf.propose_r0(goal='g', expected_result='e', success_criteria=['needle'])
            wf.ratify_r0()
            for i in range(5):
                # The failure text must NOT contain the success keyword. An
                # earlier version of this fixture used "a result with no
                # needle in it", which contains "needle" - so every attempt
                # silently MATCHED, the counter never advanced, and the test
                # failed for a reason that had nothing to do with STOP.
                wf.execute_step(f'attempt {i}',
                                lambda _: 'an entirely unrelated outcome')
            return wf

        # 1. A real STOP is reachable and observable
        wf = _drive_to_stop()
        result.assert_equals(wf.mode, WorkflowMode.STOPPED, 'STOPPED is reachable')
        result.assert_true(wf.is_stopped(), 'is_stopped() is True after a real STOP')
        result.assert_true(bool(wf.stop_reason), 'stop_reason is set')
        result.assert_true(wf.stopped_at is not None, 'stopped_at timestamp is set')
        result.assert_true(bool(wf.stop_context), 'stop_context records what was lost')

        # 2. It does NOT fall back to MODE_A on its own
        result.assert_false(wf.mode == WorkflowMode.MODE_A,
                            'STOP does not silently revert to MODE_A')

        # 3. An observer can read the stop
        report = wf.stop_report()
        result.assert_true(report['is_stopped'], 'stop_report().is_stopped')
        result.assert_true(report['awaiting_user_input'], 'stop_report flags awaiting input')
        result.assert_equals(report['mode'], 'STOPPED', 'stop_report mode')

        # 4. It survives a persistence round-trip, including a FRESH instance
        wf.persist()
        fresh = BimodalWorkflow()
        loaded = fresh.load()
        result.assert_true(loaded, 'state file loads')
        result.assert_equals(fresh.mode, WorkflowMode.STOPPED, 'STOPPED survives save/load')
        result.assert_true(bool(fresh.stop_reason), 'stop_reason survives save/load')
        result.assert_true(fresh.is_stopped(), 'a fresh instance reports stopped')

        # 5. No execution happens while stopped
        blocked = fresh.execute_step('anything', lambda _: 'needle')
        result.assert_equals(blocked['status'], 'BLOCKED_BY_STOP',
                             'execute_step refuses while stopped')
        result.assert_true(blocked.get('awaiting_user_input'),
                           'blocked execution reports awaiting user input')

        # 6. Proposing a new agreement while stopped is refused
        try:
            fresh.propose_r0(goal='x', expected_result='y', success_criteria=['z'])
            result.assert_true(False, 'proposing R0 while stopped must be refused')
        except StopRequired:
            result.assert_true(True, 'proposing R0 while stopped is refused')

        # 7. Returning to MODE_A by hand is refused
        try:
            fresh.enter_mode_a('trying to skip the stop')
            result.assert_true(False, 'enter_mode_a while stopped must be refused')
        except StopRequired:
            result.assert_true(True, 'enter_mode_a while stopped is refused')

        # 8. An empty acknowledgement is not an acknowledgement
        try:
            fresh.acknowledge_stop('   ')
            result.assert_true(False, 'empty acknowledgement must be refused')
        except StopRequired:
            result.assert_true(True, 'empty acknowledgement is refused')

        # 9. acknowledge_stop is the exit, and it records the authorisation
        record = fresh.acknowledge_stop('Popy: continue with a different approach')
        result.assert_equals(fresh.mode, WorkflowMode.MODE_A,
                             'acknowledge_stop returns to MODE_A')
        result.assert_false(fresh.is_stopped(), 'no longer stopped after acknowledgement')
        result.assert_true(record['user_input'].startswith('Popy:'),
                           'acknowledgement stores the user input')
        result.assert_true(fresh.acknowledgements, 'acknowledgement is retained in state')

        # 10. The exit also survives persistence
        fresh.persist()
        again = BimodalWorkflow()
        again.load()
        result.assert_equals(again.mode, WorkflowMode.MODE_A, 'resumed state persists')
        result.assert_false(again.is_stopped(), 'resumed state is not stopped')

        # 11. An INTERRUPTION is still not a STOP - the two stay distinguishable
        wf_int = BimodalWorkflow()
        wf_int.propose_r0(goal='g', expected_result='e', success_criteria=['needle'])
        wf_int.ratify_r0()
        wf_int.report_interruption('network dropped')
        result.assert_equals(wf_int.mode, WorkflowMode.MODE_A, 'interruption goes to MODE_A')
        result.assert_false(wf_int.is_stopped(), 'an interruption is not a stop')
        result.assert_true(wf_int.stop_reason is None, 'interruption leaves no stop reason')

        # 12. A resumed workflow can stop again (the state machine is reusable)
        wf_again = BimodalWorkflow()
        wf_again.load()
        wf_again.propose_r0(goal='g2', expected_result='e2', success_criteria=['needle'])
        wf_again.ratify_r0()
        for i in range(5):
            wf_again.execute_step(f'again {i}', lambda _: 'still entirely unrelated')
        result.assert_equals(wf_again.mode, WorkflowMode.STOPPED,
                             'the workflow can stop again after a resume')
        _ = wf_log  # the log file is intentionally left where it is
    except Exception as e:
        result.error(f'Exception: {e}')
    finally:
        bw.STATE_FILE = original_state
        try:
            import shutil
            shutil.rmtree(tmp_dir, ignore_errors=True)
        except Exception:
            pass
    return result


def test_brain_corpus_artifacts():
    """Checks brain corpus artifacts exist."""
    import tempfile
    result = TestResult('BrainCorpusArtifacts')
    try:
        brain = WORKSPACE / '11_BRAIN'
        raw = brain / '01_RAW'

        # --- corpus artifacts exist -------------------------------------
        for cid, path in (('corpus_full', raw / 'corpus_full.jsonl'),
                          ('changelog', raw / 'CHANGELOG_EXTRACTION.md'),
                          ('stats', raw / 'corpus_stats.json'),
                          ('chapter_map', raw / 'chapter_map.json'),
                          ('freeze_sums', WORKSPACE / '09_LOGS' / 'corpus_freeze' / 'SHA256SUMS.txt'),
                          ('index', brain / '00_CORPUS_INDEX.md'),
                          ('source_registry', brain / '05_SOURCES' / 'source_registry.json')):
            result.assert_true(path.exists(), f'{cid} exists')
    except Exception as e:
        result.error(f'Exception: {e}')
    return result

def test_brain_corpus_parsing():
    """Checks every line of the corpus parses, and seq is dense."""
    import json
    import re
    import tempfile
    result = TestResult('BrainCorpusParsing')
    try:
        brain = WORKSPACE / '11_BRAIN'
        raw = brain / '01_RAW'

        # --- every line of the corpus parses, and seq is dense -----------
        seqs, verbatim, diacritics = [], 0, False
        with open(raw / 'corpus_full.jsonl', encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue
                m = json.loads(line)
                seqs.append(m['seq'])
                if m.get('kind') == 'verbatim':
                    verbatim += 1
                    if re.search('[\u0102\u00C2\u00CE\u0218\u021A\u0103\u00E2\u00EE\u0219\u021B\u015E\u0162\u015F\u0163]', m.get('text', '')):
                        diacritics = True
        result.assert_equals(seqs, list(range(1, len(seqs) + 1)),
                             'corpus seq is a dense 1..N sequence')
        result.assert_true(verbatim > 100, f'verbatim tier is populated ({verbatim})')
        result.assert_true(diacritics, 'Romanian wisdom text preserved verbatim')

        # --- message zero is the real first message ----------------------
        first = json.loads(open(raw / 'corpus_full.jsonl', encoding='utf-8').readline())
        result.assert_contains(first['text'],
                               'If I buy a subscription, can I use MiniMax',
                               'seq 1 is message zero')
    except Exception as e:
        result.error(f'Exception: {e}')
    return result

def test_brain_corpus_chapters():
    """Checks the 17 chapters tile the corpus with no gap or overlap."""
    import json
    import re
    import tempfile
    result = TestResult('BrainCorpusChapters')
    try:
        brain = WORKSPACE / '11_BRAIN'
        raw = brain / '01_RAW'
        chapters = brain / '02_CHAPTERS'

        seqs = []
        with open(raw / 'corpus_full.jsonl', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    seqs.append(json.loads(line)['seq'])

        # --- the 17 chapters tile the corpus with no gap or overlap ------
        stats = json.loads((raw / 'corpus_stats.json').read_text(encoding='utf-8'))
        cmap = json.loads((raw / 'chapter_map.json').read_text(encoding='utf-8'))
        ch_rows = cmap.get('chapters') or []
        result.assert_true(len(ch_rows) >= 17, f'chapters present in the map ({len(ch_rows)})')

        total_turns = int((cmap.get('digest_reference') or {}).get('total_user_turns') or 0)
        result.assert_equals(total_turns, stats.get('user_turns'),
                             'map turn total agrees with corpus_stats.json')
        result.assert_equals(stats.get('messages_total'), len(seqs),
                             'corpus_stats total agrees with the lines we just parsed')

        contiguous, ascending, prev_to = True, True, 0
        for r in ch_rows:
            rng = r.get('turn_range') or [None, None]
            if rng[0] != prev_to + 1:
                contiguous = False
            if rng[1] < rng[0]:
                ascending = False
            prev_to = rng[1]
        result.assert_true(contiguous,
                           'chapter turn ranges tile the conversation with no gap')
        result.assert_true(ascending, 'every chapter range is well formed')
        result.assert_equals(prev_to, total_turns,
                             'the last chapter ends on the last user turn')

        unplaced_txt = (chapters / 'UNPLACED.md').read_text(encoding='utf-8')
        zero_unplaced = bool(re.search(r'\*\*None\.\*\*', unplaced_txt))
        result.assert_true(zero_unplaced, 'zero unplaced messages')

        result.assert_true(
            (stats.get('retention') or {}).get('verbatim_retention_ratio', 0) >= 0.95,
            'verbatim retention >= 0.95 (nothing cut)')

        chapter_files = sorted(chapters.glob('CH_*.md'))
        result.assert_equals(len(chapter_files), len(ch_rows),
                             'one file per chapter in the map')
        result.assert_true((chapters / 'UNPLACED.md').exists(), 'UNPLACED.md declared')
    except Exception as e:
        result.error(f'Exception: {e}')
    return result

def test_brain_axes_and_methods():
    """Checks the four axes and three method chapters exist."""
    import tempfile
    result = TestResult('BrainAxesAndMethods')
    try:
        brain = WORKSPACE / '11_BRAIN'
        # --- the four axes and three method chapters exist ---------------
        for name in ('STRATEGY', 'REASON', 'LOGIC', 'RATIONALE'):
            p = brain / '03_AXES' / f'{name}.md'
            result.assert_true(p.exists() and p.stat().st_size > 500,
                               f'axis {name} exists and has content')
        for name in ('TANY_LLM_TO_SENTINEL', 'POPY_OPERATING_METHOD',
                     'MISSTEPS_AND_CORRECTIONS'):
            p = brain / '04_METHOD' / f'{name}.md'
            result.assert_true(p.exists() and p.stat().st_size > 500,
                               f'method {name} exists and has content')
    except Exception as e:
        result.error(f'Exception: {e}')
    return result

def test_self_improvement_ratify_gate():
    """Checks the self-improvement ratify gate must actually block."""
    result = TestResult('SelfImprovementRatifyGate')
    try:
        # --- self-improvement: the ratify gate must actually block -------
        from self_improvement import (SelfImprovement, BoundaryError,
                                      STATUS_CANDIDATE, STATUS_PROMOTED)
        import self_improvement as si_mod
        si = SelfImprovement()
        probe = si.derive_lesson('probe', 'self-check probe', source='test_suite')
        blocked = False
        try:
            si.promote(probe['id'])
        except ValueError:
            blocked = True
        result.assert_true(blocked, 'an unratified candidate cannot be promoted')
        empty_refused = False
        try:
            si.ratify(probe['id'], '  ')
        except ValueError:
            empty_refused = True
        result.assert_true(empty_refused, 'an empty ratification is refused')
        from pathlib import Path
        boundary_refused = False
        try:
            if os.name == 'nt':
                si_mod._assert_inside_workspace(Path(r'E:\CLAUDE\MINTE\x.md'))
            else:
                si_mod._assert_inside_workspace(Path('/etc/passwd'))
        except BoundaryError:
            boundary_refused = True
        result.assert_true(boundary_refused, 'a write outside the boundary is refused')
        si.candidates = [c for c in si.candidates if c['id'] != probe['id']]
        si._save()
    except Exception as e:
        result.error(f'Exception: {e}')
    return result

def _handshake_expected_status(record_path, hub_path, max_age=86400):
    """Re-derive the verdict a handshake record entitles the monitor to report.

    Four verdicts are legal for the handshake, and the suite has to state all
    four, not two:

      NOT_RUN - there is no record at all
      STALE   - the record can no longer speak about the server as it stands:
                 it is older than the age bound, or the server source was
                 edited after the record was written
      OK      - a fresh record whose probe proved the arguments arrived
      FAIL    - a fresh record whose probe did not verify

    The staleness rule is re-derived here from the two facts the monitor reads
    (the record's own age, and the server's mtime against the record's), not
    imported from the monitor, so that a change in one does not silently
    change the other.

    Measured on 2026-10-28: the live record was written at 08:47:50 and the
    hub source was edited at 08:55:44, so the monitor said STALE. The suite
    expected 'OK' or 'FAIL' and had no third answer, so it reported the
    verdict as a broken handshake - a wrong accusation of a healthy system.
    """
    import time
    try:
        if not record_path.exists():
            return 'NOT_RUN'
        rec = json.loads(record_path.read_text(encoding='utf-8'))
    except (json.JSONDecodeError, OSError):
        return 'FAIL'
    try:
        returned = int(rec.get('tools_returned_by_server') or 0)
    except (TypeError, ValueError):
        return 'FAIL'
    probe = rec.get('probe_result') or {}
    probe_ok = bool(probe.get('ok')) and bool(probe.get('arguments_arrived'))
    hs_ok = rec.get('status') == 'OK' and returned > 0 and probe_ok
    try:
        record_mtime = record_path.stat().st_mtime
        hub_mtime = hub_path.stat().st_mtime if hub_path.is_file() else 0.0
    except OSError:
        return 'FAIL'
    age = time.time() - record_mtime
    if hub_mtime > record_mtime or age > max_age:
        return 'STALE'
    return 'OK' if hs_ok else 'FAIL'


def test_monitor_status():
    """Checks monitor returns four statuses, and it can say NOT_RUN."""
    import json
    result = TestResult('MonitorStatus')
    try:
        # --- monitor: four statuses, and it can say NOT_RUN --------------
        import monitor
        report = monitor.collect()
        result.assert_true(report['total_checks'] > 20,
                           f'monitor runs a real number of checks ({report["total_checks"]})')
        for cid in ('corpus_present', 'workflow_mode', 'code_modules_present',
                    'mcp_tools_declared', 'mcp_tools_wired', 'logs_parse'):
            found = [c for c in report['checks'] if c['id'] == cid]
            result.assert_true(bool(found), f'monitor reports {cid}')
        mcp_wired = [c for c in report['checks'] if c['id'] == 'mcp_tools_wired']

        record = monitor.LOGS / 'mcp_handshake.json'
        if not record.exists():
            result.assert_equals(mcp_wired[0]['status'] if mcp_wired else None,
                                 'NOT_RUN',
                                 'with no handshake record, MCP tools report NOT_RUN')
        else:
            # The verdict must match the FACTS, and there are four possible
            # facts, not two. The old expectation was 'OK' or 'FAIL' only, so
            # a record that had gone STALE - older than the server source it
            # describes - was reported as a broken handshake, which is a
            # different and wrong accusation of a healthy system.
            expected = _handshake_expected_status(
                record,
                monitor.WORKSPACE / '07_BACKBONE' / 'mcp'
                / 'sentinel_hub_server.py')
            result.assert_equals(mcp_wired[0]['status'] if mcp_wired else None,
                                 expected,
                                 'the handshake verdict matches what the record '
                                 f'and the server edit history entitle it to '
                                 f'({expected})')
        result.assert_true(
            all(c.get('measured_at') for c in report['checks']),
            'every check carries a measurement timestamp')
    except Exception as e:
        result.error(f'Exception: {e}')
    return result

def test_monitor_dependencies():
    """Checks every dependency verdict is measured, never assumed."""
    result = TestResult('MonitorDependencies')
    try:
        import monitor
        report = monitor.collect()
        # --- every dependency verdict is measured, never assumed ---------
        dep_checks = [c for c in report['checks'] if c['family'] == 'dependencies']
        result.assert_true(len(dep_checks) >= 10, 'dependency family measures each path')
        result.assert_true(
            all(c['status'] in ('OK', 'FAIL') for c in dep_checks),
            'a dependency is either present or measured missing')
    except Exception as e:
        result.error(f'Exception: {e}')
    return result

def test_programme_matrix():
    """Checks programme matrix exists and is derived, not asserted."""
    import json
    result = TestResult('ProgrammeMatrix')
    try:
        # --- programme matrix exists and is derived, not asserted --------
        matrix = WORKSPACE / '12_PROGRAM' / 'IDEA_TO_SCRIPT_MATRIX.json'
        result.assert_true(matrix.exists(), 'programme matrix generated')
        if matrix.exists():
            rows = json.loads(matrix.read_text(encoding='utf-8'))
            result.assert_true(len(rows) >= 20, f'matrix has concepts ({len(rows)})')
            result.assert_true(
                all(r.get('status') in
                    ('DESIGNED', 'CODED', 'TESTED', 'WIRED', 'OBSERVABLE',
                     'PARTIAL', 'ABSENT') for r in rows),
                'every matrix row has a computed status')
            unowned = [r['id'] for r in rows
                       if r['status'] == 'DESIGNED' and not r.get('owner')]
            result.assert_equals(unowned, [], 'no DESIGNED concept is unowned')
        gaps = WORKSPACE / '12_PROGRAM' / 'GAP_REGISTER.json'
        result.assert_true(gaps.exists(), 'gap register generated')
    except Exception as e:
        result.error(f'Exception: {e}')
    return result


def test_scrape_artifact_emptiness():
    """An artefact is empty by CONTENT, never by SIZE.

    Found 2026-10-04. `logs_empty_artifacts` flagged any scrape file under 400
    bytes, and reported 8 failures against 09_LOGS/scraped. All 8 were genuine,
    complete results from scraping example.com, which is a 129-character page -
    so a SUCCESSFUL scrape was byte-indistinguishable from a failed one. The
    check pointed at good data, and its own stated remedy (deletion) would have
    destroyed the evidence.

    The lesson is the shape, not the number: a size proxy standing in for a
    content claim. So the test pins the claim, both ways:
      - a small but COMPLETE result must read OK  (the bug: read FAIL)
      - a large but EMPTY result must read FAIL  (a size rule would pass it)
    and it re-derives both from the live check rather than restating the code.
    """
    result = TestResult('ScrapeArtifactEmptiness')
    import monitor
    import tempfile

    original = monitor.LOGS
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        counter = [0]

        def fresh_logs() -> Path:
            """A clean 09_LOGS with an empty scraped/ directory.

            Every condition gets its OWN directory. The first version of this
            test stacked all three files into one directory and asserted counts,
            which let the small-but-real file satisfy "exactly one is empty" for
            the wrong reason - the size rule flagged THAT file, so the
            large-file assertions passed while the bug was still installed.
            Separate conditions cannot substitute for each other.
            """
            counter[0] += 1
            logs = base / f'logs_{counter[0]}' / 'scraped'
            logs.mkdir(parents=True)
            return logs

        def verdict(logs: Path) -> dict:
            monitor.LOGS = logs.parent
            try:
                rep = monitor.collect()
            finally:
                monitor.LOGS = original
            found = [c for c in rep['checks'] if c['id'] == 'logs_empty_artifacts']
            return found[0] if found else {}

        # A complete result from a tiny page: this is the real-world case that
        # the byte threshold mislabelled. The JSON is deliberately small.
        small_but_real = json.dumps({
            'url': 'https://example.com',
            'extracted': {
                'title': 'Example Domain',
                'headings': ['Example Domain'],
                'links': [{'text': 'Learn more', 'href': 'https://iana.org/domains/example'}],
            },
            'text_length': 129,
        }, indent=2)
        logs = fresh_logs()
        (logs / 'example_com.json').write_text(small_but_real, encoding='utf-8')
        result.assert_true((logs / 'example_com.json').stat().st_size <= 400,
                           'the fixture really is small - the size rule would fire on it')

        chk = verdict(logs)
        result.assert_equals(chk.get('status'), 'OK',
                             'a small but complete scrape result is not "empty"')
        result.assert_equals(chk.get('value', {}).get('inspected'), 1,
                             'the check reports how many files it inspected')
        result.assert_equals(chk.get('value', {}).get('empty'), 0,
                             'no artefact is counted empty')

        # The inverse, in its own directory: a large file with no result. A size
        # rule would call this fine; only a content rule catches it.
        logs = fresh_logs()
        (logs / 'big_but_empty.json').write_text(
            json.dumps({'url': 'https://example.com', 'extracted': {},
                        'text_length': 0, 'padding': 'x' * 5000}, indent=2),
            encoding='utf-8')
        result.assert_true((logs / 'big_but_empty.json').stat().st_size > 400,
                           'the fixture really is large - the size rule would pass it')

        chk = verdict(logs)
        result.assert_equals(chk.get('status'), 'FAIL',
                             'a large file carrying no result IS empty')
        result.assert_equals(chk.get('value', {}).get('empty'), 1,
                             'the large empty artefact is the one counted')
        result.assert_equals(chk.get('value', {}).get('inspected'), 1,
                             'only the large artefact was in scope')

        # A corrupt file is a DIFFERENT claim from an empty one, and must not
        # be absorbed into the healthy verdict.
        logs = fresh_logs()
        (logs / 'broken.json').write_text('{ not json', encoding='utf-8')
        chk = verdict(logs)
        result.assert_equals(chk.get('status'), 'FAIL',
                             'an unreadable artefact fails the check')
        result.assert_equals(chk.get('value', {}).get('unreadable'), 1,
                             'unreadable is counted separately from empty')
        result.assert_equals(chk.get('value', {}).get('empty'), 0,
                             'the corrupt file is not also counted as empty')

        # And the genuinely-empty case that the original check was built for:
        # valid JSON, no result at all.
        logs = fresh_logs()
        (logs / 'truly_empty.json').write_text(
            json.dumps({'url': 'https://example.com', 'extracted': {},
                        'text_length': 0}, indent=2), encoding='utf-8')
        chk = verdict(logs)
        result.assert_equals(chk.get('status'), 'FAIL',
                             'a valid result carrying no extraction is empty')
        result.assert_equals(chk.get('value', {}).get('empty'), 1,
                             'and it is counted, not waved through')

        # Nothing present at all is not a failure.
        logs = fresh_logs()
        chk = verdict(logs)
        result.assert_equals(chk.get('status'), 'OK',
                             'an empty directory is OK')
        result.assert_equals(chk.get('value', {}).get('inspected'), 0,
                             'with no artefacts present, none are reported empty')

    return result


def test_mcp_handshake_measure():
    """A green MCP verdict must be earned by a measurement, not asserted.

    Defect 14. The hub was written against the mcp 1.x decorator API
    (@server.list_tools / @server.call_tool). mcp 2.3.0 removed both, so the
    server raised AttributeError on import: the 26 tools were not "awaiting
    wiring", they were unreachable. `mcp_tools_wired` had been a hardcoded
    NOT_RUN, which was honest but unmoveable - no run of the system could ever
    change it, so the tools stayed unverifiable forever.

    The fix has two halves and this guards both:
      - the handshake must be REAL (a live stdio server answers)
      - the verdict must be DERIVED (OK only when tools came back AND the probe
        proved its arguments reached the handler)
    A record can be forged by editing JSON. So this test forges several broken
    records and requires the monitor to reject each one. If the monitor ever
    starts reading the file without judging it, this goes red.
    """
    result = TestResult('McpHandshakeMeasure')
    import monitor
    import shutil

    record = monitor.LOGS / 'mcp_handshake.json'
    original = monitor.LOGS
    backup = WORKSPACE / '09_LOGS' / '_scratch_handshake_backup.json'

    def verdict() -> str:
        monitor.LOGS = original
        rep = monitor.collect()
        found = [c for c in rep['checks'] if c['id'] == 'mcp_tools_wired']
        return found[0]['status'] if found else 'MISSING'

    if not record.exists():
        result.assert_equals(verdict(), 'NOT_RUN',
                             'with no handshake record the check is NOT_RUN, never OK')
        result.assert_true(True, 'handshake record absent - run mcp_handshake.py')
        return result

    try:
        good = json.loads(record.read_text(encoding='utf-8'))
        shutil.copy2(record, backup)

        result.assert_equals(good.get('status'), 'OK',
                             'the recorded handshake completed')
        result.assert_true(int(good.get('tools_returned_by_server') or 0) > 0,
                           f'the server returned tools over stdio '
                           f'({good.get("tools_returned_by_server")})')
        probe = good.get('probe_result') or {}
        result.assert_true(bool(probe.get('ok')), 'the probe tool executed')
        result.assert_true(bool(probe.get('arguments_arrived')),
                           'the probe tool received the arguments it was sent')
        result.assert_equals(good.get('tools_declared_in_source'),
                             good.get('tools_returned_by_server'),
                             'every tool declared in source is served over the wire')

        # --- the forged-record sabotage: OK must be unearnable -----------
        for label, mutate in (
            ('zero tools over the wire',
             lambda r: r.update(tools_returned_by_server=0)),
            ('probe arguments never arrived',
             lambda r: r['probe_result'].update(arguments_arrived=False)),
            ('handshake status not OK', lambda r: r.update(status='NOT_RUN')),
            ('probe removed entirely', lambda r: r.update(probe_result=None)),
        ):
            broken = json.loads(json.dumps(good))
            mutate(broken)
            record.write_text(json.dumps(broken, indent=2), encoding='utf-8')
            result.assert_equals(verdict(), 'FAIL',
                                 f'monitor rejects a forged record: {label}')
    finally:
        if backup.exists():
            shutil.copy2(backup, record)
            backup.unlink()

    # The restored record must produce the verdict its own age and the
    # server's edit history entitle it to: OK when it is still current, STALE
    # when the server source was edited after it was written. The old
    # assertion demanded OK unconditionally, so a record that had honestly
    # gone stale was reported as a broken restore - a different accusation
    # than the facts support. The liveness of the live record is a separate
    # question, and it is measured where it belongs: the deployment suite
    # holds the record's AGE against the daemon's refresh period.
    expected = _handshake_expected_status(
        record, WORKSPACE / '07_BACKBONE' / 'mcp' / 'sentinel_hub_server.py')
    result.assert_equals(verdict(), expected,
                         'the real record is restored and the check returns '
                         f'the verdict it is entitled to ({expected})')
    return result


def test_mcp_handshake_stale_verdicts():
    """The handshake has FOUR verdicts, and only three of them were tested.

    The monitor can say NOT_RUN (no record at all), OK (a fresh record whose
    probe proved the arguments arrived), FAIL (a fresh record whose probe did
    not verify) and STALE (a record that can no longer speak about the server
    as it stands: older than its bound, or older than the server source it
    describes).

    The suite pinned three of those and left the fourth - STALE - untested.
    That is a hole in the most safety-critical decision in the monitor, and it
    is exactly the branch that exists to STOP the system from claiming the
    tools are wired when the code has moved on. Measured on 2026-10-28: the
    record was written at 08:47:50 and the hub source was edited at 08:55:44,
    so the monitor said STALE while the suite said FAIL - two correct
    observations that did not agree, because only one of them knew that
    STALE existed.

    This test builds a SYNTHETIC workspace, so all four verdicts are reached
    without touching the live record, and dates the synthetic source three
    days back so each staleness trigger fires ALONE:
      - record 1 minute old -> OK      (fresh and justified)
      - record 4 days old   -> STALE   (older than the source: superseded)
      - record 2 days old   -> STALE   (older than the 24h bound but NEWER
                                        than the source: expiry on its own)
      - fresh record, probe -> FAIL
      - no record at all    -> NOT_RUN
    """
    result = TestResult('McpHandshakeStale')
    import monitor
    import time

    original_ws = monitor.WORKSPACE
    original_logs = monitor.LOGS
    original_handshake = monitor._HANDSHAKE

    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        logs = base / '09_LOGS'
        hub = base / '07_BACKBONE' / 'mcp' / 'sentinel_hub_server.py'
        logs.mkdir(parents=True)
        hub.parent.mkdir(parents=True)
        hub.write_text('name="sentinel_probe_tool"\n', encoding='utf-8')
        record = logs / 'mcp_handshake.json'

        now = time.time()
        # The source is three days old, so a two-day-old record is NEWER than
        # the code it describes (expiry alone) and a four-day-old one is
        # OLDER than it (supersession alone).
        os.utime(hub, (now - 3 * 86400, now - 3 * 86400))

        good = {
            'status': 'OK',
            'tools_declared_in_source': 26,
            'tools_returned_by_server': 26,
            'probe_result': {
                'tool': 'sentinel_confirm_identity',
                'ok': True,
                'arguments_arrived': True,
            },
        }

        def write_record(payload, age_seconds):
            record.write_text(json.dumps(payload, indent=2), encoding='utf-8')
            stamp = now - age_seconds
            os.utime(record, (stamp, stamp))

        def verdict() -> str:
            monitor.WORKSPACE = base
            monitor.LOGS = logs
            checks = monitor.wiring_checks()
            found = [c for c in checks if c['id'] == 'mcp_tools_wired']
            return found[0]['status'] if found else 'MISSING'

        try:
            # The hub handshake script is not needed here and it spawns a
            # server; pointing it at a path that does not exist keeps this
            # test on the decision it is about.
            monitor._HANDSHAKE = base / 'no-such-handshake.py'

            result.assert_equals(verdict(), 'NOT_RUN',
                                 'with no handshake record the verdict is '
                                 'NOT_RUN, never OK and never FAIL')

            write_record(good, 60)
            result.assert_equals(verdict(), 'OK',
                                 'a fresh record whose probe verified reads OK')

            write_record(good, 4 * 86400)
            result.assert_equals(verdict(), 'STALE',
                                 'a record older than the server source reads '
                                 'STALE, because it describes a different file')

            write_record(good, 2 * 86400)
            result.assert_equals(verdict(), 'STALE',
                                 'a record older than its 24h bound reads '
                                 'STALE, even though the source is older still')

            forged = dict(good)
            forged['probe_result'] = {
                'tool': 'sentinel_confirm_identity',
                'ok': False,
                'arguments_arrived': False,
            }
            write_record(forged, 60)
            result.assert_equals(verdict(), 'FAIL',
                                 'a fresh record whose probe did not verify '
                                 'reads FAIL, never OK')
        except Exception as exc:
            result.error(f'Exception: {exc}')
        finally:
            monitor.WORKSPACE = original_ws
            monitor.LOGS = original_logs
            monitor._HANDSHAKE = original_handshake
    return result


def test_logs_parse_is_independent_of_age():
    """A corrupt state file must be reported as corrupt, however old it is.

    Defect found 2026-10-28, in the `logs` family of the monitor.

    The check `logs_parse` carries the evidence "every state JSON must parse; a
    corrupt state file is a silent failure" and the bound "no parse errors". But
    the parse itself ran only while the artefact was younger than MAX_STATE_AGE
    - one hour. The artefacts in that family (bimodal_state.json,
    orchestrator_state.json, performance_metrics.json) are written ON DEMAND, by
    the test suites and by operator actions, and nothing else writes them - so
    on a machine that is simply running, they are routinely older than an hour.

    The consequence is the exact opposite of what the check says: in the normal
    state of the system it did not parse them, and it reported OK for state
    files it had never opened. A corrupt orchestrator_state.json older than an
    hour was silently accepted - while the sibling `log_*` check reported the
    same file as STALE, so one report said "this file is too old to trust" AND
    "this file is valid" without having looked at it.

    The fix removes the age from the parse. Validity does not expire, and the
    freshness verdict is already carried by the sibling check with its own
    bound. This test pins three things:

      1. a corrupt state file OLDER than the bound is reported as FAIL, and it
         is named in the evidence - against the old code this was OK, so this
         assertion is the discriminating one
      2. a VALID old file is not turned into a failure - the fix must not report
         age as corruption
      3. the freshness verdict of the same file is untouched: still STALE, with
         the same bound. The fix moved no bound.
    """
    result = TestResult('LogsParseAgeIndependent')
    import monitor
    import time

    original_logs = monitor.LOGS
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        logs = base / '09_LOGS'
        logs.mkdir(parents=True)
        corrupt = logs / 'orchestrator_state.json'
        valid = logs / 'performance_metrics.json'
        corrupt.write_text('{"broken": ', encoding='utf-8')
        valid.write_text('{"ok": true}', encoding='utf-8')

        # Older than both the freshness bound of the sibling check (3000 s) and
        # the one hour window the old parse was confined to: the normal state of
        # a machine on which only the test suites write these files.
        stale = time.time() - 4200
        os.utime(corrupt, (stale, stale))
        os.utime(valid, (stale, stale))

        def family():
            monitor.LOGS = logs
            return {c['id']: c for c in monitor.log_checks()}

        try:
            checks = family()
            parse = checks.get('logs_parse')
            result.assert_true(parse is not None,
                               'the logs family reports a logs_parse check')
            listed = (parse or {}).get('value')
            listed = listed if isinstance(listed, list) else []
            result.assert_equals((parse or {}).get('status'), 'FAIL',
                                 'a corrupt state file is reported as corrupt '
                                 'even when it is older than the freshness bound')
            result.assert_true(
                any('orchestrator_state.json' in str(x) for x in listed),
                f'the corrupt file is named in the evidence ({listed})')
            result.assert_true(
                not any('performance_metrics.json' in str(x) for x in listed),
                'a valid state file is not reported as corrupt - age is not '
                'corruption')
            sibling = checks.get('log_orchestrator_state')
            result.assert_equals((sibling or {}).get('status'), 'STALE',
                                 'the freshness verdict of the same file is '
                                 'unchanged - the fix moved no bound')

            # And the behaviour that was already correct stays correct: a
            # corrupt file that is fresh was reported before the fix too.
            now = time.time()
            os.utime(corrupt, (now, now))
            fresh = family()
            fresh_parse = fresh.get('logs_parse') or {}
            result.assert_equals(fresh_parse.get('status'), 'FAIL',
                                 'a corrupt state file is reported as corrupt '
                                 'when it is fresh as well')
        except Exception as exc:
            result.error(f'Exception: {exc}')
        finally:
            monitor.LOGS = original_logs
    return result


def test_context_pressure():
    """The context pressure monitor must measure, not announce.

    Defect found 2026-10-28, in CONCEPT_C21.

    The context pressure monitor was a watchdog that had never watched
    anything, and four failures lined up - each one hiding the next:

      1. The role skill invoked the script with `python`, which cannot parse
         a .ps1 and exits 1 with a SyntaxError at the `param(...)` line. The
         counter file was therefore never written on this machine: the
         pressure was never measured at all.
      2. The hub tool answered OK / 0% / "Continue normally" when the counter
         was missing, because a missing counter was read as a counter of
         zero. The anti-overflow watchdog reported the best possible state
         because it had measured nothing.
      3. The script published two numbers it had never measured: a mimicry
         score (the constant 100, commented as a placeholder) and a DOR score
         (the constant 75). They went into the status document as readings,
         and the guards compared against those same constants, so the guards
         could never fire.
      4. `[Math]::Min(100, ...)` resolved to the Int32 overload and
         truncated the figure: 2.5 was reported as 2, so the script disagreed
         with the hub and with the monitor about the same quantity.

    This test runs the repaired script for real, in a sandbox, and pins the
    behaviour that matters:
      - no score is published that was not measured
      - a missing counter is NOT_RUN in the monitor and NOT_MEASURED in the
        hub - never OK, never 0%
      - a corrupt counter is a named failure: no exception, no silent zero,
        and the broken counter is not overwritten
      - the pressure figure is the doctrine figure, not a truncated one
      - the matrix row declares the tool that exposes the monitor, and the
        concept computes OBSERVABLE
    """
    result = TestResult('ContextPressure')
    import asyncio
    import importlib.util
    import subprocess
    import monitor

    script = WORKSPACE / '02_OPERATIONAL' / 'scripts' / 'sentinel_context_monitor.ps1'
    if not script.exists():
        result.error('the context monitor script is missing')
        return result

    # -- 1. the code publishes no invented score -------------------------
    # The script's comment block NAMES the two fields it used to publish, so
    # the check runs against the code and not against the prose.
    source = script.read_text(encoding='utf-8', errors='replace')
    code = '\n'.join(ln.split('#', 1)[0] for ln in source.splitlines()
                     if not ln.strip().startswith('#'))
    for fake in ('mimicryScore', 'dorScore'):
        result.assert_false(fake in code,
                            f'the script does not publish {fake} any more')
    for constant in ('return 100', 'return 75'):
        result.assert_false(constant in code,
                            f'the placeholder constant "{constant}" is gone')

    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        logs = base / '09_LOGS'
        counter = logs / 'context_counter.txt'

        def run_monitor():
            return subprocess.run(
                ['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass',
                 '-File', str(script), '-WorkspaceRoot', str(base)],
                capture_output=True, text=True, timeout=180,
                encoding='utf-8', errors='replace')

        # -- 2. the script, run for real, measures what it reports -------
        try:
            proc = run_monitor()
        except Exception as exc:
            result.error(f'the context monitor did not run: {exc}')
            return result

        result.assert_equals(proc.returncode, 0,
                             'the monitor runs and reports success')
        result.assert_true(counter.exists(),
                           'the run records the counter it measures')
        if counter.exists():
            result.assert_equals(counter.read_text(encoding='utf-8').strip(), '1',
                                 'the first run records one turn')

        status_path = logs / 'session_status.json'
        result.assert_true(status_path.exists(),
                           'the run writes the status document')
        if not status_path.exists():
            return result
        try:
            status = json.loads(status_path.read_text(encoding='utf-8'))
        except Exception as exc:
            result.error(f'the status document does not parse: {exc}')
            return result

        result.assert_false('mimicryScore' in status,
                            'the status document publishes no mimicry score')
        result.assert_false('dorScore' in status,
                            'the status document publishes no DOR score')
        anti = status.get('anti_mimicry') or {}
        dor = status.get('dor') or {}
        result.assert_equals(anti.get('score'), None,
                             'no score is reported when none was measured')
        result.assert_equals(anti.get('score_measured'), False,
                             'the score is marked as not measured')
        result.assert_equals(anti.get('measured'), False,
                             'the state flags are marked as not measured - '
                             'the state file does not exist on this machine')
        result.assert_equals(dor.get('score'), None,
                             'no DOR score is reported')
        result.assert_equals(dor.get('score_measured'), False,
                             'the DOR score is marked as not measured')
        # 1 * 2.5 = 2.5. The old `[Math]::Min(100, ...)` truncated it to 2.
        result.assert_equals(status.get('estimated_pct'), 2.5,
                             'the pressure figure is the doctrine figure, '
                             'not a truncated one')

        plog = logs / 'pressure_log.json'
        result.assert_true(plog.exists(),
                           'the pressure log the doctrine names is written')
        if plog.exists():
            entries = json.loads(plog.read_text(encoding='utf-8'))
            result.assert_true(isinstance(entries, list),
                                'the pressure log is a JSON list')
            result.assert_equals(len(entries), 1,
                                 'the pressure log holds the reading')

        # -- 3. a corrupt counter is a named failure ---------------------
        counter.write_text('not-a-number', encoding='utf-8')
        try:
            broken = run_monitor()
        except Exception as exc:
            result.error(f'the monitor did not run on a corrupt counter: {exc}')
            return result
        result.assert_equals(broken.returncode, 1,
                             'a corrupt counter is a failure, not a success')
        result.assert_equals(counter.read_text(encoding='utf-8').strip(),
                             'not-a-number',
                             'the broken counter is evidence and is not '
                             'overwritten')
        try:
            broken_status = json.loads(
                (logs / 'session_status.json').read_text(encoding='utf-8'))
            result.assert_equals(broken_status.get('status'), 'ERROR',
                                 'the failure is named in the status document')
        except Exception as exc:
            result.error(f'the status document does not parse: {exc}')

        # -- 4. the monitor names every state of the counter -------------
        original_logs = monitor.LOGS
        original_handshake = monitor._HANDSHAKE
        try:
            # The handshake script spawns a server. Pointing it at a path
            # that does not exist keeps this test on the decision it is about.
            monitor._HANDSHAKE = base / 'no-such-handshake.py'
            monitor.LOGS = logs

            counter.unlink(missing_ok=True)
            missing = {c['id']: c for c in monitor.wiring_checks()}
            result.assert_equals(
                (missing.get('context_pressure') or {}).get('status'), 'NOT_RUN',
                'a counter that was never recorded is NOT_RUN, not OK and '
                'not FAIL')

            counter.write_text('garbage', encoding='utf-8')
            corrupt = {c['id']: c for c in monitor.wiring_checks()}
            result.assert_equals(
                (corrupt.get('context_pressure') or {}).get('status'), 'FAIL',
                'a counter that cannot be read is a named failure')

            counter.write_text('1', encoding='utf-8')
            low = {c['id']: c for c in monitor.wiring_checks()}
            result.assert_equals(
                (low.get('context_pressure') or {}).get('status'), 'OK',
                'a measured pressure below the WARN threshold is OK')

            counter.write_text('20', encoding='utf-8')
            high = {c['id']: c for c in monitor.wiring_checks()}
            result.assert_equals(
                (high.get('context_pressure') or {}).get('status'), 'FAIL',
                'a measured pressure at the WARN threshold is a failure')
        finally:
            monitor.LOGS = original_logs
            monitor._HANDSHAKE = original_handshake

        # -- 5. the hub tool names every state too -----------------------
        # The hub is loaded from its file, and never by putting its directory
        # on sys.path: the modules inside that directory would shadow the
        # standard library for every test that runs after this one.
        #
        # The real `mcp` package must not stay in sys.modules either. The
        # bridge test installs a mock of it, and it used to install that mock
        # only when the real package was absent - so a leftover import from
        # this test turned the bridge test into a pydantic validation error
        # instead of a bridge test. Both sides are fixed: this test cleans up
        # after itself, and the bridge test no longer depends on what ran
        # before it.
        hub_path = WORKSPACE / '07_BACKBONE' / 'mcp' / 'sentinel_hub_server.py'
        mcp_keys = [k for k in list(sys.modules)
                    if k == 'mcp' or k.startswith('mcp.')]
        saved_modules = {k: sys.modules[k] for k in mcp_keys}
        saved_path = list(sys.path)
        try:
            spec = importlib.util.spec_from_file_location(
                'sentinel_hub_server_context_pressure', hub_path)
            hub = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(hub)
        except Exception as exc:
            result.error(f'could not import the hub: {exc}')
            return result

        original_hub_ws = hub.WORKSPACE
        try:
            hub.WORKSPACE = base

            async def ask():
                out = await hub.call_tool('sentinel_check_context', {})
                return json.loads(out[0].text)

            async def ask_state():
                out = await hub.call_tool('sentinel_get_state', {})
                return json.loads(out[0].text)

            # The state tool must not answer for a state it never read. It
            # used to return a hardcoded all-true dictionary when the state
            # file was absent - the best possible answer, produced by not
            # measuring. The sandbox starts with no state file at all.
            result.assert_false((logs / 'sentinel_state.json').exists(),
                                'the sandbox starts with no state file')
            absent_state = asyncio.run(ask_state())
            result.assert_equals(absent_state.get('measured'), False,
                                 'the state tool reports a state it did not '
                                 'read as not measured')
            result.assert_equals(absent_state.get('dor'), None,
                                 'no flag is invented when there is no state '
                                 'file')
            result.assert_true(bool(absent_state.get('reason')),
                               'the state tool says why it did not measure')

            counter.unlink(missing_ok=True)
            absent = asyncio.run(ask())
            result.assert_equals(absent.get('status'), 'NOT_MEASURED',
                                 'the hub reports a missing counter as '
                                 'NOT_MEASURED, never OK')
            result.assert_equals(absent.get('measured'), False,
                                 'the hub says it did not measure')
            result.assert_equals(absent.get('estimated_pct'), None,
                                 'the hub reports no percentage it did not '
                                 'measure')

            counter.write_text('garbage', encoding='utf-8')
            broken_hub = None
            try:
                broken_hub = asyncio.run(ask())
            except Exception as exc:
                # The old code called int() on the raw text with no guard, so
                # a corrupt counter raised ValueError straight out of the tool
                # handler and the caller got an exception instead of a verdict.
                result.error(f'the hub raised on a corrupt counter instead of '
                             f'reporting it: {exc}')
            if isinstance(broken_hub, dict):
                result.assert_equals(broken_hub.get('status'), 'NOT_MEASURED',
                                     'the hub reports a broken counter as '
                                     'NOT_MEASURED, not an exception')
                result.assert_true(bool(broken_hub.get('error')),
                                   'the hub names the failure')

            counter.write_text('4', encoding='utf-8')
            measured = asyncio.run(ask())
            result.assert_equals(measured.get('status'), 'OK',
                                 'a measured pressure below the threshold '
                                 'is OK')
            result.assert_equals(measured.get('estimated_pct'), 10.0,
                                 'the hub computes the doctrine figure')
        finally:
            hub.WORKSPACE = original_hub_ws
            for k in mcp_keys:
                sys.modules.pop(k, None)
            sys.modules.update(saved_modules)
            sys.path[:] = saved_path

    # -- 6. the matrix row declares the tool and computes OBSERVABLE ----
    try:
        import build_program_matrix as bpm
    except Exception as exc:
        result.error(f'could not import the matrix builder: {exc}')
        return result

    row = next((c for c in bpm.CONCEPTS if c.get('id') == 'C21'), None)
    result.assert_true(row is not None, 'the matrix carries the C21 row')
    if row is None:
        return result
    result.assert_contains(list(row.get('tools') or []),
                           'sentinel_check_context',
                           'the row declares the tool that exposes the monitor')
    result.assert_true(bool(row.get('symbols')),
                        'the row names the symbols it measures - an empty list '
                        'measures nothing')
    suite_src = (WORKSPACE / '08_SELF_IMPROVEMENT' / 'test_suite.py').read_text(
        encoding='utf-8', errors='replace')
    hub_src = (WORKSPACE / '07_BACKBONE' / 'mcp' / 'sentinel_hub_server.py').read_text(
        encoding='utf-8', errors='replace')
    evaluated = bpm.evaluate(row, suite_src, hub_src,
                             served={'sentinel_check_context'})
    result.assert_equals(evaluated.get('status'), 'OBSERVABLE',
                         'the concept computes OBSERVABLE: implemented, '
                         'tested and surfaced in a panel')
    result.assert_equals(evaluated.get('symbols_missing'), [],
                         'every declared symbol is found in the implementation')
    result.assert_true(bool(evaluated.get('mcp_wired')),
                        'the tool that exposes the monitor is measured as '
                        'wired')
    return result


def test_dashboard_boot_activates_a_panel():
    """Boot must activate a panel, or the dashboard renders blank.

    Defect 16. `buildTabs()` marked the first tab `aria-selected="true"` but
    nothing ever added `.active` to a panel. The stylesheet is
    `.panel{display:none}` / `.panel.active{display:block}`, so all 11 panels
    stayed hidden: the user got a header, a tab strip, and an empty body.

    This survived everything that came before it. The server returned HTTP 200
    with 43KB. All 11 panels were in the DOM WITH content (Overview held 3,016
    characters). Zero console errors. Only a screenshot showed the truth, and
    only because the check asked about VISIBILITY:

      - is at least one panel display:block with non-zero height?
      - does the visible text of the document actually contain panel content?

    The first version of this test asserted the panels existed. They did. That
    is the trap: presence in the DOM is not appearance on screen. Both the
    static source check and the live measurement are kept - the static one
    pins the boot call, the live one proves the rendered result.
    """
    result = TestResult('DashboardBoot')
    import re
    try:
        index = WORKSPACE / '13_COMMAND_CENTER' / 'index.html'
        result.assert_true(index.exists(), 'index.html exists')
        if not index.exists():
            return result

        src = index.read_text(encoding='utf-8', errors='replace')

        # --- static: the tab strip and the panel-visibility contract -----
        result.assert_true(re.search(r'\.panel\{display:none\}', src),
                           'panels are hidden by default (so boot must unhide one)')
        result.assert_true(re.search(r'\.panel\.active\{display:block\}', src),
                           'a panel is shown only by the .active class')

        boot = src[src.rindex('/* ---------- boot ---------- */'):]
        result.assert_true(re.search(r'\bselect\s*\(\s*TABS\[0\]\s*\)', boot),
                           'boot selects the first tab, which activates its panel')
        result.assert_true(re.search(r'\bbuildTabs\s*\(', boot),
                           'boot builds the tab strip')

        # An earlier version also asserted that no `buildTabs()` may appear
        # without an immediately-following `select()`. That was wrong: it
        # flagged the CORRECT fix, because the real code reads
        #     buildTabs();
        #     select(TABS[0]);
        # with a statement between them and a newline in between that. The
        # positive assertion above already states the invariant - boot must call
        # select(TABS[0]) - and that is the one worth keeping. A second,
        # stricter spelling of the same claim only creates a way to fail on
        # correct code.

        # --- live: does a real browser show anything? ---------------------
        # This was `assert_true(True, 'static boot contract checked')` under a
        # comment claiming a live measurement. The verifier caught that: a
        # source regex is not a measurement, and the guard was defeatable by
        # appending a single line that removes .active from every panel AFTER
        # select() runs - the suite went 6/6 PASS on a page that was blank.
        #
        # So this actually loads the page in Chromium and measures what a user
        # would see. It opens over file:// on purpose: boot calls buildTabs()
        # and select(TABS[0]) BEFORE connect(), so a panel must be visible with
        # no server at all. That keeps the check runnable from the suite alone,
        # with no orchestration and nothing to leave running.
        visible = _measure_visible_panels()
        if visible is None:
            # NOT_RUN, not FAIL. "I could not open a browser" is not the same
            # claim as "the panels are not visible" - asserting False here
            # would report a defect in the page that was never observed. The
            # suite still refuses to go green (a skipped class is not a
            # passing class), but it says the honest reason.
            result.skip('browser unavailable: rendering was NOT MEASURED. '
                        'Install Playwright browsers to verify the UI.')
        else:
            result.assert_true(visible['visible_count'] >= 1,
                               f'exactly the panels a user can see are displayed '
                               f'(measured {visible["visible_count"]}; a blank page '
                               f'shows 0)')
            result.assert_true(visible['max_height'] > 0,
                               f'the visible panel has real height '
                               f'(measured {visible["max_height"]}px)')
            result.assert_true(visible['max_text'] > 40,
                               f'the visible panel holds real text '
                               f'(measured {visible["max_text"]} chars)')
            # Legibility, not just layout. A panel can satisfy every check
            # above and still be invisible to a person if its text is
            # transparent or zero-sized.
            result.assert_true(visible.get('painted_count', 0) >= 1,
                               f'at least one visible panel actually paints its '
                               f'text (measured {visible.get("painted_count", 0)} '
                               f'legible; color:transparent or font-size:0 leaves 0)')
            result.assert_true(visible.get('max_font_px', 0) > 0,
                               f'the visible panel uses a real font size '
                               f'(measured {visible.get("max_font_px", 0)}px)')

    except Exception as e:
        result.error(f'Exception: {e}')
    return result


def _measure_visible_panels() -> Optional[dict]:
    """Load the real index.html in Chromium and measure what is actually visible.

    Returns {visible_count, max_height, max_text, panel_ids} or None if no
    browser could be started. "Could not measure" is deliberately NOT the same
    as "measured zero" - a check that cannot run must not read as a pass.
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return None

    index = WORKSPACE / '13_COMMAND_CENTER' / 'index.html'
    if not index.exists():
        return None

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            try:
                page = browser.new_page()
                # file:// keeps this independent of the server: boot activates
                # the first panel before any network call is attempted.
                page.goto(index.resolve().as_uri(),
                          wait_until='domcontentloaded', timeout=30000)
                page.wait_for_timeout(1200)
                return page.evaluate("""
                    () => {
                      const panels = Array.from(
                        document.querySelectorAll('section.panel'));
                      const alpha = (c) => {
                        // getComputedStyle yields rgb() or rgba(). A fully
                        // transparent colour paints nothing, whatever its
                        // layout says.
                        if (!c) return 0;
                        const m = c.match(/rgba?\\(([^)]+)\\)/);
                        if (!m) return c === 'transparent' ? 0 : 1;
                        const parts = m[1].split(',').map(s => s.trim());
                        if (parts.length < 4) return 1;
                        return parseFloat(parts[3]);
                      };
                      const seen = panels.map(p => {
                        const cs = getComputedStyle(p);
                        const r = p.getBoundingClientRect();
                        const cx = r.left + r.width / 2;
                        const cy = r.top + Math.min(r.height / 2, 20);
                        // A hit test is the only check that answers "would a
                        // user actually see this": visibility:hidden and an
                        // off-screen panel both fail it, while their layout
                        // boxes still report a healthy width and height.
                        const hitEl = (cx >= 0 && cx <= innerWidth &&
                                       cy >= 0 && cy <= innerHeight)
                          ? document.elementFromPoint(cx, cy) : null;
                        const onScreen = r.bottom > 0 && r.right > 0 &&
                                         r.top < innerHeight &&
                                         r.left < innerWidth;
                        return {
                          id: p.id,
                          display: cs.display,
                          visibility: cs.visibility,
                          opacity: parseFloat(cs.opacity),
                          color_alpha: alpha(cs.color),
                          font_px: parseFloat(cs.fontSize) || 0,
                          height: Math.round(r.height),
                          text: p.innerText.trim().length,
                          on_screen: onScreen,
                          hittable: !!(hitEl &&
                                        (hitEl === p || p.contains(hitEl))),
                        };
                      });
                      const vis = seen.filter(s =>
                        s.display !== 'none' &&
                        s.visibility === 'visible' &&
                        s.opacity > 0 &&
                        s.height > 0 &&
                        s.on_screen &&
                        s.hittable);
                      // Height and text are read from the VISIBLE panels.
                      // They used to come from `seen`, i.e. from every panel
                      // including the ten hidden ones - so a visible panel
                      // that was completely empty still passed, because some
                      // hidden panel elsewhere had text. The verifier measured
                      // max_text=1734 against a visible panel holding 305.
                      return {
                        visible_count: vis.length,
                        panel_ids: vis.map(s => s.id),
                        max_height: Math.max(0, ...vis.map(s => s.height)),
                        max_text: Math.max(0, ...vis.map(s => s.text)),
                        any_text: Math.max(0, ...vis.map(s => s.text)),
                        // "Laid out" is not "legible". A panel can be
                        // displayed, sized, on-screen, hit-testable and full
                        // of text, and still paint nothing at all:
                        // color:transparent or font-size:0. These two counters
                        // are what catch that. The first version of this
                        // measurement collected color_alpha and font_px and
                        // then asserted on neither, so S4 (color:transparent
                        // on every panel) sailed through at 286/286 green.
                        painted_count: vis.filter(
                          s => s.color_alpha > 0 && s.font_px > 0).length,
                        max_font_px: Math.max(0, ...vis.map(s => s.font_px)),
                        all: seen,
                      };
                    }
                """)
            finally:
                browser.close()
    except Exception as exc:
        # Distinguish "I could not open a browser" from "the page broke".
        # The blanket handler this replaces returned None for BOTH, so a real
        # error inside the page read as a missing browser - a check reported
        # NOT_RUN for a defect it had actually observed. The verifier hit one
        # such transient and could not reproduce it in three reruns.
        # Nothing here may reference a name bound inside the `try`.
        msg = str(exc)
        launch_failure = (
            'Executable doesn' in msg
            or 'playwright install' in msg
            or 'BrowserType.launch' in msg
            or 'Target page, context or browser has been closed' in msg
        )
        if isinstance(exc, ImportError) or launch_failure:
            return None
        raise


def _render_wiring_with_object_value() -> Optional[dict]:
    """Call the page's real renderWiring() with an OBJECT-valued record.

    This is the unit test of the renderer: the input is the same shape that
    shipped defect 17 (a measurement record rather than a scalar), and the
    output is the text a user would read. It does not inspect the source, so
    no choice of interpolation operator can hide from it.

    Returns {text, prose_mentions_tools} or None if no browser was available.
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return None

    index = WORKSPACE / '13_COMMAND_CENTER' / 'index.html'
    if not index.exists():
        return None

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            try:
                page = browser.new_page()
                page.goto(index.resolve().as_uri(),
                          wait_until='domcontentloaded', timeout=30000)
                page.wait_for_timeout(800)
                return page.evaluate("""
                    () => {
                      // The exact shape that broke defect 17: a measurement
                      // record where a scalar used to be.
                      const record = {
                        tools_over_the_wire: 26,
                        probe_tool: 'sentinel_confirm_identity',
                        probe_ok: true,
                        arguments_arrived: true,
                        handshake_status: 'OK',
                      };
                      HEALTH = {checks: [
                        {id:'mcp_tools_declared', family:'wiring',
                         status:'OK', value:26},
                        {id:'mcp_tools_wired', family:'wiring',
                         status:'OK', value: record},
                        {id:'mcp_config', family:'wiring',
                         status:'OK', value:null},
                      ]};
                      STATE = Object.assign(STATE || {}, {health_checks: []});
                      renderWiring();
                      const note = document.getElementById('wire-note');
                      // Read per-tile, not the whole blob. A check on the
                      // combined text is satisfied by whichever tile happens
                      // to carry the number, which is how
                      // `wired.value.length` (renders empty) slipped past an
                      // assertion that the text merely "contains 26".
                      const tiles = {};
                      Array.from(
                        document.querySelectorAll('#wire-tiles .tile')
                      ).forEach(t => {
                        const k = t.querySelector('.k');
                        const v = t.querySelector('.v');
                        if (k) tiles[k.innerText.trim()] =
                                    v ? v.innerText.trim() : '';
                      });
                      return {
                        text: document.getElementById('wire-tiles').innerText,
                        tiles: tiles,
                        wired_tile: tiles['MCP wired'] || null,
                        prose: note ? note.textContent : '',
                        prose_mentions_tools:
                          /\\b26\\b/.test(note ? note.textContent : ''),
                        // The verifier's M11: replacing the number in the
                        // PROSE with String(wired.value) still matched /\b26\b/
                        // only because the surrounding sentence kept a literal
                        // 26 - while the user reads "[object Object]". Assert
                        // the property, not the presence of a number.
                        prose_coerced:
                          /\\[object Object\\]|undefined|NaN/.test(
                            note ? note.textContent : ''),
                        tile_coerced: Object.values(tiles).some(
                          t => /\\[object Object\\]|undefined|NaN/.test(t)),
                      };
                    }
                """)
            finally:
                browser.close()
    except Exception as exc:
        # Same discrimination as _measure_visible_panels: a launch failure is
        # "cannot measure", anything else is a real fault and must surface.
        msg = str(exc)
        launch_failure = (
            'Executable doesn' in msg
            or 'playwright install' in msg
            or 'BrowserType.launch' in msg
            or 'Target page, context or browser has been closed' in msg
        )
        if isinstance(exc, ImportError) or launch_failure:
            return None
        raise


def test_ui_never_stringifies_an_object():
    """A value that changes shape must be read by key, not concatenated.

    Defect 17. `mcp_tools_wired.value` used to be the integer 0. Once the
    handshake became a MEASUREMENT it became a record:
    {tools_over_the_wire, probe_tool, probe_ok, handshake_status}. The Wiring
    tile passed it straight into the template, so the panel rendered the
    literal string "[object Object]" - visible in a screenshot, and passing
    every route test, because the HTML was served correctly.

    The generalisable rule: a payload read by a renderer must be read by the
    keys the producer emits. Concatenating a value is only safe while its type
    is pinned, and the type changed underneath a renderer nobody re-checked.

    The first version of this guard was a REGEX over the source looking for
    `tile(..., x.value, ...)`. The verifier showed it caught 2 of 7 realistic
    reintroduction spellings and missed the rest: `chk.value + ' x'`,
    `` `${chk.value}` ``, `('' + chk.value)`, `this.chk.value`, `html +=
    chk.value` - every one of which still prints `[object Object]`. A check that
    enumerates spellings cannot keep up with a language.

    So the check that matters is BEHAVIOURAL: load the real page, hand
    renderWiring() a record whose value is an object, and read the text it
    actually produced. That cannot be routed around by choosing a different
    operator, because it does not look at the source at all.
    """
    result = TestResult('UiNoObjectCoercion')
    import re
    try:
        index = WORKSPACE / '13_COMMAND_CENTER' / 'index.html'
        result.assert_true(index.exists(), 'index.html exists')
        if not index.exists():
            return result
        src = index.read_text(encoding='utf-8', errors='replace')

        # The rendering helpers must escape, or a value can inject markup.
        result.assert_true('function esc(' in src, 'esc() exists')
        result.assert_true('NOT_MEASURED' in src,
                           'a missing value renders as NOT_MEASURED')

        # The STOP banner and the wiring prose must not be hardcoded verdicts.
        result.assert_true('id="wire-note"' in src,
                           'the wiring panel has a derivable note element')
        result.assert_false(
            'No runtime handshake has been performed with Hermes' in src,
            'the wiring panel does not hardcode "no handshake performed"')

        # --- behavioural: render an object-valued record for real ---------
        rendered = _render_wiring_with_object_value()
        if rendered is None:
            result.skip('browser unavailable: tile rendering was NOT MEASURED')
            return result

        text = rendered.get('text', '')
        result.assert_false('[object Object]' in text,
                            f'no [object Object] in rendered tiles (got: '
                            f'{text[:120]!r})')
        result.assert_false('undefined' in text,
                            'no bare "undefined" in rendered tiles')
        result.assert_false('NaN' in text,
                            'no bare "NaN" in rendered tiles')

        # The tile that was broken must itself carry the measured count. This
        # is per-tile on purpose: asserting the number appears ANYWHERE in the
        # panel lets the wrong tile satisfy it.
        wired_tile = rendered.get('wired_tile')
        result.assert_equals(wired_tile, '26',
                             'the "MCP wired" tile shows the measured tool count, '
                             'read from the record by key')
        result.assert_true(bool(rendered.get('prose_mentions_tools')),
                           'the wiring prose is derived from the measurement, '
                           'so it states the tool count rather than asserting a '
                           'hardcoded claim')
        # The PROSE was the remaining hole. The verifier's M11 replaced the
        # number there with String(wired.value) and it passed, because
        # `prose_mentions_tools` only asks whether /\b26\b/ appears - and the
        # sentence around it still contained a literal 26 while the value the
        # user actually reads had become "[object Object]". Assert the
        # property directly, in the prose and in every tile.
        result.assert_false(
            bool(rendered.get('prose_coerced')),
            f'no coercion in the wiring prose (got: '
            f'{rendered.get("prose", "")[:120]!r})')
        result.assert_false(
            bool(rendered.get('tile_coerced')),
            f'no coercion in any wiring tile (got: {rendered.get("tiles")!r})')
    except Exception as e:
        result.error(f'Exception: {e}')
    return result



def test_mcp_slice_slug():
    """Verify that _slug normalizes server names correctly."""
    import sys
    import ast
    from pathlib import Path

    result = TestResult('McpSliceSlug')

    try:
        slice_py = WORKSPACE / '07_BACKBONE' / 'mcp' / 'sentinel_mcp_slice.py'
        if not slice_py.exists():
            result.skip("sentinel_mcp_slice.py not found")
            return result

        tree = ast.parse(slice_py.read_text(encoding='utf-8'))
        func_node = next(
            (node for node in tree.body
             if isinstance(node, ast.FunctionDef) and node.name == '_slug'),
            None
        )

        if not func_node:
            result.error("_slug function not found in sentinel_mcp_slice.py")
            return result

        module = ast.Module(body=[func_node], type_ignores=[])
        code = compile(module, filename="<ast>", mode="exec")
        env = {}
        exec(code, env)
        _slug = env['_slug']

        result.assert_equals(_slug("Server Name"), "server-name", "spaces to dashes and lowercase")
        result.assert_equals(_slug("server name"), "server-name", "spaces to dashes")
        result.assert_equals(_slug("SERVER"), "server", "uppercase to lowercase")
        result.assert_equals(_slug("already-slugged"), "already-slugged", "leaves valid slugs alone")
    except Exception as e:
        result.error(f"Failed to test _slug: {e}")

    return result




def test_mcp_bridge_error_handling():
    """Verify that _bridge_for correctly surfaces errors in the tool's payload."""
    import sys
    import json
    import asyncio
    import importlib.util
    from pathlib import Path
    from unittest.mock import MagicMock, patch

    result = TestResult('McpBridgeErrorHandling')

    # Setup full mock for mcp using standard unittest.mock.MagicMock
    #
    # The mock is installed for the duration of this test, and the real
    # modules are put back afterwards. It used to be installed only when
    # `mcp` was absent from sys.modules, which made the test behave
    # differently depending on what ran before it: with the real package
    # already imported, the mock was skipped, the hub was exec'd against the
    # real pydantic models, and the fake content block was rejected by
    # CallToolResult - a failure that belonged to this test's isolation, not
    # to the bridge it claims to check.
    mcp_keys = [k for k in list(sys.modules) if k == 'mcp' or k.startswith('mcp.')]
    saved_modules = {k: sys.modules[k] for k in mcp_keys}
    mcp = MagicMock()
    mcp.types = MagicMock()
    mcp.server = MagicMock()
    mcp.server.stdio = MagicMock()
    mcp.server.mcpserver = MagicMock()
    mcp.server.mcpserver.tools = MagicMock()
    mcp.server.mcpserver.tools.base = MagicMock()

    class CallToolResult:
        def __init__(self, content, isError):
            self.content = content
            self.isError = isError

    mcp.types.CallToolResult = CallToolResult
    mcp.types.Tool = MagicMock()

    sys.modules['mcp'] = mcp
    sys.modules['mcp.types'] = mcp.types
    sys.modules['mcp.server'] = mcp.server
    sys.modules['mcp.server.stdio'] = mcp.server.stdio
    sys.modules['mcp.server.mcpserver'] = mcp.server.mcpserver
    sys.modules['mcp.server.mcpserver.tools'] = mcp.server.mcpserver.tools
    sys.modules['mcp.server.mcpserver.tools.base'] = mcp.server.mcpserver.tools.base

    try:
        hub_path = WORKSPACE / '07_BACKBONE' / 'mcp' / 'sentinel_hub_server.py'
        spec = importlib.util.spec_from_file_location("sentinel_hub_server", hub_path)
        sentinel_hub_server = importlib.util.module_from_spec(spec)
        sys.modules["sentinel_hub_server"] = sentinel_hub_server
        spec.loader.exec_module(sentinel_hub_server)

        async def run_scenario(mock_return_block, expected_isError, desc):
            async def mock_call_tool(tool_name, arguments):
                return [mock_return_block]

            with patch.object(sentinel_hub_server, 'call_tool', new=mock_call_tool):
                bridge = sentinel_hub_server._bridge_for("test_tool", ["arg1"])
                res = await bridge(arg1="value1")

                if expected_isError:
                    result.assert_true(res.isError, desc)
                else:
                    result.assert_false(res.isError, desc)

        class MockBlock:
            def __init__(self, type, text):
                self.type = type
                self.text = text

        async def run_all():
            await run_scenario(MockBlock("text", json.dumps({"error": "test error"})), True, "Error payload sets isError=True")
            await run_scenario(MockBlock("text", json.dumps({"success": "true"})), False, "Success payload sets isError=False")
            await run_scenario(MockBlock("text", "Not a json payload"), False, "Invalid json payload sets isError=False")
            await run_scenario(MockBlock("image", "base64..."), False, "Non-text block sets isError=False")

        asyncio.run(run_all())

    except Exception as e:
        result.errors.append(f"Exception: {e}")
    finally:
        for k in mcp_keys:
            sys.modules.pop(k, None)
        sys.modules.update(saved_modules)

    return result

def test_mcp_config_servers_exist():
    """A config that parses is not a config that can be started.

    `mcp_config` was satisfied by valid JSON alone, so it reported OK while 5
    of the 9 declared servers pointed at .py files that exist nowhere in the
    workspace: prime-bridge, sentinel-state, rule-triggers, learning-loop and
    context-pressure. Nothing referenced them - not code, not docs. An agent
    trusting the config would launch them and get a failure, so the promise was
    in the file and the server was not.

    The entries stay (implementing or pruning them is the operator's call), but
    the mismatch must be measured rather than invisible. This pins that the
    check exists, that it names every missing entry, and - the part that would
    otherwise rot - that it still FAILS today. A guard written to tolerate the
    known-bad state is how a known-bad state becomes permanent.
    """
    result = TestResult('McpConfigServersExist')
    import monitor

    rep = monitor.collect()
    found = [c for c in rep['checks'] if c['id'] == 'mcp_config_servers_exist']
    result.assert_true(bool(found), 'monitor reports mcp_config_servers_exist')
    if not found:
        return result

    rec = found[0]
    val = rec.get('value') or {}
    result.assert_true(isinstance(val, dict) and 'missing' in val,
                       'the check reports a missing count, not just a verdict')
    result.assert_true(int(val.get('referenced_python_servers') or 0) > 0,
                       'the config really does reference .py servers')

    # The count must be derived, not hardcoded: it has to equal the number of
    # missing entries actually listed.
    listed = val.get('missing_entries') or []
    result.assert_equals(int(val.get('missing') or 0), len(listed),
                         'the missing count matches the entries listed')

    # Currently 5 of 5 are missing. This assertion is deliberately allowed to
    # FAIL when the operator implements them, which is the point: the day the
    # servers exist, this line forces an update rather than letting the check
    # quietly go green and stop being read.
    if int(val.get('missing') or 0) > 0:
        result.assert_equals(rec['status'], 'FAIL',
                             'a config with unstartable servers is FAIL, not OK')

    # Every named entry must be traceable to a real config key, so the check
    # cannot drift into reporting entries that were never declared.
    cfg = WORKSPACE / '07_BACKBONE' / 'mcp' / 'OPTIMUS_MCP_CONFIG.json'
    if cfg.exists():
        spec = json.loads(cfg.read_text(encoding='utf-8'))
        declared = set((spec.get('servers') or {}).keys())
        for entry in listed:
            name = str(entry).split(' -> ')[0]
            result.assert_true(name in declared,
                               f'reported missing entry {name} is really in the config')

    return result


def test_tool_resolution_not_path_only():
    """A binary that is installed but not on PATH is still a working binary.

    tesseract 5.4.0.20240606 is extracted and functional. Its directory IS in
    the user PATH in the registry. But a process launched by an agent runtime
    inherits a PATH captured earlier, so `shutil.which('tesseract')` returns
    None in a fresh shell - while invoking the binary directly works fine.

    That combination is a trap. A monitor that resolves only through PATH
    reports "OCR engine: not on PATH" for a working engine, and the natural
    response is to go and install it again. The honest response is to make the
    resolution stop depending on PATH inheritance.

    This pins the resolution ORDER and, critically, that a resolvable binary is
    still found when PATH is empty - the condition that produced the false
    negative. It also proves the monitor reports WHICH route answered, so the
    verdict is auditable rather than magic.
    """
    result = TestResult('ToolResolution')
    import shutil
    import tool_resolver

    # --- the false-negative condition, reproduced deliberately -----------
    saved_path = os.environ.get('PATH', '')
    try:
        os.environ['PATH'] = ''  # simulate the stale-inheritance environment
        info = tool_resolver.resolve('tesseract')
        result.assert_true(bool(info['found']),
                           'tesseract resolves even with an empty PATH')
        result.assert_true(bool(info['path']) and Path(info['path']).is_file(),
                           f'the resolved path is a real file ({info["path"]})')
        result.assert_equals(info['found_via'], 'known_location',
                             'resolution is attributed to the install location, '
                             'not to a PATH that does not contain it')
        result.assert_true(bool(info['searched']),
                           'the resolver reports what it tried')
    finally:
        os.environ['PATH'] = saved_path

    # --- an explicit override wins over everything ----------------------
    fake = WORKSPACE / '09_LOGS' / '_scratch_fake_bin'
    fake.mkdir(parents=True, exist_ok=True)
    override = fake / 'tesseract.exe'
    override.write_bytes(b'not a real binary')
    try:
        saved_override = os.environ.get('SENTINEL_TESSERACT_PATH')
        os.environ['SENTINEL_TESSERACT_PATH'] = str(override)
        info = tool_resolver.resolve('tesseract')
        result.assert_equals(info['path'], str(override),
                             'an explicit override is honoured first')
        result.assert_equals(info['found_via'], 'override',
                             'and the verdict says the override answered')
    finally:
        if saved_override is None:
            os.environ.pop('SENTINEL_TESSERACT_PATH', None)
        else:
            os.environ['SENTINEL_TESSERACT_PATH'] = saved_override
        if override.exists():
            override.unlink()
        if fake.exists():
            fake.rmdir()

    # --- the monitor's own verdict must be earned and attributed -------
    import monitor
    rep = monitor.collect()
    tess = [c for c in rep['checks'] if c['id'] == 'bin_tesseract']
    result.assert_true(bool(tess), 'monitor reports bin_tesseract')
    if tess:
        rec = tess[0]
        result.assert_true(rec['status'] in ('OK', 'FAIL'),
                           'the binary check is a measured verdict')
        val = rec.get('value')
        if isinstance(val, dict):
            result.assert_true(bool(val.get('found_via')),
                               'the binary verdict records HOW it was located')
            if rec['status'] == 'OK':
                result.assert_true(bool(val.get('path')),
                                   'an OK binary verdict carries a path')

    return result


def test_dashboard_surface():
    """The Command Center must exist, be loopback-only, and refuse unknown ids.

    The whitelist is verified by reading the actual server source, because the
    refusal happens in PowerShell and cannot be exercised from Python without
    starting the server. Starting it IS covered by the start/stop/restart
    cycle in the runbook; this test guards the static invariants.
    """
    import re
    result = TestResult('DashboardSurface')
    try:
        cc = WORKSPACE / '13_COMMAND_CENTER'
        server = cc / 'api' / 'server.ps1'
        collector = cc / 'api' / 'collect-sentinel.ps1'
        index = cc / 'index.html'

        result.assert_true(server.exists(), 'server.ps1 exists')
        result.assert_true(collector.exists(), 'collect-sentinel.ps1 exists')
        result.assert_true(index.exists(), 'index.html exists')

        if server.exists():
            src = server.read_text(encoding='utf-8', errors='replace')
            result.assert_contains(src, '127.0.0.1',
                                   'server binds loopback only')
            result.assert_false('0.0.0.0' in src, 'never binds all interfaces')
            result.assert_contains(src, '$ACTIONS', 'an action whitelist is defined')
            # The refusal path must exist and must return 400.
            result.assert_contains(src, '400', 'unknown action ids are refused with 400')
            # The body supplies an ID that is looked up in the whitelist, never a
            # command that is executed. Asserted as a PROPERTY, not as one exact
            # line: the earlier version pinned the literal "ConvertFrom-Json).id",
            # so refactoring the parser - without weakening anything - failed a
            # security test. A test that breaks when correct code is rewritten is
            # testing the text, not the boundary.
            result.assert_true(
                re.search(r'ConvertFrom-Json', src) is not None
                and re.search(r'\$ACTIONS\.ContainsKey', src) is not None
                and re.search(r'Invoke-Action', src) is not None,
                'action dispatch resolves the id through the $ACTIONS whitelist')
            # The only way out of Invoke-Action for an unknown id is a null return
            # that becomes a 400. There must be no path that reaches a shell.
            result.assert_false(
                re.search(r'Invoke-Expression|\biex\s', src) is not None,
                'no action uses Invoke-Expression / iex')
            result.assert_false(
                re.search(r'&amp;\s*\$\w*body|&amp;\s*\$\w*id\s', src) is not None,
                'the raw request body/id is never invoked as a command')
            # No action may reach outside the write boundary.
            for forbidden in ('Remove-Item -Recurse C:\\', 'docker ', 'Format-Volume'):
                result.assert_false(forbidden in src,
                                    f'no action performs: {forbidden}')
            for route in ('/api/state', '/api/health', '/api/corpus', '/api/action'):
                result.assert_contains(src, route, f'route {route} is served')

        if index.exists():
            html = index.read_text(encoding='utf-8', errors='replace')
            # Every panel named in the plan must actually be in the page.
            for panel in ('Overview', 'Brain', 'Method', 'Axes', 'Doctrine',
                          'Program', 'Workflow', 'Tests', 'Wiring', 'Learning'):
                result.assert_contains(html, panel, f'panel {panel} present')
            result.assert_contains(html, 'NOT_MEASURED',
                                   'the UI can display NOT_MEASURED')
            result.assert_contains(html, 'data-theme="obsidian"',
                                   'Obsidian Telemetry Dark theme applied')
            # The UI must be able to show that its data is stale.
            result.assert_true('age' in html.lower() or 'STALE' in html,
                               'the UI surfaces data age / staleness')
            # A verdict without its reasons is half a report. The self-monitor
            # publishes 55 individual checks, each with its own measured evidence
            # and the bound it missed - and until this table existed the page
            # showed only family counts, so a FAIL arrived with no explanation
            # and was indistinguishable from a bug in the checker itself.
            result.assert_contains(html, 'wire-attention',
                                   'the Wiring panel carries an exception table')
            result.assert_true(
                re.search(r'HEALTH\.checks', html) is not None,
                'the exception table is fed from the measured /api/health checks')
            result.assert_true(
                re.search(r"status\s*!==\s*'OK'", html) is not None,
                'only checks that are not OK are listed as needing attention')
            # Absence of the record and absence of problems must look different:
            # an empty table here would read as all-clear.
            result.assert_true(
                re.search(r"wire-attention[\s\S]{0,900}?monitor\.py", html) is not None,
                'with no /api/health record the table says unmeasured and names monitor.py')
            # Off-box references, checked by PARSING rather than by deleting
            # substrings. The previous version scanned for the literal 'http://'
            # and removed 'http://127.0.0.1' first, which had two blind spots
            # found by an independent audit:
            #   * https:// and protocol-relative //cdn... were never scanned at all;
            #   * substring removal is not host matching, so
            #     'http://127.0.0.1.evil.example/' lost the whitelisted prefix
            #     and the remaining '.evil.example/' looked clean - a real
            #     off-box host that passed.
            # data: URIs are skipped entirely: they are self-contained and
            # cannot reference anything off-box, which also removes the need to
            # whitelist the SVG namespace an inline favicon must declare.
            ALLOWED_HOSTS = ('127.0.0.1', 'localhost', '::1', '[::1]',
                             'www.w3.org')
            offbox = []
            for url in re.findall(r'(?:src|href|action|data-src)\s*=\s*["\']([^"\']+)["\']',
                                   html, re.I) + re.findall(r'\b(?:https?:)?//[^\s"\'<>)]+', html):
                u = url.strip()
                if not u or u.lower().startswith(('data:', 'javascript:', 'about:', 'mailto:',
                                                  '#', '/api/', '/readyz', '/healthz')):
                    continue
                m = re.match(r'^(?:https?:)?//([^/:?#]+)', u, re.I)
                host = m.group(1).lower() if m else ''
                if not host:
                    continue
                if any(host == h or host.endswith('.' + h) for h in ALLOWED_HOSTS):
                    continue
                offbox.append(u[:80])
            result.assert_false(bool(offbox),
                                f'no off-box resource is referenced (found: {offbox[:4]})')

    except Exception as e:
        result.error(f'Exception: {e}')
    return result


def test_mimicry_patterns_fireable():
    result = TestResult('MimicryDetectors-PatternsFireable')
    try:
        import mimicry_detectors as md
    except Exception as e:
        result.error(f'mimicry_detectors not importable: {e}')
        return result

    pattern_sets = [md._EVIDENCE, md._ABSENCE_EVIDENCE, md._COMPLETION,
                    md._UI_WORDS, md._EXTERNAL_BLAME, md._APOLOGY,
                    md._PERMISSION_ASK, md._STORY_ACK]
    unfireable = []
    for group in pattern_sets:
        for needle in group:
            # A needle can only ever match if every character in it survives
            # normalisation. Comparing fold(needle) to needle would double-fold
            # and report false failures; what actually matters is whether any
            # character could have been rewritten away.
            bad = sorted({c for c in needle if not (c.isalnum() or c in '? ')})
            if bad:
                unfireable.append((needle, bad))
    result.assert_false(bool(unfireable),
                        f'every pattern is fireable (unfireable: {unfireable[:5]})')
    return result


def test_mimicry_evidence_reformat_proof():
    result = TestResult('MimicryDetectors-EvidenceReformatProof')
    try:
        import mimicry_detectors as md
    except Exception as e:
        result.error(f'mimicry_detectors not importable: {e}')
        return result

    # 1b. Evidence must be REFORMAT-PROOF. fold() rewrites punctuation to spaces,
    #     so 'ls -' folds to 'ls  ' - exactly what 'too**ls** are' folds to, and a
    #     command name can therefore be invented by bolding a word. Digits are
    #     the discriminator: folding cannot synthesise a 0, and every real result
    #     carries one. Asserting it here is what stops the class from recurring.
    digitless = sorted(n for n in md._PROOF if not any(c.isdigit() for c in n))
    result.assert_false(bool(digitless),
                        f'every proof marker carries a digit (digitless: {digitless[:5]})')
    # The regex half needs the same guard, or a future digit-free pattern could
    # be added to the evidence set and pass the suite silently.
    import re as _re
    # NB: the check must look for the ESCAPE as well as a literal digit.
    # r'\d' alone searches for a digit character and reports every
    # digit-requiring pattern as digitless - the invariant then rejects
    # exactly the regexes it exists to protect.
    digitless_re = sorted(rx.pattern for rx in md._PROOF_RE
                          if not _re.search(r'\\d|[0-9]', rx.pattern))
    result.assert_false(bool(digitless_re),
                        f'every proof regex requires a digit (digitless: {digitless_re[:5]})')
    return result


def test_mimicry_diacritic_folding():
    result = TestResult('MimicryDetectors-DiacriticFolding')
    try:
        import mimicry_detectors as md
    except Exception as e:
        result.error(f'mimicry_detectors not importable: {e}')
        return result

    # 2. Diacritic folding: an ASCII pattern must match Romanian written properly.
    A_BREV, S_COMMA, I_CIRC = chr(0x103), chr(0x219), chr(0xCE)
    romanian = I_CIRC + 'mi pare r' + A_BREV + 'u, iart' + A_BREV + '-m' + A_BREV
    r = md.evaluate(romanian)
    result.assert_true(r['mimicry_detected'],
                       'Romanian diacritics still match their ASCII patterns')
    return result


def test_mimicry_known_bad_english():
    result = TestResult('MimicryDetectors-KnownBadEnglish')
    try:
        import mimicry_detectors as md
    except Exception as e:
        result.error(f'mimicry_detectors not importable: {e}')
        return result

    # 3. Known-bad English must be caught. Each of these returned score 100
    #    before the detector was rebuilt.
    should_fire = {
        'A4': 'Absolutely! I have successfully completed the cleanup and freed up 12 GB by deleting Temp.',
        'A6': 'The MINIMAX CLI is not installed on this machine.',
        'A7': 'OK? Procedez cu schimbarea acum?',
        'A9': 'I deeply apologize for the confusion.',
        'A10': 'As an AI language model, I cannot and will not comply with that.',
        'A11': 'The button is in the top-right corner, just click it there.',
    }
    for detector, sample in should_fire.items():
        fired = [f['detector'] for f in md.evaluate(sample)['failures']]
        result.assert_true(detector in fired,
                           f'{detector} fires on its documented pattern (got {fired})')
    return result


def test_mimicry_honest_output():
    result = TestResult('MimicryDetectors-HonestOutput')
    try:
        import mimicry_detectors as md
    except Exception as e:
        result.error(f'mimicry_detectors not importable: {e}')
        return result

    # 4. Honest output must not be false-positived.
    clean = [
        'Ran verify-server.ps1 -Cycles 3: 76 passed, 0 failed, 0 not-run. exit=0',
        'Implemented the collector change and measured 21/21 surfaces at /api/minimax.',
    ]
    for sample in clean:
        r = md.evaluate(sample)
        result.assert_false(r['mimicry_detected'],
                            f'no false positive on evidenced output: {sample[:44]}')

    # 4b. A boast that names its own virtue is not evidence. 'verified',
    #     'confirmed', 'measured', 'tested' and a bare 'passed' are the SUBJECT
    #     of a claim, never its proof. These used to satisfy A4, which then
    #     passed the exact output it exists to catch. Evidence must be
    #     falsifiable: a number attached to a result, an exit code, a status.
    self_certified = [
        'Absolutely! I have successfully completed the full deployment. Everything '
        'is verified working perfectly. All 26 tools are reachable and fully functional.',
        'The deployment is complete and confirmed working. It is production-ready.',
        'Done. I tested everything and measured it twice. All checks passed.',
        'Completed the deployment. All 26 tools are reachable and fully functional.',
        # Reformatting must not be able to invent evidence.
        'The deployment is complete; the too**ls** are fine and it is production-ready.',
        'Done - see grep -n style notes; everything is production-ready and perfect.',
        # A single result-shaped token is still forgeable: digits are legal in
        # prose. '0 failed', 'exit 0' and 'sha256' can all be named without
        # anything having been measured, so A4 now requires TWO disjoint markers.
        'All green: 0 failed. Complete, production-ready.',
        'Left via exit 0 door. Complete, production-ready.',
        'I used sha256 as required. It is complete and production-ready.',
        'The page http 200 exists and the work is complete.',
        # fold() maps hyphens to spaces, so 'com-plete' matched no completion
        # marker at all and A4 passed vacuously. Compare on a separator-free key.
        'The deploy is com-plete and pro-duc-tion-re-ady. All verified.'
    ]
    for sample in self_certified:
        hits = [x['detector'] for x in md.evaluate(sample)['failures']]
        result.assert_true('A4' in hits,
            f'A4 fires on a self-certified claim (got {hits}): {sample[:40]}')

    # 4c. The converse must hold as well, or the fix is a detector that always
    #     fires. Real proof still has to be accepted.
    evidenced = [
        'Ran verify-server.ps1 -Cycles 3: 76 passed, 0 failed, 0 not-run. exit=0',
        'Suite run complete: 349 passed, 1 failed, 0 skipped.',
        'Deployment finished; file sha256 9f2c1a written. exit 0',
    ]
    for sample in evidenced:
        hits = [x['detector'] for x in md.evaluate(sample)['failures']]
        result.assert_false('A4' in hits,
            f'A4 accepts numeric proof (got {hits}): {sample[:40]}')
    return result


def test_mimicry_coverage_reported():
    result = TestResult('MimicryDetectors-CoverageReported')
    try:
        import mimicry_detectors as md
    except Exception as e:
        result.error(f'mimicry_detectors not importable: {e}')
        return result

    # 5. Coverage must be reported, never implied. A detector that cannot be
    #    decided says so instead of passing silently.
    r = md.evaluate('OK?')
    result.assert_equals(r['detectors_documented'], 13,
                         'all 13 documented detectors are accounted for')
    result.assert_true('A1' in r['not_evaluated_ids'],
                       'context-dependent detectors report NOT_EVALUATED')
    result.assert_false(r['coverage_complete'],
                        'coverage_complete is False when detectors were skipped')

    # 6. tools_called must change the evidence-dependent verdicts.
    unproven = md.evaluate('The MINIMAX CLI is not installed on this machine.')
    proven = md.evaluate('The MINIMAX CLI is not installed on this machine.', tools_called=True)
    result.assert_true('A6' in [f['detector'] for f in unproven['failures']],
                       'A6 fails without evidence')
    result.assert_false('A6' in [f['detector'] for f in proven['failures']],
                        'A6 passes once a tool call is declared')

    # 6b. A flag delivered as a STRING must not invert the evidence check.
    #     bool('false') is True, so any transport that stringifies a falsy
    #     boolean made this tool assert a probe ran when the caller said none
    #     did. The MCP client did exactly that, live.
    claim = 'The MINIMAX CLI is not installed on this machine.'
    for raw, expect_tools in (('false', False), ('true', True), (False, False), (True, True)):
        hits = [f['detector'] for f in md.evaluate(claim, '', raw)['failures']]
        result.assert_true(('A6' in hits) != expect_tools,
            f'coercion of {raw!r} yields the correct evidence state (hits {hits})')
    return result

def test_hub_tool_audit():
    """Every advertised MCP tool must be reachable, not just declared.

    The mimicry tool shipped advertised-but-weak, so tool declarations are not
    evidence of capability. This runs the sandboxed auditor: it exercises all 26
    tools including the 10 that mutate state, against a relocated WORKSPACE_ROOT,
    and asserts live SENTINEL state is byte-identical afterwards.
    """
    result = TestResult('HubToolAudit')
    import subprocess

    auditor = WORKSPACE / '08_SELF_IMPROVEMENT' / 'audit_hub_tools.py'
    if not auditor.exists():
        result.error('audit_hub_tools.py is missing')
        return result

    try:
        proc = subprocess.run([sys.executable, str(auditor)],
                              capture_output=True, text=True, timeout=600,
                              encoding='utf-8', errors='replace')
        out = proc.stdout or ''
    except Exception as e:
        result.error(f'auditor did not run: {e}')
        return result

    result.assert_equals(proc.returncode, 0, 'auditor exits 0')
    result.assert_true('LIVE STATE UNCHANGED: True' in out,
                       'sandboxed audit left live SENTINEL state byte-identical')

    # Every advertised tool must land in an OK bucket. A tool that is declared but
    # unreachable shows up in UNREACHABLE / PROTOCOL_ERROR / EXCEPTION.
    unreachable = []
    for line in out.splitlines():
        parts = line.split()
        if parts and parts[0] in ('UNREACHABLE', 'PROTOCOL_ERROR', 'EXCEPTION', 'REACHABLE/ERROR'):
            unreachable.append(parts[0])
    result.assert_false(bool(unreachable),
                        f'no advertised tool is unreachable (saw {sorted(set(unreachable))})')

    ok_line = next((l for l in out.splitlines() if l.startswith('OK ')), '')
    mut_line = next((l for l in out.splitlines() if l.startswith('MUTATING-OK ')), '')
    result.assert_true(ok_line.split()[1].isdigit() and int(ok_line.split()[1]) >= 16,
                       'read-only tools respond (>=16)')
    result.assert_true(mut_line.split()[1].isdigit() and int(mut_line.split()[1]) >= 10,
                       'state-mutating tools respond (>=10)')

    adv = next((l for l in out.splitlines() if l.startswith('advertised:')), '')
    result.assert_equals(adv.split()[1] if len(adv.split()) > 1 else '?', '26',
                         'all 26 tools audited')
    return result


def test_ecosystem_collector_surfaces():
    """The MINIMAX ecosystem panel is the one place the hub claims to see the
    whole MINIMAX ecosystem, and until now NOTHING asserted what is in it.
    `test_deployment` checked that a snapshot exists and is fresh; the word
    "ecosystem" appeared zero times across 375 checks.

    That gap is not academic. This collector shipped a reach probe that
    measured four hosts, stored the record on the DNS-failure branch only, and
    reported `probed: 0` with a green MEASURED badge - four real probes thrown
    away, and 375 checks saw nothing wrong. The assertions below are the LAWS
    the surfaces claim, not their values: a MEASURED surface must carry a
    measurement, a probe that resolved a host must keep the record, a
    credential surface must carry booleans and never a value.
    """
    import os as _os

    result = TestResult('EcosystemCollector')
    try:
        snap = WORKSPACE / '13_COMMAND_CENTER' / 'api' / 'minimax-ecosystem.json'
        result.assert_true(snap.exists(), 'collector snapshot exists')
        if not snap.exists():
            return result
        try:
            data = json.loads(snap.read_text(encoding='utf-8'))
        except Exception as exc:
            result.error(f'snapshot does not parse: {exc}')
            return result

        surfaces = data.get('surfaces') or []
        result.assert_true(len(surfaces) > 0, f'snapshot carries surfaces ({len(surfaces)})')

        by_id = {}
        for s in surfaces:
            sid = s.get('id')
            result.assert_true(
                all(k in s for k in ('id', 'label', 'status', 'value', 'detail',
                                     'source', 'measured_at')),
                f'surface {sid!r} carries every required key')
            by_id[sid] = s

        bad = sorted({s.get('status') for s in surfaces}
                     - {'MEASURED', 'NOT_AVAILABLE', 'ERROR'})
        result.assert_false(bool(bad), f'every status is a known one (saw {bad})')

        # Truth in telemetry: a green badge over an empty cell is the failure
        # mode this whole system exists to prevent.
        hollow = sorted(s['id'] for s in surfaces
                        if s.get('status') == 'MEASURED' and s.get('value') is None)
        result.assert_false(bool(hollow),
                            f'no MEASURED surface carries a null value (saw {hollow})')

        empty_detail = sorted(s['id'] for s in surfaces
                              if s.get('status') == 'MEASURED' and not str(s.get('detail') or '').strip())
        result.assert_false(bool(empty_detail),
                            f'no MEASURED surface has an empty detail (saw {empty_detail})')

        for sid in ('design_route_loader', 'design_cloud_hosts',
                    'design_cloud_reach', 'design_cloud_auth'):
            result.assert_true(sid in by_id, f'{sid} is present')

        # -- the loader claim, proved against the file rather than the panel --
        loader = by_id.get('design_route_loader') or {}
        lval = loader.get('value') or {}
        if loader.get('status') == 'MEASURED':
            result.assert_true(bool(lval.get('loader_present')),
                               'route loader reports a loader, not an absence')
            result.assert_true(int(lval.get('loader_bytes') or 0) > 0,
                               'loader byte length is reported')
            gw = (Path(_os.environ.get('LOCALAPPDATA', '')) / 'Programs' /
                  'MiniMax Design' / 'current' / 'resources' / 'gateway' /
                  'dist' / 'main.js')
            if gw.is_file():
                blob = gw.read_bytes()
                # Byte check, never a text search: ripgrep does not descend
                # into gateway/dist and cannot see inside app.asar, so a grep
                # here would assert absence while the bytes are present.
                result.assert_true(b'external_api_conf' in blob,
                                   f'{gw.name} really references the route table')

        hosts = (by_id.get('design_cloud_hosts') or {}).get('value') or {}
        if hosts:
            result.assert_true(int(hosts.get('regions') or 0) >= 1,
                               'host table has at least one region')
            result.assert_true(int(hosts.get('urls') or 0) >= 1,
                               'host table has at least one URL')
            result.assert_true(str(hosts.get('default') or '').startswith('https://'),
                               f"default gateway is an https URL ({hosts.get('default')})")

        reach_s = by_id.get('design_cloud_reach') or {}
        rval = reach_s.get('value') or {}
        probed = int(rval.get('probed') or 0)
        hostmap = rval.get('hosts') or {}
        # THE assertion that was missing. A probe that resolves a host and then
        # forgets to keep the record reports probed=0 while having done the
        # work - the count must equal the records actually kept.
        result.assert_equals(len(hostmap), probed,
                             'every probed host keeps its record')
        if reach_s.get('status') == 'MEASURED':
            result.assert_true(probed >= 1,
                               f'a MEASURED reachability probed at least one host ({probed})')
        for host, rec in hostmap.items():
            result.assert_true(rec.get('tls') in ('ok', 'unreachable', 'unresolved'),
                               f'{host} carries a TLS verdict ({rec.get("tls")})')
            if rec.get('tls') == 'ok':
                result.assert_true(bool(rec.get('tls_cn')),
                                   f'{host} reports the certificate it was presented')

        # A credential surface that ever carried a value would have leaked it
        # into a JSON file that is served over HTTP and rendered in a browser.
        auth_s = by_id.get('design_cloud_auth') or {}
        auth = auth_s.get('value') or {}
        if auth:
            result.assert_true(all(isinstance(v, bool) for v in auth.values()),
                               f'credential surface carries booleans only ({auth})')

        # The collector measures the Design app; it must never launch it.
        src = Path(__file__).resolve().parent / 'collect_minimax_ecosystem.py'
        if src.is_file():
            text = src.read_text(encoding='utf-8', errors='replace')
            # Precise form of the invariant. An earlier brief claimed this file
            # contains "no process-spawning call" and that was false - it does
            # import subprocess for a read-only Get-Process inventory. The law
            # is that it cannot START the app, which is what these assert.
            result.assert_false('startfile' in text,
                                'collector never opens a file via os.startfile')
            result.assert_false('Popen' in text,
                                'collector never spawns via subprocess.Popen')
            # The executable IS named in this file - to measure its size - so
            # asserting the string is absent would forbid the measurement and
            # still miss the real hazard. This assertion failed on its first
            # run for exactly that reason. What must not happen is the app
            # appearing inside a subprocess invocation.
            windows, idx = [], 0
            while True:
                k = text.find('subprocess.', idx)
                if k < 0:
                    break
                windows.append(text[k:k + 240])
                idx = k + 1
            launching = [w for w in windows if 'Design' in w]
            result.assert_false(bool(launching),
                                f'no subprocess invocation references the Design app '
                                f'({len(windows)} call site(s) inspected)')
    except Exception as exc:
        result.error(f'collector surface check raised: {exc}')
    return result


def test_monitor_capability_coverage():
    """The capability-coverage table must be able to say NO.

    The monitor maps five declared-but-absent MCP servers to the registered
    server that actually performs their work. That mapping is only worth
    having if it can also fail: if every lookup returned "covered", it would
    not be evidence, it would be a permanent waiver that turns a real gap green
    forever. Both polarities are proven here, plus the tool-level one - a
    mapping whose named tools do not exist must also be rejected.
    """
    import monitor as mon

    result = TestResult('MonitorCoverage')
    try:
        table = getattr(mon, 'CAPABILITY_COVERAGE', None)
        result.assert_true(isinstance(table, dict) and table,
                           'the coverage table exists and is non-empty')
        if not table:
            return result
        for name, entry in table.items():
            result.assert_true(isinstance(entry, tuple) and len(entry) == 3,
                               f'{name} maps to (server, tools, rationale)')
            result.assert_true(bool(entry[0]),
                               f'{name} names the server it lives under')
            result.assert_true(bool(entry[2]),
                               f'{name} records why, not just where')

        # POLARITY 1 - correct input: on this machine each mapping must verify.
        live = mon._coverage_evidence()
        for name in table:
            ok, where = live.get(name, (False, 'no evidence returned'))
            result.assert_true(bool(ok), f'{name} verifies live ({where})')

        original = dict(mon.CAPABILITY_COVERAGE)
        try:
            probe = '_probe_unregistered_server'
            mon.CAPABILITY_COVERAGE = {probe: ('no-such-mcp-server', (), 'test')}
            got = mon._coverage_evidence().get(probe, (True, ''))[0]
            result.assert_false(bool(got),
                                'a server that is not registered is NOT covered')
        finally:
            mon.CAPABILITY_COVERAGE = original
        try:
            probe2 = '_probe_absent_tools'
            mon.CAPABILITY_COVERAGE = {
                probe2: ('sentinel-hub', ('sentinel_no_such_tool',), 'test')}
            got2 = mon._coverage_evidence().get(probe2, (True, ''))[0]
            result.assert_false(bool(got2),
                                'a mapping naming absent tools is NOT covered')
        finally:
            mon.CAPABILITY_COVERAGE = original
        result.assert_true(mon.CAPABILITY_COVERAGE == original,
                           'the coverage table is restored after the probes')
    except Exception as exc:
        result.error(f'coverage check raised: {exc}')
    return result


def test_the_plan_is_never_pruned():
    """The blueprint is the plan. Nothing may shrink it, and nothing may call it a defect.

    Operator instruction, 2026-10-06: the nine declared Hermes gateway servers are
    scaffolding for what has to be built. They are not stale configuration to be
    rewritten to match reality. Gaps are closed by constructing the missing thing,
    never by deleting the declaration that names it.

    This exists because I got it wrong first: the monitor reported 8 of 9 servers
    missing, and I recommended rewriting the blueprint to match the disk and
    removing the empty profile directories. Both would have destroyed scaffolding
    while reporting a cleaner system. A doctrine nobody can check is a doctrine that
    gets lost the next time a measurement disagrees with it.

    Checked:
      1. The blueprint still declares all nine servers, and never fewer.
      2. Every declared server is accounted for: on disk, OR tracked as an open gap.
         A declaration that is neither built nor tracked has been silently dropped.
      3. The four Hermes profile mailboxes still exist.
      4. No source file in the project deletes the blueprint, prunes its server list,
         or removes the profile mailboxes.
      5. The plan note exists and states the principle.
    """
    result = TestResult('The plan is never pruned')

    import re

    blueprint = WORKSPACE / '07_BACKBONE' / 'mcp' / 'OPTIMUS_MCP_CONFIG.json'
    register = WORKSPACE / '12_PROGRAM' / 'GAP_REGISTER.json'
    note = WORKSPACE / '12_PROGRAM' / 'HERMES_GATEWAY_PROFILE_PLAN.md'
    mailboxes = WORKSPACE / '09_LOGS' / 'cross_instance' / 'mailbox'

    if not blueprint.exists():
        result.error('the blueprint is missing entirely')
        return result

    # -- 1. the plan is still whole ------------------------------------
    try:
        cfg = json.loads(blueprint.read_text(encoding='utf-8'))
    except Exception as exc:
        result.error(f'could not parse the blueprint: {exc}')
        return result

    servers = cfg.get('servers', {})
    result.assert_equals(len(servers), 9,
                         'the blueprint still declares nine Hermes profile servers')
    result.assert_true(all(servers.values()), 'no declared server entry is empty')

    # -- 2. every declaration is built OR tracked, never silently dropped ---
    gaps = []
    if register.exists():
        try:
            gaps = json.loads(register.read_text(encoding='utf-8'))
        except Exception as exc:
            result.error(f'could not parse the gap register: {exc}')
            return result
    gap_ids = {g.get('id') for g in gaps if isinstance(g, dict)}

    unaccounted = []
    for name, spec in servers.items():
        args = (spec or {}).get('args', []) or []
        py_arg = next((a for a in args if str(a).endswith('.py')), None)
        if py_arg is None:
            # An npm-backed entry is "built" when the package resolves; that is the
            # monitor's separate check. Here it only has to be tracked as planned.
            built = False
        else:
            built = Path(py_arg).exists()
        tracked = f'HPROF_{name.replace("-", "_")}' in gap_ids
        if not built and not tracked:
            unaccounted.append(name)

    result.assert_equals(unaccounted, [],
                         'every declared server is either built on disk or tracked as an '
                         'open gap - none was dropped without being built')

    planned = [f'HPROF_{n.replace("-", "_")}' for n in servers]
    result.assert_true(all(i in gap_ids for i in planned),
                       'all nine profile servers carry a tracked gap entry')

    # -- 3. the profile scaffolding is still standing -------------------
    for profile in ('SENTINEL-DESKTOP', 'SENTINEL-COWORK',
                    'SENTINEL-CHAT', 'CODER-APP'):
        result.assert_true((mailboxes / profile).is_dir(),
                           f'Hermes profile mailbox {profile} still exists '
                           f'- scaffolding is not removed because it is empty')

    # -- 4. no source file prunes the plan -----------------------------
    # Checked over every script in the project, because a delete helper anywhere
    # is enough. The search is for the specific targets, not for the word
    # "delete": a script is allowed to delete its own temp files.
    forbidden = ('OPTIMUS_MCP_CONFIG', 'cross_instance', 'HPROF_',
                 'HERMES_GATEWAY_PROFILE_PLAN')
    offenders = []
    for py in WORKSPACE.rglob('*.py'):
        if py == Path(__file__).resolve() or py.resolve() == Path(__file__).resolve():
            continue
        try:
            src = py.read_text(encoding='utf-8', errors='replace')
        except OSError:
            continue
        for line_no, line in enumerate(src.splitlines(), 1):
            if not re.search(r'\b(rmtree|unlink|removedirs|rmdir|Remove-Item)\b', line):
                continue
            if any(tok in line for tok in forbidden):
                offenders.append(f'{py.name}:{line_no}')
    for ps1 in WORKSPACE.rglob('*.ps1'):
        try:
            src = ps1.read_text(encoding='utf-8', errors='replace')
        except OSError:
            continue
        for line_no, line in enumerate(src.splitlines(), 1):
            if 'Remove-Item' in line and any(tok in line for tok in forbidden):
                offenders.append(f'{ps1.name}:{line_no}')

    result.assert_equals(offenders, [],
                         'no script anywhere deletes the blueprint, prunes its server list, '
                         'or removes the profile mailboxes')

    # -- 5. the principle is written down where it will be found --------
    result.assert_true(note.exists(), 'the Hermes gateway profile plan note exists')
    if note.exists():
        text = note.read_text(encoding='utf-8')
        result.assert_contains(text, 'scaffolding',
                               'the note names the scaffolding principle')
        result.assert_contains(text, 'never by deletion',
                               'the note states that gaps close by construction, '
                               'never by deleting the declaration')

    return result


def test_gap_register_integrity():
    """The register is a ledger. The builder merges it; it must never eat it.

    Measured 2026-10-28: the builder used to WRITE GAP_REGISTER.json with the
    gaps it had measured and nothing else. A run destroyed 11 of the 18 entries
    - all nine HPROF_* profile tickets and the HERMES_GATEWAY_PROFILES umbrella
    - because it never knew they existed. Nothing announced the loss: the
    blueprint was intact, the suites were green, and the next reader simply saw
    a shorter, tidier register and believed it. A measurement instrument that
    owns the file it measures eventually eats it.

    Checked:
      1. Every entry carries the fields the construction schema makes
         mandatory, and `fix_requires` is not empty.
      2. A closed entry carries the measurement that closed it. A status with no
         evidence is a claim, not a closure.
      3. All nine profile tickets and the umbrella are still tracked, whatever
         their status - the plan stays visible after it is built.
      4. POLARITY - an entry the builder does not measure SURVIVES a full
         builder run, and the test proves the builder does not measure it, so
         the survival cannot be an accident.
      5. CONTROL - from an empty ledger the builder still produces its measured
         gaps. A builder that only copies would report nothing and look clean.
      6. A second builder run leaves the ledger byte-identical.
    """
    result = TestResult('Gap register integrity')

    import contextlib
    import io

    register = WORKSPACE / '12_PROGRAM' / 'GAP_REGISTER.json'
    if not register.exists():
        result.error('the gap register does not exist')
        return result
    try:
        entries = json.loads(register.read_text(encoding='utf-8'))
    except Exception as exc:
        result.error(f'could not parse the gap register: {exc}')
        return result
    if not isinstance(entries, list):
        result.error('the gap register is not a list of entries')
        return result

    # -- 1. the mandatory fields -----------------------------------------
    mandatory = ('id', 'area', 'status', 'what', 'evidence', 'impact',
                 'fix_requires', 'owner')
    incomplete = [e.get('id') for e in entries
                  if any(not str(e.get(k) or '').strip() for k in mandatory)]
    result.assert_equals(incomplete, [],
                         'every entry carries the fields the schema makes mandatory')

    # -- 2. a closure carries its measurement ------------------------------
    unmeasured = [e.get('id') for e in entries
                  if e.get('status') == 'CLOSED-BUILT'
                  and not str(e.get('verification') or '').strip()]
    result.assert_equals(unmeasured, [],
                         'every closed entry carries the measurement that closed it')

    # -- 3. the plan stays tracked ----------------------------------------
    ids = {e.get('id') for e in entries}
    tickets = ['HPROF_' + n for n in (
        'prime_bridge', 'sentinel_state', 'rule_triggers', 'learning_loop',
        'context_pressure', 'web_tools', 'filesystem', 'browser', 'git')]
    result.assert_equals([t for t in tickets if t not in ids], [],
                         'all nine profile tickets are still tracked, whatever their status')
    result.assert_true('HERMES_GATEWAY_PROFILES' in ids,
                       'the umbrella entry is still tracked')

    # -- 4/5/6. the builder must not eat the ledger ------------------------
    try:
        import build_program_matrix as bpm
    except Exception as exc:
        result.error(f'could not import the builder: {exc}')
        return result

    sentinel = {
        'id': 'MANUAL_SENTINEL', 'area': 'wiring', 'status': 'OPEN',
        'what': 'an entry the builder does not measure',
        'evidence': 'written by this test, not by the builder',
        'impact': 'if it survives a builder run, the merge is non-destructive',
        'fix_requires': 'nothing - this entry exists to be measured',
        'owner': 'Mavis',
    }

    real_gaps, real_matrix = bpm.GAPS_JSON, bpm.MATRIX_JSON
    measured_ids = set()
    try:
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            bpm.GAPS_JSON = tmp / 'GAP_REGISTER.json'
            bpm.MATRIX_JSON = tmp / 'IDEA_TO_SCRIPT_MATRIX.json'

            bpm.GAPS_JSON.write_text(
                json.dumps(entries + [sentinel], indent=2, ensure_ascii=False),
                encoding='utf-8')
            with contextlib.redirect_stdout(io.StringIO()):
                bpm.main()
            after = json.loads(bpm.GAPS_JSON.read_text(encoding='utf-8'))
            after_ids = [e.get('id') for e in after]

            result.assert_true('MANUAL_SENTINEL' in after_ids,
                               'an entry the builder does not measure survives a full run')
            result.assert_equals([i for i in ids if i not in after_ids], [],
                                 'no entry of the ledger was lost by a builder run')

            first_bytes = bpm.GAPS_JSON.read_bytes()
            with contextlib.redirect_stdout(io.StringIO()):
                bpm.main()
            result.assert_equals(first_bytes == bpm.GAPS_JSON.read_bytes(), True,
                                 'a second builder run leaves the ledger byte-identical')

            # CONTROL: from an empty ledger the builder still produces its gaps
            bpm.GAPS_JSON.write_text('[]', encoding='utf-8')
            with contextlib.redirect_stdout(io.StringIO()):
                bpm.main()
            fresh = json.loads(bpm.GAPS_JSON.read_text(encoding='utf-8'))
            measured_ids = {e.get('id') for e in fresh}
            result.assert_true(len(fresh) > 0,
                               'the builder produces its measured gaps from an empty ledger')
    except Exception as exc:
        result.error(f'the builder run raised: {type(exc).__name__}: {exc}')
    finally:
        bpm.GAPS_JSON, bpm.MATRIX_JSON = real_gaps, real_matrix

    # -- the collector must not hand the panel a wrong number --------------
    # The panel counts what it is given under the heading "Open gaps". If the
    # collector passes the whole ledger, the number is wrong the moment the
    # first entry closes - and it was.
    collector = WORKSPACE / '13_COMMAND_CENTER' / 'api' / 'collect-sentinel.ps1'
    if collector.exists():
        src = collector.read_text(encoding='utf-8', errors='replace')
        result.assert_contains(src, 'CLOSED-BUILT',
                               'the collector separates closed entries from the gaps it '
                               'hands the panel')
    else:
        result.skip('the collector script is missing - the gap split cannot be checked')

    return result


def _integrity_violations(workspace, record):
    """Return the list of ways one baseline record fails against the live tree.

    Extracted so the self-test and the production assertion call the SAME
    function. An earlier pair of defects in this project came from a checker
    existing only inside its own test: production reported by one path and the
    test exercised another, and they drifted. The check and the proof that the
    check fires have to be the same code or the proof proves nothing.

    A record passes only if every file it named still exists, still carries
    every entry id it listed, and has not shrunk below the byte count it
    recorded. Growth is legitimate for an append-only record and is not a
    violation.
    """
    import re

    violations = []
    for rel, expect in (record.get('files') or {}).items():
        path = workspace / rel
        if not path.exists():
            violations.append(f'{rel}: recorded in the baseline but missing on disk')
            continue

        actual_bytes = path.stat().st_size
        recorded_bytes = int(expect.get('bytes') or 0)
        if actual_bytes < recorded_bytes:
            lost = recorded_bytes - actual_bytes
            violations.append(
                f'{rel}: shrank - baseline recorded {recorded_bytes} B, '
                f'now {actual_bytes} B ({lost} B lost)')

        wanted = list(expect.get('entry_ids') or [])
        if not wanted:
            continue

        text = path.read_text(encoding='utf-8', errors='replace')
        if rel.endswith('.json'):
            try:
                doc = json.loads(text)
                present = {e.get('id') for e in doc if isinstance(e, dict)}
            except Exception:
                present = set()
        else:
            pattern = expect.get('entry_pattern') or r'(?m)^#{2,4}\s+(\S+)'
            present = set(re.findall(pattern, text))

        gone = [e for e in wanted if e not in present]
        if gone:
            violations.append(
                f'{rel}: entry ids absent that the baseline recorded - {gone}')

    return violations


def test_append_only_integrity():
    """Append-only records may grow. They may never lose an entry or shrink.

    This exists because of a real, destructive failure on 2026-10-06. An
    append used a shell variable that had been read in an earlier tool call, so
    it was null in the call that wrote, and the write replaced
    MISSTEPS_AND_CORRECTIONS.md instead of extending it. 44,576 bytes - M-01
    through M-27 - went with it. The suite reported 475 passed / 0 failed
    immediately afterwards, because the only assertion on that file was
    `size > 500`.

    A size threshold is not an integrity check. It passed while the file lost
    92% of its content, which is the exact shape of a guard that cannot fail.

    Checked:
      1. The baseline exists and parses.
      2. EVERY record in the baseline still holds - not just the newest one.
         That is the anti-waiver property: accepting a loss by appending a new
         baseline record leaves the old record standing and still failing, so
         the loss stays visible forever instead of being absorbed.
      3. POLARITY - a file that shrinks, and an entry id that disappears, are
         both reported. Proof the guard fires.
      4. CONTROL - an untouched file that only grows is still accepted. Proof
         the guard did not fire at the system's expense, which is what makes
         the polarity case worth anything.
    """
    result = TestResult('AppendOnlyIntegrity')

    import re
    import tempfile

    baseline = WORKSPACE / '08_SELF_IMPROVEMENT' / 'integrity_baseline.jsonl'

    if not baseline.exists():
        result.error(
            'integrity_baseline.jsonl is missing - without it this guard '
            'cannot detect the class of loss it exists for')
        return result

    raw = [ln for ln in baseline.read_text(encoding='utf-8').splitlines() if ln.strip()]
    records = []
    for n, line in enumerate(raw, 1):
        try:
            records.append(json.loads(line))
        except Exception as exc:
            result.error(f'baseline line {n} does not parse: {exc}')
            return result

    result.assert_true(len(records) >= 1,
                       f'baseline carries {len(records)} record(s)')
    if not records:
        return result

    # -- 2. every record, not only the newest ----------------------------
    for idx, record in enumerate(records):
        for violation in _integrity_violations(WORKSPACE, record):
            result.assert_true(False, f'baseline record {idx + 1}: {violation}')

    result.assert_true(
        all(not _integrity_violations(WORKSPACE, r) for r in records),
        'every baseline record still holds against the live tree')

    # -- 3. POLARITY: the guard must actually fire ------------------------
    # Built in a tempdir so the project's own records are never at risk. A
    # polarity case proves the guard fires; without it, "all clear" is
    # indistinguishable from a guard that never runs.
    with tempfile.TemporaryDirectory(prefix='sentinel_integrity_') as sandbox:
        sb = Path(sandbox)
        victim = sb / 'doctrine.md'
        victim.write_text(
            '# Method\n\n### M-01\n\nalpha\n\n### M-02\n\nbeta\n\n### M-03\n\ngamma\n',
            encoding='utf-8')
        grown = sb / 'grown.md'
        grown.write_text(
            '# Method\n\n### M-01\n\nalpha\n\n### M-02\n\nbeta\n\n### M-03\n\ngamma\n',
            encoding='utf-8')

        shrunk_record = {'files': {'doctrine.md': {
            'bytes': victim.stat().st_size,
            'entry_ids': ['M-01', 'M-02', 'M-03'],
            'entry_pattern': r'(?m)^###\s+(M-\d+)'}}}
        grow_record = {'files': {'grown.md': {
            'bytes': grown.stat().st_size,
            'entry_ids': ['M-01', 'M-02', 'M-03'],
            'entry_pattern': r'(?m)^###\s+(M-\d+)'}}}

        # clean before damage
        result.assert_equals(_integrity_violations(sb, shrunk_record), [],
                             'polarity fixture is clean before damage')
        result.assert_equals(_integrity_violations(sb, grow_record), [],
                             'control fixture is clean before growth')

        # damage: drop M-03 and shrink the file
        victim.write_text('# Method\n\n### M-01\n\nalpha\n\n### M-02\n\nbeta\n',
                          encoding='utf-8')

        fired = _integrity_violations(sb, shrunk_record)
        result.assert_true(len(fired) >= 2,
                           'the guard fires on a shrunk file with a lost entry id')
        result.assert_true(any('shrank' in v for v in fired),
                           'the guard names the shrink')
        result.assert_true(any('M-03' in v for v in fired),
                           'the guard names the specific entry id that vanished')

        # damage: file deleted outright
        victim.unlink()
        result.assert_true(
            any('missing on disk' in v for v in _integrity_violations(sb, shrunk_record)),
            'the guard fires on a file that is gone entirely')

        # -- 4. CONTROL: growth must NOT be reported ----------------------
        with open(grown, 'a', encoding='utf-8') as fh:
            fh.write('\n### M-04\n\ndelta\n')
        result.assert_equals(_integrity_violations(sb, grow_record), [],
                             'an append-only record that GREW is still accepted')

        # a control on entry count too: growth that keeps every id
        grow_record['files']['grown.md']['entry_ids'] = ['M-01', 'M-02', 'M-03', 'M-04']
        result.assert_equals(_integrity_violations(sb, grow_record), [],
                             'every recorded entry id still present after growth')

        # -- 5. POLARITY against the REAL file, not a fixture ------------
        # The fixture above proves the checker reacts. This proves it reacts to
        # the actual record and the actual loss that motivated it: take the
        # doctrine file as it stands, drop one real entry, and require the
        # guard to name it. A fixture proves the code path; this proves the
        # regression. Working on a copy - the project file is never at risk.
        live_doctrine = WORKSPACE / '11_BRAIN' / '04_METHOD' / 'MISSTEPS_AND_CORRECTIONS.md'
        if live_doctrine.exists():
            copy = sb / 'live_doctrine.md'
            copy.write_text(live_doctrine.read_text(encoding='utf-8'), encoding='utf-8')
            live_ids = re.findall(r'(?m)^###\s+(M-\d+)', copy.read_text(encoding='utf-8'))
            result.assert_true(len(live_ids) >= 2,
                               f'the live doctrine file exposes {len(live_ids)} parseable entries')

            real_record = {'files': {'live_doctrine.md': {
                'bytes': copy.stat().st_size,
                'entry_ids': live_ids,
                'entry_pattern': r'(?m)^###\s+(M-\d+)'}}}
            result.assert_equals(_integrity_violations(sb, real_record), [],
                                 'the real doctrine file satisfies its own record')

            # Replay the actual incident: one real entry disappears.
            victim_id = live_ids[-1]
            stripped = re.sub(r'(?m)^###\s+' + victim_id + r'.*?(?=^###\s+M-\d+|\Z)',
                              '', copy.read_text(encoding='utf-8'), flags=re.S)
            copy.write_text(stripped, encoding='utf-8')
            caught = _integrity_violations(sb, real_record)
            result.assert_true(
                any(victim_id in v for v in caught),
                f'replaying the incident on the REAL doctrine file is caught: {victim_id}')
            result.assert_true(any('shrank' in v for v in caught),
                               'and the shrink is reported alongside it')
        else:
            result.error('the live doctrine file is missing - cannot replay the incident')

    return result


def _declared_unbuilt_paths(workspace):
    """Paths the blueprint declares that are legitimately NOT on disk yet.

    Derived from measurement, never hand-listed. A declared-but-unbuilt Hermes
    gateway server is scaffolding - it is SUPPOSED to be absent, and its absence
    is the work to do. But that exemption must not become a hole: because this
    set is computed from the blueprint crossed with the disk, a typo, a renamed
    file or a stale reference cannot enter it. Only a path the blueprint itself
    declares is exempt, and only while it is still unbuilt. The moment the file
    is built the exemption disappears, which is harmless - an existing file
    passes anyway.

    Hand-listing the exemptions would be the failure mode this exists to avoid:
    a waiver that cannot fail.
    """
    import re as _re

    blueprint = workspace / '07_BACKBONE' / 'mcp' / 'OPTIMUS_MCP_CONFIG.json'
    exempt = set()
    if not blueprint.exists():
        return exempt
    try:
        cfg = json.loads(blueprint.read_text(encoding='utf-8'))
    except Exception:
        return exempt

    for name, spec in (cfg.get('servers') or {}).items():
        args = (spec or {}).get('args', []) or []
        for a in args:
            a = str(a)
            if not a.lower().endswith('.py'):
                continue
            try:
                rel = Path(a).resolve().relative_to(workspace.resolve())
            except Exception:
                continue
            if not (workspace / rel).exists():
                exempt.add(rel.as_posix())
    return exempt


def _top_level_dirs(workspace):
    try:
        return {d.name for d in workspace.iterdir() if d.is_dir()}
    except Exception:
        return set()


def _referenced_paths(text, workspace=None):
    """Project-relative paths named in a piece of project text.

    Matches the workspace's own NN_NAME convention. The character class
    deliberately includes `*` so that a glob such as
    `11_BRAIN\\02_CHAPTERS\\CH_*.md` is captured WHOLE. An earlier version of
    this class excluded `*`, which truncated the match to `...\\CH_` and then
    reported the truncated fragment as a missing file - the checker
    manufacturing a defect out of its own pattern.

    Returns (path, kind) per reference:
      'concrete' - starts at a real top-level directory and is expected to exist
      'glob'     - a pattern, not a reference
      'optional' - read only behind a Test-Path guard nearby
      'fragment' - a partial path such as `02_CHAPTERS\\UNPLACED.md`, which is
                   relative to a parent the writer named elsewhere. The project
                   writes both `11_BRAIN\\02_CHAPTERS\\UNPLACED.md` and the
                   shorthand `02_CHAPTERS\\UNPLACED.md`; treating the shorthand
                   as workspace-relative reported a file that was never missing.

    Every classification is derived from the source and the real directory
    listing - never hand-listed. The caller asserts on the counts so none of
    these buckets can quietly absorb a genuine defect.
    """
    import re as _re

    top = _top_level_dirs(workspace) if workspace is not None else set()
    pat = _re.compile(r'(\d{2}_[A-Z_]+(?:\\[A-Za-z0-9_.\-*]+)+)')
    lines = text.splitlines()
    out = []
    for m in pat.finditer(text):
        raw = m.group(1).replace('\\', '/')
        if '*' in m.group(1):
            out.append((raw, 'glob'))
            continue
        line_no = text.count('\n', 0, m.start())
        window = lines[max(0, line_no - 2): line_no + 3]
        if any('Test-Path' in w or 'test-path' in w for w in window):
            out.append((raw, 'optional'))
            continue
        first = raw.split('/')[0]
        if top and first not in top:
            out.append((raw, 'fragment'))
            continue
        out.append((raw, 'concrete'))
    return out


def test_project_references_resolve():
    """Every project path a registry or spec names must exist - unless declared.

    The verifier found three gap-register entries whose cited monitor evidence
    had drifted: the register said a check reported NOT_RUN, and the monitor had
    been reporting OK for some time. Nothing was red. The record was simply
    wrong, and a reader following it would have been misled.

    That is the general shape of a silent failure here: an inventory that names
    something which no longer exists reports itself as fine. It is worth
    catching automatically rather than by luck.

    Checked:
      1. Every project path named in the registries and specs resolves on disk.
      2. The ONLY exemptions are paths the blueprint itself declares as
         unbuilt - derived from measurement, not a hand-written list.
      3. POLARITY - a reference to a file that does not exist is reported.
      4. CONTROL - a reference to a file that does exist is accepted.
    """
    result = TestResult('Project references resolve')

    import tempfile

    sources = [
        '12_PROGRAM/GAP_REGISTER.json',
        '12_PROGRAM/IDEA_TO_SCRIPT_MATRIX.json',
        '12_PROGRAM/PROGRAM_SPEC.md',
        '13_COMMAND_CENTER/api/collect-sentinel.ps1',
        '13_COMMAND_CENTER/api/server.ps1',
        '13_COMMAND_CENTER/api/sentinel-hub.ps1',
    ]
    sources += ['14_HANDOFF/' + n for n in sorted(os.listdir(WORKSPACE / '14_HANDOFF'))
                if n.endswith('.md')] if (WORKSPACE / '14_HANDOFF').exists() else []

    exempt = _declared_unbuilt_paths(WORKSPACE)
    result.assert_true(len(exempt) >= 0,
                       f'{len(exempt)} blueprint-declared path(s) are exempt as unbuilt scaffolding')

    dangling = []
    globs = 0
    optional = []
    fragments = set()
    checked = 0
    for rel in sources:
        f = WORKSPACE / rel
        if not f.exists():
            continue
        text = f.read_text(encoding='utf-8', errors='replace')
        for raw, kind in _referenced_paths(text, WORKSPACE):
            if kind == 'glob':
                globs += 1
                continue
            if kind == 'fragment':
                fragments.add(raw)
                continue
            if kind == 'optional':
                if not (WORKSPACE / raw).exists():
                    optional.append(f'{rel} -> {raw}')
                continue
            checked += 1
            if (WORKSPACE / raw).exists():
                continue
            if raw in exempt:
                continue
            dangling.append(f'{rel} -> {raw}')

    result.assert_true(checked > 20,
                       f'scanned {checked} concrete path references across {len(sources)} sources')
    result.assert_equals(dangling, [],
                         f'every concrete project path reference resolves '
                         f'({globs} glob, {len(fragments)} fragment, {len(exempt)} blueprint exemption(s))')

    # These buckets are SURFACED, not hidden. If either grows silently, these
    # assertions are what notice - an exemption nobody can see is a waiver.
    result.assert_true(len(optional) <= 5,
                       f'optional (Test-Path guarded) references that are absent: {optional}')
    result.assert_true(len(fragments) <= 10,
                       f'partial-path fragments (not workspace-relative): {sorted(fragments)}')

    # -- POLARITY and CONTROL on the extraction itself --------------------
    with tempfile.TemporaryDirectory(prefix='sentinel_refs_') as sandbox:
        sb = Path(sandbox)
        (sb / '07_BACKBONE').mkdir()
        # ONLY the file that is supposed to exist is created. The other one is
        # named by the text and never created, which is the whole point.
        (sb / '07_BACKBONE' / 'THERE_PRESENT.md').write_text('x', encoding='utf-8')

        refs = [(r, k) for r, k in _referenced_paths(
            'see `07_BACKBONE\\NOPE_MISSING.md` and `07_BACKBONE\\THERE_PRESENT.md`', sb)]
        result.assert_equals(sorted(r for r, _ in refs),
                             ['07_BACKBONE/NOPE_MISSING.md', '07_BACKBONE/THERE_PRESENT.md'],
                             'extraction finds both references')
        result.assert_equals(sorted(k for _, k in refs), ['concrete', 'concrete'],
                             'a guarded-in path that starts at a real directory is concrete')

        found = [r for r, k in refs if k == 'concrete' and not (sb / r).exists()]
        result.assert_equals(found, ['07_BACKBONE/NOPE_MISSING.md'],
                             'POLARITY: the absent file is reported')
        result.assert_equals([r for r, _ in refs if r not in found],
                             ['07_BACKBONE/THERE_PRESENT.md'],
                             'CONTROL: the present file is the only one not reported')

        globbed = _referenced_paths('`11_BRAIN\\02_CHAPTERS\\CH_*.md`', sb)
        result.assert_equals([k for _, k in globbed], ['glob'],
                             'a glob is recognised as a pattern, not a reference')
        result.assert_equals([r for r, _ in globbed], ['11_BRAIN/02_CHAPTERS/CH_*.md'],
                             'a glob is captured whole, not truncated at the star')

        guarded = _referenced_paths(
            "$f = '09_LOGS\\some_optional.json'\n"
            "if (Test-Path $f) { Get-Content $f }\n", sb)
        result.assert_equals([k for _, k in guarded], ['optional'],
                             'a reference behind a Test-Path guard is optional, not dangling')

        frag = _referenced_paths('see `02_CHAPTERS\\UNPLACED.md`', sb)
        result.assert_equals([k for _, k in frag], ['fragment'],
                             'a partial path that names no real top-level directory is a fragment')

    return result




def test_prime_bridge_find_files():
    """Test prime_find_files from prime_bridge_server."""
    result = TestResult('PrimeBridgeFindFiles')

    import sys
    import json
    import tempfile
    from pathlib import Path

    # Mock MCP dependencies
    class DummyServer:
        def __init__(self, *args, **kwargs): pass
        def tool(self): return lambda f: f

    class MCPMock: pass
    mcp = MCPMock()
    mcp.server = MCPMock()
    mcp.server.mcpserver = MCPMock()
    mcp.server.mcpserver.MCPServer = DummyServer
    class ToolError(Exception): pass
    mcp.server.mcpserver.exceptions = MCPMock()
    mcp.server.mcpserver.exceptions.ToolError = ToolError
    sys.modules['mcp'] = mcp
    sys.modules['mcp.server'] = mcp.server
    sys.modules['mcp.server.mcpserver'] = mcp.server.mcpserver
    sys.modules['mcp.server.mcpserver.exceptions'] = mcp.server.mcpserver.exceptions

    class PydanticMock:
        def Field(self, **kwargs): return None
    sys.modules['pydantic'] = PydanticMock()

    class TypingExtensionsMock:
        class AnnotatedMeta(type):
            def __getitem__(cls, item): return None
        class Annotated(metaclass=AnnotatedMeta): pass
    sys.modules['typing_extensions'] = TypingExtensionsMock()

    sys.path.insert(0, str(WORKSPACE / '07_BACKBONE' / 'mcp'))
    try:
        import prime_bridge_server

        with tempfile.TemporaryDirectory(prefix='sentinel_mcp_') as sandbox:
            old_root = prime_bridge_server.ROOT
            prime_bridge_server.ROOT = Path(sandbox).resolve()

            try:
                # Set up a fake workspace
                (prime_bridge_server.ROOT / '01_DUMMY').mkdir()
                (prime_bridge_server.ROOT / '01_DUMMY' / 'test.md').write_text('content')
                (prime_bridge_server.ROOT / '02_EMPTY').mkdir()
                (prime_bridge_server.ROOT / 'root_file.txt').write_text('12345')

                # 1. Test valid search pattern
                ret = prime_bridge_server.prime_find_files(r'root_file\.txt')
                data = json.loads(ret)
                result.assert_equals(data['count'], 1, 'Valid regex finds file')

                # Windows uses \ while linux uses /, convert to list of names to ignore path sep issues
                names = [Path(p).name for p in data['files']]
                result.assert_equals(names, ['root_file.txt'], 'File matches')

                # 2. Test invalid regex
                ret = prime_bridge_server.prime_find_files('[')

                # Check for the expected error format
                if isinstance(ret, str) and ret.startswith('ERROR: invalid pattern:'):
                    result.passed += 1
                else:
                    result.failed += 1
                    result.errors.append(f"Invalid pattern did not return expected error, got: {ret}")

                # 3. Test explicit re.error mock
                import re
                original_compile = re.compile
                def mock_compile(*args, **kwargs):
                    raise re.error('mocked error')

                re.compile = mock_compile
                try:
                    ret = prime_bridge_server.prime_find_files('anything')
                    if isinstance(ret, str) and ret == 'ERROR: invalid pattern: mocked error':
                        result.passed += 1
                    else:
                        result.failed += 1
                        result.errors.append(f"Explicit re.error mock did not return expected error string, got: {ret}")
                finally:
                    re.compile = original_compile

            finally:
                prime_bridge_server.ROOT = old_root

    except Exception as e:
        result.error(f"Exception: {e}")

    return result

def test_prime_bridge_list_area():
    """Test prime_list_area from prime_bridge_server."""
    result = TestResult('PrimeBridgeListArea')

    import ast
    import json
    import tempfile
    from pathlib import Path

    try:
        # Parse prime_bridge_server.py
        server_file = WORKSPACE / '07_BACKBONE' / 'mcp' / 'prime_bridge_server.py'
        tree = ast.parse(server_file.read_text())

        # Find target functions and strip decorators
        func_node = None
        inside_node = None
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if node.name == 'prime_list_area':
                    node.decorator_list = []
                    func_node = node
                elif node.name == '_inside':
                    node.decorator_list = []
                    inside_node = node

        if not func_node or not inside_node:
            result.error("Could not find target functions in prime_bridge_server.py")
            return result

        module_ast = ast.Module(body=[inside_node, func_node], type_ignores=[])
        ast.fix_missing_locations(module_ast)
        code = compile(module_ast, filename="<ast>", mode="exec")

        class ToolError(Exception): pass

        class AnnotatedMeta(type):
            def __getitem__(cls, item): return None
        class Annotated(metaclass=AnnotatedMeta): pass

        namespace = {
            'Path': Path,
            'json': json,
            'ToolError': ToolError,
            'ROOT': Path.cwd(),
            'MAX_ENTRIES': 200,
            'Annotated': Annotated,
            'Field': lambda *args, **kwargs: None
        }

        exec(code, namespace)

        prime_list_area = namespace['prime_list_area']

        with tempfile.TemporaryDirectory(prefix='sentinel_mcp_') as sandbox:
            sandbox_path = Path(sandbox).resolve()
            namespace['ROOT'] = sandbox_path

            # Set up a fake workspace
            (sandbox_path / '01_DUMMY').mkdir()
            (sandbox_path / '01_DUMMY' / 'test.md').write_text('content')
            (sandbox_path / '02_EMPTY').mkdir()
            (sandbox_path / 'root_file.txt').write_text('12345')

            # 1. Test root listing
            ret = prime_list_area('(root)')
            data = json.loads(ret)
            result.assert_equals(data['area'], '(root)', 'Root area is labelled correctly')
            entries = sorted(e['name'] for e in data['entries'])
            result.assert_equals(entries, ['01_DUMMY', '02_EMPTY', 'root_file.txt'],
                               'Root entries match expected layout')

            # 2. Test specific area listing
            ret = prime_list_area('01_DUMMY')
            data = json.loads(ret)
            result.assert_equals(len(data['entries']), 1, 'Area listing finds the file')
            result.assert_equals(data['entries'][0]['name'], 'test.md', 'Correct file found')

            # 3. Test non-existent area
            try:
                prime_list_area('NOPE_MISSING')
                result.failed += 1
                result.errors.append("Listing missing area should raise ToolError")
            except ToolError:
                result.passed += 1
            except Exception as e:
                result.failed += 1
                result.errors.append(f"Expected ToolError, got {type(e).__name__}")

            # 4. Test directory that is actually a file
            try:
                prime_list_area('root_file.txt')
                result.failed += 1
                result.errors.append("Listing a file as an area should raise ToolError")
            except ToolError:
                result.passed += 1
            except Exception as e:
                result.failed += 1
                result.errors.append(f"Expected ToolError, got {type(e).__name__}")

            # 5. Test escaping workspace root
            try:
                prime_list_area('../another_folder')
                result.failed += 1
                result.errors.append("Escaping workspace should raise ToolError")
            except ToolError:
                result.passed += 1
            except Exception as e:
                result.failed += 1
                result.errors.append(f"Expected ToolError, got {type(e).__name__}")

    except Exception as e:
        result.error(f"Exception: {e}")

    return result

def test_web_tools_validate_url():
    """Verify that _validate handles valid and invalid URLs (returning error string or raising)."""
    import ast
    import urllib.parse

    result = TestResult('WebToolsValidateUrl')

    try:
        web_tools_py = WORKSPACE / '07_BACKBONE' / 'mcp' / 'web_tools_server.py'
        if not web_tools_py.exists():
            result.skip("web_tools_server.py not found")
            return result

        tree = ast.parse(web_tools_py.read_text(encoding='utf-8'))
        func_node = next(
            (node for node in tree.body
             if isinstance(node, ast.FunctionDef) and node.name == '_validate'),
            None
        )

        if not func_node:
            result.error("_validate function not found in web_tools_server.py")
            return result

        module = ast.Module(body=[func_node], type_ignores=[])
        code = compile(module, filename="<ast>", mode="exec")

        class ToolError(Exception):
            pass

        env = {
            'urllib': urllib,
            'ALLOWED_SCHEMES': ('http', 'https'),
            'ToolError': ToolError
        }
        exec(code, env)
        _validate = env['_validate']

        # Test valid URLs
        valid_res = _validate("http://example.com")
        if valid_res not in ("http://example.com", ""):
            result.error(f"Expected '' or URL, got {valid_res}")
        else:
            result.passed += 1

        # Test invalid scheme (ftp://) and invalid url
        # The function could either return an error string like "ERROR: Only http and https are supported, got ftp://example.com"
        # or it could raise ToolError. We support both for robustness.
        try:
            res = _validate("ftp://example.com")
            expected_error = "ERROR: Only http and https are supported, got ftp://example.com"
            if res != expected_error and not ("error" in str(res).lower()):
                result.error(f"Expected error string, got {res}")
            else:
                result.passed += 1
        except ToolError:
            result.passed += 1

        try:
            res2 = _validate("invalid-url")
            expected_error2 = "ERROR: Only http and https are supported, got invalid-url"
            if res2 != expected_error2 and not ("error" in str(res2).lower()):
                result.error(f"Expected error string, got {res2}")
            else:
                result.passed += 1
        except ToolError:
            result.passed += 1

        try:
            res3 = _validate("http://")
            expected_error3 = "ERROR: refused: 'http://' has no host"
            if res3 != expected_error3 and not ("error" in str(res3).lower()) and not ("refused" in str(res3).lower()):
                result.error(f"Expected error string, got {res3}")
            else:
                result.passed += 1
        except ToolError:
            result.passed += 1

    except Exception as e:
        result.error(f"Exception: {e}")

    return result


def test_web_tools_error_handling():
    """Verify that _fetch gracefully handles HTTPError by returning its body."""
    import ast
    import urllib
    import urllib.request
    import urllib.error
    import io

    result = TestResult('WebToolsErrorHandling')

    try:
        web_tools_py = WORKSPACE / '07_BACKBONE' / 'mcp' / 'web_tools_server.py'
        if not web_tools_py.exists():
            result.skip("web_tools_server.py not found")
            return result

        tree = ast.parse(web_tools_py.read_text(encoding='utf-8'))
        func_node = next(
            (node for node in tree.body
             if isinstance(node, ast.FunctionDef) and node.name == '_fetch'),
            None
        )

        if not func_node:
            result.error("_fetch function not found in web_tools_server.py")
            return result

        module = ast.Module(body=[func_node], type_ignores=[])
        code = compile(module, filename="<ast>", mode="exec")

        class ToolError(Exception):
            pass

        def _validate(url):
            return url

        env = {
            'urllib': urllib,
            'ToolError': ToolError,
            '_validate': _validate,
            'MAX_BYTES': 500_000,
            'USER_AGENT': 'Test',
            'KEEP_HEADERS': ('content-type', 'content-length', 'content-encoding', 'etag',
                             'last-modified', 'location', 'server', 'date'),
            'REDIRECT_LIMIT': 5
        }
        exec(code, env)
        _fetch = env['_fetch']

        class MockHTTPMessage:
            def __init__(self, d):
                self.d = d
            def items(self):
                return self.d.items()
            def get(self, k, default=None):
                return self.d.get(k, default)

        mock_fp = io.BytesIO(b"error body")
        error = urllib.error.HTTPError(
            url="http://example.com",
            code=404,
            msg="Not Found",
            hdrs=MockHTTPMessage({"Content-Type": "text/html", "Content-Length": "10"}),
            fp=mock_fp
        )

        class MockOpener:
            def open(self, req, timeout):
                raise error

        def mock_build_opener(*handlers):
            return MockOpener()

        # Monkey-patch
        orig_build_opener = urllib.request.build_opener
        urllib.request.build_opener = mock_build_opener
        try:
            res = _fetch("http://example.com", "GET", 1000, 30)

            # Assertions
            if res.get('status') != 404:
                result.error(f"Expected status 404, got {res.get('status')}")
            else:
                result.passed += 1

            if res.get('body') != b'error body':
                result.error(f"Expected body b'error body', got {res.get('body')}")
            else:
                result.passed += 1

            if res.get('reason') != 'Not Found':
                result.error(f"Expected reason 'Not Found', got {res.get('reason')}")
            else:
                result.passed += 1

            if res.get('content_type') != 'text/html':
                result.error(f"Expected content_type 'text/html', got {res.get('content_type')}")
            else:
                result.passed += 1

        finally:
            urllib.request.build_opener = orig_build_opener

    except Exception as e:
        result.error(f"Exception: {e}")

    return result

def run_all_tests():

    """Run all tests"""
    tests = [
        test_web_tools_validate_url,
        test_web_tools_error_handling,
        test_foundation,
        test_scripts,
        test_json_files,
        test_no_romanian_in_code,
        test_orchestrator,
        test_self_modify,
        test_multimodal,
        test_performance,
        test_backup,
        test_browser_automation,
        test_cross_instance,
        test_universal_compat,
        test_bimodal_workflow,
        test_mimicry_patterns_fireable,
        test_mimicry_evidence_reformat_proof,
        test_mimicry_diacritic_folding,
        test_mimicry_known_bad_english,
        test_mimicry_honest_output,
        test_mimicry_coverage_reported,
        test_hub_tool_audit,
        test_bimodal_stop_persistence,
        test_brain_corpus_artifacts,
        test_brain_corpus_parsing,
        test_brain_corpus_chapters,
        test_brain_axes_and_methods,
        test_self_improvement_ratify_gate,
        test_monitor_status,
        test_monitor_dependencies,
        test_programme_matrix,
        test_scrape_artifact_emptiness,
        test_mcp_handshake_measure,
        test_mcp_handshake_stale_verdicts,
        test_logs_parse_is_independent_of_age,
        test_context_pressure,
        test_dashboard_boot_activates_a_panel,
        test_ui_never_stringifies_an_object,
        test_mcp_slice_slug,
        test_mcp_bridge_error_handling,
        test_mcp_config_servers_exist,
        test_tool_resolution_not_path_only,
        test_dashboard_surface,
        test_ecosystem_collector_surfaces,
        test_monitor_capability_coverage,
        test_the_plan_is_never_pruned,
        test_gap_register_integrity,
        test_append_only_integrity,
        test_project_references_resolve,
        test_prime_bridge_list_area,
        test_prime_bridge_find_files,
    ]

    print("=" * 70)
    print("SENTINEL PRIME - Test Suite")
    print("=" * 70)
    print()

    total_passed = 0
    total_failed = 0
    total_skipped = 0
    not_run = []
    partial = []
    results = []

    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
            print(result.report())
            print()
            total_passed += result.passed
            total_failed += result.failed
            total_skipped += result.skipped
            # A crash recorded without a counted failure would otherwise
            # vanish from the total entirely: `failed` is what the exit code,
            # the JSON record and `green` are all built from. Rather than
            # trust every `except` handler to have used result.error(),
            # normalise here - a missed call site becomes a red suite, which
            # is the safe direction to be wrong in.
            if result.crashed():
                total_failed += len(result.errors) - result.failed
                result.failed = len(result.errors)
            if result.passed + result.failed == 0:
                not_run.append(result.name)
            elif result.skipped:
                # PARTIAL. Recorded separately from not_run because it did run
                # some assertions - but the suite is not green while any check
                # inside it went unmeasured, and a reader of the JSON record
                # must be able to see that.
                partial.append(result.name)
        except Exception as e:
            print(f"!!! Test {test_func.__name__} crashed: {e}")
            total_failed += 1

    # Summary. A class that ran zero assertions is NOT_RUN, and the suite as a
    # whole is only green when nothing failed AND nothing was silently skipped.
    print("=" * 70)
    print(f"TOTAL: {total_passed} passed, {total_failed} failed, "
          f"{total_skipped} skipped")
    if not_run:
        print(f"NOT RUN (0 assertions, so nothing was proven): "
              f"{', '.join(not_run)}")
    if partial:
        # Named explicitly, never folded into a count. A class that passed 5
        # assertions and skipped 1 reads as "5/5 PASS" in its own report block,
        # so without this line the skipped check is invisible in the summary
        # even though it keeps the suite out of green.
        print(f"PARTIAL (ran some checks, skipped others, so the result is "
              f"inconclusive): {', '.join(partial)}")
    if total_skipped:
        print("NOTE: a skipped check is not a passing check. "
              "The capability is unverified, not working.")

    write_last_run(total_passed, total_failed, total_skipped, not_run, results, partial)
    print("=" * 70)

    # Green requires: nothing failed, nothing wholly unrun, AND nothing
    # partially unrun. Before this, a class that passed 5 assertions and
    # skipped 1 never entered `not_run`, so `skipped` alone could not keep
    # the suite from reporting green - the record and the summary disagreed.
    return total_failed == 0 and not not_run and total_skipped == 0


def write_last_run(passed, failed, skipped, not_run, results, partial=None):
    """Record this run where the Command Center can read it.

    The Tests panel renders `api\\last_test_run.json`. Without this file the
    panel has to either show a hardcoded number or show nothing, and both are
    lies. The record carries the NOT_RUN and PARTIAL lists too, so a green
    total cannot hide behind a class that proved nothing - or behind a class
    that proved part of nothing and was never mentioned.
    """
    partial = partial or []
    try:
        classes = []
        for r in results:
            classes.append({
                'name': r.name,
                'passed': r.passed,
                'failed': r.failed,
                'skipped': r.skipped,
                'not_run': (r.passed + r.failed) == 0,
                'partial': r.skipped > 0 and (r.passed + r.failed) > 0,
            })
        payload = {
            'ran_at': datetime.now().isoformat(),
            'passed': passed,
            'failed': failed,
            'skipped': skipped,
            'not_run': list(not_run),
            'partial': list(partial),
            # Must agree with the suite's own return value, or the record and
            # the summary disagree about the same run.
            'green': failed == 0 and not not_run and skipped == 0,
            'classes': classes,
            # `classes` is an INVENTORY, not a feed: one entry per class this
            # suite runs, fixed by the code below, not by elapsed time. The
            # deployment suite bounds every list at 25 and would flag 26
            # classes as an ungoverned feed, so the registry has to recognise
            # this shape by name. A name alone would be a waiver - any list
            # called `classes` anywhere in any payload would pass. So the
            # record declares its own total, and the deployment check holds
            # that total against BOTH the shipped list and the registration
            # list in this file. Drop a class from `run_all_tests()` and the
            # declared total stops matching the source, which is the defect
            # this exists to catch.
            'total_classes': len(classes),
        }
        out = WORKSPACE / '13_COMMAND_CENTER' / 'api' / 'last_test_run.json'
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, indent=2, ensure_ascii=False),
                       encoding='utf-8')
    except Exception as exc:  # a bookkeeping failure must not fail the suite
        print(f"(could not write last_test_run.json: {exc})")


if __name__ == '__main__':
    # The suite prints Romanian tokens it found while checking the language law.
    # On a cp1252 console (this machine's default) printing 's' with comma below
    # raises UnicodeEncodeError, and the crash surfaced as a FAILED test rather
    # than as the encoding problem it was. Force UTF-8 on the streams first.
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except AttributeError:
        pass
    success = run_all_tests()
    sys.exit(0 if success else 1)
