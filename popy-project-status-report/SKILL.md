---
name: popy-project-status-report
description: Popy's standing report format. Triggered by a single word - "report" - or "status report", "raport de stare", "where are we". Produces a fixed 7-section report in this order: Scope (stated first, always), Done since the beginning (compact timeline, not detail), What is left, Decisions needed from him, Considerations/risks, The one judgement call (done vs. not done), and Next. Always leads with the SCOPE. Always includes an explicit verdict on whether only detail remains or whether real problems remain. Applies to every project, not just SENTINEL_PRIME.
---

# Popy's Project Status Report

When Popy says **"report"**, produce this. Nothing else. Not a summary, not a
diary, not an essay. He wants the same shape every time so he can compare two
reports without re-reading them.

## Why this exists

He asked for it explicitly and permanently: *"When I ask for a report, this is
what I want to get, not anything else ever... This is my personal workflow."*

A report that reshapes itself each time is not a report. **Consistency of shape is
the feature.** Match the section order so he can diff two of them in his head.

## Rules that override the usual instincts

1. **Lead with the SCOPE.** He asked for this specifically: *"begin with the scope."*
   Not the timeline, not the wins. The purpose and boundary, in his terms.
2. **Timeline is compact, not detailed.** One line per completed thing. He said
   *"just scope it easily small not very large"*. If a section needs a table with
   sub-rows, it is too long.
3. **Step back. Look large.** He said *"don't look in detail, look largely."*
   Report the shape of the work, not the diffs.
4. **Give a verdict, do not hedge.** He wants to know explicitly whether the thing
   is finished. His words: *"if you don't have anything else but details left... okay
   report like that - but if it's not the case then please report on this because
   it's much more important."*
   So the verdict is a required section, not a closing sentence.
5. **Decisions are his, and they must be listed as decisions** - not as
   recommendations smuggled into the timeline.
6. **Romanian** for the report prose. Identifiers, file paths, commands and
   section anchors stay as they are on disk.

## The seven sections, in this order

### 1. SCOPUL
What the project is, what it is not, and the finish line. 3-6 lines. If the
scope itself is contested or unverified, say so here - that is the highest-value
thing the report can carry.

**Before writing the title, confirm the project name from the conversation.**
Never infer it from the folder, the workspace, or from another project you have
seen. On 2026-10-11 the name was inferred as "OPTIMUS PRIME DASHBOARD" when the
project was actually "Hermes Doctor"; the file had to be renamed and the real
damage was commits pushed into other projects' repos. If the name is not stated
in the conversation, ask — one question — rather than guess. A wrong project name
is data corruption, not a formatting slip.

### 2. SCURTĂ TIMELINE / CE S-A FĂCUT
Compact. One line per milestone, grouped into phases. No file sizes unless they
are the point. No hashes.

### 3. CE MAI RĂMASE
Open work, split by who owns it. Mark anything unmeasured as such - never fill the
gap with a plausible estimate.

### 4. DECIZII NECESARE
Only the ones that are genuinely his. Each with the recommendation, in one line,
and why it is his call. If a "decision" is really a technical choice, it does not
belong here - do the technical thing instead and say what you did.

### 5. DE LUAT ÎN CONSIDERARE
Risks, standing deviations, things that will bite later.

### 6. VERDICTUL - GATA SAU NU
The explicit call. Two shapes only:
- **"Doar detalii."** Everything of substance is done; what is left is polish.
- **"Nu e gata."** Name the medium and critical items explicitly, largest first.
Never split the difference to be agreeable. If the honest answer is "not done",
say it first and loudest.

### 7. PASUL URMĂTOR
One concrete next action, not a list.

## The report is a file, named after its own title

**A report that is only sent in chat is a report that leaves no trace.** Popy's
correction, stated twice: producing the format is one document; producing the
report itself is the second. Both are required.

On every report, write the file **at the root of the project being reported on**:

```
RAPORT DE STARE — <PROJECT> DASHBOARD - <YYYY-MM-DD HH-MM>.md
```

Rules for the name:

- **The file name equals the H1 inside it, character for character.** Popy's
  words: *"Să se numească cum are titlul în interior... Numele fișierului."* The
  name is not `raport.md`; the name is the report's own title.
- One dash between the blocks, the date at the end — so two reports of the same
  project are told apart at a glance in a file listing.
- **The time is written `20-04`, never `20:04`.** A colon is illegal in a
  Windows filename. Apply the same substitution to the H1 so the two stay
  identical; a title that cannot be its own filename is a defect.
- When a report replaces an older one, **do not silently destroy it**: copy the
  outgoing file to `raport-archive\raport-<YYYY-MM-DD_HH-MM>.md` first. A
  project with no version control has already lost M-24…M-27 once; overwriting
  the last report would repeat that shape for a much smaller loss.
- The file and the chat message carry the **same** content. A report whose file
  and whose message disagree is worse than either alone.

## Two failure modes to avoid

- **The flattering report.** Every line green, the reader learns nothing and is
  no safer than before. If the honest verdict is "not done", section 6 says so in
  the first sentence.
- **The unreadable report.** Forty lines of evidence for a status question. He
  asked for this format precisely because detail was drowning the signal.

## Evidence rule

Every number in the report is measured in the session it is written. If a figure
was not re-measured this turn, mark it with its date or write `NOT_MEASURED`. A
report repeats old numbers without saying so, it is the defect this whole session
was about - see `EVOLUTION.md` R10, where a dashboard looked alive and was frozen.