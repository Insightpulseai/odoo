# System Inventory

> One row per major component. Evidence-based, 2026-04-16.

| Component | Layer/Plane | Repo/Path | Runtime/Location | Source of Truth | Current Status | Evidence | Go-Live Criticality |
|---|---|---|---|---|---|---|---|
| Odoo CE 18 Base | Transaction | monorepo root | ACA `ca-ipai-odoo-web-dev` (Sponsored/SEA) | `ssot/odoo/runtime_contract.yaml` | configured (bare shell) | HTTP 200 + health pass; 12 modules only | P0 |
| ipai_* Custom Modules (55) | Transaction | `addons/ipai/` | Not deployed | `ssot/odoo/module_install_manifest.yaml` | repo-defined | 55 dirs in repo; 0 installed in prod DB | P0 |
| OCA Modules | Transaction | `addons/oca/` | Not deployed | `ssot/odoo/oca-baseline.yaml` | repo-defined | Submodules not hydrated | P1 |
| PostgreSQL `odoo` DB | Data | N/A | `pg-ipai-odoo` (Sponsored/SEA) | `ssot/odoo/environment-contract.yaml` | configured | 121 tables, 12 modules | P0 |
| PostgreSQL `odoo_staging` DB | Data | N/A | `pg-ipai-odoo` (Sponsored/SEA) | `ssot/odoo/environment-contract.yaml` | provisioned | 0 tables | P1 |
| PostgreSQL `odoo_dev` DB | Data | N/A | DOES NOT EXIST | `ssot/odoo/environment-contract.yaml` | blocked | psycopg2 FATAL: db does not exist | P1 |
| PG Server `pg-ipai-odoo` | Data | `infra/` | Sponsored sub / SEA | `ssot/odoo/environment-contract.yaml` | live | D4s_v3, 128GiB, v16, Ready | P0 |
| DNS `erp.insightpulseai.com` | Delivery | `infra/dns/` | Azure DNS | `ssot/infrastructure/dns_mail_authority.yaml` | live | dig CNAME correct | -- |
| DNS `prismalab.insightpulseai.com` | Delivery | `infra/dns/` | Azure DNS | `ssot/infrastructure/dns_mail_authority.yaml` | live | dig CNAME correct | -- |
| DNS `www.insightpulseai.com` | Delivery | `infra/dns/` | Azure DNS | `ssot/infrastructure/dns_mail_authority.yaml` | live | dig CNAME correct | -- |
| Azure Front Door `afd-ipai-dev` | Delivery | `infra/` | Sub1 / Global | `ssot/integrations/azure_front_door.yaml` | configured | Active on Sub1; not on Sponsored | P1 |
| Entra ID OAuth | Identity | `ssot/identity/` | Entra tenant | `ssot/identity/odoo-azure-oauth.yaml` | repo-defined | SSOT exists; auth_oauth not installed | P1 |
| Managed Identities (13) | Identity | `infra/` | Both subs / SEA | `ssot/odoo/runtime_contract.yaml` | provisioned | 6 Sponsored + 7 Sub1 | P1 |
| Key Vault `kv-ipai-dev` | Security | `infra/` | Sub1 / SEA | `ssot/odoo/runtime_contract.yaml` | provisioned | Exists; secrets unverified | P0 |
| Key Vault `kv-ipai-dev-sea` | Security | `infra/` | Sponsored / SEA | `ssot/odoo/environment-contract.yaml` | provisioned | Exists; secrets unverified | P0 |
| ACR `acripaiodoo` | Delivery | `infra/` | Sponsored / SEA | N/A | live | 20 repos | -- |
| Databricks `dbw-ipai-dev` | Data | `infra/` | Sponsored / SEA | `ssot/odoo/runtime_contract.yaml` | provisioned | Succeeded, UC enabled | P2 |
| Unity Catalog | Data | `infra/` | Databricks | Memory files | configured (unverified) | Created per memory; not verified this audit | P2 |
| AI Search `srch-ipai-dev-sea` | Agent | `infra/` | Sponsored / SEA | `ssot/integrations/_index.yaml` | provisioned | Resource exists | P2 |
| AI Search `srch-ipai-dev` | Agent | `infra/` | Sub1 / SEA | N/A | provisioned | Resource exists; PrismaLab index | P2 |
| Purview `pv-ipai-dev-sea` | Data | `infra/` | Sponsored / SEA | N/A | provisioned | Resource exists | P3 |
| Service Bus `sb-ipai-dev-sea` | Data | `infra/` | Sponsored / SEA | N/A | provisioned | Resource exists | P3 |
| Redis `cache-ipai-dev` | Data | `infra/` | Sub1 / SEA | N/A | provisioned | Resource exists | P3 |
| AI Services `ipai-copilot-resource` | Agent | `infra/` | Sub1 / East US 2 | `ssot/governance/foundry-model-routing.yaml` | live | 4 model deployments active | P1 |
| AI Services `docai-ipai-dev` | Agent | `infra/` | Sub1 / East US 2 | `ssot/integrations/azure_doc_intelligence.yaml` | provisioned | Resource exists | P2 |
| Copilot Gateway ACA | Agent | `agent-platform/` | Sub1 / SEA (internal) | `ssot/odoo/runtime_contract.yaml` | provisioned | ACA exists; no e2e flow | P2 |
| PrismaLab Gateway ACA | Agent | `apps/prismalab-gateway/` | Sub1 / SEA | `ssot/apps/desired-end-state-matrix.yaml` | live | HTTP 200; RAG index exists | P2 |
| Bot Proxy ACA | Agent | `agent-platform/` | Sub1 / SEA | N/A | provisioned | ACA exists | P3 |
| Odoo MCP ACA | Agent | `mcp/` | Sub1 / SEA (internal) | N/A | provisioned | ACA exists | P2 |
| Website ACA (IPAI) | Delivery | `apps/` | Sponsored + Sub1 / SEA | `ssot/apps/desired-end-state-matrix.yaml` | live | HTTP 200 | P3 |
| Website ACA (PrismaLab) | Delivery | `apps/` | Sponsored / SEA | `ssot/apps/desired-end-state-matrix.yaml` | live | HTTP 200 | P3 |
| Website ACA (W9 Studio) | Delivery | `apps/` | Sponsored + Sub1 / SEA | `ssot/apps/desired-end-state-matrix.yaml` | live | HTTP 200 | P3 |
| Azure Pipelines (15 defs) | Delivery | `azure-pipelines/` | Azure DevOps | CLAUDE.md | repo-defined | Files exist; runs unverified | P0 |
| Power BI | Data | N/A | Fabric capacity | `ssot/integrations/power_bi.yaml` | planned | Trial license; no models | P2 |
| Fabric Mirroring | Data | N/A | `fcipaidev` workspace | `ssot/integrations/fabric_mirroring.yaml` | unknown | Trial status uncertain | P2 |
| Backup Vault | Security | `infra/` | Sponsored / SEA | N/A | provisioned | Resource exists; policies unverified | P1 |
| Recovery Services Vault | Security | `infra/` | Sub1 / SEA | N/A | provisioned | Resource exists; policies unverified | P1 |
| VNet (Sponsored) | Network | `infra/` | Sponsored / SEA | N/A | provisioned | Resource exists | P1 |
| VNet (Sub1) | Network | `infra/` | Sub1 / SEA | N/A | provisioned | Resource exists | P1 |
| Private Endpoints (4) | Network | `infra/` | Both subs / SEA | N/A | provisioned | KV + Search + PG PEs exist | P1 |
| App Insights (4 instances) | Observability | `infra/` | Both subs / SEA | N/A | provisioned | Resources exist | P1 |
| Log Analytics (5 workspaces) | Observability | `infra/` | Both subs / SEA | N/A | provisioned | Resources exist | P1 |
| Alert Rules (3) | Observability | `infra/` | Sub1 / SEA | N/A | provisioned | Content safety, latency, error rate | P1 |
| Zoho SMTP | Email | N/A | Zoho cloud | `ssot/infrastructure/dns_mail_authority.yaml` | unknown | SSOT configured; runtime unverified | P1 |
| Meta CAPI Function App | Integration | `infra/` | Sub1 / SEA | `ssot/integrations/_index.yaml` | provisioned | Function App exists | P3 |
| Agent Skills (180+) | Agent | `agents/skills/` | Repo only | `agents/skills/registry.yaml` | repo-defined | Knowledge definitions; no runtime | P2 |
| Scrum Master Skill | Agent | `agents/skills/scrum_master/` | Repo only | N/A | repo-defined | Skill definition exists | P3 |

---

*Generated 2026-04-16. Status is evidence-based; items marked provisioned or repo-defined lack runtime verification.*
