# Azure Operator View Target State

> **Version**: 1.0.0
> **Scope**: Target state topology for the Azure platform operator pane, enforcing environment-first isolation and eliminating duplicate workspace groupings.

## 1. Context and Problem Statement
The current Azure environment view suffers from visual duplicate `insightpulseai-platform` workspace groupings, mixed shared/runtime services, and ambiguous naming (e.g., `odoo` instead of `odoo-web`). The target end state of the Azure pane must be a **clean environment control view** of the platform, structured deterministically by environment rather than conceptual architectural planes.

The Azure UI sidebar is the **runtime/operator cockpit**, not an architecture map. It should instantly answer:
1. Where does the platform run?
2. Which environment does a service belong to?
3. What is shared substrate vs. workload-specific?

## 2. Target Hierarchy (Environment First)

The canonical view must resolve exactly to this structure:

```text
Azure subscription 1
  insightpulseai-shared
    edge
    identity
    key-vault
    observability
    network

  insightpulseai-dev
    odoo-web
    odoo-worker
    odoo-cron
    auth
    plane
    mcp-coordinator
    mcp-plane
    ocr
    supabase
    superset
    crm
    shelf
    website

  insightpulseai-staging
    odoo-web
    odoo-worker
    odoo-cron
    auth
    plane
    mcp-coordinator
    ocr
    supabase
    superset

  insightpulseai-prod
    odoo-web
    odoo-worker
    odoo-cron
    auth
    plane
    mcp-coordinator
    ocr
    supabase
    superset
```

## 3. Structural Rules & Enforcements

### A. The Shared Layer (`insightpulseai-shared`)
The shared platform substrate **must never be mixed into the app runtime list**. It exclusively holds:
- Azure Front Door / WAF (Edge)
- Azure Key Vault
- Log Analytics Workspace / Application Insights (Observability)
- Shared identities (UMIs)
- VNet / Private DNS / NSGs

### B. The Environment Layer
Every workload service must be deployed into a strict environment-level Resource Group: `dev`, `staging`, or `prod`. No duplicate top-level "platform" buckets are permitted to span environments.

### C. Deterministic Service Naming
Service names reflect their **runtime role**, not their product family.
- **FORBIDDEN**: `odoo`
- **REQUIRED**: `odoo-web`, `odoo-worker`, `odoo-cron`

### D. Deprecation & Cleanup
Any service currently deployed that is not part of the active canonical platform must be moved out of the main workspace view or tagged explicitly as:
- `legacy`
- `experimental`
- `retire`

## 4. Logical vs. Azure View Mapping
Behind the scenes, the architecture remains aligned to functional planes (Odoo = transactional, Supabase = control, Databricks = intelligence, Foundry = agent). However, the Azure deployment strategy **flattens** this into the environment operator view to prevent a messy, nested duplicate service tree.
