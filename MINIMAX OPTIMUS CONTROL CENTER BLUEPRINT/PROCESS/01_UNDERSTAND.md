# 01 — STAGE 1: UNDERSTAND

**You cannot research what you have not asked about, and you cannot build a dashboard
for a purpose nobody stated.** The first stage exists to convert a wish into a
specification, and the only source of the specification is the human.

The worked example began as *"make this better"*. By the end of this stage it had
become: a 15-tab console for a 60-container AI swarm, bound to loopback, surviving
reboot, with a live AI analyst, a self-verifying page, and a quarantine restore
point. None of that was guessed. All of it was asked.

---

## The rule

**Ask everything at once.** A questionnaire the human can answer in one sitting
beats an interrogation across nine turns. Batch your questions, group them, mark
the ones that actually change the design, and let the rest default.

Then: **ask again.** Research will surface things the first round did not. That is
not failure — that is the process working. Iterate until nothing new appears.

---

## The questionnaire

### A. What is this FOR?

The single most important question, and the one most often skipped.

- **Who reads it?** One operator at 3 a.m., or a team? A wall display, or a window
  they alt-tab to?
- **What decision does it change?** A dashboard that informs nothing should not
  exist. If you cannot name the decision, you have not found the purpose yet.
- **How often?** A glance every few minutes is a *status* surface. A deep read is
  an *investigation* surface. They need different density, different defaults, and
  different refresh behaviour.
- **What is the one thing that must never be wrong?** Name it. That is the panel
  that gets the budget.
- **What is explicitly NOT wanted?** Naming the exclusions saves more time than
  naming the inclusions.

### B. What is it about? — the domain

You need the nouns and the verbs of the system before you can measure anything.

- **What are the entities?** (containers, services, bridges, models, jobs, people)
- **What states can each be in?** Enumerate exhaustively, including the ones you
  would rather not show. *Down* and *slow* and *late* and *unknown* are different
  states.
- **What does "healthy" mean here**, concretely, for one entity? If the answer is
  "it returns 200", the dashboard will report health for a process answering from a
  cache of state that no longer exists.
- **What are the relationships?** Which thing restarts which? What dies with what?
- **Who or what owns each thing?** A thing nobody restarts is a thing that stays
  dead, and the dashboard should say so.

### C. What can you actually measure?

The boundary between "would be nice" and "can be read" decides the design.

- **What already exposes this?** An API, a log, a socket, a CLI, a file.
- **What has no interface at all?** These are the honest gaps, and they belong on
  the screen labelled as gaps.
- **How fast can each be read?** A measurement that costs 20 seconds and one that
  costs 4 milliseconds do not belong on the same refresh path. This constraint
  shapes the architecture more than any other single fact.
- **What is destructive to read?** Never measure by mutating.
- **What is expensive enough that measuring it changes the system?**

### D. Constraints — the ones that close designs

- **Where does it run, and who can reach it?** Loopback-only changes the security
  story completely.
- **What is on the machine already?** A 63 GB box under memory pressure and a
  single-server laptop are different machines for planning purposes.
- **What must survive a reboot?** A scheduled task, a service, a logon hook.
- **What can be installed, and what cannot?** No new subscriptions. No changes to
  load-bearing systems. These are hard walls.
- **What is still running that must not be touched?** Name it explicitly. In the
  worked example, a 31-container swarm was protected by an explicit prohibition
  learned the hard way.

### E. The human's own standards

- **What does "good" look like to you?** Aesthetics, density, voice, language.
- **Is there something it should look like?** A reference changes the entire
  visual language. Ask now, not after building.
- **How do you want to be interrupted?** What deserves a red line and what is a
  footnote?
- **What did the last attempt get wrong?** Cheapest information in the entire
  process.

### F. Risk and reversibility

- **What happens if this is wrong?** A wrong number is a nuisance; a wrong
  *destructive* action is not.
- **Where is the restore point?** If the answer is "there isn't one yet", that is
  stage 4 work, and it comes before the first edit.
- **Who is allowed to run the destructive actions?** In the worked example, a
  whitelist resolved from the measurement — the page may only ever send an
  identifier, never a command.

---

## Exit criteria — do not leave stage 1 until all are true

- [ ] You can state the dashboard's purpose in **one sentence** that names the
      decision it supports.
- [ ] Every entity has an **enumerated state list**, and "slow" is on it somewhere.
- [ ] Every number you intend to display has a **known source** and a **known cost**.
- [ ] Every constraint that closes a design is written down.
- [ ] The restore point strategy is agreed.
- [ ] The human has said "yes, that's it" in their own words.

**If you cannot write the one-sentence purpose, you are still in stage 1.** Do not
start researching; you will research the wrong thing beautifully.

---

## The output of stage 1

A short specification — one page is plenty — containing:

1. the one-sentence purpose,
2. the entity/state table,
3. the measurement inventory (source + cost per number),
4. the constraints and prohibitions,
5. the definition of done, in the human's words.

Carry it into stage 2. It is the brief the research is answering.
