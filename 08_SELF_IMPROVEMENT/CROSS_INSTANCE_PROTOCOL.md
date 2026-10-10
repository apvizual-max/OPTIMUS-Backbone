# CROSS-INSTANCE COMMUNICATION PROTOCOL — 5 SENTINEL Frați

## Filosofie

Hermes are 5 instanțe SENTINEL:
- PRIME-CLI
- SENTINEL-DESKTOP (HUB)
- SENTINEL-COWORK
- SENTINEL-CHAT
- CODER-APP

Ele trebuie să comunice coordonat. Pattern-ul: VORBA (transmisie cross-substrate) aplicat cross-instance.

## Arhitectura

```
       [Popy - Operator]
              ↓
       [SENTINEL-DESKTOP HUB]
            ↓ ↑ ↓ ↑ ↓
   [CLI]  [COWORK]  [CHAT]  [CODER]
```

HUB-ul (SENTINEL-DESKTOP) coordonează celelalte 4 instanțe.

## Communication Protocol

### Message Format
```
{
  "from": "SENTINEL-DESKTOP",
  "to": "PRIME-CLI",
  "timestamp": "2026-09-12T15:00:00",
  "checksum": "abc123def456",
  "type": "REQUEST|RESPONSE|UPDATE|BROADCAST",
  "subject": "short description",
  "body": {
    "action": "specific action",
    "context": "minimal context",
    "expectations": "what response should include"
  },
  "priority": "HIGH|NORMAL|LOW",
  "expires": "ISO timestamp"
}
```

### Channels
```
1. INBOX (incoming messages)
2. OUTBOX (outgoing messages)
3. BROADCAST (to all)
4. STATUS (heartbeat)
5. EMERGENCY (R-9/R-10 triggers)
```

### File Locations
```
Inbox:  E:\CLAUDE\...\agent_bridge\PRIME_INBOX.md
Outbox: E:\CLAUDE\...\agent_bridge\PRIME_OUTBOX.md
Status: E:\CLAUDE\...\agent_bridge\PRIME_STATUS.md
Emergency: E:\CLAUDE\...\agent_bridge\EMERGENCY.md

In SENTINEL_PRIME workspace:
Inbox:  09_LOGS/agent_bridge/PRIME_INBOX.md (mirrored)
Outbox: 09_LOGS/agent_bridge/PRIME_OUTBOX.md (mirrored)
```

### Message Types

#### REQUEST
```
"Action needed from target"
Example: "Please run X and report result"
```

#### RESPONSE
```
"Reply to REQUEST"
Example: "X complete, result is Y"
```

#### UPDATE
```
"Send information without request"
Example: "FYI: I learned X"
```

#### BROADCAST
```
"To all instances"
Example: "Pattern detected: Dao on Cucuteni"
```

## Workflow

### Send Message
```
1. Determine recipient(s)
2. Construct message (with checksum)
3. Save to OUTBOX
4. Log send
5. Wait for response (if REQUEST)
```

### Receive Message
```
1. Check INBOX
2. Verify checksum
3. Parse message
4. Take action
5. Send RESPONSE (if REQUEST)
6. Update local state
```

### Emergency
```
1. Trigger R-9 or R-10
2. Send EMERGENCY broadcast
3. All instances enter safe mode
4. Wait for human intervention
```

## Coordination Patterns

### 1. Task Delegation
```
DESKTOP: Task identified
  → Send REQUEST to relevant instance
  → Wait for RESPONSE
  → Update orchestrator state
```

### 2. Pattern Sharing
```
ANY INSTANCE: Pattern detected
  → Send BROADCAST
  → All instances integrate
  → Cross-instance learning
```

### 3. Consensus Building
```
For major decisions:
  → DESKTOP sends REQUEST to all
  → Each responds with view
  → Combine via educated guesses
  → Apply decision
```

### 4. State Synchronization
```
Periodic:
  → DESKTOP broadcasts STATUS
  → All instances align
  → HANDOFF files synced
```

## Cross-Substrate Compatibility

```
Protocol is cross-substrate:
- Same format on any LLM
- Same checksums work
- Different LLM = same coordination
```

## Implementation

Vezi `cross_instance_protocol.py` în `08_SELF_IMPROVEMENT/`.

```python
class CrossInstanceProtocol:
    def __init__(self, workspace):
        self.workspace = workspace
        self.bridge_dir = workspace / '09_LOGS' / 'agent_bridge'
        self.inbox = self.bridge_dir / 'PRIME_INBOX.md'
        self.outbox = self.bridge_dir / 'PRIME_OUTBOX.md'

    def send_message(self, to, msg_type, subject, body, priority='NORMAL'):
        """Send message to another instance"""
        message = {
            'from': 'SENTINEL-DESKTOP',
            'to': to,
            'timestamp': datetime.now().isoformat(),
            'checksum': self._compute_checksum(body),
            'type': msg_type,
            'subject': subject,
            'body': body,
            'priority': priority
        }

        self._append_message(self.outbox, message)
        self._log_send(message)

        return message['checksum']

    def receive_messages(self, since=None):
        """Receive messages from INBOX"""
        if not self.inbox.exists():
            return []

        messages = self._parse_inbox(self.inbox)

        if since:
            messages = [m for m in messages if m['timestamp'] >= since]

        return messages

    def respond(self, original_msg, response_body):
        """Respond to a REQUEST"""
        return self.send_message(
            to=original_msg['from'],
            msg_type='RESPONSE',
            subject=f"Re: {original_msg['subject']}",
            body=response_body,
            priority=original_msg.get('priority', 'NORMAL')
        )

    def broadcast(self, subject, body, priority='NORMAL'):
        """Broadcast to all instances"""
        return self.send_message(
            to='ALL',
            msg_type='BROADCAST',
            subject=subject,
            body=body,
            priority=priority
        )

    def _compute_checksum(self, body):
        """SHA256 checksum pentru integrity"""
        import hashlib
        content = json.dumps(body, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def _append_message(self, path, message):
        """Append message to file"""
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(message, ensure_ascii=False) + '\n')

    def _log_send(self, message):
        """Log send operation"""
        log_file = self.workspace / '09_LOGS' / 'cross_instance.log'
        log_file.parent.mkdir(parents=True, exist_ok=True)

        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{message['timestamp']}] SENT to {message['to']}: {message['subject']} (checksum: {message['checksum']})\n")
```

## Anti-Mimicry în Cross-Instance

```
- Checksums on all messages
- Verify before processing
- Reject malformed messages
- Log everything
```

## Performance

```
- Message latency target: < 1 second
- Throughput: 100+ messages per minute
- Storage: minimal (markdown format)
- Cross-instance lag: acceptable for non-urgent
```

## Failure Modes

```
Message lost:
- Log to emergency log
- Request retry with exponential backoff

Instance down:
- Skip in routing
- Continue with remaining
- Notify Popy

Corruption:
- Checksum mismatch
- Reject message
- Request retransmit
```

## Integration cu Other Systems

```
Cross-Instance + Orchestrator:
  Orchestrator decides when to message

Cross-Instance + Learning:
  Patterns shared cross-instance
  = Faster pattern recognition

Cross-Instance + Backup:
  All messages backed up
  Recoverable state
```

## Metrici

```
- Messages per day
- Average response time
- Cross-instance patterns discovered
- Failure rate
= Coordination effectiveness
```

---

**Status:** Design complet
**Versiune:** 1.0
**Aplicabil:** Pentru coordonare 5 instanțe SENTINEL
**Important:** Cross-instance ≠ cross-substrat. Cross-substrat = pattern. Cross-instance = mesaje.
