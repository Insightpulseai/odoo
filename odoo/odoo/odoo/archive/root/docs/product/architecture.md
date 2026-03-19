# Architecture

High-level system overview of the InsightPulse AI platform.

## System Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         InsightPulse AI Stack                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   Mattermost ◄──► n8n ◄──► Odoo CE 18 ◄──► PostgreSQL 15            │
│       │           │            │                                     │
│       │           │            ├── Core (8069)                       │
│       │           │            ├── Marketing (8070)                  │
│       │           │            └── Accounting (8071)                 │
│       │           │                                                  │
│       │           └──────────► Supabase (external integrations)      │
│       │                                                              │
│       └─────────────────────► AI Agents (Pulser, Claude, Codex)     │
│                                                                      │
├─────────────────────────────────────────────────────────────────────┤
│  Superset (BI)  │  Keycloak (SSO)  │  DigitalOcean (Hosting)        │
└─────────────────────────────────────────────────────────────────────┘
```

## Multi-Edition Docker Architecture

The stack supports 3 Odoo editions sharing a single PostgreSQL instance:

| Edition | Port | Database | Module Focus |
|---------|------|----------|--------------|
| Core | 8069 | odoo_core | Base CE + IPAI workspace |
| Marketing | 8070 | odoo_marketing | Marketing agency extensions |
| Accounting | 8071 | odoo_accounting | Accounting firm extensions |

## Component Overview

### Odoo CE 18

- **Role**: Core ERP platform
- **Version**: 18.0 Community Edition
- **Extensions**: OCA modules + custom IPAI modules
- **Database**: PostgreSQL 15

### n8n

- **Role**: Workflow automation
- **Integrations**: Odoo, Mattermost, Supabase, external APIs
- **Location**: `n8n/` directory for workflow templates

### Mattermost

- **Role**: Team communication + ChatOps
- **Integrations**: AI agents, webhooks, runbooks
- **Location**: `mattermost/` directory

### Supabase

- **Role**: External integrations only (NOT for Odoo data)
- **Services**: Database, Auth, Storage, Edge Functions, Realtime
- **Project**: `spdtwktxdalcfigzeqrz`

### MCP Servers

Model Context Protocol servers for AI agent integration:

| Server | Purpose |
|--------|---------|
| odoo-erp-server | Odoo ERP integration |
| digitalocean-mcp-server | Infrastructure management |
| superset-mcp-server | BI platform integration |
| pulser-mcp-server | Agent orchestration |
| speckit-mcp-server | Spec enforcement |

## Data Flow

```
User Request
    ↓
Mattermost (ChatOps) / Web UI
    ↓
n8n (Workflow Orchestration)
    ↓
Odoo CE (Business Logic)
    ↓
PostgreSQL (Data Storage)
    ↓
Superset (Analytics/BI)
```

## Security Boundaries

1. **Internal Network**: Odoo, PostgreSQL, n8n, Mattermost
2. **External APIs**: Supabase, third-party integrations
3. **Public Endpoints**: Load balancer → Nginx → Odoo

## Infrastructure

- **Hosting**: DigitalOcean Droplets
- **Container Runtime**: Docker + Docker Compose
- **CI/CD**: GitHub Actions
- **Monitoring**: Health checks, Sentry (errors)
