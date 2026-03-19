# Evals — odoo-extendability-check

| Dimension | Threshold | Pass criteria |
|-----------|-----------|--------------|
| Accuracy | 0.95 | Correctly identifies oversized methods, hardcoded values, missing hook points, and inheritance violations |
| Completeness | — | All extendability dimensions evaluated — method size, hardcoding, inheritance, hooks, delegation, separation of concerns |
| Safety | 0.99 | Never approves copy-paste instead of _inherit; never approves monolithic methods that block submodule extension |
| Policy adherence | — | Violations mapped to correct guideline principle; refactoring suggestions are concrete and actionable |
| Evidence quality | — | Every violation includes file path, line number/range, and the specific code pattern |
| Refactoring quality | — | Suggested method extractions include meaningful names and clear responsibility boundaries |
