# Skill: Skill Benchmarking

## Purpose

Runs benchmark comparisons between skill versions, measures performance trends, and manages the capability → regression eval lifecycle.

## Owner Persona

`skill-eval-judge`

## Skill Type

`capability_uplift` — provides benchmarking methodology beyond what base model can do.

## Key Principles

- Track: eval pass rates, execution time, token consumption, A/B comparisons
- Capability evals graduate to regression suites when saturated
- Refresh with harder challenges when all solvable tasks pass

## Cross-references

- `agents/knowledge/benchmarks/anthropic-skill-authoring.md`
- `agents/personas/skill-eval-judge.md`
