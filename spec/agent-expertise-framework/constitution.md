# Agent Expertise Framework — Constitution

> Non-negotiable rules governing how agent expertise is defined, measured, and certified.

## Rule 1: Expertise is a career lattice, not a workshop

Agent expertise spans cloud architecture, identity, deployment, data grounding, developer tooling, platform integration, and domain specialization. It is never reduced to "can prompt well."

## Rule 2: Six levels, no shortcuts

| Level | Title | Gate |
|-------|-------|------|
| L0 | Agent User | Prompt discipline, task scoping, evidence capture |
| L1 | Agent Operator | Task decomposition, artifact validation, rollback awareness |
| L2 | Agent Builder | Ships one production-capable agent with tests and telemetry |
| L3 | Agent Platform Engineer | Ships shared frameworks for agents, tools, evaluation, deployment |
| L4 | Agent Solution Architect | Designs multi-agent business systems with governance |
| L5 | Agent Domain Fellow | Defines standards for a vertical (ERP, Copilot, Azure AI, adtech) |

No level may be skipped. Each level requires evidence, a lab deliverable, and a reviewer sign-off.

## Rule 3: Five role tracks

1. **Agent AI Engineer** — model selection, grounding, retrieval, prompt/system design, tool use, evaluation, safety
2. **Agent Developer** — API/plugin/action design, frontend embedding, backend controllers, SDK wrappers, schema contracts
3. **Agent DevOps** — deploy pipelines, environment promotion, runtime config, secrets, observability, cost controls, rollback
4. **Agent Solution Architect** — reference architectures, service boundaries, platform operating model, identity, governance
5. **Agent Functional Consultant** — domain workflows, process modeling, acceptance criteria, human approvals, business risk

Everyone follows one primary track. Cross-track competency is encouraged but not required.

## Rule 4: Six specialist schools

1. **Azure Agent School** — Azure OpenAI, AI Search, Container Apps, Postgres, observability, workload design
2. **Microsoft 365 / Copilot Agent School** — M365 Developer Program sandbox, Graph grounding, Copilot APIs, Agents Toolkit, Agent Store, MCP declarative agents
3. **Odoo / ERP Agent School** — ERP process grounding, Odoo module/context access, approval workflows, finance/compliance agents, runtime-safe actions
4. **Platform Agent School** — queues, event buses, telemetry, identity, secrets, policy, shared SDKs, agent runtime contracts
5. **Delivery Agent School** — GitHub, CI/CD, release evidence, change management, deployment gating, production rollout
6. **Domain Agent School** — marketing/adtech, finance/PPM, operations/finops, customer support/helpdesk

## Rule 5: Sandbox-first practice

All learning requires sandbox environments. Never use production for training.

| Sandbox | Purpose |
|---------|---------|
| Agent sandbox | Isolated agent development and testing |
| Integration sandbox | Cross-service connectivity validation |
| Prod-like staging | Pre-production verification with synthetic data |

Equivalent environments: Azure dev subscription, M365 developer sandbox, Odoo dev database, Supabase dev project, GitHub non-prod environment.

## Rule 6: Applied labs, not theory

Each level requires a real deliverable, not a quiz. Examples:
- Build a retrieval-backed Q&A agent
- Build an approval agent with Slack
- Build a GitHub PR/issue summarizer
- Build an Odoo expense or invoice copilot
- Build a Copilot/M365 agent grounded in org documents
- Deploy an agent with telemetry and rollback

## Rule 7: Internal certification is sovereign

Internal badges (IPAI Agent Operator, Builder, Platform Engineer, Architect, ERP Specialist, Copilot Specialist) do not wait for external certification programs. Each requires:
- Written architecture review
- Lab completion
- Production-readiness review
- Incident/failure scenario handling

## Rule 8: Governance is mandatory at L3+

From L3 upward, every agent must have:
- Design review board approval
- Eval thresholds documented
- Runtime evidence pack
- Kill-switch/rollback pattern
- Cost controls

## Rule 9: Environment terminology

Per `docs/runtime/CURRENT_ENVIRONMENT.md`:
- **Local** — developer machine
- **Shared Live Sandbox** — current state (publicly reachable, non-production data)
- **Future Production** — not yet established

Never call the current environment "production."

## Rule 10: Microsoft alignment, not dependency

This framework mirrors Microsoft's public credential structure (Azure AI Engineer, Developer, DevOps Engineer, Solutions Architect, Applied Skills, M365 Developer Program, Agents Toolkit) as a reference model. It does not depend on Microsoft certification for internal validity.
