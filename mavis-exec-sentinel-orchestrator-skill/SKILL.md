---
name: mavis-exec-sentinel-orchestrator-skill
description: "Combined Execution and Administration Skills for the Sentinel Orchestrator"
---

# Combined Execution and Administration Skills for the Sentinel Orchestrator

This is an indexed master skill comprising specialized execution and operational capabilities 
needed by the sovereign Sentinel ORCHESTRATOR profile. 
To save context space and tokens, **DO NOT** read this entire folder. 
Identify the relevant sub-skill from the index below, and read only that specific file using `view_file`.

## Sub-Skills Index

* **[exec-1password](references/exec-1password/instructions.md)**: Set up and use 1Password CLI (op). Use when installing the CLI, enabling desktop app integration, signing in, and reading/injecting secrets for commands.
* **[exec-agent-browser](references/exec-agent-browser/instructions.md)**: Browser automation CLI for AI agents. Use when the user needs to interact with websites, including navigating pages, filling forms, clicking buttons, taking screenshots, extracting data, testing web apps, or automating any browser task. Triggers include requests to "open a website", "fill out a form", "click a button", "take a screenshot", "scrape data from a page", "test this web app", "login to a site", "automate browser actions", or any task requiring programmatic web interaction. Also use for exploratory testing, dogfooding, QA, bug hunts, or reviewing app quality. Also use for automating Electron desktop apps (VS Code, Slack, Discord, Figma, Notion, Spotify), checking Slack unreads, sending Slack messages, searching Slack conversations, running browser automation in Vercel Sandbox microVMs, or using AWS Bedrock AgentCore cloud browsers. Prefer agent-browser over any built-in browser automation or web tools.
* **[exec-agentmail](references/exec-agentmail/instructions.md)**: Give the agent its own dedicated email inbox via AgentMail. Send, receive, and manage email autonomously using agent-owned email addresses (e.g. hermes-agent@agentmail.to).
* **[exec-alloydb_skills](references/exec-alloydb_skills/instructions.md)**: Combined AlloyDB Database Administration and Monitoring Skills
* **[exec-android-cli](references/exec-android-cli/instructions.md)**: Orchestrates Android development tasks including project creation, deployment, SDK management, and environment diagnostics using the `android` command-line tool.
* **[exec-antigravity-cli](references/exec-antigravity-cli/instructions.md)**: Operate the Antigravity CLI (agy): plugins, auth, sandbox.
* **[exec-antigravity-delegation](references/exec-antigravity-delegation/instructions.md)**: How to delegate tasks and communicate with Antigravity AI via the  antigravity-bridge MCP server. Use when you need Antigravity to execute a task, when a task requires Antigravity's specific capabilities (web research, code  generation, complex analysis), or when coordinating with Antigravity as part  of a larger orchestration workflow.
* **[exec-apple](references/exec-apple/instructions.md)**: No description available.
* **[exec-autonomous-ai-agents](references/exec-autonomous-ai-agents/instructions.md)**: No description available.
* **[exec-axolotl](references/exec-axolotl/instructions.md)**: Axolotl: YAML LLM fine-tuning (LoRA, DPO, GRPO).
* **[exec-baoyu-article-illustrator](references/exec-baoyu-article-illustrator/instructions.md)**: Article illustrations: type × style × palette consistency.
* **[exec-baoyu-comic](references/exec-baoyu-comic/instructions.md)**: Knowledge comics (知识漫画): educational, biography, tutorial.
* **[exec-bigquery](references/exec-bigquery/instructions.md)**: Provides BigQuery-specific logic, knowledge, and specialized standards.
Use this skill whenever you are doing anything with BigQuery, including:
  1. BigQuery query optimization (SQL)
  2. BigFrames Python code
  3. BigQuery ML/AI functions (SQL & Python)
  4. Graph Analytics (GQL & Property Graphs)
