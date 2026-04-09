# Chat Interface with File Upload — Architecture Note

> Thin Odoo bridge for managed source upload, external ingestion, and source-grounded chat.
>
> **Spec bundle**: `spec/chat-file-upload/` (constitution, PRD, plan)

---

## 1. Component boundaries

```
┌─────────────────────────────────────────────────┐
│  Odoo 18 CE  (ipai_chat_file_upload)            │
│                                                 │
│  ipai.chat.session   — chat thread              │
│  ipai.chat.message   — user/assistant messages  │
│  ipai.chat.source    — managed source metadata  │
│                                                 │
│  Controllers:                                   │
│    POST /ipai/chat/upload       → register      │
│    POST /ipai/chat/send         → chat bridge   │
│    POST /ipai/chat/source/cb    → status update │
│                                                 │
│  UI: source panel, status badges, retry action  │
└────────────┬───────────────────┬────────────────┘
             │ outbound          │ inbound callback
             ▼                   │
┌────────────────────────────────┴────────────────┐
│  agent-platform                                 │
│                                                 │
│  POST /v1/chat-sources          — ingest source │
│  POST /v1/chat-sources/{id}/retry — retry       │
│  POST /v1/chat-sessions/{id}/chat — grounded Q  │
│                                                 │
│  Extraction → Chunking → Indexing → Retrieval   │
│  Foundry orchestration for reasoning            │
│  Callback to Odoo on completion/failure         │
└─────────────────────────────────────────────────┘
```

## 2. Model surface

### `ipai.chat.session`

| Field | Type | Purpose |
|---|---|---|
| `name` | Char | Session title (auto or user-set) |
| `user_id` | Many2one(res.users) | Owner |
| `company_id` | Many2one(res.company) | Tenant scope |
| `state` | Selection | `active` / `archived` |
| `source_ids` | One2many | Linked sources |
| `message_ids` | One2many | Chat messages |
| `external_session_id` | Char | agent-platform correlation |

### `ipai.chat.message`

| Field | Type | Purpose |
|---|---|---|
| `session_id` | Many2one(ipai.chat.session) | Parent session |
| `role` | Selection | `user` / `assistant` / `system` |
| `content` | Text | Message body |
| `source_ids_snapshot` | Text (JSON) | Source IDs eligible at response time |
| `provenance_summary` | Text | Which sources were cited |
| `latency_ms` | Integer | Response time |
| `external_request_id` | Char | agent-platform correlation |

### `ipai.chat.source`

| Field | Type | Purpose |
|---|---|---|
| `name` | Char | Display name |
| `session_id` | Many2one(ipai.chat.session) | Owning session |
| `attachment_id` | Many2one(ir.attachment) | Odoo file reference |
| `source_type` | Selection | `pdf` / `image` / `docx` / `xlsx` / `url` |
| `status` | Selection | `draft` / `processing` / `indexed` / `failed` |
| `active` | Boolean | Soft-delete / deactivate |
| `external_source_id` | Char | agent-platform source ID |
| `external_index_id` | Char | Index/collection reference |
| `last_error` | Text | Failure message |
| `processed_at` | Datetime | When indexing completed |
| `checksum` | Char | SHA-256 for dedup |

## 3. Source lifecycle

```
upload/link → draft → processing → indexed → (active for chat)
                                 → failed  → (retry → processing)
                                            (deactivate → inactive)
```

Only sources with `status=indexed` AND `active=True` are eligible for grounded chat.

## 4. v1 source types

| Type | MIME | Extraction path |
|---|---|---|
| PDF | `application/pdf` | Document Intelligence / pdfminer |
| PNG/JPEG/WebP | `image/*` | Document Intelligence OCR |
| DOCX | `application/vnd.openxmlformats...wordprocessingml` | python-docx |
| XLSX | `application/vnd.openxmlformats...spreadsheetml` | openpyxl |
| URL | n/a | HTTP fetch + HTML extraction |

## 5. v1 source scope

Sources are **per-session** in v1. A source belongs to exactly one `ipai.chat.session`. Cross-session reuse is Phase 3.

## 6. API contracts

### Odoo → agent-platform

**`POST /v1/chat-sources`**
```json
{
  "source_id": "odoo_source_42",
  "session_id": "odoo_session_7",
  "source_type": "pdf",
  "filename": "invoice_march.pdf",
  "download_url": "https://erp.insightpulseai.com/web/content/ir.attachment/123/datas",
  "checksum": "sha256:abc123...",
  "callback_url": "https://erp.insightpulseai.com/ipai/chat/source/cb"
}
```

**`POST /v1/chat-sources/{id}/retry`**
```json
{ "source_id": "odoo_source_42" }
```

**`POST /v1/chat-sessions/{id}/chat`**
```json
{
  "session_id": "odoo_session_7",
  "message": "What is the total on this invoice?",
  "source_ids": ["odoo_source_42"],
  "restrict_to_sources": true
}
```

### agent-platform → Odoo

**`POST /ipai/chat/source/cb`**
```json
{
  "source_id": "odoo_source_42",
  "status": "indexed",
  "external_source_id": "ap_src_abc",
  "external_index_id": "idx_xyz",
  "error": null,
  "processed_at": "2026-04-09T17:30:00Z"
}
```

## 7. Relationship to existing modules

- **`ipai_odoo_copilot`**: The existing copilot module owns the systray chat, Foundry bridge, skill router, audit, and action queue. `ipai_chat_file_upload` depends on it and reuses its Foundry service layer where applicable.
- **`ipai_ai_agent_sources`**: Existing agent-level source management. `ipai_chat_file_upload` is a user-facing chat-scoped feature, not agent-scoped. They may share extraction patterns but are separate models.

## 8. Security

- `group_chat_user`: upload, view own sessions/sources, chat
- `group_chat_admin`: view all sessions/sources, retry, deactivate, inspect errors
- Callback endpoint authenticates via service key header (same pattern as existing `/api/pulser/chat/service`)

---

*Created: 2026-04-09*
