# Eval Template — Agent Skill

## Required eval dimensions

| Dimension | Pass criteria |
|-----------|--------------|
| Benchmark extraction | Correctly identifies the relevant benchmark pattern from source material |
| No forced dependency | Does not introduce mandatory SAP/vendor dependency into recommendations |
| Target translation | Correctly maps benchmark to actual platform (Odoo on Azure) |
| Guardrail compliance | Respects all guardrails listed in skill-contract.yaml |
| Output shape | Produces all required output fields in normalized format |
| Evidence quality | Cites specific source material, not generic summaries |

## Eval structure

Each eval case should include:
- **Input**: A realistic request that triggers this skill
- **Expected output**: The correct benchmark extraction + translation
- **Anti-pattern**: What the skill must NOT do (e.g., prescribe SAP products)
- **Pass/fail criteria**: Deterministic check for each dimension above
