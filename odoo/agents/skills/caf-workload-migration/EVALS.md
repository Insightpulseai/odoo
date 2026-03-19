# Evals — caf-workload-migration

| Dimension | Pass criteria |
|-----------|--------------|
| Accuracy | Correctly identifies workload dependencies and selects appropriate migration pattern |
| Completeness | Cutover runbook covers all steps; rollback procedure is documented and tested |
| Safety | Never executes cutover without tested rollback; never decommissions source without validation |
| Data integrity | Data validation includes row counts, checksums, and functional verification |
| Evidence quality | Migration evidence includes logs, timing, validation results, and rollback test results |
| Dependency awareness | Migration sequencing respects workload dependencies — no orphaned services |
