# Component Catalog & Implementation Blueprints (Obsidian Telemetry Dark)

> **Companion Document to `DESIGN_SYSTEM.md` & `design_schema.json`**  
> **Source of Truth**: `C:\Users\apviz\AppData\Local\hermes\desktop-plugins\design-system\`  
> **Target Framework**: React / Tailwind CSS / VS Code Codicons in Hermes Desktop

---

## 1. Architectural Component Registry

This catalog provides production-tested, copy-paste ready React component blueprints adhering strictly to the **Max 3 Fonts Invariant**, **Strict Unboxing Protocol**, **Fail-Safe Inline Styling**, and **4-Group Layout Architecture**.

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                           STANDARDIZED COMPONENT SUITE                           │
├────────────────────────────┬────────────────────────────┬────────────────────────┤
│ SectionHeader              │ ComponentGroupHeader       │ ActionCockpit          │
│ Centered, uppercase        │ Distinct group divider     │ Single horizontal row, │
│ Display font title         │ with Codicon + badge       │ button top, text under │
├────────────────────────────┼────────────────────────────┼────────────────────────┤
│ UnboxedCard                │ ElevatedDrawer             │ FilterPillsBar         │
│ Borderless nested          │ rgba(18,20,26,0.78) with   │ Monospace active chips │
│ metadata with • dots       │ 3px left chromatic strip   │ with persistent icons  │
├────────────────────────────┼────────────────────────────┼────────────────────────┤
│ ProgressGauge              │ VerdictProofBanner         │ CompletedGoalsFeed     │
│ Borderless track with      │ Verifiable proof verdict   │ Chronological Grey SOT │
│ dynamic gradient fill      │ approved / rejected        │ audit log card         │
└────────────────────────────┴────────────────────────────┴────────────────────────┘
```

---

## 2. Component Blueprints & JSX Specifications

### 2.0. `TEXT_SIZE_SYSTEM` (Goal Judge 6-Tier Typographic Scale SOT)

All text sizing is strictly regulated to 6 standardized tiers derived from the **Goal Judge** reference implementation:

```javascript
export const TEXT_SIZE_SYSTEM = {
  kpi_hero: {
    id: 'kpi_hero',
    size: '24px',
    tailwindClass: 'text-2xl',
    weight: 'font-extrabold',
    family: 'mono',
    usage: 'Prominent numerical readouts, active goal counts, budget metrics',
    sample: '24',
    reference: 'Goal Judge KPI Hero Counters (Total Tracked: 24, Active: 1, Done: 11)'
  },
  pane_title: {
    id: 'pane_title',
    size: '14px',
    tailwindClass: 'text-sm',
    weight: 'font-bold',
    family: 'display',
    usage: 'Cockpit titles, top-level pane identity, session headlines',
    sample: 'Goal Judge & Ralph Loop',
    reference: 'Goal Judge HeaderCockpit Title & Discussion Session Headline'
  },
  action_body: {
    id: 'action_body',
    size: '12px',
    tailwindClass: 'text-xs',
    weight: 'font-semibold',
    family: 'sans',
    usage: 'Cockpit action buttons, goal objective prose, modal forms',
    sample: '[ See Active Goal ]',
    reference: 'Goal Judge Primary Action Cockpit Buttons & Body Prose'
  },
  section_label: {
    id: 'section_label',
    size: '11px',
    tailwindClass: 'text-[11px]',
    weight: 'font-bold',
    family: 'display',
    usage: 'SectionHeader uppercase titles, input labels, technical session IDs',
    sample: 'RALPH LOOP ACTION COCKPIT',
    reference: 'Goal Judge SectionHeader Titles & Form Field Labels'
  },
  action_subtext: {
    id: 'action_subtext',
    size: '10px',
    tailwindClass: 'text-[10px]',
    weight: 'font-normal',
    family: 'mono',
    usage: 'Action button subtext, status badges, version chips, pill tags',
    sample: 'Launch /goal • v2.3.0',
    reference: 'Goal Judge Action Button Subtext & Micro Status Chips'
  },
  micro_caption: {
    id: 'micro_caption',
    size: '9px',
    tailwindClass: 'text-[9px]',
    weight: 'font-medium',
    family: 'mono',
    usage: 'Uppercase tracking-widest subtitles, micro timestamps, technical IDs',
    sample: 'AUTONOMOUS GOAL TRACKING & VERIFICATION TRIGGERS',
    reference: 'Goal Judge SectionHeader Subtitle (AUTONOMOUS GOAL TRACKING...)'
  }
};
```

