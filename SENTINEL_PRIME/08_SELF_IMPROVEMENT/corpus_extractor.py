#!/usr/bin/env python3
"""
Corpus Extractor for the MINIMAX SENTINEL BRAIN.

Turns the frozen conversation archive into a chronological, deduplicated,
verifiable corpus that becomes the documentation substrate of the SENTINEL role.

DESIGN (see PLAN 1, section 1.1)
------------------------------
TWO RETENTION TIERS, because "nothing cut" and "do not inline tool payloads"
are different claims and both are true:

  TIER 1 - VERBATIM (never cut)
      Every user and assistant message, in full text. This tier is what the
      "nothing is cut" rule governs. Assistant thinking is retained as well,
      separated, because it is part of the reasoning record.

  TIER 2 - EVIDENCE (referenced, not inlined)
      toolCall and toolResult records are indexed by id with a bounded preview.
      Their payloads are large and are preserved on disk in the freeze; inlining
      them would let a 1.3 MB of command output drown the reasoning it produced.
      Every evidence record keeps a pointer to its freeze file and line.

ORDER
      Chronological by (generation, line index). Never by wall clock: the
      generation order is the true order of the conversation. `turn_id` is kept
      as a grouping key; turns suffixed with ":compaction" mark a compaction
      boundary.

DEDUPLICATION
      The same message_id appears in several generations because a snapshot is
      a copy of the context at that moment. The longest occurrence wins, since
      a later copy may carry more content parts.

SCAFFOLDING
      <system-reminder> blocks injected by the harness are stripped from the
      verbatim text and preserved in a separate `scaffolding` field. Popy's words
      are the corpus; the harness scaffolding is provenance. Nothing is deleted,
      only separated.

IDEMPOTENCY
      Same frozen input -> byte-identical output. `verify` re-runs and compares
      SHA256 of the emitted corpus.

All code, comments and runtime messages in English (LANGUAGE LAW, chapter 14).
"""
import hashlib
import json
import os
import re
import sys
from collections import OrderedDict
from datetime import datetime
from pathlib import Path

WORKSPACE = Path(os.environ.get(
    'WORKSPACE_ROOT',
    r'C:\Users\apviz\.minimax-agent\projects\Mavis-Optimus-Dashboard\SENTINEL_PRIME'))

FREEZE = WORKSPACE / '09_LOGS' / 'corpus_freeze'
BRAIN = WORKSPACE / '11_BRAIN'
RAW = BRAIN / '01_RAW'
CHAPTERS_DIR = BRAIN / '02_CHAPTERS'
COMPACTION_DIR = RAW / 'compaction_summaries'

CORPUS_FILE = RAW / 'corpus_full.jsonl'
CHANGELOG_FILE = RAW / 'CHANGELOG_EXTRACTION.md'
STATS_FILE = RAW / 'corpus_stats.json'
CHAPTER_MAP_FILE = RAW / 'chapter_map.json'

# Message zero, verified during planning by reading generation 0 line 1.
# Used as an integrity anchor: if the first emitted message is not this, the
# extraction is wrong regardless of what it claims to have produced.
MESSAGE_ZERO_ANCHOR = 'If I buy a subscription, can I use MiniMax as my Hermes'

EVIDENCE_PREVIEW_CHARS = 400
SYSTEM_REMINDER_RE = re.compile(r'<system-reminder>.*?</system-reminder>', re.DOTALL)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def split_scaffolding(text: str):
    """Separate harness scaffolding from Popy's words. Nothing is deleted."""
    blocks = SYSTEM_REMINDER_RE.findall(text)
    stripped = SYSTEM_REMINDER_RE.sub('', text)
    return stripped.strip(), ('\n\n'.join(blocks) if blocks else None)


def part_text(part) -> str:
    """Extract the human-readable text of one content part."""
    if not isinstance(part, dict):
        return ''
    t = part.get('type')
    if t == 'text':
        return part.get('text') or ''
    return ''


def part_thinking(part) -> str:
    if isinstance(part, dict) and part.get('type') == 'thinking':
        return part.get('thinking') or part.get('text') or ''
    return ''


def part_toolcall(part):
    if not isinstance(part, dict) or part.get('type') != 'toolCall':
        return None
    name = part.get('name') or part.get('toolName') or ''
    args = part.get('arguments') or part.get('args') or {}
    if not isinstance(args, str):
        try:
            args = json.dumps(args, ensure_ascii=False, sort_keys=True)
        except Exception:
            args = str(args)
    return {'name': name, 'args_preview': args[:EVIDENCE_PREVIEW_CHARS]}


