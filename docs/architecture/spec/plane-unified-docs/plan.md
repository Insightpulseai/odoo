# Implementation Plan: Plane Unified Docs

> Spec bundle: `spec/plane-unified-docs/`
> Constitution: `spec/plane-unified-docs/constitution.md`
> Status: Active
> Owner: Platform Architecture
> Created: 2026-03-13

---

## Overview

This plan migrates InsightPulseAI's documentation surface from a repo-only model to a three-layer architecture: **Repo SSOT** (machine-readable), **Plane Wiki** (human-readable ops docs), and **Plane Execution** (work items, cycles, boards). The repo remains the single source of truth for code, schemas, CI, and contracts. Plane becomes the human-operable surface for strategy docs, runbooks, architecture overviews, and execution tracking.

---

## Phase 1: Inventory Existing Docs, Plans, and Specs

### Objectives

- Produce a complete inventory of all documentation artifacts across the repo
- Classify each artifact by type (machine-readable, human-readable, execution state, stale/duplicate)
- Identify ownership gaps and duplicate content

### Key Actions

1. Enumerate all files in `docs/`, `spec/`, `ssot/`, `.claude/`, `odoo18/`, `apps/*/docs/`
2. Classify each file using the three-layer model from the constitution (L1/L2/L3)
3. Flag duplicates (same content in multiple locations)
4. Flag stale content (no update in 90+ days, references deprecated systems)
5. Produce `docs/migration/PLANE_DOCS_CONSOLIDATION_MAP.md` (File 4 of this spec bundle)
6. Produce `ssot/docs/plane-docs-canonical-map.yaml` (File 5 of this spec bundle)

### Dependencies

- None (first phase)

### Exit Criteria

- Consolidation map covers all `docs/`, `spec/`, `ssot/` paths
- Every entry has a classification (L1/L2/L3), target surface, and owner
- Duplicate clusters are identified with a designated canonical source
- Map reviewed and approved

### Estimated Scope

- 300+ documentation files to classify
- 76 spec bundles to evaluate
- 15+ SSOT subdirectories to map

---

## Phase 2: Define Taxonomy and Owners

### Objectives

- Establish the Plane wiki page hierarchy (categories, subcategories)
- Assign an owner to every category
- Define naming conventions and metadata requirements
- Create the template catalog for repeatable doc types

### Key Actions

1. Define top-level wiki categories: Architecture, Product, Delivery, Runbooks, Integrations, Data Platform, ERP/Odoo, Platform/Azure, AI/Agents, Finance/Compliance, Governance, Templates, Releases, Operations, Onboarding
2. For each category: assign owner, define page naming convention, set review cadence
3. Define page metadata requirements per constitution section 5.2 (Owner, Category, Last Reviewed, Status)
4. Create template catalog: Architecture Decision Record, PRD, Runbook, Incident Postmortem, Release Checklist, Onboarding Guide, Integration Spec
5. Document taxonomy in `docs/architecture/PLANE_UNIFIED_DOCS_TARGET_STATE.md` (File 3)

### Dependencies

- Phase 1 consolidation map (to know what content exists)

### Exit Criteria

- Wiki hierarchy documented with concrete page tree
- Every category has a named owner
- Template catalog has at least 7 templates defined
- Naming convention documented and consistent with constitution section 5.5

### Estimated Scope

- 15 top-level categories
- 7+ page templates
- 1 governance document

---

## Phase 3: Stand Up Self-Hosted Plane on Azure Container Apps

### Objectives

- Deploy Plane CE (self-hosted) as an Azure Container App
- Configure domain, TLS, SSO, SMTP, storage, and backup
- Verify production readiness

### Key Actions

