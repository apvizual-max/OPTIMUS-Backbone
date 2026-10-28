## 2026-10-23 - Accessibility: Form Elements Without Accessible Names
**Learning:** Found an input element (`<input id="q">` for corpus search) without an associated label or `aria-label` attribute. This is a common accessibility issue that prevents screen readers from understanding the purpose of the input.
**Action:** Always ensure interactive elements like inputs, select boxes, and buttons have an accessible name, either via an explicit `<label>` or an `aria-label`.
## 2024-10-24 - Custom Tabs Lack Keyboard Navigation
**Learning:** Custom tab implementations often use buttons inside a nav structure but neglect arrow-key keyboard navigation and aria relationships (`aria-controls`, `aria-labelledby`, dynamic `tabindex`). Without this, screen readers and keyboard users cannot easily navigate or understand the content structure.
**Action:** Always verify custom tab navigation for ARIA attributes and arrow-key focus management, not just mouse click handling.
