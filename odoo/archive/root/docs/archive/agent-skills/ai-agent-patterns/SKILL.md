---
name: ai-agent-patterns
description: Elite AI Agent development patterns based on Google/Kaggle 5-Day Intensive. Use for building reasoning-loops, multi-agent systems, and robust tool-calling workflows.
license: MIT
metadata:
  author: InsightPulseAI
  version: "1.0.0"
---

# AI Agent Design Patterns

Architecting advanced agentic workflows that leverage reasoning, precision tool use, and multi-agent coordination.

## Core Pillars (5-Day Intensive)

### 1. Tool Use & Grounding

- **Precision Calling**: Pass exact schemas. Use Python REPL for deterministic calculations.
- **Grounding**: Always verify model output against tool results (Observations).

### 2. Reasoning Loops (ReAct)

- **Cycle**: Thought -> Action -> Observation -> Thought.
- **Validation**: Agents must explicitly state _why_ they are calling a tool before doing so.
- **Fail-safes**: Implement maximum loops to prevent infinite recursions.

### 3. Retrieval Augmented Generation (RAG)

- **Agentic Search**: The agent decides _what_ to search and _how_ to refine queries.
- **Source Verification**: Cite specific documents or tools used.

### 4. Multi-Agent Systems

- **Roles**: Define specific roles (e.g., Coder, Reviewer, Architect).
- **Communication**: Use a structured "hand-off" or "mediator" pattern.
- **Consensus**: Require multiple agents to agree on high-risk decisions.

### 5. Agentic Workflows & State

- **LangGraph Patterns**: Model complex workflows as state machines/graphs.
- **Memory**: Persistent state across turns to maintain long-term context.

## Integration Checklist

- [ ] Does the agent have the _least sufficient_ tools for the task?
- [ ] Is there a clear reasoning loop (Thought block)?
- [ ] Are tool errors handled gracefully (Observation feedback)?
- [ ] If multi-agent, is there a clear lead/orchestrator?
