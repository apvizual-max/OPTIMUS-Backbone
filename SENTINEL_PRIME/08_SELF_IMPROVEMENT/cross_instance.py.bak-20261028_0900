#!/usr/bin/env python3
"""
Cross-Instance Communication Protocol for SENTINEL_PRIME
Real implementation: 5 SENTINEL brothers share state via file-based mailbox + heartbeat.
All code/comments/messages in English.
"""
import json
import os
import socket
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


WORKSPACE = Path(os.environ.get('WORKSPACE_ROOT', 'C:\\Users\\apviz\\.minimax-agent\\projects\\SENTINEL_PRIME'))
SHARED_DIR = WORKSPACE / '09_LOGS' / 'cross_instance'
MAILBOX_DIR = SHARED_DIR / 'mailbox'
HEARTBEATS_DIR = SHARED_DIR / 'heartbeats'
REGISTRY_FILE = SHARED_DIR / 'instance_registry.json'

INSTANCES = ['PRIME-CLI', 'SENTINEL-DESKTOP', 'SENTINEL-COWORK', 'SENTINEL-CHAT', 'CODER-APP']


class CrossInstance:
    """Cross-instance communication for SENTINEL family.

    `root` relocates the entire shared-state tree. It exists because the module
    globals are resolved at IMPORT time from WORKSPACE_ROOT, so a test that only
    sets the environment before import still writes into whichever workspace the
    process inherited. That is how the suite came to overwrite the live
    PRIME-CLI heartbeat, making the control plane report a brother instance as
    ACTIVE when no such instance was running.

    Passing `root` explicitly binds the paths for THIS object only. It leaves the
    module globals - and therefore every other instance in the process - alone.

    Constructing the object does NOT register this instance. Registration is the
    act of announcing that you are running, so only `heartbeat()` performs it.
    It used to happen here, which meant every read-only caller - including the
    `sentinel_cross_instance_active` tool - rewrote the registry with a fresh
    `registered_at`, `last_seen` and `status: ACTIVE`. Looking at the registry was
    itself the thing that made the registry claim somebody was present.
    """

    def __init__(self, instance_id: str = 'PRIME-CLI', root: Optional[Path] = None):
        self.instance_id = instance_id
        if root is None:
            self.shared_dir = SHARED_DIR
        else:
            self.shared_dir = Path(root) / '09_LOGS' / 'cross_instance'
        self.mailbox_dir = self.shared_dir / 'mailbox'
        self.heartbeats_dir = self.shared_dir / 'heartbeats'
        self.registry_file = self.shared_dir / 'instance_registry.json'

        self.shared_dir.mkdir(parents=True, exist_ok=True)
        self.mailbox_dir.mkdir(parents=True, exist_ok=True)
        self.heartbeats_dir.mkdir(parents=True, exist_ok=True)

    def _register(self):
        """Register this instance in the registry"""
        registry = {}
        if self.registry_file.exists():
            try:
                registry = json.loads(self.registry_file.read_text(encoding='utf-8'))
            except Exception:
                pass

        registry[self.instance_id] = {
            'instance_id': self.instance_id,
            'registered_at': datetime.now().isoformat(),
            'last_seen': datetime.now().isoformat(),
            'status': 'ACTIVE'
        }

        self.registry_file.write_text(
            json.dumps(registry, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )

    def send_message(self, to_instance: str, message_type: str, payload: Dict) -> Dict:
        """
        Send a message to another instance.
        message_type: 'state_share', 'request', 'response', 'alert', 'pattern'
        Returns message delivery confirmation.
        """
        message_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().isoformat()

        message = {
            'message_id': message_id,
            'from': self.instance_id,
            'to': to_instance,
            'type': message_type,
            'timestamp': timestamp,
            'payload': payload,
            'read': False
        }

        # Route to recipient's mailbox
        recipient_mailbox = self.mailbox_dir / to_instance
        recipient_mailbox.mkdir(parents=True, exist_ok=True)

        message_file = recipient_mailbox / f"{message_id}_{timestamp.replace(':', '-')}.json"
        message_file.write_text(
            json.dumps(message, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )

        return {
            'status': 'SENT',
            'message_id': message_id,
            'to': to_instance,
            'message_file': str(message_file)
        }

    def broadcast(self, message_type: str, payload: Dict) -> List[Dict]:
        """Broadcast message to all other instances"""
        results = []
        for instance in INSTANCES:
            if instance != self.instance_id:
                result = self.send_message(instance, message_type, payload)
                results.append(result)
        return results

    def read_messages(self, unread_only: bool = True, limit: int = 50) -> List[Dict]:
        """Read messages from this instance's mailbox"""
        my_mailbox = self.mailbox_dir / self.instance_id
        if not my_mailbox.exists():
            return []

        messages = []
        for msg_file in sorted(my_mailbox.glob('*.json'), reverse=True)[:limit]:
            try:
                msg = json.loads(msg_file.read_text(encoding='utf-8'))
                if unread_only and msg.get('read', False):
                    continue
                messages.append(msg)
            except Exception:
                continue

        return messages

    def mark_message_read(self, message_id: str) -> bool:
        """Mark a message as read"""
        my_mailbox = self.mailbox_dir / self.instance_id
        if not my_mailbox.exists():
            return False

        for msg_file in my_mailbox.glob(f'{message_id}_*.json'):
            try:
                msg = json.loads(msg_file.read_text(encoding='utf-8'))
                msg['read'] = True
                msg['read_at'] = datetime.now().isoformat()
                msg_file.write_text(
                    json.dumps(msg, indent=2, ensure_ascii=False),
                    encoding='utf-8'
                )
                return True
            except Exception:
                return False
        return False

    def heartbeat(self, status: str = 'ACTIVE', extra: Optional[Dict] = None) -> Dict:
        """Send heartbeat to shared heartbeat file"""
        heartbeat_data = {
            'instance_id': self.instance_id,
            'status': status,
            'timestamp': datetime.now().isoformat(),
            'extra': extra or {}
        }

        heartbeat_file = self.heartbeats_dir / f"{self.instance_id}.json"
        heartbeat_file.write_text(
            json.dumps(heartbeat_data, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )

        # Update registry
        self._register()

        return heartbeat_data

    def get_active_instances(self, include_stale: bool = True) -> List[Dict]:
        """List instances with their heartbeat age and DERIVED liveness.

        The stored `status` field is whatever the writer wrote when it last ran.
        It is not evidence: a file written once says "ACTIVE" forever. So the
        reported status is recomputed here from the age, and the stored claim is
        preserved under `reported_status` rather than discarded, so a reader can
        see that the file disagreed with the clock.

        `include_stale=False` returns only instances inside the 300s window, which
        is what a caller that really wants "who is alive" should pass.
        """
        HEARTBEAT_ALIVE_SECONDS = 300
        active = []
        for hb_file in self.heartbeats_dir.glob('*.json'):
            try:
                hb = json.loads(hb_file.read_text(encoding='utf-8'))
                age_seconds = (datetime.now() - datetime.fromisoformat(hb['timestamp'])).total_seconds()
                is_alive = age_seconds < HEARTBEAT_ALIVE_SECONDS
                # Keep the writer's claim, but never present it as current truth.
                hb['reported_status'] = hb.get('status')
                hb['status'] = 'ACTIVE' if is_alive else 'STALE'
                hb['age_seconds'] = age_seconds
                hb['is_alive'] = is_alive
                if is_alive or include_stale:
                    active.append(hb)
            except Exception:
                continue

        return sorted(active, key=lambda x: x['instance_id'])

    def share_state(self, state_dict: Dict) -> Dict:
        """Share current orchestrator state with all other instances"""
        return self.broadcast('state_share', {
            'state': state_dict,
            'source': self.instance_id
        })

    def request_patterns(self, topic: str) -> Dict:
        """Request pattern data from other instances"""
        return self.send_message('SENTINEL-DESKTOP', 'request', {
            'request_type': 'patterns',
            'topic': topic
        })

    def alert_all(self, alert_type: str, message: str) -> List[Dict]:
        """Send alert to all other instances"""
        return self.broadcast('alert', {
            'alert_type': alert_type,
            'message': message,
            'severity': 'HIGH'
        })

    def get_inbox_stats(self) -> Dict:
        """Get mailbox statistics"""
        my_mailbox = self.mailbox_dir / self.instance_id
        if not my_mailbox.exists():
            return {'total': 0, 'unread': 0, 'read': 0}

        total = 0
        unread = 0
        for msg_file in my_mailbox.glob('*.json'):
            total += 1
            try:
                msg = json.loads(msg_file.read_text(encoding='utf-8'))
                if not msg.get('read', False):
                    unread += 1
            except Exception:
                pass

        return {
            'total': total,
            'unread': unread,
            'read': total - unread,
            'instance_id': self.instance_id
        }


def main():
    """Demo: cross-instance communication"""
    print("=" * 60)
    print("SENTINEL Cross-Instance Communication Demo")
    print("=" * 60)

    # Initialize as PRIME-CLI
    ci = CrossInstance(instance_id='PRIME-CLI')

    # 1. Send heartbeat
    hb = ci.heartbeat('ACTIVE', {'session': 'test', 'eu_sent': True})
    print(f"\n1. Heartbeat sent: {hb['instance_id']} - {hb['status']}")

    # 2. Send message to SENTINEL-DESKTOP
    result = ci.send_message('SENTINEL-DESKTOP', 'state_share', {
        'current_state': 'WAITING_FOR_INPUT',
        'eu_sent': True,
        'counter': 42
    })
    print(f"\n2. Message sent: ID={result['message_id']}")

    # 3. Broadcast alert
    alerts = ci.alert_all('pattern_detected', 'Cucuteni-Trypillia pattern matched')
    print(f"\n3. Alert broadcast to {len(alerts)} instances")

    # 4. Get active instances
    active = ci.get_active_instances()
    print(f"\n4. Active instances: {len(active)}")
    for inst in active[:3]:
        print(f"  {inst['instance_id']}: {inst['status']} ({inst['age_seconds']:.0f}s ago)")

    # 5. Get inbox stats
    stats = ci.get_inbox_stats()
    print(f"\n5. Inbox: {stats['total']} total, {stats['unread']} unread")

    print("\n" + "=" * 60)
    print("Cross-instance demo complete")
    print("=" * 60)


if __name__ == '__main__':
    main()
