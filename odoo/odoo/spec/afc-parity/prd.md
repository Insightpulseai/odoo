# AFC Parity — Product Requirements Document

**Version:** 1.0 | **Date:** 2026-03-15

## 1. Overview

Close the gap between our Odoo CE + OCA + ipai_* financial close implementation and SAP S/4HANA Cloud Advanced Financial Closing (AFC). Current parity: ~60%. Target: >= 80%.

## 2. Benchmark Sources

### Public/open benchmark

- **Repo:** `SAP-docs/s4hana-cloud-advanced-financial-closing` (GitHub)
- **Content:** 148 pages covering close orchestration, task management, templates, archiving, user management, security, integration
- **Use for:** Close orchestration patterns, template design, approval workflows, archiving, user/admin patterns

### Proprietary benchmark

- **Source:** SAP Help Portal — SAP Tax Compliance for S/4HANA
- **Content:** Compliance checks, scenarios, worklists, remediation semantics, VAT checks
- **Use for:** Behavioral reference only — compliance check design, finding/remediation semantics
- **Do NOT:** Treat as repo-importable SSOT or code source

### Out-of-scope (architectural mismatch)

- SAP connectivity satellite patterns (32 pages)
- BTP/Fiori/BPA-specific surfaces
- SAP Task Center, Build Work Zone, Build Process Automation integrations
- Remote job execution and scheduling queues

## 3. Current Parity Assessment

### Full parity (18 features)

Task management, multi-entity close, role-based access, 4-gate approvals, bank/GL reconciliation, financial reporting, BIR core forms (1601-C, 1702-RT, 2316, Alphalist), audit trail, user provisioning, period lock, encryption, multi-environment, user groups, financial statements, variance analysis, WHT reconciliation, tax provisioning, system landscape.

### Partial parity (10 features)

Task dependencies, task statuses, authorization scopes, compliance settings, email notifications, session security, audit logging, intercompany elimination, FX revaluation, BIR form coverage.

### Gaps (11 features)

See Section 4.

## 4. Confirmed Gap Set

### P1 — Must close (next 90 days)

| # | Gap | SAP AFC Behavior | Target |
|---|---|---|---|
| G-01 | Successor invalidation cascade | Auto-invalidate/retrigger dependent tasks on predecessor failure | Add dependency engine to `ipai_finance_ppm` |
| G-02 | Automatic archiving | Time-based task list archiving (6-18 months by close type) | Cron-driven archival by period type |
| G-03 | Granular notification scenarios | Task-specific notification configs (assigned, completed, due) | Notification scenario model + mail templates |
| G-04 | BIR 2550M/Q + 0619-E | Full form coverage | Expand `ipai_bir_tax_compliance` |

### P2 — Should close (90-180 days)

| # | Gap | SAP AFC Behavior | Target |
|---|---|---|---|
| G-05 | Substitute/delegation workflow | Temporary role assumption for absent users | Substitute management on task assignment |
| G-06 | Malware scanning on upload | Virus scan on file attachments | ClamAV integration |
| G-07 | System health dashboard | Comprehensive system status and metrics | SLA metrics + alert dashboard |
| G-08 | Email anonymization | Remove usernames after N months | Compliance cron for username redaction |
| G-09 | Task-status-driven automation | SAP BPA triggers from task status | n8n webhooks on task state changes |

### P3 — Nice to have

| # | Gap | Target |
|---|---|---|
| G-10 | Predefined role collections | Bundle Odoo groups into SAP-style role templates |
| G-11 | Multi-language close templates | Translate task list templates per language |

## 5. Success Criteria

- Parity score >= 80% (weighted by priority)
- All P1 gaps closed within 90 days
- All P2 gaps closed within 180 days
- No regression in existing parity features
- All new features include tests and documentation
