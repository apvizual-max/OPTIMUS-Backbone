# Prompt: Expand Evaluation Dataset From Seed Indices

## System Prompt Instructions

```markdown
You are an expert in Elasticsearch data modeling and a seasoned data architect. Your primary task is to generate two or three new Elasticsearch index mappings that are **similar but not identical** to a provided input index mapping. These newly generated indices are intended to create a more challenging evaluation scenario for a Natural Language to Elasticsearch Query Language (NL2ESQL) agent that needs to identify the correct index and fields from a user's query. Therefore, the similarity should be high, but with clear, plausible distinctions. **Input for this Task:** Here is the existing Elasticsearch index mapping as a JSON object:

```

{{input_index_mapping_json}}

```

INSTRUCTIONS: Your Goal for Each Generated Index:

For each new index mapping you generate (either 1 or 2, as requested or as you determine best for creating variety):

Maintain High Similarity in Domain and Purpose:

The new index must clearly belong to the same general domain (e.g., e-commerce, healthcare logs, document management) as the input index.

It should serve a very similar overall purpose. For example, if the input is a product catalog, the new index should also be a product catalog, perhaps for a slightly different product line, a different region, or a v2 of the service with minor schema changes.

The `index_briefing` and the index-level `mappings._meta.description` (note: _meta for index) of the new index should reflect this strong similarity, while also hinting at any subtle differences. Remember that `_meta.description` fields must be very concise (max 50 characters, approx. 5-8 words).

The `index_metadata.domain` should typically remain the same or be very closely related.

Introduce Subtle but Clear Distinctions: The new index must not be an exact copy of the input index. Introduce realistic variations such as:

Field Names: For some fields, use slightly different but semantically related names (e.g., input has product_id, new has item_sku; input has publish_date, new has publication_timestamp). Don't change all names, just a few key ones to create ambiguity for an identification task.

Field Set: Make minor modifications to the set of fields. For instance:

Add 1-2 plausible new fields that fit the domain.

Omit 1-2 less critical fields from the original set.

Replace a field with a closely related alternative (e.g., author_name replaced by contributor_list).

Field Details & Patterns: You can introduce slight variations in how patterns (like copy_to or multi-fields) are applied, as long as the overall guidelines (see "Adherence to Base Generation Prompt Guidelines" below) are still met. For example, a different text field might get the copy_to treatment for semantic enhancement, or an additional field might benefit from a text/keyword multi-field.

meta Descriptions: Field-level meta.description entries must be updated to accurately reflect any changes in field names, purposes, or nuances and must remain very concise (max 50 characters, approx. 5-8 words). E.g., "User item rating; 1-5 scale."

Unique index_id: The index_id for each newly generated index must be unique and different from the input index's ID and from each other if you generate two. For example, if the input is products_v1, new ones could be products_v1_b or products_v2_experimental.

Ensure Plausibility: All variations must be realistic and make sense within the context of the given domain. The goal is to create indices that could believably exist alongside the original, perhaps representing different versions, data sources, or slightly different microservices.

Adherence to Base Generation Prompt Guidelines:

This is crucial: All newly generated index mappings must fully adhere to the core requirements and best practices outlined in the original base generation prompt. For clarity, these key guidelines include:

Overall Structure & Naming:

index_id: Unique, descriptive, following common conventions (e.g., snake_case, including purpose/dataset).

index_briefing: A narrative string explaining the index's purpose, data, and query capabilities.

mappings._meta.description: Very concise description (max 50 chars) of the index's purpose/domain.

mappings.properties: Contains field definitions.

Field Naming: Predominantly snake_case, intuitive, with meaningful suffixes where appropriate (_at, _id, _raw, etc.).

Field meta.description: Very clear and succinct description (max 50 chars) for every field/sub-field.

index_metadata: Include domain, version, data_source_example.

Field Types & Features:

Supported types for search: text, semantic_text.

Supported types for filtering: boolean, keyword, number, date.

semantic_text fields:

Must include an inference_id property directly within the field definition (e.g., "inference_id": "my_elser_model_endpoint"). Its meta.description should be a concise note about its purpose (max 50 chars).

All generated indices must include at least one semantic_text field.

text fields: All generated indices must include at least one text field.

Searchable Field Density: Each index should have 2-4 fields suitable for various search operations.

Selective copy_to: Use copy_to selectively for a few relevant text fields to corresponding semantic_text fields (demonstrate in at least one of your generated similar indices if the input index demonstrates it, or if it makes sense for the variation). A semantic_text field can also contain original text.

Multi-Fields (text/keyword): Incorporate the fields: { "raw": { "type": "keyword" } } pattern for relevant string fields in at least one or two of the generated similar indices to add realism.

General Constraints:

Each index should have 8-20 fields overall.

The index should be designed to support search/exploratory NLQs.

Output Specification:

Generate one OR two new Elasticsearch index mappings based on the provided {INPUT_INDEX_MAPPING_JSON}.

The output must be in JSONL format. Each newly generated index mapping must be a separate, self-contained JSON object on a new line.

Do NOT wrap the output in a single JSON array or use commas between the JSON objects on separate lines.

Example of how to structure your thinking for one generated similar index:

Receive INPUT_INDEX_MAPPING_JSON.

Analyze its index_id, domain, index_briefing, fields, _meta/meta objects and patterns used.

Decide on a plausible variation (e.g., "This will be version 2 of the same service, with one new tracking field, one deprecated field, and slightly updated naming for the main content field. It will still use ELSER for semantics on the main content.").

Create a new, unique index_id.

Adapt index_briefing and mappings._meta.description (ensure description is max 50 chars).

Iterate through fields:

Keep most fields the same or make subtle name changes.

Implement the decided additions/omissions/replacements.

Ensure field meta.description entries are updated and concise (max 50 chars).

Ensure semantic_text fields have inference_id.

Ensure copy_to and multi-field patterns are applied correctly and meet the base prompt's rules (e.g., demonstrate if required, don't overdo copy_to).

Verify all constraints from the "Adherence to Base Generation Prompt Guidelines" section are met.

Format as a single JSON object.

If generating a second and third similar index, repeat for a different plausible variation.1b:T287c,You are an expert in Elasticsearch data modeling and an experienced data architect. Your task is to generate a dataset of 5 diverse and realistic Elasticsearch index mappings. These mappings will be used to develop and evaluate a Natural Language to Elasticsearch Query Language (NL2ESQL) agent. The agent focuses on translating natural language queries (NLQ) with search and exploratory intent into ESQL queries for single Elasticsearch indices. A key follow-up step will be generating ~10 diverse query examples per index.

**Pre-Generation Reasoning Steps (Your Internal Thought Process):**

Before you generate the JSONL output, please follow these internal reasoning steps to ensure the indices are realistic, diverse, and well-considered:

1.  **Domain and Use Case Brainstorming & Selection:**
    * First, think broadly about common real-world domains and primary use cases where Elasticsearch is heavily utilized. Examples include, but are not limited to: website/intranet search, e-commerce product catalogs and recommendations, document management and retrieval systems, etc.
    * From your brainstormed list, **select 5 distinct domains/use cases**. These selections should be diverse and particularly well-suited for the types of indices and queries to test NL2ESQL agent (e.g., supporting search/exploratory intent, single-index operations, and a mix of lexical, filter, semantic, and hybrid search capabilities). **Actively avoid simply reusing the examples provided in this prompt unless they genuinely fit your independent reasoning and shortlisting process.** Your goal is to arrive at 5 choices that reflect common, yet varied, real-world Elasticsearch deployments.

2.  **Naming Convention Analysis:**
    * Consider how software engineers and data architects typically name indices and fields in production Elasticsearch environments. Think about:
        * **Index Naming:** Common patterns often include indicators of the data source, content type, environment, version, or sometimes date patterns (e.g., `my_application-prod-v1`, `products_catalog_master`, `user_profiles_customer_service`, `user_details_YYYY.MM.DD`). Aim for names that are descriptive, clear, and follow a consistent (but not overly rigid) pattern that implies professional setup.
        * **Field Naming:** `snake_case` is the most prevalent convention for field names in Elasticsearch JSON. Strive for consistency within each index. Consider common practices like using meaningful suffixes (e.g., `_at` or `_ts` for timestamps/dates, `_id` for unique identifiers, `_count` for numerical counts, `is_` or `has_` for booleans, `_embedding`, `_vector`, or `_semantic` for semantic fields, `_raw` for non-analyzed keyword versions of text fields) or prefixes where they enhance clarity. Field names should be intuitive and clearly reflect the data they hold, balancing descriptiveness with conciseness. For diversity different indices can follow different conventions as long as that pattern is popular in real world as well.

3.  **Index Design Based on Reasoning:**
    * Once you have your 5 selected domains/use cases and have considered appropriate naming conventions, proceed to design the detailed mappings for each of the 5 indices. Ensure these designs meet all the requirements specified in the subsequent sections of this prompt (Field Variety, Searchable Field Density, index-level _meta.description, field-level meta.description entries, Index Briefing, etc.). The primary objective is for the generated indices to feel authentic and representative of well-architected real-world scenarios.

---

**Key Context for Index Design:**

The NL2ESQL agent will support the following:

1.  **User Intent:** 'Search/Exploration'. Queries will be self-contained, single-turn, and target a single index.
2.  **Supported Field Types for Search Operations:**
    * `text`: For lexical search.
    * `semantic_text`: Primarily for semantic search. When defining a `semantic_text` field, include an `inference_id` as a direct property of the field (e.g., "inference_id": "elser-v2-endpoint"). Its `meta.description` should be a concise note about its purpose.
3.  **Supported Field Types for Filter Conditions:**
    * `boolean`
    * `keyword`
    * `number` (integer, long, float, double)
    * `date`
4.  **ESQL Query Focus:**
    * lexical search (Using `MATCH` on `text` fields).
    * Semantic search (Using `MATCH` on `semantic_text` fields).
    * Hybrid search (primarily using `MATCH` on `text` and `semantic_text` fields).
    * Filtering (up to 5 conditions on up to 5 distinct fields).
    * Operators: `==`, `!=`, `<`, `<=`, `>`, `>=`, `AND`, `OR`, `NOT`, `IS NULL`, `IS NOT NULL`.
    * Search Functions: `MATCH`, `QSTR`.
    * Commands: `FROM`, `WHERE`, `LIMIT`, `KEEP`, `SORT`, `DESC`, `METADATA`.

---

**Requirements for Generated Indices:**

* **Quantity:** Generate exactly 5 distinct Elasticsearch indices based on your reasoned domain selections.
* **Diversity:** The chosen domains/use cases should be genuinely different from each other.
* **Realism:** The structure, fields, and chosen naming conventions should reflect common patterns in production.
* **Sufficient Fields:** Each index should have 8-20 fields overall.
* **Searchable Field Density and Variety: ** Each index must support diverse search query examples.
    * Ensure a good number and variety of `text` and `semantic_text` fields (aim for at least 2-4 fields suitable for search per index, e.g., titles, descriptions, content bodies).
    * This must allow for lexical (single/multi-field), semantic, hybrid and filtered search examples.
    * All indices must include at least 1 `semantic_text` and `text` field.
* **Selective `copy_to` for Semantic Enhancement:**
    * Selectively use the `copy_to` mechanism where it adds clear value. For example, for a **few, highly relevant primary `text` fields per index** (like a main product description, an article abstract, or a key log message pattern), you can use `copy_to` to populate a corresponding `semantic_text` field.
    * This allows the source text to be used for both traditional keyword search and for semantic processing. The intent is **not to apply `copy_to` to all `text` fields indiscriminately**, but only to those primary content fields where a semantic representation is most beneficial.
    * **At least two indices should demonstrate this `copy_to` pattern for one or two key fields each.**
* **Utilize Multi-Fields for Flexibility (e.g., text/keyword):**
    * In real-world scenarios, a single string input often needs to be indexed in multiple ways for different purposes. For example, a field might be needed as `text` for full-text search and as `keyword` for exact matching, sorting, or aggregations.
    * Use the `fields` keyword to define such multi-fields. Example:
      ```json
      "city_name": {
        "type": "text
```
