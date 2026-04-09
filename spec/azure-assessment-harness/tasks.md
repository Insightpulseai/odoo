# Tasks — Azure Assessment Harness

## 1. Establish harness artifacts
- [x] Create spec/azure-assessment-harness/ bundle
- [ ] Create agents/registry/assessment_personas.yaml
- [ ] Create agents/registry/assessment_judges.yaml
- [ ] Create ssot/assessment/microsoft_assessments_map.yaml
- [ ] Create ssot/assessment/scoring_rubric.yaml
- [ ] Create ssot/assessment/persona_role_map.yaml

## 2. Build skills
- [ ] Create agents/skills/assessment-evidence-harvester/SKILL.md
- [ ] Create agents/skills/assessment-answer-drafter/SKILL.md
- [ ] Create agents/skills/assessment-score-judge/SKILL.md
- [ ] Create agents/skills/assessment-gap-challenger/SKILL.md
- [ ] Create agents/skills/assessment-calibration/SKILL.md

## 3. Build operational docs
- [ ] Create docs/evidence/assessments/AZURE_ASSESSMENT_RUNBOOK.md
- [ ] Create docs/evidence/assessments/AZURE_ASSESSMENT_RESULTS_TEMPLATE.md
- [ ] Create docs/evidence/assessments/AZURE_ASSESSMENT_COMPARISON.csv

## 4. Run Stage 1 — evidence and answer pack
- [ ] Run Evidence Harvester against current repo state
- [ ] Run Answer Drafter for all 7 assessment families
- [ ] Collect missing proof list

## 5. Run Stage 2 — judges
- [ ] Run all 7 judges against answer pack
- [ ] Run Calibration Judge
- [ ] Produce internal scorecard

## 6. Run Stage 3 — synthesize
- [ ] Produce delta against R3 assessment
- [ ] Flag answer-safe vs answer-risky postures
- [ ] Produce recommended official portal answer guide

## 7. Run Stage 4 — compare (post-official)
- [ ] Run official Microsoft assessment at learn.microsoft.com/assessments/
- [ ] Export CSV results
- [ ] Save to docs/evidence/assessments/
- [ ] Compare internal vs official scores
- [ ] Update calibration model
