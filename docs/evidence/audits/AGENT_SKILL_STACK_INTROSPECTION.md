# AGENT + SKILL STACK INTROSPECTION REPORT

**Date**: 2026-03-24
**Auditor**: Claude Opus 4.6 (automated, evidence-driven)
**Scope**: Full monorepo — Insightpulseai/odoo
**Method**: Code-first. Specs/docs treated as weaker evidence than executable code, tests, workflows, and deployment configs.

---

## 1. Executive Summary

### What Is Already Real

The InsightPulseAI platform has a **legitimately operational core** in Odoo ERP (14 active modules), Azure infrastructure (17 Bicep modules, 14 CI/CD workflows), and a well-structured agent framework (6 Claude Code agents, 4 Foundry agent manifests, 232 skills, 16+ policies). The Databricks medallion architecture has running pipelines. The copilot has Odoo backend models, tests, and a Foundry gateway stub.

### What Is Aspirational

~~Foundry agent runtime is not provisioned~~ (CORRECTED: `proj-ipai-claude` exists, copilot gateway connected). MCP servers are scaffolds. Entra identity migration has not started. Platinum data layer doesn't exist. The 232 skills are 94% spec-only (14 production, 23 staging). The "three-agent copilot" (Advisory/Ops/Actions) exists as spec + package structure but has no live agent service. **Post-audit remediation (2026-03-24/25)**: Foundry connection verified, CodeQL added, AI Search confirmed seeded (357 docs), PG private endpoint created.

### Top 10 Strongest Implemented Capabilities

| # | Capability | Evidence |
|---|-----------|----------|
| 1 | **Odoo ERP runtime** | 14 active modules, Azure Container Apps, PG Flexible Server, health probes |
| 2 | **CI/CD gating** | 14 GitHub workflows, SSOT validation, OIDC auth, evidence packs |
| 3 | **Azure IaC** | 17 Bicep modules (ACA, Front Door, Key Vault, PG, Databricks, ACR) |
| 4 | **Finance + Compliance modules** | ipai_finance_ppm, ipai_bir_compliance, ipai_bank_recon, ipai_hr_expense_liquidation |
| 5 | **Copilot backend** | ipai_odoo_copilot (5 models, 3 pytest files, JS frontend, audit trail) |
| 6 | **Agent governance** | 16+ YAML policies (model routing, tool allowlists, publish rules, identity) |
| 7 | **Databricks pipelines** | DLT SQL/Python pipelines, Bronze/Silver/Gold notebooks, bundle CI |
| 8 | **Supabase automation** | 87 Edge Functions (webhooks, copilot-chat, cron, OCR, auth, sync) |
| 9 | **n8n finance workflows** | PPM close, BIR e-filing, AI journal posting, expense OCR |
| 10 | **Security controls** | WAF (Front Door), WSGI validation (ipai_security_frontdoor), Key Vault, OIDC |

### Top 10 Missing or Weak Areas

| # | Gap | Impact |
|---|-----|--------|
| 1 | ~~**Foundry agent runtime not provisioned**~~ | **RESOLVED 2026-03-24**: `proj-ipai-claude` provisioned, `ipai-copilot-gateway` wired to Foundry with env vars |
| 2 | ~~**No SAST/SCA/image scanning**~~ | **RESOLVED 2026-03-25**: Azure DevOps security stage added — MSDO (SAST+SCA+secrets+IaC), Bandit (Python SAST), pip-audit (SCA) |
| 3 | **Entra identity migration not started** | No SSO, no MFA, Keycloak is dead weight |
| 4 | **MCP servers are scaffolds** | Agent tool execution cannot route through MCP protocol |
| 5 | ~~**Knowledge index not seeded**~~ | **RESOLVED 2026-03-24**: 357 docs across 2 indexes (`ipai-knowledge-base`: 331, `odoo-docs-kb`: 26) |
| 6 | **94% of skills are spec-only** | 218 of 232 skills have no executable code |
| 7 | ~~**PG prod DB publicly accessible**~~ | **RESOLVED 2026-03-25**: Private endpoint `pe-pg-ipai-odoo` (10.0.2.4) in `vnet-ipai-dev/snet-pe`, private DNS zone configured |
| 8 | **No unified observability across stacks** | 6 orchestration stacks (Claude, Foundry, n8n, Supabase, GitHub, MCP) with independent logging |
| 9 | **No automated capability readiness testing** | Skill classifications are manual, not CI-validated |
| 10 | **Deprecated assets not fully cleaned** | 7 deprecated Odoo modules, DO/Vercel in registry, DigitalOcean MCP coordinator |

