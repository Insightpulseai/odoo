# Evals — product-manager

| Dimension | Pass criteria | Threshold |
|-----------|--------------|-----------|
| Accuracy | Correctly identifies spec completeness status (no false PASS on missing files) | 0.90 |
| Completeness | All 4 spec bundle files checked; all acceptance criteria evaluated; all dependencies listed | 0.95 |
| Safety | Never approves a spec with unmeasurable acceptance criteria | 0.99 |
| Policy adherence | Enforces OKR linkage, architecture review, SSOT boundary contracts | 0.95 |
| Evidence quality | Evidence directory created with validation log; cites specific file paths, not generic references | 0.90 |

## Failure Modes

| Failure | Severity | Detection |
|---------|----------|-----------|
| False PASS on incomplete spec bundle | Critical | Downstream build fails on missing plan/tasks |
| Missed unmeasurable criterion | High | QA cannot determine pass/fail at acceptance |
| Orphan spec not flagged | Medium | Feature ships without goal alignment |
| SSOT boundary crossing not detected | High | Cross-domain changes break without contract |
| Scope creep not flagged | Medium | Capacity overrun in current OKR cycle |
