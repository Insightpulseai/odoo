# GitHub Organization Topology — InsightPulseAI

This document defines the authoritative taxonomy and operational boundaries for the `Insightpulseai` GitHub organization.

## 1. Authoritative Repository Taxonomy

### Active Repositories (Canonical Anchors)

| Repository | Role Boundary | Visibility |
|------------|---------------|------------|
| `.github` | Org governance, issue forms, reusable workflows, policies | PRIVATE |
| `odoo` | ERP System of Record (Odoo 19 CE + OCA + IPAI bridge) | PUBLIC |
| `ops-platform` | SSOT / Secrets / Control-Plane (Vault, Edge Functions) | PRIVATE |
| `lakehouse` | Intelligence / Analytics pipelines (Databricks, Medallion) | PRIVATE |
| `infra` | Infrastructure and Edge (IaC, Azure, DO, Cloudflare) | PRIVATE |
| `web` | Product surfaces, landing pages, and documentation sites | PRIVATE |
| `design-system` | Visual language, design tokens, and shared UI assets | INTERNAL |
| `agents` | Agent runtime metadata, skills, and orchestration | PUBLIC |
| `automations` | Workflow automation, scheduled jobs, and runbooks | PRIVATE |
| `templates` | Bootstrap-only scaffolds, starter templates | PRIVATE |

### Archive / Merge Candidates

| Repository | Action | Target Anchor |
|------------|--------|---------------|
| `template-factory` | ARCHIVE | N/A |
| `plugin-marketplace` | MERGE & ARCHIVE | `ops-platform` / `agents` |
| `plugin-agents` | MERGE & ARCHIVE | `agents` |
| `dev-environment` | ARCHIVE | `.github` / `templates` |
| `ops-console` | MERGE & ARCHIVE | `web` / `ops-platform` |
| `app-crm` | MERGE & ARCHIVE | `web` / `odoo` |
| `learn` | ARCHIVE | N/A |
| `fluent-owl` | ARCHIVE | N/A |
| `roadmap` | ARCHIVE | GitHub Projects |
| `mcp-core` | MERGE & ARCHIVE | `agents` / `automations` |
| `fin-ops` | ARCHIVE | `odoo/docs` |
| `app-landing` | MERGE & ARCHIVE | `web` |
| `demo-repository` | DELETE | N/A (if disposable) |

## 2. Canonical Team Model

| Team Name | Purpose |
|-----------|---------|
| `Admins` | Organization level access control |
| `odoo-core` | ERP development and maintenance |
| `platform-core` | SSOT and control-plane management |
| `infra-devops` | IaC and pipeline automation |
| `data-ai` | Lakehouse and AI agents |
| `design-system` | Visual language and UI components |
| `automation-ops` | n8n and workflow stability |

## 3. Canonical Project Model

| Project | Status | Purpose |
|---------|--------|---------|
| `Execution Board` | ACTIVE | Daily task tracking and sprint management |
| `InsightPulse Roadmap` | ACTIVE | High-level initiative tracking |
| `PROJECT TEMPLATE` | HIDE | Base template for new projects |

## 4. Responsibility Boundaries

- **odoo**: ERP SOR only.
- **ops-platform**: SSOT / secrets / control-plane.
- **lakehouse**: intelligence / analytics pipelines.
- **infra**: infrastructure and edge.
- **web**: product and docs surfaces.
- **agents**: agent runtime metadata / skills / orchestration.
- **automations**: workflow automation, schedulers, runbooks.
- **design-system**: visual language and shared UI assets.
- **templates**: bootstrap-only, not runtime code.

## 5. Governance Rules

1. **Deterministic Naming**: Repository names must match the anchor taxonomy where possible.
2. **Archive SSOT**: History is preserved via archive state; no outdated structural residue in active repos.
3. **Boundary Integrity**: Do not duplicate logic across repos; respect the role boundaries.
4. **Visibility Defaults**: ERP and Agents are PUBLIC; Infrastructure and Platforms are PRIVATE/INTERNAL.
