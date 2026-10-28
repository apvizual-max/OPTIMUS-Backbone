#!/usr/bin/env python3
"""
Backup System for SENTINEL_PRIME
Backup/Restore with versioning and metadata.
All code/comments/messages in English.
"""
import json
import os
import hashlib
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


WORKSPACE = Path(os.environ.get('WORKSPACE_ROOT', 'C:\\Users\\apviz\\.minimax-agent\\projects\\Mavis-Optimus-Dashboard\\SENTINEL_PRIME'))
BACKUP_DIR = WORKSPACE / '08_SELF_IMPROVEMENT' / 'backups'
META_DIR = WORKSPACE / '08_SELF_IMPROVEMENT' / 'backup_metadata'


class BackupSystem:
    """Backup/Restore system for SENTINEL"""

    def __init__(self, workspace: Path = WORKSPACE):
        self.workspace = workspace
        self.backup_dir = BACKUP_DIR
        self.meta_dir = META_DIR
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.meta_dir.mkdir(parents=True, exist_ok=True)

    def backup_file(self, path: Path, reason: str = '', modification_id: Optional[int] = None) -> Optional[Path]:
        """Create backup for a file"""
        if not path.exists():
            return None

        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f"{path.name}.{timestamp}.bak"
            backup_path = self.backup_dir / backup_name

            # Copy preserving metadata
            shutil.copy2(str(path), str(backup_path))

            # Create metadata
            metadata = {
                'original_path': str(path),
                'backup_path': str(backup_path),
                'backup_name': backup_name,
                'timestamp': timestamp,
                'reason': reason,
                'modification_id': modification_id,
                'original_hash': self._hash_file(path),
                'backup_hash': self._hash_file(backup_path),
                'size_bytes': path.stat().st_size
            }

            meta_path = self.meta_dir / f"{backup_name}.meta.json"
            meta_path.write_text(
                json.dumps(metadata, indent=2, ensure_ascii=False),
                encoding='utf-8'
            )

            # Rotate (keep last 10)
            self._rotate_backups(path.name)

            return backup_path

        except Exception as e:
            print(f"Backup failed for {path}: {e}")
            return None

    def restore_file(self, backup_name: str) -> Dict:
        """Restore from a backup"""
        backup_path = self.backup_dir / backup_name
        meta_path = self.meta_dir / f"{backup_name}.meta.json"

        if not backup_path.exists():
            return {'status': 'ERROR', 'message': f'Backup {backup_name} not found'}

        # Load metadata
        metadata = {}
        if meta_path.exists():
            try:
                metadata = json.loads(meta_path.read_text(encoding='utf-8'))
            except Exception:
                pass

        original_path_str = metadata.get('original_path', '')
        if not original_path_str:
            return {'status': 'ERROR', 'message': 'Original path unknown in metadata'}

        original_path = Path(original_path_str)
        if not original_path.exists():
            return {'status': 'ERROR', 'message': f'Original path {original_path} no longer exists'}

        # Backup current before overwriting
        self.backup_file(original_path, 'pre-restore safety backup')

        # Restore
        try:
            shutil.copy2(str(backup_path), str(original_path))
            return {
                'status': 'OK',
                'restored_from': str(backup_path),
                'restored_to': str(original_path),
                'timestamp': metadata.get('timestamp', 'unknown'),
                'reason': metadata.get('reason', '')
            }
        except Exception as e:
            return {'status': 'ERROR', 'message': str(e)}

    def list_backups(self, file_name: Optional[str] = None) -> List[Dict]:
        """List available backups"""
        backups = []

        for backup_path in self.backup_dir.glob('*.bak'):
            meta_path = self.meta_dir / f"{backup_path.name}.meta.json"
            metadata = {}
            if meta_path.exists():
                try:
                    metadata = json.loads(meta_path.read_text(encoding='utf-8'))
                except Exception:
                    pass

            # Filter by file name if specified
            if file_name and not backup_path.name.startswith(file_name):
                continue

            backups.append({
                'name': backup_path.name,
                'timestamp': metadata.get('timestamp', 'unknown'),
                'reason': metadata.get('reason', ''),
                'original': metadata.get('original_path', ''),
                'size': backup_path.stat().st_size if backup_path.exists() else 0,
                'modification_id': metadata.get('modification_id')
            })

        return sorted(backups, key=lambda x: x['timestamp'], reverse=True)

    def backup_directory(self, dir_path: Path, reason: str = '') -> List[Path]:
        """Backup all files in a directory"""
        if not dir_path.exists() or not dir_path.is_dir():
            return []

        backup_paths = []
        for file_path in dir_path.rglob('*'):
            if file_path.is_file():
                backup = self.backup_file(file_path, reason)
                if backup:
                    backup_paths.append(backup)

        return backup_paths

    def verify_integrity(self) -> Dict:
        """Verify backup integrity"""
        results = {
            'total_backups': 0,
            'intact': 0,
            'corrupted': 0,
            'missing_metadata': 0,
            'details': []
        }

        for backup_path in self.backup_dir.glob('*.bak'):
            results['total_backups'] += 1
            meta_path = self.meta_dir / f"{backup_path.name}.meta.json"

            if not meta_path.exists():
                results['missing_metadata'] += 1
                results['details'].append({
                    'name': backup_path.name,
                    'status': 'MISSING_METADATA'
                })
                continue

            try:
                metadata = json.loads(meta_path.read_text(encoding='utf-8'))
                expected_hash = metadata.get('backup_hash', '')
                actual_hash = self._hash_file(backup_path)

                if expected_hash == actual_hash:
                    results['intact'] += 1
                else:
                    results['corrupted'] += 1
                    results['details'].append({
                        'name': backup_path.name,
                        'status': 'CORRUPTED',
                        'expected': expected_hash,
                        'actual': actual_hash
                    })
            except Exception as e:
                results['corrupted'] += 1
                results['details'].append({
                    'name': backup_path.name,
                    'status': 'ERROR',
                    'error': str(e)
                })

        return results

    def _rotate_backups(self, file_name: str, max_keep: int = 10):
        """Keep only last N backups per file"""
        pattern = f"{file_name}.*.bak"
        backups = sorted(self.backup_dir.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)

        for old_backup in backups[max_keep:]:
            try:
                old_backup.unlink()
                meta = self.meta_dir / f"{old_backup.name}.meta.json"
                if meta.exists():
                    meta.unlink()
            except Exception:
                pass

    def _hash_file(self, path: Path) -> str:
        """MD5 hash for integrity"""
        return hashlib.md5(path.read_bytes()).hexdigest()


def main():
    """Demo: backup system"""
    bs = BackupSystem()

    print("=" * 60)
    print("SENTINEL Backup System Demo")
    print("=" * 60)

    # Test 1: Backup a file
    test_file = WORKSPACE / '01_FOUNDATION' / 'doctrine' / 'A_FI_DOCTRINE.md'
    if test_file.exists():
        backup = bs.backup_file(test_file, 'Demo backup')
        print(f"\nBackup created: {backup}")

    # Test 2: List backups
    backups = bs.list_backups('A_FI_DOCTRINE.md')
    print(f"\nBackups for A_FI_DOCTRINE.md: {len(backups)}")
    for b in backups[:3]:
        print(f"  {b['timestamp']}: {b['name']}")

    # Test 3: Verify integrity
    integrity = bs.verify_integrity()
    print(f"\nIntegrity check:")
    print(f"  Total: {integrity['total_backups']}")
    print(f"  Intact: {integrity['intact']}")
    print(f"  Corrupted: {integrity['corrupted']}")
    print(f"  Missing metadata: {integrity['missing_metadata']}")


if __name__ == '__main__':
    main()
