# Hermes Elite Minimalist Plugin Design System (Obsidian Telemetry Dark — Master SOT)

> **Authoritative Master Specification & Living Single Source of Truth (SOT)**  
> **Reference Implementation**: `design-system` (v1.0.0)  
> **Target Environment**: Hermes Desktop App (Electron / React / Tailwind CSS / VS Code Codicons)  
> **Status**: Living Production Standard

---

## 1. Design Philosophy & Vision

The **Hermes Elite Minimalist Plugin Design System** (*Obsidian Telemetry Dark*) resolves the fundamental challenge of high-density AI telemetry: **delivering comprehensive, real-time diagnostic information without visual clutter, boxiness, or cognitive fatigue.**

In traditional plugin designs, developers frequently wrap every label, badge, and metric inside nested bordered boxes ("boxes inside boxes"). Over time, this leads to visual claustrophobia, layout misalignment, and a cramped user experience.

This design system establishes a unified standard across all Hermes plugins based on:
1. **Typographic Discipline (Max 3 Fonts)**
2. **Strict Unboxing (Negative Space & Bullet Dot Separators `•`)**
3. **8-Color Non-Overlapping Chromatic Wheel**
4. **Single-Shade Elevation (`rgba(18, 20, 26, 0.78)`)**
5. **Action Cockpit Layout (Button on top, text underneath)**

```
┌────────────────────────────────────────────────────────────────────────┐
│                        CORE DESIGN PILLARS                             │
├────────────────────────┬───────────────────────┬───────────────────────┤
│    STRICT UNBOXING     │ FAIL-SAFE COLOR MAP   │ SINGLE-SHADE ELEVATION│
│ No boxes inside boxes. │ Inline hex styles to  │ Dropdown drawers must │
│ Typography & dot dots  │ bypass Tailwind build │ differ by one shade & │
│ replace container tags │ pruning in Electron.  │ feature left accents. │
├────────────────────────┼───────────────────────┼───────────────────────┤
│   MAX 3 FONT FAMILIES  │ PERSISTENT ICONS      │ ACTION COCKPIT PATTERN│
│ UI Sans, Monospace,    │ Codicons always retain│ Single horizontal row;│
│ Display Header Sans    │ vibrant signature hue │ button top, text under│
└────────────────────────┴───────────────────────┴───────────────────────┘
```

---

## 2. The 3 Authoritative Typography Families (Max 3 Fonts)

To guarantee visual harmony and prevent arbitrary font bloat, exactly 3 font families are permitted:

| Font Family ID | Name | CSS Fallback Chain | Role & Purpose |
| :--- | :--- | :--- | :--- |
| **`sans`** | **UI Primary Sans** | `system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif` | Primary interface typography for UI controls, navigation labels, descriptions, and conversational prose. |
| **`mono`** | **Telemetry Monospace** | `ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', monospace` | Precision technical data: container IDs, hashes, timestamps, memory stats, JSON payloads, and ports. |
| **`display`** | **Display Header Sans** | `'Trebuchet MS', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif` | Cockpit titles, uppercase section headers, and prominent KPI ratio numbers. |

### Authoritative 6-Tier Text Size Hierarchy Scale (Goal Judge SOT Reference)

The text size scale is strictly anchored to the **Goal Judge** plugin as the definitive operational SOT reference point. All plugins must draw exclusively from these 6 standardized tiers:

| Tier | Size | Tailwind Token | Weight & Family | Goal Judge SOT Reference | Operational Role & Usage |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1. KPI Hero Counter** | `24px` | `text-2xl` | Extrabold (`800`) `mono` | KPI Hero Counters (`Total Tracked: 24`, `🔴 Active: 1`, `⚪ Done: 11`) | Prominent numerical readouts, large KPI metrics, active counts, turn budgets. |
| **2. Header Cockpit Title** | `14px` | `text-sm` | Bold (`700`) `display` / `sans` | HeaderCockpit Title (`⚖️ Goal Judge & Ralph Loop`) & Session Headline | Top-level pane cockpit titles, modal dialog headlines, discussion session titles. |
| **3. Primary Action & Body** | `12px` | `text-xs` | Semibold (`600`) / Regular (`400`) `sans` | Primary Action Cockpit Buttons (`[ See Active Goal ]`) & Objective Prose | Cockpit action buttons, form inputs, goal objective descriptions, standard prose. |
| **4. SectionHeader Title** | `11px` | `text-[11px]` | Bold (`700`) `display` / `mono` | SectionHeader Titles (`RALPH LOOP ACTION COCKPIT`) & Session IDs | Uppercase SectionHeader titles, form field labels, monospace session identifier tags. |
| **5. Action Subtext & Chips** | `10px` | `text-[10px]` | Normal (`400`) / Semibold (`600`) `mono` | Action Subtext (`Launch /goal`) & Micro Status Chips (`ACTIVE`, `v2.3.0`) | Action button subtext, micro status badges, version chips, category pill tags. |
| **6. Micro Caption & Meta** | `9px` | `text-[9px]` | Medium (`500`) uppercase `mono` | SectionHeader Subtitle (`AUTONOMOUS GOAL TRACKING & VERIFICATION...`) | Uppercase tracking-widest subtitles, micro timestamps, technical IDs, breadcrumbs. |

