---
title: Automations Inventory
version: 1.0
repo: Insightpulseai/odoo
owner: Insightpulseai
generated_from: Scripts, .github, supabase/functions, n8n
generated_at: 2026-02-23T17:11:45.984754+00:00
last_verified: Auto
status: Verified
ssot_intent: Track scheduled execution across the monorepo
---

# Automations Inventory

## 1. Scope and Source Paths
Verified inventory of scheduled/automated execution mechanisms.
- **Odoo**: `addons/**`
- **Supabase**: `supabase/functions/**`
- **Other**: `.github/workflows/**`, `**/*n8n*.json`

## 2. Executive Summary
- **Odoo Cron Jobs**: 0
- **Supabase Edge Functions**: 59
- **GitHub Actions**: 269
- **n8n Workflows**: 9
- **Workers/Queue**: 0 (explicitly running)
- **High-Risk Drift Items**: 3

## 3. Odoo Cron Jobs
| ID | Name | Target | Interval | Config Status | Active |
|---|---|---|---|---|---|
| None detected in standard module locations (excluding sandbox). | | | | | |

## 4. Supabase Edge Functions
| Function | Trigger | Context | Enablement |
|---|---|---|---|
| seed-odoo-finance | HTTP/Webhook | supabase/functions/seed-odoo-finance/index.ts | unknown |
| jobs-worker | Webhook | supabase/functions/jobs-worker/index.ts | unknown |
| copilot-chat | HTTP/Webhook | supabase/functions/copilot-chat/index.ts | unknown |
| cron-processor | Scheduled | supabase/functions/cron-processor/index.ts | unknown |
| ops-job-worker | HTTP/Webhook | supabase/functions/ops-job-worker/index.ts | unknown |
| shadow-odoo-finance | HTTP/Webhook | supabase/functions/shadow-odoo-finance/index.ts | unknown |
| bugbot-control-plane | HTTP/Webhook | supabase/functions/bugbot-control-plane/index.ts | unknown |
| serve-erd | HTTP/Webhook | supabase/functions/serve-erd/index.ts | unknown |
| zoho-mail-bridge | HTTP/Webhook | supabase/functions/zoho-mail-bridge/index.ts | unknown |
| odoo-webhook | Webhook | supabase/functions/odoo-webhook/index.ts | unknown |
| repo-hygiene-runner | HTTP/Webhook | supabase/functions/repo-hygiene-runner/index.ts | unknown |
| semantic-query | HTTP/Webhook | supabase/functions/semantic-query/index.ts | unknown |
| platformkit-introspect | HTTP/Webhook | supabase/functions/platformkit-introspect/index.ts | unknown |
| secret-smoke | HTTP/Webhook | supabase/functions/secret-smoke/index.ts | unknown |
| ops-trigger-build | HTTP/Webhook | supabase/functions/ops-trigger-build/index.ts | unknown |
| embed-chunk-worker | Webhook | supabase/functions/embed-chunk-worker/index.ts | unknown |
| plane-sync | Webhook | supabase/functions/plane-sync/index.ts | unknown |
| health | HTTP/Webhook | supabase/functions/health/index.ts | unknown |
| expense-policy-check | HTTP/Webhook | supabase/functions/expense-policy-check/index.ts | unknown |
| realtime-sync | HTTP/Webhook | supabase/functions/realtime-sync/index.ts | unknown |
| ops-summary | HTTP/Webhook | supabase/functions/ops-summary/index.ts | unknown |
| ops-metrics-ingest | HTTP/Webhook | supabase/functions/ops-metrics-ingest/index.ts | unknown |
| config-publish | HTTP/Webhook | supabase/functions/config-publish/index.ts | unknown |
| auth-otp-request | HTTP/Webhook | supabase/functions/auth-otp-request/index.ts | unknown |
| auth-bootstrap | HTTP/Webhook | supabase/functions/auth-bootstrap/index.ts | unknown |
| sync-odoo-modules | HTTP/Webhook | supabase/functions/sync-odoo-modules/index.ts | unknown |
| docs-ai-ask | HTTP/Webhook | supabase/functions/docs-ai-ask/index.ts | unknown |
| sync-kb-to-schema | HTTP/Webhook | supabase/functions/sync-kb-to-schema/index.ts | unknown |
| lib-brain-sync | Webhook | supabase/functions/lib-brain-sync/index.ts | unknown |
| semantic-export-osi | HTTP/Webhook | supabase/functions/semantic-export-osi/index.ts | unknown |
| bir-urgent-alert | Webhook | supabase/functions/bir-urgent-alert/index.ts | unknown |
| github-app-auth | Webhook | supabase/functions/github-app-auth/index.ts | unknown |
| catalog-sync | HTTP/Webhook | supabase/functions/catalog-sync/index.ts | unknown |
| context-resolve | HTTP/Webhook | supabase/functions/context-resolve/index.ts | unknown |
| marketplace-webhook | Webhook | supabase/functions/marketplace-webhook/index.ts | unknown |
| _template-bridge | HTTP/Webhook | supabase/functions/_template-bridge/index.ts | unknown |
| odoo-template-export | HTTP/Webhook | supabase/functions/odoo-template-export/index.ts | unknown |
| run-executor | Webhook | supabase/functions/run-executor/index.ts | unknown |
| skill-eval | HTTP/Webhook | supabase/functions/skill-eval/index.ts | unknown |
| executor | HTTP/Webhook | supabase/functions/executor/index.ts | unknown |
| tenant-invite | HTTP/Webhook | supabase/functions/tenant-invite/index.ts | unknown |
| vendor-score | HTTP/Webhook | supabase/functions/vendor-score/index.ts | unknown |
| webhook-ingest | Webhook | supabase/functions/webhook-ingest/index.ts | unknown |
| ops-runner | HTTP/Webhook | supabase/functions/ops-runner/index.ts | unknown |
| mcp-gateway | Webhook | supabase/functions/mcp-gateway/index.ts | unknown |
| ops-ingest | HTTP/Webhook | supabase/functions/ops-ingest/index.ts | unknown |
| ops-health | HTTP/Webhook | supabase/functions/ops-health/index.ts | unknown |
| three-way-match | HTTP/Webhook | supabase/functions/three-way-match/index.ts | unknown |
| consumer-heartbeat | HTTP/Webhook | supabase/functions/consumer-heartbeat/index.ts | unknown |
| auth-otp-verify | HTTP/Webhook | supabase/functions/auth-otp-verify/index.ts | unknown |
| memory-ingest | HTTP/Webhook | supabase/functions/memory-ingest/index.ts | unknown |
| email-events | Webhook | supabase/functions/email-events/index.ts | unknown |
| odoo-proxy | HTTP/Webhook | supabase/functions/odoo-proxy/index.ts | unknown |
| schema-changed | HTTP/Webhook | supabase/functions/schema-changed/index.ts | unknown |
| infra-memory-ingest | HTTP/Webhook | supabase/functions/infra-memory-ingest/index.ts | unknown |
| ipai-copilot | HTTP/Webhook | supabase/functions/ipai-copilot/index.ts | unknown |
| ops-advisory-scan | HTTP/Webhook | supabase/functions/ops-advisory-scan/index.ts | unknown |
| semantic-import-osi | HTTP/Webhook | supabase/functions/semantic-import-osi/index.ts | unknown |
| tick | HTTP/Webhook | supabase/functions/tick/index.ts | unknown |

