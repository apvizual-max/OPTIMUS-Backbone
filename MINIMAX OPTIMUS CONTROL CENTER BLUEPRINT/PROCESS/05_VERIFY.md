# 05 — STAGE 5: VERIFY

**The most-skipped stage in the world, and the only one that can tell you whether
you built something or imagined one.**

The worked example reported 7/7 for hours while a headline feature had never once
worked. Green is not a state you have earned; it is a state someone has not
disproven yet.

---

## Three layers, and you need all three

### Layer 1 — File-level: does it parse and load?

The cheapest layer, and the one people mistake for the whole.

```
node --check              on the extracted inline <script>
[Parser]::ParseFile       on every PowerShell file
```

**What it cannot do:** tell you a single thing about whether the dashboard works. A
page whose script does not parse still returns HTTP 200, still serves perfect
`/api/state`, still writes nothing to any log, and still renders a plausible
skeleton. All four statements are true simultaneously. It took a **five-hour
outage** for the worked example to discover that its own self-test, passing
continuously, had never once executed the feature it claimed to cover.

### Layer 2 — In-page: is it actually alive?

The page checks itself, from inside, about things only a running page can know:
the script executed, the tabs render, the icons paint, the font is loaded, no
external resources, the data is fresh.

This is where the worked example's "self-test" belongs, and it is genuinely
valuable — a parse error in a page that is otherwise fine is invisible to every
other layer.

**But a structural check standing in for a behavioural one is the classic trap.**
"Every control has a handler" cannot catch "the handler writes to a detached node."

### Layer 3 — Behavioural: run the thing, from the outside

The only layer that can catch everything above. Four moves, in order:

1. **Load the page in a real browser.** Not a fetch. A fetch cannot see a blank
   panel.
2. **Read the rendered geometry.** `getBoundingClientRect` and
   `getComputedStyle`, not `element exists`. Presence in the DOM is not appearance
   on screen.
3. **Press the controls.** Every one. The AI Analyst was broken for its whole life
   and was found by pressing Ask and *reading what appeared*.
4. **Watch across a re-render.** The single most productive move in the entire
   process. The failure that hides best is one that appears, then is wiped by the
   next poll — because the answer arrived after the element was replaced.

> **A control that renders perfectly and still does nothing is the defect this
> whole stage exists to find.** Only pressing it finds it.

---

## Verify the honesty, not just the function

Functional tests ask "does it work". Honesty tests ask "**does it tell the truth**".
Write both.

- **Prove a good state reads good.** Inject a healthy value, confirm it renders
  healthy.
- **Prove a bad state reads bad, and differently.** This is the one everybody
  skips. Down, slow, late, stale, empty and never-loaded must be **visibly
  different**, or the operator is reading a rumour.
- **Prove the numbers come from the measurement.** Change the measurement; the
  number must move.
- **Prove the absence of a number is explained.** A blank with no reason is worse
  than a wrong number, because it looks like nothing is happening.

In the worked example this is where the biggest win came from: a failure path
returned `$null` for *every* kind of failure, so a bridge that was **down** and a
bridge that was **healthy but answering late** rendered identically. The fix was to
make the failure result carry *which* failure — and the panel now says *"Answered
late, not down. Restarting the bridge will not help."*

---

## Prove it can survive what actually happens

| Event | Test it by |
|---|---|
| a measurement is slow or missing | break the source; confirm last-good is served and marked |
| the process dies | kill it; confirm the supervisor restores it *without help* |
| the machine reboots | cold-kill everything, then start the scheduled task and watch |
| the source changes | edit a file; confirm the running process is flagged as stale |
| the operator clicks fast | rapid-fire every control; confirm no duplicate requests, no lost state |
| the operator is on a slow link | throttle; confirm the UI degrades to "old data", not to blank |
| the disk fills | confirm the write fails loudly rather than silently truncating |

**The machine restarting without being asked is the real test of a supervisor.**
In the worked example, the supervisor recovered the console from a total outage
while nobody was watching — which was the correct behaviour, and was the only part
of that bad night that needed no human.

---

## The rules that make verification trustworthy

**Break it on purpose.** Every check must be shown capable of failing. A
verification suite nobody has ever seen go red is a decoration.

**Write the test before you trust it, and read the object it reads.** A test that
shares an identifier with the code under test is measuring the code under test. One
assertion in the worked example read `history.length` where `window.history.length`
was meant — the object it measured **was** the defect, and it passed.

**Record the version of the instrument.** "I ran it" is not evidence. "I ran *this*,
against *that*, and the output was *this*" is.

---

## Done means

- [ ] File-level parse clean
- [ ] In-page self-test green **and** shown capable of failing
- [ ] Every control pressed, with the result read
- [ ] Behaviour confirmed across at least one re-render
- [ ] Good / bad / slow / late / stale / absent states visibly different
- [ ] Kill-and-recover proven
- [ ] Reboot-survival proven
- [ ] A supervisor recovers with no human present