1. Create container app `ipai-plane-dev` in `cae-ipai-dev` environment
2. Deploy Plane Docker images (web, api, worker, beat-worker, migrator, proxy)
3. Provision PostgreSQL database for Plane (separate from Odoo database)
4. Register `plane.insightpulseai.com` in `infra/dns/subdomain-registry.yaml`
5. Configure Azure Front Door origin group for Plane (port 3002)
6. Run `scripts/dns/generate-dns-artifacts.sh` and commit generated files
7. Configure Keycloak OIDC client for Plane (`auth.insightpulseai.com`)
8. Configure Zoho SMTP for Plane notifications
9. Configure Azure Blob Storage (S3-compatible) for file uploads
10. Store all secrets in Azure Key Vault (`kv-ipai-dev`): `PLANE_SECRET_KEY`, `PLANE_DB_*`, `PLANE_SMTP_*`, `PLANE_OIDC_*`
11. Set up daily `pg_dump` backup cron for Plane database
12. Verify: health endpoint responds, SSO login works, SMTP sends test email, file upload works

### Dependencies

- Keycloak instance running at `auth.insightpulseai.com`
- Azure Front Door `ipai-fd-dev` operational
- Azure Key Vault `kv-ipai-dev` accessible
- Zoho SMTP credentials provisioned

### Exit Criteria

- `https://plane.insightpulseai.com` returns 200
- Keycloak SSO login completes end-to-end
- Test notification email received via Zoho SMTP
- File upload to Azure Blob Storage succeeds
- Daily backup cron verified (at least one successful `pg_dump`)
- Container runs as non-root user
- All secrets resolved from Key Vault (no hardcoded values)

### Estimated Scope

- 6 container images to deploy
- 1 PostgreSQL database to provision
- 1 DNS record to register
- 1 Front Door origin to configure
- 1 Keycloak client to create
- 8+ secrets to store in Key Vault

---

## Phase 4: Create Workspace, Project, and Template Skeleton

### Objectives

- Create the Plane workspace and project structure
- Instantiate wiki categories from the taxonomy
- Deploy page templates
- Configure integrations (GitHub, Slack)

### Key Actions

1. Create workspace: `InsightPulseAI`
2. Create projects:
   - `ARCH` -- Architecture and Platform Design
   - `INFRA` -- Infrastructure and Deployment
   - `SPEC` -- Product Specifications and PRDs
   - `MIGRATE` -- Migration and Consolidation
   - `OPS` -- Operations and Runbooks
   - `ERP` -- Odoo ERP Development
   - `DATA` -- Data Platform and Analytics
   - `AI` -- AI/Agent Development
   - `COMPLY` -- Finance and Compliance
   - `GOV` -- Governance and Process
3. Create wiki root pages for each taxonomy category
4. Deploy page templates (ADR, PRD, Runbook, Incident Postmortem, Release Checklist, Onboarding Guide, Integration Spec)
5. Configure GitHub integration (bidirectional issue sync per project)
6. Configure Slack integration (notifications to designated channels)
7. Create SSOT integration config files:
   - `ssot/integrations/plane_github_sync.yaml`
   - `ssot/integrations/plane_slack_intake.yaml`
   - `ssot/integrations/plane_mcp.yaml`
8. Set up work item types: Initiative, Epic, Task, Bug, Validation
9. Configure default cycle length (2 weeks)

### Dependencies

- Phase 3 (Plane instance running)
- GitHub App `pulser-hub` operational
- Slack workspace configured

### Exit Criteria

- All 10 projects created with correct identifiers
- Wiki root pages exist for all 15 taxonomy categories
- All 7 templates deployed and usable
- GitHub sync verified (create issue in Plane, appears in GitHub)
- Slack notification verified (state change triggers Slack message)
- SSOT config files committed to repo

### Estimated Scope

- 1 workspace
- 10 projects
- 15 wiki root pages
- 7 page templates
- 3 integration configs

---

## Phase 5: Migrate Canonical Human Docs from Repo to Plane Wiki

### Objectives

- Move human-readable documentation from repo to Plane wiki pages
- Replace migrated repo files with redirect stubs linking to Plane
- Preserve git history (files are not deleted, they are replaced with stubs)

