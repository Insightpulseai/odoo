# Tasks: Plane Unified Docs

> Spec bundle: `spec/plane-unified-docs/`
> Plan: `spec/plane-unified-docs/plan.md`
> Status: Active
> Created: 2026-03-13

---

## Phase 1: Inventory Existing Docs, Plans, and Specs

**Owner**: Agent | **Priority**: P0 | **Dependencies**: None

- [ ] P0 | Agent | Enumerate all files in `docs/` with type classification (L1/L2/L3)
- [ ] P0 | Agent | Enumerate all files in `spec/` with type classification
- [ ] P0 | Agent | Enumerate all files in `ssot/` with type classification
- [ ] P0 | Agent | Enumerate all files in `.claude/prompts/`, `.claude/rules/`, `.claude/commands/`
- [ ] P0 | Agent | Scan `apps/*/docs/`, `odoo19/`, `mcp/` for documentation files
- [ ] P1 | Agent | Identify duplicate content clusters (same content in multiple locations)
- [ ] P1 | Agent | Flag stale content (no git commit touching file in 90+ days)
- [ ] P1 | Agent | Flag content referencing deprecated systems (Mattermost, insightpulseai.net, Mailgun, DigitalOcean, Vercel)
- [ ] P0 | Agent | Produce `docs/migration/PLANE_DOCS_CONSOLIDATION_MAP.md`
- [ ] P0 | Agent | Produce `ssot/docs/plane-docs-canonical-map.yaml`
- [ ] P1 | Human | Review and approve consolidation map

---

## Phase 2: Define Taxonomy and Owners

**Owner**: Human (with Agent support) | **Priority**: P0 | **Dependencies**: Phase 1

- [ ] P0 | Human | Approve top-level wiki categories (15 proposed in plan)
- [ ] P0 | Human | Assign owner to each wiki category
- [ ] P1 | Agent | Draft page naming convention document
- [ ] P1 | Agent | Draft page metadata requirements (per constitution section 5.2)
- [ ] P0 | Agent | Define template catalog: ADR template
- [ ] P0 | Agent | Define template catalog: PRD template
- [ ] P0 | Agent | Define template catalog: Runbook template
- [ ] P1 | Agent | Define template catalog: Incident Postmortem template
- [ ] P1 | Agent | Define template catalog: Release Checklist template
- [ ] P2 | Agent | Define template catalog: Onboarding Guide template
- [ ] P2 | Agent | Define template catalog: Integration Spec template
- [ ] P0 | Agent | Document taxonomy in `docs/architecture/PLANE_UNIFIED_DOCS_TARGET_STATE.md`
- [ ] P1 | Human | Review and approve taxonomy and templates

---

## Phase 3: Stand Up Self-Hosted Plane on Azure Container Apps

**Owner**: Human (infrastructure) | **Priority**: P0 | **Dependencies**: Keycloak, Front Door, Key Vault

- [ ] P0 | Human | Provision PostgreSQL database for Plane (separate from Odoo)
- [ ] P0 | Human | Create container app `ipai-plane-dev` in `cae-ipai-dev`
- [ ] P0 | Agent | Deploy Plane Docker images (web, api, worker, beat-worker, migrator, proxy)
- [ ] P0 | Agent | Register `plane.insightpulseai.com` in `infra/dns/subdomain-registry.yaml`
- [ ] P0 | Agent | Run `scripts/dns/generate-dns-artifacts.sh` and commit generated files
- [ ] P0 | Human | Configure Azure Front Door origin group for Plane (port 3002)
- [ ] P0 | Human | Create Keycloak OIDC client for Plane
- [ ] P0 | Human | Store secrets in Azure Key Vault: `PLANE_SECRET_KEY`
- [ ] P0 | Human | Store secrets in Azure Key Vault: `PLANE_DB_URL`, `PLANE_DB_USER`, `PLANE_DB_PASSWORD`
- [ ] P1 | Human | Store secrets in Azure Key Vault: `PLANE_SMTP_USER`, `PLANE_SMTP_PASSWORD`
- [ ] P1 | Human | Configure Azure Blob Storage (S3-compatible) for Plane uploads
- [ ] P1 | Agent | Configure Zoho SMTP for Plane notifications
- [ ] P1 | Agent | Set up daily `pg_dump` backup cron for Plane database
- [ ] P0 | Agent | Verify: `https://plane.insightpulseai.com` returns 200
- [ ] P0 | Agent | Verify: Keycloak SSO login completes end-to-end
- [ ] P1 | Agent | Verify: test notification email received via Zoho SMTP
- [ ] P1 | Agent | Verify: file upload to Azure Blob Storage succeeds
- [ ] P1 | Agent | Verify: daily backup cron produces valid `pg_dump`
- [ ] P0 | Agent | Verify: container runs as non-root user

---

## Phase 4: Create Workspace, Project, and Template Skeleton

**Owner**: Agent | **Priority**: P0 | **Dependencies**: Phase 3

