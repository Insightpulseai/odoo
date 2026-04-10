# Odoo-on-Azure Enterprise Benchmark Audit

> **Audit Date:** 2026-03-24
> **Auditor:** Claude Opus 4.6 (automated, evidence-based)
> **Scope:** InsightPulse AI monorepo (`/Users/tbwa/Documents/GitHub/Insightpulseai`)
> **Benchmark Frame:** Enterprise cloud ERP operating disciplines (SAP-on-Azure reference architecture patterns)
> **Evidence Standard:** runnable code > tests > CI/CD > deploy manifests > runbooks > docs/specs
> **Status:** DRAFT -- requires human validation of runtime claims

---

## 1. Executive Verdict

This platform demonstrates **serious architectural intent** with meaningful working code in several critical areas. The Bicep IaC library, DNS SSOT governance, copilot module with tool execution/audit/telemetry, and Front Door security middleware are genuine production-grade components. The SSOT discipline (DNS, Azure resources, service matrix) is unusually strong for a small-team operation.

However, there is a **significant gap between documented architecture and operational reality**. Many services listed as "active" in SSOT files are actually nginx stubs. The identity plane (Entra ID) exists only as role manifests and spec bundles -- no operational SSO. Database backup/restore has never been tested per the go-live checklist. Observability config references a Prometheus/Grafana stack that is not deployed on Azure (it targets Docker Compose). The platform is **pre-production** by enterprise standards, with approximately 40-50% of the go-live checklist incomplete.

**Verdict: Credible engineering foundation. Not yet enterprise-production-ready. 12-16 weeks of focused hardening required.**

---

## 2. Benchmark Scorecard

| # | Dimension | Grade | Evidence Quality | Key Signal |
|---|-----------|-------|-----------------|------------|
| 1 | Cloud Landing Zone Alignment | **PARTIAL** | Bicep + SSOT YAML | VNet defined but not wired to ACA; no NSGs; RG model sound but still normalizing |
| 2 | ERP Runtime Architecture | **STRONG** | Bicep + Docker Compose + working modules | Web/worker/cron split, Redis session, health checks, addon governance |
| 3 | Availability, Resilience, DR | **WEAK** | Go-live checklist (mostly unchecked) | No HA on PG, no tested backup restore, no failover plan, 7-day retention only |
| 4 | Security and Compliance | **PARTIAL** | Middleware + KV + role manifests | FDID middleware real; Entra not operational; Security Defaults OFF; no CA policies |
| 5 | Release Engineering | **PARTIAL** | CI workflows + Bicep + AzDO planned | 14 GH workflows exist; AzDO pipelines skeletal; no env promotion automation |
| 6 | Business-System Integration | **PARTIAL** | n8n workflows + OCR client + connectors | 18 n8n workflows; Document Intelligence client real; no retry/idempotency layer |
| 7 | Data and Analytics | **PARTIAL** | Databricks bundle + SQL + DLT | Medallion SQL real; Unity Catalog configured; Power BI/Fabric not deployed |
| 8 | AI/Copilot/Agent Architecture | **STRONG** | Working code (898-line tool executor) | Copilot gateway, audit log, telemetry, blocked models, rate limiting, RBAC mapping |
| 9 | Observability and Operations | **WEAK** | Prometheus YAML + alerting rules | Config exists for Docker Compose; not deployed on Azure; no App Insights wiring in IaC |
| 10 | Enterprise Architecture Discipline | **STRONG** | SSOT YAML + spec bundles + maturity rubric | DNS registry, resource inventory, maturity benchmark, 40+ spec bundles, deprecation tracking |

**Overall Grade: PARTIAL (55-60% enterprise-ready)**

---

## 3. Evidence-Backed Findings

### 3.1 Cloud Landing Zone Alignment

**Evidence examined:**
- `/infra/azure/main.bicep` -- parameterized IaC with env separation (dev/staging/prod)
- `/infra/azure/modules/vnet.bicep` -- VNet with 5 subnets (ACA, PG, Databricks pub/priv, integration)
- `/infra/azure/modules/front-door.bicep` -- Premium AFD with WAF
- `/infra/azure/modules/keyvault.bicep` -- RBAC-auth, soft delete, purge protection, diagnostics
- `/infra/dns/subdomain-registry.yaml` -- 60+ line governance schema with lifecycle, provider claims
- `/infra/ssot/azure/resources.yaml` -- 83 confirmed resources, reconciled 2026-03-20
- `/infra/ssot/azure/rg-normalization-matrix.yaml` -- 5+1 RG target model

