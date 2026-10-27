## 2026-10-23 - Added missing aria-labels and roles
**Learning:** Found that header action buttons, the command palette input, the AI question textarea, and notebook query inputs in this single-page dashboard app were missing critical accessibility attributes. Icon-only buttons lacked `aria-label`, inputs lacked `aria-label` or implicit labels, which degrades screen reader experience.
**Action:** Always verify icon-only interactive elements and loose form inputs have explicit `aria-label` attributes.
