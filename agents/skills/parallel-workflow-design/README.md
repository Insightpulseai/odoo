# Skill: Parallel Workflow Design

## Purpose

Designs parallel (fan-out / fan-in) workflows where independent subtasks run concurrently and results are aggregated.

## Owner Persona

`workflow-architect`

## Skill Type

`encoded_preference` — encodes parallel workflow patterns.

## When to Use

- Subtasks are genuinely independent (no cross-task dependencies)
- Concurrent execution improves throughput
- Aggregation strategy can be defined upfront

## Key Rule

"Design your aggregation strategy before implementing parallel agents."

## Cross-references

- `agents/knowledge/benchmarks/anthropic-agent-patterns.md` §C
- `agents/skills/agent-pattern-selection/`
