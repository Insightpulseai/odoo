# Go-Live Checklist: InsightPulse AI Platform

Use this as the **release gate** for the Azure-native SaaS + data platform. This checklist ensures adherence to the canonical architecture and mandatory platform controls.

**Last reviewed**: 2026-03-27
**Current verdict**: NO-GO (5 blocking defects — see bottom)

---

## 1. Identity and Secrets — **Blockers**

* [ ] **Microsoft Entra ID is the active identity authority** for humans, service principals, and managed identities.
* [x] **Azure Key Vault is the only production secret/key/certificate authority** — `enableRbacAuthorization: true` in Bicep.
* [x] **Azure RBAC** is the default Key Vault authorization model — Key Vault Administrator restricted to platform-owners group.
* [ ] Strong auth is enabled for admins: **Microsoft Authenticator**, **passkeys/FIDO2**, and **Temporary Access Pass**.
* [ ] **Two cloud-only break-glass Global Admin accounts** exist and are documented.
* [ ] SMS and voice are disabled unless there is a documented exception.
* [ ] **No credentials in tracked files** — archive/ credential exposure remediated (12 items found in audit C-3).
* [x] **Entra tenant verified** — `insightpulseai.com` verified and default, tenant `402de71a`, Entra P2 licensed.
* [x] **Odoo OAuth providers registered** — Entra (`07bd9669`) and Google (`placeholder`) in `oauth_providers.xml`.
* [x] **`auth_oauth.authorization_header = 1`** set for Microsoft provider.

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

* [x] **Azure Databricks is the engineering core** for ingestion, processing, and serving — `dbw-ipai-dev` active.
* [ ] **Unity Catalog is mandatory** for centralized access control, lineage, auditing, and discovery.
* [x] The lakehouse uses the **mandatory medallion contract**: Bronze → Silver → Gold → Platinum.
* [ ] Production data assets are in Unity Catalog, not Hive metastore.
* [x] SQL serving is through **Databricks SQL warehouses** — warehouse `e7d89eabce4c330c` proven.

## 4. Fabric Mirroring — **Blockers**

* [x] For **Azure Database for PostgreSQL / Odoo analytics**, the mirrored landing path is **Fabric database mirroring** — `pg-ipai-odoo` has mirroring enabled.
* [x] The mirrored scope is explicitly approved — `odoo_staging` first rehearsal documented.
* [x] Fabric is treated as a **consumption complement**, not a replacement for Databricks engineering.
* [ ] **Fabric capacity is active** — needed to complete mirroring.

## 5. Power BI — **Blockers**

* [x] **Power BI is the primary business-consumption layer** — documented as mandatory in CLAUDE.md rule 12.
* [ ] Data published from Databricks to Power BI uses **Unity Catalog-enabled compute**.
* [ ] **Power BI Premium, PPU, or Fabric capacity** is active.
* [ ] **XMLA endpoint is set to Read Write** in the Power BI capacity.
* [ ] The serving contract is defined: Databricks SQL warehouse and/or Direct Lake via Fabric.

## 6. Odoo / Azure-Native Integration — **Blockers**

* [x] **Odoo operational data** writes to Azure Database for PostgreSQL (`odoo`).
* [x] **Fabric mirroring** is the canonical analytics ingress for Odoo data.
* [x] **Azure DevOps Pipelines** is the canonical CI/CD surface — GitHub Actions deprecated 2026-03-21.
* [x] **Zoho SMTP** is the canonical outbound mail path — `smtp.zoho.com:587`, credentials in Key Vault.
* [x] **Integration adoption rule** documented: native Odoo → OCA → ipai_* bridge.

> **Note**: n8n was decommissioned 2026-03-25 (VM deleted, DNS removed). Supabase was deprecated 2026-03-26 (VM deleted). Neither is a go-live dependency.

## 7. Mailbox and Experience Lanes — **Non-blocking**

