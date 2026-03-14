# Google ADK Multi-Agent Patterns — Reference

## Purpose
Reference model for agent decomposition patterns. Not the runtime choice.

## Key Patterns

### 1. Parent/Sub-Agent Hierarchy
Top-level coordinator delegates to domain specialists. Each specialist has bounded responsibility.

### 2. Workflow Agents
- **SequentialAgent**: steps execute in order
- **ParallelAgent**: steps execute concurrently, results gathered
- **LoopAgent**: iterative refinement until condition met

### 3. Shared Session State
Agents share state through a session object. State is typed and scoped.

### 4. LLM-Driven Delegation
Coordinator uses LLM reasoning to choose which specialist to invoke.

### 5. Explicit Tool Routing
Each specialist declares its tools. Coordinator does not access specialist tools directly.

## Application to InsightPulseAI
These patterns inform the MAF orchestration design:
- Coordinator = parent agent
- Specialists = sub-agents with bounded tools
- Close orchestration = SequentialAgent pattern
- Parallel data gathering = ParallelAgent pattern
- Iterative validation = LoopAgent pattern

## Source
https://google.github.io/adk-docs/agents/multi-agents/
