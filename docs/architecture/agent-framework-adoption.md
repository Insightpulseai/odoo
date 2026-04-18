# Microsoft Agent Framework — Adoption & Placement Contract

**Status**: canonical
**Authority**: [ssot/agent-platform/agent_framework_adoption.yaml](../../ssot/agent-platform/agent_framework_adoption.yaml)
**CLAUDE.md**: invariant #10a
**Upstream**: https://github.com/microsoft/agent-framework

---

## Decision

Microsoft Agent Framework (MAF) is the canonical **runtime substrate** of
`agent-platform/`. Python-first, `src/` layout Python package
(`agent_platform`). Foundry is the default model/provider lane. Odoo,
Databricks, Document Intelligence, storage, and communications are typed
**tool adapters** under `src/agent_platform/tools/`. MAF is **not** adopted
inside `agents/`, `odoo/`, `platform/`, or `infra/`.

This aligns with the Engineering Execution Doctrine: MAF is commodity
substrate (Python + .NET, graph workflows, Foundry auth, OpenTelemetry,
checkpoints) — adopt upstream and build only the thinnest IPAI delta on top.

---

## Repository responsibility model

| Repo | Owns | Does NOT own |
|---|---|---|
| [agent-platform/](../../agent-platform/) | runtime engine, orchestration, session state, retrieval execution, Foundry provider, tool adapters (Odoo/Databricks/DocIntel/storage/comms), eval runtime, telemetry, security policy enforcement | persona text, prompts, judge criteria, eval fixtures, skill registries, mailbox/user identity logic |
| [agents/](../../agents/) | personas, prompts, judges, eval scenario definitions, tool metadata, maturity/policy metadata | runtime code, framework imports, execution loops |
| [platform/](../../platform/) | tenant metadata, app bindings, env config registry, secret references, feature flags | runtime or framework code |
| [addons/](../../addons/) (Odoo) | ERP runtime, business data, Odoo module surfaces, agent-consumable APIs | orchestration core, agent runtime |

**Mental model:**
- `agent-platform/` = engine
- `agents/` = manifests/contracts loaded by the engine
- `platform/` = tenant/env state the engine reads
- `addons/` = ERP tool surface the engine calls

---

## Canonical target tree for `agent-platform/`

```
agent-platform/
├── README.md
├── pyproject.toml
├── uv.lock
├── .env.example
├── .python-version
├── azure-pipelines.yml            # main deploy (CANONICAL CI/CD authority)
├── azure-pipelines-pr.yml         # PR validation
├── azure-pipelines-eval-gate.yml  # eval-gate promotion
├── .github/workflows/
│   ├── ci.yml                     # ruff + mypy + pytest (SCOPED EXCEPTION, PR only)
│   └── contract-checks.yml        # SSOT contract validation (PR only)
├── docs/
│   ├── architecture/
│   │   ├── RUNTIME_OVERVIEW.md
│   │   ├── TOOL_ADAPTER_MODEL.md
│   │   ├── IDENTITY_AND_AUTH.md
│   │   ├── SESSION_MODEL.md
│   │   └── OBSERVABILITY.md
│   ├── runbooks/
│   │   ├── LOCAL_DEV.md
│   │   ├── DEPLOYMENT.md
│   │   ├── ROLLBACK.md
│   │   └── INCIDENT_RESPONSE.md
│   └── evidence/
├── spec/agent-platform-runtime/
│   ├── constitution.md
│   ├── prd.md
│   ├── plan.md
│   └── tasks.md
├── ssot/
│   ├── runtime/
│   │   ├── services.yaml
│   │   ├── agents.yaml
│   │   ├── tools.yaml
│   │   ├── models.yaml
│   │   ├── sessions.yaml
│   │   └── environments.yaml
│   ├── security/
│   │   ├── auth_policy.yaml
│   │   ├── role_bindings.yaml
│   │   └── allowed_tools.yaml
│   └── eval/
│       ├── gates.yaml
│       ├── scenarios.yaml
│       └── score_thresholds.yaml
├── src/agent_platform/
│   ├── __init__.py
│   ├── config.py
│   ├── logging.py
│   ├── settings.py
│   ├── main.py
│   ├── api/                 # FastAPI surface: health, chat, sessions, attachments, admin
│   ├── runtime/             # engine, registry, loader, lifecycle, graph_builder, middleware, checkpointing
│   ├── orchestration/       # router, planner, supervisor, handoffs, human_in_loop, policies
│   ├── providers/
│   │   ├── foundry/         # client, auth, models, embeddings  ← DEFAULT
│   │   └── fallback/        # null_provider
│   ├── tools/
│   │   ├── base.py
│   │   ├── registry.py
│   │   ├── contracts.py
│   │   ├── validators.py
│   │   ├── odoo/            # client, auth, sales, accounting, crm, documents
│   │   ├── databricks/      # sql, jobs, unity_catalog
│   │   ├── docintel/        # extract, classify
│   │   ├── storage/         # blobs, artifacts
│   │   └── communications/  # email, notifications
│   ├── retrieval/           # ingestion, chunking, indexing, reranking, grounding, citations
│   ├── attachments/         # pipeline, normalization, mime, virus_scan
│   ├── sessions/            # store, memory, transcripts, state_machine
│   ├── evals/               # runner, fixtures, assertions, scorecards, report
│   ├── observability/       # tracing, metrics, correlation, audit
│   ├── security/            # authz, tenant_policy, pii, secrets, content_filters
│   └── workers/             # ingestion_worker, eval_worker, artifact_worker
├── tests/{unit,integration,contract,eval,fixtures}/
├── apps/dev-console/
├── scripts/{dev,ci,release}/
├── infra/{aca,identities,monitor,env}/
└── docker/{Dockerfile, Dockerfile.dev, compose.yaml}
```

