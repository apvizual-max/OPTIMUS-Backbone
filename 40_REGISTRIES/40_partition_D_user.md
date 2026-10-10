# Registry — Partition D: (User)

**Role**: Popy's personal content partition.

## Known SENTINEL material locations

| Path | Content | Scan status |
|---|---|---|
| `D:\Alex_Knowlege_Vault\` | Top-level vault (root of personal knowledge) | 🟡 not yet scanned (depth too broad without sub-target) |
| `D:\Alex_Knowlege_Vault\03_Resources\` | Resources layer | 🟡 not yet scanned |
| `D:\Alex_Knowlege_Vault\03_Resources\03_7-SENTINEL_Character\` | SENTINEL Character assets | ✅ top-level structure verified 2026-09-18 |

## SENTINEL_Character — discovered structure (top-level, verified 2026-09-18)

The SENTINEL_Character directory is a multimodal asset vault — audio, video, brain imagery, character portraits, photo seeds, scenes, and 2 mind-map PNGs at the root.

| Folder | Content | Status |
|---|---|---|
| `AUDIO/` | 4 Romanian-language `.m4a` files on proverbs, Optimus logic, rituals, sovereign AI architecture | ✅ enumerated |
| `BRAIN/` | Sentinel Brain design — 6 numbered markdown docs + main PNG + sub-folders `Elements/`, `IMAGES - Sentinel Brain/`, `VIDEOS - Sentinel Brain/` | ✅ enumerated |
| `CHARACTER/` | Character portraits (Gemini-generated + custom) — 8 files at top level | ✅ enumerated |
| `Photo Seeds/` | 8 photo seeds for character generation (Gemini + custom) | ✅ enumerated |
| `SCENES/` | 4 scene renders (AI command center, futuristic gateway, holographic grid) | ✅ enumerated |
| `VIDEO/` | 17+ video files (Sentinel Prime AI strategic brain, cybernetic brain, neural conduits, etc.) | ✅ enumerated |
| `Sentinel Character - Mind Map.png` | Mind map (small) | ✅ |
| `Sentinel Character - Mind Map (large).png` | Mind map (large) | ✅ |

## Scan policy

- Targeted scans only. Default depth = 3.
- Read-only — Mavis does not write into D: without explicit R0.
- Each scan triggers a JURNAL_OGLINDA entry below.

## JURNAL_OGLINDA

| Date | Event | Notes |
|---|---|---|
| 2026-09-18 | Registry created | Initial scaffold; first targeted scan pending Popy R0 |
| 2026-09-18 | SENTINEL_Character top-level enumerated | 6 sub-folders + 2 root PNG mind maps + ~70 asset files. AUDIO has 4 Romanian-language m4a files on proverbs/Optimus/rituals. VIDEO has 17+ cinematic clips. BRAIN has 6 numbered design docs + extensive image/video library. CHARACTER has Gemini-generated portraits + custom photo seeds. |

## Open questions for Popy (R0)

1. What other top-level folders exist on D: that Mavis should know about (e.g., `D:\Projects\`, `D:\Archive\`)?
2. Is the path spelling `Alex_Knowlege_Vault` (sic) intentional, or a typo for `Alex_Knowledge_Vault`? Confirm before relying on it.
3. Should Mavis auto-include new top-level folders in this registry when discovered, or only on Popy's say-so?
