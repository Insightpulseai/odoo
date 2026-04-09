---
name: azure-policy-baseline
description: Azure governance policy baseline for IPAI platform
triggers:
  - keywords: ["azure policy", "compliance", "governance", "tagging", "RBAC"]
layer: C-governance
---

# Azure Policy Baseline Skill

Governance rules:

1. All resources must have tags: `environment`, `project`, `owner`, `cost-center`
2. Allowed regions: `southeastasia` (primary), `eastus` (AI services only)
3. No public IP without WAF/Front Door
4. No storage accounts with public blob access
5. Key Vault: soft-delete enabled, purge protection on prod
6. RBAC: least-privilege, no Owner on resource groups (Contributor max for automation)
7. Service principal `ae2df138`: needs subscription Reader for estate audit (currently missing)
8. Managed identities preferred over service principal secrets
9. No classic (ASM) resources — ARM only
10. Cost alerts: budget alerts at 80% and 100% on each resource group
11. Naming convention: `<type>-ipai-<env>[-<service>]` (e.g. `kv-ipai-dev`, `pg-ipai-odoo`)
12. Resource locks: CanNotDelete on production PG and Key Vault
