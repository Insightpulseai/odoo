# Template Adaptation

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

## Repo mapping

| Repo | Templates adopted |
|------|------------------|
| odoo | none |
| platform | ai-agents-starter, ai-production, multimodal-content-processing |
| automations | release-manager-assistant, multimodal-content-processing |
| agents | home-banking-assistant, ai-agents-starter |
| docs | ai-production, release-manager-assistant |
| web | ai-agents-starter (optional) |

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
