# Enterprise Parity Constitution

## Non-Negotiable Rules

### 1. CE-Only Stack
- **No Odoo Enterprise modules** may be installed or referenced
- **No odoo.com IAP** dependencies (SMS, email credits, etc.)
- All Enterprise-equivalent features must use OCA modules or IPAI custom modules
- `ipai_enterprise_bridge` is the ONLY allowed "EE replacement" layer

### 2. Single Source of Truth
- **Odoo** is SoR for transactional data (expenses, POs, GL, projects)
- **Supabase** is ops hub for external integrations, agent runs, portal sessions
- **No duplicate master data** across systems
- All sync is event-driven with idempotent handlers

### 3. Audit Trail Mandatory
- Every state change must be logged with:
  - Timestamp (UTC)
  - User/agent ID
  - Before/after state
  - Action type
- Audit data retained for 10 years (BIR compliance)
- No silent writes from agents without logging

### 4. Approval Gating for Writes
- Agent actions that create/update/delete records MUST:
  - Log to `ops.agent_audit_log`
  - For sensitive models: require human approval before commit
- Sensitive models: `account.move`, `purchase.order`, `hr.expense.sheet`

### 5. Design System Consistency
- `ipai_design_system` tokens apply to:
  - Odoo backend theme
  - Portal frontends
  - Mobile apps
  - Superset dashboards
- No ad-hoc styling that deviates from token system

### 6. Parity Claims Must Be Tested
- No capability may be declared "at parity" without:
  - Functional tests covering core flows
  - CI gate that prevents regression
  - Documentation of gaps (if any)

### 7. Security Boundaries
- Supabase RLS aligned to Odoo permission groups
- MCP tools enforce role-based access
- No elevated privileges in automation without explicit grant

### 8. Performance Requirements
- API response time < 500ms for reads, < 2000ms for writes
- Superset queries < 5s for standard dashboards
- Mobile app offline-first with sync < 30s on reconnect

---

## Constraints

| Constraint | Requirement |
|------------|-------------|
| Python version | 3.10+ |
| Odoo version | 18.0 CE |
| PostgreSQL | 15+ |
| Node.js | 18+ |
| Supabase | Latest stable |
| Superset | Latest stable |
| n8n | Latest stable |

---

## Prohibited Actions

1. Installing any module from `odoo/enterprise` repository
2. Using `odoo.com` OAuth or IAP services
3. Creating direct DB connections from Superset to Odoo (use analytics schema)
4. Storing credentials in code or version control
5. Bypassing approval workflows via direct SQL
6. Deploying without passing all CI gates
