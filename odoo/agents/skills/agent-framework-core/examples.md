# Examples — agent-framework-core

## Example 1: Document processing multi-agent workflow

**Input**: Design a workflow where documents are classified, extracted, validated by a human, then stored.

**Output**:
- Workflow graph:
  - Node `classify` -> Edge(always) -> Node `extract`
  - Node `extract` -> Edge(confidence >= 0.9) -> Node `store`
  - Node `extract` -> Edge(confidence < 0.9) -> Node `human_review`
  - Node `human_review` -> Edge(approved) -> Node `store`
  - Node `human_review` -> Edge(rejected) -> Node `classify` (retry)
- Middleware: [auth, rate_limit, content_safety, logging]
- Checkpointing: after `classify` and `extract` (long-running OCR step)
- Telemetry: `agent.doc_processing.classify`, `agent.doc_processing.extract`, etc.
- Human-in-the-loop: `human_review` gate blocks until operator approves or rejects
- Test result: PASS — 3 documents processed, 1 routed to human review, all stored
- Evidence: DevUI graph visualization + OpenTelemetry trace

## Example 2: Workflow missing telemetry

**Input**: Review an existing agent workflow that has no OpenTelemetry instrumentation.

**Output**:
- Workflow graph: 4 nodes, 3 edges — structure valid
- Middleware: configured — PASS
- Checkpointing: configured — PASS
- Telemetry: NOT CONFIGURED — FAIL (BLOCKER for production)
- Human-in-the-loop: no gates defined — N/A (not required for this workflow)
- Blocker: Production deployment requires OpenTelemetry traces on all workflows
- Recommendation: Add span instrumentation following `agent.<workflow>.<step>` convention

## Example 3: Conflating orchestration with channel delivery

**Input**: Agent workflow includes Teams message formatting and adaptive card rendering in the graph nodes.

**Output**:
- Workflow graph: POLICY VIOLATION — channel-specific logic found in orchestration layer
- Finding: Nodes `format_teams_card` and `send_teams_message` belong in the M365 Agents SDK channel layer, not in the orchestration graph
- Recommendation: Refactor — orchestration produces a result payload; channel delivery formats and sends it
- Cross-reference: `agents/skills/m365-agents-channel-delivery/` for channel packaging