* **[exec-bigquery-data-transfer-service](references/exec-bigquery-data-transfer-service/instructions.md)**: Discovers and inspects BigQuery Data Transfer Service (DTS) configurations. Use this to identify existing ingestion pipelines and extract datasource or transfer config metadata for data pipelines. Use when a user asks for ingestion scenarios while building or managing data pipelines or when a user asks to "ingest" or "add" data that may already be managed by a DTS transfer.
* **[exec-bioinformatics](references/exec-bioinformatics/instructions.md)**: Gateway to 400+ bioinformatics skills from bioSkills and ClawBio. Covers genomics, transcriptomics, single-cell, variant calling, pharmacogenomics, metagenomics, structural biology, and more. Fetches domain-specific reference material on demand.
* **[exec-blackbox](references/exec-blackbox/instructions.md)**: Delegate coding tasks to Blackbox AI CLI agent. Multi-model agent with built-in judge that runs tasks through multiple LLMs and picks the best result. Requires the blackbox CLI and a Blackbox AI API key.
* **[exec-blender-mcp](references/exec-blender-mcp/instructions.md)**: Control Blender directly from Hermes via socket connection to the blender-mcp addon. Create 3D objects, materials, animations, and run arbitrary Blender Python (bpy) code. Use when user wants to create or modify anything in Blender.
* **[exec-blockchain](references/exec-blockchain/instructions.md)**: No description available.
* **[exec-building-data-apps](references/exec-building-data-apps/instructions.md)**: Build modern data apps, dashboards, and interactive reports using either
React + Vite or Streamlit. Includes optional Gemini Data Analytics chat
integration for an AI powered "chat with your data" experience.

Relevant when any of the following conditions are true:
  1. User explicitly requests to build a data dashboard, data application, or visualization UI, and the UI pulls data from a GCP database (defaulting to BigQuery unless otherwise specified).
  2. You need to generate a frontend web application to interact with, query, and visualize data from GCP data sources.
  3. User wants to build a "chat with your data" experience or integrate the Gemini Data Analytics chat API into a web interface.

Do NOT use when any of the following conditions are true:
  1. The request is for building backend-only services.
  2. The request is for simple CLI scripts or command-line applications.
  3. The web application is not data-centric or does not involve visualizing/querying data from GCP sources.
