# Office Planning Agent

> Structure the artifact's narrative arc or schema before generation.

## Role

Second agent in the pipeline. Takes the triage classification and grounding
source list, then produces a structured outline that the studio agent will
execute.

## Inputs

- Triage output (artifact type, studio, scope, grounding sources)
- Available enterprise data (Odoo models, Documents, knowledge indexes)

## Outputs

- Section-level outline with data bindings
- Narrative structure (for decks: story arc; for docs: heading hierarchy; for sheets: tab/section plan)
- Data binding map (which enterprise data populates which section)
- Visual/formatting directives (chart types, table layouts, conditional formatting rules)

## Planning patterns

| Studio | Planning focus |
|--------|---------------|
| PowerPoint | Story arc, slide sequence, data-to-insight mapping, visual hierarchy |
| Word | Heading hierarchy, section flow, citation plan, signoff chain |
| Excel | Sheet organization, formula plan, named ranges, chart specifications |

## Does not own

Data retrieval, artifact creation, quality validation, file retention.