- [ ] P0 | Agent | Create workspace: `InsightPulseAI`
- [ ] P0 | Agent | Create project: `ARCH` (Architecture and Platform Design)
- [ ] P0 | Agent | Create project: `INFRA` (Infrastructure and Deployment)
- [ ] P0 | Agent | Create project: `SPEC` (Product Specifications and PRDs)
- [ ] P0 | Agent | Create project: `MIGRATE` (Migration and Consolidation)
- [ ] P1 | Agent | Create project: `OPS` (Operations and Runbooks)
- [ ] P1 | Agent | Create project: `ERP` (Odoo ERP Development)
- [ ] P1 | Agent | Create project: `DATA` (Data Platform and Analytics)
- [ ] P1 | Agent | Create project: `AI` (AI/Agent Development)
- [ ] P1 | Agent | Create project: `COMPLY` (Finance and Compliance)
- [ ] P2 | Agent | Create project: `GOV` (Governance and Process)
- [ ] P0 | Agent | Create wiki root pages for all 15 taxonomy categories
- [ ] P0 | Agent | Deploy ADR page template
- [ ] P0 | Agent | Deploy PRD page template
- [ ] P0 | Agent | Deploy Runbook page template
- [ ] P1 | Agent | Deploy Incident Postmortem page template
- [ ] P1 | Agent | Deploy Release Checklist page template
- [ ] P2 | Agent | Deploy Onboarding Guide page template
- [ ] P2 | Agent | Deploy Integration Spec page template
- [ ] P1 | Agent | Configure GitHub integration (bidirectional issue sync)
- [ ] P1 | Agent | Configure Slack integration (notifications)
- [ ] P1 | Agent | Create `ssot/integrations/plane_github_sync.yaml`
- [ ] P1 | Agent | Create `ssot/integrations/plane_slack_intake.yaml`
- [ ] P1 | Agent | Create `ssot/integrations/plane_mcp.yaml`
- [ ] P0 | Agent | Configure work item types: Initiative, Epic, Task, Bug, Validation
- [ ] P1 | Agent | Configure default cycle length (2 weeks)
- [ ] P0 | Agent | Verify: GitHub sync (Plane issue appears in GitHub)
- [ ] P1 | Agent | Verify: Slack notification (state change triggers message)

---

## Phase 5: Migrate Canonical Human Docs from Repo to Plane Wiki

**Owner**: Agent | **Priority**: P0 | **Dependencies**: Phase 4, Phase 1 consolidation map

### P0 Migrations (Architecture, Active PRDs, Deployment Runbooks)

- [ ] P0 | Agent | Migrate `docs/architecture/INSIGHTPULSEAI_TECHNICAL_ARCHITECTURE.md` -> Plane Wiki `Architecture > Platform Overview`
- [ ] P0 | Agent | Migrate `docs/architecture/IPAI_TARGET_ARCHITECTURE.md` -> Plane Wiki `Architecture > Target State`
- [ ] P0 | Agent | Migrate `docs/architecture/AUTH_ARCHITECTURE.md` -> Plane Wiki `Architecture > Authentication`
- [ ] P0 | Agent | Migrate `docs/architecture/DATABRICKS_ARCHITECTURE.md` -> Plane Wiki `Architecture > Data Platform`
- [ ] P0 | Agent | Migrate `docs/architecture/GOLDEN_PATH.md` -> Plane Wiki `Runbooks > Developer Golden Path`
- [ ] P0 | Agent | Migrate active PRDs from `spec/*/prd.md` -> Plane Wiki `Product > [Feature Name]`
- [ ] P0 | Agent | Migrate `docs/architecture/DEPLOY_TARGET_MATRIX.md` -> Plane Wiki `Runbooks > Deployment Targets`

### P1 Migrations (Integration Specs, Data Platform, ERP Guides)

- [ ] P1 | Agent | Migrate `docs/architecture/INTEGRATIONS_SURFACE.md` -> Plane Wiki `Integrations > Surface Map`
- [ ] P1 | Agent | Migrate `docs/architecture/N8N_AUTOMATION_CONTRACT.md` -> Plane Wiki `Integrations > n8n Contract`
- [ ] P1 | Agent | Migrate `docs/architecture/SLACK_AGENT_CONTRACT.md` -> Plane Wiki `Integrations > Slack Agent`
- [ ] P1 | Agent | Migrate `docs/architecture/SUPERSET.md` -> Plane Wiki `Data Platform > Superset`
- [ ] P1 | Agent | Migrate `docs/architecture/ODOO_EDITIONS_SSOT.md` -> Plane Wiki `ERP > Editions Policy`
- [ ] P1 | Agent | Migrate `docs/architecture/EE_PARITY_MATRIX.md` -> Plane Wiki `ERP > Enterprise Parity`
- [ ] P1 | Agent | Migrate `docs/architecture/MODULE_DECISION_RUBRIC.md` -> Plane Wiki `ERP > Module Decisions`

