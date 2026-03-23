# Go-Live Checklist: InsightPulse AI Platform

Use this as the **release gate** for the Azure-first SaaS + data platform. This checklist ensures adherence to the canonical architecture and mandatory platform controls.

## 1. Identity and Secrets — **Blockers**

* [ ] **Microsoft Entra ID is the active identity authority** for humans, service principals, and managed identities.
* [ ] **Azure Key Vault is the only production secret/key/certificate authority**.
* [ ] **Azure RBAC** is the default Key Vault authorization model.
* [ ] Strong auth is enabled for admins: **Microsoft Authenticator**, **passkeys/FIDO2**, and **Temporary Access Pass**.
* [ ] **Two cloud-only break-glass Global Admin accounts** exist and are documented.
* [ ] SMS and voice are disabled unless there is a documented exception.

## 2. SaaS Platform Foundations — **Blockers**

* [ ] The platform is mapped to the **Azure SaaS Workload Documentation** design areas:
  * Resource organization
  * Identity and access management
  * Compute
  * Networking
  * Data
  * Billing/cost management
  * Governance
  * DevOps practices
  * Incident management
* [ ] Each area has an owner, an SSOT artifact, and a runtime evidence source.
* [ ] The SaaS assessment is part of the go-live review pack.

## 3. Databricks + Unity Catalog — **Blockers**

* [ ] **Azure Databricks is the engineering core** for ingestion, processing, and serving.
* [ ] **Unity Catalog is mandatory** for centralized access control, lineage, auditing, and discovery.
* [ ] The lakehouse uses the **mandatory medallion contract**:
  * **Bronze** = raw
  * **Silver** = conformed/normalized
  * **Gold** = curated business analytics
* [ ] Production data assets are in Unity Catalog, not Hive metastore.
* [ ] SQL serving is through **Databricks SQL warehouses**, not ad hoc notebook-only access.

## 4. Fabric Mirroring — **Blockers**

* [ ] For **Azure Database for PostgreSQL / Odoo analytics**, the mirrored landing path is **Fabric database mirroring**.
* [ ] The mirrored scope is explicitly approved and not “all databases by default.”
* [ ] Fabric is treated as a **consumption complement**, not a replacement for Databricks engineering.

## 5. Power BI — **Blockers**

* [ ] **Power BI is the primary business-consumption layer**.
* [ ] Data published from Databricks to Power BI is in **Unity Catalog** and uses **Unity Catalog-enabled compute**.
* [ ] **Power BI Premium, PPU, or Fabric capacity** is active.
* [ ] **XMLA endpoint is set to Read Write** in the Power BI capacity.
* [ ] The serving contract is defined: Databricks SQL warehouse and/or Direct Lake via Fabric.

## 6. Odoo / Workflow Integration — **Blockers**

* [ ] **n8n is the required orchestration plane** for Odoo workflows, chat ingress, notifications, approvals, and app-to-app automation.
* [ ] n8n is **not** being used as the primary analytics CDC backbone.
* [ ] n8n is **self-hosted** for production use cases.

## 7. Supabase Lane — **Blockers**

* [ ] Self-hosted Supabase CDC is routed through **`supabase/etl`**, not n8n.
* [ ] Destination is explicitly chosen: **BigQuery** (CRUD) or **Apache Iceberg** (Operation Logs).
* [ ] PostgreSQL version is supported by `supabase/etl` (14–18, 15+ preferred).

## 8. Repo & CI/CD Contracts — **Blockers**

* [ ] The **`data-intelligence` repo/directory** is the code authority for Databricks assets (bundles, notebooks, SQL, pipelines).
* [ ] Deployment validation exists for Databricks bundles and medallion contracts.
* [ ] No stale nested copies remain as active authorities.

## 9. Observability & Operations — **Blockers**

* [ ] Azure Monitor / Application Insights is wired for core platform surfaces.
* [ ] Cost governance is active for Azure workloads.
* [ ] Incident ownership and escalation are defined.
* [ ] Rollback plans exist for data platform, identity/secrets, and orchestration deploys.

## 10. Evidence Pack — **Blockers**

* [ ] **Identity Evidence**: Admin/break-glass inventory, auth methods, Vault RBAC.
* [ ] **Data Evidence**: Unity Catalog schemas/lineage, Databricks serving paths, Fabric mirrored status.
* [ ] **Integration Evidence**: n8n runtime ownership, workflow registry, credential authority.
* [ ] **Delivery Evidence**: CI validation logs, deployment proof, smoke checks.

---

## Go / No-Go Rule

### **No-Go** if:
* Entra + Key Vault + RBAC are not the real control plane.
* Databricks + Unity Catalog are not the real engineering/governance plane.
* Power BI serving prerequisites (UC, capacity, XMLA) are not met.
* n8n role is unclear or overlaps with CDC.

### **Ready** only if:
* All blockers are checked.
* Evidence pack is complete.
* Rollback and support ownership are explicit.

## 11. Microsoft 365 Copilot Readiness — **Blockers**

* [ ] **Readiness assessment run** and results documented.
* [ ] **Identity/authz posture validated** for M365 Copilot admin surfaces.
* [ ] **Connector/data access model defined** for enterprise data exposure.
* [ ] **Pre-built vs build-your-own agent policy defined**.
* [ ] **M365 Agents SDK** correctly modeled as a channel adapter, not a runtime replacement.
* [ ] **Operator ownership defined** for M365 admin surfaces.

---
*Last Updated: 2026-03-21*
