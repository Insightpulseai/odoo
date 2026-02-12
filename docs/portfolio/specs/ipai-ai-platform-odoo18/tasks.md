# Tasks — IPAI AI Platform for Odoo CE/OCA 18

## Status Legend

- [ ] Pending
- [x] Completed
- [~] In Progress
- [-] Blocked

---

## 1. Spec Kit & Documentation

### 1.1 Spec Bundle
- [x] Create `spec/ipai-ai-platform-odoo18/constitution.md`
- [x] Create `spec/ipai-ai-platform-odoo18/prd.md`
- [x] Create `spec/ipai-ai-platform-odoo18/plan.md`
- [x] Create `spec/ipai-ai-platform-odoo18/tasks.md`

### 1.2 Architecture Documentation
- [ ] Create `docs/architecture/IPAI_AI_PLATFORM_ARCH.md`
- [ ] Create runtime snapshot with container/DB names
- [ ] Create data flow diagrams
- [ ] Document security boundaries

### 1.3 Data Model Documentation
- [ ] Create `docs/architecture/IPAI_AI_PLATFORM_ERD.dbml`
- [ ] Document all new tables and relationships
- [ ] Include Supabase KB schema
- [ ] Generate Mermaid ERD

### 1.4 Object Relationship Document
- [ ] Create `docs/ord/IPAI_AI_PLATFORM_ORD.md`
- [ ] Define ownership and access patterns
- [ ] Document object lifecycles

### 1.5 API Documentation
- [ ] Create `docs/api/openapi.ipai_ai_platform.yaml`
- [ ] Document all JSON-RPC endpoints
- [ ] Include Supabase RPC contracts
- [ ] Add request/response examples

---

## 2. Database & Schema

### 2.1 Supabase KB Schema
- [ ] Create `db/migrations/YYYYMMDD_ipai_kb_chunks.sql`
- [ ] Add `kb.chunks` table with pgvector
- [ ] Add unique constraint for upsert
- [ ] Create `kb.search_chunks` RPC
- [ ] Create `kb.search_chunks_text` RPC
- [ ] Test migrations locally

---

## 3. Module: ipai_ai_agents_ui

### 3.1 Odoo Module Structure
- [ ] Create `addons/ipai/ipai_ai_agents_ui/__manifest__.py`
- [ ] Create `addons/ipai/ipai_ai_agents_ui/__init__.py`
- [ ] Add security files (`ir.model.access.csv`)
- [ ] Add menu and views XML

### 3.2 JavaScript Assets
- [ ] Create command palette hook (`command_palette.js`)
- [ ] Create client action wrapper (`ai_panel_react_action.js`)
- [ ] Configure `web.assets_backend`

### 3.3 React UI Application
- [ ] Create `ui/` directory with package.json
- [ ] Configure Vite for IIFE build
- [ ] Implement `App.tsx` with Fluent UI
- [ ] Implement agent selector dropdown
- [ ] Implement chat message list
- [ ] Implement input composer
- [ ] Implement citation rendering
- [ ] Implement theme switching (light/dark)
- [ ] Implement loading and error states

### 3.4 Build & Integration
- [ ] Create build script (`scripts/copy-dist.mjs`)
- [ ] Build IIFE bundle
- [ ] Commit `static/lib/ipai_ai_ui.iife.js`
- [ ] Commit `static/lib/ipai_ai_ui.css`
- [ ] Test in Odoo

---

## 4. Module: ipai_ai_connectors

### 4.1 Odoo Module Structure
- [ ] Create `addons/ipai/ipai_ai_connectors/__manifest__.py`
- [ ] Create `addons/ipai/ipai_ai_connectors/__init__.py`
- [ ] Create models (`ipai.ai.event`)
- [ ] Add security files
- [ ] Add menu and views XML

