# Odoo.sh-Equivalent Platform — Implementation Plan

**Version**: 1.0.0
**Status**: Draft
**Last Updated**: 2026-03-11

---

## Phased Implementation

### Phase 1: Doctrine & SSOT Artifacts (Week 1-2)

**Objective**: Establish machine-readable persona definitions, capability matrix, and Odoo.sh equivalence mapping.

**Deliverables**:
1. `infra/ssot/platform/personas.yaml` — Canonical persona definitions with access scopes
2. `infra/ssot/platform/capability_matrix.yaml` — Full capability taxonomy with persona permissions
3. `infra/ssot/platform/odoosh_equivalent_capabilities.yaml` — Feature-by-feature Odoo.sh mapping

**Technical Approach**:
- YAML files are the SSOT; all other representations (docs, dashboards) are derived
- CI validation ensures YAML schema compliance
- Persona permission model is additive-only per constitution

### Phase 2: Environment Lifecycle (Week 3-5)

**Objective**: Implement branch-based environment creation and teardown on ACA.

**Deliverables**:
1. GitHub Actions workflow for environment provisioning on branch push
2. ACA revision management scripts (`scripts/infra/aca_env_create.sh`, `aca_env_destroy.sh`)
3. Ephemeral environment auto-cleanup (7-day idle TTL)
4. PR-linked staging environment with database clone

**Technical Approach**:
- Each branch maps to an ACA revision with unique ingress
- Database clone uses `pg_dump` from production snapshot (sanitized)
- Cleanup cron via GitHub Actions scheduled workflow
- Environment metadata tracked in `ops.platform_environments` table

### Phase 3: Logs, Shell & Monitoring (Week 6-8)

**Objective**: Implement runtime visibility capabilities for all personas.

**Deliverables**:
1. Log aggregation pipeline: ACA → Log Analytics → query API
2. Shell/exec access via `az containerapp exec` wrapper scripts
3. Health dashboard: port visibility, probe status, environment status
4. Mail catcher (Mailpit) for dev/staging environments

**Technical Approach**:
- Log Analytics workspace per environment tier (shared for dev, dedicated for staging/prod)
- Shell access gated by persona role (constitution rules)
- Mailpit deployed as sidecar container in non-production environments
- Health probes exposed via platform API endpoint

### Phase 4: Promotion & Gates (Week 9-11)

**Objective**: Implement the promotion pipeline with automated and manual gates.

**Deliverables**:
1. Promotion workflow: staging → production with configurable gates
2. Gate integrations: CI tests, Azure maturity score, Odoo smoke test
3. Manual approval steps for QA and PM personas
4. Rollback mechanism with verification

**Technical Approach**:
- Promotion is a GitHub Actions workflow triggered by approval event
- Gates are modular: each gate is a separate job in the workflow
- Azure maturity score gate reads from `infra/ssot/azure/platform_maturity_benchmark.yaml`
- Rollback triggers ACA revision swap (zero-downtime)

### Phase 5: Backup, DNS & Hardening (Week 12-14)

**Objective**: Complete the remaining capability packs (C5-C8).

**Deliverables**:
1. Automated backup pipeline with tested restore
2. DNS/domain routing for branch environments (wildcard subdomain)
3. Deployment history tracking and audit trail
4. Developer UX tooling integration (Codespaces config, Claude Code hooks)

**Technical Approach**:
- Backup: Azure Backup for PostgreSQL + blob storage for filestore
- DNS: Cloudflare wildcard `*.dev.insightpulseai.com` → ACA ingress
- History: GitHub Actions run metadata + `ops.deployment_history` table
- UX: `.devcontainer/` config + Claude Code SessionStart hooks

---

## Risk Mitigations

| Risk | Mitigation |
|------|------------|
| ACA cold start latency > 5min target | Pre-warm revisions; use minimum replica count of 1 for staging |
| Database clone size for staging | Sanitize + compress; use pg_dump custom format with parallel jobs |
| Mailpit security in shared infra | Network-isolated per environment; no external ingress |
| Persona role enforcement gaps | CI gate validates capability_matrix.yaml against actual IAM bindings |

---

## Integration Points

| Consumer | What It Reads | Purpose |
|----------|---------------|---------|
| `odoo/` spec bundles | Capability matrix + promotion gates | Runtime implementation |
| Azure maturity benchmark | Compute + Deployment domain evidence | Platform scoring |
| OdooOps Platform (existing) | Environment lifecycle APIs | Migration from DO to Azure |
| CI pipelines | Gate definitions + persona permissions | Access control enforcement |
