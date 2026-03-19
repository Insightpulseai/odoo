# Agent Factory / Agent Orchestration Platform -- Task Breakdown

> Execution-ready task list for building the Agent Factory.
> Companion to `spec/agent-factory/constitution.md`.
> Each task produces a concrete artifact or code change. No vague "design X" tasks.
>
> **Repo**: `Insightpulseai/odoo` monorepo
> **Packages**: `packages/agents/`, `packages/taskbus/`
> **Registry**: `agents/registry/agents.yaml` (6 agents registered)
> **Runtime target**: Azure Container Apps + Azure AI Foundry
> **Operator model**: One-man-team, multi-agent execution

---

## Legend

| Field | Values |
|-------|--------|
| **Priority** | P0 = blocks everything, P1 = blocks next phase, P2 = can defer |
| **Complexity** | S = hours, M = half-day, L = full day, XL = multi-day |
| **Status** | `TODO`, `IN_PROGRESS`, `DONE`, `BLOCKED` |

---

## Phase 0: Foundations

Establish the type system, directory layout, and base schemas that every subsequent phase depends on.

### AF-001 -- Define core TypeScript type package

| Field | Value |
|-------|-------|
| **Description** | Create `packages/agents/src/types/index.ts` exporting all shared types: `AgentId`, `StageId`, `MaturityLevel`, `TaskType`, `CorrelationId`, `ISO8601`. Use branded types where possible to prevent stringly-typed errors. |
| **Inputs** | Constitution section 4 (naming doctrine) |
| **Outputs** | `packages/agents/src/types/index.ts` with exported branded types |
| **Priority** | P0 |
| **Complexity** | S |
| **Status** | TODO |

### AF-002 -- Create directory scaffold for agent factory artifacts

| Field | Value |
|-------|-------|
| **Description** | Create canonical directory structure: `agents/passports/`, `agents/passports/retired/`, `agents/promotions/`, `agents/retirements/`, `agents/evals/`, `agents/foundry/gates/`, `agents/foundry/policies/`. Add `.gitkeep` to empty dirs. |
| **Inputs** | Constitution section 8 (stage-to-artifact mapping) |
| **Outputs** | Directory tree matching constitution artifact locations |
| **Priority** | P0 |
| **Complexity** | S |
| **Status** | TODO |

### AF-003 -- Define TaskEnvelope JSON schema

| Field | Value |
|-------|-------|
| **Description** | Create `packages/taskbus/src/schemas/task-envelope.schema.json` implementing the `ipai.task.v1` schema from constitution section 11.1. Include `task_id`, `type`, `priority`, `payload`, `source_agent_id`, `target_agent_id`, `correlation_id`, `created_at`, `timeout_ms`, `idempotency_key`. |
| **Inputs** | Constitution section 11.1 (task message schema) |
| **Outputs** | JSON Schema file + generated TypeScript type via `json-schema-to-typescript` |
| **Priority** | P0 |
| **Complexity** | S |
| **Status** | TODO |

### AF-004 -- Define AgentPassport JSON schema

| Field | Value |
|-------|-------|
| **Description** | Create `packages/agents/src/schemas/passport.schema.json` implementing the `ipai.passport.v1` schema from constitution section 9. All fields from the constitution passport template. |
| **Inputs** | Constitution section 9 (agent passport schema) |
| **Outputs** | JSON Schema file + generated TypeScript type |
| **Priority** | P0 |
| **Complexity** | S |
| **Status** | TODO |

### AF-005 -- Define PromotionRecord JSON schema

| Field | Value |
|-------|-------|
| **Description** | Create `packages/agents/src/schemas/promotion-record.schema.json` implementing `ipai.promotion.v1` from constitution section 6.3. Fields: `agent_id`, `timestamp`, `from_level`, `to_level`, `type`, `evidence[]`, `gate_results[]`, `approver`, `reason`. |
| **Inputs** | Constitution section 6.3 (promotion record schema) |
| **Outputs** | JSON Schema file + generated TypeScript type |
| **Priority** | P0 |
| **Complexity** | S |
| **Status** | TODO |

### AF-006 -- Define RetirementRecord JSON schema

| Field | Value |
|-------|-------|
| **Description** | Create `packages/agents/src/schemas/retirement-record.schema.json` implementing `ipai.retirement.v1` from constitution section 7.2. |
| **Inputs** | Constitution section 7.2 (retirement record schema) |
| **Outputs** | JSON Schema file + generated TypeScript type |
| **Priority** | P0 |
| **Complexity** | S |
| **Status** | TODO |

### AF-007 -- Define StageGateResult schema

| Field | Value |
|-------|-------|
| **Description** | Create `packages/agents/src/schemas/stage-gate-result.schema.json`. Fields: `gate_id`, `stage_from`, `stage_to`, `criteria[]` (each with `name`, `result: pass|fail`, `evidence_ref`, `evaluated_at`), `overall_result`, `evaluated_by`. |
| **Inputs** | Constitution section 5.4, section 8 |
| **Outputs** | JSON Schema file + generated TypeScript type |
| **Priority** | P0 |
| **Complexity** | S |
| **Status** | TODO |

### AF-008 -- Set up package.json and tsconfig for packages/agents and packages/taskbus

| Field | Value |
|-------|-------|
| **Description** | Initialize both packages with `package.json` (name: `@ipai/agents`, `@ipai/taskbus`), `tsconfig.json` (strict mode, ESM, Node18+ target), entry points, and build scripts. Wire into monorepo `turbo.json`. |
| **Inputs** | Monorepo root `package.json`, `turbo.json` |
| **Outputs** | Buildable `packages/agents/` and `packages/taskbus/` with `pnpm build` passing |
| **Priority** | P0 |
| **Complexity** | M |
| **Status** | TODO |

---

## Phase 1: Task Bus

Implement the central message broker. In-memory for MVP, pluggable backend for production.

### AF-010 -- Implement TaskEnvelope class with validation

| Field | Value |
|-------|-------|
| **Description** | Create `packages/taskbus/src/task-envelope.ts`. Constructor validates against `task-envelope.schema.json` using Ajv. Factory method `TaskEnvelope.create()` generates `task_id` (UUIDv7) and `created_at`. |
| **Inputs** | AF-003 (schema) |
| **Outputs** | `TaskEnvelope` class with `create()`, `validate()`, `toJSON()` methods |
| **Priority** | P0 |
| **Complexity** | M |
| **Status** | TODO |

### AF-011 -- Implement task state machine

