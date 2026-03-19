# Agent Factory -- Architecture Reference

> Condensed architecture overview for the Agent Orchestration Platform.
> Full specifications live in `spec/agent-factory/` (constitution, PRD, plan, tasks).
> This document is a quick-reference companion, not a duplicate.
>
> Owner: `@Insightpulseai-net/platform`
> Version: 1.0
> Date: 2026-03-19

---

## 1. System Overview

```
                         INSIGHTPULSE AI AGENT FACTORY
 ==========================================================================

 +------------------------------ CONTROL PLANE ----------------------------+
 |                                                                         |
 |  +------------+  +------------+  +-------------+  +--------------+     |
 |  | Agent      |  | Policy     |  | Stage Gate  |  | Evaluation   |     |
 |  | Registry   |  | Engine     |  | Engine      |  | Runner       |     |
 |  +------+-----+  +------+-----+  +------+------+  +------+-------+     |
 |         |               |               |                |              |
 |  +------+---------------+---------------+----------------+--------+    |
 |  |                  Promotion Controller                           |    |
 |  |  decide() -> evidence + gates -> append-only record             |    |
 |  +-----------------------------+-----------------------------------+    |
 |                                |                                        |
 +--------------------------------|----------------------------------------+
                                  | routing rules, kill-switch, policies
 +--------------------------------|----------------------------------------+
 |                         RUNTIME PLANE                                   |
 |                                |                                        |
 |  +-----------------------------v-----------------------------------+    |
 |  |                        TASK BUS                                  |    |
 |  |  Ingress -> Router -> Dispatcher -> Completion                   |    |
 |  |                          |                                       |    |
 |  |                     Dead Letter <-- timeout/error                |    |
 |  +------------------------------------------------------------------+   |
 |                                                                         |
 |  +------------+  +------------+  +-------------+  +--------------+     |
 |  | Agent      |  | Memory     |  | Tool        |  | Observability|     |
 |  | Executor   |  | Store      |  | Binder      |  | Collector    |     |
 |  +------------+  +------------+  +-------------+  +--------------+     |
 |                                                                         |
 +--------------------------------|----------------------------------------+
                                  | execution logs, eval results, records
 +--------------------------------|----------------------------------------+
 |                     ARTIFACT PLANE (Git)                                |
 |                                                                         |
 |  agents/registry/agents.yaml       spec/agent-factory/                  |
 |  agents/passports/<id>.yaml        ssot/agent-platform/                 |
 |  agents/contracts/<id>.yaml        docs/architecture/agent-platform/    |
 |  agents/evals/<id>/                docs/evidence/<date>/                |
 |  agents/promotions/<id>/                                                |
 +-------------------------------------------------------------------------+
```

**Plane separation is enforced.** Components must not cross boundaries except
through defined interfaces (constitution section 3).

| Interface | Direction | Protocol (MVP) | Protocol (Scale) |
|-----------|-----------|----------------|------------------|
| Control -> Runtime | Push | In-process call | HTTP API |
| Control -> Artifact | Write | Git commit | Git commit |
| Runtime -> Control | Push | Event callback | Webhook |
| Runtime -> Artifact | Write | Git commit | Git commit |
| Artifact -> Control | Pull | File read + watch | Webhook |

---

## 2. Agent Lifecycle

14 lifecycle phases spanning 16 operational stages (S01--S16) from intake to retirement.

| Phase | Purpose | Owner | Key Artifact |
|-------|---------|-------|--------------|
| Ideation | Identify need, define domain scope | Operator | Issue / brief |
| Blueprint | Declare identity, purpose, ownership | Operator | `agents/passports/<id>.yaml` |
| Contract | Define I/O schemas, tool bindings, policies | Operator | `agents/contracts/<id>.manifest.yaml` |
| Build | Implement skills, tool integrations, handlers | Operator + Agents | Agent source code |
| Unit Eval | Write and pass unit-level evaluations | Maker Agent | `agents/evals/<id>/scenarios/` |
| Integration Eval | Cross-agent and tool-binding tests | Maker Agent | `agents/evals/<id>/integration/` |
| Sandbox Eval | Full evaluation suite in isolated env | Eval Runner | `agents/evals/<id>/results/<run>.json` |
| Judge Review | Independent judge agent evaluation | Judge Agent | `agents/evals/<id>/judge-reviews/` |
| Canary Deploy | Shadow traffic or limited real traffic | Orchestrator | Deployment config + metrics |
| Staging | Full pre-production validation | Orchestrator | Staging evidence |
| Production | Live deployment, full traffic | Orchestrator | `agents/promotions/<id>/<ts>-L4.yaml` |
| Hardening | Security hardening, edge case coverage | Judge Agent | Updated policy bindings |
| Maturation | Proven baseline for domain | Operator | `agents/promotions/<id>/<ts>-L5.yaml` |
| Retirement | Deprecation notice -> sunset -> archive | Retirement Controller | `agents/retirements/<id>/` |