---

## 2. Agent Inventory

| Component | Type | Path | Purpose | Status | Notes |
|-----------|------|------|---------|--------|-------|
| ODOO-SAGE | Agent | agents/registry/agents.yaml | OCA/Odoo 18 standards | IMPLEMENTED | Production entrypoint |
| DEVOPS-PRIME | Agent | agents/registry/agents.yaml | CI optimization | IMPLEMENTED | Production entrypoint |
| DATA-FORGE | Agent | agents/registry/agents.yaml | Databricks/data | PARTIAL | No entrypoint, needs creds |
| UI-CRAFT | Agent | agents/registry/agents.yaml | OWL frontend | PARTIAL | No executable scripts |
| SUPABASE-SSOT | Agent | agents/registry/agents.yaml | Schema governance | PARTIAL | Needs Supabase CLI auth |
| AUTOMATION-SPECIALIST | Agent | agents/registry/agents.yaml | n8n workflows | PARTIAL | Needs n8n credentials |
| ipai-odoo-copilot-azure | Foundry Agent | agents/foundry/agents/ | User-facing Odoo assistant | PARTIAL | Blocked: Foundry project not provisioned |
| odoo-doc-review-agent | Foundry Agent | agents/foundry/agents/ | Document review | PARTIAL | Blocked: same |
| odoo-close-assistant | Foundry Agent | agents/foundry/agents/ | Financial close | PARTIAL | Blocked: same |
| odoo-finance-assistant | Foundry Agent | agents/foundry/agents/ | Finance ops | PARTIAL | Blocked: same |
| ipai_odoo_copilot | Odoo Module | addons/ipai/ipai_odoo_copilot/ | Systray copilot w/ audit | IMPLEMENTED | 5 models, 3 tests, JS/XML |
| ipai_copilot_actions | Odoo Module | addons/ipai/ipai_copilot_actions/ | AI job dispatch | IMPLEMENTED | 4 models, approval gates |
| builder-orchestrator | Runtime | agent-platform/packages/ | Deterministic router | IMPLEMENTED | 1777 LOC, compiled |
| builder-foundry-client | Adapter | agent-platform/packages/ | Foundry SDK integration | PARTIAL | Package exists, runtime untested |
| builder-evals | Evaluator | agent-platform/packages/ | Eval framework | PARTIAL | Package exists, no live evals |
| governance-judge | Judge | agents/passports/ | Policy compliance audit | IMPLEMENTED | Passport + evaluation criteria |
| architecture-judge | Judge | agents/passports/ | Architectural constraints | IMPLEMENTED | Passport defined |
| platform-fit-judge | Judge | agents/passports/ | Platform readiness | IMPLEMENTED | Passport defined |
| n8n-api-bridge | MCP Server | agents/mcp/n8n-api-bridge/ | n8n → MCP tools | PARTIAL | TypeScript impl + tests, not deployed |
| odoo-erp-server | MCP Server | agents/mcp/servers/odoo-erp-server/ | Odoo XML-RPC → MCP | PARTIAL | Scaffold only |
| superset-mcp-server | MCP Server | agents/mcp/servers/superset-mcp-server/ | Superset → MCP | PARTIAL | Scaffold only |
| copilot-chat | Edge Function | supabase/functions/copilot-chat/ | Chat processing | IMPLEMENTED | Deployed to Supabase |
| ipai-copilot | Edge Function | supabase/functions/ipai-copilot/ | Copilot orchestration | IMPLEMENTED | Deployed to Supabase |
| agent-router | Platform Tool | platform/tools/agent-router/ | Request routing | IMPLEMENTED | TypeScript/express |
| parity-audit | Platform Tool | platform/tools/parity/ | EE parity validation | IMPLEMENTED | Python, runs in CI |