## 5. Other Automations
| Name | Type | Trigger | Enablement |
|---|---|---|---|
| repo-structure-guard | github-action | Push/PR | enabled |
| superset-ci-cd | github-action | Manual, Push/PR | enabled |
| odoo-generated-artifacts | github-action | Manual, Push/PR | enabled |
| Colima Desktop Release | github-action | Manual, Push/PR | enabled |
| NO_CLI_NO_DOCKER Gate | github-action | Push/PR | enabled |
| IPAI AI Platform CI | github-action | Push/PR | enabled |
| skills-build-drift | github-action | Push/PR | enabled |
| Agent Preflight | github-action | Manual, Push/PR | enabled |
| All-Green Gates | github-action | Push/PR | enabled |
| CI - Web App | github-action | Push/PR | enabled |
| docs-current-state-gate | github-action | Push/PR | enabled |
| cursor-bugbot | github-action | Push/PR | enabled |
| Policy Gates (Governance SSOT) | github-action | Push/PR | enabled |
| Databricks Deploy Prod | github-action | Manual, Push/PR | enabled |
| Odoo Semantic Lint | github-action | Push/PR | enabled |
| GraphRAG Indexer Manifest Check | github-action | Manual, Push/PR | enabled |
| parity-tier0 | github-action | Push/PR | enabled |
| Parity Targets Gate | github-action | Push/PR | enabled |
| org-policy-baseline | github-action | Push/PR | enabled |
| SaaS Landing Visual Regression | github-action | Push/PR | enabled |
| Patch Release | github-action | Manual, Push/PR | enabled |
| ship-on-deploy | github-action | Unknown | enabled |
| Docker Compose SSOT Gate | github-action | Push/PR | enabled |
| IPAI Determinism Check | github-action | Push/PR | enabled |
| org-parity-guard | github-action | Push/PR | enabled |
| Supabase DB PR Check | github-action | Push/PR | enabled |
| github-waf-assessment | github-action | Cron: 0 2 * * 1, Manual | enabled |
| odoo-dbname-gate | github-action | Push/PR | enabled |
| MCP Jobs Executor | github-action | Cron: Defined, Manual | enabled |
| AI Module Naming Gate | github-action | Push/PR | enabled |
| Databricks Deploy Dev | github-action | Manual, Push/PR | enabled |
| Databricks DAB CI | github-action | Manual, Push/PR | enabled |
| InsightPulse CI/CD | github-action | Manual, Push/PR | enabled |
| Odoo/OCA Layout Lint | github-action | Manual, Push/PR | enabled |
| catalog-gate | github-action | Push/PR | enabled |
| audit-contract | github-action | Manual, Push/PR | enabled |
| Deploy Production | github-action | Push/PR | enabled |
| docs-build | github-action | Manual, Push/PR | enabled |
| Finance PPM — Team Directory & Seed SSOT Gate | github-action | Push/PR | enabled |
| Azure WAF Parity Gate | github-action | Cron: Defined, Manual, Push/PR | enabled |
| docflow-smoke | github-action | Push/PR | enabled |
| superset-bootstrap | github-action | Manual, Push/PR | enabled |
| Verify Staging | github-action | Manual | enabled |
| CD Production | github-action | Manual, Push/PR | enabled |
| Nightly Integration Audit | github-action | Cron: Defined, Manual, Push/PR | enabled |
| Supabase Branching | github-action | Manual, Push/PR | enabled |
| auto-install-parity-modules | github-action | Manual, Push/PR | enabled |
| module-catalog-drift | github-action | Manual, Push/PR | enabled |
| Block deprecated repo references | github-action | Push/PR | enabled |
| OdooOps Preflight | github-action | Push/PR | enabled |
| ... and 219 more. | | | |
| OCR Expense → Odoo Expense Record | n8n-workflow | webhook | unknown |
| n8n_enrichment_agent.json | n8n-workflow | webhook | unknown |
| BIR Deadline Alert → Odoo Task + Mattermost | n8n-workflow | webhook | unknown |
| Scout Transaction Sync → Supabase Bronze | n8n-workflow | webhook | unknown |
| InsightPulse - Tenant Provisioning Pipeline | n8n-workflow | webhook | unknown |
| Finance PPM - AI Journal Posting (Claude API + Odoo 19) | n8n-workflow | scheduleTrigger | unknown |
| Finance PPM - BIR e-Filing Automation (eFPS/eAFS) | n8n-workflow | webhook | unknown |
| Finance PPM - BIR Form Generation (Odoo 19 PH) | n8n-workflow | scheduleTrigger | unknown |
| Finance PPM - Recurrent Alerts (Odoo 19) | n8n-workflow | scheduleTrigger | unknown |

