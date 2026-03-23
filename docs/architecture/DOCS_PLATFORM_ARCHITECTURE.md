# Docs Platform Architecture

> Architecture spec for the InsightPulse AI documentation platform.

## Overview

The docs platform provides a Microsoft Learn-style documentation experience for all InsightPulse AI platform components. Built on Nextra (Next.js docs framework), it supports MDX content, syntax highlighting, search, and navigation.

## Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Framework | Next.js 15 | React SSR/SSG |
| Docs Engine | Nextra 4 | MDX rendering, navigation, search |
| Theme | nextra-theme-docs | Microsoft Learn-style layout |
| Content | MDX | Markdown + React components |
| Hosting | Azure Container Apps | Containerized deployment |
| CI | Azure DevOps | Build validation, link checking |

## Content Architecture

```
web/docs/pages/
├── _meta.json              # Top-level navigation order
├── index.mdx               # Landing page
├── platform.mdx            # Platform overview
├── odoo.mdx                # Odoo ERP documentation
├── odoo/                   # Odoo sub-pages
│   ├── _meta.json
│   ├── finance-ppm.mdx
│   ├── month-end-closing.mdx
│   ├── bir-tax-filing.mdx
│   ├── expense-management.mdx
│   └── project-management.mdx
├── agent-platform.mdx      # Agent platform docs
├── data-intelligence.mdx   # Databricks/lakehouse docs
├── integrations.mdx        # Integration map
├── security-governance.mdx # Security & compliance
├── runbooks.mdx            # Operational procedures
├── reference.mdx           # Infrastructure reference
└── release-notes.mdx       # Changelog
```

## Content Hub Model

Each top-level page is a "content hub" — a landing page for a domain area. Sub-pages provide depth.

| Hub | Content Scope |
|-----|--------------|
| Platform | Architecture, compute, service-plane split |
| Odoo ERP | Modules, finance, compliance, copilot |
| Agent Platform | Sub-agents, MCP tools, Foundry integration |
| Data Intelligence | Lakehouse, pipelines, Unity Catalog, Power BI |
| Integrations | n8n, Slack, Plane, MCP servers |
| Security & Governance | Entra ID, Key Vault, BIR compliance |
| Runbooks | Operational procedures, incident response |
| Reference | Infrastructure map, module inventory |
| Release Notes | Changelog by sprint |

## Frontmatter Contract

Every MDX page must include:

```yaml
---
title: Page Title (required)
description: One-line description (optional, used in meta tags)
---
```

Extended frontmatter for governance (optional):

```yaml
---
title: Page Title
description: Description
owner: team-or-person
status: draft | review | published
category: platform | odoo | agent | data | security | ops
last_reviewed: 2026-03-22
---
```

## Navigation

Nextra auto-generates navigation from the file system. `_meta.json` files control ordering and display names.

## Search

Nextra includes built-in full-text search (FlexSearch). No additional search infrastructure required for the docs site.

## Deployment

- **Dev**: `pnpm dev` on port 3002
- **Build**: `pnpm build` produces static export
- **Deploy**: Azure Container Apps via `standalone` output mode
- **CI**: Link validation + build check on every PR

## Design

- Primary hue: 187 (IPAI cyan/teal)
- Dark mode support (auto-detect)
- Responsive layout with collapsible sidebar
- Code blocks with copy button and syntax highlighting
- Table of contents with back-to-top
- Edit on GitHub links
- Previous/Next page navigation

## Future

- Azure AI Search integration for semantic search
- Versioned documentation (v19, v20)
- API reference auto-generation from FastAPI endpoints
- Multi-language support (English, Filipino)