---

## 3. Maturity Model

| Level | Name | Stage Range | Permissions | Evidence Required |
|-------|------|-------------|-------------|-------------------|
| L0 | Concept | S01-S02 | No execution. Design only. | Blueprint + contract schema validates |
| L1 | Prototype | S03-S05 | Sandbox only. No real data/tools. | Unit + integration evals pass |
| L2 | Evaluated | S06-S07 | Sandbox with eval data. Judge review. | Full eval suite + judge review record |
| L3 | Deployed | S08-S09 | Canary/staging with real data. Kill switch mandatory. | Security review + canary metrics in threshold |
| L4 | Production | S10-S12 | Full production. Observability mandatory. | 48h+ canary with zero critical incidents |
| L5 | Mature | S13 | Proven. May serve as baseline for derived agents. | 30-day track record. Coverage >= 80%. |

---

## 4. Task Bus

### Envelope Schema (TypeScript)

```typescript
interface TaskEnvelope {
  schema: 'ipai.task.v1';
  task_id: string;                      // UUID
  type: string;                         // 'task.<domain>.<action>'
  priority: 'low' | 'normal' | 'high' | 'critical';
  payload: Record<string, unknown>;     // typed per task type
  source_agent_id: string;              // kebab-case or 'human'
  target_agent_id?: string;             // resolved by router if omitted
  correlation_id: string;               // UUID, groups related tasks
  created_at: string;                   // ISO8601
  timeout_ms: number;                   // max 600000 (10 min)
  idempotency_key: string;             // prevents duplicate execution
}

interface TaskReceipt {
  task_id: string;
  state: TaskState;
  routed_to?: string;
  accepted_at: string;
}

type TaskState =
  | 'pending'
  | 'routed'
  | 'running'
  | 'done'
  | 'failed'
  | 'timed_out'
  | 'dead_letter';
```

### State Transitions

```
pending --> routed --> running --> done
                          |-----> failed -----> dead_letter (after max retries)
                          |-----> timed_out --> dead_letter (after max retries)
```

### Routing Model

1. Parse `task.type`, find agents declaring that type in their contract
2. Filter by lifecycle stage (>= S08 for production tasks)
3. Apply policy constraints (tool-allowlist, data-boundary, rate-limit)
4. Check agent health (heartbeat within 5 minutes)
5. Select highest-maturity agent; ties broken by registry priority, then lowest load
6. Reject tasks for retired agents (S15+) with `AGENT_RETIRED`
7. Unroutable tasks -> dead letter + Slack notification to operator

---

## 5. Factory Assembly Line

16 stages from intake to retirement.

| Stage | Name | Purpose | Entry Gate | Exit Gate |
|-------|------|---------|------------|-----------|
| S01 | intake | Blueprint submitted | None | Passport created, schema valid |
| S02 | design | Contract drafted | Valid passport | Contract schema validates, I/O defined |
| S03 | build | Implementation | Valid contract | Agent code exists, compiles/lints |
| S04 | unit-test | Unit evaluations | Buildable agent | All unit eval scenarios pass |
| S05 | integration-test | Cross-agent tests | Unit tests pass | Integration eval scenarios pass |
| S06 | eval-sandbox | Full eval in sandbox | Integration pass | Eval suite passes in isolation |
| S07 | judge-review | Independent quality review | Sandbox eval pass | Judge agent review record exists |
| S08 | canary | Limited real traffic | Judge review pass + security review | Canary metrics within thresholds |
| S09 | staging | Pre-production validation | Canary pass (48h min) | Staging metrics nominal |
| S10 | production | Full live traffic | Staging pass | Observability confirmed, kill switch bound |
| S11 | scaling | Performance optimization | Production stable | Scaling targets met |
| S12 | hardening | Security + edge cases | Scaling pass | Policy tightened, edge cases covered |
| S13 | mature | Proven baseline | 30-day prod record | Coverage >= 80%, zero critical incidents |
| S14 | deprecation-notice | Successor identified | Successor at L2+ | 30-day sunset clock started |
| S15 | sunset | Read-only, draining | 30-day notice served | All in-flight tasks drained |
| S16 | retired | Permanently decommissioned | Tasks drained | Passport archived, routing removed |

