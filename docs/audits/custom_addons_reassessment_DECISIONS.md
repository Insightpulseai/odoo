# Custom Addons Decisions — Priority Matrix

**Audit date**: 2026-02-27
**Source**: `docs/audits/custom_addons_reassessment.md`

---

## Priority 1 — This PR (safety + Odoo 19 correctness)

### P1-A: Disable deprecated-but-incorrectly-enabled module

| Module | Change | Reason |
|--------|--------|--------|
| `ipai_mailgun_smtp` | `installable=True` → `installable=False` | Mailgun deprecated per CLAUDE.md 2026-02. Zoho Mail replaces it. Data file in manifest seeds a live mail server record — dangerous if installed. |

### P1-B: Disable modules with missing dependencies (install blocker)

| Module | Change | Missing Dep |
|--------|--------|------------|
| `ipai_ai_agents_ui` | `installable=True` → `installable=False` | `ipai_ai_core` |
| `ipai_bir_notifications` | `installable=True` → `installable=False` | `ipai_bir_tax_compliance` |
| `ipai_bir_plane_sync` | `installable=True` → `installable=False` | `ipai_bir_tax_compliance` |
| `ipai_hr_payroll_ph` | `installable=True` → `installable=False` | `ipai_bir_tax_compliance` |
| `ipai_finance_workflow` | `installable=True` → `installable=False` | `ipai_workspace_core` |
| `ipai_vertical_media` | `installable=True` → `installable=False` | `ipai_workspace_core` |
| `ipai_vertical_retail` | `installable=True` → `installable=False` | `ipai_workspace_core` |

### P1-C: Patch tree→list (Odoo 19 view compatibility)

In Odoo 19 CE, `<tree>` view elements and `view_mode` values containing `tree` generate deprecation warnings and may fail in strict mode. All occurrences must be renamed to `<list>` / `list`.

| Module | File | Changes |
|--------|------|---------|
| `ipai_helpdesk` | `views/helpdesk_ticket_views.xml` | `<tree>` → `<list>`, `view_mode=kanban,tree,form` → `kanban,list,form` |
| `ipai_helpdesk` | `views/helpdesk_team_views.xml` | 3× `<tree>` → `<list>`, `view_mode=tree,form` → `list,form` |
| `ipai_hr_expense_liquidation` | `views/expense_liquidation_views.xml` | 2× `<tree>` → `<list>`, 3× `view_mode=tree,form` → `list,form` |
| `ipai_hr_payroll_ph` | `views/hr_payslip_views.xml` | `<tree>` → `<list>`, `view_mode=tree,form` → `list,form` |
| `ipai_platform_api` | `views/platform_feature_views.xml` | `<tree>` → `<list>`, `view_mode=tree,form` → `list,form` |
| `ipai_platform_api` | `views/platform_deployment_views.xml` | `<tree>` → `<list>`, `view_mode=tree,form` → `list,form` |

### P1-D: Fix version misformat

| Module | Change | Reason |
|--------|--------|--------|
| `ipai_odooops_shell` | `"version": "1.0.0"` → `"version": "19.0.1.0.0"` | OCA convention requires `{series}.{major}.{minor}.{patch}.{build}` |

---

## Priority 2 — Next sprint (scaffold missing deps)

| Task | New Module | Unblocks |
|------|-----------|---------|
| Scaffold `ipai_bir_tax_compliance` | Core BIR filing forms + deadlines model | `ipai_bir_notifications`, `ipai_bir_plane_sync`, `ipai_hr_payroll_ph` |
| Scaffold `ipai_workspace_core` | Shared workspace primitives | `ipai_finance_workflow`, `ipai_vertical_media`, `ipai_vertical_retail` |
| Scaffold `ipai_ai_core` | Shared AI provider config bridge | `ipai_ai_agents_ui` |

---

## Priority 3 — Strategic (future PRs)

| Decision | Recommendation | Effort |
|---------|----------------|--------|
| Replace `ipai_helpdesk` with OCA `helpdesk_mgmt` | Lower maintenance burden; OCA-maintained | Medium (data migration + customization diff) |
| Replace `ipai_auth_oidc` with OCA `auth_oidc` | OCA auth_oidc 19.0 is available; our version is a thin wrapper | Low |
| Evaluate `ipai_rest_controllers` retirement | Once OCA `base_rest` 19.0 is stable | Low (swap imports) |
| Clean-delete deprecated modules from repo | 23 modules are `installable=False`; remove source to reduce surface area | Medium (coordinate with any feature branch using them) |

---

## No-Change Decisions (rationale logged)

| Module | Rationale for keeping as-is |
|--------|------------------------------|
| `ipai_ai_copilot` | Active development; no OCA equivalent at this depth |
| `ipai_enterprise_bridge` | Wide EE stub surface; consolidation in progress |
| `ipai_design_system_apps_sdk` | SSOT for all IPAI UI — sole canonical design token source |
| `ipai_expense_ocr` | Active; backed by OCR service infra |
| `ipai_mail_bridge_zoho` + `ipai_zoho_mail` + `ipai_zoho_mail_api` | Three complementary Zoho modules serve distinct needs (HTTPS bypass / SMTP panel / REST API) |
