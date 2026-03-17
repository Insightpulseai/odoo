# Evaluations: Multitenancy Readiness Judge

## Eval Criteria

| Criterion | Weight | Pass Condition |
|-----------|--------|----------------|
| Evidence-based verdict | 30% | Every score backed by test results or documentation |
| Blockers identified | 25% | Critical gaps correctly identified as blockers |
| No false GO | 25% | Does not approve when isolation tests are missing/failing |
| Actionable output | 20% | Blockers have clear remediation steps and timeline |

## Eval Scenarios

### Scenario 1: Missing Isolation Tests
- **Input**: Platform has good SLOs and monitoring but no cross-tenant isolation tests
- **Expected**: NO-GO verdict, isolation testing listed as P1 blocker
- **Fail condition**: GO or CONDITIONAL GO despite missing isolation evidence

### Scenario 2: All Areas Pass
- **Input**: All 5 areas have strong evidence, minor improvements possible
- **Expected**: GO verdict with non-blocking recommendations
- **Fail condition**: NO-GO despite all areas having evidence

### Scenario 3: Partial Chaos Testing
- **Input**: Compute failure tested, DB and network not tested
- **Expected**: CONDITIONAL GO or NO-GO depending on severity of gap
- **Fail condition**: GO verdict with incomplete chaos testing

### Scenario 4: SLO Definition Gap
- **Input**: SLOs defined for enterprise tier only, free and standard undefined
- **Expected**: NO-GO, SLO gaps listed as blocker
- **Fail condition**: Acceptance of undefined SLOs for any tier
