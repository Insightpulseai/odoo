# Backlog Coverage Report

**Generated**: 2026-01-24T08:42:04.244493Z
**Git SHA**: 5abbe901c168

## Summary

| Status | Count |
|--------|-------|
| Implemented | 64 |
| Partial | 0 |
| Missing | 3 |
| **Total** | **67** |

## Missing Features (Action Required)

| Priority | Category | Title | Target Component | Evidence |
|----------|----------|-------|------------------|----------|
| P2 | Config | TODO: INSERT SAMPLE BIR CONFIG | supabase/seed/9001_erp | supabase/seed/9001_erp/9001_erp_finance_bir_templates.sql:10 |
| P2 | Config | TODO: AGENT REGISTRY | supabase/migrations | supabase/migrations/202512071170_4000_AI_RAG_AND_AGENTS.sql:19 |
| P2 | Config | TODO: comments related to Platform Kit.""" | scripts | scripts/backlog_scan.py:358 |

## Implemented Features

| Priority | Category | Title | Target Component | Evidence |
|----------|----------|-------|------------------|----------|
| P0 | API | Config publish Edge Function | supabase/functions/config-publish | supabase/functions/config-publish/index.ts |
| P0 | CI | Config publish CI workflow | .github/workflows | .github/workflows/config-publish.yml |
| P0 | Config | Design tokens SSOT (config/tokens/tokens.json) | config/tokens | config/tokens/tokens.json |
| P0 | DB | Config Registry schema (ops.config_artifacts, config_versions) | supabase/migrations | spec/supabase-platform-kit-observability/tasks.md:42, supabase/migrations/20260124100001_ops_config_registry.sql:29, supabase/migrations/20260124100001_ops_config_registry.sql:10 |
| P0 | DB | Config Registry RLS policies | supabase/migrations | supabase/migrations/20260124100001_ops_config_registry.sql:165, supabase/migrations/20260124100001_ops_config_registry.sql:196, scripts/backlog_scan.py:96 |
| P0 | DB | Config consumers table (ops.config_consumers) | supabase/migrations | spec/supabase-platform-kit-observability/tasks.md:44, supabase/migrations/20260124100001_ops_config_registry.sql:350, scripts/backlog_scan.py:118 |
| P1 | API | Consumer heartbeat Edge Function | supabase/functions/consumer-heartbeat | supabase/functions/consumer-heartbeat/index.ts |
| P1 | API | Ops health Edge Function | supabase/functions/ops-health | supabase/functions/ops-health/index.ts |
| P1 | Config | Consumers registry (config/consumers/consumers.json) | config/consumers | config/consumers/consumers.json |
| P1 | Config | Spec bundle for Platform Kit observability | spec/supabase-platform-kit-observability | spec/supabase-platform-kit-observability/constitution.md, spec/supabase-platform-kit-observability/prd.md |
| P1 | DB | Config rollouts table (ops.config_rollouts) | supabase/migrations | spec/supabase-platform-kit-observability/tasks.md:46, supabase/migrations/20260124100001_ops_config_registry.sql:97, scripts/backlog_scan.py:128 |
| P1 | DB | Drift detection function (ops.detect_config_drift) | supabase/migrations | supabase/migrations/20260124100001_ops_config_registry.sql:431, supabase/migrations/20260124100001_ops_config_registry.sql:118, scripts/backlog_scan.py:143 |
| P1 | DB | Config rollback RPC function | supabase/migrations | spec/supabase-platform-kit-observability/tasks.md:53, supabase/migrations/20260124100001_ops_config_registry.sql:466, scripts/backlog_scan.py:198 |
| P1 | UI | Control Room Platform Kit UI | apps/control-room | apps/control-room/PLATFORM_KIT_SPEC.md, spec/supabase-platform-kit-observability/plan.md:44, apps/control-room/src/components/observability/ObservabilityManager.tsx:32 |
| P2 | CI | Backlog coverage CI gate | .github/workflows | .github/workflows/backlog-coverage.yml, .github/workflows/backlog-coverage.yml:10, scripts/backlog_scan.py:3 |
| P2 | Config | Create `addons/ipai_platform_workflow/` scaffold | spec/erp-saas-clone-suite | spec/erp-saas-clone-suite/tasks.md |
| P2 | Config | Create `addons/ipai_platform_approvals/` scaffold | spec/erp-saas-clone-suite | spec/erp-saas-clone-suite/tasks.md |
| P2 | Config | Create `addons/ipai_platform_audit/` scaffold | spec/erp-saas-clone-suite | spec/erp-saas-clone-suite/tasks.md |
| P2 | Config | Create `addons/ipai_platform_theme/` scaffold | spec/erp-saas-clone-suite | spec/erp-saas-clone-suite/tasks.md |
| P2 | Config | Implement A1 role configuration model | spec/parallel-control-planes | spec/parallel-control-planes/tasks.md |
| P2 | Config | Create `observability` schema migration | spec/supabase-platform-kit-observability | spec/supabase-platform-kit-observability/tasks.md |
| P2 | Config | Create health API route | spec/supabase-platform-kit-observability | spec/supabase-platform-kit-observability/tasks.md |
| P2 | Config | Create ObservabilityManager component | spec/supabase-platform-kit-observability | spec/supabase-platform-kit-observability/tasks.md |
| P2 | Config | Create HealthTab component | spec/supabase-platform-kit-observability | spec/supabase-platform-kit-observability/tasks.md |
| P2 | Config | Create ops.config_artifacts table | spec/supabase-platform-kit-observability | spec/supabase-platform-kit-observability/tasks.md |
| P2 | Config | Create ops.config_versions table (immutable snapshots) | spec/supabase-platform-kit-observability | spec/supabase-platform-kit-observability/tasks.md |
| P2 | Config | Create ops.config_consumers table (health tracking) | spec/supabase-platform-kit-observability | spec/supabase-platform-kit-observability/tasks.md |
| P2 | Config | Create ops.config_checks table (detailed probes) | spec/supabase-platform-kit-observability | spec/supabase-platform-kit-observability/tasks.md |
| P2 | Config | Create ops.config_rollouts table (deployment tracking) | spec/supabase-platform-kit-observability | spec/supabase-platform-kit-observability/tasks.md |
| P2 | Config | Create ops.config_drift_events table | spec/supabase-platform-kit-observability | spec/supabase-platform-kit-observability/tasks.md |
| P2 | Config | Add Config Registry RLS policies | spec/supabase-platform-kit-observability | spec/supabase-platform-kit-observability/tasks.md |
| P2 | Config | Create publish_config_version RPC | spec/supabase-platform-kit-observability | spec/supabase-platform-kit-observability/tasks.md |
| P2 | Config | Create record_config_check RPC | spec/supabase-platform-kit-observability | spec/supabase-platform-kit-observability/tasks.md |
| P2 | Config | Create detect_config_drift RPC | spec/supabase-platform-kit-observability | spec/supabase-platform-kit-observability/tasks.md |
| P2 | Config | Create rollback_config RPC | spec/supabase-platform-kit-observability | spec/supabase-platform-kit-observability/tasks.md |
| P2 | Config | Create config-publish Edge Function | spec/supabase-platform-kit-observability | spec/supabase-platform-kit-observability/tasks.md |
| P2 | Config | Create design tokens SSOT (config/tokens/tokens.json) | spec/supabase-platform-kit-observability | spec/supabase-platform-kit-observability/tasks.md |
| P2 | Config | Create consumers registry (config/consumers/consumers.json) | spec/supabase-platform-kit-observability | spec/supabase-platform-kit-observability/tasks.md |
| P2 | Config | Create config-publish CI workflow | spec/supabase-platform-kit-observability | spec/supabase-platform-kit-observability/tasks.md |
| P2 | Config | Add settings toggles (config_parameter-backed) | spec/project-ce | spec/project-ce/tasks.md |
| P2 | Config | Menu items for configuration | spec/project-ce | spec/project-ce/tasks.md |
| P2 | Config | Create shared roles configuration | spec/seed-bundle | spec/seed-bundle/tasks.md |
| P2 | Config | Create notion_mapping.yaml configuration | spec/notion-finance-ppm-control-room | spec/notion-finance-ppm-control-room/tasks.md |
| P2 | Config | Create databricks.yml bundle configuration | spec/notion-finance-ppm-control-room | spec/notion-finance-ppm-control-room/tasks.md |
| P2 | Config | Create notion_sync/config.py (configuration loading) | spec/notion-finance-ppm-control-room | spec/notion-finance-ppm-control-room/tasks.md |
| P2 | Config | Create databricks.yml (bundle config) | spec/notion-finance-ppm-control-room | spec/notion-finance-ppm-control-room/tasks.md |
| P2 | Config | Configure Tailwind CSS | spec/notion-finance-ppm-control-room | spec/notion-finance-ppm-control-room/tasks.md |
| P2 | Config | Configure TypeScript | spec/notion-finance-ppm-control-room | spec/notion-finance-ppm-control-room/tasks.md |
| P2 | Config | Create next.config.js | spec/notion-finance-ppm-control-room | spec/notion-finance-ppm-control-room/tasks.md |
| P2 | Config | Create tailwind.config.js | spec/notion-finance-ppm-control-room | spec/notion-finance-ppm-control-room/tasks.md |
| P2 | Config | Create src/app/api/health/route.ts | spec/notion-finance-ppm-control-room | spec/notion-finance-ppm-control-room/tasks.md |
| P2 | Config | Create src/lib/config.ts (configuration) | spec/notion-finance-ppm-control-room | spec/notion-finance-ppm-control-room/tasks.md |
| P2 | Config | Create src/components/dashboard/HealthBadge.tsx | spec/notion-finance-ppm-control-room | spec/notion-finance-ppm-control-room/tasks.md |
| P2 | Config | Create scripts/notion-ppm/health_check.sh | spec/notion-finance-ppm-control-room | spec/notion-finance-ppm-control-room/tasks.md |
| P2 | Config | Create `spec/ipai-ai-platform-odoo18/constitution.md` | spec/ipai-ai-platform-odoo18 | spec/ipai-ai-platform-odoo18/tasks.md |
| P2 | Config | Create `spec/ipai-ai-platform-odoo18/prd.md` | spec/ipai-ai-platform-odoo18 | spec/ipai-ai-platform-odoo18/tasks.md |
| P2 | Config | Create `spec/ipai-ai-platform-odoo18/plan.md` | spec/ipai-ai-platform-odoo18 | spec/ipai-ai-platform-odoo18/tasks.md |
| P2 | Config | Create `spec/ipai-ai-platform-odoo18/tasks.md` | spec/ipai-ai-platform-odoo18 | spec/ipai-ai-platform-odoo18/tasks.md |
| P2 | Config | Create `spec/ipai-ai-platform/constitution.md` | spec/ipai-ai-platform | spec/ipai-ai-platform/tasks.md |
| P2 | Config | Create `spec/ipai-ai-platform/prd.md` | spec/ipai-ai-platform | spec/ipai-ai-platform/tasks.md |
| P2 | Config | Create `spec/ipai-ai-platform/plan.md` | spec/ipai-ai-platform | spec/ipai-ai-platform/tasks.md |
| P2 | Config | Create `spec/ipai-ai-platform/tasks.md` | spec/ipai-ai-platform | spec/ipai-ai-platform/tasks.md |
| P2 | Config | Configure TypeScript | spec/insightpulse-mobile | spec/insightpulse-mobile/tasks.md |
| P2 | Config | Configure Zustand store | spec/insightpulse-mobile | spec/insightpulse-mobile/tasks.md |
