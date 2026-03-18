# CAF Team Model

> Version: 1.0.0
> Canonical repo: `infra` / `agent-platform`

## Human Authority
Jake is the executive sponsor, strategy lead, business decision maker, IT decision maker, governance owner, compliance owner, and final approver.
No fake stakeholder theater. 

## Agent Team
The core platform agents are responsible for executing the strategy, organized logically into the following specialist roles:
- `chief-architect`: Cross-repo orchestration, prevents topology drift, routes work, enforces architecture.
- `azure-platform`: Central IT, Azure landing zones, identity/RBAC, Key Vault, networking.
- `odoo-runtime`: Workload product owner for the ERP/transactional capability.
- `foundry-agent`: Workload product owner for the AI runtime, tools, and MCP on Foundry.
- `data-intelligence`: Workload product owner for governed Databricks intelligence plane.
- `release-ops`: Release controls, CI/CD pipeline enforcement, evidence generation.

## Strategy Team Mapping
| CAF Function | Human or Agent |
| :--- | :--- |
| Executive sponsor | Jake |
| Business decision maker | Jake |
| IT decision maker | Jake |
| Lead architect | Jake + `chief-architect` |
| Security | Jake + `azure-platform` |
| Compliance | Jake |
| Finance | Jake |
| Central IT / platform | `azure-platform` |
| Release / delivery | `release-ops` |

## Governance Team Mapping
| Governance Function | Human or Agent |
| :--- | :--- |
| Governance program accountable owner | Jake |
| Architecture oversight | `chief-architect` + `azure-platform` |
| Security oversight | `azure-platform` |
| Compliance / evidence | Jake + `release-ops` |
| Cost management | Jake |
| Policy implementation | `azure-platform` + `release-ops` |
| Workload conformance | `odoo-runtime`, `foundry-agent`, `data-intelligence` |

## Product Model
Instead of a project delivery model, the program operates as a product delivery model:
* **Platform Products**: `infra`, `control-plane`
* **Workload Products**: `odoo`, `agent-platform`, `data-intelligence`, `web`, `automations`
* **Enablement Products**: `.github`, `templates`, `design-system`

## Authority and Escalation
### Human Authority (Jake)
- Approves strategy, repo models, and production migration waves.
- Accepts or rejects residual delivery and production risks.
- Provides manual gates when required by Azure DevOps pipelines (topology, RBAC, cutovers).

### Agent Authority
- **May**: Plan, edit code, prepare PRs, execute CI/CD validations, propose merge/delete operations.
- **May Not**: Unilaterally redefine the target architecture, override explicit security policies, or accept production risks.
