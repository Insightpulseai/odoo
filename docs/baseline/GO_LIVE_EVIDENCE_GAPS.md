# Go-Live Evidence Gaps

> Every subsystem where evidence is missing, contradictory, or insufficient.
> Generated 2026-04-16 from live infrastructure audit + repo analysis.

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

## GAP-03: odoo_dev Database Does Not Exist (P0)

**Claim**: `odoo_dev` is the development database (referenced in CLAUDE.md, runtime_contract.yaml, environment-contract.yaml).
**Reality**: `odoo_dev` does not exist on `pg-ipai-odoo`. Connection attempt returns `FATAL: database "odoo_dev" does not exist`.
**Evidence**: `psycopg2.connect(dbname='odoo_dev')` raises OperationalError; `pg_database` listing confirms only: azure_maintenance, azure_sys, odoo, odoo_staging, postgres.
**Impact**: Development environment is broken or was never set up on Azure PG.
**Contradiction**: `ssot/odoo/environment-contract.yaml` lines 107-108 say `assume_azure_has_odoo_dev` is forbidden, correctly noting it is local-only. But `runtime_contract.yaml` line 132 configures `odoo_dev` for local_dev. The contradiction is between docs that imply it should exist on Azure and the environment contract that says it should not.

---

## GAP-04: Key Vault Secret Population Unverified (P0)

**Claim**: Runtime secrets managed via Key Vault + managed identity.
**Reality**: Two Key Vaults exist (`kv-ipai-dev` on Sub1, `kv-ipai-dev-sea` on Sponsored). Whether they contain the required secrets is unverified in this audit.
**Evidence**: `az keyvault list` confirms both vaults exist. Secret enumeration requires vault read permission not exercised in this session.
**Required secrets per SSOT**: `azure-openai-api-key`, `odoo-db-password`, `zoho-smtp-user`, `zoho-smtp-password`, `odoo-entra-oauth-client-secret`.
**Environment contract note**: Plaintext PG password in ACA env vars is a known regression (line 97-98 of `environment-contract.yaml`).

---

## GAP-05: Cross-Subscription Architecture Unverified (P1)

**Claim**: Two Azure subscriptions work together seamlessly.
**Reality**: Resources are split:
- Sponsored sub: PG, ACR, Databricks, primary Odoo ACA, Purview, Service Bus, Backup Vault
- Sub1: AFD, KV, AI Services, 15 ACA apps, Redis, Function App, most support services
**Missing proof**: Private endpoint connectivity between subs, DNS resolution for internal services, managed identity cross-sub RBAC assignments.
**Impact**: The primary Odoo ACA (Sponsored) may not be able to reach KV, AFD, or AI services (Sub1) via private networking.

---

## GAP-06: Entra Tenant ID Conflict (P1)

**Claim**: Single Entra tenant for identity.
**Reality**: Two different tenant IDs in SSOT files:
- `ssot/odoo/runtime_contract.yaml` line 166: `402de71a-87ec-4302-a609-fb76098d1da7`
- `ssot/identity/odoo-azure-oauth.yaml` line 17: `9ba5e867-1fb2-41cb-8e94-7d7a2b8fe4a9`
**Impact**: OAuth configuration cannot be correct if the tenant ID is wrong. One of these is the actual tenant.
**Evidence**: `az account list` shows tenant `402de71a` for both subscriptions, suggesting that is correct and `9ba5e867` in the OAuth SSOT is wrong.

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
**Evidence**: `az containerapp list` shows both apps. DNS points to the Sponsored one. Sub1 one has worker + cron companions suggesting it was the original intended dev env.
**Impact**: Confusing for operations; risk of deploying to wrong app.

---

## GAP-09: Stale Runtime Contract References (P1)

**Claim**: `ssot/odoo/runtime_contract.yaml` is authoritative.
**Reality**: Line 61 references ACA environment `salmontree-b7d27e19` which does not match current environments:
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

---

## GAP-12: Zoho SMTP Not Runtime-Verified (P1)

**Claim**: Zoho SMTP is configured for outbound email.
**Reality**: `ssot/infrastructure/dns_mail_authority.yaml` and `ssot/integrations/zoho_mail.yaml` define the integration. MX/SPF/DKIM/DMARC records are specified.
**Missing proof**: Odoo `ir.mail_server` record exists and points to Zoho, a test email has been sent and received, SMTP credentials are in Key Vault and accessible at runtime.

---

## GAP-13: Power BI / Fabric Trial Expiration (P2)

**Claim**: Power BI is the primary BI surface; Fabric provides mirroring.
**Reality**: Both appear to be on trial licenses expiring around 2026-05-20.
**Missing proof**: License status, whether paid licenses have been procured, semantic models published.
**Impact**: BI and data mirroring will stop working when trials expire.

---

## GAP-14: Sponsored Sub Quota Block for AI Models (P2)

**Claim**: R2 baseline needs gpt-4.1 family + embeddings + multimodal.
**Reality**: 4 models deployed. Attempts to deploy additional models hit error `715-123420` (sponsored subscription quota limitation).
**Missing proof**: Support ticket filed and resolved, or workaround documented.
**Documented in**: `ssot/governance/foundry-model-routing.yaml` lines 49-60.

---

## GAP-15: 55 Custom Modules Fail Doctrine Checklist (P2)

**Claim**: `ipai_*` modules follow OCA-style doctrine with MODULE_INTROSPECTION.md + TECHNICAL_GUIDE.md.
**Reality**: Prior audit found 0/55 modules pass the full doctrine checklist.
**Impact**: Even when deployment pipeline works, module quality is unproven. Many may duplicate OCA functionality.

---

## GAP-16: Agent Skills Are Knowledge Only (P2)

**Claim**: 180+ agent skills provide specialist capabilities.
**Reality**: Skill directories contain knowledge definitions (SKILL.md files, prompts, system messages). No runtime agent framework is executing them.
**Missing proof**: A live agent invocation that routes to a skill, executes tools, and returns a result.

---

## GAP-17: Screenshots vs Executable Proof (General)

**Claim**: Evidence exists for various deployments.
**Reality**: `docs/evidence/` contains evidence packs from prior sessions, but these are snapshot-in-time artifacts. They do not constitute reproducible proof of current state.
**Impact**: Evidence ages quickly. A deployment that was live on 2026-04-10 may not be live today.
**Recommendation**: All evidence should include a reproducible verification command, not just a screenshot or paste.

---

## GAP-18: Duplicate Resources Across Subscriptions (P2)

**Observation**: Several resources appear duplicated across Sponsored and Sub1:
- `ipai-website-dev` ACA on both subs
- `ipai-w9studio-dev` ACA on both subs
- AI Search `srch-ipai-dev` (Sub1) and `srch-ipai-dev-sea` (Sponsored)
- Key Vault `kv-ipai-dev` (Sub1) and `kv-ipai-dev-sea` (Sponsored)
- `id-ipai-dev` managed identity on both subs
**Impact**: Unclear which is authoritative. Cost waste. Configuration drift risk.

---

*Generated 2026-04-16. Each gap includes the specific evidence (or lack thereof) that surfaces the issue.*