---

## Boundary rules

### Import boundary

`agent_framework`, `agent_framework.*`, and `agent-framework-azure-ai` imports
are permitted **only** under `agent-platform/src/agent_platform/`.

Forbidden paths (doctrine violation if `agent_framework` appears):

```
agents/**
odoo/**
addons/**
platform/**
infra/**
data-intelligence/**
apps/**
```

Enforcement: `azure-pipelines-contract-checks.yml` runs a ruff rule / grep
gate that fails the build if forbidden imports are detected.

### CI/CD placement (per CLAUDE.md authority split)

- **Azure Pipelines** = sole deploy authority.
  - `azure-pipelines.yml` — main deploy.
  - `azure-pipelines-pr.yml` — PR validation.
  - `azure-pipelines-eval-gate.yml` — eval-gate promotion.
  - `azure-pipelines-contract-checks.yml` — SSOT contract validation.
- **GitHub Actions** = scoped exception for PR-only pre-merge validation.
  - `.github/workflows/ci.yml` — ruff + mypy + pytest on PR.
  - Never runs deploys, never holds secrets, billing routed through Azure
    subscription.

---

## Provider model

| Provider | Default | Module |
|---|---|---|
| Foundry | ✅ DEFAULT | `src/agent_platform/providers/foundry/` |
| Foundry Local (solo mode) | env-swap | same module, different endpoint via `AZURE_AI_FOUNDRY_ENDPOINT` |
| Fallback | null | `src/agent_platform/providers/fallback/null_provider.py` |

Authentication: Managed Identity → Foundry via `azure-identity`. Never inline
secrets. Key Vault reference for any non-MI auth path.

