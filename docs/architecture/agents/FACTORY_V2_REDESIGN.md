# Architecture: Agent Factory V2 (Governance as Code)

## Overview
Agent Factory V2 evolves from a static registry into an active governance plane where maturity transitions (L1 -> L5) are governed by machine-verifiable SSOT contracts.

## Key Design Pillars

### 1. Machine-Readable Promotion Rails
- **Concept**: Promotion is no longer a manual sign-off but a result of a `promotion_gate` verifying specific evidence hashes.
- **Schema**: Introducing `ipai.governance.promotion.v2` which maps maturity levels to required SSOT artifacts.

### 2. Evidence-Driven Maturity
- **L1 (Modelled)**: PRD + SSOT Bundle exists.
- **L3 (Verified)**: Red Team + Acceptance Pack pass.
- **L5 (Stable)**: 5 real production soak cycles verified by `soak-rollup.json`.

### 3. Automated Quarantine (Fail-Closed)
- If an agent generates an anomaly that deviates from its `runtime_contract`, the Factory V2 will automatically revoke its `production-stable` status and move it to `quarantined`.

## Proposed Promotion Policy Schema
```yaml
schema: ipai.governance.policy.v2
agent_id: any
levels:
  L3:
    require:
      - red_team_summary.status == "PASSED"
      - acceptance_fixtures.coverage >= 0.95
  L5:
    require:
      - production_soak.cycles >= 5
      - production_soak.stability == 1.0
      - illegal_posts == 0
```

## Next Steps
1. Define the formal JSON schema for the V2 Promotion Policy.
2. Implement a `Factory Validator` script to audit existing agent passports against the new policy.
