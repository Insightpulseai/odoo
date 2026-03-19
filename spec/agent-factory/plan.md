# Agent Factory Implementation Plan

> Implementation-ready architecture for the InsightPulse AI Agent Orchestration Platform.
> Companion to: `constitution.md` (doctrine), `prd.md` (requirements), `tasks.md` (checklist).
> Effective: 2026-03-19

---

## 1. Target Architecture

```
                           INSIGHTPULSE AI AGENT FACTORY
 ============================================================================

 ┌─────────────────────────── CONTROL PLANE ───────────────────────────────┐
 │                                                                         │
 │  ┌──────────────┐  ┌──────────────┐  ┌───────────────┐                 │
 │  │  Agent        │  │  Policy      │  │  Stage Gate   │                 │
 │  │  Registry     │  │  Engine      │  │  Engine       │                 │
 │  │              │  │              │  │               │                 │
 │  │  agents.yaml │  │  resolve()   │  │  evaluate()   │                 │
 │  │  passports/  │  │  enforce()   │  │  advance()    │                 │
 │  │  contracts/  │  │  audit()     │  │  demote()     │                 │
 │  └──────┬───────┘  └──────┬───────┘  └───────┬───────┘                 │
 │         │                 │                  │                          │
 │  ┌──────┴─────────────────┴──────────────────┴───────┐                 │
 │  │              Promotion Controller                  │                 │
 │  │  decide() -> evidence + gates -> record            │                 │
 │  └────────────────────────┬──────────────────────────┘                 │
 │                           │                                            │
 │  ┌────────────────────────┴──────────────────────────┐                 │
 │  │              Evaluation Runner                     │                 │
 │  │  load_suite() -> execute() -> score() -> store()   │                 │
 │  └───────────────────────────────────────────────────┘                 │
 │                                                                         │
 └────────────────────────────────┬────────────────────────────────────────┘
                                  │
                    Control->Runtime: routing rules,
                    kill-switch, policy bindings
                                  │
 ┌────────────────────────────────┴────────────────────────────────────────┐
 │                         RUNTIME PLANE                                   │
 │                                                                         │
 │  ┌──────────────────────────────────────────────────────────────┐       │
 │  │                        TASK BUS                               │       │
 │  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │       │
 │  │  │ Ingress  │->│ Router   │->│ Dispatch │->│ Complete │    │       │
 │  │  │ validate │  │ match    │  │ execute  │  │ record   │    │       │
 │  │  │ envelope │  │ policy   │  │ timeout  │  │ evidence │    │       │
 │  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │       │
 │  │                                      │                       │       │
 │  │  ┌──────────┐                       │                       │       │
 │  │  │ Dead     │<-- timeout/error ─────┘                       │       │
 │  │  │ Letter   │                                                │       │
 │  │  └──────────┘                                                │       │
 │  └──────────────────────────────────────────────────────────────┘       │
 │                                                                         │
 │  ┌──────────────┐  ┌──────────────┐  ┌───────────────┐                 │
 │  │  Agent       │  │  Memory      │  │  Tool         │                 │
 │  │  Executor    │  │  Store       │  │  Binder       │                 │
 │  │              │  │              │  │               │                 │
 │  │  spawn()     │  │  read()      │  │  resolve()    │                 │
 │  │  run()       │  │  write()     │  │  invoke()     │                 │
 │  │  kill()      │  │  expire()    │  │  audit()      │                 │
 │  └──────────────┘  └──────────────┘  └───────────────┘                 │
 │                                                                         │
 │  ┌──────────────────────────────────────────────────────────────┐       │
 │  │  Observability Collector                                      │       │
 │  │  traces (OTLP) | metrics (counters) | logs (structured JSON) │       │
 │  │  -> Azure Monitor + Sentry + Evidence Store                   │       │
 │  └──────────────────────────────────────────────────────────────┘       │
 │                                                                         │
 └────────────────────────────────┬────────────────────────────────────────┘
                                  │
                    Runtime->Artifact: execution logs,
                    eval results, promotion records
                                  │
 ┌────────────────────────────────┴────────────────────────────────────────┐
 │                        ARTIFACT PLANE (Git)                             │
 │                                                                         │
 │  agents/                                                                │
 │  ├── registry/agents.yaml          # SSOT: all agents                   │
 │  ├── passports/<id>.yaml           # Identity + lifecycle               │
 │  ├── contracts/<id>.manifest.yaml  # I/O schema + tool bindings         │
 │  ├── evals/<id>/                   # Scenarios + results                │
 │  ├── promotions/<id>/              # Append-only records                │
 │  └── retirements/<id>/             # Sunset + archive records           │
 │                                                                         │
 │  spec/agent-factory/               # Constitution + PRD + Plan          │
 │  ssot/agent-platform/              # Runtime config SSOT                │
 │  docs/architecture/agent-platform/ # Architecture docs                  │
 │  docs/evidence/<date>/             # Execution evidence                 │
 │                                                                         │
 └─────────────────────────────────────────────────────────────────────────┘
```

### Plane Interface Contracts

| Interface | Protocol | Payload | Direction |
|-----------|----------|---------|-----------|
| Control -> Runtime | In-process function call (MVP); HTTP API (scale) | Routing rules, kill commands, policy bindings | Push |
| Control -> Artifact | Git commit (file write) | Promotion records, gate results | Write |
| Runtime -> Control | Event callback (MVP); webhook (scale) | Health signals, task completion events | Push |
| Runtime -> Artifact | Git commit (file write) | Execution logs, evidence bundles | Write |
| Artifact -> Control | File read at startup + watch (MVP); webhook (scale) | Contract schemas, policy manifests | Pull |

---

## 2. Core Services

| # | Service | Location | Purpose | MVP Transport | Scale Transport |
|---|---------|----------|---------|---------------|-----------------|
| 1 | **agent-registry** | `packages/agents/src/registry/` | CRUD for agent passports, contracts, and lifecycle state. Source of truth resolver. | In-process TypeScript | Supabase `ops.agents` |
| 2 | **task-bus** | `packages/taskbus/src/` | Accept, validate, route, dispatch, and complete typed task messages. | In-process EventEmitter | Supabase Realtime + `ops.task_queue` |
| 3 | **stage-gate-engine** | `packages/agents/src/gates/` | Evaluate stage transition criteria. Binary pass/fail. Produce gate result records. | In-process function | CI workflow step |
| 4 | **evaluation-runner** | `packages/agents/src/evals/` | Load eval suites, execute scenarios against agents, score results, persist evidence. | CLI script | GitHub Actions workflow |
| 5 | **promotion-controller** | `packages/agents/src/promotions/` | Orchestrate promotion decisions: collect evidence, run gates, write append-only records. | CLI script | CI workflow + approval gate |
| 6 | **agent-executor** | `packages/agents/src/executor/` | Spawn agent processes, bind tools, enforce timeout, capture output. | In-process | Azure Container Apps Job |
| 7 | **policy-engine** | `packages/agents/src/policies/` | Resolve, merge, and enforce policies at task dispatch time. Most-restrictive-wins. | In-process function | Sidecar (ACA) |
| 8 | **observability-collector** | `packages/agents/src/observability/` | Emit OTLP traces, structured logs, and counter metrics. Route to sinks. | Console + file | Azure Monitor OTLP |
| 9 | **tool-binder** | `packages/agents/src/tools/` | Resolve tool manifests, inject secrets via Key Vault references, invoke with audit. | In-process function | MCP tool server |
| 10 | **memory-store** | `packages/agents/src/memory/` | Read/write agent persistent state. Enforce retention. Externalize to Supabase. | In-memory Map (MVP) | Supabase `ops.agent_memory` |
| 11 | **portfolio-dashboard** | `apps/ops-console/` | KPI dashboard: agent inventory, maturity distribution, task throughput, debt tracking. | Static YAML report | ops-console web UI |
| 12 | **retirement-controller** | `packages/agents/src/retirements/` | Manage sunset timers, drain tasks, archive passports, enforce successor requirements. | CLI script | Scheduled workflow |

