# Tasks: IPAI AI Agent Builder

## Status Legend
- [ ] Not started
- [x] Completed
- [~] In progress
- [-] Blocked

---

## Phase 1: Foundation

### Module Scaffolds
- [x] Create `addons/ipai_ai_agent_builder/` directory structure
- [x] Create `addons/ipai_ai_rag/` directory structure
- [x] Create `addons/ipai_ai_tools/` directory structure
- [x] Write `__manifest__.py` for all modules
- [x] Write `__init__.py` files

### Core Models (ipai_ai_agent_builder)
- [x] Implement `ipai.ai.agent` model
- [x] Implement `ipai.ai.topic` model
- [x] Implement `ipai.ai.tool` model
- [x] Implement `ipai.ai.run` model
- [x] Implement `ipai.ai.run.event` model
- [x] Implement `ipai.ai.tool.call` model

### Security
- [x] Create `ir.model.access.csv` for all models
- [x] Define security groups (user, manager, admin)
- [x] Create record rules for multi-company

---

## Phase 2: RAG Pipeline

### Models (ipai_ai_rag)
- [x] Implement `ipai.ai.source` model
- [x] Implement `ipai.ai.chunk` model
- [x] Implement `ipai.ai.embedding` model

### Services
- [x] Implement `IpaiAiChunkingService`
  - [x] Fixed-size chunking
  - [x] Overlap handling
  - [x] SHA-256 content hashing
  - [x] Token counting
- [x] Implement `IpaiAiEmbeddingService`
  - [x] OpenAI embeddings integration
  - [x] Batch processing
  - [x] Cache invalidation
- [x] Implement `IpaiAiRetrievalService`
  - [x] Cosine similarity calculation
  - [x] Stable tie-breaking
  - [x] Top-k retrieval

### Source Ingestion
- [x] File content extraction
- [x] URL content fetching
- [x] Model field extraction
- [x] Ingestion status tracking

---

## Phase 3: LLM Integration

### Provider Abstraction
- [x] Define `IpaiAiProviderBase` interface
- [x] Implement `IpaiAiProviderOpenAI`
- [x] Implement `IpaiAiProviderGoogle`

### Prompt Assembly
- [x] System prompt injection
- [x] Topic instructions formatting
- [x] RAG context formatting
- [x] Tool definitions formatting

### Response Handling
- [x] Parse LLM response
- [x] Extract tool calls
- [x] Handle errors

---

## Phase 4: Tool Framework

### Tool Registry (ipai_ai_tools)
- [x] Python entrypoint loader
- [x] Permission validator
- [x] Input/output schema

### Built-in Tools
- [x] `crm_create_lead` tool
- [x] `calendar_create_event` tool
- [x] `sale_create_order` tool

### Execution Engine
- [x] `IpaiAiToolExecutor` service
- [x] Permission gating
- [x] Dry-run support
- [x] Audit logging

---

## Phase 5: API Layer

### REST Controllers
- [x] `POST /ipai/ai/v1/agent/<id>/chat`
- [x] `POST /ipai/ai/v1/source/<id>/ingest`
- [x] `POST /ipai/ai/v1/tool/<key>/invoke`
- [x] `GET /ipai/ai/v1/agent/<id>/runs`

### Authentication
- [x] Session validation
- [x] Permission checking
- [x] Error responses

---

## Phase 6: Config-as-Code

### YAML Schema
- [x] Define agent schema
- [x] Define topic schema
- [x] Define tool mapping
- [x] Define source schema

### Seed Script
- [x] Create `scripts/ipai_ai_seed.sh`
- [x] Implement idempotent loading
- [x] Validation logic

### Default Configurations
- [x] Create `config/ipai_ai/agents/default.yaml`
- [x] Create example agent configs

---

## Phase 7: Testing

### Unit Tests
- [x] Test chunking determinism
- [x] Test embedding cache keys
- [x] Test retrieval tie-breaking
- [x] Test tool permission checking

### Integration Tests
- [x] Test YAML → agent creation
- [x] Test source ingestion
- [x] Test RAG query flow
- [x] Test tool execution audit

---

## Phase 8: Documentation

### Module Documentation
- [x] `ipai_ai_agent_builder/README.md`
- [x] `ipai_ai_rag/README.md`
- [x] `ipai_ai_tools/README.md`

### XML Data
- [x] Demo agents
- [x] Default tools

---

## Verification

### Pre-Commit Checks
- [ ] `python3 -m compileall` passes
- [ ] `black --check` passes
- [ ] `isort --check` passes
- [ ] `flake8` passes

### CI Checks
- [ ] `./scripts/repo_health.sh` passes
- [ ] `./scripts/spec_validate.sh` passes
- [ ] Module install succeeds
- [ ] All tests pass

---

## Notes

- Ensure all models follow OCA naming conventions
- Use `_description` on all models
- Include proper `_inherit` for extending existing models
- Keep security restrictive by default
