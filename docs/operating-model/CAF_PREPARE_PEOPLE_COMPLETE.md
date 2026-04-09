# CAF Plan — Prepare Your People for Cloud (Complete)

> Tailored rewrite of Microsoft CAF "Plan → Prepare your people for the cloud."
> Cross-references: `CAF_TEAM_MODEL.md`, `CAF_PREPARE_ORGANIZATION_COMPLETE.md`, `cloud_people_readiness.yaml`

---

## 1. What this stage means

Equip the human authority and the execution system around that human with the skills necessary for successful Azure adoption. Reduce implementation risk. Create a culture of continuous learning.

For a solo founder with agents, "prepare people" means: **prepare the human authority and the agent system you documented and constrained.** The "people" are you + the agents.

---

## 2. Capability map

### Platform lane skills

| Skill | Needed by |
|---|---|
| Azure operating model (CAF) | Human + chief-architect |
| Identity / RBAC / secrets | Human + azure-platform |
| CI/CD pipeline controls | Human + release-ops |
| Monitoring / alerts / observability | Human + azure-platform |
| Governance guardrails | Human + governance-judge |

### Workload lane skills

| Skill | Needed by |
|---|---|
| Odoo CE 18 module development + OCA discipline | odoo-runtime |
| Agent Framework basics + tool integration | foundry-agent |
| Governed data products + CDC + medallion | data-intelligence |
| Next.js / frontend development | web |
| n8n workflow design + automation contracts | automations |

### Agent development skills

| Skill | Needed by |
|---|---|
| Agent Framework DevUI (local debug/trace) | foundry-agent, all makers |
| Foundry Agent Service (production hosting) | foundry-agent |
| MCP tool boundaries | agent-platform |
| Eval design and execution | agent-platform |

---

## 3. Role map

### Human authority

Jake is accountable for: strategy, risk acceptance, production exceptions, budget/FinOps, final go-live authority.

### Execution lanes

| Lane | Agents |
|---|---|
| Platform | chief-architect, azure-platform, release-ops |
| Workloads | odoo-runtime, foundry-agent, data-intelligence, web, automations |
| Review | architecture-judge, security-judge, governance-judge, finops-judge, customer-value-judge, tbwa-fit-judge |

---

## 4. Training surfaces

### Agent Framework DevUI (learning + debug)

- Visualize agents and workflows locally
- Debug tool calls and inspect traces (OpenTelemetry)
- Test multi-agent orchestration patterns
- Python-first samples (C# coming soon per Microsoft)
- **Not for production use** — development and training only

### Microsoft Foundry (production runtime)

- Fully managed Azure PaaS for enterprise AI
- Host, deploy, and scale agents
- Foundry Agent Service for hosted agents (Agent Framework, LangGraph, custom code)
- Production telemetry via Application Insights

### Rule

> Learn and debug in DevUI. Host and scale in Foundry. Govern via SSOT and CI gates.

---

## 5. Learning paths by product plane

### `infra/` and `platform/`

1. Azure operating model fundamentals
2. Identity and secret boundary management
3. Pipeline and environment controls
4. Monitoring and alerting setup
5. Governance guardrail implementation

### `agent-platform/`

1. Agent Framework basics (Python SDK)
2. DevUI: run local samples, inspect traces
3. Tool integration patterns (MCP boundaries)
4. Multi-agent workflow orchestration
5. Promote validated patterns to Foundry Agent Service
6. Eval design and continuous improvement

### `data-intelligence/`

1. Governed data product design
2. AI-ready data contracts
3. CDC bridge and medallion architecture
4. Context publishing to agents
5. Databricks / Unity Catalog publication paths

### `odoo/`

1. Odoo CE 18 module architecture
2. OCA-first module discipline
3. External bridge patterns (Foundry, Supabase)
4. Testing and upgrade-safe customization
5. Odoo 18 breaking changes awareness

### `web/`

1. Next.js / React fundamentals
2. Browser extension development
3. Secure frontend patterns (zero browser-side secrets)
4. Advisory copilot integration

---

## 6. Readiness criteria

### Platform lane readiness

- [ ] Understands Azure operating model (CAF)
- [ ] Can operate identity and secret boundaries
- [ ] Can run CI/CD gates end to end
- [ ] Can set up monitoring and alerting

### Workload lane readiness

- [ ] Can build and validate changes in assigned product plane
- [ ] Can run tests and produce evidence
- [ ] Understands ownership boundaries (what this repo owns / does not own)

### Agent lane readiness

- [ ] Can run local DevUI samples
- [ ] Can inspect agent traces
- [ ] Can promote validated agent patterns to Foundry
- [ ] Understands MCP tool boundaries

---

## 7. Guided learning surfaces

The **Foundry VS Code extension** is the primary guided-learning surface for project-scoped AI development. It supports project navigation, model catalog access, model deployment, generated sample code, and playground-driven iteration. Local debugging and experimentation (DevUI, Local Visualizer) remain distinct from hosted production runtime promotion (Foundry Agent Service).

See `agent-platform/docs/learning/AGENT_GUIDED_LEARNING_PATHS.md` for the full 6-lane progression: foundations → project fluency → model deployment → local experimentation → hosted promotion → governance readiness.

---

## 8. Review cadence

- Per-objective: assess readiness before objective work begins
- Per-cutover: verify readiness before production deployment
- Quarterly: reassess skill gaps and training needs
- On new tool/platform adoption: update training paths

---

## SSOT reference

Machine-readable readiness model: `ssot/governance/cloud_people_readiness.yaml`
