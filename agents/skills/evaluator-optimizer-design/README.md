# Skill: Evaluator-Optimizer Design

## Purpose

Designs evaluator-optimizer loops where one model generates output, another evaluates against criteria, and the loop iterates until quality threshold or max iterations.

## Owner Persona

`workflow-architect`

## Skill Type

`encoded_preference` — encodes iterative refinement patterns.

## When to Use

- Clear, measurable quality criteria exist
- First-attempt quality consistently falls short
- Iteration demonstrably improves results

## When NOT to Use

- First attempt is good enough
- Evaluation criteria are too subjective
- Deterministic tools exist (linters, formatters) — use those instead
- Real-time response is needed

## Key Rule

"Set clear stopping criteria before iterating. Know when good enough is good enough."

## Cross-references

- `agents/knowledge/benchmarks/anthropic-agent-patterns.md` §E
- `agents/skills/agent-pattern-selection/`