---

## 3. Data Model

```
 ┌──────────────┐       ┌──────────────┐       ┌──────────────┐
 │   Agent      │       │   Task       │       │   Policy     │
 │  (Passport)  │       │  (Envelope)  │       │  (Rules)     │
 ├──────────────┤       ├──────────────┤       ├──────────────┤
 │ id: string   │──┐    │ task_id: uuid│       │ id: string   │
 │ version: sem │  │    │ type: dotted │       │ type: enum   │
 │ domain: enum │  │    │ priority: l/n│       │ scope: enum  │
 │ stage: S01-16│  │    │   /h/c       │       │ rules: obj[] │
 │ maturity: L0-│  │    │ payload: obj │       │ precedence:  │
 │   L5         │  │    │ source_id: fk│──┐    │   number     │
 │ contract_ref │  │    │ target_id: fk│──┤    └──────┬───────┘
 │ skills: str[]│  │    │ corr_id: uuid│  │           │
 │ tools: str[] │  │    │ timeout_ms   │  │    ┌──────┴───────┐
 │ policies: fk │──┼──┐ │ idempot_key  │  │    │ PolicyBinding│
 │ kill_switch  │  │  │ │ state: enum  │  │    ├──────────────┤
 │ owners: str[]│  │  │ │ created_at   │  │    │ agent_id: fk │
 │ created_at   │  │  │ │ completed_at │  │    │ policy_id: fk│
 │ updated_at   │  │  │ └──────────────┘  │    │ priority: num│
 └──────┬───────┘  │  │                   │    └──────────────┘
        │          │  │                   │
        │          │  │                   │
 ┌──────┴───────┐  │  │  ┌──────────────┐│   ┌──────────────┐
 │  StageGate   │  │  │  │  Evaluation  ││   │   Metric     │
 ├──────────────┤  │  │  ├──────────────┤│   ├──────────────┤
 │ gate_id: str │  │  │  │ eval_id: uuid││   │ agent_id: fk │
 │ from_stage   │  │  │  │ agent_id: fk │┘   │ metric: str  │
 │ to_stage     │  │  │  │ suite_ref:str│    │ value: float │
 │ criteria: obj│  │  │  │ scenarios:[] │    │ timestamp    │
 │ evidence_req │  │  │  │ results: obj │    │ labels: obj  │
 │ automation   │  │  │  │ score: float │    └──────────────┘
 │ result: p/f  │  │  │  │ judge_id: fk │
 │ evaluated_at │  │  │  │ created_at   │
 └──────────────┘  │  │  └──────────────┘
                   │  │
 ┌─────────────────┘  │  ┌──────────────┐
 │                    │  │  Promotion   │
 │  ┌──────────────┐  │  ├──────────────┤
 │  │  Contract    │  │  │ agent_id: fk │
 │  ├──────────────┤  │  │ from_level   │
 │  │ agent_id: fk │  │  │ to_level     │
 │  │ version: sem │  │  │ type: p/d    │
 │  │ task_types[] │  │  │ evidence:[]  │
 │  │ inputs: json │  │  │ gate_results │
 │  │ outputs: json│  │  │ approver: obj│
 │  │ tools: refs[]│  │  │ reason: str  │
 │  │ policies: fk │  │  │ timestamp    │
 │  └──────────────┘  │  └──────────────┘
 │                    │       ^
 └────────────────────┘       │
                              │ append-only
                              │ (immutable once written)
```

### Entity Details

| Entity | Storage (MVP) | Storage (Scale) | Mutability |
|--------|---------------|-----------------|------------|
| Agent (Passport) | `agents/passports/<id>.yaml` | Same + Supabase `ops.agents` cache | Mutable (versioned) |
| Task (Envelope) | In-memory queue | Supabase `ops.task_queue` | State machine transitions only |
| StageGate | `agents/foundry/gates/<from>-<to>.yaml` | Same (static definitions) | Immutable per version |
| Evaluation | `agents/evals/<id>/results/<run>.json` | Same + `ops.eval_results` | Append-only |
| Promotion | `agents/promotions/<id>/<ts>.yaml` | Same + `ops.promotions` | Append-only (immutable) |
| Policy | `agents/foundry/policies/*.policy.yaml` | Same (static definitions) | Mutable (versioned) |
| Metric | Console output (MVP) | `ops.agent_metrics` (time series) | Append-only |
| Contract | `agents/foundry/agents/*.manifest.yaml` | Same | Mutable (versioned) |

### Task State Machine

```
  ┌──────────┐
  │ PENDING  │ (created, awaiting routing)
  └────┬─────┘
       │ route()
  ┌────┴─────┐
  │ ROUTED   │ (agent matched, awaiting dispatch)
  └────┬─────┘
       │ dispatch()
  ┌────┴─────┐
  │ RUNNING  │ (agent executing)
  └────┬─────┘
       │
  ┌────┴──────────────────────┐
  │            │               │
  ▼            ▼               ▼
┌──────┐  ┌────────┐   ┌──────────┐
│DONE  │  │FAILED  │   │TIMED_OUT │
└──────┘  └───┬────┘   └────┬─────┘
              │              │
              └──────┬───────┘
                     ▼
              ┌──────────┐
              │DEAD_LETTER│ (after max retries)
              └──────────┘
```

---

## 4. Task Bus Architecture

### Queue/Topic Model

**MVP (Phase 1)**: In-process `EventEmitter` with typed channels.

```typescript
// packages/taskbus/src/bus.ts
interface TaskBus {
  submit(envelope: TaskEnvelope): Promise<TaskReceipt>;
  subscribe(taskType: string, handler: TaskHandler): Unsubscribe;
  status(taskId: string): TaskState;
  drain(agentId: string): Promise<void>;
  kill(agentId: string): Promise<void>;
}
```

**Scale (Phase 6+)**: Supabase Realtime channels + `ops.task_queue` table for persistence.

