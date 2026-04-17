# Go-Live Evidence Gaps (v2)

> Every subsystem where evidence is missing, contradictory, or insufficient.
> Generated 2026-04-16 from live infrastructure audit + repo analysis.
> v2 additions: GAP-19 through GAP-25 (reporting, cutover, Databricks surfaces, Google Workspace boundary, source quality)

---

## GAP-01: Odoo Business Modules Not Installed (P0)

**Claim**: Odoo ERP is the transaction plane system of record for finance, CRM, project, BIR compliance.
**Reality**: Only 12 base framework modules installed. No `account`, `sale`, `purchase`, `crm`, `project`, `hr`, or any `ipai_*` module.
**Evidence**: `SELECT name FROM ir_module_module WHERE state='installed'` returns only: auth_totp, base, base_import, base_import_module, base_setup, bus, html_editor, iap, web, web_editor, web_tour, web_unsplash.
**Impact**: No ERP functionality exists. Zero business transactions can be processed.
**Sources that contradict this**: `ssot/odoo/module_install_manifest.yaml`, `ssot/apps/desired-end-state-matrix.yaml`, multiple architecture docs describe a functioning ERP.

---

## GAP-02: No Verified Deployment Pipeline (P0)

**Claim**: Azure Pipelines is the sole CI/CD authority (15 pipeline definitions in repo).
**Reality**: No evidence that any pipeline has successfully built an Odoo container image with custom modules, pushed to ACR, and deployed to the production ACA app.
**Evidence**: Pipeline files exist at `azure-pipelines/`. Run history was not collected (would require ADO API access). No deployment logs, no successful run evidence in `docs/evidence/`.
**Impact**: Cannot ship code changes to production.
**Required proof**: At least one pipeline run showing: image build success, ACR push, ACA revision update, health check pass.

---

## GAP-03: Finance/Accounting Cutover Impossible (P0) [EXPANDED in v2]

**Claim**: Odoo will handle GL, AP/AR, invoicing, BIR tax compliance, multi-currency.
**Reality**: The `account` module is not installed. ALL finance cutover checks are N/A:

| Cutover Check | Status |
|---|---|
| Opening balances loaded | N/A -- no account module |
| AR clearing complete | N/A |
| AP clearing complete | N/A |
| Trial balance reconciled | N/A |
| Bank clearing accounts | N/A |
| Multi-currency configured | N/A |
| Chart of accounts validated | N/A |
| Tax configuration (BIR) | N/A -- 7+ BIR modules in repo, none installed |
| Payment providers configured | N/A -- PayPal/Xendit available in CE18 catalog, unconfigured |
| Fiscal year defined | N/A |

**Impact**: No financial transaction processing is possible. The R2 milestone (first customer-usable Finance slice) cannot be met without installing accounting modules first.
**Prerequisite**: Install `account` module, then load chart of accounts, configure fiscal year, before any cutover check can be assessed.

---

## GAP-04: Key Vault Secret Population Unverified (P0)

**Claim**: Runtime secrets managed via Key Vault + managed identity.
**Reality**: Two Key Vaults exist (`kv-ipai-dev` on Sub1, `kv-ipai-dev-sea` on Sponsored). Whether they contain the required secrets is unverified in this audit.
**Evidence**: `az keyvault list` confirms both vaults exist. Secret enumeration requires vault read permission not exercised in this session.
**Required secrets per SSOT**: `azure-openai-api-key`, `odoo-db-password`, `zoho-smtp-user`, `zoho-smtp-password`, `odoo-entra-oauth-client-secret`.
**Known regression**: Plaintext PG password in ACA env vars (line 97-98 of `environment-contract.yaml`).
**Additional risk**: A password was exposed during this session and requires rotation.

---

## GAP-05: Cross-Subscription Architecture Unverified (P1)

**Claim**: Two Azure subscriptions work together seamlessly.
**Reality**: Resources are split:
- Sponsored sub: PG, ACR, Databricks, primary Odoo ACA (blackriver), Purview, Service Bus, Backup Vault
- Sub1: AFD, KV, AI Services, 15 ACA apps (blackstone), Redis, Function App, most support services
**Missing proof**: Private endpoint connectivity between subs, DNS resolution for internal services, managed identity cross-sub RBAC assignments.
**Impact**: The primary Odoo ACA (Sponsored) may not be able to reach KV, AFD, or AI services (Sub1) via private networking.