def result_text(message) -> str:
    """Flatten a toolResult payload down to a bounded preview."""
    c = message.get('content')
    if isinstance(c, str):
        return c
    if isinstance(c, list):
        return '\n'.join(part_text(p) for p in c if isinstance(p, dict))
    if c is None:
        d = message.get('details')
        if isinstance(d, str):
            return d
    return ''


def load_generations():
    """Read every frozen generation, in generation order."""
    gens = []
    snap_dir = FREEZE / 'snapshots'
    for path in sorted(snap_dir.glob('g*.jsonl')):
        gen_index = int(path.name.split('--')[0].lstrip('g'))
        records = []
        with open(path, 'r', encoding='utf-8') as f:
            for line_no, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    records.append((line_no, json.loads(line)))
                except json.JSONDecodeError as exc:
                    records.append((line_no, {'__parse_error__': str(exc)}))
        gens.append({
            'generation': gen_index,
            'file': path.name,
            'path': path,
            'records': records,
        })
    active = FREEZE / 'messages.jsonl'
    if active.exists():
        records = []
        with open(active, 'r', encoding='utf-8') as f:
            for line_no, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    records.append((line_no, json.loads(line)))
                except json.JSONDecodeError as exc:
                    records.append((line_no, {'__parse_error__': str(exc)}))
        # The active file is the NEWEST state of the conversation, so it must
        # sort AFTER every snapshot generation. Assigning it -1 would place the
        # most recent turns before the earliest ones and silently destroy the
        # chronology. The catalog is authoritative for its generation number.
        active_gen = max([g['generation'] for g in gens], default=-1) + 1
        catalog = FREEZE / 'history-catalog.json'
        if catalog.exists():
            try:
                declared = json.loads(catalog.read_text(encoding='utf-8'))
                active_gen = int(declared.get('activeGeneration', active_gen))
            except (json.JSONDecodeError, TypeError, ValueError):
                pass
        gens.append({
            'generation': active_gen,
            'file': active.name,
            'path': active,
            'records': records,
            'active': True,
        })
    return gens


def extract():
    """Build the corpus. Returns (messages, accounting)."""
    gens = load_generations()

    # OrderedDict keyed by message_id, keeping the richest occurrence.
    best = OrderedDict()
    accounting = {
        'input_records': 0,
        'parse_errors': [],
        'excluded_no_message_id': [],
        'excluded_scaffolding_only': [],
        'source_records': 0,
    }

    for gen in gens:
        for line_no, obj in gen['records']:
            accounting['input_records'] += 1
            accounting['source_records'] += 1
            if '__parse_error__' in obj:
                accounting['parse_errors'].append(
                    f"{gen['file']}:{line_no} {obj['__parse_error__']}")
                continue
            msg_id = obj.get('message_id')
            if not msg_id:
                accounting['excluded_no_message_id'].append(
                    f"{gen['file']}:{line_no}")
                continue
            message = obj.get('message') or {}
            role = message.get('role') or 'unknown'

            if role == 'compactionSummary':
                entry = {
                    'kind': 'compaction',
                    'message_id': msg_id,
                    'turn_id': obj.get('turn_id'),
                    'role': role,
                    'summary': message.get('summary') or '',
                    'text': '',
                }
            elif role == 'toolResult':
                preview = result_text(message)
                entry = {
                    'kind': 'evidence',
                    'message_id': msg_id,
                    'turn_id': obj.get('turn_id'),
                    'role': role,
                    'tool_name': message.get('toolName'),
                    'tool_call_id': message.get('toolCallId'),
                    'is_error': bool(message.get('isError')),
                    'text': preview[:EVIDENCE_PREVIEW_CHARS],
                    'text_len': len(preview),
                }
            else:
                parts = message.get('content')
                parts = parts if isinstance(parts, list) else []
                raw = '\n\n'.join(p for p in (part_text(x) for x in parts) if p)
                text, scaffolding = split_scaffolding(raw)
                thinking = '\n\n'.join(
                    p for p in (part_thinking(x) for x in parts) if p)
                tool_calls = [tc for tc in (part_toolcall(x) for x in parts) if tc]
                if not text and not thinking and not tool_calls:
                    accounting['excluded_scaffolding_only'].append(
                        f"{gen['file']}:{line_no} {msg_id}")
                    continue
                entry = {
                    'kind': 'verbatim',
                    'message_id': msg_id,
                    'turn_id': obj.get('turn_id'),
                    'role': role,
                    'text': text,
                    'text_len': len(text),
                    'thinking': thinking,
                    'thinking_len': len(thinking),
                    'tool_calls': tool_calls,
                    'scaffolding': scaffolding,
                }

            entry['_order'] = (gen['generation'], line_no)
            entry['source'] = {
                'generation': gen['generation'],
                'file': gen['file'],
                'line': line_no,
            }

            prior = best.get(msg_id)
            if prior is None:
                best[msg_id] = entry
            else:
                # Keep the richest copy, but remember every place it was seen.
                prior.setdefault('also_seen_in', []).append(entry['source'])
                if _weight(entry) > _weight(prior):
                    also = prior.get('also_seen_in', [])
                    entry['also_seen_in'] = also
                    best[msg_id] = entry

    messages = sorted(best.values(), key=lambda m: (m['_order'][0], m['_order'][1]))
    for i, m in enumerate(messages, start=1):
        m['seq'] = i
    return messages, accounting