```
                    ┌────────────────────────────────────┐
 submit() ────────> │         ops.task_queue              │
                    │  (PostgreSQL + Supabase Realtime)   │
                    │                                      │
                    │  INSERT -> pg_notify -> Realtime     │
                    │  channel: task.<domain>.<action>     │
                    └──────────────┬─────────────────────┘
                                   │
                    ┌──────────────┴─────────────────────┐
                    │          Router                      │
                    │  1. Parse task type                  │
                    │  2. Query registry for qualified     │
                    │     agents (maturity >= L3 for prod) │
                    │  3. Apply policy constraints         │
                    │  4. Select highest-maturity agent    │
                    │  5. Dispatch                         │
                    └──────────────┬─────────────────────┘
                                   │
                    ┌──────────────┴─────────────────────┐
                    │          Executor                    │
                    │  1. Bind tools per contract          │
                    │  2. Inject memory context            │
                    │  3. Start timeout timer (600s max)   │
                    │  4. Execute agent                    │
                    │  5. Capture output + telemetry       │
                    │  6. Write completion record          │
                    └─────────────────────────────────────┘
```

### Task Envelope Lifecycle

```
1. CREATED    - Envelope validated against ipai.task.v1 schema
2. ACCEPTED   - Idempotency key checked (dedup)
3. ROUTED     - Agent matched by task type + maturity + policy
4. DISPATCHED - Executor started, timeout clock running
5. RUNNING    - Agent processing (telemetry emitting)
6. COMPLETED  - Success: output stored, metrics updated
   FAILED     - Error: error stored, retry count incremented
   TIMED_OUT  - Timeout: killed, retry or dead-letter
7. ARCHIVED   - After retention period, moved to cold storage
```

### Routing Algorithm

```python
def route(task: TaskEnvelope) -> Agent:
    # 1. Find agents that declare this task type
    candidates = registry.find_by_task_type(task.type)

    # 2. Filter by lifecycle stage (must be >= S08 for prod tasks)
    candidates = [a for a in candidates if a.stage >= required_stage(task)]

    # 3. Filter by policy (agent must satisfy all applicable policies)
    candidates = [a for a in candidates if policy_engine.allows(a, task)]

    # 4. Filter by kill switch (exclude killed agents)
    candidates = [a for a in candidates if not a.kill_switch.active]

    # 5. Sort by maturity (highest first), then registry priority
    candidates.sort(key=lambda a: (a.maturity, a.priority), reverse=True)

    if not candidates:
        escalate_to_human(task)
        raise UnroutableTaskError(task.task_id)

    return candidates[0]
```

### Dead Letter Handling

| Condition | Max Retries | Retry Delay | Dead Letter Action |
|-----------|-------------|-------------|-------------------|
| Agent error (non-fatal) | 3 | Exponential (1s, 4s, 16s) | Log + Slack notification |
| Agent timeout | 1 | None (immediate re-route) | Log + human escalation |
| No qualified agent | 0 | N/A | Immediate escalation |
| Policy violation | 0 | N/A | Reject + audit record |
| Agent killed mid-task | 0 | N/A | Re-route to next candidate |

### Correlation and Tracing

Every task carries:
- `task_id` (UUID): unique per task instance
- `correlation_id` (UUID): groups related tasks in a workflow
- `parent_task_id` (UUID, optional): links subtasks to parent
- `trace_id` (OTLP): distributed tracing ID propagated to all spans

Trace attributes on every span:
```
agent.id, task.id, task.type, correlation.id, maturity.level, stage
```

---

## 5. Stage Gate Design

### Gate Matrix (S01-S16)

| Stage | Name | Entry Criteria | Exit Criteria | Required Artifacts | Automation |
|-------|------|----------------|---------------|-------------------|------------|
| **S01** | intake | Blueprint submitted | Passport created, owner assigned | `passports/<id>.yaml` | Full auto |
| **S02** | design | Passport exists | Contract drafted, I/O schemas defined, task types declared | `contracts/<id>.manifest.yaml` | Full auto (schema validation) |
| **S03** | build | Contract validates | Implementation exists, linter passes, type-checks clean | Agent source code, skill bindings | Full auto (CI) |
| **S04** | unit-test | Build passes | Unit eval scenarios exist and pass (>=80% pass rate) | `evals/<id>/scenarios/*.yaml`, `evals/<id>/results/<run>.json` | Full auto (CI) |
| **S05** | integration-test | Unit tests pass | Cross-agent and tool-binding tests pass | `evals/<id>/integration/*.yaml` | Full auto (CI) |
| **S06** | eval-sandbox | Integration tests pass | Full eval suite passes in isolated sandbox | `evals/<id>/results/<run>.json` with sandbox flag | Full auto (eval runner) |
| **S07** | judge-review | Sandbox evals pass | Judge agent review passes, security review complete | `evals/<id>/judge-reviews/<run>.json` | Semi-auto (judge agent + human security sign-off for L3+) |
| **S08** | canary | Judge review passes | Deployed to canary lane, receiving shadow/limited traffic | Deployment manifest, canary metrics baseline | Semi-auto (deploy pipeline + human verification) |
| **S09** | staging | Canary metrics within thresholds for 24h | Full staging deployment, pre-prod validation passes | Staging deployment evidence, load test results | Semi-auto |
| **S10** | production | Staging validation passes, L4 promotion approved | Live production deployment, full traffic, observability active | `promotions/<id>/<ts>-L4.yaml`, production deployment evidence | Semi-auto (promotion controller + human approval) |
| **S11** | scaling | Production stable for 7 days | Performance optimization complete, horizontal scaling validated | Performance benchmarks, scaling config | Manual trigger |
| **S12** | hardening | Scaling validated | Security hardening complete, edge cases covered, policies tightened | Security audit record, updated policies | Manual trigger |
| **S13** | mature | Hardening complete, 30-day production track record, zero critical incidents | Baseline for domain, L5 promotion approved | `promotions/<id>/<ts>-L5.yaml` | Semi-auto |
| **S14** | deprecation-notice | Successor at L2+, retirement approved | 30-day sunset clock started, consumers notified | `retirements/<id>/deprecation-notice.yaml` | Full auto (timer) |
| **S15** | sunset | 30 days elapsed since S14 | Task bus stops routing, in-flight tasks drained | Task drain evidence | Full auto (task bus config) |
| **S16** | retired | All tasks drained | Passport archived, execution permanently disabled | `retirements/<id>/retirement-record.yaml` | Full auto |

### Gate Evaluation Schema

```yaml
schema: ipai.gate-result.v1
gate_id: "S04-to-S05"
agent_id: "<kebab-case>"
evaluated_at: "<ISO8601>"
result: "pass"  # or "fail"
criteria:
  - name: "unit_eval_pass_rate"
    threshold: 0.8
    actual: 0.95
    result: "pass"
  - name: "type_check_clean"
    threshold: 0         # zero errors
    actual: 0
    result: "pass"
evidence_refs:
  - "agents/evals/<id>/results/<run>.json"
evaluator: "ci-pipeline"  # or "judge-<id>" or "human"
```

---

## 6. Maturity Model Integration

### Level-to-Stage Mapping

```
 L0 concept     ──── S01 intake ──── S02 design
                      │
 L1 prototype   ──── S03 build ──── S04 unit-test ──── S05 integration-test
                      │
 L2 evaluated   ──── S06 eval-sandbox ──── S07 judge-review
                      │
 L3 deployed    ──── S08 canary ──── S09 staging
                      │
 L4 production  ──── S10 production ──── S11 scaling ──── S12 hardening
                      │
 L5 mature      ──── S13 mature
                      │
 (retirement)   ──── S14 deprecation ──── S15 sunset ──── S16 retired
```

