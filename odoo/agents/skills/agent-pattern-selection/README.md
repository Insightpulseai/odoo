# Skill: Agent Pattern Selection

## Purpose

Decides which agentic pattern (single call, sequential, parallel, evaluator-optimizer, or autonomous agent) fits a given task. Enforces Anthropic's simplicity doctrine: start with the simplest pattern that works.

## Owner Persona

`workflow-architect`

## Skill Type

`encoded_preference` — encodes Anthropic's pattern selection doctrine as a repeatable decision process.

## Trigger Conditions

- New skill or agent is being designed
- Architecture review of an existing agent
- Task decomposition discussion
- Any request mentioning "should this be an agent?"

## Key Decision

The pattern hierarchy is strict:
1. Single call (default)
2. Sequential workflow (dependencies between steps)
3. Parallel workflow (independent subtasks)
4. Evaluator-optimizer (measurable iteration gains)
5. Autonomous agent (open-ended, unpredictable steps)

## Cross-references

- `agents/knowledge/benchmarks/anthropic-agent-patterns.md`
- `agents/personas/workflow-architect.md`