### 4.2 Controller Endpoints
- [ ] Create `/ipai_ai_connectors/event` endpoint
- [ ] Implement token authentication
- [ ] Implement event persistence
- [ ] Add validation for required fields

### 4.3 Admin UI
- [ ] Create event list view (tree)
- [ ] Create event detail view (form)
- [ ] Add filters (source, event_type, processed)

---

## 5. Module: ipai_ai_sources_odoo

### 5.1 Odoo Module Structure
- [ ] Create `addons/ipai/ipai_ai_sources_odoo/__manifest__.py`
- [ ] Create `addons/ipai/ipai_ai_sources_odoo/__init__.py`
- [ ] Create exporter model (`ipai.kb.exporter`)
- [ ] Add cron job definition

### 5.2 Exporter Logic
- [ ] Implement `cron_export_recent()` method
- [ ] Implement `_collect_tasks()` for project.task
- [ ] Implement `_collect_kb_pages()` for document.page
- [ ] Implement Supabase REST upsert
- [ ] Add error handling and logging

### 5.3 Configuration
- [ ] Document required environment variables
- [ ] Add lookback window config
- [ ] Add tenant mapping logic

---

## 6. Testing

### 6.1 Unit Tests (Python)
- [ ] Create `tests/test_ai_agent_basic.py`
- [ ] Test agent CRUD operations
- [ ] Test thread/message creation
- [ ] Test retriever with mocked Supabase
- [ ] Test LLM provider with mocked API
- [ ] Test exporter payload generation
- [ ] Test connector token validation

### 6.2 Integration Tests
- [ ] Test Odoo HTTP routes (smoke tests)
- [ ] Test Supabase RPC contract (mocked)
- [ ] Test end-to-end ask flow

### 6.3 E2E Tests (Playwright)
- [ ] Test command palette opens panel
- [ ] Test send message and receive response
- [ ] Test citations render correctly
- [ ] Test error state display
- [ ] Test theme switching

---

## 7. CI/CD

### 7.1 Workflow Creation
- [ ] Create `.github/workflows/ipai_ai_platform_ci.yml`
- [ ] Add UI build job
- [ ] Add Python lint job
- [ ] Add Odoo install verification job
- [ ] Add test execution job
- [ ] Add OpenAPI validation job

### 7.2 Quality Gates
- [ ] Verify React bundle exists
- [ ] Verify module installs cleanly
- [ ] Verify all tests pass
- [ ] Verify OpenAPI spec is valid

---

## 8. Deployment

### 8.1 Module Installation
- [ ] Add modules to addons path
- [ ] Run upgrade command
- [ ] Verify in Odoo Apps list

### 8.2 Environment Setup
- [ ] Configure Supabase credentials
- [ ] Configure LLM API key
- [ ] Configure connector token
- [ ] Test all integrations

### 8.3 Verification
- [ ] Open Ask AI panel
- [ ] Send test question
- [ ] Verify citation appears
- [ ] Check connector endpoint
- [ ] Verify exporter cron runs

---

## 9. Documentation Updates

### 9.1 Repository Documentation
- [ ] Update `CLAUDE.md` with new modules
- [ ] Update `docs/IPAI_MODULES_INDEX.md`
- [ ] Add entries to SITEMAP.md

### 9.2 User Documentation
- [ ] Create module README.md files
- [ ] Document configuration steps
- [ ] Add troubleshooting guide

---

## Completion Checklist

Before marking complete, verify:

- [ ] All modules install without errors
- [ ] React panel opens and functions
- [ ] Ask AI returns responses with citations
- [ ] Connector accepts events with valid token
- [ ] Exporter syncs data to Supabase
- [ ] All tests pass in CI
- [ ] Documentation is complete and accurate
- [ ] Code follows CLAUDE.md conventions

---

## Notes

- Priority order: Modules → Tests → Docs → CI
- Build React bundle locally before committing
- Test with actual Supabase before deploying
- Keep modules minimal; use existing ipai_ai_core
