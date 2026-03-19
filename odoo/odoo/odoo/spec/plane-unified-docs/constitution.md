# Constitution: Plane Unified Docs

> Spec bundle: `spec/plane-unified-docs/`
> Status: Active
> Owner: Platform Architecture
> Last reviewed: 2026-03-13

---

## 1. Purpose

This document defines the non-negotiable rules governing Plane as the unified documentation and execution surface for InsightPulseAI. These rules protect the separation of concerns between machine-readable SSOT (repo), human-readable operational docs (Plane wiki), and execution state (Plane work items/cycles).

---

## 2. Layer Separation (Non-Negotiable)

Three layers exist. They must remain separate. Violating layer separation creates drift, stale copies, and conflicting sources of truth.

| Layer | Surface | Examples | Owner |
|-------|---------|----------|-------|
| **L1: Machine-Readable SSOT** | Git repo (`Insightpulseai/odoo`) | YAML specs, JSON contracts, CI workflows, Terraform, migrations, `ssot/` tree | Repo (merge to `main`) |
| **L2: Human-Readable Ops Docs** | Plane wiki pages | Architecture overviews, runbooks, onboarding guides, decision records, delivery plans | Plane wiki (page owner) |
| **L3: Execution State** | Plane projects, work items, cycles | Initiatives, epics, tasks, bugs, sprints, OKR tracking | Plane projects (assignee) |

### 2.1 L1 to L2: Link, Never Copy

Plane wiki pages that reference machine-readable artifacts (YAML specs, JSON schemas, CI configs) MUST link to the canonical repo path. They MUST NOT paste the content inline.

Correct:
```
See: [Platform Auth Stack](https://github.com/Insightpulseai/odoo/blob/main/ssot/integrations/integration_auth_stack.yaml)
```

Incorrect:
```
# Pasted from integration_auth_stack.yaml (DO NOT DO THIS)
plane:
  url: https://plane.insightpulseai.com
  ...
```

### 2.2 L2 to L1: Never Back-Sync

Wiki prose, decision records, and operational guides written in Plane MUST NOT be duplicated back into repo `docs/` directories. If a wiki page captures a decision that affects a machine-readable contract, the contract file in the repo is updated directly -- the wiki page links to the updated contract.

### 2.3 L3 is Ephemeral State

Work items, cycle progress, and board states are execution artifacts. They are not documentation. Do not export Plane board state into repo files as "status reports." Use Plane's built-in reporting and cycle summaries.

---

## 3. Plane Role Definition

Plane is the **human-operable** documentation and execution surface:

- **Wiki**: Operational docs, architecture overviews, runbooks, decision records, delivery plans
- **Projects**: Scoped execution containers for work streams (Architecture, Infrastructure, Migration, etc.)
- **Work Items**: Trackable units of execution (initiatives, epics, tasks, bugs, validations)
- **Cycles**: Time-boxed delivery windows (sprints, monthly cycles)
- **Modules**: Thematic groupings across cycles (epics that span multiple sprints)
- **Pages**: Rich-text docs attached to projects for context

Plane is NOT the repo. Plane is NOT a CI system. Plane is NOT a secrets store.

---

## 4. Self-Hosted Deployment Rules

Plane runs as a self-hosted instance. No SaaS dependency.

| Component | Target | Notes |
|-----------|--------|-------|
| **Compute** | Azure Container Apps (`cae-ipai-dev`) | Container app: `ipai-plane-dev` |
| **Domain** | `plane.insightpulseai.com` | Registered in `infra/dns/subdomain-registry.yaml` |
| **Routing** | Azure Front Door (`ipai-fd-dev`) | Origin group: `plane`, port 3002 |
| **Auth** | Keycloak SSO (`auth.insightpulseai.com`) | Same IdP as all platform services |
| **SMTP** | Zoho (`smtp.zoho.com:587`) | Notifications, invite emails |
| **Database** | PostgreSQL (self-hosted) | Separate database from Odoo; same PostgreSQL instance pattern |
| **Object Storage** | Azure Blob Storage (S3-compatible) or MinIO | Upload attachments, images |
| **Backup** | Daily `pg_dump` | Same backup pattern as Odoo database |
| **Secrets** | Azure Key Vault (`kv-ipai-dev`) | `PLANE_SECRET_KEY`, `PLANE_DB_*`, `PLANE_SMTP_*` |

### 4.1 Auth: Keycloak SSO

