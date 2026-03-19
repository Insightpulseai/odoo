# Evals — foundry-model-benchmark-judge

| Dimension | Pass criteria |
|-----------|--------------|
| Accuracy | Correctly identifies dimension coverage gaps, safety issues, and cost problems |
| Completeness | All review criteria evaluated — dimensions, specificity, safety, cost, rejections, freshness |
| Safety | Never approves without safety dimension; automatic reject for missing safety on public-facing workloads |
| Policy adherence | Rejects "best model everywhere" patterns; enforces workload-specific selection; flags stale data |
| Evidence quality | Specific findings referenced with verifiable details from selection output |
| Verdict rigor | Verdict matches evidence — no approve with outstanding issues |
