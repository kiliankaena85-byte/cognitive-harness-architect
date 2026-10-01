# Microsoft Word DOCX & OpenXML Processing Engine Reference & API Cheatsheet

> Sourced strictly from verified official documentation.

### Pure OpenXML Architecture
Never invoke Windows COM / ActiveX Word automation in modern services.
Use `docx` npm library for procedural generation and `docx-templates` for mail-merge placeholders.