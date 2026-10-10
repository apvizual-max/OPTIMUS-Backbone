# Plugin Design System Replication Guide (Obsidian Telemetry Dark)

> **Universal 6-Step Implementation Playbook**  
> **Source of Truth**: `C:\Users\apviz\AppData\Local\hermes\desktop-plugins\design-system\`  
> **Target Audience**: Plugin Authors & AI Engineering Assistants

---

## Overview

This guide provides an end-to-end checklist and step-by-step methodology to replicate the **Obsidian Telemetry Dark** design system across any Hermes desktop plugin. Following these 6 steps guarantees 100% design consistency, prevents build-time CSS purge bugs in Electron, and eliminates the "boxes-inside-boxes" layout anti-pattern.

```
┌────────────────────────────────────────────────────────────────────────┐
│                        6-STEP REPLICATION PLAYBOOK                     │
├───────────────┬───────────────┬───────────────┬───────────────┬────────┤
│ Step 1        │ Step 2        │ Step 3        │ Step 4        │ Step 5 │
│ Scaffold      │ Standardize   │ Import 8-Color│ Unbox Metadata│ Deploy │
│ Design_Schema │ 3 Fonts       │ Chromatic Map │ & Clean Rails │ Cockpit│
└───────────────┴───────────────┴───────────────┴───────────────┴────────┘
                                                                    │
                                                                 Step 6:
                                                              Validate &
                                                             Automate Tests
