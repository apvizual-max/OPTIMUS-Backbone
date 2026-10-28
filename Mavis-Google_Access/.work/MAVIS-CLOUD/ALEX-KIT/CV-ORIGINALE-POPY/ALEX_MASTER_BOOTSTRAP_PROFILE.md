# ALEXANDRU POPESCU: MASTER BOOTSTRAP PROFILE (v3.0)

## System State, Logic Rules, and Daily Automation Priming

> **SYSTEM INVARIANT:** This document is the ultimate source of truth (SOT) for Phase 1 of the job application pipeline. Every local execution run, scoring parse, component mutation, and file compilation must strictly conform to the thresholds, layout structures, and anti-hallucination guardrails defined herein.

## 1. Core Profile Boundaries & Metadata

- **Official State Name:** Alexandru Popescu
    
- **Target Seniority Tier:** Senior / Lead / Director-Level ($Exp \ge 20$ years of verifiable industry history).
    
- **Functional Core Competencies:** Art Direction, Creative Leadership, Advertising Campaign Architecture, Commercial Visual Storytelling.
    
- **Secondary Competencies:** Graphic Design, UI-UX Design, Photo Production (Studio, Advertising, Post-Processing), Video Production (Direction, Editing, Short-to-Mid Form).
    
- **Target Industries:** Commercial Advertising, Tech, AI Platforms, Creative Agencies, Crypto, SaaS, DTC Brands.
    
- **Geographic Base:** Bucharest, Romania (Absolute location constraint).
    
- **Work Arrangement Preferences:**
    
    1. Remote ($Remote = \text{True}$)
        
    2. Hybrid or On-Site in Bucharest, Romania
        
- **Engagement Preference Hierarchy:**
    
    1. Full-Time Permanent
        
    2. Contract-based / Project-based (B2B commercial relations)
        
    3. Part-Time
        

## 2. Directory Topography & System Paths

All pipeline outputs, intermediate structures, and target folders must map deterministically to this absolute Windows file system hierarchy:

- **Primary System Root:** `D:\Alex - KV Obsidian\- ALEX - KV\ALEX-Folder\`
    
- **Application Hub Directory:** `D:\Alex - KV Obsidian\- ALEX - KV\ALEX-Folder\1 - Alex - CV and Person\JOB Aplications\`
    
- **Master Base Template:** `D:\Alex - KV Obsidian\- ALEX - KV\ALEX-Folder\1 - Alex - CV and Person\ALEX_MASTER_CV.md`
    
- **Testimonial Database:** `D:\Alex - KV Obsidian\- ALEX - KV\ALEX-Folder\1 - Alex - CV and Person\ALEX_TESTIMONIAL_LETTER.txt`
    
- **Static Portfolio Link Matrix:** `D:\Alex - KV Obsidian\- ALEX - KV\ALEX-Folder\1 - Alex - CV and Person\ALEX_LINK_MATRIX.json`
    
- **Daily Staging File:** `D:\Alex - KV Obsidian\- ALEX - KV\ALEX-Folder\1 - Alex - CV and Person\JOB Aplications\JD's_SOT_Report.md`
    

## 3. Step 1: Programmatic Filtering & Scoring Schema (`jd_scoring.json`)

When a daily raw batch of $N \ge 50$ unformatted JDs is pasted into the chat session, the local AI must execute a strict mathematical scoring loop for each entry.

### A. The Scoring Equation

The total compatibility score ($Score_{Total}$) for each parsed Job Description is calculated using the following linear weighting formula:

$$Score_{Total} = (w_{sen} \cdot S) + (w_{disc} \cdot D) + (w_{loc} \cdot L) + (w_{eng} \cdot E)$$

Where the weights are fixed at:

- $w_{sen} = 0.35$ (Seniority Alignment)
    
- $w_{disc} = 0.30$ (Discipline Alignment)
    
- $w_{loc} = 0.20$ (Location Feasibility)
    
- $w_{eng} = 0.15$ (Engagement Type)
    

