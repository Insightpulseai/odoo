# Agent Guided Learning Paths

> Canonical learning progression for building, testing, and operating agents.
> SSOT: `agent-platform/ssot/learning/agent_guided_learning_paths.yaml`

## Purpose

Define the staged learning path using:
- Microsoft Foundry VS Code extension (project fluency, model deployment, playgrounds)
- Agent Framework local development/debugging (DevUI, traces)
- Foundry-hosted production runtime (managed agent deploy)

## Core rule

Train locally, validate in project context, promote to managed runtime.

---

## Lane 1 — Foundations

**Goal**: Understand the platform before touching tools.

Skills:
- Repo topology and platform planes
- What `agent-platform` owns vs `platform` vs `odoo` vs `data-intelligence`
- Maker vs judge agent roles
- Advisory vs operator boundary
- Foundry project model (project-scoped resources)

Artifacts:
- `docs/operating-model/CAF_TEAM_MODEL.md`
- `docs/operating-model/CAF_PREPARE_PEOPLE_COMPLETE.md`
- `docs/architecture/TARGET_ORG_PLATFORM_STRUCTURE.md`
- `ssot/governance/unified_strategy.yaml`

Exit criteria:
- [ ] Can explain where agents belong in the platform
- [ ] Can identify local-dev vs hosted-runtime boundary
- [ ] Can name the 8 platform planes and their repos

---

## Lane 2 — Foundry Project Fluency

**Goal**: Navigate and use a Foundry project in VS Code.

Skills:
- Install Foundry VS Code extension
- Sign into Azure and open the correct project (`data-intel-ph`)
- Navigate Resources section (deployed models, hosted agents, connections, vector stores)
- Navigate Tools section (Model Catalog, Model Playground, Agent Playgrounds, Local Visualizer)
- Switch default project

Exit criteria:
- [ ] Can open and navigate the correct Foundry project in VS Code
- [ ] Can identify deployed models, connections, and vector stores

---

## Lane 3 — Model Deployment and Code Generation

**Goal**: Deploy a model and generate working starter code.

Skills:
- Browse Model Catalog in VS Code
- Deploy a model to the project
- Inspect deployment info (endpoint, auth, API version)
- Generate sample code in preferred SDK/language
- Understand project endpoint vs model deployment

Exit criteria:
- [ ] One deployed model exists in the correct project
- [ ] Sample code is generated and runnable
- [ ] Can explain the difference between project endpoint and model deployment endpoint

---

## Lane 4 — Local Agent Experimentation

**Goal**: Build and test agents locally before production.

Skills:
- Use Agent Playground (local) in VS Code
- Use Local Visualizer for workflow inspection
- Run Agent Framework DevUI for trace-level debugging
- Test prompts, tool calls, and multi-agent flows
- Inspect OpenTelemetry traces for failure analysis

Exit criteria:
- [ ] A local agent workflow runs successfully
- [ ] Failure paths can be debugged and explained
- [ ] Tool calls are inspectable in traces

---

## Lane 5 — Hosted Agent Promotion

**Goal**: Move validated local patterns to hosted/managed runtime.

Skills:
- Deploy hosted agent via Foundry Agent Service
- Bind project resources (connections, vector stores, tools)
- Use Agent Playground (remote) to validate hosted behavior
- Verify runtime behavior matches local expectations

Exit criteria:
- [ ] Hosted agent is deployed and callable
- [ ] Project resources are correctly bound
- [ ] Remote playground confirms expected behavior

---

## Lane 6 — Governance and Production Readiness

**Goal**: Ensure agents are safe, observable, and aligned to platform doctrine.

Skills:
- Advisory vs operator boundary enforcement
- Auth/secret boundary awareness (no browser-side secrets)
- Evidence capture (`docs/evidence/<date>/`)
- Judge-agent review before promotion
- Agent classification (dev / staging / prod ready)

Exit criteria:
- [ ] Deployment evidence exists
- [ ] Security and governance checks are attached
- [ ] Agent is classified with production-readiness status
- [ ] Rollback path documented

---

## Learning surfaces summary

| Surface | Purpose | Production? |
|---|---|---|
| Foundry VS Code extension | Project navigation, model deploy, playgrounds | No (dev tool) |
| Agent Framework DevUI | Local agent debug, trace inspection | No (dev only) |
| Foundry Agent Service | Hosted agent runtime | Yes (production) |
| Azure DevOps MCP | Live Board/PR/build context for agents | Yes (tool layer) |
