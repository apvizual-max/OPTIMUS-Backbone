# Tasking Mode: Guidelines for Task Checklists (`task.md`)

A task checklist is the operational engine that ensures mechanical execution precision. It acts as the agent's external memory, allowing it to resume work flawlessly after interruptions.

---

## 1. Initial Creation
* Immediately after receiving user approval (R0 gate) on the Implementation Plan or Learning Proposal, the agent must create `task.md` in the workspace or local brain.
* The checklist must contain all files and actions from the plan, broken down into granular, actionable checklist items.

---

## 2. Formatting and States
The checklist uses the following syntax to track execution states:

* `- [ ]` **Uncompleted**: Task is planned but not started.
* `- [/]` **In Progress**: Task is currently being worked on. *Only one or a small group of related items should be in-progress at a time.*
* `- [x]` **Completed**: Task is finished and verified.

### Structuring Example:
```markdown
- [/] Develop Coder Profile Skills
  - [x] Bundle file-safety skills into `exec-sentinel-coder`
  - [/] Create script folder and add validation helpers
  - [ ] Update manifest entries
- [ ] Verify execution
```

---

## 3. Handling Interruption and Context Resumption
Because agent executions can be interrupted due to tokens limit, timeouts, or system resets:
1. **Always Check task.md First**: At the start of a session or after an interruption, the first step is to read `task.md` to identify the current in-progress (`[/]`) and pending (`[ ]`) items.
2. **Keep it Updated**: Update `task.md` continuously as you complete steps.
3. **No Drift**: Ensure your actions remain strictly aligned with the tasks checklist. If requirements change mid-task, update the checklist first.

---

## 4. Central Index Logging
* Every time `task.md` is created or modified, a duplicate copy must be written to:
  `C:\Users\apviz\Documents\Antigravity_Folder\Antigravity_Projects\Tasks_Index`
* Filename format: `tasks-{YYYY-MM-DD_HH-mm-ss}.md`
* Use UTF-8 encoding. Create the folder if it is missing.