### Evidence Requirements by Level

| Promotion | Gate | Required Evidence | Evaluator |
|-----------|------|-------------------|-----------|
| L0 -> L1 | S02->S03 | Contract schema validates. Blueprint fields complete. | CI (schema validator) |
| L1 -> L2 | S05->S06 | Unit + integration evals pass (>=80%). Sandbox execution log. | CI (eval runner) |
| L2 -> L3 | S07->S08 | Full eval suite passes. Judge review record. Security review. | Judge agent + human |
| L3 -> L4 | S09->S10 | Canary metrics within thresholds. No critical incidents (48h min). | Promotion controller |
| L4 -> L5 | S12->S13 | 30-day production track record. Zero critical incidents. Coverage >= 80% scenarios. | Promotion controller + human |

### Permission Matrix

| Capability | L0 | L1 | L2 | L3 | L4 | L5 |
|------------|----|----|----|----|----|----|
| Receive tasks | - | sandbox only | sandbox only | canary/staging | production | production |
| Access real data | - | - | eval data | staging data | production data | production data |
| Invoke tools | - | mock tools | mock tools | real tools (bounded) | real tools | real tools |
| Write to systems | - | - | - | staging writes | production writes | production writes |
| Serve as baseline | - | - | - | - | - | yes |
| Kill switch required | - | - | - | yes | yes | yes |
| Observability required | - | - | recommended | required | required | required |

---

## 7. Orchestration Architecture

### Orchestrator Agent Design

The orchestrator is itself an agent (`orchestrator`, domain: `platform`) that routes complex multi-step work through the task bus. It does not execute domain work directly.

```
                     ┌─────────────────────┐
                     │    Human / CLI       │
                     │    (task source)     │
                     └──────────┬──────────┘
                                │
                     ┌──────────┴──────────┐
                     │   ORCHESTRATOR      │
                     │   agent             │
                     │                     │
                     │ - Decompose request │
                     │ - Plan task graph   │
                     │ - Submit to bus     │
                     │ - Monitor progress  │
                     │ - Aggregate results │
                     │ - Escalate failures │
                     └──────────┬──────────┘
                                │
            ┌───────────────────┼───────────────────┐
            │                   │                   │
     ┌──────┴──────┐    ┌──────┴──────┐    ┌──────┴──────┐
     │ task.odoo.* │    │ task.data.* │    │ task.eval.* │
     │             │    │             │    │             │
     │ ODOO-SAGE   │    │ DATA-FORGE  │    │ JUDGE       │
     └──────┬──────┘    └──────┬──────┘    └──────┬──────┘
            │                   │                   │
            └───────────────────┼───────────────────┘
                                │
                     ┌──────────┴──────────┐
                     │   ORCHESTRATOR      │
                     │   (collect results) │
                     └─────────────────────┘
```

### Specialist Routing

The orchestrator decomposes work into typed tasks. The task bus routes each task to the best-qualified specialist:

```python
# Orchestrator decomposition example
def handle_deploy_module(request):
    tasks = [
        TaskEnvelope(type="task.odoo.lint-module", payload={...}),
        TaskEnvelope(type="task.devops.build-image", payload={...},
                     depends_on=["task.odoo.lint-module"]),
        TaskEnvelope(type="task.devops.deploy-aca", payload={...},
                     depends_on=["task.devops.build-image"]),
        TaskEnvelope(type="task.eval.smoke-test", payload={...},
                     depends_on=["task.devops.deploy-aca"]),
    ]
    return submit_task_graph(tasks, correlation_id=uuid4())
```

### Judge Integration

Judge agents are structurally independent (P9: maker-judge separation):

| Aspect | Maker Agent | Judge Agent |
|--------|-------------|-------------|
| Task types | Domain-specific (`task.odoo.*`, `task.data.*`) | Evaluation (`task.eval.judge-review`) |
| Output | Work artifacts (code, config, reports) | Evaluation records (scores, verdicts, evidence) |
| Invocation | Via task bus (normal routing) | Via task bus (eval runner submits judge tasks) |
| Independence | Cannot self-evaluate | Cannot produce domain work |
| Registry | `agents/registry/agents.yaml` (maker section) | `agents/registry/agents.yaml` (judge section) |

### Retry and Fallback

```
Task submitted
    │
    ├── Agent succeeds -> DONE
    │
    ├── Agent fails (non-fatal)
    │   ├── Retry 1 (same agent, 1s delay)
    │   ├── Retry 2 (same agent, 4s delay)
    │   ├── Retry 3 (same agent, 16s delay)
    │   └── Fallback: route to next-best agent
    │       ├── Fallback agent succeeds -> DONE
    │       └── Fallback agent fails -> DEAD_LETTER + human escalation
    │
    ├── Agent times out
    │   └── Kill + re-route to next-best agent (1 attempt)
    │       ├── Succeeds -> DONE
    │       └── Fails -> DEAD_LETTER + human escalation
    │
    └── No agent qualifies -> immediate human escalation
```

### Human Escalation

Escalation triggers:
1. Dead-lettered task (all retries exhausted)
2. Unroutable task (no qualified agent)
3. Policy override required (destructive operation)
4. L3+ promotion decision (human approval gate)

Escalation channels:
- **Slack**: `#agent-factory-alerts` (primary)
- **ops.escalations** table (Supabase, audit trail)
- **Email**: `ops@insightpulseai.com` (fallback)

### Parallel vs Sequential Execution

Task graphs support both via dependency declarations:

```yaml
# Parallel: no depends_on between tasks
tasks:
  - id: lint
    type: task.odoo.lint-module
  - id: typecheck
    type: task.odoo.typecheck-module
  # lint and typecheck run in parallel

# Sequential: explicit depends_on
tasks:
  - id: build
    type: task.devops.build-image
    depends_on: [lint, typecheck]
  # build waits for both lint and typecheck
```

The orchestrator tracks a DAG of task dependencies and dispatches tasks as their dependencies complete.

---

## 8. Rollout Phases

### Phase 0: Foundations

**Scope**: Type definitions, schema contracts, repo structure scaffolding.

**Dependencies**: None (greenfield).

**Deliverables**:
| # | Deliverable | Location |
|---|-------------|----------|
| 0.1 | TypeScript type definitions for all data model entities | `packages/agents/src/types/` |
| 0.2 | JSON Schema / Zod schemas for passport, contract, task envelope, gate result, promotion record, evaluation result | `packages/agents/src/schemas/` |
| 0.3 | Directory scaffold for agents/, packages/agents/, packages/taskbus/ | Repo root |
| 0.4 | package.json + tsconfig for packages/agents and packages/taskbus | Package roots |
| 0.5 | Schema validation CLI: `pnpm agents validate <file>` | `packages/agents/src/cli/validate.ts` |

**Validation**:
- `pnpm -s typecheck` passes for both packages
- Schema validation CLI validates existing agent manifests
- All type exports compile without errors

