# Skill: Sequential Workflow Design

## Purpose

Designs sequential (prompt chaining) workflows where tasks decompose into fixed ordered steps with dependencies between them. Output of step N feeds step N+1.

## Owner Persona

`workflow-architect`

## Skill Type

`encoded_preference` — encodes sequential workflow design patterns from Anthropic's guidance.

## When to Use

- Tasks have clear dependency chains
- Accuracy matters more than latency
- Steps can be validated independently before proceeding

## Key Rule

"First try your pipeline as a single agent. Only split into a multi-step workflow when a single agent can't handle it reliably."

## Cross-references

- `agents/knowledge/benchmarks/anthropic-agent-patterns.md` §A
- `agents/skills/agent-pattern-selection/`
