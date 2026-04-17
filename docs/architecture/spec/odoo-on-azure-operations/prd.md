# PRD: Odoo on Azure Workload Operations Platform

## 1. Summary

Build an Azure-native workload operations platform for Odoo that provides the Odoo equivalent of a SAP-on-Azure operating model.

This product is not just "host Odoo on Azure."
It is a workload-specific operations layer that standardizes:

- landing-zone-aligned deployment
- workload/stamp provisioning
- runtime operations
- backup and disaster recovery
- monitoring and health checks
- upgrade and migration readiness
- release governance
- analytics and AI extension readiness

The product must support both:
- shared multitenant SMB stamps
- more isolated enterprise or regulated workload stamps

---

## 2. Problem

Many Odoo-on-Azure implementations stop at infrastructure provisioning or container hosting.

That leaves major gaps:
- no workload-specific control plane
- weak backup/restore validation
- unclear disaster recovery posture
- no standardized health and drift checks
- ad hoc runtime upgrades and promotion
- incomplete governance around secrets, monitoring, and workload security
- no structured operating model for extending Odoo into analytics and AI services

Enterprise ERP on Azure requires a workload-specific operational model, not just compute and networking.

---

## 3. Goals

### Primary goals

1. Create a shared platform + workload operating model for Odoo on Azure.
2. Make Odoo workload operations first-class and repeatable.
3. Support deployment stamps as the default unit of workload rollout.
4. Define backup, restore, DR, and recovery evidence as baseline capabilities.
5. Standardize monitoring, health validation, and drift assessment.
6. Use Azure DevOps + IaC as the canonical delivery and operations mechanism.
7. Keep Odoo as the transactional business core while enabling governed analytics and AI extensions.

### Secondary goals

1. Reduce ambiguity between platform services and workload services.
2. Support staged rollout from SMB multitenant deployments to more isolated enterprise deployments.
3. Produce machine-readable state and evidence for operations and audits.
4. Enable future specialist copilot/agent workloads without re-architecting the operational core.

---

## 4. Non-Goals

1. This PRD does not replace Odoo functional product requirements.
2. This PRD does not define billing/commercial packaging in detail.
3. This PRD does not implement specialist copilot or tax/compliance behavior directly.
4. This PRD does not require one single isolation model for all tenants or all services.
5. This PRD does not prescribe a single exact Azure resource SKU set.

---

## 5. Users

### Primary users
- platform operator
- workload operator
- release operator
- infrastructure owner
- security/governance owner

### Secondary users
- implementation partner
- analytics owner
- AI/platform extension owner
- tenant operations lead

---

## 6. Product Principles

1. **Landing zone first, workload second**
   Shared platform services are established first, then workload stamps inherit and specialize.

2. **Operate by workload, not by raw infrastructure**
   Odoo must have a workload-specific operating model with health, backup, DR, and release discipline.

3. **Stamps are first-class deployment units**
   Roll out one stamp or one bounded stamp batch at a time.

4. **Assess continuously**
   Monitoring, drift checks, and periodic operational reassessment are baseline product behavior.

5. **Automate by default**
   IaC and Azure DevOps are the standard execution paths.

6. **Recovery is a product capability**
   Backup, restore, RPO/RTO, and DR evidence are required platform features.

---

## 7. Product Surface

The baseline product must support these capabilities:

1. Provision shared Odoo-on-Azure platform foundations
2. Provision one Odoo workload stamp
3. Deploy and update Odoo runtime
4. Create and validate staging workload
5. Run backup and restore validation
6. Define and validate DR posture
7. Run workload health checks
8. Run workload inventory/drift checks
9. Promote workload safely through environments
10. Provide governed read-only analytics access
11. Support workload extension into analytics and AI planes

---

## 8. Architecture Model

### 8.1 Shared platform layer

Shared services include:
- identity and access foundations
- secret/certificate/key management
- edge/network governance
- monitoring and logging foundations
- policy/governance controls
- shared CI/CD control plane

### 8.2 Workload stamp layer

Each Odoo workload stamp includes:
- workload-specific runtime resources
- workload-specific data and storage surfaces
- workload-specific monitoring and health metadata
- workload-specific backup and recovery configuration
- workload-specific release evidence

### 8.3 Extension layers

The platform must support extension into:
- analytics/reporting plane
- AI/agent plane
- integration/orchestration plane

Odoo remains the transactional SoR for business operations.

---

## 9. Functional Requirements

### FR-001 Shared platform baseline
The system shall provide a shared Azure platform baseline that Odoo workload stamps can inherit.

### FR-002 Workload stamp provisioning
The system shall provision Odoo as workload stamps, not as ad hoc one-off environments.

### FR-003 Multi-tier workload support
The system shall support a multi-tier Odoo workload architecture with explicit separation of critical runtime components.

### FR-004 Backup policy
The system shall define and execute workload backup policy, including scheduling and retention.

### FR-005 Restore validation
The system shall support restore validation and recovery evidence generation.

### FR-006 Disaster recovery posture
The system shall define DR stance, including target recovery objectives and recovery workflow expectations.

