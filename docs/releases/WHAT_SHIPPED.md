# What Shipped - Production Release Inventory

> **Generated:** 2026-01-06T18:07:00Z
> **ReleaseBot Version:** 1.0.0
> **Repository:** jgtolentino/odoo-ce

---

## Executive Summary

| Metric | Value |
|--------|-------|
| **Last Successful Deploy** | Deploy to Production #166 |
| **Production SHA** | `782fea9a7a4656d6ba225fcbea132908978d1522` |
| **Production Tag** | `prod-20260106-1741` |
| **Deploy Timestamp** | 2026-01-06T17:40:17Z |
| **Previous Baseline** | `a42fc69f418ecb5744607749c5d544f88aae8a9d` |
| **Previous Tag** | `prod-20260106-1643` |
| **Environment** | production (erp.insightpulseai.com) |
| **Docker Image** | `ghcr.io/jgtolentino/odoo-ce:edge-standard` |

---

## Deployment Timeline

```
Timeline (2026-01-06):
├── 16:41:48Z  Deploy #165 SUCCESS  → tag: prod-20260106-1643 (a42fc69)
├── 17:40:17Z  Deploy #166 SUCCESS  → tag: prod-20260106-1741 (782fea9) ← CURRENT PRODUCTION
├── 17:40:47Z  Deploy #167 CANCELLED (07e7aa6) - superseded by concurrent deploy
├── 17:40:53Z  Deploy #168 CANCELLED (ad9be72) - superseded by concurrent deploy
└── 17:41:28Z  Deploy #169 SKIPPED  (1b4a754) - all jobs skipped
```

---

## What Shipped (Deploy #166)

### Pull Request: #165 - Upgrade React Fluent UI design system

