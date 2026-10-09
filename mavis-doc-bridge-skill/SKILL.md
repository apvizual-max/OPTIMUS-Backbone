---
name: mavis-doc-bridge-skill
description: Use when converting, merging, or transforming documents and PDFs on this machine — .docx/.xlsx/.pptx/.odt/.html/.txt/.rtf/.md conversion via the LibreOffice container, and PDF/A, PDF-to-image, PDF-to-Word, or PDF merge via the Stirling-PDF container. Triggers on "convert to pdf", "make a pdf", "merge pdfs", "pdf to word", "pdf to png", "office document", "soffice", "stirling".
---

# mavis-doc-bridge-skill

Document tooling for OPTIMUS, driven by two Docker containers that are already
running. Both are host-side scripted: **the containers have no usable API layer
that Mavis can call directly**, so the bridge is `docker exec` + `curl.exe`.

## The one rule

**Never guess a Stirling-PDF endpoint or LibreOffice filter — verify it.** The
Stirling-PDF Angular SPA serves `index.html` for *unknown* paths, so a `200` on
an invented route means nothing. See "Verifying a Stirling route" below.

## Bridge 1 — LibreOffice conversion

Script: `C:\Users\apviz\.minimax-agent\projects\scripts\convert-document.ps1`

```powershell
& 'C:\Users\apviz\.minimax-agent\projects\scripts\convert-document.ps1' `
   -InputPath 'C:\path\brief.docx' -Format pdf -AsJson
```

Formats: `pdf docx xlsx pptx html txt csv odt ods odp rtf md`.
Emits JSON with `ok / source / output / format / bytes / via`.

### Verified capability matrix

Probed 2026-10-02 against LibreOffice 25.8.7.3 (`lscr.io/linuxserver/libreoffice`)
using **one fresh output directory per target** — a shared directory silently
reports a leftover file from a previous run as a success. That trap produced two
false "OK" results before it was caught.

| source → target | result |
|---|---|
| txt → pdf, docx, odt, html, txt, rtf, md | OK |
| txt → csv | FAIL (csv is a Calc format) |
| pdf → html | OK (Draw export) |
| pdf → docx, odt, txt | FAIL — no export filter |

**A `.pdf` is not a usable source except for HTML.** For pdf → Word use Bridge 2.
The script fails fast on the blocked combinations rather than letting soffice
emit an opaque `no export filter` message.

### Why these two details matter

- `-env:UserInstallation=file:///tmp/...` is passed on every run. Without a
  private profile, repeated or concurrent calls collide on the shared LibreOffice
  profile lock and the **second call produces no output at all**.
- Each invocation costs ~20-30 s of cold start. Batch, don't loop tightly.

### Not a REST API

The container publishes a Selkies web-desktop (VNC-over-browser) on
`127.0.0.1:3001`. It is not an API. Scripted work must go through
`docker exec libreoffice soffice --headless`.

## Bridge 2 — Stirling-PDF

Script: `C:\Users\apviz\.minimax-agent\projects\scripts\stirling-pdf.ps1`

```powershell
& 'C:\Users\apviz\.minimax-agent\projects\scripts\stirling-pdf.ps1' `
   -Operation pdfa -InputPath 'C:\path\in.pdf' -AsJson
```

Operations → endpoints (all POST, all multipart):

| Operation | Endpoint |
|---|---|
| `pdfa` | `/api/v1/convert/pdf/pdfa` |
| `img` | `/api/v1/convert/pdf/img` |
| `word` | `/api/v1/convert/pdf/word` |
| `merge` | `/api/v1/general/merge-pdfs` (2+ files) |

Emits JSON with `ok / operation / endpoint / inputs / output / bytes / magic`,
and validates the response magic bytes so an HTML page is never mistaken for a PDF.

### Login is off — and the variable name is a trap

Auth is disabled by `SECURITY_ENABLELOGIN=false` in
`C:\Users\apviz\docker-compose.yml`.

`SECURITY_ENABLED=false` — which appears in most web guides — **does nothing**.
The app ignored it and kept returning 401. The correct name was read out of the
container's own `/configs/settings.yml`, which documents its own override rule:

> `security.enableLogin` → `SECURITY_INITIALLOGIN_USERNAME` (example) → so
> `security.enableLogin` → **`SECURITY_ENABLELOGIN`**

If the API starts returning 401, re-apply with:
`Set-Location C:\Users\apviz; docker compose up -d stirling-pdf`

### Verifying a Stirling route

The SPA catch-all returns `200` + HTML for any unknown path, so a 200 proves
nothing. Use POST with a non-multipart body:

- **415** → the route exists (it wants multipart)
- **404** → the route does not exist
- **401** → login came back on

```powershell
curl.exe -s -o NUL -w "%{http_code}" -X POST -H "Content-Type: application/json" `
  -d '{}' 'http://127.0.0.1:8082/api/v1/convert/pdf/pdfa'
```

## Typical chains

```powershell
$S  = 'C:\Users\apviz\.minimax-agent\projects\scripts'
$w  = 'C:\Users\apviz\.minimax-agent\projects\scratch\docbridge'

# text -> pdf -> PDF/A
$pdf = (& "$S\convert-document.ps1" -InputPath "$w\notes.txt" -Format pdf -AsJson | ConvertFrom-Json).output
& "$S\stirling-pdf.ps1" -Operation pdfa -InputPath $pdf -AsJson

# several pdfs -> one
& "$S\stirling-pdf.ps1" -Operation merge -InputPath $pdf,"$w\appendix.pdf" -AsJson
```

## Safety

- Both scripts never clobber: if the destination exists, a short run-id suffix
  is added instead of overwriting.
- Each run uses a unique `/tmp/optimus-doc-<runid>` work dir and removes it in a
  `finally` block.
- Only the **stirling-pdf** service is recreated by the compose command above.
  Never use `--remove-orphans` on the `apviz` project — it would delete
  `Antigravity_Ecosystem_Terminal`, which shares the project name but is defined
  by its own compose file.
