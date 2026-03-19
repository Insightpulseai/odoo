# Agent Platform Production Plan

> Version: 0.1.0
> Date: 2026-03-19
> Status: Phase 0-2 done, Phase 3-4 partial, Phase 5-6 next
> Build: PASS | Tests: 6/6 PASS | Cloud: BLOCKED

## Architecture

```
agents/                          agent-platform/
(design-time assets)             (runtime execution)

foundry/ipai-odoo-copilot-azure/ ──→ packages/builder-orchestrator/
  system-prompt.md                     AssetLoader (reads agents/ at init)
  tool-definitions.json                PolicyEngine (enforces guardrails)
  guardrails.md                        Orchestrator (ties it all together)
  context-envelope-contract.md         ConsoleAuditEmitter (observability)
  telemetry-contract.md
  metadata.yaml                  ──→ packages/builder-contract/
                                       ContextEnvelope, PrecursorRequest,
foundry/policies/                      PrecursorResponse, ToolDefinition,
  tool_allowlist.yaml                  AuditEvent, EvalRunResult,
  finance_tool_allowlist.yaml          SpecialistRouter

evals/odoo-copilot/              ──→ packages/builder-evals/
  thresholds.yaml                      EvalRunner, loadEvalDataset
  rubric.md                            generateEvidencePack
  dataset.jsonl
  datasets/eval-dataset-v2.json  ──→ packages/builder-foundry-client/
                                       FoundryClient (interface)
knowledge-base/                        MockFoundryClient (local dev)
  bir-compliance/                      AzureFoundryClient (production stub)
  finance-close-kb/
  general-kb/                    ──→ packages/builder-runner/
  marketing-playbooks/                 CLI: chat, health, eval, status

                                 ──→ apps/builder-factory/
                                       Precursor gateway + smoke tests
```

## Package Dependency Graph

```
builder-contract (types only, no deps)
    ↑
builder-foundry-client (depends on contract)
    ↑
builder-orchestrator (depends on contract + foundry-client)
    ↑
builder-evals (depends on contract + orchestrator)
    ↑
builder-runner (depends on all)
    ↑
builder-factory (app, depends on all)
```

## Request Flow

```
1. Request arrives (PrecursorRequest with correlation ID)
2. Orchestrator loads agent assets from agents/ (cached after init)
3. PolicyEngine builds context envelope prefix
4. PolicyEngine filters tools by mode + permitted_tools
5. FoundryClient.chatCompletion() executes the model call
6. If tool calls returned, PolicyEngine checks each tool permission
7. Permitted tools executed (mock in v0.1, real in Stage 2)
8. AuditEmitter.emit() fires for request, response, tool events
9. PrecursorResponse returned with correlation ID, latency, tool records
```

## Fail-Closed Rules

| Rule | Implementation |
|------|---------------|
| Advisory mode blocks writes | PolicyEngine.checkToolPermission() |
| Unregistered specialist blocks routing | SpecialistRouter.route() |
| Non-ready specialist blocks routing | SpecialistRouter.route() checks production_ready |
| Foundry failure returns empty | Orchestrator.execute() catch block |
| Missing context defaults restrictive | defaultContextEnvelope() |
| PII requests refused | MockFoundryClient pattern matching (Stage 2: system prompt) |

## Benchmarks

| Benchmark | Role | Status |
|-----------|------|--------|
| SAP Joule | Primary precursor benchmark | Scoped — v0.1 covers read-only advisory |
| Notion 3.0 | Secondary (context-awareness) | Scoped — context envelope implemented |
| AvaTax | Tax specialist benchmark | Blocked — ATC namespace divergence |

## CI/CD

Azure DevOps is the sole CI/CD platform. No GitHub Actions.

Pipeline stages:
1. `npm install` — resolve workspace dependencies
2. `npm run build` — TypeScript compilation (all packages)
3. `npm run test` — smoke tests
4. Eval gate — `builder-runner eval`
5. Deploy — Container App update (Stage 2)

## Release Ladder

| Level | Status | Gate |
|-------|--------|------|
| Local Dev (mock) | **Ready** | TypeScript compiles, smoke tests pass |
| Cloud Dev (Foundry) | Blocked | AZURE_AI_FOUNDRY_ENDPOINT configured |
| Advisory Release | Blocked | 30+ eval pass, telemetry live |
| Grounded Advisory | Blocked | AI Search populated, Entra roles active |
| Assisted Actions | Blocked | Read-only tools wired to real Odoo |
| GA | Blocked | Write tools evaluated, security review |
