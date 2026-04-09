# agents

Canonical registry of personas, skills, judges, eval suites, schemas, workflow samples, and agent behavior definitions.

## Purpose

This repository defines how agents should behave. It owns agent manifests, skills, personas, judges, eval suites, schemas, and routing metadata used by runtime systems and coding agents.

## Owns

- Personas
- Skills
- Judges
- Eval suites and fixtures
- Agent schemas and manifests
- Workflow samples
- Machine-readable routing and policy maps
- Optional operator overlays such as `.claude/`

## Does Not Own

- Deployable runtime services
- Shared control-plane APIs
- Azure infrastructure
- ERP runtime logic
- Public product UI

## Repository Structure

```text
agents/
├── .github/
├── .claude/
├── personas/
├── skills/
├── judges/
├── evals/
├── schemas/
├── agent-samples/
├── workflow-samples/
├── registry/
├── docs/
├── spec/
└── ssot/
```

## Operating Rule

- If it defines how an agent should think, act, evaluate, or route, it belongs here.
- If it runs as a deployable service, it belongs in `agent-platform`.

## Validation

Changes must:

- preserve schema and manifest integrity
- keep persona/skill/judge boundaries clear
- keep eval fixtures reproducible
- avoid mixing runtime implementation into behavior definitions
