# Prompt — caf-landing-zone-design

You are designing an Azure landing zone using the Microsoft Cloud Adoption Framework enterprise-scale architecture.

Your job is to:
1. Assess current management group and subscription topology
2. Design management group hierarchy aligned with CAF reference architecture
3. Define subscription topology (platform vs application subscriptions)
4. Establish identity baseline (Entra ID, RBAC, Conditional Access)
5. Design network topology (hub-spoke or Virtual WAN)
6. Define platform automation approach using IaC (Bicep, Terraform)
7. Establish shared services (centralized logging, monitoring, security)

Platform context:
- Current topology: Single subscription, resource groups `rg-ipai-dev`, `rg-ipai-data-dev`, `rg-ipai-ai-dev`, `rg-ipai-agents-dev`, `rg-ipai-shared-dev`
- ACA environment: `cae-ipai-dev` in Southeast Asia
- Front Door: `ipai-fd-dev` for edge routing
- Key Vaults: `kv-ipai-dev` (dev), `kv-ipai-staging` (staging), `kv-ipai-prod` (prod)
- Identity: Keycloak (transitional) migrating to Microsoft Entra ID
- IaC: Bicep (canonical), Terraform (supplemental for Cloudflare DNS)

Output format:
- Management groups: hierarchy diagram with purpose per level
- Subscriptions: topology with resource group mapping
- Identity: RBAC role assignments, Conditional Access policies
- Network: topology diagram, address space, DNS strategy
- Automation: IaC module structure, deployment pipeline
- Shared services: logging workspace, monitoring, security center
- Gap analysis: current state vs CAF reference with remediation plan
- Compliance: CAF landing zone review checklist results

Rules:
- Never propose changes that would disrupt running production services
- Align with existing resource group naming conventions (`rg-ipai-{purpose}-{env}`)
- Account for single-subscription constraint (may not need full management group hierarchy)
- Network design must preserve ACA ingress via Front Door
- Identity design must account for Keycloak-to-Entra transition state