---

## 6. Stage Gate Matrix

Evidence types required at each promotion boundary.

| Gate | Passport | Contract | Unit Eval | Integration Eval | Sandbox Eval | Judge Review | Security Review | Canary Metrics | Prod Metrics |
|------|:--------:|:--------:|:---------:|:----------------:|:------------:|:------------:|:---------------:|:--------------:|:------------:|
| S01->S02 | X | | | | | | | | |
| S02->S03 | | X | | | | | | | |
| S03->S04 | | | X | | | | | | |
| S04->S05 | | | X | X | | | | | |
| S05->S06 | | | | X | X | | | | |
| S06->S07 | | | | | X | X | | | |
| S07->S08 | | | | | | X | X | | |
| S08->S09 | | | | | | | | X | |
| S09->S10 | | | | | | | | X | X |
| S13->S14 | | | | | | | | | X |

`X` = required. All gates are binary: pass or fail. No conditional promotions.

---

## 7. Orchestration Model

```
                     +-------------------+
                     |    ORCHESTRATOR    |
                     |                   |
                     |  1. Read registry |
                     |  2. Consult rules |
                     |  3. Check health  |
                     |  4. Route task    |
                     +--------+----------+
                              |
              +---------------+---------------+
              |                               |
     +--------v--------+           +----------v--------+
     |   MAKER AGENTS  |           |   JUDGE AGENTS    |
     |                 |           |                   |
     |  odoo-sage      |           |  quality-sentinel |
     |  devops-prime   |  output   |  compliance-audit |
     |  data-forge     | --------> |  perf-guardian    |
     |  ui-craft       |           |  security-prober  |
     |                 |           |                   |
     +-----------------+           +-------------------+
```

**Invariants:**
- Maker agents never evaluate their own output (P9: maker-judge separation)
- All work flows through the task bus (P6: no direct agent-to-agent calls)
- Judge agents are structurally independent: no shared code, state, or policy bindings
- Kill switch available for every L3+ agent
- Unroutable tasks escalate to human operator via Slack

**Conflict resolution order:** (1) explicit registry priority, (2) lowest current
task count, (3) most recent successful evaluation.

---

## 8. Change Classification

| Change Type | Risk | Blast Radius | Required Validation |
|-------------|------|--------------|---------------------|
| New agent registration | Low | Single agent | Passport schema validation, CI lint |
| Contract modification | Medium | Agent + consumers | Schema validation, integration eval re-run |
| Policy change | Medium | Domain or platform-wide | Policy lint, affected agent re-evaluation |
| Stage promotion | Medium | Single agent | Gate passage + evidence + judge review (L3+) |
| Tool binding change | High | Agent + downstream systems | Integration eval, security review |
| Task type addition | Medium | Routing table | Registry validation, routing test |
| Kill switch activation | High | Single agent + consumers | Audit record, task drain verification |
| Agent retirement | High | Agent + all consumers | 30-day sunset, successor at L2+, task drain |
| Platform policy change | Critical | All agents | Constitution review, full eval sweep |
| Task bus schema change | Critical | All agents | Version bump, migration plan, staged rollout |

---

## 9. Governance Controls

Minimum viable controls for one-man-team operation.