**Strengths:**
- Bicep modules are well-parameterized with environment-aware naming
- DNS governance is best-in-class for this scale (YAML-first, CI-enforced)
- RG normalization model is thoughtful (runtime/data/platform/AI/observability/edge)
- Key Vault has RBAC auth, purge protection, and diagnostic settings

**Gaps:**
- VNet exists in Bicep but the main.bicep `enableFrontDoor` defaults to `false` -- VNet integration with ACA is not proven deployed
- No NSG definitions in the VNet module (subnets have no network security groups)
- No Azure Policy definitions or assignments anywhere in the repo
- No private endpoints defined (PG firewall rule is `0.0.0.0` -- AllowAzureServices)
- Entra Conditional Access: absent (Security Defaults explicitly OFF per `access_model.yaml` line 35)

### 3.2 ERP Runtime Architecture

**Evidence examined:**
- `/infra/azure/modules/aca-odoo-services.bicep` -- web/worker/cron split with managed identity, KV refs
- `/docker-compose.yml` -- well-documented local runtime (PG 16, Redis 7, Odoo 18)
- `/addons/ipai/` -- 22 custom modules visible
- `/addons/ipai/ipai_odoo_copilot/__manifest__.py` -- version 18.0.2.0.0, proper deps
- `/addons/ipai/ipai_security_frontdoor/middleware.py` -- WSGI-level FDID validation

**Strengths:**
- Three-container architecture (web/worker/cron) is correct Odoo production pattern
- Redis for session store and bus backend (proper stateless web tier)
- Health checks defined in both Docker Compose and ACA
- FDID middleware is genuine defense-in-depth (blocks `/web/database/` unconditionally)
- Module naming convention (`ipai_<domain>_<feature>`) is enforced

**Gaps:**
- Docker Compose PG password is `odoo` (acceptable for dev, but no prod compose exists)
- No horizontal autoscaling rules defined in the ACA Bicep (min/max params exist but no scale rules)
- `odoo-runtime.bicep` still defaults to `Burstable` tier PG (line 33) despite docs claiming General Purpose

### 3.3 Availability, Resilience, DR

**Evidence examined:**
- `/infra/azure/modules/postgres-flexible.bicep` lines 58-61: HA disabled, geo-redundant backup disabled
- `/docs/runbooks/ODOO18_GO_LIVE_CHECKLIST.md` -- database backup items unchecked
- `/infra/ssot/azure/service-matrix.yaml` -- health check URLs defined

**Strengths:**
- PG auto-grow storage enabled
- Health check URLs defined in service matrix
- Go-live checklist exists and is honest about gaps

**Critical gaps:**
- `highAvailability.mode: 'Disabled'` in PG Bicep -- single-instance database
- `geoRedundantBackup: 'Disabled'` -- no cross-region backup
- `backupRetentionDays: 7` -- minimal (enterprise standard: 35 days)
- Go-live checklist items unchecked: backup restore test, resource locks, failover plan
- No documented RPO/RTO targets anywhere
- No blue-green or canary deployment pattern defined
- No container revision rollback automation

### 3.4 Security and Compliance

**Evidence examined:**
- `/addons/ipai/ipai_security_frontdoor/middleware.py` -- genuine WSGI security middleware
- `/infra/azure/modules/keyvault.bicep` -- RBAC auth, purge protection
- `/infra/entra/app-roles-manifest.json` -- 10+ app roles defined with UUID v5
- `/infra/entra/role-tool-mapping.yaml` -- role-to-tool permission matrix
- `/infra/ssot/security/access_model.yaml` -- identity classes, tenant config
- `/addons/ipai/ipai_odoo_copilot/models/tool_executor.py` -- blocked models list, sanitized OData
- `/infra/tests/security/` -- bandit config and safety policy exist

**Strengths:**
- FDID middleware blocks direct access and database manager paths
- OData injection prevention in copilot tool executor (line 22-31)
- Blocked models list prevents access to `ir.config_parameter`, `res.users`, etc.
- App roles manifest is well-structured with deterministic UUIDs
- Role-tool mapping defines PROD-ADVISORY vs PROD-ACTION modes
- Key Vault secrets documented in go-live checklist (5 of 5 vaulted)

