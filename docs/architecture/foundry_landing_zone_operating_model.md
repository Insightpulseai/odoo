# Foundry Landing Zone Operating Model

> Defines the platform landing zone vs application landing zone separation
> for Azure AI Foundry workloads, following the Microsoft baseline reference
> architecture for Foundry in an Azure landing zone.
>
> Ref: https://learn.microsoft.com/en-us/azure/architecture/ai-ml/architecture/baseline-microsoft-foundry-landing-zone
> Cross-references:
>   - `infra/ssot/azure/PLATFORM_TARGET_STATE.md` (infrastructure)
>   - `infra/ssot/azure/resources.yaml` (resource inventory)
>   - `docs/architecture/AI_CONSOLIDATION_FOUNDRY.md` (agent consolidation)
>   - `ssot/governance/operating-model.yaml` (tool authority)

---

## 1. Landing Zone Separation

### Platform Landing Zone

**Owner**: Platform lead
**Scope**: Shared infrastructure consumed by all workloads.

| Resource | Resource Group | Purpose |
|----------|---------------|---------|
| Azure Front Door (`ipai-fd-dev`) | `rg-ipai-shared-dev` | Edge routing, TLS termination, WAF |
| Key Vault (`kv-ipai-dev`) | `rg-ipai-shared-dev` | Secret management for all workloads |
| Container Apps Environment (`cae-ipai-dev`) | `rg-ipai-dev` | Shared compute fabric |
| Log Analytics workspace | `rg-ipai-shared-dev` | Centralized log aggregation |
| Application Insights | `rg-ipai-shared-dev` | APM for all ACA workloads |
| Container Registry (`cripaidev`) | `rg-ipai-shared-dev` | Shared image registry |
| Azure Monitor | `rg-ipai-shared-dev` | Alerting and metrics |
| Defender for Cloud | subscription-level | Security posture management |

**Networking**: All workloads behind Front Door. No direct public IPs on Container Apps.
Internal traffic uses ACA environment's internal DNS and managed VNet integration.

**IAM**: Managed identities per workload. No shared service principals.
Key Vault access via RBAC (Key Vault Secrets User role), not access policies.

### Application Landing Zone

**Owner**: Engineering lead (per workload)
**Scope**: Workload-specific resources isolated by resource group.

| Workload | Resource Group | Key Resources |
|----------|---------------|---------------|
| Odoo ERP | `rg-ipai-dev` | `ipai-odoo-dev-web`, `ipai-odoo-dev-worker`, `ipai-odoo-dev-cron`, `ipai-odoo-dev-pg` |
| AI / Foundry | `rg-ipai-ai-dev` | `aifoundry-ipai-dev`, `oai-ipai-dev`, `docai-ipai-dev`, `srch-ipai-dev` |
| Agents runtime | `rg-ipai-agents-dev` | `vm-ipai-supabase-dev`, agent container apps |
| Data / Databricks | `rg-ipai-data-dev` | `dbw-ipai-dev`, `pg-ipai-dev`, ADLS Gen2 |
| DevOps | `rg-ipai-devops` | Agent pools, Dev Center |

---

## 2. Governance Ownership

| Domain | Owner | Governance Mechanism |
|--------|-------|---------------------|
| Platform landing zone resources | Platform lead | IaC in `infra/` + CI gates |
| Application landing zone resources | Engineering lead (per workload) | IaC in `infra/` + workload-specific pipelines |
| Identity / IAM | Platform lead | Entra ID (target), Keycloak (transitional) |
| Networking / Front Door | Platform lead | `infra/dns/subdomain-registry.yaml` → Terraform |
| Secret management | Platform lead | Key Vault RBAC + managed identity binding |
| Cost management | Platform lead | Azure Cost Management + cluster policies (Databricks) |
| Security posture | Platform lead | Defender for Cloud + GHAS + self-hosted scanning |
| Change management | Both | ADR process (constitution amendment), PR approval |

---

## 3. Foundry-Specific Operating Model

### Agent Lifecycle

```
Define (spec/) → Build (Foundry project) → Test (dev) → Promote (staging) → Deploy (prod)
                                                ↑
                                        Guardrails validated
                                        App Insights connected
                                        Role assignments confirmed
```

### Workload vs Platform Responsibilities

| Responsibility | Platform Team | Workload Team |
|---------------|---------------|---------------|
| Foundry project creation | Provisions project + RBAC | — |
| Agent definition | — | Defines agent spec, tools, instructions |
| Model deployment | Manages quota + deployment slots | Selects model for agent |
| Guardrails | Defines org-wide content safety policy | Applies agent-specific guardrails |
| Monitoring | Provides Application Insights + Log Analytics | Configures agent-specific dashboards |
| Secret access | Provisions Key Vault secrets | References secrets via managed identity |
| Networking | Front Door routing, TLS | Agent endpoint configuration |
| Cost | Budget alerts, quota management | Optimizes token usage per agent |

### Current Foundry State

| Attribute | Value |
|-----------|-------|
| Foundry project | `data-intel-ph` |
| Resource | `data-intel-ph-resource` (East US 2) |
| Active agent | `ipai-odoo-copilot-azure` (v7) |
| Model deployments | `gpt-4.1`, `text-embedding-3-small` |
| Tools | Azure AI Search (`srchipaidev8tlstu`) |
| Guardrails | Present |
| Evaluations | Not yet configured |
| Workflows | Not yet configured |

---

## 4. Shared Resources Model

### Identity

- **Current**: Keycloak (`ipai-auth-dev`) — transitional IdP
- **Target**: Microsoft Entra ID — all apps SSO via OIDC/SAML
- **Migration gates**: OIDC/SAML parity, group/role mapping, service-account replacement, break-glass admin, per-app cutover
- **Constraint**: Do not delete `ipai-auth-dev` until all gates pass

### Networking

- **Edge**: Azure Front Door (`ipai-fd-dev`) — all public traffic
- **DNS**: Cloudflare (authoritative, delegated from Spacesquare)
- **Internal**: ACA environment internal DNS — no cross-RG VNet peering needed currently
- **No VPN**: Single-developer model, no site-to-site connectivity required

### Monitoring

- **APM**: Application Insights (one instance, shared across workloads)
- **Logs**: Log Analytics workspace (centralized)
- **Alerts**: Azure Monitor action groups for critical paths
- **Security**: Defender for Cloud (subscription-level)
- **Custom dashboards**: Superset (self-hosted) for operational metrics

### Policy

- **Azure Policy**: Not yet enforced (deferred — single-subscription, single-developer)
- **Governance**: Platform constitution (CONST-001..010) enforced via CI + code review
- **Cost**: Azure Cost Management alerts (budget TBD)

---

## 5. Change Management

All changes to platform or application landing zones follow:

1. **IaC first**: Changes authored in `infra/` as Bicep/Terraform
2. **PR review**: Platform lead approves platform LZ changes; engineering lead approves workload LZ changes
3. **CI validation**: Infrastructure validators run on PR
4. **Pipeline deployment**: AzDo Pipelines deploy infrastructure changes
5. **Evidence**: Post-deployment evidence captured in `docs/evidence/`

Constitutional amendments (changes to CONST-001..010) require an ADR.

---

*Last updated: 2026-03-17*
