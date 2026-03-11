# Plan — IPAI Enterprise Workbench

## 1) Execution Plan (Phases)
### Phase A — Workspace & Services (M1)
**Deliverables**
- Dev workspace that can run:
  - Odoo (bind-mounted addons for hot iteration)
  - Postgres
  - Superset (config mounted, deterministic boot)
  - optional n8n
- "Doctor" script to validate the environment

**Key outputs**
- `sandbox/dev/docker-compose.workbench.yml` (or equivalent)
- `scripts/doctor_workbench.sh`

### Phase B — Finance PPM Canonicalization (M2)
**Deliverables**
- Workbook-driven seed generation (deterministic)
- Validation that mirrors workbook constraints
- Canonical stages import artifacts (XML + CSV template)
- Confirm OCA aggregation contains required repos (project/queue/reporting-engine as needed)

**Key outputs**
- `scripts/seed_finance_close_from_xlsx.py` enhancements (task_code, stage mapping, csv export)
- `scripts/validate_finance_ppm_data.py`
- Seed artifacts under `addons/.../data/seed/*`
- Drift gate workflow for seed outputs

### Phase C — Superset BI (M3)
**Deliverables**
- Superset datasets/views targeting Finance PPM analytics
- Starter dashboards

**Key outputs**
- `superset/` bootstrap config and importable dashboards (JSON)
- read-only DB role script for analytics access

### Phase D — Supabase+n8n+MCP Automation (M4)
**Deliverables**
- Ops schema for run logs and artifacts
- n8n flows (scheduled reminders, escalations, approvals signals)
- MCP tools for:
  - validate seeds
  - verify OCA aggregation
  - repo health/drift checks
  - deployment readiness

**Key outputs**
- `supabase/migrations/*` for ops schema
- `n8n/workflows/*.json`
- `mcp/servers/*` tool definitions and scripts

### Phase E — Design System Modules (M5)
**Deliverables**
- `ipai_design_system*` modules consuming SSOT tokens
- Odoo OWL theme adapter
- Web adapter ready for Workbench UI and future Mattermost rebrand

**Key outputs**
- `addons/ipai/ipai_design_system/` (+ optional split modules)
- `design/tokens/tokens.json` SSOT
- adapter docs and verification screenshots/visual tests (where feasible)

### Phase F — Odoo 19 Readiness (M6)
**Deliverables**
- Odoo 19 CE compatibility matrix (modules, patches, constraints)
- Upgrade playbook and gating tests
- "EE replacement" mapping refreshed for 19

**Key outputs**
- `docs/odoo19/compatibility_matrix.md`
- `scripts/upgrade_check_odoo19.sh`
- CI workflow to validate install on Odoo 19 branch

## 2) Architecture Decisions (Hard Requirements)
- Odoo DB remains primary transactional source.
- Superset reads via read-only role from stable views / replicated schema.
- Supabase used for ops queue/event logging and automation state, not for Odoo core DB.
- n8n is the orchestrator; MCP exposes tool interfaces to agents.
- Design tokens are SSOT and adapters only.

## 3) Verification Strategy
### 3.1 Repo Health
- Spec kit presence
- No EE/IAP deps
- Pre-commit + lint
- Tree/sitemap deterministic checks

### 3.2 Finance PPM
- Seed generator output equals committed seed (drift gate)
- Validation script returns 0 errors/warnings
- Stage import artifacts valid (XML/CSV)

### 3.3 Services
- Odoo starts and module install completes
- Superset starts and can query analytics views
- Supabase migrations apply (ops schema)
- n8n workflows import without error
- MCP server responds and tools execute

## 4) Rollout Strategy
- Dev workspace first, then production deploy
- Use feature branches per phase; merge only when gates pass
- Maintain an explicit deployment state snapshot doc updated per release

