# Notion x Finance PPM Control Room — Task Checklist

> **Version**: 1.0.0
> **Status**: Active
> **Last Updated**: 2025-12-21

---

## Phase 1: Foundation

### 1.1 Repository Structure
- [x] Create spec bundle (constitution, prd, plan, tasks)
- [x] Create apps/control-room directory structure
- [x] Create services/notion-sync directory structure
- [x] Create infra/databricks directory structure
- [x] Create infra/azure directory structure
- [x] Create .continue/rules directory structure
- [x] Create scripts directory with verification scripts

### 1.2 Configuration
- [x] Create .env.example for control-room
- [x] Create .env.example for notion-sync
- [x] Create notion_mapping.yaml configuration
- [x] Create databricks.yml bundle configuration

---

## Phase 2: Notion Sync Service

### 2.1 Core Module
- [x] Create notion_sync/config.py (configuration loading)
- [x] Create notion_sync/client.py (Notion API wrapper)
- [x] Create notion_sync/models.py (Pydantic models)
- [x] Create notion_sync/sync.py (sync engine)
- [x] Create notion_sync/transform.py (column mapping)
- [x] Create notion_sync/databricks_writer.py (Delta writer)
- [x] Create notion_sync/__init__.py (package init)
- [x] Create notion_sync/main.py (entrypoint)

### 2.2 Testing
- [x] Create tests/test_client.py
- [x] Create tests/test_transform.py
- [x] Create tests/conftest.py (fixtures)

### 2.3 Packaging
- [x] Create pyproject.toml
- [x] Create README.md

---

## Phase 3: Databricks Lakehouse

### 3.1 DAB Bundle
- [x] Create databricks.yml (bundle config)
- [x] Create resources/jobs.yml (job definitions)
- [x] Create resources/schemas.yml (table schemas)

### 3.2 Bronze Notebooks
- [x] Create notebooks/bronze/ingest_notion.py
- [x] Create notebooks/bronze/ingest_azure_rg.py

### 3.3 Silver Notebooks
- [x] Create notebooks/silver/transform_notion_programs.py
- [x] Create notebooks/silver/transform_notion_projects.py
- [x] Create notebooks/silver/transform_notion_budget_lines.py
- [x] Create notebooks/silver/transform_notion_risks.py
- [x] Create notebooks/silver/transform_azure_advisor.py

### 3.4 Gold Notebooks
- [x] Create notebooks/gold/budget_vs_actual.py
- [x] Create notebooks/gold/forecast.py
- [x] Create notebooks/gold/risk_summary.py
- [x] Create notebooks/gold/control_room_status.py
- [x] Create notebooks/gold/dq_checks.py

---

## Phase 4: Control Room Application

### 4.1 Project Setup
- [x] Initialize Next.js project
- [x] Configure Tailwind CSS
- [x] Configure TypeScript
- [x] Create package.json with dependencies
- [x] Create next.config.js
- [x] Create tailwind.config.js

### 4.2 Types and Schemas
- [x] Create src/types/api.ts (API response types)
- [x] Create src/types/models.ts (domain models)
- [x] Create src/lib/schemas.ts (Zod schemas)

### 4.3 API Routes
- [x] Create src/app/api/health/route.ts
- [x] Create src/app/api/kpis/route.ts
- [x] Create src/app/api/jobs/route.ts
- [x] Create src/app/api/job-runs/route.ts
- [x] Create src/app/api/dq/issues/route.ts
- [x] Create src/app/api/advisor/recommendations/route.ts
- [x] Create src/app/api/projects/route.ts
- [x] Create src/app/api/notion/actions/route.ts

### 4.4 Library Functions
- [x] Create src/lib/databricks.ts (Databricks client)
- [x] Create src/lib/notion.ts (Notion client)
- [x] Create src/lib/config.ts (configuration)

### 4.5 Components
- [x] Create src/components/layout/Sidebar.tsx
- [x] Create src/components/layout/Header.tsx
- [x] Create src/components/layout/PageContainer.tsx
- [x] Create src/components/dashboard/KPICard.tsx
- [x] Create src/components/dashboard/HealthBadge.tsx
- [x] Create src/components/dashboard/ActivityFeed.tsx
- [x] Create src/components/tables/DataTable.tsx
- [x] Create src/components/tables/JobsTable.tsx
- [x] Create src/components/tables/ProjectsTable.tsx
- [x] Create src/components/charts/BudgetChart.tsx
- [x] Create src/components/common/Button.tsx
- [x] Create src/components/common/Badge.tsx
- [x] Create src/components/common/Card.tsx

### 4.6 Pages
- [x] Create src/app/layout.tsx (root layout)
- [x] Create src/app/page.tsx (redirect to overview)
- [x] Create src/app/overview/page.tsx
- [x] Create src/app/pipelines/page.tsx
- [x] Create src/app/data-quality/page.tsx
- [x] Create src/app/advisor/page.tsx
- [x] Create src/app/projects/page.tsx

### 4.7 Styling
- [x] Create src/app/globals.css

---

## Phase 5: Azure Infrastructure

### 5.1 Bicep Templates
- [x] Create infra/azure/main.bicep
- [x] Create infra/azure/modules/databricks.bicep
- [x] Create infra/azure/modules/keyvault.bicep
- [x] Create infra/azure/modules/storage.bicep
- [x] Create infra/azure/modules/appservice.bicep
- [x] Create infra/azure/parameters/dev.parameters.json
- [x] Create infra/azure/parameters/prod.parameters.json

---

## Phase 6: CI/CD Pipelines

### 6.1 GitHub Actions
- [x] Create .github/workflows/ci-notion-ppm.yml
- [x] Create .github/workflows/deploy-control-room.yml
- [x] Create .github/workflows/deploy-databricks.yml

---

## Phase 7: Continue Rules

### 7.1 Rule Files
- [x] Create .continue/rules/architecture.md
- [x] Create .continue/rules/coding-standards.md
- [x] Create .continue/rules/data-contracts.md
- [x] Create .continue/rules/security.md

---

## Phase 8: Verification & Documentation

### 8.1 Scripts
- [x] Create scripts/notion-ppm/dev_up.sh
- [x] Create scripts/notion-ppm/run_notion_sync.sh
- [x] Create scripts/notion-ppm/dab_deploy.sh
- [x] Create scripts/notion-ppm/health_check.sh

### 8.2 Documentation
- [x] Create docs/notion-ppm/architecture.md
- [x] Create docs/notion-ppm/runbooks.md
- [x] Create docs/notion-ppm/data-dictionary.md

---

## Verification Checklist

- [x] All files created and non-empty
- [x] No placeholder values (TODO, xxx, etc.) in production code
- [x] All scripts are executable
- [x] TypeScript compiles without errors
- [x] Python passes lint checks
- [x] Documentation is complete
- [x] Commit and push to branch

---

## Notes

- All Notion database IDs are configured via environment variables
- Databricks authentication uses service principal in production
- Control Room uses API key authentication
- All secrets must be in .env files, never hardcoded