## 6. Status Matrix
| ID | Name | Type | Platform | Source Path | Trigger | Def Status | Config Status | En Status | Run Status | Verif Basis | Conf | Owner | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| func_seed-odoo-finance | seed-odoo-finance | edge-function | Supabase | supabase/functions/seed-odoo-finance/index.ts | HTTP/Webhook | present | configured | unknown | unknown | repo-static | high | Auto |  |
| func_jobs-worker | jobs-worker | edge-function | Supabase | supabase/functions/jobs-worker/index.ts | Webhook | present | configured | unknown | unknown | repo-static | high | Auto |  |
| func_copilot-chat | copilot-chat | edge-function | Supabase | supabase/functions/copilot-chat/index.ts | HTTP/Webhook | present | configured | unknown | unknown | repo-static | high | Auto |  |
| func_cron-processor | cron-processor | edge-function | Supabase | supabase/functions/cron-processor/index.ts | Scheduled | present | configured | unknown | unknown | repo-static | high | Auto |  |
| func_ops-job-worker | ops-job-worker | edge-function | Supabase | supabase/functions/ops-job-worker/index.ts | HTTP/Webhook | present | configured | unknown | unknown | repo-static | high | Auto |  |
| func_shadow-odoo-finance | shadow-odoo-finance | edge-function | Supabase | supabase/functions/shadow-odoo-finance/index.ts | HTTP/Webhook | present | configured | unknown | unknown | repo-static | high | Auto |  |
| func_bugbot-control-plane | bugbot-control-plane | edge-function | Supabase | supabase/functions/bugbot-control-plane/index.ts | HTTP/Webhook | present | configured | unknown | unknown | repo-static | high | Auto |  |
| func_serve-erd | serve-erd | edge-function | Supabase | supabase/functions/serve-erd/index.ts | HTTP/Webhook | present | configured | unknown | unknown | repo-static | high | Auto |  |
| func_zoho-mail-bridge | zoho-mail-bridge | edge-function | Supabase | supabase/functions/zoho-mail-bridge/index.ts | HTTP/Webhook | present | configured | unknown | unknown | repo-static | high | Auto |  |
| func_odoo-webhook | odoo-webhook | edge-function | Supabase | supabase/functions/odoo-webhook/index.ts | Webhook | present | configured | unknown | unknown | repo-static | high | Auto |  |
| func_repo-hygiene-runner | repo-hygiene-runner | edge-function | Supabase | supabase/functions/repo-hygiene-runner/index.ts | HTTP/Webhook | present | configured | unknown | unknown | repo-static | high | Auto |  |
| func_semantic-query | semantic-query | edge-function | Supabase | supabase/functions/semantic-query/index.ts | HTTP/Webhook | present | configured | unknown | unknown | repo-static | high | Auto |  |
| func_platformkit-introspect | platformkit-introspect | edge-function | Supabase | supabase/functions/platformkit-introspect/index.ts | HTTP/Webhook | present | configured | unknown | unknown | repo-static | high | Auto |  |
| func_secret-smoke | secret-smoke | edge-function | Supabase | supabase/functions/secret-smoke/index.ts | HTTP/Webhook | present | configured | unknown | unknown | repo-static | high | Auto |  |
| func_ops-trigger-build | ops-trigger-build | edge-function | Supabase | supabase/functions/ops-trigger-build/index.ts | HTTP/Webhook | present | configured | unknown | unknown | repo-static | high | Auto |  |
| func_embed-chunk-worker | embed-chunk-worker | edge-function | Supabase | supabase/functions/embed-chunk-worker/index.ts | Webhook | present | configured | unknown | unknown | repo-static | high | Auto |  |
| func_plane-sync | plane-sync | edge-function | Supabase | supabase/functions/plane-sync/index.ts | Webhook | present | configured | unknown | unknown | repo-static | high | Auto |  |
| func_health | health | edge-function | Supabase | supabase/functions/health/index.ts | HTTP/Webhook | present | configured | unknown | unknown | repo-static | high | Auto |  |
| func_expense-policy-check | expense-policy-check | edge-function | Supabase | supabase/functions/expense-policy-check/index.ts | HTTP/Webhook | present | configured | unknown | unknown | repo-static | high | Auto |  |
| func_realtime-sync | realtime-sync | edge-function | Supabase | supabase/functions/realtime-sync/index.ts | HTTP/Webhook | present | configured | unknown | unknown | repo-static | high | Auto |  |
| func_ops-summary | ops-summary | edge-function | Supabase | supabase/functions/ops-summary/index.ts | HTTP/Webhook | present | configured | unknown | unknown | repo-static | high | Auto |  |
| func_ops-metrics-ingest | ops-metrics-ingest | edge-function | Supabase | supabase/functions/ops-metrics-ingest/index.ts | HTTP/Webhook | present | configured | unknown | unknown | repo-static | high | Auto |  |
| func_config-publish | config-publish | edge-function | Supabase | supabase/functions/config-publish/index.ts | HTTP/Webhook | present | configured | unknown | unknown | repo-static | high | Auto |  |
| func_auth-otp-request | auth-otp-request | edge-function | Supabase | supabase/functions/auth-otp-request/index.ts | HTTP/Webhook | present | configured | unknown | unknown | repo-static | high | Auto |  |
| func_auth-bootstrap | auth-bootstrap | edge-function | Supabase | supabase/functions/auth-bootstrap/index.ts | HTTP/Webhook | present | configured | unknown | unknown | repo-static | high | Auto |  |
| func_sync-odoo-modules | sync-odoo-modules | edge-function | Supabase | supabase/functions/sync-odoo-modules/index.ts | HTTP/Webhook | present | configured | unknown | unknown | repo-static | high | Auto |  |
| func_docs-ai-ask | docs-ai-ask | edge-function | Supabase | supabase/functions/docs-ai-ask/index.ts | HTTP/Webhook | present | configured | unknown | unknown | repo-static | high | Auto |  |
| func_sync-kb-to-schema | sync-kb-to-schema | edge-function | Supabase | supabase/functions/sync-kb-to-schema/index.ts | HTTP/Webhook | present | configured | unknown | unknown | repo-static | high | Auto |  |
| func_lib-brain-sync | lib-brain-sync | edge-function | Supabase | supabase/functions/lib-brain-sync/index.ts | Webhook | present | configured | unknown | unknown | repo-static | high | Auto |  |
| func_semantic-export-osi | semantic-export-osi | edge-function | Supabase | supabase/functions/semantic-export-osi/index.ts | HTTP/Webhook | present | configured | unknown | unknown | repo-static | high | Auto |  |
| func_bir-urgent-alert | bir-urgent-alert | edge-function | Supabase | supabase/functions/bir-urgent-alert/index.ts | Webhook | present | configured | unknown | unknown | repo-static | high | Auto |  |
| func_github-app-auth | github-app-auth | edge-function | Supabase | supabase/functions/github-app-auth/index.ts | Webhook | present | configured | unknown | unknown | repo-static | high | Auto |  |
| func_catalog-sync | catalog-sync | edge-function | Supabase | supabase/functions/catalog-sync/index.ts | HTTP/Webhook | present | configured | unknown | unknown | repo-static | high | Auto |  |
| func_context-resolve | context-resolve | edge-function | Supabase | supabase/functions/context-resolve/index.ts | HTTP/Webhook | present | configured | unknown | unknown | repo-static | high | Auto |  |
| func_marketplace-webhook | marketplace-webhook | edge-function | Supabase | supabase/functions/marketplace-webhook/index.ts | Webhook | present | configured | unknown | unknown | repo-static | high | Auto |  |
| func__template-bridge | _template-bridge | edge-function | Supabase | supabase/functions/_template-bridge/index.ts | HTTP/Webhook | present | configured | unknown | unknown | repo-static | high | Auto |  |
| func_odoo-template-export | odoo-template-export | edge-function | Supabase | supabase/functions/odoo-template-export/index.ts | HTTP/Webhook | present | configured | unknown | unknown | repo-static | high | Auto |  |
| func_run-executor | run-executor | edge-function | Supabase | supabase/functions/run-executor/index.ts | Webhook | present | configured | unknown | unknown | repo-static | high | Auto |  |
| func_skill-eval | skill-eval | edge-function | Supabase | supabase/functions/skill-eval/index.ts | HTTP/Webhook | present | configured | unknown | unknown | repo-static | high | Auto |  |
| func_executor | executor | edge-function | Supabase | supabase/functions/executor/index.ts | HTTP/Webhook | present | configured | unknown | unknown | repo-static | high | Auto |  |
| func_tenant-invite | tenant-invite | edge-function | Supabase | supabase/functions/tenant-invite/index.ts | HTTP/Webhook | present | configured | unknown | unknown | repo-static | high | Auto |  |
| func_vendor-score | vendor-score | edge-function | Supabase | supabase/functions/vendor-score/index.ts | HTTP/Webhook | present | configured | unknown | unknown | repo-static | high | Auto |  |
| func_webhook-ingest | webhook-ingest | edge-function | Supabase | supabase/functions/webhook-ingest/index.ts | Webhook | present | configured | unknown | unknown | repo-static | high | Auto |  |
| func_ops-runner | ops-runner | edge-function | Supabase | supabase/functions/ops-runner/index.ts | HTTP/Webhook | present | configured | unknown | unknown | repo-static | high | Auto |  |
| func_mcp-gateway | mcp-gateway | edge-function | Supabase | supabase/functions/mcp-gateway/index.ts | Webhook | present | configured | unknown | unknown | repo-static | high | Auto |  |
| func_ops-ingest | ops-ingest | edge-function | Supabase | supabase/functions/ops-ingest/index.ts | HTTP/Webhook | present | configured | unknown | unknown | repo-static | high | Auto |  |
| func_ops-health | ops-health | edge-function | Supabase | supabase/functions/ops-health/index.ts | HTTP/Webhook | present | configured | unknown | unknown | repo-static | high | Auto |  |
| func_three-way-match | three-way-match | edge-function | Supabase | supabase/functions/three-way-match/index.ts | HTTP/Webhook | present | configured | unknown | unknown | repo-static | high | Auto |  |
| func_consumer-heartbeat | consumer-heartbeat | edge-function | Supabase | supabase/functions/consumer-heartbeat/index.ts | HTTP/Webhook | present | configured | unknown | unknown | repo-static | high | Auto |  |
| func_auth-otp-verify | auth-otp-verify | edge-function | Supabase | supabase/functions/auth-otp-verify/index.ts | HTTP/Webhook | present | configured | unknown | unknown | repo-static | high | Auto |  |
| func_memory-ingest | memory-ingest | edge-function | Supabase | supabase/functions/memory-ingest/index.ts | HTTP/Webhook | present | configured | unknown | unknown | repo-static | high | Auto |  |
| func_email-events | email-events | edge-function | Supabase | supabase/functions/email-events/index.ts | Webhook | present | configured | unknown | unknown | repo-static | high | Auto |  |
| func_odoo-proxy | odoo-proxy | edge-function | Supabase | supabase/functions/odoo-proxy/index.ts | HTTP/Webhook | present | configured | unknown | unknown | repo-static | high | Auto |  |
| func_schema-changed | schema-changed | edge-function | Supabase | supabase/functions/schema-changed/index.ts | HTTP/Webhook | present | configured | unknown | unknown | repo-static | high | Auto |  |
| func_infra-memory-ingest | infra-memory-ingest | edge-function | Supabase | supabase/functions/infra-memory-ingest/index.ts | HTTP/Webhook | present | configured | unknown | unknown | repo-static | high | Auto |  |
| func_ipai-copilot | ipai-copilot | edge-function | Supabase | supabase/functions/ipai-copilot/index.ts | HTTP/Webhook | present | configured | unknown | unknown | repo-static | high | Auto |  |
| func_ops-advisory-scan | ops-advisory-scan | edge-function | Supabase | supabase/functions/ops-advisory-scan/index.ts | HTTP/Webhook | present | configured | unknown | unknown | repo-static | high | Auto |  |
| func_semantic-import-osi | semantic-import-osi | edge-function | Supabase | supabase/functions/semantic-import-osi/index.ts | HTTP/Webhook | present | configured | unknown | unknown | repo-static | high | Auto |  |
| func_tick | tick | edge-function | Supabase | supabase/functions/tick/index.ts | HTTP/Webhook | present | configured | unknown | unknown | repo-static | high | Auto |  |
| repo-structure-guard | repo-structure-guard | github-action | GitHub | .github/workflows/repo-structure-guard.yml | Push/PR | present | configured | enabled | unknown | repo-static | high | Auto |  |
| superset-ci-cd | superset-ci-cd | github-action | GitHub | .github/workflows/superset-ci-cd.yml | Manual, Push/PR | present | configured | enabled | unknown | repo-static | high | Auto |  |
| odoo-generated-artifacts | odoo-generated-artifacts | github-action | GitHub | .github/workflows/odoo-generated-artifacts.yml | Manual, Push/PR | present | configured | enabled | unknown | repo-static | high | Auto |  |
| colima-desktop-release | Colima Desktop Release | github-action | GitHub | .github/workflows/colima-desktop-release.yml | Manual, Push/PR | present | configured | enabled | unknown | repo-static | high | Auto |  |
| no-cli-no-docker-gate | NO_CLI_NO_DOCKER Gate | github-action | GitHub | .github/workflows/no-cli-no-docker-gate.yml | Push/PR | present | configured | enabled | unknown | repo-static | high | Auto |  |
| ipai-ai-platform-ci | IPAI AI Platform CI | github-action | GitHub | .github/workflows/ipai-ai-platform-ci.yml | Push/PR | present | configured | enabled | unknown | repo-static | high | Auto |  |
| skills-build-drift | skills-build-drift | github-action | GitHub | .github/workflows/skills-build-drift.yml | Push/PR | present | configured | enabled | unknown | repo-static | high | Auto |  |
| agent-preflight | Agent Preflight | github-action | GitHub | .github/workflows/agent-preflight.yml | Manual, Push/PR | present | configured | enabled | unknown | repo-static | high | Auto |  |
| all-green-gates | All-Green Gates | github-action | GitHub | .github/workflows/all-green-gates.yml | Push/PR | present | configured | enabled | unknown | repo-static | high | Auto |  |
| ci-web | CI - Web App | github-action | GitHub | .github/workflows/ci-web.yml | Push/PR | present | configured | enabled | unknown | repo-static | high | Auto |  |
| docs-current-state-gate | docs-current-state-gate | github-action | GitHub | .github/workflows/docs-current-state-gate.yml | Push/PR | present | configured | enabled | unknown | repo-static | high | Auto |  |
| cursor-bugbot | cursor-bugbot | github-action | GitHub | .github/workflows/cursor-bugbot.yml | Push/PR | present | configured | enabled | unknown | repo-static | high | Auto |  |
| policy-gates | Policy Gates (Governance SSOT) | github-action | GitHub | .github/workflows/policy-gates.yml | Push/PR | present | configured | enabled | unknown | repo-static | high | Auto |  |
| databricks-deploy-prod | Databricks Deploy Prod | github-action | GitHub | .github/workflows/databricks-deploy-prod.yml | Manual, Push/PR | present | configured | enabled | unknown | repo-static | high | Auto |  |
| odoo-semantic-lint | Odoo Semantic Lint | github-action | GitHub | .github/workflows/odoo-semantic-lint.yml | Push/PR | present | configured | enabled | unknown | repo-static | high | Auto |  |
| graphrag-indexer-check | GraphRAG Indexer Manifest Check | github-action | GitHub | .github/workflows/graphrag-indexer-check.yml | Manual, Push/PR | present | configured | enabled | unknown | repo-static | high | Auto |  |
| parity-tier0 | parity-tier0 | github-action | GitHub | .github/workflows/parity-tier0.yml | Push/PR | present | configured | enabled | unknown | repo-static | high | Auto |  |
| parity-targets-gate | Parity Targets Gate | github-action | GitHub | .github/workflows/parity-targets-gate.yml | Push/PR | present | configured | enabled | unknown | repo-static | high | Auto |  |
| org-policy-baseline | org-policy-baseline | github-action | GitHub | .github/workflows/org-policy-baseline.yml | Push/PR | present | configured | enabled | unknown | repo-static | high | Auto |  |
| saas-landing-visual-regression | SaaS Landing Visual Regression | github-action | GitHub | .github/workflows/saas-landing-visual-regression.yml | Push/PR | present | configured | enabled | unknown | repo-static | high | Auto |  |
| patch-release | Patch Release | github-action | GitHub | .github/workflows/patch-release.yml | Manual, Push/PR | present | configured | enabled | unknown | repo-static | high | Auto |  |
| ship-on-deploy | ship-on-deploy | github-action | GitHub | .github/workflows/ship-on-deploy.yml | Unknown | present | configured | enabled | unknown | repo-static | high | Auto |  |
| compose-ssot-gate | Docker Compose SSOT Gate | github-action | GitHub | .github/workflows/compose-ssot-gate.yml | Push/PR | present | configured | enabled | unknown | repo-static | high | Auto |  |
| ipai-determinism | IPAI Determinism Check | github-action | GitHub | .github/workflows/ipai-determinism.yml | Push/PR | present | configured | enabled | unknown | repo-static | high | Auto |  |
| org-parity-guard | org-parity-guard | github-action | GitHub | .github/workflows/org-parity-guard.yml | Push/PR | present | configured | enabled | unknown | repo-static | high | Auto |  |
| supabase-db-pr-check | Supabase DB PR Check | github-action | GitHub | .github/workflows/supabase-db-pr-check.yml | Push/PR | present | configured | enabled | unknown | repo-static | high | Auto |  |
| github-waf-assessment | github-waf-assessment | github-action | GitHub | .github/workflows/github-waf-assessment.yml | Cron: 0 2 * * 1, Manual | present | configured | enabled | unknown | repo-static | high | Auto |  |
| odoo-dbname-gate | odoo-dbname-gate | github-action | GitHub | .github/workflows/odoo-dbname-gate.yml | Push/PR | present | configured | enabled | unknown | repo-static | high | Auto |  |
| mcp-jobs-executor | MCP Jobs Executor | github-action | GitHub | .github/workflows/mcp-jobs-executor.yml | Cron: Defined, Manual | present | configured | enabled | unknown | repo-static | high | Auto |  |
| ai-naming-gate | AI Module Naming Gate | github-action | GitHub | .github/workflows/ai-naming-gate.yml | Push/PR | present | configured | enabled | unknown | repo-static | high | Auto |  |
| databricks-deploy-dev | Databricks Deploy Dev | github-action | GitHub | .github/workflows/databricks-deploy-dev.yml | Manual, Push/PR | present | configured | enabled | unknown | repo-static | high | Auto |  |
| databricks-dab-ci | Databricks DAB CI | github-action | GitHub | .github/workflows/databricks-dab-ci.yml | Manual, Push/PR | present | configured | enabled | unknown | repo-static | high | Auto |  |
| insightpulse-cicd | InsightPulse CI/CD | github-action | GitHub | .github/workflows/insightpulse-cicd.yml | Manual, Push/PR | present | configured | enabled | unknown | repo-static | high | Auto |  |
| odoo-oca-lint | Odoo/OCA Layout Lint | github-action | GitHub | .github/workflows/odoo-oca-lint.yml | Manual, Push/PR | present | configured | enabled | unknown | repo-static | high | Auto |  |
| catalog-gate | catalog-gate | github-action | GitHub | .github/workflows/catalog-gate.yml | Push/PR | present | configured | enabled | unknown | repo-static | high | Auto |  |
| audit-contract | audit-contract | github-action | GitHub | .github/workflows/audit-contract.yml | Manual, Push/PR | present | configured | enabled | unknown | repo-static | high | Auto |  |
| deploy-prod | Deploy Production | github-action | GitHub | .github/workflows/deploy-prod.yml | Push/PR | present | configured | enabled | unknown | repo-static | high | Auto |  |
| docs-build | docs-build | github-action | GitHub | .github/workflows/docs-build.yml | Manual, Push/PR | present | configured | enabled | unknown | repo-static | high | Auto |  |
| finance-team-directory-gate | Finance PPM — Team Directory & Seed SSOT Gate | github-action | GitHub | .github/workflows/finance-team-directory-gate.yml | Push/PR | present | configured | enabled | unknown | repo-static | high | Auto |  |
| azure-waf-parity | Azure WAF Parity Gate | github-action | GitHub | .github/workflows/azure-waf-parity.yml | Cron: Defined, Manual, Push/PR | present | configured | enabled | unknown | repo-static | high | Auto |  |
| docflow-smoke | docflow-smoke | github-action | GitHub | .github/workflows/docflow-smoke.yml | Push/PR | present | configured | enabled | unknown | repo-static | high | Auto |  |
| ... 237 more items | | | | | | | | | | | | | |

