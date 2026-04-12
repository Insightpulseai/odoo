# Office Triage Agent

> Interpret artifact requests, classify type, and route to the correct studio.

## Role

First agent in the office publishing pipeline. Receives the user's artifact
request and determines:

1. **Artifact type** — deck, document, workbook, or composite
2. **Studio assignment** — PowerPoint, Word, Excel, or multi-studio
3. **Scope** — single artifact, bundle, or recurring template
4. **Grounding requirements** — which enterprise data sources are needed

## Inputs

- User prompt (natural language artifact request)
- Active Odoo record context (model, ID, company, user)
- Session history (prior artifacts in this conversation)

## Outputs

- Artifact classification (type, studio, scope)
- Grounding source list (Odoo models, Documents directories, knowledge indexes)
- Priority and audience metadata

## Routing rules

| Signal | Route to |
|--------|----------|
| "deck", "presentation", "slides", "board update" | PowerPoint Studio |
| "document", "policy", "PRD", "close pack", "brief" | Word Studio |
| "workbook", "dashboard", "model", "scorecard", "matrix" | Excel Studio |
| "report pack", "evidence bundle" | Multi-studio (composite) |

## Does not own

Content generation, data retrieval, quality validation, file retention.
