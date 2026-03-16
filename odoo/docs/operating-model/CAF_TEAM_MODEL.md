# CAF Strategy Team Model

> Maps Microsoft CAF strategy-team functions to the solo-founder + maker/judge agent operating model.

## Principle

One human holds all strategic decision authority. Agents are execution and review functions. No fake stakeholder hierarchies.

## Team mapping

| CAF function | Human | Agent(s) | Accountability |
|---|---|---|---|
| Executive sponsor | Jake | — | Final authority on priorities, risk, resources |
| Business decision maker | Jake | — | Business outcome ownership |
| IT decision maker | Jake | chief-architect | Technology selection, architecture decisions |
| Lead architect | Jake | chief-architect | Cross-cutting architecture |
| Central IT / platform | Jake | azure-platform | Landing zones, shared services, infra |
| Security | Jake | security-judge | Identity, RBAC, secrets, vulnerability posture |
| Compliance / governance | Jake | governance-judge | SSOT consistency, CI gate coverage, audit |
| Finance / FinOps | Jake | finops-judge | Cost optimization, resource efficiency |
| Workload: ERP | Jake | odoo-runtime | Odoo CE modules, runtime correctness |
| Workload: Agents | Jake | foundry-agent | Foundry runtime, agent workflows, evals |
| Workload: Data | Jake | data-intelligence | Databricks pipelines, data products |
| Workload: Web | Jake | — | Frontend apps, portals, browser extensions |
| Release / delivery | Jake | release-ops | Deploy, evidence, rollback, SRE feedback |
| Customer value | Jake | customer-value-judge | Business outcome alignment |
| Client fit | Jake | tbwa-fit-judge | TBWA/SMP packaging and offering fit |

## Decision model

- **Strategic decisions**: Human only (priorities, risk acceptance, resource allocation)
- **Architecture decisions**: Human + chief-architect (proposals require human approval)
- **Implementation decisions**: Maker agents (execute within spec boundaries)
- **Quality decisions**: Judge agents (validate, flag, but do not block without human override)
- **Deploy decisions**: Automatic for nonprod; protected gates only for destructive/RBAC/topology/cutover changes

## Product-plane ownership

| Product type | Planes |
|---|---|
| Platform products | infra, platform |
| Workload products | odoo, agent-platform, data-intelligence, web, automations |
| Enablement products | .github, agents, design, templates, docs |

Each product plane has persistent ownership. No temporary project teams.

## Operating model

**Shared management with centralized human accountability.** Platform products establish guardrails; workload products operate autonomously within them. See `CAF_PREPARE_ORGANIZATION_COMPLETE.md` for the full operating-model decision and responsibility maps.

## Cross-references

- Strategy: `docs/strategy/CAF_STRATEGY_COMPLETE.md`
- Organization prep: `docs/operating-model/CAF_PREPARE_ORGANIZATION_COMPLETE.md`
- Machine-readable model: `ssot/governance/cloud_operating_model.yaml`
- Migration gates: `docs/operating-model/MIGRATION_OUTCOME_GATE.md`
- Live-state definition: `docs/architecture/LIVE_STATE_DEFINITION.md`
