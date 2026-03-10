# Architecture Review Kit

A tailored architecture review framework for the InsightPulse AI platform, modeled after [Azure Architecture Review](https://learn.microsoft.com/en-us/assessments/azure-architecture-review/) but customized for our mixed-cloud ecosystem.

## Platform Profile

| Layer | Technology | Notes |
|-------|------------|-------|
| **Data** | PostgreSQL (Supabase primary) | RLS-first, multi-tenant |
| **ERP** | Odoo CE 18 + OCA | OCA-first module strategy |
| **Frontend** | Next.js/React + Vercel | Edge functions, SSR |
| **Automation** | n8n + MCP agents | Event-driven, thin orchestration |
| **Infra** | DigitalOcean + Docker | IaC preferred |
| **CI/CD** | GitHub Actions | Gate-enforced, evidence-required |
| **Observability** | Supabase (SSOT) | ops.* schema |

## Review Domains

| Domain | Focus | Weight |
|--------|-------|--------|
| A. Tenancy & Isolation | Multi-tenant boundaries, RLS | 15% |
| B. Identity & AuthZ | SSO, RBAC, service principals | 12% |
| C. Data Architecture | Postgres-first, CDC, retention | 12% |
| D. App Architecture | Modularity, API boundaries | 10% |
| E. Integration & Automation | n8n, idempotency, MCP safety | 10% |
| F. Reliability & DR | RPO/RTO, backups, multi-region | 10% |
| G. Observability & Audit | Logs, metrics, traces, audit | 8% |
| H. Security Engineering | Secrets, supply chain, runtime | 8% |
| I. Performance & Capacity | Load profiles, caching, backpressure | 5% |
| J. Cost & FinOps | Unit economics, budgets | 5% |
| K. Compliance & Governance | PII, retention, access reviews | 3% |
| L. SDLC & Change Control | CI gates, rollback, migrations | 2% |

## Directory Structure

```
architecture-review/
├── baseline/           # Azure Architecture Review extraction
├── framework/          # Scoring model, evidence requirements
├── templates/          # Report templates
├── examples/           # Sample completed reviews
└── reports/            # Actual review outputs
```

## Running a Review

1. **Prepare**: Gather evidence artifacts per `framework/evidence_index.yaml`
2. **Score**: Answer questionnaire per domain in `framework/domains/`
3. **Report**: Generate report from `templates/assessment_report.md`
4. **Remediate**: Address blockers first, then low-score items
5. **Track**: Update risk register and remediation plan

## Maturity Levels

| Level | Name | Description |
|-------|------|-------------|
| 0 | Initial | Ad-hoc, undocumented |
| 1 | Developing | Some practices defined |
| 2 | Defined | Documented, inconsistent execution |
| 3 | Managed | Consistent execution, metrics |
| 4 | Optimizing | Continuous improvement, automation |

## Blockers (Red Flags)

These items fail the review regardless of total score:

- [ ] Secrets in code or version control
- [ ] No RLS on tenant-scoped tables
- [ ] No backup/restore verification in 90 days
- [ ] Production access without audit logging
- [ ] Missing CI gates on main branch
- [ ] No rollback mechanism for deployments

## Quick Start

```bash
# Generate new review
cp templates/assessment_report.md reports/review-$(date +%Y%m%d).md

# Validate evidence
python scripts/validate_evidence.py reports/review-*.md

# Generate risk register
python scripts/generate_risk_register.py reports/review-*.md
```

## Version

- **v1.0** - Initial framework (2026-01-24)
