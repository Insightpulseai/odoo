# iot-analytics-fit-assessment — Checklist

## Signal Assessment
- [ ] Data sources identified (devices/sensors vs. APIs/databases/SaaS)
- [ ] Latency requirement quantified (seconds, minutes, hours)
- [ ] Volume characterized (events/second, sustained vs. burst)
- [ ] Device management needs assessed (provisioning, firmware, twin state)
- [ ] Time-series analytics scale evaluated (data points, retention, query patterns)

## IN_SCOPE Criteria (need 2+ for IN_SCOPE)
- [ ] Physical devices generating telemetry
- [ ] Sub-second latency requirement
- [ ] Sustained high volume (>10K events/second)
- [ ] Device management needed
- [ ] Time-series analytics at billions-of-rows scale

## OUT_OF_SCOPE Criteria (any one is sufficient)
- [ ] Data from APIs, databases, or SaaS (not devices)
- [ ] "Real-time" means minutes, not seconds
- [ ] Volume manageable with batch or CDC
- [ ] No device management
- [ ] Analytics served from standard lakehouse (Delta Lake + SQL)

## Verdict
- [ ] Verdict stated: IN_SCOPE / OUT_OF_SCOPE / CONDITIONAL
- [ ] Justification cites specific signals from workload description
- [ ] Alternative recommended if OUT_OF_SCOPE
- [ ] Clarification questions listed if CONDITIONAL
- [ ] No scope expansion beyond what signals justify
