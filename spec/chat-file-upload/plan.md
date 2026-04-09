# Plan — Chat Interface with File Upload

## 1. Delivery strategy

Deliver the feature as a thin Odoo bridge plus external ingestion/runtime services.

### Odoo responsibilities
- chat/source models
- upload UI
- source lifecycle display
- permissions
- chat request orchestration hook
- status callbacks

### External responsibilities
- extraction
- chunking/indexing
- retrieval
- Foundry request execution
- callback/status updates

## 2. Repo ownership

### `odoo`
Add a thin addon:
- `addons/ipai/ipai_chat_file_upload`

It should own:
- source models
- chat/source views
- upload/retry actions
- controller or service bridge
- audit-visible source linkage

### `agent-platform`
Add endpoints/services for:
- source ingestion request
- extraction/indexing pipeline
- source status callback
- source-grounded chat request

### `infra`
Wire:
- secrets
- managed identity/service access
- health checks
- deployment/runtime diagnostics

### `docs`
Add:
- architecture note
- release evidence references
- runbook for failed indexing/retry

## 3. Proposed Odoo model surface

### `ipai.chat.session`
Represents a chat thread or assistant session.

### `ipai.chat.message`
Represents a message and assistant response metadata.

### `ipai.chat.source`
Represents a managed source attached to a chat/session/user scope.

Suggested fields:
- `name`
- `session_id`
- `attachment_id`
- `source_type`
- `status`
- `active`
- `external_source_id`
- `external_index_id`
- `last_error`
- `processed_at`
- `checksum`

## 4. Lifecycle design

### Upload flow
1. User uploads/selects source in Odoo
2. Odoo stores metadata and attachment/link reference
3. Odoo sets status `draft`
4. Odoo hands off to external ingestion service
5. Status becomes `processing`
6. External service indexes source
7. Callback updates status to `indexed` or `failed`
8. Only `indexed + active` sources are eligible for grounded chat

### Chat flow
1. User sends message
2. Odoo determines eligible sources
3. Odoo sends chat request to external runtime
4. External runtime retrieves relevant chunks and calls Foundry
5. Odoo stores response metadata and provenance summary

## 5. API contract outline

### Odoo → agent-platform
#### `POST /v1/chat-sources`
Creates ingestion job for uploaded source.

#### `POST /v1/chat-sources/{id}/retry`
Retries failed indexing.

#### `POST /v1/chat-sessions/{id}/chat`
Runs source-grounded chat.

### agent-platform → Odoo
#### `POST /odoo/ipai/chat-sources/callback`
Updates source status/result.

## 6. Testing strategy

### Odoo tests
- source create/upload registration
- status transitions
- active/inactive restrictions
- failed source not eligible for grounded chat
- permissions checks
- chat request payload generation

### Agent-platform tests
- extraction smoke
- indexing callback contract
- grounded chat contract
- failed ingestion path
- timeout/retry behavior

### Runtime smoke
- Odoo upload endpoint reachable
- agent-platform ingestion reachable
- Foundry-backed chat path reachable
- failed indexing path observable

## 7. Release sequence

### Phase 1
- Odoo source models + UI
- external ingestion API contract
- status callback
- basic grounded chat

### Phase 2
- richer provenance/citation UI
- Odoo Documents/Knowledge integration
- improved retry/admin tooling

### Phase 3
- broader file types
- source reuse across sessions/projects
- advanced access control and policies

## 7.5 Intent router

Implement an attachment-aware intent router ahead of the generic assistant prompt path.

### Routing order
1. Active attachment detection — are there indexed sources in this session?
2. Attachment type classification — invoice, receipt, contract, spreadsheet, general
3. Task intent classification — extract, summarize, validate, review, compare
4. Routed action:
   - **extract**: run extraction pipeline, return parsed fields
   - **summarize**: extract text, generate summary
   - **validate / assess / check**: extract fields, run deterministic checks, report result
   - **review**: extract and present key fields
   - **narrow follow-up**: only if the task is genuinely ambiguous after considering attachment + intent

### Implementation location
- Intent classification: `_classify_intent()` method on controller or service
- Prompt construction: grounded prompt builder uses intent to set system instruction
- Deterministic validation: separate from LLM — compute totals, compare fields, flag mismatches

## 8. Risks

- making Odoo too heavy by moving ingestion work into workers
- unclear source scoping rules causing permission confusion
- file-type support drift between UI and actual extractor capability
- chat UX expectations outrunning grounded retrieval quality

## 9. Definition of done

The feature is done when:
- a user can upload a source in Odoo
- the source progresses through visible lifecycle states
- indexed active sources can ground chat
- failed sources are clearly surfaced and not used
- tests and live smoke evidence are complete

---

*Created: 2026-04-09*
