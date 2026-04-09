# Fit-Gap Analysis Template

## Instructions

For each business requirement:
1. Document the requirement (business language)
2. Classify: F (Fit) | C (Config) | O (OCA) | D (Delta/custom) | E (External) | G (Gap)
3. Identify the Odoo/OCA/Azure implementation surface
4. Estimate effort: S (< 1 day) | M (1-3 days) | L (3-10 days) | XL (> 10 days)
5. Assess risk: Low | Medium | High
6. Set priority: P1 (must-have) | P2 (should-have) | P3 (nice-to-have) | P4 (future)

## Template

| # | Requirement | Classification | Implementation Surface | Effort | Risk | Priority | Notes |
|---|------------|---------------|----------------------|--------|------|----------|-------|
| 1 | | | | | | | |
| 2 | | | | | | | |

## Classification Decision Tree

```
Does Odoo CE handle this out of the box?
  YES → F (Fit)
  NO  → Can it be done through Odoo configuration (settings, data records)?
    YES → C (Config)
    NO  → Does an OCA 18.0 module exist and is it stable?
      YES → O (OCA)
      NO  → Is this achievable with a custom ipai_* module (< 10 days)?
        YES → D (Delta)
        NO  → Can an external service handle this?
          YES → E (External) — specify Azure service
          NO  → G (Gap) — document and defer
```

## Summary Table (fill after analysis)

| Classification | Count | Total Effort | Action |
|---------------|-------|-------------|--------|
| F (Fit) | | | No action needed |
| C (Config) | | | Configuration sprint |
| O (OCA) | | | Module installation + testing |
| D (Delta) | | | Custom development |
| E (External) | | | Integration development |
| G (Gap) | | | Document and defer |
| **Total** | | | |

## Go/No-Go Criteria

- All P1 requirements must be F, C, O, or D with effort <= L
- No more than 20% of requirements classified as D
- No P1 requirements classified as G
- Total custom development effort < 40% of total effort
- All G items have documented workaround or deferral justification
