# Tasks - IPAI AI Platform for Odoo CE/OCA 18

## Phase 0: Foundation

### Spec Kit Bundle

- [x] Create `spec/ipai-ai-platform/constitution.md`
- [x] Create `spec/ipai-ai-platform/prd.md`
- [x] Create `spec/ipai-ai-platform/plan.md`
- [x] Create `spec/ipai-ai-platform/tasks.md`

### Architecture Documentation

- [ ] Create `docs/data-model/IPAI_AI_PLATFORM_SCHEMA.dbml`
- [ ] Create `docs/data-model/IPAI_AI_PLATFORM_ERD.mmd` (Mermaid)
- [ ] Create `docs/architecture/IPAI_AI_PLATFORM_ORD.md` (Object Relationship Document)
- [ ] Create `docs/architecture/IPAI_AI_PLATFORM_ARCH.md` (Architecture overview)
- [ ] Create `docs/api/openapi.ipai_ai_platform.yaml`

### CI Infrastructure

- [ ] Create `.github/workflows/ipai-ai-platform-ci.yml`
- [ ] Create `.github/workflows/ipai-ai-ui-build.yml`
- [ ] Add Spectral config for OpenAPI validation

---

## Phase 1: Core AI Enhancement

### ipai_ai_core Module

- [ ] Add `ipai.ai.audit` model for operation logging
  - Fields: operation, user_id, provider_id, request_json, response_json, latency_ms
- [ ] Implement `IpaiAiService` class with RAG orchestration
  - Methods: ask(), search(), get_evidence()
- [ ] Add `ipai.ai.prompt` model for templates
  - Fields: name, template, variables_json, active
- [ ] Implement confidence scoring algorithm
  - Based on citation count, relevance scores
- [ ] Add provider fallback logic
  - Primary → Secondary → Error state

### ipai_ai_agents_ui Module

- [ ] Enhance React App
  - [ ] Add streaming support (SSE)
  - [ ] Add keyboard navigation (Esc to close)
  - [ ] Implement citation preview on hover
  - [ ] Add conversation history sidebar
  - [ ] Add message copy to clipboard
- [ ] Improve error states
  - [ ] Network error handling
  - [ ] Provider unavailable state
  - [ ] Rate limit handling
- [ ] Add accessibility
  - [ ] ARIA labels
  - [ ] Focus management
  - [ ] Screen reader support

### ipai_ai_connectors Module

- [ ] Hardened event intake endpoint
  - Token validation
  - Rate limiting
  - Request validation
- [ ] Token rotation support
  - Multiple active tokens
  - Token expiration
- [ ] Event processing queue
  - Integrate with queue_job
  - Retry logic
- [ ] Event replay functionality
  - Replay by date range
  - Replay by event type

### ipai_ai_sources_odoo Module

- [ ] Chunking strategy
  - Max 1000 chars per chunk
  - Heading-aware splitting
  - Metadata preservation
- [ ] Incremental sync
  - Hash-based change detection
  - Delta exports only
- [ ] Support mail.message indexing
  - Scope by model (project.task, etc.)
  - Filter by date range
- [ ] Support document.page indexing
  - If OCA knowledge module installed
  - Full content extraction

---

## Phase 2: Workspace Primitives

### ipai_workspace_core Module

- [ ] Create `ipai.workspace` model
  - Fields: name, description, visibility, company_id
  - Visibility: private, internal, public
- [ ] Create `ipai.workspace.member` model
  - Fields: workspace_id, user_id, role
  - Roles: member, admin, owner
- [ ] Create space creation wizard
  - Name, visibility inputs
  - Auto-create linked objects
- [ ] Automatic component creation
  - project.project with workspace_id field
  - mail.channel linked to workspace
  - document folder/category
- [ ] Access rule generation
  - Record rules based on membership
  - Group creation per workspace

### Menu Integration

- [ ] Add "My Spaces" top-level menu
- [ ] Space selector in header
- [ ] Recent spaces quick access

---

## Phase 3: Testing & Quality

### Python Tests (Odoo TransactionCase)

- [ ] `test_provider.py`
  - Test provider creation
  - Test default provider logic
  - Test statistics update
- [ ] `test_thread.py`
  - Test thread creation
  - Test message append
  - Test name computation
