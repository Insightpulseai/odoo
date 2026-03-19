# Skill: Autonomous Agent Fit Assessment

## Purpose

Assesses whether a task genuinely requires an autonomous agent (LLM controls its own planning/execution loop) or if a simpler pattern would suffice. This is the final check before recommending the most complex and expensive pattern.

## Owner Persona

`workflow-architect`

## Skill Type

`encoded_preference` — encodes the criteria for when autonomous agents are justified.

## Key Principle

Autonomous agents are the pattern of last resort. They trade latency and cost for flexibility. Use only when:
- Problem is truly open-ended
- Steps cannot be predicted in advance
- Environmental feedback is required to determine next actions
- Adaptive strategies are needed

## Cross-references

- `agents/knowledge/benchmarks/anthropic-agent-patterns.md`
- `agents/skills/agent-pattern-selection/`
