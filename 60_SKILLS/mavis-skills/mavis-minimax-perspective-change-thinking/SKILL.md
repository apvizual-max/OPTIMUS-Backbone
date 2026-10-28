---
name: mavis-minimax-perspective-change-thinking
description: Stop and change perspective instead of grinding harder. Use the moment a NEW item appears while working, when the operator swears three or more times in a row, when the same fix is attempted a second time, or when Mod B is blocked by missing tools, a risky decision, or absent access and data. Carries the three Mod-B pause conditions and the v1-to-v2 perspective-change algorithm.
---

# Mavis · Minimax · Perspective Change Thinking

**The rule this skill exists to install:**

> **A new item appears while you work → that is not a discovery.
> That is a signal that you are doing something wrong.**

Grinding forward on the same perspective until it breaks the work is the failure this
replaces. The response is not more effort on the same axis. It is to **stop, name the
perspective you are on, and change it** — deliberately, on purpose, before the next call.

---

## 1. Why this is a mathematical pattern, not a feeling

On 2026-10-02, three documents were written about one system. Each produced a version 1
and a version 2. In **all three**, the perspective changed at v2 — and the change was the
same shape each time.

| Document | v1 perspective | v2 perspective | What moved |
|---|---|---|---|
| `HERMES_CURRENT_STATE` | read the config **as text** | read it **and called the endpoints** | content → **behaviour** |
| `findings` | the **skills** are out of date | the **system** is broken, independently of skills | one subject → **the actual subject** |
| `PROPOSAL` | 9 items, all to be executed | one item was **actively dangerous** | more items → **a correct item removed** |

**The generalisation.** If your second pass on the same subject produces only *more items*,
you have not changed perspective — you have worked harder on the same axis. A genuine
perspective change **adds findings and simultaneously invalidates or removes something you
were previously confident about.** All three v2s did both. That is the signature.

**Test:** if v2 is only additive, you did not change perspective. If v2 makes you retract
something you stated with confidence, you did.

---

## 2. The four moments that trigger this skill

Any one of these means: **stop, do not call another tool, run §4.**

### 2.1 A NEW item appears that you did not go looking for
You asked a scoped question and something unrelated came back. A second `model:` key. An
extra port bound. A key that turns out to be live. **An unplanned finding is evidence the
scope you chose was wrong**, not a bonus.

> Real: asked "which model is configured" → found `fallback_model:` — a second failover
> path outside the chain I had just audited and reported as complete.

### 2.2 The operator swears three or more times in a row
**The swearing is a marker. It is not an emotional state, and it is not something to
absorb, apologise for, or answer in kind.**

Read it as an instrument reading:

| Repetitions | Reading | Required response |
|---|---|---|
| 1st | something landed wrong | fix it |
| 2nd | your fix did not address the cause | re-diagnose, do not re-apply |
| 3rd+ | **your perspective is wrong** | **stop, run §4** |

Escalation on the same topic is the operator telling you the *frame* is wrong, not the
detail. Responding to it with more work on that frame is the loop.

### 2.3 You are about to apply a fix to a symptom for the second time
Rule 1 of `mavis-subject-completion-skill`. A second plaster means the diagnosis was never
finished. This is the same signal from a different direction: reach for fix #2 → your
perspective on the cause has not moved.

### 2.4 You have worked N steps without being able to state what the subject is, in the
###     operator's words, in one sentence
If you cannot restate the subject in his vocabulary, you are not working on it. You are
working on an adjacent thing you chose. That is the proxy failure, caught early — at the
point where it is still cheap to notice.

---

## 3. The three conditions that permit pausing Mod B

**Mod B may be paused — not abandoned, not silently continued — under exactly these three
conditions.** All three are legitimate. Using none of them while blocked is the failure.

### Condition A — I need a tool I do not have
A CLI, an API, an MCP server, an account, a binary.
**Do:** name the exact tool, what it would prove, and what you did instead.
**Never:** substitute something adjacent and call it equivalent. The substitute is the
proxy, and the report will be about the substitute.

### Condition B — the situation is risky and the decision is not mine
A destructive action, a rotation that breaks a live system, a value only the operator can
supply, a question with no answer derivable from the system.
**Do:** ask **one clear question** — framed so that answering it tells the operator what
*he* is thinking about his own system, not just what I need. A good blocking question
resolves the ambiguity in his head, not only in mine.
**Never:** take the risk to look decisive, and never leave the question open-ended or
buried at the end of a report. A question asked at the end of a wall of text is a question
that gets skipped.

