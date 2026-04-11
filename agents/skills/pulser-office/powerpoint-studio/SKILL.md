# PowerPoint Studio

> Publishable-quality executive deck generation from Odoo PPM data.

## Capability

Generate presentation decks (PPTX/PDF) grounded in live Odoo record context,
Finance PPM OKR metrics, retained Documents artifacts, and approved knowledge.

## Grounding sources

1. Active Odoo record context (PPM OKRs, KR scores, milestones)
2. Linked retained artifacts in Odoo Documents
3. Approved policy and knowledge indexes
4. Finance PPM dashboard metrics

## Output types

| Type | Description | Example |
|------|-------------|---------|
| Executive narrative deck | Leadership review story with clean structure | Board update, quarterly review |
| Operating review | Status + metrics + blockers + next steps | Monthly ops review |
| Board update template | Recurring board-ready status deck | Standing board presentation |
| Milestone storyline | Release / delivery narrative | R1 completion deck |

## Quality gates

- [ ] Story flow: logical narrative arc, not just a data dump
- [ ] No overflow: text and visuals fit within slide bounds
- [ ] Render QA: deck opens cleanly in PowerPoint/Google Slides/LibreOffice
- [ ] Brand-safe: consistent typography, restrained color, deliberate hierarchy
- [ ] Grounded: all data points traced to Odoo records or Documents artifacts

## Publish gate

1. Content grounded in Odoo / Documents / approved knowledge.
2. Artifact renders cleanly with no overflow, overlap, or broken layout.
3. Reviewer notes resolved and retained copies stored in Odoo Documents.
4. Final output ready to circulate externally without reformatting.

## Dependencies

- `python-pptx` — native PPTX generation
- `ipai_odoo_copilot` — Odoo context packaging
- OCA `report_xlsx` — data export fallback
- Odoo Documents — retained copy storage

## Phase

R1 Foundation → R2 Core → R3 Hardening
