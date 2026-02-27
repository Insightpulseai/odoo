# Evidence — Custom Addons Reassessment

**Audit date**: 2026-02-27
**Branch**: `feat/ipai-module-audit-odoo19`
**STATUS**: COMPLETE

---

## [CONTEXT]
- repo: Insightpulseai/odoo
- branch: feat/ipai-module-audit-odoo19
- goal: Full audit + Odoo 19 compatibility patches for addons/ipai/
- stamp: 2026-02-27T21:00+0800

---

## [CHANGES]

- `docs/audits/custom_addons_reassessment.md`: Full 59-module classification table (KEEP / KEEP/PATCH / DISABLE / DEPRECATED)
- `docs/audits/custom_addons_reassessment_DECISIONS.md`: Priority matrix P1/P2/P3 with rationale
- `docs/audits/evidence_custom_addons_reassessment.md`: This file
- `addons/ipai/ipai_mailgun_smtp/__manifest__.py`: installable=True → False (deprecated per CLAUDE.md)
- `addons/ipai/ipai_odooops_shell/__manifest__.py`: version 1.0.0 → 19.0.1.0.0
- `addons/ipai/ipai_ai_agents_ui/__manifest__.py`: installable=True → False (missing ipai_ai_core)
- `addons/ipai/ipai_bir_notifications/__manifest__.py`: installable=True → False (missing ipai_bir_tax_compliance)
- `addons/ipai/ipai_bir_plane_sync/__manifest__.py`: installable=True → False (missing ipai_bir_tax_compliance)
- `addons/ipai/ipai_hr_payroll_ph/__manifest__.py`: installable=True → False (missing ipai_bir_tax_compliance)
- `addons/ipai/ipai_finance_workflow/__manifest__.py`: installable=True → False (missing ipai_workspace_core)
- `addons/ipai/ipai_vertical_media/__manifest__.py`: installable=True → False (missing ipai_workspace_core)
- `addons/ipai/ipai_vertical_retail/__manifest__.py`: installable=True → False (missing ipai_workspace_core)
- `addons/ipai/ipai_helpdesk/views/helpdesk_ticket_views.xml`: 1× `<tree>` → `<list>`, 1× view_mode patched
- `addons/ipai/ipai_helpdesk/views/helpdesk_team_views.xml`: 3× `<tree>` → `<list>`, 1× view_mode patched
- `addons/ipai/ipai_hr_expense_liquidation/views/expense_liquidation_views.xml`: 2× `<tree>` → `<list>`, 3× view_mode patched
- `addons/ipai/ipai_hr_payroll_ph/views/hr_payslip_views.xml`: 1× `<tree>` → `<list>`, 1× view_mode patched
- `addons/ipai/ipai_platform_api/views/platform_feature_views.xml`: 1× `<tree>` → `<list>`, 1× view_mode patched
- `addons/ipai/ipai_platform_api/views/platform_deployment_views.xml`: 1× `<tree>` → `<list>`, 1× view_mode patched

---

## [EVIDENCE]

### 1. Manifest inventory (all 59 modules scanned)
- command: `python3 -c "import os, ast, json; ..."` (AST parse of __manifest__.py)
- result: PASS — 59 modules enumerated, 0 parse errors
- key counts: 23 installable=False (already deprecated), 36 installable=True before patches

### 2. Missing dependency check
- command: `ls addons/ipai/ipai_bir_tax_compliance/ addons/ipai/ipai_workspace_core/ addons/ipai/ipai_ai_core/`
- result: PASS — all 3 confirmed ABSENT (expected)
- impact: 7 modules set installable=False to prevent install-time crashes

### 3. Tree→list violation scan
- command: `grep -n "<tree\b\|view_mode.*tree" addons/ipai/*/views/*.xml`
- result: PASS — 9 `<tree>` tags + 10 `view_mode=*tree*` found across 6 files in 4 modules

### 4. Manifest patch verification
- command: Python AST re-parse of 9 patched manifests
- result: PASS — all 8 disabled manifests have installable=False; ipai_odooops_shell version=19.0.1.0.0
```
PASS: ipai_mailgun_smtp installable=False
PASS: ipai_ai_agents_ui installable=False
PASS: ipai_bir_notifications installable=False
PASS: ipai_bir_plane_sync installable=False
PASS: ipai_hr_payroll_ph installable=False
PASS: ipai_finance_workflow installable=False
PASS: ipai_vertical_media installable=False
PASS: ipai_vertical_retail installable=False
PASS: ipai_odooops_shell version=19.0.1.0.0
OVERALL: PASS
```

### 5. Tree→list patch verification
- command: `grep -rn "<tree\b\|view_mode.*tree" addons/ipai/ipai_helpdesk/... (6 files)`
- result: PASS — exit code 1 (no matches = no residual `<tree>`)
- `<list>` counts: helpdesk_ticket=1, helpdesk_team=3, expense_liquidation=2, payslip=1, platform_feature=1, platform_deployment=1

---

## [DIFF SUMMARY]

- `addons/ipai/ipai_mailgun_smtp/__manifest__.py`: Deprecated mailgun module disabled; summary updated
- `addons/ipai/ipai_odooops_shell/__manifest__.py`: Version normalized to OCA convention
- 7× `__manifest__.py` (missing-dep modules): installable set to False, preventing crash on `odoo -i`
- 6× view XML files (4 modules): `<tree>` → `<list>`, `view_mode=tree,...` → `view_mode=list,...` for Odoo 19 compat

---

## [BLOCKERS]

None for this PR.

### Future work (separate PRs)
- Scaffold `ipai_bir_tax_compliance` to re-enable 3 BIR/payroll modules
- Scaffold `ipai_workspace_core` to re-enable 3 vertical modules
- Scaffold `ipai_ai_core` to re-enable `ipai_ai_agents_ui`

---

## [NEXT - DETERMINISTIC]

- step 1: `git add docs/audits/ addons/ipai/` — stage audit docs + manifest patches
- step 2: `git commit -m "feat(ipai): module audit — disable deprecated + missing-dep + tree→list Odoo19 compat"`
- step 3: `gh pr create --base main --title "feat(ipai): module audit — Odoo 19 compat + disable 9 broken modules"`
