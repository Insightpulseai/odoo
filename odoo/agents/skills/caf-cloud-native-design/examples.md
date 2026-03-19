# Examples — caf-cloud-native-design

## Example 1: AI Agent service (event-driven on ACA)

**Input**: Design a cloud-native AI agent service that processes user requests asynchronously.

**Output**:
- Requirements: Process AI prompts, route to correct model, return structured results, handle 100 req/min
- Architecture: Event-driven with async processing
- Compute: ACA with Dapr for pub/sub and state management
  - API gateway container (receives requests, publishes to Service Bus)
  - Worker container (subscribes to Service Bus, calls Azure OpenAI, publishes results)
  - Justification: ACA + Dapr provides event-driven primitives without AKS overhead
- Data: Redis Cache for session state, PostgreSQL for audit log, Blob Storage for artifacts
- Events: Service Bus topic per agent type, dead-letter for failures, at-least-once delivery
- DevOps: GitHub Actions build, ACR push, ACA revision deployment
- Observability: Application Insights with distributed tracing, custom metrics for model latency
- WAF: Reliability (retry + DLQ), Security (managed identity), Cost (scale-to-zero), Ops (structured logs), Perf (KEDA autoscaling)

## Example 2: Document processing pipeline (serverless)

**Input**: Design a serverless document processing pipeline (upload, OCR, classify, store).

**Output**:
- Requirements: Process PDF uploads, extract text via OCR, classify document type, store results
- Architecture: Serverless pipeline with event triggers
- Compute: Azure Functions (Blob trigger → OCR → classify → store)
  - Function 1: Blob trigger on upload container
  - Function 2: Call Document Intelligence API
  - Function 3: Classify using Azure OpenAI
  - Function 4: Store results in PostgreSQL + Blob metadata
  - Cold start mitigation: Premium plan for production, Consumption for dev
- Data: Blob Storage (documents), PostgreSQL (metadata + classifications)
- Events: Event Grid for blob creation, Function chaining via output bindings
- DevOps: GitHub Actions, separate Function App per environment
- Observability: Application Insights with function-level tracing

## Example 3: AKS justification (rejected)

**Input**: Evaluate AKS for running Odoo workload.

**Output**:
- Assessment: AKS NOT JUSTIFIED for current requirements
- Justification:
  - Odoo is a monolith, not microservices — no benefit from service mesh
  - ACA provides sufficient scaling (KEDA) and ingress (Envoy)
  - AKS management overhead (node pools, upgrades, RBAC) exceeds value for solo operator
  - AKS minimum cost ($150/mo+) vs ACA ($50/mo for current scale)
- Recommendation: Stay on ACA. Revisit AKS only if: >50 containers, custom networking required, or GPU workloads needed
- ADR: "Prefer ACA over AKS until proven insufficient"
