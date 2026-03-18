# Deployment Timeline — Odoo 19 CE

Actual deployment milestones for the InsightPulse AI ERP platform migration from Odoo 18 to Odoo 19 CE.

---

## Production Stack

| Component | Value |
|-----------|-------|
| **ERP** | Odoo 19 CE + OCA + ipai_* |
| **Database** | PostgreSQL 16 |
| **Automation** | n8n |
| **Chat** | Slack |
| **External DB** | Supabase (`spdtwktxdalcfigzeqrz`) |
| **BI** | Apache Superset |
| **Hosting** | DigitalOcean |
| **Domain** | `insightpulseai.com` |
| **ERP URL** | `erp.insightpulseai.com` |
| **Docs** | GitHub Pages (Primer design system) |

---

## Milestone Timeline

### Phase 1: Foundation (2025-09 to 2025-12)

| Date | Milestone | Status |
|------|-----------|--------|
| 2025-09 | Odoo 19 CE released (Odoo Experience 2025) | Done |
| 2025-10 | Repository initialized (`Insightpulseai/odoo`) | Done |
| 2025-11 | OCA submodules pinned (18.0 branches) | Done |
| 2025-12 | Docker image baseline (`ghcr.io/...`) | Done |

### Phase 2: Core Modules (2026-01)

| Date | Milestone | Status |
|------|-----------|--------|
| 2026-01-06 | Production deploy #166 (Fluent UI AI workspace) | Done |
| 2026-01-09 | Release tag `prod-20260109-1642` | Done |
| 2026-01-19 | EE replacement matrix v1.0 published | Done |
| 2026-01-22 | Enterprise parity PRD v1.0 | Done |
| 2026-01-28 | Mattermost deprecated → Slack | Done |

### Phase 3: Finance PPM & Ship (2026-02)

| Date | Milestone | Status |
|------|-----------|--------|
| 2026-02-03 | Repo renamed `odoo-ce` → `odoo` | Done |
| 2026-02-09 | Affine deprecated, WorkOS Affine module deprecated | Done |
| 2026-02-11 | **EE Parity Gate: ALL PASS** | **Done** |
| 2026-02-11 | Finance PPM fully seeded (9 employees, 22 BIR, 36 tasks, RACI) | **Done** |
| 2026-02-11 | OCR Gateway v19.0 ready | **Done** |
| 2026-02-11 | AI Agent Builder v19.0 ready | **Done** |
| 2026-02-11 | Zoho Mail SMTP configured | **Done** |
| 2026-02-11 | Docs site upgraded to Primer design system | **Done** |

### Phase 4: OCA 19.0 Ports (2026 Q1-Q2, Planned)

| Target | Milestone | Status |
|--------|-----------|--------|
| 2026-Q1 | OCA `account_financial_report` 19.0 | Available |
| 2026-Q1 | OCA `account_tax_balance` 19.0 | Available |
| 2026-Q1 | OCA `partner_statement` 19.0 | Available |
| 2026-Q2 | OCA `dms` 19.0 port | Pending (issue #447) |
| 2026-Q2 | OCA `helpdesk_mgmt` 19.0 port | Pending |
| 2026-Q2 | OCA `base_tier_validation` 19.0 port | Pending |
| 2026-Q2 | OCA `ai_oca_bridge` 19.0 port | Pending (issue #42) |
| 2026-Q2 | OCA `mis_builder` 19.0 port | Pending |

---

## Module Ship Manifest (2026-02-11)

### Shipping Now

| Module | Version | Category | Seed Data |
|--------|---------|----------|-----------|
| `ipai_finance_ppm` | 19.0 | Finance/PPM | Cron sync |
| `ipai_finance_ppm_umbrella` | 19.0.1.1.0 | Finance/Seed | 9 employees, 22 BIR, 36 tasks, RACI |
| `ipai_finance_ppm_golive` | 19.0 | Finance/Checklist | 60+ items, 9 sections |
| `ipai_finance_closing` | 19.0 | Finance/AFC | 25+ closing templates |
| `ipai_month_end` | 19.0 | Finance/Automation | PH holidays, task templates |
| `ipai_bir_tax_compliance` | 19.0 | Finance/BIR | 36 eBIRForms, tax rates |
| `ipai_ocr_gateway` | 19.0.1.0.0 | Productivity/OCR | Provider configs |
| `ipai_ai_agent_builder` | 19.0.1.0.0 | Productivity/AI | Agent definitions |
| `ipai_ops_mirror` | 19.0 | Technical/Supabase | Cron sync |

### OCA Available (19.0)

| Module | Repository |
|--------|-----------|
| `account_financial_report` | OCA/account-financial-reporting |
| `account_tax_balance` | OCA/account-financial-reporting |
| `partner_statement` | OCA/account-financial-reporting |

### Deferred (Awaiting 19.0 Port)

| Module | Repository | Tracking |
|--------|-----------|----------|
| `dms` | OCA/dms | [#447](https://github.com/OCA/dms/issues/447) |
| `ai_oca_bridge` | OCA/ai | [#42](https://github.com/OCA/ai/issues/42) |
| `helpdesk_mgmt` | OCA/helpdesk | Migration pending |
| `base_tier_validation` | OCA/server-ux | Migration pending |
| `mis_builder` | OCA/mis-builder | Migration pending |

---

## Deprecated Items

| Item | Replacement | Date |
|------|-------------|------|
| `insightpulseai.net` | `insightpulseai.com` | 2026-02 |
| `odoo-ce` repo name | `odoo` | 2026-02-03 |
| Mattermost | Slack | 2026-01-28 |
| Affine | Removed | 2026-02-09 |
| Mailgun / `ipai_mailgun_bridge` | Zoho Mail SMTP | 2026-02 |
| `ipai_mattermost_connector` | `ipai_slack_connector` | 2026-01-28 |

---

## Verification

```bash
# Module installability
./scripts/repo_health.sh

# Spec validation
./scripts/spec_validate.sh

# DNS baseline
./scripts/verify-dns-baseline.sh

# Service health
./scripts/verify-service-health.sh
```
