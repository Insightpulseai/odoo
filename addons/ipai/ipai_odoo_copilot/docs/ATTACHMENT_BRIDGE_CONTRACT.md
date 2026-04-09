# Attachment Bridge Contract — Odoo ↔ Agent Platform

> Odoo is the **thin bridge**. All extraction, parsing, OCR, and indexing
> logic lives in `agent-platform`. This contract defines the boundary.

---

## Odoo Responsibilities

| Responsibility | Detail |
|----------------|--------|
| Upload handoff | Accept file from chat UI, forward to agent-platform intake endpoint |
| Chat record linkage | Store `attachment_id`, `source_id`, `summary`, `citation_anchor`, `retrieval_pointer` on the chat message |
| Citation display | Render citation anchors returned by the agent as clickable references in the chat UI |
| Action callbacks | Handle action metadata (e.g. "open page 3", "download original") routed back from agent answers |

---

## External Pipeline Responsibilities (agent-platform)

| Responsibility | Detail |
|----------------|--------|
| MIME detection | Sniff uploaded file to determine type and select extraction route |
| Parser selection | Route to Document Intelligence (PDF, image, DOCX, XLSX, PPTX) or Azure AI Search (EML, MSG) per `ssot/agent/attachment-routing.yaml` |
| Extraction | Run selected parser, extract text, tables, structure, image refs |
| Normalization | Produce normalized chunks with required fields: `source_id`, `parent_source_id`, `file_name`, `mime_type`, `page_or_slide`, `section_title`, `extracted_text`, `image_refs`, `citation_anchor` |
| Chunking | Apply format-aware chunking strategy (layout_aware, ocr_blocks, heading_paragraph_table, etc.) |
| Indexing | Store searchable text in retrieval index (Azure AI Search); store large binaries in object store |
| Grounding | Pass indexed chunks as grounded context to the agent for answering |

---

## Required Return Payload

When the agent-platform completes extraction and indexing for an attachment,
it returns the following JSON payload to Odoo for storage on the chat record:

```json
{
  "attachment_id": "odoo-ir-attachment-id",
  "source_id": "agent-platform-document-id",
  "summary": "one-paragraph summary of the document",
  "citation_anchor": "{source_id}#p={page_or_slide}",
  "retrieval_pointer": "azure-ai-search-index/document-key"
}
```

Odoo stores **only** these five fields on the chat message record.
The full extracted content lives in the retrieval index, never in Odoo.

---

## Hard Constraints

1. **No OCR / parser logic in Odoo modules.** All extraction runs in agent-platform.
2. **No raw binary storage in chat message rows.** Odoo stores pointers, not blobs.
3. **No direct Document Intelligence calls from Odoo Python code.** The agent-platform mediates all Azure AI service calls.
4. **No embedding or vector storage in Odoo.** Embeddings live in Azure AI Search.
5. **Citation anchors are opaque strings.** Odoo renders them but does not parse or validate their internal format.

---

## Routing Policy Reference

See `ssot/agent/attachment-routing.yaml` for the machine-readable routing
policy that governs parser selection, chunking strategy, and quality tiers
per file type.

---

## Architecture Reference

See `docs/architecture/ATTACHMENT_PIPELINE.md` for the full canonical flow
and per-format routing rules.
