---
name: Pulser Constitution
description: Enforce Pulser for Odoo architectural invariants — layered authority model, direct-ingress rule, and SaaS multitenancy isolation.
---

# Pulser Constitution Skill

## When to use
When creating or updating any technical specification, design document, or PR to ensure alignment with the authoritative platform rules in [constitution.md](file:///Users/tbwa/Documents/GitHub/Insightpulseai/spec/pulser-odoo/constitution.md).

## Core Invariants

### 1. Layered Authority Model <a id="tg8e4u"></a>
- **Azure Boards**: Planning and governance spine
- **Spec Kit**: Intended-state technical authority
- **GitHub**: Source control and pull-request truth
- **IaC and CI/CD**: Executable deployment truth
- **Azure Runtime**: Actual-state truth
- **RULE**: No single layer substitutes for the others.

### 2. Direct-Ingress Principle <a id="md-direct-ingress"></a>
- **RULE**: No Cloudflare, no proxy-based canonical ingress.
- **Canonical Ingress**: Azure DNS -> Direct custom-domain binding to Azure Container Apps -> Certificate binding at the edge.
- **Exemption**: Azure Front Door is a legacy/decommission target.

### 3. SaaS Multitenancy
- **Tenant Independence**: Pulser Tenant != Odoo Company != Microsoft Entra Tenant.
- **Isolation**: Prevent cross-tenant data leakage or logic overlap.

## Validation Checks
1. Check for Cloudflare or Front Door dependencies (Flag as legacy/prohibited).
2. Verify all technical shifts are first codified in the Spec Kit before implementation.
3. Ensure RBAC refers to Microsoft Entra ID groups, not individual mappings.