### Key Actions

1. For each entry in the consolidation map marked `migrate`:
   a. Create the Plane wiki page using the appropriate template
   b. Copy content, reformat for Plane rich text
   c. Replace inline code/YAML references with links to repo paths
   d. Set page metadata (Owner, Category, Last Reviewed, Status)
2. Replace the original repo file with a redirect stub:
   ```markdown
   # [Title] -- Migrated to Plane Wiki

   This document has been migrated to Plane Wiki.
   Canonical location: https://plane.insightpulseai.com/wiki/[path]

   Machine-readable SSOT artifacts remain in this repo.
   See: ssot/docs/plane-docs-canonical-map.yaml
   ```
3. Update `ssot/docs/plane-docs-canonical-map.yaml` status to `migrated` for each completed entry
4. Migration priority order:
   - P0: Architecture overviews, active PRDs, deployment runbooks
   - P1: Integration specs, data platform docs, ERP guides
   - P2: Onboarding guides, governance docs, decision records
   - P3: Historical specs, completed delivery plans

### Dependencies

- Phase 4 (workspace and templates ready)
- Phase 1 consolidation map complete

### Exit Criteria

- All P0 and P1 documents migrated
- Every migrated repo file replaced with a redirect stub
- No broken internal links (Plane pages link to repo for machine-readable refs)
- `plane-docs-canonical-map.yaml` updated with `migrated` status
- Spot-check: 5 randomly selected migrated pages render correctly in Plane

### Estimated Scope

- Estimated 40-60 documents to migrate (P0+P1)
- 40-60 redirect stubs to create in repo
- 40-60 YAML entries to update

---

## Phase 6: Link Execution Workflows to Specs and Plans

### Objectives

- Connect Plane work items to repo spec bundles
- Establish bidirectional traceability: Plane issue <-> GitHub PR <-> spec bundle
- Deploy MCP server for agent access to Plane

### Key Actions

1. For each active spec bundle (`spec/*/`):
   a. Create a Plane initiative or epic in the appropriate project
   b. Link to the spec bundle path in the work item description
   c. Set cycle assignment if actively in progress
2. Configure Plane MCP server (`mcp/servers/plane/`):
   a. Register tool allowlist in `ssot/integrations/plane_mcp.yaml`
   b. Deploy MCP server with Plane API credentials
   c. Verify Claude Code can read/create/update Plane work items
3. Set up n8n webhook workflows:
   a. Plane work item state change -> Slack notification
   b. GitHub PR merged -> update linked Plane work item
   c. Plane wiki page stale (90 days) -> flag for review
4. Document linking conventions in Plane wiki (Governance section)

### Dependencies

- Phase 4 (projects and work item types exist)
- Phase 5 (wiki pages exist to link to)
- MCP server code in `mcp/servers/plane/`

### Exit Criteria

- All active spec bundles have a corresponding Plane work item
- MCP server operational: Claude Code can query Plane via MCP tools
- n8n webhook workflows deployed and verified
- Linking convention documented

### Estimated Scope

- 10-15 active spec bundles to link
- 1 MCP server to deploy
- 3 n8n workflows to create

---

## Phase 7: Archive and Delete Duplicate Legacy Docs from Repo

### Objectives

- Remove stale and duplicate documentation from the repo
- Move archivable content to `archive/` directory
- Delete content that has been fully migrated with no residual value

### Key Actions

1. For each entry in the consolidation map marked `archive`:
   a. Move the file to `archive/docs-consolidation-<date>/`
   b. Add a note to the consolidation map with archive location
2. For each entry marked `delete`:
   a. Verify the content exists in Plane wiki (for migrated items) or is genuinely stale
   b. Wait 30 days after archival before deletion (per constitution section 5.3)
   c. Delete the archived file
   d. Update consolidation map status to `deleted`
