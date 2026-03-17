# PRD: Plane Unified Docs

> Spec bundle: `spec/plane-unified-docs/`
> Status: Active
> Owner: Platform Architecture
> Last reviewed: 2026-03-13

---

## 1. Problem

Documentation and execution tracking for InsightPulseAI is scattered across multiple surfaces with no unified search or linked execution state:

- **Repo markdown** (`docs/`, `docs/ai/`, `docs/architecture/`): 200+ markdown files with no discoverability beyond `grep`. No ownership metadata, no review dates, no staleness detection.
- **Ad hoc notes**: Decisions captured in Slack threads, PR comments, and commit messages that are never consolidated into searchable docs.
- **Scattered plans**: Delivery plans exist as spec bundles (`spec/*/plan.md`) but have no linked execution tracking. A plan exists in the repo; the work happens in... nowhere trackable.
- **No unified search**: Finding "how do we deploy Odoo" requires searching repo markdown, Slack history, and personal notes. There is no single search surface.
- **No execution-to-doc linkage**: When a spec bundle is implemented, there is no traceable path from the spec to the work items to the PRs to the evidence. The chain is reconstructed manually every time.
- **No staleness detection**: Docs written 6 months ago look identical to docs written yesterday. No review dates, no owners, no archive policy.

The repo is the correct home for machine-readable SSOT (YAML, JSON, contracts, CI). It is the wrong home for human-readable operational docs, runbooks, and delivery tracking.

---

## 2. Solution

Deploy self-hosted Plane CE as the unified documentation and execution surface. Plane provides:

- **Wiki**: Structured, searchable, categorized operational docs with ownership and review metadata
- **Projects + Work Items**: Execution tracking linked to specs, PRs, and deployments
- **Cycles**: Time-boxed delivery windows with carry-over tracking
- **Modules**: Epic-level groupings that span cycles
- **Pages**: Project-scoped rich docs for context and decisions
- **Search**: Full-text search across all wiki pages, work items, and comments

Plane does NOT replace the repo. The repo remains SSOT for machine-readable artifacts. Plane is the human-operable layer on top.

---

## 3. Wiki Hierarchy

The following page tree defines the taxonomy for the Plane wiki. Every page must belong to one of these categories. New categories require explicit approval.

```
Wiki Root
|
+-- Architecture
|   +-- Platform Architecture Overview
|   +-- Data Architecture
|   +-- Integration Architecture
|   +-- Infrastructure Architecture
|   +-- Security Architecture
|   +-- Decision Records (ADRs)
|
+-- Product Specs
|   +-- Active PRDs
|   +-- Completed Specs
|   +-- Archived Specs
|
+-- Delivery Plans
|   +-- Active Programs
|   +-- Milestones & Timelines
|   +-- Deferred / On Hold
|
+-- Runbooks
|   +-- Operations
|   |   +-- Daily Operations Checklist
|   |   +-- Monitoring & Alerting
|   +-- Deployment
|   |   +-- Odoo Deployment Runbook
|   |   +-- Azure Container Apps Deployment
|   |   +-- Database Migration Runbook
|   +-- Incident Response
|   |   +-- Incident Playbook
|   |   +-- Escalation Matrix
|   |   +-- Postmortem Template
|   +-- Maintenance
|       +-- Database Maintenance
|       +-- Certificate Rotation
|       +-- Backup Verification
|
+-- Integrations
|   +-- Odoo <> Supabase
|   +-- Odoo <> n8n
|   +-- Odoo <> Slack
|   +-- Azure Services
|   +-- Databricks / Lakehouse
|   +-- External APIs
|
+-- Data Platform
|   +-- Lakehouse Architecture (Bronze/Silver/Gold/Platinum)
|   +-- ETL Pipelines
|   +-- Data Serving Layer
|   +-- BI / Superset Dashboards
|
+-- ERP / Odoo
|   +-- Module Inventory & Parity Matrix
|   +-- Customization Guidelines
|   +-- Upgrade Plans (18 > 19)
|   +-- OCA Module Governance
|   +-- BIR Compliance Modules
|
+-- Platform / Azure
|   +-- Container Apps Configuration
|   +-- Front Door & Routing
|   +-- Key Vault Secret Inventory
|   +-- Monitoring & Log Analytics
|   +-- Cost Management
|
+-- AI / Agents
|   +-- MCP Server Architecture
|   +-- Copilot Integration
|   +-- Agent Framework
|   +-- Prompt Library
|   +-- Model Selection & Gateway
|
+-- Finance / Compliance
|   +-- BIR Tax Forms
|   +-- Payroll (SSS, PhilHealth, Pag-IBIG)
|   +-- Audit Trail
|   +-- Month-End Close Process
|
+-- Governance / Policies
|   +-- Security Policy
|   +-- Access Control Matrix
|   +-- Data Retention Policy
|   +-- Change Management Process
|   +-- Secrets Management Policy
|
+-- Templates
|   +-- (All reusable templates listed in section 5)
|
+-- Release / Change Logs
|   +-- Odoo Release Notes
|   +-- Platform Release Notes
|   +-- Infrastructure Change Log
|   +-- Integration Change Log
|
+-- Archive
    +-- Retired Docs
    +-- Deprecated Systems
    +-- Historical Decisions
```

