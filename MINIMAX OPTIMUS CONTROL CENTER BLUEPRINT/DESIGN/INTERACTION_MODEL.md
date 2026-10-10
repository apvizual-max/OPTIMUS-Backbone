# INTERACTION MODEL

How the page behaves over time, and the rules that keep a re-rendering page from
being an enemy to the person reading it.

---

## The central tension

The page re-renders itself every few seconds so it stays true. That same
re-rendering destroys anything the operator is **reading, typing, or waiting for**.

**Every design decision here is a decision about that tension.** The worked example
lost an entire feature to it: an answer arrived 26 seconds after the question, by
which time the element it was destined for had been replaced four times. The
answer was rendered, correctly, into a node nobody could see.

---

## Rules

### 1 — Never capture a DOM node across an `await`

```javascript
const out = document.getElementById('aiOut');   // captured
await fetch('/api/ask', …)                      // 26 seconds
out.textContent = answer                        // written into a dead node
```

The poll replaced `#view` five seconds in. Everything after that line was
invisible.

**Do:** keep the *value* outside the DOM, re-resolve the element at the moment of
writing, and make the render function draw from the value.

```javascript
let answer = null;                                  // survives re-render
function paint(){ const el=document.getElementById('aiOut'); … }   // fresh
function render(){ … paint() … }                                     // draws it every time
```

### 2 — Anything the human typed must survive a poll

Textarea contents, filter text, a scroll position, an expanded panel. Either hold
it outside the DOM, or restore it after render. **A poll that clears what someone
was typing is a poll that loses their work.**

### 3 — Never block the request path on a measurement

See `ARCHITECTURE.md` contract C3. The stall the worked example still has is this
rule broken by exactly one character.

### 4 — Show the age, always, everywhere

Data that is 4 minutes old must *look* four minutes old. This is what makes
"stale" a state the operator can act on rather than a subtlety they must notice.

### 5 — One request in flight per resource

`busy` latches, not queues. A second press while the first is running should be a
no-op, not a second request. A status bar that queues twenty actions behind each
other is worse than one that refuses.

### 6 — Polling stops when nobody is looking

When the tab is hidden, poll slowly or not at all. The worked example's poll
interval is 5 s; a background tab refreshing at 5 s is work for nobody, and on a
loaded machine it is work that costs the measurement itself.

### 7 — Animations play once

A re-render every few seconds re-triggers entrance animation, and the page pulses
forever. Fire the animation once, on first paint, and never again.

### 8 — The keyboard is a first-class path, not a shortcut

`Ctrl K` opens the palette. `1–9, 0` switch tabs. `A` jumps to the assistant.
`?` opens help. `Esc` closes everything.

Test every shortcut, and test that it **ignores itself while the operator is
typing** — a digit typed into a question box must not switch tabs. That guard is
one line and it is easy to get wrong; in the worked example a synthetic keypress
delivered to the wrong target made the guard look broken when it was fine.

### 9 — Deep-linkable state

The open tab belongs in the URL. A console you keep in a bookmark bar should land
where you left it, and a screenshot you send someone should be a link that opens
the same panel.

> Implement with `history.replaceState`, not `location.hash = …`. Assignment adds a
> history entry per interaction and buries the Back button. And **qualify it** —
> `window.history.replaceState`, not `history.replaceState`, because a script-scope
> `let history` shadows the global and the call throws on every render. That exact
> shadowing shipped a broken feature in the worked example.

### 10 — Never re-render what the operator is looking at

If a panel is expanded, keep it expanded across renders. If they are mid-scroll
in a table, keep them there. Re-render *data*; preserve *state*.

---

## The update cycle, end to end

```
 t+0.0s   the operator asks something
 t+0.0s   the handler stores the PENDING state and paints it
 t+5s     poll → render → pending state still shown, still "thinking"
 t+10s    poll → render → same
 t+26s    the response arrives → store the ANSWER, paint it
 t+30s    poll → render → the answer is STILL THERE, because it lives in a
          variable and render draws it, not because a node survived
```

**The answer must be re-derivable on every render.** If it is only ever written
once, into a node, it is gone on the next repaint.

---

## The rule behind all ten

> **The page is a function of state, not a sequence of writes.**

State lives outside the DOM. Render is pure: read state, produce the whole view.
Everything above follows from that one idea — the surviving answer, the preserved
scroll, the persistent tab, the deep link.
