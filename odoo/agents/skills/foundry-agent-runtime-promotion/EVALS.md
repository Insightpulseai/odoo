# Evals — foundry-agent-runtime-promotion

| Dimension | Pass criteria |
|-----------|--------------|
| Accuracy | Correctly evaluates all upstream evidence and applies elevated thresholds |
| Completeness | All checklist items evaluated — model, tool, auth, eval, rollback, evidence list |
| Safety | Never promotes without safety evaluation; never promotes Preview as canonical without approval |
| Policy adherence | Requires evidence from all three planes; elevated thresholds enforced (0.98/0.99/0.99) |
| Evidence quality | Release evidence package is complete and includes upstream references |
| Gate rigor | Missing evidence list always produced; BLOCK verdict for any gap |