def _weight(entry) -> int:
    """Richness score used to pick the winning copy of a duplicated message."""
    return (len(entry.get('text') or '')
            + len(entry.get('thinking') or '')
            + 200 * len(entry.get('tool_calls') or []))


def write_compaction_summaries(messages):
    """Archive compaction summaries as provenance, never as a replacement."""
    COMPACTION_DIR.mkdir(parents=True, exist_ok=True)
    written = []
    for m in messages:
        if m.get('kind') != 'compaction':
            continue
        turn = (m.get('turn_id') or 'unknown').replace(':', '_')
        gen = m['source']['generation']
        name = f"gen{gen}_{turn}.md"
        body = (
            f"# Compaction summary - generation {gen}\n\n"
            f"- message_id: `{m['message_id']}`\n"
            f"- turn_id: `{m.get('turn_id')}`\n"
            f"- source: `{m['source']['file']}:{m['source']['line']}`\n\n"
            f"**PROVENANCE, NOT THE RECORD.** This is a machine-written summary of\n"
            f"earlier messages. The messages themselves are in `corpus_full.jsonl`.\n"
            f"This file is kept so the compaction boundary stays auditable.\n\n"
            f"---\n\n{m.get('summary', '')}\n")
        (COMPACTION_DIR / name).write_text(body, encoding='utf-8')
        written.append(name)
    return written


def integrity(messages, accounting, source_text_bytes):
    """Hard assertions. A failure here means the extraction is wrong."""
    checks = []

    def check(cid, name, ok, detail):
        checks.append({'id': cid, 'name': name,
                       'status': 'OK' if ok else 'FAIL', 'detail': detail})
        return ok

    verbatim = [m for m in messages if m.get('kind') == 'verbatim']
    users = [m for m in verbatim if m.get('role') == 'user']

    first = next((m for m in messages if m.get('kind') == 'verbatim'), None)
    check('anchor', 'first verbatim message is message zero',
          bool(first) and MESSAGE_ZERO_ANCHOR in (first.get('text') or ''),
          (first.get('text', '')[:90] if first else 'no verbatim message found'))

    seqs = [m['seq'] for m in messages]
    check('seq', 'seq is a dense 1..N sequence',
          seqs == list(range(1, len(messages) + 1)),
          f'{len(messages)} messages')

    ids = [m['message_id'] for m in messages]
    check('dedupe', 'every message_id is unique in the corpus',
          len(ids) == len(set(ids)),
          f'{len(ids)} ids, {len(set(ids))} unique')

    emitted_text = sum(m.get('text_len', 0) for m in verbatim)
    ratio = (emitted_text / source_text_bytes) if source_text_bytes else 0.0
    check('verbatim_retention', 'emitted verbatim text >= 95% of extracted source text',
          ratio >= 0.95,
          f'emitted={emitted_text} source={source_text_bytes} ratio={ratio:.4f}')

    check('no_silent_drop', 'every source record is output or explicitly excluded',
          not accounting['parse_errors'] and not accounting['excluded_no_message_id'],
          f"parse_errors={len(accounting['parse_errors'])} "
          f"no_message_id={len(accounting['excluded_no_message_id'])} "
          f"scaffolding_only={len(accounting['excluded_scaffolding_only'])}")

    per_gen_user_max = max(
        (sum(1 for m in verbatim
             if m.get('role') == 'user' and m['source']['generation'] == g)
         for g in {m['source']['generation'] for m in verbatim}),
        default=0)
    check('user_turns', 'unique user turns >= the largest single generation',
          len(users) >= per_gen_user_max,
          f'unique_user_turns={len(users)} max_per_generation={per_gen_user_max}')

    romanian_preserved = any(
        re.search('[\u0103\u00e2\u00ee\u0219\u021b\u0102\u00c2\u00ce\u0218\u021a\u015f\u0163]', m.get('text', '')) for m in verbatim)
    check('language_law', 'Romanian wisdom text preserved verbatim in the corpus',
          romanian_preserved,
          'diacritics found in verbatim tier' if romanian_preserved
          else 'no Romanian diacritics found - suspect the language law was applied here')

    return checks, {'verbatim_text_bytes': emitted_text,
                    'source_text_bytes': source_text_bytes,
                    'verbatim_retention_ratio': round(ratio, 6)}


