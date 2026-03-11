# Agent Design Review Checklist

> Every agent or workflow design review must answer these questions.
> Reviewers: use this as a gate. Incomplete answers block approval.

---

## 1. Primitive Selection

- [ ] **Why not a plain function?** Document why this task requires LLM reasoning or tool use.
- [ ] **Why not a simple workflow?** If using an agent, explain why a deterministic step sequence is insufficient.
- [ ] **Why not a single agent?** If using a workflow or multi-agent system, explain why one agent cannot handle the task.

> If any of these cannot be answered clearly, the design should be simplified.

---

## 2. Tool and MCP Exposure

- [ ] **What tools are exposed to the agent?** List every tool with its capability.
- [ ] **What MCP servers are connected?** List each server and whether it is first-party or third-party.
- [ ] **What is the blast radius of each tool?** Classify as read-only, write (reversible), or write (irreversible).
- [ ] **Are destructive tools gated by confirmation?** Any tool that deletes, modifies shared state, or sends external messages must require explicit approval.

---

## 3. State and Session

- [ ] **What state is stored?** Document session data, persistence layer, and TTL.
- [ ] **Is state scoped correctly?** Per-user, per-conversation, per-workflow-run.
- [ ] **What happens on session expiry?** Graceful degradation, not silent data loss.
- [ ] **Is state serializable and inspectable?** Must be debuggable by a human.

---

## 4. Human-in-the-Loop

- [ ] **Where does human approval happen?** Identify every point where a human must confirm.
- [ ] **What is the timeout and escalation policy?** No approval step should block indefinitely.
- [ ] **Can a human override the agent's decision?** Document override mechanisms.
- [ ] **Is the approval audit trail complete?** Who approved, when, what they saw.

---

## 5. Data and Compliance Boundaries

- [ ] **What data leaves trusted boundaries?** Identify any data sent to external APIs, third-party MCP servers, or LLM providers.
- [ ] **Is PII handled correctly?** PII must not be stored in agent logs or sent to external services without consent.
- [ ] **Are geographic/compliance requirements met?** Data residency, GDPR, local regulations.
- [ ] **Are secrets handled via environment variables?** No hardcoded credentials anywhere.

---

## 6. Observability and Telemetry

- [ ] **What telemetry exists?** List metrics, logs, and traces.
- [ ] **Are structured logs emitted for every tool call?** Timestamp, tool name, input summary, output summary, duration.
- [ ] **Is token usage tracked?** Per-request and per-session token counts.
- [ ] **Are error rates monitored?** Alert thresholds defined for failure rates.
- [ ] **Is there a dashboard?** Link to observability dashboard or state that one is needed.

---

## 7. Failure Modes

- [ ] **What happens when the LLM is unavailable?** Fallback behavior documented.
- [ ] **What happens when a tool fails?** Retry strategy, max attempts, fallback.
- [ ] **What happens when the workflow is interrupted?** Checkpoint and resume strategy.
- [ ] **Is there a kill switch?** Can the agent/workflow be stopped immediately without data corruption.
- [ ] **Are failure modes tested?** Chaos testing or failure injection in labs.

---

## 8. Cost and Performance

- [ ] **What is the expected token cost per invocation?** Estimate for typical and worst-case inputs.
- [ ] **Is the cheapest sufficient model selected?** Do not use a large model when a small one works.
- [ ] **Are there caching opportunities?** Repeated queries, stable tool results.
- [ ] **What is the latency budget?** Maximum acceptable response time documented.
- [ ] **Is there a cost cap?** Maximum spend per user/session/day.

---

## 9. Deployment and CI/CD

- [ ] **How is the agent deployed?** Container, serverless, embedded in application.
- [ ] **Is there a CI pipeline?** Tests run before deployment.
- [ ] **Is there a rollback plan?** Previous version can be restored quickly.
- [ ] **Are configuration changes versioned?** Prompt changes, tool changes tracked in git.
- [ ] **Is there a staging environment?** Agent tested in non-production before production.

---

## 10. Documentation

- [ ] **Is the agent's purpose documented?** One-paragraph description of what it does and why.
- [ ] **Are tool contracts documented?** Input/output schemas for every tool.
- [ ] **Is the operational runbook complete?** How to start, stop, monitor, debug, and escalate.
- [ ] **Is the spec bundle created?** `spec/<feature>/` with constitution, prd, plan, tasks.

---

## Review Outcome

| Outcome | Criteria |
|---------|----------|
| **Approved** | All sections complete, no unresolved blockers |
| **Conditional** | Minor gaps identified, must be resolved before production |
| **Blocked** | Fundamental design issues, must redesign |

**Reviewer signs off with:**
- Name
- Date
- Outcome
- Conditions (if conditional)
- Blocking issues (if blocked)

---

## References

- `docs/agents/AGENT_EXPERTISE_FRAMEWORK.md` -- capability ladder
- `docs/agents/AGENT_CURRICULUM.md` -- training tracks
- `docs/agents/AGENT_LABS.md` -- hands-on exercises
