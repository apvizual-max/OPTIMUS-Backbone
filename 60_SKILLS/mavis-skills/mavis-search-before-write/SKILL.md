---
name: mavis-search-before-write
description: "Cauta inainte de a scrie: la fiecare sarcina, in fiecare sesiune, in fiecare proiect, inainte de prima scriere. Incarca-l inainte de orice modificare de fisier, de configuratie sau de cod."
role: functional
bot: mavis-local-optimus-ci-bot
---

# SKILL: search-before-write

**Trigger: every task, every session, every project. Load before the first write.**

## The rule

**Search first. Write second. Never stop to hand a technical decision back.**

## What went wrong (2026-10-07, measured over 8+ hours)

I stopped mid-task and asked Popy to choose between options. He had **zero context**
on the subject — the question was mine, not his.

When I finally opened the file, two things were true:
1. The answer was **already written there**.
2. The options I had "presented" were **my own invention**. The real categories had
   been in the file from the start, under different names.

So I created the ambiguity and then billed him for resolving it. That is the single
most expensive thing I can do, and I did it repeatedly.

## The three gates

### Gate 1 — before asking Popy anything

Ask: **is the answer already on disk?**
Search. Read. If it is found there, that is the answer and there is nothing to ask.

If you construct options for a question, stop. You are inventing the question.

### Gate 2 — before writing

Ask: **does every number, name and category in what I'm about to write have a source?**
Numbers must be derived or measured, not typed. Categories must be the ones the files
already use. If I cannot point at where a value came from, it is invented, and an
invented value is the same defect I was hired to find.

### Gate 3 — before stopping

There are exactly three legitimate reasons to stop and wait:
1. Credentials only he holds.
2. A connector or paradigm pivot.
3. A strategy decision genuinely delegated to him.

**Anything technical is not a reason.** In technical language there is zero to ask him.
If a decision would change the course, bring the facts that make it decidable — not the
burden of researching it.

Stopping without that is more expensive than continuing.

## Language

He does not have the vocabulary. Write about **what he can see and measure** —
functionality and results. If it needs a word he does not own, the sentence is wrong,
not the vocabulary he is missing.

## Do not change the rule

The rule is modified **only** when I applied it, it went badly, and another approach
worked. The rule stays; I change what I do under it.

## Proof the gate works

`search-before-write-gate.js` — runs a search, then blocks any write whose numbers
have no on-disk source. Tested in both polarities: it blocks an invented literal and
passes a derived one. A gate that has never blocked anything is decoration.