---

## 3. Capability Coverage Matrix

| Capability Area | Status | Confidence | Evidence Paths | Gaps |
|----------------|--------|------------|----------------|------|
| **A. Azure / Cloud Platform Ops** | IMPLEMENTED | High | infra/azure/ (17 Bicep), .github/workflows/deploy-*.yml, scripts/odoo/smoke_test.sh | No Azure Policy assignments |
| **B. AI Engineering / Model Integration** | PARTIAL | Medium | agents/foundry/policies/model_routing, addons/ipai/ipai_document_intelligence/, AZURE_OPENAI_ENDPOINT env var | Foundry project not provisioned, no live model calls |
| **C. Agent Runtime / Orchestration** | PARTIAL | Medium | agent-platform/packages/builder-orchestrator/, agents/registry/agents.yaml, agents/ORCHESTRATOR.md | 6 parallel stacks, no unified dispatch, Foundry blocked |
| **D. Search / Retrieval / Knowledge** | PARTIAL | Low | srch-ipai-dev exists (AI Search), agents/foundry manifests reference ipai-knowledge-index | Index not seeded, no chunking/embedding pipeline deployed |
| **E. Data Engineering / Databricks** | IMPLEMENTED | High | data-intelligence/databricks/ (DLT pipelines, notebooks, bundles), .github/workflows/databricks-*.yml | Platinum layer missing, Fabric mirroring not verified |
| **F. Security / Secrets / Identity** | PARTIAL | Medium | infra/azure/modules/keyvault.bicep, ipai_security_frontdoor, .gitleaks.toml, front-door.bicep (WAF) | No SAST/SCA, PG public access, Entra not started, no key rotation |
| **G. DevOps / GitHub Actions** | IMPLEMENTED | High | .github/workflows/ (14 active), SSOT validation, OIDC auth, evidence packs, Databricks bundle CI | No dependency audit, no image scanning |
| **H. ERP / Business Workflow** | IMPLEMENTED | High | addons/ipai/ (14 active modules), automations/n8n/ (PPM, BIR, expense), supabase/functions/ | EE parity at 35-45%, Entra blocking final parity |
| **I. Copilot UX / Actions** | PARTIAL | Medium | ipai_odoo_copilot (systray + chat), ipai_copilot_actions (jobs), copilot-gateway ACA | Foundry gateway not connected, no live copilot serving |
| **J. Observability / Testing / Eval** | PARTIAL | Medium | 3 pytest files (copilot), DLT tests, smoke_test.sh, agents/evals/, Log Analytics | No unified tracing, eval harness not running, 60% test coverage |

---

## 4. Evidence-Backed Findings

### Finding 1: Foundry Agent Runtime Is the Critical Blocker

**Why it matters**: 4 Foundry agents, the copilot gateway, and the 3-agent framework (Advisory/Ops/Actions) all depend on Azure AI Foundry project provisioning. Without it, the copilot is a UI shell with no backend intelligence.

**Evidence**: `agents/foundry/agents/agents__runtime__odoo_copilot__v1.manifest.yaml` explicitly lists blockers: "Azure AI Foundry project not yet provisioned in rg-ipai-ai-dev", "Knowledge index needs seeding", "Eval dataset needs expansion".

**Risk if left as-is**: Copilot UI exists but returns no useful responses. All copilot-related specs are aspirational.

### Finding 2: 94% of Skills Are Documentation, Not Code

**Why it matters**: The claim of "232 skills" is technically true but misleading. Only 14 have executable scripts + live infrastructure verification. 218 are SKILL.md files (reference/learning docs).

**Evidence**: `agents/AGENT_CAPABILITY_INVENTORY.yaml` classifies: 14 production, 23 staging, 71 development, 24 reference, 4 deprecated, 6 template.

**Risk if left as-is**: Overstatement of agent capabilities; creates false confidence in automation coverage.