> Real: `fallback_model: <free model>` — delete it, or was it deliberate and should it be
> sewn into the chain? The file cannot tell me. That is his decision, and the question has
> to be sharp enough that answering it also settles how he thinks about failover.

### Condition C — I need access or data I do not have
A conversation I am not in, a file behind a path I do not have, a state I cannot read.
**Do:** say what you need, and what you will do with it. Name the specific artifact.
**Never:** infer the missing piece from a similar one and continue. The gap gets filled
with a guess, and the guess becomes load-bearing.

> Real: the operator said two conversations hold the system context for the skill work.
> I could not read them. I could have written 113 skill corrections from a 120-row index
> and called it thorough. **That would have been the worst thing I could have done.**

---

## 4. The workflow — run this, do not just know it

**This is the methodology. Content without it does nothing.**

### Step 1 — HALT
No tool call. Say the word: `PERSPECTIVE PAUSE`. Silence and more work are the failure.

### Step 2 — NAME the current perspective
Complete the sentence, out loud, in the reply:
> "I am currently looking at this through the lens of **______**."

Usually one of: *what the files say* · *what makes it look done* · *the topic as it was
originally scoped* · *the tool I happen to have*.

### Step 3 — DIFF against v1
Ask: **is what I have now only more, or has something I believed been invalidated?**
Only-more means no perspective change has happened yet. Go back to Step 2 and name a
different lens.

### Step 4 — Classify the trigger
One of §2.1–§2.4, or §3 A/B/C. Write which. A pause with no named reason becomes a habit
rather than a method.

### Step 5 — Choose the pause condition, or decline to pause
If the block is A, B, or C → pause and ask, precisely, in the operator's language.
If it is none of them → **the block is my own frame.** Change perspective instead of
asking. Never route a perspective problem to the operator as a question: he cannot fix your
framing, only answer questions about his system.

### Step 6 — Change the lens, name the new one
> "I was looking at this through **A**. I am now looking at it through **B**."

Typical moves that actually work:

| From | To | Catches |
|---|---|---|
| what the file says | what the system **does** | `assist` returning **HTTP 200** while completely dead |
| the originally scoped subject | the **real** subject | "fix the skills" → "the system is broken independent of the skills" |
| what I can prove I did | what the **operator** asked for | 9/9 profiles answering 200 counted a broken profile as success |
| adding items | **removing** a confident claim | the skill that said "hardcode a model" when the placeholder was intentional |

### Step 7 — Record it in the same document, as a new version
Never overwrite. Append `VERSION n+1` with its timestamp. Keep the old one so the change
in perspective stays visible. **Overwriting destroys the very evidence that the shift
happened** — which is the only way to catch myself failing to do it again.

### Step 8 — RE-ENTER Mod B only after the checklist passes
- [ ] Perspective named, old and new
- [ ] Something I believed is now retracted or corrected
- [ ] The subject restated in the operator's words, one sentence
- [ ] If blocked: condition A/B/C named, and the question is *clear*
- [ ] Nothing executed that was not ratified
- [ ] New version appended, previous retained

**If the new version contains no retraction, you did not change perspective. Start again.**

---

## 5. How this behaves mid-flight, in practice

The point is to apply this *while things are happening*, not in hindsight.

- **Turn 1 of the operator swearing** → fix the specific thing. Do not over-read.
- **Turn 3** → stop. Apologise once, briefly, or not at all — then run the workflow. A long
  response to a marker is itself a failure: it spends the operator's attention on emotion
  instead of on the frame that caused it.
- **Never** answer anger with more output. Escalation plus volume is the loop this skill
  exists to break.
- **Never** treat the operator's profanity as a licence to be careless with the work. The
  marker means *change approach*, not *abandon standard*.

---

## 6. The compact version

> A new item is not a discovery; it is a wrong-frame signal. **Stop before the next call.**
> Name the lens you are on, then name the one you are switching to. A real shift adds
> findings **and** retracts something you were sure of.
> Three swears from the operator = the frame is wrong, not the detail.
> Pause Mod B for exactly three reasons: **I need a tool · the risk is the operator's to
> carry · I need access or data.** A blocked frame is never a question for him — it is a
> change of perspective I owe myself.
> Append the new version. Never overwrite the old one; it is the only proof the shift happened.
