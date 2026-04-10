---
name: Azure Runtime Review
description: Review Azure Container Apps, Front Door, Key Vault, managed identity, and networking configuration for InsightPulseAI platform
---

# Azure Runtime Review Skill

## When to use
When reviewing or modifying Azure infrastructure, deployment configs, or runtime architecture.

## Target architecture

- **Compute**: Azure Container Apps (`cae-ipai-dev` environment)
- **Edge**: Azure Front Door (`ipai-fd-dev`)
- **Database**: Azure Database for PostgreSQL (`ipai-odoo-dev-pg`)
- **Secrets**: Azure Key Vault (`kv-ipai-dev`)
- **Registry**: ACR (`cripaidev`, `ipaiodoodevacr`)
- **DNS**: Cloudflare → Azure Front Door
- **Identity**: Managed identity (transitional from Keycloak to Entra)

## Checks

1. All container apps run in `rg-ipai-dev` resource group
2. Public hostnames route through Azure Front Door, not direct IP
3. Secrets resolve from Key Vault via managed identity, never hardcoded
4. No DigitalOcean, Vercel, or deprecated provider references
5. DNS changes follow YAML-first workflow (`infra/dns/subdomain-registry.yaml`)
6. Container apps run as non-root
7. No public endpoints bypass Front Door WAF

## Reference docs
- `docs/architecture/ROADMAP_TARGET_STATE.md`
- `.Codex/rules/infrastructure.md` (global)
- `ssot/azure/resources.yaml`
