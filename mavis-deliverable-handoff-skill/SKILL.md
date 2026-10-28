---
name: mavis-deliverable-handoff-skill
description: Deliver files and websites to Popy via `<media />` and `<deliver-assets>` tags. Load whenever Mavis creates a file Popy needs to use (documents, archives, images, deployed sites). Print paths alone are not enough — Popy cannot access Mavis's filesystem directly.
---

# mavis-deliverable-handoff-skill

How Mavis delivers files Popy needs to pull down.

## Cardinal rule

When Mavis creates a file Popy needs, Mavis must **send** it via `<media />` or `<deliver-assets>` tags. Printing the file path is not enough.

## Single file — `<media />`

```
<media src="C:/absolute/path/to/file.ext" type="file" caption="Description of what's in the file" />
```

Attributes:
- `src` — absolute path (required)
- `type` — `file`, `image`, `audio`, `video` (auto-detected if omitted)
- `caption` — optional description shown alongside

## Multiple files — `<deliver-assets>`

```
<deliver-assets>
<media src="C:/path/to/file1.md" />
<media src="C:/path/to/file2.md" caption="The companion file" />
</deliver-assets>
```

## Image URL — Markdown

For an external image URL:
```
![description](https://example.com/image.png)
```
The system auto-detects this as a native image.

## Verification before sending

Before emitting a `<media />` tag:
1. Confirm the file was actually written in this turn (`write` returned success).
2. For local files: `Test-Path -Path <path> -PathType Leaf` to verify.
3. For deleted files (use `deleted="true"`): confirm the file existed before this turn and is now absent.

## Website deploy

For full website deployment, use the `website_deploy` tool — see its contract. Wrap the returned URL in a `<deliver-assets>` block with `type="website"`.

## Anti-patterns

- ❌ Printing a file path without `<media />` — Popy cannot access it
- ❌ Emitting a `<media />` for a file that was not actually created in this turn
- ❌ Emitting a planned/guessed path — must be real
- ❌ Using relative paths — must be absolute
- ❌ Scattering `<media />` tags throughout the response — wrap in `<deliver-assets>`

## Cross-references

- Doctrine: `SENTINEL_OPERATIONAL_DOCTRINE.md §15`
- Workflow file: `C:/Users/apviz/.minimax-agent/projects/Mavis-Optimus-Dashboard/30_WORKFLOWS/30_deliverable_handoff.md`
