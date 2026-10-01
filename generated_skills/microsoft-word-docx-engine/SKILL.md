---
name: microsoft-word-docx-engine
description: >-
  Parse, modify, and render Microsoft Word (.docx) documents in pure JavaScript/TypeScript without requiring Microsoft Word desktop installation.
---

# Microsoft Word DOCX & OpenXML Processing Engine

Laser-focused, narrow-specialized skill for Microsoft Word DOCX & OpenXML Processing Engine. Validated against official documentation.

## Capability Split

| Phase | What | Transport | Surface |
| :--- | :--- | :--- | :--- |
| 1 | Template Inspection | CLI/Code | `docx-templates analyze` |
| 2 | Dynamic Data Merging | Library | `createReport({ template, data })` |
| 3 | OpenXML Table & Style Injection | Library | `new Table({ rows: [...] })` |
| 4 | Integrity & Schema Verification | CLI | `preflight_check.ps1` |

## Auth & Preflight Requirements

**Token Name**: `DOCX_TEMPLATE_KEY`
**Required Scopes**: `local_filesystem_read`, `local_filesystem_write`

> [!IMPORTANT]
> Before running commands, verify that `DOCX_TEMPLATE_KEY` is present in the environment or project `.env` file. Never ask the user to paste credentials directly into chat.

## Execution Steps & Commands

### Install Dependencies
Installs serverless-safe docx generation packages

```bash
npm install docx docx-templates
```

### Generate Document
Executes template data merging with strict type safety

```bash
node scripts/generate_report.js --template template.docx --out output.docx
```

## Error Handling & Edge Cases

| Error Code | Root Cause | Agent Action |
| :--- | :--- | :--- |
| `CORRUPT_ZIP` | Invalid OpenXML archive or broken XML tag balance | Ensure template placeholders do not split across XML run nodes (<w:r>) |
| `MEMORY_LIMIT` | Document exceeds 100MB with embedded uncompressed images | Compress raster assets to WebP/JPEG before injection |

## References

- Detailed API Cheatsheet: [api_cheatsheet.md](./references/api_cheatsheet.md)
- Preflight Verification Script: [preflight_check.ps1](./scripts/preflight_check.ps1)