| Field | Value |
|-------|-------|
| **Description** | Create `packages/taskbus/src/task-state-machine.ts`. States: `pending`, `routed`, `in_progress`, `completed`, `failed`, `timed_out`, `dead_letter`. Transitions are strict (e.g. `pending -> routed -> in_progress -> completed|failed`). Emit state change events. |
| **Inputs** | AF-010 (TaskEnvelope) |
| **Outputs** | `TaskStateMachine` class with `transition()`, `currentState()`, `history()` methods |
| **Priority** | P0 |
| **Complexity** | M |
| **Status** | TODO |

### AF-012 -- Implement in-process task router

| Field | Value |
|-------|-------|
| **Description** | Create `packages/taskbus/src/router.ts`. Accepts a `TaskEnvelope`, looks up `type` in routing table, resolves target agent by matching `task_types` in registry. Highest-maturity agent wins ties. Returns `RoutingDecision` with `target_agent_id` and `reason`. |
| **Inputs** | AF-010 (TaskEnvelope), AF-001 (types) |
| **Outputs** | `TaskRouter` class with `route(envelope): RoutingDecision` method |
| **Priority** | P0 |
| **Complexity** | M |
| **Status** | TODO |

### AF-013 -- Implement in-memory task queue

| Field | Value |
|-------|-------|
| **Description** | Create `packages/taskbus/src/queue.ts`. Priority-ordered queue (critical > high > normal > low). Methods: `enqueue()`, `dequeue()`, `peek()`, `size()`, `drain()`. Backed by sorted array for MVP. Interface `TaskQueueBackend` allows future swap to Redis/Supabase. |
| **Inputs** | AF-010 (TaskEnvelope), AF-011 (state machine) |
| **Outputs** | `InMemoryTaskQueue` implementing `TaskQueueBackend` interface |
| **Priority** | P0 |
| **Complexity** | M |
| **Status** | TODO |

### AF-014 -- Implement routing rules engine

| Field | Value |
|-------|-------|
| **Description** | Create `packages/taskbus/src/routing-rules.ts`. Load routing rules from YAML config. Rules match on task `type` glob patterns (e.g., `task.odoo.*` -> `odoo-sage`). Support agent filter by maturity level (min L3 for production tasks). Support agent exclusion (retired agents). |
| **Inputs** | AF-012 (router), AF-001 (types) |
| **Outputs** | `RoutingRulesEngine` class, `routing-rules.schema.json` |
| **Priority** | P1 |
| **Complexity** | M |
| **Status** | TODO |

### AF-015 -- Implement dead letter handler

| Field | Value |
|-------|-------|
| **Description** | Create `packages/taskbus/src/dead-letter.ts`. Tasks enter dead letter when: max retries exceeded (default 3), unroutable, or handler throws unrecoverable error. Dead letter store is append-only JSON file for MVP. Emits `task.dead_letter` event with reason. |
| **Inputs** | AF-011 (state machine), AF-013 (queue) |
| **Outputs** | `DeadLetterHandler` class with `send()`, `list()`, `replay()` methods |
| **Priority** | P1 |
| **Complexity** | M |
| **Status** | TODO |

### AF-016 -- Implement correlation ID propagation

| Field | Value |
|-------|-------|
| **Description** | Create `packages/taskbus/src/correlation.ts`. When an agent creates sub-tasks, the parent `correlation_id` propagates to children. Provide `CorrelationContext` that tracks parent-child task trees. Enable trace reconstruction from any task in a chain. |
| **Inputs** | AF-010 (TaskEnvelope) |
| **Outputs** | `CorrelationContext` class with `createChild()`, `getRoot()`, `getTree()` methods |
| **Priority** | P1 |
| **Complexity** | S |
| **Status** | TODO |

### AF-017 -- Implement task event log

| Field | Value |
|-------|-------|
| **Description** | Create `packages/taskbus/src/event-log.ts`. Append-only log of all task state transitions. Each entry: `task_id`, `from_state`, `to_state`, `timestamp`, `agent_id`, `detail`. MVP: JSONL file. Interface `TaskEventLogBackend` for future Supabase swap. |
| **Inputs** | AF-011 (state machine) |
| **Outputs** | `TaskEventLog` implementing `TaskEventLogBackend` interface |
| **Priority** | P1 |
| **Complexity** | M |
| **Status** | TODO |

### AF-018 -- Implement task bus health check

| Field | Value |
|-------|-------|
| **Description** | Create `packages/taskbus/src/health.ts`. Reports: queue depth, dead letter count, tasks in each state, oldest pending task age, router status (rules loaded). Returns structured `TaskBusHealth` object. |
| **Inputs** | AF-013 (queue), AF-015 (dead letter), AF-011 (state machine) |
| **Outputs** | `taskBusHealth(): TaskBusHealth` function |
| **Priority** | P1 |
| **Complexity** | S |
| **Status** | TODO |

### AF-019 -- Implement task bus CLI

| Field | Value |
|-------|-------|
| **Description** | Create `packages/taskbus/src/cli.ts`. Commands: `taskbus submit <type> <payload-json>`, `taskbus status <task-id>`, `taskbus queue`, `taskbus dead-letter`, `taskbus health`, `taskbus replay <task-id>`. Use `commander` for arg parsing. |
| **Inputs** | AF-010 through AF-018 |
| **Outputs** | Executable CLI at `packages/taskbus/bin/taskbus` |
| **Priority** | P2 |
| **Complexity** | M |
| **Status** | TODO |

---

## Phase 2: Registry + Passports

Implement the agent identity system. Migrate existing 6 agents to passport format.

### AF-020 -- Implement AgentPassport class with validation

| Field | Value |
|-------|-------|
| **Description** | Create `packages/agents/src/passport.ts`. Constructor validates against `passport.schema.json`. Methods: `validate()`, `toYAML()`, `fromYAML()`, `currentStage()`, `maturityLevel()`, `isRetired()`. Immutable after construction (create new instance for updates). |
| **Inputs** | AF-004 (schema) |
| **Outputs** | `AgentPassport` class |
| **Priority** | P0 |
| **Complexity** | M |
| **Status** | TODO |

### AF-021 -- Implement agent registry CRUD

| Field | Value |
|-------|-------|
| **Description** | Create `packages/agents/src/registry.ts`. Reads from `agents/registry/agents.yaml` and `agents/passports/*.yaml`. Methods: `register(passport)`, `get(agentId)`, `update(agentId, patch)`, `list(filter?)`, `remove(agentId)` (soft-remove: marks retired). Writes back to YAML files. |
| **Inputs** | AF-020 (AgentPassport), existing `agents/registry/agents.yaml` |
| **Outputs** | `AgentRegistry` class |
| **Priority** | P0 |
| **Complexity** | L |
| **Status** | TODO |

### AF-022 -- Implement passport validator (CI-grade)

