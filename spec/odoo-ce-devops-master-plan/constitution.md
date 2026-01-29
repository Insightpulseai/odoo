# Constitution: Odoo CE DevOps Master Plan

## Non-Negotiable Rules

### 1. Phase Gate Enforcement
- **NO database operations until Phase 1 infrastructure is locked**
- **NO module installations until database snapshot exists**
- **NO parity claims without evidence packs**
- **NO phase advancement without GO status from gate check**

### 2. Evidence-Based Progress
- Every phase completion requires evidence in `docs/evidence/YYYYMMDD-HHMM/`
- Evidence includes: summary.json, artifacts list, verification results
- All claims must be verifiable through automated gate checks

### 3. Infrastructure Constraints
- **Cloud**: DigitalOcean App Platform only (no Azure/AWS/GCP)
- **Database**: PostgreSQL 16 (self-hosted, not managed)
- **Runtime**: Docker Compose for local, DO App Platform for production
- **Secrets**: Environment variables only, never in code

### 4. Odoo Standards
- **Version**: Odoo CE 19.0 (target), CE 18.0 (current stable)
- **Modules**: OCA-compliant only, AGPL-3 license
- **Naming**: `ipai_*` prefix for custom modules
- **Hierarchy**: Config → OCA → Delta (ipai_*)

### 5. Self-Hosted Philosophy
- Build everything ourselves to minimize costs
- No per-seat enterprise licensing
- No expensive SaaS subscriptions
- Target: ≥80% Odoo EE feature parity via CE+OCA+ipai_*

### 6. Documentation Requirements
- All significant changes reference a spec bundle
- DB schema changes require migration scripts
- Security changes require threat model updates
- Capability changes require docs updates (enforced by CI)

### 7. Backup & Recovery
- 3-datacenter backup strategy (SGP1, NYC3, AMS3)
- Daily backups with 30-day retention
- Monthly restore verification tests
- DR runbook must be tested quarterly

### 8. Quality Gates
- Parity score ≥95% for platform readiness
- All CI gates must pass before merge
- Visual parity SSIM ≥0.97 mobile, ≥0.98 desktop
- Test coverage ≥80% for ipai_* modules