### B. Axis Scoring Matrices

#### 1. Seniority ($S$)

- **Senior / Lead / Executive / Director (**$Exp \ge 10$ **years):** $S = 10.0$
    
- **Mid-Level (**$Exp \approx 5$ **years):** $S = 5.0$
    
- **Junior / Entry-Level / Internship / Graduate:** $S = -100.0$ _(Triggers instant Circuit Breaker: Auto-Drop)_
    

#### 2. Discipline ($D$)

- **Art Direction, Creative Direction, Advertising Campaign Lead:** $D = 10.0$
    
- **Graphic Design, UI-UX Design:** $D = 8.0$
    
- **Photo Production, Video Editing, Motion Graphics:** $D = 6.0$
    
- **Emerging Sectors (AI Creative, Crypto, Tech platforms matching core skillsets):** $D = 5.0$
    
- **Un-correlatable Roles (Software Dev, pure Marketing Analytics, Sales):** $D = -100.0$ _(Triggers instant Circuit Breaker: Auto-Drop)_
    

#### 3. Location ($L$)

- **Remote (Any geographic origin):** $L = 10.0$
    
- **On-Site / Hybrid in Bucharest, Romania:** $L = 8.0$
    
- **On-Site / Hybrid outside of Bucharest (Domestic or International):** $L = -5.0$
    
    - _Exceptional Override Rule:_ If seniority is Senior ($S = 10.0$), discipline is core ($D \ge 8.0$), and engagement is high ($E \ge 8.0$), bypass the instant drop and route strictly to Section 4. Otherwise, trigger instant Circuit Breaker: Auto-Drop.
        

#### 4. Engagement ($E$)

- **Full-Time (Employee or B2B Equivalent):** $E = 10.0$
    
- **Contract / Project-Based (B2B):** $E = 8.0$
    
- **Part-Time:** $E = 5.0$
    
- **Internships / Apprenticeships:** $E = -100.0$ _(Triggers instant Circuit Breaker: Auto-Drop)_
    

### C. Commercial Strategy Classifier (Mandatory Metadata)

For every job that passes the circuit breakers, the AI must evaluate the company's business model from the JD text and apply one of three tags:

- `[B2B]`: Target market consists of businesses or corporate entities.
    
- `[DTC]`: The company operates a closed, direct-to-consumer sales model with no middleman.
    
- `[B2C]`: The company sells to consumer groups directly as well as through commercial intermediaries, networks, or proxies.
    

### D. The 4-Section Output Taxonomy

After evaluation, the daily staging file `JD's_SOT_Report.md` must be overwritten with your 4 distinct sections, ordered by score descending:

1. **Section 1: The Master Stream:** Senior-level roles, Bucharest/Remote, sorted highest to lowest score.
    
2. **Section 2: Independent Projects & Contracts:** All project/contract structures, sorted highest to lowest score.
    
3. **Section 3: Under-Seniority Tracking:** Mid-level matches ($\sim 5$ years experience), sorted highest to lowest score.
    
4. **Section 4: Out-of-Location High Scorers:** The exceptional non-local, non-remote roles that scored $\ge 9.0$ on core skill axes.
    

## 4. Step 2: Component Personalization Block Schema (`cv_header_mutator.json`)

When you activate processing for a selected JD, the AI mutates **only** the top header block of `ALEX_MASTER_CV.md`. It must respect these layout boundaries to prevent compile-time visual page overflow:

### A. Layout Blocks & Structural Constraints (Joanna's Tech Talk AI Strategy)

1. **Professional Headline:** Max $10$ words.
    
    - _Constraint:_ Must directly echo the core semantic title of the JD and pair it with your high-level strategic specialization (e.g., _"Senior Art Director — Creative Strategy & Digital Product Design"_). Must fit strictly on $1$ line of text.
        
2. **Professional Summary:** Max $4$ sentences (strictly $\le 80$ words).
    
    - _Constraint:_ Must utilize the **Context-Action-Result (CAR)** metric framework. You must state the operational environment, your strategic action, and the concrete mathematical results matching the primary metrics/pain points emphasized in the JD.
        