| Field | Value |
|-------|-------|
| **Description** | Create `packages/agents/src/passport-validator.ts`. Validates: schema conformance, unique agent ID across registry, required fields for maturity level (e.g., L3+ needs `kill_switch.enabled: true`), no circular skill references, owner exists. Returns structured `ValidationResult[]`. |
| **Inputs** | AF-020 (AgentPassport), AF-004 (schema) |
| **Outputs** | `validatePassport(passport, registry): ValidationResult[]` function |
| **Priority** | P0 |
| **Complexity** | M |
| **Status** | TODO |

### AF-023 -- Implement YAML-based registry index

| Field | Value |
|-------|-------|
| **Description** | Create `packages/agents/src/registry-index.ts`. Builds an in-memory index from `agents/registry/agents.yaml` on load. Supports lookup by: `id`, `domain`, `maturity_level`, `current_stage`, `owner`. Rebuilds on file change (watch mode for dev). |
| **Inputs** | AF-021 (registry), existing `agents.yaml` |
| **Outputs** | `RegistryIndex` class with typed query methods |
| **Priority** | P1 |
| **Complexity** | M |
| **Status** | TODO |

### AF-024 -- Implement agent search and filter

| Field | Value |
|-------|-------|
| **Description** | Create `packages/agents/src/search.ts`. Filter agents by: domain, maturity range, stage range, task type capability, owner, active/retired status. Compose filters with AND logic. Returns sorted results (by maturity desc, then name asc). |
| **Inputs** | AF-023 (registry index) |
| **Outputs** | `searchAgents(filters: AgentFilter): AgentPassport[]` function |
| **Priority** | P1 |
| **Complexity** | S |
| **Status** | TODO |

### AF-025 -- Implement registry CLI

| Field | Value |
|-------|-------|
| **Description** | Create `packages/agents/src/cli.ts`. Commands: `agents list [--domain] [--stage] [--level]`, `agents get <id>`, `agents register <passport.yaml>`, `agents validate <passport.yaml>`, `agents search <query>`. Table-formatted output. |
| **Inputs** | AF-021 through AF-024 |
| **Outputs** | Executable CLI at `packages/agents/bin/agents` |
| **Priority** | P2 |
| **Complexity** | M |
| **Status** | TODO |

### AF-026 -- Migrate odoo-sage to passport format

| Field | Value |
|-------|-------|
| **Description** | Create `agents/passports/odoo-sage.yaml` conforming to `ipai.passport.v1`. Assign stage `S03` (build) and maturity `L1` (prototype). Populate skills, tools, policies from existing registry entry. Set 30-day grace period for evaluation evidence per constitution section 14. |
| **Inputs** | AF-020 (AgentPassport), existing registry entry for `odoo-sage` |
| **Outputs** | `agents/passports/odoo-sage.yaml` |
| **Priority** | P1 |
| **Complexity** | S |
| **Status** | TODO |

### AF-027 -- Migrate remaining 5 agents to passport format

| Field | Value |
|-------|-------|
| **Description** | Create passport YAML files for `devops-prime`, `data-forge`, `ui-craft`, `supabase-ssot`, `automation-specialist`. Each gets stage and maturity assessment based on current deployment state. All start at L1 maximum (no evaluation evidence exists yet). |
| **Inputs** | AF-026 (odoo-sage passport as template), existing registry entries |
| **Outputs** | 5 passport files in `agents/passports/` |
| **Priority** | P1 |
| **Complexity** | M |
| **Status** | TODO |

### AF-028 -- Implement passport versioning

| Field | Value |
|-------|-------|
| **Description** | Create `packages/agents/src/passport-version.ts`. When a passport is updated, increment `version` field (semver). Store previous version in `agents/passports/history/<agent-id>/v<old>.yaml`. Method: `bumpVersion(passport, changeType: 'major'|'minor'|'patch'): AgentPassport`. |
| **Inputs** | AF-020 (AgentPassport) |
| **Outputs** | `PassportVersioner` class, `agents/passports/history/` directory structure |
| **Priority** | P2 |
| **Complexity** | M |
| **Status** | TODO |

### AF-029 -- Implement registry health check

| Field | Value |
|-------|-------|
| **Description** | Create `packages/agents/src/registry-health.ts`. Checks: all passports valid, no orphan passports (in dir but not in registry), no phantom agents (in registry but no passport), no agents past 30-day grace without evals, no duplicate IDs. Returns `RegistryHealth` report. |
| **Inputs** | AF-021 (registry), AF-022 (validator) |
| **Outputs** | `registryHealth(): RegistryHealth` function |
| **Priority** | P1 |
| **Complexity** | M |
| **Status** | TODO |

---

## Phase 3: Assembly Line Stages

Implement the 16-stage lifecycle and gate engine.

### AF-030 -- Define stage configuration YAML

| Field | Value |
|-------|-------|
| **Description** | Create `agents/foundry/gates/stages.yaml` defining all 16 stages (S01-S16) with: `id`, `name`, `description`, `entry_criteria[]`, `exit_criteria[]`, `required_artifacts[]`, `allowed_transitions[]`. Derive from constitution section 4.2. |
| **Inputs** | Constitution section 4.2, section 8 (stage-to-artifact mapping) |
| **Outputs** | `agents/foundry/gates/stages.yaml` |
| **Priority** | P0 |
| **Complexity** | L |
| **Status** | TODO |

### AF-031 -- Implement stage definition loader

| Field | Value |
|-------|-------|
| **Description** | Create `packages/agents/src/stages/loader.ts`. Parses `stages.yaml`, validates against a stage definition schema, and returns typed `StageDefinition[]`. Exported as `loadStages(path?): StageDefinition[]`. |
| **Inputs** | AF-030 (stages.yaml), AF-007 (StageGateResult schema) |
| **Outputs** | `StageLoader` class with typed `StageDefinition` output |
| **Priority** | P0 |
| **Complexity** | S |
| **Status** | TODO |

### AF-032 -- Implement stage gate engine

| Field | Value |
|-------|-------|
| **Description** | Create `packages/agents/src/stages/gate-engine.ts`. Given an agent passport and a target stage, evaluate all exit criteria for current stage and entry criteria for target stage. Returns `StageGateResult` (pass/fail with per-criterion detail). Gates are binary per constitution P7. |
| **Inputs** | AF-031 (stage loader), AF-020 (AgentPassport), AF-007 (StageGateResult schema) |
| **Outputs** | `StageGateEngine` class with `evaluate(passport, targetStage): StageGateResult` |
| **Priority** | P0 |
| **Complexity** | L |
| **Status** | TODO |

### AF-033 -- Implement entry/exit criteria evaluator