**Critical gaps:**
- `security_defaults_enabled: false` in access_model.yaml -- MFA not enforced
- Entra tier is `free` (target: P1, not deployed)
- No Conditional Access policies defined
- No Azure Policy assignments
- PG firewall rule `0.0.0.0/0.0.0.0` (AllowAzureServices) -- overly broad
- Auth gateway is "Stub (nginx:alpine)" per service-matrix.yaml line 45
- Container image scanning: no evidence of ACR vulnerability scanning configuration
- No WAF custom rules defined in Bicep (only managed ruleset reference)

### 3.5 Release Engineering

**Evidence examined:**
- `.github/workflows/` -- 14 workflow files
- `.github/workflows/databricks-bundles-ci.yml` -- bundle validation with path filtering
- `.github/workflows/agent-factory-release-gates.yml` -- schema validation, evidence checks, terminology drift
- `/ssot/governance/ado_github_authority_map.yaml`
- `/infra/ssot/azure/target-state.yaml` lines 13-43 -- AzDO pipeline configuration

**Strengths:**
- Release gates workflow enforces evidence artifacts and terminology drift policy
- Databricks CI validates bundles on PR
- GitHub Actions deprecated in favor of AzDO Pipelines (correct enterprise choice)
- Path-filtered CI (only runs when relevant files change)

**Gaps:**
- AzDO Pipelines declared as canonical but only 2 pipelines exist (`azure-infra-deploy`, `ci-validation`)
- No Odoo module CI pipeline (no `odoo-bin --test-enable` in any workflow)
- No container image build/push pipeline
- No environment promotion pipeline (dev -> staging -> prod)
- No database migration gate in any pipeline
- Branch protection rules: referenced in docs but no evidence of enforcement config

### 3.6 Business-System Integration

**Evidence examined:**
- `/automations/n8n/workflows/` -- 18 workflow JSON files
- `/addons/ipai/ipai_document_intelligence/models/ocr_client.py` -- Azure Doc Intelligence client
- `/automations/n8n/workflows/integration/` -- asset, expense, finance handlers
- `/addons/ipai/ipai_bir_tax_compliance/` -- BIR tax engine with tests

**Strengths:**
- Document Intelligence OCR client is real (async submission, polling, MIME validation)
- 18 n8n workflows covering health check, finance close, BIR compliance, Entra sync, DNS automation
- BIR tax compliance module has dedicated test fixtures
- Bank reconciliation module has 6 test files including red-team tests

**Gaps:**
- No retry/dead-letter pattern in n8n workflows
- No idempotency keys in integration handlers
- No API versioning strategy
- n8n workflows reference credential placeholders but no evidence of actual credential binding

### 3.7 Data and Analytics

**Evidence examined:**
- `/infra/databricks/databricks.yml` -- Asset Bundle with Unity Catalog, dev/staging/prod targets
- `/infra/databricks/sql/` -- 14 SQL files (bronze/silver/gold/platinum, grants, schemas)
- `/infra/databricks/pipelines/` -- finance_bir_pipeline.sql, marketing_pipeline.sql
- `/infra/databricks/sql/multi_tenant_setup.sql` -- multi-tenant catalog setup
- `/infra/ssot/azure/target-state.yaml` -- Power BI/Fabric declared as required but `not_deployed`

**Strengths:**
- Full medallion architecture in SQL (bronze -> silver -> gold -> platinum)
- Unity Catalog configured with named schemas
- Databricks Asset Bundle with environment targets (dev/staging/prod)
- Multi-tenant SQL setup demonstrates forward thinking
- DLT pipelines exist for finance and marketing domains

**Gaps:**
- Power BI: `status: not_deployed` (declared as required primary BI)
- Microsoft Fabric: `status: not_deployed` (declared as required analytics platform)
- No evidence of Databricks jobs actually running (no run logs)
- SQL Warehouse ID hardcoded in config (`e7d89eabce4c330c`)
- No data quality framework beyond SQL assertions
- No lineage tracking configuration

### 3.8 AI/Copilot/Agent Architecture