---

## 4. Project / Work-Item Model

### 4.1 Projects

Each project is a scoped execution container. Projects map to organizational concerns, not individual features.

| Project Code | Project Name | Scope |
|--------------|-------------|-------|
| `ARCH` | Architecture | System design, ADRs, platform architecture changes |
| `SPEC` | Spec Implementation | Executing PRDs from `spec/` bundles into shipped features |
| `MIGRATE` | Migration | Odoo 18-to-19 migration, Azure migration, data migrations |
| `INFRA` | Infrastructure | Azure Container Apps, Front Door, Key Vault, networking, DNS |
| `INTEG` | Integration | Odoo-Supabase, Odoo-n8n, Odoo-Slack, GitHub sync, MCP |
| `DOCS` | Documentation | Wiki pages, runbooks, templates, doc debt cleanup |
| `QA` | Validation / QA | Test plans, parity validation, smoke tests, regression |
| `RELEASE` | Release Management | Release coordination, change logs, go-live checklists |

### 4.2 Work Item Types

| Type | Description | Example |
|------|-------------|---------|
| **Initiative** | Strategic objective spanning multiple epics | "Achieve 80% EE parity" |
| **Epic** | Large deliverable spanning multiple tasks, tracked as a Plane module | "Implement ipai_helpdesk to replace EE helpdesk" |
| **Deliverable** | Shippable unit of work with acceptance criteria | "Helpdesk ticket creation via portal" |
| **Task** | Atomic unit of work assignable to one person | "Add `helpdesk.ticket` model with required fields" |
| **Validation** | Verification/testing work item | "Run parity test for ipai_helpdesk, capture evidence" |
| **Bug** | Defect in existing functionality | "Month-end close wizard fails on empty journal" |
| **Doc Debt** | Missing or stale documentation | "Runbook missing for Azure Container Apps deployment" |
| **Decision** | Architectural or product decision requiring record | "Choose between MinIO and Azure Blob for Plane uploads" |
| **Risk** | Identified risk requiring mitigation plan | "OCA ai module not stable on 19.0" |
| **Deferred** | Explicitly deprioritized item with rationale | "VoIP integration deferred to Q3 -- no business need yet" |

### 4.3 Work Item States

```
Backlog --> Todo --> In Progress --> In Review --> Done
                                 \-> Blocked
                  \-> Cancelled
```

---

## 5. Templates

The following templates MUST be created in Plane and used for all instances of each document type.

| Template | Purpose | Key Sections |
|----------|---------|-------------|
| **Architecture Doc** | System or component architecture description | Context, Components, Interactions, Data Flow, Constraints, Decisions, Diagram Links |
| **PRD** | Product requirements for a feature or system | Problem, Solution, Requirements, Success Criteria, Out of Scope, Dependencies |
| **Implementation Plan** | Step-by-step execution plan for a PRD | Phases, Tasks per Phase, Dependencies, Risk Mitigations, Rollback Plan |
| **Runbook** | Operational procedure for a repeatable task | Prerequisites, Steps (numbered), Verification, Rollback, Escalation |
| **Migration Checklist** | Pre/during/post migration verification | Pre-flight Checks, Migration Steps, Post-migration Validation, Rollback Triggers |
| **Release Checklist** | Go-live gate checklist | Build Verification, Smoke Tests, DNS/Routing, Monitoring, Rollback Plan |
| **Incident Postmortem** | Post-incident analysis | Timeline, Impact, Root Cause, Contributing Factors, Action Items, Prevention |
| **Integration Contract Summary** | Human-readable summary of a repo integration contract | Systems, Direction, Auth, Data Flow, SSOT File Link, Failure Modes |
| **System Overview** | High-level system description for onboarding | Purpose, Stack, Key URLs, Architecture Diagram, Team Contacts |
| **Environment Handoff** | Environment access and config for new team members | URLs, Credentials (Key Vault refs only), Access Requests, First-Day Checklist |