```

---

## Step 1: Scaffold the `Design_Schema/` Documentation Directory

Every standardized plugin must maintain an internal `Design_Schema/` folder containing its design tokens and documentation:

```powershell
# Create standard design schema directory in plugin root
mkdir -Force "C:\Users\apviz\AppData\Local\hermes\desktop-plugins\<plugin-id>\Design_Schema"
```

The directory must house:
1. `design_schema.json`: Formal JSON tokens schema for the plugin.
2. `DESIGN_SYSTEM.md`: High-level architectural narrative.
3. `COMPONENT_CATALOG.md`: Specific component blueprints used.
4. `REPLICATION_GUIDE.md`: This guide.

---

## Step 2: Enforce the "Max 3 Fonts" Invariant & 6-Tier Typographic Scale (Goal Judge Reference)

Never import external Google Fonts or inject ad-hoc font families. Declare the standard font system constants at the top of your `plugin.js`:

```javascript
const FONT_SYSTEM = {
  sans: "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif",
  mono: "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', monospace",
  display: "'Trebuchet MS', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
};
```

### Typographic Mapping
- **`sans`**: All UI controls, card titles, descriptions, and conversational prose.
- **`mono`**: Container IDs, port numbers, memory stats, JSON attributes, micro-badges, and filter pill counts.
- **`display`**: Cockpit titles, uppercase section headers (`text-[11px] font-bold tracking-wider uppercase`).

### Standard 6-Tier Typographic Scale (Goal Judge SOT)
Always draw sizes strictly from the 6 standardized tiers anchored to the **Goal Judge** plugin:
1. `24px` (`text-2xl font-extrabold font-mono`): KPI Hero Counters (`Total Tracked: 24`, `🔴 Active: 1`, `⚪ Done: 11`).
2. `14px` (`text-sm font-bold font-display`): Header Cockpit Title (`⚖️ Goal Judge & Ralph Loop`) & session headlines.
3. `12px` (`text-xs font-semibold/normal font-sans`): Primary Action Buttons (`[ See Active Goal ]`) & body prose.
4. `11px` (`text-[11px] font-bold font-display/mono`): SectionHeader Titles (`RALPH LOOP ACTION COCKPIT`) & session IDs.
5. `10px` (`text-[10px] font-mono`): Action button subtext (`Launch /goal`) & micro status badges (`ACTIVE`, `v2.3.0`).
6. `9px` (`text-[9px] font-mono uppercase tracking-widest`): SectionHeader subtitles & technical micro metadata.

### Negative Space Invariant
When applying chromatic vertical left accents (e.g. `borderLeft: '3px solid #...'`), always specify explicit negative space padding: **`padding: '12px 14px 12px 18px'`** or **`paddingLeft: '22px'`**.

---

## Step 3: Integrate the 8-Color Chromatic Token Wheel

To prevent Tailwind CSS compiler purge failures in packaged Electron builds, import and reference the standardized chromatic wheel with explicit inline hex, background tint, border tint, and ambient glow values:

```javascript
const CHROMATIC_TOKENS = {
  cyan: {
    hex: '#22d3ee',
    bg: 'rgba(6, 182, 212, 0.14)',
    border: 'rgba(6, 182, 212, 0.45)',
    glow: '0 0 14px rgba(6, 182, 212, 0.35)',
    codicon: 'terminal'
  },
  emerald: {
    hex: '#34d399',
    bg: 'rgba(16, 185, 129, 0.14)',
    border: 'rgba(16, 185, 129, 0.45)',
    glow: '0 0 14px rgba(16, 185, 129, 0.35)',
    codicon: 'server-process'
  },
  purple: {
    hex: '#c084fc',
    bg: 'rgba(168, 85, 247, 0.14)',
    border: 'rgba(168, 85, 247, 0.45)',
    glow: '0 0 14px rgba(168, 85, 247, 0.35)',
    codicon: 'database'
  },
  amber: {
    hex: '#fbbf24',
    bg: 'rgba(245, 158, 11, 0.14)',
    border: 'rgba(245, 158, 11, 0.45)',
    glow: '0 0 14px rgba(245, 158, 11, 0.35)',
    codicon: 'graph'
  },
  pink: {
    hex: '#f472b6',
    bg: 'rgba(236, 72, 153, 0.14)',
    border: 'rgba(236, 72, 153, 0.45)',
    glow: '0 0 14px rgba(236, 72, 153, 0.35)',
    codicon: 'comment-discussion'
  },
  blue: {
    hex: '#60a5fa',
    bg: 'rgba(59, 130, 246, 0.14)',
    border: 'rgba(59, 130, 246, 0.45)',
    glow: '0 0 14px rgba(59, 130, 246, 0.35)',
    codicon: 'tools'
  },
  orange: {
    hex: '#fb923c',
    bg: 'rgba(249, 115, 22, 0.14)',
    border: 'rgba(249, 115, 22, 0.45)',
    glow: '0 0 14px rgba(249, 115, 22, 0.35)',
    codicon: 'zap'
  },
  indigo: {
    hex: '#818cf8',
    bg: 'rgba(99, 102, 241, 0.14)',
    border: 'rgba(99, 102, 241, 0.45)',
    glow: '0 0 14px rgba(99, 102, 241, 0.35)',
    codicon: 'server'
  }
};
```

---

## Step 4: Execute the Strict Unboxing Protocol

Transform existing nested container layouts:
1. **Remove Nested Box Borders**: Delete `border border-zinc-800 bg-zinc-900` wrappers around individual metadata items.
2. **Replace with Bullet Dots**: Format item streams as:
   ```jsx
   <div className="text-[11px] font-mono text-zinc-400 flex flex-wrap items-center gap-1.5">
     <span>PORT: <span className="text-zinc-200">8080</span></span>
     <span className="text-zinc-600">•</span>
     <span>MEM: <span className="text-emerald-400">412 MB</span></span>
     <span className="text-zinc-600">•</span>
     <span>STATUS: <span className="text-cyan-400">HEALTHY</span></span>
   </div>
   ```
3. **Elevate Dropdown Drawers**: For collapsible model cards or container details drawers, set:
   ```jsx
   style={{
     backgroundColor: 'rgba(18, 20, 26, 0.78)',
     borderLeft: `3px solid ${accentHex}`,
     padding: '16px 16px 16px 22px',
     boxShadow: '0 4px 16px rgba(0, 0, 0, 0.25)'
   }}
   ```
4. **Border Disappearance & Seamless Elevation (Rule 07)**: Outer card frames and specimen containers must never render harsh visible bounding strokes (`border-white/[0.07]`, `border-white/10`, `border-red-500/20`). Use `border border-transparent` or borderless styling. Layout hierarchy is communicated purely through discrete background elevation (`rgba(18, 20, 26, 0.78)` or `bg-black/40`), chromatic 3px left vertical anchors (`borderLeft: '3px solid <hex>'`), and generous negative space padding (`padding: '16px 16px 16px 22px'`).
5. **Eliminate Inset Highlights & Inner Dividers**: Prohibit `inset 0 1px 0` in `boxShadow` (which renders as harsh 1px top highlight lines on warm displays) and eliminate unnecessary `border-t`/`border-b` horizontal dividing rules within cards. Rely on vertical line rhythm (`space-y-3`, `pt-2.5`) instead.

---

## Step 5: Implement the Action Cockpit Standard

For primary trigger actions and quick commands, deploy the standardized single horizontal row pattern:

1. **Title**: Centered, uppercase, Display font.
2. **Layout**: `grid grid-cols-3 gap-3` (or `grid-cols-2` if 2 items).
3. **Button Position**: Button strictly on top.
4. **Explanatory Subtext**: Centered directly below the button in `text-[10px] text-zinc-400`.
5. **Inline Fail-Safe**: Provide explicit `bg`, `border`, and `glow` so the button retains its vibrant color in all themes.

---

## Step 6: Create & Run Empirical Test Verification (`tests.js`)

Never ship visual or architectural refactors without automated verification. Author a lightweight, zero-dependency Node test script (`tests.js`) asserting:
1. Syntax correctness (`node --check plugin.js`).
2. Inclusion of `FONT_SYSTEM` with exactly 3 font keys.
3. Presence of all 8 chromatic tokens with valid hex strings.
4. Single-shade elevation `rgba(18, 20, 26, 0.78)` presence.
5. Action Cockpit grid pattern (`grid-cols-3`).

Execute via:
```powershell
node tests.js
```

---

## Replication Invariant Checklist

- [ ] `Design_Schema/` directory exists with all 4 reference documents.
- [ ] No more than 3 font families utilized.
- [ ] Explicit inline hex colors used for all chromatic elements (Tailwind purge-safe).
- [ ] No nested boxes inside cards; metadata uses bullet dots (`•`).
- [ ] Dropdown drawers utilize `rgba(18, 20, 26, 0.78)` and 3px left vertical accents.
- [ ] Action buttons are horizontal single row, button on top, text underneath.
- [ ] Automated tests pass 100% with zero errors.
