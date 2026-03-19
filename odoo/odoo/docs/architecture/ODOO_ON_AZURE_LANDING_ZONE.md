# Odoo-on-Azure Landing Zone Accelerator

> Adapted from Microsoft CAF SAP-on-Azure Landing Zone Accelerator.
> SSOT: `ssot/azure/landing_zone.yaml`
> Strategy: `ssot/governance/unified_strategy.yaml`

## Overview

This document defines the landing zone architecture for running Odoo CE 19 + OCA + Azure AI Foundry + Databricks on Azure. It follows the same 5 design areas as the SAP-on-Azure LZA, transposed to the Odoo stack.

---

## 1. Identity and Access Management

**SAP equivalent**: SAP identity integration, SSO, RBAC

### Current state

- Keycloak (`ipai-auth-dev`) as transitional IdP
- Managed identities for ACA workloads: `mi-ipai-odoo-dev`, `mi-ipai-platform-dev`, `mi-ipai-lakehouse-dev` (dev/staging/prod each)
- User-assigned identity for Databricks: `id-ipai-databricks-dev`
- User-assigned identity for ACA: `id-ipai-aca-dev`, `id-ipai-agents-dev`

### Target state (OBJ-001)

- Microsoft Entra ID as canonical IdP
- MFA enforced 100%
- Named accounts for all platform admins
- Emergency access accounts
- Keycloak decommissioned after Entra cutover
- Managed identity for all workload-to-Azure-service auth (zero long-lived secrets)

### Key rule

Odoo is the relying party. Entra ID (target) or Keycloak (transitional) is the IdP. Never store primary passwords in Odoo for users with an external identity counterpart.

---

## 2. Network Topology and Connectivity

**SAP equivalent**: Hub-spoke VNet, Web Dispatcher, ExpressRoute

### Architecture

```
Internet → Cloudflare (DNS-only, authoritative)
         → Azure Front Door (ipai-fd-dev, TLS termination, WAF)
         → Container Apps Environment (ipai-odoo-dev-env)
              → ipai-odoo-dev-web (port 8069)
              → ipai-auth-dev, ipai-mcp-dev, ipai-ocr-dev, etc.
         → PostgreSQL Flexible Server (private endpoint)
         → Databricks VNet (vnet-ipai-databricks, NSG-protected)
```

### Resources

| Resource | Type | Purpose |
|---|---|---|
| `ipai-fd-dev` | Front Door profile | Public edge, TLS, WAF |
| `ipai-fd-dev-ep` | AFD endpoint | Ingress for all public hostnames |
| `ipaiDevWafPolicy` | WAF policy | Web application firewall rules |
| `vnet-ipai-databricks` | VNet | Databricks workspace isolation |
| `nsg-dbw-ipai-dev` | NSG | Databricks network rules |
| `nsg-cae-ipai-dev` | NSG | Container Apps network rules |
| `nsg-pg-ipai-dev` | NSG | PostgreSQL network rules |
| `privatelink.postgres.database.azure.com` | Private DNS zone | PG private endpoint resolution |

### DNS

Cloudflare is authoritative DNS (delegated from Spacesquare). DNS-only mode — no Cloudflare proxy/CDN. All TLS terminates at Front Door.

---

## 3. Business Continuity and Disaster Recovery

**SAP equivalent**: HANA replication, backup, availability zones

### Database

- `ipai-odoo-dev-pg`: PostgreSQL Flexible Server with Azure-managed backups
- Point-in-time restore capability
- Target: geo-redundant backup for production tier

### Compute

- Container Apps support multi-replica scaling
- Stateless Odoo web/worker containers — restart recovers state from PG
- Odoo cron runs as separate Container App (isolation from web/worker)

### Rollback

- Every deployment must have a documented rollback path
- See `docs/operating-model/MIGRATION_OUTCOME_GATE.md` for gate definitions
- See `docs/architecture/LIVE_STATE_DEFINITION.md` for live-state verification

### Target RTO/RPO

| Workload | RTO | RPO |
|---|---|---|
| Odoo ERP (production) | 1 hour | 15 minutes |
| Databricks workspace | 4 hours | 1 hour |
| Front Door / edge | Near-zero (Azure-managed) | N/A |
| Supabase VM | 4 hours | 1 hour |

---

## 4. Security, Governance, and Compliance

**SAP equivalent**: SAP security, GRC, compliance

### Key Vaults

| Vault | Environment | Resource group |
|---|---|---|
| `kv-ipai-dev` | Dev | rg-ipai-shared-dev |
| `kv-ipai-staging` | Staging | rg-ipai-shared-staging |
| `kv-ipai-prod` | Production | rg-ipai-shared-prod |
| `ipai-odoo-dev-kv` | Odoo-specific | rg-ipai-dev |
| `aifoundrkeyvault67125c7c` | Foundry-managed | rg-ipai-ai-dev |

