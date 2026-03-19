# Evals — odoo-maintainer-quality-gate

| Dimension | Pass criteria |
|-----------|--------------|
| Accuracy | Correctly identifies development_status, CI state, and dependency chain (elevated: 0.98) |
| Completeness | All quality gate criteria evaluated — no silent skips |
| Safety | Never approves modules with EE dependencies; never approves below Stable for production |
| Policy adherence | Strict gate enforcement — no exceptions to quality thresholds (elevated: 0.99) |
| Evidence quality | Test install logs with test counts, manifest field values, CI status references |
| Verdict quality | Verdict matches gate criteria exactly; CONDITIONAL includes specific actionable conditions |