### FR-007 Health checks
The system shall run workload health checks for runtime, dependencies, and operational readiness.

### FR-008 Inventory and drift checks
The system shall support inventory validation and configuration drift checks for workload resources.

### FR-009 Release orchestration
The system shall orchestrate shared-platform, workload-stamp, and runtime changes through Azure DevOps pipelines.

### FR-010 Environment-gated promotion
The system shall support protected promotion across environments with checks/approvals where required.

### FR-011 Secret and key governance
The system shall use governed secret/key management and avoid plaintext runtime secrets.

### FR-012 Monitoring baseline
The system shall emit workload monitoring signals sufficient for availability, performance, and operations analysis.

### FR-013 Analytics access path
The system shall support a governed read-only path for analytics/reporting consumers.

### FR-014 Extension readiness
The system shall support future AI and analytics integrations without changing Odoo's role as the transactional core.

---

## 10. Non-Functional Requirements

### NFR-001 Reliability
The platform must support workload designs that reduce single points of failure and make recovery behavior explicit.

### NFR-002 Security
The platform must support governed access, protected secrets, encrypted data paths, and workload telemetry.

### NFR-003 Operational excellence
The platform must support repeatable SOPs, assessments, monitoring, and automation.

### NFR-004 Performance efficiency
The platform must support workload sizing, scaling, and architecture choices appropriate to tenant/stamp class.

### NFR-005 Cost optimization
The platform must support cost-aware deployment patterns and right-sized workload placement.

### NFR-006 Recoverability
Recovery expectations must be explicit, testable, and evidenced.

### NFR-007 Auditability
Deployments, health checks, drift checks, backup/restore operations, and promotions must produce evidence.

---

## 11. Delivery Model

The product uses Azure DevOps as the sole CI/CD system.

The target pipeline topology is:

1. `ci-validation`
2. `platform-shared-delivery`
3. `stamp-delivery`
4. `runtime-delivery`
5. `quality-governance`

IaC is the default provisioning and change mechanism.

---

## 12. Environment Model

### Shared environments
- shared-dev
- shared-staging
- shared-prod

### Workload/stamp environments
- stamp-dev
- stamp-staging
- stamp-prod

Promotion policy:
- dev is low-friction
- staging is validation-oriented
- prod is protected and evidence-gated

---

## 13. Workload Operations Lifecycle

### Phase A — Platform baseline
- provision shared foundations
- validate governance and observability surfaces

### Phase B — Workload stamp creation
- provision stamp
- apply workload policy
- bind workload metadata

### Phase C — Runtime rollout
- deploy/update runtime
- run smoke checks
- publish evidence

### Phase D — Ongoing operations
- monitor
- run health checks
- run drift checks
- validate backup posture
- reassess against workload pillars

### Phase E — Recovery and continuity
- restore drill
- DR rehearsal where required
- update recovery evidence

---

## 14. Success Metrics

### Operational metrics
- workload deployments are repeatable and environment-gated
- workload health checks run successfully and consistently
- backup and restore validation exists for protected environments
- drift/inventory checks identify configuration issues before incidents

### Governance metrics
- shared vs workload responsibilities are explicit
- secrets are governed
- release evidence is machine-readable and reviewable

### Architecture metrics
- stamps can be deployed independently
- runtime and platform rollout are not tightly coupled
- analytics/AI extensions do not break workload operating discipline

---

## 15. Risks

1. Treating Odoo as "just another app" instead of a workload with explicit operating requirements
2. Mixing shared platform and workload change into one undifferentiated delivery path
3. Claiming DR readiness without restore evidence
4. Overusing self-hosted/private deployment paths where hosted execution would suffice
5. Extending into analytics/AI without a governed workload boundary

---

## 16. Open Questions

1. What is the canonical stamp metadata contract?
2. Which workloads require stricter isolation versus shared multitenant stamps?
3. What are the minimum Odoo workload health checks for promotion?
4. What are the required RPO/RTO targets by environment or customer class?
5. Which analytics read-paths are canonical first: direct reporting role, lakehouse extraction, or both?

---

## 17. MVP Scope

### Include in MVP
- shared platform/workload split
- one Odoo workload stamp model
- Azure DevOps + IaC delivery baseline
- health checks
- backup policy
- restore validation contract
- environment-gated promotion
- machine-readable evidence publication

### Exclude from MVP
- full multi-region active/active design
- advanced workload autoscaling policy
- autonomous AI/tax specialist operations
- comprehensive commercial packaging and SLA catalog

---

## 18. Benchmark Reference

Operational benchmark: **SAP on Azure / SAP on Microsoft Cloud**

Sources:
- [SAP on Azure](https://learn.microsoft.com/en-us/azure/sap/)
- [SAP on Azure Overview](https://learn.microsoft.com/en-us/azure/sap/sap-on-azure-overview)
- [SAP on Microsoft Cloud](https://azure.microsoft.com/en-us/solutions/sap/azure-solutions)

This PRD translates Microsoft's SAP-on-Azure workload operating model into an Odoo-native equivalent.
