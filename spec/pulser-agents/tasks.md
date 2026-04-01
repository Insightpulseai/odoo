# Tasks — Pulser Assistant: Runtime Layer

## Phase 1 — Agent and Workflow Templates

- [ ] Define PulserAgentTemplate contract (system prompt, tools, memory, capability package ref)
- [ ] Define PulserWorkflowTemplate contract (graph definition, checkpoints, HITL gates, capability package ref)
- [ ] Create finance-analyst agent template (open-ended financial Q&A)
- [ ] Create erp-operations agent template (Odoo read/write with safety middleware)
- [ ] Create close-orchestration workflow template (5-phase month-end close)
- [ ] Create collections-coordination workflow template (AR follow-up sequence)
- [ ] Document agent vs. workflow decision criteria

## Phase 2 — Tool Bindings

- [ ] Define PulserToolBinding contract (name, description, input/output schema, safety classification)
- [ ] Create Odoo tool bindings: account.move read, partner lookup, bank reconciliation, invoice create
- [ ] Create platform tool bindings: formation query, capability status, grounding source list
- [ ] Create data-intelligence tool bindings: Gold mart query (finance, sales, spend)
- [ ] Register all tool bindings in Foundry tool catalog

## Phase 3 — Context and Memory

- [ ] Define PulserContextProvider contract (session, record, grounding, permission contexts)
- [ ] Implement session context provider (conversation history, user prefs)
- [ ] Implement record context provider (Odoo model/record awareness)
- [ ] Implement grounding context provider (available sources from platform registry)
- [ ] Implement permission context provider (role, trust level, available actions)

## Phase 4 — Safety Middleware

- [ ] Define PulserSafetyMiddleware contract (pre/post execution hooks, policy types)
- [ ] Implement content safety middleware (Foundry content safety integration)
- [ ] Implement permission check middleware (action classification against user trust level)
- [ ] Implement finance safety middleware (strict mode for journal entries, payments, tax filings)
- [ ] Implement audit logging middleware (all actions attributed and logged)

## Phase 5 — Evaluations

- [ ] Define PulserEvalSuite contract (dataset, runner, thresholds, evidence output)
- [ ] Create finance-analyst eval suite (accuracy, grounding, safety)
- [ ] Create erp-operations eval suite (action safety, permission enforcement, correctness)
- [ ] Wire eval results as promotion gate (no production without passing evals)
- [ ] Add eval execution to AzDO pipeline

## Phase 6 — Interoperability

- [ ] Define MCP server adapter (expose Pulser tools as MCP)
- [ ] Define A2A agent endpoint (interoperable agent exposure)
- [ ] Define REST API adapter (direct HTTP access for web clients)
- [ ] Test MCP interop with at least one external consumer
- [ ] Add DevUI-like internal test harness for agent/workflow debugging

## Verification Gates

- [ ] At least one agent template and one workflow template operational
- [ ] Tool bindings operational for Odoo, platform, and data-intelligence
- [ ] Safety middleware active on all finance-sensitive actions
- [ ] Eval suites passing for all promoted capability packages
- [ ] MCP/A2A interop operational
- [ ] DevUI-like harness available for dev/test
- [ ] Agent vs. workflow distinction enforced in all templates

### Phase R5 — Tax Guru Agent Runtime

- [ ] R5.1 — Implement PulserTaxDeterminationRequest schema and intake workflow
- [ ] R5.2 — Implement PulserTaxDeterminationResult with treatment recommendation, confidence, evidence binding
- [ ] R5.3 — Implement PulserTaxPolicyAnswer retrieval workflow (grounding sources → context assembly → answer + evidence)
- [ ] R5.4 — Implement PulserTaxActionProposal with default suggest_only mode and approval escalation
- [ ] R5.5 — Create tax eval suite: determination accuracy, safety checks, escalation correctness
- [ ] R5.6 — Integrate PH-first tax rules: VAT/non-VAT, withholding classifications, BIR guidance
- [ ] R5.7 — Add capability-type routing: informational/navigational/transactional with distinct safety profiles