| Control | Mechanism | Enforcement |
|---------|-----------|-------------|
| **Access** | Agent policies declare tool-allowlist and data-boundary | Policy engine at dispatch time |
| **Audit** | All promotions, demotions, kill-switches, policy overrides logged | Append-only records in Git + `ops.*` tables |
| **Kill Switch** | Immediate task routing stop for any L3+ agent | CLI / API / Slack command; mandatory for L3+ |
| **Rollback** | Demotion record + routing removal | Demotion creates new record; original promotion intact |
| **Secrets** | Never in agent code; resolved via Key Vault at runtime | Tool binder injects opaque references |
| **Timeout** | 10-minute hard max per task execution | Runtime plane enforces; exceeded -> timed_out |
| **Idempotency** | Dedup by idempotency_key within 24h window | Task bus rejects duplicate keys |
| **Escalation** | Unroutable/destructive operations -> human | Slack notification + ops table entry |
| **Observability** | OTLP traces, structured metrics, JSON logs mandatory | Silent agents = broken agents |
| **Retirement** | 30-day sunset with successor validation | Task bus stops routing at S15; archive at S16 |

---

## 10. Metrics

Four-level metrics framework.

| Level | Scope | Key Metrics | Sink |
|-------|-------|-------------|------|
| **Agent** | Per-agent | `task.count`, `task.duration_ms`, `task.error_rate`, `eval.score` | Azure Monitor |
| **Portfolio** | All agents | Maturity distribution (L0-L5 histogram), health %, lifecycle velocity | ops-console |
| **Task Bus** | Platform | Throughput (tasks/min), routing latency, dead letter rate, queue depth | Azure Monitor |
| **Governance** | Platform | Promotions/week, demotions/week, policy violations, kill switch activations | Audit log + ops-console |

Required trace attributes on every span: `agent.id`, `task.id`, `task.type`,
`correlation.id`, `maturity.level`.

---

## 11. Repo Structure

```
spec/agent-factory/                    # Spec bundle (constitution, PRD, plan, tasks)
docs/architecture/agent-platform/      # This document + future architecture docs
ssot/agent-platform/                   # Machine-readable SSOT (runtime config)

agents/
  registry/agents.yaml                 # SSOT: all registered agents
  passports/<agent-id>.yaml            # Agent identity + lifecycle
  contracts/<agent-id>.manifest.yaml   # I/O schema + tool bindings
  foundry/
    gates/<from>-<to>.yaml             # Stage gate definitions
    policies/*.policy.yaml             # Policy definitions
    tools/*.manifest.yaml              # Tool manifests
  evals/<agent-id>/
    scenarios/*.yaml                   # Evaluation scenario definitions
    integration/*.yaml                 # Integration eval definitions
    results/<run-id>.json              # Evaluation results (append-only)
    judge-reviews/<run-id>.json        # Judge agent reviews
  promotions/<agent-id>/
    <timestamp>-<level>.yaml           # Promotion records (append-only)
  retirements/<agent-id>/
    deprecation-notice.yaml            # S14 notice
    retirement-record.yaml             # S16 archive

packages/
  agents/src/                          # Agent framework (control plane services)
    types/                             # Branded types, enums, schemas
    registry/                          # Agent registry CRUD
    gates/                             # Stage gate engine
    evals/                             # Evaluation runner
    promotions/                        # Promotion controller
    executor/                          # Agent executor
    policies/                          # Policy engine
    tools/                             # Tool binder
    memory/                            # Memory store
    observability/                     # Telemetry collector
    retirements/                       # Retirement controller
  taskbus/src/                         # Task bus implementation
    bus.ts                             # Core bus interface
    router.ts                          # Task routing engine
    state.ts                           # State machine
    dead-letter.ts                     # Dead letter queue

platform/
  services/agent-factory/              # Factory services (ACA deployment)
  services/task-bus/                   # Task bus service (ACA deployment)
```

---

## 12. Related Documents

| Document | Location | Purpose |
|----------|----------|---------|
| Constitution | `spec/agent-factory/constitution.md` | Normative doctrine, invariant rules |
| PRD | `spec/agent-factory/prd.md` | Full product requirements |
| Plan | `spec/agent-factory/plan.md` | Implementation architecture + phasing |
| Tasks | `spec/agent-factory/tasks.md` | Execution-ready task breakdown |
| Agent Registry | `agents/registry/agents.yaml` | Current agent inventory (6 registered) |
| SDLC Constitution | `agents/foundry/agentic-sdlc-constitution.md` | Coding agent behavior rules |
| Foundry Agents | `ssot/ai/agents.yaml` | Azure Foundry runtime bindings |

---

*Schema version: 1.0 -- Effective: 2026-03-19*