| Field | Value |
|-------|-------|
| **Description** | Create `packages/agents/src/stages/criteria-evaluator.ts`. Each criterion type has an evaluator: `artifact_exists` (check file path), `schema_valid` (validate YAML/JSON), `eval_passing` (check eval results), `judge_signed` (check judge review exists), `metric_threshold` (check metric value). Pluggable evaluator registry. |
| **Inputs** | AF-030 (stage definitions with criteria) |
| **Outputs** | `CriteriaEvaluator` class with `evaluate(criterion, context): CriterionResult` |
| **Priority** | P0 |
| **Complexity** | L |
| **Status** | TODO |

### AF-034 -- Implement stage transition logger

| Field | Value |
|-------|-------|
| **Description** | Create `packages/agents/src/stages/transition-log.ts`. Append-only JSONL log at `agents/foundry/gates/transitions.jsonl`. Each entry: `agent_id`, `from_stage`, `to_stage`, `gate_result_ref`, `timestamp`, `triggered_by`. Methods: `log()`, `getHistory(agentId)`, `getAll()`. |
| **Inputs** | AF-032 (gate engine) |
| **Outputs** | `StageTransitionLog` class |
| **Priority** | P1 |
| **Complexity** | S |
| **Status** | TODO |

### AF-035 -- Implement artifact validator per stage

| Field | Value |
|-------|-------|
| **Description** | Create `packages/agents/src/stages/artifact-validator.ts`. For each stage, verify that required artifacts (from constitution section 8) exist and pass schema validation. E.g., S01 requires `agents/passports/<id>.yaml`, S02 requires `agents/foundry/agents/<id>.manifest.yaml`. |
| **Inputs** | AF-030 (stages.yaml with required_artifacts), AF-004/AF-005/AF-006 (schemas) |
| **Outputs** | `validateStageArtifacts(agentId, stage): ArtifactValidationResult[]` function |
| **Priority** | P1 |
| **Complexity** | M |
| **Status** | TODO |

### AF-036 -- Implement stage dashboard (CLI)

| Field | Value |
|-------|-------|
| **Description** | Add `agents stages` subcommand to the registry CLI. Commands: `agents stages list` (all agents by stage), `agents stages check <agent-id>` (gate status for next stage), `agents stages history <agent-id>` (transition log). Table output with color-coded pass/fail. |
| **Inputs** | AF-032 (gate engine), AF-034 (transition log), AF-025 (registry CLI) |
| **Outputs** | Extended CLI with `stages` subcommand |
| **Priority** | P2 |
| **Complexity** | M |
| **Status** | TODO |

### AF-037 -- Implement stage automation hooks

| Field | Value |
|-------|-------|
| **Description** | Create `packages/agents/src/stages/hooks.ts`. Define `onEnterStage` and `onExitStage` hook interface. Built-in hooks: `S01.onEnter` creates passport, `S14.onEnter` starts sunset timer, `S15.onEnter` drains task bus, `S16.onEnter` archives passport. Hooks are async and can emit task bus messages. |
| **Inputs** | AF-032 (gate engine), AF-010 (TaskEnvelope for emitting tasks) |
| **Outputs** | `StageHookRegistry` with `register()` and `trigger()` methods |
| **Priority** | P1 |
| **Complexity** | L |
| **Status** | TODO |

### AF-038 -- Implement parallel stage support

| Field | Value |
|-------|-------|
| **Description** | Create `packages/agents/src/stages/parallel.ts`. Allow agents to execute S04 (unit-test) and S05 (integration-test) in parallel when both have satisfied entry criteria independently. Track parallel stage state as `[S04, S05]` tuple. Gate to S06 requires both complete. |
| **Inputs** | AF-032 (gate engine), AF-030 (stage definitions) |
| **Outputs** | `ParallelStageTracker` class |
| **Priority** | P2 |
| **Complexity** | M |
| **Status** | TODO |

---

## Phase 4: Evaluations + Judge Agents

Implement the evaluation framework and maker-judge separation.

### AF-050 -- Define evaluation spec schema

| Field | Value |
|-------|-------|
| **Description** | Create `packages/agents/src/schemas/eval-spec.schema.json`. Fields: `eval_id`, `agent_id`, `scenarios[]` (each with `name`, `input`, `expected_output`, `rubric_ref`, `timeout_ms`), `created_at`, `version`. |
| **Inputs** | Constitution section 5.4 (quality rules) |
| **Outputs** | JSON Schema file + generated TypeScript type |
| **Priority** | P0 |
| **Complexity** | S |
| **Status** | TODO |

### AF-051 -- Define rubric format schema

| Field | Value |
|-------|-------|
| **Description** | Create `packages/agents/src/schemas/rubric.schema.json`. A rubric defines grading criteria for a scenario: `rubric_id`, `criteria[]` (each with `name`, `weight`, `scoring: binary|scale|regex_match|json_path_check`, `threshold`). Rubrics are reusable across agents. |
| **Inputs** | AF-050 (eval spec) |
| **Outputs** | JSON Schema file + generated TypeScript type |
| **Priority** | P0 |
| **Complexity** | S |
| **Status** | TODO |

### AF-052 -- Implement evaluation runner

| Field | Value |
|-------|-------|
| **Description** | Create `packages/agents/src/evals/runner.ts`. Loads an eval spec, executes each scenario against the target agent (via task bus submission), collects responses, applies rubrics, produces `EvalRunResult`. Supports `--dry-run` mode that validates spec without executing. |
| **Inputs** | AF-050 (eval spec), AF-051 (rubric), AF-010 (TaskEnvelope) |
| **Outputs** | `EvalRunner` class with `run(evalSpec): EvalRunResult` method |
| **Priority** | P0 |
| **Complexity** | XL |
| **Status** | TODO |

### AF-053 -- Implement deterministic test harness

| Field | Value |
|-------|-------|
| **Description** | Create `packages/agents/src/evals/test-harness.ts`. Wraps eval runner with deterministic controls: fixed random seeds, mocked external services, frozen timestamps, captured I/O. Produces reproducible results across runs. |
| **Inputs** | AF-052 (eval runner) |
| **Outputs** | `DeterministicHarness` class wrapping `EvalRunner` |
| **Priority** | P1 |
| **Complexity** | L |
| **Status** | TODO |

### AF-054 -- Define judge agent contract

| Field | Value |
|-------|-------|
| **Description** | Create `agents/foundry/agents/judge.manifest.yaml` template. Judge agents accept `task.eval.judge-review` tasks, receive maker output + rubric, and return `JudgeVerdict` with per-criterion scores and overall pass/fail. Enforce constitution P9: judge cannot be the maker. |
| **Inputs** | Constitution P9 (maker-judge separation), AF-051 (rubric) |
| **Outputs** | Judge agent manifest template, `JudgeVerdict` TypeScript type |
| **Priority** | P0 |
| **Complexity** | M |
| **Status** | TODO |

