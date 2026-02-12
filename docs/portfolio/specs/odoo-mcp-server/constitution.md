# Odoo MCP Server - Constitution

## Purpose

Model Context Protocol (MCP) server for Odoo CE 18.0 XML-RPC integration, enabling Claude Code to directly interact with Odoo ERP via natural language commands.

## Non-Negotiable Rules

### 1. XML-RPC Protocol Compliance
- **MUST** use Odoo's official XML-RPC/JSON-RPC API exclusively
- **MUST NOT** directly access PostgreSQL database (use Odoo ORM)
- **MUST** support both `execute_kw` (sync) and `execute` (async) methods
- **MUST** handle Odoo API version differences (CE 18.0 specifics)

### 2. Security & Authentication
- **MUST** use environment variables for credentials (never hardcode)
- **MUST** support multiple authentication methods:
  - Session-based (cookie persistence)
  - API key (if configured in Odoo)
  - Username/password (development only)
- **MUST** implement connection pooling with max 5 concurrent connections
- **MUST** validate RLS (Row-Level Security) context for multi-tenant operations

### 3. Multi-Employee/Multi-Agency Model
- **MUST** distinguish between **Employee Codes** and **Agency IDs**:
  - Employee Code: Internal TBWA staff identifier (RIM, CKVC, BOM, etc.)
  - Agency ID: Legal entity/client identifier (res.partner records)
- **MUST** maintain proper context switching for multi-employee operations
- **MUST** enforce proper access control based on user roles
- **MUST** support batch operations across multiple employees

### 4. Error Handling
- **MUST** return structured errors with Odoo fault codes
- **MUST** implement retry logic with exponential backoff (max 3 retries)
- **MUST** gracefully handle session timeouts and re-authenticate
- **MUST** provide actionable error messages (not raw XML-RPC faults)

### 5. Performance Requirements
- **MUST** use `search_read` instead of `search` + `read` (single RPC call)
- **MUST** implement result pagination (default: 100 records, max: 1000)
- **MUST** cache frequently accessed data (chart of accounts, partners, products)
- **MUST** support lazy loading for large recordsets

### 6. Tool Naming Convention
All tools must follow pattern: `odoo:<domain>:<action>`

Examples:
- `odoo:account:create-journal-entry`
- `odoo:partner:query-vendors`
- `odoo:bir:generate-1601c`
- `odoo:project:list-tasks`

### 7. Integration Points
- **MUST** coordinate with n8n workflows via webhook triggers
- **MUST** sync with Supabase task queue for async operations
- **MUST** send notifications to Mattermost on critical operations
- **MUST** log all mutations to Odoo audit trail (`mail.message`)

## Scope Boundaries

### In Scope
✅ CRUD operations on core models (account.move, res.partner, project.task)
✅ BIR tax form generation and filing workflows
✅ Month-end closing orchestration
✅ Multi-employee expense/invoice processing
✅ Real-time data queries for dashboards
✅ Approval workflow triggers

### Out of Scope
❌ Direct PostgreSQL database access
❌ Odoo module installation/upgrade (use odoo-bin CLI)
❌ System configuration changes (use UI or config files)
❌ Custom report generation (use Odoo's reporting engine)
❌ File system operations (use Odoo attachments API)

## Architectural Constraints

### Technology Stack
- **Runtime**: Node.js 20+ or Python 3.11+
- **Protocol**: MCP SDK (@modelcontextprotocol/sdk)
- **Transport**: stdio (local) or SSE (remote via coordinator)
- **Testing**: Jest (Node.js) or pytest (Python)

### Dependencies
- Odoo CE 18.0 running on `http://odoo-erp-prod:8069`
- PostgreSQL 15 (accessed via Odoo ORM only)
- n8n for workflow orchestration
- Supabase task queue for async job management

### Deployment
- **Local**: Run via `npx` or `python -m` with stdio transport
- **Remote**: Deploy to DigitalOcean App Platform with SSE coordinator
- **Config**: Use `.env` files (never commit credentials)

## Success Criteria

1. ✅ Claude can create journal entries via natural language
2. ✅ Claude can query AP aging without manual SQL
3. ✅ Claude can trigger BIR form generation for 8 employees
4. ✅ Claude can orchestrate month-end close workflows
5. ✅ All operations audit-logged in Odoo (`mail.message`)
6. ✅ Zero direct database access (100% via Odoo API)
7. ✅ Response time <2s for queries, <5s for mutations
8. ✅ Integration tests cover all 50+ tools

## Failure Modes & Mitigation

| Failure | Impact | Mitigation |
|---------|--------|------------|
| Session timeout | 🔴 Critical | Auto-reconnect with exponential backoff |
| Invalid employee code | 🟡 Medium | Validate against `hr.employee` before operations |
| Concurrent write conflicts | 🟡 Medium | Implement optimistic locking with version checks |
| n8n webhook timeout | 🟢 Low | Queue to Supabase task bus, retry asynchronously |
| Large recordset OOM | 🟡 Medium | Enforce pagination limits, lazy loading |

## Compliance Requirements

### TBWA Finance SOPs
- All financial mutations require audit trail
- Multi-agency operations must enforce segregation of duties
- BIR forms must follow official eBIRForms specifications

### Data Privacy
- Employee codes are NOT PII (safe to log)
- Partner TINs are PII (redact from logs)
- Financial amounts logged at summary level only

### Performance SLAs
- Query operations: <2s (P95)
- Mutation operations: <5s (P95)
- Batch operations: <30s for 100 records (P95)
- Cache hit ratio: >80% for reference data
