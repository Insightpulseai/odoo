# Platform Runtime Decisions

> Architecture Decision Record (ADR) for runtime selection and reference sample adoption boundaries.

---

## Decision: Microsoft Fabric sample usage boundary

We adopt `Azure-Samples/agentic-app-with-fabric` as a reference pattern for:

- agent operational telemetry capture
- real-time event streaming and KQL/Eventhouse observability
- analytics-sidecar design
- downstream semantic/reporting integration

We do **not** adopt the sample as a transactional runtime baseline.

Fabric remains analytics/telemetry/semantic infrastructure.
Transactional application state remains outside Fabric.

**Reference**: <https://github.com/Azure-Samples/agentic-app-with-fabric>

---

## Decision: Service Fabric exclusion from target runtime

The following references are classified as **concept-only** or **excluded from adoption**:

| Reference | Classification | Reason |
|---|---|---|
| `service-fabric-dotnet-getting-started` | excluded_runtime | Introductory Service Fabric app (stateless/stateful services, Reliable Collections, Actors) |
| `service-fabric-aad-helpers` | excluded_runtime | PowerShell scripts for Azure AD apps/users to authenticate to a Service Fabric cluster |
| `service-fabric-dotnet-standalone-cluster-configuration` | excluded_runtime | Configuration templates for standalone Service Fabric clusters (on-prem or cloud) |
| `azure/service-fabric/samples-cli` | excluded_runtime | Azure CLI + `sfctl` samples for managing Service Fabric clusters, apps, and services |

### Rationale

- These references are specific to Service Fabric cluster creation, configuration, or operations.
- They are **not adopted** as runtime, deployment, or control-plane patterns for the current platform target state.
- The platform target runtime is **Azure Container Apps** (behind Azure Front Door) with **Databricks** for data intelligence and **Foundry/agent runtime** for AI workloads.
- Service Fabric solves cluster-hosted .NET distributed app concerns, which is not the architectural direction for this platform.

### Allowed use

- Conceptual study of service boundaries
- Historical comparison of cluster/app/service lifecycle models
- Migration/reference research only

### Prohibited use

- Introducing Service Fabric as a new workload runtime
- Introducing `sfctl` as an operational control surface
- Creating standalone Service Fabric clusters for the platform baseline
- Service Remoting / Reliable Services / Reliable Actors as a new platform commitment
- AAD bootstrap scripts tied to Service Fabric cluster auth

---

## Decision: Approved runtime baseline

| Lane | Runtime | Status |
|---|---|---|
| ERP / Transactional | Azure Container Apps (Odoo CE 18) | **Active** |
| Data Intelligence | Databricks (Unity Catalog, SQL Warehouse) | **Active** |
| Agent / AI | Azure AI Foundry + agent-platform | **Active** |
| Analytics / Telemetry | Microsoft Fabric (Power BI, Eventhouse) | **Active** |
| Identity | Keycloak (transitional) -> Microsoft Entra ID | **In progress** |
| Edge / Routing | Azure Front Door | **Active** |

---

*Created: 2026-03-22*
