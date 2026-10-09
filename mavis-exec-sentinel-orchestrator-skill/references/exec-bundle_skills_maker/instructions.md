# Sub-Skill: exec-bundle_skills_maker

* **Description:** Automates the modular merging, progressive disclosure, and relative path alignment of multiple related skills into a single indexed master skill.

---

# Bundle Skills Maker Skill

This skill outlines the exact procedure to merge multiple related skill directories into a single indexed master skill using a progressive disclosure architecture. This prevents context bloating and token waste.

## When to Use

Use this skill when:
- The user requests to "bundle skills", "group skills", "merge skills", or "consolidate a group of skills".
- A customizations folder becomes overpopulated, causing context window constraints.

## Step-by-Step Procedure

### 1. Group Identification & Backup
- Identify all source skill directories to be merged.
- **CRITICAL**: Create a full backup of the source folders (e.g., `skills_backup/`) before performing any changes to ensure **zero data loss** (additive editing only).

### 2. Main Index File Creation (`SKILL.md`)
- Create the target master folder (e.g., `exec-group_name` or `think-group_name`).
- Add a master `SKILL.md` in the root containing:
  - Standard YAML frontmatter with `name` matching the folder name, and a high-level `description`.
  - A clean intro text explaining how the progressive disclosure index works.
  - A **Table of Contents (Index)** listing all consolidated sub-skills, with markdown links pointing to their respective `references/[sub-skill-name]/instructions.md` files.

### 3. Modular Relational Subfolder Structure (`references/`)
- Create a `references/` directory in the master folder.
- For each original sub-skill:
  - Create a subdirectory: `references/[sub-skill-name]/`.
  - Extract the original `SKILL.md` file from the backup, strip the YAML frontmatter, and save the content as `references/[sub-skill-name]/instructions.md`.
  - Prepend a simple header identifying the sub-skill name and original description.

### 4. Code and Dependency Integration
- Check if the original sub-skill folders contain helper subfolders (`scripts/`, `examples/`, `resources/`).
- Copy all files from these subfolders into:
  - `references/[sub-skill-name]/scripts/`
  - `references/[sub-skill-name]/examples/`
  - `references/[sub-skill-name]/resources/`
- This ensures all codebase scripts, explanations, and templates are fully preserved inside the modular subfolders without name collisions.

### 5. Path Alignment and Substitution
- In each sub-skill's `instructions.md`, search for any references to local references/exec-bundle_skills_maker/scripts/\1 and update them to reflect the new nested directory structure:
  - Replace `<skill_dir>/references/exec-bundle_skills_maker/scripts/` with `<skill_dir>/references/[sub-skill-name]/scripts/`.
  - Replace `<skill_dir>/references/exec-bundle_skills_maker/examples/` with `<skill_dir>/references/[sub-skill-name]/examples/`.
  - Replace `<skill_dir>/references/exec-bundle_skills_maker/resources/` with `<skill_dir>/references/[sub-skill-name]/resources/`.
  - Adjust any other relative script paths (e.g. `references/exec-bundle_skills_maker/scripts/\1` becomes `references/[sub-skill-name]/references/exec-bundle_skills_maker/scripts/\1`).

### 6. Cleanup & Verification
- Delete the original, individual source skill directories (since they have been fully consolidated and backed up).
- Run a frontmatter syntax validator to ensure all new files parse with 0 errors and have matching `name:` properties.