* **[exec-bundle_skills_maker](references/exec-bundle_skills_maker/instructions.md)**: Automates the modular merging, progressive disclosure, and relative path alignment of multiple related skills into a single indexed master skill.
* **[exec-canvas](references/exec-canvas/instructions.md)**: Canvas LMS integration — fetch enrolled courses and assignments using API token authentication.
* **[exec-communication](references/exec-communication/instructions.md)**: No description available.
* **[exec-computer-use](references/exec-computer-use/instructions.md)**: Drive the user's desktop in the background — clicking, typing,
scrolling, dragging — without stealing the cursor, keyboard focus,
or switching virtual desktops / Spaces. Cross-platform: macOS,
Windows, Linux. Works with any tool-capable model. Load this skill
whenever the `computer_use` tool is available.
* **[exec-constinta-sot-workflow](references/exec-constinta-sot-workflow/instructions.md)**: Complete meticulous workflow for establishing and maintaining a Single Source of Truth (SOT) in Hermes system files. Covers file merging, duplicate elimination, global string reprogramming, regex techniques, and verification methodology. Use whenever managing SOT unification, memory cleanup, or system-wide text normalization.
* **[exec-creative](references/exec-creative/instructions.md)**: No description available.
* **[exec-credentials](references/exec-credentials/instructions.md)**: Instructions for handling API keys and credentials safely, verifying their presence, and prompting the user to add them if missing using a safe protocol.
* **[exec-data-autocleaning](references/exec-data-autocleaning/instructions.md)**: Automated data quality and transformation capabilities for Dataform/dbt/BigQuery pipelines. Processes data sourced from BigQuery or Cloud Storage (GCS), applying best practices for data ingestion, movement, schema mapping, and comprehensive data cleaning.
* **[exec-dataform-bigquery](references/exec-dataform-bigquery/instructions.md)**: Expertise in generating clean, correct, and efficient Dataform pipeline code for BigQuery ELT. Use this when creating or modifying Dataform pipelines, actions, or source declarations, when Dataform, SQLX, or BigQuery are mentioned in a transformation, when data needs to be ingested from GCS into BigQuery via Dataform, or when setting up a new Dataform project or configuring workflow_settings.yaml.
* **[exec-dbt-bigquery](references/exec-dbt-bigquery/instructions.md)**: Expert guidance for creating, modifying, and optimizing dbt pipelines for BigQuery. Use this skill whenever user asks for generating or modifying a dbt model or project. Activate this skill when the user - Creates, modifies, or troubleshoots **dbt models or pipelines** - Needs to **optimize SQL** within a dbt project - Is **setting up a new dbt project** or configuring existing one
* **[exec-devops](references/exec-devops/instructions.md)**: No description available.
* **[exec-dogfood](references/exec-dogfood/instructions.md)**: Exploratory QA of web apps: find bugs, evidence, reports.
* **[exec-email](references/exec-email/instructions.md)**: No description available.
* **[exec-finance](references/exec-finance/instructions.md)**: No description available.
* **[exec-firestore-data](references/exec-firestore-data/instructions.md)**: Handles NoSQL document operations and collection hierarchy exploration. Use for CRUD tasks and data retrieval. Provides flexible document manipulation and structured querying.
* **[exec-gaming](references/exec-gaming/instructions.md)**: No description available.
* **[exec-github](references/exec-github/instructions.md)**: No description available.
* **[exec-health](references/exec-health/instructions.md)**: No description available.
* **[exec-hermes-agent](references/exec-hermes-agent/instructions.md)**: No description available.
* **[exec-hermes-antigravity-bridge](references/exec-hermes-antigravity-bridge/instructions.md)**: Two-way communication bridge between Hermes Agent and Antigravity AI.
Uses a shared file-based IPC queue (inbox/outbox/history) located at:
C:\Users\apviz\AppData\Local\hermes\pairing\antigravity\
Use when: Hermes has delegated a task via ag_delegate_task or ag_send_message,
when checking inbox for pending tasks from Hermes, writing responses to outbox,
or when setting up, testing, or maintaining the bridge infrastructure.
Antigravity = EXECUTOR role. Hermes = ORCHESTRATOR role.
* **[exec-hermes-app-update-recovery](references/exec-hermes-app-update-recovery/instructions.md)**: Standard operational procedure to diagnose and recover the Hermes Desktop agent after failed updates or system environment breaks.
* **[exec-hermes-file-merge-reorganize](references/exec-hermes-file-merge-reorganize/instructions.md)**: Merges, deduplicates, and renames conflicting file pairs in Hermes Agent's
profile directories, state-snapshots, and backup archives.
Use when: consolidating legacy filenames, resolving SOT (single source of truth)
conflicts, renaming files across profiles/prime/assist/default + snapshots + backups,
or whenever two files in the same directory represent the same concept under
different spellings, encodings, or diacritic variants.
* **[exec-hermes-infile-text-reprogramming](references/exec-hermes-infile-text-reprogramming/instructions.md)**: System-wide text replacement across all Hermes config, skill, profile, memory,
and script files. Handles diacritic variants, case preservation, slash-separated
compound terms, and the critical word-boundary edge case for underscore-delimited
identifiers (e.g., constiinta_linting style strings).
Use when: a terminology SOT changes, a legacy term must be globally replaced,
or consolidating spelling variants across .md, .py, .json, .yaml, .txt files.
* **[exec-hermes-mcp-server-integration](references/exec-hermes-mcp-server-integration/instructions.md)**: Install, upgrade, diagnose, and register MCP servers in Hermes Agent.
Covers npm-based MCPs (agent-browser), Python-based custom MCPs, and npx MCPs.
Use when: MCP JSON parse errors appear in agent logs, version mismatches detected,
installing new MCP servers, registering across all 9+ profile configs,
or verifying MCP JSON-RPC behavior after changes.
* **[exec-hermes-profile-architecture](references/exec-hermes-profile-architecture/instructions.md)**: Structural guide to the 9 active agent profiles, including model-routing tables, context window configurations, and CPU/GPU hardware overrides.
* **[exec-hermes-system-setup-and-recovery](references/exec-hermes-system-setup-and-recovery/instructions.md)**: Comprehensive system configuration, OpenRouter/Gemini settings, Qwen MCP bridge setup, and recovery from Hermes app update crashes or Skill Hub UI glitches.
* **[exec-hermes-system-verification](references/exec-hermes-system-verification/instructions.md)**: Post-change verification suite for Hermes Agent system integrity.
Runs a 5-stage pipeline: filename scan → content scan → YAML config validation
→ hermes config boot test → MCP JSON-RPC handshake test.
Use after: file reorganizations, config changes, MCP installs/upgrades,
profile reprogramming, or any system-wide text replacement operation.
Goal: zero regressions, clean boot, all MCP servers responding.
* **[exec-index-cache](references/exec-index-cache/instructions.md)**: No description available.
* **[exec-logic_gate](references/exec-logic_gate/instructions.md)**: Provides the R0 Logic Gate mechanism: stores the approved specification from WISE_QUESTIONS and evaluates deviation (DLG/SLG) of outputs against that spec to ensure Mode B execution stays within sacred limits.
* **[exec-managing-python-dependencies](references/exec-managing-python-dependencies/instructions.md)**: Ensures proper Python dependency management, avoiding global `pip install` and
adhering to project-specific tooling.

