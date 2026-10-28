---
aliases:
  - Operational Input/Output Blueprint
---
# OPERATIONAL INPUT / OUTPUT BLUEPRINT (PHASE 1)

This document maps out the precise data specifications, folder structures, and system execution boundaries required to run your simplified Phase 1 Application System at maximum quality.

## 1. The Core Input: Step 0 Raw Ingestion Specification

To achieve a $100\%$ accuracy rate in your adapted CVs and letters, the raw listings you feed into the daily chat session must not just be copy-pasted wall-to-wall text. They need a basic, consistent structural metadata block at the top of each listing.

When you scrape or extract a job, format it in `JD's_SOT_Report.md` using the exact layout below before initiating **Step 1 (Scoring)**.

### The Raw JD Entry Template

```
## JD_ENTRY_[ID_NUMBER]
### METADATA
- **Company Name**: [Verbatim Name - used for folder creation and Letter variables]
- **Target Role**: [e.g., Senior UI/UX Designer / Senior Art Director]
- **Job Posting Date**: [YYYY-MM-DD - preserved for sorting]
- **Location**: [Bucharest | Remote | Hybrid | Other City]
- **Engagement Type**: [Full-Time | Contract / B2B | Part-Time]
- **Contact/Source**: [e.g., Robert - HR (from phone screen/LinkedIn) | LinkedIn Job Board]
- **User Specific Notes**: [Optional: Any specific detail from a phone discussion, e.g., "Designing enterprise web app for electricity market operations / energy trading."]

### RAW JOB DESCRIPTION
[Paste the raw text of the Job Description here]
```

### Why this specific input data is required for maximum quality:

1. **The Company Name** is parsed by the local system to automatically generate your physical folders on disk.
    
2. **The Target Role** determines which link array is pulled from `ALEX_LINK_MATRIX.json` (e.g., UI-UX, Design, Photo, Video).
    
3. **The User Specific Notes** act as the ultimate strategic "hook" for `LETTER_ENGINE.json`. If you paste a phone-screen note mentioning that the company is dealing with "energy trading and grid visualization," the letter will immediately pivot on that precise stress point, ensuring the output reads as a highly tailored, custom pitch rather than a generic template.

## 2. Step 1 Staging Output: `JD's_SOT_Report.md`

After you feed the raw list of $50+$ JDs into your daily chat session, the local AI executes `jd_scoring.json` and completely overwrites `JD's_SOT_Report.md`.

- **Storage Path**: `D:\Alex - KV Obsidian\- ALEX - KV\ALEX-Folder\1 - Alex - CV and Person\JOB Aplications\JD's_SOT_Report.md`
    
- **Format**: It automatically groups all JDs that survived the circuit breakers into your **4 sorted sections** (Section 1: Master Stream, Section 2: Contracts, Section 3: Mid-Level, Section 4: Out-of-Location), topped with a generated table of contents indexing the day's targets.
    
- **Metadata Attachment**: Every surviving listing in this report is now stamped with its calculated compatibility score and its commercial category tag: `[B2B]`, `[B2C]`, or `[DTC]`.

## 3. The Target Application Deliverables (Step 4)

Once you select your batch of $5$ to $10$ target JDs from the report, the automated loop runs. For every selected job, the AI generates a dedicated local folder and compiles the final deliverables.

### The Directory Structure

The system creates a new physical folder named strictly after the **Company Name** (extracted from your Step $0$ metadata block):

- **Target Folder Path**:
    
    `D:\Alex - KV Obsidian\- ALEX - KV\ALEX-Folder\1 - Alex - CV and Person\JOB Aplications\[Company_Name]\`
    

### The Deliverables Inside the Folder

Inside that company folder, exactly two final documents are generated:

#### 1. `[Company_Name]_CV.pdf` (The Personalized CV)

- **Format**: PDF format (preserving layout, margins, and $3 \times 3$ grid integrity).
    
- **Top 30% Mutation**: Personalized Headline, Professional Summary (with metrics), Areas of Expertise ($3 \times 3$ grid with balanced hard/soft skills), and Key Achievements (metric-heavy hooks matching the JD's requirements).
    
- **Deterministic Links**: Dynamic links mapped from `ALEX_LINK_MATRIX.json` directly matching the sub-disciplines requested in the JD are injected into your contact/experience blocks.
    
- **Frozen Experience**: Your chronological career history and **Testimonial 1** (Kevin Donlan's recommendation) remain perfectly frozen at the bottom.

#### 2. `[Company_Name]_LETTER_OF_INTENT.md` (The Strategic Letter)

- **Format**: Markdown format (`.md`), easily editable before compiling to PDF if needed.
    
- **Content Strategy**: A concise, direct, single-page strategic pitch answering the core question _"Why Hire Alex?"_ (without printing the question). It maps the company's commercial stress points (`[B2B]/[B2C]/[DTC]`) directly to your past metrics.
    
- Verbatim Recommendation: Ends with the verbatim transcription of **Testimonial 2** (Bert Konings' HMS Networks recommendation) appended directly at the floor.

## 4. Have We Met All Initial Plan Requirements?

**Yes.** We have successfully mapped the inputs and outputs to match your exact goals while stripping away all computational waste:

| Initial Plan Requirement          | Simplified Status           | Implementation Details                                                                                                                               |
| --------------------------------- | --------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Step 0 Bulk Ingestion**         | **Preserved & Optimized**   | You input $50+$ unstructured JDs. They are cleaned and structured locally.                                                                           |
| **Scoring & Restructuring**       | **Preserved**               | Surviving JDs are scored on $4$ axes and sorted into your $4$ target sections.                                                                       |
| **Company Research (Old Step 2)** | **Deferred to Phase 2**     | Eliminates rate-limits and Cloudflare captcha blocks. Deep research only happens if you land an interview.                                           |
| **"Why hire Alex?" Section (CV)** | **Preserved & Integrated**  | Dropped as a separate block; instead, the entire CV Header and Letter are designed as a single, cohesive answer to this question.                    |
| **Testimonial Matching**          | **Preserved & Streamlined** | Fixed as $2$ elite testimonials: Testimonial 1 at the footer of your CV, Testimonial 2 at the floor of your Letter of Intent. No programmatic drift. |
| **Output Directories**            | **Preserved**               | The system creates one folder per company named `[Company_Name]` inside your standard job application path.                                          |
| **Deliverables Set**              | **Streamlined to 2 Files**  | You get exactly the customized CV in PDF and the Letter in MD in each target folder.                                                                 |
|                                   |                             |                                                                                                                                                      |
### Conclusion & Quick Summary of Edits
I have compiled the complete system manual into `operational_io_blueprint.md`. This manual explicitly defines:
1. **The Step 0 Input Structure** (How to format your raw JDs to get the highest-quality output).
2. **The Staging Report Path** (`JD's_SOT_Report.md`).
3. **The Folder Location and Deliverables Name Matrix** (Ensuring that your updated CV PDF and Letter are organized exactly in `...\JOB Aplications\[Company_Name]\`).

---
