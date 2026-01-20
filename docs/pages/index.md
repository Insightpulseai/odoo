# odoo-ce Documentation

Welcome to the documentation portal for the `odoo-ce` monorepo — the InsightPulse AI platform built on Odoo 18 CE.

## Quick Links

- [Getting Started](getting-started.md) — Clone, bootstrap, and run the dev environment
- [Architecture](architecture.md) — High-level system overview
- [Developer Guide](developer-guide.md) — Conventions, branching, testing, CI
- [Modules](modules.md) — IPAI modules and OCA addons
- [Runbooks](runbooks.md) — Operational procedures

## Stack Overview

| Component | Technology |
|-----------|------------|
| **ERP** | Odoo 18 CE + OCA |
| **Database** | PostgreSQL 15 |
| **Automation** | n8n |
| **Chat** | Mattermost |
| **External DB** | Supabase |
| **BI** | Apache Superset |
| **Hosting** | DigitalOcean |

## Repository Structure

```
odoo-ce/
├── addons/           # Odoo modules (ipai_*, OCA)
├── apps/             # Node.js applications
├── packages/         # Shared packages
├── spec/             # Spec bundles (PRD, plans)
├── scripts/          # Automation scripts
├── docker/           # Docker configurations
├── docs/             # Documentation
├── mcp/              # MCP servers
└── .github/          # CI/CD workflows
```

## Getting Help

- **GitHub Issues**: [Report bugs or request features](https://github.com/jgtolentino/odoo-ce/issues)
- **Wiki**: [Internal runbooks and notes](https://github.com/jgtolentino/odoo-ce/wiki)
