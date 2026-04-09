# Plan — AI Platform Operating Model

## Implementation model

This target is implemented primarily through:
- docs for published index and cross-repo navigation
- platform for AI control-plane and retrieval docs
- agents for runtime/orchestration docs
- odoo only for connector-surface references where needed

## Repo ownership map

| Workstream | Canonical repo |
|---|---|
| AI platform index | docs |
| Foundry control plane | platform |
| Retrieval and grounding | platform |
| Agent runtime boundaries | agents |
| Odoo connector surface references | odoo |

## Area Path model

- ipai-platform\docs
- ipai-platform\platform
- ipai-platform\agents
- ipai-platform\odoo

## Iteration model

- ipai-platform\Docs\Wave-2
- ipai-platform\Docs\Hardening

## Validation model

Every workstream must identify:
- current-state bridge presence vs gap
- source-of-truth repo
- Odoo boundary rule
- required evidence

## Risks

- AI responsibilities split unclearly across repos
- retrieval/search assumptions not backed by live architecture
- drift between AI docs and actual bridge/runtime state

## Exit criteria

This target is complete only when:
- all AI platform workstreams are published
- the external-runtime-only rule is explicit
- Foundry/retrieval/safety ownership is documented
- cross-links to workload and engineering families exist
