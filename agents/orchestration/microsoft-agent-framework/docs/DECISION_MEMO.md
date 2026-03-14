# Decision Memo: Orchestration Framework Selection

## Date: 2026-03-14

## Decision
Adopt Microsoft Agent Framework as the preferred orchestration framework candidate for multi-agent evolution.

## Context
The current production agent (`ipai-odoo-copilot-azure`) runs on Azure AI Foundry Agent Service as a single-agent runtime. As the platform matures, multi-agent orchestration is needed for:
- finance close workflows
- compliance escalation
- approval paths
- long-running operational tasks
- control-tower visibility

## Options Evaluated

### Microsoft Agent Framework
- Graph-based workflows, streaming, checkpointing
- Human-in-the-loop, time-travel capabilities
- OpenTelemetry observability
- Python and .NET support
- Natural fit with existing Azure/Foundry ecosystem
- **Selected as: primary orchestration candidate**

### Google ADK
- Excellent multi-agent decomposition patterns
- SequentialAgent, ParallelAgent, LoopAgent
- Shared session state model
- Clear parent/sub-agent hierarchies
- **Selected as: design reference, not runtime choice**

### Azure AI Foundry Agent Service (current)
- Already in production
- Single-agent focused
- **Selected as: keep as current live runtime**

## Decision Rules
1. Keep Foundry as live runtime until orchestration layer is validated
2. Use MAF for orchestration prototyping
3. Use ADK patterns for agent decomposition design
4. Do not replace Foundry with MAF immediately
5. Do not introduce framework churn before current agent contracts stabilize

## Phased Adoption
- Phase 1: Document and model (current)
- Phase 2: Prototype coordinator + 2 specialists
- Phase 3: Compare against current Foundry runtime
- Phase 4: Decide final orchestration model

## First Prototype
Close/compliance orchestration workflow — stresses sequencing, state, specialist delegation, observability, and checkpointing.
