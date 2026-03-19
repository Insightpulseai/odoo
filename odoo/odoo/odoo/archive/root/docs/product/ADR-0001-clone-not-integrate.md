# ADR-0001: Clone Not Integrate - Parity Module Philosophy

**Status:** Accepted
**Date:** 2024-12-19
**Deciders:** InsightPulse AI Engineering

## Context

When building enterprise-grade functionality on Odoo CE, there are two fundamentally different approaches:

1. **Integration Approach** - Build connectors to external SaaS platforms (Notion, Concur, SAP Ariba, Cheqroom)
2. **Clone Approach** - Build native Odoo modules that replicate the *workflows* of enterprise tools

The integration approach creates:
- External dependencies on third-party services
- Ongoing API maintenance burden
- Data residency concerns
- Licensing/subscription costs
- Network latency and reliability issues

## Decision

**We adopt the "Clone Not Integrate" philosophy.**

All `ipai_*` modules are **parity modules** - native Odoo implementations that replicate enterprise tool workflows without external SaaS dependencies.

### Naming Convention

| Enterprise Tool | Parity Module | Purpose |
|-----------------|---------------|---------|
| SAP Concur | `ipai_expense` | Expense reporting with receipt OCR |
| Cheqroom | `ipai_assets` | Equipment/asset checkout tracking |
| SAP SRM/Ariba | `ipai_srm` | Supplier relationship management |
| Clarity PPM | `ipai_ppm` | Portfolio/Program Management |
| Azure Advisor | `ipai_advisor` | Operational recommendations engine |
| Notion | *Not applicable* | Use `ipai_docs` + Odoo Knowledge |

### What This Means in Practice

1. **No SaaS connector scaffolds** - We do not create `ipai_notion_sync`, `ipai_concur_api`, etc.
2. **Feature cloning** - We study enterprise tool UX and replicate workflows natively
3. **Data stays in Odoo** - All data lives in PostgreSQL, not external services
4. **Optional export** - Supabase sync is for *external analytics/dashboards*, not primary storage

### Secret Management

Secrets follow a strict hierarchy:

| Secret Type | Storage | Access |
|-------------|---------|--------|
| Database passwords | `.env` file only | `${DB_PASSWORD}` via envsubst |
| API keys (internal) | `.env` file only | Loaded at runtime |
| Service URLs | `ir.config_parameter` | Safe to store in Odoo |
| Feature toggles | `ir.config_parameter` | Safe to store in Odoo |

**Critical**: Supabase service-role keys, JWT secrets, and database passwords are **NEVER** stored in `ir.config_parameter`. They exist only in environment variables.

### Configuration Loading Pattern

Since Odoo does not natively expand `${ENV_VAR}` in `odoo.conf`, we use:

```bash
# In docker-entrypoint.sh
envsubst < /etc/odoo/odoo.conf.template > /etc/odoo/odoo.conf
exec odoo "$@"
```

This allows config files to reference environment variables safely.

## Consequences

### Positive

- No external vendor lock-in
- Predictable costs (no per-seat SaaS fees)
- Full data sovereignty
- Simpler deployment (no API gateway needed)
- Faster development cycle (no API versioning concerns)

### Negative

- Must manually implement features that SaaS provides out-of-box
- No automatic updates from SaaS vendors
- Must study enterprise tools to understand workflow patterns

### Neutral

- CI/CD matrix builds remain unchanged
- Docker image structure unchanged (still multi-stage)
- OCA modules continue to provide base functionality

## Related ADRs

- ADR-0002: Docker Build Profiles (pending)
- ADR-0003: Supabase External Analytics Pattern (pending)

## References

- Odoo 18 Development Documentation
- OCA Contributing Guidelines
- Azure Advisor Feature Set (reference implementation for `ipai_advisor`)
- Clarity PPM Feature Set (reference implementation for `ipai_ppm`)