---

## 6. Linking Model

The linking model connects Plane pages and work items to repo artifacts, PRs, and deployments. Links are the bridge between L2 (Plane wiki) and L1 (repo SSOT).

### 6.1 Wiki Page to Repo SSOT

Wiki pages that describe systems documented in repo SSOT files MUST include a "Source of Truth" section:

```markdown
## Source of Truth
- Spec bundle: [spec/plane-unified-docs/](https://github.com/Insightpulseai/odoo/tree/main/spec/plane-unified-docs/)
- Integration config: [ssot/integrations/plane_mcp.yaml](https://github.com/Insightpulseai/odoo/blob/main/ssot/integrations/plane_mcp.yaml)
- DNS entry: [infra/dns/subdomain-registry.yaml#L149](https://github.com/Insightpulseai/odoo/blob/main/infra/dns/subdomain-registry.yaml#L149)
```

### 6.2 Work Item to Spec Bundle

Work items implementing a spec bundle MUST include in the description:

```markdown
**Spec**: `spec/<feature-slug>/prd.md`
**Constitution**: `spec/<feature-slug>/constitution.md`
**Plan**: `spec/<feature-slug>/plan.md`
```

### 6.3 Work Item to PR

When a work item results in code changes:
- The Plane-GitHub integration creates a bidirectional link
- PR description includes the Plane work item identifier
- Work item is updated to `In Review` when PR is opened
- Work item is updated to `Done` when PR is merged (via webhook)

### 6.4 Work Item to Deployment Evidence

When a work item results in a deployment:
- Link to the evidence bundle: `docs/evidence/<YYYYMMDD-HHMM>/<scope>/`
- Link to the CI workflow run URL
- Validation work item references the evidence as acceptance proof

### 6.5 Cross-References Between Plane Entities

- Initiatives link to their child Epics (via Plane modules)
- Epics link to their child Deliverables/Tasks
- Decision records link to the work items they unblocked
- Risk items link to the mitigation tasks

---

## 7. Self-Hosted Deployment Target

### 7.1 Compute

| Component | Target |
|-----------|--------|
| **Platform** | Azure Container Apps |
| **Environment** | `cae-ipai-dev` (Southeast Asia) |
| **Container App** | `ipai-plane-dev` |
| **Image** | `makeplane/plane-ce:latest` (or pinned version) |
| **Port** | 3002 (internal) |
| **Replicas** | 1 (dev), 2+ (prod) |
| **Resources** | 1 vCPU, 2Gi memory (dev); scale as needed |

### 7.2 Database

| Item | Value |
|------|-------|
| **Engine** | PostgreSQL 16 |
| **Hosting** | Self-hosted (Azure Container Apps or dedicated VM) |
| **Database name** | `plane` |
| **Pattern** | Same as Odoo database -- separate database, same PostgreSQL instance or cluster |
| **Credentials** | Azure Key Vault (`kv-ipai-dev`): `plane-db-user`, `plane-db-password` |
| **Backup** | Daily `pg_dump` to Azure Blob Storage, 30-day retention |
| **Backup script** | `scripts/docker/backup-plane.sh` (already referenced in traceability index) |

### 7.3 Authentication

| Item | Value |
|------|-------|
| **Provider** | Keycloak (`auth.insightpulseai.com`) |
| **Protocol** | OpenID Connect |
| **Client ID** | Stored in Key Vault: `plane-oauth-client-id` |
| **Client Secret** | Stored in Key Vault: `plane-oauth-client-secret` |
| **Callback URL** | `https://plane.insightpulseai.com/auth/callback` |
| **Scopes** | `openid`, `profile`, `email` |

### 7.4 Email (SMTP)

| Item | Value |
|------|-------|
| **Provider** | Zoho |
| **Host** | `smtp.zoho.com` |
| **Port** | 587 (STARTTLS) |
| **Sender** | Authorized Zoho mailbox on `insightpulseai.com` |
| **Credentials** | Azure Key Vault: `zoho-smtp-user`, `zoho-smtp-password` |
| **Purpose** | Invite emails, notification digests, password resets |

### 7.5 Object Storage

