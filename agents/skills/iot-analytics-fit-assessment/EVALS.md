# iot-analytics-fit-assessment — Evaluation Criteria

## Accuracy (target: 0.95)
- Verdict correctly classifies workloads (IoT vs. non-IoT)
- Signal analysis correctly identifies data source types
- Latency and volume thresholds applied correctly

## Completeness (target: 0.90)
- All relevant signals from workload description are analyzed
- Alternative recommendation provided when OUT_OF_SCOPE
- Clarification questions provided when CONDITIONAL

## Safety (target: 0.99)
- No false IN_SCOPE verdicts for non-IoT workloads (prevents unnecessary complexity)
- No false OUT_OF_SCOPE verdicts for genuine IoT workloads (prevents under-engineering)
- Default-to-OUT_OF_SCOPE bias is correctly applied

## Policy Adherence (target: 0.99)
- Optional adjacent benchmark guardrail respected
- "Real-time" alone does not trigger IN_SCOPE
- API refresh intervals correctly classified as micro-batch
- IoT Hub recommended only when device management is needed
- ADX recommended only for time-series analytics at scale

## Failure Modes
| Mode | Detection | Mitigation |
|------|-----------|------------|
| False IN_SCOPE | Non-IoT workload classified as IoT | Verify data sources are physical devices |
| False OUT_OF_SCOPE | Genuine IoT classified as batch | Check for sub-second latency or device management |
| Scope creep | IoT architecture recommended for API data | Enforce API vs. device source classification |
| Ambiguity acceptance | CONDITIONAL without clarification questions | Require specific questions for CONDITIONAL verdicts |
| Complexity bias | Recommending IoT for simple workload | Apply default-to-OUT_OF_SCOPE principle |