---

## GAP-06: Entra Tenant ID Conflict (P1)

**Claim**: Single Entra tenant for identity.
**Reality**: Two different tenant IDs in SSOT files:
- `ssot/odoo/runtime_contract.yaml`: `402de71a-87ec-4302-a609-fb76098d1da7`
- `ssot/identity/odoo-azure-oauth.yaml`: `9ba5e867-1fb2-41cb-8e94-7d7a2b8fe4a9`
**Resolution**: `az account list` confirms `402de71a` for both subscriptions. The OAuth SSOT value `9ba5e867` is WRONG and must be corrected.
**Impact**: OAuth configuration will fail if the wrong tenant ID is used.

---

## GAP-07: Staging Environment Not Functional (P1)

**Claim**: `odoo_staging` environment exists per environment contract.
**Reality**:
- Database `odoo_staging` exists but has 0 tables
- No staging ACA app deployed
- DNS `erp-staging.insightpulseai.com` marked as planned (not created)
- No staging config files exist (marked TODO in environment-contract.yaml)
**Impact**: No pre-production testing environment.

---

## GAP-08: ACA Environment Naming Confusion (P1)

**Claim**: Clear environment separation (dev/staging/prod).
**Reality**: Production URL `erp.insightpulseai.com` is served by `ca-ipai-odoo-web-dev` (a `-dev` suffixed app) on Sponsored sub. Sub1 has `ipai-odoo-dev-web` which appears to be an older parallel.
**Evidence**: `az containerapp list` shows both apps. DNS points to the Sponsored one (blackriver). Sub1 one (blackstone) has worker + cron companions suggesting it was the original intended dev env.
**Impact**: Confusing for operations; risk of deploying to wrong app.

---

## GAP-09: Stale Runtime Contract References (P1)

**Claim**: `ssot/odoo/runtime_contract.yaml` is authoritative.
**Reality**: References ACA environment `salmontree-b7d27e19` which does not match current environments:
- Sponsored: `blackriver-f68f8a9b` (for ca-ipai-odoo-web-dev), `whitedesert-54fce6ca` (for other apps)
- Sub1: `blackstone-0df78186` (for ipai-odoo-dev-web)
**Impact**: Automation relying on this SSOT file will target wrong environment.

---

## GAP-10: No Backup/DR Verification (P1)

**Claim**: Backup infrastructure provisioned.
**Reality**: `bvault-ipai-dev-sea` (Backup Vault, Sponsored) and `rsv-ipai-dev` (Recovery Services Vault, Sub1) exist as Azure resources.
**Missing proof**: Backup policies configured, successful backup runs, tested restore procedure, RPO/RTO documented.
**Impact**: Data loss risk if PG or filestore fails.

---

## GAP-11: Monitoring Not Operationally Verified (P1)

**Claim**: Observability stack provisioned.
**Reality**: 5 Log Analytics workspaces, 4 App Insights instances, 3 alert rules exist.
**Missing proof**: Alerts are correctly routed and have fired on real events, dashboards exist and are reviewed, log retention policies configured, someone is on-call.
**Alert rules** (Sub1): `alert-ipai-content-safety-blocks`, `alert-ipai-agent-latency-p95`, `alert-ipai-agent-error-rate`.
**Note**: The 3-day Odoo outage (04-13 to 04-16, 18,526+ probe failures) was NOT caught by alerts -- discovered manually.

---

## GAP-12: Zoho SMTP Not Runtime-Verified (P1)

**Claim**: Zoho SMTP is configured for outbound email.
**Reality**: `ssot/infrastructure/dns_mail_authority.yaml` and Entra enterprise apps (Zoho + Zoho Mail Admin) confirm the integration is defined.
**Missing proof**: Odoo `ir.mail_server` record exists and points to Zoho, a test email has been sent and received, SMTP credentials are in Key Vault and accessible at runtime.

---

## GAP-13: Power BI / Fabric Trial Expiration (P2)

