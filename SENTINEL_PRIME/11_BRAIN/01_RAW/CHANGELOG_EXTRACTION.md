# CHANGELOG - corpus extraction

- generated: `2026-10-04T22:08:35.205640`
- corpus file: `01_RAW/corpus_full.jsonl`
- corpus sha256: `e4d3cbb7795560e1d2e668108bf98cc999c648feb0f18ba81620f911ba7e0e42`
- input records read: **1384**
- unique messages emitted: **955**
- verbatim tier (never cut): **692874 bytes**
- source verbatim text bytes: **692874**
- verbatim retention ratio: **1.0**

## Two-tier retention

TIER 1 VERBATIM - every user and assistant message in full. This tier is what
"nothing is cut" governs. Assistant thinking is retained in a separate field.

TIER 2 EVIDENCE - toolCall and toolResult records are indexed with a bounded
preview and a pointer to their freeze file. Their payloads stay on disk; inlining
them would let command output drown the reasoning that produced it.

## Generations consumed (in chronological order)

| gen | file | records | verbatim | evidence | compaction | verbatim bytes |
|---|---|---|---|---|---|---|
| 0 | `g000000000000--ctx_37af7a78-fd43-4d43-a86d-7ef75b0d3da0.jsonl` | 63 | 26 | 37 | 0 | 283292 |
| 1 | `g000000000001--ctx_351b78f4-1c97-4346-92bf-a30570474913.jsonl` | 226 | 106 | 120 | 0 | 382513 |
| 2 | `g000000000002--ctx_dab90d6f-9270-4a9b-8b56-45b809eb814c.jsonl` | 71 | 46 | 25 | 0 | 205321 |
| 3 | `g000000000003--ctx_d1dbe691-4d67-4551-89e7-72a37eb73eeb.jsonl` | 65 | 36 | 28 | 1 | 245506 |
| 4 | `g000000000004--ctx_b3d7fee6-0a6c-4a02-bbc9-0002598b44da.jsonl` | 312 | 194 | 118 | 0 | 376617 |
| 5 | `g000000000005--ctx_6c5422e5-8fe5-43fe-aa3f-7438ac2bf326.jsonl` | 176 | 80 | 95 | 1 | 187951 |
| 6 | `messages.jsonl` | 42 | 16 | 25 | 1 | 233836 |

## Integrity checks

| id | check | status | detail |
|---|---|---|---|
| `anchor` | first verbatim message is message zero | **OK** | If I buy a subscription, can I use MiniMax as my Hermes Agent's brain? I really need a sup |
| `seq` | seq is a dense 1..N sequence | **OK** | 955 messages |
| `dedupe` | every message_id is unique in the corpus | **OK** | 955 ids, 955 unique |
| `verbatim_retention` | emitted verbatim text >= 95% of extracted source text | **OK** | emitted=692874 source=692874 ratio=1.0000 |
| `no_silent_drop` | every source record is output or explicitly excluded | **OK** | parse_errors=0 no_message_id=0 scaffolding_only=12 |
| `user_turns` | unique user turns >= the largest single generation | **OK** | unique_user_turns=102 max_per_generation=38 |
| `language_law` | Romanian wisdom text preserved verbatim in the corpus | **OK** | diacritics found in verbatim tier |

## Excluded records (explicit, never silent)

- **excluded_scaffolding_only**: 12
  - `g000000000001--ctx_351b78f4-1c97-4346-92bf-a30570474913.jsonl:71 msg-xUZOwX9mbH1QQpcd9qCHZEIZDDIVwxW1YY4vYE1n_m4`
  - `g000000000002--ctx_dab90d6f-9270-4a9b-8b56-45b809eb814c.jsonl:71 msg-xUZOwX9mbH1QQpcd9qCHZEIZDDIVwxW1YY4vYE1n_m4`
  - `g000000000002--ctx_dab90d6f-9270-4a9b-8b56-45b809eb814c.jsonl:346 msg-pj7pxMHsoWmsimU2n9ZhAYeFSB2nqYv_kpopES5BkfE`
  - `g000000000004--ctx_b3d7fee6-0a6c-4a02-bbc9-0002598b44da.jsonl:69 msg-bQGDKELFGQb2gqHlQzFggM6NGBOAza0poKva7K2RAJk`
  - `g000000000004--ctx_b3d7fee6-0a6c-4a02-bbc9-0002598b44da.jsonl:329 msg-XLtMavtOduDZ-ACtZiIKKUa-zEahCWJ-Amful8kcdYY`
  - `g000000000005--ctx_6c5422e5-8fe5-43fe-aa3f-7438ac2bf326.jsonl:90 msg-PF9X4A0R0mZzW_pjbg1D83U65QnVAYC-IsM0Q58u9aw`
  - `g000000000005--ctx_6c5422e5-8fe5-43fe-aa3f-7438ac2bf326.jsonl:124 msg-WyjDR5AOVWTVRzyfQ6Sx2rs0QDT3YWBB1E9aPoqc098`
  - `g000000000005--ctx_6c5422e5-8fe5-43fe-aa3f-7438ac2bf326.jsonl:137 msg-sVjE6y4tBJJ6LIk7uHd-D-GrmnvuBEi8DMxVzAOrfj8`
  - `g000000000005--ctx_6c5422e5-8fe5-43fe-aa3f-7438ac2bf326.jsonl:138 msg-3Md_ZCCMWslAxMFkBAxFHJ57XD8W8GgqxR7tQ1yC7tk`
  - `g000000000005--ctx_6c5422e5-8fe5-43fe-aa3f-7438ac2bf326.jsonl:172 msg-DbWFR1h4MqFFV1XUsIIqLEcJNY5QZnNsIBSzyNvi2N8`
  - `g000000000005--ctx_6c5422e5-8fe5-43fe-aa3f-7438ac2bf326.jsonl:182 msg-AkEGzEMHNxoB6La0dT2yZ-CxiKdluYpIT_1X6AakGHo`
  - `messages.jsonl:38 msg-hnnVCIjvO8sk2r-QvER11fhAktBDcvAW29JpqQbBTC8`

## Per-message provenance

Every record in `corpus_full.jsonl` carries a `source` object with `generation`, `file` and `line`, so any message can be traced back to the exact frozen line it came from, and any frozen line can be traced forward.

## Idempotency

Re-running the extractor against the same frozen input produces a byte-identical `corpus_full.jsonl`. Verify with:

```powershell
python 08_SELF_IMPROVEMENT\corpus_extractor.py verify
```