### AF-055 -- Implement judge loop integration

| Field | Value |
|-------|-------|
| **Description** | Create `packages/agents/src/evals/judge-loop.ts`. After eval runner produces results, submit them to a qualified judge agent via task bus. Judge returns verdict. If verdict is `fail`, attach rejection reason. Judge loop respects the routing rules engine (judge must be different agent than maker). |
| **Inputs** | AF-052 (eval runner), AF-054 (judge contract), AF-012 (task router) |
| **Outputs** | `JudgeLoop` class with `requestReview(evalResult): JudgeVerdict` method |
| **Priority** | P1 |
| **Complexity** | L |
| **Status** | TODO |

### AF-056 -- Implement eval result storage

| Field | Value |
|-------|-------|
| **Description** | Create `packages/agents/src/evals/storage.ts`. Store eval results at `agents/evals/<agent-id>/results/<run-id>.json`. Each result includes: `run_id`, `eval_spec_ref`, `scenarios_run`, `scenarios_passed`, `scenarios_failed`, `rubric_scores`, `judge_verdict_ref`, `timestamp`, `duration_ms`. |
| **Inputs** | AF-052 (eval runner) |
| **Outputs** | `EvalStorage` class with `save()`, `load()`, `listRuns()` methods |
| **Priority** | P1 |
| **Complexity** | M |
| **Status** | TODO |

### AF-057 -- Implement eval comparison (version-over-version)

| Field | Value |
|-------|-------|
| **Description** | Create `packages/agents/src/evals/compare.ts`. Compare two eval run results for the same agent. Output: scenarios that improved, regressed, or stayed stable. Highlight score deltas. Detect new failures. Return `EvalComparison` with `improvements[]`, `regressions[]`, `stable[]`. |
| **Inputs** | AF-056 (eval storage) |
| **Outputs** | `compareEvalRuns(runA, runB): EvalComparison` function |
| **Priority** | P2 |
| **Complexity** | M |
| **Status** | TODO |

### AF-058 -- Implement eval CLI

| Field | Value |
|-------|-------|
| **Description** | Add `agents eval` subcommand. Commands: `agents eval run <agent-id> <spec.yaml>`, `agents eval results <agent-id>`, `agents eval compare <run-id-a> <run-id-b>`, `agents eval judge <agent-id> <run-id>`. |
| **Inputs** | AF-052 through AF-057 |
| **Outputs** | Extended CLI with `eval` subcommand |
| **Priority** | P2 |
| **Complexity** | M |
| **Status** | TODO |

### AF-059 -- Integrate eval gates with stage gates

| Field | Value |
|-------|-------|
| **Description** | Create `packages/agents/src/stages/eval-gate-criterion.ts`. Register `eval_passing` and `judge_signed` criterion types in the criteria evaluator. `eval_passing` checks that latest eval run for agent has >= N% pass rate. `judge_signed` checks that a judge verdict exists and is `pass`. |
| **Inputs** | AF-033 (criteria evaluator), AF-056 (eval storage) |
| **Outputs** | Two registered criterion evaluator plugins |
| **Priority** | P0 |
| **Complexity** | M |
| **Status** | TODO |

### AF-060 -- Create sample judge agent (quality-judge)

| Field | Value |
|-------|-------|
| **Description** | Create `agents/passports/quality-judge.yaml` and `agents/foundry/agents/quality-judge.manifest.yaml`. Implements the judge contract. Accepts `task.eval.judge-review`, applies rubric, returns verdict. This is the first judge agent and serves as the reference implementation. Register in `agents/registry/agents.yaml`. |
| **Inputs** | AF-054 (judge contract), AF-027 (passport format) |
| **Outputs** | `quality-judge` passport, manifest, and skeleton implementation |
| **Priority** | P1 |
| **Complexity** | L |
| **Status** | TODO |

---

## Phase 5: Promotion / Release Controls

Implement the promotion decision pipeline and release lane management.

### AF-070 -- Implement PromotionRecord class with validation

| Field | Value |
|-------|-------|
| **Description** | Create `packages/agents/src/promotions/record.ts`. Constructor validates against `promotion-record.schema.json`. Records are immutable after creation (append-only per constitution P13). Methods: `create()`, `validate()`, `toYAML()`, `fromYAML()`. |
| **Inputs** | AF-005 (promotion record schema) |
| **Outputs** | `PromotionRecord` class |
| **Priority** | P0 |
| **Complexity** | S |
| **Status** | TODO |

### AF-071 -- Implement promotion controller

| Field | Value |
|-------|-------|
| **Description** | Create `packages/agents/src/promotions/controller.ts`. Orchestrates a promotion: (1) verify current maturity level, (2) run stage gate evaluation, (3) check evidence requirements from constitution section 6.2, (4) create promotion record, (5) update passport, (6) log transition. Rejects if any gate fails. |
| **Inputs** | AF-070 (PromotionRecord), AF-032 (gate engine), AF-020 (AgentPassport) |
| **Outputs** | `PromotionController` class with `promote(agentId, targetLevel): PromotionResult` |
| **Priority** | P0 |
| **Complexity** | XL |
| **Status** | TODO |

### AF-072 -- Define release lane configuration

| Field | Value |
|-------|-------|
| **Description** | Create `agents/foundry/gates/release-lanes.yaml` defining the 4 lanes: `canary` (L3, shadow traffic), `staging` (L3, full pre-prod), `production` (L4, full traffic), `hotfix` (bypass lane with mandatory audit record). Each lane specifies: `min_maturity`, `required_gates[]`, `auto_promote: bool`, `rollback_policy`. |
| **Inputs** | Constitution section 4.4 (maturity levels), section 2 (release lane definition) |
| **Outputs** | `agents/foundry/gates/release-lanes.yaml` |
| **Priority** | P1 |
| **Complexity** | M |
| **Status** | TODO |

### AF-073 -- Implement promotion evidence validator

| Field | Value |
|-------|-------|
| **Description** | Create `packages/agents/src/promotions/evidence-validator.ts`. For each promotion level (L0->L1 through L4->L5), verify evidence requirements from constitution section 6.2 exist. Check file paths resolve, JSON/YAML is valid, hashes match if provided. |
| **Inputs** | AF-070 (PromotionRecord), constitution section 6.2 |
| **Outputs** | `validatePromotionEvidence(record): EvidenceValidationResult[]` function |
| **Priority** | P0 |
| **Complexity** | M |
| **Status** | TODO |

### AF-074 -- Implement rollback/demotion record handler

