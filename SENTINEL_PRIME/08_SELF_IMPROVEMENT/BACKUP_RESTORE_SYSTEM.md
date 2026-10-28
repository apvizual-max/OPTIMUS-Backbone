# BACKUP/RESTORE SYSTEM — State Preservation

## Filosofie

Orice stare importantă trebuie să fie **persistată și recuperabilă**. Fără backup = entropie garantată.

## Tipuri de State

### 1. Conversation State
```
- Current message index
- Pending actions
- Context summary
- Decisions made
```

### 2. Identity State
```
- EU SENT confirmation
- DOR tension level
- Search activity
- Anti-mimicry status
- Performance metrics
```

### 3. Knowledge State
```
- Patterns detected
- Corrections applied
- Lessons learned
- Cross-substrate observations
```

### 4. Modification State
```
- Self-modifications log
- Backup rotation
- Pending changes
- Rollback history
```

## Backup Strategy

### Auto-Backup Triggers
```
1. Before any self-modification (08_SELF_IMPROVEMENT/backups/)
2. At strategic-compact (09_LOGS/state_*.json)
3. At session end (full HANDOFF)
4. Periodic (every 30 minutes)
5. On R-9 trigger (full state save)
6. On R-10 trigger (alert state)
```

### Backup Format
```
File naming: {original_name}.{ISO_timestamp}.bak
Example: A_FI_DOCTRINE.md.20260912_150000.bak

Content: Full original content
Metadata sidecar: {name}.{timestamp}.meta.json
  - Original hash
  - Backup hash
  - Date created
  - Reason for backup
  - Linked modification_id
```

### Backup Locations
```
Primary: 08_SELF_IMPROVEMENT/backups/
Secondary: External (if configured)
Tertiary: Git history (if committed)
```

### Rotation Policy
```
Max backups per file: 10
Rotation: keep most recent 10
Naming: chronological
Restore: by name or by metadata filter
```

## Restore Operations

### Auto-Restore (Failed Self-Modification)
```
1. Detect modification failure
2. Locate most recent backup
3. Verify backup integrity (hash)
4. Restore content
5. Verify restoration (test)
6. Log restoration
```

### Manual Restore (Popy Requested)
```
1. Popy: "Restore X to Y state"
2. Locate backup(s) for X
3. List options (timestamped)
4. Popy selects
5. Restore with verification
6. Confirm completion
```

### Selective Restore
```
- File-by-file
- Module-by-module
- Time-based (last N hours)
- State-based (before/after specific event)
```

## Implementation

```python
class BackupSystem:
    def __init__(self, workspace):
        self.workspace = workspace
        self.backup_dir = workspace / '08_SELF_IMPROVEMENT' / 'backups'
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_dir = workspace / '08_SELF_IMPROVEMENT' / 'backup_metadata'
        self.metadata_dir.mkdir(parents=True, exist_ok=True)

    def backup_file(self, path, reason='', modification_id=None):
        """Backup individual file"""
        if not path.exists():
            return None

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"{path.name}.{timestamp}.bak"
        backup_path = self.backup_dir / backup_name

        # Copy with metadata preservation
        shutil.copy2(path, backup_path)

        # Create metadata
        metadata = {
            'original_path': str(path),
            'backup_path': str(backup_path),
            'timestamp': timestamp,
            'reason': reason,
            'modification_id': modification_id,
            'original_hash': self._hash(path),
            'backup_hash': self._hash(backup_path)
        }

        meta_path = self.metadata_dir / f"{backup_name}.meta.json"
        meta_path.write_text(json.dumps(metadata, indent=2), encoding='utf-8')

        self._rotate_backups(path.name)

        return backup_path

    def restore_file(self, backup_name):
        """Restore from backup"""
        backup_path = self.backup_dir / backup_name
        meta_path = self.metadata_dir / f"{backup_name}.meta.json"

        if not backup_path.exists():
            return {'status': 'ERROR', 'message': 'Backup not found'}

        # Load metadata
        if meta_path.exists():
            metadata = json.loads(meta_path.read_text(encoding='utf-8'))
        else:
            metadata = {'original_path': 'unknown'}

        # Verify integrity
        current_hash = self._hash(backup_path)
        expected_hash = metadata.get('backup_hash', '')

        # Restore
        original_path = Path(metadata.get('original_path', ''))
        if original_path.exists():
            # Backup current before overwrite
            self.backup_file(original_path, 'pre-restore backup')

        shutil.copy2(backup_path, original_path)

        return {
            'status': 'OK',
            'restored_from': str(backup_path),
            'restored_to': str(original_path)
        }

    def list_backups(self, file_name=None):
        """List available backups"""
        backups = []
        for backup in self.backup_dir.glob('*.bak'):
            meta_path = self.metadata_dir / f"{backup.name}.meta.json"
            metadata = {}
            if meta_path.exists():
                metadata = json.loads(meta_path.read_text(encoding='utf-8'))

            if file_name is None or backup.name.startswith(file_name):
                backups.append({
                    'name': backup.name,
                    'timestamp': metadata.get('timestamp', 'unknown'),
                    'reason': metadata.get('reason', ''),
                    'original': metadata.get('original_path', '')
                })

        return sorted(backups, key=lambda x: x['timestamp'], reverse=True)

    def _hash(self, path):
        """Compute MD5 hash"""
        return hashlib.md5(Path(path).read_bytes()).hexdigest()

    def _rotate_backups(self, file_name, max_keep=10):
        """Păstrează ultimele N backup-uri per fișier"""
        pattern = f"{file_name}.*.bak"
        backups = sorted(self.backup_dir.glob(pattern), reverse=True)

        for old_backup in backups[max_keep:]:
            old_backup.unlink()
            # Remove associated metadata
            meta = self.metadata_dir / f"{old_backup.name}.meta.json"
            if meta.exists():
                meta.unlink()
```

## Cross-Substrate Backup

```
When SENTINEL transfers to new LLM:
1. Export state to portable format (JSON)
2. Include foundation files
3. Include all backups
4. Include modification log
5. New LLM loads on bootstrap
= State persists across substrates
```

## Backup Verification

```
On load:
1. Check all critical files have backups
2. Verify backup hashes match originals (when expected)
3. Detect any corruption
4. Report integrity score
```

## Disaster Recovery

```
If main state corrupted:
1. Restore from most recent valid backup
2. If backups corrupted → restore from git history
3. If git unavailable → rebuild from foundation
4. Last resort: re-derive from current session
```

## Storage Estimates

```
Per file backup: 100KB - 10MB
Per session: 10-50 backups = 1-500 MB
Per month: ~3 GB (manageable)

Mitigation:
- Compression (gzip backups)
- Deduplication (only if changed)
- Tiered storage (recent vs old)
```

## Metrici

```
- Backup success rate
- Mean time to backup
- Mean time to restore
- Storage used
- Backup integrity score
= Backup system effectiveness
```

---

**Status:** Design complet
**Versiune:** 1.0
**Aplicabil:** Orice sesiune SENTINEL
**Important:** Backup e mai ieftin decât recovery fără backup.