Operating modes (per CLAUDE.md #10a):

| Mode | Context | Provider target |
|---|---|---|
| Team | Codespaces / ACA | Foundry cloud (`ipai-copilot-resource`, `gpt-4.1`) |
| Solo | Local Mac devcontainer | Foundry Local (`phi-4` / `qwen`) on-device |

Forbidden: Foundry Local inside Codespaces.

---

## Tool adapter model

Tools are **typed adapters**, not prompt blobs. Each tool:

1. Inherits from `agent_platform.tools.base.Tool`.
2. Declares request/response schema via `agent_platform.tools.contracts`.
3. Validates inputs via `agent_platform.tools.validators` before execution.
4. Reports traces via `agent_platform.observability.tracing`.
5. Enforces RBAC via `agent_platform.security.authz` before side effects.

Example: `src/agent_platform/tools/odoo/sales.py` exposes `create_sale_order`,
`search_customer`, etc. — each a typed adapter, not a prompt.

---

## Eval lane

Eval is a **first-class runtime concern**, not a test afterthought.

- **Deterministic fixtures** → `src/agent_platform/evals/fixtures.py`
- **Runtime assertions** → `src/agent_platform/evals/assertions.py`
- **Scorecards** → `src/agent_platform/evals/scorecards.py`
- **Report generation** → `src/agent_platform/evals/report.py`
- **Gates** → `ssot/eval/gates.yaml` defines promotion thresholds
- **Azure pipeline** → `azure-pipelines-eval-gate.yml` blocks promotion on
  threshold failure

---

## Migration phases

### Phase 1 — Scaffold minimal runnable skeleton (this PR)

- `pyproject.toml`, `README.md`, `.env.example`, `.python-version`
- `spec/agent-platform-runtime/{constitution,prd,plan,tasks}.md`
- `ssot/runtime/{agents,tools,models,environments}.yaml` seeds
- `ssot/security/{auth_policy,role_bindings,allowed_tools}.yaml` seeds
- `ssot/eval/{gates,scenarios,score_thresholds}.yaml` seeds
- `src/agent_platform/` Python package with:
  - `main.py`, `settings.py`, `__init__.py`
  - `runtime/` with `engine.py`, `registry.py`, `graph_builder.py`
  - `orchestration/` with `router.py`, `supervisor.py`
  - `providers/foundry/` with `auth.py`, `client.py`
  - `tools/` with `base.py`, `registry.py`
  - `tools/odoo/` with `client.py`, `sales.py`, `accounting.py`
  - `evals/` with `runner.py`, `scorecards.py`
  - `observability/` with `tracing.py`, `metrics.py`
- `tests/{unit,integration,contract}/` with smoke tests
- Azure Pipelines: add `azure-pipelines-contract-checks.yml`
- GHA scoped exception: `.github/workflows/ci.yml` (ruff + mypy + pytest)

### Phase 2 — Migrate existing code

- `agent-platform/src/orchestration/**` → `src/agent_platform/orchestration/`
- `agent-platform/src/runtime/**` → `src/agent_platform/runtime/`
- `agent-platform/src/tools/**` → `src/agent_platform/tools/`
- `agent-platform/src/policy/**` → `src/agent_platform/security/`
- Refactor `agent-platform/agents/release-manager/agent_orchestrator.py` to
  consume `agent_platform.runtime` instead of importing `agent_framework`
  directly.

### Phase 3 — Boundary enforcement

- Azure Pipelines `contract-checks` job blocks forbidden `agent_framework`
  imports outside `agent-platform/src/agent_platform/`.
- Add eval gate to `azure-pipelines-eval-gate.yml` reading `ssot/eval/gates.yaml`.

---

## Non-goals

- Not replacing supervisor-mediated orchestration pattern.
- Not importing MAF outside `agent-platform/`.
- Not forking MAF.
- Not adopting MAF as the M365 surface protocol (Agent365 SDK owns M365).
- Not mixing mailbox/user identity logic into runtime orchestration.

---

## Appendix A — Upstream reference crosswalk

The `microsoft-foundry` GitHub org is **reference material only** — samples,
labs, starter apps, and event demos. Do **not** mirror its repo layout into
the InsightPulseAI org. Our existing topology (`agent-platform`, `agents`,
`platform`, `infra`, `web`, `data-intelligence`, `addons`, `design`, `docs`)
is already more production-oriented than the Microsoft sample layout.

Use upstream repos as source inputs for specific InsightPulseAI targets:

| Upstream repo | Role in Microsoft's org | InsightPulseAI target | What to adopt |
|---|---|---|---|
| `microsoft/agent-framework` | SDK / runtime substrate | `agent-platform/` | Runtime primitives: `Agent`, `SequentialBuilder`, `GraphBuilder`, `AzureAIAgentClient`, checkpoint storage, OpenTelemetry wiring |
| `microsoft-foundry/foundry-samples` | education / integration examples | `agent-platform/src/agent_platform/providers/foundry/`, `agent-platform/src/agent_platform/tools/` | Foundry auth patterns, hosted-tool invocation, multi-agent orchestration idioms |
| `microsoft-foundry/foundry-agent-webapp` | starter web app | `web/` | Entra-authenticated chat UI, session UI, attachment UX |
| `microsoft-foundry/Foundry-Local-Lab` | local dev pattern | `agent-platform/` (solo mode) | Local provider swap, on-device NPU/GPU routing via `AZURE_AI_FOUNDRY_ENDPOINT` |
| `microsoft-foundry/Foundry_Toolkit_for_VSCode_Lab` | workshop / VS Code dev loop | `agent-platform/docs/runbooks/LOCAL_DEV.md` | Developer ergonomics for hosted agents |
| `microsoft-foundry/mcp-foundry` | MCP + Foundry experimentation | `agent-platform/src/agent_platform/tools/mcp` (future) | MCP-Foundry integration patterns |
| `microsoft-foundry/foundry-mcp-playground` | exploration surface | (reference only) | Do not clone; consult when adding new MCP-tool patterns |
| `microsoft-foundry/new-foundry-portal` | experimentation | (reference only) | Do not clone |
| `microsoft-foundry/build-2025-demos`, `microsoft-ignite-25-demos` | event assets | (reference only) | Do not clone |
| `microsoft-foundry/discussions`, `.github` | community scaffolding | (reference only) | Do not clone |

**Rule**: do not create parallel InsightPulseAI repos for workshops, demos,
event assets, or playgrounds. Those exist in Microsoft's org because they
publish to a broad audience; we operate a governed delivery platform, not a
tutorial ecosystem.

---

## References

- SSOT: [ssot/agent-platform/agent_framework_adoption.yaml](../../ssot/agent-platform/agent_framework_adoption.yaml)
- Orchestration model: [agent-orchestration-model.md](agent-orchestration-model.md)
- Three-protocol model: [three-protocol-model.md](three-protocol-model.md)
- MCP policy: [../../ssot/agent-platform/mcp_policy.yaml](../../ssot/agent-platform/mcp_policy.yaml)
- Agent factory (definitions): [../../ssot/agents/agent_factory.yaml](../../ssot/agents/agent_factory.yaml)
- Spec bundle: [../../agent-platform/spec/agent-platform-runtime/](../../agent-platform/spec/agent-platform-runtime/)
- Upstream MAF: https://github.com/microsoft/agent-framework
- Upstream Foundry samples: https://github.com/microsoft-foundry
