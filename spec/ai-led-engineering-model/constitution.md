# Constitution — Org-Wide Target Bundle

## Purpose

This bundle defines an org-wide target for the InsightPulseAI platform.

It exists so that:
- target intent is authored as a durable specification,
- repo and team ownership are explicit,
- execution can be projected into Azure Boards without losing architectural meaning,
- delivery remains traceable from target → feature → story → PR → validation.

## Governing principles

### 1. Specs are the target contract
This target is defined in spec artifacts first. Azure Boards tracks delivery but does not replace the target contract.

### 2. Repo authority must be explicit
Every workstream must identify its source-of-truth repo and owning team.

### 3. OCA first, thin bridge second
Where the target touches Odoo functionality, CE core and OCA remain the default parity lanes. Custom `ipai_*` work stays thin and limited to bridge, connector, adapter, meta-module, or narrow glue behavior.

### 4. Heavy AI and platform logic stay outside Odoo
If the target involves AI, RAG, OCR, agents, retrieval, control-plane, or runtime concerns, the primary implementation must live outside Odoo unless explicitly approved otherwise.

### 5. Evidence is mandatory
Completion requires evidence, not only authored docs or merged code. Claims tied to runtime, infra, governance, or integrations must be validated against current-state truth.

### 6. Live state and intended state must converge
If the target touches platform or runtime concerns, live inventory and IaC/SSOT must be reconciled or explicitly recorded as governed exceptions.

## Organizational scope

This target may span:
- docs
- platform
- infra
- odoo
- agents
- data-intelligence
- .github
- web

## Delivery model

Azure Boards projection:
- Epic = org-wide target
- Features = workstreams / deliverable families
- User Stories = concrete repo/team deliverables
- Tasks = execution sub-steps

## Non-goals

This bundle does not:
- replace Azure Boards,
- replace GitHub PR traceability,
- justify broad custom-module development,
- collapse all execution truth into one repo.