#### Negative Space Invariant
Whenever drawing cards or drawers featuring left chromatic accent borders (such as 3px solid `#ef4444` or `#22d3ee`), an explicit negative space of **`padding: '12px 14px 12px 18px'`** or **`paddingLeft: '22px'`** MUST be enforced to prevent visual collision between text and border lines.

---

## 3. The 8-Color Chromatic Token Wheel

| Token ID | Name | Signature Hex | Background Tint (14%) | Border Tint (45%) | Ambient Glow | Codicon | Typical Domain |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`cyan`** | **Cyan** | `#22d3ee` | `rgba(6, 182, 212, 0.14)` | `rgba(6, 182, 212, 0.45)` | `0 0 14px rgba(6, 182, 212, 0.35)` | `terminal` | Coding / AST / Antigravity |
| **`emerald`** | **Emerald** | `#34d399` | `rgba(16, 185, 129, 0.14)` | `rgba(16, 185, 129, 0.45)` | `0 0 14px rgba(16, 185, 129, 0.35)` | `server-process` | Running / Health / Gordon |
| **`purple`** | **Purple** | `#c084fc` | `rgba(168, 85, 247, 0.14)` | `rgba(168, 85, 247, 0.45)` | `0 0 14px rgba(168, 85, 247, 0.35)` | `database` | Databases / Qwen Local |
| **`amber`** | **Gold / Amber** | `#fbbf24` | `rgba(245, 158, 11, 0.14)` | `rgba(245, 158, 11, 0.45)` | `0 0 14px rgba(245, 158, 11, 0.35)` | `graph` | Reasoning / Warning / Fallback |
| **`pink`** | **Pink** | `#f472b6` | `rgba(236, 72, 153, 0.14)` | `rgba(236, 72, 153, 0.45)` | `0 0 14px rgba(236, 72, 153, 0.35)` | `comment-discussion` | Vision / Media / Mavis AI |
| **`blue`** | **Azure Blue**| `#60a5fa` | `rgba(59, 130, 246, 0.14)` | `rgba(59, 130, 246, 0.45)` | `0 0 14px rgba(59, 130, 246, 0.35)` | `tools` | Workspace / Docker Desktop |
| **`orange`** | **Orange** | `#fb923c` | `rgba(249, 115, 22, 0.14)` | `rgba(249, 115, 22, 0.45)` | `0 0 14px rgba(249, 115, 22, 0.35)` | `zap` | Observability / Restarting |
| **`indigo`** | **Indigo** | `#818cf8` | `rgba(99, 102, 241, 0.14)` | `rgba(99, 102, 241, 0.45)` | `0 0 14px rgba(99, 102, 241, 0.35)` | `server` | Core Host / Filesystem |

---

## 4. The Strict Unboxing Protocol ("No Boxes Inside Boxes")

- **Rule**: Never wrap individual metadata fields in separate bounded boxes.
- **Pattern**: Format metadata as an inline sequence of monospace text nodes separated by bullet dots (`•`).
- **Progress Tracks**: Always borderless `h-1.5 rounded-full bg-white/10 overflow-hidden`.
- **Dividers**: Eliminate unnecessary horizontal rules; use vertical line rhythm (`space-y-3`) and negative space.
- **Border Disappearance**: Outer card boundaries and living specimens must never display harsh visible bounding strokes (`border-white/[0.07]`, `border-white/10`, `border-red-500/20`). Use `border border-transparent` or borderless containers to eliminate the "boxes inside boxes" appearance. Nested inner element borders (`border border-white/5`), inner dividers (`border-t`, `border-b`), and inset highlights (`inset 0 1px 0`) are prohibited in favor of discrete background elevation (`rgba(18, 20, 26, 0.78)` or `bg-black/40`).

---

## 5. Fail-Safe Inline Styling Protocol (Tailwind Purge Mitigation)

In packaged Electron applications, Tailwind's compiler purges utility classes with arbitrary opacity or dynamic colors not present in the host application template.
- **Mitigation**: All dynamic visual styling MUST declare explicit hex color strings and bind them directly via React inline `style`:
```jsx
style: {
  backgroundColor: 'rgba(37, 99, 235, 0.28)',
  borderColor: 'transparent',
  color: '#bfdbfe',
  boxShadow: '0 0 14px rgba(59, 130, 246, 0.30)'
}
```