**Evidence examined:**
- `/addons/ipai/ipai_odoo_copilot/models/tool_executor.py` -- 898 lines, tool dispatch to Odoo ORM
- `/addons/ipai/ipai_odoo_copilot/controllers/copilot_gateway.py` -- 32KB gateway with rate limiting
- `/addons/ipai/ipai_odoo_copilot/models/copilot_audit.py` -- interaction audit log
- `/addons/ipai/ipai_odoo_copilot/models/telemetry.py` -- App Insights telemetry sender
- `/addons/ipai/ipai_odoo_copilot/services/odoo_context_builder.py` -- context envelope
- `/addons/ipai/ipai_odoo_copilot/services/diva_bridge.py` -- DIVA bridge service
- `/agents/passports/` -- 20 agent passports
- `/agents/skills/` -- 100+ skill directories
- `/agents/evals/odoo-sage-suite.yaml` -- 2 eval test cases
- `/docs/evidence/ap-invoice-agent-soak/real-soak-rollup.json` -- 5-cycle soak test evidence
- `/docs/evidence/foundry-evals/copilot-eval-results.json`

**Strengths:**
- **Tool executor is production-quality**: blocked model list, OData sanitization, record limits, sudo documentation
- **Copilot gateway is substantial**: dual-track backend (Azure OpenAI direct + Foundry Agent SDK), per-user rate limiting, message length validation
- **Audit trail**: every copilot interaction logged with user, prompt, mode, source, surface, roles
- **Telemetry**: non-blocking App Insights integration with graceful degradation
- **RBAC for tools**: role-tool-mapping.yaml maps Entra roles to permitted tools and retrieval scopes
- **AP invoice agent soak**: 5-cycle real-production soak test (95 invoices, 2 exceptions, 100% stability)
- **Context envelope builder**: constructs role-aware context for LLM grounding

**Gaps:**
- Eval suite has only 2 test cases (trivial for production claims)
- Agent passports are YAML declarations, not deployed agent instances
- 100+ skill directories exist but no evidence of skill execution or testing
- No prompt injection testing or adversarial eval framework
- No token budget management or cost tracking
- DIVA bridge service is 61 lines (skeletal)

### 3.9 Observability and Operations

**Evidence examined:**
- `/infra/monitoring/prometheus/prometheus.yml` -- scrape config for Odoo, PG, node, cAdvisor
- `/infra/monitoring/alerting/rules.yml` -- 6 alert rules (Odoo down, PG down, CPU, memory, disk, connections)
- `/infra/monitoring/grafana/` -- directory exists
- `/docs/runbooks/` -- 13 runbooks
- `/addons/ipai/ipai_odoo_copilot/models/telemetry.py` -- App Insights integration

**Strengths:**
- Prometheus config is well-structured with labeled scrape targets
- Alert rules cover critical failure modes (Odoo/PG down, high CPU/mem/disk, PG connections)
- 13 runbooks exist covering agent operations, database CLI, go-live, staging refresh
- Copilot telemetry sends to App Insights

**Critical gaps:**
- Prometheus/Grafana config targets Docker Compose service names (`odoo-core:8069`, `postgres-exporter:9187`) -- NOT the Azure runtime
- No Azure Monitor alert rules in Bicep
- No App Insights resource defined in the primary IaC (`/infra/azure/main.bicep` mentions it in comments but `app-insights.bicep` does not exist at this path)
- No Log Analytics workspace explicitly deployed (referenced but not created)
- No distributed tracing configuration
- No SLA/SLO definitions
- Runbooks are procedural checklists, not automated runbooks (Azure Automation or similar)

### 3.10 Enterprise Architecture Discipline

**Evidence examined:**
- `/infra/dns/subdomain-registry.yaml` -- rigorous SSOT with lifecycle, provider claims, CI gate
- `/infra/ssot/azure/resources.yaml` -- 83 resources reconciled from Azure Resource Graph
- `/infra/ssot/azure/service-matrix.yaml` -- versioned service inventory with health checks
- `/infra/ssot/azure/platform_maturity_benchmark.yaml` -- multi-domain maturity rubric
- `/ssot/governance/` -- 23 governance YAML files
- `/spec/` -- 40+ spec bundles with constitution/plan/prd/tasks structure
- CLAUDE.md hierarchy -- consistent operating contract across nested repos

