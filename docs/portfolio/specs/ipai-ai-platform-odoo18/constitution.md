# Constitution — IPAI AI Platform for Odoo CE/OCA 18

## Purpose

Deliver a production-grade AI platform layer for Odoo CE/OCA 18 that provides:

- A **Fluent UI (React v9) design system shell** for platform modules
- A **production-grade AI Agents capability** (Ask AI + sources + connectors + RAG)
- **Minimal custom IPAI modules**; OCA-first for everything else
- **Deterministic architecture documentation** + testability + API docs

## Non-Negotiables

### 1. OCA-First Philosophy

```
Config → OCA → Delta (ipai_*)

1. Use Odoo's built-in configuration first
2. Use vetted OCA community modules second
3. Only create ipai_* for truly custom needs
```

### 2. No Core Patching

- Never modify Odoo core; extend via addons and `web.assets_backend`
- Use inheritance (`_inherit`) and extension patterns only
- Keep custom JavaScript isolated in client actions

### 3. Read-Only AI by Default

- Agents may **read** data and **propose** actions
- Execution requires **explicit user confirmation**
- No autonomous write operations without approval workflow

### 4. Multi-Tenant Ready

- Support both "multi-company in one DB" and "DB-per-tenant" patterns
- All data models include `company_id` for isolation
- Record rules enforce company-level access boundaries

### 5. Deterministic Documentation

- Keep `.drawio` sources; export PNG via CI
- Fail PRs on schema/docs mismatch
- Auto-generate DBML/ERD from Odoo models

### 6. Design System Consistency

- Fluent UI tokens drive React shell
- Odoo SCSS theme only for minimal bridging
- Use `packages/ipai-design-tokens` for shared tokens

### 7. Auditability

- Every AI response must include citations when evidence exists
- No invented sources or hallucinated URLs
- Full trace logging for retrieval + generation steps

### 8. Secrets Management

- All secrets via env vars / CI secrets / DO App env
- Never commit API keys, tokens, or credentials
- Use `.env.example` for documentation only

## Scope Boundaries

### In Scope

- AI Panel UX (React+Fluent) inside Odoo
- Agent registry + threads + messages + sources metadata
- Connector intake endpoint for n8n/GitHub/etc
- Exporter from Odoo objects → Supabase KB
- Supabase KB schema + RPCs
- OpenAPI documentation for Odoo JSON endpoints + Supabase RPC contract
- Comprehensive tests (unit, integration, e2e, contract)

### Out of Scope (By Design)

- Replacing all Odoo UI with React (keep Odoo's OWL for standard views)
- Fully autonomous write-enabled agents (always require confirmation)
- Re-implementing Notion's entire document editor in Odoo
- Enterprise module dependencies or IAP integrations

## Quality Gates

### CI Requirements

1. Python lint (black, isort, flake8)
2. Odoo module install/upgrade verification
3. JS build (React bundle compilation)
4. Unit tests (Python TransactionCase)
5. Integration tests (Supabase mock, Odoo test env)
6. OpenAPI validation (spectral)

### Runtime Requirements

1. "No empty/error states": AI panel must handle missing KB/LLM with deterministic error copy
2. Perf: "Ask" call returns within 5s P95 with warm cache; 15s hard timeout
3. Citation coverage: >95% answers with at least 1 valid citation when evidence exists

## Module Naming Convention

All IPAI modules follow the pattern: `ipai_<domain>_<feature>`

| Domain | Prefix Pattern | Examples |
|--------|---------------|----------|
| AI | `ipai_ai_*` | `ipai_ai_core`, `ipai_ai_agents_ui` |
| Agent | `ipai_agent_*` | `ipai_agent_core` |
| Platform | `ipai_platform_*` | `ipai_platform_workflow` |

## Integration Points

### Supabase KB

- Primary use: Vector search and RAG retrieval
- RPC: `kb.search_chunks` (vector), `kb.search_chunks_text` (fallback)
- NOT used for primary Odoo data storage

### n8n Workflows

- Integration hub for external systems
- Inbound events via `/ipai_ai_connectors/event`
- Outbound triggers via Odoo automated actions

### MCP Servers

- Located in `mcp/servers/odoo-erp-server/`
- Provides Odoo ERP tools for AI agents
- Coordinates with platform via MCP protocol

## Verification Commands

```bash
# Run before every commit
./scripts/repo_health.sh       # Check repo structure
./scripts/spec_validate.sh     # Validate spec bundles
./scripts/ci_local.sh          # Run local CI checks
```

## References

- Root constitution: `/spec/constitution.md`
- CLAUDE.md: `/CLAUDE.md`
- Existing AI modules: `addons/ipai/ipai_ai_core/`, `addons/ipai/ipai_agent_core/`
