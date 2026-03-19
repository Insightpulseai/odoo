# Checklist — azure-load-testing-cli-patterns

## Pre-test

- [ ] Target environment identified (dev/staging — NOT prod without approval)
- [ ] Load testing resource created or exists
- [ ] Test plan defined (JMeter JMX or quick test)
- [ ] Load profile defined (virtual users, ramp-up, duration)
- [ ] Success criteria defined (response time, error rate, throughput)
- [ ] Test data contains no PII or real user data

## Test execution

- [ ] Test created with az load test create
- [ ] Engine instances configured
- [ ] Test run started with unique run ID
- [ ] Duration bounded (not open-ended)
- [ ] Virtual users bounded (not unlimited)

## Results analysis

- [ ] Results collected with az load test-run metrics
- [ ] P50/P95/P99 response times recorded
- [ ] Error rate calculated
- [ ] Throughput measured
- [ ] Pass/fail assessed against criteria

## Post-test

- [ ] Results saved as evidence
- [ ] Recommendations documented
- [ ] Test resources cleaned up (if temporary)
- [ ] CI/CD integration configured (if needed)

## Production tests (additional gates)

- [ ] Explicit written approval obtained
- [ ] Traffic controls in place (rate limiting, circuit breaker)
- [ ] Monitoring active during test
- [ ] Rollback plan documented
- [ ] Test window communicated to stakeholders
