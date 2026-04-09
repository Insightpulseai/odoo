# Constitution — Chat Interface with File Upload

## Purpose

Define the non-negotiable engineering and product rules for delivering an Odoo 18 chat interface with file upload, source ingestion, retrieval-backed chat, and evidence-gated release.

## Scope

This constitution applies to:
- Odoo 18 CE user-facing chat surfaces
- Odoo-side source metadata and workflow state
- external ingestion, extraction, indexing, and retrieval services
- Foundry-backed chat/reasoning flows
- release, testing, and evidence requirements

## Core doctrine

### 1. Odoo owns workflow state, not heavy AI runtime
Odoo must own:
- chat session records
- user-visible source metadata
- approval/review state
- audit-visible outcomes
- permissions and ERP-native UX

Odoo must not own:
- OCR engines
- heavyweight document parsing
- embedding generation
- vector retrieval infrastructure
- primary model orchestration runtime

### 2. File upload is a managed source workflow
The feature is not "arbitrary blob upload into chat."
It is a managed source pipeline:
- upload or link source
- process
- index
- activate/deactivate
- chat against active indexed sources

### 3. Deterministic before generative
AI may:
- extract
- summarize
- classify
- explain
- draft responses

Deterministic code must decide:
- source lifecycle state
- upload/indexing success/failure
- validation outcomes for structured financial/compliance flows
- access control
- workflow state transitions

### 4. Thin Odoo bridge doctrine
Any `ipai_*` Odoo addon created for this feature must remain thin.
It may provide:
- models
- views
- actions
- controllers
- queue hooks
- API bridge adapters

It must not reimplement the external ingestion/retrieval platform inside Odoo.

### 5. Azure-native external service doctrine
External services must assume:
- Azure Document Intelligence for extraction where applicable
- Microsoft Foundry for model/runtime orchestration
- Azure-native secret and identity handling
- private-by-default service posture when productionized

### 6. Evidence-gated release doctrine
The feature is not ship-ready unless all are true:
- product acceptance criteria satisfied
- Odoo tests green
- agent-platform/integration tests green
- live smoke path green in target environment
- evidence pack attached

## Ownership model

### `odoo`
Owns:
- chat UI
- source registration UX
- source metadata
- permissions
- chat session records
- ERP/workflow state

### `agent-platform`
Owns:
- file ingestion
- extraction
- chunking
- indexing
- retrieval
- Foundry request orchestration
- source status callbacks

### `infra`
Owns:
- Azure resource provisioning
- secrets and identity wiring
- runtime diagnostics
- deployment/release infrastructure

### `docs`
Owns:
- architecture notes
- release/evidence docs
- runbooks

## Required quality gates

### Odoo gate
- `TransactionCase` coverage for source lifecycle/business rules
- `HttpCase` or browser flow for upload and chat UX
- negative-path tests for failed indexing and inactive sources

### Agent-platform gate
- extraction smoke
- indexing/retrieval smoke
- Foundry integration smoke
- API contract tests with Odoo bridge

### Infra gate
- health probes
- managed identity/secret access validation
- runtime ingress checks
- rollback-ready deployment path

## Attachment-grounded intent rule

If a user message includes an uploaded file or directly follows an uploaded file in the same chat turn sequence, the system must treat the attachment as the primary subject by default.

The assistant must not ask generic clarification questions that ignore the attachment context when the user has already expressed a valid intent such as:
- extract
- summarize
- review
- assess
- validate
- check discrepancy
- check totals
- check compliance

The system may ask follow-up questions only when:
- multiple attachments create ambiguity about which one the user means
- the requested task is materially under-specified beyond what the document and user profile can supply
- the requested validation requires a missing business parameter not inferable from the document or profile

This rule is non-negotiable. Violating it — by asking "what type of analysis?" or "which record?" when an attachment and valid intent are present — is a product defect.

## Non-goals

- building a full general-purpose document management platform
- replacing Odoo 19 native AI Agents implementation one-to-one
- storing large file processing logic inside Odoo workers
- making AI authoritative for finance/compliance decisions
- bypassing evidence-gated release process

## Final rule

If a design choice improves convenience but violates the Odoo-thin-bridge, deterministic-control, or evidence-gated doctrines, the design choice must be rejected.

---

*Created: 2026-04-09*
