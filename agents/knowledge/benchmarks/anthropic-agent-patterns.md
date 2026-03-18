# Benchmark: Anthropic Agent Patterns

> Source: Anthropic engineering blog — building effective agents, common workflow patterns, multi-agent research, context engineering, long-running agent harnesses
>
> Role: Workflow-pattern benchmark for pattern choice decisions
>
> This is NOT architecture doctrine. It is a benchmark that informs when to use which pattern.

---

## Pattern Hierarchy (Simplicity First)

Anthropic's most consistent guidance: **do not build agents when simpler patterns suffice.**

1. **Single optimized LLM call** — sufficient for most tasks when paired with good retrieval and in-context examples
2. **Workflow patterns** — predefined code paths orchestrating LLMs and tools
3. **Agents** — LLMs dynamically directing their own processes and tool use

"Success in the LLM space isn't about building the most sophisticated system. It's about building the right system for your needs."

---

## Five Workflow Patterns

### A. Sequential (Prompt Chaining)

- Tasks decompose into fixed sequential subtasks; output of step N feeds step N+1
- Use when: clear dependency chain, accuracy matters more than latency
- Example: outline → write; generate → translate
- Rule: "First try your pipeline as a single agent. Only split into a multi-step workflow when a single agent can't handle it reliably."

### B. Routing (Classification-Directed)

- Classify input, then direct to specialized handler per category
- Use when: distinct input types need different processing
- Enables per-category optimization without cross-category degradation

### C. Parallelization (Fan-Out / Fan-In)

- Multiple independent LLM calls run simultaneously, results aggregated
- Sub-patterns: **Sectioning** (different aspects → different agents) and **Voting** (same task → multiple perspectives)
- Rule: "Design your aggregation strategy before implementing parallel agents."

### D. Orchestrator-Workers

- Central LLM dynamically determines subtasks and delegates to workers
- Key distinction from parallelization: subtasks are NOT pre-defined but determined at runtime
- Use when: task decomposition cannot be predicted in advance

### E. Evaluator-Optimizer (Iterative Refinement)

- One model generates, another evaluates against criteria; loop until quality threshold
- Use when: clear measurable quality criteria AND first-attempt quality falls short
- Do NOT use when: first attempt is good enough, criteria are too subjective, deterministic tools exist, or real-time response needed
- Rule: "Set clear stopping criteria before iterating."

---

## Autonomous Agents

Agents emerge when the LLM controls its own loop — planning, executing tools, observing results, deciding next steps.

**When to use**: open-ended problems, environmental feedback required, adaptive strategies needed.

**When NOT to use**: decomposable into fixed workflows, latency/cost constraints, low trust in model decisions.

**Mandatory**: sandboxed execution, resource limits, monitoring, human review checkpoints.

---

## Context Engineering

"Find the smallest set of high-signal tokens that maximize the likelihood of your desired outcome."

- **Compaction**: summarize conversation history, preserve critical decisions, discard redundant tool outputs
- **Structured note-taking**: persistent external memory (CLAUDE.md, progress files) for multi-hour coherence
- **Sub-agent architectures**: focused sub-agents with clean context windows, return condensed summaries (1-2K tokens)

---

## Multi-Agent Production Pattern (Anthropic Research)

- Lead researcher (Opus) spawns 3-5 subagents (Sonnet) in parallel
- Subagents output to filesystem, not conversation
- Multi-agent outperformed single-agent by 90.2%
- Token usage explains 80% of performance variance
- Scaling heuristics essential (early versions spawned 50 subagents for simple queries)

---

## Decision Framework

| Question | Answer → Pattern |
|----------|-----------------|
| Can a single call solve this? | Yes → Single call |
| Fixed sequential subtasks with dependencies? | Yes → Sequential |
| Independent subtasks benefiting from concurrency? | Yes → Parallel |
| Dynamic subtask decomposition? | Yes → Orchestrator-workers |
| Iterative refinement with measurable criteria? | Yes → Evaluator-optimizer |
| Open-ended, adaptive planning required? | Yes → Autonomous agent |

---

## Sources

- [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)
- [Common workflow patterns](https://claude.com/blog/common-workflow-patterns-for-ai-agents-and-when-to-use-them)
- [Multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)
- [Context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