---

### Phase 1: Task Bus

**Scope**: In-process task bus with typed envelopes, routing, state machine, dead letter.

**Dependencies**: Phase 0 (types, schemas).

**Deliverables**:
| # | Deliverable | Location |
|---|-------------|----------|
| 1.1 | TaskBus class with submit/subscribe/status/drain/kill | `packages/taskbus/src/bus.ts` |
| 1.2 | TaskRouter with type-based matching and maturity ranking | `packages/taskbus/src/router.ts` |
| 1.3 | TaskStateMachine (PENDING->ROUTED->RUNNING->DONE/FAILED/TIMED_OUT->DEAD_LETTER) | `packages/taskbus/src/state-machine.ts` |
| 1.4 | Dead letter queue with configurable retry policy | `packages/taskbus/src/dead-letter.ts` |
| 1.5 | Correlation ID propagation and parent-child task linking | `packages/taskbus/src/correlation.ts` |
| 1.6 | Unit tests (>=80% coverage) | `packages/taskbus/src/__tests__/` |

**Validation**:
- Submit a task, verify it routes to correct handler
- Submit a task with no handler, verify dead-letter
- Submit dependent tasks, verify sequential execution
- Kill an agent mid-task, verify re-route
- `pnpm -s test -- packages/taskbus` passes

---

### Phase 2: Registry + Passports

**Scope**: Agent registry service, passport CRUD, contract validation.

**Dependencies**: Phase 0 (schemas), Phase 1 (task bus for inter-service).

**Deliverables**:
| # | Deliverable | Location |
|---|-------------|----------|
| 2.1 | AgentRegistry class: register, get, list, update lifecycle state | `packages/agents/src/registry/registry.ts` |
| 2.2 | PassportManager: create, read, update (never delete) | `packages/agents/src/registry/passport.ts` |
| 2.3 | ContractValidator: validate manifest against schema, check tool bindings | `packages/agents/src/registry/contract.ts` |
| 2.4 | Migration script: generate passports for 6 existing registered agents | `scripts/agents/migrate-passports.ts` |
| 2.5 | CI workflow: `agent-registry-validate.yml` | `.github/workflows/` |
| 2.6 | CLI: `pnpm agents register <blueprint>`, `pnpm agents passport <id>` | `packages/agents/src/cli/` |

**Validation**:
- Register a new agent from blueprint, verify passport created
- Validate all 6 existing agents produce valid passports
- Attempt duplicate ID registration, verify rejection
- CI workflow runs on PR and catches invalid passports

---

### Phase 3: Assembly Line (Stage Gates)

**Scope**: 16-stage lifecycle, gate engine, stage transition enforcement.

**Dependencies**: Phase 2 (registry, passports).

**Deliverables**:
| # | Deliverable | Location |
|---|-------------|----------|
| 3.1 | StageGateEngine: evaluate criteria, produce gate results | `packages/agents/src/gates/engine.ts` |
| 3.2 | Gate definitions for all 16 stage transitions | `agents/foundry/gates/` |
| 3.3 | Stage transition enforcer: validates prerequisites before advancing | `packages/agents/src/gates/enforcer.ts` |
| 3.4 | Demotion handler: creates demotion records, enforces backward movement rules | `packages/agents/src/gates/demotion.ts` |
| 3.5 | CLI: `pnpm agents advance <id> <to-stage>`, `pnpm agents gate-check <id>` | `packages/agents/src/cli/` |
| 3.6 | CI workflow: `agent-stage-gate.yml` (runs on promotion PRs) | `.github/workflows/` |

**Validation**:
- Advance an agent S01->S02 with valid passport, verify success
- Attempt S01->S03 skip without S02 artifacts, verify rejection
- Demote an agent, verify demotion record created and promotion record intact
- Gate check produces machine-readable pass/fail output

---

### Phase 4: Evaluations + Judge Agents

**Scope**: Evaluation runner, scenario schemas, judge agent integration.

**Dependencies**: Phase 1 (task bus), Phase 2 (registry), Phase 3 (gates).

**Deliverables**:
| # | Deliverable | Location |
|---|-------------|----------|
| 4.1 | EvaluationRunner: load suite, execute scenarios, score, persist | `packages/agents/src/evals/runner.ts` |
| 4.2 | Evaluation scenario schema (inputs, expected outputs, scoring rubric) | `packages/agents/src/schemas/eval-scenario.ts` |
| 4.3 | Judge agent contract and passport (first judge agent) | `agents/passports/eval-judge.yaml`, `agents/foundry/agents/eval-judge.manifest.yaml` |
| 4.4 | Judge task type: `task.eval.judge-review` | Task bus registration |
| 4.5 | Maker-judge routing exclusion rule | `packages/agents/src/evals/judge-routing.ts` |
| 4.6 | CLI: `pnpm agents eval <id>`, `pnpm agents eval --judge <id>` | `packages/agents/src/cli/` |
| 4.7 | Sample eval suite for odoo-sage | `agents/evals/odoo-sage/scenarios/` |

**Validation**:
- Run eval suite for odoo-sage, verify results persisted
- Submit judge review task, verify maker agent excluded from judge pool
- Verify eval results are structured JSON (machine-verifiable)
- Gate S06->S07 requires eval results to exist

---

### Phase 5: Promotion/Release Controls

**Scope**: Promotion controller, append-only records, release lanes.

**Dependencies**: Phase 3 (gates), Phase 4 (evaluations).

**Deliverables**:
| # | Deliverable | Location |
|---|-------------|----------|
| 5.1 | PromotionController: collect evidence, run gates, write records | `packages/agents/src/promotions/controller.ts` |
| 5.2 | Append-only record writer with SHA-256 evidence hashing | `packages/agents/src/promotions/record.ts` |
| 5.3 | Release lane definitions: canary, staging, production, hotfix | `ssot/agent-platform/release-lanes.yaml` |
| 5.4 | Human approval gate (Slack notification + CLI confirm) | `packages/agents/src/promotions/approval.ts` |
| 5.5 | CI workflow: `agent-promotion.yml` (triggered by promotion PRs) | `.github/workflows/` |
| 5.6 | CLI: `pnpm agents promote <id> <to-level>`, `pnpm agents demote <id> <to-level>` | `packages/agents/src/cli/` |

**Validation**:
- Promote agent L0->L1 with valid evidence, verify record written
- Attempt L1->L2 without eval results, verify rejection
- Verify promotion record file is never overwritten (append-only)
- Verify SHA-256 hash of evidence matches file content

---

### Phase 6: Runtime Observability

**Scope**: Structured telemetry, metrics collection, alerting.

**Dependencies**: Phase 1 (task bus), Phase 2 (registry).

**Deliverables**:
| # | Deliverable | Location |
|---|-------------|----------|
| 6.1 | ObservabilityCollector: trace, metric, log emission | `packages/agents/src/observability/collector.ts` |
| 6.2 | OTLP span creation with required trace attributes | `packages/agents/src/observability/tracing.ts` |
| 6.3 | Counter metrics: task.count, task.duration, task.error_rate per agent | `packages/agents/src/observability/metrics.ts` |
| 6.4 | Structured JSON logger | `packages/agents/src/observability/logger.ts` |
| 6.5 | Health probe endpoint (heartbeat + readiness) | `packages/agents/src/observability/health.ts` |
| 6.6 | Azure Monitor sink configuration | `ssot/agent-platform/observability.yaml` |

