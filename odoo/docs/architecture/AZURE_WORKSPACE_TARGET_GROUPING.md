# Azure Workspace Target Grouping

## Purpose

Define the canonical end-state grouping for Azure resources as viewed from:
- VS Code Azure extension
- Azure operator/runtime cockpit
- architecture documentation
- environment provisioning and runtime ownership

This grouping is environment-first for operations, while remaining plane-aware in architecture.

## Design intent

The Azure workspace/resource view must answer four questions clearly:

1. What is shared vs workload-specific?
2. Which environment does a runtime belong to?
3. Which service role does a runtime perform?
4. Which services are canonical, legacy, or experimental?

It must not act as a mixed dump of:
- repo topology
- strategy docs
- speculative services
- duplicate app trees
- unnamed runtime roles

## Canonical grouping model

### Top-level grouping

- `insightpulseai-shared`
- `insightpulseai-dev`
- `insightpulseai-staging`
- `insightpulseai-prod`

### Shared platform group

The `shared` group contains substrate and cross-environment services:

- edge
  - front-door
  - waf
  - dns-integration
- identity
  - entra
  - managed-identities
  - workload-identity
- secrets
  - key-vault
- observability
  - log-analytics
  - application-insights
  - monitor-alerts
- network
  - vnet
  - subnets
  - private-dns
  - nsg
  - firewall / perimeter if used

### Environment groups

Each environment contains only workload/runtime services for that environment.

#### `insightpulseai-dev`
- odoo-web
- odoo-worker
- odoo-cron
- auth
- plane
- mcp-coordinator
- mcp-plane
- ocr
- supabase
- superset
- crm
- shelf
- website
- foundry-runtime
- databricks-access

#### `insightpulseai-staging`
- odoo-web
- odoo-worker
- odoo-cron
- auth
- plane
- mcp-coordinator
- ocr
- supabase
- superset
- foundry-runtime
- databricks-access

#### `insightpulseai-prod`
- odoo-web
- odoo-worker
- odoo-cron
- auth
- plane
- mcp-coordinator
- ocr
- supabase
- superset
- foundry-runtime
- databricks-access

## Canonical service naming rules

### Environment names
Use only:
- `shared`
- `dev`
- `staging`
- `prod`

### Runtime service names
Use role-explicit names:
- `odoo-web`
- `odoo-worker`
- `odoo-cron`

Do not use ambiguous runtime names like:
- `odoo` when multiple Odoo runtimes exist
- duplicate `platform` service labels with different meanings

### Cross-plane services
Use stable names:
- `supabase`
- `superset`
- `plane`
- `ocr`
- `auth`
- `mcp-coordinator`
- `mcp-plane`

### Intelligence / agent access surfaces
Use:
- `foundry-runtime`
- `databricks-access`

These are not the full internal service inventories of Foundry or Databricks; they are the environment-facing access/runtime surfaces.

## Plane mapping behind the grouping

The Azure resource view is environment-first, but maps to the canonical architecture planes:

- transactional plane → Odoo runtimes + PostgreSQL
- control plane → Supabase + ops/control services
- intelligence plane → Databricks access + lakehouse connectivity
- agent plane → Foundry runtime + MCP coordination
- experience plane → auth / website / CRM / shelf / portals
- substrate plane → edge / network / identity / observability / secrets
- automation plane → pipelines, jobs, schedulers, runners

The Azure workspace must privilege runtime clarity over conceptual purity.

## What must not appear in the final operator view

- duplicate top-level `insightpulseai-platform` trees
- mixed shared + workload resources in a single bucket
- legacy aliases for canonical repos/planes
- service names without runtime role clarity
- experimental resources presented as canonical production services

## Lifecycle labels

Resources should be classifiable as:

- `canonical`
- `transitional`
- `legacy`
- `experimental`
- `retire`

Only `canonical` and approved `transitional` resources should appear in the main workspace tree.

## SAP-style landscape interpretation

Following whole-landscape guidance, the platform should be legible as:
- shared platform foundation
- environment-separated workloads
- explicit operational boundaries
- clear supporting services for workload runtime

This mirrors the SAP-on-Azure principle that platform landing zone/shared services come first, then workload-specific architecture and operations.

## Databricks / Foundry interpretation

Databricks and Foundry are not represented as giant flat service trees in the Azure operator pane.
Instead, the pane should show the environment-facing access/runtime surfaces, while their deeper internal structure remains documented in their owning repos/docs.

## Delivery implications

- Azure Pipelines and GitHub remain external delivery/control surfaces, not runtime service nodes.
- The Azure workspace tree should reflect deployed runtime/state, not backlog or repo taxonomy.
