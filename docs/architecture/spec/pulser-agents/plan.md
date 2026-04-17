# Plan — Pulser Assistant: Runtime Layer

## Status
Draft

## Architecture Approach

### Directory Structure (Agent Framework-aligned)

```text
agents/
  pulser/
    templates/           # Capability-specific agent templates
      finance-analyst/
      erp-operations/
      collections/
      tax-compliance/
    workflows/           # Graph-based deterministic workflows
      close-orchestration/
      contract-review/
      bir-filing/
      collections-coordination/
    tools/               # Tool bindings for Odoo/platform/data-intelligence
      odoo/              # Odoo FastAPI endpoint bindings
      platform/          # Platform registry query bindings
      data-intelligence/ # Gold mart query bindings
    context/             # Session, memory, record-context providers
    middleware/          # Safety and policy middleware
    evals/               # Evaluation suites per capability package
      finance-analyst/
      erp-operations/
    interop/             # MCP server, A2A endpoints, API adapters
    hosting/             # Foundry Agent Service, ACA, Functions configs
```

### Agent vs. Workflow Design Rules

- **Use an agent** when the task is open-ended and tool-using (e.g., "analyze this variance")
- **Use a workflow** when the process has explicit steps, routing, and checkpoints (e.g., "execute month-end close")
- **Prefer deterministic routing** for regulated or finance-sensitive actions
- **Isolate tool adapters** from prompt logic — tools are shared across agents and workflows
- **All high-impact actions** must pass through safety middleware and eval contracts

### Context Provider Model

- **Session context**: Conversation history, user preferences, active formation
- **Record context**: Current Odoo record (model, ID, fields) when invoked from Odoo
- **Grounding context**: Available grounding sources from `platform` registry
- **Permission context**: User role, trust level, available actions from `platform` identity binding

### Safety Middleware

- Pre-execution: content safety, permission check, action classification
- Post-execution: result validation, evidence emission, audit logging
- Configurable per capability package (finance = strict, Q&A = standard)

### Hosting Model

- **Production**: Foundry Agent Service (managed hosting, enterprise controls)
- **Preview**: Foundry Agent Service (separate project or deployment slot)
- **Dev/Test**: Local DevUI-like harness, not publicly routed
- **Workflow hosting**: ACA or Foundry, depending on execution duration

## Design Principles

1. **Workflows for processes, agents for reasoning**: Deterministic business flows use workflow templates; open-ended Q&A uses agent templates
2. **Deterministic routing for regulated actions**: Finance-sensitive and compliance actions use explicit workflow routing, not emergent agent behavior
3. **Tool adapters isolated from prompts**: Odoo/platform/data-intelligence tool bindings are shared modules, not embedded in agent prompts
4. **Safety middleware mandatory**: All high-impact actions pass through configurable safety middleware
5. **Eval-gated capabilities**: No capability package promotes to production without passing eval suites
6. **Preview before production**: All new agent/workflow templates must pass through preview channel first
7. **Capability-type routing**: Agent runtime separates logic by capability type (informational/navigational/transactional) with distinct safety profiles
8. **Tax determination layer**: Tax Guru uses structured determination workflows, not just prompt-based reasoning

## Cross-Repo Dependencies

| Repo | `agents` consumes | `agents` exposes |
|------|-------------------|-----------------|
| `platform` | Formation metadata, capability package state, identity/permissions, grounding sources | Agent/workflow template metadata, eval results |
| `web` | — | Agent API endpoints (chat, workflow status), trace data |
| `odoo` | Odoo FastAPI endpoints (tool bindings) | Agent-initiated actions via tool calls |
| `data-intelligence` | Gold mart query endpoints | Analytics queries via tool bindings |

## Foundry Delegation

Per `docs/contracts/FOUNDRY_DELEGATION_CONTRACT.md`:
- Foundry owns: agent hosting, model deployment, memory management, tracing, evaluations infrastructure
- `agents` owns: agent/workflow templates, tool bindings, context providers, safety middleware, eval datasets, interop adapters

### Phase R5 — Tax Guru Agent Runtime

- Implement PulserTaxDeterminationRequest/Result workflow (jurisdiction lookup → tax type → taxability → exception → evidence)
- Implement PulserTaxPolicyAnswer contract (retrieval + grounding + evidence bundle)
- Implement PulserTaxActionProposal contract (suggest_only default, approval escalation)
- Add tax-specific eval suite (accuracy, safety, escalation correctness)
- Integrate with PH-first tax rules (VAT/non-VAT, withholding, BIR guidance)

### Phase R6 — PH Source Selection and Citation Engine

- Implement 6-tier source-selection policy (BIR legal → BIR guidance → BIR execution → CGPA competency → Odoo execution → internal context)
- Implement 5 answer-type contracts: explanation, recommendation, navigation, action_proposal, exception_review
- Implement PulserPHCitation assembly in retrieval pipeline with three citation groups (authoritative, supporting, execution_model)
- Add "no unsupported legal conclusion without citation" rule to safety middleware
- Add authority_conflict detection (Tier 1 vs Tier 6 divergence → exception case with `conflicting_sources`)
- Implement capability-to-source mapping enforcement (per-package minimum authority tier)
- Add citation completeness eval: every tax answer must have evidence bundle with ≥1 citation
- Add authority tier eval: compliance answers without Tier 1-2 authoritative_citations must flag unsupported
- Integrate CGPA CBOK as Tier 4 reasoning context (evaluative only, never legal authority)
- Integrate Odoo 18 localization as Tier 5 execution benchmark (how PH tax lands in Odoo, not what the rules are)
- Implement navigation answer separation: official BIR destinations vs internal Odoo destinations
- Add execution_model_citations to action proposals that require Odoo implementation mapping
