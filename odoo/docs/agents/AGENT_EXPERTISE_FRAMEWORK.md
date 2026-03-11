# Agent Expertise Framework

> Internal capability ladder for agent design, development, and governance.
> Modeled on Microsoft Agent Framework's separation of **functions**, **agents**, and **workflows**.

---

## Core Design Principle

> **If the task can be solved by a normal function, do not use an agent.
> If the task is open-ended and tool-using, use an agent.
> If the task has explicit steps, approvals, or coordination, use a workflow.**

This is the single most important design discipline. Every design review starts here.

---

## Three Design Primitives

| Primitive | When to use | Example |
|-----------|-------------|---------|
| **Function** | Deterministic, stateless, no LLM needed | Tax calculation, PDF generation, data validation |
| **Agent** | Open-ended, conversational, tool-using | Code review assistant, expense classifier, Q&A bot |
| **Workflow** | Defined steps, explicit order, approvals, multi-agent coordination | Month-end close, PR review pipeline, onboarding sequence |

### Decision Tree

```
Is this task deterministic with known inputs/outputs?
  YES --> Use a function
  NO  --> Does it require open-ended reasoning or tool use?
            YES --> Does it have defined steps or need approvals?
                      YES --> Use a workflow (may contain agents as steps)
                      NO  --> Use a single agent
            NO  --> Use a function
```

---

## Capability Ladder

### L1 -- Agent User

Can operate an existing agent safely.

**Must understand:**
- When to use agent vs workflow vs normal function
- Basic prompt discipline
- Evidence capture and output validation
- When to escalate to a specialist

**Output:** Uses approved agent runbooks. No direct production changes.

---

### L2 -- Agent Builder

Can build a single agent end-to-end.

**Must demonstrate:**
- Tool schema design and MCP integration
- Basic state/session handling
- Middleware hooks (logging, auth)
- Provider abstraction (model-agnostic design)
- Failure mode handling and fallbacks
- Auth and permission boundaries

**Output:** Ships one production-capable agent with tests and telemetry.

---

### L3 -- Workflow Builder

Can design graph-based workflows with coordination.

**Must demonstrate:**
- Typed routing between steps
- Checkpoints and resumability
- Retry strategies with backoff
- Human-in-the-loop approval steps
- Multi-agent and multi-function coordination
- State persistence across steps

**Output:** Ships one production workflow with approval gates and observability.

---

### L4 -- Agent Platform Engineer

Can provide shared infrastructure for agents and workflows.

**Must demonstrate:**
- Session/state management architecture
- Memory/context provider design
- Middleware pipeline (auth, logging, policy)
- Telemetry and observability infrastructure
- Provider abstraction layers
- MCP policy and tool boundary enforcement
- CI/CD for agent deployments

**Output:** Shared frameworks, SDKs, evaluation harnesses, deployment pipelines.

---

### L5 -- Agent Architect

Can design multi-agent business systems and set organizational standards.

**Must demonstrate:**
- Domain decomposition for agent portfolios
- When to use agent vs workflow vs plain function (at system scale)
- Human-in-the-loop placement strategy
- Data/compliance boundary enforcement
- Cost modeling and optimization
- Organizational operating model for agents

**Output:** Agent portfolio architecture, governance standards, certification criteria.

---

## Skills Matrix

| Capability | L1 | L2 | L3 | L4 | L5 |
|------------|----|----|----|----|-----|
| Prompt discipline | Required | Required | Required | Required | Required |
| Tool calling | Awareness | Build | Build | Design | Architect |
| MCP integration | Awareness | Build | Build | Design | Architect |
| State/session | Awareness | Use | Design | Build infra | Architect |
| Middleware | -- | Use | Use | Build | Design |
| Workflow orchestration | -- | -- | Build | Build infra | Architect |
| Checkpoints/resumability | -- | -- | Build | Build infra | Architect |
| Human-in-the-loop | Awareness | -- | Build | Build infra | Architect |
| Evaluation harnesses | -- | Build | Build | Design | Certify |
| Observability/telemetry | -- | Use | Use | Build | Design |
| CI/CD for agents | -- | Use | Use | Build | Architect |
| Cost/performance | -- | Awareness | Awareness | Optimize | Govern |
| Compliance/boundaries | Awareness | Awareness | Awareness | Enforce | Design |
| Domain modeling | -- | -- | -- | Awareness | Design |
| Governance | -- | -- | -- | Participate | Lead |

---

## Specialization Tracks

### Track 1: ERP/Odoo Agent Specialist

Focus: Odoo module context, approval workflows, finance/compliance agents, runtime-safe actions.

### Track 2: Platform Agent Engineer

Focus: Queues, event buses, telemetry, identity, secrets, policy, shared SDKs, agent runtime contracts.

### Track 3: Integration Agent Developer

Focus: API/plugin/action design, MCP server development, schema contracts, typed manifests.

### Track 4: Delivery Agent Engineer

Focus: GitHub, CI/CD, release evidence, change management, deployment gating, production rollout.

### Track 5: Domain Agent Consultant

Focus: Domain workflows, process modeling, acceptance criteria, human approvals, business risk.

---

## Internal Certification Badges

| Badge | Level | Requirements |
|-------|-------|-------------|
| IPAI Agent Operator | L1 | Runbook execution, evidence capture |
| IPAI Agent Builder | L2 | Ship one agent with tests + telemetry |
| IPAI Workflow Builder | L3 | Ship one workflow with approvals + checkpoints |
| IPAI Agent Platform Engineer | L4 | Ship shared agent infrastructure |
| IPAI Agent Architect | L5 | Architecture review + governance framework |
| IPAI ERP Agent Specialist | L2+ | Odoo-specific agent certification |

Each certification requires:
- Written architecture review
- Lab completion (see `AGENT_LABS.md`)
- Production-readiness review
- Incident/failure scenario handling

---

## References

- Microsoft Agent Framework Overview: agents vs workflows vs functions
- `docs/agents/AGENT_CURRICULUM.md` -- training tracks
- `docs/agents/AGENT_LABS.md` -- hands-on labs
- `docs/agents/AGENT_REVIEW_CHECKLIST.md` -- design review gates
