#!/usr/bin/env python3
"""
Self-Modify Engine for SENTINEL_PRIME
Allows bounded auto-modification with safety checks.
All code/comments/messages in English.
"""
import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List


WORKSPACE = Path(os.environ.get('WORKSPACE_ROOT', 'C:\\Users\\apviz\\.minimax-agent\\projects\\SENTINEL_PRIME'))
LOG_FILE = WORKSPACE / '09_LOGS' / 'self_modifications.log'
BACKUP_DIR = WORKSPACE / '08_SELF_IMPROVEMENT' / 'backups'


ALLOWED_ZONES = [
    str(WORKSPACE / '01_FOUNDATION') + '\\',
    str(WORKSPACE / '02_OPERATIONAL') + '\\',
    str(WORKSPACE / '03_INTELLIGENCE') + '\\',
    str(WORKSPACE / '05_LEARNING') + '\\',
    str(WORKSPACE / '07_BACKBONE') + '\\',
    str(WORKSPACE / '08_SELF_IMPROVEMENT') + '\\',
    str(WORKSPACE / '09_LOGS') + '\\',
    str(WORKSPACE / '10_DOCS') + '\\',
]

FORBIDDEN_ZONES = [
    'C:\\Windows',
    'C:\\Program Files',
    'C:\\Users\\apviz\\.minimax\\',
    'C:\\Users\\apviz\\.claude\\',
    'C:\\Users\\apviz\\AppData\\',
    'E:\\CLAUDE',
    'D:\\',
]

APPROVAL_REQUIRED = [
    'delete',
    'cross-system',
    'new-tool',
    'fundamental-logic',
]