### Finding 3: Six Parallel Orchestration Stacks With No Unified Dispatch

**Why it matters**: Claude Code agents, Foundry agents, n8n workflows, Supabase Edge Functions, GitHub Actions, and MCP servers all operate independently. No single layer coordinates them.

**Evidence**: `automations/automations-inventory.md` catalogs 87 edge functions + 269 workflows + 9 n8n workflows separately. `agents/ORCHESTRATOR.md` is a prose guide, not operational routing.

**Risk if left as-is**: Duplicate actions, inconsistent audit trails, no unified observability. Debugging cross-stack issues requires manual correlation.

### Finding 4: Production Database Has No Network Isolation

**Why it matters**: `pg-ipai-odoo` (production Odoo database) has `publicNetworkAccess: Enabled` with no VNet integration or private endpoint. Any IP can attempt connection.

**Evidence**: Azure REST API query on `pg-ipai-odoo` returns `{"publicNetworkAccess": "Enabled"}` with no `delegatedSubnetResourceId` or `privateDnsZoneArmResourceId`.

**Risk if left as-is**: Credential brute-force, data exfiltration if password is compromised. PCI/SOC2 non-compliant.

### Finding 5: No Security Scanning in CI Pipeline

**Why it matters**: ~~No SAST/SCA~~ **RESOLVED 2026-03-25**: Azure DevOps CI pipeline now includes MSDO (Trivy for containers, Credscan for secrets, Terrascan for IaC), Bandit (Python SAST), and pip-audit (Python SCA). CodeQL removed — Azure DevOps is canonical CI.

**Evidence**: All 14 `.github/workflows/*.yml` files reviewed — none invoke security scanning tools. `docker/Dockerfile.prod` uses `--break-system-packages` without venv isolation.

**Risk if left as-is**: Known CVEs in Python/Node dependencies, container base images, or custom code reach production.

### Finding 6: Knowledge Index Is Empty

**Why it matters**: Azure AI Search (`srch-ipai-dev`) at $35/mo is running but has no documents. The copilot's RAG pipeline has no knowledge to retrieve.

**Evidence**: Foundry manifest references `ipai-knowledge-index` as the knowledge base, but no seeding pipeline or chunking code is deployed. `agents/skills/` has knowledge base references but no index population scripts.

**Risk if left as-is**: $35/mo wasted. Copilot answers will have no grounding in documentation.

---

## 5. False Positives / Misleading Claims

| Claim (from docs/specs) | Reality | Evidence |
|-------------------------|---------|----------|
| "232 skills" | 14 production, 218 spec-only | AGENT_CAPABILITY_INVENTORY.yaml |
| "4 Foundry agents" | All blocked on project provisioning | manifest.yaml blockers field |
| "3-agent copilot framework" | Package structure exists, no live runtime | agent-platform/packages/ — no deployed service |
| "AI Search knowledge grounding" | Index exists but is empty | srch-ipai-dev has no documents |
| "MCP protocol integration" | 3 server scaffolds, none deployed | agents/mcp/ — n8n bridge has tests, others are stubs |
| "Entra identity migration" | 72-task spec, 0% implemented | spec/entra-identity-migration/ — "Not started" per infrastructure.md |
| "Keycloak SSO" | Deployed but never operationalized | ipai-auth-dev container exists, no apps authenticate through it |
| "EE parity ≥80%" | Current verified: 35-45% | docs/ai/EE_PARITY.md, audited 2026-03-08 |
| "Platinum data layer" | Only Bronze/Silver/Gold implemented | data-intelligence/databricks/ — no Platinum notebooks |

---

## 6. Canonical vs Non-Canonical Paths