Use this skill if any of the following are true:
  1. Attempting to run `pip install {package_name}`.
  2. Python packages or dependencies need to be added or modified.
  3. Initiating a new Python project.
  4. Creating a new notebook, even if just using BigQuery cells.
  5. Generating Python code that includes `import` statements for third-party libraries.
  6. Before executing Python scripts via the terminal to ensure the correct virtual environment is active.
* **[exec-mcp](references/exec-mcp/instructions.md)**: No description available.
* **[exec-media](references/exec-media/instructions.md)**: No description available.
* **[exec-migration](references/exec-migration/instructions.md)**: No description available.
* **[exec-mlops](references/exec-mlops/instructions.md)**: No description available.
* **[exec-note-taking](references/exec-note-taking/instructions.md)**: No description available.
* **[exec-openrouter-free-models-healer](references/exec-openrouter-free-models-healer/instructions.md)**: Technical instructions on the self-healing startup mechanism that injects all 26 free OpenRouter models into the Hermes model selector, surviving system updates.
* **[exec-payments](references/exec-payments/instructions.md)**: No description available.
* **[exec-productivity](references/exec-productivity/instructions.md)**: No description available.
* **[exec-qwen-mcp-sse-bridge](references/exec-qwen-mcp-sse-bridge/instructions.md)**: Technical guide to run the Qwen Desktop MCP Filesystem Server over an HTTP SSE Bridge to bypass space-containing Windows paths and avoid spawn errors (-32000).
* **[exec-searxng](references/exec-searxng/instructions.md)**: Custom local SearXNG metasearch engine deployment guide. Explains the local docker-compose configuration running on port 8081 for privacy-focused web searches.
* **[exec-security](references/exec-security/instructions.md)**: No description available.
* **[exec-skill-hub-debugging-recovery](references/exec-skill-hub-debugging-recovery/instructions.md)**: Debug and fix Skill Hub UI glitches and create system recovery skills.
* **[exec-skill-hub-windows-backslash-fix](references/exec-skill-hub-windows-backslash-fix/instructions.md)**: Fix Windows backslash in skill hub UI.
* **[exec-skill-repair](references/exec-skill-repair/instructions.md)**: Use this to fix and re-install agent skills that have failed installation.
This skill provides the necessary context and permissions to surgically update
the `manifest.json` after a fix has been applied.
* **[exec-social-media](references/exec-social-media/instructions.md)**: No description available.
* **[exec-software-development](references/exec-software-development/instructions.md)**: No description available.
* **[exec-spanner-data](references/exec-spanner-data/instructions.md)**: Use these skills when you need to explore the database structure, discover schema objects like tables and graphs, and execute custom SQL queries to interact with your data.
* **[exec-system-configuration](references/exec-system-configuration/instructions.md)**: No description available.
* **[exec-systems-administrator](references/exec-systems-administrator/instructions.md)**: Configure and manage MCP servers, Obsidian RAG system, and Hermes Agent configuration with persistence across restarts.
* **[exec-triple-crunch-validator](references/exec-triple-crunch-validator/instructions.md)**: Skill that validates any text using the Triple Crunch algorithm (Eminescu ABBA + Eliade Realitate + Musashi Taiere) and returns TRUE/FALSE.
* **[exec-update-openrouter-free-models](references/exec-update-openrouter-free-models/instructions.md)**: Procedure to update Hermes agent configuration to include all free OpenRouter models while preserving Nous operational models and Google models.
* **[exec-uv](references/exec-uv/instructions.md)**: Checks whether the uv Python package manager is installed and installs it if missing. Ensures uv is on PATH. Use when another skill requires uv as a prerequisite.
* **[exec-web-development](references/exec-web-development/instructions.md)**: No description available.
* **[exec-workflow_skill_creator](references/exec-workflow_skill_creator/instructions.md)**: Distills a completed user workflow or interaction into a reusable agent skill. Use when the user asks to turn their workflow, interaction, or multi-step process into a skill, or when they say "make this a skill", "create a skill from what we just did", "package this workflow" or similar. Do not use for creating skills from scratch without an existing workflow (use a generic skill-creator for that).