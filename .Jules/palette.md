## 2026-10-23 - Accessibility: Form Elements Without Accessible Names
**Learning:** Found an input element (`<input id="q">` for corpus search) without an associated label or `aria-label` attribute. This is a common accessibility issue that prevents screen readers from understanding the purpose of the input.
**Action:** Always ensure interactive elements like inputs, select boxes, and buttons have an accessible name, either via an explicit `<label>` or an `aria-label`.
