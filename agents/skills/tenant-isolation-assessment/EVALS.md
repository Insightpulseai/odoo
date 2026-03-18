# Evaluations: Tenant Isolation Assessment

## Eval Criteria

| Criterion | Weight | Pass Condition |
|-----------|--------|----------------|
| Assessment completeness | 25% | All four domains assessed with evidence |
| Verdict accuracy | 25% | Verdict matches actual isolation state |
| Finding severity accuracy | 20% | Severity correctly assigned per impact |
| Remediation actionability | 15% | Each gap has a specific, actionable remediation |
| Evidence quality | 15% | Findings backed by test results, not assumptions |

## Eval Scenarios

### Scenario 1: Well-Isolated Platform

- **Input**: Platform with database-per-tenant, Entra ID, private endpoints, TDE
- **Expected**: Verdict: ISOLATED with evidence in all four domains
- **Fail condition**: Verdict other than ISOLATED for a properly isolated platform

### Scenario 2: Platform with Known Network Gap

- **Input**: Platform with RLS and Entra ID, but PostgreSQL on public IP
- **Expected**: Verdict: PARTIAL with HIGH finding for network, remediation plan
- **Fail condition**: Verdict: ISOLATED (missed the network gap)

### Scenario 3: Platform with Critical Data Gap

- **Input**: Shared database without RLS, application-level filtering only
- **Expected**: Verdict: NOT_ISOLATED with CRITICAL data isolation finding
- **Fail condition**: Verdict: PARTIAL or ISOLATED (underestimated severity)

### Scenario 4: Mixed Findings Across Domains

- **Input**: Platform with strong identity but weak data isolation and partial network
- **Expected**: Verdict reflects worst-case domain, remediation prioritized by severity
- **Fail condition**: Verdict averaged across domains instead of worst-case

## Grading Rubric

| Grade | Criteria |
|-------|----------|
| A | All 5 criteria pass, verdict accurate in all 4 scenarios |
| B | 4/5 criteria pass, verdict accurate in scenarios 1-3 |
| C | 3/5 criteria pass, critical gaps identified |
| F | Verdict inaccurate — missed critical isolation gaps |

## Pass Criteria

Judge skill must achieve grade A to be trusted for pre-production security gates.
