# Constitution - IPAI AI Platform for Odoo CE/OCA 18

## Purpose

Deliver a production-grade "AI-powered platform layer" for Odoo CE/OCA 18 that provides:

- A **Fluent UI v9 (React)** design system shell for all IPAI platform modules
- A **production-grade AI Agents capability** (Ask AI + RAG + sources + connectors)
- **Notion Business-style teamspaces/workspaces** using Odoo primitives
- **Minimal custom IPAI modules**; OCA-first for everything else
- **Deterministic architecture documentation** + comprehensive testing + API docs

---

## Principles

### 1. OCA-First Architecture

Use OCA addons where available; only create IPAI modules for:
- Glue code (integration bridges)
- UX shell (Fluent UI React components)
- AI capabilities (RAG, agents, connectors)

### 2. No Core Patching

Never modify Odoo core modules. Extend via:
- Custom addons
- `web.assets_backend` for frontend assets
- Inherited views and models

### 3. Read-Only AI by Default

AI Agents operate in read-only mode:
- May read records and search data
- May propose actions with previews
- Execution requires explicit user confirmation
- Write operations require elevated permissions and audit logging

### 4. Multi-Tenant Ready

Support both deployment patterns:
- **Multi-company in single DB**: For internal departmental separation
- **DB-per-tenant**: For SaaS-style client isolation

### 5. Deterministic Documentation

- Maintain `.drawio` sources for diagrams
- Export PNGs via CI for version control
- DBML/ERD must match actual schema
- Fail PRs on documentation drift

### 6. Design System Consistency

- **Fluent UI v9 tokens** drive React shell styling
- **Odoo SCSS theme** provides minimal bridging
- No custom CSS that conflicts with either system

### 7. Auditability

Every AI response must include:
- Citations when evidence exists
- Confidence scores
- Source provenance
- No invented sources or hallucinated citations

### 8. Secrets Management

All secrets via:
- Environment variables
- CI secrets (GitHub Actions)
- DigitalOcean App Platform env
- Never committed to repository

---

## Non-Negotiables

### Security

1. **RLS-style isolation**: Record rules enforce tenant boundaries
2. **Token validation**: All API endpoints validate authentication
3. **Audit trails**: AI operations logged with user context
4. **PII protection**: Redaction hooks at ingestion/retrieval

### Quality

1. **Test coverage**: Unit, integration, and E2E tests required
2. **CI gates**: All PRs must pass linting, type checks, and tests
3. **OpenAPI validation**: API specs must be valid and complete
4. **Schema validation**: DBML must match deployed models

### Operations

1. **Health checks**: All services expose health endpoints
2. **Structured logging**: JSON logs with correlation IDs
3. **Graceful degradation**: Fallback paths for service failures
4. **Backup safety**: No destructive operations without confirmation

---

## Scope Boundaries

### In Scope

- AI Panel UX (React + Fluent UI) inside Odoo webclient
- Agent registry + threads + messages + sources metadata
- Connector intake endpoint for n8n/GitHub/Slack/external systems
- Exporter from Odoo objects to Supabase KB
- Supabase KB schema + RPCs (vector + text search)
- OpenAPI documentation for all Odoo JSON endpoints
- Supabase RPC contract documentation
- Comprehensive test suites (unit, integration, E2E)
- CI/CD workflows for validation

### Out of Scope (by design)

- Replacing all Odoo UI with React (selective enhancement only)
- Fully autonomous write-enabled agents (read-only by default)
- Re-implementing Notion's entire document editor in Odoo
- Training custom ML models within Odoo
- Real-time collaboration (websockets) - use Odoo's built-in patterns

---

## Quality Gates

### CI Must Run

1. Python linting (black, isort, flake8)
2. Odoo module install/upgrade verification
3. JavaScript/TypeScript build
4. Unit tests (Python + Jest)
5. Integration tests (Odoo test framework)
6. E2E tests (Playwright)
7. OpenAPI spec validation (Spectral)
8. DBML schema validation

### UX Requirements

- "No empty states": AI panel handles missing KB/LLM gracefully
- Deterministic error messages with actionable guidance
- Loading states for all async operations
- Keyboard accessibility (Alt+Shift+F to open panel)

### Performance

- "Ask" call returns within **5s P95** (warm cache)
- **15s hard timeout** for all AI operations
- Evidence retrieval < 500ms P95
- UI interactions < 100ms response time

---

## Container & Database Naming

### Containers

| Service | Container Name | Port |
|---------|---------------|------|
| Odoo Web | `odoo-erp-prod` | 8069 |
| PostgreSQL | `postgres` | 5432 |
| Redis (optional) | `redis` | 6379 |
| n8n | `n8n` | 5678 |
| Supabase | External (managed) | 443 |

### Databases

| Purpose | Database Name | Schema |
|---------|--------------|--------|
| Odoo Main | `odoo` | `public` |
| Supabase KB | `postgres` | `kb` |
| Supabase Auth | `postgres` | `auth` |

### Volumes

| Volume | Mount Path | Purpose |
|--------|-----------|---------|
| `odoo-web-data` | `/var/lib/odoo` | Filestore |
| `odoo-db-data` | `/var/lib/postgresql/data` | Database |

---

## Module Inventory

### IPAI Custom Modules (Minimal)

| Module | Purpose | Dependencies |
|--------|---------|--------------|
| `ipai_ai_core` | Provider registry, threads, messages, citations | `base`, `mail`, `web` |
| `ipai_ai_agents_ui` | React + Fluent UI panel | `web`, `ipai_ai_core` |
| `ipai_ai_connectors` | Inbound event intake | `base`, `mail` |
| `ipai_ai_sources_odoo` | Odoo → Supabase KB export | `base`, `project` |
| `ipai_ai_prompts` | Prompt templates | `ipai_ai_core` |
| `ipai_ai_audit` | AI operation audit logs | `ipai_ai_core` |
| `ipai_web_fluent2` | Fluent 2 design tokens | `web`, `mail` |
| `ipai_platform_theme` | Platform theming | `web` |
| `ipai_workspace_core` | Workspace/teamspace primitives | `base`, `project`, `mail` |

### OCA Dependencies

| Category | Modules |
|----------|---------|
| Server Tools | `queue_job`, `base_exception`, `sentry` |
| Knowledge | `document_page`, `document_page_project` |
| Project | `project_*` addons |
| Web | `web_responsive`, `web_refresher` |

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| AI Panel Adoption | 30% weekly active users | Analytics |
| Citation Coverage | > 95% answers with citations | Audit logs |
| Response Latency | P95 < 5s | APM metrics |
| Error Rate | < 1% | Error tracking |
| Test Coverage | > 80% | Coverage reports |
| Documentation Completeness | 100% endpoints documented | CI validation |

---

*Last updated: 2025-01-06*
