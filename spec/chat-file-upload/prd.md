# PRD — Chat Interface with File Upload

## 1. Overview

Build an Odoo 18 chat interface that supports managed file upload and source-grounded chat for enterprise workflows.

The feature should let a user:
- open a chat surface in Odoo
- upload or attach a supported source
- see source processing/indexing state
- chat against active indexed sources
- review source provenance and failures

The product must fit the existing architecture:
- Odoo 18 CE as transactional/workflow surface
- thin `ipai_*` bridge doctrine
- external extraction/indexing/retrieval runtime
- Foundry-backed reasoning/orchestration

## 2. Problem statement

Current chat/copilot experiences are limited when users need to bring their own files into the conversation. Users need a controlled way to upload files, convert them into retrievable sources, and use those sources in chat without turning Odoo into a document-processing runtime.

The missing capability is a user-friendly bridge between:
- chat UI in Odoo
- source ingestion/indexing outside Odoo
- grounded responses with clear source status and provenance

## 3. Users

### Primary users
- finance operators
- project/operations users
- internal analysts
- admins and reviewers using Odoo chat/copilot workflows

### Secondary users
- developers/admins validating source ingestion
- support users diagnosing failed uploads/indexing

## 4. Goals

### Product goals
- enable file-backed chat in Odoo 18
- expose source lifecycle clearly in UI
- support grounded answers from uploaded/indexed sources
- keep heavy processing outside Odoo
- maintain auditability and permissions

### Business goals
- reduce context switching to external tools for document Q&A
- improve usability of Odoo copilot workflows
- create a reusable source-ingestion pattern for future agent features

## 5. Non-goals

- arbitrary unbounded chat attachments without lifecycle controls
- full enterprise DMS replacement
- advanced document authoring/collaboration
- global source sync for every external repository in v1
- production-grade cross-tenant sharing in v1

## 6. User stories

### US-1 Upload a source
As a user, I can upload a PDF or supported file from the chat interface so the system can process it for grounded chat.

### US-2 See source status
As a user, I can see whether my source is draft, processing, indexed, active, or failed.

### US-3 Chat against sources
As a user, I can ask questions in chat and receive answers grounded in my active indexed sources.

### US-4 Restrict source usage
As a user, I can choose to restrict the assistant to explicitly selected active sources.

### US-5 Understand failures
As a user, I can see when indexing failed and what the failure reason is.

### US-6 Admin traceability
As an admin/reviewer, I can inspect what source was used and whether the source was active at response time.

## 7. Functional requirements

### FR-1 Chat surface
Provide an Odoo chat interface with:
- message thread
- upload action
- source panel/list
- source status display
- optional source restriction mode

### FR-2 Source registration
Support source registration types in v1:
- uploaded PDF
- uploaded image
- uploaded Office document where extraction path supports it
- linked web URL
- optional Odoo Documents/Knowledge reference if already available in workspace

### FR-3 Source lifecycle
Each source must move through:
- `draft`
- `processing`
- `indexed`
- `failed`
- `inactive` (logical state via active flag)

### FR-4 External ingestion
Upon source submission, Odoo must hand off ingestion work to external services that perform:
- extraction
- normalization
- chunking
- indexing
- callback/result update

### FR-5 Source-grounded chat
Chat requests must support:
- no-source chat
- chat restricted to selected sources
- chat across all active indexed sources visible to that session/user

### FR-6 Provenance
Responses should retain enough metadata to support:
- which sources were eligible
- which sources were actually cited/used
- indexing state at response time

### FR-7 Permissions
Only authorized users may:
- upload sources
- activate/deactivate sources
- access chat sessions and uploaded content

### FR-8 Failure handling
If source processing/indexing fails:
- source status must become `failed`
- error message must be visible
- source must not be usable for grounded chat

### FR-10 Attachment-aware intent resolution

The chat interface must resolve user intent against the active attachment set before falling back to generic clarification.

When a message contains or immediately follows an uploaded attachment, the system must:
1. Detect attachment presence
2. Classify attachment type (invoice, receipt, contract, general document)
3. Classify user intent from the message
4. Route to the appropriate action path

Intent routing examples:
- "extract first" with an uploaded document → run extraction, return parsed fields
- "assess if the tax computation is correct" with an uploaded invoice → run extraction + deterministic validation
- "summarize this" with an uploaded file → summarize the file content
- "check totals" with an uploaded invoice → extract line items, compute totals, compare against printed totals
- "review" with an uploaded document → extract and present key fields for review

Anti-patterns (must not happen):
- Asking "what type of analysis do you want?" when the user said "assess"
- Asking "what record/module do you mean?" when an attachment is present
- Asking "please provide more details" when intent and attachment are both clear

### FR-9 Admin controls
Admins/operators must be able to:
- retry indexing
- deactivate source
- inspect ingestion error
- inspect external IDs/status

## 8. Non-functional requirements

### NFR-1 Odoo responsiveness
Uploading a source must not block the Odoo request cycle longer than necessary to register the source and enqueue handoff.

### NFR-2 Externalized heavy work
All heavy extraction/indexing work must occur outside Odoo workers.

### NFR-3 Auditability
The system must preserve chat/source linkage and source lifecycle history sufficient for operational review.

### NFR-4 Security
Secrets and external service credentials must never be hardcoded in Odoo modules or repo-tracked config.

### NFR-5 Release safety
The feature must be releasable behind evidence-backed gates.

## 9. UX requirements

### Chat panel
The UI should include:
- conversation pane
- composer
- upload button
- source drawer or sidebar
- status chips/badges for source lifecycle

### Source row fields
At minimum show:
- source name
- source type
- status
- active/inactive
- last updated
- error indicator if failed

### Source actions
At minimum support:
- upload/add
- activate/deactivate
- retry indexing
- remove/unlink if allowed

## 10. Success metrics

### Product metrics
- source upload success rate
- indexing success rate
- median time from upload to indexed
- percentage of chats using grounded sources
- percentage of failed sources retried successfully

### Operational metrics
- zero Odoo worker stalls caused by ingestion work
- no unauthorized source access
- evidence pack available for release candidate

## 11. Dependencies

- Odoo chat/copilot surface
- agent-platform ingestion/indexing service
- extraction service (Document Intelligence or equivalent)
- Foundry-backed response path
- Azure-native secret/identity/runtime wiring for production

## 12. Open questions

- exact supported file types in v1 vs later
- whether Odoo Documents/Knowledge integration is in v1 or v2
- whether retrieved responses will expose explicit citations in v1
- whether source ownership is per chat, per user, or reusable across chats in v1

## 13. Release decision rule

The feature is only ship-ready when:
- Odoo tests pass
- agent-platform integration tests pass
- live environment smoke passes
- known exceptions are documented
- evidence pack is attached

---

*Created: 2026-04-09*
