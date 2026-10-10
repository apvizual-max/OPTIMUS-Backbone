# DASHBOARD QUESTIONS — stage 1, ready to ask

Hand this over as-is and let them answer in one sitting. Mark the starred ones:
those change the architecture, and guessing them is how dashboards get built for
the wrong system.

---

## A. Purpose

1. **Who is going to read this?** Just you at 3 a.m., or a team? A second screen
   on the wall, or a window you alt-tab to?
2. ★ **What decision does it change?** If I cannot name it, we are building a
   decoration.
3. **How often will they look?** A glance every few minutes is a *status* surface.
   A deep read is an *investigation* surface. They need different density and a
   different default view.
4. ★ **What must never be wrong on this screen?** That is the panel that gets the
   attention.
5. **What do you explicitly NOT want to see?** Naming the exclusions saves more
   time than naming the inclusions.

## B. The domain

6. ★ **What are the things?** Every entity the dashboard will talk about.
7. ★ **For each one, what states can it be in?** Include the awkward ones.
   *Down, slow, answering-late, stale and never-measured are five different
   states and must look different.*
8. ★ **What does "healthy" mean concretely, for one of them?** If the answer is
   "it answers", we will report health for something that is answering from a
   cache of state that no longer exists.
9. **What are the relationships?** Who restarts what? What dies with what?
10. **Who owns each thing?** A thing nobody restarts is a thing that stays dead,
    and the screen should say so.

## C. Measurement

11. ★ **What already exposes this?** An API, a log, a socket, a CLI, a file.
12. **What has no interface at all?** These are your honest gaps. They belong on
    screen labelled as gaps.
13. ★ **How long does one read of each take?** Get real numbers. This decides the
    architecture more than any other answer here.
14. **What is expensive enough that measuring it changes the system?**
15. **What is destructive to read?** Never measure by mutating.

## D. Constraints

16. ★ **Where does this run, and who can reach it?** Loopback-only changes the
    security story completely.
17. **What is on the machine already?** RAM, disk, CPU, and whether there is a
    GPU. A loaded box and an idle one are different designs.
18. ★ **What must survive a reboot?** A scheduled task, a service, a logon hook.
19. **What can be installed, and what must not be touched at all?** Name the
    prohibitions. A fleet that was lost once is a fleet you never prune.
20. **Are there existing dashboards or tools this must agree with?**

## E. Standards

21. **What does "good" look like to you?** Density, colour, voice, language.
22. **Is there something it should look like?** A reference changes the entire
    visual language, so this is best asked now rather than discovered later.
23. **How should it get your attention?** What deserves a red line, and what is a
    footnote?
24. **What did the last attempt get wrong?** The cheapest information available.

## F. Risk

25. ★ **What happens if this is wrong?** A wrong number is a nuisance. A wrong
    *destructive action* is not.
26. **Where is the restore point?** If there is not one yet, that is stage 4 work
    and it comes before the first edit.
27. **Who may run the actions?** In the reference implementation the page may only
    ever send an identifier, never a command.
28. **Is there anything here that must never happen automatically?** Write it down
    now, while you are thinking about it.

---

## After they answer

- [ ] Purpose is **one sentence** naming a decision.
- [ ] Every entity has an **exhaustive state list**.
- [ ] Every number has a **source** and a **cost**.
- [ ] Prohibitions are written down.
- [ ] Restore point strategy agreed.
- [ ] They have said "yes, that's it" in their own words.

**If you cannot write the one-sentence purpose, do not start researching.** You
will research the wrong thing beautifully.

Then go to stage 2, and **expect a second round of questions**. That is the
process working.
