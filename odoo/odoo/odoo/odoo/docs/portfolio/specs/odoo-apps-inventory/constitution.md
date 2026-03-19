# Odoo Apps Inventory — Constitution

## Purpose

This specification governs the 55-app parity strategy: ensuring all Odoo CE 18.0 functionality matches or exceeds Odoo Enterprise through OCA modules and Control Room custom builds.

## Non-Negotiables

### 1. Zero Enterprise Dependency
- **Rule**: No Odoo Enterprise license required for any functionality
- **Enforcement**: All 10 Enterprise-only apps replaced via OCA or Control Room
- **Verification**: `./scripts/odoo/verify-ce-parity.sh` must pass

### 2. OCA-First Replacement Strategy
- **Rule**: Prefer OCA modules over custom builds when available
- **Rationale**: Community-maintained, tested, upgrade-compatible
- **Exceptions**: Only when OCA lacks feature parity (documented in PRD)

### 3. Control Room Integration Standard
- **Rule**: All custom modules expose APIs via Control Room
- **Pattern**: Supabase schema + Node.js API + React UI
- **Enforcement**: Must pass OpenAPI spec validation

### 4. Audit Trail Requirement
- **Rule**: All data mutations logged to audit tables
- **Tables**: `*_audit` suffix (e.g., `kb_audit`, `sign_audit`)
- **Fields**: `id`, `entity_id`, `action`, `changed_by`, `timestamp`, `change_summary`

### 5. Persona-Aware Access
- **Rule**: All Control Room modules support persona-based filtering
- **Personas**: `admin`, `finance`, `operations`, `hr`, `sales`, `service`
- **Implementation**: Row-level security in Supabase + JWT claims

## Boundaries

### In Scope
- 38 CE-native apps (install only)
- 9 OCA replacement modules
- 7 Control Room custom modules
- Installation automation scripts
- Parity verification tooling

### Out of Scope
- Odoo Enterprise license acquisition
- Third-party SaaS integrations (except n8n connectors)
- Mobile native apps (React Native planned for Phase 4)

## Success Criteria

| Metric | Target | Measurement |
|--------|--------|-------------|
| App parity | 55/55 | Inventory checklist |
| CE-native installed | 38/38 | Odoo module list |
| OCA deployed | 9/9 | OCA manifest validation |
| Control Room modules | 7/7 | API health checks |
| Zero Enterprise deps | 0 | License audit |

## Governance

- **Owner**: Platform Engineering
- **Review Cadence**: Weekly during implementation, monthly after
- **Change Process**: PRD amendment → spec review → constitution update