| Field | Value |
|-------|-------|
| **PR** | [#165](https://github.com/jgtolentino/odoo-ce/pull/165) |
| **SHA** | `782fea9a7a4656d6ba225fcbea132908978d1522` |
| **Author** | jgtolentino |
| **Merged At** | 2026-01-06T17:40:14Z |
| **Files Changed** | 28 |
| **Additions** | +5,888 |
| **Deletions** | -18 |

#### Summary
Production-ready React Fluent UI AI workspace with:
- Provider registry with multi-provider support
- Thread/message persistence with citations
- Workspace (Teamspace) model for Notion-style organization
- RAG integration with Supabase pgvector KB

---

## Changes by Category

### 1. Product Features (User-Visible)

| Change | Description | Evidence |
|--------|-------------|----------|
| IPAI AI Platform Spec | Spec kit bundle for IPAI AI Platform | `spec/ipai-ai-platform/` |
| Workspace OpenAPI | Workspaces endpoints and schemas | `docs/api/openapi.ipai_ai_platform.yaml` |
| DiagramFlow Tool | Mermaid to BPMN/Draw.io converter | `tools/diagramflow/` |

### 2. IPAI Modules (Odoo addons/ipai/*)

| Module | Change Type | Install Status | Version |
|--------|-------------|----------------|---------|
| `ipai_ai_core` | **Tests Added** | UNVERIFIED (no upgrade log) | — |

**Note:** Deploy to Production workflow does not execute Odoo module install/upgrade commands. Module installation status cannot be verified from this deploy workflow. The "Deploy Odoo Prod (upgrade module)" workflow failed (runs #24, #25).

### 3. OCA Dependencies

| Change | Status |
|--------|--------|
| No OCA manifest changes in this deploy | — |

### 4. Infra/CI/Workflows

| File | Change Type | Description |
|------|-------------|-------------|
| `.github/workflows/diagrams.yml` | **Added** | New workflow for diagram generation/validation |
| `.github/workflows/ipai-ai-platform-ci.yml` | Modified | Updated module paths and validation checks |

### 5. Data/Seed/Config

| Item | Status | Notes |
|------|--------|-------|
| Database Migrations | NONE | No SQL migrations in commit range |
| Seed Data | NONE | No seed data changes |
| Environment Config | UNCHANGED | — |

### 6. Documentation & Data Models

| File | Type | Description |
|------|------|-------------|
| `docs/data-model/IPAI_AI_PLATFORM_SCHEMA.dbml` | **New** | DBML schema for AI Platform |
| `docs/data-model/IPAI_AI_PLATFORM_ERD.mmd` | **New** | Mermaid ERD diagram |
| `docs/architecture/IPAI_AI_PLATFORM_ARCH.md` | Updated | Workspace design and deployment checklist |
| `docs/architecture/IPAI_AI_PLATFORM_ORD.md` | **New** | Object Relationship Document with attribute definitions |
| `spec/ipai-ai-platform/constitution.md` | **New** | Non-negotiable rules and constraints |
| `spec/ipai-ai-platform/prd.md` | **New** | Product requirements document |
| `spec/ipai-ai-platform/plan.md` | **New** | Implementation plan |
| `spec/ipai-ai-platform/tasks.md` | **New** | Task checklist |

---

## Files Changed (Complete List)

```
 .github/workflows/diagrams.yml                     | 187 +++++++++
 .github/workflows/ipai-ai-platform-ci.yml          |  28 +-
 SITEMAP.md                                         |  14 +-
 TREE.md                                            |  56 ++-
 addons/ipai/ipai_ai_core/tests/__init__.py         |   4 +
 addons/ipai/ipai_ai_core/tests/test_provider.py    | 170 ++++++++
 addons/ipai/ipai_ai_core/tests/test_service.py     | 173 ++++++++
 addons/ipai/ipai_ai_core/tests/test_thread.py      | 326 +++++++++++++++
 docs/api/openapi.ipai_ai_platform.yaml             | 194 +++++++++
 docs/architecture/IPAI_AI_PLATFORM_ARCH.md         | 129 ++++++
 docs/architecture/IPAI_AI_PLATFORM_ORD.md          | 450 +++++++++++++++++++++
 docs/data-model/IPAI_AI_PLATFORM_ERD.mmd           | 228 +++++++++++
 docs/data-model/IPAI_AI_PLATFORM_SCHEMA.dbml       | 374 +++++++++++++++++
 docs/diagrams/ipai_platform_flow.mmd               |  46 +++
 docs/diagrams/mappings/azure_to_do_supabase_odoo.yaml | 308 ++++++++++++++
 spec/ipai-ai-platform/constitution.md              | 223 ++++++++++
 spec/ipai-ai-platform/plan.md                      | 355 ++++++++++++++++
 spec/ipai-ai-platform/prd.md                       | 426 +++++++++++++++++++
 spec/ipai-ai-platform/tasks.md                     | 290 +++++++++++++
 tools/diagramflow/README.md                        | 155 +++++++
 tools/diagramflow/package.json                     |  27 ++
 tools/diagramflow/src/cli.ts                       | 338 ++++++++++++++++
 tools/diagramflow/src/index.ts                     |  17 +
 tools/diagramflow/src/parseMermaid.ts              | 387 ++++++++++++++++++
 tools/diagramflow/src/remap.ts                     | 283 +++++++++++++
 tools/diagramflow/src/toBpmn.ts                    | 408 +++++++++++++++++++
 tools/diagramflow/src/toDrawio.ts                  | 292 +++++++++++++
 tools/diagramflow/tsconfig.json                    |  18 +
 28 files changed, 5888 insertions(+), 18 deletions(-)
```

---

## What Did NOT Ship

The following changes are on `main` but have **NOT** been deployed to production:

### PR #166 - Set up Auto-Claude autonomous coding framework

| Field | Value |
|-------|-------|
| **PR** | [#166](https://github.com/jgtolentino/odoo-ce/pull/166) |
| **SHA** | `ad9be7232ad0b4ba7adc6613515cb1b210eb71d9` |
| **Status** | **NOT DEPLOYED** |
| **Reason** | Deploy runs #167/#168 cancelled, #169 skipped |

**Changes NOT in production:**
- `spec/auto-claude-framework/` - Spec bundle for Auto-Claude
- `addons/ipai/ipai_skill_api/` - REST API module for skills
- `supabase/migrations/20260106000001_kg_schema.sql` - Knowledge Graph schema
- `skills/` - 5 core skill definitions
- `tests/e2e/playwright/` - E2E test scaffolding
- `tests/api/` - API contract tests
- `addons/oca/manifest.yaml` - OCA agent framework dependencies

---

## Failed Workflows

These workflows attempted to run but **FAILED** (no production changes from them):

| Workflow | Run # | SHA | Conclusion |
|----------|-------|-----|------------|
| Deploy Odoo Prod (upgrade module) | #25 | ad9be72 | **FAILURE** |
| Deploy Odoo Prod (upgrade module) | #24 | 782fea9 | **FAILURE** |
| Deploy Finance PPM to Production | #39 | ad9be72 | **FAILURE** |
| Deploy Finance PPM to Production | #38 | 782fea9 | **FAILURE** |

**Impact:** No Odoo module upgrades were executed via these workflows.

---

## Deployment Evidence

### Workflow Run Details

| Field | Value |
|-------|-------|
| **Workflow** | Deploy to Production |
| **Run ID** | 20756736863 |
| **Run Number** | 166 |
| **HTML URL** | https://github.com/jgtolentino/odoo-ce/actions/runs/20756736863 |
| **Status** | completed |
| **Conclusion** | success |

### Job Execution Summary

| Job | Status | Duration |
|-----|--------|----------|
| Pre-flight Checks | SUCCESS | 5s |
| Deploy to Production | SUCCESS | 7s |
| Production Smoke Test | SUCCESS | 63s |
| Auto-Tag Release | SUCCESS | 8s |

### Deploy Steps (from "Deploy to Production" job)

1. **Set up job** - SUCCESS
2. **Checkout** - SUCCESS
3. **Deploy notification - Starting** - SUCCESS
4. **Deploy to production server** - SUCCESS
5. **Verify deployment** - SUCCESS
6. **Deploy notification - Complete** - SUCCESS

### Release Tag Created

| Field | Value |
|-------|-------|
| **Tag** | `prod-20260106-1741` |
| **URL** | https://github.com/jgtolentino/odoo-ce/releases/tag/prod-20260106-1741 |
| **Full Changelog** | https://github.com/jgtolentino/odoo-ce/compare/prod-20260106-1643...prod-20260106-1741 |

---

## UNVERIFIED Items

The following items could not be verified from available workflow logs:

| Item | Reason | Risk |
|------|--------|------|
| Odoo module install/upgrade | Deploy workflow doesn't run `-u module` commands | LOW - code deployed, module state unknown |
| Database migrations | No migration logs available | LOW - no migrations in commit range |
| Docker image pull on server | SSH step output not captured in API | LOW - workflow succeeded |
| Health check result | Smoke test stub doesn't capture response | LOW - job succeeded |

---

## Provenance Links

| Resource | URL |
|----------|-----|
| Deploy Run #166 | https://github.com/jgtolentino/odoo-ce/actions/runs/20756736863 |
| PR #165 | https://github.com/jgtolentino/odoo-ce/pull/165 |
| Commit 782fea9 | https://github.com/jgtolentino/odoo-ce/commit/782fea9a7a4656d6ba225fcbea132908978d1522 |
| Release Tag | https://github.com/jgtolentino/odoo-ce/releases/tag/prod-20260106-1741 |
| Previous Tag | https://github.com/jgtolentino/odoo-ce/releases/tag/prod-20260106-1643 |

---

*Generated by ReleaseBot for jgtolentino/odoo-ce*