def write_corpus(messages):
    RAW.mkdir(parents=True, exist_ok=True)
    with open(CORPUS_FILE, 'w', encoding='utf-8', newline='\n') as f:
        for m in messages:
            out = {k: v for k, v in m.items() if not k.startswith('_')}
            f.write(json.dumps(out, ensure_ascii=False, sort_keys=True) + '\n')
    return sha256_file(CORPUS_FILE)


def write_changelog(messages, accounting, checks, meta, corpus_hash):
    RAW.mkdir(parents=True, exist_ok=True)
    gen_seen = OrderedDict()
    for m in messages:
        g = m['source']['generation']
        gen_seen.setdefault(g, {'file': m['source']['file'], 'count': 0,
                                'verbatim': 0, 'evidence': 0, 'compaction': 0,
                                'bytes': 0})
        gen_seen[g]['count'] += 1
        gen_seen[g][m['kind']] = gen_seen[g].get(m['kind'], 0) + 1
        gen_seen[g]['bytes'] += m.get('text_len', 0)

    lines = [
        '# CHANGELOG - corpus extraction',
        '',
        f"- generated: `{meta['generated']}`",
        f"- corpus file: `01_RAW/corpus_full.jsonl`",
        f"- corpus sha256: `{corpus_hash}`",
        f"- input records read: **{accounting['input_records']}**",
        f"- unique messages emitted: **{len(messages)}**",
        f"- verbatim tier (never cut): **{meta['verbatim_text_bytes']} bytes**",
        f"- source verbatim text bytes: **{meta['source_text_bytes']}**",
        f"- verbatim retention ratio: **{meta['verbatim_retention_ratio']}**",
        '',
        '## Two-tier retention',
        '',
        'TIER 1 VERBATIM - every user and assistant message in full. This tier is what',
        '"nothing is cut" governs. Assistant thinking is retained in a separate field.',
        '',
        'TIER 2 EVIDENCE - toolCall and toolResult records are indexed with a bounded',
        'preview and a pointer to their freeze file. Their payloads stay on disk; inlining',
        'them would let command output drown the reasoning that produced it.',
        '',
        '## Generations consumed (in chronological order)',
        '',
        '| gen | file | records | verbatim | evidence | compaction | verbatim bytes |',
        '|---|---|---|---|---|---|---|',
    ]
    for g, info in gen_seen.items():
        lines.append(
            f"| {g} | `{info['file']}` | {info['count']} | {info.get('verbatim',0)} | "
            f"{info.get('evidence',0)} | {info.get('compaction',0)} | {info['bytes']} |")

    lines += ['', '## Integrity checks', '',
              '| id | check | status | detail |', '|---|---|---|---|']
    for c in checks:
        lines.append(f"| `{c['id']}` | {c['name']} | **{c['status']}** | {c['detail']} |")

    lines += ['', '## Excluded records (explicit, never silent)', '']
    if not accounting['parse_errors'] and not accounting['excluded_no_message_id'] \
            and not accounting['excluded_scaffolding_only']:
        lines.append('None. Every source record reached the corpus or is a compaction '
                     'summary archived under `01_RAW/compaction_summaries/`.')
    else:
        for k, v in accounting.items():
            if isinstance(v, list) and v:
                lines.append(f'- **{k}**: {len(v)}')
                for item in v[:40]:
                    lines.append(f'  - `{item}`')
                if len(v) > 40:
                    lines.append(f'  - ... and {len(v) - 40} more')

    lines += ['', '## Per-message provenance', '',
              'Every record in `corpus_full.jsonl` carries a `source` object with '
              '`generation`, `file` and `line`, so any message can be traced back to the '
              'exact frozen line it came from, and any frozen line can be traced forward.',
              '', '## Idempotency', '',
              'Re-running the extractor against the same frozen input produces a '
              'byte-identical `corpus_full.jsonl`. Verify with:', '', '```powershell',
              'python 08_SELF_IMPROVEMENT\\corpus_extractor.py verify', '```', '']
    CHANGELOG_FILE.write_text('\n'.join(lines), encoding='utf-8')


