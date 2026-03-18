# Agent Labs

> Hands-on exercises for the IPAI Agent Expertise Framework.
> Each lab produces a working deliverable, not just theory.

---

## Lab 1: First Agent (L1-L2)

**Objective:** Build a minimal agent that answers questions using one tool.

**Deliverables:**
- Agent with system prompt and one tool (e.g., file reader)
- Structured logging of every tool call
- Input validation on user prompts
- Test harness with 5 test cases

**Acceptance criteria:**
- Agent responds correctly to 5/5 test prompts
- Every tool call is logged with timestamp, input, output
- Agent gracefully handles malformed input

---

## Lab 2: Tool-Enabled Agent (L2)

**Objective:** Build an agent that uses multiple tools to complete a task.

**Deliverables:**
- Agent with 3+ tools (e.g., database query, HTTP fetch, file write)
- Tool selection logic (agent picks the right tool for the task)
- Error handling when a tool fails
- Token usage tracking

**Acceptance criteria:**
- Agent correctly selects tools for 10 varied prompts
- Failed tool calls produce user-facing error messages, not stack traces
- Token usage is recorded per request

---

## Lab 3: MCP-Enabled Agent (L2)

**Objective:** Connect an agent to an MCP server and use its tools.

**Deliverables:**
- Agent connected to one MCP server (e.g., `odoo-erp-server` or `github`)
- Tool discovery from MCP server manifest
- Auth credential handling via environment variables
- Request/response logging

**Acceptance criteria:**
- Agent discovers tools from MCP server at startup
- Agent executes at least 3 different MCP tools successfully
- No credentials appear in logs or output

---

## Lab 4: Stateful Agent (L2)

**Objective:** Add session state to an agent so it remembers context across turns.

**Deliverables:**
- Multi-turn conversation with context retention
- Session persistence (survives process restart)
- Session expiry after configurable TTL
- Session cleanup on explicit end

**Acceptance criteria:**
- Agent correctly references information from 3+ turns ago
- Session survives simulated restart
- Expired sessions produce clean "session not found" responses

---

## Lab 5: Sequential Workflow (L3)

**Objective:** Build a linear workflow with typed step contracts.

**Deliverables:**
- 4-step workflow (e.g., fetch data -> validate -> transform -> store)
- Typed input/output contracts between steps
- Step-level error handling with retry (max 3 attempts)
- Execution log with step timing

**Acceptance criteria:**
- Workflow completes successfully end-to-end
- A step failure triggers retry, then fails gracefully after 3 attempts
- Execution log shows step name, duration, status for each step

---

## Lab 6: Checkpointed Workflow (L3)

**Objective:** Build a workflow that can resume from the last successful step after failure.

**Deliverables:**
- 5-step workflow with checkpoint after each step
- Checkpoint persistence (database or file)
- Resume command that picks up from last checkpoint
- Idempotent step execution (re-running a step produces same result)

**Acceptance criteria:**
- Kill workflow at step 3, resume, and it starts at step 3 (not step 1)
- Re-running a completed step does not duplicate data
- Checkpoint data is human-readable for debugging

---

## Lab 7: Human-in-the-Loop Workflow (L3)

**Objective:** Build a workflow with an approval gate that pauses for human decision.

**Deliverables:**
- Workflow that pauses at an approval step
- Notification to approver (Slack message or CLI prompt)
- Timeout with escalation (if no response in N minutes, notify escalation contact)
- Approval/rejection recorded in audit log
- Workflow resumes on approval, terminates on rejection

**Acceptance criteria:**
- Workflow pauses and waits (does not proceed without approval)
- Approval resumes workflow within 5 seconds
- Rejection terminates workflow with audit record
- Timeout triggers escalation notification

---

## Lab 8: Middleware and Telemetry (L4)

**Objective:** Build a middleware pipeline for an agent runtime.

**Deliverables:**
- Auth middleware: validates bearer token before agent execution
- Logging middleware: structured JSON logs for every request/response
- Rate limiting middleware: max N requests per minute per user
- Telemetry dashboard: request count, latency p50/p95/p99, error rate
- Middleware composition: all three run in sequence

**Acceptance criteria:**
- Invalid token returns 401, not agent output
- Rate-limited requests return 429 with retry-after header
- Dashboard shows real metrics from test traffic
- Adding/removing middleware does not require agent code changes

---

## Lab 9: Multi-Agent Coordination (L4-L5)

**Objective:** Build a system where two agents collaborate on a task.

**Deliverables:**
- Supervisor agent that decomposes a task and delegates to specialist agents
- Two specialist agents with different tool sets
- Shared context protocol (how agents pass information)
- Conflict resolution when agents disagree
- Combined output assembly

**Acceptance criteria:**
- Supervisor correctly routes subtasks to the right specialist
- Specialists operate with isolated tool sets (cannot access each other's tools)
- Final output combines contributions from both specialists
- Conflicting outputs are flagged for human review

---

## Lab 10: Odoo Expense Classification Agent (ERP Track)

**Objective:** Build an agent that classifies Odoo expenses into accounting categories.

**Deliverables:**
- Agent connected to Odoo via MCP or XML-RPC
- Reads unclassified `hr.expense` records
- Classifies into predefined `account.account` categories
- Creates draft journal entries for review
- Confidence score per classification

**Acceptance criteria:**
- Correctly classifies 8/10 test expenses
- Low-confidence classifications (<70%) are flagged for human review
- No journal entries are posted without human approval
- All classifications logged with reasoning

---

## Lab Completion Matrix

| Lab | Level | Track | Prerequisite Labs |
|-----|-------|-------|-------------------|
| Lab 1: First Agent | L1-L2 | A | None |
| Lab 2: Tool-Enabled Agent | L2 | A | Lab 1 |
| Lab 3: MCP-Enabled Agent | L2 | A | Lab 1 |
| Lab 4: Stateful Agent | L2 | A | Lab 1 |
| Lab 5: Sequential Workflow | L3 | B | Lab 2 |
| Lab 6: Checkpointed Workflow | L3 | B | Lab 5 |
| Lab 7: Human-in-the-Loop Workflow | L3 | B | Lab 5 |
| Lab 8: Middleware and Telemetry | L4 | D | Lab 2, Lab 4 |
| Lab 9: Multi-Agent Coordination | L4-L5 | C | Lab 2, Lab 5 |
| Lab 10: Odoo Expense Agent | L2+ | E | Lab 3 |

---

## Sandbox Environments

Each lab should run against isolated environments:

| Environment | Purpose | Access |
|-------------|---------|--------|
| Odoo dev database | ERP agent labs | `odoo_dev` via Docker |
| Supabase dev project | State persistence labs | Dev project credentials |
| GitHub non-prod repo | Integration labs | Test repository |
| Local MCP servers | MCP labs | `mcp/servers/` in repo |

---

## References

- `docs/agents/AGENT_EXPERTISE_FRAMEWORK.md` -- capability ladder
- `docs/agents/AGENT_CURRICULUM.md` -- training tracks
- `docs/agents/AGENT_REVIEW_CHECKLIST.md` -- design review gates