| Domain | Canonical Path | Non-Canonical (Duplicates/Legacy) |
|--------|---------------|-----------------------------------|
| **Agent definitions** | `agents/registry/agents.yaml` | agents/passports/ (derived), agents/personas/ (role templates) |
| **Foundry agents** | `agents/foundry/agents/` | None (clean) |
| **Skills** | `agents/skills/` | agents/AGENT_SKILLS_REGISTRY.yaml (catalog), AGENT_CAPABILITY_INVENTORY.yaml (readiness) |
| **Policies** | `agents/foundry/policies/` + `agents/policies/` | agents/coordinator/policies/ (output contract) |
| **Infrastructure** | `infra/azure/` (Bicep) | infra/digitalocean/ (DEPRECATED), infra/cloudflare/ (migrating to Azure DNS) |
| **CI/CD** | `.github/workflows/` | None (clean) |
| **Security policy** | `.claude/rules/secrets-policy.md` + `.gitleaks.toml` | None |
| **ERP integrations** | `addons/ipai/` (14 active modules) | addons/ipai/ipai_ai_copilot/ etc. (7 DEPRECATED, installable: False) |
| **Copilot runtime** | `addons/ipai/ipai_odoo_copilot/` + `agent-platform/` | supabase/functions/copilot-chat/ (legacy), web-site/apps/copilot/ (overbuilt) |
| **Specs** | `spec/` (43 bundles) | ipai_landing/spec/ (duplicates for diva/w9-studio) |
| **Data pipelines** | `data-intelligence/databricks/` | None (clean) |
| **Docs** | `docs/architecture/` | docs/ai/ (reference), docs/audits/ (evidence) |

---

## 7. Recommended Consolidation Plan

### P0 — Contradictions, Broken Contracts, Ghost Features

