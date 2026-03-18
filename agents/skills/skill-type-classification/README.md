# Skill: Skill Type Classification

## Purpose

Classifies every agent skill as either `capability_uplift` or `encoded_preference`. This classification determines the eval strategy and durability expectations.

## Owner Persona

`skill-author`

## Skill Type

`encoded_preference` — this is itself an encoded preference skill (it documents the classification process).

## Classification Rules

| Type | Definition | Eval Strategy | Durability |
|------|-----------|---------------|------------|
| `capability_uplift` | Makes the model do something better than prompting alone | Regression testing; may become obsolete as models improve | Medium |
| `encoded_preference` | Sequences work according to team's process/doctrine | Fidelity validation; durable if process is accurate | High |

## Cross-references

- `agents/knowledge/benchmarks/anthropic-skill-authoring.md`
- `agents/personas/skill-author.md`
