# Agent Certification Paths

> Internal certification badges for agent expertise. Sovereign to IPAI — does not depend on external certification programs.

## Certification badges

### IPAI Agent Operator (L1)

**Prerequisites**: L0 complete
**Track**: Any

| Requirement | Detail |
|------------|--------|
| Task decomposition | Demonstrate breaking a problem into agent tasks |
| Artifact validation | Review and approve 3 agent outputs |
| Rollback execution | Successfully rollback one agent action |
| Policy awareness | Pass policy/risk awareness check |
| Environment selection | Correctly choose dev/staging/sandbox for 3 scenarios |

**Assessment**: Supervised execution of standard agent flow with post-review.

### IPAI Agent Builder (L2)

**Prerequisites**: IPAI Agent Operator (L1)
**Track**: AI Engineer, Developer, or DevOps

| Requirement | Detail |
|------------|--------|
| Ship one agent | End-to-end: design -> build -> test -> deploy |
| Prompt contract | Documented system prompt with guardrails |
| Tool schema | At least one typed tool interface |
| Eval suite | Automated evaluation with pass/fail criteria |
| Telemetry | Agent emits metrics/logs to observability stack |
| Failure handling | Documented error/timeout/hallucination handling |

**Assessment**: Architecture review + working demo + code review.

### IPAI Agent Platform Engineer (L3)

**Prerequisites**: IPAI Agent Builder (L2)
**Track**: AI Engineer, Developer, or DevOps

| Requirement | Detail |
|------------|--------|
| Shared framework | Ship a reusable component (SDK, tool library, eval harness) |
| Multi-agent orchestration | Demonstrate coordination of >=2 agents |
| Memory strategy | Implement session or long-term memory |
| CI/CD pipeline | Automated agent testing and deployment |
| Observability | Dashboard with agent metrics |
| Governance review | Pass design review board assessment |

**Assessment**: Platform contribution review + governance board sign-off.

### IPAI Agent Architect (L4)

**Prerequisites**: IPAI Agent Platform Engineer (L3)
**Track**: Solution Architect

| Requirement | Detail |
|------------|--------|
| Architecture design | Multi-agent system design document |
| Domain decomposition | Map business processes to agent boundaries |
| Human-in-the-loop | Design approval gates for agent actions |
| Compliance | Meet regulatory requirements for agent domain |
| Cost model | Budget and cost projection for agent portfolio |
| Governance | Define operating model for agent team |

**Assessment**: Architecture review board presentation + written evaluation.

### IPAI ERP Agent Specialist (School)

**Prerequisites**: IPAI Agent Builder (L2)
**School**: Odoo / ERP Agent School

| Requirement | Detail |
|------------|--------|
| ERP grounding | Agent accesses Odoo models correctly |
| Approval workflows | Agent integrates with Odoo approval chains |
| Finance/compliance | Agent handles BIR/tax/regulatory data safely |
| Runtime safety | Agent cannot corrupt ERP state |
| Domain lab | Complete Odoo ask-AI lab |

**Assessment**: Working ERP agent demo + domain expert review.

### IPAI Copilot Agent Specialist (School)

**Prerequisites**: IPAI Agent Builder (L2)
**School**: Microsoft 365 / Copilot Agent School

| Requirement | Detail |
|------------|--------|
| M365 sandbox | Enrolled in Microsoft 365 Developer Program |
| Graph grounding | Agent uses Microsoft Graph for data access |
| Copilot API | Agent uses Copilot extensibility APIs |
| Agent Store | Agent packaged for Agent Store distribution |
| MCP integration | Declarative agent with MCP tool binding |
| Domain lab | Complete M365 Copilot/Graph sandbox lab |

**Assessment**: Working Copilot agent demo + platform review.

## Assessment process

### Step 1: Self-assessment

Candidate reviews their evidence against badge requirements.

### Step 2: Lab completion

Candidate completes required labs for the badge level.

### Step 3: Architecture review

For L2+: written architecture document reviewed by qualified reviewer (one level above).

### Step 4: Production-readiness review

For L2+: demonstrate deployment with telemetry, rollback capability, and error handling.

### Step 5: Incident simulation

For L3+: handle a simulated agent failure scenario (timeout, hallucination, data corruption, cost runaway).

### Step 6: Board review (L4+)

Present to agent design review board for final sign-off.

## Reviewer requirements

| Badge level | Reviewer minimum level |
|-------------|----------------------|
| L1 Operator | L2 Builder |
| L2 Builder | L3 Platform Engineer |
| L3 Platform Engineer | L4 Architect |
| L4 Architect | L5 Fellow or Review Board |
| School Specialist | L3+ in same school |
