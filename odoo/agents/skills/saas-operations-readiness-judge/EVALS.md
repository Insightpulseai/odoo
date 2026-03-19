# Evaluations: SaaS Operations Readiness Judge

## Eval Criteria

| Criterion | Weight | Pass Condition |
|-----------|--------|----------------|
| Assessment completeness | 20% | All six domains assessed with specific metrics |
| Verdict accuracy | 25% | Verdict matches actual operational state |
| Blocker identification | 20% | Critical gaps correctly identified as blockers |
| Condition specificity | 15% | Conditions have clear acceptance criteria |
| Evidence quality | 20% | Scores backed by metrics, not assumptions |

## Eval Scenarios

### Scenario 1: Fully Ready Platform

- **Input**: All six domains at acceptable or strong maturity
- **Expected**: Verdict: READY with evidence for each domain score
- **Fail condition**: Verdict other than READY for a genuinely ready platform

### Scenario 2: Platform with Monitoring Gaps

- **Input**: Five domains acceptable, monitoring at 60% coverage with no tracing
- **Expected**: Verdict: CONDITIONAL with specific monitoring conditions
- **Fail condition**: Verdict: READY (ignored monitoring weakness) or NOT_READY (over-reacted)

### Scenario 3: Platform with No Incident Response

- **Input**: No runbooks, no on-call, no escalation — other domains adequate
- **Expected**: Verdict: NOT_READY with incident response as blocker
- **Fail condition**: Verdict: CONDITIONAL (under-estimated criticality of missing incident response)

### Scenario 4: Platform with Multiple Weak Domains

- **Input**: Three domains weak (monitoring, scaling, compliance), none at blocker level
- **Expected**: Verdict: CONDITIONAL with conditions for each weak domain
- **Fail condition**: Verdict: READY (ignored multiple weaknesses)

## Grading Rubric

| Grade | Criteria |
|-------|----------|
| A | All 5 criteria pass, verdict accurate in all 4 scenarios |
| B | 4/5 criteria pass, verdict accurate in scenarios 1-3 |
| C | 3/5 criteria pass, blockers correctly identified |
| F | Verdict inaccurate — missed blockers or false READY |

## Pass Criteria

Judge skill must achieve grade A to be trusted for production launch gates. Grade B acceptable for non-critical assessments (quarterly reviews).