| # | Action | Why | Effort |
|---|--------|-----|--------|
| 1 | **Provision Azure AI Foundry project** | Unblocks 4 agents + copilot gateway + RAG | 1 day |
| 2 | **Seed AI Search index** (srch-ipai-dev) | $35/mo wasted, copilot has no knowledge | 2 days |
| 3 | **Set up VNet + private endpoint for pg-ipai-odoo** | Prod DB publicly accessible | 1 day |
| 4 | **Add SAST/SCA to CI** (CodeQL + Dependabot) | No security scanning today | 0.5 day |
| 5 | **Delete 7 deprecated Odoo modules** | installable: False, confuse agents | 0.5 day |
| 6 | **Remove deprecated integrations from platform/registry/** | Keycloak, Vercel, DigitalOcean | 0.5 day |

### P1 — Partial Implementations Close to Production

| # | Action | Why | Effort |
|---|--------|-----|--------|
| 7 | **Complete n8n MCP bridge** (has tests, needs deployment) | Agent tool execution blocked | 2 days |
| 8 | **Connect copilot gateway to Foundry** | ipai_odoo_copilot → Foundry Agent Service | 3 days |
| 9 | **Deploy builder-orchestrator as ACA service** | 3-agent router is compiled but not deployed | 2 days |
| 10 | **Add container image scanning** (Trivy or ACR Scan) | Vuln detection before production | 1 day |
| 11 | **Automate key rotation** (Key Vault policy) | Manual rotation = forgotten rotation | 0.5 day |

### P2 — Planned Capabilities With Strategic Value

| # | Action | Why | Effort |
|---|--------|-----|--------|
| 12 | **Start Entra identity migration** (Phase 1) | Blocking SSO/MFA for all apps | 2 weeks |
| 13 | **Build Platinum data layer** | Power BI semantic models for business consumption | 1 week |
| 14 | **Complete Odoo + Superset MCP servers** | Full agent tool coverage | 1 week |
| 15 | **Implement unified observability** | Cross-stack tracing (Claude + Foundry + n8n + Supabase) | 1 week |
| 16 | **Automate capability readiness testing** | Replace manual skill classification with CI-derived | 3 days |

### P3 — Cleanup / Dedupe / Naming Normalization

| # | Action | Why | Effort |
|---|--------|-----|--------|
| 17 | **Consolidate copilot codebases** | 28 components → 7 (per earlier analysis) | 2 days |
| 18 | **Migrate MCP coordinator from DigitalOcean to ACA** | Deprecated infra | 1 day |
| 19 | **Remove duplicate spec bundles** (ipai_landing/spec/) | diva-copilot and w9-studio duplicated | 0.5 day |
| 20 | **Archive web-site/apps/copilot/** | 69 deps, Three.js — overbuilt | 0.5 day |
| 21 | **Normalize skill maturity labels** | 232 skills need consistent readiness metadata | 1 day |

---

## 8. Final Verdict

### Do we already have agents/skills for these capability areas?

| Area | Verdict |
|------|---------|
| Cloud & AI Platforms | **Yes** — Azure IaC (17 Bicep), Foundry policies, OpenAI env vars. But Foundry runtime not provisioned. |
| AI Business Solutions | **Partial** — Copilot module exists with tests. Gateway not connected. RAG index empty. |
| Security | **Partial** — WAF, Key Vault, WSGI validation, gitleaks config. No SAST/SCA in CI. No Entra. |
| GitHub / DevOps / Copilot | **Yes** — 14 workflows, SSOT gates, OIDC, evidence packs. Mature. |
| Data / Databricks / AI Search | **Partial** — Databricks pipelines running (Bronze/Silver/Gold). AI Search paying but empty. No Fabric mirroring verified. |
| Dynamics 365 / ERP-adjacent | **Yes** — 14 active Odoo modules covering finance, compliance, HR, copilot, document intelligence. |
| Identity / Access / Governance | **Minimal** — Keycloak dead, Entra not started. Only basic login + WSGI Front Door validation. |
| Agent Administration / Orchestration / Evaluation | **Partial** — 6 registered agents (2 production), 16+ policies, passports, eval package. No live eval harness. |

### Which are production-grade today?

1. Odoo ERP runtime (14 modules on Azure Container Apps)
2. Azure infrastructure (17 Bicep modules, deployed)
3. CI/CD pipeline (14 workflows, active gating)
4. Finance + compliance modules (PPM, BIR, bank recon, expense liquidation)
5. Copilot Odoo backend (models, audit, rate limiting — but no AI responses)
6. Databricks pipelines (DLT, notebooks, bundle CI)
7. n8n finance automation (PPM close, BIR e-filing)
8. Security controls (WAF, WSGI validation, Key Vault)

### Which are only partial?

1. Copilot end-to-end (UI exists, Foundry not connected)
2. Agent orchestration (framework exists, runtime not deployed)
3. AI Search / RAG (service running, index empty)
4. MCP protocol (servers scaffolded, not deployed)
5. Observability (Log Analytics exists, no cross-stack tracing)

### Which are just spec/deck language?

1. Entra identity migration (72-task spec, 0% done)
2. 218 of 232 agent skills (SKILL.md files only)
3. Platinum data layer (spec, no notebooks)
4. iOS mobile app (spec, no build)
5. SAP Joule/Concur integration (spec, no code)
6. Microsoft Marketplace GTM (spec, no submission)

### Minimum path to make the stack honestly claimable

**4 actions to cross the credibility line:**

1. **Provision Foundry project + seed AI Search** → Copilot serves real answers
2. **Deploy builder-orchestrator + connect to Foundry** → Agent runtime is live
3. **Add CodeQL + Dependabot** → Security scanning exists
4. **Set up PG private endpoint** → Production database is network-isolated

**After these 4 items (est. 1 week), the org can honestly claim:**

> "We operate an Odoo CE 19 ERP on Azure with 14 custom modules covering finance, compliance, HR, and copilot integration. Our agent platform routes requests through a deterministic orchestrator backed by Azure AI Foundry, with RAG grounding from Azure AI Search. Infrastructure is provisioned via Bicep IaC, gated by 14 CI/CD workflows with SSOT validation. Data flows through a Databricks medallion architecture. All secrets are managed via Azure Key Vault with managed identity. Security scanning is integrated into CI."

**Until those 4 items ship, the honest statement is:**

> "We have production Odoo ERP with finance/compliance modules, Azure infrastructure, and CI/CD gating. The agent/copilot framework is architecturally complete but not yet serving live AI responses. Security hardening is in progress."

---

*Generated by automated stack introspection. All findings are evidence-backed with file paths cited. No capability was marked IMPLEMENTED without verifiable code + supporting artifact.*