**Claim**: Power BI is the primary BI surface; Fabric provides mirroring.
**Reality**: Both appear to be on trial licenses expiring around 2026-05-20 (~34 days).
**Missing proof**: License status, whether paid licenses have been procured, semantic models published.
**Impact**: BI and data mirroring will stop working when trials expire.

---

## GAP-14: Sponsored Sub Quota Block for AI Models (P2)

**Claim**: R2 baseline needs gpt-4.1 family + embeddings + multimodal.
**Reality**: 4 models deployed. Attempts to deploy additional models hit error `715-123420` (sponsored subscription quota limitation).
**Missing proof**: Support ticket filed and resolved, or workaround documented.
**Documented in**: `ssot/governance/foundry-model-routing.yaml`.

---

## GAP-15: 55 Custom Modules Fail Doctrine Checklist (P2)

**Claim**: `ipai_*` modules follow OCA-style doctrine with MODULE_INTROSPECTION.md + TECHNICAL_GUIDE.md.
**Reality**: Prior audit found 0/55 modules pass the full doctrine checklist.
**Impact**: Even when deployment pipeline works, module quality is unproven. Many may duplicate OCA functionality.

---

## GAP-16: Agent Skills Are Knowledge Only (P2)

**Claim**: 180+ agent skills provide specialist capabilities.
**Reality**: Skill directories contain knowledge definitions (SKILL.md files, prompts, system messages). No runtime agent framework is executing them. agents/ repo audit grade: D (44/100).
**Missing proof**: A live agent invocation that routes to a skill, executes tools, and returns a result.
**Best-developed agent**: Scrum Master (65/100) -- spec complete, code partial, control missing.

---

## GAP-17: Screenshots vs Executable Proof (General)

**Claim**: Evidence exists for various deployments.
**Reality**: `docs/evidence/` contains evidence packs from prior sessions, but these are snapshot-in-time artifacts. They do not constitute reproducible proof of current state.
**Impact**: Evidence ages quickly. A deployment that was live on 2026-04-10 may not be live today (as proven by the 3-day outage discovered this session).
**Recommendation**: All evidence should include a reproducible verification command, not just a screenshot or paste.

---

## GAP-18: Duplicate Resources Across Subscriptions (P2)

**Observation**: Several resources appear duplicated across Sponsored and Sub1:
- `ipai-website-dev` ACA on both subs
- `ipai-w9studio-dev` ACA on both subs
- AI Search `srch-ipai-dev` (Sub1) and `srch-ipai-dev-sea` (Sponsored)
- Key Vault `kv-ipai-dev` (Sub1) and `kv-ipai-dev-sea` (Sponsored)
- Managed identities on both subs
**Impact**: Unclear which is authoritative. Cost waste. Configuration drift risk.

---

## GAP-19: Azure DevOps Reporting Plane Entirely Unverified (P2) [NEW in v2]

**Claim**: ADO is the portfolio/planning system with 23 epics, 120+ issues, 250+ tasks, 5 iterations.
**Reality**: This data comes from agent memory only. No ADO API queries, dashboards, Analytics views, or OData connections were verified this audit.
**Missing proof**:
- At least one ADO dashboard with refreshable data
- Pipeline analytics (success rate, deployment frequency)
- OData connection to Power BI
- Analytics view configuration
**Impact**: Cannot use ADO as evidence source for project health or go-live readiness until reporting surfaces are verified.
**Source quality**: Agent memory is LOW trust. Official docs and API queries are required for evidence.

---

## GAP-20: No Refreshable Reporting Evidence (P2) [NEW in v2]

**Claim**: Various dashboards and reports exist or will exist.
**Reality**: No refreshable report with live data has been demonstrated for any subsystem:
- No Power BI reports
- No ADO dashboards
- No Databricks dashboards
- No operational monitoring dashboards
**Evidence requirement**: A report qualifies as evidence only if it shows: data recency timestamp, query source, and at least one meaningful metric. Screenshots alone are insufficient.

---

## GAP-21: Databricks Surface Distinctions Not Assessed (P2) [NEW in v2]

