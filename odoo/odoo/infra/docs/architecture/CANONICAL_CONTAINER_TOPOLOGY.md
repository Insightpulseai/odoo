# Canonical Container Topology

**Version**: 1.0.0
**Last Updated**: 2026-03-11
**SSOT**: `ssot/runtime/container-topology.yaml`

---

## Overview

This document defines the platform-wide container/service target state for all environments. It is the canonical reference for naming, service decomposition, and runtime classification.

**Ownership**: `infra/` owns the global topology. `odoo/` consumes it for ERP-specific runtime contracts.

---

## Local Development Target

**Required**: 2 core containers for day-to-day coding.

| Container | Role |
|-----------|------|
| `insightpulse-devcontainer` | Main coding container (Python, Node, Odoo tooling, git, linters, dev shell) |
| `insightpulse-dev-db` | Local PostgreSQL sidecar |

**Optional** (run only when testing specific surfaces):

| Container | Role | When Needed |
|-----------|------|-------------|
| `insightpulse-dev-redis` | Cache | Testing cache-dependent features |
| `insightpulse-dev-ocr` | OCR service | Testing document processing |
| `insightpulse-dev-mailcatcher` | Mail sink (Mailpit) | Testing email flows |
| `insightpulse-dev-mcp` | MCP server | Testing MCP integrations |
| `insightpulse-dev-n8n` | Automation | Testing workflow triggers |

**Local rule**: For normal editing, the clean default is **2 containers**. Do not keep a half-alive runtime stack around during normal editing.

---

## Azure Production Target

**Target**: 10 runtime units (ACA apps/jobs).

### Naming Convention

```
ipai-<service>-<env>
```

Where `<env>` is one of: `dev`, `staging`, `prod`.

### Core Odoo (4 units)

| Service | Type | Role | Notes |
|---------|------|------|-------|
| `ipai-odoo-web` | App | Odoo HTTP/RPC server | Primary web-facing service |
| `ipai-odoo-worker` | App | Async worker (longpolling, cron offload) | Handles long-running requests |
| `ipai-odoo-cron` | App | Scheduled actions runner | Executes `ir.cron` jobs |
| `ipai-odoo-init` | Job | Module install/upgrade | Runs on deploy, not persistent |

### Platform Services (6 units)

| Service | Type | Role | Notes |
|---------|------|------|-------|
| `ipai-auth` | App | Authentication gateway | Keycloak |
| `ipai-mcp` | App | MCP server coordinator | Model Context Protocol |
| `ipai-n8n` | App | Workflow automation | Self-hosted n8n |
| `ipai-ocr` | App | Document OCR processing | |
| `ipai-superset` | App | BI dashboards | Apache Superset |
| `ipai-plane` | App | Project management | Plane.so |

### Database / Cache (Managed Services)

| Service | Target | Notes |
|---------|--------|-------|
| PostgreSQL | Azure Database for PostgreSQL Flexible Server | Not a container in production |
| Redis | Azure Cache for Redis (if needed) | Not a container in production |

---

## Environment Examples

### Dev
```
ipai-odoo-web-dev
ipai-odoo-worker-dev
ipai-odoo-cron-dev
ipai-odoo-init-dev
ipai-auth-dev
ipai-mcp-dev
ipai-n8n-dev
ipai-ocr-dev
ipai-superset-dev
ipai-plane-dev
```

### Staging
```
ipai-odoo-web-staging
ipai-odoo-worker-staging
ipai-odoo-cron-staging
ipai-odoo-init-staging
ipai-auth-staging
ipai-mcp-staging
ipai-n8n-staging
ipai-ocr-staging
ipai-superset-staging
ipai-plane-staging
```

### Production
```
ipai-odoo-web-prod
ipai-odoo-worker-prod
ipai-odoo-cron-prod
ipai-auth-prod
ipai-mcp-prod
ipai-n8n-prod
ipai-ocr-prod
ipai-superset-prod
ipai-plane-prod
```

Note: `ipai-odoo-init-prod` runs as a job during deployments, not as a persistent container.

---

## Prohibited in Target State

- Generic names like `odoo-web` (must use `ipai-` prefix)
- Duplicate names like both `odoo-web` and `ipai-odoo-web`
- Legacy stack names like `ipai-nginx`
- Multiple unrelated postgres containers without explicit role naming
- Dead/exited containers in the active project
- Docker Desktop / default context drift names
