# Go-Live Checklist: InsightPulse AI Platform

Use this as the **release gate** for the Azure-native SaaS + data platform. This checklist ensures adherence to the canonical architecture and mandatory platform controls.

**Last reviewed**: 2026-03-27
**Current verdict**: NO-GO (3 remaining blockers: B-1 DOCUMENTED, B-2 IN PROGRESS, B-3 DOCUMENTED; B-4 CLOSED, B-5 CLOSED)

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

## Blocker Burn-Down (2026-03-27)

| # | Blocker | Owner | Evidence required | Gate status |
|---|---------|-------|-------------------|-------------|
| B-1 | **Entra ID not operational as IdP** — local password is only working auth | Identity / Platform | Production login round-trip via Entra SSO succeeds. Enterprise apps assigned. Conditional access baseline applied. `ipai_auth_oidc` module installed. | **DOCUMENTED** — activation runbook at `docs/runbooks/entra-idp-activation.md`, execution pending |
| B-2 | **12 credentials exposed in `archive/`** — Odoo admin password (5 locations), PG password, Supabase SERVICE_ROLE key, ANON key (x2), PG pooler string, 3 user passwords | Security / Platform | All 12 credentials rotated. `archive/` files sanitized or deleted. Old credentials confirmed non-functional. Pre-commit hook scanning added. | **IN PROGRESS** — repo sanitized (see `docs/evidence/20260327-blockers/B2-credential-sanitization.md`), runtime rotation still needed |
| B-3 | **No break-glass accounts** — tenant recovery path absent | Identity / Platform | Two cloud-only Global Admin accounts created. Credentials vaulted. MFA exclusion policy documented. Recovery procedure tested. | **DOCUMENTED** — procedure at `docs/runbooks/break-glass-accounts.md`, execution pending |
| B-4 | **No incident / rollback plans** — operational recovery not production-ready | Platform / Ops | Incident severity model exists. Rollback path for identity, data, and deployment cutover documented. Owner and escalation chain defined. Stop conditions explicit. | **CLOSED** — runbooks at `docs/runbooks/incident-response.md` |
| B-5 | **Fabric capacity not active** | Data / Analytics | *Conditional*: blocker **only if** a production workload in this release depends on Fabric capacity. Otherwise downgrade to post-go-live enablement. Currently blocks: Fabric mirroring completion, Power BI Premium/PPU, XMLA endpoint. | **CLOSED** — explicitly deferred to post-go-live (see `docs/runbooks/fabric-capacity-decision.md`) |

### Burn-down sequence

```text
B-2 (credentials)  ──→  can be done independently, immediate
B-3 (break-glass)  ──→  prerequisite for B-1
B-1 (Entra IdP)    ──→  depends on B-3, largest effort
B-4 (runbooks)     ──→  can be done in parallel with B-1
B-5 (Fabric)       ──→  scope decision first, then provision or defer
```

### Exit criteria per blocker

**B-1 done when**: Production login path is Entra-backed. Target enterprise apps assigned. User/group access model validated. SSO round-trip works. Conditional access / MFA baseline applied.

**B-2 done when**: All 12 credentials rotated. `archive/` no longer contains live secrets. Repo and runtime references updated. Validation confirms old credentials no longer work.

**B-3 done when**: Two cloud-only Global Admin accounts exist. Credentials vaulted. MFA exclusion policy intentionally designed. Recovery procedure documented and tested.

**B-4 done when**: Incident severity model exists. Rollback path for cutover documented. Owner / escalation chain defined. Validation steps and stop conditions explicit.

**B-5 done when**: Either capacity provisioned and validated for in-scope workloads, **or** the checklist explicitly marks Fabric as out of release scope.

### Release posture (updated 2026-03-27)

> **NO-GO (reduced):** B-4 (runbooks) and B-5 (Fabric) are closed. B-2 (credentials) is in progress -- repo sanitized but runtime rotation pending. B-1 (Entra IdP) and B-3 (break-glass) are documented with executable runbooks but require Entra admin execution.

**Remaining blockers before go-live**: Execute B-3 (create break-glass accounts), then B-1 (activate Entra OIDC), then complete B-2 (runtime credential rotation). Treat the 7 runtime verifications (`RUNTIME_VERIFICATION_PLAN.md`) as the final evidence gate after blocker closure.

---

*Last Updated: 2026-03-27*
