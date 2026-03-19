# iot-analytics-fit-assessment

Judge skill that assesses whether streaming telemetry or IoT analytics is actually in scope for a workload. Returns IN_SCOPE, OUT_OF_SCOPE, or CONDITIONAL to prevent accidental expansion into IoT architecture.

## When to use
- Workload mentions streaming, telemetry, sensors, or IoT
- Architecture review includes real-time data ingestion
- Scope assessment for new data platform initiative
- Technology selection involving Azure Data Explorer or IoT Hub

## Key rule
Default verdict is OUT_OF_SCOPE. IoT analytics is an optional adjacent benchmark, not a primary architecture concern. "Real-time dashboards" or "API refresh every 5 minutes" do not constitute IoT scope. Only genuine device telemetry, sub-second latency, or high-volume streaming (>10K events/sec) triggers IN_SCOPE.

## Source
"IoT analytics with Azure Data Explorer and Azure IoT Hub" -- Microsoft Learn architecture card.

## Cross-references
- `agents/knowledge/benchmarks/azure-databricks-architecture-cards.md` (Card 4)
- `agent-platform/ssot/learning/databricks_architecture_card_map.yaml`
