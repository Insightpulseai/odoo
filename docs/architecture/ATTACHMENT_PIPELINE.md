# Attachment Pipeline for Pulser / Odoo Copilot

## Goal

Support chat attachments for:
- PDF
- images
- DOCX
- XLSX
- PPTX
- EML / MSG
- extracted child attachments from email containers

## Boundary

- `agent-platform` owns file sniffing, extraction, normalization, chunking, indexing, and agent grounding.
- `odoo` owns only thin bridge behavior: upload handoff, chat record linkage, citation display, and action callbacks.
- `docs/spec` owns the architecture contract and routing policy.

## Canonical flow

1. User uploads attachment in chat UI.
2. Backend sniffs MIME type and extension.
3. Router selects extractor:
   - Document Intelligence for PDF, image, DOCX, XLSX, PPTX
   - Azure AI Search document extraction/indexing for EML/MSG containers
4. Extracted content is normalized into sections/chunks with citation anchors.
5. Chunks are indexed or passed as grounded context.
6. Agent answers with source-backed citations.

## Routing rules

### PDF
- Preferred: Document Intelligence Layout
- Fallback: Document Intelligence Read
- Reason: preserves structure, tables, headings, and citation-friendly page context

### Images
- Preferred: Document Intelligence Read
- Fallback: Layout
- Reason: OCR-first extraction path

### DOCX / XLSX / PPTX
- Preferred: Document Intelligence Layout
- Reason: supported input class for Office documents
- Caveat: image behavior differs from PDF; embedded images should not be treated as fully reliable without a secondary path

### EML / MSG
- Preferred: Azure AI Search document extraction/indexers
- Reason: email containers are better handled as search/indexing documents than as Document Intelligence-first payloads
- Caveat: MSG attachments index as part of a single document unless custom unpacking is added

## Odoo integration rules

- Odoo must not persist raw extracted blobs inside chat records.
- Odoo stores:
  - attachment pointer
  - retrieval pointer
  - summary
  - citation anchor
  - action callback metadata
- Parser logic, OCR, Office extraction, and email container unpacking stay outside Odoo modules.

## Recommended bootstrap

- Chat shell: `Get started with AI agents`
- Document retrieval pattern: `RAG chat with Azure AI Search`
- Image-specific UX pattern: `Multimodal GenAI experience: Q&A on uploaded images`

## Optional next step

Add custom email-unpack preprocessing so each child attachment gets its own retrieval document instead of relying on container-level indexing only.