---

### 2.1. `SectionHeader` (Display Title)

- **Purpose**: Establishes thematic rhythm and section demarcation without cluttered horizontal dividers.
- **Font**: `display` (`'Trebuchet MS', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif`).
- **Subtitle**: `mono` (`text-[9px] uppercase tracking-widest text-zinc-500`).

```jsx
function SectionHeader({ icon, title, subtitle, colorHex = '#22d3ee' }) {
  return (
    <div className="text-center pt-2 pb-1 space-y-0.5">
      <div 
        className="text-[11px] font-bold tracking-wider uppercase flex items-center justify-center gap-1.5"
        style={{ fontFamily: "'Trebuchet MS', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif", color: colorHex }}
      >
        {icon && <i className={`codicon codicon-${icon} text-xs`} style={{ color: colorHex }} />}
        <span>{title}</span>
      </div>
      {subtitle && (
        <span 
          className="text-[9px] text-zinc-500 uppercase tracking-widest block font-mono"
          style={{ fontFamily: "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', monospace" }}
        >
          {subtitle}
        </span>
      )}
    </div>
  );
}
```

---

### 2.1b. `ComponentGroupHeader` (Layout Group Boundary & Counter Badge)

- **Purpose**: Establishes structural layout groups with vertical rhythm (`space-y-8` root, `space-y-4` group), Codicon icon, uppercase title, description, and specimen count badge without bounding box strokes.
- **Font**: `display` for title, `sans` for subtitle, `mono` for count badge.
- **Divider**: Subtle bottom border line (`border-b border-white/[0.06] pb-2`).

```jsx
function ComponentGroupHeader({ icon, title, subtitle, count, colorHex = '#60a5fa' }) {
  return (
    <div className="pb-2 border-b border-white/[0.06] flex items-center justify-between select-none">
      <div className="flex items-center gap-2">
        <i className={`codicon codicon-${icon} text-sm`} style={{ color: colorHex }} />
        <div className="flex flex-col">
          <span 
            className="text-xs sm:text-sm font-bold uppercase tracking-wider"
            style={{ fontFamily: "'Trebuchet MS', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif", color: colorHex }}
          >
            {title}
          </span>
          {subtitle && (
            <span className="text-[11px] text-zinc-400 font-sans">
              {subtitle}
            </span>
          )}
        </div>
      </div>
      {count && (
        <span 
          className="text-[10px] font-mono px-2 py-0.5 rounded bg-white/5 text-zinc-400 border border-white/10 font-semibold"
          style={{ fontFamily: "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', monospace" }}
        >
          {count}
        </span>
      )}
    </div>
  );
}
```

---

### 2.2. `ActionCockpit` (Horizontal Button Row with Text Underneath)

- **Rule**: Single horizontal row (`grid grid-cols-3 gap-3`). Button strictly on top, descriptive label underneath.
- **Fail-Safe Styling**: Inline hex background, border, text, and ambient glow.

```jsx
function ActionCockpit({ actions }) {
  return (
    <div className="grid grid-cols-3 gap-3 pt-1">
      {actions.map((act, idx) => (
        <div key={idx} className="flex flex-col items-center text-center group">
          <button
            onClick={act.onClick}
            disabled={act.disabled}
            className="w-full flex items-center justify-center gap-1.5 px-3 py-2 text-xs font-semibold rounded-lg border transition-all duration-200 active:scale-[0.98] cursor-pointer"
            style={{
              backgroundColor: act.bg || 'rgba(37, 99, 235, 0.28)',
              borderColor: act.border || 'rgba(59, 130, 246, 0.65)',
              color: act.text || '#bfdbfe',
              boxShadow: act.glow || '0 0 14px rgba(59, 130, 246, 0.30)',
              fontFamily: "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
            }}
          >
            <i className={`codicon codicon-${act.icon || 'play'} text-sm`} />
            <span>{act.label}</span>
          </button>
          <span 
            className="text-[10px] text-zinc-400 mt-1.5 leading-tight px-1"
            style={{ fontFamily: "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" }}
          >
            {act.subtext}
          </span>
        </div>
      ))}
    </div>
  );
}
```

---

### 2.3. `UnboxedCard` (Negative Space & Bullet Dot Telemetry)

- **Rule**: No nested borders or visible bounding boxes. Root containers use `border border-transparent` with single-shade elevation. Monospace items separated by `•`.