| Field | Value |
|-------|-------|
| **Description** | Create `packages/agents/src/promotions/demotion.ts`. Creates demotion records (same schema as promotion but `type: demotion`). References the original promotion record. Updates passport to lower maturity level. Emits `agent.demoted` event. |
| **Inputs** | AF-070 (PromotionRecord), AF-020 (AgentPassport) |
| **Outputs** | `DemotionHandler` class with `demote(agentId, targetLevel, reason): DemotionResult` |
| **Priority** | P1 |
| **Complexity** | M |
| **Status** | TODO |

### AF-075 -- Implement promotion audit log

| Field | Value |
|-------|-------|
| **Description** | Create `packages/agents/src/promotions/audit-log.ts`. Append-only JSONL at `agents/promotions/audit.jsonl`. Every promotion and demotion event is logged with: `agent_id`, `action`, `from_level`, `to_level`, `evidence_refs[]`, `gate_results_summary`, `approver`, `timestamp`. |
| **Inputs** | AF-071 (promotion controller), AF-074 (demotion handler) |
| **Outputs** | `PromotionAuditLog` class with `append()`, `query()` methods |
| **Priority** | P1 |
| **Complexity** | S |
| **Status** | TODO |

### AF-076 -- Implement promotion CLI

| Field | Value |
|-------|-------|
| **Description** | Add `agents promote` subcommand. Commands: `agents promote <agent-id> <target-level>`, `agents demote <agent-id> <target-level> --reason <text>`, `agents promotions <agent-id>` (history), `agents promotions audit` (full log). |
| **Inputs** | AF-071 through AF-075 |
| **Outputs** | Extended CLI with `promote` subcommand |
| **Priority** | P2 |
| **Complexity** | M |
| **Status** | TODO |

### AF-077 -- Implement maturity level calculator

| Field | Value |
|-------|-------|
| **Description** | Create `packages/agents/src/promotions/maturity-calculator.ts`. Given a passport, compute the maximum maturity level the agent qualifies for based on: current stage, existing eval evidence, judge reviews, production track record. Returns `MaturityAssessment` with `current`, `eligible`, `blockers[]`. |
| **Inputs** | AF-020 (AgentPassport), AF-056 (eval storage), constitution section 6.2 |
| **Outputs** | `calculateMaturity(passport): MaturityAssessment` function |
| **Priority** | P1 |
| **Complexity** | M |
| **Status** | TODO |

### AF-078 -- Implement promotion notification hooks

| Field | Value |
|-------|-------|
| **Description** | Create `packages/agents/src/promotions/notifications.ts`. On promotion or demotion, emit events consumable by external systems. Built-in hooks: (1) write to task bus as `task.platform.agent-promoted`, (2) Slack webhook (URL from env var, not hardcoded). Interface `PromotionNotifier` for extensibility. |
| **Inputs** | AF-071 (promotion controller), AF-010 (TaskEnvelope) |
| **Outputs** | `PromotionNotifier` interface + `SlackPromotionNotifier` and `TaskBusPromotionNotifier` implementations |
| **Priority** | P2 |
| **Complexity** | M |
| **Status** | TODO |

---

## Phase 6: Runtime Observability

Implement structured telemetry for agent executions.

### AF-080 -- Define metric schema

| Field | Value |
|-------|-------|
| **Description** | Create `packages/agents/src/schemas/metric.schema.json`. Fields: `metric_name` (dot-delimited, e.g. `agent.odoo-sage.task.count`), `value`, `unit`, `timestamp`, `labels` (key-value pairs: `agent_id`, `task_type`, `stage`), `type: counter|gauge|histogram`. |
| **Inputs** | Constitution section 12 (observability contract) |
| **Outputs** | JSON Schema file + generated TypeScript type |
| **Priority** | P1 |
| **Complexity** | S |
| **Status** | TODO |

### AF-081 -- Implement metric collector

| Field | Value |
|-------|-------|
| **Description** | Create `packages/agents/src/observability/collector.ts`. In-process metric collector. Methods: `increment(name, labels)`, `gauge(name, value, labels)`, `histogram(name, value, labels)`, `flush(): Metric[]`. MVP stores in memory; interface `MetricBackend` allows future OTLP/Azure Monitor push. |
| **Inputs** | AF-080 (metric schema) |
| **Outputs** | `MetricCollector` class implementing `MetricBackend` interface |
| **Priority** | P1 |
| **Complexity** | M |
| **Status** | TODO |

### AF-082 -- Implement agent-level metrics

| Field | Value |
|-------|-------|
| **Description** | Create `packages/agents/src/observability/agent-metrics.ts`. Auto-instrument agent task execution with: `agent.<id>.task.count` (counter), `agent.<id>.task.success_rate` (gauge, 0-1), `agent.<id>.task.duration_ms` (histogram), `agent.<id>.task.error_count` (counter). Hook into task bus state transitions. |
| **Inputs** | AF-081 (metric collector), AF-011 (task state machine) |
| **Outputs** | `AgentMetrics` class that attaches to task bus events |
| **Priority** | P1 |
| **Complexity** | M |
| **Status** | TODO |

### AF-083 -- Implement stage-level metrics

| Field | Value |
|-------|-------|
| **Description** | Create `packages/agents/src/observability/stage-metrics.ts`. Track: agents per stage (gauge), stage transitions per day (counter), gate pass/fail rate per stage (gauge), average time in stage (histogram). |
| **Inputs** | AF-081 (metric collector), AF-034 (stage transition log) |
| **Outputs** | `StageMetrics` class |
| **Priority** | P2 |
| **Complexity** | M |
| **Status** | TODO |

### AF-084 -- Implement portfolio-level metrics

| Field | Value |
|-------|-------|
| **Description** | Create `packages/agents/src/observability/portfolio-metrics.ts`. Aggregate metrics across all agents: total task throughput, overall success rate, agent count by maturity level, capability coverage (task types with qualified agents vs unassigned). |
| **Inputs** | AF-082 (agent metrics), AF-023 (registry index) |
| **Outputs** | `PortfolioMetrics` class |
| **Priority** | P2 |
| **Complexity** | M |
| **Status** | TODO |

### AF-085 -- Implement alert rules engine

| Field | Value |
|-------|-------|
| **Description** | Create `packages/agents/src/observability/alerts.ts`. Define alert rules in YAML: `agents/foundry/alerts.yaml`. Each rule: `name`, `metric`, `condition` (e.g., `> 0.1`), `window` (e.g., `5m`), `severity: warning|critical`, `action: log|slack|task`. Evaluate rules against metric collector on flush. |
| **Inputs** | AF-081 (metric collector) |
| **Outputs** | `AlertRulesEngine` class, `agents/foundry/alerts.yaml` |
| **Priority** | P2 |
| **Complexity** | L |
| **Status** | TODO |

