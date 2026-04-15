# agent-platform / orchestration

**Authority:** `docs/architecture/agent-orchestration-model.md`
**Invariant:** CLAUDE.md Cross-Repo Invariant #10a (three-protocol + supervisor-mediated)

---

## What lives here

This directory owns the **runtime** of Pulser's supervisor-mediated orchestration. All state, retries, approvals, dispatch logic, and judge loops live here — **not** in `agents/` (which is definitions-only).

```
orchestration/
├── supervisor/       # pulser_supervisor A2A server (intake → plan → dispatch → judge → synthesize)
├── router/           # planner/router submodule — decides which workers to dispatch
├── dispatcher/       # worker invocation (builds handoff envelopes, enforces allowed_tools)
├── retries/          # retry policies, backoff, circuit breakers, DLQ routing
├── approvals/        # control.approvals integration (L3_dual_review, L4_human_gate blocking)
└── judge_loop/       # judge orchestration (contract, safety, helpfulness)
```

---

## What does NOT live here

| Belongs elsewhere | Correct location |
|---|---|
| Agent personas / system prompts | `agents/<agent_name>/persona.md` |
| Skill implementations | `agents/skills/<skill>/SKILL.md` |
| Judge prompts | `agents/judges/<judge>/` |
| Eval golden sets | `agents/evals/<agent>/golden/` |
| Agent Cards | `agents/<agent_name>/.well-known/agent-card.json` |
| Agent-level MCP tool adapters | Each agent's own repo space or `packages/` if shared |

---

## Runtime shape

Every Pulser agent (supervisor, worker, judge, synthesizer) is a **MAF A2A server** (`github.com/microsoft/agent-framework`, Python, `agent-framework` package). Orchestration logic here assembles MAF workflow graphs from Agent Card registrations.

Local dev runs in devcontainer with Foundry Local backing (`solo mode`).
Production runs on Azure Container Apps with Foundry cloud backing (`team mode`).
See CLAUDE.md #10a for the two-modes contract.

---

## Contracts (must match)

Every dispatch emits:
1. An **agent_request envelope** — `agent-platform/contracts/envelopes/agent_request.yaml`
2. A **handoff contract** — `agent-platform/contracts/handoffs/handoff.yaml`

Every worker/judge returns:
3. An **agent_result envelope** — `agent-platform/contracts/envelopes/agent_result.yaml`

Schema validation is enforced at supervisor dispatch and result ingest.

---

## Hard rules

1. **Workers never initiate calls to workers.** Supervisor mediates.
2. **Every dispatch has a `workflow_id` and `step_id`.**
3. **Every worker output is schema-validated** before the synthesizer sees it.
4. **Tool permissions are per-step**, declared in the handoff envelope.
5. **Workflow state lives here**, not in the workers. Workers are stateless.
6. **Judge loop runs on every high-risk path** (mutation, financial posting, compliance, external publish).

---

## Implementation status

| Component | Status |
|---|---|
| Envelopes + handoff schemas | ✅ Written (`contracts/`) |
| Supervisor runtime | 🟡 Phase 2 deliverable |
| Router / planner | 🟡 Phase 2 deliverable |
| Dispatcher | 🟡 Phase 2 deliverable |
| Judge loop | 🟡 Phase 2 deliverable |
| Approvals integration | 🟡 Phase 2 deliverable (wires to existing control.approvals) |
| Retries + DLQ | 🟡 Phase 2 deliverable |

---

## First caller

The **Pulser Scrum Master ADO extension** is the first end-to-end consumer. See `docs/research/ado-pulser-scrum-extension.md` + `addendum-a2a.md` for design, and Phase 2 build artifacts for the implementation.