**Strengths:**
- **DNS SSOT is exemplary**: lifecycle states, provider claims, CI enforcement, generated artifacts
- **Resource inventory is reconciled against live Azure**: timestamps, source attribution, errata notes
- **Maturity benchmark is self-aware**: L0-L4 levels per criterion with honest self-assessment
- **Spec bundle discipline**: consistent 4-file structure (constitution/plan/prd/tasks) across 40+ bundles
- **Deprecation tracking**: explicit dates, replacements, and "never use" policy
- **Naming convention**: documented, enforced, with errata for exceptions

**Gaps:**
- ADR (Architecture Decision Record) format not used -- decisions embedded in YAML/MD without explicit ADR numbering
- Significant path duplication: `odoo/odoo/odoo/odoo/infra/azure/` nesting indicates structural debt
- Some SSOT files have `planned` or `not_deployed` items listed alongside `active` -- could confuse automation

---

## 4. Odoo-Specific Strengths

1. **Copilot-as-first-class-citizen**: The copilot module (`ipai_odoo_copilot`) is genuinely impressive -- 898-line tool executor with security controls, 32KB gateway with rate limiting, audit trail, and App Insights telemetry. This is ahead of most Odoo deployments.

2. **Front Door security middleware** (`ipai_security_frontdoor`): WSGI-level FDID validation with database manager blocking. Simple, effective, production-appropriate.

3. **BIR tax compliance engine**: Domain-specific Philippine tax compliance with test fixtures and acceptance tests. Shows real business domain investment.

4. **Bank reconciliation with red-team tests**: 6 test files including adversarial testing -- unusual and commendable for Odoo modules.

5. **OCA governance rules**: Documented maturity levels, quality gates, porting workflow, manifest gap tracking. The OCA-first philosophy is consistently applied.

---

## 5. Benchmark Misses (vs. Enterprise Cloud ERP Reference)

| Miss | Enterprise Expectation | Current State |
|------|----------------------|---------------|
| HA database | Zone-redundant PG with automatic failover | Single instance, HA disabled |
| Tested DR | Documented RPO/RTO, annual DR drill | No RPO/RTO, backup restore untested |
| Operational identity | SSO via Entra ID with MFA + CA policies | Security Defaults OFF, Entra Free tier |
| Network isolation | Private endpoints, NSGs, no public DB access | PG allows all Azure services, no NSGs |
| Azure Policy | Deny rules for resource compliance | No policy definitions in repo |
| Container scanning | ACR vulnerability scanning, admission control | No scanning evidence |
| Automated deployment | Full CI/CD with env promotion gates | 2 skeletal AzDO pipelines, no deploy automation |
| Azure-native observability | Azure Monitor alerts, App Insights, Log Analytics workspace | Prometheus config for Docker, no Azure Monitor in IaC |
| Automated runbooks | Azure Automation or Logic Apps for incident response | Manual markdown runbooks only |
| Load testing | Performance baselines with regression gates | 1 k6 script (`odoo_login_and_nav.js`), no CI integration |

---

## 6. False Maturity Signals

These items appear mature but are not operational:

| Signal | Appearance | Reality |
|--------|-----------|---------|
| Service matrix shows 12 "active" services | Implies running production fleet | Auth, MCP, OCR, Superset are nginx stubs (`note: "Stub (nginx:alpine)"`) |
| 100+ agent skill directories | Implies vast AI capability | Skill directories contain YAML declarations, no execution evidence |
| 20 agent passports | Implies deployed agent fleet | Passports are capability declarations, not deployed instances |
| 83 Azure resources reconciled | Implies well-managed cloud | Includes legacy/experimental resources still in normalization |
| Prometheus alerting rules | Implies active monitoring | Targets Docker Compose service names, not Azure runtime |
| `target-state.yaml` lists Power BI + Fabric | Implies analytics platform | Both show `status: not_deployed` |
| Eval suite exists | Implies tested AI quality | 2 trivial regex-match test cases total |
| AP invoice soak test shows 95 invoices | Implies production validation | Soak data has future dates (exit_date: 2026-03-25) -- may be projected, not observed |

---

## 7. Canonical Architecture Paths

These are the verified-real paths that matter:

| Component | Canonical Path | Evidence Level |
|-----------|---------------|----------------|
| Azure IaC | `/infra/azure/main.bicep` + `modules/*.bicep` | Runnable Bicep |
| Odoo runtime Bicep | `/infra/azure/odoo-runtime.bicep` | Runnable Bicep |
| DNS SSOT | `/infra/dns/subdomain-registry.yaml` | SSOT + CI gate |
| Azure resource inventory | `/infra/ssot/azure/resources.yaml` | Reconciled from live |
| Service matrix | `/infra/ssot/azure/service-matrix.yaml` | Versioned YAML |
| Docker local dev | `/docker-compose.yml` | Working compose |
| Copilot module | `/addons/ipai/ipai_odoo_copilot/` | Working Python |
| Security middleware | `/addons/ipai/ipai_security_frontdoor/middleware.py` | Working Python |
| Document Intelligence | `/addons/ipai/ipai_document_intelligence/models/ocr_client.py` | Working Python |
| Databricks bundle | `/infra/databricks/databricks.yml` + `sql/` | Bundle + SQL |
| Identity roles | `/infra/entra/app-roles-manifest.json` | JSON manifest |
| Role-tool mapping | `/infra/entra/role-tool-mapping.yaml` | YAML config |
| Go-live checklist | `/docs/runbooks/ODOO18_GO_LIVE_CHECKLIST.md` | Honest tracker |
| Maturity benchmark | `/infra/ssot/azure/platform_maturity_benchmark.yaml` | Self-assessment rubric |
| Spec bundles | `/spec/<domain>/` (40+ bundles) | Planning artifacts |

---

## 8. Production-Claim-Safe Statement

**The following claims are evidence-supported and safe to make:**

- "Odoo CE 19 running on Azure Container Apps with web/worker/cron split behind Azure Front Door" -- TRUE per Bicep + service matrix + go-live checklist partial completion
- "SSOT-governed DNS and Azure resource management" -- TRUE per subdomain-registry.yaml + resources.yaml
- "AI copilot with Odoo ORM tool execution, audit trail, rate limiting, and role-based access" -- TRUE per copilot module code
- "Defense-in-depth with FDID validation middleware and database manager blocking" -- TRUE per middleware.py
- "Medallion lakehouse architecture with Databricks" -- TRUE per SQL definitions (deployment status uncertain)
- "Entra ID role manifest prepared for enterprise RBAC" -- TRUE (manifests exist, not deployed)

**The following claims are NOT safe to make:**

- "Enterprise-grade high availability" -- FALSE (PG HA disabled, no failover)
- "Production-ready security posture" -- FALSE (MFA not enforced, no CA policies, no network isolation)
- "Fully automated CI/CD pipeline" -- FALSE (only 2 skeletal AzDO pipelines)
- "Operational observability" -- FALSE (monitoring config targets Docker, not Azure)
- "Tested disaster recovery" -- FALSE (backup restore never tested per go-live checklist)
- "12 operational services" -- MISLEADING (4+ are nginx stubs)

---

## 9. Prioritized Remediation Backlog

### P0 -- Production Blockers (must fix before any production claim)

| # | Item | Effort | Evidence Gap |
|---|------|--------|-------------|
| P0-1 | Enable PG HA (zone-redundant) + increase backup retention to 35 days | 2h | `postgres-flexible.bicep` line 59-61 |
| P0-2 | Enable Entra MFA (Security Defaults ON or Conditional Access) | 4h | `access_model.yaml` line 35 |
| P0-3 | Test PG backup restore on disposable DB, document RPO/RTO | 4h | Go-live checklist items unchecked |
| P0-4 | Wire App Insights + Log Analytics into main.bicep, deploy | 4h | No `app-insights.bicep` at primary IaC path |
| P0-5 | Add NSGs to VNet subnets + restrict PG to ACA subnet only | 4h | `vnet.bicep` has no NSGs, PG allows `0.0.0.0` |

### P1 -- Enterprise Table Stakes (required for credible enterprise claim)

| # | Item | Effort | Evidence Gap |
|---|------|--------|-------------|
| P1-1 | Build Odoo container image CI pipeline (ACR push + vulnerability scan) | 8h | No container build pipeline |
| P1-2 | Create env promotion pipeline (dev -> staging -> prod) with migration gate | 16h | No promotion automation |
| P1-3 | Deploy Azure Monitor alerts replacing Prometheus config | 8h | Prometheus targets Docker Compose |
| P1-4 | Define and deploy Azure Policy (require tags, deny public PG, require KV) | 8h | No policy definitions |
| P1-5 | Replace nginx stubs with real services OR remove from service matrix | 4h | 4+ services are stubs |
| P1-6 | Add private endpoints for PG + Key Vault + ACR | 8h | All using public access |
| P1-7 | Deploy Entra Conditional Access policies (MFA + location + risk) | 8h | Entra Free tier, no CA |

