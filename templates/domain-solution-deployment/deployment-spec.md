# Deployment Spec — <Domain Solution Name>

> **Status**: Draft | Ready | Deployed
> **Benchmark**: Microsoft Business Process Solutions deployment pattern
> **Spec bundle**: `spec/<slug>/`

---

## 1. Workload Item

| Field | Value |
|-------|-------|
| **Solution name** | `<named solution artifact>` |
| **Solution type** | `<semantic-model \| agent \| dashboard \| composite>` |
| **Owning repo** | `<repo>` |
| **Owning plane** | `<data-intelligence \| platform \| agent-platform \| web>` |
| **Spec bundle** | `spec/<slug>/` |

## 2. Deployment Boundary

| Field | Value |
|-------|-------|
| **Workspace / project** | `<Databricks workspace \| Fabric workspace \| ACA resource group>` |
| **Resource group** | `<Azure RG>` |
| **Capacity / SKU** | `<Fabric capacity \| Databricks cluster policy \| ACA plan>` |

## 3. Required Roles

| Action | Required role | Identity |
|--------|--------------|----------|
| Enable feature / workload | `<Global Admin \| Fabric Admin \| RG Owner>` | `<who>` |
| Create workspace / project | `<Workspace Owner \| Contributor>` | `<who>` |
| Deploy solution artifact | `<Contributor \| Pipeline identity>` | `<who>` |
| Create orchestration connection | `<Contributor + data access>` | `<who>` |
| Onboard source systems | `<Contributor + source credentials>` | `<who>` |

## 4. Target Region & Data Residency

| Field | Value |
|-------|-------|
| **Primary region** | `<e.g., southeastasia>` |
| **Business data location** | `<stays in primary region>` |
| **Metadata / control plane** | `<geography-level backend \| same region>` |
| **Data residency constraint** | `<regulatory or policy constraint, if any>` |

## 5. Orchestration / Metadata Connection

> **Rule**: This connection MUST be provisioned and verified before any source onboarding.

| Field | Value |
|-------|-------|
| **Connection type** | `<Fabric SQL DB \| Databricks catalog \| Azure PG \| other>` |
| **Connection target** | `<server/database/catalog>` |
| **Connection identity** | `<managed identity \| service principal>` |
| **Connection ID** | `<captured after creation>` |
| **Purpose** | `<orchestration metadata, extraction state, processing coordination>` |

### Pre-onboarding checklist

- [ ] Connection provisioned
- [ ] Connection ID captured
- [ ] Identity has required data access roles
- [ ] Connection health verified (SELECT 1 or equivalent)

## 6. Source Onboarding Sequence

> **Rule**: Sources are onboarded in order. Each source depends on the orchestration connection being live.

| Order | Source | Method | Landing | Prerequisites |
|-------|--------|--------|---------|---------------|
| 1 | `<primary source>` | `<Fabric Mirroring \| ADF \| API>` | `<Bronze \| staging>` | `<orchestration connection live>` |
| 2 | `<secondary source>` | `<method>` | `<landing>` | `<source 1 complete>` |
| 3 | `<reference data>` | `<method>` | `<landing>` | `<none>` |

## 7. Deployment Sequence

```text
1. Verify required roles
2. Provision deployment boundary (workspace/RG)
3. Create orchestration connection
4. Verify orchestration connection health
5. Deploy solution artifact
6. Onboard source 1
7. Verify source 1 landing
8. Onboard source 2..N
9. Run post-deploy verification
10. Publish deployment attestation
```

## 8. Post-Deploy Verification

| Check | Method | Pass criteria |
|-------|--------|--------------|
| Orchestration connection health | `<SQL ping \| API call>` | `<response OK>` |
| Source landing freshness | `<row count \| timestamp check>` | `<data within SLA>` |
| Semantic model integrity | `<reconciliation query>` | `<totals match source>` |
| Dashboard / template render | `<HTTP \| Power BI API>` | `<renders without error>` |
| Agent grounding | `<test query>` | `<cites semantic source>` |

## 9. Rollback

| Field | Value |
|-------|-------|
| **Rollback target** | `<previous artifact version \| snapshot ID>` |
| **Rollback method** | `<redeploy previous image \| restore snapshot>` |
| **Data rollback** | `<append-only — no data rollback needed \| snapshot restore>` |

## 10. Post-Deploy Next Steps

- [ ] Validate freshness SLA after first full refresh cycle
- [ ] Enable monitoring / alerting for orchestration connection
- [ ] Wire agent tools to semantic model endpoints
- [ ] Update domain solution registry
