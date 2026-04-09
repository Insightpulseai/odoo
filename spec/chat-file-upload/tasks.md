# Tasks — Chat Interface with File Upload

## Phase 1 — Core models and lifecycle (DONE)

- [x] Chat session model with UUID correlation
- [x] Chat message model with provenance tracking
- [x] Chat source model with state machine validation
- [x] Security groups and ACL rules
- [x] Session and source UI views
- [x] Navigation menus
- [x] Source lifecycle tests (30/30 pass)

## Phase 1.5 — Local extraction pipeline (DONE)

- [x] PDF extraction via PyPDF2
- [x] DOCX extraction via ZIP/XML parsing
- [x] XLSX extraction via ZIP/XML shared strings
- [x] Image OCR via pytesseract
- [x] Azure Document Intelligence fallback
- [x] Auto-extraction on upload
- [x] Grounded chat via Foundry service

## Phase 1.x — Attachment-aware intent routing

- [ ] Add intent classifier (`_classify_intent`) for extract/summarize/review/validate
- [ ] Add attachment-aware context resolver to `send_message`
- [ ] Build intent-specific system prompts for Foundry calls
- [ ] Route invoice-like docs to extraction + deterministic validator
- [ ] Add regression tests for:
  - [ ] uploaded PDF + "extract first" -> extraction starts
  - [ ] uploaded invoice + "assess if tax computation is correct" -> extraction + validation
  - [ ] uploaded doc + "summarize this" -> summarization
- [ ] Anti-regression: fail if assistant asks generic clarification when attachment + intent present

## Phase 2 — Richer provenance and citation UI

- [ ] Citation markers in assistant responses
- [ ] Source panel in chat UI
- [ ] Odoo Documents/Knowledge integration

## Phase 3 — Broader file types and reuse

- [ ] Source reuse across sessions
- [ ] Advanced access control
- [ ] Additional file type support

---

*Created: 2026-04-09*