**Validation**:
- Execute a task, verify trace span emitted with all required attributes
- Verify metrics increment correctly (count, duration, error_rate)
- Health probe returns 200 when agent is healthy, 503 when killed
- Structured logs parse as valid JSON

---

### Phase 7: Portfolio Governance

**Scope**: KPI dashboard, agent inventory reports, technical debt tracking.

**Dependencies**: Phase 2 (registry), Phase 6 (observability).

**Deliverables**:
| # | Deliverable | Location |
|---|-------------|----------|
| 7.1 | Portfolio report generator: agent count by maturity, domain, stage | `packages/agents/src/portfolio/report.ts` |
| 7.2 | KPI definitions: mean time to promote, eval pass rate, task throughput | `ssot/agent-platform/kpis.yaml` |
| 7.3 | Technical debt tracker: agents past grace period, missing evals, stale passports | `packages/agents/src/portfolio/debt.ts` |
| 7.4 | CLI: `pnpm agents portfolio`, `pnpm agents debt` | `packages/agents/src/cli/` |
| 7.5 | ops-console integration (dashboard page) | `apps/ops-console/` |

**Validation**:
- Portfolio report generates correct counts for 6 existing agents
- Debt tracker identifies agents missing passports/evals
- KPI calculations produce non-zero values for active agents

---

### Phase 8: Retirement Workflows

**Scope**: Sunset timers, task draining, passport archival.

**Dependencies**: Phase 1 (task bus), Phase 2 (registry), Phase 3 (gates).

**Deliverables**:
| # | Deliverable | Location |
|---|-------------|----------|
| 8.1 | RetirementController: deprecate, sunset, retire lifecycle | `packages/agents/src/retirements/controller.ts` |
| 8.2 | Sunset timer: 30-day countdown from S14 entry | `packages/agents/src/retirements/timer.ts` |
| 8.3 | Task drain: stop routing new tasks, wait for in-flight completion | `packages/agents/src/retirements/drain.ts` |
| 8.4 | Passport archival: move to `agents/passports/retired/` | `packages/agents/src/retirements/archive.ts` |
| 8.5 | Successor validation: require successor at L2+ before S15 | `packages/agents/src/retirements/successor.ts` |
| 8.6 | CLI: `pnpm agents deprecate <id>`, `pnpm agents retire <id>` | `packages/agents/src/cli/` |

**Validation**:
- Deprecate an agent, verify S14 record and 30-day timer
- Attempt retirement without successor, verify rejection
- Retire an agent, verify passport moved to `retired/` and task bus stops routing

---

## 9. Change Classification

| Change Type | Risk | Blast Radius | Required Validations | Stage-Gate Impact | Release Rules | Rollback Rules |
|-------------|------|--------------|---------------------|------------------|---------------|----------------|
| **Prompt** (system instruction edit) | Medium | Single agent | Eval suite re-run, judge review if L3+ | Re-run S04-S06 evals | Canary 24h, then staging | Revert prompt, re-deploy |
| **Tool** (add/remove/modify tool binding) | High | Agent + downstream systems | Contract re-validation, integration tests, security review | Re-run S05 (integration), S07 (security) | Staging validation required | Remove tool binding, re-deploy |
| **Policy** (add/modify policy rule) | High | All agents in policy scope | Policy conflict check, affected agent re-evaluation | No stage regression; policy takes effect immediately | Apply to staging first, 24h soak | Revert policy file, re-apply |
| **Workflow** (task graph modification) | Medium | Orchestrator + affected agents | Workflow simulation, dependency validation | No stage impact (workflow is orchestrator config) | Deploy orchestrator update to canary | Revert workflow definition |
| **Model** (LLM backend change) | Critical | All agents using that model | Full eval re-run for all affected agents, latency benchmarks | Re-run S06 (eval sandbox) for all affected | Canary with shadow traffic, 48h soak | Revert model routing policy |
| **Skill** (add/modify agent skill) | Medium | Agents binding that skill | Skill unit tests, affected agent eval re-run | Re-run S04 (unit test) for skill, S05 for bindings | Normal promotion flow | Unbind skill, re-deploy agent |
| **Memory** (schema change to agent memory) | High | Agent + memory-dependent workflows | Migration script, backward compatibility check | No stage impact if backward compatible; S05 re-run if breaking | Migration script in staging first | Reverse migration + re-deploy |
| **Orchestration** (routing/dispatch logic) | Critical | All agents (task bus is backbone) | Full regression: submit sample tasks for every task type | No stage impact on individual agents; task bus itself is infra | Blue-green deployment, instant rollback | Revert task bus code, restart |
| **Contract** (I/O schema change) | High | Agent + all consumers | Schema backward compatibility, consumer re-validation | Re-run S02 (design) validation | Breaking changes require major version bump | Revert contract, re-deploy |
| **Gate** (modify stage criteria) | Medium | All agents at affected stage | Gate definition review, retroactive check on in-stage agents | N/A (gates are meta-config) | Apply immediately; no deployment | Revert gate definition |
| **Registry** (add/remove agent) | Low | Single agent | Passport validation, naming lint | New agent starts at S01 | Commit to main | Soft-delete (set to S16) |
| **Infrastructure** (runtime env change) | Critical | All agents in affected environment | Full smoke test, health probes, rollback plan documented | No stage impact on agents | Blue-green with instant rollback | Revert infra change |

---

## 10. Repo Structure

