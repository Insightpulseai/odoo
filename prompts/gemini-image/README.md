# Gemini Image Prompt Library

Reusable prompt assets for Gemini Image / Imagen / Nano Banana style workflows.

## Goals
- Keep image prompts versioned and reusable
- Separate base prompts from variants
- Standardize metadata for model, aspect ratio, output intent, and brand constraints
- Reduce naming and visual drift across product, marketing, and brand assets

## Conventions
- Each prompt lives in its own directory
- `base.prompt.md` = canonical default prompt
- `*.variant.prompt.md` = optional tailored variants
- All prompts should follow the schema in `schema/prompt.schema.json`
- `catalog/index.yaml` is the discovery index for all prompt assets

## Categories
- `brand/` — OG cards, keynote covers, brand posters
- `marketing/` — homepage visuals, campaign creatives
- `product-ui/` — UI concept renders, dashboard mockups, workflow screens
- `ads/` — performance / campaign visual prompts
- `docs-diagrams/` — architecture and explainer visuals
- `edit-workflows/` — image transformation / refinement prompts

## Prompt authoring rules
- Keep one clear objective per prompt
- Prefer minimal but specific instructions
- Separate:
  - subject
  - composition
  - style
  - key constraints
  - output requirements
- Use approved public naming only:
  - InsightPulseAI
  - Pulser
  - Odoo on Cloud
  - Cloud Operations
  - Analytics & Dashboards
- Do not use deprecated public naming in new prompt assets

## Naming rules
Directory names:
- lowercase
- hyphen-separated
- stable and descriptive

Prompt files:
- `base.prompt.md` for canonical prompt
- `<variant>.variant.prompt.md` for alternatives