---

## 6. Single-Shade Dropdown Elevation

Dropdown drawers and collapsible details:
1. Elevate background by exactly one subtle shade: `backgroundColor: 'rgba(18, 20, 26, 0.78)'`.
2. Anchor with a **3px solid left vertical accent line** matching the component's signature chromatic hue: `borderLeft: '3px solid #22d3ee'`.
3. Elevation box shadow: `boxShadow: '0 4px 16px rgba(0, 0, 0, 0.25)'` (inset 1px top highlight lines are eliminated to prevent harsh horizontal strokes on warm/high-contrast monitors).
4. Negative space padding: Explicit left padding `18px` or `22px` (`padding: '16px 16px 16px 22px'`) to create generous breathing room between the 3px vertical accent line and interior typography.

---

## 7. Action Cockpit Layout Invariant

For actionable button panels:
- Centered section header: `text-center uppercase font-bold text-zinc-300 tracking-wider`.
- Distributed horizontally in a single row (`grid grid-cols-3 gap-3 sm:gap-6`).
- Interactive button positioned strictly **ON TOP**.
- Explanatory title & subtitle stacked cleanly **UNDER** the button.

---

## 8. Rule 07: Border Disappearance & Seamless Elevation

Layout containers must never rely on visible bounding strokes ("boxes inside boxes"). Use `border-transparent` or seamless elevation (`bg-black/40`, `rgba(18, 20, 26, 0.78)`) and single-sided chromatic left anchors (`borderLeft: 3px solid <hex>`). Layout hierarchy is communicated purely through negative space, vertical rhythm, and contrast.

---

## 9. Four-Group Layout Architecture & Vertical Spacing Hierarchy

For complex gallery views, cockpits, and multi-component plugin tabs, elements must be organized into 4 distinct, cohesive layout groups separated by generous vertical rhythm rather than harsh bounding lines:

1. **Group 1: Execution & Action Cockpits** (Standard 3-Button Cockpits, Steering Intervention Drawers, Trigger Panels).
2. **Group 2: Telemetry Readouts & Progress Gauges** (Unboxed Metric Strips with bullet dot separators `•`, Ratio Bars, Turn Budget Loopers & Consumption Meters).
3. **Group 3: Interactive Surfaces & Navigation Controls** (Filter Pills Bar, 7-State Goal Judge Status Matrix, Single-Shade Elevated Drawers, Criteria & Subgoals Checklists).
4. **Group 4: Adversarial Evaluation & Audit Logs** (Verdict Proof Banners Approved/Rejected, Completed Goals Chronological Feeds & Audit Cards).

### Spacing & Typography Invariants:
- **Root Separation**: `space-y-8` with fail-safe inline flex `gap: '36px'` and `paddingBottom: '48px'` between major layout groups.
- **Intra-Group Separation**: `space-y-4` with fail-safe inline flex `gap: '20px'` between group header and components within each group.
- **Fail-Safe Purge-Proof Spacing**: Because Tailwind utility classes (e.g. `space-y-8`, `space-y-2.5`, `gap-2.5`) are purged in packaged Electron desktop builds, all layout containers must declare inline flex styles (`display: 'flex', flexDirection: 'column', gap: ...`) to guarantee robust vertical rhythm.
- **Elevated Specimen Enclosures**: Individual specimens are housed in single-shade elevated cards (`rgba(18, 20, 26, 0.78)`), `borderRadius: '12px'`, `padding: '16px 18px'`, and `boxShadow: '0 4px 16px rgba(0, 0, 0, 0.25)'` to establish clear visual hierarchy.
- **Group Headers**: `ComponentGroupHeader` featuring a 16px Codicon, Display Header Sans uppercase title (`text-xs sm:text-sm font-bold`), explanatory subtitle (`text-[11px] text-zinc-400`), a monospace specimen counter badge (`text-[10px] font-mono font-semibold px-2 py-0.5 rounded bg-white/5 text-zinc-400 border border-white/10`), with fail-safe inline `paddingBottom: '12px'`, `marginBottom: '4px'`, and `borderBottom: '1px solid rgba(255, 255, 255, 0.08)'`.
- **Goal Judge SOT Readability Scale**:
  - Section headers: `text-sm font-bold uppercase tracking-wider`
  - Body text / prose: `text-xs sm:text-[13px] text-zinc-300 leading-relaxed`
  - Action buttons: `text-xs font-semibold py-2 px-3`
  - Status badges: `text-xs font-bold`
  - Telemetry readouts: `text-xs font-mono`
  - KPI Hero counters: `text-2xl font-extrabold font-mono` (24px)

