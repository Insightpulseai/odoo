# System Inventory (v2)

> One row per major component. Evidence-based, 2026-04-16.
> v2 additions: reporting/analytics rows, Databricks surface distinctions, finance cutover, tenant boundary, source-quality notes

| Component | Layer/Plane | Repo/Path | Runtime/Location | Source of Truth | Current Status | Readiness Stage | Evidence | Go-Live Criticality |
|---|---|---|---|---|---|---|---|---|
| Odoo CE 18 Base | Transaction | monorepo root | ACA `ca-ipai-odoo-web-dev` (Sponsored/SEA) | `ssot/odoo/environment-contract.yaml` | configured (bare shell) | prerequisite-pending | HTTP 200 + health pass + assets serving; 12 modules only | P0 |
| ipai_* Custom Modules (55) | Transaction | `addons/ipai/` | Not deployed | `ssot/odoo/module_install_manifest.yaml` | repo-defined | blocked | 55 dirs in repo; 0 installed; 0/55 pass doctrine | P0 |
| OCA Modules | Transaction | `addons/oca/` | Not deployed | `ssot/odoo/oca-baseline.yaml` | repo-defined | blocked | Submodules not hydrated | P1 |
| Finance Cutover | Transaction | `addons/ipai/` | N/A | `ssot/assurance/review-gates.yaml` | blocked | blocked | All checks N/A: no account module | P0 |
| PostgreSQL `odoo` DB | Data | N/A | `pg-ipai-odoo` (Sponsored/SEA) | `ssot/odoo/environment-contract.yaml` | configured | prerequisite-pending | 121 tables, 12 modules, ir_attachment.location=db | P0 |
| PostgreSQL `odoo_staging` DB | Data | N/A | `pg-ipai-odoo` (Sponsored/SEA) | `ssot/odoo/environment-contract.yaml` | provisioned | blocked | 0 tables | P1 |
| PostgreSQL `odoo_dev` DB | Data | N/A | Local only (correct per contract) | `ssot/odoo/environment-contract.yaml` | repo-defined | prerequisite-pending | Local-only; does not exist on Azure (expected) | P2 |
| PG Server `pg-ipai-odoo` | Data | `infra/` | Sponsored sub / SEA | `ssot/odoo/environment-contract.yaml` | live | deployment-ready | D4s_v3, 128GiB, v16, Ready, publicAccess | P0 |
| DNS `erp.insightpulseai.com` | Delivery | `infra/dns/` | Azure DNS | `ssot/infrastructure/dns_mail_authority.yaml` | live | stabilization-required | dig CNAME correct (blackriver) | -- |
| DNS `prismalab.insightpulseai.com` | Delivery | `infra/dns/` | Azure DNS | `ssot/infrastructure/dns_mail_authority.yaml` | live | stabilization-required | dig CNAME correct (whitedesert) | -- |
| DNS `www.insightpulseai.com` | Delivery | `infra/dns/` | Azure DNS | `ssot/infrastructure/dns_mail_authority.yaml` | live | stabilization-required | dig CNAME correct (blackstone/Sub1) | -- |
| Azure Front Door `afd-ipai-dev` | Delivery | `infra/` | Sub1 / Global | N/A | configured | prerequisite-pending | Active on Sub1; not on Sponsored | P1 |
| Entra ID OAuth | Identity | `ssot/identity/` | Entra tenant 402de71a | `ssot/identity/odoo-azure-oauth.yaml` | repo-defined | blocked | Enterprise app registered; auth_oauth not installed; tenant ID conflict | P1 |
| Managed Identities (13) | Identity | `infra/` | Both subs / SEA | `ssot/odoo/runtime_contract.yaml` | provisioned | prerequisite-pending | 6 Sponsored + 7 Sub1 | P1 |
| Tenant/Company Boundary | Identity | `ssot/tenants/` | Odoo res.company | `ssot/tenants/tenant-registry.yaml` | repo-defined | prerequisite-pending | 4 tenants defined; only 1 likely exists | P1 |
| Enterprise Apps (11) | Identity | `ssot/identity/` | Entra | `ssot/identity/enterprise-apps.runtime-state.yaml` | configured | prerequisite-pending | 11 observed; identity surfaces, not tenant boundaries | P1 |
| App Registrations (21) | Identity | N/A | Entra | N/A | unknown | unknown | Not enumerated this audit | P2 |
| Key Vault `kv-ipai-dev` | Security | `infra/` | Sub1 / SEA | `ssot/odoo/runtime_contract.yaml` | provisioned | prerequisite-pending | Exists; secrets unverified | P0 |
| Key Vault `kv-ipai-dev-sea` | Security | `infra/` | Sponsored / SEA | `ssot/odoo/environment-contract.yaml` | provisioned | prerequisite-pending | Exists; secrets unverified | P0 |
| ACR `acripaiodoo` | Delivery | `infra/` | Sponsored / SEA | N/A | live | deployment-ready | 20 repos | -- |
| Databricks Workspace | Data | `infra/` | Sponsored / SEA | N/A | provisioned | prerequisite-pending | Succeeded, UC enabled | P2 |
| Databricks Admin Console | Data | `infra/` | Sponsored / SEA | N/A | unknown | unknown | Not assessed | P2 |
| Databricks Developer Tooling | Data | `infra/ssot/databricks/` | Local + Workspace | `infra/ssot/databricks/developer-tooling.contract.yaml` | repo-defined | prerequisite-pending | Contracts defined; VS Code ext contract exists | P3 |
| Databricks Apps Runtime | Data | N/A | Sponsored / SEA | N/A | unknown | unknown | Not assessed | P3 |
| Unity Catalog | Data | `infra/` | Databricks | Agent memory | configured (unverified) | prerequisite-pending | Created per memory; not verified this audit | P2 |
| AI Search `srch-ipai-dev-sea` | Agent | `infra/` | Sponsored / SEA | N/A | provisioned | prerequisite-pending | Resource exists | P2 |
| AI Search `srch-ipai-dev` | Agent | `infra/` | Sub1 / SEA | N/A | provisioned | prerequisite-pending | Resource exists; PrismaLab index | P2 |
| Purview `pv-ipai-dev-sea` | Data | `infra/` | Sponsored / SEA | N/A | provisioned | prerequisite-pending | Resource exists | P3 |
| Service Bus `sb-ipai-dev-sea` | Data | `infra/` | Sponsored / SEA | N/A | provisioned | prerequisite-pending | Resource exists | P3 |
| Redis `cache-ipai-dev` | Data | `infra/` | Sub1 / SEA | N/A | provisioned | prerequisite-pending | Resource exists | P3 |
| AI Services `ipai-copilot-resource` | Agent | `infra/` | Sub1 / East US 2 | `ssot/governance/foundry-model-routing.yaml` | live | stabilization-required | 4 model deployments active | P1 |
| AI Services `docai-ipai-dev` | Agent | `infra/` | Sub1 / East US 2 | N/A | provisioned | prerequisite-pending | Resource exists | P2 |
| Copilot Gateway ACA | Agent | `agent-platform/` | Sub1 / SEA (internal) | `ssot/governance/agent-interop-matrix.yaml` | provisioned | prerequisite-pending | ACA exists; no e2e flow | P2 |
| PrismaLab Gateway ACA | Agent | `apps/prismalab-gateway/` | Sub1 / SEA | N/A | live | stabilization-required | HTTP 200; RAG index exists | P2 |
| Bot Proxy ACA | Agent | `agent-platform/` | Sub1 / SEA | N/A | provisioned | prerequisite-pending | ACA exists | P3 |
| Odoo MCP ACA | Agent | `mcp/` | Sub1 / SEA (internal) | N/A | provisioned | prerequisite-pending | ACA exists | P2 |
| Scrum Master Agent | Agent | `agents/skills/scrum_master/` | Repo only | N/A | repo-defined | prerequisite-pending | 65/100 score; spec complete, code partial, control missing | P3 |
| Website ACA (IPAI) | Delivery | `apps/` | Sponsored / SEA | N/A | live | stabilization-required | HTTP 200 | P3 |
| Website ACA (PrismaLab) | Delivery | `apps/` | Sponsored / SEA | N/A | live | stabilization-required | HTTP 200 | P3 |
| Website ACA (W9 Studio) | Delivery | `apps/` | Sponsored + Sub1 / SEA | N/A | live | stabilization-required | HTTP 200 | P3 |
| Azure Pipelines (15 defs) | Delivery | `azure-pipelines/` | Azure DevOps | CLAUDE.md | repo-defined | unknown | Files exist; runs unverified | P0 |
| Power BI | Reporting | N/A | Fabric capacity | N/A | planned | blocked | Trial license; no models; no reports | P2 |
| Fabric Mirroring | Data | N/A | `fcipaidev` workspace | N/A | unknown | unknown | Trial status uncertain | P2 |
| ADO Dashboards | Reporting | N/A | Azure DevOps | N/A | unknown | unknown | Not verified | P2 |
| ADO Analytics Views | Reporting | N/A | Azure DevOps | `ssot/semantic/odata-entity-map.yaml` (stub) | unknown | unknown | Not queried | P2 |
| ADO Pipeline Analytics | Reporting | `azure-pipelines/` | Azure DevOps | N/A | unknown | unknown | No run history | P2 |
| Power BI + ADO Integration | Reporting | N/A | Power BI + ADO OData | N/A | planned | blocked | No semantic model; trial license | P2 |
| Google Workspace (W9) | Collaboration | N/A | Google (w9studio.net) | `ssot/tenants/tenant-registry.yaml` | configured | N/A | Collaboration workspace, NOT tenant boundary | P3 |
| Backup Vault | Security | `infra/` | Sponsored / SEA | N/A | provisioned | prerequisite-pending | Resource exists; policies unverified | P1 |
| Recovery Services Vault | Security | `infra/` | Sub1 / SEA | N/A | provisioned | prerequisite-pending | Resource exists; policies unverified | P1 |
| VNet (Sponsored) | Network | `infra/` | Sponsored / SEA | N/A | provisioned | prerequisite-pending | Resource exists | P1 |
| VNet (Sub1) | Network | `infra/` | Sub1 / SEA | N/A | provisioned | prerequisite-pending | Resource exists | P1 |
| Private Endpoints (4) | Network | `infra/` | Both subs / SEA | N/A | provisioned | prerequisite-pending | KV + Search + PG PEs exist | P1 |
| App Insights (4 instances) | Observability | `infra/` | Both subs / SEA | N/A | provisioned | prerequisite-pending | Resources exist | P1 |
| Log Analytics (5 workspaces) | Observability | `infra/` | Both subs / SEA | N/A | provisioned | prerequisite-pending | Resources exist | P1 |
| Alert Rules (3) | Observability | `infra/` | Sub1 / SEA | N/A | provisioned | prerequisite-pending | Content safety, latency, error rate | P1 |
| Zoho SMTP | Email | N/A | Zoho cloud | `ssot/infrastructure/dns_mail_authority.yaml` | unknown | unknown | SSOT configured; runtime unverified | P1 |
| Meta CAPI Function App | Integration | `infra/` | Sub1 / SEA | N/A | provisioned | prerequisite-pending | Function App exists | P3 |
| Agent Skills (180+) | Agent | `agents/skills/` | Repo only | N/A | repo-defined | prerequisite-pending | Knowledge defs; no runtime; audit grade D (44/100) | P2 |
| Agent Interop Matrix v2 | Agent | `ssot/governance/` | Repo only | `ssot/governance/agent-interop-matrix.yaml` | repo-defined | prerequisite-pending | A2A v0.2.0, 8+ agents defined | P2 |
| Review Gates (5 phases) | Assurance | `ssot/assurance/` | Repo only | `ssot/assurance/review-gates.yaml` | repo-defined | prerequisite-pending | 5 phases; prepare gate not started | P1 |
| Vercel GitHub App | Integration | N/A | GitHub | N/A | stale | blocked | Deprecated; needs uninstall | P3 |

---

*Generated 2026-04-16 v2. Status is evidence-based; items marked provisioned or repo-defined lack runtime verification. Readiness stage added in v2.*