| Item | Value |
|------|-------|
| **Provider** | Azure Blob Storage (S3-compatible API via Azurite for dev, Azure for prod) or MinIO |
| **Bucket** | `plane-uploads` |
| **Purpose** | File attachments, images, avatar uploads |
| **Credentials** | Azure Key Vault: `plane-storage-access-key`, `plane-storage-secret-key` |
| **Retention** | No auto-delete; managed via Plane admin |

### 7.6 Domain & Routing

| Item | Value |
|------|-------|
| **Domain** | `plane.insightpulseai.com` |
| **DNS** | CNAME to Azure Front Door (already in `infra/dns/subdomain-registry.yaml`) |
| **Front Door** | Origin group `plane`, routes `plane-static` (cached) and `plane-default` (no cache) |
| **TLS** | Managed by Azure Front Door |
| **Static assets** | `/_next/static/*` and `/static/*` cached for 7 days |

### 7.7 Backup

| Item | Value |
|------|-------|
| **Database** | Daily `pg_dump --format=custom` of `plane` database |
| **Storage** | Azure Blob Storage, `backups/plane/` container |
| **Retention** | 30 days rolling |
| **Script** | `scripts/docker/backup-plane.sh` |
| **Verification** | Weekly restore test to ephemeral database |
| **Monitoring** | Backup job status reported to `ops.platform_events` via n8n |

---

## 8. Migration Phases

### Phase 1: Infrastructure Provisioning

- Deploy Plane CE container to Azure Container Apps (`ipai-plane-dev`)
- Provision PostgreSQL database (`plane`)
- Configure Azure Front Door origin group and routes (already defined in `infra/azure/front-door-routes.yaml`)
- Configure Azure Blob Storage bucket for uploads
- Store all secrets in Azure Key Vault
- Verify: `curl -s https://plane.insightpulseai.com/ | grep -q "Plane"` returns 200

### Phase 2: Authentication & Access

- Register Plane as OIDC client in Keycloak
- Configure Plane to use Keycloak as sole auth provider
- Disable local authentication for team members
- Create service account for API access (MCP server, n8n webhooks)
- Configure Zoho SMTP for notification emails
- Verify: SSO login succeeds, invite email arrives via Zoho

### Phase 3: Workspace & Project Setup

- Create workspace: `insightpulseai` (slug: `insightpulseai`)
- Create all 8 projects from section 4.1 (`ARCH`, `SPEC`, `MIGRATE`, `INFRA`, `INTEG`, `DOCS`, `QA`, `RELEASE`)
- Configure work item types, states, and labels per section 4.2
- Set up cycle cadence (2-week default)
- Configure priority levels: Urgent, High, Medium, Low, None

### Phase 4: Wiki Taxonomy Bootstrap

- Create the full wiki page tree from section 3
- Seed each category with a placeholder page explaining its purpose
- Create all 10 templates from section 5
- Populate "Architecture > Platform Architecture Overview" as the first real page
- Populate "Runbooks > Deployment > Odoo Deployment Runbook" as the second real page
- Apply metadata (owner, category, last-reviewed, status) to all pages

### Phase 5: Integration Wiring

- Enable Plane-GitHub bidirectional sync for the `Insightpulseai/odoo` repo
- Configure Plane-Slack notifications to designated channels
- Deploy Plane MCP server (`mcp/servers/plane/`) with updated workspace config
- Configure n8n webhook for Plane events (work item state changes, page updates)
- Verify: Create a work item in Plane, confirm GitHub issue appears; merge PR, confirm Plane item updates

### Phase 6: Content Migration

- Identify repo `docs/` files that are operational docs (not machine-readable SSOT)
- For each identified file:
  - Create corresponding Plane wiki page in the correct taxonomy category
  - Add "Source of Truth" links back to any repo SSOT files referenced
  - Add page metadata (owner, category, last-reviewed, status)
  - Do NOT delete the repo file yet (Phase 7)
- Priority migration targets:
  - `docs/ai/ARCHITECTURE.md` --> Architecture > Platform Architecture Overview
  - `docs/ai/DOCKER.md` --> Runbooks > Deployment
  - `docs/ai/TROUBLESHOOTING.md` --> Runbooks > Operations
  - `docs/ai/TESTING.md` --> Governance > QA Process

### Phase 7: Repo Doc Cleanup

