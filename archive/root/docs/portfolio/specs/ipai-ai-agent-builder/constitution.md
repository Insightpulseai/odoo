# Constitution: IPAI AI Agent Builder

## Purpose

This document defines the non-negotiable rules and constraints for the IPAI AI Agent Builder module, which provides Odoo 19 AI Agents feature parity for CE/OCA deployments.

## Non-Negotiable Rules

### 1. CE-Only, OCA-First

- **NO** Odoo Enterprise code or modules
- **NO** odoo.com IAP dependencies
- **NO** proprietary Odoo services
- Prefer OCA modules over custom implementation where available
- Custom code (`ipai_*`) only for truly unique requirements

### 2. Configuration Over Code

- All agent/topic/tool/source definitions MUST be expressible via YAML config
- CLI-driven setup: no manual UI steps required for deployment
- Idempotent seed scripts for reproducible environments
- XML data files for initial configuration

### 3. Deterministic RAG Pipeline

- **Fixed chunking**: consistent `chunk_size` (default: 1000 tokens) and `overlap` (default: 200 tokens)
- **Stable hashing**: SHA-256 content hash for deduplication
- **Reproducible retrieval**: cosine similarity with stable tie-breaking (`score DESC, chunk_id ASC`)
- **Prompt assembly order**: system prompt + topic instructions + retrieved context + user message

### 4. Audited Tool Execution

- Tools execute ONLY via structured protocol (JSON-RPC style)
- **NO** freeform database writes outside tool boundaries
- Every invocation logged: `who`, `what`, `when`, `input`, `output`, `status`
- Permission gating via Odoo groups and record rules
- Support for `dry_run` mode on risky operations

### 5. Provider Abstraction

- Support multiple LLM providers (ChatGPT, Gemini minimum)
- Provider selection via configuration, not code changes
- API keys via environment variables only
- **NO** hardcoded credentials

### 6. Security

- Secrets stored in environment variables, never in code/database
- RLS (Row-Level Security) awareness for multi-company
- Tool permissions mapped to Odoo security groups
- Input sanitization on all user-provided content

### 7. Observability

- Structured logging for all operations
- Latency metrics for LLM calls
- Database tables for audit trail:
  - `ipai.ai.run` - conversation runs
  - `ipai.ai.run.event` - detailed events
  - `ipai.ai.tool.call` - tool invocations
  - `ipai.ai.chunk` - RAG chunks
  - `ipai.ai.embedding` - vector embeddings

### 8. Testing Requirements

- Unit tests for: chunking determinism, embedding cache keys, retrieval tie-breaking
- Integration tests for: YAML config loading, RAG pipeline end-to-end, tool execution audit
- All tests must pass in CI before merge
- No changes to existing parity scoring logic

### 9. API Contract

- REST endpoints with JSON payloads
- Versioned API paths (`/ipai/ai/v1/...`)
- OpenAPI/Swagger documentation
- Rate limiting considerations

### 10. Backwards Compatibility

- New features must not break existing `ipai_ask_ai` functionality
- Migration scripts for schema changes
- Deprecation notices before removal

## Acceptance Criteria

A compliant implementation MUST:

1. Allow creating agents from YAML configuration without UI interaction
2. Support ChatGPT and Gemini providers via environment configuration
3. Execute RAG queries with deterministic, reproducible results
4. Execute at least 3 real tools (CRM lead, calendar event, sale order) with full audit trail
5. Pass all unit and integration tests
6. Generate no Python syntax errors on `compileall`
7. Pass OCA-style linting (`black`, `isort`, `flake8`)