- [ ] `test_citation.py`
  - Test citation creation
  - Test ranking
- [ ] `test_service.py`
  - Test ask() method (mocked provider)
  - Test search() method
  - Test confidence calculation
- [ ] `test_controllers.py`
  - Test /bootstrap endpoint
  - Test /ask endpoint
  - Test /feedback endpoint
  - Test authentication requirements
- [ ] `test_security.py`
  - Test record rules
  - Test cross-company access denial

### JavaScript Tests (Jest)

- [ ] `odooRpc.test.ts`
  - Test request formatting
  - Test response parsing
  - Test error handling
- [ ] `App.test.tsx`
  - Test initial render
  - Test agent selection
  - Test message sending
- [ ] `MessageCard.test.tsx`
  - Test user message render
  - Test assistant message render
  - Test citation render
- [ ] `Composer.test.tsx`
  - Test input handling
  - Test send button state
  - Test keyboard shortcuts

### E2E Tests (Playwright)

- [ ] `ai_panel.spec.ts`
  - Open panel via Alt+Shift+F
  - Open panel via menu
  - Close panel via Escape
- [ ] `conversation.spec.ts`
  - Send message
  - Receive response
  - View citations
  - Start new conversation
- [ ] `feedback.spec.ts`
  - Submit helpful rating
  - Submit not helpful rating
- [ ] `theme.spec.ts`
  - Toggle dark mode
  - Theme persistence

---

## Phase 4: CI/CD & Documentation

### CI Workflows

- [ ] `ipai-ai-platform-ci.yml`
  - Python linting (black, isort, flake8)
  - Odoo module install test
  - Python unit tests
  - JS unit tests
  - E2E tests (if applicable)
- [ ] `ipai-ai-ui-build.yml`
  - Build React bundle
  - Verify artifact existence
  - Upload artifacts
- [ ] `openapi-validate.yml`
  - Spectral validation
  - Breaking change detection

### Documentation

- [ ] Module READMEs
  - [ ] `addons/ipai/ipai_ai_core/README.md`
  - [ ] `addons/ipai/ipai_ai_agents_ui/README.md`
  - [ ] `addons/ipai/ipai_ai_connectors/README.md`
  - [ ] `addons/ipai/ipai_ai_sources_odoo/README.md`
  - [ ] `addons/ipai/ipai_workspace_core/README.md`
- [ ] API Reference
  - [ ] Endpoint examples with curl
  - [ ] Response schemas
- [ ] Deployment Guide
  - [ ] Environment setup
  - [ ] Supabase configuration
  - [ ] Provider configuration
- [ ] Troubleshooting Guide
  - [ ] Common errors
  - [ ] Debug logging

---

## Verification Checklist

### Before Commit

- [ ] `./scripts/repo_health.sh` passes
- [ ] `./scripts/spec_validate.sh` passes
- [ ] Python linting passes
- [ ] TypeScript compiles
- [ ] All tests pass

### Before PR

- [ ] DBML matches actual models
- [ ] OpenAPI spec is valid
- [ ] Documentation is complete
- [ ] No TODO comments left
- [ ] Commit messages follow convention

### Before Merge

- [ ] All CI checks green
- [ ] Review approved
- [ ] No merge conflicts
- [ ] Changelog updated

---

## Acceptance Criteria

### AI Panel

- [ ] Opens via Alt+Shift+F within 500ms
- [ ] Agent list populated from provider registry
- [ ] Messages display with proper formatting
- [ ] Citations render with clickable links
- [ ] Confidence badge shows correct state
- [ ] Theme toggle persists across sessions

### Workspaces

- [ ] Space creation wizard completes successfully
- [ ] Project, channel, folder created automatically
- [ ] Non-members cannot access private spaces
- [ ] Members can access assigned spaces

### Integrations

- [ ] Connector endpoint accepts valid tokens
- [ ] Invalid tokens rejected with 401
- [ ] Events persisted to database
- [ ] Events queryable in admin UI

### Knowledge Export

- [ ] Cron runs on schedule
- [ ] Tasks exported to kb.chunks
- [ ] KB pages exported (if available)
- [ ] Incremental sync works (no duplicates)

---

*Last updated: 2025-01-06*
