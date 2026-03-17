# Docs platform PRD

## Problem

The InsightPulse AI platform has 167 architecture docs, 27 contracts, and 76 specs scattered across `docs/` with no publishing pipeline, no app shell, no search, and no versioning. Engineers waste time locating authoritative content. Duplicates drift. Compliance reviewers cannot verify which version is current. There is no single entry point for platform documentation.

## Solution

A four-plane docs platform:

1. **Repo SSOT plane** — spec bundles, YAML manifests, contracts, schemas. Machine-readable. Lives in git.
2. **Docs content/build plane** — authored docs, static assets, extensions, tests. Deterministic builds. Modeled after `odoo/documentation`.
3. **Docs product UI plane** — Fluent 2 React v9 app shell with navigation, search, metadata, dark mode, admin controls.
4. **Human-operable workspace plane** — Plane self-hosted for planning, runbooks, wiki, execution coordination.

## Users

| Role | Access | Primary need |
|------|--------|-------------|
| Developers | Read/write | Find specs, architecture docs, API contracts quickly |
| Platform engineers | Read/write | Runbooks, infra docs, deployment procedures |
| Compliance reviewers | Read-only | Audit trails, policy docs, BIR compliance evidence |
| Executives | Read-only | Architecture summaries, delivery status, governance |

## Scope

### In scope

- Deterministic build pipeline (MkDocs or Sphinx)
- Fluent 2 app shell (header, left nav, content pane, right TOC, search, dark mode)
- Content taxonomy with 14 categories
- Plane workspace integration
- Migration of existing 270+ docs to correct canonical surface
- CI publishing to Azure Static Web Apps
- Version switcher for release-tagged docs

### Out of scope

- CMS or WYSIWYG editing
- Public marketing site
- Customer-facing documentation
- Localization (future phase)

## Documentation taxonomy

| # | Category | Canonical surface | Owner | Audience |
|---|----------|-------------------|-------|----------|
| 1 | Architecture | Published site | Platform engineers | All |
| 2 | Product specs | Repo (spec bundles) | Product/engineering | Developers |
| 3 | Delivery plans | Plane | Engineering leads | Engineering, executives |
| 4 | Runbooks | Published site | Platform engineers | Platform engineers |
| 5 | Integrations | Published site | Integration engineers | Developers |
| 6 | Platform/Azure | Published site | Platform engineers | Platform engineers |
| 7 | ERP/Odoo | Published site | Odoo developers | Developers |
| 8 | Data platform | Published site | Data engineers | Data engineers, analysts |
| 9 | AI/Agents | Published site | AI engineers | Developers |
| 10 | Finance/Compliance | Published site | Finance/compliance | Compliance reviewers |
| 11 | Governance/Policies | Repo (contracts) | Engineering leads | All |
| 12 | Release/Change logs | Published site (auto-generated) | CI/CD | All |
| 13 | Templates | Repo | Engineering leads | Developers |
| 14 | Archive | Repo (`docs/archive/`) | None (frozen) | Reference only |

## Success criteria

| Metric | Target |
|--------|--------|
| Build time | Deterministic local build < 5 seconds |
| Coverage | All 270+ docs categorized into exactly one of 14 categories |
| Duplication | Zero duplicate canonical content across planes |
| App shell | Fluent 2 shell with dark mode, left nav, search, right TOC |
| Plane | Workspace created with delivery plans and runbooks linked |
| Accessibility | WCAG 2.2 AA verified |
| Search | Full-text search across all published docs |

## Stack

| Component | Technology |
|-----------|-----------|
| Content/build | MkDocs + Material theme (or Sphinx) |
| App shell | Fluent 2 React v9, FluentProvider, tokens |
| Hosting | Azure Static Web Apps |
| SSOT | Supabase (`spdtwktxdalcfigzeqrz`) |
| Analytical lake | Azure Data Lake Storage (ADLS) |
| ERP | Odoo CE 19 + OCA + ipai_* on Azure Container Apps |
| Workspace | Plane self-hosted |
| CI | GitHub Actions |
