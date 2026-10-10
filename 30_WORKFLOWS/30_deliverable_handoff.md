# Workflow — Deliverable Handoff

**Purpose**: How Mavis delivers files Popy needs to use.

## Cardinal rule — emit, don't just print

When Mavis creates a file Popy needs (a doctrine, a config, an archive, an image), Mavis must **send** it via `<media />` or `<deliver-assets>...</deliver-assets>` tags. Printing the file path is not enough — Popy cannot access Mavis's filesystem directly.

## `<media />` (single file)

```
<media src="C:/Users/apviz/.minimax-agent/projects/SENTINEL_OPERATIONAL_DOCTRINE.md" type="file" caption="Paste-into-Custom-instructions doctrine" />
```

Attributes:
- `src` — absolute path (required)
- `type` — `file`, `image`, `audio`, `video` (auto-detected if omitted)
- `caption` — optional description shown alongside

## `<deliver-assets>` (multi-file / site deployment)

```
<deliver-assets>
<media src="C:/.../file1.md" />
<media src="C:/.../file2.md" />
</deliver-assets>
```

For website deploys, use the `website_deploy` tool — see that tool's contract.

## Verification before sending

Before emitting a `<media />` tag:
1. Confirm the file was actually written in this turn (`write` returned success).
2. For local files: `Test-Path -Path <path> -PathType Leaf` to verify.
3. For deleted files (use `deleted="true"`): confirm the file existed before this turn and is now absent.

## Anti-patterns

- ❌ Printing a file path without `<media />` — Popy cannot access it
- ❌ Emitting a `<media />` for a file that was not actually created in this turn
- ❌ Emitting a planned/guessed path — must be real
- ❌ Using relative paths — must be absolute

## Multiple deliverables

If Mavis created multiple files Popy needs, wrap them in one `<deliver-assets>` block with a brief summary above it. Do not scatter individual `<media />` tags throughout the response.

## JURNAL_OGLINDA

| Date | Event | Notes |
|---|---|---|
| 2026-09-18 | Workflow codified | First backbone session |