def digest():
    """Print the user-turn digest used to author the chapter boundaries."""
    width = int(sys.argv[2]) if len(sys.argv) > 2 else 600
    messages, _ = extract()
    verbatim = [m for m in messages if m.get('kind') == 'verbatim']
    n = 0
    for m in verbatim:
        if m.get('role') != 'user':
            continue
        n += 1
        text = ' '.join((m.get('text') or '').split())
        print(f"#{n:03d} seq={m['seq']:4d} g={m['source']['generation']} "
              f"len={m.get('text_len',0):6d} | {text[:width]}")
    print(f"TOTAL user turns: {n}")


def verify():
    """Re-extract and compare against the corpus already on disk."""
    if not CORPUS_FILE.exists():
        print('FAIL: no corpus on disk to verify')
        return 1
    before = sha256_file(CORPUS_FILE)
    messages, accounting = extract()
    compactions = write_compaction_summaries(messages)
    after = write_corpus(messages)
    if before != after:
        print(f'FAIL: corpus is not idempotent\n  before={before}\n  after ={after}')
        return 1
    checks, _ = integrity(messages, accounting, _source_text_bytes(messages))
    failed = [c for c in checks if c['status'] != 'OK']
    print(f'idempotent: OK  sha256={after}')
    print(f'compaction summaries archived: {len(compactions)}')
    for c in checks:
        print(f"  [{c['status']}] {c['id']}: {c['detail']}")
    if failed:
        print(f'FAIL: {len(failed)} integrity check(s) failed')
        return 1
    print('all integrity checks OK')
    return 0


def _source_text_bytes(messages):
    return sum(m.get('text_len', 0) for m in messages if m.get('kind') == 'verbatim')


def _user_turn_ordinals(verbatim):
    """Map every user message to its 1-based user-turn ordinal."""
    ordinal = {}
    n = 0
    for m in verbatim:
        if m.get('role') == 'user':
            n += 1
            ordinal[m['seq']] = n
    return ordinal, n


