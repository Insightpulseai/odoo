# Plan — Azure Assessment Harness

## Implementation stages

### Stage 1 — Build the answer pack

Creator agents produce:
- question-by-question draft answers per assessment family
- cited evidence per answer (file path, command output, or Resource Graph query)
- confidence level per answer (high / medium / low)
- missing proof list per domain

### Stage 2 — Run judges

Judge agents:
- score each pillar/domain
- challenge optimistic answers
- downgrade where evidence is only "present" but not "governed" or "proven"
- flag answer-risky postures

### Stage 3 — Synthesize

Synthesis judge outputs:
- internal normalized scorecard
- recommended official portal answer posture
- delta list against current internal assessment (R3)
- blocker vs recommendation split

### Stage 4 — Compare against official portal

After running the real Microsoft assessment:
- export official results to CSV
- save to `docs/evidence/assessments/`
- compare internal simulator score vs official portal score
- measure recommendation overlap
- identify blind spots unique to each
- update calibration model

## Artifact ownership

| Artifact | Location | Owner |
|---|---|---|
| Spec bundle | spec/azure-assessment-harness/ | agents |
| Personas | agents/registry/assessment_personas.yaml | agents |
| Judges | agents/registry/assessment_judges.yaml | agents |
| Skills (5) | agents/skills/assessment-*/ | agents |
| Assessment map | ssot/assessment/microsoft_assessments_map.yaml | ssot |
| Scoring rubric | ssot/assessment/scoring_rubric.yaml | ssot |
| Persona role map | ssot/assessment/persona_role_map.yaml | ssot |
| Runbook | docs/evidence/assessments/AZURE_ASSESSMENT_RUNBOOK.md | docs |
| Results template | docs/evidence/assessments/AZURE_ASSESSMENT_RESULTS_TEMPLATE.md | docs |
| Comparison CSV | docs/evidence/assessments/AZURE_ASSESSMENT_COMPARISON.csv | docs |

## Dependency model

- Evidence Harvester depends on: IPAI_PLATFORM_ANALYSIS.md, ssot/azure/, infra/azure/, docs/architecture-review/
- Answer Drafter depends on: Evidence Harvester output + microsoft_assessments_map.yaml
- Score Judge depends on: Answer Drafter output + scoring_rubric.yaml
- Gap Challenger depends on: Score Judge output
- Calibration depends on: all judge outputs + (later) official Microsoft results

## Risks

- Self-assessment bias (mitigated by skeptical judges)
- Evidence staleness (mitigated by harvester pulling from current-state artifacts)
- Scoring drift from Microsoft methodology (mitigated by calibration judge + post-official comparison)
- Scope creep into building a hosted assessment platform (out of scope per constitution)

## Exit criteria

- All 7 assessment families have draft answer packs
- Judges have scored and challenged the full pack
- Calibration judge has produced confidence ratings
- Runbook documents the full workflow
- Results template is ready for official assessment comparison
