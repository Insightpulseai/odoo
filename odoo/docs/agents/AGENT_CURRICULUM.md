# Agent Curriculum

> Training tracks for the IPAI Agent Expertise Framework.
> Each track maps to capability levels defined in `AGENT_EXPERTISE_FRAMEWORK.md`.

---

## Track A -- Agent Fundamentals (L1-L2)

Target: Everyone who builds or operates agents.

### Module A1: Agent vs Workflow vs Function

- Decision tree: when each primitive applies
- Anti-patterns: using agents for deterministic tasks, using functions for open-ended reasoning
- Exercise: classify 10 real tasks into the correct primitive

### Module A2: Single Agent Design

- Prompt contract structure (system prompt, user prompt, tool results)
- Tool schema definition and registration
- Input validation and output parsing
- Error handling and graceful degradation

### Module A3: MCP Integration

- MCP protocol fundamentals (resources, tools, prompts)
- Connecting an agent to one MCP server
- Tool boundary enforcement
- Authentication and credential handling via environment variables

### Module A4: State and Session Management

- Session lifecycle (create, persist, resume, expire)
- Context window management
- Memory patterns: short-term (session), long-term (database)
- State serialization and deserialization

### Module A5: Middleware and Observability

- Middleware pipeline concept (pre-call, post-call hooks)
- Logging middleware: structured logs for every tool call
- Auth middleware: token validation, permission checks
- Telemetry: latency, token usage, error rates

---

## Track B -- Workflow Engineering (L2-L3)

Target: Builders who need multi-step orchestration.

### Module B1: Sequential Workflows

- Linear step execution
- Input/output contracts between steps
- Error propagation and step-level retries

### Module B2: Branching Workflows

- Conditional routing based on step output
- Type-safe route definitions
- Fallback and default branches

### Module B3: Concurrent Workflows

- Parallel step execution
- Fan-out/fan-in patterns
- Dependency graph resolution
- Race conditions and mutex patterns

### Module B4: Approval Workflows

- Human-in-the-loop step design
- Approval request/response protocol
- Timeout and escalation policies
- Audit trail for approval decisions

### Module B5: Resumable Workflows

- Checkpoint design: what to persist
- Resume from checkpoint after failure
- Idempotent step execution
- Long-running workflow patterns (hours/days)

---

## Track C -- Architecture Decision Discipline (L3-L5)

Target: Architects and senior builders.

### Module C1: Task Classification

Every learner must answer these questions for any proposed agent system:

1. Is this task open-ended or deterministic?
2. Should it be a plain function?
3. Should it be a single agent?
4. Should it be a workflow?
5. Does it need multi-agent coordination?
6. Does it need human approval?

### Module C2: Boundary Design

- Data classification: what can leave trusted boundaries
- Tool exposure policy: which tools agents can access
- MCP server trust model: first-party vs third-party
- Geographic and compliance boundaries

### Module C3: Cost and Performance

- Token usage budgets per agent/workflow
- Model selection by task complexity (use cheapest model that works)
- Caching strategies for repeated queries
- Latency budgets and SLA design

### Module C4: Multi-Agent Systems

- Agent-to-agent communication patterns
- Supervisor/worker architectures
- Shared context vs isolated context
- Conflict resolution between agents

---

## Track D -- Enterprise Controls (L3-L5)

Target: Platform engineers and architects.

### Module D1: State Management Infrastructure

- Session store design (Redis, PostgreSQL, Supabase)
- TTL and cleanup policies
- Cross-service session sharing

### Module D2: Telemetry Infrastructure

- Structured logging standards
- Metrics collection (Prometheus/OpenTelemetry patterns)
- Trace correlation across agent calls
- Dashboard design for agent health

### Module D3: Middleware and Policy

- Policy-as-code for tool access
- Rate limiting and quota enforcement
- Content filtering middleware
- Audit logging for compliance

### Module D4: Provider Abstraction

- Model-agnostic agent design
- Provider switching without code changes
- Fallback chains (primary model -> backup model)
- Cost routing (route to cheaper model when possible)

### Module D5: Compliance and Data Boundaries

- Data residency requirements
- PII handling in agent context
- Third-party MCP server risk assessment
- Audit and evidence requirements

---

## Track E -- ERP/Odoo Agent Specialization (L2+)

Target: Odoo developers building agent-powered modules.

### Module E1: Odoo Context Access

- Reading Odoo models via XML-RPC / JSON-RPC
- MCP server for Odoo (`mcp/servers/odoo-erp-server/`)
- Field-level access control in agent context
- Record-level security (ir.rule) implications

### Module E2: Odoo Approval Agents

- `ipai_approvals` workflow integration
- Agent-assisted approval routing
- Human override patterns
- Audit trail in Odoo chatter

### Module E3: Finance and Compliance Agents

- BIR compliance validation agents
- Month-end close orchestration
- Expense classification agents
- Tax computation verification

### Module E4: Odoo Module as Agent Host

- Embedding agent capabilities in ipai_* modules
- Configuration via ir.config_parameter
- Cron-triggered agent workflows
- User-facing agent UX in Odoo views

---

## Assessment Requirements by Level

| Level | Required Assessments |
|-------|---------------------|
| L1 | Classify 10 tasks, operate one agent safely |
| L2 | Build one agent, connect one MCP server, add telemetry |
| L3 | Build one workflow with approvals and checkpoints |
| L4 | Ship shared agent infrastructure, design review participation |
| L5 | Architecture review, governance framework, incident simulation |

---

## References

- `docs/agents/AGENT_EXPERTISE_FRAMEWORK.md` -- capability ladder
- `docs/agents/AGENT_LABS.md` -- hands-on exercises
- `docs/agents/AGENT_REVIEW_CHECKLIST.md` -- design review gates