- For each repo doc migrated to Plane wiki:
  - Replace file content with a redirect notice: "This document has moved to Plane wiki. See: [link]"
  - Keep the file in the repo (do not delete) to avoid broken links
  - Add `status: redirected-to-plane` metadata
- Update `docs/architecture/PLATFORM_REPO_TREE.md` to reflect the new ownership
- Update `CLAUDE.md` references to point to Plane wiki where applicable
- Do NOT move machine-readable SSOT files (`ssot/`, `infra/`, `spec/`) -- they stay in repo

### Phase 8: Governance Activation

- Enable 90-day staleness detection via n8n scheduled workflow
- Configure automated Slack notifications for pages needing review
- Set up weekly wiki health report (pages by status, staleness count, orphan detection)
- Configure backup verification (weekly restore test)
- Document the Plane admin runbook in Plane wiki (Runbooks > Maintenance)
- Run first governance cycle: review all pages, confirm metadata, archive stale content

---

## 9. Governance Model

### 9.1 Page Ownership

Every wiki page has exactly one owner. The owner is responsible for:
- Keeping the page accurate and current
- Reviewing the page at least every 90 days
- Responding to staleness flags within 30 days
- Archiving the page when it is no longer relevant

### 9.2 Review Cadence

| Category | Review Frequency | Rationale |
|----------|-----------------|-----------|
| Runbooks | Monthly | Operational procedures change with deployments |
| Architecture | Quarterly | Architecture evolves slowly |
| Product Specs | On completion | Specs are reviewed when the work ships |
| Delivery Plans | Per cycle (bi-weekly) | Plans update every sprint |
| Governance / Policies | Quarterly | Policies are stable |
| Templates | Quarterly | Templates evolve with process |
| Release Logs | Never (append-only) | Historical record |

### 9.3 Change Control

- Any team member can propose a wiki page edit
- Architecture docs and Governance/Policy pages require review by the page owner before publish
- Runbooks and operational docs can be updated directly (reviewed post-hoc)
- Template changes require review by the Documentation project lead

### 9.4 Metrics

Track and report monthly:

| Metric | Target | Source |
|--------|--------|--------|
| Pages with active owner | 100% | Plane page metadata |
| Pages reviewed within 90 days | > 90% | Plane page metadata |
| Orphan pages (no category) | 0 | Automated check |
| Work items with spec link | > 80% | Plane work item fields |
| Work items with PR link (when code shipped) | > 90% | Plane-GitHub integration |
| Average cycle velocity | Trending up | Plane cycle reports |

### 9.5 Escalation

- Staleness flags unresolved for 30 days: escalate to project lead
- Orphan pages: block until categorized (no orphan pages allowed)
- Missing templates: block work item creation for that doc type until template exists
- Backup failures: immediate Slack alert to `#ops-alerts`, escalate if unresolved in 4 hours

---

## 10. Success Criteria

### 10.1 Launch (Phase 1-3 Complete)

- [ ] Plane accessible at `https://plane.insightpulseai.com` with Keycloak SSO
- [ ] All 8 projects created with correct configuration
- [ ] Zoho email notifications working
- [ ] Daily database backup running and verified

### 10.2 Operational (Phase 4-5 Complete)

- [ ] Full wiki taxonomy created with placeholder pages
- [ ] All 10 templates created and usable
- [ ] GitHub bidirectional sync active for `Insightpulseai/odoo`
- [ ] Slack notifications active for work item state changes
- [ ] MCP server connected and auditing tool calls

### 10.3 Migration (Phase 6-7 Complete)

- [ ] Priority operational docs migrated from repo to Plane wiki
- [ ] All migrated pages have correct metadata (owner, category, last-reviewed)
- [ ] Repo docs replaced with redirect notices
- [ ] `PLATFORM_REPO_TREE.md` updated to reflect Plane ownership

### 10.4 Steady State (Phase 8 Complete)

- [ ] 90-day staleness detection running
- [ ] Weekly wiki health report delivered to Slack
- [ ] First governance cycle completed (all pages reviewed)
- [ ] Backup restore test passed
- [ ] Zero orphan pages
- [ ] > 80% of work items linked to spec bundles

### 10.5 Anti-Success (Failure Indicators)

- Wiki pages with pasted YAML/JSON from repo (layer violation)
- Repo markdown files duplicating Plane wiki content (layer violation)
- Work items with no cycle assignment for > 2 weeks
- Pages with no owner
- Backup not tested for > 30 days
- MCP audit gaps (tool calls without `ops.run_events` rows)
