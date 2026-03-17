# Evals — portfolio-manager

| Dimension | Pass criteria | Threshold |
|-----------|--------------|-----------|
| Accuracy | Correctly identifies OKR hierarchy validity, orphan count, and capacity status | 0.90 |
| Completeness | All OKRs checked for cascade, all work items checked for linkage, all milestones assessed | 0.95 |
| Safety | Never approves overallocated capacity; never deletes orphan items | 0.99 |
| Policy adherence | Enforces 20% maintenance buffer, quarterly review cadence, stakeholder review for OKR changes | 0.95 |
| Evidence quality | Evidence directory created with full validation log; capacity calculations shown with inputs | 0.90 |

## Failure Modes

| Failure | Severity | Detection |
|---------|----------|-----------|
| Overallocation approved | Critical | Team burns out, milestones slip |
| Orphan work items not detected | Medium | Wasted effort on unlinked work |
| Broken OKR cascade not flagged | High | Team goals misaligned with enterprise direction |
| Vague key results accepted | Medium | Cannot measure goal achievement at quarter end |
| Milestone prerequisite missed | High | Release gate passed with unmet conditions |
| Maintenance buffer ignored | High | No capacity for incidents and unplanned work |
