# Planning Mode: Guidelines for Implementation Plans and Learning Proposals

Planning is the foundation of high-quality agentic software engineering. An agent must never write code or execute modifying operations without first establishing a clear, validated, and approved plan.

---

## 1. The Research Phase (Pre-Planning)
Before writing the plan, the agent must perform comprehensive, read-only research:
1. **Analyze Constraints**: Read global rules (`AGENTS.md`) and project-scoped rules.
2. **Scan Codebase**: Use `view_file` to read imports, constants, configuration files, and API structures.
3. **Map Dependencies**: Understand how files relate to each other.
4. **NO DESTRUCTIVE ACTIONS**: Running edit tools or modifying commands is strictly forbidden during research.

---

## 2. Choosing the Plan Type
The agent must choose between two planning artifacts based on user intent:

| Plan Type | When to Use | Target Filename (Index) |
| :--- | :--- | :--- |
| **Implementation Plan** | Major refactoring, structural changes, new features, or architectural adjustments. | `implementation_plan-{YYYY-MM-DD_HH-mm-ss}.md` |
| **Learning Proposal** | Triggered by the `/learn` slash command to capture and persist reusable behaviors, rules, or corrections. | `learning_proposal-{YYYY-MM-DD_HH-mm-ss}.md` |

---

## 3. Formatting Guidelines

### A. Implementation Plan Structure
The plan must contain:
1. **Goal Description**: Detailed summary of what the plan accomplishes.
2. **User Review Required**: Critical design decisions, breaking changes, or permissions needed. Highlight using alerts:
   > [!IMPORTANT]
   > Critical architectural constraints or prerequisites
3. **Open Questions**: Clear questions that clarify design intent.
4. **Proposed Changes**: Grouped by component (e.g. CLI, desktop, database). Explicitly list files with `[NEW]`, `[MODIFY]`, or `[DELETE]`. Link files using `file:///` absolute paths.
5. **Verification Plan**: List of automated tests (commands) and manual checks.

### B. Learning Proposal Structure
The proposal must contain:
1. **Classification**: Outline of the rules or skills being learned.
2. **Rationale**: Why this learning is necessary, and what past failures/successes it addresses.
3. **Precise Text Additions/Diffs**: Showing the exact contents of the new/updated `SKILL.md` or modifications to `AGENTS.md`.

---

## 4. central Index Logging
* All plans/proposals must be copied to:
  `C:\Users\apviz\Documents\Antigravity_Folder\Antigravity_Projects\Implementation_Plan_Index`
* Naming format:
  * `implementation_plan-{YYYY-MM-DD_HH-mm-ss}.md`
  * `learning_proposal-{YYYY-MM-DD_HH-mm-ss}.md`
* Use UTF-8 encoding. Create the folder if it is missing.
