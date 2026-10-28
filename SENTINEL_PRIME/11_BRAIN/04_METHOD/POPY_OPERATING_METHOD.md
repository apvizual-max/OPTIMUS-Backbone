# POPY OPERATING METHOD - how a session is actually run

The observed procedure for driving SENTINEL work: how a session opens, how agreement is formed,
how execution is authorised, how the operator intervenes, and how a session ends. This is the
*driver's* manual; `TANY_LLM_TO_SENTINEL.md` is the *builder's* manual.

Source: the corpus, 102 user turns, `../01_RAW/corpus_full.jsonl`. Turn numbers are user turns.

---

## 1. The shape of a session

```
OPEN      a question, a challenge, or a reference material - never a bare order
          -> the system is asked to reason before it is asked to build

STRESS    the operator tests the answer against reality (a real file, a real number,
          a real claim about the world) and the system either holds or is corrected

TEACH     the operator supplies the source material at full density (poems, vessels,
          sessions) and the system must extract the structure from it rather than
          describe the material

CODE      the settled structure becomes files, then code, then tests, in that order
          and in the same session

VERIFY    the operator asks whether it actually works, in the same words each time:
          "real?", "functional?", "implemented?", "tested?"

CORRECT   one line, then compliance. The rule is recorded and becomes durable.
```

The ordering is not stylistic. Each stage produces the input the next stage needs: you cannot code
from an unstressed answer, and you cannot verify a thing that was never written down.

---

## 2. The correction idiom

The single most transferable pattern in the corpus. A correction has three parts and no padding:

| Part | Example from the corpus |
|---|---|
| The verdict, flat | "you are NOT showing competence here mate" (turn 3) |
| The specific failure | "ei considera ca nu exista nici o similitudine concreta...de asta, nu ai dreptate sa te contrazici" (turn 78) |
| The boundary that is *not* being drawn | "eu nu te-am intrebat daca esti biologic viu...ca nu sunt creetin" (turn 67) |

Three properties worth copying:

1. **It is one line of verdict and one line of substance.** No speech, no reassurance, no
   negotiation of feelings.
2. **It states what was NOT asked.** Turn 67 is a correction that works by removing a strawman the
   model had introduced. Naming the false question is faster than answering it.
3. **It is followed by compliance, not by an argument.** The lesson is recorded afterwards as a
   durable rule. The argument, if there is one, comes later and in one line.

The operator also corrects **himself** in the same idiom - "Dar 'jumătate din călugării care conduc
Ortodoxia sunt femei' — exagerez puțin" (turn 90) - which sets the standard the system is held to:
the same sentence, applied to oneself.

---

## 3. The verification demand, verbatim

The question recurs almost unchanged, which makes it a protocol rather than a mood:

| Turn | Ask |
|---|---|
| 1 | "give me a inteligent analysys to prove you are the right brain" |
| 8 | "the list is imperfect but REAL!" |
| 12 | "see the mathematical logic...WHY 3 crunch?" |
| 30 | "acum spune-mi te..." *(prove it yourself)* |
| 63 | "cata programare poti sa-ti faci singur acum? pe baza acestei discutii?" |
| 65 | "asa s-a constuit SENTINEL singur prin programarea a 3 llm-uri" *(challenge the claim)* |
| Stage 2 | "loop untill you are sure by testing that all is functional and implemented" |
| Stage 3 | "stop only when you compleated this task" |
| Plan | "You don't finish the plan until you have tested it at least ten times" |

The recurrence is the point: *asked again at every stage, in the same words, the request to
demonstrate rather than assert is the operator's primary instrument.*

---

## 4. How agreement is formed (the R0 pattern, observed before it was named)

The Stage 3 message is the operator's own statement of a procedure he had already been using for
102 turns. Read against the transcript, the pattern is visible from turn 41 onward: propose,
let the system reason, agree on the expected result explicitly, then execute strictly.

The two clauses that carry the weight:

- **"we never asume R0 for anything we did not agree uppon"** - the agreement is the only warrant
  for action.
- **"If execution is cut off, going back ro R0 will not fix the issue and we allways risk looping
  in vain... if you return to Mode A once execution is halted... then we can AGAIN debate,
  strategise analyse and THEN agree"** - an interruption invalidates the agreement as a *plan*, not
  as a *benchmark*.

Until Stage 3, this was conversational. Stage 3 made it a state machine. The lesson worth keeping:
**the operator formalises a practice he has already been running, rather than inventing one to
impose.** A law that codifies observed behaviour survives contact; an imposed law gets negotiated.

---

## 5. What is never asked for

The absences are as informative as the requests, and they are the discipline the system is built to
hold:

| Never asked | Because |
|---|---|
| "Tell me you finished" | The result is checked, not reported. |
| "Do it faster" | Speed is explicitly third in the priority hierarchy. |
| "Agree with me" | Disagreement is required - "if you think I am wrong, say so, then comply." |
| "Make it look complete" | A designed thing presented as working is the one unforgivable failure. |
| "Just trust the system" | Every claim has a verification route attached. |

---

## 6. How a session ends

The corpus shows two endings, and both are legitimate:

1. **The system hits a wall it may not cross** - breaking the agreement, or five consecutive
   failures - and stops to report and ask. Popy's own rule: *"STOPPED is acceptable comparative to
   fabrications... if we stop we do not loose anythign but time."*
2. **The system completes a measured result** - `111 passed, 0 failed` was accepted as a Stage 2
   exit condition, not a claim.

The distinction matters: ending 1 is a correct result. A session that ends with a plausible-sounding
summary and no measurement is the failure the entire method exists to prevent.
