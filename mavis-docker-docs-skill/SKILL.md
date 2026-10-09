---
name: mavis-docker-docs-skill
description: Document and PDF operations via the local Docker services. stirling-pdf (:8082) transforms existing PDFs (merge/split/OCR/watermark/convert); libreoffice (:3001) converts Office formats headlessly. Use for "merge these PDFs", "split this PDF", "OCR this scan", "convert this DOCX to PDF". Triggers on PDF merge/split/OCR/watermark, DOCX/XLSX/PPTX conversion.
---

# mavis-docker-docs-skill

Two local Docker services cover document operations. Neither has an MCP bridge; this skill drives them over HTTP / container exec.

## stirling-pdf — `:8082`

| Property | Value |
|---|---|
| Image | `stirlingtools/stirling-pdf:latest` (**2.14.3**) |
| Port | `127.0.0.1:8082 → 8080` |
| Status | `Up (healthy)` |
| Auth | **🔴 401 on every route** — see below |
| Compose origin | project `apviz`, from `C:\Users\apviz\docker-compose.yml` — **that file no longer exists** |

### Auth gate (the real blocker)

The container sets `DOCKER_ENABLE_SECURITY=false`, but that is the **wrapper image** flag, not the app flag. Stirling-PDF 2.x gates auth on the app property, which defaults to **on**, so every route returns 401 — including `/api/v1/info` and `/api/v1/tools/*`.

Fix — one env var, then recreate the container:

```yaml
services:
  stirling-pdf:
    image: stirlingtools/stirling-pdf:latest
    environment:
      SECURITY_ENABLED: "false"     # <-- the real gate
    ports: ["127.0.0.1:8082:8080"]
    volumes: ["stirling-data:/tmp/stirling"]
volumes:
  stirling-data:
```

`DOCKER_ENABLE_SECURITY=false` can stay or go; it is not what the app reads.

### API surface once ungated

| Operation | Endpoint |
|---|---|
| version / health | `GET /api/v1/info` |
| tool list | `GET /api/v1/tools/*` |
| merge PDFs | `POST /api/v1/merge-pdf` (multipart) |
| split PDF | `POST /api/v1/split-pdf` |
| convert (PDF↔images, PDF→DOCX) | `POST /api/v1/convert/pdf` |
| add / remove password | `POST /api/v1/add-password`, `POST /api/v1/remove-password` |
| watermark | `POST /api/v1/add-watermark` |
| OCR | `POST /api/v1/ocr-pdf` |
| rotate / flip | `POST /api/v1/rotate-pdf`, `POST /api/v1/flip-pdf` |

Verify auth is off before batching:
```powershell
Invoke-WebRequest http://127.0.0.1:8082/api/v1/info -UseBasicParsing
```

## libreoffice — `:3001`

| Property | Value |
|---|---|
| Image | `lscr.io/linuxserver/libreoffice:latest` |
| Port | `127.0.0.1:3001 → 3000` |
| Status | `Up` |
| Surface | web UI (HTTP 200, serves the LibreOffice front end) — **no REST API** |
| Binary | `/usr/bin/soffice`, `/usr/bin/libreoffice` |

The port is a browser UI, not an API. For scripted conversion, exec `soffice --headless --convert-to` inside the container instead:

```powershell
$d = 'C:\Program Files\Docker\Docker\resources\bin\docker.exe'
# DOCX -> PDF
& $d exec libreoffice soffice --headless --convert-to pdf --outdir /tmp/lo /tmp/lo/in.docx
# then copy the result out
& $d cp libreoffice:/tmp/lo/in.pdf C:\Users\apviz\Downloads\in.pdf
```

Stage inputs by `docker cp` first, convert, copy back. Formats LibreOffice handles: doc, docx, xls, xlsx, ppt, pptx, odt, ods, odp, rtf, csv, html, and outputs pdf.

## Precedence

- **New PDF from text** → use the `minimax-pdf` MiniMax Hub skill (generation), not stirling (transformation only).
- **Transform an existing PDF** → stirling-pdf, once auth is off.
- **Office → PDF/other** → libreoffice `soffice --headless`.
- **Anything Office** → also check `word_editor` / `excel_editor` / `pptx-generator` first; they are in-process and faster for structured edits. These two containers are for *batch* and *format conversion*.

## Anti-patterns

- ❌ Assuming `DOCKER_ENABLE_SECURITY=false` disables Stirling auth — it does not.
- ❌ Expecting a REST API on libreoffice :3001 — it is a browser UI.
- ❌ Using stirling to create a PDF from scratch — it transforms.
- ❌ Forgetting `docker cp` in/out; `soffice` cannot see host files.

## Cross-references

- Docker fleet: `…\projects\70_CONNECTORS\70_docker_fleet_inventory.md`
- Bridge group: `…\projects\20_BRIDGES\minimax\`
- Content skills: `minimax-pdf`, `pptx-generator`, `excel_editor`, `word_editor`