**Claim**: Databricks workspace is provisioned and UC-enabled.
**Reality**: "Workspace provisioned" covers only one of four distinct Databricks surfaces:
1. **Workspace** (notebook/SQL development) -- provisioned (verified)
2. **Admin console** (governance, cluster policies, access control) -- NOT assessed
3. **Developer tooling** (VS Code extension, CLI, SDK) -- contract defined, not verified
4. **Apps runtime** (Databricks Apps hosting) -- NOT assessed
**Impact**: Workspace provisioning does not imply developer tooling readiness or admin governance configuration.
**Contracts**: `infra/ssot/databricks/developer-tooling.contract.yaml`, `infra/ssot/databricks/vscode-extension.contract.yaml`

---

## GAP-22: Google Workspace / Entra / Odoo Boundary Model Untested (P2) [NEW in v2]

**Claim**: W9 Studio uses Google Workspace (w9studio.net) for collaboration; Entra is the identity authority; Odoo holds the tenant boundary via res.company.
**Reality**: This three-system boundary model is defined in SSOT files but not tested:
- `ssot/tenants/tenant-registry.yaml`: W9 Studio = company 2, Google Workspace = collaboration only
- `ssot/identity/identity-boundary-policy.yaml`: enterprise apps = identity surfaces, NOT tenant boundaries
**Missing proof**:
- W9 Studio company record exists in Odoo
- Google Workspace users can authenticate to Odoo via Entra (not via Google directly)
- Tenant data isolation is enforced by company-level record rules
**Note**: w9studio.net is NOT insightpulseai.com. It is a collaboration domain, not a tenant domain.

---

## GAP-23: Enterprise Apps vs App Registrations Not Reconciled (P2) [NEW in v2]

**Claim**: 11 enterprise apps and 21 app registrations are properly managed.
**Reality**: Enterprise apps are documented in `ssot/identity/enterprise-apps.runtime-state.yaml` (11 apps observed). App registrations (21 total) are NOT enumerated in this audit.
**Missing proof**:
- Full app registration inventory with owner/purpose
- Mapping between enterprise apps and app registrations
- Identification of stale/unused registrations (ipai-n8n-entra flagged for deletion)
- Certificate/secret expiry review (GitHub SAML cert expires 2028-03-30 -- only one checked)
**Impact**: Identity sprawl risk. Stale registrations are a security concern.

---

## GAP-24: Review Gate Artifacts Missing (P1) [NEW in v2]

**Claim**: `ssot/assurance/review-gates.yaml` defines 5 implementation phases with mandatory gate reviews.
**Reality**: Phase gate assessment:

| Phase | Gate | Required Artifacts | Artifacts Present |
|---|---|---|---|
| Discover | Discover checkpoint | 5 artifacts | Partial (scope/architecture exist; gap-fit incomplete) |
| Initiate | Solution blueprint review | 7 artifacts | Partial (architecture exists; env topology done; integration design incomplete) |
| Implement | Implementation progress review | 5 artifacts | None (no sprint demos, no test coverage) |
| Prepare | Go-live readiness review | 10 artifacts | None (no UAT, no cutover plan, no mock go-live, no rollback plan) |
| Operate | Hypercare exit review | 5 artifacts | None |

**Impact**: The Prepare phase requires 10 artifacts including UAT sign-off, cutover plan rehearsal, go/no-go criteria, and rollback plan testing. None exist.

---

## GAP-25: 3-Day Outage Not Caught by Monitoring (P1) [NEW in v2]

**Claim**: Observability stack with alerts is provisioned.
**Reality**: Odoo was down from 2026-04-13 to 2026-04-16 (3 full days) with 18,526+ startup probe failures. The outage was discovered manually during this session, not by any alert.
**Root causes**: Wrong DB_HOST (pg-ipai-odoo-dev vs pg-ipai-odoo), env var collision (PORT/USER), empty database, ephemeral filestore.
**Impact**: The existing alert rules (content safety, latency, error rate on Sub1) are agent-focused, not infrastructure-focused. No ACA health alert, PG connectivity alert, or startup probe failure alert exists for the production Odoo app.
**Recommendation**: At minimum, add ACA startup probe failure alerts and PG connectivity alerts for the Sponsored sub.

---

*Generated 2026-04-16 v2. Each gap includes the specific evidence (or lack thereof) that surfaces the issue.*
