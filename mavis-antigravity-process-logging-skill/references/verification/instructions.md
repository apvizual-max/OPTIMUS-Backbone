# Verification Mode: Guidelines for Testing, Debugging, and Walkthroughs (`walkthrough.md`)

Verification ensures that the completed work meets the user's requirements exactly, without regression, bugs, or omissions. An agent must verify its own changes before concluding a task.

---

## 1. Automated Verification
Always prioritize automated checks to validate changes:
1. **Syntax Checks**: Parse Python, YAML, JSON, or configuration files to verify correct syntax.
2. **Unit Tests**: Propose and run the project's test commands (e.g. `pytest`, `npm test`).
3. **Dry Runs**: Execute dry runs of scripts to verify file structures and permissions.

---

## 2. Error Digestion and Debugging
If a test or command fails during verification:
1. **Analyze Stack Traces**: Read the error output carefully to locate the exact file name and line number of the failure.
2. **Do Not Hallucinate Fixes**: Check the actual source code at that location before modifying it.
3. **Incremental Fixing**: Make small, targeted modifications and rerun tests immediately.
4. **Update task.md**: If a fix requires additional steps, add them to `task.md` under a `Debugging` section.

---

## 3. Walkthrough Design (`walkthrough.md`)
The walkthrough summarizes the completed work and presents evidence of success.

### Required Sections:
1. **Description of Accomplishments**: A clear, bulleted summary of all changes made.
2. **Files Modified**: Links to all new, modified, or deleted files using `file:///` absolute paths.
3. **Verification Details**:
   - Commands run and their console outputs.
   - Evidence of successful compilations or test runs.
   - Screenshots/recordings (if visual changes were made).
4. **Self-Analytics (Double Check)**:
   - Compare the final state against the user's initial prompt and the approved plan.
   - Confirm that NO user requirements were omitted, and no placeholder code remains.

---

## 4. Central Index Logging
* Every time a walkthrough is created or updated, copy it to:
  `C:\Users\apviz\Documents\Antigravity_Folder\Antigravity_Projects\Walkthrough_index`
* Filename format: `walkthrough-{YYYY-MM-DD_HH-mm-ss}.md`
* Use UTF-8 encoding. Create the folder if it is missing.
