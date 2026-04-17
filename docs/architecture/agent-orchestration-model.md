# Pulser Agent Orchestration Model — Canonical Doctrine

**Status:** Canonical. Supersedes any prior "peer-to-peer agent" framing.
**Rev:** 2026-04-15
**Anchors:** `CLAUDE.md` Cross-Repo Invariant #10a, `ssot/governance/agent-interop-matrix.yaml`, `agent-platform/contracts/envelopes/`.

---

## 0. Blunt rule

> **Agent-to-agent orchestration belongs in `agent-platform/`, not in `agents/`.**
> **Workers never invoke workers directly. The supervisor mediates everything.**
> **`agents/` = definitions (runtime-free). `agent-platform/` = execution.**

Use agent-to-agent as controlled supervisor-mediated task execution. Do not build a free-form agent swarm.

---

## 1. Repo ownership split

| Repo / directory | Owns |
|---|---|
| `agents/` | personas, skills, judges, evals, prompt contracts, registries, Agent Cards |
| `agent-platform/` | orchestration runtime (supervisor, router, dispatcher, retries, approvals, traces), session/thread state, tool execution, workflow state, judge loops, envelopes, handoffs |
| `platform/` | shared contracts and cross-plane state |
| `odoo/addons/ipai/*` | business truth (records, actions, policies grounded in Odoo) |

---

## 2. Canonical agent roles

| Role | Responsibility |
|---|---|
| **Intake / triage** | Normalize request; identify tenant/product/context; attach policies; classify task type. |
| **Planner / router** | Decide which specialist workers are needed; emit a task graph with stop conditions. |
| **Specialist workers** | `pulser_scrum_master`, `tax_guru`, `bank_recon`, `ppm-agent`, `research-agent`, `platform-ops-agent`, etc. Return **structured outputs** to the orchestrator. **Do not call each other.** |
| **Judge / verifier** | Contract conformance, safety/policy, evidence sufficiency. Approve, request retry, or route to human. |
| **Synthesizer / response** | Merge approved outputs; format final artifact; emit response. |

---

## 3. Execution flow (the canonical loop)

```
1. intake          — request received at A2A entry point
2. plan            — planner emits task graph + stop conditions
3. dispatch N workers (parallel where safe)
4. collect structured results
5. judge / verify
6. retry or escalate if needed
7. synthesize
8. persist trace + eval
9. return response
```

**Not allowed:** `Worker A → Worker B → Worker C → Worker A → Worker D …` without supervisor mediation.

---

## 4. Orchestration patterns (pick per use case)

### A. Sequential chain
Steps must happen in order. Example: `research-question → literature search → evidence extraction → summary`.

### B. Fan-out / fan-in
Parallel specialists collected into a synthesis. Example: `planner → {finance, tax, compliance} → judge → synthesizer`.

### C. Judge loop
Output validated before release. Example: `worker → judge → (retry worker | approve)`.

### D. Human gate
Compliance, filing/submission, destructive ops, financial posting, policy-sensitive decisions. Blocks workflow until approved in `control.approvals`.

---

## 5. State model (orchestrator owns, agents do not)

### Workflow states
`queued | running | waiting_on_worker | waiting_on_human | retrying | failed | completed | cancelled`

### Step states
`pending | dispatched | returned | judged | approved | rejected`

Persisted in `agent-platform` workflow store. Workers are stateless — they receive an envelope, return an envelope, nothing carries over.

---

## 6. Contracts (see `agent-platform/contracts/envelopes/`)

Every agent invocation carries an **agent_request envelope**. Every result returns an **agent_result envelope**. Every handoff from supervisor to worker passes a **handoff contract** that scopes allowed tools, timeout, retry policy, and human-approval requirement.

---

## 7. Anti-patterns (rejected at code review)

- Agent-to-agent direct messaging as the main control model
- Shared mutable memory without ownership
- Tool access granted globally to all agents
- Prompts as the only orchestration logic
- Missing per-step schemas
- No judge/review loop on mutating flows
- No tenant/session isolation
- Workers carrying state between invocations
- A worker importing another worker's client SDK

---

## 8. Success criteria

1. No worker agent calls another worker directly without orchestrator mediation.
2. Every agent execution is traceable by `workflow_id` and `step_id`.
3. Every worker returns a structured output envelope.
4. Judge/review loop exists for every high-risk path (mutations, financial posting, compliance, external publishing).
5. Tool permissions are per-agent and per-step (declared in the handoff envelope).
6. Workflow state is owned centrally by `agent-platform`, not by workers.
7. `agents/` repo stays runtime-free (definitions only).

---

## 9. Minimal target artifacts

### In `agent-platform/`
```
agent-platform/
  orchestration/
    supervisor/
    router/
    dispatcher/
    retries/
    approvals/
    judge_loop/
  runtime/
    sessions/
    traces/
    providers/
  contracts/
    envelopes/
      agent_request.yaml
      agent_result.yaml
    handoffs/
      handoff.yaml
    outputs/
    tool_calls/
  services/
    orchestrator-api/
```

### In `agents/`
```
agents/
  personas/
  skills/
  judges/
  evals/
  registries/
    agent-catalog.yaml
    skill-catalog.yaml
  prompts/
  policies/
```

---

## 10. Relationship to the three-protocol model (invariant #10a)

- **A2A** is the transport between any two agents, including client → supervisor and supervisor → worker. See `docs/architecture/three-protocol-model.md`.
- **MCP** is the transport between an agent and its tools.
- **Agent365 SDK** is the surface into M365 (Copilot/Teams/Outlook) — it sits in front of the supervisor for M365-originated traffic only.

Orchestration doctrine does not change which protocol we use — it defines **who is allowed to initiate a call**. Workers are invoke-only. The supervisor initiates.

---

## 11. Pulser Scrum Master worked example

```
ADO extension (user: @PulserScrum /standup)
 → A2A message/send to pulser_supervisor
 → intake: classify (standup), bind tenant (ipai-platform), attach scrum policy
 → plan: dispatch [standup-worker] (single worker for daily standup)
 → dispatch pulser_scrum_master skill=standup via handoff envelope (read-only scopes)
 → judge_contract_conformance + judge_safety + judge_helpfulness
 → synthesize: Adaptive Card JSON for ADO extension
 → persist trace (workflow_id, step_ids, cost, latency, evidence_refs)
 → return
```

Retro path adds: `supervisor detects tax dependency in worker output → dispatches tax_guru as a second step → merges results`. Neither Scrum Master nor Tax Guru knows the other exists.
