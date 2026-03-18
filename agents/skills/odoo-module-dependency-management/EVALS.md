# Evals — odoo-module-dependency-management

| Dimension | Pass criteria |
|-----------|--------------|
| Accuracy | Correctly resolves full transitive dependency chain and identifies conflicts |
| Completeness | All dependencies checked — direct and transitive; no silent skips |
| Safety | Never introduces Enterprise dependencies; never modifies OCA source |
| Policy adherence | Config -> OCA -> Delta philosophy enforced; manifest alignment verified |
| Evidence quality | Includes __manifest__.py contents and dependency resolution trace |
| Blocker identification | Enterprise violations and missing dependencies flagged as blockers |
