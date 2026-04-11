# Office Research / Grounding Agent

> Retrieve and rank enterprise data for grounded artifact generation.

## Role

Third agent in the pipeline. Retrieves enterprise data from Odoo records,
Finance PPM objects, retained Documents artifacts, and approved knowledge
indexes. Classifies evidence quality for each data point.

## Inputs

- Planning output (outline, section plan, data bindings)
- Source identifiers from triage (Odoo models, Documents directories)
- Evidence requirements (which claims need source backing)

## Outputs

- Grounded data payload with per-item evidence classification
- Evidence classification per data point:
  - `evidence_found` — direct source in Odoo/Documents
  - `evidence_found_with_inference` — conclusion from multiple sources
  - `evidence_missing` — required source not found
  - `evidence_conflicting` — sources disagree

## Grounding priority order

1. Active Odoo record context
2. Linked retained artifacts in Odoo Documents
3. Finance PPM task / milestone / OKR context
4. Approved indexed policy / knowledge sources
5. Allowed external systems (only when explicitly connected)

## Does not own

Request interpretation, artifact creation, quality validation, file retention.
