# Microsoft Agent Framework — Orchestration Candidate

## Status
Evaluation candidate. Not yet production runtime.

## Decision
Adopt Microsoft Agent Framework as the preferred orchestration framework candidate for future multi-agent evolution of `ipai-odoo-copilot-azure`.

Keep Azure AI Foundry Agent Service as the live runtime in the current phase.

Use Google ADK patterns as a design reference for decomposition, not as the default runtime choice.

## Current Runtime Stack
```
landing page / internal apps
  -> backend adapter
    -> Azure AI Foundry Agent Service
      -> ipai-odoo-copilot-azure
```

## Orchestration Evolution Path
```
agents/
  orchestration/
    microsoft-agent-framework/   <- this directory
```

## Target Agent Decomposition

### Coordinator Agent
Top-level router/orchestrator. Classifies requests, chooses mode, invokes specialists, assembles responses, enforces public vs authenticated policy.

### Specialist Agents
1. **Research Agent** — source-backed retrieval, regulation/context lookup, case synthesis
2. **Insight Agent** — KPI interpretation, pattern/anomaly detection, trend summaries
3. **Planning Agent** — workflow generation, close calendars, approval/task variants
4. **Validation Agent** — deadline cross-check, workflow completeness, artifact validation
5. **Odoo Operations Agent** — model/view/security guidance, action preparation
6. **Monitoring Agent** — readiness summaries, overdue/aging rollups, exception summaries
7. **Execution/Action Agent** — tool-mediated operations only, draft/write boundaries

## First Prototype Target
Close/compliance orchestration (NOT public web chat):
1. Coordinator receives "prepare monthly close"
2. Planning agent creates close workflow
3. Validation agent checks completeness/dependencies
4. Compliance agent overlays BIR deadlines
5. Monitoring agent produces readiness summary
6. Execution agent prepares Odoo draft artifacts

## Related Documents
- `docs/DECISION_MEMO.md`
- `spec/maf-orchestration/`
- `agents/orchestration/adk-patterns/`