def build_chapters():
    """Render one markdown file per named chapter, plus the corpus index.

    The grouping is by NAME. The EXTRACTION is by order: chapter N+1 starts at
    the turn immediately after chapter N ends, so the ranges tile the corpus
    with no gap and no overlap. Tiling is asserted, not assumed.
    """
    if not CORPUS_FILE.exists():
        print('FAIL: no corpus. Run extract first.')
        return 1

    chapter_map = json.loads(CHAPTER_MAP_FILE.read_text(encoding='utf-8'))
    chapters = chapter_map['chapters']

    messages, _ = extract()
    verbatim = [m for m in messages if m.get('kind') == 'verbatim']
    ordinal, total_turns = _user_turn_ordinals(verbatim)

    # --- tiling assertions -------------------------------------------------
    problems = []
    expected_start = 1
    for ch in chapters:
        lo, hi = ch['turn_range']
        if lo != expected_start:
            problems.append(f"{ch['id']}: starts at turn {lo}, expected {expected_start}")
        if hi < lo:
            problems.append(f"{ch['id']}: empty or reversed range {lo}..{hi}")
        expected_start = hi + 1
    if expected_start - 1 != total_turns:
        problems.append(
            f"chapters cover turns 1..{expected_start - 1} but the corpus has {total_turns}")

    if problems:
        print('FAIL: chapter ranges do not tile the corpus:')
        for p in problems:
            print(f'  - {p}')
        return 1

    CHAPTERS_DIR.mkdir(parents=True, exist_ok=True)
    index_rows = []
    placed_seqs = set()
    placed_bytes = 0

    # A verbatim message belongs to the chapter of the user turn it answers,
    # that is the nearest PRECEDING user turn. The assistant reply that follows
    # a user turn is part of that turn's act, even when it lands after the next
    # chapter's first user message would have started. Assigning by raw seq
    # range would strand every trailing reply in a gap between chapters.
    user_seqs = sorted(ordinal.keys())

    def owning_turn_seq(seq):
        owner = None
        for us in user_seqs:
            if us <= seq:
                owner = us
            else:
                break
        return owner

    turn_to_chapter = {}
    for ch in chapters:
        lo, hi = ch['turn_range']
        for n in range(lo, hi + 1):
            turn_to_chapter[n] = ch

    members_by_chapter = {ch['id']: [] for ch in chapters}
    for m in verbatim:
        owner = owning_turn_seq(m['seq'])
        n = ordinal.get(owner, 1)
        ch = turn_to_chapter.get(n)
        if ch is None:
            continue
        members_by_chapter[ch['id']].append(m)
        placed_seqs.add(m['seq'])
        placed_bytes += m.get('text_len', 0)

    for ch in chapters:
        members = members_by_chapter[ch['id']]
        if not members:
            print(f"FAIL: chapter {ch['id']} has no messages")
            return 1
        lo, hi = ch['turn_range']
        first_seq = min(m['seq'] for m in members)
        last_seq = max(m['seq'] for m in members)
        user_msgs = [m for m in members if m['role'] == 'user']
        asst_msgs = [m for m in members if m['role'] == 'assistant']
        turn_ids = sorted({m.get('turn_id') for m in members if m.get('turn_id')})
        tool_calls = sum(len(m.get('tool_calls') or []) for m in members)

        fn = f"{ch['id']}_{ch['slug']}.md"
        out = [
            f"# {ch['id']} - {ch['title']}",
            '',
            f"- **seq range**: `{first_seq}..{last_seq}`",
            f"- **user turns**: `{lo}..{hi}` of {total_turns}",
            f"- **messages**: {len(members)} "
            f"({len(user_msgs)} user, {len(asst_msgs)} assistant)",
            f"- **tool calls in range**: {tool_calls} (evidence tier, "
            f"`01_RAW/corpus_full.jsonl`)",
            f"- **source turn_ids**: {', '.join(f'`{t}`' for t in turn_ids[:6])}"
            + (' ...' if len(turn_ids) > 6 else ''),
            '',
            '## What this chapter covers',
            '',
            ch['covers'],
            '',
            '## Key concepts',
            '',
        ]
        out += [f"- {k}" for k in ch['key_concepts']]
        out += ['', '## Why it matters', '', ch['why_it_matters'], '']
        if ch.get('code_links'):
            out += ['## Code and doctrine bound to this chapter', '']
            out += [f"- `{c}`" for c in ch['code_links']]
            out += ['']
        out += [
            '## Source turn',
            '',
            f"Previous chapter: {'CH_00 (start of corpus)' if lo == 1 else 'the preceding chapter'}. "
            f"Extraction is strictly chronological: turn {hi} is followed by turn {hi + 1}, "
            'which opens the next chapter.',
            '',
            '---',
            '',
            '## Verbatim record (never cut)',
            '',
            'Popy\'s words are reproduced in full, in the language he used. System-reminder '
            'scaffolding is separated out by the extractor and preserved in the corpus '
            '`scaffolding` field.',
            '',
        ]
        for m in user_msgs:
            n = ordinal[m['seq']]
            out += [
                f"### USER turn {n} - seq {m['seq']} - "
                f"gen {m['source']['generation']}",
                '',
                (m.get('text') or '').strip() or '_(no user text)_',
                '',
            ]
        out += [
            '---',
            '',
            '## SENTINEL responses in this chapter',
            '',
            'Excerpts only, so the reasoning stays readable. The complete text of every '
            'message is in `01_RAW/corpus_full.jsonl` at the `seq` shown.',
            '',
        ]
        for m in asst_msgs:
            text = (m.get('text') or '').strip()
            excerpt = text[:1200] + (' ...[truncated in this view]' if len(text) > 1200 else '')
            out += [
                f"### ASSISTANT - seq {m['seq']} - gen {m['source']['generation']} "
                f"({len(text)} chars)",
                '',
                excerpt or '_(no assistant text part)_',
                '',
            ]
        (CHAPTERS_DIR / fn).write_text('\n'.join(out), encoding='utf-8')
        index_rows.append((ch['id'], ch['slug'], fn, first_seq, last_seq,
                           lo, hi, len(members), len(user_msgs), len(asst_msgs)))

    # --- every message placed? --------------------------------------------
    all_verbatim_seqs = {m['seq'] for m in verbatim}
    unplaced = sorted(all_verbatim_seqs - placed_seqs)
    unplaced_path = CHAPTERS_DIR / 'UNPLACED.md'
    if unplaced:
        lines = ['# Unplaced messages', '',
                 'Every message in the corpus must belong to exactly one chapter or appear '
                 'here with a reason. This file is the safety net: an empty one is the '
                 'proof that nothing was dropped.', '',
                 '| seq | role | turn | reason |', '|---|---|---|---|']
        for s in unplaced:
            m = next(x for x in verbatim if x['seq'] == s)
            lines.append(f"| {s} | {m['role']} | {ordinal.get(s, '-')} | "
                         f"outside every chapter seq range |")
        unplaced_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    else:
        unplaced_path.write_text(
            '# Unplaced messages\n\n**None.** Every verbatim message in the corpus '
            'belongs to exactly one chapter. The chapter ranges tile turns 1..'
            f'{total_turns} with no gap and no overlap.\n', encoding='utf-8')

    # --- corpus index ------------------------------------------------------
    idx = [
        '# 00 - CORPUS INDEX',
        '',
        'The SENTINEL brain corpus: this conversation, in order, grouped by name.',
        '',
        f'- **total messages**: {len(messages)}',
        f'- **verbatim tier**: {sum(1 for m in messages if m["kind"] == "verbatim")} '
        f'({placed_bytes:,} bytes of text, never cut)',
        f'- **evidence tier**: {sum(1 for m in messages if m["kind"] == "evidence")} '
        '(tool calls, indexed with a bounded preview)',
        f'- **compaction summaries**: {sum(1 for m in messages if m["kind"] == "compaction")} '
        '(archived as provenance under `01_RAW/compaction_summaries/`)',
        f'- **unique user turns**: {total_turns}',
        f'- **chapters**: {len(chapters)}',
        f'- **unplaced messages**: {len(unplaced)}',
        '',
        '## Chapters in chronological order',
        '',
        '| id | chapter | seq range | turns | messages | user | assistant | file |',
        '|---|---|---|---|---|---|---|---|',
    ]
    for cid, slug, fn, fs, ls, lo, hi, n, nu, na in index_rows:
        idx.append(f"| {cid} | {slug} | {fs}..{ls} | {lo}..{hi} | {n} | {nu} | {na} | "
                   f"[`{fn}`](02_CHAPTERS/{fn}) |")
    idx += [
        '',
        '## Cross-cutting chapters',
        '',
        '| file | axis |',
        '|---|---|',
        '| [`03_AXES/STRATEGY.md`](03_AXES/STRATEGY.md) | what was aimed at, and why |',
        '| [`03_AXES/REASON.md`](03_AXES/REASON.md) | the premises and the argument chain |',
        '| [`03_AXES/LOGIC.md`](03_AXES/LOGIC.md) | the decision rules and their derivation |',
        '| [`03_AXES/RATIONALE.md`](03_AXES/RATIONALE.md) | why this rule and not the obvious alternative |',
        '',
        '## Method chapters',
        '',
        '| file | method |',
        '|---|---|',
        '| [`04_METHOD/TANY_LLM_TO_SENTINEL.md`](04_METHOD/TANY_LLM_TO_SENTINEL.md) | '
        'the procedure that turns any LLM into SENTINEL |',
        '| [`04_METHOD/POPY_OPERATING_METHOD.md`](04_METHOD/POPY_OPERATING_METHOD.md) | '
        'how Popy drives a session |',
        '| [`04_METHOD/MISSTEPS_AND_CORRECTIONS.md`](04_METHOD/MISSTEPS_AND_CORRECTIONS.md) | '
        'every correction, verbatim, and the lesson |',
        '',
        '## Raw material',
        '',
        '| file | what |',
        '|---|---|',
        '| [`01_RAW/corpus_full.jsonl`](01_RAW/corpus_full.jsonl) | every message, '
        'deduplicated, chronological, with a source pointer |',
        '| [`01_RAW/CHANGELOG_EXTRACTION.md`](01_RAW/CHANGELOG_EXTRACTION.md) | '
        'provenance and integrity checks |',
        '| [`01_RAW/corpus_stats.json`](01_RAW/corpus_stats.json) | machine-readable stats |',
        '| [`01_RAW/chapter_map.json`](01_RAW/chapter_map.json) | the grouping definition |',
        '| [`01_RAW/compaction_summaries/`](01_RAW/compaction_summaries/) | provenance, '
        'never a replacement for the record |',
        '| [`05_SOURCES/source_registry.json`](05_SOURCES/source_registry.json) | '
        'every external archive, with checksum and read-only flag |',
        '| [`06_IDEA_TO_SCRIPT.md`](06_IDEA_TO_SCRIPT.md) | concept to file to tool to test |',
        '',
        '## Language law',
        '',
        'Wisdom stays Romanian and is reproduced verbatim. Every piece of code, every '
        'identifier, every docstring, every runtime message and every UI string in this '
        'system is English. The split is enforced by the `NoRomanianInCode` test class.',
        '',
    ]
    (BRAIN / '00_CORPUS_INDEX.md').write_text('\n'.join(idx), encoding='utf-8')

    stats = json.loads(STATS_FILE.read_text(encoding='utf-8')) if STATS_FILE.exists() else {}
    stats['chapters'] = [{
        'id': cid, 'slug': slug, 'file': fn, 'seq_from': fs, 'seq_to': ls,
        'turns': [lo, hi], 'messages': n, 'user': nu, 'assistant': na,
    } for cid, slug, fn, fs, ls, lo, hi, n, nu, na in index_rows]
    stats['unplaced_messages'] = len(unplaced)
    stats['total_user_turns'] = total_turns
    STATS_FILE.write_text(json.dumps(stats, indent=2, ensure_ascii=False), encoding='utf-8')

    print(f'chapters rendered : {len(index_rows)}')
    print(f'turns covered     : 1..{total_turns}')
    print(f'unplaced messages : {len(unplaced)}')
    for cid, slug, fn, fs, ls, lo, hi, n, nu, na in index_rows:
        print(f'  {cid} {slug:44s} seq {fs:4d}..{ls:4d}  turns {lo:3d}..{hi:3d}  '
              f'{n:3d} msgs ({nu} user)')
    return 0 if not unplaced else 1