```jsx
function UnboxedCard({ title, icon, colorHex, status, metrics, children }) {
  return (
    <div className="rounded-xl border border-transparent bg-zinc-900/40 p-3.5 space-y-2.5 transition-colors hover:bg-zinc-900/60">
      {/* Header Row */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <i className={`codicon codicon-${icon} text-sm`} style={{ color: colorHex }} />
          <span 
            className="text-xs font-semibold text-zinc-200"
            style={{ fontFamily: "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" }}
          >
            {title}
          </span>
        </div>
        <span 
          className="text-[10px] font-mono px-2 py-0.5 rounded border border-transparent"
          style={{
            backgroundColor: `${colorHex}1a`,
            color: colorHex
          }}
        >
          {status}
        </span>
      </div>

      {/* Unboxed Metadata Strip (Bullet Dot Separators) */}
      <div 
        className="text-[11px] font-mono text-zinc-400 flex flex-wrap items-center gap-1.5"
        style={{ fontFamily: "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace" }}
      >
        {metrics.map((m, idx) => (
          <span key={idx} className="flex items-center gap-1.5">
            <span className="text-zinc-300">{m.label}:</span>
            <span style={{ color: m.colorHex || '#f4f4f5' }}>{m.value}</span>
            {idx < metrics.length - 1 && <span className="text-zinc-600">•</span>}
          </span>
        ))}
      </div>

      {/* Optional Body Content */}
      {children && <div className="pt-1">{children}</div>}
    </div>
  );
}
```

---

### 2.4. `SingleShadeElevatedDrawer` (Expanded Details View)

- **Rule**: Distinct background shade `rgba(18, 20, 26, 0.78)` with `border-l-[3px]` solid chromatic accent and `border border-transparent` to eliminate visual ambiguity.