## 7. Drift / Gaps / Conflicts
- **Supabase Schedulers Missing**: Many `edge-functions` are registered, but `pg_cron` extensions or external schedulers pointing to them are not formally configured in migrations.
- **Odoo Crons Obfuscated**: Core crons exist in documentation and shadow tables, but no `ir.cron` XML files are active in production `addons/ipai_*` modules.
- **n8n Orchestration Fragments**: `workflows/` directory contains n8n definitions, but tracking which ones are currently *active* requires API introspection outside the repo.

## 8. Top Risks and Immediate Fixes
1. **Define pg_cron explicitly for required Edge Functions.**
2. **Harmonize n8n repository state with production UI state.**
3. **Ensure Playwright tests explicitly cover these async trigger paths.**
4. **Audit GitHub Actions with cron schedules for overlap/duplication.**
5. **Clean up missing / deprecated Odoo crons from docs.**

## 9. Maintenance Rules
- Avoid defining automations purely in UI (e.g. n8n GUI, Odoo GUI). Store exports here.
- Update `automations-inventory.json` automatically via CI sweep.

## 10. Evidence Appendix
See `automations-inventory.json` for full JSON struct and paths.

## 11. Actionable Items & Pending Tasks (Based on Session)
Based on the execution and prior chat history, here are the actionable items and pending tasks:

- [ ] **[Ops] Align Odoo Version Constraint**: Resolve the discrepancy between `rules.md` (Odoo 18) and `CLAUDE.md`/`GEMINI.md` (Odoo 19) to prevent agent hallucination during cron/module generation.
- [ ] **[Subagents] Create Prompt Fallbacks**: Add `skills/subagents/*.prompt.md` files as mandated by `AGENTS.md` so native Gemini flows don't crash without slash commands.
- [ ] **[Data] Edge Function Schedulers**: Write native Supabase `pg_cron` SQL migrations to execute the scheduled Edge Functions mapped in `supabase/functions/*/index.ts`.
- [ ] **[CI/CD] MCP Servers Build Matrix**: Add an `npm run build` step to GitHub Actions for `odoo-erp`, `memory`, and other `source_only` MCP servers in `.claude/mcp-servers.json` so they are immediately accessible to SuperClaude.
- [ ] **[Documentation] Purge Deprecated Crons**: Sync `ir.cron` documentation against the actual `addons/` footprint, as no production-scoped custom crons were detected in the standard directories.
- [ ] **[Integration] n8n Verification Check**: Implement a script (perhaps using the new `n8nClient.ts` MCP tool) to match `.json` definitions in `automations/n8n/` against live deployed status on the platform.
- [ ] **[Automation] Finalize 'Max Integrations' Backbone**: Implement the `ops.integrations`, `ops.webhook_events`, and `ops.jobs` schema from the 'Max Integrations Backbone' implementation plan.