* [x] **Gmail add-on** deployed as pilot — `InsightPulseAI for Gmail` v1.4 @6.
* [x] **Spec bundle** exists — `spec/gmail-inbox-addon/` with constitution, PRD, plan, 55+ tasks.
* [ ] **Zoho Mail extension** planned as second host lane — not blocking for go-live.
* [ ] **Wix Headless** planned as experience lane — not blocking for go-live.

## 8. Repo & CI/CD Contracts — **Blockers**

* [x] The **`data-intelligence` repo/directory** is the code authority for Databricks assets.
* [x] **Azure DevOps Pipelines** exist — `azure-infra-deploy`, `ci-validation`.
* [ ] Deployment validation exists for Databricks bundles and medallion contracts.
* [ ] No stale nested copies remain as active authorities — odoo/odoo/odoo/ nesting needs cleanup.

## 9. Observability & Operations — **Blockers**

* [ ] Azure Monitor / Application Insights is wired for core platform surfaces.
* [ ] Cost governance is active for Azure workloads.
* [ ] Incident ownership and escalation are defined.
* [ ] Rollback plans exist for data platform, identity/secrets, and deployment.

## 10. Evidence Pack — **Blockers**

* [x] **Identity Evidence**: Entra tenant verified, P2 licensed, app registrations audited, OAuth providers in repo.
* [x] **Data Evidence**: Databricks SQL warehouse proven, DLT pipeline proven, Fabric mirroring enabled.
* [x] **Integration Evidence**: Integration/auth audit complete (25/25 gaps closed), SSOT artifacts current.
* [x] **Delivery Evidence**: AzDO pipelines exist, CI workflows defined.
* [ ] **Operational Evidence**: Monitor, incident, rollback docs not yet produced.

## 11. Microsoft 365 Copilot Readiness — **Non-blocking for MVP**

* [ ] **Readiness assessment run** and results documented.
* [ ] **Identity/authz posture validated** for M365 Copilot admin surfaces.
* [ ] **Connector/data access model defined** for enterprise data exposure.
* [ ] **Pre-built vs build-your-own agent policy defined**.
* [x] **M365 Agents SDK** correctly modeled as a channel adapter, not a runtime replacement.
* [ ] **Operator ownership defined** for M365 admin surfaces.

## 12. MCP Server and Agent Governance — **Non-blocking for MVP**

* [x] **MCP server policy** documented — 6 approved servers, rest conditional.
* [x] **Enterprise MCP Server** provisioned — 36 MCP.* scopes granted to VS Code.
* [x] **Agent skills** — gws CLI pilot, Entra MCP, Odoo copilot skill contracts in repo.
* [ ] **Custom MCP client** registered for Claude Code (T-077).

---

## Go / No-Go Rule

### **No-Go** if:

* Entra + Key Vault + RBAC are not the real control plane.
* Databricks + Unity Catalog are not the real engineering/governance plane.
* Power BI serving prerequisites (UC, capacity, XMLA) are not met.
* Archive credentials not remediated.
* No incident/rollback plans.

### **Ready** only if:

* All blockers are checked.
* Evidence pack is complete.
* Rollback and support ownership are explicit.

---

## Current Blocking Defects (2026-03-27)

| # | Defect | Section | Remediation |
|---|--------|---------|-------------|
| 1 | **Entra ID not operational as IdP** — local password is only working auth | §1 | Complete `spec/entra-identity-migration/` Phase 0-1 |
| 2 | **12 credentials exposed in archive/** | §1 | Rotate and remove per audit finding C-3 |
| 3 | **No break-glass accounts** | §1 | Create 2 cloud-only Global Admin accounts |
| 4 | **No incident/rollback plans** | §9 | Write runbooks for identity, data, and deployment rollback |
| 5 | **Fabric capacity not active** | §4, §5 | Provision Fabric capacity to complete mirroring + Power BI |

---

*Last Updated: 2026-03-27*
