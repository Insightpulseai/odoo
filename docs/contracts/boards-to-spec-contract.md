# Boards-to-Spec Contract

## Purpose

Define when and how Azure Boards work items become a Spec Kit bundle.

## Scope

Applies to: new product capabilities, new Odoo modules, major architecture changes, AI-enabled features, marketplace-bound deliverables.

## Source and target

**Source:** Azure Boards Issue
**Target:** `spec/<slug>/`

## Required source fields in Azure Boards

The source Issue must contain:

- Title
- Purpose
- Scope and out-of-scope
- Acceptance criteria
- Owner
- Target iteration
- Tags
- Related objective/Epic
- Links to any prior architecture/runtime docs

## Slug rules

The spec slug must be: lowercase, hyphen-separated, stable across PRs and releases, derived from the workstream/capability name.

Example:

- Azure Issue: `[FEAT] ipai_odoo_copilot + Foundry integration`
- Slug: `ipai-odoo-copilot-foundry-integration`

## Required output bundle

```text
spec/<slug>/
  constitution.md   — purpose, principles, non-goals, constraints, success
  prd.md            — user/problem framing, requirements, acceptance, risks
  plan.md           — architecture, dependencies, rollout, validation
  tasks.md          — implementable tasks, sequencing, verification, deployment
```

## Gate to create a spec bundle

A spec bundle is required when any of these are true:

- net-new module/app surface
- schema/integration change
- security/identity boundary change
- runtime/deployment change
- AI feature or evaluation requirement
- marketplace publication target

A spec bundle is optional only for trivial fixes that do not change behavior, contract, deployment, or user experience.

## Traceability rules

Each spec bundle must link back to Azure Boards Epic and Issue. Each Issue should link to all four spec files.

## Definition of ready for development

Development may begin only when:

- all four files exist
- the Issue link is present
- acceptance criteria are in the spec bundle
- deploy target is identified
- AI eval requirement is marked yes/no

## Failure conditions

A work item fails this contract if:

- code starts without a required spec bundle
- slug changes midstream without migration/update
- acceptance criteria exist only in chat/PR text and not in Boards/spec
- architecture-critical decisions are missing from plan.md

---

*Last updated: 2026-03-17*