```
/Users/tbwa/Documents/GitHub/Insightpulseai/
│
├── spec/agent-factory/
│   ├── constitution.md              # [EXISTS] Platform doctrine
│   ├── prd.md                       # [CREATE] Product requirements
│   ├── plan.md                      # [THIS FILE] Implementation plan
│   └── tasks.md                     # [EXISTS] Task checklist
│
├── docs/architecture/agent-platform/
│   ├── overview.md                  # Architecture overview
│   ├── data-model.md               # Entity relationship details
│   ├── task-bus.md                  # Task bus deep dive
│   └── observability.md            # Telemetry architecture
│
├── ssot/agent-platform/
│   ├── release-lanes.yaml           # Canary/staging/prod/hotfix config
│   ├── kpis.yaml                    # Portfolio KPI definitions
│   └── observability.yaml           # Telemetry sink config
│
├── agents/
│   ├── registry/
│   │   └── agents.yaml              # [EXISTS] Agent registry SSOT
│   ├── passports/
│   │   ├── odoo-sage.yaml           # Per-agent identity docs
│   │   ├── devops-prime.yaml
│   │   ├── data-forge.yaml
│   │   ├── ui-craft.yaml
│   │   ├── supabase-ssot.yaml
│   │   ├── automation-specialist.yaml
│   │   └── retired/                 # Archived passports
│   ├── contracts/                   # Alias -> foundry/agents/ manifests
│   ├── evals/
│   │   ├── odoo-sage/
│   │   │   ├── scenarios/           # Eval scenario definitions
│   │   │   ├── integration/         # Integration test scenarios
│   │   │   ├── results/             # Run results (append-only)
│   │   │   └── judge-reviews/       # Judge evaluation records
│   │   └── <agent-id>/
│   ├── promotions/
│   │   └── <agent-id>/
│   │       └── <timestamp>-<level>.yaml  # Append-only records
│   ├── retirements/
│   │   └── <agent-id>/
│   │       ├── deprecation-notice.yaml
│   │       └── retirement-record.yaml
│   ├── foundry/
│   │   ├── agents/                  # [EXISTS] Agent manifests
│   │   ├── tools/                   # [EXISTS] Tool manifests
│   │   ├── policies/               # [EXISTS] Policy definitions
│   │   ├── gates/                   # Stage gate definitions
│   │   └── schemas/                 # [EXISTS] Foundry schemas
│   ├── skills/                      # [EXISTS] Reusable skill modules
│   └── personas/                    # [EXISTS] Agent persona definitions
│
├── packages/
│   ├── agents/                      # [EXISTS - expand]
│   │   ├── package.json
│   │   ├── tsconfig.json
│   │   └── src/
│   │       ├── types/               # Entity type definitions
│   │       ├── schemas/             # Zod validation schemas
│   │       ├── registry/            # Agent registry service
│   │       ├── gates/               # Stage gate engine
│   │       ├── evals/               # Evaluation runner
│   │       ├── promotions/          # Promotion controller
│   │       ├── policies/            # Policy engine
│   │       ├── executor/            # Agent executor
│   │       ├── tools/               # Tool binder
│   │       ├── memory/              # Memory store
│   │       ├── observability/       # Telemetry collector
│   │       ├── portfolio/           # Portfolio governance
│   │       ├── retirements/         # Retirement controller
│   │       ├── cli/                 # CLI commands
│   │       └── __tests__/           # Unit tests
│   │
│   └── taskbus/                     # [EXISTS - expand]
│       ├── package.json
│       ├── tsconfig.json
│       └── src/
│           ├── bus.ts               # Core task bus
│           ├── router.ts            # Task routing
│           ├── state-machine.ts     # Task state transitions
│           ├── dead-letter.ts       # Dead letter handling
│           ├── correlation.ts       # Correlation/tracing
│           └── __tests__/           # Unit tests
│
├── platform/services/               # Future: standalone services
│   ├── agent-factory/               # Control plane API (post-MVP)
│   └── task-bus/                    # Task bus API (post-MVP)
│
└── automations/
    └── task-bus/                     # n8n workflows for task bus events
        ├── escalation.json          # Human escalation workflow
        └── metrics.json             # Metrics collection workflow
```

---

## 11. Dependencies

### Internal (Existing Infrastructure)

| Dependency | Location | Used By | Status |
|------------|----------|---------|--------|
| Agent registry YAML | `agents/registry/agents.yaml` | Registry service (Phase 2) | Exists, needs `current_stage` + `maturity_level` fields |
| Agent manifests | `agents/foundry/agents/*.manifest.yaml` | Contract validator (Phase 2) | 4 manifests exist |
| Policy definitions | `agents/foundry/policies/*.policy.yaml` | Policy engine (Phase 3) | 15+ policies exist |
| Tool manifests | `agents/foundry/tools/*.manifest.yaml` | Tool binder (Phase 1) | 2 manifests exist |
| Capability inventory | `agents/AGENT_CAPABILITY_INVENTORY.yaml` | Portfolio governance (Phase 7) | 142 capabilities tracked |
| ops-console app | `apps/ops-console/` | Portfolio dashboard (Phase 7) | Exists (substantial) |
| Supabase instance | `spdtwktxdalcfigzeqrz` | Memory store, task queue (scale) | Active |
| Azure AI Foundry | `data-intel-ph` project | Agent executor (scale) | Active, 4 logical agents |
| SSOT AI agents | `ssot/ai/agents.yaml` | Foundry runtime binding | Active |
| Agentic SDLC constitution | `agents/foundry/agentic-sdlc-constitution.md` | Predecessor (superseded by constitution.md for lifecycle) | Active (coding rules remain authoritative) |

### External (Azure + SDKs)

| Dependency | Purpose | Phase Required | Cost Impact |
|------------|---------|----------------|-------------|
| **Node.js >= 18** | TypeScript runtime for packages | Phase 0 | None (existing) |
| **pnpm** | Package management | Phase 0 | None (existing) |
| **Zod** | Runtime schema validation | Phase 0 | None (OSS) |
| **vitest** | Unit testing | Phase 0 | None (OSS) |
| **@opentelemetry/sdk-node** | OTLP trace/metric emission | Phase 6 | None (OSS) |
| **@azure/monitor-opentelemetry-exporter** | Azure Monitor sink | Phase 6 | Azure Monitor pricing (ingestion) |
| **Supabase JS client** | `ops.*` table access (memory, task queue) | Phase 1 (scale) | None (self-hosted) |
| **Azure AI Foundry SDK** | Agent execution in Foundry | Phase 6+ (scale) | Azure AI pricing |
| **Slack Web API** | Human escalation notifications | Phase 1 | None (existing workspace) |
| **GitHub Actions** | CI workflows for gates, evals | Phase 2 | Included in Enterprise plan |

---

## 12. Validation Strategy

### Per-Phase Validation

| Phase | Validation Method | Pass Criteria | Evidence Location |
|-------|-------------------|---------------|-------------------|
| **0: Foundations** | `pnpm -s typecheck`, schema CLI against existing manifests | Zero type errors, all existing manifests validate | CI output |
| **1: Task Bus** | Unit tests (>=80% coverage), integration smoke test | All task lifecycle states reachable, dead letter works | `packages/taskbus/src/__tests__/` |
| **2: Registry** | Passport generation for 6 agents, CI workflow on test PR | All 6 agents have valid passports, CI catches invalid schemas | `agents/passports/`, CI logs |
| **3: Assembly Line** | Gate evaluation for each transition, forward/backward test | All 16 gates have definitions, demotion creates records | `agents/foundry/gates/`, test output |
| **4: Evaluations** | Run sample eval suite, verify judge exclusion | Eval results are structured JSON, maker excluded from judge pool | `agents/evals/odoo-sage/results/` |
| **5: Promotions** | Promote test agent L0->L1, verify record immutability | Record written with SHA-256 hash, file never overwritten | `agents/promotions/` |
| **6: Observability** | Execute task, verify trace + metrics + logs emitted | All required trace attributes present, metrics non-zero | Console output, structured logs |
| **7: Portfolio** | Generate report for current 6 agents | Correct counts by maturity/domain/stage, debt items identified | CLI output |
| **8: Retirement** | Deprecate + retire test agent, verify full lifecycle | S14->S15->S16 transitions clean, passport archived | `agents/retirements/`, `agents/passports/retired/` |

### Continuous Validation (CI)