class SelfModifyEngine:
    """Engine for bounded self-modification"""

    def __init__(self):
        self.modification_log: List[Dict] = []
        self.backup_dir = BACKUP_DIR
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def can_modify(self, path: Path) -> bool:
        """Check if path is in allowed zone"""
        try:
            path_str = str(path.resolve()).replace('/', '\\')
        except Exception:
            path_str = str(path).replace('/', '\\')

        # Ensure path ends without trailing separator for startswith check
        path_normalized = path_str.rstrip('\\')

        # Check forbidden zones first (with boundary verification)
        for zone in FORBIDDEN_ZONES:
            zone_normalized = zone.rstrip('\\')
            # Verify boundary: must be exact match or followed by \
            if path_normalized == zone_normalized:
                return False
            if path_normalized.startswith(zone_normalized + '\\'):
                return False

        # Check allowed zones (with boundary verification)
        for zone in ALLOWED_ZONES:
            zone_normalized = zone.rstrip('\\')
            if path_normalized == zone_normalized:
                return True
            if path_normalized.startswith(zone_normalized + '\\'):
                return True

        return False

    def needs_approval(self, operation: str) -> bool:
        """Check if operation requires approval"""
        for keyword in APPROVAL_REQUIRED:
            if keyword in operation.lower():
                return True
        return False

    def backup(self, path: Path) -> Optional[Path]:
        """Create backup before modification"""
        if not path.exists():
            return None

        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f"{path.name}.{timestamp}.bak"
            backup_path = self.backup_dir / backup_name

            shutil.copy2(path, backup_path)
            return backup_path
        except Exception as e:
            print(f"Backup failed: {e}")
            return None

    def rotate_backups(self, max_keep: int = 10):
        """Keep only the last N backups per pattern"""
        if not self.backup_dir.exists():
            return

        # Group by base filename
        backups = {}
        for f in self.backup_dir.glob('*.bak'):
            base = f.name.split('.')[0]
            if base not in backups:
                backups[base] = []
            backups[base].append((f.stat().st_mtime, f))

        # Keep only max_keep most recent per group
        for base, files in backups.items():
            files.sort(reverse=True)
            for _, old_file in files[max_keep:]:
                try:
                    old_file.unlink()
                except Exception:
                    pass

    def modify(
        self,
        path: Path,
        new_content: str,
        reason: str,
        skip_backup: bool = False,
        skip_approval: bool = False
    ) -> Dict:
        """
        Apply modification with safety checks.

        Returns:
        {
            'status': 'OK' | 'FORBIDDEN' | 'NEEDS_APPROVAL' | 'ERROR',
            'backup': str | None,
            'modification_id': int,
            'message': str
        }
        """
        # 1. Safety check
        if not self.can_modify(path):
            return {
                'status': 'FORBIDDEN',
                'backup': None,
                'modification_id': None,
                'message': f'Path {path} not in allowed zone'
            }

        # 2. Approval check
        if not skip_approval and self.needs_approval(reason):
            return {
                'status': 'NEEDS_APPROVAL',
                'backup': None,
                'modification_id': None,
                'message': f'Operation "{reason}" requires Popy approval'
            }

        # 3. Backup
        backup_path = None
        if not skip_backup:
            backup_path = self.backup(path)

        # 4. Apply modification
        old_content = None
        try:
            if path.exists():
                old_content = path.read_text(encoding='utf-8')

            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(new_content, encoding='utf-8')

            # 5. Log modification
            mod_id = len(self.modification_log) + 1
            mod_record = {
                'id': mod_id,
                'timestamp': datetime.now().isoformat(),
                'path': str(path),
                'reason': reason,
                'backup': str(backup_path) if backup_path else None,
                'old_size': len(old_content) if old_content else 0,
                'new_size': len(new_content),
                'status': 'OK'
            }
            self.modification_log.append(mod_record)
            self._persist_log(mod_record)

            # 6. Rotate backups
            self.rotate_backups()

            return {
                'status': 'OK',
                'backup': str(backup_path) if backup_path else None,
                'modification_id': mod_id,
                'message': 'Modification applied successfully'
            }

        except Exception as e:
            # Rollback if needed
            if backup_path and old_content is not None:
                try:
                    path.write_text(old_content, encoding='utf-8')
                    return {
                        'status': 'ROLLED_BACK',
                        'backup': str(backup_path),
                        'modification_id': None,
                        'message': f'Modification failed, rolled back: {e}'
                    }
                except Exception:
                    pass

            return {
                'status': 'ERROR',
                'backup': str(backup_path) if backup_path else None,
                'modification_id': None,
                'message': str(e)
            }

    def _persist_log(self, record: Dict):
        """Write to self-modifications log"""
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

        log_line = f"[{record['timestamp']}] ID:{record['id']} {record['status']} {record['path']} | REASON:{record['reason']} | BACKUP:{record.get('backup', 'N/A')} | SIZE: {record['old_size']}->{record['new_size']}\n"
        log_line += '-' * 80 + '\n'

        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_line)

    def restore_backup(self, backup_path: Path, target: Path) -> Dict:
        """Restore from a backup"""
        if not backup_path.exists():
            return {'status': 'ERROR', 'message': 'Backup not found'}

        if not self.can_modify(target):
            return {'status': 'FORBIDDEN', 'message': 'Target not in allowed zone'}

        try:
            content = backup_path.read_text(encoding='utf-8')
            backup_of_backup = self.backup(target)
            target.write_text(content, encoding='utf-8')

            return {
                'status': 'OK',
                'backup_of_backup': str(backup_of_backup) if backup_of_backup else None,
                'message': f'Restored {target} from {backup_path}'
            }
        except Exception as e:
            return {'status': 'ERROR', 'message': str(e)}

    def get_modification_history(self) -> List[Dict]:
        """Return modification history"""
        return self.modification_log.copy()


def main():
    """Demo: self-modify engine"""
    engine = SelfModifyEngine()

    print("=" * 60)
    print("SENTINEL Self-Modify Engine Demo")
    print("=" * 60)

    # Test 1: Modify in allowed zone
    test_file = WORKSPACE / '08_SELF_IMPROVEMENT' / 'test_pattern.md'
    test_content = "# Test Pattern\n\nThis is a test pattern for self-modification.\n"

    result = engine.modify(
        test_file,
        test_content,
        "Adding test pattern for self-modification demo"
    )
    print(f"\nTest 1 (allowed zone): {result['status']}")
    print(f"Message: {result['message']}")

    # Test 2: Try forbidden zone
    forbidden_file = Path('C:\\Windows\\test.md')
    result = engine.modify(
        forbidden_file,
        "Should fail",
        "Testing forbidden zone"
    )
    print(f"\nTest 2 (forbidden zone): {result['status']}")
    print(f"Message: {result['message']}")

    # Test 3: Try approval-required operation
    important_file = WORKSPACE / '01_FOUNDATION' / 'test_important.md'
    result = engine.modify(
        important_file,
        "Important content",
        "delete operation test"
    )
    print(f"\nTest 3 (approval required): {result['status']}")
    print(f"Message: {result['message']}")

    # Show history
    history = engine.get_modification_history()
    print(f"\nModifications logged: {len(history)}")


if __name__ == '__main__':
    main()
