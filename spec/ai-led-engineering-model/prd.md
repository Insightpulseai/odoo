# PRD — AI-Led Engineering Model

## Objective

Publish the canonical AI-led engineering and delivery model for InsightPulseAI.

## Why this matters

The platform already operates across multiple repos and mixes specifications, runtime operations, CI/CD, and agent-assisted work. This target defines a single engineering operating model so that planning, implementation, validation, and operational feedback all follow the same cross-repo discipline.

## Benchmark model

- Azure + GitHub AI-led SDLC → planning-to-code-to-operations benchmark
- Azure Boards + GitHub integration → traceability benchmark
- Spec Kit → specification and target-contract benchmark

## In scope

- engineering index
- spec-driven development
- coding-agent and quality-agent model
- CI/CD and promotion model
- Azure Boards + GitHub traceability
- SRE feedback loop

## Out of scope

- repo-specific coding conventions not tied to the delivery model
- replacing deterministic CI/CD with agent improvisation
- bypassing spec-first planning for non-trivial work

## Success metrics

- one documented engineering operating model exists
- planning-to-PR traceability is explicit
- spec-first rules are documented
- runtime feedback loops back into engineering are documented

## Affected repos

- docs
- .github
- agents
- infra

## Owning teams

- ipai-docs
- ipai-agents
- ipai-infra
- ipai-platform

## Workstream model

1. Engineering Index
2. Spec-Driven Development
3. Agent-Assisted Delivery
4. CI/CD and Promotion
5. Azure Boards + GitHub Traceability
6. SRE Feedback Loop

## Acceptance conditions

- all engineering workstreams are documented
- Boards/GitHub/CI/CD traceability rules are explicit
- the SRE feedback loop is documented
- the spec-first model is reflected in work-item structure

## Azure Boards projection

Epic title:
`[TARGET] AI-Led Engineering Model Published`