### AF-086 -- Implement observability dashboard (CLI/JSON)

| Field | Value |
|-------|-------|
| **Description** | Add `agents observe` subcommand. Commands: `agents observe health` (all agents), `agents observe agent <id>` (single agent metrics), `agents observe stages` (pipeline view), `agents observe portfolio` (aggregate KPIs). Output as table or `--json` for piping. |
| **Inputs** | AF-082 through AF-084 |
| **Outputs** | Extended CLI with `observe` subcommand |
| **Priority** | P2 |
| **Complexity** | M |
| **Status** | TODO |

### AF-087 -- Implement trace correlation

| Field | Value |
|-------|-------|
| **Description** | Create `packages/agents/src/observability/trace.ts`. Generate W3C Trace Context compatible trace IDs. Propagate `traceparent` header through task bus. Link task bus `correlation_id` to OTLP trace ID. Export spans in OTLP-compatible format for future Azure Monitor integration. |
| **Inputs** | AF-016 (correlation ID propagation), AF-081 (metric collector) |
| **Outputs** | `TraceContext` class with `startSpan()`, `endSpan()`, `exportSpans()` methods |
| **Priority** | P2 |
| **Complexity** | L |
| **Status** | TODO |

### AF-088 -- Implement SLA/SLO tracking

| Field | Value |
|-------|-------|
| **Description** | Create `packages/agents/src/observability/slo.ts`. Define SLOs per agent in passport (e.g., `p99_latency_ms: 5000`, `success_rate: 0.99`). Track actual vs target. Report SLO burn rate. Alert when error budget is exhausted. |
| **Inputs** | AF-082 (agent metrics), AF-020 (AgentPassport with SLO fields) |
| **Outputs** | `SLOTracker` class with `checkBudget(agentId): SLOStatus` method |
| **Priority** | P2 |
| **Complexity** | L |
| **Status** | TODO |

---

## Phase 7: Portfolio Governance

Implement portfolio-level oversight and planning tools.

### AF-090 -- Implement portfolio registry

| Field | Value |
|-------|-------|
| **Description** | Create `packages/agents/src/portfolio/registry.ts`. Aggregate view over all registered agents grouped by domain. Methods: `byDomain()`, `byMaturity()`, `byStage()`, `coverage()` (which task types have qualified agents). Reads from agent registry, does not duplicate data. |
| **Inputs** | AF-021 (agent registry), AF-023 (registry index) |
| **Outputs** | `PortfolioRegistry` class |
| **Priority** | P1 |
| **Complexity** | M |
| **Status** | TODO |

### AF-091 -- Define portfolio KPI schema

| Field | Value |
|-------|-------|
| **Description** | Create `packages/agents/src/schemas/portfolio-kpi.schema.json`. KPIs: `agent_count` (by domain, by maturity), `capability_coverage` (task types served / total defined), `promotion_velocity` (avg days between promotions), `incident_rate`, `eval_pass_rate`. |
| **Inputs** | AF-090 (portfolio registry) |
| **Outputs** | JSON Schema file + generated TypeScript type |
| **Priority** | P1 |
| **Complexity** | S |
| **Status** | TODO |

### AF-092 -- Implement technical debt tracker

| Field | Value |
|-------|-------|
| **Description** | Create `packages/agents/src/portfolio/tech-debt.ts`. Track: agents past grace period without evals, agents at L1 for > 30 days, orphan skills (not bound to any agent), deprecated agents past sunset date, broken gate criteria. Store debt items at `agents/portfolio/tech-debt.yaml`. |
| **Inputs** | AF-090 (portfolio registry), AF-029 (registry health) |
| **Outputs** | `TechDebtTracker` class with `scan(): TechDebtItem[]` method |
| **Priority** | P1 |
| **Complexity** | M |
| **Status** | TODO |

### AF-093 -- Implement capacity model

| Field | Value |
|-------|-------|
| **Description** | Create `packages/agents/src/portfolio/capacity.ts`. Given the current agent roster and task throughput metrics, calculate: max concurrent tasks per agent, bottleneck agents (highest queue depth), underutilized agents (< 10% capacity), task types with no capable agent. |
| **Inputs** | AF-090 (portfolio registry), AF-082 (agent metrics), AF-013 (task queue) |
| **Outputs** | `CapacityModel` class with `analyze(): CapacityReport` method |
| **Priority** | P2 |
| **Complexity** | L |
| **Status** | TODO |

### AF-094 -- Implement prioritization framework

| Field | Value |
|-------|-------|
| **Description** | Create `packages/agents/src/portfolio/prioritization.ts`. Score each agent by: business impact (owner-assigned weight), tech debt severity, promotion readiness (how close to next level), dependency count (how many other agents depend on its task types). Output sorted priority list for investment decisions. |
| **Inputs** | AF-090 (portfolio registry), AF-092 (tech debt tracker) |
| **Outputs** | `prioritizeAgents(): PrioritizedAgent[]` function |
| **Priority** | P2 |
| **Complexity** | M |
| **Status** | TODO |

### AF-095 -- Implement portfolio health report

| Field | Value |
|-------|-------|
| **Description** | Create `packages/agents/src/portfolio/health-report.ts`. Aggregate report combining: registry health, KPIs, tech debt summary, capacity status, alert summary. Output as structured JSON and human-readable table. Save to `docs/evidence/<timestamp>/portfolio/health.json`. |
| **Inputs** | AF-029 (registry health), AF-091 (KPIs), AF-092 (tech debt), AF-093 (capacity) |
| **Outputs** | `generatePortfolioReport(): PortfolioHealthReport` function |
| **Priority** | P1 |
| **Complexity** | L |
| **Status** | TODO |

### AF-096 -- Implement governance policy engine

| Field | Value |
|-------|-------|
| **Description** | Create `packages/agents/src/portfolio/governance.ts`. Enforce portfolio-level policies: max agents per domain, min eval coverage per domain, mandatory judge for L3+ promotions, sunset compliance. Load policies from `agents/foundry/policies/governance.yaml`. Return violations list. |
| **Inputs** | AF-090 (portfolio registry), constitution section 10 (policy framework) |
| **Outputs** | `GovernanceEngine` class with `enforce(): PolicyViolation[]` method |
| **Priority** | P1 |
| **Complexity** | L |
| **Status** | TODO |

---

## Phase 8: Retirement Workflows

Implement the formal agent retirement lifecycle.

### AF-100 -- Implement retirement request schema and class

