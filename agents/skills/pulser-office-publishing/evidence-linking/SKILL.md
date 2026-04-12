# Evidence / Documents Agent

> Retain publishable artifacts in Odoo Documents with trace links.

## Role

Final agent in the pipeline. Takes the QA-approved artifact and stores it
in Odoo Documents with full metadata, trace links back to source OKRs,
milestones, and Odoo records.

## Inputs

- QA-approved artifact (PPTX, DOCX, or XLSX)
- Source data manifest (which Odoo records, Documents files, knowledge items were used)
- Artifact metadata (type, studio, audience, period, author)

## Outputs

- Retained copy in Odoo Documents with:
  - File stored in canonical directory (e.g., `Finance PPM/10-Office-Artifacts/2026/2026-04/`)
  - Metadata tags: OKR, KR, milestone, period, company, branch, lane, owner, reviewer
  - Trace links back to source records and Documents files
  - Evidence classification per data point used

## Retention rules

- Source artifacts and derivative publishable outputs are both retained.
- Prior versions are archived, not deleted.
- Each retained copy carries a link to the QA scorecard that approved it.
- Finance-critical artifacts require reviewer signoff before retention is finalized.

## Grounding feedback loop

Once retained, the artifact becomes available as a grounding source for
future Pulser queries. The Evidence / Documents Agent registers the new
artifact in the Documents retrieval index so Pulser can answer questions
about it.

## Does not own

Artifact creation, quality validation, request interpretation.