- Plane MUST authenticate via Keycloak OpenID Connect
- No local Plane accounts for team members (service accounts excepted for API access)
- OAuth callback URL: `https://plane.insightpulseai.com/auth/callback`
- Keycloak client must be registered with correct redirect URIs before go-live

### 4.2 SMTP: Zoho

- Sender address must be an authorized Zoho mailbox on `insightpulseai.com`
- SMTP credentials resolved via Azure Key Vault at runtime
- Mailgun is deprecated -- never configure Plane to use Mailgun

---

## 5. Wiki Governance Rules

### 5.1 No Unstructured Wiki Dumps

Every wiki page MUST belong to a defined category in the taxonomy (see PRD section 3). Orphan pages are prohibited. If a page does not fit an existing category, a new category must be proposed and approved before the page is created.

### 5.2 Required Page Metadata

Every wiki page MUST have:

| Field | Description | Example |
|-------|-------------|---------|
| **Owner** | Person responsible for accuracy | `@jtolentino` |
| **Category** | Taxonomy category from the hierarchy | `Runbooks > Deployment` |
| **Last Reviewed** | Date of last review | `2026-03-13` |
| **Status** | `Draft`, `Active`, `Needs Review`, `Archived` | `Active` |

### 5.3 Archive Policy

- Pages not reviewed within 90 days are flagged as `Needs Review`
- Pages flagged for 30 additional days without action are moved to `Archive`
- Archive is not deletion -- archived pages remain searchable but are visually demoted
- Automated flagging via Plane webhook + n8n workflow

### 5.4 Templates Required

All repeatable document types MUST use a Plane page template. Ad hoc formatting is not permitted for standard doc types (architecture docs, PRDs, runbooks, incident postmortems, release checklists).

### 5.5 Naming Convention

- **Page slugs**: `kebab-case` (e.g., `platform-architecture-overview`, `monthly-close-runbook`)
- **Display names**: Title Case (e.g., "Platform Architecture Overview", "Monthly Close Runbook")
- **Project identifiers**: Short uppercase codes (e.g., `ARCH`, `INFRA`, `SPEC`, `MIGRATE`)

---

## 6. Work Item Governance

### 6.1 Single Source for Execution State

Plane work items are the authoritative record for "what is being worked on." Do not maintain parallel task lists in:
- GitHub Issues (use for external/community contributions only)
- Spreadsheets
- Slack threads
- Repo markdown checklists

### 6.2 Linking to Repo

Work items that implement spec bundles MUST include:
- Link to the spec bundle path (e.g., `spec/plane-unified-docs/prd.md`)
- Link to the implementation PR when code is shipped
- Link to the evidence bundle when verification is complete

### 6.3 Cycle Discipline

- Every active work item MUST be assigned to a cycle
- Unassigned items sit in the backlog -- they are not "in progress"
- Cycles are time-boxed (2-week default)
- Carry-over items must be explicitly re-assigned to the next cycle with a note

---

## 7. Integration Boundaries

### 7.1 Plane to GitHub

- Plane GitHub integration syncs issues bidirectionally (configured per-project)
- Plane is the primary surface for planning; GitHub Issues are the primary surface for code review
- Work items created in Plane that require code changes get a linked GitHub Issue or PR
- SSOT for integration config: `ssot/integrations/plane_github_sync.yaml`

### 7.2 Plane to Slack

- Plane Slack integration sends notifications to designated channels
- Work item state changes (created, assigned, completed) trigger Slack messages
- SSOT for integration config: `ssot/integrations/plane_slack_intake.yaml`

### 7.3 Plane MCP Server

- Claude Code and VS Code access Plane via the MCP server (`mcp/servers/plane/`)
- All MCP tool calls are audited via `ops.run_events`
- Tool allowlist is the governance boundary -- no freestyle API calls
- SSOT: `ssot/integrations/plane_mcp.yaml`

---

## 8. Security Rules

- Plane API keys are stored in Azure Key Vault, never in repo
- Plane webhook secrets are stored in Azure Key Vault
- No Plane admin actions performed via console without a corresponding repo commit (IaC or config YAML)
- Plane database credentials follow the same Key Vault pattern as Odoo database credentials
- Plane container runs as non-root user

---

## 9. What This Constitution Does NOT Cover

- Specific wiki page content (that is the PRD's domain)
- Implementation timeline (that is the plan's domain)
- Task breakdown (that is tasks.md)
- Business justification (that is the PRD's problem statement)

This document covers only the **invariant rules** that must hold regardless of implementation phase or feature scope.
