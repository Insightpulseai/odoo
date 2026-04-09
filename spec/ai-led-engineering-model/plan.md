# Plan — AI-Led Engineering Model

## Implementation model

This target is implemented through:
- docs for central engineering index
- .github for policy and CI/CD governance docs
- agents for AI-led SDLC and agent role docs
- infra where promotion/deployment workflow detail must align to runtime automation

## Repo ownership map

| Workstream | Canonical repo |
|---|---|
| Engineering index | docs |
| Spec-driven development | .github |
| Agent-assisted delivery | agents |
| CI/CD and promotion | .github / infra |
| Boards + GitHub traceability | .github / docs |
| SRE feedback loop | agents |

## Area Path model

- ipai-platform\docs
- ipai-platform\infra
- ipai-platform\agents

## Iteration model

- ipai-platform\Docs\Wave-2
- ipai-platform\Docs\Hardening

## Validation model

Every workstream must validate:
- actual workflow ownership
- actual PR/build traceability behavior
- actual sprint/retro/backlog conventions
- consistency with Spec Kit bundle structure

## Risks

- planning system and execution system diverge
- traceability is partial or inconsistent
- CI/CD docs describe aspirational rather than actual flows

## Exit criteria

This target is complete only when:
- the engineering family is published
- Boards/GitHub/CI/CD traceability is explicit
- SRE feedback loop is documented
- work-item templates and naming rules are reviewable