### Security controls

- NSGs on all VNet subnets (Databricks, ACA, PG)
- WAF policy on Front Door
- Defender for Cloud (target: OBJ-007)
- Secret scanning via GitHub Advanced Security
- No secrets in git, logs, or CI output

### Governance

- SSOT files validated by CI gates
- Repo-first: all infrastructure changes via IaC (Bicep/Terraform)
- No console-only changes
- BIR tax compliance for Philippines operations

---

## 5. Platform Automation and DevOps

**SAP equivalent**: SAP deployment automation framework, Azure Center for SAP

### Delivery fabric

| Surface | Role |
|---|---|
| GitHub Actions | Default CI/CD for code, tests, linting |
| Azure DevOps pipelines | Infrastructure deployment (Bicep), environment gates |
| Azure DevOps MCP Server | Agent access to Boards/PRs/builds (tool layer) |
| Dev Center (`ipai-devcenter`) | Developer environments |
| Build pool (`ipai-build-pool`) | Self-hosted agent pool |

### Container registries

| Registry | Purpose |
|---|---|
| `ipaiodoodevacr` | Odoo container images |
| `ipaiwebacr` | Web container images |
| `cripaidev` | Shared container registry |

### Pipeline RACI

- A (Accountable) = human, via environment approval (exceptional stages only)
- R (Responsible) = maker agent jobs
- C (Consulted) = judge agent validation jobs
- I (Informed) = logs, evidence, artifacts

---

## Subscription and Resource Group topology

Single subscription: `Azure subscription 1` (`536d8cf6-...`)

| Resource group | Purpose | Key resources |
|---|---|---|
| `rg-ipai-dev` | Primary workload | 12 Container Apps, PG, KV, ACR x2 |
| `rg-ipai-agents-dev` | Legacy agents + Supabase VM | odoo-web (legacy), VM, ACA env |
| `rg-ipai-ai-dev` | AI/ML services | Foundry, Databricks, Cognitive Services, Search |
| `rg-ipai-data-dev` | Platform database | pg-ipai-dev |
| `rg-ipai-shared-dev` | Shared services (dev) | Front Door, App Insights, KV, Log Analytics, WAF |
| `rg-ipai-shared-staging` | Shared services (staging) | KV, managed identities |
| `rg-ipai-shared-prod` | Shared services (prod) | KV, managed identities |
| `rg-ipai-devops` | DevOps infrastructure | Dev Center, build pool |
| `rg-data-intel-ph` | Foundry project | AI Services resource + project |
| `rg-dbw-managed-ipai-dev` | Databricks managed | Storage, identity, access connector |

---

## Compute — Container Apps inventory

| App | RG | Ingress | Role |
|---|---|---|---|
| `ipai-odoo-dev-web` | rg-ipai-dev | Public | Odoo ERP web |
| `ipai-odoo-dev-worker` | rg-ipai-dev | None | Background jobs |
| `ipai-odoo-dev-cron` | rg-ipai-dev | None | Scheduled jobs |
| `ipai-auth-dev` | rg-ipai-dev | Public | Keycloak SSO |
| `ipai-mcp-dev` | rg-ipai-dev | Public | MCP coordination |
| `ipai-ocr-dev` | rg-ipai-dev | Public | Document OCR |
| `ipai-superset-dev` | rg-ipai-dev | Public | Apache Superset BI |
| `ipai-plane-dev` | rg-ipai-dev | Public | Plane project mgmt |
| `ipai-shelf-dev` | rg-ipai-dev | Public | Shelf service |
| `ipai-crm-dev` | rg-ipai-dev | Public | CRM service |
| `ipai-website-dev` | rg-ipai-dev | Public | Website |
| `odoo-web` | rg-ipai-agents-dev | Internal | Legacy (retire candidate) |

---

## Exceptions

| Exception | Justification |
|---|---|
| Supabase on Azure VM (not ACA) | Self-hosted Supabase requires full VM for PostgreSQL + GoTrue + PostgREST + Realtime stack |
| Single subscription | Solo-maintainer; blast-radius isolation via resource groups, not subscriptions |
| Cloudflare DNS-only | Front Door handles TLS/WAF; Cloudflare provides authoritative DNS only |

---

## Cross-references

- Strategy: `docs/strategy/CAF_STRATEGY_COMPLETE.md`
- Live-state gates: `docs/architecture/LIVE_STATE_DEFINITION.md`
- Migration gates: `docs/operating-model/MIGRATION_OUTCOME_GATE.md`
- Team model: `docs/operating-model/CAF_TEAM_MODEL.md`
- Org topology: `ssot/repo/org_topology.yaml`
- Unified strategy: `ssot/governance/unified_strategy.yaml`
- SAP parity benchmark: `docs/architecture/SAP_AFC_PARITY.md`
