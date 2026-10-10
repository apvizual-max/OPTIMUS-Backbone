# STRATEGIC TREE

**Why this exists, what it is for, and the things it must never become.** The
technical trees describe what it does. This one describes what it is *for*, and it
is the document to re-read when a change looks reasonable and still feels wrong.

---

## The one sentence

> This exists so that one person can answer *"is anything actually broken, and what
> do I do about it"* in one pass, at 3 a.m., without running a single command.

Every decision below is a consequence of that sentence, including the ones that
cost effort and bought no feature.

---

## What it is for

**Replacement for a ritual, not a display.** The alternative is a person opening
three terminals and remembering a port, a command, and a verdict. Every second
that ritual costs is the cost this pays down.

**A shared surface, not a private one.** One operator here; tomorrow, a team, a
wall display, a handover to someone who has never seen the machine. A dashboard
that only its author can read is a diary.

**The first of many.** The value is not this console. It is that the *next* one
takes an afternoon instead of a month, because the shape, the language, the traps
and the verification are already written down.

---

## What it must never become

**A green light that means nothing.** The single failure mode. Not "it broke" —
*it is green and it is lying*. The worked example sat at 7/7 for hours while a
headline feature had never worked and a five-hour outage ran in the background.
**Confidence is the product. Spend it only on things you have measured.**

**A second source of truth.** If the dashboard holds a number nothing else can
produce, it becomes a dependency — and a dashboard that breaks is worse than no
dashboard. Everything it shows is measured from the live system, every time.

**A place where opinions live.** It may form an opinion, because that is the
spark. It may not form one the human cannot re-derive from the screen. An opinion
you cannot check is a rumour, and a rumour at 3 a.m. is worse than silence.

**A place that hides its own staleness.** Data age is always on screen. A number
without a timestamp is a claim, and claims are what this thing exists to replace.

**A thing that degrades the machine.** Every process it adds is a cost paid by the
system it observes. Budget for it, measure it, and reduce it.

**An action surface.** The page may *show* what would help. It may not *do* it
beyond an explicit, whitelisted, human-initiated action — and never anything that
destroys a fleet that was already lost once.

---

## The decisions that bought no feature and were still right

Worth listing, because they are the ones that get cut first under pressure:

- **Self-contained, zero external resources.** No CDN, no webfont, no network. A
  dashboard must work on a machine whose connectivity is part of the incident.
  Cost: generating an icon subset, shipping 500 KB of font. Benefit: it works
  during a network outage, and the test can *assert* it.
- **The self-test runs its own handlers.** A structural pass is cheaper and
  catches less. The behavioural pass — stub a dependency, invoke the real
  handler, assert the result reached a *connected* node — is what would have
  caught the never-worked feature.
- **A trace mode in the collector, on from day one.** It is the difference between
  "the collector is slow" and "one endpoint takes 8.5 s of a 22 s collect".
- **Reporting what was NOT done.** The list of things noticed and deliberately
  deferred is more useful to the next person than a paragraph of praise.

---

## What "the spark" means, precisely

Not animation. Not a chart type. **The dashboard forms an opinion and shows its
reasoning.**

> *"Answered late, not down. The bridge replied in 8029 ms against an 8 s budget,
> so the probe gave up before the answer arrived. Restarting the bridge will not
> help — it is healthy and slow."*

That sentence is worth more than a page of statuses, because it is the thing a
tired person at 3 a.m. would otherwise have to work out, and might get wrong in the
direction of restarting something that is working.

The cost of the spark is one constraint — **never form an opinion you cannot back
with a measurement the human can re-derive** — and it is the single change that
turns a report into an instrument.