3. Run `scripts/repo_health.sh` to verify no broken references
4. Update `.gitignore` if needed for new archive paths
5. Clean up empty directories left after migration

### Dependencies

- Phase 5 (migration complete for all items being archived)
- 30-day waiting period for archived items before deletion

### Exit Criteria

- All `archive` entries moved to `archive/` directory
- No broken internal links in remaining repo files
- `repo_health.sh` passes
- Consolidation map updated with final statuses
- Repo file count reduced by at least 20% in `docs/` directories

### Estimated Scope

- Estimated 50-100 files to archive
- Estimated 20-40 files to delete (after 30-day wait)
- 1 archive directory to create

---

## Phase 8: Operationalize Governance and Review Cadence

### Objectives

- Establish ongoing governance for the three-layer doc architecture
- Automate staleness detection and review reminders
- Define escalation paths for governance violations

### Key Actions

1. Deploy automated staleness detection:
   a. n8n workflow: query Plane API weekly for pages with `Last Reviewed` > 90 days
   b. Flag pages as `Needs Review` automatically
   c. After 30 additional days, move to `Archive` status
   d. Send Slack digest of flagged pages to `#docs-governance` channel
2. Define review cadence per category:
   - Architecture: quarterly review
   - Runbooks: monthly review
   - PRDs/Plans: per-cycle review (every 2 weeks)
   - Integrations: quarterly review
   - Compliance: monthly review
   - Onboarding: quarterly review
3. Create governance dashboard in Plane:
   - Page count by category and status
   - Overdue reviews
   - Orphan pages (no category)
   - Migration completion percentage
4. Document escalation path:
   - Page flagged -> owner notified via Slack
   - 14 days no action -> escalate to category lead
   - 30 days no action -> auto-archive
5. Run quarterly governance audit:
   - Validate all pages have required metadata
   - Check for layer violations (L2 content in repo, L1 content in wiki)
   - Report orphan pages
   - Update `ssot/docs/plane-docs-canonical-map.yaml`

### Dependencies

- Phase 6 (n8n workflows and integrations operational)
- Phase 7 (initial cleanup complete)

### Exit Criteria

- Staleness detection n8n workflow deployed and verified
- Review cadence documented per category
- Governance dashboard operational
- First quarterly audit completed
- Escalation path documented and communicated

### Estimated Scope

- 2 n8n workflows (staleness detection, Slack digest)
- 1 governance dashboard
- 1 audit checklist
- Ongoing: quarterly audits

---

## Risk Register

| Risk | Impact | Mitigation |
|------|--------|------------|
| Plane self-hosted stability | High | Daily backups, health monitoring via n8n, rollback procedure documented |
| Team adoption resistance | Medium | Start with P0 docs only, provide templates, demonstrate search improvement |
| Content drift between surfaces | High | Constitution rules enforced via CI, quarterly audits, automated staleness detection |
| Keycloak SSO misconfiguration | Medium | Test OIDC flow before go-live, document callback URLs, fallback local admin account |
| Migration data loss | High | Redirect stubs in repo preserve git history, Plane pages are not deleted without 30-day archive |

---

## Timeline Summary

| Phase | Estimated Duration | Parallel? |
|-------|-------------------|-----------|
| Phase 1: Inventory | 2-3 days | No (foundation) |
| Phase 2: Taxonomy | 1-2 days | After Phase 1 |
| Phase 3: Deploy Plane | 3-5 days | Parallel with Phase 2 |
| Phase 4: Skeleton | 2-3 days | After Phase 3 |
| Phase 5: Migrate | 5-10 days | After Phase 4 |
| Phase 6: Link Execution | 3-5 days | After Phase 5 |
| Phase 7: Archive/Delete | 2-3 days + 30-day wait | After Phase 5 |
| Phase 8: Governance | 3-5 days | After Phase 6+7 |

Total estimated: 4-6 weeks (phases 3+2 run in parallel; phase 7 has a 30-day deferred cleanup).
