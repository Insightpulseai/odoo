# Template Adaptation

> Narrative companion to `platform/templates/adaptation-map.yaml` (template → repo mapping).
> For **upstream source adoption decisions** (consume-directly vs. clone-reference vs. fork-later vs. do-not-adopt), see the canonical SSOT at `ssot/governance/upstream-adoption-register.yaml` and the narrative register at `docs/architecture/repo-adoption-register.md`.

## Reference templates

| Template | Primary use |
|----------|-------------|
| Get started with AI agents | Agent shell, ACA hosting |
| Deploy Your AI Application in Production | Prod environment, security posture |
| Multi-modal Content Processing | Document ingestion/extraction |
| Release Manager Assistant | Release verification, evidence packs |
| Home Banking Assistant | Finance agent orchestration |

## Use them for

- Hosting patterns (ACA structure, env wiring, health checks)
- Orchestration patterns (agent graph, tool routing)
- Document pipelines (extraction, normalization, structured output)
- Production verification patterns (smoke tests, evidence, rollback)

## Do not use them for

- Replacing Odoo 18 business logic
- Bypassing Odoo approvals
- Inventing a second system of record
- Copy-pasting banking or finance domain logic

## Repo mapping (flattened 2026-04-14)

Per `docs/architecture/upstream-landing-matrix.md` — agent-plane templates land in `agent-platform`; docs mirror is reference-adaptations only. `web` and `automations` rows removed (web = browser surfaces only; automations uses canonical YAML).

| Repo | Templates adopted |
|------|------------------|
| odoo | none (preserve business execution authority) |
| agent-platform | ai-agents-starter, ai-production, home-banking-assistant, release-manager-assistant, multimodal-content-processing |
| infra | ai-production (+ azd-cli, azure-mcp-server tools) |
| data-intelligence | azure-search-documents + azure-ai-documentintelligence SDKs |
| docs | reference-adaptations mirror only (pattern harvests for any template adopted above) |

## Microsoft runtime guidance references

Use Azure Architecture Center best practices as runtime implementation guidance for:

- API design
- API implementation
- background jobs
- monitoring and diagnostics
- transient fault handling

Use Azure AI FinOps guidance as planning and operating guidance for:

- business case and funding
- governance and GenAIOps
- usage monitoring
- business-value measurement
- efficiency optimization

These are separate from Partner Center (commercial/GTM lane).

## Registry of record

`platform/templates/adaptation-map.yaml`
