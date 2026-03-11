# PRD: Odoo + Supabase Monorepo Production Deployment Research

> Product Requirements Document for deep research into deployment best practices.

---

## Problem Statement

The Odoo CE 19 + Supabase monorepo has a working deployment on DigitalOcean but lacks systematic application of proven OCA-style production practices. The current deployment was built incrementally and needs hardening, optimization, and alignment with what mature Odoo integrators (Camptocamp, Acsone, Tecnativa) actually do in production.

## Goals

1. **Document proven patterns** — what do real production Odoo deployments look like?
2. **Identify gaps** — where does the current deployment deviate from best practice?
3. **Produce actionable recommendations** — each finding maps to a config change, script, or workflow
4. **Quantify costs** — monthly cost model with optimization opportunities
5. **Harden security** — align with OWASP/CIS benchmarks for ERP systems

## Non-Goals

- Migrating away from DigitalOcean
- Adopting Kubernetes (unless cost-justified for this scale)
- Replacing Supabase with a self-hosted alternative
- Rewriting existing working code

## Success Metrics

| Metric | Target |
|--------|--------|
| Research questions answered with evidence | 100% |
| Architecture decisions documented | All major decisions |
| Production compose verified | Passes `docker compose config` |
| Security checklist coverage | OWASP Top 10 + CIS Docker |
| Cost model accuracy | Within 10% of actual billing |

## Stakeholders

- Infrastructure team (deployment, monitoring, security)
- Development team (OCA workflow, CI/CD, module management)
- Finance (cost optimization)

## Timeline

- Research phase: This spec bundle
- Implementation phase: Separate spec bundle after research approval