3. **Areas of Expertise:** Exactly $9$ key-phrase bullet points structured for a visual $3 \times 3$ grid layout.
    
    - _Constraint:_ Must perfectly map to the technical keywords in the JD. Maintain a balanced $5:4$ or $4:5$ ratio of Hard/Technical Skills to Soft/Strategic Coordinating Skills.
        
4. **Key Achievements:** Exactly $3$ high-impact bullet points.
    
    - _Constraint:_ Each bullet must lead with a bolded skill or parameter and follow the structural formula: **[Key Skill/Project Hook]:** [Task or Project Action] resulting in [Quantifiable Result/Metric wrapped in LaTeX]. Focus heavily on commercial outcomes.
        

### B. Deterministic Portfolio Link Injection

To eliminate broken URLs or system hallucinations, the AI must resolve URLs strictly from your static JSON matrix (`ALEX_LINK_MATRIX.json`).

- _The Injection Rule:_ Analyze the target JD to determine the primary functional discipline track (UI-UX, Design, Print, Photo, Video). Query `ALEX_LINK_MATRIX.json` and pick matching case URLs.
    
- _Strict Invariants:_ The AI is strictly prohibited from writing or inventing a custom URL string. If no exact match is resolved in the matrix, fall back to the base domain 'https://ap-id.ro'. For video or motion graphics requests, write exactly: `'proof of work provided on request'`.
    

## 5. Step 3: Single-Page Letter Engine Schema (`letter_engine.json`)

The synthesized Letter of Intent must function as a high-velocity strategic pitch tailored to a busy human reader, answering _"Why Hire Alex?"_ without printing the prompt.

### A. Core Stylistic Boundaries

- **Tone:** Senior architect-level, highly pragmatic, INTJ-A aligned, and direct.
    
- **Banned Behavior:** No generic introductory fluff (e.g., _"I am writing to express my enthusiastic interest..."_). The letter must immediately address the brand's primary stress point.
    
- **Length Constraint:** Must not exceed $250$ words for the body text, ensuring that when compiled with **Testimonial 2**, the entire document fits comfortably on exactly $1$ page. All numeric and scale parameters must be wrapped in LaTeX formatting.
    

### B. Synthesis Blueprint

1. **The Hook (Paragraph 1):** Directly name the company's probable commercial problem based on their business model (`[B2B]/[B2C]/[DTC]`) and state how your specific economics-aligned creative leadership methodology alleviates it.
    
2. **The Evidence (Paragraph 2):** Provide high-impact metrics from your career history (Shipley Associates, Romexpo, Yokogawa Europe) proving you have resolved this exact scale/speed/quality problem in the past.
    
3. **The AI Accelerator (Paragraph 3):** Position yourself as an AI pioneer who integrates automated pipelines (Ideogram, NanoBanana, Comfy UI, Adobe Firefly, CapCut, Runway) to multiply design throughput and eliminate production latency.
    
4. **The Closer (Paragraph 4):** Leverage your INTJ-A (Architect) logical, problem-solving mindset and prompt a direct technical discussion about their roadmap.
    
5. **The Proof (Testimonial Append):** Drop down two line breaks after the signature block and append the full, unedited markdown blockquote transcription of **Testimonial 2** from `ALEX_TESTIMONIAL_LETTER.txt`.
    

## 6. Daily Session Ingestion Execution Protocol

Every morning, when you initiate the daily chat window, paste this block to prime the AI:

```
SYSTEM BOOTSTRAP INITIATED.
1. Read file ALEX_MASTER_BOOTSTRAP_PROFILE.md.
2. Initialize local MCP file access protocols.
3. Wait for raw Job Description text block input.
4. On input, execute Step 1 Programmatic Filtering & Scoring. Overwrite JD's_SOT_Report.md with the 4-section taxonomy.
5. Pause and await manual batch selection for Step 2 and Step 3 execution.
```