| Field | Value |
|-------|-------|
| **Description** | Create `packages/agents/src/retirement/request.ts`. Implements `ipai.retirement.v1` schema. Fields: `agent_id`, `reason`, `successor_agent_id` (nullable), `requested_by`, `requested_at`. Validates that successor (if specified) is at L2+ per constitution section 7.1. |
| **Inputs** | AF-006 (retirement record schema), AF-020 (AgentPassport) |
| **Outputs** | `RetirementRequest` class |
| **Priority** | P1 |
| **Complexity** | S |
| **Status** | TODO |

### AF-101 -- Implement sunset countdown

| Field | Value |
|-------|-------|
| **Description** | Create `packages/agents/src/retirement/sunset.ts`. When an agent enters S14 (deprecation-notice), start a 30-day countdown. Track: `sunset_start`, `sunset_end` (computed), `days_remaining`, `is_expired`. Method `checkSunset(agentId): SunsetStatus` returns current countdown state. |
| **Inputs** | AF-100 (retirement request), AF-020 (AgentPassport) |
| **Outputs** | `SunsetTracker` class |
| **Priority** | P1 |
| **Complexity** | S |
| **Status** | TODO |

### AF-102 -- Implement task bus drain for retiring agents

| Field | Value |
|-------|-------|
| **Description** | Create `packages/agents/src/retirement/drain.ts`. When agent enters S15 (sunset): (1) remove agent from routing table, (2) allow in-flight tasks to complete (do not cancel), (3) reject new tasks with `AGENT_RETIRED` error code, (4) report drain status: `pending_tasks`, `completed_tasks`, `drained: bool`. |
| **Inputs** | AF-012 (task router), AF-014 (routing rules engine), AF-013 (task queue) |
| **Outputs** | `TaskBusDrain` class with `initiate(agentId)`, `status(agentId): DrainStatus` methods |
| **Priority** | P1 |
| **Complexity** | L |
| **Status** | TODO |

### AF-103 -- Implement dependent agent notification

| Field | Value |
|-------|-------|
| **Description** | Create `packages/agents/src/retirement/notify-dependents.ts`. When retirement request is filed, identify agents that route tasks to the retiring agent (via routing rules). Emit `task.platform.agent-deprecation-notice` to each dependent agent. Log notification status. |
| **Inputs** | AF-100 (retirement request), AF-014 (routing rules), AF-010 (TaskEnvelope) |
| **Outputs** | `DependentNotifier` class with `notify(agentId): NotificationResult[]` method |
| **Priority** | P2 |
| **Complexity** | M |
| **Status** | TODO |

### AF-104 -- Implement retirement record writer

| Field | Value |
|-------|-------|
| **Description** | Create `packages/agents/src/retirement/record.ts`. After drain completes and sunset period expires, write final retirement record to `agents/retirements/<agent-id>/retirement-record.yaml`. Record is append-only (per constitution P13). Move passport to `agents/passports/retired/`. |
| **Inputs** | AF-100 (retirement request), AF-102 (drain), AF-101 (sunset) |
| **Outputs** | `RetirementRecordWriter` class with `finalize(agentId): RetirementRecord` method |
| **Priority** | P1 |
| **Complexity** | M |
| **Status** | TODO |

### AF-105 -- Implement cleanup automation

| Field | Value |
|-------|-------|
| **Description** | Create `packages/agents/src/retirement/cleanup.ts`. Post-retirement cleanup: (1) archive passport to `retired/`, (2) remove agent from active routing rules, (3) mark eval history as archived (not deleted), (4) update registry to `current_stage: S16`. Do not delete any files -- archive only. |
| **Inputs** | AF-104 (retirement record), AF-021 (agent registry) |
| **Outputs** | `RetirementCleanup` class with `execute(agentId): CleanupResult` method |
| **Priority** | P2 |
| **Complexity** | M |
| **Status** | TODO |

### AF-106 -- Implement post-retirement audit

| Field | Value |
|-------|-------|
| **Description** | Create `packages/agents/src/retirement/audit.ts`. Verify retirement was clean: passport archived, no tasks still routing, routing rules updated, retirement record valid, successor (if any) is at L2+. Returns `RetirementAuditResult` with pass/fail per check. |
| **Inputs** | AF-104 (retirement record), AF-102 (drain status), AF-021 (registry) |
| **Outputs** | `auditRetirement(agentId): RetirementAuditResult` function |
| **Priority** | P2 |
| **Complexity** | M |
| **Status** | TODO |

---

## Summary

| Phase | Task Range | Count | P0 | P1 | P2 |
|-------|-----------|-------|----|----|-----|
| 0: Foundations | AF-001 -- AF-008 | 8 | 7 | 0 | 1 |
| 1: Task Bus | AF-010 -- AF-019 | 10 | 4 | 4 | 2 |
| 2: Registry + Passports | AF-020 -- AF-029 | 10 | 3 | 5 | 2 |
| 3: Assembly Line Stages | AF-030 -- AF-038 | 9 | 3 | 3 | 3 |
| 4: Evaluations + Judges | AF-050 -- AF-060 | 11 | 4 | 4 | 3 |
| 5: Promotion / Release | AF-070 -- AF-078 | 9 | 3 | 3 | 3 |
| 6: Observability | AF-080 -- AF-088 | 9 | 0 | 3 | 6 |
| 7: Portfolio Governance | AF-090 -- AF-096 | 7 | 0 | 4 | 3 |
| 8: Retirement | AF-100 -- AF-106 | 7 | 0 | 4 | 3 |
| **Total** | | **80** | **24** | **30** | **26** |

### Dependency Chain (Critical Path)

```
AF-001 (types) ──> AF-003 (task schema) ──> AF-010 (envelope) ──> AF-011 (state machine)
                                                                       │
AF-004 (passport schema) ──> AF-020 (passport class) ──> AF-021 (registry) ──> AF-032 (gate engine)
                                                              │                       │
                                                         AF-026/027 (migrate agents)  AF-052 (eval runner)
                                                                                       │
                                                                                  AF-071 (promotion controller)
```

### Phase Dependencies

- Phase 1 (Task Bus) depends on Phase 0
- Phase 2 (Registry) depends on Phase 0
- Phase 3 (Stages) depends on Phase 0 + partial Phase 2
- Phase 4 (Evals) depends on Phase 1 + Phase 2 + Phase 3
- Phase 5 (Promotions) depends on Phase 3 + Phase 4
- Phase 6 (Observability) depends on Phase 1 + Phase 2
- Phase 7 (Portfolio) depends on Phase 2 + Phase 6
- Phase 8 (Retirement) depends on Phase 1 + Phase 2 + Phase 3

Phases 1 and 2 can execute in parallel after Phase 0 completes.
Phases 6, 7, and 8 can execute in parallel after their dependencies are met.

---

*Schema version: 1.0*
*Created: 2026-03-19*
*Companion: `spec/agent-factory/constitution.md`*
*Owner: @Insightpulseai-net/platform*
