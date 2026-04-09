# Plan — Data Intelligence Operating Model

## Implementation model

This target is implemented primarily through:
- docs for central index and navigation
- data-intelligence for the canonical lakehouse/governance/BI docs
- platform where control-plane overlaps exist
- odoo only where source-system boundary guidance is needed

## Repo ownership map

| Workstream | Canonical repo |
|---|---|
| Data-intelligence index | docs + data-intelligence |
| Lakehouse and governance | data-intelligence |
| Ingestion patterns | data-intelligence |
| Consumption and BI | data-intelligence |
| Data/AI integration | data-intelligence / platform |

## Area Path model

- ipai-platform\docs
- ipai-platform\data-intelligence
- ipai-platform\platform
- ipai-platform\odoo

## Iteration model

- ipai-platform\Docs\Wave-2
- ipai-platform\Docs\Hardening

## Validation model

Every workstream must identify:
- source systems and boundaries
- batch vs real-time assumptions
- governance ownership
- semantic consumption targets
- AI-readiness implications

## Risks

- Odoo and analytics responsibilities blur
- ingestion assumptions are undocumented
- lakehouse docs describe target state only without current-state grounding

## Exit criteria

This target is complete only when:
- the data-intelligence family is published
- Odoo boundaries are explicit
- lakehouse/governance/consumption model is documented
- data/AI integration model is reviewable