```yaml
# .github/workflows/agent-factory-ci.yml
name: Agent Factory CI
on:
  pull_request:
    paths:
      - 'agents/**'
      - 'packages/agents/**'
      - 'packages/taskbus/**'
      - 'ssot/agent-platform/**'

jobs:
  typecheck:
    # pnpm -s typecheck for both packages
  schema-validate:
    # pnpm agents validate agents/registry/agents.yaml
    # pnpm agents validate agents/passports/*.yaml
  naming-lint:
    # Verify agent IDs, stage IDs, task types conform to constitution
  gate-check:
    # For promotion PRs: verify evidence exists and gates pass
  test:
    # pnpm -s test -- packages/agents packages/taskbus
```

### End-to-End Validation (Phase Gate)

Before declaring any phase complete, run:

```bash
# 1. Type safety
pnpm -s typecheck

# 2. Unit tests
pnpm -s test -- packages/agents packages/taskbus

# 3. Schema validation
pnpm agents validate --all

# 4. Existing agent compatibility
pnpm agents passport --verify-all

# 5. Gate definitions complete
pnpm agents gate-check --verify-definitions
```

---

## 13. MVP First Cut

The smallest practical implementation that establishes the architectural rails. Everything else is incremental on top of this foundation.

### MVP Scope (Phases 0-2, partial Phase 3)

```
 MVP Boundary
 ============================================================
 [x] TypeScript types for: Agent, Task, StageGate, Evaluation,
     Promotion, Policy, Metric
 [x] Zod schemas for: passport, contract, task envelope,
     gate result, promotion record
 [x] In-process TaskBus (EventEmitter) with typed envelopes
 [x] Task router (type matching + maturity ranking)
 [x] Task state machine (PENDING->DONE/FAILED/DEAD_LETTER)
 [x] AgentRegistry (YAML-backed, read from agents.yaml)
 [x] PassportManager (create/read/update, never delete)
 [x] StageGateEngine (evaluate criteria, produce gate results)
 [x] PromotionRecord writer (append-only, SHA-256 hashed)
 [x] Evaluation hook interface (pluggable, stub implementation)
 [x] Console-based observability (structured JSON logs)
 [x] CLI: validate, register, passport, advance, promote
 [x] CI workflow: schema validation on PR
 ============================================================
 NOT in MVP:
 [ ] Supabase persistence (in-memory/file is sufficient)
 [ ] Azure Monitor telemetry (console logs are sufficient)
 [ ] Judge agent implementation (interface only)
 [ ] Portfolio dashboard (CLI report is sufficient)
 [ ] Retirement workflows (manual process is sufficient)
 [ ] Parallel task execution (sequential is sufficient)
 [ ] Human approval via Slack (CLI confirm is sufficient)
```

### MVP File Manifest

```
packages/agents/
├── package.json
├── tsconfig.json
└── src/
    ├── types/
    │   ├── agent.ts              # Agent, Passport, Contract types
    │   ├── task.ts               # TaskEnvelope, TaskState types
    │   ├── gate.ts               # StageGate, GateResult types
    │   ├── eval.ts               # Evaluation, EvalResult types
    │   ├── promotion.ts          # Promotion, PromotionRecord types
    │   ├── policy.ts             # Policy, PolicyBinding types
    │   └── index.ts              # Re-exports
    ├── schemas/
    │   ├── passport.ts           # Zod schema for passport YAML
    │   ├── contract.ts           # Zod schema for manifest YAML
    │   ├── task-envelope.ts      # Zod schema for task messages
    │   ├── gate-result.ts        # Zod schema for gate outcomes
    │   ├── promotion-record.ts   # Zod schema for promotion records
    │   └── index.ts
    ├── registry/
    │   ├── registry.ts           # AgentRegistry class
    │   ├── passport.ts           # PassportManager class
    │   └── contract.ts           # ContractValidator class
    ├── gates/
    │   ├── engine.ts             # StageGateEngine class
    │   └── enforcer.ts           # Stage transition enforcer
    ├── promotions/
    │   ├── controller.ts         # PromotionController class
    │   └── record.ts             # Append-only record writer
    ├── evals/
    │   └── runner.ts             # EvaluationRunner interface + stub
    ├── observability/
    │   └── logger.ts             # Structured JSON console logger
    ├── cli/
    │   ├── validate.ts           # Schema validation command
    │   ├── register.ts           # Agent registration command
    │   ├── passport.ts           # Passport management command
    │   ├── advance.ts            # Stage advancement command
    │   ├── promote.ts            # Promotion command
    │   └── index.ts              # CLI entrypoint
    └── __tests__/
        ├── registry.test.ts
        ├── gates.test.ts
        ├── promotions.test.ts
        └── schemas.test.ts

packages/taskbus/
├── package.json
├── tsconfig.json
└── src/
    ├── bus.ts                    # TaskBus class (EventEmitter)
    ├── router.ts                 # TaskRouter class
    ├── state-machine.ts          # TaskStateMachine
    ├── dead-letter.ts            # DeadLetterQueue
    ├── correlation.ts            # Correlation ID handling
    └── __tests__/
        ├── bus.test.ts
        ├── router.test.ts
        └── state-machine.test.ts
```

### MVP Technology Choices

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Language | TypeScript 5.x | Existing monorepo language, type safety for schemas |
| Schema validation | Zod | Runtime validation + TypeScript inference, no codegen step |
| Task bus (MVP) | Node.js EventEmitter | Zero dependencies, sufficient for single-process |
| Task bus (scale) | Supabase Realtime + `ops.task_queue` | Already deployed, pg_notify is reliable |
| Config format | YAML (passports, gates, policies) | Human-readable, git-diffable, existing convention |
| Test framework | vitest | Fast, TypeScript-native, existing in monorepo |
| CLI framework | commander.js | Lightweight, no build step for scripts |
| Observability (MVP) | Console structured JSON | Zero dependency, parseable |
| Observability (scale) | @opentelemetry/sdk-node -> Azure Monitor | Standard, vendor-neutral core |

### MVP Acceptance Criteria

1. `pnpm -s typecheck` passes for both packages with zero errors
2. `pnpm -s test` passes with >=80% coverage for core modules
3. All 6 existing agents produce valid passports via migration script
4. Schema validation CLI correctly validates/rejects YAML files
5. Task bus routes a typed task to a registered handler and reports DONE
6. Stage gate engine evaluates S01->S02 transition with pass/fail result
7. Promotion controller writes an append-only record with SHA-256 evidence hash
8. CI workflow catches invalid passport/contract schemas on PR

### MVP Timeline Estimate

| Phase | Effort | Cumulative |
|-------|--------|------------|
| Phase 0: Foundations | 2-3 days | 2-3 days |
| Phase 1: Task Bus | 3-4 days | 5-7 days |
| Phase 2: Registry + Passports | 2-3 days | 7-10 days |
| Phase 3 (partial): Gates | 2-3 days | 9-13 days |

**MVP complete in ~2 weeks of focused execution.**

Post-MVP phases (4-8) add capability incrementally without restructuring the foundation.

---

*Schema version: 1.0*
*Effective date: 2026-03-19*
*Owner: @Insightpulseai-net/platform*
*Companion docs: constitution.md, prd.md, tasks.md*