### P2 Migrations (Governance, Onboarding, Decision Records)

- [ ] P2 | Agent | Migrate `docs/architecture/GOVERNANCE_BRANCH_PROTECTION.md` -> Plane Wiki `Governance > Branch Protection`
- [ ] P2 | Agent | Migrate `docs/architecture/ECOSYSTEM_GUIDE.md` -> Plane Wiki `Onboarding > Ecosystem Guide`
- [ ] P2 | Agent | Migrate ADRs from `docs/architecture/adr/` -> Plane Wiki `Architecture > Decision Records`

### Cross-Cutting Migration Tasks

- [ ] P0 | Agent | Replace each migrated repo file with redirect stub
- [ ] P0 | Agent | Update `ssot/docs/plane-docs-canonical-map.yaml` status to `migrated` per entry
- [ ] P1 | Agent | Verify no broken internal links in remaining repo files
- [ ] P1 | Agent | Spot-check 5 randomly selected migrated pages in Plane

---

## Phase 6: Link Execution Workflows to Specs and Plans

**Owner**: Agent | **Priority**: P1 | **Dependencies**: Phase 5, MCP server

- [ ] P1 | Agent | Create Plane initiatives for each active spec bundle in `spec/`
- [ ] P1 | Agent | Link spec bundle paths in each initiative description
- [ ] P1 | Agent | Assign active initiatives to current cycle
- [ ] P1 | Agent | Deploy Plane MCP server (`mcp/servers/plane/`)
- [ ] P1 | Agent | Register MCP tool allowlist in `ssot/integrations/plane_mcp.yaml`
- [ ] P1 | Agent | Verify: Claude Code can query Plane work items via MCP
- [ ] P1 | Agent | Verify: Claude Code can create Plane work items via MCP
- [ ] P2 | Agent | Create n8n workflow: Plane state change -> Slack notification
- [ ] P2 | Agent | Create n8n workflow: GitHub PR merged -> update linked Plane item
- [ ] P2 | Agent | Create n8n workflow: Plane wiki page stale -> flag for review
- [ ] P1 | Agent | Document linking conventions in Plane Wiki `Governance > Linking Model`

---

## Phase 7: Archive and Delete Duplicate Legacy Docs

**Owner**: Agent | **Priority**: P2 | **Dependencies**: Phase 5 migration complete

- [ ] P2 | Agent | Create `archive/docs-consolidation-20260313/` directory
- [ ] P2 | Agent | Move all `archive`-classified files from consolidation map
- [ ] P2 | Agent | Update consolidation map with archive locations
- [ ] P2 | Agent | Run `scripts/repo_health.sh` -- verify no broken references
- [ ] P3 | Agent | After 30-day wait: delete archived files marked for deletion
- [ ] P3 | Agent | Update consolidation map status to `deleted`
- [ ] P2 | Agent | Clean up empty directories
- [ ] P2 | Agent | Verify repo file count reduction in `docs/` directories

---

## Phase 8: Operationalize Governance and Review Cadence

**Owner**: Human + Agent | **Priority**: P2 | **Dependencies**: Phase 6, Phase 7

- [ ] P2 | Agent | Deploy n8n workflow: weekly staleness detection (pages > 90 days without review)
- [ ] P2 | Agent | Deploy n8n workflow: Slack digest of flagged pages to `#docs-governance`
- [ ] P2 | Human | Define review cadence per category (Architecture=quarterly, Runbooks=monthly, PRDs=per-cycle)
- [ ] P2 | Agent | Create governance dashboard in Plane (page count, overdue reviews, orphan pages)
- [ ] P2 | Agent | Document escalation path in Plane Wiki `Governance > Doc Review Escalation`
- [ ] P3 | Agent | Run first quarterly governance audit
- [ ] P3 | Agent | Validate all pages have required metadata
- [ ] P3 | Agent | Check for layer violations (L2 in repo, L1 in wiki)
- [ ] P3 | Agent | Report orphan pages
- [ ] P3 | Agent | Update `ssot/docs/plane-docs-canonical-map.yaml` from audit results
- [ ] P2 | Human | Review and approve governance model

---

## Summary

| Phase | Total Tasks | P0 | P1 | P2 | P3 |
|-------|------------|----|----|----|----|
| Phase 1: Inventory | 11 | 5 | 5 | 0 | 0 |
| Phase 2: Taxonomy | 13 | 5 | 5 | 3 | 0 |
| Phase 3: Deploy Plane | 18 | 10 | 7 | 0 | 1 |
| Phase 4: Skeleton | 27 | 10 | 13 | 4 | 0 |
| Phase 5: Migrate | 21 | 10 | 7 | 4 | 0 |
| Phase 6: Link Execution | 11 | 0 | 7 | 4 | 0 |
| Phase 7: Archive | 8 | 0 | 0 | 6 | 2 |
| Phase 8: Governance | 11 | 0 | 0 | 7 | 4 |
| **Total** | **120** | **40** | **44** | **28** | **7** |
