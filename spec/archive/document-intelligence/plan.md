# Implementation Plan: Document Intelligence

## Reference Template

- **Foundry template:** Multi-modal content processing
- **Azure resource:** `docai-ipai-dev` (Document Intelligence, Southeast Asia)
- **Also:** `data-intel-ph` in `rg-data-intel-ph` (AIServices, East US 2)

## Use Cases

- Invoice extraction (vendor invoices → Odoo `account.move`)
- Receipt OCR (expense receipts → Odoo `hr.expense`)
- Contract extraction (key terms, dates, parties)
- BIR form extraction (Philippine tax forms → structured data)
- Structured data mapping into Odoo / finance workflows

## Implementation Phases

### Phase 1 — Extraction Core

- Configure prebuilt models: invoice, receipt, ID document
- Define extraction-to-Odoo field mapping
- Wire Document Intelligence → copilot gateway → Odoo record creation
- Advisory-only mode (extracted data presented for human review)

### Phase 2 — Review Queue

- Build human-in-the-loop review UI
- Confidence thresholds for auto-accept vs manual review
- Field-level validation and correction
- Approval workflow before Odoo record creation

### Phase 3 — Custom Models

- Train custom models for BIR forms and domain-specific documents
- Define document type classification
- Build batch processing pipeline

## OpenAI Multimodal Implementation Lane

Use OpenAI multimodal patterns as the preferred implementation reference for:

- Document understanding (vision-based QA on extracted pages)
- OCR-alternative extraction (GPT-5.4 for Vision and Document Understanding)
- PDF parsing for RAG (structured extraction from unstructured documents)
- Vision-based validation and review (confidence checking, field verification)

Generation remains outside this lane unless a specific feature requires it.

## Rules

- All extracted data goes through human review before Odoo write
- Confidence scores visible on every extracted field
- Document-scoped, page/field-anchor-aware
- Approval-workflow-aware per MARKETING_ASSISTANT_DOCTRINE.md separation

---

*Last updated: 2026-03-23*