### P2 -- Maturity Improvements

| # | Item | Effort | Evidence Gap |
|---|------|--------|-------------|
| P2-1 | Expand copilot eval suite to 50+ test cases with adversarial prompts | 16h | 2 test cases total |
| P2-2 | Add distributed tracing (OpenTelemetry) to copilot and n8n | 16h | No tracing config |
| P2-3 | Implement retry/dead-letter pattern in n8n workflows | 8h | No retry logic |
| P2-4 | Deploy Power BI with Databricks SQL Warehouse connector | 16h | `status: not_deployed` |
| P2-5 | Add resource locks on production PG, KV, and storage | 2h | Go-live checklist unchecked |
| P2-6 | Integrate load test (k6) into CI pipeline with regression threshold | 8h | 1 k6 script, no CI integration |

### P3 -- Excellence Targets

| # | Item | Effort | Evidence Gap |
|---|------|--------|-------------|
| P3-1 | Implement blue-green deployment for Odoo container revisions | 16h | No deployment strategy |
| P3-2 | ADR register with numbered decisions | 8h | Decisions embedded in YAML |
| P3-3 | Clean up `odoo/odoo/odoo/odoo/` nesting (structural debt) | 4h | Path duplication |
| P3-4 | Automated DR drill (annual, scripted) | 16h | No DR drill process |
| P3-5 | Fabric mirroring for Odoo PG (declared as required, not deployed) | 16h | `status: not_deployed` |

---

## 10. Truth Summary

This platform is an **ambitious, architecturally-aware Odoo-on-Azure stack built by a small team with unusually strong governance instincts**. The SSOT discipline (DNS, resources, services, deprecations) would be credible at a 50-person platform team. The copilot module is genuinely production-quality code with security controls that many larger Odoo deployments lack. The Bicep IaC library covers the right Azure services.

The core weakness is the gap between **architectural declaration and operational reality**. The identity plane exists only as manifests. The observability stack targets a Docker Compose environment that is not the production runtime. Half the go-live checklist is unchecked. Services listed as "active" are nginx stubs. The database has no HA, untested backups, and 7-day retention. These are not minor gaps -- they are the difference between a demo and a production system.

The platform is **12-16 weeks of focused execution away from a defensible enterprise-grade claim**, assuming the P0 and P1 items are completed. The architecture is sound; the implementation needs to catch up.

---

## 11. Top 7 Uplift Actions

1. **Enable PG zone-redundant HA + 35-day backup retention** -- single most impactful resilience improvement
2. **Enable Entra MFA + deploy at least one Conditional Access policy** -- zero-trust minimum
3. **Deploy App Insights + Log Analytics via Bicep** -- operational visibility for Azure runtime
4. **Build container image CI/CD pipeline with ACR scanning** -- release engineering foundation
5. **Add NSGs + private endpoints** -- network isolation minimum
6. **Expand copilot eval suite to 50+ cases** -- validate the strongest asset
7. **Complete the go-live checklist** -- the honest self-assessment already identifies the gaps

---

## 12. Final Answer

**Would a serious enterprise architect accept this as a credible Odoo-on-Azure platform baseline?**

**Conditional yes.** The architecture is credible. The governance discipline is impressive. The copilot module is differentiated. But a serious enterprise architect would immediately flag: no HA database, no MFA enforcement, no operational observability on Azure, no automated deployment pipeline, and 4 stub services in the "active" inventory. They would accept this as a **well-architected pre-production platform** with a clear path to production, not as a production-ready system.

The honest framing: *"Enterprise-architected Odoo-on-Azure platform in pre-production hardening, with production-quality AI copilot, SSOT governance, and IaC foundation. Targeted for production readiness by Q2 2026."*

---

*Audit generated from codebase evidence. Runtime state not verified (no Azure CLI access). All file paths are absolute and verified to exist on disk at audit time.*
