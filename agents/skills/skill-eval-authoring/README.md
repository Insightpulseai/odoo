# Skill: Skill Eval Authoring

## Purpose

Designs and writes evaluation suites for agent skills. Treats evals as mandatory quality gates — no skill ships without eval evidence.

## Owner Persona

`skill-eval-judge`

## Skill Type

`encoded_preference` — encodes the eval authoring process from Anthropic's guidance.

## Key Principles

- Grade outputs, not paths
- Use parallel clean-context agents for uncontaminated evaluation
- Multiple complementary eval methods (Swiss Cheese Model)
- Evals are living artifacts requiring ongoing maintenance

## Cross-references

- `agents/knowledge/benchmarks/anthropic-skill-authoring.md`
- `agents/personas/skill-eval-judge.md`