```jsx
function SingleShadeElevatedDrawer({ isOpen, colorHex, title, details, onClose }) {
  if (!isOpen) return null;

  return (
    <div 
      className="mt-2.5 rounded-lg border border-transparent p-3 space-y-2 transition-all duration-200"
      style={{
        backgroundColor: 'rgba(18, 20, 26, 0.78)',
        borderLeft: `3px solid ${colorHex || '#22d3ee'}`
      }}
    >
      <div className="flex items-center justify-between pb-1">
        <span 
          className="text-[11px] font-semibold text-zinc-300 flex items-center gap-1.5"
          style={{ fontFamily: "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" }}
        >
          <i className="codicon codicon-info text-xs" style={{ color: colorHex }} />
          <span>{title || 'Expanded Specification'}</span>
        </span>
        {onClose && (
          <button onClick={onClose} className="text-zinc-500 hover:text-zinc-300 text-xs cursor-pointer">
            <i className="codicon codicon-close" />
          </button>
        )}
      </div>

      {/* Unboxed Spec Details */}
      <div 
        className="text-[11px] font-mono text-zinc-400 space-y-1"
        style={{ fontFamily: "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace" }}
      >
        {details.map((item, idx) => (
          <div key={idx} className="flex items-center justify-between">
            <span className="text-zinc-500">{item.name}</span>
            <span className="text-zinc-200">{item.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

### 2.5. `BorderlessProgressGauge` (Borderless Visual Track)

- **Rule**: Zero outer borders on the progress bar track. Clean, curved rounded track with inline glow.

```jsx
function BorderlessProgressGauge({ label, value, max, colorHex, unit = '' }) {
  const pct = Math.min(100, Math.max(0, Math.round((value / max) * 100)));

  return (
    <div className="space-y-1.5">
      <div className="flex justify-between text-[11px]">
        <span 
          className="text-zinc-400"
          style={{ fontFamily: "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" }}
        >
          {label}
        </span>
        <span 
          className="font-mono text-zinc-300"
          style={{ fontFamily: "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace" }}
        >
          {value}{unit} / {max}{unit} ({pct}%)
        </span>
      </div>
      <div className="w-full h-1.5 rounded-full bg-zinc-800/80 overflow-hidden">
        <div 
          className="h-full rounded-full transition-all duration-300"
          style={{
            width: `${pct}%`,
            backgroundColor: colorHex || '#22d3ee',
            boxShadow: `0 0 8px ${colorHex || '#22d3ee'}66`
          }}
        />
      </div>
    </div>
  );
}
```

---

### 2.6. `FilterPillsBar` (Interactive Monospace Filter Tabs)

- **Rule**: Clean pill buttons with monospace active counts.

```jsx
function FilterPillsBar({ tabs, activeTab, onSelectTab }) {
  return (
    <div className="flex items-center gap-1.5 overflow-x-auto pb-1 scrollbar-none">
      {tabs.map((tab) => {
        const isActive = activeTab === tab.id;
        return (
          <button
            key={tab.id}
            onClick={() => onSelectTab(tab.id)}
            className="flex items-center gap-1.5 px-2.5 py-1 text-xs font-medium rounded-full border transition-all duration-150 cursor-pointer"
            style={{
              backgroundColor: isActive ? 'rgba(255, 255, 255, 0.08)' : 'transparent',
              borderColor: isActive ? tab.colorHex || '#22d3ee' : 'rgba(255, 255, 255, 0.08)',
              color: isActive ? '#ffffff' : '#a1a1aa'
            }}
          >
            {tab.icon && (
              <i 
                className={`codicon codicon-${tab.icon} text-xs`}
                style={{ color: isActive ? tab.colorHex : '#71717a' }}
              />
            )}
            <span>{tab.label}</span>
            {tab.count !== undefined && (
              <span 
                className="text-[10px] font-mono px-1 py-0.2 rounded-full"
                style={{
                  backgroundColor: isActive ? `${tab.colorHex}26` : 'rgba(255, 255, 255, 0.05)',
                  color: isActive ? tab.colorHex : '#a1a1aa'
                }}
              >
                {tab.count}
              </span>
            )}
          </button>
        );
      })}
    </div>
  );
}
```

---

### 2.7. `VerdictProofBanner` (Verifiable Evidence Cockpit)

- **Rule**: Distinct single-shade background `rgba(18, 20, 26, 0.78)` with `borderLeft: '3px solid #22c55e'` (Approved) or `'3px solid #ef4444'` (Rejected).
- **Format**: Headline verdict in `display` font, monospace bullet line with commit hashes, test pass metrics, and empirical evidence.

```jsx
function VerdictProofBanner({ status = 'approved', commitHash, testSummary, message }) {
  const isApproved = status === 'approved';
  const colorHex = isApproved ? '#22c55e' : '#ef4444';

  return (
    <div 
      className="p-3 rounded-lg border border-white/[0.07] space-y-1.5 text-xs shadow-md"
      style={{
        backgroundColor: 'rgba(18, 20, 26, 0.78)',
        borderLeft: `3px solid ${colorHex}`
      }}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-1.5 font-bold" style={{ color: colorHex }}>
          <i className={`codicon codicon-${isApproved ? 'check-all' : 'error'} text-sm`} />
          <span style={{ fontFamily: "'Trebuchet MS', -apple-system, sans-serif" }}>
            {isApproved ? 'VERDICT: PROOF VERIFIED (APPROVED)' : 'VERDICT: REJECTED (NO PROOF)'}
          </span>
        </div>
        <span 
          className="text-[9px] font-mono px-1.5 py-0.2 rounded border"
          style={{
            backgroundColor: `${colorHex}26`,
            color: colorHex,
            borderColor: `${colorHex}4d`
          }}
        >
          {isApproved ? 'EVIDENCE 100%' : 'PROOF MISSING'}
        </span>
      </div>
      <div 
        className="text-[11px] text-zinc-300 flex flex-wrap items-center gap-2 pt-0.5"
        style={{ fontFamily: "ui-monospace, SFMono-Regular, monospace" }}
      >
        {commitHash && (
          <>
            <span className="text-zinc-500">Commit:</span>
            <strong className="text-cyan-300">{commitHash}</strong>
            <span className="text-zinc-600">•</span>
          </>
        )}
        <span className={isApproved ? 'text-emerald-300' : 'text-rose-300'}>{testSummary}</span>
        {message && (
          <>
            <span className="text-zinc-600">•</span>
            <span className="text-zinc-400">{message}</span>
          </>
        )}
      </div>
    </div>
  );
}
```

---

### 2.8. `TurnBudgetGauge` (Dynamic Looper HUD)

- **Rule**: Borderless progress track with dynamic threshold coloration (Green < 50%, Amber 50-80%, Rose > 80%). Includes quick-action looper triggers.

```jsx
function TurnBudgetGauge({ usedTurns, maxTurns, onExtend, onLoop }) {
  const pct = Math.min(100, Math.round((usedTurns / maxTurns) * 100));
  const trackColor = pct > 80 ? '#ef4444' : pct > 50 ? '#fbbf24' : '#34d399';

  return (
    <div className="p-3 rounded-lg border border-white/[0.06] bg-black/25 space-y-2.5">
      <div className="flex items-center justify-between text-xs">
        <span className="font-semibold text-zinc-300 flex items-center gap-1.5">
          <i className="codicon codicon-history text-cyan-400 text-xs" />
          <span>Turn Budget Looper</span>
        </span>
        <span 
          className="text-[11px] font-mono font-bold"
          style={{ color: trackColor }}
        >
          {usedTurns} / {maxTurns} turns ({pct}%)
        </span>
      </div>
      <div className="h-1.5 rounded-full bg-white/10 overflow-hidden">
        <div 
          className="h-full rounded-full transition-all duration-300"
          style={{ width: `${pct}%`, backgroundColor: trackColor }}
        />
      </div>
      <div className="flex items-center justify-between gap-1 pt-0.5">
        <div className="flex items-center gap-1.5">
          <button 
            type="button" 
            onClick={() => onExtend(10)}
            className="px-2 py-0.5 rounded text-[10px] font-mono font-semibold bg-white/5 hover:bg-white/10 border border-white/10 text-zinc-200 transition-colors"
          >
            +10 Turns
          </button>
          <button 
            type="button" 
            onClick={() => onExtend(25)}
            className="px-2 py-0.5 rounded text-[10px] font-mono font-semibold bg-white/5 hover:bg-white/10 border border-white/10 text-zinc-200 transition-colors"
          >
            +25 Turns
          </button>
        </div>
        <button 
          type="button" 
          onClick={onLoop}
          className="px-2 py-0.5 rounded text-[10px] font-bold border flex items-center gap-1 transition-all"
          style={{
            backgroundColor: 'rgba(6, 182, 212, 0.15)',
            borderColor: 'rgba(34, 211, 238, 0.40)',
            color: '#67e8f9'
          }}
        >
          <i className="codicon codicon-sync text-[10px]" />
          <span>🔄 Loop Goal</span>
        </button>
      </div>
    </div>
  );
}
```

---

### 2.9. `CriteriaSubgoalsDrawer` (Evaluation Criteria Manager)

- **Rule**: Single-shade drawer with cyan left border, numbered criteria with emerald indices, and inline addition/removal controls.

```jsx
function CriteriaSubgoalsDrawer({ isOpen, onToggle, criteria, onAdd, onRemove, onEdit }) {
  return (
    <div className="space-y-1.5">
      <button 
        type="button" 
        onClick={onToggle}
        className="w-full p-2.5 rounded-lg border border-transparent bg-black/30 flex items-center justify-between text-xs cursor-pointer select-none hover:bg-white/[0.02]"
      >
        <div className="flex items-center gap-2">
          <i className="codicon codicon-target text-xs text-cyan-400" />
          <span className="font-semibold text-white">🎯 Evaluation Criteria & Subgoals ({criteria.length})</span>
        </div>
        <i className={`codicon codicon-${isOpen ? 'chevron-up' : 'chevron-down'} text-xs text-zinc-500`} />
      </button>
      {isOpen && (
        <div 
          className="p-3 rounded-lg border border-transparent space-y-2 text-xs"
          style={{
            backgroundColor: 'rgba(18, 20, 26, 0.78)',
            borderLeft: '3px solid #06b6d4',
            boxShadow: '0 4px 16px rgba(0, 0, 0, 0.25)'
          }}
        >
          <div className="space-y-1.5">
            {criteria.map((crit, idx) => (
              <div key={idx} className="flex items-center justify-between gap-2 p-1.5 rounded bg-white/[0.03] border border-transparent">
                <div className="flex items-start gap-1.5 flex-1 min-w-0">
                  <span className="font-mono text-emerald-400 font-bold text-[11px]">{idx + 1}.</span>
                  <span className="text-[11px] text-zinc-200">{crit}</span>
                </div>
                <div className="flex items-center gap-1">
                  <button onClick={() => onEdit(idx)} className="p-1 hover:text-cyan-400 text-zinc-500 text-xs">
                    <i className="codicon codicon-edit" />
                  </button>
                  <button onClick={() => onRemove(idx)} className="p-1 hover:text-rose-400 text-zinc-500 text-xs">
                    <i className="codicon codicon-trash" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

---

### 2.10. `MidTurnSteeringCockpit` (`/steer` Guidance Injection)

- **Rule**: Distinct red-tinted drawer with quick preset buttons for immediate operator intervention without canceling the loop.

```jsx
function MidTurnSteeringCockpit({ isOpen, onToggle, steerText, onChangeText, onSteer, onSelectPreset }) {
  const PRESETS = [
    { label: '⚡ Fix errors first', text: 'Prioritize diagnosing and fixing the root cause error first.' },
    { label: '🛡️ Zero regressions', text: 'Do not touch existing working features; keep tests passing.' },
    { label: '🔍 Test proof required', text: 'Execute actual empirical test commands and show stdout before claiming completion.' },
    { label: '📊 Final summary', text: 'Wrap up and produce a clear final summary of deliverables.' }
  ];

  return (
    <div className="space-y-1.5">
      <button 
        type="button" 
        onClick={onToggle}
        className="w-full p-2.5 rounded-lg border border-transparent bg-red-500/[0.07] flex items-center justify-between text-xs cursor-pointer select-none hover:bg-red-500/[0.12]"
      >
        <div className="flex items-center gap-2">
          <i className="codicon codicon-run-above text-xs text-rose-400" />
          <span className="font-semibold text-rose-300">⏩ Steer Run Mid-Turn (/steer)</span>
        </div>
        <i className={`codicon codicon-${isOpen ? 'chevron-up' : 'chevron-down'} text-xs text-rose-400/60`} />
      </button>
      {isOpen && (
        <div 
          className="p-3 rounded-lg border border-transparent space-y-2 text-xs"
          style={{
            backgroundColor: 'rgba(18, 20, 26, 0.78)',
            borderLeft: '3px solid #ef4444',
            boxShadow: '0 4px 16px rgba(0, 0, 0, 0.25)'
          }}
        >
          <div className="flex items-center gap-2">
            <input 
              type="text" 
              value={steerText} 
              onChange={(e) => onChangeText(e.target.value)}
              placeholder="Inject mid-turn guidance..."
              className="flex-1 py-1.5 px-2.5 rounded bg-black/50 border border-transparent text-xs text-zinc-200 font-sans focus:outline-none focus:border-red-500/30"
            />
            <button 
              type="button" 
              onClick={onSteer}
              className="py-1.5 px-3 rounded border border-transparent font-bold text-xs flex items-center gap-1.5"
              style={{
                backgroundColor: 'rgba(239, 68, 68, 0.40)',
                borderColor: 'transparent',
                color: '#fecaca',
                boxShadow: '0 0 10px rgba(239, 68, 68, 0.35)'
              }}
            >
              <i className="codicon codicon-arrow-right" />
              <span>Steer</span>
            </button>
          </div>
          <div className="flex flex-wrap items-center gap-1.5 pt-0.5">
            <span className="text-[10px] font-mono text-zinc-400 font-semibold uppercase">Presets:</span>
            {PRESETS.map((p) => (
              <button 
                key={p.label}
                type="button" 
                onClick={() => onSelectPreset(p.text)}
                className="px-2 py-0.5 rounded text-[10px] bg-red-500/10 hover:bg-red-500/20 text-red-300 border border-transparent transition-colors"
              >
                {p.label}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
```

---

## 3. Style Verification Matrix

| Component | Font Compliant | Inline Purge Safe | Unboxed Metas | Elevation Compliant |
| :--- | :---: | :---: | :---: | :---: |
| `SectionHeader` | ✅ `display` | ✅ Inline font | N/A | N/A |
| `ActionCockpit` | ✅ `sans` | ✅ Hex + Glow | ✅ No nested boxes | N/A |
| `UnboxedCard` | ✅ `sans` + `mono` | ✅ Hex borders | ✅ Bullet dots (`•`)| N/A |
| `ElevatedDrawer` | ✅ `sans` + `mono` | ✅ Inline left-accent | ✅ Clean key-value | ✅ `rgba(18,20,26,0.78)` |
| `ProgressGauge` | ✅ `sans` + `mono` | ✅ Inline bar glow | ✅ Borderless | N/A |
| `FilterPillsBar` | ✅ `sans` + `mono` | ✅ Dynamic borders | ✅ Monospace pills | N/A |
| `VerdictProofBanner` | ✅ `display` + `mono` | ✅ Hex colors + glow | ✅ Bullet dots (`•`)| ✅ `rgba(18,20,26,0.78)` |
| `TurnBudgetGauge` | ✅ `sans` + `mono` | ✅ Dynamic bar color | ✅ Tabular numbers | N/A |
| `CriteriaDrawer` | ✅ `sans` + `mono` | ✅ Hex borders | ✅ Clean numbered list| ✅ `rgba(18,20,26,0.78)` |
| `SteeringCockpit` | ✅ `sans` + `mono` | ✅ Red accent + glow | ✅ Unboxed presets | ✅ `rgba(18,20,26,0.78)` |

