# Skill Trigger Tuning — Examples

## Example: odoo-module-scaffolding trigger tuning

### Baseline
- Triggers: "scaffold module", "create odoo module", "new module"
- False positive: "create a new Python module" (not Odoo-specific)
- False negative: "I need a fresh ipai_* addon" (uses different vocabulary)

### Fix
- Description changed: "Scaffolds new Odoo addons with ipai_* naming" → adds "addon" vocabulary
- Trigger added: "new ipai module", "new addon", "scaffold addon"
- Trigger refined: "create module" → "create odoo module" (more specific)

### Result
- Baseline: precision=80%, recall=70%
- After: precision=95%, recall=90%
