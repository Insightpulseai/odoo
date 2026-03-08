# Agent Expertise Framework

> Role-based capability ladder for agent expertise, modeled after Microsoft's credential structure.

## Design principle

Expertise is a **career lattice**, not a workshop. Agent capability spans cloud architecture, identity, deployment, data grounding, developer tooling, platform integration, and domain specialization. It is never reduced to "can prompt well."

## Capability levels

### L0 — Agent User

Can safely use existing agents.

| Capability | Detail |
|-----------|--------|
| Prompt discipline | Writes clear, scoped prompts |
| Task scoping | Knows what agents can and cannot do |
| Evidence capture | Saves and reviews agent outputs |
| Escalation | Knows when to hand off to a specialist |

**Output**: Uses approved agent runbooks. No direct production changes.

### L1 — Agent Operator

Can run and supervise agents in bounded workflows.

| Capability | Detail |
|-----------|--------|
| Task decomposition | Breaks problems into agent-sized tasks |
| Artifact validation | Reviews agent outputs before merge/deploy |
| Rollback awareness | Knows how to revert agent actions |
| Policy/risk awareness | Understands compliance boundaries |
| Environment selection | Chooses dev vs staging vs sandbox correctly |

**Output**: Executes standard agent flows. Reviews outputs before merge/deploy.

### L2 — Agent Builder

Can build one agent end-to-end.

| Capability | Detail |
|-----------|--------|
| Prompt contract design | Defines system prompts, tool schemas, guardrails |
| Tool schema design | Builds typed tool interfaces |
| Grounding/data-source design | Connects agents to knowledge sources |
| Evaluation harnesses | Writes eval suites for agent quality |
| Failure mode handling | Handles errors, timeouts, hallucinations |
| Auth and permission boundaries | Implements least-privilege access |

**Output**: Ships one production-capable agent with tests and telemetry.

### L3 — Agent Platform Engineer

Can build reusable agent infrastructure.

| Capability | Detail |
|-----------|--------|
| Orchestration | Multi-step, multi-agent coordination |
| Memory/context strategy | Session, conversation, long-term memory |
| Queue/event architecture | Async processing, event-driven agents |
| Model/provider abstraction | Swap models without code changes |
| Secrets/RBAC | Secure credential management |
| Observability | Metrics, traces, logs for agents |
| CI/CD for agents | Automated testing and deployment |

**Output**: Shared frameworks for agents, tools, evaluation, deployment.

### L4 — Agent Solution Architect

Can design multi-agent business systems.

| Capability | Detail |
|-----------|--------|
| Domain decomposition | Maps business processes to agent boundaries |
| Interoperability | Agents work across systems (Odoo, Azure, M365) |
| Human-in-the-loop approvals | Designs approval gates |
| Compliance | Meets regulatory and policy requirements |
| Cost controls | Budget management per agent |
| Org operating model | Defines how agents fit the organization |

**Output**: Agent portfolio architecture, governance, and roadmap.

### L5 — Agent Domain Fellow

Can define standards for a vertical.

| Specialization | Example focus |
|---------------|--------------|
| ERP/Odoo agent fellow | Odoo module patterns, finance agents, compliance |
| Copilot/M365 agent fellow | Graph grounding, Teams integration, Agent Store |
| Azure AI platform fellow | Azure OpenAI, AI Search, Container Apps |
| Marketing/adtech agent fellow | Campaign automation, analytics agents |

**Output**: Canonical patterns, reviews, curriculum, and certification standards.

## Role tracks

| Track | Focus areas |
|-------|-------------|
| **Agent AI Engineer** | Model selection, grounding, retrieval, prompt/system design, tool use, evaluation, safety |
| **Agent Developer** | API/plugin/action design, frontend embedding, backend controllers, SDK wrappers, schema contracts, tests |
| **Agent DevOps** | Deploy pipelines, environment promotion, runtime config, secrets, observability, cost controls, rollback |
| **Agent Solution Architect** | Reference architectures, service boundaries, platform operating model, identity, governance |
| **Agent Functional Consultant** | Domain workflows, process modeling, acceptance criteria, human approvals, business risk |

## Specialist schools

| School | Focus |
|--------|-------|
| **Azure Agent School** | Azure OpenAI, AI Search, Container Apps, Postgres, observability, workload design |
| **Microsoft 365 / Copilot Agent School** | M365 Developer Program sandbox, Graph grounding, Copilot APIs, Agents Toolkit, Agent Store, MCP declarative agents |
| **Odoo / ERP Agent School** | ERP process grounding, Odoo module/context access, approval workflows, finance/compliance agents |
| **Platform Agent School** | Queues, event buses, telemetry, identity, secrets, policy, shared SDKs, agent runtime contracts |
| **Delivery Agent School** | GitHub, CI/CD, release evidence, change management, deployment gating |
| **Domain Agent School** | Marketing/adtech, finance/PPM, operations/finops, customer support/helpdesk |

## Sandbox environments

| Sandbox | Purpose | Provider |
|---------|---------|----------|
| Agent sandbox | Isolated agent dev/test | Azure dev subscription |
| M365 dev sandbox | Copilot/Graph agent dev | Microsoft 365 Developer Program |
| Odoo dev sandbox | ERP agent dev | `odoo_dev` database |
| Supabase dev sandbox | Data/auth agent dev | Supabase dev project |
| GitHub non-prod | CI/CD agent dev | GitHub environment with protection rules |

## Applied labs (minimum 6)

1. Azure OpenAI + AI Search — retrieval-backed Q&A agent
2. Slack approval agent — approval workflow with Slack integration
3. GitHub PR/issue agent — PR summarizer using GitHub API
4. Odoo ask-AI — expense or invoice copilot
5. M365 Copilot/Graph sandbox — Copilot agent grounded in org documents
6. Evaluation/telemetry — agent deployment with observability and rollback

## Phased rollout

| Phase | Scope | Timing |
|-------|-------|--------|
| 1 | Capability framework (this doc + matrix + cert paths) | Week 1-2 |
| 2 | Lab catalog (≥6 labs with templates) | Week 3-4 |
| 3 | Sandbox environments (provisioned, isolated) | Week 5-6 |
| 4 | Assessments (rubrics, first L2 cert) | Week 7-8 |
| 5 | Governance (review board, promotion standards) | Week 9-10 |

## References

- [Microsoft Credentials Catalog](https://learn.microsoft.com/en-my/credentials/browse/?products=azure)
- [Microsoft 365 Developer Program](https://developer.microsoft.com/en-us/microsoft-365/dev-program)
- [Microsoft 365 Copilot APIs](https://devblogs.microsoft.com/microsoft365dev/microsoft-365-copilot-apis/)
- [Microsoft 365 Agents Toolkit](https://devblogs.microsoft.com/microsoft365dev/introducing-the-microsoft-365-agents-toolkit/)
- Spec bundle: `spec/agent-expertise-framework/`