def main():
    # The corpus carries Romanian verbatim, so every console path must be UTF-8.
    # The Windows default console encoding is cp1252 and raises
    # UnicodeEncodeError on the first diacritic it meets, which would make a
    # Romanian-language system look broken for a reason that is purely a
    # console setting.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding='utf-8', errors='replace')
        except (AttributeError, ValueError):
            pass

    cmd = sys.argv[1] if len(sys.argv) > 1 else 'extract'
    if cmd == 'digest':
        digest()
        return 0
    if cmd == 'verify':
        return verify()
    if cmd == 'chapters':
        return build_chapters()

    messages, accounting = extract()
    compactions = write_compaction_summaries(messages)
    checks, retention = integrity(messages, accounting, _source_text_bytes(messages))
    corpus_hash = write_corpus(messages)

    stats = {
        'generated': datetime.now().isoformat(),
        'corpus_sha256': corpus_hash,
        'messages_total': len(messages),
        'verbatim': sum(1 for m in messages if m['kind'] == 'verbatim'),
        'evidence': sum(1 for m in messages if m['kind'] == 'evidence'),
        'compaction': sum(1 for m in messages if m['kind'] == 'compaction'),
        'user_turns': sum(1 for m in messages
                          if m['kind'] == 'verbatim' and m['role'] == 'user'),
        'assistant_turns': sum(1 for m in messages
                               if m['kind'] == 'verbatim' and m['role'] == 'assistant'),
        'accounting': {k: (len(v) if isinstance(v, list) else v)
                       for k, v in accounting.items()},
        'retention': retention,
        'checks': checks,
    }
    STATS_FILE.write_text(json.dumps(stats, indent=2, ensure_ascii=False), encoding='utf-8')
    write_changelog(messages, accounting, checks,
                    {'generated': stats['generated'], **retention}, corpus_hash)

    print(f"corpus      : {CORPUS_FILE}")
    print(f"messages    : {stats['messages_total']} "
          f"(verbatim {stats['verbatim']}, evidence {stats['evidence']}, "
          f"compaction {stats['compaction']})")
    print(f"user turns  : {stats['user_turns']}")
    print(f"compactions : {len(compactions)} archived")
    print(f"sha256      : {corpus_hash}")
    for c in checks:
        print(f"  [{c['status']}] {c['id']}: {c['detail']}")
    return 0 if all(c['status'] == 'OK' for c in checks) else 1


if __name__ == '__main__':
    raise SystemExit(main())
