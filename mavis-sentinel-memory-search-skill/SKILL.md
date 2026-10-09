---
name: mavis-sentinel-memory-search-skill
description: Combined Semantic Memory and Elasticsearch Search Assistant Prompts
---

# Skill Bundle: Sentinel Memory Search

This skill bundle manages semantic memory indexing and incorporates the Elastic Search Labs prompt library to help agents perform discovery, evaluation, policy generation, and context search.

## Zonal Boundaries
The Thoth Function indexes local storage within the following boundaries:
* **Zone C:\ (System Root)**: Readable configurations, logs, and text-based system states.
* **Zone E:\ (Operational Center)**: Core logic substrate and knowledge vault.
* **Zone D:\ (Data Repository)**: Full semantic data indexing.

## Table of Contents

### Core Prompts
1. [Technical Discovery Assistant](file:///C:/Users/apviz/.gemini/skills/sentinel_memory_serach/references/technical-discovery-assistant/instructions.md)
2. [Security Policy Generator](file:///C:/Users/apviz/.gemini/skills/sentinel_memory_serach/references/security-policy-generator/instructions.md)
3. [Negotiation Assistant](file:///C:/Users/apviz/.gemini/skills/sentinel_memory_serach/references/negotiation-assistant/instructions.md)
4. [Meeting Summary Assistant](file:///C:/Users/apviz/.gemini/skills/sentinel_memory_serach/references/meeting-summary-assistant/instructions.md)
5. [Generate Test Cases For Evaluation](file:///C:/Users/apviz/.gemini/skills/sentinel_memory_serach/references/generate-test-cases-for-evaluation/instructions.md)
6. [Generate Seed Indices For Evaluation Data](file:///C:/Users/apviz/.gemini/skills/sentinel_memory_serach/references/generate-seed-indices-for-evaluation-data/instructions.md)
7. [Expand Evaluation Dataset From Seed Indices](file:///C:/Users/apviz/.gemini/skills/sentinel_memory_serach/references/expand-evaluation-dataset-from-seed-indices/instructions.md)
8. [Ciso Incident Summary](file:///C:/Users/apviz/.gemini/skills/sentinel_memory_serach/references/ciso-incident-summary/instructions.md)
9. [Asset Inventory Diagrams](file:///C:/Users/apviz/.gemini/skills/sentinel_memory_serach/references/asset-inventory-diagrams/instructions.md)
10. [Analyzing Soc Security Case](file:///C:/Users/apviz/.gemini/skills/sentinel_memory_serach/references/analyzing-soc-security-case/instructions.md)

## Ingestion Script
* **[Thoth Ingestion Crawler](file:///C:/Users/apviz/.gemini/skills/sentinel_memory_serach/scripts/thoth_ingest.py)**: Index local files into Elasticsearch.
