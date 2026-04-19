# App Surface and MCP Topology

Canonical source:
- [`platform/ssot/org/app-surface-and-mcp-topology.yaml`](../../platform/ssot/org/app-surface-and-mcp-topology.yaml)

## Purpose

Define the four primary application surfaces and the cross-cutting MCP/tooling model across the operating org.

## Four primary app surfaces

| App | Domain | Class | Launch priority |
|---|---|---|---|
| ERP | [erp.insightpulseai.com](https://erp.insightpulseai.com) | transactional_app | P0 |
| InsightPulseAI Main | [www.insightpulseai.com](https://www.insightpulseai.com) | flagship_web_app | P1 |
| W9 Studio | [www.w9studio.net](https://www.w9studio.net) | business_unit_app | P2 |
| PrismaLab | [prismalab.insightpulseai.com](https://prismalab.insightpulseai.com) | domain_app | P2 |

## Ownership split

| Repo | Role |
|---|---|
| `web` | Owns app surfaces (4 apps) |
| `platform` | Owns MCP policy and connector contracts |
| `agent-platform` | Owns runtime tool/session execution |
| `agents` | Owns personas, skills, judges, and task contracts |
| `odoo` | Owns transactional truth for ERP |
| `data-intelligence` | Owns analytics/retrieval surfaces |
| `infra` | Owns infrastructure substrate |
| `docs` | Owns architecture and runbooks |

## Rules

- MCP is cross-cutting and must be app-scoped
- No blanket cross-app tool access
- Side-effecting tools require policy, approval, and audit
- Production connectors must be explicitly approved
- Secrets must be vaulted or brokered, never exposed as plaintext in runtime

## Per-app MCP scope

| App | Allowed categories | Disallowed categories | Side-effect policy |
|---|---|---|---|
| ERP | odoo_tools · approval_workflows · document_ai · notifications · github_search_readonly_optional | unrestricted_external_connectors · cross_app_admin_tools | guarded |
| InsightPulseAI Main | public_content_tools · analytics_read_tools · assistant_tools · document_search_readonly | direct_transactional_write_tools · internal_finance_tools | mostly_readonly |
| W9 Studio | content_ops_tools · booking_tools_optional · asset_ops_tools_optional · notifications | erp_finance_admin_tools · broad_cross_tenant_connectors | guarded |
| PrismaLab | research_tools · document_ai · analytics_read_tools · citation_search | unrelated_business_unit_tools · unrestricted_procurement_tools | guarded |

## Environment scoping

| Environment | Read connectors | Side-effecting tools |
|---|---|---|
| dev | Relaxed read-only allowed | Test or sandbox only |
| staging | Production-like read | Guarded non-prod only |
| production | Only explicitly approved | Approval + audit required |

## Tenant and domain boundaries

- App domain maps to allowed tool scope
- No cross-app tool access without explicit policy
- No cross-tenant data access without explicit grant
- Hidden or sensitive data visibility must follow RBAC

## Cross-repo contracts

| Producer | Consumer | Contract |
|---|---|---|
| platform | agent-platform | mcp_tool_registry_and_policy |
| agents | agent-platform | app_specific_personas_skills_judges |
| data-intelligence | agent-platform + web | analytics_and_retrieval_surfaces |
| odoo | agent-platform + web | transactional_tool_surfaces_for_erp |

## Assertions

- `Insightpulse-ai` is primary operating org for all 4 apps
- MCP is cross-cutting, not a standalone app
- `platform` owns policy
- `agent-platform` owns runtime execution
- `agents` owns behavioral definitions
- Each app has explicit tool scope

## Related

- Org target state: [`ssot/governance/github-enterprise-org-target-state.yaml`](../../ssot/governance/github-enterprise-org-target-state.yaml)
- Clean chain: [`platform/ssot/architecture/github-azure-chain.yaml`](../../platform/ssot/architecture/github-azure-chain.yaml)
- Pulser pack matrix: [`platform/ssot/agents/pulser-pack-matrix.yaml`](../../platform/ssot/agents/pulser-pack-matrix.yaml)
- Surface bindings: [`platform/ssot/agents/surface-bindings.yaml`](../../platform/ssot/agents/surface-bindings.yaml)
- MCP allowlist: [`ssot/governance/mcp-allowlist.yaml`](../../ssot/governance/mcp-allowlist.yaml)
- AI governance baseline: [`platform/ssot/policy/azure-ai-governance-baseline.yaml`](../../platform/ssot/policy/azure-ai-governance-baseline.yaml)
- Skill/pack pattern unified: [`ssot/agent-platform/skill-pack-pattern-unified.yaml`](../../ssot/agent-platform/skill-pack-pattern-unified.yaml)
- Site template adoption: [`ssot/web/site-template-adoption.yaml`](../../ssot/web/site-template-adoption.yaml)
